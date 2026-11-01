# CPU适配、SDK审计与初期部署的实施历史

2026-10-13从AGENTS.md迁出，按主题保存原记录；原文“当前”“已批准”“下一步”和暂停/恢复只表示当时状态，不是现行进度或新的执行授权。最新进度见[PROJECT-PROGRESS](../../../PROJECT-PROGRESS.md)，执行规范以[AGENTS.md](../../../AGENTS.md)为准。源行编号与迁移清单用于追溯；不改写原失败、修订或验收边界。

<a id="a230"></a>

## A230 · ONNX参考与正式混合候选（2026-10-06，实施）

来源：整理前 AGENTS.md 第230–231行。

- ONNX参考与正式混合候选（2026-10-06，实施）：工程/数值分阶段，以ONNX直接对照Lite，不等待Icraft全CPU Matmul打通；正式Matmul仍NPU、Gather保持。代理获明确授权创建独立.local/pose-v1-onnx-conda并安装/运行本机CPU ORT1.23.2，固定Python3.10.21/NumPy2.2.5；三样本全部候选有限、首样本重复逐位一致、不同输入响应已验证，完整环境/依赖哈希与产物evidence/onnx-reference-environment-20261006.json。新增独立pose_mixed_check、SDK Host暂存桥、构建/分阶段/回传工具和新包；原推理器/CMake、三CPU实现文件及模型输入哈希保持。新C++尚未编译/板测，不能称mixed/NPU/精度通过。负责FPAI构建、传输、Lite运行；代理准备代码并主动审阅日志。顺序构建→107例Host桥→离线真实RAW/PS→30秒SDK两16KiB往返→300秒Session apply→180秒308→300秒三样本，每阶段回传核验文件同一包/程序匹配后继续；硬件必须--allow-device-init。区域/缓冲区/融合映射不明确或超时/OOM/总线/SDK异常即停止讨论，不自动重试/复位/改SDK/BOOT/模型/缓存策略。数值容限依实测讨论，不做GT/MPJPE/物理标定；HDMI/RTSP/5Hz/延迟/30分钟不含本轮结论。入口tools/pose-v1/MIXED-VALIDATION-COMMANDS.md、MIXED-VALIDATION.md；旧ORT未批准/CPU待讨论属于历史阶段。

<a id="a232"></a>

## A232 · CPU最小适配Lite门检正式验收（2026-10-06）

来源：整理前 AGENTS.md 第232–233行。

- CPU最小适配Lite门检正式验收（2026-10-06）：完成r2交叉编译、Lite独立运行、回传及Windows文件复核，代理直接读取独立核验通过。107例=18正常/89拒绝，22输出/59,600个float32值与NumPy参考逐位一致、全有限、最大差0；12条注册记录匹配，TopK188/437、GatherElements192、ScatterND582/649补齐init/forward并前向通过，Gather442保持原后端并通过，CPU Matmul未补齐。新包282/回传40项哈希、程序/图/Host库、六SDK头文件/3.39.0版本匹配；ldd全解析，提交dmesg前后尾部相同，退出0/stderr空。程序SHA2568cf2017cedf6a97f98ce485d979239b659291f3c91d3a3d550382c1c94588622。仅固定FP32/全有效分布/HostDevice CPTR候选验收，未接入原推理器/创建完整Session/Device::Open/NPU/DMA/HDMI；实际NPU内存交接/CPU Matmul参考及完整mixed仍待讨论，不自动接入或运行。完整CPU-ADAPTER-RESULTS-20261006.md、evidence/cpu-adapter-independent-review-20261006.json和cpu-adapter-20261005-review.json。中途Windows命令拆行错误已人工完整命令解决，勿重跑C；下述“待回传”是历史状态。

<a id="a234"></a>

## A234 · CPU候选Lite运行截图反馈（2026-10-06）

来源：整理前 AGENTS.md 第234–235行。

- CPU候选Lite运行截图反馈（2026-10-06）：截图显示在批准路径完成传输/运行，sh run-cpu-adapter.sh及exit.txt均0，stdout报告107例完成、stderr显示空，summary status=cpu_candidate_tests_passed/case_count=107，device_opened/full_model_executed/mixed_verified均false。这是程序内部检查报告；本地尚无完整回传目录，注册12条记录/实际22份输出/板端SDK和程序哈希独立联查未完成，不能提前宣布完整CPU门检或mixed通过。现在人工操作CPU-ADAPTER-COMMANDS.md D完整回传并文件数值复核；不要重跑C/覆盖目录/直接接入推理器。代理未连接板端或运行程序。截图和结构化反馈evidence/cpu-adapter-board-run-feedback-20261006.png/.json；此前目录未创建/运行未执行属于较早状态。

