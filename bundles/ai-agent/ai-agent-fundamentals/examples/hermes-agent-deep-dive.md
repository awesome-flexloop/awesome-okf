---
type: Example
title: hermes-agent 架构深度走读
description: 从 AIAgent 入口到 MoA 多代理循环——逐模块解析 hermes-agent v0.20.0 的核心架构、75+参数配置、工具注册表与设计模式
tags: [ai-agent, hermes, walkthrough, tool-registry, moa, design-patterns, python]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T02:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md#hermes-agent
---

# hermes-agent 架构深度走读

本示例通过 hermes-agent v0.20.0 的源码走读，展示一个**生产级 Python Agent 框架**的架构设计。hermes-agent 是本知识包覆盖的 12 个项目中功能最全面的 Python Agent 框架。

## 1. 整体架构鸟瞰

hermes-agent 的架构可以分为五层：

```
┌─────────────────────────────────────────────────────────┐
│ 传输层 (transports/)                                     │
│ CLI / Telegram / Discord / Webhook                      │
├─────────────────────────────────────────────────────────┤
│ Agent 层 (agent/)                                        │
│ AIAgent → agent_init.init_agent() → agent_loop          │
│  ├─ moa_loop.py (MoA 多代理)                            │
│  ├─ base.py (Agent 基类)                                │
│  └─ loop.py (工具调用循环)                               │
├─────────────────────────────────────────────────────────┤
│ 能力层                                                   │
│ toolsets.py (工具集组合) / skills/ (技能管理) / lsp/    │
│ pet/ (Prompt Engineering Toolkit)                        │
├─────────────────────────────────────────────────────────┤
│ 工具层 (ToolRegistry 单例)                               │
│ web_search / terminal / read_file / vision_analyze / ...│
│ (约 40 个核心工具)                                       │
├─────────────────────────────────────────────────────────┤
│ Provider 层（适配器模式）                                 │
│ OpenAI / Anthropic / DeepSeek / Local / ... (5+ 适配器) │
└─────────────────────────────────────────────────────────┘
```

## 2. AIAgent 入口：75+ 参数的可配置设计

AIAgent 类通过构造参数控制几乎所有行为，而不是通过子类化：

```python
class AIAgent:
    def __init__(
        self,
        # 模型配置
        model: str = "gpt-4",
        provider: str = "openai",
        api_key: str | None = None,
        api_base: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        
        # 系统与行为
        system_prompt: str | None = None,
        persona: str | None = None,           # 预设角色
        
        # 工具配置
        toolsets: list[str] | None = None,     # 工具集名称列表
        tools: list[Callable] | None = None,   # 自定义工具
        tool_choice: str = "auto",             # auto/required/none
        
        # 执行模式
        execution_mode: str = "concurrent",    # concurrent/sequential/segmented
        max_concurrent_tools: int = 5,
        
        # 安全与授权
        check_fn: Callable | None = None,      # 工具授权函数
        check_fn_ttl: int = 300,              # 授权缓存 TTL（秒）
        allow_dangerous_commands: bool = False,
        
        # 记忆与上下文
        memory_enabled: bool = True,
        context_window: int = 128000,
        compression_threshold: float = 0.8,
        
        # 多代理
        moa_config: MoAConfig | None = None,   # MoA 配置
        
        # 回调与观测
        on_tool_start: Callable | None = None,
        on_tool_end: Callable | None = None,
        on_llm_start: Callable | None = None,
        on_llm_end: Callable | None = None,
        on_error: Callable | None = None,
        
        # ... 总计 75+ 参数
    ):
```

**设计决策分析**：使用大参数列表而非继承体系的好处是——配置集中、所有行为可从构造函数一目了然、不需要理解继承树。代价是参数列表长，但通过分组和默认值缓解了这个问题。

### agent_init 模块化初始化

实际初始化逻辑委托给 `agent_init.py`，将 75+ 参数的配置分配给各子系统：

```python
# agent/agent_init.py (概念性)
def init_agent(agent: AIAgent):
    """根据 AIAgent 配置初始化各子系统"""
    
    # 1. 初始化 Provider 适配器
    agent.provider_adapter = create_provider(
        provider=agent.provider,
        model=agent.model,
        api_key=agent.api_key,
        api_base=agent.api_base,
    )
    
    # 2. 初始化 ToolRegistry 并加载工具
    registry = ToolRegistry.get_instance()
    if agent.toolsets:
        tools = resolve_toolsets(agent.toolsets)  # 解析 includes/excludes
        for tool in tools:
            registry.register(tool.name, tool.func, tool.schema)
    for custom_tool in agent.tools or []:
        registry.register(custom_tool.__name__, custom_tool, infer_schema(custom_tool))
    
    # 3. 初始化记忆系统
    if agent.memory_enabled:
        agent.memory = create_memory(agent.memory_config)
    
    # 4. 初始化 MoA（如果配置）
    if agent.moa_config:
        agent.moa_client = MoAClient(agent.moa_config)
    
    # 5. 设置回调
    agent.callbacks = Callbacks(
        on_tool_start=agent.on_tool_start,
        on_tool_end=agent.on_tool_end,
        # ...
    )
```

