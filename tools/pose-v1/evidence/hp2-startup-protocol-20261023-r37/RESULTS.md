# r37 启动协议诊断：实板异常、源码对照与恢复结果

2026-10-24。**已用时序合格的协议检查位流完成一次被动启动，复现 HP2 AR=0／R=6，并抓到原生协议规则 58／59／61。已恢复原 BOOT 文件和原 BOOT 运行；D45 仍未解决。** AI 四路连接、接通的 HDMI／旧视频 S01 支路及功能复位均保持。

## 设计与测试条件

PL 作为 AXI 主机，通过 HP2 读取 PS DDR；PL 发 AR，PS 边界返回 R。AI 连接为 HC0→HP0、HC1→HP1、HC2→HP2 S00、HC3→HP3，HP2 S01 接 HDMI／旧视频支路，未删除模块。本轮没有加载 SDK、执行 DMA／推理或启动 HDMI 读帧，没有按实体键；候选通过软件重启加载，未做断电冷启动。

观察点位于原厂 PS7 适配宏的外露 HP2 口与互联 M00 之间；不把这个宏名称直接等同于已知硬 PS 内部实现。采样器与其 `S_AXI_HP2_ACLK` 共用 `hp_axi_aclk_1`，名义 200 MHz／5 ns；GP 为 100 MHz，PS FCLK0 为 50 MHz。原生 `axi_protocol_checker:2.0` revision 4 按 AXI3、64 位数据、32 位地址、6 位 ID、读写检查容量各 8 配置，整束监测输入寄存 1 个 HP 周期，保留全部 160 位状态。

`PS_HP2_resetn` 是 PS7 的 `SAXIHP2ARESETN` 输出，本轮用于观察及检查器 ARESETN，不驱动 PL 功能复位。`PL_HP2_resetn` 是 HP2 PL AXI 互联的低有效复位，复位控制器使用 HP 时钟并等待 PL MIG DDR 就绪。`HP_reset` 是 HP 域高有效功能复位，由系统复位、取反的 FCLK_RESET0_N 和软件复位合成后在 HP 域产生，取反后接 HDMI／旧视频等模块。PS 输出拉高是否等于适配层／PS 全部内部状态已清理，尚缺匹配 030ai／AArch64 的接口契约。

独立保存首次任意指示的完整状态和周期；128 点、每点 576 位的连续窗口由首个非建议指示触发，32 点前史＋触发点＋95 点后史。首次任意指示的发布增加 1 个 HP 周期流水，保留原事件周期和状态；非建议窗口没有整体后移。建议项、协议规则、容量／配置项分别解码。

## 实板关键现象

候选启动 ID：`b5231f10-7b90-4a71-8c90-20851c9d0e8c`。启动监测累计 **PS AR 握手 0、R 握手 6**；AW／W／B 握手均 0，计数溢出掩码 0，事件缓冲未溢出。S01 源端连接核验通过，输入掩码 `180224`。

| 实际 HP 周期 | 观察结果 |
|---|---|
| 342377～342408 | 首个连续窗口内 PS_HP2_resetn=0、PS_RVALID=0、PL_HP2_resetn=0、HP_reset=1、PS_ARVALID=0 |
| **342409** | **PS_HP2_resetn、PS_ARREADY、PS_RVALID 同一采样边沿升高**；RID=0x20、RRESP=0、RLAST=0、RDATA=0，RREADY=0；PL 互联仍复位 |
| **342414** | 原生状态首次出现 **58／59／61** 及建议项 92／93／95；距上述原始边沿 5 个 HP 周期，名义 25 ns |
| 342445 | FCLK_RESET0_N 首次升高；此前最早 RVALID 已出现，AI 和 HDMI 功能复位仍未释放 |
| 342447 | HP_reset 从 1 降为 0；此时 PL_HP2_resetn 仍为 0 |
| 342453 | AI 的 pl_rst_n 升高；此时 PL_HP2_resetn 仍为 0 |
| **11588729** | PL_HP2_resetn 从 0 升为 1；PS_RVALID 仍为 1、RID=0x20 |
| 11588731～11588734、11588736～11588737 | PS R 通道共 6 次握手，每拍 RID=0x20、RLAST=0、RRESP=0、RDATA=0 |
| 11588735 起 | S01_RVALID 升高，S01_RREADY 在该窗口全程为 0；窗口末 PS／S01 RVALID 仍为 1，HC2 无 AR／R 握手 |

