# r16 原位库加载／Open分段结果

补充批准一次Open；沿用r15当前r9启动，未写BOOT、未新增候选启动。纯CSR父进程不链接SDK；SDK子进程先返回READY再等待GO，严格只调用一次Open。**五段均健康，未复现故障。** 不能据此宣布跨启动稳定或排除所有间歇性库加载／Open影响。

| 区间 | FREEZE代次 | 200MHz窗口ms | 复位异常周期 | HDMI / HP2 RVALID周期 |
|---|---:|---:|---:|---:|
| pure_before_library | 4 | 24.370825 | 0 | 0 / 0 |
| library_load | 6 | 49.118195 | 0 | 0 / 0 |
| Device_Open | 8 | 28.19041 | 0 | 0 / 0 |
| idle_after_Open | 10 | 28.32866 | 0 | 0 / 0 |
| Device_Close_and_unload | 12 | 7.69844 | 0 | 0 / 0 |

全部窗口flags=0x19，六路AR/R握手均0；完整104字原值、固定代次与SDK原始输出已回传。SDK进程正常关闭，父进程exit0，整段0.347476秒、owner为空。Open窗口没有记录hp_clk_rst／HP2 peripheral_aresetn异常周期，不能把Open当作保证整条共享路径复位的动作；其它SDK内部复位域不在此结论范围。

r14失败出现在显式Open前，但当时进程已链接SDK，库加载混杂因素保留；r15的纯CSR前置及r16库加载／Open在另一个启动中均正常。现有证据优先要求继续捕获“完全不加载SDK的故障启动”，再做同启动的一次PL复位对照。已有复位连线；MIG就绪、复位覆盖和释放时序仍是待验证原因，未声称缺复位或BOOT文件损坏。

已使用r15尚未消费的一次原BOOT回退并核验，当前boot_id=909a27b1-1d3b-4613-86dd-a0b3e35ea734；原BOOT／六SDK／九启动文件保持、FPGA operating、无占用，串口关闭。r15及r16均关闭，剩余额度0。没有DMA、模型推理、HDMI START、按键或长期测试。

原始结果：[result.json](result.json)、[全部回传](evidence-software-init.tar)、[执行记录](execution.log)；最终原BOOT审计见[r15](../hdmi-reset-ab-20261018-r15/final-audit.json)。工具编译、9类观测测试及4类无硬件协议测试见[PLAN](PLAN.md)和本目录原生日志。协议测试初次因容器无python3未运行，改用已有Bash后4类通过，没有安装工具或把环境错误改写为执行通过。
