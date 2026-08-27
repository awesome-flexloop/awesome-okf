---
type: Example
title: 使用规划间隔实现 Plan-and-Execute
description: 设置planning_interval启用规划-执行模式，让Agent先制定计划再执行
tags: [规划, Plan-and-Execute, 高级]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: agents-source
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: memory-source
    resource: /references/memory-api.md
    title: Memory API 参考
---

# 使用规划间隔实现 Plan-and-Execute

## 概述

本示例演示如何通过 `planning_interval` 参数启用 Plan-and-Execute（规划-执行）模式。在普通 ReAct 模式下，Agent 每一步都只考虑当前情况；而在规划模式下，Agent 会每隔 N 步停下来重新审视任务，制定或更新执行计划，然后按照计划继续执行。这对于需要多步骤协调的复杂任务非常有效。

这个示例解决的核心问题：**如何让 Agent 在处理复杂多步任务时不跑偏，始终朝着最终目标前进**。

## 前置条件

- Python 3.10+
- 安装 codified-smolagents：`pip install codified-smolagents`
- Hugging Face API Token（环境变量 `HF_TOKEN`）
- 可选：搜索依赖 `pip install duckduckgo-search requests markdownify`（用于联网规划示例）

## 完整代码

```python
"""
示例 06: 使用规划间隔实现 Plan-and-Execute
演示：planning_interval 参数 → 观察 PlanningStep → 复杂任务规划效果 → summary_mode → provide_run_summary
"""

import os
from codified_smolagents import (
    ToolCallingAgent,
    CodeAgent,
    HfApiModel,
    DuckDuckGoSearchTool,
)
from codified_smolagents.monitoring import LogLevel
from codified_smolagents.memory import PlanningStep, ActionStep, TaskStep

# ============================================================
# 第一步：理解 planning_interval 参数
# ============================================================
print("=" * 60)
print("📋 planning_interval 参数说明")
print("=" * 60)
print("""
  planning_interval: 每隔多少步执行一次规划
    - None（默认）: 不启用规划，纯 ReAct 模式
    - N (整数): 每执行 N 步行动后，插入一个 PlanningStep
                Agent 会回顾已完成的工作，更新事实和计划

  工作流程（planning_interval=3）：
    Step 0: TaskStep（接收任务）
    Step 1: PlanningStep（初始规划：收集事实 + 制定计划）
    Step 2: ActionStep（执行计划第1步）
    Step 3: ActionStep（执行计划第2步）
    Step 4: ActionStep（执行计划第3步）
    Step 5: PlanningStep（更新规划：更新事实 + 更新计划）
    Step 6: ActionStep（继续执行）
    ...
    直到 FinalAnswerStep（给出最终答案）
""")

model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")

# ============================================================
# 第二步：启用 planning_interval=3 并观察 PlanningStep
# ============================================================
print("=" * 60)
print("🧪 测试: planning_interval=3 的执行过程")
print("=" * 60)

agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=["math", "statistics"],
    planning_interval=3,   # 每3步进行一次规划/重新规划
    max_steps=12,
    verbosity_level=LogLevel.INFO,
)

# 一个需要多步骤完成的复杂任务
complex_task = """
请完成以下数据分析任务：
1. 生成 50 个 1 到 100 之间的随机整数（随机种子用 42）
2. 计算这些数的均值、中位数、标准差
3. 统计其中的素数个数
4. 将这些数从小到大排序，找出第25百分位数和第75百分位数
5. 最终输出一个格式整齐的分析报告
"""

result = agent.run(complex_task)
print(f"\n✅ 最终结果:\n{result}")

# ============================================================
# 第三步：观察 PlanningStep 在 memory 中的位置
# ============================================================
print("\n" + "=" * 60)
print("🔍 分析 memory.steps 中的步骤类型")
print("=" * 60)

for i, step in enumerate(agent.memory.steps):
    step_type = type(step).__name__
    if isinstance(step, PlanningStep):
        print(f"\n📋 Step {i}: PlanningStep（规划步骤）")
        print(f"   计划内容 (plan): {step.plan[:200]}...")
    elif isinstance(step, TaskStep):
        print(f"\n📝 Step {i}: TaskStep（任务步骤）")
        print(f"   任务: {step.task[:100]}...")
    elif isinstance(step, ActionStep):
        print(f"\n⚡ Step {i}: ActionStep（行动步骤）")
        if step.error:
            print(f"   ⚠️ 错误: {step.error}")
        elif step.observations:
            obs_preview = str(step.observations)[:100]
            print(f"   观察结果: {obs_preview}...")
    else:
        print(f"\n🏁 Step {i}: {step_type}")


# ============================================================
# 第四步：对比启用/不启用规划的效果
# ============================================================
print("\n" + "=" * 60)
print("⚖️ 对比: 有规划 vs 无规划")
print("=" * 60)

research_task = """
帮我研究一下 Python 3.13 相比 3.12 版本的主要新特性：
- 列出至少3个性能改进
- 列出至少2个新的语法特性
- 列出任何重要的弃用或破坏性变更
- 最后给出是否建议升级的结论
"""

# 无规划模式
print("\n❌ 无规划模式 (planning_interval=None):")
agent_no_plan = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    planning_interval=None,
    max_steps=8,
    verbosity_level=LogLevel.OFF,
)
try:
    result_no_plan = agent_no_plan.run(research_task)
    steps_no_plan = len([s for s in agent_no_plan.memory.steps if isinstance(s, ActionStep)])
    print(f"  执行行动步数: {steps_no_plan}")
    print(f"  结果(前200字): {result_no_plan[:200]}...")
except Exception as e:
    print(f"  执行异常: {e}")

# 有规划模式
print("\n✅ 有规划模式 (planning_interval=3):")
agent_with_plan = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    planning_interval=3,
    max_steps=10,
    verbosity_level=LogLevel.OFF,
)
try:
    result_with_plan = agent_with_plan.run(research_task)
    steps_with_plan = len([s for s in agent_with_plan.memory.steps if isinstance(s, ActionStep)])
    planning_steps = len([s for s in agent_with_plan.memory.steps if isinstance(s, PlanningStep)])
    print(f"  执行行动步数: {steps_with_plan}")
    print(f"  规划步数: {planning_steps}")
    print(f"  结果(前200字): {result_with_plan[:200]}...")
except Exception as e:
    print(f"  执行异常: {e}")

print("""
💡 观察要点：
  - 启用规划后，Agent 会在开始时制定明确计划，减少盲目搜索
  - 定期重新规划帮助 Agent 修正方向，避免在错误路径上浪费步数
  - 规划会占用额外的 LLM 调用（每个 PlanningStep 都要调用一次模型）
  - 简单任务不需要规划，复杂多步骤任务规划效果明显
""")


# ============================================================
# 第五步：summary_mode 对消息输出的影响
# ============================================================
print("\n" + "=" * 60)
print("📝 summary_mode 摘要模式")
print("=" * 60)

# write_memory_to_messages 方法可以以摘要模式输出消息
agent_summary = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=["math"],
    planning_interval=2,
    max_steps=4,
    verbosity_level=LogLevel.OFF,
)
_ = agent_summary.run("计算1到100中所有能被3整除但不能被5整除的数的和。")

# 普通模式：包含所有步骤的完整信息
messages_full = agent_summary.write_memory_to_messages(summary_mode=False)
print(f"\n📄 普通模式消息数: {len(messages_full)}")
total_chars_full = sum(len(str(m.get('content', ''))) for m in messages_full)
print(f"   总字符数: {total_chars_full}")

# 摘要模式：精简输出，SystemPromptStep 和 PlanningStep 返回空列表
messages_summary = agent_summary.write_memory_to_messages(summary_mode=True)
print(f"📄 摘要模式消息数: {len(messages_summary)}")
total_chars_summary = sum(len(str(m.get('content', ''))) for m in messages_summary)
print(f"   总字符数: {total_chars_summary}")
print(f"   压缩率: {(1 - total_chars_summary/total_chars_full)*100:.1f}%")

print("""
📖 summary_mode 效果：
  - SystemPromptStep: 摘要模式返回空列表（不发送系统提示词）
  - PlanningStep: 摘要模式返回空列表（不发送计划内容）
  - ActionStep: 保留核心内容但精简
  用途：在长对话中减少token消耗，或在提供运行摘要时使用
""")


# ============================================================
# 第六步：provide_run_summary 获取执行摘要
# ============================================================
print("\n" + "=" * 60)
print("📊 provide_run_summary 运行摘要")
print("=" * 60)

# provide_run_summary 参数用于被管理智能体（managed agent）
# 当子 Agent 被主 Agent 调用完成后，如果 provide_run_summary=True
# 会在返回结果中追加执行摘要信息

# 这里演示如何通过 replay() 方法获取可读的执行回放
agent_for_replay = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=["math"],
    planning_interval=2,
    max_steps=4,
    verbosity_level=LogLevel.OFF,
)
_ = agent_for_replay.run("计算圆半径为7的面积和球体体积。")

# 使用 memory.get_succinct_steps() 获取精简步骤
succinct_steps = agent_for_replay.memory.get_succinct_steps()
print(f"\n📋 精简步骤数: {len(succinct_steps)}")
for i, step in enumerate(succinct_steps):
    # 精简步骤排除了 model_input_messages
    step_keys = [k for k in step.keys() if step[k] is not None]
    print(f"  Step {i}: 类型={step.get('type', 'unknown')}, 字段={step_keys}")

# 使用 replay() 方法美观地打印执行过程
print("\n🎬 执行回放（detailed=False）:")
agent_for_replay.replay(detailed=False)

# 获取完整步骤（包含 model_input_messages）
full_steps = agent_for_replay.memory.get_full_steps()
print(f"\n📚 完整步骤数: {len(full_steps)} (包含模型输入消息)")


# ============================================================
# 第七步：实践建议
# ============================================================
print("\n" + "=" * 60)
print("💡 规划间隔使用建议")
print("=" * 60)
print("""
  ┌─────────────────────────────────────────────────────────┐
  │  任务类型               │  推荐 planning_interval      │
  ├─────────────────────────────────────────────────────────┤
  │  简单问答               │  None（不启用）              │
  │  单步计算               │  None                        │
  │  2-4步的多步任务        │  2-3                         │
  │  复杂研究/写作任务      │  3-5                         │
  │  超长多源调研任务       │  4-6                         │
  │  代码生成与调试         │  3-4                         │
  └─────────────────────────────────────────────────────────┘

  注意事项：
  1. 每次规划都要额外调用一次 LLM，增加成本和延迟
  2. 规划间隔太小（如1）会导致频繁规划，效率低下
  3. 规划间隔太大（如10）则失去规划的指导意义
  4. 建议先用 verbosity_level=DEBUG 观察规划质量再调参
""")
```

