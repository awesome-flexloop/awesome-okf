---
type: reference
title: "部署与基础设施参考"
description: "Coze Studio Docker Compose 11 服务编排、可插拔基础设施选项、Helm Chart、Makefile 目标与环境变量配置参考"
tags: [部署, Docker, Kubernetes, Helm, 基础设施, 环境变量]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-086
    resource: /references/deployment-infrastructure.md
    title: "Docker Compose 11 服务"
  - id: F-cs-087
    resource: /references/deployment-infrastructure.md
    title: "270+ .env 配置项"
---

# 部署与基础设施参考

## Docker Compose 服务栈

Docker Compose 编排 **11 个服务**，使用 `coze-network` 桥接网络，所有服务均配置 healthcheck。

```
                    ┌─────────────────────────────────────┐
                    │         coze-network (bridge)        │
                    │                                      │
  ┌─────────┐      │  ┌──────────┐  ┌──────────┐          │
  │  用户   │──────┼─▶│ coze-web │  │coze-server│          │
  │ :8888   │      │  │ (nginx)  │  │  (:8888)  │          │
  └─────────┘      │  └────┬─────┘  └─────┬─────┘          │
                    │       │              │                │
                    │  ┌────┴────┬────────┴───────┐        │
                    │  ▼         ▼                ▼        │
                    │ mysql    redis     elasticsearch     │
                    │ :3306    :6379         :9200        │
                    │  (8.4)   (8.0)        (8.18)        │
                    │                                    │
                    │  ┌──────┐  ┌──────┐  ┌────────┐    │
                    │  │minio │  │ etcd │  │ milvus │    │
                    │  │:9000 │  │:2379 │  │:19530  │    │
                    │  └──────┘  └──────┘  └────────┘    │
                    │                                    │
                    │  ┌──────────┬─────────┐            │
                    │  │nsqlookupd│  nsqd   │ nsqadmin   │
                    │  │ :4160/61 │ :4150/1 │  :4171     │
                    │  └──────────┴─────────┘            │
                    └─────────────────────────────────────┘
```

### 各服务详情

| 服务 | 镜像 | 端口 | 关键配置 |
|------|------|------|----------|
| **mysql** | `mysql:8.4.5` | 3306 | utf8mb4 字符集，utf8mb4_unicode_ci 排序规则，Atlas CLI  schema 迁移 |
| **redis** | `bitnamilegacy/redis:8.0` | 6379 | AOF 禁用，4 IO 线程，允许空密码 |
| **elasticsearch** | `bitnamilegacy/elasticsearch:8.18.0` | 9200 | analysis-smartcn 中文分词插件，自动初始化索引 schema |
| **minio** | `minio/RELEASE.2025-06-13` | 9000/9001 | 创建 opencoze 和 milvus bucket，自动复制 default_icon 和 official_plugin_icon |
| **etcd** | `bitnamilegacy/etcd:3.5` | 2379 | 自动压缩(revision keep 1000)，4GB quota，无认证 |
| **milvus** | `milvusdb/milvus:v2.5.10` | 19530 | standalone 模式，依赖 etcd+MinIO，seccomp:unconfined |
| **nsqlookupd** | `nsqio/nsq:v1.2.1` | 4160/4161 | NSQ 查找服务 |
| **nsqd** | `nsqio/nsq:v1.2.1` | 4150/4151 | NSQ 消息队列 |
| **nsqadmin** | `nsqio/nsq:v1.2.1` | 4171 | NSQ 管理界面 |
| **coze-server** | `cozedev/coze-studio-server:latest` | 8888 | 入口 `/app/opencoze`，挂载 .env 和 backend/conf |
| **coze-web** | `cozedev/coze-studio-web:latest` | ${WEB_LISTEN_ADDR:-8888}:80 | nginx 静态文件服务 |

## 可插拔基础设施选项

### 消息队列（EventBus）— 5 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `nsq` | NSQ 消息队列 | ✅ 默认 |
| `kafka` | Apache Kafka（IBM/sarama v1.45.1） | — |
| `rmq` | Apache RocketMQ | — |
| `pulsar` | Apache Pulsar | — |
| `nats` | NATS JetStream | — |

### 向量存储（VectorStore）— 3 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `milvus` | Milvus 向量数据库 v2.5.10 | ✅ 默认 |
| `vikingdb` | 火山引擎 VikingDB | — |
| `oceanbase` | OceanBase 数据库 | — |

### 对象存储（Storage）— 3 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `minio` | MinIO 对象存储 | ✅ 默认 |
| `tos` | 火山引擎 TOS（ve-tos-golang-sdk/v2 v2.7.17） | — |
| `s3` | AWS S3（aws-sdk-go-v2/service/s3 v1.84.1） | — |

### 向量嵌入（Embedding）— 5 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `ark` | 火山引擎 Ark | ✅ 默认 |
| `openai` | OpenAI Embedding | — |
| `ollama` | Ollama 本地嵌入 | — |
| `gemini` | Google Gemini Embedding | — |
| `http` | 自定义 HTTP 接口 | — |

