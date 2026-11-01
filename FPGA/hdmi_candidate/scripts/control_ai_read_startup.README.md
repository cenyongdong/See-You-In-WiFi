# read-v3本机启动监督器

执行位置为Windows `D:/FPGACompetitionProject`，解释器沿用本机已核验的Codex Python。`control_ai_read_startup.py`默认`inspect`只做实际包审查及远程源码编译，不联机；真实manifest尚未产生时必须失败关闭。

`capture --kind candidate|fallback --approved --approval-file <实际新回执>`先核对完整本地门检、manifest、当前任务未暂停及该UART动作授权，再启动本批只收串口进程。子进程在打开前再次核对批准回执SHA、manifest、暂停状态和实际COM7 USB身份；115200/8N1、DTR/RTS关闭、0 TX，300秒／4MiB，读取超时250ms。ready以临时文件原子发布。主机保存初始PID、实际创建时间、进程镜像、完整源码及stdout/stderr；任何启动或ready错误都保存原错、请求自有reader停止并有界观察，不触碰其它端口或进程。

`reboot --kind candidate|fallback --approved --approval-file <同一实际回执>`重新核对相应动作授权及仍存活的同一UART PID／创建时间／镜像，然后保留本机独占尝试目录。远程源码复用`prepare_remote_read_v3.py`的受审查guard定义，验证本次实际包、远端暂停状态、完整安装／恢复记录及启动文件／SDK／owner，先保存远端独占尝试和请求文件，再发送唯一一次reboot。不因SSH断开、超时或未知状态重复命令。

恢复观察总预算180秒，包含首次命令及每次只读连接；每轮连接预算受剩余时间约束。尚活的运输进程必须先监督，不启动另一连接。所有输出保存在新目录，以唯一tag行识别业务JSON，不能把SSH退出码当启动或推理通过。成功要求实际boot_id改变；只证明SSH恢复，不证明新PL逻辑、DMA或推理正确。

正式`transport`薄入口导入本包W3 `execute_read_v3.py`的`transport_bounded`，保留原内层预算及外层`timeout+10`。冻结UTF8源码通过普通文件stdin交给固定小argv OpenSSH，独立askpass沿用主机密钥pin与内存认证；stdout／stderr分别保存，超时保留自有PID和still-running事实，不kill、不重连。导入模块不联机；executor不反向导入监督器。该执行器为manifest绑定的第五adapter，必须与其余四份源码一起核对实际SHA。

候选成功返回后，主执行器通过W3 `execute_read_v3.py publish --kind candidate-startup`，核对本机`candidate-startup-read-v3/result.json`的真实来源、包／boot_id／SHA／实际transport后，在同一动作授权下上传到本包板端`metadata/candidate-startup.json`。这只是实际启动证据发布，不得伪造或拿旧记录替代。随后首先用该执行器的`stage --stage postboot-restore`执行已生成且重新门检的源，远端入口带`--approved`，完整恢复原BOOT并读回；此证据缺失时，远端`candidate_identity`／`restored_identity`会拒绝SDK阶段。

可选回退也先由主执行器执行已门检的只读`fallback-preflight`，核对返回的当前包／boot_id／原BOOT和失败证据，再将这份真实返回值上传为`metadata/fallback-preflight.json`；原BOOT回退控制器会再次独立审查。上传前必须调用当前包相应批准门，不把工具传输成功当业务审查通过。

观察到新启动后会请求UART停止，并在5秒内核对reader关闭记录与原PID退出。无法确认时只记资源未证实回收，不发送kill或声称清理完成；主执行器须继续监督这一已知进程后才能交付。接收器关闭或驱动故障仍可能需要原进程观察，真实Windows串口行为不能由mock代替。

当前本机离线验证入口为`tools/pose-v1/evidence/hdmi-live-20261017-r3/startup-supervisor-mock-r2/`，对应实际控制器SHA `8d2016d96cacddcdc16823519bff9b21ae00d883fe8d921193558a13914b25d4`、executor SHA `08e64fbeb4a21e5fe0f26629cdb098857b263961ae738c5ed6f94549033d26c3`；原28项与新增薄入口delegation共29项纯mock通过，实际25.203秒、合成180秒场景172秒。动态导入及全部进程／认证／网络边界均替换为mock。旧`startup-supervisor-mock-r1/`与其28项原源码证据保持。mock不证明Windows串口、Linux FAT写入、实际SSH重启或新候选板测通过。旧r2两个重启额度已耗尽，本监督器的存在不构成新许可，旧DATA保持暂停。
