---
type: Example
title: "规则与回执：写 rules.json、预演派活、让 Agent 用代码块说话"
description: "官方定时规则原文示例、外部事件规则字段表、规则热生效与容错、五类回执协议、ask 代码块示例与 why 事件链复查"
tags: ["rules.json", "cron", "回执协议", "dry-run", "emit", "agent-autoloop why"]
status: stable
sources:
  - id: official-readme
    resource: https://github.com/KKKKhazix/agent-autoloop/blob/main/README.md
    title: "Agent Autoloop 官方 README「日常怎么配 / Agent 怎么跟中台配合」"
  - id: blog
    resource: https://mp.weixin.qq.com/s/T9_acg247gxzUNL4j5zrCw
    title: "开源我这折腾了1年的「Agent自动化系统」（2026-11-04）"
---

# 规则与回执

> **⚠️ 可复现性声明**：本篇的规则示例与回执格式**来自官方 README（2026-11-06 `main` 分支快照）**，可照做，但**本知识包未在本机安装运行该项目**。凡本包自行整理、非官方逐字给出的内容（字段表、预演流程、检查清单）均显式标注为「教程整理」。

## 1. 规则文件在哪、管什么

规则文件：`~/.agent-autoloop/rules.json`（F-049）。它承担五步流程的第 2 步：内核按规则决定**哪个 Agent、去哪个目录、用哪个 Skill**（F-019）。同一件事短时间内连续来多条消息会合成一轮，也在这一步处理。

两条官方规则示例分别对应「定时触发」与「外部事件触发」（F-049）。

### 1.1 定时规则（官方 README 原文示例）

```json
{
  "name": "早报",
  "when": { "cron": "0 9 * * *" },
  "to": "codex",
  "cwd": "~/notes",
  "prompt": "整理昨天的笔记和提交，写今天的早报。"
}
```

| 字段 | 含义 |
|------|------|
| `name` | 规则名，便于 `rules explain` 与 `why` 中识别 |
| `when.cron` | cron 表达式，这里是每天 9:00 |
| `to` | 派给哪个 Agent |
| `cwd` | Agent 在哪个目录干活 |
| `prompt` | 交给 Agent 的提示词 |

### 1.2 外部事件规则（教程整理的字段表）

官方另给出一份外部事件规则示例，字段为 `when.source` / `types` / `to` / `cwd` / `skill` / `parallel`（F-049）。下表为**教程对这些字段的整理，不是官方 JSON 原文**：

| 字段 | 作用 | 与定时规则的差别 |
|------|------|-----------------|
| `when.source` | 指定事件来源，用来匹配 Webhook / 轮询送进来的事件 | 定时规则用 `when.cron`，这里用来源 |
| `types` | 限定接收的事件类型 | 定时规则不需要 |
| `to` / `cwd` | 派给谁、在哪个目录 | 相同 |
| `skill` | 指定使用的 Skill | 定时示例未出现 |
| `parallel` | 并发处理开关 | 定时示例未出现 |

> 需要逐字可用的外部事件规则时，请直接复制官方 README 的示例；本包不臆造其具体取值。

### 1.3 规则改动后的行为（官方 F-050）

- 规则保存后**几秒内生效**；
- 改错、文件被删或读不到时，系统**继续按旧规则跑，并发卡片提醒**，不会静默停摆；
- 官方自测命令里有 `agent-autoloop why 1`，可查某一轮是按哪一版规则派活的（F-060，博文示例输出含「规则版本 #1」，F-027）。

## 2. 先预演，再接真实事件

```bash
agent-autoloop rules explain                 # 解释当前规则会怎么派活
agent-autoloop emit <类型> --dry-run         # 预演这条事件会派给谁
```

官方对 `emit --dry-run` 的限定是：**不连接中台、不写日志**（F-048）。教程整理的推荐顺序：

1. 写好 `rules.json` → `rules explain` 看解析结果；
2. `emit <类型> --dry-run` 看这条事件会落到哪个 Agent / 目录；
3. 确认无误后再接真实 Webhook 或启用 cron。

> 这一步对应 [03 插件生态](../concepts/03-plugin-ecosystem.md) 的分档提示：官方四种 Webhook 模板只在本地模拟服务验证过（F-055），先在 `--dry-run` 里把规则跑通，再考虑接真实服务。

## 3. 回执协议：Agent 怎么跟中台说话

中台对 Agent 只有一个约定：**在最后一条回复里交代结果**（F-020、F-034）。需要提问、通知、结卡片、约复查或触发新事件时，在回复末尾附一个 `agent-autoloop` 代码块。不用装 SDK、不改 Agent 源码。

### 3.1 `ask` 示例（官方 README 与博文均给出）

````text
```agent-autoloop
{
  "ask": [{
    "title": "怎么发货？",
    "text": "两种方式今天都能发出。",
    "options": ["快递", "自提"],
    "key": "shipping"
  }]
}
```
````

| 字段 | 作用 |
|------|------|
| `title` | 卡片标题 |
| `text` | 说明文字 |
| `options` | 给人点的选项 |
| `key` | 结果回写时用的键，人工点选后据此接回原会话 |

### 3.2 五类回执（官方 F-051）

| 回执 | 作用 | 备注 |
|------|------|------|
| `ask` | 发卡片请人拍板 | 见上例 |
| `notice` | 通告 | 只告知的通告标 `fyi`，**不带按钮** |
| `resolve` | 结卡片 | — |
| `later` | 约定稍后复查 | 对应五步流程第 4 步的「半小时后复查」分支（F-021） |
| `events` | 触发新事件 | 对应「触发下一步」分支（F-021） |

### 3.3 两条容错设计（官方 F-051）

- **JSON 写错时只让在原会话重写最后一段回复，不重做已完成的业务**——这一点与 [事件溯源](../concepts/02-four-mechanisms.md) 的「只追加」是配套的：已确认的业务动作不会被回滚重跑。
- **`"resume": true`** 表示接续上一轮会话，用于需要延续上下文的场合。

> 与 [指令数据分离](../concepts/02-four-mechanisms.md) 的关系：外部事件的文字应以文件路径作为「资料」传入，提示词里只留校验过的类型、编号、链接；官方对事件里携带 `cwd` / `agent` / `access` 字段**直接拒收**（F-057）。博文的 Issue #42 提示词示例（F-029）是这一约束在提示词层的写法。

## 4. 复查：用 why 把一轮拆开

```bash
agent-autoloop why 1
```

官方把它列为「自己跑一遍」的第一条命令（F-060）。博文给出的输出示例包含：第 1 轮·演示、规则版本 #1、触发事件来源 `local`·类型 `demo.start`·对象 `example`、`local` 领取（演示程序）、结束「演示完成」、时间戳 11-03 20:47:25（F-027）。

> 该输出为**博文原文示例**，官方 README 亦提供同一命令但本包未记录其完整实测终端输出；以本机实际执行结果为准。

## 5. 边界提示

1. 本篇规则示例与回执格式来自官方文档，**未在本机实测**；官方场景模板样例数据均为虚构、脚本与回执只用本地 HTTP 与假飞书 CLI 验证（F-067）。
2. `rules.json` 改错时系统会继续按旧规则跑并发卡片（F-050）——排查「改了规则没生效」时先确认文件是否被读到，别急着改规则内容。
3. 高频 cron 触发前请先读 [安装篇第 0 节](01-install-and-first-run.md) 的用量与合规提示（F-064）。
4. 完整的 F 编号与口径差异见 [信源与事实登记](../references/article-source.md) 与 [P0 核验报告](../references/verification.md)。
