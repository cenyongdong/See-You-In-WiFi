# 正式核心接口与开发指南

**版本定位（2026-10-29）：** 本页保留早期工程、兼容接口或对应批次结果，文中的“当前”只指该版本。现行 180-query 主链在[主工程](../pose180_pipeline/README.md)，运行及验收范围见[最终进度](../../PROJECT-PROGRESS.md)；旧命令不作为最新部署入口。

2026-10-17 HDMI新增接口（旧演示尚未链接）：`pose::hdmi::canvas(rgb720)`返回拥有的1920×1080 RGB565LE字节；`pose::hdmi::Output(device,evidence)`由SDK所属主线程创建并持有设备引用与两块UDMA帧。`show(pixels,id)`完整写入空闲帧并等候地址/ID采纳后返回，`observe()`核对硬件故障，`close()`取得新响应和对应停止tag、idle／在途清零后显式释放。析构不能安全停止时保留缓冲并退出进程，不能假装完成释放。设备必须比Output活得更久；禁止独立进程分配重叠的SDK池或直接解引用BOTH地址。完整接口见[hdmi_output.hpp](display/hdmi_output.hpp)，范围及失败结果见[HDMI应用](../hdmi_demo/README.md)。

本页以当前 `software/demo/CMakeLists.txt` 实际链接的实现为准。先读[核心导读](README.md)，再从[应用入口](../demo/board/main.cpp)沿数据流阅读；接口签名以对应头文件为准。命名空间中的 `pose_v1`、`cpu_candidate`、`mixed_candidate` 是保留的接口名，不表示应继续修改历史目录。

## 模块关系与接入入口

| 数据流 | 实现目录 | 推荐接入方式 |
|---|---|---|
| MAT → 原始 CSI 记录 | `input` | Python `load_mat` / `encode_window`，主机编排使用 `demo/host/replay.py` |
| TCP → 完整拥有值窗口 | `input` | `pose_v1::transport::Receiver`，向主线程返回 `Item` |
| 窗口 → 预处理 → 完整模型输出 | `input`、`inference` | 应用使用 `wifi_demo::Engine`；核心接口为 `pose_v1::application::Engine` |
| 输出 → 姿态 IPC → NV12 | `display` | 应用使用 `wifi_demo::Video`；显示子进程接口为 `pose::display::Process` |
| NV12 → VPU → 拥有压缩包 | `video` | 编码线程调用 `pose::video::encodeResident` |
| 压缩包 → H264 AU → RTSP | `stream` | `AccessUnitAssembler`、`AccessUnitChannel`、`serveGuardedAccessUnits` |
| 原值、身份、阶段记录 → 文件 | `diagnostics` | 由推理适配统一配置，应用显式 `save_evidence`，不由视频线程调用 |

主机不预处理、不推理、不注入 GT。显示和流媒体不持有 Engine 或 SDK 张量；模块之间交接完整拥有值，不能借用 SDK 地址或驱动缓冲区的生命周期。

## 输入接口

