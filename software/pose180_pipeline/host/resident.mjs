// Optional demo subscriber. No input pacing, archive ACK or board control.
import fs from 'node:fs';
import path from 'node:path';
import net from 'node:net';
import http from 'node:http';
import {Worker} from 'node:worker_threads';
import {fileURLToPath} from 'node:url';
import {decodeFull, selectTopPoses, FULL_BYTES, FullRecordReader, ProcessingWindow} from './full_record.mjs';
import {PresentationReader, decodePresentation, visiblePresentation} from './presentation.mjs';

const options = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
	if (!process.argv[i + 1] || options.has(process.argv[i]))
		throw new Error('Expected unique --option value');
	options.set(process.argv[i], process.argv[i + 1]);
}
const take = (k, f) => {
	const v = options.get(k) ?? f;
	options.delete(k);
	return v;
};
const mode = take('--mode', 'view'), replay = take('--replay', '');
const board = take('--board', '192.168.126.49'),
	  port = Number(take('--port', mode === 'view' ? '39385' : '39383'));
if (!['raw', 'view'].includes(mode) || replay && mode !== 'view')
	throw new Error('Invalid presentation mode');
const httpPort = Number(take('--http-port', '39380')), output = take('--output', '');
const metricsPort = Number(take('--metrics-port', '39383'));
const metricsStateUrl = take('--metrics-state-url', '');
if (metricsStateUrl) {
	const url = new URL(metricsStateUrl);
	if (url.protocol !== 'http:' || !['127.0.0.1', '[::1]', 'localhost'].includes(url.hostname) ||
		url.username || url.password || mode !== 'view' || replay)
		throw new Error('Shared timing requires a local raw observer and live view mode');
}
const localAddress = take('--local-address', '');
const seconds = Number(take('--seconds', '0')), mock = take('--mock', '0') === '1';
if (options.size || ![port, httpPort].every(n => Number.isInteger(n) && n > 0 && n <= 65535) ||
	!Number.isInteger(metricsPort) || metricsPort < 0 || metricsPort > 65535 || !Number.isFinite(seconds) ||
	seconds < 0 || localAddress && !net.isIP(localAddress))
	throw new Error('Invalid options');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
let worker, busy = false, pending, recordDrops = 0, recorded = 0, archiveError = '', socket, timer,
			runtimeTimer, closed = false;
let last = null, lastAt = 0, received = 0, invalid = 0, duplicates = 0, reconnects = 0, connected = false,
	used = 0;
const recent = []; // At most 64 reception times, independent of run duration.
const processing = new ProcessingWindow(), telemetryReader = new FullRecordReader(), subscribers = new Set();
let telemetrySocket, telemetryTimer, telemetryConnected = false, telemetryInvalid = 0, broadcastTimer,
									 healthTimer;
const raw = Buffer.alloc(FULL_BYTES);
const viewReader = new PresentationReader();
let replayTimer, restartReplay;
let replayEnded = false;
const connection = {board, port, requested_local_address : localAddress || null,
	attempts : 0, local_address : null, connect_ms : null, first_result_ms : null, last_error : null};
let connectionStarted = 0, reportedError = '', lastErrorLog = -Infinity;

function boardSocket(targetPort) {
	const client = net.createConnection({host : board, port : targetPort,
		...(localAddress ? {localAddress} : {})});
	// Bound the TCP handshake separately from a healthy connection's idle time.
	// An absent temporary address must not leave an OS-level SYN pending for ages.
	const deadline = setTimeout(() => client.destroy(Object.assign(
		new Error('Board TCP connection timed out'), {code : 'ETIMEDOUT'})), 1500);
	client.once('connect', () => {
		clearTimeout(deadline);
		client.setTimeout(30000);
	});
	client.once('close', () => clearTimeout(deadline));
	client.setKeepAlive(true, 1000);
	return client;
}

function accept(next) {
	if (last && next.session === last.session && BigInt(next.sequence) <= BigInt(last.sequence)) {
		++duplicates;
		return;
	}
	if (last && next.session !== last.session)
		recent.length = 0;
	last = next;
	lastAt = performance.now();
	if (!replay && connection.first_result_ms === null) {
		connection.first_result_ms = Math.round(lastAt - connectionStarted);
		console.log('PC_FIRST_RESULT', JSON.stringify(connection));
	}
	++received;
	recent.push(lastAt);
	if (recent.length > 64)
		recent.shift();
	processing.observeView(next, lastAt);
	if (next.metrics)
		processing.observeResult(next, lastAt);
	scheduleBroadcast();
}

