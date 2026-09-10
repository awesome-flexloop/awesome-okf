---
okf_version: "0.2"
type: Concept
title: "Context（上下文）与 Context Window"
description: "Context 的组成、Context Window 的定义与容量、溢出行为及应对策略。"
tags: ["Context", "Context Window", "上下文", "记忆", "FIFO", "溢出"]
generated: 2026-09-09
verified: 2026-09-09
status: verified
stale_after: "2027-09-09"
sources:
  - "F-011~F-020"
  - "S2: CSDN 镜像"
---

# 02 Context（上下文）与 Context Window

> 对应事实：F-011~F-020
> 知识层级：事实层

---

## 一、什么是 Context？

**Context 是 AI 能"记住"的所有信息的总和**，包括：

| 组成部分 | 说明 |
|----------|------|
| 用户问题 | 当前输入的内容 |
| 对话历史 | 之前的对话记录 |
| System Prompt | 系统预设的人设和规则 |
| 工具定义 | 可用工具的描述信息 |
| AI 正在输出的内容 | 流式输出时也在消耗 Context |

---

## 二、什么是 Context Window？

**Context Window 是 Context 能容纳的最大 Token 数量**，相当于 AI 的"短期记忆容量"。

| 模型 | Context Window | 相当于 |
|------|---------------|--------|
| GPT-4 | 128K Token | 约 10 万单词 |
| Claude 3.5 | 200K Token | 约 30 万汉字 |
| Claude 3.1 Pro | 100 万 Token | 约《哈利波特》全集 |

> ⚠️ **注意**：不同模型版本、不同厂商的 Context Window 差异很大，以上数据为文章发布时的参考值。

---

## 三、为什么重要？

### Context Window 溢出后的行为

通常采用 **FIFO（先进先出）** 策略：最早的对话会被"遗忘"。

后果：
- AI 忘记之前的约定
- 回答与上下文不一致
- 复杂推理链断裂

### 类比

Context Window 就像一块白板——写满了就得擦掉最早的内容。

---

## 四、实际应用建议

| 策略 | 说明 |
|------|------|
| 精简 Prompt | 去除冗余描述，减少 Token 消耗 |
| 分段处理 | 超长文档拆分为多个请求 |
| 摘要压缩 | 对话历史定期摘要，保留关键信息 |
| 选择大 Window 模型 | 长文本场景优先选 200K+ 模型 |
