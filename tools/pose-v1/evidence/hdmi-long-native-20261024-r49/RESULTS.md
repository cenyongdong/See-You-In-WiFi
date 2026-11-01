# r49：原生RGB565实际联动与30Hz吞吐卡点

2026-10-24。主机权限修正后再做1次候选启动、1次SDK、30Hz/52800帧长测及1次原BOOT回退。使用同一r45时序合格位流与r47软件，不改AI四路、模型/SDK/数学/NPU分配、帧协议或200ms采纳期限。

## 结果与边界

本轮未完成长期稳定性验证。主机真实节拍器在实际沙箱外权限中预检通过；候选健康启动，初态PS AR=0/R=0、消费0拍，完整160位仅READY建议项。启动后恢复原BOOT文件再打开唯一一次SDK。

30Hz负载在短样本中出现积压：主机发送69帧，保存36份完整实际原值并接收35份最终确认；板端记录完成/Host归档/HDMI采纳各36帧，另保留第37次发布尝试及未发布原值。主机最终触发已有20ms节拍门限：`Host missed absolute send slot by 139.454ms; no catch-up burst`，随即关闭输入；板端保留后续`Truncated/idle CSI connection`，native exit=1。父控制器约34.749秒结束，SDK守护约30.611秒，其中实际帧输出阶段只有约数秒。没有自动重试或放宽门限。

只确认骨架短暂可见，不能认定连续显示正常。所有36次采纳faults=0，无200ms超时；STOP证明与帧缓冲释放完成，5次完整原生协议检查无新增错误，SDK/启动身份保持、内核日志未变、无资源危险。消费0拍意味着本轮也未证明异常消费后的功能恢复。

离线复核36份完整原值的有限值、身份、候选选择及源时间戳均通过；其中三份冻结参考输入/全部分数逐位一致，score>0.2受检最大关节三维偏差0.9765625mm，ADR48门检通过。其余样本不能据此宣称冻结准确率。37次索引oracle比较无不一致；本轮无重复源对照。第36份完整原值已保存但未收到最终确认，明确保留`host_count_matches=false`，未把它改写为35或补造确认。

## 实际耗时

| 阶段 | 样本 | 平均 | 最大 |
|---|---:|---:|---:|
| 推理处理 | 35份确认 | 24.035ms | 33.427ms |
| 等待PC归档ACK | 36次完成等待 | 27.280ms | 39.663ms |
| 原生RGB565绘图 | 36帧 | 3.427ms | 11.397ms（首次） |
| SDK写帧至采纳观测 | 36帧 | 12.268ms | 19.617ms |
| PC实际文件写入 | 36份 | 0.267ms | 0.546ms |

完整确认短样本约14.751帧/秒，两次FLIP之间平均约68.297ms。原RGB放大/转换瓶颈已经消除，但不能把CPU渲染提升43.62倍等同于整机提升43.62倍。

源码中，原长测主线程推理后入队即可继续下一帧，publisher处理保存ACK；HDMI联合版本收到Host ACK并完成数值门后，主线程绘图、SDK写帧并等待采纳，完成交接后才继续下一次推理。上述阶段串行合计约67ms，与实测间隔一致。SDK每帧只写一次完整RGB565；回读仅在初始化双缓冲验证，不存在已证的每帧全图读回。应用两端已有TCP_NODELAY。

ACK等待明显大于PC保存/门检本身，但当前时间戳不能区分传输、SSH及调度的具体来源。原长链使用Git OpenSSH，本链使用Windows OpenSSH，先做纯普通内存/网络对照，不据此直接认定根因。提前进行纯CPU绘图可与ACK重叠，预计仅节省约3ms，不能承诺达到30Hz；进一步改变逐帧等待或显示策略属于单独决策。

## 恢复与数据

已完成唯一原BOOT运行回退，原运行身份`ef19aa67-8848-40c6-b4a2-df9da7e4be68`；原BOOT SHA256为ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef。9项启动文件、6项SDK、FPGA operating及无设备占用核验通过。主机、反向转发和两个UART采集器均结束，UART TX=0。包关闭，实际1候选/1SDK/1回退，剩余均0。

板端原始现场：[candidate-evidence.tar.gz](candidate-evidence.tar.gz)，8309678字节，SHA256=99cc6ab37b924182f349444af95dcba438ba3c704540e0d22a09b79372a50ffc。包含未发布原值、全部失败、逐帧时间、索引oracle、SDK/协议/资源及STOP原值。主机完整实际数据：[host/actual.full](host/actual.full)，36×60784=2188224字节，wire SHA256=0f378d0a634c335026abd6d50d2b8f0b9d2558d48a55b539ef27b0520e157427。数值复核：[host/analysis.json](host/analysis.json)，交付阶段：[host/delivery-analysis.json](host/delivery-analysis.json)，执行状态：[state.json](state.json)，简表：[result-summary.json](result-summary.json)，恢复：[final-audit.json](final-audit.json)、[closed.json](closed.json)。

启动前主机服务的隧道随本轮候选重启断开，尚未打开SDK，零输入/输出；其证据以preboot前缀保留。候选启动后重建主机服务并再次通过节拍器预检，没有增加候选/SDK次数。预分配但未接收数据的3.2GB容量文件只在原现场保留，Git保存其零记录说明，不将容量当作原值数据。
