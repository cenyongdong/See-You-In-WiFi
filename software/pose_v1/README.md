# CSI首版：当前实施状态（2026-10-07）

**版本定位（2026-10-29）：** 本页保留早期工程、兼容接口或对应批次结果，文中的“当前”只指该版本。现行 180-query 主链在[主工程](../pose180_pipeline/README.md)，运行及验收范围见[最终进度](../../PROJECT-PROGRESS.md)；旧命令不作为最新部署入口。

> 当前RTSP首批已验证：200帧传输/重连与标准播放器100帧逐位原视频，有限上下文清理通过，无新依赖。[结果/录制视频](../../tools/pose-v1/RTSP-RESULTS-20261007.md)、[F0接入准备](../../tools/pose-v1/F0-INTEGRATION-PREP-20261007.md)。当前是预生成码流回放，在线VPU/实际推理合并、显式色彩、HDMI/整机长期仍待；旧未RTSP/暂停条目为历史。

> 当前最新：视频任务已恢复，真实27骨架/54帧有限编码及两独立上下文重复通过，主机完整核验，MMAP描述兼容修正已采用。[结果/视频](../../tools/pose-v1/VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md)、[恢复入口](../../tools/pose-v1/RESUME-VIDEO-20261007.md)。原推理/SDK/BOOT保持，HDMI1080p60未改时序，RTSP/实时合并/整机长期未通过。旧暂停和失败条目按历史保留。

> 当前视频任务暂停：新`vpu_encoder.hpp/.cpp`有限接口与`vpu_sequence_check`已构建/协商；真实27画面54输入测试发生固件MMU ABORT，未动态编码验收或生产接入。[报告](../../tools/pose-v1/VIDEO-SEQUENCE-RESULTS-20261007.md)、[恢复](../../tools/pose-v1/RESUME-VIDEO-20261007.md)。原30帧/推理/渲染保持，阶段恢复后前不继续测试。

> 最新VPU独立文件：新增SDK无关`src/vpu_encode_check.cpp`，两端实际MPLANE、NV12两plane与H264单plane/30帧编码通过，MP4上传主机逐帧审查通过。[报告/样片](../../tools/pose-v1/VPU-RESULTS-20261007.md)、[命令](../../tools/pose-v1/VPU-COMMANDS-20261007.md)。暂未生产编码器/RTSP/并发推理，原渲染保持720p。HDMI目标改为1080p60，设备测试暂停，未改时序/BOOT。

> 最新E1-C：新增skeleton_render及独立检查器，实际CPU画面/三格式、ARM27图与三帧网络结果绘图通过。[报告与预览](../../tools/pose-v1/RENDER-RESULTS-20261007.md)、[命令](../../tools/pose-v1/RENDER-COMMANDS-20261007.md)。render-CMakeLists.txt为隔离构建入口；旧应用/引擎/数学保留。尚未HDMI/编码/RTSP，[V0查询](../../tools/pose-v1/V0-VIDEO-PAIRING-20261007.md)不替代输出验收。

> 最新E1-A/B：生产入口已不依赖冻结Tokens，TCP完整组包/单槽与三/27帧真实网络对照通过；38次成功前向输入及全输出逐位此前板端。[结果](../../tools/pose-v1/APPLICATION-RESULTS-20261007.md)、[命令](../../tools/pose-v1/APPLICATION-COMMANDS-20261007.md)。2Hz为正确性验证，不作整机吞吐；尚无渲染/视频/长期服务。

> 最新：现有数值阶段已人工验收；profiling关闭＋单时钟计量及消息构造优化已完成，处理基线5.24655Hz/P95 190.75409ms，整机/视频/长期未验收。[P2结果](../../tools/pose-v1/P2-RESULTS-20261007.md)。较早“数值未验收/4.65Hz/P2候选”保留为历史。

原runtime_core保留固定参考门禁与Host107/E0/N1/P1证据；新application_core提供生产和checked验证两入口、完整FP32数组及状态/耗时。生产配置使用minimal_log=true及有界采样，单Engine串行；隔离构建入口tools/pose-v1/application-CMakeLists.txt，原主CMake未覆盖。[后续路线](../../tools/pose-v1/FULL-FLOW-PLAN-20261007.md)已批准，下一步渲染和视频配套。

<details>
<summary>历史r1/r2与早期交付说明（不作当前执行入口）</summary>

# CSI首版：当前实施状态

