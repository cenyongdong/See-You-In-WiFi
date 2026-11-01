# E1-C骨架渲染与V0配套核对结果（2026-10-07）

## 工程内容总结

核对E1-A/B后要求继续下一阶段。代理完成CPU骨架渲染、像素缓冲区转换、ARM验证、三帧真实网络推理后的绘图接入及只读视频查询。人工确认显示器尚未连接；未启动HDMI、编码或RTSP。

### 索引与坐标约定

`visualization/visualize_24_pose.py`的BONES与24版`limb_loss.py`一致，共14条连接。实际绘图使用这份索引拓扑，不使用通用petr分支的另一套连线，也不导入GT、平滑、人物匹配或展示阈值。
进一步核对发现24版原可视化在显示层明确对C2取反并设置Z朝上。当前渲染保留原始坐标，仅沿用这项显示符号约定；不继承其米/毫米单位声明，画面仅标MODEL UNITS、C0/C1/-C2及索引0..13。

固定正交投影：raw中心(1.75,1.75,3.4)、yaw30°、elevation20°、220像素/模型单位、屏幕中心(460,355)，画布1280×720。没有逐帧自动缩放或重新居中；网格平面raw C2=4.2是展示辅助，不代表物理地面标定。
合成与真实预览已由代理目视检查，拓扑、显示方向与配置可追溯；解剖名称和物理轴标定仍未确认。

### 工程与验证

新增SDK无关 `skeleton_render.hpp/.cpp`、独立检查器；新 `application_render_check.cpp`只在既有完整本帧结果返回后绘图，原engine、CPU数学/注册/桥、网络接收、模型/RAW/SDK/BOOT和帧协议保持。
画面显示帧号、最高分槽位、分数与状态；支持RESULT/NO INPUT/STOPPED状态，非结果状态不画旧骨架。分数只用于选择与显示，不宣称已标定置信度或稳定人物身份。

| 门检 | 实测结果 |
| --- | --- |
| Native自检 | 合成/裁剪/无输入/停止四画面；同分取首槽、输入不变、8拒绝用例通过 |
| Native真实27帧 | 用此前已验收板端全输出绘图，投影/选择及RGB565/NV12/NV21由独立NumPy核验 |
| 新ARM构建 | 467包、23构建来源、15ARM头文件/两后端匹配，三个AArch64程序，无RPATH/RUNPATH |
| ARM纯CPU渲染 | 自检与真实27帧通过；RGB画面、RGB565、NV12、NV21全部与Native逐字节一致，零真实关节被裁剪；179完整回传，无Device::Open |
| 新程序Host107 | 107例含拒绝、12注册/Gather、22输出59600FP32及Host内容正负路径通过；52完整回传 |
| 网络推理＋绘图 | 原三帧新前向与此前板端全输入/全输出逐位一致；绘图选中同一槽位/42坐标，画面帧号6/7/8与本帧一致；三格式独立核验；70完整回传 |
| V0查询 | /dev/video0 MVX能力/格式/尺寸及sysfs/DT读取通过，两端只枚举MPLANE；不配置/申请队列/stream，不写寄存器 |

三个正式阶段均exit0、stderr空、完整dmesg前后相同。只读视频查询同样exit0/stderr空/dmesg保持，没有新依赖或自动重试/复位。本轮没有模型数值修正或深度性能优化。

CPU27帧绘图均值 **11.93939ms**、P95 **12.13419ms**；同时生成RGB565＋NV12＋NV21三种诊断缓冲区均值 **88.84998ms**、P95 **89.60106ms**，不含磁盘写出。真实三帧绘图约11.46–12.45ms、三转换约88.38–88.94ms。
网络发送频率为2Hz，这些是新渲染模块的短批次数据，不作为整机5Hz或30分钟验收。三种格式同时生成包含两份替代YUV格式计算；未来实际输出只保留所需格式，并按已批准方案用有界独立绘图/输出工作者测吞吐和CPU/DDR争用，仍不并发调用Engine。

### 产物

- 新包：`.local/pose-v1-render/package-20261007-r1`；构建：`.local/pose-v1-build/mixed-20261007-render-r1`；板端：`/tmp/pose-v1-render/20261007-r1`。
- 接入程序SHA256：`0fc63b8f64a78884538ab8c4cb4701ad5fc6046e11e44ad62f960cf5b8dd9533`。
- 纯CPU渲染程序：`d5347fadc95213c6fd36fc023a286134d627fdda1234f77b5c81bc8523ec4eb2`。
- 查询程序：`a5b587a75b35b7a54c183b3dfe7ad3c65fe6c5cf0138e349629d05507e3de6e1`。
- manifest：`a6955281211f9f069cfcac7297b243f340c4096cc2f1ca3913289dec64997437`。
- [完整核验](evidence/render-20261007-r1/completion-review.json)、[坐标来源](evidence/render-20261007-r1/coordinate-source-review.json)、[查询与配套表](V0-VIDEO-PAIRING-20261007.md)。

真实画面：[帧6](evidence/render-20261007-r1/board-preview/call0.png)、[帧7](evidence/render-20261007-r1/board-preview/call1.png)、[帧8](evidence/render-20261007-r1/board-preview/call2.png)。PNG是ARM输出RGB的无损导出，没有电脑重新推理或修改姿态。原始PPM/三格式/日志在本机完整保留，大尺寸生成物已加入.gitignore，仓库保留预览和哈希核验。

## 对后续开发的参考

E1-C的CPU帧缓存与真实推理接入已通过工程门检，V0只有部分接口完成。当前设备枚举NV12/NV21输入与H264输出、720p符合尺寸范围，但实际planes/stride/sizeimage/色彩约定、编码结果和播放尚未验证。
参考VPU默认单平面CAPTURE与本轮查询不同，下一步应以实际MPLANE接口协商，不调用相机示例的MMU修改或套用固定SPS/PPS切片。

HDMI720p像素时钟/扫描/换帧映射仍未确认，且屏幕未连接，不写候选地址或宣称实屏通过。先准备独立VPU合成画面编码→文件解码→RTSP门检；HDMI需匹配当前BOOT配套及显示器，独立输出通过后才双路合并与长期验收。
全部验证进程已退出，SSH/SFTP已关闭。恢复从[new checkpoint](evidence/render-20261007-r1/next-checkpoint.json)开始，不重复已通过的CPU/Host/三帧门检。
