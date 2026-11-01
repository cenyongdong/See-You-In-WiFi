# 视频、常驻生命周期与计量的实施历史

2026-10-13从AGENTS.md迁出，按主题保存原记录；原文“当前”“已批准”“下一步”和暂停/恢复只表示当时状态，不是现行进度或新的执行授权。最新进度见[PROJECT-PROGRESS](../../../PROJECT-PROGRESS.md)，执行规范以[AGENTS.md](../../../AGENTS.md)为准。源行编号与迁移清单用于追溯；不改写原失败、修订或验收边界。

<a id="a050"></a>

## A050 · 公开read真实画面有限门检完成（2026-10-10）

来源：整理前 AGENTS.md 第50–51行。

- 公开read真实画面有限门检完成（2026-10-10）：阶段恢复后隔离input-read-r1，程序70c9df9f…ae2082d／manifest dbf88b3f…ad37d06f，403载荷126来源。仅设备输入改公开Tensor::read直写自有Host CPTR，旧桥／原主fbf330d7…acb8702d／数学／Gather／模型／SDK／BOOT及Host输入、输出写回保持；新桥实际Host107／12注册／59600与Native read8／ARM read11拒绝通过。单VPU实际capture→主线程单Engine4＋103共107／1615700FP32逐位旧参考，旧S23失败样本四次正确；1712对象／856shadow／856查询＋963元数据稳定，计数非DMA fence，底层根因未证。108NV12／149299200字节逐位Native，824编码／归还／解码覆盖107来源／实际PTS／7364关节通过，298NoInput／419重复不计新姿态；正常drain／LAST／两STREAMOFF／join后Engine释放／七项保存／内核同。准备普通29无需规整（0）；最终MemAvailable746760KiB／CmaFree18744KiB／普通23仅现场。旧失败／暂停证据保持，整体暂停已撤销，本批程序／连接均结束无后台。ADR_30、INPUT-READ-RESULTS/NEXT及evidence/input-read-20261010-r1 completion/next-checkpoint为最新入口；下一新组合显示／TCP／owned-AU门检，不回填旧网络结果或宣布长期／5Hz／HDMI／零拷贝。估算83/100保持；以下准备及暂停状态为历史。

<a id="a052"></a>

## A052 · 真实画面故障任务恢复（2026-10-10）

来源：整理前 AGENTS.md 第52–53行。

- 真实画面故障任务恢复（2026-10-10）：阶段恢复后，撤销整体暂停。旧picture-r1失败及暂停证据保留，不重跑。已核验公开Tensor::read签名和Host起点/容量契约，新增隔离input-read-r1候选，仅设备输入read直写自有Host CPTR；Host输入、输出写回、数学、模型、SDK、BOOT及异常快照保持。ADR_30记录决策；目前126来源/403载荷已冻结，尚未编译或板测，不认定已修复。

<a id="a054"></a>

## A054 · 主动暂停真实拥有画面任务（2026-10-10）

来源：整理前 AGENTS.md 第54–55行。

- 主动暂停真实拥有画面任务（2026-10-10）：真实拥有画面picture-r1已实现、构建及Native／ARM五组契约通过；一次硬件首次VPU启动成功，单上下文三窗4＋长阶段16共20前向302000FP32正确，第21次inv20／S23_30_330／192索引144有限非整数／8坏段失败，完整103未过。坏段同次前一slot0复制同偏移，两轮PL DDR源94080字节正确，对象稳定／168计数234；具体瞬时复制责任未证。20画面采用、21NV12逐位Native、392解码前缀／20来源／实际PTS／1330关节过，3采样未捕获，不记正常drain／LAST。异常原文及3输入47760／两晚源保留；两abort STREAMOFF／join／七项保存／原内核同，全部程序／连接结束。一规整66.20272ms普通9→16，最终745428KiB／CmaFree1604／普通10仅现场，无清缓存／重启／CMA／BOOT变化。根因未修，83/100保持。 当前整个任务暂停，停止构建／连接／板测／后台／自动唤醒，等待独立执行许可。7d421b40…b1b59e9／manifest e7c4b944…01adb98，403包118来源；旧主和单次常驻保持。恢复先读RESUME-PICTURE-20261010、ADR_29及picture-20261010-r1 pause-checkpoint；不重跑旧失败或接续inv21，先本机身份和公共搬运路径审查。旧“当前已完成”仅前阶段历史。

<a id="a056"></a>

## A056 · 单次常驻生命周期完成（2026-10-10）

来源：整理前 AGENTS.md 第56–57行。

