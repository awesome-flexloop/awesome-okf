---
type: concept
title: "API 与开发工具类 Skills 详解"
description: "claude-api/mcp-builder/skill-creator/webapp-testing 四个开发类 Skill 的用途、结构、编写规范与可复用模式，含 TRIGGER+SKIP 探测式 description 与双跑评估闭环。"
tags: [skills, claude-api, mcp, skill-creator, playwright, official-skills]
sources:
  - id: anthropic-skills-local
    resource: "external/libs/anthropics/skills"
    title: "Anthropic Skills 参考实现仓库（本地镜像）"
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-10-24" }
status: stable
stale_after: 2027-04-24
---

# API 与开发工具类 Skills 详解

覆盖 4 个 skill：`claude-api`、`mcp-builder`、`skill-creator`、`webapp-testing`。

这组 skill 是**面向开发者本身**的工具——它们不讲如何产出业务文档，而是讲如何调用 Claude API、如何搭 MCP server、如何造 skill、如何测 Web 应用。

---

## 一、claude-api —— 最大的单文件知识库

| 维度 | 内容 |
|------|------|
| **用途** | Claude API / Anthropic SDK 权威参考：模型 id、定价、参数、流式、工具调用、MCP、agents、缓存、token 计数、模型迁移 |
| **SKILL.md** | 616 行 / **105,762 字节**（19 个中单文件最大，F-061c） |
| **目录文件数** | 96 |
| **许可** | Apache-2.0 |

### 目录结构

```
claude-api/
├── SKILL.md            # 105KB 主体
├── LICENSE.txt
├── csharp/claude-api/     README, batches, files-api, streaming, tool-use
├── curl/                  examples.md, managed-agents.md   ← 🔺 无 claude-api/ 子目录
├── go/claude-api/         README, files-api, streaming, tool-use
├── go/managed-agents/     README
├── java/claude-api/       README, files-api, streaming, tool-use
├── java/managed-agents/   README
├── php/claude-api/        README, batches, files-api, streaming, tool-use
├── php/managed-agents/    README
├── python/claude-api/     README, batches, files-api, sdk-upgrade, streaming, tool-use
├── python/managed-agents/ README
├── ruby/claude-api/       README, streaming, tool-use
├── ruby/managed-agents/   README
├── typescript/claude-api/ README, batches, files-api, streaming, tool-use
├── typescript/managed-agents/ README
└── shared/
    ├── evals/             build-eval, cost-hillclimb, eval-audit, eval-hillclimb
    │   └── report/        SCHEMA.md, build-report-lite.mjs, runner-scaffold.mjs
    ├── managed-agents-quickstarts/   13 个场景 md
    └── preserved-thinking-migration/ causes.md, drop_block_probe.py, prefix_diff.py
```

🔺 **`curl/` 是结构例外**（F-061b）：其余 7 种语言都是 `<lang>/claude-api/` + 可选 `<lang>/managed-agents/`，只有 curl 直接平铺 `examples.md` 与 `managed-agents.md`。写按语言分发的脚本时必须特判。

### SKILL.md 章节全景

```
# Building LLM-Powered Applications with Claude
## Before You Start
## Output Requirement
## Defaults
## Warning: API Drift - Your Training Prior May Be Stale
## Subcommands
## Language Detection
### Language-Specific Feature Support
## Which Surface Should I Use?
### Building an Agent: Four Approaches
### Should I Build an Agent?
## Architecture
## Current Models (cached: 2026-10-06)
## Authentication (Quick Reference)
## Thinking & Effort (Quick Reference)
## Compaction (Quick Reference)
## Prompt Caching (Quick Reference)
## Fast Mode (Quick Reference)
## Task Budgets (Quick Reference)
## Provider Clients (Quick Reference)
   ### Amazon Bedrock / Microsoft Foundry / Google Cloud Vertex AI
## Context Editing (Quick Reference)
## Mid-Conversation System Messages (Quick Reference)
## Managed Agents (Beta)
## Server Tools (Quick Reference)
## Document & File Input (Quick Reference)
## Tool Use Patterns (Quick Reference)
## Other API Surfaces (Quick Reference)
## Workload Identity Federation (Quick Reference)
## Reading Guide
### Quick Task Reference
## When to Use WebFetch
## Common Pitfalls
```

### 🔴 编写规范要点

1. **模型表带缓存日期**——`## Current Models (cached: 2026-10-06)`。日期写在标题里，读者一眼知道信息新鲜度（F-066）。
2. **显式的漂移警告节**——`## Warning: API Drift - Your Training Prior May Be Stale` 独立成节，承认"模型的训练先验可能已过期"。
3. **默认模型写明**——`claude-opus-5-5` 为当前默认（F-066）。
4. **每个能力节都标 "(Quick Reference)"**——暗示这是速查而非教程，完整文档在 `<lang>/claude-api/`。
5. **`## When to Use WebFetch` + `## Common Pitfalls`** 收尾——把"什么时候该去查外部文档"和"常见错法"显式化。

