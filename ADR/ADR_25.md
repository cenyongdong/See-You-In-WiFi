# ADR_25：公开 PL DDR 分配容量与较高来源位置对照

日期：2026-10-10。状态：范围执行完成；独立较高位置对照通过，模型根因未解决。

## 问题与证据

模型 GatherElements192 的偶发坏块仍未解决；旧失败现场完整保留于 ADR_23。ADR_24 的真实类型静态／动态／VPU 三阶段各100对正确，但独立 SDK 来源位于4096／34368，模型来源109232128／109285376约104MiB。来源位置、NPU生产以及运行压力仍有差别，不能把前批通过当模型修复。

## 取舍与决策

按获批 [方案](../tools/pose-v1/TYPED-SCRATCH-NEXT-20261010.md)，先查询公开管理器，不包装模型绝对地址、不动私有cursor或映射。独立审计实际通过：DefaultMemManager、ADDR起点4096、声明容量4294963200、空已分配块列表，默认区域归属本设备。该数值是SDK管理空间声明，不独立证明所有4GiB均为实物可用存储。

匹配ARM头文件构造函数公开保存start/byte_size；Tensor.mallocOn→PLDDR区域malloc→DefaultMemManager→MemChunk创建的成功路径记录地址／长度并分配小型管理对象。块构造的operator new参数96字节，与申请字节数不同；所核验成功路径未调用Linux大块CMA、mmap或整块初始化。完整函数范围和哈希绑定到 [管理器审计](../tools/pose-v1/evidence/plddr-position-20261010-r1/manager.acceptance.json)。不据此宣称SDK所有分配路径都无Linux申请。

新独立适配先在同区域使用Tensor.mallocOn持有96MiB占位，不对占位read/write/copy；再由SDK选择真实192两类型的源及32字节padding。仅接纳64–128MiB数值窗口内、64对齐、归属正确、容量足够、无别名与重叠的实际返回位置。这不是硬件bank划分，也不要求与旧模型地址精确相同。位置未控制、容量或所有权变化即停止，不增加占位试探。

范围契约封装在SDK无关模块，SDK分配封装在独立适配实现；复用冻结动态模式／复制／拥有值／异常两晚源机制，主推理器和CPU数学不改。Native／ARM先验后一次无VPU动态100对，再一次VPU动态100对。未创建模型Session或NPU前向。释放后用公开管理器验证自有块归还。

## 解决与验证结果

管理器审计、构建、Native／ARM契约、无VPU动态与动态＋VPU全部通过。新探针f375b781…408f16b／manifest29759437…2e1b464，403载荷94来源；主ELF和旧typed ELF逐位保持，原Host107／12注册／59600值明确身份复用，未新模型运行。Native／ARM位置各12拒绝及原字节各8拒绝通过。

96MiB SDK自有占位起点4096，无数据访问；返回源100667392／100697664、padding32位于100697632，真实类型／分布／合法窗口／64对齐／归属／非重叠均过。无VPU100对94.25189ms、VPU100对19800.40012ms，合2388000 FP32逐位正确，动态index1–100及独立期望指纹全部对应。公开分配块0→1→4→0，两个阶段均归还全部自有块。

229capture含1参数集／227图像／1空LAST、41557字节；227解码ID与实际PTS通过、提交归还／正常drain／两STREAMOFF／join后SDK销毁。仅合成NoInput，无模型Session／NPU forward。本批普通512KiB单位24达到资源策略余量，规整0；内核事件保持，全项目程序／端口／代理会话关闭。

完整实现、程序身份、实际结果及范围见[本批结果](../tools/pose-v1/PLDDR-POSITION-RESULTS-20261010.md)与[完成证据](../tools/pose-v1/evidence/plddr-position-20261010-r1/completion-review.json)。正常测试没有触发硬件异常；异常保留逻辑复用冻结模块，不能把其Native测试当本批真实SDK异常路径发生过。

## 限制和后续

实际较高来源通过，NPU生产与真实运行时状态仍待单独对照；源约96MiB并非精确旧模型104MiB。不证明整个4GiB物理容量、SDK／VPU所有条件正确或cache fence。最终MemAvailable698728KiB／CmaFree130360／普通单位24为现场，系统另有apt任务，不直接推断泄漏。下一[原混合引擎无视频有限对照](../tools/pose-v1/PLDDR-POSITION-NEXT-20261010.md)仅准备未实施。持续保存旧失败，稳定103、长期、HDMI、零拷贝尚待。
