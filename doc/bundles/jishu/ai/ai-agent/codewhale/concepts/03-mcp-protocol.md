---
type: Concept
title: "MCP 协议集成"
description: "mcp crate 实现 MCP 服务器生命周期管理和工具代理，包含 McpServerConfig、ToolFilter、限定名安全折叠和调用时过滤等安全机制。"
tags: [codewhale, mcp, protocol, json-rpc, tool-filter, stdio, security]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# MCP 协议集成

`codewhale-mcp` crate 描述为 "MCP server lifecycle and tool proxy compatibility"，负责管理 MCP（Model Context Protocol）服务器连接的生命周期，并在工具代理兼容性之外解决了三个实际安全问题：限定名碰撞、过滤器绕过和失败重试导致的重复副作用。

## McpServerConfig

单个 MCP 服务器进程的配置定义在 `crates/mcp/src/lib.rs`：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct McpServerConfig {
    pub name: String,
    pub command: String,
    #[serde(default)]
    pub args: Vec<String>,
    #[serde(default)]
    pub env: HashMap<String, String>,
    #[serde(default = "default_true")]
    pub enabled: bool,
}
```

字段说明：
- `name`：唯一服务器标识符，用于工具名限定
- `command`：服务器可执行文件的路径或名称
- `args`：传递给服务器进程的命令行参数
- `env`：为服务器进程设置的环境变量
- `enabled`：是否启动此服务器，默认为 `true`

完整的服务器定义还包括工具过滤器：

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct McpServerDefinition {
    pub config: McpServerConfig,
    #[serde(default)]
    pub filter: ToolFilter,
}
```

## ToolFilter

`ToolFilter` 使用 allow/deny 列表控制暴露哪些工具：

```rust
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ToolFilter {
    #[serde(default)]
    pub allow: Vec<String>,
    #[serde(default)]
    pub deny: Vec<String>,
}
```

过滤规则：
- **deny 优先于 allow**
- 空 `allow` 表示暴露所有工具（除非被 deny）
- 过滤器在**调用时**强制执行，而不仅仅在列出时

过滤逻辑实现：

```rust
fn allowed_by_filter(name: &str, filter: &ToolFilter) -> bool {
    if filter.deny.iter().any(|pattern| pattern == name) {
        return false;
    }
    if filter.allow.is_empty() {
        return true;
    }
    filter.allow.iter().any(|pattern| pattern == name)
}
```

被 deny 的工具无法通过直接寻址执行——客户端不能绕过 list 直接构造限定名调用被过滤的工具。

## McpManagedClient Trait

MCP 客户端连接的抽象 trait：

```rust
pub trait McpManagedClient: Send + Sync {
    fn list_tools(&self) -> Result<Vec<McpToolDescriptor>>;
    fn call_tool(&self, tool_name: &str, arguments: Value) -> Result<Value>;
    fn list_resources(&self) -> Result<Vec<McpResourceDescriptor>>;
    fn read_resource(&self, uri: &str) -> Result<Value>;
}
```

实现包括：
- `ChildProcessMcpClient`：通过 stdio 通信的子进程 MCP 客户端
- `InMemoryMcpClient`：用于测试和嵌入式调用的内存客户端

MCP 工具描述符：

```rust
pub struct McpToolDescriptor {
    pub server_name: String,
    pub tool_name: String,
    pub qualified_name: String,
    pub description: Option<String>,
}
```

## McpManager

`McpManager` 管理多个 MCP 服务器连接，内部使用两个 HashMap：

```rust
#[derive(Default)]
pub struct McpManager {
    configs: HashMap<String, (McpServerConfig, ToolFilter)>,
    clients: HashMap<String, Box<dyn McpManagedClient>>,
}
```

### 服务器注册与名称碰撞检测

`register_server` 方法在注册时检测经过 `sanitize_component` 折叠后的名称碰撞：

```rust
pub fn register_server(
    &mut self,
    config: McpServerConfig,
    filter: ToolFilter,
    client: Box<dyn McpManagedClient>,
) -> Result<()> {
    if let Some(existing) = self.colliding_server_name(&config.name) {
        bail!(
            "MCP server '{}' collides with already-registered server '{existing}': \
             both qualify tools as 'mcp__{}__*'",
            config.name,
            sanitize_component(&config.name)
        );
    }
    self.clients.insert(config.name.clone(), client);
    self.configs.insert(config.name.clone(), (config, filter));
    Ok(())
}
```

碰撞检测逻辑：

```rust
fn colliding_server_name(&self, name: &str) -> Option<&str> {
    let sanitized = sanitize_component(name);
    self.configs
        .keys()
        .find(|existing| existing.as_str() != name && sanitize_component(existing) == sanitized)
        .map(String::as_str)
}
```

### 限定名安全

