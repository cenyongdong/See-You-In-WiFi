# Wi-Fi 人体三维姿态端到端演示

**版本定位（2026-10-29）：** 本页保留早期工程、兼容接口或对应批次结果，文中的“当前”只指该版本。现行 180-query 主链在[主工程](../pose180_pipeline/README.md)，运行及验收范围见[最终进度](../../PROJECT-PROGRESS.md)；旧命令不作为最新部署入口。

## 2026-10-13正式核心重构版本

当前入口使用[software/core](../core/README.md)六个功能目录，旧pose_v1和历史检查器保留。参数解析独立为demo_options，视频网络/绘图/编码线程入口分别封装；公开接口和原运行行为保持。构建仍导出锁定别名，但当前锁显式引用新核心；原锁和路径/哈希映射见[ADR_47](../../ADR/ADR_47.md)。

实际完成：11组本机、ARM构建、Lite CPU107/22输出/59600 FP32逐位，以及三窗口全部原始输入/预处理/分数/姿态逐位旧参考。354编码/294 GUI解码、全3来源/42关节、drain/LAST和回收通过，规整0，身份与内核同。[完整证据](../../tools/pose-v1/evidence/core-refactor-20261013-r1/README.md)。本轮没有60窗口执行；下方2026-10-11旧命令和结果保留为历史。

当前已验证构建为`.local/pose-v1-build/demo-refactor-20261013-r1`，板端为`/tmp/wifi-pose-demo-refactor-20261013-r1`；已完成的运行目录不得再次使用。默认模型来源重新核验为`D:/Person-in-WIFI-3D/Person-in-WiFi-3D-repo/result/icraft_2024`，配对SHA保持原固定值。

本机执行位置是当前仓库根目录`D:/FPGACompetitionProject`。本轮实际核验的回放环境位于旧受管工作区`C:/Users/cenyongdong/.codex/worktrees/dea3/FPGACompetitionProject/.local/pose-v1-conda/python.exe`，Python3.10.21/NumPy2.2.5/h5py3.16.0；仅使用该既有环境，旧工作区不写入。播放器仍用既有WIFI-densepose。Docker/FPAI及原SDK必须可用，不安装替代版本。

可复核静态身份：`python software/demo/verify_core.py static`。`verify_core.py native --tag`和`build.py --tag`的tag必须是新的唯一值，分别生成本机字节对照与ARM构建，成功退出才通过，任何错误停止并保留日志。

`validate_board.py`用于本轮已批准的一次CPU107→三窗口顺序验证：参数`--build`指定核验通过的构建，`--evidence`指定不存在的证据目录，`--cpu-package/--reference`指定原身份输入和数值参考，`--model-dir`指定同SHA模型，`--viewer-python`指定现有播放器。此入口在身份/Host协议/CPU完整输出门检后才放行三窗口，密码由遮罩窗口在内存中输入，预期CPU及short报告、完整tar/值/日志和清理证据。失败/超时/身份变化立即停止，不自动重试；再次实板运行须先按项目约束确认新阶段与新远端目录，不能重复本轮已完成路径。

## 2026-10-11原演示说明（历史范围）

演示入口整合既有框架：主机读取预采 CSI → TCP → Lite 的 PS 预处理和 PS/NPU 混合推理 → SDK 无关显示子进程绘制骨架 → 板端 VPU 编码 H.264 → RTSP/TCP → 主机 OpenCV 窗口。

默认每秒发送两个**完整 CSI 窗口**，编码预览为10fps。推理期间重复最新画面，启动画面标记 NoInput；重复画面不计新姿态吞吐。最高分候选的14关节坐标来自真实板端模型输出，无 GT 注入、主机推理、平滑或候选修补。HDMI不接入。

本版是有界演示：默认60输入、约30秒回放；可设1–100输入，最长回放55秒。板端总预算180秒、编码上限1000、一次单Engine/单VPU生命周期。尚未修复的并发首次坏读、VPU连续页启动条件、严格5Hz和长期可靠性限制继续保留。任何索引/非有限/SDK/网络异常均保存现场停止。

