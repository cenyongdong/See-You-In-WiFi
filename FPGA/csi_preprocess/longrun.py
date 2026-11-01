"""Prepare and observe the authorized 30-minute dataset run; reuse qualified PL."""
from pathlib import Path
import argparse,collections,hashlib,json,os,shutil,subprocess,sys,tarfile,time,urllib.request
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'.local/csi-longrun-20261031-r1'
NAME='pose180-csi-longrun-20261031-r1'
BASE=ROOT/'.local/csi-preprocess-20261031-r3/pose180-csi-preprocess-20261031-r3'
CONTROL=ROOT/'software/pose180_pipeline/control'
sys.path.insert(0,str(CONTROL))
from dataset_input import prepare_dataset,prepare_playlist,sha
DOCKER='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
NODE='C:/Users/cenyongdong/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def save(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def command(label,argv):
 with (WORK/'reports'/(label+'.log')).open('w',encoding='utf-8') as f:
  p=subprocess.Popen(list(map(str,argv)),stdout=f,stderr=subprocess.STDOUT)
  save(WORK/'reports'/(label+'-process.json'),dict(pid=p.pid,argv=list(map(str,argv)),started=time.time()))
  rc=p.wait()
 save(WORK/'reports'/(label+'-exit.json'),dict(native_exit=rc))
 if rc:raise RuntimeError(label+' failed: inspect original log')
def prepare():
 import numpy as np
 origin=Path('D:/Person-in-WIFI-3D/Person-in-WiFi-3D-repo/data/wifipose')
 folder=origin/'train_data';sequences=collections.defaultdict(list)
 for line in (folder/'train_data_list.txt').read_text(encoding='utf-8-sig').splitlines():
  stem=Path(line.strip()).stem
  if stem:
   seq,index=stem.rsplit('_',1);sequences[seq].append(int(index))
 candidates=[]
 for seq,indices in sequences.items():
  values=sorted(indices);runs=[];start=last=values[0]
  for value in values[1:]:
   if value!=last+1:runs.append((last-start+1,start));start=value
   last=value
  runs.append((last-start+1,start));count,start=max(runs)
  people=int(np.load(folder/'keypoint'/(seq+'_'+str(start)+'.npy'),allow_pickle=False).shape[0])
  if count>=290 and people in (1,2,3):candidates.append(dict(sequence=seq,start=start,count=290,people=people))
 # Longest available contiguous train runs; keep familiar recordings when possible,
 # then spread over recording environments. No inference-quality cherry-picking.
 selected=[];preferred={1:'S51_10',2:'S52_16',3:'S23_43'}
 buckets={}
 for people in (1,2,3):
  rows=sorted((c for c in candidates if c['people']==people),key=lambda c:(c['sequence']!=preferred[people],c['sequence']))
  buckets[people]=rows[:10]
  if len(buckets[people])!=10:raise ValueError('Insufficient continuous clips')
 for i in range(10):
  for people in (1,2,3):selected.append(buckets[people][i])
 save(WORK/'selection.json',dict(split='train',clips=selected,unique_windows=8700,playback_hz=15,
  unique_playback_seconds=580,repetitions=4,maximum_inputs=34800,active_run_seconds=1800,
  selection='30 complete 290-window contiguous runs; 10 per person count; labels only classify provenance',
  attribution='Person-in-WiFi 3D / Wiception3D, official Kaggle v1, CC BY 4.0; converted raw CSI, original authors retain attribution'))
 directories=[]
 for i,c in enumerate(selected):
  out=WORK/'clips'/('%02d-%s'%(i+1,c['sequence']))
  if not out.exists():prepare_dataset(origin,'train',c['sequence'],c['start'],290,15,out)
  directories.append(out);print('PREPARED',i+1,c['sequence'],flush=True)
 playlist=WORK/'playlist'
 if not playlist.exists():prepare_playlist(directories,[c['people'] for c in selected],playlist)
 print('PLAYLIST_READY',flush=True)
