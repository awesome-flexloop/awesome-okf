---
type: Example
title: 对比不同框架的 Agent 循环实现
description: 通过代码级对比分析 hermes-agent、Zleap-Agent、deepseek-harness (Cordis)、veadk-python 四个框架的 Agent 核心循环实现，理解 ReAct 理论到生产代码的四种工程路径，帮助你在设计自己的 Agent 时做出架构选择。
tags: [ai-agent-fundamentals, example, agent-loop, react, comparison, hermes, zleap, cordis, veadk]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: concepts
    resource: /concepts/01-agent-loop.md
    title: Agent 核心循环概念
---

## 场景说明

你正在设计自己的 AI Agent 框架，或者需要为项目选择 Agent 架构。面对 ReAct 理论模型（think-act-observe 循环），不同的生产级框架采用了截然不同的工程实现路径。本示例将：
1. 实现四种 Agent 循环（从极简 ReAct 到生产级）
2. 对比每种模式的优缺点
3. 演示错误恢复、并发工具、中断处理等关键工程问题
4. 给出架构选择决策指南

## ReAct 理论模型（起点）

所有 Agent 框架都基于同一个理论核心——ReAct 循环：

```python
# 理论上的最简 Agent 循环
def react_loop(goal: str, tools: list) -> str:
    """ReAct: Reasoning + Acting"""
    messages = [{"role": "user", "content": goal}]
    
    while True:
        # THINK: LLM 推理
        response = llm.chat(messages, tools=tools)
        
        if not response.tool_calls:
            return response.content  # 无工具调用，返回最终答案
        
        # ACT: 执行工具
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call.name, tool_call.arguments)
            messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})
        
        # OBSERVE: 工具结果已追加到 messages，下一轮 LLM 可见
```

这个 10 行的伪代码抓住了本质，但缺少所有生产级特性。下面我们看四个框架如何在它的基础上构建。

## 实现一：单体可配置循环（hermes-agent 风格）

hermes-agent 用一个大的 `AIAgent` 类（75+ 参数）将所有配置集中在一个类中。

