---
type: Concept
title: Go/Python 桥接机制
description: Go Agent 通过 os/exec 以子进程方式调用 uv run 启动 Python 脚本，解析 stdout 中的 JSON 行实现跨语言通信，支持上下文取消和文件上传回传。
tags: [ai-infra-guard, go, python, bridge, subprocess, uv, stdout]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: python
    resource: /references/python-subsystems.md
    title: Python 子系统信源
---

## 为什么需要桥接

AIG 的核心扫描引擎（指纹识别、HTTP 探测、CVE 匹配）用 Go 编写，因为 Go 在高并发网络 I/O 和单二进制分发上有优势。但 LLM 驱动的安全分析任务（代码审计、越狱测试、MCP 动态检测）依赖 Python 的 AI 生态（LangChain、OpenAI SDK、MCP SDK）。

桥接机制让两种语言各司其职：Go 负责任务调度、进度管理、网络通信；Python 负责 AI 推理和复杂分析。

## 桥接架构

```
┌─────────────────────────────────────────────────────┐
│                    Go Agent 进程                      │
│                                                       │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────┐ │
│  │ TaskManager  │───►│ Task.Execute │───►│  callbacks│ │
│  └─────────────┘    └──────┬───────┘    └────┬────┘ │
│                             │                 │      │
│                    utils.RunCmdWithContext    │      │
│                             │                 │      │
└─────────────────────────────┼─────────────────┼──────┘
                              │ os/exec         │
                              ▼                 │
┌─────────────────────────────────────────────────┼──────┐
│              Python 子进程 (uv run)              │      │
│                                                  │      │
│  main.py / cli_run.py                            │      │
│    ├─ LLM 调用                                   │      │
│    ├─ 代码分析                                   │      │
│    └─ print(json.dumps({"type":..., "content":{}})) ──────┘
│       (stdout JSON lines)                        │
└──────────────────────────────────────────────────┘
```

## 调用方式

所有 Python 子系统通过 `uv run --no-project <script>` 启动。`--no-project` 标志让 uv 使用脚本所在目录的依赖而非当前工作目录的项目配置。

### 统一调用函数

Go 端调用 `utils.RunCmdWithContext`：

```go
err := utils.RunCmdWithContext(
    ctx,           // context.Context — 支持任务终止
    workDir,       // Python 子系统根目录
    uvBin,         // uv 可执行文件路径
    argv,          // 参数列表
    func(line string) {  // 逐行回调
        ParseStdoutLine(server, rootDir, tasks, line, callbacks, &config, upload)
    },
)
```

该函数：
1. 创建 `exec.CmdContext`，ctx 取消时自动 kill 子进程
2. 设置 stdout pipe
3. 按行扫描 stdout
4. 每行调用 callback
5. 等待进程退出

### uv 路径解析

Go 端通过以下函数定位 Python 子系统：
- `utils.ResolveMcpScanDir()` — mcp-scan 目录
- `utils.ResolveAgentScanDir()` — agent-scan 目录
- `utils.ResolvePromptSecurityDir()` — AIG-PromptSecurity 目录
- `utils.ResolveSkillScanDir()` — skill-scan 目录
- `utils.ResolveUvBin()` — uv 可执行文件路径

## stdout JSON 行协议

Python 子系统通过 stdout 输出进度，每行一个 JSON 对象。Go 端的 `ParseStdoutLine` 函数负责解析：

```go
func ParseStdoutLine(server, rootDir string, tasks []SubTask, line string,
    callbacks TaskCallbacks, config *CmdConfig, upload bool) {

    if len(line) > 1 && line[0] == '{' {
        var cmd CmdContent
        json.Unmarshal([]byte(line), &cmd)
        // 根据 cmd.Type 分发...
    } else {
        fmt.Println(line)  // 非 JSON 行直接透传
    }
}
```

### 消息信封

```go
type CmdContent struct {
    Type    string          `json:"type"`
    Content json.RawMessage `json:"content"`
}
```

### 支持的消息类型

| type | Go 处理逻辑 |
|------|------------|
| `newPlanStep` | 调用 `NewPlanStepCallback`，自动更新任务计划状态 |
| `statusUpdate` | 维护 `CmdConfig.StatusId` 状态机，调用 `StepStatusUpdateCallback` |
| `toolUsed` | 构造 `Tool` 对象，调用 `ToolUsedCallback` |
| `actionLog` | 调用 `ToolUseLogCallback` |
| `resultUpdate` | 标记所有子任务完成，可选上传附件，调用 `ResultCallback` |
| `error` | 调用 `ErrorCallback` |

