# 本机工具路径与调用方法（历史资料）

迁出日期：2026-10-13。下列原文来自整理前AGENTS.md第345行起，路径/工具状态以原核对日期为准，使用前依现行规范重新核验；命令示例不是执行授权。现行资料入口见[REFERENCES](../../../REFERENCES.md)。

## 本机工具路径与调用方法

以下路径于 2026-10-01 核对。命令示例使用 Windows PowerShell；带引号的可执行文件路径须用 `&` 调用。构建目录、Tcl/TOML、模型和输入文件必须换成已确认的实际文件；下面的 `example`、`path_to_confirm` 均为占位示例，本次未创建这些目录或执行构建。详细资料索引见 `REFERENCES.md` 第 5、6 节。

### Procise：FPGA 主开发工具

| 用途 | 本机路径 |
| --- | --- |
| 安装根目录 | `C:\FudanMicro\Procise` |
| GUI 启动器 | `C:\FudanMicro\Procise\procise_launch.exe` |
| Shell 启动器 | `C:\FudanMicro\Procise\procise_sh_launch.exe` |
| Tcl 执行程序 | `C:\FudanMicro\Procise\bin\procise.exe` |
| 编程下载工具程序 | `C:\FudanMicro\Procise\bin\procise_jtag.exe` |
| /约束/IP 等手册 | `C:\FudanMicro\Procise\documents` |
| Tcl 命令查找线索 | `C:\FudanMicro\Procise\conf\commands_*.xml` |

按需要选择一个启动器：

```powershell
& 'C:\FudanMicro\Procise\procise_launch.exe'
& 'C:\FudanMicro\Procise\procise_sh_launch.exe'
```

在 **Procise Shell 的 Tcl 提示符**中执行脚本，可使用 `source {D:/fpga_work/example/build.tcl}`；这不是 PowerShell 命令。工程路径不支持中文，后续需要构建工作副本时，按既有歧义处理规范先讨论路径布局并记录源码来源。

直接批处理调用 `bin\procise.exe` 时，需要为当前进程配置运行环境。下例依据本机手册及参考区 `FPGA_LED_Wujing_Full\build.ps1` 的调用方式整理；该参考工程是历史脚本依据，不能直接复用其板级引脚约束：

```powershell
$prociseRoot = 'C:\FudanMicro\Procise'
$prociseBuildDir = 'D:\fpga_work\example' # 替换为已确认、已存在的工作目录
$env:PATH = (Join-Path $prociseRoot 'dll') + ';' + $env:PATH
$env:APP_DIR = $prociseRoot
$env:TCL_LIBRARY = Join-Path $prociseRoot 'tcl8.4'
$env:ICTIME_HOME = $prociseRoot
$env:FMSH_DB = Join-Path $prociseRoot 'db'
$prociseJob = Start-Process `
    -FilePath (Join-Path $prociseRoot 'bin\procise.exe') `
    -ArgumentList 'build.tcl' `
    -WorkingDirectory $prociseBuildDir `
    -WindowStyle Hidden -PassThru -Wait `
    -RedirectStandardOutput (Join-Path $prociseBuildDir 'procise.stdout.log') `
    -RedirectStandardError (Join-Path $prociseBuildDir 'procise.stderr.log')
if ($prociseJob.ExitCode -ne 0) { throw 'Procise 返回失败，请检查构建日志。' }
```

这里修改的是当前 PowerShell 进程及其子进程的环境，不是系统永久环境。`build.tcl` 应位于工作目录；退出码还须结合日志、预期产物及报告检查，不能只凭退出码或位流存在宣布实现/时序通过。

原生 Procise **简单 RTL 工程**的 Tcl 流程示例（文件和顶层均为占位）：

```tcl
create_project -name example -device JFMQL30TAI676H
add_design_file -file example_top.v example_top.fdc
set_top -top example_top
save_project
load_design -stage_elaborate -no_hier
launch_run -stage bitstream
exit
```

