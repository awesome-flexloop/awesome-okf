---
type: Concept
title: 状态持久化存储与向量记忆引擎
description: Zleap-Agent @zleap/store 包的持久化架构——PostgreSQL+pgvector 双引擎存储，A/B 双线记忆（agent_memory 笔记 + core 事件图引擎），RRF 多路融合排序召回，抽取管线与幂等写入机制。
tags: [zleap-agent, store, persistence, postgresql, pgvector, memory, rrf, embedding, event-graph]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T13:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: store-main
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/store/src/store.ts
    title: PgStore 主存储实现
  - id: store-schema
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/store/src/schema.ts
    title: 顶层 Schema DDL
  - id: core-schema
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/store/src/core/schema.ts
    title: Core 事件图 Schema (source_group/source/event/entity/event_entity)
  - id: core-rrf
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/store/src/core/rrf.ts
    title: Reciprocal Rank Fusion 融合排序
  - id: core-types
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/store/src/core/types.ts
    title: Core 事件图类型定义 (CoreStore/CoreEvent/CoreEntity)
  - id: core-extract
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/store/src/core/extract.ts
    title: 抽取管线 (ingestFragment/contentHash/reconciler)
  - id: record-memory
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/store/src/core/record-memory.ts
    title: B 线 RecordMemoryPort 适配器
---

# 状态持久化存储与向量记忆引擎

`@zleap/store` 是 Zleap-Agent 的持久化层，基于 **PostgreSQL + pgvector** 提供结构化存储与向量语义召回能力。其核心设计采用 **A/B 双线记忆架构**：A 线 `agent_memory` 专用于对人印象笔记，B 线 `core` 事件图引擎承载通用工作记录与经验记忆，两者通过统一的 `ZleapStore` 接口对外暴露。存储层还承担定时任务、运行时缓存、IM 网关集成配置、Avatar/Space/Skill/MCP 配置等全量状态的持久化。

## 整体架构

存储层以 `PgStore` 类为中心，构造时注入 pg Pool、向量维度和批量向量化函数，内部通过工厂方法创建 14 个子存储门面，统一实现 `ZleapStore` 接口：

```typescript
// store.ts L85-L100
export interface ZleapStore extends RuntimePersistence, SuperAgentStorageAdapter {
  readonly notes: AgentNoteStore;          // A 线 · agent_memory 对人笔记
  readonly core: CoreStore;                // B 线 · core 事件图引擎
  readonly integrations: GatewayIntegrationStore;
  readonly runtimeCache: RuntimeCacheStore;
  readonly tasks: ScheduledTaskStore;
  embedText(text: string): Promise<number[]>;
  saveSession(session: Session): Promise<void>;
  touchSession(sessionId: string, runId: string, updatedAt: Date): Promise<void>;
  listArtifacts(input?): Promise<DurableArtifactRecord[]>;
  close(): Promise<void>;
}
```

```mermaid
graph TB
    subgraph 调用方
        CS[ConversationService]
        GW[Gateway GatewayRunner]
        TK[Tasks Service]
        AV[Avatar]
    end

    subgraph ZleapStore
        direction TB
        PgStore[PgStore<br/>pg.Pool + dimension + embed]
        PgStore --> NS[notes<br/>AgentNoteStore<br/>A线笔记]
        PgStore --> CS2[core<br/>CoreStore<br/>B线事件图]
        PgStore --> INT[integrations<br/>GatewayIntegrationStore]
        PgStore --> RC[runtimeCache<br/>RuntimeCacheStore]
        PgStore --> TS[tasks<br/>ScheduledTaskStore]
        PgStore --> AVST[avatars/spaces/models/skills/mcp<br/>配置存储]
        PgStore --> THR[threads/sessions/ledger<br/>会话账本]
    end

    subgraph PostgreSQL
        direction TB
        AM[(agent_memory)]
        SG[(source_group)]
        SRC[(source)]
        EVT[(event)]
        ENT[(entity)]
        EE[(event_entity)]
        ST[(scheduled_tasks/runs)]
        CFG[(avatars/spaces/threads/...)]
    end

    CS --> PgStore
    GW --> PgStore
    TK --> PgStore
    AV --> PgStore

    NS --> AM
    CS2 --> SG & SRC & EVT & ENT & EE
    TS --> ST
    INT & RC & AVST & THR --> CFG
```

