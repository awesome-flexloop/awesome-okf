---
type: Reference
title: XERJ 官方文档站洞察（第二轮）
description: 阅读 xerj.org/docs/ 得到的六条增量洞察（洞察 7～12）——含「接了线但没接线」「集群给的是选主环不是副本」「诚实被编码进响应体」等，附事实覆盖分配
tags: [xerj, 架构洞察, 官方文档, 配置面, 集群]
generated: { by: source-code-to-okf-wiki/I, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-docs-facts
    resource: /references/facts-docs.md
    title: 第二轮事实清单
  - id: xerj-docs-source
    resource: /references/docs-source.md
    title: 官方文档站信源登记
---

# XERJ 官方文档站洞察（第二轮）

> 本文件是第二轮的 I 阶段产出，编号续接 [第一轮洞察](insights.md)（洞察 1～6）。每条按「陈述 / 证据 / 反常识 / 行动」四元组组织，证据引用第二轮事实编号（F-207～F-338）。

## 洞察 7：配置文件里最危险的不是缺键，而是「接了线但没接线」

- **陈述**：XERJ 的配置面有 24 个段、代码里 24 个 `*Config` 结构体，但文档的「Full key table」只覆盖 15 段，`engine/xerj.default.toml` 只交付 13 段；**16 个键被完全接受、校验、然后什么都不做**，另有 1 个部分接线——改离默认值只会在启动时打一条警告。
- **证据**：F-256～F-261。被明确标注为「Accepted but not wired」的键有 16 个完全未接线 + 1 个部分接线（`[vector] default_quantization`），包括 `[merge] min_segments / io_rate_mb_per_sec / max_concurrent`、`[compression] enabled / block_size_docs`、`[fts] default_analyzer`、`[vector] default_metric / hnsw_m / hnsw_ef_construction / hnsw_ef_search / max_dimensions`、`[logs] retention_days / time_partition`、`[indexing] turbo_batch_size / turbo_parallel / turbo_fast_analyzer`（F-260）。另有 10 个键存在于 default toml 却不在文档键表中（F-259）：`server.auto_port`、`server.trusted_proxies`、`auth.metrics_token`、`storage.flush_idle_secs`、`limits.max_actions_per_bulk`、`limits.snapshot_repo_allowlist`、`limits.hub_pack_restore`、`limits.max_segment_hydration_cache_mb`、`logging.format`、`logging.access_log`。
- **反常识**：文档首页说「Every key has a production-ready default, so the smallest working config is an empty file」——听上去配置面是完备的。但完备的是**默认值**，不是**覆盖面**。一个运维者把 `io_rate_mb_per_sec` 从 100 调到 20，会得到一条「已接受」的启动日志和一个**完全未被限流**的合并路径（F-233）。没有这个键，运维者至少知道要自己解决；有了这个键，运维者以为已经解决。
- **行动**：改任何非默认配置项之前，先确认它是「wired」还是「accepted but not wired」——判据有三条：键表里有没有「Not wired」标注；改离默认值时启动是否打警告；该键的真实来源是否在别处（例如合并并行度实际来自 `XERJ_MERGE_PARALLELISM`，因为 `[merge] max_concurrent` 没接线，F-274）。

## 洞察 8：集群模式今天给的是「选主环」，不是「数据副本」

- **陈述**：`[cluster] enabled = true` 启动的是内嵌 Raft：选主、心跳、带认证的节点间传输、持久化的本地 Raft 日志——这些是真实且被测试过的；但**元数据不复制、文档不复制、没有分片路由、没有节点生命周期 API**。集群模式当前是一个「带共识层的单节点」。
- **证据**：F-239～F-249。文档以四张「What cluster mode does not give you yet」清单逐项写明：节点 A 创建的索引在节点 B 上不存在；节点 A 上 PUT 文档、节点 B 上 GET 返回 404 `index_not_found`（3 节点环实测，F-241）；没有到主分片的转发也没有副本读；没有 drain / activate / remove 端点，也没有 region split-merge（F-243，该页还注明「此前版本的这一页写过它们，但二进制从未发布过」）。真实的部分是：每任期恰好一个 leader、随机 150–300 ms 选举超时、3 节点回环环实测约 250 ms 选出新 leader（F-244）；节点间每条连接用 HMAC-SHA256 挑战认证且不存在未认证模式（F-245）。
- **反常识**：内嵌 Raft + 选主 + 250 ms 故障转移，组合起来非常像「分布式数据库」。但**分布式数据库的分布式指的是数据分布，而 XERJ 集群模式的分布式指的是控制面分布**。数据仍然是节点本地的（F-241、F-307）。把 `cluster.enabled = true` 读成「多副本高可用」，是这里最容易犯、也最贵的错误。
- **行动**：需要第二份活副本时，用 **WAL tap**——它是单向的（单向写入外部 ES 兼容目标，F-288），不是双向复制，但它能在目标短暂不可达时靠 `min_retained_generations` 找回条目（F-291）。集群升级则必须按「同一维护窗口全停全起」规划，因为线协议没有版本协商（F-250）。

## 洞察 9：诚实被编码进了响应体，而不只是写进文档

- **陈述**：XERJ 把「边界」做成**可执行的检查点**而非文字承诺——大多数能力边界在遇到时会以明确错误、明确警告或明确状态出现，而不是静默降级。
- **证据**：F-286、F-327～F-331、F-312。具体地：未支持的 ES 调用返回结构化 `not_supported_yet` 错误而不是 500（F-327）；scroll 超过快照窗口返回 400 并说明「不会返回被静默截断的结果集」（F-331）；`_cat/indices?v` 不出表头行这一**会咬人**的差异被写在「Known semantic differences」里而不是藏起来（F-326）；`_id` 按字典序排序导致的静默截断被专门用一整段展开并给出实测（F-333）；WAL 损坏时引擎自愈（截断撕裂尾部 / 冻结中段损坏文件 / 跳过不可读帧）而不是拒绝启动，且**没有**人工修复命令（F-312）；未接线的配置键改离默认值会在启动时打警告（F-260）。
- **反常识**：大多数项目的「诚实」是写在 README 里的——它描述意图。这里不同：诚实被编译进**响应体和启动日志**。因此评估 XERJ 时，它的**错误码比它的成功路径更值得读**：错误码告诉你的不只是「这次失败了」，还有「这个能力边界的确切形状」。
- **行动**：把 XERJ 当作一个「用失败模式表达契约」的系统来评估。上手第一天不要只跑成功路径——去撞边界：查一个未映射字段、请求一个未实现的融合方式、给一个非法量化值、开一个超过上限的 scroll。你会看到它如何描述自己。

## 洞察 10：量化换的是精度，不是内存（#392 在三处重复出现）

- **陈述**：`scalar8` 量化（ES 的 `int8_hnsw` 别名）**不是内存优化**——它换来的是打分精度，代价是 1～2% 的召回损失；常驻内存不变，而且它放弃了 HNSW 服务的 kNN。
- **证据**：F-359（`vectors.html`：scalar8 是 1 字节/维的码，扫描时**从 `_source` 读全精度向量并按查询现量化**，所以 RAM 里什么都不变小；且 scalar8 的 `_score` 及其排序依赖候选集——#392）、F-298（运维页容量规划：向量按 `dims × 4` 字节叠加，**即便 scalar8 也不减常驻**）、F-311/F-316（排障页「node RAM climbs forever」的对策里再次点名 #392，并说明节点级 `[vector] default_quantization` 未接线）、F-360（量化只能按字段在 mapping 的 `index_options.type` 打开；节点级键未接线，只有 `"binary"` 的拒绝会读它）、F-362（ES 的 `index_options.type` 保持宽松，线兼容面上不拒绝 ES 映射）。
- **反常识**：ES 的 `int8_hnsw` 是「省内存」的卖点。XERJ 提供同名特性，但语义相反——**它换的是精度**（用量化码打分，而不是拿全精度向量去比）。想要省内存，得从别的方向来：更小的维度数、更多的索引、切掉 flush_size_mb。
- **行动**：评估量化时先问「我要省的是内存还是召回」。要省召回 → 可以用 scalar8（1～2% 损失，且实测 recall@10 = 0.998，F-351）。要省内存 → 量化帮不上忙，得改维度或拓扑。同时注意节点级开关没接线（F-260），量化只能**按字段**在 mapping 里通过 `index_options.type` 打开。

## 洞察 11：文档站的「每个页面都有源码指针」本身就是一种可追溯性设计

- **陈述**：官方文档的每个页面底部都有一行 `Source → engine/crates/...`，键表给出每个键的类型、默认值与**是否接线**，每个数字都标注测量条件与日期；这把「文档」变成了一份**可机械复核的断言集**。
- **证据**：F-208（首页规则："If the docs and the code disagree, the code is right"）、F-258～F-260（键表带类型/默认值/接线状态）、F-235（压缩力度带具体事故数据：1.55M → 21k docs/s、75% 文档被拒）、F-238（注明「#318 之前这两个键被静默忽略」）、F-243（注明「此前版本写过、但二进制从未发布过」）、F-241（3 节点环实测出的 404）、F-330（上限常量带 issue 号 #198）、F-291（`min_retained_generations` 连上限与成本公式都写明）、F-219/F-358（分析器注册处注释把「为什么 `standard` 不含停用词」写得一清二楚，文档却写反了）。
- **反常识**：一堆「accept but not wired」的坦白，比一份「全部可用」的表格**更有用**——因为前者告诉你**不能依赖什么**，后者只告诉你有什么。一份诚实标注了空洞的 API 文档，其工程价值高于一份把所有键都写成「已支持」的文档。
- **行动**：把每页底部的 `Source →` 行当作**查证入口**而不是装饰。遇到文档里任何一个数字，回源码数一遍的成本极低——本轮 4 处不一致全部在十分钟内机械检出（见 [facts-docs.md](facts-docs.md) 交叉核验记录）。

## 洞察 12：文档的「诚实」与「漂移」共存，而漂移可以被机械检出

- **陈述**：这个项目在「代码 vs 文档」这一层有强纪律（首页明文规则），但在「文档 vs 文档」这一层没有门禁——同一发布版内存在**六处**不一致，其中**一处是实质性的能力错误**，且**全部可被机械检出**。
- **证据**：F-212（导航写 "32 variants"，同页正文列 50，代码 50）、F-257（CLI 页写 `--config` 默认 `./xerj.toml`，配置页与代码说没有这个回退）、F-320（迁移页 1,371/1,374 vs README 徽章 1,366/1,369）、F-336（explain 端点：文档两处都不对，代码是 `POST /v1/indices/:name/explain-plan`）、**F-218/F-219/F-358（分析器清单：文档写 4 个且 `simple` 根本不存在，代码注册 11 个；文档说 `standard` 含英文停用词，代码说它刻意不含）**、F-335（原生 API 文档列 13 个端点，路由实际注册 31 个）。第一轮还发现同类漂移三处（F-200～F-203：MCP 工具数 13 vs 17、检测器 8 vs 9、格式族 13 vs 28）。
- **反常识**：项目纪律的对象是「代码 vs 文档」，而「文档 vs 文档」这一层没有自动校验——所以**同一个站点内部**也会打架。这不是纪律失效，而是纪律的边界；理解这一点很重要，否则你会以为「官方文档写了」就等于「官方文档对」。
  更值得警惕的是**第 5 项的量级**：它不是数字对不上，而是**一个不存在的分析器被写进了文档、两个真实存在的重要分析器（`ecommerce` 的双向同义词、`cjk`/`thai`/`icu_folding` 的多语言支持）被漏掉**，并且**默认分析器的语义被写反了**——照文档配置中文语料的人，会得到一个不存在的分析器名；照文档理解 `standard` 的人，会误以为它会丢掉 "GET" 这类词。
- **行动**：**不要把官方文档当唯一事实源**。具体做法：凡是要写进自己的决策文档的数字，都回源码核一遍（本轮成本极低：数一个常量、跑一个 grep、比对一张表、读一段注册代码）；凡是要引用的端点路径，同时查两个页面**并 grep 路由表**；凡是要用的能力名，回源码确认它**真的被注册**。养成这条习惯后，官方文档就从「信源」变成了「线索」——而线索的质量恰恰是它自己最在意的部分。

---

## 第二轮事实覆盖分配

| 概念文档 | 覆盖的第二轮事实编号 | 主题 |
|---|---|---|
| [09 查询类型与聚合](/concepts/09-query-types-and-aggregations.md) | F-209～F-217 | 50 种查询、2 种显式拒绝、62 种聚合、精确性与采样例外 |
| [10 分析器与摄取管线](/concepts/10-analyzers-and-ingest.md) | F-218～F-224 | 4 个内置分析器、4 条摄取路径、端到端背压 |
| [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md) | F-225～F-255 | 三文件 segment、WAL 三档、9 种列编码、Zstd 三档、集群四项「不提供」、磁盘格式标记 |
| [12 配置与环境变量](/concepts/12-config-and-environment.md) | F-256～F-292 | 24 段配置面、16 个未接线键、环境变量优先级不统一、认证与 TLS、WAL tap 与 rerank 的写一次语义 |
| [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md) | F-293～F-317 | systemd、就绪探针、SIGHUP 热加载、容量三数字、三文件 fd、备份四式、升级、6 类症状 |
| [05 官方文档地图与选型](/examples/05-official-docs-map.md) | F-318～F-358 | 46 页导航地图、ES 兼容边界与 4 处漂移、Corpus Hub 两条通道、10 recipe + 5 playbook 选型 |

## 学习路径更新（两轮合并）

```
第一轮（源码与上游自述）              第二轮（官方手册）
  00 整体架构      ──────────────→  09 查询类型与聚合
  01 安装与快速上手  ──────────────→  10 分析器与摄取管线
  02 autoindex 流水线 ─────────────→  11 存储、压缩与集群现状
  03 MCP 智能体接口  ──────────────→  12 配置与环境变量
  04 检索路径与裁剪   ─────────────→  13 生产运维与排障
  05 向量与混合检索
  06 记忆与第二大脑
  07 ES 兼容与基准
  08 参考编码与语料库
```

**推荐读法**：先用第一轮建立「它是什么、边界在哪」的心智模型，再用第二轮查「具体怎么配、怎么运维」。若你是运维者，第二轮的三篇（11/12/13）比第一轮更重要；若你是要把它接进产品的工程师，第一轮的 03/04/05 更重要。

## 相关参考

- [第一轮洞察](insights.md)：洞察 1～6
- [第二轮事实清单](facts-docs.md)：F-207～F-338 与交叉核验记录
- [官方文档站信源登记](docs-source.md)：本轮信源身份与页面清单
