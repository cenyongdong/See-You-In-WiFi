# 正式融合绑定门检修正方案（已批准）

已明确回复“同意”，代理已应用修正并生成r3新包，完成本机回放/异常拒绝核验；新ARM编译和板端运行尚未执行。
当前入口[MIXED-FUSION-R3-COMMANDS.md](MIXED-FUSION-R3-COMMANDS.md)，交付[MIXED-FUSION-R3-DELIVERY.md](MIXED-FUSION-R3-DELIVERY.md)。
下文“未修改/待批准”为方案讨论时记录，不覆盖上述最新批准状态。

依据：[r2完整取证结果](MIXED-BINDING-R2-APPLY-RESULTS.md)。1173个原HardOp在apply后合并到七个实际ZG绑定，
原检查器直接按原ID查部署后表而停止；8622可追溯到9185。九项异常快照拒绝检查已在本机通过。
当前仅完成资料/数据审计和方案，未修改正式C++或mixed_validation_gate.py、未构建或运行新程序。

## 拟修改文件和行为

1. software/pose_v1/src/mixed_check.cpp：Session创建后验证1181原节点直接绑定，1173 HardOp均ZG、八非HardOp均Host。
   apply后按实际绑定表的ZG后端实例查询其forward_info，只处理已实际绑定的执行组，不能因hardop_map有条目就认定已绑定。
2. 每个执行组要求信息已定义、net_hardop ID等于绑定键、属于同一ZG后端，hardop_map与idx_map对应同步元数据一致。
   merge_from中的每个ID必须是原图HardOp；七组联合恰好覆盖全部1173原节点，每个只出现一次，无额外成员。
   当前范围固定于本模型/SDK及r2观测七组9185至9191；分组成员集合应匹配已审阅快照，变化时停止讨论。
   原HardOp条目layer_count=0不作为缺绑定判断；只要求已绑定有效组layer_count>0。
3. 非HardOp继续要求原ID直接绑定到Host；六计算节点与Input/Output保持，不允许用融合覆盖它们。
   保留两组全部公共快照，新增每个原节点的effective_op_id/binding_kind/is_hardop追溯记录；
   bindings.jsonl仍记录全部1181原节点，其中1173条是原HardOp，不把七组数量冒充1173原节点数量。
4. tools/pose-v1/mixed_validation_gate.py：修正实际HardOpNode类型识别，并独立复核创建绑定、部署实际组及全部merge_from、
   两同步表、原到有效ID映射和1181条最终记录；原覆盖要求及六Host要求保持。保存完整原ID与组映射。
   缺成员/重复/额外Host成员/错误后端/未绑定有效组/组身份或同步表不符/模型SDK变化均拒绝。

算法/模型/RAW、CPU计算和数据桥、Matmul的NPU分配、SDK自动优化及设备配置保持。
不补CPU Matmul、不再次调用autoMerge，不禁用融合或通过删检查/降低原覆盖数绕过门检。

## 验证与执行分工

代理应用批准修正并保留r2源码/脚本备份，新增离线核验及异常拒绝检查，以新r3包/构建标签生成身份。
人工操作交叉编译；代理核验后，人工按新身份Host107→真实RAW/PS离线→30秒SDK内存→300秒apply逐阶段回传。
旧r1/r2包、程序、门禁与失败证据全部保留，不复用旧程序验收或重跑旧目录。
本次修正后的首次硬件目标仍仅apply，不forward。新apply门检通过并回传核验后，才推进原批准的单样本/三样本路线。
任何超时/OOM/总线/SDK异常或未知映射变化保留停止，不自动重试/复位/改SDK。
代理仅实施源码/脚本和本机证据审阅；FPAI构建/传输/板端执行仍人工完成。

## 不确定性与审批原因

当前证明SDK元数据原节点追溯完整；并未执行NPU或验证实际PS/NPU数据同步、整图输出及数值精度。
新的追溯核验可使程序正确区分合并键与原ID，但其ARM编译、正式apply及后续前向仍需实际验收。
本轮批准的r2范围仅公共快照；此方案改变正式门检与本机核验器，按根AGENTS.md决策与执行审批条款先讨论批准。
