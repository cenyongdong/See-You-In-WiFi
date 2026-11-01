# 真实骨架编码故障修正与重复验证（2026-10-07）

阶段恢复后已恢复视频任务。V2-A现已完成：27份已验收ARM画面组成54帧文件，两次独立VPU上下文均完整编码；主机解码、来源与关节可见性检查通过。HDMI目标仍为1920×1080@60，尚未改变硬件时序。

## 故障定位与最小修正

r2保持原数据与配置，仅增加QUERYBUF/QBUF/DQBUF、cookie/offset、Host复制、所有权与poll取证。仍触发MMU ABORT，提交8/归还2；Host复制全部一致，没有提前重用或buffer ERROR。驱动RAM日志记录PC0x1888、FAR0、SDMA master5、FAULT0x6、FADDR0x20600000。这些地址不能单独证明空指针、CPU物理地址或具体页表错误。

本机厂商`pipeline/vpu/vpu.h`的Buffer保留QUERYBUF描述并用于QBUF；原新接口重建plane时把mem_offset清零。r5仅保存每plane的opaque MMAP cookie，并在QBUF中保留该值，不推断物理地址。六缓冲区、容量、NV12/H264多平面、色彩、码率、profile、逐行复制、所有权与停止条件保持。相对于r2的完整[源码差异](evidence/video-descriptor-20261007-r5/r2-to-r5-source.diff)已保存。

这是当前板端/固件组合的兼容修正，有两次实测支持；没有驱动源码或页表ABI，不能宣称所有V4L2驱动都需要该字段、或已证明固件内部全部根因。没有重置、换BOOT/固件、扩大缓冲区或修改相机MMU。

r3试用单平面CAPTURE在色彩门检失败；调度失误导致随后encode入口也被调用，但同样在分配/STREAMON之前拒绝，完整记录保留。r4补EXT_PIX_FORMAT magic后仍拒绝，未编码。两者未放宽色彩或纳入正式实现，当前保留原CAPTURE_MPLANE。

## 实测与独立核验

- GCC9.4 AArch64 PIE，程序01965fa28f15b94893eebc8a3f540699454ef0623664cb0888b6b7933aef23d3，58728字节，无warning/Icraft依赖；三源码与构建副本、六载荷包及清单一致。
- 输入74649600字节，SHA256 5da0b23d093eae65c9a3bd6cbcf8bceb86782ce38c6eacd0faae2189b13b6216，与失败r1/r2相同。27个离散CSI窗口，每幅显示两帧；不是连续动作录像或新模型推理。
- 协商、首次编码、独立上下文重复均exit0/stderr空/dmesg前后相同；BOOT、SDK与三库身份通过。
- 每次54提交/54归还、56 capture chunks（含参数集和空LAST），115次QBUF描述/所有权核验，54次Host复制正确，正常STOP→LAST→两队列STREAMOFF。
- 每次H264179648字节，两次SHA256均d51c98b183b4b0ff5ff7142403c1fa1c8146a5be4be71672afcd17e9d38eaac3。MP4180680字节，传输SHA256 10702f94fc3f5dd3473585cf0c0a5088a102fb75799770a8b918af2bc7fe0aa0。
- 主机既有OpenCV完整解码54帧，1280×720/10fps/5.4秒，ID0..53与全部来源正确，27份姿态不同，756次关节邻域可见性检查通过。最近红色像素最大距离4.12px；这是渲染可见性检查，不是3D精度验收。RGB lossy比较均绝对误差1.433/PSNR40.87dB，不作色彩标定。
- 实际Annex B为1 SPS/1 PPS/2 IDR NAL/52非IDR NAL；IDR capture PTS为[0, 3000000]微秒。参数集首chunk31字节，不能套参考固定24/8长度，也不能把56个chunk当56图像。RTSP仍需AU边界与拥有字节的接口。

[动态MP4](evidence/video-descriptor-20261007-r5/encode/results/review.mp4) · [联系图](evidence/video-descriptor-20261007-r5/host-review/contact-sheet.png) · [完整核验](evidence/video-descriptor-20261007-r5/completion-review.json) · [下一检查点](evidence/video-descriptor-20261007-r5/next-checkpoint.json)

## HDMI与下一步

表示资料全部在本地；已核对发布包、参考代码/RTL、DT/clock/fb/DRM/udma和download.bit候选路径。BOOT/DTB身份对应不等于寄存器映射对应；参考宽高只控制缓冲区、RTL像素时钟来自外部cam_clk，未建立当前Lite时序/scanout归属/停止协议。三个download.bit/BOOT候选路径本次查询均不存在，该事实也不能反推实际FPGA加载来源。未写HDMI寄存器、分配扫描缓冲区、修改时序或执行实屏。

继续按[NEXT-VIDEO-PLAN](NEXT-VIDEO-PLAN-20261007.md)：先审查动态样片，再隔离RTSP；已有live555参考可用于接口核查，但其固定SPS/PPS长度与把返回buffer指针重新入队后的队列引用不能照搬。先复制到有界owned AU，再归还VPU缓冲区；使用capture PTS和实际NAL，验证加入/断开重连/60秒退出。色彩VUI尚未确认，不把G_FMT601有限当码流已显式声明。HDMI配套缺失不阻断RTSP准备。

本轮没有RTSP播放、推理/编码合并、双路或整机5Hz/30分钟验收。原推理、数学、SDK、BOOT与帧完成协议保持；全部测试已退出，SSH/SFTP关闭，无后台任务。旧暂停和失败检查点按历史保存，不覆盖。
