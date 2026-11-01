# 真实 xlconcat IP → Procise → Lite 实板验证结果

日期：2026-10-01。 [PLAN.md](D:/FPGACompetitionProject/tools/mcp-validation/ip-reuse/PLAN.md)，并在下载后确认“灯序、速度和单灯状态均符合预期”。本次全流程功能验收通过。

## 结论与实际范围

**Vivado MCP 生成真实 xlconcat IP、写入 RTL/testbench、驱动 XSim → 同一份综合 HDL 交给 Procise 原生综合/布局布线/位流 → Procise 原生 JTAG → 实板观察，已通过。** 验证对象是 Vivado 2019.1 的 `xilinx.com:ip:xlconcat:2.1` / Rev.3，四个 1-bit 输入、4-bit 输出。目标始终是悟净 Lite / `JFMQL30TAI676H`；`xc7z030ffg676-2` 仅用于前端 IP 元数据生成与仿真。

这证明了这个未加密、无器件原语依赖的简单组合 IP 源码可以交接。成功范围不包括其他 IP/配置、加密源码、FIFO/BRAM/Clocking/DSP、DMA、HDMI 或 AXI 系统。MCP 是操作入口，未承担 IP 语义转换。当前 Procise MCP 固定旧流水灯工程，本次新工程后端及下载均使用 **Procise 原生批处理**，不能记作新工程的 Procise MCP 构建/JTAG 已验证。

## 工程与源码

工程：[FPGA/lite_led_ip_bridge](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/README.md)。原 `lite_led_chaser` 工程的 RTL/testbench/FDC 哈希经独立核对保持不变，旧构建及上板记录保留。MCP 配置、EDA 安装、器件数据库和 JFM hook 未修改。

流水灯保留 25 位计数器和初始化 `0001` 的四位状态寄存器，默认 100 MHz、25,000,000 周期/步、0.25 秒。真实 IP 输入为 In0=state[3]、In1=state[2]、In2=state[0]、In3=state[1]，dout 作为下一状态，达到 LED1→3→2→4→1。

| 实际综合源码 | 来源与 SHA-256 |
| --- | --- |
| [lite_led_chaser.v](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/rtl/lite_led_chaser.v) | 当前工具会话 Vivado MCP 写入；`bab90edfe091ad2278414f7d76b9df1530d50d7d8e8ff3ba3007975d781848ac` |
| [synth/led_state_concat.v](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/ip/led_state_concat/synth/led_state_concat.v) | Vivado 2019.1 实际生成的综合包装器，例化厂商模块并固定参数；`f24914b76fa7fb6efaec1d20fa2273f10199a4aa3253f44232f3bc764462b33b` |
| [xlconcat_v2_1_vl_rfs.v](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/ip/led_state_concat/hdl/xlconcat_v2_1_vl_rfs.v) | 生成产品中的厂商实现 HDL，与安装库逐字节一致；`bf101401b966e7c7121bd17b0099f468f8e5fb15a376ac2e747885cdafd86689` |

三个模块形成已审核的源码闭包：`lite_led_chaser → led_state_concat → xlconcat_v2_1_3_xlconcat`。没有使用自写 IP 替身、stub、funcsim、DCP 或其他预综合 IP 网表。XSim 与 Procise 都编译 **synth 包装器及同一份厂商 HDL**；生成目录中的独立 sim 包装器未作为本次交接输入。完整清单、XCI 参数及哈希见 [source-manifest.json](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/source-manifest.json)。

实际会话回读 Vivado 2019.1 / AMD64，IP revision=3、NUM_PORTS=4、dout_width=4、checkpoint=0；`synth_1` 和 `impl_1` 均为 `Not started`，本次没有在 Vivado 执行综合或实现。前端会话已关闭，外部 GUI 会话未操作。[实际 MCP 返回](D:/FPGACompetitionProject/tools/mcp-validation/ip-reuse/mcp-evidence.json)。

## 验证结果

