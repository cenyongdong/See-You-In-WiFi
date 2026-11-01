# mixed-r1真实参数与PS离线验收（2026-10-06）

## 工程内容总结

保留上次缺gate预检目录后完成正式offline-check并完整回传；代理读取日志、运行文件核验并独立复查参数/输入。
Lite ARM Icraft/CustomOp3.39.0，程序SHA2567cf761f1dd7d1ca1bf8a1db1826e4d9b34574b1a8dc0ac662c987eed52722a17保持。
原ZG图/RAW包290项、回传32项哈希、15SDK头文件/Host＋ZG库/程序/上一Host验收身份匹配，ldd完整。

| 真实参数 | 值编号 | 字节数 | 实际核验 |
| --- | --- | --- | --- |
| TopK188输入1 | 484 | 4 | 有限FP32，K=100 |
| TopK437输入1 | 1135 | 4 | 有限FP32，K=100 |
| ScatterND582输入1 | 1550 | 50,400 | 12,600有限整数，实际排列为完整100×14×3坐标网格，各轴范围0..99/0..13/0..2 |
| ScatterND649输入1 | 1726 | 50,400 | 同上，两个真实索引转储相同 |

固定检查器通过SDK lazyLoadParamsFromFile装载原RAW，检查Params.hasData、dtype/存储和合法值后转储。
本模式没有用fixture替换参数；这里未开发通用RAW二进制格式解析器。
308/309/310三份原始CSI的PS输入共32,400 FP32，有限且与固定参考、已生成ONNX输入逐位一致。
图接口在检查器中核对为[1,180,60]→分数[1,100]/姿态[1,100,14,3]；1173HardOp/六Host为静态图规格，尚非Session绑定验收。
12条注册记录匹配，五缺失节点补齐、Gather保持。

退出0、stdout/stderr空，无failure.json；stages完整为started→real_parameters_validated→registered_before_session→offline_validation_completed。
mode=offline-check/device_init_allowed=false，没有Device::Open、完整Session或算子前向。
完整dmesg前后相同，无新增内核消息；available686→687MiB、Swap0为前后快照。
纯PS预处理三次为15.35236/5.60302/5.58911ms，不作原因推断或连续性能验收。

证据：[offline-check.acceptance.json](evidence/mixed-20261006-r1/offline-check.acceptance.json)、
[独立复核](evidence/mixed-20261006-r1/offline-independent-review.json)，完整回传evidence/mixed-20261006-r1/offline-check。
代理只执行文件分析，没有接入板端、运行模型、修改源码/SDK/模型或重编译。

## 对后续开发的参考

已证明真实RAW中四个CPU参数可物化、当前三份原始输入经PS处理与部署参考一致，并通过图/注册门禁。
仍未证明设备区域、ADDR/BOTH搬运、NPU生产者到CPU消费者的同步、Session绑定或混合精度。
下一步按批准方案，仅SDK两16KiB缓冲区往返（30秒、显式设备初始化），核验后再Session部署。
执行前人工确认BOOT/JTAG保持且无其他AI/显示访问；未知则暂停。失败保存完整日志，不自动重试/复位/改配置。
SDK内存往返即使通过，也不是NPU写入/CPU读取同步或推理数值通过。
