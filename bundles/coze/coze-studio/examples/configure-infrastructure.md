---
type: example
title: "配置基础设施后端"
description: "通过环境变量切换向量数据库、对象存储、嵌入模型和消息队列等基础设施后端，适配不同部署环境"
tags: [基础设施, 配置, VectorStore, Storage, MQ, 环境变量]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-090
    resource: /references/deployment-infrastructure.md
    title: "5 MQ / 3 VectorStore / 3 Storage / 5 Embedding 选项"
  - id: F-cs-107
    resource: /references/deployment-infrastructure.md
    title: "Helm Chart MySQL/OceanBase 切换"
---

# 配置基础设施后端

Coze Studio 的基础设施层高度可插拔，通过修改 `.env` 文件中的环境变量即可切换底层组件。本指南介绍如何切换向量数据库、对象存储、嵌入模型和消息队列，以适配本地开发、云端部署或企业私有环境。

## 默认配置（本地 Docker）

默认配置使用全开源本地栈：

| 组件 | 默认后端 |
|------|----------|
| 消息队列 | NSQ |
| 向量数据库 | Milvus |
| 对象存储 | MinIO |
| 嵌入模型 | Ark（火山引擎） |
| OCR | VE（火山引擎） |
| 文档解析器 | builtin |
| 重排序 | RRF |
| 关系数据库 | MySQL 8.4 |
| 搜索引擎 | Elasticsearch 8.18 |

## 切换向量数据库（VectorStore）

### 切换到 VikingDB（火山引擎）

```bash
# 在 .env 中配置
VECTOR_STORE=vikingdb
VIKINGDB_HOST=<vikingdb-endpoint>
VIKINGDB_AK=<access-key>
VIKINGDB_SK=<secret-key>
VIKINGDB_REGION=cn-beijing
```

### 切换到 OceanBase

```bash
VECTOR_STORE=oceanbase
OB_HOST=<oceanbase-host>
OB_PORT=2881
OB_USER=root@test
OB_PASSWORD=<password>
OB_DATABASE=coze
```

使用 Helm Chart 部署时，OceanBase 可通过 values.yaml 切换：

```yaml
oceanbase:
  enabled: true  # 默认 false
```

> **注意**：切换向量数据库后，已有的向量数据不会自动迁移，需要重新索引知识库文档。

## 切换对象存储（Storage）

### 切换到 AWS S3

```bash
STORAGE_TYPE=s3
S3_ENDPOINT=https://s3.amazonaws.com
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=<access-key-id>
S3_SECRET_ACCESS_KEY=<secret-access-key>
S3_BUCKET=coze-studio
```

### 切换到火山引擎 TOS

```bash
STORAGE_TYPE=tos
TOS_ENDPOINT=https://tos-cn-beijing.volces.com
TOS_REGION=cn-beijing
TOS_ACCESS_KEY=<access-key>
TOS_SECRET_KEY=<secret-key>
TOS_BUCKET=coze-studio
```

切换存储后端后，需要手动创建对应 bucket，并迁移已有文件。默认的 MinIO 会自动创建 `opencoze` 和 `milvus` 两个 bucket。

## 切换嵌入模型（Embedding）

### 切换到 OpenAI Embedding

```bash
EMBEDDING_PROTOCOL=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-xxxxxxxxxxxxxxxx
EMBEDDING_BASE_URL=https://api.openai.com/v1
```

### 切换到 Ollama 本地嵌入

```bash
# 先在 Ollama 中拉取嵌入模型
ollama pull nomic-embed-text

# .env 配置
EMBEDDING_PROTOCOL=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=http://host.docker.internal:11434/api
```

### 切换到自定义 HTTP 嵌入服务

```bash
EMBEDDING_PROTOCOL=http
EMBEDDING_BASE_URL=http://your-embedding-service:8080/embed
EMBEDDING_MODEL=your-model-name
```

## 切换消息队列（EventBus）

### 切换到 Kafka