### 工厂函数与降级策略

`createStore()` 是唯一的对外入口，使用 PostgreSQL advisory lock 序列化 schema 初始化，连接失败时返回 `null` 让 CLI 降级为内存模式：

```typescript
// store.ts L108-L135
const SCHEMA_BOOTSTRAP_LOCK = 0x7a1ea9; // "zleap"

export async function createStore(config: StoreConfig): Promise<ZleapStore | null> {
  const pool = new Pool({
    connectionString: config.connectionString,
    max: 4,
    connectionTimeoutMillis: 3000,
  });
  try {
    const client = await pool.connect();
    try {
      await client.query('SELECT pg_advisory_lock($1)', [SCHEMA_BOOTSTRAP_LOCK]);
      try {
        await client.query(schemaSql(config.dimension));
      } finally {
        await client.query('SELECT pg_advisory_unlock($1)', [SCHEMA_BOOTSTRAP_LOCK]).catch(() => {});
      }
    } finally {
      client.release();
    }
    return new PgStore(pool, config.dimension, config.embed);
  } catch {
    await pool.end().catch(() => {});
    return null;  // CLI 降级为内存模式
  }
}
```

关键设计决策：
- **Pool 大小固定为 4**：存储操作主要是短查询+向量搜索，4 个连接足够并发
- **连接超时 3 秒**：快速失败，避免 CLI 启动时数据库不可达导致长时间挂起
- **Advisory Lock**：`0x7a1ea9`（"zleap" 的十六进制）确保多进程并发启动时 DDL 不冲突
- **null 返回即降级**：调用方收到 `null` 后切换到内存模式，不阻断用户交互

## A/B 双线记忆架构

Zleap-Agent 的记忆系统采用双线分离设计，各有明确的职责边界与数据模型。

### A 线：agent_memory 对人笔记

A 线是传统的键值式笔记表，专门存储**对人印象（impression）**和遗留兼容的 experience 类型。每条笔记按 `agent_id + kind + (user_id)` 作用域隔离，支持 FIFO 自动归档：

```typescript
// store.ts L893-L947 — write 方法核心逻辑
write: async (input, limit = DEFAULT_AGENT_NOTE_LIMIT) => {
  const note: AgentNote = {
    id: input.id ?? randomUUID(),
    kind: input.kind,
    agentId: input.scope.agentId,
    userId: input.kind === 'impression' ? input.scope.userId : undefined,
    memory: input.memory,
    status: 'active',
    createdAt: now, updatedAt: now,
  };
  // UPSERT 插入/更新笔记
  await this.pool.query(
    `INSERT INTO agent_memory (...) VALUES (...)
     ON CONFLICT (id) DO UPDATE SET ...`,
    [...],
  );
  // FIFO 归档：超出 limit 的旧笔记自动标记为 archived
  await this.pool.query(
    `UPDATE agent_memory SET status = 'archived', updated_at = $ts
     WHERE id IN (
       SELECT id FROM agent_memory
       WHERE status = 'active' AND kind = $kind AND $scope
       ORDER BY created_at DESC, id DESC
       OFFSET $limit
     )`,
    [...],
  );
  return note;
}
```

A 线特点：
- **scopeWhere 谓词**：impression 类型绑定 `user_id`，experience 类型仅按 `agent_id` 隔离
- **FIFO 归档**：每个 scope 只保留最近 `limit`（默认 `DEFAULT_AGENT_NOTE_LIMIT`）条 active 笔记，溢出自动归档
- **遗留兼容**：experience kind 仅为兼容旧数据，新的经验记忆走 B 线 core 引擎
- **不支持向量搜索**：A 线是纯结构化笔记，语义召回走 B 线

### B 线：core 事件图引擎

B 线是通用结构化事件记忆引擎，采用 **source → event → entity** 三层图模型，5 张核心表：

