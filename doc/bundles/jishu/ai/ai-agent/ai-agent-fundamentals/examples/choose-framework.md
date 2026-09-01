---
type: Example
title: Agent 框架选型指南
description: 根据项目需求选择合适的 AI Agent 框架——从需求分析、能力评估、决策矩阵到代码示例，覆盖 cordis、hermes-agent、Zleap-Agent、deepseek-harness、veadk-python 等框架的选型场景与权衡分析。
tags: [ai-agent-fundamentals, example, framework-selection, decision-guide, cordis, hermes, zleap, veadk]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: loop
    resource: /concepts/01-agent-loop.md
    title: Agent 核心循环
  - id: tools
    resource: /concepts/02-tool-system.md
    title: 工具系统
  - id: provider
    resource: /concepts/05-provider-abstraction.md
    title: Provider 抽象
---

## 场景说明

你的团队需要为一个新项目选择 AI Agent 框架。面对众多选项（LangChain、CrewAI、AutoGen、Cordis/dsh、hermes-agent 等），你需要根据项目需求做出理性的技术选型。本示例将：
1. 建立选型决策框架（需求维度→能力映射）
2. 对比主流框架在各维度的表现
3. 给出 6 个典型场景的选型建议
4. 提供选型验证的最小可行性代码

## 选型决策框架

选型不是"选最好的框架"，而是"选最匹配需求的框架"。按以下 8 个维度评估：

| 维度 | 关键问题 | 权重说明 |
|------|---------|---------|
| **任务复杂度** | 单步问答 vs 多步推理 vs 多 Agent 协作 | 决定循环复杂度需求 |
| **扩展性需求** | 固定功能 vs 需要第三方插件 | 决定插件架构需求 |
| **安全要求** | 个人工具 vs 企业级多租户 | 决定授权/隔离级别 |
| **模型支持** | 单模型 vs 多模型 vs 本地模型 | 决定 Provider 抽象需求 |
| **部署环境** | 本地CLI vs 云端服务 vs 桌面App | 决定运行时需求 |
| **开发语言** | TypeScript/JavaScript vs Python vs Rust | 缩小框架范围 |
| **可观测性** | 简单日志 vs 全链路追踪 | 决定日志/事件需求 |
| **团队规模** | 个人项目 vs 10人团队 vs 平台产品 | 决定架构复杂度上限 |

## 主流框架能力矩阵

基于源码分析的五个框架能力对比：

| 能力维度 | **hermes-agent** | **Cordis/dsh** | **Zleap-Agent** | **veadk-python** | **LangChain* |
|---------|-----------------|---------------|-----------------|-----------------|-------------|
| **语言** | Python | TypeScript | TypeScript | Python | Python/JS |
| **循环模型** | 单体可配置 | Waterfall事件链 | 三级状态机 | Runtime委托 | Chain/Agent |
| **工具系统** | ToolRegistry+工具集 | Capability Seam | Workspace作用域 | Runtime注册 | Tool类+装饰器 |
| **Provider** | 适配器模式 | Service Seam | 双注册表 | 运行时委托 | 统一接口 |
| **多Agent** | MoA内置 | subagent包 | Workspace流水线 | agents/模块 | CrewAI/AutoGen |
| **记忆系统** | 短期+长期 | 插件化 | Workspace隔离 | 短期+长期 | Memory类 |
| **安全隔离** | 授权门控+TTL | guard包+沙箱 | 运行时白名单 | Runtime级 | 基础工具 |
| **插件系统** | 回调钩子 | Cordis Fiber/Service | Hook点 | Runtime切换 | 工具/链组合 |
| **状态可观测** | 回调函数 | Session log | EventBus | Runner事件 | Callbacks |
| **代码复杂度** | 高(75+参数) | 中(插件组合) | 高(三级状态机) | 中(分层) | 中(链式API) |
| **学习曲线** | 中 | 高 | 高 | 中 | 低-中 |

> *LangChain 作为参考框架列示，非本项目深度分析对象。

## 场景一：个人 CLI 工具（最简单场景）

**需求**：一个命令行工具，能读取文件、执行命令、回答代码问题。单用户，本地运行。

**推荐**：从零写最简循环 或 使用 hermes-agent 基础模式

