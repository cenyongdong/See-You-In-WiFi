# 正式融合追溯r3 SDK内存往返验收

人工操作一次受限memory-check并完整回传；代理仅本机核验，无板端接入或重跑。
退出0、stderr空，28回传/291包项、15ARM头文件/两库/Icraft及CustomOp3.39.0和程序e8d66113…e6c696a8身份匹配。
设备device25122301/icore FMSHZGV3TECH-AID - 24160628、固定AXI URL保持。
两个16KiB缓冲区均ADDR、AXIZG330AIPLDDRMemRegionNode，offset0/chunk16384/已分配。
固定程序验证SDK区域归属及分配不重叠；绝对地址未输出，不作独立地址映射验收。
三组模式六份回读共24,576有限FP32逐位一致，包含正负零，也与r2已验收模式回读一致。
完整dmesg前后相同，available均723MiB/Swap0；不作峰值内存或性能结论。

[独立复核](evidence/mixed-20261006-fusion-r3/memory-independent-review.json)、
[新内存门禁](evidence/mixed-20261006-fusion-r3/memory-check.acceptance.json)已保存。
仅SDK CPU↔设备数据复制通过，未完整Session、NPU生产者同步或模型前向。
下一步仅[MIXED-FUSION-R3-COMMANDS.md F](MIXED-FUSION-R3-COMMANDS.md)：传新内存验收后一次300秒正式apply门检并完整回传。
新原到融合组校验此时才进入ARM Session路径；完整复核前不forward，不重跑旧r1/r2或复用旧门禁。
