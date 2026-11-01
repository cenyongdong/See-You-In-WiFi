# 2024 epoch442 独立混合推理门检：人工操作说明（2026-10-05）

**旧链入口（2026-10-29）：** 本页属于早期 pose-v1 诊断／验证，当前部署从[最终进度](../../PROJECT-PROGRESS.md)进入；旧主机路径、板端目录、算子计数与阶段授权不能套用最新演示。

**2026-10-06当前路线**：CPU独立候选已验收，ONNX直接对照板端、工程/数值分阶段。
本机ONNX参考已完成；新独立pose_mixed_check候选及[新命令](MIXED-VALIDATION-COMMANDS.md)已交付，尚未编译/板测。
下述停止条件及三端参考要求保留为原检查器历史记录；不要使用旧二进制执行F3，它没有新混合注册/桥。
原CPU Matmul问题保留诊断，不再阻断新工程门检；首版NPU与双路要求保持。

**最新停止条件（2026-10-05）**：独立注册探针已获批准并完成，Matmul及ZG图的TopK/GatherElements/ScatterND共五个Host节点缺少init/forward注册，只有Gather有注册。见HOST-REGISTRY-RESULTS-20261005.md。当前不得执行F2重跑或F3 mixed；先核对SDK官方支持/加载机制，任何修复方案另讨论批准。以下既有阶段命令保留为历史说明，不因命令存在或初始化probe通过而绕过新阻断。软件一般人工操作，特殊问题允许代理工具协助的最新规则见AGENTS.md。

状态：源码、脚本和命令已交付；已完成固定打包及FPAI交叉编译/链接，代理读取产物复核通过。
最新D反馈：板端11项包文件以`files.lf.sha256`校验全部OK、退出码0，ldd已列出的依赖均解析成功；
ZG图inspect返回0，接口/阶段/配置及stderr已由后续截图复核，**D离线检查通过**。
随后运行E probe退出码0，SDK device=25122301；完整产物/日志已复核，**E初始化探测通过，推理与数值结果尚未验证**。
人工实际执行，代理核对日志并维护源码；已有inspect-zg保留，不重复执行。
本轮只检查三个固定真实窗口，不接网络服务、HDMI、VPU或RTSP，不修改模型、BOOT、SDK或FPGA工程。

2026-10-05已提交A及补查截图：GCC9.4.0/CMake3.24.2确认；Icraft和CustomOp均arm64 3.39.0、
第三方包arm64 0.1.1，均已安装。SDK配置目录`/usr/cmake`内Host/ZG330配置及对应头文件/库路径已确认。
最新B/C结果已复核：构建目录`.local/pose-v1-build/inference-20261005-165059-043b0c40`，
二进制SHA256 `d1006f9bd78050ffa484c64bf74fb62542d270c7acca5068e9da611a5bdc05e5`；
7份源码记录和11份包文件哈希/大小全部匹配。**现在准备F1/F2参考；不重传、不重跑D或probe，参考有效前不进入mixed。**
ORT缺失、Windows cmake/cl当前PATH不可见保持，见[环境查询记录](ENVIRONMENT-QUERY-20261005.md)。

Windows工具后续只读定位：`D:\Visual Studio\ Visual Studio 2022\Community`存在MSVC/CMake和厂商开发终端脚本，
目录名开头空格应保留。仅文件存在，SDK/临时终端/CMake生成器及Host编译未验证。
现在先按[WINDOWS-HOST-ENV-CHECK.md](WINDOWS-HOST-ENV-CHECK.md)人工查询，不直接执行F2构建。

