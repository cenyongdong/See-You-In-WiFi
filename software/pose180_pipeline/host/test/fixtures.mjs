// Deliberately synthetic PIWFUL3 fixture; it is never an NPU reference output.
import {FULL_BYTES, SCORE_OFFSET, POSE_OFFSET} from '../full_record.mjs';

export function record({
	index = 0,
	session = 42n,
	source = 123n,
	best = 179,
	fullPattern = false,
	target = Buffer.alloc(FULL_BYTES)
} = {}) {
	const b = target;
	b.fill(0);
	b.write('PIWFUL3\0');
	b.writeUInt32LE(3, 8);
	b.writeUInt32LE(FULL_BYTES, 12);
	for (const [offset, value] of [[ 16, session ], [ 24, BigInt(1000000 + index) ], [ 32, BigInt(index) ],
			 [ 40, source ], [ 48, 1n ], [ 56, 2n ], [ 64, 3n ], [ 72, BigInt(index + 1) ]])
		b.writeBigUInt64LE(value, offset);
	for (const off of [80, 88, 96, 104])
		b.writeDoubleLE(1, off);
	b.writeUInt32LE(180, 116);
	b.writeUInt32LE(best, 120);
	const selected = b.subarray(128, 384);
	selected.write('PIWPOSE1');
	selected.writeUInt16LE(1, 8);
	selected.writeUInt16LE(88, 10);
	selected.writeUInt32LE(256, 12);
	for (const [offset, value] of [[ 16, session ], [ 24, BigInt(1000000 + index) ], [ 32, BigInt(index) ],
			 [ 40, source ], [ 48, 3n ], [ 80, BigInt(index + 1) ]])
		selected.writeBigUInt64LE(value, offset);
	selected.writeUInt32LE(best, 56);
	selected.writeUInt16LE(14, 60);
	selected.writeUInt32LE(1, 68);
	selected.writeUInt32LE(1, 72);
	if (fullPattern) {
		for (let i = 0; i < 10800; ++i)
			b.writeFloatLE(((index * 31 + i) % 1000) / 16, 384 + i * 4);
		for (let candidate = 0; candidate < 180; ++candidate) {
			b.writeFloatLE(-candidate / 1024, SCORE_OFFSET + candidate * 4);
			for (let i = 0; i < 42; ++i)
				b.writeFloatLE(
					index / 1024 + candidate / 256 + i / 128, POSE_OFFSET + (candidate * 42 + i) * 4);
		}
	}
	b.writeFloatLE(.9, SCORE_OFFSET + best * 4);
	selected.writeFloatLE(.9, 64);
	for (let i = 0; i < 42; ++i) {
		if (!fullPattern)
			b.writeFloatLE(i + .125, POSE_OFFSET + (best * 42 + i) * 4);
		selected.writeFloatLE(b.readFloatLE(POSE_OFFSET + (best * 42 + i) * 4), 88 + i * 4);
	}
	return b;
}

export function confirmed(sequence, target = Buffer.alloc(8)) {
	target.writeBigUInt64LE(BigInt(sequence));
	return target;
}
