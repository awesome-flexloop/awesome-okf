---
okf_version: "0.2"
type: example
title: 搭建 Gateway 多 Agent 系统
description: 使用 GatewayRunner 搭建多平台多 Agent 网关系统，配置平台适配器（CLI/Web/API），实现会话隔离、LRU Agent 缓存、流式响应分发，将 Agent 能力接入多种消息渠道
tags: [hermes-agent, example, gateway, multi-agent, platform-adapter, session, streaming, lru-cache]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/gateway-multi-agent.md
  - /concepts/platform-plugin.md
  - /concepts/agent-core-loop.md
  - /concepts/memory-subsystem.md
sources:
  - id: hermes-agent-self
    resource: /references/hermes-agent-sources.md
    title: hermes-agent 源码参考
---

# 搭建 Gateway 多 Agent 系统

## 场景说明

本示例演示如何使用 hermes-agent 的 `GatewayRunner` 搭建多 Agent 网关系统。Gateway 是 hermes-agent 接入多种消息平台（CLI、Web、API Server、飞书、微信、Discord、Signal、WhatsApp 等 22+ 平台）的核心组件，负责管理平台适配器、会话隔离、Agent 实例 LRU 缓存、流式响应分发和跨会话并发控制。通过 Gateway，同一个 Agent 后端可以同时为多个平台的用户提供服务。

**前置条件**：
- Python ≥ 3.11 且 < 3.14
- 已安装 hermes-agent（`pip install hermes-agent`）
- 拥有一个兼容 OpenAI Chat Completions API 的模型服务
- 理解 [Gateway 多 Agent 概念](../concepts/gateway-multi-agent.md) 和 [平台插件概念](../concepts/platform-plugin.md)

## 完整代码示例

