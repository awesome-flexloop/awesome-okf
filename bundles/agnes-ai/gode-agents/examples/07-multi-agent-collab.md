---
type: Example
title: 多智能体协作
description: 使用managed_agents实现多智能体协作，让主Agent调用子Agent
tags: [多智能体, 协作, managed_agents, 高级]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: agents-source
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: tools-source
    resource: /references/tools-api.md
    title: Tools API 参考
---

# 多智能体协作

## 概述

本示例演示如何使用 `managed_agents` 参数实现多智能体协作。通过将专业化的子 Agent（如搜索专家、计算专家、代码专家）注册到主 Agent，主 Agent 可以根据任务需求自动选择并调用合适的子 Agent 来完成子任务，形成"总管+专家"的协作模式。每个子 Agent 必须设置 `name` 和 `description`，主 Agent 根据 description 判断何时调用哪个子 Agent。

这个示例解决的核心问题：**如何将复杂任务分解给多个专业化 Agent 协同完成，而不是让一个大而全的 Agent 处理所有事情**。

## 前置条件

- Python 3.10+
- 安装 codified-smolagents 及相关依赖：
  ```bash
  pip install codified-smolagents duckduckgo-search requests markdownify
  ```
- 可选：安装 gradio 用于 Web UI：`pip install gradio`
- Hugging Face API Token（环境变量 `HF_TOKEN`）

## 完整代码

