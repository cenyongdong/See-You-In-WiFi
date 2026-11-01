# r24：HP2复位协调实现与单次实板结果（包已关闭）

当前：r24已完成候选启动、正确SW6对照、一次条件Open及原BOOT回退，各1次；包关闭、额度0。当前原BOOT运行，设备无占用。旧DATA独立暂停，HDMI长期未批准；结果与证据见末节。

改动依据与边界：r23正确SW6清零CSR，但GP可观测期间未见HP2侧PL互联复位，完全无SDK时已有异常返回；[原值、停钟对照及限制](../hdmi-boot-witness-20261019-r23/PLAN.md)。r24只把原`proc_sys_reset_1.dcm_locked=1`改为`ddr3_init_done & ~ddr_ui_rst`，让时钟恢复阶段仍有复位条件。原IP、复位极性和四个共享ARESETN连接保留；没有改模型、SDK、频率、协议、NPU分配或新增豁免。**该修改不等于PS内部FIFO复位；板上停钟因果及故障是否消失仍待实测，D45未关闭。**

实际验证：原生成复位IP的启动就绪、运行时钟、停钟漏采、就绪门恢复与保持输入对照均通过，[仿真](reset-sim/result.json)。完整布线WNS +0.030ns、WHS +0.010ns，TNS／THS为0；新增就绪路径5ns、最差+0.585ns，374位保持总线10ns、五个GP首级5ns均有效，bus skew违例和内部未约束端点均0。仍有且只有原两处AI Min Period例外，raw_timing_pass=false；默认DRC仍有原rx_sdi REQP-52／56，正式write_bitstream仅按既定四项GT处理后为0错误／58警告／32建议。[完整门检](qualification.json)。上述为离线门检；有限板测见末节，不扩为整机验收。

BOOT `a0ed66d07ba05d80c3d0188d93afda1036a9c7df212ce9badb74b229c61e3e49`，7,023,552字节；非PL全部字节与原BOOT相同，PL载荷换序匹配且填充不变。[实际文件及唯一身份](package-review.json)。实际综合使用BD的`synth/ps_ai.v`，不是未编译的独立导出文件；三处修改及原生成HDL备份见[source-overlay.json](source-overlay.json)。重新生成BD可能覆盖手工HDL，重建须使用仓库`prepare_hp2_ready_candidate.py`。复用原r23布线DCP及24个OOC IP，没有升级IP。

本包已批准并执行的范围（现已关闭）：

1. 临时安装r24并启动最多1次；SSH恢复后先恢复原BOOT文件并完整读回核验，再接触CSR。
2. 无SDK采启动基线／历史；仅健康空闲或既有无握手返回故障可进入一次正确PL_KEY1／SW6／F8对照。实际松开后先存五寄存器初始值，归零才采按后窗口及历史，按住期间不访问CSR。
3. 两次纯CSR均健康、GP／HP2实际断言与宽度及历史保持均通过、无未解释的ready路径先返回后请求，才允许一次库加载／Device::Open分段。一个物理按键可能产生多个内部边沿，因此要求两域计数增加且脉宽为正，不要求恰好一个边沿。异常停止，不重试。
4. 最后或异常后最多1次原BOOT回退，核验原运行、启动／SDK身份与无占用后关闭额度。本包不含DMA、推理、HDMI START或长期验证，也不修FAT。

执行前已放置`/root/hdmi-hp2-ready-20261020-r24`的未启用文件及候选载荷；[传输校验](stage-inert-verification.log)确认候选SHA匹配、inactive、同一原运行身份及无占用。SDK／启动保护只读审计见[r24前置审计](../hdmi-boot-witness-20261019-r23/r24-preflight-audit-20261020.log)。[配置](deploy/config.json)、[未启用授权](deploy/authorization.json)及[执行入口](deploy/reset_key_board.py)。该准备记录不代表执行授权；本包后来当前已关闭，不能复活额度。

本轮工具耗时（原生进程实际返回）：综合188.985s；增量实现1172.500s（约19分33秒），是已记录串行工具阶段最高项，占约73.4%；最终物理复核102.531s；实际bit 128.797s；Procise后处理4.234s、BOOT封装0.531s。离线配置开始至BOOT完成墙钟约27.52分钟，不含此前r23实板对照及后续文件准备；仿真与实现重叠，不叠加计算墙钟。复用匹配率99.99%单元／99.81%网络并不消除原生全局优化、数据库加载和自动报告耗时。本轮没有多代理审查或重建24个IP；后续可把必要的早期连接检查放在即将退出的综合进程中，避免路由父进程保留已打开设计的内存。原始配置失败日志保留，昂贵阶段未因包装器重跑。

## r24实板结果（2026-10-20，包已关闭）

候选运行ID为`bfa7b3c7-74dd-490c-b32b-02503ca9d26f`。SSH恢复后先恢复并完整读回原BOOT，才访问CSR；原始记录集中在[evidence-r24-20261020.tar](evidence-r24-20261020.tar)。

- 无SDK启动基线：五寄存器初始ABI/count/status/request/response为0x41495201／104／0／0／0，0→2窗口健康。首次可观测source时钟起PS／HDMI AR、R累计均0，未见RVALID；HP2侧PL互联启动复位断言1次、低电平5,618,047个GP周期。见[启动解码](baseline-decoded.json)。
- 人工确认一次正确SW6并松开后，初始五寄存器再次归零；按后纯CSR健康。GP复位断言增加16、HP2复位断言增加1，HP2低电平增加5,817,068个GP周期（100MHz下约58.17068ms）。16是内部边沿数，不能等同16次人手操作；历史跨本地复位保持，累计AR／R仍全0，无溢出和未解释返回。见[按后解码](post-reset-decoded.json)。
- 两次冻结之间，按实际约束的GP 100MHz／source 200MHz换算，GP计时59.74525898s、source计时57.41839992s，相差2.32685906s；GP复位累计高电平2.32696214s。该计数比较与HP时钟在按键复位期间中断相符，配合原IP仿真支持停钟漏采机制；计数冻结切点有域间偏差，不当作外部波形，也不等于PS内部FIFO复位证明。
- 条件门通过后，实际库加载前4／库加载6／Device::Open8／Open后空闲10／Close与卸载12五窗口均健康；实际Open恰好1次、退出0、owner为空。最后启动历史仍无AR／R及RVALID。见[软件分段](software-phase-summary.json)、[最终历史](software-history-decoded.json)。本包没有DMA、推理、HDMI START或长期验证。
- 已使用批准的一次原BOOT回退；原运行ID为`1ad69497-8ebe-4b8f-9004-780866f64fcd`，SDK／九启动文件一致、FPGA operating、无占用。[最终审计](final-audit.json)、[关闭授权](deploy/authorization.json)。

本轮证明新候选能建立启动和SW6后的实际HP2互联复位，并完成按键后的单次Open；只有一次候选启动样本，且Open在SW6之后，不能据此关闭D45或宣称无按键跨启动稳定。后续[复用同一BOOT的r25](../hdmi-startup-stability-20261020-r25/PLAN.md)已获批准并执行，其无按键首例故障与本包有限通过分别认定。

耗时：授权记录至原BOOT回退关闭回执约5分20秒，含现场按键等待和代理操作间隔，不是完整互斥分解。已记录原子步骤中，候选BOOT写入／完整校验约8.1秒、还原约4.8秒（约1秒计时分辨率，不含前置audit）；库加载／Open／Close整段0.291秒，不能当纯Open耗时。[统计口径与原值](board-timing-summary.json)。未重编位流或增加多代理审查。
