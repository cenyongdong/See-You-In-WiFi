# r15 纯CSR启动样本与回退

同一r9 BOOT候选启动1次，SSH恢复23.734秒，先完整恢复原BOOT文件。纯CSR ELF的DT_NEEDED仅标准C/C++运行库、无Icraft SDK。20.0844ms窗口4,016,880周期，flags=0x19、复位异常0，六路AR/R握手及HP2/HDMI RVALID均0，前置状态健康。依方案**未按PL_KEY2**，故没有复位前后故障对照，不称硬件复位已修复。

另批准[r16原位SDK分段](../hdmi-software-init-20261018-r16/REPORT.md)，不新增BOOT写入或重启。随后消费本包唯一原BOOT回退，SSH恢复87.234秒；当前boot_id 909a27b1-1d3b-4613-86dd-a0b3e35ea734。原BOOT文件／六SDK／九启动文件符合，FPGA operating、owner为空，串口均关闭，TX=0；两包均关闭，无剩余启动／Open额度。旧DATA暂停、FAT不修，HDMI长期未启动。

原值：[前置观测](probe-1.json)、[全部回传](evidence-final.tar)、[最终审计](final-audit.json)、execution-before.log及execution-fallback.log。本次是健康启动样本，跨启动故障仍未定位。
