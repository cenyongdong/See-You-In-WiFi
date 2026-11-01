# 整理前历史文档快照

2026-10-13迁存。以下所有“当前”“待执行”均是原阶段描述，请勿用于判定今日状态；相对文档链接已按新位置调整。最新入口为根目录PROJECT-PROGRESS.md或DIFFICULTIES.md。

# 项目进度总览（2026-10-11）

## 当前：首版有界端到端演示已验证，原坏读定位暂停

software/demo完成预采CSI回放→Lite PS/NPU→骨架渲染/VPU H264→RTSP/TCP→主机GUI。默认60个2Hz窗口全部消费/不同姿态/全来源显示，637编码和577主机解码；短阶段另3输入/352编码/292解码，两阶段正常drain/释放和最终身份通过。前三样本有完整逐位参考，其余57仅结构/有限性/选择/映射。一次获准重启已用，成功两阶段规整0，全部进程和连接结束。

项目已处于可展示首版全链集成、可靠性与性能优化待收敛阶段。管理83/100保持，仅计划估算，非性能/精度通过率；永久首启动、原高负载坏读、严格5Hz、30分钟、HDMI/真实采集仍待。旧DATA排查暂停，本批不推进其下一方案。[结果](../../../tools/pose-v1/DEMO-RESULTS-20261011.md)／[技术汇报](../../../ADR/TechDetails.md)／[恢复入口](../../../tools/pose-v1/evidence/demo-20261011-r4/next-checkpoint.json)。以下当前为历史。

## 当前：目录预建过，首次DATA96与正确晚源读已取证，根因未修

four4/off100/on前94共198完整正确2328480FP32；第199实际前向inv94/A首DATA96全同上一B，INDEX正确，四物理晚源读全正确。首次拥有指纹匹配错误文件（保存后记录），目录热领取无FS/本批不超槽，但输入写盘最大166.999ms。307 NoInput前缀/abort清理与身份过，服务连接全关闭，规整0。当前仍首版闭环后的并发可靠性定位，管理83/100（非通过率或工期）保持；on100/完整103/严格整机5Hz/30min/HDMI未过。下一首次Host目的租约/失败CPTR对照仅方案准备，不重跑旧Session。[结果](../../../tools/pose-v1/PRODUCER-PREPARED-RESULTS-20261011.md)／[ADR_44](../../../ADR/ADR_44.md)／[下一](../../../tools/pose-v1/PRODUCER-PREPARED-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-prepared-20261011-r1/next-checkpoint.json)。以下当前为历史。

## 当前：源租约和Host read过，目录等待在前向前被截止门检拦截

四调用/off100/on前49共153前向1799280 FP32逐位，正常租约关闭／零源读；有VPUinv49目录创建915.86ms阻塞，绝对时隙在reset前拒绝，不产生错误输出、物理晚源read尚未触发。目录内部等待责任及原DATA800根因仍待。221 NoInput视频前缀和abort清理过，原152软件／模型SDKBOOT及异常读取保持。全部程序连接关闭，规整0；下一放行前空目录与有界领取令牌仅准备，数据仍原位保存。当前仍处首版闭环后并发可靠性定位，管理83/100保持（非通过率／工期），完整103／严格整机5Hz／长期／HDMI待。

[结果](../../../tools/pose-v1/PRODUCER-SOURCE-READ-RESULTS-20261011.md)／[ADR_43](../../../ADR/ADR_43.md)／[下一](../../../tools/pose-v1/PRODUCER-SOURCE-READ-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-source-read-20261011-r2/next-checkpoint.json)。以下当前为历史。

## 当前：高地址独立组＋VPU发生前帧数据复用，已获得更小失配场景

高地址四调用／off100／on前49共153完整1799280FP32正确，第50次DATA800有限值逐位同前帧A，INDEX正确、首次拥有输出已错、输入／计数／身份正常；尚无晚源证据，SDK/NPU/DMA/cache责任未证。不能以此称复现了原192索引错完全相同机制。214 NoInput视频前缀／异常清理过，正常drain-LAST未过；原152软件、模型SDKBOOT和异常读取保持，资源只读／规整0，程序连接全结束。下一单调用源租约及失败两轮只读证据仅准备。当前仍是首版闭环后的并发可靠性定位，管理83/100不变（非通过率／工期），完整103／严格5Hz／长期／HDMI待。

[结果](../../../tools/pose-v1/PRODUCER-ADDRESS-RESULTS-20261011.md)／[ADR_42](../../../ADR/ADR_42.md)／[下一](../../../tools/pose-v1/PRODUCER-ADDRESS-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-address-20261011-r2/next-checkpoint.json)。以下当前为历史。

## 当前：reset前已分段，无／有VPU各100过，正式高地址坏读仍待定位

200独立19成员调用／2352000 FP32及输入全逐位、0→11／绝对时隙过；307 NoInput图像与正常drain-LAST、资源释放过。旧1.764秒尖峰未复现，输入保存区间46／42ms等待有观测但底层责任未证；正式坏索引未修。原152软件及模型SDKBOOT保持，原异常读取保留。下一公开SDK高地址布局可行性仅准备，不猜映射或同时改保存策略。仍处首版闭环后的并发可靠性定位，管理83/100不变（非通过率／工期），完整103／严格整机5Hz／长期／HDMI待；一次有记录规整，所有本批程序／连接结束。

[结果](../../../tools/pose-v1/PRODUCER-PHASE-RESULTS-20261011.md)／[ADR_41](../../../ADR/ADR_41.md)／[下一](../../../tools/pose-v1/PRODUCER-PHASE-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-phase-20261011-r2/next-checkpoint.json)。以下当前为历史。

## 当前：无视频100通过，有视频82次数据正确但时隙失败

同身份独立19成员off100／on82共2140320 FP32逐位参考、0→11正确，on inv81 reset前1763.68731ms空档导致时隙退出1，不能认定文件I/O或NPU根因。实际并发覆盖162/164复制跨度，270 NoInput图像解码正确；正常drain-LAST未验。原正式192坏值未复现未修、异常读取保持，当前仍处首版闭环后的并发可靠性定位，主观管理83/100不变（非通过率或工期），完整103／严格整机5Hz／长期／HDMI待。一次有记录规整，原模型SDKBOOT/CMA和152软件保持，程序／连接全结束。下一分段观察及准备后绝对截止检查仅准备。

[结果](../../../tools/pose-v1/PRODUCER-VPU-RESULTS-20261011.md)／[ADR_40](../../../ADR/ADR_40.md)／[下一](../../../tools/pose-v1/PRODUCER-VPU-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-vpu-20261011-r2/next-checkpoint.json)。以下当前为历史。

## 当前：独立真实19成员四调用过，正式高并发首次读根因未修