首次原生 160 位状态为 `0x0000000000000000b00000002c00000000000000`，低字在前的 32 位数组为 `[0, 738197504, 2952790016, 0, 0]`。

| 位 | 原生名称 | 本轮判读 |
|---|---|---|
| 58 | AXI_ERRS_RDATA_NUM | 读返回数量／事务记账相关协议规则 |
| 59 | AXI_ERRS_RID | 返回读 ID 与检查器已知请求的匹配规则 |
| 61 | AXI_ERRS_RVALID_RESET | 复位期间／释放附近 RVALID 的协议规则 |
| 92／93／95 | XILINX_AWREADY_RESET／WREADY_RESET／ARREADY_RESET | READY 复位建议项，单独出现不认定协议违规 |

协议窗口为 342382～342509，检查器 SystemResetn、ready、seen_reset_low 在整个窗口均为 1，PL 互联仍复位，五个 AXI 通道握手均 0。未出现检查容量超限位。因此这次协议规则指示发生在 6 拍 R 握手之前，并非消费这 6 拍之后才产生的报错，也不只是旧窗口里的 READY 建议项。

## 波形、原始数据与证据边界

- [完整协议窗口 PNG](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/protocol/protocol.png)、[CSV](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/protocol/protocol.csv)、[VCD](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/protocol/protocol.vcd)，包含完整 AR／R／AW／W／B 及 160 位状态。
- [首次 PS RVALID 窗口](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/cycletrace/bank0.png)：342377～342504，共 128 点。
- [PL 互联复位释放窗口](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/waveforms/cycletrace/bank1.png)：11588697～11588824，共 128 点；两窗均有同名 CSV／VCD。
- 未加工的 BRAM／计数读回值：[协议 raw.json](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/board-candidate/run-1/protocol/raw.json)、[双窗口 raw.json](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/board-candidate/run-1/cycletrace/raw.json)、[释放事件 raw.jsonl](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/board-candidate/run-1/release/raw.jsonl)。图是这些真实连续样点的绘制，不是示意图或仿真。

AR 握手累计为 0 的范围是本次硬件监测启动至冻结的有效 HP 时钟观测段；逐拍 ARVALID=0 仅对上述连续窗口有直接证据。配置前、停钟时和两个窗口之间没有逐拍覆盖。GP 初始高电平不能替代实际释放边沿；本次释放同拍结论来自 HP 原始连续样点。

**RVALID 在 RREADY=0 时持续为 1 本身合法。** 本轮新增证据是复位边沿附近、无已观测请求时的原生 58／59／61 指示，仍不能凭它唯一判定 PS 内部逻辑或某个 PL IP 故障。原生检查器输入寄存和内部状态计算存在延迟，25 ns 是本次实测报告间隔，不作为普遍固定延迟；不要把整个原始窗口平移。

官方已说明 HP FIFO 在 PL，不再把“PS 内部 HP FIFO 残留”作为确认原因。配置前事务状态、适配层与互联两侧复位含义／释放次序，以及软件重启与冷上电是否不同，仍需区分。S01 收到返回是可见事实，单凭 RID=0x20 不能追溯最初由哪个历史主机发起。

## 捕获后的离线连线核实

