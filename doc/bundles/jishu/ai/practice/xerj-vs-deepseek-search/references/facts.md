---
type: Reference
title: XERJ × DeepSeek Search/Fetch 对比——事实清单
description: 对比束的编号事实清单（F-001 起），按 XERJ 侧 / DeepSeek 侧 / 对照三组组织，每条标注来源与核验状态
tags: [xerj, deepseek, 对比, 事实清单, 检索选型]
generated: { by: source-code-to-okf-wiki/R, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: compare-source
    resource: /references/source.md
    title: 对比束信源登记
  - id: xerj-bundle
    resource: ../../frameworks/xerj/index.md
    title: XERJ 源码学习知识包
  - id: deepseek-guide
    resource: https://api-docs.deepseek.com/zh-cn/guides/search
    title: DeepSeek API 文档——网页搜索与抓取
---

# XERJ × DeepSeek Search/Fetch 对比——事实清单

> 每条标注**所属侧**与来源。XERJ 侧事实来自既有 xerj 束（已在该束内完成 Grep 级验证与计数复核），引用时给出来源编号；DeepSeek 侧事实来自**在线官方文档逐条复核**（见 [source.md](source.md)）。

## X 组：XERJ 侧

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | 语料来源是**本地任意文件夹**：格式识别基于内容而非扩展名，28 个 `Family` 变体、25 个抽取器模块，覆盖源码、PDF/DOCX/XLSX/PPTX/EPUB、邮件 mbox、日志、SQLite/SQL dump、Unity 资产等 | xerj 束 F-029、F-030、F-034 |
| F-002 | 检索面：BM25 全文 + kNN 向量 + `hybrid` 融合（`rrf`/`linear`）、50 种查询类型、62 种聚合 | xerj 束 F-209、F-211、F-094 |
| F-003 | 记忆层：`/_memory/{namespace}` 命名空间（每个命名空间是物理隔离的索引）+ `/_graph` 第二大脑（9 个确定性边检测器、每次调用最多两跳） | xerj 束 F-127～F-129、F-133、F-340 |
| F-004 | 上下文控制：`_passage` 伪字段从原字段切片，`_source` 投影裁剪其余字段。实测 5 个命中覆盖索引后的源码文件：默认完整文档 **416,630 字节** → 加 `_passage` + 投影后 **12,122 字节**（**34 倍**） | xerj 束 F-087、F-088 |
| F-005 | 默认 `_search` 返回完整文档；`_source` 省略时引擎生成的 `<field>_vector`、`<field>_vector_chunks` 伴随字段不返回 | xerj 束 F-086、F-338 |
| F-006 | 边界以追加式提示编码进响应体：`_xerj.hints` 携带 `unknown_field` 条目与开箱即用的修正请求；`ax-*`（autoindex 创建）索引上未映射字段的查找返回 **400** 并报出字段名与可检索字段 | xerj 束 F-089、F-091、F-092 |
| F-007 | 不支持的 ES 线协议调用返回结构化 `not_supported_yet` 错误，而不是 500 | xerj 束 F-327 |
| F-008 | scroll 是有界前置快照，上限 **10,000** 文档；超出返回 400 `illegal_argument_exception` 并在错误信息里给出 `search_after` 替代方案与「不会返回被静默截断的结果集」的说明 | xerj 束 F-330、F-331、F-334 |
| F-009 | HTTP 429 的语义是**内存断路器短时卸荷**而非失败：客户端降并发、退避后只重发被拒条目并继续，终行带 `bulk_retries=N` | xerj 束 F-167 |
| F-010 | 成本形态是**固定成本**：一次索引 + 一台机器；无按次调用费，无按 token 计费 | xerj 束 F-302～F-305（备份与运维形态） |
| F-011 | 隐私默认本地。节点可打开的出站连接只有四类，其中只有三个会携带文档文本——`rerank`（搜索期）、代理嵌入（`--embed-mode proxy`）、WAL tap——**三者默认关闭**；神经模型下载与集群 Raft 不携带文档文本 | xerj 束 F-099、F-127 |
| F-012 | 质量自宣**附测量条件与复现脚本**：未过滤 kNN 的 recall@10 1.00、100 探针均值 0.976（ES 8.13.4 同协议 0.937），且明确区分「ANN 路径实测」与「精确路径构造保证」；基准的 4 处败因完整写出而非略去 | xerj 束 F-124、F-125、F-155、F-157 |
| F-013 | 规模受本机约束：服务端按已索引文档数保留堆，三个 per-segment 缓存在合并回收其 segment 之前无上限；一次观测到 20.2 GB 常驻 | xerj 束 F-100、F-101 |
| F-014 | 部署形态：**一个静态二进制**（61.6 MB，含神经嵌入后端），无 JVM，无外部服务依赖 | xerj 束 F-013、F-329 |
| F-015 | 质量声明的**可验证性**：官方文档站首页即写明「Every key, every flag, every default in these docs comes out of the Rust crates under `engine/crates/`. If the docs and the code disagree, the code is right」 | xerj 束 F-208 |

## D 组：DeepSeek 侧

| 编号 | 事实 | 来源 |
|---|---|---|
| F-016 | 语料来源是**公网实时网页**：Search 接口由 DeepSeek 自研搜索引擎提供支持 | 官方文档「Search 接口」段 |
| F-017 | 过滤机制：针对 **SEO 作弊**、**GEO 操纵**（专门让 AI 在回答里引用自家内容的优化）和**低质量 AI 生成内容**有识别过滤机制；**过滤规则本身不公开**，其边界与召回影响不可外部验证 | 仓库内 deepseek-v41-flash-1017 束 F-058（引官方公告）；本轮在线文档未展开该段 |
| F-018 | 两个端点：`POST https://api.deepseek.com/v1/tools/search`（Search）与 `POST https://api.deepseek.com/v1/tools/fetch`（Fetch）；均为**原始 JSON API**，使用与 DeepSeek API 相同的 Bearer 鉴权 | 官方文档「接口说明」段 |
| F-019 | Search 请求字段：`query`（必填，1～128 个 Unicode 字符，不能全为空白）、`count`（1～50，默认 10）、`ori_question`（触发搜索的用户原始问题）、`localization`（优先返回本地化结果的 IP）、`need_content`（默认 false，为 false 时 `content` 恒为空字符串）；**请求体中的未知字段会被忽略** | 官方文档「请求字段」表 |
| F-020 | 搜索语法原样传递给搜索服务：`site:`、`-site:`、`-关键词`、`-"短语"`、`"短语"`、`lang:`、`after:`（`after:2025` 或 `after:2025-01-01` 两种粒度）、`before:`；可在一个 query 中组合多个操作符 | 官方文档「搜索语法」表 |
| F-021 | Search 响应 `results[]` 字段：`rerank_score`（0～3，综合相关性/权威性/时效性，**≥1.5 为优质结果**）、`title`、`url`、`snippet`（约 100～200 字符，适用于前端展现）、`summary`（约 600～800 字符，适用于给模型阅读）、`content`、`site_name`、`site_icon`、`date`（UTC RFC 3339，未知为 null）、`authority`（0～4，**-1 表示未知**，**≥3 为极权威**） | 官方文档「results 中每一项包含以下字段」表 |
| F-022 | Fetch 请求字段仅 `url`（≤8192 字符，必须为含 host 的 HTTP/HTTPS URL，不能携带用户名或密码）；响应为 `title` + `content`（抓取后的 Markdown 正文） | 官方文档「Fetch 接口」段 |
| F-023 | **Fetch 的结果受目标站点的可用性和访问策略影响**（官方原文） | 官方文档「Fetch 接口」段末 |
| F-024 | 上下文分层：默认 `need_content: false` 时 `content` 恒为空字符串；`snippet`（100～200）面向前端，`summary`（600～800）面向模型，`content` 是完整正文 | 官方文档 + 仓库内 deepseek-search-fetch 束 05 集成篇 |
| F-025 | 错误响应使用 **OpenAI 兼容格式**，`param` 字段**恒为 `null`**；状态码覆盖 400（请求不合法）、401（Key 缺失或无效）、402（余额不足）、403（Fetch 被安全策略拒绝）、404（未获取到可用网页内容）、408（读请求体超时）、413（请求体过大）、429（超 QPS 限制）、500（服务端错误）、504（下游请求超时） | 官方文档「错误」段 |
| F-026 | 404 的五种成因被合并到同一个码：URL 不可用、被站点策略拦截、目标站点返回错误、内容类型不受支持、页面没有可提取的 Markdown 正文 | 官方文档「错误」表 404 行 |
| F-027 | 重试策略由官方给出：408 / 429 / 5xx 等待后重试；402 先充值再重试；**其它 4xx 不修改请求不重试**；Search 与 Fetch **都是只读请求** | 官方文档「错误」段末 |
| F-028 | 计费：Search 与 Fetch 各按**请求次数**计费，**不按 token 或返回结果条数**；每 1,000 次成功请求 **5 元**（即 ¥0.005/次）；**只有 HTTP 200 且产生结果才计费**（Search 的 `results` 非空、Fetch 返回正文）；请求失败、无结果、超时不计费；`count` 不影响价格 | 官方文档「计费」段 |
| F-029 | 限速按**账号粒度**计算，与用哪个 API Key 无关，与模型并发限制相互独立：Search **100 QPS**、Fetch **25 QPS**，两者互不占用额度；超过账号级限制返回 429；**Fetch 另有目标域名级 QPS 限制**（官方未公布具体数值），超过也返回 429 | 官方文档「限速」段 |
| F-030 | **2026-11-01 00:00（北京时间）**起，当前用户在 DeepSeek Harness / Claude Code / Codex 中使用 DeepSeek API 时经 Server 端工具调用访问到 Search/Fetch 的这部分调用也按次计费 | 官方文档「计费」段末 |
| F-031 | 质量自宣只覆盖索引规模（千亿级网页）、多语言、实时返回与过滤机制；**未提供召回率、时延或与主流搜索引擎的对比数据** | 仓库内 deepseek-v41-flash-1017 束「引用边界」第 1 条 |
| F-032 | **无状态**：Search 与 Fetch 每次调用独立，不保存语料、不提供跨会话记忆或任何持久化检索层 | 官方文档全文（无相关端点与状态说明） |
| F-033 | Fetch 面向**目标站点**与反爬策略，因此同一 URL 在不同来源（公开接口 vs 站点直连）可能得到不同结果 | 由 F-023、F-026 推出——**本条为对照推论，非官方原文** |

## C 组：对照与综合

| 编号 | 事实 | 来源 |
|---|---|---|
| F-034 | **语料归属是第一决策轴**：问「我们内部昨晚那次 CI 失败日志里写了什么」——DeepSeek 侧结构上做不到（它不索引私有日志，F-032）；问「今天 Rust 发布了什么新特性」——XERJ 侧结构上做不到（它只索引本地文件，F-001） | F-001、F-032 的直接推论 |
| F-035 | 两者的上下文成本控制遵循**同一思想的不同实现**：都是「先给摘要、按需再给全文」——XERJ 是 `_passage` 服务端切片 + `_source` 投影（F-004、F-005）；DeepSeek 是 `snippet`/`summary`/`content` 三档 + `need_content` 默认 false（F-019、F-024） | F-004、F-005、F-019、F-024 |
| F-036 | 两者的成本曲线形状相反：DeepSeek 线性于成功请求数且**惩罚重复查询**（F-028）；XERJ 是固定成本、边际近零（F-010） | F-010、F-028 |
| F-037 | 深研型任务里 Search/Fetch 费用已与 token 费**同量级**：50 轮 × 2 次/轮 = ¥0.50；50 轮 × 4 次/轮 = ¥1.00（对比同仓 1017 max 档单任务约 ¥1.3） | 仓库内 deepseek-v41-flash-1017 束 03 搜索 API 篇 §5；同束 01 成本篇 §2 |
| F-038 | **失败可诊断性存在实质差距**：XERJ 把边界编码进响应体与错误码（F-006、F-007、F-008、F-009）；DeepSeek 的 404 把五种成因合并（F-026），Agent 无法区分「页面不存在」与「被站点策略拦截」——而这两者需要完全不同的反应 | F-006～F-009、F-026 |
| F-039 | 两者的质量自宣方式不同：XERJ 附测量条件、失败案例与复现脚本（F-012、F-015）；DeepSeek 只给规模与机制描述，不给可对比的召回/时延数据（F-031） | F-012、F-015、F-031 |
| F-040 | **两者可串联而非二选一**：Search 定位「该看哪个页面」→ Fetch 取正文 → 写入 XERJ 索引 → 之后用 XERJ 查（重复的公网检索被本地命中替代，F-036 的成本结论直接支持这一路径） | 由 F-028、F-036、F-010 组合推出的**架构建议**——非任一方的官方表述 |
| F-041 | 两者的隐私边界方向相反：XERJ 默认数据不出机器（F-011），DeepSeek 的检索词与目标 URL **必然出网**（F-016、F-022） | F-011、F-016、F-022 |
| F-042 | 两者的规模上限来源不同：XERJ 受本机磁盘与内存约束（F-013）；DeepSeek 受其自有索引覆盖与账号级 QPS 约束（F-016、F-029） | F-013、F-016、F-029 |

## 核验备注

| 编号 | 备注 |
|---|---|
| F-017 | 本轮在线官方文档页未展开过滤机制段（该段在官方公告与仓库内束中）；**本条按仓库内既有束的官方引述保留，标注为「官方公告口径」而非「本轮在线复核」** |
| F-031 | 同上：质量自宣的「未提供对比数据」是**缺失性断言**，依据是官方文档全文与定价页均无相关数据 |
| F-033 | **对照推论**，非官方原文；引用时须标注推论属性 |
| F-040 | **架构建议**，由三条事实组合推出；两侧均无官方表述支持或反对 |

## 相关参考

- [信源登记](source.md)：三类信源与本轮核验清单
- [核验记录](verification.md)：核验方法与结论
- [References 索引](index.md)：本目录汇总
