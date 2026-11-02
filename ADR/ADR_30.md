# ADR_30：公开 Tensor::read 直写自有 Host 输入暂存

2026-10-10。状态：公开read候选真实拥有画面107有限门检通过；底层根因、组合与长期可靠性待验证。

## 现象与边界

ADR_29 的真实画面第21次调用在192索引出现144个有限非整数；8坏段等于同次前一个输入复制内容，两轮晚源正确。索引目标已64字节对齐，layerCount始终234。这些证据不证明瞬时源、DMA完成或具体写入者，也不支持靠对齐或计数等待修复。

## 决策

匹配3.39.0头文件的公开签名为 `Tensor::read(char*,uint64_t,uint64_t) const`；`data()` 是张量起点，offset只用于容量检查，不重复加偏移。独立模块只接受匹配dtype、合法范围、自有Host CPTR且不与源共chunk的目标。保留原输入wait、所有权/布局检查、异常Host快照与两晚源，设备输入改用源read直写该目标；Host输入与输出copyFrom保持。单独目标不替换旧桥、旧程序或修改SDK/模型/BOOT。

read与copy共享设备region入口，区别在cross-region临时目标及写回链路；不是零拷贝、显式DMA fence或已证根因修复。源码封装契约、SDK适配及桥接，禁止直接解引用ADDR/BOTH。

## 验证顺序与停止

Native拥有内存/边界/异常契约→ARM公开Host read真实192两规格47040字节及11拒绝→新桥Host107/12注册/22输出59600值→新身份一次单VPU实际capture后主线程单Engine，原三窗重复4次→2Hz103。保留真实渲染/拥有NV12/10fps/容量2/180秒/首capture5秒/初始化60秒及异常完整保存。任何异常停止，旧失败不重跑；自主规整只作有记录资源准备，保持CMA/BOOT，不清缓存。完整画面与视频主机独立核验，不把前缀通过当107通过。

## 解决与实测结果

隔离程序70c9df9f…ae2082d／manifest dbf88b3f…ad37d06f，403载荷126来源。原118来源冻结，桥逆替换新增include及输入调用后逐字符等于原桥；旧主程序仍fbf330d7…acb8702d。Native read8拒绝、16守护字节及异常原文通过；ARM相同8拒绝加SDK Host真实192两规格47040字节／3拒绝过。新桥实际Host107／12注册／22输出59600FP32全通过。

无规整的新目录首次capture成功，单VPU→主线程同一Engine初始化29.30360秒，原4＋103共107／1615700FP32逐位旧参考；旧失败S23_30_330在inv20／47／74／101全部正确。1712对象／856shadow和856查询＋963元数据稳定，未放宽非整数门禁。这个有限结果支持选择公开read作为下一组合候选，不能宣称共享底层read路径或具体写入者已修复。

107实际拥有画面全采用、容量2水位1／覆盖0；108NV12共149299200字节逐位Native；824编码／归还／解码，298启动NoInput＋107新结果＋419重复，实际PTS／帧标记／7364关节过。正常drain／LAST／两STREAMOFF、join后Engine释放、七项保存、内核同，程序和SSH／SCP均结束。视频SHA510b11f3…2cdd825；有损RGB诊断不当逐位RGB、MPJPE或标定。

准备普通高阶29、规整0；编码进入75／raw后73／capture后65是不同时间资源快照，最终746760KiB可用／CmaFree18744／普通23，仅现场。没有清缓存／重启／CMA／BOOT／SDK改变。tar mtime警告来自两端日历时间差，以哈希／内容／steady_clock核验，未修改时钟。

下一独立组合显示子进程／TCP／owned AU，再有界整机5Hz；当前不是RTSP、HDMI、30分钟、任意碎片首次启动或零拷贝通过。原失败证据、Host坏值及两晚源采集保持，不以成功覆盖失败。

[结果报告](../tools/pose-v1/INPUT-READ-RESULTS-20261010.md)、[后续方案](../tools/pose-v1/INPUT-READ-NEXT-20261010.md)、完整证据（历史附件，当前仓库未附：`../tools/pose-v1/evidence/input-read-20261010-r1/completion-review.json`）、恢复点（历史附件，当前仓库未附：`../tools/pose-v1/evidence/input-read-20261010-r1/next-checkpoint.json`）。

## 后续限制更新

同一read模块回接显示/TCP/RTSP后，2Hz103和名义5Hz103完整内容通过；明确5.05Hz的独立新目录第34返回出现582更新数据及最终姿态128有限值不同。原有限通过记录不变，read路径不足保证更高负载正确，不能替代底层生产／同步／写回调查。最新依据[ADR_33](ADR_33.md)与[组合结果](../tools/pose-v1/COMBINED-READ-RESULTS-20261010.md)。
