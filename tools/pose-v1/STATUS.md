# 首版当前状态（2026-10-07，数值验收与P2更新）

**历史状态记录：** 本页的“当前”和“下一步”属于早期开发阶段。最终交付与设备状态分别见[项目进度](../../PROJECT-PROGRESS.md)和[恢复入口](../../FPGA/hdmi_candidate/RESUME.md)；不从本页启动旧负载。

> 2026-10-08当前：两缓冲启动三次回归及有限主线程Engine＋后台VPU三/27窗口通过，987原始编码帧全解码核验。[启动](VPU-STARTUP-RESULTS-20261008.md)、[常驻/预览](RESIDENT-RESULTS-20261008.md)、恢复点（历史附件，当前仓库未附：`evidence/resident-20261008-r6/next-checkpoint.json`）。下一在线owned AU/live555，保留原模型/数学/SDK/BOOT、主线程模式/两缓冲候选；旧后台Engine/六缓冲失败勿重跑。任务未被暂停，测试与SSH/SFTP已关闭，无后台。不是daemon/RTSP/整机5Hz/长期验收，预览名义10fps不当真实PTS；旧入口为历史。

> 2026-10-08当前：真实推理→渲染→VPU的有限内容链路已核验，两成功码流一致；无规整的新进程重复仍在固件连续页分配失败，**启动稳定性未过**。[结果/视频](PIPELINE-RESULTS-20261008.md)、[下一门检](PIPELINE-NEXT-20261008.md)、检查点（历史附件，当前仓库未附：`evidence/pipeline-20261008-r6/next-checkpoint.json`）。下一先取证REQBUFS/STREAMON页状态再依据证据修正，随后常驻上下文/有界实时/在线RTSP。属于失败停止，不自动规整/重试；旧阶段“当前/暂停”均为历史，整机/HDMI仍待。

> 当前RTSP首批已验证：200帧传输/重连与标准播放器100帧逐位原视频，有限上下文清理通过，无新依赖。[结果/录制视频](RTSP-RESULTS-20261007.md)、[F0接入准备](F0-INTEGRATION-PREP-20261007.md)。当前是预生成码流回放，在线VPU/实际推理合并、显式色彩、HDMI/整机长期仍待；旧未RTSP/暂停条目为历史。

> 当前最新：视频任务已恢复，真实27骨架/54帧有限编码及两独立上下文重复通过，主机完整核验，MMAP描述兼容修正已采用。[结果/视频](VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md)、[恢复入口](RESUME-VIDEO-20261007.md)。原推理/SDK/BOOT保持，HDMI1080p60未改时序，RTSP/实时合并/整机长期未通过。旧暂停和失败条目按历史保留。

当前最新：暂停并等待唤醒。[真实骨架首批失败报告](VIDEO-SEQUENCE-RESULTS-20261007.md)、[恢复说明](RESUME-VIDEO-20261007.md)、暂停检查点（历史附件，当前仓库未附：`evidence/video-sequence-20261007-r1/next-checkpoint.json`）。新API/真实27来源与54输入/协商通过，编码exit1且固件MMU ABORT，仅3部分图像，不作动态视频验收；HDMI配套不足未写，离线1080p图完成。会话关闭，补查认证前取消，不连接/构建/板测/后台；旧“接续执行”按历史理解。

当前最新授权：已审查样片并允许HDMI测试，解除下文暂停；[NEXT-VIDEO-PLAN](NEXT-VIDEO-PLAN-20261007.md)为后续执行顺序，新恢复点（历史附件，当前仓库未附：`evidence/video-next-plan-20261007.json`）。先真实骨架54帧动态文件与HDMI当前BOOT配套，后1080p60实屏/RTSP/实际推理合并。本轮只计划和资料核对，未新板测/时序切换，旧暂停记录为历史。

当前最新V2文件：独立H264720p10fps/30帧编码、回传MP4及主机逐帧ID/移动图审查通过，[结果/视频](VPU-RESULTS-20261007.md)、核验（历史附件，当前仓库未附：`evidence/vpu-20261007-r1/completion-review.json`）、恢复点（历史附件，当前仓库未附：`evidence/vpu-20261007-r1/next-checkpoint.json`）。无新依赖，原推理/SDK/BOOT保持，未RTSP/实时合并/长期。HDMI已接DELL E2421HN，目标1080p60、测试暂停，尚未硬件时序切换；此前未接屏/未编码属历史。下一步有界接口、真实预生成骨架帧与timestamp/VUI/RTSP。

当前最新E1-C：CPU骨架画面、27帧ARM/Native逐位画面及RGB565/NV12/NV21、三帧真实网络结果绘图已核验，[结果/预览](RENDER-RESULTS-20261007.md)。[V0配套表](V0-VIDEO-PAIRING-20261007.md)确认当前MVX两端MPLANE及NV12/NV21/H264枚举，尚未协商/编码；HDMI未接屏、720p时钟/扫描未确认。新的恢复点（历史附件，当前仓库未附：`evidence/render-20261007-r1/next-checkpoint.json`）指向独立编码与HDMI配套，旧“下一渲染”按此前阶段理解。

最新E1-A/B首批已执行完成：[结果](APPLICATION-RESULTS-20261007.md)、完成证据（历史附件，当前仓库未附：`evidence/application-20261007-r2/completion-review.json`）。生产入口无冻结Tokens依赖，TCP完整记录/单槽与3/27帧网络结果通过，38成功前向全输出逐位此前板端。2Hz验证无丢弃，27帧到达至结果P95 193.76084ms不作为整机5Hz。有限CLI与有界诊断不是长期服务；下一步渲染及视频配套，旧“本次未新应用”文字属此前规划历史。

首版采用当前lazy-r4异构方案的决策已确认，见[ADR_01](../../ADR/ADR_01.md)。[全流程计划](FULL-FLOW-PLAN-20261007.md)已归档，下一批建议生产接口与TCP接收，随后渲染/独立视频/双路长期验证。零拷贝/图/新算子性能优化后置；本次未执行新应用或板测。

