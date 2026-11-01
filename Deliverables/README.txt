当前交付入口（2026-11-01核对，r4，原生RAR5）

1. pose180-csi-release-20261031-r4.rar：唯一最新部署包，CSI分组流水＋PL骨架合成、30段官方输入、PC滤波前后双页、最新版BOOT与四机实时采集安装文件。
2. pose180-complete-sources-20261031-r4.rar：精简完整源码＋JSON/RAW/ONNX模型＋当前合格BIT，实际198,429,558字节（198.43 MB）；含当前FPGA重建必需IP／网表／基线，无无关器件和重复缓存。
3. pose180-csi-release-20261031-r4-DEPLOY.md：PC解压上传、默认BOOT、手动启停和恢复。
4. SOURCE-20261031.md：源码入口、权重范围、厂商闭源依赖与重建限制。
5. PERFORMANCE.md、evidence/：关键性能、资源、数值差异、长测和原始报告。
6. release-20261031-r4-validation.json、两份.rar.sha256：实际大小及完整性核验。

当前只保留r4交付；旧压缩包和解压副本清理记录及旧说明／校验／关键硬件报告留在.local/delivery-cleanup-20261031-r1/。
工作源码、原始训练checkpoint及.local原始证据不删除。r4为本机交付修订，本轮未连接或修改设备，最近板端核验目录仍是/root/pose180-csi-release-20261031-r1。

7. FPGA-REBUILD-20261101-r1.md、evidence/fpga-full-rebuild-20261101-r1/：从r4 RAR新解压的完整本地综合／布局布线／BIT与Procise证据。新BIT在FPGA-rebuild-artifacts-20261101-r1/，仅日期时间头与原合格BIT不同，未上板。
源码RAR保留10月31日独立重建验证的冻结身份；部署RAR于11月1日同步实时采集完整说明、四机安装文件，并仅附最新版BOOT。两份RAR各自的最新校验值以同名.sha256为准。提交用技术文档Word／PDF本轮暂不处理。
