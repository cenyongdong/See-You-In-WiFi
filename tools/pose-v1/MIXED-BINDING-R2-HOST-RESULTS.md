# 绑定快照r2 Host回归与离线预检复核

完成Lite运行及完整回传；代理仅分析本机文件，未接入板端或重跑程序。

Host阶段退出0、stderr空，107例（18正常/89拒绝）、12注册记录通过。
22份输出共59,600个有限FP32值与NumPy固定参考及已验收r1输出逐位一致，最大差0。
Gather原注册保持；94次桥搬运记录为84次input_to_host和10次host_to_output，源/目标均Host CPTR。
290项包校验、45项回传校验、15份ARM头文件、Host/ZG库及Icraft/CustomOp3.39.0身份匹配。
返回程序SHA25694a03a903a4a97f229b1549dcbd1bade193d60dbb23753c1f030431fbd061248，与新r2构建一致。
dmesg完整前后逐位相同，available723→722MiB、Swap0；该快照不代表峰值内存或性能。
mode=host-check、device_init_allowed=false，无完整Session、设备初始化或NPU前向。

提前运行的offline-check仅留下package-check.log、timeout-path.txt、timeout-version.txt；290项全部OK，GNU timeout8.30。
结合截图缺少gates/host-check.acceptance.json及runner顺序，确认在程序调用前停止，没有离线检查结果。
原本机offline-check目录已原样保存在offline-preflight-missing-gate，避免后续成功结果覆盖失败证据。

证据：[Host独立核验](evidence/mixed-20261006-binding-r2/host-independent-review.json)、
[Host验收](evidence/mixed-20261006-binding-r2/host-check.acceptance.json)、
[离线预检复核](evidence/mixed-20261006-binding-r2/offline-preflight-review.json)。
下一步人工操作[命令E](MIXED-BINDING-R2-COMMANDS.md)：传入新r2 Host验收、受保护地改名保留板端失败目录，
再仅执行一次30秒offline-check并完整回传；暂不memory/apply/mixed。
Host回归通过不能证明快照功能、融合映射、NPU同步、完整模型精度或连续性能。
