# 正式融合追溯r3构建验收

完成FPAI GCC9.4.0/CMake3.24.2、ARM Icraft/CustomOp3.39.0配置、五CPP编译及链接，代理仅读取本机产物。
291项包、17份来源身份、11份构建文件及副本、15ARM头文件/Host＋ZG库身份通过。
新融合基线头与批准源码匹配，创建/部署追溯校验的实际SDK调用已通过ARM编译，运行行为仍待板测。

程序555,800字节，SHA256 e8d66113ad3d9a34f9f210e5f7038560bc3dbfa681b9a057d748ff39e6c696a8。
AArch64 ELF64 little-endian PIE，直接Host/ZG依赖，无RPATH/RUNPATH。
仅mixed_check.cpp143行原版本JSON输出-Wmisleading-indentation警告；if控制逗号、后两语句无条件执行符合原意，
因新增include从142移至143，逻辑未变。无error，不需为该警告重编译。

[构建门禁](evidence/mixed-20261006-fusion-r3/build.acceptance.json)、
[独立构建审查](evidence/mixed-20261006-fusion-r3/build-review.json)已生成。
本次仅构建身份验收，无新Host/设备/Session/前向执行，不能称正式apply或混合推理通过。
下一步仅[MIXED-FUSION-R3-COMMANDS.md B/C](MIXED-FUSION-R3-COMMANDS.md)：新r3目录传输后Host107回归并完整回传，
核验后才提供离线/内存/一次apply命令；旧r1/r2不重跑或复用门禁。