同窗口后续查询已确认cl/x64/VS目录及CMake可用，但WindowsSdkDir未设置、WindowsSDKVersion仅`\`，
F2 Windows构建暂停。候选[REFERENCE-NEXT-PLAN.md](REFERENCE-NEXT-PLAN.md)讨论Lite host参考及ORT解析预览，
未批准前不执行候选、不自动补SDK；原F2/F3命令仍受前提限制，不能直接跳过参考进入mixed。

B“先用Lite Host作参考”；本阶段F2执行平台改为Lite，复用现有二进制/optimized图及固定张量。
当前先按[LITE-HOST-COMMANDS.md](LITE-HOST-COMMANDS.md)第1步查询资源并交回，不启动模型。
ORT解析/安装未获批准，F1暂停；F3仍须参考数值有效和配套/并发条件确认，不能直接运行。

## 执行顺序和暂停点

1. Windows查询FPAI中的SDK构建文件、主机编译工具和ONNX依赖，提交输出确认实际路径。
2. 打包已通过门检的原三份CSI和已锁定模型；在FPAI交叉编译，保存完整日志及二进制哈希。
3. 将包和二进制传板，检查哈希/动态库并离线检查模型接口。
4. 单独运行SDK初始化探测，提交版本和日志讨论；**到这里先停，不把退出码0当作兼容性通过**。
5. 配套无新矛盾、探测结果经复核后，用同一包完成ONNX参考、Icraft Host参考和Lite混合推理。
6. 对照数值及后端执行证据，再讨论分数/坐标误差容限。这里没有预设量化误差阈值。

任何步骤失败均保留目录、退出码、stdout/stderr及内核日志，停止后续步骤；不自行安装、降级、换模型、
全CPU替代、修改启动配置或重启重试。外部超时杀进程不保证DMA/NPU恢复到初始状态。

## A. 当前先执行：环境查询

位置：**Windows PowerShell**。下面固定当前worktree，不能替换成Docker原挂载中的旧源码。

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseDocker = 'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
$posePython = Join-Path $poseRoot '.local\pose-v1-conda\python.exe'
& $poseDocker exec FPAI aarch64-linux-gnu-g++ --version
& $poseDocker exec FPAI cmake --version
& $poseDocker exec FPAI dpkg-query -W '-f=${Package} ${Architecture} ${Version} ${Status}\n' | Select-String -Pattern 'icraft|customop'
& $poseDocker exec FPAI find /usr /opt -name 'icraft-hostbackend-config.cmake' -o -name 'icraft-zg330backend-config.cmake'
& $posePython tools\pose-v1\inference_gate.py dependencies
Get-Command cmake,cl -ErrorAction SilentlyContinue | Select-Object Name,Source
```

逐条含义：

| 命令 | 目的、通过标准和停止条件 |
| --- | --- |
| 设置三个变量及工作目录 | 固定源码、Docker与独立Conda入口；找不到路径就停止，不借用koala |
| GCC/CMake版本查询 | 记录实际交叉工具；预期GCC9.4，缺失或版本变化先反馈 |
| dpkg-query | 核对FPAI Icraft/CustomOp实际版本，当前目标3.39.0；输出缺包或不同版本不安装修复 |
| find | 查出SDK CMake实际目录；多份、两个包不在同一目录或未找到时讨论，不随意挑选 |
| dependencies | 只查询NumPy/onnxruntime模块是否存在，不导入ORT、不推理、不安装；ORT缺失需另行批准独立环境安装 |
| Get-Command | 查询Windows CMake/MSVC入口；普通PowerShell未显示cl不证明未安装，可在已安装的x64 VS开发终端查询；没有则讨论Host参考执行工具，不自动安装 |

**请先提交这组输出。** SDK实际目录和Windows编译工具是当前未确认的参数。

## B. 固定打包（Windows PowerShell）

前提：A中的Python存在，历史300样本fixtures仍保留。此步骤不运行模型。

```powershell
$posePackage = Join-Path $poseRoot '.local\pose-v1-inference\package-20261005'
& $posePython tools\pose-v1\inference_gate.py prepare `
  --repo 'D:\Person-in-WIFI-3D\Person-in-WiFi-3D-repo' `
  --fixtures '.local\pose-v1-validation\host-300-20261004\fixtures' `
  --output $posePackage
