import test from 'node:test';
import assert from 'node:assert/strict';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {fileURLToPath} from 'node:url';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {PresentationReader, decodePresentation, visiblePresentation, VIEW_LIMIT} from '../presentation.mjs';
import {record} from './fixtures.mjs';
const frame = (n = 1) => ({
	schema : 'PIWVIEW1',
	version : 1,
	replay : false,
	session : '18446744073709500000',
	frame : String(n),
	sequence : String(n),
	source_ns : String(1000000000 + n * 67000000),
	hold_ms : 250,
	poses : [ {
		track : '7',
		candidate : 19,
		score : .8,
		held : false,
		observed_ns : String(1000000000 + n * 67000000),
		age_ms : 0,
		joints : Array(42).fill(.3)
	} ],
	raw_poses : []
});

test('PC binds the selected interface and promptly joins a board service started later', async () => {
	const target = await free(), hp = await free(), base = 'http://127.0.0.1:' + hp;
	const sockets = [];
	let child, output = '', errors = '', sentBack = 0;
	const source = net.createServer(socket => {
		sockets.push(socket);
		socket.on('data', b => sentBack += b.length);
		socket.write(JSON.stringify(frame()) + '\n');
	});
	try {
		child = spawn(process.execPath,
			[
				fileURLToPath(new URL('../resident.mjs', import.meta.url)), '--board', '127.0.0.1',
				'--local-address', '127.0.0.2', '--port', String(target), '--metrics-port', '0',
				'--http-port', String(hp), '--seconds', '5', '--mock', '1'
			],
			{windowsHide : true});
		const done = once(child, 'exit');
		child.stdout.on('data', b => output += b);
		child.stderr.on('data', b => errors += b);
		await until(() => output.includes('PC_BOARD_WAIT'));
		const get = async () => await (await fetch(base + '/api/state')).json();
		const waiting = await get();
		assert.equal(waiting.connected, false);
		assert.equal(waiting.connection.requested_local_address, '127.0.0.2');
		assert(waiting.connection.last_error);
		await new Promise(resolve => source.listen(target, '127.0.0.1', resolve));
		const started = performance.now();
		const live = await until(async () => {
			const s = await get();
			return s.received === 1 && s;
		});
		const delay = performance.now() - started;
		assert(delay < 850, `Ready board waited ${delay.toFixed(1)} ms for retry`);
		assert.equal(sockets[0].remoteAddress, '127.0.0.2');
		assert.equal(live.connection.local_address, '127.0.0.2');
		assert.equal(live.connection.last_error, null);
		assert(
			live.connection.connect_ms >= 0 && live.connection.first_result_ms >= live.connection.connect_ms);
		assert(output.includes('PC_FIRST_RESULT'));
		assert.equal(sentBack, 0);
		assert.equal((await done)[0], 0, errors);
		assert.equal(errors, '');
	} finally {
		child?.kill();
		sockets.forEach(socket => socket.destroy());
		if (source.listening)
			await new Promise(resolve => source.close(resolve));
	}
});

