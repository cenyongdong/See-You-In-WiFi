# 核心源码重构验证证据

范围与结论见[重构记录](../../../software/pose180_pipeline/REFACTOR-20261106.md)。本目录仅保存本地离线检查证据，未更新发布包或连接设备。

- `scope.json`：基线、修改清单与最终源码身份。
- `before-validation-r2/`、`after-final-validation-r2/`：新旧构建与回归命令、退出码及日志。
- `numeric/`、`numeric-final/`：数值报告、完整输出对照摘要和日志；每侧约 40 MB 的完整输出保留于本机 `.local/core-refactor-20261106-r1/`。
- `final-checks/`：CSI 恢复、开发测试、候选构建／CTest／HTTP 资源检查。
- `hardware-review.json`、`python-format-equivalence.json`：硬件未改动记录及格式化阶段等价检查。
- `initial-failures/`：初始基线依赖遗漏日志；其它原始失败与修复结果在相应目录并列保留。
- `doc-check/`：显式纳入新增文档的链接检查。

`/workspace` 是本机仓库挂载路径；`before/` 是隔离基线，候选包使用自身依赖。ARM64 仅编译，Python 容器采用 `--network none`，PC 仅使用回环和 mock。日志中的设备状态由测试桩提供。
