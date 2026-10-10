---
okf_version: "0.2"
type: Concept
title: "十个创作工具：多模态创作闭环"
description: "OpenCreator 的创作工具矩阵——视频翻译、下载、封面、图片、写作、小红书、脚本、火柴人、配音、视频生成及开发中工具"
tags: [opencreator, creator-tools, video-translation, seedance, whisper, tts]
sources:
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator README Creator Tools 与模型表"
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
---

# 十个创作工具

OpenCreator 装载了覆盖「内容创作日常」的创作工具，官方称当前版本含 **10 个可用工具**，另有 **2 个开发中工具**[F-002](references/facts.md)[F-050](references/facts.md)。可用模型与服务取决于本机 Codex 环境与 AI 服务设置。

## 工具矩阵

| 工具 | 状态 | 能力要点 | 事实参考 |
|------|------|---------|---------|
| 视频翻译 | ✅ Available | 老本行；导入本地/公开视频，云端或本地 Whisper 转写，LLM 断句/对齐/术语/翻译；双语字幕、配音或自定义声音样本、横竖屏；导出 SRT/音频/成片 | [F-008~F-013](references/facts.md) |
| 视频下载 | ✅ Available | 解析 YouTube/B站/X/TikTok/Instagram/抖音/小红书/Facebook/Pinterest 公开链接，列格式、下视频或音频 | [F-014~F-016](references/facts.md) |
| 封面生成 | ✅ Available | 结合主题、视频链接与可选参考图，生成并对比多个缩略图变体 | [F-002](references/facts.md) |
| 图片生成 | ✅ Available | 用 GPT Image 从提示词 + 参考图生成，可配比例与数量，预览/单张下载 | [F-002](references/facts.md) |
| 文章写作 | ✅ Available | 从主题/链接/视频/源文档生成选题、大纲与成稿，可加图并导出 Markdown/HTML/PDF | [F-002](references/facts.md) |
| 小红书笔记 | ✅ Available | 从主题或源材料生成完整小红书笔记，可配目标受众/类型/长度 | [F-002](references/facts.md) |
| 短视频脚本 | ✅ Available | 按受众/平台/时长/语气生成可分镜拍摄的脚本 | [F-002](references/facts.md) |
| 火柴人动画 | ✅ Available | 文字/YouTube 内容 → 解说词、配音、形象一致的分镜、字幕、可下载动画；与艺术家 Harbor Hsia 合作原创角色（姓名未经独立核验） | [F-017/F-018](references/facts.md) |
| 智能配音 | ✅ Available | 文稿进配音出，音色/语速/情绪可调 | [F-020~F-022](references/facts.md) |
| 视频生成 | ✅ Available | 用 Seedance 从提示词 + 参考图生成，每版单独保存不覆盖旧版 | [F-019](references/facts.md) |
| Auto Clips（开发中） | 🔧 In development | 分析长视频、识别高光、切成可复用短片段 | [F-050](references/facts.md) |
| Digital Avatar（开发中） | 🔧 In development | 脚本 + 语音 + 数字人出镜的视频 | [F-050](references/facts.md) |

> 博文只列了 10 个「可用」工具，官方 Creator Tools 表另有 Auto Clips 与 Digital Avatar 两个**开发中**工具，本包补充。

## 视频翻译（老本行，最完整）

- **语言**：14 种源语言、101 种目标语言 [F-008](references/facts.md)。
- **转写**：云端 Whisper，或本地 faster-whisper、WhisperKit（官方另补充 whisper.cpp）[F-009](references/facts.md)。
- **LLM 参与**：负责断句、对齐、术语与翻译 [F-010](references/facts.md)。
- **出片配置**：双语字幕、配音音色/自定义声音样本、字幕样式、横屏/竖屏 [F-011](references/facts.md)。
- **导出**：SRT、音频或成片 [F-012](references/facts.md)。
- **官方示例**：一段 46 分钟本地视频一次跑完出完整字幕，无遗漏/无重叠、断句自然 [F-013](references/facts.md)。

## 视频下载

贴链接 → 列出所有可用格式 → 选格式下载视频或音频 [F-015](references/facts.md)。支持 9 个平台：YouTube、B站、X、TikTok、Instagram、抖音、Facebook、小红书、Pinterest [F-014](references/facts.md)。部分来源需要平台 cookie；小红书需贴完整长链、短链不支持（后者为作者补充观察，官方仅言「有些来源需要 cookie」）[F-016](references/facts.md)。

## 模型供给（图像 / 视频 / 语音）

官方模型表（博文未细化，本包补充）：
- **图像**：GPT Image、Seedream 4.0（即梦）、Kling v2.1、Nano Banana（Gemini 2.5 Flash Image）[F-052](references/facts.md)。
- **视频**：Seedance 2.5、Kling v2.1 Master、Veo 3.1 [F-053](references/facts.md)。
- **语音与转写**：Whisper、OpenAI TTS、MiniMax、Edge TTS、阿里云语音、火山引擎语音；本地转写另支持 faster-whisper、WhisperKit、whisper.cpp [F-021](references/facts.md)[F-009](references/facts.md)。

## 模板库

不想从零写提示词，可从模板起步——分**视频创作**与**图片设计**两类，官方与独立创作者都有贡献，第三方模板会署名并链接出处 [F-033](references/facts.md)。点开模板可查看示例效果、完整提示词、参数与作者，提示词完全公开 [F-034](references/facts.md)。

## 相关概念

- [项目身份与定位](00-what-is-opencreator.md)
- [Agent 与 Codex 原生架构](02-agent-and-codex-native.md)