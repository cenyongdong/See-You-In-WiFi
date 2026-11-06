import {renderPage} from './viewer_page.mjs';
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
const connection = {
	board,
	port,
	requested_local_address : localAddress || null,
	attempts : 0,
	local_address : null,
	connect_ms : null,
	first_result_ms : null,
	last_error : null
};
let connectionStarted = 0, reportedError = '', lastErrorLog = -Infinity;

function boardSocket(targetPort) {
	const client =
		net.createConnection({host : board, port : targetPort, ...(localAddress ? {localAddress} : {})});
	// Bound the TCP handshake separately from a healthy connection's idle time.
	// An absent temporary address must not leave an OS-level SYN pending for ages.
	const deadline = setTimeout(() => client.destroy(Object.assign(
									new Error('Board TCP connection timed out'), {code : 'ETIMEDOUT'})),
		1500);
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
		const response = await fetch(metricsStateUrl, {signal : AbortSignal.timeout(750)});
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
const page = renderPage(mode);
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
	fs.createReadStream(file)
		.on('error',
			error => {
				console.error('PC_ASSET_ERROR', JSON.stringify({url : req.url, code : error.code, file}));
				if (res.headersSent) {
					res.destroy();
					return;
				}
				res.writeHead(
					error.code === 'ENOENT' ? 404 : 500, {'Content-Type' : 'text/plain; charset=utf-8'});
				res.end('PC viewer asset unavailable: ' + req.url + '. Extract the complete PC package.');
			})
		.pipe(res);
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