- 单次常驻生命周期完成（2026-10-10）：单次常驻r1 c4c5caaf…c601822／manifest45dfbd83…1f0fc8a，403包108来源；Native／ARM阶段13、107计数16、原生命周期6／Run9拒绝过，原Host107／12注册59600身份复用。实际单VPU／单主线程Engine连续三窗4＋103合107前向1615700FP32逐位旧参考、518合成图像／实际PTS／像素通过，520packet／93978字节／正常drain-LAST／两STREAMOFF／join后Engine销毁。192源109232128／109285376保持，1712对象／856shadow、856查询234、963元数据稳定；原模型／SDK／BOOT／数学／ready/reset(1)／745和异常两晚源保持。一次规整144.80296ms／普通9→28，编码进入31→29→21／首次20；不是永久首启动修复或已证阈值。exit0／stderr空／原内核同／七项保存成功，所有项目程序／端口／代理连接结束，最终745488KiB／CmaFree28892／普通30仅现场。旧坏块未复现／根因未修，未显示／网络／HDMI／持续5Hz／长期／零拷贝；83/100保持。 诊断仅新目标824→856行，旧主fbf330d7…cb8702d／旧model-vpu4bab1a1d…49aab2a保持。全局调用0–106、帧100000–100106，无阶段重开／重建；stage日志同对象，清理actual/null分开。979返回文件核验，旧计数审查器824限制的本机错误保留，新适配器856修正，未重跑板测。ADR_28／02及RESIDENT-SEQUENCE-RESULTS/NEXT、resident-sequence-20261010-r1 completion/next-checkpoint为当前入口；下一真实拥有画面仅准备，旧当前为历史。

<a id="a058"></a>

## A058 · 同程序模型／合成VPU对照结束（2026-10-10）

来源：整理前 AGENTS.md 第58–59行。

- 同程序模型／合成VPU对照结束（2026-10-10）：同ELF模型／合成VPU对照r2已结束：Native／ARM6生命周期及9运行拒绝过，原Host107／12注册59600身份复用；model-three4、vpu-three4及model-103共111前向1676100FP32逐位旧参考，310合成图像／实际PTS过。最后vpu-103在首次capture前DQBUF EIO，内核MVX固件order7／512KiB普通页失败；Engine未创建、前向0，无模型坏块复现。规整3次有记录但仍失败，不是首启动可靠性修复；两abort STREAMOFF／join／七项保存过，成功内核同而最后新增错误完整保留。原数学／模型／SDK／BOOT与异常两晚源保持，全程序／端口／代理连接结束。根因未修、并发103／长期／5Hz／HDMI未过，83/100保持。 r2 4bab1a1d…49aab2a／manifest28d76b02…cde6da0，403包102来源；1776对象／888shadow、888查询234、999元数据稳定。资源规整61.46912／15.20305／14.12106ms，共同与两VPU前各一次，非失败后循环重试。末次9→7→0普通高阶页，释放后740060KiB／CmaFree40／普通8仅现场。清理Engine_destroyed为null reset点，不证明创建。ADR_27／02、MODEL-VPU-RESULTS/NEXT及model-vpu-20261010-r2 completion/next-checkpoint为当前入口；下一资源生命周期仅准备，旧当前／传输阻断为历史。

<a id="a090"></a>

## A090 · r4源读回实施及有限回归（2026-10-09）

来源：整理前 AGENTS.md 第90–93行。

- r4源读回实施及有限回归（2026-10-09）：

审阅批准后新增异常后两轮Tensor::read及源区域/地址元数据；仅当前已验证源、单轮≤原暂存且≤1MiB、两轮间不写盘，无直接ADDR/BOTH解引用/显式wait/reset/cache/新forward，原错误保留。a7903f6a…ba21cf6/manifest4f85e814…705aa8d，403包63来源；Host107/12注册59600FP32/IPC通过，Host192两轮94080字节逐位暂存，尚非设备源。初始工具延误0输入/5s超时；预置客户端后4前向60400FP32/495本地帧通过但DESCRIBE404无网络，旧现场保留。新首URI就绪控制，同包/门禁/180s在新目录4前向60400FP32/499编码469网络2730关节/四来源实际PTS像素通过，首次DESCRIBE200；未伪造404分支通过。合8正确前向120800值，坏值均未复现、模型错误设备源读回0次，不称root修复或永久可靠。实际ARM XRT库a29e4eee…749dc96匹配板端，copy/read入口委托区域接口已核，具体DMA/cache未穷尽。本轮规整0/模型SDKBOOT帧协议保持/最终内核同/子回收/source0/端口释放/Engine join后销毁，全连接结束。当前入口SOURCE-READBACK-R4-RESULTS及source-readback-20261009-r4 completion/next-checkpoint；ADR_17更新，旧R3三块95零+NaN保留未解。下一保留异常捕获到有限覆盖或自然启动、继续区域路径审计，不循环制造故障；旧尖峰/5Hz/103/HDMI/长期未过。

<a id="a094"></a>

## A094 · 纯计时及失败输入r3结果（2026-10-09）

来源：整理前 AGENTS.md 第94–97行。

- 纯计时及失败输入r3结果（2026-10-09）：

