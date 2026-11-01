# NPU生产者与首次读取异常的取证历史

2026-10-13从AGENTS.md迁出，按主题保存原记录；原文“当前”“已批准”“下一步”和暂停/恢复只表示当时状态，不是现行进度或新的执行授权。最新进度见[PROJECT-PROGRESS](../../../PROJECT-PROGRESS.md)，执行规范以[AGENTS.md](../../../AGENTS.md)为准。源行编号与迁移清单用于追溯；不改写原失败、修订或验收边界。

<a id="a009"></a>

## A009 · 目录预建与物理失败晚源本批结束（2026-10-11）

来源：整理前 AGENTS.md 第9–10行。

- 目录预建与物理失败晚源本批结束（2026-10-11）：PRODUCER-SOURCE-READ-NEXT，ADR_44。r1 d3772b3c…b22ef875，Native/ARM目录126拒绝/四100唯一空路径/顺序拥有令牌/线程/保存兼容过，原152及上批源读实现保持，Host CPTR8输出188160字节过。four4/off100/on前94合198完整正确2328480FP32；第199次即on inv94/A首DATA96有限值全逐位上一B同偏移，6×64B/stride256/phys0x6816000…6500，INDEX全对。首次拥有FNV与错误文件绑定（在保存后记录，非早期即时采样）；两轮四物理Tensor::read94080字节全部正确，第一晚源在初copy结束3.42335ms后，ready/count11非fence。租约4/100/95全部关/forced0，异常停止，原首次文件未修，预建call95–99空；不重跑失败Session。准备0.56224/12.41432/11.84572ms，热令牌max0.00723/0.06393/0.08171ms，初50/序列60/总180/5.05绝对槽保持；数据保存max166.99851ms仍待，未目录/截止失败。309raw/308归还/308packet56763B/307 NoInput连续/1844ioctl/190copy交叠非fence，两abort STREAMOFF0/join后scopeSession毁/prefix1→0/allSDK0，非正常drain。资源audit101→101/规整0，pgmajfault3其余allocstall/reclaim/OOM/compact0；最终BOOTSDK模型内核同/FPGA operating/本批程序管理器端口代理连接全闭，732908/27204KiB仅现场。Host初本机解包拒测试symlink保留tar/partial，仅普通字节＋链接元数据适配及4非法路径拒绝过，无板测重跑。目录整改过，root/on100/完整103/严格5Hz/长期/HDMI未过，管理83/100保持。当前PRODUCER-PREPARED-RESULTS/NEXT及producer-prepared-20261011-r1 completion/next-checkpoint；下一匹配copyFrom/read静态链＋首次Host目的寿命/失败CPTR公开快照仅准备，原错误物理读取不删。以下实施中/当前为历史。

<a id="a011"></a>

## A011 · 放行前目录准备实施（2026-10-11）

来源：整理前 AGENTS.md 第11–12行。

- 放行前目录准备实施（2026-10-11）：PRODUCER-SOURCE-READ-NEXT；新增独立SDK无关独占根/四或100空目录及顺序一次拥有令牌，热领取仅内存，目录准备在deployment.ready之前且沿用初始50秒门禁。真实输入/identity/stages/outputs保存位置、保存后比较、单调用源租约/失败四read和原异常读取保持；不同时延迟落盘/改存储/时隙或SDK。原152源码保持，按Native/ARM合同与HostCPTR→four→off100→on最多100，失败保留停止，不延长或重跑失败Session。ADR_44为本批独立决策，结果待验。

<a id="a013"></a>

## A013 · 单调用输出租约本批结束（2026-10-11）

来源：整理前 AGENTS.md 第13–14行。

- 单调用输出租约本批结束（2026-10-11）：PRODUCER-ADDRESS-NEXT，ADR_43。r2 9772a0e1…30853b28，Native/ARM范围/代次/线程/寿命/拥有值/零正常读/诊断清理失败仍原错过，ARM Host CPTR8输出188160字节逐位，无物理Device/Session。新Opaque Scope保留真实outputs到compare结束，正常关闭，下次reset拒绝活租约，销毁Session前失效；失败四read/94080字节模块已构建，实际尚未触发。four4/off100/on前49合153前向1799280FP32及输入全逐位/有限/0→11，租约4/100/49开关相等、forced0/源读0。on计划inv49/B目录create915.85662ms CPU0.29944ms自愿切换2缺页0，随后Host/journal约0.92314ms；原绝对截止在reset/forward前拒绝exit1，保存B输入无outputs/trace/late-source/call50，未当on100通过或原DATA800修复。4842事件，阶段allocstall/reclaim/OOM/compact/pgmajfault全0；目录API内等待已定位但FS/存储/调度责任未证。225raw/224归还/222ownedpacket41056字节/221 NoInput解码ID0–220正确，1340Q/DQ两缓冲单线程/98copy全交叠非fence，尾四未解码/两abort STREAMOFF0/正常drain-LAST未过；join后Scope/Session毁/prefix1→0/allSDK0。资源只读普通512单位196→196（早off197），规整0/无清缓存重启CMABOOTSDK模型变化，最终733520/27876KiB仅快照，stage/final内核同/FPGA operating/本批程序管理器端口代理连接全闭。r1 Host缺Network头编译失败及误续审计衍生缺build-result保留，r2补头分开构建审计，无r1板测/失败Session重跑。原152软件/745/数学waitcopy保存/正式异常读回保持。ADR_43、PRODUCER-SOURCE-READ-RESULTS/NEXT、producer-source-read-20261011-r2 completion/next-checkpoint当前；下一放行前预建目录/有界一次令牌仅准备，不同时移动数据落盘，继续失败只读但不强行触发，根因/完整103/严格5Hz/长期/HDMI待，管理83/100保持。以下当前为历史。

<a id="a015"></a>

## A015 · 独立高地址生产者本批结束（2026-10-11）

来源：整理前 AGENTS.md 第15–16行。

- 独立高地址生产者本批结束（2026-10-11）：PRODUCER-PHASE-NEXT，ADR_42。复用匹配ARM分配链并核当前三头／XRTAXI身份，Native/ARM地址12拒绝、载荷9、Trace/时隙/ioctl过。r2 745a6aae…b0e9e3f，104MiB自动SDK前缀4096起/auto_free/4096对齐无读写，9块非重叠，输入109088768/109068288、输出109113344/109092864非OCM/owner/尺寸/别名正确，在104–105MiB带非正式精确布局。每Session放行前真实往返/部署核验；四调用47040＋off100 1176000＋on前49 576240全逐位/有限，合153完整1799280值。on第50次inv49/B两输出保存后数值exit1，call50不存在；4386 DATA800有限值全部逐位同inv48/A同偏移，31段12×64＋19×128字节/起点64对齐，4390 INDEX4200全正确，输入全B/0→11/source_ready真/地址身份稳，forward431.12μs/copy156.82及88.21μs无尖峰。既非候选微误差也未证明缓存或NPU责任，首次复制拥有值已错；隔离源局部句柄已结束，没有晚源read，不重开追读，原正式异常读取冻结保持。1282 Q/DQ单线程fd6/两端2，100copy全交叠非fence；216raw/215归还/215ownedpacket40561字节/214 NoInput解码ID0–213前缀正确，尾两未解码，两abort STREAMOFF0/join后Session毁/prefix1→0/allSDK0，正常drain-LAST未过，summary0不是实际无工作。资源只读254→254，规整0/无清缓存重启/CMABOOTSDK模型变化；stage/final内核同/FPGA operating/本批程序管理器端口代理连接全结束，最终694740/2024KiB仅快照。r1只编译未上传，r2加强异常Device存活期前缀销毁；本机失败审查事件数4898→4896修正不改程序/数据不重跑。原152软件/745/数学/wait/copy/保存保持，管理83/100/完整103/严格5Hz/长期/HDMI待。ADR_42、PRODUCER-ADDRESS-RESULTS/NEXT、producer-address-20261011-r2 completion/next-checkpoint当前；下一单调用公开源租约＋失败两轮Tensor::read仅准备，无新源读取、无读晚值修补。以下当前为历史。

