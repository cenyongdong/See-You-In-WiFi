# 悟净 Lite 流水灯全流程验证

本工程是独立 PL 测试，目标器件为 **JFMQL30TAI676H**。于 2026-10-01 同意具体实现方案、以 XSim 2019.1 做纯 RTL 行为仿真、以 Procise 做综合/实现/位流/JTAG 下载，并同意将启动时钟显式修正为 `JtagClk`。板上下载属于 FPGA 易失配置，掉电失效。

## 当前源码与 MCP 验证：LED1→3→2→4（2026-10-01）

已重载两个 MCP 服务，并批准复用本工程测试新灯序，首阶段验收止于位流。随后明确授权下载，已通过 Procise 原生 JTAG 下载，现场确认“灯序和速度均符合预期”。当前 [RTL](rtl/lite_led_chaser.v) 为 **PL_LED1→3→2→4→1**，仍为 100 MHz、0.25 秒/步；旧 RTL/testbench 已备份到 `revisions/led_1234_before_1324`。下方历史原生上板记录属于旧灯序；新灯序验收使用本节的新下载与观察证据。

当前工具会话 Vivado MCP 按长期 AMD64 配置直接启动 2019.1，写入 RTL/testbench 并经 `run_tcl exec` 驱动既有 XSim 脚本；独立预期表检查分频 1/7/19 各 200 周期通过，实际状态 `0001→0100→0010→1000→0001`。随后 Procise MCP 完成原生综合、布局布线、位流和复核，作业最终状态 `reviewed`。

本次内部 setup/hold 裕量 **5.962/0.192 ns**，各 58 个端点、违例 0；LC 11/19650。五引脚/电平、29 INIT、JtagClk 和当前/仿真/构建 RTL 哈希均通过；四 LED 的 `no_output_delay` 边界保留。[完整结果及 MCP 调用证据](../../tools/mcp-validation/led1324/RESULTS.md)。

- [新仿真日志](runs/sim_20261001_182621_aa641e/simulate.stdout.log)。
- [新位流复核](runs/build_20261001_183334_5f3fc1/build-review.json)。
- 新位流（历史附件，当前仓库未附：`D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/rundir/lite_led_chaser.bit`），5,980,582 字节；SHA-256 `285356540f63f5b1a150827777f8e5e411843718976590db0cb39739b5ef7c18`。**已下载，观察确认通过**。
- [新灯序下载记录](runs/build_20261001_183334_5f3fc1/jtag_20261001_184939/program-result.json)：2026-10-01 18:50，北京时间；扫链确认 FPGA part 0，STAT=`0x40007ffc`，易失配置、未写 Flash。下载使用现有 Procise 原生脚本，MCP 首版仍无 JTAG 工具。

## 功能与板级依据

输入 100 MHz，每计数 25,000,000 个周期切换一次，单灯亮 0.25 秒，完整一圈 1 秒。当前灯序为 PL_LED1→3→2→4，原上板版本为 PL_LED1→2→3→4。RTL 不含厂商 IP；25 位计数器和四位循环寄存器在配置时初始化。两次 Procise 综合 EDIF 均检查全部 29 个寄存器的 INIT，计数器全 0、灯状态为 `0001`。这项结论针对当前 Procise/器件，不自动适用于其他平台。

