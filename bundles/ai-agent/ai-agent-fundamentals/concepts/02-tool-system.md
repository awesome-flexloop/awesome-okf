---
type: Concept
title: 工具系统
description: AI Agent 的工具注册、函数调用、授权门控、执行模式与工具集组合——从 ToolRegistry 单例到 Capability Seam 模式
tags: [ai-agent, tool-system, function-calling, tool-registry, authorization, capability-seam]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:20:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: hermes
    resource: /references/ai-agent-sources.md#hermes-agent
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
  - id: dsh
    resource: /references/ai-agent-sources.md#deepseek-harness
  - id: cordis
    resource: /references/ai-agent-sources.md#cordis
---

# 工具系统

工具（Tool）是 Agent 与外部世界交互的桥梁。没有工具，Agent 只能"思考"不能"行动"；有了工具，Agent 可以搜索网页、执行代码、读写文件、调用 API、操作数据库。工具系统是 Agent 框架最核心的子系统之一。

## 工具的定义

一个工具通常包含以下要素：

| 要素 | 说明 |
|------|------|
| **名称（name）** | 唯一标识符，LLM 通过名称选择工具 |
| **描述（description）** | 告诉 LLM 这个工具做什么、何时使用 |
| **参数模式（parameters schema）** | JSON Schema 定义输入参数格式 |
| **执行函数（handler/callable）** | 实际执行工具逻辑的函数 |
| **权限/标签（permissions/tags）** | 工具的安全级别、分类标签 |

在 Function Calling API 中，工具以 JSON Schema 形式传递给 LLM，LLM 返回工具名称和参数后，框架负责执行并将结果注入对话。

## hermes-agent：ToolRegistry 单例 + 工具集组合

### ToolRegistry 注册表

hermes-agent 使用 `ToolRegistry` 单例模式管理所有可用工具。每个工具注册时提供名称、描述、参数 schema 和执行函数：

```python
# 概念性伪代码：hermes-agent 工具注册
class ToolRegistry:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, name: str, func: Callable, schema: dict, **kwargs):
        """注册工具到全局注册表"""
        self._tools[name] = Tool(name=name, func=func, schema=schema, **kwargs)
    
    def get(self, name: str) -> Tool:
        return self._tools[name]
    
    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())
```

### 工具集（Toolsets）组合

hermes-agent 的 `toolsets.py`（1000+ 行）定义了**工具集**机制——将相关工具分组，并支持嵌套组合：

```python
# 核心工具集（所有场景都需要的基础工具）
_HERMES_CORE_TOOLS = [
    "web_search", "web_extract",      # 网络能力
    "terminal", "process",            # 命令执行
    "read_file", "write_file", "patch", "search_files",  # 文件操作
    "vision_analyze", "image_generate",  # 多模态
    "skills_list", "skill_view", "skill_manage",  # 技能管理
    # ... 约 40 个核心工具
]

# 工具集字典：支持 includes 嵌套
TOOLSETS = {
    "hermes-core": _HERMES_CORE_TOOLS,
    "debugging": {
        "includes": ["hermes-core"],
        "tools": ["lsp_hover", "lsp_definition", "lsp_references", "debug_breakpoint"]
    },
    "coding": {
        "includes": ["hermes-core", "debugging"],
        "tools": ["git_operations", "test_runner", "linter"]
    },
    "hermes-telegram": {
        "includes": ["hermes-core"],
        "tools": ["telegram_send", "telegram_reply"]
    },
    "hermes-discord": {
        "includes": ["hermes-core"],
        "tools": ["discord_send", "discord_reply"]
    },
    "webhook-safe": {
        # Webhook 场景的安全工具集（排除危险操作）
        "includes": ["hermes-core"],
        "exclude": ["terminal", "write_file", "patch"]
    }
}
```

工具集的 `includes` 支持嵌套引用，形成有向无环图（DAG），最终解析出扁平的工具列表。`exclude` 用于排除特定工具（如安全场景禁用终端）。

### 工具执行流程

hermes-agent 的工具执行流程包含多个安全层：

1. **工具选择**：LLM 返回 `tool_calls` 列表
2. **授权检查（check_fn）**：每个工具调用前通过授权函数检查
   - TTL 缓存：同一工具短时间内重复调用不重复授权
   - 瞬态故障抑制：授权服务临时故障时的降级策略
3. **执行模式路由**：并发/顺序/分段
4. **结果验证**：检查工具返回值格式
5. **结果注入**：将结果序列化为 LLM 可理解的格式追加到消息历史

## Zleap-Agent：按 Workspace 作用域过滤的 ToolRegistry

Zleap-Agent 同样使用 Registry 模式，但工具是按 **Workspace 作用域** 过滤的：

```typescript
// 概念性伪代码：Zleap Workspace 工具过滤
class AgentRuntime {
    registerTool(tool: Tool): void {
        this.toolRegistry.register(tool);
    }
    
    createSpaceContext(space: Workspace): WorkContext {
        // 按 allowedToolIds 过滤工具
        const availableTools = new Map<string, Tool>();
        for (const toolId of space.allowedToolIds) {
            const tool = this.toolRegistry.get(toolId);
            if (tool) availableTools.set(toolId, tool);
        }
        return {
            availableTools,
            callTool: async (toolId, args) => {
                // 运行时再次检查：Workspace 外的工具调用抛出异常
                if (!availableTools.has(toolId)) {
                    throw new Error(`tool_not_allowed: ${toolId} not in workspace`);
                }
                return this.executeTool(toolId, args);
            }
        };
    }
}
```

