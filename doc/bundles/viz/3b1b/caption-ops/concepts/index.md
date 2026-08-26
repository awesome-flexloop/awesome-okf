# 概念文档

caption-ops 字幕工具集核心概念，共 5 篇，按学习路径组织。

* [00 caption-ops 工具集总览](00-caption-ops-overview.md) — caption_ops 是 3Blue1Brown 用于视频字幕自动化制作的 Python 工具集，采用 Unix 哲学设计的松散脚本集合，提供从音频下载、转录、时间对齐、多语言翻译到 SRT 生成、YouTube 上传的完整字幕处理管线。
* [01 音频转录：faster-whisper本地/API双模式](01-transcription.md) — 支持 faster-whisper 本地转录与 OpenAI API 云端转录双模式，采用云端优先、本地兜底的回退策略，核心输出词级时间戳而非直接生成 SRT，为后续句子对齐和智能分段提供基础数据。
* [02 多语言翻译：DeepL/Google/GPT多后端](02-translation.md) — 支持 DeepL、Google Translate、GPT-4o 三种翻译后端，采用 DeepL 优先、Google 回退的策略路由，提供批量翻译、上下文感知翻译等功能，支持 19 种目标语言。
* [03 SRT操作：时间轴与智能分段](03-srt-operations.md) — 包含 SRT 读写与智能分段、命令行时间偏移工具、词级到句级时间映射的 Levenshtein 模糊对齐算法，是连接转录结果与最终可用字幕的关键桥梁。
* [04 完整管线：从视频到多语言字幕](04-pipeline-workflow.md) — 端到端工作流串联了音频下载、转录、翻译、SRT生成、YouTube上传等所有环节，通过中间产物文件实现可中断、可审核、可修改的非破坏性管线，支持批量多视频处理和人工修正后的自动同步。

```{toctree}
:hidden:
:maxdepth: 7

00-caption-ops-overview
01-transcription
02-translation
03-srt-operations
04-pipeline-workflow
```
