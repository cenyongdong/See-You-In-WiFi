import test from 'node:test';
import assert from 'node:assert/strict';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import {record} from './fixtures.mjs';
import {selectTopPoses, SCORE_OFFSET, POSE_OFFSET} from '../full_record.mjs';

test('PC top3 selection uses strict float32 threshold and preserves raw records', () => {
	const raw = record();
	for (let i = 0; i < 180; ++i)
		raw.writeFloatLE(0.1, SCORE_OFFSET + 4 * i);
	raw.writeFloatLE(0.8, SCORE_OFFSET + 4 * 179);
	raw.writeFloatLE(0.7, SCORE_OFFSET + 4 * 2);
	raw.writeFloatLE(0.6, SCORE_OFFSET + 4 * 3);
	raw.writeFloatLE(0.5, SCORE_OFFSET + 4 * 4);
	const original = Buffer.from(raw), three = selectTopPoses(raw);
	assert.deepEqual(three.map(p => p.candidate), [ 179, 2, 3 ]);
	assert.deepEqual(raw, original);
	three.forEach(p => p.joints.forEach(
					  (v, i) => assert.equal(v, raw.readFloatLE(POSE_OFFSET + (p.candidate * 42 + i) * 4))));
	for (let i = 0; i < 180; ++i)
		raw.writeFloatLE(0.2, SCORE_OFFSET + 4 * i);
	assert.deepEqual(selectTopPoses(raw), []);
	raw.writeUInt32LE(0x3e4cccce, SCORE_OFFSET + 4 * 7); // next float above 0.2f
	assert.deepEqual(selectTopPoses(raw).map(p => p.candidate), [ 7 ]);
	raw.writeFloatLE(0.5, SCORE_OFFSET + 4 * 1);
	raw.writeFloatLE(0.5, SCORE_OFFSET + 4 * 2);
	raw.writeFloatLE(0.5, SCORE_OFFSET + 4 * 3);
	raw.writeFloatLE(0.5, SCORE_OFFSET + 4 * 4);
	assert.deepEqual(selectTopPoses(raw).map(p => p.candidate), [ 1, 2, 3 ]);
});

const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

async function until(check, label, ms = 4000) {
	const end = Date.now() + ms;
	while (Date.now() < end) {
		const result = await check();
		if (result)
			return result;
		await wait(20);
	}
	throw new Error(label);
}

async function freePort() {
	const s = net.createServer();
	await new Promise(resolve => s.listen(0, '127.0.0.1', resolve));
	const port = s.address().port;
	await new Promise(resolve => s.close(resolve));
	return port;
}

test(
	'optional PC consumes split results without ACK, marks stale, reconnects and serves the existing 3D modules',
	async () => {
		const sockets = [];
		let sentBack = 0, child, output = '', errors = '';
		const source = net.createServer(socket => {
			sockets.push(socket);
			socket.on('data', b => {
				sentBack += b.length;
			});
		});
		await new Promise(resolve => source.listen(0, '127.0.0.1', resolve));
		const httpPort = await freePort(), base = 'http://127.0.0.1:' + httpPort;
		try {
			child = spawn(process.execPath,
				[
					fileURLToPath(new URL('../resident.mjs', import.meta.url)),
					// Includes a deliberate 5.2 s stale interval, reconnect, and asset
					// reads on Windows; leave room for filesystem/scheduler latency.
					'--mode', 'raw', '--board', '127.0.0.1', '--port', String(source.address().port),
					'--http-port', String(httpPort), '--seconds', '20', '--mock', '1'
				],
				{windowsHide : true, stdio : [ 'ignore', 'pipe', 'pipe' ]});
			const finished = once(child, 'exit');
			child.stdout.on('data', b => {
				output += b;
			});
			child.stderr.on('data', b => {
				errors += b;
			});
			await until(() => output.includes('RESIDENT_PC_READY'), 'PC server did not become ready');
			const get = async () => await (await fetch(base + '/api/state')).json();
			let state = await until(async () => {
				const s = await get();
				return s.connected && s;
			}, 'No result connection');
			assert.equal(state.phase, 'waiting_input');
			assert.equal(state.frame, null);
			assert.equal(state.mock, true);
			const html = await (await fetch(base)).text();
			assert.match(html, /原始候选 · /);
			for (const asset of ['/scene.js', '/vendor/three.module.js', '/vendor/three.core.js',
					 '/vendor/OrbitControls.js']) {
				const response = await fetch(base + asset);
				assert.equal(response.status, 200, asset);
				assert((await response.text()).length > 1000, asset);
			}
			const frame = record();
			sockets[0].write(frame.subarray(0, 23));
			await wait(30);
			assert.equal((await get()).received, 0, 'Partial record became a pose');
			sockets[0].write(frame.subarray(23));
			state = await until(async () => {
				const s = await get();
				return s.received === 1 && s;
			}, 'No complete pose');
			assert.equal(state.phase, 'live');
			assert.equal(state.frame.candidate, 179);
			assert.equal(state.frame.joints.length, 42);
			sockets[0].write(frame);
			state = await until(async () => {
				const s = await get();
				return s.duplicates === 1 && s;
			}, 'Duplicate was not recognized');
			assert.equal(state.received, 1);
			assert.equal(state.frame.sequence, '1');
			await wait(5200);
			state = await get();
			assert.equal(state.phase, 'result_stale');
			assert.equal(state.connected, true);
			assert.equal(state.reconnects, 1, 'Ordinary missing input reset a healthy result connection');
			assert.equal(state.new_results_hz, 0);
			assert.equal(state.received, 1);
			assert.equal(state.frame.sequence, '1');
			sockets[0].destroy();
			await until(() => sockets.length === 2, 'PC did not reconnect');
			sockets[1].write(record({index : 1}));
			state = await until(async () => {
				const s = await get();
				return s.received === 2 && s;
			}, 'No result after reconnect');
			assert.equal(state.phase, 'live');
			assert.equal(state.frame.sequence, '2');
			assert.equal(state.reconnects, 2);
			assert.equal(sentBack, 0, 'PC observer wrote ACK/control/input bytes to board');
			await verifyPage(html, state);
			const [code] = await finished;
			assert.equal(code, 0, errors);
			assert.equal(sentBack, 0);
			assert.equal(errors, '');
			// Timer exit must close the actual listener, including fetch keepalive.
			const probe = net.createServer();
			await new Promise((resolve, reject) => {
				probe.once('error', reject);
				probe.listen(httpPort, '127.0.0.1', resolve);
			});
			await new Promise(resolve => probe.close(resolve));
		} finally {
			child?.kill();
			for (const socket of sockets)
				socket.destroy();
			await new Promise(resolve => source.close(resolve));
		}
	});

