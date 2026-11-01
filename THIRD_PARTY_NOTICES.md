# 开源许可与第三方内容

本项目原创代码和原创说明文档采用根目录 [MIT License](LICENSE)。MIT 授权仅覆盖贡献者有权授权的部分，不改变已有第三方版权、许可证或分发条件。文件内已有的版权和许可证声明继续有效。

| 内容 | 来源与适用范围 |
|---|---|
| Person-in-WiFi 3D 模型实现及其派生内容 | 上游 [aiotgroup/Person-in-WiFi-3D-repo](https://github.com/aiotgroup/Person-in-WiFi-3D-repo)，Copyright 2022–2023 Hikvision Research Institute；采用 Apache-2.0，原文保存在 [LICENSES/Person-in-WiFi-3D-Apache-2.0.txt](LICENSES/Person-in-WiFi-3D-Apache-2.0.txt)。`tools/pose180/`、模型导出与训练适配中的上游派生部分保留该许可，不能视为仅受 MIT 授权。 |
| 模型、训练权重与官方 CSI 片段 | `model/` 和部署包中的模型及官方数据来自上述项目及其数据发布入口；来源见 [模型说明](model/README.md) 与 [当前30段片段及长测](FPGA/csi_preprocess/LONGRUN.md)；10月29日三片段选材另存历史记录。本仓库不对第三方数据和权重另行授予 MIT 权利；代码的 Apache-2.0 许可也不在这里推定为所有数据的独立使用授权。复用、再发布或商用前须核对相应原始发布条件。 |
| Three.js | [mrdoob/three.js](https://github.com/mrdoob/three.js)，MIT；现有演示包和源码快照内已保留 `software/pc_viewer/node_modules/three/LICENSE`（演示包位于 `pc/` 下）。 |
| ws | [websockets/ws](https://github.com/websockets/ws)，MIT；用于旧 PC 工程的 npm 依赖，由包管理器安装时保留其许可证。 |
| FPGA 厂商示例、生成 IP、BOOT、SDK 和运行库 | `FPGA/` 中带有厂商声明的源码、生成文件及部署包中的相关二进制，遵守各自原有条款，不适用本项目 MIT。包括带 msxbo / Liyang Milian 声明的 HDMI 示例，以及复旦微、Icraft 相关接口和资产；本项目未为这些资产新增再分发授权。SDK 和工具链由使用者通过官方渠道取得。 |
| 比赛指南、厂商资料及引用图片 | 保留原作者及发布方权利；收录用于项目开发、说明和追溯，不因本仓库公开而转换为 MIT。 |

对上游模型的工程适配包括 180-query 部署、共享关节细化计算、部署算子适配和板端输入输出连接；具体实现与实测范围见 [模型说明](model/README.md) 和 [项目进度](PROJECT-PROGRESS.md)。这些修改不代表原创论文模型或数据集由本项目创作。论文引用：Kangwei Yan 等，*Person-in-WiFi 3D: End-to-End Multi-Person 3D Pose Estimation with Wi-Fi*，CVPR 2024。

当前仅保留最新RAR部署及源码／权重交付；旧包清理前保留关键说明、校验与报告，原始工作源码及证据不删除。新源码包包含上游模型原始代码与许可，其许可证边界同样按本页说明理解，分发时应随附本页和所需第三方许可。仓库的公开状态不等于所有附带资料均已获得可任意再发布的授权。

r4本机源码RAR按用户要求包含当前目标必需的厂商EDIF／EDF／IP DCP、PS导出、030ai适配资源和增量基线；这些仍适用原厂条款。11月1日完整重建证明的是给定适配工具环境中的工程级依赖完整性，不为厂商资产新增许可，也不表示厂商IP闭源原始实现已开源。
