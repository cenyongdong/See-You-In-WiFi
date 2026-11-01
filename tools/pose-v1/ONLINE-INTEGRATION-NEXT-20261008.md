# F0-A3真实在线接入入口

最新入口：[保存优先及一次规整完整TCP三/27通过](PRESAVED-RESULTS-20261008.md)、[检查点](evidence/tcp-presaved-20261008-r1/next-checkpoint.json)。旧失配未复现但根因未证，下一低日志整机计量准备，旧恢复/失败记录保留历史。

当前入口已更新：[guarded固化/TCP三窗及未解决项](TCP-INTEGRATION-RESULTS-20261008.md)、[检查点](evidence/tcp-evidence-20261008-r1/next-checkpoint.json)、[恢复方案](TCP-RECOVERY-NEXT-20261008.md)。本文件下面内容为此前批准路线，勿重跑历史门检。

2026-10-08门检后更新：本文件三/27真实串联及guarded独立网络正负验证已完成，见[LIVE结果](LIVE-RESULTS-20261008.md)。首轮晚加入失败及修正保留，正式r2尚未含guarded；当前恢复点`evidence/live-20261008-completion/next-checkpoint.json`。下文为获批实施方案/原门检顺序，不重新执行已完成阶段。

2026-10-08：原授权继续有效；全项目归档先完成，AU模块Native/ARM/网络适配门检已通过。此文件是实施接续入口，不重复索要阶段授权，也不把已记录字节门检充作实时闭环。

## 冻结与新集成边界

保留resident-r6、owned-rtsp-r3、模型/RAW/SDK/BOOT/CPU数学、reset(1)/0→745/Gather/NPU分配、双缓冲/prime2/格式/cookie/Host复制。新独立目标/包/构建/板端目录；不修改成功原型以冒充旧身份。

采用独立编排适配层：Engine仅主线程创建/处理/销毁，在整个测试窗口保持活着；VPU编码线程拥有上下文，capture回调把已经owned的字节/PTS交给AU模块；网络线程只运行online_rtsp。画面容量2 popLatest与AU容量8拒绝背压分别管理。输入源、验证/取证、编排和网络实现各有接口，不包含其他功能.cpp/访问私有状态或复制数学。

## 串行门检

1. 新集成源码静态审查与FPAI构建身份；新程序Host107/12注册/59,600FP32回归，加AU/队列合同。SDK未初始化的门检通过再进入硬件。
2. 真实308/309/310/重复308，同一Engine，VPU先获得actual capture，初始化5秒/60秒界限保持；ready后20秒、整段180秒/最多1000帧。完整input/scores/poses逐位旧参考、Host与ZG回调、实际采样/capture/AU/RTP和decoded_id对应。
3. 初次网络加入需在Engine ready之前完成，客户端接收覆盖四种来源及NoInput；不要只截取启动NoInput100帧就宣布全部新结果通过。以实际新增帧ID/PTS组建立当轮参考，不用旧r6码流替代。
4. 三窗通过再27＋首帧重复2Hz，客户端覆盖全部28调用的画面来源，模型输出逐位旧参考。保留实际PTS，不用预览固定10fps替代网络计量；正常stop生产→VPU drain/LAST→AU EOF→网络清理→Engine同owner释放。
5. 独立有限慢客户端门检：明确AU/发送侧背压及停止，不能随意丢P帧，也不能只凭AU highwater1证明socket缓冲有界。超时/异常完整回传停止，禁止自动重开设备或循环重试。

每阶段核验当前包/程序/BOOT/SDK/日志之后才下一阶段。异常、非有限、不同输入全部相同、来源错配、CMA/身份变化停止，不放宽已有数值或内核门禁。整机计量、真实TCP窗口全流程和长期测试在此后继续原批准路线；HDMI映射未明不写。

## 当前检查点

AU适配门检证据 `evidence/owned-rtsp-20261008-r3/completion-review.json`；没有新VPU/NPU执行、没有后台服务。实际在线集成尚未执行。本机OpenCV环境Python3.8，新审查脚本须兼容；参考NAL哈希可能重复，以首IDR＋顺序＋实际PTS＋解码ID联合定位。