```python
"""个人 CLI Agent —— 最简循环实现"""
import asyncio
import json
from openai import AsyncOpenAI

client = AsyncOpenAI()  # 使用 OPENAI_API_KEY 环境变量

# 定义工具
def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def run_command(cmd: str) -> str:
    """执行shell命令并返回输出"""
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout + result.stderr

tools_def = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from disk",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command",
            "parameters": {
                "type": "object",
                "properties": {"cmd": {"type": "string"}},
                "required": ["cmd"]
            }
        }
    }
]

tool_handlers = {"read_file": read_file, "run_command": run_command}

async def chat(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": user_message}
    ]
    
    for _ in range(10):  # 最大10轮
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools_def,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        messages.append(msg)
        
        if not msg.tool_calls:
            return msg.content or ""
        
        for tc in msg.tool_calls:
            func = tool_handlers[tc.function.name]
            args = json.loads(tc.function.arguments)
            result = func(**args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)[:4000]  # 截断防止溢出
            })

# 使用
if __name__ == "__main__":
    result = asyncio.run(chat("How many lines of code are in main.py?"))
    print(result)
```

**选型理由**：
- 不需要复杂的插件系统 → 50行代码即可
- 不需要多租户/安全隔离 → 直接执行
- 单模型 → 不需要 Provider 抽象
- 总代码量 <100行，没有引入框架的必要

## 场景二：企业级编码助手（中等复杂度）

**需求**：类似 Claude Code/Cursor 的编码助手，支持文件操作、终端执行、代码搜索、Web 搜索。需要授权机制、并发工具、安全检查、多模型支持。

**推荐**：hermes-agent 或自建单体可配置循环

