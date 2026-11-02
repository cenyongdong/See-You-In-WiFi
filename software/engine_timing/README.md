# Engine推理计时诊断

**版本定位（2026-10-29）：** 本页保留早期工程、兼容接口或对应批次结果，文中的“当前”只指该版本。现行 180-query 主链在[主工程](../pose180_pipeline/README.md)，运行及验收范围见[最终进度](../../PROJECT-PROGRESS.md)；旧命令不作为最新部署入口。

这个目录提供独立测试程序、源码导出/构建/打包工具及时间线分析器。正式`software/core`、demo锁、模型JSON/RAW、CPU数学、Gather注册、SDK、BOOT和`reset(1)/745`协议保持。诊断副本只增加计时观测及公开SDK采样入口，不接入正式演示，不恢复旧DATA坏读定位。

## 能回答什么

| 数据 | 入口/范围 | 可以解释 | 不能据此解释 |
|---|---|---|---|
| Engine阶段墙钟 | preprocess、输入准备、reset、Session.forward、末端等待、输出读取、选择 | 每个可见阶段延迟，首次初始化与处理分开 | 纯NPU计算或DDR比例 |
| 每算子回调跨度 | 原7个Host＋7个ZG回调 | 原Host/Gather、ZG提交跨度及顺序 | 异步ZG回调跨度等于硬件执行时间 |
| CPU桥细项 | spec、wait、counter_wait、allocate、copy、cpu、writeback | 164ms等待集中在哪些算子/输入；CPU工作和搬运API成本 | wait全部来自NPU或可全部被删掉 |
| 线程CPU/rusage | CLOCK_THREAD_CPUTIME_ID、RUSAGE_THREAD | 线程CPU占用、缺页及自愿/非自愿切换 | 切换次数对应具体调度等待毫秒数 |
| SDK四项分析 | Session.timeProfileResults | SDK报告的wall/copy/hardware/other原值 | tuple单位及逐帧/累计语义尚未核实，不自动换成ms |
| 硬件层时间 | ZG330Device.getLayerTime(745)，公开说明单位ms | 硬件执行层时间分布；读取耗时另列 | 纯算术与DDR停顿拆分；层序与原HardOp身份尚未独立核实 |
| 桥逻辑字节 | 源/目标是否Host、声明bytes | 公开复制API的有效吞吐 | 实际PL DDR读写通信量、内部权重复用或总线带宽 |

`forward_partitions`通过区间并集扣除子区间；不把回调、CPU桥和Session.forward重复相加。`dispatch_callbacks_and_unobserved_ns`是未覆盖残余，包含SDK、回调及其他工作，不能命名为精确SDK调度。墙钟减线程CPU的差值保留有符号原值，小区间可能出现采样噪声。

本机还核对了`icraft-pf/data_struct.h`：其中MAC时间与传输时间有按算量/流量/带宽计算的公式。该公式不能替代本项目实际DDR-stall周期；其默认BY目标也不能直接作为ZG330测量配方。本版不启用这个未经核实的路径，不配置Profiler空间、频率、MMU、缓存或私有寄存器。

## 程序及产物

- `prepare.py`：核对demo锁的全部源码，以唯一别名导出新目录。精确锚点生成诊断副本，锚点或哈希改变即停止；前后哈希单列，原锁不改。
- `application_clock.hpp`：单线程、有界内存采样。异常展开也记录已进入的Span；容量/线程错误先保存部分证据再拒绝。
- `sdk_profile.hpp`：仅在`sdk`模式，在process返回、完整输出保存比较通过后，下一帧reset之前采样；采集成本不混入Engine process。
- `main.cpp`：单Engine，固定308/309/310三个已验收窗口，默认一轮3次，最多8轮24次。无VPU/TCP/显示；任一输入、输出、SDK、计时合同异常均停止，不重试。
- `build.py`：在既有FPAI中核对ARM SDK、编译ARM64程序，不运行模型。
- `make_package.py`：从2026-10-13已验收三窗口归档读取原CSI字节，并与冻结参考哈希核对。重新包装PIWCSI1头，保留1000000–1000002帧号；不是新模型输出。
- `board_run.py`：板端资源/内核/BOOT/SDK/模型和包身份门检，120秒子进程预算、5秒退出宽限；保留全部日志及哈希，无自动重试、规整或重启。
- `analyze.py`：生成`report.json`、`report.md`及`chrome-trace.json`。原始证据哈希核验后分析，拒绝覆盖旧报告；失败批只报告部分证据。Chrome/Perfetto可导入时间线，每帧单独轨道，硬件相对时间不伪装成宿主绝对时间线。

模式分别为`baseline`（本诊断二进制关闭采样和SDK profiling）、`wall`（宿主观测）、`sdk`（宿主观测＋SDK分析）。三种模式使用同一二进制与同一输入序列，逐阶段独立运行；`wall`要求上一baseline分析通过，`sdk`要求上一wall分析通过。baseline仍保留原Engine回调/安全检查，不称无任何观测的理想运行。不同模式的均值差包含运行波动，不作精确“扣除探针开销”修正。

## 当前验证状态（2026-10-13）