// The optional timing subscriber never sends ACKs or controls the board.
// A missing/busy raw port only removes timing numbers, not the filtered pose.
function connectTelemetry() {
	if (metricsStateUrl) {
		pollSharedTelemetry();
		return;
	}
	if (closed || replay || mode !== 'view' || !metricsPort)
		return;
	telemetryReader.reset();
	telemetrySocket = boardSocket(metricsPort);
	telemetrySocket.on('connect', () => {
		telemetryConnected = true;
	});
	telemetrySocket.on('data', chunk => {
		try {
			telemetryReader.push(chunk, f => processing.observeResult(f, performance.now()));
			scheduleBroadcast();
		} catch {
			++telemetryInvalid;
			telemetrySocket.destroy();
		}
	});
	telemetrySocket.on('timeout', () => telemetrySocket.destroy());
	telemetrySocket.on('error',
		() => {
		});
	telemetrySocket.on('close', () => {
		telemetryConnected = false;
		telemetryReader.reset();
		processing.reset();
		if (!closed)
			telemetryTimer = setTimeout(connectTelemetry, 500);
	});
}

// Reuse the local raw subscriber when it already owns the board's single
// raw-output connection. Only matching result identities feed the existing
// processing window; shared telemetry never supplies poses or drives inference.
async function pollSharedTelemetry() {
	if (closed)
		return;
	try {
		const response = await fetch(metricsStateUrl, {signal: AbortSignal.timeout(750)});
		if (!response.ok)
			throw new Error('Shared timing unavailable');
		const value = await response.json();
		if (closed)
			return;
		telemetryConnected = value.mode === 'raw' && value.connected === true &&
			Number.isFinite(value.age_ms) && value.age_ms < 1500;
		if (telemetryConnected && value.frame)
			processing.observeResult(value.frame, performance.now());
	} catch {
		telemetryConnected = false;
	}
	if (!closed) {
		scheduleBroadcast();
		telemetryTimer = setTimeout(pollSharedTelemetry, 250);
	}
}

if (output && (replay || mode !== 'raw'))
	throw new Error('Raw archive requires explicit --mode raw without replay');
if (output) {
	fs.mkdirSync(output, {recursive : false});
	worker =
		new Worker(new URL('./resident_archive.mjs', import.meta.url), {workerData : path.resolve(output)});
	worker.on('message', result => {
		busy = false;
		if (result.ok) {
			++recorded;
			archiveError = '';
		} else
			archiveError = result.error;
		if (pending) {
			const b = pending;
			pending = undefined;
			archive(b);
		}
	});
	worker.on('error', error => {
		archiveError = error.message;
		pending = undefined;
		worker = undefined;
		busy = false;
	});
}

function archive(bytes) {
	if (!worker)
		return;
	if (busy) {
		if (pending)
			++recordDrops;
		pending = Buffer.from(bytes);
		return;
	}
	busy = true;
	worker.postMessage(Buffer.from(bytes));
}

function connect() {
	if (closed)
		return;
	used = 0;
	viewReader.reset();
	connectionStarted = performance.now();
	++connection.attempts;
	connection.local_address = null;
	connection.connect_ms = null;
	connection.first_result_ms = null;
	socket = boardSocket(port);
	// Missing CSI windows do not imply a broken TCP session. The page marks
	// stale results independently; a 30 s idle watchdog still detects dead peers.
	socket.on('connect', () => {
		connected = true;
		++reconnects;
		connection.local_address = socket.localAddress;
		connection.connect_ms = Math.round(performance.now() - connectionStarted);
		connection.last_error = null;
	});
	socket.on('timeout', () => socket.destroy());
	socket.on('error', error => {
		connection.last_error = error.code || error.message;
		const now = performance.now();
		if (connection.last_error !== reportedError || now - lastErrorLog >= 10000) {
			reportedError = connection.last_error;
			lastErrorLog = now;
			console.log('PC_BOARD_WAIT', JSON.stringify(connection));
		}
	});
	socket.on('data', chunk => {
		if (mode === 'view') {
			try {
				viewReader.push(chunk, f => {
					if (f.replay)
						throw new Error('Historical record on live channel');
					accept(f);
				});
			} catch {
				++invalid;
				socket.destroy();
			}
			return;
		}
		for (let offset = 0; offset < chunk.length;) {
			const n = Math.min(FULL_BYTES - used, chunk.length - offset);
			chunk.copy(raw, used, offset, offset + n);
			used += n;
			offset += n;
			if (used !== FULL_BYTES)
				continue;
			used = 0;
			archive(raw);
			try {
				const next = decodeFull(raw);
				next.poses = selectTopPoses(raw, 3, 0.2);
				accept(next);
			} catch {
				++invalid;
				socket.destroy();
				break;
			}
		}
	});
	socket.on('close', () => {
		connected = false;
		used = 0;
		processing.reset();
		scheduleBroadcast();
		if (!closed)
			timer = setTimeout(connect, 250);
	});
}

