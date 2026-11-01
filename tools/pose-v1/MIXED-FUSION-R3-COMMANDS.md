# 已批准的融合追溯修正r3命令

代理已应用批准修正、保存r2源码/核验器备份、生成新包并通过本机回放与异常拒绝检查。
最新r3三样本已执行并失败停止：[失败结果](MIXED-FUSION-R3-THREE-FAILURE.md)，三个不同输入的全部输出却与308首帧相同。
**A至H全部不要重跑，不生成三样本门禁或正常精度验收。** 原包/程序/失败结果保持。
当前仅待讨论[MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md](MIXED-INPUT-FRESHNESS-DIAGNOSTIC-PLAN.md)，不修改SDK、模型、cache或ready。
下方前置阶段待核验是此前执行说明，旧r1/r2失败证据保持。
范围见[MIXED-FUSION-BINDING-FIX-PLAN.md](MIXED-FUSION-BINDING-FIX-PLAN.md)，
交付见[MIXED-FUSION-R3-DELIVERY.md](MIXED-FUSION-R3-DELIVERY.md)。

## A. Windows PowerShell交叉编译

执行位置：本机Windows PowerShell，工作目录为当前worktree；前置为既有FPAI容器运行、ARM SDK保持3.39.0。
新包已准备，不再次运行prepare，不覆盖r1/r2目录。新BuildTag在本机和容器均创建独立目录，已有则停止。

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePackage = Join-Path $poseRoot '.local\pose-v1-mixed-validation\package-20261006-fusion-r3'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\mixed-20261006-fusion-r3'
& .\tools\pose-v1\Build-MixedValidation.ps1 -Package $posePackage -BuildTag 'mixed-20261006-fusion-r3'
```

目的：FPAI GCC9.4/CMake3.24.2交叉编译独立pose_mixed_check；11份构建文件含新静态融合基线头，
SDK目录/usr/cmake，15ARM头文件/Host及ZG库/版本核验不依赖容器Python。
本命令不运行候选程序、创建Session或访问设备。原版本输出缩进warning若仍出现保留完整日志，由代理审阅。
任何throw、非0构建退出或SDK/源码身份不匹配都保留停止，不重试/改编译选项/改库。

预期产物位于$poseBuild：pose_mixed_check.arm64、build.log、build-result.json、sdk-audit.json和source/sdk-snapshot。
源码快照和二进制须核验后才生成r3的build.acceptance.json。完成后通知代理即可主动读取本机文件，不必截图代替日志。

## 后续顺序（按对应已验收阶段推进）

新板端路径固定为/tmp/pose-v1-mixed-validation/20261006-fusion-r3，当前人工按下方B创建/传输。
构建核验后代理提供新目录创建/传输和仅Host命令，每阶段完整回传且新身份验收文件传入后才继续：

| 阶段 | 限时 | 范围与通过要求 |
| --- | ---: | --- |
| Host | 300秒 | 107例/12注册/22输出，计算和数据桥与原参考逐位一致，无设备初始化 |
| 离线 | 30秒 | 真实RAW四参数、三PS输入、注册及接口正确，无设备初始化 |
| SDK内存 | 30秒 | 两16KiB数据缓冲区/六回读逐位一致，设备/区域身份匹配 |
| 正式apply | 300秒 | 不forward；创建1181原绑定、部署七组完整唯一覆盖1173HardOp/八Host，新增追溯记录及两组快照匹配基线 |

已有r1/r2包、门禁、目录及失败证据保持，不改名或复用旧验收SHA。
硬件前BOOT/JTAG保持25122301基线且无其他AI/显示访问；显式--allow-device-init由既有runner控制。
超时/OOM/总线/SDK异常、组成员/同步/后端变化即保留停止，不自动重试/复位/改SDK优化。
正式apply成功仍须代理独立核验，当前不执行mixed-one或mixed-three，不宣布NPU/完整数值通过。

## B. 新r3目录创建与传输

执行位置：Lite SSH。取消登录shell的errexit/nounset；独立sh任一检查失败即停止本次创建，SSH窗口保持。
仅在新子目录不存在时创建；返回0后再Windows传输，非0停止说明情况，不删除或覆盖已有目录。

```sh
set +e
set +u
sh -c 'set -eu; test -d /tmp; mkdir -p /tmp/pose-v1-mixed-validation; test ! -e /tmp/pose-v1-mixed-validation/20261006-fusion-r3; mkdir /tmp/pose-v1-mixed-validation/20261006-fusion-r3; mkdir /tmp/pose-v1-mixed-validation/20261006-fusion-r3/gates'
echo $?
```

Windows PowerShell重新指定全部r3路径，避免沿用旧r2变量：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePackage = Join-Path $poseRoot '.local\pose-v1-mixed-validation\package-20261006-fusion-r3'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\mixed-20261006-fusion-r3'
scp -o StrictHostKeyChecking=yes -r $posePackage 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/package'
if ($LASTEXITCODE -ne 0) { throw '新包传输失败，停止。' }
scp -o StrictHostKeyChecking=yes (Join-Path $poseBuild 'pose_mixed_check.arm64') 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/pose_mixed_check'
if ($LASTEXITCODE -ne 0) { throw '新程序传输失败，停止。' }
scp -o StrictHostKeyChecking=yes (Join-Path $poseBuild 'build-result.json') 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/build-result.json'
if ($LASTEXITCODE -ne 0) { throw '构建身份传输失败，停止。' }
scp -o StrictHostKeyChecking=yes 'tools/pose-v1/evidence/mixed-20261006-fusion-r3/build.acceptance.json' 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/gates/build.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '构建验收传输失败，停止。' }
```

