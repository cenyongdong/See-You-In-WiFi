# CPU候选验证：人工操作命令（2026-10-06修正）

批准范围见[CPU-ADAPTER.md](CPU-ADAPTER.md)。代理本轮未执行下面的准备、编译或测试。
先执行A、B并回传编译日志；核对通过后再按C运行已批准的CPU测试。任一步失败立即停止，
保留目录和日志，不自行重试、删目录、更换SDK/链接方式/模型或进入mixed。

**A/B/C/D已人工完成并经完整复核，独立CPU候选门检通过。** 107例、12条注册记录、
22份实际输出/59,600个FP32值逐位一致，包/回传/SDK/程序身份匹配。
最终[结果](CPU-ADAPTER-RESULTS-20261006.md)及独立核验（历史附件，当前仓库未附：`evidence/cpu-adapter-independent-review-20261006.json`）。
以下命令保留为执行历史，不重复准备/编译/板端运行或覆盖已存在的证据；正式推理器接入及完整mixed另讨论。
r2完成配置/编译/链接，
282项包哈希、5份源码及ARM二进制身份匹配，新旧281项非manifest文件相同；
SDK六头文件、Host库和两包3.39.0匹配。见evidence构建复核（历史附件，当前仓库未附：`evidence/cpu-adapter-r2-build-review-20261006.json`）。
当前包`.local/pose-v1-cpu-adapter/package/20261006-r2`及构建`cpu-adapter-20261006-r2`；
程序SHA256为`8cf2017cedf6a97f98ce485d979239b659291f3c91d3a3d550382c1c94588622`。
不要重复A/B或改旧包manifest。两次失败记录保留；仅交叉编译验收，不代表板端加载/算子数值通过。

## A．Windows PowerShell：为修正源码生成新身份包

前置：当前worktree、独立Conda Python/NumPy 2.2.5和原三样本包仍存在。
在Windows PowerShell执行，后续B/D沿用同一窗口变量；这里无需Visual Studio或ONNX Runtime。
原包`package/20261005`保持，新输出目录必须不存在。此步骤重新记录源码身份，仍使用原固定合成输入/参考逻辑。

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-conda\python.exe'
$poseGraph = Join-Path $poseRoot '.local\pose-v1-inference\package-20261005\models\piw24_ZG.json'
$posePackage = Join-Path $poseRoot '.local\pose-v1-cpu-adapter\package\20261006-r2'
& $posePython tools\pose-v1\cpu_adapter_gate.py prepare --graph $poseGraph --sdk 'C:\Icraft\CLI v3.39.0' --output $posePackage
if ($LASTEXITCODE -ne 0) { throw '准备失败，停止并保存报错，不安装依赖或覆盖目录。' }
```

目的：核对固定模型和原头文件身份，读取真实六个算子规格，用NumPy生成合成输入/参考。
`--output`必须不存在；`manifest.json`记录源码、头文件、模型、规格和用例身份，
`files.sha256`是LF清单。预期打印`Prepared 107 CPU-only cases; no tests executed`。
这一步不运行SDK算子、不连接Docker/板子。数量不同、哈希/版本报错或任何异常均停止。

## B．Windows PowerShell：使用修正版进行一次新目录构建

前置：A成功生成新的107用例身份包；FPAI容器正在运行，SDK位于`/usr/cmake`。
在Windows PowerShell执行以下完整命令，重新设置变量，不依赖此前窗口状态：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-conda\python.exe'
$posePackage = Join-Path $poseRoot '.local\pose-v1-cpu-adapter\package\20261006-r2'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\cpu-adapter-20261006-r2'
& .\tools\pose-v1\Build-CpuAdapter.ps1 -Package $posePackage -BuildTag 'cpu-adapter-20261006-r2'
```

脚本从**当前worktree**复制三份候选源码及独立CMake，不使用容器挂载中的旧项目。
固定GCC aarch64-linux-gnu-g++、CMake及ARM Icraft/CustomOp 3.39.0；对比原Host库和六份规范化头文件。
容器新目录`/tmp/pose-v1-cpu-adapter-20261006-r2`，本机输出：
`.local\pose-v1-build\cpu-adapter-20261006-r2`，两者必须此前不存在；旧失败目录不删除或覆盖。
版本由容器dpkg-query查询；六份ARM头文件/Host库经Docker cp -L导出到`sdk-snapshot`，
PowerShell/.NET核对原身份并生成sdk-audit.json，无需安装容器Python。

`--parallel 2`限定编译并发，`-ffp-contract=off`禁用浮点融合；只链接官方HostBackend依赖。
预期目标`pose_cpu_adapter_check`完成、file显示ARM aarch64、readelf没有ZG后端直接依赖，
生成`pose_cpu_adapter_check.arm64`、`sdk-audit.json`、`build-result.json`和`build.log`。
另保留`sdk-snapshot`，build-result记录实际修正版脚本哈希；旧包manifest不回写，新包记录本次修正身份。
日志仅在原生命令捕获时临时使用Continue并转换stderr为文本，finally恢复Stop，仍以非0退出停止。
遇到警告应核对日志，不能把stderr出现或构建进度百分比单独作为通过/失败判断。
脚本不执行二进制。请先回传`build.log`、`sdk-audit.json`及`build-result.json`供代理核对。
任何编译/版本/头文件差异先讨论，不自动修正。

## C．核对构建后：传输与Lite一次CPU测试

前置：B产物已核对通过；Lite SSH仍是`root@192.168.126.49`，原SDK/库未改。
这是既有批准范围内的独立CPU测试，不是完整模型推理或NPU测试，不需重跑已有probe/模型。
在MobaXterm的**Lite SSH终端**先核对父目录：

