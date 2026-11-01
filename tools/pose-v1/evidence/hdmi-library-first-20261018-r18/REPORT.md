# r18 加载顺序与PL按键对照结果

2026-10-18，执行位置Windows D:/FPGACompetitionProject → SSH Lite，复用同一r9 BOOT a0fe608b…61fb00，不重编FPGA。上限与实际为：候选启动1／1、条件PL按键1／1、原BOOT回退1／1；显式SDK Open实际0。包已关闭，剩余额度全部0；无DMA、推理、HDMI START或长期验证，旧DATA暂停、FAT不修。

## 实际结果

候选SSH恢复24.125秒，boot_id=9939cbee-0692-406c-a129-bfcf7cc2c659。先恢复原BOOT文件并完整读回，再运行无SDK依赖父进程；SDK子进程先完成库加载READY，之后父进程才首次打开/dev/mem、读取CSR。CSR起始status/request/response=0/0/0，ARM/FREEZE后0/2/2，完整104字已保存。尚未调用显式Device::Open即捕获同类故障：

| 原值 | 本次结果 |
|---|---|
| 观察窗口 | 4,894,421周期＠200MHz，24.472105ms |
| flags／窗口内复位计数 | 0x19／0 |
| 六路AR／R握手 | 全部0／0 |
| HDMI RVALID／RVALID且不READY | 均4,894,421，覆盖整个窗口 |
| HP2 RVALID／RVALID且不READY | 均4,894,421，覆盖整个窗口 |
| 当前HDMI／HP2 RID | 0／0x20，RRESP均0、RLAST均0 |

父进程健康门拒绝后退出71，原文“After-library pre-Open abnormal: Device::Open skipped”；子进程日志无SDK错误、已退出，owner为空。该71来自前置观测拒绝，不是一次Open／DMA的SDK超时。没有重试SDK，也没有进入后续Open。

人工确认“已按一次PL_KEY2／SW7并松开”。按键后PS boot_id未变，独立纯CSR程序0.015395秒退出1，原文“Not a fresh observer: no command issued”；ABI／长度门已过，但初始status/request/response至少一项不满足0。程序未发ARM/FREEZE，也未产生104字快照。**因此没有取得有效的按键后对照，不能判定故障被清除，也不能据此认定复位未到达。** 原探针没有保存这三个初始寄存器的具体值，是本轮诊断缺口；原失败日志保持。

最终原BOOT回退23.782秒，boot_id=4da54744-6eae-420a-a656-efa7403db35c。运行与启动文件均已恢复，六SDK／九启动文件符合、FPGA operating、设备无占用；串口关闭且TX=0。[最终审计](final-audit.json)、[使用次数](fallback-result.json)。

## 已核对及仍未知

本次进一步排除了“必须先调用显式Open才会出现异常”的解释；库加载与BOOT仍不能独立定因。CSR先访问的r17三个样本健康、SDK先加载的本次失败只是顺序线索，仍有r11成功反例；单次对照也改变了时序，不能推断统计因果。ARM前是否曾发生事务仍未知。

不启动Vivado或重编，直接只读检查原r9实际已布线DCP中的EDIF与XDC：sys_rst在F8／LVCMOS15，IBUF接入ps_ai_peripheral；观测器复位逻辑为LUT2 INIT=0xD（!FCLK_RESET0_N OR sys_rst），连接csr_release异步清零，request_sequence的FDCE CLR再由csr_release[2]反相驱动。硬件确有按键复位路径；这不等于已测得物理按键电平、脉冲传播和有效复位。原厂MIG就绪与复位释放协调疑点仍保留。[实际网表摘录](reset-edif-summary.txt)、[父层连接](reset-parent-net.txt)；DCP沿用r9保护身份，未改源设计／约束／位流。

下一诊断需先保留按键后初始原值并验证有效复位，再判断复位覆盖与启动释放时序；本轮不追加启动样本、按键或SDK。HDMI长期验证仍须单独批准。

## 软件修正与执行证据

修正未来独立纯CSR探针：在任何门检拒绝之前，将ABI、长度、status/request/response完整写入stderr；保留严格初始代次及无命令拒绝规则，不把旧代次当复位成功。FPAI GCC9.4原生／AArch64 -Wall -Wextra -Werror编译通过，5类自测通过，新增“保留代次2时零命令退出”覆盖。产物与日志在diagnostic-fix/，**未部署／上板**，不替换本轮已执行的旧ELF，也不改SDK或协议。容器与本批连接已结束。

最初prepare因包预建空boot-mount目录与辅助函数的“必须不存在”检查冲突而退出；当时只有原BOOT只读审计和prepare预约，无BOOT写入／重启／SDK。核实同boot_id、空且未挂载目录、无install预约后，继续原prepare剩余备份步骤；未删预约或覆盖原失败。原execution.log与execution-resume.log均保留。后续没有重跑失败SDK负载。

执行入口、参数、停止条件见[PLAN.md](PLAN.md)、deploy/config.json、execute*.py；原始结果见[software-1.json](software-1.json)、[post-reset-1.json](post-reset-1.json)、[continuation.json](continuation.json)及三份evidence-*.tar；完整命令／串口／SSH日志均在本目录。25秒为软监测，正常进程不因外层超时销毁。
