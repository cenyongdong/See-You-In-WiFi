# 公开 read 输入桥：真实拥有画面有限验证

2026-10-10。阶段恢复后，隔离 input-read-r1 已完成。107 次真实推理及拥有画面／编码通过；本轮通过范围为 2Hz 输入、10fps 预览、单次有限生命周期，不是长期可靠性、整机5Hz或底层根因验收。

## 处理方法

冻结旧 `tensor_identity_bridge_r2.cpp` 及失败 picture-r1。新增独立 `read_input_bridge.cpp` 和 `input_read_sdk` 模块：源张量等待完成后，通过公开 `Tensor::read` 直接写入 SDK 分配的自有 Host CPTR。核验 dtype、容量、偏移、Host 区域及不共源 chunk；张量 data 已指向起点，不再加 offset。Host 输入和输出 writeback 的 copyFrom 保持，CPU数学／分布声明／Gather原实现／Matmul NPU分工及原帧协议不变。

新桥逆替换这一调用及新增include后，逐字符等于旧桥。异常 Host 暂存、两轮晚源、计数／对象／元数据取证保留，没有重复读纠错或异常后继续计算。设备read与旧copy仍共享源区域入口，不能据一次通过断言已找到 DMA/cache 的内部责任者；这是一条有实测支持的候选搬运路径。

## 身份与门检

新程序 `70c9df9f566c0b7fa55c1f86ef1440cf52ce610dba5e8de3ce0b711c0ae2082d`；manifest `dbf88b3f1cf877aa8ffeaa766a3b94775f978d93f3cc2fa523b727adad37d06f`。403载荷／126构建来源。原主程序仍为 fbf330d7…acb8702d；旧118来源逐项冻结，模型、RAW、SDK3.39.0／AXI库和BOOT身份核验。

Native：新read契约8拒绝、16守护字节与原异常传播通过；画面13、阶段13、计数16、生命周期6、Run9拒绝全部通过。ARM：同组契约通过，公开Host read实际192两规格47040字节／3拒绝通过。新桥实际Host107／12注册／22输出／59600 FP32逐位参考通过，非仅旧Host身份复用。

首次VPU capture后，主线程同一个Engine初始化29.30360秒，三窗＋重复4次→103，共107尝试／107完整返回，1615700 FP32逐位旧板端参考。旧失败样本 S23_30_330 在 inv20、47、74、101 均完整正确。没有新失败快照，未重跑旧失败目录。

对象1712条／856个拥有shadow稳定；8源chunk、44个Host目标地址。192查询856条全部达到234，963元数据合1819条，无查询错误或低于目标。计数仍不作为DMA fence，当前诊断I/O也不用于性能验收。

## 画面与视频

107画面全发布／采用，队列容量2、水位1、覆盖0／合并0。108份NV12含NoInput，共149299200字节逐位Native冻结渲染一致；824采样标记诊断hash与Native一致，FNV仅辅助关联，不代替字节核验。

824编码提交／824输入归还／824图像完整解码，含298启动NoInput、107个新真实来源、419重复旧画面。实际PTS、10bit ID、全部来源及7364关节可见性通过；重复不计新姿态吞吐。H264 1322032字节，SHA256 `510b11f39dc9d5d814ba629e65aaa2c50f1f59b753eaa82854472e5d82cdd825`。RGB平均绝对误差1.40314／最大帧均值1.44753为8bit有损诊断；不称RGB逐位一致、物理标定或MPJPE。

正常drain／LAST／两STREAMOFF，编码线程join后Engine销毁，七项独立保存成功；exit0、stderr空、内核前后逐字节相同，测试／SSH／SCP全部结束。板端最终进程和端口证据无项目服务。

## 资源与限制

准备快照普通512KiB单位29，高于策略余量16，规整写入0；没有清缓存／重启／CMA或BOOT修改。编码进入时自然变化到75、raw后73、capture后65，不能把不同时间快照当同一状态或固定可用余量。释放后MemAvailable746760KiB、CmaFree18744KiB、普通单位23，仅当前现场，不证明无泄漏或任意碎片条件可靠。

传输tar出现板端时钟早于主机文件mtime的警告，原日志保留；以SHA256、实际steady_clock和内容核验，不调整系统时钟或据mtime判断身份。Host及硬件均在原有界预算内完成，无自动重试。

## 证据与下一步

[组合Host门检](evidence/input-read-20261010-r1/contracts.combined.acceptance.json)、[完整数值／生命周期](evidence/input-read-20261010-r1/picture.acceptance.json)、[对象](evidence/input-read-20261010-r1/picture.objects.json)、[查询](evidence/input-read-20261010-r1/picture.counts.json)、[视频](evidence/input-read-20261010-r1/video-review/review.json)、[样片拼图](evidence/input-read-20261010-r1/video-review/contact-sheet.png)、[ADR_30](../../ADR/ADR_30.md)。

下一先冻结本候选作为有限通过基线，再把同一公开read适配层接入独立显示子进程／TCP与owned AU网络组合，保留当前文件检查器及所有失败；Host→原三窗→2Hz103逐级核验，通过后再独立有界5Hz。不能将当前结果回填到旧网络／显示程序。HDMI实际配套／30分钟／首次启动任意条件／零拷贝仍另验。
