# 升级后衍生字段差异审查与有限继续条件

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

2026-10-15，已获白名单修订升级与严格门检授权。原始字面CONFIG门检和首次参数传播后的门检均真实拒绝，报告不回写。提出有限规则时尚未运行正式generate_target；后新r3已生成并通过参数/端口后检及AXI3有界路由/原生互联综合，完整系统当前受PS7→PCPU7扩展端口不匹配阻塞。升级工具自动产生的例化模板与后续正式生成分开记录。[实际报告](../../tools/pose-v1/evidence/hdmi-ip-generation-20261015-r3/REPORT.md)。

随后明确回复“批准有限例外并继续生成验证”；以下有限规则已获批准。原严格拒绝继续保留，生成前另建独立契约门检。

## 已验证不变的部分

- 28项活动XCI的全部原有HDL MODELPARAM_VALUE参数与原参考一致；12个独立根IP及4个BD根IP的配置保持，PS自定义包及AI_Mate原网表未改。
- BD重新传播/校验后，数据位宽、AXI3协议、有效时钟频率和ID位宽恢复原配置。初始32位/AXI4是未完成传播的中间默认状态，不作为结果接受。
- BD实际连线成员、地址映射、标量端口方向/位宽和接口声明保持；连线列表排序不影响连接，两个ID_WIDTH的value_src从default_prop改default但实际均为12。
- 4个子核的CLK2X元数据10MHz→100MHz，但两版本REG_AW/AR/W/R/B都仅为7/1；本机原语包component.xml明确只有任一REG_*=11才启用CLK2X，两侧均未启用，也没有aclk2x连线。

## 尚未接受的差异，需明确有限范围后才能生成

1. 五个受管理子核的Component_Name编号改变，BD层级角色一一对应、连线和地址不变。应按角色记录映射，不能改旧XCI哈希伪装相同。
2. 四个register_slice新增17个PARAM字段，包括HAS_*、MAX_BURST_LENGTH、NUM_*等。它们是当前修订新增字段，全部值已保存；实际HDL模型参数未增改，现有接口位宽/协议仍一致，仍需生成后验证端口和握手，不能仅凭参数相同宣称逻辑等价。
3. 四处RST.POLARITY不再显式写入新XCI，本机component.xml默认仍为ACTIVE_LOW、映射到aresetn；须按默认解析结果核验，不能把缺省当作未知值或任意忽略。
4. `/axi_interconnect_4/m00_couplers/m00_regslice/M_AXI`的只读NUM_READ/WRITE_OUTSTANDING元数据由2→8。28项HDL参数中相关原值均未变，但广告能力元数据确有变化，不能据此证明实际允许更多在途事务或擅自提高测试负载。

已尝试在新隔离副本恢复该接口原标注，Vivado报告BD41-738：它是受管理appcore内部对象，不能直接修改；此尝试exit1已保存停止，没有强行修改XCI或厂商源码，没有继续正式生成。原始失败不抹去。

## 建议的有限继续规则

允许且仅允许上述已列出的受管理名称/缺省解析/未启用时钟/新增字段/只读接口元数据差异进入候选生成；旧字面门检仍记拒绝，新建单独的契约门检及例外记录。全部原有实际HDL参数、外部接口位宽/协议/复位、地址与连线必须保持，未知差异继续拒绝。

生成后核对实际RTL/模型参数和端口，尤其确认未引入REGION等额外活动端口、寄存器级数或自动流水。对AXI背压/完整burst/在途读与停止进行仿真；对板端共享模型原值及显示做分项回归，测试负载不因元数据8而扩大。没有生成/仿真/Procise实现及安全切换条件前，不下载候选。PS包、AI_Mate、BOOT、模型/RAW/SDK仍保持；旧DATA暂停。

另外，原BD时钟ASSOCIATED_BUSIF含不存在的gp0_monitor/gp1_monitor并产生BD41-1287。建议在候选中仅移除此两条悬空关联，保留实际GP接口关联和全部连线；作为明确记录的元数据修正，重新validate并相关CRITICAL WARNING消失，不绕过检查。

若不接受这些有限差异，则保持严格拒绝和停止，等待原修订可用配套；不自动更换工具版本、修改全局数据库或减少系统模块绕过。

证据：[原始严格门检](../../tools/pose-v1/evidence/hdmi-ip-revision-20261015-r1/strict-config-gate.json)、[传播后门检](../../tools/pose-v1/evidence/hdmi-bd-validation-20261015-r1/post-validation-config-gate.json)、[HDL与总线逐项比较](../../tools/pose-v1/evidence/hdmi-bd-validation-20261015-r1/HDL-and-bus-contract-review.json)、[只读属性恢复失败](../../tools/pose-v1/evidence/hdmi-bd-metadata-20261015-r1/stderr.txt)。
