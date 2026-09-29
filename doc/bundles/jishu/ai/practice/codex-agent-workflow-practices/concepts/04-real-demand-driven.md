---
okf_version: "0.2"
type: concept
title: "真实需求驱动：Feature Flag 与 AI Native 流程"
description: "通过更快的部署交付节奏和自动化的用户反馈分析，让 AI 开发成果真正放大——不仅提升开发产能，更要放大最终用户价值"
tags: [codex, feature-flag, ai-native, deployment, user-feedback]
sources:
  - id: blog
    url: https://zhuanlan.zhihu.com/p/2040748661567710711
generated:
  by: "agent:agnes"
  at: "2026-09-09T04:25:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-09T04:30:00+08:00"
status: stable
stale_after: "2026-11-21"
---

# 真实需求驱动：Feature Flag 与 AI Native 流程

## 核心命题

> "如果只是按部就班地完成排期任务，可能很快就会陷入无需求可做的境地。" [作者观点]

要烧掉更多 token，主观能动性最重要。关键不只是开发更快，而是要有**更多真实需求**支撑 agent 工作。

## Feature Flag / Research Preview 策略

### 传统方式的问题

传统分支开发需要各种 pick/patch 的迭代，速度慢。

### Feature Flag 方式的优势

> "Feature flag、'research preview'之类的做法，相比传统的分支开发，各种 pick/patch 的迭代速度要快得多" [F-019](../article-source.md#F-019)

- 新功能默认隐藏，通过 flag 控制开关
- 可以快速部署到正式环境让用户体验
- 避免"完美主义陷阱"：不需要等到功能完全成熟才发布
- 配合 AI 开发节奏：快速试错、快速迭代

### 与垂直切片的配合

Feature flag 与垂直切片拆分天然配合（详见 [06-spec-and-plan](06-spec-and-plan.md)），未完成功能默认隐藏，不影响整体系统稳定性。

## 用户反馈信号自动化

让流程变得更 AI native，关键一环是用户反馈的自动获取与分析：

| 环节 | 传统方式 | AI Native 方式 |
|------|---------|--------------|
| 反馈获取 | 人工收集、整理 | 自动获取用户反馈信号 |
| 反馈分析 | 人工阅读、分类 | Agent 自动分析反馈 |
| 优先级判断 | 人工排期 | Agent 辅助判断优先级 |
| 修复执行 | 人工开发 | Agent 自动修复 |

## 核心原则

> "要让整个流程变得更加 AI native，而不是只在开发环节提升 10 倍产能，并不能放大最终的成果。" [作者观点]

**关键洞察**：AI 生产力提升如果只停留在开发环节，而不延伸到交付、反馈、迭代的全链路，最终成果不会显著放大。

## 主题关联

- 与 [01-parallel-workflow](01-parallel-workflow.md) 衔接：更快交付意味着更多并行需求可被同时处理
- 与 [07-quality-assurance](07-quality-assurance.md) 衔接：真实需求驱动下，质量保障需要适配更快迭代节奏

```{toctree}
:hidden:
:maxdepth: 1
```
