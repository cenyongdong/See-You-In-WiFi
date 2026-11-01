# 六边界读路径观测v3：受控启动执行草案

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

2026-10-17。**本页是未获新启动授权的草案。候选BOOT尚未生成，完整候选门检尚未完成；当前不能安装、启动或重复失败负载。** 本轮阶段恢复后仅恢复已批准范围内的诊断，不重置r2已使用的候选启动／原BOOT回退额度。以下拟议范围须待真实产物、完整本地审查及针对本包明确批准后才生效。旧DATA独立暂停。

## 实际产物与审查入口

最终唯一运行参数入口为`tools/pose-v1/evidence/hdmi-live-20261017-r3/controlled-startup-read-v3/manifest.json`。当前不创建假清单、不填写候选占位哈希。根执行器须待实际BOOT／位流及构建结果产生后，保存真实绝对来源、字节数和完整SHA，并把本页修订为可审查的实际包后再申请确认。

| 对象 | 当前范围 |
|---|---|
| 候选BOOT／后处理bit | 尚未出；全部身份以最终manifest及完整读回为准，不套用v2 SHA |
| 原BOOT | 已知保护身份7,023,552字节／ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef，执行前仍须完整实读核对 |
| 独立DMA探针 | build-read-probe-r2实际构建通过，ELF SHA8b04513732e9d2c0a44bf4cb0a270808857b71fba0becf51a7f333d4000d9276；固定四档至1MiB、FreshBoot代数0→1→2，尚未新板测 |
| 三窗HDMI包 | read-shared-build-r2实际构建／完整15文件包核验通过，ELF SHAa9a4e8494427b2cf40656ee281133f69c57d46c75ea3472451e7025a2e4040eb、archive SHA49a6ef2a38d8e822dc47a1c67224aa0d2da20d1fa52933d5a6074b3d588e589c；显式AfterSuccessfulProbe代数2→3→4。旧r1首次0/0契约不能承接probe，完整旧证据保留，不部署旧包 |
| 模型／fixture | 固定共享JSON／RAW与12份三窗fixture、15文件完整包，保持原数值门禁、CPU注册及NPU分配 |
| 本机流程草案 | `.local/hdmi-live-20261017-r3/controlled_read_v3.py`仅离线检查manifest、绑定授权、生成阶段计划和独立审查回传probe文件；没有远程执行入口，不能把此脚本存在写成板测通过 |

完整候选放行至少需要：观测单元、实际六边界时钟／复位与总线位宽、CDC保持总线、整机综合／路由／STA／DRC、原厂工具补丁身份、BOOT非PL字节及载荷比较、ARM探针／共享包与双epoch契约均完成。原两个AI最小周期定点例外只在原对象／模型范围适用，不能扩到新观测时序或新DRC。原始失败报告及所有告警必须保留；不能只凭工具exit0或单个passed标志代替整包审查。

## 当前硬件来源修订与严格绑定

最新候选使用managed PS源路径：原完整生成`ps_ai.v`仅在原顶层追加三个被动输出及赋值，模块名保留`ps_ai`；该完整文件已经改变，不能称原generated fullPS逐字节未变。其余12个原模块、原唯一timescale，以及原BD／XCI／11份PS OOC内容保持。[managed-PS-observer-r2/review.json](../../tools/pose-v1/evidence/hdmi-live-20261017-r3/managed-PS-observer-r2/review.json)保存精确逆向复原与前后SHA：新fullPS为b87b798ce01c707027766660c501ed2232aaeaec5f093bc291e095ab1f637cb7，wrapper为502c463544a5cbc4e5af20460af274418e5f6c68661e92ee6a3eca9c8b3c86f2。

原v3改名全局顶层导致managed PS依赖／leaf缺失的综合失败、r2的scripts_only调度失败均保留，不改写通过。综合父运行仍为`synth_read_v3r3`，约束仍取`read-v3r3-constraints-r3`；当前候选只接受`read-v3r6-bootstrap`／`read-v3r6-route`／`read-v3r6-reports`／`read-v3r6-bit`及native `route_read_v3r6`，`managed_run:false`，不读取或伪造managed run状态。完整候选仍待实际门检。旧r3 route在720.625秒因日志only监控被停止，31份native文件冻结于route-monitor-policy-r1，不能记为Vivado逻辑失败或已通过。旧约束阶段113.078秒的clock绑定失败、constraints-r2的查询语义失败与partial CDC报告保留，不代替新约束阶段通过。

