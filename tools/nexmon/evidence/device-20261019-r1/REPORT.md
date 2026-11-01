# RT-AC86U Nexmon 实机部署与 CSI 验证

验证日期：2026-10-19。结论：**这台 RT-AC86U 可以采集真实 5 GHz 三链 CSI**。临时部署、单链、固定三链及 20 秒短时检查均通过；结束后已恢复原驱动及正常无线服务。本次没有进行模型推理、300 Hz 受控发射或长期可靠性验收。

## 实机与执行位置

- 执行端：Windows `D:\FPGACompetitionProject`；路由器：有线 `192.168.50.1`、管理员 `admin`。本机有线 1 Gbps，外网走 WLAN；已有接口优先级 WLAN 10／有线 50，本轮未修改。
- 铭牌：RT-AC86U，H/W R1.5，2019 年生产。运行系统实际为 **ASUSWRT-Merlin-KoolShare 386.9**，内核 **4.1.27 aarch64**，与商品所称原厂固件不同；本轮没有刷写整机系统。
- 5 GHz 为 `eth6`：deviceid `0x43c5`、chipnum `0xaa90`、chiprev `4`、corerev `0x41`、boardid `0x798`、boardrev `P102`。这些字段与上游 [REVINFO](https://github.com/seemoo-lab/nexmon/blob/master/REVINFO.md) 的 RT-AC86U 记录一致，`0xaa90` 本身不是换芯不兼容的证据。
- 原无线固件为 `10.10.122.20 (r683106)`、2022-07-14、FWID `01-9cc0c14d`。Nexmon 补丁使用准备阶段固定的 2019 基础无线映像，构建标识 `1232-5`。原模块与候选均为 AArch64、`vermagic=4.1.27 SMP preempt mod_unload aarch64`，依赖相同；实际加载与采集结果进一步验证了本次组合。

完整身份见 [01](01-preflight.json)、[02](02-driver-identity.json)、[模块检查](04-module-inspection-v2.json)。原驱动备份 [dhd-original-device.ko](dhd-original-device.ko) 为 1,658,168 字节，本地与路由器 OpenSSL SHA256 一致：`67faa220d9add7faa3b3a52f5ed7e82899548e2e66aed9a3a25506b6aa1ab323`。模块检查v2修正了BSS无文件字节时不计算字段哈希，模块／固件区身份结论不变，原检查文件保留。

SSH 人工在管理页开启为仅 LAN。直接有线邻居 MAC 与机身标签一致，首次观测 ED25519 指纹为 `SHA256:dGim8cOG0mswATT6pOWM9Cb9THxeTyQTEaIgLJ795P8`，之后严格固定该公钥；这是本次直连的首次信任记录，不是外部证书证明。密码经本机窗口进入进程内存，通过本地命名管道供 SSH 使用，未写入参数、环境变量或文件。通道结束记录见 [28](28-close-credential-channel.json)。

## 部署与通过标准

本轮复用已编译产物，没有重跑构建。原生命令在 [commands](commands)，对应完整退出码／stdout／stderr 为本目录编号 JSON。候选、工具及数据均放在路由器 `/tmp/nexmon-csi-20261019-r1`，没有配置自启动。

先完成原模块备份与远端哈希、架构／依赖、实际无线修订检查。随后将固件、nexutil、makecsiparams、录制器及候选模块传到 RAM 目录，逐项验证传输 SHA。只在身份及传输通过后卸载／加载，无强制加载、内核替换或整机重启。

原驱动公开 `firmware_path` 参数的试验参考了上游 [Issue 162](https://github.com/seemoo-lab/nexmon_csi/issues/162)。实测该全局参数被第一颗 2.4 GHz 芯片消费并清空，第二颗 5 GHz 仍加载其原映像；[10](10-load-external-firmware.json)、[11](11-radio-version-readback.json)保留这一部分成功，不能记为 5 GHz 部署通过。原因明确后，采用官方标准路线加载已准备的 `dhd-csi.ko`；[13](13-load-supported-csi-module.json)记录两个无线接口加载 2019 映像及 Nexmon 控制台标识。原模块文件仍保留在只读根文件系统。

5 GHz 启动后先关闭 MPC 自动休眠，保持接口 up。通过一次有界被动扫描选定本地信标源，未变更国家码或发射功率。实际采集参数：

| 参数 | 值 |
| --- | --- |
| 接收接口／频段 | eth6／5 GHz |
| 信道／带宽／FFT | 149／20 MHz／64 点，chanspec `0xd095` |
| 原始发射源 | `a0:70:b7:ee:8d:50`，仅选择其信标首字节 `0x80` |
| 空间流 | 0，NSS mask `0x1` |
| 单链接收 | core 0，mask `0x1` |
| 三链接收 | core 0、1、2，mask `0x7` |
| 格式 | 当前 18 字节头，CSI 包内 chip marker 106 |

参数先由实机 makecsiparams 生成，再在 PC 解码检查 34 字节、chanspec、掩码与 MAC，才发出 setter。IOCTL 500 配置成功，501 回读启用值 `AQA=`（uint16 1）；停止值 `AAA=`（uint16 0）。录制器按单链 10 秒／4,000 包、三链 10 秒／10,000 包、短时检查 20 秒／20,000 包执行，每份 PCAP 另限 32 MiB，先到上限即停。三链两次均在录制结束后关闭 CSI。

通过标准：原始 PCAP 完整、预期 MAC／chip／FFT／流及固定 core 组合正确、至少 20 个完整组、无重复／缺链、解码有限且非全零、录制器无内核丢包或错误。未满足时保存原值并暂停该阶段；不补包、复制链或插值使其通过。

## 实际数据

| 实际录制时间 | CSI 包数 | 完整原始帧组 | 每个 core 包数 | 缺链／重复 | 内核丢包 | 完整组到达率 |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| 单链 10.039880 秒 | 95 | 95 | core 0：95 | 0／0 | 0 | 9.56 Hz |
| 三链 10.039914 秒 | 291 | 97 | core 0／1／2：各 97 | 0／0 | 0 | 9.67 Hz |
| 三链 20.039536 秒 | 576 | 192 | core 0／1／2：各 192 | 0／0 | 0 | 9.61 Hz |

三份原始文件均回传 PC，路由器 OpenSSL SHA 与 PC 回传／解析 SHA 一致。汇总见 [capture-summary.json](capture-summary.json)，原始数据及最终解析：

- [单链 PCAP](singlecore-r1.pcap)、[解析](singlecore-r1-verification.json)。
- [三链 PCAP](threecore-r1.pcap)、[修正后的解析](threecore-r1-verification-v2.json)。
- [20 秒 PCAP](threecore-stability-r1.pcap)、[解析](threecore-stability-r1-verification.json)。

这些是路由器实际 AF_PACKET 录制的原始以太网帧，无合成包或 PC 侧伪造封装。逐份 parser JSON 的 `hardware_test=false` 只表示解析器本身不判定采集来源；真实设备来源由本轮 SSH 原生命令、录制器结果和双端文件哈希建立，不修改该历史字段冒充来源证明。

## 发现与处理

三链第一轮的原始包实际包含 `csiconf=0x0000/0x0100/0x0200`。旧解析器使用低 3 位，曾把它们都判成 core 0，原失败结果保留在 [threecore-r1-verification.json](threecore-r1-verification.json)。上游 BCM4366 微码将 `(stream<<3 | core)<<8` 写入 SHM，C 提取器原样复制，与其它芯片的低字节布局不同。已按 chip marker 106 明确取高字节，并拒绝非法保留位；未放宽缺链或重复门槛。

修正后对**同一份** 291 包 PCAP 离线复核通过 97 组三链，无重录或改写原始值。新增实际头部／真实 PCAP 回归，现有与新增共 **17 项测试通过**，见 [parser-tests-v2.log](parser-tests-v2.log)。此后才开展 20 秒采集，未将原判失败覆盖成通过。代码见 [csi_verify.py](../../host/csi_verify.py) 与 [测试](../../host/test_csi_verify.py)，原来源身份与失败留存不回写。

本机通道的空 IPC 连接处理问题通过无网络本地试验复现、修正，前后日志保留；人工确认前两个实际认证窗口是其输入后手动关闭，故不能把那两次退出归因于路由器或空连接。第三次保留窗口后，SSH 身份检查、传输及部署实际通过。BusyBox 缺少部分命令，使用现有 OpenSSL 做远端 SHA；普通 CLI 选项错误的原退出码保留。模块初始化和未关联状态出现的 `-4`／`-17` 在随包 Broadcom 头中分别为 NOTUP／NOTASSOCIATED；随后启动、参数回读和实采通过。未发现 Oops、Unknown symbol 或内核 panic，不能把所有非零日志抹去或宣称长期无故障。

## 结束状态与后续边界

[恢复记录](26-restore-original-runtime.json)确认：CSI 已关闭，监控模式关闭；原 2022 驱动重新加载，原文件 SHA 不变；两个频段 up，5 GHz 回到原 161/80，2.4 GHz 按原自动选择设置运行在 11 信道（开始时为 8）。仅重启无线服务恢复正常配置，没有整机重启、BOOT／启动脚本变更或系统固件刷写。[最终检查](27-final-state.json)无录制进程、monitor=0、无内核致命错误；[认证进程](28-close-credential-channel.json)已关闭。RAM 目录保留本轮工具和原始包供核对，重启后不保证存在。

本轮证明一台接收节点、一个空间流、固定三个 RX core 的 CSI 通路。约 9.6 Hz 是所选环境信标的到达率，不是设备采集上限，也不代表 300 Hz。最大相邻到达间隔约 205 ms；没有发射侧逐帧台账，不能把内核丢包 0 扩为 RF 整帧丢失 0。接收端时钟尚未联网同步，PCAP 内日期为 2018 年，报告日期按本机实际执行日记录；相对间隔可用，绝对时钟及跨节点同步未验收。

现有模型结构、预处理、SDK、NPU 分配和帧协议均未修改，未连接 Lite，FPGA／HDMI和旧 DATA 暂停保持。后续要面向现场实时骨架，仍需受控发射提高有效帧率、独立 PC 适配层审查 30 子载波与 20 帧时间窗，并解决原模型三个独立接收节点轴；不能把本机三条链复制成三个节点。未实现 AGC／相位校准、标签采集、训练或精度评估，不据此次短时通过保证这些结果。

复用时保留已验证的候选和工具，无需重新编译；使用新的 RAM 目录、原公钥核验与本机密码窗口，按已保存命令的参数顺序重新临时加载。不得把外部 firmware_path 的第一颗芯片效果当 5 GHz 已加载，也不得给 2022 内嵌映像机械套用 2019 固定偏移。需要常驻自启动或更换整机系统时另按实际影响讨论。