四项传输全部完成后，在Lite SSH执行C；不拷贝或改写旧r2门禁凑身份。

## C. 仅新Host回归并回传

执行位置：Lite SSH。新程序增加执行位，runner重核验291项包、程序/SDK及新构建门禁，然后运行107例Host回归。
限时300秒；无Device::Open、完整Session或NPU操作。任何非0仍完整回传，不重跑或进入后续阶段。

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-fusion-r3
test -f gates/build.acceptance.json
test ! -e run-host-check
chmod u+x pose_mixed_check
sh package/run-mixed-validation.sh host-check
'
echo $?
```

预期退出0，run-host-check保存107例（18正常/89拒绝）、12注册、22输出/59,600FP32、桥记录及完整SDK/内核日志。
退出0是程序内检结果，需代理独立核验后才能生成r3 host-check.acceptance.json；当前不运行offline-check。
Windows PowerShell将整个新结果目录回传：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\host-check'
if (Test-Path -LiteralPath $poseReturn) { throw 'Host回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/run-host-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw 'Host回传失败，停止。' }
```

完成后通知代理读取；不要自行进入offline/memory/apply或使用已有r2 Host验收文件。

## D. Host验收后仅离线门检

前置：r3 Host已由代理完整核验、生成新门禁；不传r2的Host验收文件。
Windows PowerShell（当前worktree）传入新r3验收：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\host-check.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/gates/host-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw 'Host验收传输失败，停止。' }
```

Lite SSH仅一次；独立sh检查新离线目录不存在，任一失败停止命令组但保持登录窗口。
30秒内检查真实RAW的四参数、三CSI的PS输入、注册及接口，不Device::Open/完整Session/forward。

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-fusion-r3
test -f gates/host-check.acceptance.json
test ! -e run-offline-check
sh package/run-mixed-validation.sh offline-check
'
echo $?
```