## 文件与依赖

| 模块 | 入口 | 职责 |
|---|---|---|
| 原始输入 | `host/replay.py` | 只读取 MAT `csi_out`，调用既有 PIWCSI1 编码，无预处理/GT |
| 主机控制 | `host/run.py` | 数据目录、速率、帧号、播放器就绪与退出管理 |
| 主机显示 | `host/viewer.py` | FFmpeg RTSP/TCP 实际解码与显示、帧指纹/快照 |
| 板端编排 | `board/main.cpp` | 主线程持有Engine，TCP接收、错误停止、释放顺序 |
| 推理适配 | `board/demo_engine.*` | 统一配置既有Engine及异常/阶段/对象证据，保持主线程所有权 |
| 视频模块 | `board/demo_video.*` | 显示队列、常驻VPU、拥有AU、RTSP线程 |
| 结果保存 | `board/demo_results.*` | 有界保存原始CSI、全部分数/姿态/预处理输入与选中关节 |
| 运行门检 | `board/runner.py` | 身份/资源、首次启动条件、180秒预算、完整失败归档 |
| 构建部署 | `build.py`、`deploy.py` | 固定框架来源/SDK/厂商库，新目录构建和传输 |

`baseline-lock.json`记录被复用的源码和编译别名，而非复制并维护另一套数学实现。构建时导出已冻结框架到独立暂存目录；实际编入的核心为 `trace_application_core_r2`、`read_input_bridge`、CPU适配、显示与VPU/RTSP模块。原验证检查器均保留。

当前本机已有环境可直接使用，不需要安装：

- CSI回放：仓库 `.local/pose-v1-conda/python.exe`，Python3.10.21、NumPy2.2.5、h5py3.16.0。
- 视频窗口：`C:/Users/cenyongdong/miniconda3/envs/WIFI-densepose/python.exe`，OpenCV/FFmpeg；可通过 `--viewer-python` 指定其他已配置环境。
- 交叉编译：Docker容器 `FPAI`，ARM64 SDK3.39.0，厂商live555/SSL静态库；`build.py`中记录本机工具路径，逐项验哈希。

## 构建与运行

以下 PowerShell 命令在**仓库根目录**执行；每次使用未存在的新构建/证据目录。模型不放进Git，使用已验收 `.local/pose-v1-combined-read/package-20261010-r1/graph/piw24_ZG.json/.raw`。如果模型位置不同，核对同一SHA后在部署脚本中指定位置，禁止换用未经验证的图或权重。

已验证的构建为 `.local/pose-v1-build/demo-20261011-r5`。可直接将同一程序部署至下一未使用的r5目录；当前已完成的r4目录及证据不能覆盖。若需要重新编译，使用 `build.py --tag demo-20261011-r6` 的新构建目录并核对来源；下面演示使用已验r5程序。

```powershell
& .local/pose-v1-conda/python.exe software/demo/deploy.py install
& .local/pose-v1-conda/python.exe software/demo/deploy.py short
& .local/pose-v1-conda/python.exe software/demo/review.py short --evidence tools/pose-v1/evidence/demo-20261011-r5
& .local/pose-v1-conda/python.exe software/demo/native_render.py short --evidence tools/pose-v1/evidence/demo-20261011-r5
& C:/Users/cenyongdong/miniconda3/envs/WIFI-densepose/python.exe software/demo/review_video.py short --evidence tools/pose-v1/evidence/demo-20261011-r5
& .local/pose-v1-conda/python.exe software/demo/deploy.py demo
& .local/pose-v1-conda/python.exe software/demo/review.py demo --evidence tools/pose-v1/evidence/demo-20261011-r5
& .local/pose-v1-conda/python.exe software/demo/native_render.py demo --evidence tools/pose-v1/evidence/demo-20261011-r5
& C:/Users/cenyongdong/miniconda3/envs/WIFI-densepose/python.exe software/demo/review_video.py demo --evidence tools/pose-v1/evidence/demo-20261011-r5
```

