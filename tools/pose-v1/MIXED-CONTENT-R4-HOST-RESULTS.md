# r4 Host回归与内容路径验收

人工操作并完整回传，代理仅本机核验，无板端接入或重跑。
退出0、stderr空，107例（18正常/89拒绝）、12注册、22份CPU输出/59,600有限FP32与固定及r3结果逐位一致，最大差0。
94次桥事件（84输入/10输出）均Host CPTR，Gather原实现保持。
附加纯Host路径完成：两个固定模式各caller读回和Input0别名模拟，共四份43,200字节正例，与独立NumPy模式逐位一致且同句柄/Chunk。
错期望负例保存第五份43,200字节实际数据，matches_expected=false且内容仍与第二模式一致，未修改实际Tensor。
未分配和FP16在读取前拒绝，host-content-check.json及host_content_paths_completed齐全。
五份捕获总216,000字节，SDK Host read及记录机制已在ARM运行验证；这是模拟别名，**没有验证真实Session Input0回调**。

52回传/291包项、15ARM头文件/两库/3.39.0及程序ba8d5398…15dcea7身份匹配。
完整dmesg前后相同，available686→687MiB/Swap0；无Device::Open、Session或NPU，不作性能结论。
[独立复核](evidence/mixed-20261006-content-r4/host-independent-review.json)、
[Host门禁](evidence/mixed-20261006-content-r4/host-check.acceptance.json)已保存。
下一步仅[MIXED-CONTENT-R4-COMMANDS.md D](MIXED-CONTENT-R4-COMMANDS.md)传新Host门禁后一次30秒离线检查并完整回传。
r3不同输入相同输出问题仍未定位，不直接进入硬件或重跑旧r3。
