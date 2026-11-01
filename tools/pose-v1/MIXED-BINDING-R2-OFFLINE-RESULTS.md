# 绑定快照r2离线门检结果

人工操作Lite离线检查并完整回传；代理仅分析本机文件，未接入板端或重跑程序。
退出0、stdout/stderr空，started→real_parameters_validated→registered_before_session→offline_validation_completed。
32项回传及290项包校验通过，程序94a03a90…bd061248、15份ARM头文件、两后端库及Icraft/CustomOp3.39.0身份匹配。

真实RAW参数：TopK188/437分别读取value484/1135，两个K均100；ScatterND582/649分别读取value1550/1726，
各50,400字节、12,600个有限FP32索引，与完整[100,14,3]坐标网格逐位一致，且与r1已核验参数一致。
检查器按固定图调用SDK lazyLoadParamsFromFile并验证参数存储，未使用合成fixture替代。
三份CSI输入308/309/310、frame6/7/8共32,400有限FP32值，与固定参考及ONNX参考输入逐位一致。
12注册记录符合预期，Gather保持；PS预处理观测5.67611/5.51163/5.55515ms，不作持续性能结论。
完整dmesg前后相同、available均723MiB、Swap0；mode=offline-check、device_init_allowed=false。
未初始化设备、创建完整Session或运行NPU/前向，不是完整模型数值验收。

证据：[独立核验](evidence/mixed-20261006-binding-r2/offline-independent-review.json)、
[离线验收文件](evidence/mixed-20261006-binding-r2/offline-check.acceptance.json)。
此前失败预检保留在offline-preflight-missing-gate，本次正式结果在offline-check，互不覆盖。
下一步仅执行[命令F](MIXED-BINDING-R2-COMMANDS.md)：传入新r2离线门禁，再一次30秒SDK两16KiB缓冲区往返并回传。
该测试需初始化设备；BOOT/JTAG身份保持且无其他AI/显示访问才执行。memory通过前不进入apply或mixed。
