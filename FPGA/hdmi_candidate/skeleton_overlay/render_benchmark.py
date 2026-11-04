"""Draw an exportable data chart from retained board evidence (not a screen capture)."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from run import WORK

r = WORK / 'reports'
ps = json.loads((r / 'ps-native-display-metrics.json').read_text())
pl = json.loads((r / 'pl-native-display-metrics.json').read_text())['overlay']
bench = [json.loads(line) for line in (r / 'board/ps-benchmark-121333.log').read_text().splitlines() if line.startswith('{')]
three = next(row for row in bench if row['people'] == 3)
im = Image.new('RGB', (1800, 1060), '#f3f6fa')
d = ImageDraw.Draw(im)
def text(x, y, s, size=28, color='#15263c', bold=False):
    f = ImageFont.truetype('C:/Windows/Fonts/' + ('msyhbd.ttc' if bold else 'msyh.ttc'), size)
    d.text((x, y), s, font=f, fill=color)
text(62, 42, 'PS / PL 板端对照与实现代价', 48, bold=True)
text(64, 116, '同一开发板、同一模型、相同官方 CSI 片段；此图为日志统计，不是 HDMI 实屏截图。', 27)
panels = [('CPU 绘图准备', '同一合成三人姿态，各 100 次', three['ps_prepare_ms'], three['pl_command_prepare_ms']),
    ('动态提交调用', 'PS 整帧上传＋翻帧 / PL 写指令', ps['frame_upload_and_flip_issue_ms']['mean'], pl['submit_ms']['mean']),
    ('提交至显示确认', '含等待；PL 另包含硬件绘制', ps['write_and_adopt_ms']['mean'], pl['submit_and_adopt_ms']['mean'])]
for i, (title, note, a, b) in enumerate(panels):
    x = 60 + i * 570
    d.rounded_rectangle((x, 190, x + 540, 610), radius=18, fill='white')
    text(x + 24, 214, title, 32, bold=True)
    text(x + 24, 268, note, 23)
    scale = 475 / max(a, b)
    for j, (label, value, color) in enumerate([('PS', a, '#718096'), ('PL', b, '#1678ad')]):
        y = 330 + j * 120
        text(x + 24, y, f'{label}   {value:.4f} ms', 29)
        d.rectangle((x + 24, y + 49, x + 24 + max(1, value * scale), y + 75), fill=color)
    text(x + 24, 566, '均值；越短表示该项耗时越少', 22)
text(65, 654, '实板结果', 31, bold=True)
text(65, 704, '417 次新推理 / HDMI 采纳；225 组相同输入的全部 180 候选输出逐字节一致。', 28)
text(65, 753, '动态命令平均 666 B；硬件绘制平均 5.243 ms；用户确认骨架和信息持续更新。', 28)
text(65, 802, '新增模块：1,145 LUT / 939 FF / 4 DSP / 128.5 BRAM36；WNS +0.017 ns，WHS +0.029 ns。', 27)
text(65, 868, '口径：后两图来自保留环（PS 229 条、PL 226 条），不含 PS 绘图准备；不能相加冒充端到端实测。', 23)
text(65, 910, '边界：3 次输入窗口替换、PC 原始记录 2 次丢弃；首次背景上传和持续 DDR 背景读取仍存在。', 23)
text(65, 952, '收益是 CPU 绘图卸载与提交开销下降；本轮未证明端到端加速、功耗下降或长期稳定性。', 23)
out = r / 'figures/board-performance-comparison.png'
out.parent.mkdir(exist_ok=True)
im.save(out)
print(out)
