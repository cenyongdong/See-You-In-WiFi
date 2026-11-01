# r3 308单样本混合计算工程验收

完成一次180秒受限mixed-one并完整回传；代理仅本机分析，无板端接入或重跑。
退出0、stderr空，阶段完成forward_started→case_completed→mixed_completed_not_numerically_accepted。
51回传/291包、SDK/两库/15ARM头文件、程序e8d66113…e6c696a8及设备25122301/icore24160628身份匹配。
真实参数/三PS前检输入保持，正式1173原节点融合追溯通过。

## 实际执行与输出

仅308/frame6/invocation0/source_time_ns0前向一次。七ZG组9185–9191均回调一次，六Host计算节点188/192/437/442/582/649均执行，另有Input0回调。
五个适配节点共八次SDK输入搬运，115,360字节从PLDDR ADDR到Host CPTR；适配结果以Host CPTR返回。
本次没有SDK提供的输出缓冲区writeback记录，不把此未触发分支认定为混合场景已验收；原Host回归保留。
分数[1,100]/400字节、姿态[1,100,14,3]/16,800字节，共4300有限FP32值，全部100候选已保存。
完整dmesg前后相同，available722→723MiB/Swap0。
前向204.64506ms、输出转储2.7998ms、单帧含证据208.09317ms、Session初始化及快照26795.38561ms。
这些是单次观测，不作5Hz、持续性能、显示延迟或端到端结论。

## 初步ONNX差异（无容限验收）

已重新核验ONNX参考12项哈希/模型/CPU provider/首帧重复基线。两端输出不是逐位一致。

| 指标 | 最大绝对差 | 平均绝对差 | RMS | P95绝对差 |
| --- | ---: | ---: | ---: | ---: |
| 全100分数，相同槽位 | 0.00304520 | 0.00122795 | 0.00138946 | 0.00212389 |
| 全100×14×3坐标，相同槽位 | 1.32329583 | 0.22922763 | 0.35551595 | 0.82695546 |
| 各端最高分候选的坐标 | 0.01611638 | 0.00550002 | 0.00709729 | 0.01328887 |

两端最高分槽位均0，ONNX分数0.94519699、板端0.94824219。
相同槽位或最高分槽位相同不证明候选身份相同；本轮未做候选匹配，不能据这些数字断言差异来源。
坐标为模型原始单位，无物理标定、真实标签或MPJPE评估，不能解释为毫米误差。
误差容限按约定等待三样本完整报告后讨论，不自动宣布数值通过。

[工程独立核验](evidence/mixed-20261006-fusion-r3/mixed-one-independent-review.json)、
[工程门禁](evidence/mixed-20261006-fusion-r3/mixed-one.acceptance.json)、
[初步差异](evidence/mixed-20261006-fusion-r3/mixed-one-preliminary-differences.json)、
[参考身份复核](evidence/mixed-20261006-fusion-r3/mixed-one-difference-source-review.json)。
下一步仅[MIXED-FUSION-R3-COMMANDS.md H](MIXED-FUSION-R3-COMMANDS.md)一次300秒三样本及同Session重复首样本，完整回传后核验工程和误差。
