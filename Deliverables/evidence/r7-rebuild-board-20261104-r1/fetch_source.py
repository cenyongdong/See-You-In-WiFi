from pathlib import Path
import hashlib,json,subprocess,time
from urllib.request import Request,urlopen
R=Path.cwd();W=R/'.local/r7-board-20261104-r1';NAME='pose180-current-sources-20261104-r7'
URL='https://github.com/cenyongdong/See-You-In-WiFi/releases/download/deploy-r4-20261031/'
EXPECTED='4481f7503f4093ce4fe5cd16738b4580465d00e0cf221b9134eab27e8c0cee08'
for name in (NAME+'.rar.sha256',NAME+'.rar'):
    digest=hashlib.sha256();path=W/name
    with urlopen(Request(URL+name,headers={'User-Agent':'r7-independent-board-verification'}),timeout=60) as response,path.open('xb') as output:
        while chunk:=response.read(1024*1024):output.write(chunk);digest.update(chunk)
    if name.endswith('.rar'):
        assert digest.hexdigest()==EXPECTED
        assert (W/(NAME+'.rar.sha256')).read_text().split()[0]==EXPECTED
        (W/'download.json').write_text(json.dumps(dict(url=URL+name,bytes=path.stat().st_size,sha256=digest.hexdigest(),downloaded_from_release=True),indent=2)+'\n')
    print('Downloaded and checked',name,flush=True)
source=W/'source';source.mkdir()
steps=[]
def run(name,args):
    start=time.time()
    with (W/(name+'.log')).open('wb') as log:p=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT)
    steps.append(dict(stage=name,command=list(map(str,args)),native_exit=p.returncode,seconds=time.time()-start))
    (W/'source-steps.json').write_text(json.dumps(steps,indent=2)+'\n')
    if p.returncode:raise RuntimeError((W/(name+'.log')).read_text(errors='replace')[-2500:])
    print(name,'PASS',flush=True)
run('archive-test',[R/'.local/release-20261031-r3/rar-tool/Rar.exe','t','-idq',W/(NAME+'.rar')])
run('extract',[R/'.local/release-20261031-r3/rar-tool/Rar.exe','x','-idq',W/(NAME+'.rar'),str(source)+'\\'])
run('source-manifest',['python',source/NAME/'tools/check_package.py'])
run('prepare-fpga',['python',source/NAME/'tools/build_fpga.py','prepare','--build-dir',W/'hardware','--procise','C:/FudanMicro/Procise'])
print('Fresh release source ready',flush=True)