```mermaid
erDiagram
    source_group ||--o{ source : contains
    source ||--o{ event : emits
    source ||--o{ entity : references
    event ||--o{ event_entity : links
    entity ||--o{ event_entity : linked_by

    source_group {
        text id PK
        text name
        jsonb metadata
        timestamptz created_at
        timestamptz updated_at
    }

    source {
        text id PK
        text group_id FK
        text kind
        text agent_id
        text user_id
        text tenant_id
        text space_id
        text thread_id
        text name
        jsonb metadata
        text status
        timestamptz created_at
        timestamptz updated_at
    }

    event {
        text id PK
        text source_id FK
        text summary
        text content
        jsonb metadata
        text[] keywords
        text[] message_ids
        text content_hash
        text relation_id
        text supersedes_id
        text superseded_by
        timestamptz superseded_at
        float8 importance
        float8 confidence
        text status
        timestamptz valid_until
        vector embedding
        tsvector search_text
        timestamptz created_at
        timestamptz updated_at
    }

    entity {
        text id PK
        text source_id FK
        text type
        text name
        text normalized_name
        text[] aliases
        vector embedding
        timestamptz created_at
        timestamptz updated_at
    }

    event_entity {
        text id PK
        text event_id FK
        text entity_id FK
        text role
        text description
        float8 weight
        float8 confidence
    }
```

核心设计原则：**身份在 source，event 纯净**。所有隔离维度（agent/user/tenant/space/thread）都落在 `source` 表上，`event` 表只有 `source_id` 外键，不携带任何身份列。这使得 event 表结构极其纯净，可以被不同 group（memory/knowledge）复用。

#### Source 隔离与唯一约束

source 表的唯一约束实现了多维度的作用域隔离：

```sql
-- core/schema.ts L35-L38
CREATE UNIQUE INDEX IF NOT EXISTS source_scope_idx
  ON source (group_id, agent_id, kind, COALESCE(user_id,''), COALESCE(space_id,''), COALESCE(thread_id,''));
```

使用 `COALESCE(col,'')` 将 NULL 转为空字符串参与唯一约束，确保同一 (group, agent, kind, user, space, thread) 组合只有一个 source。entity 按 `(source_id, type, normalized_name)` 去重，同一 source 内同名实体共享引用。

#### Event 索引策略

event 表建立了 6 个索引覆盖全部查询路径：

| 索引 | 类型 | 用途 |
|------|------|------|
| `event_source_idx` | B-tree | 按 source 列出事件，按 created_at 倒序 |
| `event_hash_idx` | Unique B-tree | content_hash 幂等查找 |
| `event_relation_idx` | B-tree | relation_id 关联事件链 |
| `event_superseded_by_idx` | B-tree | 被替代事件反向查找 |
| `event_embedding_idx` | IVFFlat (cosine) | 向量相似度搜索，lists=100 |
| `event_search_idx` | GIN | 全文搜索（tsvector） |
| `event_keywords_idx` | GIN | 关键词数组查询 |

## RRF 多路融合召回

Core 引擎的召回（recall）采用 **四路并行检索 + Reciprocal Rank Fusion** 融合排序策略，兼顾语义、词法、实体和图结构四种信号。

```mermaid
flowchart TD
    Q[查询文本 + embedding] --> ISO[Step 1: Isolation<br/>选定可见 source 集合]
    ISO --> V[Step 2: Vector 路径<br/>pgvector cosine 距离]
    ISO --> L[Step 3: Lexical FTS<br/>plainto_tsquery + ts_rank]
    ISO --> E[Step 4: Entity 匹配<br/>normalized_name 精确 + ILIKE 模糊]
    V --> RRF
    L --> RRF
    E --> G[Step 5: Graph 扩展<br/>1-2 hop 共享实体]
    G --> RRF
    RRF[Step 6: RRF 融合<br/>score = Σ 1/k+rank]
    RRF --> FAST{mode?}
    FAST -->|fast| OUT[返回 top-N]
    FAST -->|precise| RR[Step 7: LLM Reranker<br/>精排后返回]
    RR --> OUT
```

### 四路检索实现

