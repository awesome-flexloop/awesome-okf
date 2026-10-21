---
type: Concept
title: "AI Skill 运行契约：三条硬约束与四个流水线阶段"
description: "skills/ 目录下三个 Skill 的结构与 frontmatter、vibeknow-create 的 Run Contract 六条硬约束、outline→tts→render→publish 四阶段、Skill 如何消费事件与授权决策"
tags: [vibeknow, cli, skill, agent, 运行契约, 事件流]
generated:
  by: trae-seven-concepts
  at: "2026-10-21T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T00:00:00+08:00"
status: stable
stale_after: "2027-04-21"
sources:
  - id: vksrc
    resource: https://github.com/vibeknow/cli
    title: "VibeKnow CLI 源码仓库 v0.9.2 @ 93a26eca"
  - id: facts
    resource: /references/source-facts.md
    title: "VibeKnow CLI 编号事实清单 F-001~F-104"
---

# AI Skill 运行契约：三条硬约束与四个流水线阶段

> **事实编号**：F-101~F-104（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


CLI 仓库自带 `skills/` 目录，把「怎么用它」写成 Agent 能读懂的运行契约。这是理解整个 CLI 设计意图的最佳入口——**CLI 的很多约束不是为人写的，是为 Agent 写的。**

## 三个 Skill

| Skill | 职责 | SKILL.md 行数 |
|---|---|---|
| `vibeknow-core` | 认证、profile、配置、诊断 | 131 |
| `vibeknow-create` | 生成视频、跟踪进度、下载结果、浏览音色 | 438 |
| `vibeknow-doc` | 文档上传与状态 | 109 |

连同 references 目录共 12 个文件。

## frontmatter

```yaml
---
name: vibeknow-create
description: "..."
version: 0.9.2
emoji: "🎬"
homepage: https://github.com/vibeknow/cli
allowed-tools: Bash(vibeknow:*)
metadata:
  openclaw:
    requires:
      bins: ["vibeknow"]
    install:
      - kind: node
        package: vibeknow-cli
        bins: [vibeknow]
    primaryEnv: VIBEKNOW_TOKEN
    envVars:
      - name: VIBEKNOW_TOKEN
        required: false
      - name: VIBEKNOW_EXPORT_TIMEOUT
        required: false
---
```

`allowed-tools: Bash(vibeknow:*)` 把工具范围限定在该 CLI 的命令上。`VIBEKNOW_TOKEN` 是可选的——未设置时 CLI 使用 `vibeknow auth login` 配置的凭证。

## Run Contract：六条硬约束

`vibeknow-create` 的 Run Contract 段写明：这些规则从运行开始的那一刻起生效，每一条存在的原因都是**违反它会让用户花钱，或者让一个仍在进行的运行丢失**。

### 1. 不对同一请求跑两次 `vibeknow create`

第二次 create **永远是第二次计费渲染**，它不会恢复或续跑第一次。丢了 id 时的正确动作是 `vibeknow jobs list`，再 `vibeknow video list`。只有 CLI 明说可以了（`resend_safe: true`）才从头开始。

### 2. 不合并两个流

`2>&1` 破坏契约：stdout 是结果，stderr 是其它一切。需要保留就重定向到不同文件。

### 3. 不把 `tail -n 20` 当游标

事件是成批到达的。从保存的 offset 读 stderr，否则会静默跳过整个阶段。

### 4. 安静时不重发

渲染要几分钟，流水线在其中某些段落本就是静默的。慢、一段时间没输出、工具调用在你这侧超时——这三者都与「一个即将成功的运行」相容。

### 5. 一个进程拥有这个流

`create` 与 `video wait` 已经在轮询后端、打印进度、收集结果。不要在运行中的 `video wait` 旁边再起一个 `video status` 循环，也不要用自己的 poller 包住命令。

### 6. 进程结束了不等于运行结束了

shell 返回、后台作业结束、通知到达——这些都不告诉你任务的状态。要读退出码和 stdout。

### 7. 不自己编 `--confirm`，不主动加 `--yes`

CLI 把一个计费决策交回来时，它停下来正是因为这个选择不该由你代做。转达它，然后等待。

## 四个流水线阶段

```
outline  →  tts  →  render  →  publish
```

**不是每个节点都报进度**：每次运行中的若干部分——以及 `handdraw` 运行的整个中段——是设计上的静默。静默不是卡死，等一个终态事件。

## 等待要分步

`vibeknow video wait --for 90s` 会在事件流上观察 90 秒，然后报告到达的阶段，并以退出码 6 + `reason: "wait_budget_expired"` 结束，再跑一次继续等。

适用场景是你的工具超时短于一次渲染。`video status` 不能替代它——work 行在导出阶段之前不携带进度。

## 事件的消费方式

- `--output ndjson` 输出结构化进度事件（`schema_version: "1"`）
- `--output json` 时 stdout 恰好一个 JSON 文档，stderr 是 `vk_event={...}` 进度行——**一次调用同时得到两者**，不必在「看着」和「解析」之间二选一
- `VIBEKNOW_EVENTS=1` 让文本模式也有同样的事件行，`VIBEKNOW_EVENTS=0` 抑制它们

## 产物的转交方式

`share_url` 是托管页面，终端里没法给别人看。传 `--preview-dir <dir>` 给 `create` / `video status` / `video wait` / `video export`，封面静帧（以及导出后的 MP4）会落到磁盘，每个都由一个带绝对 `local_path` 的 `resource_ready` 事件宣告。

**把每一个新的 `local_path` 交给用户一次。** 内容未变化时不会重复宣告，所以往同一个目录里重跑是安全的。

## 实践建议

1. **把 Skill 文档当成 CLI 的使用说明书读**，Run Contract 段是最有价值的部分。
2. **先 `jobs list` 再 `create`**。
3. **不要用 `2>&1`**。
4. **退出码 6 + `wait_budget_expired` 是正常状态**，再等一轮。

## 相关概念

- [/concepts/03-output-and-events.md](/concepts/03-output-and-events.md) —— stdout / stderr 分工
- [/concepts/08-preview-artifacts.md](/concepts/08-preview-artifacts.md) —— `resource_ready` 事件与本地路径
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 为什么不能自己加 `--yes`
- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码 6 的三态判定
