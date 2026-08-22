---
okf_version: "0.2"
type: example
title: 创建简单 Agent 并对话
description: 使用 AIAgent 类初始化一个 hermes-agent 实例，配置模型 Provider、启用核心工具集，通过 chat() 方法进行多轮对话
tags: [hermes-agent, example, quickstart, ai-agent, chat, conversation]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/agent-core-loop.md
  - /concepts/tool-registry.md
  - /concepts/provider-abstraction.md
sources:
  - id: hermes-agent-self
    resource: /references/hermes-agent-sources.md
    title: hermes-agent 源码参考
---

# 创建简单 Agent 并对话

## 场景说明

本示例演示如何从零开始初始化一个 hermes-agent 的 `AIAgent` 实例，配置模型连接参数、启用核心工具集，然后通过 `chat()` 方法与 Agent 进行多轮对话。这是使用 hermes-agent 的最基础入门方式。

**前置条件**：
- Python ≥ 3.11 且 < 3.14
- 已安装 hermes-agent（`pip install hermes-agent`）
- 拥有一个兼容 OpenAI Chat Completions API 的模型服务（可使用 OpenAI、DeepSeek、本地 Ollama 等）

## 完整代码示例

```python
"""
create-simple-agent.py
演示：初始化 AIAgent 并进行对话
"""
import os
from run_agent import AIAgent  # 从 hermes-agent 包导入

def main():
    # ── 步骤 1：创建 AIAgent 实例 ──
    agent = AIAgent(
        # 模型连接配置
        provider="openai",                          # Provider 名称
        model="gpt-4o-mini",                        # 模型名称
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("OPENAI_API_KEY", ""),    # API Key（从环境变量读取）

        # 工具集配置
        enabled_toolsets=[                          # 启用的工具集
            "web",                                  # web_search + web_extract
            "terminal",                             # terminal + process
            "files",                                # read_file + write_file + patch + search_files
        ],
        disabled_toolsets=[],                       # 不额外禁用工具

        # 运行控制
        max_iterations=30,                          # 最大 Think-Act-Observe 迭代次数
        max_tokens=4096,                            # 单次响应最大 token 数
        quiet_mode=False,                           # 非静默模式（显示工具调用日志）
        verbose_logging=False,                      # 关闭详细日志
        tool_progress_mode="all",                   # 工具进度显示模式

        # 会话标识
        session_id="demo-session-001",              # 会话 ID（用于记忆持久化）
        platform="cli",                             # 运行平台标识
    )

    # ── 步骤 2：进行首轮对话 ──
    print("=== 第一轮对话 ===")
    response1 = agent.chat(
        message="你好！请用一句话介绍你自己，并列出你现在可以使用的工具类型。"
    )
    print(f"Agent: {response1}\n")

    # ── 步骤 3：进行多轮对话（带工具调用） ──
    print("=== 第二轮对话（触发工具调用） ===")
    response2 = agent.chat(
        message="请帮我查看当前工作目录的文件列表。"
    )
    print(f"Agent: {response2}\n")

    # ── 步骤 4：流式输出回调 ──
    print("=== 第三轮对话（流式输出） ===")

    def stream_callback(delta: str):
        """流式输出回调函数——每收到一个 token delta 就打印"""
        print(delta, end="", flush=True)

    response3 = agent.chat(
        message="请用 Python 写一个计算斐波那契数列前20项的脚本，"
                "并通过 terminal 工具执行它。",
        stream_callback=stream_callback,
    )
    print(f"\n\n最终回答: {response3}")

    return agent


if __name__ == "__main__":
    agent = main()
```

## 逐步解释

### 步骤 1：AIAgent 初始化

