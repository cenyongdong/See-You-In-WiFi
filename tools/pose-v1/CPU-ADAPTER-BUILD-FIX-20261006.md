# CPU候选构建：容器Python前提修正（2026-10-06，已批准并应用）

本方案，现已应用审阅过的候选脚本；原脚本备份和失败证据保留。
生效脚本语法检查0错误，未执行修正版构建或算子测试，不是构建/前向通过。
执行入口为[CPU-ADAPTER-COMMANDS.md](CPU-ADAPTER-COMMANDS.md)的B部分。

## 已确认事实

成功生成测试包后运行Build-CpuAdapter.ps1，日志显示GCC9.4.0、CMake3.24.2，
随后`docker exec FPAI python3`返回127：`executable file not found in $PATH`。
构建尚未进入CMake配置/C++编译，也没有候选程序或算子测试结果。
该报错只证明当前容器执行环境找不到该命令，不足以排除其他位置的解释器。
构建脚本未预先核实容器Python可用性，这是脚本的前提缺失。

代理只读复核了实际测试包`.local/pose-v1-cpu-adapter/package/20261005`：282项清单哈希匹配，
107用例（18正常、89异常拒绝）、22份正常参考输出；原图及5份构建文件身份匹配，
失败构建目录中的源码副本/manifest也匹配。这是产物完整性检查，不是算子数值运行通过。
实际包路径与初始命令说明的`package-20261005`不同，但脚本接收实际路径，本次不需要因此重做测试包。

## 已应用的修正

[候选完整脚本](Build-CpuAdapter.no-container-python.candidate.ps1)及
[审阅补丁](Build-CpuAdapter.no-container-python.candidate.patch)作为审阅历史保留，
当前Build-CpuAdapter.ps1与候选逐字节一致；原脚本备份在
`evidence/Build-CpuAdapter.before-no-container-python-20261006.ps1`。
只替换SDK审计实现：

1. 容器仍通过dpkg-query查询Icraft/CustomOp arm64版本，要求3.39.0。
2. Docker cp导出六份原头文件及Host so到新构建目录的sdk-snapshot。
3. Windows PowerShell/.NET核对头文件CRLF→LF规范化SHA256及Host库原字节SHA256，
   与同一测试包manifest对照，保留原审计字段/停止条件；头文件UTF-8解码失败也停止。
4. sdk-audit.json在Windows生成，保留审计方式及导出文件；build-result.json增加实际构建脚本哈希。

无需为FPAI安装Python或其他依赖，不改容器镜像、SDK、候选C++、CMake、模型、测试输入或参考输出。
修改的是核验执行位置，仍核对容器实际文件，不能拿Windows SDK代替ARM身份。
生效脚本已完成PowerShell语法解析（0错误）；Docker导出、修正版构建及算子运行都没有执行。

## 接下来执行的顺序

代理已保留原脚本身份并应用审阅补丁，更新命令说明和修正记录。
随后在Windows PowerShell项目目录使用现有测试包和新的构建标签：

```powershell
$poseRoot = 'C:\Users\cenyongdong\.codex\worktrees\dea3\FPGACompetitionProject'
Set-Location -LiteralPath $poseRoot
$posePackage = Join-Path $poseRoot '.local\pose-v1-cpu-adapter\package\20261005'
& .\tools\pose-v1\Build-CpuAdapter.ps1 -Package $posePackage -BuildTag 'cpu-adapter-20261006-r1'
```

新Windows目录`.local/pose-v1-build/cpu-adapter-20261006-r1`和容器目录
`/tmp/pose-v1-cpu-adapter-20261006-r1`必须此前不存在；旧失败目录完整保留，不删除/覆盖。
预期产物仍为build.log、sdk-audit.json、build-result.json及ARM二进制，新增sdk-snapshot审计原件。
编译失败/身份差异继续停止并讨论，不自动改链接/SDK或继续板端测试。
回传构建日志和JSON经代理核对后，再沿既有批准范围进入Lite CPU测试。

修改Build脚本不会改变测试包中的C++/CMake身份；包内sources记录原准备阶段脚本身份作为历史来源保留，
新build-result记录实际修正版脚本身份。不直接回写现有manifest或清单哈希。

该修正按AGENTS.md决策审批规范取得后应用，不扩大为代理代执行构建或板端测试。
应用身份和边界见`evidence/cpu-adapter-build-fix-applied-20261006.json`。