| 文件与命名空间 | 接口 | 输入与输出、限制 |
|---|---|---|
| [csi_io.py](input/csi_io.py) | `load_mat(path)` | 读取 MAT `csi_out`，检查原 MAT 形状与 real/imag 字段，转换为固定形状 complex128；有限性在 encode_window 校验，依赖 NumPy/h5py |
| 同上 | `encode_window(csi, frame_id, source_time_ns=0)` | 返回拥有的 `bytes`，32 字节头部加 86400 字节负载，共 86432 字节；原始复数按实部/虚部 float64 编码，不做预处理 |
| [preprocess.hpp](input/preprocess.hpp)，`pose_v1` | `RawCsi`、`Window`、`Tokens` | `RawCsi` 为 5400 个 `complex<double>`，逻辑形状 `[3,3,30,20]`；`Window` 带帧号与源时间；`Tokens` 为 10800 个 FP32，模型形状 `[1,180,60]` |
| 同上 | `raw_index(r,a,n,t)` | 固定原始数组索引；调用方必须满足接收器、天线、子载波、时间的范围，函数本身不做范围检查 |
| 同上 | `preprocess(csi)` | 返回拥有的 `Tokens`；布局为接收器、天线、时间、30 幅度与 30 校正相位；保留 unwrap、线性校正与复指数重建的表达式和运算顺序 |
| 同上 | `read_window(filename)` / `write_tokens(filename,tokens)` | 完整记录文件 → `Window`；将实际 FP32 输入写入文件。文件错误或非法记录抛异常 |
| [tcp_receiver.hpp](input/tcp_receiver.hpp)，`pose_v1::transport` | `decode_record(bytes)` | 只接受完整固定长度记录，检查头部和负载，返回拥有的 `Window`；TCP 分包边界不是记录边界 |
| 同上 | `LatestSlot::push/pop/clear/close/finished` | 线程安全单个待处理槽；只替换尚未消费的窗口，`pop(wait)` 按值转移所有权，超时返回空。已经消费的窗口不受覆盖影响 |
| 同上 | `Receiver(address,port,idle_ms,max_sessions)` | 持有监听/连接描述符和接收线程；重组并校验完整记录。`pop(wait)` 返回可选 `Item{window,session,sequence,arrived}` |
| 同上 | `check/errors/stats/port/stop/stopAndStats/finished` | `check()` 向调用线程传播接收错误；`stats()` 给出接收、拒绝、覆盖等计数；`stop()` 唤醒并结束接收线程后释放描述符。不能以发送成功代替接收确认 |

PIWCSI1 头部契约为小端 `<8sIIQQ>`：magic、版本 1、负载长度、frame_id、source_time_ns。主机 `source_time_ns` 与板端单调时钟不直接相减计算延迟。

## 推理接口

| 文件与命名空间 | 接口 | 责任与调用约束 |
|---|---|---|
| [application_core.hpp](inference/application_core.hpp)，`pose_v1::application` | `Config` | 指定固定 graph/raw、新 evidence 目录、设备许可、诊断/计时范围。配置选项不代替阶段授权 |
| 同上 | `Engine(Config)` / 析构 | 每进程唯一实例，由主线程创建、串行调用和销毁；构造检查模型、融合、SDK/设备身份并初始化 Session。异常后永久停止，不能复用失败实例或自动重建 |
| 同上 | `process_window(Window)` | 返回拥有的 `Result`：原帧标识、调用号、10800 FP32 输入、100 分数、4200 姿态值、选中 42 坐标及分阶段统计。全部模型输出必须保留，再做有限性/严格参考核验 |
| 同上 | `process_window_checked(Window,case_name,expected_input)` | 在原处理路径上启用固定输入参考核验；不能用参考值替换实际计算或晚源值修补坏值 |
| 同上 | `save_evidence()` / `init_ms()` | 显式保存已经拥有的运行证据；初始化计时查询不访问/复位硬件。析构不替代显式保存 |
| [host_cpu_adapter.hpp](inference/host_cpu_adapter.hpp)，`pose_v1::cpu_candidate` | `validate_spec(op)` | 检查固定 FP32 形状、轴、布局及全有效分布，未知规格用 `Rejection` 拒绝；`Rejection::code()` 提供原错误分类 |
| 同上 | `register_missing(graph,backend)` / `forward(op,inputs,outputs)` | 注册缺失 CPU 算子并执行批准数学核；不覆盖已有/部分注册，不扩大算子规格。保留已有 Gather；Matmul 仍分配 NPU |
| [mixed_bridge.hpp](inference/mixed_bridge.hpp)，`pose_v1::mixed_candidate`；实现 [read_input_bridge.cpp](inference/read_input_bridge.cpp) | `configure`、`set_frame`、`register_ops`、`forward`、`tensor_info` | 内部 SDK 桥：记录上下文、注册回调、检查张量、设备输入 → Host 拥有暂存 → CPU 数学 → 原输出写回。由 Engine 配置，业务代码不自行追加读回或改变回调次序 |
| [input_read_contract.hpp](inference/input_read_contract.hpp)，`pose::input_read` | `HostView` / `boundedRead(destination,bytes,reader)` | 目标必须是拥有的 Host 分配；先检查 offset/capacity，再将有效目的地址交给 reader，原读取错误继续传播 |
| [input_read_sdk.hpp](inference/input_read_sdk.hpp)，同命名空间 | `intoHost(source,destination)` | 源/目标 dtype 相同、存储范围合法；目标为 Host CPTR，源/目标不能同 chunk。仅使用公开 `Tensor::read` 读入目标，不将 ADDR/BOTH 当普通指针 |
| [mixed_fusion_baseline.hpp](inference/mixed_fusion_baseline.hpp) | `host_ids`、`members`、`sync` | 固定模型融合成员与完成阈值映射；是基线数据，不能作为可自由调整的调度参数 |
| [lazy_runtime_validation.hpp](inference/lazy_runtime_validation.hpp)，`pose_v1::runtime_detail` | 内部校验辅助函数 | 检查固定模型/张量/分布/融合/输出；属于实现细节，不作为新模块的公开接入接口 |