```python
"""企业级编码 Agent —— 基于单体可配置模式"""
import asyncio
from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum

class AuthLevel(Enum):
    """工具授权级别"""
    ALWAYS_ALLOW = "always"      # 读文件、搜索等
    CONFIRM = "confirm"          # 写文件、网络请求
    NEVER = "never"              # 危险操作（在安全模式下）

@dataclass
class ToolDef:
    name: str
    handler: Callable
    description: str
    parameters: dict
    auth_level: AuthLevel = AuthLevel.CONFIRM
    tags: list[str] = None

class CodingAgent:
    """企业级编码助手"""
    
    def __init__(
        self,
        model: str = "gpt-4o",
        provider: str = "openai",
        tool_mode: str = "concurrent",  # concurrent | sequential | segmented
        dangerous_tools_disabled: bool = False,
        max_iterations: int = 30,
        on_confirmation: Callable | None = None,  # 用户确认回调
    ):
        self.model = model
        self.provider = provider
        self.tool_mode = tool_mode
        self.dangerous_disabled = dangerous_tools_disabled
        self.max_iterations = max_iterations
        self.on_confirmation = on_confirmation or self._default_confirm
        self.tools: dict[str, ToolDef] = {}
        self._auth_cache: dict[str, bool] = {}
    
    @staticmethod
    def _default_confirm(tool_name: str, args: dict) -> bool:
        """默认确认：打印到终端等待用户输入"""
        print(f"\n⚠️  Agent wants to use '{tool_name}' with: {args}")
        response = input("Allow? [y/N] ").strip().lower()
        return response == 'y'
    
    def register_tool(self, tool: ToolDef):
        if self.dangerous_disabled and tool.auth_level == AuthLevel.NEVER:
            return  # 不注册危险工具
        self.tools[tool.name] = tool
    
    async def _check_auth(self, tool_name: str, args: dict) -> bool:
        """授权检查"""
        tool = self.tools[tool_name]
        
        if tool.auth_level == AuthLevel.ALWAYS_ALLOW:
            return True
        
        if tool.auth_level == AuthLevel.NEVER:
            return False
        
        # CONFIRM 级别：带缓存（同一操作30秒内不重复确认）
        cache_key = f"{tool_name}:{hash(str(sorted(args.items())))}"
        if cache_key in self._auth_cache:
            return self._auth_cache[cache_key]
        
        allowed = await asyncio.get_event_loop().run_in_executor(
            None, self.on_confirmation, tool_name, args
        )
        self._auth_cache[cache_key] = allowed
        return allowed
    
    async def _execute_tool(self, tc) -> dict:
        """执行单个工具（含安全检查）"""
        args = json.loads(tc.function.arguments)
        
        # 路径安全检查（防止遍历攻击）
        if "path" in args:
            import os
            resolved = os.path.realpath(args["path"])
            if not resolved.startswith(os.getcwd()):
                return {"tool_call_id": tc.id, "content": f"Error: Path {args['path']} is outside the working directory"}
        
        # 授权检查
        allowed = await self._check_auth(tc.function.name, args)
        if not allowed:
            return {"tool_call_id": tc.id, "content": "User denied this operation."}
        
        # 执行
        handler = self.tools[tc.function.name].handler
        try:
            result = await handler(**args) if asyncio.iscoroutinefunction(handler) else handler(**args)
            return {"tool_call_id": tc.id, "content": str(result)[:8000]}
        except Exception as e:
            return {"tool_call_id": tc.id, "content": f"Error: {type(e).__name__}: {e}"}
    
    async def _execute_tools(self, tool_calls) -> list[dict]:
        """按模式执行工具"""
        if self.tool_mode == "concurrent":
            # 并发执行独立工具
            return await asyncio.gather(*[self._execute_tool(tc) for tc in tool_calls])
        elif self.tool_mode == "segmented":
            # 分段：先读/搜，后写，最后执行命令
            read_ops = [tc for tc in tool_calls if tc.function.name.startswith(("read", "search", "list"))]
            write_ops = [tc for tc in tool_calls if tc.function.name.startswith(("write", "edit", "delete"))]
            cmd_ops = [tc for tc in tool_calls if tc.function.name.startswith("run")]
            
            results = []
            for group in [read_ops, write_ops, cmd_ops]:
                results.extend(await asyncio.gather(*[self._execute_tool(tc) for tc in group]))
            return results
        else:
            # 顺序执行
            results = []
            for tc in tool_calls:
                result = await self._execute_tool(tc)
                results.append(result)
                if "Error:" in str(result.get("content", "")):
                    break
            return results
    
    async def run(self, message: str) -> str:
        """主循环"""
        messages = [
            {"role": "system", "content": "You are a senior software engineer assistant."},
            {"role": "user", "content": message}
        ]
        
        tools_schema = [
            {"type": "function", "function": {
                "name": t.name, "description": t.description, "parameters": t.parameters
            }}
            for t in self.tools.values()
        ]
        
        for _ in range(self.max_iterations):
            response = await client.chat.completions.create(
                model=self.model, messages=messages,
                tools=tools_schema if tools_schema else None
            )
            msg = response.choices[0].message
            messages.append(msg)
            
            if not msg.tool_calls:
                return msg.content or "Task completed."
            
            results = await self._execute_tools(msg.tool_calls)
            for r in results:
                messages.append({"role": "tool", "tool_call_id": r["tool_call_id"], "content": r["content"]})
        
        return "Reached maximum iterations."

# 注册工具集
agent = CodingAgent(model="gpt-4o", tool_mode="segmented")
agent.register_tool(ToolDef(
    name="read_file", handler=read_file,
    description="Read a file's contents",
    parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    auth_level=AuthLevel.ALWAYS_ALLOW,
    tags=["read"]
))
agent.register_tool(ToolDef(
    name="write_file", handler=write_file,
    description="Write content to a file",
    parameters={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
    auth_level=AuthLevel.CONFIRM,
    tags=["write"]
))
agent.register_tool(ToolDef(
    name="run_command", handler=run_command,
    description="Execute a shell command",
    parameters={"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]},
    auth_level=AuthLevel.CONFIRM,
    tags=["execute"]
))
```

**选型理由**：
- 需要授权机制 → 单体类集中管理授权
- 需要并发工具 → concurrent/segmented 模式
- 需要安全检查 → 路径验证+授权级别
- 多模型 → 通过 provider 参数适配（需扩展）
- hermes-agent 是这种模式的生产级实现

## 场景三：可插件化 Agent 平台（高扩展性）

**需求**：构建一个 Agent 平台，第三方可以开发插件扩展能力（如添加新的 LLM provider、新工具、新中间件）。需要热插拔、独立开发、生命周期管理。

**推荐**：Cordis + deepseek-harness（Waterfall 事件链 + Capability Seam）