### 🔴 最高级的 description 写法（F-022、F-089）

它是 19 个中**唯一**在 description 里内嵌可执行探测命令的：

```
SKIP only when another provider is being worked on (overrides all triggers):
OpenAI/GPT/Gemini/Llama/Mistral/Cohere/Ollama named in the query; OR
`grep -rE 'openai|langchain_openai|google.generativeai|genai|mistralai|cohere|ollama'`
over the project hits (run this grep FIRST if no provider named — don't Read the file).
```

三个设计要点：

| 要点 | 作用 |
|------|------|
| **SKIP 覆盖所有 TRIGGER** | 显式写 "overrides all triggers"——避免误触发 |
| **给出可执行命令** | 模型无需猜"是否用了别的 provider"，直接跑 grep |
| **规定执行时机** | "run this grep FIRST ... don't Read the file"——防止先读文件再判断 |

> 🟢 **可复用模式**：当一个 skill 会被**同类工具抢占**时，在 description 里放一段**可执行的排除探测**。这比写"仅当用户提到 X 时使用"有效得多——后者依赖模型语义判断，前者给模型一条确定的判定路径。

### shared/ 目录的三块

| 目录 | 内容 | 用途 |
|------|------|------|
| `managed-agents-quickstarts/` | **13** 个场景（F-063）：bug-hunter、contract-tracker、data-analyst、deep-researcher、explainer-video-maker、field-monitor、incident-commander、performance-tuner、sprint-retro-facilitator、structured-extractor、support-agent、support-to-eng-escalator、watchlist-scanner | Managed Agents 的即用场景范本 |
| `preserved-thinking-migration/` | `causes.md` + `drop_block_probe.py` + `prefix_diff.py` | 保留思考块的迁移诊断工具 |
| `evals/` | 4 篇 eval 方法论文 + `report/`（Schema + Node 构建脚本） | 成本爬坡与审计的评估方法 |

---

## 二、mcp-builder —— 四阶段 MCP 开发

| 维度 | 内容 |
|------|------|
| **用途** | 构建高质量 MCP server（Python FastMCP / Node MCP SDK），集成外部 API |
| **SKILL.md** | 236 行 |
| **资源** | `reference/`（4 篇）+ `scripts/`（2 py + xml + requirements.txt） |
| **许可** | Apache-2.0 |

### 四阶段流程（F-067）

```
# Process
## 🚀 High-Level Workflow
### Phase 1: Deep Research and Planning
### Phase 2: Implementation
### Phase 3: Review and Test
### Phase 4: Create Evaluations
```

### 🔴 核心亮点：reference 的加载时机标注（F-069）

`## 📚 Documentation Library` 段把 4 个 reference 文件按**加载阶段**分组：

| 标注 | 文件 |
|------|------|
| **Load First** | `mcp_best_practices.md` |
| **Load During Phase 1/2** | `python_mcp_server.md`、`node_mcp_server.md` |
| **Load During Phase 4** | `evaluation.md` |

这是 19 个 skill 中**唯一**完整做到这一点的。它直接决定了上下文成本——不给时机标注，模型会一次性全读 4 篇。

### scripts/

| 文件 | 职责 |
|------|------|
| `evaluation.py` | MCP 评估 harness——用 Claude 跑测试问题，检查工具是否被调用、步骤是否有 `<summary>` 包裹 |
| `connections.py` | 连接工厂（`create_connection`） |
| `example_evaluation.xml` | 评估结果示例 |
| `requirements.txt` | Python 依赖 |

`evaluation.py` 的提示词模板结构（实测）：

```python
EVALUATION_PROMPT = """You are an AI assistant with access to tools.

When given a task, you MUST:
1. Use the available tools to complete the task
2. Provide summary of each step in your approach, wrapped in <summary> tags
...
```

> 🟢 **可复用模式**：**用 XML 标签做输出结构约束**（`<summary>`）比自然语言指令更可靠——评估 harness 解析标签边界比解析散文确定得多。

---

## 三、skill-creator —— 元技能

| 维度 | 内容 |
|------|------|
| **用途** | 创建/修改/评估 skill，测量性能，优化 description |
| **SKILL.md** | 485 行（19 个中第二长） |
| **目录文件数** | 18 |
| **许可** | Apache-2.0（**但无 `license` frontmatter 字段**——F-019） |

### 目录结构