真实部署、独立临时PLDDR往返及同Session固定A/B/A/B通过，47040 FP32逐位参考、0→11与释放正确。mock不支持搬运的r1失败已查明，r2使用Host CPTR／真实内存前置门检，不把mock当物理证据。原152冻结软件、模型、SDK与BOOT不变，未新完整模型／VPU／Host107或长期门检。下一有／无VPU各固定100调用方案仅准备，原异常读取保持。仍处首版闭环后的高并发可靠性定位，主观管理估计83/100不变，不是通过率／工期；103／严格5Hz／长期／HDMI待验。本批代理程序／管理器／连接结束，规整0，内核同。

[结果](../../../tools/pose-v1/PRODUCER-GROUP-RESULTS-20261011.md)／[ADR_39](../../../ADR/ADR_39.md)／[下一](../../../tools/pose-v1/PRODUCER-GROUP-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-group-20261011-r2/next-checkpoint.json)。以下当前为历史。

## 当前：真实19成员参考与mock范围已闭合，首次物理读取根因仍待

本轮完成原RAW公开仅读、实际权重／指令身份、adapted 19来源映射、两图案23520 FP32独立参考及重放；mock独立部署sync0→11过。无物理NPU forward／新视频／Host107或并发门检。下一先独立物理apply核对真实段，再固定四调用，保留原异常读取。项目仍处首版闭环后的高并发可靠性定位，管理83/100不变（主观工作包估计，非通过率／工期），103／严格5Hz／长期／HDMI待。规整0、内核同、程序和连接关闭。

[结果](../../../tools/pose-v1/PRODUCER-REFERENCE-RESULTS-20261011.md)／[ADR_38](../../../ADR/ADR_38.md)／[下一](../../../tools/pose-v1/PRODUCER-REFERENCE-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-reference-20261011-r2/next-checkpoint.json)。以下当前为历史。

## 当前：SDK检查与部署映射更明确，真实生产者参考／硬件完成契约待闭合

本轮完成六匹配头与后端检查路径审查、ARM XIR-only三视图和官方apply/log映射；没有NPU前向／视频或新增数值验收。8629／8631为零指令Cast，原组19成员11层，检查器有计数达标后条件copy；实际触发／DDR保证未证。官方数据与索引地址同旧失败，均非OCM。

r2 apply/log exit0；r3误预期一日志而实际两份导致门禁exit1，数据完整、原错保留。误判日志缺失源于Git过滤，目录故障推断撤回。纠正r4仅编译；无硬件重跑。当前仍处于首版全链后的并发数据可靠性定位，管理83/100不变（非通过率／工期），103／严格5Hz／长期／HDMI待；全部连接与程序结束、规整0、内核同。

[结果](../../../tools/pose-v1/PRODUCER-CONTRACT-RESULTS-20261011.md)／[ADR_37](../../../ADR/ADR_37.md)／[下一](../../../tools/pose-v1/PRODUCER-CONTRACT-NEXT-20261011.md)／[当前恢复点](../../../tools/pose-v1/evidence/producer-contract-20261011-r2/next-checkpoint.json)。以下当前为历史。

## 当前：双模式内存读取通过，剩余生产者／DMA完成责任待证

匹配AXI/XRT与板端UDMA模块审查确认锁、轮询和缓存同步路径。独立两应用方法在无VPU／合成VPU下共400动态对4704000 FP32正确，两VPU共455图像／实际PTS／解码正确，无NPU／完整模型。当前未复现原192坏片段；不能把内存对照通过称为模型并发修复。

项目仍处于首版全链之后的并发数据可靠性定位阶段，管理估算83/100保持（非通过率／工期）。完整103／严格5Hz／长期／HDMI待。本批批准范围结束，程序／连接全关闭，规整0／内核同／原模型SDKBOOT保持；下一匹配生产完成契约及最小真实NPU对照仅准备。

[结果](../../../tools/pose-v1/AXI-READ-RESULTS-20261011.md)／[ADR_36](../../../ADR/ADR_36.md)／[下一](../../../tools/pose-v1/AXI-READ-NEXT-20261011.md)／[当前恢复](../../../tools/pose-v1/evidence/axi-pair-20261011-r4/next-checkpoint.json)。以下当前为历史。

## 当前：首次复制返回已出现旧输入片段，优先定位共享读取暂存与完成机制

ReadPhase隔离模块及正确链接r3已通过Native／ARM／Host107和四窗口60400FP32、492编码462网络全内容。唯一固定QPC5.05诊断48正确返回后192失败：立即快照592变化589非整数，CPU前字节不变，592变化全部等于紧前输入同偏移值，两晚源正确。观察边界已缩小，底层SDK／DMA／cache或源时序责任尚未证明，原数学／模型／SDK／BOOT保持。

项目处于首版全链之后的并发数据可靠性和读事务完成责任定位阶段。不是候选数值容限验收或已完成性能优化；完整103／严格5Hz／长期／HDMI继续待。本批已结束，十保存任务及资源回收通过，所有测试／连接关闭；r2集成错误与修正保留，一次规整143.23443ms，r3无规整。下一AXI／UDMA实现审计方案仅准备未执行，管理工程估算83/100保持。

[结果](../../../tools/pose-v1/READ-PHASE-RESULTS-20261011.md)／[ADR_35](../../../ADR/ADR_35.md)／[下一](../../../tools/pose-v1/READ-PHASE-NEXT-20261011.md)／[恢复点](../../../tools/pose-v1/evidence/read-phase-20261011-r3/next-checkpoint.json)。以下当前为历史。

## 当前：公开上游边界模块通过，首次read／Host暂存瞬态责任待定位

原Gather／ZG八点观察已完成Native、ARM、Host107和四窗口全链回归，4返回60400FP32及495编码465网络全内容正确。唯一QPC5.05诊断55返回830500FP32正确后，第56次调用192首次Host索引1584变化／1582非整数，随后两轮晚设备read全部逐位旧参考；异常完整保存并停止。当前失败尚未到Gather442，不能认定原Gather或某个DMA／cache环节责任。

首版工程已贯通，目前处于并发数据可靠性与读取完成契约定位阶段。八点公开保留生产者句柄并非Session私有输入映射证明；55边界分组仅首四帧有完整字节数学验收，诊断不作性能验收。r3保存预算失败在r4以原8＋独立1账本修正，旧构建／数据／失败保留。下一首次read和CPU使用前Host字节边界方案已准备，尚未执行。所有测试／连接关闭；本批准范围两次有记录规整，高负载无规整，未清缓存／重启／改CMA／BOOT。管理估算83/100保持，不是通过率；103高负载、严格5Hz、长期和HDMI待。

[结果](../../../tools/pose-v1/UPSTREAM-BOUNDARY-RESULTS-20261011.md)／[ADR_34](../../../ADR/ADR_34.md)／[下一](../../../tools/pose-v1/UPSTREAM-BOUNDARY-NEXT-20261011.md)／[恢复点](../../../tools/pose-v1/evidence/upstream-boundary-20261011-r4/next-checkpoint.json)。以下当前为历史。

## 当前：完整异常保存完成，582上游边界责任待定位

