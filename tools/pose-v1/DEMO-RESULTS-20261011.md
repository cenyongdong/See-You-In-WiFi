# 2026-10-11 端到端演示结果

暂停现阶段坏读定位、优先形成software/demo全链演示，本工作包已完成。真实数据源为指定wifipose/test_data/csi目录；主机仅读MAT csi_out并PIWCSI1回放，Lite执行PS预处理/既有PS-NPU Engine/骨架渲染/VPU H264，主机通过RTSP/TCP实际解码和GUI显示。HDMI未接入。

## 程序与数据身份

- 构建：`.local/pose-v1-build/demo-20261011-r5`。
- pose_demo SHA256：`82201e97547504ccd0c883191dbbb9e05957e378a77de0cbda5006c6f5d987e0`。
- 显示子进程SHA256：`6d88d03af190a893445838ef3695d0774ad006d1863f9b063827e0d6e4137d39`。
- 模型图SHA256：`75ffdc37b93dcb4913678991d6e7cf5cd0ab09c59653224d07c7434345acb8a0`。
- RAW SHA256：`3991a679282a4c6b014aece59b717910bc53fd14e67c0fac5fb9f93d4ae054d3`。
- 成功板端目录：`/tmp/wifi-pose-demo-20261011-r4`。本机完整证据：[demo-20261011-r4](evidence/demo-20261011-r4/completion-review.json)。
- SDK3.39.0/BOOT/CPU数学/Gather/NPU分配/public-read桥/帧reset(1)/profiling-off保持。旧152冻结软件未修改；SDK15头/厂商189头库锁定。

## 通过范围

| 项目 | short三窗口 | demo默认60窗口 |
|---|---:|---:|
| 原始CSI收到/消费/完整输出 | 3/3/3 | 60/60/60 |
| 原始负载逐位核对 | 3 | 60 |
| 不同姿态输出 | 3 | 60 |
| VPU编码/离线解码图像 | 352 | 637 |
| 主机实际RTSP GUI解码 | 292 | 577 |
| 真姿态来源覆盖 | 3 | 60 |
| 骨架投影关节核验 | 42 | 840 |
| 总时长（含初始化） | 36.50511秒 | 65.16524秒 |
| 普通512KiB单位前/后 | 202/202 | 149/149 |
| 成功阶段规整 | 0 | 0 |

两阶段共63真实CSI推理/989编码/869主机解码，默认2Hz窗口发送与10fps最新画面采样，60窗口无覆盖。开始约30秒NoInput是Engine初始化；编码重复画面不等于新姿态。主机从IDR进入，启动部分未解码不影响全60来源覆盖。原码流ID顺序和42/840投影关节通过；身体区域RGB平均绝对差1.64523/1.64924来自有损H264，不是姿态数值误差。

308/309/310两阶段均匹配旧原始CSI、PS输入10800FP32、完整100分数和4200姿态，逐位且有限。其余57输入全部保存完整返回，但仅形状/有限性/候选选择/来源映射检查，未完成全量精度验收。旧CPU107/12注册/59600值身份复用，本轮未新跑Host107。Native/ARM TCP七拒绝及所有权、碎片重组、断连、重复、idle合同新执行通过。

正常drain/LAST、两STREAMOFF、全部raw归还、线程join后Engine销毁、子进程/端口释放均过。最终只读审计确认BOOT/SDK/模型与成功阶段同、kernel同/FPGA operating、无项目进程及39001/8554监听。MemAvailable750300KiB/CmaFree130784KiB仅最终现场，CMA256MiB保持。全部测试/播放器/SSH已结束。

## 历史失败和实际修正

1. r1构建调用旧TCP selftest缺参数，Native停止；补--self-test后协议通过。
2. 首短测试VPU DQBUF EIO、普通512KiB单位1；一次规整39.27594ms后仍1，Engine/前向/PC解码均0。完整异常和内核回传，没有重跑失败Session。
3. 额外批准一次可控重启；实际只一次systemctl reboot。前后BOOT/SDK同、新boot-id/FPGA operating，普通单位980。/tmp被系统清空，旧失败已在本机保存；新只读目录补重启审计，无第二次重启、清缓存或CMA变化。
4. r2新运行首次capture过，Engine证据目录缺失导致构造失败；main修正目录创建。播放器open/read预算调整到10/5秒、总90/175保持。
5. r3运行Engine初始化过、255 NoInput解码，首次CSI Producer Recorder未配置拒绝。新增独立demo_engine集中原模块初始化/保存，没有更改NPU或数学。r5程序在新r4目录通过两阶段。
6. 本机编排修正取消播放器并始终取归档，修订分别新目录新包，失败数据不覆盖。详情见[ADR_45](../../ADR/ADR_45.md)。

## 证据及操作入口

- [Host协议](evidence/demo-20261011-r4/host.review.json)。
- [短阶段数据/实时显示](evidence/demo-20261011-r4/short.review.json)、[原VPU视频](evidence/demo-20261011-r4/short.video-review.json)。
- [60窗口数据/实时显示](evidence/demo-20261011-r4/demo.review.json)、[原VPU视频](evidence/demo-20261011-r4/demo.video-review.json)。
- [最终只读收尾](evidence/demo-20261011-r4/final-return/final/review.json)。
- [运行说明](../../software/demo/README.md)、[技术汇报](../../ADR/TechDetails.md)、[检查点](evidence/demo-20261011-r4/next-checkpoint.json)。

码流short SHA256 `15a8c1ec75610718cca3852b289ff84a5b18897d1668aa63ac63130a7d2affdf`，demo `6e6440ee89224a9ba333f0861b6344e984516d2efb44b39ac525c7d7637be711`。原归档及画面数据留本机，Git仅提交报告、源码、哈希和小预览，摘要不能替代完整回传。

## 限制与后续

原高负载DATA96/800/192/582首次坏读根因没有修复，保持暂停，原首次文件/晚源读不删。永久VPU首启动、严格整机5Hz、30分钟、真实采集、零拷贝及HDMI未通过。当前处于有界可展示系统完成、性能与长期可靠性待收敛阶段，管理83/100保持（非验收通过率或工期）。本批无继续排查或后台运行；若阶段恢复后旧排查，先核对身份和ADR_44检查点，不能续用已失败Session或重启前/tmp句柄。
