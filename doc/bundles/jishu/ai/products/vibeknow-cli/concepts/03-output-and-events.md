---
type: Concept
title: "输出三通道：stdout 是答案、stderr 是过程、磁盘是记忆"
description: "text/json/ndjson 三种输出格式的解析优先级、VIBEKNOW_OUTPUT 环境变量、vk_event= 结构化事件通道的开启规则与 advisory 语义"
tags: [vibeknow, cli, 输出格式, json, 事件流, agent]
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
  - id: exitcodes
    resource: /references/exit-code-contract.md
    title: "VibeKnow CLI 退出码契约全表"
---

# 输出三通道：stdout 是答案、stderr 是过程、磁盘是记忆

> **事实编号**：F-037~F-042、F-095~F-100（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


VibeKnow CLI 把「给人看的结果」「给程序看的进度」「跨会话的记忆」分在三个地方。这个拆分不是风格偏好，而是让 Agent 与人类共用同一套命令的前提。

## 三种输出格式

| 格式 | 适用场景 |
|---|---|
| `text` | 人类阅读的键值块与散文 |
| `json` | 程序解析的单个对象 |
| `ndjson` | 逐行对象流 |

### 解析优先级

```
显式 --output  >  VIBEKNOW_OUTPUT 环境变量  >  默认 text
```

`internal/output/format.go` 的 `ResolveFormat(flagVal, flagSet, env)` 接受一个独立的 `flagSet` 布尔量，用来区分「传了空串」与「没传这个旗标」——两者都落到 `text`，但走的是不同分支。

**非法取值是错误，不是静默回落。** `--output jsonl` 会被拒绝并提示只能是 `text, json, ndjson` 三者之一。源码注释记着原因：旧行为是打印人类文本并退出 0，打错的调用方拿到散文却没有任何异常信号。

### 刻意不做「检测到管道就切 JSON」

源码注释里有一句值得原样记住：不这么做，因为这会在升级时改变每一条既有 shell 流水线的输出；对齐的 CLI（gh、kubectl、docker）都保持格式显式。

因此想要结构化输出必须显式声明，两种方式：

```bash
vibeknow create --text "..." --output json          # 单次声明
export VIBEKNOW_OUTPUT=json                          # 整个会话声明
```

## 事件通道：stderr 上的 `vk_event=`

结构化进度事件走 **stderr**，每行以 `vk_event=` 前缀开头：

```
vk_event={"type":"task.submitted","task_id":42,"session_id":"..."}
vk_event={"type":"resource_ready","asset_kind":"cover_image",...}
```

包头的注释交代了这道拆分的来由：CLI 过去让调用者在「看进度」和「拿可解析结果」之间二选一——`--output json` 直到结束才打印任何东西，`--output ndjson` 又把进度流放到 stdout 上顶掉了最终答案，消费者得读完整个流自己猜哪一行是终态。

拆分之后，stdout 只承载答案，stderr 承载过程。消费者要进度就 grep stderr 的前缀；只要结果就读 stdout，两边互不干扰。

### 开启规则

| 条件 | 事件通道 |
|---|---|
| `VIBEKNOW_EVENTS` = `1` / `on` / `true` / `stderr` | 开启 |
| `VIBEKNOW_EVENTS` = `0` / `off` / `false` / `none` | 关闭 |
| 其它取值或未设置 | 跟随格式：仅 `--output json` 时默认开启 |

默认只在 json 下开启，理由写在源码注释里：text 模式下 stderr 是给人的进度显示，把 JSON 混进去等于拿一个没人要的人机界面换一个。json 模式已经意味着「有程序在读」，此时散文没有听众。

**ndjson 模式的事件留在 stdout**，不复制到 stderr——那个形态是发布出去的、调用方会解析的流，复制会让同时读两个流的人看到双份事件。

### advisory 语义

事件是建议性质的：`Emit` 丢弃写入错误，不向调用方返回失败；通道关闭时返回零值 `Emitter`，`Emit` 是空操作。包头注释的说法是——一个不得不处理「进度行没写出去」的调用方，是个会把事情办砸的调用方。

推论：**stderr 写不出来不该让一次已完成的渲染变成失败的命令**，这条在实现上是显式保证的。

## 消费侧的纪律

1. **结果只读 stdout**，过程另抓 stderr 的 `vk_event=` 行。
2. **不要 `2>&1` 合并两个流**——合并之后无法再区分结果与过程，事件行会混进 JSON 载荷里。随仓 `vibeknow-create` Skill 把这条写成了硬约束。
3. **要全程结构化就显式 `--output json`**（事件自动开），或设 `VIBEKNOW_OUTPUT=json`。
4. **落盘产物靠 `resource_ready` 事件里的 `asset_kind` 与内容哈希去重**，不要指望事件把 URL 带回来（见 [08-preview-artifacts.md](08-preview-artifacts.md)）。

## 统一快照结构

多个 `vk video` 子命令共用 `internal/video/snapshot` 的快照结构，字段包括 TaskID、SessionID、WorkID、Engine、Title、DurationMs、CoverURL、Preview、Export、NextActions。

| 渲染函数 | 形态 |
|---|---|
| `RenderText` | 键值块，stderr 追加提示行 |
| `Render` | 按格式分派到上面两个或 NDJSON |
| `RenderNDJSON` | 载荷中置 `type="snapshot"` |

快照状态取 4 值：`idle` / `running` / `succeeded` / `failed`。`nextActions` 按导出状态分四支给出可直接执行的后续命令——这正是退出码 7 时该读的东西。

## 相关概念

- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码与 `error.detail` 的读法
- [/concepts/08-preview-artifacts.md](/concepts/08-preview-artifacts.md) —— `resource_ready` 事件与落盘产物
- [/concepts/10-ai-skill-contract.md](/concepts/10-ai-skill-contract.md) —— 「不合并两个流」的出处
