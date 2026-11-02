# 独立推理门检：用户环境查询结果（2026-10-05）

## 补查后的最新结论

继续提供目录和dpkg文件清单截图，证据为`evidence/sdk-files-query-20261005.png`与
`evidence/sdk-packages-query-20261005.png`。已确认：

- SDK配置目录`/usr/cmake`，包含`icraft-hostbackend-config.cmake`、`icraft-zg330backend-config.cmake`及aarch64导出文件。
- `/usr/include/icraft-backends/zg330backend/zg330backend.h`、`/usr/include/icraft-xrt/dev/zg330_device.h`存在于包清单；
  `/usr/lib/aarch64-linux-gnu/libicraft_zg330backend.so`与ZG330相关AIU库也列在已安装包中。
- `icraft arm64 3.39.0`、`customop arm64 3.39.0`、`icraftmdzthirdparty arm64 0.1.1`均为`install ok installed`。
- 构建脚本的SDK配置文件名称与这些路径一致，当前不需要因先前精确搜索没有输出而安装后端包。

可以继续已批准方案的B固定打包、C交叉编译，设置`-SdkCmakeDir '/usr/cmake'`。
这只是构建入口和文件配套确认，尚未证明编译/链接、实际头文件API、运行库加载或NPU功能通过。
ORT缺失、Windows cmake/cl当前PATH不可见的状态仍保留；它们不阻止独立FPAI交叉编译准备。
此阶段先提交构建日志，不越过编译复核、设备probe和数值验收门检。

下文“ZG330配置未找到/不能进入C”是补查前的历史状态，以本段更新为准。

来源：人工操作Windows PowerShell命令后提供的两张截图，见
`evidence/environment-query-20261005.png`和`evidence/windows-tools-query-20261005.png`。
代理仅审查截图/本地资料，没有执行Docker、编译、推理或安装。

## 已确认及证据边界

| 项目 | 截图结果 | 判断 |
| --- | --- | --- |
| FPAI交叉编译器 | aarch64-linux-gnu-g++ (Ubuntu9.4.0-1ubuntu1~20.04.2)9.4.0 | 已查询，与此前GCC9.4基线一致 |
| FPAI CMake | 3.24.2 | 容器CMake可调用；不能扩展为Windows CMake可调用 |
| FPAI Icraft | icraft:arm64 3.39.0 | 匹配当前版本；`*icraft*`查询不包含CustomOp，后者此次未核验 |
| SDK配置文件搜索 | 仅`/usr/cmake/icraft-hostbackend-config.cmake` | 此次精确文件名搜索未发现ZG330配置；可能是包内容、命名或布局不同，尚不能确诊NPU运行库缺失 |
| 独立Conda NumPy | dependencies输出true | 模块可找到，本次不是版本/导入/推理测试 |
| 独立Conda ONNX Runtime | dependencies输出false | 当前环境未找到ORT；ONNX参考暂停，不自动安装 |
| Windows CMake/MSVC | 第二张图中正确Get-Command cmake,cl没有输出 | 当前终端PATH不可见；不能证明全机未安装 |

首图最初的Docker变量调用和Python路径调用报错，后续重新设置变量后已分别查询成功；
不是GCC、Conda或模型故障。首图最后使用Get-Content无法查询命令入口；随后正确使用Get-Command，
结果仍无输出，以上Windows判断依据第二张图。

## 下一步：只补充包内容查询

执行位置：Windows PowerShell，当前worktree根目录。命令只查询FPAI已安装文件，不编译、安装或访问板卡。

```powershell
$poseDocker = 'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
& $poseDocker exec FPAI ls -1 /usr/cmake
& $poseDocker exec FPAI dpkg-query -L icraft:arm64 | Select-String -Pattern 'cmake|zg330|zhuge|buyi'
& $poseDocker exec FPAI dpkg-query -W '-f=${Package} ${Architecture} ${Version} ${Status}\n' | Select-String -Pattern 'icraft|customop'
```

1. `ls`显示已确认存在的SDK配置目录内容，用于核对实际模块命名；目录不可读则停止反馈。
2. `dpkg-query -L`检查Icraft包已登记的配置、后端库和头文件路径；找不到包或没有相关文件时反馈，不能据此自动安装。
3. 最后一条查询软件包版本/架构/安装状态，并同时筛选CustomOp；引号内的`${...}`是dpkg格式占位，
   应完整保留，不改为双引号让PowerShell展开。预期相关包为arm64/3.39.0并显示install ok installed；异常先讨论。

提交这三条输出后，讨论是否需要构建配置适配、缺包补齐或不同Host参考入口。
当前不能把`/usr/cmake`直接填入构建脚本继续C：脚本依赖的ZG330配置尚未找到。
ORT安装和Windows编译环境的选择均需另行具体讨论，不自动更换执行平台或依赖。
这次仅完成部分环境查询，不是编译、SDK初始化或混合推理验收。

## 后续Windows编译工具定位（2026-10-05）

不确定安装情况，代理只读找到VS 2022 Community目录
`D:\Visual Studio\ Visual Studio 2022\Community`及MSVC14.44.35207 cl/link/nmake、头文件/库、VsDevCmd.bat和CMake。
目录名` Visual Studio 2022`开头有一个空格。CMake文件元数据3.31.6-msvc6；并未运行查询或编译。
默认vswhere及常见Windows Kits注册表入口未找到/未返回记录，不能据此确诊SDK缺失或安装完整。
下一步仅临时进入x64开发CMD查工具/SDK，命令见[WINDOWS-HOST-ENV-CHECK.md](WINDOWS-HOST-ENV-CHECK.md)，
静态证据`evidence/windows-host-tool-discovery-20261005.json`（历史附件，当前仓库未附）。
安装、修复、新生成器、Host构建或模型执行未进行；ORT缺失保持，后续依赖方案另行讨论。
本文件早期“ZG配置未找到/不能构建”的状态已由后续完整SDK清单及实际交叉构建更新，最新见STATUS.md。
