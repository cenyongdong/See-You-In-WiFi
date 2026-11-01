# 数值参考执行路线与依赖预览方案（2026-10-05，B已批准，ORT预览待批准）

后续注册探针已批准并执行：Matmul无注册，ZG六个Host节点中的TopK/GatherElements/ScatterND共五个也无注册，Gather有注册，见HOST-REGISTRY-RESULTS-20261005.md。全CPU参考和混合图PS部分均有当前注册缺口，停止执行下面的B模型命令及mixed；不能只换参考平台就认定混合推理可运行。ORT预览/安装未批准，后续注册/加载或SDK/模型修复另讨论批准。

“先用Lite Host作参考”。B路线及其资源前检/三样本参考范围已批准，
实际软件操作人工执行；资源查询已复核（available 744 MiB、Swap 0、/tmp剩余47G、结果前缀无旧文件）。随后一次300秒受限Host参考退出码1，执行未通过，原因待日志。暂停重跑与mixed，下列执行步骤保留为已批准试跑的历史方案；当前只读取已有诊断。
具体逐阶段命令：[LITE-HOST-COMMANDS.md](LITE-HOST-COMMANDS.md)。
此回复未批准下面独立ORT依赖预览项，不进行pip解析/安装或Windows SDK变更。

## 当前事实

