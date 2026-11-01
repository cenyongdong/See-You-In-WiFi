# 真实拥有画面阶段：暂停恢复入口

当前已唤醒：公开read隔离候选107真实画面有限门检通过，旧暂停和失败内容以下仅作历史。最新读[INPUT-READ-RESULTS](INPUT-READ-RESULTS-20261010.md)及[新检查点](evidence/input-read-20261010-r1/next-checkpoint.json)。

2026-10-10，记录进度并暂停，等待唤醒。所有板测、回传、Native参考／解码审查已结束，无后台程序或代理连接；暂停期间不构建、连接、板测或自动唤醒。

## 已完成与未通过

隔离picture-r1程序7d421b40…b1b59e9／manifest e7c4b944…01adb98，403载荷118来源。单VPU实际capture→主线程单Engine，真实最高分骨架与拥有NV12、容量2源、10fps编码／2Hz三窗→103入口已实现。Native／ARM各画面13、阶段13、计数16、生命周期6、Run9拒绝过；旧主／常驻入口／模型／数学／SDK／BOOT保持，Host107／12注册59600仅冻结身份复用。

一次新目录运行：前三窗＋重复4次正确，随后103阶段前16次正确，合20前向302000FP32逐位旧参考。第21次inv20／local16／frame100020／S23_30_330，在GatherElements192索引非有限整数检查退出1，103没有通过，未重跑。

## 当前故障证据

保存3个CPU拥有输入47760字节。188.slot0与192.slot0逐位同CSI旧中间参考；192.slot1有144个有限但非整数索引，首3680，8坏段起点mod256均128，全部坏段等于同次、紧邻此前192.slot0复制的相同偏移字节，并非“上一帧”已证。两轮稍后真实PL DDR源读取94080字节，两slot四读取均逐位正确；晚于原复制，不能证明复制瞬间源或具体写入者。

326对象／163shadow稳定，168查询全234、183复制元数据；真实192源109232128／109285376合法不重叠，Host目标mod64分别32／0、FP32对齐合法。计数234不是DMA/cache fence，坏indices目标已64对齐，不以等待234／64对齐当修复。此次2Hz也复现，不能把问题限定为5Hz请求频率；真实绘图、NV12复制、写盘与堆／时序同时变化，不直接归罪渲染或VPU。

## 画面与清理

20画面全部发布／采用，队列水位1、覆盖／合并0。21份NV12（含NoInput）29030400字节逐位Native冻结渲染一致；395采样标记诊断hash一致。已捕获392图像：297NoInput＋95真实图像（20新来源／75重复），实际PTS、ID、1330关节及来源前缀过；3采样未捕获，485017字节部分H264保留，不记正常drain／LAST或完整视频验收。VPU summary submitted/returned为异常返回前默认0，不当实际计数；日志395输入queued／394归还。两abort STREAMOFF返回0、worker join后Engine释放、七项独立保存成功；内核无新增变化。

一次规整66.20272ms普通9→16；编码进入14→raw12→capture6→首次5，首次启动成功。最终MemAvailable745428KiB／CmaFree1604／普通10是释放后现场，不证明泄漏或永久可靠。无清缓存、重启、CMA／BOOT／SDK变化。

## 唤醒后的顺序

1. 读[暂停检查点](evidence/picture-20261010-r1/pause-checkpoint.json)和[进度证据](evidence/picture-20261010-r1/pause-progress-review.json)，核验冻结包／程序和已有失败。旧运行及失败数据不覆盖，不从停止的Engine继续inv21。
2. 完成本机公共SDK搬运路径审计：当前输入桥是`dst.copyFrom(0,src,0,bytes)`，晚源路径是`Tensor::read`。它们共享设备区域入口但目标与时刻不同，不能假定改API即修复。下一最小候选可评估公开read直接写入自有Host CPTR，保持dtype／范围／wait／CPU数学与输出写回，先明确actual API签名、所有权和测试边界；不猜ADDR映射、cache helper或寄存器。
3. 提出新身份／新目录的最小单路径变更与Host／三窗／有界长序列门检，再执行新验证；当前仅记录恢复建议，未写入该修复或新板测。保留异常Host暂存及两晚源，不放宽非整数、有限性或完整候选门禁。

稳定真实画面103、持续5Hz／长期、HDMI／在线RTSP、安全连续申请和零拷贝仍待；管理粗估83/100保持。

证据：[数值失败审查](evidence/picture-20261010-r1/picture.failed-review.json)、[Host对照](evidence/picture-20261010-r1/failure-host-comparison.json)、[坏段](evidence/picture-20261010-r1/failure-block-pattern.json)、[两晚源](evidence/picture-20261010-r1/failure-late-sources.json)、[视频前缀](evidence/picture-20261010-r1/video-prefix-review/review.json)、[样片拼图](evidence/picture-20261010-r1/video-prefix-review/contact-sheet.png)、[ADR_29](../../ADR/ADR_29.md)。
