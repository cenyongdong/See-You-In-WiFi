# r7 独立完整重建与板测状态

2026-11-04：从 GitHub Release 重新下载 r7 RAR，在新目录解压后完成综合、实现前优化、布局／物理优化、布线、完整物理报告、BIT 生成及 Procise 适配；七个原生阶段退出码均为 0，累计约 41.0 分钟。ARM64 应用、原生编译和 8 项离线测试通过。新 BOOT 已完成离线封装及分区核验。

**独立生成位流及有限上板功能验证已完成，现场确认画面正常、骨架持续更新。** 计划上限 120 秒，实际有效运行 57.456 秒后人工停止；完成 853 次新推理／HDMI 采纳并安全退出。已恢复安装前实际读回的原 BOOT，正常重启后设备空闲。该短测不作为完整 120 秒、长期或实时 CSI 精度验收。

## 输入与独立性

- [发布的 r7 源码包](https://github.com/cenyongdong/See-You-In-WiFi/releases/download/deploy-r4-20261031/pose180-current-sources-20261104-r7.rar)：190,554,743 字节，SHA256 `4481f7503f4093ce4fe5cd16738b4580465d00e0cf221b9134eab27e8c0cee08`。
- 本次下载、RAR 检查、新目录解压和源码清单校验均实际执行。清单包含 799 个条目，另有清单文件自身；构建后再次校验通过，未修改包内源码。
- 新工作目录为本机 `.local/r7-board-20261104-r1/`，解压源码位于其 `source/pose180-current-sources-20261104-r7/`，独立工程位于 `hardware/`。构建未覆盖工作区源码，也未读取旧工作区的最终综合／布线产物。
- 按包内流程使用随包提供的厂商 IP、PS 导出及 CSI v2 增量参考。完整执行各阶段不表示禁用包内增量参考，也不表示脱离厂商工具／许可／SDK。实际工具为原厂适配 Vivado 2018.3、Procise 2025.1.1 temp／SVN 32494，目标 JFMQL30TAI676H，Vivado 逻辑器件为 `xc7z030ffg676-2`。

[下载身份](evidence/r7-rebuild-board-20261104-r1/download.json) · [解压与准备命令](evidence/r7-rebuild-board-20261104-r1/source-steps.json) · [输入路径检查](evidence/r7-rebuild-board-20261104-r1/input-isolation.json) · [构建后清单校验](evidence/r7-rebuild-board-20261104-r1/post-build-source-integrity.log)

## 完整实现与物理检查

| 检查 | 本次结果 |
|---|---|
| setup：WNS／TNS | +0.030 ns／0，失败端点 0 |
| hold：WHS／THS | +0.029 ns／0，失败端点 0 |
| 路由 | 97,096 条可布线网络全部完成，路由错误 0 |
| 内部时序覆盖 | 无最大延迟约束缺失的内部端点、无缺少时钟的寄存器端点 |
| 功能 CDC、CSI／滤波时序、总线偏斜 | 既定有界路径及资源检查通过 |
| 原有 AI 最小周期例外 | `clkout1_buf/I` 为 −0.409 ns；`plle2_adv_inst/CLKOUT0` 为 −0.071 ns |
| 原有 GT DRC 范围 | REQP-52：`rx_sdi_inst/SDI0/SDI/GTX_i/gtxe2_i`；REQP-56：`rx_sdi_inst/gtxe2_common_0/gtxe2_common_i` |

两处 AI 对象均位于 `U0_ps_ai_peripheral/ZGolo/u_AI_Mate_top/clkrst_wrapper_u0/AI_CORE_CLK/inst/`。仅按[原有 AI／GT 适配范围](../FPGA/hdmi_candidate/BOARD-RELEASE-20261016.md)认定 BIT 前置资格；`raw_timing_pass=false` 原样保留，不宣称原始时序／DRC 零违例。没有新增时序例外、降频或 DRC 豁免。

路由中间摘要曾出现 WNS −0.031 ns、TNS −0.051 ns，后续路由放置调整后收敛到上述最终值；中间值仍在原生日志中。不能用中间摘要代替完整布线后的检查。

[物理资格及实际输入哈希](evidence/r7-rebuild-board-20261104-r1/qualification.json) · [最终时序](evidence/r7-rebuild-board-20261104-r1/physical/timing-final.rpt) · [脉宽](evidence/r7-rebuild-board-20261104-r1/physical/pulse-width.rpt) · [路由](evidence/r7-rebuild-board-20261104-r1/physical/route-status-final.rpt) · [DRC](evidence/r7-rebuild-board-20261104-r1/physical/drc-final.rpt) · [总线偏斜](evidence/r7-rebuild-board-20261104-r1/physical/bus-skew-final.rpt) · [控制 CDC](evidence/r7-rebuild-board-20261104-r1/physical/control-cdc.tsv)

## 软件与 BOOT

从本次解压目录使用 `csi-v3-arm64` 和 `native-offline` 预设，在新的容器构建目录中编译。ARM64 ELF 为 AArch64；生成的 `pose180_demo` 与 r4 已发布程序哈希相同。8 项测试全部通过：postprocess、single_person、buffer、renderer、overlay、release_guard、hdmi_resource、journal。编译未初始化 SDK，构建结束后容器恢复原来的停止状态。

BOOT 使用本次新适配 BIT 和包内 FSBL／BL31／U-Boot，保留已部署映像名称以避免修改名称表。PL 分区位于偏移 186,816，长度 5,980,464 字节；按原格式转换后与本次位流载荷完全一致，非 PL 字节及填充与 r4 BOOT 一致。

首次本地封装包装器没有匹配到原厂后处理改写的启动器入口，实际额外执行了一次 Procise 位流适配，原生退出码为 0，但未产生 BOOT，包装器退出码为 1。该额外适配结果与此前留存副本逐字节相同。修正为明确指定 BOOT Tcl 的启动器后，BOOT 封装退出码为 0，分区核验通过。原始失败、原生日志和修复记录保留；未重跑综合或布局布线，未修改 r7 包内源码。

[软件命令和退出码](evidence/r7-rebuild-board-20261104-r1/application/steps.json) · [8 项测试日志](evidence/r7-rebuild-board-20261104-r1/application/native-tests.log) · [BOOT 分区核验](evidence/r7-rebuild-board-20261104-r1/boot/composition.json) · [包装器原失败](evidence/r7-rebuild-board-20261104-r1/boot/wrapper-failure.json) · [修复结果](evidence/r7-rebuild-board-20261104-r1/boot/wrapper-recovery.json)

## 新产物与保留位置

| 产物 | 字节数 | SHA256 |
|---|---:|---|
| 原生 BIT | 5,980,025 | `821b02e3946e5eb935c520def49443f6ef9cab64f7e2a4130b1c794b803e1b1a` |
| Procise 适配 BIT | 5,980,609 | `116cd23b2011136e6492b4da0095c937cdd034ccc316976c6a3852a074f2760f` |
| 新 BOOT | 7,023,552 | `20ba0696f7d121289af65b31819b67b2dd411874a6842d4329e2c8bdd2ec39bd` |
| ARM64 应用 | 695,208 | `e85fac442dadb22e263698242c8dbcb63ee5841b1b52c2ba8436bb8d5a1a1bb3` |

完整原生 stdout、Vivado log、退出码及物理报告保存在 `Deliverables/evidence/r7-rebuild-board-20261104-r1/` 的 `native/`、`physical/` 和 `reports/` 下；软件日志在 `application/`，BOOT 两次包装器记录在 `boot/`。本轮工程原始 log 和报告也原位保留，未清理工程。

大体积 BIT、BOOT、应用及各阶段 DCP 仅在本机留存，仓库未附：工作目录中的 `hardware/fpai_demo_vivado.runs/impl_pose_filter/`、`boot/BOOT.BIN`、`application/pose180_demo`、`hardware/*.dcp`。精确绝对路径、尺寸及最终产物哈希见[产物身份](evidence/r7-rebuild-board-20261104-r1/local-result.json)，工程日志／报告／检查点清单见[保留文件](evidence/r7-rebuild-board-20261104-r1/retained-files.json)。

## 上板结果与恢复

使用本次新 BOOT 和 r7 新编译应用，外部测试夹具为已发布官方数据集；实际经过 S51_10、S22_01、S23_43 三个单／双／三人片段。原模型、SDK、TopK=3、严格 score >0.2、CPU 人物滤波、PL CSI 和 PL 骨架绘图保持原配置。现场确认 HDMI 画面正常、骨架持续更新。

| 项目 | 实际结果 |
|---|---|
| 运行范围 | 上限 120 秒，人工正常停止；有效运行 57.45598152 秒，原生进程总计约 83.598 秒 |
| 新推理／HDMI 采纳 | 853／853；末次选中 1／2／3 人的帧数分别为 284／288／274，另有 7 帧未选中人物 |
| PL CSI | 853 次调用，51,180 组；硬件故障 0，后端降级 0 |
| 原有边界回退 | 4,287 次点边界回退，1 次整窗边界回退；不解释为严格逐位数值无损 |
| 有界处理原值 | 接收 856 窗、输入替换 3、记录丢弃 1，最长结果间隔 293 ms |
| PC 观察 | 本轮未连接 PC 观察器；`pc_sent=0`、`pc_dropped=853`、`view_dropped=853` 原值保留，不据此宣称 PC 端验收 |
| 退出和释放 | 原生退出码 0，`native_shutdown_complete=true`；STOP tag 1879048227 已证明，随后释放帧资源 |
| 结果留存检查 | 有界环保留序号 641–853 共 213 条完整记录，输入、分数、姿态及计时均为有限值，索引有效；两份 SDK 显存读回与写入内容一致 |
| 关闭后状态 | 设备占用为空，临时地址已撤销，无测试端口监听，无 SDK 后台续跑 |

213 条记录来自原有轮转记录器，不能作为全部 853 次输出的严格基线比较。业务状态快照仍保留末次 `running` 字段；结束判断采用原生退出码、完成回执、监督器退出、STOP 证明和设备占用检查。候选启动后的内核日志与测试结束时完全相同，未增加内核日志。

本轮实际执行：SDK 启动 1 次；候选 BOOT 安装／正常重启各 1 次；原 BOOT 恢复／正常重启各 1 次。全部九项启动文件及六项 SDK 身份恢复核验一致，恢复后未再启动 SDK。本轮已关闭，不复用已消耗次数。

- 测试前 boot_id：`871a1021-493b-454a-9edc-1d71d603b3fc`。
- 候选 boot_id：`92a13649-0769-407a-852e-2f5c16482827`；BOOT 为本次新产物 `20ba0696f7d121289af65b31819b67b2dd411874a6842d4329e2c8bdd2ec39bd`。
- 恢复后 boot_id：`dc15a18d-0385-482f-84f2-577baf3889a7`；BOOT 恢复为 `23922f488d9d4842f217f1b318624c82607e35c6dc0c0b2ea3c803ca4023aa35`。
- 板端证据目录：`/root/pose180-r7-rebuild-20261104-r1`。板端墙钟未同步，运行子目录日期为 2026-11-03；本轮实际执行日期为 PC 的 2026-11-04（Asia/Shanghai），持续时长使用单调时钟，原始时间戳未改写。

[板测结果](evidence/r7-rebuild-board-20261104-r1/board/result.json) · [原生退出回执](evidence/r7-rebuild-board-20261104-r1/board/run/outcome.json) · [完成回执](evidence/r7-rebuild-board-20261104-r1/board/run/run/completion.json) · [STOP 证明](evidence/r7-rebuild-board-20261104-r1/board/stop-proof.json) · [保留结果检查](evidence/r7-rebuild-board-20261104-r1/board/retained-output-check.json) · [实屏观察](evidence/r7-rebuild-board-20261104-r1/board/screen-observation.json) · [最终恢复审计](evidence/r7-rebuild-board-20261104-r1/board/final-audit.json) · [关闭回执](evidence/r7-rebuild-board-20261104-r1/board/closed.json)

板测的原生日志、运行／启动／关闭记录和恢复审计已保存在上述证据目录的 `board/` 下；完整取回包及二进制结果在本机留存，仓库未附：`.local/r7-board-20261104-r1/board-evidence.tar.gz` 和 `returned/`。证据包 SHA256 为 `dd2200ae8eb6635346f51fd7e0dddb9ccd4f724569eabc700ecc3376daff621f`。原 BOOT 备份同时留存在 PC 的 `pretest-BOOT.bin` 和板端本轮目录，均已核验。

没有更新远端 Release、部署 RAR 或默认 BOOT 身份文件；包内“未上板”描述保留为发布时快照。本轮没有实时 CSI、PC 观察器、长期稳定性或精度验收。[执行范围](evidence/r7-rebuild-board-20261104-r1/plan.json) · [最终板测状态](evidence/r7-rebuild-board-20261104-r1/board-state.json)
