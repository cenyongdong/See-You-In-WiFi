# ADR_23：真实模型复制对象、类型和拥有字节对齐取证

日期：2026-10-10。状态：获批本批已完成；新Host／三窗全内容通过，唯一103在第73次192坏索引停止，完整对象及原字节保存，根因未修。

## 问题与依据

[ADR_22](ADR_22.md)的固定1D／低位SDK scratch在无VPU与编码并发各100对正确，但模型192索引曾含前一次数据复制同偏移残留，稍后设备源正确。生产计数234不能单独证明DMA／缓存完成。scratch与实际模型的dtype、分布、区域／chunk／源位置和动态生产不同，不能直接认定模型故障修复。

## 采用方案

新SDK-free `tensor_identity_observation` 保存有界元数据，通过独立SDK适配层采集公开对象身份。每个桥输入原copy前／原拥有shadow后记录源／目标Tensor、Region、chunk、Device对象的数值身份，以及指针种类、合法设备地址或Host CPTR身份、offset／capacity／bytes、实际与声明shape／layout／FP32／merged轴及完整valid_mask。对象地址不是物理地址；ADDR/BOTH不解引用，不读取私有偏移。

原wait／copy／192四点公开计数／582638／reset(1)／745／CPU数学、原Gather、SDK／模型／BOOT保持。正常设备数据读取新增0，未加入等待、零拷贝或固定sleep。after-copy记录置于原拥有shadow之后；同copy对象身份变化保存错误行并停止，数据已由既有Frame拥有。8项独立flush使完整结果比较失败不阻断对象、快照、原异常及参考保存。

记录上限2048行／4MiB；模块所有者为主线程。保存前后不要求跨调用对象地址相同，因为合法SDK分配可变化；只比较同copy前后并与原shadow对齐。Native／ARM检查对象变化、设备／声明／范围／目标种类、次序／线程／预算／不可覆盖保存。新主ELF实际重做Host107和原异常两轮源读取，不复用旧主ELF验收。

Host通过后新目录三窗＋重复全内容回归，再一次103有界诊断；完整候选及异常拒绝保持，异常保存停止。VPU原两缓冲／cookie／帧协议、Engine主线程和join后销毁保持。规整如需要按既有自主策略记录；不清缓存／重启／改CMA或BOOT，不重跑旧失败。

## 实施中的难点与修正

r1新增adapter有格式告警，严格selftest因单行if告警停止构建；r2修正adapter但selftest仍同一告警，未板测。r3独立测试源显式加括号，通过-Werror Native17拒绝及ARM交叉编译。旧源、包和失败日志保留；修改仅格式，不放宽检查或编译选项。

主程序ELF `fbf330d73ec34c43c7c2757253115e720ba7dccfd6fc6f54a28c6cbaacb8702d`，manifest `c83773ef0e51aed2b85cdc2128a4549b9188a50c239c5fd2ee2a422ca98387e4`，403载荷／80来源。源码、15SDK头和189厂商文件已核验。实际Native／ARM各17拒绝、部分错误身份行保存通过。

## 解决与验证结果

新主程序实际Host107／12注册／59600 FP32通过，旧47040字节Host异常暂存／94080字节两轮读回和独立保存契约保持。新三窗4前向60400 FP32／489编码459网络全内容通过；4份ARM画面＋warmup逐位Native，64对象记录与32shadow一致。

唯一103前72完整正确1087200 FP32，第73次S51_01_301／inv72／frame100072在GatherElements192因非整数索引退出1，未完整103。失败128值均有限但非整数，7坏段全部同紧邻前次192数据复制同偏移；188及192数据输入正确，索引原shadow、异常暂存和Frame拥有字节一致，两晚设备源94080字节逐位同正确CSI参考。失败192八计数全234；两模型阶段合616计数全234，没有据此加等待。

新对象记录合1222条，失败阶段1158条／579shadow／651原元数据，所有实际／声明shape／layout／FP32／full-valid merged-mask、设备归属／范围和同copy前后身份一致。192两源地址109232128／109285376，源offset0／各容量恰等bytes；共同PL DDR区域但chunk不同、不重叠。两个Host目标亦共同Host区域／不同chunk／不重叠；失败Host地址模64为16／32，仍FP32对齐，说明先前256对齐不是该残留出现的必要条件。只证明本次可见身份和范围，不证明内部DMA中转或物理别名。

八项独立保存全部完成，失败3输入47760字节及29份ARM参考／72份Native重建完好。434捕获图像404网络／70结果来源1946关节仅正确前缀：已完成inv70／71未捕获，3采样尾未出，不记完整视频或正常LAST。73接收／消费、72返回、0覆盖，PC74次send非ACK，连接10053对应停止现场。合76正确1147600 FP32，未性能验收。

两abort STREAMOFF0／子回收256／network source0／Engine join后销毁／内核同／端口释放，代理会话全关闭。规整0、无清缓存／重启／CMA／SDK／模型／BOOT变化；最终MemAvailable749348KiB／CmaFree4228／普通512KiB单位23，仅现场，不作泄漏或永久可靠性证明。

源码格式／取证耦合问题已修正，坏块根因未修。复制前新字符串元数据分配与计时会扰动时序，失败从早前inv3／11移动到72不能当性能提升或稳定性修复。匹配DMA／UDMA定义仍缺证；后续先以真实类型常量scratch控制类型差别，再单独动态模式，保留原始错误和两晚源，不猜寄存器、cache或零拷贝修复。[结果](../tools/pose-v1/TENSOR-IDENTITY-RESULTS-20261010.md)／[下一方案](../tools/pose-v1/TENSOR-IDENTITY-NEXT-20261010.md)／完成审查（历史附件，当前仓库未附：`../tools/pose-v1/evidence/tensor-identity-20261010-r3/completion-review.json`）／恢复点（历史附件，当前仓库未附：`../tools/pose-v1/evidence/tensor-identity-20261010-r3/next-checkpoint.json`）。

本批证据（历史附件，当前仓库未附：`../tools/pose-v1/evidence/tensor-identity-20261010-r3/`）；[获批路线](../tools/pose-v1/SCRATCH-COPY-NEXT-20261010.md)。