```
skill-creator/
├── SKILL.md
├── LICENSE.txt
├── agents/
│   ├── analyzer.md      # 事后归因（"unblids" 盲比结果）
│   ├── comparator.md    # 盲比（A/B 隐藏身份）
│   └── grader.md        # 评分（按 expectation 逐条判定）
├── assets/
│   └── eval_review.html # 报告样式资产
├── eval-viewer/
│   ├── generate_review.py
│   └── viewer.html      # 人工审阅对比结果
├── references/
│   └── schemas.md       # evals.json / grading.json / benchmark.json 三类 Schema
└── scripts/
    ├── __init__.py
    ├── aggregate_benchmark.py
    ├── generate_report.py
    ├── improve_description.py
    ├── package_skill.py
    ├── quick_validate.py
    ├── run_eval.py
    ├── run_loop.py
    └── utils.py         # parse_skill_md()
```

### 5 步创建流程

```
## Communicating with the user
## Creating a skill
### Capture Intent
### Interview and Research
### Write the SKILL.md
### Skill Writing Guide
```

### 🔴 评估闭环：双跑是最低成本的确证方式

```
## Running and evaluating test cases
### Step 1: Spawn all runs (with-skill AND baseline) in the same turn
### Step 2: While runs are in progress, draft assertions
### Step 3: As runs complete, capture timing data
### Step 4: Grade, aggregate, and launch the viewer
### What the user sees in the viewer
### Step 5: Read the feedback
```

四个关键设计：

| 设计 | 为什么重要 |
|------|-----------|
| **with-skill 与 baseline 同一批次发起** | 避免环境差异污染对比结果 |
| **运行期间并行起草断言** | 不浪费等待时间 |
| **盲比隐藏身份** | 消除位置偏好 |
| **事后归因（analyzer）** | 不只知"谁赢"，还知"为什么赢" |

> 🟢 **可复用模式**：任何"加了这个能力有没有用"的问题，答案只能是**对照组实测**。官方给出的最小实现就是双跑——不复杂，但比任何主观判断可靠。

### quick_validate.py 是格式的权威定义（F-013 ~ F-018）

```python
ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
```

它校验：name 格式/长度、description 长度与尖括号、compatibility 类型与长度。

🔴 **它不校验行数**（F-017）——`grep -n "500" quick_validate.py` 只命中 `len(compatibility) > 500`。

---

## 四、webapp-testing —— Playwright 测试

| 维度 | 内容 |
|------|------|
| **用途** | 用 Playwright 与本地 Web 应用交互——验证功能、调试 UI、抓浏览器截图与日志 |
| **SKILL.md** | 95 行 |
| **资源** | `scripts/with_server.py` + `examples/`（3 个 py） |
| **许可** | Apache-2.0 |

### 结构骨架

```
# Web Application Testing
## Decision Tree: Choosing Your Approach
## Example: Using with_server.py
## Reconnaissance-Then-Action Pattern
## Common Pitfall
## Best Practices
## Reference Files
```

### 🔴 with_server.py：环境编排器（F-070）

```
python scripts/with_server.py --server "npm run dev" --port 5173 -- python automation.py

python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python test.py
```

生命周期：`起服务 → 探端口就绪（`is_server_ready(port, timeout=30)` 轮询）→ 跑命令 → 清理`。

关键设计：`--server`/`--port` **可重复**以支持多服务，`--` 之后接要执行的命令。

### 三种示例（F-071）

| 示例 | 覆盖场景 |
|------|---------|
| `console_logging.py` | 捕获浏览器控制台输出 |
| `element_discovery.py` | 元素探测 |
| `static_html_automation.py` | 静态 HTML 自动化 |

### 🔴 核心模式：Reconnaissance-Then-Action

正文有独立小节讲这个模式——**先侦察（看清页面结构），再动作**。配套 `## Common Pitfall` 指出直接盲操的失败模式。

> 🟢 **可复用模式**：任何 UI 自动化场景都应先"侦察"再"动作"。直接凭想象点击 DOM 是最常见的失败源；先 dump 元素、截图，再基于真实结构操作。
>
> 加上 `with_server.py` 的编排器形状，这套组合可直接搬到任何"需要起服务再测"的栈（前端、爬虫、集成测试）。

---

## 五、四者横向对比

| skill | 核心资产 | 独有机制 | 可直接复用模式 |
|-------|---------|---------|--------------|
| claude-api | 105KB SKILL.md + 8 语言目录 + shared/ | TRIGGER+SKIP 探测式 description | 描述里的可执行排除探测 |
| mcp-builder | 四阶段流程 + 4 篇 reference | **reference 加载时机标注** | 分阶段加载策略 |
| skill-creator | 3 子代理 + 9 脚本 + eval-viewer | **双跑评估闭环** | with/without 对照组 |
| webapp-testing | with_server + 3 示例 | **侦察—动作分离** | 环境编排器形状 |

---

## 相关文档

- [Skill Creator工具详解](02-skill-creator.md) — 元技能完整流程
- [Claude API Skill详解](03-claude-api-skill.md) — API 用法与漂移警告
- [事实登记表](../references/facts.md) — F-061~F-077 实测