```python
import asyncio
import signal
from dataclasses import dataclass, field
from typing import Callable, Any
from collections import defaultdict
import time

# --- 基础类型 ---

@dataclass
class ToolCall:
    name: str
    arguments: dict
    id: str

@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    handler: Callable
    tags: list[str] = field(default_factory=list)

class AuthorizationError(Exception):
    pass

class LoopHygieneError(Exception):
    """检测到无限循环"""
    pass

# --- 授权门控 ---

class AuthorizationGate:
    """工具授权检查，带 TTL 缓存和瞬态故障抑制"""
    
    def __init__(self, ttl_seconds: float = 30.0):
        self._cache: dict[str, float] = {}
        self._ttl = ttl_seconds
        self._failure_count: dict[str, int] = defaultdict(int)
        self._failure_threshold = 3
    
    async def check(self, tool_name: str, arguments: dict) -> bool:
        cache_key = f"{tool_name}:{hash(str(sorted(arguments.items())))}"
        now = time.time()
        
        # TTL 缓存命中
        if cache_key in self._cache and now - self._cache[cache_key] < self._ttl:
            return True
        
        # 瞬态故障抑制：授权服务短时不可用时降级
        if self._failure_count[tool_name] >= self._failure_threshold:
            # 失败过多，暂时允许（降级策略）
            return True
        
        # 实际授权检查（这里简化为始终允许）
        # 生产中会调用用户确认或策略引擎
        allowed = True  # await self._do_check(tool_name, arguments)
        
        if allowed:
            self._cache[cache_key] = now
            self._failure_count[tool_name] = 0
        else:
            self._failure_count[tool_name] += 1
        
        return allowed

# --- 工具注册表 ---

class ToolRegistry:
    """单例工具注册表"""
    _instance = None
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, tool: Tool):
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Tool:
        return self._tools[name]
    
    def list_all(self) -> list[Tool]:
        return list(self._tools.values())

# --- 核心 Agent 类 ---

class AIAgent:
    """单体可配置 Agent（hermes-agent 风格）"""
    
    def __init__(
        self,
        llm_client: Any,
        tools: list[str] | None = None,        # 工具名列表
        tool_execution_mode: str = "concurrent", # concurrent | sequential | segmented
        max_iterations: int = 50,
        authorization_gate: AuthorizationGate | None = None,
        enable_hygiene_check: bool = True,
        on_tool_start: Callable | None = None,
        on_tool_end: Callable | None = None,
        on_error: Callable | None = None,
        system_prompt: str = "You are a helpful assistant.",
    ):
        self.llm = llm_client
        self.registry = ToolRegistry.get_instance()
        self.tool_names = tools or [t.name for t in self.registry.list_all()]
        self.execution_mode = tool_execution_mode
        self.max_iterations = max_iterations
        self.auth_gate = authorization_gate or AuthorizationGate()
        self.enable_hygiene = enable_hygiene_check
        self.on_tool_start = on_tool_start
        self.on_tool_end = on_tool_end
        self.on_error = on_error
        self.system_prompt = system_prompt
        self._interrupted = False
        
        # 循环卫生检测
        self._recent_calls: list[tuple[str, str]] = []
        self._hygiene_window = 5
        self._hygiene_threshold = 3  # 窗口内重复次数阈值
    
    def interrupt(self):
        """处理 Ctrl+C 中断"""
        self._interrupted = True
    
    def _check_hygiene(self, tool_name: str, args_str: str):
        """循环卫生检测：防止无限循环"""
        self._recent_calls.append((tool_name, args_str))
        if len(self._recent_calls) > self._hygiene_window:
            self._recent_calls.pop(0)
        
        # 检查是否有重复调用
        call_signature = (tool_name, args_str)
        if self._recent_calls.count(call_signature) >= self._hygiene_threshold:
            raise LoopHygieneError(
                f"Detected potential infinite loop: "
                f"{tool_name} called {self._hygiene_threshold} times with same arguments"
            )
    
    async def _execute_tools(self, tool_calls: list[ToolCall]) -> list[dict]:
        """按配置的模式执行工具"""
        
        async def execute_one(tc: ToolCall) -> dict:
            # 回调
            if self.on_tool_start:
                self.on_tool_start(tc.name, tc.arguments)
            
            try:
                # 授权检查
                allowed = await self.auth_gate.check(tc.name, tc.arguments)
                if not allowed:
                    raise AuthorizationError(f"Tool {tc.name} not authorized")
                
                # 循环卫生检查
                if self.enable_hygiene:
                    self._check_hygiene(tc.name, str(sorted(tc.arguments.items())))
                
                # 获取并执行工具
                tool = self.registry.get(tc.name)
                result = await tool.handler(**tc.arguments)
                
                if self.on_tool_end:
                    self.on_tool_end(tc.name, result)
                
                return {
                    "tool_call_id": tc.id,
                    "content": str(result),
                    "error": None
                }
            except Exception as e:
                if self.on_error:
                    self.on_error(tc.name, e)
                return {
                    "tool_call_id": tc.id,
                    "content": None,
                    "error": str(e)
                }
        
        if self.execution_mode == "concurrent":
            # 并发执行：独立工具并行
            return await asyncio.gather(*[execute_one(tc) for tc in tool_calls])
        
        elif self.execution_mode == "sequential":
            # 顺序执行：工具间有依赖
            results = []
            for tc in tool_calls:
                result = await execute_one(tc)
                results.append(result)
                # 错误时停止
                if result["error"]:
                    break
            return results
        
        elif self.execution_mode == "segmented":
            # 分段执行：按类型分组（只读→写→命令）
            read_tools = [tc for tc in tool_calls if tc.name.startswith("read") or tc.name.startswith("search")]
            write_tools = [tc for tc in tool_calls if tc.name.startswith("write") or tc.name.startswith("edit")]
            cmd_tools = [tc for tc in tool_calls if tc.name.startswith("run") or tc.name.startswith("exec")]
            
            results = []
            for group in [read_tools, write_tools, cmd_tools]:
                group_results = await asyncio.gather(*[execute_one(tc) for tc in group])
                results.extend(group_results)
            return results
        
        else:
            raise ValueError(f"Unknown execution mode: {self.execution_mode}")
    
    async def run(self, user_message: str) -> str:
        """主循环"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 注册信号处理
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self.interrupt)
            except NotImplementedError:
                pass  # Windows 不支持 add_signal_handler
        
        tools_def = [
            {"name": t.name, "description": t.description, "parameters": t.parameters}
            for t in self.registry.list_all()
            if t.name in self.tool_names
        ]
        
        for iteration in range(self.max_iterations):
            if self._interrupted:
                return "Execution interrupted by user."
            
            # THINK: LLM 推理
            response: LLMResponse = await self.llm.chat(messages, tools=tools_def)
            messages.append({"role": "assistant", "content": response.content, "tool_calls": response.tool_calls})
            
            # 无工具调用 → 循环结束
            if not response.tool_calls:
                return response.content or ""
            
            # ACT: 执行工具
            tool_results = await self._execute_tools(response.tool_calls)
            
            # OBSERVE: 注入结果
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "content": result["content"] or result["error"],
                    "tool_call_id": result["tool_call_id"]
                })
        
        return f"Reached maximum iterations ({self.max_iterations})"
```

