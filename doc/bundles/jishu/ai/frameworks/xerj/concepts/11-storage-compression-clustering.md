---
type: Concept
title: 存储、压缩与集群现状
description: XERJ 的存储布局（每段三个 mmap 文件、WAL 三档持久性）、9 种列编码与 Zstd 三档力度，以及集群模式当前真实的四项能力与四项「不提供」
tags: [xerj, 存储, wal, 压缩, 集群, raft]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-docs-facts
    resource: /references/facts-docs.md
    title: 官方文档站事实清单
  - id: xerj-docs-source
    resource: /references/docs-source.md
    title: 官方文档站信源登记
---

# 存储、压缩与集群现状

本篇覆盖三件事：**数据怎么落在盘上**、**怎么压**、以及**集群模式今天到底是什么**。第三件是最容易被误读的。

## 存储布局

### 每个 segment 是三个文件

这是与「一个 segment 目录放十几个文件」的设计不同的地方（F-225）：

```
data/
├── logs/                      ← 一个索引
│   ├── schema.json            ← 字段映射
│   ├── wal/
│   │   ├── wal-000001         ← 只追加
│   │   └── wal-000002         ← 按 wal_max_size_mb 轮转
│   ├── seg-000001/
│   │   ├── segment.seg        ← 列式数据，mmap
│   │   ├── segment.sidx       ← seek 用的跳过索引，mmap
│   │   └── segment.ids        ← doc-id 旁挂（外部 id → 内部序号），mmap
│   └── seg-000002/
│       ├── segment.seg
│       ├── segment.sidx
│       └── segment.ids
├── cluster/                   ← Raft 元数据（仅集群模式）
│   ├── raft-log-*
│   └── snapshots/
```

三个文件**全部 mmap**，读取直接来自操作系统页缓存，无应用侧缓冲（F-226）。

| 文件 | 内容 | 为什么独立成文件 |
|---|---|---|
| `segment.seg` | 列式数据。每个字段一条独立列 run，查询只触碰实际读取的列；整数列用 delta-of-delta 或 FOR，字符串列用 dictionary + FST | 列存让「只读两列」不必读整行 |
| `segment.sidx` | 稀疏的逐列 seek 表，点查不必扫整列 | 让点查变成 O(log n) 而非 O(n) |
| `segment.ids` | 外部文档 id → 内部序号 | **放在主文件之外**，这样 id 查找不会把列存页拉进内存 |

> **可迁移的设计点**：把 id 旁挂文件独立出来，等于把「按 id 查」这条路径的内存代价与「按列查」解耦。三文件结构还有一个直接后果：**每个打开的 segment 占 3 个文件描述符**（见 [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md)）。

### Segment 不可变

写入后不再改变。更新与删除通过**写新 segment 加墓碑**实现；合并把存活文档重写进更大的 segment（F-228）。这正是备份可以只是文件系统复制的原因（见 [13](/concepts/13-operations-and-troubleshooting.md)）。

### WAL：三个持久性档位

每个索引一个 WAL，按 `wal_max_size_mb`（默认 1024 MiB）**分代轮转**；旧代在 flush 检查点越过尾代之后释放（F-229）。持久性由 `[storage] wal_sync` 决定（F-230）：

| 档 | 行为 | 丢什么 | 用在哪 |
|---|---|---|---|
| `sync` | 每次确认写入前 fsync（一个 `_bulk` 请求一次 fsync，即 group commit）。断电可持久，对齐 ES 的 `index.translog.durability: request` | 不丢 | 金融/合规负载 |
| `batched`（默认） | 写入立即到达内核，**XERJ 进程崩溃不丢任何东西**；后台循环每 `wal_batch_ms`（默认 100 ms）fsync | 断电或内核 panic 最多丢最后约 **100 ms** 已确认写入 | 绝大多数场景 |
| `async` | 从不 fsync，由操作系统决定何时刷 | 断电或 OS 崩溃最多丢约 **1 秒** | 仅开发/基准 |

> **关键区分**：`batched` 档下，**进程崩溃不丢数据**（数据已在内核页缓存里，进程死掉内核仍在），只有**断电**才丢那约 100 ms。这两条常被混为一谈。

### 合并：四个键真正生效

合并路径实际读取的只有四个键（F-231）：

| 键 | 默认 | 作用 |
|---|---|---|
| `max_segment_mb` | 8192 | 达到此大小的段不再参与合并 |
| `tier_floor_mb` | 4 | 层边界 |
| `min_merge_count` | 4 | **逐层触发阈值**（真正的触发器） |
| `max_merge_count` | 16 | 一次批量合并的段数上限，因而也是**合并峰值内存的上限** |

