---
type: Guide
title: 合法采集直播与保留时间轴
sources:
  - {id: sources, resource: ../references/source-manifest.md}
  - {id: facts, resource: ../references/facts.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 合法采集直播与保留时间轴

已结束的直播优先寻找平台允许的回放或导出。录制工具只能获得其当前有权访问的数据，不能恢复未录下且已从平台窗口移除的历史。本页命令仅为操作示例，未在本机执行；需先安装核验来源的工具并确认录制权限。

## 应用音频捕获

| 系统 | 官方资料确认的入口 | 应注意什么 |
|---|---|---|
| Windows | OBS 28+ 应用音频捕获，Windows 10 2004+/11；OBS 30.1+ 窗口/游戏捕获可带音频 | 全局 Desktop Audio 与应用音频不要重复收同一声音 |
| macOS | macOS 13+ 与 OBS 30+ 的 macOS Audio Capture；OBS 28/29 路径不同 | Screen Capture 源隐藏时可能连音频一起消失 |
| Linux | 原生 PulseAudio 输入/输出设备；应用级可研究 PipeWire 插件 | 检查 WirePlumber、音频后端与插件兼容，不照搬 Windows 界面 |

见 F-001—F-003。优先捕获指定应用，关闭麦克风和无关桌面声音；切换耳机/扬声器后重新做小样。OBS 官方容器页的默认格式文字存在不一致，本教程建议主动选择 MKV 或经验证的容错容器，而非依赖默认值。普通 MP4/MOV 中断未收尾时可能不可用。[F-004](../references/facts.md)

## 从页面获取流

以下一行命令适合 PowerShell、Bash 等常见终端；大写 URL 名是参数占位说明，不是有效地址。

```bash
streamlink --output capture.bin "LIVE_PAGE_URL" best
```

Streamlink 默认偏向播放；`--output` 写文件，`--record` 边播放边保存，`--stdout` 才是标准输出。`capture.bin` 保留原始流，后续让 FFmpeg 探测封装；扩展名不是格式转换。`--hls-live-restart` 取可取得的最早片段，不保证完整开播历史。发现流、打开流的重试不等于无限守护。[F-005、F-006](../references/facts.md)

已发布回放的示例：

```bash
yt-dlp --ignore-config --no-playlist --abort-on-unavailable-fragments "REPLAY_URL"
```

`--ignore-config` 避免隐含旧配置；仍需审查实际下载行为。严格失败选项能暴露不可用片段，但不能恢复缺失内容。`--live-from-start` 在核验版本中仍实验性且仅列出 YouTube、Twitch、TVer、mellow-fan，不能外推到抖音/B站。`--download-sections` 不是循环分段器。[F-010、F-011](../references/facts.md)

## 已授权媒体直链

```bash
ffmpeg -n -reconnect 1 -reconnect_streamed 1 -reconnect_on_network_error 1 -reconnect_delay_max 10 -i "DIRECT_HTTP_LIVE_MEDIA_URL" -map "0:v:0?" -map "0:a?" -c copy capture.mkv
```

这要求 HTTP 持续媒体地址，不是普通直播间网页；选项适用范围受协议与 FFmpeg 版本限制。命令只展示基础重连，不是完整 HLS 会话恢复策略。`-n` 拒绝覆盖既有文件；使用新会话目录并保存退出码与错误日志。不要公开带签名参数的地址，也不要把令牌粘贴到公共知识包。

重连时记录缺口并建立新的连续媒体项；`reconnect_at_eof` 只适合需要把 EOF 当故障的直播路径，不应无区别加给回放。重试不能补回过期片段。[F-009](../references/facts.md)

## 已关闭录制的分段

在新建空目录中执行，输入是停止写入的 `capture.bin`：

```bash
ffmpeg -n -i capture.bin -map "0:v:0?" -map "0:a?" -c copy -f segment -segment_time 600 -reset_timestamps 1 -segment_list segments.csv -segment_list_type csv part-%04d.mkv
```

这是离线后处理示例，不是“边播边分析”。流复制切段受关键帧约束，600 秒是目标，不是每段实际长度；CSV 给出媒体段起止秒数，保留它用于偏移映射。`reset_timestamps` 令段内时间接近零，不会自动给每个字幕恢复全局时间。CSV 的段起点不一定是目标音轨首个解码采样的起点，不能直接作为抽取 WAV 的偏移。[F-007、F-008](../references/facts.md)

上述两条 FFmpeg 命令保留全部音轨，再在原文件或保留全音轨的段上检查轨道：

```bash
ffprobe -v error -show_streams -show_format -of json part-0000.mkv
```

按音轨逐一试听，确认主播所在轨。以下仅在目标恰好是第一个音轨时使用 `0:a:0`；否则替换音轨序号，再生成常见 ASR 输入格式：

```bash
ffmpeg -n -i part-0000.mkv -map 0:a:0 -ac 1 -ar 16000 -c:a pcm_s16le part-0000.wav
```

`0:a:0` 是第一个音轨，不保证它就是主播声音。先用 `ffprobe` 检查轨道并试听；多音轨内容不应随意混为单声道。16 kHz 只是常见识别输入，最终服从模型要求。需要保留视频理解能力时，不要删除原始视频。

## 准实时采集如何接上

可将获授权直播流通过 Streamlink 标准输出送给 FFmpeg，FFmpeg 输出固定格式音频块，消费端只处理关闭的块。相比逐条复制命令，这一步额外需要进程监督、管道退出码、文件完成信号、背压、时轴映射和断线登记；本包不把上述离线分段命令冒充完整运行服务。

具体延迟以“观众声音到达 → 字幕定稿”的测量为准。短块增加上下文丢失和重复合并风险；需要接近即时字幕时优先评估[流式 ASR](03-local-asr.md)，不要盲目把分段参数改得极小。
