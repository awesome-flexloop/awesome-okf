---
type: Concept
title: 配置与环境变量
description: XERJ 的配置面全貌——24 个配置段、文档键表只覆盖 12 段、16 个「接了线但没接线」的键、环境变量优先级不统一的规则、认证与 TLS、WAL tap 与 rerank 的写一次语义
tags: [xerj, 配置, toml, 环境变量, 认证, tls]
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

# 配置与环境变量

> **本篇的核心不是「有哪些键」，而是「哪些键是假的」。**
> 读配置文档时最容易受伤的地方，是那些**被接受、被校验、然后什么都不做**的键。

## 配置面有多大

| 口径 | 数量 | 来源 |
|---|---:|---|
| 代码里的配置段 | **24** 个 `*Config` 结构体 | `xerj-common/src/config.rs` |
| 文档「Full key table」覆盖的段 | **15** | `config.html`（`server`/`auth`/`tls`/`storage`/`merge`/`compression`/`fts`/`vector`/`logs`/`embedding`/`limits`/`indexing`/`cluster`/`rerank`/`wal_tap`） |
| `engine/xerj.default.toml` 交付的段 | **13** | 该文件 |
| 文档键表里缺失、但存在于 default toml 的键 | **10** | 脚本比对 |

那 10 个键是（F-259）：

```
server.auto_port            server.trusted_proxies
auth.metrics_token          storage.flush_idle_secs
limits.max_actions_per_bulk limits.snapshot_repo_allowlist
limits.hub_pack_restore     limits.max_segment_hydration_cache_mb
logging.format              logging.access_log
```

`[logging]` 整段在文档键表里**完全缺席**，但 `RUST_LOG` / `XERJ_LOG` 显然在控制日志——这条线索指向一个未文档化的段。

## 配置文件从哪来

> **只从 `--config <PATH>` 读，其次是 `XERJ_CONFIG`。别无其他搜索路径**——两者都未设时使用内置默认值，**即使 `./xerj.toml` 或 `/etc/xerj/xerj.toml` 存在**（F-256）。

源码确认：`xerj-server/src/main.rs:699` 是 `.or_else(|| std::env::var("XERJ_CONFIG").ok().map(PathBuf::from))`。

> ⚠️ **一处文档漂移**：CLI 参考页的用法摘要写 `--config` 的默认值是 `./xerj.toml`，与配置页及源码矛盾（F-257）。**以代码为准——没有这个回退。**

这意味着「把配置放在当前目录」这个直觉在 XERJ 上不成立：要么显式给 `--config`，要么给 `XERJ_CONFIG`。

## 「接了线但没接线」的完整清单

以下键**被接受并校验，但行为不变**；把其中任何一个改离默认值，只会在启动时打一条警告（F-260）。共 **16 个完全未接线** + **1 个部分接线**（`[vector] default_quantization` 只有 `"binary"` 的拒绝分支会读它）：

### `[merge]`

| 键 | 默认 | 为什么不生效 | 真正生效的东西 |
|---|---|---|---|
| `min_segments` | 10 | 被 `min_merge_count` 取代 | `[merge] min_merge_count = 4` |
| `io_rate_mb_per_sec` | 100 | 合并 I/O 在本构建不限流；尊重它的限流器位于引擎**从不构造**的合并执行器里 | 无 |
| `max_concurrent` | 1 | 合并并行度不来自这里 | `XERJ_MERGE_PARALLELISM`（默认 1） |

### `[compression]`

| 键 | 默认 | 为什么不生效 |
|---|---|---|
| `enabled` | true | 每个持久化产物都是压缩信封，**不存在未压缩写入路径**，`false` 对盘上无影响 |
| `block_size_docs` | 128 | 存储编解码器按整个 segment section 做列存，**不是按文档数分块**，没有文档块可定尺寸（范围 16～4096，启动时校验） |

### `[fts]`

| 键 | 默认 | 为什么不生效 |
|---|---|---|
| `default_analyzer` | "standard" | 文本字段用**自己的**分析器；无则用索引的 `analysis.analyzer.default`；再无则 `standard` |

### `[vector]`

