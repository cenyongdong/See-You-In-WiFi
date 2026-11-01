# 独立H.264有限测试：位置、产物与停止边界

代理执行本轮。HDMI目标为1920×1080@60Hz且设备测试暂停；本文件只覆盖720p10fps独立VPU文件编码，不初始化Icraft、相机MMU、HDMI、RTSP或写寄存器。

## 主机准备与构建

主机仓库根目录运行`prepare_vpu_frames.py`，使用已有NumPy生成30份逐帧变化NV12，共41,472,000字节。基础为已验收synthetic渲染，底部新增五位帧号与移动条；BT.601有限范围。新目录与LF清单，不覆盖旧包。
`Build-Vpu.ps1 -BuildTag vpu-20261007-r4`在已有FPAI内以GCC9.4.0交叉编译SDK无关`pose_vpu_encode_check`；构建仅编译，不执行设备程序。构建目录已存在时停止，后续修改必须新标签。

本轮已有r1换行预检失败、r2格式顺序导致H2642×2、r3默认编码色彩标记问题，旧结果保留。r4先按Linux接口设置CAPTURE/OUTPUT，再按本机厂商Encoder顺序重新设置CAPTURE并回查两端；要求宽高/布局/颜色正确，不接受默默调整规格。

## Lite阶段

使用已有SSH/SFTP，在新`/tmp/pose-v1-vpu/20261007-r4`上传程序、frames.nv12、manifest.json、files.sha256、run-vpu-stage.sh、board_application_preflight.py。首次登录只对程序`chmod u+x`，不在登录shell设置errexit。

逐阶段在独立sh执行：

```sh
sh /tmp/pose-v1-vpu/20261007-r4/run-vpu-stage.sh negotiate
# 完整回传run-negotiate，代理核验后才执行下一条。
sh /tmp/pose-v1-vpu/20261007-r4/run-vpu-stage.sh encode
```

每阶段预期`run-*/preflight.json`、清单校验、完整dmesg前后、资源、退出码、stdout/stderr及results/events.jsonl。协商不REQBUFS/STREAMON；编码使用驱动MMAP两输入plane（921600/460800、stride1280）与一个H264输出plane，6缓冲区请求以实际返回为准，逐行复制、独立DQBUF、STOP→LAST及全部输入返回后STREAMOFF/释放。不假定一个编码chunk对应一帧，不截固定SPS/PPS。

CLI要求`--allow-vpu-stream`，30帧固定上限，5秒无进展/25秒内部预算，外部30秒TERM＋3秒KILL。身份、格式、范围、错误buffer、超时或OOM/总线异常即保存停止；不自动重跑/改BOOT/重置设备。视频文件为`run-encode/results/video.h264`，成功仍须主机解码与帧ID审查。

## 文件回传与主机审查

在板端已有FFmpeg中仅将Annex-B重新封装MP4，`-c:v copy`，不重新编码；新文件不得覆盖。原始H264和MP4均上传Windows主机，逐文件SHA256核验。
主机已有PI_wifi_sensing环境OpenCV5.0.0/FFmpeg61.19.100，用`review_vpu_video.py`逐帧解码，核验720p/10fps、30帧、所有ID与移动条、唯一画面及输入完整哈希，导出六帧PNG/contact-sheet。计算有损RGB误差/PSNR供审查，不把视频解码数值声明为原始逐位一致或色度校准。无需安装新包。

本轮不建立实时双路/网络播放/5Hz/长期验收；首版推理源与原渲染工程保持。
