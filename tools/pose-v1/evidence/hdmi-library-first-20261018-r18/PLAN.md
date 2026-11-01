# r18 单次加载顺序对照（执行完成，已回原BOOT、关闭）

实际1次候选、1次PL按键、1次回退，Open为0；Open前故障复现、按键后采样被拒绝，详见[REPORT.md](REPORT.md)。以下保留批准范围。

同r9 BOOT a0fe608b…61fb00，FPGA不重编；仅更换无SDK依赖的观测父进程，为其增加--library-first入口。新父进程已在FPAI／AArch64 GCC9.4以-Wall -Wextra -Werror构建通过，ELF依赖不含SDK；SDK子进程沿用r16实板验证的同一二进制。Windows工作目录D:/FPGACompetitionProject，执行目标root@192.168.126.49，包内完整参数见deploy/config.json。

请求1次候选安装／启动，SSH恢复后先还原原BOOT文件并完整读回。首次/dev/mem及CSR访问之前先启动SDK子进程、等待库加载READY，尚不调用显式Open；随后首段固定CSR 0→2，健康才允许本启动至多一次Open，继续Open后空闲与关闭／卸载观测（至8）。SDK异常或代次／身份／逻辑错误停止，不重试。故障原值先完整保存，进程软监控而非超时杀死。

只有捕获同类“Open前、六路AR/R均0、HP2及HDMI已RVALID”的有效快照，且子进程已退出、无设备占用，才请求按PL_KEY2／SW7一次约0.5秒松开；确认后仅用无SDK程序采严格复位后0→2作对照，不再Open。本包最多一次按键；未复现则不按键。结束最多一次原BOOT回退、独立核验关闭。需新增明确许可，r17次数已关闭，不借用旧包。

不做DMA、模型推理、HDMI START／长期显示或文件系统修复，旧DATA仍暂停；固定SDK／模型／数学／频率／帧协议保持。原BOOT及候选身份复用保护清单，板端安装前检查当前原BOOT运行、九启动文件、六SDK、设备owner和串口接收就绪。启动失败保全串口，不重复发重启。

这个对照只测试“SDK先加载、CSR后访问”的复现线索，不声称等同r14所有时序或能单次证明库加载因果。已有r11成功反例；若仍健康，也不能宣布启动稳定性修复。r9看不到ARM前历史，这一限制保持。执行入口execute_until_pause.py，实际按键确认后才可execute_after_reset.py，最后execute_fallback.py；未批准包authorization.active=false，不能执行。
