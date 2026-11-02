# r4逐次输入内容取证源码交付

回复“同意”批准输入内容诊断方案。代理已保存r3五份源码/脚本备份、写入隔离诊断并生成最终包；未编译/接入板端/重新执行模型。
目标是定位连续forward实际内容最早停止更新的边界，不预设SDK缓存或DMA原因，不执行猜测性修复。

## 已实现

- 显式--capture-host-content仅允许Host/mixed模式。caller Tensor.write后通过SDK read保存Host CPTR原43200字节，核对当前tokens。
- Input0 post callback保存API传回的Host CPTR数据，要求dtype符合caller并逐位一致；记录same_handle/same_chunk。内容或存储不符先保存可得证据后停止。
- 桥只转储原copyFrom之后的Host暂存及原CPU计算结果，不新增设备读操作。frame和invocation共同标识，重复308不会混淆。
- 新content_diagnostic.hpp验证Host/CPTR/FP32/范围及安全名称，通过SDK read读取；辅助caller句柄不跨forward调用保留。
- Host模式在原107例后追加纯Host内容测试：两固定FP32模式读回及模拟别名，错期望、未分配和FP16拒绝；没有Session/Device::Open。
- host_content_review.py核对完整或提前停止记录，保存SHA及逐元素变化，定位caller或Input0内容不符；success核验要求每调用完整17记录。

捕获目录content/index.jsonl及callN.kind.opID.slotM.f32。完整混合调用为两根输入记录＋八桥输入＋七结果，约253760字节/次。
没有修改CPU数学/Gather、融合基线/原绑定要求、模型/RAW、SDK默认选项、原waitForReady/copyFrom/setReady处理、BOOT或位流。
未新增reset/重新apply/每帧重建Session、输入Tensor复用、setReady(false)、缓存助手或zero-copy。
内容记录改变Host时序及分配行为，若问题消失不能作为修复结论；回调所传Tensor的解释仍需依据实际记录及SDK语义，不能据对象关系直接宣布硬件使用了新帧。

## 验证与尚存限制

仅本机模拟格式测试：Host/单次/四次正例及11类异常或提前停止场景通过，能区分实际caller内容不符与Input0旧内容。
模拟数据不是C++ SDK read的实测；新Host内容路径必须ARM运行验证。
Python AST/板端嵌入Python3.8语法/LF、C++捕获名称字面量白名单、来源与包哈希检查通过。
旧CPU/原推理器/融合检查源码片段及SDK等待/复制调用保持。

最终包.local/pose-v1-mixed-validation/package-20261006-content-r4-final：291项哈希、12构建文件、20来源。
原r3共享非manifest载荷289份保持，仅runner增加显式捕获参数；中间准备包完整保留，不用于构建。
最终交付身份（历史附件，当前仓库未附：`evidence/mixed-20261006-content-r4/delivery-review.json`）、
最终模拟检查（历史附件，当前仓库未附：`evidence/mixed-20261006-content-r4/offline-content-tests-final/review.json`）。
新ARM编译/API调用、Host实际内容读回及板端捕获均待验证；不称根因已定位或三样本已修复。
现在仅[MIXED-CONTENT-R4-COMMANDS.md A](MIXED-CONTENT-R4-COMMANDS.md)最终包交叉编译，构建核验后按新身份逐阶段推进。
