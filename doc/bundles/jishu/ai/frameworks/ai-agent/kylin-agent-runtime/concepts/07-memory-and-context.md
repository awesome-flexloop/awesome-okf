---
type: Concept
title: 记忆与上下文——会话存储、压缩引擎、记忆提供者与用户画像治理
description: 按四层拆解 Kylin Agent Runtime 的"自进化"机制：SessionDB 全文检索、ContextCompressor 压缩、MemoryProvider 钩子族与带置信度/加密治理的用户画像。
tags: [kylin-agent-runtime, memory, context, session-db, user-profile]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
---

# 记忆与上下文：四层"自进化"机制

> 术语速记：**SessionDB**（基于 SQLite 的会话状态库）、**ContextEngine**（上下文引擎抽象基类）、**MemoryProvider**（可插拔记忆提供者）、**ProfileEntry**（带置信度与生命周期的画像条目）。

README 把本项目描述为"自进化智能体运行时"，但代码里并不存在单一的"记忆模块"。架构洞察 I-4 指出，"自进化"实际由三套存储、三套策略的学习回路构成；本文按数据自下而上组织为四层：**会话检索层 / 上下文压缩层 / 外部记忆层 / 用户画像与技能策展层**（I-4）。

## 四层总览

| 层 | 核心符号 | 持久化 | 治理强度 |
|---|---|---|---|
| ① 会话存储 | `SessionDB` / `MemoryDB` | SQLite（9 普通表 + 2 迁移表 + 2 FTS5 虚表）（Q-006） | 结构化存储 + 全文检索 |
| ② 上下文引擎 | `ContextEngine`(ABC) / `ContextCompressor` | 不持久化，运行时压缩消息历史 | 阈值触发，首尾消息保护 |
| ③ 记忆提供者 | `MemoryManager` / `MemoryProvider`(ABC) | 8 个插件后端（F-097） | 钩子协议，后端自治 |
| ④ 画像与策展 | `agent/user_profile/`、`curator` | Fernet 加密文件 / 技能状态文件 | 置信度门槛 + 显式授权 + 假名化 |

## 第一层：会话存储 SessionDB 与 MemoryDB

会话状态库的主类是 `SessionDB`（kylin_agent_runtime_state.py:381），`MemoryDB(SessionDB)` 是其子类（同文件:4050）（F-129）。

**表结构**（F-130，计数见 Q-006）：

- 9 张普通表：`schema_version`、`sessions`、`projects`、`project_roots`、`messages`、`state_meta`、`task_runs`、`task_subruns`、`task_checkpoints`。
- 2 张后加的 Telegram 迁移表：`telegram_dm_topic_mode`、`telegram_dm_topic_bindings`（快照中位于建表迁移段 kylin_agent_runtime_state.py:3440、:3453），服务 Telegram 私信话题模式。

**两张 FTS5 全文检索虚表**（F-131）：

- `messages_fts`：`USING fts5(content)`，由三个触发器把 `content + tool_name + tool_calls` 拼接进索引，使工具调用内容也能被搜到。
- `messages_fts_trigram`：`tokenize='trigram'`，源码注释说明其用途是支撑 **CJK（中日韩文字）子串检索**（kylin_agent_runtime_state.py:352-358）。trigram 分词器生成重叠的 3 字节序列，因此不依赖空格分词；检索代码对单个 token 含 3 个及以上 CJK 字符的查询才走 trigram 路径（源码注释 kylin_agent_runtime_state.py:2982-2993）。

**关键读写方法**（F-132）：`create_session`（:838）、`save_project`（:875）、`get_session`（:1162）、`get_session_title`（:1274）、`list_sessions_rich`（:1392）、`append_message`（:1663）、`add_task_checkpoint`（:2084），以及两个检索入口 `search_messages`（:2878）与 `search_sessions`（:3178）。这两个方法支撑了对话内"搜索过往对话"的能力（README 首段宣称的学习闭环之一，F-010）。

## 第二层：上下文引擎 ContextEngine 与压缩器

**ContextEngine：抽象基类的默认契约。**

`class ContextEngine(ABC)` 位于 agent/context_engine.py:32（F-081），定义三个抽象方法 `update_from_response` / `should_compress` / `compress`，并给出类级默认阈值：

