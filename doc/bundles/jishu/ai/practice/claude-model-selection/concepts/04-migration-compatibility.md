---
type: Concept
title: "迁移兼容清单"
description: "换模型名之前必须测的七类差异：preserved thinking、强制思考、tool_choice、computer use、Haiku 4.5 迁移与安全回退。"
tags: [claude, migration, compatibility, thinking, tool-use]
generated: { by: "lobsterai/main", at: "2026-11-10T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T13:30:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: article
    resource: /references/article-source.md
  - id: cc-model-config
    resource: https://code.claude.com/docs/en/model-config
---

# 迁移兼容清单

## 为什么不能只改模型名

四个模型都支持工具调用与图像输入（F-066），但 thinking、工具选择、计算机使用与安全回退的行为并不一致。直接替换 `model` 字段可能得到 400、静默丢失推理，或让某类请求被安全分类器改道。

博文的原则是：**按最严格的模型构建请求**，这样任何一步都能上下移动而不改代码（F-074）。

## 一、Preserved thinking 与 400

Fable 5.2 对所有 API 账号启用 preserved thinking。如果 thinking block 之前的任何内容发生变化——系统提示、工具定义或更早的消息——API 会返回 400，除非显式选择丢弃受影响的 thinking（F-067）。

处理方式：

1. 用 Claude Code、Claude Agent SDK 或 Claude Managed Agents 构建时，不需要改动。
2. 自建请求时保持历史只追加，不要回头改系统提示或工具定义。
3. 迁移前用一段长对话做回归，确认没有隐式改写历史。

## 二、Thinking 不是到处都能关

Opus 5.5 与 Fable 5.2 始终思考，请求里关闭 thinking 会返回错误；Sonnet 5.5 默认思考，`between_tools` 让它在工具间隙才思考；Haiku 5.5 默认思考，但在 `high` 及以下可以关闭（F-069）。

还有一个容易出 bug 的细节：响应可能以 thinking block 开头。解析时必须按 `type` 读取内容块，不能假设第一个块就是文本。

## 三、tool_choice 的强制调用会报错

在 Sonnet 5.5、Opus 5.5、Fable 5.2 上，`tool_choice` 设为 `any` 或指定某个 `tool` 会返回 400（F-070）。

替代写法：

1. `tool_choice: auto`。
2. 给工具加 `strict: true`。
3. 在提示词里明确说明什么时候该用这个工具。

这实际上把“强制调用”从参数约束变成了提示约束，回归测试要覆盖“模型是否在预期时机调用了工具”。

## 四、Computer use 的工具集限制

计算机使用只在 Claude API 与 Google Cloud（Google managed）上，通过 `computer_toolset_20260801` 工具集支持（F-071）。其他平台或旧工具集不能假设兼容。

## 五、Haiku 4.5 → 5.5 的三处不兼容

从 Haiku 4.5 迁到 5.5 时（F-072）：

1. 用 effort 取代 `budget_tokens`。
2. 移除非默认的 `temperature`、`top_p`、`top_k`，否则返回 400。
3. 消息必须以 user turn 结尾；用 assistant turn 让模型续写会返回 400。

第三点最容易被忽略，因为它在旧模型上可能“能跑”。

## 六、安全回退会换模型

Opus 5.5、Sonnet 5.5、Fable 5.2 都运行安全分类器，最常命中网络安全与生物内容。在 Claude Code 中，被标记的请求可以改由旧模型重跑，转录里会提示用了哪个模型（F-073）。

Fable 5.2 沿用 Fable 5.1 的回退映射：网络安全请求回退到 Opus 4.8，生物请求回退到 Opus 5。这意味着同一段代码在普通请求与回退请求上的行为可能不同，评测时要区分。

## 七、迁移前的回归清单

1. 长对话追加历史，确认不触发 preserved thinking 的 400。
2. 关闭 thinking 的请求是否还有？有则移除或改档。
3. 所有 `tool_choice: any` 或指定 tool 的调用改成 `auto` + `strict`。
4. 内容块解析是否按 `type` 分支，而不是按位置。
5. computer use 是否在受支持平台与工具集上。
6. 是否有非默认采样参数或 assistant 结尾消息。
7. 安全敏感领域是否准备了回退模型的预期行为。
8. 多模型系统是否统一按最严格模型构建请求。

## 多模型共存的写法

如果一套系统同时跑多个模型，按最严格的那个写请求：历史只追加、`tool_choice: auto` 配 strict 工具、按 type 读内容块、提示词与工具描述精确到“最字面”的模型也能照做（F-074）。这样升降档只是换一个字符串，而不是重写调用层。

路由规则简单时（例如每种步骤固定一个模型），让代码选模型；只有规则本身需要语义判断时，才让模型参与路由。
