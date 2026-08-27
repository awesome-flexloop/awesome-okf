---
type: example
title: "AWS Bedrock与Google Vertex后端"
description: "使用AnthropicBedrock和AnthropicVertex客户端通过AWS Bedrock或Google Vertex AI访问Claude模型，包括认证配置、模型ID差异和同一套代码切换后端。"
tags: [bedrock, vertex, aws, google-cloud, multi-cloud, iam, deployment]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
sources:
  - id: F-059~F-073
    resource: /python-sdk/references/multi-cloud.md
    title: "Anthropic Python SDK 多云后端认证参考"
  - id: concept-01
    resource: /python-sdk/concepts/01-client-init.md
    title: "客户端初始化与配置"
  - id: concept-07
    resource: /python-sdk/concepts/07-multi-cloud.md
    title: "多云后端部署"
---

# AWS Bedrock与Google Vertex后端

本示例演示如何使用 Anthropic Python SDK 的多云客户端，通过 AWS Bedrock 或 Google Vertex AI 访问 Claude 模型，而不是直接连接 Anthropic 官方 API。你将学习：两种云平台客户端的初始化方式、认证配置（IAM角色/密钥/服务账号）、模型ID格式差异，以及如何编写后端无关的代码通过配置一键切换云平台。

## 为什么使用多云后端

| 后端 | 适用场景 | 认证方式 |
|------|---------|---------|
| Anthropic 直连 | 快速原型、通用应用、中小规模 | API Key |
| AWS Bedrock | 已在 AWS 生态、企业级合规、IAM权限管理 | AWS SigV4（IAM角色/密钥） |
| Google Vertex AI | 已在 GCP 生态、区域化部署、企业安全 | GCP OAuth2（服务账号） |

多云客户端的核心优势：**上层 API（messages.create 等）用法 100% 与官方客户端一致**，只是初始化参数不同，学习成本为零。

## 前置准备

### 对于 AWS Bedrock
1. 拥有 AWS 账号
2. 在 AWS Bedrock 控制台申请访问 Claude 模型权限
3. 配置 AWS 凭证（环境变量、~/.aws/credentials、或 IAM 角色）

```bash
# 方式1：环境变量（开发测试用）
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

# 方式2：AWS CLI 配置（推荐开发环境）
aws configure
```

### 对于 Google Vertex AI
1. 拥有 GCP 账号，创建项目并启用 Vertex AI API
2. 创建 Service Account 并下载 JSON 密钥文件
3. 配置凭证

```bash
# 方式1：环境变量指向服务账号密钥文件
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
```

## 完整代码

