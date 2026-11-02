# ADR_40：同身份独立生产者与VPU对照、公开ioctl观察

日期：2026-10-11。状态：本批已结束；无VPU100次通过，有VPU82次数据正确但时隙失败，正式故障根因未解决。

## 问题与决策

ADR_39的独立19成员无视频四调用通过，未复现正式并发坏片段。本批同一新程序身份依次无／有VPU各固定100次A/B交替，5.05Hz预定时隙、不追帧，阶段60秒／总180秒；保持原SDK适配源、公开19成员view、真实RAW／参考、0→11、保存后比较与原正式异常读取。

复用冻结scratch VpuLoad及timed_resident_encoder，原两缓冲／cookie／格式／复制／帧协议不改。已有日志缺QBUF精确单钟时间，新增独立SDK无关链接观察模块，用GNU链接器wrap仅透传本可执行文件静态VPU调用的ioctl；SDK共享库内部ioctl不被wrap，没有LD_PRELOAD或修改SDK。

只记录公开QBUF／DQBUF结构元数据、进入／返回时间、线程和errno，不访问MMIO、映射画面内容或私有状态。已核对静态调用统一传单个指针；不把它作为通用无参ioctl拦截器。记录容量8192，单VPU写线程，溢出／线程变化停止；无文件I/O在ioctl观察路径。先以Native／ARM桩验证指针、参数、返回值、errno、EINTR／EAGAIN、未知操作、容量及detach合同，保持失败调用本身的原语义。

有VPU先真实capture，再主线程SDK Session；失败停止编码、join后释放SDK。报告QBUF至capture和SDK复制的实际交叠，跨度仅表示提交至返回，不证明硬件忙／DMA fence。观察锁与时钟仍有扰动，不能把本批局部时间当整机性能。

## 实施与结果

同一r2程序SHA256 `5dde91e187bf5cf3a63f09bac80cf64f52bf5206448062250a1aa2197d632b0a`，18来源与152份冻结软件哈希核验；Native／ARM载荷拥有值、9拒绝、时隙算术及ioctl透传合同通过。原SDK适配与VPU源码不改。r1测试期望数值多写1ns导致Native失败，r2仅纠正该期望；实际5.05Hz公式不改，r1源码和日志保留，r1未板测。

无VPU100调用、1,176,000 FP32全部逐位独立参考／有限，输入保存一致，每次0→11、时隙门禁通过，exit0／stderr空。有VPU先真实capture再主线程Session、真实内存往返核验后放行；实际82调用、964,320 FP32全部正确，第82次（inv81）完整保存和比较后超出198.019801ms时隙，exit1 `Call exhausted slot; no catch-up`，未执行call82。合计182调用／2,140,320 FP32正确，不改成200调用或有VPU100通过，未复现正式192坏索引。

inv81从实际开始到reset前有1763.68731ms空档；随后forward460.98μs、两个copy91.12／109.15μs。该空档含目录／输入／身份文件保存、SDK Host输入校验／分配／写入、调度；当前日志不能拆开。VPU两相邻ioctl之间同期有1655.39453ms空档，最长实际ioctl1.6711ms；空档在被观察的Q/DQ调用之外，不能定位为固件卡死。整阶段allocstall／reclaim／OOM／compact增量0，pgmajfault17，后者未定位到尖峰，不能作为根因证据。

当前入口只在调用开始检查时隙，准备后无第二门检，因此inv81迟到后仍进行了这一次前向，随后停止；没有补发后续调用。下一新身份应在准备完成、reset前检查原绝对截止时间，并先完成上述分段观察；不以放宽时隙或强加延时解决。

公开ioctl1628条、单编码线程／fd6，NV12输出type10与H264 capture type9，两端各2缓冲；SDK复制164跨度中162与提交至capture跨度交叠，确认有限并发覆盖，仍不是硬件忙或fence证明。271拥有packet共47,878字节（包括一份参数头），主机解码270图像ID0–269连续正确，272原始画面提交且Host复制均正确，尾270／271未解码。画面全部NoInput，不计新姿态吞吐。失败两STREAMOFF成功、join后SDK销毁且块0；正常drain／LAST未过。冻结summary的submitted／returned=0源于abort异常未返回EncodeResult，不代表无工作，原字段不伪改。

无VPU阶段后普通高阶页折算512KiB单位7，代理执行一次有记录规整161.29668ms，7→34；CMA256MiB保持，没有清缓存、重启、循环规整或失败重跑。首capture取得不证明永久首次启动可靠性。阶段及最终内核日志逐位同，BOOT／SDK／模型同、FPGA operating，本批程序／管理器／测试端口／连接均结束。有VPU阶段结束CmaFree2072KiB，最终只读收尾MemAvailable694568KiB／CmaFree106916KiB，仅不同时间快照，不作泄漏证明。

只读收尾r1错误用构建清单查未链接的Host库，KeyError保留；r2新目录分别核对三库preflight和四库链接身份通过，仅只读，没有模型或视频重跑。所有失败、码流和原始数据保持。

## 后续与限制

优先补齐reset前SDK与应用阶段单钟观察、绝对时隙二次门检，以及VPU poll／生产／复制阶段观察；诊断日志先在有界拥有内存保存，结束后写出，但证据迁移改变时序，须独立身份／合同和完整数值回归。暂不据此改零拷贝、图、同步或SDK。正式坏值根因仍待，管理83/100不变，完整103／严格整机5Hz／长期／HDMI待；本批无网络／完整Engine或新Host107，旧异常读取保持。

详见[本批结果](../tools/pose-v1/PRODUCER-VPU-RESULTS-20261011.md)、[下一诊断](../tools/pose-v1/PRODUCER-VPU-NEXT-20261011.md)、恢复点（历史附件，当前仓库未附：`../tools/pose-v1/evidence/producer-vpu-20261011-r2/next-checkpoint.json`）。
