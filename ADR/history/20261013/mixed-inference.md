# 正式混合推理接入与帧状态的实施历史

2026-10-13从AGENTS.md迁出，按主题保存原记录；原文“当前”“已批准”“下一步”和暂停/恢复只表示当时状态，不是现行进度或新的执行授权。最新进度见[PROJECT-PROGRESS](../../../PROJECT-PROGRESS.md)，执行规范以[AGENTS.md](../../../AGENTS.md)为准。源行编号与迁移清单用于追溯；不改写原失败、修订或验收边界。

<a id="a148"></a>

## A148 · 首版接入计划已批准并开始（2026-10-07）

来源：整理前 AGENTS.md 第148–149行。

- 首版接入计划已批准并开始（2026-10-07）：明确“同意你的计划方案，请继续执行”，批准FULL-FLOW-PLAN-20261007.md路线。代理先执行首批E1-A生产接口与E1-B TCP回放；SDK/BOOT/模型/RAW/CPU数学/帧协议保持，单Engine串行、最新完整窗口槽位1、验证包装器保留固定参考。无新依赖，先SDK无关协议/队列自检→新ARM构建身份→Host107→生产/验证三帧重复回归→三/27帧网络结果对照；新修订保留失败与旧包，不重试同一失败运行或自动复位。源代码与有界日志修改属于此次接入；零拷贝/图/新内核优化仍后置。视频按后续配套/独立测试图/合并门检顺序，不因本批通过而宣称双路、整机或30分钟验收。

<a id="a150"></a>

## A150 · 首版异构基线与延期优化决策（2026-10-07）

来源：整理前 AGENTS.md 第150–151行。

- 首版异构基线与延期优化决策（2026-10-07）：明确以当前异构方案先完成项目全流程，闭环后再考虑真实指针映射/零拷贝、图与自定义算子性能优化。ADR/ADR_01.md已记录注册/布局/跨域内存/融合/帧状态/性能及视频配套难点，保留lazy-r4显式SDK复制、CPU适配、Gather/Matmul分工与reset(1)最终就绪协议；164ms等待不归为已证实搬运，0.47ms可见复制不作全后端搬运上界。FULL-FLOW-PLAN-20261007.md规划E1-A生产接口→E1-B TCP→渲染→独立HDMI/编码RTSP→双路/30分钟，下一批建议仅A/B，具体实施与设备/视频配套另定。本轮仅本机文档整理，无新代码/构建/SSH/设备初始化；项目粗估69/100约65%–70%不因写方案增加。N2非阻断，旧暂停/待数值文字按历史理解，不以规划代替实施或验收。

<a id="a152"></a>

## A152 · P2定位与消息优化完成（2026-10-07）

来源：整理前 AGENTS.md 第152–153行。

- P2定位与消息优化完成（2026-10-07）：按profiling-off/单时钟性能任务，r3量到平均212.93086ms/4.69636Hz，CPU桥等待164.48ms、CPU forward29.59ms，复制仅0.47ms；ZG调用跨度不作纯NPU时间。新增隔离lazy-r4，仅CPU/验证助手各增加const char*消息重载共4行，所有原检查/计算/SDK调用/同步/缓冲区策略保持，原CPU/r2/r3/r6不改。Host107含拒绝、原三帧＋重复、3预热＋30计量通过；37次输出逐位r6、exit0/stderr空/dmesg相同。平均190.60146ms/P95 190.75409ms/最大190.80669ms/5.24655Hz，当前短期处理基线达5Hz但不含网络/渲染/编码，余量约9.4ms；整机/10Hz/长期未通过。程序4f7fe3597bb2aaaa69884a429062ce0c3977b63a30c328b8ce6c9f9e41ab84ad，352包/16构建。数值阶段通过，原误差与query未证事实保留，N2非阻断。原perf_gate遗漏hashlib只以独立review_perf_stage供标准库绑定修正，不改数据/hash/规则、不重跑板测。结果P2-RESULTS-20261007.md及evidence/perf-20261007-lazy-r4/completion-review.json；会话关闭。当前性能任务已完成，后续未知窗口生产接口/网络/渲染/视频及算法、同步、缓存或模型变化另议。

<a id="a154"></a>

## A154 · 数值阶段验收与P2已批准（2026-10-07）

来源：整理前 AGENTS.md 第154–155行。

- 数值阶段验收与P2已批准（2026-10-07）：现有27样本数据精度阶段，接受候选排序颠倒解释，同时要求关闭SDK profiling、优先以单一时钟拆分forward内部各类开销并寻找优化方案。记录为基于现有证据的验收决定，不将算术精度/排名交换推断写成跨端query身份证明；PC/板端模型输入已逐位一致，不归因于已证实的传输损坏。代理可实施独立profiling-off计量候选并执行Host/原三帧回归及3预热＋30计量，原模型/SDK/BOOT/帧完成协议保持、失败停止、新目录保留r2。采用steady_clock记录Host、SDK等待/复制和ZG backend跨度，异步跨度不等同纯NPU耗时；数值原误差不改写，不新增ONNX中间输出/依赖或视频。具体改变算法、缓存、同步、并行或位流的优化方案仍据实测另议。

<a id="a156"></a>

## A156 · E0/N1/P1及H0完成（2026-10-07）

来源：整理前 AGENTS.md 第156–157行。

- E0/N1/P1及H0完成（2026-10-07）：阶段恢复后代理完成r2本地/ORT复核、P1预热三帧先对r6的前置门禁、FPAI构建和Lite四阶段。Host107/12注册/22输出通过；E0四帧与r6逐位一致；N1 27＋重复28次、27套输出/476捕获/实际CPU364000值一致；P1三预热＋30计量33次全部与r6一致，每帧0→745、1173七ZG组/六计算Host保持。四阶段exit0/stderr空/dmesg相同，52/124/604/113回传；程序8970f692b8636e420ae972277fb2a45b79b844895e0664fd99d8352e4cf00192，351包、BOOT/模型/RAW/SDK/CPU/桥/预处理/r6/r1保持，profiling开启。ORT27独立86项及旧308一致；同槽坐标最大2.77697、最高分坐标2.67562模型单位，S52_18_317前两名交叉支持排名交换推断而ORT query身份未证，原误差未重排、容限未通过。P1平均214.85948ms/4.65420Hz、P95 215.49764ms，forward占93.72%，≥5Hz及整机/长期未通过。H0只读资料完成，720p/骨架/VPU配套仍未知，不初始化视频。结果RUNTIME-RESULTS-20261007.md、evidence/runtime-20261007-r2/completion-review.json；SSH/SFTP已关闭。原E0/N1/P1任务已完成，停止自动执行；NEXT-GATE-20261007.md的N2/P2及E1/视频/容限/新依赖/profiling改动未批准，需讨论后再执行。旧暂停/未板测文字为历史。

