# LED1→3→2→4：Vivado / Procise MCP 衔接验证方案

日期：2026-10-01。明确回复“同意该方案并执行”，已按以下范围实施并通过验收；结果见 [RESULTS.md](D:/FPGACompetitionProject/tools/mcp-validation/led1324/RESULTS.md)。

## 已检查的服务

当前工具会话已发现并调用 Procise MCP `get_environment`，原生探测通过，实际版本为 2025.1.1 temp / SVN 32494。Vivado MCP 直接按长期配置启动独立 Tcl 会话 `lite_led1324_pipeline`，实际 2019.1、AMD64，通过；没有临时启动器。原有外部 GUI 不操作。

## 建议实施范围

现有 Procise MCP 固定支持 `D:\FPGACompetitionProject\FPGA\lite_led_chaser`，不接受其他工程路径。建议复用该工程，先把旧 RTL/testbench 保存到 `revisions\led_1234_before_1324`，保留全部原仿真、构建、复核和上板记录。新增独立工程则需另行讨论 MCP 服务适配/重载，不纳入当前建议。

- 功能：LED1→LED3→LED2→LED4→LED1，单灯循环。默认 100 MHz / 25,000,000 周期，每步 0.25 秒，一圈 1 秒。
- RTL 初始 `0001`，循环连接改为 `led_state <= {led_state[1], led_state[0], led_state[2], led_state[3]};`，对应 `0001→0100→0010→1000→0001`。保持 25 位计数器及四个灯状态寄存器，不引入厂商 IP。
- testbench 按四个明确预期值独立查表，分频 1/7/19 各检查 200 周期；覆盖初始化、每步边界、单灯及回绕，打印实际前八步灯状态。
- 已验证硬件/FDC 不变：时钟 AC14/LVCMOS33；LED1/2/3/4 引脚 J1/M6/H7/J8、LVCMOS15；10 ns 时钟。原理图依据 REFERENCES B4。
- 由当前工具会话 Vivado MCP 的 Tcl 文件操作写入批准 RTL/testbench，调用既有 XSim 2019.1 脚本进行行为仿真。不是 Xilinx 综合或位流移植，也不创建带虚构 Xilinx 目标器件的工程。
- 仿真通过后调用当前工具会话 Procise MCP `start_led_build/get_job_status/read_build_report/list_artifacts/review_led_build`，完成原生综合、布局布线、内部时序、JtagClk 位流和 INIT/引脚/哈希复核。原构建及复核脚本、MCP 代码/配置不改，不需要再次重载。
- 本次验收截至位流生成和复核，不自动扩展为 JTAG/Flash 或肉眼功能验收。

## 证据及结果

保存本次真实 MCP 调用、仿真/构建目录、源文件与位流 SHA-256、时序与引脚/INIT 复核，并更新工程 README、AGENTS.md、REFERENCES.md、Done.md。四 LED 无外部输出延迟的边界继续明确记录；时序数据以本次 Procise 原始报告为准，不预设等于旧值。

此方案依据 AGENTS.md“根据分析结论形成的决策，必须在执行前评估并取得明确同意”提交确认；取得上述明确同意后才备份、修改工作源码并启动新构建。原构建/仿真/复核脚本、MCP 服务及配置未修改；本次未下载上板。
