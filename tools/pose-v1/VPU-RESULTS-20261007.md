# V2独立H.264文件编码与主机审查完成

将HDMI目标更新为1920×1080@60Hz，并先暂停HDMI测试、独立编码后回传主机审查。本轮已完成后者；**HDMI只是目标变更，板端时序、BOOT和位流没有修改**。DELL E2421HN已经接入且报告不支持时序，原“未接屏”记录为历史。PC设置截图不能证明板端当前输出模式。

## 工程结果

新增SDK无关`pose_vpu_encode_check`、构建、有限阶段运行、主机生成/解码与独立取证工具。不链接Icraft，不初始化NPU/HDMI/相机MMU，不直接访问寄存器。
FPAI GCC9.4.0构建无警告，AArch64 PIE仅依赖标准运行库；最终程序SHA256为`8f713fc8d6c76a03053544634591448f1068ef0a392261023bf73d5b1538e8ce`。新r4包保留所有历史目录和源码副本；原推理及CPU渲染实现保持。

MVX实际协商输入为NV12、1280×720、两平面：Y容量921600、UV容量460800，两者stride1280；编码输出H264、单平面2097152字节。两端返回SMPTE170M/601/有限量化/709传递设置；10fps Q16、2Mbps、Baseline控制读回一致。
请求六个驱动MMAP缓冲区，按实际planes/容量逐行复制，输入与输出独立出队，正常STOP→LAST并确认全部输入返回后STREAMOFF/释放。没有硬编码SPS/PPS长度或把MPLANE当连续单plane。步骤参考[Linux stateful encoder接口](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/dev-encoder.html)及本机厂商`Encoder`实现。

输入是已验收synthetic骨架背景＋五位帧ID/移动标记，30帧41,472,000字节，输入SHA256 `34eb4ed557d1f2c399e0867b5cc8e5c64be88f1baec30d10799e1197a58d16cd`。这是独立预生成图像测试，没有在编码时重新运行推理。

| 项目 | 实测结果 |
| --- | --- |
| 编码/归还 | 30帧提交、30帧归还、LAST正常；32个capture chunk含头部及空结束包 |
| 原始码流 | 36,717字节；1 SPS、1 PPS、1 IDR、29非IDR slice，Annex-B边界解析通过 |
| PC审查容器 | MP437,649字节，1280×720、10fps、3秒、Constrained Baseline、yuv420p |
| 主机逐帧 | 原始H264与MP4各30帧，编号0..29与移动标记均正确、30图均不同，两种文件解码像素逐位相同 |
| 传输 | 原始H264与MP4的主机SHA256与板端清单一致 |
| 身份/异常 | BOOT/SDK3.39.0/三库一致；协商与编码exit0/stderr空，完整dmesg前后相同，无OOM/总线错误 |
| 有损参考 | 原始NV12经主机OpenCV转换对照：8位RGB平均绝对误差1.42279、最大64、PSNR41.17324dB；包含解码色彩约定，不是逐位视频编码或色度校准验收 |

完整[完成核验](evidence/vpu-20261007-r1/completion-review.json)、[协商](evidence/vpu-20261007-r1/negotiate.review.json)、[编码](evidence/vpu-20261007-r1/encode.review.json)、[主机30帧审查](evidence/vpu-20261007-r1/host-review/review.json)保留。

审查视频：[MP4样片](evidence/vpu-20261007-r1/encode-r4/results/review.mp4)；主机解码[六帧联系图](evidence/vpu-20261007-r1/host-review/contact-sheet.png)。骨架为测试合成姿态，静态画面中的FRAME999属于基础图；底部五位块和移动条是本次编码序列0..29，不冒充新推理帧。

## 已遇到问题及修正边界

1. r1清单使用Windows回车，Linux把回车当文件名；预检停止、程序未启动。修正为字节写入LF清单，新r2目录，保留失败。
2. r2先设置CAPTURE再原始输入后，MVX保留编码2×2；严格门检停止，未分配/开流。按厂商本机Encoder在原始输入之后重新设置编码输出、两端G_FMT回查，r3尺寸正确。
3. r3编码端默认709/全范围而原始输入601/有限，未开流。r4显式设置编码色彩并两端一致，实际返回通过。ffprobe未报告H264显式色彩标记，不能据G_FMT宣称VUI色彩信号已经正确。
4. 裸H264没有容器PTS。板端FFmpeg重新封装时有unset timestamp警告（exit0），本次以明确10fps重建3秒离线时间轴，不重新编码。主机OpenCV裸流元数据给25fps和无效帧数，第一次误用MP4速率断言失败后保留目录；独立Annex-B审查只认实际解码计数/ID，MP4速率仍严格核验。未来RTSP必须使用capture时间戳并正确区分头部/帧，不套裸流自动速率。

## 对后续开发的参考

独立VPU文件路径与主机解码已通过，不等于实时推理＋编码争用、HDMI、RTSP重连、整机5Hz或30分钟通过。2Mbps是控制目标，本次低变化短片不能作长期码率或吞吐基线。
下一步可封装有界编码输入/输出接口，保留实际plane/复制/生命周期检查；用已生成真实骨架帧序列验证，再接独立RTSP及时间戳/色彩标记。HDMI仍按暂停，恢复时先建立当前BOOT像素时钟/scanout/换帧配套与1080p60目标映射，不写猜测寄存器。
无新依赖安装：主机使用已有PI_wifi_sensing环境OpenCV5.0.0预编译FFmpeg61.19.100，板端使用已有FFmpeg4.2.7进行文件封装/探测。SSH、SFTP和验证进程均已结束；新[检查点](evidence/vpu-20261007-r1/next-checkpoint.json)，不重复已通过门检。
