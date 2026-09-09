---
type: reference
title: QAnything 架构洞察（I 阶段）
description: 基于 QAnything 60 条源码事实（F-qa-001~060）综合分析的 RAG 系统架构洞察与 concepts/ 知识地图
tags: [qanything, rag, netease-youdao, architecture, insights]
generated: { by: okf-wiki/0.2, at: 2026-09-09 }
phase: I（架构洞察，Task 8）
baseline: v2.0.0 后 HEAD @ 615417a
status: stable
verified: { by: "process:seven-concepts-v-fix", at: "2026-09-09" }
stale_after: 2027-09-09
sources:
  - resource: vendor/netease-youdao/QAnything/
  - resource: /references/facts.md
---

# QAnything 架构洞察

> 本文是 I 阶段（架构洞察）产出，基于 `references/facts.md` 的 60 条零推测事实（F-qa-001~060），提炼网易有道 QAnything v2.0.0 基线的核心架构洞察，并规划 `concepts/` 知识地图。事实编号与证据位置以 facts.md 为准。

## 核心架构洞察

### 洞察一：问答链路上散布着一组硬编码阈值，构成"隐性召回契约"

**陈述**：`LocalDocQA.get_knowledge_based_answer()` 的召回质量由一组未入配置、直接硬编码在方法体内的魔数共同决定：rerank 分数 < 0.28 的文档剔除、相邻 rerank 分数相对差 > 0.5 时截断后续文档、FAQ 条目相关性 ≥ 0.9（或 question 完全匹配）时跳过 LLM 直接返回答案、且仅当 query token 数 ≤ 300 时才触发 rerank。

**证据**：F-qa-003（rerank 0.28 剔除 + 相对差 0.5 截断）、F-qa-004（FAQ 相似度 0.9 短路）、F-qa-005（rerank 触发条件 `num_tokens_rerank(query) <= 300`）、F-qa-009（`get_rerank_results()` 内再次硬编码 0.28）。

**反常识**：与"阈值应集中在配置文件"的直觉相反，这些决定回答质量的关键数字散落在编排方法体内，且 0.28 在 `get_knowledge_based_answer` 与 `get_rerank_results` 两处重复出现——同一生效阈值有两个维护点，存在漂移风险。更反直觉的是 rerank 的"门槛前置"设计：query 超过 300 tokens 时整个 rerank 阶段被跳过，此时最终排序退化为向量检索原始顺序，长问题用户 silently 得到更弱的召回，而 API 入参中的 `rerank` 开关（F-qa-038）并不能覆盖这一隐性行为。

**行动**：接入或魔改 QAnything 时，调参不能只改 `model_config.py`——必须先全文检索 `local_doc_qa.py` 中的字面量阈值；若做二次开发，应将 0.28/0.5/0.9/300 提取为配置项并消除重复定义；评估长 query 场景时须意识到 rerank 可能未生效，需单独验证。

---

### 洞察二：父子切分（parent 800 / child 400）以"小块召回、大块阅读"换取精度与上下文的兼得

**陈述**：`ParentRetriever` 默认 parent chunk 800、child chunk 400，parent 块 chunk_overlap 为 0、child 块 chunk_overlap 恒为 child 尺寸的 1/4（默认 100）；`SelfParentRetriever.aadd_documents()` 执行两级切分，child 文档带 `[headers]` 前缀元数据写入 Milvus/Elasticsearch 双索引，parent 全文则存入 MySQL（`MysqlStore`）；检索时以 child 命中定位、再回填 parent 内容进入上下文。

**证据**：F-qa-010（默认切分参数与按请求动态重建 splitter）、F-qa-011（两级切分 + `[headers]` 前缀 + 双写 + MysqlStore parent docstore）、F-qa-012（Milvus similarity 检索 child，`hybrid_search` 时合并 ES 结果去重）、F-qa-016（`MysqlStore.mget()` 展开 parent，FAQ 展开为 `question：answer`）、F-qa-025（`DEFAULT_PARENT_CHUNK_SIZE=800`、`DEFAULT_CHILD_CHUNK_SIZE=400`、SEPARATORS 列表）。

