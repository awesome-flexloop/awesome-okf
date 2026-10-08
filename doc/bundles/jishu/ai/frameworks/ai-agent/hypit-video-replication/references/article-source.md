---
type: Reference
title: "Hypit 博文与官方事实登记（F-001~F-024）"
description: "登记微信公众号文章与 Hypit 官方仓库、README、Skill 中的关键事实。"
tags: ["Hypit", "视频工作流", "事实登记", "Agent Skill"]
generated: { by: "reference_agent", at: "2026-09-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/N5jRPXG_fSs668l5mSUdvQ?from=industrynews&color_scheme=light#rd
  - id: repo
    resource: https://github.com/hypit-ai/hypit
  - id: readme
    resource: https://raw.githubusercontent.com/hypit-ai/hypit/main/README.md
  - id: skill
    resource: https://raw.githubusercontent.com/hypit-ai/hypit/main/skills/hypit/SKILL.md
---

# 信源与事实登记

> F-001~F-002、F-023~F-024 来自微信公众号文章；F-003~F-022 为官方仓库、README 与 Skill 核验事实。博文中的 Star 数为页面时点单源；官方示例成本仅代表示例运行口径。

| 编号 | 事实 | 状态 |
|---|---|---|
| F-001 | 文章标题为《一条视频复刻 100 个版本，Hypit 开源了。》 | 页面元数据 |
| F-002 | 作者为“开源日记”，发布时间为 2026-09-21 11:49。 | 页面元数据 |
| F-003 | Hypit 官方仓库为 `hypit-ai/hypit`，公开仓库。 | 官方仓库 |
| F-004 | Hypit 可让 AI Agent 把参考视频克隆为完整工作流。 | 官方 README |
| F-005 | 工作流覆盖素材、字幕、B-roll 和特效，并以 words 而非 seconds 锚定。 | 官方 README |
| F-006 | 可从参考视频、模板或自然语言描述开始。 | 官方 README |
| F-007 | 生成模型可选，代码渲染视觉可在不调用生成模型时完成。 | 官方 README |
| F-008 | 官方 Skill 支持 SVML、SVS、SVRun 以及 Runtime/凭证设置。 | 官方 Skill |
| F-009 | 安装命令为 `npx skills add hypit-ai/hypit -g`。 | 官方 README |
| F-010 | 官方仓库提供 Quickstart、Develop 与 Demo 入口。 | 官方 README |
| F-011 | README 徽章声明 Node.js 22.15+、pnpm 10.33、TypeScript 5.9。 | 官方 README |
| F-012 | README 徽章声明 Apache-2.0 with conditions。 | 官方 README |
| F-013 | GOAT DEBATE 是 20 秒足球 tier list 示例。 | 官方 README |
| F-014 | 示例使用 Seedance 2 Mini 720p、GPT Image 2、WhisperX 词级对齐与声音同步排行榜。 | 官方 README |
| F-015 | 示例包含香蕉猫、翻转排名、科技公司创始人三种 clone。 | 官方 README |
| F-016 | 官方给出 GOAT DEBATE 总成本 `$1.15`。 | 官方示例口径 |
| F-017 | 示例并发使用 64 个 headless Chromium 进程。 | 官方示例口径 |
| F-018 | 官方还展示 Podcast、Street Interview 两种结构复用示例。 | 官方 README |
| F-019 | 官方列出 TikTok Shop/affiliate、AI UGC、播客访谈和代码渲染视频等方向。 | 定位声明 |
| F-020 | Skill 要求对参考视频检查画面、帧、语音时间和结构。 | 官方 Skill |
| F-021 | Skill 区分 Brief、Treatment、Timeline、Components 与 Runtime。 | 官方 Skill |
| F-022 | Clone 流程应识别 cut、picture、reveal、sound 与语义的关系，再对目标内容重建。 | 官方 Skill |
| F-023 | 博文称项目获得 1.1 万多个 GitHub Star。 | 时点单源 |
| F-024 | 博文将 Hypit 适用于信息流广告、TikTok Shop、联盟营销、AI UGC 与短视频批量生产。 | 作者转述 |