明确验收现有27样本部署数值阶段；原误差不改写，query身份未证明，N2作为非阻断诊断保留。
验收决定（历史附件，当前仓库未附：`evidence/perf-20261007-r3/user-numerical-acceptance.json`）、[P2完整结果](P2-RESULTS-20261007.md)。

SDK profiling已关闭；单一steady_clock定位CPU桥等待/计算等开销。独立lazy-r4仅减少成功检查的错误字符串构造，保留全部检查/算法/同步。
Host107/四帧回归/3预热＋30计量通过，全部37输出与r6逐位一致。平均190.60146ms/P95 190.75409ms/5.24655Hz，处理核心短期基线达5Hz。
当前未包括网络/绘图/编码，200ms预算余量约9.4ms；整机5Hz/10Hz、HDMI/RTSP与30分钟闭环未通过。
原模型/RAW/SDK/BOOT、r2/r3/r6保持；新核验evidence（历史附件，当前仓库未附：`evidence/perf-20261007-lazy-r4/completion-review.json`），新[命令](P2-SINGLE-CLOCK-COMMANDS-20261007.md)。
性能任务完成，会话关闭，没有自动继续部署视频。下一阶段生产接口与应用/输出具体方案另议。

<details>
<summary>r1至r5及最初准备状态（历史记录，保留失败和修正，不作当前命令入口）</summary>

> 最新状态（2026-10-06）：因Lite关机、离开现场明确暂停E0/N1/P1，等待唤醒。新核心已编译，27份ORT参考已生成；未传输/板测，源码及独立证据复核待完成。见 evidence/runtime-20261006-r1/pause-checkpoint.json。

# 首版阶段结果（2026-10-06，三样本混合工程与跨帧状态修正更新）

下一轮准备已完成：[具体计划](NEXT-PHASE-PLAN-20261006.md)，E0运行核心→N1九组27份固定样本→P1低日志性能基线，H0本机资料并行。
已分析既有输出同分/预算并核对27候选身份；未新模型、编译或板测，实施范围/执行方和数值容限待讨论。

最新r6跨帧同输出故障已解决并完成三样本工程验收：[完整结果](MIXED-FRAME-STATE-R6-RESULTS.md)。
代理完成构建/Host107/离线/内存/apply/单/三全部门检；每帧清FPGA状态后0→745，三帧分数及姿态分别不同，重复308全部内容和输出逐位一致。
新mixed-three.acceptance.json和完整ONNX误差已保存，131回传/291包/SDK/设备及内核保持；Matmul仍NPU、原SDK/模型/BOOT未改。
数值容限、持续≥5Hz/延迟、HDMI/RTSP和30分钟闭环仍待；后方停止/候选/代执行文字为历史，不重跑旧包。

最新r4三样本已失败并完成分析：[报告](MIXED-CONTENT-R4-THREE-FAILURE.md)，130回传/68内容/身份保持，四forward后退出1，全输出相同。
Caller/Input0按帧更新，前段局部变化而后段582/649及输出不变；五CPU内核对实际输入52000FP32正确，PS/NPU交接/完成状态/搬运/复用根因待查。
不生成mixed-three门禁，停止重跑/数值验收/后续硬件；[r5状态取证](MIXED-CONTENT-R5-READINESS-PLAN.md)待批准，未改ready/cache/模型/SDK。后方“当前仅H”为历史。

最新r4单样本内容已验收：69回传/291包/身份保持，真实caller/Input0与308逐位一致，17份内容及4300输出全有限，七ZG/六Host执行。
[单样本结果](MIXED-CONTENT-R4-ONE-RESULTS.md)，mixed-one.acceptance.json已生成；当前仅r4命令H一次300秒同Session三帧及重复首帧内容取证并回传。
连续输入更新及r3故障根因仍未知，207.07742ms仅取证单次观测，不作修复/数值/性能通过；后方待单样本为历史。

最新r4 apply-only已验收：1181原节点/1173HardOp经七实际ZG组完整唯一覆盖、八Host/身份保持，45回传/291包通过，无content/forward。
[apply结果](MIXED-CONTENT-R4-APPLY-RESULTS.md)，apply-check.acceptance.json已生成；当前仅r4命令G一次180秒308实际内容取证并回传。
真实Session输入仍未读回，r3故障未定位；后文待apply为历史。

最新r4 SDK内存已验收：两16KiB六回读/24,576有限FP32逐位一致，28回传/291包/设备版本及新身份通过。
[内存结果](MIXED-CONTENT-R4-MEMORY-RESULTS.md)，memory-check.acceptance.json已生成；当前仅r4命令F一次300秒apply-only并回传。
未内容前向或Session实际输入取证，r3不同输入同输出故障仍待定位；后文待内存为历史。

最新r4离线已验收：真实四RAW参数/三PS输入32,400有限FP32/12注册及身份保持，32回传/291包通过，无设备/Session/NPU。
[离线结果](MIXED-CONTENT-R4-OFFLINE-RESULTS.md)，offline-check.acceptance.json已生成；当前仅r4命令E一次30秒SDK内存往返并回传。
真实Session内容更新仍待取证，后文待离线为历史。

最新r4 Host107＋内容路径已独立验收：CPU22输出59,600FP32保持，两模式SDK读回/别名模拟及错期望/未分配/FP16拒绝通过。
[Host结果](MIXED-CONTENT-R4-HOST-RESULTS.md)，host-check.acceptance.json已生成；当前仅r4命令D30秒离线并回传。
无Session/设备初始化/NPU，真实Input0内容尚未取证，r3不同输入同输出仍待定位；后文待Host为历史。

最新r4-final构建已独立核验，291包/20来源/12构建/15ARM头文件及两库匹配，新AArch64 PIEba8d5398…15dcea7。
[构建结果](MIXED-CONTENT-R4-BUILD-RESULTS.md)，build.acceptance.json已生成；当前仅r4命令B/C新目录传输后Host＋内容路径回传。
未实际Host内容读回或Session取证，r3三样本故障仍待定位；后文未编译为历史。