直接应用开发优先使用 [demo_engine.hpp](../demo/board/demo_engine.hpp) 的 `wifi_demo::Engine(model,freshEvidence)`，由其统一配置首次 Host 坏值、两轮源读取、阶段、计数与身份记录。只改核心 Engine 而漏掉适配层配置，会失去要求的诊断契约。

## 诊断接口

诊断模块不是独立恢复或同步机制。它们由主线程及其串行 SDK Host 回调使用；配置一次，按原采样位置记录，保留所有上限。错误处理顺序是保存首次原值和拥有快照 → 有界两轮源读取 → 继续传播原计算错误。

| 文件与命名空间 | 接口与用途 | 所有权与错误 |
|---|---|---|
| [host_failure_evidence.hpp](diagnostics/host_failure_evidence.hpp)，`pose::failure_evidence` | `Blob`、`configure/enabled/save/noteCaptureError`；保存首次输入字节、形状与布局 | Blob 拥有字节，模块无 SDK/设备依赖；聚合上限 1 MiB；诊断错误另记，不替代原计算错误 |
| [failure_source_readback.hpp](diagnostics/failure_source_readback.hpp)，`pose::source_diagnostic` | `configure/capture`；原 Host 错误保存后校验源身份、准备拥有目标，再执行两轮公开 SDK read | `capture` 只在错误路径使用，遵守原设备许可与字节预算；不推进模型，不追加正常路径读回 |
| [host_stage_observation.hpp](diagnostics/host_stage_observation.hpp)，`pose::stage_observation` | `Completion/waitFresh`、`Info`、`Call::afterCopy/validate/saveFailure`、`configure/recordCompletion/recordSyncFailure/saveMetadata/failureRoot` | 有界计数观察、搬运时间和 post-copy 字节；`Call` 拥有快照。ready/count 不是底层硬件写完成的独立证明 |
| [invocation_evidence.hpp](diagnostics/invocation_evidence.hpp)，`pose::invocation_evidence` | `Frame::begin/record/save/bytes/inputs`；`Task/flush` | Frame 固定创建线程，拥有当次输入字节；`flush` 尝试全部保存任务，保存错误不掩盖已存在原错误 |
| [producer_count_observation.hpp](diagnostics/producer_count_observation.hpp)，`pose::producer_count` | `Point/Source`、`Recorder::sample/save/size`、模块级 `configure/sample/save` | 在原 BeforeWait/AfterWait/BeforeCopy/AfterCopy 点记录生产者计数；单线程记录器，元数据不作为新同步步骤 |
| [tensor_identity_observation.hpp](diagnostics/tensor_identity_observation.hpp)，`pose::tensor_identity` | `Storage/Pair`、`Recorder::sample/save`、模块级 `configure/enabled/sample/save` | 记录张量/region/chunk/device/address/offset/capacity 及原前后配对；地址只作证据，不能解引用 |
| [content_diagnostic.hpp](diagnostics/content_diagnostic.hpp)，`pose_v1::content_diagnostic` | `configure/enabled/set_context/capture` | 仅允许已驻留 Host CPTR FP32，捕获拥有字节并记录来源；拒绝设备读、wait/copyTo 和非法边界 |
| [application_clock.hpp](diagnostics/application_clock.hpp)，`pose_v1::forward_clock` | `start/record/Span/save` | 有界单调时钟诊断；采样点、线程保护、8192 记录上限保持。不能用诊断模式代替吞吐验收 |
| [bounded_load_contract.hpp](diagnostics/bounded_load_contract.hpp)，`pose::bounded_load` | `fixtureIndex/keepReference` 及固定预算 | 保留历史有界工作包契约，演示不据此自动启动 103 输入测试；旧 DATA 排查仍暂停 |

