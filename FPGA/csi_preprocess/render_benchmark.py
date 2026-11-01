"""Standalone report figure, generated only from retained board measurements."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('benchmark');p.add_argument('qualification');p.add_argument('output');a=p.parse_args()
b=json.loads(Path(a.benchmark).read_text());q=json.loads(Path(a.qualification).read_text())
im=Image.new('RGB',(1800,1030),'#f3f6fa');d=ImageDraw.Draw(im)
def text(x,y,s,size=28,bold=False,color='#172b45'):
 f=ImageFont.truetype('C:/Windows/Fonts/'+('msyhbd.ttc' if bold else 'msyh.ttc'),size);d.text((x,y),s,font=f,fill=color)
text(60,40,'CSI 幅相预处理：软件 / FPGA 板端对照',46,True)
text(62,112,f"同一开发板、同一 {b['frames']} 帧官方训练集 CSI；交替 PS / PL 执行顺序；日志统计图。",27)
panels=[('CPU 实际占用时间','线程 CPU 时钟，包含转换与传输',b['PS_CPU_ms_per_window'],b['PL_CPU_ms_per_window']),
 ('完整预处理总耗时','墙钟时间，包含传输、硬件等待与 PS 收尾',b['PS_wall_ms_per_window'],b['PL_wall_ms_per_window'])]
for i,(title,note,ps,pl) in enumerate(panels):
 x=60+i*850;d.rounded_rectangle((x,185,x+820,580),radius=18,fill='white')
 text(x+25,210,title,33,True);text(x+25,265,note,25)
 for j,(label,v,c) in enumerate([('PS 软件',ps,'#748399'),('PL 混合后端',pl,'#1979aa')]):
  y=325+j*112;text(x+25,y,f'{label}   {v:.4f} ms / 窗口',29)
  d.rectangle((x+25,y+50,x+25+max(1,750*v/max(ps,pl)),y+75),fill=c)
reduction=100*(1-b['PL_CPU_ms_per_window']/b['PS_CPU_ms_per_window'])
text(65,620,f'CPU 时间变化：减少 {reduction:.1f}%（仅本预处理算子，不代表整机 CPU 利用率）',31,True)
text(65,682,f"PL 分段墙钟：上传 {b['upload_ms_per_window']:.3f} / 等待 {b['wait_ms_per_window']:.3f} / 下载 {b['download_ms_per_window']:.3f} / PS 收尾 {b['finish_ms_per_window']:.3f} ms。",27)
text(65,726,'分段计时不含前置 FP64→FP32 转换；上方完整总耗时包含该转换。',24)
r=q['csi_resources']
text(65,779,f"新增 CSI 核：{r['LUT']:g} LUT / {r['FF']:g} FF / {r['DSP']:g} DSP / {r['BRAM36']:g} BRAM36。",28)
text(65,826,f"幅度最大绝对误差 {b['amplitude_max_abs']:.3g}；相位最大绝对误差 {b['phase_max_abs_rad']:.3g} rad。",27)
text(65,886,'PL：CORDIC 幅度 / 原始相位；PS：相位展开、线性校正、边界回退。原模型和 NPU 不变。',24)
text(65,932,'范围：有限 GP 算子实测；不代表功耗、模型精度、新现场 CSI 或长期稳定性验收。',24)
out=Path(a.output);out.parent.mkdir(exist_ok=True);im.save(out);print(out.resolve())
