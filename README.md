# 基于 Wi-Fi CSI 的嵌入式多人三维姿态感知系统

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

原创部分采用 MIT；模型派生代码、官方数据、厂商资产等适用各自条款，详见 [第三方声明](THIRD_PARTY_NOTICES.md)。

## 一、作品介绍

本作品面向高隐私性智能家居，通过 Wi-Fi 信道状态信息（CSI）感知人体动作，在悟净 Lite 平台完成多人三维姿态推理与显示。系统无需摄像头或人体穿戴设备，以三维骨架呈现活动，为居家活动观察、健身交互等应用提供感知基础。

系统采用 PS、NPU 与 PL 协同实现：PS 负责输入整理、相位双精度收尾、姿态后处理与坐标投影，NPU 执行模型推理；PL 执行 CSI 幅相计算及90点分组流水、二维骨架／关节点／动态信息绘制与本地 HDMI 合成。PC 网页作为可选观察端，支持三维视角交互；板端推理和本地显示可以独立运行。

```text
实时 CSI 采集 ──┐
               ├─→ PS＋PL 预处理 → NPU 姿态推理 → PS 筛选、跟踪与滤波 ─┬─→ PL / HDMI
板端官方 CSI ──┘                                                └─→ 可选 PC 三维网页
```

两种输入互斥，共用同一套预处理和推理链。官方数据模式在板端读取转换后的原始 CSI 并逐帧推理；当前演示包采用 **30段连续官方训练片段、8700个不同窗口，1／2／3人各10段**，默认有限运行30分钟。模型采用原 epoch99 的 180-query 部署图，输出最多三人、每人 14 个关节，使用 TopK=3 和严格 `score > 0.2` 筛选。

本仓库保存当前软件核心、FPGA 工程、模型适配工具、部署交付及开发记录。阅读源码从 `software/pose180_pipeline/` 开始；直接部署从 `Deliverables/` 开始。项目已完成有限实板演示、30分钟官方输入长测、交付整理及源码RAR独立完整FPGA重建，具体实测范围见 [PROJECT-PROGRESS.md](PROJECT-PROGRESS.md)。

## 二、目录与文件职责

### 2.1 仓库目录

| 位置 | 职责 |
|---|---|
| [software/pose180_pipeline/](software/pose180_pipeline/) | **当前主工程**：板端核心、输入控制、PC 页面、测试及构建打包入口 |
| [FPGA/hdmi_candidate/](FPGA/hdmi_candidate/) | HDMI 硬件工程；`rtl/`、`constraints/`、`scripts/`、`sim/` 分别保存逻辑、约束、构建脚本与仿真，发布配置按恢复说明及对应记录核对 |
| [Deliverables/](Deliverables/) | **唯一最新 RAR 部署包和精简源码＋权重包**；`evidence/` 为关键原始报告，旧交付目录已按要求清理 |
| [model/](model/README.md) | 当前部署 JSON／RAW、源 ONNX、转换配置与模型说明已放行；训练 checkpoint 和中间产物留在本机，获取与使用方式见模型索引 |
| [tools/](tools/) | 模型训练、转换、采集、验证与故障分析工具；带日期的取证目录按所属历史阶段阅读 |
| [Docs/commit_docs/](Docs/commit_docs/) | 技术文档、海报等提交材料；`Docs/` 其余部分主要为厂商资料与开发参考 |
| [CompetitionDescription/](CompetitionDescription/) | 比赛选题指南等本机参考资料 |
| [ADR/](ADR/) | 架构决策、接口设计和技术说明 |
| [software/core/](software/core/)、[demo_v1/](demo_v1/) | 早期共享实现与旧演示工程，保留用于追溯；当前 180-query 核心维护位置见下表 |
| `.local/`、`Logs/`、`tmp/` | 本机验证证据、运行日志和临时产物，不作为常规 Git 交付内容 |

### 2.2 部署包与提交文件

