# ADR_08：高内聚模块与在线编码AU桥

- 日期：2026-10-08；状态：接续路线；设计落实中，尚未在线实板验收。
- 背景：已有Engine、绘图、双缓冲VPU、有限常驻及独立live555回放已分别通过。直接复制大检查器或互相访问私有状态将增加所有权、线程和错误路径风险。所有后续源码高内聚、低耦合。

2026-10-08后续实测：独立r2真实本地CSI→Engine→render→VPU capture→AU→RTSP三窗＋重复/27窗＋重复已通过，32完整前向/980编码/650网络像素、全部32来源与实际PTS正确，Engine在workers join后才主线程销毁。原先“未实际在线”文字为前轮AU记录字节门检范围。首轮27晚加入与修正另记[ADR_09](ADR_09.md)，发送失败保护独立候选记[ADR_10](ADR_10.md)；guarded未进入正式r2。当前结果[入口](../tools/pose-v1/LIVE-RESULTS-20261008.md)，整机/长期/HDMI仍未通过。

## 决策与接口

1. 编码字节解析/参数集/单slice AU合同放入SDK无关模块，输入仅owned字节/PTS，输出owned NAL/AU。拒绝超容量、非法前缀/参数变化、不支持布局/PTS，不读VPU私有缓冲。
2. 有界AU桥负责队列、订阅、背压和停止/异常。与允许覆盖旧画面的容量2队列不同，已开始的编码参考链不随意丢P帧；超限失败，加入只从实际IDR和参数集开始。
3. live555适配层独占事件循环及source/sink/session生命周期；跨线程只使用经本机接口核对的通知契约，不能直接在编码线程调用网络对象。实际SPS/PPS用于SDP，steady_clock采样PTS映射到同一wall epoch，不伪造恒定10fps RTP步长。
4. 编排层只依赖Engine、render、VPU和网络公开接口。Engine继续主线程所有，VPU独占编码线程；服务测试窗口内保持Engine存活，有限r6原型不改成生产daemon。异常全局停止，先停生产，VPU drain和owned packet完成，再网络清理。
5. 不包含其他功能.cpp，不复制CPU数学或SDK帧完成逻辑。共享结构仅为必要契约，内部辅助类型私有；新目标/包/构建/目录保留原成功源。

## 门检与失败策略

先SDK-free Host测试owned数据/队列上限/通知/参数集/IDR/PTS/关闭及异常，再交叉构建身份/Host107；实际三窗＋重复及27窗有限联调后，核验完整模型输出、packet/NAL/RTP字节、时间、来源、主机解码和清理。失败保留现场，不自动重试/规整/复位。无新BOOT/SDK/模型、HDMI寄存器或常驻系统服务安装。

## 解决与验证结果

2026-10-08模块门检完成：新增SDK无关AccessUnitAssembler、容量8的AccessUnitChannel和online_rtsp适配器。采用非阻塞self-pipe通知：厂商UsageEnvironment.hh明确triggerEvent只允许外部线程调用且同ID未处理前不能再次触发；本方案让生产线程只写pipe，全部live555操作在网络线程，不依赖反复跨线程triggerEvent。

Native及Lite ARM分别通过17类拒绝、2000次并发顺序/通知、字节独占/关闭/背压测试。新程序eafd397cbe2cc60c77f20ce5054ff2b0bf7268302d6caffa3c9a9a0cd86619f5；189份厂商头/静态库与原基线一致。有限生产线程按已验收r6实际capture PTS提交493个AU，两个RTSP会话各100帧VCL/RTP时钟和解码像素逐位原视频，IDR加入/3秒保活/TEARDOWN/重连通过。首个SDP临时source没有AU，两实际source均释放，端口归还、exit0、dmesg相同；两行厂商RTCP stderr保留。队列highwater1，没有覆盖编码链。

新的取证难点：P帧字节可相同，NAL哈希不能单独作为帧身份。参考按唯一首IDR定位，再连续帧序号和真实PTS对应，逐帧字节＋解码10bit ID/像素独立核验；不把哈希相同解释为画面相同。见[结果](../tools/pose-v1/OWNED-AU-RESULTS-20261008.md)。

内容覆盖补充：r3两会话200帧是启动NoInput段；随后在新r4-active上下文延后加入，另108帧覆盖NoInput25帧、invocation0/1/2各5帧、invocation3重复68帧。全部VCL/实际PTS/10bit ID/BGR像素一致，四来源完整，正常exit0/内核同/端口与source归还。两上下文各一次，第二轮是不同内容覆盖测试，不是失败自动重试。汇总308网络解码帧，真实在线VPU仍未执行。

**本轮输入仍是已记录的capture字节，没有新VPU/NPU初始化，不是在线推理→VPU→RTSP验收。** 真实实时AU、网络慢客户端端到端背压、同进程争用和长期服务仍待下一门检。r6有限Engine在固定batch结束即销毁，下一集成应保持Engine至服务窗口结束，不能直接把原型称为常驻服务。后续进入[真实在线接入](../tools/pose-v1/ONLINE-INTEGRATION-NEXT-20261008.md)，无需重复旧Host/文件编码测试或改变模型/SDK/BOOT。
