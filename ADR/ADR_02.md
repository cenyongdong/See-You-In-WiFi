# ADR_02：VPU连续内存分配与同进程常驻编码策略

- 日期：2026-10-08
- 状态：本轮启动三次回归与有限同进程工作者验证完成；在线RTSP/长期启动另验
- 关联：[有限接入证据](../tools/pose-v1/PIPELINE-RESULTS-20261008.md)、[难点索引](../DIFFICULTIES.md)

## 问题与事实

真实PS/NPU→骨架→VPU有限同进程链路已有两次成功，每次八完整前向、十编码帧；成功间全部NV12与H264逐位一致。无规整的新进程重复在Engine创建前失败：MVX固件`map_protocol_v2`调用`mvx_mmu_alloc_contiguous_pages`，申请order7/512KiB，标志`GFP_KERNEL|__GFP_NORETRY|__GFP_ZERO`。

失败时CMA已有256MiB预留，仍约67MiB空闲，512KiB及以上空闲块均标记CMA；普通高阶块不足。一轮显式内存规整约0.193秒后新目录成功，支持碎片方向，但不证明驱动内部全部根因。旧MMU ABORT与本次固件分配失败分别记录，不能混为同一故障。

## 选项与决策

| 路径 | 收益 | 限制与风险 | 本轮决定 |
| --- | --- | --- | --- |
| 同进程编码线程常驻 | 保留一个VPU上下文和MMAP资源，减少反复固件加载/分配；避免新增IPC | 不能修复首次启动，线程停止/所有权/背压需验证 | 优先实施；一个Engine线程、一个VPU线程、待处理画面容量2 |
| 增大CMA | 若DMA/CMA路径实际容量不足可能受益 | 普通不可移动页申请未必可用CMA，扩大可能减少普通页余量；需改变启动配置和恢复验证 | 保持256MiB，先核查实际驱动分配路径 |
| 调整分配时序/占用 | 可能在普通高阶页耗尽前完成固件初始化 | 必须查明REQBUFS/prime/STREAMON占用，不凭猜测改变缓冲数 | 先只读分阶段快照，再依据证据提出最小修正 |

保持六输入/六输出缓冲、prime2、opaque cookie、Host复制和原数学/SDK/模型/BOOT/reset(1)/745。不自动规整、drop_caches、重启或重开设备。常驻不等同稳定首次启动；三次预定独立启动任何一次失败即停止剩余试验。

## 实施与验收

r7只增加分配阶段内存快照和模块/内核配置/cmdline/reserved-memory核查；新构建/Host107后一次180秒有限combined。常驻独立入口按真实steady_clock采样10fps，发布owned NV12，队列满丢最旧未消费画面并记录；重复帧不算新姿态。首capture5秒、Engine60秒、就绪后20秒、外部180秒、最多1000编码帧。全部输入/输出及视频源映射独立复核；在线RTSP、HDMI、整机5Hz/30分钟不在本轮结论。

## 解决与验证结果

2026-10-08启动阶段：r7六缓冲快照确认capture REQBUFS后普通order7以上块归零，实际模块直接调用__alloc_pages_nodemask(0x10dc0)，CMA256MiB保持。基于该证据新增隔离两缓冲候选，仅改变申请数量6→2；实际两端返回2、映射19.9→6.64MiB，保留普通高阶页。程序33f865a2…171273，Host107完整通过，三次预定独立启动均exit0/stderr空/dmesg同，24完整前向/30编码、三码流逐位一致。无规整/重启或SDK/BOOT修改。详见[启动结果](../tools/pose-v1/VPU-STARTUP-RESULTS-20261008.md)。

r8最初Host300秒超时95例全部符合预期，原失败保存；新外部420秒预算完成107例，数学/拒绝规则/程序和包不变。该时限调整不扩大硬件180秒预算。

本轮启动回归通过，不保证普通高阶页完全不足时必能启动。原六缓冲实现保持。常驻r2入口完成Host107；静态审查后新r5补充popLatest及coalesced计数，源选择后取实际采样时间，避免积压时FIFO额外延迟。队列满覆盖与采样合并分别统计，固定2Hz测试要求两者均0。队列Native测试通过；r1/r3/r4构建原型及r2Host保留，只有最终r5进入后续常驻板测。板端常驻/完整视频映射结果待补充，不能提前记作常驻修复完成。

常驻r5后续实测：Host107通过，resident-three第一次模型输出读取被原有限性检查拒绝。七ZG/七Host回调、0→745及两输出ready齐全，内核前后相同；VPU约292个NoInput提交，未发布任何模型画面，异常两队列停止返回0。未生成resident-three验收、不进入27窗口，不弱化检查或复位。此问题与固件启动分配分开；原因未知，新r6只隔离Engine所有者线程到主线程（此前所有通过程序的调用位置），编码仍后台，数学/同步/硬件并行政策不变。[保留失败](../tools/pose-v1/evidence/resident-20261008-r5/resident-three-failure-review.json)。