def package():
 release=WORK/NAME;release.mkdir(exist_ok=False)
 shutil.copytree(BASE/'board',release/'board',ignore=shutil.ignore_patterns('runs','next-boot.json','verified-boot.json','__pycache__'))
 board=release/'board'
 command('arm-build',[DOCKER,'exec','FPAI','cmake','--build','/tmp/csi-preprocess-20261031-r3-arm','--parallel','2','--target','pose180_demo'])
 command('arm-copy',[DOCKER,'cp','FPAI:/tmp/csi-preprocess-20261031-r3-arm/pose180_demo',board/'pose180_demo'])
 for name in ('dataset.json','dataset.piwcsi2'):shutil.copyfile(WORK/'playlist'/name,board/name)
 for name in ('input_config.py','startup.py'):shutil.copyfile(CONTROL/name,board/name)
 ident=json.loads((board/'identity.json').read_text())
 ident.update(package=NAME,dataset_repetitions=4,verified_boot_ids=[],board_tested=False)
 for name in ident['files']:ident['files'][name]=sha(board/name)
 save(board/'identity.json',ident)
 for name in ('stop.sh','status.sh','check.sh','prepare-boot.sh','recover.sh'):shutil.copyfile(BASE/name,release/name)
 (release/'start.sh').write_text('#!/bin/sh\nset -eu\nroot=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec python3 "$root/board/startup.py" start --seconds 1800 "$@"\n',encoding='utf-8',newline='\n')
 # Reboot only: reuse the actual qualified BOOT. No install/reset or SDK retry.
 (release/'reboot.py').write_text('''import json,subprocess,sys\nfrom pathlib import Path\nr=Path(__file__).resolve().parent\nsys.path.insert(0,str(r/'board'))\nimport startup\nfrom run_hdmi_trial import owners\nif owners():raise RuntimeError('Device owned')\nidentity=startup.read(r/'board/identity.json')\nstartup.verify_boot(identity)\nreceipt=startup.read(r/'board/next-boot.json')\nif receipt['previous_boot_id']!=startup.boot_id():raise RuntimeError('Prepare-boot does not match current boot')\nf=r/'reboot-issued.json'\nwith f.open('x') as stream:json.dump(dict(previous_boot_id=startup.boot_id(),BOOT_sha256=identity['BOOT_sha256'],BOOT_writes=0),stream)\np=subprocess.Popen(['/bin/sh','-c','sleep 2; exec /sbin/reboot'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)\nprint(json.dumps(dict(reboot_issued=True,pid=p.pid)))\n''')
 shutil.copyfile(Path(__file__).with_name('longrun_monitor.py'),release/'monitor.py')
 shutil.copyfile(WORK/'selection.json',release/'selection.json')
 archive=WORK/(NAME+'.tar.gz')
 def perms(member):
  if member.name.endswith('.sh') or Path(member.name).name in ('pose180_demo','board_benchmark','overlay_tests'):member.mode=0o755
  return member
 with tarfile.open(archive,'w:gz',compresslevel=1) as tar:tar.add(release,arcname=NAME,filter=perms)
 save(WORK/'reports/package.json',dict(archive=str(archive),sha256=sha(archive),BOOT_sha256=ident['BOOT_sha256'],software_sha256=ident['files']['pose180_demo'],BOOT_writes=0,normal_reboots=1,SDK_attempts=1,seconds=1800))
 print((WORK/'reports/package.json').read_text(),flush=True)
def transport():
 command('transport-'+time.strftime('%H%M%S'),[sys.executable,Path(__file__).with_name('board_transport.py'),*sys.argv[2:],
  '--package',NAME,'--evidence-directory',WORK/'reports/board'])
