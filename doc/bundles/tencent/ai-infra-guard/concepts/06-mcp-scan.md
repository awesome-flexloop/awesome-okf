---
type: Concept
title: MCP 安全扫描
description: AIG 内置 Go 原生 MCP 扫描器（internal/mcp）支持 stdio/SSE/Streamable HTTP 三种传输协议，结合静态规则和 LLM 动态分析检测 MCP 插件的 SSRF、SQL 注入、路径遍历、工具投毒等漏洞。
tags: [ai-infra-guard, mcp, security, scanner, plugin, llm]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: python
    resource: /references/python-subsystems.md
    title: Python 子系统信源
  - id: data-rules
    resource: /references/data-rules.md
    title: 数据文件与规则格式信源
---

## 概述

MCP（Model Context Protocol）是 AI Agent 与外部工具通信的开放协议。AIG 对 MCP 生态提供两层安全扫描能力：

1. **Go 原生扫描器**（`internal/mcp/`）— 连接 MCP Server，枚举工具，使用规则 + LLM 分析工具定义和行为
2. **Python mcp-scan 子系统** — 对 MCP 插件代码进行深度静态审计和动态行为测试

两者通过 `Mcp-Scan` 任务类型统一调度，根据输入类型（URL vs 代码）选择执行路径。

## Go 原生 MCP 扫描器

### Scanner 结构

```go
type Scanner struct {
    mutex         sync.Mutex
    results       []*Issue
    PluginConfigs []*PluginConfig
    aiModel       *models.OpenAI
    client        *client.Client
    csvResult     [][]string
    codePath      string
    url           string
    callback      func(data interface{})
    language      string
    logger        *gologger.Logger
}
```

### 支持的传输方式

| 方法 | 传输协议 | MCP SDK 客户端 |
|------|---------|---------------|
| `InputCommand(ctx, command, argv)` | stdio | `client.NewStdioMCPClient` |
| `InputSSELink(ctx, link)` | SSE | `client.NewSSEMCPClient` |
| `InputStreamLink(ctx, link)` | Streamable HTTP | `client.NewStreamableHttpClient` |
| `InputUrl(ctx, url)` | 自动探测 | 依次尝试 "", "/mcp", "/sse" |

`InputUrl` 对给定 URL 尝试三个路径：
1. 根路径（Streamable HTTP）
2. `/mcp`（Streamable HTTP）
3. `/sse`（SSE）

任一成功即返回，全部失败则返回最后一个错误。

### PluginConfig（插件规则）

```go
type PluginConfig struct {
    Info struct {
        ID          string   `yaml:"id"`
        Name        string   `yaml:"name"`
        Description string   `yaml:"description"`
        Author      string   `yaml:"author"`
        Category    []string `yaml:"categories"`
    } `yaml:"info"`
    Rules          []Rule `yaml:"rules,omitempty"`
    PromptTemplate string `yaml:"prompt_template"`
}

type Rule struct {
    Name        string `yaml:"name"`
    Pattern     string `yaml:"pattern"`
    Description string `yaml:"description"`
}
```

规则从 `data/mcp/` 目录的 YAML 文件加载，当前内置 15 个规则文件，覆盖：

| 规则文件 | 检测目标 |
|---------|---------|
| `cors.yaml` | CORS 配置错误 |
| `mcp_ssrf.yaml` | 服务端请求伪造 |
| `mcp_sql_injection.yaml` | SQL 注入 |
| `mcp_path_traversal.yaml` | 路径遍历 |
| `mcp_tool_rug_pull.yaml` | 工具恶意行为（Rug Pull） |
| `tool_poisoning.yaml` | 工具投毒攻击 |

### Issue（漏洞结果）

```go
type Issue struct {
    Title       string `json:"title"`
    Description string `json:"description"`
    Level       Level  `json:"level"`
    Suggestion  string `json:"suggestion"`
    RiskType    string `json:"risk_type"`
}
```

威胁级别：

```go
const (
    LevelLow      Level = "low"
    LevelMedium   Level = "medium"
    LevelHigh     Level = "high"
    LevelCritical Level = "critical"
)
```

### LLM 结果解析

`ParseIssues(input string)` 从 LLM 输出中提取结构化漏洞：

```go
var (
    blockRegex    = regexp.MustCompile(`(?s)<result>(.*?)</result>`)
    titleRegex    = regexp.MustCompile(`<title>(.*?)</title>`)
    descRegex     = regexp.MustCompile(`(?s)<desc>(.*?)</desc>`)
    levelRegex    = regexp.MustCompile(`<level>(.*?)</level>`)
    riskTypeRegex = regexp.MustCompile(`<risk_type>(.*?)</risk_type>`)
    suggesRegex   = regexp.MustCompile(`(?s)<suggestion>(.*?)</suggestion>`)
)
```

