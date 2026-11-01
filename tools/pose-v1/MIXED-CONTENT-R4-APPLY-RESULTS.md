# r4 apply-only验收

一次执行完整回传，代理仅本机核验，无设备接入或重跑。
退出0、stderr空，Session创建/apply及正式原到有效组追溯阶段完成。
1181条原节点记录齐全，1173HardOp经七个实际ZG组9185–9191完整唯一覆盖，无遗漏/重复/额外成员，固定成员和同步基线保持。
六计算Host188/192/437/442/582/649及Input0/Output672保持，原8622→9185。
两组十快照、binding-summary.json、RAW参数及PS输入与离线基线一致。
45回传/291包/15ARM头文件/两库/3.39.0及程序ba8d5398…15dcea7、设备25122301/icore24160628身份匹配。
完整dmesg前后相同，available685→686MiB/Swap0；无failure、桥执行、模型输出或content目录。

[独立复核](evidence/mixed-20261006-content-r4/apply-independent-review.json)、
[apply门禁](evidence/mixed-20261006-content-r4/apply-check.acceptance.json)已保存。
仅部署/绑定通过，content_capture=false，尚未读取真实Session Input0内容，不证明r3连续输入故障修复。
下一步仅[MIXED-CONTENT-R4-COMMANDS.md G](MIXED-CONTENT-R4-COMMANDS.md)一次180秒308单样本、显式Host内容取证并完整回传。
任何提前停止均保留已有caller/Input0内容，不自动继续三样本或重试。