当前以2026-10-06 [r6三样本混合工程验收](../../tools/pose-v1/MIXED-FRAME-STATE-R6-RESULTS.md)为准：跨帧同输出已解决，SDK状态清理/计数与输出就绪协议通过，模型/CPU数学/NPU分工保持。
[下一阶段计划](../../tools/pose-v1/NEXT-PHASE-PLAN-20261006.md)已准备，运行核心、扩展数值及低日志基线的新实施范围待确认。
原pose_inference_check仍保留；下方r1/r2“当前”“未编译/板测”“下一步”是历史阶段，勿照旧命令重跑或宣称视频已通过。

当前快照r2构建及源码/SDK身份已核验，[构建结果](../../tools/pose-v1/MIXED-BINDING-R2-BUILD-RESULTS.md)。
新程序尚未板测/快照运行，新r2目录传输后先Host回归；原r1失败及门检保留。

并应用绑定快照r2：仅mixed_check.cpp增加创建后/apply后SDK公共元数据快照，原严格门检/其他源码保持。
新包已准备，尚未编译/新板端运行；[当前命令](../../tools/pose-v1/MIXED-BINDING-R2-COMMANDS.md)。
旧r1 apply未通过，r2是取证，仍不能直接模型forward或宣布部署通过。

当前SDK设备内存往返已验收，[结果](../../tools/pose-v1/MIXED-MEMORY-RESULTS-20261006.md)。
两16KiB ADDR PLDDR/六输出24,576FP32逐位一致；尚未模型Session或NPU计算，下一步仅apply-check。

当前offline真实RAW/PS门检已通过，[结果](../../tools/pose-v1/MIXED-OFFLINE-RESULTS-20261006.md)；
仅真实参数/输入/图/注册验收，设备内存与Session仍待实测。下一步传验收文件后仅30秒memory-check。

最新mixed-r1 Host暂存桥已独立通过107例/12注册/22输出59,600FP32回归，见[结果](../../tools/pose-v1/MIXED-HOST-RESULTS-20261006.md)。
仅Host CPTR，真实RAW/NPU内存/完整Session仍待逐阶段验收；Host不重跑，现在传入验收文件并处理离线预检失败目录。

最新2026-10-06 mixed-r1已交叉编译并经代理文件核验，一条缩进warning审查不影响预期JSON行为，源码保持。
见[构建结果](../../tools/pose-v1/MIXED-BUILD-REVIEW-20261006.md)；当前继续传输及Host桥回归，尚无新板端运行结果。
下面新C++未编译为初次交付状态。

2026-10-06已批准并交付独立 `pose_mixed_check`：新mixed_bridge/mixed_check/mixed_host_check复用已验收CPU计算接口，
SDK复制至Host暂存、六阶段独立验证；原CMake/推理器/CPU实现保持。独立构建配置在tools/pose-v1/mixed-validation-CMakeLists.txt。
新C++尚未编译/板测；[当前命令](../../tools/pose-v1/MIXED-VALIDATION-COMMANDS.md)。
本机三样本[ONNX参考](../../tools/pose-v1/ONNX-REFERENCE-RESULTS-20261006.md)已完成，不等待Icraft全CPU Matmul；
实际NPU交接、完整模型数值及HDMI/RTSP仍未验收。

2026-10-06独立CPU候选已在Lite通过107例/22份输出的数值及注册门检，
见[结果与限制](../../tools/pose-v1/CPU-ADAPTER-RESULTS-20261006.md)。
原Gather保持，CPU Matmul未补齐；候选仍未接入本目录原推理器/CMake，实际NPU内存交接和完整模型未验收。
下面候选未编译/运行文字保留为较早状态，首版NPU及双路要求保持。

2026-10-05新增隔离CPU候选：`include/host_cpu_adapter.hpp`、`src/host_cpu_adapter.cpp`、
`src/host_cpu_adapter_check.cpp`。使用`tools/pose-v1/cpu-adapter-CMakeLists.txt`独立构建，
**未接入本目录原CMake或pose_inference_check**，不补CPU Matmul或覆盖Gather。
范围、SDK证据和设计限制见[CPU-ADAPTER.md](../../tools/pose-v1/CPU-ADAPTER.md)，
人工操作入口见[CPU-ADAPTER-COMMANDS.md](../../tools/pose-v1/CPU-ADAPTER-COMMANDS.md)。
目前仅源码交付和静态审查，尚未编译/实板CPU测试，不能推定完整混合推理通过。

目标：PS原始CSI预处理→PS/NPU混合推理→单人14关节固定三维视角→720p HDMI＋H.264 RTSP。
骨架≥5Hz、争取10Hz；板端画面完成P95≤500ms，播放器延迟另测，30分钟稳定性待验收。

