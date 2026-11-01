# 当前实测性能、资源与证据（2026-11-01）

本页统一维护比赛文档可引用的关键数据。对象为 CSI v3 分组流水＋PL 二维骨架绘制，原 epoch99／180-query、TopK=3、严格 score >0.2、CPU 多人跟踪和 One Euro。以下来自既有实板／原生 EDA 结果，r4交付及11月1日独立重建均未新增板测。证据副本与原始路径映射见 [evidence/index.json](evidence/index.json)，完整原始日志仍保留在开发工作区 `.local/`。

## CSI 预处理：完整链路与 CPU 时间

420 个官方 train 窗口，每窗 5400 个复数，90 点一组、60 组。PS 参考与 PL 混合实现使用同一输入；PL 指硬件幅相计算＋PS 双精度相位收尾和必要边界回退，包含传输开销。

| 指标 | PS | PL 混合 | 变化 |
|---|---:|---:|---:|
| 完整预处理平均延迟 | 5.647450 ms | 4.042900 ms | 降低 28.41%，1.397 倍 |
| CPU 平均时间／窗 | 5.629473 ms | 3.972512 ms | 降低 29.43% |
| 完整延迟 P95 | 5.671790 ms | 4.253620 ms | 降低 25.00% |
| 最大完整延迟 | 14.218540 ms | 9.588430 ms | 本次样本范围 |

PL 上传 0.328509 ms、等待 0.124308 ms、下载 1.962276 ms、PS 收尾 1.002899 ms／窗；硬件平均 237756.067 周期，100 MHz 下约 2.377561 ms。硬件计算与分组读取重叠，不能把上述硬件时间再加到完整延迟。25200 组中 19445 组在硬件 busy 时完成读取。CPU 时间不是全系统 CPU 占用百分比，以上也不是端到端推理延迟。

幅度特征最大绝对差观测值 0，相位最大差 2.38418579102e-7 rad；大于 1e-4 rad 的相位误差 0、非有限输出 0、硬件故障 0、后端降级 0。仍有 945 次局部边界回退操作及 1 次全窗边界回退，不能写成“无回退／逐位无损”。[原始基准](evidence/csi-v3/benchmark.json)，[性能图](evidence/csi-v3/optimization-comparison.png)。

PS 与早期 PL 正确版本的 NPU 对照：223 对输入，212 对输出逐位相同，11 对有差异；Top1／Top3 选择未变，最佳候选坐标最大差 0.0048828125、分数 0.0009765625；全部候选最大差分别 0.068359375／0.208251953125。分组 v3 与正确 v2 的 225 对输入和输出均逐位相同。该结果不替代真值姿态精度评估。[PS／PL 对照](evidence/csi-v2/ps-pl-npu-comparison.json)、[v2／v3 对照](evidence/csi-v3/npu-comparison.json)。首次 CSI 开发失败原值单独保留在 [失败记录](evidence/history/csi-first-failure.json)，不能用后续成功覆盖。

## 骨架绘制与图层合成

PS 保留三维到二维投影；PL 执行线段、关节点、动态文本、调色板缓冲及 HDMI 合成。960×540、4 bit 调色板双缓冲，放大到 1920×1080；绘制／GP 100 MHz，像素时钟 148.5 MHz。

| 指标 | PS 绘图 | PL 绘图 | 统计口径 |
|---|---:|---:|---|
| CPU 绘图／命令准备 | 2.977770 ms | 0.0249792 ms | 板上合成三人场景、100 次微基准 |
| 帧上传／命令提交 | 2.834802 ms | 0.071909 ms | 实际推理保留事件，PS 229／PL 226 条 |
| 提交至显示采纳均值 | 12.396506 ms | 14.139631 ms | 不含前述 CPU 绘图／命令准备；含垂直消隐等待 |
| 提交至采纳 P95 | 19.541600 ms | 22.333100 ms | 同上 |
| 每次动态提交数据 | 4147200 B | 平均 666.372 B，112–768 B | 排除初始化背景上传，不代表总 DDR 带宽 |

PL 清屏加光栅化平均 524310.845 周期（5.243108 ms）。主要收益是释放 CPU、将动态全帧传输变为少量命令；**本次显示采纳延迟没有降低**，不能把 CPU 绘图耗时比写成整机加速比。225 对保留推理结果相同；显示环中未见 underflow／tag mismatch。[PS 事件](evidence/overlay/ps-native-display-metrics.json)、[PL 事件](evidence/overlay/pl-native-display-metrics.json)、[微基准日志](evidence/overlay/board/ps-benchmark-121333.log)、[对比图](evidence/overlay/figures/board-performance-comparison.png)、[输出一致性](evidence/overlay/ps-pl-output-comparison.json)。

## 物理实现与接口

