---
type: Concept
title: "四层记忆模型：L0–L3 与四类记忆资产"
description: "梳理 Chat Memory 的 L0 对话、L1 原子、L2 场景、L3 Persona 四层，以及 Skill/Wiki/CodeGraph 资产、可见性四值与角色模型。"
tags: [tencentdb-agent-memory, concept, memory-model, persona, asset, visibility]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-readme
    resource: /references/02-readme-changelog.md
    title: README 与 CHANGELOG 信源
---

# 四层记忆模型：L0–L3 与四类记忆资产

> **本篇看点**：Chat Memory 被组织为 L0 Conversation → L1 Atom → L2 Scenario → L3 Core/Persona 四个层级，原始对话以 JSONL 按天落盘，逐层抽取为原子记忆、场景文件与长期认知（F-037~F-040）。在此之外还有 Skill、Wiki、CodeGraph 三类资产，配合 private/team/restricted/agent 四值可见性、两层角色与 Agent Loadout 做装配（F-041~F-048）。本篇并列登记数据目录的两套历史口径，并概述 v3 数据格式、混合检索与兼容 API 面（F-050~F-056）。

## 四层总览

```text
L0 Conversation  原始对话（事实留痕，JSONL 按天）
      ↓ 抽取
L1 Atom          原子记忆（persona / episodic / instruction）
      ↓ 聚合
L2 Scenario      场景（scene_blocks/*.md，带 META 与 heat）
      ↓ 升华
L3 Core/Persona  长期认知（跨会话 Persona）
```

Chat Memory 分上述四个层级（F-037）。越往下层抽象度越高、信息密度越大；L0/L1 的抽取去重管线见 [02-l0-l1-pipeline.md](02-l0-l1-pipeline.md)，L2/L3 的文件格式与触发机制见 [03-l2-scene-l3-persona.md](03-l2-scene-l3-persona.md)（F-037）。

## L0 Conversation：JSONL 按天存储

L0 是原始对话层，以 JSONL 按天存储，路径形态为 `conversations/YYYY-MM-DD.jsonl`（F-038）。按天切分意味着 L0 是只追加的事实留痕，不依赖向量或 LLM 即可存在（F-038）。

## L1 Atom：原子记忆三分类

L1 是从对话中抽取出的原子记忆，类型上分为事实、偏好、约束、事件等，并归为 persona / episodic / instruction 三大类（F-039）。三大类的含义可据名称对应为：画像类、经历事件类、指令约束类，抽取的默认参数与去重决策在管线篇展开（F-039）。

## L2 Scenario：Markdown 场景块

L2 以 Markdown 文件存储在 `scene_blocks/*.md`，文件内含 META 分隔符与 heat（热度）数值（F-040）。场景层把一段段相关对话聚合成可导航、可检索的 Markdown 场景块，heat 用于表达其活跃程度（F-040）。

## L3 Core/Persona：长期认知

L3 为 Core/Persona 长期认知层，代表跨会话沉淀下来的稳定画像与准则（F-037）。Persona 的更新由五类触发条件驱动，作用域通过 scope 串与行级校验控制，细节见场景与 Persona 篇（F-037）。

## 四类记忆资产

除 Chat Memory 外，系统还有 Skill、Wiki、CodeGraph 三类资产，合计四类（F-041）：

| 资产 | 内容与机制 |
|---|---|
| Chat Memory | 即 L0–L3 四层对话记忆（F-041） |
| Skill | 从跑通的任务里提炼可复用 SOP，附带版本、资源文件、触发边界、执行步骤、验证规则；2.0.0 新增 Skill 强制归档功能（F-042） |
| Wiki | 把文档变成结构化页面 + 链接图谱，README 注明灵感来自 Karpathy 的 LLM 知识库实践（F-043） |
| CodeGraph | 索引仓库的符号、文件、调用关系、影响路径，供 Agent 改代码前做 impact analysis；2.0.0 新增定时自动同步代码库（F-044） |

