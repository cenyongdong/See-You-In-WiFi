# 已批准的绑定快照r2执行命令

最新r2 apply已执行并完整取证：[结果](MIXED-BINDING-R2-APPLY-RESULTS.md)，七个ZG组完整唯一覆盖1173原节点。
原ID直接检查仍退出1，正式门检修正需另行批准；当前所有命令均不要重跑，不执行mixed。
下方步骤是历史执行记录；新入口待[MIXED-FUSION-BINDING-FIX-PLAN.md](MIXED-FUSION-BINDING-FIX-PLAN.md)批准后交付。

当前仅核心候选应用及新包准备完成，**未编译、未运行新程序**。先执行A，代理核验构建后再B/C。
程序新增Session创建后/部署后两组公共元数据快照，原严格绑定门检、CPU实现、SDK默认优化和数学运算保持。
不修改或重跑旧r1，不复用/改写旧验收文件，不执行mixed-one/mixed-three。

## A. Windows PowerShell交叉编译

前置：既有FPAI容器运行，SDK仍3.39.0，当前worktree源码与新包一致。工作目录为本worktree。

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-onnx-conda\python.exe'
$posePackage = Join-Path $poseRoot '.local\pose-v1-mixed-validation\package-20261006-binding-r2'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\mixed-20261006-binding-r2'
& .\tools\pose-v1\Build-MixedValidation.ps1 -Package $posePackage -BuildTag 'mixed-20261006-binding-r2'
```

新BuildTag对应本机及容器的新目录；已有目录或非0退出即停，不覆盖/重复编译。
脚本核对10份构建文件、15ARM头文件/两后端库/版本，用GCC9.4/CMake3.24.2与/usr/cmake构建pose_mixed_check。
不运行二进制或初始化设备；保留完整stderr，仍可能出现原有版本JSON缩进warning，由代理审阅。
预期产物pose_mixed_check.arm64/build.log/build-result.json/sdk-audit.json及源码/SDK副本；通知代理目录即可主动读取。

代理构建核验（仅文件分析）：

```powershell
& $posePython tools\pose-v1\mixed_validation_gate.py review-build --package $posePackage --build $poseBuild --output tools\pose-v1\evidence\mixed-20261006-binding-r2\build.acceptance.json
if ($LASTEXITCODE -ne 0) { throw '新构建核验未通过，停止。' }
```

## B. 构建核验后创建新板端目录并传输

执行位置：Lite SSH。先关闭登录shell的errexit/nounset；创建命令在独立sh进程中非0即停，避免遗漏括号导致SSH退出。

```sh
set +e
set +u
sh -c 'set -eu; test -d /tmp; mkdir -p /tmp/pose-v1-mixed-validation; test ! -e /tmp/pose-v1-mixed-validation/20261006-binding-r2; mkdir /tmp/pose-v1-mixed-validation/20261006-binding-r2; mkdir /tmp/pose-v1-mixed-validation/20261006-binding-r2/gates'
echo $?
```

仅对子目录不存在时创建；非0即停。旧20261006-r1及其run-apply-check不改名、不删除。
Windows PowerShell（重新设定r2变量，避免沿用旧r1的poseBuild或posePackage）：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePackage = Join-Path $poseRoot '.local\pose-v1-mixed-validation\package-20261006-binding-r2'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\mixed-20261006-binding-r2'
scp -o StrictHostKeyChecking=yes -r $posePackage 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/package'
if ($LASTEXITCODE -ne 0) { throw '包传输失败，停止。' }
scp -o StrictHostKeyChecking=yes (Join-Path $poseBuild 'pose_mixed_check.arm64') 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/pose_mixed_check'
if ($LASTEXITCODE -ne 0) { throw '程序传输失败，停止。' }
scp -o StrictHostKeyChecking=yes (Join-Path $poseBuild 'build-result.json') 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/build-result.json'
if ($LASTEXITCODE -ne 0) { throw '构建身份传输失败，停止。' }
scp -o StrictHostKeyChecking=yes 'tools/pose-v1/evidence/mixed-20261006-binding-r2/build.acceptance.json' 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/gates/build.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '构建验收传输失败，停止。' }
```

Lite SSH：

```sh
chmod u+x /tmp/pose-v1-mixed-validation/20261006-binding-r2/pose_mixed_check
echo $?
```

仅修改新程序执行位。runner每次重新核验包、程序、SDK和对应前阶段验收；不拷贝r1验收来凑门禁。

## C. 新身份逐阶段验证

Lite SSH重连后可先执行以下两条，它们仅取消当前登录shell的errexit/nounset；独立runner内部的失败停止仍保持。

