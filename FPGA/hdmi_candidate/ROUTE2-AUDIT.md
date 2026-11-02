# 原厂 Vivado＋JFM／Procise 路径二审查

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

2026-10-16，随后已同意实施并授权自主决策，参考整机链实际结果及门检停止见[AI-CLOCK-GATE.md](AI-CLOCK-GATE.md)。以下保留路径二审查时的结果与边界；32项配套及GT范围已在后续实施，不再等待重复批准。原审查时，审查路径二，并允许代理依据现场自主处理超时。本页区分实际执行、脚本预览与后续构建决策；完整原值见本批报告（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-jfm-route2-20261016-r1/REPORT.md`）。

## 已确认的实现职责

本地《30TAI使用教程》第1—6页要求版本匹配的 Vivado、JFM_PATH、关闭 IP 缓存、IP 使用 OOC，添加原厂 hook 后直接 Generate Bitstream。第7—8页使用 Procise Create BOOT Image 和 BIF 打包。实际受保护脚本还包含独立的 30TAI ICAP 后处理，不能只凭教程截图省略它。

已查明的链路是：原始2018.3工程及同配置IP/OOC → Vivado＋JFM综合、优化、实现和生成.bit → 原厂30TAI ICAP后处理调用Procise → 经核对的BIF/ELF打包BOOT → 完整门检后实板验证。原生Procise的PS7→PCPU7通用EDIF导入失败继续保留，但不是这条原厂链路的前置步骤。

本次只执行到工程身份、hook配置预览、MIG OOC和原厂前置检查；没有执行顶层实现或位流后处理。当前BOOT及最近现场“不支持当前时序”的状态没有新实屏结果可替代。

## 隔离工程和实际结果

工作目录为D:/FPGACompetitionProject/.local/hdmi-jfm-route2-20261016-r1；工具为D:/vivado18.3/Vivado/2018.3，保留上一批已授权的030ai补丁。只复制原参考工程297份文件及必要JFM文件，没有复制Vivado工具目录。原参考SHA逐项一致；2019.1升级工程单独保留，没有降级导入。

| 项目 | 实际结果 | 边界 |
|---|---|---|
| 原工程IP状态 | 28项全部未锁定，保持原修订 | 不等于28项均完成综合 |
| HARC.cfg | 当前安装与原厂源SHA完全相同 | 配置预览拦截并跳过同字节复制，无安装写入 |
| Hook | 隔离工程六项绑定重开后存在，place前后为空 | 仅生成脚本文本，没有执行顶层hook |
| 配置预览驱动 | 原厂add_hook返回后，错误调用save_project导致exit1 | 保留整阶段失败；独立重开确认配置，不重跑add_hook |
| 初次pre_patch_check | 检出mig_7series_0未有OOC成果 | 原始失败保留，没有伪造检查点 |
| 同配置MIG OOC | 262.133509秒、exit0，实际DCP生成 | 非运行时XCI参数、DDR .prj字节不变，无IP升级 |
| 再次pre_patch_check | 9.815504秒、exit0 | 是原厂前置检查通过，不是完整实现或DDR实板验收 |
| Procise接口 | 本机存在increment_bit_cfg_v3与BOOT相关命令 | 没有实际处理.bit或生成BOOT |

MIG初始预算180秒，到达门限时日志持续更新、未见ERROR；进程祖先链证明四个Vivado进程均属同一作业。代理将预算延至360秒，继续原进程至成功，没有重启作业。完整判断见timeout-decisions.json（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-jfm-route2-20261016-r1/mig-ooc/timeout-decisions.json`）。最初资源快照中的直接路径匹配不能识别相对路径子进程，后续祖先链记录为归属依据。

## 参数、写入与门检审查

本次预览明确传入 `-xfft_modify FALSE -change_speed FALSE -disable_icap TRUE -device 0`。这是受写入守卫限制的审查配置，尚不是经过完整构建验证的配置。