**关键安全设计**：`callTool` 在运行时再次检查工具是否在当前 Workspace 的 `allowedToolIds` 中，即使 LLM 试图通过某种方式调用未授权工具，也会被运行时拦截。

## deepseek-harness：Capability Seam 三角色模式

deepseek-harness（基于 Cordis）将工具系统抽象为**能力缝（Capability Seam）**，每个能力由三个角色组成：

### 三角色模型

| 角色 | 职责 | 示例 |
|------|------|------|
| **Service Definition** | 定义接口（TypeScript 类型 + Schema） | `llm` 包定义 `LLMService` 接口 |
| **Service Provider** | 实现接口，注册到 Context | `deepseek` provider 实现 `LLMService` |
| **Consumer** | 声明依赖并使用服务 | `core` 包的 agent-loop 消费 `LLMService` |

```typescript
// 1. Service Definition（接口定义）
interface LLMService {
    complete(messages: Message[]): Promise<LLMResponse>;
    stream(messages: Message[]): AsyncIterable<Chunk>;
}

// 2. Service Provider（实现 + 注册）
class DeepSeekProvider extends Service implements LLMService {
    async complete(messages: Message[]): Promise<LLMResponse> {
        // 调用 DeepSeek API
    }
    
    constructor(ctx: Context) {
        super(ctx, 'llm');  // 注册为 'llm' 服务
    }
}

// 3. Consumer（使用）
ctx.inject(['llm'], (llm: LLMService) => {
    // agent-loop 使用 llm.complete()
});
```

### 内置能力包

deepseek-harness 通过独立的 npm 包提供丰富的工具能力：

| 包 | 能力 | Provider 选项 |
|----|------|--------------|
| `llm` | LLM 推理 | DeepSeek（内置），可扩展 |
| `shell` | Shell 命令执行 | local（本地）、pwsh（PowerShell） |
| `fs` | 文件系统操作 | 本地文件系统 + 安全策略 |
| `web` | Web 搜索/抓取 | search、fetch |
| `mcp` | MCP 协议工具 | MCP server 连接 |
| `lsp` | Language Server | LSP 协议 |
| `terminal` | 持久终端会话 | 终端复用 |
| `sandbox` | 沙箱执行 | E2B 沙箱 |
| `subagent` | 子代理委派 | 子代理 |

### 注册即副作用

Cordis 的设计原则是**注册即副作用**：所有功能贡献通过 `ctx.effect()` 注册，返回 disposer 函数用于清理：

```typescript
ctx.effect(() => {
    // 注册工具
    const tool = ctx.registry.register('search', searchHandler);
    // 返回清理函数（Fiber dispose 时调用）
    return () => tool.dispose();
});
```

## 工具系统设计模式总结

### 模式一：全局注册表（Registry Pattern）

hermes-agent 和 Zleap-Agent 都使用 Registry 模式——一个中心化的注册表存储所有可用工具。

- **优点**：简单直接，工具查找 O(1)
- **缺点**：全局状态、难以隔离（Zleap 通过 Workspace 作用域过滤弥补）

### 模式二：能力缝（Capability Seam）

Cordis/dsh 使用 Service Definition/Provider/Consumer 三角色分离。

- **优点**：接口与实现分离、可热替换、依赖注入、自动生命周期管理
- **缺点**：概念复杂度高、需要追踪服务注册和消费关系

### 模式三：工具集组合（Toolset Composition）

hermes-agent 的 `TOOLSETS` 字典支持 `includes` 嵌套和 `exclude` 排除。

- **优点**：场景化工具配置、避免重复列举、安全场景快速裁剪
- **缺点**：嵌套解析增加复杂度，需要 DAG 循环检测

### 模式四：作用域过滤（Scope Filtering）

Zleap-Agent 的 Workspace 级 `allowedToolIds` 实现细粒度权限控制。

- **优点**：强隔离、最小权限原则
- **缺点**：需要为每个 Workspace 配置工具白名单

## 工具安全多层防御

所有四个框架都实现了多层安全防御：

| 防御层 | hermes | Zleap | dsh/Cordis |
|--------|--------|-------|------------|
| LLM 提示工程 | system prompt 约束 | system prompt + workspace prompt | system prompt |
| 工具描述约束 | 清晰描述工具用途 | 按 workspace 展示可用工具 | Service 级别 |
| 运行时授权 | check_fn TTL 缓存 | allowedToolIds 运行时检查 | guard 包 + 策略 |
| 沙箱隔离 | 可选 sandbox | 无内置 | sandbox 包 + E2B |
| 审计日志 | 回调钩子 | EventBus 全量事件 | Session log（可重建） |
| 路径安全 | 路径遍历检查 | workspace 内文件隔离 | fs 策略 |

## 相关概念

- [Agent 核心循环](01-agent-loop.md) — 工具调用在循环中如何被触发和处理
- [插件化架构模式](08-plugin-architecture.md) — Capability Seam 模式的底层 Cordis 实现
- [多智能体编排](04-multi-agent.md) — 子代理如何作为"工具"被调用
- [Cordis 插件系统深度解析](/examples/cordis-plugin-system.md) — Cordis Fiber/Service/Registry 代码级分析
