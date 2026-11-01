# 26版pose-only：全新初始化500轮Adam训练

**最新状态（2026-10-04 09:08核验）：训练已于01:40:51在第6轮末因连续两轮分支严重退化自动停止。只有5轮完整评估，最佳第4轮420.189946mm；500轮未完成。** 训练进程均退出，未重启或修改参数，未启用定时监测。详细结果、参数/梯度与checkpoint证据见[STATUS-20261004-0908.md](STATUS-20261004-0908.md)。以下为启动历史及当时验证范围。

2026-10-04方案为从头训练500epoch，并选择论文Adam配方A；00:41:21（北京时间）正式启动。单项及四卡门检、源码/配置/快照核验和实际训练启动已通过，**训练尚未完成，精度尚未验收**。配置采用暂不启用定时监测，旧自动化ID26保持PAUSED；不承诺会话结束后自动回查。

启动后补充快照：第1轮训练的2811步已完成，四卡一致性通过，正在进行首轮评估，评估指标尚待核验。首轮末分化L2=0.003813、细化注意力L2=51.173392，均有限且未触发既有严重趋零门禁；相较初始化快速缩小仍需关注。见`evidence/first-epoch-training.json`；下文第501步为较早启动快照。

## 工程内容总结

服务器`ssh gpu-server`，根目录`/public/cyd/Person-in-WiFi-3D-repo`，Python`/home/ubuntu/miniconda3/envs/PersonInWIFI/bin/python`；PyTorch1.13.1+cu117、MMCV1.5.3、MMDetection2.25.0、GPU1–4四张RTX A5500。结果`result/tpami2026_scratch_20261004`，Windows入口`Z:\Person-in-WiFi-3D-repo\result\tpami2026_scratch_20261004`。

全新初始化模型/优化器，不加载24版、10轮实验或外部预训练checkpoint，不恢复训练计数。新注册`PETR2026Scratch`显式绕过旧类的migrate调用；复用已核对的STE、14个独立残差分化MLP、3层vanilla refine及姿态索引代码，旧代码/配置/权重/结果未改。虽然复用文件名中含Transfer的结构类，实际不进行迁移；门检禁止torch.load并记录checkpoint_calls为空，正式hook再次确认epoch/iter=0且优化器state为空。

分化Linear权重/偏置N(0,0.001²)，Refine Decoder正常初始化、坐标回归末层零初始化。只训练14关节，不增加mesh/SMPL。

Adam统一lr2e-5、betas(0.9,0.999)、eps1e-8、weight_decay1e-4，无迁移学习率分组或衰减排除；每卡batch8/worker4，总batch32，FP32、seed0、clip0.1。500轮，MMCV step450/gamma0.1，已测试边界：完成450轮后第451轮lr2e-6。数据/预处理/划分不变，每轮评估全部7824帧；分类/坐标2/70保留lambda35比例。每10轮checkpoint、保留最近5份，另保留最佳及最终checkpoint；旧实验权重不删除。

论文PDF第7页（印刷12719）明确给出Adam、batch32、500epoch、2e-5、weight_decay1e-4、450轮衰减0.1及lambda35。beta2/eps、seed/clip、MLP深度/初始化std、整体损失2倍缩放和decoder辅助监督为已记录的实现选择，不宣称逐行官方复现。

## 已完成验证及证据

1. [单项门检](D:/FPGACompetitionProject/tools/pose26-scratch/20261004/evidence/gates/unit_gate.json)：6层编码器、3层人体/细化解码器、vanilla8头256维、14分支、15-token、索引/置信度排序、仅细化损失梯度通路；分化权重/偏置std0.000999973/0.000991597；无checkpoint调用，学习率衰减边界通过。
2. [四卡门检](D:/FPGACompetitionProject/tools/pose26-scratch/20261004/evidence/gates/ddp_gate.json)：4卡×8、96样本、3步，参数范数一致，checkpoint全部有限，优化器为单组Adam/lr2e-5/wd1e-4。短程在独立smoke目录，正式训练重新初始化，不复用短程更新。
3. [启动审计](D:/FPGACompetitionProject/tools/pose26-scratch/20261004/evidence/prelaunch-audit.json)及[独立启动核验](D:/FPGACompetitionProject/tools/pose26-scratch/20261004/evidence/startup-verification.json)：129份源码/配置/列表当前与source_snapshot哈希一致，解析配置哈希通过，正式GPU1–4有负载、4个训练rank运行；正式日志已超过500步且已记录诊断有限。项目evidence为采集时快照，实时读服务器结果目录。
4. 启动身份：监督PID54209、torchrun54220、训练rank54225–54228（SSH可见PID）。nvidia-smi显示另一组PID且process_name为Not Found，未证明两组PID的逐项映射；操作进程时以重新核对的SSH/proc命令行身份为准，不能仅凭nvidia-smi PID操作进程。

## 实际入口与边界

已由隔离流水线执行下列训练命令，**不可重复执行**：

```bash
cd /public/cyd/Person-in-WiFi-3D-repo
CUDA_VISIBLE_DEVICES=1,2,3,4 PYTHONDONTWRITEBYTECODE=1 \
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 \
PYTHONPATH=/public/cyd/Person-in-WiFi-3D-repo \
/home/ubuntu/miniconda3/envs/PersonInWIFI/bin/python -B \
-m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=4 \
tools/train.py configs/wifi/petr_wifi_tpami2026_scratch.py --launcher pytorch --seed 0
```

状态/日志：`pipeline-status.json`、`train.stdout.log`、`initialization.json`、`branch_diagnostics.jsonl`、`epoch_parameter_checks.jsonl`、`evaluations.jsonl`。非有限值、索引错误、四卡不一致或连续两轮分化/细化注意力L2<1e-10时停止；不自动改AdamW、调参、重启或延长。500轮结束后生成final-report.json、metrics.csv及曲线，仍须独立核验才可记录完成。

## 对后续开发的参考

- 第501步快照：分化L2从1.357186降至0.016044，裁剪前/后分化梯度约0.009753/0.000014741；损失从第50步2721.3降到第500步37.15。数值仍有限、尚未触发严重趋零门禁，但参数快速缩小值得关注，不能把损失下降写成精度或分支有效性通过。
- 明确采用论文Adam，耦合L2衰减与上一轮AdamW方案不同；旧退化原因尚未唯一确诊。本次不能静默保留AdamW的衰减排除，也不能由短程通过推定500轮无退化。
- 每轮继续报告人数、关节与固定匹配下粗/细化对照；GT辅助greedy100候选的逐帧指标只能与既有基准同口径对照，不能作为实部署人数选择验收。
- 不做ONNX/Icraft/NPU或FPGA部署；未来调整优化器、损失、数据、初始化或追加训练仍须先讨论批准。