```python
import os
from typing import Literal
from anthropic import (
    Anthropic,
    AsyncAnthropic,
    AnthropicBedrock,
    AsyncAnthropicBedrock,
    AnthropicVertex,
    AsyncAnthropicVertex,
    AnthropicError,
)


# ========== 客户端工厂：根据配置创建对应后端的客户端 ==========

def create_client(
    backend: Literal["direct", "bedrock", "vertex"] = None,
    model_preference: str = None,
):
    """
    根据环境变量配置创建对应的 Anthropic 客户端。

    环境变量：
        ANTHROPIC_BACKEND: "direct"（默认）、"bedrock" 或 "vertex"
        ANTHROPIC_MODEL: 模型 ID（各后端格式不同，也可使用自动映射）

    Args:
        backend: 强制指定后端，不指定则从环境变量读取
        model_preference: 模型偏好（如 "sonnet"、"haiku"、"opus"）

    Returns:
        (client, model_id) 元组
    """
    backend = backend or os.getenv("ANTHROPIC_BACKEND", "direct")

    # 根据后端和偏好映射到正确的模型 ID
    model_map = {
        "direct": {
            "sonnet": "claude-3-5-sonnet-latest",
            "haiku": "claude-3-5-haiku-latest",
            "opus": "claude-opus-4-latest",
        },
        "bedrock": {
            "sonnet": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "haiku": "anthropic.claude-3-5-haiku-20241022-v1:0",
            "opus": "anthropic.claude-opus-4-20250514-v1:0",
        },
        "vertex": {
            "sonnet": "claude-3-5-sonnet@20241022",
            "haiku": "claude-3-5-haiku@20241022",
            "opus": "claude-opus-4@20250514",
        },
    }

    model_preference = model_preference or os.getenv("ANTHROPIC_MODEL_PREFERENCE", "sonnet")

    if backend == "direct":
        # ====== Anthropic 官方直连 ======
        client = Anthropic()  # 自动从 ANTHROPIC_API_KEY 读取
        model_id = os.getenv("ANTHROPIC_MODEL") or model_map["direct"][model_preference]
        print(f"[客户端] Anthropic 直连 | 模型：{model_id}")

    elif backend == "bedrock":
        # ====== AWS Bedrock ======
        # Bedrock 客户端支持多种认证方式，按默认凭证链自动查找：
        # 1. 显式传入参数
        # 2. 环境变量 AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY
        # 3. ~/.aws/credentials 配置文件
        # 4. EC2/ECS/Lambda 等环境中的 IAM 角色（IMDS）
        client = AnthropicBedrock(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            # 显式传入密钥（开发测试用，生产环境建议用 IAM 角色）
            # aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
            # aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            # aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
            # aws_profile=os.getenv("AWS_PROFILE"),
        )
        model_id = os.getenv("ANTHROPIC_MODEL") or model_map["bedrock"][model_preference]
        print(f"[客户端] AWS Bedrock ({os.getenv('AWS_REGION', 'us-east-1')}) | 模型：{model_id}")

    elif backend == "vertex":
        # ====== Google Vertex AI ======
        # Vertex 客户端认证方式：
        # 1. 环境变量 GOOGLE_APPLICATION_CREDENTIALS 指向服务账号 JSON
        # 2. GCE/GKE/Cloud Run 等环境的默认服务账号
        # 3. 显式传入 credentials 对象或 access_token
        client = AnthropicVertex(
            project_id=os.getenv("GCP_PROJECT_ID"),
            region=os.getenv("GCP_REGION", "us-central1"),
            # 可选：显式传入服务账号凭证
            # credentials=google.oauth2.service_account.Credentials.from_service_account_file("..."),
            # access_token=os.getenv("GCP_ACCESS_TOKEN"),
        )
        model_id = os.getenv("ANTHROPIC_MODEL") or model_map["vertex"][model_preference]
        print(f"[客户端] Google Vertex ({os.getenv('GCP_REGION', 'us-central1')}) | 模型：{model_id}")

    else:
        raise ValueError(f"不支持的后端：{backend}，可选值：direct/bedrock/vertex")

    return client, model_id


async def create_async_client(
    backend: Literal["direct", "bedrock", "vertex"] = None,
    model_preference: str = None,
):
    """创建异步版本的客户端（用法与同步完全对称）"""
    backend = backend or os.getenv("ANTHROPIC_BACKEND", "direct")
    model_preference = model_preference or os.getenv("ANTHROPIC_MODEL_PREFERENCE", "sonnet")

    model_map = {
        "direct": {"sonnet": "claude-3-5-sonnet-latest"},
        "bedrock": {"sonnet": "anthropic.claude-3-5-sonnet-20241022-v2:0"},
        "vertex": {"sonnet": "claude-3-5-sonnet@20241022"},
    }

    if backend == "direct":
        client = AsyncAnthropic()
    elif backend == "bedrock":
        client = AsyncAnthropicBedrock(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
        )
    elif backend == "vertex":
        client = AsyncAnthropicVertex(
            project_id=os.getenv("GCP_PROJECT_ID"),
            region=os.getenv("GCP_REGION", "us-central1"),
        )
    else:
        raise ValueError(f"不支持的后端：{backend}")

    model_id = model_map[backend][model_preference]
    return client, model_id


# ========== 业务逻辑：后端无关的对话代码 ==========

def simple_chat(client, model_id: str, question: str) -> str:
    """
    简单对话函数——注意：这段代码完全不关心后端是哪个！
    无论使用 Anthropic 直连、Bedrock 还是 Vertex，代码都一样。

    Args:
        client: Anthropic/AnthropicBedrock/AnthropicVertex 实例
        model_id: 对应后端格式的模型 ID
        question: 用户问题

    Returns:
        Claude 的回复文本
    """
    message = client.messages.create(
        model=model_id,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return message.content[0].text


def multi_turn_chat(client, model_id: str, system_prompt: str = None) -> None:
    """
    多轮对话——同样后端无关。
    流式、工具调用、视觉等所有功能在多云客户端上用法完全相同。
    """
    messages = []

    questions = [
        "你好，请用一句话介绍你自己",
        "Python 中列表和元组的主要区别是什么？",
        "能给一个简单的代码示例吗？",
    ]

    for i, question in enumerate(questions, 1):
        messages.append({"role": "user", "content": question})

        kwargs = {
            "model": model_id,
            "max_tokens": 1024,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        message = client.messages.create(**kwargs)
        reply = message.content[0].text
        messages.append({"role": "assistant", "content": reply})

        print(f"\n【第{i}轮】")
        print(f"你：{question}")
        print(f"Claude：{reply}")
        print(f"(token：输入 {message.usage.input_tokens} / 输出 {message.usage.output_tokens})")


def streaming_chat(client, model_id: str, question: str) -> str:
    """
    流式对话——多云客户端同样支持流式！
    """
    full_text = ""
    print(f"你：{question}")
    print("Claude（流式）：", end="", flush=True)

    with client.messages.stream(
        model=model_id,
        max_tokens=1024,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        for text in stream.text_stream:
            full_text += text
            print(text, end="", flush=True)

        final_message = stream.get_final_message()
        print(f"\n\n(流式完成 | token：{final_message.usage.input_tokens} in / {final_message.usage.output_tokens} out)")

    return full_text


# ========== 各后端认证方式演示 ==========

def bedrock_auth_demo():
    """演示 AWS Bedrock 的各种认证方式（代码框架）"""
    print("\n" + "=" * 60)
    print("AWS Bedrock 认证方式演示")
    print("=" * 60)

    print("""
# 方式1：默认凭证链（生产环境推荐 - IAM 角色）
# 在 EC2/ECS/EKS/Lambda 上运行时，SDK 自动从 IMDS 获取凭证
client = AnthropicBedrock(aws_region="us-east-1")

# 方式2：显式传入 Access Key（仅开发测试用，不要硬编码！）
client = AnthropicBedrock(
    aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_region="us-east-1",
)

# 方式3：使用 AWS Profile（本地开发推荐）
# 读取 ~/.aws/credentials 中配置的 profile
client = AnthropicBedrock(
    aws_profile="my-dev-profile",
    aws_region="us-west-2",
)

# 方式4：临时 Session Token（STS AssumeRole 场景）
client = AnthropicBedrock(
    aws_access_key="ASIA...",  # 临时凭证以 ASIA 开头
    aws_secret_key="...",
    aws_session_token="Fwo...",  # 临时 token
    aws_region="us-east-1",
)
""")


def vertex_auth_demo():
    """演示 Google Vertex AI 的各种认证方式（代码框架）"""
    print("\n" + "=" * 60)
    print("Google Vertex AI 认证方式演示")
    print("=" * 60)

    print("""
# 首先需要安装 google-auth 库（如果还没装）：
# pip install google-auth

# 方式1：默认凭证链（生产环境推荐）
# 在 GCE/GKE/Cloud Run/Functions 上自动使用服务账号
# 本地开发：设置 GOOGLE_APPLICATION_CREDENTIALS 环境变量
client = AnthropicVertex(
    project_id="your-project-id",
    region="us-central1",
)

# 方式2：显式传入 Service Account 凭证文件
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(
    "/path/to/your-service-account-key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
client = AnthropicVertex(
    project_id="your-project-id",
    region="us-central1",
    credentials=credentials,
)

# 方式3：显式传入 Access Token（短有效期场景）
client = AnthropicVertex(
    project_id="your-project-id",
    region="us-central1",
    access_token="ya29.a0AfH6SMB...",  # OAuth2 Access Token
)
""")


# ========== 模型 ID 速查表 ==========

def model_id_cheatsheet():
    """打印各后端模型 ID 对照表"""
    print("\n" + "=" * 60)
    print("各后端模型 ID 对照表")
    print("=" * 60)
    print("""
| 模型              | Anthropic 直连                | AWS Bedrock                                          | Google Vertex               |
|-------------------|------------------------------|------------------------------------------------------|----------------------------|
| Claude 3.5 Sonnet | claude-3-5-sonnet-latest     | anthropic.claude-3-5-sonnet-20241022-v2:0            | claude-3-5-sonnet@20241022 |
| Claude 3.5 Haiku  | claude-3-5-haiku-latest      | anthropic.claude-3-5-haiku-20241022-v1:0             | claude-3-5-haiku@20241022  |
| Claude Opus 4     | claude-opus-4-latest         | anthropic.claude-opus-4-20250514-v1:0                | claude-opus-4@20250514     |

⚠️ 注意事项：
1. Bedrock 模型 ID 带 "anthropic." 前缀和版本后缀 ":0"
2. Vertex 模型 ID 使用 "@日期" 格式而非 "-latest"
3. 模型可用性因区域而异，请检查对应云平台文档
4. 最新模型可能先在 Anthropic 直连上线，云平台会滞后一段时间
""")


# ========== 主函数 ==========

def main():
    """
    主函数：演示多云客户端使用。

    运行方式：
    1. Anthropic 直连（默认）：
       python 05-bedrock-vertex.py
       （需要设置 ANTHROPIC_API_KEY）

    2. AWS Bedrock：
       set ANTHROPIC_BACKEND=bedrock
       set AWS_REGION=us-east-1
       python 05-bedrock-vertex.py
       （需要配置 AWS 凭证）

    3. Google Vertex：
       set ANTHROPIC_BACKEND=vertex
       set GCP_PROJECT_ID=your-project-id
       set GCP_REGION=us-central1
       set GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
       python 05-bedrock-vertex.py
    """

    # 打印认证方式演示和模型 ID 表（无需真实凭证也能看）
    bedrock_auth_demo()
    vertex_auth_demo()
    model_id_cheatsheet()

    # 尝试运行实际对话（需要配置对应后端的凭证）
    print("=" * 60)
    print("尝试运行实际对话...")
    print("=" * 60)

    try:
        client, model_id = create_client()

        # 简单对话
        print("\n--- 简单对话 ---")
        reply = simple_chat(client, model_id, "用一句话解释什么是云计算")
        print(f"你：用一句话解释什么是云计算")
        print(f"Claude：{reply}")

        # 流式对话（注释掉以避免过长输出）
        # print("\n--- 流式对话 ---")
        # streaming_chat(client, model_id, "Python 有哪些优点？")

    except AnthropicError as e:
        print(f"\nAPI 错误（这是正常的——如果没有配置对应后端的凭证）：{type(e).__name__}")
        print(f"错误信息：{str(e)[:200]}")
        print("\n提示：要运行实际对话，请配置对应后端的凭证：")
        print("  - Anthropic 直连：设置 ANTHROPIC_API_KEY")
        print("  - AWS Bedrock：设置 AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/AWS_REGION")
        print("  - Google Vertex：设置 GCP_PROJECT_ID + GOOGLE_APPLICATION_CREDENTIALS")
    except Exception as e:
        print(f"\n配置错误：{type(e).__name__}: {e}")
        print("\n这通常意味着缺少必要的环境变量配置。")
        print("查看上面的认证方式演示和模型 ID 表了解如何配置。")


if __name__ == "__main__":
    main()
```

