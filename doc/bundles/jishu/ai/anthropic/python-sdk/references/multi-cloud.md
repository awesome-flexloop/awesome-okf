---
type: reference
title: "Anthropic Python SDK 多云后端认证参考"
description: "AnthropicBedrock（AWS Bedrock）、AnthropicVertex（Google Vertex AI）、AnthropicAWS、AnthropicGoogleCloud 等多云客户端类、认证参数、base_url 选择逻辑与 Beta 支持的完整 API 参考。"
tags: [bedrock, vertex, aws, google-cloud, multi-cloud, authentication, sigv4]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-059~F-073
    resource: /python-sdk/references/multi-cloud.md
    title: "Anthropic Python SDK 多云后端认证参考"
---

# Anthropic Python SDK 多云后端认证参考

本文档登记 Anthropic Python SDK 支持的多云后端客户端类，包括 AWS Bedrock、Google Vertex AI、原生 AWS、Google Cloud 等平台的客户端入口、认证参数、base_url 选择逻辑、签名机制与 Beta 功能支持。

> **核心设计**：所有多云客户端通过**继承**（而非组合）复用核心 `Anthropic`/`AsyncAnthropic` 客户端，只重写认证相关逻辑，上层 API（`messages.create`、`client.beta` 等）用法与官方客户端 100% 兼容。

## 客户端导入

所有多云客户端均可直接从 `anthropic` 顶层包导入：

```python
from anthropic import (
    AnthropicBedrock,      # AWS Bedrock 同步客户端
    AsyncAnthropicBedrock, # AWS Bedrock 异步客户端
    AnthropicVertex,       # Google Vertex AI 同步客户端
    AsyncAnthropicVertex,  # Google Vertex AI 异步客户端
    AnthropicAWS,          # 原生 AWS 同步客户端
    AsyncAnthropicAWS,     # 原生 AWS 异步客户端
    AnthropicGoogleCloud,  # Google Cloud 同步客户端
    AsyncAnthropicGoogleCloud,  # Google Cloud 异步客户端
)
```

## AWS Bedrock 客户端

### AnthropicBedrock（同步）

**类路径**：`anthropic.AnthropicBedrock`

继承自 `BaseBedrockClient[httpx.Client, Stream[Any]]` 和 `SyncAPIClient`，定义在 `lib/bedrock/_client.py`。

**构造函数核心参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `aws_access_key` | `str \| None` | AWS Access Key ID |
| `aws_secret_key` | `str \| None` | AWS Secret Access Key |
| `aws_region` | `str \| None` | AWS 区域（如 `"us-east-1"`） |
| `aws_profile` | `str \| None` | AWS 配置文件名称 |
| `aws_session_token` | `str \| None` | AWS Session Token（临时凭证） |
| `workspace_id` | `str \| None` | Workspace ID |
| `skip_auth` | `bool` | 是否跳过认证（用于本地测试） |

**默认配置**：

| 配置项 | 值 | 说明 |
|--------|----|------|
| `base_url` | `f"https://bedrock-runtime.{aws_region}.amazonaws.com"` | 根据区域动态生成 Bedrock Runtime endpoint |
| `DEFAULT_VERSION` | `"bedrock-2023-05-31"` | Bedrock API 版本常量 |

### AsyncAnthropicBedrock（异步）

**类路径**：`anthropic.AsyncAnthropicBedrock`

继承自 `BaseBedrockClient[httpx.AsyncClient, AsyncStream[Any]]` 和 `AsyncAPIClient`，参数与同步版本一致，`http_client` 类型为 `httpx.AsyncClient`。

### Bedrock 模块结构

`lib/bedrock/` 目录包含以下模块：

| 模块文件 | 说明 |
|---------|------|
| `_client.py` | AnthropicBedrock/AsyncAnthropicBedrock 客户端类定义 |
| `_beta.py` | Bedrock Beta 功能支持 |
| `_beta_messages.py` | Bedrock Beta 消息资源 |
| `_stream.py` | Bedrock 流式响应处理 |

## Google Vertex AI 客户端

### AnthropicVertex（同步）

**类路径**：`anthropic.AnthropicVertex`

继承自 `BaseVertexClient[httpx.Client, Stream[Any]]` 和 `SyncAPIClient`，定义在 `lib/vertex/_client.py`。

**构造函数核心参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `project_id` | `str \| None` | GCP 项目 ID |
| `region` | `str \| None` | GCP 区域（如 `"us-central1"`、`"global"`） |
| `access_token` | `str \| None` | GCP Access Token |
| `credentials` | `google.auth.credentials.Credentials \| None` | google-auth 凭证对象 |

**Base URL 选择逻辑**：