const state = () => {
	const now = performance.now(), age = last ? Math.max(0, Math.floor(now - lastAt)) : null;
	const active = recent.filter(t => now - t < 2000);
	const hz = active.length > 1 ? (active.length - 1) * 1000 / (now - active[0]) : 0;
	const phase = !connected ? 'reconnecting'
		: !last				 ? 'waiting_input'
		: age >= 2000		 ? 'result_stale'
		: age >= 750		 ? 'waiting_result'
							 : 'live';
	return {
		mock,
		connected,
		received,
		invalid,
		duplicates,
		reconnects,
		recorded,
		recordDrops,
		archiveError,
		phase,
		connection : {...connection},
		new_results_hz : Number(hz.toFixed(2)),
		age_ms : age,
		mode,
		replay : !!replay,
		replayEnded,
		processing : {
			...processing.snapshot(now),
			connected : mode === 'raw' ? connected : telemetryConnected,
			invalid : telemetryInvalid
		},
		frame : last ? (mode === 'view' ? visiblePresentation(last, age) : last) : null
	};
};

function sendState(res, payload) {
	if (res.destroyed)
		return;
	if (res.writableLength + Buffer.byteLength(payload) > 65536) {
		res.destroy();
		return;
	}
	res.write(payload);
}

function broadcast() {
	broadcastTimer = undefined;
	if (!subscribers.size || closed)
		return;
	const payload = 'data: ' + JSON.stringify(state()) + '\n\n';
	for (const res of subscribers)
		sendState(res, payload);
}

function scheduleBroadcast() {
	if (!closed && !broadcastTimer)
		broadcastTimer = setTimeout(broadcast, 0);
}

