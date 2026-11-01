# 随机初始化训练 epoch4：Icraft 上板对照候选

> 本页为历史模型记录，仅说明文档纳入 Git；下列本机附件不随克隆提供。当前部署模型见 [模型索引](../README.md)。

**最终状态（2026-10-29）：** 从零训练 epoch4 已在 10 月 28 日完成有限实板对比，1989 次新推理、HDMI 采纳与 PC 发送，正常退出。现场未确认明显改善，最终演示恢复原 epoch99，本候选保留历史；[板测结果](../../software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md)。下文转换与 Host 差异仍限定于当时样本；旧自采原始数据已清理，不保证原训练可直接复跑。

2026-10-28。本候选来自随机初始化后仅用现场数据训练的最佳epoch4，不是未经训练的随机权重。已完成CPU ONNX导出、Icraft 3.39.0 FP16五阶段转换和生成图Host核对；初次转换时尚未部署；后续有限实板结果见文首更新。

## 供后续对照的文件

| 路线 | ONNX | 板端JSON／RAW模型包 |
| --- | --- | --- |
| 随机初始化训练 epoch4 | 本模型（本机附件：`source/onnx/pose180_shared.onnx`） | 独立模型包（本机附件：`../../Deliverables/history/models/piw24_kinect_scratch-e4-20261028-r1-model.tar.gz`） |
| 原模型微调 epoch13 | 微调模型（本机附件：`../piw24_kinect_finetune-e13-20261028-r1/source/onnx/pose180_shared.onnx`） | 微调模型包（本机附件：`../../Deliverables/history/models/piw24_kinect_finetune-e13-20261028-r1-model.tar.gz`） |

两包均只含模型与身份／核对记录，不包含启动程序、SDK或BOOT。板端文件为 `piw24_pose180_ZG.json` 和 `piw24_pose180_ZG.raw`，必须成对使用；解压后位于各自候选名下的 `models/`。应分别接入独立启动目录并同步模型身份，不直接覆盖另一会话的启动包或绕过身份检查。

两版沿用相同输入预处理、同一TOML转换配置、FP16、zhuget330目标、4×4单核。外部FP32输入为 `[1,180,60]`，输出为 `scores [1,180]` 和 `poses [1,180,14,3]`。后续比较应保持CPU TopK=1、滤波参数、输入片段和显示设置一致；不修改HDMI或帧协议。

## 来源与实际核对

最佳权重来自 `/public/cyd/kinect-calibrated-20261028-r1/scratch-r1/best_top1_mpjpe_epoch_4.pth`，按固定1200条验证子集的Top1 MPJPE选出。独立快照在同根目录 `preview-scratch-export-r1/checkpoint.pth`；初始化记录确认训练起点没有加载预训练权重。

CPU严格加载555项已训练参数，opset11导出，ONNX检查及三个现场TRAIN样本数值核对通过。ONNX Runtime与PyTorch最大坐标差为0.000003338 m，低于既有0.00002绝对差门限。三个输入与微调候选逐字节相同；FP32参考输出分别来自各自模型。

Icraft五阶段原生退出码均为0，转换耗时27.64秒。最终图为950个HardOp，无Host计算、TopK、GatherElements或ScatterND，JSON／RAW身份匹配。三个生成图Host样本输出尺寸正确且全部有限：

| 现场样本 | FP32／FP16 Top1索引 | Top1单关节最大偏差 | Top1关节平均偏差 |
| --- | --- | --- | --- |
| batch-r5-1_144 | 147／147 | 5.57 mm | 4.03 mm |
| batch-r6-2_4150 | 147／147 | 10.13 mm | 7.14 mm |
| long-r4_4460 | 147／147 | 9.62 mm | 6.99 mm |

全部候选单关节最大转换偏差25.09 mm。以上差值表示FP16相对该模型FP32的变化，不是对真实骨架的MPJPE，也不能用来证明随机初始化模型比微调模型更准。相同Top1索引不表示三帧输出坐标相同。

仅认定转换及Host执行成功，不认定实板精度或效果通过。完整验证／留出测试比较及单人同场景、部分坐标标定、RF／曝光对时边界见最终训练比较（本机附件：`../../.local/kinect-calibrated-20261028-r1/COMPARISON.md`）。导出阶段曾优先建议微调路线；后续实物对比未确认改善，最终恢复原 epoch99。

## 复现与记录

- 导出：`../../tools/kinect/export_preview.py`，`--run` 指向scratch-r1，使用新的输出目录；原生日志保存在服务器 `preview-scratch-export-r1.log`。
- 转换：复用 `../../tools/pose180/deploy/convert.py`，导入后将 `OUT` 指向本独立目录；Host使用同目录的 `reference.py --generated`。
- 数值比较：`../../tools/kinect/compare_icraft_preview.py --model-dir <本目录>`；只读取现有输出、保存差异，不执行推理，也不覆盖旧报告。
- 冻结权重身份：`source/checkpoint-identity.json`；ONNX验证：`source/onnx/verification.json`；转换和原生日志：`conversion.json`、`logs/`、`reference-generated/`；完整差异：`host-comparison.json`；交付身份：`candidate.json`。

本次没有启动新训练、采集或板端负载，原微调候选、原epoch99及其它会话的运行程序保持。
