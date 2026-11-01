# 现场微调 epoch13：Icraft 上板预览候选

> 本页为历史模型记录，仅说明文档纳入 Git；下列本机附件不随克隆提供。当前部署模型见 [模型索引](../README.md)。

**最终状态（2026-10-29）：** 微调 epoch13 已在 10 月 28 日完成有限实板对比，2823 次新推理、HDMI 采纳与 PC 发送，正常退出。现场未确认明显改善，最终演示恢复原 epoch99，本候选保留历史；[板测结果](../../software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md)。下文转换与 Host 差异仍限定于当时样本；旧自采原始数据已清理，不保证原训练可直接复跑。

2026-10-28。在训练期间冻结当时微调最优权重，完成 ONNX 导出、Icraft 3.39.0 FP16 转换与生成图 Host 核对。此目录独立于原 epoch99，初次转换时尚未部署；后续有限实板结果见文首更新。

16:45结果更新：两组训练和完整评估已结束，epoch13仍是微调最终最佳轮次，本候选无需重新转换。最终比较（本机附件：`../../.local/kinect-calibrated-20261028-r1/COMPARISON.md`）建议用于有限上板观察；不代表正式演示精度通过。已交付归档保留导出时说明和身份，以下子集选择信息亦为当时原始记录。

## 文件与使用范围

- ONNX：`source/onnx/pose180_shared.onnx`。
- 板端模型：`piw24_pose180_ZG.json` 与 `piw24_pose180_ZG.raw`，必须成对使用。
- 模型包：`../../Deliverables/history/models/piw24_kinect_finetune-e13-20261028-r1-model.tar.gz`；解压后为本候选名称下的 `models/` 及身份、核对记录。它只含模型，不含启动程序、SDK 或 BOOT。
- `candidate.json` 记录最终模型身份；`source/checkpoint-identity.json` 记录冻结权重；`host-comparison.json` 保存完整数值差异。

模型保持既有输入预处理、输入 `[1,180,60]` 和输出 `scores [1,180]`、`poses [1,180,14,3]`，全部外部接口为 FP32。沿用 CPU TopK=1 的选人接口，HDMI 与 PC 帧协议不变；采用本包 JSON/RAW 时，必须在独立启动包内同步模型身份，不能只覆盖原启动包文件或绕过身份检查。另一会话正在修正板端异常释放，本次没有打包其未完成的运行程序，也没有启动板端测试。

## 来源与实际核对

冻结来源为服务器 `/public/cyd/kinect-calibrated-20261028-r1/finetune-r1/best_top1_mpjpe_epoch_13.pth`。冻结副本保留于同根目录 `preview-export-r1/checkpoint.pth`，不依赖训练后续是否替换最优文件。此轮固定1200条验证子集Top1 MPJPE为207.070 mm；导出时尚未完成的完整验证和独立测试，现见上方最终比较链接，不使用子集数值代替最终结果。

CPU 严格加载 555 项权重，opset 11 导出。三个现场 TRAIN 样本（首、中、尾行）上，ONNX Runtime 与 PyTorch 最大坐标差 0.000016213 m，既有 0.00002 绝对差门限通过；不是泛化精度验收。

Icraft 五阶段原生退出码全部为 0，转换耗时 28.98 秒。最终图为 950 个 HardOp，无 Host 计算、TopK、GatherElements 或 ScatterND，JSON/RAW 配对检查通过。生成图三个 Host 样本均成功、输出有限，Top1 索引均保持：

| 样本 | FP32／FP16 Top1 | Top1 单关节最大偏差 | Top1 关节平均偏差 |
| --- | --- | --- | --- |
| batch-r5-1_144 | 161／161 | 15.57 mm | 12.33 mm |
| batch-r6-2_4150 | 173／173 | 8.51 mm | 3.56 mm |
| long-r4_4460 | 179／179 | 24.62 mm | 14.92 mm |

上述是转换前后输出差，不是对 Kinect 真值的 MPJPE。全部候选的单关节最大差为 168.14 mm，不能由 Top1 三例推断全部候选数值一致；完整原始输出和日志保留。本次认定转换及 Host 执行成功，未认定量化精度或实板效果通过。

## 数据边界

模型仅使用单人、同一现场数据。标签采用部分实测的现场米制坐标，H=1.87 m、W=1.90 m、B=0.68 m，未知 A 假设为 0.95 m、水平朝向沿图示；不是完整官方外参标定。14 关节语义与 RF／曝光精确对时仍未确认。它适合做现场有限效果对照，不能作为多人或跨场景效果保证。

## 复现入口

导出入口为 `../../tools/kinect/export_preview.py`；原生调用和冻结身份保存在服务器 `preview-export-r1.log` 与本目录 `source/`。转换复用 `../../tools/pose180/deploy/convert.py`，导入后将模块 `OUT` 指向本候选目录再调用 `main()`；Host 核对复用 `reference.py --generated`，同样指定独立 `OUT`。TOML、每阶段命令、原生退出码与日志在本目录保存，不应在已有日志目录中重复执行或覆盖结果。
