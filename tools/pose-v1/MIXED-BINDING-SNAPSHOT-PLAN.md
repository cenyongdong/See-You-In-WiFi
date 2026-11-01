# 绑定追溯最小取证方案（2026-10-06已批准）

已明确回复“同意方案”。候选已逐字节应用到核心源码，原文件备份在新r2证据目录；
新包已准备，尚未交叉编译、运行新Host/离线/内存或apply取证。
新入口[MIXED-BINDING-R2-COMMANDS.md](MIXED-BINDING-R2-COMMANDS.md)，旧r1保持失败状态，不重跑。
下方“当前仅候选”是批准前阶段记录；仍不降低门检、自动改变SDK优化或执行mixed。

目标：补全8622缺绑定的诊断证据，区分真实缺绑定、SDK合并表示或键/编号粒度差异。
依据及旧失败：[MIXED-APPLY-FAILURE-20261006.md](MIXED-APPLY-FAILURE-20261006.md)。

## 可审查改动

[候选完整源码](mixed_check.binding-snapshot.candidate.cpp)、[候选补丁](mixed-binding-snapshot.candidate.patch)。
仅新增snapshot_bindings，在Session创建后和apply返回后各写一次：

- 完整backendBindings的全部键与后端类型（不预设键就是原始HardOp ID）。
- 原图、Session及每个Backend的network_view：列表顺序、ID、SDK typeKey及is_hardop布尔值。
- ZG forward_info的全部hardop_map：键、net_hardop ID、sync_idx和merge_from成员。
- ZG idx_map的全部键、sync_index/layer_count，以及后端清单。

只读取SDK公开元数据，不读取缓存/任意寄存器，不直接解引用硬件数据地址，
不重复调用autoMerge，不改变默认SDK优化、注册函数、数据桥、模型/RAW/BOOT、原算法或前向代码。
原严格绑定门检保留，取证后仍可能退出1；**日志收集完成不是apply验收通过**。
静态签名/字段已按3.39.0头文件审查，未实际编译，ARM构建与字段运行状态待人工操作。

## 拟执行顺序和分工

后代理仅应用候选、生成新身份包和具体命令；旧mixed-r1包/程序/失败目录保留。
以新构建标签交叉编译，代理核对源码/SDK/二进制。因程序身份变更，新门禁文件不得由旧验收改名或改SHA复用。
按现有顺序复核新Host107例、离线真实参数/输入和SDK内存，再一次300秒apply取证，不做模型forward。
如希望调整新程序前置门检的复用方式，须另外形成并批准可验证的身份/范围方案，当前不跳过。
全部产物完整回传后，代理依据实际merge_from/runtime视图讨论正式绑定校验办法；
必须覆盖1173个原HardOp和六Host计算节点，不接受只降低计数或删除停止条件。
超时/OOM/总线/SDK异常立即保留停止，不自动重试/复位/改参数。

这一步会重新初始化设备并创建/apply Session，**不是纯板端只读查询**；负责实际执行。
当前仅候选准备，未应用核心修改、生成新运行包、编译、重跑apply或执行mixed。
