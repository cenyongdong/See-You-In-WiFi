# 整理前历史文档快照

2026-10-13迁存。以下所有“当前”“待执行”均是原阶段描述，请勿用于判定今日状态；相对文档链接已按新位置调整。最新入口为根目录PROJECT-PROGRESS.md或DIFFICULTIES.md。

# 项目难点索引

最新：[ADR_45](../../../ADR/ADR_45.md)记录演示整合、VPU连续页失败/一次获准重启、Engine目录与Producer Recorder配置遗漏，以及独立demo_engine修正。三窗口与60窗口全链显示/正常回收已过；成功阶段规整0。首次启动永久可靠性未证，旧DATA96/800坏读定位暂停，原保护/证据保持。[技术总汇](../../../ADR/TechDetails.md)／[结果](../../../tools/pose-v1/DEMO-RESULTS-20261011.md)。以下当前为历史。

最新：[ADR_44](../../../ADR/ADR_44.md)，目录mkdir等待以放行前预建/热一次令牌移出并验；首次DATA96/拥有副本指纹与文件一致但保存后记录、全部上一B，四晚物理源读正确，首次Host目的后续状态未观测，责任未证。Host测试symlink回传解包拒绝以普通字节/精确链接元数据修正，无板测重跑。[结果](../../../tools/pose-v1/PRODUCER-PREPARED-RESULTS-20261011.md)。以下当前为历史。

2026-10-11最新：[ADR_43](../../../ADR/ADR_43.md)记录源租约/Host188160字节read过、153前向正确、有VPUinv49目录等待915.86ms且准备截止成功拦截，物理晚源read未触发／根因未修；[结果](../../../tools/pose-v1/PRODUCER-SOURCE-READ-RESULTS-20261011.md)／[下一目录预备](../../../tools/pose-v1/PRODUCER-SOURCE-READ-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-source-read-20261011-r2/next-checkpoint.json)。221 NoInput视频前缀/abort清理过，所有连接结束，原异常读取保持，下一未执行，以下当前为历史。

2026-10-11最新：[ADR_42](../../../ADR/ADR_42.md)记录高地址SDK前缀控制、四调用/off100通过、on inv49 DATA800逐位前帧A的独立更小失配；首次输出已错但无晚源证据，责任未证。214 NoInput视频前缀/abort清理过，全部连接结束；[结果](../../../tools/pose-v1/PRODUCER-ADDRESS-RESULTS-20261011.md)／[下一失败只读租约](../../../tools/pose-v1/PRODUCER-ADDRESS-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-address-20261011-r2/next-checkpoint.json)。下一未执行、原正式异常读取保留，以下当前为历史。

2026-10-11最新：[ADR_41](../../../ADR/ADR_41.md)归档reset前分段／准备后绝对时隙、off/on各100及307 NoInput视频正常回收。2352000 FP32逐位，旧1.764秒尖峰未复现，保存区间等待已观察但底层原因未证，正式坏读未修；[结果](../../../tools/pose-v1/PRODUCER-PHASE-RESULTS-20261011.md)／[下一公开高地址可行性](../../../tools/pose-v1/PRODUCER-PHASE-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-phase-20261011-r2/next-checkpoint.json)。原异常读取保持、下一未执行、程序连接全结束，以下当前为历史。

2026-10-11最新：[ADR_40](../../../ADR/ADR_40.md)记录同身份off100通过、on82数值正确后时隙失败及reset前1.764秒空档，正式根因未修。271packet／270 NoInput图像／162复制交叠、异常清理通过，正常drain-LAST未过；[结果](../../../tools/pose-v1/PRODUCER-VPU-RESULTS-20261011.md)／[下一分段观察](../../../tools/pose-v1/PRODUCER-VPU-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-vpu-20261011-r2/next-checkpoint.json)。原异常读取保留，下一未执行，全部程序连接结束，以下当前为历史。

