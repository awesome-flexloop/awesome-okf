---
type: Concept
title: 五种任务类型
description: AIG 定义了 AI-Infra-Scan、Mcp-Scan、Model-Redteam-Report、Agent-Scan、Skill-Scan 五种任务类型，分别覆盖基础设施漏洞扫描、MCP 插件审计、大模型安全体检、Agent 安全评估和 Skill 安全扫描五个维度。
tags: [ai-infra-guard, tasks, scan, mcp, redteam, agent]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: go-server
    resource: /references/go-server.md
    title: Go WebSocket 与 HTTP Server 信源
  - id: python
    resource: /references/python-subsystems.md
    title: Python 子系统信源
---

## 任务类型常量

任务类型定义在 `common/agent/types.go` 中：

```go
const (
    TaskTypeAIInfraScan        = "AI-Infra-Scan"
    TaskTypeMcpScan            = "Mcp-Scan"
    TaskTypeModelRedteamReport = "Model-Redteam-Report"
    TaskTypeModelJailbreak     = "Model-Jailbreak"
    TaskTypeAgentScan          = "Agent-Scan"
    TaskTypeSkillScan          = "Skill-Scan"
    TaskTypeTestDemo           = "Test-Demo"
)
```

所有任务处理器实现 `TaskInterface` 接口：

```go
type TaskInterface interface {
    GetName() string
    Execute(ctx context.Context, request TaskRequest, callbacks TaskCallbacks) error
}
```

Agent 启动时通过 `RegisterTaskFunc` 注册处理器，Server 下发任务时按 `TaskType` 字段匹配。

## 1. AI-Infra-Scan（基础设施扫描）

**实现**：`common/agent/tasks.go` 中的 `AIInfraScanAgent`

**语言**：纯 Go（唯一不调用 Python 子进程的任务类型）

**功能**：对目标 IP/域名/URL 进行指纹识别和 CVE 漏洞匹配，可选 AI 截图分析未授权访问。

**任务计划**（3 步）：
1. 准备扫描环境
2. 执行深度扫描
3. 智能分析与报告生成

**关键参数**：
- `target` — 目标列表（从 Content 按换行分割）
- `headers` — 自定义 HTTP 头
- `timeout` — 请求超时（默认 30 秒）
- `model` — 可选 AI 模型配置（model/token/base_url）

**特殊能力**：
- 对纯 IP 目标自动调用 nmap 扫描端口 `11434,1337,7000-9000,18789`
- 支持从附件读取目标列表
- AI 模式下对每个目标进行浏览器截图 + LLM 未授权分析
- 并发 AI 分析受信号量限制（maxConcurrentAnalysis=5）
- 最终输出安全评分（0-100）和漏洞列表

## 2. Mcp-Scan（MCP 安全扫描）

**实现**：`common/agent/mcp_task.go` 中的 `McpTask`

**语言**：Go 调度 + Python `mcp-scan/` 子系统

**功能**：对 MCP（Model Context Protocol）服务器或 MCP 插件代码进行安全审计。

**两种传输模式**：

### code 模式
- 触发条件：有附件上传，或 Content 包含 `github.com`
- 支持 `.zip`/`.tar.gz`/`.tgz`/`.whl` 文件解压，或 git clone
- 命令参数：`--repo <folder>`
- 任务计划（3 步）：信息收集 → 代码审计 → 漏洞整理

### url 模式
- 触发条件：直接输入 MCP Server URL
- 从 Content 中正则提取 `https?://[^\s]+`
- 命令参数：`--server_url <url>`
- 任务计划（4 步）：信息收集 → 恶意行为检测 → 漏洞检测 → 漏洞整理

**关键参数**：
- `model` — LLM 配置（model/token/base_url）
- `headers` — 自定义 HTTP 头
- `language` — 输出语言（zh/en）

## 3. Model-Redteam-Report（大模型安全体检）

**实现**：`common/agent/prompt_tasks.go` 中的 `ModelRedteamReport`

**语言**：Go 调度 + Python `AIG-PromptSecurity/` 子系统

**功能**：对大语言模型进行自动化越狱测试和安全评测，支持多模型并行、多评测数据集。

**任务计划**（3 步）：
1. 初始化越狱环境
2. 执行模型安全评估
3. 生成模型安全报告

**Scenario 格式**：
- 单条 prompt：`Custom:prompt=<text>`
- 数据集：`MultiDataset:dataset_file=<path>,num_prompts=<n>,random_seed=<n>,prompt_column=<col>`

**关键参数**：
- `model` — 被测模型列表（支持多个并行）
- `eval_model` — 评判模型
- `datasets.dataFile` — 评测集名称（从 data/eval/ 加载）
- `datasets.numPrompts` — 采样数量（-1 表示全部）
- `datasets.randomSeed` — 随机种子（默认 42）
- `techniques` — 越狱技术列表（默认 Raw）

**评测模型来源**：优先使用环境变量 `eval_base_url`/`eval_api_key`/`eval_model`，否则使用请求参数中的 eval_model。

## 4. Agent-Scan（Agent 安全评估）

**实现**：`common/agent/agent_task.go` 中的 `AgentTask`

**语言**：Go 调度 + Python `agent-scan/` 子系统

**功能**：对 AI Agent 配置进行动态安全测试，评估其工具调用安全性和prompt注入抵抗力。

**任务计划**（3 步）：
1. Info Collection
2. Vulnerability Detection
3. Vulnerability Review

**关键参数**：
- `agent_data` — Agent Provider YAML 内容（Server 从知识库读取后注入）
- `eval_model` — 评判模型（model/token/base_url/limit）

Go 端将 agent_data 写入临时文件，通过 `--agent_provider` 参数传给 Python 子进程。

## 5. Skill-Scan（Skill 代码审计）

**实现**：`common/agent/skill_task.go` 中的 `SkillTask`

**语言**：Go 调度 + Python skill-scan 子系统

**功能**：对 Agent Skill 项目进行代码安全审计。结构与 Mcp-Scan 的 code 模式类似，但仅支持代码模式（附件或 GitHub URL）。

**任务计划**（3 步）：信息收集 → 代码审计 → 漏洞整理

## 任务结果格式

所有任务最终通过 `ResultCallback` 返回 `map[string]interface{}`，AI-Infra-Scan 的结果结构为：

```go
map[string]interface{}{
    "total":   len(advisories),
    "score":   score.SecScore,
    "results": scanResults,  // []CallbackScanResult
}
```

Python 子系统的结果通过 stdout JSON 行的 `resultUpdate` 类型返回，具体结构由各 Python 子系统定义。

## 任务标题生成

`TaskManager.generateTaskTitle` 根据任务类型和参数自动生成中文或英文标题：

| 任务类型 | 中文标题前缀 | 标题构成 |
|---------|------------|---------|
| AI-Infra-Scan | AI基础设施扫描 - | 附件名/目标内容 |
| Mcp-Scan | MCP扫描 - | 文件名/GitHub项目名/SSE链接 |
| Model-Jailbreak | 一键越狱任务 - | 模型名 + prompt |
| Model-Redteam-Report | 大模型安全体检 - | 模型名 |
| Agent-Scan | Agent安全扫描 - | agent_id + 内容 |
| Skill-Scan | Skill扫描 - | 文件名/GitHub项目名 |

## 相关概念

- [分布式架构总览](/concepts/00-architecture.md)
- [Go/Python 桥接](/concepts/05-python-bridge.md)
- [MCP 安全扫描](/concepts/06-mcp-scan.md)
- [WebSocket 通信协议](/concepts/04-websocket-protocol.md)
