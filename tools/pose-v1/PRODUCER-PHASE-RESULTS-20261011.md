# reset前分段观察与绝对时隙门检结果

2026-10-11。PRODUCER-VPU-NEXT；本批已结束，下一仅准备。

## 通过内容与限制

同程序SHA256 `b81835cdfea38efc40faacb23639fa2bf8f716b8bf6504b6cdc0ee9613c9e06f`：无／有VPU各固定100次A/B、5.05Hz预定绝对时隙通过。实际200调用、2,352,000 FP32和全部输入逐位独立参考／有限、每次0→11；准备结束和最终deadline均独立核对在原planned+198019801ns内。阶段exit0／stderr空／内核同，原1.764秒尖峰未复现，正式192坏读未复现未修。不能把独立低地址组通过记为完整103／整机5Hz或永久可靠性。

Native／ARM：载荷拥有值及9拒绝、原时隙算术、公开ioctl返回／errno／EINTR／EAGAIN透传，以及新Trace容量／线程归属／异常不掩盖／返回值／截止边界通过。模拟迟到路径不前向；本批物理100均在时隙内，没有真实触发该拒绝路径。Host107引用原已验收批次，没有新跑。

## 实现与分段结果

SDK无关Trace预分配最多16384事件，main线程所有、同steady_clock／线程CPU／getrusage缺页及切换计数，阶段各9800事件；热路径不写新增诊断文件，join与SDK销毁后落盘。应用记录sleep、video检查、目录、输入／identity保存、SDK调用、比较及最终检查；独立SDK诊断副本记录owner／校验、Host分配／存储检查／输入字节复制／write、journal打开／flush、reset／forward／wait／输出复制与保存。原producer_sdk和152冻结软件不改，副本diff保存，原数据保存位置和完整输出保存后比较保持。

| 最长区间 | 墙钟 | 线程CPU | 计数与判断 |
|---|---:|---:|---|
| off输入486保存，inv30 | 46.84692ms | 0.20014ms | 自愿切换1，缺页0；保存区间有等待 |
| on输入486保存，inv54 | 42.52643ms | 0.33235ms | 自愿切换2，缺页0；保存区间有等待 |
| on forward，inv2 | 3.72188ms | 0.34671ms | 自愿切换1，缺页0；不是纯NPU时间 |
| on Host分配最大 | 0.06657ms | 见原事件 | 本轮无长分配空档 |
| on Host write最大 | 0.03287ms | 见原事件 | 本轮无长写入空档 |
| on journal flush最大 | 0.07562ms | 见原事件 | 本轮无长flush空档 |

墙钟差与切换计数不能进一步区分存储等待、文件系统或调度责任，也不能把本轮46／42ms回填为旧1763ms尖峰根因。分段观察本身增加时钟／资源系统调用，原故障未复现，不称修复了IO或NPU问题。父sdk_call与子阶段嵌套，不能把各均值简单相加；sleep不计计算负载。

截止检查位于Host输入、journal首条准备后／reset前，仍使用原planned绝对终点；最终检查也使用原绝对终点，不由actual重启预算。当前journal的before_forward写入位于reset后；其跨度已观察但本轮没有超过时隙，不证明任意调度下硬实时保证。

## 视频与并发

先实际非空capture，再主线程Session；实际两个图案SDK自有临时区往返与部署范围核验后放行。独立9185原19成员、真实RAW／权重、0→11、非OCM SDK chunk所属范围保持，输出物理61440／40960，是原8467／8479别名；正式故障地址109232128／109285376没有在本批重建。

307 NoInput合成画面提交／归还，309 owned packet含首参数头和尾空LAST，共56763字节；主机解码307图像ID0–306连续、720p正确，完整PTS／来源／像素哈希保持。终止LAST的PTS0不计图像时钟，非空码流PTS非递减，首参数头与首图像同PTS。两端各2缓冲、NV12 OUTPUT_MPLANE type10／H264 CAPTURE_MPLANE type9、cookie／Host复制不改，307 Host复制equal。1844公开Q/DQ单编码线程／fd6，200次SDK copy跨度均与提交至capture跨度交叠；这不是硬件忙或DMA fence证明，不计新姿态吞吐。

正常drain／LAST／两STREAMOFF、全部输入归还、join后SDK毁且块0通过，没有abort。没有TCP／RTSP／显示／HDMI或完整Engine新门检。

## 资源、失败与收尾

off后普通512KiB折算2单位，代理一次规整326.36828ms、2→149，全四类前后快照／内核／原因保存，CMA256MiB保持；未清缓存、重启或重复规整。首启动成功不等于长期可靠性。最终MemAvailable694424／CmaFree1864KiB只作快照。

r1打包错用旧管理器名，板端在ARM合同／Device初始化前找不到新文件；原包和日志保留。r2新目录纠正包清单，复用同一已核验ELF和Native成果，无源码或数学更改，重新核对ARM合同后才执行物理阶段；不是失败Session重跑。板端未来mtime警告保留，不改系统时钟。

最终只读BOOT9／三preflight库及四链接库／模型RAW／SDK版本同，FPGA operating、dmesg逐位同，程序／管理器／端口39001和8554及所有代理连接结束，未追加独立暂停，管理83/100保持。

[off阶段](evidence/producer-phase-20261011-r2/off.phase-review.json)、[on阶段](evidence/producer-phase-20261011-r2/on.phase-review.json)、[完整视频](evidence/producer-phase-20261011-r2/on.video-review.json)、[SDK副本diff](evidence/producer-phase-20261011-r2/sdk-adaptation.diff)、[完成绑定](evidence/producer-phase-20261011-r2/completion-review.json)、[恢复](evidence/producer-phase-20261011-r2/next-checkpoint.json)、[ADR_41](../../ADR/ADR_41.md)、[下一](PRODUCER-PHASE-NEXT-20261011.md)。
