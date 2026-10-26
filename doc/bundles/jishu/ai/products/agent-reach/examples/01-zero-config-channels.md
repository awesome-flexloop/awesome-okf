---
okf_version: "0.2"
type: Example
title: "默认渠道实操：网页、GitHub、YouTube、B站、V2EX"
description: "v1.6.0 默认 5 渠道的可照做命令与意图说法，附 RSS/Exa 退役说明、bili-cli 与 doctor 自查方式"
tags: [agent-reach, zero-config, jina-reader, github, youtube, bilibili, v2ex, retired-channels]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-26T11:45:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
---

# 示例 01：默认渠道实操

> v1.6.0 的默认档是 **5 个**：web、youtube、github、bilibili、v2ex（F-108）。实际使用通常不用手敲命令——对 Agent 说意图即可；这里列底层命令，是为了让你知道 Agent 在调什么、出问题能自查。
> **已退役**：v1.5 时代的 RSS（feedparser）与 Exa 全网搜索（mcporter）在 v1.6.0 的渠道表与代码目录中都已移除（F-108），本页末尾保留说明供旧版用户对照。

## 1. web：读任意网页

```bash
curl -s "https://r.jina.ai/https://example.com/article"
```

把目标 URL 接在 `https://r.jina.ai/` 后，返回渲染后的正文文本（F-088）。Agent 侧的说法是"帮我看看这个链接：https://..."，由它自行拼装。

## 2. github：gh CLI

```bash
gh search repos "ai agent" --sort stars --limit 10   # 按 star 搜仓库
gh repo view owner/repo                              # 看仓库详情/README
gh issue list -R owner/repo                          # 看 issue（含评论需进一步读）
```

读公开仓库无需登录；私有仓库或提 Issue/PR 才需要 `gh auth login`（F-088）。

## 3. youtube：字幕与转文字

```bash
yt-dlp --list-subs "https://www.youtube.com/watch?v=VIDEO_ID"          # 先看有哪些字幕轨
yt-dlp --write-sub --skip-download "https://www.youtube.com/watch?v=VIDEO_ID"   # 只下字幕
```

要点：区分**自动生成字幕**与**手动字幕**；语音转文字（无字幕时）需要 Groq 或 OpenAI Key，由本人用 `agent-reach configure groq-key` 配置（F-088/F-114）。

## 4. bilibili：bili-cli，搜索免登录

```bash
bili search "AI 教程" --type video -n 5
```

- 能力：搜索 + 视频详情，**无需登录**；字幕需要扫码登录（F-088）。
- 上游是 bili-cli，不是 yt-dlp：2026-06 yt-dlp 被 B站风控 412 封死后，bilibili 渠道首选切为 bili-cli，备选 OpenCLI → 搜索 API（F-085/F-115）。
- doctor 报 bili 后端 missing 时，对 Agent 说"帮我配 B站"或按 doctor 处方的命令装 bili-cli。

## 5. v2ex：热门、节点、帖子与回复

```bash
agent-reach v2ex hot
agent-reach read https://www.v2ex.com/t/123456
```

无需登录即可读热门、节点帖、帖子详情与回复（F-088/F-108）。

## 已退役：RSS 与 Exa（v1.5 用户会看到，v1.6 已无）

| 渠道 | 旧实现 | 现状 |
|------|--------|------|
| RSS / Atom | feedparser，零配置 | v1.6.0 渠道表与 `channels/` 目录均无 rss（F-108） |
| 全网语义搜索 | Exa via mcporter，免 Key | 同上，exa_search 与 mcporter 均已移除（F-106/F-108） |

> 迁移建议：需要订阅源时，让 Agent 直接用网页读取或你自己的 RSS 客户端；需要全网搜索时，用 Agent 自带搜索或 `web` 渠道。不要把"16 个平台"当成当前能力清单（见 [概念 05](../concepts/05-version-drift-and-channel-matrix.md)）。

## 调用方式：人说意图，Agent 选后端

| 你说 | Agent 自选的底层 |
|------|----------------|
| "帮我看看这个链接 https://…" | `curl r.jina.ai/URL` 或 `agent-reach read` |
| "GitHub 上搜一下最火的 XX 项目" | `gh search repos …` |
| "这个 YouTube 视频讲了啥" | `yt-dlp` 抽字幕 |
| "B站搜几个 XX 视频" | `bili search …` |
| "V2EX 上大家在聊什么" | `agent-reach v2ex hot` |

动手前 Agent 会先看渠道状态，确认当前后端可用（F-040/F-111）。渠道不认识时先跑 `agent-reach channels` 看动作与参数。

## 自查清单

- [ ] `agent-reach doctor --text` 中 5 个默认渠道无 missing/timeout
- [ ] B站要用字幕时，已完成扫码登录
- [ ] 需要转文字的渠道，Key 已由本人配置（不在对话里传 Key）
- [ ] 行为与预期不符时先看 `doctor --text` / `check <渠道> --text`，而不是直接重试

## 下一步

- [示例 02：登录态渠道与 Cookie 安全](02-login-channels-and-cookie-safety.md)
- [概念 01：14 渠道三级矩阵](../concepts/01-capability-layer-architecture.md)