最新r4输入内容取证已批准并应用：[交付](MIXED-CONTENT-R4-DELIVERY.md)，291项最终包/12构建/20来源及本机11异常检查通过。
当前仅[MIXED-CONTENT-R4-COMMANDS.md A](MIXED-CONTENT-R4-COMMANDS.md)最终标签编译，未ARM内容实测；r3三样本失败仍保持，不forward重跑或自动修复。
新观测可能改变时序/分配行为，正常三样本工程/数值仍未验收；后面待批准为历史记录。

**当前停止：r3三样本不同输入响应失败。** 输入/ONNX不同，板端三个完整输出却与308首帧相同，退出1、无工程验收。
[失败证据](MIXED-FUSION-R3-THREE-FAILURE.md)，身份/绑定/内核正常；仅回调/重复首帧不证明每次使用新输入。
[输入内容取证方案](MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md)待批准，当前不重跑、不改缓存/ready/SDK、不生成正常数值报告。
后面三样本待执行为历史，约39ms失败后续耗时不作性能通过。

最新r3 308单样本混合工程通过：七ZG/六Host实际执行，完整4300有限FP32、八SDK搬运及身份/内核核验通过。
[单样本结果](MIXED-FUSION-R3-ONE-RESULTS.md)，mixed-one.acceptance.json已生成；forward204.64506ms仅单次观测。
与ONNX有数值差异，尚未容限验收；当前仅r3命令H一次三帧+重复首帧并完整回传，核验后全误差讨论。
后文前向待验证为历史状态，不能把工程通过扩大为精度、持续性能或HDMI/RTSP通过。

最新r3正式apply已验收：创建1181原绑定、部署后1173原HardOp经七实际ZG组完整唯一覆盖、八Host保持，退出0/身份/内核正常。
[apply结果](MIXED-FUSION-R3-APPLY-RESULTS.md)，apply-check.acceptance.json已生成；当前仅r3命令G180秒308实际单样本并回传。
尚无模型前向/NPU计算/两端数值通过结论，旧r1/r2失败证据保持，后文待apply为历史。

最新r3 SDK内存已验收：两16KiB六回读/24,576有限FP32逐位一致，28回传/291包/设备版本及新身份匹配。
[内存结果](MIXED-FUSION-R3-MEMORY-RESULTS.md)，memory-check.acceptance.json已生成；当前仅r3命令F一次300秒正式apply并回传，不forward。
新原到有效组校验尚待Session路径实际运行，SDK复制不证明NPU同步；后文待内存为历史状态。

最新r3离线已验收：四真实RAW参数/三PS输入32,400有限FP32/12注册及身份保持，32回传/291包通过，无设备/Session/NPU。
[离线结果](MIXED-FUSION-R3-OFFLINE-RESULTS.md)，offline-check.acceptance.json已生成；当前仅r3命令E30秒SDK内存往返并回传。
新融合追溯实际apply仍待执行，后文待离线为历史状态。

最新r3 Host回归已验收：107例/12注册/22输出59,600有限FP32逐位一致，45回传/291包及新身份匹配。
[Host结果](MIXED-FUSION-R3-HOST-RESULTS.md)，host-check.acceptance.json已生成；当前仅r3命令D一次离线并回传。
无Session/设备初始化/NPU，新融合追溯尚未ARM运行；后文Host待执行为历史。

最新r3构建已独立核验，291包/17来源/11构建文件/15ARM头文件及两库一致，新AArch64 PIE e8d66113…e6c696a8。
[构建结果](MIXED-FUSION-R3-BUILD-RESULTS.md)，build.acceptance.json已生成；当前仅r3命令B/C新目录传输和Host107回传。
融合追溯API编译通过，正式板端映射/Session apply及前向仍待验收；后文未编译为历史状态。

最新r3正式融合追溯修正已由并应用；创建原绑定/部署七组原1173覆盖/八Host保持，核验器HardOpNode修正。
[交付](MIXED-FUSION-R3-DELIVERY.md)，本机模拟新追溯回放与18异常拒绝通过，291项新包已准备。
当前仅[MIXED-FUSION-R3-COMMANDS.md A](MIXED-FUSION-R3-COMMANDS.md)新标签交叉编译；未新ARM编译/板测，不forward。
后续新身份Host/离线/内存/一次apply逐阶段，不复用旧门禁；下面待批准是历史记录。

最新r2 apply取证完成、原门检仍退出1：实际七个ZG组完整唯一覆盖1173原HardOp，8622归9185，六Host保持。
[完整分析](MIXED-BINDING-R2-APPLY-RESULTS.md)、原到有效组映射和九异常拒绝审计已保存。
Session/apply返回不等于完整前向通过；无模型计算、无apply.acceptance。
[正式追溯修正方案](MIXED-FUSION-BINDING-FIX-PLAN.md)待批准，暂停硬件及forward；下方待取证为历史状态。

最新2026-10-06：绑定快照r2构建、Host107、真实RAW/三PS离线和SDK内存六回读均已独立验收。
[r2内存结果](MIXED-BINDING-R2-MEMORY-RESULTS.md)，新memory-check.acceptance.json已生成。
当前仅执行[MIXED-BINDING-R2-COMMANDS.md G](MIXED-BINDING-R2-COMMANDS.md)一次300秒apply公共快照取证并完整回传。
严格1173/六Host绑定要求保持；原停止条件可能仍退出1，日志采集不等于映射/部署通过，不model forward。
设备复制不证明NPU生产者同步；旧r1始终失败，下面阶段待运行/未批准等是历史状态。