r4实际在1801.297秒达到1800秒硬上限并被monitor停止，route未完成、未见工具error，原`read-v3r4-route/execution.json`保留；r4只作物理检查点前驱，不要求其route通过。r5实际route724.875秒exit0、reports363.968秒exit0，但正式门按新增setup违例拒绝，`route-release-rejection-r5/execution.json`exit1且未生成review.json；原两个AI例外不覆盖新HDMI路径。r6继续使用同44,506,212字节physopt（SHA `f58a5f8e6f432be7e656de5ee32eae5ae63b491d5a5cb1055425ee32895525d9`），仅在原route后、第一次完整JFM route_post前加入一次四项物理优化；不改RTL／接口／频率／约束／豁免，但物理实现会改变。

planner逐份实读r6四phase真实execution／phase-review、DIRECTORY为`.`的context、guard、937源／41库、逐phase自有driver SHA与冻结物理算法AST、同r4检查点／r3综合约束来源。实际顺序固定为NoTimingRelaxation route、`phys_opt_design -placement_opt -routing_opt -rewire -critical_pin_opt`、首次完整原厂JFM route_post、原checkpoint和报告；三边界fully/errors原值及完整route-status报告均须通过。独立新review薄适配保留原全部STA／DRC门并证明逆AST，只在全部通过后独占写最终review。bit还须同routed／physopt SHA、完整原厂hooks／context、11字段实际release及精确两派生隔离门。缺任何实际产物就关闭，不借旧bit或放宽时序。

后处理／BOOT／最终包目录仍为`read-v3-icap`、`read-v3-boot`、`controlled-startup-read-v3`，源bit只接受`reference/fpai_demo_vivado.runs/route_read_v3r6/ai7030_edif_top.bit`。新packager薄适配固定旧完整算法与13处身份转换；actual／base／AST源均归档，ICAP与BOOT review同`candidate_run`且`managed_run:false`。新planner与全部helper／review／packager源码闭包均在local_review绑定，动态状态另查；本地准备不构成上板许可。

因离开板边已专项暂停候选BOOT安装／启动与HDMI现场观察，相关UART／reboot入口同样暂停；离线工作和只读证据继续。每次对应入口必须读取动态`onsite_observation_work.paused`且仅明确恢复为false后放行，不能以旧DATA暂停代替全任务状态；必要的已授权原BOOT安全还原不因此阻塞。该动态状态不纳固定local_review SHA，当前没有新启动许可。

## 拟议的限定操作

拟申请一次临时安装该实际候选BOOT并受控启动。SSH恢复后的首要动作是还原原BOOT文件、完整读回SHA并核对其它启动文件、sync／卸载；之后运行中PL仍为候选，此状态必须和启动文件已恢复分别记录。

仅在独立四档probe完整通过、全量文件回传与字节核对、观测代数2/2和正常释放均证实时，才运行新的三窗共享推理→HDMI包。必要时拟允许最多另一次原BOOT回退启动，仅恢复原运行状态。上述一次候选和一次可选回退均须新包明确批准；不得借用旧许可。SDK／数据／身份故障保存即停，不自动重试、重开失败Session、复位／清错或改epoch。

不改uEnv、DTB、内核、SDK、模型／数学、CPU/Gather注册、NPU分配、频率或帧协议；不做JTAG热重配、永久BOOT替换、FAT修复、清脏标志、清缓存、扩大CMA、PC展示或骨架网络协议。

## 授权与参数必须失败关闭

最终manifest必须绑定所有实际文件与本地完整门检原值。离线检查器默认`inspect`只读；manifest缺失、候选不存在、SHA／大小／非PL字节不符、任一门检缺失或失败均输出closed，不会联机。`authorized-plan`还要求显式`--approved`和新的回执，回执必须绑定本次manifest完整SHA、package_id=ai-read-v3、原文及限定次数；只提供CLI布尔值、旧v2回执或历史暂停前许可均拒绝。脚本不生成授权回执，也不能自行证明人类批准真实，根执行器负责由本次实际答复建立可信证据。