`strategy` 只有一个已实现值 `size_tiered`；`log_structured` 在**启动时被拒**，而不是被静默替换（F-232、F-261）。文档给出的理由值得记住：一个为读放大问题选了 leveled 策略的运维者，不该被悄悄跑成另一种策略。

另有三个键被接受但**未接线**（F-233、F-260）：

| 键 | 未接线的原因 | 真正生效的替代 |
|---|---|---|
| `min_segments` | 被 `min_merge_count` 取代 | `[merge] min_merge_count` |
| `io_rate_mb_per_sec` | 合并 I/O 在本构建里不限流；尊重它的限流器位于引擎**从不构造**的 storage-crate 合并执行器里 | 无 |
| `max_concurrent` | 合并并行度来自环境变量 | `XERJ_MERGE_PARALLELISM`（默认 1） |

## 压缩：两层

### 块压缩：Zstd 三档

| 档 | 力度 | 用途 |
|---|---|---|
| `fast` | Zstd L1 | 编码最快，比率最松 |
| `balanced` | Zstd L3 | **默认** |
| `best` | Zstd L6 | 冷存储，每字节解码窗口的实测比率最紧 |

**力度在合并时生效，不在 flush 时**（F-236）。flush 恒写 L3，因为 flush 是摄入的背压临界点——文档记录了一次事故：把 flush 力度调高曾让持续吞吐从 **1.55M docs/s 崩到 21k docs/s**，且 75% 文档被拒。合并跑在摄入路径之外，而它产出的长寿命段才是占盘的主体。

两个推论：

- **改力度不会立刻生效**，它随合并发生；想作用于已有数据需 force-merge（F-237）。
- **不同力度的段可以在同一索引共存**，无需迁移也无需重建——Zstd 解码不依赖写入时的力度（F-237）。

`[compression] enabled` 与 `block_size_docs` 被接受但**未接线**（F-238）：每个持久化产物都是压缩信封，**不存在未压缩的写入路径**；且存储编解码器按整个 segment section 做列存，而非按文档数分块，所以没有「文档块」可供 `block_size_docs` 来定尺寸。这两个键在 #318 之前是**静默忽略**的。

### 列编码：9 种，写入时自动选

按列的形状在写入时选择（F-234）：

| 编码 | 形状 | 用于 |
|---|---|---|
| `BitsetEnum` | ≤16 个不同值 → 4 位索引 + 位图 | `level`、`status_class` |
| `Dictionary` | ≤256 个不同字符串 | `service`、`host`、`method` |
| `DeltaTimestamp` | 检测到 Apache/Nginx/ISO → 秒级 delta-of-delta | `@timestamp` |
| `PackedIp` | IPv4 存 u32，IPv6 存 u128 | IP 字段 |
| `UrlTemplate` | 路径归一化，`/users/:id` 把高基数 URL 收敛成模板 | URL 字段 |
| `Varint` | 小整数 | `status`、`bytes` |
| `Bitpacked` | 布尔，8 个/字节 | 布尔列 |
| `FixedPrecision` | 浮点存缩放 varint | 百分位、时长 |
| `RawString` | 高基数回退 | `message`、`user_agent` |

> `UrlTemplate` 值得单独一提：它把「每个 URL 都是不同值」这个高基数问题，转成「URL 模板 + 参数」两个低基数列。这是列存引擎应对高基数字符串的标准手法。

## 集群现状：给的是选主环，不是数据副本

集群模式使用**内嵌 Raft 实现**，无需 etcd / ZooKeeper / Consul，且**集群模式是一个配置开关，不是独立进程**（F-239）。

### 当前**不**提供的四项

官方文档用四张清单逐项写明（F-240～F-243）：

| 不提供 | 具体表现 |
|---|---|
| 元数据复制 | 节点 A 创建的索引在节点 B 上不存在；没有生产路径会提出 `ClusterCommand` |
| 文档复制 | 节点 A 上 PUT 文档、节点 B 上 GET 返回 **404 `index_not_found`**（3 节点环实测） |
| 分片路由 | 没有到主分片的转发，没有副本读；每个节点的 API 只服务该节点的存储 |
| 节点生命周期 API | 没有 drain / activate / remove 端点，也没有 region split-merge。文档注明「此前版本的这一页写过它们，但二进制从未发布过」 |

### 真实且被测试过的四项

| 能力 | 实测 |
|---|---|
| 选主 | 每任期恰好一个 leader；随机 **150–300 ms** 选举超时；自动故障转移。3 节点回环环（tick 50 ms）实测杀 leader 后约 **250 ms** 选出新 leader，此后选举稳定数分钟 |
| 带认证的节点间传输 | 每条连接用 cluster secret 做 **HMAC-SHA256 over a per-connection challenge**；**不存在未认证模式**，无 secret 时节点拒绝启动 |
| 死节点隔离 | 宕机或无响应对端在状态切换时产生**一条 WARN**，随后是 100 ms → 6.4 s 的退避重试阶梯；**从不让发给存活对端的消息延迟** |
| 持久化本地 Raft 日志 | 每节点持久化其任期、投票与已提交条目，重启时重放 |

