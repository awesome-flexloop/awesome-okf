---
okf_version: "0.2"
type: Concept
title: "书籍与作者：《深入理解 AI Agent》开源教材档案"
description: "李博杰《深入理解 AI Agent：设计原理与工程实践》书籍卡片——Apache-2.0开源、GitHub双时点指标、作者学术与产业履历、Pine AI背景、三种获取渠道"
tags: [AI Agent, 开源书, 李博杰, Pine AI, ai-agent-book, 教材, Apache-2.0]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T21:00:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-16T21:00:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/XL9UWNcrC9BwQw8BbShHOA
    title: 杰克王聊AI博文（2026-08-01）
  - id: github-api
    url: https://api.github.com/repos/bojieli/ai-agent-book
    title: GitHub 仓库元数据 API
  - id: author-site
    url: https://ring0.me/whoami/
    title: 李博杰官方个人页
---

# 书籍与作者：开源教材档案

> **双时点提示**：本文所有数字均标注口径时点。博文数字截止 **2026-07-31**（F-008）；核验日数字为 **2026-09-16** GitHub API 实时值（F-024）；书籍内容结构已从博文时代的 1.4 版升级为 2.0 版（F-028/F-041）。

## 一、书籍卡片

| 项目 | 内容 |
|------|------|
| 书名 | 《深入理解 AI Agent：设计原理与工程实践》（英文发行名 AI-Agents-in-Depth）（F-004） |
| 作者 | 李博杰（Bojie Li），GitHub @bojieli（F-004） |
| 仓库 | https://github.com/bojieli/ai-agent-book（F-022/F-024） |
| 开源协议 | **Apache License 2.0**（允许自由分发；博文未提协议，核验补充，F-024） |
| 内容形态 | 10 章正文 + 配图（SVG）+ 配套实验，正文源码在 `book/`（introduction + chapter1~10 + 后记），PDF/EPUB 由 release 流水线构建（F-039） |
| 实验规模 | 博文时点官方口径 **95 个**（博文写 94，见勘误 E1）；2.0 版 **109 个**（F-025/F-029） |
| 语言版本 | 博文时点 13 种；核验日 15 种社区翻译（F-020/F-029） |
| 在线阅读 | https://bojieli.github.io/ai-agent-book/（GitHub Pages，多语言切换、章节折叠、全文搜索、实验直达，main 推送自动重建，F-036） |

### 仓库指标（双时点）

| 指标 | 博文时点（2026-07-31，F-008） | 核验日（2026-09-16，F-024） |
|------|------------------------------|----------------------------|
| Star | 27,979（标题口径"2.8 万"） | 47,817 |
| Fork | 2,957 | 5,328 |
| 创建时间 | — | 2025-09-09（博文"2025 年 9 月上线"✓，F-009/F-024） |
| 其他 | GitHub 全球 Trending 日榜（README 挂 Trending Project of the Day 徽章，F-036） | 默认分支 main，主语言 Python，has_pages=true |

> 第三方旁证：CSDN 2026-08-06 文章独立记载"27k+ Star、16 天 1.6 万星"，与博文时点量级吻合（F-037）。

## 二、作者档案（经官方页核验）

李博杰的身份博文只给了三句话，核验其官方个人页（ring0.me）与 2026 版 CV 后完整画像如下（F-031）：

| 维度 | 档案 |
|------|------|
| 现职 | **Pine AI 首席科学家**（2025-01 至今） |
| 教育 | 中国科学技术大学**少年班**本科（2010-2014）；中科大-微软亚洲研究院联合培养博士（2019，导师陈恩红教授、张霖涛博士） |
| 产业经历 | 2019 年华为首批 TopMinds"天才少年"（2019-2023），Unified Bus（UB）核心架构师，带全球 25 人团队做下一代数据中心互连；此前联合创立隐身 AI 创业公司（2023-08—2024-10，CTO） |
| 学术记录 | SIGCOMM/SOSP/NSDI/PLDI 一作论文（ClickNP、KV-Direct、SocksDirect、1Pipe 等）；ACM 中国优秀博士学位论文奖、微软学者奖学金 |
| 个人站点 | 博客 01.me（F-006）、whoami 在 ring0.me |
| 博文未提的细节 | 少年班出身、华为天才少年、系统/网络方向顶级会议论文——解释了本书"架构定义+工程实践"而非框架 API 罗列的写法来源 |

> 博文另称其为"中科大 Linux 用户组成员"（F-005），官方个人页与 CV 均未检出该表述（F-040），**仅博文单源，本知识包不予采用**。

## 三、Pine AI：作者的产业实验场

博文强调"这本书不是象牙塔里写出来的"，依据是作者在 Pine AI 的产品实践（F-007）。核验结果（F-032）：

- Pine AI（19pine.ai）做**替用户真实打电话**的全自主语音 Agent：协商账单、取消订阅、解决争议、预约——双 LLM 语音架构（Communicator 实时对话 + Reasoner 后台策略），与书中第 9 章（1.4 版）语音/实时交互内容直接呼应。
- 公司为 Series A 阶段（融资 2500 万美元，Fortwest 领投）。
- 其 CV 自述"93% 谈判成功率、累计为消费者节省超 3700 万美元"——**作者 CV 自述口径，非第三方审计**，不作为独立成效事实引用。

## 四、获取渠道（三渠道均与官方 README 逐字核对，F-022/F-025）

```bash
# 1. 在线阅读（免费，多语言、全文搜索）
#    https://bojieli.github.io/ai-agent-book/

# 2. 下载中文 PDF（release latest 始终指向 main 最新构建）
#    https://github.com/bojieli/ai-agent-book/releases/download/latest/AI-Agents-in-Depth-zh-CN.pdf
#    另有 EPUB 与 14 个社区译本的 PDF/EPUB

# 3. 克隆全书（含配套实验代码）
git clone https://github.com/bojieli/ai-agent-book
```

全书 Apache-2.0 免费开源；也可用 pandoc + xelatex（ElegantBook 文档类）自行从 `book/` 编译 PDF（F-039）。

## 五、本包读法

- 想快速理解全书思想骨架 → [01 核心公式](01-core-formula.md) 与 [02 工作流模式](02-workflow-patterns.md)
- 想按章学习/跑实验 → [03 章节地图与实验体系](03-chapter-map-and-experiments.md)
- 关心社区生态与时效 → [04 社区生态与学习指引](04-community-and-learning.md)
- 数字与表述的可信度细节 → [核验报告](../references/verification.md)
