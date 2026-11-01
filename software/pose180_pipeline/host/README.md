# 180-query PC 观察与主机验证

2026-10-31当前发布默认保留滤波前／滤波后对照：包根`start-pc.ps1`同时启动raw（http://127.0.0.1:39381/）与view（http://127.0.0.1:39380/），后者共享前者计时，Ctrl+C结束本批两个只读PC进程。raw仅按TopK=3／score>0.2选取原始候选，没有人物关联与One Euro；view是板端后处理结果，与HDMI共用。两页分别标明滤波前／后，可并排比较。

当前常驻入口为 `resident.mjs`，渲染资源集中在本目录 `web/scene.js`，PC 检查在 `test/`。网页行为保持，旧严格链 `run.mjs` 及其历史依赖保留。

部署包根目录的 `start-pc.ps1` 来自本目录同名模板，自动查找 PATH、常用安装位置及本机已有 Codex Node.js；也可用 `-NodePath <node.exe完整路径>` 指定。`-Check` 只核对 Node.js 版本，不连接开发板。普通 PowerShell 不一定继承 Codex 的运行时 PATH，启动器因此不再依赖裸 `node` 命令。

PC 已配置演示有线地址 `192.168.126.100/24` 时，可执行 `./start-pc.ps1 -Board 192.168.126.49 -LocalAddress 192.168.126.100`，通过固定板端地址并指定源网卡。其它电脑须使用自己的有线 IP；`-LocalAddress` 不修改系统网络设置。默认 `192.168.50.49` 是板端演示期间的临时别名，正常结束时可能移除。TCP 建连单独限时 1.5 秒，骨架通道断开后 250 ms 重试，已连接的无数据等待仍保留 30 秒。终端 `PC_BOARD_WAIT` 显示失败原因，`PC_FIRST_RESULT` 记录实际源地址及本次连接收到首帧的耗时；`/api/state` 的 `connection` 字段提供相同诊断。PC 启动后先打开页面，再开始板端演示；PC 不启动或重试板端 SDK。

10月29日PC修订曾进入r3-final；当前已随r4 RAR交付，双页共享计时见本页10月31日补充。当时22项本地检查覆盖建连、断线、显式源地址、拆包、SSE、过期与正常退出；最近实板发送记录见[最终进度](../../../PROJECT-PROGRESS.md)。下述 10 月 28 日性能栏验证和旧严格链保留各自范围。

## 常驻演示观察端

2026-10-28：PC 页面新增简洁性能栏，只显示板端处理耗时（ms）、骨架更新率（次/秒）和运行状态；不显示 MPJPE。骨架坐标、视角和 HDMI 保持原有实现。本轮只修改 `host/`，未改另一会话的板端滤波、异常退出清理或启动包构建文件，也未部署到板端。

观察端默认订阅39385派生骨架，复用板端人物ID、滤波坐标与250ms暂失有效期；支持TopK=1和`score_threshold: null`。拖动旋转、滚轮缩放、右键平移，并可切换透视／正面／侧面／俯视。PC不发送输入、ACK或板端控制命令。

页面使用 `/api/events` SSE 接收新结果，由 `requestAnimationFrame` 每次只采用最新结果，取代原100ms轮询；慢页面不积压历史姿态。骨架更新率统计本页实际采用的不同session／sequence且含新观测的骨架，不计重复绘制、纯暂失保持或过期隐藏。统计窗口5秒，数字每秒刷新；浏览器绘制FPS不冒充推理FPS。源头低帧率或浏览器负载仍会限制实际更新率，不承诺固定30Hz。

板端处理耗时取近5秒匹配样本的中位数，后台保留P95但不在页面展示。派生模式通过独立只读TCP连接订阅39383原始结果，校验现有PIWFUL3格式并按session／sequence／frame／source_ns四元身份匹配；最多缓存256条，重复和旧会话不续期。`process_ms`包含预处理、输入写入、模型调用与最终等待、输出读取和候选选择，不含后续姿态滤波、HDMI绘制或跨设备传输。它不是纯NPU耗时，也不是RF到显示端到端延迟。

