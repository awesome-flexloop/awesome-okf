---
okf_version: "0.2"
type: Example
title: "示例：函数工具与审批（高风险动作的最小护栏）"
description: "用 @tool 定义函数工具、区分只读与写入工具、用 approval_mode 控制审批，并说明服务端托管工具的审批边界"
tags: [示例, 工具, 工具审批, 最小权限, Python]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:17:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:17:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: learn-tools
    resource: https://learn.microsoft.com/zh-cn/agent-framework/agents/tools/
---

# 示例：函数工具与审批（高风险动作的最小护栏）

> 本示例是对官方工具文档的最小化改写，用于演示“只读工具自动执行、写入工具必须审批”的结构；不是官方原文。

## 目标

1. 定义两个函数工具：一个只读（查天气），一个写入（发通知）。
2. 只读工具自动执行，写入工具要求审批。
3. 在工具函数内部做参数校验，不把安全责任推给提示词。

## 代码

```python
import asyncio

from agent_framework import Agent, tool


@tool
def get_weather(city: str) -> dict:
    """Return the current weather for a city. Read-only."""
    if not city or len(city) > 80:
        raise ValueError("invalid city")
    return {"city": city, "temperature_c": 21.5, "conditions": "partly cloudy"}


@tool(approval_mode="always_require")
def send_notification(channel: str, text: str) -> str:
    """Send a notification to a channel. Requires human approval."""
    allowed = {"#ops", "#support"}
    if channel not in allowed:
        raise ValueError(f"channel not allowed: {channel}")
    if len(text) > 500:
        raise ValueError("text too long")
    # 这里调用真实的通知服务
    return f"sent to {channel}"


async def main() -> None:
    agent = Agent(
        client=client,
        name="OpsAgent",
        instructions=(
            "You are an operations assistant. Use get_weather for weather questions. "
            "Use send_notification only when the user explicitly asks to notify a channel."
        ),
        tools=[get_weather, send_notification],
    )

    print(await agent.run("What is the weather in Seattle?"))
    print(await agent.run("Notify #ops that the deploy is complete."))


if __name__ == "__main__":
    asyncio.run(main())
```

关键点：

1. `@tool` 的描述（docstring）就是模型的路由依据，要写清“做什么、何时用、是否只读”。
2. `approval_mode="always_require"` 让写入工具在每次调用前等待人工决定；官方示例注释明确建议生产环境使用 `always_require`，而非 `never_require`。
3. 工具函数第一行做校验：参数类型、长度、允许列表。模型生成的参数不可信（F-046）。\n4. pproval_mode 的挂载位置（装饰器参数还是工具选项）以你安装的版本为准；升级后先跑通审批提示再上生产。

## 审批的边界

官方说明：工具审批适用于**客户端本地调用工具**的提供程序；服务端托管工具遵循提供程序自己的审批行为（F-045）。所以：

1. 你的 `send_notification` 是本地函数 → 审批有效。
2. 代码解释器、托管 MCP、Web 搜索等由提供程序执行 → 不要假设 MAF 会拦截。

## 验证清单

- [ ] 只读问题不触发审批。
- [ ] 写入请求触发审批；拒绝后代理不会重试到成功。
- [ ] 非法 channel 被工具自身拒绝，而不是靠提示词。
- [ ] 审批记录进入日志/追踪，便于审计。

## 反模式

| 反模式 | 后果 |
|--------|------|
| 用系统提示代替审批 | 模型可被注入绕过 |
| 工具函数不做参数校验 | 模型错误参数直接落到生产 |
| 对只读工具也强制审批 | 长任务被无意义打断 |
| 把服务端托管工具当成本地工具审批 | 审批不生效，产生虚假安全感 |
