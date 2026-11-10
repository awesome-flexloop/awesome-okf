---
okf_version: "0.2"
type: bundle
title: "mini-SWE-agent：100 行 Agent 的极简工程学"
description: "mini-SWE-agent v2.4.6 全栈中文教程——项目谱系与硬指标、bash-only/线性历史/无状态 subprocess 三原则、三协议与 190 行主循环、六类执行环境、toolcall 与 textbased 双通道、YAML 配置与扩展、74% 评测边界、七条可迁移经验；含源码地图（符号/行号/调用链）、3 篇官方文档实操与 4 条博客勘误"
tags: [mini-swe-agent, SWE-agent, SWE-bench, Coding Agent, Python, bash, litellm, Docker, OKF]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: blog-mini-swe-agent
    resource: https://lukaxiya.github.io/coding-agent-blog/posts/mini-swe-agent/
    title: "mini-SWE-agent：100 行代码如何击败了大多数 Agent 框架（AI 编程实战笔记，2026-03-22）"
  - id: github-mini-swe-agent
    resource: https://github.com/SWE-agent/mini-swe-agent
    title: "SWE-agent/mini-swe-agent 官方仓库（v2.4.6，commit 04d809ce）"
  - id: official-docs
    resource: https://mini-swe-agent.com/latest/
    title: "mini-SWE-agent 官方文档"
  - id: blog-facts
    resource: /references/blog-source.md
    title: "博客事实清单 F-001 ~ F-034"
  - id: repo-facts
    resource: /references/repo-source.md
    title: "仓库事实清单 F-035 ~ F-100"
  - id: verification
    resource: /references/verification.md
    title: "P0 核验报告与四条硬勘误"
---

# mini-SWE-agent：100 行 Agent 的极简工程学

> **性质声明**：本 bundle 为**源码教程 + 博客核验**混合型知识包。主体事实来自官方仓库 v2.4.6（commit `04d809ce`，2026-09-03）的源码、官方文档与 GitHub API；博客作为问题导览与观点来源。已发现并校正 **4 条硬勘误**（Stars、SWE-bench 年份、快速开始 API、tool-calling 版本错位），核验详情见 [references/verification.md](references/verification.md)。`examples/` 三篇为官方文档命令，**未在本机实测**。

mini-SWE-agent 是 SWE-bench / SWE-agent 团队的一次反向实验：把 coding agent 的脚手架减到约 100 行核心代码，只给模型一个 bash 工具，用完全线性的消息历史，在 SWE-bench verified 上达到 74%（Gemini 3 Pro，官方声明）。它的价值不在“小”，而在**用最小结构把模型能力、执行环境与轨迹数据拆成三个可替换的协议**。

## 信源说明

| 信源 | 类型 | 覆盖范围 | 状态 |
|---|---|---|---|
| 博客《mini-SWE-agent：100 行代码如何击败了大多数 Agent 框架》 | 第三方解读（2026-03-22） | F-001 ~ F-034 | ✅ 已抓取；4 条勘误 |
| GitHub 仓库 `SWE-agent/mini-swe-agent` | 官方源码 v2.4.6 | F-035 ~ F-100 | ✅ 浅克隆实读 |
| 官方文档 `mini-swe-agent.com/latest` | 官方文档 | Quick Start / CLI / 环境 / 模型 / SWE-bench / FAQ / v2 migration | ✅ 已抓取 |
| GitHub API | 官方元数据 | Stars / forks / license / created_at | ✅ 2026-11-10 快照 |
| 知乎文章 `zhuanlan.zhihu.com/p/2011860096536314782` | 用户提供的第二信源 | — | ❌ 403/404，未使用（F-090） |

## 知识结构总览

