---
type: Concept
title: "版本化历史与轨迹流：history_v2.sqlite"
description: "history_v2 三触发条件与 SQLite-only 约束、6 表 3 索引、内容寻址 bodies 与 body_refs、7 类轨迹事件、LiveBus 实时投影、50 轮热窗、legacy 兼容读取，以及它为何成为不可热重绑的服务。"
tags: [octop, history, trajectory, sqlite, content-addressed, live-bus, archive, versioning]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-164、F-169、F-425~F-440（v1.0.2b5）
  - id: lifecycle
    resource: /references/server-launch.md
    title: 服务器启动与组合根
---

# 版本化历史与轨迹流：history_v2.sqlite

[01-server-lifecycle.md](01-server-lifecycle.md) 记录了 `_boot_runtime` 的装配顺序。其中第 ③④ 步构造的 `TrajectoryStore` / `HistoryArchive` 是 1.0.2 周期新增的可选子系统：它把开启之后的新回合写进独立的 `history_v2.sqlite`，与旧消息/轨迹表分段共存、兼容读取。本文解释其触发条件、存储结构、实时轨迹流与「不可逆」约束。

## 1. 三个触发条件与 SQLite-only 约束

归档是否在启动时构造，由一个三条件析取决定（F-169）：

```python
archive_path = self.paths.root / "history_v2.sqlite"
if config.history_v2_enabled or archive_path.exists() \
        or archive_path.with_suffix(".required").exists():
    ...
```

- 配置开关 `history_v2_enabled`（默认 false）；
- 归档文件已存在（曾开启过，关掉后仍要能读）；
- 旁边的 `history_v2.required` 标记存在（文件丢失时拒绝启动而不是静默重建空库——源码实测：缺文件且有标记时抛 `FileNotFoundError("The required history archive is missing: ...")`）。

控制面不是 SQLite 时直接拒绝（F-169）：

```python
raise ValueError("Versioned history currently requires the SQLite control plane")
```

归档以控制面 SQLite 的**绝对路径**作为身份：`identity = str(config.database.resolve_sqlite_path(self.paths.root).resolve())`，打开时校验 `archive_meta` 中的 version=1 与 identity，不符抛 "History archive version or control-plane identity mismatch"（F-169，store.py 源码实测）。用户口径见 `docs/versioned-history.md`：配置项 `history_v2_enabled`、环境变量 `OCTOP_HISTORY_V2_ENABLED` 默认 false，「PostgreSQL 开启此功能会明确拒绝启动」（F-440）。

## 2. 6 张表、3 个索引

`history/store.py` 的 `_SCHEMA` 一次建出 6 张表（F-429）：

```
archive_meta                 单行：version=1 + 控制面身份 identity
segments                     线程分段：format ∈ {legacy, v2}，双边界序号
turns                        回合：status、error、started_at/finished_at
bodies                       内容寻址正文：digest(PK) → value
documents                    消息/事件文档：kind ∈ {message, event}
body_refs                    文档↔正文多对多引用（owner, digest）
```

3 个索引分别服务线程分页、回合取文档与引用反查（F-430）：`segments_thread ON segments(thread_id,id)`、`documents_turn ON documents(turn_id,kind,seq)`、`refs_digest ON body_refs(digest)`。两处 CHECK 约束把格式枚举钉死：segments.format 仅 `'legacy'/'v2'`，documents.kind 仅 `'message'/'event'`（F-430）。

打开参数偏可靠性（F-433）：`PRAGMA synchronous=FULL`、`busy_timeout=5000`，建库事务为 `BEGIN IMMEDIATE`，初始行 `INSERT INTO archive_meta VALUES (1, identity)`。

## 3. 内容寻址：bodies 与 body_refs

归档最核心的设计是消息与轨迹**共享正文池**（F-431）：

```python
TEXT_BLOCK_SIZE = 1024
_BODY_KEYS = frozenset({
    "content", "text", "reasoning_content", "thinking",
    "summary", "args", "result",
})
```

摘要算法为 `sha256(body.encode()).hexdigest()`（F-432）。7 个键中任意一个的大字段都按 1024 个 **Unicode 字符**的固定边界切块（按字符计数保证切分与拼接不破坏 UTF-8，store.py 注释原文），每块单独算 digest 入 bodies，文档经 body_refs 引用这些块。文档 doc_id 形态为 `message:{turn_id}:{index}`（F-434），轨迹兼容层则用 `"event:" + event.event_id`（F-436）。

这带来两个工程性质（store.py 模块 docstring 原文 + docs 口径）：完全相同的大字段（如系统提示、固定工具结果）只存一份，被消息视图与事件视图共享；替换一个流式文档时，只在同一事务里释放它独占的旧正文块，不扫整轮、不碰历史回合。编码标签覆盖 dict/list/body/text/value 等形态（F-432）。文档同时说明：不同形态的内容（工具结果对象与其格式化文本）可能分别保存，**不承诺语义去重**（docs/versioned-history.md）。

## 4. 轨迹模型：7 类事件、11 字段、10 指标

```python
TrajectoryKind = Literal[
    "user", "assistant", "tool", "context",
    "compacted", "system", "unknown",
]   # 7 个（F-425）
```