```typescript
// store.ts L1218-L1280 — recall 核心检索逻辑

// 2) Vector 路径：余弦距离，返回 1 - distance 作为分数
if (input.embedding && input.embedding.length === dimension) {
  const r = await this.pool.query(
    `SELECT *, 1 - (embedding <=> $1::vector) AS _score FROM event
     WHERE source_id = ANY($2) AND status = 'active' AND embedding IS NOT NULL
     ORDER BY embedding <=> $1::vector LIMIT $3`,
    [toVector(input.embedding), sourceIds, candidateLimit],
  );
  r.rows.forEach((row, index) => bump(row, 'vector', Number(row._score), index + 1));
}

// 3) Lexical FTS：全文搜索，分数归一化到 [0,1]
const lex = await this.pool.query(
  `SELECT *, ts_rank(search_text, plainto_tsquery('simple', $1)) AS _score FROM event
   WHERE source_id = ANY($2) AND status = 'active'
     AND search_text @@ plainto_tsquery('simple', $1)
   ORDER BY _score DESC LIMIT $3`,
  [input.queryText, sourceIds, candidateLimit],
);
const maxLex = lex.rows.reduce((m, row) => Math.max(m, Number(row._score)), 0);
lex.rows.forEach((row, index) => bump(row, 'lexical', maxLex > 0 ? Number(row._score) / maxLex : 0, index + 1));

// 4) Entity 路径：实体名精确/模糊匹配
if (terms.length) {
  const ent = await this.pool.query(
    `SELECT DISTINCT e.* FROM event e
     JOIN event_entity ee ON ee.event_id = e.id
     JOIN entity en ON en.id = ee.entity_id
     WHERE e.source_id = ANY($1) AND e.status = 'active'
       AND (en.normalized_name = ANY($2) OR en.name ILIKE ANY($3))
     ORDER BY e.created_at DESC LIMIT $4`,
    [sourceIds, terms, likeTerms, candidateLimit],
  );
  ent.rows.forEach((row, index) => bump(row, 'entity', 1, index + 1));
}

// 5) Graph 路径：共享实体的 1-2 hop 扩展，decay = 0.5^hop
if (hops >= 1 && seenEvents.size > 0) {
  for (let hop = 1; hop <= hops; hop += 1) {
    const g = await this.pool.query(
      `SELECT DISTINCT e.* FROM event e
       JOIN event_entity ee ON ee.event_id = e.id
       WHERE e.source_id = ANY($1) AND e.status = 'active'
         AND ee.entity_id IN (SELECT ee2.entity_id FROM event_entity ee2 WHERE ee2.event_id = ANY($2))
         AND e.id <> ALL($2)
       ORDER BY e.created_at DESC LIMIT $3`,
      [sourceIds, seedIds, candidateLimit],
    );
    // decay 衰减：hop1=0.5, hop2=0.25
    const decay = 0.5 ** hop;
    g.rows.forEach((row, index) => bump(row, 'graph', decay, ((hop-1)*candidateLimit) + index + 1));
  }
}
```

### RRF 融合算法

```typescript
// core/rrf.ts L16-L55
const DEFAULT_RRF_K = 60;

export function mergeRrfRankings<T extends { id: string; createdAt: Date }>(
  contributions: RrfContribution<T>[],
  k = DEFAULT_RRF_K,
): RrfMerged<T>[] {
  const byId = new Map<string, { item: T; paths: string[]; pathRanks: Record<string, number>; pathScores: Record<string, number> }>();

  for (const contribution of contributions) {
    const rank = normalizeRank(contribution.rank);
    let entry = byId.get(contribution.item.id);
    if (!entry) {
      entry = { item: contribution.item, paths: [], pathRanks: {}, pathScores: {} };
      byId.set(contribution.item.id, entry);
    }
    // 同一 event 在同一路径出现多次，取最佳（最小）rank
    if (!(path in entry.pathRanks)) {
      entry.paths.push(path);
      entry.pathRanks[path] = rank;
    } else {
      entry.pathRanks[path] = Math.min(entry.pathRanks[path], rank);
    }
  }

  return [...byId.values()]
    .map((entry) => ({
      ...entry,
      score: Object.values(entry.pathRanks).reduce((sum, rank) => sum + 1 / (k + rank), 0),
    }))
    .sort((a, b) => b.score - a.score || b.item.createdAt.getTime() - a.item.createdAt.getTime());
}
```

RRF 公式：`score = Σ 1/(k + rank_i)`，其中 k=60 是经典 RRF 默认值。排序规则：先按融合 score 降序，同分按 createdAt 降序（新事件优先）。

### 召回模式

```typescript
// core/types.ts L125-L129
export type RecallMode = 'fast' | 'precise';
```

