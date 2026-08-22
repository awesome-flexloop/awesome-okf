---
type: Concept
title: 模型 Provider 抽象
description: LLM 提供商的统一接口层——从适配器模式到 ProviderRegistry、能力声明与运行时委托
tags: [ai-agent, provider, llm, adapter, model-registry, multi-model, runtime-delegation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: hermes
    resource: /references/ai-agent-sources.md#hermes-agent
  - id: veadk
    resource: /references/ai-agent-sources.md#veadk-python
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
  - id: dsh
    resource: /references/ai-agent-sources.md#deepseek-harness
---

# 模型 Provider 抽象

AI Agent 框架需要支持多种 LLM 提供商（OpenAI、Anthropic、DeepSeek、本地模型等），Provider 抽象层解决"如何用统一接口接入不同模型"的问题。好的 Provider 抽象不仅是 API 适配，还包括模型能力声明、fallback 策略、流式处理、token 计数等。

## 为什么需要 Provider 抽象

不同 LLM 提供商的 API 存在显著差异：

| 差异维度 | 具体表现 |
|----------|---------|
| API 格式 | OpenAI 使用 `/chat/completions`，Anthropic 使用 `/messages`，本地模型使用 OpenAI-compatible 接口 |
| 消息格式 | OpenAI 用 `role: system/user/assistant/tool`，Anthropic 用不同的消息结构 |
| 工具调用 | Function Calling 格式各异（tool_calls vs content blocks） |
| 流式协议 | SSE 格式、chunk 结构、delta 表示不同 |
| 能力差异 | 有些模型不支持 vision、有些不支持 function calling、上下文窗口大小不同 |
| 认证方式 | API Key、OAuth、本地无认证 |

Provider 抽象层的作用是**屏蔽这些差异**，让上层 Agent 逻辑用统一方式与任何模型交互。

## 模式一：适配器模式（hermes-agent）

hermes-agent 使用经典的**适配器模式（Adapter Pattern）**，为每个 LLM 提供商实现一个适配器类，统一到共同接口。

### 适配器接口

```python
# 概念性伪代码：hermes-agent Provider 适配器
class BaseLLMProvider(ABC):
    """LLM Provider 基类"""
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """统一的聊天补全接口"""
        pass
    
    @abstractmethod
    async def count_tokens(self, messages: list[Message]) -> int:
        """Token 计数"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> ModelCapabilities:
        """返回模型能力声明"""
        pass

@dataclass
class ModelCapabilities:
    """模型能力声明"""
    supports_function_calling: bool = True
    supports_vision: bool = False
    supports_streaming: bool = True
    max_context_tokens: int = 128000
    max_output_tokens: int = 4096
```

### 适配器实现

hermes-agent 实现了 5+ 个 LLM provider 适配器：

```python
# 概念性示例
class OpenAIAdapter(BaseLLMProvider):
    async def chat_completion(self, messages, tools=None, stream=False, **kwargs):
        # 转换为 OpenAI 格式
        openai_messages = self._to_openai_messages(messages)
        openai_tools = self._to_openai_tools(tools) if tools else None
        # 调用 OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=openai_tools,
            stream=stream,
            **kwargs
        )
        # 转换回统一格式
        return self._from_openai_response(response)

class AnthropicAdapter(BaseLLMProvider):
    async def chat_completion(self, messages, tools=None, stream=False, **kwargs):
        # 转换为 Anthropic 格式（system 是顶层参数而非消息）
        system_prompt = self._extract_system(messages)
        anthropic_messages = self._to_anthropic_messages(messages)
        # 调用 Anthropic API
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=anthropic_messages,
            tools=tools,  # Anthropic 工具格式
            stream=stream,
            **kwargs
        )
        return self._from_anthropic_response(response)
```

### Agent 中的 Provider 选择

hermes-agent 的 `AIAgent` 在初始化时通过配置参数选择 provider：

```python
class AIAgent:
    def __init__(self, model: str = "gpt-4", provider: str = "openai", **kwargs):
        self.provider = self._get_provider(model, provider)
        # provider 可以是 "openai", "anthropic", "deepseek", "local", etc.
```

## 模式二：ProviderRegistry + ModelRegistry（Zleap-Agent）

Zleap-Agent 使用**双注册表**模式：ProviderRegistry 管理提供商适配器，ModelRegistry 管理具体模型实例及其能力覆盖。

```typescript
// packages/ai/src/registry.ts

// Provider 适配器接口
interface ProviderAdapter {
    id: string;
    createClient(config: ProviderConfig): LLMClient;
}

// 模型定义
interface ModelDefinition {
    id: string;
    providerId: string;           // 关联到哪个 provider
    modelName: string;            // 提供商侧的模型名
    capabilities?: Partial<ModelCapabilities>;  // 模型级能力覆盖
}

// 能力声明
interface ModelCapabilities {
    toolCalling: boolean;
    cacheBreakpoints: boolean;    // Anthropic 缓存断点
    thinking: boolean;            // 扩展思考模式
    tokenizer: TokenizerConfig;
    maxOutputTokens: number;
}

class ProviderRegistry {
    register(adapter: ProviderAdapter): void;
    get(id: string): ProviderAdapter;
    list(): ProviderAdapter[];
}

class ModelRegistry {
    register(model: ModelDefinition): void;
    get(id: string): ModelDefinition;
    list(): ModelDefinition[];
    
    getClient(modelId: string): LLMClient {
        const model = this.get(modelId);
        const provider = this.providerRegistry.get(model.providerId);
        return provider.createClient(model.config);
    }
}
```

### 模型级能力覆盖

Zleap 的关键设计是**模型级能力覆盖**——即使同一 provider 的不同模型也可能有不同能力，注册表允许在模型级别覆盖默认能力：

```yaml
# 概念性配置示例
providers:
  openai-compatible:
    baseUrl: "http://localhost:11434/v1"
    apiKey: "ollama"
models:
  gpt-4o:
    providerId: openai
    modelName: gpt-4o-2024-08-06
    capabilities:
      toolCalling: true
      vision: true
      maxOutputTokens: 16384
  llama3.1-local:
    providerId: openai-compatible
    modelName: llama3.1:70b
    capabilities:
      toolCalling: false      # 本地模型不支持 function calling
      vision: false
      maxOutputTokens: 4096
```

## 模式三：Service Seam（deepseek-harness/Cordis）

deepseek-harness 将 LLM 能力抽象为 Cordis **Service Seam**（Service Definition + Provider + Consumer），与工具系统使用相同的插件模式。

```typescript
// packages/llm/ - Service Definition
interface LLMService {
    complete(messages: Message[], options?: CompleteOptions): Promise<LLMResponse>;
    stream(messages: Message[], options?: StreamOptions): AsyncIterable<Chunk>;
    countTokens(messages: Message[]): Promise<number>;
}

// 内置 DeepSeek Provider
class DeepSeekLLMProvider extends Service implements LLMService {
    // 实现 DeepSeek API 调用
    async complete(messages, options) { /* ... */ }
}

// Consumer 使用
ctx.inject(['llm'], (llm: LLMService) => {
    // agent-loop 通过 ctx.llm 调用，不感知具体 provider
    const response = await llm.complete(messages, { tools });
});
```

这种设计的优势是：可以通过 Cordis 的配置覆盖（`intercept()`）和插件替换机制，在运行时切换 LLM provider，甚至可以同时使用多个 provider 实现 fallback 或 A/B 测试。

## 模式四：运行时委托（veadk-python）

veadk-python 的 Provider 抽象更激进——不仅抽象 LLM 调用，还将**整个执行循环**委托给不同的运行时后端：

```python
class Agent(LlmAgent):
    model_name: Union[str, list[str]]  # 支持模型名列表（多个候选）
    model_provider: str                # provider 标识
    model_api_base: str                # API 基础 URL
    runtime: str = "base"              # 运行时选择：base/codex/piagent

class Runner:
    def select_runtime(self, agent: Agent) -> BaseRuntime:
        if agent.runtime == "codex":
            return CodexRuntime(agent)
        elif agent.runtime == "piagent":
            return PiAgentRuntime(agent)
        else:
            return BaseRuntime(agent)
```

| 运行时 | 行为 |
|--------|------|
| `base_runtime` | veadk 自己的 Agent 循环实现 |
| `codex/runtime` | 委托给 OpenAI Codex Agent 运行时 |
| `piagent/runtime` | 委托给 PiAgent 运行时 |

这意味着同一个 Agent 配置（模型、工具、记忆）可以在不同的 Agent 执行引擎上运行。

## Provider 抽象的关键设计维度

### 1. 能力声明（Capability Declaration）

每个模型需要声明自己支持什么：

| 能力 | 说明 | 不支持时的降级策略 |
|------|------|------------------|
| Function Calling | 模型是否能调用工具 | 使用 ReAct prompting（文本中解析工具调用） |
| Vision | 是否支持图像输入 | 跳过图像，使用图像描述替代 |
| Streaming | 是否支持流式输出 | 切换为非流式调用 |
| Extended Thinking | 是否支持扩展思考 | 关闭 thinking 参数 |
| Context Window | 最大 token 数 | 触发更激进的上下文压缩 |

### 2. 消息格式转换

不同 provider 的消息格式差异是适配器中最繁琐的部分：

| 差异点 | OpenAI 格式 | Anthropic 格式 |
|--------|------------|----------------|
| System prompt | `role: "system"` 消息 | `system` 顶层参数 |
| Tool calls | `message.tool_calls[]` | `content` 中的 `tool_use` block |
| Tool results | `role: "tool"` 消息 | `content` 中的 `tool_result` block |
| 多模态 | `content: [{type: "text", ...}, {type: "image_url", ...}]` | `content: [{type: "text", ...}, {type: "image", ...}]` |

### 3. Token 计数

准确的 token 计数对于上下文管理至关重要：
- **使用模型自带的 tokenizer**：最准确但需要加载 tokenizer 模型
- **使用 tiktoken 等库**：对于 OpenAI 模型较准确
- **估算**：字符数/4（粗略估计，误差较大）

### 4. 错误处理与 Fallback

生产环境需要处理：
- **Rate limit**：指数退避重试
- **API 故障**：切换到备用 provider/model
- **上下文溢出**：自动压缩后重试
- **模型不支持请求的能力**：降级到替代方案

## 四种实现对比

| 维度 | hermes（适配器） | Zleap（双注册表） | dsh（Service Seam） | veadk（运行时委托） |
|------|----------------|-----------------|--------------------|--------------------|
| 抽象粒度 | API 调用 | API + 模型能力 | 服务级（可替换整个LLM实现） | 整个执行循环 |
| 切换复杂度 | 修改 agent 配置 | 修改模型注册 | Cordis 配置覆盖 | 修改 agent.runtime |
| 能力声明 | Provider 级别 | 模型级别覆盖 | Service 配置 | Runtime 级别 |
| 多模型同时使用 | MoA 内置 | 需自行实现 | 可注入多个llm服务 | Runtime 内处理 |
| 扩展性 | 新增适配器类 | 注册新 provider/model | 安装 Cordis 插件 | 新增 Runtime 类 |

## 相关概念

- [Agent 核心循环](01-agent-loop.md) — Provider 在循环中的角色
- [上下文管理](06-context-management.md) — Token 计数与窗口管理依赖 provider 能力
- [插件化架构模式](08-plugin-architecture.md) — Cordis Service Seam 模式
- [hermes-agent 架构深度走读](/examples/hermes-agent-deep-dive.md) — 适配器模式的代码级分析