预期退出0，run-offline-check保存真实TopK K、ScatterND索引、三PS输入和完整身份/内核日志。
非0、超时或异常都保留并回传，不重跑/覆盖，也不改模型、SDK或直接进入memory/apply。
Windows PowerShell完整回传：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\offline-check'
if (Test-Path -LiteralPath $poseReturn) { throw '离线回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/run-offline-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '离线回传失败，停止。' }
```

回传后通知代理核验。退出0不代替文件核验；新offline验收未生成并传板前不执行memory-check。

## E. 离线验收后仅SDK内存往返

前置：r3离线已独立核验，确认此前25122301核验后BOOT/JTAG未改变，且无其他AI/HDMI/视频应用访问设备。
不能确认则停止说明，不自行终止其他进程、复位设备或访问任意寄存器。
本阶段显式初始化设备，SDK分配两个16KiB数据缓冲区，三组固定FP32模式共六份回读要求逐位一致。
外部限时30秒，区域/版本/存储不符即停；只SDK CPU↔设备复制，不执行完整Session或模型forward。

Windows PowerShell传入新r3离线验收文件：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\offline-check.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/gates/offline-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '离线验收传输失败，停止。' }
```

Lite SSH执行一次，登录窗口不启用errexit，独立sh失败即停止本次命令：

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-fusion-r3
test -f gates/offline-check.acceptance.json
test ! -e run-memory-check
sh package/run-mixed-validation.sh memory-check
'
echo $?
```

预期退出0，run-memory-check包含设备版本、SDK区域、六份回读及完整日志。
任一非0、超时/OOM/总线/SDK异常保存停止并回传，不重试/改缓存/复位，也不执行apply或mixed。
退出0并不证明NPU生产者同步，需独立核验完整回读后才生成新memory门禁。

Windows PowerShell回传全部结果：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\memory-check'
if (Test-Path -LiteralPath $poseReturn) { throw '内存回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/run-memory-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '内存结果回传失败，停止。' }
```

回传后通知代理核验。新memory验收通过并传板后，再提供一次正式apply门检命令；当前不运行前向。

## F. 内存验收后一次正式apply门检

前置：r3内存已独立核验、生成新门禁，BOOT/JTAG保持25122301基线且无其他AI/显示竞争访问。
本阶段会初始化设备、加载真实RAW、创建并apply混合Session，外部限时300秒，**不forward**。
创建时检查1181原节点直接绑定；部署后七个实际ZG组须完整唯一覆盖1173原HardOp，并匹配固定组成员/同步基线。
八Host（六计算节点和Input/Output）保持；group count不能代替原HardOp覆盖数。
不禁用SDK融合、不再次autoMerge、不复用r2门禁或重跑旧失败目录。

Windows PowerShell传入新r3内存验收文件：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\memory-check.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/gates/memory-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '内存验收传输失败，停止。' }
```

Lite SSH仅一次；独立sh中的检查非0即停止，登录窗口保持：

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-fusion-r3
test -f gates/memory-check.acceptance.json
test ! -e run-apply-check
sh package/run-mixed-validation.sh apply-check
'
echo $?
```

预期退出0，阶段含original_bindings_validated_before_apply、original_to_effective_bindings_validated及apply_and_bindings_completed_no_forward。
results应保存两组十份完整快照、1181条bindings.jsonl、binding-summary.json、真实参数/PS输入及完整设备/内核日志。
未到成功阶段时只保留实际取得的证据；任何非0、超时/OOM/总线/SDK异常或基线变化立即停止，不自动重试/复位/改SDK。
无论成功或失败都完整回传，不因退出0直接进入mixed或手工生成apply验收文件。

