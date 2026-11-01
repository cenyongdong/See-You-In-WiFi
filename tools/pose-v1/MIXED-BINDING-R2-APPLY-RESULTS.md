# 绑定快照r2 apply取证与停止原因

完成一次300秒受限apply-check并完整回传；代理只分析本机文件，无板端重跑。
退出1、stderr仅Original op lacks traceable backend binding (including any fusion): 8622。
阶段已到session_applied，创建后/部署后各五份快照齐全；未forward、bridge空，没有模型输出。
45回传/290包哈希、程序94a03a90…bd061248、15ARM头文件/两库/3.39.0及设备25122301/icore24160628身份一致。
真实四RAW参数、三PS输入与r2已验收离线结果保持，完整dmesg前后相同、available均722MiB。

## 实际绑定与融合映射

Session创建后绑定1181项：1173个HardOp全部ZG，六个Host计算节点及Input0/Output672共八项Host。
apply后绑定15项：七个ZG执行组与上述八项Host。
原图、Session视图及后端视图成员/类型保持；两个ZG映射表各1180项，包括1173原条目和七个融合组条目。
只从**实际绑定到ZG的七组**取merge_from，覆盖原HardOp集合恰好1173项，无遗漏、重复或额外节点。

| 实际ZG执行组 | 原HardOp成员数 | sync_index | layer_count |
| --- | ---: | ---: | ---: |
| 9185 | 366 | 0 | 223 |
| 9186 | 19 | 223 | 11 |
| 9187 | 412 | 234 | 243 |
| 9188 | 7 | 477 | 4 |
| 9189 | 189 | 481 | 157 |
| 9190 | 134 | 638 | 82 |
| 9191 | 46 | 720 | 25 |

原8622属于组9185，其ZG绑定实际存在；原检查器在apply后仍逐个原ID直接查backendBindings，因键已合并而停止。
六个Host计算节点188/192/437/442/582/649保持，Gather原实现不改。这次停止不能据此归因于缺失NPU算子。
428个原条目的layer_count为0，融合组均正数；不能把layer_count当原节点覆盖计数或据零值认定丢失。
其更深层指令语义本轮未验证，覆盖结论依据实际绑定的merge_from及集合核验。

另发现本机核验器使用icraft::xir::HardOp字符串，而本次SDK typeKey实际是icraft::xir::HardOpNode。
这是尚未触发的核验器类型识别问题，需与正式融合追溯修正一同审阅；当前生产脚本未修改。

## 证据与界限

[独立审查](evidence/mixed-20261006-binding-r2/apply-independent-review.json)、
[快照审计](evidence/mixed-20261006-binding-r2/binding-snapshot-audit/review.json)、
[1173项原到执行组映射](evidence/mixed-20261006-binding-r2/binding-snapshot-audit/original-to-effective.jsonl)。
离线审计工具mixed_binding_snapshot_audit.py通过真实快照及九项篡改拒绝检查：缺成员、重复成员、混入Host、
丢执行组绑定、错误后端、组ID不符、同步表不符、Gather后端改变和创建时HardOp误放Host。
审计初版对所有条目要求layer_count>0导致停止；读取实际428个原条目为0后，仅要求已绑定执行组正数，
原条目允许0并两表一致。该本机审计规则调整未修改任何板端程序、SDK或模型。

**apply正式门检仍未通过，不生成apply验收文件。** 快照证明元数据追溯完整，不证明NPU执行、PS/NPU同步或模型精度。
具体修正候选范围见[MIXED-FUSION-BINDING-FIX-PLAN.md](MIXED-FUSION-BINDING-FIX-PLAN.md)，待讨论批准后才应用。