<a id="a236"></a>

## A236 · CPU测试目录前置补充（2026-10-06）

来源：整理前 AGENTS.md 第236–237行。

- CPU测试目录前置补充（2026-10-06）：现场反馈mkdir /tmp/pose-v1-inference-20261005/cpu-adapter-20261005报No such file or directory/cannot create directory，推测历史父目录缺失，板端实际父路径尚未只读确认；不归因于重启或模型/SDK故障。已在CPU-ADAPTER-COMMANDS.md C补齐Lite SSH中ls检查、mkdir -p仅补同一批准父目录，再以普通mkdir创建独立子目录；若/tmp缺失/权限错误/子目录已存在则停止，不删除/覆盖。属于既有批准测试路径的前置说明补全，代理未创建目录、传输、接入SSH或运行算子；CPU数值/NPU仍未通过。

<a id="a238"></a>

## A238 · CPU候选r2交叉编译复核通过（2026-10-06）

来源：整理前 AGENTS.md 第238–239行。

- CPU候选r2交叉编译复核通过（2026-10-06）：完成新包package/20261006-r2和构建cpu-adapter-20261006-r2，配置/两文件编译/链接通过，日志无error/warning正文。代理只读核对282项包哈希、5份源码/副本及实际脚本哈希、六ARM头文件/Host库/两包3.39.0，全部匹配；新旧281项非manifest文件相同，数学输入/参考未变。ELF AArch64 PIE SHA256 8cf2017cedf6a97f98ce485d979239b659291f3c91d3a3d550382c1c94588622，直接NEEDED无ZG/AIU、无RPATH/RUNPATH；板端ldd/注册前向和数值仍未验收。用户可按CPU-ADAPTER-COMMANDS.md C进入既有批准的一次300秒受限Host测试，原Gather保留、无完整Session/Device::Open/NPU/DMA/HDMI；完整回传核对后才判断CPU门检，不自动mixed。代理未生成包/编译/连接板端；证据evidence/cpu-adapter-r2-build-review-20261006.json。旧“r2未编译”为人工操作前历史，不能扩展为板端运行通过。

<a id="a240"></a>

## A240 · CPU r2源码/日志修正已批准并应用（2026-10-06）

来源：整理前 AGENTS.md 第240–241行。

- CPU r2源码/日志修正已批准并应用（2026-10-06）：CPU-ADAPTER-COMPILE-FIX-20261006.md，已仅将检查器三处数组修改改为Array::set(-1,dims[-1]-1)，Build-CpuAdapter.ps1在原生命令日志捕获内临时Continue/转换stderr文本，finally恢复Stop，仍非0退出停止。两文件与审阅候选逐字节一致、原文件备份/evidence和旧测试包/失败目录保留；注册内核、SDK、模型和原推理源码未改，PowerShell语法0错误。下一步按CPU-ADAPTER-COMMANDS.md A生成新身份包package/20261006-r2，再B以标签cpu-adapter-20261006-r2构建；因源码身份变化本次必须新包，不回写旧manifest或跳过哈希。代理尚未生成r2包/执行Docker/编译/算子测试，不能排除其他编译问题；先回传新包/构建结果核对，再C。应用证据evidence/cpu-adapter-compile-fix-applied-r2-20261006.json，旧“候选待批准”是审批前历史；无CPU/NPU前向验收。

<a id="a242"></a>

## A242 · CPU候选r1编译反馈（2026-10-06）

来源：整理前 AGENTS.md 第242–243行。