if ($LASTEXITCODE -ne 0) { throw '打包失败，停止。' }
```

从300份已验证清单中复制S11_01_308/309/310的原始记录和参考张量，保留原帧号，不重新计算或修改预处理。
锁定ONNX、optimized及ZG的JSON/RAW哈希；输出`manifest.json`、`files.sha256`和`inputs/reference/models`。
目录已存在、历史fixtures丢失、输入或模型哈希变化均停止；不覆盖或重新导出模型。

## C. FPAI交叉编译（Windows PowerShell）

前提：A及补查已确认SDK目录为`/usr/cmake`，B样本包准备成功。

```powershell
$poseSdkCmake = '/usr/cmake'
& .\tools\pose-v1\Build-Inference.ps1 -SdkCmakeDir $poseSdkCmake
```

脚本把当前worktree的`software/pose_v1`和工具链文件复制到唯一容器`/tmp`目录；避免使用`/workspace`旧副本。
配置Linux/aarch64、GCC、C++17、Release/O2及预处理`-ffp-contract=off`，仅构建`pose_inference_check`。
链接厂商CMake目标`Icraft::HostBackend`和`Icraft::ZG330Backend`；没有新第三方依赖或直接手填库路径。
不执行二进制或测试。预期产物位于脚本打印的唯一`.local/pose-v1-build/inference-*`目录：
`pose_inference_check.arm64`、`build.log`、`binary-sha256.txt`、`source-manifest.json`。
`file`应为AArch64 ELF，动态依赖应与已安装arm64 3.39.0配套；编译、链接、ELF检查任一失败停止并提交日志。

## D. 传输、哈希和离线接口检查

本次传输、ldd及inspect已人工执行并复核通过，下面读取命令保留供追溯，不需重复执行：

```bash
cd /tmp/pose-v1-inference-20261005
ls -l inspect-zg
cat inspect-zg/graph-io.json
cat inspect-zg/stages.jsonl
cat inspect-zg/run-config.json
cat inspect-zg.stderr.log
```

这些命令不重跑程序、不初始化设备。核对输入float32 `[1,180,60]`、输出依次`[1,100]`与`[1,100,14,3]`，
阶段包含offline_inspection_complete、配置mode为inspect/device_init_allowed为false且无failure.json。
stderr为空是正常情况；若有内容交回分析。文件缺失、接口不符或失败记录出现则停止，保留现场。
下面是此前已执行的传输/检查步骤，保留供追溯，本次不要重新执行。

Windows PowerShell：以下已填入本次C的实际输出目录。板端地址取此前已核对的
`root@192.168.126.49`；若现在变化，先反馈，不猜新地址。SSH口令由用户交互输入。

```powershell
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\inference-20261005-165059-043b0c40'
$poseSsh = 'C:\Windows\System32\OpenSSH\ssh.exe'
$poseScp = 'C:\Windows\System32\OpenSSH\scp.exe'
& $poseSsh root@192.168.126.49 'test ! -e /tmp/pose-v1-inference-20261005 && mkdir /tmp/pose-v1-inference-20261005'
if ($LASTEXITCODE -ne 0) { throw '板端目录冲突或SSH失败，停止。' }
& $poseScp -r $posePackage 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/package'
if ($LASTEXITCODE -ne 0) { throw '样本包传输失败，停止。' }
& $poseScp (Join-Path $poseBuild 'pose_inference_check.arm64') 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/pose_inference_check'
if ($LASTEXITCODE -ne 0) { throw '程序传输失败，停止。' }
```

目的：创建独立临时工作目录，传送样本/模型/程序；不写BOOT、系统库或原工程。目录存在即停止，不能删除历史目录重试。

随后在**Lite的MobaXterm SSH终端**逐条执行：

```bash
cd /tmp/pose-v1-inference-20261005
sha256sum pose_inference_check
cd package
sha256sum -c files.sha256
cd ..
chmod u+x pose_inference_check
ldd ./pose_inference_check
command -v timeout
timeout --version
./pose_inference_check inspect --graph package/models/piw24_ZG.json --output inspect-zg > inspect-zg.stdout.log 2> inspect-zg.stderr.log
echo $?
cat inspect-zg/graph-io.json
```

程序哈希须与C一致，包内每项校验应OK；`ldd`不得有`not found`，timeout须支持GNU的kill-after。
`chmod`只给本次程序执行权限；`inspect`只解析本地模型JSON，不调用Device::Open、不访问硬件。
接口应为一个float32`[1,180,60]`输入，以及依次`[1,100]`分数/`[1,100,14,3]`姿态输出。
退出码须0、不得有failure.json，预期stage为offline_inspection_complete；这仍不是推理通过。
所有命令失败时停止；不要在终端一次粘贴跳过失败检查。

## E. 单独SDK初始化探测（Lite SSH；结束后先交回日志）

E已复核通过，仅覆盖Device::Open/version：阶段完整、stdout报告初始化成功、stderr为空、无failure.json，
device=25122301、icore=FMSHZGV3TECH-AID - 24160628，提供的内核尾部未见探测相关总线/DMA错误。
启动阶段EXT4恢复及journal异常关闭/更换信息已保留，不当作probe错误，不自动修复。
下面命令均已人工执行并提交，留作追溯；不重跑probe或重复读取已有材料。
下一步F1/F2参考环境准备；ORT缺失/Windows Host工具待确认，安装或更换参考平台须另行讨论。

本次probe已经人工执行，退出码0，SDK device版本25122301与既有基线一致。
compatibility_passed=false为源码固定写出的“兼容性待验收”，不代表SDK已经检测失败，也不得改为true绕过验收。
现在仅在Lite SSH读取已保存的结果并交回，不重跑或覆盖目录/日志：

```bash
cd /tmp/pose-v1-inference-20261005
ls -l probe
cat probe/device-version.json
cat probe/stages.jsonl
cat probe/run-config.json
cat probe.stdout.log
cat probe.stderr.log
cat probe.dmesg.log
```

目的：核对icore完整文本、stage应以probe_complete_requires_review结束、mode=probe及device_init_allowed=true，
并检查有无failure.json、SDK警告/异常及内核总线/DMA错误。stdout/stderr为空可能正常，需结合其余文件。
任何文件缺失、失败记录或异常先停并讨论；保存的dmesg尾部为上下文，不把所有旧内核信息归因于本次probe。
当前版本相符与退出码0只证明Open/version返回，不代表模型计算或数值兼容性。
下面是此前前置检查和probe执行步骤，保留供追溯，本次不要重复执行。

D已通过。下述只读查询已人工执行：GNU coreutils timeout 8.30、四个probe路径不存在，
可见进程未见明显AI/HDMI/编码应用。仍需人工确认自0x25122301核验后未替换BOOT或JTAG加载其他位流，
且无其他演示使用设备；确认前不运行probe。以下查询保留供追溯，不需重复执行：

```bash
cd /tmp/pose-v1-inference-20261005
command -v timeout
timeout --version
ps -eo pid,comm,args
ls -ld probe probe.stdout.log probe.stderr.log probe.dmesg.log
```

timeout应为GNU实现并支持既定signal/kill-after参数；缺失或不明确时停止，不安装替代工具。
进程列表用于审查是否有AI/HDMI/编码应用并发，不仅按单一程序名判断；列表不能排除未显示的其他访问方。
最后ls仅查询已有探测证据是否存在：首次未执行时这四个路径应报不存在，属于预期，不是程序故障。
有任一旧probe产物则先讨论，不覆盖、不删除或重新探测。另需人工确认BOOT未再改变、当前没有其他演示/AI/显示程序在用设备。
确认前不执行下面probe命令，不自行停止后台进程或重启板子。

前提：D全部通过，板卡BOOT仍是已确认的25122301，当前无其他AI/显示进程并发访问设备。
如果无法确认并发状态，先讨论。**Open可能访问/初始化硬件，不是先前4字节只读探测**。
本轮已批准方向是独立初始化/混合推理门检；操作人工执行。程序没有reset/check或HDMI/VPU动作。

```bash
cd /tmp/pose-v1-inference-20261005
timeout --signal=TERM --kill-after=5s 30s ./pose_inference_check probe --allow-device-init --output probe > probe.stdout.log 2> probe.stderr.log
echo $?
cat probe/device-version.json
dmesg | tail -n 80 > probe.dmesg.log
```

`--allow-device-init`明确允许这个进程使用固定参考NPU/DMA URL；无任意地址参数。
超时仅约束进程，不保证硬件恢复；超时/异常/总线或DMA错误停止，不重复调用或复位。
正常退出只证明Open/version调用返回，需核对FPGA/icore/SDK配套及内核日志。
**将probe文件夹、stdout/stderr、dmesg和构建日志交给代理分析后再执行下一阶段。**
不能凭版本字符串相同直接宣布3.39.0与参考位流功能兼容。

## F. 三路径参考与混合推理（准备命令；E复核后继续）

### F1 ONNX CPU参考，Windows PowerShell

前提：A确认onnxruntime可用；若缺失，先讨论安装，不自动执行pip。只用于数值参考，不能作为NPU验收。

```powershell
& $posePython tools\pose-v1\inference_gate.py onnx --package $posePackage `
  --output '.local\pose-v1-inference\onnx-20261005'
if ($LASTEXITCODE -ne 0) { throw 'ONNX参考失败，停止。' }
```