final_evidence Native/ARM/Host107及原三窗全链通过。固定QPC5.05一次诊断第25返回出现128有限姿态失配；完整25返回及八保存任务、CPU写回前值和两轮晚源均成功保留。582/649更新源晚读仍与bad Host相同；437正确，真实RAW＋实际输入的独立NumPy重建与582 CPU及最终姿态各4200值逐位一致，异常早于582内核。

项目仍处于首版工程贯通后的并发数据可靠性、异常责任定位及吞吐验收阶段。保存缺口已解决、数据根因未解决；下一原Gather442与ZG9189/Hard8131边界取证准备，未实施新观察或进一步板测。本轮规整0、所有测试/连接结束，管理83/100保持；不将诊断进展计为高负载稳定或长期/HDMI通过。

[结果](../../../tools/pose-v1/FINAL-EVIDENCE-RESULTS-20261010.md)／[ADR_33](../../../ADR/ADR_33.md)／[下一](../../../tools/pose-v1/FINAL-EVIDENCE-NEXT-20261010.md)／[恢复点](../../../tools/pose-v1/evidence/final-evidence-20261010-r2/next-checkpoint.json)。

以下“当前”与实施中条目为历史。

## 当前：首版全链有限回归通过，较高负载有限数据可靠性待定位

公开read＋显示子进程／真实TCP／RTSP的三窗、2Hz103与名义5Hz103全数值/来源/内容通过，合210前向；严格≥5实测4.998467未过。新增本机QPC发送器的一次明确5.05Hz能力批次第34返回出现582更新输入与姿态128有限值失配，原bad Host与全部返回数据保留、root未证，测试／会话已全部结束，暂停已撤销。

项目处于首版工程贯通后的并发数据正确性、完整异常取证和吞吐验收阶段；可用有限展示基线已有，不能宣称高负载永久稳定或长期/HDMI通过。下一先补最终输出门检晚源和CPU写回前拥有值、save-only序列化，再新身份Host/三窗及一次诊断；旧失败不重跑、不调频率继续凑阈值。管理83/100保持，仅工程估算。

[结果](../../../tools/pose-v1/COMBINED-READ-RESULTS-20261010.md)／[ADR_33](../../../ADR/ADR_33.md)／[下一](../../../tools/pose-v1/COMBINED-READ-NEXT-20261010.md)／[当前检查点](../../../tools/pose-v1/evidence/combined-read-20261010-r1/next-checkpoint.json)。以下当前为历史。

## 当前：真实拥有画面107有限门检通过，准备组合回归

阶段恢复后并撤销整体暂停。公开read隔离候选新Host107及107真实前向1615700FP32逐位参考通过，108NV12逐字节Native一致，824图像解码覆盖107来源／实际PTS／7364关节通过；正常资源释放、规整0、原内核同，全部程序／连接结束。重复画面不计新姿态吞吐，原坏块、失败及暂停证据保留。

项目处于首版全流程贯通后的并发可靠性验证与组合回归阶段。设备输入read直写自有Host CPTR是一条有限验证通过的候选处理路径，底层瞬时复制责任尚未证明；下一新身份接入显示子进程／TCP／owned AU，再整机有界5Hz。长期／HDMI／采集终版／安全连续申请／零拷贝待，管理估算83/100保持，不是通过率。

[结果](../../../tools/pose-v1/INPUT-READ-RESULTS-20261010.md)／[ADR_30](../../../ADR/ADR_30.md)／[下一方案](../../../tools/pose-v1/INPUT-READ-NEXT-20261010.md)／[当前检查点](../../../tools/pose-v1/evidence/input-read-20261010-r1/next-checkpoint.json)。以下“当前”及暂停条目均为历史。


- 真实画面故障任务恢复（2026-10-10）：阶段恢复后，撤销整体暂停。旧picture-r1失败及暂停证据保留，不重跑。已核验公开Tensor::read签名和Host起点/容量契约，新增隔离input-read-r1候选，仅设备输入read直写自有Host CPTR；Host输入、输出写回、数学、模型、SDK、BOOT及异常快照保持。ADR_30记录决策；目前126来源/403载荷已冻结，尚未编译或板测，不认定已修复。

## 历史：暂停，真实画面20正确后192坏值复现

真实拥有画面picture-r1已实现、构建及Native／ARM五组契约通过；一次硬件首次VPU启动成功，单上下文三窗4＋长阶段16共20前向302000FP32正确，第21次inv20／S23_30_330／192索引144有限非整数／8坏段失败，完整103未过。坏段同次前一slot0复制同偏移，两轮PL DDR源94080字节正确，对象稳定／168计数234；具体瞬时复制责任未证。20画面采用、21NV12逐位Native、392解码前缀／20来源／实际PTS／1330关节过，3采样未捕获，不记正常drain／LAST。异常原文及3输入47760／两晚源保留；两abort STREAMOFF／join／七项保存／原内核同，全部程序／连接结束。一规整66.20272ms普通9→16，最终745428KiB／CmaFree1604／普通10仅现场，无清缓存／重启／CMA／BOOT变化。根因未修，83/100保持。

首版全流程已贯通，当前仍在并发数值可靠性定位；真实画面103、长期／5Hz与视频终版未验收。管理粗估83/100是工程估算，不是通过率。[恢复入口](../../../tools/pose-v1/RESUME-PICTURE-20261010.md)／[ADR_29](../../../ADR/ADR_29.md)／[暂停点](../../../tools/pose-v1/evidence/picture-20261010-r1/pause-checkpoint.json)。暂停期间不连接或新测试。以下当前为历史。

## 当前：单次常驻合成VPU＋真实模型107通过

单次常驻r1 c4c5caaf…c601822／manifest45dfbd83…1f0fc8a，403包108来源；Native／ARM阶段13、107计数16、原生命周期6／Run9拒绝过，原Host107／12注册59600身份复用。实际单VPU／单主线程Engine连续三窗4＋103合107前向1615700FP32逐位旧参考、518合成图像／实际PTS／像素通过，520packet／93978字节／正常drain-LAST／两STREAMOFF／join后Engine销毁。192源109232128／109285376保持，1712对象／856shadow、856查询234、963元数据稳定；原模型／SDK／BOOT／数学／ready/reset(1)／745和异常两晚源保持。一次规整144.80296ms／普通9→28，编码进入31→29→21／首次20；不是永久首启动修复或已证阈值。exit0／stderr空／原内核同／七项保存成功，所有项目程序／端口／代理连接结束，最终745488KiB／CmaFree28892／普通30仅现场。旧坏块未复现／根因未修，未显示／网络／HDMI／持续5Hz／长期／零拷贝；83/100保持。

首版全流程已贯通，当前在并发数值可靠性与首次启动资源治理阶段；本次有限通过不增加管理粗估，也不代表整机／长期验收。[结果](../../../tools/pose-v1/RESIDENT-SEQUENCE-RESULTS-20261010.md)／[ADR_28](../../../ADR/ADR_28.md)／[下一](../../../tools/pose-v1/RESIDENT-SEQUENCE-NEXT-20261010.md)／[恢复点](../../../tools/pose-v1/evidence/resident-sequence-20261010-r1/next-checkpoint.json)。以下当前为历史。

