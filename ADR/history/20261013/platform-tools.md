# 平台、启动介质与本机工具的历史

2026-10-13从AGENTS.md迁出，按主题保存原记录；原文“当前”“已批准”“下一步”和暂停/恢复只表示当时状态，不是现行进度或新的执行授权。最新进度见[PROJECT-PROGRESS](../../../PROJECT-PROGRESS.md)，执行规范以[AGENTS.md](../../../AGENTS.md)为准。源行编号与迁移清单用于追溯；不改写原失败、修订或验收边界。

<a id="a321"></a>

## A321 · 当前基线

来源：整理前 AGENTS.md 第321–321行。

- 当前基线：悟净开发板 Lite；Icraft 3.39.0；Procise 来自 `FMSH_Procise_2025.1.1_temp_202603201420_32494.exe`；板载镜像为 `icraft_v3_ubuntu20.04_aarch64_sd_image.bin`。参考位流尚未确定，不能自行选定；人工确认 `Docs/开发板手册/JFMQL30TAI_LITE.pdf` 是 30TAI 配套原理图，查阅 `REFERENCES.md` B4 获取页码和引脚依据。MIPI BANK12 电平及 GPIO 网络名/BANK 对应仍存在资料冲突，相关接线或约束须先讨论核对，不自行决断。

<a id="a323"></a>

## A323 · 已验证硬件状态（现场反馈，2026-09-30）

来源：整理前 AGENTS.md 第323–323行。

- 已验证硬件状态（现场反馈，2026-09-30）：Lite 已在无 SD 卡情况下完成开机和连线上板测试，使用 Alinx 黑金下载器，Procise 与 Vivado 均可识别芯片；不再将下载器连接/器件识别列为尚未验证。此结果不自动证明 Linux 启动、特定位流功能、DDR/AI 或模型已验证。

<a id="a324"></a>

## A324 · SD 启动最新状态（现场确认，2026-10-02；2026-10-03 补充板端查询/分区表）

来源：整理前 AGENTS.md 第324–324行。

- SD 启动最新状态（现场确认，2026-10-02；2026-10-03 补充板端查询/分区表）：已更换 SD 卡、完成 SD 启动卡制作和上板验证；串口正常输出信息，能够登录板载 Linux 系统。当前新卡的基本 SD 启动/串口登录已通过，不再作为待验证项；此前校验失败、启动文件异常及 H2testw 严重错误的记录属于旧卡历史，不能套用于新卡，也不能据换卡后启动成功追溯确诊旧卡的精确故障。截图已确认根设备 /dev/mmcblk0p2、ext4、rw,relatime，mmcblk0=58.3G、p1=1G、p2=26.1G，根文件系统约26G；resize2fs/sfdisk 存在，growpart 未找到。sfdisk=2.34，DOS/MBR ID=0x370deffb，总122167296个512字节扇区；p1 start/size/type=2048/2097152/e，p2=2101248/54687500/83。新卡品牌/型号、全容量、启动组件哈希和板端 runtime 版本未核验；成功登录不等于全容量、AI/模型或系统分区扩容已验证。扩大系统分区，设计要求代理仅提供具体命令和逐条说明，实际扩容人工在悟净 Lite 已启动的板载 Ubuntu 中通过串口执行。已形成备份/预演→sfdisk只扩大p2末尾→重启→resize2fs的逐条说明，目标p2长度120066048扇区（约57.25GiB）；这些为待人工操作步骤，未扩容/验收，未验证内核在线扩容支持。最新记录见 REFERENCES.md 第15节/15.1/15.2、Done.md 和 tools\sd-image-validation\20261002-new-card-board-confirmation.json，具体命令见同目录20261003-expand-root-COMMANDS.md。

<a id="a325"></a>

## A325 · 原生 FPGA 测试（2026-10-01）

来源：整理前 AGENTS.md 第325–325行。

- 原生 FPGA 测试（2026-10-01）： `FPGA\lite_led_chaser` 独立流水灯方案、XSim 2019.1 纯 RTL 行为仿真、Procise 全流程及生成位流后直接 JTAG 易失配置下载，并批准 StartupClk=JtagClk 修正；本次仿真、原生综合/布局布线/内部时序、位流复核和下载已完成，现场确认“四颗 LED 按预期循环”，全流程功能验收通过。总结见 `Done.md`，入口和证据见 `FPGA\lite_led_chaser\README.md`、`REFERENCES.md` 第 13 节；不能将其扩展为 Flash/BOOT 更新、AI 系统或 MCP 全流程已验收。本次流水灯未使用 MCP；后续接入状态见 MCP 基线相关条目。

