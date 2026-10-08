---
type: Concept
title: "Skill 记忆：版本化快照、head 索引与 17 个 v3 端点"
description: "Skill 子系统以 skills/skill_fts/skill_vec 三物理对象承载不可变多版本快照，并通过 17 个 /v3/skill/* 端点对外提供创建、抽取、文件与归档能力。"
tags: [tencentdb-agent-memory, concept, skill, memorycore, versioning, fts5, vec0]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-core-api
    resource: /references/03-api-references.md
    title: v3 API 三卷信源
---

# Skill 记忆：版本化快照、head 索引与 17 个 v3 端点

> **本篇看点**
>
> - Skill 数据层 v2 只有三张物理对象，并刻意不建绑定/草稿/资源类表（F-131）。
> - 每个版本是不可变快照：`UNIQUE(skill_id, version)`，唯一名约束只作用于 head 行（F-132、F-133）。
> - FTS5 + vec0 双索引围绕 head 与预算设计，正文超 4000 字不进全文索引（F-134~F-136）。
> - 对外是 17 个 `/v3/skill/*` 端点，service 模式按 instance 解析各自的 SkillCore（F-145、F-146）。

## 1. 三物理对象与「故意不建的表」

Skill 数据层 v2 重构只落三张物理对象：`skills` 主表、`skill_fts`（fts5 虚表）、`skill_vec`（vec0 虚表，仅 dimensions>0 时创建）；DDL 注释明确不建 `skill_bindings`、`task_skill_drafts`、`skill_resources`、`assets` 等表——绑定下沉管控面、资源 manifest 收敛进主表（F-131）。

| 物理对象 | 类型 | 职责 |
|---|---|---|
| `skills` | 主表 | 版本化主数据与 manifest（F-131、F-132） |
| `skill_fts` | fts5 虚表 | 名称/描述/正文全文检索（F-131、F-134） |
| `skill_vec` | vec0 虚表 | 语义向量检索，仅 dimensions>0 创建（F-131、F-135） |

## 2. 主表字段与六个索引

主表除 `row_id` 行标识外含 17 个字段，并设 `UNIQUE(skill_id, version)`（F-132）：

| 分组 | 字段（F-132） |
|---|---|
| 版本标识 | `skill_id`、`version`、`is_head` |
| 隔离归属 | `user_id`、`owner_agent_id`、`team_id`、`task_id` |
| 内容 | `name`、`description`、`content`、`content_hash` |
| 承载 | `manifest_json`、`storage_dir`、`status`、`metadata_json` |
| 时间戳 | `created_at_ms`、`updated_at_ms` |

主表共 6 个索引，其中唯一索引是 head-only 的部分索引（F-133）：

| # | 索引 | 说明（F-133） |
|---|---|---|
| 1 | `uniq_skills_team_agent_name_head` | 作用于 (team_id, owner_agent_id, name)，且仅 `is_head=1 AND status='active'` |
| 2 | team 辅助索引 | 按团队检索 |
| 3 | owner 辅助索引 | 按 owner Agent 检索 |
| 4 | user 辅助索引 | 按用户检索 |
| 5 | version 辅助索引 | 版本查询 |
| 6 | task 辅助索引 | 按任务检索 |

## 3. FTS5、vec0 与 4000 字预算

- `skill_fts` 索引 `name`/`description`/`content` 三列，另带四个 `UNINDEXED` 隔离列；分词器为 `unicode61 remove_diacritics 1`（F-134）。
- `skill_vec` 声明 `embedding float[__DIM__]`、`distance_metric=cosine`；`__DIM__` 在 init 时替换为实际维度（如 1536）（F-135）。
- FTS 索引正文存在字符预算：常量 `FTS_CONTENT_MAX=4000`，超出部分不进 FTS（F-136）。

## 4. create / update / delete / get 流程

SkillCore 的写路径先解析校验 SKILL.md，再生成或校验 `skill_id`，随后调用 SkillVersioning 创建或追加版本；校验失败抛 `SkillCoreError`（F-137）。

```text
create / update
  请求 → 解析校验 SKILL.md → 生成或校验 skill_id
       → SkillVersioning 创建/追加版本 → 写库
       失败：抛 SkillCoreError（F-137）
```

