# r17 跨启动分段观测结果

2026-10-18，Windows主机 D:/FPGACompetitionProject → SSH Lite，同一r9 BOOT，未重编FPGA。上限3次候选启动、1次条件PL按键、1次原BOOT回退；实际3／0／1，SDK Open共3次且每启动仅一次。包已关闭，剩余额度0。

三次启动均在SSH恢复后先恢复原BOOT文件并完整读回，再执行无SDK依赖的纯CSR快照；全部健康。随后同一启动各执行独立父进程覆盖的库加载、一次Open、Open后空闲及关闭／卸载，五段全部通过。各段flags=0x19、ARM窗口复位计数0、六路AR/R握手0、六路RVALID计数0。没有DMA、模型推理、HDMI START或长期验证；未触发故障按键条件。

| 候选 | boot_id | SSH恢复秒 | 纯CSR／SDK分段 |
|---|---|---:|---|
| 1 | 32c247d2-fba5-49f5-b9ba-a7fc9ade3582 | 87.437 | 通过／通过 |
| 2 | 45e611b2-db24-4b86-b6a3-e2def75ca8de | 25.235 | 通过／通过 |
| 3 | 44331025-ece5-4297-bd0c-8e4e8b6b67ff | 27.375 | 通过／通过 |

最终原BOOT回退25.875秒，boot_id=c138a741-7e26-4d2f-9d4f-b9d802774605。原BOOT文件及运行均已恢复，六SDK／九启动文件符合、FPGA operating、设备无占用；串口关闭且TX=0。原BOOT SHA及完整核验见[final-audit.json](final-audit.json)。

结论：本批未复现D45，不能宣布启动稳定性修复，也未取得“故障→PL复位”的因果对照。r14证明显式Open不是异常出现的必要条件，但其程序已链接SDK，无法独立排除库初始化。r15／r17均先访问CSR再加载SDK；这只是待检验的顺序线索，r11曾有SDK先加载仍成功的反例，不据此断言原因。r9观测器仅保存ARM后历史，不能倒推出启动期间没有事务或复位。

硬件已有复位接线，不能解释成“未设计复位”；MIG就绪与复位释放协调仍待验证。[复位链原始分析](../hdmi-startup-20261018-r14/REPORT.md)。本轮不修改硬件、SDK、模型或启动配置，不恢复旧DATA。

完整原值：[continuation.json](continuation.json)、三份evidence-candidate-*.tar及[evidence-final.tar](evidence-final.tar)；执行位置、参数与阶段入口见[PLAN.md](PLAN.md)、[deploy/config.json](deploy/config.json)、execution*.log。25秒仅软监控，不销毁正常进程。失败条件保持：身份变化、SDK／观测异常停止后续候选，不自动重试。