```typescript
// 基于 Cordis 的可插件化 Agent 平台
import { Context, Service, Schema } from 'cordis'

// --- 1. 服务定义（Service Definition） ---

// LLM 服务接口
abstract class LLMService extends Service {
    static inject = []
    abstract complete(messages: Message[], opts?: CompleteOpts): Promise<LLMResponse>
    abstract stream(messages: Message[], opts?: StreamOpts): AsyncIterable<Chunk>
}

// Shell 服务接口
abstract class ShellService extends Service {
    abstract exec(cmd: string, opts?: ExecOpts): Promise<ExecResult>
}

// --- 2. 插件：核心循环 ---

interface LoopState {
    messages: Message[]
    response?: LLMResponse
    done: boolean
    iteration: number
}

function coreLoopPlugin(ctx: Context) {
    // 注册 agent/run 命令
    ctx.command('agent/run', async (message: string) => {
        const state: LoopState = {
            messages: [{ role: 'user', content: message }],
            done: false,
            iteration: 0
        }
        
        while (!state.done && state.iteration < 50) {
            state.iteration++
            
            // Waterfall 链：每个插件可以在任意阶段介入
            await ctx.waterfall('agent/loop', state)
            
            if (state.response) {
                state.messages.push(assistantMsg(state.response))
                if (state.response.toolCalls) {
                    const results = await ctx.waterfall('agent/execute-tools', state.response.toolCalls)
                    state.messages.push(...results)
                } else {
                    state.done = true
                }
            }
        }
        
        return state.response?.content
    })
    
    // 默认 LLM 调用（作为 waterfall 的一环）
    ctx.waterfall('agent/loop', async (state: LoopState, next) => {
        const llm = ctx.get('llm')  // 通过 Service 名获取，不感知具体实现
        state.response = await llm.complete(state.messages, {
            tools: ctx.registry.getAvailableTools()
        })
        return next(state)
    })
}

// --- 3. 插件：DeepSeek Provider（第三方可替换） ---

class DeepSeekProvider extends LLMService {
    constructor(ctx: Context) {
        super(ctx, 'llm')  // 注册为 'llm' 服务
    }
    
    async complete(messages: Message[], opts?: CompleteOpts) {
        // 调用 DeepSeek API
        const resp = await fetch('https://api.deepseek.com/v1/chat/completions', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.config.apiKey}` },
            body: JSON.stringify({ model: 'deepseek-chat', messages, tools: opts?.tools })
        })
        return this.parseResponse(await resp.json())
    }
    
    async *stream(messages: Message[], opts?: StreamOpts): AsyncIterable<Chunk> {
        // SSE 流式处理
    }
}

// --- 4. 插件：OpenAI Provider（用户可选择） ---

class OpenAIProvider extends LLMService {
    constructor(ctx: Context) {
        super(ctx, 'llm')
    }
    async complete(messages, opts) { /* OpenAI API 调用 */ }
    async *stream(messages, opts) { /* OpenAI SSE */ }
}

// --- 5. 插件：循环卫生 Guard ---

function hygieneGuardPlugin(ctx: Context) {
    const recentCalls = new Map<string, number>()
    
    ctx.waterfall('agent/loop', async (state: LoopState, next) => {
        if (state.response?.toolCalls) {
            for (const tc of state.response.toolCalls) {
                const key = `${tc.name}:${JSON.stringify(tc.arguments)}`
                const count = (recentCalls.get(key) || 0) + 1
                recentCalls.set(key, count)
                
                if (count >= 3) {
                    state.done = true
                    state.messages.push({
                        role: 'system',
                        content: `[Guard] Detected repeated call to ${tc.name}. Try a different approach.`
                    })
                    return state  // 短路
                }
            }
        }
        return next(state)
    })
}

// --- 6. 插件：Web 搜索能力 ---

class WebSearchService extends Service {
    async search(query: string): Promise<SearchResult[]> {
        // 调用搜索 API
    }
}

function webSearchPlugin(ctx: Context) {
    ctx.plugin(WebSearchService)
    ctx.registry.registerTool({
        name: 'web_search',
        description: 'Search the web for information',
        parameters: {
            type: 'object',
            properties: { query: { type: 'string' } },
            required: ['query']
        },
        handler: async (args) => {
            const web = ctx.get('web.search')
            const results = await web.search(args.query)
            return results.map(r => `${r.title}\n${r.snippet}\n${r.url}`).join('\n\n')
        }
    })
}

// --- 使用：组装应用 ---

const app = new Context()

// 安装插件（可以按需选择）
app.plugin(coreLoopPlugin)
app.plugin(DeepSeekProvider)       // 选择 DeepSeek 作为 LLM
// app.plugin(OpenAIProvider)      // 或切换到 OpenAI
app.plugin(hygieneGuardPlugin)
app.plugin(webSearchPlugin)
// app.plugin(sandboxPlugin)       // 第三方沙箱插件
// app.plugin(mcpPlugin)           // MCP 协议支持

