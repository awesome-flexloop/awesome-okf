---
type: concept
title: "可插拔基础设施架构"
description: "Coze Studio 基础设施层的多后端可插拔设计：MQ、向量库、存储、嵌入、OCR、解析器、重排序、LLM 的工厂模式与云端/私有部署适配"
tags: [可插拔, 基础设施, 工厂模式, 多后端, 部署架构]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-090
    resource: /references/deployment-infrastructure.md
    title: "5 MQ / 3 VectorStore / 3 Storage / 5 Embedding 选项"
  - id: F-cs-115
    resource: /references/deployment-infrastructure.md
    title: "searchstore 4 后端工厂模式"
---

# 可插拔基础设施架构

Coze Studio 的 infra/ 层采用高度可插拔的架构设计，几乎所有基础设施组件都支持多种后端实现。通过工厂模式和接口抽象，平台可以在不修改业务代码的情况下切换底层基础设施，从默认的全本地开源栈（MinIO/Milvus/NSQ）平滑迁移到云服务（火山引擎 TOS/VikingDB/Ark）或其他兼容实现。这种设计使 Coze Studio 既能一键本地部署，也能接入企业已有的云基础设施。

## 可插拔全景图

```
┌──────────────────────────────────────────────────────────────────────┐
│                     应用层 (application/)                            │
│           业务逻辑通过统一接口调用基础设施能力                         │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ 接口抽象
┌──────────────────────────────┼───────────────────────────────────────┐
│                    infra/ 基础设施层                                  │
│  ┌─────────────────────────┴─────────────────────────────────────┐  │
│  │                     工厂模式注册中心                            │  │
│  └──┬──────────┬──────────┬──────────┬──────────┬───────────────┘  │
│     ▼          ▼          ▼          ▼          ▼                   │
│  ┌──────┐ ┌────────┐ ┌───────┐ ┌───────┐ ┌──────────┐              │
│  │  MQ  │ │VectorDB│ │Storage│ │Embed  │ │SearchStore│              │
│  │(5选1)│ │ (3选1) │ │(3选1) │ │(5选1) │ │  (4选1)  │              │
│  └──┬───┘ └───┬────┘ └──┬────┘ └──┬────┘ └────┬─────┘              │
│     │         │         │         │           │                     │
│  ┌──┴──┐   ┌──┴──┐   ┌──┴──┐   ┌──┴──┐     ┌──┴────┐               │
│  │NSQ  │   │Mil-│   │MinIO│   │Ark  │     │Elastic│               │
│  │Kafka│   │vus │   │TOS  │   │Ope- │     │search │               │
│  │Roc- │   │Vik-│   │S3   │   │nAI  │     │Milvus │               │
│  │ketMQ│   │ing-│   │     │   │Olla-│     │Ocean- │               │
│  │Pul- │   │DB  │   │     │   │ma   │     │Base   │               │
│  │sar  │   │Ocea│   │     │   │Gemi-│     │Viking │               │
│  │NATS │   │nBa│   │     │   │ni   │     │DB     │               │
│  └─────┘   │se  │   │     │   │HTTP │     └───────┘               │
│            └────┘   └─────┘   └─────┘                             │
│                                                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐                                        │
│  │ OCR  │ │Parser│ │Rerank│  ← 文档处理组件                         │
│  │(2选1)│ │(2选1)│ │(2选1)│                                        │
│  │VE/Pad│ │Bui- │ │Vik/  │                                        │
│  │dleocr│ │ltin/│ │RRF   │                                        │
│  │      │ │Pad- │ │      │                                        │
│  │      │ │dle  │ │      │                                        │
│  └──────┘ └─────┘ └──────┘                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## 消息队列（EventBus）— 5 选项

事件总线模块（`infra/eventbus/`）支持 5 种消息队列后端，用于系统内部的异步事件驱动：

| 后端 | 依赖库 | 默认 | 适用场景 |
|------|--------|------|----------|
| **NSQ** | `nsqio/go-nsq v1.1.0` | ✅ 默认 | 本地部署、简单场景 |
| **Kafka** | `IBM/sarama v1.45.1` | — | 大规模生产、高吞吐 |
| **RocketMQ** | `apache/rocketmq-client-go/v2` | — | 阿里云/企业级部署 |
| **Pulsar** | — | — | 云原生消息平台 |
| **NATS (JetStream)** | — | — | 轻量级云原生消息 |

Docker Compose 默认启动 NSQ 三件套（nsqlookupd:4160/4161、nsqd:4150/4151、nsqadmin:4171），开箱即用。切换到其他 MQ 只需修改环境变量，无需改代码。

## 向量数据库（VectorStore）— 3 选项

向量存储用于知识库的语义检索和 Agent 记忆的向量查询：

| 后端 | 默认 | 适用场景 |
|------|------|----------|
| **Milvus** v2.5.10 standalone | ✅ 默认 | 开源向量数据库，本地/私有部署 |
| **VikingDB** | — | 火山引擎向量数据库服务 |
| **OceanBase** | — | OceanBase 原生向量能力 |

Docker Compose 默认启动 Milvus standalone 模式，依赖 etcd（元数据存储）和 MinIO（对象存储）。Milvus 容器配置了 `seccomp:unconfined` 以确保向量计算的正常运行。

## 对象存储（Storage）— 3 选项

文件存储模块（`infra/storage/`）使用统一的 Storage 接口，支持三种对象存储后端：

| 后端 | 依赖库 | 默认 | 适用场景 |
|------|--------|------|----------|
| **MinIO** | `minio-go/v7 v7.0.90` | ✅ 默认 | 本地 S3 兼容存储 |
| **TOS** | `ve-tos-golang-sdk/v2 v2.7.17` | — | 火山引擎 TOS |
| **S3** | `aws-sdk-go-v2/service/s3 v1.84.1` | — | AWS S3 兼容存储 |

每种后端在 `infra/storage/impl/` 下有独立实现：`minio/`、`tos/`、`s3/`。MinIO 启动时自动创建 `opencoze` 和 `milvus` 两个 bucket，并复制默认图标资源。

## 向量嵌入（Embedding）— 5 选项

文档向量化是知识库 RAG 流程的核心环节：

| 后端 | 默认 | 说明 |
|------|------|------|
| **Ark** | ✅ 默认 | 火山引擎方舟嵌入模型 |
| **OpenAI** | — | OpenAI text-embedding 系列 |
| **Ollama** | — | 本地 Ollama 嵌入模型 |
| **Gemini** | — | Google Gemini 嵌入 |
| **HTTP** | — | 自定义 HTTP 嵌入接口 |

通过 `MODEL_PROTOCOL_N` 序号后缀模式配置多个模型实例，详见 [LLM 集成](05-llm-integration.md)。

## OCR — 2 选项

光学字符识别用于提取图片和扫描文档中的文本：

| 后端 | 默认 | 说明 |
|------|------|------|
| **VE (火山引擎 OCR)** | ✅ 默认 | 云端 OCR 服务 |
| **PaddleOCR** | — | 开源本地 OCR 引擎 |

## 文档解析器（Parser）— 2 选项

文档解析负责将 PDF、DOCX 等格式文件解析为纯文本：

| 后端 | 默认 | 说明 |
|------|------|------|
| **builtin** | ✅ 默认 | 内置解析器（Python 脚本，后端 Docker 内预装 pdfplumber、python-docx 等） |
| **PaddleOCR** | — | 使用 PaddleOCR 进行文档解析 |

后端 Docker 镜像中内置了 Python 3 venv 环境和文档处理脚本（`parse_pdf.py`、`parse_docx.py`、`sandbox.py`），并通过 Deno 预初始化了 Pyodide Python 沙箱。

## 重排序（Rerank）— 2 选项

检索结果重排序提升 RAG 的检索精度：

| 后端 | 默认 | 说明 |
|------|------|------|
| **RRF** (Reciprocal Rank Fusion) | ✅ 默认 | 无模型依赖的排序融合算法 |
| **VikingDB** | — | VikingDB 内置重排序能力 |

## 搜索存储（SearchStore）— 4 选项

`infra/document/searchstore` 模块使用工厂模式注册 4 种搜索后端：

| 后端 | 注册方式 |
|------|----------|
| **Elasticsearch** | go-elasticsearch v7 + v8 双版本支持 |
| **Milvus** | 向量搜索 |
| **OceanBase** | 混合搜索 |
| **VikingDB** | 火山引擎搜索服务 |

工厂模式使得新增搜索后端只需实现接口并注册，不影响调用方代码。Elasticsearch 在 Docker Compose 中默认使用 `bitnamilegacy/elasticsearch:8.18.0`，预装 analysis-smartcn 中文分词插件，启动时自动初始化索引 schema。

## 数据库与缓存

| 组件 | 技术 | 说明 |
|------|------|------|
| 关系数据库 | MySQL 8.4.5（GORM） | utf8mb4 字符集，Atlas CLI 管理 schema 迁移；可选 OceanBase |
| 缓存 | Redis 8.0（go-redis/v9 v9.7.3） | AOF 禁用，4 IO 线程，Docker Compose 默认无密码 |
| 配置中心 | etcd 3.5 | revision 自动压缩(keep 1000)，4GB quota |

## 工厂模式实现

Coze Studio 的可插拔架构主要通过以下 Go 设计模式实现：

1. **接口定义**：每个基础设施模块在根目录定义接口（如 `infra/storage/storage.go` 中的 Storage 接口）
2. **工厂注册**：各实现在 `init()` 函数中通过工厂方法注册自身
3. **配置驱动**：通过 `.env` 中的配置项决定使用哪个实现
4. **依赖注入**：应用初始化时根据配置实例化具体实现，注入到跨域契约层

以搜索存储为例，四个后端实现都遵循相同接口，通过工厂注册后，上层代码无需感知底层使用的是 ES 还是 Milvus。

## 云端 vs 私有部署

可插拔架构天然支持两种部署模式：

| 部署模式 | MQ | VectorStore | Storage | Embedding | OCR |
|----------|-----|-------------|---------|-----------|-----|
| **本地/Docker** | NSQ | Milvus | MinIO | Ollama/Ark | PaddleOCR |
| **火山云** | Kafka/RMQ | VikingDB | TOS | Ark | VE |
| **AWS** | Kafka/MSK | — | S3 | OpenAI | — |
| **混合** | 任意 | 任意 | 任意 | 任意 | 任意 |

`.env.example` 包含 270+ 配置项，覆盖了所有可插拔组件的配置。切换后端通常只需要修改对应的环境变量并重启服务。

## 相关概念

- [整体架构概览](00-overview-ddd-architecture.md)
- [DDD 分层详解](01-ddd-layers.md)
- [LLM 集成](05-llm-integration.md)
- [部署与运维](08-deployment-operations.md)
- [配置基础设施示例](../examples/configure-infrastructure.md)
- [部署与基础设施参考](../references/deployment-infrastructure.md)
