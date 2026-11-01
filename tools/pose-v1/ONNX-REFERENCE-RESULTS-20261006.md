# 三样本ONNX部署参考结果（2026-10-06）

## 工程内容总结

代理创建、安装并运行独立环境。本机新Conda前缀为
`.local/pose-v1-onnx-conda`，Python3.10.21、NumPy2.2.5、onnxruntime1.23.2 CPU预编译wheel；
coloredlogs15.0.1、humanfriendly10.0、flatbuffers25.12.19、protobuf7.36.2、pyreadline3 3.5.6、sympy1.14.0、mpmath1.3.0。
实际依赖与八wheel的下载哈希锁定；pip check、模块来源及DLL导入通过。原预处理/base/koala/Icraft环境未用于安装。
首次离线Conda在沙箱CUDA虚拟包IPC处报WinError5；同一离线创建命令获自动审批后在沙箱外成功，未更改依赖方案。
未使用源码构建。安装来源及版本依据：[PyPI1.23.2](https://pypi.org/project/onnxruntime/1.23.2/)、
[官方CPU安装说明](https://onnxruntime.ai/docs/install/)。

固定CPUExecutionProvider、ORT_SEQUENTIAL、intra/inter线程1、ORT_ENABLE_ALL。
epoch442 ONNX SHA256为`7b04090e374e31e016d5703bbcf1d0a561d0b98f268fde984b0bf0461598bd21`；
原11项三样本包身份核验后，以同一10800 FP32输入得到 `[1,100]`分数、`[1,100,14,3]`姿态。
三帧12,900输出值全有限；首帧再次运行逐位一致；不同输入的完整输出有响应差异。

| 样本 | 帧号 | 前向耗时/ms | 最高分槽位 | 最高分 |
| --- | --- | --- | --- | --- |
| S11_01_308 | 6 | 221.808 | 0 | 0.9451969862 |
| S11_01_309 | 7 | 221.606 | 0 | 0.9754498005 |
| S11_01_310 | 8 | 212.305 | 0 | 0.9581497312 |

耗时仅为本机Windows CPU参考，不是板端吞吐率。输入保留source_time_ns=0，不虚构采集时间。
产物 `.local/pose-v1-mixed-validation/onnx-20261006`含原输入、全部候选、帧记录、环境/设置/耗时及LF哈希清单；
12项产物哈希独立复核通过。安装报告、Conda explicit/list/history、pip freeze和wheel位于
`.local/pose-v1-reference-deps/20261006`。公共归档
[onnx-reference-environment-20261006.json](evidence/onnx-reference-environment-20261006.json)，
[依赖锁定](onnx-reference.requirements.lock)，[参考程序](onnx_reference_v1.py)。

## 对后续开发的参考

这一基线可直接与板端同一原始CSI预处理后的完整输出比较，无需等待Icraft全CPU Matmul注册。
参考通过不证明Icraft模型/NPU或部署精度通过；误差容限仍按实测另议。
三份数据仅验证初始部署，不代表全测试集精度、GT/MPJPE、物理标定或多人匹配质量。
保持固定模型、原始输入、实际运行设置及输出哈希，可在后续查错时区分输入、后端计算和候选槽位变化。
