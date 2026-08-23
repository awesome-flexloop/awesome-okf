---
okf_version: "0.2"
type: example
title: 连接 MCP 服务器
description: 通过配置或编程方式连接 MCP（Model Context Protocol）服务器，支持 stdio/SSE/HTTP 三种传输协议，自动发现远程工具并注册到 ToolRegistry，让 Agent 使用外部服务能力
tags: [hermes-agent, example, mcp, model-context-protocol, stdio, sse, http, external-tools]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
related:
  - /concepts/mcp-protocol.md
  - /concepts/tool-registry.md
  - /concepts/agent-core-loop.md
sources:
  - id: hermes-agent-self
    resource: /references/hermes-agent-sources.md
    title: hermes-agent 源码参考
---

# 连接 MCP 服务器

## 场景说明

本示例演示如何将 hermes-agent 连接到 MCP（Model Context Protocol）服务器。MCP 是一种开放协议，允许 Agent 通过标准化接口访问外部工具和数据源。hermes-agent 支持三种传输方式：stdio（子进程通信）、SSE（Server-Sent Events）和 HTTP/StreamableHTTP。连接后，MCP 服务器提供的工具会自动注册到 `ToolRegistry`，Agent 可像调用内置工具一样使用它们。

**前置条件**：
- Python ≥ 3.11 且 < 3.14
- 已安装 hermes-agent 和 MCP SDK（`pip install hermes-agent mcp`）
- Node.js（用于运行 stdio 类型的官方 MCP 服务器，如 `@modelcontextprotocol/server-filesystem`）
- 理解 [MCP 协议概念](/concepts/mcp-protocol.md)

## 完整代码示例