```bash
EVENTBUS_TYPE=kafka
KAFKA_BROKERS=kafka-1:9092,kafka-2:9092
KAFKA_TOPIC=coze-events
```

### 切换到 RocketMQ

```bash
EVENTBUS_TYPE=rmq
ROCKETMQ_NAMESRV=namesrv:9876
ROCKETMQ_TOPIC=coze-events
ROCKETMQ_PRODUCER_GROUP=coze-producer
```

> **注意**：如果使用 Docker Compose，默认只启动 NSQ。切换到其他 MQ 需要自行部署对应的服务或修改 `docker-compose.yml`。Helm Chart 部署时可通过 values.yaml 配置。

## 切换 OCR 和文档解析器

### OCR 切换到 PaddleOCR

```bash
OCR_TYPE=paddleocr
```

PaddleOCR 为本地开源 OCR，无需云端 API。

### 文档解析器

```bash
# 使用内置解析器（默认）
PARSER_TYPE=builtin

# 使用 PaddleOCR 解析
PARSER_TYPE=paddleocr
```

## 切换重排序（Rerank）

```bash
# 使用 RRF（默认，无模型依赖）
RERANK_TYPE=rrf

# 使用 VikingDB 重排序
RERANK_TYPE=vikingdb
```

## 切换搜索存储（SearchStore）

搜索存储支持 4 种后端（通过工厂模式注册）：

```bash
# Elasticsearch（默认）
SEARCH_STORE=elasticsearch

# Milvus 向量搜索
SEARCH_STORE=milvus

# OceanBase 混合搜索
SEARCH_STORE=oceanbase

# VikingDB
SEARCH_STORE=vikingdb
```

## 完整私有部署配置示例

以下是使用全本地/开源组件的私有部署配置：

```bash
# === 基础设施 ===
# 消息队列：NSQ（Docker 默认已包含）
EVENTBUS_TYPE=nsq

# 向量数据库：Milvus（Docker 默认已包含）
VECTOR_STORE=milvus

# 对象存储：MinIO（Docker 默认已包含）
STORAGE_TYPE=minio

# 嵌入模型：Ollama 本地
EMBEDDING_PROTOCOL=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=http://host.docker.internal:11434/api

# LLM：Ollama 本地
MODEL_PROTOCOL_0=ollama
MODEL_ID_0=llama3
MODEL_API_KEY_0=
MODEL_NAME_0=Llama3 Local
MODEL_BASE_URL_0=http://host.docker.internal:11434/v1

# OCR：PaddleOCR 本地
OCR_TYPE=paddleocr

# 文档解析：内置
PARSER_TYPE=builtin

# 重排序：RRF（无依赖）
RERANK_TYPE=rrf

# 搜索存储：Elasticsearch（Docker 默认已包含）
SEARCH_STORE=elasticsearch

# === 注册控制 ===
# 仅允许特定邮箱注册
ALLOW_REGISTRATION_EMAIL=admin@example.com
```

## 应用配置

修改 `.env` 后，需要重启后端服务使配置生效：

```bash
# Docker Compose 环境
docker compose -f docker/docker-compose.yml restart coze-server

# 如果修改了基础设施相关配置（如切换了数据库/存储），可能需要重启整个栈
make down && make web
```

## 验证配置

1. 检查后端日志确认组件连接成功：
```bash
docker compose -f docker/docker-compose.yml logs coze-server | grep -i "error\|fail\|connect"
```

2. 在 Web 界面中测试核心功能：
   - 创建智能体并对话（验证 LLM 配置）
   - 上传文档到知识库（验证 Storage、Embedding、SearchStore 配置）
   - 执行工作流（验证 EventBus 配置）

## 相关文档

- [可插拔基础设施](/concepts/04-pluggable-infrastructure.md)
- [部署与运维](/concepts/08-deployment-operations.md)
- [添加 LLM 模型](/examples/add-llm-model.md)
- [Docker 快速入门](/examples/docker-quickstart.md)
- [部署与基础设施参考](/references/deployment-infrastructure.md)
