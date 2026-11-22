---
okf_version: "0.2"
type: Concept
title: "AI agent 治理与生态：把人和 agent 放在同一套 API 上"
description: "官方 AI office 定位、命令事件权限闸门、Univer CLI 与 Worktree 审阅流程、五个生态集成仓库与官方现行命令写法"
tags: [univer, ai-agent, command-events, cli, worktree, governance]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-20T10:20:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7WCDC4R7mxqFRHMP0Zf9hA
  - id: official-readme
    url: https://github.com/dream-num/univer/blob/dev/README.md
  - id: official-skills
    url: https://github.com/dream-num/skills
  - id: official-installation
    url: https://docs.univer.ai/guides/sheets/getting-started/installation
---

# AI agent 治理与生态：把人和 agent 放在同一套 API 上

> 概念层（Who / Governance）。本文是博文「给 AI 改表加一道闸」一节的官方口径还原 + 口径勘误。

## 设计前提：agent 是正式用户，不是外挂

官方 description 逐字含 "**for people and AI agents**"（F-058），README 写明：

> "Agents can use the same open-source APIs; your application supplies the model and tool orchestration."（F-058/F-072）

也就是说：agent **不模拟点击、不自己拼 xlsx**，直接调 Facade API 写值、写公式、读结果（F-023）；模型选型、工具编排、权限策略由应用侧负责，Univer 只管表格这一层（F-024）。这个分工意味着——**SDK 不替你做 agent 安全，但给了你一个天然统一的治理面**。

## 命令事件：权限闸门落在哪一层

因为用户操作和 agent 调用都走同一套命令系统（见 [03-命令系统](03-command-system-and-plugin-architecture.md)），治理点可以下沉到命令层，而不必拦在 UI 上：

| 事件 | 时机 | 能力 |
|------|------|------|
| `BeforeCommandExecute` | 执行前 | 检查、**取消**执行 |
| `CommandExecuted` | 执行后 | 通知监听者 |

（F-025/F-026/F-068，官方逐字："`BeforeCommandExecute` can inspect and cancel an execution; `CommandExecuted` reports executions to listeners"）

官方还说明：`univerAPI.Event` 提供 typed events、`univerAPI.Enum` 提供枚举，应用不必导入私有服务或硬编码字符串；监听器返回 disposables，取消能力仅在事件支持时生效（F-068）。

**可迁移模式**：让 AI 动表之前挂一个 `BeforeCommandExecute` 监听，按业务规则判定越权改动并当场拦下，再用 `CommandExecuted` 留审计记录。这样权限与审计对"人"和"agent"用同一套实现，不会出现两套逻辑漂移。完整示意见 [examples/02](../examples/02-agent-command-guard.md)（**非官方示例，仅示意**）。

## CLI 与 Worktree：官方的 agent 工作区形态

博文描述的流程（F-027~F-030）——隔离草稿里改、自己读回核对、给本地预览链接、合并还是丢掉由你决定——在官方材料中逐项可对应：

- `univer-cli` SKILL.md：CLI 面向 `.univer` 多 Unit 文件，提供**隔离 worktrees**、版本匹配的 Facade 指引、**model readback** 与浏览器 viewer 交接；`trunk` 是已审阅主线，worktree 是 agent 变更的隔离范围；**worktree commit 是持久写入边界，merge 始终是显式审阅决定**（F-071）。
- 官方明确 "**Command success is not correctness evidence**"——命令成功不等于结果正确，必须读回目标模型、验证任务断言、必要时检查渲染结果（F-071）。
- AI SDK 文档侧给出三段式：**Understand/discover/edit**（结构化内容读取、Facade 读写模式、mutations 捕获与 commit）、**Check the rendered result**（Render Runtime 截图、幻灯片布局 lint）、**Edit drafts for human review**（Worktree 多轮修改后交人 review/merge/reopen）（F-072）。
- CLI 覆盖 **Sheet / Doc / Slide / Base / Board** 五类 Unit，不止博文说的 Excel/Word/PPT 三种（F-031/F-071）。

## ⚠️ 口径勘误：博文的 CLI 安装命令已经演进

博文给的是 `npx skills add dream-num/skills -s univer-cli -g`（F-028）。核验结论不是"错了"，而是**实体真实、写法已变**：

| 项 | 官方现行（2026-11-20） |
|----|----------------------|
| skills 仓库 README 主推 | `npx skills add dream-num/skills --skill build-with-univer`（`-g` 用户级、`-a claude-code` 指定 agent） |
| 安装文档推荐 | `npx skills add dream-num/skills --skill univer-integrate` |
| `univer-cli` skill | 目录**确实存在**，但 SKILL.md 标 `hidden: true`；其自身安装为 `npm install -g univer-cli` + `univer doctor` |
| 历史提示 | 官方提示旧教程引用的 `dream-num/univer-sdk-skills` 应改用 `dream-num/skills` |

（F-070/F-071）

`-s` 简写未见于官方现行文档。因此本知识包在 [examples/02](../examples/02-agent-command-guard.md) 给出官方现行写法，博文写法登记为历史/简写口径，**不照搬**。

## 生态集成清单（官方五个仓库）

| 项目 | 提供 |
|------|------|
| Univer CLI | 本地命令行工作区，创建/编辑/检查/交付 Office 内容 |
| Univer Office for **DeepSeek Harness** | 关联内容、结果校验、版本化变更、隔离 Worktree 协同 |
| Univer Office for **WorkBuddy** | 本地 Office 集成、MCP 预览、草稿审阅（**Developer preview**） |
| Univer Office for **OpenClaw** | 创建、审阅与交付 Office 内容的工具 |
| Univer SDK Skills | 帮编码 agent 集成 SDK、开发插件、实现后端工作流 |

（F-070；博文只提了 OpenClaw 与 DeepSeek Harness，属不穷尽列举）

另有参考应用 [Univer Workspace](https://github.com/dream-num/univer-workspace)，把编辑器、协同、文件能力、既有 agent 与人工审阅组合成可自托管工作区（F-072）。

## 阅读下一篇

- [05 · 选型与可迁移模式](05-selection-and-transferable-patterns.md)——把上面几条抽象为可复用模式
- [核验报告 §口径对照表](../references/verification.md)——7 项 ⚠️ 的完整处置