**特点分析**：
- ✅ 配置集中，一个类控制所有行为
- ✅ 三种工具执行模式（concurrent/sequential/segmented）
- ✅ 授权门控 + TTL 缓存 + 故障降级
- ✅ 循环卫生检测防止无限循环
- ❌ 75+ 参数导致类复杂度高
- ❌ 扩展新功能需要修改类本身

## 实现二：三级状态机驱动循环（Zleap-Agent 风格）

Zleap 将循环分解为 Run → Work → Step 三级状态机，每个级别有独立生命周期。

```python
from enum import Enum
from typing import Any
import asyncio
from dataclasses import dataclass, field

# --- 状态枚举 ---

class RunStatus(Enum):
    CREATED = "created"
    SESSION_ASSEMBLING = "session_assembling"
    PLANNING = "planning"
    WORKING = "working"
    INTEGRATING = "integrating"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"

class WorkStatus(Enum):
    CREATED = "created"
    QUEUED = "queued"
    LOADING = "loading"
    ACTIVE = "active"
    PRODUCING = "producing"
    CURATING = "curating"
    EXITED = "exited"

class StepStatus(Enum):
    LOADING = "loading"
    ACTIVE = "active"
    PRODUCING = "producing"
    CURATING = "curating"
    EXITED = "exited"

# --- 事件总线（简化版） ---

class EventBus:
    def __init__(self):
        self._observers: dict[str, list[Callable]] = {}
    
    def observe(self, event_type: str, callback: Callable):
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(callback)
    
    def emit(self, event_type: str, **data):
        for cb in self._observers.get(event_type, []):
            cb(**data)

# --- Workspace 定义 ---

@dataclass
class Workspace:
    """一个工作空间：包含独立的 prompt、工具白名单、handler"""
    id: str
    prompt: str
    allowed_tool_ids: list[str]
    handler: Callable | None = None  # 自定义 handler，None 则使用默认 ReAct 循环

@dataclass
class WorkContext:
    """Workspace 运行时上下文"""
    workspace: Workspace
    available_tools: dict[str, Tool]
    input: Any = None
    output: Any = None
    event_bus: EventBus = field(default_factory=EventBus)
    aborted: bool = False

# --- Agent Runtime ---

class AgentRuntime:
    """Zleap 风格的三级状态机运行时"""
    
    def __init__(self, llm_client: Any, tool_registry: ToolRegistry):
        self.llm = llm_client
        self.tool_registry = tool_registry
        self.event_bus = EventBus()
        self.run_status = RunStatus.CREATED
    
    def _transition_run(self, new_status: RunStatus):
        """Run 级状态转换"""
        old = self.run_status
        self.run_status = new_status
        self.event_bus.emit("run:status-change", old=old, new=new_status)
    
    def create_space_context(self, workspace: Workspace) -> WorkContext:
        """为 Workspace 创建上下文，按 allowedToolIds 过滤工具"""
        available = {}
        for tool_id in workspace.allowed_tool_ids:
            tool = self.tool_registry.get(tool_id)
            if tool:
                available[tool_id] = tool
        
        return WorkContext(
            workspace=workspace,
            available_tools=available,
            event_bus=EventBus()
        )
    
    async def _execute_step(self, context: WorkContext, messages: list, tools_def: list):
        """Step 级：单次 LLM 推理 + 工具执行"""
        context.event_bus.emit("step:status", status=StepStatus.ACTIVE)
        
        response: LLMResponse = await self.llm.chat(messages, tools=tools_def)
        context.event_bus.emit("step:status", status=StepStatus.PRODUCING)
        
        results = []
        if response.tool_calls:
            for tc in response.tool_calls:
                # 运行时检查：工具必须在白名单中
                if tc.name not in context.available_tools:
                    results.append({
                        "tool_call_id": tc.id,
                        "content": None,
                        "error": f"tool_not_allowed: {tc.name} not in workspace"
                    })
                    continue
                
                tool = context.available_tools[tc.name]
                try:
                    result = await tool.handler(**tc.arguments)
                    results.append({
                        "tool_call_id": tc.id,
                        "content": str(result),
                        "error": None
                    })
                except Exception as e:
                    results.append({
                        "tool_call_id": tc.id,
                        "content": None,
                        "error": str(e)
                    })
        
        context.event_bus.emit("step:status", status=StepStatus.EXITED)
        return response, results
    
    async def _execute_work(self, context: WorkContext, max_steps: int = 30) -> Any:
        """Work 级：一个 Workspace 内的完整 ReAct 循环"""
        workspace = context.workspace
        context.event_bus.emit("work:status", status=WorkStatus.LOADING)
        
        messages = [
            {"role": "system", "content": workspace.prompt},
            {"role": "user", "content": str(context.input)}
        ]
        
        tools_def = [
            {"name": t.name, "description": t.description, "parameters": t.parameters}
            for t in context.available_tools.values()
        ]
        
        context.event_bus.emit("work:status", status=WorkStatus.ACTIVE)
        
        for step in range(max_steps):
            if context.aborted:
                context.event_bus.emit("work:status", status=WorkStatus.EXITED)
                return None
            
            response, results = await self._execute_step(context, messages, tools_def)
            
            if not response.tool_calls:
                context.output = response.content
                context.event_bus.emit("work:status", status=WorkStatus.CURATING)
                break
            
            messages.append({"role": "assistant", "content": response.content, "tool_calls": response.tool_calls})
            for r in results:
                messages.append({"role": "tool", "content": r["content"] or r["error"], "tool_call_id": r["tool_call_id"]})
        
        context.event_bus.emit("work:status", status=WorkStatus.EXITED)
        return context.output
    
    async def run(self, user_message: str, spaces: list[Workspace]) -> Any:
        """Run 级：流水线执行多个 Workspace"""
        self._transition_run(RunStatus.SESSION_ASSEMBLING)
        artifact = user_message
        
        self._transition_run(RunStatus.PLANNING)
        # 可在此插入规划阶段
        
        self._transition_run(RunStatus.WORKING)
        
        for i, space in enumerate(spaces):
            context = self.create_space_context(space)
            context.input = artifact
            
            try:
                result = await self._execute_work(context)
                artifact = result  # 产出作为下一个 Workspace 的输入
            except Exception as e:
                self._transition_run(RunStatus.FAILED)
                self.event_bus.emit("run:error", workspace=space.id, error=str(e))
                raise
        
        self._transition_run(RunStatus.INTEGRATING)
        # 整合各 Workspace 产出
        
        self._transition_run(RunStatus.DELIVERING)
        final_output = artifact
        
        self._transition_run(RunStatus.COMPLETED)
        return final_output
    
    def abort(self):
        """中止当前 Run"""
        self._transition_run(RunStatus.ABORTED)
```

