# 无探针启动位流与可靠性验证

2026-10-25，移除当前位流的全部检查探针／协议检查器，并作为启动位流进行可靠性验证。本轮在独立覆盖层移除r45的AI事件与六路读监视器、启动见证、逐周期记录器、AXI协议检查器及记录器、诊断CSR路由、有限启动返回消费器和MARK_DEBUG属性。原r45源码、产物与失败证据保留。

范围纠正：将`hp2_startup_drain`及控制入口一起删除是代理的分类错误。该模块主动接收、丢弃限定的启动异常返回，属于缓解行为，不能归为纯观察探针。因此本轮不是“仅移除被动探针”的对照，不能用其DMA失败判断探针或消费器的单独影响；后续移除诊断应保留主动消费及必要安全条件。复用此前成功的原r45镜像上板，另建r10包，不重用本轮额度。

保留AI四路连接、HP2/S01本地HDMI、原HP2就绪／复位、原时钟、功能AXI协议及HDMI采纳／错误／STOP排空逻辑。常驻程序新增显式`POSE180_DEMO_PROBE_FREE`构建配置，完全不创建旧诊断MMIO映射；普通构建默认仍沿原仪器化入口。模型、SDK、数学、帧协议和r8时间网格跟踪保持。

无线源复用已完成独立四机重启及接收重连验证的[路由器自启动服务](../../../software/pose180_pipeline/resident/autostart/README.md)，目标仍为板端`192.168.50.49:39033`。本轮早期仅上传过临时无线包、未加载或启动；这些临时目录随后已被路由器任务的重启清除，不执行本地旧`radios_run.py`的load／start／stop。两项聊天协调共用设备。

本轮使用原厂2018.3／030ai与Procise路线，复用原厂PS及未改IP检查点，重新综合及完整布局布线。只有实际时序、完整路由、必要DRC和诊断结构移除核验通过，才生成并安装新的BOOT。原AI两项最小周期例外保持，不新增豁免。

计划可靠性范围为最多3次独立候选启动，每次最多1次SDK初始化；前两次各120秒真实CSI／HDMI，最后一次1800秒。每次先核对实际启动身份并恢复磁盘上的原BOOT作故障回退保障，再开展业务；成功退出后才能进入下一次启动。出现实际SDK／设备失败时停止本轮后续负载，保留证据并在安全停止条件成立后执行最多1次原BOOT回退，不将外层超时当作设备失败。全部测试通过后，最后一轮仍运行候选时将候选BOOT写回启动文件，保留原BOOT备份；不遗留测试负载。

本轮已执行并关闭，可靠性验证未通过：第1次无探针候选能启动Linux，但SDK初始化上传参数发生真实DMA超时，后两次及30分钟试验取消。实际1候选／1 SDK／1原BOOT回退，余额全部0。旧DATA、D45全面根因调查及姿态问题仍暂停，不宣布旧根因关闭。

## 实际物理结果与交付身份

完整综合、优化、布局、物理优化、布线、报告及bit生成的原生退出码均为0。实际布线84934／84934条可布线网完成、路由错误0；setup WNS `+0.030 ns`、hold WHS `+0.012 ns`，TNS／THS均0，内部未约束端点0。仅保留原AI两项同对象最小周期例外`−0.409／−0.071 ns`，因此原始`raw_timing_pass=false`，不伪写全部原生时序通过。最终DRC仅使用原有目标与GT适配范围，无新增豁免。

实际布线网表中七组诊断层级均为0、调试核0、MARK_DEBUG网0。原厂链接网表继承的1277个MARK_DEBUG属性在布线前清除；HP2就绪路径仍以5ns约束，实际slack `+0.580 ns`，S01 ARVALID／ARADDR／RREADY功能连线保持。详见qualification.json（本机留存，仓库未附：`../../../tools/pose-v1/evidence/hdmi-probe-free-20261025-r1/qualification.json`）及同目录`physical/`原始报告。