**反常识**：直觉上"embedding 的 chunk 越小越精确、越大上下文越完整"是不可兼得的取舍，但 QAnything 的解法不是调一个中间值，而是**让两个 chunk 尺寸各司其职**——400 的 child 负责向量空间的精确命中，800 的 parent 负责给 LLM 提供完整语义。另一个容易被忽略的细节是 parent 块 overlap 为 0、child 块 overlap 固定为 child 尺寸的 1/4，即调大 child 会同时增大冗余量；且 child 元数据里的 `[headers]` 前缀与页内容的 `![figure]`/`![equation]` 过滤（F-qa-018）说明 embedding 输入经过了专门的"文本净化"预处理。

**行动**：复刻该策略时，child/parent 比例（1:2）与 child overlap=child/4 是起点而非教条，应按 embedding 模型的 max_length（本项目 512，F-qa-024）约束 child 上限；入库链路必须保证 child 命中 → parent 回填的双写一致性，删除文件时需同步清理 Milvus/ES/MySQL 三处（F-qa-015 的 ES 逐条删除即为例证）。

---

### 洞察三：以 `kb_id` 为 partition key 的 Milvus 集合，把多租户隔离下推到向量库分区层

**陈述**：`VectorStoreMilvusClient` 以 `partition_key_field="kb_id"` 构建单一集合（`qanything_collection_240625`），所有知识库共用一个 collection，按知识库 id 自动路由分区（`num_partitions=64`），检索表达式为 `kb_id in [...]`；知识库的删除/隔离不删集合结构，而是按 partition key 过滤。

**证据**：F-qa-013（`partition_key_field="kb_id"`、auto_id、ef=64）、F-qa-014（`flush_interval=600s`/`flush_threshold=10000` 缓冲落盘、`_create_collection()` 建 64 分区集合）、F-qa-012（检索 expr 为 `kb_id in [...]`）、F-qa-036（kb_id 生成规则：`'KB' + uuid.uuid4().hex`，quick 模式加 `_QUICK` 后缀）、F-qa-023（`MILVUS_COLLECTION_NAME`、阈值常量集中区）。

**反常识**：常见的多租户做法是"每租户一 collection"，而 QAnything 反其道而行——**单集合 + partition key**，分区数固定 64。这意味着分区是哈希路由而非"一个知识库一个分区"，知识库数量远多于 64 时多个 kb_id 会共享物理分区，隔离是逻辑级的而非物理级的。另一个工程细节：缓冲落盘参数（600 秒或 1 万条才 flush）意味着刚入库的文档在向量库中并非立即可检索，与"上传立即可问"的用户预期存在时间窗。

**行动**：评估数据安全需求时须明确这是逻辑隔离——若要求物理级租户隔离需改造为分 collection 方案；性能调优时关注 64 分区的上限约束（知识库规模增长后哈希不均的尾部延迟）；排查"文件已入库但检索不到"时应先检查 flush 缓冲窗口与文件状态机（gray/yellow/green/red，F-qa-042）而非向量库配置。

---

### 洞察四：推理与解析能力被拆为五个独立本地服务进程，由 shell 脚本编排成单体部署

**陈述**：embedding（9001）、rerank（8001）、ocr（7001）、pdf_parser（9009）、insert_files（8110）五个 Sanic 微服务各自独立进程运行，主 API 服务（8777）通过 `model_config.py` 中的 localhost URL 常量以 HTTP 调用它们；`entrypoint.sh` 以 nohup 依次拉起全部 6 个进程、PID 写入自动生成的 `close.sh`，并以轮询日志中 `"Starting worker"` 字符串作为就绪判据。

**证据**：F-qa-024（四个 LOCAL_*_SERVICE_URL 常量与 512 max_length）、F-qa-028~F-qa-032（五个 dependent_server 的路由、端口、推理后端 ONNX/设备选择、MySQL 轮询入库）、F-qa-045（entrypoint 六进程编排与 180 秒启动超时）、F-qa-047（memory_usage.sh 按进程统计 RSS）、F-qa-057~F-qa-059（compose 中基础设施服务与主容器关系）。