<a id="a158"></a>

## A158 · E0/N1/P1已恢复（2026-10-07）

来源：整理前 AGENTS.md 第158–159行。

- E0/N1/P1已恢复（2026-10-07）：人工确认Lite已开机并设计要求继续中断任务，撤销该任务暂停。代理按原批准范围先读取恢复检查点，审查源码/ORT参考并补P1测量前r6门禁，新包新构建保留r1，再逐阶段Host107→E0→N1→P1。原模型/RAW/SDK/BOOT、profiling及异常停止条件保持；H0本机只读，视频/E1及容限另议。旧暂停文字为历史，不扩大为新训练或视频执行授权。

<a id="a160"></a>

## A160 · 全项目进度/恢复标记完成（2026-10-06）

来源：整理前 AGENTS.md 第160–161行。

- 全项目进度/恢复标记完成（2026-10-06）：当前仅要求整理进度，不解除此前E0/N1/P1暂停。根PROJECT-PROGRESS.md为全项目当前总览，约50%–60%仅首版工程管理粗估（主观工作包权重58/100），不是功能/数值通过率或剩余工期；实时采集终版和2026训练旁支另列。下次先读tools/pose-v1/RESUME-20261006.md及evidence/runtime-20261006-r1/progress-snapshot.json；先源码/参考复核并补P1测量前r6校验，用新修订/包/构建保留r1，再Host107→E0→N1→P1，视频另议。旧状态文件/README历史已折叠保留，暂停期间不连接、构建、推理或启用自动化。

<a id="a162"></a>

## A162 · E0/N1/P1暂停（2026-10-06）

来源：整理前 AGENTS.md 第162–163行。

- E0/N1/P1暂停（2026-10-06）：人工确认Lite已关机且不在现场，设计要求先中断任务，唤醒后继续。新隔离核心已交叉编译/构建身份核验，27样本＋重复ORT参考已生成；没有板端传输、Host107、新核心回归或N1/P1执行，不当作新工程/性能验收。停止连接重试、后台工作或自动唤醒；恢复先读evidence/runtime-20261006-r1/pause-checkpoint.json并完成源码/证据复核。原E0/N1/P1批准范围保持，待阶段恢复后。

<a id="a164"></a>

## A164 · E0/N1/P1实施与执行方已批准（2026-10-06）

来源：整理前 AGENTS.md 第164–165行。

- E0/N1/P1实施与执行方已批准（2026-10-06）：明确回复“同意，由代理执行”，批准NEXT-PHASE-PLAN-20261006.md。代理新增隔离运行核心、一次180秒原三样本＋首帧重复回归，既有Host107注册回归；通过后在既有ORT环境生成九组27固定样本＋重复参考、一次120秒28次板测；再做原三帧输出回归及一次120秒3预热＋30计量低日志基线。SDK profiling保持，模型/RAW/SDK/BOOT及r6源码程序保留，异常停止不自动重试；安全帧边界reset(1)沿用已验收协议，不作reset(0)。H0仅本机只读视频/骨架资料。新依赖、中间ONNX输出、误差容限、视频初始化及E1网络应用仍另议，批准不等于新阶段验收。

<a id="a166"></a>

## A166 · 难点复盘与下一阶段准备完成（2026-10-06）

来源：整理前 AGENTS.md 第166–167行。

- 难点复盘与下一阶段准备完成（2026-10-06）：总结Done.md并准备后续推进，代理把r1–r5历史记录折叠保留，集中整理环境/换行/构建/Host注册布局/融合ID/跨帧状态/数值候选/性能/HDMI及人工边界难点。仅读既有证据，新增prepare_next_phase.py实际核验27候选（九组各首/中/末，来自既有300），生成排序/时间预算分析；板端相邻同分29/30/31 vs ORT1/2/0不证明排序为全部误差根因，带取证207.230065ms＋另测PS5.781265ms仅约213ms预算提示。NEXT-PHASE-PLAN-20261006.md推荐E0核心→N1 27＋首帧重复→P1 3预热＋30计量、H0本机资料并行。尚未新模型/板测/编译或修改r6运行源码；新阶段实施/执行方与容限待确认，上一轮代理全权故障修复不自动扩展为新视频/性能范围。当前27仅身份选择不是数值验收，SDK profiling保持，相关关闭或优化另据实测讨论。

<a id="a168"></a>

## A168 · 跨帧同输出故障r6已解决并验收（2026-10-06）

来源：整理前 AGENTS.md 第168–169行。

- 跨帧同输出故障r6已解决并验收（2026-10-06）：代理完成构建/传输/Lite全阶段测试。r5实测计数首次0→745、次帧745→1222，SDK本帧绝对阈值提前满足；仅mixed_check.cpp每帧安全边界调用官方Device::reset(1)清FPGA状态、确认0，输出waitForReady及最终745后才下一帧，不做reset(0)/直接寄存器/SDK模型BOOT修改或Session重建。r6构建/Host107/离线/内存/apply/单/三全部退出0；131三帧回传/68内容/76状态，四次0→745，三份分数和姿态分别不同，重复308所有捕获及输出逐位一致，五CPU实际52000FP32由NumPy一致，1173七组/六计算Host/Gather保持。程序f826fc31441caf09ef22d94561672023737ab4c330ba22ec0159ecf7f77e144a，SDK3.39.0/设备25122301/icore24160628/291包保持，内核各阶段前后相同。mixed-three.acceptance.json及完整ONNX误差已生成；数值容限/MPJPE/持续性能未验收，约206.6–208.2ms少量取证前向不作5Hz通过。结果MIXED-FRAME-STATE-R6-RESULTS.md及evidence/mixed-20261006-frame-state-r6/completion-review.json；旧r3/r4/r5失败和原检查器保留，不重跑历史包或扩展到HDMI/RTSP及无关训练。