2026-10-11最新：[ADR_39](../../../ADR/ADR_39.md)记录独立19成员物理部署／四调用、mock无数据搬运的门检修正与locale只读核验。47040 FP32／0→11／释放通过，正式并发根因未修；[结果](../../../tools/pose-v1/PRODUCER-GROUP-RESULTS-20261011.md)／[下一有无VPU对照](../../../tools/pose-v1/PRODUCER-GROUP-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-group-20261011-r2/next-checkpoint.json)。100调用未实施，原异常读取保持，以下当前为历史。

2026-10-11最新：[ADR_38](../../../ADR/ADR_38.md)记录真实参数／19来源映射／受限FP16-TF32参考及mock独立0→11。数学参考已闭合，物理读取根因未修；[结果](../../../tools/pose-v1/PRODUCER-REFERENCE-RESULTS-20261011.md)／[下一](../../../tools/pose-v1/PRODUCER-REFERENCE-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/producer-reference-20261011-r2/next-checkpoint.json)。无新物理前向／并发通过，全部程序和连接结束，以下当前为历史。

2026-10-11最新：[ADR_37](../../../ADR/ADR_37.md)记录生产者检查器条件copy、零指令Cast、19成员参考缺口、官方部署映射与日志门检/误检索修正。[结果](../../../tools/pose-v1/PRODUCER-CONTRACT-RESULTS-20261011.md)／[下一](../../../tools/pose-v1/PRODUCER-CONTRACT-NEXT-20261011.md)／[数据核验](../../../tools/pose-v1/evidence/producer-contract-20261011-r2/data-review.json)／[恢复](../../../tools/pose-v1/evidence/producer-contract-20261011-r2/next-checkpoint.json)。无模型前向，新根因未修；r3 exit1为一/两日志数量错误，原码/数据保留，r4仅编译。全部会话结束，以下当前为历史。

2026-10-11最新：[ADR_36](../../../ADR/ADR_36.md)匹配AXI／UDMA责任审查及两方法／四条件内存对照完成；400动态对过，无NPU生产，原模型根因未修。锁／轮询／cache同步存在但生产完成未知。[结果](../../../tools/pose-v1/AXI-READ-RESULTS-20261011.md)／[责任证据入口](../../../tools/pose-v1/AXI-READ-RESPONSIBILITY-20261011.md)／[下一](../../../tools/pose-v1/AXI-READ-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/axi-pair-20261011-r4/next-checkpoint.json)。本批已结束、无规整／后台；以下当前为历史。

2026-10-11最新：[ADR_35](../../../ADR/ADR_35.md)记录read返回／CPU前快照、实际目标链接遗漏及修正、执行位、参考覆盖难点。48正确后192立即592坏值全部等于前输入同偏移，CPU前不变、两晚源正确；共享读取暂存／完成责任待证。[结果](../../../tools/pose-v1/READ-PHASE-RESULTS-20261011.md)／[下一](../../../tools/pose-v1/READ-PHASE-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/read-phase-20261011-r3/next-checkpoint.json)。原异常读取保留，已停止无重跑，以下当前为历史。

2026-10-11最新：[ADR_34](../../../ADR/ADR_34.md)记录公开回调outputs契约／生产句柄边界限制、Host原Gather绑定上下文、打包身份、8任务保存预算及实际传输ID审查难点。Host／四窗口已通过；55正确后192初始Host索引1584变化、两晚源正确，首次read／暂存责任待查。[结果](../../../tools/pose-v1/UPSTREAM-BOUNDARY-RESULTS-20261011.md)／[下一](../../../tools/pose-v1/UPSTREAM-BOUNDARY-NEXT-20261011.md)／[恢复](../../../tools/pose-v1/evidence/upstream-boundary-20261011-r4/next-checkpoint.json)。异常保存停止，根因未修，以下当前为历史。

2026-10-10最新：[完整保存与晚源结果](../../../tools/pose-v1/FINAL-EVIDENCE-RESULTS-20261010.md)／[ADR_33](../../../ADR/ADR_33.md)／[下一边界方案](../../../tools/pose-v1/FINAL-EVIDENCE-NEXT-20261010.md)／[当前恢复点](../../../tools/pose-v1/evidence/final-evidence-20261010-r2/next-checkpoint.json)。保存缺口已解决，582上游数据异常未解决；本批已停止、无后台，严格5Hz/长期/HDMI保持待验。以下最新为历史。