**当前不是完整首版。** 300份真实回放预处理门检及运行FPGA版本身份已通过；
SDK混合推理兼容性和视频时序仍待核验，NPU推理/HDMI/VPU访问暂停。

## 已实现

- C++17原始CSI读取、幅度及相位校正、正确模型token布局；无新的滤波/平滑。
- MAT读取和原始TCP回放发送端，格式见 [PROTOCOL.md](PROTOCOL.md)。发送端未与板端服务联调。
- 从原训练类AST提取三种预处理方法，避开mmdet/GPU依赖；合成与真实样本数值对照。
- 已交叉编译并在Lite上运行独立预处理检查器，不接触NPU/HDMI/VPU寄存器。
- 启动分区FAT16只读检查、模型和源码哈希、错误样本和环境锁定。

## 已验证与未解决项

1. 已更换BOOT，板端哈希与所选Lite 25122301包一致；其余8文件保持原镜像身份。
   FSBL日志确认PL下载，BOOT配置载荷与同包.bit对应；经单独批准的最小只读探测回读FPGA版本0x25122301。
   uEnv二次download.bit加载未确认，启动配置未改，版本相符不代表推理兼容性或HDMI时序已通过。
2. 修正零幅值复数运算的带符号零行为后，扩展至固定9组300份真实CSI，Linux主机及实板
   均与Windows NumPy参考float32张量逐位一致，幅度及相位标量/周期最大误差0，实板与主机哈希也全相同。
3. 门检使用幅度atol/rtol=1e-6、相位周期最大≤1e-5 rad，保留标量绝对差；真实相位标量差>1e-5 rad须讨论。
   人工±π降为非阻断诊断，周期最大2.333111/2.693437 rad仍失败，不宣称普遍等价或边界通过。
4. 魔数错误、截断、尾随数据和NaN输入在主机/板端均拒绝。
5. 300份实际CSI在Lite预处理median=5.781265ms、P95=5.8595ms；不包括收包、推理、绘制、编码。

## 构建与测试

源码可用CMake构建，交叉编译参数：`-DCMAKE_CXX_COMPILER=aarch64-linux-gnu-g++`。
数值测试使用实际记录的GCC9.4、`-O2 -ffp-contract=off`；后者防止浮点融合影响对照。

```text
pose_preprocess_check --self-test
pose_preprocess_check input.csi output.f32
```

Windows验证Conda环境位于项目`.local/pose-v1-conda`（）；Python3.10.21、NumPy2.2.5、
h5py3.16.0、PyWavelets1.8.0。不是训练环境，也不是板端Python依赖。
精确包锁定、执行证据及后续条件见 `../../tools/pose-v1/`。

## 后续条件

- 运行身份及预处理门检已通过，接下来讨论SDK初始化/混合推理门检，核对HDMI时序；屏幕尚未连接。
- 任何启动修改、位流替换、依赖安装、模型修正或新增FPGA工程先讨论。人工边界保留非阻断失败记录。
- 然后实现并测试混合推理、接收服务、有限队列、骨架渲染、HDMI、VPU/live555 RTSP和长期验收。
- 不使用全CPU或电脑推理代替正式NPU验收，也不把预制预测动画作为实时结果。

本阶段结果见[RESULTS-300.md](../../tools/pose-v1/RESULTS-300.md)，旧证据保留为历史状态。

## 2026-10-05：独立推理门检源码交付

新增`src/inference_check.cpp`，Icraft SDK目标默认关闭，原预处理源码及已验收二进制未改。
开启`POSE_BUILD_ICRAFT_CHECK`后构建独立检查器；`POSE_ENABLE_ZG330=OFF`可构建Windows Host参考。
四种模式：inspect只检查图、probe初始化并记录版本、host执行optimized参考图、mixed执行ZG＋Host完整图。
硬件模式必须显式给`--allow-device-init`，无reset/check/视频输出或自动回退；初始推理仅允许原三份固定真实窗口。
Host可读取固定参考张量，mixed必须在PS从原CSI执行预处理。完整候选、后端记录及耗时输出用于后续核验。

**本次只是源码及命令交付，尚未编译、运行或数值验收。** 编译、模型及软件操作人工执行。
详见[逐条执行说明](../../tools/pose-v1/INFERENCE-COMMANDS.md)及[HDMI静态审查](../../tools/pose-v1/HDMI-STATIC-AUDIT.md)。

</details>
