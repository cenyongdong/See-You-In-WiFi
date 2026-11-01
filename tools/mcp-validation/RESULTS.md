# Procise / Vivado MCP 验证记录

最新状态（2026-10-01）：已重载 Procise/Vivado MCP 并批准新灯序方案，**当前工具会话 Vivado 2019.1 直接启动、写入 LED1→3→2→4 源码并驱动 XSim，Procise 七工具完成原生构建及复核，全部通过**。最新构建 `build_20261001_183334_5f3fc1`，内部 setup/hold 5.962/0.192 ns、违例 0；随后新位流下载，Procise 原生 JTAG 完成，现场确认新灯序与速度符合预期。[完整结果](D:/FPGACompetitionProject/tools/mcp-validation/led1324/RESULTS.md)、[当前工具会话实际返回](D:/FPGACompetitionProject/tools/mcp-validation/led1324/mcp-calls.final.json)。

以下首版历史记录的日期为 2026-10-01。范围：悟净 Lite / JFMQL30TAI676H，原生实现 Procise 2025.1.1 temp / SVN 32494；Vivado 2019.1 仅作行为仿真和参考工程辅助。 Procise 首版实现、独立安装 `mcp==2.2.0`、真实 stdio 构建与复核；随后批准临时固定目录的 Vivado 启动定位，以及项目配置写入、BOM 编码适配/复验和启动日志捕获。当时执行这些批准项，没有重新下载 FPGA 或修改用户级配置/永久环境；后续长期配置修改单独记录在末节。

## 首版阶段结果（历史）

| 验证对象 | 证据与结论 |
| --- | --- |
| Procise MCP 独立协议客户端 | initialize → tools/list → tools/call 通过，七工具均实际调用；[协议记录](D:/FPGACompetitionProject/tools/mcp-validation/procise-stdio-validation.json) |
| 实际 Procise 环境 | 固定无害探测启动原生程序，返回 2025.1.1 temp / SVN 32494；不是只根据安装路径认定版本 |
| 异步构建 | 新作业约 0.016 秒返回 ID；完整测试约 47 秒，包括轮询、协议调用、复核和错误用例；不是 EDA 加速结论 |
| 最新新构建复核 | `build_20261001_170101_78f11a`：内部 setup/hold 4.740/0.170 ns、违例端点 0；五个引脚、电平、29 INIT、源码/MCP 新仿真哈希和 JtagClk 设置通过；[复核](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_170101_78f11a/build-review.json) |
| 解析一致性 | 返回的时序、时钟、检查计数逐项等于同一原生 JSON；六项产物大小/哈希逐项等于磁盘文件 |
| 错误与范围控制 | 未知/非法 job、缺目录、越界目录、重复活动构建、非法日志行数和越界仿真路径均 `isError=true`；另有五项失败导向报告门禁测试通过 |
| Vivado 参考工程辅助 | 当前工具会话的 `parse_xpr` 成功；原始 XML 独立核对：part `xc7z030ffg676-2`、top `ai7030_edif_top`、设计文件 91、XDC 2、IP/BD 14、仿真文件 0、run 2；[独立核对](D:/FPGACompetitionProject/tools/mcp-validation/independent-evidence-checks.json) |
| Vivado MCP 独立 stdio 客户端 | 未改安装的 `vivado-mcp 0.3.26` / MCP SDK 2.2.0：指定 2019.1 会话成功；Tcl 错误返回后可继续查询；经 `run_tcl exec` 调用既有 `Simulate.ps1`，新 XSim 自检通过；[协议记录](D:/FPGACompetitionProject/tools/mcp-validation/vivado-stdio-validation.json) |
| 当前工具会话 Vivado 进程 | 的临时 AMD64 子进程修正后，当前工具会话 `start_session/run_tcl/stop_session`、版本查询、错误恢复和 XSim 自检均通过；[当前工具会话协议返回及独立核对](D:/FPGACompetitionProject/tools/mcp-validation/vivado-live-validation.json)。未实施长期修复 |
| 当前工具会话 Procise 接入 | 批准的项目配置已写入，Codex CLI 已正确读取七工具；配置采用暂不重载，当前工具会话工具发现/调用仍待验收，不自行重载 |

