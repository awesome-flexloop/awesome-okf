---
type: Reference
title: 进程登记：seven-concepts-v（对抗审查）
description: 本知识包各文档 verified.by 所用自动化审查进程的定义、范围与复核路径
tags: [process, verification, seven-concepts, okf]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:42:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: seven-concepts
    resource: .agents/commands/seven-concepts.md
    title: 七概念方法论编排指令集
---

# 进程登记：seven-concepts-v

## 用途

本知识包的 `verified.by` 使用 `process:seven-concepts-v`，表示文档经过“七概念”方法论中的 V（对抗性审查）阶段：以源码与官方文档为唯一事实源，对草稿逐条攻击，记录问题并回改。

## 进程定义

| 项 | 值 |
|---|---|
| actor | `process:seven-concepts-v` |
| 输入 | 草稿文档、`spec/facts.md`、上游源码与文档 |
| 方法 | 逐条声明回查；至少提出 5 条具体质疑；至少采纳 2 条修正 |
| 输出 | `spec/review.md` 中的审查记录与修正清单 |
| 复核 | 任何读者可按 `references/source-map.md` 路径回查 |

## 审查范围

1. **事实性**：版本号、依赖、默认值、事件名、模板名、配置键。
2. **行为性**：缓存条件、模板过滤、主题切换、版本切换、搜索时序。
3. **边界**：`dirhtml`、非 HTML builder、`file://`、无祖先页面、空模板。
4. **可操作性**：示例配置是否可复制运行，路径与字段是否完整。
5. **表述**：是否存在“总是/绝不/唯一”等过度概括。

## 不覆盖

- 未在源码或官方文档中出现的行为不做推断。
- 不验证上游未来版本；`stale_after` 为重新评估节点。
- 不替代人工可访问性测试与真实站点验收。

## 复核路径

1. 打开 `spec/facts.md`，按事实编号找到对应源文件。
2. 打开 `spec/review.md`，查看该事实是否被质疑与修正。
3. 如发现新问题，在 `log.md` 记录并更新 `status` / `verified`。
