# 防闪现后处理与精简硬件：离线结果

**2026-10-27 最新决定：暂停布线并取消新增 PL 开发，全部本批实现进程已停止；v2 几何／批量滤波扩展保留为未部署实验，不继续构建或上板。** 既有合格 v1 位流及原有功能保留，后续采用 PS 后处理。本页保留首次离线阶段原值；当前结果、PS 实测和取消边界统一见[后续记录](../../../software/pose180_pipeline/resident/PRESENTATION-20261026.md#2026-10-27v5-后处理与已取消的-pl-扩展)。

2026-10-25～26。软件CPU后处理、HDMI／PC派生展示、历史回放、精简守卫和参数化1／4路滤波核已实现并完成下述离线验证。**两版滤波LUT均超过批准预算；生产推荐仍为r45＋CPU后处理，PL版本作为实验结果保留。精简硬件未取得启动／部署资格。**

本阶段没有连接板端或路由器，没有部署、BOOT写入、设备重启、SDK推理、整机布局布线或位流生成。原r45和完整诊断源码未改，旧DATA／D45全面调查未恢复。当前板端暂停及回退核验边界仍见[原记录](../../../software/pose180_pipeline/resident/TOP3-VALIDATION.md)。

## 软件与展示

[SDK无关核心](../../../software/pose180_pipeline/src/pose/postprocess.cpp)由实时入口与[离线回放](../../../software/pose180_pipeline/tools/native/pose_replay.cpp)共用。顺序为Top3、严格`score > 0.2f`、双距离去重、全局有界人物匹配、异常门限、One Euro与生命周期。保留同分候选索引规则，不补第四名；关联同价按确定的轨迹ID／候选索引次序处理。14关节中心、RMS尺度下限0.25，去重门限0.2尺度；关联使用实际dt及`0.5+4dt`／`0.5+6dt`门限。中心匀速预测速度限定为每轴4尺度／秒，避免单次估计污染后续匹配。

至多3条确认和3条待确认记录；连续两帧且间隔≤250ms才确认，待确认漏检即重新计数。首次确认直接初始化滤波；确认后的失配仅保留末次有效姿态≤250ms并标暂失，不续写观测时间、不外推。会话／恢复代次、时间或序号倒退清空状态。显示优先级为当前匹配、新确认、暂失；颜色跟随稳定轨迹ID。默认参数为1Hz／0.5／1Hz。模型／SDK／预处理／NPU分配及原始输出不改。

`PresentationFrame`携带会话、源帧、序号、源时间、轨迹ID、候选、分数、42坐标、暂失标志、末次有效观测时间，并附原始Top3对照。HDMI和PC来自同一帧；原39383／PIWFUL3保留，39385为独立`PIWVIEW1/version=1` NDJSON，记录上限16KiB、最新值缓存、部分发送独立拥有、发送缓存16KiB、停滞500ms断开，无应用ACK。PC中历史回放明确标识，双视图并排，无插帧，接收后补计姿态年龄并到期隐藏；HTTP失败时清空派生视图。

HDMI空闲时由原SDK所有者处理姿态到期并重绘。**若SDK阻塞，同一所有者无法准时清除已扫描的HDMI旧画面；本阶段没有声称硬件保证250ms清屏。** 这与算法不续写有效时间是不同保证，实板端到端时效仍需下一阶段确认。原始模式保留其历史过期提示行为。

`--hardware-profile r45 --filter-backend cpu`为当前默认。显式选择`pose-stabilizer-offline-v1`会在创建SDK／IO之前拒绝；不会探测r45不存在的新CSR。[PL适配器](../../../software/pose180_pipeline/src/pose/pl_filter.hpp)通过调用方提供的MMIO回调访问，先核对显式新身份和ABI，失败隔离、不重试，不猜测Linux地址映射。已接入同一后处理核心的可选后端接口，实际生产入口尚不开放。

## 实际验证结果

| 项目 | 结果 |
|---|---|
| 原生／ARM64 | FPAI GCC9.4、Icraft3.39，CPU核心、resident mock、r45 ARM64 resident编译成功；原渲染／显示状态／缓冲回归通过 |
| 算法 | 排名交换、同分、重复、阈值、孤立跳点、持续新位置、确认中断、漏检到期、离场／重建、两人交叉、不规则dt、恢复代次／时间回退、非有限拒绝、原数组不变通过 |
| 固定噪声 | 固定随机种子、15Hz、1000点，去掉前101点；静止RMS下降56.86%，目标≥40% |
| 运动响应 | 15Hz采样1Hz正弦，稳定段离散误差最小滞后1帧≈66.67ms，目标≤100ms；不是全部动作或实板端到端延迟保证 |
| 浮点／定点 | 正常24×126样本最大差`1.64017e-5`；含不同人物dt、漏检、槽位复用和代次重建的后端测试最大差`1.45435e-5`，均<0.001 |
| RTL滤波 | 1／4路40×126坐标逐位一致，覆盖正常、不规则dt、重初始化、银行保持、极值饱和、完整发布；CSR测试覆盖不完整提交、忙时重复、读背压、局部复位 |
| 启动 | 健康和实际原消费器已知消费流程通过；18类故障拒绝、原消费器9类边界、CSR序号／CDC／不可变快照／复位不重放通过；真实r8／r9原始证据离线复算仍分别因见证差异／范围外原生状态拒绝 |
| PC | 5组Node测试通过，含原PIWFUL3回归、任意拆包、合包、非法值、超长、过期、无ACK、重连、历史回放不联网；真实浏览器双视图和重播操作已检查 |
| 慢PC | 最终隔离网络容器mock：4秒内继续690次推理，派生结果可丢弃、重连获得新序号，native exit 0。不是SDK／板测 |
| HDMI | 派生ID／暂失／剩余有效时间与原渲染兼容测试通过，已查看1920×1080离线栅格；没有实屏验收 |

真实记录均只读消费留存环，按原时间戳播放。没有真值，**不宣称身份或精度正确，也不把回放计作新推理**：

| 留存片段 | 帧数 | 人数变化：原始→派生 | 确认的新轨迹ID数 | 平均／最长首次确认间隔 | CPU核心均值／最大 |
|---|---:|---:|---:|---:|---:|
| r11 | 205 | 84→43 | 32 | 72.77／133.70ms | 0.0188／0.5374ms |
| r12 | 221 | 72→58 | 39 | 114.60／200.71ms | 0.0111／0.0368ms |

中心变化>0.5模型单位：原始**同排名位置**为72／80次，派生**同轨迹ID**为1／0次。两项关联方式不同，新增／删除轨迹另外计数，不能将它们直接当作同一人物跳变改善率。拒绝匹配对334／430个，去重各20个；拒绝对数不是拒绝帧数。首次确认延迟不包含在上面的滤波运动滞后中。仍存在轨迹重建和人数变化，效果不能写成“闪现已彻底解决”。

## 旧准入→新保护→测试／缺口

| 旧保护条件 | 新保护 | 对应验证／处理 |
|---|---|---|
| SDK／DMA／HDMI业务之前、同一次配置 | 明确命令、一次arm、终态不重复；新身份／ABI与命令响应序号 | healthy/known流程、重复命令、旧profile拒绝；部署仍关闭 |
| PS／PL复位释放且有覆盖 | 同HP采样点记录两侧复位低电平；原生checker seen_reset/ready依赖保留 | 缺失覆盖、复位中断拒绝；实际配置起点／时钟网络仍待整合核验 |
| 历史AR／AW／W／B及提前reader活动为零 | 各AI端、S01、PS请求／写活动直接锁存为错误 | 故障2／3、consumer冲突测试；不以当前电平零替代历史 |
| HC0～3无返回 | 四路RVALID合并锁存错误 | HC故障拒绝，不只检查HC2 |
| PS RID=0x20、S01 RID=0、RRESP=OKAY | 有效电平即检查，首事件保存身份及同一周期编号 | ID／响应故障拒绝 |
| 确实存在已知待消费seed | PS已接受1～255拍、S01未接受、两端valid、S01未ready、原生已知规则历史 | 已知消费通过；提前S01接受或证据缺失拒绝 |
| 完整协议检查／容量／事务归属 | **保留原生协议检查器及注册观察器**，160位历史OR锁存；只容许58／59／61／92／93／95，未知位拒绝 | 原生79及软件receipt79拒绝；不宣称紧凑逻辑复刻完整AXI checker |
| 首事件三见证相等、连续采样窗 | 新核只用一个HP事件时间源，快照来自该源 | r8旧证据不能转换为新receipt。多源起点／事务归属未知不能被映射成零；硬件覆盖资格保持false |
| 原消费256拍／4096周期／64静默及终态 | `hp2_startup_drain`原源码、参数、复位／错误／晚到行为和RREADY OR原样保留 | 原9例边界全部通过 |
| PS／S01消费前后守恒 | 消费前计数、累计计数、实际drain拍数独立比对 | 健康5拍样本与不守恒拒绝 |
| 一个最终RLAST、后续不能再返回 | 末拍位置、后续握手错误锁存，三端联合静默≥64周期 | 非最终RLAST、晚到及PS静默不足拒绝 |
| 原生历史保留，显式一次rearm后重新检查 | 历史OR不随rearm清除，rearm只允许安全终态，准入须fresh live清零 | rearm＋admit流程；完整checker重置契约仍依赖原模块 |
| 完整波形／大快照的软件依赖 | 精简ABI独立，不伪装旧寄存器 | 独立覆盖层移除大型波形／六边界快照；**这些离线测试尚不能证明所有旧保护已等价，因此覆盖层硬连COVERAGE_COMPLETE=0** |

状态为观察／可消费／消费中／安全结束／业务获准／拒绝。任何错误锁存；CSR复位不清源状态、不再执行旧命令。快照在确认响应后保持到下一条命令，单笔未完成命令之外的写入报错。完整诊断版本仍可复用。

这个阶段的成果是可测试的精简设计和明确裁剪缺口，**不是一份可以绕过旧准入直接启动的生产位流**。独立覆盖层生成器保留AI四路、HP分配、原消费器及其OR连接；未生成实现／bit脚本。覆盖层通过原厂xvlog语法解析，尚未做整机展开／综合／CDC／布线资格检查。

## PL滤波与资源

同一套RTL支持`LANES=1/4`，按坐标索引模4分银行。32位有符号Q16.16；加减、乘法均宽中间值后饱和，乘法最近舍入、正好中点远离零。PS传入量化的`1/dt`、导数alpha、`2πdt`、min_cutoff及beta；RTL按[定点参考](../../../software/pose180_pipeline/src/pose/fixed_filter.hpp)的运算顺序递归更新，不使用另一套浮点近似。支持dt为1～250ms，范围外拒绝PL调用，CPU后端不受此定点范围限制。

CSR `0x400b1000–0x400b1fff`：`00` ABI504f5301，`04` busy／错误，`08`提交1／局部复位2，`0c`序号，`10`完成序号，`14`周期，`18`路数，`1c`初始化mask，`20..30`五参数，`34`更新mask，`400..5f7`126个完整输入，`800..9f7`126个输出。未写齐或忙时提交报错；所有lane完成后切换输出银行。局部复位仅作用于滤波器，无总线复位／DMA主机／新时钟／HP连接。

漏检人物的dt不同，不能用一份dt更新三个人。PS适配器按人物提交并使用update_mask冻结其他银行；轨迹ID映射独立PL状态槽，重建强制初始化。最终`PresentationFrame`要等所有当前人物完成才发布。

Vivado2018.3、当前适配xc7z030ffg676-2、OOC综合。GP时钟20ns；没有改变频率／库／例外。以下资源含滤波CSR：

| 版本 | LUT／预算 | FF／预算 | DSP／预算 | BRAM36等效／预算 | 全126坐标周期／50MHz时间 |
|---|---:|---:|---:|---:|---:|
| 1路 | **1250／800** | 980／1000 | 4／8 | 2／4 | 3656／73.12μs |
| 4路 | **3448／2500** | 1799／3000 | 16／32 | 8／16 | 930／18.60μs |

4路计算为1路25.44%，两版<1ms；**LUT预算均失败，不扩大预算**。综合寄存器路径估计setup slack均10.415ns，hold为0.107／0.100ns；OOC端口未建立整机外部延迟，不能作为完整时序通过。

每人物提交实际计算：1路1472周期；4路384／381／384周期。三人分别更新计算总计4416／1149周期（88.32／22.98μs）。CSR无等待总线下每批135写周期、126个输出读取630周期；三批合计2295周期，另加状态轮询和上游AXI／软件调用开销。纯RTL传输下限45.9μs，**真实PS MMIO耗时未测，不能把纯计算倍速当成端到端倍速**。

守卫＋CSR最终综合为1492 LUT／2275 FF／0 DSP／0 BRAM；使用`COVERAGE_COMPLETE=1`评估完整功能资源，发布覆盖层仍为0。HP=5ns／GP=20ns独立OOC模型；此报告未应用整机CDC约束，也不构成时序资格。重复获准命令会撤销准入并锁存错误，复测通过。

从**实际r45 routed DCP只读**提取：

| 原模块 | LUT | FF | BRAM36等效 | 覆盖层处理 |
|---|---:|---:|---:|---|
| 六边界／启动见证 | 7255 | 13006 | 0 | 裁剪为紧凑核，覆盖资格尚未成立 |
| 逐周期记录 | 409 | 774 | 15 | 裁剪 |
| 协议波形记录 | 415 | 1659 | 8 | 裁剪 |
| AI事件快照 | 267 | 2235 | 0 | 裁剪 |
| 原deferred控制 | 137 | 914 | 0 | 由独立CSR替代 |
| 原生协议观察／checker | 1351 | 1732 | 0 | **保留依赖** |
| 原主动消费器 | 41 | 39 | 0 | **原样保留** |

拟裁剪块合计8483 LUT／18588 FF／23 BRAM等效；新增加守卫及上表滤波资源。这里混合了旧routed块计数与新OOC综合，路由器、跨层优化和Slice打包尚未重做，**不报虚构的整机空闲Slice**。r45仍为18996／19650 Slice；旧错误裁剪版15197仅作历史对照，3799差值不直接计作新余量。

## 复现与证据

统一工作目录：`.local/pose-postprocess-offline/`。原生／ARM构建日志`build-235637/`，其后补充的独立守卫软件头增量编译及适配测试exit 0（汇总见`validation.json`）；最终滤波RTL `rtl-20261025-235847/`；滤波综合`rtl-20261025-233758/lanes1,lanes4/`；最终守卫综合`rtl-20261026-000947/`、流程`rtl-20261026-000939/`；18拒绝`rtl-20261025-234256/`、滤波CSR`234304`、原消费边界`234311`、守卫CSR`234448`、覆盖层解析`235728`。每目录保留原生退出码、完整工具日志，综合目录含utilization／timing及DCP。`baseline/`是一次r45检查点只读统计，`replay/`含NDJSON及上述JSON统计，`legacy-rejections.json`保留r8／r9本次离线拒绝，`view-io-final/`是最终慢消费者日志。

```powershell
# 软件：正常CMake，不需要SDK即可编译核心、回放及测试。
cmake -S software/pose180_pipeline -B .local/pose-postprocess-offline/native-repro
cmake --build .local/pose-postprocess-offline/native-repro
# 在相应平台运行postprocess_tests、pl_adapter_tests、renderer_tests。
node --test software/pose180_pipeline/host/test/presentation.test.mjs software/pose180_pipeline/host/test/resident.test.mjs
python software/pose180_pipeline/resident/replay_retained.py --binary .local/pose-postprocess-offline/pose_replay.exe --output .local/pose-postprocess-offline/replay
node software/pose180_pipeline/host/resident.mjs --replay .local/pose-postprocess-offline/replay/r12-replay.ndjson --http-port 39380 --seconds 120
# RTL：先运行fixed_filter_vectors生成工作目录的input/expected/params.hex。
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py filter
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py filter-csr
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py guard
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py guard-faults
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py guard-csr
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py drain-bounds
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py synthesis
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py guard-synthesis
python FPGA/hdmi_candidate/pose_stabilizer/run_offline.py overlay-parse
python FPGA/hdmi_candidate/pose_stabilizer/replay_rejections.py
```

RTL入口只调用xsim／OOC synthesis，不调用实现或板卡工具；长进程保留PID，等待超时不自动杀进程。旧拒绝样本／旧构建错误日志均保留。下一阶段是解决LUT预算和守卫覆盖缺口，再由新硬件身份进入整合／时序／启动可靠性验证；本阶段不执行这些步骤。
