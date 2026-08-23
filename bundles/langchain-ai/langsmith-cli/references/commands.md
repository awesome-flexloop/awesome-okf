---
type: reference
scope: langsmith-cli
name: commands
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: langsmith-cli 命令参考——全部命令、标志、过滤器与输出格式详解
---

# 命令参考

本参考基于源码 `internal/cmd/` 中的 Cobra 命令定义整理。

## 全局用法

```
langsmith [global flags] <command> [subcommand] [flags] [args]
```

### 全局标志

| Flag | 环境变量 | 默认 | 说明 |
|---|---|---|---|
| `--api-key` | `LANGSMITH_API_KEY` | — | LangSmith API Key（隐藏） |
| `--api-url` | `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` | API URL |
| `--profile` | `LANGSMITH_PROFILE` | — | 选择命名 profile |
| `--workspace` | `LANGSMITH_WORKSPACE_ID` | — | 工作区 ID |
| `--workspace-id` | — | — | `--workspace` 的隐藏别名 |
| `--format` | — | `pretty` | 输出格式：`pretty` 或 `json` |
| `--version` | — | — | 显示版本信息 |

## project

追踪项目（session）查询。

### `project list`

列出工作区中的追踪项目（不含实验，实验用 `experiment list`）。

```bash
langsmith project list [--limit N] [--name-contains SUBSTR] [-o FILE]
```

- 默认返回 20 个，按最近活动（`last_run_start_time`）降序排列。
- 使用 `SessionListParams`，设置 `ReferenceFree=true`、`IncludeStats=true`。

### `project issues`

列出项目的问题。

## trace

端到端 trace 查询与导出。一个 trace 是代表一次完整应用调用的 run 树。

### `trace list`

```bash
langsmith trace list [filter flags] [--include-metadata] [--include-io] \
  [--include-feedback] [--include-flagged] [--full] [--show-hierarchy] [-o FILE]
```

- 默认 limit 20，仅查询 root run（`IsRoot=true`），按开始时间降序。
- 默认时间窗口 7 天。
- `--show-hierarchy`：对每个 trace 获取完整 run 树并以树形渲染（pretty）或嵌套 JSON 输出。
- `--full`：等价于 `--include-metadata --include-io --include-feedback`。

### `trace get TRACE_ID`

```bash
langsmith trace get <trace-id> [--project NAME | --project-id UUID] \
  [--since TS | --last-n-minutes N] [--include-*] [--full] [-o FILE]
```

获取指定 trace 的所有 run（按 `Order=Asc` 升序），pretty 模式输出树形结构。

### `trace export OUTPUT_DIR`

```bash
langsmith trace export <dir> [filter flags] [--include-*] [--full] \
  [--filename-pattern PATTERN]
```

将每个 trace 导出为独立 JSONL 文件。默认 limit 10。
`--filename-pattern` 支持 `{trace_id}` 和 `{name}` 占位符，默认 `{trace_id}.jsonl`。

### `trace messages`

查询 trace 消息（v2 专属功能，自托管 < 0.16 不可用）。

### `trace stats`

显示 trace 统计信息。

### `trace setup`

配置 Claude Code 或 Codex 将 trace 发送到 LangSmith。

```bash
langsmith trace setup [claude|codex] [API_KEY] [URL] [PROJECT] \
  [--project NAME] [--user NAME] [--email EMAIL] [--yes] [--no-install] [--scope user|project]
```

写入 agent 本地配置文件（0600 权限），通过 agent 自身 CLI 安装插件。

## run

单个 run 查询。Run 是 trace 中的一个步骤（LLM 调用、tool 调用、chain 步骤等），可位于任意层级。

### `run list`

```bash
langsmith run list [filter flags] [--run-type TYPE] [--include-*] [--full] [-o FILE]
```

- 默认 limit 50（**非** root-only，包含所有层级 run）。
- `--run-type`：llm、chain、tool、retriever、prompt、parser。

### `run get RUN_ID`