- `save_project` 会将运行目录切换到 `rundir`；预期位流和报告应按实际脚本/工程设置查找，并保留日志。跨不同工程时，手册建议重新启动 Procise Shell。
- 本次实测 `launch_run` 完成后返回工程根目录；后续重新 `bitgen` 前须显式切换到 `rundir`，防止同名文件写到不同目录。流水灯脚本已按批准方案处理，`ReviewBuild.py` 核对最终报告、INIT、引脚、电平及文件哈希；当前已确认的 ASCII 工程目录是 `D:\FPGACompetitionProject\FPGA\lite_led_chaser`。
- Procise 使用 `launch_run -stage ...`；不能直接套用 Vivado 的 `launch_runs` 或 `vivado -mode batch -source ...`。上例也不能替代含 PS/AI、BD、网表或 JFM 迁移步骤的系统工程流程；这类工程须先查 `REFERENCES.md` D1–D5，再核对 IP、约束和专用步骤。
- 下载与在线调试按本机《编程下载工具使用手册》《Procise在线调试手册》操作。Alinx 下载器已能识别芯片，但品牌名称不能直接推定 Tcl 的 `cable_type` 参数；使用前核对工具实际识别结果。
- 本次实测 Alinx 下载器显示为 `DIGILENT/JTAG-HS1`，序列号 `210512180081`；当前 Procise 的 `init_chain` 接受 `-cable_type usb-jtag-hs1`，大写显示名返回参数错误。链中 `jfmql30` 为 part 0（IDCODE `0x9372c093`），`ps_dap` 为 part 1。已验证 `program_bit {已复核位流绝对路径} -part 0` 与 `read_reg -part 0 -reg STAT -read`；重连、换板/下载器或链变化时须重新扫链核对，不能永久假设目标总为 0。

### Icraft：AI 模型编译与运行工具

| 用途 | 本机路径 |
| --- | --- |
| 安装根目录 | `C:\Icraft` |
| 当前版本目录 | `C:\Icraft\CLI v3.39.0` |
| 当前版本链接 | `C:\Icraft\CLI`（本机符号链接指向 `CLI v3.39.0`） |
| CLI 程序 | `C:\Icraft\CLI v3.39.0\bin\icraft.exe` |
| 组件与组合命令配置 | `C:\Icraft\CLI v3.39.0\bin`、其中的 `comb.toml` |
| 本地文档 | `C:\Icraft\CLI v3.39.0\docs` |
| 自定义算子资料 | `C:\Icraft\CustomOp_v3.39.0` |

优先明确版本目录，并把该版本 `bin` 放到当前进程 PATH 首部：CLI 会通过 PATH 查找 `icraft-parse` 等子程序，仅写主程序绝对路径仍不足以保证子程序版本一致。初始化、版本和帮助查询：

```powershell
$icraftRoot = 'C:\Icraft\CLI v3.39.0'
$icraftBin = Join-Path $icraftRoot 'bin'
$icraftExe = Join-Path $icraftBin 'icraft.exe'
$env:PATH = $icraftBin + ';' + $env:PATH
& $icraftExe --version
& $icraftExe --help
& $icraftExe parse --help # 其他组件可用 optimize/quantize/adapt/generate/run 等替换
& $icraftExe docs         # 按需要打开本地文档
```

本次实际查询得到 Icraft `3.39.0`、CLI `3.39.0.0-431be90(2608211646)`；`Get-Command icraft` 当前也指向 `C:\Icraft\CLI\bin\icraft.exe`。后续应重新查询，不能假设链接/PATH 永远不变；不要通过带版本参数的 `--version` 调用擅自切换已确认基线。

命令格式为 `icraft <command> [config.toml] [--key value] [--dry_run]`。TOML 须紧跟命令名；单组件读取与命令同名的小节，命令行同名参数覆盖配置文件。模型相关路径若为相对路径，应从配置约定的工程工作目录执行，而不能假设它们相对 TOML 所在目录。

模型、输入规格、校准数据和配置已讨论确定后，可使用以下方式；当前阶段不据此创建模型配置：

