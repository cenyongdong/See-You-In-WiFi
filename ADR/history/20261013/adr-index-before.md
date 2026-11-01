# 整理前历史文档快照

2026-10-13迁存。以下所有“当前”“待执行”均是原阶段描述，请勿用于判定今日状态；相对文档链接已按新位置调整。最新入口为根目录PROJECT-PROGRESS.md或DIFFICULTIES.md。

# 架构决策与难点归档

最新：[ADR_45](../../../ADR/ADR_45.md)端到端演示整合及启动/初始化修正；三窗口和60窗口真实CSI→PS/NPU→VPU→主机GUI通过，旧坏读排查暂停。[TechDetails.md](../../../ADR/TechDetails.md)汇总项目技术实现、算子适配、数据/视频流和实测限制；[结果](../../../ADR/../tools/pose-v1/DEMO-RESULTS-20261011.md)。以下当前为历史。

最新：[ADR_44](../../../ADR/ADR_44.md)目录预建通过，on inv94 DATA96全同上一B/四晚物理源正确；并发数值根因未修。[结果](../../../ADR/../tools/pose-v1/PRODUCER-PREPARED-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/PRODUCER-PREPARED-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_43](../../../ADR/ADR_43.md)单调用租约与Host read过；有VPU目录等待在前向前超截止，物理两轮源read未触发，根因未修。[结果](../../../ADR/../tools/pose-v1/PRODUCER-SOURCE-READ-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/PRODUCER-SOURCE-READ-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_42](../../../ADR/ADR_42.md)公开SDK高地址独立组：四调用/off100通过，有VPUinv49首次DATA800逐位前帧，INDEX正确，责任未证；[结果](../../../ADR/../tools/pose-v1/PRODUCER-ADDRESS-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/PRODUCER-ADDRESS-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_41](../../../ADR/ADR_41.md)reset前分段与绝对时隙，off/on各100／2352000 FP32及307 NoInput视频通过，旧尖峰未复现、正式坏读未修；[结果](../../../ADR/../tools/pose-v1/PRODUCER-PHASE-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/PRODUCER-PHASE-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_40](../../../ADR/ADR_40.md)独立生产者／VPU对照：off100通过，on82次数据正确后时隙失败，reset前1.764秒空档待分解；正式坏读未修。[结果](../../../ADR/../tools/pose-v1/PRODUCER-VPU-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/PRODUCER-VPU-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_39](../../../ADR/ADR_39.md)独立真实19成员四调用：47040 FP32逐位／0→11／SDK块释放通过；mock能力假设以Host CPTR和真实临时区门检修正，旧失败保留，正式并发根因未修。以下当前为历史。

最新：[ADR_38](../../../ADR/ADR_38.md)原19成员真实RAW、受限独立参考与mock部署；23520 FP32参考和0→11模拟范围通过，物理NPU首次读未验证，根因未修。以下当前为历史。

最新：[ADR_37](../../../ADR/ADR_37.md)生产者完成契约、零指令Cast与官方日志核验。确认条件copy与非OCM部署地址，实际触发/DDR语义未证；[结果](../../../ADR/../tools/pose-v1/PRODUCER-CONTRACT-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/PRODUCER-CONTRACT-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_36](../../../ADR/ADR_36.md)匹配AXI／UDMA读取责任边界与独立双模式对照，400动态对及455合成VPU图像通过；无NPU生产，模型根因未修。[结果](../../../ADR/../tools/pose-v1/AXI-READ-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/AXI-READ-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_35](../../../ADR/ADR_35.md)首次复制返回／CPU前拥有快照与集成链接门禁；48正确后192的592坏值在第一快照已存在、全同前输入偏移、两晚源正确，共享读取暂存／完成责任待证。[结果](../../../ADR/../tools/pose-v1/READ-PHASE-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/READ-PHASE-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_34](../../../ADR/ADR_34.md)原Gather／ZG公开生产边界已实测；Host／四窗通过，高负载55正确后192初始Host坏、两晚源正确，首次read／暂存责任待定位。[结果](../../../ADR/../tools/pose-v1/UPSTREAM-BOUNDARY-RESULTS-20261011.md)／[下一](../../../ADR/../tools/pose-v1/UPSTREAM-BOUNDARY-NEXT-20261011.md)。以下当前为历史。