const assets = new Map([
	[ '/scene.js', path.join(root, 'software/pose180_pipeline/host/web/scene.js') ],
	[
		'/vendor/three.module.js',
		path.join(root, 'software/pc_viewer/node_modules/three/build/three.module.js')
	],
	[ '/vendor/three.core.js', path.join(root, 'software/pc_viewer/node_modules/three/build/three.core.js') ],
	[
		'/vendor/OrbitControls.js',
		path.join(root, 'software/pc_viewer/node_modules/three/examples/jsm/controls/OrbitControls.js')
	]
]);
const page =
	`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${mode === 'raw' ? '滤波前 · 原始候选' : '滤波后 · 展示结果'}</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0b111b;color:#e5eef9;font:16px system-ui;overflow:hidden;display:flex;flex-direction:column;height:100dvh}header{padding:18px 24px 10px;flex:none}h1{font-size:20px;margin:0} .heading{display:flex;align-items:center;justify-content:space-between;gap:16px}#viewport{flex:1;min-height:0}#frame{color:#91a8bd;font:13px ui-monospace,monospace}.metrics{display:grid;grid-template-columns:1fr 1fr 1.35fr;gap:12px;margin:16px 0 12px}.metric{background:#101e2d;border:1px solid #263c50;border-radius:10px;padding:12px 16px;min-width:0}.label{color:#92acc3;font-size:12px;letter-spacing:.06em}.value{font-size:27px;line-height:1.45;font-weight:600;font-variant-numeric:tabular-nums}.unit{font-size:13px;color:#a0b6c9;font-weight:400}#phase{font-size:18px;color:#9ee8ce}#phase[data-state]:not([data-state=live]){color:#ffce84}button{background:#172838;color:#d8e9f6;border:1px solid #385364;border-radius:5px;padding:6px 12px;cursor:pointer}button[aria-pressed=true]{background:#294558;border-color:#82b9bf}nav{display:flex;gap:8px}@media(max-width:620px){header{padding:12px}.metrics{gap:6px;margin:10px 0}.metric{padding:9px}.value{font-size:22px}#phase{font-size:14px}h1{font-size:17px}}
</style>
<script type="importmap">{"imports":{"three":"/vendor/three.module.js","three/addons/controls/OrbitControls.js":"/vendor/OrbitControls.js"}}</script>
<header><div class="heading"><h1>Wi-Fi 姿态 · ${mode === 'raw' ? '滤波前' : '滤波后'}</h1><span id="frame">FRAME —</span></div>
<section class="metrics" aria-label="实时性能">
<div class="metric"><div class="label">板端处理耗时</div><div class="value"><span id="process">—</span> <span class="unit">ms</span></div></div>
<div class="metric"><div class="label">骨架更新率</div><div class="value"><span id="pose-rate">0.0</span> <span class="unit">次/秒</span></div></div>
<div class="metric"><div class="label">运行状态</div><div class="value" id="phase" data-state="waiting_input">等待首个真实结果</div></div>
</section><nav aria-label="视角"><button data-view="perspective" aria-pressed="true">透视</button><button data-view="front" aria-pressed="false">正面</button><button data-view="side" aria-pressed="false">侧面</button><button data-view="top" aria-pressed="false">俯视</button></nav></header><div id="viewport"></div>
<script type="module">import {createScene} from './scene.js';
const bones=[[0,1],[0,2],[0,3],[2,4],[2,5],[3,6],[3,7],[4,8],[5,7],[5,9],[6,10],[7,11],[9,12],[11,13]];
const el=id=>document.getElementById(id);let scene;const filtered=${mode === 'view'};
try{scene=createScene(el('viewport'),bones,()=>{},{maxPoses:3});}
catch(error){el('phase').textContent='三维渲染不可用';el('phase').dataset.state='error';console.error(error);}
if(scene){
const buttons=document.querySelectorAll('[data-view]');
buttons.forEach(button=>button.addEventListener('click',()=>{scene.view(button.dataset.view);buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));}));
const phases={live:'运行中',waiting_input:'等待首个真实结果',waiting_result:'等待新结果',result_stale:'结果已过期',reconnecting:'连接中断 · 自动重连'};
const text=(id,value)=>{const target=el(id);if(target.textContent!==value)target.textContent=value;};
let latest=null,receivedAt=0,streamLive=false,identity='',counted='',session='',lastMetrics=-Infinity,animation,disposed=false;
const updates=[];const stream=new EventSource('/api/events');
stream.onmessage=event=>{try{latest=JSON.parse(event.data);receivedAt=performance.now();streamLive=true;}catch{streamLive=false;}};
stream.onerror=()=>{streamLive=false;};
function draw(now){
 if(disposed)return;
 const s=latest,f=s?.frame,age=f?Math.max(0,(s.age_ms??0)+now-receivedAt):null;
 const connected=streamLive&&s?.connected;
 const phase=!connected?'reconnecting':!f?'waiting_input':age>=2000?'result_stale':age>=750?'waiting_result':'live';
 el('phase').dataset.state=phase;
 text('phase',(!streamLive?'观察端连接中断':(s.replay?'历史回放 · ':s.mock?'模拟测试 · ':s.mode==='raw'?'原始候选 · ':'')+(s.replayEnded?'播放结束':phases[phase])));
 let visible=f;
 if(filtered&&f)visible={...f,poses:connected?f.poses.filter(p=>p.age_ms+age<=f.hold_ms):[]};
 if(visible){
  if(session!==f.session){session=f.session;updates.length=0;counted='';}
  const resultId=f.session+':'+f.sequence;
  const key=resultId+':'+visible.poses.map(p=>p.track??p.candidate).join(',');
  if(key!==identity){scene.setPose(visible);identity=key;
   if(resultId!==counted&&connected&&age<750&&visible.poses.some(p=>!p.held)){
    updates.push(now);if(updates.length>512)updates.shift();counted=resultId;
   }
  }
 }else if(filtered&&identity){scene.setPose({poses:[]});identity='';}
 while(updates.length&&now-updates[0]>=5000)updates.shift();
 if(now-lastMetrics>=1000){
  lastMetrics=now;
  const rate=connected&&updates.length>1?(updates.length-1)*1000/Math.max(1,now-updates[0]):0;
  el('pose-rate').textContent=rate.toFixed(1);
  const m=s?.processing,hasTiming=connected&&!s.replay&&m?.connected&&m.samples>0&&now-receivedAt<1500;
  el('process').textContent=hasTiming?m.median_ms.toFixed(2):'—';
 }
 text('frame','FRAME '+(f?.frame??'—'));
 animation=requestAnimationFrame(draw);
}
animation=requestAnimationFrame(draw);
window.addEventListener('pagehide',()=>{disposed=true;stream.close();cancelAnimationFrame(animation);scene.dispose();},{once:true});
}</script></html>`;
const server = http.createServer((req, res) => {
	res.setHeader('Cache-Control', 'no-store');
	if (replay && req.method === 'POST' && req.url === '/api/replay/restart') {
		restartReplay();
		res.writeHead(204).end();
		return;
	}
	if (req.method !== 'GET') {
		res.writeHead(405).end();
		return;
	}
	if (req.url === '/api/events') {
		if (subscribers.size >= 4) {
			res.writeHead(503).end();
			return;
		}
		res.writeHead(200,
			{'Content-Type' : 'text/event-stream', 'Connection' : 'keep-alive', 'X-Accel-Buffering' : 'no'});
		res.flushHeaders();
		subscribers.add(res);
		res.on('close', () => subscribers.delete(res));
		res.on('error', () => subscribers.delete(res));
		sendState(res, 'data: ' + JSON.stringify(state()) + '\n\n');
		return;
	}
	if (req.url === '/api/state') {
		res.setHeader('Content-Type', 'application/json');
		res.end(JSON.stringify(state()));
		return;
	}
	if (req.url === '/') {
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(page);
		return;
	}
	const file = assets.get(req.url);
	if (!file) {
		res.writeHead(404).end();
		return;
	}
	res.setHeader('Content-Type', 'text/javascript');
	fs.createReadStream(file).on('error', error => {
		console.error('PC_ASSET_ERROR', JSON.stringify({url : req.url, code : error.code, file}));
		if (res.headersSent) {
			res.destroy();
			return;
		}
		res.writeHead(error.code === 'ENOENT' ? 404 : 500,
			{'Content-Type' : 'text/plain; charset=utf-8'});
		res.end('PC viewer asset unavailable: ' + req.url + '. Extract the complete PC package.');
	}).pipe(res);
});
server.maxConnections = 8;
server.requestTimeout = 5000;
server.listen(httpPort, '127.0.0.1',
	() => console.log('RESIDENT_PC_READY',
		JSON.stringify({url : `http://127.0.0.1:${httpPort}`, board, port, archive : !!output, mock})));