## 3. 工具注册表与工具集组合

### ToolRegistry 单例

```python
class ToolRegistry:
    _instance: "ToolRegistry | None" = None
    _tools: dict[str, Tool]
    _categories: dict[str, list[str]]  # 分类索引
    
    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._tools = {}
            cls._instance._categories = {}
        return cls._instance
```

单例模式保证整个进程中工具注册表是唯一的——无论从哪里注册工具，所有 AIAgent 实例都能看到。

### 工具集 DAG 解析

`toolsets.py` 的 TOOLSETS 字典支持 `includes` 嵌套，形成 DAG：

```python
TOOLSETS = {
    "web": {
        "tools": ["web_search", "web_extract", "web_fetch"]
    },
    "terminal": {
        "tools": ["terminal", "process", "kill_process"]
    },
    "file": {
        "tools": ["read_file", "write_file", "patch", "search_files", "list_directory"]
    },
    "hermes-core": {
        "includes": ["web", "terminal", "file"],  # 嵌套引用
        "tools": ["vision_analyze", "image_generate", "skills_list", ...]
    },
    "coding": {
        "includes": ["hermes-core"],
        "tools": ["git_operations", "test_runner", "linter", "lsp_hover", ...]
    },
    "debugging": {
        "includes": ["hermes-core"],
        "tools": ["lsp_definition", "lsp_references", "debug_breakpoint", ...]
    },
    "coding-full": {
        "includes": ["coding", "debugging"],  # 嵌套多层
        "tools": []
    },
    "webhook-safe": {
        "includes": ["hermes-core"],
        "exclude": ["terminal", "write_file", "patch"]  # 排除危险工具
    }
}
```

解析时使用 DFS 遍历 includes，合并 tools 列表，应用 exclude，检测循环引用。

## 4. 核心循环实现

```python
# agent/loop.py (概念性)
async def agent_loop(agent: AIAgent, messages: list[Message]) -> Message:
    """Agent 主循环"""
    
    while True:
        # 1. 构建工具定义列表（发送给 LLM）
        available_tools = agent.get_available_tools()
        tool_definitions = [t.to_openai_schema() for t in available_tools]
        
        # 2. 调用 LLM
        response = await agent.provider_adapter.chat_completion(
            messages=messages,
            tools=tool_definitions if tool_definitions else None,
            tool_choice=agent.tool_choice,
        )
        
        # 3. 检查是否需要工具调用
        if not response.tool_calls:
            # 无工具调用 → 循环结束
            return response.message
        
        # 4. 工具授权
        if agent.check_fn:
            for tc in response.tool_calls:
                if not await check_tool_authorization(agent, tc):
                    # 授权失败 → 注入错误消息，继续循环让 LLM 处理
                    messages.append(make_error_message(tc, "Authorization denied"))
                    continue
        
        # 5. 执行工具（按执行模式）
        if agent.execution_mode == "concurrent":
            results = await execute_tools_concurrent(
                response.tool_calls, agent.max_concurrent_tools
            )
        elif agent.execution_mode == "sequential":
            results = await execute_tools_sequential(response.tool_calls)
        else:  # segmented
            results = await execute_tools_segmented(response.tool_calls)
        
        # 6. 将工具结果追加到消息历史
        for tc, result in zip(response.tool_calls, results):
            messages.append(make_tool_result_message(tc, result))
        
        # 7. 检查循环卫生（防止无限循环）
        if detect_loop(messages):
            return make_handoff_message("Loop detected, asking for user input")
```

## 5. MoA（Mixture of Agents）实现

MoA 通过 `MoAClient` 门面类和 `MoAChatCompletions` 实现，对外暴露与 OpenAI 兼容的接口：