原始结果端口只有一个消费者：被其它记录器占用或断开时，耗时显示“—”，派生骨架继续独立显示。可用 `--metrics-port 0` 禁用附加耗时连接，或指定其它原始端口。旧软件可显式使用 `--mode raw --port 39383`，直接复用原始流耗时，不额外连接。原始模式接收间隔超过750ms提示等待、2秒提示过期并保留末次姿态；派生模式在本页逐帧检查250ms有效期并隐藏过期骨架。断线自动重连，不控制板端停止或重试。

2026-10-31补充：同时运行本机raw记录器和view页面时，view使用`--metrics-state-url http://127.0.0.1:39381/api/state --metrics-port 0`共享已有raw观察器计时，避免争用板端单消费者端口。每250ms读取本机最新原始结果，仍按四元身份匹配近5秒样本，中位数基于这些采样而非每个输入帧；不向展示链注入原始姿态。仅允许本机HTTP，源断开／过期时隐藏耗时，骨架接收独立继续。定向测试覆盖计时更新与失联隔离，并在[本轮长测](../../../FPGA/csi_preprocess/LONGRUN.md)中修复发现的空白耗时，人工确认数值更新。单独运行view仍可沿用原直接TCP计时方式。

```powershell
# 手动运行PC观察端；此命令会连接指定的板端地址：
node software/pose180_pipeline/host/resident.mjs --board 192.168.50.49 --mode view --http-port 39380
# 本地历史回放不连接任何板端端口，耗时显示“—”：
node software/pose180_pipeline/host/resident.mjs --replay .local/pose-postprocess-offline/replay/r12-replay.ndjson --http-port 39380 --seconds 120
node --test software/pose180_pipeline/host/test/resident.test.mjs software/pose180_pipeline/host/test/presentation.test.mjs software/pose180_pipeline/host/test/performance.test.mjs software/pose180_pipeline/host/test/host.test.mjs
```

打开 `http://127.0.0.1:39380/`。HTTP只监听本机，最多8连接，其中SSE最多4个；单客户端发送缓存上限64KiB，慢客户端断开后由浏览器重连。关闭页面释放SSE和绘制资源；观察进程到时或Ctrl+C后关闭全部本批socket／HTTP／worker。默认不归档，仅`--mode raw --output <新目录>`可启用原有独立归档worker。PC退出或物理断线不阻断板端CSI／推理／HDMI。

本地21项定向测试通过，覆盖完整记录兼容、拆包、错配、重复／跨会话、过期、无ACK、SSE及耗时断开隔离、页面合并最新结果和退出释放。真实浏览器在约30Hz本地模拟输入下观察到约22～23次/秒骨架更新；页面明确标记模拟测试，仅证明PC更新不再受100ms轮询限制，不作为板端性能实测。[本地页面预览](D:/FPGACompetitionProject/.local/pc-performance-20261028-r1/pc-performance-preview.jpg)。本次没有改写既有启动包产物；新增实现仅在原有打包已包含的`resident.mjs`和`full_record.mjs`中，无新增运行依赖，后续打包会随这两个文件纳入。

## 严格主机模拟输入与完整归档

入口使用现有 `demo_v1/data` 的对齐复数窗口；不接 CSI 实采。原 `demo_v1` 基线与网页资源保持原位复用。

```powershell
node software/pose180_pipeline/host/run.mjs --stage short --count 900 --hz 30 --data demo_v1/data/mixed --output software/pose180_pipeline/runs/new-short --pacer-python python --linger 0
node --test software/pose180_pipeline/host/test/host.test.mjs
node software/pose180_pipeline/host/test/sustained_loopback.mjs --output .local/pose180-pipeline-20261025-r1/localhost-mock-900
```

持续回环仅连接 localhost 并启动真实主机入口；默认 900 帧、30Hz，假板固定 8 个输入槽，先填满 8 个信用，再在首次完整记录归档 ACK 后注入一次 200ms 最终确认延迟。每帧全部 180 候选使用明确的 mock 数值，归档逐字节比对、核对信用与不突发追赶、退出后重新绑定端口证明资源回收。该结果只验证主机协议、缓冲及背压，不构成 NPU／DDR／HDMI 实板稳定性验证。完整主机日志和原值均保存在指定新目录，失败现场不自动删除。