<a id="a017"></a>

## A017 · reset前分段及绝对时隙本批完成（2026-10-11）

来源：整理前 AGENTS.md 第17–18行。

- reset前分段及绝对时隙本批完成（2026-10-11）：PRODUCER-VPU-NEXT，ADR_41。同b81835cd…3c9e06f，新Trace有界16384／每阶段9800，Native／ARM载荷9拒绝、时隙／ioctl及容量线程异常返回值／迟到不前向合同过。SDK诊断副本仅观察＋reset前原绝对截止，原152冻结软件／producer_sdk／VPU源码／数学／等待／复制／数据保存位置／异常读取及SDK模型RAWBOOT保持。off100/on100共2352000FP32及输入全逐位／有限／0→11，准备结束与最终绝对时隙独立核验过，exit0/stderr空，旧1763ms尖峰及正式192坏读未复现未修；物理迟到拒绝未触发。最长leaf为输入486保存off46.84692ms CPU0.20014ms自愿切换1/on42.52643ms CPU0.33235ms自愿切换2、缺页0，区间等待已观测但IO/存储/调度根因未证；on Host分配0.06657/write0.03287/journal flush0.07562ms，forward最大3.72188ms CPU0.34671ms切换1非纯NPU。307raw提交归还、309ownedpacket56763字节含头及空LAST、307解码ID0–306/NoInput正确，1844公开Q/DQ单线程fd6/type10/9各2，200copy全交叠提交capture跨度非fence，正常drain-LAST/两STREAMOFF/join后SDK毁块0过，无新姿态吞吐／完整Engine／Host107／TCP/HDMI。一次自主规整326.36828ms普通512单位2→149，无清缓存/重启/CMABOOT变；最终694424/1864KiB仅快照，BOOTSDK模型内核同/FPGA operating/本批程序管理器端口代理连接全结束。r1打包旧管理器名错误在合同/Device前停止保留，r2新包复用同ELF修正并ARM过，非失败Session重跑。ADR_41、PRODUCER-PHASE-RESULTS/NEXT、producer-phase-20261011-r2 completion/next-checkpoint当前；下一公开SDK高地址布局可行性仅准备，不能猜地址或与保存优化同时改动。原异常读取／745保持，管理83/100／完整103／严格整机5Hz／长期／HDMI待。以下当前为历史。

<a id="a019"></a>

## A019 · 独立生产者／VPU对照本批结束（2026-10-11）

来源：整理前 AGENTS.md 第19–20行。

- 独立生产者／VPU对照本批结束（2026-10-11）：PRODUCER-GROUP-NEXT。r2 5dde91e1…32b0a同身份18来源／152冻结软件，Native／ARM载荷9拒绝、时隙及ioctl透传合同过。无VPU100调用1176000FP32全逐位／有限／0→11／时隙过；有VPU先实际capture后主线程Session及真实往返，82调用964320FP32全正确，inv81保存比较后因Call exhausted slot退出1、无call82，不记100通过。合182／2140320值，正式192坏读未复现未修。inv81 reset前1763.68731ms空档，随后forward460.98μs／copy91.12及109.15μs；空档含目录／输入身份写盘、SDK Host输入校验分配写入和调度，未拆分，不归因已证IO或NPU。当前仅调用开始检查时隙，准备结束无二次门检，迟到仍完成该一次前向后停止、无追帧。VPU Q/DQ间1655.39453ms空档，最长ioctl1.6711ms；阶段allocstall/reclaim/OOM/compact0、pgmajfault17未定位。1628公开记录／单VPU线程／fd6／NV12type10及H264type9／各2buffer，164copy中162交叠提交capture跨度非fence；271ownedpacket47878字节含参数头，270解码ID0–269正确，272raw提交／271归还，尾两未解码，全部NoInput不计新姿态吞吐。两abort STREAMOFF0／join后SDK毁块0，正常drain-LAST未过；冻结summary0计数字段因abort未返回不能当无工作。一次自主规整161.29668ms、普通512单位7→34，无清缓存／重启／CMABOOTSDK模型变化；阶段及最终内核同，FPGA operating／全部本批程序管理器端口连接结束。最终694568/106916KiB仅快照。Native r1期望+1ns错误／只读收尾r1 Host清单KeyError与新r2修正保留，无失败硬件重跑。ADR_40、PRODUCER-VPU-RESULTS/NEXT、producer-vpu-20261011-r2 completion/next-checkpoint当前；下一reset前应用与SDK分段单钟／准备后绝对截止检查仅准备，原异常读取／745／CPU分工保持，83/100／完整103／严格整机5Hz／长期／HDMI待。以下当前为历史。

<a id="a021"></a>

## A021 · 独立19成员真实生产者本批完成（2026-10-11）

来源：整理前 AGENTS.md 第21–22行。

- 独立19成员真实生产者本批完成（2026-10-11）：PRODUCER-REFERENCE-NEXT，新增ADR_39。r1 4a6a7251…a8da0494载荷ARM/9拒绝过，但mock第一输入返回全零99差异exit1；板端/FPAI mock库d6606416…1557776的PLDDR读写各ret，能力假设错误，不是正式坏索引证据，未物理NPU/重跑。新r2 0183e2a0…d17d7d5六匹配头/四SDK库/152冻结软件不变；Native/ARM载荷拥有值/9拒绝、mock部署及35360字节HostCPTR过。真实apply原19→9185/sync0→11，四边界非OCM、两输出61440/40960属SDK chunk/8467/8479别名；独立临时PLDDR35360字节往返在前向前逐位，代理核对后同Session固定A/B/A/B四调用，保存后比较47040FP32全有限/逐位/A≠B/重复同、每次0→11，SDK块释放0。单钟forward196.88–461.61μs/copy55.75–145.73μs仅四次局部跨度，不作纯NPU或性能；首reset至末拥有约10.04ms/管理器9.16秒不混。原CPU/Gather/桥/模型/RAW/SDK/BOOT/CMA、745及异常读取保持，无VPU/显示/TCP/新Host107/规整/清缓存/重启，仅4次帧reset(1)。只读收尾C locale旧启动©转义原字节差异保留，新UTF8只读与物理阶段逐位同，未硬件重跑；最终BOOT/SDK/内核同/FPGA operating/程序管理器结束/代理SSH/SCP闭，750384/26472KiB仅现场。当前PRODUCER-GROUP-RESULTS/NEXT、ADR_39及producer-group-20261011-r2 completion/next-checkpoint。低地址无视频四调用未复现正式并发，根因未修，83/100/103/严格5Hz/长期/HDMI待。下一同身份无/有VPU各固定100次5.05Hz有界对照仅方案准备，未接入/运行，原异常读取不删。以下当前为历史。

