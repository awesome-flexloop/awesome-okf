---
okf_version: "0.2"
type: Example
title: "实操 3：agent 命令闸门、CLI 工作区与本地开发"
description: "命令事件权限闸门示意（非官方代码）、官方现行 skills 安装命令与博文口径勘误、Worktree 审阅流程、源码本地开发"
tags: [univer, ai-agent, cli, command-events, skills, example]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-20T10:40:00+08:00" }
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

# 实操 3：agent 命令闸门、CLI 工作区与本地开发

> **可复现性声明**：本页分三类内容，请勿混同——① 官方逐字命令（安装/本地开发）；② 官方概念与流程（事件名、Worktree）；③ **非官方示意代码**（闸门片段，仅表达结构，未经运行验证）。

## 1 · 命令闸门示意（⚠️ 非官方代码，仅示意）

官方只给出事件语义，未给出完整监听器示例：`BeforeCommandExecute` 可在执行前检查并取消，`CommandExecuted` 向监听者报告执行；监听器返回 disposables（F-025/F-026/F-068）。下面片段**是本知识包为说明结构而写的伪代码，不是官方 API 用法**，实际参数形态须查 [API Reference](https://docs.univer.ai/reference/classes/univer) 与 `univerAPI.Event` 定义：

```ts
// ⚠️ 非官方示意：表达「执行前拦截 + 执行后留痕」的结构，勿直接复制
const before = univerAPI.addEvent(
  univerAPI.Event.BeforeCommandExecute,
  (params) => {
    if (isOutOfScopeForAgent(params)) {
      // 官方说明取消能力仅在事件支持时生效；具体取消方式以 API 文档为准
      deny(params)
    }
  }
)

const after = univerAPI.addEvent(
  univerAPI.Event.CommandExecuted,
  (params) => auditLog.write(params)
)

// 监听器返回 disposables，组件卸载时释放
before.dispose()
after.dispose()
```

**为什么值得这样设计**：人和 agent 共用同一套命令系统，权限判定与审计只需实现一次，不会出现"UI 禁了按钮、agent 从 API 绕过去"的旁路（见 [概念 04](../concepts/04-agent-governance-and-ecosystem.md)）。

## 2 · 官方现行 skills 命令（⚠️ 博文写法已演进）

| 用途 | 官方现行命令 | 出处 |
|------|-------------|------|
| 让编码 agent 学会按任务选 SDK | `npx skills add dream-num/skills --skill build-with-univer` | skills 仓库 README（F-070） |
| 把 Web SDK 接入已有应用 | `npx skills add dream-num/skills --skill univer-integrate` | 官方安装文档（F-070） |
| 用户级安装 / 指定 agent | 追加 `-g`；或 `-a claude-code`、`-a codex`、`-a opencode` | skills 仓库 README（F-070） |
| 查看已装 skills | `npx skills list` | 官方安装文档（F-070） |

官方另提示：**旧教程引用的 `dream-num/univer-sdk-skills` 已过时**，应使用 `dream-num/skills`（F-070）。

> 博文写的 `npx skills add dream-num/skills -s univer-cli -g`（F-028）：`skills/univer-cli` 目录确实存在，但标 `hidden: true`，且官方现行文档未使用 `-s` 简写。该 skill 自身的安装入口是 `npm install -g univer-cli` + `univer doctor`（F-071）。**本知识包不照搬博文写法**。

## 3 · CLI 的 agent 工作区流程（官方概念）

```text
.univer 目标文件（Sheet/Doc/Slide/Base/Board 五类 Unit）
   ↓ 建隔离 worktree
agent 在草稿里读写 → 命令成功 ≠ 结果正确
   ↓ model readback 自检 + viewer 渲染核对
交人审阅 → 显式 merge 或 reopen（trunk 是已审阅主线）
```

（F-071/F-072）

`univer-cli` SKILL.md 明确要求：始终显式指定 `.univer` 路径、加载 core 与对应 Unit Skill、**不要直接编辑 `.univer` 存储或用无关写入器替代**；若 CLI 不可用或 `doctor` 报阻塞性运行时失败，应停止并报告诊断，而不是换工具绕过（F-071）。

## 4 · 源码本地开发（官方逐字）

```bash
git clone https://github.com/dream-num/univer.git
cd univer
pnpm install
pnpm dev
```

（F-048/F-072；README「Local development」逐字一致）

| 项 | 要求 |
|----|------|
| 开发 monorepo | Node.js `>=22.18` |
| 仅跑 Headless | Node.js `>=18.17.0` |
| pnpm | 用 `package.json` 中 `packageManager` 声明的版本 |
| 浏览器 | Chrome 88 编译目标；缺 `Intl.Segmenter` 时补 `@formatjs/intl-segmenter` |

（F-049/F-050/F-051/F-069）

## 5 · 文件转换的授权提醒

博文说得对：CLI 能处理 Office 内容，但**文件转换属于单独授权的能力**（F-031/F-062）。XLSX/DOCX/PPTX 与内部 Unit 快照之间的映射由 Server SDK 的 Exchange 承担，与 `workbook.save()` 的 JSON 快照是两条独立能力。重度使用前请确认授权说明与商务条款（本知识包未核验价格与水印细节）。

## 相关

- [实操 2 · 报价单与生命周期等待](01-quotation-with-lifecycle.md)
- [概念 04 · AI agent 治理与生态](../concepts/04-agent-governance-and-ecosystem.md)
- [核验报告 §引文逐字核对表](../references/verification.md)
