# 分化分支关闭衰减：10轮从零对照实验

**最新结果：2026-10-04 12:00:59完成10轮并停止，13:06独立核验通过。最佳第6轮344.787403mm，第10轮377.942667mm。分化参数没有归零，但第7–10轮所有抽检的分化/细化注意力梯度为零，细化学习仍存在退化；不能将训练完成等同于算法有效。** 完整结果见[RESULTS.md](RESULTS.md)。

是上一轮建议的“仅关闭 Differentiation Branch 衰减”对照，不是关闭整条细化路径。当前已按10轮授权停止，禁止自动延长、重启或变更参数。此前暂不启用监测的选择保持；没有为本实验启用定时任务，ID26仍暂停。下述10:20–10:25启动/运行状态和待验收文字是历史记录，已由上述完成核验更新；最终证据见`evidence/completion-20261004-1306`和`evidence/completion-verification.json`。

交付前最新只读查询（10:25:28）：stage=training，第1轮第1701个训练步，分化L2=1.719859849，分化/注意力梯度及查询残差非零；日志未记录异常，仍无完整评估。初期分支未塌缩，不代表已越过原第6轮退化点或精度改善。证据 `evidence/progress-latest.json`；下方10:21启动核验为较早独立快照。

## 工程内容总结

服务器 `ssh gpu-server`，项目 `/public/cyd/Person-in-WiFi-3D-repo`，Python `/home/ubuntu/miniconda3/envs/PersonInWIFI/bin/python`，PyTorch 1.13.1+cu117、MMCV1.5.3、MMDetection2.25.0。GPU1–4四张RTX A5500，每卡batch8/worker4，总batch32，FP32、seed0、全局梯度裁剪0.1。

唯一算法变量：`bbox_head.transformer.joint_differentiators.` 下14个独立MLP的56份Linear权重/偏置（1,842,176个元素）衰减从1e-4改成0。其余所有参数，包括Refine Decoder、坐标偏移回归、STE、查询、偏置及归一化，继续沿用原实验衰减规则1e-4。冻结参数仍冻结。优化器仍为Adam，统一lr2e-5、betas(0.9,0.999)、eps1e-8。保留step450/gamma0.1，本次10轮不会触发。

模型仍为PETR2026Scratch：不加载任何checkpoint或优化器状态，分化权重/偏置N(0,0.001²)、正常初始化3层vanilla细化器、坐标回归末层零初始化；仅14关节，不含mesh/SMPL。数据、预处理、训练/测试列表、2/70损失及索引逻辑保持原实验。新配置、优化器构造器和审计hook独立新增，旧模型、配置、权重及结果保留。

远程新源码：`opera/models/tpami2026_diff_nodecay.py`、`configs/wifi/petr_wifi_tpami2026_diff_nodecay.py`、`tools/pose26_diff_nodecay`。项目内同名文件是上传源码副本，具体远程对应和SHA256见 `upload-map.json`、`manifest.json`。`build_local.py` 为本地构造工具，不能当作服务器训练入口；本地配置依赖服务器原配置，不应直接在Windows训练。

### 验证证据

- `evidence/gates/unit_gate.json`：56份参数分组和完整覆盖通过；模型/训练数据配置相同、初始化各模块L2与旧实验一致，禁止torch.load的初始化门检无checkpoint调用；三层普通注意力、14分支、索引对应及仅细化损失梯度连通通过。第一步实际分化梯度为零，其全部参数更新前后逐元素相等。
- `evidence/gates/ddp_gate.json`：4卡×8、96样本、3步，DDP范数一致，checkpoint有限，两组Adam衰减[0,1e-4]，计数与分组通过。短程分化L2=1.357186178；短程权重不进入正式训练。
- `evidence/control-consistency.json`：旧500轮实验129份源码/列表哈希未变，新14份清单哈希通过；与原实验实际解析配置逐项核对，差异只限批准的衰减分组/审计hook、新路径和10轮停止。正式启动再次验证GPU1–4空闲。
- `evidence/startup-verification.json`：正式134份源码/配置/列表及source_snapshot哈希、实际解析配置哈希通过，初始模块L2与原实验完全一致；实际监督、torchrun及4个rank在运行，记录诊断有限。10:21:30快照已记录到第251步，分化L2=1.564860762，分化/注意力裁剪后梯度约9.40e-5/0.008027，首轮全量评估尚未完成。

服务器结果目录 `/public/cyd/Person-in-WiFi-3D-repo/result/tpami2026_diff_nodecay_20261004`，映射入口 `Z:\Person-in-WiFi-3D-repo\result\tpami2026_diff_nodecay_20261004`。本轮使用SSH，不以Z盘可用性判断训练结果。启动身份：监督PID70223、torchrun70234、rank70239–70242；后续操作必须重新核对PID和完整命令行。

### 实际训练入口

以下由独立监督流水线执行，**不可重复运行**：

```bash
cd /public/cyd/Person-in-WiFi-3D-repo
CUDA_VISIBLE_DEVICES=1,2,3,4 PYTHONDONTWRITEBYTECODE=1 \
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 \
PYTHONPATH=/public/cyd/Person-in-WiFi-3D-repo \
/home/ubuntu/miniconda3/envs/PersonInWIFI/bin/python -B \
-m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=4 \
tools/train.py configs/wifi/petr_wifi_tpami2026_diff_nodecay.py --launcher pytorch --seed 0
```

优先查 `pipeline-status.json`、`train.stdout.log`、`branch_diagnostics.jsonl`、`epoch_parameter_checks.jsonl`、`evaluations.jsonl`。每轮全7824帧评估人数分组、逐关节及固定匹配粗/细化误差；非有限值、索引错误、DDP不一致及连续两轮分化/细化注意力L2<1e-10仍会停止。最终保存epoch10和最佳权重，生成 `final-report.json`、`metrics.csv`、曲线及与旧实验前5轮的同轮对照；这些目前均待验证。生成报告仍需独立验收，不等于自动通知。

## 对后续开发的参考

本次先验证“分化分支耦合L2衰减是否与塌缩有关”，不是重做500轮论文配方或证明精度已提升。保持Adam和其他变量，关闭范围仅为分化MLP。需要观察能否越过原第6轮退化点、分化参数/梯度与残差是否保持有效，以及细化是否改善同匹配姿态；无衰减不代表参数不会因监督损失而收缩。

主要对照是失败的全衰减从零实验前5轮评估及第6轮退化诊断。24版123.085352129mm只是已收敛参考，不是10轮从零实验的公平终局对照；单seed结果不能证明稳定增益。禁止从本次短程稳定推定10轮或长期成功，也不据此推广为整条细化路径应当零衰减。论文统一衰减的偏离已明确记录。

旧实验保留，任何后续扩大零衰减范围、更换优化器、调整初始化/损失或继续长训练，都须先讨论批准。
