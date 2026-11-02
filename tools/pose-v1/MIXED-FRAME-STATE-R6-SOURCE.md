# 跨帧执行状态修正r6：来源与边界

2026-10-06明确将当前问题所有执行操作交给代理，代理直接构建、传输、运行及读取证据。
本文件为修正来源说明；构建和全部板端工程阶段现已通过，[完整结果](MIXED-FRAME-STATE-R6-RESULTS.md)为当前验收结论。

## 实际定位

r5-r1同一Session首次308从层计数0到745；第二帧开始仍745，结束1222，后两帧仍1222。
SDK等待阈值按原固定七组分别为223/234/477/481/638/720/745，并未加上一帧计数。
因此第二帧及后续部分等待被先前的计数提前满足，Host读取前段或后段旧数据，握手发生在当前段完成之前。
这解释了r4 caller/Input0更新、前段局部变化而最终4300值不变的现象；修复效果仍需r6实测闭环。

依据来自匹配的ARM运行库：ZG检查函数调用layerCount再作大于等于比较；Session.forward未见Device::reset调用。
板端与FPAI XRT so哈希均a29e4eee6106afae0b6aada4a07e85416ac6dfc3e74083033ae5d1411749dc96。
详见`evidence/mixed-20261006-readiness-r5/r5-r1/count-review.json`（历史附件，当前仓库未附）
和静态运行库审查（历史附件，当前仓库未附：`evidence/mixed-20261006-readiness-r5/static-runtime-review.json`）。

## 最小修正

仅在独立mixed_check.cpp的每帧边界：

1. 要求上一帧已确认完成，记录清理前状态。
2. 使用官方公共Device::reset(1)清FPGA执行状态，检查ZG330Device::layerCount()==0后开始forward。
3. 保持同一个Session、已加载模型/RAW和原七组及六计算Host绑定。
4. 前向返回后，用原SDK的10秒waitForReady逐项确认两个输出，检查最终计数等于固定最后组720+25=745。
5. 输出和内容仍通过原SDK搬运/dump，保留重复首帧与不同输入响应停止门禁。

官方AXIZG330AIU手册的reset等级表区分0全部状态（FPGA/NPU）与1仅FPGA状态。
该段有拷贝的AXIQL100AIU名称，因此另外核对了当前ARM ZG330DeviceNode::reset实现：level1仅状态清理路径，未进入level0全复位路径。
本次不使用reset(0)、直接寄存器写、setReady(false)、清缓存、额外sleep、每帧重建Session或SDK/模型/BOOT替换。
这是明确帧生命周期的修正，不是失败后自动重试或用全复位掩盖错误。

## 验证边界

新包package-20261006-frame-state-r6、新构建mixed-20261006-frame-state-r6及新板端目录，旧r3/r4/r5证据和程序保留。
新身份逐阶段构建、Host107/内容、离线、SDK内存、apply、单帧、三帧及同Session首帧重复；异常保留停止。
原门禁之外，review_frame_state_protocol.py检查每帧清理前/后计数、七组完成阈值、最终745、输出就绪和实际内容。
三帧分数与姿态须分别具有三套不同输出，重复308的全部捕获内容和输出须与第一次一致。
本轮不能宣布全测试集精度、误差容限、5Hz/延迟、HDMI/RTSP或长期闭环通过。

代理完成构建、Host/离线/内存/apply/单/三全部执行及独立核验；数值容限与长期性能仍待验收。
