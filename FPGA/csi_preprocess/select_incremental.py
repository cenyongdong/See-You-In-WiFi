"""Reuse r1's qualified placement/routing for the small CSI buffer revision.
Only physical reuse is requested; new synthesis supplies the full new netlist.
"""
from run import ROOT,WORK
import json
r=WORK/'reports';old=ROOT/'.local/csi-preprocess-20261031-r1/pipeline-routed-direct.dcp'
assert old.exists()
v=(r/'place-nonincremental.tcl').read_text()
anchor='open_checkpoint {'+(WORK/'pipeline-opt.dcp').as_posix()+'}'
assert v.count(anchor)==1
v=v.replace(anchor,anchor+'\nread_checkpoint -incremental {'+old.as_posix()+'}')
v=v.replace('nonincremental','csi-incremental')
(r/'place-csi-incremental.tcl').write_text(v)
v=(r/'route-direct.tcl').read_text().replace('physopt-nonincremental','physopt-csi-incremental').replace('route-direct','route-csi-incremental').replace('routed-direct','routed-csi-incremental')
(r/'route-csi-incremental.tcl').write_text(v)
for name in ('report-closure.tcl','bit-closure.tcl'):
 p=r/name;p.write_text(p.read_text().replace('pipeline-routed-closure.dcp','pipeline-routed-csi-incremental.dcp'))
p=WORK/'qualify_closure.py';v=p.read_text()
v=v.replace("'route-direct', 'physopt-direct', 'report-closure'", "'route-csi-incremental', 'report-closure'")
v=v.replace("'route-direct','physopt-direct','report-closure'", "'route-csi-incremental','report-closure'")
v=v.replace('place-nonincremental','place-csi-incremental').replace('pipeline-routed-closure.dcp','pipeline-routed-csi-incremental.dcp')
p.write_text(v)
(r/'implementation-selection.json').write_text(json.dumps(dict(mode='incremental',reference=str(old),
 reason='Only CSI buffers/diagnostics changed; preserve the qualified unchanged NPU and overlay physical context.'),indent=2))
print('Prepared physical reuse from r1; does not reuse its failed CSI netlist')