```python
"""
示例 07: 多智能体协作
演示：创建子Agent → name/description设置 → managed_agents注册 → 自动调用 → __call__模板 → GradioUI
"""

import os
from codified_smolagents import (
    ToolCallingAgent,
    CodeAgent,
    HfApiModel,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    tool,
)
from codified_smolagents.monitoring import LogLevel

model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")

# ============================================================
# 第一步：创建专业化的子 Agent
# ============================================================
# 每个子 Agent 必须设置 name 和 description（作为 managed agent 时必需）
# description 告诉主 Agent 这个子 Agent 擅长什么、什么时候应该调用它

# ---- 子Agent 1: 网页搜索专家 ----
web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=model,
    max_steps=6,
    verbosity_level=LogLevel.INFO,
    name="web_search_agent",
    description="""
    网页搜索专家。擅长在互联网上搜索最新信息、访问网页提取内容。
    当需要查找实时信息、新闻事件、最新技术动态、网站内容时使用此Agent。
    不要将数学计算或代码编写任务交给此Agent。
    """,
    provide_run_summary=True,  # 执行完后提供运行摘要给主Agent
)

# ---- 子Agent 2: 数学计算专家（CodeAgent，擅长精确计算） ----
math_agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=["math", "statistics", "numpy"],
    max_steps=5,
    verbosity_level=LogLevel.INFO,
    name="math_agent",
    description="""
    数学计算专家。擅长执行精确的数学计算、统计分析、数值运算。
    可以编写和运行Python代码来计算复杂的数学问题，如概率统计、微积分、
    线性代数、斐波那契数列、素数判断等。所有计算结果都是通过代码实际
    运行得到的，100%准确。当需要精确数学答案时使用此Agent。
    """,
    provide_run_summary=True,
)

# ---- 子Agent 3: 文本处理专家（自定义工具） ----
@tool
def text_analyzer(text: str, operation: str) -> str:
    """
    对文本进行分析和处理。
    Args:
        text: 要分析或处理的文本内容
        operation: 操作类型，支持 "summarize"(摘要)、"keywords"(关键词提取)、
                   "sentiment"(情感倾向)、"word_freq"(词频统计)、
                   "translate_en"(翻译为英文)、"readability"(可读性评分)
    """
    import re
    from collections import Counter

    if operation == "word_freq":
        words = re.findall(r'[\u4e00-\u9fff]|\w+', text.lower())
        freq = Counter(words).most_common(10)
        return "词频Top10: " + ", ".join(f"{w}({c})" for w, c in freq)
    elif operation == "word_count":
        return f"总字数: {len(text)}, 词数: {len(text.split())}"
    elif operation == "readability":
        sentences = max(1, len(re.findall(r'[。！？.!?]', text)))
        words = len(text.split())
        return f"平均句长: {words/sentences:.1f} 词/句"
    else:
        return f"不支持的操作: {operation}。支持: word_freq, word_count, readability"

text_agent = ToolCallingAgent(
    tools=[text_analyzer],
    model=model,
    max_steps=3,
    verbosity_level=LogLevel.INFO,
    name="text_agent",
    description="""
    文本处理专家。擅长对文本进行分析处理，包括词频统计、字数统计、
    可读性分析等。当需要对已有文本进行分析、统计或处理时使用此Agent。
    不具备搜索和数学计算能力。
    """,
    provide_run_summary=True,
)


# ============================================================
# 第二步：创建主 Agent，注册 managed_agents
# ============================================================
print("=" * 60)
print("🤖 创建主 Agent 并注册子 Agent")
print("=" * 60)

manager_agent = ToolCallingAgent(
    tools=[],  # 主 Agent 自己不需要工具，通过子 Agent 完成任务
    model=model,
    managed_agents=[web_agent, math_agent, text_agent],  # 注册子Agent
    max_steps=12,
    verbosity_level=LogLevel.INFO,
    # 可选：启用规划，让主 Agent 更好地分解任务
    planning_interval=4,
)

# 查看注册的 managed agents
print("\n📋 注册的子 Agent:")
for name, agent in manager_agent.managed_agents.items():
    print(f"  - {name}: {agent.description.strip()[:80]}...")


# ============================================================
# 第三步：主 Agent 自动选择调用子 Agent
# ============================================================
print("\n" + "=" * 60)
print("🔄 测试1: 需要数学计算的任务（应调用 math_agent）")
print("=" * 60)

result1 = manager_agent.run(
    "请计算从1到1000中，所有既能被7整除又能被3整除的数的和是多少？"
    "然后再计算这些数的平均值。"
)
print(f"\n✅ 主Agent回答:\n{result1}")


print("\n" + "=" * 60)
print("🔄 测试2: 需要搜索的任务（应调用 web_search_agent）")
print("=" * 60)

result2 = manager_agent.run(
    "搜索一下2026年人工智能领域最重要的突破或新闻是什么，给出简要总结。"
)
print(f"\n✅ 主Agent回答:\n{result2}")


# ============================================================
# 第四步：复杂任务：主 Agent 调用多个子 Agent 协作
# ============================================================
print("\n" + "=" * 60)
print("🔄 测试3: 复杂任务（需要多个子Agent协作）")
print("=" * 60)

result3 = manager_agent.run(
    """
    请完成以下综合任务：
    1. 搜索"Python编程语言"的相关信息
    2. 根据搜索结果，计算Python首次发布到2026年经过了多少年
    3. 对搜索到的核心信息做词频分析
    最后整合所有信息给出一个完整的回答。
    """
)
print(f"\n✅ 主Agent回答:\n{result3}")


# ============================================================
# 第五步：理解 __call__ 模板渲染机制
# ============================================================
print("\n" + "=" * 60)
print("📖 __call__ 模板渲染（task/report）")
print("=" * 60)
print("""
当主 Agent 调用一个子 Agent 时，会执行以下流程：

1. 渲染 managed_agent.task 模板：
   ┌─────────────────────────────────────────────┐
   │  你是一个专门的Agent，名叫 {name}。         │
   │  你的描述是：{description}                  │
   │  请完成以下任务：{task}                     │
   └─────────────────────────────────────────────┘
   → 子 Agent 收到渲染后的任务描述

2. 子 Agent 执行 self.run() 完成任务

3. 渲染 managed_agent.report 模板：
   ┌─────────────────────────────────────────────┐
   │  以下是 {name} 的执行结果：                │
   │  {result}                                   │
   └─────────────────────────────────────────────┘
   → 主 Agent 收到渲染后的报告

4. 如果 provide_run_summary=True，追加运行摘要：
   ┌─────────────────────────────────────────────┐
   │  执行摘要：执行了N步，使用了X工具...        │
   └─────────────────────────────────────────────┘
""")


# ============================================================
# 第六步：直接调用子 Agent（__call__ 方法）
# ============================================================
print("=" * 60)
print("🔧 直接调用子 Agent（绕过主Agent）")
print("=" * 60)

# 子 Agent 也可以直接通过 __call__ 调用
# __call__ 会自动渲染 task/report 模板
direct_result = math_agent("计算 2^20 的值是多少？")
print(f"\n🧮 math_agent 直接调用结果:\n{direct_result[:200]}")


# ============================================================
# 第七步：provide_run_summary 获取执行摘要
# ============================================================
print("\n" + "=" * 60)
print("📊 provide_run_summary 执行摘要")
print("=" * 60)

# 运行一个子Agent任务
_ = math_agent.run("计算1到100所有素数的和。")

# 通过 memory.steps 查看执行摘要信息
from codified_smolagents.memory import ActionStep, PlanningStep

action_steps = [s for s in math_agent.memory.steps if isinstance(s, ActionStep)]
print(f"math_agent 执行了 {len(action_steps)} 个行动步骤")
for i, step in enumerate(action_steps):
    if step.tool_calls:
        for tc in step.tool_calls:
            print(f"  Step {step.step_number}: 调用了代码执行")
    if step.error:
        print(f"  Step {step.step_number}: 遇到错误: {step.error}")
    if step.duration:
        print(f"  Step {step.step_number}: 耗时 {step.duration:.2f}秒")

print("""
💡 provide_run_summary=True 的作用：
  - 当子Agent完成任务后，会在返回结果中附加运行摘要
  - 摘要包含：执行步数、使用的工具、遇到的错误、关键决策点
  - 主Agent可以根据摘要判断子任务是否成功完成
  - 如果失败，主Agent可以决定重试或换一个子Agent
""")


# ============================================================
# 第八步：使用 GradioUI 可视化多Agent交互
# ============================================================
print("\n" + "=" * 60)
print("🌐 GradioUI 可视化界面")
print("=" * 60)
print("""
取消下面代码的注释即可启动 Gradio Web 界面：

```python
from codified_smolagents import GradioUI

