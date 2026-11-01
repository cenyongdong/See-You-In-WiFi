# Lite Host三样本数值参考：人工操作说明（2026-10-05）

**旧链入口（2026-10-29）：** 本页属于早期 pose-v1 诊断／验证，当前部署从[最终进度](../../PROJECT-PROGRESS.md)进入；旧主机路径、板端目录、算子计数与阶段授权不能套用最新演示。

状态：Host参考退出码1，日志已定位Session::Create<HostBackend>绑定op_id=1 MatmulNode失败，尚未执行样本前向；根因仍待库/注册审查。见HOST-BINDING-REVIEW-20261005.md。暂停重跑及数值比较/mixed，下面执行命令保留为历史记录，不再次运行。

后续独立注册探针已确认Matmul及ZG图六个Host节点中的五个无注册，Gather有注册；
具体HOST-REGISTRY-RESULTS-20261005.md。CPU参考与混合图PS部分均存在注册阻断，不能跳过参考或直接运行mixed。
复用已交叉编译二进制，SHA256为
`d1006f9bd78050ffa484c64bf74fb62542d270c7acca5068e9da611a5bdc05e5`。
不改源码/构建/模型，不重编译/重传二进制，不安装依赖，不调用NPU Device::Open。
Host只作数值参考，正式PS/NPU及双路验收要求保持。

## 1. 资源与结果路径查询（已执行、截图已复核）

2026-10-05截图：总内存993 MiB、available 744 MiB、Swap 0；/tmp位于根文件系统，剩余47G。
可见进程未见明显其他推理/视频应用，host-reference-20261005前缀查询无输出。
证据：evidence/lite-host-resource-query-20261005-1.png及-2.png。
可进入已批准的第2步一次受限试跑；模型峰值内存、ARM算子支持和耗时仍未知，不把资源前检当成模型通过。
下列命令保留为已完成的查询记录，不必重跑。

位置：Lite的MobaXterm SSH（root@192.168.126.49），不是Windows终端或训练服务器。

```bash
cd /tmp/pose-v1-inference-20261005
free -m
df -h /tmp
ps -eo pid,comm,args
find . -maxdepth 1 -name 'host-reference-20261005*' -print
```

- cd固定此前已校验的程序/包目录；目录不存在则停止，不另建或猜路径。
- free报告总/可用内存和Swap；重点看available，不能只看free或64.5MB权重大小推断总需求。
- df查询/tmp实际所在文件系统剩余空间，不改分区。
- ps查是否有其他推理/视频任务；不自动终止进程，不能仅凭名字保证所有设备空闲。
- find仅查询这次输出前缀；没有输出表示未发现旧产物，出现任一路径先停并保留，不覆盖/删除。

本次资源结果已复核；模型临时张量内存和运行时间尚未实测，不设置未经讨论的Swap或线程参数。

## 2. 资源复核后：固定三样本Host执行

继续在同一Lite SSH终端，确认本次结果前缀仍无旧文件，当前未运行其他推理/视频任务。
使用E已验证的GNU timeout，保持SDK默认设置；不修改优化配置。

先保存操作前内核上下文，再运行一次：

```bash
cd /tmp/pose-v1-inference-20261005
dmesg | tail -n 80 > host-reference-20261005.before.dmesg.log
timeout --signal=TERM --kill-after=5s 300s ./pose_inference_check host --graph package/models/piw24_optimized.json --raw package/models/piw24_optimized.raw --inputs package/inputs --reference-tokens package/reference --output host-reference-20261005 > host-reference-20261005.stdout.log 2> host-reference-20261005.stderr.log
echo $?
```

立即记录退出码。0表示程序完成，仍须核对文件/后端/数值；非0（含timeout、137、139等）停止后续阶段，
只读取/保存本次诊断，不重跑、复位或改模型。
300秒约束整个初始化及三个窗口，TERM后5秒仍未退出则KILL；不保证CPU参考能在该时限内完成。
`--reference-tokens`使用与ONNX完全相同的已校验float32输入；仅host允许该参数。
optimized图由HostBackend/HostDevice执行，不带allow-device-init，也不走NPU/DMA Open分支。

随后无论是否成功，都保存/读取本次已有诊断；文件不存在则报告，不创建假结果或重跑：

```bash
dmesg | tail -n 80 > host-reference-20261005.after.dmesg.log
free -m
ls -l host-reference-20261005
cat host-reference-20261005/stages.jsonl
cat host-reference-20261005/run-config.json
cat host-reference-20261005/failure.json
cat host-reference-20261005/results.jsonl
cat host-reference-20261005.stdout.log
cat host-reference-20261005.stderr.log
```