<a id="a326"></a>

## A326 · SD扩容后续验收（2026-10-03，更新前述“待人工操作/未扩容”状态）

来源：整理前 AGENTS.md 第326–326行。

- SD扩容后续验收（2026-10-03，更新前述“待人工操作/未扩容”状态）：已在板载Ubuntu串口终端执行并明确确认扩容成功，最终截图显示内核p2长度120066048个512字节扇区、根/dev/mmcblk0p2 ext4 rw,relatime；resize2fs 1.45.5完成在线扩容至15008256个4KiB块，与分区字节数一致。lsblk p2约57.3G，df根容量57G、已用6.3G、可用48G、使用率12%。本次分区/根文件系统扩容人工执行并以截图验收通过，代理只核对和记录；无全容量写读、resize后额外重启或长期稳定性证据，不能扩大为AI/runtime验收。最新结果见Done.md同一工作补充、REFERENCES.md 15.3、tools\sd-image-validation\20261003-expansion-success.png和结构化记录。此前待执行文字为命令准备阶段的历史状态。

<a id="a327"></a>

## A327 · MCP 与 Vivado 辅助基线（2026-10-01，初始接入历史状态；最新见当前工具会话衔接验收）

来源：整理前 AGENTS.md 第327–327行。

- MCP 与 Vivado 辅助基线（2026-10-01，初始接入历史状态；最新见当前工具会话衔接验收）：优先讨论 Procise MCP，并将 Vivado MCP 用于仿真和参考工程辅助；已自行接入 `vivado-mcp`，本会话已发现工具且成功调用只读 `list_sessions`，返回无活跃会话，尚未通过 MCP 启动 Vivado 或运行仿真。Vivado 以现有 **2019.1** 为准，安装入口 `D:\Xilinx\Vivado\2019.1\bin\vivado.bat`；资料中使用 Vivado 2018 版的项目仅作思路参考，不将 2018 作为当前执行基线，不因旧工程的版本说明要求安装 2018 或自行升级/迁移工程与 IP。对 Procise MCP 的方向认可属于讨论范围，开发、安装和配置变更仍须先明确方案并获同意；已有 Vivado MCP 的辅助调用不能替代 Procise 原生实现与实板验收。

<a id="a328"></a>

## A328 · MCP 首版后续验证（2026-10-01，首版阶段历史状态；最新见当前工具会话衔接验收）

来源：整理前 AGENTS.md 第328–328行。

- MCP 首版后续验证（2026-10-01，首版阶段历史状态；最新见当前工具会话衔接验收）：首版、独立 SDK `mcp==2.2.0`、项目配置写入、复核日志编码适配/复验，以及 Vivado 临时启动捕获和仅子进程 AMD64 验证。`tools\procise_mcp` 七工具真实 stdio 客户端通过；首版阶段作业 `build_20261001_170101_78f11a` 用 MCP 新仿真完成复核，未下载。`.codex\config.toml` 已写入，Codex CLI 已读取；配置采用“暂不重载”，当前工具会话 Procise 工具发现/调用待后续验收，不自行重载。Vivado MCP 的 XPR 解析/原 XML 核对、独立客户端和当前工具会话临时修正后的 2019.1 会话、错误恢复、经现有脚本执行的 XSim 均通过。当前工具会话原先两个架构变量为空，厂商启动器默认选择不存在的 32 位程序；仅给测试子进程设 PROCESSOR_ARCHITECTURE=AMD64 后通过，测试会话已关闭，永久环境/安装及生效 Vivado 配置未改；长期修复仍须讨论批准。第三方工具 `[ERROR]` 正文可能伴随 `isError=false`，须同时核对正文/rc/产物。`ReviewBuild.py` 已批准支持 UTF-8/UTF-16 BOM 日志，批准脚本哈希已更新，不据此回写原上板记录。入口与证据见 `tools\mcp-validation\RESULTS.md`、`tools\procise_mcp\README.md` 和 `REFERENCES.md` 第 14 节。首版无任意 Tcl/JTAG/Flash，不承诺取消或重启恢复；超时不等于底层作业已取消。

<a id="a330"></a>

## A330 · 开发与训练环境（记录说明，2026-10-01）

来源：整理前 AGENTS.md 第330–330行。

