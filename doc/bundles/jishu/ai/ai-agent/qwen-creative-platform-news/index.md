---
okf_version: "0.2"
type: bundle
title: "千问创作平台多Agent协同：AI短剧剧组"
description: "阿里千问创作平台多Agent协同功能开测资讯速报——5个Agent组成虚拟剧组（策划/编剧/视觉/分镜/成片），底层Wan 3.0+Qwen-Image 3.0 Pro，书旗ManClaw漫剧Agent，导演视角解读"
tags: [千问, Qwen, Wan 3.0, 多Agent, AI短剧, AI漫剧, ManClaw, Seedance, 书旗, 资讯速报]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T23:30:00+08:00" }
status: stable
stale_after: 2026-10-31
sources:
  - id: wechat-article-luodao
    resource: https://mp.weixin.qq.com/s/7QNQ3_CpIya3MR45Twq07g
    title: 《阿里做了个AI短剧团队，不是工具》（微信公众号"罗导聊Ai"，作者"罗富平导演"，2026-08-27 17:25，原创）
  - id: cls-exclusive-2465003
    resource: https://www.cls.cn/detail/2465003
    title: 财联社/科创板日报：千问创作平台多Agent协同小范围测试（2026-08-26）
---

# 千问创作平台多Agent协同：AI短剧剧组

> **⚠️ 性质声明**：本 bundle 为**资讯速报类知识包**，记录 2026 年 8 月底阿里千问创作平台多Agent协同功能开测这一单一产品发布事件。信息源自微信公众号"罗导聊Ai"博文及财联社/科创板日报等权威媒体核验。博文作者为影视导演，第四章"导演视角三句大实话"为**作者专业观点**（F-031~F-034），非阿里官方表态。核验中发现博文存在 3 处需更正/标注的问题（Wan 上一代版本号、Arena 排名时效性、小云雀表述简化），已在 [references/verification.md](references/verification.md) 中如实记录。

2026 年 8 月 27 日，阿里千问创作平台上线多Agent协同功能并进入小范围测试（F-003）。该功能将 AI 短剧/漫剧创作流程拆解为五个专业Agent——策划、编剧、视觉、分镜、成片——模拟真实剧组分工协作（F-005），底层接入 Wan 3.0 视频模型和 Qwen-Image 3.0 Pro 文生图模型（F-008、F-015）。同期，阿里书旗团队推出垂直漫剧创作Agent ManClaw，搭载字节跳动 Seedance 2.0 模型，4-7 分钟可出漫剧初版（F-018、F-022）。

本知识包以导演视角的博文为事实基础，结合财联社、阿里云官方文档、国家广电总局等权威来源核验，梳理这一多Agent协同创作产品的核心能力、底层模型规格与行业背景。

---

## 信源说明

本知识包采用**双信源**结构：

| 信源 | 类型 | 覆盖范围 |
|------|------|---------|
| 微信公众号"罗导聊Ai"博文 | 主信源（博文） | F-001 ~ F-034（博文全部事实与作者观点） |
| 财联社/阿里云官方/广电总局/半年报等 | 核验信源 | 8 项核验结论 + F-035 ~ F-039 核验补充事实 |

核验中发现博文存在 3 处需更正或标注的问题：①Wan 上一代版本号应为 Wan 2.7 而非 Wan 2.5（F-039）；②Qwen-Image 3.0 Pro 的 Arena.ai 排名有时效性，综合榜中国第一已被字节 seedream 超越（F-038）；③"小云雀是《被裁掉的女孩》幕后工具"表述过于简化（F-036）。完整核验报告见 [references/verification.md](references/verification.md)。

---

## 📚 知识结构总览

```
qwen-creative-platform-news/
├── concepts/              # 核心概念文档（1篇）
│   └── 00-multi-agent-creative-team.md   # 多Agent剧组协同
├── references/            # 信源登记簿（2篇）
│   ├── article-source.md  # F-001~F-039 事实完整登记
│   └── verification.md    # 8项核验结论与勘误说明
├── index.md               # 本文件
└── log.md                 # 生成日志
```

