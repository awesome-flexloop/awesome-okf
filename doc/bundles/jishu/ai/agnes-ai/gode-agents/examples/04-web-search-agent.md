---
type: Example
title: 构建网页搜索 Agent
description: 使用DuckDuckGoSearchTool和VisitWebpageTool构建联网搜索Agent
tags: [搜索, 网页, 工具组合]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: tools-source
    resource: /references/tools-api.md
    title: Tools API 参考
  - id: agents-source
    resource: /references/agents-api.md
    title: Agents API 参考
---

# 构建网页搜索 Agent

## 概述

本示例演示如何使用内置的 `DuckDuckGoSearchTool`（网页搜索）和 `VisitWebpageTool`（网页访问）构建一个能够联网获取实时信息的 Agent。通过 `add_base_tools=True` 一键加载基础工具集，或手动组合工具实现"搜索→访问→提取→回答"的信息检索工作流。

这个示例解决的核心问题：**如何让 Agent 突破训练数据的时间限制，获取最新的网络信息**。

## 前置条件

- Python 3.10+
- 安装 codified-smolagents 及搜索相关依赖：
  ```bash
  pip install codified-smolagents duckduckgo-search requests markdownify
  ```
- Hugging Face API Token（环境变量 `HF_TOKEN`）
- 网络连接（DuckDuckGo 搜索和网页访问需要联网）

## 完整代码

```python
"""
示例 04: 构建网页搜索 Agent
演示：add_base_tools → 单独使用搜索工具 → 访问网页 → 组合搜索+访问 → 错误处理
"""

from codified_smolagents import (
    ToolCallingAgent,
    CodeAgent,
    HfApiModel,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    FinalAnswerTool,
)
from codified_smolagents.monitoring import LogLevel

# ============================================================
# 第一步：使用 add_base_tools=True 一键加载基础工具
# ============================================================
# add_base_tools=True 会自动添加三个内置工具：
#   - DuckDuckGoSearchTool (web_search): DuckDuckGo 网络搜索
#   - VisitWebpageTool (visit_webpage): 访问网页并提取内容
#   - WikipediaSearchTool (search_wikipedia): 维基百科搜索
# （对于 ToolCallingAgent，还会添加 PythonInterpreterTool）

model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")

agent = ToolCallingAgent(
    tools=[],                 # 工具列表为空
    model=model,
    add_base_tools=True,      # 一键添加 web_search、visit_webpage、search_wikipedia
    max_steps=8,
    verbosity_level=LogLevel.INFO,
)

# 查看自动加载了哪些工具
print("=" * 60)
print("📦 add_base_tools=True 自动加载的工具：")
for name, tool in agent.tools.items():
    print(f"  - {name}: {tool.description[:80]}...")
print("=" * 60)

# 运行一个需要联网的查询
print("\n🌐 测试联网搜索：")
result1 = agent.run(
    "今天的科技新闻有哪些重大事件？请搜索最新的AI相关新闻，总结3条最重要的。"
)
print(f"\n✅ 回答:\n{result1}")


# ============================================================
# 第二步：单独使用 DuckDuckGoSearchTool
# ============================================================
print("\n" + "=" * 60)
print("🔍 单独使用 DuckDuckGoSearchTool")
print("=" * 60)

# 创建搜索工具实例
search_tool = DuckDuckGoSearchTool()

# 可以直接调用（不通过 Agent）
print("\n🔧 直接调用搜索工具：")
search_results = search_tool("Python 3.13 新特性")
print(search_results[:500] + "..." if len(search_results) > 500 else search_results)

# 将搜索工具单独交给 Agent
search_agent = ToolCallingAgent(
    tools=[search_tool],
    model=model,
    max_steps=4,
    verbosity_level=LogLevel.INFO,
)

print("\n🤖 Agent 使用搜索工具：")
result2 = search_agent.run(
    "搜索一下 Hugging Face smolagents 框架的最新版本号是多少？"
)
print(f"\n✅ 回答:\n{result2}")


# ============================================================
# 第三步：使用 VisitWebpageTool 访问网页内容
# ============================================================
print("\n" + "=" * 60)
print("🌐 单独使用 VisitWebpageTool 访问网页")
print("=" * 60)

visit_tool = VisitWebpageTool()

# 直接访问网页（返回 Markdown 格式的内容）
print("\n🔧 直接访问网页（截取前500字）：")
try:
    page_content = visit_tool("https://docs.python.org/3/tutorial/appetite.html")
    print(page_content[:500] + "...")
except Exception as e:
    print(f"访问失败（可能是网络问题）: {e}")

# 让 Agent 使用网页访问工具
visit_agent = ToolCallingAgent(
    tools=[visit_tool],
    model=model,
    max_steps=3,
    verbosity_level=LogLevel.INFO,
)

print("\n🤖 Agent 使用网页访问工具：")
result3 = visit_agent.run(
    "请访问 https://www.example.com 这个网页，告诉我网页的标题和主要内容是什么。"
)
print(f"\n✅ 回答:\n{result3}")


# ============================================================
# 第四步：组合搜索 + 网页访问回答复杂问题
# ============================================================
print("\n" + "=" * 60)
print("🔗 组合 web_search + visit_webpage 回答复杂问题")
print("=" * 60)

# 手动组合搜索和访问工具
web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=model,
    max_steps=10,
    verbosity_level=LogLevel.INFO,
)

# Agent 会自动规划：先搜索→找到相关链接→访问网页→提取信息→回答
print("\n🤖 多步骤网络研究：")
result4 = web_agent.run(
    "搜索 'codified-smolagents github' 找到项目主页，"
    "然后访问该页面，告诉我这个项目是做什么的，主要特性有哪些。"
)
print(f"\n✅ 回答:\n{result4}")


# ============================================================
# 第五步：CodeAgent 也能使用搜索工具
# ============================================================
print("\n" + "=" * 60)
print("💻 CodeAgent + 搜索工具")
print("=" * 60)

code_web_agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    additional_authorized_imports=["datetime", "json"],
    max_steps=8,
    verbosity_level=LogLevel.INFO,
)

result5 = code_web_agent.run(
    "搜索今天（2026年）奥运会的最新奖牌榜情况，"
    "然后用Python代码整理成一个简单的Markdown表格输出。"
)
print(f"\n✅ 回答:\n{result5}")


# ============================================================
# 第六步：错误处理与健壮性
# ============================================================
print("\n" + "=" * 60)
print("⚠️ 搜索中的错误处理")
print("=" * 60)

# 搜索工具可能因网络问题失败，Agent 会自动重试或调整策略
robust_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=5,
    verbosity_level=LogLevel.DEBUG,  # DEBUG 级别可看到重试和错误信息
)

# 提供一个可能搜索不到精确结果的查询
result6 = robust_agent.run(
    "搜索 'xyz_nonexistent_topic_12345'，如果搜索不到结果，就直接告诉我。"
)
print(f"\n✅ 回答:\n{result6}")

print("""
💡 错误处理最佳实践：
  1. 为 Agent 设置合理的 max_steps（建议 6-10 步），避免无限循环
  2. 使用 verbosity_level=DEBUG 观察搜索失败时的行为
  3. 在任务描述中给出明确指示，如"如果搜索不到就说没找到"
  4. 网络不可用时，Agent 可以降级为使用模型已有知识回答
""")
```