- **fast 模式**：四路 RRF 融合后直接返回，无 LLM 调用，用于 prefetch 和快速响应
- **precise 模式**：在 fast 候选集上再调用可插拔的 `CoreReranker`（LLM 精排），仅用于主动 recall

## 抽取管线（Ingestion Pipeline）

从会话片段到结构化事件记忆的完整写入流程由 `ingestFragment()` 实现，包含抽取、向量化、去重、调和、写入五个阶段：

```mermaid
flowchart LR
    MSG[会话片段<br/>messages[]] --> ENS[ensureSource<br/>获取/创建source]
    ENS --> EXT{extractor<br/>存在?}
    EXT -->|否| DONE[返回空数组]
    EXT -->|是| LLM[LLM抽取<br/>ExtractedEvent[]]
    LLM --> EMB[批量向量化<br/>embed(memory)]
    EMB --> LOOP[逐事件处理]
    LOOP --> KW[topKeywords<br/>≥4字符非停用词]
    KW --> HASH{contentHash<br/>已存在?}
    HASH -->|是| SKIP[跳过-幂等]
    HASH -->|否| REL[findRelated<br/>查找相关记忆]
    REL --> REC{reconciler<br/>决策}
    REC -->|skip| SKIP
    REC -->|keep_both| INS[insertEvent<br/>新事件]
    REC -->|replace_old| REP[supersede旧事件+插入新事件]
    REC -->|keep_old| ARC[新事件标记archived]
    INS --> OUT[输出CoreEvent[]]
    REP --> OUT
    ARC --> OUT
```

### contentHash 幂等键

```typescript
// core/extract.ts L76-L78
export function contentHash(parts: (string | undefined)[]): string {
  return createHash('sha256')
    .update(parts.filter(Boolean).join('\u0000').trim().toLowerCase())
    .digest('hex');
}
```

对 parts 数组过滤 undefined，以 `\0` 分隔，trim + toLowerCase 后计算 SHA-256。数据库层面通过 `event_hash_idx` 唯一索引（WHERE content_hash IS NOT NULL）保证幂等。

### 调和器（Reconciler）四决策

```typescript
// core/extract.ts L64-L68
export type CoreMemoryReconcileDecision =
  | { action: 'skip'; reason?: string }          // 跳过，不写入
  | { action: 'keep_both'; targetId?: string; reason?: string }  // 共存
  | { action: 'replace_old'; targetId: string; reason?: string } // 替代旧记忆
  | { action: 'keep_old'; targetId?: string; reason?: string };  // 保留旧的
```

当调和器返回 `replace_old` 时，系统自动将旧事件标记为 `superseded` 并设置 `superseded_by` 反向引用，形成记忆版本链。

### 关键词提取

```typescript
// core/extract.ts L80-L97
const STOPWORDS = new Set([
  'this', 'that', 'with', 'from', 'have', 'were', 'they', 'them', 'their',
  'about', 'would', 'could', 'should', 'there', 'here', 'what', 'when',
  'where', 'which', 'while', 'because', 'into', 'over', 'then', 'than', ...
]);

export function topKeywords(text: string, limit = 8): string[] {
  const counts = new Map<string, number>();
  for (const raw of text.toLowerCase().split(/[^\p{L}\p{N}]+/u)) {
    if (raw.length < 4 || STOPWORDS.has(raw)) continue;
    counts.set(raw, (counts.get(raw) ?? 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, limit)
    .map(([word]) => word);
}
```

内置 25 个英文停用词，提取 ≥4 字符的词/数字，按词频排序，默认最多 8 个。关键词同时存入 `event.keywords` 数组（GIN 索引）和 `search_text` tsvector。

## RecordMemoryPort 适配器

`createRecordMemoryPort()` 将 B 线通用 CoreStore 适配为 agent 层定义的 `RecordMemoryPort` 接口，使得 agent 层无需感知 core 引擎的存在：