最新：[ADR_33](../../../ADR/ADR_33.md)最终门检两轮晚源与实际坏输入NumPy验证、上游边界待查；[ADR_13](../../../ADR/ADR_13.md)save-only实测已解决汇总阻断。[本轮结果](../../../ADR/../tools/pose-v1/FINAL-EVIDENCE-RESULTS-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_31](../../../ADR/ADR_31.md)显示/TCP/RTSP组合；[ADR_32](../../../ADR/ADR_32.md)发送时钟/能力测量；[ADR_33](../../../ADR/ADR_33.md)582有限更新输入失配与最终输出门检取证缺口。[结果](../../../ADR/../tools/pose-v1/COMBINED-READ-RESULTS-20261010.md)。 以下当前为历史。

当前：[ADR_30](../../../ADR/ADR_30.md)公开read自有Host输入桥，真实画面107有限通过；根因／长期待验。[结果](../../../ADR/../tools/pose-v1/INPUT-READ-RESULTS-20261010.md)。

2026-10-10当前：[ADR_29](../../../ADR/ADR_29.md)新增真实拥有画面决策及192坏值复发证据；Native／ARM过，20前向和视频前缀过，103未过。暂停，下一仅读恢复点并审计公共搬运路径，[入口](../../../ADR/../tools/pose-v1/RESUME-PICTURE-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_28](../../../ADR/ADR_28.md)独立记录单VPU／单Engine跨三窗与103的107调用编排及诊断上限问题，Native／ARM／完整数值／518合成码流通过。首次启动与长期可靠性分开，旧模型坏块根因仍待；[结果](../../../ADR/../tools/pose-v1/RESIDENT-SEQUENCE-RESULTS-20261010.md)／[下一](../../../ADR/../tools/pose-v1/RESIDENT-SEQUENCE-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_27](../../../ADR/ADR_27.md)同ELF模型／合成VPU对照：前三阶段通过，末次固件512KiB申请失败、Engine未创建。规整后仍失败，补充[ADR_02](../../../ADR/ADR_02.md)同决策结果，不认定模型坏块根因或稳定并发103通过。[结果](../../../ADR/../tools/pose-v1/MODEL-VPU-RESULTS-20261010.md)／[下一](../../../ADR/../tools/pose-v1/MODEL-VPU-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_26](../../../ADR/ADR_26.md)独立记录实际混合模型移除视频负载的三窗／103通过，源地址同旧失败但坏块未复现、根因未修；无VPU／显示／网络、规整0。下一同身份模型／合成VPU单因素设计仅准备。[结果](../../../ADR/../tools/pose-v1/MODEL-ONLY-RESULTS-20261010.md)／[方案](../../../ADR/../tools/pose-v1/MODEL-ONLY-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_25](../../../ADR/ADR_25.md)独立记录公开分配器与合法较高源位置：96MiB SDK占位不访问数据，动态100／VPU100对正确、自有块归还，模型根因仍未修。原数学／模型／SDK／BOOT保持，规整0；[结果](../../../ADR/../tools/pose-v1/PLDDR-POSITION-RESULTS-20261010.md)／[下一原Engine无视频有限对照](../../../ADR/../tools/pose-v1/PLDDR-POSITION-NEXT-20261010.md)仅准备。以下当前为历史。

2026-10-10当前：[ADR_24](../../../ADR/ADR_24.md)独立记录真实类型／连续动态数据／VPU搬运三阶段全部通过及其范围。低位SDK自有源没有复现模型坏块，较高来源／NPU生产差别仍待；规整为资源准备，原失败保持。[结果](../../../ADR/../tools/pose-v1/TYPED-SCRATCH-RESULTS-20261010.md)／[下一公开源位置方案](../../../ADR/../tools/pose-v1/TYPED-SCRATCH-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_23](../../../ADR/ADR_23.md)独立记录真实模型复制对象／dtype／范围取证。新Host／三窗通过，inv72的192残留128非整数／7坏段复发；同copy对象和合法范围稳定、晚源正确，未根因修复。[结果](../../../ADR/../tools/pose-v1/TENSOR-IDENTITY-RESULTS-20261010.md)／[下一类型／动态模式对照](../../../ADR/../tools/pose-v1/TENSOR-IDENTITY-NEXT-20261010.md)。以下当前为历史。

