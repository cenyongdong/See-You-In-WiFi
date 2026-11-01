# r20 无SDK按键清零校准结果

2026-10-18，Windows D:/FPGACompetitionProject → SSH Lite，同r9 BOOT a0fe608b…61fb00，不重编FPGA。并实际完成：候选启动1次、PL_KEY2／SW7按键1次、原BOOT回退1次；SDK加载与Open均0，包已关闭、剩余额度全部0。未做DMA、推理、HDMI START／长期验证或文件系统修复，旧DATA暂停。

## 取得的实际原值

候选SSH恢复27.375秒，boot_id=482f2b49-a6d8-40c3-8f5a-ec7bd70ebc6c；SSH恢复后先完整还原原BOOT文件，再运行独立纯CSR ELF。基线初始代次0，ARM/FREEZE后为2，104字完整保存，20.094345ms窗口内flags=0x19、复位计数0、六路AR/R及RVALID计数均0，owner为空，属于健康空闲，符合本包按键范围。

人工确认“已按一次PL_KEY2／SW7并松开”。没有电气脉宽测量；代理只记录实际人工确认。随后仅运行一次纯CSR程序，结果如下：

| 时刻 | ABI | 长度 | status | request | response |
|---|---:|---:|---:|---:|---:|
| 基线开始、发命令前 | 0x41495201 | 104 | 0 | 0 | 0 |
| 基线ARM/FREEZE完成 | 0x41495201 | 104 | 0 | 2 | 2 |
| 按键后、发命令前 | 0x41495201 | 104 | 0 | 2 | 2 |

**按键后读回没有表现为归零。** 程序0.015529秒退出1，原文“Not a fresh observer: no command issued”，五个初始值已保存；没有发新的ARM/FREEZE，没有第二次按键、额外采样或SDK。PS boot_id未变，owner为空。结果中的valid=false／healthy=false仅表示未取得通过门检的快照，不能解释成按键后总线已测得不健康。

这一结果独立于SDK和偶发故障复现：本次基线健康且完全未加载SDK，也没有观察到预期的CSR清零。因此，不能再把“按键完成”当作“硬件有效复位已验证”。但单次按键后状态仍为2也不能唯一排除瞬时清零后再次变化、CSR读回／复位覆盖问题，不能直接断言物理按键脉冲未到达，更不能直接认定它就是D45启动故障根因。

## 已核对与下一处证据缺口

r9实际DCP中已有F8输入、复位LUT及观测器FDCE异步清零连接，[既有实际网表摘录](../hdmi-library-first-20261018-r18/reset-edif-summary.txt)继续适用；本轮没有重开Vivado或修改位流。重新目视原始按键原理图，SW7／PL_KEY2高有效及其与R400／R401／C571的连接与原[引脚契约](../../../../FPGA/hdmi_candidate/PIN-CONTRACT.md)一致，实际物理电平尚未测得。

本机Procise只读命令查询确认有原始scan_ir_jtag／scan_dr_jtag接口，但没有取得该器件的SAMPLE指令与F8边界扫描映射，尚无可直接采用的引脚采样流程。查询只执行info／help／exit，没有初始化链、移位、下载或任何板端JTAG操作。[命令盘点](tool-capability/inventory.stdout.log)、[帮助查询](tool-capability/help.stdout.log)。不猜测指令或映射，也不据此断言工具完全不支持。

下一步先确认现场是否能直接测量PL_KEY2电平；若不能，准备独立复位见证的离线方案：用不随PL_KEY2清零的观测状态保留按键电平／边沿、目标复位边沿及首次异常时序。此处仅为方向，不授权新的按键、BOOT、重启或长期验证。现有ARM后计数及自复位代次无法提供完整脉冲经历。

## 回退、范围与证据

唯一原BOOT回退SSH恢复85.515秒，boot_id=0078c99b-70f2-40d8-9445-0bb5002df570。等待期间监测原进程与串口，没有重发重启或销毁进程。最终原BOOT运行与文件均恢复，六SDK／九启动文件符合、FPGA operating、设备无占用，串口关闭且TX=0。[最终审计](final-audit.json)、[实际次数](fallback-result.json)。本批无后台任务。

执行位置、完整参数、前置条件及失败停止条件见[PLAN.md](PLAN.md)、deploy/config.json和execute*.py。原值见[probe-1.json](probe-1.json)、[post-reset-1.json](post-reset-1.json)、[实际人工确认](user-reset-confirmation.json)、[恢复状态](continuation.json)，完整SSH／串口与三份evidence-*.tar保留。本次实际验证了新增探针在非零初始代次时先保存五寄存器原值、再零命令退出的路径；不称按键复位通过或启动稳定性修复。
