# CPU算子注册与最小适配：批准范围及源码交付（2026-10-05）

**旧链入口（2026-10-29）：** 本页属于早期 pose-v1 诊断／验证，当前部署从[最终进度](../../PROJECT-PROGRESS.md)进入；旧主机路径、板端目录、算子计数与阶段授权不能套用最新演示。

**2026-10-06最终：独立CPU候选门检通过。** 完成构建、Lite测试及回传；
107例和12条注册记录经核验，22份输出/59,600个FP32值与NumPy参考逐位一致，
五个缺失节点注册前向通过、原Gather保持。见[最终结果](CPU-ADAPTER-RESULTS-20261006.md)。
适用范围仍为固定FP32、全有效分布及Host CPTR内存，正式推理器未接入、mixed未验收；
下面未执行/待回传文字是开发过程历史，勿据此重跑。

2026-10-06最新结果：r2新包/交叉编译已完成并经[evidence复核](evidence/cpu-adapter-r2-build-review-20261006.json)，
源码/SDK/程序/包身份匹配，281项数据参考及辅助文件不变；ARM程序编译链接通过。
仅构建验收，板端加载及107例CPU数值尚未运行；当前从[命令C](CPU-ADAPTER-COMMANDS.md)开始，
不重复A/B、不直接进入mixed。以下未编译文字保留为历史状态。

2026-10-06最新：r1的SDK审计/CMake配置通过，C++编译未完成；已修正检查器三处
Array API及PowerShell原生stderr日志捕获，旧记录保留。新包/新r2构建尚未执行，
从[更新命令A/B](CPU-ADAPTER-COMMANDS.md)开始，源码身份变化须新包，
此前“无需重做A”仅针对未改C++的上一步审计修正。完整前向和mixed仍未验收。

2026-10-06更新：已生成107用例测试包（实际`package/20261005`），282项哈希复核匹配；
原构建因容器PATH找不到python3在SDK审计停止，未开始CMake配置/C++编译。
并应用[构建审计修正](CPU-ADAPTER-BUILD-FIX-20261006.md)，SDK门禁保持、原记录保留。
直接按[命令B](CPU-ADAPTER-COMMANDS.md)以新标签构建，测试包无需重做；修正版编译与CPU前向尚未运行。
下面“没有生成测试包”等描述为初始源码交付状态，不代表后续已生成产物缺失。

应用侧最小验证方案。当前仅完成源码、构建/测试脚本、命令和静态审查；
没有生成测试包、交叉编译、运行算子、连接Lite或加载候选。执行入口：
[CPU-ADAPTER-COMMANDS.md](CPU-ADAPTER-COMMANDS.md)。一般软件操作仍人工执行。

## 原始证据与资料整合

- 板端注册探针：[HOST-REGISTRY-RESULTS-20261005.md](HOST-REGISTRY-RESULTS-20261005.md)。
  TopK 188/437、GatherElements 192、ScatterND 582/649没有init/forward；Gather 442已有注册。
  优化图的Matmul也缺注册，但正式ZG图没有CPU Matmul，不改变其NPU分配。
- 原始ARM包：`Icraft_3.39.0_onchip.deb`，SHA256
  `aa24f938566d8892d262bc87bac8048bb8b41c4e4199870debf96b5cc4615ab3`。
  包清单证据：`evidence/original-arm-host-package-review-20261005.json`。
- 包内`hostbackend/port/common/hostbackend_impl.h`第369/373/375行分别注册
  GatherElements/TopK/ScatterND；`tensor_ops.h`第1579/1674/1836行提供明文前向包装，
  `hostbackend/common/tensor_kernel.h`第5668/6140/6425行提供inline数学内核。
  本机六份关键头文件与原始ARM包按LF规范化后相同，固定哈希在`cpu_adapter_gate.py`。
  本机SDK入口`C:/Icraft/CLI v3.39.0/include`；Windows原始字节哈希不同只是CRLF差异。
- 注册API在`icraft-xrt/core/backend.h`：`BackendOpRegistry::Register(..., can_override=false)`、
  `BackendOpRegisterHelper`、`ICRAFT_ADD_OP_TO_BACKEND`。`hostbackend/backend.h`还有目标分派层
  `ICRAFT_ADD_HOSTBKND_OP`。本候选选择前者，在main阶段显式注册现有XIR类型，不新增XIR类型。
