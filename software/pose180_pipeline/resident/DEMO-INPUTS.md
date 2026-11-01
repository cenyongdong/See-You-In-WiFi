# 双输入演示与源码阅读入口

当前[r4部署](../../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)采用原epoch99、TopK=3、严格score>0.2、CPU多人跟踪／滤波；官方输入为30段、8700个不同窗口、1／2／3人各10段，默认有限运行1800秒，来源与结果见[长测](../../../FPGA/csi_preprocess/LONGRUN.md)。实时采集和官方预采CSI共用PS＋PL预处理、NPU推理、PL骨架合成及独立PC双页；官方入口读取CSI执行新推理。10月29日[三片段](DATASET-PLAYLIST.md)及旧Top1仅保留历史记录，旧交付包已清理。

## 两项展示

| 项目 | 实时采集 | 官方预采数据 |
|---|---|---|
| 包内入口 | `sh start-live.sh` | `sh start-dataset.sh` |
| 启动器参数 | `--input-source live_csi` | `--input-source official_dataset` |
| 原生参数 | `--csi board/csi.conf --input-port 0` | `--dataset board/dataset.piwcsi2 --input-port 0` |
| 输入模块 | `src/input/csi.cpp` → `src/input/nexmon/` | `src/input/dataset.cpp` |
| 结束条件 | 手动停止；可指定 `--seconds 300` | EOF 自动正常退出；可提前停止 |
| 来源记录 | 每轮 `request.json`、状态与 CSI 诊断 | 同上及 `dataset.json` 的 split、sequence、样本映射和哈希 |

最新三片段包的 `start.sh` 默认官方数据；`start-live.sh` 显式选择实时采集。数据集默认按清单顺序播放一轮，可使用 `sh start-dataset.sh --dataset-repetitions 3`；上限为 30 轮且总输入不超过 9000（420 帧清单最多 21 轮）。每段及每轮重置跟踪代次，原样本身份保留。`--seconds 0` 在数据集模式下仍会在 EOF 退出。文件缺失、身份不符或选择错误会拒绝启动，不自动转为实时采集。

此前 r2 双输入包为 train / S51_10 的单人片段，TopK=1；当前包顺序播放 1／2／3 人，单人恢复原 S51_10 并裁剪至约 10 秒，双人和三人各约 9 秒。训练集演示不计为独立测试精度。可按下文准备其它片段并重新生成独立包，不直接修改已打包输入绕过身份检查。

## 安全切换和查看

1. 先按[最终部署说明](../../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)核对本次启动资格。首次未知 boot_id 或启动消费已用过时，安全停止后执行 `sh prepare-boot.sh`，安排正常重启；它本身不重写 BOOT 或重启。返回后在板端包目录执行 `sh check.sh --input-source live_csi` 或 `sh check.sh --input-source official_dataset`。检查本身不初始化 SDK。
2. 需要 PC 展示时先在 Windows 启动包内 `start-pc.ps1` 并打开网页，再启动板端选定入口。默认板端 `192.168.50.49` 是临时别名；本机推荐固定有线 `-Board 192.168.126.49 -LocalAddress 192.168.126.100`，其它电脑使用自己的地址，见[PC 连接说明](../host/README.md)。页面端口 `39380`，PC 断开不停止板端。
3. 执行 `sh stop.sh` 请求正常退出，随后 `sh status.sh` 检查 native／supervisor 已退出、`native_shutdown_complete=true`、设备占用为空和临时地址已清理。数据集 EOF 也需要检查关闭结果。
4. **同一清单内的片段自动切换，不需要重启。** 程序完整退出后重新启动，或切换为另一种输入，仍需正常重启并重新预检。功能启动消费入口每次 FPGA 配置只能使用一次；安全退出不会重置它。安全停止确认后执行 `python3 board/startup.py prepare-boot`，再执行已授权的正常 `reboot`，回来后重新 `check` 和选择入口。

