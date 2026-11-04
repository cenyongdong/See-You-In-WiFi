# FPGA 工程资料入口

更新：2026-11-04。当前硬件为 `probe-free-drain-overlay-csi-v3`：PL执行CSI幅相／90点分组流水及二维骨架／关节点／动态信息绘制合成；PS保留双精度相位收尾、人物后处理与投影，人物滤波默认CPU。有限板测、30分钟官方输入长测及r4源码RAR完整本地重建已完成；后者没有上板。当前分工、资源与证据见[CSI专项](csi_preprocess/README.md)、[骨架专项](hdmi_candidate/skeleton_overlay/README.md)、[完整重建](../Deliverables/FPGA-REBUILD-20261101-r1.md)。历史几何／批量滤波扩展、心率及旧DATA／D45全面调查的独立冻结保持。

| 用途 | 入口 |
|---|---|
| RTL／C++ 书写、重构与验证规范 | [编码规范](CODING-STANDARDS.md)、[本轮重构与验证](REFACTOR-20261104.md) |
| 当前自研硬件源码与隔离构建 | [源码映射](current_sources.json)、[构建入口](../tools/release/prepare_refactored_fpga.py) |
| 当前选择、最后观察与本机恢复备份 | [恢复入口](hdmi_candidate/RESUME.md)、[默认 BOOT 身份](hdmi_candidate/default_boot.json) |
| HDL、接口、帧采纳与停止契约 | [HDMI 工程说明](hdmi_candidate/INTEGRATION.md) |
| 保留启动消费的派生硬件 | [probe_free_drain](hdmi_candidate/probe_free_drain/README.md) |
| 已有 PL 滤波的物理结果与分项测时 | [后处理与 PS／PL 比较](../software/pose180_pipeline/resident/PRESENTATION-20261026.md#pl-计算与资源) |
| 启动异常历史、事实与假设 | [故障交接](hdmi_candidate/HDMI-FAULT-HANDOFF.md)、[困难最终处置](../DIFFICULTIES.md) |
| 构建工具与适配依据 | [路线二配置](hdmi_candidate/ROUTE2-BUILD-PLAN.md)、[资料索引](../REFERENCES.md) |
| 全部硬件 Markdown | [完整文档目录](../DOCUMENTATION.md) |

[10 月 16 日总结](FPGA-WORK-SUMMARY-20261016.md)、各候选和诊断报告保留当时源码／约束／启动身份。旧“当前”“下一步”不代表现行方案，不能将任意工作副本视为合格位流来源；无设计变更不重复构建。
