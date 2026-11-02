# ADR_34：原Gather与ZG上游公开边界观察

日期：2026-10-11。状态：批准范围已实施、构建和板测结束；Host及正常四窗口通过，高负载192失败完整保存，根因待定位。下方实施中条目保留为历史。

## 现象与依据

前一批inv24姿态128有限失配，437输出正确；582/649更新输入两轮晚read均与原bad Host相同。真实RAW＋actual输入NumPy与582 CPU和最终姿态分别逐位同，异常早于582内核。原Gather442以及ZG9189/Hard8131边界没有实际数据，不能认定生产或读路径责任，详见ADR_33。

公开Session::CallBackFunc参数明确叫output_tensors，pre不是输入列表；Session私有tmap_不应接触。接口文档甚至post描述写作“之前”，不据此猜内部实现。选择post中按公开Value ID取生产者张量，在下一消费者pre中观察保留的生产者句柄，明确并非Session内部实际参数映射的直接快照。

## 当前决策

新增SDK无关upstream_boundary拥有值模块、薄SDK适配、隔离upstream_application_core和检查器。旧Gather init/forward注册及计算、bridge/SDK/模型/BOOT/reset(1)/745/profiling-off保持，不替换Gather或读取其他模块私有状态。

八点：437.post索引1137、9188.post数据4406、442.pre保留数据和索引、442.post1148、9189.pre保留1148、9189.post4414与4418。实际group回调必须公开包含所需Value ID且张量声明/归属/范围准确，否则停止，不猜映射。每点通过公开waitForReady(10s)及read，单steady_clock分别记等待/读/计数；计数不是DMA fence。ADDR/BOTH只记录身份不解引用。

每帧主线程清除五句柄和当前拥有值；最多103帧/824条元数据、101600拥有字节/帧。完整保存前四帧及最终现场，正常测量段不逐帧写大型画面或全部边界数据。FNV64仅诊断摘要；完整保存帧逐位核验，不以摘要替代数学验收。新模块正确处理部分读取错误和控制字符JSON。

36冻结产物从已核验上一构建逐位复用，来源/SDK/厂商身份重新核验，只编译三个新增目标；旧构建不写入。预编译发现需GNU++17/-DNDEBUG及公开Operation setters，错误日志保留，未访问板端设备。

## 验证与限制

Native拥有值/线程/上限/逐帧清除/部分失败7拒绝通过。接下来ARM同契约、Host内存调用原Gather并以NumPy核验，Host107→原三窗→一次固定QPC5.05/103输入新目录诊断。硬件180秒，异常保存停止，不重跑旧失败/调频/猜cache、对齐或零拷贝。

附加read、等待、句柄寿命和摘要计算会改变时序；保留的公开生产者可能被静态物理复用，不泛称实际消费者输入。若异常不复现，只说明这批观察下结果，不能认定根因修复或严格性能通过。

## 解决与验证结果

最终r4程序2534bdac…08eb7b、manifest7ab71582…a25cf6，403载荷／146来源，36冻结产物逐位复用。Native／ARM及原Gather单算子Host NumPy、Host107／12注册／59600FP32通过；四窗口4次60400FP32、八点32记录、495编码／465网络及全部四来源、正常drain／LAST和资源清理通过。原注册、数学、模型、SDK、BOOT和帧协议保持。

唯一固定QPC5.05诊断55正确返回830500FP32后，inv55／实际frame100056／S11_32_349在GatherElements192拒绝非整数索引。初始Host索引1584项不同、1582非整数、无NaN／Inf；两轮晚设备read全部逐位本帧旧参考，数据输入正确。原8保存＋独立1边界任务均成功。当前失败尚未到442，不能归因原Gather；晚源正确支持首次read／暂存或生产／完成时序的瞬态假设，不证明具体责任。

440条元数据覆盖55完整八点分组，仅前四完整帧保存拥有字节并逐位NumPy核验；当前inv55边界为空。中间帧FNV是诊断摘要，不能写成全部55 Gather数学逐位验收。组9189另有未观察的1860量化FP16输入，不以1148正确排除整个组输入问题。

一覆盖使调用序号与传输序号分离；独立审查／画面导出适配实际frameID，旧错误标签目录及审查失败保留，不重跑板测。407图像／377网络仅52来源前缀，正确尾52／53／54未capture，不能记完整103或正常结束。两abort STREAMOFF／子回收／network0／join后Engine销毁／内核同／端口释放，所有测试与连接关闭。

r3/r4四窗准备各规整一次148.45488／225.37927ms并保存现场；高负载前普通512KiB单位68，无规整。没有清缓存、重启或改CMA／BOOT。新模块等待／read／句柄／摘要与保存改变时序，本轮不作严格5Hz、长期或根因修复结论，管理83/100保持。

[完整结果](../tools/pose-v1/UPSTREAM-BOUNDARY-RESULTS-20261011.md)／绑定证据（历史附件，当前仓库未附：`../tools/pose-v1/evidence/upstream-boundary-20261011-r4/completion-review.json`）／[下一首次read／Host边界方案](../tools/pose-v1/UPSTREAM-BOUNDARY-NEXT-20261011.md)。


### r1 Host构造失败与r2修正

r1 Host-only的原Gather测试在构造合成group时，setOutputs拒绝复用模型网络已持有的Value4414。原Gather及Host107/设备均尚未执行，完整失败保留。r2只将合成HardOp/Value改为独立公开对象；产品ELF仍222b0816…c848e05逐位同r1，36冻结产物同。146来源/403包r2构建通过，原Gather/Host107正在验证。不是模型、SDK或注册修正。


### Host-only139阶段定位

r2修正节点所有权后直接forward仍139，内核前后字节同。两个新的独立20秒Host阶段探针分别证明构造、原init及topk/data/pre442公开采样完成，停止于原Gather forward；均未打开设备，保留独立文件/归档。r3仅给原Gather单算子view绑定HostDevice::Default并提供Host输出，不创建完整模型Session；产品ELF仍同，Host门检进行中。此测试上下文错误不当作真实混合Gather根因证明。


### r3 Host通过、三窗保存预算阻断与r4修正

r3补Host后端单Gather view/Device和显式输出后，原Gather NumPy、8点101600字节、Host107/12/59600完整通过。r3首次打包脚本误用了r2 build，被身份门禁在Host前拦截，原包保留；已新增显式路径＋打包前manifest/程序/测试绑定的工具，正确r3在新目录运行。

三窗实际4 presaved60400值逐位正确，客户端466帧结束；结束新增第9persist任务超出冻结flush的8任务上限，所有延后保存未执行。现场保留，未103，不能将四返回正确计整批通过。r4仅保留原8任务再用同一冻结flush单独执行1项上游保存及独立账本，不改变原模块或数学；新构建中。资源普通512单位8时一次规整148.45488ms，内核同，非数值修复。