`release_blocked`、缺少关闭证明或仍有占用时，保留原资源和独占，先按现有恢复流程处置，不能直接切换、强杀或盲目重试。`recover.sh` 仅作已证明安全的收尾，不初始化 SDK。两个输入都复用现有 PC 网口别名管理；数据集模式不开 CSI 接收端口，也不登录或修改路由器。已安装的路由器采集服务独立保留。

## 从源码构建与准备输入

项目中的核心源码已集中到 [../src/](../src/README.md)，可直接按模块查阅。以下路径相对于 `software/pose180_pipeline/`：

- `control/startup.py`、`input_config.py`：输入选择、启动预检、独占和运行请求。
- `src/app/main.cpp`、`src/common/core.hpp`：唯一推理线程、最新完整窗口、独立消费者和收尾顺序。
- `src/input/csi.cpp`、`dataset.cpp`：两种输入适配器，仅发布拥有自身字节的 `Input`。
- `src/preprocess/`、`src/inference/`：原数学、SDK 所有权、首次输出及在途释放保护。
- `src/pose/`、`src/display/`、`host/presentation.mjs`：后处理与双路显示。
- `control/service.py`、`process_guard.py`、`startup_network.py`：监督、父进程死亡、身份核验和网络回收。

原生构建要求 Linux、CMake ≥3.24、C++17；ARM64 交叉构建沿用 GCC 9.4 与 Icraft/customop 3.39.0。SDK 和模型不包含在纯源码归档中；完整演示包另含已核对的模型和 BOOT 备份。BOOT 不自动安装，SDK 不设置自启动。

```sh
cd software/pose180_pipeline
cmake --preset native-offline
cmake --build --preset native-offline

# ARM64 SDK环境（当前FPAI容器）
cmake --preset csi-v3-arm64
cmake --build --preset csi-v3-arm64
```

当前新建CMake构建目录默认启用 `PL_CSI`、`PL_OVERLAY`、`PL_FILTER` 与 `PROBE_FREE_DRAIN`，对应已发布CSI v3位流；`PL_POST`保持关闭。SDK目标仍通过ARM64预设启用，普通本机配置保留不依赖SDK的离线测试。预设显式设置完整选项，重新配置时可覆盖旧缓存里的OFF；仅修改CMakeLists默认值不会自动覆盖已有缓存。可在configure命令追加`-B <独立目录>`，随后使用`cmake --build <同一目录> --target pose180_demo`。

`PL_FILTER=ON`保留已验证位流中的寄存器接口，人物滤波仍由CPU执行。通用打包器核对实际CMake缓存与CSI v3身份，并写入`preprocess_backend=pl`、`renderer_backend=pl`；原生程序若不经启动器直接执行，仍须显式传入`--preprocess-backend pl --renderer-backend pl --hardware-profile probe-free-drain-overlay-csi-v3`及所需参数。旧硬件构建必须显式选择其完整开关组合，不能混用当前默认值。

在已有 NumPy／h5py 环境准备官方原始 MAT：

```powershell
python software/pose180_pipeline/control/dataset_input.py --dataset-root D:/Person-in-WIFI-3D/Person-in-WiFi-3D-repo/data/wifipose --split train --sequence S51_10 --start 10 --count 290 --hz 15 --output .local/new-official-clip
python software/pose180_pipeline/control/test_dataset_input.py .local/new-official-clip
```

完整项目中用 `tools/build_startup.py --work <新构建目录>` 构建，完成检查后用 `tools/package_startup.py --work <新包目录> --build-work <构建目录> --dataset <片段目录>` 打包。这两个工具位于 `software/pose180_pipeline/` 下。打包工具还需要项目内已验收模型、默认 BOOT 与验证记录；纯源码归档的独立编译不依赖这些本地历史资产。

本次审查、实际检查结果和仍未验收的边界见 [FINAL-REVIEW.md](FINAL-REVIEW.md)。
