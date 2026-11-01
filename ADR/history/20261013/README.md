# 2026-10-13 文档迁存索引

本目录承接原AGENTS.md中的实施过程/阶段结果及整理前的进度、难点快照。**只作历史证据，不是现行指令或新的执行授权。** 原文中的“当前”“已批准”“下一步”按原日期理解；当前状态以[PROJECT-PROGRESS](../../../PROJECT-PROGRESS.md)为准，执行规范以[AGENTS.md](../../../AGENTS.md)为准。

## 主题与位置

| 文件 | 内容 | Agents原记录数 |
|---|---|---:|
| [demo.md](demo.md) | 端到端演示/重启历史/整合验收；对应ADR_45 | 3 |
| [read-diagnostics.md](read-diagnostics.md) | 首次坏读、SDK搬运、生产者/租约/目录取证；对应ADR_17–44 | 33 |
| [video-lifecycle.md](video-lifecycle.md) | VPU、真实画面、常驻/阶段顺序/整机计量；对应ADR_02、07–16、27–31 | 28 |
| [mixed-inference.md](mixed-inference.md) | 正式图接入、融合追溯、帧计数和分阶段验收；对应ADR_00、01、05 | 43 |
| [cpu-sdk.md](cpu-sdk.md) | CPU注册、布局适配、Host路径与初期SDK/板端核验；对应ADR_03–05 | 31 |
| [training.md](training.md) | 26版迁移/全新/零衰减实验及定时检查历史；对应ADR_04 | 9 |
| [platform-tools.md](platform-tools.md) | SD/FPGA/IP/MCP/环境阶段历史；对应ADR_03 | 14 |

另存[toolchain-runbook](toolchain-runbook.md)保存原工具路径/调用示例，标明原核对日期，不将历史占位路径当当前配置。三个历史全文快照：[progress-before](progress-before.md)、[difficulties-before](difficulties-before.md)、[adr-index-before](adr-index-before.md)；相对链接按新位置调整，历史结论未改写。

## 完整性与有效规范

- 迁出161项历史记录（含异常读取规范所附当时接续方案）；19项规范来源提炼到现行Agents，原工具资料整体迁存。
- [migration-map.json](migration-map.json)逐项记录原行范围、原块SHA256及去向；A行号锚点对应整理前Agents文件，避免依赖整理后的行号。
- 原Agents/进度/难点/ADR索引逐字节备份保存在本机已忽略的.local/document-reorganization-20261013，身份见[validation.json](validation.json)。原连接IP/账号放到进度配置入口，原凭据不在公共历史副本中重复传播。
- 新文档职责在[ADR_46](../../ADR_46.md)；旧ADR_00–45与原始源码/证据/完成清单不覆盖，历史报告内的原文档哈希仍对应当时版本，不能要求其匹配今天已整理的文件。
- 本轮仅文档整理，无构建、安装、连接、板测或新增验收；DATA排查暂停和一次重启许可已用完的约束保持。
