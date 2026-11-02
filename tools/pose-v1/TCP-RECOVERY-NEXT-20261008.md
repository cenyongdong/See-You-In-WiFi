# 首启动恢复与输出失配取证准备

最新本阶段采用一次规整，保存优先新目标完成三/27＋重复32全链验证，见[PRESAVED结果](PRESAVED-RESULTS-20261008.md)及当前检查点（历史附件，当前仓库未附：`evidence/tcp-presaved-20261008-r1/next-checkpoint.json`）。此次一次授权已使用，无需重复恢复旧包；本文件下方为此前准备/历史停止状态，不作再次规整或重启指令。

当前按既定失败策略结束板测，属于失败停止；没有后台任务或自动重试。先读[结果](TCP-INTEGRATION-RESULTS-20261008.md)、检查点（历史附件，当前仓库未附：`evidence/tcp-evidence-20261008-r1/next-checkpoint.json`）、[ADR_02](../../ADR/ADR_02.md)与[ADR_12](../../ADR/ADR_12.md)。

## 恢复首启动条件

新诊断程序、包及Host107已验，下一阶段不需重复Host图解析来制造更多分配压力。必须先由配置采用恢复方式：优先受控冷启动后尽早保留一个VPU上下文，或单次有记录的规整诊断。两者都未执行，不写入runner、不作为循环重试政策。现有批准方案要求“不自动规整、不重启、不改CMA/BOOT”；没有选择前只继续本机分析，不再启动设备。

若选择冷启动：保持同BOOT/模型/SDK/CMA，确认板端恢复SSH后先只读核验身份、内核/cmdline、竞争进程和内存，再传相同已验诊断身份到全新目录。既有纯Host gate在相同程序/包/SDK身份下可携带，不伪造新运行；新VPU及模型结果必须重新独立核验。快照只作观察，不以一时出现普通order7块保证初始化成功。

## 已准备的具体门检

- 程序：`.local/pose-v1-build/mixed-20261008-tcp-evidence-r1/pose_live_pipeline_check.arm64`，SHA256 `d7def2de0727cabe12c5d2b8a5cc692416bb63428e3b462202ce458734f98a47`。
- 包：`.local/pose-v1-tcp-evidence/package-20261008-r1`，manifest `08052d25a852660ebab5de61c308f187dcf56d4806098ad4880c0044e9edf4c5`，403项/44来源，完整LF清单。
- runner：`run-tcp-evidence.sh`。板端新目录必须含`package`、程序、`build-result.json`、对应`gates/host-check.acceptance.json`。
- 主机先运行`armed_tcp_live_peer.py --package <上述包> --cases three --output <全新主机目录>`，确认`PEER_ARMED`后才启动板端`sh <新目录>/run-tcp-evidence.sh live-three`。收到真实`LIVE_READY live-three`后向已有主机进程写`START`，不再临时启动另一个进程。
- 完整回传后按`live_gate.py`、`review_tcp_live_input.py`、`review_resident_video.py`、`review_live_network.py`及`complete_live_stage.py --input-review`核验，只有最终完整门禁生成后进入27。
- 27同样提前arm。若原输出比较再次拒绝，保存`results/failed-result`完整输入/分数/姿态/原始CSI和identity；全局停止，回传后独立NumPy逐位/误差/候选检查。原错误和门禁不放宽。

成功采样日志仍为前4帧；失败捕获仅发生在异常之后，不增加正常路径全帧大文件落盘。首次capture5秒、Engine60秒、ready后20秒、硬件总180秒和1000编码帧边界保持。

## 证据之后的决策

有限差异按实测分类，不能先认定舍入或候选换位。若内容失配明显，再限定公开CPU桥/实际Input0/输出存储的取证；若只在并行时出现，设计明确对照而非直接改同步、cache或等待。修复须有针对性回归。

27通过前不启动整机性能或长期测试，不更换SDK、模型、BOOT或驱动。HDMI配套未明，仍不猜写寄存器。已准备的[整机计划](WHOLE-SYSTEM-NEXT-20261008.md)保留为后续，当前不执行。
