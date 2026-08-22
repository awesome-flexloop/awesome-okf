---
okf_version: "0.2"
type: example
title: 构建顺序与并行工作流
description: 使用 SequentialAgent 和 ParallelAgent 组合多 Agent 协作工作流，通过 output_key 在子 Agent 间传递状态，实现管道式处理和并行分析后汇总的复杂任务编排
tags: [veadk-python, example, workflow, sequential-agent, parallel-agent, multi-agent, pipeline, orchestration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/composite-agents.md
  - /concepts/agent-and-runner.md
  - /concepts/memory-system.md
sources:
  - id: veadk-python-self
    resource: /references/veadk-python-sources.md
    title: veadk-python 源码参考
---

# 构建顺序与并行工作流

## 场景说明

本示例演示如何使用 VeADK 的组合 Agent（Composite Agents）构建多 Agent 协作工作流。VeADK 提供了三种核心组合模式：`SequentialAgent`（顺序执行，类似管道）、`ParallelAgent`（并行执行，类似扇出-扇入）和 `LoopAgent`（循环执行，直到满足条件）。子 Agent 之间通过 `output_key` 将结果写入共享会话状态，下游 Agent 通过 `{key_name}` 模板引用上游结果。这种模式让复杂任务可以拆分为多个专精 Agent 的协作，每个 Agent 专注单一职责。

**前置条件**：
- Python ≥ 3.10
- 已安装 veadk-python（`pip install veadk-python`）
- 拥有一个兼容 OpenAI Chat Completions API 的模型服务
- 理解 [Agent 与 Runner 概念](/concepts/agent-and-runner.md) 和 [组合 Agent 概念](/concepts/composite-agents.md)

## 完整代码示例

```python
"""
build-sequential-workflow.py
演示：使用 SequentialAgent 和 ParallelAgent 构建多 Agent 工作流
"""

import asyncio
import os

from veadk import Agent, Runner
from veadk.agents.sequential_agent import SequentialAgent
from veadk.agents.parallel_agent import ParallelAgent
from veadk.agents.loop_agent import LoopAgent
from veadk.memory.short_term_memory import ShortTermMemory


# ── 示例 1：简单顺序管道 ──
# 大纲 → 写作 → 编辑（经典三阶段内容生产）

def build_content_pipeline() -> SequentialAgent:
    """
    构建内容生产流水线：
    1. Outliner（大纲师）：生成大纲
    2. Writer（写手）：扩展为文章
    3. Editor（编辑）：润色定稿
    """
    outliner = Agent(
        name="outliner",
        instruction=(
            "你是一位专业的内容策划师。根据用户给出的主题，"
            "生成一个包含3-5个要点的结构化大纲。"
            "只输出大纲内容，用数字编号，不要写其他文字。"
        ),
        output_key="outline",  # 输出写入 session state 的 key
    )

    writer = Agent(
        name="writer",
        instruction=(
            "你是一位技术写作者。根据以下大纲，扩展为一篇"
            "200-300字的短文，语言流畅、逻辑清晰：\n\n{outline}"
            # {outline} 引用 outliner 的输出
        ),
        output_key="draft",
    )

    editor = Agent(
        name="editor",
        instruction=(
            "你是一位资深编辑。对以下草稿进行润色，确保语言精炼、"
            "没有错别字、表达专业。只返回最终润色后的文本，"
            "不要添加修改说明：\n\n{draft}"
        ),
        output_key="final_article",
    )

    return SequentialAgent(
        name="content_pipeline",
        description="内容生产流水线：大纲→写作→编辑",
        sub_agents=[outliner, writer, editor],
    )


# ── 示例 2：并行分析 + 顺序汇总 ──
# 收益分析 ∥ 风险分析 → 综合决策

def build_decision_pipeline() -> SequentialAgent:
    """
    构建决策分析工作流：
    1. 并行阶段：收益分析师 + 风险分析师（同时执行）
    2. 顺序阶段：综合决策师（基于并行结果给出建议）
    """
    benefits_analyst = Agent(
        name="benefits_analyst",
        instruction=(
            "你是一位商业分析师。针对用户提出的方案，"
            "分析三个最主要的收益点，每个收益点说明具体影响。"
            "用简洁的要点格式输出。"
        ),
        output_key="benefits",
    )

    risks_analyst = Agent(
        name="risks_analyst",
        instruction=(
            "你是一位风险管理专家。针对用户提出的方案，"
            "分析三个最重要的风险，每个风险给出一个可行的缓解措施。"
            "用简洁的要点格式输出。"
        ),
        output_key="risks",
    )

    # ParallelAgent：子 Agent 并行执行，共享 session state
    parallel_analysis = ParallelAgent(
        name="parallel_analysis",
        description="并行分析：收益 + 风险",
        sub_agents=[benefits_analyst, risks_analyst],
    )

    synthesizer = Agent(
        name="synthesizer",
        instruction=(
            "你是一位决策顾问。基于以下分析结果，给出一份简洁的决策简报，"
            "包含：推荐结论、核心权衡、下一步行动建议。\n\n"
            "【收益分析】\n{benefits}\n\n"
            "【风险分析】\n{risks}"
        ),
        output_key="decision_brief",
    )

    # SequentialAgent 可以嵌套 ParallelAgent
    return SequentialAgent(
        name="decision_pipeline",
        description="决策分析流水线：并行分析→综合建议",
        sub_agents=[parallel_analysis, synthesizer],
    )


# ── 示例 3：带评审的循环改进 ──
# 写作 → 评审 →（不达标则重写）→ 定稿

def build_iterative_pipeline() -> SequentialAgent:
    """
    构建迭代改进工作流：
    1. Writer（写手）：撰写文章
    2. Reviewer（评审）：评分并决定是否通过
    3. LoopAgent：如果评分 < 8 分，让 Writer 改进（最多3轮）
    """
    writer = Agent(
        name="writer",
        instruction=(
            "你是一位技术文档作者。根据用户的主题撰写一篇技术短文。"
            "如果之前有评审意见，请根据反馈改进你的文章。\n\n"
            "{review_feedback}"
        ),
        output_key="article",
    )

    reviewer = Agent(
        name="reviewer",
        instruction=(
            "你是一位严格的技术文档评审员。阅读以下文章，从准确性、"
            "清晰度、结构三个维度打分（每项1-10分），计算总分（满分30）。"
            "如果总分 >= 24，输出 'PASS:' 后跟最终文章。"
            "如果总分 < 24，输出 'REVISE:' 后跟具体的改进建议。\n\n"
            "文章：\n{article}"
        ),
        output_key="review_result",
    )

    # LoopAgent 循环执行 sub_agents，直到满足条件或达到最大迭代次数
    write_review_loop = LoopAgent(
        name="write_review_loop",
        sub_agents=[writer, reviewer],
        max_iterations=3,          # 最多3轮迭代（防止无限循环）
        # exit_condition 可选：自定义退出条件函数
        # 默认检查最后一个 Agent 的输出是否包含 "PASS:"
    )

    finalizer = Agent(
        name="finalizer",
        instruction=(
            "从以下评审结果中提取最终通过的文章内容"
            "（去掉 PASS: 标记和评分信息）：\n\n{review_result}"
        ),
        output_key="final_article",
    )

    return SequentialAgent(
        name="iterative_pipeline",
        description="迭代写作流水线：写作→评审→循环改进→定稿",
        sub_agents=[write_review_loop, finalizer],
    )


# ── 示例 4：多阶段研发流程 ──
# 需求分析 → (前端设计 ∥ 后端设计) → 技术方案汇总

def build_dev_planning_pipeline() -> SequentialAgent:
    """
    构建研发规划工作流（更复杂的嵌套示例）：
    1. 需求分析师：分析用户需求
    2. 并行：前端设计师 + 后端架构师
    3. 技术负责人：汇总技术方案
    """
    req_analyst = Agent(
        name="requirements_analyst",
        instruction=(
            "你是一位需求分析师。将用户的需求描述转化为结构化的需求说明，"
            "包含：功能需求列表、非功能需求、用户角色。"
            "用清晰的要点格式输出。"
        ),
        output_key="requirements",
    )

    frontend_designer = Agent(
        name="frontend_designer",
        instruction=(
            "你是一位前端工程师。基于以下需求，给出前端技术方案："
            "技术选型、组件架构、状态管理、关键交互设计。\n\n{requirements}"
        ),
        output_key="frontend_plan",
    )

    backend_architect = Agent(
        name="backend_architect",
        instruction=(
            "你是一位后端架构师。基于以下需求，给出后端技术方案："
            "技术选型、API设计、数据模型、关键技术难点。\n\n{requirements}"
        ),
        output_key="backend_plan",
    )

    parallel_design = ParallelAgent(
        name="parallel_design",
        description="前后端并行设计",
        sub_agents=[frontend_designer, backend_architect],
    )

    tech_lead = Agent(
        name="tech_lead",
        instruction=(
            "你是一位技术负责人。综合前后端方案，输出完整的技术方案文档，"
            "包含：概述、技术栈、架构设计、接口约定、部署方案、风险点。\n\n"
            "【需求】\n{requirements}\n\n"
            "【前端方案】\n{frontend_plan}\n\n"
            "【后端方案】\n{backend_plan}"
        ),
        output_key="tech_spec",
    )

    return SequentialAgent(
        name="dev_planning_pipeline",
        description="研发规划流水线：需求→并行设计→方案汇总",
        sub_agents=[req_analyst, parallel_design, tech_lead],
    )


# ── 运行演示 ──

async def run_pipeline_demo(pipeline, user_message: str, session_id: str, label: str):
    """运行一个工作流并打印结果。"""
    # 组合 Agent 不自带记忆，需要显式传入 ShortTermMemory
    runner = Runner(
        agent=pipeline,
        short_term_memory=ShortTermMemory(),
        app_name="workflow_demo",
    )

    print(f"\n{'='*60}")
    print(f"📋 {label}")
    print(f"{'='*60}")
    print(f"输入: {user_message}\n")
    print(f"🤖 Agent 工作中...\n")

    result = await runner.run(
        messages=user_message,
        session_id=session_id,
    )

    print(f"📤 最终输出:\n{result}\n")
    return result


async def main():
    print("=== VeADK 多 Agent 工作流示例 ===\n")
    print("组合模式：SequentialAgent（顺序）+ ParallelAgent（并行）+ LoopAgent（循环）")
    print("状态传递：通过 output_key 写入共享状态，通过 {key} 在指令中引用\n")

    # 示例 1：内容生产流水线
    pipeline1 = build_content_pipeline()
    await run_pipeline_demo(
        pipeline1,
        user_message="主题：为什么代码审查（Code Review）对团队很重要？",
        session_id="content-demo",
        label="示例1：内容生产流水线（大纲→写作→编辑）",
    )

    # 示例 2：决策分析流水线
    pipeline2 = build_decision_pipeline()
    await run_pipeline_demo(
        pipeline2,
        user_message="我们团队应该从 Python 3.11 升级到 Python 3.14（自由线程版本）吗？",
        session_id="decision-demo",
        label="示例2：决策分析流水线（并行分析→综合建议）",
    )

    # 示例 3：迭代写作流水线（较慢，可选运行）
    # pipeline3 = build_iterative_pipeline()
    # await run_pipeline_demo(
    #     pipeline3,
    #     user_message="写一篇介绍 asyncio 异步编程的短文",
    #     session_id="iterative-demo",
    #     label="示例3：迭代写作流水线（写作→评审→循环改进）",
    # )

    # 示例 4：研发规划流水线
    pipeline4 = build_dev_planning_pipeline()
    await run_pipeline_demo(
        pipeline4,
        user_message="我要做一个团队内部的 URL 短链服务，支持自定义短码和访问统计。",
        session_id="dev-plan-demo",
        label="示例4：研发规划流水线（需求→前后端并行设计→方案汇总）",
    )

    print("=== 所有示例完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
```

## 逐步解释

### 组合 Agent 类型

VeADK 提供三种组合模式：

| 类型 | 类名 | 行为 | 适用场景 |
|------|------|------|---------|
| 顺序 | `SequentialAgent` | 子 Agent 按列表顺序依次执行 | 管道式处理、多阶段加工 |
| 并行 | `ParallelAgent` | 子 Agent 同时执行 | 独立分析、扇出-扇入模式 |
| 循环 | `LoopAgent` | 循环执行子 Agent 直到条件满足 | 迭代改进、自我修正 |

### output_key 状态传递机制

每个 Agent 可以设置 `output_key`：
- Agent 执行完成后，其输出文本写入共享会话状态的该 key 下
- 下游 Agent 在 `instruction` 中使用 `{key_name}` 模板引用上游输出
- 模板在 Agent 运行前自动替换为对应值
- 未设置 `output_key` 的 Agent 输出不被存储（但仍在对话历史中可见）

### SequentialAgent 详解

```python
SequentialAgent(
    name="pipeline_name",
    description="描述文本",
    sub_agents=[agent1, agent2, agent3],  # 按顺序执行
)
```
- 子 Agent 按列表顺序逐个执行
- 每个子 Agent 可以看到前面所有 Agent 的 output_key 结果
- 适合：流水线处理、多步转换、需要顺序依赖的任务
- 最后一个子 Agent 的输出作为整个 SequentialAgent 的输出

### ParallelAgent 详解

```python
ParallelAgent(
    name="parallel_name",
    description="描述文本",
    sub_agents=[agentA, agentB],  # 并行执行
)
```
- 所有子 Agent 同时开始执行
- 每个子 Agent 只能看到 ParallelAgent 之前阶段的状态（不能互相看到对方的输出）
- 所有子 Agent 完成后才继续后续阶段
- 适合：独立维度分析、多视角评审、可并行的独立任务

### LoopAgent 详解

```python
LoopAgent(
    name="loop_name",
    sub_agents=[writer, reviewer],  # 循环体
    max_iterations=3,                # 最大迭代次数（防无限循环）
)
```
- 反复执行 sub_agents 列表
- 默认退出条件：最后一个 Agent 的输出包含 "PASS:"
- 可自定义 `exit_condition` 函数
- `max_iterations` 是安全兜底，防止死循环
- 适合：迭代改进、自我评审修正

### 嵌套组合

组合 Agent 可以任意嵌套：
- SequentialAgent 包含 ParallelAgent（示例2、4）
- SequentialAgent 包含 LoopAgent（示例3）
- ParallelAgent 的子 Agent 可以是 SequentialAgent
- 嵌套深度没有硬性限制，但建议不超过 4 层以免调试困难

### 记忆要求

组合 Agent（Sequential/Parallel/Loop）不自带记忆模块，创建 Runner 时必须显式传入 `ShortTermMemory()`：
```python
runner = Runner(
    agent=pipeline,
    short_term_memory=ShortTermMemory(),  # 组合 Agent 必须显式传入
    app_name="my_app",
)
```
这是因为组合 Agent 管理多个子 Agent，需要外部提供会话存储来维护共享状态。

## 输出结果

运行脚本后，预期输出类似：

```
=== VeADK 多 Agent 工作流示例 ===

============================================================
📋 示例1：内容生产流水线（大纲→写作→编辑）
============================================================
输入: 主题：为什么代码审查（Code Review）对团队很重要？

🤖 Agent 工作中...

📤 最终输出:
代码审查是软件工程中不可或缺的质量保障实践。首先，它能有效发现代码中的缺陷和潜在问题，在代码合入主线之前拦截Bug，降低线上故障风险...

============================================================
📋 示例2：决策分析流水线（并行分析→综合建议）
============================================================
输入: 我们团队应该从 Python 3.11 升级到 Python 3.14（自由线程版本）吗？

🤖 Agent 工作中...

📤 最终输出:
【推荐结论】建议暂缓升级到 Python 3.14 自由线程版本...
【核心权衡】性能提升 vs 生态兼容性风险...
【下一步建议】在非核心服务上先行试点，评估第三方库兼容性...
```

## 注意事项

1. **必须传入 ShortTermMemory**：组合 Agent 没有默认记忆，使用 Runner 时必须显式传入 `short_term_memory=ShortTermMemory()`，否则会报错。

2. **output_key 命名唯一性**：同一工作流中各 Agent 的 `output_key` 不能重复。如果下游 Agent 的 output_key 与上游同名，会覆盖上游值，导致模板引用出错。

3. **并行 Agent 的状态隔离**：ParallelAgent 的子 Agent 之间不共享运行时状态。它们只能看到 ParallelAgent 执行之前的 session state，不能互相读取对方的 output_key。

4. **循环迭代成本**：LoopAgent 每轮迭代都会产生 LLM 调用成本。`max_iterations` 务必设置合理值（建议 3-5），避免因退出条件不满足导致大量 Token 消耗。

5. **指令中的模板语法**：引用 output_key 使用 `{key_name}`（单花括号），不是 Jinja2 的 `{{ key_name }}`。模板替换是简单的字符串替换，确保 key 名正确。

6. **错误传播**：子 Agent 执行失败（如模型调用超时）会导致整个组合 Agent 失败。建议对关键子 Agent 设置模型 fallback（通过 `model_name` 列表）。

7. **调试技巧**：开发工作流时，可以单独测试每个子 Agent（用单 Agent + Runner），确认每个环节的输出符合预期后再组装。

8. **避免过深嵌套**：虽然组合 Agent 支持任意嵌套，但过深的嵌套会导致：① 调试困难（难以定位哪个子 Agent 出问题）；② Token 消耗增加（每个 Agent 的指令都占用上下文）；③ 延迟累积。建议扁平化设计，必要时将子工作流封装为独立 Agent。
