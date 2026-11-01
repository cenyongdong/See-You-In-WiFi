# Lite Host参考绑定失败审查（2026-10-05）

## 工程内容总结：已验证的失败范围

在Lite执行现有二进制的host模式，optimized JSON/RAW及原三份输入；退出码1。
原始日志仍在板上，当前代理依据截图及本地源码/模型静态审查，未代执行软件、重跑或修复。
截图依次为evidence/lite-host-binding-failure-20261005-1.png、-2.png、-3.png。

stderr核心错误：

```text
Check failed: (is_bound) is false
Op is NOT bound to any backend, op_id = 1, type_key = icraft::xir::MatmulNode
```

调用栈来自Session::Create<HostBackend> → Session::bindToBackendsByOrder，SDK报告session.cpp第255行。
stages为started → inputs_validated_before_device_access → parameters_loaded → failed_stop_no_retry。
run-config为mode=host、device_init_allowed=false，graph/raw指向piw24_optimized；输出目录仅failure.json、graph-io.json、run-config.json和stages.jsonl，stdout为空。
源码parameters_loaded标记对应lazyLoadParamsFromFile返回，不能作为全部权重已物化/数值通过的证据。
会话创建失败，尚未进入三个样本的前向计算。没有NPU Device::Open或DMA执行证据。

模型中op_id=1是float32 Matmul，目标@hostt：输入[1,180,60]与权重[1,60,256]，输出[1,180,256]。
ZG图的六个Host计算算子为188 TopK、192 GatherElements、437 TopK、442 Gather、582/649 ScatterND；
不能因全模型Host缺少Matmul绑定就断言ZG混合推理也失败，也不能跳过参考直接将mixed记为通过。

截图还出现读取错误路径：stdout.log应在工作目录下，以host-reference-20261005.stdout.log命名；
stages.jsonl应有完整.jsonl后缀。这些读取路径错误与SDK的Matmul绑定失败是两件事。
截图显示先查询目标目录不存在，随后再次执行同一命令；本次可审查的产物就是随后展示的失败记录，
不将其自动视为此前退出码截图的未覆盖原始日志，也不继续重跑。

内核尾部止于启动阶段约11.66秒，未见本次OOM/总线错误；free显示total=993、available=687 MiB、Swap=0。
这不是300秒timeout终止的证据，已知直接失败点是SDK绑定检查；不能凭退出后的可用内存证明没有任何瞬时内存问题。
EXT4恢复和journal异常关闭消息仍属启动上下文，不据此修复文件系统。

## 对后续开发的参考

本机3.39.0的docs/hostbackend/index.html（约948–1055行）将Matmul列为CPU支持。
该说明不足以保证当前板端ARM二进制有相同算子实现、注册集合或依赖加载方式。
已有二进制声明并实际解析到libicraft_hostbackend.so，不能把本次错误简单解释为整份Host库没链接。
安装CustomOp并不自动保证标准Matmul注册成功；本次没有足够证据认定缺少某一个CustomOp插件。

当前结论：本次ARM Host运行环境没有为该Matmul成功提供可绑定后端；深层原因仍待包身份、
依赖/注册检查。可能涉及板端库构建范围、依赖/注册或版本/文件身份差异，不能直接宣布ARM绝对不支持。
不要手写Matmul替代、改模型、借其他环境、复制库、调整Swap/线程或重跑原目录。

## 只读库身份与依赖审计（、代理已完成）

本轮授予特殊问题直接工具协助权限，并批准该审计；代理已直接SSH完成只读查询。
板端Icraft/CustomOp为arm64 3.39.0、安装状态正常；dpkg -V icraft:arm64无差异输出、退出码0。
Host实际库SHA256 d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130，
与原始onchip安装包一致。CMake依赖声明含CudaDefault，readelf查询成功。
最终审计SSH退出码0、stderr空，证据evidence/board-host-library-audit-20261005.stdout.log及同前缀其他记录。
本地原包静态审查evidence/original-arm-host-package-review-20261005.json。
不支持“Host库损坏/被替换”判断，注册及实际支持范围仍待核验；未执行模型或修复环境。
后续独立CPU注册探针已获批准并执行，见HOST-REGISTRY-RESULTS-20261005.md。
Matmul无init/forward注册；ZG六个Host节点中的TopK/GatherElements/ScatterND共五个也无注册，只有Gather有注册。
当前混合推理存在实际Host注册阻断，停止mixed；未前向计算或判定NPU硬件失败。
以下为已执行的审计范围记录：

目的：确认板端已安装库是否有包校验差异，并检查Host后端的导出配置和依赖线索。
不执行模型、创建Session、访问NPU/寄存器、安装依赖或修改配置；本轮按特殊问题权限由代理在Lite SSH执行。
只读结果无法完整证明运行时算子注册，但能缩小下一步诊断范围。

```bash
cd /tmp/pose-v1-inference-20261005
dpkg-query -W -f='${Package} ${Architecture} ${Version} ${Status}\n' icraft:arm64 customop:arm64
dpkg -V icraft:arm64
dpkg-query -L icraft:arm64 | grep -E 'hostbackend|cuda|matmul'
readlink -f /lib/aarch64-linux-gnu/libicraft_hostbackend.so
sha256sum /lib/aarch64-linux-gnu/libicraft_hostbackend.so
cat /usr/cmake/icraft-hostbackend-targets-aarch64.cmake
cat /usr/cmake/icraft-hostbackend-targets-aarch64-release.cmake
command -v readelf
```

- dpkg-query读取包版本/文件列表；目标包名来自此前查询。包找不到即提交提示，不改用猜测包名。
- dpkg -V仅读取已登记文件做校验；无输出仅表示未报告其可检查项目的差异，不证明注册或算子支持。
- readlink/sha256sum记录此前ldd解析到的Host库最终路径和内容身份。
- 两份CMake文件读取实际导出目标/依赖/库路径，缺失先报告，不复制Windows配置。
- command -v只查询readelf是否存在；本轮不安装它。
- 所有输出提交审查；异常不自动修复。若需下一阶段导出依赖分析、C++算子注册探针或改参考平台，另交具体方案批准。

正式NPU/双路验收标准保持。Windows Host路线仍受Windows SDK未识别约束；ONNX Runtime预览/安装未批准。
