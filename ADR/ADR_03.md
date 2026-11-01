# ADR_03：平台、启动介质与可追溯构建

- 日期：2026-10-08；历史范围：2026-10-01起。
- 状态：已有范围归档；底层存储故障部件及长期可靠性不作扩展结论。
- 决策：先确认实际字节、配套身份与分阶段结果，再进入下一环节。使用隔离目录和完整日志，不把工具成功提示等同于实板功能。

## 难点、尝试与解决结果

| 问题/影响 | 证据和处理 | 结果与限制 |
| --- | --- | --- |
| FPGA引脚、电平、初始化和JTAG目标易混淆 | 以Lite原理图核对100MHz AC14、LED J1/M6/H7/J8及1.5V；FDC锁定，XSim自检，再Procise原生综合/布局布线/时序/位流身份和JTAG链复核 | 原生及MCP灯序现场通过；xlconcat IP从Vivado到Procise实板交接通过。只是PL/IP方法验收，非PS/NPU/HDMI工程验收 |
| MCP工具跨EDA边界及长任务状态 | 通过隔离灯序和真实IP工程验证工具输出、任务状态、位流与原生实现，不把调用成功代替报告/板测 | [流水灯](../tools/mcp-validation/led1324/RESULTS.md)、[IP交接](../tools/mcp-validation/ip-reuse/RESULTS.md)；不扩大为任意Tcl/JTAG能力 |
| 原生工具的目录/参数和报告适配差异 | launch_run回到工程根，生成位流前显式切rundir；JTAG显示名DIGILENT/JTAG-HS1不等于init_chain参数usb-jtag-hs1；BGN Disallow*默认标记误判及XSim UTF-16/BOM识别按实际日志修正 | 先停止下载并重构建复核，保留原失败；不隐藏LED no_output_delay，也不套用于同步外设 |
| 当前工具会话Vivado启动误选不存在32位程序 | 只读诊断定位架构环境变量空，临时测试子进程AMD64通过；后只在Vivado MCP子进程配置PROCESSOR_ARCHITECTURE=AMD64，保留其他配置字节及备份，重载后实测 | 新stdio及当前工具会话版本/错误恢复/XSim均通过。未改系统环境或EDA安装；源码/IP元数据xc7z030不是实板器件，实板仍JFMQL30TAI676H |
| imageUSB校验失败、无串口、BOOT头损坏 | 镜像有512字节专用头，跳头计算MD5/SHA1与内置值一致；FAT簇链提取9个启动文件后卡仅1个匹配。更换读卡器仍异常，H2testw局部950MiB中835MiB错误 | 换SD卡后人工确认串口/登录正常，后续分区扩容和SSH通过。旧卡链路失败明确，但不能确诊假容量/读卡器或宣称全容量已验。原始诊断路径见[Done启动记录](../Done.md) |
| 扩容/SSH地址与运行配套不明确 | 先核对实际mmc分区和文件系统，再人工操作扩容；保存板端查询、BOOT/SDK/设备及库身份 | 后续基线SDK3.39.0、device25122301/icore24160628、BOOT ff350477…8b31ef；不替换历史BOOT，也不将暂时断网误判为程序失败 |
| Windows开发环境跨窗口丢失 | VsDevCmd初始化仅作用于所在CMD，另开的where cl无法验证它；同窗口确认x64 cl，WindowsSDK仍未有效识别 | Lite交叉编译成为本轮路径；不为此修改base或强行开展Windows Host构建 |
| 容器没有python3、实际SDK签名不符、PowerShell把stderr当异常 | SDK身份审计移至主机；按实际头使用Array::set；完整捕获stdout/stderr再检查真实退出码 | [CPU编译修正](../tools/pose-v1/CPU-ADAPTER-COMPILE-FIX-20261006.md)。不安装容器Python、不改SDK、不回写旧产物哈希 |
| 清单CRLF、缺验收gate、/tmp消失或set-e登录shell退出 | 生成LF清单并校验正确文件；验收绑定当前程序/包；新目录mkdir前验证，独立sh执行门检，不在登录shellset-eu | 缺gate属于预检未启动，非推理失败。已有目录非0须保留，不能删除或把旧gate改名冒充新验收 |
| 本机生成脚本引号、ODR冲突和Host预算 | 复杂源码用补丁/独立Python；私有辅助Case进入匿名namespace避免vector弱符号布局碰撞；依据实际图解析开销调整外部Host预算420s | [难点D01/D02/D08](../DIFFICULTIES.md)；保持107例/拒绝规则与硬件180s预算。超时历史保留，不把95例记完整通过 |

## 后续参考

源码→包载荷→构建副本→SDK头/库→ARM程序→板端输入/日志/输出均记录SHA256。新身份重新生成对应门禁，不覆盖失败。只读审计与设备初始化、部署与前向分开。旧路径D:/FPGACompetitionProject为历史证据来源，现工作区报告保留其来源，不伪造迁移后的原始文件。

生成环境、原始大张量、二进制和码流留在本地并由.gitignore控制；可提交摘要/清单和审查报告不能替代本地完整证据。暂停期间关闭测试/连接，不自动唤醒；恢复先读最新检查点。