- CPU候选r1编译反馈（2026-10-06）：新目录cpu-adapter-20261006-r1已通过SDK身份审计、CMake配置/生成；代理只读核对导出六头文件、Host so/3.39.0版本及五份源码副本匹配。编译检查器mutate时PowerShell NativeCommandError中断stderr管道，本地log无error正文，未完成编译/链接。静态确认三处Array::get_mutable()->at用法错误：继承的get_mutable返回Object*，应使用SDK Array::set；不能排除其他编译问题。已准备CPU-ADAPTER-COMPILE-FIX-20261006.md和两文件候选补丁，拟仅修三处测试API及完整日志捕获、保留非0退出门禁，再人工生成新身份包/标签20261006-r2构建。候选语法0错误但未批准/应用/重编译；现有源码、包、r1目录与日志保留，不直接进入Lite。证据evidence/cpu-adapter-compile-failure-r1-20261006.json；无算子/NPU/数值验收。旧“修正版未编译”是执行前状态，当前编译尝试仍未通过。

<a id="a244"></a>

## A244 · CPU构建审计修正已批准并应用（2026-10-06）

来源：整理前 AGENTS.md 第244–245行。

- CPU构建审计修正已批准并应用（2026-10-06）：CPU-ADAPTER-BUILD-FIX-20261006.md，生效Build-CpuAdapter.ps1已与审阅候选逐字节一致；仅用容器dpkg-query及Docker cp -L导出文件、Windows PowerShell/.NET哈希替换容器Python审计，SDK版本/六头文件/Host库身份门禁保持。原脚本备份evidence/Build-CpuAdapter.before-no-container-python-20261006.ps1，旧失败目录/测试包/manifest未改；构建记录新增实际脚本哈希。PowerShell语法0错误，未执行Docker/编译/板端测试。下一步直接按CPU-ADAPTER-COMMANDS.md B，复用实际包.local/pose-v1-cpu-adapter/package/20261005，显式新标签cpu-adapter-20261006-r1；不重做A，不覆盖旧目录。回传build.log/sdk-audit.json/build-result.json经核对后再C。CPU/NPU前向仍未通过；下述“修正待批准/生效脚本未改”为批准前历史，不能将应用修正当作构建通过。证据evidence/cpu-adapter-build-fix-applied-20261006.json。

<a id="a246"></a>

## A246 · CPU候选构建反馈（2026-10-06）

来源：整理前 AGENTS.md 第246–247行。

- CPU候选构建反馈（2026-10-06）：已生成107用例测试包，实际路径.local/pose-v1-cpu-adapter/package/20261005；代理只读核对282项哈希、18正常/89拒绝用例、22份参考输出及5份源码/构建副本匹配。构建在SDK身份核验的docker exec FPAI python3步骤退出127，当前容器PATH找不到python3，尚未进入CMake/C++编译，没有CPU运行/NPU验收。原失败目录完整保留；候选CPU-ADAPTER-BUILD-FIX-20261006.md拟以Docker导出文件及Windows PowerShell/.NET哈希取代容器Python，保留全部SDK门禁、不安装依赖。候选脚本/补丁已准备、语法0错误，生效Build-CpuAdapter.ps1未改，未操作Docker/SSH/编译或测试。应用修正及新标签cpu-adapter-20261006-r1构建待批准；不重做/回写现有测试包或覆盖旧证据。下述“尚未生成”为交付时历史状态，候选算子前向仍未通过。

<a id="a248"></a>

## A248 · CPU算子最小适配源码交付（2026-10-05）

来源：整理前 AGENTS.md 第248–249行。

- CPU算子最小适配源码交付（2026-10-05）：CPU注册与最小适配方案，已新增隔离的host_cpu_adapter模块、独立检查器及tools/pose-v1/CPU-ADAPTER-COMMANDS.md。仅应用侧显式注册TopK/GatherElements/ScatterND，禁止覆盖既有条目，Gather保持原实现；限定当前ZG图的FP32规格、Host内存与全有效分布，仅清除临时内核描述的冗余分布。设计107用例/22份正常输出，尚未生成测试包、编译或运行，不能称为注册/数值通过。Python AST及PowerShell语法检查通过，板端shell为LF；原推理检查器/CMake及固定模型哈希保持。人工操作准备、交叉编译、传输和Lite CPU测试，代理审查日志；先A/B构建核验，再C实板测试，失败保存证据停止，不自动改SDK/模型/缓冲区策略。未接入正式推理器、不补CPU Matmul、无Session/Device::Open/NPU/DMA/HDMI；全CPU参考及完整mixed门检仍待解决，后续接入方案另行讨论。入口CPU-ADAPTER.md、REFERENCES.md 18.6及evidence/cpu-adapter-source-delivery-20261005.json。此前“新增算子方案未批准”为历史阶段状态，不扩展本次批准范围。

