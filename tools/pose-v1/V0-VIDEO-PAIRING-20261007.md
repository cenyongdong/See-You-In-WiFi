# V0视频配套核对：已确认部分与待确认接口

最新授权：已完成编码样片审查，允许HDMI测试，解除下述暂停；[下一视频计划](NEXT-VIDEO-PLAN-20261007.md)与[来源哈希/检查点](evidence/video-next-plan-20261007.json)更新。参考默认1080p仅控制帧缓存大小/提交地址，仍需当前BOOT的clock/scanout/换帧配套核验；没有新硬件时序切换。

最新补充：下文是此前查询阶段记录。现已实测720p NV12两plane、H264单plane、明确stride/容量及30帧独立文件编码/主机解码，[结果](VPU-RESULTS-20261007.md)。HDMI已连接DELL E2421HN但现场反馈时序不支持，目标更新1080p60并暂停测试，尚未切换硬件时序；旧无显示器/720p目标按历史理解。

本轮按已批准路线查询sysfs/device-tree/proc及V4L2能力。V4L2只open/close、QUERYCAP、ENUM_FMT、ENUM_FRAMESIZES；没有S_FMT、REQBUFS、QBUF、STREAMON、mmap或SDK Device::Open，也未写候选寄存器、更换BOOT或启动相机示例。人工确认HDMI显示器尚未连接。

## 已确认的运行事实

| 项目 | 本轮依据 | 结论边界 |
| --- | --- | --- |
| 视频节点 | `/dev/video0`，driver `mvx`，card `Linlon Video device`，device_caps `0x520c003` | 存在M2M能力，不表示已成功编码 |
| 原始图像输入 | type10 `VIDEO_OUTPUT_MPLANE`枚举NV12/NV21等 | 未请求格式，planes/stride/sizeimage/色彩空间均未协商 |
| 编码流输出 | type9 `VIDEO_CAPTURE_MPLANE`枚举H264/M264/AVC1/HEVC等 | 单次枚举不能证明任意profile/码率/帧率可用 |
| 单平面队列 | type1/2枚举均返回无支持格式 | 不直接采用参考actor默认的单平面CAPTURE |
| 720p候选尺寸 | NV12/NV21输入、H264输出报告2..8192、步进2，1280×720符合枚举范围 | 仍须S_FMT/G_FMT返回及实际编码通过；不扩大为8192视频可正常编码 |
| 设备树 | `amba-apu@0/mve@f0020000`，compatible `arm china,linlon-v5`，status okay，clock-name `clk_vpu` | 只记录系统公开信息，不直接读写该地址 |
| u-dma-buf | 节点size128MiB，sysfs可见 | 未用于渲染设备输出，未证明HDMI扫描/缓存一致性 |
| framebuffer | `/proc/fb`为空 | 无已注册fbdev路径，不能据此写/dev/fb0或声称HDMI没有独立自定义路径 |
| PS时钟 | clk_summary可读 | 未建立PL HDMI实际像素时钟映射，不用PS clock树替代74.25MHz证明 |
| 内核状态 | 查询前后dmesg完全相同，FPGAoperating | 仅查询通过，不是视频配置/流测试 |

完整[查询](evidence/render-20261007-r1/video-query/capabilities.json)、[sysfs/DT](evidence/render-20261007-r1/video-query/sysfs.json)及[独立复核](evidence/render-20261007-r1/video-query.review.json)已保存。

## 当前参考代码不能直接采用的内容

参考VPU actor默认1920×1080@60、NV21、HEVC、OUTPUT_MPLANE输入＋单平面CAPTURE输出。本轮真实设备只枚举多平面队列，因此首版H.264编码应根据设备实际返回使用两端MPLANE，并核验driver返回的num_planes、bytesperline、sizeimage；MPLANE不等于图像一定分成多个独立内存plane。

参考encoder有硬编码输入planes等行为；不能把它作为NV12/NV21内存布局证明。参考RTSP首包按固定24/8字节SPS/PPS取切片，也不适用于未验证的实际H264输出。下一实现要按NAL/长度边界解析，并明确Annex-B与AVC1格式，不靠固定偏移。

不能为运行相机示例而调用其`mmuModeSwitch(false)`或额外Device::Open初始化：首版画面来自PS骨架帧，原NPU内存/同步模式保持。

## CPU帧缓存接口已准备

Renderer生成1280×720 RGB24（2,764,800字节）；已验证转换为RGB565小端（1,843,200字节）、NV12及NV21（各1,382,400字节）。YUV按BT.601有限范围、2×2 RGB箱式平均、连续Y＋交织UV/VU、stride1280定义，像素算法有独立NumPy逐字节参考。

这些是CPU逻辑缓冲区的明确规格，不是驱动已经接受的DMA或扫描缓冲区：

1. 后续对新VPU上下文请求1280×720、H264和所选原始格式，显式请求并检查返回的色彩空间/量化/色度约定；若返回不同色彩矩阵，按新配置调整转换并重新核验。
2. 读取实际plane数量、stride/sizeimage，并在驱动管理的MMAP/队列缓冲区内逐行复制/填充；不把连续CPU字节数当驱动容量，不实现零拷贝。
3. 有限合成画面编码，逐帧记录PTS/源frame_id、bytesused、错误及结束/清理；先生成可解码H264文件，再RTSP，不与NPU/HDMI竞争初始化。
4. 队列/驱动中断后保存失败并停止，不自动复位或改BOOT。只有编码、NAL、PC解码通过，才将真实骨架帧接入。

这四项是下一V2候选门检，不是本轮已执行。现有系统头文件可用于实现；不要求安装新依赖或编译整套参考相机应用。

## HDMI仍需的配套依据

参考包README标记AI Mate25122301，但原参考RTL对应关系、1080p默认值与实际BOOT的720p配置仍未建立。当前无fbdev、无显示器，不使用参考0x40080054地址或0x094..0x0B0时序寄存器做猜测性配置。

进入V1前需匹配当前BOOT/bit发布说明或工程的像素/串行时钟、720p时序、RGB565字节序/stride、地址更新与换帧完成机制，并连接支持720p60的显示器进行OSD/色条/换帧观察。仅把软件宽高改为1280×720或CPU图片正确，都不能宣称HDMI720p60成立。

VPU可独立准备，不以HDMI未连为由停止已具备依据的CPU与编码准备；但双路/整机/30分钟验收仍须实际显示与播放。
