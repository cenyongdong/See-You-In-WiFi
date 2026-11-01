"""Exact project dependencies for the qualified CSI v3 FPGA rebuild (no tool install)."""
from pathlib import Path
REF='.local/hdmi-boot-witness-20261019-r23/reference'
HW='.local/csi-preprocess-20261031-r3'
INCREMENTAL='.local/csi-preprocess-20261031-r2/pipeline-routed-csi-incremental.dcp'
def collect(root):
 root=Path(root);files={}
 def add(p):
  if not p.is_file():raise FileNotFoundError(p)
  if p.is_symlink():raise ValueError('Dependency link: '+str(p))
  files[p.relative_to(root).as_posix()]=p
 def tree(rel):
  for p in (root/rel).rglob('*'):
   if p.is_file() and p.name!='AI_Mate_no_detpost.edif' and not any(x in p.name for x in ('_sim_netlist','_funcsim','_timesim')) and p.suffix.lower() not in {'.log','.jou','.bak','.wdb','.rpt','.pb','.html','.pdf'} and '__pycache__' not in p.parts:add(p)
 for suffix in ['rtl','fpai_demo_vivado.srcs','constrs_1','PS_AI IP'] :tree(REF+'/'+suffix)
 for suffix in ['030ai','edif','edif_transform','process_control','xadc_filter','paspd/fmsh/030ai']:tree(REF+'/ip_patch/'+suffix)
 for p in (root/REF/'ip_patch').iterdir():
  if p.is_file() and p.suffix.lower()!='.bak':add(p)
 for suffix in ['paspd/fmsh/xc7z030.paspd','paspd/xilinx/xc7z030.paspd','tools/bitfile_replace.tcl','tools/mig_auto_winCheck.tcl','tools/iostandard_check.tcl','tools/netdelay_check.tcl'] :add(root/REF/'ip_patch'/suffix)
 for rel in [REF+'/fpai_demo_vivado.xpr',REF+'/fpai_demo_vivado.runs/synth_hp2ready_r24/dont_touch.xdc','.local/hdmi-ps-release-20261020-r26/ps-export.dcp',INCREMENTAL]:add(root/rel)
 for n in ['candidate.bif','FSBL251210_ddr400_demo.out','bl31.elf','u-boot']:add(root/HW/'boot-package'/n)
 return files
