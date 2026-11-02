# Procise Lite MCP 首版

2026-10-01 此首版的代码、独立环境安装和 stdio 验证。目标为悟净 Lite / JFMQL30TAI676H；首版仅封装已验证的流水灯工程，使用 Procise 2025.1.1 temp / SVN 32494 原生实现。本目录不是通用 Procise Tcl 会话服务。

## 启动与验证

独立环境：`D:\FPGACompetitionProject\.local\procise-mcp-venv`，Python 3.12.14，官方 SDK `mcp==2.2.0`。安装来源/依赖详见 [安装报告](../mcp-validation/procise-sdk-install.json)、[锁定清单](requirements.lock.txt)。未修改 Conda、Procise 安装或永久 PATH。

```powershell
# stdio 服务：stdout 为 MCP 协议，不直接向其输入 Tcl。
& 'D:\FPGACompetitionProject\.local\procise-mcp-venv\Scripts\python.exe' `
  'D:\FPGACompetitionProject\tools\procise_mcp\server.py'
```

以下是复验入口。集成测试会实际新建一次流水灯构建，须在已授权的验证任务中执行：

```powershell
& 'D:\FPGACompetitionProject\.local\procise-mcp-venv\Scripts\python.exe' `
  'D:\FPGACompetitionProject\tools\procise_mcp\test_report_gates.py'
& 'D:\FPGACompetitionProject\.local\procise-mcp-venv\Scripts\python.exe' `
  'D:\FPGACompetitionProject\tools\procise_mcp\validate_stdio.py'
