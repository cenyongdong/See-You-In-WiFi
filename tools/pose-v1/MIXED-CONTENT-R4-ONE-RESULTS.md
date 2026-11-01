# r4 308单样本内容取证验收

## 工程内容总结

一次运行并完整回传，代理仅读取本机证据，无板端接入或重跑。
ARM Icraft/CustomOp3.39.0、程序ba8d5398…15dcea7、设备25122301/icore24160628及291项包身份保持；69项回传哈希通过。
退出0、stderr空，原节点融合追溯及真实参数门检通过。

308/frame6/invocation0一次前向保存17份Host CPTR FP32内容，共253760字节：
实际caller、真实Input0返回、八份SDK复制后的Host输入和七份适配结果，全部有限。
Caller和Input0各10800个FP32与固定308输入逐位一致，句柄/内存块别名记录均true。
本次实际Input0路径通过；别名记录本身不证明后续NPU读到新帧。

七ZG组9185–9191及六计算Host节点实际回调，另有Input0回调；八次ADDR→Host CPTR搬运115360字节。
完整100分数和4200姿态均有限，并与r3单样本308输出逐位一致。
本次适配结果由Host返回，提供输出缓冲区写回路径未触发。
forward207.07742ms，输出保存2.73488ms，含证据IO单帧210.97278ms，Session初始化26507.59282ms。
完整内核日志前后相同，available685→686MiB、Swap0；这些单次取证耗时不作持续性能验收。

[正式单样本门禁](evidence/mixed-20261006-content-r4/mixed-one.acceptance.json)、
[内容复核](evidence/mixed-20261006-content-r4/mixed-one-content-review.json)、
[独立复核](evidence/mixed-20261006-content-r4/mixed-one-independent-review.json)已保存。

## 对后续开发的参考

初次forward输入内容已确认，但r3不同CSI同输出故障仍未定位，连续输入更新、数值容限及性能尚未验收。
按已批准方案，仅执行[命令H](MIXED-CONTENT-R4-COMMANDS.md)一次300秒同Session的308/309/310/308内容取证。
若输入边界失配提前停止，保留部分记录并完整回传，不补跑；不得猜测性改ready/cache、复位或重建Session规避问题。
诊断IO及Host分配会影响时序，即使三帧响应恢复也不能直接宣布修复。
