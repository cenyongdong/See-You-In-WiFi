# 当前 CSI v3 集成源码

这里保存当前 `probe-free-drain-overlay-csi-v3` 的两个集成模块。初始内容来自已验证 CSI v3 构建输入；本轮只整理自研连接区域，验证状态见 [重构记录](../../../REFACTOR-20261104.md)。

- [hdmi_board.sv](hdmi_board.sv)：当前带骨架覆盖层接口的板级显示模块。
- [ps_ai_peripheral.sv](ps_ai_peripheral.sv)：包含厂商 PS／AI／DDR 接线和项目自研 GP 路由、CSI、显示接入；厂商区域保留原署名和接线。

`../integration/hdmi_board.sv` 是早期无覆盖层的隔离仿真变体。两个文件定义相同的模块名，不得用递归通配符同时加入工程。当前整机应按 [显式源码映射](../../../current_sources.json) 和 [构建入口](../../../../tools/release/prepare_refactored_fpga.py) 选择输入。

厂商与基线依赖由合格源码包提供；当前自研输入从工作源码复制到全新构建目录，并保存来源与哈希。旧发布包和历史构建目录不被覆盖。现有默认 BOOT 与设备恢复仍以 [RESUME](../../RESUME.md) 为准。