2026-10-10当前：[ADR_31](../../../ADR/ADR_31.md)组合有限内容门检过；[ADR_32](../../../ADR/ADR_32.md)PC粗时钟和严格吞吐未过；[ADR_33](../../../ADR/ADR_33.md)582有限更新数据异常、最终门检晚源未触发和结果汇总重复验收缺口，root未证，已停止。本批错误和bad拥有数据完整保留，[下一](../../../tools/pose-v1/COMBINED-READ-NEXT-20261010.md)。 以下当前为历史。

2026-10-10当前：[ADR_30](../../../ADR/ADR_30.md)公开read直接进入自有Host输入暂存，真实画面107完整数值及视频有限门检通过；旧192坏块本轮未复现，read仍共享源区域，根因与长期可靠性未证。异常取证保持，旧失败不改。暂停已撤销，[结果](../../../tools/pose-v1/INPUT-READ-RESULTS-20261010.md)／[下一](../../../tools/pose-v1/INPUT-READ-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_29](../../../ADR/ADR_29.md)真实拥有画面2Hz条件inv20的192残留复现：144非整数／8段同此前slot0字节，两晚源正确，对象／计数稳定；20正确输出与视频前缀已核验，root未修。暂停，[恢复入口](../../../tools/pose-v1/RESUME-PICTURE-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_28](../../../ADR/ADR_28.md)单次常驻三窗→103通过，解决阶段重复申请的编排与107诊断容量／编号碰撞边界；旧192坏块未复现，首次启动在一次规整及普通高阶余量条件下成功，不认定永久可靠。[结果](../../../tools/pose-v1/RESIDENT-SEQUENCE-RESULTS-20261010.md)／[下一](../../../tools/pose-v1/RESIDENT-SEQUENCE-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_27](../../../ADR/ADR_27.md)同程序对照前三阶段通过，最后VPU启动512KiB普通连续页不足，规整后仍失败；Engine创建前退出，不归因192模型坏块。[ADR_02](../../../ADR/ADR_02.md)同决策追加首次启动反例，明确常驻与首次启动分别验收。[结果](../../../tools/pose-v1/MODEL-VPU-RESULTS-20261010.md)／[下一方案](../../../tools/pose-v1/MODEL-VPU-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_26](../../../ADR/ADR_26.md)记录无视频真实混合模型4＋103全部完整输出正确、192源同旧失败／对象和计数稳定。坏块未复现，视频不是已证根因；堆、初始化与保存I/O差别保留。规整0、全项目程序／会话结束。下一同身份仅模型／合成VPU对照仅准备。[结果](../../../tools/pose-v1/MODEL-ONLY-RESULTS-20261010.md)／[方案](../../../tools/pose-v1/MODEL-ONLY-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_25](../../../ADR/ADR_25.md)记录公开容量／合法较高位置对照：DefaultMemManager公开地址空间确认，96MiB SDK自有占位未触碰数据，实际两源100667392／100697664动态100及VPU100全正确、公共块全部归还。本批规整0、根因未修；约96MiB位置不能替代实际模型104MiB／NPU生产。下一原Engine无视频有限对照仅准备。[结果](../../../tools/pose-v1/PLDDR-POSITION-RESULTS-20261010.md)／[方案](../../../tools/pose-v1/PLDDR-POSITION-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_24](../../../ADR/ADR_24.md)记录真实192类型／动态更新／VPU并发独立三阶段各100对正确，低位SDK源4096／34368未复现坏块；与模型约104MiB来源及NPU生产仍不同。一次资源规整不当数值修复，跨内核采集格式仅旧©单行精确对齐，原字节保持。[结果](../../../tools/pose-v1/TYPED-SCRATCH-RESULTS-20261010.md)／[下一合法源位置对照](../../../tools/pose-v1/TYPED-SCRATCH-NEXT-20261010.md)。全测试关闭，根因未修，以下当前为历史。

