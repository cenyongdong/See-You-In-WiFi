# 悟净 Lite：真实 xlconcat IP 流水灯源码交接

2026-10-01 已完成 Vivado 2019.1 MCP 生成 IP/编写 RTL/XSim → Procise 2025.1.1 temp 原生综合、布局布线、位流 → JTAG 易失下载 → 现场观察。现场确认“灯序、速度和单灯状态均符合预期”。完整过程与限制见 [RESULTS.md](../../tools/mcp-validation/ip-reuse/RESULTS.md)。

## 功能与硬件

目标是 Lite / JFMQL30TAI676H，默认 100 MHz、0.25 秒/步，LED1→3→2→4→1。时钟 AC14/LVCMOS33；LED1/2/3/4 为 J1/M6/H7/J8、LVCMOS15，高电平点亮。FDC 从原已验证工程逐字节复制，原理图依据为 `Docs/开发板手册/JFMQL30TAI_LITE.pdf` 第 9/10/21/22 页。

真实 Vivado `xlconcat` 2.1 Rev.3 配置四个 1-bit 输入，将 state[3]、state[2]、state[0]、state[1] 接入 In0–In3，dout 装入灯状态寄存器。没有编辑厂商源码，也没有用自写拼接模块充当 IP。

## 文件与执行入口

| 文件 | 职责 |
| --- | --- |
| `rtl/lite_led_chaser.v` | 当前工具会话 Vivado MCP 写入的顶层 RTL，实际例化生成 IP |
| `sim/tb_lite_led_chaser.sv` | IP 全部 16 种输入独立真值表；分频 1/7/19 的流水灯 200 周期自检 |
| `ip/led_state_concat/led_state_concat.xci` | IP 配置来源，不直接供 Procise 综合 |
| `ip/led_state_concat/synth/led_state_concat.v` | 本次仿真和原生综合共同采用的真实综合包装器 |
| `ip/led_state_concat/hdl/xlconcat_v2_1_vl_rfs.v` | 未修改的厂商 Verilog 实现，与安装库哈希一致 |
| `source-manifest.json` | 三份设计 HDL、XCI、参数、来源哈希与本次模块闭包 |
| `scripts/generate-ip.tcl` | 2019.1 IP 生成复现步骤；默认保护现有 XCI，复现应指定新 ASCII 目录 |
| `scripts/AuditSources.py` | 本项目特定的源文件/参数检查与清单生成，非通用 HDL 解析器 |
| `scripts/Stage-Sources.ps1` | 用清单哈希校验并复制同一设计源码到独立仿真/构建目录 |
| `scripts/Simulate.ps1` | XSim 编译真实综合 HDL、自检、保留日志；本次由 Vivado MCP 调用 |
| `scripts/Build.ps1`、`build.tcl` | Procise 原生解析、综合、布局布线、位流及 JtagClk |
| `scripts/ReviewBuild.py` | 时序、引脚、INIT、位流、全部 IP 源码一致性和无黑盒复核 |
| `scripts/Program.ps1` | 下载前重新扫链、复核位流及 IP 源码哈希，再经原生 Procise 下载 |

本次 Vivado MCP 的 `run_tcl` 实际执行：

```tcl
puts [exec {C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe} -NoProfile -NonInteractive -ExecutionPolicy Bypass -File {D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/scripts/Simulate.ps1}]
```

Procise 构建与复核的已执行命令（PowerShell，项目根目录）：

```powershell
& 'D:\FPGACompetitionProject\FPGA\lite_led_ip_bridge\scripts\Build.ps1'
& 'D:\FPGACompetitionProject\.local\procise-mcp-venv\Scripts\python.exe' `
  'D:\FPGACompetitionProject\FPGA\lite_led_ip_bridge\scripts\ReviewBuild.py' `
  --build-dir 'D:\FPGACompetitionProject\FPGA\lite_led_ip_bridge\runs\build_20261001_193157_bef06d' `
  --sim-dir 'D:\FPGACompetitionProject\FPGA\lite_led_ip_bridge\runs\sim_20261001_193106_688cd5'
```

此处 build/sim 参数记录本次实际作业，重新构建必须使用新的对应目录，不复核或下载同名旧文件。任何后续设计变更、扩大范围或新的上板任务仍依根目录 AGENTS.md 讨论批准。当前 Procise MCP 服务限定旧工程，本试验没有扩展其配置/工具。

## 本次通过的产物与边界

- 仿真：`runs/sim_20261001_193106_688cd5`，16 种 IP 输入及 1/7/19 各 200 周期通过。
- 构建：`runs/build_20261001_193157_bef06d`，setup/hold=5.962/0.192 ns、违例 0，五引脚/电平、29 INIT、JtagClk 通过。四 LED 保留 no_output_delay。
- 最终位流（历史附件，当前仓库未附：`D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/rundir/lite_led_chaser.bit`）：5,980,582 字节；SHA-256 `00c833bb65fec1573ecf0a8cf59c45c50cff76ab7f0a3398696c43be4f608c56`。
- [下载与观察记录](runs/build_20261001_193157_bef06d/jtag_20261001_193337/program-result.json)：19:34 经 jfmql30 part 0 下载，STAT=0x40007ffc，人工确认通过。

本次没有 Vivado 综合：前端两个 run 最终均为 Not started，checkpoint=0。物理实现与验收以 Procise 和当前 Lite 为准。结果只覆盖这个明文组合 IP 的配置/源码交接；Concat 可优化为连线，不能作为加密 IP、存储器、时钟核、DMA 或 HDMI 已兼容的证据。没有 Flash/BOOT、布线后仿真、仪器周期测量或整份配置读回。
