"""Host-only identity/argument checks, no Linux process or device operations."""
import json,sys,types
from run import WORK
root=WORK/'pose180-skeleton-overlay-20261031-r2/board'
# fcntl is never called here; allow importing the Linux launcher on Windows.
if sys.platform=='win32':sys.modules['fcntl']=types.ModuleType('fcntl')
sys.path.insert(0,str(root))
import startup
ident=json.loads((root/'identity.json').read_text())
startup.verify_files(root,ident)
selected=startup.select_input(root,ident,None,None)
argv=startup.command(root,root/'unused-test-run',123,120,selected)
opts=dict(zip(argv[1::2],argv[2::2]))
assert opts['--renderer-backend']=='pl' and opts['--hardware-profile']=='probe-free-drain-overlay-v1'
assert opts['--filter-backend']=='cpu' and opts['--top-k']=='3' and opts['--score-threshold']=='0.2'
result=dict(package_files_verified=True,renderer=opts['--renderer-backend'],hardware_profile=opts['--hardware-profile'],
            selection=selected,SDK_started=False,board_access=False,scope='host-only files/arguments; no process-control emulation')
(WORK/'reports/software-package-check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
