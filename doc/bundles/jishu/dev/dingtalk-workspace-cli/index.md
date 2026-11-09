---
okf_version: "0.2"
type: bundle
title: "钉钉工作区 CLI（dws）：命令契约、静态管线与 Agent 集成"
description: "面向人与 AI Agent 的钉钉工作区命令行——命令契约模型、静态端点管线、20 个服务域、OAuth 多组织身份、输出与 Schema 契约、安全预览与审计、Agent 技能与事件、工程门禁与边界"
tags: [钉钉, DWS, CLI, Go, AI Agent, MCP, Schema, OAuth, 企业协作, 命令契约, 静态生成, 源码学习]
generated: { by: "seven-concepts-cmd", at: "2026-11-09T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-09T12:00:00+08:00" }
status: stable
stale_after: 2027-02-28
sources:
  - id: repo
    resource: "\\\\10.16.11.3\\ai\\notebook\\dev\\libs\\dws\\dingtalk-workspace-cli"
    title: "dingtalk-workspace-cli 源码（HEAD c631e4fb，v1.0.68-beta.1）"
  - id: facts
    resource: /references/facts.md
    title: "源码事实登记 F-001 ~ F-081"
  - id: verification
    resource: /references/verification.md
    title: "核验报告、口径冲突与对抗审查"
---

# 钉钉工作区 CLI（dws）：命令契约、静态管线与 Agent 集成

> **性质声明**：本包由 **seven-concepts-cmd 技能（R→I→E→C）** 对仓库 `HEAD c631e4fb`（`v1.0.68-beta.1`）只读学习生成，属**源码一手研读**，非官方文档转述，亦非实测报告。
>
> **三条硬边界**：① **未执行 `dws` 二进制**，所有行为结论来自源码、README 与 `docs/`；② **未逐包审阅** 59 个 `internal/` 一级包，只精读架构、命令框架、Schema、认证、安全与技能相关部分；③ **未访问钉钉服务端**，接口行为、返回字段与限流口径不在核验范围。
>
> 引用任何数字前请先读 [事实登记](references/facts.md) 与 [核验报告](references/verification.md)。

## 这是什么

dws 是钉钉官方的**工作区命令行工具**，用 Go 编写，Apache-2.0 许可，同时面向人与 AI Agent：人用 `--help` / `--dry-run` / `--format table`，Agent 用 `--format json` / `--jq` / 内置 Skills（F-009 ~ F-014）。

它的结构性特点有两条：**命令表在编译期静态生成**（不依赖运行时 `tools/list`），以及**同一份 `corecmd.Spec` 契约同时驱动 Cobra 命令树与 MCP Schema**——所谓「双表面同源」（F-026 ~ F-032）。

## 结构总览

```text
dingtalk-workspace-cli/
├── index.md                 ← 本文件（性质声明 + 分层导航 + 边界）
├── log.md                   ← 生成日志（R→I→E→C 过程与质量门记录）
├── concepts/                ← 概念层（9 篇）
│   ├── index.md
│   ├── 00-overview-and-positioning.md    ← 定位层：是什么/给谁用/不适用
│   ├── 01-command-contract-model.md      ← 结构层：Spec 七面与约束系统
│   ├── 02-static-endpoint-pipeline.md    ← 架构层：五段管线与生成物守护
│   ├── 03-command-surface-and-products.md← 结构层：20 服务域与产品归并
│   ├── 04-auth-identity-and-profiles.md  ← 机制层：三条登录路径与多组织
│   ├── 05-output-and-schema-discovery.md ← 接口层：格式/投影/退出码/Schema
│   ├── 06-safety-dry-run-and-audit.md    ← 治理层：预览/确认/审计/出站
│   ├── 07-agent-skills-and-events.md     ← 集成层：技能布局/事件/raw api
│   └── 08-engineering-and-boundaries.md  ← 边界层：门禁/测试/选型/缺口
├── examples/                ← 演练层（3 篇，命令取自 README）
│   ├── index.md
│   ├── 00-install-and-login.md
│   ├── 01-daily-workspace-operations.md
│   └── 02-agent-workflow.md
└── references/              ← 信源层（事实先行）
    ├── index.md
    ├── facts.md             ← F-001 ~ F-081
    └── verification.md      ← 核验、冲突 C-1~C-4、对抗 D-1~D-7
```

## 分层导航

- **先判断值不值得用**：[00 定位与全景](concepts/00-overview-and-positioning.md)——双表面、20 服务域、三个不适用
- **理解它怎样组织命令**：[01 命令契约模型](concepts/01-command-contract-model.md)——`corecmd.Spec` 七个面、五级回退、三类执行体、五条不变量
- **看命令表从哪来**：[02 静态端点管线](concepts/02-static-endpoint-pipeline.md)——五段管线、十倍放大、生成物守护
- **看产品怎么切**：[03 命令面与产品组织](concepts/03-command-surface-and-products.md)——两把尺子、三个归并决策
- **要登录与多组织**：[04 认证、身份与多组织](concepts/04-auth-identity-and-profiles.md) → [演练 00](examples/00-install-and-login.md)
- **要写脚本/接 Agent**：[05 输出与 Schema 发现](concepts/05-output-and-schema-discovery.md) → [07 Agent 技能与事件](concepts/07-agent-skills-and-events.md) → [演练 02](examples/02-agent-workflow.md)
- **要管安全与合规**：[06 安全、预览与审计](concepts/06-safety-dry-run-and-audit.md)
- **要做技术选型或二次开发**：[08 工程与边界](concepts/08-engineering-and-boundaries.md)
- **要溯源/质疑时**：[信源登记簿](references/index.md)、[事实登记](references/facts.md)、[核验报告](references/verification.md)

## 信任与生命周期

| 维度 | 裁决 |
|------|------|
| status | **stable**（核心结构——双表面同源、静态管线、契约模型、五条不变量——均有源码与官方架构文档双重依据） |
| 信源距离 | 源码一手研读 + 官方仓库文档；无第三方转述，无厂商自宣成效数字 |
| 核验规模 | 81 条事实（F-001 ~ F-081）+ 4 条口径冲突 + 7 条对抗意见 |
| stale_after | **2027-02-28**；上游发稳定版、Schema/命令面变更、CI 门禁调整即触发复核 |

## 已知边界

1. **无运行时实测**：未执行二进制，安装、登录、事件订阅的实际表现均未验证；演练命令以 README 为准。
2. **版本是 beta**：`v1.0.68-beta.1`，命令面与 Schema 仍可能变动；正式采用前应核对当期稳定版。
3. **服务域计数存在两个口径**：README 口径为 20 个服务域，`docs/command-index.md` 快照为 13 个产品 / 180 条命令；两者维度不同，已在 [核验报告](references/verification.md) 记为 C-1，本包不强行统一。
4. **Go 版本口径超前**：仓库声明 Go 1.26.7，高于常见稳定版本认知，记为 C-2；以仓库实况为准，未验证工具链可得性。
5. **无全量命令总数**：快照只覆盖 `docs/command-index.md` 所列，记为 C-4；不要在对外材料中声称「共 N 条命令」。
6. **文档数字易腐**：仓库规模、文档篇数、技能脚本数会随提交变化，正文一律引用 F 编号而非复制数字。
7. **未覆盖服务端语义**：权限模型、限流、字段级返回、错误码映射均以服务端为准，本包只描述客户端契约。

## 主题关联

- 同组 [plane](../plane/index.md)：协作平台类工具的自托管对照——一个管项目，一个管企业工作区
- 上级 [dev](../index.md)：开发与协作工具组
- 上级 [jishu](../../index.md)：技术域总索引

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```