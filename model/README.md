# 模型与部署资产

当前演示采用原始 epoch99 的 180-query 共享关节细化图。板端实际使用的文件位于 [piw24_pose180_shared-20261024-r1/](piw24_pose180_shared-20261024-r1/README.md)，同一模型也包含在 [最终部署包](https://github.com/cenyongdong/See-You-In-WiFi/releases/download/deploy-r4-20261031/pose180-csi-release-20261031-r4.rar) 的 `board/models/` 中。

## 克隆仓库后可直接取得

| 文件 | 用途 |
|---|---|
| [piw24_pose180_ZG.json](piw24_pose180_shared-20261024-r1/piw24_pose180_ZG.json) | Icraft 最终部署计算图 |
| [piw24_pose180_ZG.raw](piw24_pose180_shared-20261024-r1/piw24_pose180_ZG.raw) | 与 JSON 配套的板端权重，约 35.0 MB |
| [pose180_shared.onnx](piw24_pose180_shared-20261024-r1/source/pose180_shared.onnx) | 已导出的共享细化 ONNX，约 52.7 MB，可作为 Icraft 转换输入 |
| [piw24_pose180.toml](piw24_pose180_shared-20261024-r1/piw24_pose180.toml) | Icraft 3.39.0 五阶段转换配置，按本目录相对路径运行 |
| [identities.json](piw24_pose180_shared-20261024-r1/source/identities.json) | 原训练与导出文件的 SHA-256 身份记录 |

部署图与权重须配套使用。格式转换、模型数值与实板运行分别验证，结果见 [部署实测](../tools/pose180/deploy/RESULTS.md)。直接演示不需要重新训练或转换，按 [部署说明](../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md) 使用完整包即可。

## 本机保留的开发产物

训练权重 `piw24_pose180_shared-20261024-r1/source/best_mpjpe_epoch_99.pth` 为 274,727,776 字节，超过 GitHub 普通 Git 的 100 MiB 单文件限制，继续保留在本机；其校验值见上方身份文件。当前未通过 Git LFS 分发该 checkpoint，也没有已发布的该 checkpoint 下载链接。需要恢复训练时，应向项目维护者取得这一文件并核对身份；现有 ONNX 和 ZG 文件足以供转换或部署使用。[GitHub 大文件说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)

转换中间阶段 JSON／RAW、参考输出、原生日志及历史候选权重不随 Git 克隆提供。旧自采训练数据已清理，历史训练命令不保证可直接重跑。

## 历史模型说明

| 模型 | 用途与最终选择 |
|---|---|
| [自采微调 epoch13](piw24_kinect_finetune-e13-20261028-r1/README.md) | 有限实板比较候选，未作为最终演示模型 |
| [自采从零 epoch4](piw24_kinect_scratch-e4-20261028-r1/README.md) | 有限实板比较候选，最终恢复原 epoch99 |
| [180-query 从零训练](piw24_pose180_scratch130-20261027-r1/README.md) | 独立训练实验记录 |
| [早期共享细化图](piw24_shared-20261015-r1/README.md) | 100-query 阶段的转换与实板记录 |
| [早期 no-scatter 图](piw24_noscatter-20261014-r3/README.md) | 早期去 ScatterND 的 Icraft 转换记录；r1／r2 为此前失败取证 |

历史目录只放行说明文档，其正文标注的本机附件和旧权重不作为当前部署入口。

2026-10-31轻量交付：最新源码RAR也包含上述JSON／RAW／ONNX及转换配置；不含原始PyTorch训练检查点。完整原始checkpoint留在工作目录，源码包不代表能够从中恢复优化器续训状态。