- `docs/extensibility/customop.html`和`docs/demo/samples/customop/softop.html`可参考注册流程；
  部分示例forward签名较旧，实际以3.39.0头文件的四参数ABI为准。
  `icraft-utils/dll.h`中的`ICRAFT_CUSTOM_DIR`搜索按type_key加载库，不能据此认定已知标准算子的
  缺失后端函数会自动补齐。本候选不扫描插件、不改该环境变量。
- 原CustomOp ARM包提供DetPost、DetPostZG、GridSample、ImageMake、NearestUpsample、SegPost、WarpAffine，
  未提供三类缺失标准算子的独立so；不能将重新安装CustomOp视为已证实的修复。

## 布局限制与具体处理

原内核明确拒绝任何非空`distributions`。真实ZG图六个Host节点的九项输入声明分别为
完整的180、42、100或3元素有效范围，均为ZERO、没有静态无效元素。
直接照抄完整`hostbackend_impl.h`会同时定义后端方法、注册大量已有算子，并仍遭遇布局拒绝；本候选不这样使用。

新增`software/pose_v1/include/host_cpu_adapter.hpp`、`src/host_cpu_adapter.cpp`和
`src/host_cpu_adapter_check.cpp`。注册前检查原有条目，不覆盖/删除；已有Gather回调类型保持不变，
Matmul注册前后都保持缺失。五个节点的init/forward必须全部可见。

包装器限制为当前模型的FP32、*...C行主序、形状、轴、K=100及ScatterND NONE。
在运行时检查分布轴、掩码长度、全有效性、字节数、声明与实际dtype相等；仅清除临时
`TensorDesc`的冗余分布，不改变XIR或模型文件。拒绝NaN/Inf、不支持的规格、非法索引和错误缓冲区。
索引/K仍使用模型实际的FP32存储，SDK内核负责有限整数和范围核验，不将它们改成另一种模型dtype。

**本阶段仅接受HostDevice内存。** 没有用便携cache helper假定Linux物理/双地址内存自动同步，
也不接受ADDR/NPU内存。后续真实PS/NPU交接需要另行验证同步、复制及输出缓冲区，不因本候选通过而跳过。

## 测试设计与停止条件

`cpu_adapter_gate.py prepare`人工执行，使用已批准NumPy 2.2.5生成固定合成输入和独立参考。
设计107个用例：18个正常用例（含负索引、分配/提供输出缓冲区）、89个异常拒绝；
正常输出共22份，包含TopK同值排序和正/负零的逐位比较。这些是设计数量，尚未生成或运行。

- 缺失算子：从真实图读取声明，替换进程内参数为合成数据，通过实际注册的init/forward回调测试。
- 已有Gather：不注册替代；以仅包含op442的CPU NetworkView在HostDevice上初始化原后端并前向。
  两个用例检查原实现与给定输出缓冲区；若原实现也失败，保存结果讨论，不自动覆盖Gather。
- 异常：非法轴/K、非整数/越界/NaN索引、输入NaN/Inf、FP16、错误形状/布局、非全有效/非法掩码、
  字节/dtype不符、输入数量不符、输出数量/缓冲区不符、sorted=false及非NONE归约。
  只有指定`Rejection`类别才算相应负例通过；SDK异常、崩溃、超时不能冒充通过。
- 模型及六份头文件哈希固定；容器和板端Host so/包版本必须与审计身份一致。
  Linux清单明确LF，禁止覆盖构建、包、运行和复核目录；不自动重试或修复依赖。
- 构建独立CMake目标只链接HostBackend，原推理CMake和检查器保持原SHA256。
  不创建Session、不读取模型RAW、不初始化硬件设备，不访问NPU/DMA/HDMI或启动配置。

通过必须满足程序退出0、stderr空、全部用例和注册记录完整、产物哈希匹配、22份数值输出逐位一致。
完成后由代理审查；CPU候选通过不代表完整模型、NPU、性能或双路输出通过。
Matmul浮点参考与完整推理数值门检仍单独待解决，不自行跳过参考进入mixed。
