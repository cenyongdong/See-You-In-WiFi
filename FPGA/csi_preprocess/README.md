# CSI 幅相预处理硬件下放

**2026-11-01当前状态：** r4源码RAR已在独立新解压目录完成完整综合／链接／放置／物理优化／布线／BIT及Procise适配，配置载荷与包内合格BIT一致；见[完整重建](../../Deliverables/FPGA-REBUILD-20261101-r1.md)。最新交付为r4 RAR，30段官方输入长测与PC滤波前／后对照已完成有限验证。最后板端观察、默认BOOT及重新启动要求统一见[恢复入口](../../FPGA/hdmi_candidate/RESUME.md)；下文短测和早期位流身份仅描述各自轮次。

2026-10-31现行交付为r4 RAR；源码含模型权重、最新BIT及目标器件必需IP／网表／实现基线，旧交付包清理，原始实测证据保留。关键数据统一见 [性能与资源汇总](../../Deliverables/PERFORMANCE.md)，当前入口见 [部署说明](../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)。以下专项记录保留当时原值。

2026-10-31已归档当前源码与完整部署包，当前默认BOOT经板端读回确认；[发布说明](../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)、[完整源码说明](../../Deliverables/SOURCE-20261031.md)。下方r3短测boot_id与次数属于该次历史运行，当前设备状态以[恢复入口](../hdmi_candidate/RESUME.md)为准。
**10月31日最后板端观察：** 已复用r3位流完成[30分钟官方长输入双路实测](LONGRUN.md)，并修复PC骨架页的共享耗时显示；长测结束时SDK安全关闭、设备空闲，实际软件及恢复以上述长测记录为准。下方r3性能和短测结果按原轮次保留。

2026-10-31 实现以释放 CPU，随后批准先软件优化、再分组流水。当前 r3 已完成物理实现、独立性能对照及 NPU＋HDMI 有限现场实测；不恢复心率或旧 DATA 调查。