```typescript
// core/record-memory.ts L105-L207
export function createRecordMemoryPort(deps: RecordMemoryDeps): RecordMemoryPort {
  return {
    ingest: async ({ scope, messages }) => {
      const scoped = workScope(scope); // 需要完整 userId+spaceId+threadId
      if (!scoped) return [];
      const events = await ingestFragment(
        { groupId: RECORD_GROUP_ID, kind: WORK_KIND, scope: scoped, messages },
        { core: deps.core, embed: deps.embed, extractor: deps.extractor, ... },
      );
      return events.map((event) => toRef(event, WORK_KIND));
    },
    writeExperience: async (input) => {
      const scope = experienceScope(input.scope); // 仅 agentId
      // ... 直接写入 experience kind 事件
    },
    recall: async (input) => {
      // 同时检索 work 和 experience 两种 kind，融合排序
      const perKind = await Promise.all(kinds.map(async (kind) => { ... }));
      return perKind.flat().sort((a,b) => b.score - a.score || ...).slice(0, limit);
    },
    listRecent: async (...) => { ... },
    detail: async (id, scope) => {
      const detail = await deps.core.detail(id);
      if (!canReadSource(detail.source.kind, detail.source, scope)) return undefined;
      return { ...toRef(detail, ...), entities: ... };
    },
    deleteByThread: async ({ agentId, threadId }) => {
      await deps.core.deleteByThread({ groupId: RECORD_GROUP_ID, agentId, threadId, kind: RECORD_KIND });
    },
  };
}
```

适配层关键映射：
- `groupId` 固定为 `'memory'`
- 工作记录 `kind='work'`，需要完整 scope（userId+spaceId+threadId）
- 经验记忆 `kind='experience'`，仅按 agentId 隔离（跨会话/跨用户可召回）
- `canReadSource()` 做访问控制检查，experience 级别的记忆 agent 内全局可读
- `detail()` 查询返回 entities 关联数据（type/name/role）

## MCP 配置安全过滤

存储层内置了 MCP 配置的敏感字段过滤函数，防止密钥意外落盘：

```typescript
// store.ts L227-L276
const MCP_SECRET_CONFIG_KEY = /(?:secret|token|password|credential|authorization|bearer|api[_-]?key)/i;

export function sanitizeMcpConfigForStorage(value: unknown): Record<string, unknown> | undefined {
  if (!isPlainObject(value)) return undefined;
  return pruneEmptyObject(sanitizeMcpConfigObject(value, []));
}

function shouldStripMcpConfigValue(keyPath: string[]): boolean {
  // config.env 保存 stdio 环境变量（常含 API key），保留供运行时 spawn 使用
  if (keyPath[0] === 'env') return false;
  const key = keyPath[keyPath.length - 1] ?? '';
  return MCP_SECRET_CONFIG_KEY.test(key);
}
```

过滤规则：
- 匹配 `secret/token/password/credential/authorization/bearer/api_key` 的 key 自动剥离
- **例外**：`config.env`（stdio MCP 服务器的环境变量）保留，因为运行时 spawn 子进程需要这些环境变量
- 剥离后空对象被 `pruneEmptyObject()` 清理，返回 undefined

## 定时任务存储

`ScheduledTaskStore` 提供定时任务的 CRUD 和运行记录管理，任务状态机为 `queued → running → completed/failed/skipped`：

```typescript
// store.ts L845-L857 — stale run 回收
reclaimStaleRuns: async (olderThanSeconds) => {
  const result = await this.pool.query(
    `UPDATE scheduled_task_runs
       SET status = 'failed',
           finished_at = now(),
           error = 'reclaimed: stale running run without completion'
     WHERE status = 'running'
       AND COALESCE(started_at, scheduled_for) < now() - ($1 || ' seconds')::interval`,
    [String(seconds)],
  );
  return result.rowCount ?? 0;
}
```

`reclaimStaleRuns()` 将超过阈值仍处于 running 状态的 run 标记为 failed，防止 Worker 崩溃后任务永久挂起。任务支持 `permissionMode`（full_access/request_approval），与网关权限模式一致。

## 子存储门面总览

PgStore 构造函数中初始化 14 个子存储，覆盖全部持久化需求：