```python
"""
setup-gateway-multi-agent.py
演示：搭建 Gateway 多 Agent 网关系统，配置平台适配器
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional

# ── 步骤 1：配置日志 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gateway-example")


# ── 步骤 2：创建 Gateway 配置 ──

def create_gateway_config(hermes_home: Optional[Path] = None):
    """
    创建 GatewayConfig 配置对象。

    GatewayConfig 控制网关的行为：会话存储、平台配置、
    模型设置、工具启用、并发控制等。
    """
    from gateway.run import GatewayConfig
    from hermes_constants import set_hermes_home

    if hermes_home is None:
        hermes_home = Path.home() / ".hermes"
    hermes_home.mkdir(parents=True, exist_ok=True)
    set_hermes_home(hermes_home)

    config = GatewayConfig(
        # ── 基础配置 ──
        hermes_home=str(hermes_home),
        sessions_dir=str(hermes_home / "sessions"),

        # ── 模型配置 ──
        provider="openai",
        model="gpt-4o-mini",
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("OPENAI_API_KEY", ""),

        # ── 工具配置 ──
        toolsets=["web", "file", "terminal"],  # 全局启用的工具集
        max_iterations=50,                      # 最大工具调用轮次
        timeout_seconds=300,                    # 单轮对话超时

        # ── 会话配置 ──
        session_idle_timeout=3600,              # 会话空闲超时（秒）
        max_concurrent_sessions=10,             # 最大并发会话数
        agent_cache_size=100,                   # Agent LRU 缓存大小

        # ── 平台适配器配置 ──
        platforms={
            # CLI 平台（本地终端交互）
            "cli": {
                "enabled": True,
                "type": "cli",
            },
            # API Server 平台（HTTP API 接口）
            "api_server": {
                "enabled": True,
                "type": "api_server",
                "host": "127.0.0.1",
                "port": 8765,
                "cors_origins": ["*"],
                "auth_token": os.getenv("HERMES_API_TOKEN", ""),  # 可选认证
            },
        },

        # ── 流式响应配置 ──
        streaming_enabled=True,
        stream_chunk_size=4096,

        # ── 多 Profile 支持（可选）──
        multiplex_profiles=False,  # 启用多 Profile 隔离
    )

    return config


# ── 步骤 3：自定义平台适配器（可选）──
# 演示如何创建一个简单的自定义平台适配器

def create_custom_adapter():
    """
    创建自定义平台适配器示例。

    继承 BasePlatformAdapter，实现消息接收和发送接口，
    即可将 Agent 接入任意消息平台。
    """
    from gateway.platforms.base import BasePlatformAdapter, PlatformConfig
    from gateway.platform_registry import Platform
    from dataclasses import dataclass

    @dataclass
    class CustomPlatformConfig(PlatformConfig):
        """自定义平台配置。"""
        webhook_url: str = ""
        api_key: str = ""

    class CustomPlatformAdapter(BasePlatformAdapter):
        """
        自定义平台适配器示例。

        只需实现：
        1. start() - 启动平台监听（如启动 HTTP 服务器、连接 WebSocket）
        2. stop() - 停止平台
        3. _handle_incoming_message() - 处理收到的消息
        4. send_message() - 发送消息到平台
        """

        platform = Platform("custom")  # 注册平台类型

        def __init__(self, config: CustomPlatformConfig):
            super().__init__(config, self.platform)
            self.webhook_url = config.webhook_url
            self.api_key = config.api_key
            self._running = False

        async def start(self) -> bool:
            """启动适配器。连接平台、开始监听消息。"""
            logger.info(f"Custom adapter starting (webhook={self.webhook_url})")
            self._running = True
            # 在这里：启动 HTTP 服务器、连接 WebSocket、注册 webhook 等
            return True

        async def stop(self):
            """停止适配器。清理资源、断开连接。"""
            logger.info("Custom adapter stopping")
            self._running = False

        async def send_message(self, chat_id: str, text: str, **kwargs):
            """
            发送消息到平台。

            Args:
                chat_id: 目标会话/频道 ID
                text: 消息文本内容
                **kwargs: 附件、回复ID等额外参数
            """
            logger.info(f"[Custom→{chat_id}] {text[:100]}...")
            # 在这里：调用平台 API 发送消息
            return True

        async def _handle_incoming_message(self, chat_id: str, user_id: str,
                                           text: str, **kwargs):
            """
            处理从平台收到的消息。

            调用 self.run_turn() 将消息交给 Agent 处理，
            Agent 的响应会通过 send_message() 自动发送回去。
            """
            await self.run_turn(
                chat_id=chat_id,
                user_id=user_id,
                message=text,
                stream_callback=self._stream_chunk,
            )

        async def _stream_chunk(self, chunk: str, done: bool = False):
            """处理流式响应块。"""
            if done:
                logger.info("[Custom] Response complete")
            else:
                # 实时推送流式块到平台
                pass

    return CustomPlatformAdapter, CustomPlatformConfig


# ── 步骤 4：启动 Gateway ──

async def start_gateway_example():
    """
    启动 Gateway 的完整示例。

    GatewayRunner 管理所有平台适配器的生命周期，
    每个会话有独立的 AIAgent 实例（LRU 缓存），
    消息通过适配器接收→Agent 处理→适配器发送的流程。
    """
    from gateway.run import GatewayRunner, start_gateway

    # 创建配置
    config = create_gateway_config()
    logger.info("Gateway config created")

    # ── 方式 A：使用 start_gateway() 便捷函数 ──
    # 这是最简单的方式，自动创建 GatewayRunner 并启动
    logger.info("Starting gateway via start_gateway()...")
    # success = await start_gateway(config=config)
    # return success

    # ── 方式 B：手动创建 GatewayRunner（更灵活）──
    runner = GatewayRunner(config=config)

    # 注册自定义平台适配器（可选）
    CustomAdapter, CustomConfig = create_custom_adapter()
    custom_config = CustomConfig(
        enabled=True,
        webhook_url="https://example.com/webhook",
        api_key=os.getenv("CUSTOM_API_KEY", ""),
    )
    # runner.register_adapter(CustomAdapter(custom_config))

    # 注册启动/关闭钩子
    @runner.on_startup
    async def on_gateway_started():
        logger.info("✅ Gateway started successfully!")
        logger.info(f"   Platforms active: {list(runner.adapters.keys())}")

    @runner.on_shutdown
    async def on_gateway_stopped():
        logger.info("👋 Gateway stopped")

    # 添加消息中间件（可选，用于日志/过滤/修改）
    @runner.middleware
    async def log_all_messages(ctx, next_handler):
        """简单的日志中间件：记录所有消息。"""
        logger.info(
            f"[Message] platform={ctx.platform} chat={ctx.chat_id} "
            f"user={ctx.user_id} text={ctx.text[:50]}..."
        )
        response = await next_handler(ctx)
        return response

    # 启动 Gateway（阻塞直到停止）
    logger.info("Starting gateway manually...")
    logger.info("Press Ctrl+C to stop")
    success = await runner.start()
    return success


# ── 步骤 5：Gateway API 使用示例 ──

def gateway_api_usage_example():
    """
    演示如何通过 API Server 与 Gateway 交互。

    当 api_server 平台启用后，可以通过 HTTP API 发送消息，
    适用于 Web 前端、第三方服务集成等场景。
    """
    import httpx

    api_base = "http://127.0.0.1:8765"
    auth_token = os.getenv("HERMES_API_TOKEN", "")
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    # ── 发送消息（非流式）──
    def send_message(chat_id: str, text: str, user_id: str = "user1"):
        """发送消息并等待完整响应。"""
        response = httpx.post(
            f"{api_base}/v1/chat",
            headers=headers,
            json={
                "chat_id": chat_id,
                "user_id": user_id,
                "message": text,
                "stream": False,
            },
            timeout=300,
        )
        return response.json()

    # ── 发送消息（流式）──
    def send_message_streaming(chat_id: str, text: str, user_id: str = "user1"):
        """发送消息并接收流式响应。"""
        with httpx.stream(
            "POST",
            f"{api_base}/v1/chat",
            headers=headers,
            json={
                "chat_id": chat_id,
                "user_id": user_id,
                "message": text,
                "stream": True,
            },
            timeout=300,
        ) as response:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    yield data

    # ── 获取会话列表 ──
    def list_sessions():
        """获取活跃会话列表。"""
        response = httpx.get(f"{api_base}/v1/sessions", headers=headers)
        return response.json()

    # ── 获取会话历史 ──
    def get_session_history(chat_id: str):
        """获取指定会话的消息历史。"""
        response = httpx.get(
            f"{api_base}/v1/sessions/{chat_id}/history",
            headers=headers,
        )
        return response.json()

    # 使用示例
    print("=== Gateway API 示例 ===")
    print(f"API Base URL: {api_base}")
    print()
    print("发送消息: POST /v1/chat")
    print("流式响应: POST /v1/chat (stream: true)")
    print("会话列表: GET /v1/sessions")
    print("会话历史: GET /v1/sessions/{chat_id}/history")
    print()
    print("Example: send_message('chat-001', '你好，请介绍一下你自己')")

    return {
        "send_message": send_message,
        "send_message_streaming": send_message_streaming,
        "list_sessions": list_sessions,
        "get_session_history": get_session_history,
    }


# ── 主入口 ──

def main():
    """主函数：启动 Gateway 或演示 API 用法。"""
    import argparse

    parser = argparse.ArgumentParser(description="Hermes-Agent Gateway 示例")
    parser.add_argument(
        "--mode",
        choices=["start", "api-demo"],
        default="api-demo",
        help="运行模式：start=启动网关服务器，api-demo=演示API调用",
    )
    parser.add_argument(
        "--hermes-home",
        type=str,
        default=None,
        help="Hermes 主目录路径",
    )
    args = parser.parse_args()

    if args.mode == "start":
        # 启动 Gateway（异步事件循环）
        hermes_home = Path(args.hermes_home) if args.hermes_home else None
        config = create_gateway_config(hermes_home)

        if sys.platform == "win32":
            # Windows 需要特定的事件循环策略
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            asyncio.run(start_gateway_example())
        except KeyboardInterrupt:
            logger.info("Gateway interrupted by user")
    else:
        # 演示 API 用法
        gateway_api_usage_example()


if __name__ == "__main__":
    main()
```

