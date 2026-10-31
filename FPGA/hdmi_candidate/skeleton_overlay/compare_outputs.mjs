// Compare retained real board outputs, using the unchanged production decoder.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {decodeFull,FULL_BYTES,INPUT_BYTES} from '../../../software/pose180_pipeline/host/full_record.mjs';

function stats(xs) {
    xs.sort((a,b)=>a-b);
    return xs.length ? {samples:xs.length,mean:xs.reduce((a,b)=>a+b,0)/xs.length,
        p95:xs[Math.ceil(.95*xs.length)-1],max:xs.at(-1),p95_method:'nearest rank'} : {samples:0};
}
function load(directory) {
    const frames=new Map();
    for(const name of fs.readdirSync(directory).filter(n=>n.endsWith('.full'))) {
        const bytes=fs.readFileSync(path.join(directory,name));
        if(bytes.length%FULL_BYTES) throw new Error(`Partial record: ${name}`);
        for(let i=0;i<bytes.length;i+=FULL_BYTES) {
            const raw=bytes.subarray(i,i+FULL_BYTES),frame=decodeFull(raw);
            if(frames.has(frame.sequence)) throw new Error(`Duplicate sequence: ${frame.sequence}`);
            frames.set(frame.sequence,{raw,frame});
        }
    }
    return frames;
}
const [psDir,plDir,output]=process.argv.slice(2);
if(!output) throw new Error('Usage: node compare_outputs.mjs PS_RING PL_RING OUTPUT_JSON');
const ps=load(psDir),pl=load(plDir),byInput=new Map(),pairs=[];
const inputKey=row=>createHash('sha256').update(row.raw.subarray(384,384+INPUT_BYTES)).digest('hex');
for(const row of ps.values()) {
    const key=inputKey(row);
    if(!byInput.has(key)) byInput.set(key,[]);
    byInput.get(key).push(row);
}
for(const row of pl.values()) {
    const candidates=byInput.get(inputKey(row));
    if(candidates?.length) pairs.push([candidates.shift(),row]);
}
let inputsEqual=0,outputsEqual=0,maxAbsError=0;
for(const [aRow,bRow] of pairs) {
    const a=aRow.raw,b=bRow.raw;
    if(a.subarray(384,384+INPUT_BYTES).equals(b.subarray(384,384+INPUT_BYTES))) ++inputsEqual;
    if(a.subarray(384+INPUT_BYTES).equals(b.subarray(384+INPUT_BYTES))) ++outputsEqual;
    for(let i=384+INPUT_BYTES;i<FULL_BYTES;i+=4)
        maxAbsError=Math.max(maxAbsError,Math.abs(a.readFloatLE(i)-b.readFloatLE(i)));
}
const metrics=frames=>Object.fromEntries(['process_ms','preprocess_ms','forward_ms','output_ms','queue_ms']
    .map(key=>[key,stats([...frames.values()].map(row=>row.frame.metrics[key]))]));
const range=frames=>{const xs=[...frames.keys()].sort((a,b)=>Number(a)-Number(b));return xs.length?[xs[0],xs.at(-1)]:[];};
const result={scope:'Retained bounded-ring records only; original decoder validates finite inputs and all 180 candidate outputs. Pairs are matched by input payload hash and checked byte-for-byte because dropped inputs shift publication sequence numbers. Timing/session metadata are excluded from output comparison.',
    ps_records:ps.size,pl_records:pl.size,paired_records:pairs.length,
    sequence_ranges:{ps:range(ps),pl:range(pl)},
    identical_input_pairs:inputsEqual,identical_output_pairs:outputsEqual,maximum_output_absolute_error:pairs.length?maxAbsError:null,
    ps_metrics:metrics(ps),pl_metrics:metrics(pl)};
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