> 本 bundle **不设 examples/ 目录**——内容为资讯速报，无可运行代码示例。这是"资讯速报"骨架的首次验证应用：concepts 仅 1 篇，stale_after 缩短至约 2 个月。

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [多Agent剧组协同](concepts/00-multi-agent-creative-team.md) | 5个Agent分工（策划/编剧/视觉/分镜/成片）+ Wan 3.0规格（30秒/混合输入/双版本）+ Qwen-Image 3.0 Pro + ManClaw漫剧Agent（Seedance 2.0/4-7分钟/5万IP）+ 行业背景与监管 |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [博文信源事实清单](references/article-source.md) | F-001 ~ F-034 博文事实完整登记（分元信息/产品发布/模型规格/ManClaw/行业竞争/监管/作者观点七类），F-035 ~ F-039 核验补充与勘误 |
| [核验报告](references/verification.md) | 8 项核验逐项结论表（5✅ + 3⚠️），权威来源 URL，3 项勘误详解 |

事实编号索引说明见 [references/index.md](references/index.md)。

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2026-08-27 发布的博文与 2026-08-28 完成的轻量核验生成
- **覆盖事实**：共 39 条事实（F-001 ~ F-034 来自博文，F-035 ~ F-039 为核验补充）
- **核验情况**：8 项声明经 WebSearch 核验，5 项通过，3 项发现需更正或标注（Wan 版本号、Arena 排名时效性、小云雀表述简化）
- **status**：stable — 产品发布事件为已发生事实
- **stale_after**：2026-10-31 — 资讯速报类知识包生命周期约 2 个月；千问创作平台与 ManClaw 均处于内测阶段，产品能力可能快速迭代
- **方法论链路**：R（事实采集）→ I（洞察提炼）→ E（信源先行成文）→ V（核验），详见 [log.md](log.md)

### 已知边界

1. **导演观点性质**：博文作者为 25 年影视导演（F-001），第四章"导演视角三句大实话"（F-031~F-034）为**作者专业观点**，包括"大厂做基础设施非卖铲子""多Agent方向正确""导演不会失业"等判断，非阿里官方表态。
2. **Wan 上一代版本号勘误（F-039）**：博文称"Wan 2.5 只能 15 秒"有误，上一代版本号应为 **Wan 2.7**（阿里云国际博客确认）。Wan 3.0 的 30 秒时长、10图/5视频/5音频上限、PDF/网页/PPT 输入、Standard/Prime 双版本、7 折优惠均核验通过。
3. **Arena 排名时效性（F-038）**：博文称 Qwen-Image 3.0 Pro"在 Arena.ai 中文模型排名第一"不够准确。8 月 5 日上线初期确为中国模型第一，但 8 月 10 日综合榜已被字节 seedream-5.0-pro 超越；商业设计分类榜仍为第一。引用时须标注时点。
4. **ManClaw 搭载竞品模型（F-035）**：ManClaw 搭载的是**字节跳动 Seedance 2.0** 视频模型而非阿里自家 Wan 3.0，阿里书旗团队在漫剧场景选用了竞品模型。
5. **小云雀表述简化（F-036）**：博文称字节"小云雀"是《被裁掉的女孩》幕后工具，准确说法是该剧**第二季**使用小云雀 Seedance 2.5 制作，第一季涉及 LibTV 等多平台协作。
6. **产品内测阶段**：千问创作平台多Agent协同与 ManClaw 均处于小范围测试/内测阶段（F-003、F-018），功能与定价可能调整。Wan 3.0 Standard 7 折优惠期为 8 月 24 日至 9 月 23 日（F-012）。
7. **监管新规即将实施（F-030、F-037）**：《微短剧发展管理办法》于 2026 年 9 月 1 日施行，AI 微短剧纳入三类分级备案，须每集添加 AI 提示标识，AI 微短剧投资阈值单独设定（一类≥80万/二类30-80万/三类<30万）。

---

**本知识包共收录 4 个内容文档（1 个概念 + 2 个信源 + 根索引），外加 2 个子目录索引与生成日志，合计 7 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
