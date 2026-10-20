---
type: Concept
title: autoindex 零配置流水线
description: XERJ 旗舰能力的完整机制——内容驱动的格式识别、25 个抽取器、字段来源标记决定的数据集划分、阶段序列、10 分钟决策门与退出码语义
tags: [xerj, autoindex, 摄取, 零配置, 决策门]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-facts
    resource: /references/facts.md
    title: XERJ 事实清单
  - id: xerj-insights
    resource: /references/insights.md
    title: 架构洞察与知识地图
---

# autoindex 零配置流水线

`xerj autoindex <folder>` 是 XERJ 的旗舰能力：把任意文件夹变成类型化、可查询、自我描述的索引，不需要写 schema，也不需要配置管线。源码注释里第一句就划定了它的边界——**纯 ES 兼容 HTTP 客户端特性，不链接 `xerj-engine`，可对任意端点工作，无法拖垮服务端**（F-027）。

## 三个阶段

上游的验证记录是：在 1,995 文件的密文清单语料上，80/81 项 ground-truth 检查通过（跨格式关联被精确找到，五种埋设的日期编码全部正确定型，方言敌意的 CSV 精确处理），另加一个独立语料（F-014）。

一次运行大致分三段：

| 段 | 做什么 | 关键性质 |
|---|---|---|
| Phase A | 遍历、嗅探、采样 | 读遍每个文件以识别类型并**在本机测出各格式族的吞吐率** |
| Phase B | 真正索引 | 用 Phase A 测得的速率换算耗时区间 |
| 收尾 | 目录刷新、计数、关联、直方图、目录落库 | 每一步都可独立恢复 |

## 格式识别：永不信任扩展名

源码注释的第一句就是规则本身（F-028）：

> Content-based format detection. **NEVER trusts file extensions.**
> Order: magic bytes → binary check → text heuristics
> (json/jsonl → html/xml → logs → sql dump → csv → yaml → txt)

`sniff::Family` 枚举共 **28 个**变体（F-029）：

```
Jsonl, Json, Csv, Logs, Xml, Html, Yaml, TxtProse, TxtLines, Pdf, Eml, Mbox,
Docx, Pptx, Xlsx, Xls, Doc, Epub, Ipynb, Man, Sqlite, SqlDump, Code,
UnityYaml, UnityMeta, Bvh, Stub, Binary
```

其中几个反直觉的识别方式：

- `.doc`（Word 97-2003，OLE2 复合文件）靠 **OLE2 魔数 + `WordDocument` 流**识别，正文经 FIB piece table 恢复；
- `.xls`（BIFF8）靠 **OLE2 魔数 + `Workbook`/`Book` 流**识别；
- `.ipynb` 在 JSON 分类器**之前**按内容判定，避免被当成普通 JSON；
- Unity 的 `.meta` 靠首行 `fileFormatVersion:` 识别，作为 GUID 到路径的连接键；
- `Stub` 只由 CLI 参数 `--stub <glob>` 指定，永远不会被嗅探出来——它只产出一张「名卡」记录，内容永不打开。

> **反常识**：把 `data.csv` 改名成 `data.pdf` 不会改变识别结果。识别由内容决定，不由文件名决定。

## 抽取器：25 个模块，有界内存，从不致命

`extract/` 下有 **25 个**抽取器模块（F-030）：

```
bvh  code  csv_x  doc  docx  eml  epub  html  ipynb  json  jsonl  logs  man
mbox  opc  pdf  pptx  sqldump  sqlite_x  txt  unity  xls  xlsx  xml_x  yaml_x
```

模块顶部的契约只有一句（F-031）：**每个抽取器都是有界内存且从不死 Fatal**——解析失败按 `family → txt → junk-with-metadata` 降级并计数。一个坏文件不会毁掉整次运行。

产出的记录结构是 `RawRecord`（F-032）：

| 字段 | 含义 |
|---|---|
| `fields` | 字段名到值的映射 |
| `locator` | 内容位置定位符（字节偏移 / 序号 / 表+行）——幂等 `_id` 的成分 |
| `group` | 文件内的子数据集组（SQL/SQLite 的表名） |
| `origin` | 字段名来自文件还是来自抽取器 |

### 分段与截断的四个常量

| 常量 | 值 | 依据 |
|---|---|---|
| `MAX_LINE` | 16 MB | 单行上限（F-035） |
| `MAX_WHOLE_FILE` | 64 MB | 整文件解析上限（F-035） |
| `SECTION_CHARS` | **2 KB** | 目标字符/文档段（F-036） |
| `SECTION_OVERLAP` | 200 | 上一段末尾在下一段开头重复的字符数（F-039） |
| `MAX_RECORDS_PER_FILE` | 4096 | 单文件记录数上限（F-038） |