| 键 | 默认 | 为什么不生效 |
|---|---|---|
| `default_metric` | "cosine" | 相似度来自**字段映射**；没有映射的字段一律按余弦 |
| `hnsw_m` | 16 | 内置 HNSW 图以**固定 M=16** 构建，该键尚未接到构建流程 |
| `hnsw_ef_construction` | 200 | 同上（须 ≥ `hnsw_m`） |
| `hnsw_ef_search` | 100 | 服务路径不读它——ANN beam 宽度来自请求的 `num_candidates`（下限 800） |
| `default_quantization` | "none" | 不是节点级默认值：**只有 `"binary"` 的拒绝会读它**；量化来自各字段映射里的 `index_options` |
| `max_dimensions` | 16384 | 只做校验（≥1），**没有任何映射或文档按它检查** |

### `[logs]`

| 键 | 默认 | 为什么不生效 |
|---|---|---|
| `retention_days` | 90 | **本构建不跑任何保留作业**，日志数据一直留到你删 |
| `time_partition` | "1h" | 日志索引**不按时间分区** |

### `[indexing]`

| 键 | 默认 | 为什么不生效 |
|---|---|---|
| `turbo_batch_size` | 1000 | turbo 请求**按一个批次**索引（范围 500～5000） |
| `turbo_parallel` | true | turbo 摄入**不再预分词**，没有可并行之物 |
| `turbo_fast_analyzer` | false | turbo 路径忽略它；字段保留各自的分析器 |

### 判据

改任何非默认键之前，问三句：

1. 键表里有没有「Not wired」标注？
2. 改离默认值时启动会打警告吗？（会打 → 它就是没接线的）
3. 该功能的真实来源在别处吗？（例：合并并行度在 `XERJ_MERGE_PARALLELISM`；量化在字段映射的 `index_options`）

## 真正生效的关键键

### `[server]`

| 键 | 默认 | 说明 |
|---|---|---|
| `rest_port` | 8080 | 原生 REST（`/v1/*`） |
| `grpc_port` | 8081 | gRPC（`xerj.v1.XerjSearch`）。**即使 `[tls]` 开启也是明文 h2c**（F-264） |
| `es_compat_port` | 9200 | ES 兼容端口；`0` 表示让操作系统分配（启动时打印），**不等于禁用监听** |
| `bind_address` | "127.0.0.1" | 所有监听器共用。**必须是 IPv4/IPv6 字面量**——不解析主机名，给了主机名则拒绝启动（在创建数据目录之前）（F-262） |
| `allow_insecure_network_bind` | false | 允许「TLS 关闭 + 非回环绑定」。默认为 false，因为明文暴露会让每个 `Authorization` 头里的 API 密钥明文过网（F-263） |
| `data_dir` | "./data" | 索引、WAL、段的根。需要快速 I/O 与足够空间 |

### `[storage]`

| 键 | 默认 | 说明 |
|---|---|---|
| `wal_sync` | "batched" | `sync` / `batched` / `async`，见 [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md) |
| `wal_batch_ms` | 100 | `batched` 下的 fsync 节奏（1～10000）；越低丢失窗口越小 |
| `wal_max_size_mb` | 1024 | WAL 轮转阈值（MiB）；越大则轮转越少、崩溃恢复越久 |
| `flush_size_mb` | 512 | 触发段 flush 的 memtable 缓冲大小（MiB） |
| `flush_interval_secs` | 30 | 即使缓冲没满，两次 flush 之间的最长墙钟间隔 |

### `[limits]`

| 键 | 默认 | 说明 |
|---|---|---|
| `max_query_memory_mb` | 512 | 每查询内存上限，超出即取消 |
| `max_concurrent_searches` | 64 | 全局在途查询上限，多余排队 |
| `max_fields_per_index` | 500 | 字段爆炸防护。**ES 默认是 1000，这里刻意更严** |
| `max_result_window` | 10000 | 允许的 `from + size` 上限；带 `index.max_result_window` 设置的索引以设置为准（不论高低）。超出请用 `search_after` 或 PIT |

> `max_process_memory_mb` **建议不写**：留空则按机器（8/16/32 GiB 档）自动定进程级上限；显式设 MiB 上限只用于**抬高**大机器上的余量——例如大的 `autoindex` 触发 429 `circuit_breaking_exception` 时。

### `[embedding]`

| 键 | 默认 | 说明 |
|---|---|---|
| `default_endpoint` | "" | OpenAI 兼容嵌入 URL。**留空则关闭摄入时的自动嵌入** |
| `default_model` | "" | 传给该端点的模型名 |
| `batch_size` | 64 | 每次嵌入 API 调用的文档数（1～2048），越大越摊薄往返成本 |
| `timeout_ms` | 5000 | 每次嵌入请求尝试的 HTTP 超时；**超时会退避重试最多 3 次**，之后摄入失败并带该错误 |