当前快照r2新构建已独立验收，源/SDK/新AArch64 PIE身份匹配，唯一原缩进warning已审查。
[构建结果](MIXED-BINDING-R2-BUILD-RESULTS.md)，build.acceptance.json已生成；新目录传输后仅Host107完整回传。
新快照尚未运行，不跳到apply/mixed，旧r1失败状态保持。下方r2未编译为此前状态。

当前绑定快照r2并应用：仅追加两阶段公共元数据快照，保留原1173＋六Host门检，旧r1保持失败状态。
新包290项通过，289项非manifest载荷与r1相同，核心仅mixed_check.cpp变化，尚未新编译/运行。
当前从[MIXED-BINDING-R2-COMMANDS.md A](MIXED-BINDING-R2-COMMANDS.md)开始新构建并返回日志。
新程序前置门检后只做apply取证，不model forward；取证非0仍回传，不生成虚假验收。
旧“候选未批准”是此前状态，仍不能重跑r1或直接mixed。

**当前停止：apply-r1未通过**。既有目录取证发现退出1，session_applied后原HardOp8622缺预期绑定追溯，未forward。
SSH断开为在登录shell单独set -eu后目录检查失败触发退出；代理只读取回35项完整结果，身份/内核检查正常。
[失败审查](MIXED-APPLY-FAILURE-20261006.md)，[完整绑定快照候选](MIXED-BINDING-SNAPSHOT-PLAN.md)未批准/应用/执行。
不重跑apply、不删/改名失败目录、不进入mixed；SDK合并/绑定粒度仍需实际映射证据，不直接放宽验收。

当前SDK设备内存往返已验收：版本25122301/icore24160628匹配，两16KiB ADDR PLDDR缓冲区，六输出24,576FP32逐位一致。
28回传/290包及SDK身份通过，stderr空、内核前后相同；[结果](MIXED-MEMORY-RESULTS-20261006.md)。
memory-check.acceptance.json已生成；下一步仅300秒apply-check，无模型forward。NPU/CPU同步、完整Session及mixed仍未验收。
下面memory待执行/回传均为历史状态。

最新mixed-r1 offline已正式验收：四真实RAW参数合法、三PS输入与固定及ONNX逐位一致；32回传/290包及程序/SDK身份通过。
退出0/阶段完整/stdout及stderr空/内核前后相同，无设备初始化、Session或前向。[结果](MIXED-OFFLINE-RESULTS-20261006.md)。
offline-check.acceptance.json已生成；当前传入验收文件，确认BOOT/JTAG保持且设备空闲后仅memory-check（30秒）。
设备区域/Session/NPU/部署数值仍未验收，下面离线待运行/回传均为历史状态。

最新离线预检审阅：现场反馈Host验收已传板，失败目录三文件/290项校验OK已核对，未调用离线程序。
现在按[MIXED-VALIDATION-COMMANDS.md](MIXED-VALIDATION-COMMANDS.md)保留改名原失败目录，再一次30秒offline-check并回传。
只有Host桥阶段已验收；真实RAW/PS离线结果及硬件阶段均未通过。预检证据（历史附件，当前仓库未附：`evidence/mixed-20261006-r1/offline-preflight-review.json`）。

最新2026-10-06：mixed-r1 Host桥回归独立验收通过，107例/12注册/22输出59,600FP32逐位一致、全有限。
45项完整回传/290包及程序/SDK身份匹配，stderr空、内核前后相同；[结果](MIXED-HOST-RESULTS-20261006.md)。
host-check.acceptance.json已生成，传板后继续离线；上次失败预检目录须保留回传审阅再按补充命令处理。
真实RAW、设备内存、Session部署和NPU仍未验收；下文Host待回传属于早期状态。

## 2026-10-06：ONNX参考完成、独立mixed候选交付

工程/数值分阶段、ONNX直接对照Lite；Icraft全CPU Matmul缺口不阻断本轮。
新Conda Python3.10.21/NumPy2.2.5/CPU ORT1.23.2已安装并锁定依赖/哈希。
308/309/310全部候选12,900个FP32输出有限，首样本重复逐位一致，不同输入响应存在，12项产物哈希核验通过。
见[ONNX结果](ONNX-REFERENCE-RESULTS-20261006.md)及evidence（历史附件，当前仓库未附：`evidence/onnx-reference-environment-20261006.json`）。
已交付独立pose_mixed_check/SDK Host桥/新包及六阶段脚本；原推理器/已验收CPU实现/模型保持。
最新构建已通过：mixed-20261006-r1配置/编译/链接完成，代理核对290包项/10源码/15头文件/Host＋ZG库及程序哈希匹配。
一条缩进warning经控制流审查不影响预期JSON行为，源码及程序保持，无需重编译；[审查结果](MIXED-BUILD-REVIEW-20261006.md)。
构建核验时Lite新阶段尚未执行，当时继续命令B传输及C仅host-check；实际反馈更新如下。

随后最新反馈：已传板并运行host-check，runner exit=0；本地完整回传尚未取得，新Host桥未独立验收。
提前启动offline-check因缺少host-check.acceptance.json在预检停止，未调用离线程序；不要重跑host-check/直接硬件。
先C回传Host结果，核验生成并传入验收文件；失败预检目录亦保留回传，后续按命令文档补充保留改名，不覆盖证据。
后续每阶段核验再推进，硬件显式allow-device-init；不自动重试/复位/改模型，误差容限实测另议。
数值报告、NPU完整计算、HDMI/RTSP/5Hz/延迟/30分钟尚无通过结论；下面旧未批准/待回传均为对应历史状态。

## 2026-10-05：下一阶段交付状态

**2026-10-06 CPU候选正式验收通过**：完整回传及文件复核已取得，代理独立核验107例（18正常/89拒绝）、12注册记录、22输出/59,600个FP32值逐位一致及全有限；包282/回传40哈希和SDK/程序身份匹配，ldd完整，退出0/stderr空。五个缺失Host节点补注册及前向通过、原Gather保持并通过。见[最终结果](CPU-ADAPTER-RESULTS-20261006.md)、独立证据（历史附件，当前仓库未附：`evidence/cpu-adapter-independent-review-20261006.json`）。仅Host CPTR/全有效分布的独立候选通过，未接入正式推理器或验证NPU交接/完整模型，CPU Matmul参考仍待解决。不要重跑C/D或自动mixed；下文待回传为历史状态。