- `threshold_percent = 0.75`：上下文占用达到模型窗口 75% 时应考虑压缩；
- `protect_first_n = 3`、`protect_last_n = 6`：默认保护开头 3 条与结尾 6 条消息；
- 另带一组默认空钩子：`on_session_start` / `on_session_end` / `get_tool_schemas` / `handle_tool_call` / `update_model`。

**ContextCompressor：一个需要如实记录的阈值覆盖事实。**

唯一内置实现 `class ContextCompressor(ContextEngine)` 在 agent/context_compressor.py:453（F-082）。其构造参数签名为 `threshold_percent: float = 0.50`、`protect_first_n=3`、`protect_last_n=20`、`summary_target_ratio=0.20`（:512-515），**但构造函数体内又无条件执行 `self.threshold_percent = 0.80`（:533），并据此计算 `threshold_tokens = int(context_length * 0.8)`，入参 0.50 实际不生效**。这是勘误 E-004 明确记录的代码事实（context_compressor.py:512 vs :533），本文如实陈述，不做"默认阈值 0.50"的转述。

压缩入口 `compress(messages, current_tokens=None, focus_topic=None, force=False)`（:1487）支持强制压缩与聚焦主题；摘要目标长度按 `summary_target_ratio * context_length` 推导（:553、:1413 附近）。首尾保护的语义是"系统提示词之外**额外**保护 N 条非系统消息"（源码注释 :1304-1319：`protect_first_n=3` 表示系统消息 + 前 3 条非系统消息不被压缩）。

**@ 引用展开与路径白名单。**

用户消息中的 `@` 引用在进模型前展开为实际内容（F-083，agent/context_references.py）：

- `REFERENCE_PATTERN`（:17）支持 `@diff`、`@staged`、`@file`、`@folder`、`@git`、`@url:<value>`，文件类引用还可带 `:行号`；
- `parse_context_references` 与 `preprocess_context_references`（同步 + async 两版）负责扫描与替换；
- `_ensure_reference_path_allowed`（:342）实施路径白名单，即"引用文件"并非任意路径可读，这是压缩/引用链路上的一道安全边界。

## 第三层：MemoryManager 与可插拔记忆提供者

**编排器与 ABC 钩子族。**

`class MemoryManager`（agent/memory_manager.py:244）负责多后端的统一编排（F-084）：`add_provider` 注册后端；`build_system_prompt` 聚合记忆注入系统提示词；`prefetch_all` / `queue_prefetch_all` / `sync_all` 提供预取（同步与异步队列）；`get_all_tool_schemas` / `handle_tool_call` 把各后端工具并入 Agent 工具面；生命周期钩子有 `on_session_switch`（:457）、`on_pre_compress`（:492）、`on_memory_write`（:537）、`on_delegation`、`shutdown_all`。

`class MemoryProvider(ABC)`（agent/memory_provider.py:42）是后端契约（F-085）：抽象面为 `name` / `is_available` / `initialize` / `get_tool_schemas`；可选钩子包括 `on_turn_start`、`on_session_switch`、`on_pre_compress`、`on_delegation`、`save_config`。值得注意的是 `on_memory_write`（:262）带结构化参数——**action 取值 `add` / `replace` / `remove`，target 取值 `memory` / `user`**（:271 注释），即记忆写入在协议层就区分了"新增/替换/删除"与"写事实记忆/写用户信息"两种维度，后端可据此做差异化存储或拒绝。

**8 个插件后端与 InsightsEngine。**

记忆后端以插件形式存在于 `plugins/memory/`，共 8 个目录（F-097）：`byterover`、`hindsight`、`holographic`、`honcho`、`mem0`、`openviking`、`retaindb`、`supermemory`，每个后端以 `plugin.yaml` + Python 模块自描述。由于供应链安全策略，这类可选后端按需懒安装而非进入 `[all]`（参见 I-5 与概念 05）。

在会话数据之上，`class InsightsEngine`（agent/insights.py:93）提供统计洞察（F-086）：`generate(days=30, source=None)`（:111）聚合会话、工具使用、技能使用、消息统计四类数据（`_get_sessions` / `_get_tool_usage` / `_get_skill_usage` / `_get_message_stats`），并分别用 `format_terminal`（:726）与 `format_gateway`（:866）渲染给 CLI 与消息网关两种出口。

## 第四层：用户画像治理与技能策展

这是治理强度最高的一层（I-4 的核心反差点："学习用户"不是无约束写入）。

**画像模型：110 个字段与三重治理。**