## 环境变量：优先级不统一

这是环境变量页最该记住的一句话（F-269）：

> 优先级**不是统一的**。覆盖类（如 `XERJ_BIND_ADDRESS`）压过配置文件（又被 CLI 标志压过）；机密类（如 `XERJ_CLUSTER_AUTH_SECRET`、rerank 提供方那一对）是**回退**，配置文件里的非空值胜过它们。

### 找到配置与过滤日志

| 变量 | 默认 | 说明 |
|---|---|---|
| `XERJ_CONFIG` | 未设 | 配置文件路径。`--config` 胜出；两者都无则用内置默认值（**不查 `./xerj.toml`**） |
| `XERJ_LOG` | info | tracing 过滤器，接受 `tracing_subscriber` 语法，如 `xerj_api=debug,info` |
| `RUST_LOG` | — | 回退过滤器，**仅在 `XERJ_LOG` 未设时**被检查 |

### 服务器覆盖与机密

| 变量 | 说明 |
|---|---|
| `XERJ_BIND_ADDRESS` | 覆盖 `server.bind_address`；`--bind` 胜出。**空值是启动错误** |
| `XERJ_ALLOW_INSECURE_NETWORK_BIND` | 双向覆盖 `server.allow_insecure_network_bind`。**严格布尔**（1/true/yes/on，0/false/no/off），其他值拒绝启动 |
| `XERJ_EMBED_MODE` | `lexical` / `neural` / `proxy` / `auto` / `onnx-experimental`；`--embed-mode` 胜出（F-270） |
| `XERJ_EMBEDDING_API_KEY` | 代理嵌入器的 Bearer 密钥。**仅环境变量**——没有对应配置键（F-271） |
| `XERJ_CLUSTER_AUTH_SECRET` | 集群传输密钥，`cluster.auth_secret` 为空时使用（配置值胜出）。**至少 16 字符** |
| `XERJ_MAX_PROCESS_MEMORY_MB` | `auto` / `off` / `unlimited` / MiB；胜过 `limits.max_process_memory_mb`（F-272） |
| `XERJ_SEGMENT_HYDRATION_CACHE_MB` | 段水合缓存预算；胜过 `limits.max_segment_hydration_cache_mb`；**被钳到内存的 50%**（F-273） |
| `XERJ_MERGE_PARALLELISM` | 合并并行度（默认 1）——**真正生效的那个旋钮**（F-274） |
| `XERJ_COMPAT_DISTRIBUTION` / `_VERSION` | 固定 ES 兼容身份（`elasticsearch` 或 `opensearch`，以及版本）；`--compat-*` 胜出 |
| `XERJ_DECIDE_MODE` / `_MODEL_DIR` | `/_decide` 档位（`history` 或 `local`）与本地模型目录；`--decide-*` 胜出 |
| `XERJ_ONNX_MODEL` / `_TOKENIZER` / `_LOG` | ONNX 路径与运行时日志级别（默认 warn）；标志胜出 |
| `XERJ_CONSOLE_KEY` | 64 位 hex 的 Console 主密钥，胜过 `.xerj_master_key` 文件；格式错误即报错（F-277） |
| `XERJ_NUM_CPUS` | 节点自 sizing 用的核数，**优先于 cgroup 与操作系统检测**（F-275） |
| `TOKIO_WORKER_THREADS` | 默认 `cores − 8`，范围 64～512（F-276） |

### 客户端子命令

| 变量 | 默认 | 说明 |
|---|---|---|
| `XERJ_URL` | http://localhost:9200 | `search` / `def` / `code` / `gain` / `init` / `mcp` 用的节点；`--url` 胜出。**`xerj autoindex` 故意忽略它并会明说**，必须用 `--url`（F-281） |
| `XERJ_API_KEY` | — | 客户端子命令（含 autoindex）的 API 密钥；`--api-key` 胜出 |
| `XERJ_AUTH` | — | `xerj mcp` 的 `Authorization` 头值（如 `ApiKey <key>`）；`--auth` 胜出 |
| `XERJ_CODE_HOME` | ~/.xerj-code | `xerj corpus` / `xerj code` 的语料与状态目录 |
| `XERJ_DISABLE_FEEDBACK` | — | 隐藏反馈提示（`--disable-feedback` 同效） |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` / `AWS_REGION` / `AWS_ENDPOINT_URL(_S3)` | — | `s3://` / `r2://` 根与 S3 存储后端的凭据与端点（F-278） |