## 运行方式

```bash
# 1. Anthropic 直连（默认，需要 ANTHROPIC_API_KEY）
python 05-bedrock-vertex.py

# 2. AWS Bedrock（需要配置 AWS 凭证）
# Windows PowerShell:
$env:ANTHROPIC_BACKEND="bedrock"
$env:AWS_REGION="us-east-1"
python 05-bedrock-vertex.py

# 3. Google Vertex（需要 GCP 项目和服务账号）
$env:ANTHROPIC_BACKEND="vertex"
$env:GCP_PROJECT_ID="your-project-id"
$env:GCP_REGION="us-central1"
$env:GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
python 05-bedrock-vertex.py
```

## 代码解析

### 核心设计：继承复用，API 完全一致

所有多云客户端都**继承**自核心客户端基类，只重写认证相关逻辑，上层 API 完全一致。这意味着：

```python
# 官方直连
from anthropic import Anthropic
client = Anthropic()
client.messages.create(...)       # ✓
client.messages.stream(...)       # ✓
client.beta.messages.create(...)  # ✓

# Bedrock
from anthropic import AnthropicBedrock
client = AnthropicBedrock(aws_region="us-east-1")
client.messages.create(...)       # ✓ 完全相同的调用！
client.messages.stream(...)       # ✓
client.beta.messages.create(...)  # ✓

# Vertex
from anthropic import AnthropicVertex
client = AnthropicVertex(project_id="...", region="...")
client.messages.create(...)       # ✓ 完全相同！
```