```python
# agent/moa_loop.py (概念性)
class MoAClient:
    """MoA 客户端，接口兼容 OpenAI client"""
    
    def __init__(self, config: MoAConfig):
        # Aggregator: 主 Agent（通常使用更强的模型）
        self.aggregator = AIAgent(
            model=config.aggregator.model,
            provider=config.aggregator.provider,
            system_prompt=AGGREGATOR_PROMPT,
        )
        
        # References: 多个参考 Agent
        self.references = [
            AIAgent(model=ref.model, provider=ref.provider,
                    system_prompt=ref.prompt)
            for ref in config.references
        ]
        
        # 暴露 chat.completions 接口（OpenAI 兼容）
        self.chat = MoAChatCompletions(self)

class MoAChatCompletions:
    def __init__(self, client: MoAClient):
        self.client = client
    
    async def create(self, messages: list, **kwargs):
        """兼容 openai.chat.completions.create()"""
        # Phase 1: Fan-out - 并行获取所有 reference 的回答
        reference_tasks = [
            ref.provider_adapter.chat_completion(messages, **kwargs)
            for ref in self.client.references
        ]
        reference_responses = await asyncio.gather(*reference_tasks)
        
        # Phase 2: 构建 aggregator 输入
        aggregator_messages = self._build_aggregator_messages(
            messages, reference_responses
        )
        
        # Phase 3: Aggregator 综合回答
        return await self.client.aggregator.provider_adapter.chat_completion(
            aggregator_messages, **kwargs
        )
    
    def _build_aggregator_messages(self, original_messages, reference_responses):
        """将原始消息和 reference 回答组合成 aggregator 的输入"""
        messages = list(original_messages)
        messages.append(Message(
            role="system",
            content="Here are responses from multiple AI assistants. "
                    "Synthesize their insights to provide the best answer."
        ))
        for i, resp in enumerate(reference_responses):
            messages.append(Message(
                role="system",
                content=f"[Assistant {i+1}]: {resp.message.content}"
            ))
        return messages
```

使用方式与普通 OpenAI 客户端一致——这是关键的设计，让 MoA 可以作为透明的替换层：

```python
# 使用 MoA 和使用普通模型一样
client = MoAClient(moa_config)
response = await client.chat.completions.create(
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
```

## 6. 设计模式盘点

hermes-agent 中可以识别出 13 种设计模式：

| 模式 | 应用位置 | 作用 |
|------|---------|------|
| **Singleton** | ToolRegistry | 全局唯一工具注册表 |
| **Adapter** | Provider 层（5+适配器） | 统一不同 LLM API |
| **Facade** | MoAClient | 简化 MoA 复杂子系统 |
| **Strategy** | execution_mode | 三种工具执行策略可切换 |
| **Composite** | TOOLSETS（includes嵌套） | 工具集的组合嵌套 |
| **Observer** | Callbacks（on_tool_start等） | 事件通知与观测 |
| **Factory** | create_provider()/init_agent() | 创建对象而不指定具体类 |
| **Guard** | check_fn + TTL缓存 | 工具授权门控 |
| **Chain of Responsibility** | 授权检查→执行→结果注入 | 请求沿处理链传递 |
| **Template Method** | agent_loop 结构 | 固定循环骨架，步骤可配置 |
| **Proxy** | MoAClient（接口兼容） | 控制对多Agent的访问 |
| **Decorator** | Callback wrapping | 透明添加观测行为 |
| **Circuit Breaker** | 瞬态故障抑制 | 授权服务故障时的降级 |

## 7. 安全机制多层防御

hermes-agent 的安全设计值得注意：

1. **check_fn TTL 缓存**：授权函数的结果缓存 TTL 秒，避免对同一工具的重复授权弹窗
2. **瞬态故障抑制**：授权服务暂时不可用时，短时间内不重复请求
3. **路径安全检查**：文件工具检查 `../` 路径遍历
4. **危险命令排除**：`webhook-safe` 工具集排除 terminal/write_file/patch
5. **插件覆盖授权**：插件可以注册自己的授权逻辑，覆盖默认 check_fn
6. **循环卫生检测**：检测重复的工具调用模式，防止无限循环

## 关键收获

通过 hermes-agent 的走读，可以总结出生产级 Python Agent 框架的关键设计要点：

1. **参数化优于继承**：75+ 构造参数而非复杂继承树，让配置集中可见
2. **模块化初始化**：`init_agent()` 将配置分发给各子系统，避免构造函数膨胀
3. **DAG 工具集组合**：includes/excludes 支持场景化工具裁剪，避免重复列举
4. **接口透明的多代理**：MoAClient 对外暴露与单模型一致的接口，降低使用门槛
5. **多层安全防御**：授权门控、路径检查、危险排除、循环检测层层叠加
6. **适配器隔离外部依赖**：所有 LLM 交互通过适配器，切换模型不影响核心逻辑
