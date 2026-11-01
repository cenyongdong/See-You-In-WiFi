# CPU算子注册与最小适配：Lite验收结果（2026-10-06）

**已批准的独立CPU候选门检通过。** 人工操作交叉编译、传输和Lite测试，
代理直接读取回传文件并独立核验；未重跑程序、连接板端或接入正式推理器。
这不代表完整PS/NPU混合推理、实时CSI、性能或双路显示通过。

## 工程内容总结

平台为悟净Lite、ARM Icraft/CustomOp3.39.0，FPAI GCC9.4.0/CMake3.24.2。
独立程序包含应用侧TopK/GatherElements/ScatterND注册与原SDK明文数学内核的受限包装，
已有Gather保持原后端；未补CPU Matmul、不改模型/权重/SDK/BOOT或原推理检查器。
注册模块只接受固定模型的FP32规格、HostDevice CPTR内存、全有效ZERO分布，
仅清除临时TensorDesc的冗余分布信息，原XIR声明保持。

| 节点 | 算子 | 注册前init/forward | 注册后init/forward | 实际规格前向 |
| --- | --- | --- | --- | --- |
| 188、437 | TopK | 均缺失 | 均可见 | 两种形状/轴、同值排序、FP32 K与索引、输出缓冲区通过 |
| 192 | GatherElements | 缺失 | 可见 | 原形状、FP32索引/负索引、输出缓冲区通过 |
| 582、649 | ScatterND | 均缺失 | 均可见 | 原形状、参数索引、NONE归约、负索引/缓冲区通过 |
| 442 | Gather | 已有 | 保持已有 | 调用原后端的两种输出缓冲区用例通过 |

- 107个实际用例：18个正常、89个异常拒绝，记录顺序/节点/拒绝类别与固定清单一致。
- 22份输出，共59,600个float32值，与独立NumPy参考逐位一致，最大绝对误差0；全部有限。
  TopK索引精确一致，逐字节核对也包含带符号零。
- 12条注册前后记录匹配；测试程序成功结束也通过原Gather回调类型保留和CPU Matmul未新增的内部检查。
- 新包282项、回传40项文件哈希全部匹配；新旧281项数据/参考/辅助文件一致。
- 板端程序、模型、Host库与已验收构建及原包身份一致，六份头文件与3.39.0版本门禁通过。
- 脚本及程序退出0、stderr为0字节；板端ldd依赖均解析，无ZG/AIU依赖项。
- 提交的运行前后dmesg尾部逐字节相同；内存available快照748→746 MiB、Swap0。
  未测峰值内存或完整模型内存，不能据此宣布性能/稳定性通过。

程序SHA256：`8cf2017cedf6a97f98ce485d979239b659291f3c91d3a3d550382c1c94588622`。
模型SHA256：`75ffdc37b93dcb4913678991d6e7cf5cd0ab09c59653224d07c7434345acb8a0`。
Host库SHA256：`d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130`。

证据入口：

- [代理独立核验](evidence/cpu-adapter-independent-review-20261006.json)：哈希、注册、107用例和每份实际输出身份。
- [文件复核](evidence/cpu-adapter-20261005-review.json)：22输出逐位比较及统计。
- [完整回传目录](evidence/cpu-adapter-20261005-return)：registry/cases/summary、输出、SDK、ldd、包校验、内核及内存日志。
- [构建复核](evidence/cpu-adapter-r2-build-review-20261006.json)：来源、ELF、SDK及新旧固定包对照。

Windows文件复核命令首次因换行被拆开，报`--results`缺参数和独立`--output`解析错误；
之后完整命令成功，实际review.json已生成并与代理核验一致。这是主机命令输入问题，未导致板端程序重跑，
无需因前两条命令错误重新执行CPU测试。

## 对后续开发的参考

已证明应用注册与原SDK明文内核在当前Host内存/规格/全有效分布条件下可工作，
无需安装额外插件或覆盖原Gather。SDK公开算子列表、包安装和注册可见性都不能代替实际前向数值检查。
可复用原包身份固定、独立合成参考、精确异常拒绝、给定输出缓冲区及回传逐文件核验流程。

候选尚未接入正式推理检查器。真实NPU缓冲区类型、缓存同步、复制/零拷贝与原图内存规划未验证；
不能把CPTR内存测试推广到ADDR/BOTH或非全有效分布，也不能直接跳过完整模型Session门检。
正式ZG模型Matmul保持NPU分配；optimized全CPU数值参考的Matmul注册缺口仍单独待解决。
后续应讨论推理器接入、PS/NPU实际数据交接及完整数值参考，明确方案获批准后执行。
本阶段没有Device::Open、NPU/DMA/HDMI计算，未验证更新率、延迟或30分钟闭环。