运行目录须不存在，父目录须预先存在。默认结果监听 `127.0.0.1:39381`，模拟输入连接 `192.168.126.49:39382`，展示服务监听 `127.0.0.1:39380`。保留 `HOST_READY`、`runtime.json` 与旧控制器需要的 `session/stage/count/hz` 字段；兼容 `--frames`，优先使用 `--count`。可用 `--input-host`、`--input-port`、`--result-port`、`--http-port` 定向控制回环测试。

默认 `--max-inflight 8`，允许 1～64；全局信用只在完整记录已归档、校验、主机 ACK 和板端最终 8 字节确认完成后归还。默认 `--max-frame-age-ms 1000`，范围大于 0 且不超过 60000；超期停止并保存已收到原值与在途清单。增加预算不改变严格实时判定。

发送按 `epoch+i/hz` 的绝对时刻执行。epoch 在首 tick 前通过 READY/GO 建立，不能按首个晚发帧重置。默认绝对发送误差预算为 20ms（`--send-tolerance-ms`）；普通调度抖动继续跟绝对槽。如果背压使上一发送跨过下一整槽，随后按一帧间隔继续，禁止追赶突发，`strict30Hz=false`，并保留原 `planned_ns`、实际发送时间与漏槽统计。`strict30Hz` 只代表本次完整输入发包节拍；处理、端到端 33.333ms 门另列。pacer 每次只发一个 tick；主机等下一帧信用可用后，以 `NEXT <delay_ns>` 传回最短等待，由 Python 高精度等待完成。Python 下一时刻同时满足原绝对槽与最短等待，不使用 Node 多次 sleep 轮询，通知队列不会按运行时长累计。

完整结果为 `PIWFUL3/3`，固定 74544 字节：128 字节头、256 字节选中姿态、43200 字节预处理输入、720 字节分数、30240 字节全部姿态。头 offset116 为 candidate_count=180，offset120 为 best_index，offset124 为 0。选中姿态仍为 `PIWPOSE1/1`，候选索引允许 0～179。

`actual.full` 在`HOST_READY`及输入准入前按目标帧数完整预写并`fsync`，使用一个至多1MiB暂存块；不只扩展逻辑EOF。本机D盘是机械盘，后续运行用`--output`指定C盘NVMe上的新目录，例如`C:/Users/cenyongdong/FPGACompetitionRuns/pose180-pipeline-20261025-r2/host-hdmi`，父目录须已存在。这样将文件分配移出逐帧路径，并分开来源读取与归档写入；不保证存储永远没有长尾。[本轮实测与存储修正](../RESULTS.md)

每条完整原值先等文件写入回调与必要 drain，再解码和 ACK。该确认表示操作系统文件写入完成，不表示逐帧 fsync。非法／非有限原值保留，不能用晚值替换。收到板端最终确认后，写 `received.jsonl` 并归还信用；`sent.jsonl` 同样逐条等待有界写入。三个写入通道各自最多一个应用层在途写，不向 Node stream 连续堆积。`--hdmi 0|1`明确本次实际模式，默认1；初始化连接等待60秒，发包后的1秒帧龄门保持。

固定内存包括 128 窗预读环（短批次相应缩小）、2 个输入封包槽、1 个完整结果槽、1 个 ACK 与 1 个最终确认槽。封包槽必须等 socket 写入回调及必要 drain 后才能复用；结果槽必须等完整归档／ACK处理结束后才能进入下条记录。网页只保留最新姿态，慢 WebSocket 的发送缓存超过 64KiB 时断开。

结束时按实际写入字节截断预分配文件，生成 `summary.json` 和 `host-delivery.jsonl`。未确认的完整原值仍在 `actual.full`；不足完整记录的尾部保存在 `actual.partial`，不足最终确认字的尾部保存在 `confirmation.partial`。失败不会自动重试 SDK 或设备。