使用已锁定float32输入及CPUExecutionProvider，按输出签名识别分数和姿态，保存完整二进制、帧号和环境版本。
输出数量/形状/dtype变化、NaN/Inf、执行失败均停止，不自动改ONNX算子或模型。

### F2 当前已批准：Lite Icraft optimized Host参考

采用[LITE-HOST-COMMANDS.md](LITE-HOST-COMMANDS.md)，先资源查询，再一次300秒受限Host运行，
保存完整输出/输入/Host回调与日志、回传哈希核对。没有Device::Open，不初始化NPU。
主机回传目录仍为`.local/pose-v1-inference/host-20261005`，来源须记录Lite ARM。
资源/运行/数值未通过，异常停讨论；正式部署保持PS/NPU混合路径。

### F2历史方案：Windows x64 VS开发PowerShell（SDK未识别，当前不执行）

前提：A确认CMake/MSVC及VS生成器可用，以下配置指定`-A x64`；若实际使用Ninja等生成器，先讨论对应命令。
临时PATH仅使用已批准Icraft独立依赖，不能借koala。
已只读找到既有批准依赖：`D:\FPGACompetitionProject\.local\icraft-runtime\cuda-11.8.0`，
当前worktree不含该依赖副本。新增Host启动器读取这里的manifest、逐项检查三个DLL哈希，
仅给子进程补PATH，不复制/安装依赖。缺文件或哈希不符时停止。此步骤需要现有开发终端，不要求新安装软件。

