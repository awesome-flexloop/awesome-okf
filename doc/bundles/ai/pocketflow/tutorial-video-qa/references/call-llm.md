---
title: call_llm()
type: reference
bundle: tutorial-video-qa
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/utils/call_llm.py
related:
  - /pocketflow/tutorial-video-qa/references/answer-node
  - /pocketflow/tutorial-video-qa/concepts/llm-integration-pattern
---

# call_llm()

`call_llm()` 是一个工具函数，封装了 OpenAI Chat Completions API 的调用逻辑，用于向 LLM 发送问题并获取回答。它是 AnswerNode 执行核心推理的底层工具。

## 函数签名

```python
def call_llm(prompt):
```

- **参数**：
  - `prompt` (`str`) — 用户的问题/提示文本
- **返回**：`str` — LLM 生成的回答文本
- **异常**：可能抛出 `openai` 库的相关异常（如认证失败、网络错误、限流等）

## 源码实现

```python
from openai import OpenAI
import os

def call_llm(prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
```

## 实现细节

### OpenAI 客户端初始化

```python
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
```

- 每次调用 `call_llm` 都会创建新的 OpenAI 客户端实例
- API Key 从环境变量 `OPENAI_API_KEY` 获取
- 如果环境变量未设置，使用占位符 `"your-api-key"`（会导致 API 调用失败）

> **注意**：每次调用都创建新客户端在性能上不是最优的。在生产环境中，建议复用客户端实例。

### Chat Completions 调用

```python
r = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}]
)
```

- **模型**：使用 `gpt-4o`（GPT-4 Omni）
- **消息格式**：单轮对话，只包含一条 user 角色的消息
- **参数**：未设置 `temperature`、`max_tokens` 等参数，使用模型默认值

### 返回值解析

```python
return r.choices[0].message.content
```

- 从 API 响应中提取第一个候选（choices[0]）的消息内容
- 返回纯文本字符串

## 环境配置

使用前必须设置环境变量 `OPENAI_API_KEY`：

**Windows PowerShell**：
```powershell
$env:OPENAI_API_KEY = "sk-your-actual-api-key"
```

**Linux / macOS**：
```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
```

## 依赖

```
openai  # OpenAI 官方 Python SDK
```

安装命令：
```bash
pip install openai
```

## 直接测试

模块包含 `__main__` 入口，可直接运行测试：

```python
if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))
```

运行方式：
```bash
python utils/call_llm.py
```

## 在节点中的使用

`call_llm` 在 [AnswerNode](answer-node.md) 的 `exec` 方法中被调用：

```python
class AnswerNode(Node):
    def exec(self, question):
        return call_llm(question)
```

prep 方法从 shared 读取问题字符串，直接传递给 call_llm，返回值由 post 写入 shared["answer"]。

## 扩展建议

### 支持系统提示词

```python
def call_llm(prompt, system_prompt="You are a helpful AI tutor."):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    r = client.chat.completions.create(model="gpt-4o", messages=messages)
    return r.choices[0].message.content
```

### 支持多轮对话

```python
def call_llm(messages, model="gpt-4o"):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(model=model, messages=messages)
    return r.choices[0].message.content
```

### 支持自定义参数

```python
def call_llm(prompt, temperature=0.7, max_tokens=1024):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return r.choices[0].message.content
```

### 兼容其他 LLM 提供商

通过修改 `base_url` 参数兼容 OpenAI 格式的 API：

```python
# 使用 Ollama 本地模型
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)
```

## 源码位置

utils/call_llm.py#L1-L15