<a id="a023"></a>

## A023 · 真实融合组参考本轮完成（2026-10-11）

来源：整理前 AGENTS.md 第23–24行。

- 真实融合组参考本轮完成（2026-10-11）：PRODUCER-CONTRACT-NEXT，新增ADR_38。沿既有manifest找到原adapted图，19个来源／Value／dtype全对应；XIR-only RAW检查器1c26d038…7bfb3af通过三原RAW的MD5，22项导出、6144指令字节，8507实际96字节42个FP16一＋6零，adapted逐位同／optimized42个FP32一。公开lazyFileOffset源字节核验，两FP16/TF32精确可表示图案23520FP32与标量地址／原Matmul逐位同、重放同，逻辑TF32数组不作物理19位编码或一般舍入证明。mock7cc0e0b6…c028884公开19成员view创建/apply过，有效组9185/sync0→11，边界400/17280/30240/16800、四非OCM／输出别名；两日志8016/655字节，模拟地址不作物理地址。mock有模拟Device/Session，无物理NPU或forward；正式9186/223→234/最终745、CPU/Gather/数学/桥/模型/RAW/SDK/BOOT保持，Host107引用旧批不新跑。r1 HardOp→bool编译失败，新r2 defined()修正，旧源码/日志保留；tar板钟警告保留不改钟。两阶段exit0/stderr空/跨阶段内核同，规整0，无VPU/TCP/重启/清缓存/CMA变化；程序/SSH/SCP结束，最终751576/21992KiB仅现场。当前PRODUCER-REFERENCE-RESULTS/NEXT、ADR_38及producer-reference-20261011-r2 completion/next-checkpoint。下一独立物理apply核对真实段／sync再固定A/B/A/B四调用，尚未物理候选/前向；原异常读取保留、根因未修、83/100/103/严格5Hz/长期/HDMI待。以下当前为历史。

<a id="a025"></a>

## A025 · 生产者契约本轮结束（2026-10-11）

来源：整理前 AGENTS.md 第25–26行。

- 生产者契约本轮结束（2026-10-11）：AXI-READ-NEXT，ADR_37。六匹配ARM/Windows头和ZG/XRT完整符号核验；检查器layerCount≥阈值后有条件区域copy/PL→PL DMA，实际触发及DDR完成未证。XIR-only e51ea127…da1d47在ARM三视图过、无RAW/Device/Session；8629/8631为零指令零层Cast，原9186组19成员11层/223＋11＝234、输入486及带填充FP16的478，独立参考未闭合，未独立NPU测试。官方apply/log复用36冻结对象，r2 8576af7f…5e1bbe7 exit0已有两日志；r3 97641b15…40864be错预期1而实际2、exit1，均无forward/VPU。两日志418328/56218字节核验，8467/4386共址109232128，8479/4390共址109285376，均非OCM、同旧失败。首次rg受Git忽略误判r2日志缺失，目录缺陷推断撤回；普通流目录契约不证明官方log故障。两文件门检修正r4 7ec4e3cc…2e27b78仅编译未板测，不伪改exit1/重跑。12注册/原七组/参数通过，CPU/Gather/桥/模型/RAW/SDK/BOOT保持，Host107引用前批不重跑。FPAI头缺失/ISO宏/旧头告警/传输前路径清单错误与修正留存。全内核同、规整0、进程端口/SSH/SCP全结束；最终MemAvailable751964/CmaFree37600KiB仅现场。现读PRODUCER-CONTRACT-RESULTS/NEXT、ADR_37及producer-contract-20261011-r2 completion/next-checkpoint。下一先公开RAW仅读、实际19成员参数/布局/NumPy参考闭合，再考虑只透传公开UDMA属性的有界观察；无现成strace/未安装、无新动态观察。根因未修，原异常读取保留，83/100/完整103/严格5Hz/长期/HDMI待。以下当前为历史。

<a id="a027"></a>

## A027 · AXI／UDMA读取对照本批完成（2026-10-11）

来源：整理前 AGENTS.md 第27–28行。

- AXI／UDMA读取对照本批完成（2026-10-11）：READ-PHASE-NEXT，ADR_36。匹配AXI/XRT/板端UDMA模块确认16MiB暂存、mutex/状态轮询、CPU缓存同步；不能视为NPU/DDR完成证明。独立r4主b2f7db68…73fec7/Hosta1823244…86406c/manifestde0ace33…bf975，25来源；Host376320字节/8拒绝、四模式400动态对4704000FP32过，NumPy400指纹/保存141120FP32过；真实192 dtype/布局/全有效声明，较高PL地址100667392/100697664，前缀不访问。原CPU/Gather源哈希同，Host107引用上批非新跑，无Session/NPU。两VPU226/229合成图像实际PTS/解码/drain-LAST/STREAMOFF10/9/全块归还/join后SDK毁/内核同通过，NoInput不计姿态吞吐。页准备17/83，规整0；最终MemAvailable714320/CmaFree37544KiB仅现场，项目进程端口及SSH/SCP全结束，无后台。r1头名/r2命名空间与char*Werror/r3const签名失败保留，r4修正；原归档权限以byte-only readable副本解决审查，不改数据。未复现旧坏索引，根因未修，原首次快照与异常两晚源保持。当前AXI-READ-RESULTS/NEXT/RESPONSIBILITY及evidence/axi-pair-20261011-r4 completion/next-checkpoint；下一生产者/事务完成契约方案未执行，不猜同步/延时/私有映射或改SDK/BOOT，83/100、103完整/严格5Hz/长期/HDMI待。以下实施状态为历史。

<a id="a029"></a>

## A029 · AXI/UDMA读取对照实施（2026-10-11）

来源：整理前 AGENTS.md 第29–30行。

- AXI/UDMA读取对照实施（2026-10-11）：READ-PHASE-NEXT。新增ADR_36，匹配AXI/XRT/板端UDMA模块静态审查，确认16MiB暂存/锁/状态轮询/CPU缓存同步路径，不以未见fence认定缺同步。独立公开API读与copy模块r4，25来源，原CPU/Gather/模型/SDK/BOOT不改；Host376320字节/8拒绝及无VPU两模式各100动态对通过并独立NumPy核验，尚未NPU/Session。下一按已批准有限两缓冲VPU并发对照，每模式新进程新目录、先实际capture后SDK；资源策略按自主规整权限记录前后，不以通过宣称根因已修。r1打包头名错误/r2命名空间及签名Werror/r3签名失败留存，r4修正，不放宽门禁、不重跑旧Engine。本条实施状态待结果更新。

<a id="a031"></a>

## A031 · 首次复制返回／CPU前快照本批完成（2026-10-11）

来源：整理前 AGENTS.md 第31–32行。

