# 实时推理 → HDMI 阶段进度与暂停报告

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

记录日期：2026-10-18。执行位置：Windows `D:/FPGACompetitionProject`；本轮使用既有 Vivado 2018.3／JFM／Procise 适配链，未更换模型、SDK或工具版本。

**任务已整体暂停，实时推理 → HDMI 全链路仍未打通。** 此前只暂停现场观察；本次扩大为停止离线诊断、构建、部署和板测，等待独立执行许可。报告及交接记录完成后不留后台续作。旧 DATA 调查继续独立暂停。

## 已完成到哪里

| 环节 | 实际结果 | 验收边界 |
|---|---|---|
| HDMI读帧、显示与骨架渲染 | 历史两幅四色分区切换及三份真实输出骨架回放已确定；渲染字节、帧采纳及STOP后释放有证据 | 尚未完成“新推理结果实时驱动HDMI”的闭环；此前黑屏／首次START异常记录保留 |
| 固定共享模型与NPU | 原BOOT对照中，同程序四档DMA至1MiB及三窗新推理通过；原共享模型另有历史30分钟串行正确性验证 | 这些是原配置能力，不证明HDMI候选中的AI路径正常，也不证明持续实时RF输入 |
| HDMI候选中的故障隔离 | r5及观测v2均出现64B DMA通过、4KiB写SDK异常，退出71并停止；v2原错误与同Device快照已保存，随后回退原BOOT | 根因D45未查明；更大两档、候选中的三窗推理及HDMI联动未执行，不自动重试失败负载 |
| 新被动观测诊断实现 | 读路径观测RTL、ARM软件及Host控制入口已准备并做离线验证，保留固定模型／SDK／数学／分配／帧协议 | 新观测候选尚未形成可发布的r7位流／BOOT，未上板取到新故障现场 |
| r7最小HDMI修改 | 仅在隔离REF7调整reader在IDLE时清计数的位置；24组、5773周期、11378次严格比较全部116位输出通过 | 有限局部测试，不是全机器形式等价、最终时序通过或DMA根因修复；正式仓库reader及旧REF未改 |
| r7综合与完整约束 | 综合273.344秒、约束163.218秒，实际执行与正式门均通过；2768位快照全部10ns、最小余量+9.492ns，937源／41库身份符合 | 综合约束通过不等于布局布线后的STA／DRC通过 |
| r7布局／物理优化 | native实际完成place及phys_opt，生成44,437,238字节physopt检查点；父阶段1430.672秒exit1，非监控超时 | 原父阶段未通过，没有父导出检查点或phase-review；route、最终STA／DRC及r7 bit／ICAP／BOOT未执行 |

历史显示与联动故障见[HDMI显示报告](../../tools/pose-v1/evidence/hdmi-display-20261017-r1/REPORT.md)、[原BOOT对照报告](../../tools/pose-v1/evidence/hdmi-live-20261017-r1/REPORT.md)、[v2故障与回退报告](../../tools/pose-v1/evidence/hdmi-live-20261017-r2/REPORT.md)。本轮详细阶段证据见[r3报告](../../tools/pose-v1/evidence/hdmi-live-20261017-r3/REPORT.md)。

## 当前问题和卡点

### 1. 核心功能故障仍是D45

原BOOT中的DMA／三窗推理可通过，加入HDMI的候选却在4KiB写入时抛SDK异常。现有证据把问题范围缩到候选集成配置与AI传输路径，但还不能确定具体RTL、互联、时钟或运行时原因。没有证据证明骨架渲染本身导致故障，也没有完成修复验证。

下一轮原本需要新增被动读路径观测值来缩小范围；因为该观测候选尚未完成物理实现和发布门检，目前没有新增板端数据。参见[难点D45](../../DIFFICULTIES.md)及[完整诊断证据](../../tools/pose-v1/evidence/hdmi-live-20261017-r3/REPORT.md)。

### 2. 候选发布先后被物理时序与校验脚本阻断

r5完整物理报告存在9条HDMI `next_addr → received` setup违例：WNS −0.137ns、TNS −1.226ns。r6一次物理优化后仍为WNS −0.085ns、TNS −0.760ns，因此没有放行。r7改用上述最小reader调整并重新综合，但尚未完成实际布线，改善效果未知，未增加HDMI时序豁免。