| 文件或目录 | 用途 |
|---|---|
| [最新部署包](Deliverables/pose180-csi-release-20261031-r4.rar) | CSI分组流水＋骨架绘图、30段官方CSI、最新PC与BOOT |
| [部署说明](Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md) | 默认位流、手动启动／停止、PC与恢复 |
| [完整源码包](Deliverables/pose180-complete-sources-20261031-r4.rar) | 当前PS／PC／PL、模型原始代码、IP配置、约束、关键报告与JSON／RAW／ONNX和当前合格BIT；含目标器件所需厂商IP／网表／增量基线，工具链及验证边界见源码说明 |
| [源码说明](Deliverables/SOURCE-20261031.md) | 自研／复用分工、核心入口及重建依赖 |
| [完整FPGA重建](Deliverables/FPGA-REBUILD-20261101-r1.md) | 2026-11-01从r4 RAR新解压完成实际综合／布局布线／BIT与Procise；包含完整日志与既定例外 |
| [交付核验](Deliverables/release-20261031-r4-validation.json) | RAR完整性、文件一致性及独立解压构建检查；引用既有BOOT核验，无新增SDK运行 |
| [技术文档排版修订版](Docs/commit_docs/技术文档_v1_排版修订.docx) | 既有提交稿，本轮按用户要求暂不更新；[技术文档 v1](Docs/commit_docs/技术文档_v1.docx) 保留用户编辑版本 |
| [项目海报](Docs/commit_docs/项目海报.pdf) | A1 竖版作品海报 |

部署包解压后的关键位置如下，路径均相对于包根目录：

| 包内位置 | 职责 |
|---|---|
| `board/models/` | 板端推理模型 |
| `board/dataset.piwcsi2`、`board/dataset.json` | 官方 CSI 数据及片段来源、顺序清单 |
| `board/runs/` | 本次运行生成的日志与状态 |
| `check.sh`、`prepare-boot.sh` | 运行前核对及下一次启动凭据准备 |
| `start-dataset.sh`、`start-live.sh` | 官方30片段顺播与实时采集两个启动入口 |
| `stop.sh`、`status.sh` | 正常结束与关闭状态核验 |
| `start-pc.ps1` | Windows PC 观察服务入口 |

### 2.3 当前核心源码

**核心源码集中在 [software/pose180_pipeline/src/](software/pose180_pipeline/src/README.md)，程序入口是 [app/main.cpp](software/pose180_pipeline/src/app/main.cpp)，正式构建目标为 `pose180_demo`。** 同一模块的头文件与实现文件放在同一目录中。

| 模块或文件 | 职责 |
|---|---|
| [src/app/](software/pose180_pipeline/src/app/) | 参数解析、输入选择、推理线程与程序生命周期 |
| [src/common/](software/pose180_pipeline/src/common/) | 公共数据结构、最新窗口、固定缓冲和帧协议 |
| [src/input/](software/pose180_pipeline/src/input/) | `csi.cpp` 接入实时 CSI，`dataset.cpp` 读取官方数据；`nexmon/` 负责解码、三 RX 组窗和重连 |
| [src/preprocess/](software/pose180_pipeline/src/preprocess/) | 幅度与相位预处理，将复数 CSI 转为 `[1,180,60]` FP32 特征 |
| [src/inference/](software/pose180_pipeline/src/inference/) | SDK 与模型资源管理、推理、输出读取和在途资源释放保护 |
| [src/pose/](software/pose180_pipeline/src/pose/) | 候选筛选、去重、人物关联及 CPU 姿态滤波 |
| [src/display/](software/pose180_pipeline/src/display/) | PS坐标投影、PL骨架／关节点／动态信息绘制合成、HDMI采纳与停止排空 |
| [src/io/](software/pose180_pipeline/src/io/)、[src/diagnostics/](software/pose180_pipeline/src/diagnostics/) | 独立网络消费者、状态发布与有界异步日志 |
| [src/compat/](software/pose180_pipeline/src/compat/) | 旧严格链和历史硬件配置的兼容声明 |
| [control/](software/pose180_pipeline/control/README.md) | Python 启停控制、双输入配置、数据准备及路由器服务 |
| [host/](software/pose180_pipeline/host/README.md) | Node.js 观察服务、`web/` 三维页面和 PC 测试 |
| [tests/](software/pose180_pipeline/tests/README.md) | 原生模块测试、Nexmon 测试和 SDK 接口替身 |
| [tools/](software/pose180_pipeline/tools/) | 构建、打包与离线检查工具 |
| [CMakeLists.txt](software/pose180_pipeline/CMakeLists.txt) | 当前 C++ 工程统一构建入口 |
| [resident/](software/pose180_pipeline/resident/) | 演示使用说明、分阶段验证与历史运行记录 |

### 2.4 根目录文档