原始来源：JFMQL30TAI_LITE.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/开发板手册/JFMQL30TAI_LITE.pdf`），实际 PDF 页码为 9、10、21、22；另见根目录 `REFERENCES.md` B4。

| 信号 | FPGA 封装引脚 | 电平 | 依据 |
| --- | --- | --- | --- |
| `clk_100m` | AC14 | LVCMOS33 | BANK12；G1 单端 100 MHz，VCC3V3 |
| `led[0]` / PL_LED1 | J1 | LVCMOS15 | BANK33，PL_VCC1V5 |
| `led[1]` / PL_LED2 | M6 | LVCMOS15 | BANK33，PL_VCC1V5 |
| `led[2]` / PL_LED3 | H7 | LVCMOS15 | BANK34，PL_VCC1V5 |
| `led[3]` / PL_LED4 | J8 | LVCMOS15 | BANK34，PL_VCC1V5 |

LED 经 NDS331N 低侧开关驱动，FPGA 输出高电平点亮。约束显式锁定五个引脚、电平、10 ns 时钟周期，LED 设置 DRIVE 4、SLEW SLOW。

## 原生 LED1→2→3→4 上板验证结果（历史）

| 阶段 | 结果与证据 |
| --- | --- |
| RTL 仿真 | XSim 2019.1 自检通过；分频值 1、7、19 各检查 200 周期，覆盖初始化、准确切换边界、单灯顺序与回绕 |
| 原生实现 | Procise 2025.1.1 temp / SVN 32494；setup 裕量 4.740 ns、hold 裕量 0.170 ns，各有 58 个内部端点、违例端点 0 |
| 时序覆盖 | 无缺失时钟/未约束内部端点/组合环；四个 LED 为 `no_output_delay`，没有外部同步采样要求，因此不伪造输出延迟；不能宣称所有 I/O 时序均完成验收 |
| 资源 | LC 13/19650、GCDU 1/32、IOU18M 4/72、IOU33M 1/48 |
| 位流复核 | JFMQL30TAI676H；StartupClk=JtagClk；原生 placed FDC 与引脚表一致；仿真/构建 RTL 哈希一致；INIT 检查通过 |
| JTAG 下载 | 2026-10-01 12:06，目标 `jfmql30` part 0，IDCODE `0x9372c093`；Procise 报告 SVF 执行成功，STAT 回读 `0x40007ffc` |
| 实际灯光 | 现场确认“四颗 LED 按预期循环”；本次全流程功能验收通过，未用仪器测量周期精度 |
| MCP | 先完成原生流程，随后讨论接入；本次未安装、配置或调用 FPGA MCP |

原生上板最终构建：`runs/build_20261001_120459_3fa8ba`。位流为该目录下 `rundir/lite_led_chaser.bit`，5,980,582 字节，SHA-256：

```text
a443d8f4bfde85eedc9de0e0328680cbb5d06c364f1113c55b14c4c6f4475eec
```

主要证据：`build-review.json`；`rundir/lite_led_chaser_route.json`、`lite_led_chaser_placed.fdc`、`lite_led_chaser.edif`、`lite_led_chaser.bgn`；`procise.stdout.log`；`jtag_20261001_120606/download.stdout.log` 和 `program-result.json`。

仿真记录在 `runs/sim_20261001_115631_342b3c`。`logs/preflight` 保留下载器查询、帮助查询和最初失败参数的排查日志。更早的两个 `build_*` 是保留的排查记录，不能作为本次最终位流入口。

## 复现命令

在 Windows PowerShell 中运行，构建每次创建新目录，不复用旧产物。仿真为纯 RTL 行为仿真；没有声称完成复旦微原语网表或布线后时序仿真。脚本只设置当前进程及其子进程环境，不修改永久 PATH。

以下仿真和构建操作须处于已授权任务中。当前源码为新灯序，示例复核目录对应新灯序；重新运行后应换成实际新目录。不要用当前源码重新复核原上板目录，以免混淆历史证据。

```powershell
$ledRoot = 'D:\FPGACompetitionProject\FPGA\lite_led_chaser'
& "$ledRoot\scripts\Simulate.ps1"
& "$ledRoot\scripts\Build.ps1"

# 用上面输出的新目录替换此处路径。
$ledBuild = "$ledRoot\runs\build_20261001_183334_5f3fc1"
$ledSim = "$ledRoot\runs\sim_20261001_182621_aa641e"
$ledPython = 'C:\Users\cenyongdong\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $ledPython "$ledRoot\scripts\ReviewBuild.py" --build-dir $ledBuild --sim-dir $ledSim
if ($LASTEXITCODE -ne 0) { throw '位流复核失败。' }
```

`ReviewBuild.py` 仅需 Python 标准库；输出的 `reviewed_for_jtag_download` 是复核状态，不构成下载授权。本次新灯序是在位流阶段结束、另行收到明确下载指令后才上板。原 `Program.ps1 -BuildDir <已复核的新目录>` 默认只扫链，加 `-Program` 才下载，后续下载须处于明确授权任务中；下载器序列号默认为实测的 `210512180081`，更换下载器或链结构时须重新查询核对。重新复核会生成新的复核记录，不应覆盖已经归档的观察结果。

## 已验证的 Procise Tcl 差异

1. `launch_run -stage bitstream` 是 Procise 流程；不能直接替换成 Vivado 的 `launch_runs`。
2. 本机工具的下载器显示名称是 `DIGILENT/JTAG-HS1`，但 `init_chain -cable_type` 实际接受 **`usb-jtag-hs1`**。大写显示名称和手册示例在本机返回参数错误；未改驱动或厂商设备数据库。
3. 链中有 FPGA part 0 和 PS DAP part 1；`-part` 应按实际链序号核对，不能把它理解成只要有两个器件就写 2。
4. 默认 `launch_run` 位流启动时钟是 Cclk；按手册的 JTAG 要求追加 `bitgen lite_led_chaser.bit -g StartupClk:JtagClk`。`launch_run` 返回工程根目录后必须显式 `cd rundir`，否则追加命令写到另一个目录。

本次下载命令由脚本生成并落盘：

```tcl
get_cable_info
init_chain -cable_type usb-jtag-hs1 -serial_number 210512180081
program_bit {已复核的绝对路径/lite_led_chaser.bit} -part 0
read_reg -part 0 -reg STAT -read
```

## MCP 参考：从原生后端到当前工具会话衔接

本次已经验证 Windows 下 XSim 行为仿真、Procise 独立批处理作业、JSON 时序报告解析、位流哈希及 JTAG 扫链/下载/寄存器回读。这些可作为 Procise MCP 适配层的后端基础。

随后已确定的小型 Procise MCP 已完成独立 stdio 验证；本轮又通过当前工具会话的七工具及 Vivado MCP 实现新灯序仿真→原生位流复核，详见顶部链接。Vivado 辅助纯 RTL 行为仿真，Procise 负责复旦微实现；不能直接替换两者的可执行路径或套用 Xilinx IP。首版仍限定本工程，没有 JTAG、任意 Tcl、取消或重启恢复；未做受控性能或准确率对照。
