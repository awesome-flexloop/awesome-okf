# 概念文档

QAnything 核心架构概念，共 8 篇，按"全景 → 部署 → 编排 → 检索 → 存储 → 服务化 → API → 演进"的认知顺序组织。

## 系统全景与部署

* [00 QAnything 全景——六进程 RAG 应用架构](00-overview.md) — Vue 前端、Sanic 主服务、五个本地推理/解析进程与 Milvus/ES/MySQL 三存储的分工协作，建立完整心智模型。
* [01 部署与最小问答闭环](01-quick-start.md) — docker-compose 启动、entrypoint 拉起 6 进程、模型软链接、"Starting worker" 就绪判定与首次问答验证。

## 问答编排与检索

* [02 LocalDocQA 问答编排链与硬编码阈值](02-rag-pipeline.md) — get_knowledge_based_answer() 生成器逐帧拆解，0.28/0.5/0.9/300 阈值集群的工程含义与治理建议。
* [03 父子切分与 Milvus/ES 混合检索](03-retrieval.md) — parent 800/child 400 两级切分、"小块召回、大块阅读"、child 双写索引与 hybrid_search 合并去重。

## 存储与服务化

* [04 Milvus 分区多租户与三存储分层](04-storage-multitenancy.md) — 单集合 + kb_id partition key、64 分区、三层存储职责划分与跨库一致性。
* [05 依赖服务化——五个本地推理/解析进程](05-dependent-servers.md) — embedding/rerank/ocr/pdf_parser/insert_files 接口契约、ONNX 后端与 entrypoint 进程编排。
* [06 API 层、Bot 配置与知识库运维](06-api-ops.md) — 28 条路由四大功能组、user_id__user_info 标识、Bot LLM 参数 JSON 与 gray→green 状态机。

## 演进考古

* [07 演进痕迹——死代码、失效导入与版本错位](07-evolution-traces.md) — faiss/milvus 死模块、集合名日期戳与 compose 镜像版本错位，还原单机 FAISS 到服务化 Milvus 的演进轨迹。

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-quick-start
02-rag-pipeline
03-retrieval
04-storage-multitenancy
05-dependent-servers
06-api-ops
07-evolution-traces
```
