# r14：首次捕获故障启动的 Open 前异常

2026-10-18，Windows / FPAI / Lite，复用原r9 BOOT，未重编FPGA。**本轮应用尚未调用Device::Open，HP2和HDMI已同时持续RVALID、RREADY=0。** 排查范围已从“Open后首次见异常”前移到“本轮应用Open前已有异常”；启动稳定性尚未修复。

## 实测结果

最多3次候选启动、1次原BOOT回退，首个异常即停止后续样本。实际使用1次候选启动及1次原BOOT回退；后两次取消，本地／板端授权均关闭，所有剩余额度0。SDK Open、DMA、推理、HDMI START及长期验证均0次。

- 候选boot_id：8d0370f4-98ea-4506-8abc-0342a11f7093，SSH恢复87.922秒；恢复后先还原原BOOT文件并卸载、完整读回，才运行独立CSR探针。
- Open前固定代次0→1→2，完整104字已保存。200MHz窗口5,016,168周期，即25.08084ms；flags=0x19，窗口内复位异常计数0。六路AR／R握手均0；HDMI和PS HP2两端的RVALID、RVALID&&!RREADY均覆盖全部5,016,168周期。
- 当前引脚：HDMI ARVALID=0、ARREADY=1、RVALID=1、RREADY=0、RID=0、RRESP=OKAY、RLAST=0；PS HP2同样背压，RID=0x20（6位ID的来源位5为1，指向S01/HDMI）。当前引脚值不是被接受的事务台账，不能据此断定数据内容或历史事务是否合法。
- 前置门拒绝，探针exit72，耗时0.253312秒；stderr明确Device::Open skipped。Open中／后及Close窗口均未执行。未重试失败负载。
- 原BOOT运行回退SSH恢复27.172秒，最终boot_id 30ed1321-b37a-4655-b172-ab8551e6124e；原BOOT文件、六SDK／九启动文件符合，FPGA operating、owner为空，两个串口捕获均已关闭、TX=0。本批无残留板端进程。

原值与独立复核：[review.json](review.json)、[板端完整原值](returned-trace.jsonl)、[原始stderr](returned-stderr.log)、[最终审计](final-audit.json)、[完整回传](evidence-final.tar)、[执行日志](execution.log)。串口候选／回退各37,075／36,955字节，分别在uart-candidate-1和uart-original-fallback；只接收，无复位输入。已查rc.local及启用服务，没有发现AI应用启动项；这不是从上电到采样期间所有进程行为的完整证明。

## 对“是不是没有硬件复位”的判断

“完全没有接复位”与实际网表不符。只读打开原r9已布线DCP，确认S00／S01／M00及互联共用proc_sys_reset_1的peripheral_aresetn；HDMI返回有效位m_valid_i_reg是FDRE、INIT=0，R端通过反相的流水化复位驱动；时钟来自MIG UI BUFG。HDMI ARVALID对应实际FSM寄存器，已有前轮INIT／清零核验。[本轮网表原值](reset-netlist.txt)、[原生日志](reset-netlist.vivado.log)，native exit0，未修改设计／约束。

保留的r9实际构建源进一步显示：proc_sys_reset_1的dcm_locked接常1；外复位为reset_n & soft_rst_n，其中reset_n=sys_rst_n & FCLK_RESET0_N；HC／HDMI的hp_clk_rst经过另一条双寄存器链，HDMI mem_resetn=~hp_clk_rst。MIG ui_clk_sync_rst在该复位释放链中未参与，ddr3_init_done也未直接作为该互联复位的释放条件。**这些是需要检查的时钟就绪／复位覆盖疑点，不是已经证明的缺陷或修复方案。** 不依据Xilinx通用假设改复旦微适配设计，也不直接改库或重编。