# 创建一个带多Agent协作的完整系统
demo_agent = ToolCallingAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent, math_agent, text_agent],
    planning_interval=4,
    max_steps=15,
    verbosity_level=LogLevel.INFO,
)

# 启动 Gradio Web UI
# 默认在 http://localhost:7860 启动
GradioUI(demo_agent).launch(
    server_name="0.0.0.0",  # 允许外部访问
    server_port=7860,       # 端口号
    share=False,            # 是否创建公共链接
)
```

启动后你可以在浏览器中：
  - 直接输入问题与Agent对话
  - 观察Agent实时的思考过程和工具调用
  - 看到主Agent如何将任务分配给不同的子Agent
  - 流式输出，打字机效果回复
""")


# ============================================================
# 第九步：嵌套多Agent（子Agent也可以有自己的managed_agents）
# ============================================================
print("\n" + "=" * 60)
print("🪆 嵌套多智能体（树形结构）")
print("=" * 60)
print("""
多智能体系统支持树形嵌套：

        主Agent (Manager)
       ├── 搜索团队Leader
       │   ├── 网页搜索Agent
       │   └── 维基百科Agent
       ├── 计算团队Leader
       │   ├── 数学计算Agent
       │   └── 数据分析Agent
       └── 写作Agent

实现方式：
  1. 创建底层叶子Agent（web_agent, wiki_agent, math_agent...）
  2. 创建团队Leader，将底层Agent加入其 managed_agents
  3. 创建顶层Manager，将团队Leader加入其 managed_agents

注意事项：
  - 嵌套层级不宜过深（建议不超过3层），否则延迟和token成本会很高
  - 每个Agent都需要清晰的 name 和 description
  - 合理设置 max_steps，避免递归调用过深
""")

# 演示简单的两层嵌套结构
@tool
def wiki_search(query: str) -> str:
    """
    在维基百科中搜索内容（模拟）。
    Args:
        query: 搜索关键词
    """
    return f"[维基百科模拟结果] 关于'{query}'的百科条目内容..."

wiki_agent = ToolCallingAgent(
    tools=[wiki_search],
    model=model,
    max_steps=3,
    verbosity_level=LogLevel.OFF,
    name="wiki_agent",
    description="维基百科搜索专家，用于查找百科知识和定义性内容。",
)

# 搜索团队Leader管理两个搜索Agent
search_team = ToolCallingAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent, wiki_agent],
    max_steps=6,
    verbosity_level=LogLevel.OFF,
    name="search_team",
    description="搜索团队，可以进行网页搜索和维基百科搜索。需要查找信息时使用。",
)

# 顶层Manager管理搜索团队和数学专家
top_manager = ToolCallingAgent(
    tools=[],
    model=model,
    managed_agents=[search_team, math_agent],
    max_steps=10,
    verbosity_level=LogLevel.OFF,
)

# 简单测试
try:
    nested_result = top_manager.run("圆周率π的值是多少？精确到小数点后10位。")
    print(f"\n嵌套多Agent回答: {nested_result[:200]}")
except Exception as e:
    print(f"嵌套Agent执行异常（可能需要更多步数或模型不支持深层规划）: {type(e).__name__}")


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("💡 多智能体协作最佳实践")
print("=" * 60)
print("""
  1. 子Agent设计原则：
     ✓ 每个子Agent只做一件事（单一职责）
     ✓ description 要清晰描述"什么时候该用我"
     ✓ name 使用有意义的英文标识符（python标识符规则）

  2. 主Agent设计原则：
     ✓ 主Agent工具列表通常为空（通过子Agent完成任务）
     ✓ 主Agent可以有自己的工具（也可以直接调用工具）
     ✓ 建议启用 planning_interval 帮助任务分解

  3. provide_run_summary 建议设为 True：
     ✓ 主Agent可以看到子Agent的执行摘要
     ✓ 便于判断子任务是否成功
     ✓ 便于调试多Agent系统

  4. 避免名称冲突：
     ✗ 工具名称和子Agent名称不能重复
     ✗ 系统会在初始化时检测冲突并抛异常

  5. 性能考虑：
     ⚠ 每次子Agent调用都涉及多步LLM推理
     ⚠ 嵌套过深会导致响应变慢、成本增加
     ⚠ 合理设置每层的 max_steps
""")
```