2026-10-10当前：[ADR_22](../../../ADR/ADR_22.md)独立记录SDK-owned双源搬运与编码并发判别。100对无VPU＋100对VPU全部正确、200合成图像／实际PTS通过；模型坏块未复现、根因未修。原Host107明确身份复用、部分复制异常保存补齐，下一真实模型对象身份仅准备。[结果](../../../ADR/../tools/pose-v1/SCRATCH-COPY-RESULTS-20261010.md)／[下一方案](../../../ADR/../tools/pose-v1/SCRATCH-COPY-NEXT-20261010.md)。以下当前／最新为历史。

2026-10-09当前：新建[ADR_21](../../../ADR/ADR_21.md)记录192生产完成观测与连续搬运残留判别，不挤入旧ADR。失败时8计数全234、55坏段同前次数据复制，wait-to234不作为默认修正。[本批结果](../../../ADR/../tools/pose-v1/PRODUCER-COUNT-RESULTS-20261009.md)／[下一受控搬运设计](../../../ADR/../tools/pose-v1/PRODUCER-COUNT-NEXT-20261009.md)。

2026-10-09最新：同一决策[ADR_20](../../../ADR/ADR_20.md)补充单帧取证／独立落盘实际接入与新103第12调用192失败证据；未另起重复ADR。保存缺口已修补，496坏索引18段同前次复制同偏移、晚源正确，数值根因继续待。[结果](../../../ADR/../tools/pose-v1/INVOCATION-GUARD-RESULTS-20261009.md)／[下一方案](../../../ADR/../tools/pose-v1/INVOCATION-GUARD-NEXT-20261009.md)。

2026-10-09最新[ADR_20](../../../ADR/ADR_20.md)：独立第2轮有限姿态失配与保存再比较耦合；完整异常保留、第三轮停止。SDK-free Frame/独立flush Native/ARM验证通过，尚未集成，根因及638之外的读取边界继续待。[当前结果](../../../ADR/../tools/pose-v1/STARTUP-GUARD-RESULTS-20261009.md)。

2026-10-09最新[ADR_19](../../../ADR/ADR_19.md)：原复制后Host拥有快照、元数据/FP32对齐与582生产组完成检查；Host/三窗/新103全部数值视频通过。107次新查询初始638、没有额外等待，根因及永久修复未证；旧[ADR_17](../../../ADR/ADR_17.md)同问题更新并保留NaN/坏块/晚源。原103失败的[ADR_18](../../../ADR/ADR_18.md)保留，不改写历史。后续首次启动/长期/真实映射与一致性仍待。

2026-10-09新增[ADR_18](../../../ADR/ADR_18.md)：103全边界、稀疏ARM/完整Native参考及失败前缀验收边界；[ADR_17](../../../ADR/ADR_17.md)补首次真实设备源正确/Host暂存异常事实。103尚未通过，不回写旧数据/性能为成功。

2026-10-09同决策后续：ADR_16补充32次纯计时/有限输入节拍，ADR_17补充长期保留异常读回及66次全链覆盖。旧坏值/尖峰原因未证，未另建重复ADR。[当前结果](../../../ADR/../tools/pose-v1/SOURCE-COVERAGE-RESULTS-20261009.md)。

2026-10-08整理，从平台到应用依赖顺序阅读。新主题使用新编号；同一决策的后续实测更新其对应文件。原报告、失败现场和历史决定保留，本文档不替代其原始证据。

