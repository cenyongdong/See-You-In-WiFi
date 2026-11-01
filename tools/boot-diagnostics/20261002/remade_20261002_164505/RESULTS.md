# 重制 SD 卡后的只读复核（2026-10-02 16:45）

## 工程内容总结

结果：当前检查未通过。明确说明本次仍未开启 imageUSB 写后校验，尚未用 Lite 参考 BOOT 替换。因此本次全部启动文件应与原 imageUSB 镜像一致。

Windows 10，重新枚举相同 USB 读卡器序列号121220160204、Disk3、报告容量67,101,834,240字节；E: FAT分区偏移1,048,576、大小1,073,741,824字节；F: Linux类型分区偏移1,075,838,976、大小28,000,000,000字节，符合源镜像布局。分区布局相符不能证明数据内容正确，HealthStatus=Warning未据此单独确诊。

普通文件读取9个文件，仅FSBL与源匹配、其余8个不匹配。不在电脑旁，无法进行本次USB安全弹出/重新连接，未将该操作标为完成。

补充使用 Win32 CreateFileW GENERIC_READ + OPEN_EXISTING + FILE_FLAG_NO_BUFFERING，只读文件数据，VirtualAlloc页对齐64KiB缓冲。先以本地参考目录uEnv.txt作为控制文件，该方法和普通读取摘要一致且符合既有源摘要；再读SD卡9个文件，仍只有FSBL匹配。BOOT.bin全部7,023,552字节为零；fmqlmp-verify.dtb全部15,996字节为零；两个独立bit文件和bl31.elf也全部为零。uEnv.txt返回二进制样内容而非源ASCII启动配置，Image和u-boot也不匹配。

普通读取和无缓存读取的部分内容不同，表明文件数据缓存影响了初读观测；两种读取均没有通过源文件内容核对。不使用跨读取摘要变化作为随机硬件故障的独立证明。无缓存标志只绕过Windows文件数据缓存，不绕过文件系统元数据缓存或硬件/读卡器缓存。

结论：当前可读取的启动内容无效，卡/读卡器/写入链路问题仍然存在，尚不能单独归因于读卡器、卡或软件。没有重新上板测试、全卡原始扇区比对、Linux根分区内容校验或全容量测试；不能宣布当前卡制作成功。

证据：file-comparison.json（枚举和普通摘要）、critical-file-bytes-before-reconnect.json（初读关键字节）、unbuffered-file-comparison.json（控制文件和无缓存复核）。复核脚本为上级 Read-FatUnbuffered.py。本次未改写SD文件、格式化、重制镜像、更新BOOT或进行板端操作。

## 对后续开发的参考

1. 烧录后文件名、大小和分区存在不能替代内容验证；未替换BOOT时，全部启动文件应先与原镜像匹配。
2. Windows普通读取可能保留文件数据缓存。只读NO_BUFFERING可用于补充确认，但无法替代USB重新连接、正确源基线、全盘校验及实板启动。
3. 回到电脑后优先更换已知正常的读卡器进行交叉验证；数据异常已成立，无需将修改启动参数或板端位流作为当前解决方案。任何覆盖写卡、容量检测或修复仍需按既有方案明确批准。

Win32方法依据：https://learn.microsoft.com/en-us/windows/win32/fileio/file-buffering
