# ADR_43：单调用公开输出租约与失败后两轮源读证据

日期：2026-10-11。状态：本批完成；租约／Host read与有限数值回归过，VPU准备时隙失败，物理晚源读尚未触发。

## 问题与决策

ADR_42在独立高地址组＋VPU inv49 DATA800有限值逐位前帧，INDEX正确，首次拥有输出已错但局部源句柄已经释放；本批不能重开旧Session追读。新增单调用租约，仅延长实际forward返回公开Tensor的强引用到原比较结束，正常立即归还、下一reset前拒绝活租约；主线程／代次／Session有效性检查。

仅在原保存结果比较失败后执行两轮公开Tensor::read，每轮两实际输出47040字节／共94080，拥有副本／metadata／dtype／计数与同一单钟保存；无直接ADDR/BOTH解引用、额外wait/sleep/reset/forward/源写或cache helper。原错误继续重抛，诊断失败也不覆盖原错，首次文件不修补。租约在worker join和Session销毁前归还；强引用寿命和额外查询会影响时序，不能把未复现称为修复。

先SDK无关范围／溢出／代次／线程／失效／容量／拥有值／正常零读／诊断失败仍原错合同及ARM Host CPTR公开read，再新包四调用、无VPU100回归、有VPU最多100，仍高地址前缀／原Trace／固定5.05Hz／60与180秒门禁，异常停止不重试。

## 解决与验证结果

r2 ELF9772a0e12bfe04807ccff33caa9136e0689f733caa024afa9d9da0ee30853b28。SDK无关租约范围／重叠／代次／线程／失效／拥有值／零正常读／诊断和清理失败仍原错合同在Native／ARM通过；ARM Host CPTR公开Tensor::read八输出188160字节逐位独立参考，没有物理Device／Session。r1因Host检查器缺Network完整头文件编译失败留存；r2补头文件，单独构建后再审计，r1未板测。r1构建失败后误继续审计而产生缺build-result的衍生错误也保留，后续依赖工具分开执行。

四调用47040 FP32、无VPU100／1176000、VPU前49／576240全逐位参考／有限、0→11，合153实际前向1799280 FP32；租约分别4／100／49打开关闭，forced_expired0、source_read_calls0。高地址109113344／109092864、104MiB前缀、owner及原数学／RAW／SDK／BOOT保持。Scope在Session销毁前失效并清除源句柄，prefix1→0／所有块0。

VPU inv49计划200805093543847ns，实际开始200805093627180ns，目录创建915.85662ms／线程CPU0.29944ms／自愿切换2，缺页0；之后Host与journal准备约0.92314ms。原planned+198019801ns截止检查在reset前拒绝，调用未执行reset／forward，没有该次输出文件／trace／late-source，保留B输入及原错误 `Prepared call missed absolute slot; no forward`。这是成功阻止迟到调用的物理门检，不能记on100通过，也未触发物理失败后两轮源读。目录API内等待已定位，不区分文件系统／存储／调度内部原因，更不能回溯解释ADR_42的DATA800失配。

阶段4842事件、显式forward49，异常标记deadline及sdk_call；allocstall／reclaim／OOM／compact／pgmajfault增量全0。VPU225raw／224归还、222ownedpacket41056字节／221 NoInput图像ID0–220解码正确，1340 Q/DQ单线程、98copy全部交叠提交capture跨度非fence。尾四图像未解码，两abort STREAMOFF0，正常drain-LAST未过；join后Session毁／所有资源释放。冻结summary0计数因为abort未返回结果，不当实际无工作。

资源只读普通512KiB单位196→196，本批规整0／无清缓存重启／CMA256MiB保持。阶段及最终内核逐位同、BOOT／SDK／模型同／FPGA operating、程序管理器端口代理连接全结束。最终MemAvailable733520KiB／CmaFree27876KiB只作快照。原152软件、745、正式异常读取保持，管理83/100和103／严格5Hz／长期／HDMI待。

## 后续决策

先移出已定位的逐帧目录创建：新身份在放行前准备空目录，热路径只消费有界拥有目录令牌；实际输入／输出保存及比较仍在原位置，不同时改为全批结束落盘。继续原时隙／有界次数、租约和失败只读；输入／output保存仍可能阻塞，异常照旧停止，不以扩大截止或追帧补通过。物理两轮源读取仍待自然失配实测，不重跑本批失败Session或用晚值修复。

[结果](../tools/pose-v1/PRODUCER-SOURCE-READ-RESULTS-20261011.md)／[下一](../tools/pose-v1/PRODUCER-SOURCE-READ-NEXT-20261011.md)／恢复（历史附件，当前仓库未附：`../tools/pose-v1/evidence/producer-source-read-20261011-r2/next-checkpoint.json`）。
