# r9 AI读路径观测候选：现场有界执行包

**适用范围（2026-10-29 核对）：** 本页的版本、参数、工具与执行状态属于文内注明的阶段；历史“最新／当前／下一步”和旧包次数不覆盖[现行恢复入口](RESUME.md)。已发布默认硬件、现存备份与启动流程统一从该入口查询，本页原始结果和限定例外保持。

2026-10-18，状态：**并执行；4KiB SDK失败停止，已完成唯一原BOOT回退，本包关闭。** r9已实际启动；64B通过、4KiB SDK异常71停止；后两档／三窗新推理／HDMI START未执行。已完成唯一原BOOT回退与只读身份复核，全部启动额度用完。D45未解。 本包不接入Vivado MCP。批准时原文独立保留于approved-plan.md（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/r9-user-authorization/approved-plan.md`）。

## 实际候选与范围

- 候选BOOT：7,023,552字节，SHA256 `a0fe608bb4890f941238b1557f2202987116d1e25669f220fcb4b84fec11fb00`。
- 原BOOT：同长度，SHA256 `ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`。
- 实际Procise ICAP位流：SHA256 `f3efc208de2510053eee0d87953f00d1e6981274ada7efb8f2176e2165bb83fb`。
- BOOT仅PL分区变化，偏移186816、长度5980464字节，PL差异2114580字节；非PL全部字节一致，载荷字交换及填充一致。首次8字节分区名称变化的失败封装保留，已用原文件基名重新生成，未手工修改映像字节。
- 新reader只缩短4KiB边界判定，无协议／流水／错误语义变化，1048576个组合和24组状态机比较通过。完整物理及55项正式复核通过，setup +0.030ns、hold +0.023ns、TNS／THS=0、HDMI CE最小+0.315ns；2768位观测约束符合，原厂DRC配置0 Error。
- 原AI两个相同对象Min Period −0.409／−0.071ns例外保持，raw_timing_pass仍false，无新增豁免。完整旧失败、Warning、默认DRC和原route父exit1均保留。本包是新物理实现与诊断观测候选，**D45未证修复**。
- 固定三窗软件、模型JSON／RAW、SDK、CPU数学／Gather注册、NPU分配及帧协议保持。只做有界新推理→HDMI验证，不代表连续CSI输入、严格5Hz、长期或PC 3D验收。

## 执行前现场身份与前置条件（历史原值）

本轮只读SSH审查通过：原BOOT／六SDK／九启动根文件身份符合，内核IMAGE同原保护SHA，FPGA operating、设备owner为空。当前boot_id为`b2752700-4c7d-440f-b62a-c1f5d7f421b0`，与10月17日不同，未推断外部启动原因，执行包绑定本次实际会话。COM7为CP210x `USB\VID_10C4&PID_EA60\0001`；尚未打开串口。安装前重新核对实际启动会话、根分区余量、启动文件和设备占用，串口打开前再次核对USB身份。

FAT已知2168个未引用簇问题不修复，不修改uEnv、DTB、内核、SDK、模型或频率；不做JTAG热重配，不清缓存。旧DATA独立暂停。旧v2候选启动和原BOOT回退额度均已用完，不从该旧许可推导本包许可。

## 本包已批准的执行范围（执行已结束）

1. Windows工作目录D:/FPGACompetitionProject。本机Host计划已实际复核，五份适配入口对完整原算法逆AST恢复通过；远端源在本机生成、编译并封存后才可执行。主机密钥pin、内存认证和有界传输沿用原流程。
2. 使用新板端持久目录`/root/hdmi-live-20261018-r9/package-r1`，传输后逐项核对SHA；完整备份并回传原BOOT到主机，不覆盖旧失败证据。源、设备、SDK、内核或启动文件身份变化则停止核验。
3. **本包候选BOOT只临时安装一次、受控启动一次**。先确认原BOOT独立备份、回退条件、串口ready和唯一执行标记，再挂载经核验启动分区，写入、fsync、完整读回核对、替换BOOT并sync／卸载。启动观察SSH最多180秒、串口最多300秒／4MiB／0 TX；状态不明不重复启动命令。
4. 候选启动且SSH恢复后，**首先还原原BOOT文件、完整读回核对并确认其它启动文件／SDK不变**，再做负载。运行中PL仍为候选；启动文件还原与运行中回退分别报告。SSH不能恢复时保留串口并停止，可能需要人工介质恢复。
5. 新进程做64／4096／65536／1048576字节四档DMA往返，分配上限1MiB，子进程20秒／外层30秒。每档实际全字节比较；SDK／数据／身份异常立即保存原错并停止，不自动重复负载，不继续后续档位。允许失败后同Device一次既定观测快照，仅作诊断、不重新Open／复位／清错。
6. **仅四档全部通过后**，新进程执行固定共享模型三窗新推理→PS RGB565渲染→PL HDMI。子进程120秒／外层140秒，先保存完整实际输出，再执行原数值门：全部输入与分数逐位一致、所有输出有限；score>0.2候选最大关节三维偏差≤3mm，低分误差保留。三份新骨架各约5秒，现场确认画面与切换；重复扫描不算新姿态。
7. 显示已START时，按原已验证STOP流程取得新响应、匹配停止ID、idle和在途位清零后释放帧；不能证明时保留帧并停止。保存全部观测／SDK原错／数值／显示与进程证据，不遗留后台任务。
8. **必要时最多一次原BOOT回退重启**，只恢复原运行状态，不能加载其它候选或继续追加负载。任何失败不扩大该上限，不修文件系统，不恢复旧DATA。

## 可核查证据

本轮报告（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/REPORT.md`）、正式55项复核（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/read-v3r9-independent-reports-r1/review.json`）、实际位流（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/read-v3r9-native-bit-r3/bit-identity.json`）、BOOT非PL比较（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/read-v3-boot-r2/review.json`）、原始离线包（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/controlled-startup-read-v3-r2/manifest.json`）、实际执行manifest（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/controlled-startup-read-v3-execution-r9/manifest.json`）、Host实检（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/host-plan-review-r1/`）、板端只读身份（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/onsite-resume-readonly-r2/`）。

实际执行manifest SHA256：`3b5887ecece138973ee2ebef20b533211971674c0b33c7cbd9784159065cf085`；本机Host独立计划实检73.547秒exit0，local_review SHA256 `ccfc5ee31dc51f09493c64ce9d82102a279bc51bc312074eb0793404e79bd704`。生成源不构成批准；随后，原始回执见r9-user-authorization（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/r9-user-authorization/actual-authorization.json`），当前包授权已关闭。

