# 独立真实生产者与VPU对照结果

2026-10-11。批准范围PRODUCER-GROUP-NEXT已执行，异常后停止，无硬件重跑。

## 结论与实际门检

| 项目 | 结果 | 适用边界 |
|---|---|---|
| Native／ARM载荷、时隙、ioctl合同 | 通过 | 9拒绝、拥有值、透传返回／errno／EINTR／EAGAIN／容量／detach；没有新Host107 |
| 无VPU固定100调用 | exit0；1,176,000 FP32逐位／有限 | 受限两图案A/B，低地址独立19成员，时隙门禁通过 |
| 有VPU固定100计划 | exit1；只完成82调用 | 已保存964,320 FP32逐位／有限；inv81超时隙，不是100通过 |
| 编码前缀 | 271 owned packet／47,878字节，270解码图像ID0–269正确 | 参数头不计图像；272 raw提交，尾270／271未解码；全部NoInput |
| 清理／身份 | 两abort STREAMOFF成功、join后SDK毁／块0，内核／BOOT／SDK／模型同 | 正常drain／LAST未过；不证明永久首启动可靠性 |

合计182调用、2,140,320 FP32与独立参考逐位一致；每个实际输入也逐位，实际SDK计数0→11。没有复现正式GatherElements192坏索引，不证明其已修复，也不构成完整模型／整机5Hz验收。管理估计83/100保持。

## 身份及集成边界

同一r2 ELF：`5dde91e187bf5cf3a63f09bac80cf64f52bf5206448062250a1aa2197d632b0a`。18来源、原152冻结软件、原producer_payload／producer_sdk和scratch VpuLoad／timed_resident_encoder、模型／RAW、四链接库及BOOT9哈希核验。独立9185融合组保留原19成员及真实RAW，原正式223→234／最终745、CPU／Gather／桥与异常读取不改。两输出61440／40960、别名8467／8479及SDK chunk所属范围均已部署核对；两图案实际35360字节往返在放行前通过，off／on都是同Session后固定100计划。

`producer_schedule`只负责预定时隙；`vpu_ioctl_observation`只记录公开V4L2元数据；集成入口负责生命周期，不包含其他功能.cpp或操作私有SDK状态。GNU wrap仅静态VPU ioctl，SDK共享库内部ioctl保持，无LD_PRELOAD、直接MMIO或零拷贝。8192记录容量、单VPU写线程、结束后写出，本批1628记录没有溢出。观察锁与时钟有扰动，局部跨度不能当纯NPU性能。

## 失败定位

inv81计划183259567281900ns，实际开始183259567357650ns，reset开始183261331044960ns。准备至reset有**1763.68731ms**空档，实际开始至最终拥有输出1765.25773ms。随后forward460.98μs；4386／4390 copy91.12／109.15μs，wait4.23／3.72μs。完整结果保存、比较正确后时隙门禁停止，call82不存在。

空档尚未分解：目录创建／输入及身份写盘，SDK Host输入校验／分配／写入，以及调度都处于这段。原SDK适配在创建stages日志前准备Host输入，故不能从现有journal排除它。当前入口仅在调用开始检查时隙，准备结束没有二次检查，inv81迟到后仍完成这一次前向；没有后续补发。下一应在reset前按原绝对截止时间再检查，且先做分段单钟观察，不扩大时隙。

编码ioctl ordinal1620→1621间有1655.39453ms空档，最长实际Q/DQ调用1.6711ms。同期两线程都有被观察调用外空档，不能断言固件／DMA卡死或文件I/O根因。整个有VPU阶段allocstall、pgscan／pgsteal、OOM、compact增量0，pgmajfault17是阶段总量，尚无尖峰关联定位；不以此认定内存压力已彻底排除。

## 视频与并发审查

实际NV12 OUTPUT_MPLANE type10、H264 CAPTURE_MPLANE type9，两端各2；格式720p、NV12 planes2／stride1280／921600+460800字节，H264 planes1／2097152字节，cookie／复制保持。272 Host复制检查均equal，单线程fd6的公开QBUF/DQBUF实际参数与packet PTS／bytes一致。

164次SDK复制跨度中162与原始提交至capture跨度交叠；该跨度不是硬件实际忙／DMA完成或fence证明。271 packet包括31字节首参数头，270图像解码ID0–269，无倒序／漏号；PTS非递减（参数头与第一图像同PTS），实际270不同capture PTS保留。尾270／271原始提交后未解码，不能以272记编码全通过。原始码流、PTS、来源和像素哈希见on.video-review。

异常停止两STREAMOFF返回0，worker join后SDK销毁／剩余块0。没有正常drain／LAST验收。冻结VPU summary的submitted／returned=0是abort抛出、EncodeResult未返回造成的占位值；实际日志有272提交／271输入归还，原字段保持不改。

## 资源与失败保留

off后普通高阶折算512KiB单位7；代理仅一次compact_memory写1，161.29668ms、7→34，全四类前后快照／内核／原因保存。无第二规整、清缓存、重启、CMA／BOOT／SDK变化。实际首capture早于SDK初始化，但单次成功不代表首次启动长期可靠。

Native r1时隙测试期望多1ns导致失败；r2只改期望、公式不变，r1源码／build.log保留且未板测。只读收尾r1库清单错误KeyError保留；新r2核对Host preflight三库及本程序四库通过，没有硬件重跑。阶段和最终dmesg逐位同，FPGA operating，进程／管理器／端口39001及8554释放，代理SSH／SCP全结束。有VPU阶段结束CmaFree2072KiB，最终只读MemAvailable694568KiB／CmaFree106916KiB；不同时间快照不证明泄漏。

## 证据与恢复

[无VPU核验](evidence/producer-vpu-20261011-r2/off.data-review.json)、[有VPU失败核验](evidence/producer-vpu-20261011-r2/on.failure-review.json)、[视频及交叠](evidence/producer-vpu-20261011-r2/on.video-review.json)、[最终只读审计](evidence/producer-vpu-20261011-r2/final-r2-return/final-r2/review.json)、[完成绑定](evidence/producer-vpu-20261011-r2/completion-review.json)、[恢复点](evidence/producer-vpu-20261011-r2/next-checkpoint.json)、[ADR_40](../../ADR/ADR_40.md)、[下一](PRODUCER-VPU-NEXT-20261011.md)。本批已结束，不重跑失败Session、不改输出或放宽有限性／索引／时隙门禁；下一仅准备。