2026-10-10当前：[ADR_23](../../../ADR/ADR_23.md)记录真实模型公开对象／dtype／全有效分布／范围与原shadow一致、同copy前后稳定，但inv72的192仍有128有限非整数、7段同前次复制，晚源正确。没有观察到同域源或Host范围重叠，内部暂存／DMA／生产瞬间可见性仍未证；元数据分配／时序扰动不当修复。[结果](../../../tools/pose-v1/TENSOR-IDENTITY-RESULTS-20261010.md)／[下一类型与动态模式对照](../../../tools/pose-v1/TENSOR-IDENTITY-NEXT-20261010.md)，已安全停止，无失败重跑。以下当前为历史。

2026-10-10当前：[ADR_22](../../../ADR/ADR_22.md)记录SDK-owned双源100对无VPU＋100对编码并发均正确，200合成图像／实际PTS通过。模型坏块未在独立1D／低位／固定模式条件复现，实际dtype／分布／chunk／源位置／生产时序差别继续待证，未根因修复。部分异常保存补caller-owned字节，Host107明确身份复用。[结果](../../../tools/pose-v1/SCRATCH-COPY-RESULTS-20261010.md)／[下一对象身份观察](../../../tools/pose-v1/SCRATCH-COPY-NEXT-20261010.md)。规整0、会话关闭，以下当前／最新为历史。

2026-10-09当前：[ADR_21](../../../ADR/ADR_21.md)独立记录192四点计数和残留判别。新103第4次失败时计数234，1728坏索引55段逐位前次数据复制同偏移、晚源正确；不默认加wait-to234，搬运／可见性待证。[结果](../../../tools/pose-v1/PRODUCER-COUNT-RESULTS-20261009.md)／[受控搬运方案](../../../tools/pose-v1/PRODUCER-COUNT-NEXT-20261009.md)。七项保存完好，103／性能未过。以下“当前／最新”为历史。

2026-10-09当前：[ADR_20](../../../ADR/ADR_20.md)单帧取证／独立落盘已接入，Host／三窗通过；新103第12次192索引496非整数拒绝。18坏段同前次数据复制同偏移，Host256对齐、两个晚源正确；早读与SDK DMA暂存／同步责任未证。六项保存、3输入47760字节、102元数据及ARM参考完整。[结果](../../../tools/pose-v1/INVOCATION-GUARD-RESULTS-20261009.md)／[下一定位](../../../tools/pose-v1/INVOCATION-GUARD-NEXT-20261009.md)，没有新103／性能通过。以下“最新”为历史。

2026-10-09最新：[ADR_20](../../../ADR/ADR_20.md)记录有限姿态652值/35候选失配、最高分骨架不变以及保存再比较导致元数据缺失。新SDK-free单帧拥有值/独立flush模块测试通过，主程序接入待；原异常/拒绝及源码保持。静态638仅覆盖582，649结束720；[SDK审计](../../../tools/pose-v1/SDK-MAPPING-AUDIT-20261009.md)区分UDMA同步与PL DDR映射，不猜零拷贝修复。以下“最新”为历史。

2026-10-09最新：[ADR_19](../../../ADR/ADR_19.md)新增Host原复制后shadow、元数据/FP32对齐与582生产组638完成检查。Host、三窗及103全链通过，107次新增检查均首次638、无额外等待；旧异常未复现，不能写等待修复或DMA/cache fence已证。[ADR_17](../../../ADR/ADR_17.md)保留NaN/周期坏块及稍后正确源，根因继续待验证。短期100计量5.000193338Hz达到门限且余量极小，不代替永久可靠性/长期。见[完整结果](../../../tools/pose-v1/STAGE-GUARD-RESULTS-20261009.md)。下面“最新”为历史。

