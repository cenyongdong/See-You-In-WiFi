# CSI 分组流水与骨架绘图：当前发布包

发布日期：2026-10-31，部署说明与实时采集配套更新：2026-11-01，r4（RAR）。正式交付目录为 `pose180-csi-release-20261031-r4`。

## 已发布内容与验证边界

- 原 epoch99／180-query 模型；TopK=3，严格 score >0.2，CPU 多人跟踪与 One Euro 保持。
- PS：CSI 输入与组窗、FP32转换、相位双精度收尾／边界回退、姿态后处理与坐标投影。
- PL：CSI CORDIC 幅度／原始相位，90点完整组读算流水；二维骨架、关节点、动态信息与HDMI合成。
- NPU：原模型推理。PC：可选三维展示及板端耗时，独立于板端主链。
- 默认输入为官方 train 的30个连续片段、8700个不同窗口，1／2／3人各10段，15 Hz播放、最多重复4轮；默认1800秒有限运行。它是数据集新推理，不是实时采集或独立测试精度评测。
- 本包复用已完成30分钟实测的 ARM64程序、模型、输入与BOOT，补齐最新PC代码和发布说明；新压缩包未另外启动SDK测试。原长测25396次推理／HDMI采纳，存在少量发送丢弃、最长2.29秒结果间隔及一次PC人工重启，完整边界保留于 `evidence/longrun-summary.json`。
- 420窗独立预处理：PS完整5.647ms→PL混合4.043ms，CPU5.629→3.973ms；幅度特征最大差0，相位最大差2.3842e-7rad，含1次全窗边界回退。并非逐位无损或真值精度验收。

本次r4保留最新CMake默认值、预设与构建／打包配置，并整理源码、权重和性能证据，运行程序、模型、数据和BOOT与r1保持相同字节。新默认配置重新编译结果也与已发布程序一致。r4是本机交付修订，本轮未连接或重新部署开发板；最近已核验的板端目录仍是`/root/pose180-csi-release-20261031-r1`，配套运行能力相同。下方r4路径用于今后的独立解压部署。

## 文件与环境

| 路径 | 内容 |
|---|---|
| `board/` | 已验证ARM64程序、启动控制、模型、原始CSI输入与身份清单 |
| `boot/BOOT.BIN` | 最新版替换位流 |
| `router-service/` | 四台既有RT-AC86U的已验证开机服务安装文件、角色／校验清单与首次安装脚本 |
| `pc/`、`start-pc.ps1` | 最新PC服务、网页及Three.js必要资源 |
| `build-config/`、`SOURCE.md` | 最新CMake／预设／构建打包脚本快照与完整源码说明；实际编译使用完整源码包的原目录结构 |
| `evidence/` | 数值／性能、NPU对照、物理资格、长测与默认BOOT核验 |

板端要求现有 ARM64 Icraft/customop 3.39.0 与 Python 3；PC要求已有 Node.js 20+，无需 npm install。SDK和工具安装包不重复分发。模型、官方数据及厂商IP适用各自许可，见第三方声明。

BOOT SHA256：`23922f488d9d4842f217f1b318624c82607e35c6dc0c0b2ea3c803ca4023aa35`。
程序 SHA256：`e85fac442dadb22e263698242c8dbcb63ee5841b1b52c2ba8436bb8d5a1a1bb3`。

## 板端部署与默认位流

`boot/BOOT.BIN` 是包含最新版CSI v3＋骨架绘图位流的完整BOOT启动镜像，用于替换启动分区中的同名镜像；它不是可直接改名使用的裸 `.bit` 文件。本部署包只附最新版BOOT，不附旧版位流。

本包为 RAR5。先在 PC 使用支持 RAR 的解压工具解压，再用 SCP／SFTP 将整个 `pose180-csi-release-20261031-r4` 目录上传到 `/root/`，无需板端安装 RAR。不要覆盖旧运行目录。RAR 从 Windows 解压上传后先恢复原生程序执行位：

```sh
cd /root/pose180-csi-release-20261031-r4
chmod +x board/pose180_demo
python3 boot_control.py audit
```

上轮发布已直接读取启动分区：`BOOT.BIN` 与上述最新镜像完全一致、设备占用为空，因而未重复写BOOT或重启。启动分区中的其它历史BIT文件不代表实际默认；默认配置由BOOT镜像携带。默认位流不等于SDK或演示开机自启动，本包不安装推理自启动。