| 范围 | LUT | FF | DSP | BRAM36 |
|---|---:|---:|---:|---:|
| 当前整机 | 42986 | 56026 | 34 | 258 |
| CSI 模块 | 1584 | 698 | 6 | 24 |
| 骨架绘图模块 | 1128 | 939 | 4 | 128.5 |
| 保留的旧滤波硬件 | 3396 | 1935 | 16 | 8 |

BRAM 为 258／265（97.36%），剩余 7 个 BRAM36。旧滤波核存在于位流，但当前演示滤波运行在 CPU；不能将其列为本次运行加速贡献。资源按各自层级统计，不把各行相加当作整机资源。

完整布局布线 WNS +0.030 ns、WHS +0.029 ns，TNS／THS 为 0，97096 条网全部连通，内部未约束端点为 0。`raw_timing_pass=false` 原值保留：存在两项已批准的原 AI 最小周期例外，本轮没有新增时序或 DRC 豁免，也不是完全无例外通过。[资格及源身份](evidence/csi-v3/qualification-closure.json)、[时序](evidence/physical/timing-final.rpt)、[DRC](evidence/physical/drc-final.rpt)、[资源](evidence/physical/total-utilization.rpt)、[BIT／BOOT 对应](evidence/csi-v3/package-review.json)。

CSI CSR 为 `0x400b3000`、ABI `0x43534903`；绘图 CSR 为 `0x400b2000`、ABI `0x534b4c01`。当前 BOOT SHA256：`23922f488d9d4842f217f1b318624c82607e35c6dc0c0b2ea3c803ca4023aa35`。程序 SHA256：`e85fac442dadb22e263698242c8dbcb63ee5841b1b52c2ba8436bb8d5a1a1bb3`。

## 30 分钟双输出长测

官方 train 连续 30 段、8700 个不同窗口，1／2／3 人各 10 段，以 15 Hz 输入时间线循环并执行新推理；有效运行 1800.004 秒，总进程 1827.279 秒。收到 25400 窗，新推理 25396 次、HDMI 采纳 25396 次，有效阶段平均约 14.109 次／秒。不是实时 CSI 测试，也不是独立 test 集准确度评测。

- PC 滤波前发送／接收 25394、发送丢弃 2；滤波后板端发送 25390、发送丢弃 6，前后两段观察累计至少 25389。一次受控 PC view 重启用于修复共享计时，重启前是快照，不能把差额 1 认定为精确网络丢包数。
- 最长新结果间隔 2287 ms，异步日志丢弃 39；CSI 硬件故障 0、后端降级 0，边界回退操作 196807 次、全窗回退 20 次。分组总计 1523760，其中 busy 期间读取 1100793 组。
- RSS 峰值 79240 KiB，热态首末观测 78712→32056 KiB；FD 18–19，线程 6。没有据此宣称无限期无泄漏。
- 在开始及末段均确认 PC、HDMI 持续正常更新，PC 板端耗时已变化。SDK 正常关闭，设备占用为空，PC 观察器结束。计数不等于浏览器每帧实际绘制。

[完整统计](evidence/longrun/summary.json)、[现场反馈](evidence/longrun/visual-confirmations.json)、[长测图](evidence/longrun/stability-30min.png)。最新 CMake 默认值和预设完成实际 ARM64 编译、离线构建及配置检查，程序与已发布版本相同：[构建结果](evidence/cmake/result.json)。


## 本次源码RAR构建验证

独立解压、新建构建目录，ARM64程序、原生离线目标、软件骨架／渲染检查、420窗CSI数值检查、CSI分组流水和骨架RTL仿真均通过；ARM64输出与当前部署程序SHA256相同。新测试使用30段部署数据的前420窗，幅度差0、相位最大差2.38418579102e-7 rad、1245次局部边界回退操作，属于本机模型／RTL验证，不替代上方实板性能数据。该软件／RTL轮次没有重跑全FPGA实现；随后11月1日已独立完成，见下节。[本次结果](evidence/rebuild/result.json)、[命令、退出码与耗时](evidence/rebuild/steps.json)、[数值原值](evidence/rebuild/numeric.json)。

## 源码RAR完整硬件复现

2026-11-01使用198429558字节的r4 RAR重新解压，实际执行综合、厂商IP／PS链接、放置、物理优化、布线、完整物理报告、BIT和Procise适配，原生阶段退出码均为0。WNS +0.030 ns、WHS +0.029 ns、TNS／THS=0，97096条网络全连通、内部未约束端点0；新适配BIT配置载荷与包内合格BIT一致，仅日期／时间头不同。既定两项AI周期例外和原厂GT适配原值保留；这不是新实板运行或严格零违例验收。完整日志、报告、恢复产物和身份统一见[重建报告](FPGA-REBUILD-20261101-r1.md)。
