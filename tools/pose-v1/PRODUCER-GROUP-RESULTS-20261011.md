# 独立真实19成员生产者：部署与四调用结果

2026-10-11。PRODUCER-REFERENCE-NEXT实施，有限门检完成。正式并发读取故障未复现，根因未修。

| 门检 | 实际结果 |
|---|---|
| 构建／SDK身份 | 程序0183e2a0…d17d7d5，六匹配头／四SDK库；原模型及RAW固定 |
| SDK无关载荷 | Native及ARM两图案／拥有值／9拒绝通过 |
| mock | 原r1搬运全零exit1；匹配库读写是ret。新r2 mock部署＋35360字节Host CPTR通过 |
| 真实内存／部署 | 35360字节独立SDK自有PLDDR往返逐位；19成员唯一ZG组9185、0→11及真实chunk范围过 |
| 物理四调用 | 同一Session固定A/B/A/B；47040 FP32逐位参考，全有限；交替不同、重复相同 |
| 释放与收尾 | SDK块0、有限管理器／程序结束，BOOT／SDK／内核保持，规整0 |

真实两输出位于61440／40960，容量30240／16800，分别为8467／8479的别名，四边界非OCM。代理先回传核对部署与真实临时内存往返，再放行绑定部署指纹的控制文件。控制等待只是阶段审查，不是硬件fence。每次保持reset(1)、SDK waitForReady／copyFrom及0→11，两个输出全部保存后比较；ADDR／BOTH未解引用，无晚读修补。

两图案来自ADR_38的真实参数／adapted数学，有限FP16／TF32精确可表示；不是一般舍入、ONNX全部输出或真实CSI精度新增验收。原CPU数学／Gather／正式模型745协议、SDK／BOOT／CMA、VPU缓冲与cookie保持；本批无VPU／RTSP／显示、无新Host107。原冻结源由归档逐项复核。

单钟forward调用196.88–461.61μs、复制55.75–145.73μs，仅四次局部记录；不能作为纯NPU时间、性能分位或整机5Hz。首reset至末拥有值约10.04ms，管理器9.16秒包含部署／控制／保存。

r1误把mock当数据存储导致99个索引值失配，全失败记录保留；查明板端／FPAI mock库d6606416…1557776的读写ret后，新r2使用Host CPTR与真实独立缓冲区前置门检，没有修改mock／SDK或吞错。只读收尾初次因旧启动©符号的locale转义出现原字节差异；新UTF-8只读采集逐位同，旧档案保留，没有硬件重跑。

最终本批程序／管理器和代理SSH／SCP结束，项目输入／RTSP端口无监听。内核跨阶段及同方式最终采集逐位同；BOOT9／SDK身份及FPGA operating保持。最终MemAvailable750384／CmaFree26472KiB仅快照，无规整／清缓存／重启或持久配置变更。项目管理估计83/100保持，103／严格5Hz／长期／HDMI待验。

完整源与原始数据留在本机；Git文本不能代替完整证据包。[数值核验](evidence/producer-group-20261011-r2/data-review.json)／[真实部署门](evidence/producer-group-20261011-r2/deployment.review.json)／[ADR_39](../../ADR/ADR_39.md)／[下一](PRODUCER-GROUP-NEXT-20261011.md)。
