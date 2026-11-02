# 比赛开发资料索引与理解记录

**当前依据（2026-11-01）：** 当前硬件分工、源与接口见[架构说明](ADR/TechDetails.md)；厂商IP／网表／增量基线和外部工具范围见[源码说明](Deliverables/SOURCE-20261031.md)；r4 RAR独立完整实现、原生时序／DRC及配置载荷比对见[重建报告](Deliverables/FPGA-REBUILD-20261101-r1.md)。最后设备观察见[RESUME](FPGA/hdmi_candidate/RESUME.md)，历史附件可用范围见[导航](DOCUMENTATION.md#引用与归档)。

## 历史资料阅读与阶段记录

**文档职责（2026-10-29）：** 本页保存资料阅读与历史理解，不用来判断当前交付或批准新任务。最终进度见 [PROJECT-PROGRESS](PROJECT-PROGRESS.md)，全量导航和遗留附件说明见 [DOCUMENTATION](DOCUMENTATION.md#引用与归档)。文中的旧工具选择、预算和计划按日期理解；部分历史本地附件已不在当前工作区。

2026-10-24 HDMI现行入口：[结构/源码](FPGA/hdmi_candidate/INTEGRATION.md)、[最后恢复状态](FPGA/hdmi_candidate/RESUME.md)、[本轮实测及首读原值](tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/RESULTS.md)。官方PSOC GP/HP经验总结及其与当前器件的适用边界见[资料判读](FPGA/hdmi_candidate/diagnostics/PROTOCOL-CHECKER-REVIEW-20261023.md)；以下“当前/尚未”按原日期作为历史资料，不覆盖上述入口。

2026-10-25独立采集入口：[Nexmon状态与实机结果](tools/nexmon/README.md)、[四机1发3收报告](tools/nexmon/evidence/multirx-20261025-r1/REPORT.md)、[无PC板端软件候选](tools/nexmon/board/README.md)。10月17日[本地构建与离线证据](tools/nexmon/evidence/preparation-20261017-r1/REPORT.md)、[芯片调查](tools/csi-planning/RT-AC86U-NEXMON-AUDIT-20261017.md)及[到货部署方案](tools/nexmon/DEPLOYMENT-PLAN.md)保留历史范围，不覆盖四机现状。独立180-query模型的转换、数值及压测边界见[部署实测](tools/pose180/deploy/RESULTS.md)。现行执行边界见[项目总览](PROJECT-PROGRESS.md)；下文早期“尚未核验”等描述按原日期理解。

## HDMI资料入口（2026-10-18历史，现行状态见文首）

[INTEGRATION.md](FPGA/hdmi_candidate/INTEGRATION.md)维护模块分工、CSR／帧契约、时钟／TMDS、工具适配及阶段结果；[显示应用](software/hdmi_demo/README.md)维护PS渲染与同Device生命周期。[难点索引](DIFFICULTIES.md)记录D05及D42–D45，近期原值与安全回退见[暂停汇报](FPGA/hdmi_candidate/STARTUP-PAUSE-REPORT-20261018.md)。r13三窗新推理→HDMI已通过，D45启动稳定性未解决，开发与上板整体暂停；本任务不接入Vivado MCP。

原厂引脚依据见[PIN-CONTRACT](FPGA/hdmi_candidate/PIN-CONTRACT.md)，2018.3／030ai与JFM职责见[路径二实施配置](FPGA/hdmi_candidate/ROUTE2-BUILD-PLAN.md)，r9身份与有限时序例外见[候选规格](FPGA/hdmi_candidate/CANDIDATE-BOARD-READ-R9.md)。它们分别是资料、历史计划或已关闭执行包，不能据其旧“下一步”自动启动任务。所有数值／时序及BOOT保护继续按Agents现行规则。

## r9首次实板执行记录（历史，后续r13已通过）

2026-10-18，r9执行包实际完成有界执行。候选安装／启动一次，SSH恢复34.344秒后先还原原BOOT并完整核验；64B DMA全字节往返通过，4KiB写在5.191秒触发SDK内部5000ms超时，child exit71。按失败停止规则，64KiB／1MiB、三窗新推理和HDMI START均未执行，没有重试失败负载。已用本包唯一原BOOT回退，SSH恢复28.688秒；运行中与启动文件均回到原BOOT，六SDK／九启动文件符合、FPGA operating、owner为空，串口均关闭。候选／回退额度均为0，本地及板端本包授权已关闭，旧DATA仍暂停。当时D45与新推理→HDMI尚未解决；后续三窗闭环已在r13通过，D45仍未解决。

104字真实快照已验证：观测窗口约5.064秒，HC2接受9笔AR而R握手0；共享HP2对PS出口接受8笔AR、R握手2后持续背压；HDMI入口AR握手0、RVALID且RREADY=0覆盖整个窗口。ARM后未记录复位异常。疑点收敛到HP2共享返回通道及其初始化／分发状态，但没有逐事务台账或ARM前历史，不能唯一断定错路由、ID丢失或复位原因。实际发布DCP只读检查确认S00接HC2、S01接HDMI、6位PS RID进入返回流水线，未发现直接错线或显然ID截断；这不证明互联运行正确。 仍在位的r9证据目录（本机留存，仓库未附：`tools/pose-v1/evidence/hdmi-live-20261018-r9`）。本轮不接入Vivado MCP；原厂资料、固定保护及旧DATA边界保持。

## 此前阶段资料（保留当时结果，当前入口见上）

2026-10-16当前结果：本机安装的D:/vivado18.3/Vivado/2018.3已按新授权就地打原版030ai补丁；未复制完整工具。34文件/63,130,403字节备份SHA通过，九项最终目标匹配厂商源，其余备份文件未变。真实扩展PS的RTL展开29.826517秒、综合22.396529秒，工具均exit0；全部4527个命名连接/3868个AI连接可绑定，实际EDIF/DCP已生成。Liberty总数断言失败保留，独立核对证实运行库/实例7212位引脚一致，仅调试元数据表示差异及未调用DEBUGDATA160。通用转换后Procise导入3.833887秒exit1，PCPU7端口不匹配，已停止未重跑。本地JFM确有Vivado实现hook＋可选Procise位流后处理，尚未采用；其HARC、速度和DRC影响需讨论。 本批证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-vivado2018-20261016-r2/REPORT.md`）、[后续实现路径](FPGA/hdmi_candidate/JFM-FLOW-REVIEW.md)。当前180秒阶段授权已实际执行，取消完整工具副本方案；原生导入失败后停止实现。以下较早状态保留当时范围。

2026-10-15历史版本路线：人工确认官方资料已全部本地保存且无2019.1配套，要求先评估迁移、不可行再下载2018.3。实际2019.1运行库PS7的3305个位引脚与安装Liberty一致；030ai配套有7213个位引脚，工程使用的3868个AI_端口在现运行库全部缺失、在配套Liberty全部存在。九项替换源有八项受保护，现有资料不能形成可验证的完整2019.1迁移；普通RTL/IP成果保持。2018.3官方下载入口已打开但网页返回会话未建立，尚未取得安装包；未安装或替换库，原生PCPU7适配仍需独立门检。 本批证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-jfm-compatibility-20261015-r1/REPORT.md`）、[具体方案](FPGA/hdmi_candidate/VIVADO-VERSION-PLAN.md)。下述较早建议保留其当时范围，不再以继续寻找2019.1包为当前恢复任务。

2026-10-15本机资料补查：进一步核对真实replace_7z030ai_file：严格限2018.3，先恢复多器件库再替换9项Vivado原语/器件文件；当前2019.1工程内只读入单文件仍报AI_IN端口不匹配，未改全局库或绕过版本检查。原理图确认AC14/100MHz、TMDS差分对，以及F8=1.5V/高有效PL_KEY2；IO直驱1080p60不可保证的限制保持。PS构建仍阻塞，未下载候选。 JFM与引脚补查（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-jfm-pin-review-20261015-r1/REPORT.md`）、[Lite引脚契约](FPGA/hdmi_candidate/PIN-CONTRACT.md)、[真实JFM过程与版本边界](FPGA/hdmi_candidate/JFM-COMPATIBILITY-REVIEW.md)。原PDF第9/10/19/21/22页已渲染目视核验，图纸Sheet号与PDF页码分开记录。

2026-10-15 HDMI已获实板、隔离同配置重建、16根IP修订白名单及有限衍生字段例外授权。实板只读身份/12寄存器核验通过，BOOT/六份SDK/内核同；新r3有限契约门检、97.600秒IP生成及28项原有HDL参数/生成端口后检通过。实际生成AXI3互联两入口全32个ID、64读/64写完整16拍burst及背压通过，Procise原生互联综合16.417秒exit0；纯输出OBUFDS→ODU_DS真实引脚布线兼容探针通过。完整系统当前受阻于自定义PS7扩展端口与Procise PCPU7声明不匹配，PS门检8.418秒exit1，已停止。尚无完整候选位流，未下载、未改BOOT或重启，实屏仍待验；旧DATA继续暂停。 本批总报告（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-bringup-20261015-r1/REPORT.md`）、生成/后检（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-ip-generation-20261015-r3/REPORT.md`）、[PS阻塞与恢复入口](FPGA/hdmi_candidate/PS-ADAPTATION-STATUS.md)。

以下各日期/批次保留原执行范围，旧“暂不上板”不覆盖最新实板授权。

2026-10-15 HDMI：阶段验收接受r5像素内核结果及4KiB/FIFO成果；新r6 core/r7 pixel全阶段exit0，仿真分别11.540/30.102秒，均未超90秒。隔离uihdmitx.v两处时钟输入已改10'b1111100000，Lite 7FAMILY新旧模型各128周期验证20%→50%占空比通过。原r5超时及非目标UFAMILY精确边沿诊断失败保留。PS/DDR/TMDS原生物理集成、CDC/实现时序及实屏待验，暂不上板、不换BOOT。 本批报告（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-split-20261015-r1/REPORT.md`）、[候选状态](FPGA/hdmi_candidate/RESUME.md)。旧DATA继续暂停。

2026-10-15 HDMI新核验：本地Lite BOOT/bit与选用版相同；实板显示控制0x20230218及12寄存器读取过，BOOT/六份SDK库/内核前后一致。参考RTL行为仿真确认200MHz扫描80.81Hz、停消费可卡读帧及AXI在RREADY=0时提前完成缺陷；后者不代表当前BOOT故障已证。显示器已接仍报时序不支持，误点稳定画面作废。隔离候选修正独立时钟/AXI/停止换帧，先仿真和Procise构建，暂不上板。 执行、原值和限制（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-contract-validation-20261015-r1/REPORT.md`）。

2026-10-15 HDMI已先归档[完整讨论（冻结快照）](tools/pose-v1/evidence/architecture-output-20261017-r1/before-document-edit/ARCHITECTURE-DISCUSSION-20261015.md)，再一次板端只读核验：BOOT/三份SDK核心库同、FPGA operating；无DRM/fb/I²C适配器，clk_summary不能观测HDMI像素/PLL。参考RTL显示门控可能令读FIFO不再消费，不能等一帧即释放；当前发布位流时钟与停止契约待补，色条未启动。执行/原值/停止门槛（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-stage1-20261015-r2/REPORT.md`）。未改BOOT/SDK/模型，无MMIO、设备初始化或后台，旧DATA暂停。

2026-10-15共享新包稳定性已完成：原编译包三窗、30秒/1131次及30分钟/62,945次实板串行推理的数值/内存观察通过，完整实际输入/输出回传后SHA及现行门禁独立复核通过。暖机后RSS75204→73628KiB、PSS73887→71779KiB，Private_Dirty/VmData不增，FD13/线程3/映射86保持；Engine均值23.278220ms，含保存/比较速率34.969次/秒。无崩溃/SDK异常/新增内核日志，但11次process超过1秒、最大4.158秒（forward4.151秒/进程CPU20.177ms），时延长尾原因未知，列D41，不称实时性通过。Engine正常销毁、本批进程和连接结束。r1可选/proc接口失败原样保留，r2兼容修复4项本机检查后新Session继续；归档SSH超时只监测/取回原归档，未重跑推理。模型/RAW/数学/CPU注册/NPU分配/SDK/BOOT不改，常规诊断限前三帧，异常证据路径保留。仅三个冻结输入，无视频/网络叠加，不能扩展为整机或任意输入绝对无泄漏保证。完整报告（历史附件，当前仓库未附：`tools/pose-v1/evidence/shared-stability-20261015-r2/REPORT.md`）。正式演示不换，旧DATA继续暂停。

2026-10-15现行共享图门禁v2：明确仅score>0.2候选检查3mm关节三维误差，背景保留误差诊断、完整分数/输入及所有候选有限性仍检。[ADR_48](ADR/ADR_48.md)记录新授权和阶段认可。21组自测/新ARM构建及原三份板端输出C++回放、独立NumPy复核通过，受检最大0.9765625mm；本次未新上板、不改旧exit1。完整记录及证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/shared-confidence-gate-20261015-r1/REPORT.md`）。FP16步长特征是事实，物理偏置/低分槽训练漂移原因尚未验证；旧DATA暂停。以下全候选规则为历史v1。

2026-10-15固定共享FP16候选最大关节三维偏差≤3mm，输入/分数仍逐位；例外范围与“物理偏置未验证”记录于[ADR_48](ADR/ADR_48.md)。独立门检12组自测/ARM构建通过，新Session三窗实际复验前两窗1.953125mm过、第三窗5.524271728mm超限exit1停止，无重试；三次Engine实测均值27.83871ms包含拒绝样本，不能称整组通过。政策、实际结果与完整原值（历史附件，当前仓库未附：`tools/pose-v1/evidence/shared-gate-policy-20261015-r1/REPORT.md`）。旧逐位失败保留，正式演示未替换，旧DATA暂停。以下阶段描述保留当时范围。

2026-10-15共享细化完整图已从服务器回传exportONNX/shared-refine-20261015-r1，Icraft3.39.0五阶段exit0，TOML/五对JSON-RAW保留model/piw24_shared-20261015-r1。29样本FP32导出通过；新1021 HardOp板图首帧Engine24.19628ms，但78/4200姿态坐标失配、最大关节差1.953125mm，严格停止，余两帧未跑，不能称板端数值或稳定性能通过。完整报告、计时与失败证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/shared-graph-board-20261015-r1/REPORT.md`）。正式演示未替换、旧DATA暂停。以下“尚无共享图”仅属当时历史。

2026-10-15去ScatterND图实际Lite验证：独立引擎1158 HardOp完整融合五组/最终736，三窗全部输出逐位原板端参考。Engine184.163ms；forward16.010ms后末端仍等待157.975ms，不是16ms完整推理。新JSON/RAW/ARM包、源码、原始时间线、GT指标和回收证据见板测报告（历史附件，当前仓库未附：`tools/pose-v1/evidence/noscatter-board-20261015-r1/REPORT.md`）。正式演示未替换、尚无共享细化板图，旧DATA保持暂停。以下14日“待板测”为当日历史范围。

2026-10-14主机Icraft3.39.0新完整去ScatterND图五阶段转换完成，实际TOML/五对JSON-RAW留model/piw24_noscatter-20261014-r3；1158 HardOp/四Host/ScatterND0，736仅静态计数，旧Engine/模型未换、新图板测及量化数值待验：配置、原失败与产物（历史附件，当前仓库未附：`tools/pose-v1/evidence/icraft-no-scatter-20261014-r1/README.md`）。

2026-10-13当前源码：[正式核心导读](software/core/README.md)、[重构ADR_47](ADR/ADR_47.md)、本机/CPU107/三窗口实际证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/core-refactor-20261013-r1/README.md`）。旧源码、协议、SDK及模型保持；以下历史阶段结果保留各自范围，旧DATA排查仍暂停。

最新：[全项目技术细节](ADR/TechDetails.md)、[演示运行说明](software/demo/README.md)、[ADR_45](ADR/ADR_45.md)、[63窗口板测/视频结果](tools/pose-v1/DEMO-RESULTS-20261011.md)、完成核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/demo-20261011-r4/completion-review.json`）。原坏读排查暂停，演示完成；57份额外姿态非完整精度验收，HDMI未接。以下当前为历史。

最新证据：[目录预建/首次与晚源结果](tools/pose-v1/PRODUCER-PREPARED-RESULTS-20261011.md)、[ADR_44](ADR/ADR_44.md)、失败指纹（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-prepared-20261011-r1/on.fingerprint-review.json`）、完成（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-prepared-20261011-r1/completion-review.json`）。首次DATA96与四正确晚源、原文件不修补，根因未修。

2026-10-11最新：[ADR_43](ADR/ADR_43.md)记录源租约/Host188160字节read过、153前向正确、有VPUinv49目录等待915.86ms且准备截止成功拦截，物理晚源read未触发／根因未修；[结果](tools/pose-v1/PRODUCER-SOURCE-READ-RESULTS-20261011.md)／[下一目录预备](tools/pose-v1/PRODUCER-SOURCE-READ-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-source-read-20261011-r2/next-checkpoint.json`）。221 NoInput视频前缀/abort清理过，所有连接结束，原异常读取保持，下一未执行，以下当前为历史。

2026-10-11最新：[ADR_42](ADR/ADR_42.md)记录高地址SDK前缀控制、四调用/off100通过、on inv49 DATA800逐位前帧A的独立更小失配；首次输出已错但无晚源证据，责任未证。214 NoInput视频前缀/abort清理过，全部连接结束；[结果](tools/pose-v1/PRODUCER-ADDRESS-RESULTS-20261011.md)／[下一失败只读租约](tools/pose-v1/PRODUCER-ADDRESS-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-address-20261011-r2/next-checkpoint.json`）。下一未执行、原正式异常读取保留，以下当前为历史。

2026-10-11最新：[ADR_41](ADR/ADR_41.md)归档reset前分段／准备后绝对时隙、off/on各100及307 NoInput视频正常回收。2352000 FP32逐位，旧1.764秒尖峰未复现，保存区间等待已观察但底层原因未证，正式坏读未修；[结果](tools/pose-v1/PRODUCER-PHASE-RESULTS-20261011.md)／[下一公开高地址可行性](tools/pose-v1/PRODUCER-PHASE-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-phase-20261011-r2/next-checkpoint.json`）。原异常读取保持、下一未执行、程序连接全结束，以下当前为历史。

2026-10-11最新：[ADR_40](ADR/ADR_40.md)记录同身份off100通过、on82数值正确后时隙失败及reset前1.764秒空档，正式根因未修。271packet／270 NoInput图像／162复制交叠、异常清理通过，正常drain-LAST未过；[结果](tools/pose-v1/PRODUCER-VPU-RESULTS-20261011.md)／[下一分段观察](tools/pose-v1/PRODUCER-VPU-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-vpu-20261011-r2/next-checkpoint.json`）。原异常读取保留，下一未执行，全部程序连接结束，以下当前为历史。

2026-10-11最新：[ADR_39](ADR/ADR_39.md)记录独立19成员物理部署／四调用、mock无数据搬运的门检修正与locale只读核验。47040 FP32／0→11／释放通过，正式并发根因未修；[结果](tools/pose-v1/PRODUCER-GROUP-RESULTS-20261011.md)／[下一有无VPU对照](tools/pose-v1/PRODUCER-GROUP-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-group-20261011-r2/next-checkpoint.json`）。100调用未实施，原异常读取保持，以下当前为历史。

2026-10-11最新：[ADR_38](ADR/ADR_38.md)记录真实参数／19来源映射／受限FP16-TF32参考及mock独立0→11。数学参考已闭合，物理读取根因未修；[结果](tools/pose-v1/PRODUCER-REFERENCE-RESULTS-20261011.md)／[下一](tools/pose-v1/PRODUCER-REFERENCE-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-reference-20261011-r2/next-checkpoint.json`）。无新物理前向／并发通过，全部程序和连接结束，以下当前为历史。

2026-10-11最新：[ADR_37](ADR/ADR_37.md)记录生产者检查器条件copy、零指令Cast、19成员参考缺口、官方部署映射与日志门检/误检索修正。[结果](tools/pose-v1/PRODUCER-CONTRACT-RESULTS-20261011.md)／[下一](tools/pose-v1/PRODUCER-CONTRACT-NEXT-20261011.md)／数据核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-contract-20261011-r2/data-review.json`）／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-contract-20261011-r2/next-checkpoint.json`）。无模型前向，新根因未修；r3 exit1为一/两日志数量错误，原码/数据保留，r4仅编译。全部会话结束，以下当前为历史。

2026-10-11最新：[ADR_36](ADR/ADR_36.md)匹配AXI／UDMA责任审查及两方法／四条件内存对照完成；400动态对过，无NPU生产，原模型根因未修。锁／轮询／cache同步存在但生产完成未知。[结果](tools/pose-v1/AXI-READ-RESULTS-20261011.md)／[责任证据入口](tools/pose-v1/AXI-READ-RESPONSIBILITY-20261011.md)／[下一](tools/pose-v1/AXI-READ-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`tools/pose-v1/evidence/axi-pair-20261011-r4/next-checkpoint.json`）。本批已结束、无规整／后台；以下当前为历史。

2026-10-11最新：[首次read／CPU前快照结果](tools/pose-v1/READ-PHASE-RESULTS-20261011.md)／[ADR_35](ADR/ADR_35.md)／完成身份与证据绑定（历史附件，当前仓库未附：`tools/pose-v1/evidence/read-phase-20261011-r3/completion-review.json`）／592同偏移坏值与时序核对（历史附件，当前仓库未附：`tools/pose-v1/evidence/read-phase-20261011-r3/failure-review.json`）／[下一AXI／UDMA审计](tools/pose-v1/READ-PHASE-NEXT-20261011.md)／恢复入口（历史附件，当前仓库未附：`tools/pose-v1/evidence/read-phase-20261011-r3/next-checkpoint.json`）。四窗通过、唯一高负载异常停止，Root未修，以下当前为历史。

2026-10-11最新：[公开Gather／ZG边界结果](tools/pose-v1/UPSTREAM-BOUNDARY-RESULTS-20261011.md)／[ADR_34](ADR/ADR_34.md)／完成身份与证据绑定（历史附件，当前仓库未附：`tools/pose-v1/evidence/upstream-boundary-20261011-r4/completion-review.json`）／192独立失败核对（历史附件，当前仓库未附：`tools/pose-v1/evidence/upstream-boundary-20261011-r4/failure-review.json`）／[下一首次read方案](tools/pose-v1/UPSTREAM-BOUNDARY-NEXT-20261011.md)／恢复入口（历史附件，当前仓库未附：`tools/pose-v1/evidence/upstream-boundary-20261011-r4/next-checkpoint.json`）。Host／四窗过、高负载早期192异常停止；两晚源正确不证明读路径责任。以下当前为历史。

2026-10-10最新：[完整保存与晚源结果](tools/pose-v1/FINAL-EVIDENCE-RESULTS-20261010.md)／[ADR_33](ADR/ADR_33.md)／[下一边界方案](tools/pose-v1/FINAL-EVIDENCE-NEXT-20261010.md)／当前恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/final-evidence-20261010-r2/next-checkpoint.json`）。保存缺口已解决，582上游数据异常未解决；本批已停止、无后台，严格5Hz/长期/HDMI保持待验。以下最新为历史。

2026-10-10当前：[组合结果](tools/pose-v1/COMBINED-READ-RESULTS-20261010.md)／[ADR_31](ADR/ADR_31.md)／[ADR_32](ADR/ADR_32.md)／[ADR_33](ADR/ADR_33.md)／完成/失败核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/combined-read-20261010-r1/completion-review.json`）／新恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/combined-read-20261010-r1/next-checkpoint.json`）。 以下当前为历史。

2026-10-10当前：[公开read结果](tools/pose-v1/INPUT-READ-RESULTS-20261010.md)／[ADR_30](ADR/ADR_30.md)／完成证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/input-read-20261010-r1/completion-review.json`）／恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/input-read-20261010-r1/next-checkpoint.json`）／[下一组合方案](tools/pose-v1/INPUT-READ-NEXT-20261010.md)。107真实画面有限通过，底层根因与长期未证；以下当前索引为历史。

2026-10-10当前：[无视频真实模型结果](tools/pose-v1/MODEL-ONLY-RESULTS-20261010.md)／[ADR_26](ADR/ADR_26.md)／完成证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/model-only-20261010-r1/completion-review.json`）／恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/model-only-20261010-r1/next-checkpoint.json`）／[下一同身份VPU单因素方案](tools/pose-v1/MODEL-ONLY-NEXT-20261010.md)。107完整前向正确，旧根因未修，以下当前为历史。

2026-10-10当前：[公开管理器与源位置结果](tools/pose-v1/PLDDR-POSITION-RESULTS-20261010.md)／[ADR_25](ADR/ADR_25.md)／公开审计（历史附件，当前仓库未附：`tools/pose-v1/evidence/plddr-position-20261010-r1/manager.acceptance.json`）／完成证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/plddr-position-20261010-r1/completion-review.json`）／恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/plddr-position-20261010-r1/next-checkpoint.json`）／[下一无视频真实引擎对照](tools/pose-v1/PLDDR-POSITION-NEXT-20261010.md)。两独立100对、227图像过，不是模型根因修复。以下当前为历史。

2026-10-10当前：[真实类型／动态对照结果](tools/pose-v1/TYPED-SCRATCH-RESULTS-20261010.md)／[ADR_24](ADR/ADR_24.md)／[下一源位置方案](tools/pose-v1/TYPED-SCRATCH-NEXT-20261010.md)／完成审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/typed-scratch-20261010-r1/completion-review.json`）／恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/typed-scratch-20261010-r1/next-checkpoint.json`）。三独立100对和226图像过，原Host身份复用，模型未新运行／根因未修，旧坏块／SDK审计保持。以下当前为历史。

2026-10-10当前：[模型对象取证结果](tools/pose-v1/TENSOR-IDENTITY-RESULTS-20261010.md)／[ADR_23](ADR/ADR_23.md)／[下一受控类型与动态写入方案](tools/pose-v1/TENSOR-IDENTITY-NEXT-20261010.md)／完成审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/tensor-identity-20261010-r3/completion-review.json`）／恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/tensor-identity-20261010-r3/next-checkpoint.json`）。新Host／三窗通过，inv72的192仍异常；对象和范围稳定、晚源正确，根因未修。以下当前为历史。

2026-10-10当前：[受控SDK搬运结果](tools/pose-v1/SCRATCH-COPY-RESULTS-20261010.md)／[ADR_22](ADR/ADR_22.md)／[对象身份下一方案](tools/pose-v1/SCRATCH-COPY-NEXT-20261010.md)／完成审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/scratch-copy-20261010-r3/completion-review.json`）／恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/scratch-copy-20261010-r3/next-checkpoint.json`）。原Host107明确复用，新Native／ARM／搬运／编码并发实测；模型未执行、故障未修，旧匹配SDK／DMA／UDMA审计和坏块证据保持。

2026-10-09当前：[192计数诊断结果](tools/pose-v1/PRODUCER-COUNT-RESULTS-20261009.md)、[受控SDK双源搬运设计](tools/pose-v1/PRODUCER-COUNT-NEXT-20261009.md)、[ADR_21](ADR/ADR_21.md)、完成审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-count-20261009-r2/completion-review.json`）、实际失败计数（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-count-20261009-r2/failed.counter.json`）、新恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/producer-count-20261009-r2/next-checkpoint.json`）。旧异常和SDK匹配审计保持。

2026-10-09当前恢复：[单帧取证接入结果](tools/pose-v1/INVOCATION-GUARD-RESULTS-20261009.md)、[192完成与搬运定位方案](tools/pose-v1/INVOCATION-GUARD-NEXT-20261009.md)、完成审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/invocation-guard-20261009-r1/completion-review.json`）、当前检查点（历史附件，当前仓库未附：`tools/pose-v1/evidence/invocation-guard-20261009-r1/next-checkpoint.json`）、坏段字节模式（历史附件，当前仓库未附：`tools/pose-v1/evidence/invocation-guard-20261009-r1/bad-block-pattern-r2.json`）。原有限输出和晚源证据不覆盖；SDK／映射资料继续适用。

2026-10-09最新：[结果](tools/pose-v1/STARTUP-GUARD-RESULTS-20261009.md)／[ADR_20](ADR/ADR_20.md)／[接入契约](tools/pose-v1/INVOCATION-EVIDENCE-INTEGRATION-NEXT-20261009.md)／恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/startup-guard-20261009-r1/next-checkpoint.json`）；[SDK搬运/映射审计](tools/pose-v1/SDK-MAPPING-AUDIT-20261009.md)。第一轮通过、第二轮有限姿态失配、第三轮停止；异常完整结果保留，元数据缺口明确记录，独立模块已验证未集成。以下状态作为历史。

2026-10-09最新：[Host快照/582完成检查结果](tools/pose-v1/STAGE-GUARD-RESULTS-20261009.md)、[执行契约](tools/pose-v1/STAGE-GUARD-PLAN-20261009.md)、[ADR_19](ADR/ADR_19.md)、完成审查及恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/stage-guard-20261009-r1/next-checkpoint.json`）。Host/三窗/103全值视频通过，107次新查询首次638无额外等待，旧故障根因仍未证；短期有界5Hz门限达到，不外推长期。此前“最新”按历史读取。

2026-10-09最新：[103实施与失败/真实源结果](tools/pose-v1/BOUNDED-LOAD-RESULTS-20261009.md)、[执行方案](tools/pose-v1/BOUNDED-LOAD-PLAN-20261009.md)、[下一Host shadow准备](tools/pose-v1/HOST-STAGING-FAULT-NEXT-20261009.md)、[ADR_18](ADR/ADR_18.md)、[ADR_17](ADR/ADR_17.md)、恢复检查点（历史附件，当前仓库未附：`tools/pose-v1/evidence/bounded-load-20261009-r2/next-checkpoint.json`）。Host及三窗全链通过，103在第61次拒绝NaN后停止；两轮真实源正确但原暂存0异常，不提前宣布根因/性能修复。

2026-10-09最新：[保留异常读取后的覆盖/纯计时结果](tools/pose-v1/SOURCE-COVERAGE-RESULTS-20261009.md)、完成与恢复入口（历史附件，当前仓库未附：`tools/pose-v1/evidence/source-coverage-20261009-r4/next-checkpoint.json`）、[有限执行方案](tools/pose-v1/SOURCE-COVERAGE-PLAN-20261009.md)、[ADR_16](ADR/ADR_16.md)、[ADR_17](ADR/ADR_17.md)。66正确前向/997编码937网络，旧故障未复现，诊断不作5Hz验收；下面此前“最新”保留为历史。

2026-10-08最新：[独立显示子进程可行性](tools/pose-v1/DISPLAY-PROCESS-RESULTS-20261008.md)、[尖峰/有界入口下一方案](tools/pose-v1/DISPLAY-PROCESS-NEXT-20261008.md)、[ADR_15](ADR/ADR_15.md)。70正确全链，5Hz输入33全消费，实测4.99165Hz不舍入验收；83/100保持，后续此前状态是历史。

2026-10-08最新实测：[整机低日志/2Hz/5Hz结果](tools/pose-v1/SYSTEM-TIMING-RESULTS-20261008.md)、[最小显示worker方案](tools/pose-v1/SYSTEM-TIMING-NEXT-20261008.md)、[ADR_14](ADR/ADR_14.md)。实际4.22311Hz未达标，数值/视频正确；管理83/100保持。下方此前“推进前”记录为历史。

2026-10-08推进前审阅：[当前进度、剩余难点与后续方案](tools/pose-v1/PROJECT-STATUS-AND-NEXT-20261008.md)。有限TCP全链已通过，下一建议独立低日志整机计量；当前仅核对文档，没有新执行，管理83/100保持。

2026-10-08最新：[保存优先＋一次规整/32全链](tools/pose-v1/PRESAVED-RESULTS-20261008.md)、完成审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/tcp-presaved-20261008-r1/completion-review.json`）、检查点（历史附件，当前仓库未附：`tools/pose-v1/evidence/tcp-presaved-20261008-r1/next-checkpoint.json`）、[ADR_13](ADR/ADR_13.md)。旧失配未复现，不证明截断原因；永久CMA/长期/性能/HDMI未验。

2026-10-08当前：[guarded/TCP结果及两类停止](tools/pose-v1/TCP-INTEGRATION-RESULTS-20261008.md)、检查点（历史附件，当前仓库未附：`tools/pose-v1/evidence/tcp-evidence-20261008-r1/next-checkpoint.json`）、[恢复计划](tools/pose-v1/TCP-RECOVERY-NEXT-20261008.md)、[启动ADR_11](ADR/ADR_11.md)、[输出失配ADR_12](ADR/ADR_12.md)。guarded32与TCP三窗通过，27失配未解决；新捕获Host107通过而VPU普通连续页失败，未规整/重启，不推进性能。

2026-10-08启动与有限常驻：[独立ADR_02](ADR/ADR_02.md)、[难点索引](DIFFICULTIES.md)、[实际模块/分配/三启动](tools/pose-v1/VPU-STARTUP-RESULTS-20261008.md)、[32前向/987视频/主线程对照](tools/pose-v1/RESIDENT-RESULTS-20261008.md)、当前核验与检查点（历史附件，当前仓库未附：`tools/pose-v1/evidence/resident-20261008-r6/completion-review.json`）。不扩大CMA、不泛称SDK线程限制；在线RTSP/HDMI/长期另列。

2026-10-08 F0：[有限合并/新视频/失败与规整诊断](tools/pose-v1/PIPELINE-RESULTS-20261008.md)、完整核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/pipeline-20261008-r6/completion-review.json`）、[接续分配取证与常驻方案](tools/pose-v1/PIPELINE-NEXT-20261008.md)。两有限成功不等于启动稳定/实时闭环；Linux连续分配及compact_memory官方依据见报告，不将一次诊断变生产策略。

2026-10-07RTSP当前：[结果/样片](tools/pose-v1/RTSP-RESULTS-20261007.md)、200帧/重连（历史附件，当前仓库未附：`tools/pose-v1/evidence/rtsp-20261007-r3/completion-review.json`）、直接播放器100帧（历史附件，当前仓库未附：`tools/pose-v1/evidence/rtsp-20261007-r4-player/completion-review.json`）、SPS信号（历史附件，当前仓库未附：`tools/pose-v1/evidence/rtsp-20261007-r3/color-signal-review.json`）、[F0准备](tools/pose-v1/F0-INTEGRATION-PREP-20261007.md)。厂商live555/SSL原包复用无安装；已通过独立回放，不代表在线编码或整机闭环。

2026-10-07当前视频：[r5修正/动态MP4](tools/pose-v1/VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md)、两上下文及主机核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/video-descriptor-20261007-r5/completion-review.json`）、下一检查点（历史附件，当前仓库未附：`tools/pose-v1/evidence/video-descriptor-20261007-r5/next-checkpoint.json`）。QUERYBUF cookie保留解决当前有限编码问题；旧MMU/色彩拒绝保留，HDMI时序及RTSP/整机待验。

2026-10-07下一视频阶段：已审查样片并恢复HDMI测试授权，[新计划](tools/pose-v1/NEXT-VIDEO-PLAN-20261007.md)、授权/来源哈希检查点（历史附件，当前仓库未附：`tools/pose-v1/evidence/video-next-plan-20261007.json`）。参考HDMI类只分配RGB565缓存和提交地址，未配置时序；先建立当前BOOT配套，再1080p60实屏。旧暂停属历史，本轮无新板测。

2026-10-07独立VPU：[结果与主机MP4](tools/pose-v1/VPU-RESULTS-20261007.md)、[命令](tools/pose-v1/VPU-COMMANDS-20261007.md)、完整核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/vpu-20261007-r1/completion-review.json`）。实际两端MPLANE/NV12两plane/H264单plane、30帧与主机解码通过；V4L2初始化/独立队列/drain依据[Linux stateful encoder官方接口](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/dev-encoder.html)和本机厂商vpu.h Encoder/mvx-v4l2-controls.h，未使用相机MMU及固定SPS/PPS切片。HDMI新目标1080p60、暂停，硬件时序未改；RTSP与色彩/时戳仍待。

2026-10-07渲染与V0：[ARM画面/真实推理绘图结果](tools/pose-v1/RENDER-RESULTS-20261007.md)、[配套查询与差异](tools/pose-v1/V0-VIDEO-PAIRING-20261007.md)、完整核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/render-20261007-r1/completion-review.json`）。CPU渲染与三格式逐位通过；VPU仅MPLANE枚举，HDMI未接/配套未确认，编码/RTSP及整机性能仍待。

2026-10-07 E1首批：[生产接口/TCP完整实板结果](tools/pose-v1/APPLICATION-RESULTS-20261007.md)、独立核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/application-20261007-r2/completion-review.json`）、[命令与超时修正](tools/pose-v1/APPLICATION-COMMANDS-20261007.md)。38成功前向逐位此前板端，2Hz网络正确性通过；渲染/双路/整机吞吐及长期仍待。旧“接口/网络尚未实现”按历史理解。

2026-10-07首版取舍：[ADR_01当前异构方案与延期优化](ADR/ADR_01.md)、[全流程分阶段计划](tools/pose-v1/FULL-FLOW-PLAN-20261007.md)。人工确认先完成回放首版闭环，深度零拷贝/图/算子优化后置；本轮仅规划，E1及视频尚未实施，管理粗估保持。

2026-10-07最新：数值阶段验收（历史附件，当前仓库未附：`tools/pose-v1/evidence/perf-20261007-r3/user-numerical-acceptance.json`）、[P2定位与5.25Hz核心基线](tools/pose-v1/P2-RESULTS-20261007.md)。不含网络/绘图/编码，整机/长期与双路仍未验收；较早“数值待验收”属历史。

2026-10-07最新：[运行核心/27样本/性能结果](tools/pose-v1/RUNTIME-RESULTS-20261007.md)、[H0配套资料](tools/pose-v1/H0-INTEGRATION-AUDIT-20261007.md)、[N2/P2候选](tools/pose-v1/NEXT-GATE-20261007.md)。原批准E0/N1/P1已执行完成；数值容限及5Hz未通过，视频未操作。以下20261006暂停文字为历史，最新以此结果及STATUS.md为准。

2026-10-06进度/恢复入口：[全项目阶段与估算](PROJECT-PROGRESS.md)、[下一次唤醒](tools/pose-v1/RESUME-20261006.md)及当时的待办清单（现已撤下，追溯方式见[文档目录](DOCUMENTATION.md#撤下页面的阅读位置)）。暂停保持；r6已验收，新核心只编译通过、ORT27已生成而独立复核待完成，N1/P1板测和双路显示未完成。

当前首版入口（2026-10-06）：[跨帧修正与三样本混合工程结果](tools/pose-v1/MIXED-FRAME-STATE-R6-RESULTS.md)、
[三样本ONNX已完成参考](tools/pose-v1/ONNX-REFERENCE-RESULTS-20261006.md)，范围及证据见18.7。
以下较早基线/待批准文字为历史快照，最新状态以18.7和Done.md首节为准。

整理日期：2026-09-30（Asia/Shanghai）；同日补充 Lite 完整原理图；2026-10-01 补充开发/训练环境、Icraft 依赖诊断、流水灯实测及 Vivado MCP 状态；2026-10-02 补充换卡后的 SD 启动和串口登录现场确认；2026-10-03 补充根分区扩容验收、板端SSH/Icraft安装及Docker交叉编译环境进度。项目根目录：`D:\FPGACompetitionProject`。

本文件用于选题、架构设计、FPGA 开发、AI 部署、系统联调和比赛材料准备时查找依据。内容区分资料明确记载、结合源码得到的分析，以及尚未确认的事项；它不是已经通过上板验证的操作手册。遇到冲突时回到原始资料核对，并评估，不自行选定解释或技术路线。

## 1. 已确认的项目基线与阅读范围

### 1.1 人工确认的基线

| 项目 | 当前基线 | 确认情况 |
| --- | --- | --- |
| 硬件 | 悟净开发板 Lite（轻量版），FMQL30TAI / ZG330 平台 | 既定配置；不是完整版悟净，也不是 100TAI/BUYI 平台 |
| 下载链/上电 | Alinx 黑金下载器；无 SD 卡开机和连线上板测试已完成 | 现场反馈 Procise/Vivado 均可识别芯片；具体算法、Linux、DDR/AI 的成功不能由器件识别推导 |
| SD 启动/串口登录（最新） | 已更换 SD 卡并完成启动卡制作、上板验证；串口正常输出，可登录板载系统 | 现场确认，2026-10-02，见第15节；根分区/ext4扩容已于2026-10-03人工执行并以截图验收，见15.3；旧卡故障记录保留为历史；runtime/AI另行核验 |
| FPGA 工具 | `FMSH_Procise_2025.1.1_temp_202603201420_32494.exe` 安装的 Procise | 人工确认；安装目录 `C:\FudanMicro\Procise`；主程序 ProductVersion 为 `2025.1.1 temp` |
| Vivado 辅助工具/MCP | D:/vivado18.3/Vivado/2018.3/bin/vivado.bat，64-bit Build2405991；2019.1保留 | 当前030ai九项＋32项原厂IP库补丁；参考位流/Procise ICAP已生成，完整时序未通过；实际结果（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-jfm-build-20261016-r1/REPORT.md`） |
| AI 工具 | Icraft 3.39.0 | 人工确认；`C:\Icraft\CLI` 是指向 `C:\Icraft\CLI v3.39.0` 的符号链接；另有 `CustomOp_v3.39.0` |
| 主机↔Lite板端通信 | 网线直连，MobaXterm SSH开发/通信 | 人工确认已使用，2026-10-03；地址/账号未提供，未由代理连接测试，见第16节 |
| 板端 Icraft/CustomOp | 已从指定3.39.0安装包目录传输板端包并完成两者安装 | 本地onchip包control为arm64/3.39.0；实际板端已安装版本/路径尚无查询输出，见第16节 |
| 主机交叉编译环境 | Docker容器名 `FPAI`；已搭建并配置相关工具链 | 明确是容器名；镜像、编译器、sysroot及编译产物实板运行未核验，见第16节 |
| 本机开发环境 | Windows 10；另有双系统 Ubuntu | 记录说明；倾向方案 A，Procise/Icraft 保留在 Windows；Windows Icraft 独立依赖第一阶段已获批准并通过加载验证，见 I5 |
| 当前算法训练位置 | 远程 Ubuntu 服务器，文件目录挂载到本机 `Z:` | 记录说明；仅记录文件访问入口，尚未核验远程执行方式、服务器软件版本及本项目具体目录 |
| 板载镜像 | `icraft_v3_ubuntu20.04_aarch64_sd_image.bin` | 人工确认；位于下载区“板载Linux镜像”；不能据文件名推断镜像内已经安装的 runtime 版本 |
| 首版候选位流/AI_MATE | 已选Lite 25122301单路PLIN+pHDMI BOOT，板上哈希及运行版本0x25122301核验通过 | 见18.4；SDK混合推理、HDMI时序及双路功能仍未验收，不扩大为完整系统已通过 |
| 完整原理图 | `JFMQL30TAI_LITE.pdf`，28 页，见 B4 | 人工确认它是 30TAI 配套原理图；标题栏名称、原始图纸页码差异仍保留说明 |

安装包称为“驱动程序”时，需要区分：上述 Procise `.exe` 是开发软件安装包，JTAG 下载器驱动另有专门资料，二者不能混为一谈。

**平台执行原则：本项目 FPGA 开发与实现以复旦微 Procise 为目标。** Vivado 是可选的参考工程前端/IP 生成或仿真辅助；HDL/接口方法可以借鉴，器件、IP/原语、时序库、约束、位流与调试必须按复旦微平台适配。两套工具均能通过下载器识别芯片，不代表底层实现或位流互通。

**训练资料边界（明确补充，2026-10-01）**：`koala` 环境及其中训练的模型与本次比赛项目无关；当前算法训练在远程 Ubuntu 服务器进行。本次比赛的核心模型、采集格式和预处理规格仍按既有要求留待顶层架构讨论，不能从旧训练环境、服务器上未核验的文件或挂载盘名称推定。

### 1.2 资料位置

| 编号 | 位置 | 主要价值 |
| --- | --- | --- |
| R1 | [比赛说明](CompetitionDescription) | 总体通知、复旦微选题要求和评分维度，决定作品必须完成什么 |
| R2 | 开发板手册（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/开发板手册`） | Lite 硬件配置及完整原理图；接口、电平、封装引脚、启动、时钟和板卡限制 |
| R3 | 26嵌赛开发（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发`） | 30TAI 工具链教程、FPGA 工程、PS 示例、BOOT 组件、位流、迁移工具包 |
| R4 | Procise 文档（本机路径，仓库未附：`C:/FudanMicro/Procise/documents`） | 本机工具的流程、Tcl、约束、下载、调试、仿真和原语说明 |
| R5 | Icraft 3.39.0 文档首页（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/index.html`） | 模型编译、ZG330 量化、运行时、算子限制、调优与错误定位 |
| R6 | 外部下载资料（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料`） | 镜像、交叉编译容器、3.39.0 安装包、更新参考实现、报告模板和流水灯验证记录 |

本次建立了 PDF、DOCX、HTML 和示例的目录索引：补充原理图后共有 25 份内容不重复的 PDF（929 页，其中含 7 页扫描版通知），另读了 4 份 DOCX 的文字内容。对比赛文件、Lite 手册、30TAI 教程、FPAI_DEMO 说明进行了重点阅读，对扫描版通知和关键硬件图表进行了图像核对；新增原理图完成了 28 页内容定位，并重点核对了芯片 BANK/封装引脚、时钟、电源、GPIO、视频、GT、LED/按键与 XADC 电路。Procise 大型原语/HRDT 手册、Icraft 大量 API 页面按目录和开发问题定位阅读，并非逐项验证全部 API。示例阅读覆盖 README、构建配置、YAML、关键 RTL/C++、BIF、uEnv 和已有工具日志。

安装包、压缩包、镜像、网表、位流和第三方库按用途及可读取元数据归档，没有执行安装、刷写或重新构建。没有把“文件存在”“历史日志成功”写成“当前 Lite 板已经运行成功”。首次整理前根目录 `AGENTS.md` 为空，`ADR` 未见决策文件。

### 1.3 使用优先级

- **必读**：比赛通知、复旦微选题指南、Lite 手册及 B4 原理图中涉及所用接口的页面、30TAI 使用教程、FPAI_DEMO 说明，以及已选版本对应的 Icraft 文档。
- **开发时直接查**：Procise /约束/在线调试/下载手册，ZG330 量化与运行时文档，参考工程的源码和配置。
- **按需求查**：VPU 示例、通用迁移流程、原语、Modelzoo_utils API、BSP 工具、HRDT。
- **只作对照或历史依据**：完整版手册、其他芯片的迁移示例、未确定版本的预编译位流、完整版流水灯位流。

## 2. 比赛要求：决定方案和验收材料

### C1. 复旦微 FPGA 赛道选题指南（8 页，必读）

来源：[全国大学生嵌入式芯片与系统设计竞赛'2026FPGA赛道选题指南-复旦微.pdf](CompetitionDescription/全国大学生嵌入式芯片与系统设计竞赛'2026FPGA赛道选题指南-复旦微.pdf)。

关键定位：PDF 第 3–5 页为技术平台与 Lite 裁剪资源；第 5–6 页为任务要求和 FPGA 开发方向；第 6–7 页为评分标准；第 7–8 页为支持、成果与来源要求。

设计要求：

1. 围绕明确应用场景完成需求、架构、软硬件划分和数据流设计，说明 CPU、NPU、FPGA 各自承担什么任务及划分依据。
2. 至少部署一种 AI 算法到 30TAI，覆盖模型转换、量化/精度分析、仿真、上板推理和性能测试。
3. 至少完成一项 FPGA 开发，可以是接口、预处理、后处理、自定义硬算子、加速 IP 或实时控制。
4. 形成从输入、预处理、AI 推理到后处理、反馈和展示的系统闭环。
5. 提交可复现的工程、说明、测试数据，以及演示视频或现场实物演示。
6. 允许在选题、方案、实现等环节使用智能体和大模型，但应说明具体工具、使用环节和工作量占比，留存证据。

对开发的意义：只完成模型演示或独立 RTL 模块，尚不能覆盖上述要求。厂商提供的流水灯和加法器有助于验证工具链/接口，但作品还需要体现与应用有关的 FPGA 工作及其系统贡献。

评分关注场景价值、异构划分依据、部署精度、FPGA 功能/资源/时序/集成、长时间稳定性、可复现性能和答辩。原文没有给出各维度的数值权重，不能自行编造百分比。可选加速方向包括缩放、颜色转换、滤波、特征提取、检测阈值/NMS、分割后处理、数据压缩和协议解析等；它们是选题参考，不代表本项目已经选定。

建议从开发开始留存：原始模型与量化精度、软件与 FPGA 同等输入下的耗时、端到端延迟/FPS、PL 资源与时序报告、异常恢复及稳定性记录，以及 AI 辅助开发与人工审核记录。这是根据评分要求归纳的取证方式，不是新增比赛规则。

### C2. FPGA 创新设计赛道通知（第一轮，7 页，必读）

来源：[ff581b85-e214-4b8f-a044-3287f8825750.pdf](CompetitionDescription/ff581b85-e214-4b8f-a044-3287f8825750.pdf)。文件为扫描件，不能依赖普通文本搜索；已通过逐页图像阅读识别为《关于组织参加2026年全国大学生嵌入式芯片与系统设计竞赛——FPGA创新设计赛道的通知（第一轮）》。

- 第 3 页：每队不超过 3 名学生、2 名指导教师，每位学生仅参加 1 队；本科生组要求成员均为本科生，研究生组至少一名研究生；初赛提交报告及视频等材料，具体提交要求另行通知。
- 第 4 页：决赛期间安排 FPGA 基础编程设计能力考核，通过后取得决赛评奖资格；包括作品介绍、演示与专家提问。因此必须理解和能解释自己提交的 FPGA 设计。
- 第 5 页：通知发布日 2026-07-06；报名截止 2026-09-22 24 时；作品设计期为 2026 年 9 月至 11 月 4 日；作品提交时间为 **2026-11-04 18 时**；决赛计划 **2026-11-20 至 11-22**，地点为南京江北新区。
- 第 6 页：具体安排可能调整，以后续官方通知为准；列有设计文档及作品视频的发布/出版安排，准备提交素材时应核对对应要求。

以上是本地“第一轮”通知的记载，不等同于已确认的最新赛程。2026-09-30 访问[竞赛官网](https://www.socchina.net/)只取得赛道入口页，未检索到足以再次核实上述具体日期的后续通知；最终提交格式、后续通知和日程变动仍须核对。

### C3. 技术文档模板（提交材料参考）

来源：技术文档.docx（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/技术文档.docx`）。内容是作品报告模板，而非芯片技术手册。

结构为作品名称、摘要、作品概述、系统组成及功能、完成情况与性能、总结、参考文献。模板要求名称不出现学校等识别信息；摘要 800 字以内，功能/应用领域/技术特点各 400 字以内，性能/创新点/设计流程各 200 字以内，可扩展之处 300 字、心得 1000 字以内，参考文献不超过 20 篇。要求系统框图、输入输出标记、实物照片、软件界面和量化指标。

价值在于指导开发中提前收集架构、图表和实验素材。它来自下载区，未确认是否为本届 FPGA 赛道最终提交模板；最终格式不能仅凭此文件决定。

## 3. Lite 硬件：能力、限制与接口依据

### B1. Lite 硬件手册（32 页，硬件主依据）

来源：悟净开发板Lite（轻量版）硬件使用手册V1.0.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/开发板手册/悟净开发板Lite（轻量版）硬件使用手册V1.0.pdf`）。本节页码均指 PDF 文件页序；目录存在错页，应以正文页序定位。

| 主题 | 已读到的内容与开发意义 | PDF 页 |
| --- | --- | --- |
| 芯片/平台 | 手册称 JFMQL30TAI676H；四核 CPU 最高 1GHz，PL 约 125K 逻辑单元、400 DSP、9.3Mb BRAM；NPU 8TOPS INT8、4TFLOPS FP16/BF16、2TFLOPS TF32 | 4–9 |
| PS/PL 内存 | PS DDR3 1GB、32bit；PL DDR3 2GB、64bit。需要分别预算 Linux/应用内存和模型、权重、特征图、视频缓存 | 5、12–13 |
| 峰值与实际 | 上述算力和容量是平台规格；参考 AI_MATE、视频通路和自定义模块会占用 PL 资源，不能直接视作全部可用资源或实际模型速度 | 8；结合 D2 分析 |
| 启动 | JTAG、QSPI、SD 启动。MIO5/4/3 分别为 JTAG=000、QSPI=100、SD=110；MIO2=0 级联、1 独立 | 10–11 |
| 时钟 | PS 必须使用 50MHz，手册明确不能用 33.333MHz；有 PL 100MHz、DDR 外部差分 200MHz、MGT 148.5MHz 时钟源 | 14（含原理图片段） |
| 存储 | 单片 QSPI0 Flash 256Mbit，即 32MB；MicroSD 承载 BOOT、内核、文件系统及数据，板卡配置表列 32GB TF | 5、15、17–18 |
| JTAG/串口 | PS/PL 各有 20pin JTAG；PS USB UART 用 CP2103GM，MIO50/51 | 15、18 |
| 以太网/USB | 保留一路 PS 千兆网，YT8521 PHY；四个 USB2.0 HOST 通过 HUB 扩展，并非四个独立 USB 控制器 | 16、21–22 |
| LED/按键 | PL_LED1–4 引脚 J1/M6/H7/J8；PL_KEY1/2 引脚 F8/E7；可作为接口与基础逻辑验证入口 | 19–20 |
| 视频输入 | 两路 SDI 输入；MIPI CSI J16 为两数据 lane、一时钟 lane。手册写 PL BANK12 1.8V、控制 I2C 上拉至 3.3V，但 B4 图中 BANK12 VCCO 接 3.3V，使用前须讨论核对 | 26、28–29 |
| HDMI | IO 模拟 HDMI；手册给出 720p60，并提示部分显示器在 1080p60 下闪屏，TMDS 速率超出其注明的 HR bank 上限 | 25 |
| PCIe/SFP | 板级 PCIe 金手指 x1；SFP0 可用。芯片规格中的 PCIe Gen2 x4 不等于板级布线 x4 | 5、8、23–24 |
| GPIO | HEADER 14×2 共 16 路 GPIO，手册列 4 路 3.3V、12 路 1.8V；B4 按网络追踪后发现具体分组与注释不一致，不能仅按网络名确定电平 | 27 |
| XADC | 正文给出 12bit、1MSPS，外部模拟输入 AVpp<1Vpp；正文通道文字与表格不一致，B4 电路支持表格中的 J23→VAUX8、1.5V 监测→VAUX1 | 30 |
| 电源 | DC 12V 供电，含保护与分级上电时序；电源页的 6A 是保护限流值，不是已测整板功耗 | 31–32 |

手册第 32 页引用的文件名为 `JFMQL30TAI_V02_原理图.pdf`。随后提供并确认 `JFMQL30TAI_LITE.pdf` 是 30TAI 配套图纸，已纳入 B4；文件名不同不代表已经证实二者是同一修订或同一文件。现在可沿接口网络追踪到芯片封装引脚与 BANK 供电，仍应保留具体电平冲突并核对实际板卡。

### B2. Lite 与完整版差异

对照来源：C1 第 4–5 页及悟净开发板（完整版）硬件使用手册V1.0_嵌赛.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/开发板手册/悟净开发板（完整版）硬件使用手册V1.0_嵌赛.pdf`）（41 页）。两版使用同一 PCB，但 Lite 未焊接部分器件：

| Lite 被裁剪的功能 | 对比赛开发的影响 |
| --- | --- |
| PL 千兆网、PS QSPI1、PL eMMC | 不能照搬依赖第二网口、第二 QSPI 或 PL eMMC 的示例 |
| CAN、RTC、EEPROM | 芯片本身支持相关外设不代表 Lite 有完整板级接口 |
| SMA、SFP1、SDI 输入 3/4、SDI 输出 | 不能把完整版多路高速输入输出算作 Lite 已具备的接口 |
| 可调 GT 时钟、电流监控器件 | GT 时钟参考和功耗测量方案应先确认实际板卡支持 |

完整版手册可辅助理解共用设计、相同芯片和术语，但不能替代 Lite 接口、电平、焊接资源及约束核对。规格表中的芯片外设数也不能替代板级实装数量。

### B3. JTAG 转接图（1 页，接线对照）

来源：TRANSFER_0329.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/开发板手册/TRANSFER_0329.pdf`）。实际为 JTAG 的 14pin/20pin/8pin 转接原理图，包含 TMS/TCK/TDI/TDO、VTref、RESET/INIT 与 GND，不是悟净开发板完整原理图，也不是文件传输协议资料。

价值在于识别下载器、转接板和板端插座之间的连接；上板仍要结合实际接口方向、针脚 1 标记和启动模式。

重复资料核对：下载区“开发板手册”中的 Lite、完整版和 TRANSFER 三份 PDF，分别与项目内同名文件 SHA-256 一致。可优先引用项目内副本，避免当成不同修订版本。

### B4. Lite 完整原理图（28 页，引脚和电路连接依据）

来源：JFMQL30TAI_LITE.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/开发板手册/JFMQL30TAI_LITE.pdf`）。**人工确认它是 30TAI 配套原理图**；首图及 U1 分块符号标注 JFMQL30TAI。PDF 第 1–25 页标题栏仍写 JFMQL100TAI、V1.0，第 26–28 页保留 `<Title>`/`<RevCode>` 占位文字；图纸页数标注共 35 张，实际文件只有 28 页且图纸编号不连续。这些标注差异不改变人工确认的配套关系；是否沿用旧模板、是否按 Lite 裁剪页面尚无独立说明，不自行断定原因。

本节所有“PDF 页”指文件中的实际页序。原图 `Sheet` 编号不能直接当 PDF 页码：PDF 1–15 对应 Sheet 1–15；PDF 16–28 依次对应 Sheet **17、18、21、23、24、25、26、28、29、30、31、32、33**。原编号 16、19、20、22、27、34、35 未出现在该文件中，不据此断言补充了错误图纸或必须另找七页。

#### B4.1 页面导航与参考价值

| PDF 页 | 内容 | 用途 |
| --- | --- | --- |
| 1 | JFMQL30TAI、PS/PL/GTX 与外设总览 | 对照 Lite 实际保留的接口及系统划分 |
| 2–3 | PS MIO、启动模式、时钟/复位；QSPI0 | 启动拨码、PS 时钟与启动故障定位 |
| 4–5 | PS DDR 引脚、DDR 器件 | 理解 PS 内存连接；BSP/FSBL 调整仍需配套参数和实际验证 |
| 6–8 | PS 千兆网 YT8521、CP2103 串口、MicroSD、USB PHY/HUB | 外设电源、复位、MIO 与连接路径定位 |
| 9–11 | U1 BANK0/12/13、33/34/35、MGT | 建立接口网络→封装引脚→BANK/参考时钟的依据，是约束核对的重点 |
| 12–15 | 芯片电源引脚/去耦、PL DDR 64bit 及端接 | 理解 PL DDR 与供电连接，不等于已取得全部控制器时序参数 |
| 16 | MIPI J16、GPIO J17、拨码 | 摄像头/外设连接；与第 9 页交叉追踪引脚和电平 |
| 17–19 | 两路 SDI、SFP0、HDMI 输出 | 视频/高速链路、外围器件及 HDMI 输出限制 |
| 20–22 | XADC、100/200/148.5MHz 时钟、LED/按键及 JTAG 电平转换 | 简单 PL 验证、模拟采集、时钟输入与下载接线 |
| 23–28 | PCIe x1、供电总览、DC12V 保护、各路稳压及 GT 电源 | PCIe 与供电/上电故障排查；不把额定器件参数当整板实测功耗 |

重要性：B1 给出功能和使用限制，B4 补齐网络、器件、电路和封装引脚，可用于检查 XDC/FDC、端口极性及外设连接。应同时核对 B1、B4、D3 和实际板卡；以下是**图纸连接记录，尚未上板验证**，也不是已选定的新工程约束。

#### B4.2 时钟、基础 I/O 与视频关键引脚

成对引脚均按 P/N 顺序列出。BANK VCCO 是图示供电，不自动决定每个端口应选哪种 IOSTANDARD；差分时钟、TMDS、GT 和模拟输入尤其不能统一当普通 GPIO 使用。

| 网络/功能 | 图示封装引脚 | 连接及开发意义 | PDF 页 |
| --- | --- | --- | --- |
| PS_CLK，50MHz | B24 | U3 50MHz 振荡器；PS 时钟不能与 PL 输入互换 | 2 |
| PL_100MHz | **AC14** | G1 100MHz 单端振荡器→BANK12 MRCC；图示 VCCO12=3.3V，周期 10ns | 9、21 |
| PL_DDR_EXT_CLK_P/N，200MHz | **C8/C7** | X3 差分源，经交流耦合/偏置连接 BANK34；图示 VCCO34=1.5V，周期 5ns；与 D3 sys_clk_p/n 一致 | 10、21 |
| MGT_148P5M_CLK_P/N，148.5MHz | **R6/R5** | X6→MGTREFCLK0P/N_112；与 D2/D3 Lite SDI 参考时钟一致，周期约 6.734ns | 11、21 |
| PCIE_CLK_Q0_P/N | U6/U5 | MGTREFCLK1P/N_112，属于另一路参考时钟；不能仅因旧完整版约束使用 U6/U5 就代替 Lite 的 R6/R5 | 11、23 |
| PL_LED1 / PL_LED2 | J1 / M6 | BANK33，VCCO=PL_VCC1V5；D3 中 LED1/2 注释写 BANK13，与图纸不符 | 10、22 |
| PL_LED3 / PL_LED4 | H7 / J8 | BANK34，VCCO=PL_VCC1V5 | 10、22 |
| PL_KEY1 / PL_KEY2 | F8 / E7 | BANK34，VCCO=PL_VCC1V5 | 10、22 |
| HDMIO_FCLK_P/N | AC17/AC16 | BANK12，VCCO=3.3V | 9、19 |
| HDMIO_FD0_P/N | AA15/AA14 | HDMI 数据通道 0，BANK12 | 9、19 |
| HDMIO_FD1_P/N | Y16/Y15 | HDMI 数据通道 1，BANK12 | 9、19 |
| HDMIO_FD2_P/N | W16/W15 | HDMI 数据通道 2，BANK12 | 9、19 |
| MIPI_LANE0_P/N；LANE1_P/N；CLK_P/N | Y12/Y11；Y10/AA10；AC13/AD13 | 都连 BANK12；手册所写 1.8V 与图示 BANK12 VCCO=3.3V 冲突，暂不据此决定摄像头接法或 IOSTANDARD | 9、16 |
| CAM_GPIO / CAM_SCL / CAM_SDA / CAM_CLK | AE15 / AE17 / AF17 / Y17 | 摄像头控制/时钟网络；需与 HS/LP 通路、电阻和外设电平一起核对 | 9、16 |

由第 22 页电路分析：LED 使用 NDS331N 低侧开关，PL 输入高电平时导通点亮；按键网络有 10K 下拉，按下接 PL_VCC1V5，因而图示为**空闲低、按下高**。这是按电路得出的极性判断，尚未测量实板。

第 19 页原图注释也提醒：直接通过 IO 模拟 HDMI 不能保证所有显示器支持 1080p60，建议 IO 方案使用 720p 或更低分辨率，需要 1080p 时考虑专用输出芯片。它与 B1 的风险提示一致，不能由示例默认 1080p60 推导出可靠输出已得到验证。

第 11 页高速收发连接：SDI0_RX P/N=AB4/AB3（RX0），SDI1_RX=Y4/Y3（RX1）；SFP0 RX=V4/V3、TX=U2/U1（通道 2）；PCIe RX=T4/T3、TX=R2/R1（通道 3）。这些是 GT 管脚，不能套用普通 GPIO 电平约束。D2 的 `FMC_HPC_GBTCLK0_M2C_C_P/N` 是工程端口名，仍应按其 R6/R5 实际连接理解，不据名称推断本板有 FMC 插座。

#### B4.3 GPIO J17：必须沿网络追踪 BANK

第 16 页 J17 旁注写“4 引脚 3.3V、12 引脚 1.8V”；按第 9 页 U1 引脚与 VCCO 追踪，数量仍是 4+12，**但具体网络分组与 `HR_IO12/13` 名称所暗示的 BANK 不一致**。下表电压仅记录芯片侧图示 BANK 供电，不能当作已确认实板电平或接线许可。

| J17 脚号 | 网络 | U1 封装引脚 | 图中实际 BANK | 图示 VCCO |
| --- | --- | --- | --- | --- |
| 3 / 4 | HR_IO12_1P / 1N | AC21 / AC22 | 13 | 1.8V |
| 5 / 6 | HR_IO12_2P / 2N | AE20 / AE21 | 13 | 1.8V |
| 13 / 14 | HR_IO13_6P / 6N | AF19 / AF20 | 13 | 1.8V |
| 15 / 16 | HR_IO13_5P / 5N | AD20 / AD21 | 13 | 1.8V |
| 17 / 18 | HR_IO13_4P / 4N | AE18 / AF18 | 13 | 1.8V |
| 19 / 20 | HR_IO13_3P / 3N | AD18 / AD19 | 13 | 1.8V |
| 21 / 22 | HR_IO13_2P / 2N | W13 / Y13 | 12 | 3.3V |
| 23 / 24 | HR_IO13_1P / 1N | AE13 / AF13 | 12 | 3.3V |

J17 的供电脚与信号脚是不同用途，表中未将供电脚计入 16 路 GPIO。连接器旁有 3.3V/1.8V 电源并不能说明邻近信号使用同一电平。若要接传感器、扩展板或驱动这些信号，先评估此冲突，再核对实板修订、厂商说明或测量证据，不自行选择以注释或芯片页为最终接线依据。

#### B4.4 XADC：明确的外部接口和电源监测连接

第 20 页网络与第 9–10 页 U1 管脚交叉核对结果如下；P/N 仍按顺序列出，外部接口 pin3=P、pin2=N、pin1=GND。

| 接口/被测对象 | 通道 | U1 P/N 引脚 | 图示连接 |
| --- | --- | --- | --- |
| J24 外部输入 | VP/VN | N14/P13 | 专用模拟输入 |
| J25 外部输入 | VAUX0P/N | F12/E12 | 外部辅助通道 0 |
| **J23 外部输入** | **VAUX8P/N** | E10/D10 | 外部辅助通道 8 |
| **PS_VCC1V5 监测** | **VAUX1P/N** | G10/F10 | 两个 1K 电阻等比分压，标称 1.5V 对应约 0.75V 输入 |
| VCC1V8 监测 | VAUX9P/N | G12/G11 | 两个 1K 电阻等比分压，标称 1.8V 对应约 0.9V 输入 |

因此新增电路证据支持 B1 第 30 页的**表格/图片**，而非该页将 VAUX1 与 VAUX8 对调的正文。资料层面可明确记录这种对应关系；正式开发仍需确认实际板卡连接、XADC 配置及模拟输入范围，不能把电源轨未经分压直接接入模拟输入。

## 4. 项目内 30TAI 开发包：最直接的系统集成参考

### D1. 30TAI 使用教程（11 页，工具链主入口）

来源：30TAI使用教程.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/30TAI使用教程.pdf`）。它把 Vivado/IP 补丁、Procise、BOOT 与 PS 应用串成完整流程，是理解当前示例如何产生位流和运行程序的重要资料。

关键内容：

1. 第 1–5 页：JFM_Kits 放在不含中文、空格和特殊字符的英文路径；`JFM_PATH` 指向 `ip_patch` 上一级；关闭 Vivado IP Cache；每个 IP 做 OOC 综合；加载 `ip_patch/run.tcl`，执行 `add_hook_tcl_to_prj`；30TAI 时序库使用 `replace_7z030ai_file`，切回其他器件时使用 `reset_database_to_default`。
2. 第 5–6 页：示例基于 Vivado 2018.3（教程写作 2018.03），器件代理为 `xc7z030ffg676-2`；加入 RTL、约束、BD 和 `PS_AI IP` 仓库。教程建议直接点 Generate Bitstream，由补丁流程处理，不能套用其他迁移教程的执行顺序。
3. 第 7–9 页：根据 BIF 打包 FSBL、PL 位流、bl31、u-boot 为 `BOOT.bin`，替换 SD 卡 FAT 分区中的 BOOT；SSH 方式必须确认真实启动分区已挂载，仅把文件放入未挂载的 `/root/bits` 不会更新启动内容。
4. 第 9–11 页：安装交叉编译所需 Icraft/CustomOp，不在 30TAI 板上编译该示例；CMake 指定 `TARGET_CHIP=ZG`；无 SDI 时 YAML 的 `camera.vtc=true` 使用测试图，接 SDI 时为 `false`。

这里的 Vivado 是该厂商参考工程的前端/IP 生成与迁移环节；最终面向复旦微器件的实现和位流仍涉及 Procise。不能把普通 Xilinx 位流直接当成复旦微可用位流。是否沿用这套参考流程，要在参考实现确定后讨论。

### D2. FPAI_DEMO 说明（8 页，软硬件接口主入口）

来源：FPAI_DEMO说明.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/FPAI_DEMO说明.pdf`）。

数据流（第 1–2 页）：SDI 1080p60 → PL 解码成 RGB888 并分成两路 → 一路预处理后进入 PL DDR 供 AI 推理，另一路进入 PS DDR 供显示 → PS 启动 AI、读取输出、后处理和叠加 → HDMI 显示。它说明推理 FPS、视频输入帧率和显示 FPS 是不同指标，测试中要分别记录。

默认 `AI_Mate.edif` 带 DetPost 硬算子；`AI_Mate_no_detpost.edif` 可替换以降低 PL 逻辑占用。这是明确的资源取舍，不能只改网表却不核对模型与后处理配置。

自定义硬算子接口（第 2–8 页）：

- 一路 PS 主动访问的寄存器接口，32bit 地址/数据，custom op 寄存器空间为 `0x400C0000–0x400FFFFF`。
- 一路 custom op 主动读写 PL DDR 的数据接口，32bit 地址、512bit 数据，即每拍 64 字节。
- `User_Ddr_awwinfo[70:7]` 是 64bit 字节使能；有效传输发生在 `valid && ready` 同时为真时。
- C++ 通过 `defaultRegRegion().read/write` 控制寄存器，`defaultMemRegion().malloc` 分配 PL DDR，并用 MemChunk 读写；文档列默认 64 字节对齐。

价值：这是从软件基线扩展为 FPGA 加速模块的具体入口。寄存器配置、DDR 访问、结束标志和 PS 读回形成可观察闭环。该接口是参考设计提供的自定义握手接口，不能仅因名称近似就当成完整标准 AXI 接口；应查 RTL 的转换模块与握手实现。

Lite 的特定约束（第 1 页）与当前源码一致：`FMC_HPC_GBTCLK0_M2C_C_P/N` 使用 **R6/R5**，完整版为 **U6/U5**。这也是“同一 PCB”仍需按板版核对约束的直接例子。

### D3. FPGA 工程、约束与 PS 示例

| 文件/目录 | 作用与本轮检查到的内容 |
| --- | --- |
| fpai_demo_vivado.xpr（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/fpai_demo_vivado.xpr`） | 工程头记录 Vivado 2018.3，Part 为 xc7z030ffg676-2，IPCache 为 disable，使用 PS_AI IP；存在打包者旧路径，重建时须核对引用 |
| impl_constraints.xdc（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/constrs_1/impl_constraints.xdc`） | 当前已启用 Lite R6/R5；差分 200MHz `sys_clk_p/n` 为 C8/C7，5ns；MGT 参考时钟周期 6.734ns；含 HDMI、按键、LED 与 PJTAG 约束。B4 核对了关键引脚，但 LED1/2 的 BANK13 注释应按原理图理解为 BANK33；本次未改源码/约束 |
| ai7030.xdc（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/constrs_1/ai7030.xdc`） | 与实现约束一起构成工程约束来源；修改时还需看约束加载顺序和作用范围 |
| rtl（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/rtl`） | 包含顶层、AI_Mate stub/EDIF、自定义 adder、SDI、时钟复位与接口转换等，是 FPGA 修改入口 |
| adder_demo.cpp（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_app/examples/1_single_input+ai/PLin+SingleNet+HDMI/src/adder_demo.cpp`） | 分配 PL DDR → 写输入 → 写寄存器启动 → 轮询 done（10 秒超时）→ 读回结果，能用于核对寄存器/DDR/握手通路 |
| CMakeLists.txt（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_app/examples/1_single_input+ai/PLin+SingleNet+HDMI/CMakeLists.txt`） | 默认 TARGET_CHIP=BY，30TAI 应显式选 ZG；C++17，UNIX 分支设置 aarch64-linux-gnu 编译器和 Icraft 后端库 |
| sdicamera+yolov5+hdmi.yaml（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_app/examples/1_single_input+ai/PLin+SingleNet+HDMI/configs/ZG/sdicamera+yolov5+hdmi.yaml`） | 实际使用 axi://zg330aiu，NPU 基址 0x40000000、DMA 基址 0x80000000；模型 640×352，输入/显示 1920×1080@60，detpost=true，fpga_nms=false；这些地址仅适用于对应参考设计 |
| modelzoo_utils（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_app/deps/modelzoo_utils`） | 运行时工具库，含 C++/Python API、设备/模型/视频通路辅助；本包 version.log 首行为 v20250826142435 |

adder 示例中 `reg_base+0xC0` 读取版本，`+0x4/+0x8` 写传输配置，`+0x0` 启动，`+0x80` 读结束。地址与长度的打包方法应以对应 RTL 为准，不能把示例寄存器编码视为任意自定义算子的通用协议。

YAML 里的 `__3.31__` 是配置字段，不能据此认定本机 Icraft 版本。当前 YAML 的 `detpost=true` 也不代表 NMS 已在 FPGA 运行，文件另有 `fpga_nms=false`。准确划分需结合模型、位流和源码。

### D4. BOOT 组件和项目内 BIT

来源：BOOT_Gen（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/BOOT_Gen`）、BIT（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/BIT`）、icraft_deb（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_app/icraft_deb`）。

- `7030ai_psin.bif` 打包 FSBL251210_ddr400_demo.out、ai7030_edif_top.bit、bl31.elf、u-boot，包含 `apu_x32` 配置；BIF 内仍是 `C:/Users/admin/Downloads/BOOT_Gen/...`，须改成真实可读取位置后才可复现。
- BIT 同时提供 `30tai_detpost` 与 `30tai_lite_detpost`，各有 BOOT.bin 与 `ai7030_top_disable_icap.bit`；按命名属于不同板版候选，不能凭命名认定已与 3.39.0 匹配。
- 项目内 `icraft_deb` 附带 Icraft/CustomOp **3.33.1** 板端安装包；它们是旧示例依赖，不是确定的 3.39.0 基线。
- `FSBL`、设备树、u-boot、位流、Linux 镜像和 runtime 需视为一组系统组件；已报告新卡基本启动和串口登录通过（第 15 节），实际组件版本/哈希、runtime 与 AI 配套组合仍未核验。

### D5. JFM_Kits / IP Patch / 通用迁移资料

来源：JFM_Kits（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits`）、fmsh_migration_process（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits/ip_patch/fmsh_migration_process`）。本包 `ip_patch_version.log` 为 `5.3.2.1_100AI_LV`，需与 30TAI 教程及实际脚本支持范围一起判断，不能只看后缀猜测是否支持本板。

| 资料 | 参考价值与适用边界 |
| --- | --- |
| 100t&&130工程迁移流程_V5.0.docx（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits/ip_patch/fmsh_migration_process/100t&&130工程迁移流程_V5.0.docx`） | 解释普通/BD 工程、GT、DSP、调试核与约束迁移，含 JFM_PATH/FMSH_PROCISE_PATH、版本/路径要求；主要针对 FMP100/130 |
| 基于修改Vivado数据库的FMP100.docx（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits/ip_patch/fmsh_migration_process/基于修改Vivado数据库的FMP100.docx`） | FMP100/130 与数据库替换的补充步骤，文中使用 JFMP130T8、xc7a100t 等；不是 30TAI 的器件选型依据 |
| 基于FMP100T4开发板的Vivado to Procise迁移流程.pdf（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits/ip_patch/fmsh_migration_process/基于FMP100T4开发板的Vivado to Procise迁移流程.pdf`） | 39 页，Vivado2018.3 的简单工程、IP/ILA、DSP/GT 等案例；适合理解迁移机制和定位问题，不能照抄 FMP100T4 器件配置 |
| vccm_boost脚本使用说明.docx（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits/ip_patch/tools/vccm_boost/vccm_boost脚本使用说明.docx`） | 位流补丁工具用法，例子针对 JFM7VX690T80；非 Lite 日常开发必选步骤 |
| procise_incr_cfg.txt（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits/ip_patch/procise_incr_cfg.txt`） | 模板器件为 JFM7K325T8，输入是 sw_ctrl_led.bit；不能原样用于本项目 |

含 `run.tcl`、器件数据库、原语/IP 替换和约束转换脚本的工具包是厂商迁移流程的组成部分，不应把全部文件作为竞赛自研 RTL。压缩包是原始分发件，已解压目录便于查阅；若更新版本，要记录来源和差异。

## 5. Procise：按开发环节查手册

以下文件都来自本机安装目录，页数是 PDF 总页数。部分文档修订时间早于本机 2025.1.1 temp，命令可用性还应核对本机工具。页内编号可能有罗马数字前言，不能与 PDF 页序混用。

| 资料 | 页数 | 重要性、已理解内容与查阅场景 |
| --- | --- | --- |
| 软件安装与初始化手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/软件安装与初始化手册.pdf`） | 13 | 环境、安装路径、license、启动/驱动问题；文件标记 V2025.1，说明自 V2023.2 起安装包带长期通用 license |
| Procise用户使用手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Procise用户使用手册.pdf`） | 36 | 必查。GUI 新工程到综合、优化、布局布线、时序与位流，及 Shell/Tcl 工程；PDF 第 9 页明确工程路径不支持中文 |
| Procise应用示例一.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Procise应用示例一.pdf`） | 37 | 第一个原生 Procise 工程的操作参考，适合工具链入门，器件/引脚要替换为本板 |
| Procise约束手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Procise约束手册.pdf`） | 32 | 必查。FDC 组织/加载顺序/生效范围；get_ports/nets/cells/pins，时钟、I/O 延迟、时钟组、false/multicycle path、PACKAGE_PIN、IOSTANDARD 等 |
| 引脚约束工具使用手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/引脚约束工具使用手册.pdf`） | 17 | I/O Planning、封装/BANK、电平、位置约束、DCI 与保存；遇到引脚报错时结合 Lite 手册和实际板卡 |
| Timing Constraint Wizard使用手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Timing Constraint Wizard使用手册.pdf`） | 11 | 向导辅助时序约束；不能取代正确识别时钟、外设时序和跨时钟域关系 |
| 静态时序分析的时序路径.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/静态时序分析的时序路径.pdf`） | 7 | 四类路径、setup/hold、corner、arrival/required/slack 与 timing report；用于解释和定位性能限制 |
| 仿真验证使用手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/仿真验证使用手册.pdf`） | 13 | ModelSim 环境、库编译、行为与综合后功能仿真；需要相应仿真工具和复旦微库，不能认为 Procise 单独包办所有仿真 |
| Procise在线调试手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Procise在线调试手册.pdf`） | 57 | 必查。ILA/Mark Debug、ChipXplorer、带 ILA 信息的 bit/ltx、触发与波形；用于握手、复位、FIFO 和 DDR 通路上板定位 |
| 编程下载工具使用手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/编程下载工具使用手册.pdf`） | 35 | 必查。JTAG 下载、MCS、SPI/BPI Flash、FlashLoaderBootGen；下载 `.bit` 与更新整板 BOOT 是不同操作 |
| Procise驱动安装指导手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/driver/Procise驱动安装指导手册.pdf`） | 6 | 下载器驱动/过滤驱动说明；强调 Xilinx 官方 DLC 驱动和旧补充包冲突，按实际下载器选流程 |
| Platform Tools使用手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Platform Tools使用手册.pdf`） | 82 | 位流增量配置、转换、压缩/加密、create_prom、器件交互等；多数功能按需求查，不是全部必执行 |
| BspSettingTool使用说明.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/BspSettingTool使用说明.pdf`） | 10 | PSOC PS 外设 BSP 驱动版本引用调整；只改工程索引，需先 Export Hardware；不支持修改 FSBL/Flashloader 驱动版本 |
| Verilog语法说明.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Verilog语法说明.pdf`） | 25 | 本机原生综合支持/限制参考；文档列 SystemVerilog 等不支持情形，不能据 Vivado 示例含 .sv 推断原生综合支持完全相同 |
| Procise原语手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Procise原语手册.pdf`） | 257 | RAM、DSP、时钟、I/O 等原语的功能/属性/端口/例化；应按器件系列查对应条目，而不是照抄其他系列模板 |
| Procise HRDT用户手册.pdf（本机路径，仓库未附：`C:/FudanMicro/Procise/documents/Procise HRDT用户手册.pdf`） | 116 | TMR、BRAM/DRAM/FIFO 加固和翻转率预估等可靠性方向；一般系统联调阶段优先级较低，采用前需确认支持器件与资源代价 |

辅助入口：lab_samples（本机路径，仓库未附：`C:/FudanMicro/Procise/lab_samples`） 有 counter 与 led_flow；language_templates（本机路径，仓库未附：`C:/FudanMicro/Procise/language_templates`） 有 Verilog/VHDL 原语模板；conf（本机路径，仓库未附：`C:/FudanMicro/Procise/conf`） 中有 commands_basic/builtin/sdc/util.xml，可作为本机 Tcl 命令查找线索。

**工程复现要点**：本项目文档目录含中文且 `PS_AI IP` 含空格，而 Procise 工程和 JFM 补丁分别有路径限制。若后续构建需要工作副本，应先讨论路径布局并记录源码来源；本次没有移动或重写资料目录。时序报告需同时检查 setup/hold、时钟覆盖、I/O 约束和未约束路径，不能只凭“生成了位流”认定时序与上板均正确。

## 6. Icraft 3.39.0：模型部署、精度与运行时

### I1. 首先找对 30TAI/ZG330 文档

本机文档同时覆盖 BUYI/100TAI、ZG330/30TAI 等平台，部分通用示例默认 BUYI。30TAI 相关流程要查 **ZHUGE/ZG330**，不能照抄 Buyi 的 target、设备地址、量化参数或模型文件。

| 入口 | 内容及用途 |
| --- | --- |
| 安装（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/start/installation.html`） | Windows/Linux 安装、CLI 链接、Python 与 CMake SDK 环境 |
| 编译（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/start/compilation.html`） | TOML 与 parse → optimize → quantize → adapt → generate，模型中间产物和日志 |
| 框架支持列表（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/ops/framework.html`） | 导入格式/框架版本/ONNX opset 和算子参数限制，是选模型、导出模型前的直接检查依据 |
| Parse（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/parse/index.html`） | 模型解析；出错时区分文件格式、算子映射、输入形状和参数问题 |
| ZHUGE Quantizer（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/quantizer/zhuge/zhuge.html`） | 30TAI 的 INT8/BF16/FP16/TF32、校准、混合精度、量化配置与错误码 |
| Adapt（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/adapt/index.html`）、Codegen（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/codegen/index.html`） | 硬件适配与指令生成；前端支持某个算子不代表所有后端配置均能部署 |
| 运行（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/start/running.html`）、icraft-run（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/icraft-run/index.html`） | Host 仿真与设备推理、CLI/API、模型和输入、输出导出 |
| XRT（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/xrt/index.html`） | Device、MemChunk、Tensor、Session 及后端的运行时基础 |
| ZG330Backend（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/zg330backend/index.html`） | 30TAI 部署、内存复用、网络连接、OCM/ETM 调优；实际推理通过 Session.forward |
| AXI ZG330 设备（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/axizg330aiu/index.html`）、Socket ZG330 设备（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/socketzg330aiu/index.html`）、Server（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/server/index.html`） | 板端 AXI 访问与远程设备运行是不同部署方式；端口、地址、server 及权限需核对 |
| Icraft Show（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/show/index.html`） | 查看网络、逐层精度对比、OCM/ETM 内存分析，定位模型转换和量化误差 |
| XIR（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/xir/index.html`）、自定义算子（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/extensibility/customop.html`）、Demo（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/demo/index.html`） | 计算图、Pass/算子扩展与示例；软件 CustomOp 扩展并不自动等于新增 FPGA 硬算子 |
| 故障排查（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/troubles/trouble_shotting.html`）、版本缺陷（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/defects/version_defects.html`）、更新日志（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/changelogs/change_logs.html`） | 区分配置问题、权限/PS 内存问题和历史版本限制 |

也可使用资料自述中的 `icraft docs` 打开文档。本轮按静态 HTML 阅读，未启动 Icraft 执行模型编译。

### I2. 编译与精度验证的理解

编译流程为五个阶段：解析原始模型、图优化、量化、硬件适配、指令生成。快速开始页面部分文字称“四个步骤”，但列举了五个组件；按实际命令链理解，不把文字笔误扩展为额外步骤。

模型的 JSON 保存网络结构，RAW 保存参数，应成对保留并区分 parsed/optimized/quantized/adapted/最终 ZG 阶段。日志入口通常是 `.icraft/logs/{网络名}`；记录 TOML、模型、校准集列表、工具版本和原始导出环境才能复现结果。

本机“框架支持列表”记载：TorchScript 通过 torch.jit.trace 导出，列 PyTorch 1.9.0/2.0.1；ONNX opset 11/14/17、IR 8，ONNX 最高 1.13.1。它是本地资料记载的边界，不能假设任意新导出器、动态形状、ONNX 版本都已支持。表格不仅列支持符号，还列 Conv、Pad、Pool 等参数限制，选模型时要查具体配置。

30TAI 的 ZHUGE 量化文档支持 INT8、BF16、FP16、TF32；INT8 依赖来自实际场景的代表性校准数据，涉及 saturation/per 等配置；BF16/FP16/TF32 不走完全相同的校准步骤。`qdtype`、混合精度和输入变换要按 ZHUGE 文档配置，通用 BUYI 的 bits=8 示例不是完整的 30TAI 配方。

建议保留原框架、解析/优化、量化、设备推理四层结果用于误差定位，再与端到端性能比较。模型精度、NPU 推理耗时、数据搬运和显示耗时分别记录，不用峰值 TOPS 替代作品实测性能。

### I3. 运行时与版本配套

XRT 用设备、后端和 Session 组织运行。ZG330Backend 文档明确：部署后要通过 Session 的 forward 接口实际执行推理；OCM 优化、ETM 复用、多个网络输入输出共用 PL DDR 可减少外存或 PS/PL 拷贝开销，适用于性能瓶颈分析。

本机仍带旧版 30TAI v3.33.0 发布说明（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/version/Icraft v3.33.0_FMQL30TAI.html`），它明确该版 compiler/runtime 必须同版本并配套 AI_MATE 25101801。这个旧声明不能直接充当 3.39.0 的完整兼容矩阵，但说明版本配套是必须核验的系统条件。

故障排查页提示：Session 被 kill 时检查 PS DDR 内存需求；`Open /dev/mem failed` 时检查管理员权限。此类提示是排查方向，仍须结合实际日志判断。缺陷页“不支持 detpost”明确标记 **v3.33.0**，不能套到 3.39.0；本机 3.39.0 CustomOp 目录可见 DetPostZG 等 DLL，但文件存在也不能证明某个位流和模型组合已上板兼容。

### I4. Windows 依赖诊断与环境分工（2026-10-01）

- `icraft run --help` 与直接调用 `icraft-run.exe --help` 都曾出现 `nvfuser_codegen_ic.dll` 的 LoadLibrary/WinError 126 警告；帮助正常输出，退出码为 0。
- 被点名 DLL 存在。静态 PE 依赖分析发现 `torch_cuda_ic.dll` 需要 `cufft64_10.dll`、`cublas64_11.dll`，`cusolver64_11.dll` 还需要 `cublasLt64_11.dll`；这些库在 Icraft bin 与当时搜索路径中缺失，直接加载相关现有库返回错误 126。
- 仅在独立测试进程中临时加入 `C:\Users\cenyongdong\miniconda3\envs\koala\Lib\site-packages\torch\lib` 后，警告消失、stderr 为 0 字节、退出码为 0，帮助正文与原结果逐字节一致。该目录的 Python/相关 DLL 为 Windows x64 格式，Conda Python 记录为 `win-64`；所附 PyTorch 为 `2.1.2+cu118`。这些信息是诊断依据，不是比赛训练环境或版本基线。
- 该结果验证了 CUDA 依赖库的可发现性会影响警告，但仅覆盖帮助命令级加载，未验证实际模型、CPU/GPU 推理或 ZG330 实板运行，也不能据此认定 CUDA 11.8 是 Icraft 3.39.0 的厂商指定版本。
- 方案倾向保留 Windows 上的 Procise/Icraft；当前算法训练在远程 Ubuntu 服务器，`Z:` 用于访问其文件。本机双系统 Ubuntu 不是当前训练位置。远程训练到 Windows Icraft 的模型/数据交接格式及实际路径，后续按项目顶层架构讨论，不在当前阶段填入。
- 此阶段提出为 Windows Icraft 准备独立、版本明确的兼容依赖及启动方式，后续第一阶段已确定并完成，详见 I5。`koala` 与本项目无关，不能擅自作为长期依赖；超出已批准范围的安装、全局配置或工具迁移仍须先讨论。

### I5. Windows Icraft 独立依赖方案与第一阶段结果（2026-10-01，已批准并完成）

“下载两个官方 ZIP、建立独立目录和启动脚本，并执行加载验证”，。以下第一阶段已经完成，与之前仅针对 `koala` 的临时验证分开记录。

**版本依据与限制**：Icraft 本机文件、安装包自述及已查手册尚未给出 3.39.0 对 CUDA 小版本的明确兼容矩阵。CUDA 11.8 是候选验证组合，依据是先前 `2.1.2+cu118` 目录的库让帮助命令警告消失；它不是厂商确认的 Icraft 必需版本，也不能取代模型/GPU/板端验证。已有 Icraft CUDA/cuDNN DLL 与新增库共同组成的环境仍需实测，不能称为已经完整配套的 CUDA 11.8 工具链。

**已使用的依赖来源**：[NVIDIA CUDA 11.8.0 官方组件清单](https://developer.download.nvidia.com/compute/cuda/redist/redistrib_11.8.0.json) 给出 Windows x86_64 ZIP、组件版本、大小及 SHA-256；下载的两个 ZIP 均通过官方哈希验证。缺失的三个 DLL 已由以下两个组件补充，Windows x64 格式、许可证、依赖和导入符号均已检查：

| 官方组件 | 固定组件版本 | 已补充的 DLL | ZIP 大小（字节） | 官方 SHA-256 |
| --- | --- | --- | --- | --- |
| `libcublas` | `11.11.3.6` | `cublas64_11.dll`、`cublasLt64_11.dll` | 420850025 | `67b0934a6359e4ee26fff823c356021589d392c4fd49ca12624f570edc08e2b9` |
| `libcufft` | `10.9.0.58` | `cufft64_10.dll` | 168982770 | `a4071a85e3983bf42ea7a2e9bebe3b0b3c9ac258668580adc32ee1c385f7556f` |

官方 ZIP 相对路径分别为 `libcublas/windows-x86_64/libcublas-windows-x86_64-11.11.3.6-archive.zip` 和 `libcufft/windows-x86_64/libcufft-windows-x86_64-10.9.0.58-archive.zip`，基址为 `https://developer.download.nvidia.com/compute/cuda/redist/`。合计约 590 MB（562.5 MiB），解压所需空间另行核对。这些是 NVIDIA 组件版本，不是 Icraft 或 PyTorch 版本；本方案直接补充运行库，不以安装训练框架作为获取依赖的手段。

**已建立的文件与影响范围**：

- 依赖根目录：cuda-11.8.0（本机留存，仓库未附：`D:/FPGACompetitionProject/.local/icraft-runtime/cuda-11.8.0`）；保留原 ZIP、官方清单、解压包结构、许可证、文件哈希及验证日志，目前合计约 1.40 GiB。
- 项目启动器：[Invoke-Icraft.ps1](tools/Invoke-Icraft.ps1)。仅为 Icraft 子进程配置 PATH，依次优先使用 `C:\Icraft\CLI v3.39.0\bin`、上述 cuBLAS/cuFFT 包的实际 bin 目录；Icraft 自带库仍按原安装目录使用。每次调用校验三个新增 DLL 的 SHA-256，记录参数、工作目录、子进程 PATH 前缀、退出码及 stdout/stderr；支持显式指定工作目录。
- runtime-manifest.json（本机留存，仓库未附：`D:/FPGACompetitionProject/.local/icraft-runtime/cuda-11.8.0/runtime-manifest.json`） 固定来源、版本、ZIP/DLL 哈希和路径；verification-report.json（本机留存，仓库未附：`D:/FPGACompetitionProject/.local/icraft-runtime/cuda-11.8.0/verification-report.json`） 记录实际加载路径，三个新增 DLL 均来自独立依赖目录。测试 PATH 仅含 Icraft、上述组件和 Windows 系统目录，排除了 Conda 等训练路径。
- 获取的是两个官方 ZIP；第一阶段范围为独立目录和启动器，不涉及 NVIDIA 驱动/全局 PATH/注册表变更、系统 CUDA 安装器、Conda 训练环境修改、服务器修改或 FPGA 配置。

**已完成的第一阶段验收**：

1. 两个 ZIP 的 SHA-256/大小与官方清单一致；检查 12 个 DLL 的依赖链，核对 5 组共 226 项导入符号，无缺失符号或新未解析依赖。新增 DLL 均为 Windows x64 PE，厂商 LICENSE 已保留。
2. 在独立进程中加载 `cusolver64_11.dll`、`torch_cuda_ic.dll`、`nvfuser_codegen_ic.dll` 成功；通过 Windows 模块句柄检查三个 NVIDIA DLL 的实际路径，与独立目录清单完全匹配。
3. 原环境 `run --help` 退出码为 0，stderr 为 219 字节且有 nvfuser 警告；独立环境的版本/帮助、Windows PowerShell 5.1 启动器的版本/帮助退出码均为 0、stderr 均为 0 字节，帮助正文与原结果逐字节一致。当前 PowerShell 7.6.5 的启动器版本查询也通过。
4. 原 Icraft 核心文件哈希及用户/系统永久 PATH 在验收前后一致；启动器没有修改父进程 PATH。未执行系统 CUDA 安装器、更新驱动、改动训练环境或服务器。
5. 验收仅覆盖“独立库来源下的帮助/加载验证”。本次比赛模型规格尚未确定，正式编译、量化、CPU/GPU 推理以及 ZG330 部署的功能、精度、性能验证仍须在相应任务中另行讨论与授权。

可直接使用的加载查询命令：

```powershell
& 'D:\FPGACompetitionProject\tools\Invoke-Icraft.ps1' -IcraftArgs @('--version')
& 'D:\FPGACompetitionProject\tools\Invoke-Icraft.ps1' -IcraftArgs @('run', '--help')
```

详细说明见 [tools/README.md](tools/README.md)。[Prepare-IcraftRuntime.py](tools/Prepare-IcraftRuntime.py) 记录两个批准组件的获取/校验/解压过程；[Verify-IcraftRuntime.py](tools/Verify-IcraftRuntime.py) 记录 PE/符号/实际加载路径及 CLI/启动器复核方法，均仅使用 Python 标准库；启动器本身无需 Python/Conda。

回退方式是停用启动器；新增依赖位于独立目录。删除目录、更换组件、增加依赖、模型/设备操作或调整全局配置仍须按 `AGENTS.md` 的决策审批规范确认具体目标与范围。

## 7. 外部下载区：补充实现、环境与历史验证

### E1. Icraft 3.39.0 安装包与 Linux 环境

来源：Icraft自述文件.txt（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/Icraft自述文件.txt`）、Icraft_V3.39.0安装包（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/Icraft_V3.39.0安装包`）。

- Windows 安装包为 Icraft_Setup_v3.39.0.exe 和可选 CustomOp_Setup_v3.39.0.exe；自述强调先安装 Icraft。
- 已读取 `30TAI&100TAI.zip` 的目录，确有 **Icraft/CustomOp_3.39.0_amd64.deb**（主机交叉编译）和 **Icraft/CustomOp_3.39.0_onchip.deb**（板端 aarch64）。
- 压缩包内另有 cp38 的 Linux x86_64/aarch64 wheel，`30TAI&100TAI_win_python.zip` 内有 cp38 win_amd64 wheel；这些 Python API 包需 Python 3.8，不应与 400TAI/Python 3.12 包混用。
- 还包含 DecoderDLL 及第三方依赖安装包，按模型/应用实际需要选用。

来源：板载Linux镜像（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/板载Linux镜像`）、交叉编译docker（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/交叉编译docker`）。

镜像 BIN 大小为 31,914,983,936 字节，约 29.72GiB；另有 `.7z` 与 imageUSB.exe。`ubuntu20.04_container.tar` 是交叉编译环境候选。它们对快速建立匹配运行环境价值很高，但本轮未挂载镜像、导入容器或确认镜像内已安装的软件版本；实际卡容量、分区和现有文件须在刷写任务时确认。

**后续进度（2026-10-03）**：已完成Lite SD启动/根分区扩容、MobaXterm SSH通信、板端Icraft与CustomOp安装，并在本机搭建Docker容器 `FPAI`、配置交叉编译工具链。容器所用镜像尚未提供，不能据此认定来自上述tar。安装包control核对及最新状态见第16节，前述“本轮未导入/安装”保留为初始资料整理阶段的历史说明。

### E2. 26040701：单路 PLIN + pHDMI

来源：参考包 README（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/参考实现/单路PLIN+pHDMI/fpai_demo_package_26040701/fpai_demo_package_26040701/README.md`）、BUILD_GUIDE（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/参考实现/单路PLIN+pHDMI/fpai_demo_package_26040701/fpai_demo_package_26040701/docs/BUILD_GUIDE.md`）、API_REFERENCE（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/参考实现/单路PLIN+pHDMI/fpai_demo_package_26040701/fpai_demo_package_26040701/docs/API_REFERENCE.md`）。

包头标注平台 ZG、AI Mate **25122301**、Icraft **3.36.0**，打包时间为 2026-04-07。包含无 AI 的 `0_datapath/PLin+HDMI` 与 `1_single_input+ai/PLin+SingleNet+HDMI`。先验证数据通路、再加入网络有助于缩小联调故障范围，但这仍是待讨论的开发路线，而非本次选定基线。

2026-10-15使用既定资源重新核验：Lite25122301 `BOOT.bin` SHA为`ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`，与历史板端记录一致，配对.bit配置载荷对应；38份来源及三份重复头身份已保存。参考例的输入初始化藏在SDICamera构造；项目参考RTL中输入可编程VTC不等同HDMI扫描，后者固定1080p及读帧长度，无SDI未锁定时cam_clk fallback值得优先核实。参考RTL与该BOOT的构建对应、实际像素/串行时钟及安全换帧/停止仍未证。本轮只做本机离线分析，无板端操作；详见资源分析报告（历史附件，当前仓库未附：`tools/pose-v1/evidence/hdmi-resource-audit-20261015-r1/REPORT.md`），不将线索或历史哈希当新实屏通过。

API 文档解释 Pipeline + Actor：输入、NPU、输出/后处理各阶段在线程和队列中协作，MessageMeta 的 buffer_index 用于定位缓存，BufferManager 管理内存流转。它有助于理解吞吐、缓存生命周期、时间戳和显示叠加，不能仅凭“零拷贝”描述认为所有阶段都无数据复制。

### E3. 26040702：单路 PLIN + VPU

来源：参考包 README（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/参考实现/单路PLIM+VPU/fpai_demo_package_26040702/fpai_demo_package_26040702/README.md`）、VPU 示例 README（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/参考实现/单路PLIM+VPU/fpai_demo_package_26040702/fpai_demo_package_26040702/examples/1_single_input+ai/PLin+SingleNet+VPU/README.md`）。

实际例子是 `0_datapath/PLin+VPU`、`1_single_input+ai/PLin+SingleNet+VPU`，用于视频编码输出；外层目录拼作“PLIM”。当作品需要编码视频、网络传输或存档时具有参考价值，不等于 Lite 有 SDI 输出。

文档有拷贝残留：包头仍写 pHDMI 用途，快速开始仍指向 HDMI 路径；包头标 3.36.0，示例 README 又写 3.33.1 并链接旧版位流。不能依据其中单一字段决定最终编译依赖与位流。

### E4. 下载区 Lite 25122301 位流候选

来源：悟净LITE版_BOOT_25122301_单路PLIN+pHDMI(外置detpost)（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/参考实现/位流/悟净LITE版_BOOT_25122301_单路PLIN+pHDMI(外置detpost)/悟净LITE版_BOOT_25122301_单路PLIN+pHDMI(外置detpost)`）。

实际包含 BOOT.bin、ai7030_top_disable_icap.bit、FSBL251210_ddr400_demo.out、bl31.elf、u-boot、Image、fmqlmp-verify.dtb 和 uEnv.txt，是启动组件集合，不只是孤立 FPGA 位流。

`uEnv.txt` 里串口为 115200，root 指向 mmcblk0p2、mem=1024M；`bootcmd` 先执行 `loadbit`，而 `loadbit` 从 **mmc 0:2 读取 download.bit**，随后内核/设备树从 0:1 加载。当前解压目录中未见名为 download.bit 的文件，只有 ai7030_top_disable_icap.bit。

它与 D1 的“替换 FAT 分区 BOOT.bin”流程存在差异。缺少实际板端启动布局证据，不能自行决定重命名、放入哪个分区或修改启动命令；应在确定参考位流后讨论并核对实际启动链。

### E5. 完整版流水灯工程：工具链验证价值高，上板适用性有限

来源：FPGA_LED_Wujing_Full/README.md（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/FPGA_LED_Wujing_Full/README.md`）、build.tcl（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/FPGA_LED_Wujing_Full/build.tcl`）、procise.stdout.log（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/FPGA_LED_Wujing_Full/output/procise.stdout.log`）。

目标 JFMQL30TAI676H，使用 100MHz PL 时钟，每 0.25 秒轮换 LED；build.ps1 在英文路径创建工程，build.tcl 展示 create_project、add_design_file、set_top、load_design、launch_run 等流程。日志记载 Procise 2025.1.1 temp、SVN 32494、2026-03-20 构建，可作为指定安装包的历史使用证据。

README 报告 setup slack 4.740ns、hold slack 0.170ns，但明确物理时钟输入引脚尚未锁定，I/O 电平沿用默认值。新增 B4 已给出 Lite PL_100MHz→AC14、LED 的 BANK33/34→1.5V，可为后续适配提供图纸依据；这不会自动补齐该历史工程或验证其位流。本轮只查阅记录，没有重建/上板。该例可参考 RTL、Tcl、日志与英文路径构建方式；现成位流不能视为 Lite 可直接使用的已验证结果，且纯 PL 位流不会自动保留 AI_MATE/NPU 配套通路。

### E6. 其他软件分发件

来源：下载区 Procise（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Procise`）。有人工确认的 2025.1.1 temp EXE/RAR，另有 `FMSH_VultureHWDT_2026.1_202609151421_4029.exe/.zip`。VultureHWDT 本轮仅发现分发件，未发现可据此确认功能、替代关系或兼容性的说明，不能将其认定为必须安装的软件。

## 8. 按问题查资料

| 遇到的问题 | 首查 | 补充查阅/需要取得的证据 |
| --- | --- | --- |
| 作品是否满足比赛要求、怎么留实验材料 | C1、C2、C3 | 后续正式通知、软硬件划分、性能对比与 AI 工具记录 |
| Lite 是否有某接口、引脚/电平是什么 | B1、B4、B2、D3 | B4 网络→U1 管脚→BANK 供电；实际板卡；MIPI/GPIO 冲突先讨论 |
| 30TAI 为什么还需要 Vivado/JFM 补丁 | D1、D2、D5 | 当前参考工程 XPR、脚本、补丁与时序库版本 |
| Procise 无法启动、下载器找不到 | 安装/初始化、驱动/下载手册 | 设备型号、连接、启动模式、驱动和错误日志 |
| 综合语法、黑盒/IP、原语问题 | Verilog/原语手册、D5 | 区分原生 RTL 与 Vivado 网表迁移流程 |
| 引脚或 XDC/FDC 转换报错 | 约束手册、I/O Planning、B4、D3 | 真实顶层端口、BANK 电平、板版、约束顺序和转换日志 |
| 首次流水灯/按键验证或 100MHz 引脚缺失 | B4.2、B1、E5 | AC14 时钟与 LED/KEY 1.5V BANK；核对板卡及极性后再适配约束 |
| GPIO/MIPI 电平或 XADC 通道不清 | B4.3/B4.4、B1、第 9 节 | 不能按 HR_IO12/13 名称判断 BANK；电平冲突先讨论，XADC 图纸支持 J23→VAUX8 |
| 时序不满足、跨时钟域有问题 | 约束、时序路径、在线调试手册 | 全部时钟、setup/hold、例外路径依据、ILA 波形 |
| 自定义 FPGA 加速器如何接 PS/DDR | D2、adder RTL/C++、XRT | 寄存器协议、512bit 数据/字节使能、对齐、ready/valid、超时 |
| BOOT 更新后不生效或 Linux 不启动 | D1、D4、E4 | 实际分区、挂载、启动日志、FSBL/DTB/位流组合；不混用启动流程 |
| 模型解析/算子不兼容 | I1 框架列表、Parse、算子具体页 | 原始导出版本、opset、输入形状、失败阶段日志 |
| 精度下降 | ZHUGE Quantizer、Show、运行 | 校准数据、RGB/BGR、布局、归一化、逐层/各阶段结果 |
| 推理慢、程序被 kill | ZG330Backend、XRT、故障排查 | PS/PL DDR 各自占用、OCM/ETM、数据复制、处理各阶段时间 |
| 视频黑屏、闪屏、无摄像头输入 | B1/B4 HDMI/SDI、D1 VTC、E2 数据通路 | 视频配置、时钟、Lite GT 引脚 R6/R5；1080p60 限制及 MIPI 电平冲突须先讨论 |
| 需要视频编码/记录 | E3、VPU 能力说明 | 软件接口、编码配置、输出路径和实际吞吐 |
| 需要可靠性加固 | HRDT | 支持器件、加固对象和资源/时序代价 |

## 9. 已发现的矛盾与待确认项

本节保留讨论上下文，不把未确认内容固化成方案。已明确版本、镜像及 B4 的 30TAI 配套关系，暂不确定参考位流；已确认的结论及时更新，新发现的接口电平冲突保留待核对，后续任务依赖相应结论时先讨论。

| 事项 | 证据/不清晰处 | 当前处理与后续讨论点 |
| --- | --- | --- |
| 原理图标题栏/编号差异（配套关系已确认） | B4 文件名与芯片符号为 30TAI，标题栏为 100TAI、共 35 张，实际 28 页；与 B1 引用文件名不同 | 人工确认它是 30TAI 配套原理图；已完成补充。保留 PDF/Sheet 对照，不自行判定模板遗留或裁剪原因，也不改项目芯片基线 |
| 参考实现配套版本 | 基线 3.39.0；项目包 3.33.1；260407 包头 3.36.0；VPU README 又标 3.33.1 | 保留 3.39.0 基线，待确定参考位流后核对 AI_MATE、runtime、CustomOp、模型和设备树 |
| 板载 runtime 尚未核验 | 已确认镜像文件，但未读取运行系统的软件包版本 | 后续取得板端版本/启动日志；不假设镜像文件名代表 3.39.0 |
| 启动位流加载方式 | D1 BOOT.bin 流程；E4 uEnv 另加载第二分区 download.bit，包内未见同名文件 | 已向记录说明差异；未选择部署路线，不自动改名/改启动配置 |
| DetPost 与资源取舍 | D2 带/不带 DetPost 网表；YAML detpost=true、fpga_nms=false | 选择网表时一起讨论模型与后处理，不自行删 IP 或认定 NMS 已硬件化 |
| HDMI 默认 1080p60 | 示例配置与 B1 第 25 页提示的闪屏风险相遇 | 已说明；需核对显示设备及要求，720p60 或其他输出方案尚未选定 |
| 时钟名称与来源（新增引脚依据） | B1 配置表列“PL 200MHz”，正文有 100MHz 和 DDR 200MHz；E5 历史工程未锁定时钟引脚 | B4 明确 100MHz=AC14、差分 200MHz=C8/C7、MGT 148.5MHz=R6/R5；资料中的 100MHz 引脚缺口已补齐，历史工程未自动更新，也未上板验证 |
| XADC 通道不一致（新增电路依据） | B1 第 30 页正文将 VAUX1/VAUX8 对调，表格/图片对应 VAUX8 外部、VAUX1 电源 | B4 第 20 页支持 J23→VAUX8、PS_VCC1V5→VAUX1；记录电路证据，正式使用前核对板卡、配置及分压 |
| MIPI BANK12 电平冲突 | B1 第 28–29 页写 1.8V；B4 第 9 页 VCCO12 接 VCC3V3，MIPI HS/LP 与控制网络连此 BANK | 已向记录说明；配套图纸确认不等于冲突已解决。接摄像头或设置 IOSTANDARD 前讨论并取得实板/厂商依据，不自行选定 1.8V 或 3.3V |
| GPIO 网络名与 BANK 不对应 | B4 第 16 页接口名 HR_IO12_* 的 4 路信号在第 9 页连 BANK13/1.8V；HR_IO13_1/2* 连 BANK12/3.3V，其余连 BANK13/1.8V | 已向记录说明；按 B4.3 保留逐网络追踪记录，不能按名称或连接器电源分组直接决定实板接线电平 |
| LED 约束注释误导 | D3 LED1/2 注释写 BANK13，B4 J1/M6 属 BANK33，H7/J8 属 BANK34；两个 BANK 均图示 1.5V | 引脚与 BANK 以电路追踪记录核对；本次只补文档，未修改工程或默认 I/O 电平 |
| Lite 手册文字/目录问题 | HEADER 目录写第 31 页而正文第 27 页；USB 表头写 JFMQL100TAI | 记录原文问题，按实际正文定位，不据错误表头变更芯片平台 |
| 参考示例说明拷贝残留 | 项目 HDMI README 标题写 VPU、30TAI 位流栏 TODO；VPU 包 README 仍列 HDMI 路径 | README 不能单独作完整构建说明，需和文件树/CMake/YAML/源码交叉核对 |
| Icraft 本地文档旧内容 | 3.39.0 日志标“开发中”；旧版页与通用示例含旧版本/BUYI 参数 | 已安装版本；功能、限制按对应版本/架构与实际日志核验 |
| 芯片名称形式差异 | Lite 手册 JFMQL30TAI676H，指南也使用 FMQL30TAI676HM 等表述 | 记录来源差异；器件选择结合实际芯片标记/工具支持，不擅自替换 |
| 最新赛程与报告格式 | 本地为第一轮通知，C3 最终适用性未确认 | 保留原文日期/限制，最终提交前核对后续正式要求 |

## 10. 在线补充来源与更新方式

原始链接来源：DocsResources.txt（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/DocsResources.txt`）、开发教程网址.txt（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/开发教程网址.txt`）、参考包 README。它们是资料发现入口，不是已经阅读完毕的在线内容：

| 入口 | 用途 | 本轮访问情况 |
| --- | --- | --- |
| [悟净开发板资料库/PLIN 教程入口](https://university-program.fdwmy.com/) | 板卡、入门、配套工程更新 | 2026-09-30 浏览工具无法取得内容，保留入口，未宣称其当前资料已核实 |
| [2026嵌赛开发资料下载](https://share.weiyun.com/ZcPwQ9gq) | 厂商分发包 | 本轮以本地已下载资料为阅读对象，未遍历网盘 |
| [ICraft ModelZoo 集合](https://www.modelscope.cn/collections/icraft_modelzoo-18b52923d4854f) | 选择模型及编译配置参考 | 浏览工具无法取得内容；具体模型版本、许可、ZG330 兼容性后续再查 |
| [FPAI 参考设计项目](https://www.modelscope.cn/models/AIBS/fpai_reference_design) | 参考包来源与后续版本 | 来源于本地 README，本轮未核实在线版本 |
| [竞赛官网](https://www.socchina.net/) | 后续赛程与正式提交要求 | 已取得赛道入口页，未取得更细的后续通知 |
| [入门博客入口](https://blog.csdn.net/qq_36840004) | 启动和实操补充 | 来源于 DocsResources；辅助经验不替代本板/本版本的厂商依据，本轮未逐篇阅读 |

DocsResources 还提供复旦微官方赛事 QQ 群 **790072144**，说明可向专家反馈问题；C2 另列组委会交流群，职责不同。需要询问厂商时先整理板版、软件版本、位流/模型版本和完整日志，再评估沟通内容，不自动对外发送消息。

第三方模型、代码、IP 和参考设计应记录来源及许可，答辩区分厂商通路与自研部分；260407 参考包 README 标有“仅限内部使用”，公开发布相关文件前需要核对授权范围。

后续补充时，在相关章节记录新版本、来源、适用板版、验证状态和人工确认结果；如果一次上板实验验证了某组合，应把“资料记载/待确认”更新为具体环境下的实测结果，并保存对应配置与日志，而不是只覆盖旧结论。

## 11. FPGA 开发资料充分性评估（2026-09-30）

本节基于再次阅读本索引、D1/D2、Procise 仿真/语法资料，以及复查 XPR、约束、关键 RTL/C++、JFM 脚本和本机部分工具路径形成。它是开发准备评估，未运行综合、仿真、位流生成或下载；没有改参考工程、安装软件或选定参考位流。

### 11.1 总体结论与适用范围

**已有资料足以启动 Lite 基础 PL 工程、独立 RTL 功能模块的设计和验证准备；接入 PS/PL DDR、AI_MATE 或完整视频系统有明确参考入口，但尚不足以确认一套可复现、可直接上板的系统基线。** 新增 B4 后，基础时钟/LED/按键的引脚依据已补齐；当前主要不足集中在工具版本与补丁状态、示例的适用边界、仿真环境、系统配套和实板验证证据。

应区别三类事项：资料未提供足够细节，需要补资料；资料已有但本机环境未验证，需要环境检查；源码/配置已有但未在当前 Lite 上复现，需要实验。不能将三类情况一律称为“缺资料”，也不能以资料齐全代替实验结果。

| 开发内容 | 现有依据 | 充分性判断 | 还需要的内容或证据 |
| --- | --- | --- | --- |
| 建原生 Procise PL 工程，时钟/LED/按键验证 | B1/B4、Procise /约束手册、E5 Tcl/构建记录 | 可以开始设计；不必先解决 AI 参考位流版本；已验证 Alinx 连接与芯片识别 | 用明确引脚/电平重新建立 Lite 约束；核对本次配置所需启动模式；实际构建与功能验证 |
| FIFO、状态机、定点运算、流式预处理等独立 RTL | Procise 语法/原语/仿真资料、参考 RTL | 足以按明确功能规格开始 | 明确输入输出、位宽/符号、吞吐/延迟、溢出处理；建立自校验 testbench；确认可用仿真工具 |
| PLL/DDR/SDI 等含 IP 的参考工程复现 | D1/D2/D3/D5、BD、XCI、PS_AI IP、EDIF | 文件基础较完整，工具与补丁状态未闭合 | Vivado 2018.3 或厂商认可的替代版本；正确 JFM_PATH、30TAI 时序库、OOC/IP 和 hook；构建日志 |
| PS 寄存器控制新增 PL 模块 | D2、adder RTL/C++、XRT | 接口入口明确，可设计寄存器协议 | 选定系统基线后核对地址映射、时钟/复位、软件 API；定义 busy/done/error、重复启动和超时恢复 |
| PL DDR 数据搬运与较大规模计算 | D2 512bit 接口、B4 DDR、D3 MIG/RTL | 能理解接口，adder 小示例不足以作通用 DMA 规格 | 通用地址与长度、字节使能、读写完成语义、背压、对齐/尾部、缓冲区管理、实测带宽；见 11.2 |
| SDI→预处理→AI→HDMI 系统 | D1/D2/D3、E2/E4、B4 | 有较直接参考实现，版本/启动链/性能未验证 | 参考位流与对应可编辑工程、AI_MATE/runtime/模型配套；显示设备和输入源；当前资源/时序、端到端测试 |
| MIPI 摄像头或 J17 GPIO 扩展 | B1/B4、部分参考通路 | 电平冲突影响接线和约束，不能直接实施相关部分 | 先讨论第 9 节冲突；取得实板/厂商电平依据，再补外设型号、协议、驱动与时序资料 |
| 将新增算子纳入 Icraft 模型编译/调度 | I1/XIR/CustomOp，D2 PL 接口 | PL 可由 PS 控制的依据已有；ZG330 模型内自动调度新硬算子的完整流程未确认 | 30TAI/ZG330 3.39.0 对应的扩展示例、后端/适配/调用约定与验证；不能照搬 BUYI 示例 |
| 自建 PCIe/SFP 协议或重做 DDR 控制器 | B1/B4、部分原语/IP 资料 | 板级连接可查，尚未建立完整开发依据 | 按具体用途补协议/IP 支持、外部设备时序、驱动、时钟复位和测试环境；不能由引脚齐全推导出功能可直接实现 |

原生 Procise RTL 流程与 D1 的 Vivado→JFM 补丁→Procise 流程需要分别理解：基础独立 PL 设计可依据原生流程；含厂商 BD/IP/AI_MATE 的系统工程以其指定前端和迁移流程为依据。不能把参考工程中的 SystemVerilog/VHDL/IP 直接当成本机原生综合已支持的全部语法。

### 11.2 本次源码与环境复查的新发现

1. **XPR 的补丁引用尚未就绪。** 按 XPR 中 `$PPRDIR` 和 `$PSRCDIR` 解析检查了 101 个 `File` 条目，8 个指向工程内 `ip_patch/process_control/*.tcl` 的文件当前不存在，其余 93 个条目存在；BD 与 `PS_AI IP` 目录均存在。缺失引用涉及 synthesis_pre、implementation_opt_pre/post、implementation_place_pre/post、implementation_route_post、write_bitstream_pre/post。JFM_Kits 的 process_control 目录能找到其中 6 个同名脚本，未找到 place_pre/post 同名文件。run.tcl（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/JFM_Kits/JFM_Kits/ip_patch/run.tcl`） 有按 JFM_PATH 复制补丁的逻辑。应按 D1 重载 hook 后核对有效引用和运行步骤；目前既不能将旧 XPR 当作开箱可构建工程，也不能仅由这 8 个引用认定整包缺失核心 RTL 或一定无法复现。
2. **本机前端版本尚未匹配。** 已找到 `D:\Xilinx\Vivado\2019.1\bin\vivado.bat`；人工确认没有安装 Vivado 2018.3。D2 明确参考 FPGA 工程仅适用于其指定 Vivado 版本，XPR/历史日志为 2018.3，尚无认可 2019.1 替代的依据。**不要由助手执行下载，Vivado 下载人工执行。** 基础原生 Procise RTL 开发不以安装 2018.3 为前提；复现 D1/D2 工程时需要先讨论匹配版本，不擅自升级工程、IP 或时序库。
3. **验证用资料不能替代 testbench。** XPR 的 `sim_1` 没有 `File` 条目，顶层配置仍为 ai7030_edif_top；检索到的 tb_smpte_sdi/tb_v_smpte_sdi 文本是 IP 内存初始化文件，不能作为新增模块的验证计划。Procise 仿真手册提供第三方 ModelSim 调用及编库步骤；本次 PATH 未检出 vsim/iverilog/verilator，不等于这些工具一定未安装，也未确认许可证或仿真库可用。已确认 `D:\Xilinx\Vivado\2019.1\bin` 下 xvlog.bat、xelab.bat、xsim.bat 存在，可作为纯 RTL 模块仿真的环境候选，尚未验证运行；它们存在并不证明 2018.3 系统参考工程可在 2019.1 直接复现。AI_MATE EDIF 不应自动视作完整可用的功能仿真模型，必要时对接口建立行为模型并单独验证新模块。
4. **adder 数据宽度是演示用法。** ai7030_edif_top.v（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/rtl/ai7030_edif_top.v`） 的 User_Ddr 总线为 512bit，但 adder_top.v（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/rtl/adder_op/adder_top.v`） 的读写数据端口为 64bit，计算只读取低 32bit；adder_demo.cpp（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_app/examples/1_single_input+ai/PLin+SingleNet+HDMI/src/adder_demo.cpp`） 每个输入占用一个 64 字节槽，只检查该槽的低字节。顶层写字节使能设置为全 1。应明确处理截断/扩展、上位数据及写掩码，不能认为该演示每拍处理了 64 字节有效算法数据。
5. **adder 地址和计数不能直接推广。** reg_ctrl.v（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/rtl/adder_op/reg_ctrl.v`） 将基地址/长度分别放在一个 32bit 寄存器的低/高 16bit；dma.v（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/rtl/adder_op/dma.v`） 的基地址输入也只有 16bit，并每次加 64 字节。adder.v（本机留存，仓库未附：`D:/FPGACompetitionProject/Docs/26嵌赛开发/fpai_demo_fpga/rtl/adder_op/adder.v`） 内部完成计数仅 9bit，而长度端口为 16bit。大地址、大帧或长数组开发需要重新定义协议；长度是传输数还是最后索引、零长度及最后一次写完成均应仿真核验，不能直接复制小规模示例并假设覆盖任意 PL DDR 地址/长度。
6. **时钟域和完成语义需要审核。** adder_top 使用不同的 gp_clk/hp_clk，通过 pulse_cross 传递 start/done，但未连接其 rdy1，且多位配置在两个时钟域之间使用；reset_reg 的时钟与寄存器访问域也需要核对。需要验证配置稳定窗口、单次/重复启动、背压与复位中断；done 是否意味着最终结果已提交 DDR 需沿读写链核对。此处是静态检查提出的验证点，未通过仿真认定全部为已复现缺陷。
7. **时序例外与 DRC 降级不能照搬。** D3 ai7030.xdc 含具体层级的 false_path，并把 REQP-44/46/52/56 降为 Warning。修改层级/IP 后必须检查约束是否匹配对象、时钟覆盖、例外依据和实际 DRC 内容；时序被排除并不证明 CDC 设计正确，DRC 变成 Warning 也不说明其影响已消除。
8. **模型内硬算子与 PS 主动调用 PL 是不同工作量。** Icraft 自定义硬算子示例（本机路径，仓库未附：`C:/Icraft/CLI v3.39.0/docs/demo/samples/customop/hardop.html`） 明确围绕 BuyiBackend 展开。D2/adder_demo 能支持 PS 配置寄存器、PL 读写 DDR 的开发入口，但没有据此证实 ZG330 3.39.0 可以直接套用 BUYI 模型内扩展流程。若比赛功能只是独立预/后处理并由 PS 协同，可先按对应接口设计；若要求算子嵌入模型图、自动适配与调度，需先补对应平台依据并讨论。

### 11.3 开发中预计遇到的问题及验证内容

| 问题 | 需要关注的内容 | 优先资料与应取得的结果 |
| --- | --- | --- |
| 工程打不开、IP 失效、黑盒或不支持语法 | 英文工作路径、工具版本、文件引用、OOC、PS_AI IP、JFM hook、代理器件与目标器件 | D1/D3/D5、Procise 语法/原语；完整构建日志、未解析模块清单 |
| 位流能生成但板上没有反应 | 顶层/引脚、电平、时钟频率、复位极性、启动模式、JTAG 链、实际加载的是哪个位流 | B1/B3/B4、驱动/下载手册；器件识别、下载日志和可观察基础功能 |
| 功能仿真通过但时序或 CDC 出问题 | 生成时钟、复位释放、同步器、异步 FIFO、脉冲与多位配置跨域、约束对象 | 时序/约束/在线调试手册、D3；setup/hold、未约束路径、CDC 审核与 ILA 波形 |
| DDR 数据错误、死锁、完成后结果未写完 | 地址单位、64 字节对齐、位宽、掩码、背压、最后传输、缓存所有权和软件生命周期 | D2、11.2、XRT；自校验读写、随机背压、边界长度及超时恢复 |
| 自定义逻辑挤占 AI/视频资源 | 已有 AI_MATE/DDR/SDI/HDMI 占用、时钟与布线、DSP/BRAM、频率目标 | D2/D3、实际实现报告；先取得系统基线资源/时序，再预算增量，不能把 125K/400 DSP 全当空闲 |
| 黑屏、花屏、帧错位或吞吐不足 | 视频时序、RGB/BGR/YCbCr、像素位宽、跨域、缓存、显示限制、AI 预处理一致性 | B1/B4、视频 RTL、D1 VTC、E2；输入/输出各阶段帧率、数据一致性和端到端延迟 |
| Linux/AI 在更新 PL 后异常 | 独立 PL 位流是否包含原系统逻辑、FSBL/DTB/BOOT、实际加载路径、runtime/AI_MATE/模型配套 | D1/D4/E4、I3；启动日志、运行时版本和已验证组合。独立测试位流不会自动保留原 AI 通路 |
| 比赛难以证明 FPGA 的贡献 | 软件/硬件等价输入、精度与定点误差、搬运开销、资源时序、稳定性和复现 | C1/C3；参考输出、自校验测试、性能对比及配置/源码/日志归档 |

对新模块的有效验证应覆盖正常输入、边界输入、随机背压、复位/重复启动、溢出/符号位及超时；根据具体模块选取，不为无关功能增加测试。综合成功、位流生成和上板通过分别记录，不能相互替代。

### 11.4 下一阶段可讨论的推进顺序

以下是建议顺序，尚未替配置采用开发目标、构建路径或系统位流：

1. 本次 FPGA 功能、输入输出及验收指标留待顶层架构讨论；板卡无 SD 上电、Alinx 连接和两套工具芯片识别已有人工确认，后续关注具体功能验证与仿真工具情况，不重复要求确认已完成的连线/识别工作。
2. 若先做基础 PL：在约定的英文工作目录建立 Lite 时钟/LED/按键小工程，显式约束 AC14 与 1.5V LED/KEY，再验证构建、时序及下载链。
3. 对比赛功能先写独立 RTL 和软件参考结果，做自校验模块仿真；若涉及 MIPI/GPIO 冲突，先讨论解决对应电平依据。
4. 若需要 AI/DDR/视频系统集成：先确定参考工程、位流及配套版本，恢复迁移脚本和 IP，复现未改动基线，记录资源/时序与运行结果。
5. 再接入新增模块，逐项核对寄存器、DMA/流接口、时钟复位、软件调用和端到端性能，并保留可恢复的已验证基线。

当前最优先补齐的是具体开发目标、可执行的工具/仿真环境和实板状态；系统扩展还需要选定可复现的参考基线。无需为了基础 RTL 开发等待所有高级接口资料齐全；也不能在基线未闭合时承诺任意 AI/视频功能可直接上板。

### 11.5 面向 CSI→3D 人体姿态建模的补充评估

系统目标：作品目标是基于 **Wi-Fi CSI（Channel State Information，信道状态信息）** 实现 3D 人体姿态建模；CSI 滤波降噪、部分算子加速、高速 DMA、FPGA HDMI 骨架输出均为当前想法，**不要求全部实现，也尚未选定具体 FPGA 功能**。板卡已到手，SD 卡预计 2026-10-01 到，目前优先考虑 FPGA 侧准备。人工确认无 SD 卡开机及 Alinx 黑金连线上板测试已完成，Procise/Vivado 均能识别芯片；xsim 已发现入口但尚未由本助手运行验证。

**当前将采集设备/接入接口/格式、姿态模型与相关算法规格留空，后续在项目顶层架构设计时给出并讨论。** 这是有意延后的架构工作，不作为当前基础 FPGA 准备的阻断项；不自行选择滤波算法、算子或采集硬件，不在当前阶段继续要求补齐这些内容。B1/B4 的摄像头 MIPI CSI 资料不能直接作为 Wi-Fi CSI 数据采集协议；MIPI 电平冲突只有选用该接口时才影响实现。

| 候选方向 | 已有可用内容 | 面向本项目还缺什么 | 当前可达到的阶段 |
| --- | --- | --- | --- |
| Wi-Fi CSI 输入和滤波降噪 | RTL/定点运算、FIFO、PS/PL 接口及硬件连接资料 | 设备与传输协议；复数 I/Q 或幅度/相位等格式；子载波/天线/时间维度、采样节奏、滤波方法与模型训练时的预处理，均暂留空 | 可以准备通用流接口与验证方法；未确定上述规格前不能给出正确的项目滤波实现 |
| 部分算子加速 | D2 的 PL custom op 接口、adder 示例、DSP/BRAM/流水线依据、Icraft 模型分析资料 | 实际模型、主要耗时层、支持算子、张量布局/量化尺度/精度、数据路径；是否由 PS 调用或嵌入模型调度 | 可以评估候选计算模块；不能仅凭存在 PL 接口保证推理提速，ZG330 模型内扩展流程仍需依据 |
| 高速 DMA / 数据搬运 | D2 512bit PL DDR 接口、寄存器访问、示例 DMA、MemChunk API | 数据源与目标、持续/突发带宽、缓冲区/缓存管理、并发与所有权、实际链路限制；通用地址/长度和背压协议 | 可以设计和模块仿真；系统测速需要配套基线和软件；若跨采集设备/PS/PL/NPU，不能把一条 PL DDR 接口当整个链路 |
| HDMI 骨架输出 | B4 HDMI 引脚、D3 TMDS 编码/串行化、视频时序与帧缓存 RTL、已有 PS DDR 显示路径 | 模型输出关节数/顺序/坐标含义、骨架连线、3D 到 2D 的投影、显示视角/尺寸/刷新；PL 画线或 PS 渲染的划分 | HDMI 输出骨架有参考基础；现有相机画面/检测框示例并不是已实现的人体骨架渲染器；分辨率先按限制讨论 |

需要先打通的数据契约是：采集端输出→预处理→模型输入→模型输出→骨架显示。每一段记录形状、布局、数值范围、单位/坐标系、更新频率和缓存所有权；这些是功能规格，不能由板卡手册或示例文件名替。

当前架构字段：采集设备 `待顶层架构讨论`；接入接口/格式 `待顶层架构讨论`；模型 `待顶层架构讨论`；滤波算法/加速算子/DMA 指标/显示规格 `待顶层架构讨论`。以上字段保留空缺，不从厂商 SDI/Yolo 示例推定本作品使用摄像头、Yolo、图像预处理或相同缓冲区布局。

**SD 进度更新（现场确认，2026-10-02）**：已更换卡、完成 SD 启动卡制作，并通过上板验证：串口正常输出，可登录板载 Linux。前述 SD 卡未到/启动待验证属于早期状态，当前以第 15 节为准；runtime、模型、AI 和 DMA 联调未由基本启动验证覆盖。

决定 FPGA 做哪部分，应先建立可复现的软件参考和阶段耗时：滤波是否适合流式实现、哪些模型算子是瓶颈、搬运是否占主要耗时、显示是否需要 PL 独立生成，再讨论实现成本与收益。所增加的搬运、CPU/PL 同步和精度损失都应计入比较，不只看单个 RTL 模块频率。当前不需要四个候选项同时开发。

SD 卡未到不阻止 RTL 设计、testbench、约束准备、综合/实现准备；已完成 JTAG 连线/器件识别，后续可结合本次板级模式讨论独立 PL 的易失配置和功能验证。Linux/runtime、模型推理、PS 应用与端到端 DMA 联调则需要可用运行环境和版本基线。是否采用独立 PL 测试或系统工程集成仍须按项目目标讨论，不把前者的成功当作 AI 系统已通。

## 12. Procise 平台与 Vivado MCP 接入可行性（2026-09-30）

### 12.1 平台边界和新验证状态

技术约束：本次 FPGA 开发平台是**复旦微 Procise**；Vivado/Xilinx 与 Procise 在上层开发方法上高度相似，但底层芯片和 IP 需要适配。已将这一点写入 AGENTS.md 作为执行规范。已完成无 SD 卡开机、Alinx 黑金下载器连线及上板测试，Procise/Vivado 均能识别芯片；该项是现场反馈的实板证据，本助手本轮没有重做测试，也没有据此宣称特定位流、Linux、DDR 或 AI 已验收。

| 层次 | 可以借鉴的内容 | 仍须按 Procise/30TAI 验证的内容 |
| --- | --- | --- |
| 算法、RTL、接口 | 流水线、状态机、握手、FIFO、定点算法、testbench 的方法 | 原生综合支持语法、推导结果、复位/CDC、最终资源和时序 |
| 约束与工程流程 | 时钟/输入输出/例外约束的设计思路，部分相同命令形式 | FDC/转换、对象层级、加载顺序、器件引脚/BANK、工具实际支持命令 |
| IP 与原语 | 功能规格、端口和参数含义 | PLL/MMCM、DDR、GT、PS、调试核等的复旦微替换/迁移、补丁和时序库 |
| 报告、位流与下载 | Vivado 前端报告可作为阶段证据，器件识别可证明连接状态 | 复旦微目标上的布局布线/时序、合法位流、下载与实际功能；Vivado 普通位流不等于可用 Procise 位流 |

### 12.2 MCP 能带来的收益与限制

MCP 在这里是把本地 EDA 操作以工具接口提供给智能体的连接方式。它可以让工具调用参数、任务状态和报告结果更明确，减少 GUI 操作、反复启动和手工搬运日志；持久会话、错误分类、原始报告落盘与结构化查询有潜在效率收益。是否比现有脚本更快，需要实际比较，本次未测量速度或准确率。

准确率的收益主要来自能读取**真实工具状态和证据**，而非 MCP 协议本身。若包装层解析错报告、使用旧结果、查询错设计阶段或沿用错误器件/IP，结构化输出也可能误导。应保留后端工具/版本/目标器件、设计阶段、输入文件摘要、时间及原始日志路径；字段缺失记录为 unknown，不能按 0 或通过处理。

本会话已有 shell/文件工具，能运行经核验的 Procise Tcl 并分析报告；MCP 不增加原本不存在的芯片支持，也不是开始 FPGA 开发的前提。针对本项目，最有价值的接口应围绕 Procise 构建与验证，其次才是 Vivado 前端辅助。

### 12.3 公开 Vivado MCP 实现的比较

目前尚未指定具体仓库，以下按公开实现比较，未选定/安装。查询了当前可用工具和 Plugin Management 目录，本次未找到现成可调用的 Vivado/Procise 集成；目录检索结果不等于全网不存在此类工具。

| 实现 | 查阅到的特征 | 对本机/本项目的判断 |
| --- | --- | --- |
| [mapleleavessssssss-wq/vivado-mcp](https://github.com/mapleleavessssssss-wq/vivado-mcp) | 支持 Windows/Linux 和 GUI/Tcl/attach；作者以 2019.1 为主要支持基线，2018.3 只验证部分 IP 元数据路径；可查询 IP、波形和结构化报告 | 与当前 2019.1 前端环境较贴近，可作为辅助候选；不能据此确认 D1 的 2018.3+JFM 全流程兼容，也没有证实 Procise 适配 |
| [Arthurzxy/vivado_mcp_native](https://github.com/Arthurzxy/vivado_mcp_native) | 使用原生 subprocess 管理持久 Vivado Tcl 会话，提供 Windows 支持、报告与仿真操作；包名是 vivado-mcp-native | 可作为 Windows 会话自动化候选；其命令仍面向 Vivado，不是 Procise 后端 |
| [coreyhahn/vivado_mcp](https://github.com/coreyhahn/vivado_mcp) | 使用 pexpect 与 Vivado Tcl 提示符交互，支持工程、报告与流程工具 | 在原生 Windows 上要额外核对传输实现；不作为当前环境首选，不能只替换程序路径就用于 Procise |
| [newtonsart/vivado-mcp-server](https://github.com/newtonsart/vivado-mcp-server) | Vivado 内 Tcl 插件通过本地 TCP 与 Python MCP 通信，可控制已打开会话；含 Hardware Manager 操作 | GUI 会话接入有参考价值，但需修改加载配置并核验版本；Xilinx 硬件调试操作仍不能视为复旦微适配完成 |

以上为 README/部分源码静态核验，支持声明属于各项目作者提供的范围，不等于在本机验证。项目名称、PyPI 包名和版本不能混用；接入前须固定具体仓库/提交或版本。本轮只通过浏览工具查阅公开文档和源码，未下载软件、运行安装脚本或修改 MCP/Vivado 配置。

### 12.4 为什么不能把 Vivado MCP 直接当 Procise MCP

公开代码可见：[coreyhahn 的 server.py](https://github.com/coreyhahn/vivado_mcp/blob/master/server.py) 使用 `open_project`、`launch_runs synth_1/impl_1` 和 `report_timing_summary` 等 Vivado 操作，报告解析也按 Vivado 字段进行。[其会话代码](https://github.com/coreyhahn/vivado_mcp/blob/master/vivado_session.py) 按 Vivado 启动参数与提示符管理进程。仅将 VIVADO_PATH 改为 Procise 的 exe，不会转换这些假设。

本机 Procise 用户手册第四节明确提供 Shell/Tcl、RTL 与 EDIF 流程，Tcl 工程创建使用 create_project/add_design_file/set_top/load_design/launch_run；典型推进命令为 `launch_run -stage bitstream`，与 Vivado 的 `launch_runs` 不相同。E5 的 build.tcl 是当前工具相关的历史使用参考。该手册还提示跨不同工程时建议重启 Procise Shell，说明也不能无条件照搬一个永久复用所有工程的会话模型。

此外，Vivado MCP 自动执行普通 synth→impl→bitstream 时不一定遵循 D1 要求的 JFM hook、30TAI 时序库、OOC 和特殊步骤。必须审核实际命令链；“MCP 工具调用成功”“Vivado 前端时序通过”“Hardware Manager 识别成功”均不能替代复旦微后端适配与验收。

### 12.5 推荐路径与验证方式

**建议：以 Procise 脚本/报告闭环作为主开发路径；Vivado MCP 可作为范围明确的辅助试点，不作为必须先安装的组件。** 若未来反复构建、查询和诊断的成本明显上升，可把已验证的 Procise 自动化包装为本地 MCP，再按实际需要增加 Vivado 前端工具。

| 路径 | 作用 | 当前可行性 |
| --- | --- | --- |
| Procise Tcl + 现有 shell 工具 | 目标器件构建、实现、报告和位流证据 | 有本地手册和历史脚本依据；仍需在本机/本工程验证，当前无需先引入 MCP |
| 小型 Procise MCP 适配层 | 对经核验的命令提供环境检查、构建任务、进度、报告、产物查询 | 技术上可设计；首版可用独立作业进程，避免先依赖未验证的持续交互会话；报告解析和命令支持需测试，不在本轮擅自开发 |
| Vivado MCP 辅助 | 参考 XPR/BD/IP 参数检查、纯 RTL/XSim、前端报告整理 | 可作候选；明确版本与工作副本，普通 Xilinx IP/实现结果须经过 Procise 适配 |

[官方 MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) 确认 Codex 支持本地 stdio 服务和按工具限定可用范围，因此技术上能接入这些本地服务器；这只证明客户端连接机制，并不证明某服务器已适配 Procise。

如后续决定试点，先用独立的小工程比较 MCP 与原 Tcl 流程：核对工具/器件/顶层，运行自校验 RTL 仿真，对同一来源报告比对关键字段；明确失败、超时及旧结果处理，再验证 Procise 产生的产物。Vivado 侧硬件下载、自动 IP 升级、修改共享时序数据库等操作不能由“接入 MCP”本身推定已适配或已授权。对于 D1 系统工程，应先验证指定工具版本和 JFM 流程，再开放对应自动化能力。

本轮仅完成分析和规范更新；未安装或接入任何 MCP，未下载 Vivado。采集格式、模型和算法方向仍留待顶层架构讨论。

## 13. 悟净 Lite 原生 FPGA 流水灯实测（2026-10-01）

验证“代码→仿真→综合→上板”，并授权生成位流后直接下载；随后明确同意具体引脚/电平、0.25 秒单灯循环、独立 ASCII 工程路径、XSim 行为仿真、Procise 实现和 JTAG 易失配置方案，以及 StartupClk=JtagClk 修正。原上板灯序为 **LED1→2→3→4**。MCP 顺序为**先完成原生流程，再讨论接入**。本节记录原生历史验收；当前工作源码后续已改为 LED1→3→2→4，其 MCP 仿真/位流验证见 14.2，不扩展原上板结论。

### 13.1 源码、板级约束与证据入口

- 工程说明与复现：[FPGA/lite_led_chaser/README.md](FPGA/lite_led_chaser/README.md)。
- 原 LED1→2→3→4 的 RTL 备份：[lite_led_chaser.v](FPGA/lite_led_chaser/revisions/led_1234_before_1324/lite_led_chaser.v)；原自检 testbench 备份：[tb_lite_led_chaser.sv](FPGA/lite_led_chaser/revisions/led_1234_before_1324/tb_lite_led_chaser.sv)。当前工作源码和新灯序结果见 14.2。
- 原生约束：[lite_led_chaser.fdc](FPGA/lite_led_chaser/constraints/lite_led_chaser.fdc)。B4 原理图实际 PDF 第 9/10/21/22 页：AC14 100 MHz/LVCMOS33；J1/M6/H7/J8 为四颗 LED/LVCMOS15，BANK33/34 的 VCCO 为 1.5 V；高电平点亮。
- 脚本：[Simulate.ps1](FPGA/lite_led_chaser/scripts/Simulate.ps1)、[Build.ps1](FPGA/lite_led_chaser/scripts/Build.ps1)、[build.tcl](FPGA/lite_led_chaser/scripts/build.tcl)、[ReviewBuild.py](FPGA/lite_led_chaser/scripts/ReviewBuild.py)、[Program.ps1](FPGA/lite_led_chaser/scripts/Program.ps1)。

### 13.2 验证结果与边界

| 阶段 | 实测结论 |
| --- | --- |
| 仿真 | 本机 XSim 2019.1；自检通过。1/7/19 三种分频值各检查 200 周期，覆盖初始化、切换边界、单灯顺序、循环回绕。硬件默认 25,000,000 个周期/步，100 MHz 下 0.25 秒/步 |
| 原生实现 | Procise 2025.1.1 temp / SVN 32494；目标 JFMQL30TAI676H；综合、布局布线和位流均完成 |
| 内部时序 | setup 裕量 4.740 ns、hold 裕量 0.170 ns，内部 setup/hold 各 58 个端点，违例端点 0；无缺失时钟、未约束内部端点或组合环 |
| I/O 时序边界 | 四颗 LED 为 `no_output_delay`，原生报告标记 High；它们没有外部同步采样协议。本次保留这项记录，没有伪造输出延迟或用例外隐藏。不能推导为所有接口时序均已验收 |
| 资源 | LC 13/19650，GCDU 1/32，IOU18M 4/72，IOU33M 1/48 |
| 位流复核 | native placed FDC 五个引脚及电平正确；29 个寄存器 INIT 正确；仿真/构建/当前 RTL 哈希一致；StartupClk=JtagClk；UnconstrainedPins=Disallow |
| 上板下载 | 2026-10-01 12:06，用 Procise 下载到链中 FPGA part 0；工具返回正常，SVF 指令执行成功，STAT 回读 `0x40007ffc`；未写 Flash/BOOT |
| 肉眼功能 | 现场确认“四颗 LED 按预期循环”，本次全流程功能验收通过；未用仪器测量周期精度 |
| 其他范围 | 仅纯 RTL 行为仿真，没有复旦微网表/布线后仿真；没有 Linux、DDR、PS 应用、模型或 AI 系统验收；没有安装/调用 FPGA MCP |

最终构建与位流（使用这一份，不使用排查阶段同名文件）：

- [build-review.json](FPGA/lite_led_chaser/runs/build_20261001_120459_3fa8ba/build-review.json)。
- lite_led_chaser.bit（历史附件，当前仓库未附：`D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_120459_3fa8ba/rundir/lite_led_chaser.bit`），5,980,582 字节；SHA-256 `a443d8f4bfde85eedc9de0e0328680cbb5d06c364f1113c55b14c4c6f4475eec`。
- [原生时序报告](FPGA/lite_led_chaser/runs/build_20261001_120459_3fa8ba/rundir/lite_led_chaser_route.json)；[最终位流设置](FPGA/lite_led_chaser/runs/build_20261001_120459_3fa8ba/rundir/lite_led_chaser.bgn)。
- [仿真日志](FPGA/lite_led_chaser/runs/sim_20261001_115631_342b3c/simulate.stdout.log)；[下载及状态回读日志](FPGA/lite_led_chaser/runs/build_20261001_120459_3fa8ba/jtag_20261001_120606/download.stdout.log)；[program-result.json](FPGA/lite_led_chaser/runs/build_20261001_120459_3fa8ba/jtag_20261001_120606/program-result.json)。

### 13.3 本机命令差异与排查经验

1. `get_cable_info` 显示 Alinx 黑金为 `DIGILENT/JTAG-HS1`，VID/PID=`0403/6014`，序列号 `210512180081`。但本机 `init_chain` **实际接受 `usb-jtag-hs1`**，手册/显示名 `DIGILENT/JTAG-HS1` 返回 `Cable_type option error`。只修正命令参数格式，没有安装/修改驱动或厂商数据库。
2. 链包含 `jfmql30` part 0，IDCODE `0x9372c093`；`ps_dap` part 1，IDCODE `0x6ba00477`。程序下载对象为 FPGA 的实际序号 0，不是按链中器件数量填值。
3. `launch_run -stage bitstream` 默认生成 `StartupClk=Cclk`。本机用户手册说明 JTAG 启动应选择 JtagClk；追加原生 `bitgen lite_led_chaser.bit -g StartupClk:JtagClk`，并核对 `.bgn`。
4. `save_project`/构建过程涉及目录切换；本机 `launch_run` 结束后回到工程根目录，追加 `bitgen` 必须先显式 `cd rundir`。首次追加命令在根目录生成另一份同名文件，复核门禁发现 `rundir` 文件仍为 Cclk 后停止下载；修正目录后重新构建，通过复核才下载。
5. 退出码、Tcl 完成标记和“文件存在”不足以独立判断成功。本次保留真实日志、原生报告、源码/位流哈希，下载前扫链并核对器件/序号，使用复核过的明确绝对路径。

已验证命令：

```tcl
get_cable_info
init_chain -cable_type usb-jtag-hs1 -serial_number 210512180081
program_bit {已复核的绝对路径/lite_led_chaser.bit} -part 0
read_reg -part 0 -reg STAT -read
```

`logs/preflight` 中保存了版本/帮助/枚举/扫链及失败参数的排查日志。更换板卡、下载器或连接方式时重新核对序列号、IDCODE 和链序号；当前成功不证明其他连接也可直接套用。

### 13.4 对 MCP 的新增证据与后续讨论

原生工具链现已具备可复现的 Windows 脚本与报告入口：XSim 行为仿真、Procise 独立构建进程、JSON 时序报告、位流/源码哈希、JTAG 枚举/下载/寄存器回读。由此可以具体讨论小型 **Procise MCP 适配层**，而不是假设将 Vivado MCP 的 exe 路径换掉即可适配。

建议首轮候选能力为环境/版本查询、仿真、构建任务、报告与产物查询；下载保留显式调用和目标/哈希检查。独立作业进程已有实测依据，持久交互会话尚未验证。Vivado MCP 仍可作为 XSim 或参考工程前端辅助，不能替代 Procise 的原生实现证据。

本次尚未验证 MCP 客户端连接、协议调用、超时/取消、错误映射、解析与原报告一致性，亦未比较速度或准确率。优先采用原生工具，MCP接入另行评估；任何 MCP 开发、安装或配置变更须按 AGENTS.md 先讨论获得同意。流水灯脚本成功只证明后端基础可行，不能写成 MCP 已验证。

### 13.5 后续基线更新：Vivado MCP 已接入、以 2019.1 为准（2026-10-01）

本小节记录原生流水灯完成后的初始接入状态；后续首版实施与验证结果见第 14 节。

优先讨论 Procise MCP，将 Vivado MCP 用于仿真和参考工程辅助，并说明已自行接入 `vivado-mcp`。当前辅助工具以 `D:\Xilinx\Vivado\2019.1` 下的 Vivado 2019.1 为准；资料中采用 Vivado 2018 版的项目仅作思路参考，不作为当前运行版本要求，不据此要求安装 2018 或自行升级/迁移旧工程与 IP。

本会话已发现 `mcp__vivado__*` 工具，并成功执行只读 `list_sessions` 查询，返回“当前没有活跃的 Vivado 会话”。此结果更新前文“尚无可调用 FPGA MCP”的历史状态：Vivado MCP 接口已可调用，但没有通过它启动 Vivado、运行仿真或验证 Procise 适配；尚未比较 MCP 与原生脚本的速度或准确率。没有修改 MCP 配置、参考工程、IP 或板上配置。

对 Procise MCP 的方向认可授权继续讨论，具体开发/安装/配置方案仍按 AGENTS.md 先讨论并获同意。流水灯的完成总结已写入 [Done.md](Done.md)，采用“工程内容总结＋对后续开发的参考”模板；该工程通过原生工具完成，不追溯记为 MCP 仿真/下载成功。

## 14. Procise 首版与 Vivado MCP 验证（2026-10-01）

 [首版方案](tools/mcp-validation/PLAN.md) 后已实现并验证；完整结果见 [RESULTS.md](tools/mcp-validation/RESULTS.md)，调用入口与限制见 [Procise MCP README](tools/procise_mcp/README.md)。SDK 在 `.local/procise-mcp-venv`，与已有 VivadoMcp、Icraft、训练环境分离；随后批准并写入 Procise 项目配置、增加日志 BOM 识别及执行 Vivado 临时诊断。未改系统 PATH、EDA 安装或用户级配置。

下表主要记录首版阶段证据；长期配置并自行重载两个 MCP 服务，最新当前工具会话衔接验收见 14.2，更新此前“聊天调用待验收”的状态。

| 能力 | 当前证据与适用范围 |
| --- | --- |
| Procise stdio 协议 | 官方 SDK 2.2.0 独立客户端 initialize/list/call 通过；七工具覆盖固定环境探测、原生报告、流水灯异步构建、状态/日志、产物和复核；[协议记录](tools/mcp-validation/procise-stdio-validation.json) |
| 原生构建一致性 | 最新新构建 `build_20261001_170101_78f11a` 内部 setup/hold 4.740/0.170 ns、违例端点 0，五引脚/电平、29 INIT、JtagClk、MCP 新仿真与源码哈希通过；四 LED 的 `no_output_delay` 仍列出。未下载新位流，也未替代原实板验收 |
| 报告/错误处理 | 时钟/时序/检查计数与同一原始 JSON 相等；产物哈希/大小与磁盘相等；七类非法调用返回 `isError=true`，五类缺失或矛盾报告测试通过。BGN 默认值 `*` 首次误判已修正，原失败记录保留 |
| Vivado 参考辅助 | 当前工具会话 `parse_xpr` 与原始 XML 核对通过：91 个设计文件、2 XDC、14 IP/BD、0 显式仿真文件、2 runs；part/top 正确。XML 7.39 不是程序版本，路径宏推断不等于文件存在。未打开、升级或实现旧工程 |
| Vivado 仿真辅助 | 未改安装的 `vivado-mcp 0.3.26` / SDK 2.2.0 独立客户端成功启动 2019.1、处理 Tcl 错误后继续运行，经 `run_tcl exec` 调用已有 `Simulate.ps1`，三分频值各 200 周期自检通过；[协议记录](tools/mcp-validation/vivado-stdio-validation.json)、[新仿真日志](FPGA/lite_led_chaser/runs/sim_20261001_165013_4e2b85/simulate.stdout.log) |
| 当前工具会话接入 | 首版阶段 Procise 项目配置写入后暂不重载，Vivado 仅临时 AMD64 修正通过；后续长期配置见 14.1。现已重载，当前工具会话两个服务实际启动/调用、新灯序仿真→原生位流复核通过，见 14.2 |

开发时新增注意事项：Vivado MCP 启动或 Tcl 错误正文可能伴随外层 `isError=false`，不能只凭外层状态继续；其启动失败分支丢弃已采集 stdout，空 stderr 不足以判断原因。Windows PowerShell 5.1 仿真日志为 UTF-16 BOM；`ReviewBuild.py` 已获批准支持 UTF-8/UTF-16 BOM，错误文本保留测试及 MCP 新仿真的完整复核串联通过，门禁未放宽。详见 [独立核对](tools/mcp-validation/independent-evidence-checks.json)、[编码与配置验证](tools/mcp-validation/encoding-and-config-verification.json)、[当前工具会话 Vivado MCP 验证](tools/mcp-validation/vivado-live-validation.json)。

首版作业仅在当前服务实例管理，不含取消、重启恢复、多客户端并发或任意 Tcl/JTAG；客户端超时不等于取消。MCP 约 0.016 秒返回作业 ID，完整验证约 47 秒，不能据此认定 EDA 加速或准确率提升。获益是统一入口、任务状态、范围限制及证据整合，仍有依赖/适配层维护成本。

[Procise 项目配置](.codex/config.toml)、[编码适配](tools/mcp-validation/ReviewBuild-encoding.candidate.patch)、[启动日志捕获](tools/mcp-validation/Vivado-Capture.cmd)、[子进程 AMD64 临时验证](tools/mcp-validation/Vivado-AMD64-Test.cmd) 均已获明确同意并执行。当前 Procise 重载暂不进行；Vivado 长期方案随后获实施，更新见 14.1。不能将独立协议客户端通过写成尚未重载的当前工具会话接入通过，也不能把临时验证授权扩大为其他持久环境/配置修改。

### 14.1 Vivado MCP 长期配置实施（2026-10-01）

“根据之前得到的结论和分析修改 Vivado MCP 的长期配置”，已在 用户级 Codex 配置（本机路径，仓库未附：`C:/Users/cenyongdong/.codex/config.toml`） 的 `[mcp_servers.vivado.env]` 只增加 `PROCESSOR_ARCHITECTURE = "AMD64"`。保留 VIVADO_PATH=2019.1、Python/模块入口及其余全部字段和原始字节；未修改系统环境、EDA 安装、Procise 项目配置或审批策略。写入前备份位于原配置同目录，路径及前后哈希见 [修改记录](tools/mcp-validation/vivado-permanent-config-change.json)。

验证读取 `codex mcp get vivado --json` 的实际结果启动新 stdio MCP 服务，并仅在测试父进程移除两个架构变量，模拟此前的缺失条件；AMD64 值由生效配置提供。无需临时 `.cmd`，省略 `vivado_path` 参数，直接启动配置指定的 Vivado 2019.1、回读版本及架构均通过，测试会话已关闭。[协议与验证证据](tools/mcp-validation/vivado-permanent-config-validation.json)。本次为配置/启动验证，不重复综合、仿真或上板。

长期配置写入时，已有聊天服务尚未重启，不能据文件写入认定其已加载；当时 Procise 暂不重载的选择也仍有效。随后报告已重载两个 MCP 服务，当前工具会话直接启动和协作验收已通过，更新见 14.2；本节的独立客户端记录保持历史状态。

### 14.2 当前工具会话 MCP：LED1→3→2→4 仿真与原生位流（2026-10-01）

现场反馈已重载 Procise/Vivado MCP，并明确同意 [新灯序具体方案](tools/mcp-validation/led1324/PLAN.md)。**当前工具会话实际调用验证通过：Vivado MCP 按长期配置直接启动 2019.1/AMD64、写入 RTL/testbench、驱动 XSim；Procise MCP 对同一 RTL 完成原生综合、布局布线、位流生成和复核。** 完整结果见 [led1324/RESULTS.md](tools/mcp-validation/led1324/RESULTS.md)，[实际 MCP 返回](tools/mcp-validation/led1324/mcp-calls.final.json) 和 [原报告/磁盘独立对照](tools/mcp-validation/led1324/verification.json) 均保留。

| 项目 | 本次证据 |
| --- | --- |
| 源码与仿真 | 当前 [RTL](FPGA/lite_led_chaser/rtl/lite_led_chaser.v) 为 LED1→3→2→4，100 MHz、0.25 秒/步；旧 RTL/testbench 已备份。独立预期表自检 1/7/19 各 200 周期，实际状态 `0001→0100→0010→1000→0001`；[仿真日志](FPGA/lite_led_chaser/runs/sim_20261001_182621_aa641e/simulate.stdout.log) |
| Procise 作业 | ID `5c5f8f383cd74afa87915adc67921a80`，构建 `build_20261001_183334_5f3fc1`，最终 reviewed、退出码 0；七工具均通过当前工具会话调用 |
| 原生实现与时序 | setup/hold 裕量 5.962/0.192 ns，各 58 个端点、违例 0；LC 11/19650；无缺失时钟或未约束内部端点，四 LED 的 `no_output_delay` 保留；[原生报告](FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/rundir/lite_led_chaser_route.json) |
| 产物复核 | 五引脚/电平、29 INIT、JFMQL30TAI676H、JtagClk、当前/仿真/构建 RTL 哈希相符；原报告与 MCP 字段、产物大小/哈希与磁盘逐项一致；[复核记录](FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/build-review.json) |
| 最终位流 | lite_led_chaser.bit（历史附件，当前仓库未附：`D:/FPGACompetitionProject/FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/rundir/lite_led_chaser.bit`），5,980,582 字节；SHA-256 `285356540f63f5b1a150827777f8e5e411843718976590db0cb39739b5ef7c18` |

原构建/仿真/复核脚本、MCP 服务及配置未修改；仅本次 Vivado Tcl 会话已关闭，外部 GUI 未操作。纯 RTL 前端行为验证与复旦微后端实现的衔接现有实际证据；不扩展为 Vivado Xilinx IP/原语直接可用、布线后仿真、其他项目或受控性能/准确率提升。Procise MCP 仍限定当前流水灯，暂无任意 Tcl、JTAG、取消或重启恢复能力。

**该阶段批准止于位流复核，当时新位流未上板。** 原 LED1→2→3→4 的上板记录未扩展到新灯序。下载，新位流的实板结果见 14.3；其他范围仍须依 AGENTS.md 讨论批准。

### 14.3 新灯序位流下载与实板确认（2026-10-01）

将新位流下载上板，已在复核原位流/源码哈希及当前 JTAG 链后，通过既有 `Program.ps1` 和 **Procise 原生下载工具**完成。没有修改 MCP 服务或新增下载能力，不将此环节写成 MCP 下载已验证。

2026-10-01 18:50（北京时间），下载器序列号 `210512180081`，`usb-jtag-hs1`；重新确认 FPGA `jfmql30` part 0 / IDCODE `0x9372c093`，PS DAP part 1。下载退出码 0，SVF 成功，STAT 回读 `0x40007ffc`，scan/download stderr 均为空。位流仍为 14.2 的 `285356540f63f5b1a150827777f8e5e411843718976590db0cb39739b5ef7c18`，下载前后哈希一致。

现场确认 **“灯序和速度均符合预期”**，对应 LED1→3→2→4→1、约 0.25 秒/步、单灯循环，新灯序实板功能验收通过。该确认来自肉眼观察，没有仪器周期测量或整份配置读回比对。下载是 FPGA 易失配置，掉电失效；未写 Flash/BOOT。

证据：[program-result.json](FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/jtag_20261001_184939/program-result.json)、[下载日志](FPGA/lite_led_chaser/runs/build_20261001_183334_5f3fc1/jtag_20261001_184939/download.stdout.log)、[板上核对及现场确认](tools/mcp-validation/led1324/board-validation.json)。详细步骤见 [验证结果](tools/mcp-validation/led1324/RESULTS.md) 的后续上板小节，完成总结见 `Done.md`。至此通过新灯序的 MCP 前端仿真/后端位流→Procise 原生 JTAG→实板观察流程；不扩大到其他工程、厂商 IP、Linux/AI 或 MCP JTAG 能力。

### 14.4 Vivado 真实 xlconcat IP → Procise 原生实现：实板通过（2026-10-01）

分析“利用 Vivado MCP 操作现成 IP、编写代码/仿真 → Procise 综合/位流”的可行性，并在可行时用流水灯上板，随后明确回复“同意 xlconcat 最小验证方案并执行”。**独立真实 IP 流水灯全流程已通过，现场确认“灯序、速度和单灯状态均符合预期”。** 完整结果见 [ip-reuse/RESULTS.md](tools/mcp-validation/ip-reuse/RESULTS.md)，工程入口为 [lite_led_ip_bridge/README.md](FPGA/lite_led_ip_bridge/README.md)。实施前分析、已批准范围与只读阶段记录分别见 [ANALYSIS.md](tools/mcp-validation/ip-reuse/ANALYSIS.md)、[PLAN.md](tools/mcp-validation/ip-reuse/PLAN.md)、[preflight.json](tools/mcp-validation/ip-reuse/preflight.json)。

当前工具会话 Vivado MCP 创建 2019.1 前端工程后，实际生成 `xilinx.com:ip:xlconcat:2.1` / Rev.3、四个 1-bit 输入和 4-bit 输出，写入顶层/testbench，驱动 XSim。源码闭包为顶层 → 真实综合包装器 → 未修改厂商 Verilog，均为可读源码，无新增原语/加密依赖。XSim 和 Procise 使用**同一份综合包装器与厂商 HDL**，未用 stub、funcsim、自写 IP 替身或预综合网表。IP 全部 16 种输入及流水灯分频 1/7/19 各 200 周期通过。Vivado checkpoint=0，synth/impl run 均 Not started；元数据 part `xc7z030ffg676-2` 不代表物理目标。

新工程 `FPGA\lite_led_ip_bridge` 的 Procise 原生批处理对 JFMQL30TAI676H 完成综合/布局布线/位流；当前 Procise MCP 固定旧工程，本次未扩展服务或配置。原 `lite_led_chaser` 工程、脚本和历史验收记录保留。新 build 为 `build_20261001_193157_bef06d`，对应 `sim_20261001_193106_688cd5`；setup/hold 裕量 5.962/0.192 ns，各 58 端点、违例 0，LC 11/19650。五引脚/电平、29 INIT、无遗留 IP 黑盒、当前/仿真/构建 HDL/XCI 哈希、JtagClk 和 UnconstrainedPins=Disallow 均通过；四 LED 的 no_output_delay 保留。

最终 位流（历史附件，当前仓库未附：`D:/FPGACompetitionProject/FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/rundir/lite_led_chaser.bit`） 为 5,980,582 字节，SHA-256 `00c833bb65fec1573ecf0a8cf59c45c50cff76ab7f0a3398696c43be4f608c56`。19:34（北京时间）重新扫链确认 `usb-jtag-hs1` / `210512180081`、jfmql30 part 0 / IDCODE 0x9372c093、ps_dap part 1，通过 Procise 原生 JTAG 下载成功，STAT=0x40007ffc。人工确认 LED1→3→2→4→1、约 0.25 秒/步、单灯符合预期。为易失配置，无 Flash/BOOT、仪器周期测量或整份配置读回。

入口证据：[源码与参数清单](FPGA/lite_led_ip_bridge/source-manifest.json)、[MCP 实际返回及前端最终状态](tools/mcp-validation/ip-reuse/mcp-evidence.json)、[原生复核](FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/build-review.json)、[独立核对](tools/mcp-validation/ip-reuse/verification.json)、[下载与现场确认](FPGA/lite_led_ip_bridge/runs/build_20261001_193157_bef06d/jtag_20261001_193337/program-result.json)。完成总结已按两个模板小节写入 Done.md，记录规范见 AGENTS.md。

计数器 IP 本地包含受保护 VHDL；FIFO/BRAM/Clocking/DSP 等也需核对具体原语、参数、初始化与时序语义。XCI/BD 不是直接供 Procise 原生综合的完整 HDL，DCP/stub/funcsim 也不能仅因可用于 Vivado 仿真就认定可迁移。D1 的复杂迁移还包含 Vivado IP OOC 综合、JFM hook 和 30TAI 时序库，不能称作全部综合都在 Procise；本机 2019.1 与整套 JFM 迁移的兼容性未验证。

本次结果证明这个简单明文组合 IP/配置的源码交接路线可行；Concat 在综合后已无独立 IP 单元引用，资源/时序与此前同灯序 RTL 相同，不能据此宣称加速或将成功推广到 FIFO、DMA、HDMI 等复杂核。MCP 不转换原语、库或约束。后续其他 IP 必须逐核核对完整可综合源码、语法、依赖、初始化/复位、时序与具体配置，并依 AGENTS.md 讨论批准；本次未安装补丁、加载 JFM hook 或验证 2019.1 全系统迁移。

## 15. 更换 SD 卡后的基本启动与串口登录（2026-10-02）

**最新状态（现场确认）**：已更换 SD 卡，完成 SD 启动卡制作及悟净 Lite 上板验证；串口正常输出信息，能够登录板载 Linux 系统。基本 SD 启动/串口登录已通过，不再列为当前阻断项。

证据来源是人工现场记录，保存在 [新卡现场确认记录](tools/sd-image-validation/20261002-new-card-board-confirmation.json)；本轮代理只同步文档，没有重新读取新卡、捕获串口或操作板端。平台仍采用已确认的 Lite 和镜像基线；本次没有独立核验新卡型号/全容量、实际文件系统、BOOT/位流/内核/设备树哈希或板端 runtime 版本，不能由成功登录推导 AI、模型或完整系统联调已通过。

此前旧卡的 imageUSB 校验失败、启动文件异常、更换读卡器后的失败复核及 H2testw 严重错误，保留在 [旧卡诊断报告](tools/boot-diagnostics/20261002/RESULTS.md) 和 Done.md 中，作为旧介质历史证据。它们不适用于当前新卡，换卡后启动成功也不追溯确诊旧卡精确故障。

方案倾向扩大系统分区，并明确本次代理只需提供具体命令及逐条详细解释，实际操作人工执行。人工确认：在悟净 Lite 已启动的板载 Ubuntu 中通过串口执行。扩容尚未执行/验收；需先取得实际设备名、根分区类型/挂载、剩余空间布局和工具可用性，再形成板端在线扩容命令。截图的 1.00 GB FAT、26.08 GB 第二分区、31.17 GB 未分配仅为截图布局信息，不替代 Linux 设备名和文件系统确认。

扩容命令的参考依据：[Ubuntu 20.04 growpart 手册](https://manpages.ubuntu.com/manpages/focal/man1/growpart.1.html)、[Ubuntu 20.04 resize2fs 手册](https://manpages.ubuntu.com/manpages/focal/man8/resize2fs.8.html)。growpart 扩大分区表中的分区，resize2fs 扩大 ext2/3/4 文件系统；两者作用不同。已挂载 ext4 在线扩容依赖实际内核/文件系统支持，不对已挂载根分区执行离线 e2fsck，也不自行假定根设备总是 mmcblk0p2。

### 15.1 板端只读查询结果（2026-10-03，截图）

现场提供 [串口截图](tools/sd-image-validation/20261003-board-preflight.png)：lsblk 显示 mmcblk0=58.3G、p1=1G、p2=26.1G 且 p2 挂载到 /；findmnt 明确根设备为 /dev/mmcblk0p2、ext4、rw,relatime。df 显示 /dev/root 的根文件系统约26G，已用6.3G、可用18G、26%。/dev/root 是 df 所显示的根设备名，实际扩容目标按 findmnt 的 /dev/mmcblk0p2 核对。mtdblock0/1 不是本次 SD 扩容目标。

command -v 返回 /usr/sbin/resize2fs 和 /usr/sbin/sfdisk，没有 growpart 路径；当前分区/根文件系统未扩至卡尾。以上是人工操作查询后的截图证据，代理未操作板端。实际分区表类型、扇区起始/末尾及 sfdisk 版本仍待查询；先核对再确定现有 sfdisk 是否可用于只扩大第二分区末尾的方案，不自行安装软件或执行写分区命令。参考 [Ubuntu 20.04 sfdisk 手册](https://manpages.ubuntu.com/manpages/focal/man8/sfdisk.8.html)。扩容仍未执行/验收，结构化结果已补入新卡确认记录。

### 15.2 实际分区表确认与扩容命令说明（2026-10-03）

随后提交 [分区表截图](tools/sd-image-validation/20261003-partition-table.png)，更新15.1的待查询状态：sfdisk为util-linux 2.34；磁盘为DOS/MBR，ID=0x370deffb，共62549655552字节、122167296个512字节扇区。p1 start=2048、size=2097152、type=e；p2 start=2101248、size=54687500、end=56788747、type=83。仅有这两个分区，p2之后至磁盘尾为连续未分配区域。

已依据截图形成 [逐条命令说明](tools/sd-image-validation/20261003-expand-root-COMMANDS.md)：使用现有sfdisk 2.34，先备份和no-act预演，以-N 2仅设置第二分区长度为120066048扇区，保留起始2101248、type=83、p1和磁盘ID；禁用签名擦除、不立即更新内核边界，正常重启后核对内核分区长度，再以resize2fs扩大ext4。目标最后扇区122167295，第二分区容量约57.25GiB。上述数值仅适用于本次卡及布局，不能用于其他卡。

**状态仍为命令说明准备完成、实际扩容待人工操作/验收。** 代理未连接板端、安装软件、写分区表或扩大文件系统。保持供电稳定，任何预演/写表字段不符或报错即停止；实际内核的ext4在线扩容支持未验证，不执行挂载根分区的离线e2fsck。实际输出及重启登录、df容量结果待后续补全。

### 15.3 SD根分区及ext4扩容通过（2026-10-03，人工操作/现场截图）

明确报告扩容成功，并提交 [最终串口截图](tools/sd-image-validation/20261003-expansion-success.png)，更新15.2的“待执行/验收”状态。内核识别p2为120066048个512字节扇区；根设备仍为/dev/mmcblk0p2、ext4、rw,relatime。resize2fs 1.45.5实际完成已挂载根文件系统在线扩容，报告15008256个4KiB块；两者均为61473816576字节，约57.25GiB，文件系统已覆盖扩大后的分区。

最终lsblk显示p2约57.3G且挂载/、p1约1G；df显示根ext4总57G、已用6.3G、可用48G、使用率12%，扩容前为26G总量和18G可用。本次扩容人工操作并以截图验收通过，代理只核对证据、计算和更新说明。备份/预演/正式写表完整输出未包含在最终截图中，无全容量写读、resize后额外重启或长期稳定性证据；不扩大为AI或runtime验收。详细“工程内容总结＋后续开发参考”已补入Done.md同一工作的扩容验收小节，结构化记录和命令文档均已更新。

## 16. 板端SSH、Icraft/CustomOp安装与Docker交叉编译环境（2026-10-03）

### 16.1 已完成的环境准备

同步并明确补充：悟净Lite已使用SD启动，网线连接主机，在MobaXterm通过SSH开发/通信；已将指定目录中的板端Icraft与CustomOp传输到板上并完成安装；本机Docker交叉编译环境已搭建，相关工具链已配置，**FPAI是容器名**。这些完成状态来源于陈述，不能继续把板端SSH或板端工具安装列为尚未开展。

| 环境 | 当前已知用途/状态 | 尚未独立核验的具体信息 |
| --- | --- | --- |
| Windows主机 | 既有Procise FPGA实现和Icraft 3.39.0 CLI；MobaXterm连接Lite | 本轮没有修改Windows工具基线 |
| 悟净Lite板载Ubuntu | 已SD启动、完成此前根分区扩容；SSH开发/通信；Icraft与CustomOp已安装 | 实际已安装包版本/路径、CLI或运行库加载结果、参考位流/AI_MATE及模型兼容性 |
| 本机Docker容器 `FPAI` | 已配置交叉编译环境和工具链 | 镜像名/ID、容器身份、编译器前缀/版本、sysroot、容器内Icraft/CustomOp版本、编译产物架构和板端执行结果 |
| 远程Ubuntu训练服务器 | 算法训练位置仍按此前记录说明，文件挂载 `Z:` | 不能将板端SSH地址/账号当成训练服务器的连接信息；本次未更新模型或训练规格 |

未提供的地址、账号和路径保留为空；本次未连接SSH、查询Docker或运行编译/部署。进度同步不是对新的环境修复、配置或设备操作的批准。

### 16.2 本地安装包来源与control核对

指定目录：30TAI&100TAI（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/Icraft_V3.39.0安装包/30TAI&100TAI/30TAI&100TAI`）。按E1索引读取 Icraft自述文件.txt（本机路径，仓库未附：`D:/Dowload from Chrome/嵌赛资料/Icraft/Icraft自述文件.txt`），并只读解析四份deb的ar/control.tar.xz元数据：

| 文件 | control中的Package / Version / Architecture | 资料定位 |
| --- | --- | --- |
| `Icraft_3.39.0_onchip.deb` | Icraft / 3.39.0 / arm64 | Ubuntu20.04-aarch64板端包 |
| `CustomOp_3.39.0_onchip.deb` | CustomOp / 3.39.0 / arm64 | 对应板端扩展包，人工确认安装 |
| `Icraft_3.39.0_amd64.deb` | Icraft / 3.39.0 / amd64 | 自述用于amd64上交叉编译arm64 |
| `CustomOp_3.39.0_amd64.deb` | CustomOp / 3.39.0 / amd64 | 对应主机侧扩展包；容器实际安装状态未查询 |

该核对确认**本地安装包**标识，不能替代板端/容器已安装软件的查询。`onchip`与`amd64`角色按资料和实际包架构区分；3.33.1旧工程包及3.36.0参考实现不因此改为当前3.39.0基线。E1的`ubuntu20.04_container.tar`仍只作为已有参考资料，未得到FPAI容器源镜像确认。

### 16.3 后续使用的参考与证据边界

当前已具备人工确认的Linux登录、以太网SSH通信、板端工具安装和主机交叉编译环境准备，可作为后续讨论应用开发/部署的起点。具体实施前仍需在对应任务范围内核对实际工具路径、版本、目标架构、sysroot和依赖，并以“交叉编译产物→传输→板端运行”的实际结果验收；安装完成本身不证明AI推理、模型精度、FPGA系统配套或算子扩展已经通过。

记录来源：[进度与澄清](tools/development-environment/20261003-progress.json)、[本地安装包control元数据](tools/development-environment/20261003-package-control.json)。本轮代理完成的是资料核对和项目状态记录，未替人工操作上述安装/配置，也未开始新的交叉编译或板端测试。总结见Done.md对应两模板小节，执行上下文见AGENTS.md最新进度条目。

## 17. Person-in-WiFi 3D：2026姿态迁移实验（2026-10-03）

此节更新早期“核心模型/训练服务器尚未核验”的状态。指定本机算法目录`D:\Person-in-WIFI-3D\Person-in-WiFi-3D-repo`，训练服务器目录`/public/cyd/Person-in-WiFi-3D-repo`（`Z:\Person-in-WiFi-3D-repo`），并授权通过`ssh gpu-server`分析、推送和四卡训练。已独立验证该SSH及`PersonInWIFI`环境；不是koala、双系统Ubuntu或Lite板端。

本轮从24版epoch442迁移，修正分化分支初始化与优化方式，只做14关节骨架。新代码、说明和哈希清单位于[pose26-transfer/20261003](tools/pose26-transfer/20261003/README.md)，论文与实现的逐项对应见[PAPER_AUDIT.md](tools/pose26-transfer/20261003/PAPER_AUDIT.md)。论文原文件在上述本机算法目录`paper/Person-in-WiFi_3D_Unified_Model_for_3D_WiFi_Perception.pdf`，关键内容PDF第5–6页。MLP深度、std0.001、STE初始化和本轮AdamW迁移训练参数属于复现/实验选择，不声称为论文公开配方。

已通过：169张量迁移逐元素一致；STE关闭时粗姿态与旧模型误差0；三层8头256维普通自/交叉注意力；14个残差分化分支，权重/偏置均随机近零；15-token输入、人物/关节索引、仅细化损失梯度连通；4卡短程训练和优化器断点恢复。24版在7824帧重新评估为123.085352129mm，与既有基准一致。证据见上述目录`evidence/gates`、`evidence/baseline`和`evidence/prelaunch-audit.json`。

正式训练已于2026-10-03 21:59启动：GPU1–4、每卡batch8/worker4，FP32，AdamW lr迁移2e-6/新增2e-5，矩阵wd1e-4（分化、偏置、归一化、查询/STE排除），clip0.1，分类/坐标权重2/70，seed0、固定10轮。旧代码、旧权重和旧结果保留，新结果位于服务器`result/tpami2026_transfer_20261003`。以该目录`pipeline-status.json`核对实时状态；只有训练实际结束且`final-report.json`、最佳checkpoint与曲线核对通过后才可记为完成。10轮后必须停止讨论，不自动延长。

**评估/开发边界**：维持原CSI预处理与数据划分；现有MPJPE用GT辅助greedy匹配100候选并逐帧平均，不等同真实部署人数检测准确率；逐关节、人数分组和固定匹配下细化前后误差均追加记录。坐标物理轴未确认。该训练不代表ONNX、Icraft编译、NPU推理或顶层项目架构已确定；mesh/SMPL明确排除。早期没有确认模型的文字为历史阶段，不能阻止当前明确授权的姿态训练，也不能扩展为板端部署授权。

首轮实际结果（22:10快照）：第1/10轮MPJPE126.41057mm，基准123.08535mm；同配对粗预测126.06887mm，细化尚无收益。已进入第2轮，未修改批准参数，未出现参数趋零。详见Done.md首轮补充和项目evidence；最终结果仍待10轮结束核验。

26版实验定时检查：人工确认后创建当前工具会话heartbeat（ID26），每10分钟仅检查并在完成/失败/异常时通知。10轮结果现已核验、记录并通知，随后通过应用工具停用，配置读回PAUSED；首次22:27检查为运行阶段历史状态。停止证据见[automation-stop.json](tools/pose26-transfer/20261003/evidence/automation-stop.json)，说明见[MONITOR.md](tools/pose26-transfer/20261003/MONITOR.md)，最终结果见17.1。

### 17.1 10轮实验结束与验收（2026-10-03）

23:42完成10轮/28,110步并停止，最佳第9轮122.873803893mm，相比基准123.085352129mm降低0.211548236mm（0.172%）；第10轮124.680599441mm。10次全7824帧评估、四卡一致性、563条有限诊断、126份代码/配置/列表及快照哈希、完整配置、CSV与权重哈希/元数据核对通过，进程退出。单/双/三人100.32099/123.27283/150.64941mm；最佳轮粗→细化122.79552→122.87380mm，细化未体现稳定收益。不能由小幅单seed改善认定稳定提升或分化分支作用。

完整逐关节/人数/阶段表、产物和边界见[RESULTS.md](tools/pose26-transfer/20261003/RESULTS.md)，核验见同目录evidence/completion-verification.json；最佳权重已复制至.local/pose26-training/20261003，哈希与服务器一致。前述“训练进行中”保留为历史阶段，当前已结束，后续消融/延长/部署仍需先讨论批准。

### 17.2 全新初始化500轮：论文Adam配方（2026-10-04，已启动/未完成）

本轮设计要求从头训练500epoch，并选择A论文Adam方案；原“从epoch10恢复到100轮”的建议未批准、未执行。论文PDF第7页（印刷12719）的Training Details已提取并可视核对：Adam/momentum0.9、wd1e-4、batch32、500epoch、初始lr2e-5、450轮乘0.1、focal alpha0.25/gamma2、lambda35。当前beta2/eps、clip/seed、MLP深度/std、2/70整体缩放及辅助decoder监督仍是实现选择，不宣称全部细节等同作者代码。

独立新模块`opera/models/tpami2026_scratch.py`、新配置`configs/wifi/petr_wifi_tpami2026_scratch.py`、管理脚本`tools/pose26_scratch`已部署；明确绕过migrate，不加载旧模型/优化器或外部预训练权重。模型结构复用此前经核对的STE、14分化分支和3层vanilla细化，只做14关节。旧代码/权重/10轮结果保留。

单项初始化/无checkpoint调用/索引/梯度/学习率边界门检与4卡96样本3步检查通过；129份当前源码/配置/列表及snapshot、解析配置哈希独立核验通过。2026-10-04 00:41（北京时间）已正式启动GPU1–4、每卡batch8/worker4、FP32 seed0 clip0.1、Adam统一lr2e-5/wd1e-4，无迁移分组/衰减排除，MMCV step450/gamma0.1（完成450轮后第451轮lr2e-6），500轮后汇总停止，不自动重试/延长。结果`Z:\Person-in-WiFi-3D-repo\result\tpami2026_scratch_20261004`；进程身份和实际命令见README及pipeline-launch.json。

启动验收快照已超过500步，记录有限，四个训练rank与GPU1–4负载已确认，但未完成首轮评估或500轮验收。分化L2从1.357186迅速缩小至第501步0.016044，尚未触发连续两轮严重趋零门禁；此趋势需要关注，不能根据损失下降认定精度提高。明确暂不启用定时监测，旧ID26保持PAUSED，不自行更新；会话结束后没有本项自动回查任务。错误/非有限值/索引异常、四卡不一致和连续两轮分支严重趋零由训练内置门禁中止，不自动改参数。

入口、边界与证据：[README.md](tools/pose26-scratch/20261004/README.md)、[批准方案](tools/pose26-scratch/20261004/PLAN.md)、[启动核验](tools/pose26-scratch/20261004/evidence/startup-verification.json)。独立证据为启动时快照，实时读新结果目录pipeline-status.json/train.stdout.log/branch_diagnostics.jsonl/evaluations.jsonl；后续参数/数据/部署变更仍需先讨论批准。

后续快照：第1轮2811训练步已完成，四卡一致性通过；末轮分化/细化注意力L2=0.003813/51.173392，有限但较初始化明显下降。首轮评估尚待核验，不能记为精度通过。见同目录evidence/first-epoch-training.json。

**最新检查（2026-10-04 09:08，更新前述运行状态）**：实际已于01:40:51在第6轮末触发`RuntimeError: Persistent branch collapse`，流水线为failed_stopped，无自动重试；监督/torchrun/四个rank退出，GPU空闲。5轮完整7824帧评估MPJPE依次479.294219、453.726498、439.551332、420.189946、438.772184mm，最佳第4轮；没有第6轮评估或500轮final-report。分化L2第5轮约7.30e-21、第6轮16851步约7.44e-38，分化/细化注意力梯度及分化残差为0，连续两轮严重趋零触发门禁。338条已记录诊断有限，不能把数值有限视为分支学习有效。

最佳checkpoint epoch4/iter11244全部权重有限、SHA256 eaec533377d8098dab8fa35e6104c5330840fc7d0be0658ffdc669a794213361；129份源码/快照和配置哈希通过，最佳仍保留服务器。Z盘本次不可读，已通过SSH读取和复制原始证据至项目；挂载问题与训练的01:40退化停止分开判断。当前未重启/调参/启用监测，后续修复或实验仍需批准。完整人数/关节/阶段对照见[当前结果报告](tools/pose26-scratch/20261004/STATUS-20261004-0908.md)，原始证据为同目录evidence/check-20261004-0906。

### 17.3 分化分支关闭衰减：10轮从零对照（2026-10-04，完成核验/仍有梯度退化）

**最新结果（13:06完成核验，更新下述启动记录）**：12:00:59正常完成10轮/28,110步并停止，训练进程退出、GPU空闲。最佳第6轮344.787402826mm，末轮377.942666765mm；10次7824帧评估与四卡检查、563条有限诊断、134份源码/快照及解析配置哈希、最佳/最终权重有限性及SHA256通过。最佳固定匹配粗→细化344.997972→344.787403mm，仅约0.210569mm改善。前5轮同轮对照有改善也有退步，不能将跨轮最佳差异当作稳定收益。

分化L2保留约1.908233679、查询残差非零，但第6轮15351步首次抽检到分化/细化注意力梯度同时0，第7–10轮全部抽检均0；坐标回归L2末轮约0.01530。当前权重范数门禁并未覆盖持续零梯度，本次没有修改门禁。结论限于这次单seed对照：只关分化衰减避免了分化参数归零，仍未解决整条细化通路的梯度退化，不能据此继续长训练或扩展衰减范围。

最佳权重服务器`result/tpami2026_diff_nodecay_20261004/best_mpjpe_epoch_6.pth`、SHA256 `4fb71e4a604cb064ec11a6d7de52a3190cd44ad1dc1d58c3a135bce947276def`；最终`epoch_10.pth`、SHA256 `50a5ffa2b7e9e45dd6ac5d1797fe5af91f35203360b3fed772b812a9f9ac975d`。权重保留服务器，完整同轮、人数、14关节及固定匹配表见[RESULTS](tools/pose26-diff-nodecay/20261004/RESULTS.md)，独立证据为同目录evidence/completion-verification.json和completion-20261004-1306。训练已结束，没有自动延长/重启/部署或启用监测，后续技术方案仍须批准。以下为原实现与启动阶段。

“先仅关闭分化分支衰减”的对照实验。新独立Adam构造器只将`bbox_head.transformer.joint_differentiators.`下56份权重/偏置设为wd=0，剩余参数仍wd1e-4；Refine Decoder和坐标回归仍衰减。保留原Adam lr2e-5、betas(.9,.999)、eps1e-8、初始化、结构、数据/划分、2/70损失、FP32 seed0 clip0.1、GPU1–4、每卡batch8/worker4；模型/优化器从零，不加载旧checkpoint。固定10轮后停止讨论，保留step450但本轮不会到达。旧500轮配置/源码/结果和旧10轮迁移结果保留。

单项门检通过：实际完整分组、相同初始化模块范数、无checkpoint读取、人物/关节索引及梯度；第一次零分化梯度更新前后该分支参数逐元素相等。4卡96样本3步通过，分化L2约1.357186178；短程权重丢弃。旧实验129份源码/列表哈希未变，与实际旧解析配置的差异逐项审查通过。正式134份源码/快照/配置哈希及实际监督/torchrun/4个rank通过独立启动核验。

2026-10-04 10:20:27启动，结果服务器`/public/cyd/Person-in-WiFi-3D-repo/result/tpami2026_diff_nodecay_20261004`，映射`Z:\Person-in-WiFi-3D-repo\result\tpami2026_diff_nodecay_20261004`；监督70223、torchrun70234、rank70239–70242，后续操作前重新核对身份。10:21:30启动快照第251步分化L2=1.564860762、梯度/残差非零、已记录诊断有限，首轮评估未完成。此为运行/分支初期证据，不是精度改善、10轮完成或长期稳定验收。

每轮仍评估7824帧、人数/关节/固定匹配粗细化误差，并记录参数/梯度及四卡一致性；非有限值、索引错误、DDP不一致和连续两轮严重分支趋零门禁保留。10轮后生成最佳/最终权重、final-report、CSV/曲线及与全衰减从零实验前5轮的同轮对照；目前待完成/独立核验。24版已收敛基准只是参考，不能作为10轮从零结果的公平终局比较；单seed且关闭衰减不保证细化有效。论文衰减规则的偏离明确记录。暂不启用定时监测、ID26暂停保持；没有自动通知承诺，不自动延长/重启或扩大零衰减范围。

源码副本、远程映射、批准范围及证据入口：[README](tools/pose26-diff-nodecay/20261004/README.md)、[PLAN](tools/pose26-diff-nodecay/20261004/PLAN.md)、[启动验收](tools/pose26-diff-nodecay/20261004/evidence/startup-verification.json)。实时查服务器pipeline-status.json和各日志，项目evidence是采集时快照。

交付前10:25:28只读查询：stage=training、第1轮1701步，分化L2=1.719859849、分化/注意力梯度及查询残差非零，未记录异常但无完整评估，仍未到原第6轮退化点。见同目录`evidence/progress-latest.json`；不能由此认定长期稳定或精度提高。

## 18. PS主导首版架构与独立预处理阶段（2026-10-04）

首版架构决策已人工审查批准并归档：[ADR_00](ADR/ADR_00.md)。ADR记录架构、范围、工具分工、停止条件和验收目标；以下记录实施事实与证据，不能将方案批准视为功能验收通过。

首版原始CSI回放→板端PS预处理→PS/NPU混合推理→单人14关节固定三维视角→720p HDMI＋H.264 RTSP。
采用2024 epoch442；正式验收须NPU和双路均通过，≥5Hz、10Hz优化目标、板端完整窗口到画面P95≤500ms，播放器另测。
实时三接收器采集与PL扩展后续讨论，先按实测收益选择；不自动将此前候选功能变为必做。

### 18.1 实测环境、启动与输入契约

板端此前只读查询确认Ubuntu20.04.4/aarch64、Icraft/CustomOp3.39.0、mvx M2M视频驱动声明H.264/HEVC与原始格式、
udmabuf128MiB；本次再次读取启动FAT16及设备树。FPAI为容器名，实际镜像`ubuntu20.04:custom`，挂载原D盘项目；
arm64 SDK/CustomOp3.39.0、交叉GCC9.4存在。SDK安装和视频格式声明都不代表推理或编码已通过。

本次FAT16直接只读解析，9启动文件与镜像大小/哈希全部一致，见启动审计（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-audit.json`）
和源镜像对照（历史附件，当前仓库未附：`tools/pose-v1/evidence/boot-source-comparison.json`）。uEnv仍从p2加载download.bit，前次根目录未找到；
BOOT内及实际运行AI_MATE身份、HDMI映射未确认，设备访问暂停，等待保留串口日志。根目录新增`Logs`；未挂载或修改启动文件。

原始窗口契约见[PROTOCOL.md](software/pose_v1/PROTOCOL.md)：32字节头部，帧号/时间戳，86400字节float64 I/Q，
`[3 receiver,3 antenna,30 carrier,20 sample,2]`；输出float32 `[1,180,60]`，30幅度＋30相位。
回放发送端已实现但板端TCP接收服务尚未实现，不将文件数值测试当作网络联调。

Conda独立验证环境，当前worktree`.local/pose-v1-conda`，Python3.10.21/NumPy2.2.5/h5py3.16.0/PyWavelets1.8.0，
见精确依赖锁定（历史附件，当前仓库未附：`tools/pose-v1/evidence/conda-explicit.txt`）。在线安装因TLS中断失败后缓存离线成功，未改渠道、证书、既有Conda或板端依赖。

### 18.2 预处理实板结果与限制

从原`wifi_pose.py`提取实际三种预处理方法，不导入mmdet/GPU。db11在20个时间样本下最大分解层数为0，幅度不变；
保留相位展开、三天线相对相位、共用线性校正、复数重构再angle与token排列。
初次移植错误来自零幅值复数乘法带符号零，已按原式修正并保留初次失败（历史附件，当前仓库未附：`tools/pose-v1/evidence/host-preprocess-initial-failure.json`）。

修正后主机（历史附件，当前仓库未附：`tools/pose-v1/evidence/host-preprocess.json`）和实板（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-preprocess.json`）9类用例结果：
真实S11_01_308/309/310及常量/零/随机的float32张量逐位一致；板端真实样本预处理5.70319/5.78065/5.72649ms；
四类非法记录拒绝。0.75rad斜坡差7.5051e-14；±π边界最大差6.24063/5.76522，未定义容限/修改展开规则，不能宣布总体等价或门检通过。
相位边界浮点敏感性仅是排查方向，需进一步取证，不以推断消除失败。

已交叉构建并在Lite上执行独立程序，SHA256 `65d44aa2aff5ffe2975300b27b1325dc7b25d5cb71cd6f85ee5076b4aa4a59b2`；
[构建脚本](tools/pose-v1/Build-Preprocess.ps1)复现同一哈希。代码、模型、源文件哈希见资产清单（历史附件，当前仓库未附：`tools/pose-v1/evidence/asset-manifest.json`）。
只在/tmp写测试产物，没有NPU/HDMI/VPU设备访问。上述时延不是端到端推理/显示指标。

### 18.3 尚未实现与下一步

归档时运行位流配套、π边界和误差容限仍需讨论（最新运行身份及门检已更新，见18.4）。未执行ONNX/Icraft参考/板端混合推理，未实现板端接收服务、队列、骨架渲染、
HDMI/编码RTSP与30分钟闭环；不能用全CPU或电脑推理替代NPU正式验收。最新状态见[STATUS.md](tools/pose-v1/STATUS.md)
及[软件README](software/pose_v1/README.md)。任何新增依赖、启动配置、模型修正或FPGA工程继续先讨论批准。

### 18.4 300份真实回放门检及运行FPGA版本核验（2026-10-04，最新）

[ADR_00第12节](ADR/ADR_00.md)记录的验收调整：9组固定300份，含旧3份；幅度atol/rtol=1e-6，
相位周期最大≤1e-5 rad，保留标量绝对差，真实相位绝对差>1e-5 rad仍须讨论。
人工±π保留非阻断诊断，周期最大2.333111/2.693437 rad仍失败，不把周期比较当作失败消除方法。
此次Linux主机及Lite分别300/300与Windows参考逐位一致，实板/主机输出哈希全相同；幅度、相位标量及周期最大差均为0，
四类非法输入都拒绝。原算法/模型/ARM二进制保持不变；预处理单项median=5.781265ms，P95=5.8595ms，不是端到端验收。
见固定清单（历史附件，当前仓库未附：`tools/pose-v1/evidence/replay-300-manifest.json`）、汇总（历史附件，当前仓库未附：`tools/pose-v1/evidence/replay-300-summary.json`）、
实板报告（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-preprocess-300.json`）。

替换BOOT后，最新只读审计（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-runtime-audit-25122301.json`）确认BOOT SHA256为
`ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`，与指定Lite 25122301包相同；
其余8个启动文件保持旧审计身份。`Logs/Log1.txt`明确记录FSBL下载PL完成、Linux启动；
uEnv导入后文件系统错误不记为download.bit加载成功，也不否定FSBL先前的PL加载。
按日志分区位置解析BOOT，32位字节序转换后的完整.bit载荷与BOOT对应内容相同，BOOT另有4字节尾随`20000000`，
见载荷对应证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/boot-25122301-comparison-resolved.json`）。
另外明确批准最小只读映射，取得0x4000001C原始字节01231225、值0x25122301，
见运行版本证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/fpga-version-read-25122301.json`）。未调用SDK Open/reset/check、DMA、模型或视频访问。

板端Icraft/CustomOp:arm64实际3.39.0；参考软件标3.36.0，兼容性尚待混合推理实测，保持当前SDK不自动降级。
参考ZG URL声明NPU=0x40000000、DMA=0x80000000；3.39.0 `zg330_device.h`定义版本偏移0x1C及initAfterRegions，
SDK初始化实现未由头文件证明为只读，不能把Open当作普通只读审计操作。
HDMI包装器RGB565/地址0x40080054/地址单位8字节，只配置缓存而不配置视频时序；
参考配置1920×1080@60，不能只改宽高就宣称720p60成立。首版720p60保持，屏幕未接，尚未实屏验证。

详细工程内容与后续限制见[RESULTS-300.md](tools/pose-v1/RESULTS-300.md)，具体探测审批与后续门检见
[NEXT-GATE.md](tools/pose-v1/NEXT-GATE.md)。前述3份、待日志、位流未知及未定义容限的条目为历史阶段。

### 18.5 独立混合推理检查器与HDMI静态审查（2026-10-05，源码交付）

下一阶段方向。新增[检查器源码](software/pose_v1/src/inference_check.cpp)、可选SDK CMake目标、
[FPAI构建脚本](tools/pose-v1/Build-Inference.ps1)、[Host启动器](tools/pose-v1/Run-HostReference.ps1)及
[打包/ONNX/对照工具](tools/pose-v1/inference_gate.py)。代理仅编辑与静态审查，尚未编译、测试或运行；
实际软件与AI操作人工执行，详细位置/参数/产物/停止条件见[执行说明](tools/pose-v1/INFERENCE-COMMANDS.md)。
SDK目录、Windows编译工具及ORT依赖待查询，不自动安装。现有独立DLL包仍位于原项目D盘，worktree没有副本；
Host启动器逐项核对已批准manifest/DLL哈希，仅补子进程PATH，不借koala。

静态依据为本机3.39.0头文件`icraft-xrt/core/session.h`、`core/tensor.h`、`core/device.h`、
`icraft-xir/core/network.h`、`core/data_type.h`及Host/ZG330 backend头文件和厂商CMake导出目标。
使用Session::Create<ZG330Backend,HostBackend>，记录bindings和post-callback；Tensor.dump(SFB)规范化逻辑float32输出。
初始三样本保留100候选/14关节/3坐标及帧号；分数/坐标数值验收待实测讨论。
SDK回调是运行路径证据，不能扩展为独立总线测量或完整性能验收；原预处理源码/模型未改。

[HDMI静态审查](tools/pose-v1/HDMI-STATIC-AUDIT.md)补充：参考video_define启用1080p，color_bar含720分支；
frame_ctrl包含0x094–0x0B4可写时序/使能线索，参考时钟IP请求148.5/742.5MHz。
时序寄存器存在不证明当前运行位流配套；RGB565缓存包装器仍未配置720p时序。
部分垂直前后肩名称与color_bar对应不同，须追踪消费者语义，不自行修正或写寄存器。
首版720p60、NPU、双路及30分钟闭环验收均保持待完成。

随后提交[环境查询截图及分析](tools/pose-v1/ENVIRONMENT-QUERY-20261005.md)：FPAI GCC9.4.0、
CMake3.24.2和Icraft arm64 3.39.0确认；仅找到HostBackend配置，尚需核对包内容及后端实际命名。
独立Conda NumPy可找到、ORT缺失；Windows cmake/cl当前PATH不可见，不能判定全机没有编译工具。
此次查询不包含CustomOp，相关状态待补查；未编译、安装或初始化设备。

后续补查更新：项目的`/usr/cmake`及包清单截图确认Host/ZG330配置、aarch64导出、ZG330头文件及后端so/AIU库。
FPAI icraft/customop均arm64 3.39.0，icraftmdzthirdparty arm64 0.1.1，均install ok installed；
当前可用SDK构建目录为`/usr/cmake`。不需要根据此前搜索结果认定缺后端并安装，
但头文件API/链接/运行兼容性仍需编译与后续门检。ORT和Windows工具入口问题未解决，未执行推理。

随后完成B/C固定打包和交叉构建`inference-20261005-165059-043b0c40`，GCC9.4.0/CMake3.24.2，
实际配置/编译/链接成功。AArch64 PIE二进制SHA256
`d1006f9bd78050ffa484c64bf74fb62542d270c7acca5068e9da611a5bdc05e5`；
7份源码记录、11份包文件大小/哈希、二进制哈希全部复核匹配，见
cross-build-review-20261005.json（历史附件，当前仓库未附：`tools/pose-v1/evidence/cross-build-review-20261005.json`）。
动态依赖含Host/ZG330后端、XRT/XIR/Utils及标准运行库，日志无RPATH/RUNPATH项；
不能据此证明板端库可解析或运行ABI通过。接下来人工操作D，ldd/inspect结果复核前不推进初始化。

D阶段现场反馈：程序哈希匹配、ldd列出的依赖均解析成功；校验清单CRLF导致Linux把CR当作文件名后缀，
11项No such file。已只读确认本地清单11行CRLF，源于打包脚本默认文本换行；
[候选方案](tools/pose-v1/CRLF-CHECKSUM-FIX.md)仅修清单写入及人工生成LF清单重新核验，尚未批准执行。
这不是已证明的文件丢失/模型损坏，板端包完整性仍未通过，inspect/SDK初始化和推理均未验收。

D阶段后续更新：实际校验`files.lf.sha256`，11项均OK且退出码0，板端包完整性已通过；
ZG图inspect随后退出码0，见新截图（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-checksum-inspect-exit0-20261005.png`）。
图接口、阶段、运行配置及stderr尚待提交复核，不能仅凭退出码宣布离线接口或NPU通过。
生产打包脚本候选修正尚未应用；已保留旧清单及失败记录，设备初始化/混合推理未执行。

D产物随后已由现场提供并复核：输入[1,180,60]、分数[1,100]、姿态[1,100,14,3]顺序符合float32门禁，
阶段offline_inspection_complete、mode=inspect/device_init_allowed=false，stderr为空且无failure.json。
结合11项包校验与退出码0，D离线检查通过；见产物截图（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-inspect-artifacts-20261005.png`）。
尚未加载RAW或访问设备，下一步先核对GNU timeout、并发应用和BOOT是否保持，不自动停止进程或执行probe。

E前置查询随后确认：/usr/bin/timeout为GNU coreutils 8.30，probe及三份日志不存在；
可见进程未见明显AI/HDMI/编码应用，内核线程名称不能代替故障/占用证据。
截图：timeout与进程（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-probe-preflight-20261005-1.png`）、
剩余进程及路径（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-probe-preflight-20261005-2.png`）。
尚需确认运行位流未因BOOT替换/JTAG加载而改变及无其他演示占用；probe/推理未执行。

E执行更新：实际probe退出码0，SDK device版本25122301与基线一致，icore已回报，
probe.dmesg.log已保存；见执行截图（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-probe-exit0-20261005.png`）。
compatibility_passed=false由检查器源码固定写入，表示尚未通过完整兼容性验收，不是SDK检测失败。
stdout/stderr、stages/run-config及内核日志内容待复核，不能仅凭Open/version成功推进或认定混合推理通过。
读取命令见[执行说明E](tools/pose-v1/INFERENCE-COMMANDS.md)；不重跑probe、不改模型/SDK或验收标记。

E完整复核通过：现场提供阶段、配置、stdout/stderr及内核尾部，阶段以probe_complete_requires_review结束，
mode=probe/device_init_allowed=true，无failure.json、stderr为空，stdout报告Device initialization successful。
device=25122301、icore=FMSHZGV3TECH-AID - 24160628，AXI zg330aiu及固定NPU/DMA地址一致。
提供的内核尾部未见探测相关总线/DMA错误；启动时EXT4恢复/journal异常关闭及更换信息保留，不归因于本次探测。
证据：产物及stdout（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-probe-review-20261005-1.png`）、
内核上段（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-probe-review-20261005-2.png`）、末段（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-probe-review-20261005-3.png`）。
通过范围仅Open/version，不是完整3.39.0模型计算兼容性；下一步F1/F2参考，ORT及Windows编译工具待落实。

Windows Host工具后续只读定位：VS 2022 Community位于`D:\Visual Studio\ Visual Studio 2022\Community`，
` Visual Studio 2022`目录名开头有一个空格；已找到MSVC14.44.35207编译/链接工具、头文件/库及CMake文件元数据3.31.6-msvc6。
文件存在不能证明SDK完整/工具实际调用或编译通过；默认vswhere及常见Windows Kits入口未找到/未返回记录，
不自动修复/重装。查询：[WINDOWS-HOST-ENV-CHECK.md](tools/pose-v1/WINDOWS-HOST-ENV-CHECK.md)，
证据：定位记录（历史附件，当前仓库未附：`tools/pose-v1/evidence/windows-host-tool-discovery-20261005.json`）。ORT仍缺失，模型参考未执行。

Windows终端首次启动反馈为目录名开头空格遗漏：实际名称首字符32，带空格脚本存在、不带空格路径不存在；
不能据此认定SDK缺失。已更新同一[查询说明](tools/pose-v1/WINDOWS-HOST-ENV-CHECK.md)用真实目录项构造路径，
证据首次路径错误（历史附件，当前仓库未附：`tools/pose-v1/evidence/windows-host-path-error-20261005.png`），初始化/后续编译未通过。

后续截图已显示开发终端横幅，但查询截图cl未找到、架构/SDK变量未设置；
是否在同一CMD进程执行仍待确认，不由此认定SDK缺失或安装损坏。初始化子脚本只读确认存在，
v17.0横幅是vswhere缺失时的源码默认，不作编译通过证据。截图：
启动（历史附件，当前仓库未附：`tools/pose-v1/evidence/windows-host-banner-20261005.png`）、
查询（历史附件，当前仓库未附：`tools/pose-v1/evidence/windows-host-unset-query-20261005.png`）。

人工确认查询来自另开的CMD，未继承原开发终端环境；不据此认定原窗口初始化失败/SDK缺失。
现在回原初始化窗口查询，原环境及SDK仍待验证，不安装、修复或直接构建。

原CMD实际查询更新：cl/x64/VS目录均可用，CMake实际3.31.6-msvc6；WindowsSdkDir未设置、WindowsSDKVersion仅`\`。
4个厂商v10.0登记入口及5个常见目录未找到有效SDK，不排除其他自定义路径；Windows Host构建暂停，不自动安装。
证据：同窗口查询（历史附件，当前仓库未附：`tools/pose-v1/evidence/windows-host-sdk-query-20261005.png`）。
后续[候选方案](tools/pose-v1/REFERENCE-NEXT-PLAN.md)讨论复用Lite已有host模式作数值参考及独立Conda ORT1.23.2解析预览，
不改正式NPU/双路要求，尚未批准或执行；模型参考与mixed未通过。

随后已明确批准B“先用Lite Host作参考”，本阶段F2改到Lite ARM，复用已有二进制/optimized模型与固定输入。
资源前检已人工执行并经截图复核：总内存993 MiB、available 744 MiB、Swap 0，/tmp剩余47G；未见明显其他推理/视频应用，结果前缀无旧文件。证据：资源（历史附件，当前仓库未附：`tools/pose-v1/evidence/lite-host-resource-query-20261005-1.png`）、进程与路径（历史附件，当前仓库未附：`tools/pose-v1/evidence/lite-host-resource-query-20261005-2.png`）。下一步按批准范围人工执行一次300秒Host参考，具体[LITE-HOST-COMMANDS.md](tools/pose-v1/LITE-HOST-COMMANDS.md)第2步；前检不保证模型峰值内存/算子支持或执行成功。
Host尚未执行，ARM支持及内存/数值待验证；仅B获批准，ORT解析/安装仍未批准，不改正式PS/NPU/双路要求。

最新Host执行反馈更新上述状态：一次受限试跑退出码1，截图（历史附件，当前仓库未附：`tools/pose-v1/evidence/lite-host-exit1-20261005.png`）。Host参考未通过，具体失败阶段/原因待现有日志审查；不重跑、覆盖输出或直接推进mixed。读取说明见LITE-HOST-COMMANDS.md第2步，新增failure.json诊断读取；没有模型/依赖/环境修复或NPU计算验收。

最新日志已定位到Session创建时op_id=1 MatmulNode没有后端绑定，尚未样本前向；mode=host/device_init_allowed=false、parameters_loaded后failed_stop_no_retry。内核尾部未见本次OOM、available 687 MiB。见[完整失败审查与只读候选](tools/pose-v1/HOST-BINDING-REVIEW-20261005.md)，evidence/lite-host-binding-failure-20261005-1.png至-3.png。本机Host文档将Matmul列为CPU支持，不能代替ARM板端注册范围核验；正式ZG六个Host计算算子不含Matmul，因此既不宣布NPU混合路线失败，也不跳过参考门检。库身份/依赖只读审计候选待批准，未修复/重跑/安装。

后续审计并增加特殊问题代理工具协助权限（见AGENTS.md分工条款），代理已直接SSH完成。
Icraft/CustomOp arm64 3.39.0，icraft包校验无差异；Host库SHA256 d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130与原始onchip包相同，CMake含CudaDefault依赖，readelf存在。证据审计日志（历史附件，当前仓库未附：`tools/pose-v1/evidence/board-host-library-audit-20261005.stdout.log`）、同前缀stderr/退出码及原包审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/original-arm-host-package-review-20261005.json`）。未访问设备或重跑模型；库完整不等于Matmul注册/支持。新[独立注册探针候选](tools/pose-v1/HOST-REGISTRY-PROBE-PLAN.md)尚未批准或执行，后续修复/安装仍按审批规范。

**注册探针后续验收**：取得独立执行许可后，代理完成FPAI GCC9.4/CMake3.24.2/ARM Icraft3.39.0交叉编译与Lite一次30秒查询，退出码0、stderr空、5项回传哈希匹配。optimized Matmul op1无init/forward注册；ZG op188/437 TopK、192 GatherElements、582/649 ScatterND也无注册，442 Gather有注册。见[完整结果](tools/pose-v1/HOST-REGISTRY-RESULTS-20261005.md)、结构化复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/host-registry-20261005/review.json`）。探针不创建Session/调用Device::Open/前向计算，原源码/推理二进制/模型/SDK未改。全CPU参考与ZG图PS部分均有当前注册缺口，mixed停止；不能仅换参考平台或凭Gather注册认定NPU/数值通过。后续官方配套/注册机制须核对，加载插件、改链接/SDK/模型或新增算子实现另讨论批准。

**Matmul分配澄清（静态核对）**：CPU host模式使用optimized图建立独立浮点数值参考，并非正式部署划分。原仓库quantized图130个Matmul（含op1）均为@zhuget(330)，adapted图132个Matmul也均为该目标；最终ZG图为硬算子指令，CPU计算节点仅上述六个、无CPU Matmul。正式矩阵计算保持ZG路径，尚未实际NPU验收；部署侧注册阻断是TopK/GatherElements/ScatterND，不能把CPU参考Matmul失败解释为ZG不支持Matmul。

### 18.6 CPU算子注册与全有效布局最小适配（2026-10-05，批准及源码交付）

隔离应用侧方案。资料整合与限制见[CPU-ADAPTER.md](tools/pose-v1/CPU-ADAPTER.md)，
逐条人工操作命令见[CPU-ADAPTER-COMMANDS.md](tools/pose-v1/CPU-ADAPTER-COMMANDS.md)。
源码交付及静态核验身份见evidence/cpu-adapter-source-delivery-20261005.json（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-source-delivery-20261005.json`）。

| 资料/文件 | 开发参考价值与边界 |
| --- | --- |
| ARM 3.39.0原包的`hostbackend/port/common/hostbackend_impl.h` | TopK/GatherElements/ScatterND注册依据；包含后端方法定义及大量已有注册，不能整体引入应用。 |
| `hostbackend/port/common/tensor_ops.h`、`common/tensor_kernel.h` | 原明文包装与inline数学内核；明确拒绝非空distributions，需要独立核验临时描述适配，不能只注册就宣布可用。 |
| `icraft-xrt/core/backend.h` | BackendOpRegistry禁止默认覆盖，BackendOpRegisterHelper实际forward为四参数ABI；以本机3.39.0签名为准，旧示例不能代替。 |
| `icraft-xir/core/data_type_attr.h`、固定`piw24_ZG.json` | 六个Host节点/九项分布声明的完整有效范围；候选只支持当前FP32形状、轴、ZERO全有效掩码。 |
| [host_cpu_adapter.cpp](software/pose_v1/src/host_cpu_adapter.cpp) | 应用显式注册五个缺失节点，运行时核对元数据、字节数与Host内存，只清除临时TensorDesc分布；不改模型，Gather保持原后端。 |
| [host_cpu_adapter_check.cpp](software/pose_v1/src/host_cpu_adapter_check.cpp) | 无Session/Device::Open的独立合成测试；真实六节点规格、注册前后核对、调用实际注册回调，Gather只初始化单CPU节点view。 |
| [cpu_adapter_gate.py](tools/pose-v1/cpu_adapter_gate.py)、[独立CMake](tools/pose-v1/cpu-adapter-CMakeLists.txt) | 固定NumPy 2.2.5独立参考、源码/模型/原ARM头文件及so身份；独立构建不接入原推理器。设计107用例/22份正常输出，尚未生成或运行。 |

六份关键头文件与原ARM包按CRLF→LF规范化后相同，原Host so保持
`d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130`。
原CustomOp包没有三类缺失标准算子的独立插件；仅设ICRAFT_CUSTOM_DIR不能证明注册成功。
源码中固定原ZG模型SHA256、SDK头文件身份和原推理源码/CMake身份，编译与板端复核仍人工执行。

本轮仅完成源码/脚本和静态审查（Python AST、PowerShell语法、LF脚本）；
**未生成测试包、交叉编译或执行CPU前向**，不把计划数量写为已通过数量。
候选只接受HostDevice CPTR内存，不证明实际PS/NPU缓冲区、同步/复制、非全有效去填充或完整模型可用。
CPU Matmul参考缺口及完整mixed数值门检继续保留；后续正式推理器接入须另行讨论，禁止直接推进NPU/HDMI/RTSP验收。

2026-10-06执行反馈：实际生成的测试包为`.local/pose-v1-cpu-adapter/package/20261005`，
282项清单哈希及5份构建文件/副本只读复核匹配；107个用例及22份正常参考已生成，但未执行SDK算子。
构建日志确认GCC9.4.0、CMake3.24.2，随后`docker exec FPAI python3`因当前PATH无该命令退出127，
尚未进入CMake配置/C++编译。[故障与修正候选](tools/pose-v1/CPU-ADAPTER-BUILD-FIX-20261006.md)
保留原SDK门检，改由Docker导出实际ARM文件和Windows PowerShell计算哈希，避免新增容器Python依赖。
生效脚本未修改，修正和新构建待批准；原目录/清单保留，不自动重跑。
证据：结构化审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-build-failure-20261006.json`）。

随后修正，已将审阅候选写入生效Build-CpuAdapter.ps1，原脚本备份/旧目录/测试包保持。
保留原SDK身份门检，核验位置改到Windows且记录实际构建脚本哈希；语法0错误，但容器导出/编译/前向均未执行。
直接按[更新命令B](tools/pose-v1/CPU-ADAPTER-COMMANDS.md)使用现有包及新标签cpu-adapter-20261006-r1，
不重做A；应用身份（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-build-fix-applied-20261006.json`）。
上述“未修改/待批准”保留为审批前历史，不能将修正应用记为构建通过。

r1实际执行更新：SDK身份及CMake配置/生成通过，导出六头文件、Host库、两包3.39.0版本和五份源码副本匹配。
编译检查器时PowerShell原生stderr导致Stop，日志无完整error；静态核对
`icraft-xir/base/array.h`的Array::set与`base/object.h:290`的ObjectRef::get_mutable返回类型，
确认三处`dims.get_mutable()->at(...)`错误，Object*没有at。
[源码及日志修正候选](tools/pose-v1/CPU-ADAPTER-COMPILE-FIX-20261006.md)未批准/应用，
未重编译或CPU测试，不能排除其他编译问题。证据
r1审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-compile-failure-r1-20261006.json`）。

Array API/日志两项修正，已应用审阅候选、保留原文件备份与旧包/失败证据。
PowerShell语法0错误，未执行r2准备/构建/前向；SDK门禁和非0退出停止保持。
现在按[执行A/B](tools/pose-v1/CPU-ADAPTER-COMMANDS.md)生成新身份包package/20261006-r2，
构建标签cpu-adapter-20261006-r2，禁止回写旧包manifest绕过来源核验。
应用身份：r2修正记录（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-compile-fix-applied-r2-20261006.json`），
具体处理见[修正说明](tools/pose-v1/CPU-ADAPTER-COMPILE-FIX-20261006.md)；其他编译问题仍待实际日志核对。

r2实际构建复核更新：完成配置/编译/链接，GCC9.4.0/CMake3.24.2、ARM Icraft/CustomOp3.39.0，
282项包哈希和5份源码/副本匹配，SDK六头文件/Host库身份一致；新旧281项非manifest文件相同。
程序为AArch64 PIE，SHA256 `8cf2017cedf6a97f98ce485d979239b659291f3c91d3a3d550382c1c94588622`，
直接依赖无ZG/AIU，无RPATH/RUNPATH。完整evidence复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-r2-build-review-20261006.json`）。
接下来按[命令C](tools/pose-v1/CPU-ADAPTER-COMMANDS.md)执行既定的一次受限CPU测试；
板端加载、注册前向、实际107用例数值仍未验收，不把编译通过扩展为mixed或NPU通过。

随后现场提供Lite运行截图：脚本/exit.txt为0，stdout报告107例完成，stderr为空，
summary=cpu_candidate_tests_passed并标记未Device::Open/完整模型/mixed。
此为程序内部检查报告，注册和22份实际输出的独立文件核验仍待完整回传，当前没有本地结果目录。
截图/结构化反馈：evidence/cpu-adapter-board-run-feedback-20261006.json（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-board-run-feedback-20261006.json`）。
人工操作[命令D](tools/pose-v1/CPU-ADAPTER-COMMANDS.md)完整回传，不重跑C或提前混合推理。

**最终验收更新（2026-10-06）**：完整40项回传及review.json已取得，代理直接读取独立核验通过。
107例（18正常/89拒绝）、12条注册前后记录、22份输出/59,600个FP32值与NumPy参考逐位一致且有限，
最大差0；282项包校验、板端程序/模型/Host库及SDK身份匹配，ldd完整，退出0/stderr空。
五个缺失节点补齐init/forward并前向通过，原Gather保持并通过，CPU Matmul未补齐。
完整[结果与限制](tools/pose-v1/CPU-ADAPTER-RESULTS-20261006.md)、
代理独立核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-independent-review-20261006.json`）及
文件复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/cpu-adapter-20261005-review.json`）。
提交前后dmesg尾部相同，内存快照不是峰值/完整模型性能测试。
仅Host CPTR/全有效分布的独立候选验收，未接入推理器、验证NPU缓冲区/同步/搬运或完整模型Session。
后续接入/数值参考另讨论，不直接推进mixed；此前待回传为历史，中途拆行报错后完整命令已成功。

### 18.7 ONNX直接参考与PS/NPU独立接入候选（2026-10-06）

最新难点复盘与下一轮准备：[Done.md首节](Done.md)、[E0/N1/P1及H0具体方案](tools/pose-v1/NEXT-PHASE-PLAN-20261006.md)、
既有证据分析（历史附件，当前仓库未附：`tools/pose-v1/evidence/next-phase-20261006/existing-evidence-analysis.json`）、
27候选清单（历史附件，当前仓库未附：`tools/pose-v1/evidence/next-phase-20261006/proposed-27-cases.json`）。
已完成本机身份/排序/预算分析及候选选择，未新增模型/板测；新实施范围、执行方和数值容限待确认，不将计划记为验收。

最新r6跨帧同输出已解决：[工程与数值结果](tools/pose-v1/MIXED-FRAME-STATE-R6-RESULTS.md)、
[修正来源](tools/pose-v1/MIXED-FRAME-STATE-R6-SOURCE.md)、
完成核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-frame-state-r6/completion-review.json`）、
完整ONNX误差（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-frame-state-r6/onnx-comparison.json`）。
代理完成全部阶段；每帧SDK reset(1)清FPGA状态、0→745，三帧分别响应/首帧全部内容重复一致，模型及NPU分工保持。
三样本工程门禁通过，数值容限/性能/显示仍待；下方r3/r4/r5停止及待批准为此前阶段，不重跑旧包。

最新r4三样本失败已分析：[报告](tools/pose-v1/MIXED-CONTENT-R4-THREE-FAILURE.md)、
内容复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/mixed-three-content-review.json`）、
独立失败复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/mixed-three-failure-review.json`）。
Caller/Input0正确更新，局部前段变化而后段和最终不变；五CPU内核对实际输入52000FP32逐位一致。
停止重跑/正常数值及后续硬件，不生成三样本门禁；[r5候选](tools/pose-v1/MIXED-CONTENT-R5-READINESS-PLAN.md)待讨论批准，未改运行策略。

最新r4单样本内容验收：[结果](tools/pose-v1/MIXED-CONTENT-R4-ONE-RESULTS.md)、
内容复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/mixed-one-content-review.json`）、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/mixed-one-independent-review.json`）。
真实caller/Input0与308逐位一致，17内容/七ZG/六Host及4300有限输出通过；连续输入故障仍未知。
当前仅[r4命令H](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md)一次300秒三帧＋重复首帧内容取证并回传；后方待单样本为历史。

最新r4 apply-only验收：[结果](tools/pose-v1/MIXED-CONTENT-R4-APPLY-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/apply-independent-review.json`）、
apply门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/apply-check.acceptance.json`）。
1181原节点/1173HardOp七组追溯及八Host保持，无content/forward；当前仅[r4命令G](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md)308内容前向并完整回传。
根因仍未确定，下方待apply为历史。

最新r4 SDK内存验收：[结果](tools/pose-v1/MIXED-CONTENT-R4-MEMORY-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/memory-independent-review.json`）、
内存门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/memory-check.acceptance.json`）。
两16KiB六回读/24,576有限FP32逐位一致及身份保持，无Session/前向；当前仅[r4命令F](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md)apply-only并回传。
不同输入同输出仍未定位，下方待内存为历史。

最新r4离线验收：[结果](tools/pose-v1/MIXED-CONTENT-R4-OFFLINE-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/offline-independent-review.json`）、
离线门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/offline-check.acceptance.json`）。
真实RAW/三PS输入32,400有限FP32及新身份通过，无设备/Session/NPU；当前仅[r4命令E](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md)SDK内存往返并回传。
实际Session内容仍未取证，下方待离线为历史。

最新r4 Host/内容路径验收：[结果](tools/pose-v1/MIXED-CONTENT-R4-HOST-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/host-independent-review.json`）、
Host门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/host-check.acceptance.json`）。
原107例/22输出59,600FP32保持，两模式SDK读回/别名模拟及三拒绝路径通过；无真实Session Input0取证。
当前仅[r4命令D](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md)30秒离线并回传，不直接硬件；下方Host待验为历史。

最新r4-final构建验收：[结果](tools/pose-v1/MIXED-CONTENT-R4-BUILD-RESULTS.md)、
构建门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/build.acceptance.json`）。
291包/20来源/12构建/15ARM头文件/两库匹配，AArch64 PIEba8d5398…15dcea7，捕获API编译通过。
当前仅[r4命令B/C](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md)新final目录传输/Host＋内容路径并回传，不直接硬件；下方未编译为历史。

最新r4输入内容取证已批准交付：[源码说明](tools/pose-v1/MIXED-CONTENT-R4-DELIVERY.md)、
最终身份（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/delivery-review.json`）、
本机模拟核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-content-r4/offline-content-tests-final/review.json`）。
实际caller/Input0/现有Host暂存与CPU结果内容记录，原计算/SDK处理保持；291包项/12构建/20来源、11异常检查通过。
当前仅[r4命令A](tools/pose-v1/MIXED-CONTENT-R4-COMMANDS.md)最终包交叉编译，未新ARM/板测，不把取证交付当修复；下方待批准为历史。

最新r3三样本失败停止：[完整审查](tools/pose-v1/MIXED-FUSION-R3-THREE-FAILURE.md)、
61项结果核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/mixed-three-failure-review.json`）、
SDK只读资料审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/mixed-three-SDK-source-review.json`）。
输入/ONNX均有不同响应，但板端三个完整输出与308首帧相同；不生成三样本验收/正常误差报告。
[新输入内容诊断方案](tools/pose-v1/MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md)待批准，暂停新硬件；不直接认定cache/DMA或SDK故障。
下面下一步三样本为历史，原单样本工程通过仅保留其适用范围。

最新r3单样本工程验收：[结果](tools/pose-v1/MIXED-FUSION-R3-ONE-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/mixed-one-independent-review.json`）、
工程门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/mixed-one.acceptance.json`）。
七ZG/六Host实际执行、4300有限FP32、八SDK搬运/身份核验通过；单次forward204.64506ms不作性能验收。
ONNX初步差异已报告，无数值容限通过；仅[r3命令H](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md)三帧及重复首帧并回传。
下方前向待验证为历史；HDMI/RTSP/完整精度/持续性能仍未验收。

最新r3正式apply验收：[结果](tools/pose-v1/MIXED-FUSION-R3-APPLY-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/apply-independent-review.json`）、
apply门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/apply-check.acceptance.json`）。
1181原节点/1173HardOp经七实际ZG组完整唯一追溯及八Host保持，ARM正式门检已通过，无模型前向。
当前仅[r3命令G](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md)180秒308单样本并回传，核验前不三样本；下方待apply为历史。

最新r3 SDK内存验收：[结果](tools/pose-v1/MIXED-FUSION-R3-MEMORY-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/memory-independent-review.json`）、
内存门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/memory-check.acceptance.json`）。
两16KiB六回读/24,576有限FP32逐位一致及版本/身份通过，无Session/NPU前向。
当前仅[r3命令F](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md)300秒正式apply并回传，核验前不mixed；后文待内存为历史。

最新r3离线验收：[结果](tools/pose-v1/MIXED-FUSION-R3-OFFLINE-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/offline-independent-review.json`）、
离线门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/offline-check.acceptance.json`）。
真实RAW四参数/三PS输入32,400有限FP32及新身份核验通过，无设备/Session/NPU。
当前仅[r3命令E](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md)30秒SDK内存往返并回传，不apply；后文待离线为历史。

最新r3 Host验收：[结果](tools/pose-v1/MIXED-FUSION-R3-HOST-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/host-independent-review.json`）、
Host门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/host-check.acceptance.json`）。
107例/12注册/22输出59,600有限FP32与固定及r2逐位一致、新身份匹配；无Session/设备/NPU。
当前仅[r3命令D](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md)真实RAW/PS离线并回传；新融合函数实际apply仍待验收，后文待Host为历史。

最新r3构建验收：[结果](tools/pose-v1/MIXED-FUSION-R3-BUILD-RESULTS.md)、
构建门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/build.acceptance.json`）。
291包/17来源/11构建文件/15ARM头文件及两库匹配，AArch64 PIE e8d66113…e6c696a8，新融合调用已编译。
当前仅[r3命令B/C](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md)新目录传输/Host回归并回传，不直接后续阶段；下方未编译属历史。

最新正式融合追溯r3已批准并交付：[交付结果](tools/pose-v1/MIXED-FUSION-R3-DELIVERY.md)、
源码/包审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/source-and-package-review.json`）、
本机回放（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-fusion-r3/offline-replay-final/review.json`）。
严格1173原覆盖/八Host保持，实际七组+固定成员/同步基线追溯，核验器HardOpNode识别修正。
291包项/11构建文件/17来源和18异常回放通过；模拟记录不作ARM/正式apply通过。
当前仅[r3命令A](tools/pose-v1/MIXED-FUSION-R3-COMMANDS.md)新标签交叉编译，后续逐阶段；下方方案待批准为历史。

最新r2 apply取证：[结果](tools/pose-v1/MIXED-BINDING-R2-APPLY-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/apply-independent-review.json`）、
原到有效组完整映射（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/binding-snapshot-audit/original-to-effective.jsonl`）。
原1173 HardOp确实被七组实际ZG绑定的merge_from完整且唯一覆盖，8622归9185；旧原ID直接检查导致退出1。
十快照/身份通过及九异常拒绝完成，但无forward或apply验收；[正式门检修正方案](tools/pose-v1/MIXED-FUSION-BINDING-FIX-PLAN.md)待批准。
当前停止，不重跑r2或直接mixed；后文待取证为历史。

最新r2 SDK内存验收：[结果](tools/pose-v1/MIXED-BINDING-R2-MEMORY-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/memory-independent-review.json`）、
内存门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/memory-check.acceptance.json`）。
两16KiB ADDR SDK设备缓冲区六回读/24,576有限FP32逐位一致、版本/身份匹配，无完整Session/模型前向。
下一步仅[r2命令G](tools/pose-v1/MIXED-BINDING-R2-COMMANDS.md)一次300秒apply快照取证，非0仍完整回传，不mixed。
下方前置待执行为历史，复制通过不证明NPU同步或融合追溯。

最新r2离线验收：[结果](tools/pose-v1/MIXED-BINDING-R2-OFFLINE-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/offline-independent-review.json`）、
离线门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/offline-check.acceptance.json`）。
真实RAW四参数/三PS输入32,400 FP32及身份核验通过；无设备初始化/Session/NPU。
下一步仅[r2命令F](tools/pose-v1/MIXED-BINDING-R2-COMMANDS.md)30秒SDK内存往返并回传，核验前不apply；后文待离线为历史。

最新r2 Host验收：[结果](tools/pose-v1/MIXED-BINDING-R2-HOST-RESULTS.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/host-independent-review.json`）、
新Host门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/host-check.acceptance.json`）。
107例/12注册/22输出59,600有限FP32逐位一致，新身份匹配；提前offline仅预检、程序未启动。
当前仅执行[r2命令E](tools/pose-v1/MIXED-BINDING-R2-COMMANDS.md)传门禁/保留失败目录后离线检查并回传，暂不硬件。
Host回归不证明快照运行、融合映射或NPU前向；后文待回传为历史状态。

最新快照r2构建验收：[构建结果](tools/pose-v1/MIXED-BINDING-R2-BUILD-RESULTS.md)、
构建门禁（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/build.acceptance.json`），程序SHA25694a03a90…bd061248。
候选源码/10构建文件/15ARM头文件/两库及包身份通过，新字段可编译；实际快照/1173映射仍未知。
当前新目录传输后仅Host回归，旧r1不能重跑或复用门禁；之前未编译是应用时状态。

最新绑定快照r2并应用；新包290项/289非manifest载荷保持，原严格门检不变，尚未新编译/运行。
[r2执行命令](tools/pose-v1/MIXED-BINDING-R2-COMMANDS.md)、
[已批准方案](tools/pose-v1/MIXED-BINDING-SNAPSHOT-PLAN.md)、
应用记录（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/source-applied.json`）、
新包静态审查（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-binding-r2/package-preparation.json`）。
仅补足Session/后端视图及ZG merge_from等公共快照，保留旧r1失败目录及1173/六Host要求，取证不等于部署通过。

最新apply停止：[失败及SSH退出审查](tools/pose-v1/MIXED-APPLY-FAILURE-20261006.md)、
35项失败结果取证（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/apply-failure-review.json`），Session.apply返回后原HardOp8622未在预期绑定表找到，未forward。
SDK public autoMerge/MergedOps、ZG HardOpInfo.merge_from、Session/Backend.network_view为下一步取证接口，尚无完整实际映射。
[快照候选方案](tools/pose-v1/MIXED-BINDING-SNAPSHOT-PLAN.md)及[补丁](tools/pose-v1/mixed-binding-snapshot.candidate.patch)未应用/编译/运行。
保留原绑定1173＋六Host要求，暂停apply重跑和mixed；新方案先批准，不自动改SDK、计数或删除旧目录。

最新SDK设备内存往返已通过：[结果](tools/pose-v1/MIXED-MEMORY-RESULTS-20261006.md)、
独立复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/memory-independent-review.json`）、
memory-check.acceptance.json（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/memory-check.acceptance.json`）。
两16KiB ADDR PLDDR缓冲区/六份24,576FP32模式含零符号位逐位一致；版本25122301/24160628、28回传及SDK身份匹配。
仅SDK CPU↔设备搬运，未完整Session/模型前向或NPU生产者同步；下一步仅apply-check，回传核验后再单样本。

最新真实RAW/PS离线门检通过：[结果](tools/pose-v1/MIXED-OFFLINE-RESULTS-20261006.md)、
独立参数/输入复核（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/offline-independent-review.json`）、
offline-check.acceptance.json（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/offline-check.acceptance.json`）。
四真实参数合法、三PS输入与固定及ONNX逐位一致、32回传/290包及SDK身份匹配；无Session/设备初始化/前向。
下一步仅SDK两16KiB内存往返，版本/区域/同步与NPU仍待实测；后文离线未运行是之前的阶段状态。

最新Host桥门检已通过：107例、12注册、22输出/59,600FP32逐位一致及全有限；回传45/包290哈希与SDK身份匹配。
[Host结果及边界](tools/pose-v1/MIXED-HOST-RESULTS-20261006.md)、独立核验（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/host-independent-review.json`）、
host-check.acceptance.json（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/host-check.acceptance.json`）。
仅Host CPTR暂存回归，真实RAW/设备内存/完整Session/NPU仍待实测；当前传验收文件并回传提前offline的失败预检目录。

最新构建补充：mixed-20261006-r1已完成，代理核验290项包、10源码/副本、15ARM头文件、Host/ZG库及二进制身份通过。
唯一缩进warning经控制流审查符合版本JSON输出预期，源码/包保持，无需重编译。
[构建审查](tools/pose-v1/MIXED-BUILD-REVIEW-20261006.md)、验收门禁文件（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-20261006-r1/build.acceptance.json`）。
现在用户可继续B传输、C仅host-check；尚无新Host桥/设备内存/完整Session/NPU运行结果，下面未编译为源码交付时状态。

工程/数值验收分阶段：ONNX直接对照Lite，不等待Icraft全CPU Matmul注册。
CPU最小适配107例/12注册/22输出59,600 FP32已独立验收；正式Matmul仍NPU、Gather保持。
历史审批/失败记录保留；18.5/18.6中“ORT未批准、mixed待讨论”的当时状态不覆盖本次明确授权。

| 资料/产物 | 用途及实际状态 |
| --- | --- |
| [MIXED-VALIDATION.md](tools/pose-v1/MIXED-VALIDATION.md) | 已批准范围，SDK Host暂存桥、区域/缓冲区/分布限制及阶段通过线 |
| [MIXED-VALIDATION-COMMANDS.md](tools/pose-v1/MIXED-VALIDATION-COMMANDS.md) | FPAI构建、首次传输、Lite六阶段限时执行、回传及逐阶段验收文件 |
| [ONNX结果](tools/pose-v1/ONNX-REFERENCE-RESULTS-20261006.md)、环境记录（历史附件，当前仓库未附：`tools/pose-v1/evidence/onnx-reference-environment-20261006.json`） | 实测Python3.10.21/NumPy2.2.5/CPU ORT1.23.2、三帧完整候选、重复首帧一致与12项哈希 |
| [参考runner](tools/pose-v1/onnx_reference_v1.py)、[依赖锁](tools/pose-v1/onnx-reference.requirements.lock) | CPUExecutionProvider、顺序/线程1/ORT_ENABLE_ALL；八官方wheel哈希 |
| [mixed_bridge](software/pose_v1/src/mixed_bridge.cpp)、[检查器](software/pose_v1/src/mixed_check.cpp)、[Host回归](software/pose_v1/src/mixed_host_check.cpp) | 独立候选源码已写，未编译/板测，不改原推理器与已验收CPU实现 |
| [独立CMake](tools/pose-v1/mixed-validation-CMakeLists.txt)、[构建脚本](tools/pose-v1/Build-MixedValidation.ps1) | pose_mixed_check，复制当前worktree源码；ARM身份核验不依赖容器Python |
| [分阶段runner](tools/pose-v1/run-mixed-validation.sh)、[核验器](tools/pose-v1/mixed_validation_gate.py) | LF清单、timeout、SDK身份、上一验收门禁、全部输出数值统计；未执行新板端阶段 |
| [SDK身份](tools/pose-v1/mixed-sdk-pins.json)、交付记录（历史附件，当前仓库未附：`tools/pose-v1/evidence/mixed-source-delivery-20261006.json`） | 15份当前/原ARM头文件匹配、原Host/ZG库哈希，源码/测试包/保留文件与静态检查 |

独立Conda `.local/pose-v1-onnx-conda`；安装/下载/锁定及Conda导出
`.local/pose-v1-reference-deps/20261006`；参考 `.local/pose-v1-mixed-validation/onnx-20261006`，
新包 `.local/pose-v1-mixed-validation/package-20261006-final`。旧包及证据不覆盖。
ORT版本/安装依据：[PyPI1.23.2](https://pypi.org/project/onnxruntime/1.23.2/)、
[官方CPU安装](https://onnxruntime.ai/docs/install/)；实际运行/加载结果以本机证据为准。

2026-10-08当前入口：[ADR全项目难点索引](ADR/README.md)、[真实VPU/推理RTSP串联结果](tools/pose-v1/LIVE-RESULTS-20261008.md)、恢复点（历史附件，当前仓库未附：`tools/pose-v1/evidence/live-20261008-completion/next-checkpoint.json`）。以下“待板测”等为2026-10-06初期历史，后续固定输入混合/数值/核心性能/有限实时RTSP已通过各自范围；guarded候选正式固化、TCP前端合并、HDMI与整机长期仍待。

真实RAW四参数、PS三输入、SDK两16KiB往返、Session1173HardOp/六Host绑定、308及三样本实际执行均待板测。
ADDR/BOTH只通过SDK复制，Host staging不能替代NPU同步证明；区域或可追溯融合绑定缺失即停止讨论。
工程通过后报告完整分数/坐标与最佳候选差异，容限据实测讨论，不做GT/MPJPE/物理标定。
本机参考耗时不作板端性能。完整NPU/数值、HDMI/RTSP、5Hz/延迟/30分钟闭环尚未验收。

最新：[前向尖峰取证结果](tools/pose-v1/FORWARD-TRACE-RESULTS-20261008.md)、[有界扩展设计](tools/pose-v1/BOUNDED-MEASUREMENT-DESIGN-20261008.md)、[ADR_16](ADR/ADR_16.md)。

最新：[纯计时与异常字节结果](tools/pose-v1/FORWARD-TRACE-R3-RESULTS-20261009.md)、[源数据判别计划](tools/pose-v1/FORWARD-DATA-RECOVERY-NEXT-20261009.md)、[ADR_17](ADR/ADR_17.md)。

最新：[r4源读回结果](tools/pose-v1/SOURCE-READBACK-R4-RESULTS-20261009.md)／完成证据（历史附件，当前仓库未附：`tools/pose-v1/evidence/source-readback-20261009-r4/completion-review.json`）。
