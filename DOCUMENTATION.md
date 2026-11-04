# 项目文档导航

更新日期：2026-11-04。本文汇总项目说明、架构决策、模块接口、部署入口与历史验证记录；现行入口和历史资料按下方分类阅读。

当前实现和验收先读[项目进度](PROJECT-PROGRESS.md)，启动／最后设备观察先读[恢复入口](FPGA/hdmi_candidate/RESUME.md)。当前分工为PL CSI幅相／90点组流水及骨架合成、PS相位收尾／人物后处理／投影、NPU推理和PC滤波前后独立观察。当前 Release 提供 r4 部署包和 r7 源码包。

## 当前阅读入口

| 目的 | 维护位置 |
|---|---|
| 项目现状、未验收和冻结边界 | [PROJECT-PROGRESS](PROJECT-PROGRESS.md)、[DIFFICULTIES](DIFFICULTIES.md#后续验证与冻结范围)、[Agents](AGENTS.md) |
| 架构、硬件分工、模块与接口 | [TechDetails](ADR/TechDetails.md)、[ADR索引](ADR/README.md)、[核心目录](software/pose180_pipeline/src/README.md) |
| 部署、BOOT、最后观察与安全恢复 | [r4部署说明](Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)、[RESUME](FPGA/hdmi_candidate/RESUME.md) |
| FPGA RTL／C++ 代码书写与重构规范 | [FPGA 编码规范](FPGA/CODING-STANDARDS.md)、[重构与验证记录](FPGA/REFACTOR-20261104.md) |
| CSI幅相与PL骨架自研内容 | [CSI专项](FPGA/csi_preprocess/README.md)、[骨架专项](FPGA/hdmi_candidate/skeleton_overlay/README.md) |
| PC滤波前后及共享计时 | [PC说明](software/pose180_pipeline/host/README.md) |
| 数据来源、30分钟实测及关键性能 | [长测](FPGA/csi_preprocess/LONGRUN.md)、[性能汇总](Deliverables/PERFORMANCE.md) |
| 源码RAR、厂商依赖及完整硬件复现 | [r7 源码说明](Deliverables/SOURCE-20261104.md)、[r4 历史重建](Deliverables/FPGA-REBUILD-20261101-r1.md) |
| 模型与第三方许可 | [模型索引](model/README.md)、[第三方声明](THIRD_PARTY_NOTICES.md)、[安全维护](SECURITY.md) |
| 当前参赛技术报告 | [技术文档v13（PDF）](Docs/commit_docs/技术文档_v13.pdf) |
| 当前项目海报 | [架构对齐版（A1 PDF）](Docs/commit_docs/项目海报_架构对齐版.pdf) |
| AI辅助开发流程、人工审核与贡献边界 | [AI辅助开发说明](Docs/llm_usage.md) |

## Git 克隆后的文件可用范围

- 普通 Git 克隆提供已提交的源码、部署模型、精选证据及参赛材料。两份正式 RAR 通过 [GitHub Release](https://github.com/cenyongdong/See-You-In-WiFi/releases/tag/deploy-r4-20261031) 下载。[r4 部署包](https://github.com/cenyongdong/See-You-In-WiFi/releases/download/deploy-r4-20261031/pose180-csi-release-20261031-r4.rar) · [下载 r7 源码 RAR](https://github.com/cenyongdong/See-You-In-WiFi/releases/download/deploy-r4-20261031/pose180-current-sources-20261104-r7.rar)
- `.local/`恢复记录、原始训练checkpoint、未公开的历史附件及其它本机资料不随Git克隆提供；SDK／EDA安装、许可和匹配的器件环境外置。不能根据说明中的本机路径推断文件已公开。
- 下载后使用各自的 SHA256 校验文件。[部署包 SHA256](https://github.com/cenyongdong/See-You-In-WiFi/releases/download/deploy-r4-20261031/pose180-csi-release-20261031-r4.rar.sha256) · [源码包 SHA256](https://github.com/cenyongdong/See-You-In-WiFi/releases/download/deploy-r4-20261031/pose180-current-sources-20261104-r7.rar.sha256)
- r7 的内容和验证边界见[源码说明](Deliverables/SOURCE-20261104.md)。r4 预编译部署包的验证记录见[部署核验](Deliverables/release-20261031-r4-validation.json)。
- 旧交付包、旧采集及副本已清理；工作源码、原始训练checkpoint和必要证据保留。10月29日清理见记录（本机留存，仓库未附：`.local/project-cleanup-20261029-r1/summary.json`），10月31日交付清理见记录（本机留存，仓库未附：`.local/delivery-cleanup-20261031-r1/summary.json`）。旧r3被r4替代的说明／校验保存在 `.local/delivery-cleanup-20261031-r1/prior-records/r3-superseded-by-r4/`。

## 引用与归档

- 原始报告和冻结快照保留原文，其中可能包含已清理附件、旧相对目录和本机SDK的原始引用。这些历史附件缺口不作为现行下载／部署入口，也不因链接缺失而改写原测试结果。当前可公开复核的数据以[性能与证据汇总](Deliverables/PERFORMANCE.md)及其链接为入口。
- 普通说明中的“本机留存，仓库未附”表示本机文件未发布；“历史附件，当前仓库未附”表示当前未提供可供网页读取的对应附件。两类条目保留原路径供追溯，不提供无效网页跳转。
- 当前参赛技术报告为[技术文档v13（PDF）](Docs/commit_docs/技术文档_v13.pdf)。
- 历史稿包括已发布的[v1排版修订Word](Docs/commit_docs/技术文档_v1_排版修订.docx)和[v1 Word](Docs/commit_docs/技术文档_v1.docx)。原始模板`Docs/commit_docs/技术文档.docx`和旧版PDF`Docs/commit_docs/技术文档_v1.pdf`本机留存，仓库未附。[原版海报](Docs/commit_docs/项目海报.pdf)记录较早的系统分工。

## 链接检查

仓库提供[只读链接检查脚本](tools/docs/check_links.py)，使用Python 3.9及以上版本和Git，无需设备、SDK或网络访问。

```sh
python tools/docs/check_links.py --worktree
python tools/docs/check_links.py --ref HEAD --output-dir .local/doc-link-check
```

工作区模式只使用已跟踪文件；拟发布的新文件须用可重复的`--include-new 仓库相对路径`显式加入，且不能仍被Git忽略。指定`--ref`时读取该提交的实际文件树和正文，不使用本机未提交内容。Git未在PATH时可用`--git`指定程序。普通文档错误使检查返回非零；受保护历史记录的附件缺口单独报告，新增文档不会因位于历史目录而自动豁免。外部网站不作在线存活检查。

## 撤下页面的阅读位置

| 原页面 | 现行位置 |
|---|---|
| `ToDoLists.md` | [恢复入口](FPGA/hdmi_candidate/RESUME.md)和[后续验证范围](DIFFICULTIES.md#后续验证与冻结范围)；原文可按已有Git历史追溯 |
| `ARCHITECTURE-DISCUSSION-20261015.md` | [现行架构](ADR/TechDetails.md)与[ADR_49](ADR/ADR_49.md)；原阶段讨论保留历史属性 |
| `PROJECT-PROGRESS-before-hdmi-20261017.md` | [项目进度](PROJECT-PROGRESS.md)；旧估算不作为当前完成程度 |

## 分类目录

| 分类 | Markdown数 |
|---|---:|
| 本机历史记录与冻结快照 | 61 |
| 架构说明与决策历史 | 66 |
| 项目总览与维护规则 | 12 |
| 交付与复现说明 | 4 |
| 共享核心与旧工程 | 18 |
| 参考资料与提交材料索引 | 2 |
| FPGA模块与实现历史 | 66 |
| 模型来源与候选历史 | 7 |
| 当前主工程与分阶段记录 | 28 |
| 训练采集及部署工具 | 36 |
| 原始结果与取证报告 | 69 |
| 早期pose-v1开发历史 | 164 |

以下目录同时列出已发布Markdown和明确标记的本机资料，分类数量按实际列项统计。“历史”指正文按所属时间理解，不表示缺陷已修复或任务获得新授权。冻结报告中的附件按原记录范围阅读。

<details>
<summary>本机历史记录与冻结快照（61份，不随仓库分发）</summary>

以下文件本机留存，不随仓库分发；纯文本路径仅用于本机追溯，不提供GitHub网页跳转。

| 文档 | 用途与范围 |
|---|---|
| `.local/ai-hdmi-drain-joint-20261024-r39/source/diagnostics/README.md` | 历史决策／记录／模块参考；README |
| `.local/ai-hdmi-joint-20261023-r35/source/diagnostics/README.md` | 历史决策／记录／模块参考；README |
| `.local/ai-hdmi-joint-20261023-r36/repro-source/diagnostics/README.md` | 历史决策／记录／模块参考；README |
| `.local/engine-timing-test-fixtures/synthetic-2d7301ac0d82414eb642d72e9cb3d517/analysis/report.md` | 历史决策／记录／模块参考；Engine计时分析 |
| `.local/engine-timing-test-fixtures/synthetic-bcb42a333fb749a39320906dd0bf74d7/analysis/report.md` | 历史决策／记录／模块参考；Engine计时分析 |
| `.local/hdmi-ack-transport-20261024-r50/README.md` | 历史决策／记录／模块参考；Synthetic ACK transport comparison |
| `.local/hdmi-complete-verify-r2/README.md` | 历史决策／记录／模块参考；HDMI 完整源码工程（r26 读帧连接基线） |
| `.local/hdmi-complete-verify/README.md` | 历史决策／记录／模块参考；HDMI 完整源码工程（r26 读帧连接基线） |
| `.local/hdmi-live-20261017-r3/execute_read_v3.README.md` | 历史决策／记录／模块参考；read-v3显式逐步执行入口 |
| `.local/hdmi-live-20261017-r3/prepare_remote_read_v3.README.md` | 历史决策／记录／模块参考；read-v3逐阶段源码生成器 |
| `.local/hdmi-main-docs-20261024/Done.md` | 历史决策／记录／模块参考；已完成工作记录 |
| `.local/hdmi-main-docs-20261024/PROJECT-PROGRESS.md` | 历史决策／记录／模块参考；项目进度总览 |
| `.local/hdmi-pipeline-20261024-r53/display/README.md` | 历史决策／记录／模块参考；r53 single-owner begin/poll HDMI output |
| `.local/hdmi-render-speed-20261024-r47/native-render/README.md` | 历史决策／记录／模块参考；Native RGB565 HDMI renderer |
| `.local/hdmi-render-speed-20261024-r47/renderer/CHANGES.md` | 历史决策／记录／模块参考；r47 static background cache |
| `.local/hdmi-s01-isolation-20261022-r28/HDMI-PS-HP2-OFFICIAL-QUESTIONS-20261022.md` | 历史决策／记录／模块参考；FMQL30TAI HDMI启动异常技术问题报告 |
| `.local/hdmi-s01-soak-20261022-r29/HDMI-PS-HP2-OFFICIAL-QUESTIONS-20261022.md` | 历史决策／记录／模块参考；FMQL30TAI HDMI启动异常技术问题报告 |
| `.local/hp2-deferred-consume-20261024-r45/deploy/INTERFACE.md` | 历史决策／记录／模块参考；r45 board controller interface |
| `.local/hp2-deferred-consume-20261024-r45/gates/INPUT-CONTRACT.md` | 历史决策／记录／模块参考；r45 deferred consumption: collector and pure gate |
| `.local/hp2-deferred-consume-20261024-r45/source/diagnostics/README.md` | 历史决策／记录／模块参考；README |
| `.local/hp2-mmio32-20261024-r46/README.md` | 历史决策／记录／模块参考；r46 offline MMIO32 correction |
| `.local/kinect-calibrated-20261028-r1/COMPARISON.md` | 历史决策／记录／模块参考；现场 Kinect／CSI 两组限时训练结果 |
| `.local/kinect-csi-direct-20261028-r5/COLLECTION.md` | 历史决策／记录／模块参考；Kinect／CSI 长时动作原始数据 |
| `.local/kinect-csi-direct-20261028-r6/COLLECTION.md` | 历史决策／记录／模块参考；含坐姿的新增长时采集 |
| `.local/kinect-pairing-20261028-r1/PAIRING.md` | 历史决策／记录／模块参考；CSI—Kinect 接收时刻配对 |
| `.local/nexmon-rtac86u-20261017-r1/nexmon_csi/README.md` | 历史决策／记录／模块参考；Nexmon Channel State Information Extractor |
| `.local/nexmon-rtac86u-20261017-r1/nexmon_csi/utils/makecsiparams/README.md` | 历史决策／记录／模块参考；README |
| `.local/nexmon-tx-router-20261022-r1/derivative-source-r2/README.md` | 历史决策／记录／模块参考；Nexmon Scheduled Transmission |
| `.local/nexmon-tx-router-20261022-r1/derivative-source/README.md` | 历史决策／记录／模块参考；Nexmon Scheduled Transmission |
| `.local/nexmon-tx-router-20261022-r1/source-archive/nexmon_tx_task-main/README.md` | 历史决策／记录／模块参考；Nexmon Scheduled Transmission |
| `.local/pose-v1-build/demo-core-check-20261014-r1/demo/README.md` | 历史决策／记录／模块参考；Wi-Fi 人体三维姿态端到端演示 |
| `.local/pose-v1-build/demo-refactor-20261013-r1/demo/README.md` | 历史决策／记录／模块参考；Wi-Fi 人体三维姿态端到端演示 |
| `.local/pose180-final-core-20261029-r1/source-unpacked/software/core/README.md` | 历史决策／记录／模块参考；正式运行核心 |
| `.local/pose180-final-core-20261029-r1/source-unpacked/software/pose180_pipeline/resident/DEMO-INPUTS.md` | 历史决策／记录／模块参考；双输入演示与源码阅读入口 |
| `.local/pose180-final-core-20261029-r1/source-unpacked/software/pose180_pipeline/resident/FINAL-REVIEW.md` | 历史决策／记录／模块参考；核心源码最终审查与双输入归档 |
| `.local/pose180-final-core-20261029-r1/source-unpacked/software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md` | 历史决策／记录／模块参考；两模型 TopK=1 安全核心测试 |
| `.local/pose180-final-core-20261029-r1/source-unpacked/software/pose180_pipeline/resident/STARTUP-PACKAGE.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-final-core-20261029-r1/source-unpacked/SOURCE-README.md` | 历史决策／记录／模块参考；核心源码归档 |
| `.local/pose180-hdmi-20261025-r2/README.md` | 历史决策／记录／模块参考；pose180 HDMI 新包：已关闭 |
| `.local/pose180-kinect-board-test-20261028-r1/README.md` | 历史决策／记录／模块参考；自采模型有限测试（已结束）及原始模型恢复 |
| `.local/pose180-original-longrun-20261028-r1/README.md` | 历史决策／记录／模块参考；原始epoch99长时测试：持续运行 |
| `.local/pose180-resident-continuous-20261025-r6/firmware-test/derivative/README.md` | 历史决策／记录／模块参考；Nexmon Scheduled Transmission |
| `.local/pose180-resident-continuous-20261025-r6/firmware-test/final-down-status/derivative/README.md` | 历史决策／记录／模块参考；Nexmon Scheduled Transmission |
| `.local/pose180-resident-continuous-20261025-r6/firmware-test/final/derivative/README.md` | 历史决策／记录／模块参考；Nexmon Scheduled Transmission |
| `.local/pose180-resident-continuous-20261025-r6/firmware/derivative-source/README.md` | 历史决策／记录／模块参考；Nexmon Scheduled Transmission |
| `.local/pose180-top1-no-threshold-20261028-r1/source-unpacked/software/pose180_pipeline/resident/STARTUP-PACKAGE.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r1/unpacked/pose180-top1-no-threshold-20261028-r1/README.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r2/source-unpacked/software/core/README.md` | 历史决策／记录／模块参考；正式运行核心 |
| `.local/pose180-top1-no-threshold-20261028-r2/source-unpacked/software/pose180_pipeline/resident/STARTUP-PACKAGE.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r2/unpacked/pose180-top1-no-threshold-20261028-r2/README.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r3/release-before-pre-hardware-check/README.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r3/source-unpacked/software/core/README.md` | 历史决策／记录／模块参考；正式运行核心 |
| `.local/pose180-top1-no-threshold-20261028-r3/source-unpacked/software/pose180_pipeline/resident/STARTUP-PACKAGE.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r3/unpacked/pose180-top1-no-threshold-20261028-r3/README.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r4/source-unpacked/software/core/README.md` | 历史决策／记录／模块参考；正式运行核心 |
| `.local/pose180-top1-no-threshold-20261028-r4/source-unpacked/software/pose180_pipeline/resident/STARTUP-PACKAGE.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/pose180-top1-no-threshold-20261028-r4/unpacked/pose180-top1-no-threshold-20261028-r4/README.md` | 历史决策／记录／模块参考；TopK=1、无置信度阈值启动包 |
| `.local/r30-relocated/README.md` | 历史决策／记录／模块参考；r30 实际源码工程（供官方检查，2026-10-26） |
| `.local/r30-relocated/waveforms/HDMI_HP2_REAL_r30/README.md` | 历史决策／记录／模块参考；HDMI／HP2 实板连续波形（2026-10-22，r30） |
| `.local/router-autostart-20261025-r1/HANDOFF.md` | 历史决策／记录／模块参考；READY — router autostart verified |
| `.local/technical-document-20261029-r1/artifact.md` | 历史决策／记录／模块参考；技术文档填充约定 |

</details>

<details>
<summary>架构说明与决策历史（66份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [ADR/ADR_00.md](ADR/ADR_00.md) | 历史决策／记录／模块参考；ADR_00：首版采用 PS 主导的 CSI 回放、混合推理与双路显示架构 |
| [ADR/ADR_01.md](ADR/ADR_01.md) | 历史决策／记录／模块参考；ADR_01：以已验证PS/NPU异构方案完成首版闭环，深度性能优化后置 |
| [ADR/ADR_02.md](ADR/ADR_02.md) | 历史决策／记录／模块参考；ADR_02：VPU连续内存分配与同进程常驻编码策略 |
| [ADR/ADR_03.md](ADR/ADR_03.md) | 历史决策／记录／模块参考；ADR_03：平台、启动介质与可追溯构建 |
| [ADR/ADR_04.md](ADR/ADR_04.md) | 历史决策／记录／模块参考；ADR_04：固定部署基线、独立参考与训练旁支隔离 |
| [ADR/ADR_05.md](ADR/ADR_05.md) | 历史决策／记录／模块参考；ADR_05：受限CPU适配、融合追溯与每帧完成协议 |
| [ADR/ADR_06.md](ADR/ADR_06.md) | 历史决策／记录／模块参考；ADR_06：可解释性能测量与隔离应用接口 |
| [ADR/ADR_07.md](ADR/ADR_07.md) | 历史决策／记录／模块参考；ADR_07：视频格式、驱动描述与传输时序的分阶段验证 |
| [ADR/ADR_08.md](ADR/ADR_08.md) | 历史决策／记录／模块参考；ADR_08：高内聚模块与在线编码AU桥 |
| [ADR/ADR_09.md](ADR/ADR_09.md) | 历史决策／记录／模块参考；ADR_09：在线门检的启动协同与完整来源覆盖 |
| [ADR/ADR_10.md](ADR/ADR_10.md) | 历史决策／记录／模块参考；ADR_10：慢客户端发送错误与有界TCP候选 |
| [ADR/ADR_11.md](ADR/ADR_11.md) | 历史决策／记录／模块参考；ADR_11：完整CSI网络输入与受保护视频输出的模块接入 |
| [ADR/ADR_12.md](ADR/ADR_12.md) | 历史决策／记录／模块参考；ADR_12：TCP与视频并行下输出回归失配的有界取证 |
| [ADR/ADR_13.md](ADR/ADR_13.md) | 历史决策／记录／模块参考；ADR_13：保存优先门检与单次规整恢复验证 |
| [ADR/ADR_14.md](ADR/ADR_14.md) | 历史决策／记录／模块参考；ADR_14：整机单时钟计量与传输、样本身份分离 |
| [ADR/ADR_15.md](ADR/ADR_15.md) | 历史决策／记录／模块参考；ADR_15：独立显示子进程与有界拥有值IPC |
| [ADR/ADR_16.md](ADR/ADR_16.md) | 历史决策／记录／模块参考；ADR 16：前向尖峰定位与有界计量扩展 |
| [ADR/ADR_17.md](ADR/ADR_17.md) | 历史决策／记录／模块参考；ADR 17：异构与视频并行时的周期性数据块异常 |
| [ADR/ADR_18.md](ADR/ADR_18.md) | 历史决策／记录／模块参考；ADR_18：103次有界计量与独立画面参考 |
| [ADR/ADR_19.md](ADR/ADR_19.md) | 历史决策／记录／模块参考；ADR_19：Host复制快照、元数据校验与生产组完成检查 |
| [ADR/ADR_20.md](ADR/ADR_20.md) | 历史决策／记录／模块参考；ADR_20：有限姿态输出失配与独立取证落盘 |
| [ADR/ADR_21.md](ADR/ADR_21.md) | 历史决策／记录／模块参考；ADR_21：192生产完成观测与连续SDK搬运残留判别 |
| [ADR/ADR_22.md](ADR/ADR_22.md) | 历史决策／记录／模块参考；ADR_22：SDK 拥有双源搬运隔离与编码并发判别 |
| [ADR/ADR_23.md](ADR/ADR_23.md) | 历史决策／记录／模块参考；ADR_23：真实模型复制对象、类型和拥有字节对齐取证 |
| [ADR/ADR_24.md](ADR/ADR_24.md) | 历史决策／记录／模块参考；ADR_24：真实类型与动态写入的独立 SDK 搬运对照 |
| [ADR/ADR_25.md](ADR/ADR_25.md) | 历史决策／记录／模块参考；ADR_25：公开 PL DDR 分配容量与较高来源位置对照 |
| [ADR/ADR_26.md](ADR/ADR_26.md) | 历史决策／记录／模块参考；ADR_26：真实混合模型移除视频负载的独立对照 |
| [ADR/ADR_27.md](ADR/ADR_27.md) | 历史决策／记录／模块参考；ADR_27：同一程序的模型／合成编码负载对照 |
| [ADR/ADR_28.md](ADR/ADR_28.md) | 历史决策／记录／模块参考；ADR_28：单次编码上下文跨三窗／103生命周期 |
| [ADR/ADR_29.md](ADR/ADR_29.md) | 历史决策／记录／模块参考；ADR_29：单次常驻上下文接入真实拥有骨架画面 |
| [ADR/ADR_30.md](ADR/ADR_30.md) | 历史决策／记录／模块参考；ADR_30：公开 Tensor::read 直写自有 Host 输入暂存 |
| [ADR/ADR_31.md](ADR/ADR_31.md) | 历史决策／记录／模块参考；ADR_31：公开read输入桥回接显示子进程、TCP与owned AU |
| [ADR/ADR_32.md](ADR/ADR_32.md) | 历史决策／记录／模块参考；ADR_32：发送端时钟精度与有界吞吐余量验证 |
| [ADR/ADR_33.md](ADR/ADR_33.md) | 历史决策／记录／模块参考；ADR_33：公开read路径的有限姿态失配与最终门检取证缺口 |
| [ADR/ADR_34.md](ADR/ADR_34.md) | 历史决策／记录／模块参考；ADR_34：原Gather与ZG上游公开边界观察 |
| [ADR/ADR_35.md](ADR/ADR_35.md) | 历史决策／记录／模块参考；ADR_35：192首次复制返回与CPU使用前Host字节边界 |
| [ADR/ADR_36.md](ADR/ADR_36.md) | 历史决策／记录／模块参考；ADR_36：匹配 AXI 读路径责任边界与独立双模式对照 |
| [ADR/ADR_37.md](ADR/ADR_37.md) | 历史决策／记录／模块参考；ADR_37：真实 NPU 生产者完成契约与最小视图可执行性 |
| [ADR/ADR_38.md](ADR/ADR_38.md) | 历史决策／记录／模块参考；ADR_38：真实融合组参数、受限独立参考与模拟部署 |
| [ADR/ADR_39.md](ADR/ADR_39.md) | 历史决策／记录／模块参考；ADR_39：独立19成员物理生产者的部署门与固定四调用 |
| [ADR/ADR_40.md](ADR/ADR_40.md) | 历史决策／记录／模块参考；ADR_40：同身份独立生产者与VPU对照、公开ioctl观察 |
| [ADR/ADR_41.md](ADR/ADR_41.md) | 历史决策／记录／模块参考；ADR_41：reset前分段观察与准备后绝对时隙门检 |
| [ADR/ADR_42.md](ADR/ADR_42.md) | 历史决策／记录／模块参考；ADR_42：独立NPU生产者的SDK自有高地址布局 |
| [ADR/ADR_43.md](ADR/ADR_43.md) | 历史决策／记录／模块参考；ADR_43：单调用公开输出租约与失败后两轮源读证据 |
| [ADR/ADR_44.md](ADR/ADR_44.md) | 历史决策／记录／模块参考；ADR_44：调用目录预建与一次性拥有令牌 |
| [ADR/ADR_45.md](ADR/ADR_45.md) | 历史决策／记录／模块参考；ADR_45：暂停坏块定位，整合端到端演示 |
| [ADR/ADR_46.md](ADR/ADR_46.md) | 历史决策／记录／模块参考；ADR_46：执行规范、进度、难点与历史过程分开维护 |
| [ADR/ADR_47.md](ADR/ADR_47.md) | 历史决策／记录／模块参考；ADR_47：正式核心目录与保持行为的可读性重构 |
| [ADR/ADR_48.md](ADR/ADR_48.md) | 历史决策／记录／模块参考；ADR_48：共享细化 FP16 候选的有界数值门检 |
| [ADR/ADR_49.md](ADR/ADR_49.md) | 历史决策／记录／模块参考；ADR_49：PS／NPU感知、PL HDMI与PC独立3D展示 |
| [ADR/ADR_50.md](ADR/ADR_50.md) | 历史决策／记录／模块参考；ADR_50：端到端演示优先、有界缓存与分级自动恢复 |
| [ADR/ADR_ToBeDiscussed.md](ADR/ADR_ToBeDiscussed.md) | 历史决策／记录／模块参考；杀手锏 1：【FPGA 硬件 CSI 预处理加速 IP】（消灭 5.66ms CPU 耗时） |
| [ADR/history/20261013/adr-index-before.md](ADR/history/20261013/adr-index-before.md) | 历史决策／记录／模块参考；整理前历史文档快照 |
| [ADR/history/20261013/cpu-sdk.md](ADR/history/20261013/cpu-sdk.md) | 历史决策／记录／模块参考；CPU适配、SDK审计与初期部署的实施历史 |
| [ADR/history/20261013/demo.md](ADR/history/20261013/demo.md) | 历史决策／记录／模块参考；端到端演示的实施与验收历史 |
| [ADR/history/20261013/difficulties-before.md](ADR/history/20261013/difficulties-before.md) | 历史决策／记录／模块参考；整理前历史文档快照 |
| [ADR/history/20261013/mixed-inference.md](ADR/history/20261013/mixed-inference.md) | 历史决策／记录／模块参考；正式混合推理接入与帧状态的实施历史 |
| [ADR/history/20261013/platform-tools.md](ADR/history/20261013/platform-tools.md) | 历史决策／记录／模块参考；平台、启动介质与本机工具的历史 |
| [ADR/history/20261013/progress-before.md](ADR/history/20261013/progress-before.md) | 历史决策／记录／模块参考；整理前历史文档快照 |
| [ADR/history/20261013/read-diagnostics.md](ADR/history/20261013/read-diagnostics.md) | 历史决策／记录／模块参考；NPU生产者与首次读取异常的取证历史 |
| [ADR/history/20261013/README.md](ADR/history/20261013/README.md) | 历史决策／记录／模块参考；2026-10-13 文档迁存索引 |
| [ADR/history/20261013/toolchain-runbook.md](ADR/history/20261013/toolchain-runbook.md) | 历史决策／记录／模块参考；本机工具路径与调用方法（历史资料） |
| [ADR/history/20261013/training.md](ADR/history/20261013/training.md) | 历史决策／记录／模块参考；训练旁支与检查任务的历史 |
| [ADR/history/20261013/video-lifecycle.md](ADR/history/20261013/video-lifecycle.md) | 历史决策／记录／模块参考；视频、常驻生命周期与计量的实施历史 |
| [ADR/README.md](ADR/README.md) | 现行入口／含历史章节；架构决策与难点归档 |
| [ADR/TechDetails.md](ADR/TechDetails.md) | 现行入口／含历史章节；Wi-Fi CSI 多人三维姿态系统架构与接口 |

</details>

<details>
<summary>项目总览与维护规则（12份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [AGENTS.md](AGENTS.md) | 历史决策／记录／模块参考；项目执行规范 |
| `ARCHITECTURE-DISCUSSION-20261015.md`（本机留存，仓库未附） | 历史决策／记录／模块参考；架构讨论记录与 HDMI 后续实施范围 |
| [DIFFICULTIES.md](DIFFICULTIES.md) | 现行入口／含历史章节；项目困难与最终处置 |
| [DOCUMENTATION.md](DOCUMENTATION.md) | 现行入口／含历史章节；项目文档导航 |
| [Done.md](Done.md) | 现行入口／含历史章节；已完成工作记录 |
| `PROJECT-PROGRESS-before-hdmi-20261017.md`（本机留存，仓库未附） | 历史决策／记录／模块参考；项目进度总览 |
| [PROJECT-PROGRESS.md](PROJECT-PROGRESS.md) | 现行入口／含历史章节；项目最新进度 |
| [README.md](README.md) | 现行入口／含历史章节；基于 Wi-Fi CSI 的嵌入式多人三维姿态感知系统 |
| [REFERENCES.md](REFERENCES.md) | 现行入口／含历史章节；比赛开发资料索引与理解记录 |
| [SECURITY.md](SECURITY.md) | 现行入口／含历史章节；凭据与安全维护 |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | 现行入口／含历史章节；开源许可与第三方内容 |
| [Logs/README.md](Logs/README.md) | 日志目录说明；日志本体本机留存 |

</details>

<details>
<summary>交付与复现说明（4份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [Deliverables/FPGA-REBUILD-20261101-r1.md](Deliverables/FPGA-REBUILD-20261101-r1.md) | 现行入口／含历史章节；r4源码RAR独立完整FPGA重建实测（2026-11-01） |
| [Deliverables/PERFORMANCE.md](Deliverables/PERFORMANCE.md) | 现行入口／含历史章节；当前实测性能、资源与证据（2026-11-01） |
| [Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md](Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md) | 现行入口／含历史章节；CSI 分组流水与骨架绘图：当前发布包 |
| [Deliverables/SOURCE-20261031.md](Deliverables/SOURCE-20261031.md) | 历史；r4 源码与 FPGA 依赖说明 |

</details>

<details>
<summary>共享核心与旧工程（18份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [demo_v1/diagnostics/README.md](demo_v1/diagnostics/README.md) | 历史决策／记录／模块参考；README |
| [demo_v1/README.md](demo_v1/README.md) | 历史决策／记录／模块参考；demo_v1：论文CSI → Lite融合推理 → 主机实时3D |
| [demo_v1/RESULTS.md](demo_v1/RESULTS.md) | 历史决策／记录／模块参考；demo_v1 实测与恢复入口 |
| [software/core/INTERFACES.md](software/core/INTERFACES.md) | 历史决策／记录／模块参考；正式核心接口与开发指南 |
| [software/core/pose/README.md](software/core/pose/README.md) | 历史决策／记录／模块参考；姿态后处理源码位置 |
| [software/core/README.md](software/core/README.md) | 历史决策／记录／模块参考；核心源码入口 |
| [software/demo/README.md](software/demo/README.md) | 历史决策／记录／模块参考；Wi-Fi 人体三维姿态端到端演示 |
| [software/engine_timing/README.md](software/engine_timing/README.md) | 历史决策／记录／模块参考；Engine推理计时诊断 |
| [software/hdmi_demo/README.md](software/hdmi_demo/README.md) | 历史决策／记录／模块参考；HDMI独立接入应用 |
| [software/pc_viewer/README.md](software/pc_viewer/README.md) | 历史决策／记录／模块参考；PC 三维姿态观察台 |
| [software/pc_viewer/VALIDATION-20261018.md](software/pc_viewer/VALIDATION-20261018.md) | 历史决策／记录／模块参考；60份真实历史结果的连续动作回放 |
| [software/pose_events/README.md](software/pose_events/README.md) | 历史决策／记录／模块参考；纯PS离线动作事件原型 |
| [software/pose_output/README.md](software/pose_output/README.md) | 历史决策／记录／模块参考；SDK无关骨架网络输出 |
| [software/pose_v1/PROTOCOL.md](software/pose_v1/PROTOCOL.md) | 历史决策／记录／模块参考；原始 CSI 窗口契约 v1 |
| [software/pose_v1/README.md](software/pose_v1/README.md) | 历史决策／记录／模块参考；CSI首版：当前实施状态（2026-10-07） |
| [software/vitals/HYBRID-20261026.md](software/vitals/HYBRID-20261026.md) | 历史决策／记录／模块参考；心率流式模块与可选 PL 后端 |
| [software/vitals/README.md](software/vitals/README.md) | 历史决策／记录／模块参考；独立心率模块 |
| [software/vitals/VALIDATION-20261019.md](software/vitals/VALIDATION-20261019.md) | 历史决策／记录／模块参考；心率PS参考实现离线验证结果 |

</details>

<details>
<summary>参考资料与提交材料索引（2份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [Docs/commit_docs/官方数据集演示片段清单.md](Docs/commit_docs/%E5%AE%98%E6%96%B9%E6%95%B0%E6%8D%AE%E9%9B%86%E6%BC%94%E7%A4%BA%E7%89%87%E6%AE%B5%E6%B8%85%E5%8D%95.md) | 参考原文；官方数据集视频演示片段清单 |
| [Docs/llm_usage.md](Docs/llm_usage.md) | AI辅助开发说明；可复用流程、人机分工与人工审核 |

</details>

<details>
<summary>FPGA模块与实现历史（66份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [FPGA/ARCHITECTURE-SCORING-ANALYSIS-20261019.md](FPGA/ARCHITECTURE-SCORING-ANALYSIS-20261019.md) | 历史决策／记录／模块参考；面向比赛评分的整体架构与PS PL任务划分分析报告 |
| [FPGA/CSI-PREPROCESS-VITALS-PROPOSAL-20261018.md](FPGA/CSI-PREPROCESS-VITALS-PROPOSAL-20261018.md) | 历史决策／记录／模块参考；FPGA输入预处理与心率检测可行性分析及顶层技术方案 |
| [FPGA/csi_preprocess/LONGRUN.md](FPGA/csi_preprocess/LONGRUN.md) | 现行入口／含历史章节；CSI 分组流水与双路显示：30分钟官方输入长测 |
| [FPGA/csi_preprocess/README.md](FPGA/csi_preprocess/README.md) | 现行入口／含历史章节；CSI 幅相预处理硬件下放 |
| [FPGA/FPGA-WORK-SUMMARY-20261016.md](FPGA/FPGA-WORK-SUMMARY-20261016.md) | 历史决策／记录／模块参考；FPGA／HDMI工作总结与架构讨论交接 |
| [FPGA/hdmi_candidate/AI-CLOCK-GATE.md](FPGA/hdmi_candidate/AI-CLOCK-GATE.md) | 历史决策／记录／模块参考；原厂整机实现后的AI时钟门检 |
| [FPGA/hdmi_candidate/AI-HDMI-JOINT-20261023.md](FPGA/hdmi_candidate/AI-HDMI-JOINT-20261023.md) | 历史决策／记录／模块参考；AI → HDMI 联合测试状态（2026-10-23） |
| [FPGA/hdmi_candidate/AI-PATH-DIAGNOSIS-20261017.md](FPGA/hdmi_candidate/AI-PATH-DIAGNOSIS-20261017.md) | 历史决策／记录／模块参考；HDMI候选AI／PL-DDR路径诊断与原配置对照 |
| [FPGA/hdmi_candidate/baselines/ps_release_r26/README.md](FPGA/hdmi_candidate/baselines/ps_release_r26/README.md) | 历史决策／记录／模块参考；隔离前的实际合格构建基线 |
| [FPGA/hdmi_candidate/BOARD-PLAN.md](FPGA/hdmi_candidate/BOARD-PLAN.md) | 历史决策／记录／模块参考；HDMI候选实机阶段执行包 |
| [FPGA/hdmi_candidate/BOARD-RELEASE-20261016.md](FPGA/hdmi_candidate/BOARD-RELEASE-20261016.md) | 历史决策／记录／模块参考；参考位流定点豁免与受控板测发布 |
| [FPGA/hdmi_candidate/CANDIDATE-AI-MONITOR-V2.md](FPGA/hdmi_candidate/CANDIDATE-AI-MONITOR-V2.md) | 历史决策／记录／模块参考；AI被动观测候选v2：受控启动与三窗HDMI执行包 |
| [FPGA/hdmi_candidate/CANDIDATE-AI-READ-V3.md](FPGA/hdmi_candidate/CANDIDATE-AI-READ-V3.md) | 历史决策／记录／模块参考；六边界读路径观测v3：受控启动执行草案 |
| [FPGA/hdmi_candidate/CANDIDATE-BOARD-READ-R9.md](FPGA/hdmi_candidate/CANDIDATE-BOARD-READ-R9.md) | 历史决策／记录／模块参考；r9 AI读路径观测候选：现场有界执行包 |
| [FPGA/hdmi_candidate/CANDIDATE-BOARD-TEST-R5.md](FPGA/hdmi_candidate/CANDIDATE-BOARD-TEST-R5.md) | 历史决策／记录／模块参考；HDMI r5受控启动与静态实屏执行包 |
| [FPGA/hdmi_candidate/diagnostics/ack_transport_r50/README.md](FPGA/hdmi_candidate/diagnostics/ack_transport_r50/README.md) | 历史决策／记录／模块参考；Synthetic ACK transport comparison |
| [FPGA/hdmi_candidate/diagnostics/ai_read_monitor.README.md](FPGA/hdmi_candidate/diagnostics/ai_read_monitor.README.md) | 历史决策／记录／模块参考；六边界被动读路径观测器 |
| [FPGA/hdmi_candidate/diagnostics/deferred_consume_r45/README.md](FPGA/hdmi_candidate/diagnostics/deferred_consume_r45/README.md) | 历史决策／记录／模块参考；r45 同位流、同启动有限消费诊断 |
| [FPGA/hdmi_candidate/diagnostics/HP2-CYCLETRACE.md](FPGA/hdmi_candidate/diagnostics/HP2-CYCLETRACE.md) | 历史决策／记录／模块参考；HP2 双窗口实板采样（r30） |
| [FPGA/hdmi_candidate/diagnostics/mmio32_r46/README.md](FPGA/hdmi_candidate/diagnostics/mmio32_r46/README.md) | 历史决策／记录／模块参考；r46 offline MMIO32 correction |
| [FPGA/hdmi_candidate/diagnostics/native_rgb565_r47/README.md](FPGA/hdmi_candidate/diagnostics/native_rgb565_r47/README.md) | 历史决策／记录／模块参考；Native RGB565 HDMI renderer |
| [FPGA/hdmi_candidate/diagnostics/native_rgb565_r51/README.md](FPGA/hdmi_candidate/diagnostics/native_rgb565_r51/README.md) | 历史决策／记录／模块参考；r51 static-background overlap |
| [FPGA/hdmi_candidate/diagnostics/native_rgb565_r53/display/README.md](FPGA/hdmi_candidate/diagnostics/native_rgb565_r53/display/README.md) | 历史决策／记录／模块参考；r53 single-owner begin/poll HDMI output |
| [FPGA/hdmi_candidate/diagnostics/PROTOCOL-CHECKER-REVIEW-20261023.md](FPGA/hdmi_candidate/diagnostics/PROTOCOL-CHECKER-REVIEW-20261023.md) | 历史决策／记录／模块参考；官方资料与 AXI 协议检查 IP 的适用性 |
| [FPGA/hdmi_candidate/diagnostics/README.md](FPGA/hdmi_candidate/diagnostics/README.md) | 历史决策／记录／模块参考；AI数据通路被动观测 |
| [FPGA/hdmi_candidate/diagnostics/S01-ISOLATION.md](FPGA/hdmi_candidate/diagnostics/S01-ISOLATION.md) | 历史决策／记录／模块参考；S01源端隔离对照 |
| [FPGA/hdmi_candidate/diagnostics/waveforms-20261022/README.md](FPGA/hdmi_candidate/diagnostics/waveforms-20261022/README.md) | 历史决策／记录／模块参考；HDMI / PS HP2 实测波形与原始记录 |
| [FPGA/hdmi_candidate/diagnostics/waveforms-r30-20261022/README.md](FPGA/hdmi_candidate/diagnostics/waveforms-r30-20261022/README.md) | 历史决策／记录／模块参考；HDMI／HP2 实板连续波形（2026-10-22，r30） |
| [FPGA/hdmi_candidate/HDMI-FAULT-HANDOFF.md](FPGA/hdmi_candidate/HDMI-FAULT-HANDOFF.md) | 历史决策／记录／模块参考；HDMI启动故障工程排查交接 |
| [FPGA/hdmi_candidate/HDMI-PS-HP2-OFFICIAL-QUESTIONS-20261022.md](FPGA/hdmi_candidate/HDMI-PS-HP2-OFFICIAL-QUESTIONS-20261022.md) | 历史决策／记录／模块参考；FMQL30TAI HDMI启动异常技术问题报告 |
| [FPGA/hdmi_candidate/INTEGRATION.md](FPGA/hdmi_candidate/INTEGRATION.md) | 现行入口／含历史章节；HDMI结构、接入过程与验证边界 |
| [FPGA/hdmi_candidate/IP-CONTRACT-REVIEW.md](FPGA/hdmi_candidate/IP-CONTRACT-REVIEW.md) | 历史决策／记录／模块参考；升级后衍生字段差异审查与有限继续条件 |
| [FPGA/hdmi_candidate/IP-REVISION-PLAN.md](FPGA/hdmi_candidate/IP-REVISION-PLAN.md) | 历史决策／记录／模块参考；隔离工程IP修订升级的已批准范围与结果 |
| [FPGA/hdmi_candidate/JFM-COMPATIBILITY-REVIEW.md](FPGA/hdmi_candidate/JFM-COMPATIBILITY-REVIEW.md) | 历史决策／记录／模块参考；replace_7z030ai_file的真实作用与当前版本边界 |
| [FPGA/hdmi_candidate/JFM-FLOW-REVIEW.md](FPGA/hdmi_candidate/JFM-FLOW-REVIEW.md) | 历史决策／记录／模块参考；原厂流程审查与当前实现入口 |
| [FPGA/hdmi_candidate/PAUSE-REPORT-20261018.md](FPGA/hdmi_candidate/PAUSE-REPORT-20261018.md) | 历史决策／记录／模块参考；实时推理 → HDMI 阶段进度与暂停报告 |
| [FPGA/hdmi_candidate/PIN-CONTRACT.md](FPGA/hdmi_candidate/PIN-CONTRACT.md) | 历史决策／记录／模块参考；Lite板HDMI、参考时钟及按键引脚核对 |
| [FPGA/hdmi_candidate/pose_stabilizer/README.md](FPGA/hdmi_candidate/pose_stabilizer/README.md) | 历史决策／记录／模块参考；防闪现后处理与精简硬件：离线结果 |
| [FPGA/hdmi_candidate/probe_free/README.md](FPGA/hdmi_candidate/probe_free/README.md) | 历史决策／记录／模块参考；无探针启动位流与可靠性验证 |
| [FPGA/hdmi_candidate/probe_free_drain/README.md](FPGA/hdmi_candidate/probe_free_drain/README.md) | 历史决策／记录／模块参考；去除诊断、保留异常消费的 HDMI 候选 |
| [FPGA/hdmi_candidate/PS-ADAPTATION-STATUS.md](FPGA/hdmi_candidate/PS-ADAPTATION-STATUS.md) | 历史决策／记录／模块参考；30TAI自定义PS原生适配阻塞与恢复入口 |
| [FPGA/hdmi_candidate/R24-RESOURCE-AUDIT.md](FPGA/hdmi_candidate/R24-RESOURCE-AUDIT.md) | 历史决策／记录／模块参考；r24实际布线检查点资源审计 |
| [FPGA/hdmi_candidate/README.md](FPGA/hdmi_candidate/README.md) | 现行入口／含历史章节；HDMI模块资料入口 |
| [FPGA/hdmi_candidate/RESUME.md](FPGA/hdmi_candidate/RESUME.md) | 现行入口／含历史章节；当前设备、部署与恢复入口 |
| [FPGA/hdmi_candidate/ROUTE2-AUDIT.md](FPGA/hdmi_candidate/ROUTE2-AUDIT.md) | 历史决策／记录／模块参考；原厂 Vivado＋JFM／Procise 路径二审查 |
| [FPGA/hdmi_candidate/ROUTE2-BUILD-PLAN.md](FPGA/hdmi_candidate/ROUTE2-BUILD-PLAN.md) | 历史决策／记录／模块参考；路径二实施配置与顺序 |
| [FPGA/hdmi_candidate/scripts/build_ai_read_shared.README.md](FPGA/hdmi_candidate/scripts/build_ai_read_shared.README.md) | 历史决策／记录／模块参考；三窗推理→HDMI只读路径观测构建器 |
| [FPGA/hdmi_candidate/scripts/control_ai_read_startup.README.md](FPGA/hdmi_candidate/scripts/control_ai_read_startup.README.md) | 历史决策／记录／模块参考；read-v3本机启动监督器 |
| [FPGA/hdmi_candidate/scripts/package_ai_read_offline.README.md](FPGA/hdmi_candidate/scripts/package_ai_read_offline.README.md) | 历史决策／记录／模块参考；读路径观测v3离线打包器 |
| [FPGA/hdmi_candidate/scripts/package_ai_read_postroute.README.md](FPGA/hdmi_candidate/scripts/package_ai_read_postroute.README.md) | 历史决策／记录／模块参考；r6离线打包薄适配 |
| [FPGA/hdmi_candidate/scripts/README-ai-read-r7-offline.md](FPGA/hdmi_candidate/scripts/README-ai-read-r7-offline.md) | 历史决策／记录／模块参考；r7 离线 bit／ICAP／BOOT 适配候选 |
| [FPGA/hdmi_candidate/scripts/README-hdmi-reader-idle-r7.md](FPGA/hdmi_candidate/scripts/README-hdmi-reader-idle-r7.md) | 历史决策／记录／模块参考；HDMI reader r7 isolated full flow |
| [FPGA/hdmi_candidate/scripts/review_ai_read_postroute.README.md](FPGA/hdmi_candidate/scripts/review_ai_read_postroute.README.md) | 历史决策／记录／模块参考；r6独立正式报告门 |
| [FPGA/hdmi_candidate/sim/tb_generated_axi3_stream.README.md](FPGA/hdmi_candidate/sim/tb_generated_axi3_stream.README.md) | 历史决策／记录／模块参考；有限AXI3连续读测试台 |
| [FPGA/hdmi_candidate/skeleton_overlay/README.md](FPGA/hdmi_candidate/skeleton_overlay/README.md) | 现行入口／含历史章节；骨架硬件绘制与图层合成 |
| [FPGA/hdmi_candidate/software/AI-READ-MONITOR.md](FPGA/hdmi_candidate/software/AI-READ-MONITOR.md) | 历史决策／记录／模块参考；独立AI读路径观测适配与固定DMA探针 |
| [FPGA/hdmi_candidate/STARTUP-PAUSE-REPORT-20261018.md](FPGA/hdmi_candidate/STARTUP-PAUSE-REPORT-20261018.md) | 历史决策／记录／模块参考；实时推理到HDMI启动稳定性暂停汇报 |
| [FPGA/hdmi_candidate/SYSTEM-INTEGRATION-PLAN.md](FPGA/hdmi_candidate/SYSTEM-INTEGRATION-PLAN.md) | 历史决策／记录／模块参考；HDMI修复接入整机与实板验证 |
| [FPGA/hdmi_candidate/TIME-REPORT-20261018.md](FPGA/hdmi_candidate/TIME-REPORT-20261018.md) | 历史决策／记录／模块参考；上一轮任务耗时复盘 |
| [FPGA/hdmi_candidate/VIVADO-VERSION-PLAN.md](FPGA/hdmi_candidate/VIVADO-VERSION-PLAN.md) | 历史决策／记录／模块参考；2019.1迁移评估与2018.3备用环境方案 |
| [FPGA/hdmi_validation/PROPOSAL.md](FPGA/hdmi_validation/PROPOSAL.md) | 历史决策／记录／模块参考；HDMI 候选修正方案（已批准候选阶段，现暂停） |
| [FPGA/hdmi_validation/README.md](FPGA/hdmi_validation/README.md) | 历史决策／记录／模块参考；HDMI 独立诊断与行为验证 |
| [FPGA/lite_led_chaser/README.md](FPGA/lite_led_chaser/README.md) | 历史决策／记录／模块参考；悟净 Lite 流水灯全流程验证 |
| [FPGA/lite_led_ip_bridge/README.md](FPGA/lite_led_ip_bridge/README.md) | 历史决策／记录／模块参考；悟净 Lite：真实 xlconcat IP 流水灯源码交接 |
| [FPGA/README.md](FPGA/README.md) | 现行入口／含历史章节；FPGA 工程资料入口 |
| [FPGA/vitals_acf/README.md](FPGA/vitals_acf/README.md) | 历史决策／记录／模块参考；心率自相关 PL 核心 |

</details>

<details>
<summary>模型来源与候选历史（7份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [model/piw24_kinect_finetune-e13-20261028-r1/README.md](model/piw24_kinect_finetune-e13-20261028-r1/README.md) | 历史决策／记录／模块参考；现场微调 epoch13：Icraft 上板预览候选 |
| [model/piw24_kinect_scratch-e4-20261028-r1/README.md](model/piw24_kinect_scratch-e4-20261028-r1/README.md) | 历史决策／记录／模块参考；随机初始化训练 epoch4：Icraft 上板对照候选 |
| [model/piw24_noscatter-20261014-r3/README.md](model/piw24_noscatter-20261014-r3/README.md) | 历史决策／记录／模块参考；完整去ScatterND ONNX：Icraft3.39.0主机转换 |
| [model/piw24_pose180_scratch130-20261027-r1/README.md](model/piw24_pose180_scratch130-20261027-r1/README.md) | 历史决策／记录／模块参考；从零初始化训练 epoch130：180-query 转换候选 |
| [model/piw24_pose180_shared-20261024-r1/README.md](model/piw24_pose180_shared-20261024-r1/README.md) | 现行入口／含历史章节；当前 180-query 共享 FP16 模型 |
| [model/piw24_shared-20261015-r1/README.md](model/piw24_shared-20261015-r1/README.md) | 历史决策／记录／模块参考；共享细化 Icraft 产物 |
| [model/README.md](model/README.md) | 现行入口／含历史章节；模型与部署资产 |

</details>

<details>
<summary>当前主工程与分阶段记录（28份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [software/pose180_pipeline/board/README.md](software/pose180_pipeline/board/README.md) | 现行入口／含历史章节；源码已按模块归位 |
| [software/pose180_pipeline/control/autostart/README.md](software/pose180_pipeline/control/autostart/README.md) | 历史决策／记录／模块参考；四路 CSI 路由器开机服务 |
| [software/pose180_pipeline/control/README.md](software/pose180_pipeline/control/README.md) | 现行入口／含历史章节；启停、输入准备与运行管理 |
| [software/pose180_pipeline/evidence/20261025/README.md](software/pose180_pipeline/evidence/20261025/README.md) | 历史决策／记录／模块参考；2026-10-25阶段归档 |
| [software/pose180_pipeline/host/README.md](software/pose180_pipeline/host/README.md) | 现行入口／含历史章节；180-query PC 观察与主机验证 |
| [software/pose180_pipeline/README.md](software/pose180_pipeline/README.md) | 现行入口／含历史章节；180-query 演示工程与核心源码 |
| [software/pose180_pipeline/resident/ADAPTIVE-CSI.md](software/pose180_pipeline/resident/ADAPTIVE-CSI.md) | 历史决策／记录／模块参考；实时 CSI 的容错组窗与后台对齐 |
| [software/pose180_pipeline/resident/autostart/README.md](software/pose180_pipeline/resident/autostart/README.md) | 历史决策／记录／模块参考；路由器服务源码位置 |
| [software/pose180_pipeline/resident/CSI-INTEGRATION-20261027.md](software/pose180_pipeline/resident/CSI-INTEGRATION-20261027.md) | 历史决策／记录／模块参考；自适应 CSI 输入接入与连续性实板验证 |
| [software/pose180_pipeline/resident/DATASET-DEMO.md](software/pose180_pipeline/resident/DATASET-DEMO.md) | 历史决策／记录／模块参考；官方数据集开发验证与视频演示 |
| [software/pose180_pipeline/resident/DATASET-PLAYLIST.md](software/pose180_pipeline/resident/DATASET-PLAYLIST.md) | 现行入口／含历史章节；三片段顺序演示（2026-10-29） |
| [software/pose180_pipeline/resident/DEMO-INPUTS.md](software/pose180_pipeline/resident/DEMO-INPUTS.md) | 现行入口／含历史章节；双输入演示与源码阅读入口 |
| [software/pose180_pipeline/resident/FINAL-REVIEW.md](software/pose180_pipeline/resident/FINAL-REVIEW.md) | 现行入口／含历史章节；核心源码最终审查与双输入整理 |
| [software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md](software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md) | 历史决策／记录／模块参考；两模型 TopK=1 安全核心测试 |
| [software/pose180_pipeline/resident/LONG-VALIDATION.md](software/pose180_pipeline/resident/LONG-VALIDATION.md) | 历史决策／记录／模块参考；r4：自主源端与30分钟联合验证结果 |
| [software/pose180_pipeline/resident/PHASE-CONTINUITY.md](software/pose180_pipeline/resident/PHASE-CONTINUITY.md) | 历史决策／记录／模块参考；时间分支连续性修正与离线推理对照 |
| [software/pose180_pipeline/resident/PHASE-PREPROCESS-AUDIT.md](software/pose180_pipeline/resident/PHASE-PREPROCESS-AUDIT.md) | 历史决策／记录／模块参考；姿态预处理的相位跳变诊断 |
| [software/pose180_pipeline/resident/PHASE-TRACKING.md](software/pose180_pipeline/resident/PHASE-TRACKING.md) | 历史决策／记录／模块参考；r8／r9：时间网格跟踪、启动见证与实板复验 |
| [software/pose180_pipeline/resident/PRESENTATION-20261026.md](software/pose180_pipeline/resident/PRESENTATION-20261026.md) | 历史决策／记录／模块参考；展示精简、防闪现复验与 PS／PL 滤波测时 |
| [software/pose180_pipeline/resident/README.md](software/pose180_pipeline/resident/README.md) | 现行入口／含历史章节；常驻演示核心与真实CSI→推理→HDMI |
| [software/pose180_pipeline/resident/STARTUP-PACKAGE.md](software/pose180_pipeline/resident/STARTUP-PACKAGE.md) | 现行入口／含历史章节；演示启动包与历史验证 |
| [software/pose180_pipeline/resident/STUTTER-VALIDATION.md](software/pose180_pipeline/resident/STUTTER-VALIDATION.md) | 历史决策／记录／模块参考；r5：卡顿优化、PC观察与联合长测 |
| [software/pose180_pipeline/resident/TOP3-VALIDATION.md](software/pose180_pipeline/resident/TOP3-VALIDATION.md) | 历史决策／记录／模块参考；r45复验与Top-3置信度筛选 |
| [software/pose180_pipeline/resident/TX-LEASE.md](software/pose180_pipeline/resident/TX-LEASE.md) | 历史决策／记录／模块参考；r6：TX持续任务与定期续期 |
| [software/pose180_pipeline/resident/WINDOW-RECOVERY.md](software/pose180_pipeline/resident/WINDOW-RECOVERY.md) | 历史决策／记录／模块参考；r7：共同窗口诊断与更早软恢复 |
| [software/pose180_pipeline/RESULTS.md](software/pose180_pipeline/RESULTS.md) | 历史决策／记录／模块参考；2026-10-25：180-query实测、归档修正与HDMI启动停止 |
| [software/pose180_pipeline/src/README.md](software/pose180_pipeline/src/README.md) | 现行入口／含历史章节；当前核心源码 |
| [software/pose180_pipeline/tests/README.md](software/pose180_pipeline/tests/README.md) | 现行入口／含历史章节；离线测试位置 |

</details>

<details>
<summary>训练采集及部署工具（36份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [tools/boot-diagnostics/20261002/MEDIA-TEST-PLAN.md](tools/boot-diagnostics/20261002/MEDIA-TEST-PLAN.md) | 历史决策／记录／模块参考；当前 SD 卡/读卡器全容量检测方案（待批准） |
| [tools/boot-diagnostics/20261002/new_reader_20261002_191749/RESULTS.md](tools/boot-diagnostics/20261002/new_reader_20261002_191749/RESULTS.md) | 历史决策／记录／模块参考；更换绿联读卡器并重新制作后的只读复核（2026-10-02 19:17） |
| [tools/boot-diagnostics/20261002/remade_20261002_164505/RESULTS.md](tools/boot-diagnostics/20261002/remade_20261002_164505/RESULTS.md) | 历史决策／记录／模块参考；重制 SD 卡后的只读复核（2026-10-02 16:45） |
| [tools/boot-diagnostics/20261002/RESULTS.md](tools/boot-diagnostics/20261002/RESULTS.md) | 历史决策／记录／模块参考；Lite SD 启动只读排查（2026-10-02） |
| [tools/boot-diagnostics/20261002/user_h2testw_20261002_193901/RESULTS.md](tools/boot-diagnostics/20261002/user_h2testw_20261002_193901/RESULTS.md) | 历史决策／记录／模块参考；补充 H2testw 结果的分析 |
| [tools/csi-planning/ROUTER-CSI-FEASIBILITY-20261014.md](tools/csi-planning/ROUTER-CSI-FEASIBILITY-20261014.md) | 历史决策／记录／模块参考；路由器替代采集节点：可行性与模型影响 |
| [tools/csi-planning/RT-AC86U-NEXMON-AUDIT-20261017.md](tools/csi-planning/RT-AC86U-NEXMON-AUDIT-20261017.md) | 历史决策／记录／模块参考；RT-AC86U芯片版本与Nexmon部署查证 |
| [tools/kinect/README.md](tools/kinect/README.md) | 历史决策／记录／模块参考；Kinect v2 采集与微调准备 |
| [tools/mcp-validation/ip-reuse/ANALYSIS.md](tools/mcp-validation/ip-reuse/ANALYSIS.md) | 历史决策／记录／模块参考；Vivado 现成 IP → Procise：可行性分析 |
| [tools/mcp-validation/ip-reuse/PLAN.md](tools/mcp-validation/ip-reuse/PLAN.md) | 历史决策／记录／模块参考；真实 xlconcat IP 流水灯：已批准试验方案 |
| [tools/mcp-validation/ip-reuse/RESULTS.md](tools/mcp-validation/ip-reuse/RESULTS.md) | 历史决策／记录／模块参考；真实 xlconcat IP → Procise → Lite 实板验证结果 |
| [tools/mcp-validation/led1324/PLAN.md](tools/mcp-validation/led1324/PLAN.md) | 历史决策／记录／模块参考；LED1→3→2→4：Vivado / Procise MCP 衔接验证方案 |
| [tools/mcp-validation/led1324/RESULTS.md](tools/mcp-validation/led1324/RESULTS.md) | 历史决策／记录／模块参考；LED1→3→2→4：当前工具会话 Vivado / Procise MCP 验证 |
| [tools/mcp-validation/PLAN.md](tools/mcp-validation/PLAN.md) | 历史决策／记录／模块参考；Procise / Vivado MCP 验证方案（首版已批准并完成独立验证） |
| [tools/mcp-validation/RESULTS.md](tools/mcp-validation/RESULTS.md) | 历史决策／记录／模块参考；Procise / Vivado MCP 验证记录 |
| [tools/nexmon/board/README.md](tools/nexmon/board/README.md) | 历史决策／记录／模块参考；路由器直接进入开发板：软件候选 |
| [tools/nexmon/DEPLOYMENT-PLAN.md](tools/nexmon/DEPLOYMENT-PLAN.md) | 历史决策／记录／模块参考；RT-AC86U 到货后的部署与 CSI 验证方案 |
| [tools/nexmon/README.md](tools/nexmon/README.md) | 历史决策／记录／模块参考；RT-AC86U Nexmon 采集状态与恢复入口 |
| [tools/pose180/deploy/RESULTS.md](tools/pose180/deploy/RESULTS.md) | 历史决策／记录／模块参考；180-query转换、板端验证与高压测试 |
| [tools/pose180/PLAN.md](tools/pose180/PLAN.md) | 历史决策／记录／模块参考；180-query、无TopK、共享joint decoder修改方案 |
| [tools/pose180/STATUS.md](tools/pose180/STATUS.md) | 历史决策／记录／模块参考；180-query共享模型：训练状态与恢复入口 |
| [tools/pose180/TRAINING-ANALYSIS-20261027.md](tools/pose180/TRAINING-ANALYSIS-20261027.md) | 历史决策／记录／模块参考；180-query从零训练平台期分析与下一轮方案 |
| [tools/pose26-diff-nodecay/20261004/PLAN.md](tools/pose26-diff-nodecay/20261004/PLAN.md) | 历史决策／记录／模块参考；已批准的分化分支零衰减对照实验（2026-10-04） |
| [tools/pose26-diff-nodecay/20261004/README.md](tools/pose26-diff-nodecay/20261004/README.md) | 历史决策／记录／模块参考；分化分支关闭衰减：10轮从零对照实验 |
| [tools/pose26-diff-nodecay/20261004/RESULTS.md](tools/pose26-diff-nodecay/20261004/RESULTS.md) | 历史决策／记录／模块参考；分化分支零衰减10轮：完成核验与结果（2026-10-04） |
| [tools/pose26-scratch/20261004/PLAN.md](tools/pose26-scratch/20261004/PLAN.md) | 历史决策／记录／模块参考；26版500轮全新训练：已批准范围 |
| [tools/pose26-scratch/20261004/README.md](tools/pose26-scratch/20261004/README.md) | 历史决策／记录／模块参考；26版pose-only：全新初始化500轮Adam训练 |
| [tools/pose26-scratch/20261004/STATUS-20261004-0908.md](tools/pose26-scratch/20261004/STATUS-20261004-0908.md) | 历史决策／记录／模块参考；500轮从头实验：2026-10-04 09:08检查结果 |
| [tools/pose26-transfer/20261003/MONITOR.md](tools/pose26-transfer/20261003/MONITOR.md) | 历史决策／记录／模块参考；训练结果定时检查 |
| [tools/pose26-transfer/20261003/PAPER_AUDIT.md](tools/pose26-transfer/20261003/PAPER_AUDIT.md) | 历史决策／记录／模块参考；TPAMI 2026 姿态路径核对 |
| [tools/pose26-transfer/20261003/README.md](tools/pose26-transfer/20261003/README.md) | 历史决策／记录／模块参考；2026姿态模型：epoch442迁移实验 |
| [tools/pose26-transfer/20261003/RESULTS.md](tools/pose26-transfer/20261003/RESULTS.md) | 历史决策／记录／模块参考；2026姿态迁移：首轮10轮结果 |
| [tools/pose26-transfer/20261004/PLAN.md](tools/pose26-transfer/20261004/PLAN.md) | 历史决策／记录／模块参考；26版姿态模型后续正式训练方案（待人工确认） |
| [tools/procise_mcp/README.md](tools/procise_mcp/README.md) | 历史决策／记录／模块参考；Procise Lite MCP 首版 |
| [tools/README.md](tools/README.md) | 历史决策／记录／模块参考；Windows Icraft 独立依赖 |
| [tools/sd-image-validation/20261003-expand-root-COMMANDS.md](tools/sd-image-validation/20261003-expand-root-COMMANDS.md) | 历史决策／记录／模块参考；Lite 新 SD 卡根分区扩容命令（2026-10-03） |

</details>

<details>
<summary>原始结果与取证报告（69份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [tools/nexmon/evidence/device-20261019-r1/REPORT.md](tools/nexmon/evidence/device-20261019-r1/REPORT.md) | 历史决策／记录／模块参考；RT-AC86U Nexmon 实机部署与 CSI 验证 |
| [tools/nexmon/evidence/dual-router-20261022-r1/REPORT.md](tools/nexmon/evidence/dual-router-20261022-r1/REPORT.md) | 历史决策／记录／模块参考；双RT-AC86U专用发射、300Hz与相位验证 |
| [tools/nexmon/evidence/fourth-router-20261025-r1/REPORT.md](tools/nexmon/evidence/fourth-router-20261025-r1/REPORT.md) | 历史决策／记录／模块参考；第四台RT-AC86U基础CSI接收验证 |
| [tools/nexmon/evidence/intel-phase-20261023-r1/REPORT.md](tools/nexmon/evidence/intel-phase-20261023-r1/REPORT.md) | 历史决策／记录／模块参考；论文原始与对齐CSI的只读相位核查 |
| [tools/nexmon/evidence/multirx-20261025-r1/REPORT.md](tools/nexmon/evidence/multirx-20261025-r1/REPORT.md) | 历史决策／记录／模块参考；RT-AC86U四机：1发3收及300Hz同事件对齐验证 |
| [tools/nexmon/evidence/second-router-20261022-r1/REPORT.md](tools/nexmon/evidence/second-router-20261022-r1/REPORT.md) | 历史决策／记录／模块参考；第二台RT-AC86U实机兼容与基础CSI接收验证 |
| [tools/nexmon/evidence/third-router-20261023-r1/REPORT.md](tools/nexmon/evidence/third-router-20261023-r1/REPORT.md) | 历史决策／记录／模块参考；第三台RT-AC86U基础接收验证 |
| [tools/nexmon/evidence/third300-20261023-r1/REPORT.md](tools/nexmon/evidence/third300-20261023-r1/REPORT.md) | 历史决策／记录／模块参考；第三台RT-AC86U的300Hz采样验证 |
| [tools/pose-v1/evidence/ai-hdmi-cold-consumed-20261024-r43/RESULTS.md](tools/pose-v1/evidence/ai-hdmi-cold-consumed-20261024-r43/RESULTS.md) | 历史决策／记录／模块参考；r43：单次冷启动对照，目标异常未出现 |
| [tools/pose-v1/evidence/ai-hdmi-consumed-joint-20261024-r41/RESULTS.md](tools/pose-v1/evidence/ai-hdmi-consumed-joint-20261024-r41/RESULTS.md) | 历史决策／记录／模块参考；r41：同启动异常消费后联合验证，目标事件未出现 |
| [tools/pose-v1/evidence/ai-hdmi-consumed-joint-20261024-r42/RESULTS.md](tools/pose-v1/evidence/ai-hdmi-consumed-joint-20261024-r42/RESULTS.md) | 历史决策／记录／模块参考；r42：重复温重启取样，目标异常未出现 |
| [tools/pose-v1/evidence/ai-hdmi-drain-joint-20261024-r39/RESULTS.md](tools/pose-v1/evidence/ai-hdmi-drain-joint-20261024-r39/RESULTS.md) | 历史决策／记录／模块参考；r39：启动消费位流下的 AI→HDMI 联合验证 |
| [tools/pose-v1/evidence/ai-hdmi-joint-20261023-r36/RESULTS.md](tools/pose-v1/evidence/ai-hdmi-joint-20261023-r36/RESULTS.md) | 历史决策／记录／模块参考；AI → HDMI 联合测试状态（2026-10-23） |
| [tools/pose-v1/evidence/ai-hdmi-startup-control-20261024-r44/PLAN.md](tools/pose-v1/evidence/ai-hdmi-startup-control-20261024-r44/PLAN.md) | 历史决策／记录／模块参考；r44：已授权的启动前置状态有界对照 |
| [tools/pose-v1/evidence/ai-hdmi-startup-control-20261024-r44/RESULTS.md](tools/pose-v1/evidence/ai-hdmi-startup-control-20261024-r44/RESULTS.md) | 历史决策／记录／模块参考；r44：无消费版本复现异常，消费版本本次健康、消费0拍 |
| [tools/pose-v1/evidence/ai-hdmi-timing-20261024-r40/RESULTS.md](tools/pose-v1/evidence/ai-hdmi-timing-20261024-r40/RESULTS.md) | 历史决策／记录／模块参考；r40：AI→HDMI 90帧有界联动与换帧计时诊断 |
| [tools/pose-v1/evidence/hdmi-ack-transport-20261024-r50/RESULTS.md](tools/pose-v1/evidence/hdmi-ack-transport-20261024-r50/RESULTS.md) | 历史决策／记录／模块参考；r50：普通网络归档确认耗时对照 |
| [tools/pose-v1/evidence/hdmi-boot-witness-20261019-r23/PLAN.md](tools/pose-v1/evidence/hdmi-boot-witness-20261019-r23/PLAN.md) | 历史决策／记录／模块参考；r23离线结果与待批准板测包 |
| [tools/pose-v1/evidence/hdmi-hp2-ready-20261020-r24/PLAN.md](tools/pose-v1/evidence/hdmi-hp2-ready-20261020-r24/PLAN.md) | 历史决策／记录／模块参考；r24：HP2复位协调实现与单次实板结果（包已关闭） |
| [tools/pose-v1/evidence/hdmi-library-first-20261018-r18/PLAN.md](tools/pose-v1/evidence/hdmi-library-first-20261018-r18/PLAN.md) | 历史决策／记录／模块参考；r18 单次加载顺序对照（执行完成，已回原BOOT、关闭） |
| [tools/pose-v1/evidence/hdmi-library-first-20261018-r18/REPORT.md](tools/pose-v1/evidence/hdmi-library-first-20261018-r18/REPORT.md) | 历史决策／记录／模块参考；r18 加载顺序与PL按键对照结果 |
| [tools/pose-v1/evidence/hdmi-library-reset-20261019-r22/PLAN.md](tools/pose-v1/evidence/hdmi-library-reset-20261019-r22/PLAN.md) | 历史决策／记录／模块参考；r22：SDK先加载与故障下SW6复位对照 |
| [tools/pose-v1/evidence/hdmi-long-git-20261024-r52/RESULTS.md](tools/pose-v1/evidence/hdmi-long-git-20261024-r52/RESULTS.md) | 历史决策／记录／模块参考；r52：真实启动异常消费后的有限推理/HDMI联动 |
| [tools/pose-v1/evidence/hdmi-long-native-20261024-r48/PLAN.md](tools/pose-v1/evidence/hdmi-long-native-20261024-r48/PLAN.md) | 历史决策／记录／模块参考；r48：原生RGB565接回原30Hz长链路 |
| [tools/pose-v1/evidence/hdmi-long-native-20261024-r48/RESULTS.md](tools/pose-v1/evidence/hdmi-long-native-20261024-r48/RESULTS.md) | 历史决策／记录／模块参考；r48：原生 RGB565 接入后的首次长测尝试 |
| [tools/pose-v1/evidence/hdmi-long-native-20261024-r49/PLAN.md](tools/pose-v1/evidence/hdmi-long-native-20261024-r49/PLAN.md) | 历史决策／记录／模块参考；r49：主机管道权限修正后的单次长测 |
| [tools/pose-v1/evidence/hdmi-long-native-20261024-r49/RESULTS.md](tools/pose-v1/evidence/hdmi-long-native-20261024-r49/RESULTS.md) | 历史决策／记录／模块参考；r49：原生RGB565实际联动与30Hz吞吐卡点 |
| [tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/RESULTS.md](tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/RESULTS.md) | 历史决策／记录／模块参考；r53 单 SDK 线程推理与 HDMI 流水调度 |
| [tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r32/RESULTS.md](tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r32/RESULTS.md) | 历史决策／记录／模块参考；HP2 原生协议检查实板结果（2026-10-23，r32） |
| [tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r32/waveforms/cycletrace/README.md](tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r32/waveforms/cycletrace/README.md) | 历史决策／记录／模块参考；HP2 实板连续波形 |
| [tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r33/RESULTS.md](tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r33/RESULTS.md) | 历史决策／记录／模块参考；HP2 再次实板捕获结果（r33，2026-10-23） |
| [tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r33/waveforms/cycletrace/README.md](tools/pose-v1/evidence/hdmi-protocol-checker-20261023-r33/waveforms/cycletrace/README.md) | 历史决策／记录／模块参考；HP2 实板连续波形 |
| [tools/pose-v1/evidence/hdmi-ps-release-20261020-r26/PLAN.md](tools/pose-v1/evidence/hdmi-ps-release-20261020-r26/PLAN.md) | 历史决策／记录／模块参考；r26 PS／PL释放顺序取证结果 |
| [tools/pose-v1/evidence/hdmi-readframe-20261023-r34/RESULTS.md](tools/pose-v1/evidence/hdmi-readframe-20261023-r34/RESULTS.md) | 历史决策／记录／模块参考；HDMI 有限读帧实板结果（r34，2026-10-23） |
| [tools/pose-v1/evidence/hdmi-render-overlap-20261024-r51/RESULTS.md](tools/pose-v1/evidence/hdmi-render-overlap-20261024-r51/RESULTS.md) | 历史决策／记录／模块参考；r51：静态底图准备与归档确认重叠 |
| [tools/pose-v1/evidence/hdmi-render-speed-20261024-r47/RESULTS.md](tools/pose-v1/evidence/hdmi-render-speed-20261024-r47/RESULTS.md) | 历史决策／记录／模块参考；r47：直接 RGB565 渲染优化 |
| [tools/pose-v1/evidence/hdmi-reset-ab-20261018-r15/REPORT.md](tools/pose-v1/evidence/hdmi-reset-ab-20261018-r15/REPORT.md) | 历史决策／记录／模块参考；r15 纯CSR启动样本与回退 |
| [tools/pose-v1/evidence/hdmi-reset-calibration-20261018-r20/PLAN.md](tools/pose-v1/evidence/hdmi-reset-calibration-20261018-r20/PLAN.md) | 历史决策／记录／模块参考；r20 单次PL按键清零校准（执行完成，已回原BOOT、关闭） |
| [tools/pose-v1/evidence/hdmi-reset-calibration-20261018-r20/REPORT.md](tools/pose-v1/evidence/hdmi-reset-calibration-20261018-r20/REPORT.md) | 历史决策／记录／模块参考；r20 无SDK按键清零校准结果 |
| [tools/pose-v1/evidence/hdmi-reset-meter-20261019-r21/PLAN.md](tools/pose-v1/evidence/hdmi-reset-meter-20261019-r21/PLAN.md) | 历史决策／记录／模块参考；r21：纠正按键后的r9复位／启动分段对照 |
| [tools/pose-v1/evidence/hdmi-reset-values-20261018-r19/PLAN.md](tools/pose-v1/evidence/hdmi-reset-values-20261018-r19/PLAN.md) | 历史决策／记录／模块参考；r19 单次补充复位取证（执行完成、已回原BOOT、关闭） |
| [tools/pose-v1/evidence/hdmi-reset-values-20261018-r19/REPORT.md](tools/pose-v1/evidence/hdmi-reset-values-20261018-r19/REPORT.md) | 历史决策／记录／模块参考；r19 单次补充取证结果 |
| [tools/pose-v1/evidence/hdmi-software-init-20261018-r16/PLAN.md](tools/pose-v1/evidence/hdmi-software-init-20261018-r16/PLAN.md) | 历史决策／记录／模块参考；r16 同一启动中的SDK库加载／Open对照（待补充批准） |
| [tools/pose-v1/evidence/hdmi-software-init-20261018-r16/REPORT.md](tools/pose-v1/evidence/hdmi-software-init-20261018-r16/REPORT.md) | 历史决策／记录／模块参考；r16 原位库加载／Open分段结果 |
| [tools/pose-v1/evidence/hdmi-startup-20261018-r14/PLAN.md](tools/pose-v1/evidence/hdmi-startup-20261018-r14/PLAN.md) | 历史决策／记录／模块参考；r14 启动诊断：复用 r9，区分 BOOT 与 Device::Open |
| [tools/pose-v1/evidence/hdmi-startup-20261018-r14/REPORT.md](tools/pose-v1/evidence/hdmi-startup-20261018-r14/REPORT.md) | 历史决策／记录／模块参考；r14：首次捕获故障启动的 Open 前异常 |
| [tools/pose-v1/evidence/hdmi-startup-combined-20261018-r17/PLAN.md](tools/pose-v1/evidence/hdmi-startup-combined-20261018-r17/PLAN.md) | 历史决策／记录／模块参考；r17 合并的跨启动诊断（已批准、执行完成、已关闭） |
| [tools/pose-v1/evidence/hdmi-startup-combined-20261018-r17/REPORT.md](tools/pose-v1/evidence/hdmi-startup-combined-20261018-r17/REPORT.md) | 历史决策／记录／模块参考；r17 跨启动分段观测结果 |
| [tools/pose-v1/evidence/hdmi-startup-stability-20261020-r25/PLAN.md](tools/pose-v1/evidence/hdmi-startup-stability-20261020-r25/PLAN.md) | 历史决策／记录／模块参考；r25：同r24位流的无按键启动对照（首例异常，包已关闭） |
| [tools/pose-v1/evidence/hp2-bounded-drain-20261024-r38/RESULTS.md](tools/pose-v1/evidence/hp2-bounded-drain-20261024-r38/RESULTS.md) | 历史决策／记录／模块参考；r38：启动异常返回的有界消费实板验证 |
| [tools/pose-v1/evidence/hp2-deferred-consume-20261024-r45/RESULTS.md](tools/pose-v1/evidence/hp2-deferred-consume-20261024-r45/RESULTS.md) | 历史决策／记录／模块参考；r45：同启动有限消费诊断的物理验收与首次板测 |
| [tools/pose-v1/evidence/hp2-mmio32-20261024-r46/PLAN.md](tools/pose-v1/evidence/hp2-mmio32-20261024-r46/PLAN.md) | 历史决策／记录／模块参考；r46：原生单次 MMIO32 修正与有界板测 |
| [tools/pose-v1/evidence/hp2-mmio32-20261024-r46/RESULTS.md](tools/pose-v1/evidence/hp2-mmio32-20261024-r46/RESULTS.md) | 历史决策／记录／模块参考；r46 实板结果：真实异常已消费，显示验证未通过 |
| [tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/RESULTS.md](tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/RESULTS.md) | 历史决策／记录／模块参考；r37 启动协议诊断：实板异常、源码对照与恢复结果 |
| [tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/cycletrace/README.md](tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/cycletrace/README.md) | 历史决策／记录／模块参考；HP2 实板连续波形 |
| [tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/README.md](tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/README.md) | 历史决策／记录／模块参考；HP2 启动异常 r37：原生协议检查实板数据 |
| [tools/pose180/results/analysis-epoch50-counts-r1/REPORT.md](tools/pose180/results/analysis-epoch50-counts-r1/REPORT.md) | 历史决策／记录／模块参考；第50轮：高分候选数量与人数分组分析 |
| [tools/pose180/results/comparison-100-vs180-epoch50-epoch59/REPORT.md](tools/pose180/results/comparison-100-vs180-epoch50-epoch59/REPORT.md) | 历史决策／记录／模块参考；第59轮、50轮180-query与原100-query三组对比 |
| [tools/pose180/results/comparison-100-vs180-epoch50/REPORT.md](tools/pose180/results/comparison-100-vs180-epoch50/REPORT.md) | 历史决策／记录／模块参考；原epoch442的100-query与迁移第50轮180-query对比 |
| [tools/pose180/results/final-delivery-20261023-r1/comparison/REPORT.md](tools/pose180/results/final-delivery-20261023-r1/comparison/REPORT.md) | 历史决策／记录／模块参考；100轮最终最佳第99轮与epoch442、第59轮对比 |
| [tools/nexmon/evidence/preparation-20261017-r1/REPORT.md](tools/nexmon/evidence/preparation-20261017-r1/REPORT.md) | 历史准备阶段的原始报告 |
| [tools/pose-output/evidence/pc-replay-20261018-r1/REPORT.md](tools/pose-output/evidence/pc-replay-20261018-r1/REPORT.md) | 历史PC回放阶段的原始报告 |
| [tools/pose-v1/evidence/architecture-output-20261017-r1/REPORT.md](tools/pose-v1/evidence/architecture-output-20261017-r1/REPORT.md) | 历史架构输出整理的原始报告 |
| [tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/ADR/README.md](tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/ADR/README.md) | 架构调整前的冻结快照，按原阶段阅读 |
| [tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/ARCHITECTURE-DISCUSSION-20261015.md](tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/ARCHITECTURE-DISCUSSION-20261015.md) | 架构调整前的冻结快照，按原阶段阅读 |
| [tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/Done.md](tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/Done.md) | 架构调整前的冻结快照，按原阶段阅读 |
| [tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/FPGA/README.md](tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/FPGA/README.md) | 架构调整前的冻结快照，按原阶段阅读 |
| [tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/PROJECT-PROGRESS.md](tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/PROJECT-PROGRESS.md) | 架构调整前的冻结快照，按原阶段阅读 |
| [tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/REFERENCES.md](tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/REFERENCES.md) | 架构调整前的冻结快照，按原阶段阅读 |

</details>

<details>
<summary>早期pose-v1开发历史（164份）</summary>

| 文档 | 用途与范围 |
|---|---|
| [tools/pose-v1/APPLICATION-COMMANDS-20261007.md](tools/pose-v1/APPLICATION-COMMANDS-20261007.md) | 历史决策／记录／模块参考；首批生产接口与TCP验证命令 |
| [tools/pose-v1/APPLICATION-RESULTS-20261007.md](tools/pose-v1/APPLICATION-RESULTS-20261007.md) | 历史决策／记录／模块参考；E1-A生产接口与E1-B TCP回放结果（2026-10-07） |
| [tools/pose-v1/AXI-READ-NEXT-20261011.md](tools/pose-v1/AXI-READ-NEXT-20261011.md) | 历史决策／记录／模块参考；下一阶段：生产者完成契约与证据交接 |
| [tools/pose-v1/AXI-READ-RESPONSIBILITY-20261011.md](tools/pose-v1/AXI-READ-RESPONSIBILITY-20261011.md) | 历史决策／记录／模块参考；并发坏索引责任证据入口（本机审阅版） |
| [tools/pose-v1/AXI-READ-RESULTS-20261011.md](tools/pose-v1/AXI-READ-RESULTS-20261011.md) | 历史决策／记录／模块参考；匹配 AXI／UDMA 读路径审查与双模式内存对照 |
| [tools/pose-v1/BOUNDED-LOAD-PLAN-20261009.md](tools/pose-v1/BOUNDED-LOAD-PLAN-20261009.md) | 历史决策／记录／模块参考；103次低日志有限门检实施 |
| [tools/pose-v1/BOUNDED-LOAD-RESULTS-20261009.md](tools/pose-v1/BOUNDED-LOAD-RESULTS-20261009.md) | 历史决策／记录／模块参考；103次入口实施、门检及真实设备源异常取证 |
| [tools/pose-v1/BOUNDED-MEASUREMENT-DESIGN-20261008.md](tools/pose-v1/BOUNDED-MEASUREMENT-DESIGN-20261008.md) | 历史决策／记录／模块参考；更长有界计量入口设计 |
| [tools/pose-v1/COMBINED-READ-NEXT-20261010.md](tools/pose-v1/COMBINED-READ-NEXT-20261010.md) | 历史决策／记录／模块参考；当前恢复入口与最小取证方案 |
| [tools/pose-v1/COMBINED-READ-RESULTS-20261010.md](tools/pose-v1/COMBINED-READ-RESULTS-20261010.md) | 历史决策／记录／模块参考；公开read、显示子进程、TCP与RTSP组合结果 |
| [tools/pose-v1/CPU-ADAPTER-BUILD-FIX-20261006.md](tools/pose-v1/CPU-ADAPTER-BUILD-FIX-20261006.md) | 历史决策／记录／模块参考；CPU候选构建：容器Python前提修正（2026-10-06，已批准并应用） |
| [tools/pose-v1/CPU-ADAPTER-COMMANDS.md](tools/pose-v1/CPU-ADAPTER-COMMANDS.md) | 历史决策／记录／模块参考；CPU候选验证：人工操作命令（2026-10-06修正） |
| [tools/pose-v1/CPU-ADAPTER-COMPILE-FIX-20261006.md](tools/pose-v1/CPU-ADAPTER-COMPILE-FIX-20261006.md) | 历史决策／记录／模块参考；CPU候选r1编译问题：源码与日志修正（2026-10-06，已批准并应用） |
| [tools/pose-v1/CPU-ADAPTER-RESULTS-20261006.md](tools/pose-v1/CPU-ADAPTER-RESULTS-20261006.md) | 历史决策／记录／模块参考；CPU算子注册与最小适配：Lite验收结果（2026-10-06） |
| [tools/pose-v1/CPU-ADAPTER.md](tools/pose-v1/CPU-ADAPTER.md) | 历史决策／记录／模块参考；CPU算子注册与最小适配：批准范围及源码交付（2026-10-05） |
| [tools/pose-v1/CRLF-CHECKSUM-FIX.md](tools/pose-v1/CRLF-CHECKSUM-FIX.md) | 历史决策／记录／模块参考；校验清单CRLF问题诊断与最小修正方案（2026-10-05，待批准） |
| [tools/pose-v1/DEMO-RESULTS-20261011.md](tools/pose-v1/DEMO-RESULTS-20261011.md) | 历史决策／记录／模块参考；2026-10-11 端到端演示结果 |
| [tools/pose-v1/DISPLAY-PROCESS-NEXT-20261008.md](tools/pose-v1/DISPLAY-PROCESS-NEXT-20261008.md) | 历史决策／记录／模块参考；独立显示子进程后的接续方案 |
| [tools/pose-v1/DISPLAY-PROCESS-RESULTS-20261008.md](tools/pose-v1/DISPLAY-PROCESS-RESULTS-20261008.md) | 历史决策／记录／模块参考；独立显示子进程可行性验证结果 |
| [tools/pose-v1/ENVIRONMENT-QUERY-20261005.md](tools/pose-v1/ENVIRONMENT-QUERY-20261005.md) | 历史决策／记录／模块参考；独立推理门检：用户环境查询结果（2026-10-05） |
| [tools/pose-v1/F0-INTEGRATION-PREP-20261007.md](tools/pose-v1/F0-INTEGRATION-PREP-20261007.md) | 历史决策／记录／模块参考；实际推理画面接入编码的准备（2026-10-07） |
| [tools/pose-v1/FINAL-EVIDENCE-NEXT-20261010.md](tools/pose-v1/FINAL-EVIDENCE-NEXT-20261010.md) | 历史决策／记录／模块参考；582上游边界最小取证准备 |
| [tools/pose-v1/FINAL-EVIDENCE-PLAN-20261010.md](tools/pose-v1/FINAL-EVIDENCE-PLAN-20261010.md) | 历史决策／记录／模块参考；最终输出门检取证 |
| [tools/pose-v1/FINAL-EVIDENCE-RESULTS-20261010.md](tools/pose-v1/FINAL-EVIDENCE-RESULTS-20261010.md) | 历史决策／记录／模块参考；最终门检完整保存与晚源取证结果 |
| [tools/pose-v1/FORWARD-DATA-RECOVERY-NEXT-20261009.md](tools/pose-v1/FORWARD-DATA-RECOVERY-NEXT-20261009.md) | 历史决策／记录／模块参考；异常数据块的下一有限取证 |
| [tools/pose-v1/FORWARD-TRACE-R3-RESULTS-20261009.md](tools/pose-v1/FORWARD-TRACE-R3-RESULTS-20261009.md) | 历史决策／记录／模块参考；纯计时与异常Host输入取证结果 |
| [tools/pose-v1/FORWARD-TRACE-RESULTS-20261008.md](tools/pose-v1/FORWARD-TRACE-RESULTS-20261008.md) | 历史决策／记录／模块参考；前向尖峰诊断首轮结果 |
| [tools/pose-v1/FULL-FLOW-PLAN-20261007.md](tools/pose-v1/FULL-FLOW-PLAN-20261007.md) | 历史决策／记录／模块参考；首版全流程接入计划（2026-10-07） |
| [tools/pose-v1/H0-INTEGRATION-AUDIT-20261007.md](tools/pose-v1/H0-INTEGRATION-AUDIT-20261007.md) | 历史决策／记录／模块参考；视频与骨架接入资料核对（H0，2026-10-07） |
| [tools/pose-v1/HDMI-STATIC-AUDIT.md](tools/pose-v1/HDMI-STATIC-AUDIT.md) | 历史决策／记录／模块参考；HDMI配套与720p60静态核对（2026-10-05） |
| [tools/pose-v1/HOST-BINDING-REVIEW-20261005.md](tools/pose-v1/HOST-BINDING-REVIEW-20261005.md) | 历史决策／记录／模块参考；Lite Host参考绑定失败审查（2026-10-05） |
| [tools/pose-v1/HOST-REGISTRY-PROBE-PLAN.md](tools/pose-v1/HOST-REGISTRY-PROBE-PLAN.md) | 历史决策／记录／模块参考；Host注册探针方案（2026-10-05，已批准并执行） |
| [tools/pose-v1/HOST-REGISTRY-RESULTS-20261005.md](tools/pose-v1/HOST-REGISTRY-RESULTS-20261005.md) | 历史决策／记录／模块参考；Lite Host注册探针结果（2026-10-05） |
| [tools/pose-v1/HOST-STAGING-FAULT-NEXT-20261009.md](tools/pose-v1/HOST-STAGING-FAULT-NEXT-20261009.md) | 历史决策／记录／模块参考；设备源与Host暂存差异后的最小取证准备 |
| [tools/pose-v1/INFERENCE-COMMANDS.md](tools/pose-v1/INFERENCE-COMMANDS.md) | 历史决策／记录／模块参考；2024 epoch442 独立混合推理门检：人工操作说明（2026-10-05） |
| [tools/pose-v1/INPUT-READ-NEXT-20261010.md](tools/pose-v1/INPUT-READ-NEXT-20261010.md) | 历史决策／记录／模块参考；下一接续：公开 read 适配层的组合回归 |
| [tools/pose-v1/INPUT-READ-RESULTS-20261010.md](tools/pose-v1/INPUT-READ-RESULTS-20261010.md) | 历史决策／记录／模块参考；公开 read 输入桥：真实拥有画面有限验证 |
| [tools/pose-v1/INVOCATION-EVIDENCE-INTEGRATION-NEXT-20261009.md](tools/pose-v1/INVOCATION-EVIDENCE-INTEGRATION-NEXT-20261009.md) | 历史决策／记录／模块参考；有限输出异常的单帧取证与独立落盘接入契约 |
| [tools/pose-v1/INVOCATION-GUARD-NEXT-20261009.md](tools/pose-v1/INVOCATION-GUARD-NEXT-20261009.md) | 历史决策／记录／模块参考；下一最小定位：192生产完成与连续搬运残留 |
| [tools/pose-v1/INVOCATION-GUARD-RESULTS-20261009.md](tools/pose-v1/INVOCATION-GUARD-RESULTS-20261009.md) | 历史决策／记录／模块参考；单帧拥有值与独立落盘接入：本批结果 |
| [tools/pose-v1/LITE-HOST-COMMANDS.md](tools/pose-v1/LITE-HOST-COMMANDS.md) | 历史决策／记录／模块参考；Lite Host三样本数值参考：人工操作说明（2026-10-05） |
| [tools/pose-v1/LIVE-RESULTS-20261008.md](tools/pose-v1/LIVE-RESULTS-20261008.md) | 历史决策／记录／模块参考；真实在线串联与网络模块验证结果 |
| [tools/pose-v1/MIXED-APPLY-FAILURE-20261006.md](tools/pose-v1/MIXED-APPLY-FAILURE-20261006.md) | 历史决策／记录／模块参考；apply-r1失败与SSH退出审查（2026-10-06） |
| [tools/pose-v1/MIXED-BINDING-R2-APPLY-RESULTS.md](tools/pose-v1/MIXED-BINDING-R2-APPLY-RESULTS.md) | 历史决策／记录／模块参考；绑定快照r2 apply取证与停止原因 |
| [tools/pose-v1/MIXED-BINDING-R2-BUILD-RESULTS.md](tools/pose-v1/MIXED-BINDING-R2-BUILD-RESULTS.md) | 历史决策／记录／模块参考；绑定快照r2构建验收（2026-10-06） |
| [tools/pose-v1/MIXED-BINDING-R2-COMMANDS.md](tools/pose-v1/MIXED-BINDING-R2-COMMANDS.md) | 历史决策／记录／模块参考；已批准的绑定快照r2执行命令 |
| [tools/pose-v1/MIXED-BINDING-R2-HOST-RESULTS.md](tools/pose-v1/MIXED-BINDING-R2-HOST-RESULTS.md) | 历史决策／记录／模块参考；绑定快照r2 Host回归与离线预检复核 |
| [tools/pose-v1/MIXED-BINDING-R2-MEMORY-RESULTS.md](tools/pose-v1/MIXED-BINDING-R2-MEMORY-RESULTS.md) | 历史决策／记录／模块参考；绑定快照r2 SDK内存往返验收 |
| [tools/pose-v1/MIXED-BINDING-R2-OFFLINE-RESULTS.md](tools/pose-v1/MIXED-BINDING-R2-OFFLINE-RESULTS.md) | 历史决策／记录／模块参考；绑定快照r2离线门检结果 |
| [tools/pose-v1/MIXED-BINDING-SNAPSHOT-PLAN.md](tools/pose-v1/MIXED-BINDING-SNAPSHOT-PLAN.md) | 历史决策／记录／模块参考；绑定追溯最小取证方案（2026-10-06已批准） |
| [tools/pose-v1/MIXED-BUILD-REVIEW-20261006.md](tools/pose-v1/MIXED-BUILD-REVIEW-20261006.md) | 历史决策／记录／模块参考；mixed-r1构建与警告复核（2026-10-06） |
| [tools/pose-v1/MIXED-CONTENT-R4-APPLY-RESULTS.md](tools/pose-v1/MIXED-CONTENT-R4-APPLY-RESULTS.md) | 历史决策／记录／模块参考；r4 apply-only验收 |
| [tools/pose-v1/MIXED-CONTENT-R4-BUILD-RESULTS.md](tools/pose-v1/MIXED-CONTENT-R4-BUILD-RESULTS.md) | 历史决策／记录／模块参考；r4-final Host内容取证构建验收 |
| [tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md) | 历史决策／记录／模块参考；已批准的逐次Host输入内容取证r4命令 |
| [tools/pose-v1/MIXED-CONTENT-R4-DELIVERY.md](tools/pose-v1/MIXED-CONTENT-R4-DELIVERY.md) | 历史决策／记录／模块参考；r4逐次输入内容取证源码交付 |
| [tools/pose-v1/MIXED-CONTENT-R4-HOST-RESULTS.md](tools/pose-v1/MIXED-CONTENT-R4-HOST-RESULTS.md) | 历史决策／记录／模块参考；r4 Host回归与内容路径验收 |
| [tools/pose-v1/MIXED-CONTENT-R4-MEMORY-RESULTS.md](tools/pose-v1/MIXED-CONTENT-R4-MEMORY-RESULTS.md) | 历史决策／记录／模块参考；r4 SDK内存往返验收 |
| [tools/pose-v1/MIXED-CONTENT-R4-OFFLINE-RESULTS.md](tools/pose-v1/MIXED-CONTENT-R4-OFFLINE-RESULTS.md) | 历史决策／记录／模块参考；r4离线门检验收 |
| [tools/pose-v1/MIXED-CONTENT-R4-ONE-RESULTS.md](tools/pose-v1/MIXED-CONTENT-R4-ONE-RESULTS.md) | 历史决策／记录／模块参考；r4 308单样本内容取证验收 |
| [tools/pose-v1/MIXED-CONTENT-R4-THREE-FAILURE.md](tools/pose-v1/MIXED-CONTENT-R4-THREE-FAILURE.md) | 历史决策／记录／模块参考；r4三样本退出1：内容边界分析 |
| [tools/pose-v1/MIXED-CONTENT-R5-READINESS-PLAN.md](tools/pose-v1/MIXED-CONTENT-R5-READINESS-PLAN.md) | 历史决策／记录／模块参考；r5完成状态与PS/NPU交接取证候选（未批准） |
| [tools/pose-v1/MIXED-FRAME-STATE-R6-RESULTS.md](tools/pose-v1/MIXED-FRAME-STATE-R6-RESULTS.md) | 历史决策／记录／模块参考；不同输入同输出问题已解决：r6实板工程验收 |
| [tools/pose-v1/MIXED-FRAME-STATE-R6-SOURCE.md](tools/pose-v1/MIXED-FRAME-STATE-R6-SOURCE.md) | 历史决策／记录／模块参考；跨帧执行状态修正r6：来源与边界 |
| [tools/pose-v1/MIXED-FUSION-BINDING-FIX-PLAN.md](tools/pose-v1/MIXED-FUSION-BINDING-FIX-PLAN.md) | 历史决策／记录／模块参考；正式融合绑定门检修正方案（已批准） |
| [tools/pose-v1/MIXED-FUSION-R3-APPLY-RESULTS.md](tools/pose-v1/MIXED-FUSION-R3-APPLY-RESULTS.md) | 历史决策／记录／模块参考；正式融合追溯r3 apply验收 |
| [tools/pose-v1/MIXED-FUSION-R3-BUILD-RESULTS.md](tools/pose-v1/MIXED-FUSION-R3-BUILD-RESULTS.md) | 历史决策／记录／模块参考；正式融合追溯r3构建验收 |
| [tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md) | 历史决策／记录／模块参考；已批准的融合追溯修正r3命令 |
| [tools/pose-v1/MIXED-FUSION-R3-DELIVERY.md](tools/pose-v1/MIXED-FUSION-R3-DELIVERY.md) | 历史决策／记录／模块参考；融合绑定门检修正r3交付 |
| [tools/pose-v1/MIXED-FUSION-R3-HOST-RESULTS.md](tools/pose-v1/MIXED-FUSION-R3-HOST-RESULTS.md) | 历史决策／记录／模块参考；正式融合追溯r3 Host回归验收 |
| [tools/pose-v1/MIXED-FUSION-R3-MEMORY-RESULTS.md](tools/pose-v1/MIXED-FUSION-R3-MEMORY-RESULTS.md) | 历史决策／记录／模块参考；正式融合追溯r3 SDK内存往返验收 |
| [tools/pose-v1/MIXED-FUSION-R3-OFFLINE-RESULTS.md](tools/pose-v1/MIXED-FUSION-R3-OFFLINE-RESULTS.md) | 历史决策／记录／模块参考；正式融合追溯r3离线门检验收 |
| [tools/pose-v1/MIXED-FUSION-R3-ONE-RESULTS.md](tools/pose-v1/MIXED-FUSION-R3-ONE-RESULTS.md) | 历史决策／记录／模块参考；r3 308单样本混合计算工程验收 |
| [tools/pose-v1/MIXED-FUSION-R3-THREE-FAILURE.md](tools/pose-v1/MIXED-FUSION-R3-THREE-FAILURE.md) | 历史决策／记录／模块参考；r3三样本停止：不同输入得到相同输出 |
| [tools/pose-v1/MIXED-HOST-RESULTS-20261006.md](tools/pose-v1/MIXED-HOST-RESULTS-20261006.md) | 历史决策／记录／模块参考；mixed-r1 Host桥回归验收（2026-10-06） |
| [tools/pose-v1/MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md](tools/pose-v1/MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md) | 历史决策／记录／模块参考；连续forward输入内容诊断方案（已批准） |
| [tools/pose-v1/MIXED-MEMORY-RESULTS-20261006.md](tools/pose-v1/MIXED-MEMORY-RESULTS-20261006.md) | 历史决策／记录／模块参考；mixed-r1 SDK设备内存往返验收（2026-10-06） |
| [tools/pose-v1/MIXED-OFFLINE-RESULTS-20261006.md](tools/pose-v1/MIXED-OFFLINE-RESULTS-20261006.md) | 历史决策／记录／模块参考；mixed-r1真实参数与PS离线验收（2026-10-06） |
| [tools/pose-v1/MIXED-VALIDATION-COMMANDS.md](tools/pose-v1/MIXED-VALIDATION-COMMANDS.md) | 历史决策／记录／模块参考；混合验证人工操作命令（2026-10-06） |
| [tools/pose-v1/MIXED-VALIDATION.md](tools/pose-v1/MIXED-VALIDATION.md) | 历史决策／记录／模块参考；ONNX参考与PS/NPU混合工程验证（2026-10-06） |
| [tools/pose-v1/MODEL-ONLY-NEXT-20261010.md](tools/pose-v1/MODEL-ONLY-NEXT-20261010.md) | 历史决策／记录／模块参考；下一最小变量：同一程序的模型／VPU负载对照 |
| [tools/pose-v1/MODEL-ONLY-RESULTS-20261010.md](tools/pose-v1/MODEL-ONLY-RESULTS-20261010.md) | 历史决策／记录／模块参考；真实混合模型移除视频负载：本批完成 |
| [tools/pose-v1/MODEL-VPU-NEXT-20261010.md](tools/pose-v1/MODEL-VPU-NEXT-20261010.md) | 历史决策／记录／模块参考；下一步：先恢复VPU首次启动条件，再完成长序列对照 |
| [tools/pose-v1/MODEL-VPU-RESULTS-20261010.md](tools/pose-v1/MODEL-VPU-RESULTS-20261010.md) | 历史决策／记录／模块参考；同一程序模型／合成VPU对照结果 |
| [tools/pose-v1/MODEL-VPU-RESUME-20261010.md](tools/pose-v1/MODEL-VPU-RESUME-20261010.md) | 历史决策／记录／模块参考；同身份模型／VPU对照：待传输恢复 |
| [tools/pose-v1/NEXT-GATE-20261007.md](tools/pose-v1/NEXT-GATE-20261007.md) | 历史决策／记录／模块参考；E0/N1/P1之后的优先事项（候选方案，未执行） |
| [tools/pose-v1/NEXT-GATE.md](tools/pose-v1/NEXT-GATE.md) | 历史决策／记录／模块参考；下一步待批准：实际运行FPGA版本查询 |
| [tools/pose-v1/NEXT-PHASE-PLAN-20261006.md](tools/pose-v1/NEXT-PHASE-PLAN-20261006.md) | 历史决策／记录／模块参考；r6之后：数值扩展、性能基线与正式应用接入计划 |
| [tools/pose-v1/NEXT-VIDEO-PLAN-20261007.md](tools/pose-v1/NEXT-VIDEO-PLAN-20261007.md) | 历史决策／记录／模块参考；下一阶段：动态骨架编码、HDMI1080p60与独立RTSP |
| [tools/pose-v1/ONLINE-INTEGRATION-NEXT-20261008.md](tools/pose-v1/ONLINE-INTEGRATION-NEXT-20261008.md) | 历史决策／记录／模块参考；F0-A3真实在线接入入口 |
| [tools/pose-v1/ONNX-REFERENCE-RESULTS-20261006.md](tools/pose-v1/ONNX-REFERENCE-RESULTS-20261006.md) | 历史决策／记录／模块参考；三样本ONNX部署参考结果（2026-10-06） |
| [tools/pose-v1/OWNED-AU-RESULTS-20261008.md](tools/pose-v1/OWNED-AU-RESULTS-20261008.md) | 历史决策／记录／模块参考；Owned AU桥与网络适配器门检（2026-10-08） |
| [tools/pose-v1/P2-RESULTS-20261007.md](tools/pose-v1/P2-RESULTS-20261007.md) | 历史决策／记录／模块参考；Profiling-off单时钟定位与错误消息优化结果 |
| [tools/pose-v1/P2-SINGLE-CLOCK-COMMANDS-20261007.md](tools/pose-v1/P2-SINGLE-CLOCK-COMMANDS-20261007.md) | 历史决策／记录／模块参考；Profiling-off单时钟候选与lazy-r4验证命令 |
| [tools/pose-v1/PIPELINE-NEXT-20261008.md](tools/pose-v1/PIPELINE-NEXT-20261008.md) | 历史决策／记录／模块参考；F0接续门检：启动分配取证→常驻编码器（2026-10-08） |
| [tools/pose-v1/PIPELINE-RESULTS-20261008.md](tools/pose-v1/PIPELINE-RESULTS-20261008.md) | 历史决策／记录／模块参考；真实推理→骨架→H.264有限接入结果（2026-10-08） |
| [tools/pose-v1/PLDDR-POSITION-NEXT-20261010.md](tools/pose-v1/PLDDR-POSITION-NEXT-20261010.md) | 历史决策／记录／模块参考；下一对照：真实混合引擎运行，移除视频负载 |
| [tools/pose-v1/PLDDR-POSITION-RESULTS-20261010.md](tools/pose-v1/PLDDR-POSITION-RESULTS-20261010.md) | 历史决策／记录／模块参考；公开分配器与较高来源位置对照：本批完成 |
| [tools/pose-v1/PRESAVED-RESULTS-20261008.md](tools/pose-v1/PRESAVED-RESULTS-20261008.md) | 历史决策／记录／模块参考；保存优先与一次规整恢复验证结果 |
| [tools/pose-v1/PRODUCER-ADDRESS-NEXT-20261011.md](tools/pose-v1/PRODUCER-ADDRESS-NEXT-20261011.md) | 历史决策／记录／模块参考；下一诊断：隔离高地址失败后的公开源读证据 |
| [tools/pose-v1/PRODUCER-ADDRESS-RESULTS-20261011.md](tools/pose-v1/PRODUCER-ADDRESS-RESULTS-20261011.md) | 历史决策／记录／模块参考；独立高地址生产者：有限前帧数据复用失配 |
| [tools/pose-v1/PRODUCER-CONTRACT-NEXT-20261011.md](tools/pose-v1/PRODUCER-CONTRACT-NEXT-20261011.md) | 历史决策／记录／模块参考；下一阶段：闭合真实融合组参考，再选择动态读事务观察 |
| [tools/pose-v1/PRODUCER-CONTRACT-RESULTS-20261011.md](tools/pose-v1/PRODUCER-CONTRACT-RESULTS-20261011.md) | 历史决策／记录／模块参考；生产者完成契约、最小视图与官方部署日志核验 |
| [tools/pose-v1/PRODUCER-COUNT-NEXT-20261009.md](tools/pose-v1/PRODUCER-COUNT-NEXT-20261009.md) | 历史决策／记录／模块参考；下一方案：受控SDK双源搬运一致性，先隔离NPU |
| [tools/pose-v1/PRODUCER-COUNT-RESULTS-20261009.md](tools/pose-v1/PRODUCER-COUNT-RESULTS-20261009.md) | 历史决策／记录／模块参考；192公开生产计数诊断结果 |
| [tools/pose-v1/PRODUCER-GROUP-NEXT-20261011.md](tools/pose-v1/PRODUCER-GROUP-NEXT-20261011.md) | 历史决策／记录／模块参考；下一诊断：同身份有／无VPU的独立生产者对照 |
| [tools/pose-v1/PRODUCER-GROUP-RESULTS-20261011.md](tools/pose-v1/PRODUCER-GROUP-RESULTS-20261011.md) | 历史决策／记录／模块参考；独立真实19成员生产者：部署与四调用结果 |
| [tools/pose-v1/PRODUCER-PHASE-NEXT-20261011.md](tools/pose-v1/PRODUCER-PHASE-NEXT-20261011.md) | 历史决策／记录／模块参考；下一控制变量：独立生产者的公开SDK地址布局 |
| [tools/pose-v1/PRODUCER-PHASE-RESULTS-20261011.md](tools/pose-v1/PRODUCER-PHASE-RESULTS-20261011.md) | 历史决策／记录／模块参考；reset前分段观察与绝对时隙门检结果 |
| [tools/pose-v1/PRODUCER-PREPARED-NEXT-20261011.md](tools/pose-v1/PRODUCER-PREPARED-NEXT-20261011.md) | 历史决策／记录／模块参考；下一最小边界：保留首次Host目的张量，失败时公开CPTR快照 |
| [tools/pose-v1/PRODUCER-PREPARED-RESULTS-20261011.md](tools/pose-v1/PRODUCER-PREPARED-RESULTS-20261011.md) | 历史决策／记录／模块参考；目录预建与首次错误/晚源对照结果 |
| [tools/pose-v1/PRODUCER-REFERENCE-NEXT-20261011.md](tools/pose-v1/PRODUCER-REFERENCE-NEXT-20261011.md) | 历史决策／记录／模块参考；下一门检：独立真实生产者，先部署再固定四调用 |
| [tools/pose-v1/PRODUCER-REFERENCE-RESULTS-20261011.md](tools/pose-v1/PRODUCER-REFERENCE-RESULTS-20261011.md) | 历史决策／记录／模块参考；真实生产者参考与mock部署结果 |
| [tools/pose-v1/PRODUCER-SOURCE-READ-NEXT-20261011.md](tools/pose-v1/PRODUCER-SOURCE-READ-NEXT-20261011.md) | 历史决策／记录／模块参考；下一最小调整：放行前准备调用目录，保留失败源读 |
| [tools/pose-v1/PRODUCER-SOURCE-READ-RESULTS-20261011.md](tools/pose-v1/PRODUCER-SOURCE-READ-RESULTS-20261011.md) | 历史决策／记录／模块参考；单调用输出租约：归还通过，物理晚源读未触发 |
| [tools/pose-v1/PRODUCER-VPU-NEXT-20261011.md](tools/pose-v1/PRODUCER-VPU-NEXT-20261011.md) | 历史决策／记录／模块参考；下一诊断：分解reset前空档并守住绝对时隙 |
| [tools/pose-v1/PRODUCER-VPU-RESULTS-20261011.md](tools/pose-v1/PRODUCER-VPU-RESULTS-20261011.md) | 历史决策／记录／模块参考；独立真实生产者与VPU对照结果 |
| [tools/pose-v1/PROJECT-STATUS-AND-NEXT-20261008.md](tools/pose-v1/PROJECT-STATUS-AND-NEXT-20261008.md) | 历史决策／记录／模块参考；当前项目进度与后续方案（2026-10-08） |
| [tools/pose-v1/READ-PHASE-NEXT-20261011.md](tools/pose-v1/READ-PHASE-NEXT-20261011.md) | 历史决策／记录／模块参考；下一阶段：匹配AXI读取实现与共享暂存责任 |
| [tools/pose-v1/READ-PHASE-RESULTS-20261011.md](tools/pose-v1/READ-PHASE-RESULTS-20261011.md) | 历史决策／记录／模块参考；首次复制返回与CPU使用前Host快照：本轮结果 |
| [tools/pose-v1/README.md](tools/pose-v1/README.md) | 历史决策／记录／模块参考；首版实施工具与证据 |
| [tools/pose-v1/REFERENCE-NEXT-PLAN.md](tools/pose-v1/REFERENCE-NEXT-PLAN.md) | 历史决策／记录／模块参考；数值参考执行路线与依赖预览方案（2026-10-05，B已批准，ORT预览待批准） |
| [tools/pose-v1/RENDER-COMMANDS-20261007.md](tools/pose-v1/RENDER-COMMANDS-20261007.md) | 历史决策／记录／模块参考；渲染与只读视频核对命令 |
| [tools/pose-v1/RENDER-RESULTS-20261007.md](tools/pose-v1/RENDER-RESULTS-20261007.md) | 历史决策／记录／模块参考；E1-C骨架渲染与V0配套核对结果（2026-10-07） |
| [tools/pose-v1/RESIDENT-RESULTS-20261008.md](tools/pose-v1/RESIDENT-RESULTS-20261008.md) | 历史决策／记录／模块参考；同进程有限常驻工作者结果（2026-10-08） |
| [tools/pose-v1/RESIDENT-SEQUENCE-NEXT-20261010.md](tools/pose-v1/RESIDENT-SEQUENCE-NEXT-20261010.md) | 历史决策／记录／模块参考；下一单因素：常驻上下文中的真实拥有画面 |
| [tools/pose-v1/RESIDENT-SEQUENCE-RESULTS-20261010.md](tools/pose-v1/RESIDENT-SEQUENCE-RESULTS-20261010.md) | 历史决策／记录／模块参考；单次常驻生命周期结果（2026-10-10） |
| [tools/pose-v1/RESULTS-300.md](tools/pose-v1/RESULTS-300.md) | 历史决策／记录／模块参考；300份真实CSI门检与25122301运行身份核验（2026-10-04） |
| [tools/pose-v1/RESUME-20261006.md](tools/pose-v1/RESUME-20261006.md) | 历史决策／记录／模块参考；唤醒恢复入口（2026-10-06） |
| [tools/pose-v1/RESUME-PICTURE-20261010.md](tools/pose-v1/RESUME-PICTURE-20261010.md) | 历史决策／记录／模块参考；真实拥有画面阶段：暂停恢复入口 |
| [tools/pose-v1/RESUME-VIDEO-20261007.md](tools/pose-v1/RESUME-VIDEO-20261007.md) | 历史决策／记录／模块参考；视频任务暂停与恢复入口（2026-10-07） |
| [tools/pose-v1/RTSP-RESULTS-20261007.md](tools/pose-v1/RTSP-RESULTS-20261007.md) | 历史决策／记录／模块参考；独立RTSP传输、重连与直接播放器结果（2026-10-07） |
| [tools/pose-v1/RUNTIME-COMMANDS-20261007.md](tools/pose-v1/RUNTIME-COMMANDS-20261007.md) | 历史决策／记录／模块参考；E0/N1/P1 r2执行与复现命令（2026-10-07） |
| [tools/pose-v1/RUNTIME-RESULTS-20261007.md](tools/pose-v1/RUNTIME-RESULTS-20261007.md) | 历史决策／记录／模块参考；E0/N1/P1运行核心、扩展数值与性能基线结果（2026-10-07） |
| [tools/pose-v1/SCRATCH-COPY-NEXT-20261010.md](tools/pose-v1/SCRATCH-COPY-NEXT-20261010.md) | 历史决策／记录／模块参考；下一定位：真实模型张量与连续复制对象身份 |
| [tools/pose-v1/SCRATCH-COPY-RESULTS-20261010.md](tools/pose-v1/SCRATCH-COPY-RESULTS-20261010.md) | 历史决策／记录／模块参考；受控 SDK 双源搬运与编码并发结果 |
| [tools/pose-v1/SDK-MAPPING-AUDIT-20261009.md](tools/pose-v1/SDK-MAPPING-AUDIT-20261009.md) | 历史决策／记录／模块参考；ARM SDK搬运、同步和映射边界核查 |
| [tools/pose-v1/shared-output-gate/README.md](tools/pose-v1/shared-output-gate/README.md) | 历史决策／记录／模块参考；共享细化输出门检 |
| [tools/pose-v1/SOURCE-COVERAGE-PLAN-20261009.md](tools/pose-v1/SOURCE-COVERAGE-PLAN-20261009.md) | 历史决策／记录／模块参考；异常读回保留后的有限覆盖与纯计时 |
| [tools/pose-v1/SOURCE-COVERAGE-RESULTS-20261009.md](tools/pose-v1/SOURCE-COVERAGE-RESULTS-20261009.md) | 历史决策／记录／模块参考；异常读回保留后的有限覆盖与纯计时结果 |
| [tools/pose-v1/SOURCE-READBACK-R4-RESULTS-20261009.md](tools/pose-v1/SOURCE-READBACK-R4-RESULTS-20261009.md) | 历史决策／记录／模块参考；r4错误后源读回：实施与有限回归结果 |
| [tools/pose-v1/STAGE-GUARD-NEXT-20261009.md](tools/pose-v1/STAGE-GUARD-NEXT-20261009.md) | 历史决策／记录／模块参考；本批后的推进准备 |
| [tools/pose-v1/STAGE-GUARD-PLAN-20261009.md](tools/pose-v1/STAGE-GUARD-PLAN-20261009.md) | 历史决策／记录／模块参考；原复制快照与582完成检查：本批执行契约 |
| [tools/pose-v1/STAGE-GUARD-RESULTS-20261009.md](tools/pose-v1/STAGE-GUARD-RESULTS-20261009.md) | 历史决策／记录／模块参考；Host快照与582完成检查：实现和有界回归结果 |
| [tools/pose-v1/STARTUP-GUARD-PLAN-20261009.md](tools/pose-v1/STARTUP-GUARD-PLAN-20261009.md) | 历史决策／记录／模块参考；三次独立启动回归与SDK映射核查执行契约 |
| [tools/pose-v1/STARTUP-GUARD-RESULTS-20261009.md](tools/pose-v1/STARTUP-GUARD-RESULTS-20261009.md) | 历史决策／记录／模块参考；独立启动回归与有限输出失配结果 |
| [tools/pose-v1/STATUS.md](tools/pose-v1/STATUS.md) | 历史决策／记录／模块参考；首版当前状态（2026-10-07，数值验收与P2更新） |
| [tools/pose-v1/SYSTEM-TIMING-NEXT-20261008.md](tools/pose-v1/SYSTEM-TIMING-NEXT-20261008.md) | 历史决策／记录／模块参考；整机计量后的最小修正方案 |
| [tools/pose-v1/SYSTEM-TIMING-RESULTS-20261008.md](tools/pose-v1/SYSTEM-TIMING-RESULTS-20261008.md) | 历史决策／记录／模块参考；有界整机单时钟计量结果 |
| [tools/pose-v1/TCP-INTEGRATION-RESULTS-20261008.md](tools/pose-v1/TCP-INTEGRATION-RESULTS-20261008.md) | 历史决策／记录／模块参考；Guarded接入与完整CSI网络链路验证结果 |
| [tools/pose-v1/TCP-RECOVERY-NEXT-20261008.md](tools/pose-v1/TCP-RECOVERY-NEXT-20261008.md) | 历史决策／记录／模块参考；首启动恢复与输出失配取证准备 |
| [tools/pose-v1/TENSOR-IDENTITY-NEXT-20261010.md](tools/pose-v1/TENSOR-IDENTITY-NEXT-20261010.md) | 历史决策／记录／模块参考；下一定位：真实类型和动态模式 SDK scratch 对照 |
| [tools/pose-v1/TENSOR-IDENTITY-RESULTS-20261010.md](tools/pose-v1/TENSOR-IDENTITY-RESULTS-20261010.md) | 历史决策／记录／模块参考；真实模型复制对象与类型取证结果 |
| [tools/pose-v1/TYPED-SCRATCH-NEXT-20261010.md](tools/pose-v1/TYPED-SCRATCH-NEXT-20261010.md) | 历史决策／记录／模块参考；下一独立对照：SDK拥有来源的地址位置 |
| [tools/pose-v1/TYPED-SCRATCH-RESULTS-20261010.md](tools/pose-v1/TYPED-SCRATCH-RESULTS-20261010.md) | 历史决策／记录／模块参考；真实类型／动态模式／VPU并发独立对照结果 |
| [tools/pose-v1/UPSTREAM-BOUNDARY-NEXT-20261011.md](tools/pose-v1/UPSTREAM-BOUNDARY-NEXT-20261011.md) | 历史决策／记录／模块参考；下一阶段：首次read／Host暂存边界定位 |
| [tools/pose-v1/UPSTREAM-BOUNDARY-RESULTS-20261011.md](tools/pose-v1/UPSTREAM-BOUNDARY-RESULTS-20261011.md) | 历史决策／记录／模块参考；原Gather及ZG上游公开边界：本轮结果 |
| [tools/pose-v1/V0-VIDEO-PAIRING-20261007.md](tools/pose-v1/V0-VIDEO-PAIRING-20261007.md) | 历史决策／记录／模块参考；V0视频配套核对：已确认部分与待确认接口 |
| [tools/pose-v1/VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md](tools/pose-v1/VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md) | 历史决策／记录／模块参考；真实骨架编码故障修正与重复验证（2026-10-07） |
| [tools/pose-v1/VIDEO-SEQUENCE-RESULTS-20261007.md](tools/pose-v1/VIDEO-SEQUENCE-RESULTS-20261007.md) | 历史决策／记录／模块参考；真实骨架视频与HDMI配套首批：VPU异常停止，HDMI未写入 |
| [tools/pose-v1/VPU-COMMANDS-20261007.md](tools/pose-v1/VPU-COMMANDS-20261007.md) | 历史决策／记录／模块参考；独立H.264有限测试：位置、产物与停止边界 |
| [tools/pose-v1/VPU-RESULTS-20261007.md](tools/pose-v1/VPU-RESULTS-20261007.md) | 历史决策／记录／模块参考；V2独立H.264文件编码与主机审查完成 |
| [tools/pose-v1/VPU-STARTUP-RESULTS-20261008.md](tools/pose-v1/VPU-STARTUP-RESULTS-20261008.md) | 历史决策／记录／模块参考；VPU连续内存取证与启动最小修正（2026-10-08） |
| [tools/pose-v1/WHOLE-SYSTEM-NEXT-20261008.md](tools/pose-v1/WHOLE-SYSTEM-NEXT-20261008.md) | 历史决策／记录／模块参考；完整网络窗口接入之后的门检顺序 |
| [tools/pose-v1/WINDOWS-HOST-ENV-CHECK.md](tools/pose-v1/WINDOWS-HOST-ENV-CHECK.md) | 历史决策／记录／模块参考；Windows Host工具定位与用户环境查询（2026-10-05） |

</details>