```text
mini-swe-agent/
├── concepts/                          # 9 篇概念
│   ├── 00-project-overview.md         # 身份、谱系、版本、硬指标、三个流行误说
│   ├── 01-design-philosophy.md        # bash-only / 线性历史 / 无状态 subprocess
│   ├── 02-architecture-and-code.md    # 三协议、run→step→query→execute_actions
│   ├── 03-execution-environments.md   # local/docker/singularity/bubblewrap/contree/swerex
│   ├── 04-model-integration.md        # 十类模型、toolcall vs textbased、成本与重试
│   ├── 05-configuration-and-extension.md  # YAML 三段、Jinja、轨迹、子类化
│   ├── 06-benchmarks-and-boundaries.md    # 74% 口径、能力边界、不适用场景
│   ├── 07-transferable-lessons.md     # 七条可迁移工程经验
│   └── 08-source-map.md               # 模块/符号/行号、调用链、数据契约、扩展点、测试地图
├── examples/                          # 3 篇官方文档实操（未本机实测）
│   ├── 01-install-and-cli.md
│   ├── 02-python-bindings.md
│   └── 03-swebench-batch.md
├── references/
│   ├── blog-source.md                 # F-001 ~ F-034
│   ├── repo-source.md                 # F-035 ~ F-100
│   └── verification.md                # 11 项 P0 + E-1~E-4 + 单源边界
├── index.md
└── log.md
```

## 核心结论

1. **三条设计原则**：只用 bash、完全线性历史、每个动作独立 subprocess（F-010 ~ F-012、F-054、F-073）。
2. **三个 Protocol**：Agent / Model / Environment 正交拆分；换模型或换沙箱不改循环（F-049 ~ F-062）。
3. **v2 已经转向 tool calling**：默认 `LitellmModel` 使用 `BASH_TOOL`，v1 的“无工具”说法只适用于 textbased 模式（F-060、E-4）。
4. **74% 有官方背书但口径有限**：官方只公布结果与 Gemini 3 Pro 单点，不公开完整评测配置（F-070、F-088）。
5. **博客有三处硬错误**：26k+ Stars（实际 9,496）、SWE-bench 2024（实际 2023）、`MiniSWEAgent`/`result.passed`（不存在）（E-1 ~ E-3）。
6. **源码只有四个动作**：查限制 → 问模型 → 执行动作 → 追加观察；其余是注册、配置、环境适配、序列化与测试（F-091 ~ F-100）。

## 推荐阅读路径

| 目标 | 路径 |
|---|---|
| 先建立全局认识 | 00 → 01 → 02 |
| 想动手跑起来 | 00 → examples/01 → examples/02 |
| 想做评测/研究 | 01 → 06 → examples/03 |
| 想改造/扩展 | 02 → 03 → 04 → 05 |
| 想逐行读源码 | 02 → 08 |
| 只想拿经验 | 07 |

## 主题关联

| 关联知识包 | 关系 |
|---|---|
| [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) | Agent 六大架构模式；本束是其“极简基线”案例 |
| [opencode](../opencode/index.md) | 另一个 terminal coding agent；对比工具集与权限模型 |
| [pi-cli](../pi-cli/index.md) | 极简 CLI Agent；对比 TypeScript 生态的极简实现 |
| [openai-codex](../openai-codex/index.md) | 三语言 coding agent；对比沙箱与审批层 |
| [coding-harness-general-purpose-agents](../../../practice/coding-harness-general-purpose-agents/index.md) | 复用 coding harness 运行时；本束可作为“harness 之前”的基线 |
| [pocketflow](../../pocketflow/index.md) | 另一个“100 行”极简框架；对比节点/流程抽象与 Agent 循环 |

## 核验摘要

| 项 | 结果 |
|---|---|
| P0 项 | 11 项（9 项通过/口径，2 项不成立） |
| 硬勘误 | 4 条（E-1 Stars、E-2 年份、E-3 API、E-4 tool-calling） |
| 单源边界 | 6 条（74% 配置、对比表、采用者、启动速度、能力边界、知乎缺口） |
| 版本锁定 | v2.4.6 / commit `04d809ce` / 2026-09-03 |

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
examples/index
references/index
log
```