- 开发与训练环境（记录说明，2026-10-01）：本机为 Windows 10，方案倾向方案 A，即 Procise 与 Icraft 保留在 Windows；当前算法训练在远程 Ubuntu 服务器上进行，其文件目录已挂载到本机 `Z:`。本机另有双系统 Ubuntu，但不能据此把当前训练位置写成本机 Ubuntu。`Z:` 挂载只表明文件访问入口，不能据此认定 SSH、远程执行或服务器软件环境已经验证；具体项目目录与比赛核心模型仍待后续讨论。 Windows Icraft 独立依赖目录、两个官方 ZIP、启动器及第一阶段加载验证；该阶段已通过，见 `REFERENCES.md` I5。其余安装、配置、迁移与模型/设备操作仍遵循决策审批规范。

<a id="a332"></a>

## A332 · Icraft 独立调用入口

来源：整理前 AGENTS.md 第332–332行。

- Icraft 独立调用入口：第一阶段验证已通过，可在已授权任务中调用 `tools\Invoke-Icraft.ps1`，例如 `& 'D:\FPGACompetitionProject\tools\Invoke-Icraft.ps1' -IcraftArgs @('run', '--help')`。独立依赖位于 `.local\icraft-runtime\cuda-11.8.0`；启动器只给子进程补 PATH，并固定 Icraft 3.39.0、校验 DLL 哈希、保留日志。调用说明见 `tools\README.md`，验证证据见该依赖目录的 `verification-report.json`。不得将加载/帮助通过视为模型、GPU 或实板功能通过，也不得因启动器存在而推定模型编译/部署操作已获授权。

<a id="a335"></a>

## A335 · Vivado MCP 长期配置（2026-10-01，配置写入时状态；后续重载验收见下一条）

来源：整理前 AGENTS.md 第335–336行。

- Vivado MCP 长期配置（2026-10-01，配置写入时状态；后续重载验收见下一条）：本轮设计要求实施此前讨论的长期方案，已仅在 `C:\Users\cenyongdong\.codex\config.toml` 的 `[mcp_servers.vivado.env]` 增加 `PROCESSOR_ARCHITECTURE = "AMD64"`，其他配置逐字节保留，备份与证据见 `tools\mcp-validation\vivado-permanent-config-change.json`。读取 Codex 实际解析配置的新 stdio MCP 进程已验证：无需临时启动器，直接启动 Vivado 2019.1 并回读 AMD64，通过后已关闭测试会话。已有聊天 Vivado MCP 进程尚未重启，不能宣称已加载新配置；新启动/重启后才生效。此授权不扩展为系统环境、EDA 安装或 Procise 重载；Procise 仍暂不重载。结果见 `REFERENCES.md` 14.1 和 `tools\mcp-validation\RESULTS.md`。

<a id="a337"></a>

## A337 · 当前工具会话 MCP 衔接验收（2026-10-01，位流阶段历史状态；后续上板见下一条）

来源：整理前 AGENTS.md 第337–338行。

- 当前工具会话 MCP 衔接验收（2026-10-01，位流阶段历史状态；后续上板见下一条）：已重载 Procise/Vivado MCP，并明确批准 `tools\mcp-validation\led1324\PLAN.md`。当前工具会话 Procise 七工具均已调用通过；Vivado 2019.1 直接使用长期配置启动并回读 AMD64，无临时启动器。已先备份旧 RTL/testbench 至 `FPGA\lite_led_chaser\revisions\led_1234_before_1324`，通过 Vivado MCP 写入 LED1→3→2→4 新源码并驱动 XSim 自检，再经 Procise MCP 完成原生综合/布局布线/位流及复核；最新 `build_20261001_183334_5f3fc1` 对应 `sim_20261001_182621_aa641e`，内部 setup/hold 5.962/0.192 ns、违例端点 0，五引脚/电平、29 INIT、JtagClk、源码哈希和原报告对照通过。完整证据见 `tools\mcp-validation\led1324\RESULTS.md`、`REFERENCES.md` 14.2 和 `Done.md`。本轮批准止于位流复核，新位流未下载、未实板观察；旧 LED1→2→3→4 上板确认不得扩展到新灯序。构建/仿真/复核脚本、MCP 服务及配置未改；首版仍只支持当前流水灯工程，无任意 Tcl/JTAG/Flash、取消或重启恢复。遇到新工程/IP/接口或扩大工具范围仍须讨论批准，不因本次通过自动扩展授权。

<a id="a339"></a>

## A339 · 新灯序上板验收（2026-10-01，更新前述“未上板”阶段状态）

来源：整理前 AGENTS.md 第339–340行。

