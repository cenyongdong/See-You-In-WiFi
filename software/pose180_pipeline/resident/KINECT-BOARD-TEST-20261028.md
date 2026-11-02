# 两模型 TopK=1 安全核心测试

**已结束专项（2026-10-29 核对）：** 微调 epoch13、从零 epoch4、恢复原 epoch99 分别完成 2823／1989／4429 次新推理、HDMI 采纳及 PC 发送，三轮均正常退出；前两模型现场未确认明显改善。原始结果（本机留存，仓库未附：`../../../.local/pose180-kinect-board-test-20261028-r1/test-results.json`）。当前交付是[Top3 三片段 r3](DATASET-PLAYLIST.md)，本页 Top1 命令、曾经的等待／重启计划和远端目录仅作历史；旧远端目录已清理。

2026-10-28 历史专项。将此前TopK=1启动包适配最新安全核心，准备现场微调与随机初始化训练模型的上板对比。原r4及模型归档保留，本批使用独立目录，不复活旧测试额度。

| 测试模型 | 独立启动包 | 本地准备目录 |
| --- | --- | --- |
| 微调 epoch13 | `Deliverables/history/software/pose180-kinect-finetune-e13-safe-20261028-r1.tar.gz` | `.local/pose180-kinect-finetune-e13-safe-20261028-r1` |
| 随机初始化训练 epoch4 | `Deliverables/history/software/pose180-kinect-scratch-e4-safe-20261028-r1.tar.gz` | `.local/pose180-kinect-scratch-e4-safe-20261028-r1` |
| 已恢复：原始 epoch99 | `Deliverables/history/software/pose180-original-e99-safe-20261028-r1.tar.gz` | `.local/pose180-original-e99-safe-20261028-r1` |

以上路径相对项目根目录。实际包校验、板端检查与测试结果统一见 `.local/pose180-kinect-board-test-20261028-r1/`。后续已设计要求启动开发板测试、提前切换随机初始化版，并在两者现场效果均较差后恢复原始epoch99。原始包保持相同安全核心、TopK=1／无阈值与显示设置，仅恢复受保护原模型文件；默认有限处理期300秒。

两包复用已验证的 `.local/pose180-top1-no-threshold-20261028-r5/arm64/pose180_demo`，658616字节，SHA256为 `68cdd986ab72cf8af7d16f4809ca3c9d851d11b414ece2645b36e0acdb4260c1`。该程序含HDMI部分构造回滚、重复释放保护、NPU在途异常保留资源、非标准异常收尾；本地构建和故障注入已完成，不等于新模型组合实板通过。新包保留对应本地验证记录，未重建FPGA或更换SDK。

模型外部接口与原180-query图一致。固定CPU TopK=1、无置信度阈值、单人连续性滤波开启、基础One Euro参数0.5／0.3／1、实时自适应CSI和原预处理。两版使用同一程序、启动器、PC指标栏、HDMI和合格BOOT；只改变模型与其身份记录。PC性能栏含板端处理耗时、骨架更新率和运行状态，不增加精度显示。

每包解压后在根目录使用：

```sh
sh check.sh
sh start.sh          # 默认处理期300秒
sh status.sh
sh stop.sh          # 请求正常停止，不强杀
```

`start-pc.ps1 -Board 192.168.126.49`可使用板端诊断地址显示PC画面，HTTP端口39380；待启动器增加CSI地址后也可使用192.168.50.49。PC可独立关闭。包内BOOT仅备份，不自动安装，亦无SDK自启动。

开始效果比较时先微调、后随机初始化，每次最多300秒，不并行运行。上一包需真实退出、关闭证明完整且设备无占用；当前功能启动消费入口每次FPGA配置仅使用一次，因此切换模型还需准备并正常重启，重新核对BOOT及预检后启动，不能仅凭上个SDK正常退出就在同一boot启动下一包。异常进入 `release_blocked` 时保留独占及资源，不强杀或自动重试。

本次微调版已正常停止，完成2823次推理；现场反馈为能显示但跟随／位置仍较差。随机初始化版首次在同一boot被 `Startup consumer already used in this configuration` 拦截，0次推理。对应检查位于首次snapshot／consume写入及Runtime构造之前；原始错误、空启动消费记录、进程身份、空设备占用和前一运行完整关闭证明均已保留。按既有上板授权追加一次受控正常重启、一次新的最长300秒scratch尝试，不修改旧失败为成功、不更换BOOT或SDK。最新结果以上述唯一目录为准。旧包未收尾事项不因本次测试而被标记完成。

当前启动标识若不在既有准入范围，先只读核对启动分区、SDK及设备空闲；按原入口 `python3 board/startup.py prepare-boot` 记录启动文件身份，受控正常重启后再运行 `check.sh`，不伪造已验证boot_id，不写BOOT。准备阶段与真正推理测试分别记录。

效果判断以实际动作跟随、位置偏差和连续性为主，不把显示滤波平滑或三例Host数值核对当成精度提升证明。训练测试结果及坐标／同步边界见项目 `.local/kinect-calibrated-20261028-r1/COMPARISON.md`。
