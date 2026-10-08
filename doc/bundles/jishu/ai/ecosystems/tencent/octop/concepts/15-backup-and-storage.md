---
type: Concept
title: "自动备份、归档与存储后端"
description: "六内容目录 tar.gz 系统备份、workspace zip 导入、三路数据面采集器（文件集/pg_dump -Fc/SQLite online backup）、chats 归档、octop_auto_backup 定时任务，以及 10 kind 存储后端与沙箱配置。"
tags: [octop, backup, archive, pg-dump, sqlite, cron, storage-backend, docker, sandbox]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-154、F-402~F-424（v1.0.2b5）
---

# 自动备份、归档与存储后端

Octop 的数据保护分两层：`infra/backup/` 负责把整台实例的状态打成 tar.gz 并按计划轮转；`infra/backend/` 负责把 `storage_backends` 表的配置行解析成 harness 可用的执行/存储规格。本篇依次拆解。

## 1. 系统备份：六个内容目录

`system_archive.py` 把数据根下六类内容归入同一个 tar.gz（F-402）：

```python
_CONFIG_DIR = "config"          # 配置
_DB_DIR = "db"                  # octop.db（SQLite 快照）或 octop.dump（pg_dump 自定义格式）
_WORKSPACES_DIR = "workspaces"
_SKILL_PACKAGES_DIR = "skill-packages"
_PLUGINS_DIR = "plugins"
_KNOWLEDGE_DIR = "knowledge"
_MANIFEST_NAME = "manifest.json"
```

归档文件名形态 `octop-backup-{YYYYMMDDTHHMMSSZ}.tar.gz`（F-404）。遍历时跳过 13 个噪音目录名（F-403）：

```
.git、__pycache__、.venv、venv、node_modules、
.mypy_cache、.pytest_cache、.ruff_cache、.tox、
.next、.turbo、dist、build
```

另有两个治理细节（F-404）：历史 LightClaw 迁移库带后缀字面 `"-migrated-from-lightclaw"`；解包使用 `tarfile.data_filter`（Python 3.12 的路径穿越防护）。聊天记录默认不入系统备份（`include_chats` 默认 False，F-404）。

## 2. 工作区归档：zip merge / replace

单个 Agent 工作区走独立的 zip 导入导出（`workspace_archive.py`），模式为字面量类型（F-405）：

```python
WorkspaceImportMode = Literal["merge", "replace"]
_SKIP_DIR_NAMES = frozenset({".git", "__pycache__", ".venv", "node_modules"})
```

`merge` 合入现有工作区；`replace` 先清空再解包，但只删除明文非隐藏项，内置技能路径（`_builtin_skills`）在跳过清单内，不会被误删（F-405）。zip 条目名经 `_safe_zip_name` 归一，拒绝 `..` 路径段（F-405）。

备份存储侧 `store.py` 接受 `.tar.gz` 与 `.tgz` 两种后缀，自动备份前缀 `"octop-auto-backup-"`；读取清单时成员名匹配 `manifest.json` 或 `./manifest.json`，且只读 tar 的**首个成员**（F-406）。

## 3. 三路数据面采集器与 manifest

数据库内容的采集按驱动分三路，元数据统一进 manifest：

| 采集器 | 适用 | 实现要点 |
|--------|------|----------|
| 文件集遍历 | workspaces/plugins/skill-packages/knowledge/config | 跳过 13 个噪音目录；tarfile.data_filter 解包（F-403、F-404） |
| `pg_dump` | PostgreSQL | 命令形态 `pg_dump -Fc -f ... --dbname`，支持 `--exclude-table-data`；恢复用 `--clean --if-exists --no-owner`；returncode ≥ 2 判失败（F-410） |
| SQLite online backup | SQLite | 在线备份 API 字面调用 `src.backup(dest_conn)`；恢复后执行 `PRAGMA wal_checkpoint(FULL)`；源库以只读 URI `file:...?mode=ro` 打开（F-408） |

采集时还会处理属主与密钥（F-407）：JWT 密钥从 `"jwt"` 键捕获；8 张带属主的表（agents、channels、cron_jobs、sessions、threads、connectors、connector_oauth_states、usage_log）参与用户重映射；users 表按实测 11 列（id、username、password_hash、role、display_name、disabled、created_at、locale、preferences_json、login_failed_count、login_locked_until）搬运（F-409）。

manifest 版本固定 `MANIFEST_VERSION = 1`，`BackupManifest` 的关键默认值（F-411）：

```python
includes_plugins=False
includes_knowledge=False
includes_chats=True     # 旧归档无此键时视为 True（旧格式整库导出本就含聊天）
```

旧档兼容还有两条：缺 `includes_plugins`/`includes_knowledge` 键时按 False 处理——老版本从不打包这两个目录（F-411，源码实测）。

## 4. chats 归档：五表、两目录、六文件

聊天数据的剥离/保留由 `chats.py` 精确定义。删除顺序子表优先（F-412）：

```python
CHAT_TABLES_CHILD_FIRST = (
    "trajectory_events", "thread_messages", "thread_history_projection",
    "threads", "sessions",
)   # PARENT_FIRST = reversed(...)
```