<a id="a250"></a>

## A250 · 独立CPU注册探针验收（2026-10-05）

来源：整理前 AGENTS.md 第250–251行。

- 独立CPU注册探针验收（2026-10-05）：HOST-REGISTRY-PROBE-PLAN.md，代理按特殊问题权限完成FPAI GCC9.4/CMake3.24.2、ARM Icraft3.39.0交叉编译和Lite一次30秒受限注册查询。探针退出码0、stderr空、5项回传哈希通过；optimized op1 Matmul无init/forward注册；ZG六个Host计算节点中188/437 TopK、192 GatherElements、582/649 ScatterND也无注册，只有442 Gather有注册。全CPU参考及混合图PS部分均存在当前注册阻断，停止mixed，不把注册查询完成当成前向/NPU/数值验收。结果tools/pose-v1/HOST-REGISTRY-RESULTS-20261005.md及evidence/host-registry-20261005/review.json；探针SHA256 4106daf64086e478b7540788eab52d4551680cb11f8b8b104a4f582d86d6d05c。原核心源码/推理二进制/模型/SDK未改，无Session/Device::Open/RAW/算子前向。后续官方注册机制核对可读资料；加载插件、改链接/SDK/模型或新增算子实现等方案及执行须先讨论批准，不自动修复或重试。

<a id="a252"></a>

## A252 · Host库只读审计完成（2026-10-05）

来源：整理前 AGENTS.md 第252–253行。

- Host库只读审计完成（2026-10-05）：新增特殊问题代理直接工具协助权限并批准审计，代理SSH确认Icraft/CustomOp均arm64 3.39.0，dpkg -V icraft:arm64无差异、退出码0；Host库SHA256 d0fbf6c81e5b57b4a908f11aad27571b8f2e68a3ede7ba33c9a4f783ba266130与原始onchip包一致，CMake导出含CudaDefault，readelf可用。完整日志tools/pose-v1/evidence/board-host-library-audit-20261005.stdout.log及同前缀记录，原包静态审查original-arm-host-package-review-20261005.json。未执行模型/设备初始化或修复，不能据库完整性认定Matmul支持；独立CPU注册探针HOST-REGISTRY-PROBE-PLAN.md为未批准候选，编译/运行及后续修复仍先讨论。口令仅用于SSH认证，不写项目文件/日志。

<a id="a254"></a>

## A254 · Lite Host绑定失败已定位（2026-10-05）

来源：整理前 AGENTS.md 第254–255行。

- Lite Host绑定失败已定位（2026-10-05）：日志显示Session::Create<HostBackend>/bindToBackendsByOrder在op_id=1 MatmulNode绑定检查失败；mode=host/device_init_allowed=false，输入已验证、lazyLoadParamsFromFile返回后failed_stop_no_retry，尚未执行样本前向。内核尾部未见本次OOM、available 687 MiB；不能凭此宣布ARM平台全面不支持或NPU混合路线失败。深层原因待实际库身份/依赖/注册审查；本机文档CPU支持不等于板端支持，安装CustomOp也不能直接证明标准Matmul注册。保持暂停重跑/模型或SDK修改/mixed，下一步只读审计候选待批准。审查tools/pose-v1/HOST-BINDING-REVIEW-20261005.md，截图evidence/lite-host-binding-failure-20261005-1.png至-3.png；软件仍人工操作。

<a id="a256"></a>

## A256 · Lite Host执行未通过（2026-10-05，更新下述尚未运行状态）

来源：整理前 AGENTS.md 第256–257行。

- Lite Host执行未通过（2026-10-05，更新下述尚未运行状态）：人工操作一次已批准的300秒Host参考后截图退出码1；具体失败阶段和原因待stdout/stderr、stages/run-config/failure及内核日志复核，不能凭退出码判断OOM、算子缺失或模型问题。证据tools/pose-v1/evidence/lite-host-exit1-20261005.png。暂停重跑、覆盖输出、数值比较及mixed；只人工保存/读取本次诊断，代理分析。任何修复/新路线先讨论批准，不自动改模型、依赖、Swap或SDK配置。未验收Host数值/NPU/双路，ORT解析/安装仍未批准。

<a id="a258"></a>

