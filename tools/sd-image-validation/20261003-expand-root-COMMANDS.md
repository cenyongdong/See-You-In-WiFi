# Lite 新 SD 卡根分区扩容命令（2026-10-03）

状态更新（2026-10-03）：已执行并明确确认扩容成功；[最终截图](20261003-expansion-success.png)确认内核分区长度120066048扇区、resize2fs在线扩容到15008256个4KiB块、df根容量57G/可用48G。本说明保留原执行步骤，不代表代理操作设备；备份、预演和正式写表完整输出未包含在最终截图中。仅适用于本次已核对的 /dev/mmcblk0、DOS/MBR、sfdisk 2.34、ext4 根分区 /dev/mmcblk0p2。

证据：[板端查询](20261003-board-preflight.png)、[分区表](20261003-partition-table.png)、[结构化记录](20261002-new-card-board-confirmation.json)。当前磁盘共122167296个512字节扇区，ID=0x370deffb。p1 start=2048,size=2097152,type=e；p2 start=2101248,size=54687500,type=83。p2扩容目标长度=122167296-2101248=120066048扇区，最后扇区122167295，约57.25GiB。数字仅适用于本卡本布局，不用于其他卡。

保持供电稳定，停止应用负载；逐步执行，任何报错或预期字段不符即停止并保留完整输出。此方案不移动分区起始、不格式化文件系统；写分区表与扩大ext4是两个步骤，中间重启。以下是供人工操作的具体方案，不作为扩容通过记录。

1. 创建本次备份目录（只创建目录，不修改分区；首次操作时执行）：

   ```bash
   mkdir -p /root/sd-expand-20261003
   ```

2. 保存并查看原始分区表。`--dump`读取分区表，`>`把输出保存为文本，`&&`只在导出成功时显示备份。备份只是分区表，不是全卡数据备份；将显示内容同时保存到Windows文本文件。不要在写表后重新执行此命令覆盖原始备份。

   ```bash
   sfdisk --dump /dev/mmcblk0 > /root/sd-expand-20261003/mmcblk0-before.sfdisk && cat /root/sd-expand-20261003/mmcblk0-before.sfdisk
   ```

   核对label=dos、label-id=0x370deffb，两个分区的start/size/type与上面证据相符。

3. 仅预演修改，不写卡。`printf`提供`size=120066048`和换行；管道传给sfdisk。`-N 2`只修改第二分区，未指定的start/type保留；size以扇区为单位。`--no-act`不写设备，`--no-reread`跳过磁盘占用检查，`--no-tell-kernel`不请求内核更新分区边界，两个wipe选项禁止清除签名。不能删除`-N 2`。

   ```bash
   printf 'size=120066048\n' | sfdisk --no-act --no-reread --no-tell-kernel --wipe never --wipe-partitions never -N 2 /dev/mmcblk0
   ```

   预演新表应保留p1不变，p2 Start=2101248、End=122167295、Sectors=120066048、Id=83。遇到不支持的参数、报错、其他修改或签名删除提示则停止。预演结束如需查看退出状态，立即执行`echo $?`，应为0；其他命令执行后再查不代表该预演的状态。

4. 正式写入第二分区的新长度。与预演相比去掉`--no-act`，添加`--backup`及`-O`，后者指定原始分区表扇区备份文件前缀，sfdisk会追加设备名和偏移。其余保护和目标保持相同；这一步会写分区表。

   ```bash
   printf 'size=120066048\n' | sfdisk --backup -O /root/sd-expand-20261003/ptable --no-reread --no-tell-kernel --wipe never --wipe-partitions never -N 2 /dev/mmcblk0
   ```

   紧接着检查退出状态：

   ```bash
   echo $?
   ```

   应为0；非0或任何异常不要继续，不要反复写入、强制操作或盲目重启，保留输出再分析。

5. 核对卡上的新表：

   ```bash
   sfdisk --dump /dev/mmcblk0
   ```

   磁盘ID和p1应保持原值；p2应为start=2101248,size=120066048,type=83。此时内核里的p2和df可能仍为26G，是刻意未通知内核的结果，不直接运行resize2fs。

6. 同步待写数据，再正常重启：

   ```bash
   sync
   reboot
   ```

   `sync`提交文件系统待写数据；`reboot`正常重启，让内核重新加载扩大后的分区边界。等待串口启动并重新登录，不用断电替代正常重启。

7. 重启后核对内核看到的分区长度和根挂载：

   ```bash
   cat /sys/class/block/mmcblk0p2/size
   findmnt -no SOURCE,FSTYPE,OPTIONS /
   ```

   第一条以512字节扇区显示长度，应为120066048；第二条应仍为/dev/mmcblk0p2、ext4、rw。长度不符、根来源变化或只读挂载则停止。此时df仍约26G是正常的，因为尚未扩大ext4。

8. 扩大ext4文件系统：

   ```bash
   resize2fs /dev/mmcblk0p2
   ```

   不指定新容量会使用整个分区。扩大的已挂载ext4依赖板端内核支持在线扩容；成功时会报告新文件系统块数。若不支持在线扩容或要求离线检查，停止并提供原文；不要对挂载的根分区执行e2fsck，不强制resize，不格式化。

9. 写回并验证结果：

   ```bash
   sync
   lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
   df -hT /
   ```

   lsblk的p2应约57.2G且仍挂载/；df的ext4总容量应明显由26G增加到约56–57GiB，具体显示取决于文件系统元数据和舍入，可用容量不等于分区总容量。将正式写表、重启后长度、resize2fs和df输出发回，供补全实际扩容验收。

依据：[Ubuntu 20.04 sfdisk手册](https://manpages.ubuntu.com/manpages/focal/man8/sfdisk.8.html)、[Ubuntu 20.04 resize2fs手册](https://manpages.ubuntu.com/manpages/focal/man8/resize2fs.8.html)。本说明只给出本次已核对的配置，未在板端执行，不保证未核验的内核在线扩容能力。
