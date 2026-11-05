from pathlib import Path
import hashlib,json,subprocess,time
R=Path.cwd();W=R/'.local/r7-board-20261104-r1';P=W/'source/pose180-current-sources-20261104-r7';O=W/'application';O.mkdir()
def mapped(p):return '/workspace/'+p.relative_to(R).as_posix()
steps=[]
def run(name,args):
    start=time.time()
    with (O/(name+'.log')).open('wb') as log:p=subprocess.run(list(map(str,args)),stdout=log,stderr=subprocess.STDOUT)
    steps.append(dict(stage=name,command=list(map(str,args)),native_exit=p.returncode,seconds=time.time()-start))
    (O/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
    if p.returncode:raise RuntimeError((O/(name+'.log')).read_text(errors='replace')[-4000:])
    print(name,'PASS',flush=True)
for arch,preset in [('arm64','csi-v3-arm64'),('native','native-offline')]:
    build='/tmp/r7-board-20261104-r1-'+arch
    if subprocess.run(['docker','exec','FPAI','test','-e',build]).returncode==0:raise FileExistsError(build)
    run(arch+'-configure',['docker','exec','-w',mapped(P),'FPAI','cmake','--preset',preset,'-B',build])
    run(arch+'-build',['docker','exec','FPAI','cmake','--build',build,'--parallel','2'])
run('native-tests',['docker','exec','FPAI','ctest','--test-dir','/tmp/r7-board-20261104-r1-native','--output-on-failure'])
run('copy-application',['docker','cp','FPAI:/tmp/r7-board-20261104-r1-arm64/bin/pose180_demo',O/'pose180_demo'])
run('elf-identity',['docker','exec','FPAI','aarch64-linux-gnu-readelf','-h','/tmp/r7-board-20261104-r1-arm64/bin/pose180_demo'])
exe=O/'pose180_demo';(O/'identity.json').write_text(json.dumps(dict(source_package_sha256=json.loads((W/'download.json').read_text())['sha256'],application_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),bytes=exe.stat().st_size,SDK_initialized=False),indent=2)+'\n')
print((O/'identity.json').read_text(),flush=True)
