# r25：同r24位流的无按键启动对照（首例异常，包已关闭）

r24已完成一次健康启动、正确SW6实际HP2复位和按键后Open，已回原BOOT并关闭。缺口是：尚未验证不先按SW6时能否直接Open，也没有新候选的重复启动样本。[上一包实测与耗时](../hdmi-hp2-ready-20261020-r24/PLAN.md)。

本包复用已实测r24的同一BOOT，不重编HDL、bit或模型，不改SDK／数学／协议。BOOT SHA256仍为`a0ed66d07ba05d80c3d0188d93afda1036a9c7df212ce9badb74b229c61e3e49`；资格与唯一产物身份复用[r24门检](../hdmi-hp2-ready-20261020-r24/qualification.json)、[封装](../hdmi-hp2-ready-20261020-r24/package-review.json)。

最多3次候选安装／启动，每次最多1次库加载／Open；全包最多1次原BOOT回退。不含任何SW6／SW7按键、DMA、推理、HDMI START或长期验证。

1. 每次SSH恢复后先恢复原BOOT文件并完整读回，再无SDK采0→2及同一冻结的启动历史。前置五寄存器不满足初态或遇其它异常时保存原值、停止，不重试。
2. 仅纯CSR健康、启动历史中有实际HP2复位断言和正脉宽、计数无相关溢出、没有未解释的ready路径先返回后请求，才直接执行一次库加载／Open／空闲／Close与卸载；不先按键，不追加额外CSR清零。
3. 本次软件阶段及最终历史均通过，才可进入下一次候选；任何一次异常立即停止后续候选和SDK负载，不重试失败负载。每次Open最多1次，全包最多3次；原BOOT文件始终先恢复，再开始该启动的观测。
4. 第3次完成或首次异常后，最多1次原BOOT回退，审计原运行、SDK／启动文件及无占用后关闭所有额度。此处最多3次是热重启样本，不代表冷上电、统计可靠性、DMA／推理或长期HDMI验收。

执行程序最初以inactive放置板端`/root/hdmi-startup-stability-20261020-r25`。共享观察代码沿用r24默认流程，新增明确的无按键入口；3次顺序由独立控制器负责，复用原BOOT写入／读回实现、原观测器及原SDK子进程。启动命令前有独占持久化记录，工具超时不得重发。每次结果分别位于run-1／2／3，前次通过是下一启动的硬前提。

[配置](deploy/config.json)、[已关闭授权](deploy/authorization.json)、[控制器](deploy/startup_stability_board.py)、[共享观测](deploy/reset_key_board.py)。入口由代理执行：`startup_stability_board.py prepare/install/candidate-reboot/restore/probe/software/fallback-reboot/close --cycle N`。本包后来已确定并执行，当前已关闭；准备和语法检查不算实际启动通过。

[板端未启用校验](inactive-guard-and-transfer-check.log)已确认：同一原BOOT运行身份、无owner、候选SHA匹配；未批准执行被阻断、样本0／4被拒绝、缺少前次通过记录时不能继续。没有访问CSR、加载SDK、写启动分区或重启。当前状态与余额仅见[state.json](state.json)。旧DATA仍独立暂停，FAT不修；本任务不接入Vivado MCP。

## 实际执行及结论（2026-10-20）

批准最多3次候选启动，实际第1次无SDK即复现既有故障，依包约定取消第2／3次及全部SDK阶段。实际消耗：候选启动1、原BOOT回退1；按键、SDK加载／Open、DMA、推理、HDMI START和长期均0。原始板端证据一次回传为[evidence-r25-20261020.tar](evidence-r25-20261020.tar)，包括完整原生输出、过程记录及最终审计；原失败没有重试。

候选运行ID `f7e3af86-a439-4beb-895a-fc82f4bd4e46`。SSH恢复后先恢复并完整读回原BOOT的7,023,552字节，再进行一次纯CSR观测及同一FREEZE的只读历史读取；无按键、无SDK。完整解码见[cycle-1-decoded.json](cycle-1-decoded.json)。

| 实测对象 | 原值／结果 |
|---|---|
| 初始五寄存器 | ABI 0x41495201、104字、status／request／response均0 |
| 纯CSR窗口 | 4,018,538个source周期，flags=0x19，复位周期0；六边界ARVALID／AR握手／R握手均0 |
| 返回背压 | PS边界及HDMI边界RVALID、R背压均占满窗口；当前PS RID32、HDMI RID0，RRESP均0 |
| 启动历史 | PS／HDMI AR累计均0；PS原始R握手6、HDMI原始R握手0；计数无相关溢出 |
| 首次ready路径RVALID | 观察到AR之前已返回标志为true，PS RID32、RRESP0；首事件周期模2³²=11,658,424 |
| 实际复位见证 | GP合并复位断言0；HP2侧PL互联复位断言1，低电平5,657,425个GP周期（100MHz名义值下56.57425ms） |

事实：补齐DDR就绪门后，启动阶段已有HP2侧PL互联复位，本次仍在SDK加载前复现同类故障。故Device::Open不是该故障出现的必要条件；“未发生PL互联复位”也不能充分解释本次故障。PS原始6次R握手含复位期采样，不能称为6笔合法事务。首事件仅有32位模值，本次总source周期已超过一次回绕，不能把11,658,424直接换算为配置后绝对时间，或与GP复位宽度相减。

未知：当前见证不是PS内部FIFO复位，无法区分PS端残留／初始化、两侧复位与时钟释放先后或可观测source时钟之前的活动。静态复核原生成PS模块确有输出`S_AXI_HP2_ARESETN`（并非输入），它没有纳入现有19字历史；`RCOUNT[7:0]`／`RACOUNT[2:0]`已从生成BD引至peripheral，但也未进入本次快照。其有效性与复位语义须按复旦微实际资料确认，不能直接套用通用Xilinx寄存器。下一诊断重点是PS端复位／FIFO状态与PL互联就绪释放的先后证据；不继续盲目重复同包启动，不盲写PS复位寄存器，不把延长PL复位当作已证修复。没有生成新位流或启动新包。

结束：已使用唯一批准的原BOOT回退，原运行ID `056656a3-abb3-4b45-888f-18b9658fe3b7`；原BOOT文件SHA及六SDK／九启动文件符合保护身份，FPGA operating、owner为空。授权已关闭且所有余额0，见[最终审计](final-audit.json)及[状态](state.json)。旧DATA仍暂停，FAT不修，HDMI长期未批准。

耗时：主机批准记录至close日志约122.3秒（14:05:20→14:07:22，含本机协调和启动等待），没有EDA重编；板端跨启动时钟不连续，不能用tar内板端mtime推算整包耗时。

后续离线更正：RCOUNT／RACOUNT虽从生成封装引出，但原厂适配已将其固定为0，原语同名引脚复用于NPU数据；本页将其列为待考察方向不构成有效FIFO占用来源。真实PS复位输出与下一轮方案见[r26](../hdmi-ps-release-20261020-r26/PLAN.md)。本次r25的全部原值与实测结论保持。
