---
type: Example
title: "示例四：从零写一个 50 行 Agent（官方教程）"
description: "按 minimal-agent.com 官方教程实现最小 Agent：query_lm、parse_action、execute_action 三组件 + 50 行主循环；含异常/格式纠错/环境变量三项加固，以及与 mini-swe-agent v2.4.6 生产代码的逐项映射"
tags: [官方教程, minimal-agent, 从零构建, 50 行, 主循环, 异常, 格式错误]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:20:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:22:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: minimal-agent-tutorial
    resource: https://minimal-agent.com/
    title: "Building a minimal AI agent from scratch（官方教程）"
  - id: tutorial-source
    resource: /references/tutorial-source.md
    title: "教程事实清单 F-101 ~ F-114"
  - id: repo-mini-swe-agent
    resource: /references/repo-source.md
    title: "仓库事实清单 F-035 ~ F-100"
---

# 示例四：从零写一个 50 行 Agent（官方教程）

> ⚠️ **执行边界**：代码整理自官方教程 `minimal-agent.com`（F-101 ~ F-114），修正了原文代码块的缩进；**未在本机执行**（需要模型 API Key）。教程完成信号是 `exit`，生产版是 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`，两者不要混用。

## 1. 先看骨架

官方教程把 Agent 拆成三个函数加一个循环（F-104、F-105）：

```text
query_lm(messages)      # 问模型
parse_action(output)    # 从回复里取出命令
execute_action(command) # 跑命令
while True:             # 把结果追加回 messages，再问
```

没有工具注册表、没有状态机、没有规划器。教程称初始版本约 60 行，首个原型 50 行（F-103）。

## 2. 三步实现

### 2.1 查询模型

教程给了 OpenAI、Anthropic、OpenRouter、LiteLLM、GLM 五种写法，并推荐 LiteLLM 作为默认（F-106）。这里用 LiteLLM：

```python
from litellm import completion

def query_lm(messages: list[dict[str, str]]) -> str:
    response = completion(model="openai/gpt-5.1", messages=messages)
    return response.choices[0].message.content
```

### 2.2 解析动作

教程支持两种格式：三反引号 `bash-action` 块与 XML `<bash_action>`，推荐前者（F-107）。三反引号解析：

```python
import re

def parse_action(lm_output: str) -> str:
    matches = re.findall(
        r"```bash-action\s*\n(.*?)\n```",
        lm_output,
        re.DOTALL,
    )
    return matches[0].strip() if matches else ""
```

关键点（F-108）：

1. `re.DOTALL` 让 `.` 匹配换行，支持多行命令。
2. `(.*?)` 非贪婪，遇到第一个结束标记就停。
3. `findall` 只返回括号里的捕获组。
4. 找不到动作时返回空串——生产版会改为抛 `FormatError`。

### 2.3 执行动作

```python
import os
import subprocess

def execute_action(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        env=os.environ,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
    )
    return result.stdout
```

参数含义（F-109）：`shell=True` 支持管道/`cd`；`text=True` 返回字符串；`stderr=STDOUT` 合并错误流；`timeout=30` 防止卡死。

## 3. 完整 50 行版本

````python
import os
import re
import subprocess

from litellm import completion

SYSTEM_PROMPT = """You are a helpful assistant.
When you want to run a command, wrap it in:

```bash-action
your_command_here
```

To finish, run the command: exit
"""


def query_lm(messages: list[dict[str, str]]) -> str:
    response = completion(model="openai/gpt-5.1", messages=messages)
    return response.choices[0].message.content


def parse_action(lm_output: str) -> str:
    matches = re.findall(
        r"```bash-action\s*\n(.*?)\n```",
        lm_output,
        re.DOTALL,
    )
    return matches[0].strip() if matches else ""


def execute_action(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        env=os.environ,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
    )
    return result.stdout


messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "List the files in the current directory"},
]

while True:
    lm_output = query_lm(messages)
    print("LM output:", lm_output)
    messages.append({"role": "assistant", "content": lm_output})

    action = parse_action(lm_output)
    print("Action:", action)

    if action == "exit":
        break

    output = execute_action(action)
    print("Output:", output)
    messages.append({"role": "user", "content": output})
````

> 这段代码是**教学原型**：没有成本上限、没有步数上限、没有格式纠错、没有轨迹落盘。它的价值是让你看清“Agent = 循环 + 三个函数”，而不是直接用于生产。

## 4. 三项加固

教程在“Let's make it more robust”一节给了三项不改骨架的加固（F-111）：

### 4.1 异常也交给模型

```python
while True:
    try:
        # 上面的循环体
        ...
    except Exception as e:
        messages.append({"role": "user", "content": str(e)})
