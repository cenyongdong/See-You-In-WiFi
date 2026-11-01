# 独立心率模块

**最终范围（2026-10-29）：** 本模块冻结，未进入最终演示主链，也没有可信真实心率检出。新增 PL 扩展已取消，旧原始采集数据已清理；下文“最新开发”、采集路径和下一步按历史阶段理解。[现行冻结记录](HYBRID-20261026.md)、[项目进度](../../PROJECT-PROGRESS.md)。

**2026-10-26 最新开发入口：[流式心率与可选 PL 后端](HYBRID-20261026.md)。** 已增加原始同包天线对流式接入、PS 时间适配、单特征故障隔离、定点／PL 后端与 CPU 降级；已完成主机测试、ARM64 交叉构建、RTL／GP 桥仿真及 OOC 资源测量，并执行新的有限真实 CSI 采集。真实心率检出、精度和板端整机运行仍未通过；下文 2026-10-19～22 内容是严格参考路径及历史范围，当前实现与实测以新入口为准。

2026年10月22日：仅对历史RT-AC86U实采做主机离线核对，未恢复采集或连接设备。盘点53份归档PCAP（含回放副本），最长约26秒，无单份40秒记录；三段代表性连续段约10秒，真实三链I/Q可用，但直接送入原50Hz模块均被质量门拒绝，HR／RR为空。扩大检查的每段168条载波／天线对特征均有超过原相位步长阈值的跳变。人工确认有人静坐、没有同步心率参考；因此仅验证诊断接入与拒绝流程，未验证真实心率检出或精度。实际结果、原始回执与下一步条件见[本次离线核对](validation-real-nexmon-20261022.json)；入口为[历史数据诊断](../../tools/vitals/audit_nexmon_vitals.py)。原参考算法、质量门和姿态／板端协议保持不变，实机排查继续暂停。

同日继续完成[50Hz时间适配与相位故障隔离](validation-alignment-nexmon-20261022.json)：使用原始NMD连续段的相对RX时刻、同包天线差分及时间unwrap，再做有界时间插值、抗混叠FIR和50Hz降采样。9项故障／信号契约及12项信号验证通过；真实数据仍没有完整40秒合格窗口，**相位跳变根因未解决**。适配器仅输出诊断相位数组和逐通道有效掩码，不生成严格I/Q输入，不声称均匀输出网格就是均匀RF采样；原C++、姿态预处理和板端协议均未改动。

2026年10月19日：取舍完成C++17参考实现和主机离线验证。**姿态预处理保持原PS实现；本模块不链接SDK、模型、HDMI、Web或设备驱动，不连接板卡。** 当前结果和限制见[验证报告](VALIDATION-20261019.md)，机器结果只维护在[验证摘要](validation-summary-20261019.json)。

2026年10月20日：完成时间轴适配后，修正心率及辅助呼吸支路的ACF候选选择，保持原质量门。此前3个漏检和扩大检查发现的4个谐波误报均已解决；原36例、38个采样率用例、296个扫描正例及96个负例通过，15项契约在Windows／Linux通过，新ARM64产物完成交叉编译和静态复核。真实OctoNet相位及源时钟／包序号证据仍不合格，阶段B未启动。详细原值、历史失败及边界见[验证报告](VALIDATION-20261019.md)，Python适配器仍仅在主机运行。

## 模块和接口

| 文件 | 职责 |
|---|---|
| `reference.hpp`／`reference.cpp` | 拥有值输入、数据质量检查、相位／滤波／相关／频谱及结果判断 |
| `offline.cpp` | 有界CSV输入、JSON结果／原始中间值、主机计时；无网络或设备入口 |
| `test/reference_tests.cpp` | 数值输入、时间、缺样、运动、配置与容量契约 |
| `../../tools/vitals/signal_fixtures.py` | 可复现的解析信号及负面样例；全部标为synthetic |
| `../../tools/vitals/validate_offline.py` | 原生程序调用与独立NumPy／SciPy对照 |
| `../../tools/vitals/import_nexmon.py` | 显式复用已有Nexmon解析器，读取历史PCAP，不采集／插值／复制链 |
| `../../tools/vitals/adapt_octonet_timing.py` | 原时刻天线差分、原始质量门、插值及抗混叠；仅输出主机诊断相位，不伪造RF时钟／序号／I/Q |
| `../../tools/vitals/align_nexmon_phase.py` | NMD2／3连续RX时间段的50Hz相位适配、原始跳变／缺测污染范围标记；不接入严格C++输入或设备 |
| `../../tools/vitals/test_align_nexmon_phase.py`／`validate_nexmon_alignment.py` | 低频保真、混叠、换行／真实跳变、短缺测及完整合成窗口验证；不宣称真实心率检出 |
| `../../tools/vitals/validate_timing_adapter.py` | 已知信号叠加实际时间戳，验证10／20／25／50Hz；保留漏检与拒绝，独立于原基线 |
| `../../tools/vitals/validate_rate_sweep.py` | 48–120次／分、步长2的跨采样率解析扫描及噪声／呼吸谐波等负例；不宣称真实人体精度 |

