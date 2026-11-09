---
okf_version: "0.2"
type: Concept
title: "Agent 集成：Schema、Skill、Event 三个界面"
description: "dws 面向 AI 的三条接入路径——可查询的命令 Schema、按产品分装的 Skills、可订阅的事件流，以及 raw API 与 Agent 标识的边界"
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
  - id: readme
    resource: "README.md"
  - id: skill
    resource: "skills/"
facts: [F-010, F-030, F-031, F-053, F-054, F-055, F-056, F-057, F-058, F-059, F-060, F-062]
---

# 07 · Agent 集成

> 核心判断：Agent 不需要「更多工具」，需要**更少的歧义**。dws 用三个界面分工——Schema 解决「怎么调」，Skill 解决「先做什么」，Event 解决「什么时候做」。

## 1. 三个界面各管什么

| 界面 | 形态 | 回答的问题 | 不该用它做什么 |
|------|------|-----------|--------------|
| Schema | `dws schema <path>` | 这条命令要哪些参数、有什么约束与风险 | 不要用来获取业务数据 |
| Skill | `skills/multi/*`（16 个产品技能）、`skills/mono`（单技能） | 一个业务任务的步骤、字段规则、错误码 | 不要当作接口文档的替代 |
| Event | `dws event consume <EventCode>` | 什么事件发生了、如何持续监听 | 不要用来轮询状态 |

（F-030、F-053、F-056）

## 2. Schema：确定性优先

- 完全本地派生，不触网（F-030）；
- 分级查询，避免一次性灌满上下文（F-031）；
- 叶层带 effect/risk/confirmation，Agent 可据此决定是否请求人工确认。

推荐调用序列：

```text
dws schema                    # 1. 先看有哪些产品
dws schema chat               # 2. 锁定产品
dws schema chat message send  # 3. 取单条命令的完整契约
```

不要一上来 `dws schema --all`：体量大、噪声多，且会挤占推理预算。

## 3. Skill：把「业务常识」装进 Agent

两种布局（F-053）：

| 布局 | 结构 | 适用 |
|------|------|------|
| `multi` | 16 个产品级技能（chat、calendar、aitable、doc、mail、minutes、event……） | 按需加载，上下文占用小 |
| `mono` | 单个总技能，含 `products/`、`references/`、`scripts/` 共 37 个脚本 | 一次装全，适合重型工作流 |

安装方式（F-054）：

```bash
npx skills add DingTalk-Real-AI/dingtalk-workspace-cli
dws skill setup --mode multi --target <技能目录>
```

状态管理（F-055）：

- 安装记录写入 `skills-state.json`，记录归属与版本；
- 安装前自动备份；
- `mono` 与 `multi` 互切时清理对方产物，避免两套技能同时命中。

> **洞察**：Skill 与 Schema 的分工很像「菜谱」与「食材清单」。Schema 保证每一步合法，Skill 保证整体流程正确。只给 Agent Schema，它会用合法步骤做出错误流程；只给 Skill，它会在字段层面反复试错。

## 4. Event：从「轮询」转向「订阅」

事件目录共 33 个事件（F-056），命令族：

| 命令 | 作用 |
|------|------|
| `dws event list` | 列出事件与分类 |
| `dws event schema` | 查看某事件的载荷结构 |
| `dws event consume <EventCode>` | 订阅并输出事件 |
| `dws event status` / `stop` | 查看/停止订阅进程 |

输出与传输（F-057）：

```bash
dws event consume <EventCode> --flatten
```

- 以 NDJSON 逐行输出到 stdout，天然适合管道；
- `--flatten` 展平嵌套载荷，减少下游解析层级；
- 支持跨进程共享本地总线（Unix Socket / Named Pipe），多个消费者可复用一条订阅。

**工程注意**：消费进程是长驻的，脚本必须处理重连与退出码 6（限流/服务端错误），不能假设一次连接永久有效。

## 5. Raw API：能力兜底，但请隔离

```bash
dws api GET /v1.0/contact/users/me
dws api POST <path> --data @payload.json
dws api GET <path> --page-all --page-limit 50
```

（F-058）

| 特性 | 说明 |
|------|------|
| 双域自动识别 | 按路径判断走哪个开放平台域 |
| 文件体 | `--data @file` 传 JSON；`--file` 走 multipart |
| 分页 | `--page-all` 自动翻页，默认 10 页、上限 500 |
| 边界 | 受域名白名单约束；**不出现在 Agent Schema 中**（F-060） |

把 raw API 当作「人类排障通道」，而不是 Agent 的常规能力。一旦让 Agent 自由使用 raw，命令契约、确认门、审计语义都会被绕过。

## 6. Agent 标识与归属

| 变量 | 作用 |
|------|------|
| `DWS_AGENT_PRODUCT` | 调用方产品名 |
| `DWS_AGENT_HOST` | 运行宿主 |
| `DWS_AGENT_VER` | 调用方版本 |
| `DWS_AGENT_EXT` | 扩展信息 |

（F-059）

`--ai-tag` 默认开启，把上述信息注入请求头，便于服务端区分「人调用」与「Agent 调用」，也便于审计归因。

## 7. 本地开发桥接

`dws dev connect` 把消息机器人接到本地 AI CLI（F-062）：

```bash
dws dev connect --channel auto --unified-app-id <appId>
```

- 会话内可用 `/new` 重置上下文、`/clear` 清理；
- 适合「在钉钉里 @ 机器人，由本地模型干活」的闭环开发；
- 与业务命令不同，它管理的是**本地进程与会话**，不是云端资源。

## 8. 反模式

| 反模式 | 后果 | 替代 |
|--------|------|------|
| 把 `--all` Schema 塞进系统提示 | 上下文爆炸、注意力稀释 | 分级查询 |
| 同时安装 mono 与 multi | 技能重复命中、行为不确定 | 二选一，切换时清理 |
| 让 Agent 调 raw api | 绕过契约与审计 | 用标准命令 |
| 用事件流做同步请求 | 延迟高、顺序无保证 | 事件做触发，命令做执行 |

## 延伸

- 安全约束：[06-safety-dry-run-and-audit.md](06-safety-dry-run-and-audit.md)
- 完整工作流示例：[examples/02-agent-workflow.md](../examples/02-agent-workflow.md)
- 对抗意见 D-2、D-5：[references/verification.md](../references/verification.md)