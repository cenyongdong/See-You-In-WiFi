# 原厂整机实现后的AI时钟门检

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

2026-10-16更新：已明确特批下述两个Min Period检查，解除该项HELD，允许受控实板测试；原始时序失败及尚未验证的语义保留。[现行定点豁免与发布状态](BOARD-RELEASE-20261016.md)。下文为豁免前的门检事实及停止依据，其中“不得新增豁免／HELD”的旧决策已被本次定点授权更新，其余范围不扩展。

2026-10-16，原厂Vivado2018.3＋JFM构建及Procise ICAP后处理已实际生成参考位流，完整时序门检未通过。本页记录停止上板的依据；不把已有板测授权取消，也不以此恢复旧DATA调查。

## 已验证事实

新独立实现impl_r2用时1173.647281秒、工具exit0。之前含IP综合的完整链在1800秒外层上限处停止，当时已完成布局、进入布线，日志无ERROR；现场独立封存。新实现复用已完成综合，新旧实际生成Tcl的差异仅为报告对象名称，原策略、约束、输入和hook一致。

| 检查 | 实际结果 | 判断 |
|---|---|---|
| Setup | WNS=0.030ns，TNS=0，失败端点0 | 通过该项，裕量很小 |
| Hold | WHS=0.021ns，THS=0，失败端点0 | 通过该项 |
| 最小周期（Pulse Width Checks中的Min Period） | WPWS=−0.409ns，TPWS=−0.479ns，失败端点2 | **不通过**；总时序摘要明确Timing constraints are not met |
| 时钟/内部约束覆盖 | no_clock=0，内部max-delay未约束端点0 | 仅该范围通过 |
| 外部时序 | HIGH级未设input delay 11、output delay 6 | 未完成接口逐项解释，不能称全约束覆盖 |
| CDC | Critical报告条目12,822 | 尚未逐项闭合；报告条目不是独立硅上故障数 |

两处违例同属clk_out1_AI_CORE_CLK_ST，报告周期1.000ns：BUFG/I要求1.409ns，裕量−0.409ns；PLLE2_ADV/CLKOUT0要求1.071ns，裕量−0.071ns。汇总数值存在打印精度，使用原报告，不用四舍五入后的单项强行回算总和。

原始AI_Mate.edif中已存在AI_CORE_CLK_ST，PLL参数输入周期5ns、反馈倍频5、输出分频1。实际路由检查点只读查询确认该PLL输出到BUFG，BUFG可见叶负载为ai_core_clk_locked_reg/C。这是网表可见连接；**不能据此推定实际硬核完整时钟分配，亦不能宣称芯片不能或能够在1GHz可靠工作**。是否为特定硬核的占位/保活结构及其正式时序适配语义，仍待验证。

该违例来自原厂参考AI时钟模型，未接入本项目HDMI候选；不能归因于HDMI字符串常量修复，也不能为修复HDMI擅改固定AI_Mate或NPU频率。

## DRC上下文须分开

实际实现会话的路由DRC列出99项Warning/Advisory、无Error，CHECK-1明确只有REQP-44/46/52/56被关闭；两个RAM异步控制检查触及单规则20项显示上限，99不是无截断的全量故障总数。实际GT为一个GTXE2_CHANNEL及一个GTXE2_COMMON，均在原SDI层次。

在另一个Vivado会话复开DCP后，DRC启用状态恢复默认，REQP-52/56再次出现为Error。这份未恢复原厂规则配置的诊断报告与实现会话的DRC分别保留，不能据此抹去任一结果或扩展关闭其它检查。AI最小周期违例并未豁免，两种报告都不改变该门检失败。

MIG的CLOCK_DEDICATED_ROUTE=FALSE在原2018.3配置生成、尚未执行JFM hook的XDC中已经存在，限其200MHz CLK_REF到clk_ref_mmcm_gen.mmcm_i/CLKIN1；不是本次新增HDMI例外。实际030ai默认速度分支只复制zynq.lib/padr，已与现安装逐位核对相同；保留change_speed=FALSE没有替换成另一套速度模型。

## 本地资料核对范围和限制

核对了原厂受保护过程实际定义、原始AI网表、实现驱动/约束、实际PLL/BUFG属性及路由连接，并检索本地30TAI教程、FPAI_DEMO说明及板原理图。教程第5页已完整渲染核验，确认工具加载与目标版本；该页不构成1GHz门检豁免依据。原理图正文不能全文检索，本轮检索**不能证明所有本地资料都不存在相关说明**；本轮尚未得到针对这两个单元、该库版本的正式适配或例外依据。

## 自主决策及恢复边界

保持AI_Mate、PS/DDR参数、SDK、模型和既有频率；不新增最小周期豁免、不修改时序库数值、不降频来包装通过。参考位流及ICAP输出列为HELD，不生成/替换BOOT、不下载、不重启；HDMI候选接入和1080p60目标继续保留已有授权，但这些参考产物不代表候选已经完成。

下一步应首先核对硬核AI时钟的正式适配契约和外部时序/CDC报告中可归类的原厂结构，再确定候选完整实现的门检范围。取得可核验依据前，依赖完整时序验收的上板步骤保持停止；不要求仅为超时重新批准。不把本次时序/CDC诊断当旧DATA根因证据。不要用整体位流可生成、setup/hold为正、旧BOOT曾能推理等事实代替本次最小周期或CDC验收。

[完整本批报告](../../tools/pose-v1/evidence/hdmi-jfm-build-20261016-r1/REPORT.md)、[实际结果与边界](../../tools/pose-v1/evidence/hdmi-jfm-build-20261016-r1/result-review.json)、[只读时钟连接](../../tools/pose-v1/evidence/hdmi-jfm-build-20261016-r1/AI-clock-trace/actual-clock-connectivity.txt)、[完整CDC原值](../../tools/pose-v1/evidence/hdmi-jfm-build-20261016-r1/implementation-only-r2/CDC.rpt)。
