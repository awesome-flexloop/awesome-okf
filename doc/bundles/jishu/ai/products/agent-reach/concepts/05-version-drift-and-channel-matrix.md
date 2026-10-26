---
okf_version: "0.2"
type: Concept
title: "版本漂移与渠道矩阵：从 16 到 14"
description: "拆解 Agent Reach 渠道数的三代口径（v1.5 tag 13 / main 16 / v1.6.0 14），给出 5 默认 + 6 可选 + 3 实验矩阵、退役渠道与 1.5→1.6 迁移清单"
tags: [agent-reach, channels, version-drift, platform-matrix, migration]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-26T11:15:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
  - id: github-api
    url: https://api.github.com/repos/Panniantong/Agent-Reach
  - id: readme-v150
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/v1.5.0/README.md
---

# 版本漂移与渠道矩阵：从 16 到 14

> 事实层 + 判读规则。本文回答一个具体问题：为什么同一篇介绍里是"16 个平台"，官方 README 却只有 14 个？答案不是谁抄错，而是**渠道数本身随版本变**。
> 如果你只想记一件事：**引用平台数必须同时给出版本与时点**。

## 1. 三代口径，三个数字

| 时点/来源 | 数字 | 数的是什么 | 依据 |
|-----------|------|-----------|------|
| v1.5.0 tag（2026-06-11） | 13 | `agent_reach/channels/` 去掉 2 个框架文件后的渠道模块数 | F-106 |
| main@2026-10-08（首版核验） | 16 | 20 个 py 文件 = 3 框架 + 17 实现，其中 mcporter 是 Exa 的承载，对外 16 渠道 | F-107 |
| main@2026-10-26（v1.6.0） | 14 | 17 个 py 文件 = 3 框架 + 14 渠道实现；README 明确 5 默认 / 6 可选 / 3 实验 | F-108 |

三个数字都"对"，但分别属于 tag、未发版的 main、和最新 main。文章写于 2026-10-17，正处在 main 有 16 个实现的窗口内，所以"16"有代码依据；但**它的表格只列了 13 行**（缺 Exa、Facebook、Instagram），标题与表格就已经对不上（F-086/F-087）。

## 2. 现行 14 渠道矩阵

```mermaid
flowchart TB
    R[agent-reach 渠道] --> D[默认 5<br/>装好即用]
    R --> O[可选 6<br/>说一句"帮我加 X"]
    R --> E[实验 3<br/>反爬更严，可能随时失效]
    D --> D1[bilibili · v2ex · github · youtube · web]
    O --> O1[xiaohongshu · xueqiu · boss · xiaoyuzhou · linkedin · reddit]
    E --> E1[twitter · facebook · instagram]
```

| 档位 | 渠道 | 能做什么 | 需要什么 |
|------|------|---------|---------|
| 默认 | bilibili | 搜索、视频信息、热门、字幕 | 无；字幕需登录（扫码） |
| 默认 | v2ex | 热门、节点、帖子与回复、用户 | 无 |
| 默认 | github | 搜仓库、读仓库/README、读 issue 与 PR | 无 |
| 默认 | youtube | 视频信息、搜索、字幕、语音转文字 | 无；转文字需 Groq 或 OpenAI Key |
| 默认 | web | 网页搜索、网页阅读（保底） | 无 |
| 可选 | xiaohongshu | 搜笔记、读正文、看评论 | 登录 |
| 可选 | xueqiu | 实时行情、搜股票、热帖、热股 | 行情免登录；热帖热股需登录 |
| 可选 | boss | 搜职位、读 JD | 登录 |
| 可选 | xiaoyuzhou | 播客转文字 | Groq Key |
| 可选 | linkedin | 搜职位、读职位详情 | 公开职位免登录；站内搜索需登录 |
| 可选 | reddit | 搜帖子、读正文、评论、版块 | 登录 |
| 实验 | twitter | 搜推文、用户资料、用户推文、读推文串 | 登录 |
| 实验 | facebook | 搜索、主页资料 | 登录 |
| 实验 | instagram | 搜用户、主页资料、用户帖子 | 登录 |

> 依据：v1.6.0 README 平台表（F-108）。"实验"档是官方自己标注的"能用但平台反爬更严、可能随时失效"——这类渠道不适合作为生产依赖。

## 3. 退役与新增：数字变化的真实原因

- **退役**：`rss`（feedparser）与 `exa_search`（全网语义搜索，经 mcporter）在 v1.6.0 的渠道列表与实现中都不再出现；项目在 v1.4.2 起就以"诚实瘦身：移除失修渠道"为版本主题。
- **新增/前移**：`boss`、`facebook`、`instagram` 在 v1.5.0 tag 里还没有文件，但在 main 与 v1.6.0 中已进入实现与平台表。这一增一减，把 16 变成了 14。
- **口径升级**：分级从"装好即用 / 配置后解锁"改成"默认 / 可选 / 实验"，新增的"实验"档其实是**风险披露**——承认有一批渠道随时可能坏。这比笼统写"支持 N 个平台"更诚实。

## 4. 读平台数的三条规则

1. **带版本**：写"v1.6.0 支持 14 个渠道"，不要写"支持 16 个平台"。
2. **带时点**：Star、渠道数、release 数都是动态值；引用格式建议"102,508（2026-10-26）"。
3. **数实现，不数宣传**：以 `channels/` 目录的渠道模块数与 README 平台表交叉验证；两者不一致时，以代码目录为准并注明差异（本次即 17 文件 − 3 框架 = 14）。

## 5. 从 1.5 迁到 1.6 的检查清单

```text
[ ] 确认当前版本：agent-reach version（1.6+ 输出 JSON；1.5 输出纯文本一行）
[ ] 装 uv（如缺）：官方脚本；Windows 用 powershell 安装脚本
[ ] uv tool install --force <latest release zip>
[ ] 新开 shell，再查 agent-reach version 是否为 JSON
[ ] agent-reach setup（保留 ~/.agent-reach/config.yaml，移除旧程序，刷新 skill）
[ ] 原样展示 installation_report.markdown，按 user_actions 逐条处理
[ ] 复核渠道集：默认 5 是否齐全；需要的小红书/雪球/BOSS 是否补上
[ ] 回归一条真实查询（如 agent-reach read <链接>），确认 ok:true
```

> 迁移期最容易踩的两个坑：一是沿用 `pipx`/`pip` 的旧命令（1.6 统一走 uv）；二是以为 `doctor` 还输出人读文本（1.6 起默认 JSON，人读要 `--text`）。依据 F-109/F-111。

## 6. 这条"漂移"给读者的通用启示

- **平台数不是能力指标**：14 个渠道里 3 个是"实验"档，真正的稳定面是默认 5 个。
- **减渠道可以是升级**：移除失修渠道降低了"看起来支持但一用就坏"的假象，属于可信度投资。
- **写作与版本的时间差**：一篇 10-17 发布的文章，可能描述的是 10-08 的 main；6 天后 1.6 发布，安装器全换。**读二手技术文章时，先看它的写作日期与所指版本。**

## 阅读导航

- 机制本身（有序后端、active_backend）：[01 · 能力层架构](01-capability-layer-architecture.md)
- 版本漂移的核验证据：[references/verification-02.md](../references/verification-02.md)
- 团队如何锁版本：[04 · 团队落地](04-team-rollout-and-compliance.md)
- 安装实操：[示例 00](../examples/00-install-and-doctor.md)
