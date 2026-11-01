# 当前 180-query 共享 FP16 模型

本目录提供最终演示所用的原始 epoch99 模型部署资产。输入为已预处理 FP32 CSI 特征 `[1,180,60]`，输出为 180 个候选分数及 `180×14×3` 关节坐标；候选选择和姿态滤波由 PS 完成。

Git 中提供以下文件：

- [piw24_pose180_ZG.json](piw24_pose180_ZG.json) 与 [piw24_pose180_ZG.raw](piw24_pose180_ZG.raw)：配套的板端计算图与权重。
- [source/pose180_shared.onnx](source/pose180_shared.onnx)：已导出的 ONNX。
- [piw24_pose180.toml](piw24_pose180.toml)：实际 Icraft 3.39.0 转换配置。
- [source/identities.json](source/identities.json)：训练 checkpoint 和 ONNX 的来源身份。

`source/best_mpjpe_epoch_99.pth`、转换中间产物、参考输出及日志仅保存在本机；文件获取方式及 Git 范围见 [模型索引](../README.md)。直接演示可使用 [完整部署包](../../Deliverables/pose180-csi-release-20261031-r4.rar)，无需重新转换。

数值检查、实际板测原值、30 分钟 124,518 次模型压测及恢复入口见 [实测结果](../../tools/pose180/deploy/RESULTS.md)。运行稳定性记录不替代数值精度验收；本次文件补齐没有重新执行模型转换或板端验证。

2026-10-31轻量交付：最新源码RAR也包含上述JSON／RAW／ONNX及转换配置；不含原始PyTorch训练检查点。完整原始checkpoint留在工作目录，源码包不代表能够从中恢复优化器续训状态。