<a id="a170"></a>

## A170 · 当前混合推理难点执行方调整（2026-10-06）

来源：整理前 AGENTS.md 第170–171行。

- 当前混合推理难点执行方调整（2026-10-06）：明确将当前问题所有执行操作交由代理，要求优先排查并解决后报告。代理可直接执行当前问题的构建/传输/板端取证和有依据的最小修正验证，无需逐阶段代执行；保留旧证据和身份门禁，不将此授权扩展到无关训练、模型/权重更换、BOOT/位流替换或外部消息。原当前问题待批准取证的执行权限按此最新授权更新，修复结论仍须实测，不用猜测性配置或重复同一失败运行代替诊断。

<a id="a172"></a>

## A172 · r4三样本内容异常复核（2026-10-06）

来源：整理前 AGENTS.md 第172–173行。

- r4三样本内容异常复核（2026-10-06）：一次回传130项、四forward后退出1“不同CSI全部输出相同”，68内容1015040字节全有限、291包/SDK/设备/真实参数/1173覆盖及内核保持。每次caller/Input0与当前固定输入一致；309 Input0变化10431而ZG9185→TopK188暂存不变，310及重复308前段188/192/437变化但后段582/649和最终4300输出仍首帧，重复308前段不等首次。五适配节点对本次真实输入由NumPy重算28结果52000FP32逐位一致；Gather442未内容捕获不扩大验收。范围已缩至PS/NPU交接、完成状态/搬运/复用待查，未证明ready/cache或SDK故障。无三样本门禁，停止重跑/正常数值/显示/性能；原源码不改。结果MIXED-CONTENT-R4-THREE-FAILURE.md和evidence/mixed-20261006-content-r4/mixed-three-failure-review.json；MIXED-CONTENT-R5-READINESS-PLAN.md仅未批准候选，不执行reset/setReady(false)/sleep/重建Session等猜测修复。代理仅本机证据与SDK阅读，旧待三样本属历史。

<a id="a174"></a>

## A174 · r4单样本内容验收（2026-10-06）

来源：整理前 AGENTS.md 第174–175行。

- r4单样本内容验收（2026-10-06）：一次回传69项，291包/SDK/程序/设备身份一致，退出0/stderr空/内核前后相同。308/frame6/invocation0真实caller及Input0各10800FP32与固定输入逐位一致，17份Host内容253760字节全有限；七ZG及六计算Host实际回调，八ADDR→CPTR搬运115360字节，4300输出与r3单样本逐位一致。mixed-one.acceptance.json及独立内容复核已生成，单次207.07742ms不算持续性能，提供输出writeback未触发。仅MIXED-CONTENT-R4-COMMANDS.md H一次300秒同Session308/309/310/308内容诊断完整回传；失配保留部分记录停止，不自动重试/reset/cache/ready修改。连续输入问题仍未知，诊断改变时序不作修复证明，数值/性能未验收。结果MIXED-CONTENT-R4-ONE-RESULTS.md及evidence/mixed-20261006-content-r4/mixed-one-independent-review.json；代理仅本机分析，旧待单样本为历史。

<a id="a176"></a>

## A176 · r4 apply-only验收（2026-10-06）

来源：整理前 AGENTS.md 第176–177行。

- r4 apply-only验收（2026-10-06）：一次回传45项，1181原节点/1173HardOp经七实际ZG组完整唯一覆盖、八Host和固定成员/同步基线保持，十快照/汇总齐全；291包/SDK/程序/设备/RAW/PS身份一致，退出0/stderr空/内核前后相同，无模型forward/桥执行/content目录。apply-check.acceptance.json已生成，仅MIXED-CONTENT-R4-COMMANDS.md G一次180秒308内容取证并完整回传，17预期记录含caller/Input0/八暂存输入/七结果，提前输入失配停止时保留部分记录，不重试/改ready/cache或直接三样本。部署通过不证明真实Input0更新或r3故障修复；结果MIXED-CONTENT-R4-APPLY-RESULTS.md及evidence/mixed-20261006-content-r4/apply-independent-review.json，代理仅读本机文件，旧待apply为历史。

<a id="a178"></a>

## A178 · r4 SDK内存验收（2026-10-06）

来源：整理前 AGENTS.md 第178–179行。

- r4 SDK内存验收（2026-10-06）：一次回传28项，两16KiB ADDR SDK数据缓冲区六回读/24,576有限FP32逐位一致含正负零，与r3一致；device25122301/icore24160628、291包/SDK/程序身份通过，退出0/stderr空/内核前后相同，未Session/forward、content_capture=false。memory-check.acceptance.json已生成；仅MIXED-CONTENT-R4-COMMANDS.md F一次300秒apply-only完整回传，1173原覆盖/八Host/固定七组保持，核验前不内容前向或复用旧门禁/重试/复位。SDK复制不证明输入更新或NPU同步，r3故障未定位。结果MIXED-CONTENT-R4-MEMORY-RESULTS.md及evidence/mixed-20261006-content-r4/memory-independent-review.json；代理仅读本机文件，旧待内存为历史。

<a id="a180"></a>

## A180 · r4离线验收（2026-10-06）

来源：整理前 AGENTS.md 第180–181行。

- r4离线验收（2026-10-06）：一次完整回传32项，代理核验真实四RAW参数与r3一致、三PS输入32,400有限FP32与固定/ONNX/r3逐位一致、12注册及Gather保持；291包/15ARM头文件/两库/3.39.0及新程序身份通过，退出0/stdout及stderr空、内核前后相同，无设备/Session/NPU、content_capture=false。offline-check.acceptance.json已生成，仅MIXED-CONTENT-R4-COMMANDS.md E传新门禁，在BOOT/JTAG保持且无竞争访问时一次30秒SDK内存往返并完整回传；核验前不apply/forward或复用旧门禁。实际Session输入仍未取证，不作根因/修复结论；结果MIXED-CONTENT-R4-OFFLINE-RESULTS.md及evidence/mixed-20261006-content-r4/offline-independent-review.json，代理仅本机分析，旧待离线为历史。