## A258 · Lite Host资源前检复核（2026-10-05）

来源：整理前 AGENTS.md 第258–259行。

- Lite Host资源前检复核（2026-10-05）：截图显示总内存993 MiB、available 744 MiB、Swap 0，/tmp所在根文件系统剩余47G；可见进程未见明显其他推理/视频应用，host-reference-20261005前缀无旧文件。可人工继续已批准的一次300秒Host参考，峰值内存/ARM算子/耗时仍未知；超时、OOM或算子异常即停止，不自动重试、加Swap或改线程/模型。Host尚未执行，不记为参考数值或NPU通过；ORT解析/安装仍未批准。证据tools/pose-v1/evidence/lite-host-resource-query-20261005-1.png及-2.png，命令LITE-HOST-COMMANDS.md第2步。

<a id="a260"></a>

## A260 · Lite Host参考路线已批准（2026-10-05）

来源：整理前 AGENTS.md 第260–261行。

- Lite Host参考路线已批准（2026-10-05）：先用Lite Host作参考，本阶段F2改为Lite ARM，复用已校验二进制d1006f9b…c05e5及optimized图/三份固定参考张量，不新增依赖/编译或调用Device::Open；先查询资源并交回，再按批准的300秒Host运行范围执行、回传完整输出/Host回调及哈希。命令`tools/pose-v1/LITE-HOST-COMMANDS.md`，范围REFERENCE-NEXT-PLAN.md。Host尚未运行，ARM支持/内存/耗时及数值待验证，不是全CPU部署降级或NPU通过；ONNX Runtime解析/安装本轮未获批准，仍暂停，mixed须参考数值有效后推进。原Windows Host方案因SDK未识别保留，不自动修复。代理只编写/审查及记录，软件命令人工执行。

<a id="a262"></a>

## A262 · Windows Host SDK未识别（2026-10-05，更新下述窗口待查询）

来源：整理前 AGENTS.md 第262–263行。

- Windows Host SDK未识别（2026-10-05，更新下述窗口待查询）：回原开发CMD后cl/x64/VSINSTALLDIR及CMake3.31.6-msvc6均确认可用；WindowsSdkDir未设置、WindowsSDKVersion仅反斜杠，有效SDK未识别。代理只读检查4个厂商Windows v10.0登记入口与5个常见目录均未找到，不能排除其他未登记目录；F2不构建、不手填INCLUDE/LIB/安装/修复。证据`tools/pose-v1/evidence/windows-host-sdk-query-20261005.png`。已准备`REFERENCE-NEXT-PLAN.md`讨论B复用已编译Lite host模式作为数值参考、A后续完善Windows SDK；另独立Conda CPU ORT1.23.2仅dry-run依赖预览，两项未批准/执行。CPU参考不是部署降级，不改变正式NPU/双路要求，输出误差仍须讨论；不因现有host模式可用静态结论就自行执行或跳过参考进入mixed。

<a id="a264"></a>

## A264 · Windows Host查询窗口已澄清（2026-10-05）

来源：整理前 AGENTS.md 第264–265行。

- Windows Host查询窗口已澄清（2026-10-05）：自动定位路径后已显示VS开发终端横幅，另一截图where cl未找到、架构/SDK变量未设置；随后明确查询是在另开的CMD执行，其未继承原开发终端环境，不据此认定原窗口初始化失败/SDK缺失/安装损坏。代理只读确认start/parse/winsdk/vcvars脚本存在，横幅v17.0为vswhere缺失时的默认值，不作版本或编译验收。现在人工回原初始化窗口查询，原窗口环境及SDK仍待验证；暂停F2及依赖它的mixed，不自动补PATH/安装/修复。证据`tools/pose-v1/evidence/windows-host-banner-20261005.png`及`windows-host-unset-query-20261005.png`，命令说明WINDOWS-HOST-ENV-CHECK.md。

<a id="a266"></a>

## A266 · Windows Host工具文件已定位（2026-10-05）

来源：整理前 AGENTS.md 第266–267行。

