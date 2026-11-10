---
okf_version: "0.2"
type: Concept
title: "护栏与能力差异：沙箱、审批与扩展模型"
description: "对照四家 harness 的沙箱、审批、权限与扩展机制，说明为什么护栏位置比功能清单更影响选型。"
tags: [sandboxing, approval, permissions, guardrails, extensions, security]
generated: { by: "lobsterai/main", at: "2026-11-10T15:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:05:00+08:00" }
status: stable
stale_after: "2027-04-30"
sources:
  - id: radar
    resource: https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents
  - id: agent-sandboxing
    resource: https://www.thoughtworks.com/radar/techniques/agent-sandboxing
  - id: claude-sdk
    resource: https://code.claude.com/docs/en/agent-sdk/overview
  - id: claude-hosting
    resource: https://code.claude.com/docs/en/agent-sdk/hosting
  - id: codex-sdk
    resource: https://github.com/openai/codex/blob/main/sdk/typescript/README.md
  - id: codex-app-server
    resource: https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md
  - id: opencode-permissions
    resource: https://opencode.ai/docs/permissions/
  - id: pi-readme
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md
---

# 护栏与能力差异：沙箱、审批与扩展模型

> 文章的核心选型判断不是“谁功能多”，而是“护栏放在哪里”：Codex 与 Claude Agent SDK 提供沙箱与审批策略，Pi 把护栏留给扩展（F-017、F-018）。这句话决定了团队要自己做多少安全工作。

## 1. 为什么护栏是选型轴

通用 agent 的风险与编码 agent 不同。

1. 编码 agent 的活动范围通常限定在仓库、终端与构建工具。
2. 通用 agent 可能接触业务系统、客户数据、运营后台与外部 API。
3. 一旦 agent 能发邮件、改配置、调用支付接口，误操作的代价远高于改坏一个文件。

Thoughtworks 在同一期雷达把 **Agent sandboxing** 列为 Adopt，并建议所有 agent 默认在隔离环境运行，按威胁建模做风险分级，遵循最小权限（F-027、F-034）。这不是某个厂商的功能，而是采用 harness 时的底线。

## 2. 三种护栏位置

| 位置 | 作用 | 典型实现 |
|---|---|---|
| 运行时/容器层 | 限制文件、网络、进程与系统调用 | 容器、虚拟机、托管沙箱（F-034、F-045） |
| SDK/服务层 | 决定哪些工具自动运行、哪些需要审批 | permissions、approval policies（F-017、F-044） |
| 扩展/应用层 | 自定义校验、审计、脱敏、业务规则 | hooks、extensions、插件（F-018、F-038） |

三种位置不是替代关系，而是纵深防御。只做一层，通常不够。

## 3. 四家对照

| 维度 | Claude Agent SDK | Codex | OpenCode | Pi |
|---|---|---|---|---|
| 沙箱 | 托管/容器层提供；SDK 有 network sandbox 配置（F-045，E-1） | SDK 可传 `sandbox_workspace_write`（F-046） | 由部署方式决定；server 本身不是沙箱 | 默认不带，交给扩展（F-018） |
| 审批 | permissions：自动运行 / 需审批（F-038） | app-server 有审批请求；`default_permissions` 可配（F-040、F-046） | allow / deny / ask 规则（F-044） | 默认不带，交给扩展（F-018） |
| 钩子/扩展 | hooks、plugins（F-038） | 配置覆盖、app-server 接口（F-039、F-040） | 插件与权限规则（F-044） | extensions、skills、prompt templates（F-043） |
| 默认姿态 | 能力完整，配置项多 | 能力完整，SDK 与服务两种边界 | 权限模型清晰，HTTP 边界 | 最小、可扩展、默认克制 |
| 适配成本 | 中 | 中 | 中 | 低起步、高自定义 |

> 表中 OpenCode 的权限信息来自官方 Permissions 文档（F-044），文章本身未点名 OpenCode 的护栏能力；这是补充事实，不是原文结论。

## 4. Claude Agent SDK：能力全，但沙箱在另一层

Claude Agent SDK 的 permissions 负责“哪些工具自动运行、哪些需要审批”（F-038）。这解决的是**动作级**风险：模型可以提议，但执行前要过人这一关。