r7最新的直接卡点是父脚本的状态判断。native日志及完成标记表明phys_opt成功；父脚本却硬要求STATUS为 `phys_opt_design Complete!`，在STATUS／NEEDS_REFRESH组合断言处退出1，两项当时原值未打印。

之后仅做了一次全新只读查询：工具62.109秒exit0；包含前后全文件比对的总耗时156.188秒。当前实现为 `Not started route_design`、`NEEDS_REFRESH=0`、进度80%；综合为完成、refresh=0、100%。完整REF7的4810文件、旧937源／XPR、41库及原失败证据，前后SHA／size／mtime／集合全部一致。独立复核也通过。

这些证据支持“原生物理步骤已完成、当前下一步布线未开始”的有限判断，也说明脚本预设的完成文案与实际工具状态不兼容；**不能据此回填失败时历史属性、改写原父exit1或宣称STA通过。** 尚未执行补充检查点审核、结果投影或后继route。

原失败和新观察分别保留：[父失败保全](../../tools/pose-v1/evidence/hdmi-live-20261017-r7/place-parent-failure-r1/review.json)、[只读查询](../../tools/pose-v1/evidence/hdmi-live-20261017-r7/place-run-state-query-r1/review.json)、[独立查询复核](../../tools/pose-v1/evidence/hdmi-live-20261017-r7/place-run-state-query-independent-r1/review.json)、[后续消费边界评估](../../tools/pose-v1/evidence/hdmi-live-20261017-r7/place-native-continuation-review-r1/review.json)。

### 3. 本轮耗时不全是必要的硬件实现时间

除实际综合、布局布线及物理优化外，我编写的校验脚本对Vivado缓存元数据、综合完成标记和实现状态文字存在不准确假设，造成额外的误拒绝、取证与窄修。这是本轮执行中的流程问题，增加了耗时，也使排查长期停留在“获得合格观测候选”的前置阶段。

已修正的缓存／综合标记判断保留了原失败和独立验证；最新place状态问题仅完成诊断，没有在暂停前继续修门禁或重新构建。准备脚本、mock通过和原生子步骤完成都没有计为整机完成。

## 暂停现场与恢复入口

- 最新固定物理检查点：`.local/hdmi-live-20261017-r7/reference/fpai_demo_vivado.runs/impl_read_v3r7/ai7030_edif_top_physopt.dcp`，SHA256 `453a031b1bf820a3e5aae96d3a73a29665304d3855f35fb85327117544dc6f68`。
- 原始父阶段、原生Tcl／日志／完成标记、源库身份和查询前后清单均已封存。既有aa175执行器及fa28正式契约未为本次失败改写；未执行的旧审核／投影候选不适用于本次真实失败，也未接入发布门。
- 本次没有SSH、Device初始化、DMA、推理、HDMI START、BOOT写入或重启。上次板端只读证据为2026-10-17原BOOT运行身份；本报告不把它当作刚刚重新核验。旧执行包重启额度已用完。
- 本机暂停核对时Vivado进程数为0；三个协作代理已停止技术作业，仅完成本报告所需交接。没有安排定时恢复或后台续跑。
- 统一恢复入口：[continuation-state.json](../../tools/pose-v1/evidence/hdmi-live-20261017-r3/continuation-state.json)。阶段恢复后前，不继续任何诊断、构建、部署或板测。

恢复后建议先审核固定native检查点的上下文、来源及补充回执消费方式，解决状态文案兼容问题，再以独立有界作业只执行后续route，避免重复place／phys_opt。仍须完成原厂JFM、完整STA／DRC及发布门；通过后才生成和核验离线bit／ICAP／BOOT包。此处是交接建议，不是新执行授权。

实际上板还需要阶段恢复后现场步骤并批准新的具体BOOT／重启包；既有许可不能复用。届时先做有界DMA，全部通过才做三窗新推理 → HDMI现场验收；SDK或数据异常仍保存现场并停止。PC高质量3D展示及CSI实时采集接入不包含在本次HDMI闭环验收中。