- 原厂适配的 `SAXIHP2ARESETN` 确为输出，直连 PS7 宏同名口；RDATA／RID／RLAST／RRESP／RVALID 也从该宏直接接出。可读文本没有给出宏内部 FIFO 实例及复位完成含义。[原厂适配源码](D:/FPGACompetitionProject/.local/hdmi-boot-witness-20261019-r23/reference/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ipshared/8fd3/hdl/verilog/processing_system7_v5_5_atc.v:5663)
- HP2 互联 M00／S00／S01 的 `HAS_DATA_FIFO=0`、`HAS_REGSLICE=1`，可见返回缓存是寄存切片；其 PL 复位与 PS 输出分开。原厂适配还将 HP2 RACOUNT／RCOUNT 及对应写计数固定为 0，不能凭这些计数判断 FIFO 为空。[互联实际配置](D:/FPGACompetitionProject/.local/hdmi-boot-witness-20261019-r23/reference/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_axi_interconnect_3_0/ps_ai_axi_interconnect_3_0.xci:277)
- 交叉互联为 S00 分配基础 ID 0、S01 分配 0x20，各线程 ID 宽 5。因此异常 RID=0x20 会自然路由为 S01 RID=0；这解释返回去向，不能反推出 HDMI 曾发 AR。[ID 配置](D:/FPGACompetitionProject/.local/hdmi-boot-witness-20261019-r23/reference/fpai_demo_vivado.srcs/sources_1/bd/ps_ai/ip/ps_ai_xbar_4/ps_ai_xbar_4.xci:2145)

上述证据不足以选择 FIFO 复位修复。应请官方明确 PS7 适配宏所对应 PL HP FIFO 的实例／转换层、复位输入、SAXIHP2ARESETN 覆盖范围及释放所需时钟／握手条件。现阶段不改 HDMI 消费端，不猜旧 A7 的私有 PS 复位寄存器。

## 2026-10-24 源码对照与异常传播验证

本节为捕获后的离线分析，没有新增 BOOT 写入、重启或 SDK／HDMI 负载。对照的是 r37 **实际综合输入**，而非仅按主分支同名文件判断：顶层覆盖文件位于 `.local/hp2-startup-protocol-20261023-r37/sources/`，实际 HDMI RTL 和原生 IP 来自 `.local/hdmi-boot-witness-20261019-r23/reference/`；原已适配参考基线位于 `.local/hdmi-jfm-build-20261016-r1/reference/`。这些目录均位于 `D:/FPGACompetitionProject`。

### 与原参考工程的连接关系

```text
AI HC0 ───────────────────────────── HP0
AI HC1 ───────────────────────────── HP1
AI HC2 ── S00 ─┐
               ├─ 原 HP2 AXI 互联 M00 ─ PS7 适配宏 HP2 ─ PS DDR
视频支路 ─ S01 ┘
AI HC3 ───────────────────────────── HP3

S01 的 AR／R：新 hdmi_board → HDMI reader／像素 FIFO → 新 TMDS 输出
S01 的 AW／W／B：仍接旧 frame_to_ps_largebuf 相机写通路
```

上图为逻辑连接，读数据方向为 PS DDR 经互联返回 reader。新 HDMI 接替原视频读显示通路，没有将新旧两个读主机直接并接。原 `frame_to_ps_largebuf` 保留，`CANDIDATE_SCANOUT=1` 关闭旧读请求／读使能／RD_START，并关闭旧显示 PLL／TMDS；旧读输出悬空，旧读返回输入固定 0。r37 源码中一处 “detached” 注释已过时，实际 S01 连接为接通，判断以端口连线为准。[实际顶层连接](D:/FPGACompetitionProject/.local/hp2-startup-protocol-20261023-r37/sources/ps_ai_peripheral.sv:866)、[新读显示入口](D:/FPGACompetitionProject/.local/hp2-startup-protocol-20261023-r37/sources/ps_ai_peripheral.sv:1048)

对照已适配参考，AI_Mate 的 **314 个端口连接全部一致**；HP2 互联、交叉互联、M00／S01 寄存切片、PS 配置和相应复位 IP 的参数值均一致。HP2 S00 给 AI、S01 给视频，是参考原有结构。原始发布包到适配参考已有的 `.hp_clk` 连接不能归因于此次 HDMI 修改。`demo_clkrst_wrapper.v` 与原始参考文本一致，HP 时钟仍取 PL MIG 的 DDR 时钟。

需要单独保留的已有差异是：HP2 PL 互联复位控制器的 `dcm_locked` 从参考常量 1 改为 `ddr3_init_done & ~ddr_ui_rst`，因此互联等待 PL DDR 就绪；这不是新增 AI 端口改接。PS_HP2_resetn、HP 功能复位及 PL 互联复位并非同一信号。[实际复位连接](D:/FPGACompetitionProject/.local/hp2-startup-protocol-20261023-r37/sources/ps_ai.v:3869)

