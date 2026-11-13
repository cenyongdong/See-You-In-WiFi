# 项目最新进度

<<<<<<< HEAD
**2026-11-06，核心源码本地重构：** 主入口、CSI 接口、控制脚本和 PC 页面按职责整理，编码规范与打包依赖同步；新旧离线回归、数值对照及隔离候选的原生／ARM64 构建通过。硬件输入未变，复用原实现证据；未发布、部署或板测。[范围与验证记录](software/pose180_pipeline/REFACTOR-20261106.md)

**2026-11-04，r7 独立完整重建：** 从 GitHub 发布包重新下载并解压，完整综合至 BIT／Procise、BOOT 封装及应用重编译完成，工程 log、时序报告和恢复检查点已保留；追加有限上板验证完成，853 次新推理／HDMI 采纳，实屏确认正常，人工停止后安全回退原 BOOT。[验证记录与产物](Deliverables/R7-REBUILD-BOARD-20261104.md)

**2026-11-04，工作源码重构：** 当前自研 RTL 与 FPGA 目录 28 个 C++ 文件完成可读性维护，编码规范及显式构建映射已落地；离线数值／周期对照、双架构编译和完整 FPGA 实现／BIT／Procise 已完成。该重构阶段未上板，随后 r7 独立重建的板测结果见上方；已发布包与默认 BOOT 不变；结果与原始例外见[重构记录](FPGA/REFACTOR-20261104.md)。

**2026-11-01，r4 本地完整复现：** 从当时的 r4 源码 RAR新解压，完成原生综合／链接／放置／物理优化／布线／报告／BIT及Procise适配，退出码均为0；新适配BIT配置载荷与包内合格BIT一致。setup／hold满足，既定AI周期例外和GT适配原值保留，未上板。关键数值、完整日志、位流及恢复检查点统一见[独立完整重建报告](Deliverables/FPGA-REBUILD-20261101-r1.md)。
=======
**2026-11-13，旧 100-query TopK 融合独立实验：** PL 通用外设、原生布局适配及完整模型联合仿真已通过；ZG330 排名候选新增 7 组实板首次输出逐位通过，真实 DDR 搬运和直接端口绑定通过。实际 1 次 SDK／7 次 forward，正常退出、分配归零、设备空闲，BOOT 写入和重启均为 0。尚缺 PL 的 SoC 接入、整机实现与整图实板性能；D2a 融合二进制和详细 SDK 状态解码限制仍保留，不改变交付模型和 BOOT。实现、证据和恢复入口见 [TopK／Gather 实验](FPGA/topk_gather/README.md)。

**2026-11-01，本地完整复现完成：** 从最新r4源码RAR新解压，完成原生综合／链接／放置／物理优化／布线／报告／BIT及Procise适配，退出码均为0；新适配BIT配置载荷与包内合格BIT一致。setup／hold满足，既定AI周期例外和GT适配原值保留，未上板。关键数值、完整日志、位流及恢复检查点统一见[独立完整重建报告](Deliverables/FPGA-REBUILD-20261101-r1.md)。
>>>>>>> hardops

## 最终交付

