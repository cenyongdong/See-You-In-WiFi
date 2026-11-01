# r6离线打包薄适配

工作目录`D:/FPGACompetitionProject`；`package_ai_read_postroute.py`默认inspect，仅核冻结源码和13处精确AST转换，不启动工具。显式`icap`／`boot`／`bundle`才进入对应新目录及原有有界工具流程。

固定复用旧packager SHA bf39a9…39ac3f的完整算法，旧文件不改；仅将r5阶段／native身份、bit门字段名及冻结planner SHA换为r6。反向AST完全等于原算法，仍执行全部原BOOT／模型／SDK／数值身份及派生隔离门；没有复制另一套算法。base `__file__`保持真实，另归档actual-r6-adapter、base原字节、实际适配AST源及完整转换清单。

三个phase均先进入新planner公开纯lineage门，完整核实际r6四phase、正式报告、bit、11字段release和原厂派生隔离；再把完整优化原值链与所有源码／物理产物SHA加入阶段input-identities，结束前重核。任何实际门缺失或未通过，Procise前就停止。旧r5位流不得替代r6，后处理目录仍为read-v3-icap／read-v3-boot／controlled-startup-read-v3。

最终五adapter表及额外源码SHA闭包在`E3/postroute-r6-adapters-r1/`；planner保护共享contract、实际reviewadapter和bit release helper，并将新／旧packager源码纳local_review。固定SHA依赖闭包没有manifest自引用；批准后任何影响动作的源码变化均使既有回执失配。动态onsite状态另行每次入口读取：候选安装／启动／UART／reboot／HDMI动作在专项暂停期间拒绝，离线inspect／源码生成和已授权必要原BOOT还原不因此阻塞。

`mock-r5`55项纯mock通过、3.141秒，含AST位置／次数／逆变换、真实格式的三边界原值、额外物理命令拒绝、完整release／DRC负例及现场暂停范围；本组实际EDA／Procise／板端操作为0。新工具流程尚未实际通过，不以inspect或源码生成替代发布验收。