- Windows Host工具文件已定位（2026-10-05）：不确定C++工具安装情况，代理只读找到`D:\Visual Studio\ Visual Studio 2022\Community`，第二层目录名开头有一个空格；含MSVC14.44.35207的Hostx64/x64 cl/link/nmake、C++头文件与库、VsDevCmd.bat及CMake文件元数据3.31.6-msvc6。不再把普通PATH查不到解释为机器没有工具；这不是实际启动、SDK完整、CMake VS实例发现或编译通过。默认vswhere及常见Windows Kits注册表入口未找到/未返回记录，不自动修复/重装。查询命令`tools/pose-v1/WINDOWS-HOST-ENV-CHECK.md`，证据`evidence/windows-host-tool-discovery-20261005.json`；仅临时进入x64开发CMD及查询环境，错误先提交，不编译/安装/切换生成器或运行模型。ORT缺失保持，F1/F2参考及mixed尚未执行。

<a id="a268"></a>

## A268 · E初始化探测复核通过（2026-10-05，更新下述日志待复核）

来源：整理前 AGENTS.md 第268–269行。

- E初始化探测复核通过（2026-10-05，更新下述日志待复核）：现场提供完整probe产物及日志截图，阶段started→opening_device_not_readonly→probe_complete_requires_review，mode=probe/device_init_allowed=true，无failure.json，stderr为空；stdout报告Device initialization successful，AXI zg330aiu/NPU=0x40000000/DMA=0x80000000，device=25122301、icore=FMSHZGV3TECH-AID - 24160628。结合退出码0，E仅Open/version初始化探测通过；提供的dmesg尾部未见探测相关总线/DMA错误，启动时EXT4恢复、journal异常关闭/更换及其他启动提示保留，不归因于probe，不自动修复或改时间。未执行模型、六Host算子/NPU计算或数值/性能验收；compatibility_passed=false固定待验收标记保持。证据`tools/pose-v1/evidence/board-probe-review-20261005-1.png`至`-3.png`。下一步准备F1/F2参考，ORT缺失与Windows Host编译工具待确认；参考有效前不进入mixed，不自动安装依赖或转为全CPU部署。

<a id="a270"></a>

## A270 · E探测执行反馈（2026-10-05，更新下述未执行状态）

来源：整理前 AGENTS.md 第270–271行。

- E探测执行反馈（2026-10-05，更新下述未执行状态）：实际执行固定30秒timeout的probe，退出码0，device-version.json的device=25122301，与基线一致；icore已显示、待文本日志复核，已保存probe.dmesg.log但内容未提交。compatibility_passed=false是检查器固定输出的待验收标记，不是SDK兼容性失败结论。stdout/stderr、stages/run-config及内核日志仍待复核，E尚未完整验收；不重跑probe或覆盖证据，不进入mixed。此结果证明本次Device::Open/version返回，不能扩大为DMA/NPU计算、完整模型、HDMI或RTSP通过。证据`tools/pose-v1/evidence/board-probe-exit0-20261005.png`；软件操作人工执行，代理未连接SSH或初始化设备。

<a id="a272"></a>

## A272 · E前置查询反馈（2026-10-05）

来源：整理前 AGENTS.md 第272–273行。

- E前置查询反馈（2026-10-05）：截图确认/usr/bin/timeout为GNU coreutils 8.30，probe及三份对应日志均不存在；可见进程列表未见明显AI/HDMI/编码应用，方括号kbase/mvx等内核线程不能据名称认定为故障或演示占用。截图不独立证明当前位流未改变或所有访问方均空闲；仍需人工确认上次0x25122301核验后未替换BOOT/通过JTAG加载其他位流、无其他演示使用设备，再进入既定E。未执行probe，不自动停止进程、重启或初始化。证据`tools/pose-v1/evidence/board-probe-preflight-20261005-1.png`及`-2.png`。

<a id="a274"></a>

## A274 · D阶段离线接口验收（2026-10-05，更新下述产物待复核）

来源：整理前 AGENTS.md 第274–275行。

- D阶段离线接口验收（2026-10-05，更新下述产物待复核）：现场提供inspect-zg产物截图，输入[1,180,60]、分数[1,100]、姿态[1,100,14,3]及顺序符合检查器float32门禁，阶段started→offline_inspection_complete，mode=inspect/device_init_allowed=false，stderr为空且目录无failure.json。结合前述11项校验和退出码0，D阶段通过；未加载RAW参数、执行推理或调用Device::Open。证据`tools/pose-v1/evidence/board-inspect-artifacts-20261005.png`。E前仍须确认GNU timeout可用、无AI/显示并发占用且BOOT未再改变，人工操作软件命令；不因离线通过认定NPU兼容或双路显示通过，不自行终止进程、复位设备或重跑覆盖已有目录。