<a id="a182"></a>

## A182 · r4 Host及内容路径验收（2026-10-06）

来源：整理前 AGENTS.md 第182–183行。

- r4 Host及内容路径验收（2026-10-06）：完整回传52项，107例/12注册/22CPU输出59,600有限FP32与固定/r3逐位一致、94Host CPTR桥事件/Gather保持；附加两模式SDK Host读回和模拟Input0别名四正例与NumPy逐位一致、错期望负例false且实际数据不改、未分配/FP16读取前拒绝。五捕获216000字节/汇总阶段完整，291包/SDK/程序身份匹配、退出0/stderr空/内核前后相同，无Device::Open/Session/NPU。host-check.acceptance.json已生成，仅MIXED-CONTENT-R4-COMMANDS.md D一次30秒离线并完整回传，核验前不硬件/复用旧门禁/重跑r3；实际Session Input0尚未取证，不能称根因或修复通过。结果MIXED-CONTENT-R4-HOST-RESULTS.md及evidence/mixed-20261006-content-r4/host-independent-review.json；代理仅读本机文件，旧Host待验为历史。

<a id="a184"></a>

## A184 · r4-final内容取证构建验收（2026-10-06）

来源：整理前 AGENTS.md 第184–185行。

- r4-final内容取证构建验收（2026-10-06）：GCC9.4/CMake3.24.2、ARM两包3.39.0完成五CPP编译/链接，代理核对291包/20来源/12构建副本/15ARM头文件/两库匹配。AArch64 PIE578960字节，SHA256ba8d53985fabdfdc12939d794825d31a0ee29bf9516567be5ba9356c515dcea7，直接Host/ZG依赖、无RPATH/RUNPATH；仅原JSON缩进warning147行已审查，无error。build.acceptance.json已生成，仅MIXED-CONTENT-R4-COMMANDS.md B/C新final目录传输＋Host107/附加纯Host内容测试并完整回传，不直接离线/硬件或复用旧门禁。SDK read/句柄API可编译不代表实际读回/Session内容或已修复，r3失败保持。结果MIXED-CONTENT-R4-BUILD-RESULTS.md及evidence/mixed-20261006-content-r4/build-review.json；代理仅读本机文件，旧未编译属历史。

<a id="a186"></a>

## A186 · 连续输入内容r4批准后交付（2026-10-06）

来源：整理前 AGENTS.md 第186–187行。

- 连续输入内容r4批准后交付（2026-10-06）：明确“同意”输入内容取证方案，代理保存r3五源码/脚本备份，新增--capture-host-content、实际caller SDK读回、Input0返回逐位比较、桥现有复制后的Host暂存/计算结果捕获及invocation；仅有界Host CPTR FP32，不新增设备读/寄存器，不跨次保留诊断caller句柄，不改原wait/copy/ready、CPU数学/Gather/融合/模型/RAW/SDK。Host107后附纯Host捕获/别名模拟及错期望/未分配/FP16拒绝路径；本机模拟Host/一/四次正例及11异常/提前停止通过，不算ARM/Session结果。最终包package-20261006-content-r4-final为291哈希/12构建/20来源，初始中间包保留勿用。仅MIXED-CONTENT-R4-COMMANDS.md A标签mixed-20261006-content-r4-final编译，核验后按新身份Host/离线/内存/apply/单/三逐阶段；不重跑r3或猜测性reset/cache修复。交付MIXED-CONTENT-R4-DELIVERY.md、evidence/mixed-20261006-content-r4/delivery-review.json；未新编译/板测，诊断影响时序不能作性能/已修复结论。

<a id="a188"></a>

## A188 · r3三样本异常停止（2026-10-06）

来源：整理前 AGENTS.md 第188–189行。

- r3三样本异常停止（2026-10-06）：一次mixed-three回传61项，四次前向后退出1“不同CSI全输出相同”，无summary/验收。三PS输入不同且与固定/ONNX一致，309/310有10431/10445元素变化、ONNX全部分数/坐标变化；板端三个4300输出却与308首帧及之前mixed-one逐位一致。每次七ZG/六Host回调、32桥事件，身份/绑定/参数/内核正常、available均689MiB；回调不证明新帧内容，约39ms后续耗时不得作性能通过。保留三帧结果，停止重跑/正常数值验收/后续硬件显示，不伪造三样本门禁。MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md为待批准新r4内容取证，实际caller Tensor/Input0/已复制Host暂存及Host结果逐次捕获，不猜测性改cache/ready/reset/模型/SDK。当前根因未知，运行源码保持；结果MIXED-FUSION-R3-THREE-FAILURE.md及evidence/mixed-20261006-fusion-r3/mixed-three-failure-review.json，代理仅本机数据/SDK阅读。

<a id="a190"></a>

## A190 · r3单样本混合工程验收（2026-10-06）

来源：整理前 AGENTS.md 第190–191行。

- r3单样本混合工程验收（2026-10-06）：mixed-one完整回传51项，退出0/stderr空；308/frame6一次前向，七ZG组和六Host计算节点实际执行，八SDK ADDR→Host CPTR搬运115360字节，完整4300有限FP32输出/参数/输入/绑定/291包/SDK/程序/设备身份通过，内核前后相同。mixed-one.acceptance.json已生成；单帧forward204.64506ms不作5Hz/持续性能结论，本次适配结果Host返回、提供输出缓冲区writeback未触发。初步ONNX有差异（分数最大0.00304520、同槽坐标1.32329583、各端最佳坐标0.01611638模型单位），无精度/MPJPE/物理单位或候选身份结论。仅MIXED-FUSION-R3-COMMANDS.md H一次300秒三帧+同Session重复首帧并完整回传，核验跨Session/同Session重复及不同输入响应后全误差讨论；不重试/改容限/模型/SDK。结果MIXED-FUSION-R3-ONE-RESULTS.md及evidence/mixed-20261006-fusion-r3/mixed-one-independent-review.json；代理仅本机分析，旧前向待验为历史。

<a id="a192"></a>

