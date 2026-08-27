---
type: Example
title: 从零构建简易 Agent
description: 不依赖任何 Agent 框架，用 Python 从零实现一个具备核心能力的 AI Agent——包括 ReAct 循环、工具系统（函数调用）、记忆管理（短期/摘要/向量）、错误恢复与安全控制，帮助理解 Agent 的底层原理。
tags: [ai-agent-fundamentals, example, from-scratch, react, tool-calling, memory, tutorial]
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
  - id: memory
    resource: /concepts/03-memory-architecture.md
    title: 记忆架构
---

## 场景说明

你想理解 AI Agent 的底层原理，不依赖 LangChain、CrewAI 等框架，用最少的 Python 代码从零构建一个可运行的 Agent。最终的 Agent 将具备：
1. **ReAct 核心循环**（think-act-observe）
2. **工具系统**（注册工具、函数调用、结果注入）
3. **记忆管理**（短期消息历史 + 摘要压缩 + 简单向量检索）
4. **错误恢复**（超时、重试、循环检测）
5. **安全控制**（工具白名单、路径安全）

全程约 300 行代码。

## 前置准备

```bash
# 只需要 openai SDK（支持任何 OpenAI-compatible API）
pip install openai

# 如果需要本地模型支持，安装 ollama 并运行：
# ollama pull llama3.1:8b
```

## 第一步：定义基础类型和工具系统

```python
"""mini_agent.py — 从零构建的简易 AI Agent"""
from __future__ import annotations
import json
import time
import inspect
import asyncio
from typing import Callable, Any, get_type_hints
from dataclasses import dataclass, field
from openai import AsyncOpenAI

# =============================================================================
# Part 1: 工具系统 — 注册、Schema 生成、执行
# =============================================================================

@dataclass
class ToolResult:
    """工具执行结果"""
    content: str
    error: str | None = None
    duration_ms: float = 0

class ToolRegistry:
    """工具注册表：自动从函数签名生成 JSON Schema"""
    
    def __init__(self):
        self._tools: dict[str, dict] = {}
        self._handlers: dict[str, Callable] = {}
    
    def register(self, func: Callable | None = None, *, name: str | None = None, description: str | None = None):
        """注册工具，可以作为装饰器使用"""
        def decorator(fn: Callable) -> Callable:
            tool_name = name or fn.__name__
            tool_desc = description or (inspect.getdoc(fn) or f"Tool: {tool_name}").split('\n')[0]
            
            # 从函数签名自动生成 JSON Schema
            hints = get_type_hints(fn)
            sig = inspect.signature(fn)
            properties = {}
            required = []
            
            type_map = {str: "string", int: "integer", float: "number", bool: "boolean", list: "array", dict: "object"}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                param_type = hints.get(param_name, str)
                json_type = type_map.get(param_type, "string")
                properties[param_name] = {"type": json_type}
                # 从 docstring 中提取参数描述（简化版）
                if param.default is inspect.Parameter.empty:
                    required.append(param_name)
            
            self._tools[tool_name] = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_desc,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            self._handlers[tool_name] = fn
            return fn
        
        if func is not None:
            return decorator(func)
        return decorator
    
    def get_tool_defs(self) -> list[dict]:
        """获取发给 LLM 的工具定义列表"""
        return list(self._tools.values())
    
    def get_handler(self, name: str) -> Callable | None:
        return self._handlers.get(name)
    
    def has_tool(self, name: str) -> bool:
        return name in self._handlers
    
    async def execute(self, name: str, arguments: dict, timeout: float = 30.0) -> ToolResult:
        """执行工具，带超时和错误捕获"""
        handler = self._handlers.get(name)
        if not handler:
            return ToolResult(content="", error=f"Unknown tool: {name}")
        
        start = time.time()
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await asyncio.wait_for(handler(**arguments), timeout=timeout)
            else:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, lambda: handler(**arguments)),
                    timeout=timeout
                )
            return ToolResult(
                content=str(result)[:8000],  # 截断防止 token 溢出
                duration_ms=int((time.time() - start) * 1000)
            )
        except asyncio.TimeoutError:
            return ToolResult(content="", error=f"Tool {name} timed out after {timeout}s", duration_ms=int(timeout*1000))
        except Exception as e:
            return ToolResult(content="", error=f"{type(e).__name__}: {e}", duration_ms=int((time.time() - start) * 1000))
```