后续远程适配器的每个写入、启动、UART打开或负载入口，均须先调用同一授权门、检查当前暂停状态及该动作是否在允许表内，再核对实际前置证据。候选安装／候选重启／可选原BOOT重启分别使用主机与板端新目录的独占记录，先保留一次尝试标记再发命令；不因SSH断开或外层超时重发reboot。标记存在即停止并审查原命令／进程，不自动重置次数。再次暂停时禁止续跑。

## 批准后拟执行的有界顺序

1. Windows D:/FPGACompetitionProject，仅主执行器控制SSH、UART及板端。复核当前原BOOT／六SDK／内核／完整启动根文件、boot_id、挂载、存储余量和设备owner；owner空不证明硬件排空。复核实际设备、COM7 CP210x VID/PID/序列号及必要扫链身份，不固定历史part号。既有pinned Ed25519与内存askpass认证沿用，不把口令写argv／环境／日志。
2. 通过后在manifest指定的`/root/hdmi-live-20261017-r3/`之下建立新的持久子目录（建议read-v3），不使用会被启动清除的/tmp。完整保存实际原BOOT回读和主机独立原件，全部启动根文件身份存入新metadata。传输后逐文件SHA与长度核对，15文件tar只允许独立普通相对文件，拒绝链接／重复／越界／大包；固定模型与fixture全部符合才可继续。
3. 新UART记录仅115200/8N1、DTR／RTS关闭、0 TX，最多300秒／4MiB；保存真实PID、USB身份及ready，故障或超限保留原始rx.bin并关闭资源。UART是否ready不能替代BOOT／链目标／授权门。
4. 在该包新批准及原件双备份均成立时，核对/dev/mmcblk0p1实际块设备与FAT16结构，拒绝已有不明挂载。仅候选BOOT临时文件写入、fsync、完整读回、原子替换，核对其它启动文件仍逐字节同本轮基线，sync／卸载。已知FAT两表／2168未引用簇／状态字节1来源未明仍保留；一旦出现新链／交叉／身份／I/O异常停止，不能自行fsck或以已有问题为理由忽略新异常。
5. 独占记录后只发送一次受控候选reboot，SSH恢复观察最多180秒；每次只读连接新日志。收到SSH退出／断开不等于启动成功，必须新boot_id且板端可读。SSH不能恢复时保留UART并停止，不声称可自动回退；可能需要人工恢复介质及新的明确处置。
6. 新启动SSH恢复后，先完整还原原BOOT、fsync／完整读回SHA，其它启动根文件和SDK不变，sync／卸载。没有此证据不得调用Device::Open、DMA、模型或HDMI。还原启动文件与运行中候选配置分开核验。
7. 使用新进程和新证据路径执行manifest的`ai_read_dma_probe <trace>`，不是旧`ai_dma_probe ... --with-monitor`。子进程观察门限20秒、外层30秒；分配上限1MiB、64B对齐，四档64／4096／65536／1048576字节。公开SDK正常Open之后先验证身份／状态和ABI／104字／FreshBoot代数0/0，一次ARM到1/1；全部完整写读、先存全量source/actual再比较，四档间无新增快照或同步。原SDK异常先保存，随后sameDevice FREEZE104及旧v2 MIG各至多一次，继续停止原负载，不新Open／reset后伪造原现场。失败或在途不确定时保留分配，不擅自释放。
8. probe exit0且没有超时仍不是唯一门检：独立读取全量八个source/actual文件，核对长度、完整生成模式与逐字节相同；严格四个有序roundtrip_pass、1MiB实际分配、104字uint32／ABI原值及verified代数2/2、旧MIG24字、completed_and_released均须存在。六通道以`b=8+16*c`检查`words[b+3]`非OKAY响应握手计数与`words[b+12]`首次错误meta均必须为0（包括首次valid bit31）；任一非0保留raw并停止shared，不重试。任何SDK／数据／身份／诊断错停止共享阶段；观察寄存器恰为2/2或错误计数为0均不能单独证明probe通过、事务完成或硬件drain。
9. 仅前门检全过、同一候选boot_id保持、原BOOT启动文件仍已还原且无其它owner时，启动新共享包`pose_hdmi_demo <package> <fresh-output> --allow-device-init`。子进程观察120秒、外层140秒，一Engine沿用同一Device。新Open后观测硬件必须仍为2/2，显式AfterSuccessfulProbe一次ARM至3/3；若为0或任意其它代数则保存停止，不改FreshBoot或读取现场后自适应。三个固定真实窗口实际输出先完整保存再按ADR_48 v2比较，三帧各保持约5秒；重复扫描不计新推理。
10. Session.apply异常时先完整原错、同一仍存活Device FREEZE104与旧MIG，再继续原异常；main构造失败路径不解引用已销毁Device。成功仅在三窗全过、完整输出和HDMI安全STOP／匹配停止ID／idle／在途清零及帧释放均证实后，才同Device FREEZE到4/4、保存104字与MIG并销毁Engine。现场画面确认、PL采纳ID、数值、生命周期和吞吐分开报告；有限三窗不等于连续CSI／严格5Hz／长期验收。
11. 任何异常先保存完整stdout／stderr／trace／实际字节／内核／内存／owner／挂载／进程状态，回传归档并校验；不是把旧probe包装的SSH exit0当作child exit0。外层观察超时不能直接复制旧控制器terminate/kill：先辨识原进程是否仍推进、是否已START和是否能证明安全停止，记录PID及所有权，按既有超时规则监测原进程，不启动第二份负载或盲目释放在途帧。真实SDK／逻辑／数据错误仍立即停止受影响步骤。
12. 必要时只使用新批准的那一次原BOOT回退：前提是原BOOT完整恢复证据已存在、失败现场已保存、当前目标与UART ready正确，再独占记录并只发一次原BOOTreboot。不得追加BOOT写入或其它候选；恢复后只读核对新boot_id／原BOOT／SDK／operating，不因回退重新测试失败负载。若原BOOT无法确认已恢复或SSH不可达，则不能声称此回退可自动执行。
13. 收尾只回收本批可识别PID、UART、SSH和连接，保存所有失败与资源结果；没有未经要求的后台续跑。未证实硬件排空时保留相关帧／分配并记录，不拿owner空、ready、计数或Linux缓存操作代替完成证据。

