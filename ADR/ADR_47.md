# ADR_47：正式核心目录与保持行为的可读性重构

日期：2026-10-13。当前演示完整主链重构、等价拆分长函数、新建正式核心并保留原源码；明确由代理执行本机/FPAI、Lite CPU107及三窗口回归。本轮不执行60窗口，不恢复旧DATA坏读排查。

## 问题与决策

当前演示依赖的生产模块、历史检查器与故障实验原先混放在pose_v1；实际编译来源还依赖版本文件到构建别名的导出映射，直接整理同名旧模块容易改错对象。按sensor_protocol.cpp的四空格、同行花括号、中文步骤注释和逻辑间空行整理，迁入software/core六个功能目录；旧路径与旧内容保留，当前demo只编译新核心。

迁入21份CPP、31份HPP和1份Python。52份C++核心去注释后逐token一致，预处理/CPU/Gather/NPU/公开SDK读/诊断/帧协议/模型RAW/SDK/BOOT保持。应用参数解析提取demo_options；三个视频线程入口独立封装，原局部变量、异常捕获、线程启动与join顺序保持。Python展开连写步骤，补充职责注释；构建分为导出、SDK身份、厂商暂存和编译，原检查器只调整构建链接。

旧锁126份源码逐项核验；926份历史源码/脚本原字节保持。新锁追加三份原检查器来源，逐项锁定新核心并继续导出原编译别名。新锁不是旧源码逐位未变的声明，迁移前锁、原demo副本、路径/哈希映射和文档修订分别归档。

## 实施中发现与处理

当前D盘工作区没有原.local环境和参考；Docker/WSL及既有FPAI起初停止。仅启动既有工具运行时，没有安装或改变配置。git worktree核验定位到仍存在的dea3工作区，原NumPy2.2.5/Python3.10.21环境和CPU107/三窗口参考逐字节复制至新验证目录，旧工作区不写入。默认Python的fixture准备因NumPy版本不符在生成任何包或用例之前拒绝；未绕过版本门禁、未安装替代环境。

早期格式化的逐token门检发现三冒号空格会改变词法边界，先纠正生成器再进入编译；原源码始终未改。ARM的一条私有need(std::string)未使用警告，用相同编译选项对旧CPU适配源码重现，保留原重载并记录依据，未放宽其他检查。

## 实际验证

| 阶段 | 结果与范围 |
|---|---|
| 静态 | 原锁126、冻结926、52份核心C++逐token通过；生产目标仅用新核心，测试正文保持 |
| 本机 | 11组SDK无关检查器通过：TCP、AU、Host失败、阶段、调用证据、生产者计数、存储身份、读边界、显示IPC、预处理、渲染 |
| 独立字节对照 | 308/309/310的CSI记录新旧逐字节；预处理同时逐位旧实现及原参考；RGB/RGB565/NV12/NV21颜色及骨架画面逐字节 |
| FPAI | 56条命令成功，3个演示程序及11个回归程序ARM构建；15份SDK头与189份厂商文件匹配；仅旧基线同源unused-function警告 |
| Lite CPU | 原107例、12条注册、22输出、59600 FP32逐位通过，272.58892371秒，在原300秒预算内；Host-only，无NPU前向/规整 |
| Lite三窗口 | 3接收/3消费/3完整输出、0覆盖、3不同姿态；全部CSI、预处理、分数和姿态逐位308/309/310原参考；2Hz输入，354编码/294主机GUI解码 |
| 视频与清理 | 全3真实姿态来源和42关节通过；完整原H264354帧解码；正常drain/LAST、两STREAMOFF、join先于Engine销毁、进程与端口回收通过 |
| 最终身份 | BOOT/SDK库与开始相同、FPGA operating、内核日志相同，规整0、无重启/CMA/BOOT/模型/SDK修改；全部本批认证连接与播放器结束 |

本轮构建：.local/pose-v1-build/demo-refactor-20261013-r1；新板端目录/tmp/wifi-pose-demo-refactor-20261013-r1。CPU与三窗口分别保存原始回传tar、完整值、日志和SHA，未续用失败Session。

## 边界与证据

这是重构后的固定功能/数值/三窗口视频回归，不是旧DATA根因修复，不是60窗口重验、严格5Hz、长期、永久首次启动或HDMI验收。272.59秒CPU结果不构成延长300秒预算的许可。原警告不代表新增数学问题，但后续编译仍需核对实际SDK签名与身份。

[核心导读](../software/core/README.md)、[演示说明](../software/demo/README.md)、完整证据（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/README.md`）、迁移映射（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/source-migration.json`）、静态（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/static-review.json`）、本机（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/native-20261013-r1.review.json`）、构建（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/build-review.json`）、CPU107（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/board/cpu.acceptance.json`）、三窗口（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/board/short.review.json`）、视频（历史附件，当前仓库未附：`../tools/pose-v1/evidence/core-refactor-20261013-r1/board/short.video-review.json`）。