| 顺序 | 文档 | 范围与当前状态 |
| --- | --- | --- |
| 1 | [ADR_00](../../../ADR/ADR_00.md) | PS主导回放首版、固定2024模型、双路显示目标；HDMI实际配套仍待验证 |
| 2 | [ADR_03](../../../ADR/ADR_03.md) | FPGA工具/IP交接、启动介质、运行环境、构建与证据链 |
| 3 | [ADR_04](../../../ADR/ADR_04.md) | 训练旁支、CSI预处理、ONNX参考和数值验收边界 |
| 4 | [ADR_05](../../../ADR/ADR_05.md) | CPU注册、受限布局适配、SDK搬运、融合追溯与跨帧完成协议 |
| 5 | [ADR_01](../../../ADR/ADR_01.md) | 首版明确复制的性能困境与优化后置决定 |
| 6 | [ADR_06](../../../ADR/ADR_06.md) | 单时钟定位、消息开销、应用协议、绘图与集成隔离 |
| 7 | [ADR_07](../../../ADR/ADR_07.md) | VPU格式/cookie、RTSP参数集/时钟/保活与HDMI缺口 |
| 8 | [ADR_02](../../../ADR/ADR_02.md) | 普通高阶页分配、双缓冲、有限常驻、队列和Engine线程归属实测 |
| 9 | [ADR_08](../../../ADR/ADR_08.md) | 高内聚低耦合原则及下一在线AU桥的模块契约，实施中 |
| 10 | [ADR_09](../../../ADR/ADR_09.md) | 首轮27窗客户端晚加入、就绪协同与完整来源覆盖，修正通过 |
| 11 | [ADR_10](../../../ADR/ADR_10.md) | 慢客户端发送错误与有界TCP候选，独立正负门检通过，r2未接入 |
| 12 | [ADR_11](../../../ADR/ADR_11.md) | 既有完整CSI接收模块与受保护视频输出隔离接入；guarded已回归，TCP门检中 |
| 13 | [ADR_12](../../../ADR/ADR_12.md) | TCP与视频并行下第六窗口输出回归失配，失败结果捕获与原因待验证 |
| 14 | [ADR_13](../../../ADR/ADR_13.md) | 保存优先及一次规整后32完整全链通过，旧失配原因/永久CMA可靠性未证 |

| 15 | [ADR_14](../../../ADR/ADR_14.md) | 整机单时钟计量、身份分离和覆盖统计；4.22Hz未达标，显示线程候选及首启动条件待验证 |

| 16 | [ADR_15](../../../ADR/ADR_15.md) | 实际独立显示子进程/拥有值IPC/回收通过；4.99165Hz严格5Hz和尖峰/可靠性待验 |
| 17 | [ADR_16](../../../ADR/ADR_16.md) | 前向尖峰单钟取证与103请求有界扩展，尖峰原因仍待 |
| 18 | [ADR_17](../../../ADR/ADR_17.md) | CPU暂存周期坏块/NaN与两轮晚源正确，异常取证长期保留，根因未证 |
| 19 | [ADR_18](../../../ADR/ADR_18.md) | 103边界、稀疏ARM及完整Native参考，旧第61次失败保留 |
| 20 | [ADR_19](../../../ADR/ADR_19.md) | Host复制快照/元数据与582完成检查；新103完整通过，未观察到额外等待 |
| 21 | [ADR_20](../../../ADR/ADR_20.md) | 有限姿态失配与证据保存耦合；Frame/独立flush测试通过，集成待 |
| 22 | [ADR_21](../../../ADR/ADR_21.md) | 192生产计数234时仍残留；完整保存，wait-to234不作为默认修正 |
| 23 | [ADR_22](../../../ADR/ADR_22.md) | SDK拥有同长度／64对齐scratch及编码并发通过；模型对象差别和坏块根因待证 |
| 24 | [ADR_23](../../../ADR/ADR_23.md) | 真实复制对象／dtype／范围稳定仍残留；完整8项保存，下一受控类型／动态模式准备 |
| 25 | [ADR_24](../../../ADR/ADR_24.md) | 真实类型静态／动态／动态＋VPU自有低位源搬运通过；实际来源位置／NPU生产与根因待证 |

[难点索引](../../../ADR/../DIFFICULTIES.md)提供问题入口；[Done](../../../ADR/../Done.md)保留按日期的实现和验证记录；[进度](../../../ADR/../PROJECT-PROGRESS.md)区分工程估算和实际验收。

[ADR_ToBeDiscussed](../../../ADR/ADR_ToBeDiscussed.md)是待讨论的硬件优化构想，不是已采纳决定。其0.1ms、30–50fps和“消除157ms”等估计没有实测证明；桥等待不能全部归因于TopK或ScatterND计算，核心5.25Hz也不是整机吞吐。保留草案原文，不据此修改IP、模型或BOOT。

历史定位：[ADR_16](../../../ADR/ADR_16.md)：前向尖峰单钟取证与103请求有界扩展契约；结果待当前板测。

历史难点：[ADR_17](../../../ADR/ADR_17.md)：TopK188周期性128字节块异常，Host捕获已验证，源／复制／写入者待区分。