| 产物 | SHA-256 |
|---|---|
| 新BOOT（未晋升为默认启动文件） | `5046c75573d77a664fe96e7e67918850708ebf413d0a05110be1cf286eaabeac` |
| Procise处理后的bit | `3e178f1ce08de686a88e20348faf14d73bc0fe9d23d4aca497631cdefe534768` |
| 当前恢复的原BOOT | `ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef` |

新BOOT路径为`.local/hdmi-probe-free-20261025-r1/boot-package/BOOT-probe-free-r1.bin`，长度7023552字节。PL以外所有字节、padding及原FSBL／bl31／U-Boot均与原BOOT一致，见package-review.json（本机留存，仓库未附：`../../../tools/pose-v1/evidence/hdmi-probe-free-20261025-r1/package-review.json`）。源／约束身份记录于qualification，配套ARM64编译及无旧观察器符号检查通过。

## 第1次板测与失败原值

候选实际boot_id为`c85ef290-22d3-4088-9abc-e33ea650f6e1`，串口收到完整Linux启动、SSH恢复、FPGA状态为operating。新软件确认`hardware_profile=probe_free; diagnostic_MMIO=0`，没有运行旧协议检查器准入／有限消费。原BOOT已在同一次候选运行中恢复至启动文件，再启动唯一一次SDK。

三RX自动连接并形成共同窗口，状态计数`received=2`。SDK在`Session::apply → ApplyHelper::applyUpload → MemChunk::write → dmaWrite`阶段失败，原始异常为：

```text
stage: initialization, invocation: 0
Check failed: (done) is false
DMA Read time out (5000 ms).!
DDR_DMA_STATUS: 0X5
DDR_RDMA_CNT: 1000024232
DDR_WDMA_CNT: 1000024332
DMA_VERSION: 1000024426
```

监督进程实测31.619568秒后结束，native exit=3，推理0、HDMI采纳0。没有可用模型输出，原生score／pose失败转储均0字节；未晚读、未重试。完成记录`native_shutdown_complete=true`，设备owner为空；内核日志before／after原值完整保留。此样本证明移除诊断结构仍不能保证SDK初始化成功；表现与旧D45上传异常相似，但无探针样本不能确定底层机制，也不能据此判定原探针是唯一原因或完全无影响。

## 恢复与证据

已安全回退并核验原BOOT运行，当前boot_id `49232404-e890-4d36-afd2-f91a211f08a4`。原BOOT及另外8个启动文件、SDK身份和无设备占用通过最终核对；第1轮关闭，未执行的第2／3轮撤销授权。两次只收UART均已关闭，PC临时`.50.102`已移除、原`.126.100`及WLAN保留，TX／RX3临时SSH已恢复关闭。

路由器持久自启动继续启用：TX仍为同一generation1，最后样本84次续期、0失败；三RX在板端接收程序退出后正常等待重连。本轮未加载或停止无线驱动／守护，没有遗留本轮测试负载。

- 最终状态：state.json（本机留存，仓库未附：`../../../tools/pose-v1/evidence/hdmi-probe-free-20261025-r1/state.json`）。
- 原始板端包：`.local/hdmi-probe-free-20261025-r1/round-1-result-evidence.tar.gz`；提取入口`board-evidence-round-1/`。
- 原始失败：`board-evidence-round-1/pipeline/run/engine/failure.json`；退出与资源：`pipeline/outcome.json`、`pipeline/run/completion.json`、`pipeline/metadata/`。
- BOOT安装／恢复／回退／关闭与最终审计：`board-evidence-round-1/boot-control/metadata/`；串口：`uart-candidate-1/`、`uart-fallback/`。

本候选保持未晋升状态；先复验原r45镜像。该候选的SDK／DMA失败机制尚未定位，不自动重复本配置、不恢复旧包或全面根因调查。源码、bit与BOOT及全部失败证据保留。
