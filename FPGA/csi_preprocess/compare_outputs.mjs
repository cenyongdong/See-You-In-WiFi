import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {decodeFull,FULL_BYTES,INPUT_BYTES,SCORE_OFFSET,POSE_OFFSET} from '../../software/pose180_pipeline/host/full_record.mjs';
const [psDir,plDir,output,referenceDescription='PS preprocessor reference']=process.argv.slice(2);
if(!output)throw Error('PS full-record directory, PL directory, output JSON required');
function load(dir){const out=[];for(const name of fs.readdirSync(dir).filter(n=>n.endsWith('.full'))){
 const data=fs.readFileSync(path.join(dir,name));if(data.length%FULL_BYTES)throw Error('Partial full record');
 for(let off=0;off<data.length;off+=FULL_BYTES){const raw=data.subarray(off,off+FULL_BYTES);out.push({raw,frame:decodeFull(raw)});}
}return out;}
// Amplitude remains byte-identical on the actual official dataset. Match this
// unchanged feature plus original source/frame identity, never publication seq.
function key(row){const h=createHash('sha256');for(let k=0;k<180;++k)h.update(row.raw.subarray(384+k*240,384+k*240+120));
 return `${row.frame.frame}/${row.frame.source_ns}/${h.digest('hex')}`;}
const ps=load(psDir),pl=load(plDir),index=new Map();
for(const a of ps){const k=key(a);if(index.has(k))throw Error('Ambiguous reference input');index.set(k,a);}
let paired=0,identicalOutputs=0,bestChanged=0,inputPhaseMax=0,scoreMax=0,poseMax=0;
let identicalInputs=0,changedWithIdenticalInput=0,selectedPoseMax=0,selectedScoreMax=0,top3Changed=0;
const differences=[];
function selected(row){const a=Array.from({length:180},(_,i)=>({i,s:row.raw.readFloatLE(SCORE_OFFSET+4*i)}));return a.filter(v=>v.s>.2).sort((a,b)=>b.s-a.s||a.i-b.i).slice(0,3).map(v=>v.i);}
for(const b of pl){const a=index.get(key(b));if(!a)continue;++paired;
 const sameOutput=a.raw.subarray(SCORE_OFFSET).equals(b.raw.subarray(SCORE_OFFSET));
 const sameInput=a.raw.subarray(384,SCORE_OFFSET).equals(b.raw.subarray(384,SCORE_OFFSET));
 if(sameOutput)++identicalOutputs;if(sameInput)++identicalInputs;
 if(sameInput&&!sameOutput)++changedWithIdenticalInput;
 if(JSON.stringify(selected(a))!==JSON.stringify(selected(b)))++top3Changed;
 selectedScoreMax=Math.max(selectedScoreMax,Math.abs(a.frame.score-b.frame.score));
 for(let j=0;j<42;++j)selectedPoseMax=Math.max(selectedPoseMax,Math.abs(a.frame.joints[j]-b.frame.joints[j]));
 if(!sameOutput)differences.push({frame:b.frame.frame,source_ns:b.frame.source_ns,input_byte_identical:sameInput,best_candidate:a.frame.candidate,new_best_candidate:b.frame.candidate,reference_top3:selected(a),new_top3:selected(b)});
 if(a.frame.candidate!==b.frame.candidate)++bestChanged;
 for(let i=384;i<FULL_BYTES;i+=4){const delta=Math.abs(a.raw.readFloatLE(i)-b.raw.readFloatLE(i));
  if(i<SCORE_OFFSET && ((i-384)/4)%60>=30)inputPhaseMax=Math.max(inputPhaseMax,delta);
  else if(i>=SCORE_OFFSET && i<POSE_OFFSET)scoreMax=Math.max(scoreMax,delta);
  else if(i>=POSE_OFFSET)poseMax=Math.max(poseMax,delta);
 }
}
function metrics(rows){return Object.fromEntries(['process_ms','preprocess_ms','forward_ms','output_ms'].map(k=>{
 const a=rows.map(r=>r.frame.metrics[k]).sort((a,b)=>a-b);return [k,{samples:a.length,mean:a.reduce((a,b)=>a+b,0)/a.length,p95:a[Math.ceil(.95*a.length)-1]}];}));}
const result={scope:'Retained real NPU outputs; paired by unchanged amplitude bytes and original frame/source identity. Not a new accuracy/ground-truth or long-duration test.',
 reference_description:referenceDescription,
 ps_records:ps.length,pl_records:pl.length,paired_records:paired,unpaired_pl_records:pl.length-paired,
 identical_output_pairs:identicalOutputs,best_candidate_changed:bestChanged,input_phase_max_abs_rad:inputPhaseMax,
 identical_input_pairs:identicalInputs,changed_output_with_identical_input:changedWithIdenticalInput,
 selected_best_pose_max_abs:selectedPoseMax,selected_best_score_max_abs:selectedScoreMax,top3_selection_changed:top3Changed,different_output_pairs:differences,
 score_max_abs:scoreMax,all_candidate_pose_max_abs:poseMax,ps_metrics:metrics(ps),pl_metrics:metrics(pl)};
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
if(!paired)process.exitCode=2;
