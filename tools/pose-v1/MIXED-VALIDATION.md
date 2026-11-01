# ONNX参考与PS/NPU混合工程验证（2026-10-06）

**旧链入口（2026-10-29）：** 本页属于早期 pose-v1 诊断／验证，当前部署从[最终进度](../../PROJECT-PROGRESS.md)进入；旧主机路径、板端目录、算子计数与阶段授权不能套用最新演示。

本方案。工程门检和数值验收分阶段；以Windows ONNX完整模型直接对照Lite输出，
不再等待Icraft全CPU Matmul打通。正式模型、权重、PS/NPU分配和首版HDMI/RTSP要求保持。
本机ONNX已运行；新C++候选尚未交叉编译、部署或板端运行。

## 已完成与候选实现

- 独立Conda `.local/pose-v1-onnx-conda`：Python3.10.21、NumPy2.2.5、CPU ORT1.23.2，八个依赖wheel哈希锁定。
  三份固定参考输入生成全部候选；有限性、接口、首样本重复逐位一致通过。详见[参考结果](ONNX-REFERENCE-RESULTS-20261006.md)。
- 独立目标 `pose_mixed_check`，不改原inference_check/CMake或已验收CPU三文件。
  三类注册调用已验收 `cpu_candidate::validate_spec/forward`；Gather442原实现、Matmul仍由ZG图安排。
- SDK桥先验证dtype、布局、全有效分布及实际chunk字节边界，等待输入ready，再复制到新Host CPTR张量；
  内核输出通过SDK写回完整提供的缓冲区，未提供时返回Host张量。部分输出缓冲区拒绝。
  ADDR/BOTH只用于SDK搬运/元数据读取，不解引用；设备区域必须属于已核验Device。
- 离线模式从原RAW懒加载并核对TopK K=100、两份ScatterND整数索引、参数身份/字节数及已加载状态。
  缺少加载数据则停，不用合成参数替换。合成参数仅用于原107例Host回归的独立内存图。
- Session创建前显式注册，任何原有/部分注册变化拒绝。1173个原HardOp须具有ZG绑定，六Host节点须具有Host绑定；
  若SDK只提供融合后的编号、无法追溯原节点，则保存失败讨论，暂不猜测融合映射。
- trace记录帧号、指针类别、区域类型、chunk/offset/字节数、SDK搬运、后端回调、初始化/前向/输出耗时。

## 工程门检顺序

| 阶段 | 上限 | 核验范围 |
| --- | --- | --- |
| 构建 | 不运行程序 | FPAI GCC9.4/CMake3.24.2、15份ARM头文件/Host＋ZG库、源码和AArch64二进制身份 |
| host-check | 300秒 | 新入口和Host暂存桥的107例、12注册记录、22输出/59,600值与原NumPy参考逐位一致；无完整Session/Device::Open |
| offline-check | 30秒 | 原图/RAW、四个真实参数、三原始CSI的PS预处理逐位一致、接口和注册；无设备初始化 |
| memory-check | 30秒 | SDK默认设备数据区域，两16KiB FP32缓冲区、三模式/六回传数据逐位一致 |
| apply-check | 300秒 | 版本身份、Session创建/apply、全部原节点绑定；不forward |
| mixed-one | 180秒 | 仅308前向，六Host及ZG回调、正确有限的全部候选输出 |
| mixed-three | 300秒 | 308/309/310前向后同一Session重复308（共四次），并与单样本阶段逐位对照、检查输入响应 |

每阶段使用新目录，stdout/stderr/退出码、完整dmesg前后、内存、SDK/程序/包身份和LF哈希清单回传。
核验器产生验收文件后人工传入 `gates`；缺少同一程序/包的上一阶段验收文件，runner在运行前停止。
退出0本身不是通过；代理还审阅完整日志、回调及数值。已出现的历史内核消息与本次新增错误区分。

SDK往返通过仅证明本次分配区域的copyFrom搬运，不能代替NPU写入后与CPU读取之间的同步验收。
Linux cache helper不提供这一证明，本候选不调用它。真实桥待mixed阶段确认；Gather原内核的设备输入能力仍须实测。
外部timeout终止后不自动复位/重启或重试，保存现状讨论。

## 数值对照与范围

三样本工程证据通过后，独立比较工具以相同帧/输入对照ONNX与板端100分数、100×14×3坐标。
报告最大/平均绝对误差、RMS、P95、逐位一致性、相同槽位关节L2及双方最高分槽位/最佳姿态差异。
相同槽位不代表候选身份相同；不做GT匹配、多人匹配、MPJPE或物理坐标标定。
实测误差提交讨论容限，不自动标为精度通过。Windows CPU参考耗时不作为板端性能。

新环境和本机参考由代理执行；源码/脚本/日志审阅由代理负责。FPAI编译、传输、Lite运行人工执行，
入口[MIXED-VALIDATION-COMMANDS.md](MIXED-VALIDATION-COMMANDS.md)。
超时、OOM、总线/SDK异常、非有限输出、身份变化、输入响应异常均停止保存；不自动改SDK/BOOT/模型/缓存策略。
ONNX分支失效仅暂停数值比较，独立工程阶段仍按批准方式推进。HDMI/RTSP、5Hz、延迟及30分钟闭环不属于本轮结论。
