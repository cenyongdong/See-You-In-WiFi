# 参考位流定点豁免与受控板测发布

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

2026-10-16，解除两处原厂AI时钟模型Min Period所致HELD，并新位流接入项目、进行实时实板验证。本次发布状态为 **RELEASED_FOR_CONTROLLED_BOARD_TEST**；原始报告仍为时序失败，整机签核尚未完成。当前未下载。下载器重连后扫链已恢复；新发现该发布参考位流的配置载荷与当前所选BOOT相同，重复加载不会引入HDMI修复。

## 特批范围

例外标签“已知原厂安全占位时钟”作为工程例外标签记录；“原厂bug”“安全”“与核心功能无关”及占位语义尚未独立证实。已经证实的是：原厂AI_Mate网表包含该时钟模型，路由检查点可见叶负载为ai_core_clk_locked_reg/C。在该既定例外范围内，可以继续受控板测，无需再次批准这两个检查。

共同路径前缀为`U0_ps_ai_peripheral/ZGolo/u_AI_Mate_top/clkrst_wrapper_u0/AI_CORE_CLK/inst/`，共同为`clk_out1_AI_CORE_CLK_ST`、报告周期1.000ns。

| 定点对象（前缀后） | 检查 | 要求 | 原裕量 | 放行方式 |
|---|---|---|---|---|
| clkout1_buf/I | Min Period | 1.409ns | −0.409ns | 定点例外 |
| plle2_adv_inst/CLKOUT0 | Min Period | 1.071ns | −0.071ns | 定点例外 |

WPWS−0.409ns、TPWS−0.479ns和两个失败端点按原报告保存；不改库、频率、约束或AI_Mate，不通过设置全域false_path包装通过。没有新增其它时序/DRC豁免。CDC及外部时序未完整签核须在实测结果中继续披露。

## 发布身份和功能范围

实体位于新发布目录（本机留存，仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/released-reference-products`），源为上一批封存的HELD目录，源目录不回写。

| 产物 | 字节 | SHA-256 |
|---|---:|---|
| ai7030_edif_top.bit | 5,980,025 | 5a435937c5a0be8a3bce0db77555bd85e67c4b4ebf450c5afbd662e779e2fb50 |
| ai7030_edif_top_disable_icap.bit | 5,980,609 | ab9af4b8679a8f4bbe958d4dadbc78b81156da4a3b5a67c6510c9d1269befb78 |

后者经过原厂30TAI Procise ICAP/VCCM后处理，为拟临时配置的发布实体。原始头部`7z030ffg676`来自已核验JFM适配链，目标是JFMQL30TAI676H，不能仅按Xilinx头部用通用下载器直接处理。

本次实体为**原厂参考RTL重建**，未接入独立修复的HDMI scanout/独立时钟/新CSR/stop-drain接口；原参考ASCII常量等源码保持原样。参考位流实板测试用于验证构建/适配链，不计为HDMI修复候选或实时性能验收。修复候选仍按[集成契约](INTEGRATION.md)推进。

## 已执行预检和回退

板端192.168.126.49只读核验：BOOT SHA `ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`，六份SDK库同基线，FPGA operating，无相关设备FD owner。SSH主机密钥固定，认证只在内存提供，连接已结束。

回退位流（本机留存，仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/rollback/ai7030_top_disable_icap.bit`） SHA `6818b7f8dea8e0f9dbda1b0d11127255ee1ba8876326bc7708a633641784f72e`。重新核验当前选择BOOT偏移186816、PL分区5980464字节；32位字节交换后全部回退载荷一致，余4字节填充。该核验不证明热重配或回退已实测。

首次两次扫链均0 cable/无FTDI；随后接通下载器，Windows实际枚举USB VID0403/PID6014、210512180081。依据这一外部变化建立r3新目录，Procise实际扫链4.029秒exit0：jfmql30、IDCODE0x9372c093、part 0，ps_dap part 1、IDCODE0x6ba00477。未执行program_bit；以后下载前仍需新扫链，不永久假设编号。

