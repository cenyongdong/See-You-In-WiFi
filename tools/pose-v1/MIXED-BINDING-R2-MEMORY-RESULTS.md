# 绑定快照r2 SDK内存往返验收

完成一次受限memory-check并完整回传，代理仅本机分析，无板端接入/重跑。
程序退出0、stderr空，28回传/290包、15ARM头文件/Host与ZG库/Icraft及CustomOp3.39.0身份匹配。
新r2程序SHA25694a03a903a4a97f229b1549dcbd1bade193d60dbb23753c1f030431fbd061248。
SDK Open/version匹配device25122301、icore FMSHZGV3TECH-AID - 24160628，固定AXI URL保持。

两个16KiB缓冲区均ADDR、AXIZG330AIPLDDRMemRegionNode，offset0/chunk16384/已分配。
固定程序验证defaultMemRegion所属Device及两地址不重叠；绝对地址未输出，不作独立地址映射验收。
三组模式六份回读共24,576有限FP32值逐位一致，包括左首值-0和右首值+0，也与r1已验收模式回读一致。
完整dmesg前后相同，available723→724MiB、Swap0；这不是峰值内存/连续性能测试。
stage=sdk_memory_roundtrip_completed_not_NPU_coherence_proof，未创建完整Session或模型前向。

[独立复核](evidence/mixed-20261006-binding-r2/memory-independent-review.json)、
[新r2内存门禁](evidence/mixed-20261006-binding-r2/memory-check.acceptance.json)已保存。
仅证明SDK CPU↔设备数据复制，不证明NPU生产者/CPU消费者同步、完整模型绑定或精度。
下一步按[命令G](MIXED-BINDING-R2-COMMANDS.md)，一次300秒apply-check收集创建后/部署后的十份公共元数据快照。
旧严格门检可能仍退出1，全部证据均须回传；不做模型forward、自动重试/复位或生成apply验收。