- 首次复制返回／CPU前快照本批完成（2026-10-11）：r3程序731078a2…199ba／manifest87a20566…c39e7，403包154来源39冻结ELF逐位。SDK无关ReadPhase只192.slot1两拥有快照，原copy／数学／同步／最终源和CPU捕获保持，无第二设备read或坏值修补。Native8拒绝／ARM／Host107／12注册59600及原Gather过；实际final_evidence桥三观察点和目标对象链接核验，四窗4返回60400、8快照33600FP32逐位、32上游、492编码462网络全4来源／实际PTS／像素2716关节／正常drain-LAST通过。唯一固定QPC5.05诊断48正确724800后inv48／frame100049／S52_18_317在192失败，立即快照592变化589非整数0非有限，CPU前510.2μs及原失败Host不变，全部592逐位等于紧前slot0同偏移，两晚源94080正确；49快照阶段变化0，目标模64=0，对象稳／392查询234非fence。384边界48完整组，当前未到442；源／SDK／DMA／cache责任未证，包装器174.94μs非纯DMA。50接收49消费48返回1覆盖，51发送非ACK；48root/presaved及原8＋上游1＋阶段1全保存。389采样386图像356网络仅46来源，尾46/47未capture，1288关节前缀，不记103／正常drain或5Hz。两abort／子回收／network0／join后Engine毁／内核同／端口释放，全测试和连接关闭；范围r2一次规整143.23443ms，r3两准备普通512单位20无规整，未清缓存/重启/CMA/BOOT/SDK改变。r1Werror／r2权限126／r2观察桥未链接保存失败及r3新修订、r6＋N1参考补309/310均留存，r2四数值和503/473内容正确不补整批通过。当前ADR_35、READ-PHASE-RESULTS/NEXT及evidence/read-phase-20261011-r3 completion/next-checkpoint；下一先匹配AXI／共享UDMA暂存实际read完成和互斥，方案仅准备，根因未修，管理83/100、严格5Hz/103完整/长期/HDMI/零拷贝待。以下实施中为历史。

<a id="a033"></a>

## A033 · 首次read／CPU前Host边界已批准实施（2026-10-11）

来源：整理前 AGENTS.md 第33–34行。

- 首次read／CPU前Host边界已批准实施（2026-10-11）：UPSTREAM-BOUNDARY-NEXT。ADR_35新增独立ReadPhase拥有值及薄SDK适配，仅192.slot1保留原copy并在返回后／CPU前各拥有16800字节；无第二设备read、坏值修补或数学／同步／SDK变化，原Gather／ZG与异常两晚源保留。r1 Native缩进Werror编译失败留存，r2只新测试文件修正；Native8拒绝／所有权／首四＋末帧／部分错误通过，403包154来源／39冻结ELF构建身份通过，程序a80a1bca…698f74、manifest5d178f3c…967f1b2。板端Host107／新ARM契约执行中，尚未本批NPU／VPU；通过后四窗，再一次固定QPC5.05／103有界诊断，180秒、失败保存停止，不重跑旧失败或调频。当前evidence/read-phase-20261011-r2及ADR_35；旧上批完成保持。

<a id="a035"></a>

## A035 · 公开上游边界本批结束（2026-10-11）

来源：整理前 AGENTS.md 第35–36行。

- 公开上游边界本批结束（2026-10-11）：r4程序2534bdac…08eb7b／manifest7ab71582…a25cf6，403包146来源36冻结ELF逐位。Native／ARM／原Gather单view Host NumPy／Host107／12注册59600通过；四窗口4返回60400、32边界、495编码465网络全4来源／实际PTS／像素／正常drain-LAST通过。唯一固定QPC5.05诊断55正确830500后inv55／实际frame100056／S11_32_349在192拒绝，初始Host索引1584变化1582非整数0非有限，两轮晚源94080字节逐位旧参考，数据正确。57接收56消费55返回1覆盖，不能以inv推传输ID；55root/presaved及原8＋独立1保存全成功，440边界元数据首四完整字节，当前失败未到442。public producer句柄不是Session私有输入映射证明，9189另有未观测量化FP16 Value1860。407图像377网络仅52来源前缀，尾52/53/54未capture，未103或正常drain验收。886身份443复制279Host地址稳定、448查询234不是fence；瞬态初次read／暂存责任未证。r1节点归属/r2裸Gather139/两Host探针/r3误打包身份阻断/r3九保存预算失败及本机实际传输ID审查修正保留，r4调用侧原8＋独立1解决保存不改旧flush或数学。r3/r4四窗各规整148.45488/225.37927ms，诊断普通512单位68无规整；无清缓存/重启/CMA/BOOT/SDK变化。两abort/子回收/network0/join后Engine毁/内核同/端口释放，全测试和连接关闭，未自动重试。ADR_34、UPSTREAM-BOUNDARY-RESULTS/NEXT及evidence/upstream-boundary-20261011-r4 completion/next-checkpoint为最新，下一先审查SDK读完成契约及首次read后/CPU前拥有快照，方案准备未执行。根因未修，83/100、严格5Hz/长期/HDMI/零拷贝待。以下实施中/当前为历史。

<a id="a037"></a>

## A037 · 上游公开边界观察实施中（2026-10-11）

来源：整理前 AGENTS.md 第37–38行。

- 上游公开边界观察实施中（2026-10-11）：FINAL-EVIDENCE-NEXT。新模块通过公开post按Value4406/1137/1148/4414/4418取生产者，pre向量是outputs，不当inputs；保留句柄取样不是私有tmap快照。八点/每帧101600拥有字节/首四与最后帧/824元数据上限，主线程清除；原Gather注册/数学/SDK/BOOT/profiling-off/745保持。Native7拒绝/线程/字节/部分JSON过，146来源/403包编译核验，36冻结产物逐位复用且旧构建不写。r1 Host合成节点Value所有权构造失败未运行Gather或设备保留；r2只改独立测试节点，产品222b0816…c848e05同，Host-only验证中。当前ADR_34与evidence/upstream-boundary-20261011-r2/in-progress-checkpoint，Host/三窗过后一次固定QPC5.05有界诊断，不重跑旧失败、调频或猜cache。下方已完成为前批历史。

<a id="a039"></a>

## A039 · 最终门检晚源与完整保存完成（2026-10-10）

来源：整理前 AGENTS.md 第39–42行。

- 最终门检晚源与完整保存完成（2026-10-10）：新bca60bb4…1cc86a3/manifest8f0adfb2…03afcd2，403包/138来源，33原ELF逐位。Native/ARM/Host107/12注册/59600及三窗4次60400、490编码460网络全内容通过。一次固定QPC5.05 inv24/S53_02_301姿态128有限值失配max0.2705078125，前24正确；25root/presaved/时钟及八保存成功，解决重复oracle阻断。四源两轮134400读全成功，582/649更新晚源均同bad Host；437正确，真实RAW＋actual输入NumPy与582CPU/649到最终各4200逐位。400对象/200输入无变，192计数200均234但非fence；late共享SDK路径且可物理复用，根因未证。345图像/315RTSP仅前缀/23源，正确尾23未捕获、bad24未发布；abort两STREAMOFF/子回收/network0/join后毁/内核同/端口释放。规整0，资源21/16，未清缓存/重启/CMA/BOOT/SDK改变，全测试/连接结束。r1编译Werror及根脚本误指package未启动Host保留。当前FINAL-EVIDENCE-RESULTS/NEXT、ADR_33与evidence/final-evidence-20261010-r2 next-checkpoint，下一公开442与ZG9189/Hard8131边界观察待准备，不重跑旧失败/调频/覆盖Gather或继续停止Engine。管理83/100、严格5Hz/长期/HDMI待。

以下“当前”与实施中条目为历史。

<a id="a043"></a>

## A043 · 最终输出失配取证实施中（2026-10-10）