## 逐步解释

### Gateway 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     GatewayRunner                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CLI Adapter  │  │ API Adapter  │  │ Feishu/...   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│  ┌──────┴─────────────────┴─────────────────┴───────┐      │
│  │              Delivery Router                     │      │
│  │  （消息路由、会话隔离、并发控制、中间件）          │      │
│  └──────┬─────────────────┬─────────────────┬──────┘      │
│         │                 │                 │              │
│  ┌──────┴───┐      ┌─────┴────┐      ┌─────┴────┐        │
│  │ Session  │      │ Session  │      │ Session  │         │
│  │  State   │      │  State   │      │  State   │         │
│  │ ┌──────┐ │      │ ┌──────┐ │      │ ┌──────┐ │         │
│  │ │Agent │ │      │ │Agent │ │      │ │Agent │ │  ← LRU  │
│  │ │AIAgt │ │      │ │AIAgt │ │      │ │AIAgt │ │   缓存  │
│  │ └──────┘ │      │ └──────┘ │      │ └──────┘ │         │
│  └──────────┘      └──────────┘      └──────────┘         │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  SessionStore (持久化会话历史)                     │     │
│  └──────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────┘
```

### 步骤 1：创建 GatewayConfig

`GatewayConfig` 是网关的核心配置对象，包含：
- **基础配置**：`hermes_home`、`sessions_dir` 等路径配置
- **模型配置**：`provider`、`model`、`base_url`、`api_key`，所有会话共享的默认模型
- **工具配置**：`toolsets`、`max_iterations`、`timeout_seconds`
- **会话配置**：空闲超时、最大并发数、Agent 缓存大小
- **平台配置**：`platforms` 字典，每个键是平台名，值是平台配置
- **流式配置**：是否启用流式响应、块大小
- **多 Profile**：`multiplex_profiles` 启用多用户 Profile 隔离

### 步骤 2：GatewayRunner 生命周期

1. **初始化**：`GatewayRunner(config=config)` 创建实例，加载配置
   - 创建 `SessionStore` 持久化会话历史
   - 创建 `DeliveryRouter` 消息路由
   - 初始化适配器字典 `self.adapters`

2. **启动**：`await runner.start()`
   - 获取 PID 文件锁（防止重复实例）
   - 启动系统监控（内存看门狗、循环活性检测）
   - 并行启动所有启用的平台适配器
   - 进入事件循环，等待消息

3. **消息处理流程**：
   - 适配器收到消息 → 封装 `TurnContext`
   - 经过中间件链 → 路由到对应会话
   - 获取或创建 `AIAgent` 实例（LRU 缓存）
   - 执行 Agent 循环（Think-Act-Observe）
   - 响应通过适配器发送回平台

4. **停止**：SIGINT/SIGTERM 或 `/stop` 命令
   - 停止接受新消息
   - 等待进行中的会话完成（可配置超时）
   - 停止所有适配器
   - 持久化会话状态
   - 释放 PID 锁

### 步骤 3：会话隔离与 Agent 缓存

- 每个 `(platform, chat_id)` 组合对应一个独立会话
- 每个会话有独立的 `SessionState`，包含：
  - `AIAgent` 实例（独立对话历史、TodoStore、记忆）
  - 会话元数据（创建时间、最后活跃时间、模型覆盖）
  - 租约状态（防止同一会话并发处理多个消息）
- Agent 实例使用 LRU 缓存策略：
  - 最近使用的 Agent 保持在内存中
  - 超出 `agent_cache_size` 时淘汰最久未使用的
  - 淘汰前持久化会话历史
- 会话空闲超时后，Agent 从缓存移除，历史保留在磁盘

### 步骤 4：平台适配器

内置支持 22+ 平台适配器：

| 平台 | 类型 | 说明 |
|------|------|------|
| CLI | cli | 本地终端交互 |
| API Server | api_server | HTTP REST API |
| Webhook | webhook | 通用 Webhook 接收 |
| Feishu | feishu | 飞书机器人 |
| WeChat | weixin | 微信公众号/企业微信 |
| Discord | discord | Discord 机器人 |
| Signal | signal | Signal 消息 |
| WhatsApp | whatsapp_cloud | WhatsApp Cloud API |
| Telegram | telegram | Telegram 机器人 |
| QQ Bot | qqbot | QQ 机器人 |
| ... | ... | 其他平台 |

自定义适配器需继承 `BasePlatformAdapter` 并实现：
- `start()` / `stop()`：生命周期管理
- `send_message()`：发送消息到平台
- 通过 `self.run_turn()` 处理传入消息

### 步骤 5：API Server 接口

API Server 平台启动后暴露 REST API：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/v1/chat` | POST | 发送消息（支持 stream=true/false） |
| `/v1/sessions` | GET | 列出活跃会话 |
| `/v1/sessions/{id}/history` | GET | 获取会话历史 |
| `/v1/sessions/{id}` | DELETE | 删除/重置会话 |
| `/v1/models` | GET | 列出可用模型 |
| `/health` | GET | 健康检查 |