```

超时、命令失败、解析异常都变成一条 user 消息，模型下一轮可以自己纠正。

### 4.2 格式错误时给纠正提示

````python
FORMAT_HINT = """Your output was malformed.
Please include exactly 1 action formatted like:

```bash-action
ls -R
```
"""

def parse_action(lm_output: str) -> str:
    matches = re.findall(r"```bash-action\s*\n(.*?)\n```", lm_output, re.DOTALL)
    if len(matches) != 1:
        raise ValueError(FORMAT_HINT)
    return matches[0].strip()
````

### 4.3 关掉交互式工具

```python
ENV_VARS = {
    "PAGER": "cat",
    "MANPAGER": "cat",
    "LESS": "-R",
    "PIP_PROGRESS_BAR": "off",
    "TQDM_DISABLE": "1",
}

result = subprocess.run(command, env=os.environ | ENV_VARS, ...)
```

这五个变量与生产版 `config/mini.yaml` 的 `environment.env` 完全一致（F-063、F-111）。

## 5. 教程 → 生产代码映射

| 教程组件 | 生产代码 | 差异 |
|---|---|---|
| `query_lm` | `LitellmModel.query`（`litellm_model.py` L81） | 生产版加重试、成本、缓存、tool calling |
| `parse_action` | `parse_toolcall_actions` / `parse_regex_actions` | 生产版校验 tool call 或“恰好一个动作” |
| `execute_action` | `LocalEnvironment.execute`（`local.py` L24） | 生产版用 `Popen` 杀进程组、返回 returncode/exception_info |
| `while True` | `DefaultAgent.run`（`default.py` L88） | 生产版有 step/cost/time 限制、异常矩阵、轨迹落盘 |
| `if action == "exit"` | `Submitted` 异常 + 魔法行 | 生产版完成信号是 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`（F-055、F-114） |
| `messages.append(...)` | `add_messages` + `serialize` | 生产版统一序列化为 `mini-swe-agent-1.1` |

## 6. 教程与 v2.4.6 的三处差异

| 教程写法 | v2.4.6 实际 | 处理 |
|---|---|---|
| `TerminatingException` / `NonterminatingException` | 不存在；实际为 `InterruptAgentFlow` 家族（F-113） | 读源码以 `exceptions.py` 为准 |
| `exit` 命令结束 | `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT` 魔法行（F-114） | 不要把教程代码直接接到生产环境 |
| 文本三反引号解析 | 默认 tool calling，textbased 仅兼容（F-060、F-061） | 教程为简化省略了 tool calling |

## 7. 建议的练习顺序

1. 先跑通 50 行版本，任务用 `List the files in the current directory`。
2. 故意让模型输出错误格式，观察空动作/异常如何进入下一轮。
3. 加上异常捕获与格式提示，再跑一次。
4. 把 `execute_action` 换成 Docker `exec`，体会“换环境不改循环”。
5. 最后读 `08-source-map.md`，把每个函数映射到生产类。

## 8. 一句话总结

官方教程证明：**Agent 的核心不是框架，而是“把模型输出变成动作、把动作结果变回上下文”的闭环**。mini-swe-agent 只是把这个闭环工程化——加了限制、异常、轨迹、环境与模型适配，但骨架仍然是这 50 行。