来源：整理前 AGENTS.md 第43–45行。

- 最终输出失配取证实施中（2026-10-10）：COMBINED-READ-NEXT。隔离final_evidence新增SDK无关拥有值Recorder、公开Tensor句柄/read适配和无oracle保存器；保留582/649四源67200字节、437/582三CPU输出17600字节，主线程每帧清除。最终比较失败在Engine存活且无下一forward/reset时两轮晚read，可能物理复用，不当原生产时刻证明。返回先完整保存再严格比较，结束保存全部记录不重复oracle。r1构建SDK测试缩进Werror停止未板测，保留；r2 Native7拒绝/部分read/线程/原值保存与原有限/NaN错误通过，交叉编译中。新目录Host107→原三窗→一次QPC5.05固定103诊断，硬件180秒/profiling-off/原数学/SDK/BOOT/模型/745保持，不重跑旧fps505或调频；当前恢复入口evidence/final-evidence-20261010-r2/in-progress-checkpoint。旧完成结论保持。

<a id="a046"></a>

## A046 · 公开read组合阶段本批结束（2026-10-10）

来源：整理前 AGENTS.md 第46–47行。

- 公开read组合阶段本批结束（2026-10-10）：d0e6bb8a…bad89ab／manifest6e2a9274…fb8e629，403载荷128来源，旧主/read画面候选/数学/模型/SDK/BOOT保持。新Host107/12注册59600及Native/ARM AU/TCP/IPC/异常拥有值/两轮Host源过；原三窗＋2Hz103＋名义5Hz103合210正确3171000FP32、2291正常编码2201网络全来源/实际PTS/像素/回收/内核同过。5Hz103全部消费0覆盖102交叠，4.998467Hz、画面P95 257.01215ms，严格≥5未过。Python3.10 monotonic为GetTickCount64/15.625ms，实际到达4.995578Hz；新QPC模块末2ms有界轮询/20ms迟到拒绝，无系统定时器更改；一次明确5.05Hz新目录前33正确498300值，第34inv33/S13_07_304最终姿态128有限值/max0.5546875不同，输入/分数逐位正确，最高分槽0未受影响。8Host115360字节最早582.slot1异常、649.slot1亦128异常，其余6槽对；272查询234/582638一poll/544对象稳定非DMA fence，CPU没抛异常故两晚设备源未触发，root未证。35接收34消费返回/PC36sent非ACK，完整第34 presaved60400保留，complete-results重复验收中断，另7任务过；360本地330网络仅31源，正确31/32未capture、3尾未出、无drain验收。两abort0/子回收256/network0/join后Engine毁/内核同/会话全部关闭无重跑。规整三次95.6013/17.91117/24.95034ms，普通9→25/1→4/2→5，2Hz103无规整26→26；最终750292KiB/CmaFree31592/普通37仅现场，无清缓存/重启/CMA变化。ADR31/32/33、COMBINED-READ-RESULTS/NEXT和combined-read completion/next-checkpoint为最新；下一先有界最终输出失配源/CPU输出捕获与save-only，再新Host/三窗后一次诊断，不重跑fps505、不再调频率。旧通过/暂停/失败保持，管理83/100，严格5Hz/长期/HDMI/零拷贝待。

<a id="a048"></a>

## A048 · 公开read组合回归已批准（2026-10-10）

来源：整理前 AGENTS.md 第48–49行。

- 公开read组合回归已批准（2026-10-10）：INPUT-READ-NEXT。隔离combined-read-r1新增显示子进程／TCP／owned-AU目标，128来源403载荷，d0e6bb8a…bad89ab／manifest6e2a9274…fb8e629。旧主／read候选／模型／SDK／BOOT冻结；Native AU2000／TCP7拒绝／IPC6912000字节9拒绝／103映射206渲染5拒绝通过，ARM待。2Hz103需51秒，独立策略ready60／network120／client125，硬件180秒、1000编码上限保持，严格全103覆盖。代理依次Host107→三窗→2Hz103，各返回审查，失败保存停止，异常Host和两晚源保持；ADR_31及prepare-checkpoint为本批入口。600秒SSH外部上限仅允许捕获旧420秒Host门检与日志，不扩硬件预算。

<a id="a062"></a>

## A062 · 真实混合模型无视频有限对照本批结束（2026-10-10）

来源：整理前 AGENTS.md 第62–63行。

- 真实混合模型无视频有限对照本批结束（2026-10-10）：model-only-r1 9ed61d9d…d925741／manifest34c3c25c…e355903，403包98来源；原主fbf330d7…cb8702d／Engine／桥／CPU数学／402非清单载荷／SDK／模型／RAW／BOOT逐位保持，Host107／12注册59600及原异常读取身份复用，未新入口Host107。Native／ARM各9拒绝、103调度顺序／窗口与返回值拥有／异常停止／不突发补帧／独立flush过。三窗4正确60400＋103正确1555300合107前向1615700 FP32逐位旧参考，CSI／输入／完整100分数姿态保存后比较；六Host＋输入0／七ZG回调、1173融合、0→745过。192真实源109232128／109285376同旧失败，1712对象／856shadow身份合法稳定、963copy元数据／856查询全234，107次582首次638/poll1；Host目标mod64覆盖0/16/32/48均FP32对齐正确，不作64对齐修复。主线程Engine生命周期／七项flush／exit0／stderr空／所有阶段原内核同；无VPU／绘图显示／网络／HDMI、正常新设备读0、异常设备源读触发0，本批规整0，无清缓存／重启／CMA／BOOT变化。最终MemAvailable700208KiB/CmaFree9312／普通单位1仅现场，所有项目程序／端口／代理会话关闭。旧坏块未复现、根因未修，移除视频同时改变启动／堆／保存时序，不认定VPU有责或稳定并发103／5Hz／长期。ADR_26、MODEL-ONLY-RESULTS/NEXT及model-only-20261010-r1 completion/next-checkpoint为当前入口；下一同身份模型／合成VPU单因素对照仅准备未实施，原异常／两晚源继续保持，不猜cache／等待／私有映射／零拷贝。管理粗估83/100保持，旧当前为历史。

<a id="a064"></a>

## A064 · 公开PL DDR容量／较高来源位置独立对照本批结束（2026-10-10）

来源：整理前 AGENTS.md 第64–65行。

- 公开PL DDR容量／较高来源位置独立对照本批结束（2026-10-10）：audit bfdacec4…4ef0ba5零Tensor，DefaultMemManager公开ADDR4096／4294963200字节、空块，匹配ARM成功分配路径为地址管理／小型元数据，非整个4GiB物理容量证明。position-r1 f375b781…408f16b／manifest29759437…2e1b464，403包94来源；主fbf330d7…cb8702d与旧typed f1c88850…218f2d9逐位保持，Host107／12注册59600与旧异常读取身份复用，未新模型。Native／ARM位置12拒绝＋冻结字节8拒绝／101模式202指纹过。96MiB SDK自有占位起点4096、read/write/copy0，真实192类型／分布源100667392／100697664、padding32@100697632／64对齐／合法窗口／不重叠；无VPU动态100对94.25189ms＋VPU100对19800.40012ms合2388000FP32全字节正确，初始各1对读回／对间0、index1–100全唯一。公开块0→1→4→0，全部自有块归还。VPU229capture含1参数集227图像1空LAST／41557字节，227解码ID与实际PTS、提交归还／正常drain／两STREAMOFF／join后SDK销毁过，NoInput合成不计模型吞吐。规整0、资源前普通单位24／策略16，内核事件同（跨shell/Python仅旧jffs2版权符号完整单行转义白名单），未清缓存／重启／CMA／BOOT变化，所有项目程序／端口／代理会话关闭。最终MemAvailable698728KiB/CmaFree130360／普通单位24仅现场，apt后台任务不擅改。无模型Session／NPU forward，旧坏块未复现／根因未修；约96MiB源不等于模型精确104MiB，NPU生产及运行时差异仍待。ADR_25、PLDDR-POSITION-RESULTS/NEXT和plddr-position-20261010-r1 completion/next-checkpoint为当前入口。下一原混合Engine无视频三窗→103仅准备未实施，不猜等待/cache/私有映射／零拷贝或重跑旧失败；管理粗估83/100保持，稳定103／长期／HDMI待，旧当前为历史。

