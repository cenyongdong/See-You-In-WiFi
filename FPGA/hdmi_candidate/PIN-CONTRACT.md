# Lite板HDMI、参考时钟及按键引脚核对

2026-10-19纠正：原记录将F8误标为PL_KEY2。硬件手册第20页与原理图第10／22页一致，正确映射为PL_KEY1／SW6→F8、PL_KEY2／SW7→E7。r9把sys_rst接F8、rx_gtx_full_reset接E7；因此此前SW7按键结果不能验证F8观测器复位。见[r21方案与原始依据](../../tools/pose-v1/evidence/hdmi-reset-meter-20261019-r21/PLAN.md)。r21已实际验证正确SW6按下／松开后观测器0/2/2→0/0/0；只证明该CSR域清零，未测实际电压或全部复位域。

2026-10-15，只读核对Docs/开发板手册/JFMQL30TAI_LITE.pdf的PDF第9、10、19、21、22页，实际图纸Sheet标签为9、10、23、25、26；完整页面与放大图已目视检查。页脚沿用JFMQL100TAI标题，U1器件符号明确为JFMQL30TAI；下表同时与原工程XDC及候选已执行的引脚探针对照，不凭文件名或标题推断兼容。

| 作用 | 原理图网络 | FPGA球位 | BANK／供电 | 使用契约 |
|---|---|---|---|---|
| 独立参考时钟 | PL_100MHz | AC14 | 12／3.3V | G1标称100MHz，MRCC；不是SDI或MIG推导时钟 |
| TMDS时钟P／N | HDMIO_FCLK_P/N | AC17／AC16 | 12／3.3V | 原生差分输出，两端配对 |
| TMDS数据0 P／N | HDMIO_FD0_P/N | AA15／AA14 | 12／3.3V | 对应HDMI D0 |
| TMDS数据1 P／N | HDMIO_FD1_P/N | Y16／Y15 | 12／3.3V | 对应HDMI D1 |
| TMDS数据2 P／N | HDMIO_FD2_P/N | W16／W15 | 12／3.3V | 对应HDMI D2 |
| 热插拔输入 | HDMIO_HPD | AE16 | 12／3.3V | 经R353/R354分压，不等于已取得EDID或显示器时序支持 |
| DDC时钟 | HDMIO_FSCL | AA17 | 12／3.3V | Q4电平转换至HDMI侧5V上拉；只允许下拉/释放，需核验实际双向接口 |
| DDC数据 | HDMIO_FSDA | AB17 | 12／3.3V | Q5电平转换；只允许下拉/释放，不推挽驱动 |
| CEC | HDMIO_CEC | AB16 | 12／3.3V | 可选独立控制，不与DDC互换 |
| r9 sys_rst输入 | PL_KEY1／SW6 | F8 | 34／1.5V | 松开低、按下高；串联R397，非PS上电复位 |
| r9 rx_gtx_full_reset输入 | PL_KEY2／SW7 | E7 | 34／1.5V | 松开低、按下高；串联R401，不是r9的sys_rst |

第22页显示PL_KEY1由SW6、R396 10K下拉、R397 10K串接与C570滤波组成；PL_KEY2对应SW7、R400／R401与C571，两者按钮均接PL_VCC1V5。r9复位使用前者，物理请求高有效；仍需在各时钟域实现规范的复位同步/释放，并保持AXI复位协调，不能把按钮抖动或局部复位当在途读完成。早期F8极性分析保留，原按键名称映射现已纠正；未修改RTL或板上接线。

第19页显示FPGA IO直接通过电容/保护网络到HDMI，没有专用发送器。该页明确指出1080p60不能保证，建议专用HDMI输出芯片，IO直驱支持720p及以下。现行1080p60仍是候选目标；此处不自动改成720p，也不能把逻辑仿真、100MHz引脚布线探针当1.485Gb/s输出验收。最终仍须实际器件/IO时序、完整布线和显示器确认。

这些球位和电气网络不能提供PS7/PCPU7内部AI_IN/AI_OUT原语端口定义。PS配套问题见[JFM核对结果](JFM-COMPATIBILITY-REVIEW.md)。完整原值和SHA见本批证据（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-jfm-pin-review-20261015-r1/REPORT.md`）及pin-contract.json。当前未接入HPD/DDC/CEC新功能，没有MMIO、EDID读取或硬件测量。