审查批准后代理实施新隔离timing_frames、SDK-free持久化和CPU异常Host暂存捕获，原数学/等待/复制/reset(1)/745/双缓冲/子程序保持。r2发现Host探针的旧局部日志指针寿命已结束，在77正确例后主动TERM exit143，未执行探针/硬件；新r3仅公共configure(nullptr,false)修正探针上下文，不解释旧硬件异常。r3程序6ce50e14…39ea1fd/manifest529bc282…187cd07，403载荷61来源，Host107/12注册59600FP32/IPC通过，9持久化拒绝和真实192探针47040字节逐位/0.5唯一非法索引通过。原三窗首帧188有限性拒绝，180值720字节完整捕获，96值在[0,128)/[256,384)/[512,640)改变为95零+索引11的0xffffffff NaN，其余84逐位旧308桥输入；不是微小定点误差，但源设备未读回、缓存/DMA/NPU/VPU责任未证。diag0/timing0/profiling-off仍失败，额外readiness单因解释不足；0完整结果/120失败回传，四真实RAW参数/融合/身份/内核同/STREAMOFF两端0/子回收/network0/端口释放/Engine join后销毁。规整0次，未改BOOT/CMA/SDK/模型或清缓存/重启，无后台/会话。当前读FORWARD-TRACE-R3-RESULTS、ADR_17和forward-trace-20261009-r3/next-checkpoint；下一有界源元数据+两次SDK读回计划准备未执行，r1/r2/r3不重跑、不放宽finite/索引门禁；原221.61ms尖峰/严格5Hz/103/HDMI/长期仍待，旧完成结论保留。

<a id="a098"></a>

## A098 · 前向尖峰取证r1结果（2026-10-08）

来源：整理前 AGENTS.md 第98–101行。

- 前向尖峰取证r1结果（2026-10-08）：

新隔离d4506060…da4f7e/403包57来源，原Engine/桥/子程序不改。Host107/12注册/59600FP32及IPC通过，原三窗重复4次60400FP32/501编码471网络通过。trace-5hz前三次45300FP32逐位旧参考，inv3/frame100003在GatherElements192两输入复制后因非有限整数索引退出1，未到inv28；213条局部记录、145失败回传，旧221.61ms尖峰原因未证。前三次桥等待164.46/CPU13.86/复制0.599ms不混性能验收，profiling-off。两STREAMOFF成功/子回收/network0/Engine在join后销毁/端口释放/内核同，会话全部关闭。规整一次79.59499ms，普通512KiB单位50→66，初始0在Host后已恢复，必要性未证明；代理自主规整权限按最新生效。103身份计划准备未执行；下一分离timing_frames与诊断SDK查询＋异常Host暂存输入取证，新身份Host/三窗后有限诊断，r1不重跑/不放宽索引或速率门禁。ADR_16、FORWARD-TRACE-RESULTS及forward-trace-20261008-r1/next-checkpoint为最新入口；未新长负载/HDMI/长期，旧显示阶段完成记录保留。

<a id="a104"></a>

## A104 · 独立显示子进程可行性完成（2026-10-08）

来源：整理前 AGENTS.md 第104–105行。

- 独立显示子进程可行性完成（2026-10-08）：父3c95eaa7…1f37c05/子de78f7cd…7dbbfda，403包/57来源，子ELF无SDK/VPU且fd仅stdio/socket/自有日志；Engine父主线程保持。Host107/12注册/59600FP32、6912000字节IPC逐位和9拒绝/取消/子退出/回收通过。原三窗重复＋2Hz＋5Hz70前向/1057000FP32全部旧参考、1479编码/849网络/70来源/实际PTS/像素/8232关节通过，正常3子回收、阶段exit0/内核同。5Hz33输入全33消费/显示/编码采用，无覆盖，32次推理显示交叠，实际4.99164849Hz（较4.22311提高18.20%）、画面P95 262.20753ms/父拥有画面264.32126ms，严格≥5Hz未过不舍入判过。inv28 S11_12_329 forward221.6102ms尖峰原因未证，下一有限单钟内部定位及更长有界入口准备，profiling-off/原数学/745/两缓冲/cookie保持。本轮追加授权一次规整实际71.98146ms、普通512KiB单位3→25，无第二次/清缓存/重启/CMA/BOOT变更；最终MemAvailable744640KiB/CmaFree4256KiB/order7+0，非永久可靠性或泄漏证明。四窗核验expected33错误只以新适配器修正至expected4，源码包/数据/阈值不改，无板测重跑。最终认证等待关闭仅只读重连取现场，无模型重跑。结果DISPLAY-PROCESS-RESULTS/NEXT、ADR_15及evidence/display-process-20261008-r1 completion/next-checkpoint为最新入口；测试/SSH/SCP/客户端全结束，无后台，HDMI/长期/严格5Hz/安全连续申请仍待。

<a id="a106"></a>

## A106 · 独立显示子进程验证已批准（2026-10-08）

来源：整理前 AGENTS.md 第106–107行。

- 独立显示子进程验证已批准（2026-10-08）：工作子进程，按最新请求新增SDK无关可执行文件/实际PID与有界Unix域IPC，不替换成普通显示线程。Engine仍父进程主线程；exec在VPU/SDK/线程之前，输入拥有值/输出NV12，结果队列2/IPC信用1/原接收1画面2AU8保持，错误有界回收自身子进程，不自动重开。代理构建、Host/IPC后有限三窗重复→2Hz→5Hz，严格参考/时钟/来源/释放保持。只读确认order7+0后追加明确允许本轮一次规整；该历史批次在Host通过后执行了一次compact_memory写1并保存前后取证，未清缓存/重启或改CMA/BOOT/SDK。ADR_15为本轮决策，实施/结果待更新，旧r2已完成计量状态保留。