## 运行说明

1. 确保 `HF_TOKEN` 环境变量已设置。
2. 安装可选搜索依赖：`pip install duckduckgo-search requests markdownify`
3. 将代码保存为 `06_planning_interval.py`。
4. 运行：`python 06_planning_interval.py`

**预期输出**：
```
============================================================
📋 planning_interval 参数说明
============================================================
  planning_interval: 每隔多少步执行一次规划
    - None（默认）: 不启用规划，纯 ReAct 模式
    - N (整数): 每执行 N 步行动后，插入一个 PlanningStep
...

============================================================
🧪 测试: planning_interval=3 的执行过程
============================================================
━━━ Planning Step ━━━
Initial facts:
- 用户需要完成一个多步骤数据分析任务
...
Initial plan:
1. 首先生成随机数据
2. 计算描述性统计量
...

============================================================
🔍 分析 memory.steps 中的步骤类型
============================================================

📝 Step 0: TaskStep（任务步骤）

📋 Step 1: PlanningStep（规划步骤）
   计划内容 (plan): Initial plan:
1. 生成随机数...

⚡ Step 2: ActionStep（行动步骤）
...
```

## 代码解析

### 1. planning_interval 工作机制

```python
agent = CodeAgent(
    tools=[],
    model=model,
    planning_interval=3,  # 每3步执行一次规划
)
```