当前 [GitHub Release](https://github.com/cenyongdong/See-You-In-WiFi/releases/tag/deploy-r4-20261031) 推荐 r4 部署包与 r7 重构源码包，保留 r6 源码附件。r7 已完成独立解压软件／RTL 验证，并进一步完成独立完整 FPGA 重建；部署包未更新。[r7 源码说明](Deliverables/SOURCE-20261104.md)

2026-11-01部署补充：r4部署说明补齐实时四机接线／首次安装／启停与定位，配套RAR加入已验证路由器安装文件，只附最新版BOOT；升级前保留设备实际BOOT读回保护。主程序、模型、数据与最新版BOOT不变，没有新板测；当时的 r4 源码包身份见历史重建报告。

**2026-10-31，r4交付补齐：** 当前实现为 PL CSI 分组预处理＋PL 二维骨架／关节点／动态信息合成，PS 保留双精度相位收尾、后处理、人物滤波及坐标投影，NPU 使用原 epoch99／180-query 模型。TopK=3、严格 score >0.2；PC 保留滤波前／后双页和共享板端计时。

[部署说明](Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)和[性能及证据汇总](Deliverables/PERFORMANCE.md)记录当前演示范围。

CMake默认启用PL CSI／骨架绘图及依赖，预设和打包配置已同步；实际ARM64编译程序与已验证版本一致。r3已从RAR独立解压后完成ARM64／离线编译和核心RTL仿真，ARM64程序与已部署版本逐字节相同；10月31日r4追加厂商IP、网表和增量基线，完成局部依赖验证（首次属性断言失败保留）；11月1日新增完整布局布线复现，见上方独立报告，两轮均未连接板端或启动SDK测试。最近板端核验目录仍是 `/root/pose180-csi-release-20261031-r1`；默认BOOT此前读回与CSI v3一致，当前恢复与安全启停见 [RESUME](FPGA/hdmi_candidate/RESUME.md)，该状态是历史观察快照。

420窗基准已证明CSI完整延迟5.647→4.043 ms，CPU时间5.629→3.973 ms；仍有有限相位差及边界回退，不宣称数学逐位无损。30段官方train输入、8700不同窗口循环，1800.004秒内完成25396次新推理和HDMI采纳；现场确认开始及末段PC／HDMI持续更新。少量发送丢弃、最长2.287秒结果间隔及一次PC人工重启均保留。骨架绘图减少CPU负担和动态传输量，不宣称实测显示采纳延迟降低。完整数值、资源、范围统一见性能汇总。

尚未验收：任意实时环境精度、无限期无人值守、旧D45根治及运行中PL_KEY1恢复；本轮没有补做实时CSI测试。历史几何／滤波扩展、心率和旧DATA全面调查的独立冻结继续保持。项目difficulty“已解决（工程收口）”不改变失败原值。

## 项目演进

| 阶段 | 主要进展与转折 | 追溯入口 |
|---|---|---|
| 9 月底～10 月初 | 核对 Lite、Procise／JFM、Icraft 与资料；解决启动介质和开发环境问题 | [资料记录](REFERENCES.md)、[困难记录](DIFFICULTIES.md) |
| 10 月 4～13 日 | 对齐 CSI 数学、补齐 ARM Host 算子／融合契约；跑通早期混合推理与 VPU／RTSP；旧 DATA 异常取证后暂停全面根因调查 | [历史成果](Done.md)、[ADR 索引](ADR/README.md) |
| 10 月 14～24 日 | HDMI 接入与时序收敛；多轮启动异常隔离、波形与协议取证；采用保留单次主动消费的缓解路径；180-query 原 epoch99 成为主图 | [HDMI 工程](FPGA/hdmi_candidate/INTEGRATION.md)、[模型部署](tools/pose180/deploy/RESULTS.md) |
| 10 月 25～27 日 | 按 ADR_50 改为有界常驻、PC／记录解耦；打通真实 CSI、局部恢复和独立显示；完成六片段双输出，发布默认 BOOT 与七色条 | [常驻记录](software/pose180_pipeline/resident/README.md)、[数据集阶段](software/pose180_pipeline/resident/DATASET-DEMO.md) |
| 10 月 28 日 | 加固单人显示及资源生命周期；比较自采模型后恢复原 epoch99；长测启动有证据，但没有长期验收结论 | [模型对比](software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md)、[启动与安全历史](software/pose180_pipeline/resident/STARTUP-PACKAGE.md) |
| 10 月 29 日 | 核心目录整理、最终审查、FD 竞态修正、双输入与三片段部署、PC 连接修正；完成板端及本地清理 | [最终审查](software/pose180_pipeline/resident/FINAL-REVIEW.md)、收尾原始记录（本机留存，仓库未附：`.local/project-cleanup-20261029-r1/summary.json`） |

所有 difficulty 的项目跟踪状态统一为“已解决（工程收口）”，逐项处置和仍存在的技术限制见 [DIFFICULTIES.md](DIFFICULTIES.md)。该状态不改变历史失败或未验收结论。后续可选验证和冻结项统一见[后续验证与冻结范围](DIFFICULTIES.md#后续验证与冻结范围)，文档的现行／历史属性及撤下页面的去向见[文档目录](DOCUMENTATION.md)。