| 文件 | 职责 |
|---|---|
| [README.md](README.md) | 作品介绍、目录职责和交付入口 |
| [PROJECT-PROGRESS.md](PROJECT-PROGRESS.md) | 项目完成情况、最终配置、实测范围和恢复入口 |
| [DIFFICULTIES.md](DIFFICULTIES.md) | 开发难点、处理方法及工程收口说明 |
| [DOCUMENTATION.md](DOCUMENTATION.md) | 完整 Markdown 导航与历史文档分类 |
| [Done.md](Done.md) | 分阶段成果及开发参考 |
| [REFERENCES.md](REFERENCES.md) | 资料索引与阅读记录 |
| [Agents.md](Agents.md) | 本地工程执行规则与授权边界 |
| [.gitignore](.gitignore) | Git 提交范围，采用指定交付文件放行规则 |
| [LICENSE](LICENSE)、[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | 原创部分的 MIT 许可及第三方内容的适用边界 |
| [SECURITY.md](SECURITY.md) | 本机凭据配置、提交脱敏与安全维护 |

## 三、部署与演示入口

板端使用 ARM64 Lite、匹配的已发布 BOOT、Icraft/customop 3.39.0 和 Python 3。可选 PC 观察端需要 Node.js 20 或以上；包内已带网页资源，无需 `npm install`。完整操作以 [部署说明](Deliverables/pose180-csi-release-20261031-r4-DEPLOY.md) 为准。

1. 在PC解压RAR，将整个目录上传到板端；板端推荐位置为 `/root/pose180-csi-release-20261031-r4`。
2. 按部署说明核对设备状态、BOOT 和启动资格，再执行所选输入的 `check.sh`。
3. 如需 PC 展示，先运行 `start-pc.ps1`，指定实际可达的板端地址及本机有线地址，并排打开滤波前 `http://127.0.0.1:39381/` 与滤波后 `http://127.0.0.1:39380/`。
4. 板端执行 `sh start-dataset.sh` 顺序展示30段官方数据，或执行 `sh start-live.sh` 开始实时采集；两个入口不能并发运行。
5. 数据集默认1800秒结束，实时默认300秒；也可通过 `sh stop.sh` 正常结束，再用 `sh status.sh` 核对关闭状态。

30段片段共用同一次 SDK 生命周期，片段之间无需重启。当前硬件每次 FPGA 配置只允许消费一次功能启动入口，完整结束后再次启动推理或切换输入，须按部署说明准备凭据、正常重启并重新预检。`prepare-boot.sh` 只核对启动文件和准备凭据，不写 BOOT，也不自行重启；单独重启 PC 服务不需要重启开发板。

## 四、进一步阅读与维护

- 了解数据流、模块接口和资源所有权：阅读 [技术说明](ADR/TechDetails.md) 与 [ADR 索引](ADR/README.md)。
- 修改当前软件：从 [核心模块索引](software/pose180_pipeline/src/README.md) 开始，再阅读 [测试入口](software/pose180_pipeline/tests/README.md) 和 [最终审查记录](software/pose180_pipeline/resident/FINAL-REVIEW.md)。
- 查看硬件发布、设备状态和恢复步骤：阅读 [RESUME.md](FPGA/hdmi_candidate/RESUME.md)。历史运行状态不等于设备当前在线状态。
- 查看展示片段的来源和范围：阅读 [30段输入与长测记录](FPGA/csi_preprocess/LONGRUN.md)。

本机Deliverables提供当前完整源码与部署包及校验文件；本次未执行Git提交或远端上传，不将新包标作已公开发布。Git已有交付及模型放行范围见目录说明。大尺寸训练 checkpoint、模型中间产物、SDK 安装资料、日志和构建缓存仍为本机工作资产；旧交付压缩包和旧解压副本已清理，历史关键记录保存在 `.local/delivery-cleanup-20261031-r1/`；因此部分历史附件需要完整开发工作区才能打开。文件范围与文档检查说明见 [完整导航](DOCUMENTATION.md#git-克隆后的文件可用范围)，训练权重的获取方式见 [模型说明](model/README.md#本机保留的开发产物)。

当前板端实现已完成30分钟官方输入长测；PC双页与计时另有本地检查。关键数据及原始证据集中见 [性能汇总](Deliverables/PERFORMANCE.md)。有限演示、长期运行和数值精度分别记录，完整验证边界统一见 [项目进度](PROJECT-PROGRESS.md)，不在本页重复维护。

## 五、获取源码与参与开发

```sh
git clone https://github.com/cenyongdong/FPGACompetitionProject.git
cd FPGACompetitionProject
```

部署现有演示请使用第三节的完整包。源码开发从当前主工程和对应测试说明开始；硬件构建需要匹配的厂商工具链、器件支持及 SDK，普通克隆不附带这些开发环境。设备账号由使用者自行配置，见 [凭据说明](SECURITY.md)。

欢迎通过 Issue 报告问题或提交 Pull Request。修改应说明具体行为、验证方法和适用硬件；本地检查与实板结果分开记录，不提交密码、原始个人采集或无关构建产物。复用原创代码时保留 MIT 版权及许可声明；第三方部分按 [第三方声明](THIRD_PARTY_NOTICES.md) 处理。