- 新灯序上板验收（2026-10-01，更新前述“未上板”阶段状态）：下载新位流，已复核 `build_20261001_183334_5f3fc1` 的位流/源码/仿真哈希及当前 JTAG 链，用既有 `Program.ps1` 经 Procise 原生下载到 `jfmql30` part 0；位流 SHA-256 `285356540f63f5b1a150827777f8e5e411843718976590db0cb39739b5ef7c18`，2026-10-01 18:50（北京时间）完成，STAT=`0x40007ffc`。现场确认“灯序和速度均符合预期”，新 LED1→3→2→4→1 的实板功能验收通过。下载是 FPGA 易失配置，未写 Flash/BOOT；无仪器周期测量或整份配置读回。入口见 `REFERENCES.md` 14.3、`tools\mcp-validation\led1324\RESULTS.md`、新构建的 `jtag_20261001_184939\program-result.json` 和 `Done.md`。下载环节用原生工具，Procise MCP 服务/七工具未改，不能宣称 MCP JTAG 已验证；旧灯序记录仍保留。此授权仅覆盖本次明确的新位流，后续扩大功能、配置或写 Flash 等操作仍须讨论批准。

<a id="a341"></a>

## A341 · 真实 IP 源码交接实板验收（2026-10-01）

来源：整理前 AGENTS.md 第341–342行。

- 真实 IP 源码交接实板验收（2026-10-01）： `tools\mcp-validation\ip-reuse\PLAN.md` 的 xlconcat 最小方案。独立 `FPGA\lite_led_ip_bridge` 已用当前工具会话 Vivado 2019.1 MCP 生成真实 xlconcat 2.1 Rev.3（四个 1-bit 输入）、写入 RTL/testbench、以同一综合包装器/厂商 HDL 通过 16 种组合及分频 1/7/19 各 200 周期 XSim；随后用 Procise 原生批处理完成综合/布局布线/位流复核及 JTAG 易失下载。`build_20261001_193157_bef06d` 对应 `sim_20261001_193106_688cd5`，setup/hold=5.962/0.192 ns、违例 0，五引脚、电平、29 INIT、全部 HDL/XCI 哈希和 JtagClk 通过；位流 SHA-256 `00c833bb65fec1573ecf0a8cf59c45c50cff76ab7f0a3398696c43be4f608c56`，19:34 下载至 jfmql30 part 0，STAT=0x40007ffc。现场确认“灯序、速度和单灯状态均符合预期”。Vivado checkpoint=0，synth/impl run 未启动，全部综合在 Procise；当前 Procise MCP 仍固定旧工程，本次未扩展服务或配置。仅证明这个无器件原语依赖的明文组合 IP/具体配置能交接；不能推广到加密源码、FIFO/BRAM/Clocking/DSP、DMA、HDMI 或 AXI 系统，也不能以 MCP 替代适配。原工程和记录保留，无 Flash/BOOT；详细结果见 `REFERENCES.md` 14.4、`tools\mcp-validation\ip-reuse\RESULTS.md` 和 `Done.md`。后续 IP/工程/工具扩展仍须先讨论批准。

<a id="a343"></a>

## A343 · 板端网络/Icraft与Docker交叉编译最新进度（人工确认，2026-10-03）

来源：整理前 AGENTS.md 第343–344行。

- 板端网络/Icraft与Docker交叉编译最新进度（人工确认，2026-10-03）：悟净Lite已通过SD启动，网线连接主机，已在MobaXterm通过SSH进行开发和通信；已将 `D:\Dowload from Chrome\嵌赛资料\Icraft\Icraft_V3.39.0安装包\30TAI&100TAI\30TAI&100TAI` 中的板端Icraft及CustomOp传输到板上并完成安装。本机Docker交叉编译环境已搭建、相关工具链已配置，明确 `FPAI` 是**容器名**，不是已确认的镜像名。代理只读核对本地安装包control：两份onchip包均为arm64/3.39.0，两份amd64包均为amd64/3.39.0；这不是板端或容器已安装软件的独立版本查询。板端实际包版本/路径、SSH地址、容器镜像身份/编译器/sysroot及“交叉编译→板端运行”尚未核验，不自行填写或据安装完成认定AI/runtime/参考位流配套和模型推理通过。板端SSH与远程Ubuntu训练服务器是不同对象，不能混用；当前训练位置和Windows Procise/Icraft基线保持此前记录说明。记录见 `REFERENCES.md` 第16节、`Done.md`、`tools\development-environment\20261003-progress.json`。本次进度同步不扩展为代理连接SSH、操作Docker、安装/部署或执行新的板端任务授权。
