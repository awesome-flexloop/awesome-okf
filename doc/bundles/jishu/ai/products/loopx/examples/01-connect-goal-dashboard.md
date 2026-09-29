---
okf_version: "0.2"
type: Example
title: 实操 2——连接项目、引导式建立长期目标与工作台巡检
description: loopx connect/status/start-goal --guided 完整链路、预期输出、.loopx 状态目录与 dashboard 工作台每日巡检用法
tags: [loopx, connect, start-goal, dashboard, 实操]
generated:
  by: trae-solo-agent
  at: "2026-09-16T20:40:00+08:00"
status: stable
stale_after: "2026-11-30"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/BzxrklBhyJBWjhupDtcgVQ
  - id: github-loopx
    url: https://github.com/huangruiteng/loopx
---

# 实操 2：连接项目、建立首个长期目标与工作台巡检

> 对应博文「快速开始」后半段（F-024~F-026）与作者描述的跨周续做体验。命令与官方 Getting Started 逐字一致；预期输出综合博文与官方 README。

## 1. 在项目根目录连接

```bash
cd /path/to/your-project
loopx connect
loopx status
```

- `loopx connect` 把当前项目登记给 LoopX；**项目尚未初始化时，它会提示状态缺失**（F-024），而不是静默创建或覆盖任何东西——官方强调"LoopX should reuse existing state rather than overwrite it"（应复用既有状态而非覆盖）。
- `loopx status` 是日常入口：展示当前目标（objective）、**等你拍板的具体用户门禁**、下一条 Agent 待办（F-026）。

## 2. 引导式建立长期目标

状态缺失时按引导创建一个长期目标（F-025，博文中文示例）：

```bash
loopx start-goal --guided --project . --goal-text "你的长期目标"
```

官方英文示例：

```bash
loopx start-goal --guided --project . --goal-text "Your long-running objective"
```

参数含义：

| 参数 | 作用 |
|---|---|
| `--guided` | 引导式交互，适合首次建目标 |
| `--project .` | 绑定当前目录为目标的项目根 |
| `--goal-text` | 长期目标的自然语言描述（跨天/跨周的大目标，而非单轮小任务） |

建完再跑一次 `loopx status`，博文给出的预期是：**当前目标、待你拍板的门禁、下一个待办都已可见**（F-026）。

## 3. 打开本地工作台

```bash
loopx dashboard
```

浏览器中拉起本地工作台（F-016）。博文的使用画像：

- 一屏看到正在跑的目标、卡在等回复的门禁、定时挂着的任务与已经停掉的任务；
- **上周开始的目标这周再打开，仍停在原位置**，当时的证据与剩余待办都在，接着做即可；
- 可同时挂多个 Agent 会话（Codex 一段、Claude Code 一段），Goal 状态与证据不丢（F-017）。

1.0 补充：`loopx dashboard` 是官方受支持的浏览器/PWA 路径；1.0 release 另提供原生桌面预览（与 CLI 共享同一套 loopback 服务，关闭窗口只停掉它自己启动的服务进程，既有服务与持久 Goal 状态不受影响）。

## 4. 让宿主真正"进环"

建目标只完成了控制面准备，还需在宿主侧触发循环。官方按宿主给出不同入口（核验事实 F-045）：

- **Codex App / CLI**：让 Agent 连接本项目、跑 `loopx doctor`、保留既有状态并报告当前门禁与下一待办，之后用 `$loopx <复杂任务>` 或从 /skills 选择 loopx；
- **Claude Code**：安装 opt-in 适配器后，`/loopx <任务>` 发起、`/loop` 持续循环；
- **Cursor / shell / 自定义 runner**：用安装器 + `loopx doctor`，手动连接或在 runner 中调用；
- **DeepSeek Harness**：装原生 dsh 插件选择 loopx 技能（或用 dsh goal-mode 适配器跑无头轮次）。

每一轮续做在机制上都会重新经过 `loopx quota should-run` 闸门——无状态变化即安静跳过且不计费（机制细节见 [概念 01](../concepts/01-control-plane-mechanism.md)）。

## 5. 每日巡检三条命令（官方运营建议）

```bash
loopx status
loopx history --goal-id your-project-goal
loopx quota should-run --goal-id your-project-goal
```

- `status` 看第一屏注意力（目标/门禁/待办）；
- `history` 回看该目标的紧凑运行历史与证据；
- `quota should-run` 确认循环当前是否具备继续条件。

需要给所有者一页式决策视图时，用 `loopx review-packet`（决策、证据、校验与未决门禁的压缩包）。

## 6. 版本控制注意

连接后项目内会出现本地运行态目录，官方要求保持忽略、不要提交（F-046）：

```gitignore
.loopx/
.codex/goals/
.local/
```

## 7. 与博文场景的对应

- 大型重构 / issue 清理：建一个跨周 goal，每日用 status + review-packet 复盘，证据自动落本地；
- 盯 PR / 日报：配定时调度后由 quota should-run 兜底，无变化不花钱；
- 多 Agent：Codex 实现、Claude Code（或另一会话）评审，所有权与交接在 todo claim/update 与 evidence 中显式保留。

场景适配判断见 [概念 02](../concepts/02-evidence-and-fit.md)。