test('filtered SSE pairs timing by identity and remains independent when telemetry disconnects', async () => {
	const views = [], raws = [];
	let ack = 0, child, output = '', reader;
	const viewServer = net.createServer(s => {
		views.push(s);
		s.on('data', b => ack += b.length);
	});
	const rawServer = net.createServer(s => {
		raws.push(s);
		s.on('data', b => ack += b.length);
	});
	await Promise.all([
		new Promise(r => viewServer.listen(0, '127.0.0.1', r)),
		new Promise(r => rawServer.listen(0, '127.0.0.1', r))
	]);
	const hp = await free(), base = 'http://127.0.0.1:' + hp;
	try {
		child = spawn(process.execPath,
			[
				fileURLToPath(new URL('../resident.mjs', import.meta.url)), '--board', '127.0.0.1', '--port',
				String(viewServer.address().port), '--metrics-port', String(rawServer.address().port),
				'--http-port', String(hp), '--seconds', '4', '--mock', '1'
			],
			{windowsHide : true});
		const done = once(child, 'exit');
		child.stdout.on('data', b => output += b);
		await until(() => output.includes('RESIDENT_PC_READY') && views.length && raws.length);
		const response = await fetch(base + '/api/events');
		assert.match(response.headers.get('content-type'), /text\/event-stream/);
		reader = response.body.getReader();
		const events = [];
		let pending = '';
		const reading = (async () => {
			while (true) {
				const {done, value} = await reader.read();
				if (done)
					break;
				pending += Buffer.from(value).toString();
				let end;
				while ((end = pending.indexOf('\n\n')) >= 0) {
					const message = pending.slice(0, end);
					pending = pending.slice(end + 2);
					if (message.startsWith('data: '))
						events.push(JSON.parse(message.slice(6)));
				}
			}
		})().catch(() => {
				   });
		const f = frame();
		f.frame = '1000000';
		f.session = '42';
		f.source_ns = '123';
		f.poses[0].observed_ns = '123';
		const wrong = record({session : 43n});
		raws[0].write(wrong);
		views[0].write(JSON.stringify(f) + '\n');
		await until(() => events.some(e => e.frame?.sequence === '1'));
		assert.equal(events.at(-1).processing.samples, 0, 'Unrelated session timing matched');
		const matching = record();
		matching.writeDoubleLE(18.5, 80);
		raws[0].write(matching.subarray(0, 33));
		raws[0].write(matching.subarray(33));
		await until(() => events.some(e => e.processing.samples === 1));
		assert.equal(events.at(-1).processing.median_ms, 18.5);
		raws[0].destroy();
		await wait(50);
		f.sequence = '2';
		f.frame = '1000001';
		views[0].write(JSON.stringify(f) + '\n');
		const get = async () => await (await fetch(base + '/api/state')).json();
		const state = await until(async () => {
			const s = await get();
			return s.frame?.sequence === '2' && s;
		});
		assert.equal(state.connected, true);
		assert.equal(state.processing.connected, false);
		assert.equal(state.processing.samples, 0);
		assert.equal(ack, 0);
		await reader.cancel();
		await reading;
		assert.equal((await done)[0], 0);
	} finally {
		await reader?.cancel().catch(() => {
									 });
		child?.kill();
		[...views, ...raws].forEach(s => s.destroy());
		await Promise.all([ new Promise(r => viewServer.close(r)), new Promise(r => rawServer.close(r)) ]);
	}
});
test('explicit Top1 without confidence cutoff retains low, zero and negative finite scores', () => {
	for (const score of [.001, 0, -.5]) {
		const f = {...frame(), top_k : 1, score_threshold : null};
		f.poses[0].score = score;
		assert.equal(decodePresentation(JSON.stringify(f)).poses[0].score, score);
	}
	const strict = {...frame(), top_k : 1, score_threshold : 0};
	strict.poses[0].score = 0;
	assert.throws(() => decodePresentation(JSON.stringify(strict)));
	for (const update of [{top_k : 0}, {top_k : 4}, {score_threshold : 'none'}, {score_threshold : 1.1}])
		assert.throws(() => decodePresentation(JSON.stringify({...frame(), ...update})));
	const tooMany = {...frame(), top_k : 1, score_threshold : null};
	tooMany.raw_poses = [ frame().poses[0], frame().poses[0] ];
	assert.throws(() => decodePresentation(JSON.stringify(tooMany)));
});
const wait = ms => new Promise(r => setTimeout(r, ms));

async function until(fn) {
	for (let i = 0; i < 150; i++) {
		const v = await fn();
		if (v)
			return v;
		await wait(20);
	}
	throw new Error('wait expired');
}

async function free() {
	const s = net.createServer();
	await new Promise(r => s.listen(0, '127.0.0.1', r));
	const p = s.address().port;
	await new Promise(r => s.close(r));
	return p;
}