## A192 · 正式融合r3 apply验收（2026-10-06）

来源：整理前 AGENTS.md 第192–193行。

- 正式融合r3 apply验收（2026-10-06）：一次apply完整回传45项，退出0/stderr空/无failure；创建1181原绑定及部署后1181逻辑追溯完整，1173HardOp经七实际ZG组9185–9191完整唯一覆盖、固定成员及同步基线匹配，六计算Host与Input/Output保持，8622归9185。C++正式门检/本机独立复查及291包/SDK/程序/设备/RAW/PS身份通过，十快照/汇总齐全，内核前后相同；无forward/桥执行/模型输出。apply-check.acceptance.json已生成，仅MIXED-FUSION-R3-COMMANDS.md G一次180秒mixed-one/308完整回传，核验前不三样本/重试/复位/改模型或SDK。部署通过不宣称NPU计算、同步、数值或性能。结果MIXED-FUSION-R3-APPLY-RESULTS.md及evidence/mixed-20261006-fusion-r3/apply-independent-review.json；代理仅本机分析，旧待apply属历史。

<a id="a194"></a>

## A194 · 正式融合r3内存验收（2026-10-06）

来源：整理前 AGENTS.md 第194–195行。

- 正式融合r3内存验收（2026-10-06）：一次memory完整回传，代理核验28回传/291包/15ARM头文件/两库/3.39.0及新程序身份匹配，退出0/stderr空；device25122301/icore24160628、SDK ADDR PLDDR两16KiB六回读/24,576有限FP32逐位一致含正负零，内核前后相同。memory-check.acceptance.json已生成；仅MIXED-FUSION-R3-COMMANDS.md F一次300秒正式apply，1181原绑定/七实际ZG组1173完整唯一覆盖/八Host/固定成员与同步基线保持，完整回传核验前不forward，不自动重试/复位或复用旧门禁。SDK复制不证明NPU同步，新融合函数实际运行仍待Session门检。结果MIXED-FUSION-R3-MEMORY-RESULTS.md及evidence/mixed-20261006-fusion-r3/memory-independent-review.json；代理仅本机分析，旧内存待验证属历史。

<a id="a196"></a>

## A196 · 正式融合r3离线验收（2026-10-06）

来源：整理前 AGENTS.md 第196–197行。

- 正式融合r3离线验收（2026-10-06）：完整回传，代理核验真实四RAW参数与r2一致、两K=100及两份完整ScatterND索引网格；三PS输入32,400有限FP32与固定/ONNX/r2逐位一致、12注册和原Gather保持。32回传/291包/15ARM头文件/两库/3.39.0及程序e8d66113…e6c696a8身份匹配，退出0/stdout及stderr空、内核前后相同，无设备初始化/Session/NPU。offline-check.acceptance.json已生成；仅MIXED-FUSION-R3-COMMANDS.md E传新验收，在BOOT/JTAG保持且无竞争访问时一次30秒SDK内存往返并完整回传，核验前不apply/forward或复用旧门禁。结果MIXED-FUSION-R3-OFFLINE-RESULTS.md及evidence/mixed-20261006-fusion-r3/offline-independent-review.json；代理仅本机分析，旧离线待验证属历史。

<a id="a198"></a>

## A198 · 正式融合r3 Host验收（2026-10-06）

来源：整理前 AGENTS.md 第198–199行。

- 正式融合r3 Host验收（2026-10-06）：完整回传后代理核验107例（18正常/89拒绝）、12注册、22输出/59,600有限FP32与固定及r2逐位一致、Gather保持；94桥事件均Host CPTR（84输入/10输出），45回传/291包/15ARM头文件/两库/3.39.0及程序e8d66113…e6c696a8身份通过，退出0/stderr空、内核前后相同。host-check.acceptance.json已生成；仅MIXED-FUSION-R3-COMMANDS.md D传新验收后一次30秒离线并完整回传，核验前不硬件/重跑/复用旧门禁。无设备初始化/完整Session/NPU，新融合追溯函数尚未ARM执行。结果MIXED-FUSION-R3-HOST-RESULTS.md及evidence/mixed-20261006-fusion-r3/host-independent-review.json；代理仅本机分析，旧Host待验收属历史。

<a id="a200"></a>

## A200 · 正式融合r3构建验收（2026-10-06）

来源：整理前 AGENTS.md 第200–201行。

- 正式融合r3构建验收（2026-10-06）：GCC9.4/CMake3.24.2、ARM Icraft/CustomOp3.39.0完成五CPP编译/链接；代理本机核对291包/17来源/11构建副本（含静态融合基线头）/15ARM头文件/两后端库匹配。AArch64 PIE555800字节，SHA256e8d66113ad3d9a34f9f210e5f7038560bc3dbfa681b9a057d748ff39e6c696a8，直接Host/ZG依赖、无RPATH/RUNPATH，仅旧JSON缩进warning143行且已审查，无error。build.acceptance.json已生成；仅MIXED-FUSION-R3-COMMANDS.md B新目录传输＋C Host107完整回传，核验前不offline/硬件或复用旧门禁。新API可编译不代表映射运行/正式apply/前向通过，代理未编译/板端接入。结果MIXED-FUSION-R3-BUILD-RESULTS.md及evidence/mixed-20261006-fusion-r3/build-review.json，旧未编译属历史。

<a id="a202"></a>

## A202 · 正式融合追溯r3批准后交付（2026-10-06）

来源：整理前 AGENTS.md 第202–203行。

- 正式融合追溯r3批准后交付（2026-10-06）：明确“同意”MIXED-FUSION-BINDING-FIX-PLAN.md，代理保存r2源码/核验器备份并应用修正。创建1181原绑定/1173HardOp全ZG，部署仅实际绑定七组经固定merge_from完整唯一覆盖1173，八Host保持；组ID/同一后端实例/同步表/基线变化拒绝，原层数0不当缺覆盖。保留快照、新增原到有效ID及汇总，核验器识别HardOpNode并独立复查，apply无forward范围保持。新C++/JSON基线、本机回放18异常＋非布尔标记拒绝、291包哈希/11构建/17来源/LF及AST通过；模拟记录不算ARM执行。原infer/CMake/CPU/桥/预处理/forward保持，未编译或板测。当前仅MIXED-FUSION-R3-COMMANDS.md A新标签mixed-20261006-fusion-r3构建，核验后Host→离线→内存→一次apply逐阶段，不复用旧门禁/重跑r2/直接mixed。交付MIXED-FUSION-R3-DELIVERY.md、evidence/mixed-20261006-fusion-r3/source-and-package-review.json；旧待批准为历史。