<a id="a108"></a>

## A108 · 整机单时钟计量完成（2026-10-08）

来源：整理前 AGENTS.md 第108–109行。

- 整机单时钟计量完成（2026-10-08）：按批准本批1–3完成r2构建/Host107/12注册/59600FP32和2Hz/5Hz实际TCP全链。程序265fd389…d913542，403包/48来源；两阶段62前向/936200FP32逐位旧参考，981编码/591网络/全部62来源/PTS/像素/5516关节通过，exit0/阶段内核同，原模型/SDK/BOOT/帧协议/两缓冲保持，无本批规整或新依赖。2Hz33消费/0覆盖/30计量；5Hz33发送29消费4覆盖，扣3预热26计量，4.22311Hz、画面P95 444.50684ms，整机5Hz未过。主线程串行绘图＋NV12平均44.31442ms是下一最小修正依据，保持Engine主线程，将拥有值显示放独立SDK无关worker的方案仅已准备未实施。RTSP交接P95 852.29247ms不是PC呈现。最终MemAvailable738456KiB/CmaFree5004KiB/order7+为0，仅现场，不证明泄漏；下一首启动条件须单独处理，不自动清缓存/重启/CMA改变。r1构建清单失败及warm占位参考遗漏/本机审查修正保留，不修改当前包或重跑板测。结果SYSTEM-TIMING-RESULTS、NEXT及ADR_14、evidence/system-timing-20261008-r2 completion/next-checkpoint为最新入口；本批测试与SSH/SCP结束，无后台。HDMI/长期/安全连续申请仍未验。

<a id="a110"></a>

## A110 · 整机计量实施已批准（2026-10-08）

来源：整理前 AGENTS.md 第110–111行。

- 整机计量实施已批准（2026-10-08）：已审查PROJECT-STATUS-AND-NEXT-20261008并按规划继续。代理执行本批1–3：独立低日志/单steady_clock计量、2Hz三预热＋30消费回归、通过后有界5Hz负载；传输序号与原样本身份分离，实际消费逐位核对，发送/消费/覆盖/发布/采用/重复分开。保留原诊断、数学/SDK/BOOT/745/缓冲/cookie/网络错误停止；测量结束后有界完整保存。r1清单配置失败保留，r2构建身份已核验，Host与硬件尚未验收。不得自动清缓存/重启或盲改CMA/HDMI；瓶颈实测后另给最小修正。ADR_14及evidence/system-timing-20261008-r2为本轮入口，旧当前完成状态是前一阶段。

<a id="a112"></a>

## A112 · 保存优先及单次规整验证完成（2026-10-08）

来源：整理前 AGENTS.md 第112–113行。

- 保存优先及单次规整验证完成（2026-10-08）：新增保存后比较候选c98b2286…93d66f45，403包/44来源；原CPU/模型/SDK/BOOT/reset(1)/745/VPU2缓冲/cookie保持，Host107/59600/协议/保存契约通过。单次compact_memory写1耗159.69498ms，普通高阶折算512KiB单位5→91；随后两个独立进程三/27窗＋重复32前向、483200FP32逐位旧参考、984编码/864网络/全来源/实际PTS/像素/5502关节通过，exit0/阶段内核同。S12_48_349当前差异0、最高两分差0.04931640625，未复现旧失配或候选颠倒；定点截断原因及query身份不当已证，保存I/O时序影响保留。无第二次规整、清缓存、重启/CMA/BOOT改变；CMA安全申请须匹配驱动分配/DMA/MMU/cache/释放，不用扩大预留或MOVABLE猜改。ADR_13/12/02及Done/进度更新，当前读PRESAVED-RESULTS和evidence/tcp-presaved-20261008-r1 next-checkpoint。全服务/会话关闭，下一独立低日志整机计量准备；未整机5Hz/长期/HDMI/CMA永久可靠性。该批单次规整已记录，不自动复位，旧阻断及失败为历史。

<a id="a114"></a>

## A114 · 本轮保存优先与规整授权（2026-10-08）

来源：整理前 AGENTS.md 第114–115行。

- 本轮保存优先与规整授权（2026-10-08）：门检置于完整实际输出保存之后，再分析候选/数值差异；比较规则、有限性和异常停止保持，截断/候选颠倒仅待证假设。该历史批次通过一次有记录的内存规整推进了有限全链验证。该批执行恢复的历史证据保留，不清缓存、不自动重试、不重启或改CMA/BOOT/SDK/模型。未来安全CMA申请须核验驱动分配接口/地址/MMU/同步与释放路径，当前授权不等于修改驱动或扩大CMA。实测后记录难点、结果和限制。

<a id="a116"></a>

## A116 · guarded与TCP门检进度（2026-10-08）

