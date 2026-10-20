---
type: Reference
title: XERJ 事实清单
description: XERJ 源码事实登记——按模块编号的事实清单（F-001 起），每条标注仓库相对路径与行号，零推测
tags: [xerj, 事实清单, rust, 源码事实]
generated: { by: source-code-to-okf-wiki/R, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-source
    resource: /references/source.md
    title: XERJ 源码快照登记
  - id: xerj-facts
    resource: /references/facts.md
    title: 本事实清单
---

# XERJ 事实清单

> 采集自 commit `51ff219276d7e55d9d85b4938e8b94f235f9d099`（`xerj-org/xerj`）。
> 每条事实标注仓库相对路径与行号，不含推断性表述；数量类事实由脚本计数（口径见 [source.md](source.md)）。
> 快照登记与计数口径见 [source.md](source.md)。

## A 组：定位、规模与许可

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | 仓库上游为 `xerj-org/xerj`，本地快照位于工作区 `external/dao/search/xerj`，采集时工作树无未提交改动 | `git remote -v` / `git status --porcelain` |
| F-002 | `engine/crates/` 下有 18 个 crate | 脚本计数 |
| F-003 | `engine/` 下共有 552 个 Rust 源文件 | 脚本计数 |
| F-004 | `engine/` 下 Rust 代码行数合计 521,684 行 | 脚本计数 |
| F-005 | 许可证为 Apache License 2.0；`NOTICE` 标注 "XERJ / Copyright 2026 The XERJ Authors" | `LICENSE:1-3`、`NOTICE:1-2` |
| F-006 | `docs/ARCHITECTURE.md` 将 XERJ 描述为 "an AI-native search, vector, and log-analytics engine written from scratch in Rust and published under Apache-2.0" | `docs/ARCHITECTURE.md:9-12` |
| F-007 | `docs/ARCHITECTURE.md` 记录 "an independent implementation that shares no code and no architecture with Elasticsearch or Lucene" | `docs/ARCHITECTURE.md:12-15` |
| F-008 | `docs/ARCHITECTURE.md` 记录 "speaks the Elasticsearch 8.x HTTP protocol as a zero-migration adoption bridge" | `docs/ARCHITECTURE.md:13-16` |
| F-009 | `README.md` 记录 "XERJ is compatible with the API. It is not a reimplementation of Elasticsearch internals, and it is not a fork." | `README.md:396-397` |
| F-010 | `docs/WHY_XERJ.md` 把 ES 兼容类比为 CockroachDB / Neon 讲 Postgres 协议 | `docs/WHY_XERJ.md:5-9` |
| F-011 | `docs/WHY_XERJ.md` 列出 AI 智能体相对经典搜索引擎的三类问题：Onboarding、Orientation、Continuity | `docs/WHY_XERJ.md:13-19` |
| F-012 | `landing/llms.txt` 声明 "ES wire compatibility is the transport, not the product." | `landing/llms.txt:3` |
| F-013 | `docs/WHY_XERJ.md` 记录单一静态二进制 61.6 MB（含神经嵌入后端），`--no-default-features` 精简版 58.2 MB，神经后端占 3.4 MB | `docs/WHY_XERJ.md:44-46` |
| F-014 | `docs/WHY_XERJ.md` 记录 autoindex 流水线经对抗验证：1,995 文件的密文清单语料上 80/81 项 ground-truth 检查通过 | `docs/WHY_XERJ.md:40-42` |
| F-015 | `docs/WHY_XERJ.md` 记录持久性验证：ack 删除在 SIGTERM/SIGKILL 重启后存活（11/11 随机崩溃时序格），合并不具备静默丢文档的结构性能力（loss firewall） | `docs/WHY_XERJ.md:50-52` |

## B 组：crate 架构与运行形态

| 编号 | 事实 | 来源 |
|---|---|---|
| F-016 | `docs/ARCHITECTURE.md` 的 crate 职责表共 16 行（15 个 crate + `tests/es-compat-yaml` 测试 harness）；`xerj-hub` 与 `xerj-mcp` 未列入该表 | `docs/ARCHITECTURE.md:48-65` |
| F-017 | 横切支撑 crate 为 `xerj-common`（共享 `Config`/`Schema`/`FieldType`/`XerjError`）、`xerj-ai`（分块、嵌入代理、记忆存储）、`xerj-cluster`（内嵌 Raft 集群元数据）、`xerj-wasm`（转换管线插件） | `docs/ARCHITECTURE.md:41-44` |
| F-018 | 服务器入口启动三个并发 TCP 监听：原生 REST 默认 :8080、ES 兼容默认 :9200、gRPC 默认 :8081（XerjSearch 服务，明文 h2c） | `engine/crates/xerj-server/src/main.rs:5-10` |
| F-019 | 服务器在 SIGTERM 或 SIGINT 上优雅关闭 | `engine/crates/xerj-server/src/main.rs:11` |
| F-020 | `xerj-server` 提供 `index` 子命令，直接把 NDJSON 文件摄入引擎，绕过 axum/hyper/tokio 请求调度与 bulk 响应序列化 | `engine/crates/xerj-server/src/main.rs:13-22` |
| F-021 | `xerj-server` 在非 MSVC 目标上使用 jemalloc 作为全局分配器 | `engine/crates/xerj-server/src/main.rs:30-32` |
| F-022 | Linux 下的 jemalloc 运行参数为 `background_thread:true,dirty_decay_ms:1000,muzzy_decay_ms:1000`（符号名 `_rjem_malloc_conf`） | `engine/crates/xerj-server/src/main.rs:47-54` |
| F-023 | 该配置的测量依据：6,200 万条记录批量装载下，匿名 RSS 每摄入一条文档增长约 4–5 KB（15.5M 文档时 83 GB），直至被内核 OOM 杀死；开启后台线程后工作集 RSS 持平 | `engine/crates/xerj-server/src/main.rs:40-46` |
| F-024 | 顶层子命令共 14 个字符串标识：`index`、`search`、`def`、`init`、`gain`、`autoindex`、`brain`、`share`、`feedback`、`code`、`corpus`、`hub`、`ask`、`mcp`（另有一处 `xerj_autoindex::extract::xls::WORKER_ARG` 内部工作器参数） | `engine/crates/xerj-server/src/main.rs:126-145` |
| F-025 | 顶层子命令在服务器标志解析器之前分派；写在子命令之前的标志会被移到子命令之后（`xerj --url URL corpus …`） | `engine/crates/xerj-server/src/main.rs:124-125` |
| F-026 | `flag_value()` 把"以 `--flag` 结尾且无值"视为错误而非静默未设置（`xerj --insecure --data-dir` 过去会启动在默认数据目录） | `engine/crates/xerj-server/src/main.rs:155-163` |

## C 组：autoindex 零配置摄取流水线

| 编号 | 事实 | 来源 |
|---|---|---|
| F-027 | `xerj-autoindex` 是纯 ES 兼容 HTTP 客户端特性，不链接 `xerj-engine`，可对任意端点工作 | `engine/crates/xerj-autoindex/src/lib.rs:1-4` |
| F-028 | 格式识别基于内容，代码注释明确 "Content-based format detection. NEVER trusts file extensions."；顺序为 magic bytes → 二进制检查 → 文本启发式（json/jsonl → html/xml → logs → sql dump → csv → yaml → txt） | `engine/crates/xerj-autoindex/src/sniff.rs:1-4` |
| F-029 | `sniff::Family` 枚举共 28 个变体：Jsonl、Json、Csv、Logs、Xml、Html、Yaml、TxtProse、TxtLines、Pdf、Eml、Mbox、Docx、Pptx、Xlsx、Xls、Doc、Epub、Ipynb、Man、Sqlite、SqlDump、Code、UnityYaml、UnityMeta、Bvh、Stub、Binary | `engine/crates/xerj-autoindex/src/sniff.rs:11-80` |
| F-030 | `extract/` 下共 25 个抽取器模块：bvh、code、csv_x、doc、docx、eml、epub、html、ipynb、json、jsonl、logs、man、mbox、opc、pdf、pptx、sqldump、sqlite_x、txt、unity、xls、xlsx、xml_x、yaml_x | `engine/crates/xerj-autoindex/src/extract/mod.rs:5-29` |
| F-031 | 每个抽取器都是有界内存且从不死 Fatal：解析失败按 family → txt → junk-with-metadata 降级并计数 | `engine/crates/xerj-autoindex/src/extract/mod.rs:1-3` |
| F-032 | `RawRecord` 结构含 `fields`、`locator`（内容位置定位符，幂等 `_id` 的成分）、`group`（文件内子数据集组）、`origin` | `engine/crates/xerj-autoindex/src/extract/mod.rs:63-74` |
| F-033 | `FieldOrigin` 枚举区分 `Data`（字段名读自文件本身）与 `Extractor`（字段名由抽取器发明）；数据集聚类只用前者作键 | `engine/crates/xerj-autoindex/src/extract/mod.rs:38-59` |
| F-034 | `FieldOrigin` 的注释记录：提取器发明的字段名若进入聚类键，提取器变更会静默把文件移到另一个索引并孤立已写入的文档（issue #178） | `engine/crates/xerj-autoindex/src/extract/mod.rs:38-48` |
| F-035 | 常量 `MAX_LINE = 16 << 20`（16 MB 单行上限），`MAX_WHOLE_FILE = 64 << 20`（64 MB 整文件解析上限） | `engine/crates/xerj-autoindex/src/extract/mod.rs:89-90` |
| F-036 | 常量 `SECTION_CHARS = 2 << 10`（2 KB 目标字符/文档段）；原值 32 KB 被判为存储粒度而非检索粒度 | `engine/crates/xerj-autoindex/src/extract/mod.rs:91-102` |
| F-037 | 32 KB 段的实测记录：460 次提交的历史文件产生 25 个文档覆盖 15,407 行，相关提交不可检索；2 KB 段加段落重叠后可检索 | `engine/crates/xerj-autoindex/src/extract/mod.rs:95-98` |
| F-038 | 常量 `MAX_RECORDS_PER_FILE = 4 << 10`（4096 条/文件上限），截断经 `ExtractStats.truncated` 上报 | `engine/crates/xerj-autoindex/src/extract/mod.rs:104-114` |
| F-039 | 常量 `SECTION_OVERLAP = 200`（上一段末尾 200 字符在下一段开头重复） | `engine/crates/xerj-autoindex/src/extract/mod.rs:116-118` |
| F-040 | `open_reader()` 用 `flate2::read::MultiGzDecoder` 处理 gzip，缓冲区 256 KB，返回的 reader 实现 `Send` | `engine/crates/xerj-autoindex/src/extract/mod.rs:120-136` |
| F-041 | 默认路径阶段序列为：walk、hash、scan、prepare、graph、index、graph-corpus、finalize-refresh、finalize-count、finalize-correlate、finalize-histogram、finalize-catalog | `engine/crates/xerj-autoindex/src/cli.rs:531-533` |
| F-042 | `--no-graph` 路径阶段序列为：walk、hash、scan、prepare、snapshot、index、finalize-catalog、finalize-refresh、finalize-verify | `engine/crates/xerj-autoindex/src/cli.rs:534-538` |
| F-043 | 恢复运行从 `replay` 阶段开始，其 `index` 阶段只统计尚待应用的写入操作 | `engine/crates/xerj-autoindex/src/cli.rs:539-540` |
| F-044 | `EXIT_NEEDS_DECISION = 4`，与通用失败码 1 区分 | `engine/crates/xerj-autoindex/src/gate.rs:42-44` |
| F-045 | `DEFAULT_MAX_MINUTES = 10` | `engine/crates/xerj-autoindex/src/gate.rs:46-48` |
| F-046 | `Approval` 枚举为 `Proceed` / `Fast` / `Cancel`；`Approval::parse` 显式拒绝 `narrower` | `engine/crates/xerj-autoindex/src/gate.rs:50-58`、`76-88` |
| F-047 | 决策门只在三项条件同时成立时才在终端提示：stdin 是终端、stderr 是终端、进度输出未被静默 | `engine/crates/xerj-autoindex/src/cli.rs:555-562` |
| F-048 | 未提示的运行行为一致：JSON 决策请求写到 stdout（`--quiet` 不静默 stdout），进程退出码 4，载荷含 `prompt_not_offered_because` 字段说明缺哪一项 | `engine/crates/xerj-autoindex/src/cli.rs:556-563` |
| F-049 | 估算区间只覆盖客户端侧抽取，不含服务端索引、嵌入与网络时间；阶段 A 从未完整读取的格式族被排除在算式外而非按其他族的速率计价 | `engine/crates/xerj-autoindex/src/cli.rs:543-550` |
| F-050 | 退出码语义：`0` 完成、`3` 完成但含 junk（属成功）、`2` 用法错误、`1` 任何错误、`4` 需要决策 | `AGENTS.md`（退出码段） |
| F-051 | 退出码 3 携带 `reason=catalog-alias-sweep-failed`（语料已索引，仅目录去重清理未完成）或 `datasets_refused=N files_refused=M` | `AGENTS.md`（退出码段） |
| F-052 | `indexed_vs_submitted_line()` 在"目录已存活但本次未提交任何记录"时追加 "(already indexed; nothing new to send)" | `engine/crates/xerj-autoindex/src/lib.rs:97-105` |
| F-053 | `ingest_docs_per_sec()` 以本次提交的文档数为分子、耗时为分母，零提交时返回 0 | `engine/crates/xerj-autoindex/src/lib.rs:83-89` |
| F-054 | `next_hint()` 在打印后续命令时把密钥渲染为 `$XERJ_API_KEY` 或 `$(cat <path>)` 表达式，不直接回显管理员密钥 | `engine/crates/xerj-autoindex/src/lib.rs:129-150` |
| F-055 | 索引名格式为 `<prefix>-<dataset-slug>`，`--prefix` 默认 `ax` | `landing/llms.txt:26` |
| F-056 | `--dry-run` 走完遍历、嗅探与采样，不写入任何索引 | `AGENTS.md`（"Running an index on someone's machine"） |
| F-057 | 数据目录必须放在将被索引的目录之外；`data/` 不在内置忽略列表中 | `landing/llms.txt:20` |

## D 组：MCP 智能体接口

| 编号 | 事实 | 来源 |
|---|---|---|
| F-058 | `xerj-mcp` 同时是库与独立二进制；主 `xerj` 二进制的 `xerj mcp` 子命令调用库入口 `run` | `engine/crates/xerj-mcp/src/lib.rs:1-8` |
| F-059 | 传输为 MCP stdio：stdin/stdout 上的换行分隔 JSON-RPC 2.0 消息 | `engine/crates/xerj-mcp/src/lib.rs:9-12` |
| F-060 | crate 文档记录该进程暴露 **17 个**工具：14 个无需 hub 密钥，3 个 Corpus Hub 工具（`xerj_hub_*`） | `engine/crates/xerj-mcp/src/lib.rs:12-20` |
| F-061 | 14 个无 hub 密钥的工具中，13 个构造引擎已接受的请求并转发 | `engine/crates/xerj-mcp/src/lib.rs:14-16` |
| F-062 | 单元测试函数名为 `tools_list_has_all_seventeen` | `engine/crates/xerj-mcp/src/lib.rs:3612` |
| F-063 | 已发布 schema 文件 `landing/docs/agents/schemas/mcp-tools.json` 的 `tools[]` 长度为 17 | 脚本计数（`tools` 数组） |
| F-064 | 17 个工具名为：`xerj_search`、`xerj_semantic_search`、`xerj_vector_search`、`xerj_hybrid_search`、`xerj_memory_store`、`xerj_memory_recall`、`xerj_brain_ego`、`xerj_brain_link`、`xerj_brain_unlink`、`xerj_brain_overview`、`xerj_map`、`xerj_code_search`、`xerj_plan`、`xerj_field_report`、`xerj_hub_find`、`xerj_hub_def`、`xerj_hub_ask` | `engine/crates/xerj-mcp/src/lib.rs:701-1163`、`src/hub.rs:52-105` |
| F-065 | 认证优先级为 `--auth` > `XERJ_AUTH` > （仅回环地址时）本地 `admin.key` 发现 | `engine/crates/xerj-mcp/src/lib.rs:250-272` |
| F-066 | 回环守卫：本地密钥发现对非回环 URL 不触发 | `engine/crates/xerj-mcp/src/lib.rs:263-265` |
| F-067 | 回环回退的存在理由：`xerj init` 有意不把凭据写进项目作用域的 `.mcp.json`，否则官方一键设置会对每个工具调用返回 401（#961） | `engine/crates/xerj-mcp/src/lib.rs:234-240` |
| F-068 | `DEFAULT_PROTOCOL_VERSION = "2025-06-18"`，`DEFAULT_XERJ_URL = "http://localhost:9200"` | `engine/crates/xerj-mcp/src/lib.rs:106-109` |
| F-069 | 五个检索工具接受 `max_tokens` 并被强制执行：响应文本绝不超预算，用 XERJ 的 `StandardTokenizer`（UAX #29 分词）计数，重叠的 file:line 段落先去重再计预算，超预算命中降级为定位符 | `engine/crates/xerj-mcp/src/lib.rs:89-95` |
| F-070 | `hub_tools_served()` 在未配置 hub 签名密钥时从 `tools/list` 与帮助文本中省略 `xerj_hub_*` 工具 | `engine/crates/xerj-mcp/src/lib.rs:184-190` |
| F-071 | 帮助文本的工具数量与名单取自 `tool_specs()`，与 `tools/list` 返回同一列表 | `engine/crates/xerj-mcp/src/lib.rs:192-196` |
| F-072 | stdout 专用于 JSON-RPC 流，诊断信息走 stderr；未显式给定 auth 且解析到磁盘上的密钥时，密钥文件路径在 stderr 公布 | `engine/crates/xerj-mcp/src/lib.rs:86-87`、`350-355` |
| F-073 | 未知参数直接报错退出（"unknown argument … — see `xerj mcp --help`"），不留静默忽略 | `engine/crates/xerj-mcp/src/lib.rs:313-318` |
| F-074 | JSON-RPC 批量数组与单对象都支持（2024-11-05 用批量，2025-06-18 放弃批量） | `engine/crates/xerj-mcp/src/lib.rs:376-378` |
| F-075 | `xerj_plan` 对应 `POST /_ask`，是确定性规则规划器而非 LLM | `engine/crates/xerj-mcp/src/lib.rs:36` |
| F-076 | `xerj_brain_*` 系列工具操作的是链接索引而非图数据库：确定性词法检测 + 显式断言，无神经理解、无查询语言、无无界遍历 | `engine/crates/xerj-mcp/src/lib.rs:57-61` |
| F-077 | `xerj_field_report` 默认发送：先开 GitHub PR，GitHub 不可用时 POST 到 `https://xerj.org/api/field-report`；`confirm: false` 预览，`--disable-feedback` / `XERJ_DISABLE_FEEDBACK=true` 关闭 | `engine/crates/xerj-mcp/src/lib.rs:16-20` |

## E 组：检索路径、查询与响应裁剪

| 编号 | 事实 | 来源 |
|---|---|---|
| F-078 | 搜索请求依次经过 `xerj-api`（Axum handler）→ `xerj-query`（`parse_request()` 把 ES JSON 解析为 `SearchRequest`/`QueryNode` 树）→ `xerj-engine`（`Engine::get_index()` → `Index::search()`） | `docs/ARCHITECTURE.md:69-83` |
| F-079 | 查询同时匹配内存 memtable 与磁盘 segment，结果合并使新写入文档立即可检索 | `docs/ARCHITECTURE.md:85-87` |
| F-080 | `size > 0` 的命中物化上界为前 `from + size` 个候选 | `docs/ARCHITECTURE.md:87-89` |
| F-081 | 聚合管线在 `size:0` 时走列式快速路径 | `docs/ARCHITECTURE.md:79-80` |
| F-082 | 写入路径为 API → `IndexStore`：WAL 追加（分片 `Mutex<WalWriter>` + 全局 `AtomicU64` seq_no）→ 存储 memtable（向上取整到 2 的幂的哈希分区）→ FTS memtable（`engine.ingest_shards` 哈希分区）→ flush 为不可变 segment → 后台合并 | `docs/ARCHITECTURE.md:92-108` |
| F-083 | `engine.ingest_shards` 被校验为非零且不超过 256 的 2 的幂 | `docs/ARCHITECTURE.md:110-112` |
| F-084 | WAL writer 分片数与向上取整后的存储 memtable 分区数属于不同域，不承诺一一对应；FTS memtable 又是独立的一层 | `docs/ARCHITECTURE.md:113-123` |
| F-085 | 重启时 `Engine::new()` 扫描数据目录，对每个索引目录调 `Index::open()`：`IndexStore::open()` 重放 WAL 进存储 memtable，`WalReader::replay()` 从 WAL 重建 FTS memtable，`doc_count = segments + memtable` | `docs/ARCHITECTURE.md:125-135` |
| F-086 | 默认 `_search` 省略 `<field>_vector` 与 `<field>_vector_chunks` 伴随字段；需要向量时须显式 `"_source": true` | `landing/llms.txt:70` |
| F-087 | 默认 `_search` 返回完整文档；实测 5 个命中覆盖索引后的源码文件 = 416,630 字节，加 `"fields":["_passage"]` 并投影 `_source` 后为 12,122 字节（34 倍缩减） | `landing/llms.txt:71` |
| F-088 | `_passage` 伪字段返回 `{field,ordinal,start_offset,end_offset,text,page?}`，从原始字段切片 | `landing/llms.txt:71` |
| F-089 | `_passage` 在任何 `_mapping` 与默认响应中都不出现；当 `_source` 未投影且未请求 `_passage` 时，响应会带一条就绪的修正请求提示 | `landing/llms.txt:71` |
| F-090 | `fields_request_includes_passage()` 判定请求字段是否含 `_passage` | `engine/crates/xerj-api/src/es_compat.rs:8050-8066` |
| F-091 | `_xerj.hints` 是追加式提示结构，不落在 `hits`/`total`/`_score` 内，因此不影响既有 ES 客户端 | `landing/llms.txt:71` |
| F-092 | 在 `ax-*`（autoindex 创建）索引上，未映射字段的查找返回 400 并报出字段名与可检索字段；ES 自身行为是 0 命中 | `landing/llms.txt:65` |
| F-093 | 严格模式可按请求（`?strict_unknown_fields=true`）或按索引（`index.query.strict_unknown_fields=true`）开启；`exists` 查询在未映射字段上仍返回真实的 0 命中 | `landing/llms.txt:65` |
| F-094 | 混合融合只支持 `rrf`（默认，k=60）与 `linear`；`fusion:"learned"` 未实现并显式报错 400 | `landing/llms.txt:64` |
| F-095 | `rerank` 是唯一在搜索期把文档文本发往外部的搜索期特性：默认最多 30 条（上限 300）命中的文本发往第三方相关性评判服务，返回 0–1 概率取代 `_score` | `landing/llms.txt:63` |
| F-096 | `rerank` 失败策略为"超时降级、契约违约上报"：提供方慢则返回 HTTP 200 + 引擎原序 + `_rerank.applied:false`；无密钥 503、已禁用 403、密钥被拒/体畸形/不可达 502，均带 `rerank_exception` 且无命中 | `landing/llms.txt:63` |
| F-097 | `rerank` 与 `sort`、`search_after`、`collapse`、scroll（打开与续取）、`size:0`、`_msearch`、搜索模板、`_async_search`、原生 `/v1` 搜索 API 与 gRPC 同时使用时被拒绝（400） | `landing/llms.txt:63` |
| F-098 | `rerank` 需要运维方配置的提供方密钥（`[rerank] api_key` 或 `TYPESAFE_API_KEY`），请求内不能传递；`[rerank] enabled = false` 完全禁止 | `landing/llms.txt:63` |
| F-099 | 另有两个特性在开启时会外发文本，且默认关闭：`[embedding] default_endpoint` / `--embed-mode proxy`，以及 WAL tap（`PUT /_xerj/wal_tap`） | `landing/llms.txt:63`、`72` |
| F-100 | 服务端按已索引文档数保留堆：三个 per-segment 缓存（`stored_value_cache`、`dv_cache`、`id_pos_cache`）在合并回收其 segment 之前无上限 | `landing/llms.txt:72` |
| F-101 | 观测数据点：2026-09 一次 lexical 模式节点在大规模多仓库代码语料中途常驻 20.2 GB | `landing/llms.txt:73` |
| F-102 | 源码文件经 tree-sitter 解析并做 AST 感知索引（符号 + 全文），Lucene 检出（6,113 个源文件、51 MB）单线程进程内抽取约 1,500 files/s（13 MB/s），tree-sitter 解析占其中约 72% | `README.md:415-419` |
| F-103 | 重建索引是增量的：内容与上次索引代际逐字节相同的文件跳过解析并沿用已提交结果；全量内容哈希仍会运行以检测变更，故总耗时下限是哈希而非解析 | `README.md:425-429` |
| F-104 | 抽取吞吐基准可用 `XERJ_EXTRACT_BENCH=/path/to/repo cargo test -p xerj-autoindex --release extract_bench -- --nocapture --ignored` 复现 | `README.md:421-423` |

## F 组：向量、嵌入与混合检索

| 编号 | 事实 | 来源 |
|---|---|---|
| F-105 | `Embedder` 后端有四个：词法（内置）、代理（外部 OpenAI 兼容 `/v1/embeddings`）、神经（内置 BERT，candle 进程内，`neural` feature）、ONNX（实验性，`onnx-experimental` feature，惰性加载） | `engine/crates/xerj-ai/src/embedder.rs:3-22` |
| F-106 | 查询路径会用写入时所用的同一后端自动嵌入 `semantic_text` 字段，使摄入与查询向量同源 | `engine/crates/xerj-ai/src/embedder.rs:22-26` |
| F-107 | `Embedder::is_active` 区分神经/代理/ONNX 后端与词法回退 | `engine/crates/xerj-ai/src/embedder.rs:23-25` |
| F-108 | 内置词法嵌入器 `DEFAULT_DIMS = 384` | `engine/crates/xerj-ai/src/local.rs:25-29` |
| F-109 | 哈希函数为 64 位 FNV-1a（初值 `0xcbf29ce484222325`，质数 `0x00000100000001b3`） | `engine/crates/xerj-ai/src/local.rs:31-40` |
| F-110 | 采用有符号哈希：低位选桶，1 个高位比特选符号，以降低无符号特征哈希的碰撞偏置 | `engine/crates/xerj-ai/src/local.rs:42-55` |
| F-111 | 特征构成：整词一元组权重 1.0；词内字符三元组（以 `#` 补边）权重 0.35 | `engine/crates/xerj-ai/src/local.rs:70-97` |
| F-112 | 累加器整体做 L2 归一化，使余弦相似度与文本长度无关 | `engine/crates/xerj-ai/src/local.rs:99-100` |
| F-113 | 源码注释明确该嵌入器 "is **not** a neural model — it captures lexical / sub-word overlap, not deep semantics" | `engine/crates/xerj-ai/src/local.rs:10-13` |
| F-114 | 空文本或 `dims == 0` 产生全零向量，余弦相似度按 0 处理 | `engine/crates/xerj-ai/src/local.rs:57-62` |
| F-115 | 默认嵌入模式为词法；`--embed-mode neural` 启用内置 all-MiniLM-L6-v2 BERT 编码器，模型（约 90 MB）首次使用时自动下载 | `landing/llms.txt:66` |
| F-116 | `--embed-mode` 是服务器启动标志且在**摄入时**生效：文档写入时在用的模式就是该文档保留的模式；词法切神经不会重新嵌入已索引内容 | `landing/llms.txt:67` |
| F-117 | 神经模型文件（`config.json`、`tokenizer.json`、`model.safetensors`）经 HTTPS 从 HuggingFace Hub（`sentence-transformers/all-MiniLM-L6-v2`）下载到 `~/.cache/huggingface`；XERJ 自身不为其固定校验和 | `landing/llms.txt:68` |
| F-118 | 空气隔离部署可预先下载三个文件并把 `embedding.local_model_dir` 指向该目录，届时不再发生任何下载 | `landing/llms.txt:68` |
| F-119 | HNSW 参数：每层每节点最大双向连接数 `m = 16`，构建期动态候选表大小 `ef_construction = 200`，层选择用标准 ln 公式，邻居选择用论文 Algorithm 4 多样性启发式（hnswlib 与 Lucene 使用的变体） | `engine/crates/xerj-vector/src/hnsw.rs:6-12`、`134-143` |
| F-120 | HNSW 图完全驻内存，持久化由 storage crate 负责 | `engine/crates/xerj-vector/src/hnsw.rs:13-14` |
| F-121 | 2026-07-12 的 flat-slab 重构：节点存于单一 slot 索引的连续 slab（一个 `Vec<f32>` 存向量、`Vec<Vec<u32>>` 存各层邻居表、`Vec<u64>` 位图存搜索期访问集）；此前 `HashMap<u64, Arc<RwLock<Node>>>` 布局使 beam search 约为距离计算本身的 5 倍慢 | `engine/crates/xerj-vector/src/hnsw.rs:15-22` |
| F-122 | HNSW 磁盘格式：魔数 `XHNS0001`，格式版本 2（v1 为初版；v2 增加尾部 tombstone 块） | `engine/crates/xerj-vector/src/hnsw.rs:41-51` |
| F-123 | 未过滤 kNN 在全精度余弦字段且文档数 ≥ 1,024 时走持久化 HNSW 图的 beam search 并对其候选精确重打分；`num_candidates` 是 beam 宽度（下限 800，缺省时套用 ES 的 1.5×k） | `landing/llms.txt:62` |
| F-124 | ANN 路径召回率是**实测值**：50k×128 维基准语料上官方基准查询 recall@10 为 1.00，100 探针均值 0.976 / 最小 0.90（同协议下 ES 8.13.4 为 0.937 / 0.70） | `landing/llms.txt:62` |
| F-125 | 走精确暴力扫描的形态：过滤或嵌套 kNN、非余弦相似度、SQ8 量化字段、文档数少于 1,024 的索引、图过期，以及 `semantic` 与 `/_memory` 召回 | `landing/llms.txt:62` |
| F-126 | ANN 路径可能返回少于 k 条命中 | `landing/llms.txt:62` |

## G 组：智能体记忆、第二大脑与规划器

| 编号 | 事实 | 来源 |
|---|---|---|
| F-127 | 记忆写入端点 `POST /_memory/{namespace}`，正文含 `text`、`metadata`、可选 `id`、可选 `vector`、可选 `dedup` 与 `dedup_threshold`；文本自动嵌入，命名空间互相隔离 | `landing/llms.txt:82` |
| F-128 | 召回端点 `POST /_memory/{namespace}/_recall`，正文含 `query`、`semantic`、`k`、可选 `filter`、可选 `recency_weight` | `landing/llms.txt:83` |
| F-129 | 召回模式按序为：显式 `vector` kNN → `hybrid:true`（BM25 + 服务端语义，按倒数排名融合）→ `semantic:true`（服务端嵌入）→ 纯 `query` 文本（BM25） | `landing/llms.txt:83` |
| F-130 | `POST /_ask` 输入 `{index, prompt}`，输出 `{query, plan[], confidence, indices[]}`；输出的 `query` 可直接放进 `_search` 正文 | `landing/llms.txt:98` |
| F-131 | `/_ask` 是确定性规则引擎而非 LLM；无法在索引中落地的短语返回 422 并指名该短语，不猜测 | `landing/llms.txt:98` |
| F-132 | `/_ask` 返回的每个查询都已通过节点自身的解析器 | `landing/llms.txt:98` |
| F-133 | 第二大脑不是图数据库：没有查询语言、没有最短路径、没有 PageRank、没有无界遍历；边是普通 XERJ 文档，每次调用最多两跳 | `docs/SECOND_BRAIN.md:3-6` |
| F-134 | 一个脑由一个名字加两个保留索引派生：边索引 `.xerj-memory-{brain}-edges`、默认节点索引 `.xerj-memory-{brain}` | `docs/SECOND_BRAIN.md:15-21` |
| F-135 | 保留前缀 `.xerj-memory-` 与智能体记忆 API 使用的命名空间相同，故脑的默认节点索引即同名记忆命名空间 | `docs/SECOND_BRAIN.md:22-25` |
| F-136 | 边文档映射含 `edge_id`/`src`/`dst`/`type`/`detector`/`src_file`/`src_format`/`dst_format`（keyword）、`weight`/`confidence`（float）、`valid_at`/`invalid_at`/`created_at`/`expired_at`（date，epoch_millis）、`schema_version`（integer）、`evidence.quote`（text）、`evidence.source`（keyword）、`evidence.offset`（long） | `docs/SECOND_BRAIN.md:39-47` |
| F-137 | 边文档 `_id` 由 `edge_id = xxh3_128("xg1\0" src "\0" type "\0" dst "\0" decimal(valid_at_ms))` 渲染为 32 位小写十六进制 | `engine/crates/xerj-autoindex/src/detect/mod.rs:47-61` |
| F-138 | 边被软失效而非删除，因此"上周二它相信什么"仍可回答 | `engine/crates/xerj-autoindex/src/detect/mod.rs:14-17` |
| F-139 | 检测器注册表 `default_detectors()` 返回 9 个检测器：wikilink、mdlink、href、pathcite、cratecite、sequence、samedir、sharedterm、emailthread | `engine/crates/xerj-autoindex/src/detect/mod.rs:428-442` |
| F-140 | 检测器标签为 `wikilink@2`、`mdlink@2`、`href@2`、`pathcite@1`、`cratecite@1`、`sequence@2`、`samedir@2`、`sharedterm@1`、`email-thread@1` | `engine/crates/xerj-autoindex/src/detect/*.rs`（各 `TAG` 常量） |
| F-141 | 检测是确定性而非 LLM 过程：同一语料在 mtime 不变时必须产出逐字节相同的边集，因为边身份（进而幂等重跑、kill -9 安全、双时态历史）挂在 `(src, type, dst, valid_at)` 的内容哈希上 | `engine/crates/xerj-autoindex/src/detect/mod.rs:5-12` |
| F-142 | `emailthread` 一个检测器对应两种边类型（`replies_to` 与 `attachment_of`），二者一起版本化 | `engine/crates/xerj-autoindex/src/detect/mod.rs:457-459` |
| F-143 | 边模式版本常量 `EDGE_SCHEMA_VERSION = 1`；脑元文档保留 `_id` 为 `__xerj-brain-meta` | `engine/crates/xerj-autoindex/src/detect/mod.rs:39-45` |
| F-144 | 脑名校验：非空、长度 ≤ 200、首字符为小写字母或数字、其余字符限于 `a-z 0-9 _ - .`、不含 `..`、不得以 `-edges` 结尾 | `engine/crates/xerj-autoindex/src/detect/mod.rs:67-73` |
| F-145 | 决策接口 `POST /v1/systemone`（原生 REST 端口 `--port + 1`）与 `POST /_decide`（ES 兼容端口）返回类型化判断，答案由带标签历史索引上的加权投票在本地给出 | `landing/llms.txt:94` |
| F-146 | `model` 字段回显 `xerj-history-vote-1`，不是 Jev 模型名；零标注支持的问题是 422 并指名 ids，不伪造 0.5 | `landing/llms.txt:94` |
| F-147 | AG News（12 万条带标签样本）上测得 0.9182 准确率，覆盖全部 7,600 条测试项，`/v1/systemone` 每项 p50 42.7 ms | `landing/llms.txt:94` |
| F-148 | `/_decide` 返回证据：带标签的邻居、引擎分数、权重 | `landing/llms.txt:94` |

## H 组：ES 兼容、基准与运营边界

| 编号 | 事实 | 来源 |
|---|---|---|
| F-149 | 一致性套件在每次提交上运行，当前通过 1366/1369 个用例；套件位于 `engine/tests/es-compat-yaml` | `README.md:394-396` |
| F-150 | ES 兼容性 YAML 套件目录 15 个（aggregations、bulk、ccr、cluster、delete_by_query、indices、ingest、ml、reindex、scroll、search、security、smoke、update_by_query、vectors），用例文件 221 个 | 脚本计数 |
| F-151 | 硬门禁为零失败：通过与跳过的总数会随上游套件变化，判定应基于失败数而非固定总数 | `AGENTS.md`（"The hard gate"） |
| F-152 | 兼容实现的表面：indices、documents、bulk、search、aggregations、mappings、kNN、scroll、reindex 与 `_cat` 端点；Kibana 与官方客户端库可直接连接 | `README.md:386-388` |
| F-153 | scroll 是有界的前置快照而非逐 segment 游标：精确总数超出快照窗口的查询被拒为 400，不静默截断；任意大小的结果集应使用 `search_after` | `README.md:388-392` |
| F-154 | 最新闭环对拍（对照 live Elasticsearch 8.13.4）得分 55 胜、26 平、4 负，含 1.72 倍摄入吞吐与 1.61 倍更小的磁盘占用 | `README.md:401-404` |
| F-155 | 四处失败均为同一缺口：高写入速率下运行的读 p99；该发现被完整写出于 `demo/playbooks/MIXED_READ_UNDER_WRITE_FINDING_2026-07-08.md` | `README.md:406-408` |
| F-156 | `docs/WHY_XERJ.md` 记录同一记分卡为 "55W / 26T / 4L, 3 N/A on the full matrix" | `docs/WHY_XERJ.md:53-55` |
| F-157 | 基准方法学为闭环、关缓存、语料相同、带正确性校验（"faster-but-wrong counts as a loss"），发布前经独立对抗复测；复测把数字推向不利于 XERJ 的一侧时，公开数字当天更正 | `docs/WHY_XERJ.md:53-56` |
| F-158 | XERJ 侧头条指标的一键复现脚本位于 `scripts/bench/`（摄入 docs/s、size:0 延迟、kNN 召回、重排阶段契约） | `docs/WHY_XERJ.md:56-58` |
| F-159 | 安全模型：全新节点只绑定 `127.0.0.1`；明文绑定到其他接口需显式允许，否则拒绝启动 | `README.md:59-64` |
| F-160 | `--insecure` 关闭 TLS 与 API 密钥认证，能访问该端口的调用方即超级用户，可读可删包括每个 `/_memory` 命名空间在内的所有索引 | `README.md:59-63` |
| F-161 | 认证默认开启（任何不带 `--insecure` 的启动，含从配置文件启动），首次启动铸造 `admin.key`；`autoindex` 不从 `xerj.toml` 读取密钥，须用 `--api-key` 或 `XERJ_API_KEY`，否则每个请求返回 401 | `README.md:217-226` |
| F-162 | 安装脚本对下载资产做 SHA-256 校验且失败即中止（缺 checksum 或不匹配都中止）；`sh` 安装器依次尝试 `sha256sum`、`shasum`、`openssl`、`sha256`、`busybox`、`cksum`，全部不可用时拒绝安装；`XERJ_INSECURE_SKIP_CHECKSUM=1` 才允许跳过 | `landing/llms.txt:14` |
| F-163 | 安装器不修改 shell profile；新 shell 中 `~/.local/bin` 常不在 `PATH` 上，须用绝对路径或先导出 PATH | `landing/llms.txt:16` |
| F-164 | `XERJ_VERSION=vX.Y.Z` 可固定版本，`XERJ_INSTALL_DIR` 可指定安装目录；Windows 默认装到 `%LOCALAPPDATA%\Programs\xerj` 并加入用户 PATH（`XERJ_NO_PATH=1` 可退出） | `landing/llms.txt:14` |
| F-165 | `xerj init` 在项目中注册 MCP server 到 `.mcp.json`，并为 Claude Code/Cursor 写一份 10 行 skill，对其编辑的文件留 `.bak` 备份；`xerj gain` 从节点审计日志显示计数过的用量（搜索数、命中率、延迟） | `landing/llms.txt:22` |
| F-166 | `autoindex` 是唯一没有 HTTP 等价物的操作：没有 `POST /_autoindex`，也没有触发端点，必须在文件所在机器上运行 | `landing/llms.txt:77` |
| F-167 | HTTP 429 是节点内存断路器短时卸荷：运行降低并发、退避后只重发被拒条目并继续，流中出现 "server is shedding load … re-offering"，终行带 `bulk_retries=N`；节点持续 600 秒不接收才退出 1 | `landing/llms.txt:37` |
| F-168 | 数据集被服务器以 HTTP 400 拒绝时，该数据集的文件被记为 junk 并附服务器给出的原因，其他数据集照常索引，退出码为 3，`xerj-done` 带 `datasets_refused=N files_refused=M`；401/403/404/408/429/5xx 不算拒绝，仍退出 1 | `landing/llms.txt:36` |
| F-169 | 告警能力是部分的：真实可用的形态只有 `PUT /_watcher/watch/<id>` 配 `trigger.schedule.interval`（≥ 1 秒）、单索引 `input.search`、`condition.xerj_decide` 与 `index_alert` 动作；其余形态返回 501 | `landing/llms.txt:69` |
| F-170 | 告警的诚实边界：重启不恢复 watch，单次 decide 预算 1000 | `landing/llms.txt:69` |
| F-171 | 用户自备摄入插件未实现：转换管线只有内置原生代码（树中没有 wasmtime 后端） | `landing/llms.txt:69` |
| F-172 | 记录包（record pack）自 v1.0.0-rc.78 起真实存在：`xerj corpus build` 把声明式配方变成带校验和的可移植记录包，`corpus add --from <pack>` 校验每文件 SHA-256，`--verify-sig` 校验 SHA256SUMS 上的 ed25519 分离签名 | `landing/llms.txt:69` |
| F-173 | 尚未构建的是"预索引"那一半：可挂载的已建索引包仍不存在；hub 目录中除一个包外仍是真实语料 | `landing/llms.txt:69` |

## I 组：参考编码与语料库

| 编号 | 事实 | 来源 |
|---|---|---|
| F-174 | 参考编码闭环为：`xerj corpus add`（克隆参考仓库，一次一个领域）→ `xerj corpus build`（收割记录成可移植包）→ `xerj corpus index`（用 autoindex 建索引）→ `xerj code`（检索后再写，每次任务） | `tools/xerj-code/SKILL.md:254-262` |
| F-175 | 克隆为浅克隆（`--depth 1`），落在 `~/.xerj-code/corpora/<name>/`；每次构建在旁写一份 `corpus.json`（URL、完整 commit SHA、许可证） | `tools/xerj-code/SKILL.md:281-285` |
| F-176 | 语料名与仓库名在触碰文件系统前校验，含 `/`、`*`、前导 `.` 或保留字的名字在解析阶段被拒（固定克隆检出会执行 `git checkout --force`） | `tools/xerj-code/SKILL.md:299-302` |
| F-177 | `xerj code` 返回的是匹配到的**定义**而非字节窗口：定位来自索引已携带的 `symbols[]`，输出形如 `[function addBulkStringToReplyIOV @ line 2635 — 366 of 272,498 chars]` | `tools/xerj-code/SKILL.md:341-348` |
| F-178 | `xerj code` 的退出码：`0` 有命中、`1` 无匹配（含 `--json` 的空 `hits.hits`）、`2` 用法错误/节点不可达/传输失败/30 天过期拒绝、`3` 语料在 `state/` 中但本节点 0 个存活索引 | `tools/xerj-code/SKILL.md:365-371` |
| F-179 | `xerj code` 与 `xerj search` 的退出码契约不同：后者在空结果时退出 0 | `tools/xerj-code/SKILL.md:373-374` |
| F-180 | 默认检索模式为 `bm25`；两语料十二个手标查询的实测：bm25 的 top-3 在 rust-text 为 6/6、kv-oss 为 6/6、合并 12/12 | `tools/xerj-code/SKILL.md:378-386` |
| F-181 | hybrid 曾是默认值，选它只基于 rust-text 语料（其 top-1 更优）；在 C 语料上向量臂只覆盖 407 个索引中的 5 个（issue #173） | `tools/xerj-code/SKILL.md:392-397` |
| F-182 | 自 #977 起 hybrid 为服务端融合：单个原生顶层 `hybrid` 查询，`{"fusion":{"method":"rrf","k":60}}`，无客户端排名合并；命中前先给出"实际跑了哪些臂"的说明行 | `tools/xerj-code/SKILL.md:405-414` |
| F-183 | 向量臂只对映射了 `semantic_text` 的索引可用；语义查询作用于未映射索引时不降级，而是让整个请求 400 并带上通配符下的其他索引 | `tools/xerj-code/SKILL.md:417-422` |
| F-184 | `xerj code` 从不请求 `highlight`：在本引擎上 highlight 块会改变 `_score` 并重排命中（issue #177），同一查询 top-1 无 highlight 为 6/6、有 highlight 为 1/6 | `tools/xerj-code/SKILL.md:427-430` |
| F-185 | 受限许可证（AGPL、SSPL、Elastic、BUSL、GPL 系、MPL、未知）命中的段落下方会带 `!! <licence>: adapt the APPROACH, do not copy the code` | `tools/xerj-code/SKILL.md:452-458` |
| F-186 | 超过 30 天的索引被拒绝作答，除非传 `--stale-ok` | `tools/xerj-code/SKILL.md:460-463` |
| F-187 | MEATL 输出格式每命中一行：`@ok f=<file>:<line> score=<12.34>[ why=<licence>]`、`@no q="<query>" why=no-match-in-corpus`、`@mode <arms-ran note>` | `tools/xerj-code/SKILL.md:476-482` |
| F-188 | 对照实测：7 个专用构造库、21 次运行，原生与 xerj 都解出 21/21；xerj 的输出 token 少 1.5 倍、成本低 1.3 倍；纯记忆失败 1/21 并多花 6.5 倍成本 | `tools/xerj-code/SKILL.md:21-30` |
| F-189 | 对已记忆的公共库代码，检索是净开销（"retrieval is **overhead**"），纯记忆最便宜，注入大段参考反而可能是最差的一臂 | `tools/xerj-code/SKILL.md:31-34` |
| F-190 | 语料级实测：裸提示在 33 个受测语料上为 20%，带语料为 98% | `tools/xerj-code/SKILL.md:174-178` |
| F-191 | `xerj corpus index <corpus> --fresh` 在现有索引旁构建替代索引（命名 `xc-<corpus>-b<stamp>-*`），校验通过后以原子改名切换 `state/<corpus>.json`，再按精确名字删除旧索引；失败的构建被删除，旧索引、旧状态文件与旧状态目录原样保留 | `tools/xerj-code/SKILL.md:196-210` |
| F-192 | 记录数是三态：一个数字、404（无匹配索引，即真零）、或 Unknown（超时、5xx、无法解析）；Unknown 不授权任何删除或切换 | `tools/xerj-code/SKILL.md:211-217` |
| F-193 | 状态文件有两个前缀：`prefix` 恒为 `xc-<corpus>`（整个命名空间），`index_prefix` 是已验证的那次构建，也是 `xerj code` 实际查询的索引 | `tools/xerj-code/SKILL.md:230-234` |
| F-194 | 首次构建中断时保留该构建并在状态文件记 `salvaged: true` 与真实 `autoindex_exit`；`xerj code` 每次查询在 stderr 警告覆盖不完整——此时"未命中"不是"代码不存在"的证据 | `tools/xerj-code/SKILL.md:218-226` |
| F-195 | `tools/xerj-code/hub/` 下有 5 个已定版语料定义：`xerj-search`、`xerj-vector`、`xerj-storage`、`xerj-columnar`、`xerj-blogposts` | `tools/xerj-code/hub/` 目录 |
| F-196 | 语料源分三档：`review.use` 字段记录每个仓库属于哪一档；Elasticsearch（AGPL/SSPL/Elastic 许可）与 sonic（MPL-2.0）为"仅可参考"档 | `tools/xerj-code/SKILL.md:63-69` |
| F-197 | `xerj corpus add --from` 读本地文件，v1.0.0-rc.95 起不抓取 URL，传 URL 报 "no such manifest" | `tools/xerj-code/SKILL.md:96-98` |
| F-198 | `xerj code` 的 MCP 版本 `xerj_code_search` 文本输出与 `xerj code` 的散文输出逐字节相同（同样的命中、同样的 `!!` 许可证警告、同样的页脚）；拒绝类错误为 `isError: true`，**无匹配为 `isError: false`** | `tools/xerj-code/SKILL.md:436-443` |
| F-199 | `xerj code` 之外的 MCP 工具 `xerj_code_search` 走 `tools/xerj-code/` 参考编码管线，含陈旧拒绝、许可证警告、无匹配即指引 | `AGENTS.md`（MCP 段） |

## J 组：文档与代码的已知漂移

| 编号 | 事实 | 来源 |
|---|---|---|
| F-200 | `AGENTS.md` 写 "Thirteen tools: `xerj_search`, … `xerj_code_search`"，实际 `tools/list` 服务 17 个（F-060、F-063） | `AGENTS.md`（MCP 段） |
| F-201 | `README.md` 写 "Thirteen tools are exposed. Eleven are thin proxies over an endpoint XERJ already serves"，其工具表列 11 + `xerj_map` + `xerj_code_search` = 13；实际 17 个 | `README.md:330-344` |
| F-202 | `README.md` 写 "the `/_graph` routes, evidence on links, the eight detectors and the two-hop cap"，注册表实际返回 9 个检测器（F-139） | `README.md:461-463` |
| F-203 | `docs/WHY_XERJ.md` 写 "streaming extractors for 13 format families"，代码侧 `extract/` 有 25 个抽取器模块、`sniff::Family` 有 28 个变体（F-029、F-030） | `docs/WHY_XERJ.md:30` |
| F-204 | `README.md` 记录参考编码三臂实测：仅凭记忆 260,916 输出 token / $11.18 / 解出 11/16；grep 驱动 26,477 / $3.27 / 16/16；XERJ 9,982 / $1.58 / 16/16 | `README.md:94-99` |
| F-205 | `README.md` 记录上述对比为比 grep 少 2.7 倍输出 token、比仅凭记忆少 26 倍，单个 Java 任务最多 278 倍 | `README.md:100-102` |
| F-206 | `README.md` 记录 grep 式 agent 在一个语料上最多拉入 1.06M 输入 token | `README.md:88-89` |

## 相关参考

- [信源登记](source.md)：仓库身份、计数口径与关键文件清单
- [架构洞察与知识地图](insights.md)：洞察四元组与学习路径
- [领域背景](background-research.md)：检索栈背景与成本模型
- [References 索引](index.md)：本目录汇总
