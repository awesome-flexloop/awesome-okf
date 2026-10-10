---
okf_version: "0.2"
type: Concept
title: "核心理念与项目定位"
description: "answer-me-with-html 的核心哲学『让模型写它擅长的内容，把排版布局画图这些机械活交给程序』，以及 Karpathy 的人类跟不上模型输出的观察"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/A-9ViZO69NJ30ZTsofjYeQ
    title: "开源星探 2026-10-06 公众号文章"
  - id: github
    url: https://github.com/QingYunA/answer-me-with-html
    title: "answer-me-with-html 仓库 README"
  - id: karpathy-x
    url: https://x.com/karpathy/status/2105819303471976479
last_modified: 2026-10-10
status: draft
stale_after: 2026-12-31
---

# 核心理念与项目定位

## 一句话哲学

**让模型写它擅长的内容，把排版、布局、画图这些机械活交给程序**。[博客文章](https://mp.weixin.qq.com/s/A-9ViZO69NJ30ZTsofjYeQ) 用一句极简表达概括了 answer-me-with-html 的全部立意（F-003）。它**不是一个独立的 Web App**，也不是一个让你写 Prompt 的网站，而是一个**装在 Agent 里的 Skill**（F-002）。

## 背后的观察：人类跟不上模型输出的长度

[Karpathy 在 X 上的帖子](https://x.com/karpathy/status/2105819303471976479)（F-001）指出：当 LLM 的输出越来越长，跟不上它反而是**我们自己**——不是模型不够强，而是人类的阅读带宽没有随模型 token 吞吐同步变宽。仓库 README 将其重述为「keeping up with their output becomes the hard part」：**人类需要的不是更多的字，而是更好的呈现方式**。「更多字」在 token 成本与阅读载荷上是同一件事，真正的解法是改变信息的载体形态。

## 为什么不用「直接让模型写 HTML」？

模型的输出瓶颈在**输出 token**：要让模型手写一个完整页面，它必须逐行敲出 CSS、每一个包裹 `div`、每一个 SVG 坐标——而输出 token 恰恰是「你盯着等它吐出来」的东西。answer-me-with-html 的思路是：

1. 模型**只写内容**（一段很短的 Markdown 草稿：标题 + 几个组件指令）；
2. 掉头交给随 Skill 内嵌的 CLI 工具 `am`；
3. CLI 承担布局、配色、画图、导出；
4. 约 50ms 后得到可读页面。

这一分工把「模型的输出 token」从排版机械劳动中解放出来，换来的是量级的 token 节省和更快的响应（详见[基准核验](01-mechanics-benchmarks-components.md)）。

## 项目形态速记

| 维度 | 定位 |
|------|------|
| 类别 | Agent Skill（装上后像往常一样提问，Agent 自判「这问题值得做页面」） |
| 支持 Agent | Claude Code、Codex、Cursor、OpenCode（README 另注 installer 支持 70+ agents） |
| 运行环境 | Node.js 20+，无 npm install 步骤，CLI 内嵌在技能目录 |
| 许可证 | MIT（仓库声明） |
| 作者 / 账号 | QingYunA（GitHub）；公众号推手账号「开源星探」 |

## 关键事实引用

本文核心事实编号见 [信源事实清单](../references/article-source.md)（F-001 起因、F-002 定位、F-003 哲学）与 [P0 核验报告](../references/verification.md)。