限定名格式为 `mcp__<server>__<tool>`。`sanitize_component` 将 `-`、`.`、非字母数字字符折叠为 `_` 并小写化：

```rust
fn sanitize_component(value: &str) -> String {
    value
        .chars()
        .map(|ch| {
            if ch.is_ascii_alphanumeric() || ch == '_' {
                ch.to_ascii_lowercase()
            } else {
                '_'
            }
        })
        .collect()
}
```

这意味着 `my-server`、`my_server`、`My.Server` 全部限定为 `mcp__my_server__*`。如果注册两个这样的服务器，HashMap 迭代顺序将决定哪个服务器响应调用——这是一个非确定性的安全漏洞，因此注册时会拒绝碰撞名称。

超过 64 字符的限定名使用哈希截断：

```rust
fn qualify_tool_name(server: &str, tool: &str) -> String {
    let server = sanitize_component(server);
    let tool = sanitize_component(tool);
    let mut name = format!("mcp__{server}__{tool}");
    if name.len() > 64 {
        let mut hasher = DefaultHasher::new();
        name.hash(&mut hasher);
        let hash = format!("{:x}", hasher.finish());
        let suffix = format!("_{}", &hash[..12]);
        // ... 截断并附加哈希后缀
    }
    name
}
```

### 工具调用与防重放

`call_tool` 在调用时强制执行过滤器：

```rust
pub fn call_tool(&self, server_name: &str, tool_name: &str, arguments: Value) -> Result<Value> {
    let client = self.clients.get(server_name)
        .with_context(|| format!("MCP server '{server_name}' not available"))?;
    if let Some((_, filter)) = self.configs.get(server_name)
        && !allowed_by_filter(tool_name, filter)
    {
        bail!("tool '{tool_name}' on MCP server '{server_name}' is blocked by the tool filter");
    }
    client.call_tool(tool_name, arguments)
}
```

关键安全设计：**失败的 qualified tool call 不会被重试**。`call_qualified_tool` 的快速路径在调用失败时直接返回错误，不 fall through 到扫描循环——这防止文件写入、提交或付费 API 被执行两次。

### 生命周期管理

McpManager 提供完整的服务器生命周期方法：
- `register_server`：注册服务器配置和客户端
- `start_all`：启动所有已注册服务器，通过回调发出状态更新
- `stop_server`：停止运行中的服务器
- `unregister_server`：完全移除服务器
- `list_tools`：列出所有运行中服务器的工具（应用过滤器）
- `call_tool` / `call_qualified_tool`：调用工具

启动状态通过 `McpStartupStatus` 枚举报告：

```rust
#[serde(rename_all = "snake_case")]
pub enum McpStartupStatus {
    Starting,
    Ready,
    Failed { error: String },
    Cancelled,
}
```

## stdio JSON-RPC 服务器

CodeWhale 可以自身作为 MCP stdio 服务器运行。TUI 中 `codewhale-tui serve --mcp` 运行 MCP stdio 服务器，`codewhale mcp-server` 是等价的 dispatcher 入口。

stdio JSON-RPC 服务器支持 13 个方法：

| 方法 | 说明 |
|------|------|
| `initialize` | 初始化连接 |
| `healthz` | 健康检查 |
| `capabilities` | 查询服务器能力 |
| `tools/list` | 列出工具 |
| `tools/call` | 调用工具 |
| `resources/list` | 列出资源 |
| `resources/read` | 读取资源 |
| `server/list` | 列出已注册服务器 |
| `server/register` | 注册新服务器 |
| `server/start` | 启动服务器 |
| `server/stop` | 停止服务器 |
| `server/unregister` | 注销服务器 |
| `shutdown` | 关闭服务器 |

JSON-RPC 请求结构：

```rust
#[derive(Debug, Deserialize)]
struct JsonRpcRequest {
    #[serde(default)]
    jsonrpc: Option<String>,
    #[serde(default)]
    id: Option<Value>,
    method: String,
    #[serde(default)]
    params: Value,
}
```

## 插件 MCP 安全边界

插件贡献的 MCP 服务器使用更严格的审查边界：
- 未知字段失败关闭（`#[serde(deny_unknown_fields)]`）
- 远程 literal headers 被拒绝
- 声明的网络主机必须精确匹配

这是设计有意为之——插件捆绑的 MCP 服务器比用户 `mcp.json` 配置的服务器受到更严格的验证。

## 相关概念

- [Agent 核心运行时](02-agent-core.md) — Runtime 中的 mcp_manager 组件
- [工具系统](04-tool-system.md) — ToolRegistry 与 MCP 工具集成
- [Fleet 多 Agent](05-fleet-subagents.md) — 子 agent 继承工具注册表
- [沙箱与执行策略](07-sandbox-execpolicy.md) — MCP 工具调用的权限控制
- [CodeWhale 简介](00-introduction.md) — 项目概述
