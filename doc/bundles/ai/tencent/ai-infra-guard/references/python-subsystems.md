---
type: Reference
title: Python 子系统与 Go/Python 桥接信源
description: 记录 mcp-scan、agent-scan、AIG-PromptSecurity 三个 Python 子系统的目录结构、入口脚本、命令行参数及 stdout JSON 协议。
tags: [ai-infra-guard, python, bridge, mcp-scan, agent-scan, prompt-security]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-python
    resource: /references/python-subsystems.md
    title: Python 子系统与 Go/Python 桥接信源
---

## 源码路径

- `common/agent/mcp_task.go`
- `common/agent/agent_task.go`
- `common/agent/prompt_tasks.go`
- `common/agent/skill_task.go`
- `common/agent/parse_cmdline.go`
- `common/agent/tasks.go`
- `mcp-scan/`
- `agent-scan/`
- `AIG-PromptSecurity/`

## 桥接机制

所有 Python 子系统通过以下模式被 Go Agent 调用：

1. Go 端构造 `argv`，以 `uv run --no-project <entry.py>` 开头
2. 调用 `utils.RunCmdWithContext(ctx, workDir, uvBin, argv, callback)` 启动子进程
3. callback 逐行接收 stdout，调用 `ParseStdoutLine` 解析
4. Python 端输出 JSON 行，首字符为 `{`
5. 非 JSON 行直接 `fmt.Println` 透传

### ParseStdoutLine 协议

```go
func ParseStdoutLine(server, rootDir string, tasks []SubTask, line string,
    callbacks TaskCallbacks, config *CmdConfig, upload bool)
```

解析的 JSON 结构：

```go
type CmdContent struct {
    Type    string          `json:"type"`
    Content json.RawMessage `json:"content"`
}
```

支持的 `type` 值及对应内容结构：

| type | 结构 | 字段 |
|------|------|------|
| `newPlanStep` | `CmdNewPlanStep` | title, stepId |
| `statusUpdate` | `CmdStatusUpdate` | brief, description, stepId, status |
| `toolUsed` | `CmdToolUsed` | tool_id, tool_name, brief, status, stepId, params |
| `actionLog` | `CmdActionLog` | tool_id, tool_name, log, stepId |
| `resultUpdate` | `map[string]interface{}` | 任意结果数据 |
| `error` | `string` | 错误消息 |

当 `upload=true` 时，resultUpdate 中的 content 数组若含 `attachment` 字段，Go 端会调用 `utils.UploadFile` 上传文件并替换 URL。

## mcp-scan 子系统

### 目录结构

```
mcp-scan/
├── main.py                 # 入口脚本
├── pyproject.toml
├── requirements.txt
├── mcp_scan/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   └── agent.py
│   ├── prompt/
│   │   ├── agents/dynamic/
│   │   │   ├── general_analyzing_prompt_template.md
│   │   │   ├── malicious_behaviour_testing.md
│   │   │   ├── project_summary.md
│   │   │   ├── system_prompt.md
│   │   │   └── vulnerability_testing.md
│   │   ├── build_preview.md
│   │   ├── code_audit.md
│   │   ├── dynamic_verification.md
│   │   ├── mcp_opera.md
│   │   ├── project_summary.md
│   │   └── vuln_review.md
│   ├── redteam/
│   │   ├── __init__.py
│   │   ├── attacker.py
│   │   ├── evaluator.py
│   │   ├── orchestrator.py
│   │   ├── report.py
│   │   ├── strategy.py
│   │   └── target.py
│   ├── tools/
│   │   ├── execute/
│   │   ├── file/
│   │   ├── finish/
│   │   ├── mcp_tool/
│   │   ├── thinking/
│   │   ├── dispatcher.py
│   │   └── registry.py
│   └── utils/
│       ├── aig_logger.py
│       ├── config.py
│       ├── extract_vuln.py
│       ├── llm.py
│       ├── llm_manager.py
│       ├── mcp_tools.py
│       ├── parse.py
│       ├── pre_scan.py
│       ├── project_analyzer.py
│       ├── prompt_manager.py
│       ├── sarif_formatter.py
│       └── tool_context.py
└── testcase/
```