```powershell
Push-Location -LiteralPath 'D:\path_to_confirm\model_project'
try {
    $icraftConfig = '.\configs\model.toml' # 占位；替换为已核对的 TOML
    & $icraftExe compile $icraftConfig --dry_run # 先打印命令；不执行编译
    & $icraftExe compile $icraftConfig           # 完整编译
    # 分步诊断时依次使用以下命令，选择完整或分步流程即可：
    # & $icraftExe parse $icraftConfig
    # & $icraftExe optimize $icraftConfig
    # & $icraftExe quantize $icraftConfig
    # & $icraftExe adapt $icraftConfig
    # & $icraftExe generate $icraftConfig
    # & $icraftExe run $icraftConfig # 须另行核对 [run]、输入和后端/设备条件
} finally {
    Pop-Location
}
```

- 本机 `comb.toml` 确认 `compile` 顺序是 `parse → optimize → quantize → adapt → generate`。实际分步脚本须检查每一步退出码和日志，失败即停止，不继续使用旧产物。保留成对 JSON/RAW、TOML、工具版本及日志。
- 悟净 Lite/30TAI 查 ZHUGE/ZG330 文档；本机 `parse --help` 的默认 target 是 `Buyi`，因此必须显式核对配置中的 `target = "zhuge"` 及后续适配/生成参数。不得将图像示例的形状、预处理或量化参数直接用于 Wi-Fi CSI。
- `run` 的 Host 验证与 ZG330 实板运行需分别配置；板端运行时、位流、服务、设备地址及输入未确定时，只记录命令形式，不自行填入。帮助输出成功不代表模型编译或板端部署已验证。
- Icraft 警告诊断（2026-10-01）：CLI 与直接调用 `icraft-run.exe --help` 均出现 `nvfuser_codegen_ic.dll` 加载警告，帮助正常输出且退出码均为 0。被点名的 DLL 实际存在；PE 导入依赖链中 `torch_cuda_ic.dll` 需要 `cufft64_10.dll`、`cublas64_11.dll`，`cusolver64_11.dll` 还需要 `cublasLt64_11.dll`，这三者在 Icraft bin 与当前搜索路径中缺失；直接加载相关现有库返回错误 126。
- 的临时验证（2026-10-01）：仅在独立子进程中将 Icraft 3.39.0 bin 和 `C:\Users\cenyongdong\miniconda3\envs\koala\Lib\site-packages\torch\lib` 依次放到 PATH 首部，再执行 `icraft run --help`。该 Conda 环境的 PyTorch 为 `2.1.2+cu118`，包含上述缺失库；加入路径后警告消失、stderr 为 0 字节、退出码为 0，帮助正文与原环境逐字节一致。由此确认当前警告与 CUDA 依赖库的可发现性有关；本次只验证帮助命令级加载，未验证模型、Host/CUDA 推理或实板兼容性，未实施长期修复。后续复制 DLL、永久修改 PATH、安装 CUDA、更换 Icraft/PyTorch 或采用长期启动配置，均须先讨论并获得；不得将此次临时验证的同意扩展为这些操作的授权。

命令依据：[Procise 用户使用手册](C:/FudanMicro/Procise/documents/Procise用户使用手册.pdf) 第四节；Icraft 本地 [CLI](<C:/Icraft/CLI v3.39.0/docs/cli/index.html>)、[编译](<C:/Icraft/CLI v3.39.0/docs/start/compilation.html>)、[命令行参数](<C:/Icraft/CLI v3.39.0/docs/interface/cli_arguments.html>)；以及版本/帮助查询和实测记录。Icraft 独立组件与启动器第一阶段验证见 `REFERENCES.md` I5；Procise 原 LED1→2→3→4 流水灯构建及 JTAG 下载见第 13 节和 `Done.md`。模型编译/推理与 AI 系统部署仍未验证；MCP 独立客户端、长期配置及当前工具会话新灯序仿真→Procise 位流复核的状态见第 14 节、14.1、14.2。当前源码为 LED1→3→2→4，新位流随后下载并通过实板观察，见 14.3。
