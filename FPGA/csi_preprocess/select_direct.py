"""Use the successful direct route; do not run unnecessary post-route physopt."""
from run import WORK
import json
r=WORK/'reports'
assert json.loads((r/'route-direct-execution.json').read_text())['native_exit']==0
for name in ('report-closure.tcl','bit-closure.tcl'):
 p=r/name;p.write_text(p.read_text().replace('pipeline-routed-closure.dcp','pipeline-routed-direct.dcp'))
p=WORK/'qualify_closure.py'
v=p.read_text().replace("'route-direct', 'physopt-direct', 'report-closure'", "'route-direct', 'report-closure'")
v=v.replace("'route-direct','physopt-direct','report-closure'", "'route-direct','report-closure'")
v=v.replace('pipeline-routed-closure.dcp','pipeline-routed-direct.dcp')
p.write_text(v)
(r/'implementation-selection.json').write_text(json.dumps(dict(checkpoint='pipeline-routed-direct.dcp',
 reason='Native direct-route setup and hold are positive; final report/qualification still required.',
 post_route_physopt_run=False),indent=2))
print('Selected direct routed checkpoint for final reports and bit')