本轮证据支持：当前应用的Open不是此次异常产生的必要条件；应优先查BOOT／FSBL到Linux之前的PS-PL初始化、HP2返回状态及复位时序。它不能证明BOOT文件损坏、完全没发生复位、互联一定错路由，或早于ARM时从未产生过请求。窗口内复位计数0，只表示窗口内没捕获异常，不能证明启动复位执行正确。PS内部返回状态、互联及HDMI的覆盖范围是否一致仍未知。

注意：r14探针虽未调用Device::Open，ELF仍链接SDK；所以这一步仅排除显式Open为必要条件，尚未独立排除SDK库加载的静态初始化。已核验r15所用旧独立CSR ELF的DT_NEEDED仅标准C/C++运行库，无Icraft／驱动SDK，后续对照消除此混杂因素。原始依赖见[preopen-ELF.txt](preopen-ELF.txt)。

## 后续边界

不再调整Open后的等待来掩盖本次前置故障；不重试4KiB，不进入连续推理和HDMI长期验证。下一诊断应能区分“异常在HP2启动时产生”与“已有返回状态未被统一复位”，并覆盖ARM以前的初始化历史。任何新的BOOT／重启、启动配置修改或硬件复位实验另按具体包讨论；旧DATA仍独立暂停，FAT不修。HDMI长期验证须单独明确批准。

## 本轮方法与耗时

新增独立MMIO Open区间探针、6类故障测试、固定代次及原错优先保存，交叉编译和4类控制器门检通过；异常启动实际只消费Open前窗口。新增诊断软件不改SDK／模型／数学／协议。准备过程与实际包见[PLAN](PLAN.md)、build/execution.json、build/result-r2.json；不把准备通过写成板端全窗口通过。

只读Vivado查询是本轮离线主要等待：19:14启动，19:40报告退出；原生open_checkpoint墙钟7分20秒、CPU43秒，前面还有工具冷启动／加载等待。跨采样CPU、内存和阶段日志在推进，因此持续监测原进程，没有杀进程重开，也没有重做综合或实现。该耗时不等于综合／布局布线耗时。受控上板主要墙钟为两次SSH恢复及文件恢复核验；实际探针仅0.253秒。

## 已准备、未执行的r15复位对照

实际包[next-reset.tar](next-reset.tar)，授权默认关闭；仅复用同一r9 BOOT和r13已核验的独立ai_preopen_monitor（不链接调用Device::Open）。控制器已通过语法及4类边界测试（授权关闭、第二候选、重复按键记录、PS boot_id变化均拒绝），BOOT保护／完整读回沿用r14；未部署、未按键、未启动。

请求范围：一次同r9候选临时安装／启动，SSH恢复后先完整还原原BOOT文件，先保存Open前原值。若前置状态健康，结果为未复现，不按键、不做其它负载，直接回退；若确有同类前置故障，在无设备占用、没有SDK／DMA／帧分配时，人工仅按PL_KEY2／SW7一次（约0.5秒后松开），代理停止MMIO访问直至人工确认松开。按键是F8的高有效PL复位输入，已核原理图／引脚契约，**不是PS复位或电源按钮**。[实际引脚资料](../../../../FPGA/hdmi_candidate/PIN-CONTRACT.md)。

人工确认后、等待约1秒，再采集一次严格代次0→1→2快照；要求boot_id未变、观测代次确已被复位到0、完整104字保存。若代次没复位、ABI／身份不符、观察窗口不健康或原值异常，保存停止，不重按、不重试。该动作也会复位MIG及HC／HDMI并使PL DDR重新初始化，因此只允许在上述无负载状态，不能在推理中使用；不能将CSR代次归零当作PS HP2内部也已复位的证明。

无论比较结果如何，完成最多一次原BOOT回退并核验、关闭。SDK Open、DMA、推理、HDMI START及长期验证均不包含。若硬件PL复位后故障清除，只能支持稳定时钟条件下的复位／重新初始化改变了故障状态，仍不等于自动启动稳定性已解决；若保留，则继续查PS HP2内部状态与更早的启动事务。该包须另获明确批准及在场，r14余下次数不会复活。