- Lite的300份原始CSI预处理门检、三样本包完整性、ZG图离线检查及SDK Open/version探测已通过各自范围；完整模型尚未执行。
- 在正确的原开发CMD中已找到MSVC Hostx64/x64 cl，目标x64，VSINSTALLDIR正确，CMake实际回报3.31.6-msvc6。
- WindowsSdkDir未设置，WindowsSDKVersion仅为`\`，SDK尚未被开发脚本识别。
  代理只读检查厂商脚本使用的4个Windows v10.0登记入口和5个常见Windows Kits目录，均未找到。
  不能排除另有未登记的自定义SDK目录；不因此直接安装或手填INCLUDE/LIB。
- 项目Conda环境Python3.10.21/NumPy2.2.5，此前查询未找到ONNX Runtime。
- 已编译并校验的AArch64检查器包含host模式：创建HostBackend/HostDevice，不进入Device::Open分支；
  读取optimized JSON/RAW及同一固定参考张量，保存三份完整分数、姿态、后端回调与耗时。
  这只是静态可行性，尚未执行，不能承诺ARM Host所有算子支持或内存足够。

## Host参考路线选择

| 路线 | 收益 | 代价与未知项 |
| --- | --- | --- |
| A：继续Windows Host | 保持原定x86 ONNX＋x86 Icraft Host对照，更便于分离平台浮点差异 | 需先定位/补齐Windows SDK及验证VS实例发现；具体安装版本/组件方案还须讨论，当前不安装 |
| B：本阶段改用Lite Host参考 | 复用已编译二进制及3.39.0 SDK，不新增Windows/板端依赖；同一ARM Host与后续PS/NPU混合结果直接比较 | 全模型CPU计算可能慢、占用板端有限内存；ARM Host算子支持须实测；与Windows ONNX对比还混有架构浮点差异，不能把差异全归于转换 |

建议先选B，理由是当前正式目标是Lite混合推理数值验收，现有ARM二进制已包含这条独立参考路径。
这不改变正式NPU＋HDMI＋RTSP要求，不将全CPU参考作为部署降级方案。
若后续数值差异难以定位或ARM Host不支持，停止并讨论A或其他参考路径，不自动切换、删门禁或改模型。

## B已批准的人工操作范围

位置：Lite的MobaXterm SSH，目录`/tmp/pose-v1-inference-20261005`。
先查询free -m、df -h /tmp及现有进程，确认无其他推理/视频任务；结果先提交，不根据未实测内存估算直接开跑。
optimized RAW为64,493,152字节，不代表总内存需求；临时张量/运行库/证据文件还会占用额外内存和空间。
确认资源与新结果路径可用后，只执行已有检查器的host模式；无需重新编译/传输。

```bash
cd /tmp/pose-v1-inference-20261005
timeout --signal=TERM --kill-after=5s 300s ./pose_inference_check host --graph package/models/piw24_optimized.json --raw package/models/piw24_optimized.raw --inputs package/inputs --reference-tokens package/reference --output host-reference-20261005 > host-reference-20261005.stdout.log 2> host-reference-20261005.stderr.log
echo $?
```

该命令所属B范围已批准，资源查询现已复核；具体操作与失败停止条件见LITE-HOST-COMMANDS.md第2步。
`--reference-tokens`只用于host，保证与ONNX逐位相同输入；不带allow-device-init，程序不打开NPU/DMA设备。
mode=host/device_init_allowed=false，三份结果各100分数/4200坐标、形状正确且全部有限，
输入与参考逐位一致、后端绑定/回调属于Host，无ZG执行；阶段完整且无failure.json后，才进入数值对照。
结果、stdout/stderr及新保存的内核日志一并回传，保留文件哈希。每个输出/日志路径必须不存在，不覆盖旧证据。
超时、异常、OOM、算子不支持或非有限结果立即停止，不自动重试/复位/降级；参考性能不代表正式混合性能。
结果成功也仅是参考执行完成，输出误差仍待ONNX对照和讨论。

## ONNX Runtime依赖预览（独立审批项，暂不安装）

建议候选为CPU包`onnxruntime==1.23.2`。
[Microsoft维护的PyPI版本页](https://pypi.org/project/onnxruntime/1.23.2/)确认Python>=3.10，
含CPython3.10 Windows x86-64 wheel，与当前Python/系统架构相符。
这是可复现候选，不是最新版本声明，也不证明模型执行已通过。
[官方安装说明](https://onnxruntime.ai/docs/install/)区分CPU/GPU包，本参考仅用CPUExecutionProvider。

本项拟申请在项目独立Conda环境中进行pip版本查询及dry-run依赖解析，保存报告，不安装软件；当前未批准：

- 解释器固定当前worktree `.local/pose-v1-conda/python.exe`，不使用base/koala/Icraft环境。
- 约束NumPy==2.2.5，保留h5py/PyWavelets及其他已装包；不升级现有组件。
- 仅解析官方PyPI预编译wheel，保存report到新建独立 `.local/pose-v1-reference-deps/preview-20261005`。
- dry-run会联网获取元数据，可能下载wheel到pip缓存，不是无写入操作；不执行安装或模型。
- 解析完成后由代理审阅具体依赖版本/哈希/变更清单，形成安装锁文件，再单独请求安装同意。
- 没有pip、版本不支持dry-run、证书/下载失败、要求源码构建或现有包变化时停止，不改证书/渠道/自动升级pip。

具体候选命令（在Windows PowerShell执行，获批准前不执行）：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-conda\python.exe'
& $posePython -m pip --version
if ($LASTEXITCODE -ne 0) { throw 'pip不可用，停止。' }
$posePreview = Join-Path $poseRoot '.local\pose-v1-reference-deps\preview-20261005'
if (Test-Path -LiteralPath $posePreview) { throw '预览目录已存在，保留并停止。' }
New-Item -ItemType Directory -Path $posePreview | Out-Null
& $posePython -m pip --isolated install --dry-run --only-binary=:all: `
  --index-url 'https://pypi.org/simple' `
  --constraint 'tools\pose-v1\ort-preview.constraints.txt' `
  --report (Join-Path $posePreview 'resolution.json') 'onnxruntime==1.23.2'
if ($LASTEXITCODE -ne 0) { throw '依赖预览失败，保留报告/输出并停止，不安装。' }
```

isolated忽略pip配置与环境变量，index-url固定官方PyPI；报告中的实际来源还须核对，
不把解析成功当作文件来源/哈希或安装验收。约束文件仅用于固定已有数值依赖版本。
预期输出包含Would install，产生resolution.json且不出现Successfully installed；
报告/终端输出交回后才讨论安装锁文件。
官方CPython3.10 Windows x64 ORT wheel SHA256为
`0be6a37a45e6719db5120e9986fcd30ea205ac8103fd1fb74b6c33348327a0cc`，预览报告须与此核对。

B范围已批准、Host尚未执行；ORT部分仍仅候选，未运行解析、安装或任何参考模型。
Windows SDK提供平台头文件/库，与编译器及VC运行库不同，见[Microsoft SDK说明](https://learn.microsoft.com/en-us/windows/apps/windows-sdk/)；
选择B不等于修好了Windows SDK，A仍保留为后续环境完善路线。