### 基准与调试旋钮

二进制还读一组供基准、A/B 与剖析用的 `XERJ_*` 变量：`XERJ_FLUSH_SIZE_MB`、`XERJ_FLUSH_DOCS`、`XERJ_MERGE_INTERVAL_SECS`、`XERJ_DISABLE_QUERY_CACHE`、`XERJ_DISABLE_FAST_AGGS` 等。**生产环境保持未设置。**

其中一条危险（F-280）：**`XERJ_SKIP_WAL` 关闭预写日志**——已确认的写入会在崩溃时丢失。

### rerank 提供方

| 变量 | 默认 | 说明 |
|---|---|---|
| `TYPESAFE_API_KEY` | — | rerank 提供方密钥，`rerank.api_key` 为空时使用。**从不回显**：`GET /_xerj/rerank` 只报告是否设置、来自 env |
| `TYPESAFE_ENDPOINT` | https://api.typesafe.ai/v1/systemone | 提供方端点，`rerank.endpoint` 为空时使用。**它就是被判定的文档文本被 POST 到的地址** |

两者都在**启动时读取一次**——运行中改动不生效。设置密钥**不会**为任何搜索打开重排：请求仍须带 `rerank` 块，且 `[rerank] enabled = false` 会覆盖两个变量（F-282）。

端点在启动时被校验：必须是绝对 `http://` 或 `https://` URL 且不含 `user:password@`，否则节点拒绝启动（F-283）。

## 认证与 TLS

### API 密钥

`[auth] enabled = true`（默认）时，每个请求都必须带 `Authorization: ApiKey <key>`（F-268）。也接受 `Bearer <key>` 与 `Basic base64(user:<key>)`，但**文档化并被每个 XERJ 客户端发送的是 ApiKey**。

管理密钥是 **64 字符 hex**，写入 `<data_dir>/admin.key`，权限 **0600**（F-266）：

```
$ cat /var/lib/xerj/admin.key
4f2c9e17b83a0d5641fe72c8b90a3d5e17c46b8f92a0e35d7148bc6a03f9e2d1
```

启动横幅**点名该文件但不打印密钥**。它在重启时被**复用**而非重新生成。`admin_api_key` 留空时首次运行生成一个 256 位密钥写入该文件（F-265）。

**轮换是一次重启**（F-267）：

```sh
sudo rm /var/lib/xerj/admin.key
sudo systemctl restart xerj
sudo journalctl -u xerj | grep -A4 'First-run'
```

删除后下次启动铸造并打印一个新的；写入自己的 64 字符 hex 会被原样采纳；文件里的其他内容被视为**损坏并被替换**。

### TLS

在服务器终止 TLS。需要 `cert_path` + `key_path`（PEM）。在 Kubernetes 或负载均衡器后面应**保持关闭**，在代理处终止——一处轮换证书、一处记录握手。

### 网络边界

`bind_address` 默认 `127.0.0.1`：没配置的节点只在本机可达。`tls.enabled = false` 时非回环绑定**拒绝启动**（每个监听器都以明文 HTTP 服务，`Authorization` 头里的 API 密钥会明文过网）。要么开 TLS，要么在前面已有 TLS 终止时显式声明 `server.allow_insecure_network_bind = true`。

> **`--insecure` 逃不掉这条检查**：它清掉 `tls.enabled`，因此在 `0.0.0.0` 上同样触发拒绝启动——除非显式声明暴露是有意的。

## 两个「写一次」的表面

### WAL tap