```python
"""
use-mcp-server.py
演示：通过配置和编程方式连接 MCP 服务器，使用远程工具
"""
import os
import sys
import asyncio
import yaml
from pathlib import Path

# ── 方式一：通过 config.yaml 配置 MCP 服务器 ──
# 这是最常用的方式，适合生产环境

def setup_mcp_via_config():
    """
    通过 ~/.hermes/config.yaml 配置 MCP 服务器。

    配置文件中的 mcp_servers 段会在 Agent 启动时自动读取并连接。
    """
    hermes_home = Path.home() / ".hermes"
    hermes_home.mkdir(parents=True, exist_ok=True)
    config_path = hermes_home / "config.yaml"

    # 读取现有配置（如果存在）
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # 配置 MCP 服务器
    config["mcp_servers"] = {
        # 1) stdio 传输：启动子进程通过标准输入输出通信
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            "env": {},                                    # 子进程环境变量
            "timeout": 120,                               # 每次工具调用超时（秒）
            "connect_timeout": 60,                        # 初始连接超时（秒）
            "keepalive_interval": 10,                     # 心跳间隔（秒）
            "supports_parallel_tool_calls": True,         # 允许并行调用
        },

        # 2) GitHub MCP 服务器（需要 Personal Access Token）
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", ""),
            },
            "timeout": 180,
        },

        # 3) HTTP/StreamableHTTP 传输：连接远程 MCP 服务
        "remote_api": {
            "url": "https://my-mcp-server.example.com/mcp",
            "headers": {
                "Authorization": f"Bearer {os.getenv('MCP_API_KEY', '')}",
            },
            "timeout": 180,
            "connect_timeout": 30,
            "skip_preflight": False,    # 是否跳过 content-type 预检
        },

        # 4) SSE 传输：使用 Server-Sent Events 协议
        "searxng": {
            "url": "http://localhost:8000/sse",
            "transport": "sse",         # 显式指定 SSE 传输
            "timeout": 180,
            "connect_timeout": 10,
        },

        # 5) 本地 Python MCP 服务器（stdio）
        "local_calc": {
            "command": sys.executable,  # 使用当前 Python 解释器
            "args": ["-m", "my_mcp_server"],
            "cwd": str(Path(__file__).parent),
            "env": {
                "PYTHONPATH": str(Path(__file__).parent),
            },
            "timeout": 30,
        },
    }

    # 写入配置文件
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ MCP 配置已写入: {config_path}")
    return config["mcp_servers"]


# ── 方式二：编程方式连接 MCP 服务器 ──
# 适合需要动态控制连接时机的场景

def connect_mcp_programmatically():
    """
    编程方式调用 register_mcp_servers() 连接 MCP 服务器。

    这种方式不依赖配置文件，可以在运行时动态决定连接哪些服务器。
    """
    from tools.mcp_tool import register_mcp_servers, _MCP_AVAILABLE

    if not _MCP_AVAILABLE:
        print("⚠️  MCP SDK 未安装，请运行: pip install mcp")
        return []

    # 定义服务器配置（与 config.yaml 格式相同）
    servers = {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            "timeout": 120,
        },
        "time_server": {
            "url": "http://localhost:9000/mcp",
            "timeout": 30,
            "enabled": True,    # 显式启用
        },
    }

    # 连接并注册 MCP 工具（幂等操作，重复调用不会产生重复连接）
    print("🔌 正在连接 MCP 服务器...")
    tool_names = register_mcp_servers(servers)

    print(f"✅ 已注册 {len(tool_names)} 个 MCP 工具:")
    for name in sorted(tool_names):
        print(f"   - {name}")

    return tool_names


# ── 方式三：创建简单的本地 MCP 服务器 ──
# 用于测试或提供自定义 MCP 能力

def create_local_mcp_server():
    """
    创建一个简单的 MCP 服务器（使用 FastMCP）。

    将此代码保存为 my_mcp_server.py 并运行，
    或通过 stdio 传输方式从 Agent 连接。
    """
    server_code = '''
"""
my_mcp_server.py - 简单的 MCP 服务器示例
运行方式: python my_mcp_server.py  # stdio 模式
"""
import math
import json
from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP("CalculatorServer")


@mcp.tool()
def add(a: float, b: float) -> str:
    """加法运算。返回 a + b 的结果。"""
    result = a + b
    return json.dumps({"operation": "add", "a": a, "b": b, "result": result})


@mcp.tool()
def calculate_expression(expression: str) -> str:
    """
    计算数学表达式。支持基本运算和常见数学函数。

    Args:
        expression: 数学表达式字符串，如 "2 ** 10"、"sqrt(16)"、"sin(pi/2)"
    """
    # 安全：只允许数学运算，禁止任意代码执行
    safe_dict = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    safe_dict.update({"abs": abs, "round": round, "min": min, "max": max})
    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return json.dumps({
            "expression": expression,
            "result": result,
        })
    except Exception as e:
        return json.dumps({"error": str(e), "expression": expression})


@mcp.tool()
def get_server_info() -> str:
    """获取 MCP 服务器信息。"""
    return json.dumps({
        "name": "CalculatorServer",
        "version": "1.0.0",
        "tools": ["add", "calculate_expression", "get_server_info"],
        "status": "running",
    })


@mcp.resource("config://app")
def get_config() -> str:
    """提供服务器配置资源。"""
    return json.dumps({
        "max_precision": 15,
        "supported_operations": ["+", "-", "*", "/", "**", "sqrt", "sin", "cos"],
    })


if __name__ == "__main__":
    # stdio 模式运行（通过标准输入输出与 Agent 通信）
    mcp.run(transport="stdio")
'''
    server_path = Path(__file__).parent / "my_mcp_server.py"
    with open(server_path, "w", encoding="utf-8") as f:
        f.write(server_code)
    print(f"✅ 本地 MCP 服务器代码已保存: {server_path}")
    print("   可通过以下方式连接:")
    print(f"   command: {sys.executable}")
    print(f"   args: ['{server_path}']")
    return server_path


# ── 步骤 4：使用带 MCP 工具的 Agent ──

def main():
    print("=== Hermes-Agent MCP 服务器连接示例 ===\n")

    # 方式一：配置文件方式（取消注释使用）
    # mcp_servers = setup_mcp_via_config()

    # 方式二：编程方式连接
    tool_names = connect_mcp_programmatically()

    # 创建本地 MCP 服务器（用于测试）
    server_path = create_local_mcp_server()

    # 连接本地 MCP 服务器
    from tools.mcp_tool import register_mcp_servers, _MCP_AVAILABLE
    if _MCP_AVAILABLE:
        local_tools = register_mcp_servers({
            "calc_server": {
                "command": sys.executable,
                "args": [str(server_path)],
                "timeout": 30,
            },
        })
        if local_tools:
            print(f"\n✅ 本地计算器 MCP 工具已注册: {local_tools}")

    # 初始化 Agent（自动加载 config.yaml 中的 MCP 配置）
    from run_agent import AIAgent

    agent = AIAgent(
        provider="openai",
        model="gpt-4o-mini",
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("OPENAI_API_KEY", ""),
        # MCP 工具自动注册到 mcp-<server_name> 工具集
        # 可通过 toolsets 参数启用，或通过 mcp_servers 配置启用
        toolsets=["mcp-filesystem", "mcp-calc_server"],
    )

    # 检查 MCP 工具是否可用
    from tools.registry import registry
    mcp_tools = [
        t for t in registry.get_registered_toolset_names()
        if t.startswith("mcp-")
    ]
    print(f"\n=== 已注册的 MCP 工具集: {mcp_tools} ===")
    for t in mcp_tools:
        print(f"  [{t}]: {registry.get_tool_names_for_toolset(t)}")

    # 与 Agent 对话（Agent 会自动调用 MCP 工具）
    print("\n=== Agent 对话测试 ===")
    print("（确保已配置 OPENAI_API_KEY 且本地 MCP 服务器可运行）")

    # 发送消息
    response = agent.chat("帮我计算 2 的 20 次方，再计算 sin(pi/4) 的值")
    print(f"Agent: {response}")


if __name__ == "__main__":
    main()
```