本次 Procise 新位流 5,980,582 字节，SHA-256 `c352c0a2e6369646ae12f340db908f594bcaac1d66460efdc3ca38f1f116827c`，未下载。原已上板位流哈希仍为 `a443d8f4bfde85eedc9de0e0328680cbb5d06c364f1113c55b14c4c6f4475eec`，原观察证据不变。跨次位流哈希不同没有用于判定失败或二进制可复现；各自复核摘要与各自文件一致。

## 发现的问题

1. **报告默认值标记。** 首轮原生构建成功，适配层却把 BGN 的 `Disallow*` 当成不同配置而误报 failed。星号为默认值标记，修正比较并保留原值后复验通过。[首轮记录](D:/FPGACompetitionProject/tools/mcp-validation/procise-stdio-attempt1.json) 保留此失败；不能仅因 MCP 接通而推定解析准确。
2. **Vivado 错误通道。** 已安装工具将 `[ERROR] ...` 放在正文，但 MCP `isError=false`；独立测试中的 Tcl 错误也如此。后续检查必须同时看正文、Tcl rc 和预期完成标记，不能仅凭外层成功状态继续。当前没有修改第三方工具。
3. **启动诊断不足与实际原因。** 最初当前工具会话服务仅返回空 stderr，安装代码在 stdout EOF 时丢弃已收集的启动 stdout。ASCII 工作目录未解决、有无控制台原生探测均通过，因此不能认定这些是原因。追加批准的启动捕获显示误选 win32；临时验证记录修正前 `PROCESSOR_ARCHITECTURE` 和 `PROCESSOR_ARCHITEW6432` 均空，补 AMD64 后当前工具会话实际启动和仿真通过，和厂商 `loader.bat` 默认 32 位选择逻辑吻合。为什么上层环境未提供变量尚未调查，不把这一层因果推定为 Windows/Vivado 版本不兼容。[原始变量](D:/FPGACompetitionProject/tools/mcp-validation/vivado-architecture-before.txt)。
4. **PowerShell 日志编码。** SDK MCP 调用 Windows PowerShell 5.1 执行新仿真，日志为 UTF-16 BOM。首次 Procise 复核使用原 UTF-8 仿真。随后增加 `ReviewBuild.py` 的 BOM 识别并更新批准脚本哈希，UTF-8/BOM 与 UTF-16 LE/BE BOM 的 PASS/ERROR 保留验证通过；以此次 MCP 新仿真做新构建和完整复核也通过，没有回写原来已上板的复核记录。

独立 SDK 新仿真目录为 [sim_20261001_165013_4e2b85](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/sim_20261001_165013_4e2b85/simulate.stdout.log)，已用于最新 Procise stdio 完整复核。当前工具会话临时修正后的新仿真为 [sim_20261001_170754_15228a](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/sim_20261001_170754_15228a/simulate.stdout.log)，独立解码确认 PASS、1996 ns 结束、RTL/TB 与源文件一致，RTL 也等于已复核 Procise 构建。两者均三种分频参数 1/7/19 各检查 200 周期。经 MCP 调用的是现有 XSim 脚本，未验收 `launch_simulation` 工程模式、GUI 波形或厂商网表仿真。

XPR 输出的 `7.39` 是工程 XML 格式版本，不能当作 Vivado 程序版本。仿真文件 0 是显式 sim fileset 无文件，不证明工程没有可继承的设计源；宏路径展开也不证明引用文件全部存在。参考工程没有打开、升级、实现或采用其 Xilinx IP。

## 首版阶段追加批准与状态（历史）

