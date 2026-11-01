# 最终输出门检取证

 COMBINED-READ-NEXT。本批新增独立 final_source_recorder（SDK 无关拥有值）、final_source_sdk（公开 Tensor 句柄和 read）、owned_result_save（序列化无数学门检）及两个契约测试；仅隔离 final_evidence_check/bridge 使用。旧 combined-read 和全部原模块不改。

每帧主线程清除旧句柄，保留582/649四份读后 Host 值共67200字节及公开源句柄，保留437/582三份 CPU 写回前值17600字节。最终输出比较失败时，先通知所有工作线程停止，再于 Engine 存活且无下一次前向/reset 的条件下预分配两轮共134400字节，调用公开 read。读取失败保留已完成轮次、原错误和独立取证错误；不继续未完成读取。晚源可能被后续层复用，不能直接认定为原生产时刻值。

每次返回值先保存完整 input/scores/poses/raw 和身份，再执行冻结严格比较；退出阶段遍历所有拥有记录保存 root result、时钟与索引，不重复 oracle。原计算异常、非有限/索引拒绝、帧完成协议不放宽。新增持有句柄、Host 副本及保存 I/O 可能改变时序，本批不作性能验收。

Native 拥有字节/线程/两轮/部分失败/清除/原始失配保存 → ARM 同契约和真实图 Host read → Host107/12注册/59600FP32 → 原三窗重复4次 → 新目录一次 QPC5.05固定103输入诊断。三窗仍2Hz；不调频、不重跑旧fps505。Host420秒、硬件180秒、编码最多1000；按自主规整权限记录资源准备。异常取全证停止，不复位、清缓存、重启或修改SDK/模型/RAW/BOOT/CMA。

当前 Native 已通过，r1因SDK测试缩进Werror停止，r2修正并加强晚存储身份检查，交叉编译正在执行；设备和数学稳定性尚未通过本批。恢复点 evidence/final-evidence-20261010-r2/in-progress-checkpoint.json。