### 步骤 6：中间件

Gateway 支持中间件模式，在消息处理前后插入自定义逻辑：
- 日志记录
- 消息过滤（如敏感词检查）
- 消息修改（如自动翻译）
- 统计和监控
- 权限验证

中间件签名：`async def middleware(ctx, next_handler)`

## 输出结果

使用 `--mode start` 启动 Gateway 后：

```
2026-08-23 14:30:00 [INFO] gateway.run: Starting gateway...
2026-08-23 14:30:01 [INFO] gateway.platforms.api_server: API server listening on 127.0.0.1:8765
2026-08-23 14:30:01 [INFO] gateway.run: ✅ Gateway started successfully!
2026-08-23 14:30:01 [INFO] gateway.run:    Platforms active: [Platform.CLI, Platform.API_SERVER]
```

API 调用示例：
```bash
# 发送消息
curl -X POST http://127.0.0.1:8765/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"test-001","message":"你好","stream":false}'

# 响应
{"response":"你好！我是 Hermes Agent，有什么可以帮助你的？","chat_id":"test-001"}
```

## 注意事项

1. **PID 文件锁**：Gateway 启动时会在 `hermes_home/gateway.pid` 写入 PID 文件，防止同一 HERMES_HOME 下启动多个实例。使用 `--replace` 参数可强制替换已有实例。

