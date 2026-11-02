# Vivado 现成 IP → Procise：可行性分析

日期：2026-10-01；目标为悟净 Lite / JFMQL30TAI676H；Vivado 2019.1，Procise 2025.1.1 temp / SVN 32494。结论为**有条件可行，须按 IP 的实际输出与依赖分别验证**。本文第 1–7 项保留实施前的分析依据与只读预检状态。 xlconcat 最小方案，真实 IP 生成、同一综合源码 XSim、Procise 原生综合/位流、JTAG 与实板观察全部通过；最新事实和证据见 [RESULTS.md](RESULTS.md)。不将后续结果推广为所有 IP 可用。

## 已验证事实与资料依据

1. Vivado MCP 是操作 Vivado 的入口，IP 来自本机 Vivado/IP 仓库；MCP 不转换器件原语、加密库或约束。此前使用 MCP 写入自写 RTL、经 XSim 验证并由 Procise 实现/上板成功，不含现成 IP，不能直接作为 IP 适配证明。
2. [AMD Concat 产品说明](https://www.amd.com/en/products/adaptive-socs-and-fpgas/intellectual-property/xlconcat.html) 将其定义为总线拼接 IP。本机 `xlconcat_v2_1/component.xml` 的 **behavioral simulation 与 Verilog synthesis fileset 指向同一份** `hdl/xlconcat_v2_1_vl_rfs.v`。变更日志为 2019.1 / v2.1 Rev.3，模块为 `xlconcat_v2_1_3_xlconcat`；源码未加密，静态检查为参数化 generate/assign 拼接，未识别到器件原语或下层模块例化。
3. 该源码 SHA-256 为 `bf101401b966e7c7121bd17b0099f468f8e5fb15a376ac2e747885cdafd86689`。这支持以它为最小 RTL 交接候选的推断，**尚不是 Procise 编译成功或实板成功的结论**。实际生成的包装器及完整源码闭包还须审核。
4. 本机 `c_counter_binary_v12_0_vh_rfs.vhd` 开头是 `protect begin_protected` 等受保护源码。本轮未验证 Procise 对该加密格式、语言及底层库的支持，不能把它当成可见的通用 Verilog 源码直接输入。
5. 30TAI 使用教程（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/30TAI使用教程.pdf`） 第 2/5/6 页设计要求 IP OOC 综合、JFM hook、`replace_7z030ai_file`，参考版本为 2018.03。已核对文字与第 5 页截图；教程的迁移流程不能写成“IP 在 Vivado 只生成/仿真，然后 Procise 原生综合全部 IP”。
6. 本地 JFM 包含 2018.3、2019.2 等数据库/脚本目录，本轮检索到的 2019.x 版本子目录只有 2019.2；没有得到该包与现有 2019.1 的完整迁移兼容证明。未加载 `run.tcl`、安装补丁或修改器件数据库，也不要求安装 2018。
7. 当前工具会话 MCP 独立 Tcl 会话已启动 2019.1，`get_parts` 确认 `xc7z030ffg676-2` 存在，可作为候选 IP 前端工程的元数据目标；物理器件仍以 Procise 的 JFMQL30TAI676H 为准。无工程会话 `get_ipdefs` 查询为空；因此目前只确认安装文件存在，IP catalog 创建/生成仍待新方案实施，不据空结果判定缺少 IP。会话已关闭。

实际 MCP 返回及静态来源记录见 [preflight.json](preflight.json)。[UG896 的脚本示例](https://docs.amd.com/r/2021.1-English/ug896-vivado-ip/Scripting-Examples) 说明 XCI、输出产品、DCP 和仿真/综合设置之间的关系；该官方网页为 2021.1，本文仅用其解释文件职责，2019.1 的实际命令与生成结果须在本机核对。

## 分类型判断

| 输入/资源 | 所需条件 | 当前判断 |
| --- | --- | --- |
| 自写纯 RTL、可读且不依赖器件原语的软 IP 综合源码 | Procise 支持其语法；完整模块/参数依赖；用实际源码仿真、综合和上板 | 自写 RTL 已通过；后续 xlconcat 四端口配置亦已实板通过，其他核/配置仍需实测 |
| FIFO、BRAM、DSP、Clocking、I/O 等包含厂商原语的 IP | 核对原语、参数、初始化、时序/复位语义、对应复旦微资源与约束；原生替代或厂商支持的转换 | 逐核适配；不能因接口相同就直接采用 |
| 加密源码、只给网表的 IP | 工具/密钥/语言/库与版本兼容，或厂商提供的替代及迁移流程 | 本轮未确认，不能泛化支持 |
| XCI、BD | 工程配置/连接描述，须生成可综合源码或使用受支持的迁移流程 | 不作为 Procise 原生 RTL 输入直接替代实现 |
| DCP、funcsim/stub 文件 | DCP 是 Vivado checkpoint；stub 只有接口，funcsim/行为模型不一定是实现源码 | 不能据它们可仿真就认定可原生综合成硬件 |
| JFM 的 OOC/EDIF 迁移 | 精确工具版本、30TAI 映射、补丁、约束和专用步骤 | 资料证明存在这一路径；当前 2019.1 完整路径未验收，且包含 Vivado 前端综合 |

## 建议的最小验证及解释范围

以真实 `xlconcat` 配置 4 个 1-bit 输入，参与灯状态下一步的组合拼接，实现与旧灯序相同的 LED1→3→2→4→1；保持已验证引脚、电平、100 MHz 和 0.25 秒步长。由 Vivado MCP 配置/生成 IP、写入 RTL、运行实际综合源码的 XSim，再把包装器与 IP HDL 交给 Procise **原生综合**、布局布线、位流复核和经明确授权的 JTAG 下载。

收益是以简单源码核验“真实现成 IP 输出 → 同一源码仿真/实现 → 实板”的交接，成本是新工程、IP 参数/文件清单和复核维护。Concat 最终可能优化为连线，代表性有限：不能据一次成功推广到计数器加密 IP、FIFO/BRAM、Clocking、DMA、HDMI 或 AXI 系统。若希望直接验证更接近项目负载的 IP，需另行选择具体核并讨论其适配与接口。

完整实施范围见 [PLAN.md](PLAN.md)。按 AGENTS.md 先讨论并取得具体方案同意后，已建立独立工程实施并完成实板确认，原已验证工程保留；具体结果见 RESULTS.md。此批准仅覆盖本次 xlconcat 试验，后续其他 IP、配置或迁移路径仍须讨论。