仅在另一设备确认为已知r2启动身份、负载安全结束且具备本机身份时，使用 `python3 boot_control.py install` 安装v3，再按受控流程正常重启；其它BOOT身份会被拒绝，不绕过检查。安装前脚本先读回设备实际BOOT并核验为已知身份，再保存到 `boot-operations/BOOT-before.readback.bin`。该文件仅是此次真实升级产生的本机恢复回执，不随交付预装旧版位流；没有有效读回回执时恢复操作会拒绝。未知BOOT身份不自动覆盖，先完成设备身份及安全恢复核对。

## 手动运行与安全结束

新解压包不携带已消费的启动凭据，也不把此前只读BOOT核验伪装为SDK实测。首次演示前，确认所有旧任务安全结束：

```sh
sh prepare-boot.sh
# 仅当 prepared=true 且设备空闲时正常重启
python3 reboot.py
```

重连后：

```sh
cd /root/pose180-csi-release-20261031-r4
sh check.sh --input-source official_dataset
sh start-dataset.sh
sh status.sh
```

默认运行1800秒，也可首次启动时指定 `sh start-dataset.sh --seconds 120`；相邻片段在同一个SDK生命周期内切换。提前结束执行 `sh stop.sh`，核对 `running=false`、`native_shutdown_complete=true`、`device_owners=[]`。每次FPGA配置只允许一次功能启动消费；完整结束后再启动或切换输入，须重新prepare、正常重启、check。若完成证明缺失或release_blocked，不强杀释放或盲目重试。

## 实时CSI采集部署

实时模式使用一台TX和三台RX，原始CSI经有线网直达开发板，PC只作可选观察端。以下命令分清“PC”“路由器”和“开发板”执行位置。首次使用先完成上方板端文件部署与BOOT核对；已有服务时直接从第3步开始。

### 1. 接线、网络与采集配置

| 设备 | 角色／地址 | 配置 |
|---|---|---|
| 第一台路由器 | RX1，192.168.50.1/24 | 唯一DHCP服务；接收CSI |
| 第二台路由器 | TX，192.168.50.2/24 | DHCP关闭；无线发射 |
| 第三台路由器 | RX2，192.168.50.3/24 | DHCP关闭；接收CSI |
| 第四台路由器 | RX3，192.168.50.4/24 | DHCP关闭；接收CSI |
| 开发板eth0 | 管理地址192.168.126.49；运行临时地址192.168.50.49/24 | 运行期间监听TCP 39033 |
| 可选PC有线网卡 | 示例192.168.50.102/24、192.168.126.100/24 | 同一网卡可添加两个地址；保留WLAN外网，勿占用其它设备地址 |

TX的4个LAN口分别连接开发板、RX1、RX2、RX3，WAN留空。PC接任一RX的空闲LAN口；HDMI显示器直连开发板。四机LAN地址／DHCP先在管理界面设置为表中值；服务安装脚本保留这些设置，不自动配置LAN。

本项目四机已验证配置为RT-AC86U、eth6、信道161／20MHz。TX发送300Hz；三RX启用三天线并过滤TX无线MAC `f0:2f:74:39:45:6c`，随后向开发板 `192.168.50.49:39033` 发送。TX的LAN MAC与上述无线MAC不同，不混用。`board/csi.conf` 已配置这组地址、来源、通道与 `alignment=adaptive`；现有gain和相位处理参数保留。

板端启动器会在运行前检查地址冲突并临时添加 `.50.49/24`，正常安全结束后只撤销自己添加的地址。无需额外手动启动接收器、修改CSI端口或在PC转发数据。只配置PC的`.50.102`时，启动前未必能通过临时地址SSH开发板，因此同时保留`.126.100`，用`.126.49`进行管理。

### 2. 四台路由器首次安装（已安装则跳过）

`router-service/` 附四机已实测的v2服务文件及 `package.json` 校验信息。安装脚本按角色核对RT-AC86U型号、LAN IP／MAC、JFFS脚本开关和压缩包SHA256，保留原KoolShare开机钩子及原厂驱动。它绑定本项目既有四台设备，不是任意同型号路由器的通用刷机包；不同设备或固件需重新匹配驱动与身份。首次安装前在路由器管理界面启用SSH和JFFS自定义脚本，保持已有匹配固件与内核。

在PC的解压包根目录上传对应文件，然后登录对应路由器安装。下列每段中的 `scp`／`ssh` 在PC执行，`sh /tmp/install.sh ...` 在已登录的路由器执行。SSH按提示认证，不把密码写进命令。
sh /jffs/pose180-csi/service.sh enable
exit  # 回到PC终端再处理下一台

