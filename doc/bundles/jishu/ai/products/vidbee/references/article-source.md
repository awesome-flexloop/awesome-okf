---
type: Reference
title: VidBee 事实登记
status: stable
verified: {by: "process:seven-concepts-v", at: "2026-10-10"}
stale_after: 2026-12-31
source: https://mp.weixin.qq.com/s/JfabWbrAcVGVQeY-vjTs3A
sources:
  - {id: article, resource: "https://mp.weixin.qq.com/s/JfabWbrAcVGVQeY-vjTs3A"}
  - {id: readme, resource: "https://github.com/nexmoe/VidBee/blob/v2.1.0/README.md"}
  - {id: release, resource: "https://github.com/nexmoe/VidBee/releases/tag/v2.1.0"}
  - {id: transcribe, resource: "https://vidbee.org/docs/transcribe/"}
  - {id: ai-prompts, resource: "https://vidbee.org/docs/ai-prompts/"}
  - {id: repo, resource: "https://github.com/nexmoe/VidBee"}
  - {id: readme-main, resource: "https://github.com/nexmoe/VidBee/blob/feeea6b2b5f451e62774c87c25f3056d583f494f/README.md"}
generated: {by: "process:okf-wiki-agent", at: "2026-10-10"}
---

# VidBee 事实登记

