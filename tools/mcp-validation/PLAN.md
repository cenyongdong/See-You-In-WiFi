# Procise / Vivado MCP 验证方案（首版已批准并完成独立验证）

日期：2026-10-01。目标平台为悟净 Lite / JFMQL30TAI676H，Procise 2025.1.1 temp / SVN 32494；Vivado 辅助版本固定为 2019.1。明确答复“同意首版范围并执行”，下述 Procise 首版已实现并通过独立 stdio 验证；随后项目配置写入、日志编码适配/复验和 Vivado 启动日志捕获，均已执行。当前工具会话接入重载仍需验收。结果见 [RESULTS.md](D:/FPGACompetitionProject/tools/mcp-validation/RESULTS.md)。

## 依据与取舍

原生流水灯流程已通过，已有独立批处理构建、自检仿真、原生 JSON 时序报告、源码/位流哈希与实板证据。MCP 可以统一这些入口及作业状态，但不会降低 EDA 内部运行时间或自动补齐器件/IP 适配。首轮以结果一致性和失败状态准确性判断可行性，效率改进尚需对照测量。

建议先做独立进程作业，不采用持久 Procise Tcl 会话：前者已有实测调用依据；后者涉及提示符、输出分帧、工程切换与故障恢复，尚未验证。代价是每次构建仍需启动 Procise，首版也只支持既有流水灯工程，不能视为通用 EDA MCP。

## Procise 已批准首版范围

- 源码放在 `D:\FPGACompetitionProject\tools\procise_mcp`；独立 Python 环境放在 `.local\procise-mcp-venv`。
- 使用官方 Python MCP SDK，拟固定 `mcp==2.2.0`（本机 VivadoMcp 环境已安装此版），依赖从 PyPI 下载到独立环境；保留安装报告和实际依赖版本，不修改原有 Conda 环境、系统 PATH 或 Procise 安装。
- 本地 stdio 传输，使用 SDK 2.x 的 `MCPServer` API；本机该版已取消旧 `FastMCP` 导入，应按实际版本开发。
- 首版工具：环境/版本查询、已有原生报告查询、流水灯异步构建、作业状态、日志尾部、产物/哈希查询、最新作业复核。构建调用已验证的 `Build.ps1`，复核调用 `ReviewBuild.py`。
- 长任务先返回作业 ID，后续查询结果；区分 running/failed/completed/reviewed，缺字段不按 0 或成功处理；服务/客户端超时不能写成底层作业已取消。
- 只允许已批准的流水灯工程及其新作业目录，不提供任意 Tcl、通用命令执行、板上下载或 Flash 操作。首版不承诺作业取消、服务重启后继续管理或多并发。
- 首轮用官方 SDK 客户端实际完成 initialize→tools/list→tools/call，通过 stdio 查询并启动一次真实 Procise 构建；与同一份原始报告和位流摘要逐字段核对，检查未知作业、缺失文件和越界路径的失败结果。
- 本阶段不修改 Codex MCP 配置；通过后给出可审阅的配置，再讨论接入。协议客户端通过与当前工具会话工具实际可调用是两个独立验收状态。

## Vivado MCP 验证范围

- 使用已接入的 `vivado-mcp`，以独立会话启动指定 Vivado 2019.1，查询实际版本与 Tcl 返回/错误行为。
- 通过 MCP 调用已有 XSim 流水灯自检流程，保存新日志和源码哈希，与原生 PASS 结果对照。纯 RTL 测试不采用 Xilinx 综合或位流作为 30TAI 证据。
- 参考工程只做离线 XPR 解析，并与原始 XML 核对器件、顶层、源文件/约束/IP 数量；不打开或升级原 2018 版工程/IP。
- 已执行只读 `list_sessions` 和 `parse_xpr`；尚无 MCP 仿真通过结论。初次指定 `vivado.bat` 的 tcl 会话启动返回“Vivado 进程意外退出”，将先排查启动路径和实际 MCP 实现，不直接修改已有 MCP 配置。

更新：独立 SDK stdio 客户端已通过 Vivado 会话、版本、错误恢复及 XSim 仿真。当前工具会话的初次 Tcl 启动失败，经追加批准的日志捕获定位为误选不存在的 32 位 Vivado；再经批准仅补子进程 AMD64，当前工具会话的版本、错误恢复和 XSim 自检也已通过。修正前两个架构变量均空，和厂商启动器默认 win32 逻辑吻合。长期配置仍只准备候选，未实施。UTF-16 日志适配、新仿真联查复验和 Procise 项目配置均已完成；暂不重载，当前工具会话 Procise 调用验收保留待办，不自行重载。

## 接入依据

[OpenAI MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) 说明本地 stdio、项目级 `.codex/config.toml`、启动/工具超时及工具白名单。配置方案将在原型验证后列出具体命令、目录和工具名；当前不执行配置变更。