## 当前：同身份对照前三阶段通过，VPU首次启动仍阻断

同ELF模型／合成VPU对照r2已结束：Native／ARM6生命周期及9运行拒绝过，原Host107／12注册59600身份复用；model-three4、vpu-three4及model-103共111前向1676100FP32逐位旧参考，310合成图像／实际PTS过。最后vpu-103在首次capture前DQBUF EIO，内核MVX固件order7／512KiB普通页失败；Engine未创建、前向0，无模型坏块复现。规整3次有记录但仍失败，不是首启动可靠性修复；两abort STREAMOFF／join／七项保存过，成功内核同而最后新增错误完整保留。原数学／模型／SDK／BOOT与异常两晚源保持，全程序／端口／代理连接结束。根因未修、并发103／长期／5Hz／HDMI未过，83/100保持。

[结果](../../../tools/pose-v1/MODEL-VPU-RESULTS-20261010.md)／[下一方案](../../../tools/pose-v1/MODEL-VPU-NEXT-20261010.md)／[恢复点](../../../tools/pose-v1/evidence/model-vpu-20261010-r2/next-checkpoint.json)。首版全流程已贯通，目前处于并发数值可靠性与编码启动资源治理阶段；管理粗估83/100不变，不是功能通过率。以下当前为历史。

## 当前：真实混合模型无视频三窗／103诊断完成

107实际前向1615700 FP32逐位旧参考，真实192源与旧失败相同、1712对象／856计数合法，数据保存完整；Native／ARM契约与原Host身份通过。无视频／显示／网络，规整0、内核同、程序及代理连接结束。旧坏块未复现，根因仍未解决，不能以无视频通过认定VPU有责。[结果](../../../tools/pose-v1/MODEL-ONLY-RESULTS-20261010.md)／[ADR_26](../../../ADR/ADR_26.md)／[恢复点](../../../tools/pose-v1/evidence/model-only-20261010-r1/next-checkpoint.json)。

项目仍处首版全流程贯通后的并发数值可靠性定位，管理粗估83/100不变。下一[同身份模型／合成VPU对照](../../../tools/pose-v1/MODEL-ONLY-NEXT-20261010.md)仅准备，稳定并发103／长期5Hz／HDMI／采集终版／零拷贝仍待。以下当前为历史。

## 当前检查点：公开管理器与较高来源位置对照完成

本轮批准范围已完成：合法SDK占位使源实际位于100667392／100697664，动态100对＋VPU100对2388000 FP32逐位正确，227合成编码ID／实际PTS过，公共自有块全部归还。Native／ARM位置12＋字节8拒绝；原主／Host107身份保持。本批规整0，无模型Session／NPU前向，旧坏块未复现、根因仍待。全测试／代理会话结束。[结果](../../../tools/pose-v1/PLDDR-POSITION-RESULTS-20261010.md)／[ADR_25](../../../ADR/ADR_25.md)／[恢复点](../../../tools/pose-v1/evidence/plddr-position-20261010-r1/next-checkpoint.json)。

首版全流程已贯通，当前处于并发数值可靠性定位，管理粗估83/100不变，不是测试通过率。下一[真实混合Engine无视频有限对照](../../../tools/pose-v1/PLDDR-POSITION-NEXT-20261010.md)仅准备，未新模型门检。稳定103、持续5Hz／长期、HDMI／采集终版／零拷贝仍待。以下“当前”检查点均为历史。

## 当前检查点：2026-10-10 真实类型／动态写入独立对照通过，模型故障未复现

获批真实类型静态→动态→动态＋VPU各100对合3582000 FP32正确，Native／ARM模式契约与226合成编码图像／实际PTS核验过。原主ELF相同、Host107身份复用；无模型Session／NPU前向，根因未修。一次资源规整14→143单位／217.37457ms，内核事件同／退出与连接关闭。下一公开SDK管理器与合法自有较高来源位置对照仅准备；仍处首版贯通后的并发数值可靠性定位，管理粗估83/100保持，稳定103／持续5Hz／长期／HDMI／采集终版／零拷贝待。[结果](../../../tools/pose-v1/TYPED-SCRATCH-RESULTS-20261010.md)／[ADR_24](../../../ADR/ADR_24.md)／[下一方案](../../../tools/pose-v1/TYPED-SCRATCH-NEXT-20261010.md)／[检查点](../../../tools/pose-v1/evidence/typed-scratch-20261010-r1/next-checkpoint.json)。

## 历史检查点：2026-10-10 真实对象稳定，模型192残留复发

获批对象／dtype／范围观察已接入，实际新Host107与三窗全内容通过；唯一103在第73次192拒绝128有限非整数，7坏段同前次复制同偏移、两晚源正确。新对象1222行与原shadow对齐、同copy前后身份稳定，source和Host范围各不重叠，616计数全234；根因未修。合76正确1147600 FP32，失败媒体只前缀，未完整103或性能验收。规整0、内核同、全会话资源关闭；下一真实类型常量／动态SDK scratch候选仅准备。仍处全流程首版后的数值并发可靠性定位，管理粗估83/100保持，稳定103／持续5Hz／长期／HDMI／采集终版／零拷贝待。[结果](../../../tools/pose-v1/TENSOR-IDENTITY-RESULTS-20261010.md)／[ADR_23](../../../ADR/ADR_23.md)／[下一方案](../../../tools/pose-v1/TENSOR-IDENTITY-NEXT-20261010.md)／[检查点](../../../tools/pose-v1/evidence/tensor-identity-20261010-r3/next-checkpoint.json)。

## 历史检查点：2026-10-10 独立搬运与编码并发通过，模型坏块未复现

批准的SDK-owned30240／16800、64对齐隔离已完成：Native／ARM各10拒绝，原Host107身份复用；无VPU100对＋VPU并发100对合2388000 FP32正确，200合成图像／实际PTS／解码序号通过。无模型Session／NPU forward，不记模型修复或真实推理视频验收；下一真实源／区域／chunk／dtype和目标对象身份观察仅准备。规整0、内核同、资源及代理会话关闭。管理粗估83/100保持，当前是全流程首版已贯通后的并发数值可靠性定位；稳定103／持续5Hz／长期／HDMI／采集终版／零拷贝仍待。[结果](../../../tools/pose-v1/SCRATCH-COPY-RESULTS-20261010.md)／[ADR_22](../../../ADR/ADR_22.md)／[下一方案](../../../tools/pose-v1/SCRATCH-COPY-NEXT-20261010.md)／[检查点](../../../tools/pose-v1/evidence/scratch-copy-20261010-r3/next-checkpoint.json)。

## 历史检查点：2026-10-09 192故障时已234，受控搬运一致性设计

