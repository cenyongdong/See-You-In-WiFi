# 第三台RT-AC86U基础接收验证

2026-10-23，第三台兼容现有NMD3模块，单链及三链基础CSI接收通过。开启SSH，最终保留仅LAN、22端口；无线运行已恢复自带驱动，无采集、恢复或内存认证进程常驻。本报告只对应基础接收检查，后续300Hz新授权与实测另记。

## 身份及兼容性

| 项目 | 本机实测 |
|---|---|
| 管理地址／有线MAC | 192.168.50.1／04:D9:F5:92:29:20 |
| 5GHz接口／MAC | eth6／04:D9:F5:92:29:24 |
| 系统／平台 | Merlin-KoolShare 386.9_0，Linux 4.1.27，AArch64，2023-05-02构建 |
| 无线硬件 | chipnum=0xaa90、chiprev=4、corerev=0x41、boardid=0x798、phyrev=0x21，与第一台一致 |
| 原无线固件 | 10.10.122.20 r683106，FWID 01-9cc0c14d |
| 原驱动SHA256 | 67faa220d9add7faa3b3a52f5ed7e82899548e2e66aed9a3a25506b6aa1ab323，与第一台字节一致 |
| 临时接收模块SHA256 | 44295c737800c052030d95f1709d148e19a0ac0324184c638553ad87de1ffcf1，复用已验收NMD3，无新构建 |

SSH主机公钥与前两台不同，独立记录于本批known_hosts，未替换全局旧机记录。原驱动独立取回，系统文件未覆盖；模块及工具仅部署到/tmp/nexmon-third-router-20261023-r1，由180秒闲置／600秒硬期限保护恢复。实际加载成功，无强制加载。[原始预检](01-preflight.json)、[原驱动备份](03-stock-backup.json)、[兼容依据](compatibility.json)、[实际加载](06-load.json)。底标H/W修订号未人工读取，不据驱动相同推断底标相同。

## 实收结果

第二台仅接电，扫描识别自有MAC F0:2F:74:39:45:6C、主信道161、约−31dBm。第三台限定此MAC及Beacon首字节0x80，接收161/20，即5.805GHz、20MHz、native64；未连接或采集其它网络业务。

| 10秒录制 | CSI记录 | 有效事件 | PCAP到达组率 | 内核丢包 |
|---|---:|---:|---:|---:|
| core0 | 97 | 97个单链组 | 9.665Hz | 0 |
| core0/1/2 | 294 | 98个完整三链组 | 9.766Hz | 0 |

三链294条NMD3与CSI全部配对，无缺链、重复核心、重复身份、Retry或配对问题。恢复PHY覆盖前原字后，56个有效载波及完整64点解码均有限；存在少量单载波零值，未出现全零CSI记录。原生录制退出0，包数及字节预算未耗尽。Beacon约9.77Hz不能代替300Hz验证；低16位RX时钟亦不用于此次低速跨包连续时序认定。

原始数据：[单链](single.pcap)、[三链](three.pcap)；解析：[单链](08-single-verification.json)、[三链](10-three-verification.json)、[元数据](10-three-metadata.json)、[I/Q与恢复检查](14-data-and-restoration-checks.json)。解析器hardware_test=false仅表示该步骤离线执行，数据来自本次实际接收。

## 恢复及边界

已重新加载本机自带驱动并restart_wireless，无整机重启。原驱动哈希、SSID及无线NVRAM白名单保持；两接口up、AP=1、monitor=0，prism消失，armed=0、restored=1、看门狗退出。2.4GHz在原自动选信道设置下由8变为6，5GHz恢复161/80。内存认证进程退出0，凭据未写入命令行、环境变量或文件。[恢复原值](11-restore-and-verify.json)、[认证关闭](13-auth-stopped.json)、[汇总](run-summary.json)。

SSH原来关闭，保留开启。首次提交使用了错误的选项编号1；读取本机页面发现其含义为LAN & WAN后，立即修正为2（仅LAN）。最终网页及实际SSH读回均为sshd_enable=2、port=22、pass=1、forwarding=0，登录成功；不能将首次提交描述为已限定LAN。LAN地址与DHCP保持原值，未将第三台与旧的同地址样机并网。

采集后有2处初始化IOCTL −4，无新增Oops、BUG、Call Trace、Kernel panic或Unknown symbol，不声称日志完全无警告。没有刷机、启动自动加载、Lite访问或模型／数学／SDK／板端协议修改。基础接收通过不代表第三台稳定300Hz、相位问题根治、跨接收机同步或人体模型效果通过。
