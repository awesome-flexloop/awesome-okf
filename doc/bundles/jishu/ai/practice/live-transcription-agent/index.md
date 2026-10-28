---
okf_version: "0.2"
type: Guide
title: 直播本地转录与 Agent 证据分析
description: 从授权录制、离线或流式识别到带时间戳与逐字引文的 Agent 分析，比较现有工具并设计最小适配层。
tags: [ASR, live-stream, local-first, agent, evidence, transcription]
sources:
  - {id: sources, resource: references/source-manifest.md}
  - {id: facts, resource: references/facts.md}
status: flagged
stale_after: 2027-01-28
generated: {by: "process:okf-wiki-agent", at: "2026-10-28"}
---

# 直播本地转录与 Agent 证据分析

> **证据边界（flagged）**：工具接口、版本条件和部分实现已经查阅官方资料；平台连通性、真实录制、本机 ASR、GPU 兼容性、离线网络行为和 Agent 分析效果未实测。纯 Python 引用检查不代表真实转录或语义正确性。研究截至 2026-10-28，产品能力以所列版本为准。

第一版建议使用 OBS 或支持目标平台的录制工具保留授权媒体，录制停止后用本地 ASR 生成时间戳文本，再让只读 Agent 输出带片段 ID 与逐字引文的分析。需要边播边分析时，再增加关闭短块、定稿队列和证据修订；没有明确低延迟要求，不必先搭建流式服务。

## 按目标选择入口

| 你要完成的事情                         | 先读                                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------------- |
| 在 Windows 验证浏览器声音能否进入本地文件       | [应用录音实践](examples/windows-recording.md)                                                  |
| 选择录制器、ASR 或实时转录方案               | [工具选型](concepts/01-tool-selection.md)                                                    |
| 避免断线、关键帧和错误时间戳                  | [采集与切段](concepts/02-capture.md)                                                          |
| 比较离线、准实时、真正流式识别                 | [本地 ASR](concepts/03-local-asr.md)                                                       |
| 将已关闭的 PCM WAV 转为 Agent 可读 JSONL | [离线转录示例](examples/offline-transcription.md)                                              |
| 让分析可定位、可复核而非只出摘要                | [证据契约](concepts/04-transcript-contract.md)与[Agent 分析](concepts/05-agent-analysis.md)     |
| 防止虚构引用和把语料当指令                   | [引用检查示例](examples/agent-evidence-check.md)与[可靠性和安全](concepts/06-reliability-security.md) |

## 范围与交付

本包包含 7 篇概念、3 篇实践示例、4 篇参考记录，以及目录与变更日志，共 19 个 Markdown 文件。研究覆盖 OBS、FFmpeg、Streamlink、yt-dlp、国内录播项目、Whisper 系列、FunASR、SenseVoice、sherpa-onnx、Buzz 和本地结构化分析；已有 VidBee 内容以链接复用。

自建部分限于交换格式、定稿和引用关系设计，以及离线转录、引用检查代码示例。没有交付全天候录制守护、MCP 服务或可直接部署的平台。示例代码嵌在教程中，需读者保存后按前置条件运行。

只处理自有或授权材料。公开可看不自动授予录制、云处理、改编或发布权；本教程不绕过登录、验证码或 DRM，不采集账号 Cookie。原始媒体与私人分析留在独立本地工作目录，不放入公开知识包。

## 阅读顺序

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
log
```

