---
okf_version: "0.2"
type: bundle
title: "《深入理解 AI Agent》开源书：李博杰 ai-agent-book 核验导览"
description: "李博杰《深入理解 AI Agent：设计原理与工程实践》开源教材博文核验——Agent=LLM+上下文+工具公式、Harness工程、10章地图与实验体系（94/95/109三口径勘误）、工作流5图、13→15语言、Apache-2.0免费获取"
tags: [AI Agent, 开源书, 李博杰, Pine AI, ai-agent-book, Harness, 工作流模式, MCP, 多Agent, 博文转化]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T21:00:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-16T21:00:00+08:00" }
status: stable
stale_after: 2026-11-30
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/XL9UWNcrC9BwQw8BbShHOA
    title: 《2.8万Star！AI Agent 教材来了：10章94实验，中科大博士免费开源》（杰克王聊AI，2026-08-01）
  - id: github-repo
    url: https://github.com/bojieli/ai-agent-book
    title: 《深入理解 AI Agent》开源主仓库（main 分支 2.0）
  - id: github-api
    url: https://api.github.com/repos/bojieli/ai-agent-book
    title: GitHub 仓库元数据 API（2026-09-16 核验）
  - id: snapshot
    url: https://github.com/bojieli/ai-agent-book/blob/8c2b7f55e4bd2e5348b15b823dd23a179ef3decf/README.md
    title: 博文发布前 9 小时仓库快照（2026-07-31，commit 8c2b7f5）
  - id: author-site
    url: https://ring0.me/whoami/
    title: 李博杰官方个人页
---

# 《深入理解 AI Agent》开源书：核验导览

> **性质声明**：本知识包基于"杰克王聊AI"2026-08-01 推荐博文转化，是对开源书 [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book) 的**资源盘点/技术综述，非源码教程**。**本包无 examples/ 目录**——博文虽给出获取与运行命令，但公众号作者未报告实测、无输入输出展示（操作可复现性两问 Q2 为否），运行方式在 [03 章节地图](concepts/03-chapter-map-and-experiments.md) 中以概念文档承载。作者观点已显式标注。

> **⏱️ 双时点提示**：博文数字截止 **2026-07-31**（书为 1.4 版）；本包核验于 **2026-09-16**（书已升级 2.0 版）。实验总数、语言数、Python 版本、章节结构均已变化，正文一律双口径并列。仓库侧数字请以 GitHub main 分支为准。

## 信源说明