**使用示例**：

```python
# 创建 Workspace 流水线
planning_space = Workspace(
    id="planning",
    prompt="You are a planner. Break down the task into steps.",
    allowed_tool_ids=["web_search", "read_file"]  # 只允许搜索和读文件
)

execution_space = Workspace(
    id="execution",
    prompt="You are an executor. Implement the plan.",
    allowed_tool_ids=["write_file", "terminal", "read_file"]  # 允许写和执行
)

review_space = Workspace(
    id="review",
    prompt="You are a reviewer. Check the implementation for issues.",
    allowed_tool_ids=["read_file", "lsp_hover"]  # 只读 + LSP
)

runtime = AgentRuntime(llm_client=mock_llm, tool_registry=registry)

# 注册状态观察
runtime.event_bus.observe("run:status-change", lambda old, new: print(f"Run: {old.value} → {new.value}"))

# 执行流水线
result = await runtime.run(
    "Build a REST API for user management",
    spaces=[planning_space, execution_space, review_space]
)
```

**特点分析**：
- ✅ 三级状态机让生命周期清晰可观测
- ✅ Workspace 间强隔离，工具白名单运行时检查
- ✅ EventBus 全量事件可日志化、可调试
- ✅ 流水线模式天然支持多阶段任务
- ❌ 增加新状态需要修改状态机枚举
- ❌ Workspace 间只能通过 artifact 传递数据