### Go 端调用参数（McpTask）

```
uv run --no-project main.py \
  --model <model> \
  --base_url <base_url> \
  --api_key <token> \
  --prompt <content> \
  --debug \
  --aig-mode \
  --language <zh|en> \
  [--header key:value ...] \
  [--repo <folder> | --server_url <url>]
```

两种模式：
- **code 模式**：有附件或 content 含 github.com → `--repo` 指定解压/clone 目录，3 步计划（信息收集、代码审计、漏洞整理）
- **url 模式**：直接输入 MCP Server URL → `--server_url`，4 步计划（信息收集、恶意行为检测、漏洞检测、漏洞整理）

## agent-scan 子系统

### 目录结构

```
agent-scan/
├── main.py
├── pyproject.toml
├── requirements.txt
├── providers.yaml
├── env.example
├── feature.md
├── agent_scan/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   └── utils/
│       └── llm.py
└── testcase/
    ├── case1/main1.py
    └── case3/main.py
```

### Go 端调用参数（AgentTask）

```
uv run --no-project main.py \
  -m <eval_model> \
  -k <api_key> \
  -u <base_url> \
  --agent_provider <temp_yaml_path> \
  --language <zh|en> \
  --aig-mode
```

- `agent_data`（YAML 内容）从 Server 分发参数中获取
- Go 端写入临时文件，路径通过 `--agent_provider` 传入
- 3 步计划：Info Collection、Vulnerability Detection、Vulnerability Review
- 工作目录由 `utils.ResolveAgentScanDir()` 解析

## AIG-PromptSecurity 子系统

### 目录结构

```
AIG-PromptSecurity/
├── cli_run.py            # 入口脚本
├── pyproject.toml
├── Dockerfile
├── LICENSE.md
├── README.md
├── README_ZH.md
└── cli/
    ├── __init__.py
    ├── mappings.py
    ├── models.py
    └── parsers.py
```

### Go 端调用参数（ModelRedteamReport）

```
uv run --no-project cli_run.py \
  --async_mode \
  --model <model> --base_url <url> --api_key <key> --max_concurrent <n> \
  [--model <model2> ...] \
  --evaluate_model <eval_model> \
  --eval_base_url <eval_url> \
  --eval_api_key <eval_key> \
  --techniques Raw \
  --choice serial \
  --lang <zh|en> \
  --scenarios <scenario> \
  --choice parallel \
  --techniques <technique...>
```

Scenario 格式：
- 自定义 prompt：`Custom:prompt=<text>`
- 数据集：`MultiDataset:dataset_file=<path>,num_prompts=<n>,random_seed=<n>,prompt_column=<col>`

支持多个 model 并行测试。评测集通过 `utils.GetEvaluationsDetail(server, dataName)` 从 Server 下载为临时 JSON 文件。

3 步计划（中文）：初始化越狱环境、执行模型安全评估、生成模型安全报告。

## SkillTask 调用

SkillTask 结构与 McpTask code 模式几乎一致，但仅支持 code 模式：

```
uv run --no-project main.py \
  --model <model> --base_url <url> --api_key <key> \
  --prompt <content> --debug --aig-mode --language <lang> \
  --repo <folder>
```

工作目录由 `utils.ResolveSkillScanDir()` 解析。

## 路径解析函数

Go 端通过以下函数定位 Python 子系统目录：
- `utils.ResolveMcpScanDir()`
- `utils.ResolveAgentScanDir()`
- `utils.ResolvePromptSecurityDir()`
- `utils.ResolveSkillScanDir()`
- `utils.ResolveUvBin()` — 定位 uv 可执行文件

## 相关概念

- [Go/Python 桥接](/concepts/05-python-bridge.md)
- [MCP 安全扫描](/concepts/06-mcp-scan.md)
- [四种任务类型](/concepts/01-task-types.md)
