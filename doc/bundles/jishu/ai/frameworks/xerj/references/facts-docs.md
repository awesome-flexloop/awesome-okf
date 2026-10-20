---
type: Reference
title: XERJ 官方文档站事实清单
description: 第二轮事实登记——来自 xerj.org/docs/ 46 页文档站的事实（F-207～F-338），每条标注页面与来源，并记录与源码交叉核验的结果
tags: [xerj, 事实清单, 官方文档, 交叉核验]
generated: { by: source-code-to-okf-wiki/R, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-docs-site
    resource: https://xerj.org/docs/
    title: XERJ 官方文档站（v1.0.0-rc.97）
  - id: xerj-docs-source
    resource: /references/docs-source.md
    title: 官方文档站信源登记
  - id: xerj-facts
    resource: /references/facts.md
    title: 第一轮事实清单（源码）
---

# XERJ 官方文档站事实清单（第二轮）

> 采集自 `xerj.org/docs/`（版本 v1.0.0-rc.97），落地快照 `landing/docs/` 46 页。
> 编号续接第一轮（F-207 起）。每条标注页面与来源；**凡能在源码复核的，均已回到 `engine/crates/` 核验**，核验结论写在「核验」列或本表末尾的「交叉核验记录」。

## K 组：文档站与查询/聚合

| 编号 | 事实 | 页面 | 核验 |
|---|---|---|---|
| F-207 | 文档站共 46 个 HTML 页面，页脚与侧栏版本标识为 `XERJ.AI · V1.0.0-RC.97 · 2026-08-11` | 全站 | 脚本计数；与 `engine/Cargo.toml` 的 `version = "1.0.0-rc.97"` 一致 |
| F-208 | 文档站首页声明 "Every key, every flag, every default in these docs comes out of the Rust crates under `engine/crates/`. If the docs and the code disagree, the code is right." | `index.html` | — |
| F-209 | 支持的查询类型共 **50** 个，全部是同一个 `QueryNode` 枚举的变体，编译到同一执行计划 | `queries.html` | ✅ `xerj_query::parser::SUPPORTED_QUERY_TYPES` 计数 = 50 |
| F-210 | 另有 2 个查询键被识别但**显式拒绝**：`has_child` 与 `has_parent`，解析期返回 400，理由是 XERJ 从不物化父子连接 | `queries.html` | ✅ `REJECTED_QUERY_TYPES` = `has_child, has_parent` |
| F-211 | 聚合类型共 **62** 个，覆盖 metric / bucket / sampling / scope / geo / pipeline 六个家族 | `aggregations.html` | ✅ `xerj_engine::aggs::SUPPORTED_AGG_TYPES` 计数 = 62 |
| F-212 | 站点导航栏的摘要写 "Query types · 32 variants · one planner"，与同页正文的 50 个及源码的 50 个不一致 | `index.html` 导航 | ❌ 漂移（见 K 组交叉核验记录 1） |
| F-213 | 每个桶聚合返回**精确计数**，桶路径上没有 HyperLogLog 近似 | `aggregations.html` | — |
| F-214 | 唯一的精确性例外是采样家族（`sampler`、`random_sampler`、`diversified_sampler`）：按 `_score` 截断到前 `shard_size` 条匹配文档（默认 200），其子聚合只看到该切片 | `aggregations.html` | — |
| F-215 | 索引活文档超过 **10,000** 后，`terms` 及其他列式可用聚合改读 doc-values ordinal 直方图（`fast_aggs.rs`）而不是扫描倒排；低于该阈值走 JSON 路径，文档称其为参考实现 | `aggregations.html` | — |
| F-216 | `percentiles` 默认在排序值上做线性插值；`hdr` 选项切到 HdrHistogram 最近秩 | `aggregations.html` | — |
| F-217 | `cardinality` 是精确的：每个不同值都进哈希集合，内存随基数增长 | `aggregations.html` | — |
| F-218 | 官方文档 `analyzers.html` 列出 **4** 个内置分析器（`standard`、`whitespace`、`simple`、`english`）；而源码 `xerj-fts/src/analyzer.rs` 的 `register_defaults()` 实际注册 **11** 个：`standard`、`english`、`whitespace`、`keyword`、`lowercase`、`stemmer`、`cjk`、`thai`、`icu_folding`、`ecommerce`、`code`。文档的 `simple` 在整个 `engine/` 树中**零次出现**；源码的 `keyword`/`lowercase`/`stemmer`/`cjk`/`thai`/`icu_folding`/`ecommerce`/`code` **未被文档提及** | `analyzers.html` / 源码 | ❌ 漂移（见 K 组交叉核验记录 5）；✅ `self.register(` 计数 = 12（其中 1 处为用户自定义分析器） |
| F-219 | 各分析器的真实管线（源码注册处注释）：`standard` = Unicode 词切分 + 小写化，**无停用词、无词干**（刻意改成与 ES 的 `standard` 逐语义一致——旧管线含英文停用词会丢掉 "GET"、Snowball 词干会过度匹配 "static"/"statics"）；`english` = **旧的** `standard` 管线（unicode 切分 + 小写化 + 英文停用词 + Snowball 词干）；`whitespace` = 只按空白切分、无归一化；`keyword` = 整个输入作为单个 token；`lowercase` = whitespace 分词 + 小写化；`stemmer` = standard + Snowball 词干、无停用词；`cjk` = CJK/日/韩 bigram 分词器；`thai` = 泰文词边界分词器；`icu_folding` = NFKC 归一化过滤 + standard 分词器；`ecommerce` = standard 分词 + 精选同义词表（**同义词扩展是双向的**：搜 "sneakers" 也匹配含 "trainers"/"shoes" 的文档）+ Snowball 词干；`code` = 面向代码的管线 | `xerj-fts/src/analyzer.rs:1094-1230` | ✅ 逐条读注册处注释 |
| F-220 | 没有自有分析器的文本字段用索引声明的 `analysis.analyzer.default`，索引未声明则用 `standard` | `analyzers.html` | ✅ 与 `config.html` 的 `[fts] default_analyzer` 未接线说明一致 |
| F-221 | 节点侧 `[fts] default_analyzer` 被接受但**未接线**，改离默认值会在启动时打警告 | `analyzers.html` / `config.html` | — |

## L 组：摄取、存储、压缩、集群

| 编号 | 事实 | 页面 | 核验 |
|---|---|---|---|
| F-222 | 进程内解析器随写入器运行，4 条摄取路径覆盖多数真实负载：`turbo-ingest`（NDJSON 批量）、`logs`（自动识别 Apache/Nginx/ISO-8601 时间戳）、`syslog`（RFC-5424）、`otlp`（OpenTelemetry HTTP protobuf，无需 collector） | `ingest.html` | — |
| F-223 | OTLP 的 trace 落成**连通图**而非扁平文档 | `ingest.html` | — |
| F-224 | 背压是端到端的：memtable 接近 `flush_size_mb` 时写入器阻塞而非 OOM；WAL 滚动快于 segment flush 时 `turbo-ingest` 返回 429 并带 `Retry-After` 头 | `ingest.html` | — |
| F-225 | 每个 segment 是**三个文件**，不是含十二个文件的 segment 目录：`segment.seg`（列式数据）、`segment.sidx`（seek 用的稀疏跳过索引）、`segment.ids`（外部 doc id → 内部序号旁挂文件） | `storage.html` | ✅ `xerj-storage/src/segment.rs` |
| F-226 | 三个文件全部 mmap，读取直接来自操作系统页缓存，无应用侧缓冲 | `storage.html` | — |
| F-227 | 列存布局：每个字段一条独立列 run，查询只触碰实际读取的列；整数列用 delta-of-delta 或 FOR，字符串列用 dictionary + FST | `storage.html` | — |
| F-228 | 更新与删除通过写新 segment 加墓碑实现；合并把存活文档重写进更大的 segment | `storage.html` | — |
| F-229 | 每个索引一个 WAL，按 `wal_max_size_mb`（默认 1024 MiB）分代轮转；旧代在 flush 检查点越过尾代后释放 | `storage.html` | — |
| F-230 | `wal_sync` 三档：`sync`（每次确认写入前 fsync，一个 `_bulk` 请求一次 fsync 即 group commit，断电可持久，对齐 ES 的 `index.translog.durability: request`）、`batched`（默认，写入立即到达内核，后台每 `wal_batch_ms`（默认 100 ms）fsync，断电最多丢最后约 100 ms 已确认写入）、`async`（从不 fsync，断电最多丢约 1 秒，仅供开发/基准） | `storage.html` | ✅ `config.html` 键表同 |
| F-231 | 合并路径实际读取四个键：`max_segment_mb`（8192，达到此大小不再合并）、`tier_floor_mb`（4，层边界）、`min_merge_count`（4，逐层触发阈值）、`max_merge_count`（16，一次批量合并的段数上限，因而也是合并峰值内存的上限） | `storage.html` | ✅ `config.html` 示例块同 |
| F-232 | `strategy` 只有一个已实现值 `size_tiered`；`log_structured` 在启动时被拒，而不是被静默替换 | `storage.html` | ✅ `config.html` 同 |
| F-233 | 合并段的另三个键被接受但未接线：`min_segments`（被 `min_merge_count` 取代）、`io_rate_mb_per_sec`（本构建不做合并 I/O 限流，尊重它的限流器位于引擎从不构造的 storage-crate 合并执行器里）、`max_concurrent`（合并并行度实际来自 `XERJ_MERGE_PARALLELISM`，默认 1） | `storage.html` | ✅ `config.html` 同 |
| F-234 | 列编码共 **9** 种，写入时按列形状自动选择：`BitsetEnum`（≤16 个不同值 → 4 位索引 + 位图）、`Dictionary`（≤256 个不同字符串）、`DeltaTimestamp`（检测 Apache/Nginx/ISO → 秒级 delta-of-delta）、`PackedIp`（IPv4 存 u32，IPv6 存 u128）、`UrlTemplate`（路径归一化，`/users/:id` 把高基数 URL 收敛成模板）、`Varint`（小整数）、`Bitpacked`（布尔，8 个/字节）、`FixedPrecision`（浮点存缩放 varint）、`RawString`（高基数回退） | `compression.html` | ✅ `xerj-compress/src/field_codec.rs` |
| F-235 | 块压缩三个 Zstandard 力度档：`fast` = L1、`balanced` = L3（默认）、`best` = L6（冷存储） | `compression.html` | — |
| F-236 | 力度在**合并时**生效而非 flush 时：flush 恒写 L3，因为 flush 是摄入的背压临界点——把 flush 力度调高曾让持续吞吐从 **1.55M docs/s 崩到 21k docs/s** 且 75% 文档被拒 | `compression.html` | — |
| F-237 | 不同力度的 segment 可在同一索引内共存，无需迁移也无需重建：Zstd 解码不依赖写入时的力度 | `compression.html` | — |
| F-238 | `[compression] enabled` 与 `block_size_docs` 被接受但未接线（每个持久化产物都是压缩信封，不存在未压缩写入路径；存储编解码器按整个 segment section 做列存而非按文档数分块）——#318 之前这两个键被静默忽略 | `compression.html` | ✅ `config.html` 同 |
| F-239 | 集群模式使用内嵌 Raft 实现，无需 etcd / ZooKeeper / Consul；集群模式是一个配置开关，不是独立进程 | `clustering.html` | — |
| F-240 | 集群模式**当前不提供**元数据复制：节点 A 创建的索引在节点 B 上不存在，没有生产路径会提出 `ClusterCommand` | `clustering.html` | — |
| F-241 | 集群模式**当前不提供**文档复制：节点 A 上 PUT 文档、节点 B 上 GET 返回 404 `index_not_found`（3 节点环实测） | `clustering.html` | — |
| F-242 | 集群模式**当前不提供**分片路由：没有到主分片的转发、没有副本读，每个节点的 API 只服务该节点的存储 | `clustering.html` | — |
| F-243 | 集群模式**当前不提供**节点生命周期 API：没有 drain / activate / remove 端点，也没有 region split-merge。文档记载此前版本的这一页写过它们，但二进制从未发布过 | `clustering.html` | — |
| F-244 | 集群里真实且被测试过的是：选主（每任期恰好一个 leader，随机 150–300 ms 选举超时，自动故障转移；3 节点回环环（tick 50 ms）实测杀 leader 后约 **250 ms** 选出新 leader）、带认证的节点间传输、持久化的本地 Raft 日志 | `clustering.html` | — |
| F-245 | 节点间每条连接用 cluster secret 做 HMAC-SHA256 挑战认证；不存在未认证模式，节点无 secret 时拒绝启动 | `clustering.html` | ✅ `config.html` 同 |
| F-246 | 死节点隔离：宕机或无响应的对端在状态切换时产生一条 WARN，随后是 100 ms → 6.4 s 的退避重试阶梯；它从不让发给存活对端的消息延迟 | `clustering.html` | — |
| F-247 | `peers` 条目格式为 `"<host>:<port>=<host>:<port>"`：节点 id 即套接字地址，标签与地址不一致时节点拒绝启动（#1171：友好的标签会让该节点的投票回执无法投递） | `clustering.html` | ✅ `config.html` 同 |
| F-248 | 集群模式启动时有三项检查，任一不满足即拒绝启动：`cluster.auth_secret`（或 `XERJ_CLUSTER_AUTH_SECRET`）必须设置；非回环 `bind_address` 需要 `[tls]` 或 `server.allow_insecure_network_bind = true`；TLS 开启且离开回环时，明文 gRPC 监听需要 `tls.allow_insecure_grpc_h2c = true` | `clustering.html` | — |
| F-249 | `GET /_cluster/health` 报告的是**回答请求的那个节点**，不是环的成员（那部分接线仍在路线图上） | `clustering.html` | — |
| F-250 | 集群升级没有线协议版本协商：新线版本的节点与旧线版本的节点双向都无法通信，因此集群升级是同一维护窗口内所有节点全停全起，不是滚动重启 | `upgrades.html` | — |
| F-251 | 磁盘格式守卫是每个索引目录携带的格式标记 `<data_dir>/<index>/xerj_meta.json`，内容形如 `{"format_version":1,"xerj_version":"1.0.0-rc.95"}` | `upgrades.html` | ✅ `xerj-storage/src/index_store.rs`：`DATA_DIR_META_FILE = "xerj_meta.json"` |
| F-252 | 当前二进制读取格式 2（`DATA_DIR_FORMAT_VERSION = 2`，基线 `DATA_DIR_BASE_FORMAT_VERSION = 1`）；若索引的 `format_version` 高于二进制理解范围，该索引**拒绝打开**，节点仍会启动，索引以失败原因记入日志 | `upgrades.html` | ✅ 同上常量 |
| F-253 | 打开索引从不抬升其标记；标记从 1 升到 2 只发生在 flush 写入一个**无法原样用作文件名**的全文字段名时（长度超过 128 字节，或含 `/ \ : * ? " < > \|` 之一） | `upgrades.html` | ✅ `xerj-fts/src/index.rs` 的 `field_file_component` |
| F-254 | 没有迁移步骤也没有 migrate 子命令：更新的二进制就地打开旧的数据目录 | `upgrades.html` | — |
| F-255 | 滚动回退 = 重装上一个二进制：对标记版本仍可被旧二进制读取的索引有效；标记已越过的索引在旧二进制下打不开，回退意味着恢复升级前的备份 | `upgrades.html` | — |

## M 组：配置、环境变量、认证与安全

| 编号 | 事实 | 页面 | 核验 |
|---|---|---|---|
| F-256 | 配置文件只从 `--config <PATH>` 读取，其次是 `XERJ_CONFIG`；**别无其他搜索路径**——两者都未设时使用内置默认值，即使 `./xerj.toml` 或 `/etc/xerj/xerj.toml` 存在 | `config.html` | ✅ `xerj-server/src/main.rs:699` 为 `.or_else(\|\| std::env::var("XERJ_CONFIG")...)` |
| F-257 | CLI 参考页的用法摘要写 `--config` 的默认值是 `./xerj.toml`，与配置页及源码矛盾 | `cli.html` | ❌ 漂移（见 M 组交叉核验记录 2） |
| F-258 | 配置代码里有 **24** 个 `*Config` 结构体（对应 24 个配置段），文档的「Full key table」覆盖 **15** 段（`server`/`auth`/`tls`/`storage`/`merge`/`compression`/`fts`/`vector`/`logs`/`embedding`/`limits`/`indexing`/`cluster`/`rerank`/`wal_tap`），`engine/xerj.default.toml` 交付 **13** 段 | `config.html` / 源码 | ✅ `xerj-common/src/config.rs` 结构体计数；✅ 文档键表段落计数；✅ default.toml 段计数 |
| F-259 | 下列 10 个键存在于 `xerj.default.toml` 但**不在**文档的键表中：`server.auto_port`、`server.trusted_proxies`、`auth.metrics_token`、`storage.flush_idle_secs`、`limits.max_actions_per_bulk`、`limits.snapshot_repo_allowlist`、`limits.hub_pack_restore`、`limits.max_segment_hydration_cache_mb`、`logging.format`、`logging.access_log` | `config.html` / `xerj.default.toml` | ✅ 脚本比对 |
| F-260 | 配置里存在大量「被接受但未接线」的键：**16 个完全未接线**（`[merge] min_segments / io_rate_mb_per_sec / max_concurrent`、`[compression] enabled / block_size_docs`、`[fts] default_analyzer`、`[vector] default_metric / hnsw_m / hnsw_ef_construction / hnsw_ef_search / max_dimensions`、`[logs] retention_days / time_partition`、`[indexing] turbo_batch_size / turbo_parallel / turbo_fast_analyzer`），**外加 1 个部分接线**（`[vector] default_quantization` 只有 `"binary"` 的拒绝分支会读它）；改离默认值会在启动时打警告，但行为不变 | `config.html` | ✅ 逐条见键表描述；✅ 文档中 "not wired" 出现 29 次 |
| F-261 | `[merge] strategy` 的 `log_structured` 值在启动时被拒，而不是被静默替换成 `size_tiered`——文档给出的理由是：为一个读放大问题选了 leveled 策略的运维者，不该被悄悄跑成另一种策略 | `config.html` | — |
| F-262 | `[server] bind_address` 必须是 IPv4 或 IPv6 字面量：**不解析主机名**，给了主机名的节点拒绝启动（且在数据目录创建之前） | `config.html` / `cli.html` | — |
| F-263 | `allow_insecure_network_bind` 是「明文暴露是有意为之」的显式声明：默认为 false，`tls.enabled = false` 时非回环绑定会拒绝启动，因为每个监听器都以明文 HTTP 服务，`Authorization` 头里的 API 密钥会明文过网 | `config.html` | — |
| F-264 | gRPC 监听即使在 `[tls] enabled = true` 时也始终是明文 h2c；离开回环且 TLS 开启时节点拒绝启动，除非 `tls.allow_insecure_grpc_h2c = true` | `config.html` | — |
| F-265 | `[auth] admin_api_key` 留空时首次运行生成一个 256 位密钥，写入 `<data_dir>/admin.key` | `config.html` | — |
| F-266 | 管理密钥是 **64 字符 hex 字符串**，写入 `<data_dir>/admin.key` 且权限 **0600**；启动横幅点名该文件但**不打印密钥**；它在重启时被复用而非重新生成 | `security.html` | — |
| F-267 | 密钥轮换是一次重启：删除 `admin.key` 后下次启动铸造并打印一个新的；写入自己的 64 字符 hex 会被原样采纳；文件里的其他内容被视为损坏并被替换 | `security.html` | — |
| F-268 | 认证接受 `Authorization: ApiKey <key>`，同时也接受 `Bearer <key>` 与 `Basic base64(user:<key>)`；文档化并被每个 XERJ 客户端发送的是 ApiKey | `security.html` | — |
| F-269 | 环境变量的优先级**不统一**：覆盖类（如 `XERJ_BIND_ADDRESS`）压过配置文件又被 CLI 标志压过；机密类（如 `XERJ_CLUSTER_AUTH_SECRET`、rerank 提供方那一对）是回退，配置文件里的非空值胜出 | `env.html` | — |
| F-270 | `XERJ_EMBED_MODE` 接受 `lexical`、`neural`、`proxy`、`auto`、`onnx-experimental`；`--embed-mode` 胜出 | `env.html` | ✅ 与 `main.rs` 的 `CliArgs.embed_mode` 一致 |
| F-271 | `XERJ_EMBEDDING_API_KEY` 是代理嵌入器的 Bearer 密钥，**仅环境变量**——没有对应的配置键 | `env.html` | — |
| F-272 | `XERJ_MAX_PROCESS_MEMORY_MB` 接受 `auto`、`off`、`unlimited` 或 MiB，胜过 `limits.max_process_memory_mb` | `env.html` | — |
| F-273 | `XERJ_SEGMENT_HYDRATION_CACHE_MB` 胜过 `limits.max_segment_hydration_cache_mb`，且被钳制到内存的 50% | `env.html` | — |
| F-274 | `XERJ_MERGE_PARALLELISM`（默认 1）才是真正生效的合并并行度——`[merge] max_concurrent` 未接线 | `env.html` / `config.html` | ✅ 同上 |
| F-275 | `XERJ_NUM_CPUS` 给出的核数优先于 cgroup 与操作系统检测，用于节点自 sizing | `env.html` | — |
| F-276 | `TOKIO_WORKER_THREADS` 默认为 `cores − 8`，范围 64～512 | `env.html` | — |
| F-277 | `XERJ_CONSOLE_KEY` 是 64 位 hex 的 Console 主密钥，胜过 `.xerj_master_key` 文件；格式错误即报错 | `env.html` | — |
| F-278 | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` / `AWS_REGION` / `AWS_ENDPOINT_URL(_S3)` 用于 `s3://` / `r2://` 根与 S3 存储后端 | `env.html` | — |
| F-279 | 二进制还读一组供基准、A/B 与剖析用的 `XERJ_*` 变量（`XERJ_FLUSH_SIZE_MB`、`XERJ_FLUSH_DOCS`、`XERJ_MERGE_INTERVAL_SECS`、`XERJ_DISABLE_QUERY_CACHE`、`XERJ_DISABLE_FAST_AGGS` 等），生产环境应保持未设置 | `env.html` | — |
| F-280 | `XERJ_SKIP_WAL` 关闭预写日志，**已确认的写入会在崩溃时丢失** | `env.html` | — |
| F-281 | `XERJ_URL` 对 `search` / `def` / `code` / `gain` / `init` / `mcp` 生效；`xerj autoindex` **故意忽略它并会明说**，必须用 `--url` | `env.html` | — |
| F-282 | `TYPESAFE_API_KEY` 与 `TYPESAFE_ENDPOINT` 是 rerank 提供方的环境回退；配置文件的非空值胜出，因此服务环境中一个游离的变量无法悄悄改变文档文本被送往何处 | `env.html` | ✅ `config.html` 同 |
| F-283 | `TYPESAFE_ENDPOINT` 在启动时被校验：必须是绝对的 http:// 或 https:// URL 且不含 `user:password@`，否则节点拒绝启动 | `env.html` | ✅ `config.html` 同 |
| F-284 | rerank 的字符串有服务端上限：`rerank.instructions` 2000 字符（提供方线格式每条被判定文档都重复一次）、问题 4000 字符、model 128 字符；超长返回 400 并指名字段 | `api-es-compat.html` | — |
| F-285 | rerank 的**每个分页请求都会重新判定一次窗口**；成本敏感时应取一次窗口后在客户端分页 | `api-es-compat.html` | — |
| F-286 | `rerank` 与 `sort`、`search_after`、`collapse`、scroll、`size:0` 同时使用会被 400 拒绝；`_msearch`、搜索模板、`_async_search`、`_rank_eval` 按名称拒绝该块，而不是丢弃它 | `api-es-compat.html` | ✅ 第一轮 F-097 |
| F-287 | `GET /_xerj/rerank`（仅超级用户）返回是否配置、是否设了密钥、密钥来自配置还是环境、去掉查询串后的端点，以及服务端上限；**从不返回密钥本身** | `api-es-compat.html` / `config.html` | — |
| F-288 | WAL tap 是单向的、单节点的，**不是跨集群复制** | `config.html` | — |
| F-289 | WAL tap 的 `target_url` 不得携带凭据（`user:pass@host` 启动时被拒），因为该 URL 会被 `GET /_xerj/wal_tap`、`_stats` 和日志回显；凭据放 `target_auth` | `config.html` | — |
| F-290 | WAL tap 的 `target_auth` 是只写的：`GET /_xerj/wal_tap` 只报告是否设置，从不报告其值 | `config.html` | — |
| F-291 | WAL tap 的 `min_retained_generations` 是**有界下限而不是保留租约**：额外代价至多为 n × `storage.wal_max_size_mb`（每索引每 WAL 分片），无论 tap 是否在跑，因此停滞的目标不会撑满本节点磁盘；上限 64，启动时即做范围检查，配置文件不能绕过该上界 | `config.html` | — |
| F-292 | WAL tap 的 `poll_interval_ms` 默认 500（范围 50～60000），是端到端延迟的下限；tap 不进入写入路径 | `config.html` | — |

## N 组：生产运维、备份、升级与排障

| 编号 | 事实 | 页面 | 核验 |
|---|---|---|---|
| F-293 | 生产部署的心智模型是「一个二进制、一个配置文件、一个数据目录」 | `operations.html` | — |
| F-294 | 官方 systemd 单元以非 root 用户运行并启用加固项（`NoNewPrivileges`、`PrivateTmp`、`ProtectSystem=strict`、`ProtectHome`、`ReadWritePaths`、`ProtectKernelTunables`、`ProtectKernelModules`、`ProtectControlGroups`、`SystemCallArchitectures`、`LockPersonality`），`LimitNOFILE=1048576` | `operations.html` | — |
| F-295 | 存活与就绪是两个独立探针：`GET /v1/health` 在进程绑定监听器后即返回 200（liveness）；`GET /v1/health/ready` 只在 WAL 完整重放且最后一次 flush 检查点落盘后返回 200（readiness），响应形如 `{"status":"ready","wal_replayed":true,"indices":4,"uptime_s":17}` | `operations.html` | — |
| F-296 | 多数可调项通过 SIGHUP 热加载；端口、TLS 证书、`data_dir`、`cluster.enabled` 需要完整重启，热加载会被拒绝并在日志里给出明确错误 | `operations.html` | — |
| F-297 | 日志走 stdout，结构化格式（生产为 JSON，TTY 下为 pretty），由 `RUST_LOG` 控制；级别从低到高为 `error → warn → info → debug → trace`，`info` 是生产默认 | `operations.html` | ✅ `env.html` 同 |
| F-298 | 容量规划的三个主导数字：磁盘约为 ES 的 1/1.6（实测 1.61×），并为合并预留 30% 空间（合并两个 5 GiB 段需要临时 10 GiB 空闲）；RAM 空闲基线约 400 MB，向量字段按 `dims × 4` 字节叠加（**即便 scalar8 量化也不减常驻**，只改评分精度，#392），memtable 按索引受 `flush_size_mb` 约束；CPU 每个 turbo_parallel worker 占一核，繁忙节点至少留 2 核给查询路径 | `operations.html` | — |
| F-299 | 每个打开的 segment 占 **3 个文件描述符**（data / sidx / ids），1000 段的索引约需 3000 个 fd | `operations.html` | ✅ 与 F-225 的三文件结构一致 |
| F-300 | 指标端点是 `GET /v1/metrics`，Prometheus 文本格式；计数器 7 个（`docs_indexed`、`queries_executed`、`bytes_written`、`bytes_read`、`rerank_requests`、`rerank_documents_judged`、`rerank_provider_tokens`），直方图 5 个（`query_latency`、`index_latency`、`flush_duration`、`merge_duration`、`wal_write_latency`），仪表 5 个（`segment_count`、`doc_count`、`memory_usage`、`active_searches`、`wal_size_bytes`） | `metrics.html` | ✅ `xerj-common/src/metrics.rs` |
| F-301 | `rerank_documents_judged` 是计费单位；`rerank_requests` 按结果分为 applied / degraded / refused / failed | `metrics.html` | — |
| F-302 | 备份是纯文件系统操作：segment 写后不变、WAL 只追加，因此可以在服务运行时复制数据目录，恢复就是把目录复制回去 | `backup-restore.html` | — |
| F-303 | 热备份前调 `POST /v1/admin/flush` 强制 memtable flush，响应形如 `{"flushed_indices":4,"segments_written":4,"wal_checkpoint":12847}`；随后 rsync；由于 segment 是内容寻址的，后续 rsync 只传新 segment | `backup-restore.html` | — |
| F-304 | `POST /v1/admin/backup` 把数据目录的完整副本流式传到任意 S3 兼容端点，请求体为 `{destination, credentials:{endpoint,access_key,secret_key}, flush_first}`，响应为 `{backup_id, bytes, duration_ms}`；**默认可增量**（只上传目标端没有的 segment） | `backup-restore.html` | — |
| F-305 | 恢复流程：停服 → 替换数据目录 → 启动，**无导入步骤**——启动时的 WAL 重放从磁盘上的文件重建 memtable 状态 | `backup-restore.html` | — |
| F-306 | 单索引备份：先 `POST /v1/indices/<name>/flush`，再 tar 该子目录 | `backup-restore.html` | — |
| F-307 | 集群备份就是把单节点流程在每个节点上跑一遍：索引数据当前是节点本地的，每个节点持有它所服务索引的完整副本，没有分片子集也没有 drain API 需要排序 | `backup-restore.html` | ✅ 与 F-241 一致 |
| F-308 | XERJ 遵循 SemVer：补丁版本是可直接替换的；次版本可能引入向后兼容的 schema 字段；主版本可能改变磁盘格式，此时二进制随附一次性迁移工具 | `upgrades.html` | — |
| F-309 | 单节点升级四步：备份 → 取新版本并**校验**（解压与校验和链式绑定，校验失败的包不会被解到运行节点上）→ 原地替换二进制 → 用 `GET /v1/health` 的 `.version` 确认 | `upgrades.html` | — |
| F-310 | 单节点升级的停机时间等于 WAL 重放时间，低百万级活文档负载下通常是数秒 | `upgrades.html` | — |
| F-311 | 排障页给出 6 类症状，每类都给出「症状 → 指标 → 日志行 → 该改的配置键」四件套 | `troubleshooting.html` | — |
| F-312 | WAL 自愈有三种情形且不需要人工修复命令：撕裂的尾部被截断（日志 `WAL open: healed torn tail (crash/ENOSPC leftover) by truncation`）、文件中段损坏则冻结该文件且追加转到新分代（`WAL open: mid-file corruption detected`）、重放时跳过不可读帧（`skipping corrupt WAL entry during replay`）；撕裂或损坏区域的写入丢失，其前的全部重放 | `troubleshooting.html` | — |
| F-313 | 集群 flapping（leader 每几秒换一次）的处置是把 `[cluster] tick_ms` 从 50 提到 150 或 250，让心跳在慢网络上有余量；**永远不要把 tick 间隔降到最差节点对 RTT 以下**；抬完 tick 仍持续抖动是缺陷而非调参问题，应带 `RUST_LOG=xerj_cluster=debug` 提 issue | `troubleshooting.html` | — |
| F-314 | WAL tap 目标显示数据陈旧的检查点是 `GET /_xerj/wal_tap/_stats`（看 gap 与重试退避），再降 `poll_interval_ms` 或提 `max_batch_docs`；单节点上没有副本会陈旧——搜索读活跃 memtable 加 segment，本地结果总是当前 | `troubleshooting.html` | — |
| F-315 | 提 issue 前的诊断采集是 5 条命令（`--version`、`/v1/health`、`/v1/metrics`、`/_cluster/health`、`journalctl`）；**报告里要排除配置文件与 admin.key**——密钥是节点的管理员凭据，应手工粘贴相关配置段 | `troubleshooting.html` | — |
| F-316 | 内存查询上限超限的日志串是 "query cancelled: max_query_memory_mb exceeded"；并发超限表现为 `active_searches` 顶到 `max_concurrent_searches` | `troubleshooting.html` | — |
| F-317 | 合并期间磁盘满的根因是没有为合并暂存空间预留：合并两个 N 大小的段需要 2N 空闲直到合并完成；处置是降 `[merge] max_segment_mb` 或腾磁盘 | `troubleshooting.html` | — |

## O 组：ES 兼容面、滚动升级与语义差异

| 编号 | 事实 | 页面 | 核验 |
|---|---|---|---|
| F-318 | 兼容监听器在 `GET /` 上宣称 **8.13.0** 并在响应里发 `X-Elastic-Product: Elasticsearch`——这正是 Kibana 与官方客户端在愿意对话前检查的两个握手门 | `migration-from-es.html` | — |
| F-319 | 一致性套件是 ES 公开 rest-api-spec YAML 测试的**精选 202 文件子集**，另加 XERJ 自写的 AI 原生表面用例；本地树中 `engine/tests/es-compat-yaml/yaml` 下共 **221** 个 `.yml` 文件（脚本计数） | `migration-from-es.html` | ✅ 脚本计数 = 221；分布：aggregations 82、search 74、search.vectors 11、bulk 10、indices.create 8 等 |
| F-320 | 迁移页记录 2026-09-20 的一次全量跑通过 **1,371 / 1,374** 个用例（3 skip），而同一发布版的 README 徽章写 **1366/1369** | `migration-from-es.html` / `README.md` | ❌ 漂移（见 O 组交叉核验记录 3） |
| F-321 | 一致性 runner 的两个已知限制：不校验错误行为（期望值未被断言），且只讲原始 HTTP——CI 里不跑任何 ES 客户端库 | `migration-from-es.html` | — |
| F-322 | 仓库里没有 Kibana 端到端测试，也没有客户端版本矩阵；被验证的是线协议本身与 curl 形状的请求配方 | `migration-from-es.html` | — |
| F-323 | 「第一天就能用」的清单：索引 CRUD、文档 CRUD、bulk、查询 DSL（50 种）、聚合（62 种）、集群端点、`_delete_by_query` | `migration-from-es.html` | ✅ 与 F-209、F-211 一致 |
| F-324 | 「需要重写」的清单：整索引 scroll 读取（Painless 脚本与脚本化度量未实现、runtime fields 不支持、跨集群搜索在 v0.1 是单集群、ML 作业不是特性、Watcher/告警框架需用 `/v1/explain-plan` 端点加外部规则运行器、ILM 不执行且没有保留作业） | `migration-from-es.html` | — |
| F-325 | 已知语义差异：BM25 分数是 XERJ 自己的，排序顺序符合查询意图，但精确 `_score` 浮点与 ES 不同，且会随后台合并移动 collection statistics 而对同一查询发生位移——与两个 ES 次版本之间的内部差异同类 | `migration-from-es.html` | — |
| F-326 | `_cat/indices?v` 只输出数据行，**没有列头行**；但列顺序与 ES 相同，因此按位置解析仍然可用，按表头解析不可用；`_cat/indices/:index` 返回该索引的行，未知索引名返回 404 | `migration-from-es.html` | — |
| F-327 | ES 兼容层对不支持的调用返回结构化 `not_supported_yet` 错误，而不是 500 | `api-es-compat.html` | — |
| F-328 | `PUT /:index/_mapping` 只允许追加（additive only） | `api-es-compat.html` | — |
| F-329 | 相对 ES 的改善项：无堆调优；**11 MB 静态可执行文件 vs 620 MB 的 ES tarball**；一等公民的 explain plan（`/v1/explain-plan` 返回优化器树而非 profile dump）；列式摄入（写入时按列选编码）；向量维度上限 **16384**（ES 封顶 4096） | `migration-from-es.html` | ✅ 与 F-252 的 `max_dimensions` 默认 16384 一致 |
| F-330 | scroll 快照窗口上限是 **10,000** 文档 | `api-es-compat.html` | ✅ `es_compat.rs:41728` `SCROLL_SNAPSHOT_MAX_HITS: usize = 10_000`（issue #198） |
| F-331 | 超过上限的 scroll 请求返回 400 `illegal_argument_exception`，错误信息说明不会返回被静默截断的结果集，并建议改用 `search_after` | `api-es-compat.html` | ✅ 同上 |
| F-332 | 一条更宽松的路径：`POST /:index/_search_scroll` 别名**按索引**套用上限，因此逗号分隔的多索引 scroll 走这条路径可以从每个索引各快照整个上限（实测该路径返回 12,000 条命中跨 120 页）；但该路径上逐命中的 `_index` 不可靠（续页返回原始逗号分隔索引规格而非解析后的索引），因此 `(_index, _id)` 不是那里的唯一键（#405） | `api-es-compat.html` | — |
| F-333 | `_id` 是 keyword，因此**按字典序排序**——`"1000" < "999"`；对数字样式的 id 按 `_id` 升序翻页会在 `"10897"` 处结束而非 `"999"`，且不会报错，会静默截断（实测 11,450 条中只走了 1,010 条） | `api-es-compat.html` | — |
| F-334 | `search_after` 的游标是上一页最后一个命中的 `sort` 数组，需逐字回传，不得由页码推算 | `api-es-compat.html` | — |
| F-335 | 原生 REST API（端口 8080）在文档页上列出 **13** 个端点（F-335 所列为 `GET /v1/health`、`GET /v1/metrics`、`PUT/GET/DELETE /v1/indices/:name`、`POST /v1/indices/:name/docs`、`POST /v1/indices/:name/turbo-ingest`、`POST /v1/indices/:name/search`、`POST /v1/indices/:name/_explain`、`POST /v1/indices/:name/logs`、`POST /v1/indices/:name/syslog`、`POST /v1/indices/:name/otlp`、`GET /v1/indices/:name/_mapping`）；而 `xerj-api/src/router.rs` 实际注册 **31** 个 `/v1/` 路由模式，文档未列出的包括 `/v1/admin/backup`、`/v1/admin/flush`、`/v1/admin/slow_queries`、`/v1/admin/slow_queries/threshold/:ms`、`/v1/ask`、`/v1/cluster/health`、`/v1/dashboard/summary`、`/v1/embedding/identity`、`/v1/health/ready`、`/v1/indices`、`/v1/indices/:name/_flush`、`/v1/indices/:name/docs/:id`、`/v1/indices/:name/docs/_bulk`、`/v1/indices/:name/encodings`、`/v1/indices/:name/enrich`、`/v1/indices/:name/explain-plan`、`/v1/indices/:name/ingest`、`/v1/models`、`/v1/pipelines/:name`、`/v1/schema/:name`、`/v1/schema/:name/evolve`、`/v1/systemone` | `api-native.html` / 源码 | ✅ 路由模式脚本计数 = 31 |
| F-336 | explain 端点的真实路径是 **`POST /v1/indices/:name/explain-plan`**（路由注释为「返回查询执行计划而不执行它」）。官方站点上两处都不准确：原生 API 页写 `POST /v1/indices/:name/_explain`，迁移页写 `/v1/explain-plan`（缺 `/v1/indices/:name` 前缀） | `api-native.html` / `migration-from-es.html` / 源码 | ✅ `xerj-api/src/router.rs:166` |
| F-337 | `POST` 到显式 id 路径（`/{index}/_doc/{id}`）**不会索引**——显式 id 用 `PUT`，自动 id 用 `POST` | `agents/quickstart.html` | — |
| F-338 | `semantic_text` 字段的伴随嵌入落在 `<field>_vector` 字段，并且默认是 `_source` 的一部分——不过滤字段会让响应变大 | `agents/quickstart.html` | ✅ 与第一轮 F-086 一致 |

## P 组：智能体表面、Corpus Hub、Recipe 与 Playbook

| 编号 | 事实 | 页面 | 核验 |
|---|---|---|---|
| F-339 | For AI 页定义**七个规范智能体操作**：一个 CLI 子命令（`xerj autoindex`，无 HTTP 路由）+ 六个 HTTP 操作（`xerj_search`、`xerj_semantic_search`、`xerj_vector_search`、`xerj_hybrid_search`、`xerj_memory_store`、`xerj_memory_recall`） | `agents/index.html` | — |
| F-340 | 每个记忆命名空间是**物理隔离的索引**，因此智能体 A 永远读不到智能体 B 的记忆 | `agents/index.html` | — |
| F-341 | `GET /` 返回 ES 风格的信息文档，示例含 `"version":{"number":"8.13.0","lucene_version":"9.10.0"}` 与 `"tagline":"You Know, for Search"`——ES 客户端把它当握手，正是现成 ES 客户端库能直连 XERJ 的原因 | `agents/quickstart.html` | — |
| F-342 | Corpus Hub 有两条通道：Lane A 是参考语料清单 `tools/xerj-code/hub/<name>.json`（别人的源码，固定 commit）；Lane B 是记录包配方 `tools/packs/<name>/recipe.toml`（从多源蒸馏出的结构化记录） | `corpus-hub.html` | — |
| F-343 | 许可证审查有三种判定：`adapt-with-attribution`（Apache-2.0/MIT/BSD，改写时引 file:line）、`approach-only`（AGPL/SSPL/Elastic/BUSL/GPL，只读设计、自己写代码、绝不粘贴）、`mixed`（逐文件分档，需在 note 里指明边界） | `corpus-hub.html` | ✅ 与第一轮 F-196 的三档一致 |
| F-344 | 文档记载了一次自伤：项目自己的许可证检测器曾把 Elasticsearch 报成 Apache-2.0——因为 AGPL 文本里含有 "an \"Apache License 2.0\" compatible license" 这一句 | `corpus-hub.html` | — |
| F-345 | 贡献 PR 必须**从 `corpus-hub` 分支切出**（不是 main），以便 CI 工作流随 PR 一起进来 | `corpus-hub.html` | — |
| F-346 | CI 除同一份校验器外还跑两条注册表守卫：注册表路径下不得有超过 5 MB 的文件（构建产物包与密钥材料不得入库），`tools/packs/keys/` 下不得有私钥材料 | `corpus-hub.html` | — |
| F-347 | 构建出的包从不入库：维护者从配方构建，把签名的包挂到 GitHub Release，清单链接它——git 里的注册表只存配方与清单 | `corpus-hub.html` | ✅ 与第一轮 F-172、F-173 一致 |
| F-348 | 语料是否适合入 Hub 的两个判定问题都是实测式的：能否说清领域（"an agent working on ___ would query this for ___"），内容是否未被模型记住（公开热门库上检索是开销） | `corpus-hub.html` | ✅ 与第一轮 F-189 一致 |
| F-349 | Recipe 索引记录 flagship autoindex 的实测：1,995 文件 / 518 MB 语料上 80/81 项 ground-truth 检查通过，2,018,398 条记录存活、耗时 38.1 s，`kill -9` 后恢复到完全相同的计数 | `recipes/index.html` | ✅ 与第一轮 F-014 同源 |
| F-350 | Recipe 索引记录 passage retrieval 的实测：98% top-3 vs 汇总式的 32%——长文档以任一段落参与竞争（best-passage，max-sim 评分） | `recipes/index.html` | — |
| F-351 | Recipe 索引记录向量量化的实测：`scalar8` 下 recall@10 = 0.998 | `recipes/index.html` | — |
| F-352 | Recipe 索引记录 PDF/DOCX/HTML/MD/TXT 文件夹索引的实测：21/22 vs 公平 grep 基线的 14/22，决定性差距在 binary_only（6/7 vs 0/7），因为 grep 读不了 PDF/DOCX | `recipes/index.html` | — |
| F-353 | 文档站提供 5 个 Playbook：SIEM（日志分析，含 5 个检测查询）、日志分析、向量·RAG、全文检索、可观测性；每个都给出索引 schema、摄取命令、查询与仪表盘 | `playbooks/*.html` | — |
| F-354 | SIEM Playbook 的 5 个检测查询分别针对：Top 源 IP、异常父进程、DNS 隧道候选（正则 `[a-zA-Z0-9]{30,}\..*`）、横向移动（terms 动作 + cardinality 去重主机数）、基于 date_histogram 的尖峰检测 | `playbooks/siem.html` | — |
| F-355 | 可观测性 Playbook 用三个独立索引承载 metrics / traces / logs，OTLP 直入无需 collector；trace 通过 `trace_id` 关联日志 | `playbooks/observability.html` | — |
| F-356 | 全文检索 Playbook 展示了 `multi_match` 的字段加权（`"fields": ["title^3", "body"]`）、`match_phrase` 的 `slop`、`bool` 的 must + filter 组合，以及 terms + date_histogram 双层聚合 | `playbooks/full-text.html` | — |
| F-357 | 向量·RAG Playbook 指出 `hybrid` 是一个查询子句，因此放在 `query` 内部，且 `queries` 的每一项把自己的子句包在 `query` 里（`linear` 融合时的可选 `weight` 放在旁边） | `playbooks/vector-search.html` | ✅ 与 F-330 附近的写法一致 |

---

## Q 组：向量量化（补记，供洞察 10 引用）

| 编号 | 事实 | 页面 | 核验 |
|---|---|---|---|
| F-358 | 官方文档 `analyzers.html` 给出的 `standard` 描述（「Unicode 感知分词、小写化、英文停用词表」）与源码相反：源码的 `standard` **刻意不含停用词也不含词干**；文档的 `english` 描述（「standard + Porter2 词干 + 更大的停用词表」）也不是源码的构造方式——源码的 `english` 是**旧的** `standard` 管线（unicode 切分 + 小写化 + 英文停用词 + Snowball 词干），且词干实现是 `rust_stemmers` 的 Snowball 而非文档所称的 Porter2。源码的注释给出了改动理由：英文停用词会丢掉 "GET"，Snowball 词干会过度匹配 "static"/"statics"，两者都造成与 Elasticsearch 默认 `standard` 的语义偏离 | `analyzers.html` / `xerj-fts/src/analyzer.rs:1094-1126` | ✅ 源码注释逐字核对 |
| F-359 | `scalar8`（8 位/维）带来 1～2% 召回损失；文档明确它**换的是精度而不是内存**：扫描时从 `_source` 读全精度向量并按查询现量化，因此常驻内存不变；且 scalar8 的 `_score` 及其产生的排序依赖候选集（#392）。量化在服务端是唯一被读取的量化器 | `vectors.html` | ✅ 与 `config.html` 的 `default_quantization` 描述、`operations.html` 的容量规划三处一致 |
| F-360 | 量化在**映射层被遵守或被拒**（#275 已修）：`"scalar8"`（别名 `"int8"`）与 `"none"` 是本构建实现的值；`"binary"`、`"scalar4"`、`"int4"` 或拼写错误（如 `"sq8"`）在 `PUT /<index>` 与 `PUT /<index>/_mapping` 上返回 400 `mapper_parsing_exception`，指名该值与可接受集合，且**索引不会被创建**。#275 之前这些值返回 200、被 `GET /_mapping` 原样回显、然后被忽略——字段存全精度 f32，而读回的 mapping 却写着别的 | `vectors.html` | — |
| F-361 | `binary`（1 位/维）**未实现**：服务器在 `default_quantization = "binary"` 时拒绝启动，而不是静默按全精度存储同时宣称 32 倍节省；`scalar4` 根本不是该键接受的值——vector crate 里的 4 位量化器既不能从配置也不能从映射到达 | `vectors.html` / `config.html` | — |
| F-362 | 严格性被限制在 XERJ 自己的量化键上：Elasticsearch 的 `index_options.type` 保持宽松——`hnsw`、`flat`、`int4_*` 与 `bbq_*` 映射仍能创建，由精确 f32 扫描服务，因为**线兼容面上不能拒绝一个 ES 映射** | `vectors.html` | — |

---


本轮把文档站的每个可核数字回到 `engine/crates/` 与 `engine/` 复核，**四处不一致**：

| # | 不一致点 | 文档说法 | 代码事实 | 处置 |
|---|---|---|---|---|
| 1 | 查询类型数量 | 站点导航写 "32 variants"；同页正文列 50 个 | `SUPPORTED_QUERY_TYPES` = **50** | 以代码为准；正文正确、导航摘要错误（F-209、F-212） |
| 2 | 配置文件默认路径 | CLI 页用法摘要写 `--config` 默认 `./xerj.toml` | `main.rs:699` 只查 `--config` → `XERJ_CONFIG`，**无 `./xerj.toml` 回退** | 以代码与配置页为准（F-256、F-257） |
| 3 | 一致性用例总数 | 迁移页写 1,371 / 1,374（2026-09-20）；README 徽章写 1,366 / 1,369 | 两者都是**发布说明而非代码事实**；门禁不变量是「0 失败」 | 两者都记录，说明差异来源是快照时点（F-319、F-320） |
| 4 | explain 端点路径 | 原生 API 页写 `POST /v1/indices/:name/_explain`；迁移页写 `/v1/explain-plan` | 真实路由是 **`POST /v1/indices/:name/explain-plan`**（`router.rs:166`） | **以代码为准**；本轮已从「记录冲突」升级为「已裁决」（F-335、F-336） |
| 5 | **内置分析器清单（实质性错误）** | `analyzers.html` 写 4 个：`standard`/`whitespace`/`simple`/`english`；并把 `standard` 描述为含英文停用词、把 `english` 描述为「standard + Porter2 词干」 | 源码注册 **11** 个：`standard`/`english`/`whitespace`/`keyword`/`lowercase`/`stemmer`/`cjk`/`thai`/`icu_folding`/`ecommerce`/`code`。**`simple` 在整个 `engine/` 树中零次出现**；`standard` **不含**停用词与词干；`english` 是旧 `standard` 管线 | **以代码为准**；文档的 `simple` 不可用，且文档漏掉了 `ecommerce`（双向同义词）、`cjk`/`thai`/`icu_folding`（多语言）与 `code`（代码检索）（F-218、F-219、F-358） |
| 6 | **原生 API 覆盖面** | 原生 API 页以 13 个端点呈现 `/v1/*` 表面 | `router.rs` 实际注册 **31** 个 `/v1/` 路由模式 | 记录差异；文档页不是完整清单（F-335） |

此外记录两处**文档覆盖面缺口**（非错误，但影响评估）：

| # | 缺口 | 事实 |
|---|---|---|
| 5 | 文档键表不是全键面 | 代码有 24 个配置段，文档键表覆盖 12 段，default toml 交付 13 段；10 个键在 default toml 里却不在键表中（F-258、F-259） |
| 6 | 大量「接了线但没接线」的键 | 至少 16 个键被接受并校验，但行为不变，改离默认值只会在启动时打警告（F-260） |

## 相关参考

- [第一轮事实清单](facts.md)：F-001～F-206
- [官方文档站信源登记](docs-source.md)：本轮信源身份与页面清单
- [第二轮洞察](insights-docs.md)：洞察 7～12
- [References 索引](index.md)：本目录汇总
