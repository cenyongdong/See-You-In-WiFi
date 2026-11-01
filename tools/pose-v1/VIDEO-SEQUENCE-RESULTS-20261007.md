# 真实骨架视频与HDMI配套首批：VPU异常停止，HDMI未写入

本轮下一视频计划执行V2-A与V1-A。**真实骨架编码没有通过**：MVX固件报告`V5/V7-H264ENC: MMU ABORT`，已停止并保留部分码流。HDMI只读配套核查已完成当前可获取部分，尚不能确认时钟/时序映射与安全停止扫描协议，因此没有执行显示寄存器写入。原合成30帧编码成功仍作为受限历史基线，不能推广为真实场景编码稳定。

## 已完成的工程与真实输入准备

新增SDK无关、有界文件编码接口`vpu_encoder.hpp/.cpp`、独立`pose_vpu_sequence_check`及构建/准备/运行/主机审查工具。接口固定已协商720p NV12/10fps，frame_count2..60与输入字节数在打开视频设备前核验；每次只持有一个CPU输入帧，驱动MMAP/逐行复制/STOP/LAST/清理策略沿用r4。旧r4程序/源、原推理与渲染实现保持。
FPAI GCC9.4.0构建无warning，AArch64 PIE仅标准运行库；新程序`109e24bd32517f49f86a9f4f131ad2a3e1f070da48dd07c88db901429eef7e8c`。构建副本/三份来源与包身份一致。新包6份载荷，清单LF，新目录无覆盖。

逐份校验已验收ARM27份NV12及元数据的原回传哈希、CSI窗口/源帧号/14个投影坐标；全部27画面不同。每幅保持两编码帧，生成54份74,649,600字节输入，SHA256`5da0b23d093eae65c9a3bd6cbcf8bceb86782ce38c6eacd0faae2189b13b6216`。底部六位编码ID/移动条与实际骨架分离（骨架最大投影Y539.12，诊断区从Y600开始），原姿态和显示几何未改。这是离散窗口回放，不是连续动作录像或本轮新推理。

## 实际故障证据与结论边界

| 项目 | 核验结果 |
| --- | --- |
| 身份/格式 | BOOT/SDK3.39.0/三库一致；协商exit0/stderr空/dmesg相同。NV12两planes/stride1280/Y921600/UV460800，H264一plane2MiB，两端601有限，10fps/2Mbps/Baseline读回通过 |
| 编码退出 | exit1，stderr `poll device failure`；新内核记录`MVX ... H264ENC: MMU ABORT`，不是仅凭POLLERR猜测硬件异常 |
| 进展 | 已提交0..8共9输入，3输入归还；4个capture chunk（头部＋3图像），共29,879字节；没有完整summary/LAST/54帧验收 |
| 主机部分解码 | 有限部分文件可解码0、1、2三个编码ID，形状720p。它们不是完整动态样片；未封装为通过的MP4 |
| 资源与保持 | 未见OOM；available约730MiB，应用退出/清理后无测试进程。失败后BOOT/SDK/三库及FPGAoperating保持；未复位、重跑、换BOOT/固件或启动NPU/HDMI |

故障消息指向VPU固件内存翻译异常，但没有提供故障地址或页表信息，**尚未证明根因是用户侧buffer、驱动、固件还是配置**。输入异步排队9份，已解码前三份并不能证明“第3帧内容导致异常”。容量/行复制范围已有检查、失败前没有buffer ERROR标记，但目前日志缺少QUERYBUF的mem_offset/data_offset及完整QBUF/DQBUFplane轨迹，不能据此排除所有布局或队列问题。

固件身份已固定：`h264enc.fwb` SHA256`7c93d4ff12b54eb13bd07e6cd60d6fe58033ef022ec0bfd657754b88485e95bf`，`h264enc.prot-ver.fwb` SHA256`6b9ad1bd475c33b6f79c1a851913ccf9f2d34ae51c49fdcd1d51e7144f164271`。只读保存debugfs日志README，没有写severity、读MMIO寄存器或改固件。网络检索未找到能与本机版本及该报错直接对应的可靠修复，不采用其他平台建议替换。

当前依照已批准计划的“身份变化、超时/OOM/总线错误、异常输出或SDK/VPU错误时保存部分证据并停止”处理，不能继续RTSP或真实链路合并掩盖异常。完整[独立失败复核](evidence/video-sequence-20261007-r1/failure-review.json)与原始回传均保存。

## HDMI配套核对

允许HDMI测试的授权保持，不再处于人为暂停状态；当前卡在可执行路径的证据门检。

- 当前BOOT.BIN与本机“悟净LITE版_BOOT_25122301_单路PLIN+pHDMI”发布包逐字节SHA256一致，当前DTB也与包内文件相同。这加强发布包身份联系，**不等于本机参考RTL就是该运行位流的源码**。独立`.bit`文件的完整字节哈希/长度与发布包不同，未把BOOT匹配扩大成所有组件一致。
- 当前无fbdev/DRM/EDID节点，DT未暴露HDMI时序控制接口；PS时钟树不是PL像素/串行时钟证明。udmabuf0显示128MiB、物理起始0x30100000，但这不是可直接占用的scanout区/与NPU不冲突的证明。
- 厂商包装类只分配RGB565帧缓存并向参考0x40080054提交地址/8，没有时序设置与等待/停止扫描逻辑。参考RTL存在1080p宏、0x094..0x0B0时序线索和Xilinx时钟IP；其路径hdmi_out_clk还接外部cam_clk_use，不能仅按IP名字认定实际像素时钟148.5MHz。未把参考地址当当前板端可写地址。
- 发布包uEnv有loadbit/download.bit启动线索，已只读保存；没有HDMI时序参数。启动脚本与文件存在性不等于当前硬件已按某时序扫描，需要进一步建立实际位流与接口联系。
- 已在主机生成1920×1080 RGB565LE色条/网格/边框/灰阶测试图，逻辑stride3840、4,147,200字节，PNG已目视检查。该图明确标记OFFLINE，并非实屏截图，**尚未上传扫描输出或做1080p60实屏验收**。

HDMI只读核查前后dmesg相同；没有Device::Open、模型Session、寄存器/PLL写入、scanout内存分配或BOOT替换。

## 下一步的具体定位方向

优先准备最小VPU取证修订：保留格式/码率/profile/复制/队列数/输入来源，记录每个QUERYBUF映射cookie/长度/data_offset、QBUF/DQBUF索引/planes/flags/PTS、buffer所有权及poll revents；必要的Host写后逐行比较只证明CPU视图，不当成设备缓存同步证明。固定固件/驱动身份，与本机官方客户端内存/队列约定对照，再决定一次新目录的有界诊断。未实施新的硬件取证或猜测性缓冲区扩容/profile切换/延时。
HDMI方面需当前Lite位流的时钟、时序配置、scanout归属及停止协议资料或可核对工程，才能进入独立色条和换帧测试；不能因缺少fbdev就绕到未知地址。已有色条文件可直接用于后续确认路径。
本轮无完整动态视频/HDMI/RTSP/整机性能通过，工程管理份额不增加。会话全部结束，新[检查点](evidence/video-sequence-20261007-r1/next-checkpoint.json)保留故障和恢复门检；不重跑旧失败包。
