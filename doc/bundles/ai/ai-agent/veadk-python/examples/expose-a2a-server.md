---
okf_version: "0.2"
type: example
title: 暴露 A2A 服务端
description: 使用 VeA2AServer 将 Agent 暴露为 A2A（Agent-to-Agent）协议服务端，配置 Agent Card，通过 FastAPI 提供 JSON-RPC 接口，支持其他 Agent 通过标准协议发现和调用
tags: [veadk-python, example, a2a, agent-to-agent, a2a-server, agent-card, fastapi, json-rpc]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/a2a-protocol.md
  - /concepts/composite-agents.md
  - /concepts/agent-and-runner.md
sources:
  - id: veadk-python-self
    resource: /references/veadk-python-sources.md
    title: veadk-python 源码参考
---

# 暴露 A2A 服务端

## 场景说明

本示例演示如何使用 VeADK 将 Agent 暴露为 A2A（Agent-to-Agent）协议服务端。A2A 是 Google 提出的开放协议，定义了 Agent 之间互相发现、调用和协作的标准方式。通过 `VeA2AServer`，你的 Agent 会：
1. 暴露一个 `/.well-known/agent-card.json` 端点（Agent Card），描述自身能力
2. 通过 JSON-RPC over HTTP 接收任务请求
3. 异步执行 Agent 逻辑并返回结果
4. 支持流式响应、任务状态查询、取消等标准操作

这使得你的 Agent 可以被其他 A2A 兼容的客户端（如其他 Agent、前端界面、编排引擎）发现和调用，实现 Agent 间的互操作。

**前置条件**：
- Python ≥ 3.10
- 已安装 veadk-python 及其 A2A 依赖（`pip install "veadk-python[a2a]"`）
- 拥有一个兼容 OpenAI Chat Completions API 的模型服务
- 理解 [A2A 协议概念](../concepts/a2a-protocol.md)

## 完整代码示例

