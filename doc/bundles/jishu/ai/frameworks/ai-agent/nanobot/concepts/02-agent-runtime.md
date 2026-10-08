---
type: Concept
title: Agent 运行时
description: Agent 运行时由 AgentLoop 协调会话与上下文，AgentRunner 执行多轮 LLM 对话与工具调用，Provider 抽象支持多种 LLM 后端，Tools 自动发现并暴露给模型。
tags: [nanobot, agent-runtime, provider, tools, agent-loop]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: nanobot 源码信源
---

# Agent 运行时

Agent 运行时是 nanobot 的核心处理引擎，负责接收消息、构建上下文、调用 LLM、执行工具并返回响应。它由 AgentLoop、AgentRunner、Provider 抽象层和工具系统组成。

## AgentLoop

`AgentLoop` 是运行时的协调者，管理会话键、钩子和上下文构建。它通过 `from_config()` 工厂方法从 Pydantic 配置创建：

```python
agent_loop = agent_loop_class.from_config(
    runtime_config,
    bus,
    provider=provider,
    cron_service=cron,
    image_generation_provider_configs=image_gen_provider_configs(runtime_config),
    hook_factories=[create_file_edit_activity_hook],
    tool_registry=tools,
)
```

来源：`nanobot/cli/agent.py:172-180`

AgentLoop 提供两种处理路径：

1. **`process_direct()`**：直接处理单条消息，不经过 MessageBus（用于单发 CLI 和 SDK）
2. **`run()`**：从 MessageBus 消费入站消息的长运行循环（用于交互模式和网关）

在 classic CLI 交互模式中，这两种路径的区别清晰可见：

```python
# 单发模式 — 直接调用
response = await agent_loop.process_direct(
    message,
    session_id,
    on_progress=_make_progress(renderer),
    on_stream=renderer.on_delta,
    on_stream_end=renderer.on_end,
)

# 交互模式 — 通过 bus
bus_task = asyncio.create_task(agent_loop.run())
await bus.publish_inbound(InboundMessage(
    channel=cli_channel,
    sender_id="user",
    chat_id=cli_chat_id,
    content=user_input,
    metadata={"_wants_stream": True},
))
```

来源：`nanobot/cli/agent.py:247-253,302-405`

## LLM Provider 抽象

nanobot 支持多种 LLM 后端，全部构建在共同的基类之上。Provider 通过工厂函数 `make_provider()` 创建：

```python
from nanobot.providers.factory import make_provider

provider = make_provider(runtime_config)
```

来源：`nanobot/cli/agent.py:150`

已记录的 Provider 实现包括：

| Provider 类型 | 说明 |
|---------------|------|
| Anthropic | 原生 Anthropic Messages API |
| OpenAI 兼容 | OpenAI、OpenRouter、自定义端点、Ollama、vLLM、LM Studio |
| OpenAI Responses API | OpenAI Responses 状态保留 |
| Azure | Azure OpenAI |
| Bedrock | AWS Bedrock |
| GitHub Copilot | OAuth 认证 |
| OpenAI Codex | OAuth 认证 |

来源：`AGENTS.md:43`、`docs/providers.md`

Provider 选择遵循以下优先级：

1. 活动预设中的显式 `provider`（非 `"auto"`）直接使用
2. `provider: "auto"` 时，从模型名称关键词、配置的 API 密钥、本地 base URL 或网关 provider 推断
3. OAuth provider（如 OpenAI Codex、GitHub Copilot）需要显式登录和选择

模型通过命名 `modelPresets` 配置：

```json
{
  "modelPresets": {
    "primary": {
      "provider": "openrouter",
      "model": "anthropic/claude-opus-4.5",
      "maxTokens": 8192,
      "contextWindowTokens": 65536,
      "temperature": 0.1
    }
  },
  "agents": {
    "defaults": {
      "modelPreset": "primary"
    }
  }
}
```

来源：`docs/providers.md:28-52`

## 工具调用

AgentRunner 执行多轮 LLM 对话：发送消息到 provider，接收工具调用，执行工具，将结果反馈给模型，直到产生最终回复。

工具通过 `ToolRegistry` 注册和管理，自动发现机制有两种：

1. **pkgutil 扫描**：自动发现 `nanobot/agent/tools/` 下的内置工具模块
2. **entry-point 插件**：第三方包通过 `[project.entry-points."nanobot.tools"]` 注册

```toml
# pyproject.toml 中预留的插件入口（默认注释）
# [project.entry-points."nanobot.tools"]
# my_plugin = "my_package.plugins:MyTool"
```

来源：`pyproject.toml:112-115`

内置工具能力包括：

- 文件系统：读取、写入、编辑、列出、补丁
- Shell 执行：支持沙箱后端（如 bubblewrap）
- Web 搜索与抓取：含 SSRF 检查
- MCP 服务器：Model Context Protocol 集成
- Cron 定时任务与本地触发器
- 笔记本编辑
- 子代理生成
- 长运行任务 / 持续目标
- 图像生成
- 自修改

来源：`AGENTS.md:45`、`docs/concepts.md:162-174`

## 钩子系统

AgentLoop 支持生命周期钩子，用于可观测性和自定义。`Nanobot.run()` 接受可选的 `hooks` 参数：

```python
result = await bot.run(
    "Review this change",
    hooks=[AuditHook()],
)
```

钩子生命周期包括：

| 方法 | 触发时机 |
|------|----------|
| `wants_streaming()` | 是否需要逐 token 流式回调 |
| `before_iteration(context)` | 每次 LLM 调用前 |
| `on_stream(context, delta)` | 每个流式 token |
| `on_stream_end(context, *, resuming)` | 流式结束时 |
| `before_execute_tools(context)` | 工具执行前 |
| `after_iteration(context)` | 每次迭代后 |
| `finalize_content(context, content)` | 转换最终输出文本 |

来源：`docs/python-sdk.md:725-753`

## 模型覆盖与回退

SDK 支持在实例级和单次运行级覆盖模型：

```python
# 实例级默认模型
bot = Nanobot.from_config(model="openai/gpt-4.1")

# 单次运行覆盖
result = await bot.run("Summarize", model="openai/gpt-4.1-mini")

# 使用模型预设
bot = Nanobot.from_config(model_preset="fast")
result = await bot.run("Think deeply", model_preset="reasoning")
```

`model` 和 `model_preset` 互斥。运行时解析覆盖在 `run()` 内部通过 `runtime_resolver.resolve_override()` 完成。

来源：`nanobot/nanobot.py:177-181`、`docs/python-sdk.md:269-291`

## 流式运行

`run_streamed()` 方法返回 `RunStream` 句柄，内部使用容量为 256 的 `asyncio.Queue` 传递类型化事件：

```python
queue: asyncio.Queue[StreamEvent | object] = asyncio.Queue(maxsize=256)
emitter = SDKStreamEmitter(queue)
stream_hook = SDKStreamingHook(emitter)
```

来源：`nanobot/nanobot.py:224-226`

事件类型涵盖运行开始/完成/失败、文本增量/完成、推理增量/完成、工具开始/完成/失败共 10 种。

## 相关概念

- [整体架构](01-architecture.md)
- [消息总线](03-bus-messaging.md)
- [SDK 类型系统](04-sdk-types.md)
- [多接口架构](05-multi-interface.md)