当前Linux仅暴露FMSH FMQL FPGA Manager，未暴露fpga_bridge/fpga_region；本轮没有验证在线隔离/停止接口。无FD owner不证明PL在途AXI请求已排空，不写猜测的SLCR寄存器、不用FPGA Manager强行绕过条件。

## 执行与验收顺序

1. 下载器接通后新目录重新扫链；身份/设备不匹配停止，不自动改目标。
2. 先取得运行中PS/PL安全停止或隔离证据，准备以上回退实体及其恢复条件。若必须再次重启或修改启动配置，先说明具体操作影响；本次不包含该范围。
3. 仅执行临时配置；不覆盖BOOT。下载前再核SHA，保留Procise原生完整日志和STAT回读。下载超时/配置错误停止，保存现场，不盲目重试。
4. 成功后先核PS连接、内核、FPGA状态、SDK/显示版本及资源，再进行静态画面和显示器OSD核验。只能向已验证接口写入，不能用尚未映射的候选CSR。
5. 静态链路成立后，按冻结共享模型和既有数值契约实施分阶段实时测量，分别报告完整帧/欠载、数值、端到端延迟与吞吐；旧DATA调查不恢复。参考链路测试不能代替修复候选的stop/drain、独立148.5MHz/1080p60及并发验收。

本轮证据：报告（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/REPORT.md`）、授权与身份（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/release-authorization.json`）、实板原值（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/host-permission-r2/board-audit.json`）、扫链复核（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/chain-review.json`）、回退身份（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/rollback-identity.json`）。


## 载荷复核后的执行决定

新发布后处理bit与所选BOOT的回退bit，完整配置载荷均5980460字节，SHA-256均`657da80bb5eff97c917cf3a6c8c5b40a331b814dd840b5ac6a0bda44fb8a935d`，逐字节完全相同；Docs/BIT/30tai_lite_detpost提供的位流也相同。区别在.bit头部日期等元数据。原始未后处理bit载荷与后处理载荷不同，未把二者混用。

使用Procise实际create_boot_image及原厂BIF的-fmql、apu_x32等原参数，先用所选原bit及三份原PS文件生成对照BOOT；结果7023552字节、SHA与当前BOOT完全相同，验证了此封装路径。再只换入新发布bit得到离线试制BOOT，其PL分区仍0字节变化，只有偏移2388和2392–2399共9字节变化，对应32位交换后的映像名称。先前“应只改变PL、其余应相同”的严格断言失败原样保留，不把工具exit0当通过，也不部署此试制BOOT。没有必要为了这些名称字段修改启动文件或重启。

这证明**文件配置载荷相同**，不等于对运行中FPGA做了完整配置读回。当前板端BOOT哈希相符，FPGA operating；若要证明运行中配置的完整身份，还需合适的硬件读回或受控加载证据，不能仅用版本号替代。

因此本轮两处Min Period特批及发布有效，但不重复加载相同参考载荷来宣称完成新的HDMI修复验收。下一有效新配置必须先将已批准HDMI修复接入整机；沿用既有独立时钟、HP2读所有权、明确CSR和stop/drain集成契约。该集成尚未执行，新接口及在线切换条件未明确的依赖步骤保持待讨论。实时整机测量和实屏验证未执行，既有上板授权保持。

完整载荷比较（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/reference-payload-review.json`）、原BOOT逐字节重建（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/boot-control-utf8-r2/result.json`）、试制BOOT原后检失败（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/boot-candidate/result.json`）、本次实际成功扫链（本机留存，仓库未附：`../../tools/pose-v1/evidence/hdmi-board-reference-20261016-r1/chain-scan-device-enumerated-r3/stdout.log`）。本地30TAI教程第7–9页说明BOOT生成/替换/重启路线；本轮仅做离线封装，不据此扩展启动分区修改或再次重启许可。