来源：整理前 AGENTS.md 第116–117行。

- guarded与TCP门检进度（2026-10-08）：新guarded程序f02aceb8…248c6458，403包/36来源，Host107及32全参考前向/977编码/767网络来源/实际PTS/像素通过，实际128KiB TCP缓冲；旧r2保持。TCP程序02697797…6772855，403包/41来源，Host/协议及四实际窗口、496编码/376网络完整通过。启动timeout漏捕与工具延迟保留失败，外部有界等待和PEER_ARMED→实际LIVE_READY→START修正，硬件预算未扩。TCP27第六窗S12_48_349/frame73/invocation5输出失配，前五完整正确，131项/内核同但错误结果未保存，无27门禁。新失败-only捕获d7def2de…34f98a47，403包/44来源，Native/ARM原异常/字节及Host107/59600通过；首次VPU order7/512KiB/0x10dc0失败，85回传、0前向/无Engine创建，CMA130604KiB空闲不证明普通页可用。失败当时高阶均CMA；清理后5个普通order7为另时快照，不自动重跑门禁。未规整/清缓存/重启/CMA/BOOT变化，服务/会话全关闭，按失败策略停止。当前读TCP-INTEGRATION-RESULTS、evidence/tcp-evidence-20261008-r1 next-checkpoint及TCP-RECOVERY-NEXT；恢复首启动条件后新目录三窗→27失败取证，不称原因已查明或开始性能。原授权/数学/SDK/模型/帧协议保持，ADR_11/12及ADR_02已归档，旧检查点为历史。

<a id="a118"></a>

## A118 · 真实在线与模块验证完成（2026-10-08）

来源：整理前 AGENTS.md 第118–119行。

- 真实在线与模块验证完成（2026-10-08）：继续下一门检，新增隔离live目标/FixtureWindow证据/marker/Host适配/编排。程序ec07076fdebf04b17b2fcb90b43679a02ca938ed50fabeddb304ab9ccc253fc1，manifest bdee55fc…44110fb，403包/34来源/15SDK头/189厂商头库；Host107/12注册/59600FP32及AU17拒绝/2000通知通过。三窗＋重复491编码/221网络；协调后27＋重复489编码/429网络；32完整前向483200值逐位旧参考、650网络/395真实结果帧/5530关节与所有32来源及实际PTS/像素正确，Engine主线程持有至workers join后销毁，exit0/内核同/队列及端口释放。首轮27虽然28前向/490编码正确但晚加入ID450仅40帧，不生成网络门禁；外部ready协同程序/包不改，新目录修正，ADR_09。实际库500ms发送补偿/失败未由原r2回调接收，独立guarded模块SO_SNDBUF64KiB读回128KiB＋公共发送错误回调，SDK-free慢peer预期exit1/水位5/无失败后继续NAL，正常30秒223帧全字节/时钟/像素通过；短16秒91帧未满100保留，ADR_10。guarded未入正式r2，不能回填慢客户端保护。输入仅本地固定2Hz，真实TCP前端/整机5Hz/HDMI/30min未验。结果LIVE-RESULTS-20261008.md及evidence/live-20261008-completion completion/next-checkpoint；测试与SSH/SFTP均结束，无后台/自动化。下一新guarded集成身份/Host/真实来源回归→TCP接口→整机门检，既有授权继续，不重问执行方，不自动重试/reset或BOOT/CMA变化；旧r2/r6/SDK/数学/失败保持。

<a id="a122"></a>

## A122 · 全项目归档及AU模块门检（2026-10-08）

来源：整理前 AGENTS.md 第122–123行。

- 全项目归档及AU模块门检（2026-10-08）：先新增ADR_03–08/README和早期难点入口，再执行F0-A3基础门检。新SDK无关AU解析/容量8通道/pipe通知/单线程live555隔离模块，Native与ARM各17拒绝/2000通知通过；189厂商头库保持，程序eafd397c…86619f5，包manifest3f935563…30deb79a，9载荷。r3记录capture493AU→200网络帧为NoInput；新r4-active延后加入108帧覆盖四调用，VCL/实际RTP PTS/10bitID及全部像素逐位旧resident视频，合308解码/34回传；两上下文各一次exit0/dmesg同/端口与source归还，厂商RTCP各两行stderr保留。P帧NAL哈希非唯一，首IDR＋序列＋实际PTS＋解码ID联合定位；本机计数/Python3.8/SDP探测修正历史保留。未新VPU/NPU/HDMI、不是在线实时推理闭环，未整机/长期验收。结果OWNED-AU-RESULTS-20261008.md、r4-active completion/next-checkpoint及ONLINE-INTEGRATION-NEXT当前入口，下一主线程Engine全窗口存活＋实际capture接入与三/27门检，原授权继续，无须重复执行方确认；当前测试/SSH/SFTP均关闭、无后台。原r6/旧RTSP/模型/SDK/BOOT保持。

<a id="a124"></a>

## A124 · VPU启动与有限常驻完成（2026-10-08）

来源：整理前 AGENTS.md 第124–125行。