```bash
langsmith run get <run-id> [--project NAME] [--since TS | --last-n-minutes N] \
  [--include-*] [--full] [-o FILE]
```

获取单个 run 的完整信息。

### `run export OUTPUT_FILE`

```bash
langsmith run export <file.jsonl> [filter flags] [--run-type TYPE] [--include-*] [--full]
```

将 run 导出为单个 JSONL 文件（每行一个 JSON 对象）。默认 limit 100。

## thread

多轮对话线程查询。一个 thread 是共享 `thread_id` 的多个 root run 集合。

### `thread list`

```bash
langsmith thread list --project NAME [--last-n-minutes N] [--limit N] [-o FILE]
```

需要 `--project`。默认 20 个，按最近活动排序。select 字段额外包含 `thread_id`。

### `thread get THREAD_ID`

```bash
langsmith thread get <thread-id> --project NAME [--full] [-o FILE]
```

获取线程中的所有轮次。

## dataset

评估数据集管理。

### `dataset list`

```bash
langsmith dataset list [--limit N] [--name-contains SUBSTR] [-o FILE]
```

默认 pageSize 20，自动分页。

### `dataset get NAME_OR_ID`

获取数据集详情。支持 UUID 或名称查找。

### `dataset create`

```bash
langsmith dataset create --name NAME [--description DESC]
```

### `dataset delete NAME_OR_ID`

```bash
langsmith dataset delete <name-or-id> [--yes]
```

### `dataset export NAME_OR_ID OUTPUT_FILE`

导出数据集示例到 JSON 文件。

### `dataset upload INPUT_FILE --name NAME`

从 JSON 文件上传数据集。

## example

数据集示例管理。

### `example list`

```bash
langsmith example list --dataset NAME_OR_ID [--split SPLIT] [--limit N] [--offset N] [-o FILE]
```

默认 20 个，支持 `--offset` 分页。

### `example create`

```bash
langsmith example create --dataset NAME_OR_ID \
  --inputs JSON --outputs JSON [--metadata JSON] [--split SPLIT]
```

### `example delete EXAMPLE_ID`

## evaluator

在线/离线评估规则管理。

### `evaluator list`

列出工作区所有 evaluator 规则。

### `evaluator get [NAME]`

```bash
langsmith evaluator get [NAME] [--session-id UUID] [-o FILE]
```

按名称和/或 session ID 查询。至少提供 NAME 或 `--session-id` 之一。单个结果输出对象，多个输出数组。

### `evaluator upload EVALUATOR_FILE`

```bash
langsmith evaluator upload <file.py|file.ts|...> \
  --name NAME --function FUNC_NAME \
  (--dataset NAME | --project NAME) \
  [--sampling-rate 0.0-1.0] [--trace-filter EXPR] \
  [--replace] [--yes]
```

从 Python/JS/TS 文件上传代码评估器。CLI 自动提取指定函数，重命名为 `perform_eval`（Python）或 `performEval`（JS），并处理 export 关键字和箭头函数转换。

端点：`POST /api/v1/runs/rules`（创建）、`PATCH /api/v1/runs/rules/{id}`（替换）。

### `evaluator create-llm`

```bash
langsmith evaluator create-llm --name NAME \
  (--dataset NAME | --project NAME) \
  --model-config FILE \
  (--prompt FILE --schema FILE | --hub-ref REF) \
  [--variable-mapping JSON] [--sampling-rate N] [--replace] [--yes]
```

创建 LLM-as-judge 评估器。`--model-config` 始终必需。

### `evaluator delete NAME`

```bash
langsmith evaluator delete <name> [--yes]
```

## experiment

评估实验查询。

### `experiment list`

```bash
langsmith experiment list [--dataset NAME_OR_ID] [--limit N] [-o FILE]
```

使用 `SessionListParams`，设置 `ReferenceFree=false`（仅实验）、`IncludeStats=true`。默认 20 个。

### `experiment get NAME_OR_ID`