启用规划后，Agent 的执行循环变为：

```
TaskStep → [PlanningStep(初始)] → ActionStep × N → [PlanningStep(更新)] → ActionStep × N → ... → FinalAnswerStep
```

- **初始规划**（第一步）：Agent 先收集已知事实（`initial_facts`），然后制定初始计划（`initial_plan`）。
- **定期更新**（每 N 步后）：Agent 更新事实（`update_facts`）和计划（`update_plan`），根据执行中发现的新信息调整方向。

### 2. PlanningStep 结构

```python
@dataclass
class PlanningStep(MemoryStep):
    model_input_messages: List[Message]  # 规划时发给模型的消息
    model_output_message: ChatMessage    # 模型返回的规划响应
    plan: str                             # 生成的计划文本
```

- `plan` 字段存储 LLM 生成的计划文本，包含事实清单和执行步骤。
- 在 `to_messages()` 中，PlanningStep 输出两条消息：
  1. assistant 消息：计划内容（让后续步骤知道计划）
  2. user 消息："Now proceed and carry out this plan."（强制角色切换，防止模型继续输出计划）

### 3. PlanningPromptTemplate 六段式模板

规划提示词模板包含6个部分：

| 模板字段 | 用途 |
|---------|------|
| `initial_facts` | 首次规划时的事实收集提示 |
| `initial_plan` | 首次规划时的计划制定提示 |
| `update_facts_pre_messages` | 更新事实前的消息 |
| `update_facts_post_messages` | 更新事实后的消息 |
| `update_plan_pre_messages` | 更新计划前的消息 |
| `update_plan_post_messages` | 更新计划后的消息 |