2026-10-08常驻阶段完成：r6主线程创建/前向/保存/销毁Engine、后台编码不变，程序f4f15b7e…e7060、402包/23来源通过构建身份。Host107与三帧＋重复4次、27窗口＋重复28次完整回归均通过；483,200个FP32输入/输出逐位原板端，987视频帧全部源/ID正确，5530关节可见性核验。容量2队列high_water=1、overwritten/coalesced均0，真实PTS递增、原始码流保持；两硬件阶段exit0/stderr空/内核同，正常LAST/归还/STREAMOFF。采用已验证主线程所有者作为首版调用约束，不宣称SDK普遍不支持后台线程，内部原因仍未证明。[完整结果/视频](../tools/pose-v1/RESIDENT-RESULTS-20261008.md)、[核验](../tools/pose-v1/evidence/resident-20261008-r6/completion-review.json)。

当前交付是有界20秒工作者测试，不安装永久服务、不声称在线RTSP或整机/30分钟通过。CMA仍256MiB、原六缓冲/后台失败与模型/SDK/BOOT保留，无规整/重启。预览裁去初始化并按名义10fps重编码，仅供审查，实际采样PTS保留。测试/会话关闭，下一在线owned AU桥按新门检推进。

## 依据

### 2026-10-08后续启动边界实测

后续一次规整恢复验证，覆盖前轮禁止规整的对应限制。159.69498ms单次操作、普通高阶折算512KiB单位5→91，之后新保存优先目标两个独立进程启动及32前向/984编码/864网络通过，未第二次规整、清缓存、重启或改CMA。支持本次恢复有效，不推翻两缓冲不保证任意碎片状态的限制；安全CMA路径另按ADR_13。[结果](../tools/pose-v1/PRESAVED-RESULTS-20261008.md)。

TCP输出失配诊断新目标在首次VPU启动处再次失败，尚未创建Engine/执行模型。85项完整回传和内核新增order7/0x10dc0，amvx固件路径为`mvx_mmu_alloc_contiguous_pages → map_protocol_v2 → mvx_fw_factory`。失败当时约130,604KiB CMA空闲，512KiB及以上空闲块均CMA；两缓冲降低资源要求，仍不能保证任意普通高阶页碎片状态启动。

失败后STREAMOFF均返回0、端口和进程释放。随后只读pagetype快照出现5个Unmovable order7块，这是清理后的不同状态，不回写为故障现场，不当自动重跑门禁。原三次启动通过保持其范围。未规整、清缓存、重启或改CMA；新取证因资源条件停止，恢复方式后用新目录继续。证据`tools/pose-v1/evidence/tcp-evidence-20261008-r1/live-three`及`memory-failure-snapshot`，详见[TCP结果](../tools/pose-v1/TCP-INTEGRATION-RESULTS-20261008.md)。

- [r6完成及失败核验](../tools/pose-v1/evidence/pipeline-20261008-r6/completion-review.json)
- [Linux5.4 GFP定义](https://raw.githubusercontent.com/torvalds/linux/v5.4/include/linux/gfp.h)：mobility与NORETRY行为；上游机制不代替板端定制驱动证明。
- [Linux5.4启动参数](https://www.kernel.org/doc/html/v5.4/admin-guide/kernel-parameters.html)：CMA大小/地址属于启动配置；本轮不调整。


## 2026-10-10补充：规整后首次启动反例

同程序模型／合成VPU对照前三阶段111前向／1676100FP32正确，310合成码流通过；第四阶段在Engine之前DQBUF EIO，内核同一路径order7／512KiB普通连续申请失败。启动前有记录规整8→9单位／14.12106ms，raw REQBUFS后7、capture REQBUFS后0，约104MiB总空闲不能满足该连续申请；失败后释放恢复普通8并不反证瞬间不足。没有新模型坏块，不能将此错误归为192／ScatterND早读。

本批总3次资源准备规整，不清缓存、重启、改CMA／BOOT／驱动。两abort STREAMOFF成功／worker join／七项落盘保存，未重试旧失败。该反例将“规整可诊断并偶尔推进”与“可靠首次启动”明确分开；常驻能减少重新分配，但第一次成功仍要单独取得。下一仅准备同上下文跨短／长阶段编排和匹配驱动分配路径审计，安全连续申请／CMA修改另议。[结果](../tools/pose-v1/MODEL-VPU-RESULTS-20261010.md)／[ADR_27](ADR_27.md)／[下一](../tools/pose-v1/MODEL-VPU-NEXT-20261010.md)。


## 2026-10-10补充：单次上下文保持通过，首次资源条件仍需区分

按新[ADR_28](ADR_28.md)，一次VPU实际capture后创建同一主线程Engine，连续三窗4＋103完整通过，107前向1615700FP32／518合成图像正确；窗口切换无VPU／MMAP／Engine重建。准备规整9→28单位／144.80296ms，实际进入31、raw后29、capture后21、首capture20；与上批9→7→0的失败条件不同。保留context可避免阶段重开，但不能声称因此独自修复第一次启动或普通页分配永久可靠。

原两缓冲／cookie／6.64MiB映射／CMA256MiB／驱动／BOOT保持，正常drain-LAST／两STREAMOFF、join后Engine销毁，最终原内核同／进程结束。未清缓存／重启／改CMA／内核。进一步安全连续申请仍须匹配DMA／MMU／cache／固件与释放路径，不能由本次成功跳过。[实际结果](../tools/pose-v1/RESIDENT-SEQUENCE-RESULTS-20261010.md)。