## 运行说明

1. 安装搜索依赖：`pip install duckduckgo-search requests markdownify`
2. 确保 `HF_TOKEN` 环境变量已设置，且网络可以访问 DuckDuckGo。
3. 将代码保存为 `04_web_search.py`。
4. 运行：`python 04_web_search.py`

**预期输出**：
```
============================================================
📦 add_base_tools=True 自动加载的工具：
  - final_answer: ...
  - web_search: DuckDuckGo网络搜索工具...
  - visit_webpage: 网页访问工具...
  - search_wikipedia: 维基百科搜索工具...
============================================================

🌐 测试联网搜索：
[Step 0: ...]
Calling tools:
 web_search(query="AI news today 2026")
...
✅ 回答:
根据最新搜索结果，今天的重大AI新闻包括...
```

> ⚠️ 注意：DuckDuckGo 搜索在某些网络环境下可能不稳定，如遇超时可重试或使用代理。

## 代码解析

### 1. add_base_tools 参数

```python
agent = ToolCallingAgent(
    tools=[],
    model=model,
    add_base_tools=True,  # 一键加载内置基础工具
)
```

当 `add_base_tools=True` 时，Agent 自动添加以下工具：

| 工具名称 | 类 | 功能 |
|---------|-----|------|
| `web_search` | `DuckDuckGoSearchTool` | 使用 DuckDuckGo 搜索引擎搜索网页 |
| `visit_webpage` | `VisitWebpageTool` | 访问指定 URL 并提取 Markdown 内容 |
| `search_wikipedia` | `WikipediaSearchTool` | 在维基百科中搜索条目 |
| `python_interpreter` | `PythonInterpreterTool` | Python 代码解释器（仅 ToolCallingAgent） |
| `final_answer` | `FinalAnswerTool` | 输出最终答案（始终自动添加） |