**当前结论：完整预处理从同轮 PS 的 5.647ms 降至 4.043ms，减少28.41%；线程CPU时间从5.629ms降至3.973ms，减少29.43%。** 两项均包含输入转换和设备传输。现场确认分组版“画面正常，持续更新”；SDK完整关闭、设备占用为空、PC观察器结束。当前证据见[r3汇总](../../.local/csi-preprocess-20261031-r3/reports/final-summary.json)，恢复见[当前运行与恢复](#当前运行与恢复)。

## r3 分组流水与优化证据

先复用r2位流，优化有界相位wrap、复用中间结果、预计算线性拟合常数；不改变浮点运算语义。新收尾与原合格实现对420实际＋48合成窗逐位一致。软件优化将完整延迟从6.467ms降到5.981ms，但仍高于该轮PS的5.675ms，原始记录在[软件优化目录](../../.local/csi-optimization-20261031-r1)。

随后r3按“接收器→时间→天线→载波”输入顺序，将每个窗口分成60组，每组90复数（3天线×30载波）。PL完成一组才原子发布180字结果；PS读取该组并完成相位展开／拟合时，PL继续计算后续组。输出缓存仍为独立SDP BRAM，只读取已发布范围；窗口末尾再核对finished、tag、完成次数和已读总字数，组就绪不代替全窗完成。没有新增DMA／HP通路，原模型、NPU和张量顺序保持。

```mermaid
flowchart LR
  A[PS 组窗与 FP32 转换] --> B[GP 上传整窗]
  B --> C[PL CORDIC 计算后续组]
  C --> D[每90点提交已完成结果]
  D --> E[PS 读取及相位收尾]
  E --> F[全窗完成身份核对]
  F --> G[原 PS／NPU 推理与 PL 绘图]
```

| 实测方案，每窗口 | 线程CPU时间 | 完整预处理延迟 |
|---|---:|---:|
| PS参考，与分组版同轮 | 5.629ms | 5.647ms |
| r2原整窗串行后端 | 4.054ms | 6.467ms |
| r2位流＋软件优化 | 3.569ms | 5.981ms |
| r3 90点分组流水 | **3.973ms** | **4.043ms** |

各轮均为同板、同420窗官方train输入，逐窗交替PS优先／PL优先；原版／软件优化用r2，流水用r3，每轮各有配对PS参考。CPU计时为 `CLOCK_THREAD_CPUTIME_ID`，不是整机CPU利用率。r3 P95为4.254ms，PS为5.672ms；最大值分别9.588／14.219ms，保留而不删异常点。完整原值：[r3 benchmark](../../.local/csi-preprocess-20261031-r3/reports/benchmark.json)、[软件优化原始归档](../../.local/csi-optimization-20261031-r1/reports/board-results.tar.gz)。

![CPU与完整延迟四组实板对比](../../.local/csi-preprocess-20261031-r3/reports/optimization-comparison.png)

r3上传0.329ms、显式等待0.124ms、下载1.962ms、PS收尾1.003ms；完整4.043ms还包含转换、重排和其它控制开销。CORDIC仍约237756周期／100MHz，即2.378ms，但与读取／收尾重叠，不能再加到完整延迟上。25200组中19445组读取时PL仍busy，证明实际重叠。相对仅软件优化，分组版CPU时间略增，代价来自重排／分组控制等新增开销（未独立逐项归因），换得完整延迟显著下降。

420窗幅度最大误差0，相位最大误差2.38418579102e-7rad，无非有限、超容差或硬件错误；后端故障／不支持输入降级0。945次边界消歧及1个边界不确定窗口的原PS回退均计入结果和耗时，不能写成“从不回退”。快／慢消费者两批RTL仿真通过，证据在r3 `reports/batch-175241/`。

完整物理资格：97096网络全部布通，WNS +0.030ns、WHS +0.029ns、TNS／THS=0，内部未约束端点0；仍仅沿用两项既定AI最小周期例外及GT适配，无新增豁免、无降频。CSI核1584 LUT、698 FF、6 DSP、24 BRAM36，较r2增加38 LUT／21 FF，BRAM／DSP不增；整机42986 LUT、56026 FF、34 DSP、258/265 BRAM36。[资格与源／约束身份](../../.local/csi-preprocess-20261031-r3/reports/qualification-closure.json)及原生日志、检查点保留。

整机运行54.65秒，420输入完成417次新推理、HDMI采纳和PC双路接收，3次最新窗口替换；CSI调用417次无故障，1次边界全窗回退，留存绘图事件underflow=0。板端异步记录丢弃86条，PC原始记录417条、丢弃0，有界环实际保留225条完整输出。与r2整窗后端配对的225组输入和全部180候选输出均逐字节一致；留存样本中预处理均值6.734→4.298ms，process均值18.723→16.140ms，是集成负载下的另一个统计口径，不替代独立基准。[完整NPU对照](../../.local/csi-preprocess-20261031-r3/reports/npu-comparison.json)中历史字段`ps_*`表示明确标注的r2参考，并非本轮原PS。

现场确认[实屏正常持续更新](../../.local/csi-preprocess-20261031-r3/reports/visual-confirmation.json)。[原生板端证据](../../.local/csi-preprocess-20261031-r3/reports/board-evidence.tar.gz)含GP基准、BOOT／SDK／模型身份、运行及安全关闭结果；对比图可直接用于文档。本轮属于官方train片段的新推理，未新增实时CSI、功耗或长期验收；相对原PS的历史候选差异仍保留在下方r2记录，225组与r2一致不抹除这些差异。

## r2 历史实现与实测

r2首轮远程结果见[r2汇总](../../.local/csi-preprocess-20261031-r2/reports/final-summary.json)，随后独立三遍片段现场确认见[现场验证汇总](../../.local/csi-onsite-20261031-r1/summary.json)。下方r2数据按原轮次保留，不作为r3当前身份。

r2将原地双写端口RAM改为独立输入／输出简单双端口RAM，增加输入读回和故障位置／操作数寄存器，并增加输入读等待周期；原数学核保持。每个缓冲显式分为8192＋4096字，实际合计24 BRAM36；原10800字数组被工具向上取整导致32 BRAM36、超过整机容量的综合记录保留。两批5400点与输入读回RTL仿真通过，证据在 `.local/csi-preprocess-20261031-r2/reports/batch-164511`。增量实现使用新CSI网表，导入时复用99.47%单元、98.67%网络。

第一版采用混合分工：PL 的共享 CORDIC 计算 5400 个复数的幅度和原始相位；PS 保留相邻天线相位重建、跨载波 unwrap、公共线性相位校正和少量边界回退。原 PS `preprocess.cpp` 保持为数值参考，模型、张量顺序和 NPU 不变。没有把相位分支连续性候选混入本次下放。

## 实现及接口

- 自研 RTL：[polar.sv](polar.sv)、[batch.sv](batch.sv)。31 步 vectoring CORDIC，43 位内部向量，角度单位 π/2^30；IEEE FP32 输入和幅度输出。输入先由 PS 将原 FP64 转为 FP32，误差以原 FP64 算法对照。非有限输入拒绝；不支持的极端指数／次正规数走原 PS 路径。
- GP 100MHz 单时钟，独立片上输入／输出缓存，5400 点一批。不新增 DMA 主机、HP 连接或 DDR 地址；保留已通过的 PL 绘图及原 NPU 通路。
- CSR `0x400b3000`，当前r3 ABI `0x43534903`，兼容后端支持旧r2 `0x43534902`。00 ABI；04 busy/finished/fault；08 已加载字数；0c tag；10 command(1开始/2空闲复位)；14 完成tag；18 计算周期；1c 完成次数；20 顺序写输入；24 顺序读结果；28 已读字数；2c 输入检查地址；30 输入读回；34 当前计算字位置；38/3c 当前实部／虚部；40 错误原因；r3新增44完整组已发布字数。每窗输入／输出各10800个32位字。
- PS 适配：[pl_preprocess.cpp](../../software/pose180_pipeline/src/preprocess/pl_preprocess.cpp)，沿用已验证的 `/dev/mem` GP 映射模式；仅访问本核一页寄存器，不解引用 SDK 私有指针。批量有序设备读写、完成计数与tag核对，等待时休眠。局部失败隔离本核，后续走 PS，不重试 SDK。软件开关 `--preprocess-backend ps|pl`，须匹配新硬件 profile。
- 收尾：[polar_finish.cpp](../../software/pose180_pipeline/src/preprocess/polar_finish.cpp)。相邻相位差或 unwrap 接近 ±π 时用原双精度运算消歧；最终特征边界不确定时回退原窗口，保留零幅度复数乘法的 signed-zero 行为。

## r2 历史性能与整机证据

同一开发板、同一420帧官方train数据，逐窗交替PS优先／PL优先顺序；CPU采用 `CLOCK_THREAD_CPUTIME_ID`，计时包含输入转换和设备传输。CPU频率接口未暴露，本轮未修改频率／调度策略。原始结果：[benchmark.json](../../.local/csi-preprocess-20261031-r2/reports/benchmark.json)，可直接插入文档的[性能图](../../.local/csi-preprocess-20261031-r2/reports/cpu-comparison.png)。

| 指标，每窗口 | 原PS | PL＋PS混合后端 |
|---|---:|---:|
| 线程CPU时间 | 5.6715ms | 4.0472ms，减少28.64% |
| 完整预处理墙钟耗时 | 5.6899ms | 6.4587ms，增加13.51% |
| 幅度最大绝对误差 | 参考 | 0 |
| 相位最大绝对误差 | 参考 | 2.3842×10⁻⁷rad |

因此本版收益是**减少CPU计算时间**，不是降低预处理延迟，也不是整机CPU利用率下降28.64%。每窗节约约1.624ms CPU；硬件平均237756周期／100MHz约2.378ms，上传0.328ms、等待2.487ms、下载1.955ms、PS收尾1.497ms。独立板测无非有限输出、超容差结果、硬件错误或软件降级；945次边界消歧操作单独记录。

整机输入为官方train三片段420帧，完成417次新NPU推理／HDMI采纳，3次最新窗口替换；运行约53.92秒后SDK完整关闭，设备占用为空，临时网络已恢复。417次CSI硬件调用错误／软件降级均0，留存绘图事件无underflow。PC两通道均收到417帧，原始通道记录417帧、丢弃0；有界环实际保留最后225条完整记录，不能把累计记录数写成全部仍在磁盘。

与上轮PS预处理＋PL绘图的留存记录按原始frame／source时间及幅度字节配对，共223组；212组全部180候选输出逐字节一致，11组有数值变化。Top1／Top3选择均未改变；最佳候选坐标最大差0.0048828125、得分最大差0.0009765625；全部候选坐标最大差0.068359375、得分最大差0.208251953125。变化帧输入相位也有微小差异，未另行证明模型内放大机制；不宣称全候选等价或真值精度通过。完整原值和逐帧身份：[npu-comparison.json](../../.local/csi-preprocess-20261031-r2/reports/npu-comparison.json)。

完整物理资格：WNS +0.030ns、WHS +0.029ns、TNS／THS=0；97071网络全部布通、内部未约束端点0。仅沿用两项既定AI最小周期例外和既定GT适配，CSI没有新增时序／DRC豁免。CSI核1546 LUT、677 FF、6 DSP、24 BRAM36；整机42951 LUT、56026 FF、34 DSP、258/265 BRAM36，尚余7块BRAM36。报告与源／约束对应关系：[qualification-closure.json](../../.local/csi-preprocess-20261031-r2/reports/qualification-closure.json)。

原生板端结果保存在[board-evidence.tar.gz](../../.local/csi-preprocess-20261031-r2/reports/board-evidence.tar.gz)，包括SDK／模型／BOOT身份、GP基准、运行和关闭记录；EDA完整日志、报告、检查点均在同一r2工作目录。本轮未做现场实屏、新实时CSI、功耗或长期稳定性验收。

## 当前运行与恢复

- 当前包 `/root/pose180-csi-preprocess-20261031-r3`，本机[独立部署包](../../.local/csi-preprocess-20261031-r3/pose180-csi-preprocess-20261031-r3.tar.gz)。当前boot_id `25ce0ea9-6d21-47e0-8aa4-7c0388760b91`，BOOT SHA256 `23922f488d9d4842f217f1b318624c82607e35c6dc0c0b2ea3c803ca4023aa35`，精确身份见[default_boot.json](../hdmi_candidate/default_boot.json)。
- 本轮实际1次候选安装／正常重启、1次GP比较、1次有限SDK，无回退。SDK安全关闭、设备空闲、PC观察器结束；本轮关闭、剩余次数0，无自启动或自动续跑。当前启动消费已使用，再次手动演示需在新记录中准备`prepare-boot.sh`、正常重启和`check.sh`。
- 最近恢复基线是r2 CSI BOOT `08ebfb0cf7c23f063baba4cced36b2832adc6243b1b8cd4c3ea7e218b755184b`，随包保存为`boot/BOOT-baseline-csi-v2.bin`；旧骨架镜像与2026-10-29原r3演示包亦保留。恢复须先证明负载安全结束，记录新的有界操作，不复活旧预算。

### r2 现场轮次历史

2026-10-31回到板旁后，新建 `csi-onsite-20261031-r1` 现场轮次，独立执行1次正常重启、1次有限SDK，BOOT写入0。官方train三片段重复三遍，1260窗输入完成1257次新推理／HDMI采纳，3次窗口替换；约110.33秒正常结束。CSI调用1257次，fault／软件降级0，2835次边界消歧；留存绘图事件underflow为0。PC原始／展示各接收1257帧，原始记录丢弃0，有界环实际保留233条完整输出。SDK完整关闭、设备占用为空，PC观察器已结束。本轮已关闭、余额0；现场确认[画面正常、持续更新](../../.local/csi-onsite-20261031-r1/visual-confirmation.json)。[原始证据](../../.local/csi-onsite-20261031-r1/evidence.tar.gz)和[汇总](../../.local/csi-onsite-20261031-r1/summary.json)独立保留，不覆盖此前未现场看屏的历史记录。本轮仍是官方数据集新推理，不是路由器实时采集或长期测试。

- 历史板端包：`/root/pose180-csi-preprocess-20261031-r2`；本机[独立部署包](../../.local/csi-preprocess-20261031-r2/pose180-csi-preprocess-20261031-r2.tar.gz)。该轮boot_id `3154a9a3-d961-4ab3-b83a-4cb89480cd2e`，BOOT SHA256 `08ebfb0cf7c23f063baba4cced36b2832adc6243b1b8cd4c3ea7e218b755184b`，不代表现在运行身份。
- 原r2实际1次候选安装／正常重启、1次GP比较、1次有限SDK，无回退，保持关闭；现场轮次次数独立见上段。当前启动消费已使用，再次运行须在新运行记录中执行 `prepare-boot.sh`、正常重启、`check.sh`，然后手动 `start.sh`。没有自动续跑或SDK自启动。
- 原合格骨架BOOT `eae27ceb4ee81440caa1ee9a1d294eb8efd5c72463d228e9f1ee4d70a41c4c22` 随包保留，原骨架演示包和r3亦保留。恢复须先核验负载安全关闭，在新操作记录中安装备份并正常重启，不能复活本轮已关闭预算。

## 离线验证与失败历史

统一目录 `.local/csi-preprocess-20261031-r1/reports`。420帧来自现有官方 **train** 三片段，非新现场采集，非模型精度验收。`numeric.json`：2268000个相位值，幅度最大绝对误差0，相位最大绝对误差2.38418579102e-7 rad；阈值1e-4 rad以上为0。249个零幅度bin、945次边界回退操作均保留统计。不能把这组结果扩展到任意实采数据。

1836组独立极坐标RTL向量覆盖正负轴、signed zero、随机象限和宽动态范围；两批5400点原地读写、完成tag、完成次数、非法启动及越界读已仿真通过。初版模型对“负小数归一化为0”的象限判断与RTL有2 LSB差异，已按输入符号修正模型，原失败仿真日志保留。

ARM64集成程序及有限板测基准已编译。整机综合成功；首次opt因报告目录缺失退出，已复用完成的 `pipeline-linked-unclocked.dcp` 继续，不重做综合。48个合成窗口（随机相位、相反相位、坐标轴和零值）亦通过对照，最大相位误差2.38418579102e-7 rad，原始输出在本轮 `numeric-*/compare.log`。

r1最终直接布线检查点 `pipeline-routed-direct.dcp` 已通过物理资格：WNS +0.030ns、WHS +0.007ns、TNS/THS=0，96832条网络全部连通，内部未约束端点0。仅沿用原批准的两项AI最小周期例外，CSI未增加时序／DRC豁免或改频率。r1 CSI核1400 LUT、658 FF、6 DSP、16 BRAM36、470 Slice；整机42766 LUT、56046 FF、34 DSP、250 BRAM36、17365 Slice。见r1 `reports/qualification-closure.json` 和 `reports/physical-final-closure/`。这些是失败候选的物理数据，不是r2结果。

r1虽物理资格通过，GP实板测试第7窗报本核错误，完成计数6不代表6窗数值验收通过；一次逐字屏障合成输入测试亦失败。全程SDK次数0，已安全恢复骨架BOOT并正常重启；失败原值及归档见 `.local/csi-preprocess-20261031-r1/reports/board-failure-summary.json`、`board-failed-r1.tar.gz`。r2分离缓存后实际通过，但尚未独立证明r1底层故障机制，不将其根因写成关闭。r1位流前置脚本曾因目录缺失退出，补齐后重用合格检查点生成，原退出记录保留。

运行入口：`run.py numeric/sim/batch`，当前工作根为r3；r3用`prepare_stream.py`复用r2合格源和布线检查点。r2历史准备顺序为 `prepare.py` → `select_incremental.py` → `prepare_banked.py`，这些旧入口不可覆盖r3分组构建。实际原生阶段为 synthesis-banked → opt-banked → place-csi-incremental → route-csi-incremental → report-closure → `qualify_closure.py` → bit-closure → `package.py boot`，由 `continue_banked.py` 顺序执行至位流。准备脚本不在已执行批次重复运行；原生阶段、失败值与恢复检查点按轮次保留。复用厂商IP、器件库及已有时序例外。

板测基准对同一输入逐窗比较 PS 与 PL 后端，使用 `CLOCK_THREAD_CPUTIME_ID` 测 CPU 时间，同时单独记录墙钟、上传、等待、下载和PS收尾。纯CORDIC周期不能代替实际CPU或端到端收益。旧骨架BOOT保留为恢复基线；新板测独立包，不复活旧包。

## 自研与复用边界

自研内容为CORDIC极坐标RTL、IEEE输入／输出封装、分块批缓存、90点完整组发布与读算流水、GP寄存器协议、错误隔离和PS混合后端，以及数值／性能基准与系统集成。原PS数学作为参考；既有自研骨架绘制与合成继续运行。复用原厂PS／NPU IP、SDK、器件库、Vivado／Procise适配、FSBL／启动固件和已验证工程约束；模型及其NPU计算没有改写。比赛可据此展示“自定义CSI幅相算子＋二维绘图合成＋PS/NPU协同”，当前性能表述采用r3同时降低CPU时间和完整延迟的实测结果。