## 显示接口

| 文件与命名空间 | 接口 | 契约 |
|---|---|---|
| [display_protocol.hpp](display/display_protocol.hpp)，`pose::display` | `Pose/validate/Cancel` | Pose 拥有完整 100 分数和 4200 姿态值，以及 frame/invocation/publishedNs；validate 拒绝非法输入；Cancel 供有界 IPC 中止 |
| 同上，`wire` | `Kind/Header/Bytes/encode/decode/read/write/readHeader/writeHeader/now` | 64 字节头部，Ready/Render/Image/Stop/Stopped；精确流读写，不靠一次 read/write 完成；只允许一个在途请求 |
| [display_process.hpp](display/display_process.hpp)，`pose::display` | `Process(executable,evidence)`、`render/finish/pid`、`Image` | 在父进程设备和工作线程之前启动 SDK 无关 worker；render 同步返回拥有 NV12 和计时字段；finish 完成 STOP/ack/waitpid，不自动重启 |
| [display_queue.hpp](display/display_queue.hpp)，`pose::display` | `Queue::publish/next/close/fail/stats` | 最多两个待处理不可变 Pose；next 合并到最新待处理值并按共享拥有值返回；关闭时排出已有值，fail 唤醒并抛原错误。覆盖/coalesced 要记录 |
| [skeleton_render.hpp](display/skeleton_render.hpp)，`pose_v1::render` | `Status/Frame/project/draw` | 固定 1280×720 正交投影及 14 骨架关节；Status 区分 Result/NoInput/Stopped，Frame 拥有 RGB 和投影/选中坐标；不平滑、不 auto-fit、不改模型输出 |
| 同上 | `rgb565_le(rgb,w,h)` / `yuv420sp(rgb,w,h,nv21)` | 返回拥有像素数据；YUV 使用固定 BT.601 limited-range 整数转换和 2×2 色度平均；nv21 选择 UV/VU 排列 |
| [display_worker.cpp](display/display_worker.cpp) | 子进程可执行入口 | 只链接协议和渲染，不链接 SDK；固定信用 IPC 接收 Pose，绘制并返回 Image，结束时响应 STOP |

NoInput 和重复最新画面只是预览状态，不计新姿态或推理吞吐。

## 视频与流媒体接口