### 最关键的 reader 行为差异

| 条件 | 原参考 aq_axi_master | 当前 hdmi_axi_read |
|---|---|---|
| RREADY 生成 | `RVALID & ~RD_FIFO_FULL`，不检查是否已发起读事务 | 仅 `state==DATA`，且允许接收或丢弃时置 1 |
| 未 START／空闲时出现返回 | FIFO 未满时仍可能握手接收 | 不接收，保持 RREADY=0 |
| FIFO 写使能 | `RD_FIFO_WE=RVALID`，该表达式未限定实际握手 | 仅 DATA 状态、实际握手且响应正常时写入 |

依据：[原参考读主机](D:/FPGACompetitionProject/.local/hdmi-jfm-build-20261016-r1/reference/rtl/display/aq_axi_master.v:426)、[当前实际 reader](D:/FPGACompetitionProject/.local/hdmi-boot-witness-20261019-r23/reference/rtl/hdmi_candidate/hdmi_axi_read.v:30)。这说明旧读主机**可能掩盖异常返回**，不能证明原参考板测实际发生过同样异常，也不意味着旧 FIFO 永远不会满。

当前控制器复位为 `running=0、stopping=1、frame_active=0`，必须收到有效 START 才产生读请求；reader 仅 ADDRESS 状态产生 ARVALID。r37 首次异常时 HP_reset 仍为 1，HDMI 内存域仍复位；FCLK_RESET0_N 和 AI pl_rst_n 也为 0。结合 AR 计数及连续样点，正常 HDMI／AI 业务请求无法解释这个异常起点。TMDS 输出亦不驱动该 PS 返回信号。[读帧控制](D:/FPGACompetitionProject/.local/hdmi-boot-witness-20261019-r23/reference/rtl/hdmi_candidate/hdmi_scan_control.v:42)

### 实际互联的定向故障注入结果

使用 r37 实际 HP2 fabric、同一参考的四个原生 IP 功能网表，以及实际 HDMI 控制器和 reader，向 PS 边界**人为注入**持续 `RVALID=1、RID=0x20、RRESP=0、RLAST=0、RDATA=0`。两源 ARVALID 始终为 0，未发 START；异常在 PL 互联释放前已存在。每种条件观察 128 个 HP 周期，另设有界仿真终止条件。编译、展开和仿真均完成，原生返回码均为 0，无 Fatal，测试通过。

| 接收条件 | PS 边界被接受的拍数 | S01 被接受的拍数 | 观察末状态 |
|---|---:|---:|---|
| 当前 reader 保持空闲 | **6** | **0** | PS_RREADY=0，返回缓冲堵住 |
| 改用旧 RREADY 公式，假定旧 FIFO 未满 | 125 | 122 | PS_RREADY=1，持续消费注入数据 |

第一种条件的 PS 握手出现在相对周期 **3、4、5、6、8、9**，S01_RVALID 首次出现在周期 **7**。将周期 1 对应实板 PL 复位释放的 11588729，逐点对应实板 **11588731～11588734、11588736～11588737**，以及 S01 首次有效的 **11588735**，包括中间暂停的一拍。

因此，**6 拍现象与实际 PL 返回缓存填满的过程完全相符**；寄存切片及交叉互联内部返回流水／skid 存储足以产生该现象。不能将“6”解读为 PS 内部 FIFO 深度、6 个请求或 6 个合法完成事务。第二种条件只隔离比较旧接收公式，没有模拟完整旧视频 FIFO 和屏幕消费。

该仿真验证异常出现后的传播机制，**没有模拟或解释 PS 适配宏如何产生最早的 RVALID**，不能代替新板测。测试源码、原生命令和结果保存在本节对应的 `analysis-orphan-return/` 证据中；原始 r37 实板数据及已整理 ZIP 未改写。

### 原因排序与下一步判别