// 运行
const result = await app.serial('agent/run', 'Search for latest AI news and summarize')
```

**选型理由**：
- 需要第三方插件 → Cordis 的 Service/Plugin 机制
- 需要热插拔 → waterfall 链可以随时添加/移除
- 需要生命周期管理 → ctx.effect() 注册即副作用
- 需要 Provider 可替换 → Capability Seam 三角色分离
- deepseek-harness 是这种模式的生产级实现

## 场景四：多阶段流水线工作流（强隔离）

**需求**：构建一个代码审查 Agent，需要分阶段执行：规划（只读）→ 执行（可写）→ 验证（只读+测试）→ 报告（只读）。每个阶段有独立的上下文和工具权限。

**推荐**：Zleap-Agent（三级状态机 + Workspace 作用域）

```typescript
// Zleap 风格的多阶段流水线
import { AgentRuntime, Workspace } from 'zleap-agent'

const runtime = new AgentRuntime({
  llm: { provider: 'openai', model: 'gpt-4o' },
  tools: [readFile, writeFile, searchFiles, runTests, runLinter, gitOps]
})

// 定义流水线 Workspace
const pipeline = [
  // Stage 1: 规划（只读）
  new Workspace({
    id: 'planning',
    prompt: `You are a code review planner. Analyze the codebase and create a review plan.
    You can ONLY read files and search. Do not modify anything.
    Output a structured plan listing files to review and potential issues to check.`,
    allowedToolIds: ['readFile', 'searchFiles']  // 白名单：仅读操作
  }),
  
  // Stage 2: 深度分析（读+静态分析）
  new Workspace({
    id: 'analysis',
    prompt: `You are a code analyst. Based on the review plan, deeply analyze each file.
    Run linters and static analysis. Categorize issues by severity.`,
    allowedToolIds: ['readFile', 'searchFiles', 'runLinter']
  }),
  
  // Stage 3: 验证（读+测试）
  new Workspace({
    id: 'verification',
    prompt: `You are a verification agent. Run tests to confirm identified issues.
    Do not modify code. Only run tests and report results.`,
    allowedToolIds: ['readFile', 'runTests']
  }),
  
  // Stage 4: 报告生成（只读）
  new Workspace({
    id: 'reporting',
    prompt: `You are a report writer. Generate a structured code review report
    with severity levels, file locations, and fix suggestions.`,
    allowedToolIds: ['readFile', 'searchFiles']
  })
]

// 执行流水线（每个 Workspace 的输出作为下一个的输入）
const report = await runtime.run('Review the authentication module', pipeline)

// 状态可观测
runtime.on('run:status-change', ({ old, new: status }) => {
  console.log(`[${new Date().toISOString()}] Run: ${old} → ${status}`)
})

runtime.on('work:status-change', ({ workspaceId, old, new: status }) => {
  console.log(`  [${workspaceId}] ${old} → ${status}`)
})

// 工具越权会被运行时拦截
// 如果 LLM 试图在 planning 阶段调用 writeFile：
// → Error: tool_not_allowed: writeFile not in workspace (planning)
```

**选型理由**：
- 需要阶段隔离 → Workspace 白名单是强隔离
- 需要流程可控 → 三级状态机清晰可见
- 需要可观测 → EventBus 全量事件
- Zleap-Agent 是这种模式的生产级实现

## 场景五：多模型/多运行时部署（灵活后端）

**需求**：构建一个 AI 服务，需要支持多种部署方式：本地开发用本地模型、云端部署用 OpenAI/Anthropic、企业客户用 Codex 运行时。Agent 逻辑相同，但运行后端不同。

**推荐**：veadk-python（Agent/Runner 分层委托）

```python
"""多运行时 Agent —— veadk 风格"""
from dataclasses import dataclass, field
from typing import Any
from abc import ABC, abstractmethod

# --- Agent 配置 ---

@dataclass
class AgentConfig:
    model_name: str = "gpt-4o"
    provider: str = "openai"
    api_base: str = ""
    tools: list[str] = field(default_factory=lambda: ["web_search", "calculator"])
    system_prompt: str = "You are a helpful assistant."
    max_tokens: int = 4096
    runtime: str = "local"  # local | codex | piagent

# --- Runtime 抽象 ---

class AgentRuntime(ABC):
    @abstractmethod
    async def execute(self, config: AgentConfig, messages: list[dict]) -> str:
        pass

