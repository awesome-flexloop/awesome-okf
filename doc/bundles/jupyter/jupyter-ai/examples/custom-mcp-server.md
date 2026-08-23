---
type: Example
title: 配置自定义 MCP 服务器
description: 为 Jupyter AI 配置自定义 MCP 服务器，扩展 AI Agent 的工具能力
tags: [example, mcp, configuration, tools, extension]
sources:
  - id: mcp-config
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/mcp_config.md
    title: mcp_config.md
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 配置自定义 MCP 服务器

本示例展示如何通过 `mcp_settings.json` 配置自定义 MCP 服务器，为 AI Agent 添加文件系统访问、GitHub 操作、数据库查询等额外能力。

## 前提条件

- Jupyter AI 已安装并正常运行
- Node.js 已安装（用于运行 npm 包形式的 MCP 服务器）
- 了解 [MCP 协议基础](../concepts/04-protocols-acp-mcp.md)

## 配置文件格式

Jupyter AI 使用 `mcp_servers` 数组格式，每个服务器配置包含 `name`、`command`/`url`、`args`、`env`/`headers` 等字段。Stdio 服务器不需要 `type` 字段，HTTP 服务器必须声明 `"type": "http"`。

## 步骤 1：创建配置文件

### 找到 Jupyter 配置目录

| 操作系统 | 配置目录路径 |
|---|---|
| macOS/Linux | `~/.jupyter/` |
| Windows | `%USERPROFILE%\.jupyter\` |

如果目录中没有 `mcp_settings.json` 文件，创建一个：

**macOS/Linux:**
```bash
mkdir -p ~/.jupyter
cat > ~/.jupyter/mcp_settings.json << 'EOF'
{
  "mcp_servers": []
}
EOF
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.jupyter" | Out-Null
@'
{
  "mcp_servers": []
}
'@ | Set-Content -Path "$env:USERPROFILE\.jupyter\mcp_settings.json"
```

## 示例 1：文件系统 MCP 服务器

文件系统 MCP 服务器让 AI 可以读写指定目录的文件。

### 配置

在 `mcp_settings.json` 中添加：

```json
{
  "mcp_servers": [
    {
      "name": "Filesystem Tools",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/workspace"
      ],
      "env": []
    }
  ]
}
```

将 `/path/to/your/workspace` 替换为你想让 AI 访问的目录路径（通常是 JupyterLab 的工作目录）。

### Windows 路径注意事项

Windows 路径使用正斜杠：

```json
{
  "mcp_servers": [
    {
      "name": "Filesystem Tools",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "D:/spaces/my-project"
      ],
      "env": []
    }
  ]
}
```

### 测试

1. 重启 JupyterLab
2. 创建新聊天，选择任意 Persona
3. 发送："列出工作目录中的文件"
4. AI 应该能调用文件系统工具列出文件

> 注意：首次调用会弹出权限请求，批准后 AI 才能访问文件。

## 示例 2：GitHub MCP 服务器

GitHub MCP 服务器让 AI 可以操作 GitHub Issues、PR、代码等。

### 准备工作

1. 创建 GitHub Personal Access Token：https://github.com/settings/tokens
2. 勾选必要的权限（repo、read:org 等）

### 配置

```json
{
  "mcp_servers": [
    {
      "name": "GitHub Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": [
        {"name": "GITHUB_PERSONAL_ACCESS_TOKEN", "value": "ghp_your_token_here"}
      ]
    }
  ]
}
```

### 测试

重启 JupyterLab 后，可以让 AI：
- "列出我最近的 GitHub Issues"
- "帮我查看 jupyterlab/jupyter-ai 仓库最近的 PR"
- "为这个仓库创建一个 Issue"

## 示例 3：多服务器配置

可以同时配置多个 MCP 服务器：

```json
{
  "mcp_servers": [
    {
      "name": "Filesystem Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
      "env": []
    },
    {
      "name": "GitHub Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": [
        {"name": "GITHUB_PERSONAL_ACCESS_TOKEN", "value": "ghp_your_token_here"}
      ]
    },
    {
      "name": "Brave Search",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": [
        {"name": "BRAVE_API_KEY", "value": "your_brave_api_key"}
      ]
    }
  ]
}
```

## 示例 4：HTTP MCP 服务器

如果有远程运行的 MCP 服务器（如企业内部工具服务）：

```json
{
  "mcp_servers": [
    {
      "type": "http",
      "name": "Internal Tools",
      "url": "https://tools.company.com/mcp",
      "headers": [
        {"name": "Authorization", "value": "Bearer your-auth-token"}
      ]
    }
  ]
}
```

注意 HTTP 服务器必须包含 `"type": "http"` 字段。

## 示例 5：Python 实现的本地 MCP 服务器

如果你想自己开发 MCP 服务器（用 Python），可以使用 `mcp` Python SDK：

### 创建 MCP 服务器

创建 `my_mcp_server.py`：

```python
"""一个简单的 Python MCP 服务器，提供计算器工具"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator")

@mcp.tool()
def calculate(expression: str) -> str:
    """计算数学表达式并返回结果。

    Args:
        expression: 数学表达式字符串，如 "2 + 3 * 4"
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

