---
type: concept
scope: langsmith-cli
name: cli-commands
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: CLI 命令体系——Cobra 命令树、过滤器系统、双模式输出与分页机制
---

# CLI 命令体系

## 命令树与注册机制

langsmith-cli 使用 [Cobra](https://github.com/spf13/cobra) v1.8.1 构建命令树。根命令由 `NewRootCmd(rawVersion, displayVersion)` 在 `internal/cmd/root.go:26` 创建，通过 `AddCommand` 注册 19 个子命令组。

每个子命令组遵循一致的构造模式：`newXxxCmd()` 返回 `*cobra.Command`，在其内部通过 `cmd.AddCommand(newXxxListCmd())` 等注册具体操作。这种"一个文件一个命令组"的组织方式使代码结构与 CLI 命令树一一对应。

### 命令分组

| 命令组 | 子命令 | 主要用途 |
|---|---|---|
| `project` | list, issues | 追踪项目（session）查询 |
| `trace` | list, get, export, messages, stats, setup | 端到端 trace 查询与导出 |
| `run` | list, get, export | 单个 run（LLM/tool/chain 步骤）查询 |
| `thread` | list, get | 多轮对话线程 |
| `dataset` | list, get, create, delete, export, upload | 评估数据集管理 |
| `example` | list, create, delete | 数据集示例管理 |
| `evaluator` | get, list, upload, create-llm, delete | 评估规则管理 |
| `experiment` | list, get | 评估实验结果查询 |
| `hub` | init, push, pull, list, get, delete | Agent/Skill 仓库版本管理 |
| `sandbox` | create/list/get/update/delete/start/stop/exec/console/tunnel/ssh-setup/... | 沙箱环境 |
| `auth` | login, info, token | OAuth 认证 |
| `api` | ls, info（+ 直接请求） | 通用 API 浏览与调用 |
| `profile` | create/list/set/... | 多环境配置 |
| `workspace` | list/set/... | 工作区管理 |
| `update` | — | 自更新 |
| `insights` | — | 洞察分析 |
| `fleet` | — | Fleet 管理 |
| `apps` | init/list/get/push/pull/... | 自定义应用 |
| `prompt` | list/get/pull/push/... | Prompt Hub |

## 全局标志

根命令注册了六个 PersistentFlags（`root.go:59-66`），对所有子命令生效：

| Flag | 环境变量 | 说明 |
|---|---|---|
| `--api-key` | `LANGSMITH_API_KEY` | API Key（隐藏标志） |
| `--api-url` | `LANGSMITH_ENDPOINT` | API URL（自托管时使用） |
| `--profile` | `LANGSMITH_PROFILE` | 选择命名 profile |
| `--workspace` | `LANGSMITH_WORKSPACE_ID` | 目标工作区 ID |
| `--workspace-id` | — | 同 `--workspace`（隐藏别名） |
| `--format` | — | 输出格式：`pretty`（默认）或 `json` |

`--workspace` 和 `--workspace-id` 绑定到同一个变量 `flagWorkspaceID`，后者标记为隐藏，提供向后兼容。

## 过滤器系统

trace 和 run 命令共享统一的过滤器机制，由 `FilterFlags` 结构体（`filters.go:14-33`）和 `addCommonFilterFlags` 函数（`filters.go:36-56`）实现。

### 通用过滤标志

| Flag | 类型 | 说明 |
|---|---|---|
| `--project` | string | 项目名称（env: `LANGSMITH_PROJECT`） |
| `--project-id` | string | 项目 UUID（跳过名称查找，优先于 --project） |
| `-n, --limit` | int | 最大返回数 |
| `--last-n-minutes` | int | 最近 N 分钟时间窗口 |
| `--since` | string | 起始时间（RFC3339/日期） |
| `--before` | string | 结束时间（向前分页） |
| `--error / --no-error` | bool | 错误状态过滤 |
| `--name` | string | Run 名称搜索 |
| `--run-type` | string | Run 类型：llm/chain/tool/retriever/prompt/parser（仅 run 命令） |
| `--min-latency / --max-latency` | float | 延迟范围（秒） |
| `--min-tokens` | int | 最小总 token 数（**客户端过滤**） |
| `--tags` | string | 逗号分隔标签（OR 逻辑） |
| `--metadata` | string | metadata key=value 过滤 |
| `--filter` | string | 原生 LangSmith filter DSL 透传 |
| `--trace-ids` | string | 逗号分隔 trace ID |

### 时间窗口解析

`resolveStartTime(since, lastNMinutes)` 的优先级（`filters.go:60-75`）：

1. `--last-n-minutes N` → `now - N 分钟`
2. `--since <timestamp>` → 解析 RFC3339、`2006-01-02T15:04:05` 或 `2006-01-02`
3. 默认 → `now - 7 天`

### Filter DSL 构建

`buildFilterDSL(f)` 将 flag 翻译为 LangSmith 服务端过滤表达式（`filters.go:142-212`）：

- `--name "agent"` → `search(name, "agent")`
- `--min-latency 5` → `gte(latency, 5)`
- `--tags prod,v2` → `or(has(tags, "prod"), has(tags, "v2"))`
- `--metadata revision_id=abc` → `and(eq(metadata_key, "revision_id"), eq(metadata_value, "abc"))`
- `--trace-ids id1,id2` → `in(trace_id, ["id1", "id2"])`
- 多个条件用 `and(...)` 组合
- `--filter` 原样追加，支持任意服务端 DSL

**注意**：`--min-tokens` 无法在服务端过滤，在 `queryRuns`/`queryRunsV2` 中客户端跳过不满足条件的 run（`helpers.go:63-65`、`helpers.go:97-99`）。

## 分页机制

CLI 实现了两种分页模式：

### v1 游标分页

`queryRuns` 使用 `resp.Cursors.Next` 游标（`helpers.go:70-75`），循环请求直到收集足够结果或无下一页。

### v2 自动分页

`queryRunsV2` 使用 SDK 的 `QueryV2AutoPaging` 迭代器（`helpers.go:91-101`），内部处理游标翻页。

### 列表命令分页

项目/数据集/实验列表命令使用 SDK 的 `ListAutoPaging` 迭代器（如 `experiment.go:69`），在 `limit` 达到时提前 break。

各命令的默认 limit：

| 命令 | 默认 limit |
|---|---|
| `project list` | 20 |
| `trace list` | 20 |
| `trace export` | 10 |
| `run list` | 50 |
| `run export` | 100 |
| `dataset list` | 20（pageSize） |
| `experiment list` | 20 |
| `example list` | 20 |

## 输出系统

### 双模式渲染

每个命令通过 `GetFormat()` 获取全局格式设置：

- **pretty 模式**：使用 `tablewriter` 渲染表格（无边框、双空格列分隔）、`treeprint` 渲染 trace 层级树。
- **json 模式**：使用 `encoding/json` 的 `MarshalIndent`（2 空格缩进）输出。

### 输出辅助函数

| 函数 | 用途 |
|---|---|
| `output.OutputJSON(data, path)` | 输出缩进 JSON 到 stdout 或文件 |
| `output.OutputJSONL(items, path)` | 输出 JSONL（每行一个对象） |
| `output.OutputTable(columns, rows, title)` | 输出 ASCII 表格 |
| `output.OutputTree(data, prefix)` | 输出 run 层级树 |
| `output.PrintOutput(data, format, path)` | 通用 pretty/json 输出分发 |

写文件时向 stderr 输出状态行（如 `{"status": "written", "path": "traces.json"}`），stdout 保持干净。

### Run 数据提取

`extract.ExtractRun(run, includeMetadata, includeIO, includeFeedback)` 将 SDK 的 `RunSchema` 归一化为扁平 map（`extract/extract.go:12`），注释标注"mirrors the Python extract_run() function exactly"。三个 include 标志控制字段扩展：

- 基础字段：run_id、trace_id、name、run_type、parent_run_id、start_time、end_time
- `--include-metadata`：status、duration_ms、token_usage、costs、tags、custom_metadata
- `--include-io`：inputs、outputs、error、events
- `--include-feedback`：feedback_stats
- `--full`：以上三者全开

## 结构化命令框架

`internal/structured/` 包提供泛型声明式命令框架，用于 `auth`、`sandbox` 等较新命令。核心抽象：

- `Parent`：声明父命令及其子命令构造器列表。
- `Command[T]`：泛型命令，包含 `Action func(ctx, cmd, in T, args) (any, error)` 业务逻辑和 `Render` 渲染器。
- `PropertyList`：键值对渲染器，支持 `OmitEmpty` 和 Go template。
- `Template`：字符串模板渲染器。

这种模式将数据获取与输出渲染分离，框架自动处理 pretty/json 双模式。

## 通用 API 命令

`langsmith api` 命令（`internal/cmd/api/`）提供类似 `gh api` 的通用 HTTP 客户端能力：

- **浏览端点**：`langsmith api ls` 列出所有 API 端点，`--tag`/`--search` 过滤。
- **端点详情**：`langsmith api info GET sessions` 显示参数和说明。
- **发起请求**：`langsmith api sessions?limit=5` 直接 GET，`-X POST` 指定方法。
- **请求体**：`--body`（JSON 字符串/@file/@-）、`--input`（文件）、`-F`（类型化字段）、`-f`（原始字符串字段）。
- **响应**：`-i/--include` 包含响应头。

这为 AI 代理提供了逃生舱——当 CLI 没有封装某个 API 时，可直接通过 `api` 命令调用。

## 相关概念

- [API 客户端架构](/ai/langchain-ai/langsmith-cli/concepts/api-client) — SDK 封装、v1/v2 透明切换、认证体系
- [总览](/ai/langchain-ai/langsmith-cli/concepts/overview) — 项目定位与架构概览