你学会了 `Anthropic` 客户端，就自动学会了所有多云客户端，没有额外学习成本。

### AWS 凭证链：Bedrock 的认证方式

`AnthropicBedrock` 使用 AWS 标准凭证链，按以下优先级查找凭证：

1. **显式传入参数**：`aws_access_key`、`aws_secret_key`、`aws_session_token`
2. **环境变量**：`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`
3. **AWS 配置文件**：`~/.aws/credentials`（通过 `aws_profile` 指定）
4. **IAM 角色（IMDS）**：EC2/ECS/EKS/Lambda 等 AWS 环境中的实例元数据服务

**生产环境最佳实践**：不要硬编码密钥，使用 IAM 角色。在 AWS 上运行时（如 EC2、Lambda），SDK 会自动获取凭证，你只需要传 `aws_region` 即可。

```python
# 生产环境代码（在 AWS 上运行）
client = AnthropicBedrock(aws_region="us-east-1")
# 不需要传任何密钥！IAM 角色自动处理认证
```

### GCP 认证：Vertex 的凭证链

`AnthropicVertex` 类似地使用 Google 认证链：

1. **显式传入**：`credentials` 对象或 `access_token`
2. **环境变量**：`GOOGLE_APPLICATION_CREDENTIALS` 指向服务账号 JSON 文件
3. **GCP 环境默认凭证**：GCE/GKE/Cloud Run/Cloud Functions 的默认服务账号

