# 当前设备、部署与恢复入口

**2026-11-01仅本地完整重建完成：** 最新r4源码RAR新解压完成综合、链接、放置、物理优化、布线、BIT及Procise；新BIT配置载荷与包内合格BIT相同。新生成文件只作重建证据，未连接开发板、未改默认BOOT；[重建报告](../../Deliverables/FPGA-REBUILD-20261101-r1.md)不替代下方10月31日最后板端观察。当前部署和安全启停仍使用[最新r4部署说明](../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)，不能将r4本机目录写成已上传。

**r4最新交付（RAR）：** 最新本机[部署包与源码说明](../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)包含更新后的CMake默认值与预设，源码精简并附JSON／RAW／ONNX；旧本机交付包已清理，关键历史记录在 `.local/delivery-cleanup-20261031-r1/`，工作区恢复镜像和检查点仍在。程序与已验证r1一致。本轮未连接设备，最近已部署目录仍为`/root/pose180-csi-release-20261031-r1`，下方BOOT核验是上轮快照。

**2026-10-31发布核验：** 默认启动分区BOOT已为合格CSI v3，读回SHA与发布包一致，设备无占用。本次读取boot_id为`9866784b-bf11-419a-ab5f-7797fe3706d3`，已不同于长测时启动；不沿用旧启动消费判断，新包仍须prepare／正常重启／check后手动运行。本次BOOT写入0、代理重启0、SDK启动0；最新包与部署入口见[发布说明](../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)。下方长测boot_id与“已消费”仅是该历史轮次状态。
**2026-10-31 当前30分钟长测已完成关闭：** `/root/pose180-csi-longrun-20261031-r1` 使用同一CSI r3 BOOT，boot_id `737e40ad-de06-4139-b9d0-6fc1ae5ae03d`；一次SDK完成1800.004秒有效运行并安全退出，设备空闲、PC观察器结束。当前启动消费已使用，再次运行须新记录、正常重启与预检。本轮次数用尽，不自动续跑；双路结果、PC计时修复与恢复见[长测专项](../csi_preprocess/LONGRUN.md)。

