# Windows Host工具定位与用户环境查询（2026-10-05）

最新同窗口查询：where cl已找到Hostx64/x64编译器，目标x64、VSINSTALLDIR正确，CMake实际3.31.6-msvc6。
WindowsSdkDir未设置，WindowsSDKVersion仅`\`，有效Windows SDK未识别；不是编译器或路径继承问题。
代理只读检查厂商脚本读取的4个Windows v10.0注册表入口及5个常见Windows Kits目录均未找到，
不能排除其他自定义未登记目录。SDK未确认前不执行F2构建，不手填INCLUDE/LIB、不安装/修复。
证据`evidence/windows-host-sdk-query-20261005.png`（历史附件，当前仓库未附）。
后续路线讨论见[REFERENCE-NEXT-PLAN.md](REFERENCE-NEXT-PLAN.md)，未批准，不代表参考已完成。

## 只读定位结果

在本机文件系统找到VS 2022 Community目录：
`D:\Visual Studio\ Visual Studio 2022\Community`。
注意第二层目录名为` Visual Studio 2022`，开头有一个空格，命令必须原样复制。

| 文件 | 已读取的文件元数据 | 验证边界 |
| --- | --- | --- |
| VC/Tools/MSVC/14.44.35207/bin/Hostx64/x64/cl.exe | FileVersion 19.44.35213.0 | 文件存在，未执行或编译 |
| 同目录link.exe | FileVersion 14.44.35213.0 | 文件存在，未链接 |
| 同目录nmake.exe | 文件存在 | 未执行，不据此更换CMake生成器 |
| Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe | FileVersion 3.31.6-msvc6 | 未运行版本查询或配置 |
| Common7/Tools/VsDevCmd.bat | 文件存在，已读源码 | 尚未执行初始化 |
| VC/Tools/MSVC/14.44.35207/include/vector及lib/x64/msvcprt.lib | 文件存在 | 不能据此确认Windows SDK完整 |

普通PowerShell的PATH未找到cl/CMake，不再解释为机器没有这些文件。
安装记录中找到的Visual C++ Redistributable是运行库，不作为编译器安装证据；
上述文件定位才是本次编译工具存在的依据。
常见Visual Studio及Windows Kits注册表入口未返回记录，默认Windows Kits Include目录未列出版本；
不能由此确诊SDK未安装或注册表/安装完整。VS实例能否被CMake生成器识别也尚未核验。
`Launch-VsDevShell.ps1`的源码依赖vswhere，而默认vswhere位置此次未找到，
本次查询使用已有VsDevCmd.bat进入独立CMD，避免把未知的实例查找结果当作已验证。

## 人工执行：仅临时开发终端与查询

最新现场反馈：自动定位后已显示VS开发终端横幅；另一截图中where cl未找到，目标架构/SDK变量原样显示。
随后明确查询是在另外打开的CMD中执行，那个进程没有继承开发环境；
不据此认定原窗口初始化失败或SDK缺失。现在回原初始化窗口查询，原窗口环境及SDK仍待验证。
代理只读确认start/parse/winsdk/vcvars等厂商初始化脚本存在；横幅v17.0是vswhere缺失时的源码默认值，
不能作为完整安装版本或初始化失败证据。截图见
启动横幅（历史附件，当前仓库未附：`evidence/windows-host-banner-20261005.png`）、环境变量查询（历史附件，当前仓库未附：`evidence/windows-host-unset-query-20261005.png`）。

属于既定环境查询步骤的延续。在Windows主机执行，代理不代执行。
不安装、修复或下载软件，不改永久PATH、不编译、不运行模型，不访问板卡。

首次启动截图中的路径漏掉了目录名开头空格，CMD返回“系统找不到指定的路径”。
代理只读再次确认实际目录首字符为32（空格）、带空格路径文件存在，不带空格路径不存在。
这次失败不能作为SDK缺失或编译器损坏的证据；截图`evidence/windows-host-path-error-20261005.png`（历史附件，当前仓库未附）。
下面改为从真实目录项构造路径，Trim只用于匹配名称，FullName原样保留；查询与临时终端范围不变。

1. 如果当前提示符为CMD（没有PS标记），先执行`exit`回到原PowerShell。
   然后在Windows PowerShell逐条执行以下命令；它进入新的x64开发CMD子进程：

```powershell
$poseVsDirs = @(Get-ChildItem -LiteralPath 'D:\Visual Studio' -Directory | Where-Object { $_.Name.Trim() -eq 'Visual Studio 2022' })
if ($poseVsDirs.Count -ne 1) { throw 'VS目录缺失或不唯一，停止并反馈。' }
$poseDevCmd = Join-Path $poseVsDirs[0].FullName 'Community\Common7\Tools\VsDevCmd.bat'
if (-not (Test-Path -LiteralPath $poseDevCmd -PathType Leaf)) { throw '开发终端脚本不存在，停止。' }
cmd.exe /d /k ('call "' + $poseDevCmd + '" -arch=amd64 -host_arch=amd64')
```

`/d`禁用CMD AutoRun，`/k`保留这个临时终端；call调用已存在的厂商脚本，
两项架构参数选择x64工具与x64目标。环境设置只在子进程中，退出不改原PowerShell或系统环境。
若脚本提示初始化失败、Windows SDK缺失或其他错误，先截图并停止，不修复、不继续编译。

2. 在第1步同一窗口中、横幅下方新出现的CMD提示符执行查询；不要另外打开CMD或PowerShell。
   环境只存在于那个初始化进程，另外打开的终端不会继承它。这些不是PowerShell语法：

```cmd
where cl
where cmake
"%VSINSTALLDIR%Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" --version
echo %VSCMD_ARG_TGT_ARCH%
echo %VSINSTALLDIR%
echo %WindowsSdkDir%
echo %WindowsSDKVersion%
```

where cl应指向已发现MSVC的Hostx64/x64目录；出现多份时交回复核，不自行选用。
where cmake用于查询当前PATH；即使未找到，随后固定已发现路径的版本查询也可提供独立信息，
不因此自行补PATH。这里用成功初始化后厂商设置的VSINSTALLDIR读取同一安装目录的CMake，避免手写路径空格。
VSINSTALLDIR未设置或路径不正确时停止并反馈，不自行换软件。CMake版本预期与文件元数据3.31.6系列一致，异常交回。
目标架构应为x64/amd64，两个SDK变量应有实际路径/版本；原样输出百分号变量名表示未设置。
所有输出交回审查，尤其保留初始化错误；文件存在和版本查询不能代替后续配置/编译验证。

3. 查询完成后可执行`exit`返回原PowerShell。暂不运行F2构建或安装任何组件。

ONNX Runtime仍未安装在项目独立Conda环境中，另行准备并讨论最小依赖方案；
本次不借用koala、不修改模型或把CPU参考当作正式NPU部署。