沙箱则在更外层。官方托管文档描述每个会话启动 `claude` CLI 子进程，会话记录落本地磁盘，容器化沙箱是一种托管方式（F-045）。因此正确的理解是：

1. 审批在 SDK 层。
2. 沙箱在运行时/托管层。
3. 两者要一起配，不能只配一个（E-1）。

## 5. Codex：SDK 与 app-server 各有护栏入口

Codex SDK 的配置示例包含 `sandbox_workspace_write` 与 `default_permissions: "audit"`（F-046），说明沙箱与权限可以通过 SDK 传入。

app-server 则把审批做成协议的一部分：客户端会收到命令执行审批请求，只能接受、拒绝或取消（F-040）。这对“多人共用一套 agent 服务”的场景很重要——审批不再绑在某个人的终端上，而是由服务统一管理。

选型判断。

1. 单机脚本：SDK 配置足够。
2. 集中式服务：app-server 的审批流更合适。
3. 两者都要：SDK 做开发期，app-server 做生产期。

## 6. OpenCode：权限规则清楚，沙箱靠部署

OpenCode 的权限规则支持 allow、deny、ask 三种效果，无匹配规则时默认 ask（F-044）。这套模型的好处是可读、可版本化、可按工具与资源细化。

但权限规则不是沙箱。它决定“能不能做”，不限制“做了之后能影响多大范围”。如果 agent 能执行 shell，权限允许之后，风险仍然由宿主环境承担。因此 OpenCode 的部署通常需要额外的容器、用户隔离或网络策略。

## 7. Pi：把护栏留给扩展

Pi 的官方定位是 minimal、extensible，默认跳过 sub-agents 与 plan mode，鼓励用扩展、技能、提示模板与主题定制（F-043）。文章把这概括为“刻意把护栏留给扩展”（F-018）。

这意味着两件事。

1. **起步快**：没有一堆默认策略要理解，核心 loop 很轻。
2. **安全要自己补**：审批、审计、沙箱、脱敏都需要通过扩展或宿主环境实现。

Pi 适合“团队有能力自己做安全层、且希望完全掌控运行时”的场景；不适合“希望开箱即用、默认安全”的场景（E-2）。

## 8. 护栏设计的五个反模式

1. **只配审批，不配沙箱**：审批疲劳会让用户习惯性点“允许”，沙箱是最后一道物理边界。
2. **只配沙箱，不配审批**：沙箱能限制影响范围，但不能阻止 agent 在范围内做错事。
3. **默认全允许**：为了“体验流畅”把所有工具设为 allow，等于放弃动作级控制。
4. **扩展无审查**：第三方扩展、技能、插件是供应链风险，未审查就加载等于把执行权交给陌生人。
5. **没有审计**：出了事无法还原“谁在什么时候让 agent 做了什么”。

## 9. 按风险分级选型

| 风险级别 | 任务示例 | 建议 |
|---|---|---|
| 低 | 本地文档整理、只读检索 | 最小 harness 即可，重点是可观测 |
| 中 | 内部运营支持、工单分类、数据清洗 | 审批 + 工具白名单 + 容器隔离 |
| 高 | 生产变更、客户数据、支付/权限操作 | 沙箱 + 审批 + 审计 + 最小权限 + 人工复核 |
| 极高 | 无人值守的自动化决策 | 不建议直接交给通用 agent；必须有人工闸门与回滚 |

## 10. 采用核对清单

1. 沙箱在哪一层？容器、虚拟机，还是宿主进程？
2. 审批覆盖哪些动作？默认 allow 还是 ask？
3. 审批记录能否审计？保留多久？
4. 扩展/插件的来源与签名是否可信？
5. 网络出口是否受限？凭证如何注入？
6. 失败时能否回滚？有没有 kill switch？

## 11. 小结

护栏不是“功能列表里的一行”，而是**运行时架构的一部分**。Claude 与 Codex 把审批做成 SDK/服务能力，OpenCode 用清晰的权限规则表达，Pi 把决定权交给扩展。选型时先画清风险边界，再决定哪一层承担什么责任；否则功能越多，暴露面越大。