## 逐步解释

### MCP 传输协议

hermes-agent 支持三种 MCP 传输方式：

| 传输方式 | 配置方式 | 适用场景 |
|---------|---------|---------|
| **stdio** | `command` + `args` | 本地子进程，最常用。启动 MCP 服务器进程，通过 stdin/stdout 通信 |
| **HTTP** | `url`（默认） | 远程 HTTP 服务，支持 StreamableHTTP 协议 |
| **SSE** | `url` + `transport: sse` | 使用 Server-Sent Events 的远程服务，适合单向流式推送 |

### 方式一：config.yaml 配置

在 `~/.hermes/config.yaml` 中添加 `mcp_servers` 配置段，hermes-agent 启动时会自动：
1. 读取 `mcp_servers` 字典
2. 并行连接所有服务器（带指数退避重试）
3. 发现每个服务器提供的工具列表
4. 将工具注册为 `mcp__<server>__<tool>` 格式到 `mcp-<server>` 工具集
5. 在 Agent 调用工具时，通过对应传输协议转发请求

### 方式二：编程连接

调用 `register_mcp_servers(servers_dict)` 函数：
- 幂等操作：重复调用不会产生重复连接
- 并行连接：多个服务器同时连接
- 自动重试：连接失败时指数退避重试（最多 5 次）
- 返回值：所有已注册的 MCP 工具名列表
- 服务器故障冷却：连接失败的服务器进入冷却期，避免重启风暴

### 方式三：创建 MCP 服务器

使用 `mcp` 包的 `FastMCP` 类快速创建 MCP 服务器：
- `@mcp.tool()` 装饰器注册工具函数
- `@mcp.resource()` 装饰器注册可访问资源
- `mcp.run(transport="stdio")` 以 stdio 模式启动
- 函数的 docstring 和类型注解自动生成 MCP Schema

### MCP 工具命名

MCP 工具注册后命名格式为 `mcp__<server_name>__<tool_name>`：
- 例如 filesystem 服务器的 `read_file` 工具 → `mcp__filesystem__read_file`
- 工具集名为 `mcp-<server_name>`，如 `mcp-filesystem`
- 可通过 `toolsets=["mcp-filesystem"]` 批量启用

### 配置参数详解

