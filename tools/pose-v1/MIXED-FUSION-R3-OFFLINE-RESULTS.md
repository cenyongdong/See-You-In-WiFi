# 正式融合追溯r3离线门检验收

人工操作一次离线检查并完整回传，代理仅本机核验，无设备接入或重跑。
退出0、stdout/stderr空，32回传/291包项、15ARM头文件/两库/Icraft及CustomOp3.39.0和程序e8d66113…e6c696a8身份匹配。
真实RAW TopK188/437的K均100，ScatterND582/649各50,400字节/12,600有限FP32索引，与完整[100,14,3]坐标网格一致。
四参数与r2已验收转储逐位一致；SDK实际加载参数，没有fixture替代。
308/309/310三份PS输入共32,400有限FP32与固定、ONNX及r2参考逐位一致；12注册符合预期，Gather保持。
PS预处理观测5.65894/5.54286/5.55557ms，不作持续性能结论。
完整dmesg前后相同，available722→723MiB/Swap0；mode=offline-check、无Device::Open、完整Session或NPU。

[独立核验](evidence/mixed-20261006-fusion-r3/offline-independent-review.json)、
[离线门禁](evidence/mixed-20261006-fusion-r3/offline-check.acceptance.json)已保存。
下一步仅[MIXED-FUSION-R3-COMMANDS.md E](MIXED-FUSION-R3-COMMANDS.md)：传新r3离线验收后30秒SDK两16KiB缓冲区往返并回传。
先确认BOOT/JTAG保持、无其他AI/显示竞争访问；未memory验收前不apply/forward，正式融合函数仍待Session路径实测。
