# 真实 xlconcat IP 流水灯：已批准试验方案

日期：2026-10-01。前提与局限见 [ANALYSIS.md](ANALYSIS.md)。明确回复“同意 xlconcat 最小验证方案并执行”；按以下范围实施，实际结果另见 RESULTS.md，分析与计划本身不作为验收证据。

## 拟实施内容

1. 新建独立 ASCII 工程 `D:\FPGACompetitionProject\FPGA\lite_led_ip_bridge`。原纯 RTL 流水灯、构建脚本、批准哈希和上板证据保留。当前 Procise MCP 固定支持旧工程，本次新工程使用 **Procise 原生批处理**，不改 MCP 服务/配置。
2. 通过 Vivado MCP 创建独立 2019.1 前端工程，`xc7z030ffg676-2` 仅用于 IP 元数据生成和行为仿真。物理实现为 Procise JFMQL30TAI676H。初始化 catalog 后核对 `xilinx.com:ip:xlconcat:2.1` / Rev.3，配置 4 个 1-bit 输入，生成包装器及 simulation/synthesis 输出源码，关闭该 IP 的综合 checkpoint 生成；本试验的综合由 Procise 执行。
3. 新 RTL 仍是 25 位计数器、四位初始化 `0001` 的灯状态寄存器；把原置换表达式替换为生成的 IP 实例。输入连接为 In0=led_state[3]、In1=led_state[2]、In2=led_state[0]、In3=led_state[1]，dout 为 next_state，计数边界时装入；达到 `0001→0100→0010→1000→0001`，对应 LED1→3→2→4→1。
4. Vivado MCP 写入 RTL/testbench，通过 XSim 编译**真实 IP 包装器与综合 HDL**。自检包括 IP 组合映射的全部 16 种输入，以及分频 1/7/19 各 200 周期的初始化、步进边界、单灯及回绕。保留实际灯状态轨迹、日志和完整源码哈希。
5. 原板级约束复用：AC14/LVCMOS33、100 MHz；LED1/2/3/4 为 J1/M6/H7/J8、LVCMOS15；默认 25,000,000 周期/步、0.25 秒步长。新建工程脚本把生成的综合 HDL 作为 Procise 设计输入，执行原生综合/布局布线/时序与位流，设置 StartupClk=JtagClk。
6. 复核实际源码闭包/模块例化、IP 参数与来源哈希、仿真/构建源文件一致性、无未解析黑盒、五个 placed 引脚/电平、寄存器初始化和原生时序/位流设置。LED 的 no_output_delay 边界保持记录，时序与资源使用本次实际报告，不预设等于旧值。新脚本的新增 IP 检查不会放宽已有门禁。
7. 通过上述检查后，经 Procise 原生 JTAG 易失配置下载这份新位流；重新扫链并核对目标/哈希，不写 Flash/BOOT。请现场确认 LED1→3→2→4、约 0.25 秒/步、单灯循环后才记为实板通过。
8. 保存 IP XCI、生成脚本、完整 HDL、参数/哈希清单、XSim 日志、Procise 原始报告、位流和下载/观察证据，更新 REFERENCES、工程 README 和 Done；Done 使用两个模板小节。

## 停止条件与未确定项

- Catalog 能否创建/生成该 IP、生成包装器的实际形式、Procise 对完整生成源码的语法支持尚待实测。
- 若 catalog 仅支持不同的生成方式、输出缺综合源码、包含新原语/加密依赖、综合失败或需要补丁/数据库/安装/IP 替换，暂停依赖操作，提出证据并讨论，不能自行改用自写替身或仿真模型来称作 IP 复用成功。
- 不加载 JFM 全系统迁移 hook，不修改 EDA 数据库/安装；如需该路线，另行核对 2019.1 和 30TAI 的精确兼容条件并讨论。
- 成功结论只覆盖这个未加密组合 IP 的源码交接与流水灯实板，Concat 可能被综合优化为连线，不证明任何复杂 IP 已适配。

依据 [AGENTS.md](../../../AGENTS.md)：“根据分析结论形成的决策，必须在执行前评估并取得明确同意”。本次需要确认的是上述新 IP/独立工程/验证路线的具体实施方案；不是重复要求已经提出的上板验证。