| 信源 | 类型 | 用途 |
|------|------|------|
| [杰克王聊AI博文](https://mp.weixin.qq.com/s/XL9UWNcrC9BwQw8BbShHOA) | 主信源（第三方公众号推荐文，2026-08-01） | F-001~F-024 博文事实与观点 |
| GitHub 仓库 + API | 权威一手信源（2026-09-16） | 仓库元信息、2.0 现状、章节与实验数、资源链接核验 |
| commit 8c2b7f5 快照 | 博文发布时点一手信源（2026-07-31 22:47） | 博文时点口径还原与勘误判定 |
| ring0.me / 01.me | 作者官方站点 | 作者身份、Pine AI 业务、2.0 发布时间核验 |

## 知识结构

本知识包含 **5 篇概念文档**和 **2 篇信源参考**：

```
ai-agent-book/
├── index.md（本文件）
├── concepts/
│   ├── index.md
│   ├── 00-book-and-author.md           书籍卡片、双时点指标、作者档案、获取渠道
│   ├── 01-core-formula.md              核心公式、Harness、三维对比表
│   ├── 02-workflow-patterns.md         工作流模式（3 图/5 图/2.0 二分）
│   ├── 03-chapter-map-and-experiments.md  10 章三口径地图、实验体系、版本迁移
│   └── 04-community-and-learning.md    翻译生态、增长、观点分层、时效导览
├── references/
│   ├── index.md
│   ├── article-source.md              F-001~F-041 完整事实登记（41 条）
│   └── verification.md                 18 项 P0/P1 核验报告 + 6 条勘误
└── log.md
```

## 分层导航

### 概念文档（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [00-book-and-author](concepts/00-book-and-author.md) | 书籍卡片；Star 27,979（2026-07-31）→47,817（2026-09-16）双时点；Apache-2.0；李博杰履历（中科大少年班/华为天才少年/Pine AI 首席科学家）；三种免费获取渠道 |
| [01-core-formula](concepts/01-core-formula.md) | Agent = LLM + 上下文 + 工具（含 Environment 边界精确版）；Model–Harness 结构与"模型内化/Harness 卸层"；工具三/五类版本差异；现代 Agent 三维对比表原书完整版 |
| [02-workflow-patterns](concepts/02-workflow-patterns.md) | 博文展示链式/并行/Orchestrator 三图；核验仓库实有 5 张 fig1-wf 图（含 routing/evaluator）；2.0 改为工作流（确定性编排）vs 自主 Agent（动态决策）二分 |
| [03-chapter-map-and-experiments](concepts/03-chapter-map-and-experiments.md) | 博文 1.4 / 时点快照 / 2.0 三口径 10 章对照；实验数勘误；✅/📖/🚧 三类实验与外部依赖；uv 命令；1.4→2.0 重组 Mermaid |
| [04-community-and-learning](concepts/04-community-and-learning.md) | 13→15 种社区翻译全名单；增长数据与观点分层；适合谁读；以 main 分支为准的时效导览 |

### 信源参考（references/）

| 文档 | 内容 |
|------|------|
| [article-source](references/article-source.md) | F-001~F-041 完整事实登记（41 条 = 博文 24 + 核验补充 17） |
| [verification](references/verification.md) | 18 项 P0/P1 核验：13✅ + 2❌ + 3⚠️，另 1 项 P2 单源；6 条勘误 |

## 信任与生命周期

- **P0 核验**：18 项 = 13 ✅ + 2 ❌（非核心数字勘误）+ 3 ⚠️（口径/时效），另 1 项 P2 单源
- **勘误要点**：①博文"94 实验"在其发布时点官方口径为 95（且博文自表合计 98），2.0 版为 109；②第 6 章博文写 11、官方为 12；③"四种工作流"实为仓库 5 图、2.0 已改二分叙述；④"每个实验一条命令能跑"以偏概全（实验分三类，含外部仓库/API Key/GPU 依赖）
- **事实总数**：41 条（F-001~F-041），核验补充 17 条；作者观点 2 条显式标注
- **内容敏感度**：公开（微信公开文章 + 公开 GitHub 仓库）
- **失效日期**：2026-11-30（书籍 6 周内经历 1.4→2.0、95→109 实验，迭代极快，到期复核实验数/语言数/Python 版本/新版次）

## 已知边界

1. **博文数字时效**：27,979 star/94 实验/13 语言/Python 3.10+ 均为 2026-07-31~08-01 口径；核验日对应为 47,817 star/109 实验/15 语言/Python 3.11–3.13，引用必须带时点
2. **两处博文硬数字失准**（非核心声明，status 保持 stable）：实验总数差 1、第 6 章差 1，详见 [verification](references/verification.md) 勘误 E1/E2
3. **实验可运行性**：仅 ✅ 类可"配 Key 即跑"；📖 类需自行克隆 22 个外部仓库（固定 SHA），🚧 类尚未完成验收；调模型实验普遍需 API Key
4. **观点/事实分层**："口碑传播而非营销""所有工具都能放进对比表"为公众号作者观点（F-019/F-021）；"底层逻辑变化没那么快"是博文对原书 Harness 主张的转述（F-023/F-038）
5. **版次问题**：博文描述 1.4 版结构（2026-08-01 当代口径，非引用错误）；2.0 版第 6/7/8/9 章已重组，旧 PDF 读者应以 release latest 为准
6. **单源剔除**：博文称作者为"中科大 Linux 用户组成员"，官方页未检出，本包不采用（F-040）

## 主题关联

- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md)：跨框架六大架构模式对比——本包是"一本书的公式视角"，该束是"多框架的模式视角"，互为表里
- [book-to-skill](../book-to-skill/index.md)：书籍→Agent Skill 编译器——从"读书"到"把书变成可执行技能"的下游工具
- [agent-communication-protocols](../agent-communication-protocols/index.md)：本书第 4 章 MCP 协议的四层协议栈展开

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
