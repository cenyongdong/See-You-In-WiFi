# 180-query 演示工程与核心源码

当前默认硬件配置已更新为CSI v3：PL CSI预处理与骨架绘制开启，CPU人物滤波保持。ARM64使用 `cmake --preset csi-v3-arm64`，离线检查使用 `native-offline`；旧缓存需重新配置，完整命令与直接执行参数见[构建说明](resident/DEMO-INPUTS.md)。

2026-10-31最新发布采用CSI分组流水＋PL骨架绘图，默认30段／8700窗官方输入；[部署说明](../../Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md)、[完整源码](../../Deliverables/SOURCE-20261031.md)。下文三片段包属于10月29日历史基线。
当前源码统一在本工程内按模块维护。先看 [核心源码索引](src/README.md)，再看 [双输入演示说明](resident/DEMO-INPUTS.md)。正式目标 `pose180_demo` 保留实时采集与官方预采 CSI 两个入口，共用原 epoch99 和 HDMI／PC 输出。当前30段包采用 TopK=3、严格 score >0.2、CPU 多人跟踪／滤波，在同一次SDK生命周期中顺序播放1／2／3人共30段、8700个不同窗口并循环至有限时长；[三片段](resident/DATASET-PLAYLIST.md)与Top1模式留作历史。

```text
pose180_pipeline/
├── src/           # C++ 核心：app、common、input、preprocess、inference、pose、display、io、diagnostics
├── control/       # 手动启停、双输入准备、进程／网络清理、路由器服务及 Python 测试
├── host/          # PC 服务、web/ 页面资源与 test/ 检查
├── tests/         # 原生测试、Nexmon 测试与 SDK 替身
├── tools/         # 构建／打包脚本、native/ 离线回放与向量工具
├── resident/      # 运行说明、验证记录与历史恢复资料
└── CMakeLists.txt # 当前统一构建入口
```

2026-10-29 按模块实际搬迁源码并更新 CMake、脚本导入和 PC 资源路径。旧目录只留必要指引，历史原值与必要证据按原身份保留，旧交付压缩包／副本已清理。当前验证范围见 [最终审查记录](resident/FINAL-REVIEW.md)，设备状态见 [恢复入口](../../FPGA/hdmi_candidate/RESUME.md)。

## 早期严格归档链（历史）

**现行演示入口已按ADR_50改为[常驻核心与真实CSI→推理→HDMI](resident/README.md)，后续r5已接入PC渲染，完成30分钟运行期及RX／PC物理断线验证并关闭；现行细节见[TechDetails](../../ADR/TechDetails.md)。下文保留早期严格逐帧归档链的设计与实测范围，不代表最新演示架构。**

2026-10-25。以迁移最佳epoch99的180-query图作为后续项目推理主图，落实入口在途控制、固定缓冲复用及归档背压。新入口位于本目录；原100-query与r53源码、模型及历史证据保留。**已部署实测；原BOOT取得7,840份完整有效输出后因Host归档1秒保护停止，修正后软件验证通过。获准的新HDMI包又在SDK前因启动准入失败停止并回原BOOT，已关闭；整机稳定性未通过。**实际结果及恢复身份统一见[本轮实测](RESULTS.md)。

数据链为主机已保存的论文复数CSI窗口→PIWCSI2模拟输入→原CPU预处理→180-query单SDK运行时→PIWFUL3完整结果回传→主机归档ACK→有限性/身份检查→可选HDMI采纳→最终确认。没有接入路由器、Nexmon采集或CSI实采模块。PC网页仅展示最后一份确认结果。

## 缓冲与所有权

| 环节 | 实现与固定上限 | 回收条件 |
|---|---|---|
| 主机输入 | 128窗预读环、2个86,432字节封包槽；pacer最多1个待消费tick | socket写回调及必要drain完成后复用封包 |
| 全链在途 | 默认已发−最终确认≤8，最老未确认帧默认≤1秒 | 完整归档、校验及最终确认后归还信用；超期明确停止 |
| 板端输入 | 8个固定地址的完整复数窗口槽 | 唯一SDK线程完成本窗推理后释放 |
| 推理 | 1个长期持有的输入Tensor；720/30,240字节固定SFB暂存 | 公开最终wait、实际融合完成检查后复制完整首次输出 |
| 板端结果 | 64个固定拥有值槽，input/scores/poses净数据74,160字节/槽 | 发布、归档、可选显示及最终确认完成后释放；从不覆盖在途槽 |
| 归档 | 主机完整记录槽74,544字节；raw、metadata和sent各最多1个应用层在途写 | 同时等待写入回调及必要drain；写入完成不等于逐帧fsync |
| HDMI | 原同Device的RGB565双帧，合计8,294,400字节；CPU工作图跨帧复用 | 采纳ID/地址/pending证明后才能复用旧帧，原STOP排空证明后才能释放设备帧 |

