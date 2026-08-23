---
type: example
scope: deepagents
name: lca-variant
version: "0.7.8"
source: https://github.com/langchain-ai/lca-deepagents
description: lca-deepagents 教学变体示例——Chinook Sales Assistant 综合展示子代理、技能、内存、MCP 与人工审批
---

# lca-deepagents 教学变体示例

本示例来自 [LangChain Academy](https://academy.langchain.com/) 课程 "Foundation: Introduction to Deep Agents" 的模块5综合项目 **Chinook Sales Assistant**。它综合展示了 deepagents 的多个核心特性如何协同工作。

## 项目背景

Chinook 是一个在线音乐分销商。代理扮演销售支持人员 Jane Peacock 的助手，帮助她处理客户报价请求、更新客户记录、研究市场和生成区域报告。代理协调多个专业子代理，但 Jane 保留决策权。

## 架构概览

```
                    ┌─────────────────────┐
                    │   Main Agent        │
                    │   (Sales Assistant) │
                    │   skills + memory   │
                    └──────────┬──────────┘
                               │ task tool
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ chinook-analyst │ │ inbox-manager   │ │ quote-reviewer  │
│ (database)      │ │ (email/MCP)     │ │ (validation)    │
│ HITL: add_cust  │ │ HITL: save_draft│ │ no tools        │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          ▲
          │ (when Tavily enabled)
┌─────────────────┐
│ genre-researcher│
│ (web search)    │
└─────────────────┘
```

## 主代理配置

源码：`python/m5/sales_assistant/agent.py`

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_quickjs import CodeInterpreterMiddleware
from subagents import build_subagents
from tools.chart import render_pie_chart
from tools.html import markdown_to_html

_backend = FilesystemBackend(root_dir=str(HERE), virtual_mode=True)

async def make_graph():
    client = MultiServerMCPClient({"mock-mail": MAIL_SERVER})
    mail_tools = await client.get_tools()
    return create_deep_agent(
        model=strong_model,
        tools=[markdown_to_html, render_pie_chart] + mail_tools,
        system_prompt=SYSTEM_PROMPT,
        subagents=build_subagents(_backend, enable_search=_enable_search, mail_tools=mail_tools),
        skills=["/skills"],
        memory=["/AGENTS.md"],
        backend=_backend,
        middleware=[CodeInterpreterMiddleware()],
        name="chinook-sales-assistant",
    ).with_config({"recursion_limit": 50})
```

### 关键配置点

1. **文件系统后端**：`FilesystemBackend(root_dir=str(HERE), virtual_mode=True)` 将项目目录作为虚拟文件系统，代理读写的文件都限定在此目录内
2. **技能**：`skills=["/skills"]` 从后端的 `/skills` 目录加载可复用工作流（如 RFQ 报价、区域报告、每周新闻稿）
3. **内存**：`memory=["/AGENTS.md"]` 加载操作手册，包含代理的角色定义、专家列表、审批规则和内部规则
4. **MCP 集成**：通过 `MultiServerMCPClient` 连接模拟邮件服务器，获取邮件工具
5. **代码解释器**：`CodeInterpreterMiddleware()` 提供精确算术（报价金额必须准确，不能目测）
6. **递归限制**：设置为50（默认9999），适合教学环境

## 子代理设计

源码：`python/m5/sales_assistant/subagents.py`

### chinook-analyst（数据库专家）

```python
ANALYST_PROMPT = """You are the chinook-analyst, the data specialist...
You are the only agent that touches the database.
...use `add_customer` only when asked to add a genuinely new customer
(a human approves that write)."""
```

- 唯一拥有 SQL 工具（`query_chinook`、`introspect_schema`、`add_customer`）的代理
- 自动将数据库 schema 引导到自己的内存中
- `add_customer` 写入操作通过 `interrupt_on` 配置人工审批

### inbox-manager（邮件专家）

```python
INBOX_PROMPT = """You are the inbox-manager, the email specialist...
You own Jane's inbox and are the only agent that touches it.
- `mail_create_draft` — save a reply to the drafts folder. It NEVER sends.
...
Saving a draft pauses automatically for Jane to approve, edit, or reject."""
```

- 唯一拥有邮件 MCP 工具的代理
- `mail_create_draft` 保存草稿时自动暂停等待人工审批
- 明确告知代理没有发送工具，只能创建草稿

### quote-reviewer（报价审核者）

```python
REVIEWER_PROMPT = """You are the quote-reviewer. You receive a drafted quote...
Verify:
- The arithmetic: quantity x unit price for each line, and the grand total.
- Internal consistency...
- Plausibility...
Reply concisely: either "Looks correct" or a short list of corrections."""
```

- 无工具代理，纯 LLM 验证
- 检查算术、一致性和合理性
- 返回简洁的审核结果

### genre-researcher（流派研究员）

- 仅当 `TAVILY_API_KEY` 配置时存在
- 为每周新闻稿研究音乐流派
- 支持并行扇出（多个研究员同时工作）

## 安全设计：审批门控隔离

该示例最重要的架构教训是**工具放置策略**：

> 受审批控制的工具（`mail_create_draft`、`add_customer`）仅放在有门控的专业子代理上，绝不放在主代理上。

原因：通用子代理（`general-purpose`）继承主代理的工具集。如果主代理有 `add_customer`，模型可以：

1. 主代理调用 `task`，委派给 `general-purpose`
2. `general-purpose` 继承了 `add_customer` 工具
3. `general-purpose` 直接调用 `add_customer`，绕过主代理的审批门控

通过将敏感工具仅放在配置了 `interrupt_on` 的专业子代理上，确保访问这些工具的唯一路径经过审批。

## AGENTS.md 操作手册

`AGENTS.md` 文件通过 `memory=["/AGENTS.md"]` 加载，包含：

- **角色定义**：Jane Peacock 的销售助手，服务 Employee 3 的客户
- **专家列表**：四个专业子代理及其职责
- **审批规则**：保存邮件草稿和添加新客户需要 Jane 批准
- **内部规则**：
  - 报价金额必须精确（使用代码解释器）
  - 价格从 chinook-analyst 获取，不能编造
  - 成品写入 `/outputs/`，新闻稿使用日期文件名
  - Gmail 不可用时直接说明

## 技能目录

```
skills/
├── rfq-quote/SKILL.md       # RFQ 报价流程
├── territory-report/SKILL.md # 区域报告生成
└── weekly-newsletter/SKILL.md # 每周新闻稿
```

每个技能通过 YAML frontmatter 定义名称和描述，代理根据任务类型按需加载。

## 沙箱异步变体

`python/m5/sales_assistant_sandbox/` 目录包含同一项目的沙箱异步版本，增加了：

- `async_research.py`：异步研究代理
- `newsletter_agent_graph.py`：新闻稿代理图
- `start.sh` / `stop_sandboxes.sh`：沙箱生命周期管理脚本
- `langgraph_sandbox.json`：沙箱配置

这展示了 deepagents 从同步到异步、从本地到沙箱部署的演进路径。

## 课程模块与概念映射

| 模块 | 文件示例 | 演示的 deepagents 特性 |
|---|---|---|
| m1 | `m1.2_scratch_agent.py` | 基础 `create_deep_agent` 调用 |
| m1 | `m1.5_scratch_agent_tools.py` | 自定义工具 |
| m1 | `m1.6_agent_mcp.py` | MCP 集成 |
| m1 | `m1.8_hitl.py` | 人工在环 |
| m2 | `m2.3_sandbox_agent.py` | 沙箱后端 |
| m2 | `m2.4_interpreter_agent.py` | 代码解释器 |
| m3 | `m3.2_scratch_agent_skills.py` | 技能系统 |
| m3 | `m3.3_memory_agent.py` | 内存系统 |
| m4 | `m5/async_lab/` | 异步子代理 |
| m5 | `sales_assistant/` | 全部特性综合 |

## 环境配置

```bash
# 克隆仓库
git clone --depth 1 https://github.com/langchain-ai/lca-deepagents.git
cd lca-deepagents/python

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 ANTHROPIC_API_KEY 和 LANGSMITH_API_KEY

# 安装依赖
uv sync

# 运行 Sales Assistant
cd m5/sales_assistant
./start.sh
```

要求 Python 3.11–3.14，使用 `uv` 管理依赖。

## 相关参考

- [lca-deepagents 变体说明](/langchain-ai/deepagents/references/lca-variant) — 仓库结构与课程模块映射
- [规划与子代理](/langchain-ai/deepagents/concepts/planning-subagents) — 子代理安全模式详解
- [Todo 与上下文管理](/langchain-ai/deepagents/concepts/todo-context) — 技能和内存机制
- [后端系统](/langchain-ai/deepagents/references/backends) — FilesystemBackend 配置