工作区侧聊天目录名两个：`sessions`、`conversation_history`（F-412）；受管控的 SQLite 文件名六个：`checkpoints.sqlite` 及其 `-wal`/`-shm`、`memory.sqlite` 及其 `-wal`/`-shm`（F-413）。导入导出走 spool 表 `_users`，批量 fetchmany/executemany 的大小为 500（F-413）。

## 5. 自动备份任务

定时任务在 `_boot_runtime` 中由 `install_auto_backup_job(cron_mgr, server=self)` 挂载（F-168）。`backup/auto.py` 的常量与审计口径（F-414）：

```python
AUTO_BACKUP_JOB_ID = "octop_auto_backup"
_AUTO_FILENAME_PREFIX = "octop-auto-backup-"
BACKUP_LOCK   # 模块级 asyncio.Lock，手动/自动共享，禁止并发备份
# 审计动作：backup.auto_ok / backup.auto_failed，执行者 ACTOR_SYSTEM
```

计划与保留策略由 `BackupConfig`（frozen dataclass，位于 `src/octop/config.py`）承载，共 9 个字段（F-154、F-414）：

| 字段 | 默认值 |
|------|--------|
| `auto_enabled` | `False` |
| `schedule` | `"cron:0 4 * * *"`（每日凌晨 4 点） |
| `retention_count` | `7`（解析时要求 ≥ 1，否则 ValueError） |
| `include_config` / `include_workspaces` / `include_skill_packages` | `True` |
| `include_plugins` / `include_knowledge` | `True` |
| `include_chats` | `False` |

环境变量统一以 `OCTOP_BACKUP_` 前缀覆盖（F-414）。轮转由 `prune_auto_backups(paths, keep=retention_count)` 在每次成功后执行（F-414）。

## 6. 存储后端：5 个对象 kind 与 10 个可解析 kind

`infra/backend/adapter.py` 把 DB 配置行映射为 harness 规格，全程无 I/O。系统维护两个不同外延的集合（F-415、F-424）：

```python
_OBJECT_KINDS = frozenset({"cos", "s3", "oss", "obs", "custom"})      # 对象存储 5
_AGENT_RESOLVABLE_KINDS = frozenset({                                 # Agent 可解析 10
    "cos", "s3", "oss", "obs", "custom",
    "filesystem", "shell", "postgres", "docker", "opensandbox",
})
```

「可内置配置」与「可解析」是双层概念：存储后端管理 UI 内置前 5 个对象 kind 的表单；后 5 个（filesystem/shell/postgres/docker/opensandbox）虽不在内置对象表单里，`row_to_backend_spec` 仍能产出 harness 规格，差集恰为这 5 个（F-424）。

各类的规格要点（F-416、F-417）：

| kind | 关键事实 |
|------|----------|
| cos | 必填 access_key/secret_key/bucket/region；配置键 `secret_id`、`secret_key` |
| s3 | 配置键含 `endpoint_url`（兼容自建 S3） |
| filesystem / local_shell | `virtual_mode=True` |
| postgres | 拼接 `postgresql://` URL，schema 默认 `public` |
| opensandbox | 默认镜像 `"python:3.12"`，协议仅 http/https |

resolver 在展开 named 引用与 composite 树时还有一条安全改写：kind 为 local_shell/filesystem 且 root_dir 指向宿主根时，改写为 workspace_dir（F-420）。

## 7. Docker 沙箱：前缀、18 个透传键与三级 scope

```python
DEFAULT_SANDBOX_PREFIX = "octop_sandbox"
```

docker 配置白名单透传 18 个键（F-418）：allow_network、memory、cpus、pids_limit、command_timeout、max_output_bytes、auto_remove、workspace_path、volumes、environment、environment_file、agent_id、container_name、sandbox_scope、sandbox_prefix、username、sandbox_id、previewable。不在白名单的键不会进 harness spec。

沙箱 scope 三取值（F-419）：

| scope | 隔离粒度 | previewable 默认 |
|-------|----------|------------------|
| `agent`（默认） | 每个 Agent 独立容器 | 否 |
| `user` | 每用户共享 | 否 |
| `fixed` | 固定容器 | **是**（管理 UI 可浏览文件的唯二默认情形） |

`docker_spec_previewable` 的规则：非 docker 后端恒可浏览；docker 仅 fixed scope 默认放行，或显式 `previewable` 覆盖（F-419）。探测方面，`probe.py` 以内容 `"octop-docker-probe"`、测试 id `"test"` 按三种 scope 分支跑往返容器（auto_remove），结果消息键 `docker_probe_roundtrip_ok`/`opensandbox_probe_ok`（F-422）。opensandbox 依赖约束 `opensandbox>=0.1.16,<0.2`，探测返回 `"ready"`/`"installed"`（F-423）。文件浏览临时目录前缀 `octop-storage-browse-`，单层列目录调用后端 `als`（F-421）。

## 相关概念

- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)——install_auto_backup_job 的挂载时机
- [/concepts/16-history-trajectory.md](16-history-trajectory.md)——含聊天备份会额外携带 history_v2.sqlite 一致快照
- [/concepts/13-plugin-system.md](13-plugin-system.md)——plugins 与 skill-packages 两个备份内容目录
