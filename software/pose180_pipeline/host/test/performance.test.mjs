import test from 'node:test';
import assert from 'node:assert/strict';
import {FullRecordReader, ProcessingWindow, FULL_BYTES} from '../full_record.mjs';
import {record} from './fixtures.mjs';

const frame = (sequence, process = 10, session = '1', overrides = {}) => ({
	session,
	sequence : String(sequence),
	frame : String(1000 + sequence),
	source_ns : String(sequence * 1000000),
	metrics : {process_ms : process},
	...overrides
});

test('telemetry reader bounds partial bytes, splits/coalesces and owns decoded values', () => {
	const reader = new FullRecordReader(), wire = Buffer.concat([ record(), record({index : 1}) ]), seen = [];
	let offset = 0, step = 1;
	while (offset < wire.length) {
		const length = Math.min(7919 * step % 65537 + 1, wire.length - offset);
		reader.push(wire.subarray(offset, offset + length), f => seen.push(f));
		offset += length;
		++step;
		assert(reader.used < FULL_BYTES);
	}
	assert.deepEqual(seen.map(f => f.sequence), [ '1', '2' ]);
	assert.equal(reader.raw.length, FULL_BYTES);
	assert.equal(seen[0].frame, '1000000');
	assert.equal(seen[0].joints[0], .125);
	reader.push(record().subarray(0, 51), () => assert.fail('Partial frame emitted'));
	reader.reset();
	reader.push(record({index : 2}), f => seen.push(f));
	assert.equal(seen.at(-1).sequence, '3');
	assert.equal(reader.used, 0);
});

test('telemetry reader rejects original invalid records without callback', () => {
	const reader = new FullRecordReader(), bad = record();
	bad.writeDoubleLE(NaN, 80);
	assert.throws(() => reader.push(bad, () => assert.fail('Invalid timing emitted')), /processing time/);
	reader.reset();
	const seen = [];
	reader.push(record(), f => seen.push(f));
	assert.equal(seen.length, 1);
});

test('processing window joins either arrival order and reports median/nearest-rank P95', () => {
	const window = new ProcessingWindow();
	window.observeResult(frame(1, 10), 0);
	assert.equal(window.snapshot(0).samples, 0);
	window.observeView(frame(1), 1);
	window.observeView(frame(2), 2);
	window.observeResult(frame(2, 20), 3);
	window.observeResult(frame(3, 30), 4);
	window.observeView(frame(3), 5);
	window.observeView(frame(4), 6);
	window.observeResult(frame(4, 100), 7);
	assert.deepEqual(window.snapshot(7), {session : '1', samples : 4, median_ms : 25, p95_ms : 100});
});

test('wrong full identity, duplicate result/view and late expired samples do not contaminate', () => {
	const window = new ProcessingWindow();
	window.observeResult(frame(1, 10), 0);
	window.observeView(frame(1, 10, '1', {source_ns : '99'}), 1);
	assert.equal(window.snapshot(2).samples, 0);
	window.observeResult(frame(2, 20), 10);
	window.observeView(frame(2), 11);
	assert.equal(window.observeResult(frame(2, 9999), 4990), false);
	assert.equal(window.observeView(frame(2), 4991), false);
	assert.equal(window.snapshot(5011).samples, 0);
	assert.equal(window.observeResult(frame(2, 9999), 5012), false);
	assert.equal(window.observeView(frame(2), 5013), false);
	window.observeView(frame(3), 5020);
	assert.equal(window.observeResult(frame(3, 50), 10021), false);
	assert.equal(window.snapshot(10021).samples, 0);
});

test('view session is authoritative, retains early new-session telemetry and retires old views', () => {
	const window = new ProcessingWindow();
	window.observeResult(frame(1, 10), 0);
	window.observeView(frame(1), 1);
	window.observeResult(frame(1, 200, '2'), 2);
	assert.deepEqual(window.snapshot(2), {session : '1', samples : 1, median_ms : 10, p95_ms : 10});
	window.observeView(frame(1, 10, '2'), 3);
	assert.deepEqual(window.snapshot(3), {session : '2', samples : 1, median_ms : 200, p95_ms : 200});
	assert.equal(window.observeView(frame(2, 10, '1'), 4), false);
	assert.equal(window.observeResult(frame(2, 999, '1'), 5), false);
	assert.equal(window.snapshot(5).median_ms, 200);
	window.reset();
	assert.deepEqual(window.snapshot(6), {session : null, samples : 0, median_ms : null, p95_ms : null});
	window.observeView(frame(1), 7);
	window.observeResult(frame(1, 30), 8);
	assert.equal(window.snapshot(8).median_ms, 30);
});

test('all record and session bookkeeping stays bounded and evicted duplicate views stay old', () => {
	const window = new ProcessingWindow();
	for (let i = 1; i <= 400; ++i) {
		window.observeResult(frame(i, i), i);
		window.observeView(frame(i), i);
	}
	assert.equal(window.records.size, 256);
	assert.equal(window.snapshot(400).samples, 256);
	assert.equal(window.observeView(frame(1), 401), false);
	assert.equal(window.observeResult(frame(1, 999), 402), false);
	for (let i = 2; i <= 500; ++i) {
		window.observeResult(frame(1, 5, String(i)), 500 + i);
		window.observeView(frame(1, 5, String(i)), 500 + i);
	}
	assert(window.records.size <= 256);
	assert(window.resultSequences.size <= 256);
	assert(window.retiredSessions.size <= 256);
	assert.equal(window.snapshot(1000).session, '500');
	assert.equal(window.snapshot(1000).samples, 1);
	assert.throws(() => new ProcessingWindow({maxRecords : 257}), /bounded/);
	assert.throws(() => new ProcessingWindow({windowMs : 5001}), /bounded/);
});
