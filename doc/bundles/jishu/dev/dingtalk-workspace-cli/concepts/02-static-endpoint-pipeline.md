---
okf_version: "0.2"
type: Concept
title: "静态端点管线：把 MCP 工具编译成命令树"
description: "从 internal/syncdata 到 Cobra 命令树的五段展开、十倍放大、生成物守护，以及静态化换来的确定性与付出的版本滞后代价"
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
  - id: architecture
    resource: "docs/architecture.md"
  - id: framework
    resource: "docs/command-framework-architecture.md"
  - id: reference
    resource: "docs/reference.md"
facts: [F-011, F-012, F-026, F-027, F-028, F-029, F-030, F-031, F-032]
---

# 02 · 静态端点管线

> 核心判断：dws 的「确定性」不是在运行时保证的，而是在**构建期**用一条可重放的管线换来的；代价是它与服务端接口之间存在版本时差。

## 1. 五段管线

```text
internal/syncdata           端点数据（唯一来源）
        │
        ▼  ① KeyList         逐端点键清单
   MCP 叶 ToolSpec           单端点工具描述
        │
        ▼  ② 叶 Spec         补齐安全/约束/示例
   CommandRegistry           全部叶命令注册表
        │
        ▼  ③ Cobra 树        生成命令与 help
        └──④ Schema 输出     同一注册表派生
```

（F-026、F-027、F-030）

管线的输入只有一处：`internal/syncdata`。这避免了「命令写一套、文档写一套、Schema 写一套」的三重漂移。

## 2. 十倍放大从哪来

一个 MCP 工具描述的是「一个接口」，而一条命令只描述「一种用法」。因此一个工具会被拆成多条命令：按资源维度拆、按动词拆、按输入形态拆。仓库文档给出的经验比值约为 **10 倍**（F-028）。

这解释了两个现象：

- 命令数远多于接口数，`--help` 的层级必须分组，否则不可用；
- Schema 必须支持**分级浏览**，否则一次性输出会撑爆 Agent 的上下文。

## 3. 生成物守护：让漂移变成红色构建

```text
proto/端点定义  →  生成器  →  提交到仓库的 Go 代码
                                    │
                        git diff --exit-code  ←── 重新生成后比对
```

（F-029）

这条守护只证明一件事：**提交的生成物与生成器一致**。它不证明「生成器与服务端一致」——后者需要定期同步端点数据才能保证（见第 5 节）。

## 4. Schema：不碰服务端的自描述

`dws schema` 的三个「不做」：

| 不做 | 含义 | 收益 |
|------|------|------|
| 不访问 MCP 端点 | 纯本地读取注册表 | 离线可用、毫秒级 |
| 不调用 `tools/list` | 不做运行时发现 | 结果稳定、可缓存 |
| 不读业务数据 | 只描述接口形态 | 无权限也能自查 |

（F-030）

分级查询与字段控制（F-031、F-032）：

```bash
dws schema                      # 总览：有哪些产品
dws schema chat                 # 产品层：有哪些资源与分组
dws schema chat message send    # 叶层：参数、约束、风险、示例
dws schema --all --compact      # 全量 + 白名单字段（供审计/比对）
```

> **洞察**：Schema 分级不是 UI 优化，而是**上下文预算管理**。Agent 一次只能读有限 token，渐进披露让「先看目录、再取单页」成为默认路径，避免把整本手册塞进提示词。

## 5. 收益与代价（必须成对陈述）

| 收益 | 代价 |
|------|------|
| 接口可 diff、可评审、可回滚 | 服务端变更需重新生成并发版才可见 |
| Agent 拿到确定性清单，减少幻觉调用 | 命令行覆盖面受端点数据同步节奏限制 |
| Schema 可离线自检，CI 可做契约测试 | 生成器本身成为关键路径，出 bug 影响面大 |
| help 与 Schema 同源，文档不腐化 | 新人需理解「命令是生成的」，否则会手改生成物 |

**使用建议**：如果你的场景要求「接口今天上线、CLI 今天可用」，静态管线会成为阻碍；如果要求「接口变更可审计、Agent 行为可复现」，它就是必要成本。

## 6. 可迁移的模式：声明即接口

这套做法可以抽象成三步，适用于任何「内部 API → 对外工具面」的场景：

1. **收敛数据源**：把接口描述抽成单一结构化数据，禁止命令层自带知识。
2. **双向派生**：人类文档与机器 Schema 都从同一注册表生成。
3. **生成物入库 + 差异守护**：生成结果提交版本库，CI 用 diff 拒绝手工修改。

三步缺一不可：只做 1 会退化成配置文件，只做 2 会缺少防漂移，只做 3 会在源头不确定时反复生成噪声。

## 7. 常见误解

| 误解 | 事实 |
|------|------|
| 「dws 是 MCP 的代理」 | 它是 MCP 能力的**编译产物**，运行时不依赖 MCP 发现 |
| 「`schema` 是调用接口查出来的」 | 完全本地，不触网（F-030） |
| 「手改生成文件更快」 | 下次生成即被覆盖，且 CI diff 会失败 |

## 延伸

- 契约字段细节：[01-command-contract-model.md](01-command-contract-model.md)
- 面向 Agent 的用法：[07-agent-skills-and-events.md](07-agent-skills-and-events.md)
- 工程守护全貌：[08-engineering-and-boundaries.md](08-engineering-and-boundaries.md)