| 文件与命名空间 | 接口 | 线程、所有权与限制 |
|---|---|---|
| [vpu_pipeline_encoder.hpp](video/vpu_pipeline_encoder.hpp)，`pose::video` | `OwnedFrame/OwnedPacket/PacketConsumer/validateOwnedFrame` | 帧拥有 1382400 字节 NV12 和来源/调用/生成时刻/编码号；包拥有压缩字节、PTS/flags/sequence。validate 在复制与 QBUF 前检查帧规格 |
| [resident_frame_queue.hpp](video/resident_frame_queue.hpp)，`pose::video` | `ResidentFrameQueue::publish/pop/popLatest/fail/stop/check/stopped/stats` | 最多两个已完成不可变帧；绘图线程发布，编码线程消费并持有自己的最新帧用于重复采样；stop 不销毁已拥有帧，fail 在后续访问时传播 |
| [vpu_resident_encoder.hpp](video/vpu_resident_encoder.hpp)，`pose::video`；实现 [timed_resident_encoder.cpp](video/timed_resident_encoder.cpp) | `ResidentOptions/ResidentSample/ResidentProducer/encodeResident` | 编码线程唯一打开和操作 VPU；producer 接收编码号和采样时间，返回帧或 nullopt 请求正常 drain；consumer 收到已复制的拥有包；第一次实际非空 capture 后回调一次 |
| [vpu_encoder.hpp](video/vpu_encoder.hpp)，`pose::video` | `EncodeResult` | submitted/returned/encodedBytes/drained 记录实际编码结果；不能以文件存在代替正常 drain/LAST |
| [video_frame_marker.hpp](video/video_frame_marker.hpp)，`pose::validation` | `markEncodedFrame(nv12,id)` | 在固定图像区域标记 0..999 编码 ID，用于来源核验，不改姿态或投影 |
| [h264_access_unit.hpp](stream/h264_access_unit.hpp)，`pose::stream` | `AccessUnit/AccessUnitAssembler::consume/pictures` | 从 MVX 完整 Annex B 包提取拥有的 SPS/PPS/slice 和 PTS/IDR；只支持已验单图单 slice、稳定参数集、无 B 帧重排，不是通用 H264 解析器 |
| [access_unit_channel.hpp](stream/access_unit_channel.hpp)，`pose::stream` | `AccessUnitChannel::publish/take/close/fail/notificationFd/highWater`、`Batch` | 单生产者、单事件循环消费者，容量 8；self-pipe 唤醒网络线程，take 转移拥有 AU；溢出停止，不随意丢 P 帧。channel 必须活到网络线程 join 后 |
| [online_rtsp.hpp](stream/online_rtsp.hpp)，`pose::stream` | `RtspOptions` | 默认 port8554/maximumSeconds90/maximumClients2；调用方和 runner 共同约束预算，不修改系统网络参数 |
| [guarded_rtsp.hpp](stream/guarded_rtsp.hpp)，`pose::stream`；实现 [timed_guarded_rtsp.cpp](stream/timed_guarded_rtsp.cpp) | `GuardedRtspOptions/serveGuardedAccessUnits(channel,options,evidence)` | 同步运行在唯一网络线程，拥有 live555 对象；每客户端受限发送缓冲，RTP 错误传播到主链；新证据目录，结束时释放服务对象和端口 |

VPU QBUF 后缓冲归驱动，DQBUF 后归应用；压缩包必须在 capture 重排队前复制。QUERYBUF cookie 保留，不能替换成猜测的物理地址。正常路径提交 drain 并确认 LAST，异常路径 abort STREAMOFF；两者不能混记通过。

### 保留声明与当前目标的边界

以下声明为迁移时保留的旧接口，当前 `demo_runtime/pose_demo` 没有提供其定义：

| 保留声明 | 所在头文件 | 当前应使用的实现 |
|---|---|---|
| `encodeNv12File` | `video/vpu_encoder.hpp` | `encodeResident` |
| `encodeNv12Producer` | `video/vpu_pipeline_encoder.hpp` | `encodeResident` |
| `serveOwnedAccessUnits` | `stream/online_rtsp.hpp` | `serveGuardedAccessUnits` |
| `mixed_host_check` | `inference/mixed_bridge.hpp` | 原检查器是独立测试；正式应用使用 Engine |

这些头文件仍为正式实现提供类型，包含头文件不表示所有历史声明都在当前目标可链接。新增调用上述保留声明会缺少定义；本轮用实际 CMake 来源及 ARM 符号表核对，不为补齐旧入口混编历史 `.cpp`。若需扩展能力，应先明确需求，再在当前核心设计独立接口和相应验证。

## 应用编排与主机控制