- VPU启动与有限常驻完成（2026-10-08）：方案并选同进程工作线程。r7仅快照/模块核验，Host107通过但六缓冲capture REQBUFS耗尽普通order7+页，固件512KiB失败；amvx300496e2…074b5直接__alloc_pages_nodemask(0x10dc0)，CMA256MiB@0x30000000保持。隔离r8只请求6→2、实际两端2、映射19.9→6.64MiB，Host107及三次独立启动24前向/30编码均通过，三码流逐位，无规整/重启/BOOT或SDK变化；r8Host300秒95正确例超时保留，新外部420秒完成107，硬件180秒不扩。常驻r5后台Engine首次输出非有限失败，14回调/745/ready/内核正常，停止保留108文件，未27。r6仅Engine所有者回主线程（创建/前向/销毁同owner），编码仍后台，CPU数学/帧协议不改；Host107/32正确前向483200FP32/987编码、实际PTS/28来源和首帧重复通过，5530关节核验，397成功回传；程序f4f15b7ea8806549ad91ca4e3bd69f0fcc5ea580722b18802d5268730efe7060，402包/23来源。容量2 popLatest/coalesced与overwritten独立，固定2Hz两者0。结果VPU-STARTUP-RESULTS/RESIDENT-RESULTS-20261008.md、ADR_02、DIFFICULTIES及resident-r6 completion/next-checkpoint。主线程对照不证明SDK普遍禁止后台线程；三次启动不保证任意碎片。不是常驻daemon部署/在线RTSP/整机5Hz或30min；预览10fps重编码197帧仅审查，真实PTS/原码流保留。下一已批准F0 owned AU/live555门检，不重复旧Host/文件测试，不自动重试；HDMI配套未知不写。原六缓冲、失败、模型/SDK/BOOT保持；测试/会话全关闭，无后台/自动化。

<a id="a128"></a>

## A128 · F0有限接入与启动难点（2026-10-08）

来源：整理前 AGENTS.md 第128–129行。

- F0有限接入与启动难点（2026-10-08）：代理执行获批路线，新增隔离owned NV12/packet与finite同进程Engine→render→VPU。r6程序13693d45f9f124a287f84647fe87b3a8d2bc7d8204a4a08036afd01399f8f086，350包/21来源/15头，Host107/12注册/59600FP32及六拒绝通过；两成功各8全参考前向/10编码（2NoInput），全部NV12及H264逐位一致，主机10ID/112关节通过。成功exit0/stderr空/dmesg同；无规整的新进程重复在Engine前MVX固件order7/512KiB连续页失败，不能记稳定启动。一次显式全局内存规整0.193秒后新目录成功，仅诊断不纳入runner/生产政策，不drop_caches/改持久sysctl/复位或重试。r2 ODR冲突以新助手匿名namespace隔离、r3预算300、r5 producer/codec时钟分开修正，旧源/失败保留；新辅助类型使用内部命名空间避免与冻结源全局模板弱符号冲突。原数学/SDK/BOOT/6缓冲/cookie/reset(1)/745保持。下一PIPELINE-NEXT-20261008.md先只读分配阶段快照与有依据修正，再常驻上下文/有界实时/owned AU；HDMI、在线RTSP、整机长期未过。报告PIPELINE-RESULTS-20261008.md、evidence/pipeline-20261008-r6/completion-review.json与next-checkpoint.json；测试/SSH/SFTP关闭，无后台，按失败策略停止；已批准路线无需重复索要执行方授权。

<a id="a130"></a>

## A130 · 独立RTSP首批完成（2026-10-07）

来源：整理前 AGENTS.md 第130–131行。

- 独立RTSP首批完成（2026-10-07）：已审查动态骨架。厂商live5552024.11.28/配套SSL头库复用，无新安装；程序454d21c24831f88a513747710540294914b6e2d4fddc8ed2993420bc28758fb2，r1缺头路径失败保留。首客户端未保活，10秒回收后88正确帧超时；仅补3秒GET_PARAMETER，新r3两会话各100帧、实际参数集/IDR加入/TEARDOWN/重连/NAL逐位/9000 ticks通过，200解码像素逐位r5。r4 OpenCV/FFmpeg直接RTSP另100帧通过。两60秒上下文exit0/dmesg同/BOOT与SDK保持/source及端口归还；stderr两/一行已证厂商RTCP诊断保持不为空。SPS实际video_signal_type_present_flag=0，显式色彩待处理。当前仅owned预生成码流，未在线VPU/NPU合并、整机/长期或HDMI；源码固定single-slice合同非通用AU。结果RTSP-RESULTS-20261007.md、evidence/rtsp-20261007-r3及r4-player/completion-review.json；新next-checkpoint当前入口，F0-INTEGRATION-PREP给已批准接续门检，不再索要阶段执行授权。原VPU/Engine数学/SDK/BOOT/帧协议保持，先真实三帧＋重复有限合并再网络/实时AU，HDMI配套未明不写。服务/SSH/SFTP关闭，无后台/自动化。

<a id="a132"></a>

