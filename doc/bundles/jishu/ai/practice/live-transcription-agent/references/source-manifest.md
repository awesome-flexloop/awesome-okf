---
type: Reference
title: 来源、版本与证据边界
sources:
  - {id: registry, resource: facts.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 来源、版本与证据边界

本包在 2026-10-28 查阅公开官方文档、项目 README 和实现代码。GitHub 链接固定到本次读取的提交；这些提交是研究快照，不意味着所有工具已经在同一台机器上安装或完成兼容性测试。网页没有固定版本，后续使用时应重新核对。

## 来源清单

| ID | 来源与定位 | 本包用途 |
|---|---|---|
| S01 | [OBS Windows 应用音频指南](https://obsproject.com/kb/application-audio-capture-guide) | OBS 与 Windows 版本条件、重复音轨 |
| S02 | [OBS macOS 音频指南](https://obsproject.com/kb/macos-desktop-audio-capture-guide) | macOS 13、应用与桌面音频 |
| S03 | [OBS PulseAudio 实现](https://github.com/obsproject/obs-studio/blob/2735cc48ce60e2f03483ff5e80f96bd07e0a94d7/plugins/linux-pulseaudio/pulse-input.c#L577-L600)；[PipeWire 应用捕获插件](https://github.com/dimtpap/obs-pipewire-audio-capture/blob/6b96268112390553958a6627870aca0857122365/README.md) | 区分原生设备捕获与第三方插件 |
| S04 | [OBS 录制格式指南](https://obsproject.com/kb/audio-video-formats-guide) | MKV、普通与 fragmented/hybrid MP4 的中断边界 |
| S05 | [FFmpeg segment 文档](https://ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment)；[实现快照](https://github.com/FFmpeg/FFmpeg/blob/58584087cfc34a6b0894886b23e3d912ca4568f2/libavformat/segment.c) | 关键帧切段、CSV 时间、时间戳重置 |
| S06 | [FFmpeg HTTP 协议文档](https://ffmpeg.org/ffmpeg-protocols.html#http) | 网络重连选项与适用范围 |
| S07 | [Streamlink CLI](https://streamlink.github.io/cli.html)；[参数定义](https://github.com/streamlink/streamlink/blob/7d2b6d6d1cdb0a5692208f37b3413c8f1a0eeda5/src/streamlink_cli/argparser.py)；[HLS 实现](https://github.com/streamlink/streamlink/blob/7d2b6d6d1cdb0a5692208f37b3413c8f1a0eeda5/src/streamlink/stream/hls/hls.py) | 输出、重试、当前播放列表窗口 |
| S08 | [yt-dlp README](https://github.com/yt-dlp/yt-dlp/blob/f264a6cbd1f630894da0f368df00f8aae50140e0/README.md)；[站点列表](https://github.com/yt-dlp/yt-dlp/blob/f264a6cbd1f630894da0f368df00f8aae50140e0/supportedsites.md) | 直播起点、缺片处理、许可 |
| S09 | [Bililive-go README](https://github.com/bililive-go/bililive-go/blob/b97242bb89e8d84e497aa7ec02f9ccdbe1d05b24/README.md)；[FFmpeg 调用](https://github.com/bililive-go/bililive-go/blob/b97242bb89e8d84e497aa7ec02f9ccdbe1d05b24/src/pkg/parser/ffmpeg/ffmpeg.go#L462-L475) | 国内平台录制与分段路径 |
| S10 | [DouyinLiveRecorder README](https://github.com/ihmily/DouyinLiveRecorder/blob/add187f8d8c7ff7d231fcbee45cbb4f1ed247d3a/README.md)；[配置样例](https://github.com/ihmily/DouyinLiveRecorder/blob/add187f8d8c7ff7d231fcbee45cbb4f1ed247d3a/config/config.ini) | 平台监控、分段与凭证需求边界 |
| S11 | [StreamCap README](https://github.com/ihmily/StreamCap/blob/e1e8dbf1657df58f363e6de7a9ce739c340dba55/README.md)；[直链处理](https://github.com/ihmily/StreamCap/blob/e1e8dbf1657df58f363e6de7a9ce739c340dba55/app/core/recording/stream_manager.py#L220-L235) | 桌面/Web 形态、一次性 URL 与 FLV 限制 |
| S12 | [Whisper README](https://github.com/openai/whisper/blob/86098128c0b4f24f0e2aa2994de830614b474227/README.md) | 模型语言、30 秒滑窗、许可 |
| S13 | [faster-whisper README](https://github.com/SYSTRAN/faster-whisper/blob/9e472ae9de8bb374552f531f752654554b76b2d6/README.md)；[模型与 tokenizer 加载](https://github.com/SYSTRAN/faster-whisper/blob/9e472ae9de8bb374552f531f752654554b76b2d6/faster_whisper/transcribe.py#L675-L712) | CTranslate2、硬件、生成器、离线回退；[下载函数](https://github.com/SYSTRAN/faster-whisper/blob/9e472ae9de8bb374552f531f752654554b76b2d6/faster_whisper/utils.py)核对模型 revision 与输出目录参数 |
| S14 | [whisper.cpp README](https://github.com/ggml-org/whisper.cpp/blob/21ba6d269a02c14309355cb96822db6058d4cf48/README.md)；[stream 示例](https://github.com/ggml-org/whisper.cpp/blob/21ba6d269a02c14309355cb96822db6058d4cf48/examples/stream/stream.cpp#L278-L341) | Metal/CoreML/OpenVINO、采样步长与窗口 |
| S15 | [WhisperLive README](https://github.com/collabora/WhisperLive/blob/a640654941b118a189499b83c392e33aeb8d7415/README.md)；[后端消息](https://github.com/collabora/WhisperLive/blob/a640654941b118a189499b83c392e33aeb8d7415/whisper_live/backend/base.py#L205-L255) | 近实时服务、完成状态与说话人 |
| S16 | [WhisperLiveKit README](https://github.com/QuentinFuxa/WhisperLiveKit/blob/eb92c115ee7abc1e161b0b2159da31785b0f5566/README.md)；[API](https://github.com/QuentinFuxa/WhisperLiveKit/blob/eb92c115ee7abc1e161b0b2159da31785b0f5566/docs/API.md) | 流式策略、后端与语言范围 |
| S17 | [FunASR README](https://github.com/modelscope/FunASR/blob/940b0d2463141a2e9ace8a9fd965b4aea93f2db5/README.md)；[模型许可](https://github.com/modelscope/FunASR/blob/940b0d2463141a2e9ace8a9fd965b4aea93f2db5/MODEL_LICENSE) | 流式 Paraformer、cache、final、模型许可 |
| S18 | [SenseVoice README](https://github.com/QwenAudio/SenseVoice/blob/586bbdb2b052f4fe19322581825228b6810a9fb3/README.md) | 语言、时间戳、说话人处理 |
| S19 | [sherpa-onnx README](https://github.com/k2-fsa/sherpa-onnx/blob/8183d88b6308da6eeb945f6a335757481b402600/README.md)；[online 结果结构](https://github.com/k2-fsa/sherpa-onnx/blob/8183d88b6308da6eeb945f6a335757481b402600/sherpa-onnx/csrc/online-recognizer.h#L24-L91) | online/offline 模型边界、token 时间 |
| S20 | [Buzz README](https://github.com/chidiwilliams/buzz/blob/298dbf003505cf945bdfd1eb8e705348b59a5b34/README.md)；[实时录音指南](https://github.com/chidiwilliams/buzz/blob/298dbf003505cf945bdfd1eb8e705348b59a5b34/docs/docs/usage/2_live_recording.md) | GUI 导入与麦克风、系统声音回环、本地/API 分支 |
| S21 | [Ollama 结构化输出](https://docs.ollama.com/capabilities/structured-outputs)；[generate API](https://docs.ollama.com/api/generate) | JSON Schema、结构校验与本地端点 |
| S22 | [OWASP 提示词注入防护](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | 不可信语料、最小权限、模型外校验 |
| S23 | [库内 VidBee 知识包](../../../products/vidbee/index.md)；[转录与隐私](../../../products/vidbee/concepts/01-transcription-and-privacy.md) | 2026-10-10 的历史材料，未在本次重新核验产品 |

## 版本与许可快照

采集研究读取了 OBS 33.0.0、Streamlink 8.6.2、yt-dlp 2026.10.26、Bililive-go 0.8.3、DouyinLiveRecorder 4.0.7 和 StreamCap 1.0.3 对应材料。ASR 项目以上表完整提交为准，不把默认分支当稳定发行版。网页功能描述与本地安装版本不一致时，以本机版本文档和复测结果重新裁决。

许可概览见[选型页](../concepts/01-tool-selection.md)。源码许可不自动覆盖权重、二进制打包依赖或直播内容；该表不是商业部署的法律意见。

## 独立性与冲突

S01、S02、S04 是同一 OBS 主体；同一项目的 README、官网和实现不能算三次独立实测。S10 与 S11 同属 ihmily 维护的项目，也不能当两份独立性能评测。其他项目的文档可以证明各自接口不同，不能据此证明某一引擎准确率更高。

OBS 格式指南的默认格式表述存在差异，本教程不依赖“默认一定是某格式”，要求操作者查看实际设置。SenseVoice 的当前 README 已出现时间戳参数，本教程不沿用“始终无时间戳”的旧结论。faster-whisper 的本地目录加载仍有 tokenizer 缺失回退，示例在初始化前拒绝该形态，但完整离线运行仍须断网实测。

本包没有独立录播样本、模型精度测评或平台连通性数据。所有效果、端到端延迟和平台可用性保持未验证；总体定级为 `flagged`。
