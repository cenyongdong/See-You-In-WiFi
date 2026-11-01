# 正式融合追溯r3 Host回归验收

人工操作Host回归并完整回传；代理仅本机读取证据，无板端接入或重跑。
退出0、stderr空，107例（18正常/89拒绝）、12注册记录及22份输出/59,600有限FP32与固定NumPy参考逐位一致，
并与r2已验收Host输出逐位一致，最大差0。Gather原注册保持。
94次桥记录为84输入/10输出，源目标均Host CPTR，存储及字节长度合法。
45回传/291包校验、15ARM头文件/两库/Icraft及CustomOp3.39.0及新程序e8d66113…e6c696a8身份一致。
完整dmesg前后相同，available均723MiB、Swap0；不作峰值内存或持续性能结论。
mode=host-check/device_init_allowed=false，没有完整Session、设备初始化或NPU前向。

[独立复核](evidence/mixed-20261006-fusion-r3/host-independent-review.json)、
[新r3 Host门禁](evidence/mixed-20261006-fusion-r3/host-check.acceptance.json)已保存。
仅CPU计算/Host数据桥回归通过，正式融合追溯函数尚未在ARM Session路径执行。
下一步仅[MIXED-FUSION-R3-COMMANDS.md D](MIXED-FUSION-R3-COMMANDS.md)传新Host验收后一次30秒离线门检，
完整回传核验前不memory/apply/mixed；旧r1/r2及新Host目录不重跑或复用门禁。
