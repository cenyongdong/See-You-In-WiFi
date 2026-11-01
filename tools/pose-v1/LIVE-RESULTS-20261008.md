# 真实在线串联与网络模块验证结果

2026-10-08，继续验证模块。固定本地CSI三窗＋重复及27窗＋重复的**实际推理→绘图→VPU capture→owned AU→RTSP**有限串联已通过；慢客户端保护的独立候选正负门检通过，尚未替换正式r2。

## 实现与身份

新独立`pose_live_pipeline_check`目标，FixtureWindow/完整结果核验、图像标记、Host适配和编排各自封装。一个主线程Engine保持整个窗口，VPU工作者独占编码上下文，network工作者独占live555。容量2画面popLatest与容量8 AU链分别管理；capture已经复制成owned字节后才交给AU，原SDK/数学/复制/reset(1)/0→745/两缓冲/prime2/格式/cookie不改。

程序SHA256 `ec07076fdebf04b17b2fcb90b43679a02ca938ed50fabeddb304ab9ccc253fc1`；manifest `bdee55fcd8851d8ea14addd971c24a470421ce4b4985a00699239867844110fb`，403载荷/34构建来源/15SDK头/189厂商头库。构建 `.local/pose-v1-build/mixed-20261008-live-r2`，包 `.local/pose-v1-live/package-20261008-r2`。r1只构建，板测前r2加入并发时间读取的防下溢检查；原r6/r3及所有失败保持。

## 已通过范围

| 门检 | 实测结果 |
| --- | --- |
| 新构建/Host | GCC9.4/CMake3.24.2及SDK3.39.0匹配；Host107/12注册/22输出59,600FP32逐位参考；AU17类拒绝、2000并发通知；图像队列容量/覆盖/最新选择/独占/停止通过 |
| 原三窗＋重复 | 4次完整前向、491实际编码、221 RTSP帧，全部四调用及NoInput24帧覆盖；输入/100分数/4200姿态逐位旧参考，实际RTP/capture PTS/全部解码像素一致，2758关节检查 |
| 27窗＋重复（协调后） | 28次完整前向、489实际编码、429 RTSP帧，全部28调用及NoInput231帧覆盖；完整数值/字节/实际PTS/像素一致，2772关节检查 |
| 生命周期 | 两个成功阶段Engine创建/前向/销毁均主线程，workers_joined发生在最后sample之后、Engine_destroyed在join之后；队列覆盖/coalesced均0，AU水位2/1；正常drain/LAST/输入归还、source/端口释放，exit0/dmesg同 |

合计**32次验收前向、483,200个完整输入/分数/姿态FP32值、980实际编码、650网络解码**。全部395帧实际结果画面均传到主机核验（额外255帧NoInput），5530个关节可见性检查。重复画面不计新姿态。当前2Hz固定输入、目标10fps采样、实际时间轴；不是整机5Hz或端到端延迟/30分钟验收。RTCP厂商诊断stderr每上下文一行保留。

[三窗门禁](evidence/live-20261008-r2/live-three.acceptance.json) · [27窗完整门禁](evidence/live-20261008-r2-coordinated/live-27.acceptance.json) · [汇总/恢复](evidence/live-20261008-completion/completion-review.json)

## 难点、失败与修正

首轮27窗板端28前向/490编码exit0，但客户端加入ID450，只40帧，未覆盖来源，原失败不算27网络通过。新外部runner根据真实network ready标记，在同一次工具调用立即启动客户端；程序/403包不变，新目录通过429帧，未降低来源或100帧门禁。见[ADR_09](../../ADR/ADR_09.md)。

慢客户端取证发现实际RTP库500ms补偿/错误返回，原r2没接发送错误回调。隔离guarded候选使用公共`setOnSendErrorFunc`传播停止，SETUP后每TCP连接64KiB发送缓冲、Linux读回128KiB，不改系统网络配置/模型/SDK/VPU。见[ADR_10](../../ADR/ADR_10.md)：

- 不读取客户端：21KiB真实IDR重复10fps，85产生/80消费、水位5后RTP发送失败；错误后无继续AU/NAL，预期exit1、source/端口/内核正常。SDK-free，不打开VPU/NPU。
- 正常客户端：同guarded源码，明确30秒300帧控制，223帧全部VCL字节/实际生产时钟/解码像素与原seed一致，没有发送错误，exit0/内核同。控制画面固定NoInput，不是新推理或性能证明。
- 先前16秒正常对照只有91帧未达100门禁，保留，不反写通过；新30秒控制程序扩展的是独立测试窗口，硬件180秒与既有20秒ready窗口不改。

[慢客户端候选结果](evidence/rtsp-pressure-20261008-r1/completion-review.json) · [正常对照](evidence/guarded-normal-20261008-r1/completion-review.json)

## 当前边界与接续

正式r2使用原online_rtsp，不能把guarded候选结果回填为它的发送失败处理能力。下一新目标固化guarded候选并进行身份/Host/真实源回归，再将已验收TCP完整窗口单槽接口接入本轮固定本地CSI入口；保留2Hz/完整来源门检后，测整机计时/过载与长期。输入回放不代表实时采集或未知场景精度。

HDMI目标1080p60配套/安全停止未知，不写参考寄存器；SPS显式色彩、整机5Hz/10Hz/双路/30分钟仍待。测试和SSH/SFTP已全部结束，无后台服务或自动化。下次入口[检查点](evidence/live-20261008-completion/next-checkpoint.json)，原授权继续。