- [Procise 项目配置](D:/FPGACompetitionProject/.codex/config.toml) 已获明确批准并写入，只有 `procise_lite` 条目；[Codex CLI 解析证据](D:/FPGACompetitionProject/tools/mcp-validation/procise-codex-config-resolved.json) 与候选一致。用户级配置前后 SHA-256 均为 `b4d61b272737243419bc9bc2ef11752ea0c0eacbb9ef18336c0d16f5f5205d1c`。当前工具会话没有自动重载接口；明确回复“暂不重载”，实际调用待后续验收，不再次要求或自行重载。
- 编码修改已获批准并执行，最新版批准脚本 SHA-256 为 `1ab7b1c9e7d943bb364451a5763132d5abf205e2265076379cb6e08b2c3a7806`。[编码与配置验证](D:/FPGACompetitionProject/tools/mcp-validation/encoding-and-config-verification.json)。最新完整 stdio 通过作业为 [build_20261001_170101_78f11a](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_170101_78f11a/build-review.json)，使用上述新 MCP 仿真；位流 SHA-256 `7e611a61f00c1c6b1cd847818be06f3c95c02a34f0dea747a0be404cb0ce1686`，5,980,582 字节，未下载。首次成功结果另存为 [stage1 PASS](D:/FPGACompetitionProject/tools/mcp-validation/procise-stdio-stage1-pass.json)。
- [启动捕获](D:/FPGACompetitionProject/tools/mcp-validation/Vivado-Capture.cmd) 已获批准并执行，固定 Tcl 刻意退出不计为成功会话。实际 [stdout](D:/FPGACompetitionProject/tools/mcp-validation/vivado-from-codex.stdout.log) 显示 `Could not find 32-bit executable`，尝试不存在的 `bin/unwrapped/win32.o/vivado.exe`，stderr 空。厂商 `loader.bat` 第 31–40 行依据 PROCESSOR_ARCHITECTURE/PROCESSOR_ARCHITEW6432 判定位数，`rdiArgs.bat` 默认据此选 win32/win64。直接失败原因已定位为错误选择 32 位；当前服务到底继承了缺失还是 x86 变量仍待临时验证，不自行认定。
- [仅子进程 AMD64 验证](D:/FPGACompetitionProject/tools/mcp-validation/Vivado-AMD64-Test.cmd) 已获明确批准并执行。当前工具会话实际启动、`version -short`、预期 Tcl 错误后恢复、经现有脚本执行的 XSim 均通过，已关闭本次测试会话；另一个监听 9999 的 GUI 进程未操作，stdio 仿真不依赖该端口。两个原始架构变量均空，补 AMD64 后通过；未修改永久环境、EDA 或生效 Vivado MCP 配置。
- 长期修复随后获实施，已在现有 `[mcp_servers.vivado.env]` 增加 `PROCESSOR_ARCHITECTURE='AMD64'`；其余字段和原始字节保持不变。已从实际 Codex 解析配置启动新 MCP 服务验证通过，无临时启动器；现有聊天服务尚未重启。详见下节，不将临时测试授权视为其他持久配置变更授权。

这些操作均按 [AGENTS.md](D:/FPGACompetitionProject/AGENTS.md) 决策审批规则逐项讨论；未批准的长期配置修正不据临时测试授权执行。没有受控样本支持“MCP 比脚本更快或准确率更高”。实现收益目前是入口统一、可查询任务状态、固定范围及证据整合，成本是 SDK/适配层维护和服务故障处理。

## 长期配置实施与验证（2026-10-01）

本轮设计要求实施长期配置，仅修改 `C:\Users\cenyongdong\.codex\config.toml` 中 Vivado MCP 的 `env.PROCESSOR_ARCHITECTURE` 为 `AMD64`，原其他配置保留。修改前备份留在配置同目录；[修改范围与哈希](D:/FPGACompetitionProject/tools/mcp-validation/vivado-permanent-config-change.json) 证明只有此键增加、其余原始字节不变。首轮的“用户级配置未改”和对应历史哈希不再描述此后当前配置。

[验证脚本](D:/FPGACompetitionProject/tools/mcp-validation/validate_vivado_permanent_config.py) 读取 Codex CLI 实际解析的 Vivado 配置，测试父进程中临时移除两个架构变量，以此配置启动新 stdio MCP 进程；不使用临时 Vivado 包装器，也不覆盖 `start_session` 的 Vivado 路径。Vivado 2019.1 启动和 `AMD64` 回读通过，测试会话已关闭。[实际协议记录](D:/FPGACompetitionProject/tools/mcp-validation/vivado-permanent-config-validation.json)。本次未重复 XSim/综合/上板验证。

已有聊天服务进程的环境不会因文件写入立即改变，配置写入时尚未重启该进程；当时 Procise 的“暂不重载”选择也未改变。随后自行重载两个服务，顶部链接的新灯序任务已经直接验证当前工具会话入口、XSim 和 Procise 原生位流复核，无临时启动器。