| 子存储 | 表/数据 | 职责 |
|--------|---------|------|
| `avatars` | avatars, avatar_versions | Avatar 人格版本管理 |
| `spaces` | spaces, space_versions, capability_definitions, space_capability_bindings | Space 工作空间与能力绑定 |
| `models` | model_configs | 模型配置管理 |
| `skills` | skill_definitions | 技能定义存储 |
| `mcp` | mcp_servers, mcp_tools | MCP 服务器与工具注册 |
| `threads` | threads | 会话线程管理 |
| `sessions` | sessions, space_sessions, session_entries, session_runs | 会话条目与运行关联 |
| `ledger` | ledger_events | 运行时事件账本 |
| `runtimeCache` | runtime_cache | 6 类缓存（search_result/webpage/file_output/workspace_result/tool_result/note） |
| `tasks` | scheduled_tasks, scheduled_task_runs | 定时任务与运行记录 |
| `notes` | agent_memory | A 线对人笔记 |
| `core` | source_group/source/event/entity/event_entity | B 线事件图引擎 |
| `integrations` | gateway_integrations | IM 渠道配置（Feishu/WeChat/FeishuCli） |

## 事务支持

PgStore 提供两个事务方法保证原子性：

```typescript
// store.ts L628-L644 — 内部事务辅助
private async runInTx<T>(fn: (q: PgQueryable) => Promise<T>): Promise<T> {
  if (!('connect' in this.pool)) return fn(this.pool);
  const client = await (this.pool as PgPool).connect();
  try {
    await client.query('BEGIN');
    const result = await fn(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK').catch(() => {});
    throw error;
  } finally {
    client.release();
  }
}

// store.ts L1350-L1366 — 外部事务接口
async transaction<T>(operation: (tx: SuperAgentStorageAdapter) => Promise<T>): Promise<T> {
  // 创建一个使用同一 client 的 PgStore 实例传入 operation
  const result = await operation(new PgStore(client, this.dimension, this.embed, false));
  // ... COMMIT/ROLLBACK
}
```

- `runInTx()`：内部方法，insertEvent 使用它保证 event+entity+event_entity 的原子写入
- `transaction()`：外部接口，传入一个接收 tx store 的回调，支持跨表原子操作

## 类型签名速查

```typescript
// 配置与工厂
type StoreConfig = { connectionString: string; dimension: number; embed: Embedder; };
type Embedder = (texts: string[]) => Promise<number[][]>;
function createStore(config: StoreConfig): Promise<ZleapStore | null>;

// B 线 Core 引擎
interface CoreStore {
  ensureSource(input: EnsureSourceInput): Promise<CoreSource>;
  insertEvent(input: InsertEventInput): Promise<CoreEvent>;
  findEventByHash(sourceId: string, contentHash: string): Promise<CoreEvent | undefined>;
  recall(input: RecallInput): Promise<RecallHit[]>;
  detail(id: string): Promise<CoreEventDetail | undefined>;
  setEventStatus(id: string, status: CoreEventStatus, input?: SetEventStatusInput): Promise<void>;
  deleteByThread(input: DeleteByThreadInput): Promise<void>;
  purgeByAgent(input: PurgeByAgentInput): Promise<void>;
}

// 抽取管线
type CoreExtractor = (input: ExtractionInput) => Promise<ExtractedEvent[]>;
type CoreMemoryReconciler = (input: CoreMemoryReconcileInput) => Promise<CoreMemoryReconcileDecision>;
type CoreReranker = (input: { queryText: string; hits: RecallHit[]; limit: number }) => Promise<RecallHit[]>;
function ingestFragment(input: ExtractionInput, deps: IngestDeps): Promise<CoreEvent[]>;
function contentHash(parts: (string | undefined)[]): string;
function topKeywords(text: string, limit?: number): string[];

// RRF 融合
function mergeRrfRankings<T>(contributions: RrfContribution<T>[], k?: number): RrfMerged<T>[];
```

## 默认常量

| 常量 | 值 | 来源 |
|------|----|------|
| 默认数据库 URL | `postgres://zleap:zleap@127.0.0.1:5433/zleap` | host/src/constants.ts |
| 默认嵌入维度 | `1536`（text-embedding-ada-002） | host/src/constants.ts |
| Pool 最大连接数 | `4` | store.ts L114 |
| 连接超时 | `3000ms` | store.ts L114 |
| RRF k 值 | `60` | core/rrf.ts L16 |
| IVFFlat lists | `100` | core/schema.ts L74 |
| FTS 配置 | `'simple'`（无词干化） | store.ts L1109, L1230 |
| 笔记默认上限 | `DEFAULT_AGENT_NOTE_LIMIT` | core 包常量 |
| 关键词默认数量 | `8` | core/extract.ts L87 |
| Graph 扩展衰减 | `0.5^hop` | store.ts L1270 |