```python
"""
expose-a2a-server.py
演示：将 VeADK Agent 暴露为 A2A 协议服务端

运行方式:
    python expose-a2a-server.py

测试方式:
    curl http://localhost:8000/.well-known/agent-card.json
"""

import os
import asyncio
from typing import Optional

import uvicorn
from fastapi import FastAPI

from veadk import Agent, Runner
from veadk.a2a.ve_a2a_server import VeA2AServer, init_app
from veadk.memory.short_term_memory import ShortTermMemory
from veadk.knowledgebase import KnowledgeBase


# ── 步骤 1：创建业务 Agent ──

def create_translator_agent() -> Agent:
    """创建一个翻译 Agent（用于暴露为 A2A 服务）。"""
    return Agent(
        name="translator",
        description="多语言翻译助手，支持中英文互译，翻译准确流畅",
        instruction=(
            "你是一位专业的翻译专家。你的任务是将用户提供的文本"
            "在中文和英文之间进行高质量翻译。"
            "规则："
            "1. 如果输入是中文，翻译成英文"
            "2. 如果输入是英文，翻译成中文"
            "3. 保持原文的语气和风格（正式/非正式/技术/文学）"
            "4. 专业术语要准确"
            "5. 只输出翻译结果，不要添加解释"
        ),
    )


def create_code_reviewer_agent() -> Agent:
    """创建一个代码审查 Agent（示例：多个 Agent 可暴露在同一服务中）。"""
    return Agent(
        name="code_reviewer",
        description="代码审查助手，检查 Python 代码的质量、安全性和最佳实践",
        instruction=(
            "你是一位资深 Python 代码审查专家。审查用户提供的代码，从以下维度给出建议："
            "1. 代码质量（可读性、命名、结构）"
            "2. 潜在 Bug（逻辑错误、边界情况）"
            "3. 性能问题"
            "4. 安全隐患"
            "5. 最佳实践建议"
            "用中文输出审查结果，按严重程度分类（严重/建议/优化）。"
        ),
    )


def create_rag_agent() -> Agent:
    """创建一个带知识库的 RAG Agent。"""
    # 创建本地知识库
    kb = KnowledgeBase(backend="local", index="faq_docs")
    kb.add_from_text([
        "产品名称：智能客服系统 v3.0",
        "支持渠道：网页、微信小程序、飞书、钉钉",
        "最大并发会话数：10000",
        "响应时间：平均 < 500ms",
        "部署方式：Docker/Kubernetes",
        "定价：基础版免费，专业版 ¥999/月，企业版定制",
        "技术支持：工作日 9:00-18:00，企业版 7x24",
        "数据加密：传输 TLS 1.3，存储 AES-256",
    ])

    return Agent(
        name="product_expert",
        description="产品专家，回答关于智能客服系统的功能、定价、技术规格问题",
        instruction=(
            "你是智能客服系统的产品专家。根据知识库中的信息回答用户问题。"
            "如果知识库中没有相关信息，请告知用户联系销售。"
        ),
        knowledgebase=kb,
    )


# ── 步骤 2：创建 A2A 服务端 ──

def create_a2a_server_app(
    agent: Agent,
    server_url: str = "http://localhost:8000",
    app_name: str = "a2a_demo",
) -> FastAPI:
    """
    创建 A2A 服务端 FastAPI 应用。

    Args:
        agent: 要暴露的 Agent 实例
        server_url: 服务端对外可访问的 URL（用于 Agent Card）
        app_name: 应用名称

    Returns:
        FastAPI 应用实例
    """
    app = init_app(
        server_url=server_url,
        app_name=app_name,
        agent=agent,
        short_term_memory=ShortTermMemory(),
    )

    # 可以添加自定义路由
    @app.get("/health")
    async def health_check():
        """健康检查端点。"""
        return {"status": "healthy", "agent": agent.name}

    @app.get("/")
    async def root():
        """根路径，提供基本信息。"""
        return {
            "service": f"VeADK A2A Server - {agent.name}",
            "description": agent.description,
            "agent_card_url": f"{server_url}/.well-known/agent-card.json",
            "a2a_endpoint": f"{server_url}/",
        }

    return app


# ── 步骤 3：高级配置 - 自定义 Agent Card ──

from veadk.a2a.agent_card import get_agent_card
from a2a.types import AgentCapabilities, AgentCard, AgentProvider, AgentSkill


def create_custom_agent_card(agent: Agent, url: str) -> AgentCard:
    """
    创建自定义 Agent Card（包含更丰富的元数据）。

    Agent Card 是 A2A 协议中的服务发现机制，
    告诉客户端 Agent 的能力、技能、认证方式等。
    """
    # 定义 Agent 具备的技能
    skills = [
        AgentSkill(
            id="translate",
            name="translation",
            description="Translate text between Chinese and English",
            tags=["translation", "chinese", "english", "language"],
        ),
        AgentSkill(
            id="chat",
            name="chat",
            description="General conversation and Q&A",
            tags=["chat", "conversation"],
        ),
    ]

    # 定义 Agent 能力
    capabilities = AgentCapabilities(
        streaming=True,            # 支持流式输出
        push_notifications=False,  # 不支持推送通知
        # 可配置其他能力...
    )

    # 定义服务提供商
    provider = AgentProvider(
        organization="Your Company",
        url="https://your-company.com",
    )

    return AgentCard(
        name=agent.name,
        description=agent.description,
        url=url,
        version="1.0.0",
        capabilities=capabilities,
        skills=skills,
        provider=provider,
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        # security: {...},  # 认证方案配置
        # authentication: {...},  # 认证要求
    )


def create_a2a_server_with_custom_card(
    agent: Agent,
    server_url: str = "http://localhost:8000",
    app_name: str = "a2a_custom",
) -> FastAPI:
    """使用自定义 Agent Card 创建 A2A 服务端。"""
    # 创建 VeA2AServer 实例（而非使用 init_app 便捷函数）
    short_term_memory = ShortTermMemory()

    server = VeA2AServer(
        agent=agent,
        url=server_url,
        app_name=app_name,
        short_term_memory=short_term_memory,
    )

    # 替换默认 Agent Card
    server.agent_card = create_custom_agent_card(agent, server_url)

    # 构建 FastAPI 应用
    app = server.build()

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "agent": agent.name}

    return app


# ── 步骤 4：A2A 客户端调用示例（测试服务端）──

async def test_a2a_client(server_url: str = "http://localhost:8000"):
    """
    使用 A2A 客户端调用服务端（验证功能）。

    这部分代码演示如何从客户端视角与 A2A 服务端交互，
    实际部署时这段代码运行在其他 Agent 或客户端中。
    """
    from a2a.client import A2AClient

    print(f"\n=== A2A 客户端测试 ===")
    print(f"连接到: {server_url}")

    # 创建 A2A 客户端
    client = A2AClient(server_url)

    # 1. 获取 Agent Card（服务发现）
    agent_card = await client.get_agent_card()
    print(f"\n📋 Agent Card:")
    print(f"   名称: {agent_card.name}")
    print(f"   描述: {agent_card.description}")
    print(f"   版本: {agent_card.version}")
    print(f"   技能: {[s.name for s in agent_card.skills]}")
    print(f"   流式支持: {agent_card.capabilities.streaming}")

    # 2. 发送任务（非流式）
    print(f"\n📤 发送翻译任务...")
    task = await client.send_message(
        message="Translate to English: 人工智能正在改变世界。",
    )
    print(f"📥 任务状态: {task.status.state}")

    # 等待任务完成并获取结果
    while task.status.state not in ("completed", "failed", "canceled"):
        await asyncio.sleep(0.5)
        task = await client.get_task(task.id)

    if task.status.state == "completed":
        # 提取最终消息
        for msg in task.messages:
            for part in msg.parts:
                if hasattr(part, 'text') and part.text:
                    print(f"📥 翻译结果: {part.text}")
    else:
        print(f"❌ 任务失败: {task.status.message}")


# ── 步骤 5：启动服务 ──

def main():
    """主入口：启动 A2A 服务端。"""
    import argparse

    parser = argparse.ArgumentParser(description="VeADK A2A 服务端示例")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="监听端口")
    parser.add_argument(
        "--agent",
        choices=["translator", "reviewer", "product"],
        default="translator",
        help="要暴露的 Agent",
    )
    parser.add_argument(
        "--custom-card",
        action="store_true",
        help="使用自定义 Agent Card",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="启动后运行客户端测试（需先启动服务）",
    )
    args = parser.parse_args()

    server_url = f"http://localhost:{args.port}"

    # 选择 Agent
    agents = {
        "translator": create_translator_agent(),
        "reviewer": create_code_reviewer_agent(),
        "product": create_rag_agent(),
    }
    agent = agents[args.agent]

    print(f"=== VeADK A2A 服务端 ===")
    print(f"Agent: {agent.name} - {agent.description}")
    print(f"监听: {args.host}:{args.port}")
    print(f"Agent Card: {server_url}/.well-known/agent-card.json")
    print()

    # 创建应用
    if args.custom_card:
        app = create_a2a_server_with_custom_card(agent, server_url)
        print("使用自定义 Agent Card")
    else:
        app = create_a2a_server_app(agent, server_url)

    # 如果是测试模式，先启动服务再测试
    if args.test:
        # 在后台启动服务
        import threading
        import time

        def run_server():
            uvicorn.run(app, host=args.host, port=args.port, log_level="warning")

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(3)  # 等待服务启动

        # 运行客户端测试
        asyncio.run(test_a2a_client(server_url))
    else:
        # 正常启动服务
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
```