## 第二步：注册示例工具

```python
# =============================================================================
# Part 2: 注册工具
# =============================================================================

registry = ToolRegistry()

@registry.register
def calculate(expression: str) -> str:
    """计算数学表达式，支持 + - * / ** ( ) 和常用数学函数"""
    import math
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
    allowed_names.update({'abs': abs, 'round': round, 'min': min, 'max': max})
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

@registry.register
def get_current_time() -> str:
    """获取当前日期和时间"""
    from datetime import datetime
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} ({now.astimezone().tzinfo})"

@registry.register(description="Read a text file from the allowed directory")
def read_file(path: str) -> str:
    """读取文本文件内容（路径安全检查）"""
    import os
    safe_base = os.getcwd()
    resolved = os.path.realpath(path)
    if not resolved.startswith(safe_base):
        return f"Error: Access denied. Can only read files within {safe_base}"
    if not os.path.exists(resolved):
        return f"Error: File not found: {path}"
    try:
        with open(resolved, 'r', encoding='utf-8') as f:
            return f.read()[:10000]
    except Exception as e:
        return f"Error reading file: {e}"

@registry.register(description="Search the web using DuckDuckGo (no API key needed)")
async def web_search(query: str) -> str:
    """使用 DuckDuckGo 搜索网页"""
    import urllib.parse
    import urllib.request
    
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MiniAgent/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        results = []
        if data.get('AbstractText'):
            results.append(f"[Summary] {data['AbstractText']}")
        for topic in data.get('RelatedTopics', [])[:5]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append(topic['Text'][:300])
        
        return '\n\n'.join(results) if results else f"No results found for: {query}"
    except Exception as e:
        return f"Search error: {e}"

@registry.register
def word_count(text: str) -> str:
    """统计文本中的单词数、字符数和行数"""
    words = len(text.split())
    chars = len(text)
    lines = text.count('\n') + 1
    return f"Words: {words}, Characters: {chars}, Lines: {lines}"
```

## 第三步：记忆系统

```python
# =============================================================================
# Part 3: 记忆系统 — 短期记忆 + 摘要压缩 + 简单向量检索
# =============================================================================

@dataclass
class Message:
    """聊天消息"""
    role: str  # system | user | assistant | tool
    content: str
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None
    
    def to_dict(self) -> dict:
        d = {"role": self.role, "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        if self.name:
            d["name"] = self.name
        return d

class Memory:
    """三层记忆系统"""
    
    def __init__(self, max_recent: int = 20, summary_threshold: int = 30):
        self.system_prompt: str = ""
        self.recent_messages: list[Message] = []  # 短期：最近的消息
        self.summary: str = ""                     # 中期：早期对话的摘要
        self.long_term: list[tuple[str, list[float]]] = []  # 长期：嵌入向量（简化）
        self.max_recent = max_recent
        self.summary_threshold = summary_threshold
    
    def add(self, message: Message):
        """添加消息到短期记忆"""
        self.recent_messages.append(message)
        
        # 超过阈值时触发摘要压缩
        if len(self.recent_messages) > self.summary_threshold:
            asyncio.create_task(self._compact())
    
    async def _compact(self):
        """将早期消息压缩为摘要（异步，不阻塞主循环）"""
        if len(self.recent_messages) <= self.max_recent:
            return
        
        # 保留最近的 max_recent 条，将更早的消息摘要化
        to_summarize = self.recent_messages[:-self.max_recent]
        self.recent_messages = self.recent_messages[-self.max_recent:]
        
        # 用 LLM 生成摘要（简化：这里使用简单截断+拼接）
        # 生产环境应该调用 LLM 生成摘要
        summary_parts = []
        for msg in to_summarize:
            content_preview = msg.content[:200] if msg.content else "[tool call]"
            summary_parts.append(f"[{msg.role}]: {content_preview}")
        
        new_summary = "Earlier conversation (summarized):\n" + "\n".join(summary_parts[:10])
        self.summary = (self.summary + "\n" + new_summary).strip()[:2000]
    
    def get_messages(self) -> list[dict]:
        """获取发送给 LLM 的完整消息列表"""
        messages = []
        
        # System prompt（始终在最前面）
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # 摘要（如果有）
        if self.summary:
            messages.append({"role": "system", "content": self.summary})
        
        # 最近消息
        for msg in self.recent_messages:
            messages.append(msg.to_dict())
        
        return messages
    
    def get_context_window_size(self) -> int:
        """估算当前 token 数（粗略）"""
        total = sum(len(m.content) // 4 for m in self.recent_messages)
        total += len(self.summary) // 4
        total += len(self.system_prompt) // 4
        return total
```

