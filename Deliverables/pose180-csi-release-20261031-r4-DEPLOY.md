# CSI 分组流水与骨架绘图：当前发布包

发布日期：2026-10-31，精简交付修订r4（RAR）。正式交付目录为 `pose180-csi-release-20261031-r4`。

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
| `boot/BOOT.BIN` | 当前合格CSI v3＋骨架绘图启动镜像 |
| `boot/BOOT-baseline-csi-v2.bin` | 上一合格版本恢复备份 |
| `pc/`、`start-pc.ps1` | 最新PC服务、网页及Three.js必要资源 |
| `build-config/`、`SOURCE.md` | 最新CMake／预设／构建打包脚本快照与完整源码说明；实际编译使用完整源码包的原目录结构 |
| `evidence/` | 数值／性能、NPU对照、物理资格、长测与默认BOOT核验 |

板端要求现有 ARM64 Icraft/customop 3.39.0 与 Python 3；PC要求已有 Node.js 20+，无需 npm install。SDK和工具安装包不重复分发。模型、官方数据及厂商IP适用各自许可，见第三方声明。

BOOT SHA256：`23922f488d9d4842f217f1b318624c82607e35c6dc0c0b2ea3c803ca4023aa35`。
程序 SHA256：`e85fac442dadb22e263698242c8dbcb63ee5841b1b52c2ba8436bb8d5a1a1bb3`。

## 板端部署与默认位流

本包为 RAR5。先在 PC 使用支持 RAR 的解压工具解压，再用 SCP／SFTP 将整个 `pose180-csi-release-20261031-r4` 目录上传到 `/root/`，无需板端安装 RAR。不要覆盖旧运行目录。RAR 从 Windows 解压上传后先恢复原生程序执行位：

```sh
cd /root/pose180-csi-release-20261031-r4
chmod +x board/pose180_demo
python3 boot_control.py audit
```

上轮发布已直接读取启动分区：`BOOT.BIN` 与上述最新镜像完全一致、设备占用为空，因而未重复写BOOT或重启。启动分区中的其它历史BIT文件不代表实际默认；默认配置由BOOT镜像携带。默认位流不等于SDK或演示开机自启动，本包不安装推理自启动。

仅在另一设备确认为包内r2恢复基线、负载安全结束且具备本机身份时，使用 `python3 boot_control.py install` 安装v3，再按受控流程正常重启；其它BOOT身份会被拒绝，不绕过检查。`fallback`／`fallback-reboot` 仅供确认安全后的独立恢复操作；不要为一般软件异常自动切换BOOT。

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

实时入口保留：`sh check.sh --input-source live_csi`，然后 `sh start-live.sh`，本包默认有限300秒。它复用已有路由器服务，**本次发布未重新验证实时CSI**。当前路由器接线／服务见项目原说明，不与其它无线负载并行。

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

## 源码与恢复

完整源码包：`pose180-complete-sources-20261031-r4.rar`，包含当前PS／PC／PL及上游模型原始代码、IP配置、约束、实际构建脚本、关键报告，以及JSON／RAW／ONNX模型和当前合格BIT；补齐目标器件所需厂商网表、IP综合结果和增量实现基线，排除无关器件和重复构建缓存。重建外部依赖见 `SOURCE.md`。旧本机部署包与源码包按用户要求清理；工作区原始证据和本包r2恢复BOOT保留。关键数据统一见 `PERFORMANCE.md`。

源码RAR已独立解压完成ARM64、离线构建和核心RTL仿真，ARM64程序与本包逐字节相同；详见 `SOURCE.md` 和 `evidence/current/rebuild/result.json`。10月31日交付整理未重跑完整FPGA布局布线；11月1日随后完成r4源码RAR新解压的完整本地实现与位流生成，详见[重建报告](FPGA-REBUILD-20261101-r1.md)。新位流未上板，默认BOOT和运行程序未更换。
