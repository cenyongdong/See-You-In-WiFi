# r21：纠正按键后的r9复位／启动分段对照

当前状态：**已确定并执行关闭；正确SW6已使观测器归零，D45未复现。** 下述准备稿与申请范围保留原批准前内容，实际结果见末节。

2026-10-19，准备完成，尚未批准执行。实际位流／BOOT及现有ARM程序复用，不重编。

## 关键纠正

原厂硬件使用手册第20页和原理图PDF第10／22页一致：PL_KEY1=SW6=F8（R397），PL_KEY2=SW7=E7（R401）。r9约束将sys_rst接F8，将rx_gtx_full_reset接E7。此前让按SW7来验证F8观测器清零的指引有误；r18／r20的未归零结果不能作为F8有效复位失败的证据，原值保留。该纠正本身尚未定位D45启动根因。

## 准备与身份

当前已只读核验原BOOT／六SDK／九启动文件、FPGA operating、owner为空，boot_id=f70933d4-3b13-428e-be93-bbaa92176619。复用r9 BOOT a0fe608bb4890f941238b1557f2202987116d1e25669f220fcb4b84fec11fb00；原BOOT ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef，均7,023,552字节。已有主机独立原BOOT备份及板端6项实际复用文件核验通过，pure探针与SDK父子程序不重编。控制器语法和5种按键空闲门检通过，授权保持inactive。

## 申请的一次完整范围

1. 同r9临时安装并启动最多1次；SSH恢复后，先还原原BOOT文件并完整读回，再做其它诊断。UART只收不发，SSH最多180秒、UART每段300秒／4MiB，状态不明不重复发重启。
2. 无SDK纯CSR前置采0→2，保存完整104字。仅健康空闲或已知无AR／R握手的同类返回异常、无设备占用、复位状态正常时，允许按一次**PL_KEY1／SW6**，约0.5秒后松开；必要时用万用表测该键电平，不触碰未知测点。SW7不作为sys_rst测试键。
3. 按键期间不访问复位中的CSR。人工确认松开后，先保存五个初始寄存器；不是0/0或ABI／状态异常则零新命令退出，不加载SDK。归零后采一次0→2纯CSR快照，只有健康才继续。
4. 最多一次SDK库加载／Device::Open，使用既有无SDK父进程＋SDK子进程，按纯CSR／库加载／Open／空闲／Close分段采样。Open至多1次；首个异常保存并停止，不自动重试。不会执行DMA、模型推理、HDMI START或长期验证。
5. 最后或异常后最多1次原BOOT回退；完整核验原BOOT、SDK与启动文件，关闭新包。旧包额度不恢复，已知FAT不修，不改变模型、SDK、频率或RTL。

## 产物与判断

Windows工作目录D:/FPGACompetitionProject，板端新目录/root/hdmi-reset-meter-20261019-r21。实际config、inactive授权、deploy.tar、执行器与local-check在本目录；控制器位于FPGA/hdmi_candidate/scripts/reset_key_board.py。完整原始日志／快照及最终证据只按本次收集，不复制完整工程。

前置为2/2，正确SW6后初始为0/0，才构成观测器复位生效的证据。若同时把纯CSR启动故障清除，可支持其与复位／初始化有关，仍需区别软件加载的影响；单个健康启动不能宣布跨启动稳定。旧DATA继续暂停，HDMI长期不在本包内。

## 实际结果（2026-10-19）

执行1次r9候选启动、1次PL_KEY1／SW6、1次SDK Open及1次原BOOT回退，全部额度用完，包已关闭；无DMA、推理、HDMI START或长期验证。原BOOT文件在候选SSH恢复后已先还原并完整读回。

| 时刻 | status／request／response | 结果 |
|---|---|---|
| 无SDK基线ARM／FREEZE后 | 0／2／2 | flags=0x19；六路AR／R握手及RVALID均0，owner为空 |
| 正确SW6按下并松开后、发命令前 | 0／0／0 | ABI=0x41495201、长度104，PS boot_id未变；确认观测器CSR复位生效 |
| 按键后的纯CSR采样 | 0／2／2 | 健康；随后才加载SDK |
| pure_before_library／library_load／Open／idle／Close | FREEZE依次4／6／8／10／12 | 五段均flags=0x19，六路AR／R／RVALID均0，窗口内复位计数0，SDK父子进程正常结束 |

该启动在按键前已健康，所以不能证明SW6能修复故障启动，也不能认定跨启动稳定或全部互联／MIG复位域均正确。此前按SW7不能检验F8复位的推断已纠正；本轮没有实际测量按键电压，无需冒险探测细小焊盘。

最终原BOOT启动号b62764f3-133c-4981-8e76-4440a9973365；六SDK／九启动文件符合，FPGA operating、owner为空。完整原始快照、软件日志与最终身份在evidence-final.tar，最终审计另见final-audit.json。两段UART均TX=0且已关闭。

随后拔除网线。已通过COM7／115200串口完成登录和只读命令，返回同一启动号、uid=0、FPGA operating；登录退出并释放端口。串口包装器遇到单项字符串解析错误，原失败保留；直接从已产生的JSON恢复结果，未重发板端命令。对应原值在serial-command.rx.log、serial-command-recovered.json与serial-cleanup.json。后续通信改为串口，未重新写BOOT或重启。

后续需要取得故障启动中按正确SW6的对照，才能继续判断BOOT初始化／SDK加载／Open与返回异常的关系；当前剩余启动／按键／回退额度均0，不从本报告扩展许可。