<a id="a276"></a>

## A276 · 板端包校验更新（2026-10-05，覆盖下述CRLF阻断状态）

来源：整理前 AGENTS.md 第276–277行。

- 板端包校验更新（2026-10-05，覆盖下述CRLF阻断状态）：以`files.lf.sha256`校验11项全部OK、退出码0，板端样本/模型包完整性通过；随后运行ZG图`inspect`退出码0。截图尚未展示graph-io.json、stages.jsonl、run-config.json及stderr，离线接口验收待这些产物复核，不重跑已有inspect或覆盖目录。未进入SDK设备初始化或推理。证据`tools/pose-v1/evidence/board-checksum-inspect-exit0-20261005.png`；当前仅板端清单换行处理已人工执行，生产打包脚本的候选修正仍未应用，不把截图当作代理修改脚本的授权。

<a id="a278"></a>

## A278 · 板端校验清单CRLF阻断（2026-10-05）

来源：整理前 AGENTS.md 第278–279行。

- 板端校验清单CRLF阻断（2026-10-05）：D截图确认二进制哈希匹配、ldd列出的依赖均解析；sha256sum对11文件报尾随`\r`的No such file。代理只读确认本地files.sha256为11行CRLF，原因是inference_gate.py默认文本换行写入；不是已证明的哈希不一致或文件丢失。仅准备`tools/pose-v1/checksum-lf.candidate.patch`及`CRLF-CHECKSUM-FIX.md`，生产脚本和现有包未改，修正待批准；保留旧清单并生成LF清单后重新校验，全部OK前不继续inspect/probe/mixed。无需因此重编译、替换模型、安装SDK或改BOOT；后续软件操作人工执行。

<a id="a280"></a>

## A280 · 独立检查器交叉编译复核（2026-10-05，更新此前未编译状态）

来源：整理前 AGENTS.md 第280–281行。

- 独立检查器交叉编译复核（2026-10-05，更新此前未编译状态）：完成三样本包及FPAI构建`inference-20261005-165059-043b0c40`，GCC9.4.0/CMake3.24.2、SDK目录`/usr/cmake`，配置/编译/链接通过；AArch64 PIE二进制SHA256 d1006f9bd78050ffa484c64bf74fb62542d270c7acca5068e9da611a5bdc05e5。代理只读核对源码记录7/7、包文件大小/哈希11/11、二进制哈希与日志匹配，未代执行构建或软件测试。现在人工执行D传输、板端库解析及inspect离线检查，交回结果后再继续；尚未确认板端加载、SDK设备初始化或推理，不安装/改库/自动进入probe。证据`tools/pose-v1/evidence/cross-build-review-20261005.json`，命令`INFERENCE-COMMANDS.md`。

<a id="a282"></a>

## A282 · 推理SDK补查确认（2026-10-05，更新先前“ZG330配置未找到”）

来源：整理前 AGENTS.md 第282–283行。

- 推理SDK补查确认（2026-10-05，更新先前“ZG330配置未找到”）：截图确认`/usr/cmake`含HostBackend/ZG330Backend配置及aarch64导出，包文件清单包含ZG330后端头文件、设备头文件、后端so与AIU库；FPAI icraft/customop均arm64 3.39.0，icraftmdzthirdparty arm64 0.1.1，状态均install ok installed。可继续已批准B固定打包、C交叉编译，SDK目录用`/usr/cmake`；不据此声明编译/运行兼容性或NPU通过，不因此前搜索缺项自动安装后端。ORT缺失、Windows工具当前PATH不可见仍待讨论；先提交构建日志复核，不自动进入设备执行。详细见`tools/pose-v1/ENVIRONMENT-QUERY-20261005.md`及新增截图证据。

<a id="a284"></a>

## A284 · 推理环境查询反馈（2026-10-05，截图）

来源：整理前 AGENTS.md 第284–285行。