根据 `region` 参数自动选择 API endpoint：

| region 值 | base_url | 说明 |
|-----------|----------|------|
| `"global"` | `"https://aiplatform.googleapis.com/v1"` | 全局 endpoint |
| `"us"` | `"https://aiplatform.us.rep.googleapis.com/v1"` | 美国区域 endpoint |
| 其他区域 | 对应区域的 Rep 端点 | 如 `"europe-west1"` 等 |

**默认配置**：

| 配置项 | 值 | 说明 |
|--------|----|------|
| `DEFAULT_VERSION` | `"vertex-2023-10-16"` | Vertex AI API 版本常量 |

### AsyncAnthropicVertex（异步）

**类路径**：`anthropic.AsyncAnthropicVertex`

继承自 `BaseVertexClient[httpx.AsyncClient, AsyncStream[Any]]` 和 `AsyncAPIClient`，参数与同步版本一致。

### Vertex 模块结构

`lib/vertex/` 目录包含 Vertex AI 客户端实现，同时支持 Beta 功能（`_beta`、`_beta_messages`、`_stream` 等模块）。

## 原生 AWS 客户端

### AnthropicAWS（同步）

**类路径**：`anthropic.lib.aws.AnthropicAWS`（也可从顶层 `anthropic` 导入）

继承自核心 `Anthropic` 类，定义在 `lib/aws/_client.py`，使用 SigV4 签名直接访问 Anthropic AWS endpoint。

**构造函数核心参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `aws_access_key` | `str \| None` | AWS Access Key ID |
| `aws_secret_key` | `str \| None` | AWS Secret Access Key |
| `aws_region` | `str \| None` | AWS 区域 |
| `aws_profile` | `str \| None` | AWS 配置文件名称 |
| `aws_session_token` | `str \| None` | AWS Session Token |
| `workspace_id` | `str \| None` | Workspace ID |
| `skip_auth` | `bool` | 是否跳过认证 |

**请求签名机制**：

重写 `_prepare_request` 方法，使用 AWS SigV4 签名算法：
- 调用 `get_auth_headers` 生成 AWS 认证头
- 将签名信息注入请求头后发送

### AsyncAnthropicAWS（异步）

**类路径**：`anthropic.AsyncAnthropicAWS`

继承自 `AsyncAnthropic`，参数与同步版本一致。

### AWS 模块结构

`lib/aws/` 目录包含：

| 模块文件 | 说明 |
|---------|------|
| `_client.py` | AnthropicAWS/AsyncAnthropicAWS 客户端类定义 |
| `_auth.py` | AWS SigV4 签名实现 |
| `_credentials.py` | AWS 凭证提供者链 |

## Google Cloud 客户端

### AnthropicGoogleCloud（同步）

**类路径**：`anthropic.AnthropicGoogleCloud`

定义在 `lib/google_cloud/` 模块，用于通过 Google Cloud 平台访问 Anthropic 模型。

### AsyncAnthropicGoogleCloud（异步）

**类路径**：`anthropic.AsyncAnthropicGoogleCloud`

Google Cloud 的异步客户端版本。

## Credentials 凭证模块

`lib/credentials/` 目录提供统一的凭证管理抽象：

| 模块文件 | 说明 |
|---------|------|
| `_providers.py` | 凭证提供者实现（环境变量、配置文件、IMDS 等） |
| `_chain.py` | 凭证链（按顺序尝试多个提供者） |
| `_cache.py` | 凭证缓存机制（避免重复获取） |
| `_auth.py` | 认证流程核心逻辑 |

## 多云客户端使用模式

所有多云客户端的上层 API 与官方客户端完全一致，仅初始化参数不同：

```python
# 官方 API
from anthropic import Anthropic
client = Anthropic(api_key="sk-ant-...")
message = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)

# AWS Bedrock（API 用法完全相同）
from anthropic import AnthropicBedrock
client = AnthropicBedrock(
    aws_region="us-east-1",
    # 凭证通过默认凭证链自动获取
)
message = client.messages.create(
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)

# Google Vertex（API 用法完全相同）
from anthropic import AnthropicVertex
client = AnthropicVertex(
    region="us-central1",
    project_id="your-project-id",
)
message = client.messages.create(
    model="claude-3-5-sonnet@20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Beta 功能支持

Bedrock 和 Vertex 客户端均支持 Beta API，通过各自的 `_beta` 模块实现：
- Bedrock：`lib/bedrock/_beta.py`、`lib/bedrock/_beta_messages.py`
- Vertex：`lib/vertex/` 下的对应 Beta 模块

使用方式与官方客户端一致：`client.beta.messages.create(...)`，客户端自动处理对应云平台的 Beta 头签名与路由。
