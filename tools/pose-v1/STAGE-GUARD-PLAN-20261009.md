# 原复制快照与582完成检查：本批执行契约

，代理执行。读取[ADR_19](../../ADR/ADR_19.md)、[旧103失败](BOUNDED-LOAD-RESULTS-20261009.md)，保留旧现场。本批目标是检查和取证候选，不预先认定定点误差、过早读取或缓存根因。

新包 `.local/pose-v1-stage-guard/package-20261009-r1`；构建 `.local/pose-v1-build/mixed-20261009-stage-guard-r1`；板端 `/tmp/pose-stage-guard-20261009-r1`；证据 `evidence/stage-guard-20261009-r1`。程序27b9ff09…2769e086，manifest de32738d…96ed48d，403载荷71构建来源。

1. 构建及源码身份；无设备Native快照所有权、边界和新计数等待负例。Native已通过11拒绝、16字节拥有值、3次实际mock进度查询。
2. Lite Host107、既有IPC/AU/协议/保存契约及新增ARM快照契约；真实Host192异常探针保留旧拒绝/暂存/两轮源读取，并检查新快照逐位一致。420秒外部预算，仅Host不打开NPU/VPU。
3. 核验后传输本机Host acceptance，新目录process-three；先预置同协议PC输入/RTSP客户端，再180秒三窗＋重复。完整输入/分数/姿态逐位旧参考、4份ARM/Natively重建画面、实际NAL/PTS/解码来源/回收；每调用8输入快照元数据＋1条582新计数，共36条。新计数初始/最终、轮询数、时间单列，不把DMA/cache解释混入。
4. 前门通过后传输process-three acceptance，重新审查普通高阶页；新的180秒load-103、5Hz固定103记录、100计量。旧失败r2不重跑，异常保存停止，不自动重试。保留103/104预算、完整拥有结果和稀疏29 ARM参考及Native完整参考。正常新元数据预期927条，原计量与新增开销分别报告；严守严格速率和来源覆盖。
5. 保存最终资源/内核/身份/端口和自有进程状态，回传核验，更新ADR_19/17、Done及检查点；任一阶段失败停止其后硬件门检。规整仅根据现场证据并保存原因/前后/时间，不清缓存/重启/改CMA/BOOT。

运行命令均由代理在独立会话发起，SSH凭据不进入脚本或报告。新runner为`run-stage-guard.sh`，门检`review_stage_guard.py`＋`review_stage_observations.py`；视频独立Native参考、OpenCV逐帧及网络时钟核验复用冻结审查器。本批没有直接地址映射/零拷贝、HDR/HDMI或30分钟试验；“新增完成检查后不再出现”不单独证明根因或永久可靠。
