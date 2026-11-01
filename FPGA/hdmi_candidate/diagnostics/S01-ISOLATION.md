# S01源端隔离对照

2026-10-22。隔离前源码、约束、实际集成输入及官方Markdown问题报告已提交；回退标签为`codex/hdmi-before-s01-isolation-20261022`。当前开发分支为`codex/hdmi-s01-isolation`。

本轮r28只回答：没有HDMI／旧视频作为S01主机参与时，PS HP2最早的无已观测AR返回是否仍出现。保持AI四路、PS封装、双输入互联、SDK寄存器、共享复位提供者、原DDR就绪门及被动观测接线。它不等于删除整个S01互联内部，也不重分配HP端口。

`prepare_s01_isolation.py`从已提交的r26实际基线生成外围隔离副本：旧视频AW／W输出及HDMI AR输出不再连接PS；视频主机获得空闲反馈。S01的全部27个主机输入固定为0，包括RREADY／BREADY，不强制排空未知返回。原S01输出仍进入被动观测，通道4此时表示已隔离的S01接口，不再是功能HDMI reader的输入。

生成时逐段比较AI实例、完整PS wrapper连接、frame_trans共享复位控制及观察接线；原生link后逐输入验证实际S01由GND驱动。只读捕获、原ABI及源域首事件记录保持。部分无数据来源的HDMI FIFO会被综合合法裁掉；对应CDC对象缺失时检查实际常量／对象消失，剩余路径仍保留原约束，不新增false-path或DRC豁免。

实板还检查旧104字快照中通道4的当前管脚字83：ARBURST／ARSIZE／ARLEN／ARID、ARVALID及RREADY对应的`0x7fff9`掩码须为0。未隔离reader的ARSIZE恒为3、ARBURST为1，历史实测掩码为`0x2c000`；因此该只读检查可以区分实际隔离接线，不能只凭与r26相同的ABI就认定候选身份正确。检查不发送HDMI START，不主动消费返回。

本轮自设最多1次无SDK候选启动和1次原BOOT回退；SDK／Open、DMA、推理、HDMI START、按键及长期均为0。不改PS寄存器或启动固件，不复用已关闭r26及旧包额度。实际bit、BOOT与非PL字节核验、SSH身份和COM7 RX均满足后才进入板测。

实际结果已完成：[版本化结果与产物绑定](S01-ISOLATION-RESULT.json)。1次候选未复现早期PS返回，唯一原BOOT回退及文件／运行身份核验通过；包关闭、全部余额0、无后台工作。原r26状态保持关闭，不回写旧额度。初次SSH超时已保存；阶段恢复后连接后，只读预检及COM7实际标记接收通过，不猜中间发生的启动次数。

代码位于`C:/Users/cenyongdong/.codex/worktrees/hdmi-s01-isolation/FPGACompetitionProject`，开发分支仍为`codex/hdmi-s01-isolation`。主工作区被其它任务切到`feat/heart-rate`后，本轮迁入独立受管worktree，未切回或提交该分支。构建资产保留在`D:/FPGACompetitionProject/.local/hdmi-s01-isolation-20261022-r28`；原生完整输出、板端原值归档和最终`state.json`在`D:/FPGACompetitionProject/tools/pose-v1/evidence/hdmi-s01-isolation-20261022-r28`。这些运行产物不在新worktree的同名相对目录中。

实际setup／hold为+0.030／+0.010ns，101,957条网络完整布线；既定AI两个Min Period例外保留，原始全时序零例外并未通过。未新增时序例外或DRC豁免。非PL BOOT字节保持。原生`opt`、`opt-r2`、`bit-r2`的失败退出码保留；后续仅适配常量折叠后的实际CDC对象及匹配宽度，消费有效检查点，没有把父脚本失败改写为原生通过。

若隔离后仍出现早期PS返回，视频主机不是该样本的必要条件，但PS初始化、配置前请求和互联内部状态仍待区分。若未复现，只认定这次观测；不以一次健康样本证明修复，不自动开始SDK或端口重分配。

2026-10-22直接进行隔离版长期稳定性验证。新r29复用同一实际位流／BOOT，最多1次候选、1800秒无SDK被动驻留及1次原BOOT回退；AI四路保持，不复活r28。延迟首次FREEZE到驻留结束，期间通过未发布银行仍可读的首事件粘滞标志检测异常并提前保存；不重新ARM清掉现场。104字窗口的32位周期计数会回绕，实际时长以单调时钟及64位启动历史计数认定；无请求／返回以首事件和原始计数交叉判定，不用取模周期当总时长。本轮不验证AI负载或显示功能。实际状态与原值在`D:/FPGACompetitionProject/tools/pose-v1/evidence/hdmi-s01-soak-20261022-r29`。

r29实际结果：[版本化故障与恢复记录](S01-SOAK-RESULT.json)。同一隔离BOOT在最早GP周期3已见PS RVALID，未见已观测AR；隔离S01随后保留返回，实板源输入仍为零。首次检查即触发提前停止，原值已保存；30分钟未完成，不能称长期通过。完成1次候选＋1次原BOOT回退，已关闭、全部余额0，无后台任务。原运行态已核验为`f148231e-ada5-41bf-9c6d-2459c76c2b6b`。同一隔离镜像既能健康也能异常，故仅隔离视频源端不足以消除D45；仍保留互联内部、PS初始化及配置前事务等未知，不据此改AI端口或执行失败负载重试。
