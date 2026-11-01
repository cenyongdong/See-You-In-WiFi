# 绑定快照r2构建验收（2026-10-06）

## 工程内容总结

完成FPAI mixed-20261006-binding-r2，GCC9.4.0/CMake3.24.2、ARM Icraft/CustomOp3.39.0。
配置、五份CPP编译和链接完成；代理读取完整日志、实际源码/SDK导出文件及程序后独立核验。
包290项、10份构建源码及副本、15ARM头文件、Host/ZG库、实际构建脚本和manifest身份匹配。
快照源码与批准候选逐字节一致；SDK公开视图/forward_info/merge_from等字段已通过ARM编译，运行内容仍未知。

AArch64 ELF64 little-endian PIE程序518,712字节，SHA256
`94a03a903a4a97f229b1549dcbd1bade193d60dbb23753c1f030431fbd061248`。
直接NEEDED含Host/ZG后端、无RPATH/RUNPATH；未实板ldd、运行新Host或创建Session。
完整日志无error/fatal error，唯一-Wmisleading-indentation为此前r1已审查的142行JSON逗号多语句写法，控制流符合预期。
不需要因该warning重编译或更改已固定源码。

证据：[build.acceptance.json](evidence/mixed-20261006-binding-r2/build.acceptance.json)、
[完整构建审查](evidence/mixed-20261006-binding-r2/build-review.json)，原目录.local/pose-v1-build/mixed-20261006-binding-r2。
代理仅本地文件分析，未运行Docker构建/程序/板端设备，旧r1证据保持。

## 对后续开发的参考

新程序身份已经确定，快照字段可编译不代表能覆盖1173原HardOp或解释8622缺绑定。
按[MIXED-BINDING-R2-COMMANDS.md B/C](MIXED-BINDING-R2-COMMANDS.md)使用新20261006-binding-r2工作目录，
先Host107例完整回传，核验后离线及内存，再一次300秒apply取证，不做forward。
旧r1门禁文件不能用于新程序。不要绕过已有目录检查、删除旧失败目录、复位或重跑采样。