<a id="a204"></a>

## A204 · 绑定快照r2取证完成（2026-10-06）

来源：整理前 AGENTS.md 第204–205行。

- 绑定快照r2取证完成（2026-10-06）：一次apply完整回传45项，身份/设备/RAW/PS和内核正常，Session创建及apply返回后仍退出1于原8622直接查绑定。十份快照显示创建1173原HardOp均ZG，部署七组9185–9191实际ZG绑定，merge_from恰好覆盖1173原节点一次，无遗漏/重复/额外成员，8622归9185；六Host及Input/Output保持。仅本机审计实际快照和九异常拒绝通过、完整原到组映射保存；428原条目layer_count0不作缺覆盖判据。未forward、不生成apply门禁；正式C++/gate未改，HardOp与实际HardOpNode识别差异待一起修正。MIXED-FUSION-BINDING-FIX-PLAN.md为新待批准方案，暂停新硬件/前向，不降低1173/六Host要求、不改SDK自动优化。结果MIXED-BINDING-R2-APPLY-RESULTS.md、evidence/mixed-20261006-binding-r2/apply-independent-review.json及binding-snapshot-audit；代理仅本机文件分析。

<a id="a206"></a>

## A206 · 绑定快照r2内存验收（2026-10-06）

来源：整理前 AGENTS.md 第206–207行。

- 绑定快照r2内存验收（2026-10-06）：一次memory-check完整回传，代理核对28回传/290包/15ARM头文件/两库/3.39.0及新程序94a03a90…bd061248身份一致；退出0/stderr空，device25122301/icore24160628，两16KiB SDK ADDR PLDDR缓冲区六回读/24,576有限FP32逐位一致含正负零，dmesg完整前后相同。memory-check.acceptance.json已生成，按MIXED-BINDING-R2-COMMANDS.md G仅一次300秒Session创建/apply公共绑定快照取证，原1173/六Host门检保持，非0仍完整回传，不forward或自动重试/复位/降低计数。仅SDK设备复制通过，不证明NPU同步/完整绑定/数值；实际融合映射待分析。结果MIXED-BINDING-R2-MEMORY-RESULTS.md、evidence/mixed-20261006-binding-r2/memory-independent-review.json；代理仅本机文件分析，旧内存待回传属历史。

<a id="a208"></a>

## A208 · 绑定快照r2离线验收（2026-10-06）

来源：整理前 AGENTS.md 第208–209行。

- 绑定快照r2离线验收（2026-10-06）：完整执行回传，代理本机核验32回传/290包/15ARM头文件/两库/3.39.0及程序94a03a90…bd061248身份一致，退出0/stdout及stderr空；真实RAW两个K=100、两份ScatterND索引与完整坐标网格一致，三PS输入32,400有限FP32与固定及ONNX参考逐位一致、12注册和原Gather保持。dmesg完整前后相同，无设备初始化/完整Session/NPU。offline-check.acceptance.json已生成；按MIXED-BINDING-R2-COMMANDS.md F传新门禁，在BOOT/JTAG保持且无AI/显示竞争访问时仅一次30秒SDK两16KiB内存往返并回传，核验前不apply/mixed，不重跑旧阶段或复用r1门禁。结果MIXED-BINDING-R2-OFFLINE-RESULTS.md及evidence/mixed-20261006-binding-r2/offline-independent-review.json，旧离线待回传属历史。

<a id="a210"></a>

## A210 · 绑定快照r2 Host验收（2026-10-06）

来源：整理前 AGENTS.md 第210–211行。

- 绑定快照r2 Host验收（2026-10-06）：完整回传后代理本机核验107例（18正常/89拒绝）、12注册、22输出/59,600有限FP32逐位一致，与r1已验收输出相同；290包/45回传/15ARM头文件/两库/3.39.0和新程序94a03a90…bd061248身份通过，退出0/stderr空，94次桥搬运均Host CPTR，dmesg完整前后相同。host-check.acceptance.json已生成；提前offline仅三预检文件/290OK，确认程序未启动，本机失败目录保存在offline-preflight-missing-gate。按MIXED-BINDING-R2-COMMANDS.md E传新Host验收、固定目录受保护改名保留板端预检后仅一次30秒offline并回传；不重跑Host/复用r1门禁/直接硬件。无Device::Open/完整Session/NPU/快照映射验收，代理未接入板端。结果MIXED-BINDING-R2-HOST-RESULTS.md、evidence/mixed-20261006-binding-r2/host-independent-review.json及offline-preflight-review.json；前述待回传为历史。

<a id="a212"></a>

## A212 · 绑定快照r2构建验收（2026-10-06）

来源：整理前 AGENTS.md 第212–213行。

- 绑定快照r2构建验收（2026-10-06）：FPAI GCC9.4/CMake3.24.2、ARM Icraft/CustomOp3.39.0完成配置/五CPP编译/链接；代理核对290包项/10源码及副本/15头文件/Host＋ZG库/脚本/manifest匹配，快照源码与批准候选一致。新AArch64 ELF64 PIE 518712字节，SHA25694a03a903a4a97f229b1549dcbd1bade193d60dbb23753c1f030431fbd061248，直接Host/ZG依赖、无RPATH/RUNPATH，仅原142缩进warning且已审查，无error。build.acceptance.json已生成，可人工B创建新20261006-binding-r2目录/传输后C仅Host107完整回传，核验再offline/memory/一次apply取证。公共字段编译通过不作实际快照/映射通过；不重跑旧r1/复用旧门禁/改SDK或直接mixed。代理只读本地审查，未Docker编译/程序/板端接入。结果MIXED-BINDING-R2-BUILD-RESULTS.md、evidence/mixed-20261006-binding-r2/build-review.json；旧新r2未编译为历史。