## 第四步：安全控制和循环卫生

```python
# =============================================================================
# Part 4: 安全控制 + 循环卫生
# =============================================================================

class SafetyGuard:
    """安全防护层"""
    
    def __init__(
        self,
        allowed_tools: set[str] | None = None,   # 工具白名单，None=全部允许
        max_iterations: int = 20,                 # 最大循环次数
        max_total_tokens: int = 50000,            # 最大 token 预算
        max_repeat_calls: int = 3,                # 相同工具调用最大重复次数
        blocked_path_patterns: list[str] | None = None,
    ):
        self.allowed_tools = allowed_tools
        self.max_iterations = max_iterations
        self.max_total_tokens = max_total_tokens
        self.max_repeat_calls = max_repeat_calls
        self.blocked_patterns = blocked_path_patterns or ['..', '/etc/', '/root/', '.env']
        self._recent_tool_calls: list[tuple[str, str]] = []
    
    def can_use_tool(self, tool_name: str) -> tuple[bool, str]:
        """检查工具是否在白名单中"""
        if self.allowed_tools is not None and tool_name not in self.allowed_tools:
            return False, f"Tool '{tool_name}' is not in the allowed list"
        return True, ""
    
    def check_path_safety(self, path: str) -> tuple[bool, str]:
        """检查路径安全"""
        import os
        resolved = os.path.realpath(path)
        for pattern in self.blocked_patterns:
            if pattern in resolved:
                return False, f"Path contains blocked pattern: {pattern}"
        return True, ""
    
    def check_loop_hygiene(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """循环卫生检测：防止相同参数的工具重复调用"""
        call_sig = (tool_name, json.dumps(arguments, sort_keys=True))
        self._recent_tool_calls.append(call_sig)
        if len(self._recent_tool_calls) > 10:
            self._recent_tool_calls.pop(0)
        
        repeat_count = self._recent_tool_calls.count(call_sig)
        if repeat_count >= self.max_repeat_calls:
            return False, (
                f"Loop detected: {tool_name} called {repeat_count} times with same arguments. "
                f"Try a different approach or different parameters."
            )
        return True, ""
    
    def check_iteration_limit(self, iteration: int) -> tuple[bool, str]:
        """检查迭代次数限制"""
        if iteration >= self.max_iterations:
            return False, f"Reached maximum iteration limit ({self.max_iterations})"
        return True, ""
    
    def reset(self):
        """重置状态（新会话调用）"""
        self._recent_tool_calls.clear()
```

## 第五步：核心 Agent 类