```python
# 本地开发：设置环境变量指向密钥文件
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
client = AnthropicVertex(
    project_id="my-project",
    region="us-central1",
)

# 生产环境（在 GCP 上运行）：同样不需要传密钥文件
client = AnthropicVertex(
    project_id="my-project",
    region="us-central1",
)
```

### 模型 ID 是最容易踩的坑

不同后端的模型 ID 格式**不一样**，这是多云使用时最常见的错误：

| 后端 | 模型 ID 格式特点 | 示例 |
|------|----------------|------|
| Anthropic 直连 | `-latest` 后缀可用 | `claude-3-5-sonnet-latest` |
| Bedrock | `anthropic.` 前缀 + `:0` 版本后缀 | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| Vertex | `@日期` 后缀，无 `anthropic.` 前缀 | `claude-3-5-sonnet@20241022` |

代码示例中的 `create_client()` 工厂函数提供了一个模型映射表，根据后端自动选择正确的模型 ID 格式，这是一个推荐的实践。

### 工厂模式：编写后端无关代码

示例中的 `create_client()` 函数是一个工厂模式，它：
1. 从环境变量读取后端配置
2. 创建对应类型的客户端
3. 返回正确格式的模型 ID
4. 业务代码（`simple_chat`、`streaming_chat` 等）完全不关心后端是什么