### 2. DuckDuckGoSearchTool

```python
search_tool = DuckDuckGoSearchTool()
results = search_tool("搜索关键词")
```

- `name = "web_search"`
- 使用 `duckduckgo_search.DDGS` 库执行搜索
- 输入：`query`（搜索关键词字符串）
- 输出：搜索结果文本（包含标题、摘要和链接）
- 无需 API Key，免费使用

### 3. VisitWebpageTool

```python
visit_tool = VisitWebpageTool()
content = visit_tool("https://example.com")
```

- `name = "visit_webpage"`
- 使用 `requests` 库获取网页 HTML
- 使用 `markdownify` 将 HTML 转换为 Markdown 格式（去除导航、广告等无关内容）
- 输入：`url`（网页 URL 字符串）
- 输出：网页正文内容的 Markdown 文本
- Agent 会先用 `web_search` 找到相关 URL，再用 `visit_webpage` 获取详细内容

### 4. 典型搜索工作流

```
用户问题 → LLM 判断需要搜索
    ↓
web_search(query) → 返回搜索结果列表（标题+摘要+URL）
    ↓
LLM 分析结果，选择最相关的 URL
    ↓
visit_webpage(url) → 返回网页全文 Markdown
    ↓
LLM 提取所需信息 → 给出最终回答
```

Agent 可能在多步中反复进行"搜索→访问"，直到收集到足够信息。

### 5. TOOL_MAPPING 字典

```python
from codified_smolagents.default_tools import TOOL_MAPPING
# {
#     "python_interpreter": PythonInterpreterTool,
#     "web_search": DuckDuckGoSearchTool,
#     "visit_webpage": VisitWebpageTool,
#     "search_wikipedia": WikipediaSearchTool,
#     "final_answer": FinalAnswerTool,
# }
```

这个字典可用于按名称查找和实例化工具类。

## 扩展练习

1. **自定义搜索引擎**：创建一个使用 Google/Bing API 的搜索工具替换 DuckDuckGo，需要 API Key。

2. **添加维基百科搜索**：显式添加 `WikipediaSearchTool`，对比网页搜索和百科搜索的结果差异。

3. **深度研究 Agent**：设置 `max_steps=15`，让 Agent 访问多个网页并进行交叉验证：
   ```python
   result = agent.run(
       "研究量子计算的最新进展，至少访问3个不同来源的网页，"
       "对比不同来源的信息后给出综合回答。"
   )
   ```

4. **内容过滤工具**：创建一个自定义工具，对 `visit_webpage` 返回的长内容进行截断或摘要。

5. **搜索结果结构化**：结合 CodeAgent，让 Agent 将搜索结果整理成 JSON/CSV 格式保存：
   ```python
   agent = CodeAgent(
       tools=[DuckDuckGoSearchTool()],
       model=model,
       additional_authorized_imports=["json"],
   )
   agent.run("搜索2026年AI大模型发布信息，整理成JSON格式保存到models.json")
   ```

6. **添加 step_callbacks 监控搜索过程**：
   ```python
   def log_step(step_result):
       if hasattr(step_result, 'tool_calls'):
           for tc in step_result.tool_calls:
               print(f"[Monitor] 调用工具: {tc.function.name}")
   agent = ToolCallingAgent(
       tools=[DuckDuckGoSearchTool()],
       model=model,
       step_callbacks=[log_step],
   )
   ```

## 相关链接

- [内置工具详解](../concepts/08-builtin-tools.md) — DuckDuckGoSearchTool、VisitWebpageTool 等内置工具的详细说明
- [工具系统概述](../concepts/07-tool-system.md) — 工具的注册、查找和调用机制
- [工具调用智能体](../concepts/05-tool-calling-agent.md) — Agent 如何选择工具并传递参数
- [Tools API 参考](../references/tools-api.md) — TOOL_MAPPING 和各工具类的完整定义
- [监控与日志](../concepts/13-monitoring-logging.md) — step_callbacks 和日志级别的使用