1. **优先检查 PS7／PL HP 适配边界的启动初始化、复位覆盖和接口使能次序。** 首次异常早于 FCLK／AI／HDMI 功能复位释放，原生规则 58／59／61 随后出现。可见文本把 RVALID 从 PS7 宏直接接出，但宏内部实现不透明；目前不能进一步唯一归因于硬 PS、FSBL、PL FIFO 或具体寄存器。
2. **复位范围不一致是明确线索。** PS_HP2_resetn 比 PL 互联释放早约 **56.2316 ms**，其间 HDMI 功能复位先释放、互联继续等待 PL DDR。差异需要与原厂接口契约核对；仅继续推迟 PL 互联释放、或将已经为 1 的 PS resetn 再相与，并不能消除更早出现的异常返回。
3. **软件重启时未覆盖的适配层状态仍是候选。** 本次未做断电冷启动，也没有配置前／停钟历史的逐拍覆盖，不能认定存在历史事务，更不能认定其已被清空。应先明确同一 BOOT 的软件重启与冷上电是否要求不同的初始化／隔离顺序。
4. **新 reader 的空闲背压是已经复现的后续传播因素。** RID=0x20 按原配置被路由到 S01，本地 RID 变为 0，与新 HDMI 合法 ID 相同。若带着残留返回进入新读事务，仅靠当前 RID 检查无法区分新旧数据；这是源码可见的污染风险，本轮没有启动读帧验证它。S01 堵塞也可能阻塞共享 HP2 的后续返回，但本轮没有 AI 业务，不能称为实测推理死锁。

AI／HDMI 同时争用带宽、两个视频读主机并接、TMDS 编码或像素时序均不能解释本次“业务未启动、复位未释放时的第一个 RVALID”。现有证据也不支持用扩容 FIFO、删除旧模块或空闲强行拉高 RREADY 作为根因修复；后者可能只消耗并掩盖无主返回。

下一项最有区分力的工作，是请官方对应 **030ai／AArch64 的实际 PS7 适配实现**给出 HP PL FIFO／转换层的复位输入、SAXIHP2ARESETN 覆盖范围，以及配置／软件重启时的隔离和释放条件；再选择明确的复位方案或同位流冷／暖启动对照。保持 AI 四路，现阶段不盲改 HP 端口、旧 A7 私有复位寄存器或 HDMI 接收策略。本轮 r37 保持关闭。

## 2026-10-24 启动边界、固件与裁剪收益的进一步定位

本节为离线读取实际布线检查点、原 BOOT 对应 AArch64 FSBL 及现有实测样点的结果。没有新增板端寄存器访问、BOOT 写入、重启、SDK／HDMI 负载，也没有改变 RTL、AI 四路、频率、约束或位流。

### 本轮不裁剪的原因

裁剪有资源和维护收益，但未发现能直接消除最早 RVALID 的证据。已有 r24 实际资源审计中，旧视频加 adder 候选合计 3343 LUT、4548 FF、18.5 个 BRAM36 等效量和 6 DSP；这只是旧版本的静态资源归属，不是 r37 删除后的实现预测。旧 `frame_trans` 仍提供共享 `soft_rst` 和 SDK 寄存器响应，不能整块删除；旧 SDI 时钟／LED 和 adder 的寄存器／DDR 连接也需保留依赖。部分无用计数逻辑已被综合优化，删源码不会再省资源。

r37 已有时序合格位流，首次异常又早于业务模块解除复位。此时裁剪会同时改变复位依赖、拓扑和布局，妨碍比较。因此本轮保持模块和 AI 四路连接，集中核对 PS7／PL HP 适配边界。资源审计仍以既有 `FPGA/hdmi_candidate/R24-RESOURCE-AUDIT.md` 为准。

### 实际布线网表给出的边界

复用 r37 的完整布线检查点进行小范围只读查询，原生工具返回 0：

- `SAXIHP2RVALID` 的唯一驱动是原厂适配 **PS7 实例的同名输出**，没有来自 HDMI、旧视频或 AI 的另一个 PL 驱动。
- `SAXIHP2ARESETN` 也是该实例输出，实际只有 5 个观察／诊断接收点；它没有直接复位 PL 功能互联。PS 的 ARVALID 输入由 M00 地址寄存切片驱动，RREADY 输入由 M00 返回寄存切片驱动。
- `SAXIHP2ACLK` 与适配宏 `AI_CLK102` 接同一个 MIG 时钟 BUFG。原有 `HP_reset` 的两级链是时钟采样的 FDRE，异步复位脚没有接该复位请求；因此不能把它描述成已验证的异步置位复位器。
- 最早异常的原始连续样点里，`DDR_ui_reset=0` 而 `DDR_calibrated=0`；到 PL 互联释放窗口，前者仍为 0，后者为 1。**尚未校准不等于已证明 HP 时钟不稳定**；本次没有直接测量时钟电气稳定性。