## 旧控制器适配清单

| 旧实现 | 可复用部分 | 不得原样复用／需要的新门检 |
|---|---|---|
| W2 secure_transport.py；W3已有同名安全实现 | 内存askpass、pinned host key、严格主机、SCP限定目录、单次口令、有限ConnectTimeout及新日志 | W2 REMOTE硬编码r2；应使用现有W3允许根下的新子目录。SSH本身可执行任意命令，授权必须在每个上层动作入口，不能以运输成功替代允许执行；不得打印口令或复制Agents原文 |
| W2 stage.py | 每阶段新目录、原远程源码／stdout／stderr／执行结果保留 | EVIDENCE／WORK均r2；外层SSH0不代表子进程0，必须审查result／timeout。只会保存外层TimeoutExpired，不负责不明板端进程安全收尾，不能盲拷为完整监督器 |
| W2 start-candidate.py／start-original-fallback.py | 一条命令、独占本地记录、有限恢复轮询、UART stop请求 | 旧包许可文件、r2路径、旧boot_id和UART目录硬编码；旧脚本预检可能在真正reboot前因身份失败已退出，但“尝试”记录不能自行删除重试。新代数／候选身份从未来manifest和本轮实际启动记录取，不能替换几个字符串即宣称验证 |
| E2 install-candidate-code.py／restore-original-code.py | 块设备／FAT挂载核对、完整哈希、同目录临时文件/fsync/replace、其它启动文件比较、sync卸载 | v2候选SHA／文件名／临时名／r2目录／旧boot_id硬编码，元数据来自旧prepare。新脚本必须来自实际manifest且先批准；回退证据是本轮完整readback，不是旧目录restore.json |
| W2 capture-candidate.ps1／capture-fallback.ps1 | COM7只收、0 TX、1152008N1、DTR/RTSfalse、300秒4MiB、PID和finally关闭 | r2输出目录、v2阶段名，USB枚举身份必须重核；禁止盲关所有串口／进程。打开串口也不能隐式恢复暂停任务 |
| E2 dma-v2-code.py | 新stdout/stderr/trace、原子过程状态及有限监督 | 旧二进制／SHA／boot_id／命令行，24字旧探针。新的104字probe无--with-monitor选项，并保存八个完整字节文件；20秒后原脚本直接terminate/kill不应无条件继承 |
| 旧shared-r3-code.py／r2构建包 | 完整包SHA与fixture核验、单进程/新目录、记录PID、旧HDMI生命周期 | 路径、包SHA、模型与进程名、90秒门限和旧fresh0都过时；共享r2明确需要成功probe后的2→3→4。当前ABI／输出和完整回传必须由实际新包确认，不读旧日志判通过 |