```

## 七个工具

| 工具 | 内容与边界 |
| --- | --- |
| `get_environment` | 运行固定 Tcl 探测，返回实际 Procise 横幅、Python/SDK 路径和日志；写诊断文件 |
| `read_build_report(build_dir)` | 读取流水灯 `runs\build_*` 原生 JSON、placed FDC、BGN、位流摘要；此查询不等于完整复核 |
| `start_led_build()` | 调用固定 `Build.ps1`，立即返回 job ID；一实例只允许一个活动构建；不下载 |
| `get_job_status(job_id)` | running / failed / native_completed / reviewed；结合退出码、完成标记、源码哈希和报告，保存状态证据 |
| `tail_job_log(job_id, lines)` | 返回有大小上限的启动器/原生日志尾部；最多 200 行 |
| `list_artifacts(job_id)` | 列出已知产物的绝对路径、大小和 SHA-256；运行中结果标记 provisional |
| `review_led_build(job_id, sim_dir)` | 只复核本服务实例新建并成功完成的作业，调用原 `ReviewBuild.py`，核对仿真/源码/引脚/INIT/位流设置 |

路径先 resolve，拒绝越出既定 runs 目录的路径及链接；不提供任意 Tcl、任意命令、通用文件读取、JTAG 或 Flash 工具。执行脚本以 [批准脚本哈希](approved-scripts.json) 固定，脚本变化即拒绝执行，须先审阅并讨论。该限制是工具范围控制，不是针对本机恶意代码的安全隔离。

查询工具若刷新本地状态文件，MCP 注解明确标记为写操作。stdout 仅承载协议；原生程序及复核输出写独立日志，SDK 错误写 stderr。预期非法调用会在 stderr 留有异常记录，不能把整份服务 stderr 非空直接解释为构建失败，应结合对应工具的 `isError` 和原生日志。

## 实测结果

最新当前工具会话验收（2026-10-01）：已重载两个 MCP 服务，七个 Procise 工具均实际调用通过。当前源码改为 LED1→3→2→4；Vivado MCP 写入源码并驱动 XSim 后，Procise MCP 作业 `5c5f8f383cd74afa87915adc67921a80` 构建并复核同一 RTL，状态 reviewed。[完整结果](../mcp-validation/led1324/RESULTS.md)。最新 [build-review.json](../../FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/build-review.json) 内部 setup/hold 5.962/0.192 ns、违例 0；位流 SHA-256 `285356540f63f5b1a150827777f8e5e411843718976590db0cb39739b5ef7c18`，随后用 Procise 原生脚本下载并通过现场确认；该下载不属于 MCP 工具能力。下列独立 stdio 结果属于此前旧灯序阶段，证据保留。

[真实 stdio 验证记录](../mcp-validation/procise-stdio-validation.json) 包括 initialize、tools/list、tools/call、调用时长和原始返回。构建入口约 0.016 秒返回，完整协议/构建/复核验证约 47 秒，含轮询和错误用例；这不是与原生流程做受控性能对照的结果。

成功作业目录：[build_20261001_164532_c8ce42](../../FPGA/lite_led_chaser/runs/build_20261001_164532_c8ce42/build-review.json)。内部 setup/hold 裕量 4.740/0.170 ns，违例端点均为 0；五个引脚及电平、29 个寄存器 INIT、仿真与当前 RTL 哈希通过。StartupClk=JtagClk，BGN 默认值尾部 `*` 保留在原值字段、比较时去除。四颗 LED 的无输出延迟项仍明确列出，不能推导为所有接口时序通过。

位流 5,980,582 字节，SHA-256 `c352c0a2e6369646ae12f340db908f594bcaac1d66460efdc3ca38f1f116827c`。本次新位流没有下载上板；原来已上板并通过观察的位流证据不变。跨构建的位流哈希不要求相等：本次检查的是各自实际文件与其复核记录一致，不把重复构建当成位流二进制可复现性测试。

未知/非法作业 ID、不存在目录、越界目录、重复活动构建、非法日志行数和越界仿真目录均返回 MCP `isError=true`。五项报告门禁测试证明缺字段、遗漏检查类别、摘要与违例矛盾、未知未约束输出、非有限时序值不会被当成通过。

首个真实构建本身成功，但适配层把 `Disallow*` 与 `Disallow` 直接比较而误报失败；已修正并重测。保留 [首轮记录](../mcp-validation/procise-stdio-attempt1.json) 和新结果，说明报告适配仍需针对版本验证，MCP 接入本身不保证准确率。

## 接入候选与限制

[候选配置](codex-config.candidate.toml) 已写入 [项目配置](../../.codex/config.toml)。使用绝对 Python/服务路径、项目工作目录、七工具白名单和 20/60 秒启动/调用超时；Codex CLI `mcp get procise_lite --json` 已正确读取，见 [解析证据](../mcp-validation/procise-codex-config-resolved.json)。该写入当时原用户级配置哈希未变化。随后重载服务，当前工具会话七工具及新灯序的构建/复核已通过，见上方最新记录；SDK stdio 和 CLI 读取与实际聊天调用分别保留证据。项目配置仅在受信任项目加载，依据 [OpenAI MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。

另已批准 `ReviewBuild.py` 增加 UTF-8/UTF-16 BOM 日志识别和对应批准脚本哈希更新，时序、引脚、INIT 等门禁未修改。UTF-8、UTF-8 BOM、UTF-16 LE/BE BOM 的 PASS/ERROR 文本保留验证通过；随后以 MCP 新仿真 `sim_20261001_165013_4e2b85` 做真实 stdio 联查复验通过。[最新复核](../../FPGA/lite_led_chaser/runs/build_20261001_170101_78f11a/build-review.json) 的位流 SHA-256 为 `7e611a61f00c1c6b1cd847818be06f3c95c02a34f0dea747a0be404cb0ce1686`，仍未下载。完整最新调用记录仍为 `procise-stdio-validation.json`；之前的成功记录保留为 [首阶段 PASS](../mcp-validation/procise-stdio-stage1-pass.json)。

服务/客户端超时不等于取消底层构建。首版不含取消，也不支持服务重启后恢复管理作业；运行中关闭服务可能留下原生任务，因此应保持服务至作业终止并核对日志。旧实例的 job ID 在新实例返回 Unknown，不通过 PID 存在猜测完成状态。此版也未验证多客户端并发、断电恢复、故障注入到 Procise 进程、其他工程、PS/AI/IP 或板上下载。