**Lite运行反馈（2026-10-06，待完整回传）**：截图显示sh脚本及exit.txt退出0、stdout报告107例完成、stderr为空；summary标记CPU候选通过且device_opened/full_model_executed/mixed_verified均false。程序内部检查报告完成，本地尚无回传目录；实际注册记录/22输出及哈希联查待[命令D](CPU-ADAPTER-COMMANDS.md)，不重跑C、不进入mixed。用户目录创建/传输已达到实际运行阶段，较早mkdir缺父目录反馈不能当作当前未执行。

**目录前置反馈**：创建Lite子目录时报No such file or directory，推测父路径缺失，尚未实际ls确认。[命令C](CPU-ADAPTER-COMMANDS.md)已补父路径检查及仅对父目录mkdir -p，子目录普通mkdir保持禁止复用；不改测试路径/二进制/包，不认为这是算子失败。目录创建/传输/板端运行均未通过，代理未执行板端操作。

**2026-10-06 r2构建复核通过**：完成配置/编译/链接，5份源码及ARM二进制哈希匹配；282项包文件校验通过，新旧281项非manifest文件相同，SDK六头文件/Host库/两包3.39.0匹配。AArch64 PIE程序SHA256为8cf2017cedf6a97f98ce485d979239b659291f3c91d3a3d550382c1c94588622，直接依赖无ZG/AIU、无RPATH/RUNPATH。仅交叉编译验收，Lite加载/注册/数值尚未测试；用户可执行[命令C](CPU-ADAPTER-COMMANDS.md)，一次300秒Host测试，失败停止保存，不进入mixed。见evidence复核（历史附件，当前仓库未附：`evidence/cpu-adapter-r2-build-review-20261006.json`）；下文未编译为执行前状态。

**2026-10-06 r2批准后应用**：三处Array::set及日志捕获修正，两生效文件与审阅候选一致，原文件备份/旧包/r1目录保留；语法0错误。仅静态检查，未生成新包/重编译/算子测试，其他编译问题仍不能排除。现在人工操作[更新命令A/B](CPU-ADAPTER-COMMANDS.md)，新包`package/20261006-r2`记录源码身份、新构建标签`cpu-adapter-20261006-r2`；不改旧manifest，不直接进入C或mixed。下文“候选未批准/未应用”是审批前状态。

**2026-10-06 r1新反馈**：人工操作修正版后SDK身份及CMake配置/生成通过；编译检查器时stderr触发PowerShell中断，完整error未入build.log。静态确认三处Array::get_mutable()->at API错误，拟改Array::set并修正日志管道；[具体候选](CPU-ADAPTER-COMPILE-FIX-20261006.md)未批准/应用。SDK导出文件及五份构建源码身份已只读复核，旧包/r1目录保留，不自动重跑或进Lite。未完成编译/链接/前向，不能排除其他编译问题。

**2026-10-06修正应用更新**：审计修正，Build-CpuAdapter.ps1已替换容器Python依赖，版本/头文件/Host库门禁保持；原脚本备份及旧失败目录/测试包保留。生效脚本语法0错误，未执行Docker/编译/算子测试。直接执行[命令B](CPU-ADAPTER-COMMANDS.md)，使用既有实际包及新构建标签`cpu-adapter-20261006-r1`，无需重做A；回传日志和两份JSON后核对，再推进Lite CPU测试。下文“候选未应用/待批准”是批准前历史，修正应用不等于编译通过。

**2026-10-06人工操作反馈**：107用例测试包已生成，实际为`.local/pose-v1-cpu-adapter/package/20261005`；代理读取核对282项哈希及5份构建源码副本匹配。FPAI构建在SDK审计调用python3时退出127，当前PATH找不到该命令，未进入CMake配置/编译。停止重跑/板端测试，保留旧目录；[修正候选](CPU-ADAPTER-BUILD-FIX-20261006.md)改用Docker cp及Windows哈希保留身份门禁，无安装。候选未应用，修正版编译待批准；CPU内核/完整mixed仍未验收。此前“未生成”仅为交付时状态。

**最新批准范围与交付**：CPU算子注册及最小适配；隔离模块、独立检查器、NumPy参考/构建/板端运行/回传脚本已交付，见[CPU-ADAPTER.md](CPU-ADAPTER.md)及[执行命令](CPU-ADAPTER-COMMANDS.md)。设计107用例、22份正常输出，尚未生成、编译或运行；仅Python/PowerShell语法与SDK/模型静态核对完成。原推理程序、SDK、模型和NPU分工保持，Gather不覆盖、CPU Matmul不补齐。先执行A/B并回传构建证据，代理核对后再C受限CPU测试；不创建Session/调用Device::Open或访问NPU/DMA/HDMI。实际CPU数值、设备交接及完整mixed仍未验收。下文“新增算子未批准”为历史阶段状态。

最新：独立CPU注册探针后，代理用FPAI GCC9.4/Icraft3.39.0交叉编译并在Lite运行一次；退出码0、stderr空、5项回传哈希通过。optimized op1 Matmul无init/forward注册；ZG的188/437 TopK、192 GatherElements、582/649 ScatterND也均无注册，442 Gather有注册。当前全CPU参考及混合图五个Host节点存在注册阻断，mixed停止；未运行任何算子前向/模型/NPU。见[完整结果](HOST-REGISTRY-RESULTS-20261005.md)及evidence/host-registry-20261005/review.json。探针批准不扩展为插件加载、链接/SDK/模型修复；下文“探针未批准/运行”为历史状态。