### OCR — 2 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `ve` | 火山引擎 OCR | ✅ 默认 |
| `paddleocr` | PaddleOCR | — |

### 文档解析器（Parser）— 2 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `builtin` | 内置解析器 | ✅ 默认 |
| `paddleocr` | PaddleOCR 解析 | — |

### 重排序（Rerank）— 2 选项

| 选项 | 说明 | 默认 |
|------|------|------|
| `vikingdb` | VikingDB 重排序 | — |
| `rrf` | Reciprocal Rank Fusion | ✅ 默认 |

### LLM 协议 — 6 选项

ChatModel 支持以下协议：`openai`、`ark`、`deepseek`、`ollama`、`qwen`、`gemini`

Eino 扩展提供 7 个模型集成：ark、claude、deepseek、gemini、ollama、openai、qwen

### 搜索存储（searchstore）— 4 选项

使用工厂模式注册后端：`elasticsearch`、`milvus`、`oceanbase`、`vikingdb`

## 环境变量配置

`.env.example` 包含 **270+** 配置项，涵盖以下分类：

| 分类 | 前缀/说明 |
|------|-----------|
| Server | 服务端口、模式等 |
| MySQL | 数据库连接 |
| Redis | 缓存连接 |
| Storage | 对象存储配置 |
| ES | Elasticsearch 配置 |
| EventBus | 消息队列配置 |
| VectorStore | 向量数据库配置 |
| Embedding | 嵌入模型配置 |
| Rerank | 重排序配置 |
| OCR | OCR 配置 |
| Parser | 文档解析器配置 |
| Model | LLM 模型配置 |
| Registration | 注册控制 |
| PluginAES | 插件 OAuth AES 加密 |

### 注册控制

| 环境变量 | 说明 |
|----------|------|
| `DISABLE_USER_REGISTRATION` | 禁用用户注册 |
| `ALLOW_REGISTRATION_EMAIL` | 邮箱白名单（逗号分隔），同时作为管理员邮箱配置 |

### 插件 OAuth AES 加密

| 环境变量 | 说明 |
|----------|------|
| `PLUGIN_AES_AUTH_SECRET` | AES 认证密钥 |
| `PLUGIN_AES_STATE_SECRET` | AES 状态密钥 |
| `PLUGIN_AES_OAUTH_TOKEN_SECRET` | AES OAuth Token 密钥 |

密钥长度必须为 16/24/32 字节（AES-128/192/256）。

### LLM 模型配置

使用序号后缀模式配置多模型：

```
MODEL_PROTOCOL_0=openai
MODEL_ID_0=gpt-4
MODEL_API_KEY_0=sk-xxx
MODEL_NAME_0=GPT-4
MODEL_BASE_URL_0=https://api.openai.com/v1
```

## Backend Docker 构建

后端采用**两阶段构建**：

1. **构建阶段**：`golang:1.24-alpine`，ldflags="-s -w" 去除调试信息
2. **运行阶段**：`alpine:3.22.0`

### Python 沙箱环境

后端 Docker 镜像中安装 Python 3 venv，包含以下依赖：

| 包 | 版本 |
|----|------|
| urllib3 | 1.26.16 |
| h11 | 0.16.0 |
| httpx | 0.28.1 |
| pillow | 11.2.1 |
| pdfplumber | 0.11.7 |
| python-docx | 1.2.0 |
| numpy | 2.3.1 |

### Deno 沙箱

安装 Deno 运行时，预执行 `deno run -A jsr:@langchain/pyodide-sandbox` 初始化 Python 沙箱。

### 文档处理脚本

复制以下脚本到 `/app/`：
- `parse_pdf.py`
- `parse_docx.py`
- `sandbox.py`

### 网络端口

- 后端监听：`:8888`
- 前端 nginx：80（通过端口映射对外暴露）

## Helm Chart

| 属性 | 值 |
|------|-----|
| Chart 名称 | opencoze |
| Chart 版本 | v0.0.1 |
| App 版本 | 0.0.3 |
| 类型 | application |

关键配置：
- `coze-server` 使用 LoadBalancer 暴露 8888(HTTP) 和 8889(MinIO proxy)
- 支持 MySQL/OceanBase 切换（OceanBase 默认 enabled: false）

## Makefile 目标

| 目标 | 说明 |
|------|------|
| `debug` | 调试模式启动 |
| `fe` | 前端开发 |
| `server` | 服务端启动 |
| `build_server` | 构建服务端 |
| `sync_db` | 同步数据库（Atlas CLI） |
| `dump_db` | 导出数据库 |
| `middleware` | 中间件相关 |
| `web` | 一键启动（Docker Compose） |
| `down` | 停止服务 |
| `clean` | 清理 |
| `python` | Python 环境 |
| `atlas-hash` | Atlas hash 管理 |
| `setup_es_index` | 设置 ES 索引 |

## 系统最低要求

| 资源 | 最低配置 |
|------|----------|
| CPU | 2 核 |
| 内存 | 4GB |
| 软件 | Docker + Docker Compose |
| Go 版本 | >= 1.23.4（go.mod 声明 1.24.0） |