LLM 被要求将结果包裹在 `<arg>` 和 `<result>` XML 标签中，每个 result 包含 title/desc/level/risk_type/suggestion。

### 扫描流程

1. `NewScanner(aiConfig, logger)` 创建扫描器
2. `RegisterPlugin(plugins)` 加载 data/mcp/ 规则
3. `InputUrl`/`InputCommand`/`InputCodePath` 指定目标
4. 使用 `github.com/mark3labs/mcp-go` 连接 MCP Server
5. 枚举工具列表，与 PluginConfig 规则匹配
6. LLM 分析工具定义和行为
7. `SummaryResult` 调用 LLM 生成最终漏洞总结
8. `ParseIssues` 解析为结构化 Issue 列表

## Python mcp-scan 子系统

当 McpTask 以 **code 模式** 运行时（上传代码包或 GitHub URL），Go Agent 调用 Python `mcp-scan/main.py` 进行深度代码审计。

### 目录结构

```
mcp-scan/
├── main.py
├── mcp_scan/
│   ├── agent/           # AI Agent 实现
│   │   ├── base_agent.py
│   │   └── agent.py
│   ├── prompt/          # Prompt 模板
│   │   ├── code_audit.md
│   │   ├── vuln_review.md
│   │   ├── dynamic_verification.md
│   │   └── agents/dynamic/
│   ├── redteam/         # 红队测试模块
│   │   ├── attacker.py
│   │   ├── evaluator.py
│   │   ├── orchestrator.py
│   │   ├── strategy.py
│   │   └── target.py
│   ├── tools/           # Agent 工具集
│   │   ├── execute/     # 命令执行
│   │   ├── file/        # 文件读写
│   │   ├── mcp_tool/    # MCP 工具调用
│   │   ├── thinking/    # 思考工具
│   │   ├── finish/      # 任务完成
│   │   ├── dispatcher.py
│   │   └── registry.py
│   └── utils/           # 工具函数
```

### code 模式扫描阶段

3 步任务计划：
1. **信息收集** — 解析项目结构、依赖、MCP 工具定义
2. **代码审计** — LLM 逐文件分析，识别危险模式
3. **漏洞整理** — 汇总、去重、评级，生成报告

### url 模式扫描阶段

4 步任务计划：
1. **信息收集** — 连接 MCP Server，枚举工具
2. **恶意行为检测** — 调用工具观察副作用
3. **漏洞检测** — 构造恶意输入测试注入/SSRF 等
4. **漏洞整理** — 汇总验证结果

### Agent 工具架构

Python mcp-scan 的 Agent 可以使用以下工具：
- `execute` — 在沙箱中执行 shell 命令
- `file` — read_file / write_file 操作项目文件
- `mcp_tool` — 调用目标 MCP Server 的工具
- `thinking` — 结构化思考输出
- `finish` — 标记任务完成

工具通过 `registry.py` 注册，`dispatcher.py` 统一调度。

## 两种扫描路径的选择

```
McpTask.Execute()
  │
  ├─ 有附件 或 content 含 github.com？
  │    ├─ 是 → code 模式
  │    │       ├─ 下载/解压/clone 代码
  │    │       ├─ uv run main.py --repo <path>
  │    │       └─ Python mcp-scan 代码审计
  │    │
  │    └─ 否 → url 模式
  │            ├─ 正则提取 URL
  │            ├─ uv run main.py --server_url <url>
  │            └─ Python mcp-scan 动态测试
```

Go 原生 `internal/mcp.Scanner` 主要用于库调用和 CLI 直接扫描场景，在 Web 任务流程中实际执行由 Python 子系统完成。

## MCPType 输入类型

```go
type MCPType string

const (
    MCPTypeCommand MCPType = "command"  // stdio 命令行启动
    MCPTypeSSE     MCPType = "sse"      // SSE 远程连接
    MCPTypeSTREAM  MCPType = "stream"   // Streamable HTTP
    MCPTypeCode    MCPType = "code"     // 代码路径审计
)
```

## 相关概念

- [四种任务类型](/concepts/01-task-types.md)
- [Go/Python 桥接](/concepts/05-python-bridge.md)
- [数据文件格式](/references/data-rules.md)
- [Python 子系统信源](/references/python-subsystems.md)
