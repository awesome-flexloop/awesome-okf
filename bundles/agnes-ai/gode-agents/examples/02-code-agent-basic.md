---
type: Example
title: 创建 CodeAgent 执行 Python 代码
description: 使用CodeAgent执行Python代码进行数学计算和数据分析
tags: [入门, CodeAgent, Python执行]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: agents-source
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: models-source
    resource: /references/models-api.md
    title: Models API 参考
  - id: executor-source
    resource: /references/executor-api.md
    title: Executor API 参考
---

# 创建 CodeAgent 执行 Python 代码

## 概述

本示例演示如何使用 `CodeAgent` 让 LLM 生成并执行 Python 代码来解决问题。与 `ToolCallingAgent` 通过 JSON 调用预定义工具不同，`CodeAgent` 直接编写 Python 代码在受控沙箱中运行，适合数学计算、数据分析、逻辑推理等任务。

这个示例解决的核心问题：**如何让 Agent 自主编写和执行 Python 代码来完成计算任务**。

## 前置条件

- Python 3.10+
- 安装 codified-smolagents：`pip install codified-smolagents`
- Hugging Face API Token（环境变量 `HF_TOKEN`）
- 可选：安装 numpy 和 pandas 用于数据处理示例
  ```bash
  pip install numpy pandas
  ```

## 完整代码

```python
"""
示例 02: 创建 CodeAgent 执行 Python 代码
演示：CodeAgent 基本用法 → 数学计算 → 授权 import → 对比 ToolCallingAgent
"""

from codified_smolagents import CodeAgent, HfApiModel, ToolCallingAgent
from codified_smolagents.monitoring import LogLevel

# ============================================================
# 第一步：创建模型实例
# ============================================================
model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")

# ============================================================
# 第二步：创建基础 CodeAgent（仅使用内置模块）
# ============================================================
# CodeAgent 不需要额外工具即可执行 Python 代码
# 它内置了 Python 执行器，可以运行 LLM 生成的代码
agent = CodeAgent(
    tools=[],                        # 可以为空，CodeAgent 自带代码执行能力
    model=model,
    additional_authorized_imports=None,  # 默认只允许基础 Python 模块
    executor_type="local",           # 使用本地 Python 执行器
    max_steps=5,
    verbosity_level=LogLevel.INFO,
)

# ============================================================
# 任务1：斐波那契数列计算
# ============================================================
print("=" * 60)
print("📊 任务1: 计算斐波那契数列前20项")
print("=" * 60)

result1 = agent.run(
    "请编写 Python 代码计算斐波那契数列的前20项，"
    "并输出每一项的值。最后计算前20项的总和。"
)
print(f"\n✅ 结果:\n{result1}")

# ============================================================
# 任务2：素数判断与筛选
# ============================================================
print("\n" + "=" * 60)
print("🔢 任务2: 找出100以内的所有素数")
print("=" * 60)

result2 = agent.run(
    "请编写 Python 代码找出100以内的所有素数（质数），"
    "并统计素数的个数。要求使用埃拉托斯特尼筛法。"
)
print(f"\n✅ 结果:\n{result2}")

# ============================================================
# 第三步：授权额外的 import（numpy / pandas）
# ============================================================
print("\n" + "=" * 60)
print("📈 任务3: 使用 numpy 和 pandas 进行数据分析")
print("=" * 60)

# 通过 additional_authorized_imports 授权第三方库
agent_with_libs = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=["numpy", "pandas"],  # 授权 numpy 和 pandas
    executor_type="local",
    max_steps=5,
    verbosity_level=LogLevel.INFO,
)

result3 = agent_with_libs.run(
    "使用 numpy 生成100个服从正态分布(均值=0, 标准差=1)的随机数，"
    "然后用 pandas 创建一个 DataFrame，计算这些随机数的均值、标准差、"
    "最小值、最大值和中位数，并以表格形式输出结果。"
    "请设置随机种子为42以保证结果可复现。"
)
print(f"\n✅ 结果:\n{result3}")

# ============================================================
# 第四步：理解代码执行流程
# ============================================================
print("\n" + "=" * 60)
print("🔍 观察 CodeAgent 的代码执行步骤")
print("=" * 60)

agent_debug = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=["math"],
    executor_type="local",
    max_steps=3,
    verbosity_level=LogLevel.DEBUG,  # DEBUG 级别可看到生成的代码
)

result4 = agent_debug.run(
    "计算半径为5的圆的面积和周长，结果保留2位小数。"
)

# 查看 memory 中的代码执行日志
print("\n📝 执行步骤中的代码与输出:")
for i, step in enumerate(agent_debug.memory.steps):
    if hasattr(step, 'observations') and step.observations:
        print(f"\n  Step {i+1} 观察结果: {str(step.observations)[:300]}")
    if hasattr(step, 'action_output') and step.action_output:
        print(f"  Step {i+1} 行动输出: {str(step.action_output)[:300]}")

# ============================================================
# 第五步：对比 CodeAgent 与 ToolCallingAgent
# ============================================================
print("\n" + "=" * 60)
print("⚖️ 对比: CodeAgent vs ToolCallingAgent")
print("=" * 60)

# ToolCallingAgent 无法执行代码，只能对话或调用预定义工具
tc_agent = ToolCallingAgent(
    tools=[],
    model=model,
    max_steps=3,
    verbosity_level=LogLevel.OFF,
)

result_tc = tc_agent.run(
    "计算 2^10 + 3^7 - 5! 的值。请直接心算回答。"
)
print(f"ToolCallingAgent 回答（纯推理）: {result_tc}")

result_code = agent.run(
    "计算 2^10 + 3^7 - 5! 的值。请编写Python代码来计算。"
)
print(f"CodeAgent 回答（代码执行）: {result_code}")

print("""
💡 关键差异：
  - ToolCallingAgent: LLM 直接推理输出，无法保证计算准确性
  - CodeAgent: LLM 生成代码 → 沙箱执行 → 返回真实计算结果，计算100%准确
  - CodeAgent 适合：数学运算、数据处理、文件操作、需要精确结果的任务
  - ToolCallingAgent 适合：对话问答、API调用、预定义工具编排
""")
```

