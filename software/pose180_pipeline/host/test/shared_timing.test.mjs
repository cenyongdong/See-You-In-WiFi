import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const wait=ms=>new Promise(r=>setTimeout(r,ms));
test('view reuses local raw timing, tracks updates, and clears disconnected telemetry',async()=>{
 let connected=true,sequence=1,processMs=13,child;const clients=new Set();
 const source=net.createServer(s=>{clients.add(s);s.on('close',()=>clients.delete(s));});
 await new Promise(r=>source.listen(0,'127.0.0.1',r));
 const raw=http.createServer((req,res)=>res.end(JSON.stringify({mode:'raw',connected,age_ms:10,
  frame:{session:'10',sequence:String(sequence),frame:String(sequence),source_ns:String(sequence*1000000),metrics:{process_ms:processMs}}})));
 await new Promise(r=>raw.listen(0,'127.0.0.1',r));
 const reserve=net.createServer();await new Promise(r=>reserve.listen(0,'127.0.0.1',r));
 const port=reserve.address().port;await new Promise(r=>reserve.close(r));
 let output='';
 const timer=setInterval(()=>{sequence++;const frame={schema:'PIWVIEW1',version:1,replay:false,session:'10',frame:String(sequence),sequence:String(sequence),source_ns:String(sequence*1000000),hold_ms:250,poses:[],raw_poses:[]};for(const s of clients)s.write(JSON.stringify(frame)+'\n');},30);
 try {
  child=spawn(process.execPath,[fileURLToPath(new URL('../resident.mjs',import.meta.url)),
   '--mode','view','--board','127.0.0.1','--port',String(source.address().port),'--http-port',String(port),
   '--metrics-port','0','--metrics-state-url',`http://127.0.0.1:${raw.address().port}/api/state`,'--seconds','6'],{windowsHide:true});
  child.stdout.on('data',b=>output+=b);
  const get=async()=>{try{return await(await fetch(`http://127.0.0.1:${port}/api/state`)).json();}catch{return null;}};
  async function until(check){for(let i=0;i<80;i++){const s=await get();if(s&&check(s))return s;await wait(30);}throw Error('Shared timing did not update: '+output);}
  const state=await until(s=>s.processing.connected&&s.processing.samples>0);
  assert.equal(state.processing.median_ms,13);
  processMs=21;await until(s=>s.processing.p95_ms===21);
  connected=false;await until(s=>!s.processing.connected);
  assert((await get()).received>state.received,'Timing failure interrupted poses');
 } finally {
  clearInterval(timer);for(const s of clients)s.destroy();source.close();raw.close();raw.closeAllConnections();
  if(child&&child.exitCode===null)await new Promise(r=>child.once('exit',r));
 }
});