| 键 | 默认 | 说明 |
|---|---|---|
| `enabled` | false | 把过滤后的索引子集近实时推到外部 ES 兼容目标。**单向、单节点**——不是跨集群复制（F-288） |
| `target_url` | "" | 目标集群基址；tap POST 到 `{target_url}/_bulk`。**不得携带凭据**（`user:pass@host` 启动时被拒），因为该 URL 会被 `GET /_xerj/wal_tap`、`_stats` 和日志回显；凭据放 `target_auth`（F-289） |
| `target_auth` | "" | 原样发给目标的 `Authorization` 头。**只写**：`GET` 只报告是否设置，从不报告其值（F-290） |
| `indices` | [] | 索引允许列表（glob）。空则不发送任何东西；通配符**不会**扩展到隐藏索引，XERJ 自己的 `.xerj*` 系统索引**永远不发送** |
| `poll_interval_ms` | 500 | 每个允许索引的 WAL 轮询间隔（50～60000）。**这是端到端延迟的下限**；tap 不进入写入路径（F-292） |
| `max_batch_docs` | 1000 | 每次轮询每索引最多读取并发送的 WAL 条目数（≥1） |
| `max_batch_bytes` | 5242880 | `_bulk` 请求体上限（5 MiB）。更大的批次**拆分到多个请求**，绝不截断 |
| `request_timeout_secs` | 30 | 单请求超时；超时的批次会重试，**游标不前进**，因此不丢 |
| `max_retry_backoff_secs` | 60 | 指数抖动退避上限（1～86400），启动时即检查 |
| `min_retained_generations` | 0 | 条目全部持久进段之后仍保留的轮转 WAL 代数。默认 0 时 **WAL 保留不等待目标**：超过 `storage.flush_interval_secs` 的中断会丢条目，并在 `GET /_xerj/wal_tap/_stats` 里报成 gap。**这是有界下限，不是保留租约**——额外代价至多为 n × `wal_max_size_mb`（每索引每 WAL 分片），无论 tap 是否在跑，所以停滞的目标不会撑满本节点磁盘。上限 64（F-291） |

### rerank

| 键 | 默认 | 说明 |
|---|---|---|
| `enabled` | true | 允许 rerank 搜索阶段。它是唯一在搜索期把文档文本发往节点外的特性，且**没设密钥前什么都不做**。`false` 会用 HTTP 403 拒绝每个 rerank 请求，无论环境里有什么，且什么都不发送 |
| `api_key` | "" | 提供方密钥，留空则回退 `TYPESAFE_API_KEY`；**此处的值胜过环境变量**。两处都空则未配置，rerank 请求得到 HTTP 503。**只写**：`GET /_xerj/rerank` 只报告是否设置与来源，从不报告其值。**没有按请求传密钥的机制** |
| `endpoint` | "" | 被判定的文档文本 POST 到哪里。留空则回退 `TYPESAFE_ENDPOINT`，再回退 `https://api.typesafe.ai/v1/systemone`。必须是绝对 http(s) URL 且不含凭据（启动时拒） |

`GET /_xerj/rerank`（仅超级用户）返回：是否配置、是否设了密钥、密钥来自配置还是环境、去掉查询串后的端点，以及服务端上限（F-287）。

服务端还有字符串上限（F-284）：`rerank.instructions` 2000 字符（提供方线格式每条被判定文档都重复一次）、问题 4000 字符、model 128 字符；超长返回 400 并指名字段。

**每个分页请求都会重新判定一次窗口**（F-285）——成本敏感时应取一次窗口后在客户端分页。

## 原生 REST API（端口 8080）

13 个端点（F-335）：`GET /v1/health`、`GET /v1/metrics`、`PUT/GET/DELETE /v1/indices/:name`、`POST /v1/indices/:name/docs`、`POST /v1/indices/:name/turbo-ingest`、`POST /v1/indices/:name/search`、`POST /v1/indices/:name/_explain`、`POST /v1/indices/:name/logs`、`POST /v1/indices/:name/syslog`、`POST /v1/indices/:name/otlp`、`GET /v1/indices/:name/_mapping`。

> ⚠️ **两处需要以代码为准**：
> ① **explain 端点的真实路径是 `POST /v1/indices/:name/explain-plan`**（`router.rs:166`）——文档的 `_explain` 与迁移页的 `/v1/explain-plan` 都不对（F-336）。
> ② **文档页不是完整清单**：`router.rs` 实际注册 **31** 个 `/v1/` 路由模式，文档只列了 13 个；未列出的包括 `/v1/admin/backup`、`/v1/admin/flush`、`/v1/admin/slow_queries`、`/v1/ask`、`/v1/cluster/health`、`/v1/dashboard/summary`、`/v1/embedding/identity`、`/v1/health/ready`、`/v1/indices/:name/encodings`、`/v1/indices/:name/enrich`、`/v1/indices/:name/ingest`、`/v1/models`、`/v1/pipelines/:name`、`/v1/schema/:name`、`/v1/schema/:name/evolve`、`/v1/systemone` 等（F-335）。

## 相关概念

- [12 配置与环境变量](/concepts/12-config-and-environment.md)：本文
- [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md)：存储键与集群键的语义
- [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md)：生产配置样例与热加载边界
- [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)：客户端侧的认证回退
- 事实来源：[第二轮事实清单](/references/facts-docs.md)
- 架构洞察：[第二轮洞察](/references/insights-docs.md)
