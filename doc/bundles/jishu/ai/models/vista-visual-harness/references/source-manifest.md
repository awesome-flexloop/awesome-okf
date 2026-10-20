---
type: reference
title: "VISTA 信源登记与采集边界"
description: "量子位 VISTA 博文的信源登记——账号所有权信号、URL、发布与访问时点、可见性判定、采集停止规则，以及全部权威源的坐标与角色。"
tags: [vista, source-manifest, provenance, wechat, arxiv]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-04-20
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ"
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
  - id: project
    url: "https://vista-research.github.io/"
  - id: github
    url: "https://github.com/joshhhhhan/VISTA"
---

# 信源登记与采集边界

## 一、主信源（博文）

| 字段 | 值 |
|------|-----|
| source_id | `blog` |
| URL | `https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ` |
| 标题 | 何恺明团队发布多模态Harness框架 |
| 摘要（og:description） | 给Claude装上视觉Harness，拿下ARC-AGI-3公开集满分 |
| 公众号 | 量子位（页面 `alias` = `QbitAI`；HTML 中 `nick_name` 为 GBK 编码，解码后为"量子位"） |
| 页面 meta author | 关注前沿科技 |
| 作者署名 | henry（发自 凹非寺）——量子位惯用署名 |
| 发布时间 | **2026-10-09 10:41（北京时间）**；页面 `var ct = "1791513671"` = 2026-10-09 02:41:11 UTC |
| 访问时点 | 2026-10-20 |
| 发现渠道 | 用户直接提供 URL |
| 可见性 | 公开可访问，无访问控制 |
| 所有权信号 | 页面 `og:site_name` = Weixin Official Accounts Platform；`alias` = QbitAI；正文标注"量子位 \| 公众号 QbitAI" |
| 采集方式 | WebFetch 直接取得全文（markdown + html 双通道），正文完整，无需绕过任何限制 |
| 状态 | `collected` |

**正文抽取校验**：正文长度与结构完整（含"视觉原生的脚手架""具体实现""实验验证""作者介绍"四节及全部小节），非截断、非拦截页。

## 二、权威信源

| source_id | URL | 角色 | 关键取证 |
|-----------|-----|------|---------|
| `arxiv` | `https://arxiv.org/abs/2610.02200` | 一手事实基准（摘要 + 元数据） | 提交时间 2026-10-01 17:59:45 UTC；作者与机构；许可 CC BY 4.0；Comments 字段记载 2026-08-05 blogpost 版本 |
| `arxiv-html` | `https://arxiv.org/html/2610.02200v1` | 论文全文（§1–§7 + 附录 A/B） | 三组件定义、帧存储、inspect 算法、消融阶梯、局限、多次运行方差 |
| `project` | `https://vista-research.github.io/` | 论文早期版本 blogpost（2026-08-05） | 25 局结果表与回放链接；**不链接 VISTA arXiv**（arXiv 上线晚约 2 个月），数字与论文系统性不同 |
| `github` | `https://github.com/joshhhhhan/VISTA` | 开源实现（MIT License） | 运行要求：Linux x86_64 + Python 3.12 + Docker Engine + Codex CLI 0.145.0 / Claude Code 2.1.220；批量需 tmux；online/competition/offline 三模式 |
| `arc-methodology` | `https://docs.arcprize.org/methodology` | RHAE 官方定义 | 单关得分公式、1.15 倍上限、未通关计 0、关卡序号加权、人类基线为上中位数 |
| `arc-agi3-paper` | `https://arxiv.org/abs/2603.24621` | ARC-AGI-3 数据集构成 | 公开 25 / 半私有 55 / 完全私有 55；私有集与公开集分布外 |
| `anthropic-harness` | `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents` | 博文脉络引用的第三方原文 | 发布 2025-11-26；特性清单 + 进度文件 + git 提交三件套 |
| `arc-scorecards` | `https://arcprize.org/scorecards/` | 成绩独立可追溯性 | Opus 5.0 → RHAE 100；GPT-5.6 Sol → RHAE 99 |

## 三、采集停止规则

- 仅采集无需登录、无验证码、无邀请码即可访问的公开页面。
- 未尝试绕过任何访问控制、频控或反爬机制。
- 未推断或补写任何未在公开源中出现的文章内容。
- ARC-AGI-3 私有/半私有游戏环境不在公开仓库（需 API key 授权），**本束不采集、不复现、不推测其内容**，仅引用 ARC 官方公开的构成数据。

## 四、未采集项

| 项 | 状态 | 原因 |
|----|------|------|
| ARC-AGI-3 私有/半私有游戏环境 | `not-collected` | 不在任何公开仓库，需 API key 授权访问，超出公开采集边界 |
| 论文实验复现结果 | `not-collected` | 需付费模型 API + Docker + 大规模算力；本束转述论文数字，不宣称独立复现 |
| 各基准论文（GameWorld / AI GameStore / BabyVision）方法论细节 | `partial` | 仅核验 VISTA 论文对它们的引用与口径，未独立审查基准本身的方法论质量 |
| GitHub 仓库 548 stars / 34 forks 等计数 | `single-source` | 平台计数随时间变化，本束不将瞬时计数作为稳定事实，仅记录仓库存在性、许可与运行要求 |

## 五、关联

- 事实登记：[article-source.md](article-source.md)
- 核验报告与勘误：[verification.md](verification.md)
- 知识地图：[knowledge-map.md](knowledge-map.md)