`agent/user_profile/` 子系统（F-089）用 Pydantic 建模：`UserProfile` 与 `ProfileEntry`（条目带 `confidence` 置信度、`source: onboarding | explicit | inferred` 来源、`lifecycle: static | dynamic | boundary` 生命周期），另有 `ProfileUpdate` 与上限 50 条的 `ExtractionBatch`。字段定义共 **110 个 = FIELDS 81 个当前字段（schema.py:38）+ LEGACY_FIELDS 29 个遗留字段（schema.py:582）**。

`policy.apply_updates` 的写入策略（F-089，policy.py:13-76）：

- **推断信息必须达标**：非显式更新要求 `confidence >= 0.70`（`MIN_INFERRED_CONFIDENCE = 0.70`，policy.py:13）；
- **boundary 字段只能显式声明**：生命周期为 `boundary`（隐私边界类，如 `boundaries.do_not_record`、`boundaries.session_only`、`boundaries.do_not_infer`）的条目，推断写入一律拒绝（policy.py:45-49）；
- 隐私边界变更在同批次内优先生效，用户既有的不 infer/不记录意愿会压制后续推断（policy.py:62-74）。

**加密落盘与假名身份。**

- 存储类 `EncryptedFileProfileStore` 使用 **Fernet** 对称加密，每个用户一个 `<hmac-sha256 摘要>.profile.enc` 文件；密钥文件以 `O_EXCL` + `0o600` 权限新建，读取时用 `hmac.compare_digest` 校验用户标识（F-090，storage.py:58-92）。
- 密钥来自 `EnvironmentKeyProvider`，读取环境变量 `KYLIN_PROFILE_KEY`；LLM 抽取器 `OpenAICompatibleProfileExtractor.from_environment` 读 `KYLIN_PROFILE_LLM_*` 系列变量（F-090）。
- 对外身份用不可逆假名：`pseudonymous_user_id` 为 HMAC-SHA256 摘要加 **`v1_`** 前缀（identity.py:29-32），版本前缀为将来换算法留出迁移位（F-091）。
- 首次使用的 **onboarding 固定 3 问**（onboarding.py:1 注释明示"Exactly three resumable onboarding questions"）：称呼（`basic.preferred_name`）、年龄、职业（`occupation.category`），可断点续答（F-090）。

运行时由 `RuntimeUserProfile`（`profile_prompt` / `observe`）与 `initialize_user_profile` / `build_user_profile_prompt` 接入对话环（F-091）。

**技能策展 curator 与周边产物。**

"自进化"的另一条回路是技能自动策展（F-087，agent/curator.py）：`run_curator_review(on_summary, synchronous, dry_run)`（:1369）以 LLM 评审技能；`maybe_run_curator(idle_for_seconds)`（:1763）按空闲触发；`should_run_now`（:199）与 `apply_automatic_transitions`（:256）执行 idle/stale/archive 状态流转；状态可 `load_state` / `save_state` / `set_paused`。配套的 curator_backup.py 提供 `snapshot_skills` / `rollback` / `list_backups`，使自动流转可回滚（F-087）。

周边轻量记忆产物还包括：`embeddings/` 目录仅含 `metadata.json` 与 `vectors.npy` 两个嵌入产物文件（F-092，一笔带过）；`SubdirectoryHintTracker` 在工具调用时检查目录内提示文件；`generate_title` / `auto_title_session` 用 max_tokens=500 的辅助任务生成标题并截断到 80 字符（F-093）。

## 小结

四层各自独立、治理强度递增：底层 SessionDB 解决"记得住、搜得到"（含 CJK trigram 检索）；压缩层解决"装得下"，但要注意 E-004 记录的 0.80 覆盖 0.50 的代码事实；记忆层以 ABC 钩子族容纳 8 个异构后端；画像层则把置信度门槛、显式授权、加密与假名化作为写入前提。阅读源码时建议从 `SessionDB` → `ContextEngine` → `MemoryProvider` → `policy.py` 的顺序切入。

## 相关概念

- [02-agent-core-loop](/concepts/02-agent-core-loop.md)：对话环如何调用压缩引擎与后台复盘写记忆。
- [06-skills-and-plugins](/concepts/06-skills-and-plugins.md)：curator 策展的技能运行时与插件发现机制。
- [08-gateway-and-cron](/concepts/08-gateway-and-cron.md)：InsightsEngine 的 gateway 渲染出口与多平台会话身份。
- 上游机制可对照跨束的 [hermes-agent](../../hermes-agent/index.md) 文档。