<a id="a214"></a>

## A214 · 绑定快照r2方案已批准并应用（2026-10-06）

来源：整理前 AGENTS.md 第214–215行。

- 绑定快照r2方案已批准并应用（2026-10-06）：回复“同意方案”，mixed_check.cpp已与binding-snapshot候选逐字节一致，原r1源码已备份。仅Session创建/apply后读取完整绑定、运行/后端视图、ZG hardop_map/net_hardop/merge_from/sync索引，不再调用autoMerge，不改SDK/默认优化、原数学/前向/数据桥及严格1173＋六Host门检。新包package-20261006-binding-r2准备290项哈希通过，与r1的289非manifest载荷相同，13源身份只mixed_check.cpp变化，原CPU/推理器/CMake/模型/RAW/输入及旧r1二进制/失败目录保持。尚未新编译/测试/板端执行。按MIXED-BINDING-R2-COMMANDS.md先A新BuildTag mixed-20261006-binding-r2构建，代理审阅后新目录Host107/离线/内存各门禁，再一次300秒apply取证无forward；新验收不能用旧文件改名/改SHA，取证可能仍退出1，不自动接受或进入mixed。登录shell不单独set -eu，用独立sh运行，非0完整回传，不删目录/重试/复位。应用及静态证据evidence/mixed-20261006-binding-r2/source-applied.json与package-preparation.json。新正式融合覆盖核验仍须实际数据审阅；下述候选待批准为历史。

<a id="a216"></a>

## A216 · apply-r1失败及SSH退出审查（2026-10-06）

来源：整理前 AGENTS.md 第216–217行。

- apply-r1失败及SSH退出审查（2026-10-06）：在SSH登录shell直接set -eu，已有run-apply-check使test ! -e非0→errexit关闭登录shell。代理按特殊问题/日志权限SSH只读ls、SCP取回已有结果，35回传/290包及程序/SDK/上一memory身份通过；实际apply退出1，已session_applied，原HardOp8622未在预期backendBindings查到，bindings仅Input0一条，未forward/模型输出/桥搬运，完整dmesg前后相同。不可记为Session部署验收/NPU计算失败，不生成apply.acceptance或进入mixed。SDKautoMerge/merge_from支持合并追溯，但实际映射未知；仅加两阶段完整绑定/视图/ZG成员快照的候选MIXED-BINDING-SNAPSHOT-PLAN.md/.candidate.patch已准备，未应用/编译/运行。新核心修改/再apply方案须明确批准，保留1173＋六Host门检，不自动改SDK/计数/BOOT/模型/重试/复位/删目录。代理未SDK初始化或模型执行、口令未落文件；结果MIXED-APPLY-FAILURE-20261006.md及evidence/mixed-20261006-r1/apply-failure-review.json。旧当前应执行apply的文字在本次失败后暂停。

<a id="a218"></a>

## A218 · mixed-r1 SDK内存往返验收（2026-10-06）

来源：整理前 AGENTS.md 第218–219行。

- mixed-r1 SDK内存往返验收（2026-10-06）：一次30秒memory-check完整回传，代理核对28回传/290包、15ARM头文件/Host＋ZG库/两包3.39.0/程序7cf761f1…52722a17及上一offline验收匹配，退出0/stderr空/阶段完整/dmesg前后相同。Device::Open成功，device25122301/icoreFMSHZGV3TECH-AID - 24160628；两16KiB缓冲区ADDR、AXIZG330AIPLDDRMemRegionNode、chunk16384/offset0。固定程序验证区域归属及非重叠；六输出/三模式24,576有限FP32逐位一致含-0/+0，最大差0。仅SDK Host↔设备搬运，无完整Session/模型前向/NPU生产者到CPU消费者同步或精度通过。memory-check.acceptance.json已生成，传入gates后在BOOT/JTAG保持及无竞争访问前提下，仅300秒apply-check（创建/apply/1173HardOp＋六Host绑定、不forward），回传核验再mixed-one；失败停止保存、不重试/复位/改配置。代理仅文件分析、未板端接入。结果MIXED-MEMORY-RESULTS-20261006.md及evidence/mixed-20261006-r1/memory-independent-review.json；旧memory未执行属历史。

<a id="a220"></a>

## A220 · mixed-r1离线真实参数/PS验收（2026-10-06）

来源：整理前 AGENTS.md 第220–221行。

- mixed-r1离线真实参数/PS验收（2026-10-06）：正式offline-check完整回传，代理核验32回传/290包、15ARM头文件/Host＋ZG库/两包3.39.0及程序7cf761f1…52722a17/上一Host验收身份通过。原RAW四参数已物化，TopK188/437 K=100；ScatterND582/649各50,400字节有限整数索引为完整100×14×3网格，未fixture替换。三CSI输入32,400有限FP32与固定/ONNX逐位一致，12注册/Gather保持；退出0/stdout及stderr空/阶段完整/dmesg前后相同。mode offline-check设备初始化false，无完整Session/前向；静态1173HardOp不作绑定通过。offline-check.acceptance.json已生成，传板并确认BOOT/JTAG未改变、无其他AI/显示占用后，可按已批准顺序仅30秒memory-check（SDK两16KiB、显式allow-device-init），回传核验后再apply。区域不明/身份变化/超时/OOM/总线/SDK异常即停，不重试/复位/改配置。代理仅文件分析，未板端接入。结果MIXED-OFFLINE-RESULTS-20261006.md及evidence/mixed-20261006-r1/offline-independent-review.json；旧offline未执行属历史。

<a id="a222"></a>

## A222 · offline缺gate失败预检证据已审阅（2026-10-06）

来源：整理前 AGENTS.md 第222–223行。

- offline缺gate失败预检证据已审阅（2026-10-06）：现场反馈Host验收已传板并回传失败目录，代理读取确认仅package-check/timeout-path/version三文件、290项全部OK、GNU timeout8.30，无results/exit/SDK审计/程序日志；与先前缺host-check.acceptance异常及runner门禁顺序一致，离线程序未启动。可人工在/tmp/pose-v1-mixed-validation/20261006-r1用固定兄弟目录名保留改名，再执行一次30秒offline-check并回传；目录/验收/源目标检查失败即停，不覆盖，不重跑Host/自动硬件。代理未板端接入/执行/改源码。本次仅预检证据审阅，offline程序尚未验证、无offline.acceptance；evidence/mixed-20261006-r1/offline-preflight-review.json及MIXED-VALIDATION-COMMANDS.md。旧失败目录待回传为历史。

