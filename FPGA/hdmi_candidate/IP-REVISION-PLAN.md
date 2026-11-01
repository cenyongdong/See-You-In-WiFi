# 隔离工程IP修订升级的已批准范围与结果

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

2026-10-15已获授权：使用现有2019.1在隔离副本核对/重建同配置IP，不改原参考、不安装工具、不改全局数据库；若必须升级IP，另行讨论。

白名单修订升级与严格门检；实际升级38.897797秒exit0，但原字面门检拒绝。进一步审查后的有限例外另获批准，新r3生成/后检及AXI3原生互联综合通过，PS原生端口适配失败停止。旧门检false不回写；[生成报告](../../tools/pose-v1/evidence/hdmi-ip-generation-20261015-r3/REPORT.md)、[当前恢复入口](PS-ADAPTATION-STATUS.md)。以下保留升级前证据和当时提出的操作范围，不作为再次审批请求。

## 实际工具结果

新副本297文件/163773137字节与原参考SHA一致。现有Vivado2019.1实际IP状态查询63.445秒exit0；未运行upgrade_ip、generate_target或JFM hook。报告显示21个顶层/BD根IP中16个需要“IP revision change / Upgrade IP”；get_ips -all含子核28个，其中23个IS_LOCKED=1、5个未锁定。版本号看似相同，但修订号不同，不把同名VLNV当作已获同配置重建许可。

| 根IP类型 | 实例数 | 原修订→2019.1修订 | 本地changelog要点 |
|---|---:|---|---|
| FIFO Generator13.2 | 7 | Rev3→Rev4 | 修正部分common-clock XPM_CDC目标时钟接线；约束waiver/子核修订变化。不能一概视为纯元数据 |
| Clocking Wizard6.0 | 4 | Rev2→Rev3 | GUI修复及器件支持；仍核对实际倍/分频、时钟源及派生参数 |
| MIG4.2 | 1 | Rev0→Rev1 | 2019.1软件支持；DDR器件/位宽/引脚/1250ps/PHY比例等必须保留并审查生成差异 |
| AXI Interconnect2.1 | 3 | Rev19→Rev20 | 子核修订变化；涉及内部crossbar/register_slice |
| xlconcat2.1 | 1 | Rev1→Rev3 | 包含SENSITIVITY元数据及BD显示字符串变化 |

5个未锁定实例：两份proc_sys_reset、processing_system7自定义厂商仓库核、util_vector_logic、smpte_sdi。**不升级PS自定义核，不替换它为Xilinx原版，不升级AI_Mate EDIF。** 所有原始日志、IP-status.rpt及修订来源均已保留。

## 建议批准的操作

只对上表16个锁定根实例及其受管理子核，在另一个新隔离目录升级至本机2019.1已有相同主版本的修订，不安装/下载任何新IP。先保存CONFIG全量快照、XCI/BD/原配置与相关文件SHA，按明确白名单升级，不对所有IP运行无差别upgrade_ip。

升级后逐项核对原有CONFIG值及接口/地址/复位、FIFO位宽/深度/读模式/延迟、时钟倍分频、MIG内存型号/布局/时序、AXI宽度/时钟转换等。新默认项/推导参数/端口或地址差异单列；关键契约变化、升级报错、IP仍锁定或身份变化即保存停止，不能静默接受“默认值变化”。先通过差异门检，再生成中间产物并接Procise展开/实现验证；不凭Vivado报告代替Procise签核。

预算建议：修订升级/配置审查步骤180秒；生成/综合/实现的执行预算随实际规模分阶段记录，失败不自动重试、不复用失败目录、不擅自延长。此确认只涉及隔离IP修订变更，不包含全局数据库/hook安装、PS配置修改、BOOT替换或额外重启。已批准板测授权持续有效，待有真实可下载候选和安全切换/回退条件后执行。

若不同意修订升级，则保留当前工具/原IP，需取得与原修订匹配的已生成可用网表/配套工程后继续；不自动改装2018.3或删掉PS/NPU/DDR路径来绕过。

证据：[实际IP状态报告](../../tools/pose-v1/evidence/hdmi-system-20261015-r1/IP-status.rpt)、[本轮记录](../../tools/pose-v1/evidence/hdmi-bringup-20261015-r1/REPORT.md)。