### 4. summary_mode 的作用

```python
messages_full = agent.write_memory_to_messages(summary_mode=False)
messages_summary = agent.write_memory_to_messages(summary_mode=True)
```

| 步骤类型 | summary_mode=False | summary_mode=True |
|---------|-------------------|------------------|
| SystemPromptStep | 输出 system 消息 | 返回空列表 |
| PlanningStep | 输出计划+执行指令 | 返回空列表 |
| ActionStep | 完整输出（模型输出+工具调用+观察） | 精简输出 |
| TaskStep | 输出任务消息 | 输出任务消息 |

摘要模式主要用于：
- 被管理智能体（Managed Agent）向主 Agent 汇报时，提供精简的执行摘要
- 长对话中减少上下文 token 消耗

### 5. provide_run_summary 参数

```python
agent = ToolCallingAgent(
    tools=[...],
    model=model,
    name="search_expert",
    description="搜索专家",
    provide_run_summary=True,  # 作为子Agent被调用时提供执行摘要
)
```

当 `provide_run_summary=True` 时，Agent 作为被管理智能体（managed agent）被主 Agent 调用后，会在返回结果中追加运行摘要，包含执行了哪些步骤、使用了什么工具、遇到了什么问题等信息。这在多智能体协作中非常重要（参见示例 07）。

### 6. memory 中的步骤查看方法

```python
# 方法1：直接遍历 steps
for step in agent.memory.steps:
    if isinstance(step, PlanningStep):
        print(step.plan)

# 方法2：获取精简步骤（不含 model_input_messages）
succinct = agent.memory.get_succinct_steps()

# 方法3：获取完整步骤（含 model_input_messages）
full = agent.memory.get_full_steps()

# 方法4：美观回放
agent.replay(detailed=False)  # detailed=True 显示模型输入（更长）
```

## 扩展练习

1. **测试不同 planning_interval 值**：分别设置 1、2、3、5、None，对比同一任务的执行步数和结果质量。

2. **自定义规划模板**：通过 `prompt_templates` 参数传入自定义的 `PlanningPromptTemplate`，调整规划的详细程度和风格。

3. **结合 step_callbacks 监控规划**：
   ```python
   def on_step(step_result):
       if hasattr(step_result, 'plan'):
           print(f"[规划更新] {step_result.plan[:100]}")
   agent = ToolCallingAgent(
       tools=[...], model=model,
       planning_interval=3,
       step_callbacks=[on_step],
   )
   ```

4. **保存和加载 Agent**：使用 `agent.save("./my_planned_agent")` 将配置了规划的 Agent 保存到本地。

5. **对比 CodeAgent 和 ToolCallingAgent 的规划效果**：同样的任务和 planning_interval，观察两种 Agent 的规划差异——CodeAgent 倾向于规划代码编写步骤，ToolCallingAgent 倾向于规划工具调用步骤。

## 相关链接

- [多步智能体与 ReAct 循环](../concepts/03-multi-step-agent.md) — ReAct 循环和规划步骤的触发机制
- [内存系统](../concepts/04-memory-system.md) — PlanningStep、ActionStep 在内存中的组织方式
- [提示词模板](../concepts/12-prompt-templates.md) — PlanningPromptTemplate 的结构和自定义方法
- [高级特性](../concepts/14-advanced-features.md) — 规划与其他高级特性的组合使用
- [Agents API 参考](../references/agents-api.md) — planning_interval 和 provide_run_summary 参数说明
- [Memory API 参考](../references/memory-api.md) — PlanningStep 和 AgentMemory 的完整数据结构
