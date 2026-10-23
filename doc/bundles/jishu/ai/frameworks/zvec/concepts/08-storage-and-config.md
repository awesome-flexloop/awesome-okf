---
type: Concept
title: Zvec 存储引擎与全局配置：WAL、列存与容器自适应
description: WAL 预写日志、Arrow IPC/Parquet 列存、三种 forward store、四种磁盘 I/O 后端、init() 12 参数 cgroup 自适应与 optimize 后台合并
tags: [zvec, wal, arrow, parquet, mmap, io-uring, cgroup, optimize]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-source
    resource: /references/source-code.md
    title: alibaba/zvec 源码信源
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Zvec 存储引擎与全局配置：WAL、列存与容器自适应

Zvec 把数据库级持久化与运维能力带进了进程内形态：WAL 保障崩溃安全，段式多版本 + Arrow/Parquet 列存管理数据布局，cgroup 感知的 `init()` 让容器部署"不配置即最优"。

## 持久化与崩溃恢复

WAL（预写日志，`src/db/index/storage/wal/` 的 wal_file 与 local_wal_file）保证进程崩溃或意外断电后数据不丢。Collection 的段式管理（segment_manager + version_manager）支撑多版本读取与写后立即可见；并发模型为**多进程同时读同一 Collection、写入单进程独占**。

## 列存布局

- **Arrow IPC**（arrow_ipc_writer）：内存映射友好的进程内列式格式。
- **Parquet**（parquet_writer + parquet_buffer_pool）：磁盘压缩列存。
- **Forward store 三形态**：`mmap_forward_store`（内存映射）、`bufferpool_forward_store`（缓冲池，配合 `CollectionOption(enable_mmap=True/False)`）、`memory_forward_store`（全内存）。
- **KV 元数据**：RocksDB 8.1.1 承载 id_map、FTS 倒排列等（rocksdb_context）。

## 四种磁盘 I/O 后端（DiskANN）

`IOBackendType` 枚举四成员——`PREAD`（同步 pread，无异步 I/O）、`LIBAIO`（运行时 dlopen 加载 libaio）、`IO_URING`（raw 内核系统调用，零依赖）、`WINDOWS_OVERLAPPED`（Windows 非缓冲重叠 I/O + 完成端口）。可通过 `io_backend_type()` / `io_backend_description()` 查询当前后端。DiskANN 在装有 libaio 的系统上自动启用异步 I/O，未装则回落备用路径。

## init()：一次性的全局配置

`init()` 须在任何其他操作前调用且仅可调用一次（重复调用抛 RuntimeError），12 个可选参数：

| 参数 | 默认 | 说明 |
|---|---|---|
| log_type / log_level | CONSOLE / WARN | 日志目的地与级别 |
| log_dir / log_basename | ./logs / zvec.log | 文件日志路径与基名 |
| log_file_size / log_overdue_days | 2048 MB / 7 天 | 轮转大小与保留天数 |
| query_threads / optimize_threads | cgroup 推断 | 查询/后台（压缩、建索引）线程数 |
| invert_to_forward_scan_ratio | 0.9 | 倒排转全量正向扫描阈值 |
| brute_force_by_keys_ratio | 0.1 | 键值暴力查找偏好阈值 |
| fts_brute_force_by_keys_ratio | 0.05 | FTS 扫描策略切换阈值（独立于上一项，因逐候选 FTS 成本更高） |
| memory_limit_mb | cgroup 内存 × 0.8 | 软内存上限，接近时限流或拒绝 |

**None 参数即省略**——核心库回落环境感知默认值（cgroup CPU/内存限额）。Kubernetes/Docker 中不显式设线程与内存上限，让 Zvec 自动适配容器配额是推荐用法。

```python
import zvec

zvec.init(
    log_type=zvec.LogType.FILE,
    log_dir="/var/log/zvec",
    query_threads=4,
    memory_limit_mb=2048,
)
```

## optimize()：Flat 暂存与后台合并

新插入向量不直接进配置的向量索引，而是暂存轻量 Flat 缓冲区——最大化写入吞吐，并为原生不支持流式增量的索引类型（如 IVF）提供实时写入能力。代价是暂存区增长会拉低检索性能。

`optimize()` 触发后台线程将暂存区合并进配置索引：**不锁 Collection、不阻塞读写**。频率权衡：过低则 Flat 缓冲区过大、过高则浪费资源——原则上未索引文档达 10 万条以上时优化，按写入速率与延迟要求调整。`collection.stats` 可实时查看索引状态。

## 相关概念

- [源码架构](01-architecture.md)：storage 子目录全景
- [索引类型](03-index-types.md)：DiskANN 的 I/O 特性
- [快速上手示例](/examples/00-quickstart-python.md)：optimize 的最小用法