2. **会话线程安全**：同一会话（相同 chat_id）同时只能处理一个消息（通过 TurnLease 机制）。新消息会排队等待，避免同一 Agent 实例并发操作导致状态混乱。

3. **内存管理**：Gateway 内置内存监控，默认每 5 分钟检查一次内存使用。超过阈值时会触发会话缓存清理，将最久未使用的 Agent 持久化到磁盘后从内存移除。

4. **优雅关闭**：收到 SIGTERM 时，Gateway 会：停止接受新消息 → 等待进行中的 turn 完成（超时 30 秒）→ 停止适配器 → 持久化所有会话 → 退出。支持 systemd 集成。

5. **模型覆盖**：每个会话可以通过 API 或斜杠命令（如 `/model gpt-4o`）覆盖默认模型，覆盖状态在会话生命周期内保持有效。

6. **多 Profile 隔离**：启用 `multiplex_profiles=True` 后，每个 Profile 有独立的配置、凭证、会话存储和 Agent 缓存，适合多用户/多租户场景。

7. **流式响应**：启用流式响应时，Agent 的输出以 SSE（Server-Sent Events）格式逐块发送，客户端可以实时显示。API Server 的 `stream: true` 参数使用此功能。

8. **重启保护**：Gateway 检测到代码变更（git pull）后，会拒绝模型切换等危险操作，提示需要重启。`code_skew` 模块通过记录启动时的 git 指纹来检测变更。

9. **平台适配器错误隔离**：单个平台适配器启动失败不会影响其他平台。失败的平台会记录到 `_profile_failed_platforms`，可以通过重启命令重试。
