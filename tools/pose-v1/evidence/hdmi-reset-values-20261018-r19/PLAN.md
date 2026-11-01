# r19 单次补充复位取证（执行完成、已回原BOOT、关闭）

实际1次候选、0次按键、1次回退、1次Open，四段健康未复现；详见[REPORT.md](REPORT.md)。以下保留批准范围。

r18已复现Open前故障，但按键后旧探针因初始状态不满足0而拒绝，未保存具体值，无法判读。已补齐拒绝前的ABI、长度、status/request/response完整记录；原停止条件保持，5类本机测试和AArch64构建通过，详见../hdmi-library-first-20261018-r18/diagnostic-fix/。本包仅替换这个无SDK依赖的纯CSR ELF并将原始stderr补入结构化结果；复用r18其余四个已核验二进制及执行器，不重编FPGA，不改SDK／模型／数学／频率／协议。实际参数见deploy/config.json。

请求最多1次同r9候选启动，SSH恢复后先恢复原BOOT文件并完整读回；SDK先加载，随后首次CSR 0→2。捕获已识别的Open前同类故障则SDK子进程退出、owner为空后，人工按PL_KEY2／SW7一次；实际确认后仅采一次纯CSR：先保存五个初始寄存器原值，若不满足严格0代次，保存并退出，不发命令；若归零才采0→2快照。不重按、不再Open、不重试异常。若前置健康，沿用已准备工具允许至多一次Open及关闭观察，健康也不按键，随后结束。

最终最多1次原BOOT回退并独立核验／关闭。本包没有DMA、推理、HDMI START／长期验证或文件系统修复，旧DATA暂停。候选BOOT仍a0fe608b…61fb00，原BOOT仍ff350477…a68b31ef；安装前核对当前原BOOT运行身份、六SDK／九启动文件、无设备占用与串口只接收就绪。25秒只软监控，正常执行进程不销毁；身份／SDK／逻辑异常停止受影响步骤，不自动重试。源包的预建空挂载目录问题已排除，保留r18原失败，未更改底层BOOT替换流程。

执行入口execute_until_pause.py；按键须实际人工确认，之后execute_after_reset.py；最终execute_fallback.py。授权默认active=false，r18额度已关闭，不能借用旧包。该补充解决记录缺口，不能单独证明物理按键脉冲到达或启动稳定性修复。实际位置Windows D:/FPGACompetitionProject → root@192.168.126.49，所有执行日志与输出留本目录，失败证据不覆盖。