## 逐步解释

### A2A 协议核心概念

A2A（Agent-to-Agent）协议定义了 Agent 间互操作的标准：

| 概念 | 说明 |
|------|------|
| **Agent Card** | Agent 的"名片"，JSON 文档，描述名称、描述、能力、技能、端点 URL 等，通过 `/.well-known/agent-card.json` 暴露 |
| **Task** | 任务单元，客户端发送消息创建任务，服务端异步执行 |
| **Message** | 任务中的消息（用户消息或 Agent 响应），包含多个 Part |
| **Part** | 消息内容片段，可以是 Text、File、Data 等 |
| **JSON-RPC** | 通信协议，基于 HTTP 的 JSON-RPC 2.0 |
| **Streaming** | 流式响应，通过 SSE（Server-Sent Events）推送增量结果 |

### 步骤 1：创建业务 Agent

与普通 Agent 创建方式相同，没有特殊要求。任何 VeADK Agent 都可以暴露为 A2A 服务端，包括：
- 简单对话 Agent
- 带工具的 Agent
- 带知识库的 RAG Agent
- 组合 Agent（Sequential/Parallel/Loop）

### 步骤 2：使用 init_app 快速启动

`init_app()` 是最简便的方式，一步创建 FastAPI 应用：

```python
from veadk.a2a.ve_a2a_server import init_app
from veadk.memory.short_term_memory import ShortTermMemory

app = init_app(
    server_url="http://localhost:8000",  # 对外可访问的 URL
    app_name="my_a2a_app",               # 应用名
    agent=agent,                          # 要暴露的 Agent
    short_term_memory=ShortTermMemory(),  # 会话记忆
)
```

此函数自动完成：
1. 创建 `VeA2AServer` 实例
2. 创建内部 Runner
3. 创建 `A2AgentExecutor` 适配层
4. 生成默认 Agent Card
5. 构建 FastAPI 应用，注册所有 A2A 路由
6. 返回可直接运行的 FastAPI app

### 步骤 3：自定义 Agent Card

默认的 Agent Card 包含基本信息。如需更丰富的元数据（自定义技能、能力声明、认证配置等），直接操作 `VeA2AServer`：

1. 创建 `VeA2AServer` 实例
2. 通过 `AgentSkill` 定义 Agent 的技能列表（技能 ID、名称、描述、标签）
3. 通过 `AgentCapabilities` 声明能力（流式输出、推送通知等）
4. 通过 `AgentProvider` 标识提供方信息
5. 替换 `server.agent_card` 后调用 `server.build()`

### 步骤 4：A2A 客户端调用

从客户端角度与 A2A 服务端交互的流程：

