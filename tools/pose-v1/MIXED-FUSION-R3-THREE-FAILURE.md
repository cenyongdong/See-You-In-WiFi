# r3三样本停止：不同输入得到相同输出

一次执行mixed-three并完整回传，代理只审阅本机数据及SDK资料，未重跑或接入设备。
退出1、stderr/failure均为All outputs identical for distinct CSI; review needed，阶段failed_stop_no_retry。
四次前向308/309/310/308均完成后触发不同输入响应门禁；无成功summary，不生成mixed-three.acceptance.json。
61回传/291包/12参考哈希、程序/SDK/设备、12注册和原1173融合绑定核验通过。
真实RAW参数保持，完整dmesg前后相同，available均689MiB/Swap0；未见本次新增OOM/总线错误。

## 已验证事实

三个PS输入均10800有限FP32、与固定及ONNX输入逐位一致，三个哈希不同。

| 与308相比 | 309 | 310 |
| --- | ---: | ---: |
| 输入逐位不同元素数 | 10431 | 10445 |
| 输入最大绝对差 | 8.89354134 | 10.80150604 |
| ONNX分数变化元素数 | 100 | 100 |
| ONNX坐标变化元素数 | 4200 | 4200 |
| 板端分数变化元素数 | 0 | 0 |
| 板端坐标变化元素数 | 0 | 0 |

三个样本及重复308的完整4300输出均逐位相同，也与先前mixed-one的308输出相同。
分数SHA2560e12e7424bd8ff8b24df1006314d7d52c98572a5f4a22f3f496e9eff0cd32092，
姿态SHA256bbf3135cb79f2b77b17d8820f934217736f8c1c27e3f48dbd83544ac4e1f58bd。
输出有限，首样本同Session和跨Session重复一致，但**不同输入响应没有通过**，整体三样本工程失败。
每次有七ZG/六计算Host及Input0回调，共56条调度记录；32次桥搬运。
回调/元数据存在不能单独证明每次硬件消费了新的帧数据。
前向207.1123/39.10712/38.51481/38.37844ms，仅为失败运行观测；后续约39ms不能用于宣称性能改善或5Hz通过。

## 尚未定位的边界

原程序在每次forward前创建并写入新Host输入Tensor，但没有转储该实际Tensor或Input0返回内容。
SDK public Session.forward接收输入列表；私有tmap_/ready状态存在不证明缓存错误。
本机明文Host Input注册返回inputs，这不能替代板端编译实现/Session路径的实测。
当前无法在实际Host输入→Input0→首ZG结果→CPU暂存→最终输出间定位内容何处保持旧值。
输入更新、张量生命周期/重用、就绪状态及后端数据复用是候选原因，不能直接认定SDK缓存、DMA或模型故障。
SDK时间字段单位未确认，部分other负数也不能作为完成同步的证明。

完整失败核验（历史附件，当前仓库未附：`evidence/mixed-20261006-fusion-r3/mixed-three-failure-review.json`）、
SDK只读审查（历史附件，当前仓库未附：`evidence/mixed-20261006-fusion-r3/mixed-three-SDK-source-review.json`）。
保留原包、程序和61项结果，停止三样本重跑/正常ONNX数值验收/性能及后续显示推进。
正常compare要求三样本工程验收，本次不绕过或伪造该门禁；已有单样本差异仅保持初步记录。
下一步[逐次输入内容诊断方案](MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md)待批准，不修改SDK或自动修复。
