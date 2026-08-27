---
type: concept
title: "多云后端部署"
description: "详解 Anthropic Python SDK 如何支持 Anthropic 直连、AWS Bedrock、Google Vertex AI 等多云后端，包括各平台客户端类、认证方式、base_url 选择逻辑、credentials 凭证链与多云架构设计。"
tags: [multi-cloud, bedrock, vertex, aws, google-cloud, authentication, sigv4, credentials]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-059~F-073
    resource: /python-sdk/references/multi-cloud.md
    title: "Anthropic Python SDK 多云后端认证参考"
  - id: F-005,F-006,F-007,F-012~F-015,F-074~F-084
    resource: /python-sdk/references/sdk-client.md
    title: "Anthropic Python SDK 客户端入口与基础设施参考"
---

# 多云后端部署

Anthropic Python SDK 的一大设计亮点是**原生多云支持**。除了直接访问 Anthropic 官方 API（`https://api.anthropic.com`），SDK 还内置了对主流云平台托管 Claude 服务的客户端支持，包括 AWS Bedrock、Google Vertex AI、原生 AWS endpoint、Google Cloud 平台。所有多云客户端通过继承核心客户端实现，上层 API（如 `messages.create`）用法与官方客户端完全一致，你只需要修改初始化参数即可在不同云平台间切换。

**本文适合谁**：需要在 AWS/GCP 等云平台部署 Claude 应用的开发者、多云架构工程师、企业级 AI 应用集成负责人。

## 为什么需要多云策略

Anthropic 采用开放的模型分发策略，允许用户通过多种渠道访问 Claude 模型：

1. **Anthropic 直连**：最简单直接的方式，直接调用 Anthropic 官方 API，适合快速原型开发和中小规模应用
2. **AWS Bedrock**：Amazon Web Services 的托管 AI 服务平台，适合已在 AWS 生态中的企业，利用 AWS IAM 进行权限管理，可与 AWS 其他服务无缝集成
3. **Google Vertex AI**：Google Cloud 的 AI 平台，适合 GCP 用户，支持区域化部署、企业级安全合规
4. **Azure OpenAI Service**（注：SDK 通过自定义 base_url 支持）：Microsoft Azure 平台
5. **私有部署/本地代理**：通过自定义 `base_url` 访问企业内部代理或私有化部署的模型服务

这种多云策略带来的好处是：
- **云厂商锁定风险降低**：可以根据业务需求选择或切换云平台
- **合规与数据主权**：某些地区或行业要求数据留在特定云平台/区域
- **成本优化**：不同云平台的定价、折扣、预留实例策略不同
- **高可用与灾备**：可以跨云平台部署实现冗余

## Anthropic 直连：默认后端

默认情况下，使用 `Anthropic` 或 `AsyncAnthropic` 客户端直接访问 Anthropic 官方 API：

```python
from anthropic import Anthropic, AsyncAnthropic

# 默认 base_url = "https://api.anthropic.com"
client = Anthropic()  # 从 ANTHROPIC_API_KEY 环境变量读取 API Key

# 或者显式传入
client = Anthropic(
    api_key="sk-ant-api03-...",
    base_url="https://api.anthropic.com",  # 可省略，这是默认值
)

# 异步版本
async_client = AsyncAnthropic()
```

官方直连的特点：
- 使用 API Key 认证（`x-api-key` 请求头）
- 最新模型和功能优先上线
- 适合直接面向互联网的应用
- 无需云平台账号

## AWS Bedrock 客户端

AWS Bedrock 是 AWS 提供的托管式 AI 服务，Anthropic Claude 是 Bedrock 上的核心模型之一。SDK 提供 `AnthropicBedrock` 和 `AsyncAnthropicBedrock` 两个客户端类用于访问 Bedrock。

### 类路径与导入

```python
from anthropic import (
    AnthropicBedrock,       # 同步客户端
    AsyncAnthropicBedrock,  # 异步客户端
)
```

这两个类定义在 `lib/bedrock/_client.py`，继承自 `BaseBedrockClient` 和对应的同步/异步 API 客户端基类。

### AWS 认证方式

Bedrock 客户端支持多种 AWS 认证方式，按默认凭证链顺序自动查找：

| 认证方式 | 参数 | 说明 |
|---------|------|------|
| 显式传入密钥 | `aws_access_key`, `aws_secret_key`, `aws_session_token` | 直接传入 Access Key、Secret Key 和可选的 Session Token（用于临时凭证） |
| AWS Profile | `aws_profile` | 指定 AWS 配置文件名称（如 `"default"`、`"production"`），从 `~/.aws/credentials` 读取 |
| 环境变量 | 无（自动读取） | `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN` |
| IAM 角色 | 无（自动读取） | EC2/ECS/EKS/Lambda 等环境中的 IAM 角色，通过 IMDS（Instance Metadata Service）自动获取 |
| 跳过认证 | `skip_auth=True` | 用于本地测试或自定义签名场景 |

### 初始化示例