<a id="a066"></a>

## A066 · 真实类型／动态写入独立对照本批结束（2026-10-10）

来源：整理前 AGENTS.md 第66–67行。

- 真实类型／动态写入独立对照本批结束（2026-10-10）：typed-r1 ELF f1c88850…218f2d9／manifest04dd2dd4…1cd0900，403包90来源；原主fbf330d7…cb8702d、402非清单载荷／主来源／SDK逐位保持，Host107／12注册59600及旧源读回明确身份复用，未新模型运行。Native／ARM各8拒绝／101组模式202单槽指纹／FP32精确／陈旧代次与前次块拒绝／部分拥有值保存过。真实192两类型shape[1,180,42]/[1,100,42]、**C、merged轴2/42全有效ZERO运行时确认，SDK自有源4096/34368、32padding34336、64对齐／不同chunk／不重叠；真实类型静态100对70.58981ms、逐对更新index1–100动态100对94.37701ms、动态＋VPU100对19800.34726ms合3582000FP32全字节正确，初始源读回各1对、对间0，不重复制覆盖错误。VPU先实际非空capture后SDK，228capture含1参数集226图像1空LAST，226解码ID／实际PTS对应、41492字节、226提交归还／正常LAST／两STREAMOFF／join后SDK销毁；合成NoInput不计模型吞吐。VPU前自主规整一次217.37457ms、普通512KiB单位14→143（16为资源余量策略非驱动必需界限），无清缓存／重启／CMA／BOOT变更、非失败重跑。各阶段原始内核前后同，规整前后同；跨shell／Python仅旧jffs2启动©转义相差6字节，完整单行精确白名单后其他字节同，无新事件，GBK打印／初审只改本机工具。最终MemAvailable748576KiB/CmaFree768／普通单位177仅现场；全部程序／端口／代理会话关闭。无模型Session／NPU forward，旧inv72坏块未复现、根因未修，不能宣称SDK/VPU无责或DMA/cache fence。ADR_24、TYPED-SCRATCH-RESULTS/NEXT与typed-scratch-20261010-r1 completion/next-checkpoint为当前入口；下一公开管理器容量／合法自有较高位置对照仅准备，先确认分配语义，不指定模型地址／私有cursor／映射或改SDK猜修复。稳定103／长期／HDMI／零拷贝待，旧当前为历史。

<a id="a068"></a>

## A068 · 真实模型对象身份本批结束（2026-10-10）

来源：整理前 AGENTS.md 第68–69行。

- 真实模型对象身份本批结束（2026-10-10）：r3主ELF fbf330d7…cb8702d／manifest c83773ef…98387e4，403包80来源。删除新增元数据适配可逐位还原冻结桥／入口，原wait/copy/192查询/582638/reset(1)/745/数学/SDK/模型/BOOT保持，正常设备读取新增0。新Native/ARM各17拒绝、Host107/12注册59600、旧47040拥有值/94080两轮Host源读回通过。新三窗4正确60400FP32/489编码459网络全内容、4ARM及warm逐位Native过。唯一103前72正确1087200FP32，第73 S51_01_301/inv72/frame100072在192拒绝128有限非整数/7坏段全同前次192数据复制同偏移，188/192数据正确，两晚设备源94080正确；合76正确1147600FP32，未完整103/性能验收。新对象合1222条，失败1158条/579shadow/651元数据，类型/全有效mask/归属/范围及同copy前后对象一致；两源共同PL区域/不同chunk/不重叠，两个Host目标亦不同chunk/不重叠，失败目标mod64=16/32仍FP32对齐。合616计数全234、失败8全234，不加猜测等待或称DMA fence。8项保存全过/3失败输入47760字节/29ARM参考保持；434图像404网络/70来源1946关节仅前缀，完成inv70/71未捕获/3采样尾未出，73接收消费72返回0覆盖、PC74send非ACK。两abort STREAMOFF0/子回收256/network0/Engine join后毁/内核同/端口及代理会话关闭，规整0，最终MemAvailable749348KiB/CmaFree4228/普通512KiB单位23仅现场。r1/r2格式构建失败及SCP未结束解包文件锁只修本地工具/新身份，无板测重跑，原错误保持。ADR_23、TENSOR-IDENTITY-RESULTS/NEXT和tensor-identity-20261010-r3 completion/next-checkpoint为当前入口；根因未修，下一真实类型常量→动态模式SDK scratch对照仅准备，无新模型/私有映射/cache/BOOT/CMA猜改。稳定103/长期/HDMI待；旧当前条目为历史。

<a id="a070"></a>

## A070 · 独立SDK双源搬运本批结束（2026-10-10）

来源：整理前 AGENTS.md 第70–71行。

- 独立SDK双源搬运本批结束（2026-10-10）：scratch-r3 ELF613f2dc1…17f946／manifest df830da9…fd870a2，403包85来源；原主ELF3f0ad06c…419f1e37、402非清单载荷／原来源／SDK保持，Host107／12注册59600证据明确复用，未新运行。Native／ARM各10拒绝及47760拥有字节／前次复制块／部分异常保存通过。SDK拥有A30240／B16800、源4096／34368模64为0、32字节SDK padding，无VPU100对69.24394ms＋VPU并发100对19800.31428ms，合2388000FP32全字节正确。VPU先非空capture（SPS/PPS）后SDK打开，编码worker无SDK，202capture含200图像／1参数集／1空LAST，200解码ID与实际PTS对应、36443字节流、200提交归还／正常LAST／两STREAMOFF／join后SDK销毁，NoInput合成图不计推理吞吐。r1自然B模64为32的100对成功保留、未VPU；r2只构建，r3板测前修复第二复制异常丢首份字节、原部分槽位＋独立两轮晚源保留，硬件异常未触发。UTF8准备和本机NAL参数包计图错误只改工具、无板测重跑。全部阶段exit0／内核同／进程端口释放／代理会话关闭，规整0，最终MemAvailable748928KiB/CmaFree29916／普通512KiB单位35仅现场。无模型Session／NPU forward，模型坏块未复现、根因未修，不证明VPU／SDK无责或DMA/cache fence／零拷贝。ADR_22、SCRATCH-COPY-RESULTS/NEXT和scratch-copy-20261010-r3 completion/next-checkpoint为当前入口；下一真实源／区域／chunk／dtype／Host目标身份观察仅准备，不重跑旧失败、不猜同步/cache/SDK/BOOT修正。稳定103／长期／HDMI待，旧当前条目为历史。