## A132 · 视频恢复与V2-A完成（2026-10-07）

来源：整理前 AGENTS.md 第132–133行。

- 视频恢复与V2-A完成（2026-10-07）：阶段恢复后r2保存MMU PC0x1888/FADDR0x20600000及完整cookie/所有权/Host复制证据；r3/r4单CAPTURE色彩拒绝未采用，r3错误接续encode也在REQ/STREAM前停止，历史保留。r5仅保留QUERYBUF opaque cookie用于QBUF，原MPLANE/格式/容量/复制/controls保持。新程序01965fa28f15b94893eebc8a3f540699454ef0623664cb0888b6b7933aef23d3，协商和独立两次各54提交归还/LAST通过，两179648字节H264逐位一致；主机54ID/27来源/756关节可见性通过，exit0/stderr空/dmesg同/BOOT及SDK保持。当前有限文件兼容修正有实测支持，不泛称所有驱动要求或页表内部根因；不是实时/RTSP/5Hz/长期通过。HDMI授权保持但实际时序/scanout/停止映射缺证，未写入1080p60。结果VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md及evidence/video-descriptor-20261007-r5/completion-review.json，新next-checkpoint为当前恢复点，旧暂停/失败保持历史。下一按批准计划审查动态样片、独立RTSP准备，实际NAL/PTS和owned AU；配套资料均在本地，不反复索要未知资料。测试与SSH/SFTP已结束，无后台任务。

<a id="a134"></a>

## A134 · 视频任务已恢复（2026-10-07）

来源：整理前 AGENTS.md 第134–135行。

- 视频任务已恢复（2026-10-07）：继续中断任务，撤销上一条整体暂停。代理先读RESUME-VIDEO/暂停检查点并复核冻结身份，准备最小r2 QUERYBUF/QBUF/DQBUF/映射cookie/offset/所有权/poll取证；保持格式/码率/profile/队列数/复制/输入及旧r1失败，不重跑r1/猜复位或改BOOT。先只读设备状态与未完成download.bit来源核查，再新修订有界取证；异常保存停止。HDMI测试授权保持，配套不明不写寄存器，原推理模型/SDK/帧协议保持；旧暂停按历史理解。

<a id="a136"></a>

## A136 · 视频阶段主动暂停（2026-10-07）

来源：整理前 AGENTS.md 第136–137行。

- 视频阶段主动暂停（2026-10-07）：标记进度并在安全位置中断，等唤醒继续。新SDK无关有限VPU API/54帧候选已构建，27份ARM真实画面与54输入身份核验，协商exit0；真实编码r1提交9/归还3、仅3图像后exit1，内核H264ENC MMU ABORT，部分29879字节与全部失败证据回传，未动态/RTSP验收。失败后BOOT/SDK/三库与FPGAoperating保持，无重试/复位/换BOOT。HDMI只读DT/clock/fbdev/DRM/udma及发布包身份核对、离线1080p色条完成，时序/scanout/安全停止仍缺证，未HDMI写入/实屏。原SSH/SFTP已关闭，补查download.bit连接在认证前取消、该查询未执行。当前整体暂停，停止编译/连接/编码/HDMI/后台/自动唤醒，原HDMI授权保留但不在暂停期间执行。恢复先读VIDEO-SEQUENCE-RESULTS-20261007.md、evidence/video-sequence-20261007-r1/next-checkpoint.json与RESUME-VIDEO-20261007.md；先本机身份与失败复核、最小IOCTL/映射/所有权取证设计，再新修订有界验证，不重跑r1、猜profile/cache/延时/复位或把部分视频计通过。无新目标/自动化；等待独立执行许可。

<a id="a138"></a>

## A138 · 审查视频并恢复HDMI授权（2026-10-07）

来源：整理前 AGENTS.md 第138–139行。

- 审查视频并恢复HDMI授权（2026-10-07）：已完成独立H264视频审查，要求下一步计划并明确允许HDMI测试，解除此前HDMI暂停。代理准备NEXT-VIDEO-PLAN-20261007.md：先真实27预生成骨架54帧文件与HDMI配套核查，再有依据的1080p60独立色条/换帧、capturePTS/NAL/色彩信号及独立RTSP，最后真实推理接入/双路。构建/传输/审计由代理，实屏OSD与画面需现场核对。HDMI参考宽高只分配udma/cache和写参考地址，不配置clock/timing，不据此猜写；BOOT/SDK/模型/RAW及帧协议保持，启动组件更换另给具体方案，独立阶段串行/有界/失败保留停止。本轮仅本机资料和计划，未新板测/时序切换；旧暂停按历史理解，新检查点video-next-plan-20261007.json。

<a id="a140"></a>

## A140 · 独立VPU文件编码与主机审查完成（2026-10-07）

来源：整理前 AGENTS.md 第140–141行。

