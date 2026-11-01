# r14 启动诊断：复用 r9，区分 BOOT 与 Device::Open

状态：**已执行并关闭。** 第1次候选启动Open前即异常，取消后两组；已完成一次原BOOT回退，剩余额度均0。实际结果见[REPORT](REPORT.md)。HDMI长期验证必须另已确定。

## 当前证据与复位判断

- r12失败时，Open之后、任何本轮DMA之前，HDMI RVALID已经持续异常；64B只经过HC0，不能证明共享HP2健康。r13同一r9位流却完成四档DMA和三窗新推理→HDMI，说明故障跨启动偶发。
- 现有网表证据中，HDMI ARVALID寄存器有INIT=0及复位，互联返回有效位FDRE也有INIT=0和复位连接。因此“完全没有硬件复位”不符合已有结构证据。启动时复位脉冲、时钟可用性、释放顺序及覆盖范围仍未证，复位时序／域问题继续作为候选原因。
- 本轮只读反汇编确认驱动初始化0x50e4c调用SDK基类initAfterRegions；该基类可见setMMUMode(true)和writeReg。reset(int)符号确实存在，但不能据此声称Open必定复位HP2互联；已检查驱动的直接调用中未找到reset(int)调用，间接调用与更上层流程仍未排除。未调用reset或猜测私有寄存器。
- 本轮板端只读核验仍为原BOOT运行，boot_id 4441af42-1b7d-4953-9f59-2adba3b4e7b4；六SDK／九启动文件符合、FPGA operating、owner为空。[原始核验](current-board-audit.json)。

## 实际准备产物

Windows工程 D:/FPGACompetitionProject；原厂Vivado2018.3只读打开原r9已布线DCP进行复位链补查，不综合、不布线、不生成新bit。r9 DCP及BOOT从现存归档恢复后关键身份一致；旧失败和归档不覆盖。

FPAI原有容器／AArch64 GCC／固定Icraft3.39.0，已核对六SDK身份，-Wall -Wextra -Werror交叉编译通过，实际ELF为AArch64且链接原ZG330Backend；六类本地故障测试通过。[构建结果](build/result-r2.json)、[原始测试](build/test-r2.log)。新ELF127920字节，SHA256 5b39b6fdb68f1742bd72a4cc3191a2b8f23e3540c1100d3ccc3176ea802983de。控制器的授权关闭、样本上下界及重复重启预留阻断四项测试通过。实际部署包[deploy-approved.tar](deploy-approved.tar)，批准原文见[授权回执](authorization.json)。

原r9 BOOT仍为a0fe608bb4890f941238b1557f2202987116d1e25669f220fcb4b84fec11fb00，原BOOT为ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef，均7023552字节。只改变诊断软件，不改变SDK、模型、数学、NPU分配或帧协议。

## 请求批准的有界范围

最多3次同一r9候选临时安装／受控启动，最后或首次异常后最多1次原BOOT回退重启。第一组失败则停止后续样本；不用重启反复追求通过。每次SSH恢复后，先恢复原BOOT文件、卸载分区并完整读回；保持旧FAT问题、不修复。串口只接收、记录启动日志，不发送复位或下载命令。

每次只允许一个诊断进程、一次Device::Open，**没有DMA、模型推理、HDMI START或长期显示**。独立MMIO只操作已核实观测CSR 0x400b0400的ARM／FREEZE：

1. Open前20ms，固定代次0→1→2，保存完整104字；若异常，跳过SDK。
2. ARM代次3后执行一次Open，返回后FREEZE为4，覆盖Open过程。异常先保留SDK原错，再尽力保存独立观测；不重开、不重试。若Open导致观测代次清零，保留真实CSR元组，停止，不重新ARM冒充原窗口。
3. Open后20ms，代次4→5→6；健康才读取公开设备身份。
4. 观测正常Device销毁过程，代次6→7→8；该附加窗口区分Open与Close影响。

前后空闲门：有效窗口、flags=0x19、复位异常计数0、六通道无读握手、HDMI RVALID计数0；所有窗口不得出现HDMI RVALID或nonOKAY读响应。Open／Close期间复位计数单独保存，不预设必为0。进程异常、身份变化、观测失效或路径异常保存停止，不运行下组；回退前核验无设备占用。每个命令100ms门限只用于观测CSR；进程25秒为软监测，超时先查看原进程、日志与资源，不销毁健康任务。SSH恢复预算180秒，串口每次最多300秒／4MiB。

## 如何判读

- 故障样本在Open前已经异常：出现于本次Open以前，应查启动／PL-PS初始化链，仍不能单凭此结果归咎BOOT文件。
- Open前健康、覆盖Open的窗口首次异常：异常与Open区间相关；再依据复位计数、代次及端口计数细分，不能直接宣布SDK有错。
- Open窗口健康、随后才异常：考虑延迟状态变化；不能靠加等待宣称修复。
- 三次都健康：只是有限启动样本未复现，不是启动稳定性或长期验收通过，也不自动进入连续推理／HDMI长期验证。

执行入口：板端 /root/hdmi-startup-20261018-r14/startup_board.py；先prepare并把完整原BOOT读回主机独立核验，再写host-backup.json。cycle 1..3依次install→candidate-reboot→restore→probe；只有前一组通过才允许后一组。完成／异常后fallback-reboot，重新只读核验再close。启动命令前的独占预留计数持久化，SSH中断不能重发。恢复状态仍以本包实际日志和boot_id为准，历史计划不是授权。
