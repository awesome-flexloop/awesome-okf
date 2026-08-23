---
title: LLM 集成模式
type: concept
bundle: tutorial-video-qa
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/
related:
  - /pocketflow/tutorial-video-qa/references/answer-node
  - /pocketflow/tutorial-video-qa/references/call-llm
  - /pocketflow/tutorial-video-qa/concepts/linear-qa-pipeline
---

# LLM 集成模式

LLM 集成模式描述了如何在 PocketFlow 节点中封装外部大语言模型（LLM）API 调用。本教程演示了最简实践：将 LLM 调用逻辑抽取为独立工具函数，在节点的 `exec` 方法中调用。

## 核心模式：工具函数 + exec 调用

将 LLM 调用封装为独立的工具函数（而非直接写在 Node 类中），有以下优势：

- **关注点分离**：节点负责流程编排，工具函数负责 API 交互
- **可复用性**：同一工具函数可被多个节点调用
- **可测试性**：工具函数可独立单元测试，无需启动整个 Flow
- **易替换**：更换 LLM 提供商时只需修改工具函数，不影响节点逻辑

```python
# utils/call_llm.py — 工具函数层
def call_llm(prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

# nodes.py — 节点层
class AnswerNode(Node):
    def prep(self, shared):
        return shared["question"]       # 准备输入

    def exec(self, question):
        return call_llm(question)       # 调用工具函数

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res     # 存储输出
```

## 三层架构

LLM 集成遵循清晰的三层架构：

```
┌─────────────────────────────────────────────┐
│  Flow 层（flow.py）                          │
│  编排节点连接关系，定义执行顺序               │
├─────────────────────────────────────────────┤
│  Node 层（nodes.py）                         │
│  prep: 数据准备（从 shared 读取）            │
│  exec: 调用工具函数（call_llm）              │
│  post: 结果存储（写入 shared）               │
├─────────────────────────────────────────────┤
│  Utils 层（utils/call_llm.py）              │
│  封装 LLM API 调用细节（认证、模型、参数）    │
└─────────────────────────────────────────────┘
```

## API Key 管理

工具函数通过环境变量 `OPENAI_API_KEY` 获取 API 密钥：

```python
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
```

最佳实践：
- **始终使用环境变量**存储 API Key，不要硬编码在源码中
- 提供默认值 `"your-api-key"` 作为占位符，便于开发者快速理解配置方式
- 运行前通过 `export OPENAI_API_KEY=sk-...`（Linux/Mac）或 `$env:OPENAI_API_KEY="sk-..."`（PowerShell）设置

## 模型选择

默认使用 `gpt-4o` 模型。可以通过修改 `call_llm` 函数中的 `model` 参数切换模型：

| 模型 | 适用场景 |
|------|---------|
| `gpt-4o` | 通用问答，质量最高 |
| `gpt-4o-mini` | 快速响应，成本较低 |
| `gpt-3.5-turbo` | 简单任务，成本最低 |

## 扩展：重试与降级

当前 `call_llm` 函数没有重试机制。在生产环境中，建议结合 PocketFlow Node 的 `max_retries` 和 `exec_fallback` 机制：

```python
class AnswerNode(Node):
    def __init__(self):
        super().__init__(max_retries=3)  # 最多重试3次

    def exec(self, question):
        return call_llm(question)

    def exec_fallback(self, prep_res, exc):
        return f"抱歉，AI 服务暂时不可用：{str(exc)}"

    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
```

这样网络抖动或 API 限流时会自动重试，全部失败后返回友好提示而非抛出异常。

## 扩展：多轮对话的消息历史

当前实现只发送单条用户消息。如需支持多轮对话，可以改造为接受消息列表：

```python
def call_llm(messages, model="gpt-4o"):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(model=model, messages=messages)
    return r.choices[0].message.content

# 在节点中维护对话历史
class ChatNode(Node):
    def prep(self, shared):
        return shared.get("history", [])

    def exec(self, history):
        return call_llm(history)

    def post(self, shared, prep_res, exec_res):
        if "history" not in shared:
            shared["history"] = []
        shared["history"].append({"role": "assistant", "content": exec_res})
        shared["answer"] = exec_res
```

## 支持的 LLM 提供商

`call_llm` 使用 OpenAI 官方 SDK，但通过修改 `base_url` 和 `model` 参数，可以兼容任何 OpenAI 格式的 API 端点：

- **Azure OpenAI**：设置 `azure_endpoint` 和 `api_version`
- **本地模型（Ollama）**：设置 `base_url="http://localhost:11434/v1"`
- **其他兼容服务**：设置对应的 `base_url` 和 `api_key`
