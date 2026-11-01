"""Keep original r2 synthesis logs; replace only the oversized buffer netlist."""
from run import WORK,SRC
import shutil
r=WORK/'reports'
shutil.copyfile(SRC/'batch.sv',WORK/'sources/batch_banked.sv')
v=(r/'synthesis.tcl').read_text().replace('/sources/batch.sv','/sources/batch_banked.sv').replace('pipeline-synth.dcp','pipeline-synth-banked.dcp')
(r/'synthesis-banked.tcl').write_text(v)
v=(r/'opt.tcl').read_text().replace('pipeline-synth.dcp','pipeline-synth-banked.dcp').replace('pipeline-linked','pipeline-linked-banked').replace('pipeline-opt.dcp','pipeline-opt-banked.dcp')
(r/'opt-banked.tcl').write_text(v)
p=r/'place-csi-incremental.tcl';p.write_text(p.read_text().replace('pipeline-opt.dcp','pipeline-opt-banked.dcp'))
p=WORK/'qualify_closure.py';v=p.read_text()
v=v.replace("'synthesis', 'opt-linked' if (E/'opt-linked-execution.json').exists() else 'opt'", "'synthesis-banked', 'opt-banked'")
v=v.replace("'synthesis','opt-linked' if (E/'opt-linked-execution.json').exists() else 'opt'", "'synthesis-banked','opt-banked'")
p.write_text(v)
print('Prepared banked 8192+4096-word buffers; original nonbanked stage results retained')