13项Python分析合同通过；Windows SDK无关C++检查通过；既有FPAI中的Linux线程CPU/rusage、异常、错误线程及容量合同通过；ARM64交叉编译通过。只有原核心既有的未使用私有助手警告。完整日志见验证证据（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/engine-timing-20261013-r1/README.md`）。

上述开发交付阶段没有SSH、部署、NPU前向或板测；历史开发清单保持。

随后实际完成Lite有限计时：baseline/wall各3个固定窗口完整输出逐位通过；wall均值Engine195.098ms、forward187.617ms、桥等待162.294ms、已观测CPU核14.121ms、搬运API0.771ms。SDK模式第1帧输出正确，但硬件745项中215项负值，立即保存停止、未重试，不能计算有效NPU总耗时。公开tuple单位/累积及层序映射仍未知。初始化约30.5–31.2秒另计，不包含VPU/TCP，不外推长期并发或整机5Hz。实测表与完整证据（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/engine-timing-board-20261013-r2/README.md`）。

预检原来将dmesg历史版本与proc/version比较，r1在前向前停止；同源dmesg核验一致后仅修正包装器，新包r3和新板端目录r2执行。原源码/构建/交付封存清单不回写，正式核心/模型/SDK/BOOT保持。后续构建使用已修订board_run.py。

## 可复现执行入口

这些命令记录执行位置、输入与边界，供后续明确的有限计时阶段使用；不得复用本次已执行或失败的目录及Session。代理执行职责以当前Agents及任务范围为准。

本机构建/打包位置为Windows PowerShell，工作目录`D:\FPGACompetitionProject`。前置为既有Python、Docker/FPAI运行、Icraft ARM3.39.0、当前demo锁及已验收归档齐全。无需安装。下例使用新的r3源码/r4构建标签，目录若存在必须另取唯一标签，不能删除失败目录后重用。

```powershell
python software/engine_timing/prepare.py --output .local/engine-timing-source-NEW
python software/engine_timing/build.py --source .local/engine-timing-source-NEW --tag engine-timing-build-NEW
python software/engine_timing/make_package.py --source .local/engine-timing-source-NEW --build .local/pose-v1-build/engine-timing-build-NEW --model-dir D:\Person-in-WIFI-3D\Person-in-WiFi-3D-repo\result\icraft_2024 --output .local/engine-timing-delivery-NEW
```

`--source`为隔离导出目录，`--tag`为新的构建身份，`--model-dir`必须是使用前重新核验的当前固定模型目录，`--output`为新交付目录。每条命令退出0，`build-result.json`记录`compiled_not_board_executed`、包内模型/参考/二进制哈希闭合，才可进入后续阶段；任何非0、哈希/签名变化停止。不要从源码准备完成推导板端通过。

板端执行位置为Lite shell，工作目录为已通过主机密钥核验、内存认证传入的**新包目录**，例如`/tmp/wifi-pose-engine-timing-20261013-r3`。传输不是本脚本自动执行的动作；复制后核对包身份，赋予仅测试二进制执行权限。前置为独占NPU、无已有pose进程、内核/BOOT/SDK与已验收基线一致。默认每模式3次、120秒预算，不包含视频、网络或压力负载。

```sh
chmod u+x pose_engine_timing
python3 board_run.py --mode baseline --cycles 1
python3 analyze.py --run run-baseline --output run-baseline/analysis
```

返回/审查baseline完整输出与报告通过后，单独进行wall：

```sh
python3 board_run.py --mode wall --cycles 1
python3 analyze.py --run run-wall --output run-wall/analysis --baseline run-baseline
```

返回/审查wall通过后，单独进行sdk：

```sh
python3 board_run.py --mode sdk --cycles 1
python3 analyze.py --run run-sdk --output run-sdk/analysis --baseline run-baseline
```

`--cycles`为三窗口序列轮数，三个模式必须一致；默认1，最多8，不允许自动延长。通过标准是`exit.txt=0`、全部实际输入与分数/姿态逐位冻结参考、每帧7/7回调与最终745、完整哈希/时间线、无stderr/内核变化、正常Engine回收。SDK返回为空、长度不是745、非有限值、身份变化、异常、超时或输出失配均保存停止；超时不宣称优雅硬件回收。旧DATA恢复仍须明确任务指令。

预期产物在`run-MODE/results`：完整每帧输入/分数/姿态、`frames.jsonl`、`monotonic-spans.jsonl`、`transfers.jsonl`、`sdk-profile.jsonl`、`hardware-layers.jsonl`、原CPU异常取证；包装器另存资源、dmesg、命令、退出码、库及运行身份、完整哈希。后处理结果在`run-MODE/analysis`。失败分析只可用于理解已捕获片段，不能外推性能或正常drain。

本机离线复核入口（工作目录仍为项目根，目录必须新建）：

```powershell
python software/engine_timing/verify.py --output tools/pose-v1/evidence/engine-timing-OFFLINE-NEW
python software/engine_timing/verify_linux.py --output tools/pose-v1/evidence/engine-timing-LINUX-NEW --tag engine-timing-native-NEW
```

这些仅执行合成合同测试，没有模型、Device、Session或SSH；成功日志与源码哈希各自保存。Windows采样的线程CPU/rusage字段为null，Linux检查才覆盖这两个接口。

## 公开依据

- `C:\Icraft\CLI v3.39.0\include\icraft-xrt\core\session.h`：TimeProfileResults四项定义、Session总时间和公开回调。
- `C:\Icraft\CLI v3.39.0\include\icraft-xrt\dev\zg330_device.h`：getLayerTime单位ms；不访问私有Node计时空间。
- ARM对应头在构建时与本机所读版本逐位规范化核对，实际库身份另存。
- [既有性能报告](../../tools/pose-v1/P2-RESULTS-20261007.md)、[ADR_06](../../ADR/ADR_06.md)：等待/后端跨度不是纯硬件时间，显式桥复制不是全部内部通信量。