<a id="a072"></a>

## A072 · 192公开生产计数本批结束（2026-10-09）

来源：整理前 AGENTS.md 第72–73行。

- 192公开生产计数本批结束（2026-10-09）：3f0ad06c…419f1e37／d362ee96…86adc14，403包77来源。SDK-free192两输入原wait／copy前后8次公开layerCount观察，0–745／单inv不倒退／824条，低于234只记录；等待／copy／ready／数学／582638／reset(1)／745／Gather／SDK／BOOT保持，正常设备数据读回新增0。第七项独立保存；Native／ARM各16拒绝、Host107／12注册59600及原Frame／异常两轮源读取过。新三窗4正确60400值／493编码463网络全内容过；唯一103前3正确45300值，第4 S12_01_331/inv3/frame100003在192拒绝1728有限非整数索引，停止无重跑，合7正确105700值。失败8查询全234，合64全234，无低于234／倒退／查询错误；此观测点wait-to234不会等待，不按假设加等待或宣称DMA fence。55坏段全同前次192数据复制同偏移，188／192数据正确、两晚设备源94080字节正确；3输入47760／原元数据30＋计数32／七项保存／3ARM参考完整。失败300图像270网络1来源28关节只前缀，正确inv1/2未捕获、2尾缺；两abort STREAMOFF0／子回收256／source0／Engine join后销毁／内核同／端口与代理会话关闭。规整0，普通512KiB单位24→27→48，最终MemAvailable753672KiB/CmaFree88464仅现场。ADR_21及PRODUCER-COUNT-RESULTS/NEXT、producer-count-20261009-r2 completion/next-checkpoint为最新入口。下一公开SDK scratch30240/16800双源连续搬运（无NPU先验／VPU并发后验）方案准备未执行，匹配DMA内部mask5/A／UDMA同步语义继续调查；不直接用私有偏移、映射、cache、延时或CMA/BOOT猜改，不重跑本次103或旧失败。103／稳定5Hz／长期／HDMI／零拷贝待。

<a id="a074"></a>

## A074 · 单帧取证接入本批结束（2026-10-09）

来源：整理前 AGENTS.md 第74–75行。

- 单帧取证接入本批结束（2026-10-09）：a281cb1a…50a1e79／c8de2aa8…08e2de，403包74来源。SDK-free observer从原拥有post-copy shadow保留主线程Frame至整帧门检，≤8输入／1MiB，下一inv清空；原SDK复制／数学／582638／reset(1)／745／Gather保持，正常额外设备数据读回0。六项独立flush、原异常及旧CPU两轮源读回保留。Native／ARM各12拒绝、Host107／12注册59600值及真实Host有限最终拒绝47040字节／原异常／后续保存通过。新三窗4正确60400值、492编码462网络全内容过；唯一103前11正确166100值，第12 S21_31_349/inv11/frame100011在192拒绝496有限非整数索引，停止无重跑，合15正确226500值。3输入47760字节、102元数据／91 shadow／11个638（失败192未到582）、六项保存／11ARM参考均完整。坏索引18段全部同前一次192数据复制同偏移，目标mod256=0；188及192数据输入正确，两晚设备源94080字节同旧CSI正确。原shadow／异常暂存相同；不证明早读或UDMA/cache根因，有限硬件输出异常未覆盖，CPU异常原机制实触发。失败314图像284网络9来源238关节只前缀，正确inv9/10未捕获、3尾缺；两abort STREAMOFF0／子回收256／source0／Engine join后销毁／内核同／端口和所有代理会话关闭。本批规整0、普通512KiB单位57→40→15，最终MemAvailable748128KiB/CmaFree2120仅现场。ADR_20/17及INVOCATION-GUARD-RESULTS/NEXT、invocation-guard-20261009-r1 completion/next-checkpoint为当前入口；下一单独192公开producer234前后计数观察＋匹配SDK中转同步审计方案已准备未实施。不重跑本次103或旧start2/start3，不放宽索引／完整候选，不猜ready、指针、缓存、CMA或BOOT。103、稳定5Hz、长期、HDMI、零拷贝待。

<a id="a076"></a>

## A076 · 独立启动与有限输出保存接续结束（2026-10-09）

来源：整理前 AGENTS.md 第76–77行。

- 独立启动与有限输出保存接续结束（2026-10-09）：冻结27b9ff09…2769e086/de32738d…96ed48d，未重建主程序/重复Host107。预定三轮103，第1轮1555300FP32/593编码563网络103来源4130关节全过、4.999251559Hz严格未过；第2轮38返回/37正确558700FP32，第38 S21_19_319/inv37/frame100037输入/分数逐位同早前inv10，姿态652值/35候选不同、最大0.5078125且有限，best0及42坐标相同，不能按简单候选整行交换通过。第三轮停止未执行，合140正确2114000FP32。实际39接收/38消费返回/0覆盖，40send非ACK；完整bad结果保存但presaved38/inference37/timing38，measurement.save再次比较抛错跳过同try后面的新元数据/ARM参考，不回填638初值。旧CPU异常捕获未触发；新SDK-free invocation_evidence Frame/独立flush Native/ARM各12拒绝/16字节释放后保持/原异常与后续任务保存通过，尚未集成，失败后无新NPU/VPU/第三次模型测试。自主规整一次14.59069ms，预决策2普通块、实际写前0→4单位，仅资源策略；无清缓存/重启/CMA/BOOT/SDK/数学变化。失败385图像355网络35来源966关节只前缀，inv35/36没捕获、4尾未出，非完整视频/正常LAST。内核同/两abort STREAMOFF0/子回收/source0/Engine join后销毁/端口和全部代理会话关闭，最终MemAvailable747384KiB/CmaFree16492仅现场。匹配SDK审计CacheSyncHost Linux memcpy、UDMA同步属性、当前PL DDR仍ADDR；静态六Host结束223/234/477/481/638/720无当前等待循环，只582新查638，不证明其他读取或DMA fence。ADR_20/17/19、STARTUP-GUARD-RESULTS、SDK-MAPPING-AUDIT及startup-guard-20261009-r1 completion/next-checkpoint为最新入口；下一隔离observer从原拥有shadow保留一帧并独立落盘，Host107＋实际Host有限输出异常模拟后再新三窗/有界103。不重跑start2/start3，不降低完整候选门禁或猜映射/ready/cache；长期/HDMI/零拷贝待。

<a id="a078"></a>

## A078 · Host快照与582完成检查本批完成（2026-10-09）

来源：整理前 AGENTS.md 第78–79行。

