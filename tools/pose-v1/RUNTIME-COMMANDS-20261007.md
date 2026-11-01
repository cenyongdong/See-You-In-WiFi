# E0/N1/P1 r2执行与复现命令（2026-10-07）

本轮按阶段恢复后和此前“代理执行”批准实施；命令保留供理解/复现，无需再代执行。
历史r1、r6和所有失败证据保留，**已经执行的阶段不要重复运行**。

## Windows准备、构建与审查

位置：当前worktree PowerShell，根目录`C:/Users/cenyongdong/.codex/worktrees/dea3/FPGACompetitionProject`。
前置：独立Conda、原r6基线/固定样本、FPAI容器和ARM SDK身份保持。
固定变量如下，标签或产物存在时停止，不覆盖；下列准备/构建已由代理执行。

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePy = Join-Path $poseRoot '.local\pose-v1-onnx-conda\python.exe'
$posePackage = Join-Path $poseRoot '.local\pose-v1-runtime\package-20261007-e0-n1-p1-r2'
$poseBuild = Join-Path $poseRoot '.local\pose-v1-build\mixed-20261007-runtime-r2'
$poseEvidence = Join-Path $poseRoot 'tools\pose-v1\evidence\runtime-20261007-r2'
& $posePy tools\pose-v1\runtime_gate.py prepare --package $posePackage
& .\tools\pose-v1\Build-MixedValidation.ps1 -Package $posePackage -BuildTag mixed-20261007-runtime-r2
& $posePy tools\pose-v1\runtime_gate.py review-build --package $posePackage --build $poseBuild --output "$poseEvidence\build.acceptance.json"
```

构建只编译，不执行模型；输出ARM程序、源码副本、SDK审计、完整日志和build-result.json。
必须实际核验15来源、351清单、ARM SDK头文件/两后端库、AArch64/直接依赖与哈希，再传入本包匹配的build门禁。
复用ORT参考时先执行独立审查，不能改旧参考environment.json的包身份来伪造关联：

```powershell
& $posePy tools\pose-v1\review_runtime_reference.py --reference .local\pose-v1-runtime\onnx-27-20261006-r1 --package $posePackage --output "$poseEvidence\ORT27-review.json"
```

它证明27份输入/模型不变、86项/所有输出有限及重复、308旧参考一致，记录旧包和新包关联；不重跑ORT或安装依赖。

## Lite阶段

位置：SSH已认证的Lite，工作目录`/tmp/pose-v1-runtime/20261007-r2`。
前置：已读回BOOT9文件、SDK/内核/资源身份，运行FPGA版本由程序Open/version进一步核验；无竞争应用。
新目录已由代理创建并传入package、pose_mixed_check、build-result.json和gates/build.acceptance.json。
只使用本包`run-runtime-validation.sh`；旧runner不是本包执行入口。

每次命令都放在独立`sh -c`，不会因非0关闭SSH登录shell。**四条逐阶段执行，每条先完成、回传、审查及传回新门禁，再下一条；不能整段一次粘贴。**

```sh
sh -c 'set -eu; cd /tmp/pose-v1-runtime/20261007-r2; sh package/run-runtime-validation.sh host-check'
```

Host107上限300秒，仅Host内存/CPU注册和内容路径，不Open设备或Session。预期exit=0、107例/22输出与固定参考一致、12注册/Gather保持。
完整回传run-host-check，Windows核验后传gates/host-check.acceptance.json：

```powershell
& $posePy tools\pose-v1\runtime_gate.py review-stage --stage host-check --package $posePackage --build $poseBuild --results "$poseEvidence\host-check" --output "$poseEvidence\host-check.acceptance.json"
```

```sh
sh -c 'set -eu; cd /tmp/pose-v1-runtime/20261007-r2; sh package/run-runtime-validation.sh e0'
```

E0上限180秒，真实RAW/注册/Session apply一次，再308/309/310/308四次；保存全部输出和内容。预期完整输出与r6逐位一致、每帧0→745、1173七ZG组追溯及六计算Host。
完整回传run-e0并核验，生成/传入gates/e0.acceptance.json：

```powershell
& $posePy tools\pose-v1\runtime_gate.py review-stage --stage e0 --package $posePackage --build $poseBuild --results "$poseEvidence\e0" --output "$poseEvidence\e0.acceptance.json"
```

```sh
sh -c 'set -eu; cd /tmp/pose-v1-runtime/20261007-r2; sh package/run-runtime-validation.sh n1'
```

N1上限120秒，九组27固定真实输入＋首帧重复共28次，保存100候选分数/姿态和实际内容。预期PS一致、有限/重复一致、不同输入响应、状态和绑定保持。
完整回传run-n1并核验，生成/传入gates/n1.acceptance.json；对照ORT只出实测误差，不自动定容限：

```powershell
& $posePy tools\pose-v1\runtime_gate.py review-stage --stage n1 --package $posePackage --build $poseBuild --results "$poseEvidence\n1" --output "$poseEvidence\n1.acceptance.json"
& $posePy tools\pose-v1\runtime_gate.py compare --package $posePackage --reference .local\pose-v1-runtime\onnx-27-20261006-r1 --results "$poseEvidence\n1" --acceptance "$poseEvidence\n1.acceptance.json" --output "$poseEvidence\ONNX27-comparison.json"
```

```sh
sh -c 'set -eu; cd /tmp/pose-v1-runtime/20261007-r2; sh package/run-runtime-validation.sh p1'
```

P1上限120秒，3预热三帧分别与包内有身份r6完整输出核对后，才30次计量；每次仍检查r6输出。
SDK profiling保持，输入预载、证据批量保存，计时包含PS预处理/状态清理/前向/最终等待/读出/有限性/最高分选择。
完整回传run-p1并核验：

```powershell
& $posePy tools\pose-v1\runtime_gate.py review-stage --stage p1 --package $posePackage --build $poseBuild --results "$poseEvidence\p1" --output "$poseEvidence\p1.acceptance.json"
```

所有返回目录均需等待SSH打印阶段exit和外层返回码后再完整获取；不得用进行中的部分回传签发门禁。
阶段工具自动记录完整stdout/stderr、exit、SDK/程序/前门禁身份、free/ps/dmesg及LF哈希。
非0、超时/OOM/总线/SDK异常、身份变化、非有限或重复失配保存停止，不自动重试、关profiling、reset(0)、重建Session或更换模型/BOOT。
H0仅本机资料核对；网络/渲染/HDMI/VPU/RTSP硬件接入与最终数值容限另议。
