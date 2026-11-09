---
okf_version: "0.2"
type: Example
title: "dws 演练索引"
description: "三条端到端演练——安装与首次登录、日常办公与输出控制、Agent 工作流接入，命令均取自仓库 README"
---

# 演练索引

| # | 篇目 | 类型 | 何时用 |
|---|------|------|--------|
| [00](00-install-and-login.md) | 安装 dws 并完成首次登录 | 操作演练 | 第一次装、登录失败、多组织切换 |
| [01](01-daily-workspace-operations.md) | 日常办公操作与输出控制 | 操作演练 + 速查 | 找人、看日程、查文档、建待办 |
| [02](02-agent-workflow.md) | 把 dws 接入 Agent 工作流 | 操作演练 + 反模式 | 设计 Agent 调用链、订阅事件、raw api 兜底 |

> **来源性质声明**：三条演练的命令逐字取自仓库 `README.md`（F-070 ~ F-081），**本包未实际执行二进制、未核验服务端行为**。企业侧权限、组织开关与返回字段以实际环境为准；执行写操作前务必先 `--dry-run`。

## 按任务挑起点

| 你的处境 | 从这里开始 |
|---------|-----------|
| 还没装 | 00 步骤 1 ~ 2 |
| 装了但登录不上 | 00 步骤 3 ~ 4 + 失败判读表 |
| 有多个组织要切换 | 00 步骤 5 |
| 想知道某条命令怎么写 | 01 场景表 |
| 脚本/Agent 要稳定调用 | 02 七步闭环 |
| 要接收实时消息 | 02 步骤 6 |

```{toctree}
:hidden:
:maxdepth: 2

00-install-and-login
01-daily-workspace-operations
02-agent-workflow
```