healthTimer = setInterval(broadcast, 250);

async function stop() {
	if (closed)
		return;
	closed = true;
	clearTimeout(timer);
	clearTimeout(runtimeTimer);
	clearTimeout(replayTimer);
	clearTimeout(telemetryTimer);
	clearTimeout(broadcastTimer);
	clearInterval(healthTimer);
	socket?.destroy();
	telemetrySocket?.destroy();
	for (const res of subscribers)
		res.destroy();
	subscribers.clear();
	server.close();
	server.closeAllConnections();
	await worker?.terminate();
	console.log(JSON.stringify(state()));
}

process.on('SIGINT', stop);
process.on('SIGTERM', stop);
if (replay) {
	if (fs.statSync(replay).size > 64 * 1024 * 1024)
		throw new Error('Replay exceeds bounded file size');
	const frames = fs.readFileSync(replay, 'utf8').trim().split('\n').filter(Boolean).map(decodePresentation);
	if (frames.some(f => !f.replay))
		throw new Error('Expected explicitly historical frames');
	let index = 0;
	connected = true;

	function play() {
		if (closed || index >= frames.length) {
			replayEnded = true;
			return;
		}
		accept(frames[index]);
		const current = frames[index++];
		if (index < frames.length) {
			const next = frames[index];
			const dt = next.session === current.session
				? Math.max(0, Number(BigInt(next.source_ns) - BigInt(current.source_ns)) / 1e6)
				: 0;
			replayTimer = setTimeout(play, dt);
		} else
			replayEnded = true;
	}

	restartReplay = () => {
		clearTimeout(replayTimer);
		last = null;
		lastAt = 0;
		received = 0;
		recent.length = 0;
		processing.reset();
		index = 0;
		replayEnded = false;
		replayTimer = setTimeout(play, 250);
	};
	restartReplay();
} else {
	connect();
	connectTelemetry();
}
if (seconds)
	runtimeTimer = setTimeout(stop, seconds * 1000);