只有SDK拥有线程调用Runtime、设备写帧及CSR。接收、归档线程接触CPU拥有值，交接槽借用结果池中的只读引用，发布线程持有该槽租约直到采纳完成。进入下一次可能阻塞数秒的forward前，先证明上一帧采纳，不延后或重置200ms期限。末帧单独排空，无额外推理。

主图直接使用已有`model/piw24_pose180_shared-20261024-r1/piw24_pose180_ZG.json/.raw`。没有TopK、GatherElements、ScatterND或旧内部Host桥；输入仍为`[1,180,60]`，完整输出为180分数及180×14×3姿态。最终完成数由实际apply后的metadata导出，不套旧图计数。输入写入及最终输出的公开SDK读回仍保留，不能据此关闭D47全部根因。

## 回传与背压

PIWFUL3/v3固定74,544字节：128字节头＋256字节选中姿态＋43,200字节tokens＋720字节分数＋30,240字节全部姿态。头116为候选数180，120为最高分槽位，124保留0。旧PIWFUL1/2解析器及100候选格式不改；新解析器完整检查0～179候选与选中姿态对应关系。

每帧先归档全部首次原值，再校验并发8字节ACK；板端检查及HDMI采纳后回8字节最终确认。未确认原值和不足完整记录的尾部独立保留，不用晚读、旧结果或丢帧修补。SDK/非有限/身份/资源错误停止且不自动重试。

主机按原绝对30Hz计划记录实际发送。普通调度抖动按绝对槽运行；背压跨整槽后不追赶突发，也不重置epoch。输入节拍、处理时限和端到端时限分别报告，背压后即使所有帧完整交付，也不能写成严格30Hz通过。180图已有约4.99秒长尾，默认1秒帧龄会将其明确暴露；加深队列不能关闭长尾。

## 构建、测试及软件包

在项目根目录执行`python software/pose180_pipeline/tools/build.py`，复用现有FPAI、GCC及SDK3.39.0；构建器保留原生退出码和首次编译失败日志，增量构建成功后恢复容器原停止状态。不运行EDA，不重建已合格r45位流。

主机定向测试入口为`node --test software/pose180_pipeline/host/test/host.test.mjs`；持续localhost模拟见[主机说明](host/README.md)。C++测试覆盖固定池/交接/异常唤醒/完整协议及画布复用；C++实际编码记录与Node解析器另作交叉检查。这些均无实际SDK/NPU或HDMI硬件执行。

本机构建日志、二进制与一次软件包集中在[产物目录](../../.local/pose180-pipeline-20261025-r1)。`tools/package.py`在该目录生成`software-package.tar.gz`和身份清单，校验JSON/RAW与已部署epoch99身份一致。原模型数值误差D48及原失败保持，软件通过不构成精度或整机稳定性通过。

最新归档修正后的900帧软件回环、3.94GB生产writer测试及本轮实板失败范围，统一见[本轮实测](RESULTS.md)和[版本归档](evidence/20261025/README.md)。此前900帧结果及修正前日志保留为历史；软件通过不构成NPU、HDMI或严格30Hz实板结论。

离线完整归档解析入口为`node software/pose180_pipeline/host/analyze.mjs <actual.full> <catalog.json> <新的analysis.json>`。使用两个固定记录缓冲与来源偏移索引，检查全部180候选、完整身份／选择及同源重复的首次输入／分数／姿态字节一致性，不将重复一致性扩大为模型精度通过。

## 早期严格链的恢复记录（历史）

当前已回原BOOT、没有设备占用；新HDMI包`pose180-hdmi-20261025-r2`及旧包均已关闭。未来板测先按新的具体范围核验实际设备、原BOOT/六SDK库、无占用和恢复通道，不从历史boot_id或旧已关闭包恢复额度。`tools/board.py`复用原固定主机密钥及一次性内存认证，不把密码写入命令行、环境变量或日志。

包内`run_board.py --session <主机runtime.json中的session> --frames 52800 --hdmi 0|1 --hard-seconds 2100`只支持一次SDK进程，使用独占attempt标记、原始日志及资源观察，不写BOOT、不重启。HDMI模式必须先有新包同次启动的`startup-admission.json`及`startup-mode.txt`；本软件包没有新增BOOT/重启次数，也不提供绕过启动准入的方法。若实际需要候选启动，须按具体新包明确授权。主机参数见[host/README](host/README.md)。
