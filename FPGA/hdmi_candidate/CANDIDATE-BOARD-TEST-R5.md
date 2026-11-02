# HDMI r5受控启动与静态实屏执行包

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

状态：上次实际完成一次候选启动、原BOOT文件还原和稳定八色条确认；本次仅文档交接。**下一阶段实施现暂停，待架构确定及明确恢复，历史回退许可不自动触发重启。** [负责范围与位流操作总结](../FPGA-WORK-SUMMARY-20261016.md)。下文原计划与实际记录保留，FAT问题尚未修复。

## 已核验事实

- Vivado2018.3＋既有JFM整机实现1299.938秒exit0；WNS+0.030ns/WHS+0.029ns，TNS/THS均0。原AI两点Min Period −0.409/−0.071ns例外保持；完整原始报告仍标记Failed Timing，不称独立安全签核。
- 新bit已实际生成127.061秒exit0，Procise ICAP后处理3.711秒exit0。载荷与原BOOT不同；离线封装仅PL分区2007499字节不同，非PL全部相同。
- 候选BOOT 7023552字节，SHA `22035d99f2dacdcb1817a0c08ae8b04c3b024e51bf2f1b522f0fcb9baf252135`；原BOOT同长度，SHA `ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`。具体bit、回退BOOT和静态探针SHA见完整清单（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-integration-20261016-r1/controlled-startup-r5/manifest.json`）。
- 新扫链4.085秒exit0，JTAG-HS1/210512180081；jfmql30/0x9372c093/part0，PS-DAP/0x6ba00477/part1。以后实际program前仍新扫链，不永久固定part。
- COM7为CP210x，115200/8N1，主机DTR/RTS关闭、串口发送0字节，完整收到ttyPS0的33字节标记；接收已关闭。已证明PS UART接收链路，未实际验收新启动日志。
- 最新只读板端BOOT/六SDK同，boot_id仍8974fbf7-cbe9-4fc9-954d-4682c45b045f，FPGA operating，没有相关设备FD owner。但没有公开且已验证的全PL drain/隔离接口，不能据此热重配整机。

## 拟确认的范围

仅临时替换启动分区BOOT以加载本候选，并受控重启一次；不改uEnv、DTB、FSBL、ATF、U-Boot、内核、SDK、模型或时钟。候选启动且SSH恢复后，**先将启动分区BOOT文件恢复为原字节并读回SHA**，运行中PL暂时保留候选用于已授权测试。这样下一次正常启动仍选原BOOT；文件恢复不等于当前运行中PL已回退。

若需要恢复运行中的原配置，拟限定额外一次回退重启；不据此开放无限重启。若启动失败导致SSH不可达，保存完整UART后停止正常测试，必要时人工协助恢复SD启动介质。JTAG/串口已识别不等于已经证明所有故障下可自动恢复；不猜测U-Boot命令、PS复位寄存器或Linux热隔离语义。

这是当前建议的启动边界。AGENTS.md规定“既有一次可控重启许可不允许再次重启；新的相关操作按其授权范围处理”，已有临时板测许可不自动覆盖本次启动区修改和新的重启。

## 批准后的执行顺序与门禁

1. 在新板测批次重新核对板端启动介质/挂载点/可用空间、BOOT/uEnv/六SDK及运行资源，复制与完整读回原BOOT回退包；检查实际文件系统后再制定该介质的原子替换/同步命令。不向未知块设备写入，不用历史路径猜当前挂载点。
2. 上传已核SHA的候选与回退到新临时目录，核对实际字节。仅在范围获批、完整备份且身份一致时替换BOOT；替换后从启动分区读回全文件SHA并sync。任一异常保存停止，不盲重试。
3. 启动前打开有界UART原始字节记录，先记录boot_id和资源停止状态，再执行一次受控重启。SSH/串口启动观察预算180秒；依据规范保存现场后可自主判断正常推进的监控，不能因此扩大重启次数。
4. 若新SSH恢复，核对新boot_id、UART的FSBL/Linux启动链及BOOT/六SDK身份；立即恢复原BOOT并读回SHA。现有uEnv会尝试fatload mmc0:2 download.bit，历史日志为文件系统失败；不改此配置，也不假设其执行成功。实际候选ABI决定运行中加载身份。
5. 以5秒预算运行静态探针--read-only，必须读到core ABI 0x48444d01、board ABI 0x48445301、PLL锁定/idle、无适配错误，并检查像素/CSR计数与100ms主机时间范围。声明目标频率字段不是实际测量，完整像素/串行电气精度仍有局限。
6. 门检通过才运行--bars；无Session、帧分配或显示DMA，先做1080p60静态色条。显示器OSD分辨率/刷新率和实际画面须由现场确认；进程exit0不替代实屏。失败留完整寄存器/串口/日志，停止受影响步骤。
7. 静态通过后才在新的有限批次准备实际帧分配/翻帧/在途STOP测试及骨架接入；沿用已授权接口、资源所有权和旧DATA暂停，不把静态成功写成推理并发或整机实时验收。

## 产物与限制

执行证据（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-integration-20261016-r1/REPORT.md`）、布线门检（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-integration-20261016-r1/system-route-r5/review.json`）、新位流（本机留存，仓库未附：`../../tools/pose-v1/evidence/hdmi-integration-20261016-r1/controlled-startup-r5/hdmi-integrated-r5_disable_icap.bit`）、候选BOOT（本机留存，仓库未附：`../../tools/pose-v1/evidence/hdmi-integration-20261016-r1/controlled-startup-r5/BOOT-hdmi-r5.bin`）、回退BOOT（本机留存，仓库未附：`../../tools/pose-v1/evidence/hdmi-integration-20261016-r1/controlled-startup-r5/BOOT-original.bin`）。

REQP-1577、三条新O5布局告警及原MIG/SDI/AI告警全部保留，无新降级/豁免；本批全局CDC报告不是零告警签核，手册对IO直驱1080p60的限制保持。当前未写板端BOOT、未重启、未下载候选，不能称实屏通过。


## 实际执行后的边界

2026-10-16：HDMI修复已完成整机接入、实际候选启动和静态实屏验证。现场确认“显示稳定的八条色条”；双ABI、PLL/idle/错误门检及约148.5MHz像素计数通过，OSD分辨率/刷新率尚未提供。目标仍为1920×1080@60；r5布线WNS+0.030ns/WHS+0.029ns，原两个AI Min Period例外及其余告警保留。已使用新授权的一次候选重启，SSH约53.6秒恢复；原BOOT随后完整还原并读回原SHA，其余启动文件/六SDK不变。运行中仍为候选静态色条，不是运行中已回退；下一次启动选原BOOT。未进行显示DDR DMA、帧切换/在途STOP、NPU推理或整机实时验收，旧DATA继续暂停。跨重启/tmp清理导致的恢复源丢失已通过主机原始回传及/root持久暂存解决；另查到FAT脏标志与两条合计2168簇的未引用链，来源未知，未修复，启动区停止新增写入。

下方之前的执行顺序和哈希是提出方案时的可审查对象，不回写历史执行为通过。当前真实状态以本段和板测报告（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-candidate-20261016-r1/REPORT.md`）为准。
