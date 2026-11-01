# 端到端演示的实施与验收历史

2026-10-13从AGENTS.md迁出，按主题保存原记录；原文“当前”“已批准”“下一步”和暂停/恢复只表示当时状态，不是现行进度或新的执行授权。最新进度见[PROJECT-PROGRESS](../../../PROJECT-PROGRESS.md)，执行规范以[AGENTS.md](../../../AGENTS.md)为准。源行编号与迁移清单用于追溯；不改写原失败、修订或验收边界。

<a id="a003"></a>

## A003 · 端到端演示本批完成（2026-10-11）

来源：整理前 AGENTS.md 第3–4行。

- 端到端演示本批完成（2026-10-11）：指定software/demo与ADR/TechDetails.md，旧DATA排查继续暂停。r5程序82201e97…f5d987e0在新r4目录，Native/ARM协议及short3/demo60真实CSI→PS/NPU→独立显示→VPU H264→RTSP/TCP主机GUI过；63真实推理/989编码/869实时解码、全3/60来源及42/840关节，60窗口2Hz/0覆盖/60不同姿态。前三308/309/310输入和完整输出逐位旧参考，其他57仅结构/有限/选择/映射，不称全精度过；旧Host107/59600身份复用非新跑。旧152软件/CPU/Gather/模型RAW/SDK/BOOT/745/reset1/公开read桥和异常两晚源保持。一次获准重启已执行且用完；首失败39.27594ms规整无效、入口目录与Producer配置缺失失败保留，新demo_engine修正通过，成功两阶段规整0。正常drain-LAST/两STREAMOFF/join后Engine毁、最终BOOTSDK模型内核同/FPGA operating/无进程端口过，全部SSH/SCP/播放器结束，无后台。当前DEMO-RESULTS-20261011/ADR_45/TechDetails及evidence/demo-20261011-r4 completion/next-checkpoint；原producer-prepared恢复入口不改、不重跑旧Session。严格5Hz/长期/HDMI/永久首启动/零拷贝未过，管理83/100保持。以下当前及准备条目为历史。

<a id="a005"></a>

## A005 · 演示启动恢复授权（2026-10-11）

来源：整理前 AGENTS.md 第5–6行。

- 演示启动恢复授权（2026-10-11）：明确允许一次可控重启后验证演示。该一次systemctl reboot已执行，重启前无项目进程/39001和8554监听，BOOT/SDK前后逐位同、新boot-id/FPGA operating/普通512KiB单位980；未清缓存/改CMA/BOOT/模型/SDK。系统启动清空/tmp，全部首失败已完整在本机归档；仅新目录只读补审计，无第二次重启。后续仅新demo目录协议→三帧→60帧，旧DATA排查仍暂停，原异常保护/读取保持。

<a id="a007"></a>

## A007 · 演示系统优先（2026-10-11，新要求）

来源：整理前 AGENTS.md 第7–8行。

- 演示系统优先（2026-10-11，新要求）：暂停PRODUCER-PREPARED-NEXT的当前故障排查，保留其全部首次错误、晚源读取及检查点；改为实现software/demo端到端演示。输入只读D:/Person-in-WIFI-3D/Person-in-WiFi-3D-repo/data/wifipose预采CSI，主机模拟实时回放→板端TCP/PS预处理/既有PS+NPU Engine→独立显示子进程渲染/NV12→常驻VPU H264→RTSP主机实时显示，HDMI不纳入。复用已验证public-read桥/CPU注册/数学/帧协议/SDK/模型/BOOT；默认2Hz真实窗口、10fps预览，NoInput/重复分别记录，现有异常保护和原读取保留，不伪称根因已修或5Hz长期验收。代理实现、构建、部署和有界演示核验，运行异常保存停止。完成后ADR/TechDetails.md归档各技术实现、证据及限制；ADR_45记录整合取舍。