Windows PowerShell回传：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\apply-check'
if (Test-Path -LiteralPath $poseReturn) { throw 'apply回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/run-apply-check' $poseReturn
if ($LASTEXITCODE -ne 0) { throw 'apply结果回传失败，停止。' }
```

代理独立核验完整原到有效组映射、源/SDK/设备及无forward范围后再生成新apply门禁。
本阶段通过仅证明Session部署及绑定门检，不代表NPU计算、PS/NPU同步、完整模型数值或连续性能通过。

## G. apply验收后仅308单样本计算

前置：r3正式apply已独立核验、生成新门禁；BOOT/JTAG保持、无其他AI/HDMI/视频应用竞争访问设备。
本阶段首次实际调用混合Session.forward，初始化设备并重新加载/apply同一图；仅计算308/frame6一次。
三份输入/真实参数仍作固定前检，但309/310不执行forward。外部限时180秒，runner显式--allow-device-init及--cases one。
不改SDK默认优化、原注册、数学运算、模型或缓冲区策略；不重跑已验收apply、旧r1/r2或复用旧门禁。

Windows PowerShell传入新r3 apply验收文件：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\apply-check.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/gates/apply-check.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw 'apply验收传输失败，停止。' }
```

Lite SSH执行一次，独立sh非0即停止本次命令，登录窗口保持：

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-fusion-r3
test -f gates/apply-check.acceptance.json
test ! -e run-mixed-one
sh package/run-mixed-validation.sh mixed-one
'
echo $?
```

预期退出0、阶段mixed_completed_not_numerically_accepted，记录六Host及ZG实际回调、桥输入/输出存储和SDK搬运。
保存S11_01_308.scores.f32（100值/400字节）及poses.f32（4200值/16,800字节）、完整候选和阶段/耗时/设备/内核日志。
输出应为分数[1,100]和姿态[1,100,14,3]且全有限；退出0仍须独立核对实际执行和完整输出，不能自动宣布ONNX数值验收。
超时/OOM/总线/SDK异常、身份变化、非有限输出、布局/存储不明或缺实际Host/ZG执行即保留停止并回传。
不自动重试/复位/加Swap/改模型/改缓存或转CPU；当前不执行mixed-three。

Windows PowerShell回传全部结果（失败仍回传）：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\mixed-one'
if (Test-Path -LiteralPath $poseReturn) { throw '单样本回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/run-mixed-one' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '单样本回传失败，停止。' }
```

完整回传后代理主动读取，核验帧号/输入、七组追溯、Host/ZG回调、桥存储/搬运及完整输出。
单样本工程验收通过后再给三样本/首样本重复命令；最终完整ONNX误差报告及容限讨论仍后续进行。

## H. 单样本工程验收后三样本与首样本重复

前置：r3 mixed-one完整工程证据已核验，BOOT/JTAG保持且无其他AI/显示访问。
本阶段是原批准路线：外部限时300秒，同一Session依次前向308/309/310/308，共四次，最后一次专用于首帧重复核验。
使用同一程序/模型/RAW/注册/SDK默认优化及缓冲区策略，禁止重跑旧目录、复用旧身份或改数值容限。
308的不同运行结果也须与已保存mixed-one输出逐位核对；这不等于与ONNX逐位一致要求。

Windows PowerShell传入新r3单样本工程验收文件：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseAcceptance = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\mixed-one.acceptance.json'
scp -o StrictHostKeyChecking=yes $poseAcceptance 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/gates/mixed-one.acceptance.json'
if ($LASTEXITCODE -ne 0) { throw '单样本工程验收传输失败，停止。' }
```

Lite SSH仅执行一次，独立sh控制停止而不结束登录窗口：

```sh
set +e
set +u
sh -c '
set -eu
cd /tmp/pose-v1-mixed-validation/20261006-fusion-r3
test -f gates/mixed-one.acceptance.json
test ! -e run-mixed-three
sh package/run-mixed-validation.sh mixed-three
'
echo $?
```

预期退出0，results.jsonl保存三个不同帧的完整100候选，repeat-first.json保存第四次308的回调/耗时标记。
各帧分数100值/400字节、姿态4200值/16,800字节，另有308.repeat.scores/poses及SDK时序。
六Host和七ZG实际执行记录、桥搬运、绑定/参数/输入/SDK/设备/内核日志全部保留。
非有限输出、首帧重复不一致、不同输入输出全部不变、超时/OOM/总线/SDK异常或身份变化均停止并回传，不重试/复位/改模型或转CPU。
即使退出0，也不能自动宣布ONNX数值/连续性能通过，需代理核对完整三帧和两种首帧重复。

Windows PowerShell回传全部结果（失败仍需回传）：

```powershell
$poseReturn = Join-Path $poseRoot 'tools\pose-v1\evidence\mixed-20261006-fusion-r3\mixed-three'
if (Test-Path -LiteralPath $poseReturn) { throw '三样本回传目录已存在，保留停止。' }
scp -o StrictHostKeyChecking=yes -r 'root@192.168.126.49:/tmp/pose-v1-mixed-validation/20261006-fusion-r3/run-mixed-three' $poseReturn
if ($LASTEXITCODE -ne 0) { throw '三样本结果回传失败，停止。' }
```

代理核验时使用已保存的mixed-one目录核对跨Session首帧；完整工程核验后生成三样本工程记录和全ONNX误差报告。
相同槽位/最高分候选差异分别报告，不假定候选身份；容限依据实测讨论，HDMI/RTSP/5Hz/延迟/30分钟仍不在本轮通过范围。
