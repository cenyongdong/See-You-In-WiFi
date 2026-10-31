# 项目最终进度

**2026-10-31 骨架PL专项有限验证完成：** PS保留投影，PL完成骨架／关节点／动态信息绘制与合成；完整物理资格、位流和BOOT已完成并上板。420帧输入完成417次新推理及HDMI采纳，3次窗口替换；用户确认实屏正常，SDK已安全关闭、设备占用为空。当前安装新overlay BOOT，再次演示须正常重启；原BOOT和r3保留作回退。原始日志、软件对照、资源时序、性能图和恢复步骤集中见[专项记录](FPGA/hdmi_candidate/skeleton_overlay/README.md)。不将有限测试写成长期或新实时CSI验收。

更新：2026-10-29，依据已有实测与收尾记录整理；本次文档整理未启动设备验证。

**最终演示包已生成并完成文件核验，最近一次相同 r3 板端内容的运行完成 420 帧新推理、420 次 HDMI 采纳和 420 帧 PC 发送，正常退出且设备占用为空。** 最新打包补入 PC 启动与有线连接修正，板端内容未变；这不等于对最终压缩包重新执行了一轮上板测试，也不代表长期或精度验收通过。

## 保留的 r3 交付基线（2026-10-29）

| 项目 | 最终选择与入口 |
|---|---|
| 演示部署包 | [pose180-three-clips-20261029-r3-final.tar.gz](Deliverables/pose180-three-clips-20261029-r3-final.tar.gz)，[部署步骤](Deliverables/pose180-three-clips-20261029-r3-DEPLOY.md)，[交付目录](Deliverables/README.txt) |
| 核心源码 | [模块目录](software/pose180_pipeline/src/README.md)，[源码快照](Deliverables/pose180-core-sources-final-20261029.tar.gz) |
| 提交技术文档 | [技术文档排版修订版](Docs/commit_docs/技术文档_v1_排版修订.docx)，22 页，按最新用户稿调整 1.5 编号并核验排版；原 `技术文档.docx` 未覆盖。10月30日补充高隐私性智能家居场景、隐私设计、参数量／板端计时对照及共享关节细化计算原理；图示来源保持明确。整机正面／45° 实物照片及最终演示视频仍无完成记录 |
| 模型与显示配置 | 原始 epoch99；TopK=3 后严格 `score > 0.2`；CPU 多人跟踪／One Euro `0.5／0.3／1`；HDMI 和 PC 共用展示结果 |
| 输入接口 | `official_dataset` 板端本地读原始 CSI；`live_csi` 三 RX 实时采集。二者互斥，共用预处理和真实 NPU 推理 |
| 默认展示内容 | 官方训练集 1 人约 10 秒 → 2 人约 9 秒 → 3 人约 9 秒，共 420 帧；来源及限制见[片段清单](software/pose180_pipeline/resident/DATASET-PLAYLIST.md) |
| 硬件基线 | 原r3配套 `probe-free-drain-filter-v1`；当前已安装overlay版本，实际身份见 [default_boot.json](FPGA/hdmi_candidate/default_boot.json)，新版本入口见上方专项记录 |
| 板端与恢复 | 保留 `/root/pose180-three-clips-20261029-r3`；最后核验无原生推理进程、无设备占用。操作与备份见[恢复入口](FPGA/hdmi_candidate/RESUME.md) |

## 完成程度与证据边界

| 范围 | 已完成 | 尚不能宣称 |
|---|---|---|
| 端到端主链 | 实时 CSI／官方输入、PS／NPU、HDMI 与独立 PC 已分别完成有限实板运行；PC 不再是采集或推理必经节点 | 全天无人值守、任意环境下稳定运行 |
| 采集与恢复 | 四路由器开机服务、TX 续期、RX 局部重连、自适应组窗；已有 RX／PC 物理离线恢复记录 | 零缺窗、零卡顿或近似配对输入的姿态精度 |
| HDMI 与硬件 | 合格位流发布、七色条待机、帧采纳／STOP排空；10月31日骨架硬件绘制专项另有完整物理及有限实板证据 | D45根治、运行中PL_KEY1安全恢复；历史几何／滤波扩展仍取消 |
| 软件可读性与健壮性 | 核心按模块归位、Tab 排版、参数／状态处理加固；FD 测试竞态定位修正，8 轮完整生命周期及异常注入通过 | SIGKILL、掉电或真实 SDK 挂死时硬件资源必然安全释放 |
| 演示与 PC | 三片段同一 SDK 生命周期顺播；Node 查找、有线绑定与重连修正，22 项 PC 本地检查通过 | PC 发送计数等同每帧浏览器实际绘制，或择优训练片段等同独立测试精度 |
| 模型质量 | 180-query 原模型部署；自采微调及从零训练候选完成有限比较后恢复原 epoch99 | 自采训练明显改善、D48 数值验收通过、重影／跨 ID 突跳消除 |
| 文件收尾 | 历史上传、旧 SDK 安装包、冗余日志／自采数据清理完成；模型、官方演示输入与关键故障／FPGA 证据保留 | 已删除原始采集可直接重新训练，或所有旧远端清理回执已补齐 |

## 项目演进

| 阶段 | 主要进展与转折 | 追溯入口 |
|---|---|---|
| 9 月底～10 月初 | 核对 Lite、Procise／JFM、Icraft 与资料；解决启动介质和开发环境问题 | [资料记录](REFERENCES.md)、[困难记录](DIFFICULTIES.md) |
| 10 月 4～13 日 | 对齐 CSI 数学、补齐 ARM Host 算子／融合契约；跑通早期混合推理与 VPU／RTSP；旧 DATA 异常取证后暂停全面根因调查 | [历史成果](Done.md)、[ADR 索引](ADR/README.md) |
| 10 月 14～24 日 | HDMI 接入与时序收敛；多轮启动异常隔离、波形与协议取证；采用保留单次主动消费的缓解路径；180-query 原 epoch99 成为主图 | [HDMI 工程](FPGA/hdmi_candidate/INTEGRATION.md)、[模型部署](tools/pose180/deploy/RESULTS.md) |
| 10 月 25～27 日 | 按 ADR_50 改为有界常驻、PC／记录解耦；打通真实 CSI、局部恢复和独立显示；完成六片段双输出，发布默认 BOOT 与七色条 | [常驻记录](software/pose180_pipeline/resident/README.md)、[数据集阶段](software/pose180_pipeline/resident/DATASET-DEMO.md) |
| 10 月 28 日 | 加固单人显示及资源生命周期；比较自采模型后恢复原 epoch99；长测启动有证据，但没有长期验收结论 | [模型对比](software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md)、[启动与安全历史](software/pose180_pipeline/resident/STARTUP-PACKAGE.md) |
| 10 月 29 日 | 核心目录整理、最终审查、FD 竞态修正、双输入与三片段部署、PC 连接修正；完成板端及本地清理 | [最终审查](software/pose180_pipeline/resident/FINAL-REVIEW.md)、[收尾原始记录](.local/project-cleanup-20261029-r1/summary.json) |

按用户收尾要求，所有 difficulty 的项目跟踪状态统一为“已解决（工程收口）”，逐项处置和仍存在的技术限制见 [DIFFICULTIES.md](DIFFICULTIES.md)。该状态不改变历史失败或未验收结论。后续可选验证和冻结项统一见[后续验证与冻结范围](DIFFICULTIES.md#后续验证与冻结范围)，文档的现行／历史属性及撤下页面的去向见[文档目录](DOCUMENTATION.md)。