- Host快照与582完成检查本批完成（2026-10-09）：stage-guard-r1程序27b9ff09…2769e086/manifest de32738d…96ed48d，403载荷71来源；Native/ARM各11拒绝与16字节拥有值，Host107/12注册59600FP32、真实47040字节shadow/94080 Host源通过。三窗4＋103负载合107完整前向1615700FP32逐位旧参考、1086编码1026网络全来源/实际PTS/像素通过。103收到/消费/返回全103、覆盖0，592编码562网络/4158关节；100计量画面5.000193338Hz/P95 251.199778ms达到本批短期门限且余量极小，非长期或容量提升。107次新SDK计数全部首次638/final638/polls1，无额外等待；824输入元数据＋103计数、FP32对齐/容量通过，未触发硬件错误shadow，不证明过早读取或DMA/cache fence修复。原复制/数学/参数/reset(1)/745/Gather/SDK/BOOT/CMA保持，旧NaN/坏块/晚源与错误拒绝继续保留。规整0/内核同/正常LAST/子回收/source0/Engine join后销毁/端口及代理会话关闭，MemAvailable738124KiB/CmaFree44仅现场。ADR_19/17、STAGE-GUARD-RESULTS及stage-guard-20261009-r1 completion/next-checkpoint为最新入口；下一冻结取证基线，独立启动/更长有界及SDK搬运映射契约调查准备，尚未新板测/零拷贝/HDMI/30分钟。旧正常不加同步及103失败按历史读取，最新允许的新增完成检查生效。

<a id="a080"></a>

## A080 · Host快照与生产组完成检查已批准（2026-10-09）

来源：整理前 AGENTS.md 第80–81行。

- Host快照与生产组完成检查已批准（2026-10-09）：在保留异常源读取的基础上增加原复制后Host拥有字节、目标元数据/FP32对齐校验和显式等待。新隔离stage-guard-r1保持原CPU使用原Tensor，582首输入原waitForReady后新增公开layerCount≥638检查，图/融合无582依赖循环，超时/倒退/超界停止；非DMA/cache fence证明。shadow仅Host CPTR、≤1MiB，错误保存后继续原两轮源读取和原异常；正常不额外设备源读回。最新授权替代此前“正常不增加同步”的历史限制，原模型/数学/SDK/BOOT/reset(1)/745保持。Host→三窗→103有界逐门审查，旧103失败不重跑；零拷贝仅分析，实际映射/同步另验。ADR_19记录本轮决策，结果待核。

<a id="a082"></a>

## A082 · 103门检执行结束及真实设备源取证（2026-10-09）

来源：整理前 AGENTS.md 第82–83行。

- 103门检执行结束及真实设备源取证（2026-10-09）：r2 8510f6e…0f1f3a19/子6d88d03a…e4137d39/437dcf38…bc8495e，403包68来源；Native/ARM各206渲染103/104拒绝回收、Host107/12注册59600FP32/Host源94080字节、新三窗4前向60400FP32/491编码461网络2744关节全过。103负载前60完整前向906000FP32正确，第61(inv60/frame100060/S13_07_304)在Scatter582有限性拒绝NaN；未103/100计量/5Hz验收，异常停止、没有重跑。首次真实PL DDR ADDR两输入各16800字节，两轮新增67200；输入0Host含8–11四个0xffffffff NaN/12–15零，2096值周期性块差异，两轮源均有限且逐位旧同CSI正确中间参考；输入1暂存也一致。读取晚于原复制，不能定因缓存/复制或NPU完成时刻。diag/timing0/profiling-off、原数学/等待/copy/reset(1)/745保持。失败419码图像389网络/58来源1624关节前缀正确，已完成inv58/59没进捕获尾，3采样未捕获，不报完整视频/正常LAST；四三窗合64正确966400值。匹配板端/FPAI AXI插件d55e4887…5fc7178，跨区默认copy用临时+源read+目标write，与Tensor.read共享PL DDR入口但时间/目标不同；改API未证修复。规整0/内核同/两abort STREAMOFF0/子回收/source0/Engine join后销毁/端口释放/代理会话关闭，资源681088KiB/CmaFree26012仅现场。BOUNDED-LOAD-RESULTS、ADR_18/17及bounded-load-20261009-r2 completion/next-checkpoint为最新入口；下一复制返回shadow/Host目标地址对齐和异常Receiver统计只设计，未新硬件/缓存/BOOT/CMA变化。旧待核文字为历史。

<a id="a084"></a>

## A084 · 103低日志有界门检已批准并实施（2026-10-09）

来源：整理前 AGENTS.md 第84–85行。

- 103低日志有界门检已批准并实施（2026-10-09）：接续，代理执行构建/Host/三窗后103，不重问执行方。独立预算及稀疏ARM结束后参考/Native完整参考，原Engine/CPU/异常Host暂存及两轮SDK源读回保持；103/104预算、30秒就绪编码期/100秒网络/105秒客户端/180秒硬件协调，不只扩大timeout。r1 Native构建路径参数错误保留，r2修正并完整构建，8510f6e…0f1f3a19/子6d88d03a…e4137d39/manifest437dcf38…bc8495e、403包68来源。Native及ARM真实206渲染/104拒绝/回收、Host107/12注册59600FP32/Host源94080字节通过；Native旧33与新4份ARM参考逐位。新三窗4前向60400值/491编码461网络及全部来源/实际PTS/清理通过；103已启动待核，不提前性能/稳定性验收。当前普通高阶页充足，规整0；旧坏值/尖峰未证，HDMI/长期待。入口BOUNDED-LOAD-PLAN与bounded-load-20261009-r2，独立ADR_18归档，完成后更新检查点。

<a id="a086"></a>

## A086 · 保留异常读回后的有限覆盖完成（2026-10-09）

来源：整理前 AGENTS.md 第86–87行。

- 保留异常读回后的有限覆盖完成（2026-10-09）：同r4 a7903f6a…ba21cf6/4f85e814…705aa8d，403包63来源，复用独立Host107及上一完整三窗门检，未新编译。新预置33窗客户端、两个180秒阶段2Hz/5Hz纯计时合66前向996600FP32逐位旧参考、997编码937网络5446关节/全来源实际PTS像素/清理通过，27不同来源及各6重复一致，无覆盖。前32次1856记录/额外SDK查询0，forward最大190.54528ms、旧inv28为185.79363ms，等待164.55/CPU14.57/可见复制0.617ms，旧尖峰未复现且原因未证。实际画面间隔4.98636Hz、输入4.97948Hz，诊断非低日志性能门禁，严格5Hz未过。错误捕获目录未触发，设备异常源读取0，不称旧数据块修复。规整0/内核同/队列LAST归还/子回收/Engine join后销毁/端口释放/全部代理会话关闭。最终MemAvailable749848KiB/CmaFree0、普通高阶有空闲，仅现场非泄漏/永久首启动证明。资源解包属性访问失败保留，新字节提取22哈希通过，未板测重跑。SOURCE-COVERAGE-RESULTS及source-coverage-20261009-r4 completion/next-checkpoint为最新入口，ADR_16/17同决策更新；下一协调103低日志全部边界及参考策略，异常取证继续保留，HDMI/长期未验。

<a id="a088"></a>

## A088 · 异常数据读取保留及当时接续授权

来源：整理前AGENTS.md第88行。此处接续33输入/5Hz为历史阶段许可，不恢复当前已暂停排查。

- 异常数据读取保留（2026-10-09，）：后续集成保留r4的CPU异常Host暂存、源区域/存储身份和两轮SDK Tensor::read取证；先保存暂存、再读回、继续抛出原错误，诊断失败不掩盖原错误。保持字节上限、只读设备源和禁止ADDR/BOTH直接解引用的约束，正常路径不增加读回或同步。此机制用于复发定位，并不等同于预防或修复坏值；未触发模型设备源读回时不得写为已验证。已审阅r4并批准接续有限覆盖：同身份33输入2Hz独立核验后，有限5Hz纯计时定位，异常完整保存并停止，不重跑旧失败或放宽数值/速率。