```python
# 业务代码——完全后端无关
client, model_id = create_client()
reply = simple_chat(client, model_id, "你好")
```

这种模式让你可以：
- 通过环境变量切换后端，无需修改业务代码
- 在开发环境用 Anthropic 直连，生产环境用 Bedrock/Vertex
- 实现多云灾备：一个后端故障时切换到另一个

### 异步客户端同样支持

所有多云客户端都有对应的异步版本，API 完全对称：

```python
# 同步
from anthropic import AnthropicBedrock
client = AnthropicBedrock(aws_region="us-east-1")
message = client.messages.create(...)

# 异步
from anthropic import AsyncAnthropicBedrock
async_client = AsyncAnthropicBedrock(aws_region="us-east-1")
message = await async_client.messages.create(...)
```

异步客户端的初始化参数与同步版本完全相同。

### 区域选择注意事项

1. **Bedrock 区域**：Claude 模型并非在所有 AWS 区域都可用。常用区域：`us-east-1`（弗吉尼亚）、`us-west-2`（俄勒冈）。请在 AWS Bedrock 控制台确认你想使用的区域支持 Claude。

2. **Vertex 区域**：常用区域：`us-central1`（爱荷华）、`europe-west1`（比利时）、`asia-northeast1`（东京）。`region="global"` 使用全局 endpoint。

3. **数据驻留**：选择区域时考虑合规要求，某些行业要求数据不离开特定地理区域。

## 常见问题

1. **Bedrock 报错 "You don't have access to the model"**：你需要在 AWS Bedrock 控制台的 "Model access" 页面申请访问 Claude 模型权限，申请后通常立即生效。

2. **Vertex 报错 "Permission denied"**：检查服务账号是否有 `aiplatform.endpoints.predict` 权限，以及 Vertex AI API 是否已在 GCP 项目中启用。

3. **可以在同一个应用中同时使用多个后端吗？** 当然可以！创建多个客户端实例即可：

```python
direct_client = Anthropic()
bedrock_client = AnthropicBedrock(aws_region="us-east-1")
vertex_client = AnthropicVertex(project_id="...", region="...")
```

4. **流式、工具调用、视觉等高级功能支持吗？** 全部支持。多云客户端继承了所有功能，用法与官方客户端完全一致。

5. **Beta 功能（如 Agents、Memory）在多云上可用吗？** 支持，但需要对应云平台支持这些 Beta 功能。客户端通过各自的 `_beta` 模块自动处理。

6. **如何自定义 base_url（私有部署/代理）？** 对于自定义代理或私有部署场景，仍然使用基础 `Anthropic` 客户端，直接传 `base_url` 参数：

```python
client = Anthropic(
    base_url="https://your-private-proxy.example.com/v1",
    api_key="your-key",
)
```

## 相关概念

- [客户端初始化与配置](../concepts/01-client-init.md) — 通用客户端配置（超时、重试、中间件等）
- [多云后端部署概念](../concepts/07-multi-cloud.md) — 多云架构设计、凭证链、继承复用原理
- [基础对话](01-basic-chat.md) — 学习 messages.create 的基础用法（后端无关）
- [流式对话](02-streaming-chat.md) — 流式响应在多云客户端上同样可用
- [Anthropic Python SDK 多云后端认证参考](../references/multi-cloud.md) — 多云客户端完整参数 API 参考