```powershell
Set-Location -LiteralPath $poseRoot
$poseHostBuild = Join-Path $poseRoot '.local\pose-v1-inference\host-build-20261005'
if (Test-Path -LiteralPath $poseHostBuild) { throw 'Host构建目录已存在，保留历史并停止。' }
cmake -S software/pose_v1 -B $poseHostBuild -A x64 `
  -DCMAKE_BUILD_TYPE=Release -DPOSE_BUILD_ICRAFT_CHECK=ON -DPOSE_ENABLE_ZG330=OFF `
  '-DCMAKE_PREFIX_PATH=C:/Icraft/CLI v3.39.0/cmake'
if ($LASTEXITCODE -ne 0) { throw 'Host配置失败，停止。' }
cmake --build $poseHostBuild --config Release --target pose_inference_check
if ($LASTEXITCODE -ne 0) { throw 'Host编译失败，停止。' }
```

若A确认使用VS多配置生成器，程序路径为`$poseHostBuild\Release\pose_inference_check.exe`；单配置生成器路径
需按实际产物复核，不猜。启动后只使用HostBackend/optimized图，不打开NPU；以下为VS生成器的运行命令：

```powershell
& .\tools\pose-v1\Run-HostReference.ps1 -BuildDirectory $poseHostBuild -Package $posePackage `
  -Output (Join-Path $poseRoot '.local\pose-v1-inference\host-20261005')