```sh
set +e
set +u
```

每次只执行表中一条命令，再紧接echo $?；不要重复执行已存在的run目录。
前阶段结果经代理审阅并传入新验收文件后再下一行。硬件阶段前确认BOOT/JTAG未变且无其他AI/显示设备访问。

| 阶段 | Lite SSH命令 | 限时与通过标准 |
| --- | --- | --- |
| Host | `sh /tmp/pose-v1-mixed-validation/20261006-binding-r2/package/run-mixed-validation.sh host-check` | 300秒，107例/12注册/22输出59,600FP32与原参考逐位一致；无设备初始化 |
| 离线 | `sh /tmp/pose-v1-mixed-validation/20261006-binding-r2/package/run-mixed-validation.sh offline-check` | 30秒，真实RAW参数/PS输入/注册保持；无设备初始化 |
| SDK内存 | `sh /tmp/pose-v1-mixed-validation/20261006-binding-r2/package/run-mixed-validation.sh memory-check` | 30秒，设备版本/区域明确，六份往返模式一致 |
| 绑定取证 | `sh /tmp/pose-v1-mixed-validation/20261006-binding-r2/package/run-mixed-validation.sh apply-check` | 300秒，收集两组快照；原门检可能仍退出1，不做forward |

runner会通过--allow-device-init显式启用后两阶段硬件；不调用autoMerge第二次，不使用额外优化选项。
CPU/离线/内存成功要求exit0且完整证据核验通过；任何非0先回传，不自动重试。
**apply取证的非0也要回传**，不能靠exit0/元数据收集宣布融合映射或部署通过。新完整映射核验办法需另行审阅。

Windows PowerShell每阶段回传例子（首阶段）：

```powershell
$poseStage = 'host-check'
$poseReturn = Join-Path $poseRoot ('tools\pose-v1\evidence\mixed-20261006-binding-r2\' + $poseStage)
if (Test-Path -LiteralPath $poseReturn) { throw '新回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r ('root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/run-' + $poseStage) $poseReturn
if ($LASTEXITCODE -ne 0) { throw '回传失败，停止。' }
```

后续只将poseStage设为offline-check/memory-check/apply-check，回传后通知代理。
前三阶段由代理读取全日志，再按原核验器生成对应验收文件：

```powershell
$poseAcceptance = Join-Path $poseRoot ('tools\pose-v1\evidence\mixed-20261006-binding-r2\' + $poseStage + '.acceptance.json')
& $posePython tools\pose-v1\mixed_validation_gate.py review-stage --stage $poseStage --package $posePackage --build $poseBuild --results $poseReturn --output $poseAcceptance
if ($LASTEXITCODE -ne 0) { throw '阶段证据未通过，停止。' }
```

该review-stage仅用于host-check/offline-check/memory-check。apply取证仍保留原失败门检，代理先审阅快照，不直接生成apply验收或启动mixed。
前三阶段核验后传入新验收文件：

```powershell
scp -o StrictHostKeyChecking=yes $poseAcceptance ('root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/gates/' + $poseStage + '.acceptance.json')
if ($LASTEXITCODE -ne 0) { throw '阶段验收传输失败，停止。' }
```

## D. 绑定取证产物与停止范围

创建和apply返回后分别记录after-create/after-apply五文件：all-bindings.jsonl、views.jsonl、backends.jsonl、
zg-hardop-map.jsonl、zg-sync-map.jsonl。包含全部绑定键/SDK类型/视图成员/merge_from/net_hardop ID与同步索引。
如果apply前异常，保留可取得的快照及failure/stages日志；不要重复硬件调用补日志。
无论结果如何，保留stderr、exit、完整dmesg/SDK/二进制、真实参数及输入。超时/OOM/总线/SDK异常均停止。
原1173HardOp和六Host门检保持，实际融合追溯、SDK运行类型识别、NPU前向及精度仍未验证；不改SDK、模型、BOOT、CPU Matmul或缓存策略。

## E. 本次Host验收后继续离线检查

前置：r2 Host结果与失败预检已完整回传并审阅，程序身份匹配；不使用旧r1验收文件。
Windows PowerShell传入新验收文件：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-binding-r2\host-check.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/gates/host-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '验收文件传输失败，停止。' }
```

Lite SSH：检查失败目录仅含已审阅的三份预检文件，在同一固定目录改名保留，然后仅执行离线阶段。
这次离线程序尚未运行；下列命令不覆盖任何旧结果，独立sh非0即停止，登录窗口保持。

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-binding-r2
test -f gates/host-check.acceptance.json
test -d run-offline-check
test -f run-offline-check/package-check.log
test -f run-offline-check/timeout-path.txt
test -f run-offline-check/timeout-version.txt
test "$(find run-offline-check -mindepth 1 -maxdepth 1 | wc -l)" -eq 3
test ! -e run-offline-check/results
test ! -e run-offline-check/exit.txt
test ! -e run-offline-check.preflight-missing-gate-20261006
mv -- run-offline-check run-offline-check.preflight-missing-gate-20261006
sh package/run-mixed-validation.sh offline-check
'
echo $?
```

