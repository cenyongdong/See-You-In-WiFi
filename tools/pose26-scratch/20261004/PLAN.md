# 26版500轮全新训练：已批准范围

2026-10-04方案为从头训练500epoch，并选择论文Adam配方（A）。此前tools/pose26-transfer/20261004/PLAN.md中的恢复第10轮/累计100轮方案未批准，已被本方案替代。

## 工程内容和门检

- 新结果`/public/cyd/Person-in-WiFi-3D-repo/result/tpami2026_scratch_20261004`；新模块`opera/models/tpami2026_scratch.py`，配置`configs/wifi/petr_wifi_tpami2026_scratch.py`，运行管理脚本`tools/pose26_scratch`。不覆盖旧模型、实验配置或结果。
- 全新初始化模型/优化器，不迁移24版或加载10轮权重，不恢复epoch/iteration；不加载外部预训练权重。沿用已经核对的2026姿态结构及初始化：180 CSI token、STE、6层编码器、3层人体解码器、14个残差分化MLP、15-token细化输入、3层vanilla refine。分化Linear权重/偏置N(0,0.001²)，细化器正常初始化，坐标末层零初始化；只训练14关节，不增加mesh/SMPL。
- 原模型/数据/索引逻辑保留，通过无checkpoint调用、初始化统计、人物/关节与置信度排序索引、细化梯度、Adam参数组和学习率衰减边界门检后做4卡96样本短程。短程权重不进入正式训练；正式训练再次seed0全新初始化。
- GPU1–4，每卡batch8/worker4，总batch32；FP32、seed0、clip0.1。按论文Adam统一lr2e-5、betas(0.9,0.999)、eps1e-8、weight_decay1e-4，无上轮衰减排除/迁移学习率分组。500轮，step450/gamma0.1；MMCV标准边界为完成450轮后下一轮lr2e-6，无warmup。启动前验证实际hook行为。
- 每轮全7824帧评估，人数分组、逐关节及同匹配粗→细化对照，分支参数/梯度与四卡检查继续保留；每10轮保存checkpoint并保留最近5份，另保存最佳checkpoint及最后一轮。前轮旧权重全部保留。
- 非有限值、索引错误或连续两轮严重分支趋零即停止；不自动重启、换AdamW/调整参数或延长500轮。500轮粗估约86小时，仅为按上一轮耗时估算，实际速度可能变化。

## 论文一致性与限制

论文PDF第7页（印刷12719）明确给出Adam、momentum0.9、weight_decay1e-4、batch32、500epoch、lr2e-5、450轮衰减0.1、focal alpha0.25/gamma2、回归与分类比例lambda35。现有2/70损失权重保持lambda35比例，统一放大2倍及各decoder层辅助监督是当前代码复现选择，不宣称逐行官方复现。beta2、eps、clip、seed、MLP深度和近零std等论文未完整规定，沿用已讨论的实现选择。

旧Adam实验参数趋零，不证明Adam为唯一原因；本次遵从配置采用，不静默采用AdamW或排除衰减。训练门检仅证明实现/数值可运行，不能承诺500轮精度。GT辅助greedy100候选评估只与既有基准同口径，不代表实部署人数检测性能；不开展ONNX/Icraft/NPU部署。

正式启动与最终验收分开记录。当前文件是批准方案，实际门检、源码哈希、进程与结果以README及evidence为准。
