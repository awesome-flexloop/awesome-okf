---
type: concept
title: "部署与运维"
description: "Coze Studio Docker Compose 一键部署、Helm K8s 部署、Makefile 命令体系、数据库迁移与环境配置运维指南"
tags: [部署, Docker, Kubernetes, Helm, 运维, Makefile]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-007
    resource: /references/deployment-infrastructure.md
    title: "Docker Compose 一键部署与 Helm K8s"
  - id: F-cs-086
    resource: /references/deployment-infrastructure.md
    title: "11 个 Docker 服务"
---

# 部署与运维

Coze Studio 提供两种部署方式：Docker Compose 一键部署（适合本地开发和小规模部署）和 Helm Chart K8s 部署（适合生产环境）。Docker Compose 编排 11 个服务，通过 `make web` 一条命令即可启动完整平台。系统最低配置仅需 2 CPU 核和 4GB 内存，同时支持通过环境变量灵活切换基础设施后端，满足从本地评估到企业级生产部署的全场景需求。

## Docker Compose 服务拓扑

Docker Compose 部署时，11 个服务通过 `coze-network` 桥接网络互联：

```
                         ┌────────────────────────────┐
                         │     coze-network (bridge)  │
                         │                            │
   用户浏览器 ──:8888──▶  │  ┌──────────────────────┐  │
                         │  │  coze-web (nginx)    │  │
                         │  │  静态资源 + API 反向代理│  │
                         │  └──────────┬───────────┘  │
                         │             │ /api 代理    │
                         │             ▼              │
                         │  ┌──────────────────────┐  │
                         │  │  coze-server :8888   │  │
                         │  │  Go Hertz 后端服务    │  │
                         │  └──┬───┬───┬───┬───┬──┘  │
                         │     │   │   │   │   │      │
                         │     ▼   ▼   │   ▼   ▼      │
                         │  ┌────┐┌────┐│┌────┐┌────┐│
                         │  │my- ││re- │││ mi-││NSQ ││
                         │  │sql ││dis │││nu- ││三件││
                         │  │:330││:637│││s   ││套  ││
                         │  │6   ││9   │││    ││    ││
                         │  └────┘└────┘│└────┘└────┘│
                         │               │            │
                         │     ┌─────────┼────────┐   │
                         │     ▼         ▼        ▼   │
                         │  ┌────┐ ┌────────┐ ┌────┐ │
                         │  │ ES │ │ etcd   ││mi- │ │
                         │  │:920│ │ :2379  ││lvus│ │
                         │  │0   │ │        ││:195│ │
                         │  └────┘ └────────┘│30  │ │
                         │                    └────┘ │
                         └────────────────────────────┘
```

### 服务版本与配置

| 服务 | 镜像 | 关键配置 |
|------|------|----------|
| **mysql** | `mysql:8.4.5` | utf8mb4/utf8mb4_unicode_ci，Atlas 管理 schema 迁移 |
| **redis** | `bitnamilegacy/redis:8.0` | AOF 关闭，4 IO 线程，无密码 |
| **elasticsearch** | `bitnamilegacy/elasticsearch:8.18.0` | analysis-smartcn 中文分词，自动初始化索引 |
| **minio** | `minio/RELEASE.2025-06-13` | 自动创建 opencoze/milvus bucket，复制默认图标 |
| **etcd** | `bitnamilegacy/etcd:3.5` | 自动压缩(revision keep 1000)，4GB quota |
| **milvus** | `milvusdb/milvus:v2.5.10` | standalone 模式，依赖 etcd+MinIO |
| **nsqlookupd** | `nsqio/nsq:v1.2.1` | 4160(TCP)/4161(HTTP) |
| **nsqd** | `nsqio/nsq:v1.2.1` | 4150(TCP)/4151(HTTP) |
| **nsqadmin** | `nsqio/nsq:v1.2.1` | 4171(Web UI) |
| **coze-server** | `cozedev/coze-studio-server:latest` | 入口 `/app/opencoze`，监听 :8888 |
| **coze-web** | `cozedev/coze-studio-web:latest` | nginx 静态文件，映射 8888→80 |

所有服务均配置 healthcheck，Docker Compose 启动时会按依赖顺序启动。

## 后端 Docker 镜像

后端镜像采用两阶段构建：

1. **构建阶段**：`golang:1.24-alpine`，编译 Go 代码，ldflags="-s -w"
2. **运行阶段**：`alpine:3.22.0`

运行阶段预装的组件：

| 组件 | 说明 |
|------|------|
| **Python 3 venv** | 包含 urllib3、httpx、pillow、pdfplumber、python-docx、numpy |
| **Deno** | 预执行 `deno run -A jsr:@langchain/pyodide-sandbox` 初始化 Python 沙箱 |
| **文档处理脚本** | `parse_pdf.py`、`parse_docx.py`、`sandbox.py` 部署到 `/app/` |

## 前端 Docker 镜像

前端镜像同样两阶段构建：