**反常识**：服务名为"微服务"，实际是**共享单机生命周期的进程组**——服务间是裸 HTTP + localhost 的紧耦合，没有服务发现、没有健康检查端点注册、没有进程守护（nohup + PID 文件即全部容错）。就绪判据"日志中出现 Starting worker"（而非 HTTP 健康探测）在日志格式变更时会静默失效，180 秒超时会直接报错退出整个容器。另一个矛盾点：`local_doc_chat` 支持传入任意 `api_base` 对接外部 LLM（F-qa-038），但 embedding/rerank 等核心推理却被钉死在 localhost 常量上——**LLM 可外置，检索能力不可外置**。

**行动**：部署到生产前需自行补齐进程守护（systemd/supervisor）与健康检查；水平扩展时这五服务与主 API 的 1:1 进程假设是主要障碍，需要先把 LOCAL_* URL 常量改为可配置的服务发现地址；内存规划可参考 `memory_usage.sh` 的六进程 RSS 口径（F-qa-047）。

---

### 洞察五：失效导入与版本错位的部署工件，揭示了一条从"单机 FAISS"到"服务化 Milvus"的演进轨迹

**陈述**：`connector/database/faiss/faiss_client.py` 与 `connector/database/milvus/milvus_client.py` 两个模块导入了 `model_config.py` 中根本不存在的名称（`FAISS_LOCATION`、`FAISS_CACHE_SIZE`、`MILVUS_HOST_ONLINE`、`CHUNK_SIZE`），且全仓无任何文件 import 它们——是被新架构绕过的死代码；同时部署工件存在版本错位：git 基线为 v2.0.0 之后，但 docker-compose 主镜像仍钉在 `xixihahaliu01/qanything-*:v1.5.1`。

**证据**：F-qa-027（四个失效导入名称 + Grep 全仓验证无引用）、F-qa-013/F-qa-015（RAG 主链路实际使用 `core/retriever/vectorstore.py` 与 `elasticsearchstore.py`）、F-qa-023（集合名/索引名带 `240625` 日期戳）、F-qa-058（三平台镜像 tag v1.5.1）、F-qa-053（前端 package version 2.0.4）、F-qa-060（compose 固定 Milvus v2.4.8、ES 8.13.2、MySQL 8.4 版本组合）。

**反常识**：代码库中"看起来可用的模块"恰恰是最不可信的——两个 database connector 模块语法完整、类结构齐全，但一运行即 ImportError。这提示**源码证据必须区分"存在"与"可达"**：只有被主链路 import 的模块才反映真实架构。版本错位也违反直觉：语义化版本里 v2.0.0 应晚于 v1.5.1，但 compose 镜像、前端版本、git tag 三者各说各话，说明版本号并非单一来源驱动，部署时不能假定"git checkout 最新 = 运行最新"。

**行动**：以本仓库为学习/改造对象时，应以 F-qa-027 为戒建立"可达性验证"步骤（对疑似死代码执行 import 测试或反向引用检索）；阅读 QAnything 源码应跳过 `connector/database/` 下这两个遗留模块，直接从 `core/retriever/` 入手；自行部署时不要直接使用仓库自带 compose 的镜像 tag，需核对镜像内容与 git 基线的一致性。

---

## 设计概念文档知识地图

基于以上洞察，`concepts/` 规划 8 个概念文档（00-07），按"入门 → 核心 → 进阶"三组编排，形成由浅入深的学习路径。文档使用 `/` 开头的 bundle-relative 交叉链接。

### 分组与依赖结构

```
入门（建立心智模型）
  00-overview ──→ 01-quick-start
核心（深挖 RAG 内核）
  02-rag-pipeline ──→ 03-retrieval ──→ 04-storage-multitenancy
  05-dependent-servers ──→ 06-api-ops
进阶（主题深化）
  07-evolution-traces
```

### 入门组

**00-overview · QAnything 全景：六进程 RAG 应用架构**（前置：无）
- 一句话概要：一页看懂 QAnything——前端 Vue + Sanic API 主服务 + 五个本地推理/解析服务进程 + Milvus/ES/MySQL 三存储的系统全景图。
- 引用事实：F-qa-001、F-qa-002、F-qa-028~F-qa-033、F-qa-034、F-qa-045、F-qa-057、F-qa-059
- 前置依赖：无。被全部后续文档引用。