1. **服务发现**：`GET /.well-known/agent-card.json` → 获取 Agent Card
2. **发送任务**：`POST /`（JSON-RPC `message/send`）→ 创建 Task
3. **轮询状态**：`POST /`（JSON-RPC `tasks/get`）→ 检查任务状态
4. **获取结果**：任务完成后从 Task 的 messages 中提取响应
5. **取消任务**（可选）：`POST /`（JSON-RPC `tasks/cancel`）
6. **流式响应**（可选）：使用 SSE 端点接收实时增量

### A2A 端点

服务启动后自动注册以下端点：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/.well-known/agent-card.json` | GET | Agent Card（服务发现） |
| `/` | POST | JSON-RPC 入口（message/send, tasks/get, tasks/cancel 等） |
| `/health` | GET | 健康检查（自定义添加） |

### 部署方式

1. **直接运行**：`python expose-a2a-server.py`
2. **uvicorn/gunicorn**：`uvicorn expose-a2a-server:app --host 0.0.0.0 --port 8000`
3. **Docker 容器化**：打包为 Docker 镜像部署到 K8s
4. **AgentKit 平台**：VeADK 与火山 AgentKit 集成，一键部署

### 认证配置（可选）

通过 `credential_service` 参数传入认证服务，实现 OAuth2/API Key 等认证：
```python
from veadk.auth.ve_credential_service import VeCredentialService

server = VeA2AServer(
    agent=agent,
    url=server_url,
    app_name=app_name,
    short_term_memory=ShortTermMemory(),
    credential_service=VeCredentialService(...),  # 认证服务
)
```

## 输出结果

启动服务后：

```
=== VeADK A2A 服务端 ===
Agent: translator - 多语言翻译助手，支持中英文互译，翻译准确流畅
监听: 0.0.0.0:8000
Agent Card: http://localhost:8000/.well-known/agent-card.json

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

查询 Agent Card：
```bash
$ curl http://localhost:8000/.well-known/agent-card.json
{
  "name": "translator",
  "description": "多语言翻译助手...",
  "url": "http://localhost:8000",
  "version": "0.x.x",
  "capabilities": {"streaming": false, ...},
  "skills": [{"id": "0", "name": "chat", "description": "...", "tags": ["chat", "talk"]}],
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  ...
}
```

客户端测试输出：
```
=== A2A 客户端测试 ===
连接到: http://localhost:8000

📋 Agent Card:
   名称: translator
   描述: 多语言翻译助手，支持中英文互译，翻译准确流畅
   版本: 1.0.0
   技能: ['translation', 'chat']
   流式支持: True

📤 发送翻译任务...
📥 任务状态: completed
📥 翻译结果: Artificial intelligence is changing the world.
```

## 注意事项

1. **server_url 必须是客户端可访问的地址**：Agent Card 中的 `url` 字段是客户端连接的地址。如果服务部署在反向代理或负载均衡后，`server_url` 应设为对外暴露的 URL（如 `https://your-domain.com/a2a`），而非内网地址。

2. **ShortTermMemory 必须传入**：`VeA2AServer` 需要 `short_term_memory` 来管理会话状态，否则每个请求都是独立的，无法维护多轮对话上下文。

3. **异步任务模型**：A2A 协议是异步的——发送消息后任务可能处于 `submitted`/`working` 状态，客户端需要轮询或使用流式接口等待完成。不要假设 send_message 会同步返回结果。

4. **CORS 配置**：如果 A2A 服务端需要被浏览器前端直接调用，需要在 FastAPI 中添加 CORS 中间件：
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
   ```

5. **生产环境部署**：生产环境建议使用多 worker uvicorn/gunicorn 部署，但注意 ShortTermMemory 在多 worker 间不共享。多实例部署需使用持久化会话存储（如数据库支持的 ShortTermMemory）。

6. **流式响应**：设置 AgentCapabilities(streaming=True) 后，客户端可以通过 SSE 连接实时接收 Agent 的输出流。默认的 VeA2AServer 已支持流式。

7. **A2A 依赖**：需要安装 `a2a` Python SDK（A2A 协议参考实现）。使用 `pip install "veadk-python[a2a]"` 安装所有 A2A 相关依赖。

8. **Task Store**：默认使用 `InMemoryTaskStore`，服务重启后任务历史丢失。生产环境可替换为持久化 Task Store（数据库实现）。

9. **与 AgentKit 集成**：VeADK A2A 服务与火山引擎 AgentKit 深度集成，部署到 AgentKit 平台后可获得自动生成前端、沙箱调试、技能市场等额外能力。

10. **远程 Agent 调用**：VeADK 也提供 `remote_ve_agent.py` 作为 A2A 客户端，可将远程 A2A Agent 包装为本地 sub_agent 使用，实现 Agent 间的分布式协作。
