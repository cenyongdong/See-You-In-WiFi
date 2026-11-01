# r48：原生 RGB565 接入后的首次长测尝试

2026-10-24。已保留既有有限消费位流、AI四路连接和30Hz/52800窗的原系统链路，接入r47直接RGB565渲染。未重建FPGA，模型、SDK、数学、NPU分配、帧协议及200ms采纳期限保持。扩大显示视口，骨架与关节标注保持原显示比例。渲染CPU性能与源码说明见[r47实测](../hdmi-render-speed-20261024-r47/RESULTS.md)。

## 实际结果

本轮未完成长测。唯一候选启动为健康启动：启动时PS AR=0、R=0，消费0拍；原生160位状态仅有READY建议项92/93/95，无强制协议错误。启动准入通过后，先恢复原BOOT文件，再打开唯一一次SDK负载。

PC端HOST_READY后，实际CSI连接触发Node启动Python节拍器时出现`spawn EPERM`，首帧未发送。板端随后保存`Truncated/idle CSI connection`，原生exit=1；送入/返回/新推理完成帧均0，HDMI START和采纳帧均0。SDK Open及内存申请阶段已经执行，不能把本次记为SDK 0次。运行监测共5次完整原生协议快照，无新增错误；STOP证明和双帧缓冲释放完成，内核日志未变化，SDK/运行身份保持，没有资源危险。父控制器32.662秒结束，其中SDK守护进程约28.608秒。这不构成推理数值、实际显示、消费后恢复或长期稳定性通过。

主机纯CPU对照已定位Node创建子进程管道的沙箱权限问题：同一个Node、Python、原pacer.py与相同pipe选项，沙箱内同步EPERM、退出2且未创建子进程；沙箱外退出0，约408ms完整产生0..5六个节拍、stderr为空且子进程关闭。不能归因为Python版本不兼容。证据见[host-preflight/sandbox.result.json](host-preflight/sandbox.result.json)及[host-preflight/unsandboxed.result.json](host-preflight/unsandboxed.result.json)。

修正已用CPU对照验证，不修改原run.mjs、pacer或帧协议。后续若新增板测，先在沙箱外启动实际主机控制器，并在相同上下文通过真实节拍器预检，再允许写BOOT/启动板端及SDK。HOST_READY本身此前未覆盖节拍器创建。新一轮拟保持同一位流、同一r47软件包、30Hz/52800窗和2100秒硬上限，最多1次候选启动+1次SDK+1次原BOOT回退，任何功能错误即停，不使用已关闭r48余额。

## 恢复与原始数据

实际使用1次候选启动、1次SDK、1次原BOOT回退，包关闭、余额均0，无自动重试。原运行身份为`84eee0be-b1f1-446c-8fa1-85224c0b6cd5`；原BOOT SHA256为`ff350477e624c50d2f8180fb4b9130ec7688fbc7ca553412ed7c3dd2a68b31ef`。9项启动文件、6项SDK及FPGA operating核验通过。主机服务、反向转发及两个UART采集器均结束，串口主机TX=0。

完整板端候选现场保存在[candidate-evidence.tar.gz](candidate-evidence.tar.gz)，8102392字节，SHA256=`7fcf2a8a68c9067d18ba698209392a9145307c7ec59f7981cd60889683d8e695`；其中保留启动原始采样、全部协议快照、SDK原生失败、资源记录及STOP/释放事件。主机原始错误见[host.stderr.log](host.stderr.log)，零帧统计见[host/summary.json](host/summary.json)。恢复证据见[final-audit.json](final-audit.json)、[closed.json](closed.json)及两次UART原始接收。简表见[result-summary.json](result-summary.json)，执行状态见[state.json](state.json)。

r46物理显示失败及r39超时事实保持，未据本次启动健康或CPU加速结果关闭。当前原BOOT运行，没有后台板测。
