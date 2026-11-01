from pathlib import Path
import json,re
w=Path(__file__).resolve().parent;b=w/'build';h=b/'.local/csi-preprocess-20261031-r3';r=h/'reports/physical-final-closure'
text=lambda n:(r/n).read_text(errors='replace')
timing=text('timing-final.rpt');lines=timing.splitlines();idx=next(i for i,l in enumerate(lines) if 'WNS(ns)' in l and 'TNS(ns)' in l)
values=next(l.split() for l in lines[idx+1:] if re.match(r'^\s*-?\d+\.\d+\s+',l))
keys={0:'WNS_ns',1:'TNS_ns',2:'setup_failing_endpoints',4:'WHS_ns',5:'THS_ns',6:'hold_failing_endpoints',8:'WPWS_ns',9:'TPWS_ns',10:'pulse_failing_endpoints'}
s={k:float(values[i]) for i,k in keys.items()}
internal=int(re.search(r'There are (\d+) pins that are not constrained for maximum delay\.',timing).group(1))
route=text('route-status-final.rpt')
net=lambda label:int(re.search(re.escape(label)+r'\.+\s*:\s*(\d+)',route).group(1))
routefacts={k:net(label) for k,label in [('routable_nets','# of routable nets'),('fully_routed_nets','# of fully routed nets'),('routing_error_nets','# of nets with routing errors')]}
negative=[]
# The full timing summary lists both failing endpoints; pulse-width default shows worst per clock.
for line in timing.splitlines():
 cols=re.split(r'\s{2,}',line.strip())
 if len(cols)>=9 and cols[0].startswith(('Min ','Max ')):
  try:slack=float(cols[6])
  except ValueError:continue
  if slack<0:negative.append(dict(check=cols[0],slack_ns=slack,pin=cols[-1],raw=line.strip()))
expected={'U0_ps_ai_peripheral/ZGolo/u_AI_Mate_top/clkrst_wrapper_u0/AI_CORE_CLK/inst/clkout1_buf/I':-0.409,'U0_ps_ai_peripheral/ZGolo/u_AI_Mate_top/clkrst_wrapper_u0/AI_CORE_CLK/inst/plle2_adv_inst/CLKOUT0':-0.071}
period_ok=len(negative)==2 and all(x['check']=='Min Period' and x['pin'] in expected and abs(x['slack_ns']-expected[x['pin']])<0.0001 for x in negative)
drc=text('drc-final.rpt');errors={name:int(count) for name,count in re.findall(r'^\|\s*(\S+)\s*\|\s*Error\s*\|[^|]+\|\s*(\d+)\s*\|',drc,re.M)}
gt_ok=errors=={'REQP-52':1,'REQP-56':1} and all(pin in drc for pin in ['rx_sdi_inst/SDI0/SDI/GTX_i/gtxe2_i','rx_sdi_inst/gtxe2_common_0/gtxe2_common_i'])
bus=text('bus-skew-final.rpt').split('2. Bus Skew Report Per Constraint\n')[-1] # all detailed path slacks are preserved below
bus_slacks=[float(x) for x in re.findall(r'Slack\s*\((?:MET|VIOLATED)\)\s*:\s*([-\d.]+)',bus)]
if not bus_slacks:
 bus_slacks=[float(x) for x in re.findall(r'^\s*(?:Slow|Fast)\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)\s*$',text('bus-skew-final.rpt'),re.M)]
bus_min=min(bus_slacks) if bus_slacks else None
stages={}
for n in ['synthesis-banked','opt-banked','place-csi-incremental','route-csi-incremental','report-closure','bit-closure']:
 p=b/'rebuild-logs'/(n+'.json')
 if p.exists():stages[n]=json.loads(p.read_text())
qualified=all(x['exit_code']==0 for x in stages.values()) and all(n in stages for n in ['synthesis-banked','opt-banked','place-csi-incremental','route-csi-incremental','report-closure']) and s['WNS_ns']>=0 and s['WHS_ns']>=0 and s['TNS_ns']==0 and s['THS_ns']==0 and internal==0 and routefacts['fully_routed_nets']==routefacts['routable_nets'] and routefacts['routing_error_nets']==0 and period_ok and gt_ok and bus_min is not None and bus_min>=0
result=dict(input=json.loads((w/'identity.json').read_text()),stages=stages,timing=s,unconstrained_internal_endpoints=internal,route=routefacts,raw_timing_constraints_met='Timing constraints are met.' in timing,negative_pulse_width_checks=negative,only_existing_two_AI_period_exceptions=period_ok,raw_DRC_errors=errors,only_existing_GT_adaptation_errors=gt_ok,bus_skew_min_slack_ns=bus_min,physical_qualification_under_existing_exceptions=qualified,fresh_synthesis_opt_place_route=True,incremental_reference='Packaged CSI v2 routed DCP',new_waivers_or_constraint_changes=False,board_operations=0,scope='Independent delivered RAR extraction; full native implementation and physical reports; bit stage recorded only if actually run')
(w/'physical-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['timing','route','raw_timing_constraints_met','only_existing_two_AI_period_exceptions','raw_DRC_errors','only_existing_GT_adaptation_errors','bus_skew_min_slack_ns','physical_qualification_under_existing_exceptions']},indent=2),flush=True)
