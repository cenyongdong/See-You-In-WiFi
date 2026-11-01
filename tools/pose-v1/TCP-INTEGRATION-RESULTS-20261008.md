# Guarded接入与完整CSI网络链路验证结果

当前结论：**guarded正式隔离目标的三/27回归通过；TCP三窗＋重复完整链路通过；TCP27未通过，实际输出失配仍待取证。** 新取证目标已通过Native/ARM契约、构建身份和Host107，但VPU首次启动分配失败阻断了新模型取证。

## 已完成成果

| 身份/门检 | 已核验内容 | 证据 |
| --- | --- | --- |
| guarded集成 f02aceb8…248c6458；403包/36来源 | Host107/12注册/59,600FP32、AU17拒绝/2000通知；32正确前向/483,200输入输出值，977编码/767网络解码，全部来源/实际PTS/像素一致 | `evidence/guarded-live-20261008-r1`，两完整acceptance |
| TCP集成 02697797…6772855；403包/41来源 | Host107和原协议自检通过；两会话的四实际窗口345,728原始字节、完整输入输出逐位旧参考，496编码/376网络帧的来源/PTS/像素通过 | `evidence/tcp-live-20261008-r1-controlled/live-three.acceptance.json` |
| 失败捕获 d7def2de…34f98a47；403包/44来源 | 新层只在原异常后保存拥有值的失败结果再抛出；Native/ARM一正例、有限失配/NaN两负例及原错误/实际字节通过；Host107/59,600值、协议与AU自检保持 | `evidence/tcp-evidence-20261008-r1/host-check.acceptance.json`、`native-contracts-review.json` |

网络只增加策略适配层，guarded源码与原独立正负测试保持同哈希；每TCP连接请求64KiB，Linux实际128KiB，无系统sysctl变化。Engine创建/前向/销毁仍在主线程，保留至编码/网络工作者结束。SDK、CPU数学、模型/RAW、两VPU缓冲/prime2、MMAP cookie、显式复制与reset(1)/0→745保持。

源模块不读取参考预测作为输入。TCP接收器只提供完整拥有的Window；诊断oracle在主线程核对收到的原始CSI和本次实际结果。重复原首帧通过第二会话发送，连接内单调规则保持。输入接收槽容量1、画面槽容量2、AU容量8分别统计。

## 保留失败与修正

1. guarded本机视频审查参数误用目录：修正为JSON文件，在新审查目录通过，没有重跑板测。
2. TCP三窗首次外部等待只处理refused，1秒连接timeout使发送器提前退出；板端0接收/0前向、344启动样本、111项回传/内核同。仅新外部65秒启动等待兼容refused/timeout，新目录同程序/包完整三窗通过。已连接数据流失败不重连。
3. TCP27首次工具启动延迟越过板端5秒输入预算；主机开始连接时服务已退出，0输入/0前向/111项回传。采用主机先PEER_ARMED、实际板端LIVE_READY后向已有进程START放行；等待主机工具的时间发生在板测前，硬件180秒/Engine60秒/ready20秒等预算保持。
4. 修正控制后的TCP27接收到六窗，前五次完整结果正确，第六窗S12_48_349/frame73/invocation5在输出比较处停止。131项回传/内核同，发送端随后因全局停止收到连接终止。标准Engine dump已检查有限性；实际失配幅度、槽位和原因未知。原检查器比较先于保存，未保留错误输出，**没有27验收文件**。
5. 新失败捕获目标首次VPU启动失败，85项回传，0模型前向、没有Engine_created，VPU poll错误/两队列STREAMOFF返回0。内核新增order7、0x10dc0失败，路径`request_firmware_work_func → mvx_mmu_alloc_contiguous_pages → map_protocol_v2 → mvx_fw_factory`。CMA空闲130,604KiB，但失败时512KiB及以上块只有CMA；这是普通连续页资源问题，不能据总空闲量宣布可启动。清理后只读快照有5个Unmovable order7块，不能回写为失败当时状态或自动重试门禁。

全部原失败、原程序与引用保持。[ADR_11](../../ADR/ADR_11.md)记录输入/启动协调，[ADR_12](../../ADR/ADR_12.md)记录实际输出取证，[ADR_02](../../ADR/ADR_02.md)补启动资源适用限制。

## 当前边界与下一步

阶段通过只覆盖上述有限固定窗口；新TCP27、整机5Hz/P95、完整慢客户端清理、HDMI和30分钟未通过。本轮没有规整、清缓存、重启、CMA/BOOT修改或失败后自动重跑；所有板测、主机进程、SSH/SFTP已结束，端口与服务释放。

原27数值验收保留，不将其自动扩展为本次同身份板端失配通过。管理估计83/100保持，不以新增构建/重复门检增加份额。

最新[进度审查](evidence/tcp-evidence-20261008-r1/progress-review.json)、[恢复检查点](evidence/tcp-evidence-20261008-r1/next-checkpoint.json)。先按[TCP恢复计划](TCP-RECOVERY-NEXT-20261008.md)恢复首启动条件并取得失败实际值，完成27回归后才进入[整机有限计量](WHOLE-SYSTEM-NEXT-20261008.md)。