@mcp.tool()
def word_count(text: str) -> str:
    """统计文本的字数和词数。

    Args:
        text: 要统计的文本
    """
    chars = len(text)
    words = len(text.split())
    lines = len(text.splitlines())
    return f"字符数: {chars}, 词数: {words}, 行数: {lines}"

if __name__ == "__main__":
    mcp.run()
```

### 安装依赖

```bash
pip install mcp
```

### 配置到 mcp_settings.json

```json
{
  "mcp_servers": [
    {
      "name": "Calculator",
      "command": "python",
      "args": ["/path/to/my_mcp_server.py"],
      "env": []
    }
  ]
}
```

### 测试

重启 JupyterLab 后，发送："帮我计算 (15 + 27) * 3 的结果"，AI 应该调用 calculate 工具返回 126。

## 故障排查

### MCP 服务器不可用
1. 确认 `mcp_settings.json` 在正确的目录（`~/.jupyter/`）
2. 验证 JSON 格式正确（用 JSON 验证器检查）
3. 确认使用 `mcp_servers` 数组格式（不是 `servers` 对象）
4. 确认每个服务器配置有 `name` 字段
5. 确认 `command` 指向的程序存在且在 PATH 中
6. **重启 JupyterLab**——配置更改需要重启才能生效

### npx 命令失败
- 确认 Node.js 已安装：`node --version`
- 尝试清除 npx 缓存：`npx clear-npx-cache`
- 某些网络环境下可能需要配置 npm 镜像：`npm config set registry https://registry.npmmirror.com`

### AI 不使用自定义工具
- 确认服务器配置正确且已加载
- 尝试更明确的提示，如"使用 filesystem 工具读取 data.csv 文件"
- 检查权限设置是否阻止了工具调用
- 查看 JupyterLab 终端输出是否有错误信息

## 安全注意事项

1. **最小权限原则**：文件系统服务器只授予必要的目录访问权限
2. **API Key 安全**：不要将包含 API Key 的 mcp_settings.json 提交到版本控制
3. **审查第三方服务器**：使用社区 MCP 服务器前，了解它能做什么操作
4. **权限审批**：保持默认的权限审批模式，不要对危险操作设置"始终允许"

## 相关概念

- [自定义 MCP 服务器](../concepts/08-custom-mcp-servers.md)
- [MCP 工具与 Notebook 交互](../concepts/07-mcp-tools-and-notebooks.md)
- [ACP 与 MCP 双协议](../concepts/04-protocols-acp-mcp.md)
- [MCP 配置参考](../references/mcp-config-reference.md)
