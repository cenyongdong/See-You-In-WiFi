"""Export measured CPU/latency comparisons; no estimates are drawn as results."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
from run import ROOT, WORK
old = ROOT / '.local/csi-optimization-20261031-r1/reports/board-results/optimization-r1/results'
read = lambda p: json.loads(p.read_text())
b = read(old / 'baseline.json')
f = read(old / 'fast.json')
s = read(WORK / 'reports/benchmark.json')
q = read(WORK / 'reports/qualification-closure.json')
im = Image.new('RGB', (1800, 1130), '#f3f6fa')
d = ImageDraw.Draw(im)
def text(x, y, value, size=26, bold=False):
    font = ImageFont.truetype('C:/Windows/Fonts/' + ('msyhbd.ttc' if bold else 'msyh.ttc'), size)
    d.text((x, y), value, font=font, fill='#172b45')
text(60, 35, 'CSI 预处理优化：CPU 卸载与完整延迟', 44, True)
text(62, 105, '每轮同输入 420 窗口；包含转换、传输、等待和 PS 收尾。柱形均来自板端实测。', 26)
rows = [('PS 软件（与流水版同轮）', s['PS_CPU_ms_per_window'], s['PS_wall_ms_per_window'], '#748399'),
    ('原整窗串行 PL 后端', b['PL_CPU_ms_per_window'], b['PL_wall_ms_per_window'], '#8ba6b4'),
    ('复用位流＋软件优化', f['PL_CPU_ms_per_window'], f['PL_wall_ms_per_window'], '#32a7b5'),
    ('90 点分组流水', s['PL_CPU_ms_per_window'], s['PL_wall_ms_per_window'], '#1979aa')]
for panel, title, note, column in [(0, '线程 CPU 时间', '计算与传输消耗的 CPU 时间', 1), (1, '完整预处理延迟', '从输入准备到完整张量返回',
    2)]:
    x = 60 + 850 * panel
    d.rounded_rectangle((x, 170, x + 820, 800), radius=18, fill='white')
    text(x + 24, 193, title, 33, True)
    text(x + 24, 247, note, 25)
    maximum = max(v[column] for v in rows)
    for j, row in enumerate(rows):
        y = 310 + j * 110
        value = row[column]
        text(x + 24, y, f'{row[0]}  {value:.3f} ms', 26)
        d.rectangle((x + 24, y + 48, x + 24 + 740 * value / maximum, y + 72), fill=row[3])
cpu = 100 * (1 - s['PL_CPU_ms_per_window'] / s['PS_CPU_ms_per_window'])
latency = 100 * (1 - s['PL_wall_ms_per_window'] / s['PS_wall_ms_per_window'])
text(65, 830, f'流水版相对同轮 PS：CPU 时间减少 {cpu:.1f}%；完整延迟减少 {latency:.1f}%。', 31, True)
text(65, 889, f"读取时 PL 仍忙的组数：{s['groups_read_while_busy']} / {s['streamed_groups']}；相位最大误差 {s['phase_max_abs_rad']:.3g} rad。",
    26)
cr = q['csi_resources']
text(65, 938, f"CSI 核：{cr['LUT']:g} LUT / {cr['FF']:g} FF / {cr['DSP']:g} DSP / {cr['BRAM36']:g} BRAM36；CORDIC 迭代精度保持。",
    26)
text(65, 991, '原版与软件优化使用 r2 位流，分组流水使用 r3；每轮均另测配对 PS 参考，原值完整保留。', 24)
text(65, 1039, '这是预处理算子实测，不等于整机 CPU 百分比、功耗或任意实时 CSI 场景的性能保证。', 24)
target = WORK / 'reports/optimization-comparison.png'
im.save(target)
print(target)