公开192四点观察实现，Host／新三窗全内容通过；103第4调用192失败，合7正确105700值。失败两输入8计数均234，1728坏索引55段同前次复制同偏移，晚源正确；等待到234不会在该点产生等待，根因未解。七项保存及原异常保留，全部代理会话已关闭、规整0。下一无NPU的SDK-owned30240/16800双源连续搬运和有限VPU并发设计，仅方案未执行；不猜cache、寄存器、SDK或BOOT修正。管理粗估83/100保持，不增加为103／5Hz／长期／HDMI／零拷贝通过。[结果](../../../tools/pose-v1/PRODUCER-COUNT-RESULTS-20261009.md)／[ADR_21](../../../ADR/ADR_21.md)／[下一方案](../../../tools/pose-v1/PRODUCER-COUNT-NEXT-20261009.md)／[检查点](../../../tools/pose-v1/evidence/producer-count-20261009-r2/next-checkpoint.json)。

## 历史检查点：2026-10-09 保存接入完成，192连续搬运残留待定位

单帧拥有字节与独立落盘已实现，Host107／真实Host最终拒绝及新三窗全内容通过；本批103第12次192索引拒绝，合15正确前向226500FP32。3输入47760字节和102元数据完整，496个坏索引18段同紧邻前次复制的同偏移，两晚源均正确；数值根因未证。测试／连接全结束，规整0。下一独立192 producer234公开计数观察与匹配SDK中转同步审计已规划，尚未执行。管理粗估83/100保持，不以取证完善增加为103／5Hz／长期／HDMI／零拷贝验收。[结果](../../../tools/pose-v1/INVOCATION-GUARD-RESULTS-20261009.md)／[下一方案](../../../tools/pose-v1/INVOCATION-GUARD-NEXT-20261009.md)／[检查点](../../../tools/pose-v1/evidence/invocation-guard-20261009-r1/next-checkpoint.json)。

## 历史检查点：2026-10-09 独立回归有限输出异常，先补齐取证

预定三轮：第一轮103全内容通过、严格速率4.999251559Hz未过；第二轮第38次姿态652值失配，最佳骨架没变仍停止，第三轮未执行。合140正确完整前向2114000FP32，完整异常保留；元数据/ARM参考被重复保存门检跳过。新SDK-free单帧拥有值/独立flush已Native/ARM验证但未集成，根因未解。规整一次0→4高阶单位、14.59069ms，仅资源策略；全部代理测试和连接关闭。管理粗估83/100保持，稳定5Hz、长期、HDMI、采集终版及合法零拷贝继续待。[结果](../../../tools/pose-v1/STARTUP-GUARD-RESULTS-20261009.md)／[ADR_20](../../../ADR/ADR_20.md)／[接入契约](../../../tools/pose-v1/INVOCATION-EVIDENCE-INTEGRATION-NEXT-20261009.md)／[恢复点](../../../tools/pose-v1/evidence/startup-guard-20261009-r1/next-checkpoint.json)。

## 历史检查点：2026-10-09 新快照/582完成检查及103完整回归

stage-guard-r1已实现并通过Host107、三窗＋重复及103输入/全输出/实际视频网络；合107正确硬件前向1615700FP32、1086编码1026网络。103无覆盖，三预热后100计量画面5.000193338Hz/P95 251.199778ms，本次有界门限达到，不能外推长期稳定5Hz。107次新计数检查全部首次638，没有额外等待；旧数据故障根因仍未证，不记永久修复。取证、首次启动可靠性、HDMI、30分钟和采集终版继续待，管理粗估83/100保持，仅工程管理估计。规整0/内核同/全资源与会话关闭。恢复：[结果](../../../tools/pose-v1/STAGE-GUARD-RESULTS-20261009.md)／[ADR_19](../../../ADR/ADR_19.md)／[检查点](../../../tools/pose-v1/evidence/stage-guard-20261009-r1/next-checkpoint.json)。

## 历史检查点：2026-10-09 103已实施，真实源/Host差异取证

103预算/独立参考/Native与ARM边界、Host107及新三窗完整全链通过；103负载第61次Scatter582拒绝NaN，前60完整结果906000FP32正确。真实源两轮67200字节与旧同CSI正确中间值逐位一致，Host输入0周期性块差异2096值/四NaN，根因仍未证。已按异常条件停止并释放资源/关闭会话，没有重跑/规整。当前是故障定位推进，不能增加为103/严格5Hz/长期通过，管理粗估83/100保持。恢复：[结果](../../../tools/pose-v1/BOUNDED-LOAD-RESULTS-20261009.md)／[检查点](../../../tools/pose-v1/evidence/bounded-load-20261009-r2/next-checkpoint.json)／[下一最小取证](../../../tools/pose-v1/HOST-STAGING-FAULT-NEXT-20261009.md)。

## 历史检查点：2026-10-09 有限覆盖与纯计时完成

保留异常读取，同r4身份33次2Hz＋33次5Hz纯计时共996,600FP32/997编码937网络通过。32次纯计时1,856记录/额外查询0，旧坏值及221.61ms尖峰未复现，设备异常源读回未触发；严格5Hz仍未验收，103/HDMI/长期待。完整恢复入口：[结果](../../../tools/pose-v1/SOURCE-COVERAGE-RESULTS-20261009.md)／[检查点](../../../tools/pose-v1/evidence/source-coverage-20261009-r4/next-checkpoint.json)。所有代理服务和连接已结束，按失败策略停止，管理粗估83/100保持，不以新覆盖代替新功能验收。

## 历史检查点：2026-10-09 r4有限全链恢复通过

源读回工具已实现并经Host验证；8正确前向/120,800FP32及最终499编码469网络通过，旧异常未复现，设备源异常读取未实测，根因仍待。控制超时/404与旧三块异常均保留。当前服务/连接关闭，按失败策略停止。恢复：[r4结果](../../../tools/pose-v1/SOURCE-READBACK-R4-RESULTS-20261009.md)／[检查点](../../../tools/pose-v1/evidence/source-readback-20261009-r4/next-checkpoint.json)。不把有限通过增加为5Hz、103、首启动永久可靠性或长期验收。

## 当前检查点：2026-10-09 已取得周期性异常数据

当前首版既有异构／显示／RTSP成功结论保留。本轮纯计时和异常捕获实现/Host通过；硬件回归首帧188拒绝NaN，取得720字节及与旧参考的三块差异，尚未定位来源。当前无服务或后台，按失败策略停止。恢复：[结果](../../../tools/pose-v1/FORWARD-TRACE-R3-RESULTS-20261009.md)／[检查点](../../../tools/pose-v1/evidence/forward-trace-20261009-r3/next-checkpoint.json)。下一源数据与暂存判别；严格5Hz、旧尖峰、103、HDMI和长期仍未通过，不增加此前主观工作包百分比。

## 当前检查点：2026-10-08 前向尖峰取证

