# CPU候选r1编译问题：源码与日志修正（2026-10-06，已批准并应用）

本方案后，已将审阅候选应用到生效检查器和构建脚本，旧文件备份/包/构建目录保持。
生效PowerShell语法0错误，源码三处已改Array::set；尚未生成r2包、重编译或执行算子测试。

## 已确认与未知

新构建`cpu-adapter-20261006-r1`已完成SDK审计和CMake配置/生成。
代理只读核对导出的六份头文件、Host so与原包身份、两份3.39.0版本记录，以及五份构建源码副本，全部匹配。
此前容器Python依赖已移除，本次不是同一阻断。

截图显示编译`host_cpu_adapter_check.cpp`时，在函数mutate内产生stderr，
Windows PowerShell的NativeCommandError/RemoteException中断了日志管道。
本地build.log结束于两条Building CXX object进度，没有实际error正文；不能据此认定完整编译诊断已取得。
对象进度百分比不代表对象完成，程序未链接/验收。

静态核对确认测试代码有三处：

```cpp
dims.get_mutable()->at(dims.size()-1) -= 1;
```

`icraft-xir/base/array.h`的Array继承ObjectRef；`base/object.h:290`的get_mutable返回Object*。
ArrayNode虽有at，但这里取得的静态类型Object没有at，因此该表达式不能编译。
SDK明确提供Array::set(int64_t,T)，支持负索引；建议改为：

```cpp
dims.set(-1, dims[-1] - 1);
```

保持既有从std::vector独立复制的dims，不改变浅引用处理或三种异常用例的含义。
这是测试源码API错误；完整编译诊断缺失，不能排除其他编译问题。

## 具体修正范围

1. 仅替换检查器上述三处数组修改调用；注册模块、算子内核、形状/布局/数值策略、模型和SDK不改。
2. 修改Invoke-CpuDocker日志捕获：只在该次原生命令与日志管道内临时使用Continue，
   将stderr ErrorRecord转换为文本保存全部诊断；finally恢复原Stop策略，仍以实际Docker退出码非0停止。
   不忽略编译失败，不改参数数组/编译器/CMake/链接，不自动重试。
3. 保留现有脚本、源码、包、r1目录及失败记录。源码身份变化后，用新包记录身份，
   不回写原manifest哈希、不跳过源码哈希门禁。

已应用[审阅补丁](CPU-ADAPTER-COMPILE-FIX-20261006.candidate.patch)，
[源码候选](host_cpu_adapter_check.array-set.candidate.cpp)和
[脚本候选](Build-CpuAdapter.stderr-log.candidate.ps1)保留为审阅历史；生效文件与候选逐字节一致。
原文件备份在evidence/host_cpu_adapter_check.before-array-set-20261006.cpp和
evidence/Build-CpuAdapter.before-stderr-log-20261006.ps1。PowerShell语法0错误，尚未实际编译。

## 接下来执行

代理已应用审阅补丁、保存备份及记录，并更新[正式执行说明A/B](CPU-ADAPTER-COMMANDS.md)。
在Windows PowerShell项目根目录生成新的身份包并使用新构建目录：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePython = Join-Path $poseRoot '.local\pose-v1-conda\python.exe'
$poseGraph = Join-Path $poseRoot '.local\pose-v1-inference\package-20261005\models\piw24_ZG.json'
$posePackage = Join-Path $poseRoot '.local\pose-v1-cpu-adapter\package\20261006-r2'
& $posePython tools\pose-v1\cpu_adapter_gate.py prepare --graph $poseGraph --sdk 'C:\Icraft\CLI v3.39.0' --output $posePackage
if ($LASTEXITCODE -ne 0) { throw '新身份包准备失败，停止并报告。' }
& .\tools\pose-v1\Build-CpuAdapter.ps1 -Package $posePackage -BuildTag 'cpu-adapter-20261006-r2'
```

新包路径、新本机构建`.local/pose-v1-build/cpu-adapter-20261006-r2`及容器目录
`/tmp/pose-v1-cpu-adapter-20261006-r2`必须不存在；原包和两次失败目录不删除/覆盖。
生成器/输入/参考逻辑不变，设计仍107用例/22输出；代理随后比较新旧281项非manifest产物，
确认数据与参考逐字节不变。新的manifest和清单变化只用于记录修正源码/脚本身份。
如CMake/编译再次失败，保存完整日志停止讨论，不自动修正或继续板端测试。
返回build.log、sdk-audit.json和成功时build-result.json后，代理核对才进入Lite CPU测试。

本次已按AGENTS.md决策审批规范取得；不扩展为代理代编译、NPU/DMA/HDMI或完整模型操作。
应用身份见evidence/cpu-adapter-compile-fix-applied-r2-20261006.json；应用不等于编译/前向通过。