1. **构建阶段**：`node:22-alpine`，支持中国镜像加速（aliyun alpine、npmmirror.com）
2. **运行阶段**：`nginx:1.25-alpine`

构建命令：`rush build --to @coze-studio/app`，构建产物复制到 nginx `/usr/share/nginx/html`。

## Helm Chart K8s 部署

Helm Chart 位于 `helm/charts/opencoze/`：

| 属性 | 值 |
|------|-----|
| Chart 名称 | opencoze |
| Chart 版本 | v0.0.1 |
| App 版本 | 0.0.3 |
| 类型 | application |

关键配置：
- `coze-server` 使用 LoadBalancer 类型 Service 暴露 8888（HTTP）和 8889（MinIO proxy）
- 支持 MySQL/OceanBase 数据库切换（OceanBase 默认 `enabled: false`）

## Makefile 命令体系

Makefile 提供完整的开发和部署命令：

| 命令 | 用途 | 典型场景 |
|------|------|----------|
| `make web` | **一键启动** Docker Compose 全栈 | 首次部署、快速体验 |
| `make down` | 停止 Docker Compose 服务 | 停止开发环境 |
| `make debug` | 调试模式启动 | 后端调试 |
| `make fe` | 启动前端开发服务器 | 前端开发 |
| `make server` | 启动后端服务 | 后端开发 |
| `make build_server` | 编译后端二进制 | 后端构建 |
| `make sync_db` | 执行数据库迁移（Atlas CLI） | 数据库 schema 更新 |
| `make dump_db` | 导出数据库 schema | 生成迁移文件 |
| `make setup_es_index` | 初始化 ES 索引 | 首次部署或索引重建 |
| `make middleware` | 中间件管理 | 中间件操作 |
| `make clean` | 清理构建产物和容器 | 环境清理 |
| `make python` | Python 环境管理 | 文档处理脚本开发 |
| `make atlas-hash` | Atlas 迁移哈希管理 | 迁移文件校验 |

## 环境变量配置

`.env.example` 包含 270+ 配置项，分为以下类别：

| 类别 | 关键变量 |
|------|----------|
| **Server** | 服务端口、运行模式 |
| **MySQL** | 数据库地址、端口、用户名、密码、库名 |
| **Redis** | Redis 连接地址和密码 |
| **Storage** | 对象存储类型和连接配置 |
| **ES** | Elasticsearch 地址 |
| **EventBus** | 消息队列类型和连接 |
| **VectorStore** | 向量数据库类型和连接 |
| **Embedding** | 嵌入模型类型和 API 配置 |
| **Rerank** | 重排序配置 |
| **OCR/Parser** | OCR 和文档解析器配置 |
| **Model** | LLM 模型配置（MODEL_PROTOCOL_N/ID_N/KEY_N 序列） |
| **Registration** | 注册控制 |
| **PluginAES** | 插件 OAuth AES 密钥 |

### 关键安全配置

**注册控制**：
```bash
# 完全禁止注册
DISABLE_USER_REGISTRATION=true

# 邮箱白名单注册（同时设为管理员）
ALLOW_REGISTRATION_EMAIL=admin@example.com,dev@example.com
```

**插件 OAuth AES 加密**：
```bash
# AES 密钥长度必须为 16/24/32 字节
PLUGIN_AES_AUTH_SECRET=your-16byte-key
PLUGIN_AES_STATE_SECRET=your-16byte-key
PLUGIN_AES_OAUTH_TOKEN_SECRET=your-16byte-key
```

## 数据库迁移

Coze Studio 使用 Atlas CLI 管理数据库 schema 迁移：

- 迁移文件位于 `docker/atlas/migrations/`
- `make sync_db` 应用待执行的迁移
- `make dump_db` 导出当前 schema 为迁移文件
- `docker/mysql/schema.sql` 和 `sql_init.sql` 为初始化 SQL
- 支持 MySQL 到 OceanBase 的切换

## Elasticsearch 索引初始化

首次部署或需要重建索引时，执行：

```bash
make setup_es_index
```

此命令会创建必要的 ES 索引并配置中文分词（analysis-smartcn）。

## 系统最低要求

| 资源 | 最低配置 |
|------|----------|
| CPU | 2 核 |
| 内存 | 4GB |
| 软件 | Docker + Docker Compose |
| Go（本地构建） | >= 1.23.4（go.mod: 1.24.0） |
| 磁盘 | 建议 20GB+（含 Docker 镜像和数据卷） |

## 相关概念

- [整体架构概览](/concepts/00-overview-ddd-architecture.md)
- [可插拔基础设施](/concepts/04-pluggable-infrastructure.md)
- [LLM 模型集成](/concepts/05-llm-integration.md)
- [Docker 快速入门](/examples/docker-quickstart.md)
- [配置基础设施](/examples/configure-infrastructure.md)
- [添加 LLM 模型](/examples/add-llm-model.md)
- [部署与基础设施参考](/references/deployment-infrastructure.md)