2026-10-09最新：[103边界/参考工程](../../../ADR/ADR_18.md)已实现Host/三窗通过，负载第61 Scatter582失败；[ADR_17](../../../ADR/ADR_17.md)首次实际设备源67200字节与旧正确同CSI中间值一致，而Host暂存0有2096值/四NaN异常。原复制瞬间的源/临时/目标责任未证，下一复制返回shadow和指针对齐取证，不以换API或规整猜修复。[当前结果](../../../tools/pose-v1/BOUNDED-LOAD-RESULTS-20261009.md)。以下以前“最新”为历史。

2026-10-09最新：[异常捕获保留与66次覆盖](../../../tools/pose-v1/SOURCE-COVERAGE-RESULTS-20261009.md)、[ADR_17](../../../ADR/ADR_17.md)、[纯计时与有限节拍ADR_16](../../../ADR/ADR_16.md)。旧三个坏块未复现、设备异常源读取0；32次无额外查询forward最大190.55ms，旧221.61ms原因未证。实际输入4.97948Hz/画面4.98636Hz须与计算容量分开，不按名义5Hz或舍入判过。103全边界/参考策略是下一工程准备，以下此前“最新”按历史读取。

最新：[独立显示子进程](../../../ADR/ADR_15.md)已可行，70全参考/视频通过，33个5Hz输入全消费无覆盖；4.99165Hz不舍入判过，inv28 forward221.61ms尖峰未定位，连续分配可靠性仍待。

此前计量难点：[整机串行显示44.31ms/4.22Hz与结束时高阶块耗尽](../../../ADR/ADR_14.md)，原数值/来源通过，5Hz和长期首次分配未验；最小显示线程方案待实施。

每项记录现象、影响、证据、判断和当前结果。未查明不写成确定根因；原报告/失败目录保留，有决策取舍时使用独立ADR。

2026-10-08已补全从项目开始至当前的主题归档，入口[ADR索引](../../../ADR/README.md)。历史编号D01–D09保持；完整早期问题按下表定位，不把已解决的问题与未查明原因混为一谈。

| 历史主题 | 难点及解决路径 | ADR |
| --- | --- | --- |
| 平台/工具/证据 | FPGA约束和跨EDA IP；坏启动介质→换卡；扩容/SSH；编译SDK签名/日志；LF、gate与登录shell；ODR与预算 | [03](../../../ADR/ADR_03.md) |
| 数据/模型/训练 | 300真实CSI一致、人工相位边界仍失败；独立ORT；排名/数值验收；26迁移与500轮分支退化旁支 | [04](../../../ADR/ADR_04.md) |
| 异构推理 | 五缺注册/全有效布局；SDK显式搬运；融合1173追溯；跨帧绝对计数→reset(1)安全边界 | [05](../../../ADR/ADR_05.md)、[01](../../../ADR/ADR_01.md) |
| 性能/应用 | 单时钟/profiling-off/lazy消息；生产Engine；TCP完整窗口单槽；显示投影独立于数学 | [06](../../../ADR/ADR_06.md) |
| 视频/传输 | 格式顺序/MPLANE/cookie；owned packet/PTS；RTSP配套/保活；HDMI尚缺映射 | [07](../../../ADR/ADR_07.md) |
| 启动/常驻 | 普通高阶页6→2缓冲；队列popLatest；Engine主线程实测；在线模块契约 | [02](../../../ADR/ADR_02.md)、[08](../../../ADR/ADR_08.md) |