`TrajectoryEvent` 是 frozen dataclass，11 个字段（F-426）：event_id、thread_id、agent_id、seq、ts、kind、turn_id、request_seq、is_error、summary、payload。

聚合指标 `TrajectoryMetrics` 同样是 frozen dataclass，10 个字段（F-439）：

```python
turns, steps, llm_duration_ms, tool_duration_ms, ttft_avg_ms,
tok_per_s, cache_hit_ratio, input_tokens, output_tokens, cache_read_tokens
```

计数口径（F-439）：`turns` 数 user 事件数，`steps` 取 `len(events)`，`cache_hit_ratio = cache_read / (input + cache_read)`。

## 5. LiveBus 实时轨迹与 projector 投影

记录链路是「harness 流块 → projector → 事件 → 双写」：

```
harness chunks ──► project_harness_chunk() ──► TrajectoryEvent
                        │                            ├──► TrajectoryLiveBus（SSE 实时扇出）
                        │                            └──► HistoryStore（v2 段时入归档）
                        ▼
                 _IGNORED_TYPES 过滤 10 类
```

`TrajectoryLiveBus` 是进程内 pub/sub，订阅队列默认 maxsize=256；队列满时丢最旧事件再投递，保证慢消费者不阻塞生产（F-438，live.py 源码实测）。projector 丢弃 10 类不投影的 chunk（F-438）：reasoning、state_snapshot、state_update、usage、done、error、custom、hitl_required、slash_action、attachment；投影记录附带 content_sha256、content_chars 等键（F-438）。

服务侧节拍（F-437）：指标缓存 TTL 1.0 秒、实时更新间隔 0.05 秒；turn_id 形态 `{thread_id}:turn:{n}`；tool 事件 id 形态 `{thread}:{seq}:tool:{call_id}`；纯工具调用回合合成摘要 `"(tool call only)"`。

## 6. 开关、裁剪与 50 轮热窗

`trajectory/settings.py` 定义持久化与保留边界（F-427、F-428）：

```python
ENABLE_TRAJECTORY_KEY = "enable_trajectory"
PAYLOAD_MAX_CHARS = 64_000
SUMMARY_MAX_CHARS = 240
TRAJECTORY_RETENTION_USER_TURNS = 50      # 旧 trajectory_events 表的热窗
TRAJECTORY_SSE_REPLAY_MAX = 2_000
_CLIP_PAYLOAD_KEYS = ("content", "text", "thinking", "args", "result")
```

轨迹默认开启，**只有显式布尔 false 才关闭**（`cfg.get(ENABLE_TRAJECTORY_KEY) is not False`，F-428）。入库存前 summary 裁到 240 字符、5 个载荷键裁到 64_000 字符（F-427、F-428）。上下文分解（context_breakdown）还会标注初始系统提示、可用技能、连接器等来源段，空值显示 `"(none)"`（F-440）。

## 7. 回合状态、游标与 legacy 兼容读取

回合一共有 6 个状态，读取层按 active/paused 找未完成回合（F-434、docs）：

```
active → complete / partial / paused / failed / interrupted
```

recorder 的终态集合为 complete、partial、paused、failed、interrupted 五值；缺少工具结果、消息解码失败、轨迹写入失败都不能记 complete，写入相关错误码字面 `archive_write_failed` 与 `capture_incomplete`（F-435）。

分页游标是 base64 编码的 JSON，键为 thread/segment/before（F-434）。reader 对旧数据使用 `"legacy:"` 前缀游标，source 取值 projection/checkpoint 两种——即旧投影表与 checkpoint 状态恢复两条路（F-436）。分段边界以完整回合为准：v2 回合不再追加旧 `thread_messages`/`trajectory_events`，旧前缀段只登记边界不复制正文，兼容读取器按段分页拼接，且不提供批量回填（docs/versioned-history.md 口径）。导出端点形态为 `/api/agents/{agent_id}/threads/{thread_id}/history/export`（F-440）。

## 8. 为何它是「不可逆服务」

版本化历史一旦在本次启动中构造，控制面 DB 就**不能再热交换**。`AppRuntime.replace_services` 首行即是守卫（F-164）：

```python
if self.history_archive is not None:
    raise ValueError(
        "Restart the server to rebind a database with versioned history"
    )
```

在线换库入口 `rebind_control_plane` 另有同效守卫（错误码 SLASH_BAD_ARGS，消息 "Restart to rebind a database with versioned history"，F-179）。原因在归档的身份模型：bodies/documents 通过 `archive_meta.identity` 绑定主库绝对路径，热换一个不同时间点或不同路径的库会让 body_refs 与活文档错配。文档口径同样明确：阻止涉及 v2 数据的在线恢复与运行时换库，恢复需停机取整目录一致备份，跨机器/换路径的身份重绑定工具本期不提供（docs/versioned-history.md）。停止服务时 `history_archive.store.close()` 排在 db.close() 之前（F-171）。

## 相关概念

- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)——history_archive 在 _boot_runtime 第 ③④ 步装配
- [/concepts/12-agent-runtime-internals.md](12-agent-runtime-internals.md)——轨迹事件来自 Agent 运行时流
- [/concepts/15-backup-and-storage.md](15-backup-and-storage.md)——含聊天备份携带 history_v2.sqlite 一致快照
