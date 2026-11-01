# 混合验证人工操作命令（2026-10-06）

现已批准并应用仅加绑定快照的r2，当前使用[MIXED-BINDING-R2-COMMANDS.md](MIXED-BINDING-R2-COMMANDS.md)。
新身份包已准备，尚未编译/新阶段执行；先新BuildTag构建并核验，旧r1及下方路径不能重跑或覆盖。
旧r1失败门检不放宽，r2仅取证，不直接mixed；下面“候选待批准”为当时状态。

**当前apply-r1已失败，停止原执行命令**：目录存在源于已运行一次，session_applied后原HardOp8622缺绑定追溯导致退出1。
代理已只读取回完整结果，见[失败审查](MIXED-APPLY-FAILURE-20261006.md)。不要删除/改名后重跑apply或进入mixed。
截图省略外层括号，将set -eu用于登录shell，失败test使SSH退出；重连后无需再运行这些检查。
新[绑定快照诊断候选](MIXED-BINDING-SNAPSHOT-PLAN.md)待批准；以下原apply执行段保留历史，不作为当前重跑授权。

当前memory-check已独立验收：[SDK内存结果](MIXED-MEMORY-RESULTS-20261006.md)，memory-check.acceptance.json已生成。
Host/离线/内存不重跑；现在按下方“当前Session部署检查执行”传入验收文件，仅apply-check，完整回传再核验。
此前阶段待执行/回传文字保留为历史记录，不能直接mixed-one。

当前offline-check已独立验收：[真实RAW/PS结果](MIXED-OFFLINE-RESULTS-20261006.md)，offline-check.acceptance.json已生成。
Host/离线不重跑；现在传入离线验收文件，满足下方硬件前置条件后仅memory-check，完整回传再核验。
下面离线待运行/Host验收待传等文字为此前步骤记录。

最新Host阶段已独立验收通过，[107例/全部输出结果](MIXED-HOST-RESULTS-20261006.md)，host-check.acceptance.json已生成。
随后现场反馈Host验收已传板，失败预检目录已完整回传并审阅，仅三文件/290项校验OK，离线程序未启动。
现在直接使用下方保留目录及offline-check命令；无需再次回传旧失败目录或重跑Host。
A/B及host-check不用重跑；现在按C传入Host验收文件，并回传上次提前offline的失败预检目录。
失败目录审阅后按下方“本次提前运行offline-check的处理”保留改名，再只执行offline-check。
下面“Host待回传”属于此前截图阶段；硬件阶段仍须离线等门检通过后逐一推进。

方案已批准，代理已完成本机ONNX参考及候选源码/测试包准备；mixed-r1构建现已完成并经代理核验。
唯一缩进warning已审查，源码/程序保持，[构建结果](MIXED-BUILD-REVIEW-20261006.md)。A不用重跑，build.acceptance.json已生成。
Lite新阶段未运行；现在执行B传输，再C仅host-check。后续逐阶段由代理审阅后推进。失败立即停止，保留新目录与完整输出。
不删除/覆盖旧包，不安装板端依赖，不自动重试、reset或改BOOT/模型。

## A. Windows PowerShell：FPAI交叉编译

