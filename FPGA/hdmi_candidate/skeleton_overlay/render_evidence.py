"""Render actual RTL-exported palette pixels; never label this as a board photo."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/'.local/skeleton-overlay-20261031-r2'
d=Path(json.loads((W/'reports/frame-latest.json').read_text())['directory'])
def decode(path):
    p=np.fromfile(path,dtype='<u2').reshape(1080,1920)
    return np.stack((((p>>11)&31)*255//31,((p>>5)&63)*255//63,(p&31)*255//31),axis=2).astype('uint8')
bg=decode(W/'software/background.rgb565')
ps=decode(W/'software/fixture-3-ps.rgb565')
indices=np.array([int(x,16) for x in (d/'overlay.hex').read_text().splitlines()],dtype=np.uint8).reshape(540,960)
indices=indices.repeat(2,axis=0).repeat(2,axis=1)
palette=np.array([[0,0,0],[0x39,0x9e,0xff],[0xef,0xf3,0xf7],[0x10,0x3c,0x31],[0xb5,0xf7,0xde],[0x4a,0x3c,0x21],[0xff,0xe3,0xa5]],dtype=np.uint8)
pl=bg.copy();pl[indices!=0]=palette[indices[indices!=0]]
out=W/'reports/figures';out.mkdir(exist_ok=True)
Image.fromarray(pl).save(out/'rtl-composite-synthetic.png')
Image.fromarray(ps).save(out/'ps-reference-synthetic.png')
canvas=Image.new('RGB',(1920,650),'#f2f4f7')
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
draw.text((24,12),'SYNTHETIC FIXTURE - CPU raster / actual RTL simulation pixels (not a board capture)',fill='#182537',font=font)
draw.text((24,52),'PS: 1080p RGB565',fill='#182537',font=font)
draw.text((984,52),'PL: 960x540 palette overlay + 1080p background',fill='#182537',font=font)
canvas.paste(Image.fromarray(ps).resize((960,540)),(0,92))
canvas.paste(Image.fromarray(pl).resize((960,540)),(960,92))
canvas.save(out/'ps-vs-rtl-synthetic.png')
(out/'provenance.json').write_text(json.dumps(dict(source='synthetic three-person fixture; not model accuracy or fresh inference',rtl_pixel_file=str(d/'overlay.hex'),command_file=str(W/'software/fixture-3.hex'),command_bytes=816,draw_cycles=524866,GP_clock_Hz=100000000,estimated_draw_ms_from_simulation=5.24866,board_tested=False),indent=2))
print(out/'ps-vs-rtl-synthetic.png')
