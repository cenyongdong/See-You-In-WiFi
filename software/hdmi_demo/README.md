# HDMI独立接入应用

**版本定位（2026-10-29）：** 本页保留早期工程、兼容接口或对应批次结果，文中的“当前”只指该版本。现行 180-query 主链在[主工程](../pose180_pipeline/README.md)，运行及验收范围见[最终进度](../../PROJECT-PROGRESS.md)；旧命令不作为最新部署入口。

2026-10-25入口说明：新的180-query主图与有界主机模拟输入集成见[主推理链](../pose180_pipeline/README.md)，该句仅描述 10 月 25 日的准备阶段，后续有限实板已完成；本页保留原100-query三窗HDMI应用及当时验证，不作为新链默认运行入口。

更新：2026-10-21，仅整理状态。**r13已完成一次健康启动下三窗新推理→HDMI有界闭环，人工确认三帧切换正常。** r25已在SDK前再次复现D45，D44首次reader故障、严格实时及联合长期未通过。最后实板核验已回原BOOT；故障实施继续暂停、不删模块。[结构与阶段结果](../../FPGA/hdmi_candidate/INTEGRATION.md)、[工程师交接](../../FPGA/hdmi_candidate/HDMI-FAULT-HANDOFF.md)、[当前恢复入口](../../FPGA/hdmi_candidate/RESUME.md)。

## 结构与设备生命周期

[main.cpp](main.cpp)通过导出的共享Engine运行固定三窗。Engine主线程在Session.apply及绑定核验后，用显式`Config::on_device_ready(Device const&)`交付同一设备；HDMI适配不额外Open或使用另一个进程的分配器。hook由构建脚本加入隔离导出副本，不能把本目录CMake模板直接当作完整正式核心工程。

PS沿用[skeleton_render](../core/display/skeleton_render.cpp)完成候选选择、投影、骨架和文字绘制；[hdmi_canvas](../core/display/hdmi_canvas.cpp)只做1280×720 RGB24→1920×1080 RGB565LE双线性转换。[hdmi_output](../core/display/hdmi_output.cpp)通过公开SDK分配两帧、写入与操作候选CSR；PL完成AXI读帧、FIFO、扫描和TMDS。新应用不启动VPU／RTSP，未将骨架绘制迁到PL。

每份实际输出先保存input／scores／poses，再按[ADR_48 v2](../../ADR/ADR_48.md)比较：输入／全部分数逐位一致，输出有限，score>0.2候选最大关节三维偏差≤3mm；低分位置误差仍保存。三份新骨架各约5秒，重复扫描不计新姿态；先STOP确认和释放显示，再销毁Engine。

两帧共8,294,400字节，地址由SDK实际分配、64字节对齐并核对池范围；不硬编码、不与模型重叠。采纳预算200ms，close预算500ms。STOP须新响应、匹配停止ID、safe_idle和在途位清零；ready、计数或缓存同步不能代替。SDK／数据异常先保存原错并停止受影响负载，不自动重试。

## 入口与构建位置

| 入口 | 用途／边界 |
|---|---|
| [frame_probe.cpp](../../FPGA/hdmi_candidate/software/frame_probe.cpp) | `--memory`实际帧内存对照，`--patterns`两图案；`--user-requested-repeat`仅为当时已授权、已归档安全状态的重测，不是通用自动恢复 |
| [saved_skeleton.cpp](../../FPGA/hdmi_candidate/software/saved_skeleton.cpp) | 回放S11_01_308／309／310的历史真实结果，各约8秒，无新Session／NPU推理 |
| [main.cpp](main.cpp) | 共享模型新推理三窗、完整保存与门检、显示与释放；参数为共享包、新输出目录、`--allow-device-init` |
| [build_hdmi_display.py](../../FPGA/hdmi_candidate/scripts/build_hdmi_display.py) | 新revision构建frame_probe；`saved-`前缀选择回放应用 |
| [build_hdmi_shared.py](../../FPGA/hdmi_candidate/scripts/build_hdmi_shared.py) | 构建共享Engine联动导出副本；r9观测适配另见[读观测共享构建说明](../../FPGA/hdmi_candidate/scripts/build_ai_read_shared.README.md) |

执行位置Windows `D:/FPGACompetitionProject`，交叉编译容器FPAI，ARM64 GCC9.4／CMake3.24.2／SDK3.39.0。构建依赖已核验的`.local/shared-resident-source-20261015-r1`与共享模型交付包；使用前核实实际存在及保护身份。脚本在证据树和.local创建新目录，保存来源、依赖、ARM产物与退出码，拒绝覆盖失败证据。板端旧`/root/hdmi-display-20261017-r1`仅是历史执行位置，不能假定仍有可复用进程、句柄或有效包。

## 实际验证与未完成项

2026-10-17在r5候选下完成实际SDK双帧内存、两图案、三份历史骨架及在途STOP／释放；首次图案fault2保留。同日新模型在Session.apply上传参数时失败，发生在设备hook之前。观测v2也在独立4KiB DMA失败；这些原失败不能由后续通过覆盖。

2026-10-18复用r9，r13经Open前健康门和四档≤1MiB完整DMA门检，完成3次新推理、3帧PL采纳及STOP释放／Engine销毁；现场确认FRAME 1000000→1000001→1000002。每窗数值门和完整输出保存通过，受检最大偏差0.9765625mm。原始证据为[verification.tar](../../tools/pose-v1/evidence/hdmi-preopen-20261018-r13/verification.tar)内`run/shared/inference/frames.jsonl`、`summary.json`及完整输出；回退在[closure.tar](../../tools/pose-v1/evidence/hdmi-preopen-20261018-r13/closure.tar)。没有将回放计为新推理。

随后已纠正按键映射：SW6／F8能清零观测器，旧SW7结果不能检验F8复位；r24实际见证PL互联复位，r25同BOOT仍在SDK前异常。不能把CSR清零或一次健康Open当作PS FIFO复位／启动修复。诊断与假设见[D44／D45](../../DIFFICULTIES.md)。启动稳定性、严格实时、连续HDMI长期和PC双路并发尚未通过。旧DATA独立暂停、FAT未修；本页命令与历史包不授权恢复、重启、BOOT替换或重跑失败负载。
