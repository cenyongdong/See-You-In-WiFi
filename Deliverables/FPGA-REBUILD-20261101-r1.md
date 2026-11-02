# r4源码RAR独立完整FPGA重建实测（2026-11-01）

结论：从最新交付RAR重新独立解压，使用包内工程级源文件、厂商IP／网表和声明的CSI v2增量基线，完成综合、链接／优化、实际放置、物理优化、实际布线、物理报告、原生BIT生成和Procise适配，全部原生阶段退出码为0。**新适配位流的配置载荷与包内原合格位流逐字节对应的SHA256相同，文件头仅日期和时间不同。** 本轮未连接开发板、未运行SDK、未写BOOT；现有默认位流保持。

## 输入、工具与复现边界

- 输入：`pose180-complete-sources-20261031-r4.rar`（本机交付，仓库未附），198429558字节，SHA256 `e4b1d3243550f34f92e5f4890a4cfb1a509889c6c51f9053ce03369d8d0f2b45`。
- 新解压源：`.local/frb1101-r1/source`；新构建目录：`.local/frb1101-r1/build`。从本轮新综合结果依次实现，未借用工作区已有r3优化／放置／布线结果。
- 使用包内710个厂商依赖文件，39个关键网表／检查点身份已核对。包内r2 `pipeline-routed-csi-incremental.dcp` 是原流程声明的增量参考；本轮重新执行了 `place_design`、`phys_opt_design` 和 `route_design`，不是只打开旧r3布线结果生成BIT。
- 使用随包 `tools/release/rebuild_fpga.py` 准备独立目录，1314项构建文件、76项路径重定位；设计源、目标、频率和时序约束按包内原值执行，未新增豁免。完整命令及PID／退出码见 [result.json](evidence/fpga-full-rebuild-20261101-r1/result.json) 和 [命令目录](evidence/fpga-full-rebuild-20261101-r1/commands)。
- 外部环境：已适配Vivado 2018.3（SW Build 2405991）、Procise 2025.1.1 temp／SVN 32494，目标JFMQL30TAI676H；Vivado侧为适配的 `xc7z030ffg676-2`。工具安装、许可和对应器件环境仍须另行准备，不能换用未经适配的普通器件库。
- 工程级硬件依赖已通过完整实现及配置载荷比对验证。部分可再生仿真网表按体积策略未附带，XCI扫描因此产生警告；它们未阻断本次综合／实现。这不代表全部厂商IP的闭源原始RTL或全部仿真产物都已开源交付。

## 实际原生执行

| 阶段 | 退出码 | 秒 | 日志 |
|---|---:|---:|---|
| 综合 | 0 | 216.2 | [原生日志](evidence/fpga-full-rebuild-20261101-r1/native/synthesis-banked.vivado.log) |
| IP／PS链接与优化 | 0 | 334.3 | [原生日志](evidence/fpga-full-rebuild-20261101-r1/native/opt-banked.vivado.log) |
| 增量参考加载、放置及物理优化 | 0 | 711.4 | [原生日志](evidence/fpga-full-rebuild-20261101-r1/native/place-csi-incremental.vivado.log) |
| 实际布线 | 0 | 360.5 | [原生日志](evidence/fpga-full-rebuild-20261101-r1/native/route-csi-incremental.vivado.log) |
| 物理报告与功能连接检查 | 0 | 154.5 | [原生日志](evidence/fpga-full-rebuild-20261101-r1/native/report-closure.vivado.log) |
| 原生BIT生成 | 0 | 129.7 | [原生日志](evidence/fpga-full-rebuild-20261101-r1/native/bit-closure.vivado.log) |
| Procise适配 | 0 | 3.6 | [原生日志](evidence/fpga-full-rebuild-20261101-r1/native/procise.log) |

原生阶段累计 1910.2 秒（约 31.8 分钟），不含解压、准备、人工读取报告及归档时间。解压与准备约 95.4 秒。完整原生日志按实际结果保存，警告未删改。

## 最终物理结果及既定例外

| 检查 | 本轮结果 |
|---|---|
| Setup | WNS +0.030 ns，TNS 0，失败端点0 |
| Hold | WHS +0.029 ns，THS 0，失败端点0 |
| 路由 | 97096／97096条可路由网络全部连通；路由错误0 |
| 内部未约束端点 | 0 |
| 总线偏斜 | 最小裕量 +2.064 ns |
| CSI模块 | setup +0.485 ns，hold +0.109 ns |
| 既有滤波模块 | setup +0.951 ns，hold +0.103 ns |
| 资源 | LUT 42986；FF 56026；Slice 17396；BRAM36 258；DSP 34 |

原生总体时序仍写 `Timing constraints are not met`：WPWS −0.409 ns、TPWS −0.479 ns、2个端点，均为[既定AI时钟模型定点例外](../FPGA/hdmi_candidate/BOARD-RELEASE-20261016.md)的 `clkout1_buf/I`（−0.409 ns）和 `plle2_adv_inst/CLKOUT0`（−0.071 ns），没有扩大例外范围。

完整原生DRC含137项记录，其中2项Error为原厂030ai GT适配已有的REQP-52／REQP-56，分别对应原GTXE2_CHANNEL／GTXE2_COMMON实例。原始完整报告保留该状态；原流程的位流前厂商适配检查按既有方式执行，本轮未新增DRC降级或豁免。I/O及CDC既有警告也保留，不能把本结果写成严格零违例或整机实板验收。

路由中间日志曾有WNS −0.031 ns；最终重新打开已生成检查点后的原生时序报告为+0.030 ns，setup／hold均满足。中间原值仍保留，不以中间估算代替最终结果，也没有修改源／约束以放行。

原始报告：[完整时序](evidence/fpga-full-rebuild-20261101-r1/physical/timing-final.rpt)、[脉宽](evidence/fpga-full-rebuild-20261101-r1/physical/pulse-width.rpt)、[路由](evidence/fpga-full-rebuild-20261101-r1/physical/route-status-final.rpt)、[DRC](evidence/fpga-full-rebuild-20261101-r1/physical/drc-final.rpt)、[总线偏斜](evidence/fpga-full-rebuild-20261101-r1/physical/bus-skew-final.rpt)、[资源](evidence/fpga-full-rebuild-20261101-r1/physical/total-utilization.rpt)、[时钟](evidence/fpga-full-rebuild-20261101-r1/physical/clocks.rpt)。HDMI／overlay／filter CDC及原生功能连接检查结果也在同一physical目录。

## 新位流与可恢复产物

- 新Procise适配位流（本机留存，仓库未附：`FPGA-rebuild-artifacts-20261101-r1/pose180-csi-v3-rebuilt.bit`）：5980609字节，SHA256 `746e86a6c92399248297dce7141838d415399cf41b89a6a5ba237302ef750607`。
- 配置载荷SHA256 `e041e6230443631e93a848eaa888f536053145719c8e1878025e60fbf30e620b`，与源码RAR内合格BIT完全一致；完整文件SHA不同是因为c／d日期时间头不同，其余头字段和载荷相同。[比较记录](evidence/fpga-full-rebuild-20261101-r1/bit-identities.json)。
- 原生BIT、linked／opt／placed／physopt／routed等本轮恢复检查点保留在 `.local/frb1101-r1/build/.local/csi-preprocess-20261031-r3/`；原始输入树及全部工具stdout也保留。本轮生成的文件不替代已发布BIT／BOOT，不构成上板验收。
- 本次验证对象为身份固定的r4 RAR；新增报告作为压缩包旁的独立验证证据保存，未为补报告而改变被验证压缩包的内容。