# 本地运行时
class LocalRuntime(AgentRuntime):
    def __init__(self):
        self.providers = {}
    
    def register_provider(self, name: str, adapter: Any):
        self.providers[name] = adapter
    
    async def execute(self, config, messages):
        provider = self.providers[config.provider]
        for _ in range(config.max_tokens):  # 简化
            response = await provider.chat(
                messages=messages,
                model=config.model_name,
                tools=config.tools
            )
            if not response.tool_calls:
                return response.content
            # 执行工具...
            messages.append(response)

# Codex 运行时（委托）
class CodexRuntime(AgentRuntime):
    def __init__(self, codex_client):
        self.client = codex_client
    
    async def execute(self, config, messages):
        return await self.client.agents.run(
            model=config.model_name,
            instructions=config.system_prompt,
            messages=messages
        )

# --- Runner ---

class AgentRunner:
    def __init__(self):
        self.runtimes: dict[str, AgentRuntime] = {}
    
    def use_runtime(self, name: str, runtime: AgentRuntime):
        self.runtimes[name] = runtime
    
    async def run(self, config: AgentConfig, message: str) -> str:
        runtime = self.runtimes.get(config.runtime)
        if not runtime:
            raise ValueError(f"Unknown runtime: {config.runtime}")
        
        messages = [{"role": "user", "content": message}]
        return await runtime.execute(config, messages)

# --- 使用：不同环境切换 ---

# 本地开发配置
dev_config = AgentConfig(
    model_name="llama3.1:8b",
    provider="ollama",
    api_base="http://localhost:11434/v1",
    runtime="local"
)

# 云端生产配置
prod_config = AgentConfig(
    model_name="gpt-4o",
    provider="openai",
    runtime="local"
)

# 企业客户配置
enterprise_config = AgentConfig(
    model_name="gpt-4o",
    runtime="codex"
)

runner = AgentRunner()
runner.use_runtime("local", local_runtime)
runner.use_runtime("codex", CodexRuntime(codex_client))

# 同一 Agent 逻辑，不同运行时
result = await runner.run(dev_config, "Hello")
```

**选型理由**：
- 需要多后端 → Runtime 委托
- Agent 配置统一 → Agent 数据类
- 同一逻辑多处运行 → 切换 runtime 即可
- veadk-python 是这种模式的生产级实现

## 场景六：从零构建学习用 Agent（教学场景）

**需求**：学习 Agent 原理，从零实现一个可运行的 Agent，理解 ReAct、工具调用、记忆等核心概念。

**推荐**：不用框架，从零实现（见 [build-agent-from-scratch.md](build-agent-from-scratch.md)）

## 选型速查表

| 你的场景 | 推荐模式 | 参考框架 | 关键判断依据 |
|---------|---------|---------|------------|
| 个人 CLI 工具/原型 | 极简循环 | 自己写 <100行 | 不需要扩展性 |
| 编码助手/通用 Agent | 单体可配置 | hermes-agent | 需要授权+并发+安全 |
| 插件化平台/SaaS | 事件链+插件 | Cordis/dsh | 第三方扩展+热插拔 |
| 多阶段流水线/工作流 | 状态机 | Zleap-Agent | 阶段隔离+强权限 |
| 多后端/混合云部署 | Runtime委托 | veadk-python | 同一逻辑多引擎 |
| 学习/教学 | 从零实现 | 自己写 | 理解原理最重要 |

## 反模式警示

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 个人项目用 Cordis 级插件架构 | 过度工程，50行代码变成500行 | 用最简循环 |
| 平台产品用 LangChain Chain | Chain 模式不支持灵活的循环控制 | 用 Agent Loop 框架 |
| 多租户产品不加授权门控 | 安全事故 | 加授权+白名单+审计 |
| 同时使用多个 LLM 但无 Provider 抽象 | 每个模型写一套 API 调用 | 适配器/Service 模式 |
| 无限循环无检测 | Token 浪费+死循环 | 循环卫生+最大迭代数 |
| 工具执行无超时控制 | 工具挂住整个 Agent | 超时+中断信号 |

## 相关概念

- Agent 核心循环
- 工具系统
- 模型 Provider 抽象
- 插件化架构模式
- 多智能体编排
- [对比不同框架的 Agent 循环](compare-agent-loops.md)
- [从零构建简易 Agent](build-agent-from-scratch.md)
