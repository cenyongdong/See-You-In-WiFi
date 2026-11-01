# 103次低日志有限门检实施

接续。新隔离r2入口保留旧r4源码、模型/RAW/SDK/BOOT、CPU数学、原复制/等待/reset(1)/745和异常Host暂存/两轮SDK读回。父主线程拥有Engine，显示子进程SDK无关，编码/网络线程各自拥有资源，join后再销毁Engine。

当前产物：.local/pose-v1-bounded-load/package-20261009-r2、.local/pose-v1-build/mixed-20261009-bounded-load-r2；程序8510f6e…0f1f3a19/子6d88d03a…e4137d39，403包68来源。r1仅Native命令路径失败，旧目录/日志保留；r2括起PowerShell完整路径，不覆盖失败。

执行均由代理：

1. Build-BoundedLoadR2.ps1：本机FPAI交叉编译/SDK及厂商身份；Native参考工具无SDK/设备。review_bounded_load_r2_stage.py build及review_bounded_contracts.py检查ELF/来源。
2. 新Lite目录/tmp/pose-bounded-load-20261009-r2，run-bounded-load.sh host-check：AU/TCP/保存/IPC拒绝、103/104预算、正常和异常回收、Host107及真实Host异常读回探针。Host程序420秒、预算自检60秒；硬件180秒限制不扩。
3. 独立Host结果全部核验后，预置原三窗客户端，以process-three做三样本＋重复四次回归。核对全部数值；主机Native按实际值重建4张，与ARM参考逐位，再核对本地和真实RTSP。未全过不得上传process-three门检。
4. 全部通过后，预置bounded_load_peer_ready.py，以load-103执行27固定来源循环、103输入、3预热＋100目标计量、5Hz单会话。接收1/显示2/IPC1/AU8不变；worker最多103；30秒就绪期、网络100秒/客户端105秒、整体180秒/编码1000。diag/timing采样/profiling全部关闭，不以延长timeout替代资源边界。
5. 每个实际消费的完整输入/分数/姿态、来源/帧号和实际PTS保存。结束后按首个不同来源、首个重复和末张保存ARM参考，103全消费29张；主机reconstruct_bounded_frames.py生成全部参考，明确均为重建图，不作采样缓冲声明。review_bounded_video.py核对解码来源/关节及误差，review_live_network.py核对全部实际NAL/PTS与本次解码像素逐位。
6. 分别报告实际输入间隔、消费/覆盖/绘图/编码采用/重复、画面完成速率与P95。保留尖峰和全部丢弃，不把理论1/平均耗时或名义发送5Hz当作实测速率，不舍入判过；RTSP交接不是PC呈现。

异常保留并停止，不自动重开、重试、复位/清缓存/修改CMA。规整按当前普通高阶页自主判断且完整记录；当前充足，无需执行。SDK/BOOT身份变化即停止。代码输出和静态媒体先独立通过，不能因exit0提前进入下一阶段。103有限测试不是HDMI/长期/永久首次启动验收；旧坏值和尖峰根因未证。

证据目录tools/pose-v1/evidence/bounded-load-20261009-r2；对应新决策ADR_18，旧数据故障继续ADR_17。完成后记录实际通过和未通过边界，更新Done/检查点。