| 环节 | 本次实际证据 |
| --- | --- |
| IP 生成 | `create_ip`、参数配置、simulation/synthesis/instantiation_template 输出生成成功；保留 [XCI](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/ip/led_state_concat/led_state_concat.xci) 和 [复现脚本](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/scripts/generate-ip.tcl) |
| XSim | MCP `run_tcl exec` 驱动新 `Simulate.ps1`；全部 16 种 IP 输入以独立真值表核验；分频 1/7/19 各检查 200 周期，覆盖 INIT、步进边界、单灯和回绕；1996 ns 正常结束，两个 PASS 均存在；[原始仿真日志](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/sim_20261001_193106_688cd5/simulate.stdout.log) |
| Procise 原生实现 | 2025.1.1 temp / SVN 32494；原生解析三份 Verilog，再 synthesize、place、route、bitgen；退出码 0，stderr 空；[构建日志](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/procise.stdout.log) |
| 时序与资源 | setup/hold 裕量 5.962/0.192 ns，各 58 端点，违例 0；LC 11/19650，GCDU 1/32；无缺失时钟、未约束内部端点或组合环；四 LED 的 `no_output_delay` 仍保留；[route 原生报告](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/rundir/lite_led_chaser_route.json) |
| 源码与位流门禁 | 当前/仿真/构建三份 HDL、XCI 和清单哈希一致；EDIF 单元引用均有定义，无遗留 xlconcat 黑盒；五引脚/电平、25 个计数器 INIT=0、LED INIT=0001、器件、JtagClk、UnconstrainedPins=Disallow 均通过；[复核记录](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/build-review.json) |
| 下载 | 19:34（北京时间），重新确认 `usb-jtag-hs1` / `210512180081`、jfmql30 part 0 / IDCODE `0x9372c093`、ps_dap part 1；退出码 0，SVF 成功，STAT=`0x40007ffc`，scan/download stderr 空；[原始下载日志](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/jtag_20261001_193337/download.stdout.log) |
| 实板功能 | 现场确认“灯序、速度和单灯状态均符合预期”；对应 LED1→3→2→4→1、约 0.25 秒/步、单灯循环；[下载与现场确认记录](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/jtag_20261001_193337/program-result.json) |

最终位流：[lite_led_chaser.bit](D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/rundir/lite_led_chaser.bit)，5,980,582 字节；SHA-256 **`00c833bb65fec1573ecf0a8cf59c45c50cff76ab7f0a3398696c43be4f608c56`**。下载前后的磁盘哈希、复核及下载记录一致。下载为 FPGA 易失配置，掉电失效；没有 Flash/BOOT 更新、仪器周期测量或整份配置读回。

报告字段与原始 JSON、产物与磁盘、源码三处一致性及旧工程保留的独立核对见 [verification.json](D:/FPGACompetitionProject/tools/mcp-validation/ip-reuse/verification.json)。[board-validation.json](D:/FPGACompetitionProject/tools/mcp-validation/ip-reuse/board-validation.json) 保存本次现场确认，不继承旧灯序的观察结果。

## 遇到的工具细节与限制

- IP 定义的修订属性是 `CORE_REVISION`；最初查询 `REVISION` 返回错误，后续正确回读 3。第三方工具的错误正文仍伴随 `isError=false`，实际检查了正文与后续产物。
- `create_ip -dir` 要求父目录已存在；已建立批准的独立目录。Vivado 提示 xlconcat 设计用于 IPI，实际直接生成成功并通过本次 HDL 编译/实现；不扩大到其他 IPI-only 核。
- 该 IP 的 `GENERATE_SYNTH_CHECKPOINT` 为只读且已为 0；最初尝试设置报错，随后查询确认关闭，未创建/执行 IP 综合 run。生成后的文件查询需同时使用 `-compile_order sources -used_in ...`。这些接口错误及最终回读保留在 MCP 证据中。
- Procise 的 ELAB-W-109 指向厂商 32 输入模块中本配置未使用的 In4 等端口；生成包装器为 In4–In31 接常量 0，NUM_PORTS=4 的 generate 仅使用 In0–In3。全部组合自检、源码闭包与原生实现门禁通过，厂商 HDL 保持原字节。原日志另保留工具自身 `logfiels move ... failed` 提示；主 stdout、EDIF、时序/约束/位流报告均实际保留并完成核验，未修补该工具内部日志备份行为。
- Concat 的组合拼接在综合后已无独立 IP 单元引用；LC 与时序值恰好与此前自写同灯序 RTL 相同，不构成性能提升证据。这里的代表性是**源码交接方法**，不能推广为复杂 IP 已适配。
- 测试为行为仿真、Procise 原生内部时序及实板观察；不含布线后仿真或外部同步接口时序验收。后续其他 IP 仍须逐一核对完整可综合源码、语言、原语/加密/约束与具体配置，再讨论实施。

完成总结见根目录 [Done.md](D:/FPGACompetitionProject/Done.md)，资料索引见 [REFERENCES.md](D:/FPGACompetitionProject/REFERENCES.md) 14.4。