## manifest与授权回执格式

审查器已改为实际离线packager的`{files: {实际文件名: 描述项}, ...}`格式，不再要求早期草案提出的roles/schema_version/gates字典。必需实体包括BOOT-ai-read-v3.bin、BOOT-original.bin、ai-read-v3_disable_icap.bit、ai-read-v3.bit、ai_read_dma_probe、shared-package.tar和五份实际元数据JSON。每项必须有真实bytes／小写64位sha256，实体文件source须指向本轮指定原产物；元数据source为packager的说明文本时，读取包目录中的实际JSON，逐字节核对manifest再与对应实际构建结果作语义核对。审查器实际逐字节比较固定原PL分区以外片段且要求PL确有变化，完整15文件tar及固定模型／fixture／ARM64 ELF全部核对。

本地门检从本节指定的r3综合／constraints-r3、r4 route／reports／bit、managed-PS-r2证明、r2软件构建／epoch mock读取，不允许manifest改指旧阶段或随意指定某个passed文件。审查器还保存各实际门检JSON的SHA，形成local_review_sha256；完整原报告及原始时序例外仍保留。

当前packager只产离线包，因此根执行器在实际产物和最新只读板端审查完成后、申请新批准前，仍须在manifest追加经过审查的`execution_context`（不能从旧r2文件默取）。其中package_id为ai-read-v3；`board`填写host192.168.126.49／user root、新remote_root、boot_device、uart_port、实际uart_usb_identity、本轮pre_start_boot_id、六SDK和九份startup_files（每份size／sha256）；内核由IMAGE完整字节身份保护，旧kernel_sha256字段实际仅dmesg日志SHA，作为审查证据保留，不用于跨启动内核身份判等。动作前仍须重核。`contract`固定四档、1MiB、probe_epoch[0,1,2]、shared_epoch[2,3,4]、three_windows3、old_DATA paused和filesystem_repair false；`budgets`固定上文20/30、120/140、恢复180秒、UART300秒/4MiB/0 TX。缺execution_context也必须关闭，不将离线包当成可启动计划。追加后保存修订SHA，绑定最终manifest，不能回写成原packager输出未变。

新授权回执必须由根执行器在实际后保存，包含approved与active为true、approved_by=user、原始user_confirmation、准确manifest_sha256与local_review_sha256、相同package_id、允许动作列表和caps（candidate_boot_installations1、candidate_reboot_commands1、original_fallback_reboot_commands1），同时保持old_DATA paused／filesystem_repair false。每次远程动作仍需动态前置状态及一次记录，不能以JSON存在覆盖后续暂停或失败停止。

最终`execution_context.adapters`还须按`planner`、`generator`、`startup_controller`、`secure_transport`、`executor`五个固定role，填写`{path:实际绝对路径,sha256:实际源码SHA}`，分别指向W3/controlled_read_v3.py、W3/prepare_remote_read_v3.py、FPGA/hdmi_candidate/scripts/control_ai_read_startup.py、W3/secure_transport.py和W3/execute_read_v3.py。审查器逐字节核对五份实际源码并把SHA纳入local_review。源码在形成最终manifest前冻结；源码不包含最终manifest实际SHA，不产生循环。任一适配器改动必须生成新的实际manifest／门检及对应新批准绑定，不能沿用旧批准。

## 现有结果与仍未知项

[r3完整报告](../../tools/pose-v1/evidence/hdmi-live-20261017-r3/REPORT.md)、[新观测CSR契约](diagnostics/ai_read_monitor.README.md)、[共享构建与epoch限制](scripts/build_ai_read_shared.README.md)、[r2历史执行包](CANDIDATE-AI-MONITOR-V2.md)。D45根因未证，新被动观测的实现扰动仍在；FAT问题未修。实际候选身份与完整放行结果产生后，根执行器须补足真实产物段、授权问题及复核，不把这份草案当作已批准执行包。
