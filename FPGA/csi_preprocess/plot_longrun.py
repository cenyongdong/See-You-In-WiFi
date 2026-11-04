"""Standalone measurement figure from the retained long-run samples."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from longrun import WORK
r = WORK / 'reports'
rows = lambda p: [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
b = rows(r / 'board-evidence/monitor/samples.jsonl')
p = rows(r / 'pc/samples.jsonl')
summary = json.loads((r / 'summary.json').read_text())
active = [v for v in b if (v.get('status') or {}).get('inferred', 0) > 0]
pc = [v for v in p if v.get('raw', {}).get('connected') and v.get('raw', {}).get('received', 0) > 0]
font = FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
plt.rcParams.update({'font.family': font.get_name(), 'axes.unicode_minus': False, 'font.size': 11})
fig, axes = plt.subplots(2, 2, figsize=(14, 8), constrained_layout=True)
fig.suptitle('CSI 分组流水：30分钟官方输入双路稳定性实测', fontsize=20)
t = [(v['monotonic'] - active[0]['monotonic']) / 60 for v in active]
axes[0, 0].plot(t, [v['status']['inferred'] for v in active], label='NPU 推理', lw=2)
axes[0, 0].plot(t, [v['status']['adopted'] for v in active], label='HDMI 采纳', ls='--')
axes[0, 0].set_title('新结果累计计数')
axes[0, 0].legend()
resources = [(t[i], v['service-status.json']) for i, v in enumerate(active) if v.get('service-status.json',
    {}).get('RSS_KiB')]
axes[0, 1].plot([x[0] for x in resources], [x[1]['RSS_KiB'] / 1024 for x in resources], color='#008b89')
axes[0, 1].set_title('板端原生进程 RSS')
axes[0, 1].set_ylabel('MiB')
axes[0, 1].set_ylim(bottom=0)
tp = [(v['monotonic'] - pc[0]['monotonic']) / 60 for v in pc]
for mode, label in [('raw', 'PC 原始'), ('view', 'PC 展示')]:
    axes[1, 0].plot(tp, [v.get(mode, {}).get('new_results_hz', 0) for v in pc], label=label, alpha=.85)
axes[1, 0].set_title('PC 新结果到达率（5秒采样）')
axes[1, 0].set_ylabel('次/秒')
axes[1, 0].legend()
axes[1, 0].set_ylim(bottom=0)
for field, label in [('preprocess_ms', '预处理'), ('process_ms', '整条处理')]:
    data = [(tp[i], v['raw'].get('frame_identity', {}).get('metrics', {}).get(field)) for i, v in enumerate(pc)]
    data = [x for x in data if x[1] is not None]
    axes[1, 1].plot([x[0] for x in data], [x[1] for x in data], label=label)
axes[1, 1].set_title('板端耗时（每5秒所见最新帧，非逐帧分位数）')
axes[1, 1].set_ylabel('ms')
axes[1, 1].legend()
axes[1, 1].set_ylim(bottom=0)
for ax in axes.flat:
    ax.set_xlabel('首个有效采样后 / 分钟')
    ax.grid(alpha=.2)
fig.supxlabel('官方train：8700个不同窗口循环，新推理持续运行；不代表实时CSI或姿态真值精度验收。', fontsize=10)
fig.savefig(r / 'stability-30min.png', dpi=160)
print(r / 'stability-30min.png')
