# ADR_07：视频格式、驱动描述与传输时序的分阶段验证

- 日期：2026-10-08；状态：文件编码/有限实时编码/独立RTSP回放通过，在线接入实施中，HDMI未通过。
- 决策：先证明字节、驱动队列及真实帧来源，再证明传输；保留驱动cookie/实际参数集/PTS，拒绝猜测显示寄存器。

| 难点与历史失败 | 有依据的解决与验证 | 剩余范围 |
| --- | --- | --- |
| raw/coded格式设置顺序导致coded2×2，单plane色彩方案不适配 | raw之后重设coded并G_FMT核对；实际NV12 raw2 planes、H264 capture1、stride1280、601有限；拒绝单CAPTURE色彩候选，保留MPLANE | [独立编码](../tools/pose-v1/VPU-RESULTS-20261007.md)30帧通过。10fps与720p编码规格不等于HDMI1080p60 |
| 实际骨架编码MMU ABORT，只有部分帧 | r1/r2保存PC0x1888/FADDR0x20600000与IOCTL/offset日志；r5保留QUERYBUF opaque MMAP cookie用于QBUF，其余复制/格式/control不变 | [描述兼容修正](../tools/pose-v1/VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md)两次54帧/27来源、码流179648字节逐位、756关节通过；不是页表内部根因或所有驱动通用规则 |
| VPU输出指针归还后可能被覆盖，编码和画面来源脱节 | OwnedFrame拥有NV12字节，capture复制成OwnedPacket后归还；记录encoded_id/source/invocation/实际PTS与图像marker，正常STOP/LAST/drain/队列归还 | [有限合并](../tools/pose-v1/PIPELINE-RESULTS-20261008.md)、[常驻](../tools/pose-v1/RESIDENT-RESULTS-20261008.md)。987帧/5530关节成功；重复画面明确不算新姿态 |
| Engine初始化29秒超过编码文件deadline、首次启动资源失败 | producer/codec时间分开而总硬件180s保持；6→2缓冲保存普通order7+块，首次capture先于Engine；同进程上下文减少重复分配 | 详细选择和三次首次启动见[ADR_02](ADR_02.md)。CMA256MiB未扩大，无自动规整/清缓存/重启；有限上下文不是已部署daemon |
| live555编译头/SSL配套和会话回收 | 使用本机厂商2024.11.28及同包静态库/头；r1缺include保留。客户端88帧因无保活停止，补3秒GET_PARAMETER，新目录测试 | [RTSP结果](../tools/pose-v1/RTSP-RESULTS-20261007.md)：两会话200帧＋直接FFmpeg100，NAL/像素逐位，IDR加入/重连/TEARDOWN和端口归还；厂商RTCP诊断stderr保留 |
| 旧文件10fps和真实采样PTS混淆，SPS色彩未声明 | 文件回放90kHz9000ticks独立核验；常驻保存真实steady_clock采样PTS，MP4预览明确名义重建；实际SPS/PPS从码流取得 | SPS video_signal_type_present_flag=0，未猜primaries/transfer。跨播放器色彩标定待验；单slice索引合同非通用AU解析器 |
| 显示器报告时序不支持 | 目标1920×1080@60Hz，后恢复HDMI测试许可；只读DT/clock/BOOT/参考审计和离线色条 | 当前clock/scanout/换帧/安全停止配套未知，未写板端时序。PC截图不作板端证明；在线RTSP先推进，HDMI另待实际配套 |

## 下一方案

在线分支使用有限容量owned AU、live555事件循环单线程、生产者通知和实际PTS。等待IDR再加入，慢客户端不得任意丢P帧；超限停止。先Host拒绝/所有权测试，再实际三窗＋重复/27窗与主机逐帧核对，后整机长期。见[ADR_08](ADR_08.md)。