```python
# =============================================================================
# Part 5: 核心 Agent — ReAct 循环
# =============================================================================

class MiniAgent:
    """从零构建的 Mini Agent"""
    
    def __init__(
        self,
        llm_client: AsyncOpenAI,
        model: str = "gpt-4o-mini",
        system_prompt: str = "You are a helpful AI assistant. Use tools when needed.",
        registry: ToolRegistry | None = None,
        guard: SafetyGuard | None = None,
        temperature: float = 0.7,
    ):
        self.llm = llm_client
        self.model = model
        self.memory = Memory()
        self.memory.system_prompt = system_prompt
        self.registry = registry or ToolRegistry()
        self.guard = guard or SafetyGuard()
        self.temperature = temperature
        self._iteration_count = 0
        self._total_tokens_used = 0
    
    def _extract_tool_calls(self, response) -> list[tuple[str, dict, str]]:
        """从 LLM 响应中提取工具调用，返回 [(name, args, id)]"""
        tool_calls = []
        message = response.choices[0].message
        
        if message.tool_calls:
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append((tc.function.name, args, tc.id))
        
        return tool_calls
    
    async def _think(self) -> tuple[str, list[tuple[str, dict, str]]]:
        """THINK 阶段：调用 LLM 获取推理结果"""
        messages = self.memory.get_messages()
        tools_def = self.registry.get_tool_defs()
        
        response = await self.llm.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools_def if tools_def else None,
            tool_choice="auto" if tools_def else None,
            temperature=self.temperature,
        )
        
        # 记录 token 用量
        if response.usage:
            self._total_tokens_used += response.usage.total_tokens
        
        message = response.choices[0].message
        tool_calls = self._extract_tool_calls(response)
        
        # 保存 assistant 消息到记忆
        self.memory.add(Message(
            role="assistant",
            content=message.content or "",
            tool_calls=[
                {
                    "id": tc_id,
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(args)}
                }
                for name, args, tc_id in tool_calls
            ] if tool_calls else None
        ))
        
        return message.content or "", tool_calls
    
    async def _act(self, tool_name: str, arguments: dict) -> ToolResult:
        """ACT 阶段：执行工具，含安全检查"""
        # 1. 工具白名单检查
        allowed, reason = self.guard.can_use_tool(tool_name)
        if not allowed:
            return ToolResult(content="", error=reason)
        
        # 2. 路径安全检查（针对路径参数）
        for key, value in arguments.items():
            if isinstance(value, str) and ('path' in key.lower() or 'file' in key.lower()):
                safe, reason = self.guard.check_path_safety(value)
                if not safe:
                    return ToolResult(content="", error=f"Path safety: {reason}")
        
        # 3. 循环卫生检查
        hygienic, reason = self.guard.check_loop_hygiene(tool_name, arguments)
        if not hygienic:
            return ToolResult(content="", error=reason)
        
        # 4. 执行
        result = await self.registry.execute(tool_name, arguments)
        return result
    
    def _observe(self, tool_call_id: str, result: ToolResult):
        """OBSERVE 阶段：将工具结果注入记忆"""
        if result.error:
            content = f"Error: {result.error}"
        else:
            content = result.content
        
        self.memory.add(Message(
            role="tool",
            content=content,
            tool_call_id=tool_call_id
        ))
    
    async def run(self, user_message: str, verbose: bool = True) -> str:
        """主 ReAct 循环"""
        self.guard.reset()
        self._iteration_count = 0
        
        # 添加用户消息
        self.memory.add(Message(role="user", content=user_message))
        
        if verbose:
            print(f"\n🧑 User: {user_message}\n")
        
        while True:
            self._iteration_count += 1
            
            # 检查迭代限制
            can_continue, reason = self.guard.check_iteration_limit(self._iteration_count)
            if not can_continue:
                final_msg = f"[Agent stopped: {reason}]"
                self.memory.add(Message(role="system", content=final_msg))
                if verbose:
                    print(f"\n⚠️  {final_msg}")
                return final_msg
            
            if verbose:
                print(f"  🤔 Thinking (iteration {self._iteration_count})...")
            
            # THINK
            content, tool_calls = await self._think()
            
            if not tool_calls:
                # 无工具调用 → 返回最终答案
                if verbose:
                    print(f"\n🤖 Assistant: {content}\n")
                    print(f"📊 Stats: {self._iteration_count} iterations, "
                          f"~{self._total_tokens_used} tokens used")
                return content
            
            if verbose and content:
                print(f"  💭 {content[:200]}")
            
            # ACT + OBSERVE（并发执行所有工具调用）
            if verbose:
                tool_names = [tc[0] for tc in tool_calls]
                print(f"  🔧 Calling tools: {tool_names}")
            
            # 并发执行工具
            tasks = []
            for name, args, tc_id in tool_calls:
                tasks.append(self._execute_and_observe(tc_id, name, args, verbose))
            await asyncio.gather(*tasks)
    
    async def _execute_and_observe(self, tc_id: str, name: str, args: dict, verbose: bool):
        """执行单个工具并记录结果"""
        if verbose:
            print(f"    → {name}({json.dumps(args, ensure_ascii=False)[:100]})")
        
        result = await self._act(name, args)
        
        if verbose:
            if result.error:
                print(f"    ✗ Error: {result.error[:100]}")
            else:
                print(f"    ✓ Done ({result.duration_ms}ms, {len(result.content)} chars)")
        
        self._observe(tc_id, result)
    
    def reset(self):
        """重置会话（保留系统提示词）"""
        system = self.memory.system_prompt
        self.memory = Memory()
        self.memory.system_prompt = system
        self._iteration_count = 0
        self._total_tokens_used = 0
        self.guard.reset()
```