选主死亡曾导致**永久选举抖动**，由 #1168 修复。

### 配置与启动检查

```toml
[cluster]
enabled = true
port = 9300
peers = [
  "10.0.0.11:9300=10.0.0.11:9300",   # 节点 id 即套接字地址
  "10.0.0.12:9300=10.0.0.12:9300",
  "10.0.0.13:9300=10.0.0.13:9300",
]
tick_ms = 50
auth_secret = "<同一密钥，16+ 字符，每个节点相同>"
```

`peers` 条目格式为 `"<host>:<port>=<host>:<port>"`（F-247）——**标签必须等于地址**，否则节点拒绝启动（#1171：友好的标签会让该节点的投票回执无法投递）。当前节点就是地址与自身 `bind_address` + `cluster.port` 匹配的那一条。

启动时有**三项检查**，任一不满足即拒绝启动（F-248）：

1. `cluster.auth_secret`（或 `XERJ_CLUSTER_AUTH_SECRET`）必须设置；
2. 非回环 `bind_address` 需要 `[tls]` 或 `server.allow_insecure_network_bind = true`；
3. TLS 开启且离开回环时，明文 gRPC 监听需要 `tls.allow_insecure_grpc_h2c = true`。

还有一点容易误解：`GET /_cluster/health` 报告的是**回答请求的那个节点**，不是环的成员——成员信息那部分接线仍在路线图上（F-249）。看环的状态应看日志：

```
INFO xerj_cluster::transport: TCP transport listening (authenticated) node=10.0.0.11:9300
INFO xerj_cluster::raft: Starting election node=10.0.0.12:9300 term=1
INFO xerj_cluster::raft: Became leader node=10.0.0.12:9300 term=1
```

### 失败模式

| 场景 | 行为 |
|---|---|
| leader 崩溃 | 跟随者超时并选新 leader（3 节点回环环实测约 250 ms，含一次分裂投票重试）；环在缺席死成员的情况下保持稳定；其 Raft 日志留在磁盘上等它重入 |
| 对端挂起/宕机 | 降级时一条 WARN，然后安静；重试退避 100 ms → 6.4 s；恢复时以 INFO 记录 "peer reachable again" |
| 少数派分区 | 少数派拿不到法定人数，其选举永不收敛；多数派保留 leader。Raft 安全性成立——每任期至多一个 leader |
| 节点重入 | 用同一配置重启：节点重放本地 Raft 日志并重新参与选举。**从 leader 日志追平（快照安装）仍在接线路线图上** |

### 该不该用集群

官方给的建议很直接（F-244 所在页）：

> **今天，几乎总是不要用。** 在复制接线落地之前，集群模式给你的是一个选主环——不是数据副本。

单节点没有网络往返、不需要法定人数、备份极其简单。想要一份活的备份，用 **WAL tap** 指向第二个节点（WAL tap 是单向的，F-288）。默认配置出厂即 `[cluster] enabled = false`。

## 磁盘格式与升级守卫

索引目录携带格式标记 `<data_dir>/<index>/xerj_meta.json`（F-251）：

```json
{"format_version":1,"xerj_version":"1.0.0-rc.95"}
```

- 当前二进制读取**格式 2**（`DATA_DIR_FORMAT_VERSION = 2`，基线 1）（F-252）；
- 若索引的 `format_version` 高于二进制理解范围，该索引**拒绝打开**，节点仍会启动，索引以失败原因记入日志（F-252）；
- 打开索引**从不抬升**其标记；标记从 1 升到 2 只发生在 flush 写入一个**无法原样用作文件名**的全文字段名时（长度超过 128 字节，或含 `/ \ : * ? " < > |` 之一）（F-253）；
- 没有迁移步骤也没有 migrate 子命令：更新的二进制就地打开旧数据目录（F-254）。

集群升级另有一条硬约束：**线协议没有版本协商**，新线版本的节点与旧线版本的节点双向都无法通信，因此集群升级是同一维护窗口内所有节点全停全起（F-250）。

## 相关概念

- [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md)：本文
- [12 配置与环境变量](/concepts/12-config-and-environment.md)：未接线键的完整清单与集群配置
- [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md)：备份、升级与集群抖动排障
- [00 整体架构](/concepts/00-overview.md)：写入路径与恢复路径
- 事实来源：[第二轮事实清单](/references/facts-docs.md)
- 架构洞察：[第二轮洞察](/references/insights-docs.md)