- 独立VPU文件编码与主机审查完成（2026-10-07）：暂停HDMI并独立H264，代理实测r4 MVX720p NV12两planes/stride1280、H264一plane、两端601有限、10fps/2Mbps/Baseline读回；30帧MMAP输入正常STOP→LAST/归还，36717字节Annex-B/37649字节MP4回传哈希一致，主机OpenCV30ID/移动条/唯一图正确，两种文件解码逐位相同，exit0/stderr空/dmesg同/BOOT及SDK保持。程序8f713fc8d6c76a03053544634591448f1068ef0a392261023bf73d5b1538e8ce。保留清单CRLF、coded2x2顺序、默认coded色彩与裸流rate断言历史；未放宽720规格。编码独立预生成合成图不是新推理/RTSP/5Hz/长期。裸流PTS/ffprobe色彩未知，MP4 nominal10fps离线重建，后续RTSP需capturePTS/NAL边界和色彩依据。无新安装/HDMI或NPU初始化/寄存器/BOOT变化，显示目标1080p60仅目标并继续暂停。结果VPU-RESULTS-20261007.md及evidence/vpu-20261007-r1/completion-review.json；会话结束、新next-checkpoint恢复，旧“未编码/未接屏”按历史理解。

<a id="a142"></a>

## A142 · HDMI新目标与独立编码授权（2026-10-07）

来源：整理前 AGENTS.md 第142–143行。

- HDMI新目标与独立编码授权（2026-10-07）：连接DELL E2421HN后报告不支持当前时序，明确HDMI目标改为1920×1080@60Hz并先暂停HDMI测试。代理可准备、执行有限独立H.264编码及上传主机审查；沿用已验证720p10fps CPU输入、实际V4L2协商/MMAP、完整身份与异常停止，勿初始化NPU/HDMI、写寄存器或修改BOOT/模型/SDK。PC截图不作板端时序证明；未接屏文字为历史，实际时序更改在暂停期间不执行。

<a id="a144"></a>

## A144 · E1-C渲染与V0部分配套完成（2026-10-07）

来源：整理前 AGENTS.md 第144–145行。

- E1-C渲染与V0部分配套完成（2026-10-07）：核对进度后要求继续，并确认HDMI显示器未连接。代理完成1280×720固定视角/源BONES14条/显示层C2翻转，原坐标/数学/引擎/复制/模型/RAW/SDK/BOOT/帧协议保持，不导入GT、阈值、匹配/滤波或物理单位/解剖标签。Native/ARM四状态与8拒绝、真实27画面及RGB565LE/NV12/NV21逐位Native/NumPy通过；新467包/23来源构建、Host107/59600值、三帧2Hz网络真实推理＋本帧绘图通过，179/52/70完整回传，exit0/stderr空/dmesg保持。程序0fc63b8f64a78884538ab8c4cb4701ad5fc6046e11e44ad62f960cf5b8dd9533。绘图约11.94ms、三种诊断转换约88.85ms不作5Hz/长期。只读V4L2/query/sysfs显示MVX两端MPLANE，720p NV12/NV21/H264枚举存在；未S_FMT/REQBUFS/STREAMON、编码/RTSP/HDMI或写寄存器，HDMIclock/scanout配套仍未知。结果RENDER-RESULTS-20261007.md、V0-VIDEO-PAIRING-20261007.md及evidence/render-20261007-r1/completion-review.json；会话全部结束，恢复读新next-checkpoint，下一独立VPU按返回planes/stride/colorimetry门检，HDMI需匹配BOOT时序及接屏，不套参考单平面CAPTURE/固定SPSPPS或相机MMU修改。深度异构优化后置，旧待渲染文字为历史。

<a id="a146"></a>

## A146 · E1-A/B首批完成（2026-10-07）

来源：整理前 AGENTS.md 第146–147行。

- E1-A/B首批完成（2026-10-07）：代理按批准路线完成隔离生产接口（无固定Tokens依赖、验证包装器保留）、TCP完整记录/单待处理槽位/单Engine及有界诊断。Native/ARM协议自检、411包/19来源构建身份、BOOT9/SDK一致；Host107/59600值、交替两入口8前向、3/27网络30前向共38成功全输出逐位此前板端，四阶段exit0/stderr空/dmesg保持。2Hz发送下无丢弃/拒绝，27帧到达至结果191.95180ms/P95 193.76084ms不作整机5Hz。程序402cac43ca9de6bccb3ddf41ea7069d351f6d2e8e4500f33c41940d0869cc50c，冻结旧源/模型/RAW/SDK/BOOT/数学/复制/帧协议保持；最小日志采样4帧/8192计时条目、有限CLI最多1000帧不是长期服务。r1编译函数名错误新r2修正；27首次就绪检查20秒/总120秒因控制延误超时124，七输出逐位一致。保留失败，仅外部新控制脚本与新目录300秒/90秒READY后一次修正通过，同包/程序/门禁未伪改。结果APPLICATION-RESULTS-20261007.md及evidence/application-20261007-r2/completion-review.json；会话/后台测试全部结束。下一恢复读新next-checkpoint，E1-C渲染/V0视频配套接续既有已批准路线；未经配套确认不猜寄存器/换BOOT，新依赖另定，深度性能优化后置。旧首批未运行文字为历史。
