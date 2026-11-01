# 从零初始化训练 epoch130：180-query 转换候选

> 本页为历史模型记录，仅说明文档纳入 Git；下列本机附件不随克隆提供。当前部署模型见 [模型索引](../README.md)。

**最终选择（2026-10-29）：** 本候选有限实板反馈未确认改善，现行演示使用原 epoch99；下文参数和训练状态属于 10 月 27 日历史。[项目进度](../../PROJECT-PROGRESS.md)。

2026-10-27，Asia/Shanghai。转换全参数重新初始化训练分支的历史最佳 epoch130，并以 TopK=1、严格 `score >0.2` 接入真实 CSI／HDMI／PC 测试。原迁移 epoch99 模型始终保留。

源权重来自服务器 `result/piw24_pose180_scratch_20261024_extra100_r2/best_mpjpe_epoch_130.pth`，SHA256 `40ed3337ea7f130fa6703b70ef57ebddccdceb7dbae9f153cceefd2e41ac3204`。选择时该分支历史最佳为 141.9761 mm；选取时的学习率对照尚未超过它（仅为当时快照）。该数字是既有训练评估记录，不是本次现场精度。

导出文件为 ONNX（本机附件：`source/onnx/pose180_shared.onnx`），SHA256 `4b9cebe7b8d28bf7a85bd4a4ea0d396250d9c76fbaaa739afc297a6cffa0d70d`。CPU 两线程导出及三个真实单／双／三人样本的 PyTorch／ORT 比较通过，最大输出差 1.68085e-5；输入 `[1,180,60]`，输出 `[1,180]` 和 `[1,180,14,3]`，无 TopK／候选 GatherElements／ScatterND。服务器既有 GPU 训练没有修改或重启；导出原始报告（本机附件：`source/onnx/verification.json`）。

Icraft 3.39.0、既有 CUDA 运行库、FP16、zhuget330，五阶段原生退出均为 0，总时长 32.267 s；实际 TOML（本机附件：`piw24_pose180.toml`）、阶段结果（本机附件：`conversion.json`）和 `logs/` 保留。生成图含 950 个 HardOp、无 Host 计算，端口保持 FP32；没有 SDK、NPU 分配或硬件位流变更。

| 产物 | SHA256 |
|---|---|
| 生成图（本机附件：`piw24_pose180_ZG.json`） | `f3bd04dc65bdba4bb93a0d40d697ce86e3ed4caf21d6cad260c422ad147c753c` |
| 生成权重（本机附件：`piw24_pose180_ZG.raw`） | `40699f99a8802ead6a8e194df35b49bf5940ee38a7ffb2052111cd6a0eebb8b7` |

三个真实输入的生成图 Host 执行均 exit0，全部输出有限。相对原 FP32，Top1 索引均保持，Top1 最大关节偏差分别为 18.618／23.719／16.414 mm；全部候选的最大偏差为 159.790 mm。**量化数值精度没有验收通过**，不套用旧图的数值例外；全候选原值统计（本机附件：`reference-generated/analysis.json`）、Top1 统计（本机附件：`reference-generated/top1-analysis.json`）及原始输出保留。

板端使用独立 `.local/csi-scratch130-top1-20261027-r1`，模型文件只解包到本包私有 `pipeline/models`，传输后核对 SHA；未覆盖原 epoch99 图。实际新推理 2910 次后回原图，native_exit=0、完整安全关闭，原定 600 秒未完成，保留原时长门未通过的记录。现场反馈“两路持续更新，效果相近或更差”；这是定性反馈，无姿态 GT，不认定精度改善。后续原图恢复及当前状态统一见[实时集成记录](../../software/pose180_pipeline/resident/CSI-INTEGRATION-20261027.md)。