## 实现三：Waterfall 事件链循环（Cordis/deepseek-harness 风格）

基于 Cordis 的事件系统，循环由可插拔的 waterfall 监听器链组成。

```python
from typing import Any, Callable, Awaitable
import asyncio

# --- Waterfall 事件系统（简化版 Cordis） ---

NextCallback = Callable[[Any], Awaitable[Any]]
WaterfallHandler = Callable[[Any, NextCallback], Awaitable[Any]]

class WaterfallContext:
    """简化的 Cordis Context，支持 waterfall 事件"""
    
    def __init__(self):
        self._waterfall_handlers: dict[str, list[WaterfallHandler]] = {}
        self._disposers: list[Callable] = []
    
    def waterfall(self, event: str, handler: WaterfallHandler):
        """注册 waterfall 监听器"""
        if event not in self._waterfall_handlers:
            self._waterfall_handlers[event] = []
        self._waterfall_handlers[event].append(handler)
    
    async def dispatch_waterfall(self, event: str, initial_state: Any) -> Any:
        """分发 waterfall 事件，构建并执行链"""
        handlers = self._waterfall_handlers.get(event, [])
        if not handlers:
            return initial_state
        
        # 构建链式调用
        async def chain(index: int, state: Any) -> Any:
            if index >= len(handlers):
                return state
            
            async def next_fn(new_state=None):
                new_state = new_state if new_state is not None else state
                return await chain(index + 1, new_state)
            
            return await handlers[index](state, next_fn)
        
        return await chain(0, initial_state)
    
    def effect(self, setup: Callable[[], Callable]):
        """注册副作用，返回清理函数"""
        disposer = setup()
        if disposer:
            self._disposers.append(disposer)
    
    def dispose(self):
        """清理所有副作用"""
        for d in self._disposers:
            d()

# --- Loop State ---

@dataclass
class LoopState:
    messages: list = field(default_factory=list)
    system_prompt: str = ""
    response: LLMResponse | None = None
    tool_results: list[dict] = field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 50
    done: bool = False
    tools_def: list = field(default_factory=list)

# --- 插件：System Prompt 注入 ---

def system_prompt_plugin(prompt: str):
    def apply(ctx: WaterfallContext):
        async def inject_prompt(state: LoopState, next: NextCallback):
            state.system_prompt = prompt
            if not state.messages:
                state.messages.append({"role": "system", "content": prompt})
            return await next(state)
        ctx.waterfall("agent/loop", inject_prompt)
    return apply

# --- 插件：LLM 调用 ---

def llm_plugin(llm_client: Any):
    def apply(ctx: WaterfallContext):
        async def call_llm(state: LoopState, next: NextCallback):
            response: LLMResponse = await llm_client.chat(
                state.messages, 
                tools=state.tools_def
            )
            state.response = response
            return await next(state)
        ctx.waterfall("agent/loop", call_llm)
    return apply

# --- 插件：工具执行 ---

def tool_execution_plugin(tool_registry: ToolRegistry):
    def apply(ctx: WaterfallContext):
        async def execute_tools(state: LoopState, next: NextCallback):
            if not state.response or not state.response.tool_calls:
                state.done = True  # 无工具调用，标记完成
                return await next(state)
            
            results = []
            for tc in state.response.tool_calls:
                tool = tool_registry.get(tc.name)
                try:
                    result = await tool.handler(**tc.arguments)
                    results.append({
                        "tool_call_id": tc.id,
                        "content": str(result),
                        "error": None
                    })
                except Exception as e:
                    results.append({
                        "tool_call_id": tc.id,
                        "content": None,
                        "error": str(e)
                    })
            
            state.tool_results = results
            return await next(state)
        ctx.waterfall("agent/loop", execute_tools)
    return apply

# --- 插件：循环卫生 Guard ---

def hygiene_plugin(max_repeats: int = 3):
    def apply(ctx: WaterfallContext):
        recent_calls = []
        
        async def check_hygiene(state: LoopState, next: NextCallback):
            if state.response and state.response.tool_calls:
                for tc in state.response.tool_calls:
                    sig = f"{tc.name}:{str(sorted(tc.arguments.items()))}"
                    recent_calls.append(sig)
                    if len(recent_calls) > 5:
                        recent_calls.pop(0)
                    if recent_calls.count(sig) >= max_repeats:
                        state.done = True
                        state.messages.append({
                            "role": "system",
                            "content": f"[Guard] Stopped: {tc.name} called {max_repeats} times with same args. Try a different approach."
                        })
                        return state  # 短路，不调用 next()
            return await next(state)
        
        ctx.waterfall("agent/loop/before-tools", check_hygiene)
    return apply

# --- 插件：上下文压缩 ---

def compaction_plugin(max_tokens: int = 100000, token_counter: Callable = None):
    def apply(ctx: WaterfallContext):
        async def maybe_compact(state: LoopState, next: NextCallback):
            if token_counter:
                token_count = await token_counter(state.messages)
                if token_count > max_tokens:
                    # 压缩：保留 system + 最近 N 轮消息，中间的摘要化
                    # 简化实现：保留第一条(system)和最后5条
                    if len(state.messages) > 7:
                        state.messages = [state.messages[0]] + state.messages[-6:]
                        state.messages.insert(1, {
                            "role": "system",
                            "content": "[Compaction] Earlier conversation was compressed."
                        })
            return await next(state)
        ctx.waterfall("agent/loop", maybe_compact)
    return apply

# --- 核心 Agent ---

class WaterfallAgent:
    """Cordis waterfall 事件链驱动的 Agent"""
    
    def __init__(self):
        self.ctx = WaterfallContext()
        self.tool_registry = ToolRegistry.get_instance()
        self._plugins_applied = False
    
    def use(self, plugin_factory: Callable):
        """安装插件"""
        plugin_factory(self.ctx)
    
    async def run(self, user_message: str) -> str:
        """主循环：每次迭代触发 agent/loop waterfall"""
        state = LoopState(
            messages=[{"role": "user", "content": user_message}],
            tools_def=[
                {"name": t.name, "description": t.description, "parameters": t.parameters}
                for t in self.tool_registry.list_all()
            ]
        )
        
        while not state.done and state.iteration < state.max_iterations:
            state.iteration += 1
            state.response = None
            state.tool_results = []
            
            # 触发 waterfall 链
            state = await self.ctx.dispatch_waterfall("agent/loop", state)
            
            # 注入工具结果到消息历史
            if state.response:
                state.messages.append({
                    "role": "assistant",
                    "content": state.response.content,
                    "tool_calls": state.response.tool_calls
                })
            for r in state.tool_results:
                state.messages.append({
                    "role": "tool",
                    "content": r["content"] or r["error"],
                    "tool_call_id": r["tool_call_id"]
                })
        
        self.ctx.dispose()
        return state.response.content if state.response else "No response"
```