```python
from anthropic import AnthropicBedrock

# 方式1：使用默认凭证链（推荐，生产环境用 IAM 角色）
client = AnthropicBedrock(
    aws_region="us-east-1",  # 必填，指定 AWS 区域
)

# 方式2：显式传入密钥（仅用于开发测试）
client = AnthropicBedrock(
    aws_access_key="AKIA...",
    aws_secret_key="...",
    aws_region="us-east-1",
)

# 方式3：使用 AWS Profile
client = AnthropicBedrock(
    aws_profile="my-aws-profile",
    aws_region="us-west-2",
)

# 方式4：使用临时 Session Token（如 STS  AssumeRole 获取）
client = AnthropicBedrock(
    aws_access_key="ASIA...",
    aws_secret_key="...",
    aws_session_token="Fwo...",
    aws_region="us-east-1",
)
```

### aws_region 参数

`aws_region` 是必填参数，决定了 Bedrock Runtime endpoint：

- 默认 `base_url` 格式：`f"https://bedrock-runtime.{aws_region}.amazonaws.com"`
- 常用区域：`us-east-1`（弗吉尼亚）、`us-west-2`（俄勒冈）、`eu-west-1`（爱尔兰）、`ap-northeast-1`（东京）等
- 注意：Claude 模型并非在所有区域都可用，请参考 AWS 文档确认模型支持的区域

### Bedrock 模型 ID 差异

使用 Bedrock 时，模型 ID 格式与官方直连不同，需要使用 Bedrock 特有的模型 ARN 或模型 ID：

```python
# 官方直连的模型 ID
# model="claude-3-5-sonnet-latest"

# Bedrock 的模型 ID 格式
message = client.messages.create(
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",  # Bedrock 格式
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Bedrock 特有 Beta 支持

Bedrock 客户端通过 `lib/bedrock/_beta.py` 和 `lib/bedrock/_beta_messages.py` 模块支持 Beta 功能，自动处理 Bedrock 特有的 Beta 头签名与路由。使用方式与官方客户端一致：`client.beta.messages.create(...)`。

## Google Vertex AI 客户端

Google Vertex AI 是 Google Cloud 的企业级 AI 平台，SDK 提供 `AnthropicVertex` 和 `AsyncAnthropicVertex` 客户端类。

### 类路径与导入

```python
from anthropic import (
    AnthropicVertex,       # 同步客户端
    AsyncAnthropicVertex,  # 异步客户端
)
```

这两个类定义在 `lib/vertex/_client.py`，继承自 `BaseVertexClient` 和对应的同步/异步 API 客户端基类。默认 API 版本常量为 `DEFAULT_VERSION = "vertex-2023-10-16"`。

### GCP 认证方式

Vertex AI 客户端支持以下 GCP 认证方式：

| 认证方式 | 参数 | 说明 |
|---------|------|------|
| Service Account 凭证文件 | `credentials` | 传入 `google.auth.credentials.Credentials` 对象 |
| Access Token | `access_token` | 直接传入 OAuth2 Access Token |
| 环境变量 | 无（自动读取） | `GOOGLE_APPLICATION_CREDENTIALS` 环境变量指向 service account JSON 文件 |
| GCP 环境默认凭证 | 无（自动读取） | GCE/GKE/Cloud Run/Cloud Functions 等环境中的默认服务账号 |

### project_id 与 region 参数

Vertex 客户端需要两个关键参数：

- `project_id`：GCP 项目 ID（必填）
- `region`：GCP 区域（必填），决定了 API endpoint

```python
from anthropic import AnthropicVertex

# 方式1：使用默认凭证链（推荐，生产环境用 GCP 服务账号）
client = AnthropicVertex(
    project_id="your-gcp-project-id",
    region="us-central1",
)

# 方式2：使用 service account JSON 文件
import google.auth
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "/path/to/service-account-key.json"
)
client = AnthropicVertex(
    project_id="your-gcp-project-id",
    region="us-central1",
    credentials=credentials,
)