每条命令成功后再执行下一条，失败保留结果并停止。SSH密码仅在内存提示中输入。默认新目录为 `/tmp/wifi-pose-demo-20261011-r5` 和 `tools/pose-v1/evidence/demo-20261011-r5`；明确指定其他构建时，install/short/demo始终使用同一个 `--build`。Host协议成功后运行short；short的数值/来源与原VPU码流几何审查均通过，才运行60窗口。`native_render.py`使用已验r5导出的固定渲染来源，本机Docker/FPAI必须可用；不执行板端设备操作。

也可分终端手动启动。本机媒体程序为默认GUI，**Q/Esc**关闭窗口；`--headless`仅用于无人值守解码验证。

Lite终端（已验r4包仍在板端；先确认无项目进程和连续页资源充足，推荐使用上面的runner门检。以下直接运行绕过runner资源审计，新输出目录只用一次）：

```sh
cd /tmp/wifi-pose-demo-20261011-r4
./pose_demo --model-dir models --output /tmp/demo-fresh-results --max-frames 60 --allow-device-init --allow-vpu-stream --allow-network
```

主机PowerShell：

```powershell
& .local/pose-v1-conda/python.exe software/demo/host/run.py --data 'D:\Person-in-WIFI-3D\Person-in-WiFi-3D-repo\data\wifipose' --frames 60 --hz 2 --output .local/demo-host-new
```

默认地址192.168.126.49，CSI端口39001，视频地址 `rtsp://192.168.126.49:8554/pose`。板端可用 `--bind/--input-port/--rtsp-port` 修改，主机同步设置。主机先等待实际解码视频，再建立一次输入连接；仅启动前拒绝连接可再次探测，不重连或重发已接受的CSI会话。

## 证据、退出和实际状态

主机保存源MAT哈希、原始负载哈希、发送清单、解码帧ID/指纹和截图。板端保存全部100槽分数、100×14×3姿态、选中骨架、CSI负载和模型输入，视频样本来源/重复标记、PTS、原H264、VPU/RTSP/引擎记录。跨主机与板子时钟未同步，不直接相减宣称端到端延迟。

资源不足时启动门检在设备打开前拒绝；可按既有授权执行一次有记录的规整，但规整未恢复高阶页即停止，不能保证首启动。不得清缓存/重启/改CMA/SDK/BOOT以绕过失败门检，未经批准不执行这些操作。

正常退出停输入生产→完成显示→VPU drain/LAST→关闭AU通道→网络源回收→workers join→保存结果→销毁Engine。异常路径保留原Host输入/两轮晚源读取，执行abort STREAMOFF并退出，无自动重新打开设备。

2026-10-11实际通过：三窗口短阶段与60窗口正式演示均在主机GUI实时解码显示，分别352/637编码帧、292/577主机解码帧，覆盖全部3/60个真实姿态来源；正式阶段60接收/60消费/0覆盖、60个不同姿态输出。默认2Hz输入与10fps预览保持，启动约30秒NoInput为Engine初始化，不表示使用固定骨架。

前三份308/309/310的原始负载、PS模型输入、完整分数和姿态逐位旧参考；其余57份检查形状、有限性、选择与视频映射，尚无完整数值参考验收。原码流离线解码共989帧，882个关节投影可见性通过；H264为有损编码，不要求RGB逐位一致。

最初启动失败及两个入口初始化遗漏已完整保留；一次重启已执行，BOOT/SDK/模型/CMA未改，成功两阶段规整0。正常drain/LAST、两STREAMOFF、线程/子进程/端口回收及最终身份通过，当前无后台。详见[结果](../../tools/pose-v1/DEMO-RESULTS-20261011.md)、[ADR_45](../../ADR/ADR_45.md)、[技术细节](../../ADR/TechDetails.md)。旧高负载坏读定位继续暂停，未宣称永久首启动、严格5Hz、30分钟或HDMI通过。
