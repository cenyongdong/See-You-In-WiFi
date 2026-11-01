# LED1→3→2→4：当前工具会话 Vivado / Procise MCP 验证

日期：2026-10-01。现场反馈已重载两个 MCP 服务，并明确批准 [具体方案](D:/FPGACompetitionProject/tools/mcp-validation/led1324/PLAN.md)。**当前工具会话已实际完成 Vivado MCP 写入 RTL/testbench、XSim 自检，以及 Procise MCP 综合、布局布线、位流生成和复核，流程通过。** 该阶段验收截至位流；下载新位流，已通过 Procise 原生 JTAG 下载，现场确认“灯序和速度均符合预期”，新灯序实板功能验收通过。

## 工程与服务

复用 `D:\FPGACompetitionProject\FPGA\lite_led_chaser`，目标器件为悟净 Lite 的 `JFMQL30TAI676H`。旧 RTL/testbench 在写入前备份到 [revisions/led_1234_before_1324](D:/FPGACompetitionProject/FPGA/lite_led_chaser/revisions/led_1234_before_1324/lite_led_chaser.v)，旧运行目录和上板证据保留。

| 对象 | 当前工具会话实测 |
| --- | --- |
| Procise MCP | 七工具均已实际调用；`get_environment` 原生探测返回 Procise 2025.1.1 temp / SVN 32494；独立 Python 3.12.14 / MCP SDK 2.2.0 |
| Vivado MCP | `start_session` 省略路径覆盖，直接使用长期配置启动 Vivado 2019.1；`run_tcl` 回读 AMD64，无临时启动器，证明重载后的聊天入口可用 |
| 会话与配置 | 仅使用本次 Tcl 会话 `lite_led1324_pipeline`，已关闭；外部 GUI 未操作。未修改 MCP 服务、配置、EDA 安装或系统环境 |

用户级配置整体哈希与此前长期修改记录不同；只读语义对照发现差异仅为 `mcp_servers.node_repl.env.SKY_CUA_NATIVE_PIPE_DIRECTORY` 的值，Vivado 条目与批准的长期配置完全一致。未据整体哈希变化判定 Vivado 配置失效，也未修改配置。对照结果见 [verification.json](D:/FPGACompetitionProject/tools/mcp-validation/led1324/verification.json)。

## 实现与仿真

工作源码：[RTL](D:/FPGACompetitionProject/FPGA/lite_led_chaser/rtl/lite_led_chaser.v)、[testbench](D:/FPGACompetitionProject/FPGA/lite_led_chaser/sim/tb_lite_led_chaser.sv)。通过当前工具会话 Vivado MCP 的 Tcl 文件操作写入，随后 `run_tcl` 的 `exec` 调用既有 `scripts/Simulate.ps1`，驱动 XSim 2019.1。未使用 Vivado 的 Xilinx 综合/位流生成，也未验收 `launch_simulation` 工程模式。

硬件默认仍为 100 MHz、25,000,000 周期/步，即 0.25 秒/步、一圈 1 秒。灯状态初始化为 `0001`，连接置换实现 `0001→0100→0010→1000→0001`，对应 LED1→3→2→4→1。testbench 用明确预期值查表，不复用 RTL 的置换表达式；分频 1/7/19 各检查 200 周期，覆盖初始化、切换边界、单灯和回绕。

实测首九个状态为 `0001, 0100, 0010, 1000, 0001, 0100, 0010, 1000, 0001`；打印 PASS，1996 ns 正常结束。[仿真日志](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/sim_20261001_182621_aa641e/simulate.stdout.log) 为 UTF-16 BOM，已由批准的编码适配正常读取。

## Procise 原生结果

作业 ID：`5c5f8f383cd74afa87915adc67921a80`。当前工具会话依次调用 `start_led_build`、`get_job_status`、`tail_job_log`、`read_build_report`、`list_artifacts`、`review_led_build`，状态由 running → native_completed → reviewed，退出码 0。构建目录为 `runs/build_20261001_183334_5f3fc1`。

| 检查 | 本次结果 |
| --- | --- |
| 原生实现 | 综合、布局布线和位流生成完成；原生日志含 `BUILD_TCL_COMPLETED`，stderr 为空 |
| 内部时序 | setup 裕量 5.962 ns、hold 裕量 0.192 ns；各 58 个端点，违例端点均 0；10 ns 时钟；无缺失时钟、未约束内部端点或组合环 |
| 外部时序边界 | 保留四 LED 的 `no_output_delay=4`，其余检查计数 0；LED 没有外部同步采样协议，不扩展为完整接口时序验收 |
| 资源 | LC 11/19650、GCDU 1/32、IOU18M 4/72、IOU33M 1/48，来自本次原生日志 |
| 板级约束 | AC14/LVCMOS33 时钟；LED1/2/3/4 为 J1/M6/H7/J8、LVCMOS15，placed FDC 与既定约束相符 |
| 初始化与位流 | 29 个寄存器 INIT 通过；JFMQL30TAI676H、StartupClk=JtagClk、UnconstrainedPins=Disallow（原值 `Disallow*`） |
| 来源一致性 | 当前、仿真和构建 RTL 哈希相同；当前与仿真 testbench 相同；FDC 和执行脚本与变更前快照相同 |
| 原始证据对照 | MCP 的时序、时钟、检查计数等于同一原生 JSON；五项产物的大小和 SHA-256 等于磁盘；复核摘要与实际位流一致 |