已新增特殊问题代理直接工具协助权限并批准只读审计；代理SSH读取确认Icraft/CustomOp arm64 3.39.0，icraft包校验无差异，Host库SHA256与原始onchip包相同，CMake导出依赖明确，最终SSH/步骤退出码0、stderr空。见evidence/board-host-library-audit-20261005.stdout.log、original-arm-host-package-review-20261005.json。Host库损坏/替换缺乏证据，注册范围仍待验证。已准备[独立注册探针候选](HOST-REGISTRY-PROBE-PLAN.md)，未批准/编译/执行；未改模型/库/环境、未重跑参考或mixed。

Host日志复核更新：Session::Create<HostBackend>绑定op_id=1 MatmulNode失败，阶段到parameters_loaded后failed_stop_no_retry；mode=host/device_init_allowed=false，stdout空，无样本前向。内核尾部仍为启动消息、未见本次OOM，available 687 MiB；不能据此认定所有ARM Host均不支持Matmul或NPU混合路线已失败。本地文档CPU支持说明与板端实际注册范围须核对。见[失败审查与下一步只读候选](HOST-BINDING-REVIEW-20261005.md)及evidence/lite-host-binding-failure-20261005-1.png至-3.png；候选尚待批准，未修复或重跑。

最新Host执行反馈：人工操作已批准的一次300秒受限参考，截图退出码1，未通过；具体原因及失败阶段待stdout/stderr、stages/run-config/failure及内核上下文复核。证据evidence/lite-host-exit1-20261005.png。不要重跑或覆盖原目录/日志，不进入mixed或数值验收；下文“Host尚未执行”为此前资源前检状态，按本段更新。代理未代执行软件或改依赖/模型。

B“先用Lite Host作参考”，本阶段F2改为Lite ARM，复用已校验二进制及optimized图/固定输入。
命令已交付[LITE-HOST-COMMANDS.md](LITE-HOST-COMMANDS.md)。资源前检已复核：993 MiB总内存、744 MiB available、Swap 0，/tmp剩余47G；可见进程无明显其他推理/视频应用，目标输出前缀无旧文件。证据evidence/lite-host-resource-query-20261005-1.png及-2.png。下一步人工执行已批准的一次300秒Host参考，失败即停止；前检不保证峰值内存或算子支持。
Host尚未执行，ARM支持、内存/耗时及输出数值未知；不是部署降级，不修改模型/预处理或正式NPU/双路要求。
仅B获批准；ORT依赖解析/安装仍未获批准，原Windows Host方案保留不执行，mixed不能跳过参考门检。
下面“两项待批准”是候选交付时状态，按本段更新B。

