# Lite Host注册探针结果（2026-10-05）

## 工程内容总结

HOST-REGISTRY-PROBE-PLAN.md及特殊问题代理工具协助权限后，代理完成独立探针交叉编译、
传板、一次受限运行及回传复核。平台悟净Lite，FPAI GCC9.4.0/CMake3.24.2、ARM Icraft/CustomOp3.39.0。
原software/pose_v1源码、原推理二进制、optimized/ZG模型和SDK未修改。

探针仅以HostBackend::Init创建CPU后端对象，查询指定算子的isOpSupported、getInitFunc、getForwardFunc；
不创建Session、不初始化/前向算子、不读RAW、不调用Device::Open/寄存器/DMA，不执行模型或显示。
编译目标只链接Icraft::HostBackend及其导出依赖，没有ZG330后端。

本机构建.local/pose-v1-build/host-registry-20261005，容器/tmp/pose-v1-host-registry-20261005；
初始Docker管道访问被沙箱权限拒绝，保留build.log。经工具权限批准恢复访问，
先核对准备源码哈希，保留新的build-after-docker-access.log，随后完成首次实际编译；无编译修复/重试。
生成AArch64 ELF64 PIE，32,744字节，SHA256
4106daf64086e478b7540788eab52d4551680cb11f8b8b104a4f582d86d6d05c。

板端工作目录/tmp/pose-v1-inference-20261005/host-registry-audit-20261005为新建目录。
传输前optimized/ZG JSON和Host库SHA256与锁定身份一致；传输后探针SHA256匹配。
以30秒timeout、TERM后5秒KILL运行一次，探针退出码0、stderr为空，无超时。
回传5项产物逐文件SHA256匹配；成功完成的是注册诊断，不是模型推理验收。

| 图及节点 | 算子 | isOpSupported | init注册 | forward注册 |
| --- | --- | --- | --- | --- |
| optimized op1 | Matmul | false | false | false |
| ZG op188、437 | TopK | false | false | false |
| ZG op192 | GatherElements | false | false | false |
| ZG op442 | Gather | true | true | true |
| ZG op582、649 | ScatterND | false | false | false |

证据目录tools/pose-v1/evidence/host-registry-20261005：
- review.json：结构化结果、版本、源/二进制哈希及5项回传校验。
- board-return/run.stdout.jsonl、run.stderr.log、probe.exit.txt：板端原始结果。
- board-return/input-identities.sha256、files.sha256：程序、图/Host库身份及回传清单。
- preflight、transfer、run-transport、return各组stdout/stderr/exit：流程记录。

原推理程序仍SHA256 d1006f9bd78050ffa484c64bf74fb62542d270c7acca5068e9da611a5bdc05e5，
原核心源码SHA256 75e51aff69c61ed431e0201aa21b10463b43add17c0ad125739f8dd252accf6d。
Host库与原始安装包相同的既有证据保留：d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130。
没有保存SSH口令、安装密钥或更改SSH配置；本次使用StrictHostKeyChecking=yes、UpdateHostKeys=no。

## 对后续开发的参考

### Matmul的参考路径与正式部署路径澄清

问题为何ZG支持Matmul却放CPU。静态复核现有模型：optimized图有130个Matmul，
该图用于全CPU浮点数值参考；quantized图130个Matmul均为@zhuget(330)，包括op1。
adapted图132个Matmul也均为@zhuget(330)，最终ZG图以HardOp表示硬件指令，
其@hostt计算节点只有前述六个（另有Input/Output标记），没有CPU Matmul节点。
因此此次host模式是独立数值参考，不是把正式部署Matmul迁到CPU；
Matmul在Host无注册不否定ZG330 Matmul支持，正式部署仍走ZG路径。
依据原仓库result/icraft_2024的quantized/adapted/ZG JSON及锁定optimized/ZG图，
这是编译目标静态核对，不是NPU实际执行验收。部署注册阻断仍为TopK/GatherElements/ScatterND。

本次独立程序也查询到Matmul无init/forward注册，支持此前Session绑定失败的直接原因，
而不是仅凭原应用异常猜测。Gather查询有注册，说明不能把全部CPU后端统称为未加载。
但仍不能将“当前进程没有注册”扩大为所有ARM/Icraft版本都不支持这些算子；
是否需要另一个官方注册模块、目标条件或SDK构建配置，仍需进一步说明/证据。
库内MNN字符串不是XIR算子注册证明，包安装成功/库完整也不是算子可用证明。

正式ZG图六个Host计算节点中，五个节点（三类算子）缺注册，故不能只换数值参考平台就认定混合推理畅通。
当前两个阻断分别为全CPU参考Matmul注册缺失，以及混合图PS算子注册缺失；mixed保持停止。
Gather有注册仍未做前向数值测试，NPU本身也未运行；此次没有认定硬件/BOOT故障。

下一阶段应先核对3.39.0 ARM官方算子支持及注册/加载机制，优先寻求与现有SDK/模型配套的方案；
若需加载插件、修改链接、更新SDK或新增算子实现，先提交具体方案、影响和验证办法并获批准。
不重跑原Host、修改模型/BOOT、手写算子替代或将全CPU作为正式部署回退。
原首版NPU、HDMI、RTSP及数值/性能验收条件保持，尚未完成。
