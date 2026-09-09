---
okf_version: "0.2"
title: "2026免费大模型API汇总：40家平台免费额度全览"
description: "知乎博文《2026最新免费大模型API汇总》经过OKF v0.2七阶段工作流转化，覆盖国内23家+国际17家免费大模型API平台，含完整免费额度、速率限制与选型指南。"
source:
  - id: zhihu-article
    type: blog-article
    title: "2026最新免费大模型API汇总｜海量免费Token，学习够用一整年"
    author: 蹦豆儿
    url: https://zhuanlan.zhihu.com/p/2050524686992380835
    published: 2026-06-17
status: flagged
stale_after: 2026-08-17
---

# 2026免费大模型API汇总：40家平台免费额度全览

> **⚠️ 状态：`flagged`** — 博文核心推荐受影响：GitHub Models 已于 2026-07-30 彻底退役（F-145~F-150），OpenAI Free Tier $5 赠金已取消（F-055）。完整勘误详见 [references/verification.md](references/verification.md)。

2026年，国内外已有大量大模型API提供免费额度，足以满足个人学习与原型开发需求。本文覆盖国内23家（无需翻墙）与国际17家平台，逐一列出免费额度、速率限制、代表模型与认证要求，并附分场景选型指南。

## 核心发现（勘误摘要）

| 平台 | 博文口径 | 实际情况 | 影响 |
|------|---------|---------|------|
| GitHub Models | 免费可用，高级模型10 RPM/50 RPD | **已彻底退役（2026-07-30）** | ❌ 核心推荐失效 |
| OpenAI Free Tier | $5赠金+GPT-4o免费 | $5赠金已取消（2023年底），仅剩GPT-3.5 Turbo 3 RPM | ⚠️ 额度大幅缩水 |
| 小米MiMo | 7亿Token | 已升级至380亿Credits（Pro档，2026-05-27） | ✅ 超额完成 |
| Google AI Studio Gemini 2.5 Pro | 400 RPD | 实际50 RPD（非400 RPD） | ⚠️ 限额夸大8倍 |
| 中国移动MoMA | 9000万Token | 官方宣传2500万Token（9000万可能为活动叠加总额） | ⚠️ 口径存疑 |

详见 [references/verification.md](references/verification.md)。

## 内容导航

- [平台全景概览与关键发现](concepts/00-platform-overview.md)
- [国内23家平台详解](concepts/01-domestic-platforms.md)
- [国际17家平台详解](concepts/02-international-platforms.md)
- [选型指南与避坑建议](concepts/03-selection-guide.md)
- [参考与附件](references/index.md)

```{toctree}
:maxdepth: 2

concepts/index
references/index
log
```