| 入口 | 接口/流程 | 接入说明 |
|---|---|---|
| [demo_options.hpp](../demo/board/demo_options.hpp) | `Options/parseOptions(argc,argv)` | 返回拥有参数；不访问设备，保持默认值、校验顺序和原错误文本 |
| [demo_engine.hpp](../demo/board/demo_engine.hpp) | `wifi_demo::Engine::process_window/save_evidence` | 主线程拥有核心 Engine 和全部诊断配置；应用不跨越该适配层向视频模块传 SDK 对象 |
| [demo_video.hpp](../demo/board/demo_video.hpp) | `Video::waitCapture/beginInitialization/initialized/publish/check/abort/finish` | 拥有绘图、编码、网络工作线程；引用由调用方拥有的显示子进程；finish 必须完成全部 join，Engine 和显示对象在此之前存活 |
| [demo_results.hpp](../demo/board/demo_results.hpp) | `Results::add/save/size` | 按值拥有实际 Window 与 Result，记录到达/返回时刻，写入新目录；不借用 Engine 输出缓冲 |
| [main.cpp](../demo/board/main.cpp) | 应用生命周期 | 参数 → 新目录 → 显示子进程 → VPU 首 capture → 主线程 Engine → TCP → 消费/保存拥有结果 → 发布姿态 |
| [host/replay.py](../demo/host/replay.py) | `prepare(data,output,frames,sequence)` / `send(host,port,hz,catalog,payloads,out,viewer)` | prepare 自然序读取并保存源/负载哈希；send 等真实解码就绪后建立一次会话，绝对时隙发送。已接受会话不重连、不重发、迟到不突发追帧 |
| [host/run.py](../demo/host/run.py) | CLI `main()` | 编排准备、独立播放器、发送与回收；`--prepare-only` 只做输入准备，可在无板端时检查导入与原始字节路径 |
| [host/viewer.py](../demo/host/viewer.py) | CLI `main()` | 已有 OpenCV/FFmpeg 环境实际 RTSP/TCP 解码，保存帧指纹、截图、计数；GUI 和 headless 范围分别报告 |

正常结束顺序：停输入生产 → 绘图完成 → VPU drain/LAST → AU close → 网络对象回收 → 全部 workers join → 结果及诊断保存 → Engine 销毁。异常保留最早错误、停输入、Video abort、回收子进程；保存失败不能覆盖原计算错误。

## 构建和后续修改

生产入口是[演示 CMake](../demo/CMakeLists.txt)，[Regression.cmake](../demo/Regression.cmake)仅挂接冻结测试。通过 [build.py](../demo/build.py) / [build_support.py](../demo/build_support.py)核验当前锁、SDK 与厂商库并导出平铺别名；include 使用导出别名，不能仅增加原目录路径绕开锁。

- 核心功能在本目录六个功能子目录维护，应用编排在 `software/demo`。`software/pose_v1` 和历史工具保持冻结；测试只做必要链接/路径调整。
- 接口变更同时维护本页与头文件契约，注明形状、所有权、线程和错误传播；新辅助函数仅模块内部使用，不包含其他功能 `.cpp`，不访问私有状态或重复算法。
- 四空格、同行左花括号、运算符空格、逻辑步骤空行与中文目的注释；新代码对齐当前核心和编排的风格。整理数值/SDK/锁/计时段前确认运算顺序、变量生命周期和采样位置。
- 增改源码时更新当前锁并独立记录前后身份；迁移清单、旧锁和已完成证据不回写。验证使用新构建、新运行和新证据目录，失败后停止，不以旧程序覆盖新失败。
- 固定数学、CPU/Gather 注册、Matmul NPU 分配、`reset(1)`、模型/RAW/SDK/BOOT、协议、`-ffp-contract=off` 与字节/时间预算保持；涉及变更先讨论。

本页描述当前实现契约，不构成长期、严格 5Hz、永久首启动、HDMI 或旧 DATA 根因修复验收。检查范围与实际结果见本轮记录（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/core-check-20261014-r1/README.md`）。
