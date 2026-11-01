# 前向尖峰诊断首轮结果

本轮构建、Host107及原三窗重复全链通过；33输入5Hz取证在第4次调用GatherElements192拒绝索引后停止，原inv28尖峰尚未定位。没有诊断或严格5Hz验收。

程序d4506060bbeea426bf0d6655da1f2ca526d0d00926a2774aef8ccd4650da4f7e；manifest61dfd67d4a8ee00ff817c3007e07255536b2633f2719f6c5d2101f13e940d88e。403载荷/57构建来源，原Engine/桥/数学/SDK/模型/RAW/BOOT/745/双缓冲/cookie/子程序保持；新编排仅增加trace-5hz并令diagnostic_frames=32。

## 验证和失败证据

- Host107、12注册、59,600FP32及6,912,000字节IPC/9拒绝、回收通过。
- 原三窗＋重复4次、60,400输入和输出FP32逐位旧参考；501编码/471实际网络画面及来源/PTS/像素核验通过，exit0/内核同/正常子回收。
- trace前三次完整输出共45,300FP32逐位旧参考；第4次inv3/frame100003在192两输入等待/复制之后、CPU计算成功记录之前失败：`floating-point index is not a finite integer`。原始失败输入未捕获，尚不能区分NaN/Inf与有限非整数，也不能确认坏值的来源。213条记录含失败调用的部分记录，145回传文件完整核验。
- 前三次相对跨度：forward平均184.71315ms，桥等待164.45956ms，CPU计算13.85573ms，复制0.59907ms。类别嵌套，不可相加；ZG提交不是纯NPU时间。未到旧尖峰调用，不得以这三次宣称尖峰修复或性能通过。
- 失败后两个STREAMOFF成功，网络source0，显示子进程错误清理回收，workers join后销毁Engine；8554/39001与程序均已释放，内核前后相同。客户端不完整EOF和发送中止是本次失败结果，不生成视频/网络门禁。

## 规整与当前权限

代理自主判断是否规整，AGENTS.md中的旧另行审批限制已删除。实际本轮只执行一次，79.59499ms，普通高阶页折算512KiB单位50→66。初始只读现场order7+为0，Host后已恢复；因此不能证明此次启动必须规整。规整前后内核同；未清缓存、重启或改CMA/BOOT。三窗后资源足够，trace启动未追加规整。

## 下一步

现有diagnostic_frames同时控制计时、算子日志和readiness查询，minimal_log并未关闭前向前后state查询。先用独立计时配置分离纯Span与额外SDK查询（仅候选补丁，未应用/编译）；在CPU异常后将已拥有的Host暂存输入和参数形状、来源、哈希保存在失败目录，不改变正常路径复制、等待或算子计算。针对192的索引由NumPy逐项判定，再决定最小修正，不能通过吞掉异常、改索引或放宽门禁修复。新目录Host及原三窗后才执行新的有限诊断，不重跑r1。

103请求扩展的固定身份/20.4秒发送计划及首尾/越界检查已准备，长入口尚未实施和板测；详细预算见[有界设计](BOUNDED-MEASUREMENT-DESIGN-20261008.md)。本轮异常停止，不继续长负载、HDMI或30分钟。

独立证据：[failure-review](evidence/forward-trace-20261008-r1/failure-review.json)、[局部时钟分析](evidence/forward-trace-20261008-r1/partial-trace-analysis.json)、[原三窗门禁](evidence/forward-trace-20261008-r1/process-three.acceptance.json)。恢复先读本结果及next-checkpoint；会话和服务全部关闭。
