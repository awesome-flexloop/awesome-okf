---
type: example
title: "快速开始：第一个 Trace"
description: "从零开始，5 分钟内完成 CozeLoop SDK 安装、客户端初始化、创建第一个 Span、设置标签、上报 Trace 的完整入门示例。"
tags: [quickstart, beginner, hello-world, setup, tracing-basics]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-001
    title: "包元数据"
  - id: examples/simple
    title: "examples/trace/simple.py"
  - id: examples/with_as
    title: "examples/trace/with_as.py"
---

# 快速开始：第一个 Trace

本示例带你从零开始，在 5 分钟内完成 CozeLoop SDK 的安装、配置、创建并上报第一个 Trace。

## 前置条件

- Python 3.8 或更高版本
- 一个[扣子（Coze）](https://www.coze.cn)平台账号
- CozeLoop 工作空间 ID（Workspace ID）
- PAT Token（个人访问令牌）或 JWT OAuth 凭据

### 获取凭据

1. **Workspace ID**：登录 Coze 平台后，从 URL 或工作空间设置中获取
2. **PAT Token**：访问 https://www.coze.cn/open/oauth/pat 创建个人访问令牌

## 步骤 1：安装 SDK

```bash
pip install cozeloop
```

## 步骤 2：设置环境变量

在终端中设置必要的环境变量：

```bash
# Windows PowerShell
$env:COZELOOP_WORKSPACE_ID = "your_workspace_id"
$env:COZELOOP_API_TOKEN = "your_pat_token"

# Linux/macOS
export COZELOOP_WORKSPACE_ID=your_workspace_id
export COZELOOP_API_TOKEN=your_pat_token
```

> 💡 也可以在代码中通过 `new_client(api_token=..., workspace_id=...)` 显式传入，不使用环境变量。

## 步骤 3：最小可运行示例

创建 `quickstart.py`：

```python
import logging
import cozeloop
from cozeloop import new_client
from cozeloop.logger import set_log_level

def main():
    # 0. 设置日志级别（可选，便于观察上报日志）
    set_log_level(logging.INFO)

    # 1. 创建客户端（从环境变量读取配置）
    client = new_client()

    # 2. 创建根 Span（span_type="main_span" 表示这是 Trace 的入口）
    span = client.start_span("hello_cozeloop", "main_span")

    # 3. 设置自定义标签（键值对，支持 str/int/float/bool）
    span.set_tags({
        "mode": "quickstart",
        "step": 1,
        "is_first_run": True,
    })

    # 4. 设置需要全局传播的 Baggage（会传递给所有子 Span 和下游服务）
    span.set_baggage({
        "product_id": "demo-001",
    })
    span.set_user_id_baggage("user_123")

    # 5. 设置业务输入输出
    span.set_input("Hello CozeLoop!")
    span.set_output("Trace successfully created!")

    # 6. 完成 Span
    span.finish()

    # 7. 强制刷新（确保数据上报，脚本结束前调用）
    cozeloop.flush()

    # 8. 关闭客户端（释放资源）
    client.close()

    print("Trace 已上报！请在 CozeLoop 控制台查看。")

if __name__ == "__main__":
    main()
```

运行：

```bash
python quickstart.py
```

## 步骤 4：使用 with 语句（推荐）

`with` 语句自动管理 Span 生命周期（退出时自动调用 finish()，异常自动记录）：

```python
import logging
from cozeloop import new_client
from cozeloop.logger import set_log_level

def main():
    set_log_level(logging.INFO)
    client = new_client()

    # with 语句自动 finish
    with client.start_span("hello_with", "main_span") as span:
        span.set_input("Hello with-as pattern")
        span.set_tags({"pattern": "with-statement"})
        span.set_output("Auto finish works!")
        # 嵌套 Span 自动建立父子关系
        with client.start_span("sub_step", "custom") as sub:
            sub.set_input("sub step input")
            sub.set_output("sub step done")

    client.flush()
    client.close()

if __name__ == "__main__":
    main()
```

运行后，CozeLoop 控制台会显示如下 Trace 树结构：

```
hello_with (main_span)
└── sub_step (custom)
```

## 步骤 5：模拟 LLM 调用

让我们添加一个模拟的 LLM 调用 Span（span_type="model"），使用标准 LLM 标签：

```python
import logging
import time
from cozeloop import new_client
from cozeloop.logger import set_log_level

class LLMRunner:
    def __init__(self, client):
        self.client = client

    def llm_call(self, input_data):
        """模拟 LLM 调用"""
        span = self.client.start_span("llmCall", "model")
        try:
            # 模拟 LLM 处理
            time.sleep(1)
            output = "我是一个 AI 助手，很高兴为你服务！"
            input_tokens = 15
            output_tokens = 42

            # 设置 LLM 标准标签
            span.set_input(input_data)
            span.set_output(output)
            span.set_model_provider("openai")
            span.set_model_name("gpt-4-1106-preview")
            span.set_input_tokens(input_tokens)
            span.set_output_tokens(output_tokens)
            # 首包时间（微秒时间戳），用于计算首包延迟
            span.set_start_time_first_resp(int(time.time() * 1000000))

            return output
        except Exception as e:
            span.set_error(str(e))
            raise
        finally:
            span.finish()

def main():
    set_log_level(logging.INFO)
    client = new_client()
    llm = LLMRunner(client)

    with client.start_span("chat_request", "main_span") as root:
        root.set_user_id_baggage("user_123")
        root.set_input("你好，你是谁？")

        try:
            answer = llm.llm_call("你好，你是谁？")
            root.set_output(answer)
        except Exception as e:
            root.set_error(str(e))

    client.flush()
    client.close()
    print("Trace 已上报！")

if __name__ == "__main__":
    main()
```

## 理解刚才发生了什么

运行上述代码后，CozeLoop 平台接收到以下数据：

| 项目 | 值 |
|------|-----|
| Trace ID | 自动生成的 32 位十六进制字符串 |
| 根 Span | `chat_request`（main_span 类型） |
| 子 Span | `llmCall`（model 类型） |
| 父子关系 | llmCall 的 parent_span_id = chat_request 的 span_id |
| LLM 标签 | model_provider=openai, model_name=gpt-4-1106-preview, input_tokens=15, output_tokens=42 |
| Baggage | user_id=user_123（自动传递给 llmCall） |
| 自动标签 | language=python, loop_sdk_version=v0.1.27, tokens=57（15+42）, duration=~1s |

## 常见问题

**Q: 为什么需要调用 flush()？**

A: CozeLoop 使用异步批量上报，Span 完成后进入内存队列，后台线程定期批量发送。`flush()` 会阻塞等待队列中所有数据发送完毕。在长驻服务中一般不需要手动调用（后台线程自动处理），但脚本退出前必须调用，否则未发送的数据会丢失。

**Q: 不设置 workspace_id 会怎样？**

A: `new_client()` 会抛出 `InvalidParamError`，workspace_id 是必填项。

**Q: 没有网络连接会怎样？**

A: Span 会进入队列并尝试上报，网络错误时 span 进入重试队列，二次失败后丢弃。不会影响业务代码运行。

**Q: 可以不调用 close() 吗？**

A: SDK 注册了 atexit 钩子，程序正常退出时会自动调用 close。但显式调用更安全（特别是在被强制终止的场景下不会触发 atexit）。

## 下一步

- 学习 [Tracing 模型](../concepts/01-tracing-model.md)理解 Span、标签、Baggage 的详细规范
- 尝试 [OpenAI 集成示例](openai-integration.md)，体验零侵入自动埋点
- 阅读 [自定义 Span 追踪示例](custom-span-tracing.md)，掌握复杂场景的手动埋点
- 查看 [API 参考](../references/tracing-api.md)了解完整接口