```

`--reference-tokens`令Host与ONNX使用相同固定输入，避免把Windows C++预处理差异混入模型比较；混合模式拒绝此参数。
Host只作参考，不是缺少NPU时的运行替代。禁止用ZG HardOp图交给纯Host执行。
启动器保存独立`.launcher`日志和二进制哈希，最长等待300秒；失败时抛出异常停止，不自行重试。

### F3 Lite完整混合推理（Lite SSH）

前提：E已复核、参考数值有效、没有其他AI/视频进程并发。此步包括SDK session.apply、NPU/DMA运行及六个Host算子，
保持默认ZG优化配置，不修改模型。10秒tensor等待是SDK同步超时，不是整个模型时间上限。

```bash
cd /tmp/pose-v1-inference-20261005
timeout --signal=TERM --kill-after=5s 180s ./pose_inference_check mixed --allow-device-init --graph package/models/piw24_ZG.json --raw package/models/piw24_ZG.raw --inputs package/inputs --output mixed > mixed.stdout.log 2> mixed.stderr.log
echo $?
dmesg | tail -n 80 > mixed.dmesg.log
cat mixed/results.jsonl
sha256sum mixed/* > mixed-output.sha256
```

预期三份结果、100个分数＋4200个坐标/份，全部有限；六个Host ID 188/192/437/442/582/649均有绑定和执行记录，
ZG330后端有实际回调，记录完整profile与输出。不是1173次回调硬门禁：厂商可能合并HardOp。
若SDK合并导致Host回调不可见，程序会停并保留证据，需讨论追踪方式，不能删除门禁绕过。
本程序未调用显式reset/check，但不能承诺SDK内部初始化完全不改设备状态。
阶段耗时包含诊断输出开销，三个样本不能代表5Hz/500ms或30分钟验收。

## G. 回传与数值比较（Windows PowerShell）

仅F3通过后执行；回传目录应不存在。

```powershell
$poseBoardResult = Join-Path $poseRoot '.local\pose-v1-inference\board-20261005'
if (Test-Path -LiteralPath $poseBoardResult) { throw '回传目录冲突，停止。' }
& $poseScp -r 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/mixed' $poseBoardResult
if ($LASTEXITCODE -ne 0) { throw '回传失败，停止。' }
& $poseScp 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/mixed.stdout.log' 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/mixed.stderr.log' 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/mixed.dmesg.log' 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/mixed-output.sha256' '.local\pose-v1-inference'
if ($LASTEXITCODE -ne 0) { throw '日志回传失败，停止。' }
& $posePython tools\pose-v1\inference_gate.py verify-return --directory $poseBoardResult `
  --checksums '.local\pose-v1-inference\mixed-output.sha256'
if ($LASTEXITCODE -ne 0) { throw '回传哈希不一致，停止。' }
& $posePython tools\pose-v1\inference_gate.py compare --package $posePackage `
  --left '.local\pose-v1-inference\onnx-20261005' --right '.local\pose-v1-inference\host-20261005' `
  --output '.local\pose-v1-inference\compare-onnx-host-20261005'
if ($LASTEXITCODE -ne 0) { throw 'ONNX/Host对照异常，停止。' }
& $posePython tools\pose-v1\inference_gate.py compare --package $posePackage `
  --left '.local\pose-v1-inference\host-20261005' --right $poseBoardResult `
  --output '.local\pose-v1-inference\compare-host-board-20261005'
if ($LASTEXITCODE -ne 0) { throw 'Host/板端对照异常，停止。' }
```

工具对照帧号、shape/文件长度/有限性、预处理幅度与相位门检；真实相位标量差>1e-5 rad立即停止。
保存分数/坐标max/mean/RMS/P95差、同候选关节距离、最高分候选切换及不同输入输出变化。
坐标按模型原始单位报告，不宣称物理毫米标定；同索引对照与最高分切换分开，不把候选切换自动归因于错误。
分数/坐标仅统计，`numerical_acceptance=pending_user_discussion`；接下来依据数据讨论误差门限与性能推进。
需要提交完整结果目录，而非仅截图一张骨架。传回文件应再保存SHA256，保留原板端文件用于追溯。

## 尚未开始

HDMI时序与实屏、VPU/RTSP、网络接收与调度、连续性能及30分钟验收保持未通过。
HDMI静态核对见[HDMI-STATIC-AUDIT.md](HDMI-STATIC-AUDIT.md)，不得从本指南推导任意寄存器写权限。
