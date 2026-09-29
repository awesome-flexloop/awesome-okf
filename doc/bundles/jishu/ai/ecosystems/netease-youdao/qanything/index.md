---
type: bundle
title: QAnything 本地知识库问答 RAG 系统
okf_version: "0.2"
---

# QAnything 知识库

本知识包是网易有道开源的本地知识库问答 RAG 系统 [QAnything](https://github.com/netease-youdao/QAnything)（Question and Answer based on Anything，**AGPL-3.0** 许可证）的系统化中文源码教程。勘察基线为 tag **v2.0.0** 之后的 HEAD（`git describe` 输出 `v2.0.0-69-g615417a`，即 HEAD 超前 tag 69 commits），按勘察基线 pin commit `615417a92420d77a2606392a74f5771ca2f31a4b`，源码位于只读 git submodule `vendor/netease-youdao/QAnything`。全部内容经 R（事实采集）→ I（架构洞察）→ E（示例提炼）→ V（对抗验证）→ C（概念成文）五阶段链路生成，60 条零推测源码事实（F-qa-001~060）逐条溯源至基线源码文件。

## 概念篇（concepts/）

* [QAnything 全景——六进程 RAG 应用架构](concepts/00-overview.md) — 一页看懂系统全景：Vue 前端、Sanic API 主服务、五个本地推理/解析服务进程与 Milvus/Elasticsearch/MySQL 三存储的分工与协作。
* [部署与最小问答闭环](concepts/01-quick-start.md) — 从 docker-compose 启动到 local_doc_chat 首次问答的端到端走查：六进程就绪判定（"Starting worker" 日志轮询，180 秒超时）、模型软链接与 SSE 流式响应验证。
* [LocalDocQA 问答编排链与硬编码阈值](concepts/02-rag-pipeline.md) — 逐帧拆解 get_knowledge_based_answer() 生成器（问题改写→检索→rerank 过滤→prompt 组装→SSE 输出），剖析 0.28/0.5/0.9/300 阈值集群的工程含义与治理建议。
* [父子切分与 Milvus/ES 混合检索](concepts/03-retrieval.md) — parent 800/child 400 两级切分、"小块召回、大块阅读"链路：child 双写向量/文本索引、parent 落 MySQL 回填、hybrid_search 合并去重。
* [Milvus 分区多租户与三存储分层](concepts/04-storage-multitenancy.md) — 单集合 + kb_id partition key 的多租户隔离设计、64 分区与缓冲落盘参数，Milvus（向量）/Elasticsearch（文本）/MySQL（结构化）三层职责划分与一致性维护。
* [依赖服务化——五个本地推理/解析进程](concepts/05-dependent-servers.md) — embedding/rerank/ocr/pdf_parser/insert_files 五服务的接口契约、ONNX 推理后端与设备选择，entrypoint 进程编排的就绪判定与运维要点。
* [API 层、Bot 配置与知识库运维](concepts/06-api-ops.md) — 28 条路由的四大功能组（知识库/文件/Bot/问答）、user_id__user_info 标识拼接、Bot LLM 参数 JSON 配置与 gray→green 文件状态机的运维语义。
* [演进痕迹——死代码、失效导入与版本错位](concepts/07-evolution-traces.md) — 以 faiss/milvus 死模块、集合名日期戳与 compose 镜像版本错位为线索还原架构演进，建立"模块可达性验证"的源码阅读方法论。

## 实战示例（examples/）

* [API 流式问答调用——SSE 帧解析与 LLM 参数透传](examples/api-streaming-chat.md) — 以 stream_chat.py 演练 local_doc_chat 流式调用：SSE 帧格式（`data: ` 前缀 + `[DONE]` 末帧）、增量解析与 LLM 参数透传最佳实践。
* [知识库上传与检索流程——批量入库到命中回填](examples/kb-upload-and-retrieval.md) — 以 multi_upload_files.py 演练批量上传（扩展名白名单、200MB 分批、aiohttp 并发），拆解后端入库流水线与"child 命中、parent 回填"检索链路。
* [最小问答闭环——建库、传文件、提问](examples/minimal-qa-loop.md) — 以仓库自带测试脚本为线索，走通"新建知识库 → 上传文件 → 等待入库 → 非流式问答"最小闭环，说明每步的接口与状态机语义。

## 信源与证据（references/）

* [QAnything 源码事实清单](references/facts.md) — R 阶段事实采集：60 条零推测源码事实（F-qa-001~060），逐条溯源至 vendor 基线的 20 余个核心源码文件。
* [QAnything 架构洞察](references/insights.md) — I 阶段架构洞察：基于 60 条事实提炼 5 条核心洞察（隐性召回契约、父子切分、多租户分区、服务化拆分、演进痕迹）与 concepts/ 知识地图。
* [QAnything 信源登记](references/sources.md) — 上游仓库、固定基线（v2.0.0-69-g615417a，pin commit 615417a92420d77a2606392a74f5771ca2f31a4b）、AGPL-3.0 许可证与关键信源文件登记。

## 信任与生命周期说明

* **文档总数构成**：本知识包共收录 11 篇内容文档（8 篇 concepts + 3 篇 examples），另有 3 篇 references 证据文档（facts/insights/sources）、3 个子目录 index.md、根 index.md 与 log.md。
* **status 判定依据**：全部 11 篇内容文档 frontmatter 实际 `status: stable`。内容基于对 QAnything 基线源码的逐文件阅读与事实提取（60 条源码事实 F-qa-001~060，经 seven-concepts 方法论 V 阶段 Grep 对抗验证），并于 2026-09-09 完成 V 验证修复回合（E1-E4 四处事实错误及全部传播面已按源码事实修正）后由 draft 升级为 stable。
* **stale_after 解释**：全部内容文档统一 `stale_after: 2027-09-09`（自生成日 2026-09-09 起一年）。QAnything 处于活跃演进中（基线即 v2.0.0 后 69 commits，HEAD 无新 tag 锚定），架构细节（路由、状态机、阈值魔数）可能随上游提交漂移，该日期作为保守的重新勘察节点；届时应比对上游新 tag 与 pin commit 差值决定复勘范围。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-09-09）；`verified.at` 记录 V 阶段对抗验证事件（`process:seven-concepts-v`），两者分离、可追溯。`references/sources.md` 登记固定基线与 pin commit，全部 F 编号事实的溯源依据以此为准。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
