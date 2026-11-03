# 项目最新进度

**2026-11-01，r4 本地完整复现：** 从当时的 r4 源码 RAR新解压，完成原生综合／链接／放置／物理优化／布线／报告／BIT及Procise适配，退出码均为0；新适配BIT配置载荷与包内合格BIT一致。setup／hold满足，既定AI周期例外和GT适配原值保留，未上板。关键数值、完整日志、位流及恢复检查点统一见[独立完整重建报告](Deliverables/FPGA-REBUILD-20261101-r1.md)。

## 最终交付

当前 [GitHub Release](https://github.com/cenyongdong/See-You-In-WiFi/releases/tag/deploy-r4-20261031) 提供 r4 部署包、r6 精简源码包及同名 SHA256 文件。r6 附 AI 辅助开发说明，构建输入沿用已完成编译、RTL 仿真和完整 FPGA 重建的 r5。[r6 源码说明](Deliverables/SOURCE-20261103.md)

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