```sh
ls -ld /tmp /tmp/pose-v1-inference-20261005
```

若`/tmp`存在，而第二项报No such file or directory，表示历史父目录缺失。
原单条mkdir要求父目录已存在；现在补齐同一批准路径的父目录，再创建独立测试子目录：

```sh
mkdir -p /tmp/pose-v1-inference-20261005
mkdir /tmp/pose-v1-inference-20261005/cpu-adapter-20261005
```

`-p`仅用于父目录：父目录已有时保留，缺失时创建；测试子目录仍使用不带-p的mkdir，
防止将已有测试目录误当作新目录。通过标准：两条mkdir成功、测试子目录此前不存在。
若`/tmp`也不存在、父路径是文件、权限不足或子目录已存在，停止并报告，不删除或覆盖。
不要在Windows PowerShell或FPAI容器里运行这两条命令；应在Lite的MobaXterm SSH终端执行。
然后在A/B同一**Windows PowerShell**执行传输，SSH口令仅在交互提示输入：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-conda\python.exe'
$posePackage = Join-Path $poseRoot '.local\pose-v1-cpu-adapter\package\20261006-r2'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\cpu-adapter-20261006-r2'
scp -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -r $posePackage root@192.168.126.49:/tmp/pose-v1-inference-20261005/cpu-adapter-20261005/package
if ($LASTEXITCODE -ne 0) { throw '测试包传输失败，停止。' }
scp -o StrictHostKeyChecking=yes -o UpdateHostKeys=no (Join-Path $poseBuild 'pose_cpu_adapter_check.arm64') root@192.168.126.49:/tmp/pose-v1-inference-20261005/cpu-adapter-20261005/pose_cpu_adapter_check
if ($LASTEXITCODE -ne 0) { throw '程序传输失败，停止。' }
```

若本机SCP认证或严格主机密钥检查失败，报告原因；不关闭主机密钥检查。
也可在已认证的MobaXterm SFTP面板将包目录整体传到上面`package`，将二进制传到指定文件名；
两种方式只选一种，不重复覆盖。

回到**Lite SSH终端**：

```sh
cd /tmp/pose-v1-inference-20261005/cpu-adapter-20261005
ls -ld package/manifest.json package/files.sha256 package/fixtures/cases.tsv pose_cpu_adapter_check
chmod u+x pose_cpu_adapter_check
sh package/run-cpu-adapter.sh
echo $?
```

`chmod`只增加这个新候选程序的人工操作权限。
脚本先核对包清单、Icraft/CustomOp 3.39.0、头文件、Host库、ldd和timeout。
仅以一次`timeout --signal=TERM --kill-after=5s 300s`执行CPU测试，300秒后TERM、再5秒KILL；
不会读取模型RAW、调用Device::Open/Session或运行NPU/DMA/HDMI。

输出新目录`cpu-run-20261005`，预期退出0、run.stderr.log空、results/summary.json包含107个通过用例，
其中device_opened/full_model_executed/mixed_verified全为false。
实际程序只执行Host张量上的合成数据前向，不能称为真实CSI推理通过。
Gather原后端或候选前向出现异常、位比较不一致、退出非0（包括124超时或137强制退出）、崩溃或任何前检失败均停止；
不要重跑，也不要修改线程、库、内存/Swap或输出缓冲区策略来绕过。

执行后可读取本次日志（不再运行程序）：

```sh
cat cpu-run-20261005/exit.txt
cat cpu-run-20261005/run.stdout.log
cat cpu-run-20261005/run.stderr.log
cat cpu-run-20261005/results/summary.json
```

若前检失败，上述部分文件可能尚未生成；提交终端报错及已有目录内容，不为补齐文件重跑。
退出0也需完整回传D中的目录，核对注册前后记录、107用例及实际22份输出，不能只凭终端摘要宣布通过。

## D．Windows PowerShell：完整回传与独立数值复核

即使C失败，也请完整回传`cpu-run-20261005`；先审查stderr和失败阶段，不执行下面的数值复核。
本步骤已人工执行完成。此前截图显示运行退出0、107例完成、stderr空；以下**Windows PowerShell**命令保留，
重新设置变量，无需沿用之前窗口状态：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-conda\python.exe'
$posePackage = Join-Path $poseRoot '.local\pose-v1-cpu-adapter\package\20261006-r2'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\cpu-adapter-20261006-r2'
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\cpu-adapter-20261005-return'
if (Test-Path -LiteralPath $poseReturn) { throw '回传目录已存在，停止，保留旧证据。' }
scp -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -r root@192.168.126.49:/tmp/pose-v1-inference-20261005/cpu-adapter-20261005/cpu-run-20261005 $poseReturn
if ($LASTEXITCODE -ne 0) { throw '回传失败，停止。' }
& $posePython tools\pose-v1\cpu_adapter_gate.py review --package $posePackage --build $poseBuild --results $poseReturn --output tools\pose-v1\evidence\cpu-adapter-20261005-review.json
if ($LASTEXITCODE -ne 0) { throw '证据/数值核验失败，停止并报告，不重跑。' }
```

复核会检查包/回传逐文件哈希、编译源码与程序身份、板端与构建SDK、注册前后记录、107个用例及
22份正常数值产物的逐位一致性/有限性。预期生成`cpu_candidate_gate_passed`的review.json，仍标记mixed未验收。
提交该JSON及日志后，代理核验并更新项目记录；实际PS/NPU交接和完整推理另行讨论，不直接执行mixed。
