# 离线测试位置

**验证入口（2026-11-01）：** 当前工程默认PL CSI／PL骨架绘制开启、人物滤波CPU；[源码与依赖说明](../../../Deliverables/SOURCE-20261103.md)及[独立完整重建](../../../Deliverables/FPGA-REBUILD-20261101-r1.md)记录软件／核心RTL和完整实现的不同验证范围。现场状态以项目恢复入口的最后观察为准。

- `native/`：原生后处理、缓冲、显示、日志与资源安全检查；由上级 CMake 构建。
- `native/nexmon/`：实时解码／组窗检查，由 `tools/nexmon/board/CMakeLists.txt` 构建，共享 `src/input/nexmon/`。
- `sdk_stub/`：仅供 HDMI 资源测试使用的 SDK 替身，不进入正式目标。
- Python 输入与生命周期检查在 [../control/](../control/README.md) 的 `test_*.py`；PC 检查在 `../host/test/`。

本地检查不等于实板、实屏或长时稳定性验收；实际范围见 [审查记录](../resident/FINAL-REVIEW.md)。