业务通过`pose::vitals::analyze(Window, Config)`调用。`Window`拥有四个特征通道；每通道是同一接收节点、同一无线帧的两个天线复数值。每条`Sample`有纳秒时间、递增采样序号及有效标记。所有内存都是普通Host／PS内存，无物理地址和借用SDK对象。

每次分析独立拥有全部中间值和输出，没有全局可变滤波历史，也不会在无效输入时返回上次结果。新模块不包含其它功能的`.cpp`，不改变PIWCSI1、PIWPOSE1或显示IPC。

## 算法和当前范围

严格参考入口默认50Hz，先10秒预热、后30秒估计，共2000样本，上限2048。`analyze(Window)` 一次调用只分析一窗，调用者须先准备同包天线对的均匀连续序列；新增流式／重采样／候选特征选择入口见上方 2026-10-26 记录。

1. 校验采样时钟、时间单调性、连续序号、有效性、有限值和幅度。默认不接受缺样；任一间隔偏差超过2ms即拒绝，不补0、不重放、不默默重采样。
2. 对天线对进行正实数缩放以避免有限大值相乘溢出，计算`arg(Ha*conj(Hb))`，沿**时间**unwrap。该算法与姿态沿子载波校正完全独立。
3. 全40秒窗口去线性趋势；心率支路为四阶Butterworth高通0.8Hz＋二阶低通2.0Hz，呼吸辅助支路为二阶高通0.1Hz＋二阶低通0.5Hz。两者是独立高／低通级联，不等同于同名阶数的标准带通设计。以零状态启动，丢弃前10秒滤波输出。
4. 归一化自相关寻找全部局部峰，验证周期证据；对**未带通**的去趋势信号做Hann加窗FFT，检查原始频谱峰集中度及能量，避免滤波将噪声制造成有效心率。
5. 心率及辅助呼吸支路只在同时满足原相关系数、频带及与原谱峰相差≤0.05Hz的局部ACF峰中选择最强者，避免离散lag使两倍周期峰略高而漏检；没有合格峰仍拒绝，不把倍周期频率直接乘2。心率至少3／4通道同意，发布频率仍使用原谱插值峰；ACF频率单独保存。
6. 根据辅助呼吸结果拒绝落在其2至20次谐波±0.035Hz内的心率候选。无足够支持时返回空值和原因，不输出平滑后的旧数值。

当前研究频带为心率48–120次／分、呼吸6–30次／分。搜索边缘保留半个FFT格宽的估计不确定性，输出原估计，不夹到边界数值。10秒预热只是本轮参考配置，不保证真实传感信号一定达到稳态。

`confidence`是相关峰、谱集中度和同意通道数形成的启发式指标，不是临床准确概率。真实心率恰与呼吸谐波重合时也可能被保守拒绝；共同窄带干扰可能与真正心搏不可区分。当前阈值只在所列离线样例上验证，没有真实受试者准确度或有效率结论。

配置字段须有限、合理，估计窗至少覆盖3个最低呼吸频率周期，预热和估计样本和不得超过2048。配置非法抛出异常；数据不合格返回`invalid`及全部已发现原因；合格但无心率证据返回`no_heart_estimate`；满足本参考算法条件返回`valid`。**synthetic输入上的valid仍只是合成算法结果。**

## 时钟和来源契约

`ClockKind`只允许以下状态：

- `UnknownArrival`：默认状态，包括尚未验证的PCAP到达时间。禁止给出有效心率。
- `SyntheticUniform`：明确的离线合成时轴，只用于算法验证。
- `VerifiedSampling`：调用方负责提供真实采样时钟的验证证据。文件中需要`clock_evidence`，程序不会自动证明声明是真的。

合法CSV不意味着采样时钟合法。原始包、天线、子载波、同步和时钟证据仍由输入适配层负责。本模块不会将一台路由器的三条链伪造成三个空间接收点。

## 离线文件和结果

CSV开头采用`# key=value`元数据，其后为固定列：

```text
# origin=synthetic
# clock=synthetic_uniform
# sample_rate_hz=50
# clock_evidence=analytic uniform samples generated offline
time_ns,sequence,valid,ia0,qa0,ib0,qb0,ia1,qa1,ib1,qb1,ia2,qa2,ib2,qb2,ia3,qa3,ib3,qb3
```

I/Q均为FP64十进制数，时间和序号为无符号64位整数，valid为0或1。支持CRLF／LF和UTF-8 BOM。文件最多4MiB、8192行；`--offset`选择起始记录，默认取第一窗。窗口不足时明确拒绝；文件坏尾部、冲突的配置或已有输出文件也会拒绝。