```text
# RX1：192.168.50.1
scp -O .\router-service\install.sh .\router-service\rx1-autostart-v2.tar.gz admin@192.168.50.1:/tmp/
ssh admin@192.168.50.1
# 登录该路由器后执行：
sh /tmp/install.sh rx1 /tmp/rx1-autostart-v2.tar.gz 4d9735aee61da3afc50c8ba97bac5fe44c63e83cc7660a0a00f50068d6c8e4b1
sh /jffs/pose180-csi/service.sh enable
exit  # 回到PC终端再处理下一台

# TX：192.168.50.2
scp -O .\router-service\install.sh .\router-service\tx-autostart-v2.tar.gz admin@192.168.50.2:/tmp/
ssh admin@192.168.50.2
# 登录该路由器后执行：
sh /tmp/install.sh tx /tmp/tx-autostart-v2.tar.gz d5082c7e39dfe1ebcc564a20e70ab21153b6a9580cf115da1d402a30e3633f62
sh /jffs/pose180-csi/service.sh enable
exit  # 回到PC终端再处理下一台

# RX2：192.168.50.3
scp -O .\router-service\install.sh .\router-service\rx2-autostart-v2.tar.gz admin@192.168.50.3:/tmp/
ssh admin@192.168.50.3
# 登录该路由器后执行：
sh /tmp/install.sh rx2 /tmp/rx2-autostart-v2.tar.gz 630deae80f19a876f9388d4e7de8f5d283af48b6a379331bab9a8d73eb248914
sh /jffs/pose180-csi/service.sh enable
exit  # 回到PC终端再处理下一台

# RX3：192.168.50.4
scp -O .\router-service\install.sh .\router-service\rx3-autostart-v2.tar.gz admin@192.168.50.4:/tmp/
ssh admin@192.168.50.4
# 登录该路由器后执行：
sh /tmp/install.sh rx3 /tmp/rx3-autostart-v2.tar.gz 8206ea4ee516ade2bf78aef21070348b1c0f44e0b5ed54a4c1f668b258bb726d
sh /jffs/pose180-csi/service.sh enable
exit  # 回到PC终端再处理下一台
```

安装要求 `/jffs/pose180-csi` 尚不存在。已有该目录时，先用下方status核对角色与服务；不要重复安装、覆盖钩子或把另一角色文件装上去。安装不会启动板端SDK；首次安装成功后在该路由器执行 `sh /jffs/pose180-csi/service.sh enable`。开机服务等待启动至少60秒及接口就绪，TX／RX先后上电均可。

### 3. 路由器启动与检查（已有服务的常用入口）

分别SSH登录四台路由器，执行相同命令：

```sh
sh /jffs/pose180-csi/service.sh status
# 已安装但未启用时：启用开机服务并启动本次服务
sh /jffs/pose180-csi/service.sh enable
sh /jffs/pose180-csi/service.sh status
```

TX应为 `transmitting`，`TX_renewals` 随运行增加；RX在板端尚未监听时处于 `backoff` 且 `fault=0` 属于正常等待，板端启动后自动接入并增加字节计数。每台只保留一个守护进程。不要再并行运行旧包 `load.sh`、`router_ctl.sh start` 或其它CSI／TX无线负载。

### 4. 开发板预检与有限实时运行

在开发板执行。若本次FPGA配置尚未为此包准备启动凭据，或此前已运行／切换过数据集输入，先在所有旧负载安全结束后执行：

```sh
cd /root/pose180-csi-release-20261031-r4
sh prepare-boot.sh
# 仅当prepared=true、设备空闲时执行；本步骤不安装新BOOT
python3 reboot.py
```

重连开发板后开始实时模式：

```sh
cd /root/pose180-csi-release-20261031-r4
sh check.sh --input-source live_csi
# 确认ready=true、input.input_source=live_csi、SDK_started=false后启动
sh start-live.sh --seconds 300
sh status.sh
```

`start-live.sh` 默认300秒；首次运行也可用 `--seconds 120`。它选择 `board/csi.conf`，关闭PIWCSI2适配输入，与官方数据入口互斥。输入不存在时不会自动改用官方数据。首次结果前为七色条待机；三RX数据齐全并产生新窗口后，骨架和动态信息随新推理更新。`check`只做板端预检，不保证无线数据已到达；仍需结合四机状态、运行日志和新推理计数判断。

### 5. PC双页与停止

PC接RX的LAN口、有线地址为`.50.102`时，在同一个解压包根目录执行：

```powershell
.\start-pc.ps1 -Board 192.168.50.49 -LocalAddress 192.168.50.102
```

打开滤波前 `http://127.0.0.1:39381/` 和滤波后 `http://127.0.0.1:39380/`。也可保留本页下一节的`.126.49/.126.100`管理网段方式。PC不必常驻，退出PC观察器不停止板端推理／HDMI。

