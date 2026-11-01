# 2026姿态模型：epoch442迁移实验

2026-10-03实施。**10轮训练、结果汇总与独立核验已完成，23:42停止；最佳第9轮122.873804mm。完整结果与交付见[RESULTS.md](RESULTS.md)。** 最新运行状态以服务器`pipeline-status.json`和日志为准。

## 入口

- 本目录是项目内可审阅源码副本；未修改独立本机`D:\Person-in-WIFI-3D\Person-in-WiFi-3D-repo`及既有服务器2024/2026源码、权重和结果。
- `ssh gpu-server`；服务器`/public/cyd/Person-in-WiFi-3D-repo`；映射`Z:\Person-in-WiFi-3D-repo`。
- Python `/home/ubuntu/miniconda3/envs/PersonInWIFI/bin/python`；PyTorch1.13.1+cu117、MMCV1.5.3、MMDetection2.25.0，GPU1–4为RTX A5500。
- 新模块部署至`opera/models/tpami2026_transfer.py`、`transfer_support.py`，配置至`configs/wifi/petr_wifi_tpami2026_transfer.py`，审计/启动/汇总脚本至`tools/pose26_transfer`。
- 正式结果`result/tpami2026_transfer_20261003`。启动时流水线PID30236、torchrun30247；操作进程前必须重新核对身份。

## 已完成验证

1. 从24版epoch442迁移169个张量（10,680,492元素），逐元素一致，不恢复源优化器。源checkpoint SHA256：`6493e2250b83aef59ce4825e15d2d0043a59490275f75933f9a59867867d3221`。
2. 三层普通注意力、14个独立残差MLP、15-token序列；分化权重/偏置std=0.000999973/0.000991597，坐标末层零初始化。关闭STE后粗预测误差0；索引及仅细化损失的梯度连通性通过。见`evidence/gates/unit_gate.json`。
3. 4卡×8、96样本完成3步训练；恢复后优化器连续到6步，四卡模块范数一致。短程权重不用于正式训练。见`evidence/gates/ddp_gate.json`。
4. 24版7824帧复评**123.085352129mm**；单/双/三人99.6647/123.1150/152.5261mm，分别2586/3184/2054帧。见`evidence/baseline/evaluations.jsonl`。
5. 实际导入路径、完整解析配置、源码与数据列表哈希、GPU占用已记录；服务器`source_snapshot`保存副本。见`evidence/prelaunch-audit.json`和`resolved_config.py`。
6. 2026-10-03 21:59启动正式10轮。流水线无自动重试、恢复或延长，失败写`failed_stopped`，10轮后生成`final-report.json`、`metrics.csv`、最佳权重哈希及PNG/SVG曲线。须核对实际产物才能宣称训练完成。

初次门检因0…99测试logits导致sigmoid饱和并列而失败，改为[-2,2]后通过；网络排序未改。失败证据保留于服务器`gates/unit_gate_attempt1.log`。

## 参数和命令

AdamW，迁移lr2e-6/新增lr2e-5；矩阵wd1e-4，分化分支/偏置/归一化/查询及STE不衰减；clip0.1，分类/坐标损失2/70；FP32、seed0、每卡batch8/worker4，固定学习率10轮。预处理、划分和评估口径不变；仅14关节姿态，无mesh/SMPL。

实际命令由流水线执行并记录，**本轮已完成，勿重复执行**：

```bash
cd /public/cyd/Person-in-WiFi-3D-repo
CUDA_VISIBLE_DEVICES=1,2,3,4 PYTHONDONTWRITEBYTECODE=1 \
OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 \
PYTHONPATH=/public/cyd/Person-in-WiFi-3D-repo \
/home/ubuntu/miniconda3/envs/PersonInWIFI/bin/python -B \
-m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=4 \
tools/train.py configs/wifi/petr_wifi_tpami2026_transfer.py --launcher pytorch --seed 0
```

Windows只读查询：

```powershell
Get-Content 'Z:\Person-in-WiFi-3D-repo\result\tpami2026_transfer_20261003\pipeline-status.json'
Get-Content 'Z:\Person-in-WiFi-3D-repo\result\tpami2026_transfer_20261003\train.stdout.log' -Tail 6
```

## 诊断与边界

每50步记录分化/细化/姿态/STE参数、裁剪前后梯度L2及关节/人物查询差异，每轮核对四卡模块范数。非有限loss/梯度/抽检参数中止；连续两轮分化或细化注意力L2<1e-10视为严重塌缩并中止。数值门禁不替代对精度下降或分支无益的分析。

每轮记录整体、人数分组、逐关节MPJPE及粗→三层细化固定匹配误差。原指标依赖GT辅助greedy匹配100候选，不等同实际部署人数检测性能；坐标物理轴未确认。普通日志只显示一个lr，完整参数组见`migration.json`，两组学习率在恢复门检核对通过。

论文对应及复现选择见`PAPER_AUDIT.md`。MMCV提示未额外传入key位置编码，本实现已在CSI投影后显式加STE，不能据该提示判断缺少STE。10轮不承诺超过123.09mm，不宣称等价论文从零训练；结束后先讨论，再决定延长或改参数。

### 首轮实际评估（2026-10-03 22:10快照）

第1/10轮完成，四卡一致性、全7824帧评估及`best_mpjpe_epoch_1.pth`保存通过，训练已进入第2轮。MPJPE **126.41057mm**，高于24版基准123.08535mm约3.32522mm；固定最终匹配的粗/细化1/2/3分别126.06887/126.24047/126.33473/126.41057mm，首轮细化尚无收益。单/双/三人104.90486/126.34861/153.58244mm。分化/细化注意力L2分别1.357471858/92.75375147，未观察到旧实验的参数趋零。当前记录不是最终10轮结论，不自行调整参数或延长实验；首次best仅表示本实验已完成轮次中的最佳，不代表超过24版。

项目证据副本：`tools/pose26-transfer/20261003/evidence/evaluations.jsonl`、`epoch_parameter_checks.jsonl`、`branch_diagnostics.jsonl`。这些为采集时快照，实时结果以服务器目录为准。