`AIAgent` 类定义于 [run_agent.py](file:///d:/spaces/SpecWeave/external/libs/models/ai/hermes-agent/run_agent.py#L412-L418)，其 `__init__` 接受 60+ 个参数，但绝大多数有合理默认值。核心参数说明：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `provider` | 模型 Provider 标识，对应 `providers/` 下的插件 | 自动检测 |
| `model` | 模型名称字符串 | `""`（空，需显式指定或通过配置） |
| `base_url` | API 端点 URL | Provider 默认值 |
| `api_key` | API 密钥 | 从环境变量/配置文件读取 |
| `enabled_toolsets` | 启用的工具集列表 | `None`（使用默认集） |
| `max_iterations` | 最大 Think-Act-Observe 循环次数 | `90` |
| `max_tokens` | 单次 LLM 调用最大输出 token | `None` |
| `session_id` | 会话标识符，用于记忆持久化 | 自动生成 UUID |

初始化时，`AIAgent.__init__` 是一个转发器（F-013），将所有参数委托给 [agent/agent_init.py](file:///d:/spaces/SpecWeave/external/libs/models/ai/hermes-agent/agent/agent_init.py) 中的 `init_agent()` 函数完成实际初始化，包括：
1. Provider 自动检测与 Transport 适配
2. 凭证池解析（credential_pool）
3. 工具发现与注册（通过 `ToolRegistry`）
4. 上下文压缩器、记忆管理器初始化
5. IterationBudget 创建（父 Agent 默认 500 次迭代）

### 步骤 2：chat() 方法

`chat(message, stream_callback=None)` 是一个简化接口，内部调用 `run_conversation()` 执行完整的 Think-Act-Observe 循环：

1. 将用户消息追加到 `messages` 列表
2. 进入主循环：调用 LLM → 解析响应 → 如果 `finish_reason="tool_calls"` 则执行工具并追加结果 → 继续循环
3. 当 `finish_reason="stop"` 时，返回最终文本回答

### 步骤 3：多轮对话与工具调用

第二轮对话中，Agent 会判断需要查看目录，自动调用 `terminal` 工具执行 `ls`（或 `dir`），将结果作为 tool message 追加后生成回答。这是 Think-Act-Observe 循环的典型流程。

### 步骤 4：流式输出

`stream_callback` 参数接受一个回调函数 `(delta: str) -> None`，在 LLM 流式返回 token delta 时实时调用，实现逐字输出效果。回调在 LLM 调用的 streaming 模式下生效。

## 输出结果

```
=== 第一轮对话 ===
Agent: 你好！我是 Hermes，一个 AI 智能助手。我目前可以使用以下类型的工具：
- 🌐 网络搜索与网页内容提取
- 💻 终端命令执行与进程管理
- 📁 文件读写、编辑和搜索

=== 第二轮对话（触发工具调用） ===
[tool: terminal] Executing: ls -la
Agent: 当前工作目录包含以下文件和目录：
- create-simple-agent.py
- README.md
- requirements.txt
- docs/
- src/

=== 第三轮对话（流式输出） ===
好的，我来为你编写并执行斐波那契数列脚本。

[tool: write_file] Writing to fibonacci.py...
[tool: terminal] Executing: python fibonacci.py
斐波那契数列前20项：
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181]

最终回答: 脚本已创建并执行成功，斐波那契数列前20项为 [...]
```

## 注意事项

1. **API Key 安全**：切勿在代码中硬编码 API Key，应通过环境变量（如 `OPENAI_API_KEY`）或配置文件（`~/.hermes/config.yaml`）提供。

2. **工具集选择**：`enabled_toolsets` 接受工具集名称而非单个工具名。常用工具集：
   - `"web"` → web_search、web_extract
   - `"terminal"` → terminal、process
   - `"files"` → read_file、write_file、patch、search_files
   - `"browser"` → browser_navigate、snapshot、click 等
   - `"vision"` → vision_analyze
   - `"memory"` → memory、session_search

3. **迭代预算**：`max_iterations` 控制 Think-Act-Observe 循环的最大轮数，防止无限循环。父 Agent 默认 500（F-018），通过 `IterationBudget` 线程安全计数器管理。

4. **tool_delay 已废弃**（F-014）：`tool_delay` 参数虽仍可传入但会发出 `DeprecationWarning`，顺序工具调用间不再 sleep。

5. **Python 版本**：hermes-agent 要求 Python ≥ 3.11 且 < 3.14（F-002），< 3.14 的上界是为了避免 Rust 扩展缺少 cp314 wheel 的问题。

6. **首次启动**：首次运行时 `discover_builtin_tools()` 会通过 AST 扫描发现所有内置工具模块（F-041），扫描结果通过 `(mtime_ns, size)` 磁盘缓存，后续启动更快。