- 推理环境查询反馈（2026-10-05，截图）：FPAI GCC9.4.0/CMake3.24.2/Icraft arm64 3.39.0已查询确认；SDK精确文件名搜索仅返回`/usr/cmake/icraft-hostbackend-config.cmake`，ZG330配置未找到，不等于已确诊NPU运行库缺失。独立Conda NumPy可找到、ORT未找到；Windows正确Get-Command cmake,cl无输出，只证明当前PATH不可见。原`*icraft*`查询不核验CustomOp，需补查包内容、实际后端命名及CustomOp状态；当前不执行构建/设备初始化，不自行安装或更换参考执行环境。见`tools/pose-v1/ENVIRONMENT-QUERY-20261005.md`及截图证据；后续软件命令仍人工执行。

<a id="a286"></a>

## A286 · HDMI配套资料补充（2026-10-05，人工确认）

来源：整理前 AGENTS.md 第286–287行。

- HDMI配套资料补充（2026-10-05，人工确认）：没有另行持有的Lite25122301可编辑工程或720p60说明；参考包README/构建/API及示例配置检索未找到明确归属当前位流的720p60配置步骤，不能推断全部资料不存在。手册/原理图的720p建议不等于当前位流配置方法；HDMI时钟、寄存器及工程对应仍待核对，不自行配置或改首版目标。

<a id="a288"></a>

## A288 · 独立混合推理门检准备（2026-10-05）

来源：整理前 AGENTS.md 第288–289行。

- 独立混合推理门检准备（2026-10-05）：下一阶段方向，已编写2024 epoch442三样本的独立Icraft检查器、可选SDK CMake目标、FPAI交叉编译脚本、固定样本/模型打包、ONNX参考及数值比较工具，执行入口为`tools/pose-v1/INFERENCE-COMMANDS.md`。代理本轮仅编辑源码、静态审查和读取资料，未编译/测试/运行模型、操作Docker/SSH或初始化设备；实际软件/AI操作人工执行。SDK CMake实际目录、Windows Host参考编译工具、ONNX Runtime依赖尚待查询；不自行安装。设备probe不是只读操作，probe结果需复核后再继续混合推理；六个Host算子执行与ZG330后端回调须记录，分数/坐标容限仍待实测讨论，不把退出成功或源码交付记为推理通过。HDMI静态审查发现参考RTL可写时序项，但当前25122301位流与这份工程、像素时钟及寄存器配套尚未确认，见`HDMI-STATIC-AUDIT.md`；720p60目标保持，未访问显示硬件或修改FPGA/BOOT。此前最小只读探测授权不扩大为任意硬件操作。

<a id="a290"></a>

## A290 · 首版阻断项最新状态（2026-10-04，更新早期“位流未知/预处理门检未通过”）

来源：整理前 AGENTS.md 第290–291行。

- 首版阻断项最新状态（2026-10-04，更新早期“位流未知/预处理门检未通过”）：固定9组300份真实回放与幅度atol/rtol=1e-6、相位周期最大1e-5 rad门检，原3份样本包含其中；主机及Lite与Windows参考均300/300逐位一致，实板/主机哈希一致，幅度及相位标量/周期最大差0，4类非法记录拒绝。人工±π按明确批准降为非阻断诊断，周期最大2.333111/2.693437 rad仍失败，不能标为通过；真实相位标量差>1e-5 rad仍须暂停依赖它的推理验收并讨论模型影响。原预处理、模型及ARM二进制未改。板端BOOT哈希与指定Lite 25122301单路PLIN+pHDMI包一致，仅BOOT变更，其余8文件保持旧身份；日志FSBL已下载PL、Linux启动，uEnv后续download.bit加载未确认，未修复启动配置。BOOT内载荷经32位字节序转换与同包.bit完整载荷对应，另有4字节尾随。最小只读映射，仅读取0x4000001C得到0x25122301，运行FPGA版本身份已核验；该授权不扩展为任意寄存器、SDK Open/reset/check或推理/显示。板端Icraft/CustomOp实测arm64 3.39.0，参考包标3.36.0，混合推理兼容性仍待实际门检；HDMI参考1080p60，包装器不设置720p时序，首版720p60保持，屏幕尚未连接。NPU/HDMI/VPU/RTSP/30分钟闭环未验收。最新见`tools/pose-v1/RESULTS-300.md`、`evidence/replay-300-summary.json`、`NEXT-GATE.md`及REFERENCES.md 18.4；后续初始化、模型/显示执行仍按既有审批及配套停止条件处理，不能因版本相符认定首版已完成。
