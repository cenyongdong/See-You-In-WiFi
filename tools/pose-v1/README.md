# 首版实施工具与证据

**历史目录：** 这里是早期 100-query、混合 Host／NPU 与 VPU／RTSP 开发及取证。当前源码见 [180-query 主工程](../../software/pose180_pipeline/README.md)，现行进度见[项目总览](../../PROJECT-PROGRESS.md)。旧 NEXT／PLAN 不作为待执行任务，缺失附件按[文档引用说明](../../DOCUMENTATION.md#引用与归档)理解。

最新入口：[software/demo运行说明](../../software/demo/README.md)、[DEMO-RESULTS](DEMO-RESULTS-20261011.md)、[TechDetails](../../ADR/TechDetails.md)、[demo检查点](evidence/demo-20261011-r4/next-checkpoint.json)。三窗口＋60窗口GUI全链通过，正常退出无后台；原高负载坏读排查暂停，不自动继续旧NEXT。以下当前为历史。

当前：目录预建与同租约物理晚源本批结束，DATA96首坏晚对，根因未修。[结果](PRODUCER-PREPARED-RESULTS-20261011.md)／[下一](PRODUCER-PREPARED-NEXT-20261011.md)／[恢复](evidence/producer-prepared-20261011-r1/next-checkpoint.json)。原文件与异常读取保留，测试连接全闭，管理83/100保持。以下当前为历史。

> 2026-10-11最新：[单调用源租约结果](PRODUCER-SOURCE-READ-RESULTS-20261011.md)，Native/ARM/Host188160字节read过、153前向逐位；on计划inv49目录915.86ms被准备截止拦截，无forward或晚源读。221 NoInput视频前缀/abort释放过，原异常读取保持，所有连接结束。[ADR_43](../../ADR/ADR_43.md)／[下一目录预备](PRODUCER-SOURCE-READ-NEXT-20261011.md)／[恢复](evidence/producer-source-read-20261011-r2/next-checkpoint.json)。以下当前为历史。

> 2026-10-11最新：[高地址独立组结果](PRODUCER-ADDRESS-RESULTS-20261011.md)，four/off100及on前49正确，inv49 DATA800逐位前帧A、INDEX正确，首次拥有值已错，晚源尚未读取。214 NoInput视频前缀/abort清理过，所有连接结束；[ADR_42](../../ADR/ADR_42.md)／[下一](PRODUCER-ADDRESS-NEXT-20261011.md)／[恢复](evidence/producer-address-20261011-r2/next-checkpoint.json)。原异常读取保持、责任未证，以下当前为历史。

> 2026-10-11最新：[reset前分段结果](PRODUCER-PHASE-RESULTS-20261011.md)，off/on各100／2352000FP32及307 NoInput视频正常drain过，旧尖峰未复现、正式坏读未修。保存区间等待不能自动归因底层，原异常读取保持。[ADR_41](../../ADR/ADR_41.md)／[下一](PRODUCER-PHASE-NEXT-20261011.md)／[恢复](evidence/producer-phase-20261011-r2/next-checkpoint.json)。全部本批程序连接结束，以下当前为历史。

> 2026-10-11最新：[独立生产者／VPU结果](PRODUCER-VPU-RESULTS-20261011.md)：off100通过，on82次数据正确后时隙失败；reset前1.764秒空档未分解，正式根因未修。271packet／270 NoInput图像前缀正确、162/164复制交叠，abort清理通过但正常drain-LAST未过；原异常读取保留。[ADR_40](../../ADR/ADR_40.md)／[下一](PRODUCER-VPU-NEXT-20261011.md)／[恢复](evidence/producer-vpu-20261011-r2/next-checkpoint.json)。全部程序连接结束，以下当前为历史。

> 2026-10-11最新：[独立生产者结果](PRODUCER-GROUP-RESULTS-20261011.md)，原19成员真实部署／内存／同Session四调用47040 FP32通过。mock只有分配、读写ret，原失败保留；r2 Host CPTR及真实临时区前置门检通过。正式并发根因未修，原异常读取保持；[ADR_39](../../ADR/ADR_39.md)／[下一有无VPU对照](PRODUCER-GROUP-NEXT-20261011.md)／[恢复](evidence/producer-group-20261011-r2/next-checkpoint.json)。以下当前为历史。

> 2026-10-11最新：[原生产者参考结果](PRODUCER-REFERENCE-RESULTS-20261011.md)：原RAW权重／指令与19来源闭合，两图案23520 FP32参考／重放通过，mock独立0→11部署通过；未物理forward／新并发验收。原异常读取保持。[ADR_38](../../ADR/ADR_38.md)／[下一物理门检](PRODUCER-REFERENCE-NEXT-20261011.md)／[恢复](evidence/producer-reference-20261011-r2/next-checkpoint.json)。以下当前为历史。

> 2026-10-11最新：[生产者契约／官方日志结果](PRODUCER-CONTRACT-RESULTS-20261011.md)已归档；零指令Cast不能单独做NPU实验，19成员参考尚未闭合。官方地址同旧失败且非OCM；r3日志数量门禁exit1原错保留，r4仅编译，无模型前向/新数值验收。原异常读取保持，根因未修，程序/连接关闭。[ADR_37](../../ADR/ADR_37.md)／[下一](PRODUCER-CONTRACT-NEXT-20261011.md)／[恢复](evidence/producer-contract-20261011-r2/next-checkpoint.json)。以下当前为历史。

> 2026-10-11最新：[AXI／UDMA审查与双模式对照](AXI-READ-RESULTS-20261011.md)已完成，Host契约、400动态对、455合成图像过。无NPU生产，根因未修；原异常读取保留。[ADR_36](../../ADR/ADR_36.md)／[责任入口](AXI-READ-RESPONSIBILITY-20261011.md)／[下一](AXI-READ-NEXT-20261011.md)／[恢复](evidence/axi-pair-20261011-r4/next-checkpoint.json)。本批连接／程序全结束，未追加独立暂停，以下当前为历史。

> 2026-10-11最新：[首次复制返回／CPU前快照结果](READ-PHASE-RESULTS-20261011.md)，r3 Host107和四窗完整通过，唯一QPC5.05诊断48正确后192立即快照592变化、全同前输入偏移，CPU前不变、两晚源正确。所有异常保存与清理通过，根因未修，全部测试／连接关闭，未追加独立暂停。下一[AXI／UDMA实现审计](READ-PHASE-NEXT-20261011.md)仅准备；[完成绑定](evidence/read-phase-20261011-r3/completion-review.json)／[恢复入口](evidence/read-phase-20261011-r3/next-checkpoint.json)／[ADR_35](../../ADR/ADR_35.md)。旧暂停及当前条目均为历史。

> 2026-10-10当前：真实拥有画面已实现，20正确前向后192坏值复发，103未过；暂停，全部服务／连接结束。[恢复入口](RESUME-PICTURE-20261010.md)／[暂停点](evidence/picture-20261010-r1/pause-checkpoint.json)。以下当前为历史。

> 2026-10-10当前：[单次常驻生命周期结果](RESIDENT-SEQUENCE-RESULTS-20261010.md)，107实际前向1615700FP32／518合成图像过，一次规整／原内核同，服务和连接结束；[恢复点](evidence/resident-sequence-20261010-r1/next-checkpoint.json)／[下一真实拥有画面](RESIDENT-SEQUENCE-NEXT-20261010.md)仅准备。旧故障未修、永久首启动／5Hz／长期／HDMI待。以下当前为历史。

> 2026-10-10当前：[同程序模型／VPU对照结果](MODEL-VPU-RESULTS-20261010.md)。前三阶段111前向1676100FP32及310合成图像通过，第四阶段首次capture前固件512KiB申请失败，Engine未创建。全部服务／连接关闭；[恢复点](evidence/model-vpu-20261010-r2/next-checkpoint.json)／[下一资源生命周期](MODEL-VPU-NEXT-20261010.md)。以下当前入口为历史。

> 2026-10-08当前：两缓冲启动三次回归及有限主线程Engine＋后台VPU三/27窗口通过，987原始编码帧全解码核验。[启动](VPU-STARTUP-RESULTS-20261008.md)、[常驻/预览](RESIDENT-RESULTS-20261008.md)、[恢复点](evidence/resident-20261008-r6/next-checkpoint.json)。下一在线owned AU/live555，保留原模型/数学/SDK/BOOT、主线程模式/两缓冲候选；旧后台Engine/六缓冲失败勿重跑。任务未被暂停，测试与SSH/SFTP已关闭，无后台。不是daemon/RTSP/整机5Hz/长期验收，预览名义10fps不当真实PTS；旧入口为历史。

> 2026-10-08当前：真实推理→渲染→VPU的有限内容链路已核验，两成功码流一致；无规整的新进程重复仍在固件连续页分配失败，**启动稳定性未过**。[结果/视频](PIPELINE-RESULTS-20261008.md)、[下一门检](PIPELINE-NEXT-20261008.md)、[检查点](evidence/pipeline-20261008-r6/next-checkpoint.json)。下一先取证REQBUFS/STREAMON页状态再依据证据修正，随后常驻上下文/有界实时/在线RTSP。属于失败停止，不自动规整/重试；旧阶段“当前/暂停”均为历史，整机/HDMI仍待。

> 当前RTSP首批已验证：200帧传输/重连与标准播放器100帧逐位原视频，有限上下文清理通过，无新依赖。[结果/录制视频](RTSP-RESULTS-20261007.md)、[F0接入准备](F0-INTEGRATION-PREP-20261007.md)。当前是预生成码流回放，在线VPU/实际推理合并、显式色彩、HDMI/整机长期仍待；旧未RTSP/暂停条目为历史。

> 当前最新：视频任务已恢复，真实27骨架/54帧有限编码及两独立上下文重复通过，主机完整核验，MMAP描述兼容修正已采用。[结果/视频](VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md)、[恢复入口](RESUME-VIDEO-20261007.md)。原推理/SDK/BOOT保持，HDMI1080p60未改时序，RTSP/实时合并/整机长期未通过。旧暂停和失败条目按历史保留。

> 当前暂停：真实骨架编码发生VPU固件MMU ABORT；[首批报告](VIDEO-SEQUENCE-RESULTS-20261007.md)、[失败核验](evidence/video-sequence-20261007-r1/failure-review.json)、[恢复说明](RESUME-VIDEO-20261007.md)。HDMI只读/离线色条已准备、无实屏写入，等待唤醒。Build-VpuSequence等新工具不是已验收生产编码器，不重跑失败包。

> 最新安排：[下一视频计划](NEXT-VIDEO-PLAN-20261007.md)、[恢复授权与来源检查点](evidence/video-next-plan-20261007.json)。已审查编码样片并允许HDMI测试，暂停解除。首批真实骨架动态文件＋当前BOOT HDMI配套，随后1080p60实屏/RTSP/真实推理合并；未新板测。

> 最新独立VPU：[720p10fps/30帧结果与MP4](VPU-RESULTS-20261007.md)、[执行位置/停止条件](VPU-COMMANDS-20261007.md)、[核验](evidence/vpu-20261007-r1/completion-review.json)。Build-Vpu/prepare_vpu_frames/run-vpu-stage/audit_vpu_stage/review_vpu_video为隔离工具，主机已有OpenCV，无新安装。HDMI目标1080p60、接屏不支持时序、测试暂停未改硬件；编码文件通过不等于RTSP/整机/长期。恢复读vpu新检查点，旧未编码记录为历史。

> 最新渲染与V0：[结果/预览](RENDER-RESULTS-20261007.md)、[命令](RENDER-COMMANDS-20261007.md)、[配套差异](V0-VIDEO-PAIRING-20261007.md)、[核验](evidence/render-20261007-r1/completion-review.json)。CPU画面与三格式通过，VPU实际只枚举MPLANE，编码/HDMI/RTSP仍待；恢复按render-r1检查点。

> 最新E1首批：[生产接口/TCP结果](APPLICATION-RESULTS-20261007.md)、[命令](APPLICATION-COMMANDS-20261007.md)、[完成核验](evidence/application-20261007-r2/completion-review.json)。当前入口为application_gate.py、Build-Application.ps1、send_application_cases.py；原P2/r6保持。下一阶段为渲染/视频配套，网络2Hz正确性不算整机5Hz。

> 最新：现有数值阶段已人工验收；profiling关闭＋单时钟计量及消息构造优化已完成，处理基线5.24655Hz/P95 190.75409ms，整机/视频/长期未验收。[P2结果](P2-RESULTS-20261007.md)。较早“数值未验收/4.65Hz/P2候选”保留为历史。

当前状态见[STATUS.md](STATUS.md)、已批准[全流程计划](FULL-FLOW-PLAN-20261007.md)和[应用检查点](evidence/application-20261007-r2/next-checkpoint.json)。旧N1/P2“数值/核心5Hz未通过”按历史理解，当前固定样本数值人工验收、核心短期5.25Hz；整机/视频/长期仍待，勿重复已完成门检。

<details>
<summary>历史工具交付和阶段说明（较早“当前/下一步”按当时日期理解）</summary>


当前快照r2已编译并独立核验，[构建结果](MIXED-BINDING-R2-BUILD-RESULTS.md)，构建验收文件已生成。
使用新r2目录传输后先Host107完整回传，不重跑r1/复用旧门禁，不直接apply或mixed。

当前已批准绑定快照r2并应用，新包准备完成，尚未编译/执行；入口[MIXED-BINDING-R2-COMMANDS.md](MIXED-BINDING-R2-COMMANDS.md)。
仅SDK公共元数据快照，保留原严格门检，先新构建/前置门检后apply取证无forward，旧r1不重跑。

当前SDK设备内存往返已通过，[结果](MIXED-MEMORY-RESULTS-20261006.md)；memory验收文件已生成。
仅300秒apply-check（创建/apply/绑定、无forward），回传核验后再单样本。前置步骤不重跑。

当前offline真实RAW/PS已独立验收，[结果](MIXED-OFFLINE-RESULTS-20261006.md)；离线验收文件已生成。
满足硬件前置条件后仅30秒memory-check并回传；Host/离线不重跑，不直接Session部署。

最新mixed-r1 Host桥独立验收已通过，[107例结果](MIXED-HOST-RESULTS-20261006.md)，host-check.acceptance.json已生成。
传板并回传提前offline的失败预检目录后再继续离线；不重跑Host或跳过门禁进入硬件。

最新mixed-r1构建已核验通过；[一条缩进警告审查](MIXED-BUILD-REVIEW-20261006.md)确认控制流符合预期，源码/包保持。
build.acceptance.json已生成；现在继续命令B传输，再C仅host-check。下述未编译为原交付状态，Lite新阶段仍未运行。

2026-10-06当前入口：[MIXED-VALIDATION-COMMANDS.md](MIXED-VALIDATION-COMMANDS.md)，
独立目标pose_mixed_check及SDK Host桥已交付、新测试包已准备；尚未编译/板测，先完成构建返回证据。
[ONNX三样本参考](ONNX-REFERENCE-RESULTS-20261006.md)已实际完成，
[范围与阶段](MIXED-VALIDATION.md)、[交付身份](evidence/mixed-source-delivery-20261006.json)。
工程/数值分阶段、ONNX直接对照Lite；不等待Icraft CPU Matmul，不把源码或参考通过当成mixed/双路通过。

状态与边界见 [软件说明](../../software/pose_v1/README.md)。此目录不包含已通过的完整推理/双路显示系统。

CPU最小候选已于2026-10-06完成Lite独立验收，见[结果](CPU-ADAPTER-RESULTS-20261006.md)：
107例、12条注册记录、22输出/59,600个FP32值逐位一致；当前仍未接入正式推理器或验证NPU数据交接。
下述未编译/运行是最初源码交付状态，完整证据已补入结果文档。

2026-10-05后新增[CPU最小注册适配](CPU-ADAPTER.md)和[人工操作命令](CPU-ADAPTER-COMMANDS.md)：
`cpu_adapter_gate.py`生成固定NumPy参考并复核回传，`Build-CpuAdapter.ps1`交叉编译独立候选，
`run-cpu-adapter.sh`在Lite进行一次受限CPU测试。源码已交付，尚未生成测试包/编译/运行；
不接入现有推理器、不覆盖Gather、不补CPU Matmul、不访问NPU/DMA/HDMI。

2026-10-05新增独立混合推理检查器配套工具，尚未编译/运行：

- [INFERENCE-COMMANDS.md](INFERENCE-COMMANDS.md)：逐条执行入口，先做A环境查询。
- `Build-Inference.ps1` / `aarch64-icraft.cmake`：从当前worktree独立复制并交叉编译，不自动运行二进制。
- `Run-HostReference.ps1`：仅Host参考，逐项校验既有独立DLL，只改子进程PATH。
- `inference_gate.py`：原三份真实CSI打包、ONNX参考、数值统计和回传哈希校验，不安装或访问设备。
- [HDMI-STATIC-AUDIT.md](HDMI-STATIC-AUDIT.md)：参考源码、时钟/时序线索及资料确认；未配置HDMI硬件。

下面历史脚本保留；软件/AI操作也人工执行，不沿用历史代理代执行授权。

- `Invoke-BoardAudit.ps1` / `board_probe.py`：严格主机密钥验证，读取FAT16启动分区、设备树。
  不挂载、不改启动文件、不访问未知寄存器；交互输入密码，不写入源码/证据。
- `validate_preprocess.py`：用实际训练AST、6个合成用例和固定9组300份真实MAT与FPAI的Linux主机C++比较。
  固定清单保留原3份回归；按批准幅度/相位周期策略门检，另报告标量差。生产C++未修改。
- `numeric_metrics.py` / `test_numeric_metrics.py`：主机与板端共用数值策略；人工±π只作非阻断诊断，
  真实相位标量差>1e-5 rad仍触发讨论，防止周期等价掩盖模型输入差异。
- `prepare_board_bundle.py` / `summarize_gate.py`：生成哈希核验的固定测试包，再联查窗口/参考/主机/板端身份。
- `inspect_selected_boot.py`：离线解析所选BOOT、.bit头部/载荷，对照新旧板端审计与启动日志。
- `read_fpga_version.candidate.py`：本次经单独批准仅只读回读0x4000001C=0x25122301；
  默认为只打印方案，再执行或扩大地址/SDK初始化范围仍须符合授权，不能当作通用寄存器访问入口。
- `Invoke-BoardPreprocessTest.ps1` / `board_preprocess_test.py`：核对测试包SHA256后在唯一`/tmp`目录
  运行arm64数值程序，报告误差及异常输入；不调用AI、视频或修改系统配置。
- `replay_raw_csi.py` / `csi_io.py`：原始数据客户端，板端接收服务尚未实现，不作为网络联调通过。
- `audit_assets.py`：只读记录所选模型、源码、生成物哈希及Host/NPU图分工。
- `test_replay.py`：Windows本机TCP回环，强制碎片读取验证3个原始窗口字节不变；不代表板端网络验收。
- `diagnose_phase_boundary.py`：只在离线参考中替换标量angle以排查边界；当前替换未解释C++偏差，
  不改变生产代码/训练文件，也不构成误差容限批准。

执行源码来自当前Codex worktree；FPAI挂载原`D:\FPGACompetitionProject`。本次源码明确复制到
容器`/tmp/pose-v1-source`构建，未修改原项目挂载、镜像、工具链或已安装SDK。
临时主机/arm64二进制、输入/参考张量在`.local/pose-v1-build`与`.local/pose-v1-validation`，不提交生成物。

`evidence/host-preprocess-initial-failure.json`保留零幅值移植错误；`host-preprocess.json`为修正后主机结果，
`board-preprocess.json`为实际板端结果。每个case的名称/原始文件由主机报告关联；不得抹去π边界失败。
本次实际数值参考是上述WindowsConda版本，不据此声称原训练服务器软件栈已重验。

最新300份门检、启动及运行版本结果见[RESULTS-300.md](RESULTS-300.md)；
`evidence/*-300*`与`board-runtime-audit-25122301.json`为本阶段新证据，旧9用例与原BOOT审计保留。
审计/板端复验须指定新的`-EvidencePath`，已存在的证据文件会被拒绝覆盖。

</details>