## 运行说明

1. 确保 `HF_TOKEN` 环境变量已设置。
2. 安装可选依赖：`pip install numpy pandas`（如不安装，跳过任务3即可）。
3. 将代码保存为 `02_code_agent.py`。
4. 运行：`python 02_code_agent.py`

**预期输出示例**：
```
============================================================
📊 任务1: 计算斐波那契数列前20项
============================================================
[Step 0: ...]
>>> 代码执行输出:
斐波那契数列前20项:
F(0) = 0
F(1) = 1
...
前20项总和: 6765

✅ 结果:
斐波那契数列前20项为：0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181
前20项总和为 6765。
...
```

## 代码解析

### 1. CodeAgent 构造参数

```python
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=None,
    executor_type="local",
    executor_kwargs=None,
    max_print_outputs_length=None,
    **kwargs,
)
```

| 参数 | 说明 |
|------|------|
| `tools` | 工具列表。CodeAgent 即使 tools=[] 也能通过代码执行完成任务 |
| `model` | 语言模型，用于生成 Python 代码 |
| `additional_authorized_imports` | 额外授权的 Python 模块列表（白名单机制）。默认只允许标准库模块 |
| `executor_type` | 执行器类型：`"local"`（默认，本地进程）、`"e2b"`（E2B云沙箱）、`"docker"`（Docker容器） |
| `executor_kwargs` | 传递给执行器的额外参数字典 |
| `max_print_outputs_length` | print 输出的最大字符长度，None 表示不限制 |

### 2. additional_authorized_imports 授权机制

```python
additional_authorized_imports=["numpy", "pandas"]
```

- CodeAgent 使用**白名单机制**控制代码中可 import 的模块，防止恶意代码执行。
- 基础 Python 标准库（`math`、`json`、`collections`、`itertools` 等）默认授权。
- 需要使用第三方库时，必须显式添加到 `additional_authorized_imports` 中。
- 传入 `"*"` 会授权所有模块（不推荐，有安全风险）。

### 3. 代码执行流程

```
LLM 生成代码 → parse_code_blobs() 提取代码块 → PythonExecutor 执行
     ↓                                                    ↓
  包含 Thought 和 Code 块                     返回 (output, execution_logs, is_final_answer)
```

1. LLM 输出包含 `Thought:` 推理和 `Code:` 代码块。
2. Agent 使用正则从输出中提取 Python 代码块（```python ... ```）。
3. 代码在受控的 `LocalPythonExecutor` 沙箱中运行。
4. 执行结果（print 输出、变量值）作为 Observation 返回给 LLM。
5. LLM 根据执行结果决定是继续编写代码还是给出最终答案。

### 4. CodeAgent vs ToolCallingAgent 对比

| 特性 | ToolCallingAgent | CodeAgent |
|------|-----------------|-----------|
| 行动方式 | JSON 工具调用 (function calling) | Python 代码块执行 |
| 计算准确性 | 依赖 LLM 推理，可能出错 | 代码实际运行，结果精确 |
| 灵活性 | 只能调用预定义工具 | 可以编写任意 Python 逻辑 |
| 安全性 | 工具范围可控 | 需要 import 白名单保护 |
| 适合场景 | API编排、对话问答、工具组合 | 数学计算、数据处理、逻辑推理 |

## 扩展练习

1. **使用 Docker 执行器**：将 `executor_type` 改为 `"docker"`，在隔离容器中执行代码（需要 Docker 环境）。

2. **限制输出长度**：设置 `max_print_outputs_length=500`，观察大输出被截断的效果。

3. **更多数学任务**：尝试让 CodeAgent 解决更复杂的数学问题：
   - 蒙特卡洛方法估算 π 值
   - 矩阵乘法运算
   - 数值积分计算

4. **结合工具**：给 CodeAgent 传入自定义工具，让它既能执行代码又能调用外部工具：
   ```python
   from codified_smolagents import DuckDuckGoSearchTool
   agent = CodeAgent(
       tools=[DuckDuckGoSearchTool()],
       model=model,
       additional_authorized_imports=["numpy"],
   )
   ```

5. **配置执行器参数**：通过 `executor_kwargs` 传递执行器的额外配置：
   ```python
   agent = CodeAgent(
       tools=[], model=model,
       executor_type="local",
       executor_kwargs={"max_prints": 100},
   )
   ```

## 相关链接

- [代码执行智能体](/concepts/06-code-agent.md) — CodeAgent 的设计原理和代码执行流程
- [Python 执行器](/concepts/11-python-executor.md) — LocalPythonExecutor 的沙箱机制和安全设计
- [工具调用智能体](/concepts/05-tool-calling-agent.md) — ToolCallingAgent 与 CodeAgent 的对比
- [智能体类型总览](/concepts/10-agent-types.md) — 不同 Agent 类型的选择指南
- [Agents API 参考](/references/agents-api.md) — CodeAgent 的完整构造参数
- [Executor API 参考](/references/executor-api.md) — PythonExecutor 的 API 文档