上述结论只把最早异常的可见源头限定到适配宏输出，不穿透宏内部，不足以指认其中某个硬 PS 单元或 PL FIFO。

### 从实际 FSBL 恢复出的配置完成顺序

所查文件是原 BOOT 使用的 `FSBL251210_ddr400_demo.out`，不是旧 A7 示例，SHA-256 为 `5501c470e07537a8fb369ae40641c20c16ab403fad558e65e0a4bbf380f2396f`。r37 保留原 BOOT 的非 PL 内容。以下是实际 AArch64 指令的静态正常路径，**不是板端指令时间戳**；地址和值可信，寄存器的芯片专属语义仍待确认。

| 阶段／函数 | 实际操作 |
|---|---|
| `SystemInit` → `OpenPlPorLevelShifter` | 向 `0xe0026844` 写 `0xf`；这不是后面的接口开放函数 |
| 加载位流前，`FDevcPs_Prog_B` → `CloseUsrLevelShifter` | 先向 `0xe0026264` 写 `0xf`，再向 `0xe0026838` 写 `0` |
| 等待配置完成，`FDevcPs_pollFpgaDone` 的成功分支 | 指令 `0xfffd4804` 向 `0xe0026838` 写 `0xf`，随后 `0xfffd4810` 向 `0xe0026264` 写 `0`；两项与 `OpenUsrLevelShifter` 的操作一致 |
| 紧接上述两项 | 指令 `0xfffd4818` 调用 `delay_ms(10)` |
| 延时后 | 依次读 `0xe0029490`、`0xe0029540`、`0xe00295f0`、`0xe00296a0`；每个地址均为**整字等于 1 才写回 1，否则跳过** |

相关路径包含对 `0xe0026008`／`0xe0026004` 的解锁／锁定写入；没有改写或执行这些寄存器操作。四个延时后地址也出现在实际 DDR 初始化表中，各以掩码 1 写值 1；接口的两个地址不在这五张初始化表内，由上述函数控制。

这排除了“FSBL 完全没有配置完成后接口开放动作”这一简单解释，但**没有证明 HP 复位覆盖充分或顺序正确**。尤其四个条件写看不到 0→1 复位脉冲；若它们是普通使能位，重复写 1 不等于复位；若它们具有写命令或自清除语义，则必须按匹配版本手册解释，不能凭反汇编猜测。

ELF 调试信息将相关实现定位到原厂源码单元 `FM_QL_bsp/libsrc/devcps_v1_0/fmsh_devc.c` 的 `FDevcPs_pollFpgaDone`，以及 `FM_QL_fsbl/fmsh_sac.c` 的 `OpenPlPorLevelShifter`／`OpenUsrLevelShifter`／`CloseUsrLevelShifter`。这是 ELF 内记录的源单元名称；本机尚未找到这些匹配版本的可读源码，不能将记录中的原开发机路径当成本机可用路径。

### 对最早异常的判断如何收窄

**优先核实“接口开放时，HP 适配逻辑是否已经完成有效复位”**。实际样点中 PS_HP2_resetn、ARREADY、AWREADY、WREADY、RVALID 同拍变高，而 FCLK_RESET0_N 仍低，36 个 HP 周期后才变高；HDMI／AI 均尚未解除功能复位。FSBL 又确实存在配置完成后先进行接口开放、随后进行其它条件写的路径，两者构成值得优先核对的对应关系。

但不能直接把 `0xfffd4804` 与 HP 周期 342409 对齐：还缺 CPU 写操作到接口可见信号的实测关联和寄存器定义。**接口隔离解除，使原本不可见的电平同时显露**是一个候选解释；“HP 真实复位释放时生成了异常返回”是另一个候选解释，目前不能二选一。由此，外露 `PS_HP2_resetn=0` 也不能单独证明宏内部 HP／FIFO 一直处于有效复位；其为隔离钳位输出的可能性尚未排除。