在开发板正常结束：

```sh
sh stop.sh
sh status.sh
```

核对 `running=false`、`native_shutdown_complete=true`、`device_owners=[]` 及网络清理完成；运行记录位于 `board/runs/`。再次启动或从实时切回官方数据，仍需prepare／正常重启／check。只停板端时RX回到等待，TX继续发射；若也要停止无线发射，在四台路由器分别执行 `sh /jffs/pose180-csi/service.sh stop`，需要关闭后续开机启动时改用 `disable`。

### 6. 没有新骨架时的定位顺序

- 四机SSH不通：先检查LAN接线、地址、DHCP及PC有线网卡，不能通过修改Wi-Fi连接替代板端有线接入。
- TX未发送／有fault：查看服务status和 `/tmp/pose180-csi/` 日志，先停止冲突无线负载；不在未知运行状态反复卸载驱动。
- RX持续backoff：检查板端是否已启动live模式、临时`.50.49`是否存在，以及`board/csi.conf`的三RX地址和TCP 39033。单独check通过并不会开启接收监听。
- RX字节增长但无新推理：结合 `sh status.sh` 返回的运行目录，查看共同窗口／输入代次和新推理计数；组窗缺失与NPU失败分别处理，不能用重复扫描的旧画面冒充新结果。
- 提示功能启动已使用、缺少完成证明或 `release_blocked`：先确认前一轮安全关闭并按已有恢复流程处置，不直接重试SDK。

以上安装资产与路由器自启动来自既有四机实测；本次是部署说明／交付整理，没有新连接路由器、启动SDK或重新做实时CSI精度及稳定性验收。当前30分钟性能证据来自官方数据模式，不能替代实时场景精度。


## PC显示与耗时

PC解压同一个包，在包根目录执行：

```powershell
.\start-pc.ps1 -Board 192.168.126.49 -LocalAddress 192.168.126.100
```

默认同时启动两路：

- **滤波前：** http://127.0.0.1:39381/ ，来自原始NPU候选，仅做TopK=3／score>0.2选择，没有人物关联与One Euro。
- **滤波后：** http://127.0.0.1:39380/ ，使用板端实际后处理结果，与HDMI共用。

两页都保留三维视角和板端耗时，可并排对照。view通过本机HTTP共享raw计时，避免抢占39383单消费者通道；不将raw骨架混入滤波后结果。其它电脑将LocalAddress换成自己的有线地址；默认板端192.168.50.49是临时别名，当前开发接线建议显式使用上面的192.168.126.49。

Ctrl+C结束启动器管理的两个PC观察进程，板端推理／HDMI独立继续。日志在包根`pc-logs/`；已占用端口导致启动失败时不会结束其它进程。可用`-Seconds 120`有限观察。不要另外启动第三个raw消费者；已有观察器请先正常关闭再使用本入口。

如果`/api/state`显示`connected: true`且`received`持续增加，但网页仍停在等待，检查浏览器控制台。`/vendor/three.module.js`或`/vendor/OrbitControls.js`的`ERR_EMPTY_RESPONSE`表示原部署包可能缺少Three.js离线资源。2026-11-01已补齐当前部署RAR并修正打包规则；旧目录可将`pose180-pc-assets-fix-20261101-r1.rar`解压到含`start-pc.ps1`的部署包根目录，合并`pc/`后按Ctrl+F5刷新。无需重新安装Node.js、执行npm或重启板端。

## 源码与恢复

完整源码包：`pose180-complete-sources-20261031-r4.rar`，包含当前PS／PC／PL及上游模型原始代码、IP配置、约束、实际构建脚本、关键报告，以及JSON／RAW／ONNX模型和当前合格BIT；补齐目标器件所需厂商网表、IP综合结果和增量实现基线，排除无关器件和重复构建缓存。重建外部依赖见 `SOURCE.md`。旧本机部署包与源码包清理；工作区原始证据保留，部署包仅附最新版BOOT。关键数据统一见 `PERFORMANCE.md`。

源码RAR已独立解压完成ARM64、离线构建和核心RTL仿真，ARM64程序与本包逐字节相同；详见 `SOURCE.md` 和 `evidence/current/rebuild/result.json`。10月31日交付整理未重跑完整FPGA布局布线；11月1日随后完成r4源码RAR新解压的完整本地实现与位流生成，详见[重建报告](FPGA-REBUILD-20261101-r1.md)。新位流未上板，默认BOOT和运行程序未更换。

本次部署说明更新已同步到部署RAR；独立FPGA重建验证所用源码RAR身份保持，未更改模型、ARM64程序或最新版BOOT。
