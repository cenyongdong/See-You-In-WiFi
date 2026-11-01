# 连续forward输入内容诊断方案（已批准）

已明确回复“同意”。代理已交付r4取证源码及最终身份包、本机模拟检查通过；尚未新编译或板测。
当前入口[MIXED-CONTENT-R4-COMMANDS.md](MIXED-CONTENT-R4-COMMANDS.md)，交付[MIXED-CONTENT-R4-DELIVERY.md](MIXED-CONTENT-R4-DELIVERY.md)。
下文未写入/待批准是方案讨论时状态，不覆盖本次授权；仍仅诊断，不提前授权据日志形成的修复。

依据：[r3三样本失败](MIXED-FUSION-R3-THREE-FAILURE.md)。PS输入及ONNX响应不同，板端全输出却与308相同。
当前只完成回传和SDK资料审计，没有写入下面的诊断修改、构建新程序或执行新硬件测试。
目的：定位连续forward的实际数据在哪里不再随帧更新，不预设缓存/同步/输入生命周期原因，不直接修复。

## 诊断改动

在独立新r4候选中显式启用内容取证，保留原计算与全部停止门禁：

1. 每次Host输入Tensor.write后，用SDK read回读该CPTR Tensor的43200字节，保存caller-input，逐位核对固定tokens。
   同时记录case/frame/invocation和存储元数据；不只记录此前生成的PS输入文件。
2. 现有Input0 post callback中，仅当输出确定为同形状Host CPTR时，通过SDK read保存input0-output，比较当前caller-input。
   记录same_handle/same_chunk等对象关系，不直接解引用物理地址。若Host输入或Input0内容不符则抛出诊断停止，
   不继续后面的NPU计算去掩盖输入错误；存储不明确同样停止。
3. mixed_bridge只转储**原有SDK copyFrom完成后的Host暂存内容**及已计算的Host CPTR结果，
   覆盖五适配节点的全部非参数输入和输出。新增invocation标记避免首帧与重复帧只用frame_id混淆。
   不新增设备到Host读操作、不读任意寄存器/OCM、不改等待/就绪标记，不直接解引用ADDR/BOTH。
4. 保留原原到七组融合门检、参数/输入校验、算子回调、四次前向和“不同输入全输出相同即失败”门禁。
   内容文件保存完整原字节；代理在本机计算SHA256、逐元素差异，并按时间顺序定位最早保持旧内容的边界。

拟修改mixed_check.cpp、mixed_bridge.hpp/cpp及必要打包/核验工具；冻结CPU数学内核/Gather、模型/RAW、
SDK默认融合/内存优化、位流/BOOT。新目录/包/构建标签保留r3源码和所有失败证据。
不会在此轮增加Session reset、重新apply、每帧重建Session、强制setReady(false)、缓存清理、固定输入复用或任何猜测性修复。

## 验证和执行

代理准备源码、Host内容回读/逐位校验测试、身份包和逐条命令；人工操作新r4交叉编译与Lite操作。
新身份按既有构建→Host107/内容路径→离线→SDK内存→apply→单样本→同Session三帧＋首帧重复顺序门检，
每阶段回传核验后继续；单/三样本仍180/300秒外部限时，不重跑r3。
当前批准若取得，只授权内容取证及既有受限验证，不提前授权根据结果形成的修复/SDK配置变更。
源输入/存储不符、SDK异常、OOM/总线/超时、非有限输出或原门禁失败均完整保留停止，不自动重试/复位。

## 如何解释结果

- caller-input已不同，Input0仍首帧：优先定位Session/Host Input处理边界，不能泛称板端不支持模型。
- Input0随帧变化，首个适配节点188收到的ZG结果仍不变：范围缩小到Input0之后及首ZG段，仍需区分传入/完成状态/模型分段行为。
- 上游暂存变化、下游开始不变：按实际节点内容和输出进一步定位，不猜测地址映射。
- 加记录后不同输入响应恢复：诊断改变了时序，不能据此宣布修复，需要后续讨论受控验证。

内容读回和文件记录会增加Host开销、改变时序；本轮不能用于性能验收。SDK硬件同步及数据重用更深原因仍可能需要后续厂商资料或受控探针。
正式执行需按AGENTS.md决策与执行审批取得同意；本方案不降低工程停止条件或自动宣布精度通过。
