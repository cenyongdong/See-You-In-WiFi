# 更换绿联读卡器并重新制作后的只读复核（2026-10-02 19:17）

## 工程内容总结

结论：本次启动文件检查仍不通过。已通过不同USB设备枚举确认读卡器发生变化，不能继续将异常只归因于旧读卡器。尚不能单独确诊卡损坏、假容量或烧录软件问题。

照片显示绿联USB3.0 TF/SD二合一读卡器，具体型号未知。电脑实际枚举 Generic STORAGE DEVICE USB Device / USB序列号000000000819，PNP USBSTOR\DISK&VEN_GENERIC&PROD_STORAGE_DEVICE&REV_0819\000000000819&0，与旧121220160204不同。当前Disk3报告容量67,101,834,240字节，E:1GiB FAT与F:28,000,000,000字节Linux类型分区的起始/大小符合源镜像。

人工确认本次依然没有启用imageUSB校验，尚未替换Lite参考BOOT。因此本次BOOT以原镜像作为预期；没有将“尚未替换参考BOOT”混同为本次文件内容异常的原因。

初读9个文件仅FSBL匹配，8个不匹配；使用Win32 FILE_FLAG_NO_BUFFERING只读文件数据复核也未通过，控制文件在本地参考目录uEnv.txt上与普通读取相符。初次无缓存读取BOOT、DTB、bl31和两个bit全部为零。随后完成新读卡器USB安全弹出和重新插入；重新枚举相同新读卡器与分区后，对9个文件再做普通与无缓存复读，仍仅FSBL匹配，其余8个不匹配。

重插后无缓存BOOT.bin大小7,023,552，SHA256=c1969b87c628b890b871f7dcf77dcc746df5e48526d68f79e37398732b314c33，首64字节全零，共3,772,397个零字节；不是完整全零文件，与初次无缓存读不同。DTB首64字节为零而非源d00dfeed头；uEnv首64字节为零而非源baudrate=115200等文本，SHA256=33ba000a888ab487105fbc68ad2d931406ea0fb3700dfdc03e0395ce48e40606。不能把不同阶段的数据状态混为“最后整份BOOT全零”。

另重新从源imageUSB镜像按FAT16簇链读BOOT/UENV/Image/DTB，四个摘要与此前源记录完全一致，源BOOT启动头、DTB头、uEnv可读文本正常。前次完整payload内置MD5/SHA1核对证据仍保留；本次没有再做整份镜像完整摘要。

NO_BUFFERING仅绕过Windows文件数据缓存，不绕过文件系统元数据和硬件缓存。挂载/读取可能引起Windows元数据更新；不依据跨阶段摘要变化单独认定随机硬件读错。E:HealthStatus=Warning记录但不单独用作诊断。报告容量不证明真实可写容量。

证据：file-comparison.json、before-reconnect-unbuffered.json、after-reconnect-file-comparison.json、unbuffered-file-comparison.json、fresh-source-check.json。读卡器重新连接由现场完成并确认。未改写卡文件、格式化、重写镜像、替换BOOT、运行全容量测试或上板；Linux根分区、全卡容量、修复后启动未验收。

## 对后续开发的参考

1. 更换读卡器后再次制作及重插复读，异常仍可复现；下一步重点验证SD卡/存储链路，不能仅凭商品图或品牌宣布读卡器健康，也不能仅据当前文件异常宣布假容量。
2. 本次尚未参考BOOT替换，应先保证原镜像写入及校验通过，再按明确指定的Lite参考BOOT替换并校对摘要。普通文件和无缓存数据都不匹配时，修改uEnv参数不能修复这些错误数据。
3. 已准备全容量写入/读回测试方案，更新目标为本次新读卡器/SD组合。该操作清空整卡，待明确批准；不把自行重制当成对本工具清卡/写入测试的授权。