Windows原开发终端查询已确认：cl在Hostx64/x64、目标x64、VSINSTALLDIR正确，CMake实际3.31.6-msvc6。
WindowsSdkDir未设置、WindowsSDKVersion仅`\`，有效SDK未识别；常见文件/4个厂商登记入口未找到。
不把“编译工具可查到”当成Host可编译，不自动安装或手配SDK，保留未登记自定义路径可能性。
证据`evidence/windows-host-sdk-query-20261005.png`（历史附件，当前仓库未附）。
已准备[参考路线与ORT解析候选](REFERENCE-NEXT-PLAN.md)：B复用现有Lite host模式对照，A保留Windows SDK补齐路线；
另建议独立Conda只做CPU ORT1.23.2依赖dry-run预览，两项均待配置采用/批准，未执行或安装。
完整模型与参考尚未运行，mixed仍未推进。

Windows查询最新反馈：自动路径已显示开发终端横幅，另一个截图中where cl无结果、架构/SDK变量未设置。
已明确查询是在另开的CMD中执行，未继承原开发环境；不能据此认定原窗口初始化失败或SDK未安装。
现在回原初始化窗口查询；原窗口环境、SDK及后续编译仍待验证。
只读已确认start/parse/winsdk/vcvars等子脚本存在；v17.0横幅是vswhere缺失时的默认显示，不作版本/通过门禁。
证据：横幅（历史附件，当前仓库未附：`evidence/windows-host-banner-20261005.png`）、未设置变量（历史附件，当前仓库未附：`evidence/windows-host-unset-query-20261005.png`）。
未安装/修复/编译或运行参考，软件执行仍人工完成；原窗口环境未核验前暂停F2及依赖它的mixed。

Windows开发终端首次启动失败：截图中的`Visual Studio 2022`目录名漏掉开头空格。
只读复核实际目录首字符32，带空格脚本路径存在、无空格路径不存在，不能据此认定SDK缺失。
已将[查询说明](WINDOWS-HOST-ENV-CHECK.md)改为真实目录项构造路径，同一临时x64开发终端/查询范围不变，
未代执行终端、编译或修复。下一步先exit回PowerShell再执行自动定位命令。
证据`evidence/windows-host-path-error-20261005.png`（历史附件，当前仓库未附）。

Windows Host工具只读定位更新：找到`D:\Visual Studio\ Visual Studio 2022\Community`，
目录名开头空格必须保留；MSVC14.44.35207 cl/link/nmake与C++头文件/库、VsDevCmd.bat、CMake文件存在。
CMake文件元数据3.31.6-msvc6，不是命令运行结果。SDK完整、开发终端初始化和VS生成器发现仍待查询/验证。
默认vswhere及常见Windows Kits注册表入口未找到/未返回记录，不自动安装或修复。
命令：[WINDOWS-HOST-ENV-CHECK.md](WINDOWS-HOST-ENV-CHECK.md)，
证据：文件定位记录（历史附件，当前仓库未附：`evidence/windows-host-tool-discovery-20261005.json`）。
仅查文件不代表Host编译/模型执行通过，ORT缺失仍待讨论；前述“Windows工具待确认”按本段细化。

E完整产物已人工交付并复核：stage以probe_complete_requires_review结束，配置mode=probe、
device_init_allowed=true，目录无failure.json，stderr为空。stdout明确Device initialization successful，
AXI zg330aiu、NPU=0x40000000/DMA=0x80000000、device=25122301、icore=FMSHZGV3TECH-AID - 24160628。
结合退出码0，E仅Open/version初始化探测通过。提供的dmesg尾部未见探测相关总线/DMA错误；
EXT4恢复、journal异常关闭/更换及其他提示发生于启动阶段，不归因于probe，不自动修复。
证据：产物和stdout（历史附件，当前仓库未附：`evidence/board-probe-review-20261005-1.png`）、
内核上下文上段（历史附件，当前仓库未附：`evidence/board-probe-review-20261005-2.png`）、内核上下文末段（历史附件，当前仓库未附：`evidence/board-probe-review-20261005-3.png`）。
未执行模型或验收NPU/DMA计算；compatibility_passed=false固定待验收标记保持。
下一步F1/F2数值参考，当前ORT缺失及Windows Host编译工具待确认；参考有效前不进入mixed。
下面“E日志待复核/未运行”为历史状态，不覆盖本次限定范围的通过结果。

最新E执行反馈：运行固定30秒timeout的probe，退出码0，SDK device版本25122301与基线一致。
icore版本已显示，待文本复核；probe.dmesg.log已保存，但stdout/stderr、阶段/配置和内核日志未提交。
compatibility_passed=false为检查器固定的待验收标记，不是SDK报错。E日志复核未完成，mixed未执行。
见`evidence/board-probe-exit0-20261005.png`（历史附件，当前仓库未附）。
现在只读已有产物，不重跑/覆盖probe，不依据退出码认定DMA/NPU计算或完整混合模型通过。
下面“probe未运行”为此前准备阶段的历史状态。

E前置查询已反馈：/usr/bin/timeout为GNU coreutils 8.30，probe及三份日志不存在，
可见进程列表未见明显AI/HDMI/编码应用。kbase/mvx等内核线程不等于演示程序或故障证据。
见`evidence/board-probe-preflight-20261005-1.png`（历史附件，当前仓库未附）、
进程及目录查询（历史附件，当前仓库未附：`evidence/board-probe-preflight-20261005-2.png`）。
仍待人工确认上次0x25122301核验后未替换BOOT/JTAG加载其他位流且无其他演示访问设备；
不从进程截图推定这些事实，未运行probe或推理，不自动停止进程或复位设备。

最新D产物已复核通过：输入[1,180,60]、分数[1,100]、姿态[1,100,14,3]及顺序符合float32门禁；
阶段started→offline_inspection_complete、mode=inspect/device_init_allowed=false，stderr为空且无failure.json。
结合前述11项包校验和inspect退出码0，D离线检查通过；尚无RAW参数加载或Device::Open/推理结果。
证据`evidence/board-inspect-artifacts-20261005.png`（历史附件，当前仓库未附）。
下一步先人工只读查询GNU timeout、进程列表，确认BOOT未再次更换；并发状态不明时不运行probe。
不自动终止进程或初始化设备。下面“产物待复核”为前一次截图的历史状态。

最新D后续截图：校验`files.lf.sha256`，11项全部OK、退出码0，板端包完整性已通过。
随后ZG图inspect退出码0；graph-io.json、stages.jsonl、run-config.json及stderr尚未提交，
离线接口验收待产物复核，不重跑或覆盖inspect-zg。设备probe和推理仍未执行。
证据`evidence/board-checksum-inspect-exit0-20261005.png`（历史附件，当前仓库未附）。
生产打包脚本候选修正仍未应用；下面校验失败与待执行文字为历史状态。

最新D截图：程序哈希匹配、ldd已列出的库全部解析，但包校验清单因Windows CRLF导致11个文件名尾随CR，
sha256sum报No such file，板端包完整性仍未通过。已只读确认本地清单11行全部CRLF，
根因为inference_gate.py的默认文本换行写入；候选修正待批准，未改生产脚本或现有包。
见[CRLF-CHECKSUM-FIX.md](CRLF-CHECKSUM-FIX.md)。inspect/设备probe/推理尚未验收。

最新B/C已人工执行并交付：固定三样本打包、FPAI交叉编译与链接通过，构建
`inference-20261005-165059-043b0c40`；实际AArch64 PIE二进制SHA256为
`d1006f9bd78050ffa484c64bf74fb62542d270c7acca5068e9da611a5bdc05e5`。
代理只读核对7份源码记录、11份包文件大小/哈希及二进制哈希，全匹配。
见`evidence/cross-build-review-20261005.json`（历史附件，当前仓库未附）。
板端传输、ldd、inspect均待人工操作，设备probe/推理未执行。当前进入D后停交结果，不能因链接通过认定板端兼容。
以下“未编译/待查询”为此前交付过程快照，最新状态以本段为准。

最新补查已确认`/usr/cmake`的Host/ZG330配置及对应头文件/后端so，FPAI Icraft/CustomOp arm64 3.39.0、
第三方包arm64 0.1.1均安装正常。更新下面首次查询的“ZG配置未找到”状态；现在进入B打包/C交叉编译。
代理未编译或运行，需先收集构建结果；ORT缺失及Windows工具PATH不可见保持，不安装或直接访问设备。

首次查询（历史；上段为最新）：已执行部分环境查询并提交截图：FPAI GCC9.4.0、CMake3.24.2和Icraft arm64 3.39.0确认；
SDK精确搜索仅返回HostBackend配置；ORT未找到，Windows cmake/cl当前PATH不可见。
待补查SDK包内容/后端命名与CustomOp状态，不开始交叉编译或设备初始化，不自动安装。
详见[ENVIRONMENT-QUERY-20261005.md](ENVIRONMENT-QUERY-20261005.md)。下面“路径/工具待查询”是初次交付状态，
已确认部分以本段为准；推理未执行状态保持。

独立混合推理门检及HDMI静态核对方向。已编写检查器/构建配置/脚本/逐条命令，
见[INFERENCE-COMMANDS.md](INFERENCE-COMMANDS.md)。按新分工，本轮没有软件编译、测试、模型执行或Docker/SSH操作，
尚无新推理结果。先人工查询实际SDK CMake目录、Host编译工具和ORT依赖，再构建并提交探测结果。
不能把本次源码交付覆盖为既有门检结果或新的推理通过。

HDMI静态审查明确默认参考1080p、有可写时序线索；匹配当前BOOT的工程/寄存器与像素时钟仍不明确。
详见[HDMI-STATIC-AUDIT.md](HDMI-STATIC-AUDIT.md)。720p60、实屏和双路目标未变，未开始硬件显示操作。

## 最新结论

- 300份真实回放预处理门检已通过：主机及Lite均与Windows参考float32张量300/300逐位一致，
  实板/主机输出哈希300/300一致，幅度及相位标量/周期最大误差均为0；4类非法输入均拒绝。
- 固定清单包含原3份样本，S11/S12/S13各34份，其余6组各33份，按原列表均匀抽取并保存哈希。
  幅度atol/rtol均1e-6，相位周期最大1e-5 rad；真实相位绝对差>1e-5 rad仍须讨论。
- 明确将人工±π降为非阻断诊断，其周期误差2.333111/2.693437 rad仍失败，不记为通过。
  原预处理/模型/ARM二进制保持不变。实板预处理单项P95=5.8595ms，不是端到端性能。
- 板上BOOT与指定Lite 25122301包一致，其余8启动文件未变。BOOT内载荷经32位字节序转换后
  与同包.bit完整载荷对应，BOOT另有4字节尾随；FSBL日志确认下载PL成功，Linux正常启动。
- 经额外明确批准，最小只读回读0x4000001C得到0x25122301，运行FPGA版本身份已核验。
  uEnv二次download.bit加载仍未确认，没有改BOOT/启动配置或执行SDK Open/reset/check。
- 板端Icraft/CustomOp实际arm64 3.39.0；参考包3.36.0与当前SDK的推理兼容性仍待实际门检。
- HDMI默认参考1080p60，RGB565包装器不配置720p时序；首版720p60目标保持，屏幕尚未连接。
  NPU、HDMI、VPU、RTSP及完整闭环均未验收。

详细结果及证据见[RESULTS-300.md](RESULTS-300.md)、[NEXT-GATE.md](NEXT-GATE.md)。
以下初始独立验证及阻断描述是300份方案批准前的历史记录，不覆盖上述最新状态。

## 已完成

- PS为主的回放→混合推理→HDMI/RTSP首版；当前只实施独立、不会访问未知硬件的阶段。
- 建立`Logs`、C++预处理模块、原始CSI发送端、协议说明、只读审计、构建和数值检查工具。
- FPAI为运行中的`ubuntu20.04:custom`容器，原挂载`D:\FPGACompetitionProject:/workspace`；
  实际arm64 Icraft/CustomOp 3.39.0，交叉GCC9.4，源码从当前worktree独立复制至临时目录。
- Conda独立验证环境已完成：Python3.10.21、NumPy2.2.5、h5py3.16.0、PyWavelets1.8.0。
  首次在线创建因Python包TLS连接中断失败，随后缓存离线安装成功，未改渠道/证书/既有环境。
- 板端FAT16直接只读解析，9文件与原镜像大小/哈希全部一致；没有挂载或改启动文件。
- 零幅值复数带符号零移植错误已定位、修正，保留首次失败证据。
- 9类输入在Linux主机与实际Lite运行；3份真实CSI及常量/零/随机输出逐位一致，
  真实样本5.70319/5.78065/5.72649ms。四类非法记录均拒绝。
- arm64二进制SHA256 `65d44aa2aff5ffe2975300b27b1325dc7b25d5cb71cd6f85ee5076b4aa4a59b2`；
  可复现构建脚本再次构建得到相同哈希，与板端实测二进制一致。
- Windows TCP回环强制碎片读取，3个原始CSI窗口/帧号字节不变；只是发送端测试，未接入板端。
- 离线替换Windows NumPy angle为Python math.atan2的诊断未解释π边界差异；保留负结果，不修改原算法。

## 初始阻断与未验收（历史；更新见最新结论）

1. **启动配套未知。** 已知文件一致不等于已知运行位流。uEnv引用p2的download.bit，前次根目录未找到；
   不知道加载是否成功、BOOT内包含哪个AI系统以及当前HDMI映射。等待保留的完整启动串口日志，
   不尝试默认AI/HDMI寄存器或更换BOOT/位流。
2. **边界数值未通过。** 0.75rad斜坡误差7.5051e-14；±π合成斜坡分别有6.24063/5.76522最大绝对差。
   相位展开在此边界对微小浮点差异敏感是排查方向，尚未唯一证明因果，不能当作普通小误差忽略。
   未定义/放宽容限或改变算法，总体预处理门检待进一步讨论。
3. **闭环尚未实现。** 未运行ONNX/参考模型/板端混合推理；未实现板端TCP服务、有限队列、
   骨架绘图、HDMI、VPU/live555 RTSP或30分钟测试。NPU和正式双路验收均未通过。
4. 实际训练服务器NumPy/软件栈未在本阶段查询；原方法来源代码哈希和Windows参考依赖版本已记录，
   不能以当前Windows数值对照代替完整训练环境复现。

## 下一步

启动日志与运行版本已核对、真实回放门检已通过；下一步讨论SDK设备初始化/完整混合推理的具体门检范围，
核对当前位流HDMI实际时序，并在接屏后做实屏验收。版本相符不替代兼容性或功能验收。
启动变更、新依赖、模型修改、新增FPGA工程均遵循审批规则。不得以网络骨架备用方案、全CPU或电脑推理
替代正式首版验收，不自动重启或改板卡配置。

证据：`evidence/board-audit.json`、`boot-source-comparison.json`、`host-preprocess-initial-failure.json`、
`host-preprocess.json`、`board-preprocess.json`、`asset-manifest.json`、`conda-explicit.txt`、`build-reproduction.txt`。

</details>