结果JSON包括来源、时钟、配置、质量、每通道候选、空／有效HR／RR及各阶段耗时。`--trace`保存相位、去趋势、滤波及归一化相关原值。CSV和结果均不覆盖已有文件。当前全部记录`hardware_test=false`，表示本次执行没有访问硬件，不否认真实PCAP本身的采集来源。

## 构建与复现

本模块是独立CMake目标，运行只依赖C++标准库。以下为已经验证的本机构建方式，目录应换为新的输出位置以保留旧结果：

```powershell
cmake -S software/vitals -B .local/vitals-host -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build .local/vitals-host
ctest --test-dir .local/vitals-host --output-on-failure
python tools/vitals/validate_offline.py --executable .local/vitals-host/vitals_offline.exe --output-dir .local/vitals-validation
```

验证脚本需要既有NumPy／SciPy；本轮使用现有Conda Python3.14.6、NumPy2.5.2、SciPy1.18.1，没有安装或升级工具。数学库采用`-ffp-contract=off`。Windows本轮Release为GCC16.2、`-O3 -DNDEBUG`；最终加固版已用现有FPAI的GCC9.4、`-O2 -DNDEBUG`完成ARM64交叉编译，不链接SDK。产物、运行库要求和复核边界见[验证报告](VALIDATION-20261019.md#arm64构建和边界)，尚未执行ARM程序或核对板端运行库。

```powershell
.local/vitals-host/vitals_offline.exe --input input.csv --output new-result.json --trace new-trace.json --repeat 100
```

`--repeat`只回放同一窗口测主机算法时间，不包含CSV／JSON磁盘IO，不算新采集、独立样本或板端吞吐；不允许把快速拒绝路径用于benchmark。

真实PCAP适配器必须显式传入已有解析器及四个FFT索引，避免复制厂商解析算法或改动采集分支。比如本轮的5／11／17／23只是用于已保存记录的格式与质量检查，**没有验证它们适合心率检测**：

```powershell
python tools/vitals/import_nexmon.py --pcap capture.pcap --decoder path/to/csi_verify.py --carriers 5 11 17 23 --output new-input.csv --manifest new-source.json
```

该适配器固定读取20MHz／64点、BCM4366、stream0、三条实际RX链；缺链、重复或有歧义的帧身份拒绝。只借用解析器公开函数，不写回其工作区；输出强制标记`real_capture`和`unknown_arrival`。相对时间来自现有解析器的浮点PCAP时间API，不提升为精确RF时钟。

新增NMD相位适配器复用历史核对的同包配对及首次有效去重，选取单份录制最长的连续RX时钟段，不跨文件／时钟段拼窗。固定4条诊断特征保持原值，未按心率频谱选通道。相对RX时间先插值到600Hz工作网格，再用481点、截止15Hz、Kaiser β=8.6的对称FIR低通，取50Hz输出；每侧保留0.4秒实际数据支撑，截掉边缘，不外推。降采样前低通用于抑制混叠，相关原则见[SciPy官方说明](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html)；这里的非均匀时间适配只是有条件的数值近似，不是任意缺测信号的精确重建。

原始相邻差分相位超过0.25rad，或源间隔超过离线保守上限10ms时，任何滤波支撑涉及该区间的输出都置为NaN并标记无效。10ms是本次离线筛选配置，未经RF生产条件认证；不能靠调大它通过验收。检查直接覆盖原始间隔，极短异常即使落在工作网格点之间也不会被隐藏。普通2π表示换行可unwrap；宽频跳变不做偏移拟合／减除，防止一并抹去真实人体低频变化。原始相位与故障标记保存在输出NPZ，不回写PCAP。

降采样只改变样本密度，不增加观测时长。40秒／2000点的就绪检查保持原样；不足时返回历史不足，有故障则拒绝窗口，不补0、不重复或拼接。此适配器目前只供主机诊断，尚未替换严格的同包复数I/Q接口；后续接入需明确派生相位的来源和质量契约。复现时使用新输出目录，三份案例的输入与结果入口见上面的适配报告：

```powershell
python tools/vitals/align_nexmon_phase.py --pcap tools/nexmon/evidence/hotspot-control-20261021-r1/phone300/capture.pcap --output .local/new-phase-alignment
python -m unittest discover -s tools/vitals -p test_align_nexmon_phase.py -v
```

## 对PL加速范围的当前判断

本轮主机数据只说明相关计算和频谱判定是当前参考程序的主要计算阶段，不足以证明PS在本板上形成瓶颈。下一步先获得可信连续CSI及同步心率参考；有授权时再测ARM／PS阶段时间、CPU占用和能量。如果PS已满足要求，则不新增PL核；否则优先评估相关MAC或有明确收益的小核，而不是先把整条算法迁PL。

本轮不修改原核心、HDMI、Web、模型、SDK、帧协议、BOOT或PL配置。HDMI排查与旧DATA调查继续保持独立暂停。