| 选项或对象 | 原厂真实行为 | 本批处理／后续影响 |
|---|---|---|
| HARC.cfg | add_hook在2018.3无条件复制到安装目录 | 原厂源与现安装相同，跳过复制 |
| -xfft_modify | 缺省TRUE，调用replace_ip_database | 涉及31份RFS HDL和1份xgmac ttcl，共32项全局文件；实际32项源/目标均存在且全部不同。本批FALSE，未写入 |
| IP库覆盖范围 | FFT、公共算术、counter、Ethernet、JESD等 | 原厂清单含c_counter_binary，但当前未证实本工程实例使用它；不能仅因无FFT就将整套默认库处理视为等价可省略；需确定正式构建的库范围，完整清单（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-jfm-route2-20261016-r1/IP-library-readonly-inventory.json`）已备 |
| -change_speed | 缺省TRUE；实际xc7z030分支只复制paspd/fmsh/030ai下zynq.lib和zynq.padr（后续已证实均与现安装同SHA） | 本批FALSE；已有030ai九项补丁保持，不新增速度库处理 |
| REQP-44/46/52/56 | 030ai生成的后续脚本会禁用 | 本批只生成文本，未执行。实际规则均启用、Error级，针对GTHE2/GTXE2的GTGREFCLK保留测试时钟，不是HDMI像素时钟或CDC豁免 |
| -disable_icap | 缺省TRUE，PS独立分支调用Procise | 本批保留TRUE但拦截exec，只预览命令 |
| -device | 缺省0，PS分支按xc7z030映射目标 | 实际预览得到JFMQL30TAI676H；不填K325示例器件 |
| procise_incr_cfg.txt | 若工程根目录存在且字段启用，另走通用增量配置 | 原参考根目录不存在该文件；不复制包中的K325/sw_ctrl_led示例 |

原版保护脚本正常加载时报告引擎5.3.1.8（2026/02/05），包内ip_patch_version.log为5.3.2.1_100AI_LV。两者分别记录，不把标签差异自行解释成兼容或不兼容，更不擅自混换包。

## 30TAI后处理和BOOT边界

原厂 `disable_icap_for_psoc` 在device=0时根据xc7z030选择JFMQL30TAI676H，生成的实际命令如下。命令由原厂过程产生，本批exec已被拦截，输入是新目录内复制的原厂参考.bit；没有生成输出位流。厂商stdout中的“runs success”仅是被拦截exec后的脚本输出，不能记作Procise处理成功。

```tcl
set_device JFMQL30TAI676H
increment_bit_cfg_v3 INPUT.bit OUTPUT_disable_icap.bit -disable_icap
```

原厂按最新修改时间选择*.bit，混放原始/处理后文件可能选错或重复处理。后续必须采用一目录一输入、显式记录输入输出SHA，并核验实际Procise退出码与产物。未使用的*_revise_device.bit清理也应限定在该工作目录。

BOOT_Gen中参考bit的头部为ai7030_top、xc7z030ffg676、Vivado2018.3，日期2025/12/24；它不是新候选，也不能据此证明等同现用BOOT内分区。BIF含旧绝对路径，三份ELF均为AArch64；BIF原有apu_x32文本的意义未独立验证，不能自行改写。已有五份文件SHA记录，启动配置、ELF和当前BOOT均未变。

## 正式构建前需要确定的范围

建议继续采用本条原厂链路，保留现有030ai补丁与change_speed=FALSE；先在新隔离候选工程接入已验证的HDMI RTL，再执行分阶段契约与完整实现。正式运行前需就32项全局IP库替换及原厂四项GT DRC处理确定明确范围：前者应先备份、建立源/目标白名单并验证恢复；后者应记录实际GT使用和被关闭规则，不得扩展为HDMI、CDC或时序放行。若选择保持库未改、规则启用的探索配置，应明确它与原厂缺省不同，出现兼容失败保存停止，不能将预检查通过作为等价性证据。

完整实现仍须核验PS/DDR/AI_Mate、地址与接口、候选148.5MHz像素目标/串化时钟、实际封装引脚、复位、CDC、STA/DRC、Procise后处理及下载前器件扫链。仅工具或模块通过不能替代实屏验收。本轮不生成或替换BOOT、不重启，不恢复旧DATA调查。
