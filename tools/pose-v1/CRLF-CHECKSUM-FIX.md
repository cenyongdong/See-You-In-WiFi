# 校验清单CRLF问题诊断与最小修正方案（2026-10-05，待批准）

最新执行反馈：已在Lite生成`files.lf.sha256`并用它校验11项，全部OK、退出码0。
板端包完整性通过；ZG图inspect退出码0，后续产物内容已复核，D离线检查通过。
产物证据`evidence/board-inspect-artifacts-20261005.png`（历史附件，当前仓库未附）。
证据`evidence/board-checksum-inspect-exit0-20261005.png`（历史附件，当前仓库未附）。
生产脚本候选修正仍待明确批准、尚未应用。下面“尚未执行”为方案交付时的历史状态；
当前不要重生成新清单或重跑已有inspect。

## 已确认的问题

在Lite执行`sha256sum -c files.sha256`，所有文件名末尾显示`$'\r'`并报No such file。
代理只读检查本地同一清单，1043字节、11个LF，其中11个均为CRLF。
`inference_gate.py`第93行使用Path.write_text默认文本换行，Windows把字符串中的LF写成CRLF。
Linux sha256sum此次把CR保留在文件名中，因此实际尝试的是`inputs/S11_01_308.csi\r`，而非真实文件名。

这是代理打包脚本的换行处理遗漏。当前不是哈希比较不一致的证据，也不能由此确认文件丢失；
重新用LF清单校验之前，板端11文件完整性仍未通过。
二进制哈希在截图中与本次构建匹配；ldd已列出的依赖均解析成功，无not found。
ldd不覆盖运行时动态加载、SDK初始化或推理兼容性；inspect/probe/mixed尚未验收。

## 拟修正范围

1. 代理仅把脚本这处清单写入改为ASCII字节写入，明确保留LF。
   候选补丁为[checksum-lf.candidate.patch](checksum-lf.candidate.patch)，当前未应用。
2. 当前已传板的包无需重打包、重编译或替换模型。在板端保留旧`files.sha256`，
   生成`files.lf.sha256`，只删除CR字符并重新验证同11个文件。
3. 11项全部OK且退出码0后才继续原D的inspect；任何文件仍缺失或哈希不符则停止并反馈。
   不安装依赖，不改SDK/BOOT/寄存器，不运行设备probe或推理。

## 获同意后人工执行的具体命令

位置：Lite的MobaXterm SSH终端；目录是本次已传输的样本包。

```bash
cd /tmp/pose-v1-inference-20261005/package
test ! -e files.lf.sha256
echo $?
```

先确认退出码0，即新清单尚不存在；否则停止，保留历史文件，不覆盖。
接着逐条执行：

```bash
tr -d '\r' < files.sha256 > files.lf.sha256
sha256sum -c files.lf.sha256
echo $?
```

`tr`只读取旧清单并生成新清单，输入/模型/原始清单不修改。
预期11项均OK、sha256sum退出码0；tr报错或校验异常时停止，不继续inspect。
本方案尚未执行，获批准后代理修脚本、人工操作板端命令并提供日志。
