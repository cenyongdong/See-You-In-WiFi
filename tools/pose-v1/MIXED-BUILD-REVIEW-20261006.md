# mixed-r1构建与警告复核（2026-10-06）

## 工程内容总结

在FPAI完成mixed-20261006-r1构建，代理直接读取本地完整日志、源码副本、SDK导出文件及二进制。
GCC9.4.0、CMake3.24.2、ARM Icraft/CustomOp3.39.0；CMake配置/五份CPP编译/链接完成。
包290项、10份构建源码及副本、实际构建脚本身份、15份ARM头文件、Host/ZG库哈希匹配。
AArch64 ELF64 little-endian PIE二进制SHA256：
`7cf761f1dd7d1ca1bf8a1db1826e4d9b34574b1a8dc0ac662c987eed52722a17`。
直接NEEDED含Host/ZG后端，无RPATH/RUNPATH；板端实际ldd和前向尚未运行。

完整日志只有一条warning，无error/fatal error；位置mixed_check.cpp第142行：

```cpp
if(!first)report << ','; first=false; report << quote(p.first) << ':' << quote(p.second);
```

`-Wmisleading-indentation`提醒同一行后两条语句看起来也受if控制。实际C++语义只让第一条逗号输出有条件，
每个键值都无条件重置first并输出，正是JSON首项无逗号/后续项有逗号的预期。
可读性不佳，未发现这条警告所指代码存在分支逻辑错误；无需因此重编译，当前程序/包身份保持。
便于阅读的等价写法如下，仅作说明，**未应用源码修改**：

```cpp
if (!first) {
    report << ',';
}
first = false;
report << quote(p.first) << ':' << quote(p.second);
```

日志中的ELF“shared object”与FLAGS_1的PIE对应，产物是动态链接的位置无关可执行程序，不影响本次架构核验。
证据：build.acceptance.json（历史附件，当前仓库未附：`evidence/mixed-20261006-r1/build.acceptance.json`）、
完整警告审查（历史附件，当前仓库未附：`evidence/mixed-20261006-r1/build-warning-review.json`），原构建目录
`.local/pose-v1-build/mixed-20261006-r1`保持。
代理未重编译、运行程序、操作Docker/SSH或访问板端设备；本次仅构建证据验收。

## 对后续开发的参考

构建warning需结合控制流审查，不能将其自动当失败或完全忽略。日志记录的成功仍须与SDK/源码/程序哈希联合核验。
后续可将这种多语句写法拆行加括号；若修改已固定源码，必须生成新包/新构建身份，不能回写旧manifest。
本次保留原产物，继续[MIXED-VALIDATION-COMMANDS.md的B](MIXED-VALIDATION-COMMANDS.md)，
传输后先C的host-check（一次300秒、107例桥回归），完整回传核验后再离线参数阶段。
尚未验证新Host桥、SDK设备内存、Session部署、NPU前向或数值/性能，不直接启动硬件阶段。
