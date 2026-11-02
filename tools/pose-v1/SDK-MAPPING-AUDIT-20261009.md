# ARM SDK搬运、同步和映射边界核查

本批仅读取冻结ARM头文件、匹配XRT/AXI插件及板端sysfs元数据，不创建映射、读写参考寄存器或改驱动。XRT SHA a29e4eee…749dc96，AXI插件d55e4887…5fc7178，均与已核验板端基线匹配。版本号或接口名称本身不作为同步证明。

## 已核验路径

- XRT `MemPtr`区分CPTR、ADDR、BOTH；构造BOTH需要已有C指针与设备地址，构造函数不负责证明两者是同一有效映射。当前模型设备源实测为AXIZG330AIPLDDRMemRegionNode/ADDR，不能取CPTR或强转地址。
- `HostMemRegion`与`CacheSyncHostMemRegion`在本机Linux ARM read/write成功路径均取得CPTR后执行普通memcpy；后者没有在所核验函数体中提供可用的DMA/cache fence。ARM缓存助手在Linux分支不要求显式flush/invalidate；不把它当作设备一致性的证明。
- 默认跨区域复制沿XRT临时Host字节→源region.read→目标region.write；PL DDR read处理64字节边界和尾部，再走dmaRead。新审计的dmaRead有锁、内部传输与进度检查，再调用MemChunk::read读取UDMA区域。直接Tensor::read仍共享该源区域入口，不是已证实的修复。
- UDMA区域read成功路径有锁，使用CPTR计算offset，写offset、size和sync_for_cpu相关属性后再memcpy。它证明SDK存在内部同步动作，不证明当前失配已经定位到该动作，也不是让应用任意CPTR/ADDR包装成BOTH的许可。
- 私有MapDevice调用的GP0/GP1标识来自RegRegion初始化，用于已有NPU/DMA寄存器映射；它不能替代PL DDR数据CPU映射契约。本批没有调用该私有函数或直接打开/dev/mem。
- 只读板端udmabuf0：driver3.2.5、物理地址0x30100000、大小134217728、dma_coherent原值0、sync_mode原值1。这些不是CPU虚拟地址或现有模型源的身份。当前本地资料搜索未找到可确认匹配该已编译驱动的源码；没有假定同版本上游源码与厂商模块完全一致。

## Host生产组边界

冻结图和融合表的静态映射如下，所有相关NPU组成员均无当前Host算子的祖先依赖，已检查等待循环风险；仍不是运行时DMA同步证明。

| Host节点 | NPU生产组结束计数 | 当前额外新查询/等待 |
| --- | --- | --- |
| TopK188 | 223 | 无 |
| GatherElements192，两输入 | 234 | 无 |
| TopK437 | 477 | 无 |
| 原Gather442设备输入；另一输入来自Host437 | 481 | 无，原注册保持 |
| ScatterND582，两输入 | 638 | 有 |
| ScatterND649，两输入 | 720 | 无 |

因此582的638检查没有覆盖更早或后续649的读取。此次有限姿态失配既可能来自这些输入，也可能来自其后NPU计算或最终搬运；没有Host帧快照和即时计数，不能直接锁定649或582。下一先保存原复制后的一帧输入并与同CSI参考比较，再决定具体等待或搬运修正。若新增观察/保守生产组等待，必须分别记录其是否实际等待，保持原Gather实现和CPU数学；不能只看最终745就推断所有较早CPU读取已经及时。

## 零拷贝可行性结论

目前只确认UDMA区域有内部CPTR和同步路径；没有验收当前PL DDR源的应用可用CPU映射、所有权和缓存契约。将输入搬到UDMA再包装Host视图可能仍需一次PL→PS DMA，不能称NPU/CPU零拷贝。真正跨域共享还需要确认硬件可达地址、后端分配与MMU、缓冲生命周期、读取完成和释放；本批不改图分配/BOOT/驱动或SDK。

后续独立内存验证需从公开SDK提供的合法对象和Region开始，确认地址对应、边界及生命周期，然后逐位往返和异常释放。没有这一契约，保持显式SDK复制，先补齐数值异常取证。静态依赖证据（历史附件，当前仓库未附：`evidence/startup-guard-20261009-r1/Host-producer-dependency-review.json`）；[有限失配与保存缺口ADR_20](../../ADR/ADR_20.md)。原始函数范围和哈希保存在本机本批证据目录，说明仅限已核验函数与平台。
