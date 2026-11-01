# mixed-r1 SDK设备内存往返验收（2026-10-06）

## 工程内容总结

完成一次30秒受限memory-check并回传，代理核对完整日志及逐份FP32模式。
device=25122301、icore=FMSHZGV3TECH-AID - 24160628，URL为已核验AXI NPU0x40000000/DMA0x80000000。
SDK初始化成功；固定ARM Icraft/CustomOp3.39.0、15SDK头文件、Host/ZG库、程序及上一offline验收身份匹配。
原包290项、完整回传28项哈希通过，ldd无缺依赖。

两缓冲区均allocated=true，bytes/chunk_bytes=16,384、offset=0、pointer=ADDR，
实际region类型均AXIZG330AIPLDDRMemRegionNode。固定程序核对SDK默认区域归属、非Host区域及两个数值地址不重叠；
没有输出绝对地址，本报告不声明另行核验完整地址映射，也未直接解引用ADDR。
通过Tensor.copyFrom在Host CPTR和SDK分配的设备内存间往返，三套模式/六份回传各4,096 FP32，
共24,576个值全有限、逐位一致、最大差0，第一元素-0/+0符号位也保持。

退出0、stderr空，stages started→opening_device_not_readonly→sdk_memory_roundtrip_completed_not_NPU_coherence_proof。
mode=memory-check/device_init_allowed=true；原始stdout保留SDK初始化日志及板端时钟，不自动校时。
完整dmesg前后相同，无新增内核消息；available前后均687MiB、Swap0，仅前后快照。
本阶段未创建完整模型Session、运行RAW模型前向、读取NPU模型输出或访问HDMI。
代理仅文件分析，未连接板端、代执行、重跑/复位或修改配置/源码。

证据：[memory-check.acceptance.json](evidence/mixed-20261006-r1/memory-check.acceptance.json)、
[独立数据/区域复核](evidence/mixed-20261006-r1/memory-independent-review.json)，
完整回传evidence/mixed-20261006-r1/memory-check。

## 对后续开发的参考

已证明当前SDK、运行位流及所分配设备数据区域支持本次Host↔设备copyFrom模式往返，可作为Session部署的前置证据。
仍不能把CPU写入再CPU读回当作NPU写入后CPU读取的同步证明，不能据此宣布混合模型、DMA性能或部署精度通过。
下一步仅apply-check：300秒，加载参数、创建/apply Session、检查六Host及1173HardOp绑定，不做forward。
传入memory验收文件后执行一次新目录，完整回传核验后再单样本；BOOT/JTAG保持、无竞争访问等前置条件继续适用。
身份/区域不明、超时/OOM/总线/SDK异常或不可追溯融合绑定则保留证据停止，不自动重试/复位/改模型。