原首版异构/独立显示/RTSP全链已通过的结论保持。本轮Host与三窗通过，但5Hz诊断第4次GatherElements192索引异常停止；原第28次尖峰尚未定位，严格5Hz与长期未验收。扩展103请求只有计划和身份准备。恢复入口：[取证结果](../../../tools/pose-v1/FORWARD-TRACE-RESULTS-20261008.md)／[检查点](../../../tools/pose-v1/evidence/forward-trace-20261008-r1/next-checkpoint.json)。当前无运行服务、会话或后台测试，按失败策略停止。旧主观工作包进度不因一次失败改变为功能验收率。

> 当前：独立显示子进程可行性通过，70完整前向/1,057,000FP32和1479编码/849网络全来源/PTS/像素通过。5Hz33输入全消费无覆盖，32次交叠，4.99165Hz、画面P95 262.21ms，严格≥5Hz仍未验收；inv28 forward尖峰待定位，管理83/100保持。[结果](../../../tools/pose-v1/DISPLAY-PROCESS-RESULTS-20261008.md)、[下一方案](../../../tools/pose-v1/DISPLAY-PROCESS-NEXT-20261008.md)、[检查点](../../../tools/pose-v1/evidence/display-process-20261008-r1/next-checkpoint.json)、[ADR_15](../../../ADR/ADR_15.md)。无后台，最终order7+0，长期启动/HDMI/30分钟仍待。

<details>
<summary>历次阶段更新（历史，旧入口不作当前待办）</summary>

> 当前：整机低日志计量完成，62完整前向/936200FP32、981编码/591网络/全部来源/PTS/像素通过。5Hz发送33、消费29、覆盖4，实测4.22311Hz，画面P95 444.50684ms，5Hz未达标；主线程显示44.31ms为下一修正依据。管理83/100保持。[结果](../../../tools/pose-v1/SYSTEM-TIMING-RESULTS-20261008.md)、[下一方案](../../../tools/pose-v1/SYSTEM-TIMING-NEXT-20261008.md)、[检查点](../../../tools/pose-v1/evidence/system-timing-20261008-r2/next-checkpoint.json)、[ADR_14](../../../ADR/ADR_14.md)。无后台；结束时order7+为0，首次启动条件及长期/HDMI仍待。


> 当前：保存优先及一次规整后，TCP三/27＋重复32前向全部逐位旧参考、984编码/864网络全来源/PTS/像素通过。旧失配未复现、原因未证；本轮有限恢复不作长期CMA保证。[结果](../../../tools/pose-v1/PRESAVED-RESULTS-20261008.md)、[检查点](../../../tools/pose-v1/evidence/tcp-presaved-20261008-r1/next-checkpoint.json)、[ADR_13](../../../ADR/ADR_13.md)。管理83/100保持，无后台，后续独立整机计量/长期/HDMI仍待；下方停止入口为历史。

当前审阅入口：[本次进度与后续方案](../../../tools/pose-v1/PROJECT-STATUS-AND-NEXT-20261008.md)。本轮仅文档核对，未启动新板测。


> 当前：guarded固化32回归/977编码/767网络通过；TCP三窗＋重复四实际窗口/496编码/376网络完整通过。TCP27第六窗输出失配，新捕获已Host107/Native/ARM通过，但VPU首次普通order7分配失败阻断取证。未27/整机验收，管理83/100保持。[结果](../../../tools/pose-v1/TCP-INTEGRATION-RESULTS-20261008.md)、[检查点](../../../tools/pose-v1/evidence/tcp-evidence-20261008-r1/next-checkpoint.json)、[恢复计划](../../../tools/pose-v1/TCP-RECOVERY-NEXT-20261008.md)。无后台，未规整/重启，下方入口为历史。

> 最新：真实本地CSI三窗＋重复/27窗＋重复→推理→render→VPU→RTSP有限串联通过，32完整前向/980编码/650网络像素及全部32来源/实际PTS正确；主线程Engine持有到工作者结束。guarded网络候选独立正常223帧/慢客户端拒绝通过，尚未入r2；晚加入40帧及短控制91帧失败保留。[结果](../../../tools/pose-v1/LIVE-RESULTS-20261008.md)、[检查点](../../../tools/pose-v1/evidence/live-20261008-completion/next-checkpoint.json)、[ADR_09/10](../../../ADR/README.md)。下一固化guarded并接TCP窗口前端，整机/长期/HDMI仍待。管理估计83/100仅工作包主观份额；下方81等为历史。

> 2026-10-08最新：全项目难点归档到[ADR主题索引](../../../ADR/README.md)，模块设计规范写入Agents。下一阶段已完成owned AU桥Native/ARM及200网络帧/像素/实际PTS门检；输入是已记录的capture，未新初始化VPU/NPU，真实在线闭环尚待。[结果](../../../tools/pose-v1/OWNED-AU-RESULTS-20261008.md)、[接续入口](../../../tools/pose-v1/ONLINE-INTEGRATION-NEXT-20261008.md)。工程粗估81/100保持，不能以模块门检提高整机通过率。

> 2026-10-08当前：VPU启动资源修正三次独立进程通过，同进程有限工作者32前向/987编码及全部源映射通过。[启动结果](../../../tools/pose-v1/VPU-STARTUP-RESULTS-20261008.md)、[常驻/视频](../../../tools/pose-v1/RESIDENT-RESULTS-20261008.md)、[检查点](../../../tools/pose-v1/evidence/resident-20261008-r6/next-checkpoint.json)。下一在线owned AU/RTSP；不是常驻daemon或整机/长期验收，HDMI仍待配套。旧“启动未过”对应六缓冲/后台Engine失败，历史保留。管理粗估81/100保持，按失败策略停止，无后台。

> 2026-10-08最新：同进程真实推理→画面→VPU有限链路已核验，但无规整的新进程重复在MVX固件连续页分配失败。[完整结果](../../../tools/pose-v1/PIPELINE-RESULTS-20261008.md)、[下一分配取证](../../../tools/pose-v1/PIPELINE-NEXT-20261008.md)。两成功不记稳定启动/实时RTSP验收，主观管理估计81/100保持；HDMI/整机5Hz/30分钟仍待。已关闭测试与连接，无后台；旧RTSP准备合并条目按历史理解。

> 当前已推进到独立RTSP传输/重连和直接播放器通过：[RTSP结果](../../../tools/pose-v1/RTSP-RESULTS-20261007.md)、[当前检查点](../../../tools/pose-v1/evidence/rtsp-20261007-r3/next-checkpoint.json)。两会话200帧＋直接播放器100帧像素逐位原视频，下一为真实推理→编码→RTSP接入；显式色彩/HDMI/整机长期仍待。管理工作包估计更新81/100（约80%），仅主观工程份额，不是功能通过率或工期；历史78分记录保留。

<details>
<summary>此前阶段状态与暂停记录（历史，当前入口见上方）</summary>

> 当前视频任务已恢复，V2-A真实骨架文件编码与独立上下文重复通过：[r5结果/视频](../../../tools/pose-v1/VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md)、[当前检查点](../../../tools/pose-v1/evidence/video-descriptor-20261007-r5/next-checkpoint.json)。54帧/27来源主机核验，MMAP cookie兼容修正后两次码流逐位一致，无新增内核异常。HDMI1080p60配套仍缺时序/scanout/安全停止证据，未写入；下一独立RTSP准备与动态样片审查。整机/长期仍待，管理粗估78/100保持。下方暂停、未编码等条目为各轮历史。