- `delete` 物理删除该 skill 的所有版本，并触发归档回调（F-138）。
- `writeFiles` 依次经过 requireHead 校验、owner 校验与乐观锁校验，然后追加新版本（F-138）。
- `get` 读路径支持指定版本或默认取 head；指定版本时先确认 head 存在，再按 (skill_id, version, team_id) 查询，并触发访问后处理（F-139）。

## 5. 权限纯函数与错误码

权限校验实现为纯函数，包含三类判定：owner 校验、team 匹配、`expected_version` 与 head version 一致性的乐观锁校验；错误码分别对齐 403/404/409（F-140）。

## 6. 版本追加与向量增量

版本追加由 SkillVersioning 承担，先算新版本号并检测内容/资源是否变化，再拷贝旧版本目录、应用资源变更、写 DB，最后同步 VDB delta（F-141）。

```text
版本追加
  计算新 version → 检测内容/资源是否变化 → 拷贝旧版本目录
  → 应用资源变更 → 写 DB → 同步 VDB delta（F-141）
```

## 7. Skill 抽取：三档预检索与异步排队

抽取入口先校验 `ExtractMessage[]`，对 transcript 做格式化与截断，再按 `prefixSkillsLimit` 做 full / relevant / recent 三档预检索，最后组装 LLM prompt（F-142）。配套模块上，`skill-fast-path.ts` 提供快速通道，`skill-config.ts` 管配置、`skill-format.ts` 负责 SKILL.md 格式化、`skill-tools.ts` 定义供 Agent 调用的工具（F-143）；异步提取排队由 `queue/`（index.ts、types.ts）承载（F-144）。

## 8. 17 个 v3 端点

`/v3/skill/*` 共注册 17 个端点（F-145）：

| # | 端点 | # | 端点 |
|---|---|---|---|
| 1 | `create` | 10 | `files/write` |
| 2 | `update` | 11 | `files/remove` |
| 3 | `patch` | 12 | `files/read` |
| 4 | `delete` | 13 | `export` |
| 5 | `get` | 14 | `listing` |
| 6 | `get-by-name` | 15 | `extract` |
| 7 | `list` | 16 | `conversation/add` |
| 8 | `search` | 17 | `conversation/force-archive` |
| 9 | `versions` | | |

handler 前置解析在 service 模式优先 `resolveSkillCore(auth.serviceId)` 取 per-instance core，回退到 standalone 的 `getSkillCore()`，然后才校验请求参数（F-146）。请求 schema 用 Zod 定义在 `skill-schemas.ts`；手动触发抽取的契约照搬 `/v3/skill/conversation/add`（F-147）。

## 9. 双存储实现与两个插件子包

- TCVDB 与 SQLite 各有一份 Skill 存储实现：`store/tcvdb/skill-store.ts` 与 `store/sqlite/skill-store.ts`（F-148）。
- `openclaw-plugin` 子包含独立 package.json、`openclaw.plugin.json` 以及 `hooks/capture.ts`、`hooks/recall.ts`、`format.ts`、`sanitize.ts`（F-149）。
- `pi-plugin` 子包为 pi 平台插件，含 index.ts、package.json、vitest.config.ts（F-150）。

## 10. 设计解读：不可变快照与「工具化」资产

按洞察六的解读，Skill 与 Wiki、CodeGraph 同属「随用随取的工具」，而非每轮灌进提示词的知识库：每个版本是不可变快照（F-141），同名唯一约束只压在 head 行上（F-133），正文超过 4000 字不进 FTS（F-136），抽取前还按 full/relevant/recent 三档预算预选已有技能（F-142）。这共同体现「资产可演化、调用可钉版本」的取舍：版本历史不可变，head 承担当前生效身份，长文需靠名称与描述承载可检索性。

## 延伸阅读

- [04 存储后端与混合检索](04-storage-retrieval.md)
- [06 网关与隔离契约](06-gateway-isolation.md)
- [实战 04：Wiki/CodeGraph 导入与工具调用](../examples/04-wiki-codegraph-ingest.md)