**使用示例**：

```python
# 创建 Agent 并组装插件
agent = WaterfallAgent()
agent.use(system_prompt_plugin("You are a coding assistant."))
agent.use(compaction_plugin(max_tokens=80000, token_counter=count_tokens))
agent.use(llm_plugin(mock_llm))
agent.use(hygiene_plugin(max_repeats=3))
agent.use(tool_execution_plugin(registry))

# 执行
result = await agent.run("List Python files and count lines")
```

**特点分析**：
- ✅ 极高扩展性：新功能只需添加 waterfall 监听器
- ✅ 插件可以在任意阶段短路（不调用 next()）
- ✅ 注册即副作用，Fiber dispose 自动清理
- ✅ 模型可见 ⟺ 可日志化原则
- ❌ 控制流不直观，需要追踪监听器注册顺序
- ❌ 调试需要理解 waterfall 链的传递过程

## 实现四：Agent/Runner 分层委托（veadk-python 风格）

Agent 持有配置，Runner 负责执行循环，可委托给不同运行时后端。

```python
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field

# --- Agent 定义 ---

@dataclass
class AgentConfig:
    """Agent 配置（数据类，无逻辑）"""
    model_name: str = "gpt-4o"
    model_provider: str = "openai"
    model_api_base: str = ""
    api_key: str = ""
    tools: list[str] = field(default_factory=list)
    system_prompt: str = "You are a helpful assistant."
    max_iterations: int = 30
    temperature: float = 0.7
    short_term_memory_limit: int = 50  # 消息条数
    long_term_memory_enabled: bool = False
    runtime: str = "base"  # base | codex | piagent

class Agent:
    """纯配置 + 状态，不包含执行逻辑"""
    def __init__(self, config: AgentConfig):
        self.config = config
        self.short_term_memory: list[dict] = []
        self.long_term_memory: list[dict] = []

# --- Runtime 抽象 ---

class BaseRuntime(ABC):
    """运行时基类"""
    
    @abstractmethod
    async def execute(self, agent: Agent, messages: list[dict]) -> str:
        pass

# --- Base Runtime：本地实现 ---

class LocalRuntime(BaseRuntime):
    """veadk 自己的 Agent 循环实现"""
    
    def __init__(self, llm_client: Any, tool_registry: ToolRegistry):
        self.llm = llm_client
        self.registry = tool_registry
    
    async def execute(self, agent: Agent, messages: list[dict]) -> str:
        system_msg = {"role": "system", "content": agent.config.system_prompt}
        all_messages = [system_msg] + agent.short_term_memory + messages
        
        tools_def = [
            {"name": t.name, "description": t.description, "parameters": t.parameters}
            for t in self.registry.list_all()
            if not agent.config.tools or t.name in agent.config.tools
        ]
        
        for i in range(agent.config.max_iterations):
            response: LLMResponse = await self.llm.chat(
                all_messages, 
                tools=tools_def,
                temperature=agent.config.temperature
            )
            
            if not response.tool_calls:
                # 更新短期记忆
                agent.short_term_memory.extend(messages)
                agent.short_term_memory.append({"role": "assistant", "content": response.content})
                if len(agent.short_term_memory) > agent.config.short_term_memory_limit:
                    agent.short_term_memory = agent.short_term_memory[-agent.config.short_term_memory_limit:]
                return response.content or ""
            
            all_messages.append({"role": "assistant", "content": response.content, "tool_calls": response.tool_calls})
            for tc in response.tool_calls:
                tool = self.registry.get(tc.name)
                try:
                    result = await tool.handler(**tc.arguments)
                    all_messages.append({"role": "tool", "content": str(result), "tool_call_id": tc.id})
                except Exception as e:
                    all_messages.append({"role": "tool", "content": f"Error: {e}", "tool_call_id": tc.id})
        
        return "Max iterations reached"

# --- Codex Runtime：委托给 OpenAI Codex ---

class CodexRuntime(BaseRuntime):
    """委托给 OpenAI Codex Agent 运行时"""
    
    def __init__(self, codex_client: Any):
        self.codex = codex_client
    
    async def execute(self, agent: Agent, messages: list[dict]) -> str:
        # 将 Agent 配置映射为 Codex 格式
        codex_request = {
            "model": agent.config.model_name,
            "instructions": agent.config.system_prompt,
            "tools": agent.config.tools,
            "messages": messages,
        }
        response = await self.codex.agents.run(**codex_request)
        return response.output

# --- Runner ---

class Runner:
    """负责选择运行时并执行"""
    
    def __init__(self):
        self._runtimes: dict[str, BaseRuntime] = {}
    
    def register_runtime(self, name: str, runtime: BaseRuntime):
        self._runtimes[name] = runtime
    
    def select_runtime(self, agent: Agent) -> BaseRuntime:
        runtime_name = agent.config.runtime
        if runtime_name not in self._runtimes:
            raise ValueError(f"Unknown runtime: {runtime_name}. Available: {list(self._runtimes.keys())}")
        return self._runtimes[runtime_name]
    
    async def run(self, agent: Agent, user_message: str) -> str:
        runtime = self.select_runtime(agent)
        messages = [{"role": "user", "content": user_message}]
        return await runtime.execute(agent, messages)
```

