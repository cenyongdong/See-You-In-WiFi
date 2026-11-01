# F0接续门检：启动分配取证→常驻编码器（2026-10-08）

沿用代理执行与F0路线；本文件不是这些后续板测已经完成的证明。当前恢复先读[结果](PIPELINE-RESULTS-20261008.md)及`evidence/pipeline-20261008-r6/next-checkpoint.json`。不要重跑r2/r3/r4/r5或将r6失败重复目录覆盖。

## A1-S：先缩小启动分配问题

1. 新r7仅增加有界只读取证：进入编码器、S_FMT后、REQBUFS/MMAP后、prime后、STREAMON前后及首capture分别保存buddyinfo/pagetypeinfo/meminfo/vmstat；同时记录实际QUERYBUF各plane长度与映射占用。保留六缓冲、prime2、格式、cookie、所有权、控制、数学及deadline。新包/构建/Host门检后，仅一次180秒有限combined；异常完整保存停止。
2. 结合实际分配阶段定位哪些资源消耗普通高阶页、哪些来自CMA。总可用内存或测试完成后的页数不代替固件分配时的状态。
3. 修正候选须以取证及本机配套API为依据。可能路径为调整已证资源初始化先后、用协商得到的最小缓冲数量减少占用，或匹配BSP/MVX修复高阶连续申请。后两项必须明确修改范围/完整回归/预期效果，不能根据通用网上驱动盲改本机固件。
4. 内存规整只保留为显式诊断证据，不嵌入runner、不设持续后台规整，不改drop_caches/BOOT。保持启动失败可观察，不自动循环。首次成功与独立进程重复都需保留证据；不把常驻服务不重开误写成启动修复。

## A2：在有效初始化后保持常驻资源

一个Engine串行处理完整窗口；一个编码器上下文只创建一次，正常结束按STOP→LAST→归还→STREAMOFF释放。画面对象拥有NV12，队列最多2、最新结果策略及丢弃计数显式；初始NoInput与重复最新结果均记录，不能冒充新推理。

先纯Host测试队列容量、停止传播、producer异常与owned字节生命周期；再有限三帧＋重复回归，随后27窗口2Hz回放。真实编码PTS取单一steady_clock的采样时刻，源frame_id/invocation/新结果标志伴随图像传递；慢编码/队列满如何处理需预先写明，保持原NPU安全帧协议和单Engine。编码10fps重复策略不提高姿态更新速率。每次启动新目录、有界总时长、失败停止。

## A3：owned AU接入RTSP

确认实际packet分界/参数集/IDR及live555事件循环线程通知约定后再实现。CPU-owned AU进入有界桥，不保存已归还VPU指针。慢客户端不任意丢P帧；停止或按已证IDR边界重新开始。再测主机帧源、真实PTS、加入/保活/重连/有限退出及资源清理。

HDMI配套、显式色彩、整机5Hz与30分钟独立门检保持，不因有限文件接入提前宣布通过。无需重复索要未知资料；所有现有BSP/MVX资料先从本地索引查证。

## 工具与执行位置

- Windows仓库：`prepare_pipeline_package.py`建立新目录，`Build-Pipeline.ps1`在FPAI交叉构建，`pipeline_gate.py build`独立核验构建身份。源码或runner改变必须新包/BuildTag，不复用旧门禁。
- Lite新工作目录：传包/程序/build-result与同身份build门禁，独立`sh package/run-pipeline-stage.sh host-check`（300秒），完整回传核验后才传Host门禁并执行`combined`（180秒）。登录shell不单独启用`set -e`。
- Windows回传：`pipeline_gate.py host-check|combined --package ... --build ... --results ... --output 新文件`；失败不生成通过门禁。`review_pipeline_video.py`使用已有OpenCV环境检查实际视频；`review_pipeline_completion.py`当前只对应r6证据，不泛用到新修订。

身份、非有限、超时、页分配/VPU/SDK/总线异常或来源错配即停，回传全部部分记录；不自动重跑、复位、规整或升级HDMI/实时阶段。