> 当前任务已暂停：[恢复入口](../../../tools/pose-v1/RESUME-VIDEO-20261007.md)、[检查点](../../../tools/pose-v1/evidence/video-sequence-20261007-r1/next-checkpoint.json)。新有限VPU API构建/27真实画面与54输入/协商通过，真实编码触发固件MMU ABORT（9提交/3归还/仅3部分帧），未动态验收。HDMI只读配套与离线1080p色条完成，真实时序/安全scanout仍缺证、未写入。会话全部关闭/认证前补查已取消；等待独立执行许可，无自动工作。首版估算78/100保持，新增故障不计功能份额。

> 最新授权：已审查H264样片，允许HDMI测试，撤销下方暂停。[下一视频计划](../../../tools/pose-v1/NEXT-VIDEO-PLAN-20261007.md)先做真实骨架动态文件与HDMI配套核对，再1080p60实屏/RTSP/真实推理合并。当前仅整理计划，未新时序切换或板测，管理估算78/100保持。

> 当前最新：独立VPU H.264文件编码与Windows主机30帧解码审查通过，[样片/结果](../../../tools/pose-v1/VPU-RESULTS-20261007.md)。720p10fps/3秒，原始/MP4两文件回传哈希及解码像素一致；没有实时NPU并发/RTSP/长期结论。接屏后将HDMI目标改为1920×1080@60Hz并暂停测试，硬件时序未修改。新[恢复点](../../../tools/pose-v1/evidence/vpu-20261007-r1/next-checkpoint.json)，下方未编码/未接屏文字为历史。

> 当前最新：E1-C CPU渲染与三帧网络结果绘图已通过，[真实预览与结果](../../../tools/pose-v1/RENDER-RESULTS-20261007.md)。V0确认了MVX多平面/NV12/NV21/H264枚举，尚未实际编码；HDMI未接屏、720p配套未确认。新[检查点](../../../tools/pose-v1/evidence/render-20261007-r1/next-checkpoint.json)；下方E1-A/B入口按此前阶段理解。

> 当前最新：E1-A生产接口与E1-B TCP回放首批已实板通过，[38次全输出回归与网络结果](../../../tools/pose-v1/APPLICATION-RESULTS-20261007.md)。接收→PS预处理→PS/NPU→完整候选结果已连通，尚缺骨架画面与HDMI/RTSP。新[恢复点](../../../tools/pose-v1/evidence/application-20261007-r2/next-checkpoint.json)；此前P2恢复点按历史保留。

> 最新：已验收现有27样本数值阶段，P2单时钟定位与lazy-r4优化验证完成，处理核心基线5.24655Hz/P95 190.75409ms；正式应用、双路视频与长期闭环仍待。原query身份推断不改写，N2非阻断。旧N1/P1状态按此前日期理解。下一恢复点见[checkpoint](../../../tools/pose-v1/evidence/perf-20261007-lazy-r4/next-checkpoint.json)。

</details>


</details>

人工确认当前异构方案完成首版全流程，零拷贝/图/新算子性能优化后置。[ADR_01](../../../ADR/ADR_01.md)记录困境，[全流程计划](../../../tools/pose-v1/FULL-FLOW-PLAN-20261007.md)明确接口→网络→渲染→独立视频→双路长期验收。原规划归档未计功能份额；现按已实测E1-A/B更新管理估计。

当前处于**保存优先＋单次规整条件下的TCP固定回放→推理→骨架→VPU→guarded RTSP有限三/27全链通过，准备独立整机计量**的阶段。旧失配未复现、原因未知，长期首启动可靠性仍待。
E0/N1/P1、H0、P2、E1-A/B/C已完成工程门检，全部会话关闭；V0只完成部分配套核对，后续按独立编码/视频与双路长期门检推进，候选身份诊断非阻断。

## 完成了多少

以已批准的“原始CSI回放→Lite PS预处理→PS/NPU推理→14关节骨架→1080p60 HDMI＋H.264 RTSP”首版为范围，HDMI测试已授权但配套仍未知，目标替代原720p60，H264分支仍720p/目标10fps。
**工程就绪度粗估约80%–85%（83/100）**。本轮完成有限TCP27恢复验证，仍不因重复门检或恢复操作加份额；整机/可靠性/HDMI未完成。不是按文件/实验数量累计，也不是实测工作量、工期、比赛评分或功能通过率。
基础平台和推理难点已取得实测成果，后续未知数据、整机性能和视频闭环仍需要验证；该估算不表示剩余工期。

| 工作包 | 规划权重 | 已具备份额（估计） | 当前事实与尚缺内容 |
| --- | ---: | ---: | --- |
| 平台与工具链 | 15 | 15 | SD启动/扩容、SSH历史通信、FPAI编译、Procise流水灯与IP交接、Lite运行身份已验证；完整显示配套另列 |
| CSI契约与PS预处理 | 15 | 15 | 九组300份真实窗口跨主机/Lite逐位一致，非法输入拒绝；人工±π仍保留失败诊断，不扩展为任意输入通过 |
| 首版模型与参考环境 | 10 | 9 | 2024 epoch442/固定ONNX/ZG/RAW与隔离ORT环境保持；27份参考核验完成，不扩大为未知数据精度通过 |
| PS/NPU混合运行 | 20 | 18 | 无固定Tokens依赖的生产入口与验证入口8次全输出回归通过；网络3/27帧真实前向通过，长期应用仍待 |
| 部署数值验收 | 10 | 9 | 现有27样本阶段由明确验收；原误差保留，query身份未证，不推广至未知数据 |
| 正式应用与性能 | 10 | 7 | 网络结果及CPU画面接入通过，27帧ARM渲染/三格式逐位一致；核心短期5.25Hz保持，整机争用/吞吐与长期仍待 |
| HDMI、编码与RTSP双路 | 15 | 10 | 新保存优先TCP三/27有限全链通过；一次规整恢复有效但旧失配原因/长期首启动未证，显式色彩/HDMI1080p60配套与实屏仍待 |
| 长期运行与交付验收 | 5 | 0 | 30分钟闭环、端到端性能、异常恢复演示及最终交付材料仍待 |
| 合计 | 100 | 83 | 粗略表达为约80%–85%，只用于管理；历史58/64/69/72/75/78/81分保留，不是工期/比赛评分 |

上述份额是本次整理采用的主观估算，后续按验收成果更新，不因新增文件或重复实验自动增加。
更广义的最终比赛作品还涉及真实采集设备、同步和新场景验证；回放首版尚不代表实时感知作品完成，当前未给最终作品单独估算百分比。

## 已验证、待验证与旁支研究