预期退出0，30秒内保存run-offline-check完整日志、真实RAW参数和三份PS输入；不初始化设备。
任何非0即停止并回传，禁止重复执行本命令组或删除/覆盖失败目录，不进入memory/apply。
Windows PowerShell回传这次正式离线结果：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-binding-r2\offline-check'
if (Test-Path -LiteralPath $poseReturn) { throw '回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/run-offline-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '离线结果回传失败，停止。' }
```

本机原失败目录已保存在evidence/mixed-20261006-binding-r2/offline-preflight-missing-gate，不能改其内容。
回传后通知代理核验；此步骤不生成offline验收文件，也不证明完整混合推理通过。

## F. 离线验收后SDK内存往返

前置：r2离线已由代理完整核验、生成新门禁；确认此前25122301核验后未更换BOOT/通过JTAG更改位流，
没有其他AI、HDMI或视频应用访问设备。若不能确认，先停止并说明，不结束其他进程或尝试设备复位。
本阶段将Device::Open初始化设备，只使用SDK分配的数据区域，不直接写参考寄存器；两缓冲区各16KiB，
三组固定FP32模式共六份回读要求逐位一致。外部限时30秒；区域、设备版本或存储不符即停止。

Windows PowerShell（当前worktree）传入新r2离线验收文件：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-binding-r2\offline-check.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/gates/offline-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '离线验收传输失败，停止。' }
```

Lite SSH执行一次；登录shell不启用errexit，独立子进程保持失败停止，禁止使用旧r1程序/门禁：

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-binding-r2
test -f gates/offline-check.acceptance.json
test ! -e run-memory-check
sh package/run-mixed-validation.sh memory-check
'
echo $?
```

预期退出0，run-memory-check含SDK区域/设备版本、六份内存回读、完整日志和前后内核记录。
非0、超时、OOM、总线/SDK异常立即停止，保留结果回传，不重试/改缓存策略/复位；不执行apply或mixed。
即使退出0，也只证明SDK CPU↔设备内存复制，不能证明NPU生产者同步或模型计算。

Windows PowerShell完整回传：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-binding-r2\memory-check'
if (Test-Path -LiteralPath $poseReturn) { throw '回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/run-memory-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '内存结果回传失败，停止。' }
```

回传后通知代理核验。新memory验收未生成前不进入Session apply取证。

## G. 内存验收后一次绑定快照取证

前置：r2内存已完整核验通过；BOOT/JTAG未改变，设备无其他AI/显示访问。
本阶段按已批准方案初始化设备、加载真实RAW并创建/apply混合Session，外部限时300秒，不执行模型forward。
原1173 HardOp＋六Host严格门检保持，可能仍在原8622处退出1；这次重点获取真实SDK绑定/融合快照。
旧r1目录不重跑/改名/删除，不使用其验收文件；任何新异常保留停止，不自动重试。

Windows PowerShell传入新r2内存验收文件：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-binding-r2\memory-check.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/gates/memory-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '内存验收传输失败，停止。' }
```

Lite SSH仅执行一次；独立子进程控制失败停止，不在登录shell启用set -eu：

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-binding-r2
test -f gates/memory-check.acceptance.json
test ! -e run-apply-check
sh package/run-mixed-validation.sh apply-check
'
echo $?
```

无论退出0或1、超时或SDK异常，都保留run-apply-check并完整回传；不重新运行以补日志，不进入mixed。
预期在results保存after-create及after-apply各五份JSONL（all-bindings、views、backends、zg-hardop-map、zg-sync-map），
以及真实参数/输入、stages、失败位置、设备身份和完整前后内核日志。中途异常时只保留实际取得的文件。
完整快照收集不等于1173原节点映射验收；不得手工生成apply-check.acceptance.json绕过门禁。

Windows PowerShell回传全部结果（非0仍需回传）：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-binding-r2\apply-check'
if (Test-Path -LiteralPath $poseReturn) { throw '取证回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-binding-r2/run-apply-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '取证回传失败，停止。' }
```

回传后由代理分析实际merge_from/运行视图及绑定粒度，再讨论正式追溯校验方法；当前不放宽计数、改变SDK默认优化或运行样本。