`SECTION_CHARS` 从 32 KB 改成 2 KB 是本项目里最有价值的一处「检索粒度」教训，注释里保留了完整理由（F-036、F-037）：

> 32 KB 是**存储**粒度，不是**检索**粒度——BM25 按文档打分，32 KB 的段落会把任何匹配稀释成噪声，且每次命中都要拖 32 KB 通过 `_source`。在一个 460 次提交的历史文件上实测：32 KB 段落产出 25 个文档覆盖 15,407 行，相关提交**不可检索**；改成 2 KB 并带段落重叠后可检索。

2 KB 恰好落在内置神经嵌入器 512 token 限制之内，于是一个段落对应一个向量而不被截断。

截断从不静默：`MAX_RECORDS_PER_FILE` 触发时置 `ExtractStats.truncated`，由报告层显式呈现（F-038）。

## 数据集划分：字段来源决定边界

这是整条流水线里最容易被误解、也最关键的一处设计。

`FieldOrigin` 区分两种字段名来源（F-033）：

- `Data`——**从文件里读出来**的字段名（JSON 的 key、CSV 的表头、SQL 的列名、HTML 表格头、解析出的日志键）；
- `Extractor`——**抽取器自己发明**的字段名（`title`/`body`、`defs`/`symbols`/`symbol_count`、`page`/`section`）。

数据集聚类**只把 `Data` 字段名作为键**。源码注释解释了为什么（F-034）：

> 一个能因**抽取器变更**（而非文件变更）而出现或消失的字段名，会静默地把该文件的文档移到另一个索引，并孤立已按旧 slug 写入的文档（issue #178）。

因此：

- **修改 CSV 表头会改变它落到哪个索引**——这是设计选择，不是 bug；
- **抽取器版本升级不会让旧文档搬家**——因为 `title`/`body` 不参与聚类。

> **行动**：规划语料布局时，把「同 schema 的文件放在一起、schema 演进时另起目录」当作硬约束。否则一次表头变更就会把语料劈成两个索引，历史查询静默缺数据。

## 阶段序列与进度协议

`--no-graph` 路径的阶段序列是（F-042）：

```
walk → hash → scan → prepare → snapshot → index → finalize-catalog → finalize-refresh → finalize-verify
```

默认（带图）路径多出图相关阶段与额外收尾（F-041）：

```
walk → hash → scan → prepare → graph → index → graph-corpus
     → finalize-refresh → finalize-count → finalize-correlate → finalize-histogram → finalize-catalog
```

恢复运行从 `replay` 阶段开始，其 `index` 阶段只统计**尚待应用**的写入操作（F-043）。因此「一个仍显示 `scan` 100% 的进度行」意味着还在扫描，绝不是已经在索引。

进度输出分两行，各有用途：

| 行 | 面向 | 节奏 |
|---|---|---|
| `xerj-bar [####----] 93.4% \| index \| 8082/8083 items \| eta 7s` | 人（转述给用户逐字展示） | 最多每 15 秒一条，外加每次阶段切换，且间隔不小于 2 秒 |
| `xerj-progress phase=index basis=bytes pct=93.4 items=8082/8083 eta_s=7.2 …` | 机器（解析它） | `--progress-interval` 节奏（默认 5 秒） |

两条纪律值得记住（F-042 与 CLI 帮助）：

1. **每条记录由首个 token 标识，且强制**——路径等外部文本会被剥除控制字符并限长，所以构造的文件名无法伪造一条记录或重绘终端；
2. **`pct`/`eta_s` 在无法诚实计算时是字面量 `unknown`（JSON null），绝不用填充数字**——没有分母时进度条画成 `[????…]`，只有真正 100% 才画满。

## 10 分钟决策门

这是 XERJ 最独特的一处工程：**把「替用户决定占用他机器多久」这件事写进二进制**，而不是写进建议。

规则（F-044～F-049）：

- Phase A 已经读遍每个文件并解析，因此能**在本机测出**各格式族的吞吐率；autoindex 把它换算成一个**区间**（绝不给一个自信的单值）并打印计算依据；
- Phase A 从未完整读取的格式族被**排除在算式外**，而不是按其他族的速率计价；
- 区间**只覆盖客户端侧抽取**，不含服务端索引、嵌入与网络时间——这正是门禁比较**上界**的原因；
- 若上界超过 `--max-minutes`（默认 10，F-045）且无人批准，**一个字节都不会被写入**：JSON 决策请求写到 stdout，进程退出码 **4**；
- 回答方式是重跑同一条命令并加 `--approve proceed|fast|cancel`（F-046）。

