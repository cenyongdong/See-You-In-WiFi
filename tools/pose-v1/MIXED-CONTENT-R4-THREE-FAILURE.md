# r4三样本退出1：内容边界分析

## 工程内容总结

一次运行并回传130项文件，代理仅本机分析，未重跑模型或连接设备。
程序正常完成同一Session中的308/309/310/308四次前向后，触发：

```text
STOP: All outputs identical for distinct CSI; review needed
```

退出1是应用的不同输入响应门禁，不是本次已记录的SDK异常、超时或OOM。
不存在summary.json，不生成mixed-three.acceptance.json，不进入正常三样本数值验收。

291项包、程序ba8d5398…15dcea7、ARM Icraft/CustomOp3.39.0、两后端库/头文件、设备25122301/icore24160628、
真实RAW参数及固定输入均通过身份核对。1173原HardOp的七组追溯及八Host保持。
完整内核日志前后相同，available685→686MiB/Swap0，没有本次新增内核故障证据。
每次七ZG和六计算Host回调齐全；总56回调、32次桥搬运。回调次数不独立证明硬件已完成当前帧计算。

### 实际内容证据

68份内容全部有限，共1015040字节。以下为相对第一次308改变的FP32元素数；按原字节比较，包含索引输出。

| 位置 | 309/调用1 | 310/调用2 | 重复308/调用3 |
| --- | ---: | ---: | ---: |
| Caller输入（10800） | 10431 | 10445 | 0 |
| 真实Input0返回（10800） | 10431 | 10445 | 0 |
| TopK188暂存输入（180，来源ZG9185） | 0 | 180 | 180 |
| TopK188索引结果（100） | 0 | 100 | 100 |
| GatherElements192数据输入（7560，来源ZG9186） | 0 | 7470 | 7470 |
| GatherElements192索引输入（4200，来源ZG9186） | 0 | 0 | 0 |
| TopK437分数结果（100） | 0 | 100 | 100 |
| ScatterND582两份暂存输入（各4200，来源ZG9189） | 0/0 | 0/0 | 0/0 |
| ScatterND649两份暂存输入（各4200，来源ZG9190） | 0/0 | 0/0 | 0/0 |
| 最终分数/姿态（100/4200） | 0/0 | 0/0 | 0/0 |

四次Caller和Input0均与各自当前固定输入逐位一致，存储为有界Host CPTR。
两处same_handle/same_chunk均true，但别名本身不能证明NPU已经消费该数据。
调用0和1的全部15份桥内容相同；调用2和3的全部15份桥内容相同。
重复308的Caller/Input0与首次308相同，但前段桥内容不同，不能将本次中间结果视为同一输入的稳定重现。

更直接的分数证据：调用2/3的TopK437结果首项为0.97900390625，首次为0.9482421875，最大差0.03076171875；
最终分数四次首项仍为0.9482421875。静态图显示TopK437输出v1136经过ZG9191中的Cast/AlignAxis/Reshape/PruneAxis/Cast链到最终分数v4446。
因此除首ZG段之外，Host结果进入后续ZG及最终读出路径也必须检查；仅修caller输入不能解释全部证据。
这不能独立区分硬件旧结果、SDK读回/映射、数据上传、同步或内存复用问题。

### CPU计算独立复核

使用本次捕获的真实Host暂存输入和真实RAW K/Scatter索引，在NumPy上分别重算TopK188、GatherElements192、TopK437、ScatterND582/649。
四次共28份结果、52000个FP32逐位一致，包括稳定TopK相同值顺序和完整Scatter输出。
这排除了这些适配内核对本次已收到数据的数学结果错误；不能证明它们收到的是正确当前帧的NPU数据。
原Gather442只有执行及绑定记录，本轮没有其完整输入/结果内容捕获，不扩大为它的真实混合数值验收。

全部三帧及重复帧最终4300个输出与首帧、此前r4单样本和r3首帧一致。
分数SHA256：0e12e7424bd8ff8b24df1006314d7d52c98572a5f4a22f3f496e9eff0cd32092。
姿态SHA256：bbf3135cb79f2b77b17d8820f934217736f8c1c27e3f48dbd83544ac4e1f58bd。
本次forward为212.88942/40.57216/40.62396/40.40210ms；后续较短耗时不能作性能提升或5Hz通过。

## 对后续开发的参考

现已确认：PS预处理→caller→真实Input0内容按帧更新；五适配CPU节点对收到的数据计算正确。
最早观察到未响应的位置是调用1的Input0之后、ZG9185结果经SDK复制进入TopK188的边界。
调用2/3局部前段变化而后段/最终不变，表明不能把问题概括为“所有NPU都没有执行”或“只复用了整个首帧输出”。
当前优先假设为跨帧完成状态/SDK搬运和缓冲区复用问题，仍属推断，尚未证明具体根因。

本机头文件Tensor.waitForReady在ready_已经true时直接返回，否则轮询并将状态置true。
应用桥已有每输入10秒waitForReady；最终输出通过SDK Tensor.dump("SFB")保存。
SDK Session.forward、ZG前向及Tensor.dump的ARM实际内部实现未取得，不能据头文件直接断言ready未重置、dump不等待或SDK有bug。
不强制setReady(false)、增加sleep、清缓存、每帧重建Session、关闭融合或改变NPU分配来试错。

下一步候选为[完成状态与交接取证方案](MIXED-CONTENT-R5-READINESS-PLAN.md)，尚未批准或执行。
保留本次失败目录，停止三样本重跑、正常数值验收和后续显示/性能操作。

证据：[内容复核](evidence/mixed-20261006-content-r4/mixed-three-content-review.json)、
[独立失败复核](evidence/mixed-20261006-content-r4/mixed-three-failure-review.json)、
[本机审计源码](evidence/mixed-20261006-content-r4/review-three-local.py)。审计脚本第一次使用Python3.11订阅语法，已改为兼容3.10的tuple索引后完成；未更改板端程序。