| 编号 | 难点与影响 | 当前判断/处理 | 状态与证据 |
| --- | --- | --- | --- |
| D01 | 新全局Case与冻结Host源不同布局，vector弱符号冲突导致Host139 | 新助手进入匿名namespace，原冻结源保持 | 已修正并Host107回归；[r2证据](../../../tools/pose-v1/evidence/pipeline-20261007-r2/failure-review.json) |
| D02 | Host图重复解析使60秒预算超时；r8在300秒完成95例后超时 | 首次解析2447.24ms；r8估计约338秒，新外部420秒完成107，拒绝规则不改 | 本批完整通过；[r3](../../../tools/pose-v1/evidence/pipeline-20261007-r3/failure-review.json)、[r8历史超时](../../../tools/pose-v1/evidence/pipeline-20261008-r8/host-timeout-review.json) |
| D03 | Engine初始化约29秒误计入文件编码25秒deadline | 有界producer时间独立记录，codec25秒/stall5秒及总180秒保持 | 有限回归通过；[r5证据](../../../tools/pose-v1/evidence/pipeline-20261008-r5/combined-failure-review.json) |
| D04 | MVX固件512KiB连续分配失败，阻断进程启动 | r7确认六缓冲耗尽普通高阶块；隔离请求2缓冲、实际返回2，CMA保持 | 本轮三次启动回归通过，非长期保证；[ADR_02](../../../ADR/ADR_02.md)、[启动证据](../../../tools/pose-v1/VPU-STARTUP-RESULTS-20261008.md) |
| D05 | HDMI时序/scanout/安全停止映射未建立 | 目标1080p60，配套不明不猜写 | 待验证；[V0配套](../../../tools/pose-v1/V0-VIDEO-PAIRING-20261007.md) |
| D06 | 在线编码→RTSP所有权/实际PTS及整机争用尚未验证 | owned字节、有界队列、常驻上下文分阶段接入，重复帧不计新姿态 | 待实现/验收；[F0接续](../../../tools/pose-v1/PIPELINE-NEXT-20261008.md) |
| D07 | 容量2画面队列若按FIFO采样会在积压时显示旧结果 | 采样使用popLatest，合并跳过旧帧独立计coalesced；满队列覆盖另计overwritten；实际PTS在源选择后取时刻 | Native及最终r6三/27窗口验证通过，无固定流丢弃；[当前ADR](../../../ADR/ADR_02.md) |
| D08 | PowerShell内嵌Python/C++或shell文本的引号与命令替换导致本机生成语法错误 | 源文件采用直接补丁、复杂生成改独立Python文件；依赖步骤检查退出码。原编译原型保留，错误未执行板端硬件 | 已改正工具路径；r1/r3/r4仅本机构建原型，r2只Host，最终r5另核验 |
| D09 | r5常驻编码并行下第一次模型读取出现非有限值，阻断三/27窗口验收 | 七ZG/七Host回调与745/ready完整、内核不变。r6只将Engine所有者回主线程，编码仍后台，32完整前向与987视频核验通过 | 首版采用实测主线程模式；SDK内部原因未证，不泛称线程限制；[失败](../../../tools/pose-v1/evidence/resident-20261008-r5/resident-three-failure-review.json)、[结果](../../../tools/pose-v1/RESIDENT-RESULTS-20261008.md) |
| D10 | live555外部线程通知限制，已编码参考链不能像画面队列一样随意覆盖 | 独立AU模块/容量8通道，生产者仅写非阻塞pipe，网络事件循环唯一owner，超限拒绝不丢P帧；Native/ARM及200帧门检通过 | 实时VPU慢客户端/整体争用仍待；[ADR_08](../../../ADR/ADR_08.md) |
| D11 | 不同encoded_id的P帧压缩字节可能相同，按唯一NAL哈希建立参考失败 | 首IDR定位、连续帧序号/实际PTS和逐帧VCL比较，再解码10bit ID与原像素独立确认 | 493参考AU/200网络解码通过；不能仅由单NAL哈希判定来源；[结果](../../../tools/pose-v1/OWNED-AU-RESULTS-20261008.md) |
| D12 | PowerShell属性集合.Count并非集合元素总数；旧OpenCV环境为Python3.8，缺removeprefix/is_relative_to；SDP探测临时source额外计数 | 使用显式数组计数、兼容3.8的前缀/父目录检查，分别核验0号SDP无AU及1/2实际流和三次释放 | 本机预检/审查错误原目录保留，无硬件重跑；[本轮修正](../../../tools/pose-v1/evidence/owned-rtsp-20261008-r3/local-corrections.json) |
| D13 | 并发读取的sample时刻可能早于刚发布的Engine初始化/ready时刻，unsigned相减存在下溢风险 | 源码审查后r2增加当前时刻核验/先比较再相减；r1仅构建、未板测，数学/SDK协议不改 | 三窗真实在线生命周期通过；不将风险写为已观察故障 |
| D14 | 首轮27窗网络客户端过晚加入ID450，只收到40帧，虽28推理/490编码正确也无法覆盖来源 | 新外部runner就绪标记与同次工具启动，保持程序/包与门禁，新目录429帧/全部28来源通过；16秒正常对照91帧不足另改独立30秒控制223帧，不降低门禁 | 修正通过；[ADR_09](../../../ADR/ADR_09.md)，原失败完整保留 |
| D15 | AU队列上限不覆盖库内部TCP发送失败，正常网络通过不足以证明慢客户端停止 | 实际库确认500ms发送补偿/错误返回，独立guarded候选注册公共发送错误回调和每连接64KiB发送缓冲；负面拒绝及正常223帧对照通过 | 原r2未含该保护；[ADR_10](../../../ADR/ADR_10.md)，候选/正式集成门检分别记录 |
| D16 | TCP监听在Engine约29秒初始化后才建立；外部等待只捕获refused，1秒连接timeout提前退出，板端0输入/0前向 | 原失败111项/344NoInput及内核同保留；新外部65秒启动等待同时记录refused/timeout，已连接数据流失败不重连，程序/包/Host保持，新目录修正验证 | 验证中；[ADR_11](../../../ADR/ADR_11.md) |
| D17 | 工具启动主机进程的延迟可能越过板端5秒输入等待，27窗开始前便退出 | 保留111项/0输入/0前向/内核同失败；主机先PEER_ARMED，再板端LIVE_READY通过已有进程START放行，硬件预算保持 | 验证中；[ADR_11](../../../ADR/ADR_11.md)，与D14晚加入属于启动协调问题而非模型计算问题 |
| D18 | TCP27第六窗S12_48_349输出逐位回归失配；原比较先于保存，丢失实际错误结果 | 六输入/五完整正确前向/131项/内核同保留；新隔离适配层在原异常后存完整实际值再原样抛出，数学/SDK/门禁保持 | Native契约与构建通过，原因待验证；[ADR_12](../../../ADR/ADR_12.md) |