## 运行说明

1. 安装依赖：`pip install codified-smolagents duckduckgo-search requests markdownify`
2. 确保 `HF_TOKEN` 环境变量已设置。
3. 可选安装 gradio：`pip install gradio`（用于 Web UI 部分）
4. 将代码保存为 `07_multi_agent.py`。
5. 运行：`python 07_multi_agent.py`

**预期输出**：
```
============================================================
🤖 创建主 Agent 并注册子 Agent
============================================================

📋 注册的子 Agent:
  - web_search_agent: 网页搜索专家。擅长在互联网上搜索最新信息...
  - math_agent: 数学计算专家。擅长执行精确的数学计算...
  - text_agent: 文本处理专家。擅长对文本进行分析处理...

============================================================
🔄 测试1: 需要数学计算的任务（应调用 math_agent）
============================================================
Calling tools:
 math_agent(task="计算从1到1000中，所有既能被7整除又能被3整除的数的和...")
...
✅ 主Agent回答:
从1到1000中，既能被7整除又能被3整除的数（即能被21整除的数）的和是...
```

## 代码解析

### 1. 子 Agent 的必要属性

```python
web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    name="web_search_agent",           # 必须：有效Python标识符
    description="网页搜索专家...",     # 必须：清晰描述能力和使用场景
    provide_run_summary=True,          # 推荐：返回执行摘要
)
```

| 属性 | 是否必需 | 说明 |
|------|---------|------|
| `name` | 必需 | 子Agent的名称，必须是有效的Python标识符，不能与工具名重复 |
| `description` | 必需 | 告诉主Agent"这个子Agent擅长什么、什么时候该用它"，直接影响路由准确性 |
| `provide_run_summary` | 推荐 | 为True时，子Agent执行完后会返回运行摘要，帮助主Agent判断成功/失败 |

系统在初始化时通过 `_validate_name(name)` 验证名称有效性，通过 `_validate_tools_and_managed_agents()` 检测名称冲突。

### 2. managed_agents 参数

```python
manager_agent = ToolCallingAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent, math_agent, text_agent],  # 注册子Agent列表
)
```

- `managed_agents` 接收一个 Agent 列表。
- 初始化时 `_setup_managed_agents()` 会将其转换为 `{name: agent}` 字典。
- 主Agent在执行时，可以像调用工具一样调用子Agent——子Agent在内部被合并到工具调用字典中：`{**self.tools, **self.managed_agents}`。
- 当主Agent决定调用一个子Agent时，实际上是调用该子Agent的 `__call__()` 方法。

### 3. __call__ 模板渲染流程

```python
def __call__(self, task: str, **kwargs):
    # 1. 渲染 managed_agent.task 模板
    task_message = populate_template(
        self.prompt_templates["managed_agent"]["task"],
        {"name": self.name, "description": self.description, "task": task}
    )
    # 2. 执行 run()
    result = self.run(task_message, **kwargs)
    # 3. 渲染 managed_agent.report 模板
    report = populate_template(
        self.prompt_templates["managed_agent"]["report"],
        {"name": self.name, "response": result}
    )
    # 4. 可选追加摘要
    if self.provide_run_summary:
        report += f"\n执行摘要: ..."
    return report
```