test('bounded NDJSON splits/coalescing, finite checks, immutable age and expiry', () => {
	const r = new PresentationReader(),
		  b = Buffer.from(JSON.stringify(frame()) + '\n' + JSON.stringify(frame(2)) + '\n'), out = [];
	for (let n = 0; n < b.length; n += 17)
		r.push(b.subarray(n, n + 17), f => out.push(f));
	assert.equal(out.length, 2);
	const f = frame();
	assert.equal(visiblePresentation(f, 250).poses.length, 1);
	assert.equal(visiblePresentation(f, 251).poses.length, 0);
	assert.equal(f.poses.length, 1);
	assert.throws(() => new PresentationReader().push(Buffer.alloc(VIEW_LIMIT + 1, 65),
					  () => {
					  }));
	for (const mutate of [f => f.version = 2, f => f.poses[0].age_ms = 12, f => f.poses[0].track = '0',
						 f => f.poses[0].joints[0] = null, f => f.poses.push(f.poses[0]),
						 f => f.poses[0].score = Math.fround(.2)]) {
		const x = frame();
		mutate(x);
		assert.throws(() => decodePresentation(JSON.stringify(x)));
	}
});
test('derived TCP has no ACK, expires, rejects malformed records and reconnects', async () => {
	const sockets = [];
	let ack = 0, child, output = '';
	const source = net.createServer(s => {
		sockets.push(s);
		s.on('data', b => ack += b.length);
	});
	await new Promise(r => source.listen(0, '127.0.0.1', r));
	const hp = await free();
	try {
		child = spawn(process.execPath,
			[
				fileURLToPath(new URL('../resident.mjs', import.meta.url)), '--board', '127.0.0.1', '--port',
				String(source.address().port), '--http-port', String(hp), '--seconds', '5'
			],
			{windowsHide : true});
		const done = once(child, 'exit');
		child.stdout.on('data', b => output += b);
		await until(() => output.includes('RESIDENT_PC_READY') && sockets.length);
		const get = async () => await (await fetch('http://127.0.0.1:' + hp + '/api/state')).json();
		const bytes = Buffer.from(JSON.stringify(frame()) + '\n');
		sockets[0].write(bytes.subarray(0, 25));
		await wait(25);
		assert.equal((await get()).received, 0);
		sockets[0].write(bytes.subarray(25));
		await until(async () => (await get()).received === 1);
		await wait(280);
		assert.equal((await get()).frame.poses.length, 0);
		sockets[0].write('{}\n');
		await until(() => sockets.length === 2);
		sockets[1].write(JSON.stringify(frame(2)) + '\n');
		const state = await until(async () => {
			const x = await get();
			return x.received === 2 && x;
		});
		assert.equal(state.invalid, 1);
		assert.equal(ack, 0);
		const page = await (await fetch('http://127.0.0.1:' + hp)).text();
		assert.match(page, /id="viewport"/);
		const [code] = await done;
		assert.equal(code, 0);
	} finally {
		child?.kill();
		sockets.forEach(s => s.destroy());
		await new Promise(r => source.close(r));
	}
});
test('historical replay uses local timestamps and makes no board connection', async () => {
	const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pose-replay-')),
		  file = path.join(dir, 'frames.ndjson');
	let count = 0, child, output = '';
	const source = net.createServer(s => {
		++count;
		s.destroy();
	});
	await new Promise(r => source.listen(0, '127.0.0.1', r));
	try {
		fs.writeFileSync(file, [ 1, 2 ].map(n => JSON.stringify({...frame(n), replay : true})).join('\n'));
		const hp = await free();
		child = spawn(process.execPath,
			[
				fileURLToPath(new URL('../resident.mjs', import.meta.url)), '--replay', file, '--board',
				'127.0.0.1', '--port', String(source.address().port), '--http-port', String(hp), '--seconds',
				'2'
			],
			{windowsHide : true});
		const done = once(child, 'exit');
		child.stdout.on('data', b => output += b);
		await until(() => output.includes('RESIDENT_PC_READY'));
		const x = await until(async () => {
			const s = await (await fetch('http://127.0.0.1:' + hp + '/api/state')).json();
			return s.received === 2 && s;
		});
		assert.equal(x.replay, true);
		assert.equal(x.frame.replay, true);
		assert.equal(count, 0);
		assert.equal((await done)[0], 0);
	} finally {
		child?.kill();
		await new Promise(r => source.close(r));
		fs.rmSync(dir, {recursive : true});
	}
});