**使用示例**：

```python
# 配置 Agent
config = AgentConfig(
    model_name="gpt-4o",
    model_provider="openai",
    tools=["web_search", "terminal", "read_file", "write_file"],
    system_prompt="You are a senior developer.",
    runtime="base"  # 使用本地运行时
)
agent = Agent(config)

# 设置 Runner
runner = Runner()
runner.register_runtime("base", LocalRuntime(mock_llm, registry))
runner.register_runtime("codex", CodexRuntime(mock_codex_client))

# 运行
result = await runner.run(agent, "Explain Python decorators")

# 切换到 Codex 运行时（无需改变 Agent 配置）
agent.config.runtime = "codex"
result2 = await runner.run(agent, "Explain Python decorators")
```

**特点分析**：
- ✅ Agent 和 Runner 完全分离，配置和执行解耦
- ✅ 运行时可切换，同一配置在不同引擎上运行
- ✅ 支持记忆管理（短期/长期）
- ❌ 增加了抽象层开销
- ❌ Runtime 间行为一致性难以保证

## 四种模式对比矩阵

| 维度 | 单体可配置(hermes) | 状态机(Zleap) | 事件链(Cordis/dsh) | 分层委托(veadk) |
|------|-------------------|--------------|-------------------|----------------|
| **核心隐喻** | 大而全的类 | 生命周期状态机 | 中间件管道 | 配置/执行分离 |
| **扩展方式** | 参数+回调 | Hook点+Workspace | waterfall插件 | Runtime后端 |
| **代码量** | 中（一个大类） | 大（三级状态机） | 小（插件组合） | 中（抽象层+实现） |
| **学习曲线** | 中等（参数多） | 高（理解状态机） | 高（事件思维） | 中（分层思维） |
| **可测试性** | 中（需mock很多） | 好（状态可观测） | 好（插件独立测） | 最好（Runtime隔离） |
| **并发工具** | ✅ 三种模式 | ❌ 顺序执行 | 插件可扩展 | Runtime决定 |
| **安全隔离** | 授权门控 | Workspace白名单 | guard包+策略 | Runtime级 |
| **调试难度** | 中 | 低（状态清晰） | 高（追踪链） | 中 |
| **适合场景** | 通用Agent产品 | 流水线工作流 | 高度可扩展平台 | 多后端部署 |

## 架构选择决策树

```
需要构建 Agent？
├─ 快速原型/简单应用 → 单体可配置模式（hermes 风格）
│   └─ 优点：一个类搞定，开箱即用
│
├─ 多阶段流水线（规划→执行→审查） → 状态机模式（Zleap 风格）
│   └─ 优点：阶段隔离强，安全可控
│
├─ 插件化平台/需要第三方扩展 → 事件链模式（Cordis/dsh 风格）
│   └─ 优点：插件独立开发，热插拔
│
└─ 多运行时后端（本地+云端） → 分层委托模式（veadk 风格）
    └─ 优点：一套配置，多处运行
```

## 相关概念

- Agent 核心循环模式
- 工具系统
- 插件化架构模式
- 多智能体编排
- 模型 Provider 抽象