- `ManagedAgentPromptTemplate` 包含两个字段：`task`（任务分配模板）和 `report`（结果报告模板）。
- 使用 Jinja2 模板引擎渲染，变量包括 `name`、`description`、`task`（输入）和 `response`（输出）。

### 4. Agent 自动路由机制

主Agent选择调用哪个子Agent的机制与选择工具完全相同：
1. 系统提示词中包含所有子Agent的name和description（类似工具列表）。
2. LLM根据任务需求和各子Agent的description，生成function call。
3. `execute_tool_call()` 在合并字典中查找并调用对应的子Agent。
4. 子Agent的返回结果作为Observation返回给主Agent。

这意味着description的质量直接影响路由准确性——description写得好，Agent才能被正确调用。

### 5. GradioUI 可视化

```python
from codified_smolagents import GradioUI
GradioUI(agent).launch(server_name="0.0.0.0", server_port=7860)
```

- `GradioUI` 接收一个 `MultiStepAgent` 实例。
- `launch()` 启动 Gradio Web 服务器，默认在 `http://localhost:7860`。
- 内部使用 `stream_to_gradio(agent, task)` 生成器，调用 `agent.run(stream=True)` 实现流式输出。
- 在多Agent场景下，Web UI 可以实时展示主Agent调用子Agent的过程，非常适合调试和演示。

### 6. 嵌套多Agent

子Agent也可以有自己的 `managed_agents`，形成树形协作结构。但需注意：
- 嵌套层数建议控制在3层以内。
- 每增加一层，响应延迟和token消耗都会显著增加。
- 最深层的叶子Agent应该具体执行任务，中间层负责任务分发。

## 扩展练习

1. **添加更多专业Agent**：创建一个"代码生成Agent"（CodeAgent，擅长编写代码）或"文件操作Agent"，加入多Agent系统。

2. **自定义ManagedAgentPromptTemplate**：通过 `prompt_templates` 参数传入自定义的 `ManagedAgentPromptTemplate`，改变任务分配和报告的格式。

3. **Agent保存与加载**：将多Agent系统保存到本地：
   ```python
   manager_agent.save("./multi_agent_system")
   # 在另一个脚本中加载：
   from codified_smolagents import MultiStepAgent
   loaded = MultiStepAgent.from_folder("./multi_agent_system")
   loaded.run("你好！")
   ```

4. **从Hub加载Agent作为子Agent**：
   ```python
   from codified_smolagents import MultiStepAgent
   hub_agent = MultiStepAgent.from_hub("username/my-agent", trust_remote_code=True)
   manager = ToolCallingAgent(
       tools=[], model=model,
       managed_agents=[hub_agent],
   )
   ```

5. **step_callbacks 监控多Agent交互**：
   ```python
   def monitor_calls(step_result):
       if hasattr(step_result, 'tool_calls') and step_result.tool_calls:
           for tc in step_result.tool_calls:
               print(f"[监控] Agent调用了: {tc.function.name}")
   manager = ToolCallingAgent(
       tools=[], model=model,
       managed_agents=[...],
       step_callbacks=[monitor_calls],
   )
   ```

6. **与 add_base_tools 结合**：主Agent也可以有自己的基础工具：
   ```python
   manager = CodeAgent(
       tools=[],
       model=model,
       managed_agents=[web_agent, math_agent],
       add_base_tools=True,  # 主Agent自己也能搜索，不一定非要通过子Agent
       max_steps=15,
   )
   ```

## 相关链接

- [高级特性总览](/concepts/14-advanced-features.md) — Managed Agents、Hub集成、GradioUI的综合说明
- [架构概述](/concepts/02-architecture-overview.md) — 多智能体在整体架构中的位置
- [多步智能体](/concepts/03-multi-step-agent.md) — ReAct循环和Agent调用机制
- [智能体类型](/concepts/10-agent-types.md) — 不同Agent类型在多Agent系统中的角色
- [提示词模板](/concepts/12-prompt-templates.md) — ManagedAgentPromptTemplate的自定义
- [监控与日志](/concepts/13-monitoring-logging.md) — step_callbacks和日志配置
- [Agents API 参考](/references/agents-api.md) — managed_agents、provide_run_summary、__call__的完整API