def pc():
 out=WORK/'reports/pc';out.mkdir(exist_ok=False);children=[];handles=[]
 for mode,port in [('raw',39381),('view',39380)]:
  argv=[NODE,ROOT/'software/pose180_pipeline/host/resident.mjs','--mode',mode,'--board','192.168.126.49','--local-address','192.168.126.100','--http-port',str(port),'--metrics-port','0','--seconds','1950']
  if mode=='raw':argv+=['--output',out/'actual.full']
  else:argv+=['--metrics-state-url','http://127.0.0.1:39381/api/state']
  stdout=(out/(mode+'.stdout.log')).open('w');stderr=(out/(mode+'.stderr.log')).open('w');handles.extend([stdout,stderr])
  p=subprocess.Popen(list(map(str,argv)),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW);children.append(p)
 save(out/'processes.json',[dict(pid=p.pid,started=time.time(),bounded_seconds=1950) for p in children])
 with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
  while any(p.poll() is None for p in children):
   row=dict(at=time.time(),monotonic=time.monotonic())
   for mode,port in [('raw',39381),('view',39380)]:
    try:
     with urllib.request.urlopen('http://127.0.0.1:%d/api/state'%port,timeout=2) as response:v=json.load(response)
     frame=v.pop('frame',None)
     if frame:v['frame_identity']={k:frame.get(k) for k in ('session','frame','sequence','source_ns','score','metrics')};v['pose_count']=len(frame.get('poses',[]))
     row[mode]=v
    except Exception as e:row[mode]=dict(error=str(e))
   f.write(json.dumps(row)+'\n');f.flush();time.sleep(5)
 for f in handles:f.close()
 save(out/'exit.json',[dict(pid=p.pid,native_exit=p.returncode) for p in children]);print('PC observers ended',flush=True)
def progress():
 argv=[sys.executable,str(Path(__file__).with_name('board_transport.py')),'progress','ssh',
  'tail -n 1 /root/'+NAME+'/monitor/samples.jsonl','--package',NAME,'--evidence-directory',str(WORK/'reports/board')]
 result=subprocess.run(argv,capture_output=True,text=True)
 if result.returncode:print(result.stdout+result.stderr);raise SystemExit(result.returncode)
 v=json.loads(result.stdout);s=v.get('status') or v.get('outcome.json',{}).get('final_status',{})
 service=v.get('service-status.json',{});csi=v.get('csi',{})
 last=(WORK/'reports/pc/samples.jsonl').read_text().splitlines()[-1];local=json.loads(last)
 print(json.dumps(dict(board_seconds=service.get('elapsed',v.get('outcome.json',{}).get('seconds')),
  state=s.get('state'),inferred=s.get('inferred'),hdmi=s.get('adopted'),replaced=s.get('replaced'),
  malformed=s.get('malformed'),RSS_KiB=service.get('RSS_KiB'),fds=service.get('fds'),threads=service.get('threads'),
  csi_calls=csi.get('calls'),csi_faults=csi.get('faults'),csi_fallbacks=csi.get('fallbacks'),
  underflow=v.get('overlay_underflow_seen'),outcome=v.get('outcome.json',{}).get('native_exit'),
  PC={m:{k:local.get(m,{}).get(k) for k in ('received','phase','invalid','recordDrops','new_results_hz','age_ms','pose_count')} for m in ('raw','view')})))
def view_restart():
 out=WORK/'reports/pc';prior=json.loads((out/'view-restart-before.json').read_text(encoding='utf-8-sig'))
 processes=json.loads((out/'processes.json').read_text());seconds=max(1,int(processes[1]['started']+1950-time.time()))
 argv=[NODE,str(ROOT/'software/pose180_pipeline/host/resident.mjs'),'--mode','view','--board','192.168.126.49',
  '--local-address','192.168.126.100','--http-port','39380','--metrics-port','0',
  '--metrics-state-url','http://127.0.0.1:39381/api/state','--seconds',str(seconds)]
 with (out/'view-fixed.stdout.log').open('w') as stdout,(out/'view-fixed.stderr.log').open('w') as stderr:
  p=subprocess.Popen(argv,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  save(out/'view-fixed-process.json',dict(pid=p.pid,started=time.time(),seconds=seconds,argv=argv,
   reason='User reported missing processing time; intentional local view restart only; raw/board/HDMI remain running',
   before_received=prior['received']))
  print('VIEW_RESTARTED',p.pid,seconds,flush=True);rc=p.wait()
 save(out/'view-fixed-exit.json',dict(pid=p.pid,native_exit=rc));print('Fixed view ended',flush=True)
if __name__=='__main__':
 WORK.mkdir(exist_ok=True);(WORK/'reports').mkdir(exist_ok=True)
 {'prepare':prepare,'package':package,'transport':transport,'pc':pc,'progress':progress,'view-restart':view_restart}[sys.argv[1]]()
