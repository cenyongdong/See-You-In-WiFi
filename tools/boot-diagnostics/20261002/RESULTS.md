# Lite SD 启动只读排查（2026-10-02）

**后续状态更新（2026-10-02，现场确认）**：已更换 SD 卡并重新完成启动卡制作、上板验证；串口正常输出，能够登录板载 Linux。本文及其后续失败复核记录针对旧卡和当时连接，不用于判定当前新卡。旧卡异常证据仍保留，精确故障归因不因新卡启动成功而自动确诊。新卡确认见 [记录](../../sd-image-validation/20261002-new-card-board-confirmation.json)，项目最新状态见 [REFERENCES.md 第 15 节](../../../REFERENCES.md)。扩容尚未执行/验收，实际操作人工完成。

已发现 SD 启动介质内容异常：当前卡 FAT 分区的 BOOT.bin 与源镜像不一致，且文件头无有效源镜像启动头。后来补充参考 BOOT 替换，已额外和该指定参考 BOOT 比较，仍不一致。卡损坏、读卡器故障、写入流程/文件系统异常等底层原因尚未区分；不能将此结论扩大为开发板已损坏或 SD 为假容量卡。

## 已验证事实

- Windows 10、悟净 Lite、Procise 2025.1.1 temp / SVN 32494。
- COM7 为 CP210x USB-UART。关闭占用会话后，115200/8N1/无流控/DTR和RTS关闭，成功打开接收；150 秒窗口覆盖断电重启，接收 0 字节，结束后释放串口。
- JTAG 只读扫链识别 jfmql30 part 0（0x9372c093）、ps_dap part 1（0x6ba00477）；只读 STAT=0x40001f0c。未解释缺少复旦位定义依据的状态位。
- 人工确认 SD 模式、重新上电、D18/D19/D20/D21/D8 常亮；原理图分别对应四颗 PL 灯及 INIT_B，亮灯不等于 Linux 正常启动。跳线具体引脚位置尚未独立复核。
- 源镜像为带 512 字节头的 imageUSB 格式。前次完整 payload 的 MD5/SHA1 与内置摘要一致。此次按 FAT16 目录与簇链提取源启动文件摘要。
- 当前 SD 为 Disk 3、读卡器序列号 121220160204、报告容量 67,101,834,240 字节。E: FAT 分区和 F: Linux 类型分区起始/大小与源镜像相符；E: HealthStatus=Warning，未执行修复。
- E: 根目录 9 个启动相关文件，仅 FSBL251210_ddr400_demo.out 与源镜像匹配，其余 8 个不匹配。
- BOOT.bin 大小两者均为 7,023,552 字节，实际 3,445,904 字节不同。源 SHA256=c87b7959cd9980520324b2c17688d9b7c1e85358bfcef085b1b00bd5a4d2f121；卡 SHA256=3761c210ec71bcd27d03762e8b37d30b8f855299c74af45c451c9be3d770a1b5。
- 源 BOOT.bin 前四字节为 fe ff ff ea，卡为 49 4d 41 47（IMAG），后续类似 FAT 目录项。卡上 Image、u-boot、bl31.elf、uEnv.txt 的开头也出现类似目录项，显然不是相应有效程序/文本。
- uEnv.txt 两者 1,499 字节，有 1,496 字节不同；源包含 baudrate=115200，卡为目录样数据。BOOT.bin/uEnv.txt 第二次文件读取与第一次摘要一致；仍待拔插后复核以排除缓存影响。
- 只读打开 PhysicalDrive3 仍因 Windows 权限拒绝，未执行全卡扇区比较或真实容量验证。

## 结论与限制

当前 SD 启动文件无效，是板子无法由此卡正常启动的已确认阻断项；与此前两次写后校验失败一致。禁用校验后的 Imaging successfully 不代表写入内容正确。零串口输出与早期启动未执行相符，但不能凭此排除额外 UART/启动模式/硬件故障。

本次未重写/格式化 SD、修改 BOOT/uEnv、下载 FPGA 位流、写 Flash、重置 PS 或修改永久配置。后续修复需按 AGENTS.md 对明确方案单独批准。

## 证据

- diagnostic-status.json：串口与只读 JTAG 实测。
- com7_20261002_123044.log/.bin：串口捕获。
- scan.stdout.log、read-stat.stdout.log：原生只读 JTAG 日志。
- source-boot-manifest.json：源镜像 FAT 启动文件清单/摘要。
- card-fat-file-comparison.json：卡上 9 个文件摘要与源匹配结果。
- boot-byte-comparison.json：BOOT/uEnv 逐字节差异和复读摘要。

## 拔插后复核（12:41）

安全弹出后重新插拔 USB 读卡器。重新枚举确认同一序列号、Disk 3、E: 分区起始/大小，再读 9 个文件，仍仅 FSBL 与源匹配，8 个不匹配。BOOT.bin 新 SHA256=6ec99ec782642a5053178fdd2e6f696f69a030724ae866dcd91516ced84d238b。7 个文件的摘要相较拔插前发生变化；ai7030_top_disable_icap.bit 和 FSBL 保持原摘要。没有本任务主动文件改写/SD 写入；Windows 挂载或访问文件时可能更新文件系统元数据，不能仅凭跨挂载摘要变化就认定随机读取错误。BOOT/uEnv 内容异常的结论在重新连接后仍成立。

证据：card-after-replug.json、replug-hash-changes.json。下一项待补充另一只读卡器进行只读对比；当前仍无法将底层原因单独归给卡或读卡器。不能仅以“64GB”认定不兼容，不能将报告容量认定为真实容量。

## 补充指定参考 BOOT 后的核对

指出教程要求替换参考实现 BOOT，并指定下载区“悟净LITE版_BOOT_25122301_单路PLIN+pHDMI(外置detpost)”双层目录。实际文件名是 BOOT.bin（非 BOOT.bint），7,023,552 字节，SHA256=ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef，开头 fe ff ff ea，偏移32包含66 55 99 aa和FMSH标记。卡 BOOT 大小相同、SHA256=6ec99ec782642a5053178fdd2e6f696f69a030724ae866dcd91516ced84d238b，当前开头64字节全零，与此参考有2,254,275字节不同（首个差异偏移0）。证据：reference-boot-comparison.json。

修正结论依据：原镜像 BOOT 与指定 BOOT 的差异可能来自正常替换，不能仅据“BOOT 与原镜像不匹配”认定损坏；本例与指定参考 BOOT 也不匹配且当前启动头无效，其他启动文件异常独立存在，因此介质异常结论仍成立。此前3,445,904差异字节数仅指原镜像对比，并不是相对于选定参考的损坏字节数。人工确认：在本次插卡启动之前已经执行该参考 BOOT 替换。

人工确认没有备用读卡器，暂无法完成替代读卡器复读。未将此备用设备缺失解释为任何特定硬件的确诊。


补充：自行打开卡上 uEnv.txt 观察到乱码；读卡器为购买内存卡所赠，品牌/型号仍未知。赠品来源不作为读卡器故障的确诊证据，与既有逐字节比较共同确认 uEnv 内容异常；全容量检测尚未获明确批准、未执行。
