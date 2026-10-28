---
type: Guide
title: 本地 ASR 的模型、后端与流式边界
sources:
  - {id: sources, resource: ../references/source-manifest.md}
  - {id: facts, resource: ../references/facts.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 本地 ASR 的模型、后端与流式边界

中文直播先用目标机器上的短样本比较模型，再决定是否扩大部署。口音、背景音乐、专业词、多人重叠和演示画面分别构成不同难点；没有同样本评测，不能用上游某张速度表直接选“最强模型”。

## 模型和运行时分开选择

Whisper 是识别模型系列及其原始实现；faster-whisper 用 CTranslate2 运行 Whisper，whisper.cpp 提供原生推理路径。Whisper 的 `.en` 模型是英语专用，中文应选择多语模型。原始 `transcribe()` 对完整文件使用 30 秒滑动窗口。[F-013、F-014](../references/facts.md)

| 环境 | 可先检查的实现 | 不能假定的能力 |
|---|---|---|
| 普通 CPU | faster-whisper CPU/int8、whisper.cpp、适用的 ONNX 模型 | CPU 也可能达不到输入速度，须测 RTF |
| NVIDIA | faster-whisper CUDA 或 whisper.cpp CUDA | 当前 faster-whisper README 要求 CUDA 12 cuBLAS 与 cuDNN 9，版本须配套 |
| Apple Silicon | whisper.cpp Metal/Core ML、WhisperLiveKit 相应 MLX 配置 | faster-whisper 的 CUDA 选项不是 Metal |
| Intel | whisper.cpp OpenVINO encoder 或支持 OpenVINO 的服务/运行时 | 不是所有 Intel 设备或整个模型都自动加速 |
| 其他 GPU / 边缘设备 | sherpa-onnx 适用 provider，或经确认的原生后端 | 构建有 provider 不代表模型可运行；回退 CPU 要能被观察 |

接口与硬件事实见 F-014、F-016—F-021；不在本表承诺内存门槛、准确率或端到端延迟。

## 流式能力要看状态

- `segments` 是 Python 生成器，只说明结果迭代方式，不代表接收持续音频流。
- whisper.cpp 的 `whisper-stream` 示例定期取音频、拼接窗口后重新识别；500 ms 步长不是总延迟。
- WhisperLive 提供音频缓冲和 nearly-live WebSocket 体验；WhisperLiveKit 的 AlignAtt/SimulStreaming、LocalAgreement 等是具体解码/定稿策略，不能简单归为互不相关短块。
- FunASR 的 `paraformer-zh-streaming` 有逐会话 `cache` 与 `is_final`；sherpa-onnx 明确区分在线和非在线模型。

见 F-014、F-016—F-021。选择实时服务时确认协议如何表示临时结果、最终结果和重连后的状态重置。WebSocket 是传输通道，不是流式准确性证明。

## 中文与多语选择

FunASR 提供多模型工具链，不能把框架名字等同于某个模型。SenseVoiceSmall 支持中、粤、英、日、韩，正式接口已包含时间戳选项；非自回归、速度快不等于原生流式。长音频可按 VAD 分段，但语音活动检测只找“像语音”的区间，不保证逐字正确。[F-019、F-020](../references/facts.md)

跨语言或中英术语混杂的直播要单独测试。ASR 翻译任务和转录任务不同：转录保留原语言，翻译改变表达；若要求证据可回听，应同时保存原语言转录与翻译派生文本。

## 本地模型必须完整

faster-whisper 的固定源码显示：本地模型目录缺少 `tokenizer.json` 时会调用预训练 tokenizer 加载接口，即便调用者给了 `local_files_only=True`。因此离线部署必须检查完整目录，不能仅靠这个参数推定无外连。[F-015](../references/facts.md)

模型权重、配置、tokenizer、VAD 及说话人模型都应在部署前下载并记录来源。代码、模型许可证分别核对；下载完成之后才做断网测试。首次安装、更新检查、依赖下载和模型推理是不同网络面。

## 说话人与时间戳

说话人分离回答“哪一段像同一人”，不是“这个人是谁”。匿名 `SPEAKER_00` 在另一段录音里可能指向另一人；没有跨块匹配不能直接拼成同一个身份。重叠语音也不能仅凭分离标签认定文字归属正确。[F-022](../references/facts.md)

时间单位因实现而异：Whisper 系列常用秒；SenseVoice 时间对用毫秒；sherpa-onnx 在线 token 时间戳以秒表示，token 时间点也不等于精确词级起止。接入前用已知短样本核实单位、原点和持续时长。[F-014、F-020、F-021](../references/facts.md)

## 不应直接当成置信概率的值

解码分数、平均 log probability、语音活动分数、声纹相似度和检索相似度有不同定义。未经校准，不写成“这句话 98% 正确”。保留原值和定义，用人工抽查建立关键实体错误率、CER 与时间偏移分布，再决定是否自动接受。

ASR 可以生成流畅但错误的文字，尤其在静音、背景音乐或上下文缺失时。摘要模型还会再次压缩或改写，因此重要数字、人物、否定与操作步骤至少回听一次。[验收方法](06-reliability-security.md)
