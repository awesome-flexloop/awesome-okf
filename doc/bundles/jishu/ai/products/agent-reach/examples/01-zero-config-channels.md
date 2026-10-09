---
okf_version: "0.2"
type: Example
title: "零配置渠道实操：网页、GitHub、YouTube、B站、Exa、RSS、V2EX"
description: "默认激活 6 个零配置渠道底层命令（网页/GitHub/YouTube/Exa/RSS/V2EX）与 B站 bili-cli 免登录实操，附人说意图 Agent 选后端的调用方式"
tags: [agent-reach, zero-config, jina-reader, github, youtube, bilibili, exa, rss, v2ex]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-08T12:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
---

# 示例 01：零配置渠道实操

> 默认激活 6 渠道的命令均经 README/SKILL 命令族核验（F-067）。实际使用时通常不需要手敲——对 Agent 说意图即可，这里列出底层命令是为了让你知道 Agent 在调什么、出问题时能自查。

## 口径回顾：6 个默认激活 + 1 个免登录装好即用

官方**默认只激活 6 个零配置渠道**（F-061）：任意网页、YouTube、GitHub、RSS/Atom、Exa 全网搜索、V2EX。博文正文把 B站也列入零配置名单（共 7 个），官方口径是 B站"**装好即用：搜索+详情 bili-cli 无需登录**"——免登录但不属于默认激活的 6 个，需 bili-cli 就位（F-029/F-061）。本文先讲 6 个默认渠道，再单列 B站。

## 1. 任意网页：Jina Reader

```bash
curl -s "https://r.jina.ai/https://example.com/article"
```

把目标 URL 接在 `https://r.jina.ai/` 后，返回渲染后的正文文本（F-048/F-067）。Agent 侧的说法是"帮我看看这个链接：https://..."，由其自行拼装（F-042）。加 `-s` 是 curl 静默参数，官方 README 示例为不带 `-s` 的 `curl https://r.jina.ai/URL`，两者语义一致。

## 2. GitHub：gh CLI

读公开仓库与搜索走 GitHub 官方 `gh` CLI（F-048/F-067）：

```bash
gh search repos "ai agent" --sort stars --limit 10   # 按 star 排序搜仓库
gh repo view owner/repo                               # 查看某仓库详情（README/元信息）
```

公开信息无需登录；更高频/私有场景才需要 `gh auth login`（博文提到的"GitHub 认证配置坑"主要指这一步，F-008）。

## 3. YouTube：yt-dlp 抽字幕

```bash
yt-dlp --write-sub --skip-download "https://www.youtube.com/watch?v=VIDEO_ID"
```

只下载字幕、不下载视频（F-048）。博文点出的实际坑是要区分**自动生成字幕**与**手动字幕**（F-008），可加 `--list-subs` 先看该视频有哪些字幕轨。注意 yt-dlp 的 B站用途已在 2026-06 因 412 退役（B站改用 bili-cli，见下节与 [概念 01](../concepts/01-capability-layer-architecture.md)），但 YouTube 字幕仍是 yt-dlp。

## 4. 全网语义搜索：Exa via mcporter（免 Key）

Exa 搜索以 **MCP 方式经 mcporter 接入，不需要 API Key**（F-025/F-067）。这是 6 个零配置渠道里唯一的"AI 语义搜索"。Agent 侧直接说"帮我全网搜一下 XXX 的最新资料"即可；底层不需要你手动申请 Exa key。

## 5. RSS/Atom：feedparser

订阅源解析走 feedparser（F-015/F-067）。给 Agent 一个 RSS/Atom 链接，它可以拉取最新条目并汇总——零认证、零 Key。

## 6. V2EX：直连

V2EX 社区内容为零配置渠道之一（F-029/F-060，渠道文件 `v2ex.py` 实际存在 F-063）。对 Agent 说"看看 V2EX 上关于 XX 的讨论"即可，无需登录。

## 7. B站：免登录，但需 bili-cli 就位（非默认激活）

```bash
bili search "AI 教程" --type video -n 5      # 搜视频，返回 5 条
```

- 能力：搜索 + 视频详情，**无需登录**（F-029/F-061）。
- 上游是 **bili-cli**（不是 yt-dlp）：2026-06 B站风控对 yt-dlp 全面返回 412 后，bilibili 渠道首选切为 bili-cli，备选 OpenCLI ▸ 搜索 API（F-024/F-064）。
- `-n 5` 为限量参数；同命令族中 search-twitter 默认 `-n 10`（F-067）。
- 如果 `doctor` 报 bili 后端 `missing`，对 Agent 说"帮我配 B站"或按 doctor 输出安装 bili-cli 即可（F-046）。

## 调用方式：人说意图，Agent 选后端

零配置渠道的设计用法不是记命令，而是（F-042）：

| 你说 | Agent 自选的底层 |
|------|----------------|
| "帮我看看这个链接 https://…" | `curl r.jina.ai/URL` |
| "GitHub 上搜一下最火的 XX 项目" | `gh search repos …` |
| "这个 YouTube 视频讲了啥" | `yt-dlp` 抽字幕后阅读 |
| "B站搜几个 XX 视频" | `bili search …` |
| "全网找找 XX 的资料" | Exa via mcporter |

动手前 Agent 会先看 `doctor --json` 的 `active_backend`，确认该渠道当前后端可用（F-021/F-040）。

## 自查清单

- [ ] `agent-reach doctor` 中 6 个默认渠道无 missing/timeout（见 [示例 00](00-install-and-doctor.md)）
- [ ] B站如要用，已装好 bili-cli 且 doctor 显示 bilibili active_backend 为 bili-cli
- [ ] 命令行为与预期不符时，先 `agent-reach doctor --json` 看对应渠道实际后端，而不是直接重试

## 下一步

- [示例 02：登录态渠道与 Cookie 安全](02-login-channels-and-cookie-safety.md)
- [概念 01：16 渠道三档全景](../concepts/01-capability-layer-architecture.md)