若这是软件重启后的未覆盖状态，应该进一步区分本次配置前就存在的返回、配置过程中形成的状态和解除隔离时的错误释放。当前证据不能证明任何一项。原始监测仍只覆盖有效 HP 时钟下的本次监测期，配置前及停钟区间不在观测范围。

PL 互联迟约 56.2316 ms 释放，解释了为什么异常先停留在 PS 边界，随后才被接受 6 拍并堵在 S01；它不能反向解释更早的第一个 RVALID。新 reader 空闲背压的传播作用已有定向仿真支持，不能用空闲吞数据替代对初始化／复位的修复。

### 需要原厂明确的最小接口信息

目前缺口已收敛为下列可直接对应源码的问题，而非笼统询问“PS 怎么复位”：

1. 针对 **030ai／AArch64、FSBL 4.51**，确认上述 `fmsh_devc.c` 配置完成路径和 `fmsh_sac.c` 是否为正确版本；`0xe0026838` 与 `0xe0026264` 分别控制什么，先后顺序及等待条件是什么。
2. `0xe0029490／9540／95f0／96a0` 是使能位还是复位／刷新命令？为何条件是整字等于 1 才写 1？对软件重启后重新配置 PL，是否需要其它明确操作。
3. `SAXIHP2ARESETN` 在接口关闭时是否被钳位？它是内部 HP 复位状态、独立输出复位还是其它含义？官方所说的 PL HP FIFO 位于适配链哪一层，由什么信号复位，需要多少有效 HP 时钟以及怎样的释放顺序。

本机已安装工具包含 `ps7p` 的 BSP／FSBL 模板，但已查到的 BSP 设置工具只改已有工程的路径索引，明确不生成驱动且不支持 FSBL；现有手册未给出可确认的独立 Export Hardware 命令入口。没有安装或升级工具，也没有把旧 A7 驱动当作当前寄存器定义。

取得这些定义后，才有依据选择有界的初始化修正或接口开放前后观察；如需改启动固件，将先形成具体可审查补丁及恢复方案。当前不套用旧 A7 地址，不新增私有寄存器写，不为同一未知边界盲目重跑候选。AI 四路保持，原 BOOT 的最后已验证恢复状态不变，r37 继续关闭。

## 实际离线验证

使用既定 Vivado 2018.3／复旦微适配器件库，目标 `xc7z030ffg676-2`，后续 Procise 使用 `JFMQL30TAI676H`。未更换器件库、频率或放宽门槛。

| 检查 | 实际结果 |
|---|---|
| 完整布线 setup／hold | WNS **+0.030 ns**，WHS **+0.010 ns**，TNS／THS 均 0 |
| 布线完整性 | **111,767／111,767** 根可布线网络完成，错误 0 |
| 原有 AI 最小周期例外 | 仍为既定两处，裕量 −0.409／−0.071 ns；`raw_timing_pass=false`，现行位流生成门检通过 |
| 原始标志采样 | 20 个实际端点，5 ns 约束，最差裕量 +0.606 ns |
| 连续采样器状态／描述符 | 4／156 个端点，5／10 ns，最差裕量 +2.543／+6.674 ns |
| 协议采样器状态／保留总线 | 7／462 个端点，5／10 ns，最差裕量 +1.682／+6.489 ns |
| PS 复位输入观测 | 5 ns，最差裕量 +0.861 ns |
| 覆盖及偏斜 | 内部无未约束最大延迟端点、无无时钟寄存器；总线偏斜无违例 |
| DRC | 原报告仍保留既定 GT 范围内的 REQP-52／REQP-56 两项 Error；复用已批准的限定处理，未新增错误范围或豁免 |
| 仿真 | 10 项原生 IP 定向用例、5 项触发／快照用例通过；旧连续采样及解码兼容验证通过 |

发现并修正两项物理问题：旧跨时钟例外覆盖了新增诊断起点，现仅移除新增诊断起点对应的覆盖，不新增 false path，并逐项确认状态／原始标志端点的 5 ns 约束生效；一根诊断 BRAM 控制网有天线残段，局部重布后完整布线错误清零。两次范围展开造成内存压力的检查及一项范围可能扩大的表达均未采纳，原失败结果保留；最终采用的是小范围起点修正。

