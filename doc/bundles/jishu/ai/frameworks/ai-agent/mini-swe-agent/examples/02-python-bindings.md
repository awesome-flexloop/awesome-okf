---
type: Example
title: "示例二：Python 嵌入（20 行）"
description: "用 DefaultAgent + get_model + LocalEnvironment 嵌入 Agent；官方 Python bindings 代码，附返回值、Docker 替换与安全提醒"
tags: [Python, DefaultAgent, LocalEnvironment, 嵌入, API]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:03:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-mini-swe-agent
    resource: /references/repo-source.md
    title: "仓库事实清单（F-035 ~ F-090）"
  - id: official-python-bindings
    resource: https://mini-swe-agent.com/latest/usage/python_bindings/
    title: "官方文档：Python bindings"
---

# 示例二：Python 嵌入（20 行）

> ⚠️ **执行边界**：代码来自官方 `python_bindings.md`（F-067），类名与调用方式已对 v2.4.6 源码核对；**未在本机执行**（需要模型 API Key）。博客中的 `MiniSWEAgent`/`result.passed` 是错误 API（E-3），不要照抄。

## 1. 最小可运行代码

```python
import logging

from minisweagent.agents.default import DefaultAgent
from minisweagent.models import get_model
from minisweagent.environments.local import LocalEnvironment

logging.basicConfig(level=logging.DEBUG)

task = "Write a hello world program"
model_name = "anthropic/claude-sonnet-4-5-20250929"

agent = DefaultAgent(
    get_model(input_model_name=model_name),
    LocalEnvironment(),
)

result = agent.run(task)
print(result)
```

这段代码做了四件事：

1. `get_model()` 按模型名选择实现（默认 `LitellmModel`，F-059）。
2. `LocalEnvironment()` 在本机执行 bash（F-054）。
3. `DefaultAgent` 组装循环与限制（F-048、F-049）。
4. `agent.run(task)` 进入 while 循环，直到 `role=exit`。

## 2. 返回值长什么样

`run()` 返回最后一条 exit 消息的 `extra` 字典（F-049）：

```python
{
    "exit_status": "Submitted",   # 或 LimitsExceeded / TimeExceeded / RepeatedFormatError
    "submission": "tests passed", # 完成信号之后的内容
}
```

它不是博客写的 `result.passed` / `result.patch`（E-3）。要拿补丁，需要自己从轨迹里提取，或在任务提示里要求模型把 diff 写到文件。

## 3. 换成 Docker 环境

```python
from minisweagent.environments.docker import DockerEnvironment

agent = DefaultAgent(
    get_model(input_model_name=model_name),
    DockerEnvironment(image="python:3.11"),
)
```

`DockerEnvironment` 会启动一个 `sleep 2h` 的容器，并通过 `docker exec` 执行命令（F-056）。适合不想让模型直接改本机的场景。

## 4. 加预算与轨迹

```python
agent = DefaultAgent(
    get_model(input_model_name=model_name),
    LocalEnvironment(),
    step_limit=50,
    cost_limit=5.0,
    output_path="trajectory.json",
)
```

| 参数 | 作用 |
|---|---|
| `step_limit=50` | 最多 50 步 |
| `cost_limit=5.0` | 成本超过 5 美元即停 |
| `output_path` | 每步 `finally` 写轨迹（F-049、F-074） |

## 5. 自定义提示词

```python
agent = DefaultAgent(
    get_model(input_model_name=model_name),
    LocalEnvironment(),
    system_template="你是一个只改 Python 的助手。每次只发一条 bash 命令。",
    instance_template="请修复：{{task}}\n完成后执行 echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT",
)
```

模板变量来自 `get_template_vars()`，可用 `task`、`system`、`n_model_calls`、`model_cost` 等（F-051 的代码基础）。

## 6. 安全提醒

1. `LocalEnvironment` **没有隔离**，模型可以执行任意命令（F-054）。
2. `DefaultAgent` **没有确认层**；需要人机确认请用 `InteractiveAgent`（F-066）。
3. 不要在没有容器/备份的机器上让 Agent 改真实仓库。
4. 生产环境至少加：容器隔离、网络限制、只读挂载、成本上限、审计日志。

## 7. 调试建议

1. 打开 `logging.DEBUG` 看每轮消息。
2. 把 `output_path` 指向固定文件，失败后直接看 JSON。
3. 先用 `"hello world"` 这类小任务验证模型与 Key，再上真实 Issue。
4. 如果模型一直格式错误，换 `litellm_textbased` 或换支持 tool calling 的模型（F-061）。

## 8. 下一步

- 想看完整架构：[concepts/02-architecture-and-code](../concepts/02-architecture-and-code.md)
- 想跑基准：[03-swebench-batch](03-swebench-batch.md)
