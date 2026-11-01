# 正式融合追溯r3 apply验收

完成一次受限apply-check并完整回传，代理仅本机独立核验，无板端接入或重跑。
退出0、stderr空，阶段完成original_bindings_validated_before_apply→session_applied→
original_to_effective_bindings_validated→apply_and_bindings_completed_no_forward。
45回传/291包项、15ARM头文件/两库/3.39.0及程序e8d66113…e6c696a8身份匹配。
device25122301/icore24160628保持，真实四RAW参数及三PS输入与已验收离线基线一致。

创建1181项原绑定（1173 ZG＋八Host），部署15项实际绑定（七ZG＋八Host）。
两组十份完整快照及1181条bindings.jsonl、binding-summary.json齐全。
七组9185–9191的merge_from恰好覆盖1173原HardOp，无遗漏/重复/额外成员，组成员和同步基线与r2审阅证据匹配。
原8622→实际组9185，六计算Host188/192/437/442/582/649及Input0/Output672保持。
C++正式门检及本机独立融合核验均通过，原HardOp与有效组类型识别正确；没有降低原覆盖要求。

完整dmesg前后相同，available均723MiB/Swap0；bridge空，无operator-execution/results.jsonl或failure。
**已验证Session创建、apply部署及绑定追溯，未执行模型前向。**
不宣称NPU计算、真实PS/NPU生产者同步、部署数值、HDMI/RTSP或持续性能通过。

[独立复核](evidence/mixed-20261006-fusion-r3/apply-independent-review.json)、
[新apply门禁](evidence/mixed-20261006-fusion-r3/apply-check.acceptance.json)已保存。
旧r1/r2失败证据保持历史状态；修正后本次通过不改写此前失败记录。
下一步仅[MIXED-FUSION-R3-COMMANDS.md G](MIXED-FUSION-R3-COMMANDS.md)一次180秒mixed-one，实际前向仅308/frame6，完整回传后再考虑三样本。
