---
type: Concept
title: "L2 场景、L3 Persona 与自定义 Prompt：策略可编辑，契约不可改"
description: "SceneExtractor 参数与 META/heat 文件格式、场景索引重建、Persona 五类触发、scope 行级校验，以及 memory-prompt 四级解析、限额、守卫与 SHA-256 审计。"
tags: [tencentdb-agent-memory, concept, scene, persona, memory-prompt, audit]
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

# L2 场景、L3 Persona 与自定义 Prompt：策略可编辑，契约不可改

> **本篇看点**：L2 场景由 SceneExtractor 以 300 秒超时抽取为 `scene_blocks/*.md`，文件用 META_START/META_END 包裹含 heat 的元数据，索引可通过 syncSceneIndex 全量重建（F-081~F-084）。L3 Persona 有五类触发条件，并以 scope 串与行级校验守住多租户边界（F-085~F-087）。自定义记忆 Prompt 按 agent → team → instance → 内置四级解析，每实例 500 条、单条 10000 字符上限（F-088/F-089）；用户能改策略文本，不能改 L1=JSON/L2=Scene Markdown/L3=Persona+Doctrine 的输出协议，审计只留 SHA-256 不留正文（F-090~F-092）。这正是 spec/insights.md 洞察四概括的「策略可编辑，契约不可改，且正文不留痕」。

## SceneExtractor：300 秒、备份与上限

SceneExtractor 的参数包含 timeoutMs=300000（5 分钟）、sceneBackupCount（场景备份数）、maxScenes（场景上限）（F-081）。抽取超时按 5 分钟封顶，备份数与上限控制场景文件的数量与安全垫（F-081）。

## 场景文件格式：META 分隔符与 heat

场景文件使用 META_START/META_END 分隔符包裹元数据，元数据中含 heat（热度）数值，格式定义于 scene/scene-format.ts（F-082）：

```text
scene_blocks/<某场景>.md
<META_START>
... 元数据区（含 heat 数值）...
<META_END>
... 场景正文（Markdown）...
```

heat 表达场景的活跃程度，是场景索引与导航使用的元数据（F-082）。

## 场景索引：syncSceneIndex 重建与导航派生

syncSceneIndex 通过扫描 `scene_blocks/*.md` 重建场景索引，实现于 scene/scene-index.ts（F-083）。这意味着索引是派生物：文件是事实源，索引丢失或损坏后可从文件全量重建（F-083）。场景导航与派生分别实现于 scene-navigation.ts 与 scene-derive.ts（F-084）。

## Persona 五类触发

Persona（L3）的触发分 5 类，实现于 persona-trigger.ts（F-085）：

| # | 触发类型 | 触发时机 |
|---|---|---|
| 1 | 显式请求 | 用户/Agent 明确要求更新画像（F-085） |
| 2 | 冷启动 | 新团队/新 Agent 首次运行（F-085） |
| 3 | 恢复 | 从既有状态恢复时（F-085） |
| 4 | 首个 scene block | 第一个场景块产生时（F-085） |
| 5 | 阈值触发 | 累计量达到设定阈值时（F-085） |

## scope 串与行级校验

profile-scope.ts 定义 scope 串形态 `team:...|agent:...`，并提供 profileScopeFilter 与 profileRowInScope 两个机制：前者做过滤，后者做行级校验（F-086）。profile-sync.ts 负责 profile 在不同作用域之间同步（F-087）。

```text
scope 串： team:<team 标识>|agent:<agent 标识>
读取：     profileScopeFilter(scope)  —— 过滤出作用域内的行
写入/校验：profileRowInScope(row, scope) —— 逐行判定是否越界（F-086）
```

行级校验以纯函数方式存在，使「这条 Persona 是否属于该 team/agent」可在存储边界独立判定（F-086）。

## memory-prompt 四级解析

memory-prompt 的解析优先级为 agent → team → instance → 内置默认，实现于 memory-prompt/resolver.ts（F-088）：

```text
agent 级 Prompt   （最优先，per-Agent 差异化）
   ↓ 缺失
team 级 Prompt    （团队共性策略）
   ↓ 缺失
instance 级 Prompt（实例默认）
   ↓ 缺失
内置默认 Prompt   （兜底）（F-088）
```

## 限额与版本：500 条 / 10000 字符 / id 不变

每个 instance 最多 500 条 prompt，单条 prompt 不超过 10000 Unicode 字符；更新时版本号递增，但 memory_prompt_id 保持不变（F-089）。id 不变保留了「策略实体」的身份，版本递增保留了「同一策略的演化史」（F-089）。

## 占位符注入与 GUARD 守卫

composer 注入两个占位符：`<CUSTOM_MEMORY_STRATEGY>` 承载用户自定义策略文本，`<SYSTEM_CUSTOM_STRATEGY_GUARD>` 作为守卫约束其生效边界，实现于 memory-prompt/composer.ts（F-090）。自定义内容被限定在占位符内，而非整体替换系统提示词（F-090）。

## 固定输出协议不可改

三层输出协议被钉死，不可通过自定义 prompt 修改（F-091）：

| 层 | 固定输出格式 |
|---|---|
| L1 | JSON（F-091） |
| L2 | Scene Markdown（F-091） |
| L3 | Persona + Doctrine（F-091） |

用户能改的是「怎么判断、怎么措辞」的策略，不能改的是「以什么结构交卷」的契约；解析器期望的 schema 因此是冻结接口（F-091）。这一拆分即 spec/insights.md 洞察四的核心：可变策略文本与不可变协议骨架分离（F-090、F-091）。

## 审计：记录 SHA-256，不存正文

生成日志记录 Prompt ID、版本、来源、SHA-256，不存储 prompt 正文（F-092）。团队自定义 prompt 可能包含业务 know-how，因此按机密处理而非日志留存；复现与合规校验依靠哈希对拍，而非调阅原文（F-092）。

## API 面

| 路径 | 能力 |
|---|---|
| `/v3/memory-prompt/*` | create / get / update / delete / set / log（F-093） |
| `/v3/memory-generation-log/list` | 生成日志列表（F-093） |
| `/v3/memory-generation-log/get` | 单条生成日志（F-093） |

memory-prompt 与 memory-generation-log 各自独立成面，配合完成「自定义 + 可审计」闭环（F-093）。

## 延伸阅读

- 上一篇：[02-l0-l1-pipeline.md](02-l0-l1-pipeline.md)——L0/L1 抽取去重管线
- 下一篇：[04-storage-retrieval.md](04-storage-retrieval.md)——存储后端与混合检索
- 背景模型：[01-four-layer-memory.md](01-four-layer-memory.md)
- 信源：[README 与 CHANGELOG](../references/02-readme-changelog.md)、[源码地图](../references/01-source-code-map.md)