**01-quick-start · 部署与最小问答闭环**（前置：00）
- 一句话概要：从 docker-compose 到 `local_doc_chat` 首次问答的端到端走查，含文件状态机与 SSE 流式响应的观察方法。
- 引用事实：F-qa-038、F-qa-039、F-qa-042、F-qa-048、F-qa-049、F-qa-056~F-qa-060
- 前置依赖：00。

### 核心组

**02-rag-pipeline · LocalDocQA 问答编排链与硬编码阈值**（前置：00、01）
- 一句话概要：逐帧拆解 `get_knowledge_based_answer()` 生成器——问题改写、检索、rerank 过滤、prompt 组装、SSE 输出——并剖析 0.28/0.5/0.9/300 阈值集群的工程含义。
- 引用事实：F-qa-002~F-qa-009、F-qa-017、F-qa-020、F-qa-021
- 前置依赖：00、01。为 03（检索）与 07（演进）提供编排层上下文。

**03-retrieval · 父子切分与 Milvus/ES 混合检索**（前置：02）
- 一句话概要：parent 800/child 400 两级切分、child 双写向量/文本索引、parent 落 MySQL 回填的完整检索增强链路，以及 hybrid_search 合并去重机制。
- 引用事实：F-qa-010~F-qa-016、F-qa-018、F-qa-019、F-qa-023、F-qa-025
- 前置依赖：02。

**04-storage-multitenancy · Milvus 分区多租户与三存储分层**（前置：03）
- 一句话概要：单集合 + `kb_id` partition key 的多租户隔离设计、64 分区与缓冲落盘参数，以及 Milvus（向量）/Elasticsearch（文本）/MySQL（结构化）三层存储的职责划分。
- 引用事实：F-qa-013、F-qa-014、F-qa-015、F-qa-016、F-qa-022、F-qa-023、F-qa-036
- 前置依赖：03。

**05-dependent-servers · 依赖服务化：五个本地推理/解析进程**（前置：00）
- 一句话概要：embedding/rerank/ocr/pdf_parser/insert_files 五服务的接口契约、ONNX 推理后端与设备选择，以及 entrypoint 进程编排的就绪判定与运维要点。
- 引用事实：F-qa-024、F-qa-028~F-qa-033、F-qa-045、F-qa-046、F-qa-047
- 前置依赖：00。与 04 并列支撑 02 的"服务依赖"视角。

**06-api-ops · API 层、Bot 配置与知识库运维**（前置：01）
- 一句话概要：28 条路由的四大功能组（知识库/文件/Bot/问答）、`user_id__user_info` 标识拼接、Bot LLM 参数 JSON 配置与 gray→green 文件状态机的运维语义。
- 引用事实：F-qa-034~F-qa-043、F-qa-037、F-qa-040、F-qa-041
- 前置依赖：01。

### 进阶组

**07-evolution-traces · 演进痕迹：死代码、失效导入与版本错位**（前置：02、04）
- 一句话概要：以 faiss/milvus 死模块、集合名日期戳与 compose 镜像版本错位为线索，还原 QAnything 从单机 FAISS 到服务化 Milvus 的架构演进，并建立"模块可达性验证"的阅读方法论。
- 引用事实：F-qa-027、F-qa-013、F-qa-015、F-qa-023、F-qa-053、F-qa-058
- 前置依赖：02、04（需先理解真实主链路，才能识别绕行痕迹）。

### 学习路径说明

- **推荐顺序**：00 → 01 → 02 →（03 → 04）与 05 并行 → 06 → 07。
- **若目标是接入使用**：以 00/01/06 为主，辅以 02 理解问答行为。
- **若目标是二次开发/架构借鉴**：完整走 02→07，重点消化洞察一（阈值治理）与洞察四（服务化边界）。

## 相关引用

- 本文件事实来源：`/references/facts.md`（F-qa-001~060）
- 信源登记：`/references/sources.md`
- 待生成文档路径：`concepts/00-overview.md` ~ `concepts/07-evolution-traces.md`（见上文知识地图）