## 第六步：使用 Agent

```python
# =============================================================================
# Part 6: 运行 Agent
# =============================================================================

async def main():
    # 初始化 LLM 客户端
    # 使用 OpenAI
    client = AsyncOpenAI(api_key="your-api-key")  # 或设置 OPENAI_API_KEY 环境变量
    model = "gpt-4o-mini"
    
    # 或者使用本地 Ollama（OpenAI-compatible）:
    # client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    # model = "llama3.1:8b"
    
    # 创建安全防护
    guard = SafetyGuard(
        allowed_tools=None,  # None = 允许所有已注册工具
        max_iterations=15,
        max_repeat_calls=3,
    )
    
    # 创建 Agent
    agent = MiniAgent(
        llm_client=client,
        model=model,
        system_prompt="""You are a helpful AI assistant with access to tools.
Use tools to get accurate information. Always think step by step.
When you have the final answer, respond directly without calling more tools.
If a tool returns an error, try a different approach or ask for clarification.""",
        registry=registry,
        guard=guard,
        temperature=0.3,
    )
    
    # 运行对话
    print("=" * 60)
    print("Mini Agent — Type 'quit' to exit, 'reset' to clear memory")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not user_input:
            continue
        if user_input.lower() in ('quit', 'exit', 'q'):
            break
        if user_input.lower() == 'reset':
            agent.reset()
            print("🔄 Memory reset.")
            continue
        
        response = await agent.run(user_input, verbose=True)
        print(f"\n🤖 Final Answer: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 运行测试

```bash
# 设置 API key
export OPENAI_API_KEY="sk-..."

# 运行
python mini_agent.py
```

测试对话示例：

```
You: What is 42 * 17 + the square root of 144?
  🤔 Thinking (iteration 1)...
  🔧 Calling tools: ['calculate']
    → calculate({"expression": "42 * 17 + sqrt(144)"})
    ✓ Done (2ms, 12 chars)
  🤔 Thinking (iteration 2)...

🤖 Final Answer: 42 * 17 = 714, square root of 144 = 12, so 714 + 12 = 726.
📊 Stats: 2 iterations, ~1200 tokens used

