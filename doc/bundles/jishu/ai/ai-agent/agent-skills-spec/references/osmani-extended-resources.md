---
type: Reference
title: agent-skills 实践案例延伸学习资源
description: Addy Osmani agent-skills 技能库背后的延伸学习资源——Google 工程实践文档、Osmani 著作、《Software Engineering at Google》与 Andrej Karpathy 的 LLM 编程观察。
tags: [agent-skills, osmani, google-engineering, karpathy, learning-resources]
generated: { by: "process:learning-migration merge", at: "2026-09-02" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02" }
status: stable
stale_after: 2027-09-02
sources:
  - id: learning-osmani-resources
    resource: "SpecWeave docs/knowledge/learning/02-agent-engineering-methodology/02-prompt-coding/agent-skills-wiki/07-resources.md"
    title: 延伸学习资源（腾讯云开发者社区 2026-07-08 文章转译）
---

# agent-skills 实践案例延伸学习资源

## 资源 1：Google 工程实践文档（Google Engineering Practices Documentation）

- **类型**：官方文档
- **获取途径**：https://google.github.io/eng-practices/
- **核心学习价值**：
  - Agent Skills 中很多理念（代码评审标准、测试金字塔、基于主干开发）都直接来自 Google 的工程实践
  - 这份文档是 Google 公开的官方工程规范，包含两大部分：
    1. **代码评审指南**：评审什么、怎么评审、评审速度标准、变更大小建议、怎么写评审意见——对应 code-review-and-quality 技能
    2. **测试指南**：测试金字塔、测试大小（小/中/大测试）、Beyonce 规则、测试覆盖率的正确理解——对应 test-driven-development 技能
  - 这是 Agent Skills 背后“为什么这么设计”的源头文档，读了能理解每个实践背后的工程逻辑，而不只是记住“要这么做”

## 资源 2：Addy Osmani 的其他著作——《Learning JavaScript Design Patterns》《Patterns.dev》

- **类型**：开源书籍/博客
- **获取途径**：
  - 《Learning JavaScript Design Patterns》：https://www.patterns.dev/posts/classic-design-patterns/
  - 《Patterns.dev》（现代 Web 设计模式）：https://www.patterns.dev/
  - Addy Osmani 个人博客：https://addyosmani.com/blog/
- **核心学习价值**：
  - Addy Osmani 是 Google Chrome 团队的资深工程师，写了大量工程实践相关的经典著作
  - 《Patterns.dev》覆盖现代 Web 应用的设计模式、性能优化、组件架构、渲染策略——对应 frontend-ui-engineering 和 performance-optimization 技能
  - 他的博客有大量关于代码质量、开发流程、AI 辅助编程的文章，可以跟踪他对 Agent Skills 的后续更新和补充思考
  - 理解他的整体工程思想，能更好地理解 Agent Skills 中每个设计决策的权衡

## 资源 3：《Software Engineering at Google》（Google 软件工程）

- **类型**：书籍
- **获取途径**：O'Reilly 出版，中文译名《Google 软件工程》，纸质书/电子书均可获取
- **核心学习价值**：
  - 这本书是 Google 软件工程文化的集大成之作，由 Google 多名资深工程师合著
  - 深入讲解了：Hyrum 定律（专门有一章）、为什么代码评审是这样的流程、测试为什么按金字塔分层、基于主干开发的权衡、代码即负债的理念、文档和 ADR 的价值——Agent Skills 中几乎所有 Google 文化术语在这本书里都有详细阐述
  - 特别推荐章节：
    - 第 2 章：How to Work Well on Teams（团队协作）
    - 第 7 章：Code Review（代码评审）
    - 第 8 章：Testing（测试）
    - 第 11 章：Documentation（文档）
    - 第 14 章：Deprecation（废弃）——对应 deprecation-and-migration 技能
  - 读完这本书能从“知道 Google 怎么做”升级到“理解 Google 为什么这么做”

## 资源 4：Andrej Karpathy 的 LLM 编程观察与相关项目

- **类型**：博客/开源项目
- **获取途径**：
  - Andrej Karpathy X（原 Twitter）账号：https://x.com/karpathy
  - 相关项目：https://github.com/forrestchang/andrej-karpathy-skills（Karpathy 的 LLM 编程准则）
- **核心学习价值**：
  - Agent Skills 的核心洞察——“AI 会走最短路径跳过关键环节”——与 Karpathy 对 LLM 编程陷阱的观察高度一致
  - 他提出的“给验收标准而非步骤”、“测试驱动让 AI 循环迭代”等理念，在 Agent Skills 中都有体现
  - 对比学习 Karpathy 的准则和 Agent Skills 的 20 个技能，能更好地理解 AI 编程的共性问题和不同的解决方案侧重点
