# 独立RTSP传输、重连与直接播放器结果（2026-10-07）

已审查动态骨架视频，要求继续推进。V2-B首批传输/解码完成：复用已验收VPU输出的owned NAL与实际capture PTS；两RTSP会话各100帧，另一次直接OpenCV/FFmpeg100帧。尚未实际推理/编码并发或在线VPU→RTSP接入。

## 工程与身份

新增隔离`rtsp_replay_check.cpp`、构建/包/有限运行、标准库RTSP/RTP审计和直接播放器脚本。程序454d21c24831f88a513747710540294914b6e2d4fddc8ed2993420bc28758fb2，3882104字节，GCC9.4 AArch64 PIE，无Icraft或动态live555/SSL依赖。厂商live555版本2024.11.28，189份头/静态库逐项哈希与发布包保持；没有安装新依赖。初次r1缺配套OpenSSL头路径失败保留；r2使用同包头文件后无warning编译通过。

当前输入是已验收r5的54帧H264，SHA256 d51c98b183b4b0ff5ff7142403c1fa1c8146a5be4be71672afcd17e9d38eaac3。索引覆盖完整码流，只支持当前每PTS一个first_mb=0 VCL NAL，实际SPS19/PPS4字节，拒绝其他布局，不是通用H264 AU解析器。NAL保存在拥有字节的CPU容器，生命周期覆盖live555；无临时驱动指针、VPU/NPU/HDMI初始化或寄存器写入。

## 首轮异常及修正

r2标准库客户端接收88帧后超时。已收NAL逐字节一致、RTP时基正确，服务仍按60秒退出0，内核保持。代码将会话回收设为10秒，而客户端既未发送RTCP RR，也未发RTSP保活；厂商RTSPServer.hh明确此时会回收会话。保留完整失败，客户端补每3秒GET_PARAMETER，服务二进制/码流/队列策略不变，在新r3目录通过。没有降低数据门检或重跑失败目录。

## 实测门检

- r3服务运行60.000371秒，exit0，所有source归还、端口8554释放、dmesg前后相同，BOOT/SDK/三库保持。
- 初次加入从编码ID30的IDR开始，100帧到ID21；TEARDOWN成功后断开，再次加入从ID0开始100帧到ID45。两个会话各3次GET_PARAMETER200，306/307个RTP及各3个RTCP记录，无RTP序号缺口。
- 实际SDP参数集与源NAL一致；FU-A/单NAL重组的200个VCL全部逐字节对应原编码，顺序按ID模54，RTP步长9000/90kHz，即100ms。循环时递增时间轴，不回退为0；加入等待下一个IDR，不从P帧开始。
- 200帧主机完整解码，ID/来源及每帧BGR像素逐位原r5视频。
- r4-player独立上下文运行60秒、exit0/内核保持/清理完成；现有OpenCV5/FFmpeg直接RTSP-over-TCP解码100帧，全部顺序和像素逐位r5，不依赖自定义客户端。
- stderr不为空：r3两行、r4一行厂商RTCP构造诊断`CJN-Trace>>...maxRTCPPacketSize=4000000`，已在提供的libliveMedia.a中确认该字符串。保留原文，不当作空stderr或隐藏错误。
- 首会话录制码流重封装MP4，传输SHA与100帧解码像素核验通过。MP4仅离线重建10fps时间轴，实时RTP时间戳另由网络记录证明。

[RTSP录制样片](evidence/rtsp-20261007-r3/playback-preview/review.mp4) · [传输/重连核验](evidence/rtsp-20261007-r3/completion-review.json) · [直接播放器核验](evidence/rtsp-20261007-r4-player/completion-review.json) · [新检查点](evidence/rtsp-20261007-r3/next-checkpoint.json)

## 色彩、HDMI与接续

现有FFmpeg trace_headers实际解析SPS：timing_info_present_flag=1（32768/655360），video_signal_type_present_flag=0。因此码流未显式提供色彩矩阵/primaries/transfer；像素一致不替代其他播放器色彩标定。本轮只读核对，未改SPS/VCL或像素；下一实际编码分支需记录有依据的元数据处理。

已核对Engine/result/render/VPU文件接口，准备[F0接入门检](F0-INTEGRATION-PREP-20261007.md)：先实际三帧＋重复的完整输出回归与有限同进程编码，再单Engine/有界画面工作者、实际capture owned AU桥和27帧网络联调。原模型/RAW/SDK/BOOT/CPU数学/reset(1)协议保持，深度优化后置。

HDMI目标1080p60仍缺当前BOOT时序/scanout/安全停止配套，未改时序。此次60秒为有限服务上下文，两个实际会话约10秒各一段，并非60秒连续硬件编码或30分钟系统稳定证明；10fps是预生成文件回放，不作有效姿态10Hz/整机5Hz或端到端性能通过。测试服务、SSH/SFTP均已关闭，无后台任务。
