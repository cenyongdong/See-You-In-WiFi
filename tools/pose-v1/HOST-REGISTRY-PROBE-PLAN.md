# Host注册探针方案（2026-10-05，已批准并执行）

**旧链入口（2026-10-29）：** 本页属于早期 pose-v1 诊断／验证，当前部署从[最终进度](../../PROJECT-PROGRESS.md)进入；旧主机路径、板端目录、算子计数与阶段授权不能套用最新演示。

明确“同意你进行”，代理按本范围完成编译、传板及一次30秒受限注册查询。
探针退出码0、stderr空、回传哈希通过；Matmul及ZG六个Host节点中的五个缺注册，Gather有注册。
完整结果HOST-REGISTRY-RESULTS-20261005.md及evidence/host-registry-20261005/review.json。
下述为批准前形成的方案及范围记录；新诊断/修复仍先讨论，不因本次通过自动扩大授权。

## 已完成的只读审计

代理获本轮特殊问题协助权限及只读审计批准后，直接SSH到Lite读取包、Host库和CMake配置。
Icraft/CustomOp均arm64 3.39.0、install ok installed；dpkg -V icraft:arm64无差异输出、退出码0。
Host库最终路径/usr/lib/aarch64-linux-gnu/libicraft_hostbackend.so，SHA256为
d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130，
与原始Icraft_3.39.0_onchip.deb内库一致。原包库大小20,672,776字节。
原包和板端CMake导出HostBackend及CudaDefault，HostBackend的接口依赖XRT、rt、dl及CudaDefault，
两个库的安装路径都有明确导出。readelf存在于/usr/bin/readelf。
日志board-host-library-audit-20261005.stdout.log/.stderr.log/transport-exit.txt保存在evidence；
最终SSH退出码0、stderr为空、所有审计步骤退出码0。
初次免密失败；首次密码会话的自动HostKeys写入被权限拒绝、尾部传输产生空行错误，
因此改用UpdateHostKeys=no、LF远程命令取得上述完整日志。没有修改SSH配置、保存口令或安装密钥。

本地原包静态审查：original-arm-host-package-review-20261005.json。
Host库可打印字符串仅见MNN内部Matmul线索，未找到icraft::xir::MatmulNode完整字面量；
这只是注册缺失的线索，字符串存在/缺失都不能单独证明运行时算子支持。
当前不支持“板端Host库损坏/被另一份替换”的判断；深层注册/加载原因仍待核验。

## 拟执行范围

1. 独立探针源码及CMake候选仅放tools/pose-v1，不修改software/pose_v1、原二进制、模型或板端库。
2. 经批准后在现有FPAI内复制到新的ASCII临时目录，使用已核验GCC9.4、/usr/cmake及原ARM SDK交叉编译。
   保存源码、编译日志和二进制SHA256；编译失败即停止，不更换编译器、SDK、链接选项或算子实现。
3. 把单个探针传至现有/tmp/pose-v1-inference-20261005下的新子目录host-registry-audit-20261005；
   子目录/本机证据目录若已存在即停止，不覆盖此前结果。
4. 以原有package/models/piw24_optimized.json和piw24_ZG.json为输入运行一次，外部timeout上限30秒、TERM后5秒KILL。
   只创建HostBackend对象并读取isOpSupported/getInitFunc/getForwardFunc返回，
   查optimized op1 Matmul及ZG六个Host计算算子188/192/437/442/582/649。
5. 保存JSONL/stdout/stderr、退出码、程序/输入/库身份；诊断不作数值验收。

不创建Session，不调用backend.init/initOp/forwardOp或Tensor前向，不读取RAW权重、
不调用Device::Open/复位/寄存器，不运行模型或触碰HDMI/DMA；不安装依赖、不改BOOT或模型。
源码已按本机3.39.0头文件静态审查，尚未编译或运行，不称为探针通过。

候选文件host-registry-probe.candidate.cpp和host-registry-probe-CMakeLists.candidate.txt。
可由代理执行这项已批准范围的诊断，过程/结果向记录说明；
一般软件开发执行仍人工完成。当前只读审计批准不自动授权本新探针编译/运行。

## 结果如何使用

- Matmul无注册、ZG六个Host算子有注册：说明本SDK运行环境的全CPU参考与混合图Host部分能力不同；
  后续讨论转用其他主机Host参考的具体环境方案。不能据此断言六个算子的前向或NPU已通过。
- Matmul探针有注册、原会话仍无法绑定：进一步讨论原应用加载、目标条件/ABI或会话绑定差异；
  不立即修改链接或注册设置。
- 六个Host算子也有缺失：提交具体算子及证据，讨论SDK/模型配套，停止推进mixed。
- 异常/超时/缺少目标节点：保存诊断并停止，不自动重跑、注册替代算子或扩大探针。

所有后续修复/依赖安装/平台变更仍先讨论批准；正式NPU、双路及数值门检要求保持。
