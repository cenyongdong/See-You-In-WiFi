# Windows Icraft 独立依赖

**工具目录导航（2026-10-29）：** [全部工具与历史记录](../DOCUMENTATION.md)；当前主链构建／打包在 [pose180_pipeline/tools](../software/pose180_pipeline/tools)，实采服务见 [autostart](../software/pose180_pipeline/resident/autostart/README.md)，模型部署见 [pose180](pose180/STATUS.md)。下文是 Icraft 环境工具说明，旧 MCP 试验不代表当前主链工具选择。

2026-10-01 实施第一阶段：下载两个 NVIDIA 官方 ZIP，建立独立依赖目录和启动器，验证 DLL 加载及 CLI 帮助。当前验证已通过；模型编译、量化、CPU/GPU 推理及 ZG330 实板运行尚未验证。

## 使用

在 PowerShell 中执行：

```powershell
& 'D:\FPGACompetitionProject\tools\Invoke-Icraft.ps1' -IcraftArgs @('--version')
& 'D:\FPGACompetitionProject\tools\Invoke-Icraft.ps1' -IcraftArgs @('run', '--help')
```

后续模型和配置已确认、相应任务已授权时，可指定工作目录并传入组件参数，例如：

```powershell
# model_project 和 model.toml 为占位，当前未创建或运行模型任务。
& 'D:\FPGACompetitionProject\tools\Invoke-Icraft.ps1' `
    -WorkingDirectory 'D:\model_project' `
    -IcraftArgs @('parse', '.\configs\model.toml')
```

启动器固定使用 `C:\Icraft\CLI v3.39.0\bin\icraft.exe`，先校验三个新增 DLL 的 SHA-256，再仅为子进程补充 PATH。参数以数组传入；工作目录决定配置中的相对路径。stdout/stderr 为工具正文，工具退出码通过 `$LASTEXITCODE` 返回；每次调用的参数、工作目录、子进程 PATH 前缀和输出日志写入依赖目录的 `logs`。

## 依赖及证据

- 根目录：`D:\FPGACompetitionProject\.local\icraft-runtime\cuda-11.8.0`。
- cuBLAS `11.11.3.6`：提供 `cublas64_11.dll`、`cublasLt64_11.dll`。
- cuFFT `10.9.0.58`：提供 `cufft64_10.dll`。
- `downloads` 保留原 ZIP；`packages` 保留解压后的厂商目录结构和 LICENSE。
- [官方清单本地副本](../.local/icraft-runtime/cuda-11.8.0/redistrib_11.8.0.json)、[版本/哈希/路径清单](../.local/icraft-runtime/cuda-11.8.0/runtime-manifest.json)、[验证报告](../.local/icraft-runtime/cuda-11.8.0/verification-report.json) 记录来源与结果。
- 测试 PATH 不含 Conda；三个实际加载路径均来自独立目录。12 个库的静态检查及 226 项导入符号检查通过；相关 DLL 加载、直接 CLI 和 Windows PowerShell 5.1 启动器的版本/帮助验证通过。当前 PowerShell 7.6.5 的启动器版本查询也通过。
- 原环境帮助命令 stderr 为 219 字节且有 nvfuser 警告；独立环境和启动器 stderr 均为 0 字节，退出码为 0，帮助正文逐字节一致。
- 原 Icraft 核心文件哈希和用户/系统永久 PATH 在验证前后一致；启动器父进程 PATH 保持不变。

## 准备与复核脚本

`Prepare-IcraftRuntime.py` 使用 Python 3.8+ 标准库下载/校验/解压批准的两个组件，已有清单时拒绝覆盖。当前依赖已经准备好；重新准备、更换版本或修改目录须先讨论具体范围。

`Verify-IcraftRuntime.py` 使用 Python 3.8+ 标准库复核 PE 导入符号、独立进程 DLL 路径、CLI/Windows PowerShell 启动器输出和安装/永久 PATH 一致性。它只进行加载和帮助验证，结果写入依赖目录。执行复核时须确保 Python 来自已知环境；本次使用 Codex 随附 Python，未激活训练环境。

停用启动器即可停止使用这些补充路径。独立依赖目录目前约 1.40 GiB；删除目录、更换组件、加入新依赖或验证正式模型均需相应授权。具体背景及适配边界见 [REFERENCES.md](../REFERENCES.md) I4、I5；CUDA 11.8 仍是实测加载通过的补充组合，尚无 Icraft 厂商完整兼容矩阵。

## FPGA MCP 入口（2026-10-01）

实现并验证限定流水灯工程的 [Procise MCP 首版](D:/FPGACompetitionProject/tools/procise_mcp/README.md)。独立 stdio 客户端及 [项目 MCP 配置](D:/FPGACompetitionProject/.codex/config.toml) 读取均通过；随后自行重载两个服务，当前工具会话 Procise 七工具和 LED1→3→2→4 新灯序的仿真→位流复核也已通过。新位流随后已确定，经 Procise 原生脚本下载并通过现场观察；服务仍无 JTAG/任意 Tcl 工具。

Vivado MCP 的参考解析与 2019.1 XSim 辅助通过；长期配置已获批准增加 AMD64，重载后的当前工具会话已直接启动并驱动新灯序仿真，无临时包装器。过程发现 BGN 默认值星号、MCP 正文错误而外层成功、PowerShell UTF-16 日志等适配问题。最新结果及授权边界见 [新灯序协作验证](D:/FPGACompetitionProject/tools/mcp-validation/led1324/RESULTS.md)，历史与长期配置见 [MCP 验证记录](D:/FPGACompetitionProject/tools/mcp-validation/RESULTS.md)。
