# Owned AU桥与网络适配器门检（2026-10-08）

先完成[全项目ADR归档](../../ADR/README.md)及模块设计规范，再推进已批准F0-A3。新模块门检完成；真实VPU/NPU在线闭环仍未由本轮验证。

## 模块与身份

- `h264_access_unit`：独立解析当前MVX完整capture的Annex B/单first_mb=0 VCL合同，稳定实际SPS/PPS、递增实际PTS、有界owned字节；拒绝不支持的NAL/多slice等。不称通用H264解析器。
- `access_unit_channel`：单生产者/单网络消费者，容量8，非阻塞self-pipe通知。编码链超限失败，绝不使用画面popLatest政策丢P帧。
- `online_rtsp`：live555事件循环独占全部网络对象；IDR加入、实际参数集SDP、真实PTS映射固定wall epoch、每客户端有界AU队列、结束/异常清理。无Icraft/V4L2头依赖。
- `owned_rtsp_check`只是有限网络门检入口，读取已经回传的resident-r6 capture包，通过独立生产线程按其实际PTS发布。无新推理/编码/HDMI或系统服务安装。

新AArch64程序SHA256 `eafd397cbe2cc60c77f20ce5054ff2b0bf7268302d6caffa3c9a9a0cd86619f5`；自检 `4d2b79f078247ae3852cfdc97cde227a6efab3e84d36c950f6ae4d42cccb1697`。
构建 `.local/pose-v1-build/owned-rtsp-20261008-r3`，包 `.local/pose-v1-owned-rtsp/package-20261008-r3-final`，manifest `3f9355633382360a28c03da71d813ff0dbc11fe1007e13f72506d9d730deb79a`，9载荷。厂商live5552024.11.28/SSL189头库逐项与旧r2基线相同，无安装新依赖；构建无warning/error，无Icraft动态依赖。

## 实际验证

- Native与Lite ARM分别通过17类拒绝、2000次通知/顺序、独占字节、容量8满时拒绝、关闭和异常传播；没有NPU/VPU访问。
- 493个真实记录AU全部到达网络线程，ID/PTS/IDR与capture参考一致。通道highwater1，无覆盖/丢链。
- 两会话各100帧，FU-A/单NAL重组VCL逐字节参考，RTP序号连续；真实PTS累计差按90kHz核对，误差不超过1.1tick的时间戳量化范围，未断言恒定9000ticks。
- 实际SPS/PPS用于SDP，首帧均IDR；每3秒GET_PARAMETER，TEARDOWN200及重连通过。SDP生成临时source0不传AU，实际source1/2与临时source均归还。
- 主机OpenCV/FFmpeg解码200帧，10bit encoded_id和全部BGR像素逐位此前resident视频，画面来源对应原记录。当前只是网络字节到像素核验，没有新模型前向。
- 板端exit0，纯Host stderr空，服务stderr两行已有厂商RTCP诊断保留；17项回传哈希通过，完整dmesg前后相同，BOOT/三库/SDK/FPGA身份保持，8554已释放。

首轮r3的200帧是记录视频启动NoInput段，不能单凭其宣布骨架变化通过。因此以同一程序/包在新r4-active上下文延后加入，两会话各54帧，共108帧；范围270–323及360–413。25帧NoInput，invocation0/1/2各5帧、重复首帧invocation3共68帧，完整覆盖四来源；所有字节、实际RTP时钟和解码ID/像素一致。额外17项回传、两行厂商stderr、exit0/内核同/全部source归还。总308网络解码帧，两个服务上下文各一次。

[四来源补充汇总](evidence/owned-rtsp-20261008-r4-active/completion-review.json) · [完整内容复核](evidence/owned-rtsp-20261008-r4-active/host-decode/review.json)

[汇总](evidence/owned-rtsp-20261008-r3/completion-review.json) · [200帧完整复核](evidence/owned-rtsp-20261008-r3/host-decode-r3/review.json) · [本机修正记录](evidence/owned-rtsp-20261008-r3/local-corrections.json)

## 难点与适用范围

部分不同P帧的压缩NAL字节完全相同，不能把SHA256当唯一帧身份。核验从唯一IDR开始顺序定位，再同时核对连续encoded_id、实际PTS、VCL字节和解码像素。准备时的唯一哈希假设失败目录保留，未改原capture、帧数或像素。

PowerShell属性计数和Python3.8兼容错误只在本机修正；审查的额外source是SDP探测，按真实生命周期校验，不把它记为第三客户端。本轮两板端服务上下文各一次，第二次为了补足内容覆盖，没有失败重试/规整/复位/改CMA或BOOT。

队列容量门检不等于真实慢客户端全链路稳定证明；live555/内核socket侧延迟、实时VPU、网络和推理同时争用尚未实测。既有SPS色彩信号缺口、HDMI1080p60配套、整机5Hz、30分钟保持待验。[下一门检](ONLINE-INTEGRATION-NEXT-20261008.md)接入实际capture，保留本轮和resident-r6冻结身份。
