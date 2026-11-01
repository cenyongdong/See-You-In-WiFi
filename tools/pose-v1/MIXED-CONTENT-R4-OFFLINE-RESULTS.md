# r4离线门检验收

一次执行完整回传，代理仅本机核验，无设备接入或重跑。
退出0、stdout/stderr空，32回传/291包项、15ARM头文件/两库/3.39.0及程序ba8d5398…15dcea7身份匹配。
真实RAW TopK188/437的K均100，ScatterND582/649各50,400字节/12,600有限FP32索引，与完整[100,14,3]坐标网格一致，四参数与r3转储逐位一致。
308/309/310三PS输入共32,400有限FP32与固定/ONNX/r3参考逐位一致，12注册及原Gather保持。
预处理观测5.66225/5.52195/5.54218ms，不作持续性能结论。
完整dmesg前后相同，available均686MiB/Swap0；content_capture=false，无Device::Open/Session/NPU。

[独立核验](evidence/mixed-20261006-content-r4/offline-independent-review.json)、
[离线门禁](evidence/mixed-20261006-content-r4/offline-check.acceptance.json)已保存。
下一步仅[MIXED-CONTENT-R4-COMMANDS.md E](MIXED-CONTENT-R4-COMMANDS.md)传新离线门禁后一次30秒SDK内存往返并回传。
BOOT/JTAG及设备无竞争访问须保持；真实Session逐次内容仍待取证，不直接apply/forward。
