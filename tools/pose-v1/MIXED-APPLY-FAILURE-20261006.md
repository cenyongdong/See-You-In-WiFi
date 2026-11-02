# apply-r1失败与SSH退出审查（2026-10-06）

## 工程内容总结

截图在SSH登录shell直接执行set -eu，未包含原命令组外层括号。
test ! -e run-apply-check失败会触发errexit，结束登录shell并断开SSH；不能据此认定网络或板卡故障。
代理按特殊问题协助/日志读取授权，通过SSH只读ls确认目录已存在，再SCP取回到新本地目录，未执行检查器、Device::Open、模型或reset，未改板端文件。

已有apply-check结果为退出1，完整35项回传/290项包校验通过，程序/SDK/上一memory验收身份匹配。
Device初始化版本25122301/icore24160628保持，真实RAW参数及三份PS输入正常，注册12条符合预期。
阶段到session_applied后检查器主动停止：

```text
Original op lacks traceable backend binding (including any fusion): 8622
```

8622确实是固定ZG图中的首个HardOp；已保存的bindings.jsonl只有Input0→HostBackendNode一条，
因为检查器逐原节点查找时遇到8622即抛出，没有保存完整绑定表。
完整dmesg前后相同、无新增内核错误；bridge.jsonl为空，没有forward_started阶段或模型输出。
事实是Session::Create和apply返回，完整部署/绑定门检未通过；不是已证明的NPU计算失败或SDK不兼容。
不能生成apply验收文件或进入mixed-one，原目录/二进制/包均保持。

证据：apply-failure-review.json（历史附件，当前仓库未附：`evidence/mixed-20261006-r1/apply-failure-review.json`），
完整回传evidence/mixed-20261006-r1/apply-check，截图apply-directory-errexit-user.png。
认证口令仅用于SSH认证，未写入项目文件或日志。

## 对后续开发的参考

SDK Backend头文件提供MergedOps/autoMerge，ZG330BackendNode覆盖autoMerge；
HardOpInfoNode::merge_from明文注释为合并前HardOp ID集合，forward_info公开hardop_map/idx_map，
SessionNode/BackendNode公开network_view。来源为本机及已核对ARM3.39.0对应头文件。
**合并后的执行表示或绑定表粒度不同是候选原因，当前尚未获得实际完整映射，不能直接认定融合就是根因。**

当前检查器输出SDK typeKey为InputNode；后续正式核验还需使用SDK实际类型或is<HardOp>()，
不能混用静态JSON的HardOp名称和SDK运行时HardOpNode名称。现在没有放宽计数或修改核验器。

已准备仅增加公共元数据快照的候选，见[MIXED-BINDING-SNAPSHOT-PLAN.md](MIXED-BINDING-SNAPSHOT-PLAN.md)。
候选尚未应用、编译或上板。新方案讨论批准前不重跑apply/模型、不删改失败目录、不修改SDK优化选项。
SSH交互式操作不要单独粘贴set -eu；新连接必要时set +e/set +u，只读查询，或完整使用子shell/独立sh入口。
