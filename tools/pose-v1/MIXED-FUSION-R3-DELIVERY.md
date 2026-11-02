# 融合绑定门检修正r3交付

回复“同意”批准MIXED-FUSION-BINDING-FIX-PLAN.md，代理已应用并生成独立新身份包；未执行交叉编译或板端命令。
旧r2源码/核验器逐字节备份在evidence/mixed-20261006-fusion-r3，r1/r2包及失败证据保持。

## 实现

mixed_check.cpp新增创建阶段完整原绑定检查；apply后仅处理实际绑定到同一ZG后端实例的七个执行组。
检查forward_info定义/条目身份、两个同步映射一致、固定组成员及sync基线，无缺失/重复/额外成员。
全部1173原HardOp完整唯一覆盖，八非HardOp仍直接Host；Gather及其他CPU计算保持。
两组十份公共快照保留，bindings.jsonl输出全部1181逻辑节点的is_hardop/effective_op_id/binding_kind及实际后端，
另存binding-summary.json。原覆盖数不改为七组数量，428原条目layer_count0允许但有效组层数必须为正。

新增mixed_fusion_baseline.hpp和mixed-fusion-baseline.json，均从已审阅r2快照生成，记录七组成员及同步元数据。
核验器识别实际HardOpNode，并独立审阅创建绑定、部署七组、全部merge_from、同步表和1181条追溯记录，
要求匹配已审阅基线；apply-only还拒绝forward阶段、桥执行和模型结果文件。
SDK默认优化、模型/RAW/CPU实现/数据桥/预处理/旧推理器保持；Matmul继续NPU，不再次调用autoMerge。

## 本机验证与限制

test_mixed_fusion_binding.py使用真实r2快照生成**模拟的新格式追溯记录**，不是ARM程序输出。
1181逻辑记录/1173HardOp/七组正例通过，18类异常拒绝通过；额外验证数值1不能冒充布尔is_hardop。
C++头文件成员与JSON基线一致。Python AST、嵌入板端Python3.8语法、LF清单及包校验通过。
核对原forward代码尾部保持逐字节一致、三CPU文件及原infer/CMake身份保持。
两次回放记录保留，final为新增严格布尔校验后的最终回放。

新包.local/pose-v1-mixed-validation/package-20261006-fusion-r3：291项哈希、11构建文件、17源身份记录。
r2原289份非manifest载荷全部保持，新载荷仅增加融合JSON基线；源码记录中既有文件仅mixed_check.cpp及mixed_validation_gate.py变化。
源码/包审查（历史附件，当前仓库未附：`evidence/mixed-20261006-fusion-r3/source-and-package-review.json`）、
最终本机回放（历史附件，当前仓库未附：`evidence/mixed-20261006-fusion-r3/offline-replay-final/review.json`）。
这些验证仅证明核验算法及资料一致，C++ ARM编译、API实际调用和新正式apply仍待人工操作。

下一步仅执行[MIXED-FUSION-R3-COMMANDS.md A](MIXED-FUSION-R3-COMMANDS.md)：新标签mixed-20261006-fusion-r3交叉编译，
构建核验后逐阶段Host/离线/内存/一次apply。不复用r2门禁，不直接forward，不将交付或回放记为部署通过。