### 状态机

`CmdConfig` 维护 Python 端状态到 Go 端回调的映射：

```go
type CmdConfig struct {
    StatusId string
    Status   string
}
```

当收到 `statusUpdate`：
- `status == "running"` → 生成新的 StatusId，状态设为 running
- `status == "completed"` → 若上一状态也是 completed，生成新 StatusId；状态设为 completed

这确保每个 running→completed 循环都有唯一的状态 ID 供前端渲染。

## 各子系统命令参数

### mcp-scan

```bash
uv run --no-project main.py \
  --model <model> --base_url <url> --api_key <key> \
  --prompt "<content>" --debug --aig-mode --language zh \
  [--header key:value ...] \
  [--repo <path> | --server_url <url>]
```

### agent-scan

```bash
uv run --no-project main.py \
  -m <eval_model> -k <api_key> -u <base_url> \
  --agent_provider <temp_yaml_path> \
  --language zh --aig-mode
```

### AIG-PromptSecurity

```bash
uv run --no-project cli_run.py --async_mode \
  --model <m1> --base_url <url1> --api_key <k1> --max_concurrent 1000 \
  [--model <m2> ...] \
  --evaluate_model <eval_model> --eval_base_url <url> --eval_api_key <key> \
  --techniques Raw --choice serial \
  --lang zh --scenarios "Custom:prompt=..." \
  --choice parallel --techniques <technique...>
```

### skill-scan

```bash
uv run --no-project main.py \
  --model <model> --base_url <url> --api_key <key> \
  --prompt "<content>" --debug --aig-mode --language zh \
  --repo <path>
```

## --aig-mode 标志

所有 Python 子系统都接受 `--aig-mode` 标志。该标志告诉 Python 脚本以 AIG 集成模式运行，此时：
- 输出使用 JSON lines 格式（而非人类可读的控制台输出）
- 禁用交互式提示
- 进度通过结构化事件上报

这是 Python 脚本既能独立运行（CLI 模式）又能被 Go 调用（集成模式）的关键。

## 文件附件处理

Python 子系统生成的截图、报告等文件需要回传给 Server。流程如下：

1. Python 脚本将结果中的 `attachment` 字段设为本地文件相对路径
2. Go 端在 `ParseStdoutLine` 中处理 `resultUpdate` 时，若 `upload=true`：
   - 解析 content 数组
   - 对每个含 `attachment` 的项，调用 `utils.UploadFile(server, path.Join(rootDir, attachment))`
   - 替换为 Server 返回的 URL（`/api/v1/images/<filename>`）
3. 替换后的结果通过 `ResultCallback` 发送给 Server

`upload` 参数：
- `ModelRedteamReport` 设为 `true`（需要上传越狱报告截图）
- 其他任务设为 `false`

## 上下文取消与终止

当用户终止任务时：

1. Server 通过 WebSocket 发送 `terminate` 消息
2. Agent 调用任务的 `context.Cancel()`
3. `exec.CmdContext` 检测到 ctx.Done()，向 Python 子进程发送 kill 信号
4. `RunCmdWithContext` 返回 ctx.Err()
5. Task.Execute 返回，任务状态标记为 failed

这确保了 Python 子进程不会在任务终止后继续运行或泄漏。

## 输入文件准备

对于 code 模式的任务（Mcp-Scan、Skill-Scan），Go 端在调用 Python 前完成文件准备：

1. 从 Server 下载附件到本地 `uploads/` 目录
2. 根据扩展名解压（`.zip`/`.whl` → `ExtractZipFile`，`.tgz`/`.tar.gz` → `ExtractTGZ`）
3. 或对 GitHub URL 调用 `utils.GitClone`（超时 10 分钟）
4. 将解压目录路径通过 `--repo` 参数传给 Python

路径安全检查确保解压路径不超出 `uploads/` 目录（防止 Zip Slip 攻击）。

## 相关概念

- [四种任务类型](/concepts/01-task-types.md)
- [MCP 安全扫描](/concepts/06-mcp-scan.md)
- [WebSocket 通信协议](/concepts/04-websocket-protocol.md)
- [Python 子系统信源](/references/python-subsystems.md)