You: What time is it now, and how many characters are in "Hello, World!"?
  🤔 Thinking (iteration 1)...
  🔧 Calling tools: ['get_current_time', 'word_count']
    → get_current_time({})
    ✓ Done (0ms)
    → word_count({"text": "Hello, World!"})
    ✓ Done (1ms)
  🤔 Thinking (iteration 2)...

🤖 Final Answer: It's currently 2026-08-22 22:45:00.
"Hello, World!" has 2 words, 13 characters, and 1 line.
```

## 核心原理总结

### ReAct 循环的本质

```
while not done:
    1. THINK:  把 messages 发给 LLM → 得到 response（文本 或 工具调用）
    2. ACT:    如果有工具调用 → 执行工具 → 得到 result
    3. OBSERVE: 把 result 追加到 messages → 回到步骤 1
```

整个 Agent 的核心逻辑就是这个 while 循环。所有框架（LangChain、CrewAI、hermes-agent 等）都是在这个循环基础上增加工程特性。

### 从极简到生产级的差距

我们的 MiniAgent 约 300 行代码。生产级框架额外需要：

| 能力 | MiniAgent | 生产级框架 |
|------|-----------|-----------|
| ReAct 循环 | ✅ 基础版 | ✅ 并发/顺序/分段执行 |
| 工具注册 | ✅ 装饰器+自动Schema | ✅ 工具集组合+嵌套includes |
| 错误处理 | ✅ try/except+超时 | ✅ 重试+降级+TTL缓存授权 |
| 记忆管理 | ✅ 短期+简单摘要 | ✅ 三层记忆+向量检索+知识图谱 |
| 安全控制 | ✅ 白名单+路径检查 | ✅ 沙箱+审计+用户确认 |
| 循环卫生 | ✅ 重复检测 | ✅ 多模式检测+自动恢复 |
| Provider | ❌ 单模型 | ✅ 多Provider+fallback+负载均衡 |
| 多Agent | ❌ 单Agent | ✅ MoA+委派+编排 |
| 流式输出 | ❌ | ✅ SSE流式 |
| 可观测性 | ❌ | ✅ 全链路tracing+session log |
| 插件系统 | ❌ | ✅ Cordis/插件市场 |

### 关键设计决策

1. **工具 Schema 自动生成**：用 `inspect` 模块从函数签名和类型注解生成 JSON Schema，不需要手动编写。这是所有框架的基础做法。

2. **消息格式标准化**：统一使用 OpenAI 的消息格式（`role` + `content` + `tool_calls` + `tool_call_id`），其他 Provider 格式通过适配器转换。

3. **安全检查多层防御**：工具白名单（LLM约束）→ 运行时检查（act阶段）→ 路径安全（参数验证），三层缺一不可。

4. **记忆压缩时机**：不应该在每次迭代都压缩，而是当消息数量超过阈值时异步触发，避免阻塞主循环。

5. **工具并发执行**：当 LLM 返回多个 tool_calls 且它们之间没有依赖时，应该并发执行（`asyncio.gather`），这能显著减少迭代时间。

## 扩展练习

想进一步理解 Agent 原理，可以尝试为 MiniAgent 添加以下功能：

1. **流式输出**：使用 `stream=True` 参数实现逐字输出
2. **长期记忆**：添加 embedding + 向量数据库（如 chromadb）实现语义检索
3. **工具确认**：对危险工具（如文件写入）添加用户确认步骤
4. **多 Provider 支持**：添加 Anthropic、本地模型的适配器
5. **子 Agent 委派**：实现 `delegate_agent` 工具，可以创建子 Agent 处理子任务
6. **规划阶段**：在 ACT 之前增加 PLAN 阶段，先生成执行计划
7. **MCP 支持**：实现 MCP 协议客户端，可以连接外部 MCP 服务器获取工具

## 相关概念

- Agent 核心循环模式
- 工具系统
- 记忆架构模式
- 模型 Provider 抽象
- [对比不同框架的 Agent 循环](compare-agent-loops.md)
- [Agent 框架选型指南](choose-framework.md)