# 方式3：显式传入 access token
client = AnthropicVertex(
    project_id="your-gcp-project-id",
    region="us-central1",
    access_token="ya29...",
)
```

### base_url 区域路由逻辑

`AnthropicVertex` 根据 `region` 参数自动选择合适的 API endpoint：

| region 值 | base_url | 说明 |
|-----------|----------|------|
| `"global"` | `"https://aiplatform.googleapis.com/v1"` | 全局 endpoint |
| `"us"` | `"https://aiplatform.us.rep.googleapis.com/v1"` | 美国区域 endpoint |
| 其他区域 | 对应区域的 Rep 端点 | 如 `"europe-west1"`、`"asia-northeast1"` 等 |

### Vertex 模型 ID 差异

Vertex AI 的模型 ID 格式与官方直连也不同：

```python
message = client.messages.create(
    model="claude-3-5-sonnet@20241022",  # Vertex 格式
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

## 其他云平台客户端

除了 Bedrock 和 Vertex，SDK 还提供另外两个云平台客户端：

### AnthropicAWS / AsyncAnthropicAWS

定义在 `lib/aws/_client.py`，使用 AWS SigV4 签名直接访问 Anthropic 的 AWS endpoint，而非通过 Bedrock。

```python
from anthropic import AnthropicAWS

client = AnthropicAWS(
    aws_access_key="...",
    aws_secret_key="...",
    aws_region="us-east-1",
)
```

`AnthropicAWS` 直接继承自核心 `Anthropic` 类，重写 `_prepare_request` 方法实现 SigV4 签名，调用 `get_auth_headers` 生成 AWS 认证头注入请求。

### AnthropicGoogleCloud / AsyncAnthropicGoogleCloud

定义在 `lib/google_cloud/` 模块，用于通过 Google Cloud 平台访问 Anthropic 模型。

```python
from anthropic import AnthropicGoogleCloud

client = AnthropicGoogleCloud(
    # GCP 认证参数
)
```

## credentials 模块：统一凭证管理

SDK 在 `lib/credentials/` 目录提供了统一的凭证管理抽象层，为多云客户端提供一致的认证体验：

| 模块文件 | 职责 |
|---------|------|
| `_providers.py` | 各种凭证提供者实现：环境变量提供者、配置文件提供者、IMDS（元数据服务）提供者等 |
| `_chain.py` | 凭证链（Credentials Chain）：按优先级顺序尝试多个提供者，直到找到有效凭证 |
| `_cache.py` | 凭证缓存机制：临时凭证（如 STS Token）会过期，缓存避免重复获取 |
| `_auth.py` | 认证流程核心逻辑：协调凭证提供者、缓存、刷新机制 |

这种设计借鉴了 AWS SDK 和 Google Auth 库的最佳实践——凭证链模式：
1. 先检查显式传入的参数
2. 再检查环境变量
3. 再检查配置文件
4. 最后尝试云平台环境的元数据服务（IMDS）

开发者无需关心具体的凭证来源，SDK 会自动按顺序查找。

## 多云架构设计：继承复用的智慧

所有多云客户端采用**继承**而非组合的方式复用核心客户端代码，这是一个重要的架构决策：

```
SyncAPIClient (自动生成的基础 HTTP 客户端)
    ├── Anthropic (官方直连)
    │     └── AnthropicAWS (原生 AWS endpoint，继承自 Anthropic)
    └── BaseBedrockClient
          └── AnthropicBedrock (AWS Bedrock)
    └── BaseVertexClient
          └── AnthropicVertex (Google Vertex AI)
```

这种设计带来的好处：
- **API 100% 兼容**：所有上层方法（`messages.create`、`beta.*`、流式处理等）直接继承，无需重写
- **代码复用最大化**：只重写认证相关的 `_prepare_request` 等方法，其他逻辑全部复用
- **零学习成本迁移**：学会了官方客户端，就会用所有多云客户端，只是初始化参数不同
- **类型安全**：通过泛型参数（如 `BaseBedrockClient[httpx2.Client, Stream[Any]]`）保证同步/异步类型正确

## 多云客户端使用模式对比

| 特性 | Anthropic (官方) | AnthropicBedrock | AnthropicVertex |
|------|-----------------|------------------|-----------------|
| 认证方式 | API Key | AWS SigV4（IAM/密钥/Profile） | GCP OAuth2（Service Account/Token） |
| base_url | `https://api.anthropic.com` | 按 region 动态生成 | 按 region 路由选择 |
| 模型 ID 格式 | `claude-3-5-sonnet-latest` | `anthropic.claude-3-5-sonnet-20241022-v2:0` | `claude-3-5-sonnet@20241022` |
| 云平台集成 | 无 | AWS IAM、VPC、CloudTrail 等 | GCP IAM、VPC Service Controls 等 |
| 适合场景 | 通用、快速原型 | AWS 生态企业 | GCP 生态企业 |

### 同一套代码切换后端

得益于继承复用的设计，你可以编写与后端无关的代码，通过配置切换客户端类型：

```python
import os
from anthropic import Anthropic, AnthropicBedrock, AnthropicVertex

def create_client():
    backend = os.getenv("ANTHROPIC_BACKEND", "direct")
    
    if backend == "direct":
        return Anthropic()
    elif backend == "bedrock":
        return AnthropicBedrock(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
        )
    elif backend == "vertex":
        return AnthropicVertex(
            project_id=os.getenv("GCP_PROJECT_ID"),
            region=os.getenv("GCP_REGION", "us-central1"),
        )
    else:
        raise ValueError(f"Unknown backend: {backend}")

# 业务代码完全不关心后端
client = create_client()
message = client.messages.create(
    model=os.getenv("ANTHROPIC_MODEL"),  # 模型 ID 也可以通过配置注入
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

## 相关概念

- [客户端初始化与配置](01-client-init.md) — 学习客户端通用的超时、重试、中间件配置
- [Beta: Agents、Memory与Skills](08-beta-agents.md) — 多云客户端同样支持 Beta API 功能
- [中间件、扩展与错误处理](09-middleware-extended.md) — 多云客户端同样支持中间件和响应装饰模式
- [Anthropic Python SDK 多云后端认证参考](../references/multi-cloud.md) — 多云客户端类和参数的完整 API 手册
- [Anthropic Python SDK 客户端入口与基础设施参考](../references/sdk-client.md) — 核心客户端的完整配置参数