<a id="a224"></a>

## A224 · mixed-r1 Host桥独立验收（2026-10-06）

来源：整理前 AGENTS.md 第224–225行。

- mixed-r1 Host桥独立验收（2026-10-06）：完整回传，代理文件核验107例=18正常/89拒绝、12注册、22输出/59,600FP32全有限逐位一致最大差0；新三类桥实际搬运、五节点事件、指针均Host CPTR，Gather保持。包290/回传45哈希、15ARM头文件/Host＋ZG库/两包3.39.0及程序7cf761f1…52722a17匹配；ldd完整、退出0/stderr空、完整dmesg前后相同、available686→687MiB。host-check.acceptance.json已生成，用户可传板；此前offline预检失败目录仍需保留回传审阅，再固定子目录改名继续离线。仅新注册/Host暂存回归验收，无真实RAW/完整Session/Device::Open/NPU/部署数值或性能通过，不重跑Host/直接硬件。代理仅文件分析、未板端接入。结果tools/pose-v1/MIXED-HOST-RESULTS-20261006.md及evidence/mixed-20261006-r1/host-independent-review.json；下述待完整回传为历史。

<a id="a226"></a>

## A226 · mixed Host运行/离线预检反馈（2026-10-06）

来源：整理前 AGENTS.md 第226–227行。

- mixed Host运行/离线预检反馈（2026-10-06）：截图显示B文件已传板、host-check runner exit0；本机预期回传目录和host-check.acceptance.json均未取得，新107桥例/12注册/输出及身份未独立验收。提前启动offline-check，在加载gates/host-check.acceptance.json时FileNotFoundError；核对runner，此处在SDK审计和程序调用前，离线程序未执行。先回传run-host-check，代理核验生成验收后传入gates；不要重跑Host或执行硬件。失败预检run-offline-check已在门禁前创建，需要原样回传，确认无results/exit.txt并在Host验收后按固定子目录保留改名，再进入离线；不删除/覆盖、改runner/SDK/模型或绕过门禁。补充命令tools/pose-v1/MIXED-VALIDATION-COMMANDS.md，证据evidence/mixed-20261006-r1/host-offline-gate-feedback.json和host-exit0-offline-missing-gate-user.png，代理未接入板端。

<a id="a228"></a>

## A228 · mixed-r1构建验收（2026-10-06）

来源：整理前 AGENTS.md 第228–229行。

- mixed-r1构建验收（2026-10-06）：FPAI GCC9.4/CMake3.24.2完成配置/五CPP编译/链接；代理主动读取日志/产物，290项包、10源码/副本、15ARM头文件、Host/ZG库/两包3.39.0及AArch64 PIE身份通过。程序SHA2567cf761f1dd7d1ca1bf8a1db1826e4d9b34574b1a8dc0ac662c987eed52722a17。唯一-Wmisleading-indentation是mixed_check.cpp142行版本JSON输出三语句同一行，if仅控制逗号，其余无条件输出符合预期；未改源码/包/脚本，不重编译。build.acceptance.json已生成，可人工继续既定B传输后C仅host-check，回传再核验；新桥107例/SDK内存/完整Session/NPU/数值仍未通过。代理未执行Docker/编译/程序/SSH或设备访问。结果tools/pose-v1/MIXED-BUILD-REVIEW-20261006.md及evidence/mixed-20261006-r1/build-warning-review.json；下述新C++未编译为交付时历史。

<a id="a308"></a>

## A308 · 首版系统实施（2026-10-04）

来源：整理前 AGENTS.md 第308–308行。

- 首版系统实施（2026-10-04）：PS原始CSI回放预处理→PS/NPU混合推理→单人14关节固定三维视角→HDMI＋H.264 RTSP；采用2024 epoch442，NPU与双路均须验收，≥5Hz/争取10Hz、板端画面P95≤500ms、播放器延迟另测。新增`software/pose_v1`与`tools/pose-v1`；Conda验证环境，位于当前worktree `.local/pose-v1-conda`，Python3.10.21/NumPy2.2.5/h5py3.16.0/PyWavelets1.8.0，使用缓存离线完成，不绑定koala或更改既有环境。已完成启动分区9文件与镜像哈希一致审计、GCC9.4 arm64交叉编译及真实Lite纯预处理数值测试；3份真实CSI在主机/板端float32张量逐位一致，约5.70–5.78ms/样本，四类非法记录拒绝。±π合成边界差异仍达6.2406，总体数值门检未通过、未放宽容限或修改展开规则。实际运行AI_MATE/HDMI配套仍未知，uEnv引用第二分区download.bit但先前根目录未找到，相关设备/寄存器访问已暂停，等待启动串口日志；不得替换BOOT/位流、尝试未确认的寄存器或全CPU/电脑推理替代。FPAI实际SDK/CustomOp为arm64 3.39.0，原挂载`D:\FPGACompetitionProject`，本次构建源码明确从当前worktree复制到容器临时目录。尚未实现/验收板端TCP服务、混合推理、绘图、HDMI/编码RTSP或30分钟闭环，不将回放发送端存在当作网络链路通过。已新建根目录`Logs`，实际日志未提供；证据见REFERENCES.md第18节、Done.md与tools/pose-v1/evidence。后续安装/启动配置/模型/FPGA变更仍先讨论批准。

<a id="a329"></a>

## A329 · 项目目标

来源：整理前 AGENTS.md 第329–329行。

- 项目目标：基于 Wi-Fi CSI（信道状态信息）实现 3D 人体姿态建模；滤波降噪、部分算子加速、高速 DMA、HDMI 骨架显示只是当前候选方向，不代表全部必须实现，不自行把候选项扩展为必做任务。当前将采集接口/格式、模型和算法规格留空，后续顶层架构设计时再讨论；不自行填入，不在当前阶段继续要求确定这些内容。
