# TPAMI 2026 姿态路径核对

本次采用从 2024 epoch442 迁移的独立实验，不是从零训练，也不声明复刻未公开的作者源码。论文来源：本地 `paper/Person-in-WiFi_3D_Unified_Model_for_3D_WiFi_Perception.pdf`，PDF 第5–6页（印刷页12717–12718）；第6页图5、图6已可视核对。网格/SMPL路径排除。

| 论文内容 | 服务器实现与验收 |
| --- | --- |
| 180个CSI token，每token幅度与相位60维，投影256维，加可学习STE | 原预处理/reshape保留；`_CSIProjectionWithSTE` 新建180×256参数；STE标准差0.02是复现选择 |
| 6层编码器、100个人体查询、3层姿态解码器 | `verify_transfer.py` 检查实际层数，迁移原编码器/解码器/查询和粗预测头；关闭STE后原模型与新模型粗输出逐元素一致 |
| 14个关节查询从同一个人的identity token分化而来 | 14个独立残差MLP，`q_j = identity + MLP_j(identity)`；2个Linear和中间LeakyReLU是明确记录的复现选择，论文未明确完整层数 |
| 分化分支权重和偏置随机近零 | 所有分化Linear权重、偏置均N(0,0.001²)；实测std约0.001/0.000992；0.001不是论文给出的方差 |
| identity与关节查询一起进入细化网络 | 每人15-token序列，回归仅取后14个joint token；通过跨batch人物索引与置信度排序的动态测试 |
| 3层vanilla self-attention/cross-attention/FFN | 实际6个torch MultiheadAttention实例，8头、256维；不使用deformable attention；整个Refine Decoder正常初始化 |
| 每层预测关节坐标偏移，累加到上一层结果 | 三层累加；层间参考坐标detach沿用已有实现，不声称论文明确规定detach；末层坐标Linear零初始化 |
| 训练选Hungarian匹配人物，推理按置信度选人 | 训练人物、memory、identity共同按匹配索引选择；推理相同top-k排列作用于pose和identity；测试覆盖不同batch人物和非饱和分类分数 |
| focal分类损失和MSE坐标损失 | 实际配置FocalLoss权重2，MSE粗/细坐标权重70；保留原Hungarian匹配和辅助监督，不引入mesh损失 |

训练方式（AdamW、分组学习率、排除衰减、24版迁移、10轮）均是本轮实验设置，不称为论文原训练配方。169个张量迁移后，新STE、分化/细化网络及优化器重新开始；短程门检的更新不用于正式训练。

当前评估继承原代码的GT辅助greedy匹配、100个候选、每帧平均MPJPE。该口径可与现有123.09mm基线比较，但不能据此宣称实际部署人数检测性能或直接重现论文所有表格。细化前后采用最终预测的同一匹配索引，防止重新匹配混淆阶段比较。坐标物理轴未确认，不擅自给原始列命名。

验证证据在服务器 `result/tpami2026_transfer_20261003/gates/`：unit_gate.json、ddp_gate.json；正式启动另写prelaunch-audit.json和完整解析配置。初次索引门检因测试logits过大导致sigmoid饱和并列而失败，改用[-2,2]非饱和测试值后通过；保留失败日志，不修改网络排序规则迎合测试。
