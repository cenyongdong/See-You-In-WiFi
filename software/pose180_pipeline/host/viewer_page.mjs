// 纯页面模板：不创建连接或定时器，raw/view 只控制原有展示语义。
export function renderPage(mode) {
	return `<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${mode === 'raw' ? '滤波前 · 原始候选' : '滤波后 · 展示结果'}</title>
<style>
* {
	box-sizing:border-box
}
body {
	margin:0;
	background:#0b111b;
	color:#e5eef9;
	font:16px system-ui;
	overflow:hidden;
	display:flex;
	flex-direction:column;
	height:100dvh
}
header {
	padding:18px 24px 10px;
	flex:none
}
h1 {
	font-size:20px;
	margin:0
}
.heading {
	display:flex;
	align-items:center;
	justify-content:space-between;
	gap:16px
}
#viewport {
	flex:1;
	min-height:0
}
#frame {
	color:#91a8bd;
	font:13px ui-monospace,monospace
}
.metrics {
	display:grid;
	grid-template-columns:1fr 1fr 1.35fr;
	gap:12px;
	margin:16px 0 12px
}
.metric {
	background:#101e2d;
	border:1px solid #263c50;
	border-radius:10px;
	padding:12px 16px;
	min-width:0
}
.label {
	color:#92acc3;
	font-size:12px;
	letter-spacing:.06em
}
.value {
	font-size:27px;
	line-height:1.45;
	font-weight:600;
	font-variant-numeric:tabular-nums
}
.unit {
	font-size:13px;
	color:#a0b6c9;
	font-weight:400
}
#phase {
	font-size:18px;
	color:#9ee8ce
}
#phase[data-state]:not([data-state=live]) {
	color:#ffce84
}
button {
	background:#172838;
	color:#d8e9f6;
	border:1px solid #385364;
	border-radius:5px;
	padding:6px 12px;
	cursor:pointer
}
button[aria-pressed=true] {
	background:#294558;
	border-color:#82b9bf
}
nav {
	display:flex;
	gap:8px
}
@media(max-width:620px) {
	header {
		padding:12px
	}
	.metrics {
		gap:6px;
		margin:10px 0
	}
	.metric {
		padding:9px
	}
	.value {
		font-size:22px
	}
	#phase {
		font-size:14px
	}
	h1 {
		font-size:17px
	}
}
</style>
<script type="importmap">{"imports":{"three":"/vendor/three.module.js","three/addons/controls/OrbitControls.js":"/vendor/OrbitControls.js"}}</script>
<header>
<div class="heading">
<h1>Wi-Fi 姿态 · ${mode === 'raw' ? '滤波前' : '滤波后'}</h1>
<span id="frame">FRAME —</span>
</div>
<section class="metrics" aria-label="实时性能">
<div class="metric">
<div class="label">板端处理耗时</div>
<div class="value">
<span id="process">—</span> <span class="unit">ms</span>
</div>
</div>
<div class="metric">
<div class="label">骨架更新率</div>
<div class="value">
<span id="pose-rate">0.0</span> <span class="unit">次/秒</span>
</div>
</div>
<div class="metric">
<div class="label">运行状态</div>
<div class="value" id="phase" data-state="waiting_input">等待首个真实结果</div>
</div>
</section>
<nav aria-label="视角">
<button data-view="perspective" aria-pressed="true">透视</button>
<button data-view="front" aria-pressed="false">正面</button>
<button data-view="side" aria-pressed="false">侧面</button>
<button data-view="top" aria-pressed="false">俯视</button>
</nav>
</header>
<div id="viewport">
</div>
<script type="module">import {createScene} from './scene.js';
const bones = [
	[ 0, 1 ], [ 0, 2 ], [ 0, 3 ], [ 2, 4 ], [ 2, 5 ], [ 3, 6 ], [ 3, 7 ], [ 4, 8 ], [ 5, 7 ], [ 5, 9 ],
	[ 6, 10 ], [ 7, 11 ], [ 9, 12 ], [ 11, 13 ]
];
const el = id => document.getElementById(id);
let scene;
const filtered = ${mode === 'view'};
try {
	scene = createScene(el('viewport'), bones,
		() => {
		},
		{maxPoses : 3});
} catch (error) {
	el('phase').textContent = '三维渲染不可用';
	el('phase').dataset.state = 'error';
	console.error(error);
}
if (scene) {
	const buttons = document.querySelectorAll('[data-view]');
	buttons.forEach(button => button.addEventListener('click', () => {
		scene.view(button.dataset.view);
		buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
	}));
	const phases = {
		live : '运行中',
		waiting_input : '等待首个真实结果',
		waiting_result : '等待新结果',
		result_stale : '结果已过期',
		reconnecting : '连接中断 · 自动重连'
	};
	const text = (id, value) => {
		const target = el(id);
		if (target.textContent !== value)
			target.textContent = value;
	};
	let latest = null, receivedAt = 0, streamLive = false, identity = '', counted = '', session = '',
		lastMetrics = -Infinity, animation, disposed = false;
	const updates = [];
	const stream = new EventSource('/api/events');
	stream.onmessage = event => {
		try {
			latest = JSON.parse(event.data);
			receivedAt = performance.now();
			streamLive = true;
		} catch {
			streamLive = false;
		}
	};
	stream.onerror = () => {
		streamLive = false;
	};

	function draw(now) {
		if (disposed)
			return;
		const s = latest, f = s?.frame, age = f ? Math.max(0, (s.age_ms ?? 0) + now - receivedAt) : null;
		const connected = streamLive && s?.connected;
		const phase = !connected ? 'reconnecting'
			: !f				 ? 'waiting_input'
			: age >= 2000		 ? 'result_stale'
			: age >= 750		 ? 'waiting_result'
								 : 'live';
		el('phase').dataset.state = phase;
		text('phase',
			(!streamLive ? '观察端连接中断'
						 : (s.replay				  ? '历史回放 · '
								   : s.mock			  ? '模拟测试 · '
								   : s.mode === 'raw' ? '原始候选 · '
													  : '') +
						(s.replayEnded ? '播放结束' : phases[phase])));
		let visible = f;
		if (filtered && f)
			visible = {...f, poses : connected ? f.poses.filter(p => p.age_ms + age <= f.hold_ms) : []};
		if (visible) {
			if (session !== f.session) {
				session = f.session;
				updates.length = 0;
				counted = '';
			}
			const resultId = f.session + ':' + f.sequence;
			const key = resultId + ':' + visible.poses.map(p => p.track ?? p.candidate).join(',');
			if (key !== identity) {
				scene.setPose(visible);
				identity = key;
				if (resultId !== counted && connected && age < 750 && visible.poses.some(p => !p.held)) {
					updates.push(now);
					if (updates.length > 512)
						updates.shift();
					counted = resultId;
				}
			}
		} else if (filtered && identity) {
			scene.setPose({poses : []});
			identity = '';
		}
		while (updates.length && now - updates[0] >= 5000)
			updates.shift();
		if (now - lastMetrics >= 1000) {
			lastMetrics = now;
			const rate = connected && updates.length > 1
				? (updates.length - 1) * 1000 / Math.max(1, now - updates[0])
				: 0;
			el('pose-rate').textContent = rate.toFixed(1);
			const m = s?.processing,
				  hasTiming =
					  connected && !s.replay && m?.connected && m.samples > 0 && now - receivedAt < 1500;
			el('process').textContent = hasTiming ? m.median_ms.toFixed(2) : '—';
		}
		text('frame', 'FRAME ' + (f?.frame ?? '—'));
		animation = requestAnimationFrame(draw);
	}

	animation = requestAnimationFrame(draw);
	window.addEventListener('pagehide', () => {
		disposed = true;
		stream.close();
		cancelAnimationFrame(animation);
		scene.dispose();
	}, {once : true});
}</script></html>`;
}