```yaml
mcp_servers:
  server_name:
    # 传输配置（二选一）
    command: "npx"           # stdio: 启动命令
    args: ["-y", "..."]      # stdio: 命令参数
    url: "https://..."       # HTTP/SSE: 服务器URL
    transport: "sse"         # 可选，指定 "sse" 或默认 "http"

    # 环境变量（stdio）
    env:
      API_KEY: "..."
    cwd: "/path/to/dir"      # 工作目录

    # 超时配置
    timeout: 300             # 工具调用超时（秒），默认 300
    connect_timeout: 60      # 初始连接超时（秒），默认 60
    keepalive_interval: 180  # 心跳间隔（秒），默认 180

    # 生命周期管理（stdio）
    idle_timeout_seconds: 3600   # 空闲回收时间（0=禁用）
    max_lifetime_seconds: 86400  # 最大生命周期（0=禁用）

    # 并行调用
    supports_parallel_tool_calls: false  # 是否允许并行调用

    # HTTP 专用
    headers: {}               # 请求头
    identity_header:          # 用户身份头
      name: "X-User-Id"
      value_from: "static"    # "static" 或 "profile"
      value: "user123"
    skip_preflight: false     # 跳过 content-type 预检

    # 启用/禁用
    enabled: true             # 默认 true，设为 false 跳过连接
    lazy: false               # 懒启动：使用 schema 缓存，首次调用时才连接
```

## 输出结果

运行脚本后，预期输出类似：

```
=== Hermes-Agent MCP 服务器连接示例 ===

🔌 正在连接 MCP 服务器...
⚠️  MCP SDK 未安装或服务器未启动，跳过远程连接
✅ 本地 MCP 服务器代码已保存: /path/to/my_mcp_server.py
   可通过以下方式连接:
   command: /usr/bin/python3
   args: ['/path/to/my_mcp_server.py']

（安装 mcp SDK 并运行本地服务器后）:
✅ 本地计算器 MCP 工具已注册: ['mcp__calc_server__add', 'mcp__calc_server__calculate_expression', 'mcp__calc_server__get_server_info']

=== 已注册的 MCP 工具集: ['mcp-calc_server'] ===
  [mcp-calc_server]: ['mcp__calc_server__add', 'mcp__calc_server__calculate_expression', 'mcp__calc_server__get_server_info']

=== Agent 对话测试 ===
Agent: 2的20次方是 1,048,576。sin(π/4) = √2/2 ≈ 0.7071。
```

## 注意事项

1. **MCP SDK 依赖**：MCP 功能需要安装 `mcp` Python 包。如果未安装，`_MCP_AVAILABLE` 为 `False`，所有 MCP 相关功能静默跳过（debug 日志记录）。使用 `pip install mcp` 安装。

2. **stdio 服务器的 stderr 处理**：stdio MCP 子进程的 stderr 默认重定向到 `~/.hermes/logs/mcp-stderr.log`，避免污染终端 UI。每个服务器启动时写入时间戳标记，便于调试。

3. **凭证安全**：MCP 服务器配置中的环境变量（如 API Key）在错误消息中会被自动脱敏，不会泄露给 LLM。`env` 中的 key 名含 `KEY`/`TOKEN`/`SECRET`/`PASSWORD` 的值会在日志中掩码。

4. **并行调用**：设置 `supports_parallel_tool_calls: true` 允许同一服务器的工具被并发调用。仅在 MCP 服务器确实支持并发请求时启用，否则可能导致竞态条件。

5. **生命周期管理**：stdio 服务器可配置 `idle_timeout_seconds` 和 `max_lifetime_seconds` 实现自动回收。长时间空闲的服务器进程会被终止，下次调用时自动重启，防止资源泄漏。

6. **懒启动模式**：设置 `lazy: true` 可启用懒启动——服务器在首次工具调用时才实际连接，启动时使用缓存的 schema 注册工具。首次启动速度快，但首次调用有连接延迟。

7. **连接故障处理**：连接失败的服务器进入 60 秒冷却期（可通过 `/mcp refresh` 命令手动清除），避免每次会话都重试失败的服务器导致雪崩。瞬态故障（如网络超时）在 60 秒宽限期内被抑制，不会立即移除工具。

8. **工具更新通知**：MCP 服务器发送 `notifications/tools/list_changed` 时，hermes-agent 会自动 deregister 旧工具并重新发现新工具，无需重启进程。

9. **OSV 恶意软件检查**：stdio MCP 服务器启动前会进行 OSV 恶意软件预检查（12 秒超时，失败放行），降低供应链风险。
