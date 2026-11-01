# 第四台RT-AC86U基础CSI接收验证

2026-10-25，第四台可直接复用现有Nexmon NMD3模块，单链及三链基础5GHz CSI接收通过，无需刷机或降级。本轮只验证第四台接收兼容性，没有恢复300Hz稳定性或相位排查。全部录制已取回，原驱动、无线及原SSH关闭状态已恢复。

## 实际设备与模块

| 项目 | 实读结果 |
| --- | --- |
| 型号／整机系统 | RT-AC86U，ASUSWRT-Merlin-KoolShare 386.14_2 |
| 内核／架构 | Linux 4.1.27 SMP PREEMPT，AArch64，2025-01-16构建 |
| LAN地址／MAC | 192.168.50.1，04:D4:C4:1A:CB:68，DHCP保持开启 |
| 5GHz接口／MAC | eth6，04:D4:C4:1A:CB:6C |
| 无线硬件 | chipnum=0xaa90，chiprev=4，corerev=0x41，boardid=0x798，boardrev=P102，phyrev=0x21 |
| 原无线固件 | 10.10.122.20 r683106，FWID 01-9cc0c14d，2022-07-14 |
| 原驱动SHA256 | a2596d0207e04254cb4f847b9a01e60e45ac5a7ac5c9d36f3de63f53cd44f417 |
| 临时NMD3模块SHA256 | 44295c737800c052030d95f1709d148e19a0ac0324184c638553ad87de1ffcf1 |

原驱动与第二台备份逐字节一致，本机独立备份为[dhd-stock.ko](dhd-stock.ko)；实际insmod和接口启动成功，没有强制加载。底标H/W修订未人工读取，不据系统信息推定底标相同。SSH公钥独立固定，没有覆盖前三台记录。原始证据：[预检](preflight.json)、[兼容性](compatibility.json)、[加载](load.json)。

## 真实无线接收

将一台旧路由器仅接电。等待启动后扫描确认是第三台ASUS_20，源MAC `04:D9:F5:92:29:24`、主信道161、RSSI −35dBm。第四台仅匹配该自有MAC的Beacon（0x80），接收设为161/20，即5.805GHz、20MHz、native64；没有采集周边网络业务或产生受控发包。源机广播161/80不代表这些Beacon帧占80MHz。

| 录制 | CSI记录／完整事件 | 原生采集结果 |
| --- | --- | --- |
| 单链core0，约10秒 | 97／97 | 194条网络记录（CSI＋NMD3），内核丢包0，exit0 |
| 三链core0/1/2，约10秒 | 294／98，各core98条 | 588条网络记录（CSI＋NMD3），内核丢包0，exit0 |

三链缺组0，294条CSI和294条NMD3全部配对；98个事件均为Beacon，无Retry、无重复身份，诊断issues为空。恢复NMD3保存的原始FFT words28..30后，56个占用子载波的I/Q全部有限，各链无全零CSI记录；少量孤立子载波为0，不声称每个点始终非零。约9.7事件/秒为信标速率，不是300Hz结果。TSF低16位不适合在该低速录制中直接展开成完整连续无线时钟。

数据与回执：[单链PCAP](single.pcap)、[三链PCAP](three.pcap)、[单链采集](singlecore.json)、[三链采集](threecore.json)、[单链解析](single-verification.json)、[三链解析](three-verification.json)、[元数据](three-metadata.json)。解析器的`hardware_test=false`表示解析步骤离线，不改变PCAP来自本轮真实无线接收这一事实。跨机传输SHA与路由器端一致。

## 恢复和结论边界

模块和工具仅位于`/tmp/nexmon-fourth-router-20261025-r1`，设置180秒闲置／600秒硬期限恢复保护。结束主动加载第四台自己的原驱动、重启无线服务，核对两频段up=1、AP=1、monitor=0、原SSID及白名单NVRAM一致，prism接口消失。5GHz回到161/80；2.4GHz自动选信道由7变6，自动信道设置0保持。原驱动哈希不变，armed=0、restored=1、watchdog已退出，见[实际恢复](restoration.json)。未重启整机或改LAN/DHCP。

SSH恢复原`sshd_enable=0`及空端口，网页读回并核验22端口拒绝连接；认证进程exit0，见[SSH恢复](ssh-restoration.json)和[进程退出](auth/closed.json)。密码只用于本机内存认证，没有写入命令行、环境或文件；认证运行时已清除。台式机临时192.168.50.102移除，原192.168.126.100及DHCP Disabled保持，WLAN 172.28.193.93保持。

内核快照连续重合段确认可做新增检查，两阶段未发现新增panic、Oops、BUG、Call Trace、OOM或lockup。加载采集阶段新增IOCTL −4共37行、CHANIM −25共1行、SROM CRC提示8行（伴随Using external nvram）；恢复阶段另有−4／−23／−20／−29、WMF／IGMP、CHANIM及xtlv缓冲警告。不把短时采集成功扩大为所有固件功能完全兼容，也不把初始化警告直接认定为崩溃。[检查汇总](data-and-restoration-checks.json)及原始[dmesg前](dmesg-before.txt)、[采集后](dmesg-after.txt)、[恢复后](dmesg-restored.txt)保留。

**通过范围：第四台Nexmon部署兼容、5GHz单链和三链基础接收。** 四台基础接收设备已齐备；独立发射、稳定300Hz、三接收节点同步、相位问题和人体精度仍需分别验收。模型结构、预处理数学、SDK和板端协议保持，没有连接Lite或执行推理。下一步多机接入前需明确各LAN地址及DHCP角色；本轮未自主修改这些持久设置。
