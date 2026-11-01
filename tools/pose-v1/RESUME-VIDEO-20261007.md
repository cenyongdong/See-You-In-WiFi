# 视频任务暂停与恢复入口（2026-10-07）

> 2026-10-08当前：两缓冲启动三次回归及有限主线程Engine＋后台VPU三/27窗口通过，987原始编码帧全解码核验。[启动](VPU-STARTUP-RESULTS-20261008.md)、[常驻/预览](RESIDENT-RESULTS-20261008.md)、[恢复点](evidence/resident-20261008-r6/next-checkpoint.json)。下一在线owned AU/live555，保留原模型/数学/SDK/BOOT、主线程模式/两缓冲候选；旧后台Engine/六缓冲失败勿重跑。任务未被暂停，测试与SSH/SFTP已关闭，无后台。不是daemon/RTSP/整机5Hz/长期验收，预览名义10fps不当真实PTS；旧入口为历史。

**2026-10-08恢复入口已更新，任务未被暂停。** 先读[有限合并结果](PIPELINE-RESULTS-20261008.md)、[检查点](evidence/pipeline-20261008-r6/next-checkpoint.json)、[下一门检](PIPELINE-NEXT-20261008.md)。Host107与两有限合并成功，r6无规整新进程重复失败；不要重跑旧失败或自动compact。下一新修订只读取证分配时序，保留6队列/prime2/cookie/math，再有依据最小修正。测试与会话已关闭，无后台。以下入口均为历史阶段。

**当前入口：独立RTSP首批已完成，已审查动态样片。**

先读[RTSP结果](RTSP-RESULTS-20261007.md)、[新检查点](evidence/rtsp-20261007-r3/next-checkpoint.json)、[F0接入门检](F0-INTEGRATION-PREP-20261007.md)。r3两会话200帧＋r4标准播放器100帧逐位原视频，服务/会话均关闭；不要重跑已通过的独立文件/传输阶段。下一有限真实Engine结果→渲染→VPU/owned AU接入；模型/SDK/BOOT与帧协议保持。HDMI配套仍缺，色彩SPS标记另列。原暂停、失败和r5入口均按历史保留。

**当前入口已更新：阶段恢复后，整体暂停撤销，V2-A故障修正与完整视频核验完成。**

先读[VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md](VIDEO-DESCRIPTOR-R5-RESULTS-20261007.md)、[completion](evidence/video-descriptor-20261007-r5/completion-review.json)、[新检查点](evidence/video-descriptor-20261007-r5/next-checkpoint.json)。r5两独立上下文各54帧完整/相同码流，主机54ID/27来源/关节通过；无需重跑已通过文件编码。源码当前r5，冻结包/build及原失败均保留。
下一为动态样片人工审查及RTSP准备：实际SPS/PPS/NAL/PTS、有界owned AU/归还顺序、加入与重连；当前无后台服务或会话。HDMI配套未建立不写；原SDK/BOOT/模型及NPU帧协议保持。以下是原r1暂停与故障历史，不能作为当前执行状态。

中断、等待唤醒；当前不执行构建、连接、编码、HDMI或自动化。HDMI测试授权与已批准下一视频计划保留，待阶段恢复后再继续。

## 先读

1. `evidence/video-sequence-20261007-r1/next-checkpoint.json`：本次实际状态/暂停边界。
2. [VIDEO-SEQUENCE-RESULTS-20261007.md](VIDEO-SEQUENCE-RESULTS-20261007.md)：完整首批故障及HDMI配套结论。
3. `evidence/video-sequence-20261007-r1/failure-review.json`与原回传：真实编码exit1、固件MMU异常、9输入/3归还/仅3解码帧。
4. [NEXT-VIDEO-PLAN-20261007.md](NEXT-VIDEO-PLAN-20261007.md)：原授权路线；新故障须先定位，不进入RTSP/实时合并。

## 已完成与不可误记

- 新有限API `software/pose_v1/include/vpu_encoder.hpp`、`src/vpu_encoder.cpp`、`src/vpu_sequence_check.cpp`已交叉编译；旧r4/推理/渲染保持。
- `.local/pose-v1-vpu-sequence/package-20261007-r1`：27真实来源、54帧输入、新程序及完整身份；输入`5da0b23d093eae65c9a3bd6cbcf8bceb86782ce38c6eacd0faae2189b13b6216`，程序`109e24bd32517f49f86a9f4f131ad2a3e1f070da48dd07c88db901429eef7e8c`。
- `.local/pose-v1-build/vpu-sequence-20261007-r1`：构建日志与冻结三源码副本。
- 板端`/tmp/pose-v1-vpu-sequence/20261007-r1`：协商、编码失败、HDMI只读与失败后身份全部保留，不删除/覆盖/重跑。
- `evidence/video-sequence-20261007-r1`：negotiate/encode/hdmi-audit/failure-metadata/发布包哈希/uEnv/离线色条。encode下partial-preview仅失败取证，不是验收视频。
- 成功仅限构建/真实输入准备/协商/只读审计。真实54帧未通过；没有完整MP4、实屏、RTSP、并发推理或性能验收。
- VPU固件报MMU ABORT，原因与错误地址未确定；无OOM、BOOT/SDK变化。禁止靠buffer扩容/profile切换/延时或重新运行原包猜修复。

## 安全暂停边界

VPU程序已退出，异常路径执行队列停止/解映射/关闭；失败后无测试进程。原SSH/SFTP会话关闭。发现发布包uEnv含download.bit路径后准备补查文件，但暂停期间新SSH仍在认证前，已取消，**没有执行该远程命令**。没有后台任务或自动唤醒。

## 唤醒后顺序

先本机校验源码副本/包与失败目录哈希，再准备最小日志候选：记录QUERYBUF mem_offset/data_offset、每次QBUF/DQBUF索引/planes/flags/PTS、缓冲区所有权和poll revents。比较本机官方客户端约定、固定固件版本；日志修订不能默默改变原格式/码率/复制或把Host读回当DMA同步证明。
明确新诊断范围与错误后设备状态，再新包/新构建/新目录有界取证；不重跑r1、不自动复位。当前没有已经应用/构建的r2诊断候选。
HDMI可继续已授权只读来源核查：发布包BOOT/DTB字节对应但实际位流与可写接口仍不明，uEnv的download.bit路径查询尚未执行；时钟/scanout/安全停止证据确认后才1080p60独立测试。离线色条已准备，现场观察依旧必要。
