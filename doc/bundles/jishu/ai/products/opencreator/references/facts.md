---
okf_version: "0.2"
type: Reference
title: "OpenCreator 事实清单（facts）"
description: "自微信公众号博文与 GitHub 官方仓库采集的结构化事实清单，F-001 起连续编号，区分 page_fact 与 author_claim"
tags: [opencreator, facts, source-index]
generated: { by: "wechat-public-okf:R", at: "2026-10-10T12:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator (formerly KrillinAI)"
  - id: github-api
    url: "https://api.github.com/repos/krillinai/OpenCreator"
    title: "GitHub API 仓库元数据"
---

# OpenCreator 事实清单（facts）

> 本清单登记自博文（`blog`）与官方仓库（`github-repo` / `github-api` / `official-home`）采集的**结构事实**与**作者声明**。执行者（Agent）的解读与洞察不在此清单中，见知识地图与各概念文档。

## 事实清单

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-001 | OpenCreator 是跑在自己电脑上的 AI 创作工作台，GitHub Star 数约 1.2 万 | author_claim | blog | 导读段 | verified（官方 2026-10-10 快照 12,671） |
| F-002 | 平台内装 10 个创作工具：视频翻译、视频下载、封面生成、图片生成、文章写作、小红书笔记、短视频脚本、火柴人动画、智能配音、视频生成 | author_claim | blog | 导读段 | verified（官方列 10 个 Available 工具，另有 2 个 In development） |
| F-003 | 平台另提供 Agent 对话模式：说清需求后自行调用工具完成 | author_claim | blog | 导读段 | verified（官方「Agent conversation」） |
| F-004 | 项目前身是 KrillinAI，专做视频翻译配音 | author_claim | blog | 简介 | verified（官方 README「OpenCreator was formerly known as KrillinAI」，video-translation topic） |
| F-005 | 仓库约 2024 年底创建 | author_claim | blog | 简介 | verified（GitHub API created_at 2024-12-17） |
| F-006 | OpenCreator 面向个人与小团队本地自用，默认跑在自己机器，无需连云服务 | author_claim | blog | 简介 | verified（官方「keep creative and development work running locally」） |
| F-007 | 模型密钥由用户自行配置 | author_claim | blog | 简介 | verified（官方 Settings → AI Services） |
| F-008 | 视频翻译支持 14 种源语言、101 种目标语言 | author_claim | blog | 十工具·视频翻译 | verified（官方「14 source languages and 101 target languages」） |
| F-009 | 转写可支持云端 Whisper 与本地 faster-whisper、WhisperKit | author_claim | blog | 十工具·视频翻译 | verified（官方语音与转写表 +「本地语音转写还支持 faster-whisper、WhisperKit 和 whisper.cpp」） |
| F-010 | 大模型负责断句、对齐、术语和翻译 | author_claim | blog | 十工具·视频翻译 | verified（官方「use LLM context for subtitle segmentation, alignment, terminology, and translation」） |
| F-011 | 出片前可配双语字幕、选配音音色或用自己的声音样本，横屏竖屏都支持 | author_claim | blog | 十工具·视频翻译 | verified（官方 bilingual subtitles / dubbing / custom voice sample / landscape or portrait） |
| F-012 | 视频翻译可导出 SRT、音频或成片 | author_claim | blog | 十工具·视频翻译 | verified（官方「export SRT, audio, or video」） |
| F-013 | README 示例：一段 46 分钟本地视频一次跑完出完整字幕，无叠行，断句自然 | author_claim | blog | 十工具·视频翻译 | verified（官方「对一段 46 分钟的本地视频进行一键处理…没有字幕遗漏或重叠，断句自然」） |
| F-014 | 视频下载支持 B站、抖音、小红书、YouTube、X、TikTok、Instagram、Facebook、Pinterest | author_claim | blog | 十工具·视频下载 | verified（官方 YouTube, Bilibili, Douyin, Xiaohongshu, X, TikTok, Instagram, Facebook, Pinterest 共 9 平台） |
| F-015 | 视频下载贴链接后列出所有可用格式供挑选，也可只下音频 | author_claim | blog | 十工具·视频下载 | verified（官方「inspect available quality and format options, and download video or audio」） |
| F-016 | 部分来源需平台 cookie；小红书链接需贴完整长链，短链不支持 | author_claim | blog | 十工具·视频下载 | single-source/flagged（官方仅言「Some sources may require platform cookies」；小红书短链限制为作者补充观察） |
| F-017 | 火柴人动画使用与艺术家 Harbor Hsia 合作的原创角色，形象全程一致 | author_claim | blog | 十工具·火柴人动画 | single-source（官方称「consistent-character storyboard visuals」；Harbor Hsia 姓名未经本 bundle 独立核验） |
| F-018 | 火柴人动画丢文字进去，解说词、配音、分镜、字幕、渲染一条龙，可下载成片 | author_claim | blog | 十工具·火柴人动画 | verified（官方「Turn text or YouTube content into narration, voice, consistent-character storyboard visuals, subtitles, and a downloadable stick figure animation」） |
| F-019 | 视频生成走 Seedance，提示词加参考图，每版单独保存不覆盖旧的 | author_claim | blog | 十工具·视频生成 | verified（官方「Generate videos with Seedance…preview, regenerate, and download each version」） |
| F-020 | 智能配音：文稿进配音出，音色语速情绪可调 | author_claim | blog | 十工具·智能配音 | verified（官方「Turn scripts into voiceovers with selectable voices, pacing, and emotion controls」） |
| F-021 | 配音可接 OpenAI TTS、MiniMax、Edge TTS、阿里云、火山引擎 | author_claim | blog | 十工具·智能配音 | verified（官方语音表：OpenAI TTS、MiniMax、Edge TTS、Aliyun Speech、火山引擎语音） |
| F-022 | Edge TTS 甚至不需要密钥 | author_claim | blog | 十工具·智能配音 | single-source（Edge TTS 为微软公共语音服务，通常无需密钥，但"免密钥"为作者判断，未做独立核验） |
| F-023 | 提供可视化工作台（填参数点生成）与 Agent 对话两种用法 | author_claim | blog | 两种用法 | verified（官方 Content workspace 与 Agent conversation 双模式） |
| F-024 | Agent 层用 Codex CLI 当执行引擎，OpenCreator 未自造 Agent 循环 | author_claim | blog | 两种用法 | verified（官方「it uses Codex CLI as the execution engine instead of reimplementing an Agent loop」） |
| F-025 | Agent 复用了 Codex 的模型、工具调用、Skills 和 MCP | author_claim | blog | 两种用法 | verified（官方 Codex Native：models, tool calls, conversations, Skills, and MCP） |
| F-026 | 两种操作共用同一状态机；对话改字幕颜色则工作区同步，工作区调参对话知晓进度 | author_claim | blog | 两种用法 | verified（官方 Dual-Mode Workflow「one shared state machine keeps steps, progress, and results synchronized」） |
| F-027 | 每次修改生成新版本，旧版本设置与结果保留，可切回旧版 | author_claim | blog | 两种用法 | verified（官方 Versioning「Every revision creates a new version while preserving earlier settings and outputs」） |
| F-028 | 任务可在后台运行，关闭界面继续执行，跑完发通知 | author_claim | blog | 两种用法 | verified（官方「keep Runs working in the background」+ notifications） |
| F-029 | 可设定时任务 | author_claim | blog | 两种用法 | verified（官方 schedules） |
| F-030 | 记忆分全局、项目、对话三层，告诉过的偏好下次仍生效 | author_claim | blog | 两种用法 | verified（官方「global, project, and thread memory」) |
| F-031 | README 列出的语言模型有 GPT、DeepSeek、通义千问、Kimi、智谱 GLM、豆包、文心、混元、MiniMax | author_claim | blog | 两种用法 | verified（官方语言模型表另含 Grok，博文遗漏 Grok） |
| F-032 | 国内模型走 OpenAI 兼容接口即可接入 | author_claim | blog | 两种用法 | verified（官方「Codex model catalog or your OpenAI-compatible provider」） |
| F-033 | 模板库分视频创作和图片设计两类，官方与独立创作者都有贡献，第三方模板会署名并链到出处 | author_claim | blog | 模板库 | verified（官方「created by OpenCreator and by independent creators. Third-party templates credit their creators and link to the original source」） |
| F-034 | 模板可查看示例效果、完整提示词、参数和作者，提示词完全公开 | author_claim | blog | 模板库 | verified（官方「preview its example result and inspect its prompt, settings, tags, author, and original source」） |
| F-035 | 桌面版在 Releases 页面下安装包，提供 macOS（Apple 芯片和 Intel）和 Windows 64 位 | author_claim | blog | 上手简单 | verified（官方 Ready-to-Use Desktop App；具体平台矩阵以官方 Releases 为准） |
| F-036 | 桌面版自带 Codex CLI，不用装 Node | author_claim | blog | 上手简单 | verified（官方「with Codex CLI included」） |
| F-037 | 首次启动扫描本机有无可用 Codex 配置，有则问是否复用，无则走引导表单配别的服务商 | author_claim | blog | 上手简单 | verified（官方「scan your local Codex configuration and offer to reuse…A guided form is available for other model providers」） |
| F-038 | 网页版源码要求 Node 22 以上、pnpm 锁定 9.15.0（可用 corepack enable 对齐版本）、加 Codex CLI，克隆后 pnpm install、pnpm web:dev | author_claim | blog | 上手简单 | verified（官方 monorepo 使用 pnpm workspace；Node 22 / pnpm 9.15.0 / 端口 19861 细节以官方开发文档为准） |
| F-039 | 网页版浏览器访问 http://127.0.0.1:19861/ | author_claim | blog | 上手简单 | single-source（端口号 19861 为博文声明，本 bundle 未实测；以官方开发文档为准） |
| F-040 | 单个 Agent 任务估算耗时约十万到二十万 token，建议先拿小任务试试 | author_claim | blog | 上手简单 | single-source/flagged（社区测试估算，非官方数字） |
| F-041 | 数据、附件、日志默认全在本机 .runtime/ 目录，SQLite 存项目、会话和记忆 | author_claim | blog | 数据都在本地 | single-source（与官方 Local Security 叙事一致；.runtime 目录与 SQLite 为博文细节，未实测确认） |
| F-042 | 本地服务只监听 127.0.0.1，除健康检查外每个接口都要 token，不暴露到局域网 | author_claim | blog | 数据都在本地 | single-source（与官方 Local Security 一致；逐接口 token 细节未独立核验） |
| F-043 | 模型密钥走系统凭据存储，日志输出前会脱敏 | author_claim | blog | 数据都在本地 | verified（官方「redacted diagnostics」；密钥存系统凭据为博文细节） |
| F-044 | yt-dlp 每 7 天检查一次更新，需手动确认才安装，更新失败可回退到可用版本 | author_claim | blog | 数据都在本地 | verified（官方「check for updates periodically, and update manually while keeping the current working version available if an update fails」；周期"7 天"为博文细节） |
| F-045 | OpenCreator 仓库语言为 TypeScript | page_fact | github-api | language 字段 | verified（官方 language=TypeScript） |
| F-046 | OpenCreator 许可为 Apache-2.0 | page_fact | github-api | license.spdx_id | verified（官方 License Apache-2.0；博文未提及许可） |
| F-047 | OpenCreator 官方项目主页为 https://www.open-creator.ai/en/ | page_fact | github-api | homepage 字段 | verified |
| F-048 | OpenCreator GitHub Star 12,671 / Fork 1,306 / Open Issues 29（2026-10-10） | page_fact | github-api | 快照 | verified |
| F-049 | OpenCreator 顶层目录含 .codex/skills 与 skills/（内含 KrillinAI CLI、Subtitle、TTS、Landscape Render、Portrait Render、Cover、Pipeline Plan 等 7 个 Skill） | page_fact | github-repo | README + 目录树 | verified |
| F-050 | OpenCreator 另有两个 In development 工具：Auto Clips（长视频高光切条）与 Digital Avatar（数字人出镜） | page_fact | github-repo | Creator Tools 表 | verified（博文未提及这两个开发中工具） |
| F-051 | 界面支持简体中文、英文、瑞典语，可自动探测系统语言或手动选择 | page_fact | github-repo | README | verified（博文未提及） |
| F-052 | 图像模型支持 GPT Image、Seedream 4.0（即梦）、Kling v2.1、Nano Banana（Gemini 2.5 Flash Image） | page_fact | github-repo | 模型表 | verified（博文未细化图像模型） |
| F-053 | 视频模型支持 Seedance 2.5、Kling v2.1 Master、Veo 3.1 | page_fact | github-repo | 模型表 | verified（博文仅提 Seedance） |
| F-054 | 语言模型另支持 Grok（xAI） | page_fact | github-repo | 模型表 | verified（博文遗漏 Grok） |
| F-055 | Trendshift 标记 OpenCreator 为单日排名第一仓库（#1 Repository of the Day） | page_fact | github-repo | README badge | verified（官方 badge，动态口径） |