## 实际执行结果

2026-10-18，r9执行包实际完成有界执行。候选安装／启动一次，SSH恢复34.344秒后先还原原BOOT并完整核验；64B DMA全字节往返通过，4KiB写在5.191秒触发SDK内部5000ms超时，child exit71。按失败停止规则，64KiB／1MiB、三窗新推理和HDMI START均未执行，没有重试失败负载。已用本包唯一原BOOT回退，SSH恢复28.688秒；运行中与启动文件均回到原BOOT，六SDK／九启动文件符合、FPGA operating、owner为空，串口均关闭。候选／回退额度均为0，本地及板端本包授权已关闭，旧DATA仍暂停。**D45与新推理→HDMI全链尚未解决。**

104字真实快照已验证：观测窗口约5.064秒，HC2接受9笔AR而R握手0；共享HP2对PS出口接受8笔AR、R握手2后持续背压；HDMI入口AR握手0、RVALID且RREADY=0覆盖整个窗口。ARM后未记录复位异常。疑点收敛到HP2共享返回通道及其初始化／分发状态，但没有逐事务台账或ARM前历史，不能唯一断定错路由、ID丢失或复位原因。实际发布DCP只读检查确认S00接HC2、S01接HDMI、6位PS RID进入返回流水线，未发现直接错线或显然ID截断；这不证明互联运行正确。

完整阶段、失败原文、观测、回退及清理见r9报告（历史附件，当前仓库未附：`../../tools/pose-v1/evidence/hdmi-live-20261018-r9/REPORT.md`）。本页修订不回写批准时文档SHA。
