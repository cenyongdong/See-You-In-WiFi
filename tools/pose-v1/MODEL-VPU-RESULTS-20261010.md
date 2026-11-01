# 同一程序模型／合成VPU对照结果

2026-10-10。前三个阶段通过，第四阶段在VPU首次capture之前失败，按停止条件结束；并发103未通过，原模型坏块根因仍未解决。

## 身份与契约

同一ARM程序SHA256 `4bab1a1d61c54fdebde33eaa71a1ec378e3159c964c5dcd8e6e198aa749aab2a`，manifest `28d76b0245bc7b406fc9f66d1a5ed92699e1d25ba48ee9e7ac3de4b46cde6da0`，403载荷102来源。原主、Engine／桥／CPU数学／模型／RAW／SDK／BOOT保持。Native／ARM生命周期各6拒绝、原Run各9拒绝及拥有值／独立flush过；Host107／12注册／59600仅冻结身份复用，非新入口Host107。

## 实际阶段

| 阶段 | 结果 | 完整FP32对照 | 编码 |
|---|---|---:|---|
| model-three | 4次完整正确，exit0 | 60,400 | 无 |
| vpu-three | 4次完整正确，exit0 | 60,400 | 310合成NoInput图像，56,930字节 |
| model-103 | 103次完整正确，exit0 | 1,555,300 | 无 |
| vpu-103 | DQBUF EIO，exit1；Engine未创建，前向0 | 0 | 首次capture0，码流0字节 |

合111实际前向／1,676,100 FP32逐位旧参考，完整CSI、输入、100候选分数／姿态均先保存后比较；192真实来源109232128／109285376保持，1776对象行／888拥有快照和888计数查询稳定，计数全234，999复制元数据。111次582检查首次638/poll1。六计算Host／七ZG组、1173融合及0→745通过，profiling-off。Host目标mod64含0／16／32／48均FP32对齐正确，不认定64对齐修复。

三窗VPU实际非空capture后创建主线程Engine，310帧ID、全部像素、实际PTS、owned packet／drain／LAST及join后Engine销毁核验过。首次ready可以是参数集，不能称首次图像。合成NoInput不计姿态吞吐，不是实际骨架／RTSP／显示测试。

## 第四阶段失败位置

VPU成功协商原两缓冲／NV12／H264／cookie并排入两个原始输入，STREAMON后CAPTURE DQBUF errno5。新增内核明确记录order7／512KiB `GFP_KERNEL|__GFP_NORETRY|__GFP_ZERO`申请失败，路径`mvx_mmu_alloc_contiguous_pages → map_protocol_v2 → mvx_fw_factory`。故障瞬间普通512KiB及以上空闲块为0，约104MiB总空闲不等于连续页可用。

取证序列：entry普通512KiB折算9→raw REQBUFS后7→capture REQBUFS后0，之后prime／两STREAMON均0。快照不是分配承诺；映射长度也不证明所有内核内部物理分配方式。首次capture0、Engine未创建、前向0，因此没有192／ScatterND模型失败输入或晚源触发。`Engine_destroyed`记录仅是空指针reset清理点，不能当实际创建／销毁证明。

失败后两abort STREAMOFF返回0，worker已join，七项独立保存成功。最后阶段91文件完整核验，没有输出门禁或伪造视频通过。成功阶段内核原字节不变；最后新增分配错误保留，不白名单隐藏。所有项目程序／端口及代理连接结束。

## 资源准备与限制

自主取证规整共3次：共同准备3→10单位／61.46912ms；VPU三窗前6→6／15.20305ms；VPU103前8→9／14.12106ms。每次都有buddyinfo／pagetypeinfo／meminfo／vmstat及内核前后、原因与耗时；不是失败后循环规整或重跑。三窗成功与末阶段失败之前资源准备不同，因此不是严格相同内存条件。

策略16单位只是历史映射6.64MiB加固件512KiB的准备裕量，非已证分配下界。规整后仍失败，不能把规整写成首启动可靠性修复。CMA仍256MiB，未清缓存、重启、改BOOT／CMA／内核／驱动／SDK／数学。最终MemAvailable740060KiB／CmaFree40KiB／普通单位8是释放后现场；不能反证申请瞬间0或证明泄漏、永久可靠性。

## 结论与恢复

同一程序无视频103完整正确，仅加合成编码的三窗也正确；最后的103组合没有模型计算，不构成VPU导致旧模型坏块的因果证据。旧坏块、前次数据残留、稍后正确设备源和异常两轮读取继续保留。完整并发103、持续5Hz／长期／HDMI／零拷贝仍待；管理粗估83/100保持。

传输恢复由；实际本机bundled Git缺scp.exe，已换本机完整Git SSH/SCP，并校验既有ED25519密钥、远端包哈希。认证秘密仅在传输进程内存中使用；另设计要求将连接配置记录到AGENTS.md。审批超时记录与原失败保留。

证据：[完成审查](evidence/model-vpu-20261010-r2/completion-review.json)、[资源审查](evidence/model-vpu-20261010-r2/resource-review.json)、[启动失败](evidence/model-vpu-20261010-r2/vpu-103.failed-review.json)、[恢复点](evidence/model-vpu-20261010-r2/next-checkpoint.json)、[ADR_27](../../ADR/ADR_27.md)、[ADR_02](../../ADR/ADR_02.md)。下一先按[资源生命周期方案](MODEL-VPU-NEXT-20261010.md)准备，旧失败不重跑。