```bash
langsmith experiment get <name-or-uuid> [-o FILE]
```

先尝试 UUID 解析（直接 `Sessions.Get`），否则按名称查找。输出包含 feedback_stats、run_stats（latency/token_count/error_rate/total_cost）、example_count。

## hub

LangSmith Hub 上的 Agent/Skill 仓库管理。

### `hub init`

```bash
langsmith hub init --type skill|agent --dir DIR --name NAME
```

### `hub push`

```bash
langsmith hub push [OWNER/]REPO --type skill|agent --dir DIR
```

推送本地目录为新 commit。排除 `.git/`、`node_modules/`、密钥文件等，限制最多 500 文件、单文件 ≤ 1 MiB。

### `hub pull`

```bash
langsmith hub pull [OWNER/]REPO[:REF] --dir DIR
```

拉取 commit 文件。目标目录非空且无 `SKILL.md`/`AGENTS.md` 标记时需要 `--yes`。

### `hub list / hub get / hub delete`

发现、查看、删除仓库。标识符格式 `[OWNER/]REPO`，省略 owner 默认为 `-`（当前租户通配符）。

## sandbox

沙箱环境管理（实验性）。

子命令包括：create、list、get、update、delete、start、stop、exec、console、service-url、generate-download-url、tunnel、ssh-setup。

## auth

### `auth login`

```bash
langsmith auth login [--no-browser] [--timeout DURATION] [--prompt-workspace]
```

OAuth 2.0 设备码流。client ID 为 `langsmith-cli`，轮询间隔 5 秒。

### `auth info`

显示当前认证状态（authenticated、auth method、API URL、profile、OAuth 过期时间等）。

### `auth token`

输出 OAuth access token（必要时自动刷新）。

## profile / workspace

- `profile`：管理命名配置（create、list、set-workspace 等）。
- `workspace`：工作区列表与切换。

## update

```bash
langsmith self-update [--dry-run] [--force]
```

自更新。通过安装脚本或 GitHub Releases 安装的可原地更新；Homebrew/Scoop/go install 安装的提示使用对应包管理器。

## api

通用 API 浏览与认证请求工具。

### 浏览

```bash
langsmith api ls [--tag TAG] [--search QUERY]
langsmith api info METHOD PATH
```

### 请求

```bash
langsmith api PATH [-X METHOD] [-H HEADER] [-F KEY=VALUE] [-f KEY=VALUE] \
  [--body JSON|@FILE|@-] [--input FILE|-] [-i]
```

未指定 method 且有 body/field/input 时自动使用 POST。

## 通用过滤标志

trace 和 run 命令共享以下标志（`addCommonFilterFlags`）：

| Flag | 说明 |
|---|---|
| `--project NAME` | 项目名称（env: `LANGSMITH_PROJECT`） |
| `--project-id UUID` | 项目 UUID（优先于 --project） |
| `-n, --limit N` | 最大结果数 |
| `--last-n-minutes N` | 最近 N 分钟 |
| `--since TS` | 起始时间（RFC3339/日期） |
| `--before TS` | 结束时间 |
| `--error / --no-error` | 错误状态 |
| `--name NAME` | 名称搜索（子串） |
| `--run-type TYPE` | Run 类型（仅 run 命令） |
| `--min-latency SEC` | 最小延迟（秒） |
| `--max-latency SEC` | 最大延迟（秒） |
| `--min-tokens N` | 最小 token 数（客户端过滤） |
| `--tags TAGS` | 逗号分隔标签（OR） |
| `--metadata K=V` | metadata 过滤 |
| `--filter EXPR` | 原生 DSL 透传 |
| `--trace-ids IDS` | 逗号分隔 trace ID |

## 相关参考

- [核心数据结构](/langchain-ai/langsmith-cli/references/data-structures) — Client/Options/FilterFlags/RunSchema 等关键类型
- [API 客户端架构](/langchain-ai/langsmith-cli/concepts/api-client) — 概念性说明