async function verifyPage(html, live) {
	const script = html.match(/<script type="module">([\s\S]*?)<\/script>/)[1].replace(
		/import\s*\{\s*createScene\s*\}\s*from\s*['"]\.\/scene\.js['"];?/, '');
	const elements = new Map();
	const element = id => {
		if (!elements.has(id))
			elements.set(id, {
				textContent : '',
				dataset : {},
				events : {},
				addEventListener(kind, callback) {
					this.events[kind] = callback;
				}
			});
		return elements.get(id);
	};
	const buttons = [ 'perspective', 'front', 'side', 'top' ].map(
		view => ({...element(view), dataset : {view}, setAttribute() {}}));
	const poses = [], views = [], animations = [];
	let stream, now = 0, fpsCallback, dispose, closed = false, sceneDisposed = false;
	const context = {
		createScene : (container, bones, fps) => {
			assert.equal(bones.length, 14);
			fpsCallback = fps;
			return {
				setPose : f => poses.push(f),
				view : v => views.push(v),
				dispose() {
					sceneDisposed = true;
				}
			};
		},
		document : {getElementById : element, querySelectorAll : () => buttons},
		window : {
			addEventListener(kind, fn) {
				if (kind === 'pagehide')
					dispose = fn;
			}
		},
		performance : {now : () => now},
		EventSource : class {
			constructor(url) {
				assert.equal(url, '/api/events');
				stream = this;
			} close() {
				closed = true;
			}
		},
		requestAnimationFrame : fn => animations.push(fn),
		cancelAnimationFrame : () => {
		},
		console
	};
	vm.runInNewContext(script, context);
	const tick = (time) => {
		now = time;
		animations.shift()(now);
	};
	const deliver = value => stream.onmessage({data : JSON.stringify(value)});
	deliver({...live, age_ms : 0});
	tick(0);
	assert.equal(poses.length, 1);
	assert.equal(element('phase').dataset.state, 'live');
	assert.equal(element('process').textContent, '1.00');
	deliver({...live, age_ms : 2500, new_results_hz : 0});
	tick(1000);
	assert.equal(poses.length, 1, 'An old result manufactured another pose update');
	assert.match(element('phase').textContent, /过期/);
	stream.onerror();
	tick(1100);
	assert.equal(poses.length, 1);
	assert.match(element('phase').textContent, /中断/);
	// More than ten distinct poses per second reach the page; repeated draw calls
	// and coalesced network messages must not inflate the displayed update rate.
	for (let i = 0; i < 31; i++) {
		now = 1200 + i * 33;
		deliver({...live, age_ms : 0, frame : {...live.frame, session : '43', sequence : String(i + 3)}});
		tick(now);
	}
	tick(2300);
	assert.equal(poses.length, 32);
	assert(Number(element('pose-rate').textContent) > 20);
	const before = poses.length;
	fpsCallback(60);
	tick(2316);
	tick(2332);
	assert.equal(poses.length, before, 'Browser refresh was counted as inference');
	now = 2340;
	deliver({...live, age_ms : 0, frame : {...live.frame, session : '43', sequence : '100'}});
	deliver({...live, age_ms : 0, frame : {...live.frame, session : '43', sequence : '101'}});
	tick(2341);
	assert.equal(
		poses.length, before + 1, 'Queued stream updates were replayed instead of adopting the latest');
	assert.equal(poses.at(-1).sequence, '101');
	deliver({
		...live,
		age_ms : 0,
		processing : {connected : false, samples : 0, median_ms : null, p95_ms : null}
	});
	tick(3500);
	assert.equal(element('process').textContent, '—');
	for (const button of buttons)
		button.events.click();
	assert.deepEqual(views, [ 'perspective', 'front', 'side', 'top' ]);
	dispose();
	assert(closed && sceneDisposed, 'Page exit leaked the event connection or scene');
}
