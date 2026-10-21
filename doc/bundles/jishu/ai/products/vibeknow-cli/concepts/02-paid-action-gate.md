---
type: Concept
title: "付费授权门：把「展示条款」与「授予同意」拆成两段"
description: "cmdutil.Gate 的四级解析、HMAC 派生的 action_id 与载荷哈希、两个授权边界类型、exit 8 的阻塞输出形态与无人值守场景的处置"
tags: [vibeknow, cli, 授权门, action_id, agent, 计费]
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
  - id: vkagents
    resource: https://github.com/vibeknow/cli/blob/v0.9.2/AGENTS.md
    title: "VibeKnow CLI 仓库自带 AGENTS.md（付费门契约）"
---

# 付费授权门：把「展示条款」与「授予同意」拆成两段

> **事实编号**：F-024~F-032（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


需要花钱的动作在 VibeKnow CLI 里不原地弹提示。它先停下来，把「要花什么钱、作用于哪一次运行」渲染出来交还给调用方；调用方把一个与该条款绑定的令牌带回来，动作才继续。

## 为什么要有这道门

源码自述的场景是：确认提示默认假设有人在旁边应答。Agent 跑 CLI 时没人应答，两个选项都坏——要么永久阻塞，要么替用户花掉积分然后事后提一句。CLI 选了第三个做法：把决策交回去。

## 四级解析顺序

`cmdutil.Gate` 按固定顺序解析一个付费动作：

| 顺序 | 条件 | 结果 |
|---|---|---|
| 1 | `--yes` 传入，或环境变量 `VIBEKNOW_ASSUME_YES` 非空 | 直接放行（调用方声明自己有授权） |
| 2 | `--confirm <token>` 传入 | 校验令牌；匹配则放行，不匹配则返回退出码 2 并提示「重新取号」 |
| 3 | 存在 TTY | 交互式确认，按人期望的方式问 |
| 4 | 其余 | 把决策写到 stdout，以退出码 8 结束 |

注意顺序：显式授权声明排在令牌校验之前。这是刻意的——`--yes` 是「我已经有授权了」，令牌是「我通过这道门拿到了授权」。

## action_id 是载荷的哈希

令牌不是随机串，而是「动作类型 + 决策载荷」的 HMAC-SHA256 摘要：

```
act_ + hex(HMAC-SHA256(key, actionType || 0x00 || canonical(payload)))[:24]
```

| 要素 | 取值 |
|---|---|
| 前缀 | `act_`（常量 `TokenPrefix`） |
| 密钥 | `<config-dir>/action.key`，32 字节 `crypto/rand` 随机值；目录权限 0o700，文件权限 0o600 |
| 输入 | 动作类型字节 + 1 个 0x00 分隔字节 + 规范化载荷字节 |
| 输出长度 | 十六进制摘要前 24 位 |
| 规范化 | 载荷按键名排序后以 `k=<json值>;` 拼接，保证同一决策恒定哈希 |

**载荷进哈希这件事是整道门的核心**。条款变了（换了 session、换了价格、改了要改的那段文案），令牌就变了，旧令牌立即作废。源码注释写得很清楚：同意是针对特定价格、特定运行的一次同意；一个能扛过价格变化的令牌，等于同意了一个用户从没看过的数字。

## 两个授权边界

| 类型 | 触发命令 | 载荷 |
|---|---|---|
| `export_confirmation` | `vk video export`、`vk create --export` | `session_id`、`credits`、`operation` |
| `scene_edit_confirmation` | `vk video edit` | `session_id`、`scene_index`、`script_only`、`from`、`to` |

令牌只对它被铸造的那一个边界有效，给错类型校验不通过。

`scene_edit_confirmation` 不带 credit 数量——源码解释这是诚实的答案而非缺口：改写一段文案的花费取决于模型写了多少字、语音有多长，后端不预先报价。命名「有哪几类计费工作」是 CLI 唯一能在不编造数字的前提下说清楚的事，而编一个数字会瓦解这道门唯一的依托——用户看到的是真实条款。

`from` 与 `to` 同时出现在载荷里有两个用途：用户批准的是一个 diff，两半都得可见；载荷进哈希之后，被改的镜头在「阻断」与「恢复」之间发生变化时会铸出不同的令牌，过期的确认无法覆盖一次没人要求丢弃的改动。

## 退出码 8 的输出形态

阻断信息写在 **stdout**（不是 stderr），三种格式各有形态：

| 输出格式 | 形态 |
|---|---|
| `json` | `pending_actions[]` 数组 |
| `ndjson` | `type="action.required"` 的事件行 |
| `text` | `status=blocked` + `action_id=` + `resume=` 三个键值行 |

载荷统一含：

| 字段 | 含义 |
|---|---|
| `action_id` | 不透明令牌 |
| `type` | 边界类型 |
| `blocking` | 是否为阻断式 |
| `message` | 展示给人看的说明 |
| `payload` | 被同意的条款 |
| `options[]` | 可选项，每项含 `id` / `effect`（`resume` 或 `none`）/ `label` |
| `resume_command` | 完整拼好的继续执行命令行 |

`resume_command` 是逐字拼出来的，不是描述出来的——源码注释指出，让调用方从散文里重建这条命令正是最容易出错的一步。

两条实际形态：

```
vk video export 42 --session-id <sid> --confirm act_9f2c…
vk video edit 42 --session-id <sid> --scene 3 --script "换一种说法，更短一点。" --confirm act_9f2c…
```

第二条里的脚本文本经 `shellQuote` 转义。

## 这不是安全边界

源码明确写着：任何以用户身份运行的进程都能读到密钥。这道门防的不是蓄意绕过，是**凭空编造**。令牌无法从对话推理中产生——手上有一个令牌，就意味着代码路径已经把真实条款展示给人看过。

因此，「这个令牌是真是假」不重要，重要的是「条款被显示过」这件事有据可查。

## 为什么是 8，不是 0 也不是 2

源码给的理由值得记下：

- **不是 0**：契约把结果放在退出码里，正是为了让小模型不必解析任何东西。`vk video export` 退出 0 意味着 MP4 存在；在这个边界上它并不存在。
- **不是 2**：命令行没问题，把 Agent 送去找一个它没犯的拼写错误，只是浪费一轮对话。

## 无人值守场景怎么办

| 场景 | 做法 |
|---|---|
| 流水线确实有预算授权 | 显式传 `--yes`，或设 `VIBEKNOW_ASSUME_YES=1`。责任在调用方 |
| 流水线没有预算授权 | 接受退出码 8，把决策交给人。拿到 `action_id` 后原样回传 |
| 令牌校验失败（退出码 2） | 条款已变。重新执行一次拿新的 `action_id`，不要试图复用旧值 |

随仓发布的 `vibeknow-create` Skill 把其中两条写成了硬约束：不自行编造 `--confirm` 值，不主动追加 `--yes`。

## 相关概念

- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码契约全貌
- [/concepts/04-run-ledger-and-async.md](/concepts/04-run-ledger-and-async.md) —— 账本与异步的交互
- [/concepts/10-ai-skill-contract.md](/concepts/10-ai-skill-contract.md) —— 随仓 Skill 的运行契约
- [/examples/01-agent-safe-automation.md](/examples/01-agent-safe-automation.md) —— exit 8 的回交范式
