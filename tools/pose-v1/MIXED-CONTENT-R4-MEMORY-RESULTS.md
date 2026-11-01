# r4 SDK内存往返验收

一次执行并完整回传，代理仅本机核验，无设备接入或重跑。
退出0、stderr空，28回传/291包/15ARM头文件/两库/3.39.0及程序ba8d5398…15dcea7身份匹配。
device25122301/icore24160628及固定AXI URL保持；两16KiB缓冲区均ADDR、AXIZG330AIPLDDRMemRegionNode，offset0/chunk16384。
三组模式六份回读共24,576有限FP32逐位一致含正负零，也与r3已验收回读一致。
程序检查SDK区域所属设备及分配不重叠，未输出绝对地址，不作独立地址映射验收。
完整dmesg前后相同，available均685MiB/Swap0，不作峰值内存或性能结论。
content_capture=false，无完整Session或模型前向，不证明连续Input0更新/NPU生产者同步。

[独立复核](evidence/mixed-20261006-content-r4/memory-independent-review.json)、
[内存门禁](evidence/mixed-20261006-content-r4/memory-check.acceptance.json)已保存。
下一步仅[MIXED-CONTENT-R4-COMMANDS.md F](MIXED-CONTENT-R4-COMMANDS.md)传新内存门禁后一次300秒apply-only并完整回传。
r3同输出根因仍待内容前向取证，不自动复位或重跑旧目录。