退出非0、出现failure.json/OOM/算子异常/非有限值或日志不明确时，先提交上述证据，停止回传比较之外的后续执行。
启动阶段的旧journal等消息不自动归因于本次Host；内核前后上下文用于审查。

## 3. 成功产物门检与回传（第2步复核后）

必须有三个固定case及原帧号6/7/8，每份.input.f32为43,200字节、.scores.f32为400字节、.poses.f32为16,800字节。
形状[1,180,60]、[1,100]、[1,100,14,3]；程序检查全部有限值，但输入逐位一致、后端绑定/回调还须独立核对。
配置mode=host/device_init_allowed=false，阶段以three_cases_completed_not_numerically_accepted结束，无failure.json。
backend-bindings及operator-execution必须只显示Host运行；observed_zg_callbacks=0，不把没有NPU执行误认为本参考失败。
profile原始单位尚未确认；参考CPU耗时不代表正式混合推理性能。

第2步成功及日志复核后，人工在Lite生成清单：

```bash
cd /tmp/pose-v1-inference-20261005
sha256sum host-reference-20261005/* > host-reference-20261005.sha256
echo $?
```

清单不得预先存在；生成异常停止，保留原输出。
之后在Windows PowerShell从当前worktree回传，主机目标目录也不得存在：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$poseScp = 'C:\Windows\System32\OpenSSH\scp.exe'
$poseHostResult = Join-Path $poseRoot '.local\pose-v1-inference\host-20261005'
$poseHostEvidence = Join-Path $poseRoot '.local\pose-v1-inference\host-20261005-evidence'
if ((Test-Path -LiteralPath $poseHostResult) -or (Test-Path -LiteralPath $poseHostEvidence)) { throw '本地结果/日志目录冲突，停止。' }
New-Item -ItemType Directory -Path $poseHostEvidence | Out-Null
& $poseScp -r 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/host-reference-20261005' $poseHostResult
if ($LASTEXITCODE -ne 0) { throw '参考结果回传失败，停止。' }
& $poseScp 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/host-reference-20261005.sha256' 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/host-reference-20261005.stdout.log' 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/host-reference-20261005.stderr.log' 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/host-reference-20261005.before.dmesg.log' 'root@192.168.126.49:/tmp/pose-v1-inference-20261005/host-reference-20261005.after.dmesg.log' $poseHostEvidence
if ($LASTEXITCODE -ne 0) { throw '参考日志回传失败，停止。' }
$poseHostSeen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($poseHashLine in (Get-Content -LiteralPath (Join-Path $poseHostEvidence 'host-reference-20261005.sha256') -Encoding ASCII)) {
  if ($poseHashLine -notmatch '^([0-9a-f]{64})  host-reference-20261005/([A-Za-z0-9_.-]+)$') { throw 'Host校验清单路径/格式异常，停止。' }
  $poseHostHash = $Matches[1]
  $poseHostName = $Matches[2]
  if ($poseHostName -in @('.', '..') -or -not $poseHostSeen.Add($poseHostName)) { throw '非法或重复Host文件名，停止。' }
  $poseReturnedHash = (Get-FileHash -LiteralPath (Join-Path $poseHostResult $poseHostName) -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
  if ($poseReturnedHash -ne $poseHostHash) { throw ('Host回传哈希不符：' + $poseHostName) }
}
$poseHostFiles = @(Get-ChildItem -LiteralPath $poseHostResult -File -Force)
if ($poseHostSeen.Count -eq 0 -or $poseHostSeen.Count -ne $poseHostFiles.Count) { throw 'Host回传文件清单不完整，停止。' }
Write-Host ('Host回传哈希匹配：' + $poseHostSeen.Count + '份；数值验收仍待复核。')
```

回传/校验仍人工执行，代理随后审查输入逐位一致、完整输出/后端/帧号/哈希。
原inference_gate.py verify-return明确只接受mixed前缀，本次不调用或修改它。
上述Host专用读取只接受host-reference-20261005的简单文件名、拒绝重复/非法路径、逐文件SHA256并核对完整列表。
该目录保持原G比较命令使用的host-20261005路径，但来源明确为Lite ARM，不是Windows Host。

## 4. 尚未批准或未通过

ONNX Runtime依赖预览/安装仍待独立同意；本轮只批准B，不能自行运行pip或借koala。
Host执行成功仍只是CPU参考完成，ONNX↔Host↔mixed完整数值门检及容限未通过。
ARM Host与Windows ONNX对照包含跨架构差异，若差异不清楚先讨论，不自动归因于模型转换。
mixed/NPU正式推理、HDMI、RTSP、性能与30分钟闭环保持待验收。
