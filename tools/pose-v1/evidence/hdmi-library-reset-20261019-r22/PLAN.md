# r22：SDK先加载与故障下SW6复位对照

当前：已执行并关闭；首次候选复现故障，正确SW6清零CSR后返回异常仍在。第二次候选取消，原BOOT已回退。阶段恢复后SSH并唤醒排查，旧包仍关闭。

只读复核见[resume-audit.json](resume-audit.json)：固定SSH主机密钥一致，当前原BOOT、六SDK／九启动文件均符合，FPGA operating，无设备占用。当前启动号写入config.json；与r21最终启动号不同，采用本次实际身份，不复用旧运行句柄。COM7串口备用。

## 测试目的

r21已证明F8=PL_KEY1／SW6可清零观测器；仍缺少故障启动的正确按键对照。本包沿用r18复现过故障、r19健康的“SDK库先加载、首次CSR后置”顺序。健康样本不宣布启动稳定；按键恢复也只能支持复位／初始化相关，不能直接确定哪个域或BOOT／SDK为根因。

## 一次批准范围

1. 复用同r9 BOOT（a0fe608b…61fb00），最多临时安装并启动2次。每次SSH恢复后先还原原BOOT文件（ff350477…8b31ef）并完整读回，再执行诊断；首次异常停止剩余候选启动。第二次仅在第一次完整健康、设备空闲时进行。
2. 每启动只加载一次SDK子进程；在任何CSR映射前完成库加载。首个CSR窗口健康才允许至多1次Device::Open，随后观测空闲和Close／卸载。全包Open最多2次，异常不重试。
3. 仅捕获到Open前、零AR／R握手且HP2／HDMI整窗RVALID背压的既有故障，并确认SDK进程退出、无设备占用，才人工按PL_KEY1／SW6一次（F8，约0.5秒后松开）。不按SW7；按住期间不访问CSR。人工确认松开后，先保存五个初始寄存器；不归零则零新命令退出，归零后仅采一次纯CSR快照。按键后不再次加载SDK／Open。
4. 结束或异常后最多一次原BOOT回退，完整复核并关闭包。旧DATA继续暂停，不做DMA、推理、HDMI START／长期验证或FAT修复，不改RTL、频率、模型、SDK或网络配置。
5. SSH恢复观测预算180秒、UART每启动300秒／4MiB且TX=0。命令不因超时重发；若原生进程仍运行，先查PID／日志并监测，不自动杀进程或再次启动负载。

## 已完成的准备

BOOT和ARM ELF复用板端既有r20／r19产物，主机独立原BOOT备份沿用已核验版本。板端6项复用产物和原BOOT读回备份核验通过，实际Python语法通过；未激活授权的拒绝门在板端验证通过。控制器位于[library_reset_board.py](../../../../FPGA/hdmi_candidate/scripts/library_reset_board.py)；config.json、inactive授权、30KiB deploy.tar及execute.py在本目录。用真实r18故障、r19健康样本及owner／已Open／窗口复位／请求在途四种反例验证门检，6项通过。部署仅写新诊断目录的普通文件；没有写BOOT、重启、按键、加载SDK或操作MMIO。


## 实际结果（2026-10-19）

实际执行候选启动1次、PL_KEY1／SW6按键1次、原BOOT回退1次；Open=0，DMA／推理／HDMI START=0。首次异常即取消第二次候选，剩余额度随关闭归零。原BOOT文件已在候选SSH恢复后、任何诊断前还原并完整读回。原始快照见software-1.json、post-reset-1.json，完整进程日志及最终审计见evidence-final.tar。

| 阶段 | 实测结果 |
|---|---|
| SDK库已加载、尚未Open | 观测窗口4,652,062周期，六路AR／R握手均0；HP2及HDMI的RVALID与背压均覆盖整个窗口；父程序按门检退出71，子进程退出，无设备占用 |
| 按正确SW6后、任何新命令前 | 同一PS启动号；ABI=0x41495201、长度104、status／request／response=0／0／0，确认CSR域复位 |
| 按后纯CSR重新采样（不加载SDK） | 新窗口4,017,307周期，六路AR／R仍0，HP2／HDMI仍整窗RVALID背压，故healthy=false；原生探针正常保存快照并退出0 |
| 前后共同特征 | flags=0x19，窗口内复位计数0；PS端当前RID=0x20，HDMI端RID=0；当前引脚字分别0x0102dc06、0x0002c006 |
| 结束 | 原BOOT运行与文件复核、六SDK／九启动文件符合，FPGA operating、owner为空；两段UART均TX=0并关闭；授权关闭，无后台任务 |

本次候选SSH恢复87.156秒，原BOOT回退27.937秒，均在180秒预算内；没有因候选恢复较慢再次发重启。按键完成确认后只执行一次纯CSR采样，未重试SDK。

## 判断与剩余缺口

事实：故障下正确SW6能清零观测器，但按后返回异常仍在。不能再用“按错键”或“旧CSR快照”解释本次结果；也不能据此断言所有复位域正常或异常在按键期间从未短暂消失。ARM后零握手不排除启动更早已有请求。

实际r9 routed DCP的EDIF连接核对见reset-net-trace.txt：proc_sys_reset_1的peripheral_aresetn同时接HP2互联ARESETN／M00／S00／S01；上游RVALID来自processing_system7_0的S_AXI_HP2_RVALID。它证明这些连接存在，不证明按键期间各缓冲实际复位、MIG／时钟恢复顺序或PS侧未完成响应被清除。来源位0x20路由到S01的观测与既定映射相符，不能单凭其判定ID截断。

只读启动项检查未在已读/etc/rc.local、init.d及本地systemd服务中发现AI自动负载；对身份一致的两个SDK库构造器做直接调用扫描，主要见注册路径，不能排除间接／其它依赖库的硬件影响。板端未安装strace／ltrace，本轮不安装工具。上述检查均未加载SDK。

现有r9观测器从ARM之后才累计，无法补回启动期首笔AR／R，也未记录按键期间的实际互联复位脉冲。下一阶段需要先补足这一取证缺口，再决定PS侧队列／BOOT初始化／SDK加载／复位释放中的实际触发点；不继续用同样的健康启动统计或盲改ID连线代替定位。BOOT、重启及失败SDK负载新尝试须具体新包批准；HDMI长期仍未批准。
