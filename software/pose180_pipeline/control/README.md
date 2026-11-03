# 启停、输入准备与运行管理

**验证入口（2026-11-01）：** 当前工程默认PL CSI／PL骨架绘制开启、人物滤波CPU；[源码与依赖说明](../../../Deliverables/SOURCE-20261103.md)及[独立完整重建](../../../Deliverables/FPGA-REBUILD-20261101-r1.md)记录软件／核心RTL和完整实现的不同验证范围。现场状态以项目恢复入口的最后观察为准。

本目录收拢原 `resident/` 下的 Python、Shell 和路由器管理源码；原生 C++ 已归到 [../src/](../src/README.md)。部署包内仍采用 `board/startup.py` 等原扁平布局，设备上的启停命令不变。

| 模块 | 文件 |
|---|---|
| 手动启停与预检 | `startup.py`、`boot_audit.py`、`startup_network.py` |
| 监督与退出清理 | `service.py`、`process_guard.py`、`bounded_log.py`、`run_hdmi_trial.py` |
| 双输入接口 | `input_config.py`；`dataset_input.py` 准备／校验官方片段，`csi_mat.py` 只转换原始 MAT 字节 |
| 实时采集管理 | `router_access.py`、`router_ctl.sh`、`router_watchdog.sh`、`router_guard.c`；[autostart/](autostart/README.md) 保存已安装开机服务源码 |
| 回放、测时与既有包准备 | `replay_retained.py`、`benchmark_ps.py`、`prepare_*.py`、`package_trial.py` 等；具体历史范围以对应记录为准 |
| 离线测试 | 同目录 `test_*.py`，与被测脚本一起维护，含双输入、EOF、监督和异常清理检查 |

正式构建／打包工具是 `../tools/build_startup.py` 与 `../tools/package_startup.py`。实时和官方预采入口的参数、数据来源与切换约束见 [双输入说明](../resident/DEMO-INPUTS.md)。这里只整理位置，不安装服务、不连接设备、不启动旧包。
