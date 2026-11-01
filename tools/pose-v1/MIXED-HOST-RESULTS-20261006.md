# mixed-r1 Host桥回归验收（2026-10-06）

## 工程内容总结

完成Lite host-check并回传，代理直接读取完整目录，运行已批准的文件核验器并独立逐输出复查。
平台为Lite、ARM Icraft/CustomOp3.39.0；新mixed-r1程序人工以FPAI GCC9.4/CMake3.24.2构建，
SHA256 `7cf761f1dd7d1ca1bf8a1db1826e4d9b34574b1a8dc0ac662c987eed52722a17` 与回传一致。

107例=18正常/89异常拒绝，逐条case/op/expected/rejection/passed与原fixture一致；
12条注册前后记录匹配，五个缺失节点的三类函数显式注册，Gather保持原实现。
22份输出共59,600 FP32值全有限，与原NumPy参考逐位一致、最大差0；提供输出缓冲区与不提供两种路径均覆盖。
新桥实际SDK暂存搬运事件已记录，源/目标指针均CPTR；三类适配节点188/192/437/582/649均观察到事件。

包290项/完整回传45项哈希、程序/包及上一build验收身份匹配；15份ARM头文件、Host/ZG库及版本保持。
ldd无缺依赖，退出0、stderr空，stage started→host_bridge_regression_completed，mode=host-check/device_init_allowed=false。
完整dmesg前后逐字节相同，无本次新增内核消息；既有启动恢复/journal/驱动提示保持，不归因于本次测试。
内存available 686→687MiB、Swap0，仅前后快照，不是峰值或混合模型内存测量。

正式验收文件：[host-check.acceptance.json](evidence/mixed-20261006-r1/host-check.acceptance.json)，
独立结果：[host-independent-review.json](evidence/mixed-20261006-r1/host-independent-review.json)，
完整回传 `tools/pose-v1/evidence/mixed-20261006-r1/host-check`。
代理未重新运行检查器、编译、访问Docker/SSH或设备。

## 对后续开发的参考

已证明新注册入口与SDK Host暂存桥在原107规格/拒绝门检下保持原数值，注册/Host侧搬运可作为后续工程起点。
本阶段使用合成参数与Host CPTR，不证明真实RAW加载、ADDR/BOTH、NPU同步/计算、完整Session或部署数值通过。
CPU Matmul仍未补齐；Gather保持，正式Matmul NPU分配未改变。

现在传入host-check验收文件后可进入既定离线阶段。此前提前运行offline-check的失败目录仍需保留回传，
确认只停在门禁预检后按[命令补充](MIXED-VALIDATION-COMMANDS.md)保留改名，避免覆盖或因目录存在拦住下一次正式执行。
不要重跑host-check，不直接进入memory-check/apply/mixed；每阶段仍须完整回传核验。