**2026-10-31 此前CSI分组流水短测完成：** 当前安装r3分组CSI＋骨架绘图BOOT，已完成独立420窗对照和417次新推理／HDMI采纳，现场确认画面正常持续更新；CPU时间与完整延迟均低于PS。SDK正常关闭、设备占用为空、PC观察器结束。当前启动消费已使用，再次演示须在新运行记录中准备正常重启并预检。新包目录 `/root/pose180-csi-preprocess-20261031-r3`；最近恢复基线为r2 CSI BOOT，旧骨架及2026-10-29原r3亦保留。精确身份、次数、对比证据和恢复以[CSI专项](../csi_preprocess/README.md#当前运行与恢复)为准，不复用已关闭包次数。

此前骨架专项已完成实屏确认，证据见[骨架记录](skeleton_overlay/README.md)；下方2026-10-29及更早记录仅说明当时结果，当前状态以上方CSI专项为准。

## r3 历史记录（2026-10-29；旧本机包已清理）

- 使用 [r3 最终演示包](../../Deliverables/pose180-three-clips-20261029-r3-final.tar.gz)和[部署说明](../../Deliverables/pose180-three-clips-20261029-r3-DEPLOY.md)，源码入口为 [pose180_pipeline/src](../../software/pose180_pipeline/src/README.md)。原 epoch99、TopK=3、严格 score >0.2；官方 1／2／3 人在同一 SDK 生命周期顺播，实时接口保留。
- 板端保留 `/root/pose180-three-clips-20261029-r3`。最后一次清理核验时 boot_id 为 `c289a43e-d6aa-4f3f-835d-d4aeb0848caf`，原生推理进程及设备占用为空。这是观察快照，后续启动仍须读取实际状态，不能复用旧 boot_id。
- 最近既有 r3 运行记录：420 帧新推理、420 次 HDMI 采纳、420 帧 PC 发送、0 发送丢弃，`native_exit=0`、完整关闭、临时地址撤销。发送计数不等同浏览器逐帧绘制；不据此认定长期或精度通过。
- 本次最终打包只补入 PC 启动／连接修正，板端内容未变；收尾期间未新启 SDK、重启或写 BOOT。完整清理与最后观察以[唯一原始记录](../../.local/project-cleanup-20261029-r1/summary.json)为准。

## 启动与停止

完整命令以最终包部署说明为准。三个片段之间不重启；整套程序安全退出后再启动，或切换输入源，需要满足每次 FPGA 配置一次启动消费的保护规则。`prepare-boot.sh` 只准备下一次正常启动所需记录，本身不重写 BOOT、不重启、不运行 SDK；正常重启后重新预检。

PC 仅观察结果，不负责发包或初始化 SDK。当前电脑可使用 `-Board 192.168.126.49 -LocalAddress 192.168.126.100`，其它电脑使用自己的有线地址；具体依赖与诊断见 [PC 说明](../../software/pose180_pipeline/host/README.md)。板端 `.50.49` 是运行期间临时地址，正常结束后可能移除。

正常退出须有原生关闭及设备占用证据；完成未证明时保持 `release_blocked` 与独占，不强行释放或盲目重试。运行中 PL_KEY1 复位恢复未通过，不能用它代替正常重启流程。

## 当前硬件与本机恢复资产

| 项目 | 状态与位置 |
|---|---|
| 默认 BOOT | `probe-free-drain-overlay-csi-v3`，身份以 [default_boot.json](default_boot.json) 为准；CSI分组流水、骨架绘图在PL，相位收尾及展示滤波仍在CPU |
| 合格镜像备份 | 最近[r2 CSI BOOT](../../.local/csi-preprocess-20261031-r2/boot-package/BOOT-csi-preprocess.bin)；[骨架BOOT](../../.local/skeleton-overlay-20261031-r2/boot-package/BOOT-skeleton-overlay.bin)及更早滤波镜像亦保留 |
| 原参考恢复备份 | [BOOT-original.bin](../../.local/hdmi-startup-20261027-r1/board-bundle/common/BOOT-original.bin)，仅为恢复备份，不是当前默认 |
| r45 与派生硬件历史 | [原物理结果](../../tools/pose-v1/evidence/hp2-deferred-consume-20261024-r45/RESULTS.md)、[保留消费候选](probe_free_drain/README.md)、[滤波物理与板测](../../software/pose180_pipeline/resident/PRESENTATION-20261026.md#pl-计算与资源) |
| 独立精简守卫／新增 PL | [精简守卫](pose_stabilizer/README.md)覆盖不足，不可部署；新增几何／批量滤波整机实现已取消 |
| 心率 | [开发记录](../../software/vitals/HYBRID-20261026.md)保留，冻结且未接主链 |

## 清理后的历史路径与保留限制

51 个历史项目上传目录和 `/root/work` 的 3 个 SDK 安装包已删除；安装中的 SDK 和驱动未删除。旧 `/root/demo-v1-20261022-r1/...`、旧长测和旧模型测试目录均不可再作为远端恢复入口。必要原生记录集中在[本机证据归档](../../.local/project-cleanup-20261029-r1/board-evidence.tar.gz)；其完整范围由清理记录说明，不承诺历史每份附件均已补回。

10 月 27 日旧批关闭回执及 TX／RX3 临时 LAN SSH 恢复缺少最终核验；最新清理和临时板端地址撤销不能替代这些旧事实，也不补造旧回执。已有 PC 观察进程未由清理任务停止，不能把“板端无占用”写成所有 PC 进程退出。

| 历史阶段 | 只读追溯入口 |
|---|---|
| 10 月 28 日单人启动包、异常资源保护、模型对比 | [启动包历史](../../software/pose180_pipeline/resident/STARTUP-PACKAGE.md)、[模型测试](../../software/pose180_pipeline/resident/KINECT-BOARD-TEST-20261028.md) |
| 10 月 27 日自适应实时集成与最后停止 | [CSI 集成](../../software/pose180_pipeline/resident/CSI-INTEGRATION-20261027.md) |
| 六片段、3024 次推理与原 BOOT 回退 | [数据集阶段](../../software/pose180_pipeline/resident/DATASET-DEMO.md) |
| 早期 r4～r7 断线恢复与 TX 续期 | [常驻记录](../../software/pose180_pipeline/resident/README.md) |

后续验证使用新记录和实际设备身份，旧包次数不恢复。与独立暂停见 [AGENTS.md](../../AGENTS.md)，未完成的技术验收统一见[后续验证与冻结范围](../../DIFFICULTIES.md#后续验证与冻结范围)。

## 2026-10-27 默认启动发布与七色条

本批 `.local/hdmi-startup-20261027-r1` 复用既有物理资格，没有 RTL、频率、约束、模型或 SDK 变更，也没有新增 EDA。默认 BOOT 为 `.local/pose-filter-integration-20261026-r2/boot-package/BOOT-pose-filter-r2.bin`，SHA256 **`a22faaa71cfde653e03898d2d77bd3adee633f3d0b47b710b87c76bf2a22e291`**。发布当时运行 boot_id 为 **`ba3327af-25df-4425-9b1b-0d4d34aaf4f0`**；新软件 SHA256 `129beb8feb92882e17640dcd7a49a2328f8a46c1da6a2186ec78a66d5a6026ee`。

`hdmi_renderer.cpp` 在首次结果前绘制 1920×1080 全高七色条，顺序为白、黄、青、绿、品红、红、蓝，采用原 RGB565 帧通道；没有骨架或伪造结果。主线程先以独立 tag 提交待机并取得原采纳证明，再开放本地数据集输入。收到结果后恢复原画面；结果后的漏检／重同步提示、PC 页面及蓝色骨架保持。原生像素、等待／恢复、提交标签与计数测试通过；ARM64 Release 编译通过，仅有既有 raster565 符号比较警告。

实板使用官方 test／S11_02 的 49 个 CSI 样本，保持 PS 参数 0.5／0.3／1，同时开启 HDMI／PC。启动前主动消费 **6 拍**异常返回，安全终态后初始化 SDK；没有恢复协议检查 IP。HDMI 先接纳 `tag=1、has_result=false` 的待机，再完成 **49 次新推理／49 次结果接纳**，显示更新合计 50；PC 原始及派生各接收 49 帧，候选／源身份一致。没有输入替换、过期或记录丢弃；EOF、`native_exit=0`、tagged STOP 和帧释放完成，设备占用为空，内核日志无新增。未取得新的实屏人工确认，不把采纳证明写成实屏观感验收。

实际 **1 次候选启动、1 次 SDK、0 次参考回退启动**；BOOT 文件写入 3 次：安装候选、测试期间恢复参考文件以备故障恢复、验证安全结束后再次安装同一候选为默认。最终卸载分区后独立读回全部 BOOT，确认其它启动文件未变。当前运行位流来自本次同一候选启动，最终写文件不宣称又进行了一次启动。包已关闭，所有剩余次数为 0，串口／PC 观察及构建容器均退出，没有后台推理。

原参考恢复文件保存在本机 `.local/hdmi-startup-20261027-r1/board-bundle/common/BOOT-original.bin` ；当时板端副本路径为 `/root/demo-v1-20261022-r1/hdmi-startup-20261027-r1/common/BOOT-original.bin`（该远端目录已在 10 月 29 日清理，不再可用），SHA256 `ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`。历史参考包未改。启动消费仍是同次配置一次性行为，下一次 SDK 验证使用新包和新启动，不在本包重复初始化。

[汇总](../../.local/hdmi-startup-20261027-r1/results/summary.json)、`results/promote.json`／`closed.json`／`final-audit.json` 及 `round-1-result-evidence.tar.gz` 保留实际默认文件、启动、消费、待机和安全结束证据；`pc-observation/` 保留本轮原始／派生输出。`run_release.py` 仅为已关闭本批执行记录，不直接重跑。

后续 `prepare_presentation.py` 默认读取 `default_boot.json` 选择合格硬件及当前已安装 BOOT 作为新包的参考／回退基线，避免普通测试隐式退回旧参考版本；必要时可显式 `--reference-boot` 指定已核对备份。本机新包准备已验证默认哈希／profile 一致，检查包 `.local/hdmi-startup-next-package-check-20261027` 未部署或运行。原参考备份不因更新新包基线而覆盖。

## 历史状态摘录

以下“当前／最新／暂停”等词均指记录当时；其启动身份、额度和阶段结论不覆盖上面的当前入口。原始失败与包关闭状态保留。

2026-10-26 本轮恢复：[展示精简、后处理复验和 PS／PL 滤波比较](../../software/pose180_pipeline/resident/PRESENTATION-20261026.md)。CPU 显示包已关闭，原 BOOT 实际回退通过；新增 PL 流水线候选已完成物理资格及有限板测，原 BOOT 实际回退通过、全部关闭、无后台负载，下一步依据该记录，勿复用下述旧包。

2026-10-26 较早状态：追加 r3 已结束，首轮 PL_KEY1 运行中复位后黑屏失联，完整断电恢复；后两轮各 300 秒及现场画面确认通过，其中第 2 轮 SDK 前有界消费 16 拍返回后正常运行。最终已回原 BOOT，启动编号 `7170b447-f844-421f-b5d6-36140b450e1a`；全部新包关闭、余额 0，无本批活动负载。按键恢复仍未解决，r1／r2 不复活；[唯一结果与产物入口](probe_free_drain/README.md)，精确状态见 `tools/pose-v1/evidence/hdmi-probe-free-drain-20261026-r3/state.json`。

2026-10-26 当前专项已完成：[去除诊断、保留异常消费的 r45 派生候选](probe_free_drain/README.md)。完整物理资格及三轮各 5 分钟真实全链路测试通过，原 BOOT 文件和实际回退启动均已核验，三包关闭、无本批后台工作。产物、精确结果、恢复身份和限制统一见该记录；日志位于 `tools/pose-v1/evidence/hdmi-probe-free-drain-20261026-r1`，运行资产位于 `.local/hdmi-probe-free-drain-20261026-r1`。不复活下述历史额度或独立暂停任务。

2026-10-26 心率专项恢复：[PS 流式模块与实采](../../software/vitals/HYBRID-20261026.md)、[小型 PL 自相关核](../vitals_acf/README.md)。已完成 OOC／仿真和保留全部 r45 保护的独立覆盖层，未生成新整机位流或上板；HDMI／旧问题恢复边界仍按下文。

最新离线工作：[防闪现后处理与精简硬件](pose_stabilizer/README.md)。软件CPU后端、派生展示、1／4路RTL及OOC比较已完成；LUT预算与精简守卫覆盖缺口如实保留，未生成候选位流或部署。板端暂停与r12恢复边界不变；后续不将该覆盖层直接用作启动位流。

前一批次：[r6持续TX租约](../../software/pose180_pipeline/resident/TX-LEASE.md)已按1候选／1 SDK／10分钟／1原BOOT回退完成并关闭，全部余额0、无本批负载。该批原BOOT身份、恢复证据及剩余卡顿以r6记录为准；下述r5及更早状态保留历史，不复用旧额度。

上一批次：[r7共同窗口优化](../../software/pose180_pipeline/resident/WINDOW-RECOVERY.md)已执行并关闭，1候选／1 SDK／600秒运行期／1原BOOT回退，全部余额0、无本批负载；该批原BOOT身份及实际结果以r7记录为准。无窗恢复等待已缩短，显示器黑屏／闪屏已[显示规格限制](../../software/pose180_pipeline/resident/WINDOW-RECOVERY.md#显示规格限制)移出待定位故障。必要新验证可按[最新自主板测规范](../../AGENTS.md#自主权限与重大问题)另记新批次直接执行，不复活旧包。

当前最新批次：[r10／r11／r12](../../software/pose180_pipeline/resident/TOP3-VALIDATION.md)。r12有限推理及PC接收验证完成，随后关闭板端并暂停工作。原BOOT文件已恢复，但未执行回退启动核验；本机观察进程已结束，无本批活动负载，不自动恢复。实际次数、身份、未取回证据及恢复边界以该记录为准。

2026-10-25较早批次：[r5卡顿优化与PC联合长测](../../software/pose180_pipeline/resident/STUTTER-VALIDATION.md)已完成30分钟、RX物理恢复及PC离线实屏验证，正常停止、回原BOOT并关闭。实际1候选／1SDK／1回退，全部余额0；无本批活动负载，该批恢复身份与原值统一见r5记录及本机`.local/pose180-resident-stutter-20261025-r5/run-state.json`。r4及更早包均保持关闭。

2026-10-25新决策：[ADR_50](../../ADR/ADR_50.md)已批准端到端演示优先、有界缓存、PC／归档解耦及分级恢复，无需严格30Hz。实现与本轮真实CSI→推理→HDMI有界结果见[常驻演示记录](../../software/pose180_pipeline/resident/README.md)，已现场确认多轮骨架更新；最新包状态与恢复身份以该记录为准。当时的待办页已撤下，现行保留范围见[后续验证与冻结范围](../../DIFFICULTIES.md#后续验证与冻结范围)；下述旧包失败与关闭额度不回写。

2026-10-25较早严格主链实测：180-query新主链已部署；原BOOT有界测试止于Host归档1秒保护，修正后完成软件验证。新HDMI包`pose180-hdmi-20261025-r2`在SDK前因新增RCAM_UNDERFLOW状态未过准入，实际1候选/0 SDK/1原BOOT回退，已关闭、余额0；当前原BOOT、无占用及详细证据统一见[新主链实测](../../software/pose180_pipeline/RESULTS.md)。下述r53保留历史，不作为当前启动身份或新额度。

入口整理：2026-10-25。HDMI旧板测r53已回原BOOT；实际1次候选/1次SDK/1次回退，包关闭、余额全部0，批次结束时无本批后台工作。后续独立180-query批次的恢复见[部署实测](../../tools/pose180/deploy/RESULTS.md)；恢复时不能将历史运行身份视作实时身份。现行执行边界见[项目总览](../../PROJECT-PROGRESS.md)。

## r53历史核验状态与原始证据

| 用途 | 唯一维护入口 |
|---|---|
| 当前事实、恢复身份、问题及原始数据位置 | [r53 RESULTS](../../tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/RESULTS.md)、[state.json](../../tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/state.json) |
| 原BOOT运行、启动文件/SDK及无占用核验 | [final-audit.json](../../tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/final-audit.json)、[closed.json](../../tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/closed.json)；历史boot_id不得直接作为下次会话身份 |
| r53首读/即时副本/两轮SDK晚读和协议完整原值 | [candidate-evidence.tar.gz](../../tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/candidate-evidence.tar.gz)、[离线字节比较](../../tools/pose-v1/evidence/hdmi-pipeline-20261024-r53/index-read-analysis.json) |
| 当前源码、硬件与数据流 | [INTEGRATION](INTEGRATION.md)、[r45硬件源码](diagnostics/deferred_consume_r45/sources)、[r53主调度](diagnostics/native_rgb565_r53/joint/main.cpp)、[SDK显示适配](diagnostics/native_rgb565_r53/display/hdmi_output.cpp) |
| 当前硬件物理资格与BOOT对应关系 | [r45 RESULTS](../../tools/pose-v1/evidence/hp2-deferred-consume-20261024-r45/RESULTS.md)；r46～r53复用，无重新EDA或新增时序例外 |
| 隔离/逐拍波形/原生协议历史 | [S01隔离](diagnostics/S01-ISOLATION.md)、[r30波形](diagnostics/waveforms-r30-20261022/README.md)、[r37协议结果](../../tools/pose-v1/evidence/hp2-startup-protocol-20261023-r37/RESULTS.md) |
| 实际异常消费后有限业务 | [r52 RESULTS](../../tools/pose-v1/evidence/hdmi-long-git-20261024-r52/RESULTS.md)；不以r53健康消费0的样本替代 |
| 历史成果、难点与现行保留范围 | [Done](../../Done.md)、[DIFFICULTIES](../../DIFFICULTIES.md)、[后续验证与冻结范围](../../DIFFICULTIES.md#后续验证与冻结范围) |

## r53 当时结论与执行边界

r53健康启动（AR=0/R=0、消费0），完成187次HDMI采纳后第189次推理首读索引1568字混入同帧姿态内容。晚读正确不能修补首读，产生环节未定；只见瞬间骨架，持续实屏和联合长期均未通过。

保留原有限消费及AI四路：HC0→HP0、HC1→HP1、HC2→HP2/S00、HC3→HP3；HDMI→HP2/S01。官方说明HP FIFO位于PL，撤下PS内部HP FIFO残留的既定解释；D45根因未关闭，文档任务不恢复已中止的根因板测。

所有旧包保持关闭；新增BOOT/重启、失败SDK负载再执行按具体新包授权，不复活旧次数。旧DATA独立暂停，不删模块、不修FAT、不改模型/数学/SDK/NPU分配/帧协议，不接入Vivado MCP。SSH为主、COM7备用，未来操作前重新核验实际身份与恢复通道。

正确按键为PL_KEY1/SW6/F8；PL_KEY2/SW7/E7用于SDI GTX。观测器清零、PL互联复位、宏内部事务状态分别认定。旧r26与10月18日暂停报告保留历史，不作为最新状态或新操作授权。