README 致谢声明确认：CodeGraph 复用了 github.com/colbymchenry/codegraph 的代码，Hermes Agent skill 代码亦为复用（F-045）。

## 可见性四值

记忆资产的可见性包含四个取值（F-046）：

| 取值 | 含义 |
|---|---|
| private | Owner 只读，团队管理员不可见（F-046） |
| team | 团队内可见（F-046） |
| restricted | 基于 User / Role / Agent 的 ACL 控制（F-046） |
| agent | 同团队 Agent 定向装配（F-046） |

注意 private 对团队管理员同样不可见，可见性模型刻意不给管理员上帝视角（F-046）。

## 两层角色、Owner 与 Loadout

角色分两层：全局的 System Admin，以及团队内的 Admin/Member；Owner 自动获得管理权（F-047）。Agent Loadout 机制支持给不同 Agent 绑定不同资产，并调整优先级与使用方式，是与可见性正交的 per-Agent 装配维度（F-048）。

## 使用约束

CodeGraph 当前仅支持公开 HTTPS 仓库；Wiki 与 CodeGraph 均为异步构建，使用前需等待 ready 状态（F-049）。这意味着导入仓库或文档后不能立即假设可检索，消费端必须按构建状态机等待（F-049）。

## v2→v3 数据格式迁移

v2.0.0 起数据格式为 v3，仓库提供 v2→v3 迁移脚本目录 `MemoryCore/scripts/migrate-v2-to-v3/`（含 README）（F-050）。跨大版本升级应先阅读该目录说明再迁移数据（F-050）。

## 混合检索概述

检索采用 RRF 融合 BM25 与向量的混合检索，并受条数、字符预算与超时限制三类约束（F-051）。RRF 属于后融合：各通道分别出结果后按排名融合，单路缺失时仍可工作，存储侧参数见 [04-storage-retrieval.md](04-storage-retrieval.md)（F-051）。

## 数据目录的两套口径

数据目录存在两套历史口径，并列登记，不做单边取舍（F-054、F-055）：

```text
口径 A（README）：   ~/.memory-tencentdb/memory-tdai
口径 B（代码注释）： ~/.openclaw/memory-tdai/conversations/
                     （l0-recorder.ts 注释，历史遗留）
```

README 声明的默认数据目录为 `~/.memory-tencentdb/memory-tdai`（F-054）；l0-recorder.ts 注释中出现的 `~/.openclaw/memory-tdai/conversations/` 是另一套历史口径（F-055）。

## 兼容 API 面

README_CN 描述的 API 面包含两组：兼容接口 `/capture`、`/recall`、`/search/*`，以及分层接口 `/v2/conversation`、`/v2/atomic`、`/v2/scenario`、`/v2/core`（F-056）。前者面向既有调用方做无痛接入，后者按四层模型显式分层（F-056）。

## 版本路标（背景）

README 标注当前版本为 v2.0.0，ROADMAP 列出的 v2.0.1 方向包括零配置冷启动、Wiki 加速、自定义 Prompt、Skill 导出、Codex IDE Plan（F-052）；ROADMAP_CN 的「下个版本 · v2.0.1」清单另含 Agent 模版、`mem:` 指令增强、记忆可编辑、L0/L1 记忆搜索、Cursor 支持等项（F-053）。

## 延伸阅读

- 上一篇：[00-overview.md](00-overview.md)——产品定位与部署形态
- 下一篇：[02-l0-l1-pipeline.md](02-l0-l1-pipeline.md)——L0/L1 抽取-去重-写入管线
- 并行参考：[03-l2-scene-l3-persona.md](03-l2-scene-l3-persona.md)、[04-storage-retrieval.md](04-storage-retrieval.md)
- 信源：[README 与 CHANGELOG](../references/02-readme-changelog.md)、[源码地图](../references/01-source-code-map.md)
