---
type: example
title: "接入 MCP 服务器"
description: "在 dsh 中挂载外部 MCP 服务器：cordis.patch.yml 配置样例、stdio 与 streamable-http 两种传输、工具命名空间与资源工具的使用。"
tags: [deepseek-harness, mcp, example, integration]
generated: { by: "process:seven-concepts-cmd+source-code-to-okf-wiki", at: "2026-10-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-22T00:00:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: dsh-upstream
    resource: https://github.com/deepseek-ai/deepseek-harness
    title: DeepSeek Harness 官方仓库 docs/subsystems/mcp.zh.md 与 docs/user/guide/mcp-memory
---

# 接入 MCP 服务器

> 场景：把外部 MCP 服务器（记忆库、数据库、内部 API）的能力接进 dsh，模型就能像用内置工具一样调用它们。

## 1. 配置样例（stdio 传输）

MCP 客户端条目通过 `cordis.patch.yml` 插入。base bundle 已经统一挂载过一次客户端，这里再加一个服务器实例：

```yaml
- insert:
    - id: memory-my-server
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: my-memory
        transport: stdio
        command: my-memory-mcp
        args: []
        env: {}
        cwd: !!js process.cwd()
```

启动时带上 patch：

```sh
dsh web --patch "$PWD/apps/cli/config/examples/mcp-memory/memorix.cordis.yml"
```

## 2. HTTP 传输

```yaml
- insert:
    - id: my-remote-mcp
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: my-remote
        transport: streamable-http
        url: https://mcp.example.com/sse
        headers:
          Authorization: !!js process.env.MCP_TOKEN
```

> 记住 patch 的语义：**替换目标行的整个 `config`，不做深度合并**（见 [Profile 与组合包](../concepts/03-profile-and-bundle.md)）。这里用的是 `insert` 新增行，因此不受影响；若要改已有行，必须把所有想保留的键重述一遍。

## 3. 工具如何暴露

- 工具以 `mcp__<serverName>__<tool>` 命名空间暴露给模型
- 客户端级审批复用 `approval/*`——即 MCP 工具的高危参数同样走 dsh 的审批链
- 资源（resources）通过 `list_mcp_resources` / `list_mcp_resource_templates` / `read_mcp_resource` 三个工具访问
- 资源工具走常规 `tool/call` / `tool/result` 管线，因此同样受作用域限制与沙箱约束

## 4. 关键配置项

| 字段 | 默认 | 说明 |
|---|---|---|
| `serverName` | — | 工具命名空间前缀 |
| `transport` | — | `stdio` 或 `streamable-http` |
| `command` / `args` / `env` / `cwd` | — | stdio 传输用 |
| `url` / `headers` | — | HTTP 传输用 |
| `toolCallTimeoutMs` | — | 单次工具调用超时 |
| `failOnStartupError` | — | 启动失败是否致命 |
| `maxInstructionBytes` | 32768 | 服务器指令体上限 |
| `reconnect.enabled` | — | 自动重连 |
| `reconnect.initialDelayMs` | 500 | 首次重连延迟 |
| `reconnect.maxDelayMs` | 30000 | 退避上限 |
| `reconnect.maxAttempts` | 10 | 最大重试次数 |

## 5. 排查

```sh
# 看 MCP 客户端最终配置成什么样
dsh --profile web --patch ./my-mcp.yml --dump-config

# 看模型实际拿到的工具列表（概念 + 示例页里的工具目录同源）
# docs/tool-catalog.zh.md 由 gen-tool-catalog.ts 实际启动插件生成
```

常见问题：

1. **工具没出现**——检查 patch 行是否插到了正确的 profile；`dsh --dump-config` 确认行确实存在
2. **命名空间不对**——`serverName` 变了，工具前缀就变；模型提示词里若硬编码了旧前缀会失效
3. **stdio 起不来**——`command` 必须在 PATH 上，且 `cwd` 正确；MCP 进程的标准输出**必须只承载协议帧**

## 相关

- [能力 seam 与子系统地图](../concepts/08-capability-seams.md)
- [安全模型](../concepts/09-security-model.md)