**已验证的主链成果：** 平台可启动、工具可构建；300份真实CSI预处理一致；CPU最小适配107例/12注册/22输出59,600个FP32逐位一致；
r6混合图在308/309/310及同Session重复308上有效响应，三帧输出不同、重复首帧全部捕获及输出一致。
原1173 HardOp由七个ZG实际执行组完整追溯，六计算Host保留；Matmul仍由NPU执行。

**已解决的主要阻断：** 环境和清单问题、CPU算子注册/全有效布局受限适配、Session融合映射核验，以及跨帧旧计数导致读旧结果。
r6使用官方SDK状态清理`reset(1)`，执行前确认0、输出就绪及最终745后才进入下一帧。745是当前固定图的验收基线，不能推广到其他模型。

**数值阶段与适用范围：** 现有27样本由明确验收，完整误差保留。S52_18_317离群帧支持排名交换推断，跨端query身份仍未证明；不推广为未知数据、MPJPE或物理标定通过。

**尚未通过的验收：** 整机≥5Hz、长期延迟/启动与内存可靠性、完整混合链路慢客户端清理、HDMI及30分钟闭环。guarded和TCP完整窗口已接入并有限三/27通过；2Hz带保存运行不等于整机5Hz。子进程已将显示从主线程移出，5Hz输入全消费、实测4.99165Hz；有限画面P95 262.21ms而严格5Hz未过。5.24655Hz仍仅独立短期核心基线。

**算法旁支单独记录：** 2026版迁移10轮已结束，最佳122.873804mm相对24版123.085352mm改善约0.212mm，不能认定稳定收益；
全新500轮实验在第6轮分支退化停止，未完成500轮；零衰减10轮完成，但后期分化/细化注意力抽检梯度仍为0。
这些实验已归档并保持停止，首版部署继续使用2024 epoch442；不把训练实验数量累计成板端系统进度。

## 当前任务完成位置与下一步

E0/N1/P1＋H0、P2及首批E1-A/B均已完成；当前应用依据为[E1结果](../../../tools/pose-v1/APPLICATION-RESULTS-20261007.md)与[完成证据](../../../tools/pose-v1/evidence/application-20261007-r2/completion-review.json)，独立[P2性能基线](../../../tools/pose-v1/P2-RESULTS-20261007.md)与[r2扩展数值结果](../../../tools/pose-v1/RUNTIME-RESULTS-20261007.md)保留。

| 阶段 | 最新状态 | 尚未通过的边界 |
| --- | --- | --- |
| E0运行核心 | 原核心证据保持，新生产/验证两入口8次与r6逐位一致 | 生产入口无冻结参考依赖；未知数据分布精度和长期应用仍待 |
| N1九组扩展 | ORT27独立核验、Lite28次、476捕获/CPU364000值与全误差报告完成；明确验收 | query身份未证明，不推广至未知数据或MPJPE |
| P1/P2性能 | profiling关闭、单时钟分段与消息构造优化；Host107/原样本回归通过，30计量5.24655Hz | 仅处理核心短期基线，未包含网络/渲染/编码或30分钟 |
| H0/V0/V2部分配套 | MVX协商/两缓冲/实际capture与RTP时间轴/主机像素通过 | HDMI1080p60时序/换帧未确认，已允许测试；SPS显式色彩/关节标定未知 |
| E1/F0应用输出 | TCP完整窗口→主线程Engine→骨架→VPU→guarded RTSP三/27有限门检通过，32来源/保存值完整 | 整机性能/HDMI/长期未过；旧失配未复现原因未知，规整恢复不是永久内存方案 |

低日志计量及[独立子进程可行性](../../../tools/pose-v1/DISPLAY-PROCESS-RESULTS-20261008.md)本批已完成。下一按[尖峰/有界运行方案](../../../tools/pose-v1/DISPLAY-PROCESS-NEXT-20261008.md)准备有限单钟内部定位和更长统计入口；启动资源、CMA/HDMI仍需匹配接口，深度优化后置。
新恢复点：[当前检查点](../../../tools/pose-v1/evidence/display-process-20261008-r1/next-checkpoint.json)。一次规整授权已使用，当前无后台；旧检查点保留，不重跑历史失败或用模块门检替代整机验收。

## 项目文件导航

| 位置 | 用途 |
| --- | --- |
| [PROJECT-PROGRESS.md](../../../PROJECT-PROGRESS.md) | 全项目当前阶段、估算口径和验收差距；首先阅读 |
| [Done.md](../../../Done.md) | 已完成开发/验证及历史失败修正，保持“工程内容总结＋后续开发参考”模板 |
| [ToDoLists.md](../../../ToDoLists.md) | 当前任务顺序和未完成清单，包含暂停与批准边界 |
| [AGENTS.md](../../../AGENTS.md) | 执行权限、历史批准范围、停止条件 |
| [REFERENCES.md](../../../REFERENCES.md)／[ADR_00](../../../ADR/ADR_00.md)／[ADR_01](../../../ADR/ADR_01.md) | 资料索引、首版架构/验收目标、当前异构取舍与延期优化 |
| [最新检查点](../../../tools/pose-v1/evidence/combined-read-20261010-r1/next-checkpoint.json) | 组合有限内容通过，较高负载582有限数据失配待取证；旧错误与长期可靠性保留 |
| `software/pose_v1` | 预处理、已验证检查器、CPU适配与新隔离运行核心；源码不等同验收 |
| `tools/pose-v1`／`evidence` | 准备/构建/审查工具、命令说明和实际证据；旧r1–r5为历史 |
| `.local` | 隔离Conda、模型样本包、构建副本和完整生成物，保留身份，不覆盖旧产物 |
| `FPGA` | 流水灯及IP交接工程；不是已完成的AI＋HDMI系统工程 |
| `tools/pose26-*` | 独立算法实验及停止结果；本轮不恢复训练 |
| `Logs` | 日志存放入口；实际验收仍引用各阶段完整evidence |

本次采用总览、恢复入口和历史折叠整理，不移动、删除或重命名已有工程、模型、构建和失败证据。

主要依据：[300份PS结果](../../../tools/pose-v1/RESULTS-300.md)、[CPU结果](../../../tools/pose-v1/CPU-ADAPTER-RESULTS-20261006.md)、
[r6实板结果](../../../tools/pose-v1/MIXED-FRAME-STATE-R6-RESULTS.md)、[r6完成核验](../../../tools/pose-v1/evidence/mixed-20261006-frame-state-r6/completion-review.json)、
[新核心构建核验](../../../tools/pose-v1/evidence/runtime-20261006-r1/build.acceptance.json)、[原暂停检查点](../../../tools/pose-v1/evidence/runtime-20261006-r1/pause-checkpoint.json)。

2026-10-07新增依据：[完整结果](../../../tools/pose-v1/RUNTIME-RESULTS-20261007.md)、[误差报告](../../../tools/pose-v1/evidence/runtime-20261007-r2/ONNX27-comparison.json)、[性能基线](../../../tools/pose-v1/evidence/runtime-20261007-r2/P1-performance-analysis.json)。