F 编号仅标识本包事实条目，不是七概念中的 First Principles。此文件是唯一事实登记，不另建易漂移的副本；[核验报告](verification.md)逐行覆盖同一编号集合。`official-doc` 指官方资料确认，不代表运行实测；`author_claim` 记录作者说法，不表示采信。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 页面署名芋道源码、作者 X，标题为自动下载视频、本地转录及 AI 翻译总结的 VidBee 介绍 | page_fact | article | 页面标题与账号栏 | page-confirmed |
| F-002 | 页面发布时间为 2026-10-07 20:05，未单独显示时区 | page_fact | article | 日期栏 | page-confirmed |
| F-003 | 作者在第七章说明未安装、未运行转录，描述参考官方 README 与未指明 URL 的来源正文 | author_claim | article | 07 AUDIENCE | single-source |
| F-004 | VidBee 仓库为 public，许可标识 MIT | official_fact | repo | 仓库 API 与 LICENSE | official-doc |
| F-005 | 本次 API 快照 stars 为 10801；原文称一万多，截图 10.8k | official_fact | repo、article | stargazers_count 与仓库图 | snapshot |
| F-006 | 最新正式 release API 返回 v2.1.0，published_at 为 2026-08-30T11:43:40Z | official_fact | release | tag_name、published_at | official-doc |
| F-007 | v2.1.0 资产含 Windows setup/portable exe 与便携 zip、macOS arm64/x64 dmg/zip、Linux AppImage 与 amd64 deb | official_fact | release | assets.name | official-doc |
| F-008 | README 声明支持 1000+ 站点及在线下载、本地媒体导入；仓库 API description 列出 Bilibili，固定发布 README 未列此站名 | official_fact | readme、repo | 导语、Supported Sites、description | official-doc/not-benchmarked |
| F-009 | 发布版 README 列出桌面、Web/API 与 WXT 浏览器扩展目录；共享下载核心基于 yt-dlp/ffmpeg，API 使用 Fastify/oRPC/SSE，Web 使用 TanStack Start | official_fact | readme | Web + API、Contributing | official-doc |
| F-010 | 本地转录模型系列列为 Whisper、SenseVoice、Parakeet、Qwen3-ASR | official_fact | readme | Transcribe locally | official-doc |
| F-011 | 可使用已有源字幕，也可运行本地 ASR 产生新转录 | official_fact | readme | Transcribe locally | official-doc |
| F-012 | 可自动检测说话人、指定人数和重新标记；重新标记不修改识别文字 | official_fact | readme | Transcribe locally | official-doc |
| F-013 | 可搜索文字或说话人，点击时间戳定位播放 | official_fact | readme | Transcribe locally | official-doc |
| F-014 | 支持复制、纯文本/Markdown 导出与可选择或烧录字幕的视频 | official_fact | readme | Transcribe locally | official-doc |
| F-015 | 内置提示词用途为摘要、语法清理、FAQ、统计提取、思维导图、改写与翻译七类 | official_fact | readme | Ask AI | official-doc |
| F-016 | README 列十一类供应商：OpenAI、Anthropic、Google、DeepSeek、Groq、Azure、Hugging Face、OpenRouter、xAI、Ollama、LM Studio，另有 Custom；AI 指南称 Ollama、LM Studio 本地服务无需 API key | official_fact | readme、ai-prompts | Ask AI、Providers | official-doc |
| F-017 | Custom 可填名称、Base URL、Model ID、API key，并测试连接；可切换供应商而保留提示词库 | official_fact | readme、ai-prompts | Ask AI、Providers | official-doc |
| F-018 | ASR 在本机运行；云 AI 请求把提示词及转录内容发送到所选供应商；本地端点可使 AI 步骤也在本机 | official_fact | readme、ai-prompts | 隐私提示 | official-doc/not-network-audited |
| F-019 | 官方说明 API keys 存在用户计算机，AI 指南称不上传 VidBee | official_fact | readme、ai-prompts | Ask AI、隐私说明 | official-doc/not-security-audited |
| F-020 | 下载队列支持批量、播放列表、频道、进度、暂停、恢复、重试及移除 | official_fact | readme | Download and organize | official-doc |
| F-021 | 成功下载可自动入转录队列；转录并发上限可配置；关闭自动转录开关不会取消已有排队任务 | official_fact | readme、transcribe | Transcribe after download | official-doc |
| F-022 | RSS 支持自动或手动下载、关键词过滤、自动标签、只取最新、目录和命名模板 | official_fact | readme | RSS subscriptions | official-doc |
| F-023 | 视频容器选项为 Auto(MP4/MKV)、MP4、MKV、WebM、Original，另可单独保存音频 | official_fact | readme | Formats and metadata | official-doc |
| F-024 | 可写入可用元数据、封面、章节及字幕，并设置命名和下载位置 | official_fact | readme | Formats and metadata | official-doc |
| F-025 | 发布版 README 给出 pnpm run start:web、docker compose up -d --build、docker compose down；示例 API/Web 端口 3100/3000 | official_fact | readme | Web + API | official-doc/not-executed |
| F-026 | 固定 main README 说明下载目录 /data/downloads，/data/vidbee 保存 SQLite vidbee.db、设置及模型；若已有数据库在 /data/downloads/.vidbee，继续使用旧目录，直到 /data/vidbee/vidbee.db 存在；Web 操作服务端文件系统 | official_fact | readme-main | Storage inside API | official-doc/development-snapshot |
| F-027 | 原文认为本地模型效果通常不如云端，没有提供同任务对照数据 | author_claim | article | 03 AI | single-source/flagged |
| F-028 | 原文建议个人学习研究、不二次分发，并承认翻译解说合规性需按用途判断 | author_claim | article | 06 LIMITS | single-source/not-legal-conclusion |
| F-029 | 原文建议连接 RSSHub 解决订阅源问题 | author_claim | article | 04 QUEUE | single-source/not-tested |
| F-030 | 原文包含与 VidBee 无关的芋道项目版本、Star 与社群推广 | page_fact | article | 开头、插入推广、结尾 | excluded-from-product-claims |
| F-031 | 官方转录入口为 Transcripts → Add audio or video，也支持拖放、粘贴本地文件及下载行 Transcribe / View transcript；模型设置入口 Settings → Transcription | official_fact | transcribe | How to start it、Transcription settings | official-doc/not-executed |
| F-032 | 官方指南列队列状态、Stop/Retry、换模型重跑、No speech 的 Transcribe anyway | official_fact | transcribe | Read a transcript | official-doc/not-executed |
| F-033 | 官方指南称模型初次下载后可离线转录；Advanced → Download source 可切换 GitHub/ModelScope | official_fact | transcribe | Transcription settings | official-doc/not-executed |
| F-034 | 官方指南称 Whisper 支持 100+ 语言，其他模型覆盖不同；Tiny 偏向速度，Base/Small 为一般机器选项，大模型偏向准确度；并发默认 1，需按 RAM 调整 | official_fact | transcribe | Transcription settings | official-doc/not-benchmarked |
| F-035 | 官方 AI 流程为 Settings → Providers、Test connection、保存后 Use；Custom 要求 OpenAI-compatible /v1 端点 | official_fact | ai-prompts | Providers | official-doc/not-executed |
| F-036 | 转录指南把转录库标记 Experimental；扩展不运行本地 ASR；新 Transcript/Overview 桌面桥接晚于 v2.1.0，要求兼容构建，不能假定该正式版支持 | official_fact | transcribe | How to start it、Browser transcripts | official-doc/development-boundary |
| F-037 | 官方指南所述开发版测试使用 12 秒录音和缓存模型，未覆盖首次下载、全部语言及全部导出样式 | official_fact | transcribe | A local transcription check | official-doc/limited-test |
| F-038 | 官方指南称音频文件只能导出文本而非视频；Hard 字幕需要重编码且不能关闭 | official_fact | transcribe | Export | official-doc |