2026-10-08后续：先完整保存再原门检以及一次规整。保存缺口已以独立适配层补齐，32前向483,200FP32全部逐位旧参考、S12_48_349当前差异0，未复现旧失配/颠倒，D18根因仍未知。一次规整159.69498ms、普通高阶折算512KiB单位5→91，随后两个进程启动和984编码/864网络全来源/PTS/像素通过；D04本轮恢复有效但长期可靠性未证。27本机审查曾在SFTP未完成时提前报缺文件hash，待完成同数据核验通过，无板测重跑。详见[ADR_13](../../../ADR/ADR_13.md)、[结果](../../../tools/pose-v1/PRESAVED-RESULTS-20261008.md)。

新定位：[forward内部尖峰与有界负载扩展](../../../ADR/ADR_16.md)，隔离诊断已构建，Host/板测进行中；trace结果不混入低日志验收。

r1已定位到inv3 GatherElements192两输入复制后的索引拒绝；未保存失败输入，根因待证。Host/三窗正确，原inv28尖峰未到；[失败与接续](../../../tools/pose-v1/FORWARD-TRACE-RESULTS-20261008.md)。

最新：[周期性数据块异常](../../../ADR/ADR_17.md)：180值有96个按128/256字节区间变为95零与1NaN、84旧参考一致；纯计时关闭仍发生，源设备未读回，不归因于微小定点误差或单一readiness查询。

r4两轮源读回已实现，Host及有限全链通过；坏值未复现、设备源异常读回未触发，旧数据块难点仍待。控制5秒窗口与RTSP首URI404独立处理，不混作数据修复：[结果](../../../tools/pose-v1/SOURCE-READBACK-R4-RESULTS-20261009.md)。