`--approve` 的三个选项语义不同：`proceed` 全量索引；`fast` 索引但加 `--no-semantic --no-graph`；`cancel` 什么都不索引并干净退出。

`narrower` 被**显式拒绝**（F-046）——因为「让这次运行范围更窄」意味着指向另一个文件夹，本次运行无法代为决定，接受后再默默索引整棵树属于「接受却被忽略」这一类错误。

**终端提示有严格前提**（F-047）：只有 stdin 是终端、stderr 是终端、且进度输出未被静默时，才会真的提问。否则行为完全一致：JSON 请求进 stdout（`--quiet` 不静默 stdout），退出码 4，载荷里的 `prompt_not_offered_because` 字段说明缺的是哪一项。

> **设计要点**：永不等待一个用户看不见的问题。管道、CI、智能体驱动的运行若等 stdin，就是死锁；而不可见的提示与挂起无法区分——对一个「专门用来告诉你要花很久」的功能来说，这是最坏的失败模式。

## 退出码语义

| 码 | 含义 | 该做什么 |
|---|---|---|
| 0 | 完成 | — |
| **3** | **完成但含 junk——这是成功** | 读 `reason` 与 `datasets_refused`/`files_refused` 再下结论 |
| 2 | 用法错误 | 修命令 |
| 1 | 任何错误 | **先读 `error:` 行**再动作 |
| 4 | 需要决策 | 用 `--approve` 回答，**不要重试** |

退出码 3 携带原因字段（F-051）：

- `reason=catalog-alias-sweep-failed`——语料**已索引**且日志已提交，只是目录的重复别名清理没跑成；
- `datasets_refused=N files_refused=M`——某个数据集的映射被服务器以 400 拒绝，该数据集的文件被记为 junk 并附服务器给出的原因，**其他数据集照常索引**。

后者是最容易被误读的一种：看到「3」就以为整体失败，会把一次部分成功的运行误判为失败，重跑一遍是纯浪费。而 401/403/404/408/429/5xx **不算拒绝**，仍退出 1（F-168）。

## 幂等与恢复

- `_id` 由内容位置定位符派生，因此重复索引同一文件不产生重复文档（F-032）；
- 续跑日志（journal）记录已完成的工作，**中断的运行可恢复且永不重复**；
- 进度汇总行在「目录已存活但本次未提交任何记录」时追加 `(already indexed; nothing new to send)`，避免看起来像「什么都没索引」（F-052）；
- 吞吐率以**本次提交的文档数**为分子，零提交时返回 0（F-053）——一个空跑曾打印出 66,096.3 docs/sec 的荒唐读数。

后续提示 `next:` 会把密钥渲染为 `$XERJ_API_KEY` 或 `$(cat <path>)` 表达式，**不回显管理员密钥**（F-054）。曾经有一次盲测 onboarding 让 `autoindex` 自行发现了 `./data/admin.key` 并把它原文打印在横幅里——读者从没输入过这个秘密，在可复制输出里看到它就是泄露，不是便利。

## 服务端背压

服务器返回 HTTP 429 是内存断路器短时卸荷，不是挂起（F-167）：运行会降低并发、退避后**只重发被拒条目**并继续，流中出现 `server is shedding load … re-offering`，终行带 `bulk_retries=N`；只有节点连续 600 秒不接收才退出 1，此时错误行以 `the server kept rejecting` 开头。遇到就重跑同一条命令即可续跑。

## 规模化边界

上游自己划的线（F-100、F-101）：

- 客户端是流式且可恢复的，**多 GB 语料已验证**；
- 但服务端**按已索引文档数保留堆**：三个 per-segment 缓存（`stored_value_cache`、`dv_cache`、`id_pos_cache`）在合并回收其 segment 之前无上限；
- 观测数据点：2026-09 一次 lexical 模式节点在大规模多仓库代码语料中途常驻 **20.2 GB**。

因此：一次索引一个语料、盯进程 RSS、小机器上在语料之间重启节点（同一 `--data-dir` 重启保留所有索引并释放堆）。

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：autoindex 与引擎的解耦关系
- [01 安装与快速上手](/concepts/01-getting-started.md)：数据目录与索引目录的约束
- [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)：`xerj_map` 读取 autoindex 目录
- [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)：`_passage` 与数据集字段
- 事实来源：[事实清单](/references/facts.md)
- 架构洞察：[架构洞察](/references/insights.md)