测试中曾出现原生退出码为 0 但含 Fatal 的结果，已判为失败。修正测试对 GP 复位后 CSR 重新发布的等待后，实际重跑通过，并验证了相邻周期不同单拍状态、完整 160 位状态和 64 位周期的保留；未将旧失败改写为通过。

## 已生成产物及源码

源码基线为 `6494ff45c5923d2abc45a88de6a743e87902d6f8`，位于独立分支 `codex/hdmi-s01-isolation`。本轮源码改动已提交，主工作区其它任务的改动保持。

- 采样器源码：[hp2_protocol_trace.sv](C:/Users/cenyongdong/.codex/worktrees/hdmi-s01-isolation/FPGACompetitionProject/FPGA/hdmi_candidate/diagnostics/hp2_protocol_trace.sv)。
- 约束修正：[hp2_existing_cut_scope.tcl](C:/Users/cenyongdong/.codex/worktrees/hdmi-s01-isolation/FPGACompetitionProject/FPGA/hdmi_candidate/constraints/hp2_existing_cut_scope.tcl)。
- 实际使用的布线检查点：[pipeline-repaired-routed.dcp](D:/FPGACompetitionProject/.local/hp2-startup-protocol-20261023-r37/pipeline-repaired-routed.dcp)。
- 原始 Vivado bit：[ai7030_edif_top.bit](D:/FPGACompetitionProject/.local/hp2-startup-protocol-20261023-r37/fpai_demo_vivado.runs/impl_startup_protocol_r37_pipeline/ai7030_edif_top.bit)，SHA-256 `d8762067908f8fa72d2b2c4aebe3f85495b6511d6519e7537ce286e35853e490`。
- 适配后板用 bit：[ai7030_top_disable_icap.bit](D:/FPGACompetitionProject/.local/hp2-startup-protocol-20261023-r37/boot-package/ai7030_top_disable_icap.bit)，SHA-256 `1f7f3a4162266330147eb1ba0f4dbf1e94318ee5ea7f29dbbaf64aba23d53fed`。
- 启动包：[BOOT-hp2-startup-protocol-r37.bin](D:/FPGACompetitionProject/.local/hp2-startup-protocol-20261023-r37/boot-package/BOOT-hp2-startup-protocol-r37.bin)，7,023,552 字节，SHA-256 `58ae22619bc8459b0a795989ca5c7025cf941d82c588a4895ea037c2dff3327c`。

BOOT 内 PL 载荷换序对照通过，PL 以外字节及填充与原 BOOT 一致；FSBL、BL31、U-Boot 均保持。上述位流已实际启动并捕获异常，不能记为 HDMI 显示或 AI 联合功能通过。

## 已完成的安全恢复与后续

本轮执行 **候选启动 1 次、原 BOOT 运行回退 1 次**。首次故障取消第 2 次候选，r37 已关闭，所有余额 0；未重试业务负载。原 BOOT SHA-256 `ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`，最终运行 ID `38d16aa9-2569-4bcd-8468-fece968ff7bb`。9 个启动文件及 6 个 SDK 库身份核验通过，设备占用为空；两次 COM7 只读采集均已关闭、发送字节为 0，未留下后台采集或 EDA 作业。原有 FAT 问题保持，不进行文件系统修复。

下一步先用本次失败样本核对原厂 PS／PL 适配层和复位契约，保持 AI 四路，避免在启动异常未解释时继续 SDK／HDMI 联合负载。r37 不追加启动；断电冷启动、功能复位改接或端口架构调整均不能由本轮数据直接代替设计论证。旧 DATA 独立暂停，HDMI 长期验证未开展。

可直接交给官方的本地整理包：[HP2_STARTUP_PROTOCOL_r37_20261024.zip](D:/FPGACompetitionProject/tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/HP2_STARTUP_PROTOCOL_r37_20261024.zip)，439,459 字节，SHA-256 `88d747e007073075597e82cf65819bc6fe22bebe474e144153425e5e9452f6ba`；含三幅真实波形、完整 CSV／VCD、原始数据及采样／解码源码，尚未对外发送。