最终 [位流文件](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/rundir/lite_led_chaser.bit)：5,980,582 字节，SHA-256：

```text
285356540f63f5b1a150827777f8e5e411843718976590db0cb39739b5ef7c18
```

RTL SHA-256：`30f1fbb17c74c93fc11c796facb342c6e9d93253d2644b3223b7ccfa731e2bb4`；testbench：`f775fbb3cc59615f8475ce3c590ed4137b54d3a22325238da76bfebf704fbe6c`。

## 证据与后续参考

- [最终完整 MCP 调用返回](D:/FPGACompetitionProject/tools/mcp-validation/led1324/mcp-calls.final.json)；`mcp-calls.json` 为复核前的中间快照，最终状态以此完整记录为准。
- [独立磁盘/报告核对](D:/FPGACompetitionProject/tools/mcp-validation/led1324/verification.json)、[修改前快照](D:/FPGACompetitionProject/tools/mcp-validation/led1324/source-before.json)、[备份与修改后哈希](D:/FPGACompetitionProject/tools/mcp-validation/led1324/source-after.json)。
- [位流复核记录](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/build-review.json)、[原生时序报告](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/rundir/lite_led_chaser_route.json)、[位流设置](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/rundir/lite_led_chaser.bgn)。

这次直接验收了重载后的聊天工具入口，更新此前 Procise 仅独立客户端通过、聊天调用待验收的状态。纯 RTL 可以由 Vivado/XSim 做前端行为验证、Procise 做复旦微目标实现，并用哈希关联同一份代码。后续含原语/IP、PS/DDR/AI 或外部高速接口的设计仍需适配与自己的验证；首版 Procise MCP 仍只支持当前流水灯工程，没有任意 Tcl、下载、取消或重启恢复能力，也没有受控速度/准确率提升结论。

位流验证阶段未下载上板，原 LED1→2→3→4 的确认也未用于证明新灯序。原位流 SHA-256 仍为 `a443d8f4bfde85eedc9de0e0328680cbb5d06c364f1113c55b14c4c6f4475eec`。既有复核字段 `reviewed_for_jtag_download` 表示产物检查状态，不构成下载授权；后续取得新的明确下载指令才执行下节操作。

## 后续授权下载与实板验收（2026-10-01）

“请你将新位流下载上板进行实际验证”。下载前重新核对位流/源码/仿真哈希、器件、JtagClk、时序、INIT 和执行脚本；保持同一份已复核位流，不重新生成。使用既有 `scripts/Program.ps1 -BuildDir ...build_20261001_183334_5f3fc1 -Program`，由 Procise 原生工具完成本次下载，未修改 MCP 服务或增加 JTAG 能力。

| 环节 | 实测结果 |
| --- | --- |
| 当前连接核对 | 单个 Alinx/DIGILENT JTAG-HS1，序列号 `210512180081`；重新扫链确认 `jfmql30` part 0 / IDCODE `0x9372c093`，`ps_dap` part 1 |
| 原生下载 | 2026-10-01 18:50（北京时间）完成；退出码 0，`PROGRAM_TCL_COMPLETED` 与 `SVF instructions execute success`，scan/download stderr 均为空 |
| 状态回读 | STAT=`0x40007ffc`；未进行整份配置数据读回比对 |
| 产物一致性 | 下载前后位流 SHA-256 均为 `285356540f63f5b1a150827777f8e5e411843718976590db0cb39739b5ef7c18` |
| 实板观察 | 现场确认“灯序和速度均符合预期”：LED1→3→2→4→1，约 0.25 秒/步、同一时刻单灯；未用仪器测量周期精度 |
| 写入范围 | FPGA 易失 JTAG 配置，掉电失效；未写 Flash/BOOT |

[下载与现场确认记录](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/jtag_20261001_184939/program-result.json)、[原始下载日志](D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/jtag_20261001_184939/download.stdout.log)、[板上验证证据](D:/FPGACompetitionProject/tools/mcp-validation/led1324/board-validation.json)。新构建的 `build-review.json` 仅补充本次下载记录入口和观察字段；原生时序/位流/源码复核值保持不变，旧上板记录未改。`mcp-calls.final.json` 和 `verification.json` 保留下载前阶段的历史状态，最新物理结果以本节记录为准。

至此，当前 Lite 新灯序通过“Vivado MCP 写入源码及行为仿真 → Procise MCP 原生实现及位流复核 → Procise 原生 JTAG 下载 → 实板观察”的流程；下载环节不记为 MCP 下载已验证。