执行位置：Windows PowerShell，当前worktree。前置：既有FPAI容器运行、Docker路径已确认、当前SDK未改变。
测试包由代理准备，不需重生成。

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-onnx-conda\python.exe'
$posePackage = Join-Path $poseRoot '.local\pose-v1-mixed-validation\package-20261006-final'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\mixed-20261006-r1'
& .\tools\pose-v1\Build-MixedValidation.ps1 -Package $posePackage -BuildTag 'mixed-20261006-r1'
```

BuildTag决定本机与容器的新目录；已存在则停止。脚本先核对源码/15份头文件及Host/ZG库、两包3.39.0，
再用 `/usr/cmake`、GCC9.4、CMake3.24.2交叉编译独立 `pose_mixed_check`，不运行二进制。
日志同时保存完整stdout/stderr，按真实非0退出码停止。容器不需要python3。
通过标准：配置/编译/链接完成，`compiled_not_executed`报告及AArch64程序存在，并经代理核对身份。
产物在 `$poseBuild`：build.log、build-result.json、sdk-audit.json、sdk-snapshot、source及pose_mixed_check.arm64。
把这个目录告知代理即可主动读取；编译报错时不用重试，也不要直接上板。

代理核验构建的命令（文件分析，可由代理执行，成功前不进入B）：

```powershell
& $posePython tools\pose-v1\mixed_validation_gate.py review-build --package $posePackage --build $poseBuild --output tools\pose-v1\evidence\mixed-20261006-r1\build.acceptance.json
if ($LASTEXITCODE -ne 0) { throw '构建证据核验失败，停止。' }
```

## B. Lite SSH：新工作目录；Windows PowerShell：首次传输

前置：A已核验，build.acceptance.json存在。Lite登录 `root@192.168.126.49`，密码在终端交互输入。
本说明不记录密码；通过已核对的SSH主机身份连接，不关闭StrictHostKeyChecking。

Lite SSH执行（确认 `/tmp`存在，mkdir -p仅补父目录；独立子目录必须不存在）：

```sh
test -d /tmp || exit 1
mkdir -p /tmp/pose-v1-mixed-validation
test ! -e /tmp/pose-v1-mixed-validation/20261006-r1 || exit 1
mkdir /tmp/pose-v1-mixed-validation/20261006-r1
mkdir /tmp/pose-v1-mixed-validation/20261006-r1/gates
```

Windows PowerShell执行（保留A变量，同一窗口）：

```powershell
scp -o StrictHostKeyChecking=yes -r $posePackage 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/package'
if ($LASTEXITCODE -ne 0) { throw '包传输失败，停止。' }
scp -o StrictHostKeyChecking=yes (Join-Path $poseBuild 'pose_mixed_check.arm64') 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/pose_mixed_check'
if ($LASTEXITCODE -ne 0) { throw '程序传输失败，停止。' }
scp -o StrictHostKeyChecking=yes (Join-Path $poseBuild 'build-result.json') 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/build-result.json'
if ($LASTEXITCODE -ne 0) { throw '构建身份传输失败，停止。' }
scp -o StrictHostKeyChecking=yes 'tools/pose-v1/evidence/mixed-20261006-r1/build.acceptance.json' 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/gates/build.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '验收文件传输失败，停止。' }
```

传输阶段通过仅表示文件到达；runner在每阶段会校验LF文件清单、程序、SDK和上一验收文件身份。
Lite SSH执行：

```sh
cd /tmp/pose-v1-mixed-validation/20261006-r1 || exit 1
chmod u+x pose_mixed_check
ls -l package/manifest.json package/files.sha256 package/fixtures/cases.tsv pose_mixed_check build-result.json gates/build.acceptance.json
```

缺文件、哈希变化或依赖缺失则停止，不改LD_LIBRARY_PATH/SDK或覆盖包。

## C. 分阶段运行与回传

Lite SSH工作目录始终 `/tmp/pose-v1-mixed-validation/20261006-r1`。
每次只执行下面表格的一行，随后回传对应目录；代理核验并生成验收文件后，传入gates，再进入下一行。
硬件阶段开始前确认此次BOOT/JTAG未改变、没有其他AI/显示演示占用。若不确定则先提交现有日志，不启动硬件。
runner记录进程列表和完整dmesg，不自动终止其他进程；前四个硬件入口均显式传入 `--allow-device-init`。

| 阶段 | Lite SSH命令 | 前置验收文件 | 预期产物及通过标准 |
| --- | --- | --- | --- |
| Host回归 | `sh package/run-mixed-validation.sh host-check` | build | run-host-check，107例/12注册/22输出全与原参考逐位一致，无设备初始化 |
| 离线参数 | `sh package/run-mixed-validation.sh offline-check` | host-check | run-offline-check，四真实RAW参数、三PS输入、接口及注册正确，无设备初始化 |
| SDK内存 | `sh package/run-mixed-validation.sh memory-check` | offline-check | run-memory-check，设备版本/区域明确，两16KiB缓冲区六次回传逐位一致 |
| Session部署 | `sh package/run-mixed-validation.sh apply-check` | memory-check | run-apply-check，创建/apply，1173HardOp ZG、六Host绑定正确，无前向 |
| 308计算 | `sh package/run-mixed-validation.sh mixed-one` | apply-check | run-mixed-one，308全部候选有限、形状正确、六Host及ZG实际回调 |
| 三样本 | `sh package/run-mixed-validation.sh mixed-three` | mixed-one | run-mixed-three，308/309/310完整输出、同Session第四次308重复逐位检查与不同输入响应 |

依次最长300/30/30/300/180/300秒，TERM后5秒KILL。正常预期exit.txt为0且stderr空，但还需文件核验和日志审阅。
超时、OOM、总线/SDK异常、非有限值或全输出相同立即停止；保存回传，不自动重跑或复位。
预检失败可能尚无exit.txt/完整清单，也应原样回传诊断目录。

每行运行完，立即在Lite SSH执行（`echo`必须紧接runner，免得记录的是其他命令状态）：

```sh
echo $?
```

Windows PowerShell通用回传命令。以下例子为第一阶段，后续只将 `$poseStage` 改为表中准确阶段名：

```powershell
$poseStage = 'host-check'
$poseReturn = Join-Path $poseRoot ('tools\pose-v1\evidence\mixed-20261006-r1\' + $poseStage)
if (Test-Path -LiteralPath $poseReturn) { throw '回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r ('root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/run-' + $poseStage) $poseReturn
if ($LASTEXITCODE -ne 0) { throw '回传失败，停止。' }
```

此时告知代理该目录。代理先主动读原始日志和内核前后变化；无待讨论异常后执行文件核验：

```powershell
$poseAcceptance = Join-Path $poseRoot ('tools\pose-v1\evidence\mixed-20261006-r1\' + $poseStage + '.acceptance.json')
& $posePython tools\pose-v1\mixed_validation_gate.py review-stage --stage $poseStage --package $posePackage --build $poseBuild --results $poseReturn --output $poseAcceptance
if ($LASTEXITCODE -ne 0) { throw '阶段未通过，停止；保存诊断，不重跑。' }
```

三样本阶段须额外指定前一单样本回传目录，替代上面review-stage行：

```powershell
& $posePython tools\pose-v1\mixed_validation_gate.py review-stage --stage mixed-three --package $posePackage --build $poseBuild --results $poseReturn --previous-one tools\pose-v1\evidence\mixed-20261006-r1\mixed-one --output $poseAcceptance
if ($LASTEXITCODE -ne 0) { throw '三样本证据未通过，停止。' }
```

核验通过且代理确认完整日志无异常后，传入该阶段的验收文件。文件名由阶段自动生成：

```powershell
scp -o StrictHostKeyChecking=yes $poseAcceptance ('root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/gates/' + $poseStage + '.acceptance.json')
if ($LASTEXITCODE -ne 0) { throw '阶段验收文件传输失败，停止。' }
```

验收文件仅准许同一包/程序继续下一个已批准工程阶段，不表示数值/性能验收通过。

### 本次提前运行offline-check的处理（2026-10-06）

截图显示host-check runner退出0，随即offline-check因缺少gates/host-check.acceptance.json而在预检停止。
当时本机尚无新host-check完整回传/验收文件；现在完整Host回传已经核验通过，验收文件已生成。
先传入 `tools/pose-v1/evidence/mixed-20261006-r1/host-check.acceptance.json`，随后回传下面失败目录；不用再回传或重跑Host。
不要重跑host-check，不将截图上方旧CPU检查器107例记录当作新混合桥的独立证据。

本次runner在验收文件读取前已创建run-offline-check，留下包/timeout预检记录；直接重跑会被目录存在检查阻止。
先将该失败目录原样回传（Windows PowerShell，同一项目目录）：

```powershell
$poseFailedReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-r1\offline-preflight-missing-gate'
if (Test-Path -LiteralPath $poseFailedReturn) { throw '失败回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/run-offline-check' $poseFailedReturn
if ($LASTEXITCODE -ne 0) { throw '失败预检回传失败，停止。' }
```

代理现已审阅失败目录并确认未进入程序；现场反馈host-check验收已传板。以下人工在Lite SSH保留目录并启动离线阶段，
使用子shell使检查失败停止本次命令组，同时保留当前SSH窗口：

```sh
(
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-r1
test -f gates/host-check.acceptance.json
test -d run-offline-check
test ! -e run-offline-check/results
test ! -e run-offline-check/exit.txt
test ! -e run-offline-check.preflight-missing-gate-20261006
mv -- run-offline-check run-offline-check.preflight-missing-gate-20261006
sh package/run-mixed-validation.sh offline-check
)
echo $?
```

mv仅对上述明确的新验证子目录改名保留，不删除/覆盖；任一检查失败即停，若发现results/exit.txt则先讨论实际执行阶段。
离线阶段产物仍需完整回传核验，不能直接进入memory-check。

### 当前SDK内存往返执行（offline已验收）

前置：人工确认此次BOOT/JTAG未改变、没有其他AI/显示程序占用设备；不确定时暂停。
本阶段会通过已核验URL初始化AI设备，读取并核对device25122301/icore24160628，
在SDK默认设备数据区域分配两个16KiB缓冲区，三套FP32模式往返。限时30秒、TERM后5秒KILL。
区域归属或指针类别不明确即停止；不执行模型Session/前向，不直接解引用ADDR/BOTH或写参考寄存器。

Windows PowerShell传入离线验收文件（当前worktree）：

```powershell
Set-Location 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
scp -o StrictHostKeyChecking=yes 'tools/pose-v1/evidence/mixed-20261006-r1/offline-check.acceptance.json' 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/gates/offline-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '离线验收文件传输失败，停止。' }
```

Lite SSH执行，仅一次新memory-check目录；已存在则停，不改名/删除后重试：

```sh
(
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-r1
test -f gates/offline-check.acceptance.json
test ! -e run-memory-check
sh package/run-mixed-validation.sh memory-check
)
echo $?
```

Windows PowerShell完整回传，无论退出码0或非0均保留目录供代理审阅：

```powershell
$poseReturn = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject\tools\pose-v1\evidence\mixed-20261006-r1\memory-check'
if (Test-Path -LiteralPath $poseReturn) { throw '回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/run-memory-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '回传失败，停止。' }
```

预期exit0且六份设备往返输出逐位一致，仍需版本/区域/SDK身份和完整日志核验。
超时/OOM/总线/SDK异常即停，不重试/复位/改配置。不得直接apply-check；SDK内存往返通过也不证明NPU到CPU同步或推理数值。

### 当前Session部署检查执行（memory已验收）

前置：memory-check独立通过，BOOT/JTAG保持、无其他AI/显示设备访问；不确定或有变化时暂停。
本阶段会再次SDK初始化并核对版本，加载固定RAW/真实参数和三份PS输入，注册CPU适配后创建/apply ZG＋Host Session。
检查六Host计算节点的Host绑定和1173个HardOp的ZG绑定；缺少可追溯原节点或融合映射则停止。
最多300秒，TERM后5秒KILL，**不执行模型forward**。异常停止保留，不自动重试/复位/修改配置。

Windows PowerShell传验收文件：

```powershell
Set-Location 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
scp -o StrictHostKeyChecking=yes 'tools/pose-v1/evidence/mixed-20261006-r1/memory-check.acceptance.json' 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/gates/memory-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '内存验收文件传输失败，停止。' }
```

Lite SSH，只运行一次新apply-check目录；已经存在则停，不删除或改名重试：

```sh
(
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-r1
test -f gates/memory-check.acceptance.json
test ! -e run-apply-check
sh package/run-mixed-validation.sh apply-check
)
echo $?
```

Windows PowerShell，无论成功或失败都回传：

```powershell
$poseReturn = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject\tools\pose-v1\evidence\mixed-20261006-r1\apply-check'
if (Test-Path -LiteralPath $poseReturn) { throw '回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-r1/run-apply-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '回传失败，停止。' }
```

预期exit0、apply_and_bindings_completed_no_forward，bindings.jsonl覆盖原算子且backend正确，stdout/SDK/内核日志仍须审阅。
创建/apply成功不代表NPU计算、数据同步或模型数值通过；代理核验后再交付单样本命令，此时不执行mixed-one/mixed-three。

## D. 代理：ONNX与板端数值报告

前置：三样本工程证据已审阅，mixed-three.acceptance.json存在；参考目录12项哈希保持。
文件分析使用新ORT环境，本机执行，不触板端：

```powershell
& $posePython tools\pose-v1\mixed_validation_gate.py compare --reference .local\pose-v1-mixed-validation\onnx-20261006 --board tools\pose-v1\evidence\mixed-20261006-r1\mixed-three --acceptance tools\pose-v1\evidence\mixed-20261006-r1\mixed-three.acceptance.json --output tools\pose-v1\evidence\mixed-20261006-r1\onnx-board-errors.json
if ($LASTEXITCODE -ne 0) { throw '数值对照生成失败，停止。' }
```

报告全部槽位的分数/坐标最大、平均绝对误差、RMS、P95及逐位一致性；另列最高分槽位切换及最佳姿态差异。
原始坐标单位不作物理标定、MPJPE或候选身份推断；依据实测讨论容限。
即使工程通过，也不自动宣布精度通过；HDMI/RTSP、5Hz、延迟、30分钟闭环另行验证。
