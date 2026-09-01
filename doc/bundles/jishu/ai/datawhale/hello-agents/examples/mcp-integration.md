---
title: MCP协议集成实战
type: example
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/communication-protocols
  - /datawhale/hello-agents/concepts/multi-agent-collaboration
  - /datawhale/hello-agents/references/chapter10-communication-protocols
sources:
  - https://github.com/datawhalechina/hello-agents/tree/main/code/chapter10
---

# MCP协议集成实战

本示例展示如何在HelloAgents框架中使用MCP（Model Context Protocol）协议，包括连接MCP服务器、使用MCP工具、以及多Agent通过A2A协议协作。

## 代码位置

完整代码位于 `code/chapter10/` 目录，包含14个递进式示例：

| 文件 | 内容 |
|------|------|
| `01_TestConnect.py` | 测试LLM连接 |
| `02_Connect2MCP.py` | 连接MCP服务器基础 |
| `03_GitHubMCP.py` | GitHub MCP服务器使用 |
| `04_MCPTransport.py` | MCP传输层（stdio/SSE） |
| `05_UseMCPToolInAgent.py` | 在Agent中使用MCP工具 |
| `06_MultiAgentDocumentAssist.py` | 多Agent文档助手 |
| `07_SimpleA2AAgent.py` | 简单A2A Agent |
| `08_CustomA2AAgent.py` | 自定义A2A Agent |
| `09_A2A_Client/Server/Network.py` | A2A客户端/服务器/网络 |
| `10_A2ATool_Simple.py` | A2A工具封装 |
| `10_AgentNegotiation.py` | Agent协商 |
| `10_CustomerService.py` | 客服场景 |
| `11_ANPInit.py` | ANP初始化 |
| `12_ANPTaskDistribution.py` | ANP任务分发 |
| `13_ANPLoadBalancing.py` | ANP负载均衡 |
| `14_weather_mcp_server.py` | 天气MCP服务器实现 |

## 连接MCP服务器

```python
from hello_agents.tools import MCPTool

# 连接内置MCP服务器
mcp_tool = MCPTool()

# 连接外部MCP服务器（如GitHub）
github_mcp = MCPTool(
    server_command=["npx", "-y", "@modelcontextprotocol/server-github"]
)

# 连接自定义Python MCP服务器
weather_mcp = MCPTool(
    server_command=["python", "weather_mcp_server.py"]
)

# Agent自动获得所有MCP工具能力
agent.add_tool(mcp_tool)
agent.add_tool(github_mcp)
```

MCP的价值：无需为每个外部服务手写Tool适配器，连接MCP服务器即可自动发现和使用其提供的所有工具。

## 天气MCP服务器示例

`weather_mcp_server.py` 展示了如何构建自定义MCP服务器：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
def get_weather(location: str) -> str:
    """获取指定城市的天气信息"""
    # 调用天气API或返回模拟数据
    return f"{location}今天晴，气温25°C"

@mcp.tool()
def get_forecast(location: str, days: int = 3) -> str:
    """获取未来几天的天气预报"""
    return f"{location}未来{days}天天气预报..."

if __name__ == "__main__":
    mcp.run()
```

使用 `@mcp.tool()` 装饰器即可将普通Python函数暴露为MCP工具，Agent连接后自动获得函数签名和文档。

## 多Agent文档助手

`06_MultiAgentDocumentAssist.py` 展示了多Agent协作模式：
- 一个Agent负责文档检索（通过MCP访问文件系统）
- 一个Agent负责内容分析
- 通过消息传递协作完成文档问答

## A2A协议使用

A2A实现Agent间对等通信：

```python
# Agent A作为服务器暴露能力
# Agent B作为客户端调用A的能力
# 双方都可以主动发起请求和响应
```

`10_CustomerService.py` 展示了客服场景：
- 前台Agent接收用户问题
- 根据问题类型委派给专门的技术支持或账单Agent
- 各Agent通过A2A通信，用户获得统一回复

## ANP协议概念

ANP示例（11-13）展示了大规模Agent网络的概念：
- 服务注册：Agent在网络中注册自己的能力
- 服务发现：Agent动态发现可用的服务提供者
- 任务分发：根据能力和负载分配任务
- 负载均衡：在多个等价Agent间分配请求

## 三层架构在HelloAgents中的实现

```
协议实现层：FastMCP / a2a-sdk / 自研ANP
    ↓
工具封装层：MCPTool / A2ATool / ANPTool（均继承BaseTool）
    ↓
智能体集成层：agent.add_tool(xxx_tool) 统一注册
```

这种设计让Agent以完全相同的方式使用三种不同协议——都是Tool接口的`run()`方法，体现了"万物皆工具"的设计哲学。
