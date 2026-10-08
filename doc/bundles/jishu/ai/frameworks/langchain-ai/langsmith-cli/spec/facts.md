---
type: spec
scope: langsmith-cli
name: facts
version: "0.1.0"
source: https://github.com/langchain-ai/langsmith-cli
description: langsmith-cli 源码事实验证清单——从 Go 源码中提取的编号事实
---

# langsmith-cli 事实清单

## 项目元信息

F-001: 文件 `go.mod` 第1行，模块路径为 `github.com/langchain-ai/langsmith-cli`，Go 版本要求 `1.25.0`。

F-002: 文件 `go.mod` 第5-16行，直接依赖包括：`github.com/spf13/cobra v1.8.1`（CLI 框架）、`github.com/langchain-ai/langsmith-go v0.25.6`（LangSmith 生成式 Go SDK）、`github.com/itchyny/gojq v0.12.15`（jq 实现）、`github.com/olekukonko/tablewriter v0.0.5`（表格输出）、`github.com/pelletier/go-toml/v2 v2.2.4`（TOML 解析）、`github.com/google/uuid v1.6.0`、`github.com/xlab/treeprint v1.2.0`（树形输出）、`github.com/stretchr/testify v1.11.1`（测试）、`golang.org/x/net`、`golang.org/x/term`。

F-003: 文件 `cmd/langsmith/main.go` 第10-14行，通过 ldflags 注入三个版本变量：`version = "dev"`、`commit = "unknown"`、`date = "unknown"`。`main()` 调用 `cmd.NewRootCmd(version, displayVersion)` 创建根命令并执行。

F-004: 文件 `Makefile` 第5行，构建参数 `LDFLAGS=-ldflags "-s -w -X main.version=$(VERSION) -X main.commit=$(COMMIT) -X main.date=$(DATE)"`，使用 `CGO_ENABLED=0` 静态编译，入口 `./cmd/langsmith`。

F-005: 文件 `README.md` 第3行，项目定位为"An agent-first CLI for querying and managing LangSmith resources"，面向 AI 编码代理（deepagents、Claude Code、Cursor 等）和开发者。

## 根命令与全局标志（internal/cmd/root.go）

F-006: 文件 `internal/cmd/root.go` 第26-90行，`NewRootCmd(rawVersion, displayVersion string)` 创建 `*cobra.Command`，`Use: "langsmith"`，设置 `SilenceUsage: true`、`SilenceErrors: true`。

F-007: 文件 `internal/cmd/root.go` 第59-66行，注册六个 PersistentFlags：`--api-key`（隐藏）、`--api-url`、`--profile`、`--workspace`、`--workspace-id`（隐藏，与 --workspace 绑定同一变量）、`--format`（默认 `"pretty"`，可选 `json`）。

F-008: 文件 `internal/cmd/root.go` 第69-87行，注册 19 个子命令组：`project`、`trace`、`run`、`thread`、`dataset`、`example`、`evaluator`、`experiment`、`sandbox`、`insights`、`fleet`、`hub`、`apps`、`prompt`、`auth`、`profile`、`workspace`、`update`、`api`。

F-009: 文件 `internal/cmd/root.go` 第143-227行，`resolveClientOptions(refreshOAuth bool)` 实现配置解析优先级：flag > 环境变量 > profile > 默认值。API Key 优先级：`--api-key` > `LANGSMITH_API_KEY` > profile OAuth token > profile APIKey。

F-010: 文件 `internal/cmd/root.go` 第200-212行，OAuth token 自动刷新逻辑：当 `refreshOAuth=true` 且 profile 有 RefreshToken，且 access token 为空或 `TokenExpiresSoon(now, time.Minute)` 时，调用 `refreshProfileToken` 刷新并持久化到 config。

## 客户端封装（internal/client/client.go）

F-011: 文件 `internal/client/client.go` 第22-36行，`Client` 结构体封装 `SDK *langsmith.Client`（生成式 SDK）、`apiKey`、`oauthAccessToken`、`apiURL`、`workspaceID`、`platformPrefix`、`sessionCache map[string]string`（单次调用内的 project name→ID 缓存）、`cachedUseV2API *bool`。

F-012: 文件 `internal/client/client.go` 第50-53行，`NormalizeURL(apiURL string)` 去除尾部 `/` 和 `/api/v1` 后缀，防止 SDK 重复拼接路径。

F-013: 文件 `internal/client/client.go` 第65-99行，`NewWithOptions(options Options)` 创建客户端，认证方式优先级：`ProfileName != ""` 时使用 `langsmith.WithProfile()`；否则 APIKey 使用 `option.WithAPIKey()`；OAuth token 使用 `option.WithHeader("authorization", "Bearer ...")`。非默认 baseURL 通过 `option.WithBaseURL()` 设置，workspace 通过 `option.WithTenantID()` 设置。

F-014: 文件 `internal/client/client.go` 第121-151行，`UseV2API(ctx)` 通过 `SDK.Info.List(ctx)` 获取 `/info` 版本信息并缓存。`useV2API(version)` 判定逻辑：非 semver 版本（如 "dev"，即 Cloud）→ v2；major != 0 → v2；major==0 且 minor >= 16（`minSelfHostedV2Minor`）→ v2；否则 v1。

F-015: 文件 `internal/client/client.go` 第184-204行，平台路径前缀派生：`singleOriginPlatformPrefix = "/api/v1/platform"`；当 endpoint 以 `/api/v1` 或 `/api` 结尾时使用单源前缀，否则使用多源前缀 `/v1/platform`（去掉 `/api` 段）。

F-016: 文件 `internal/client/client.go` 第239-256行，提供 `RawGet`、`RawPost`、`RawPatch`、`RawDelete` 四个原始 HTTP 辅助方法，以及 `RawDo`（返回原始响应、不将 4xx/5xx 视为错误）。`FetchCustomAppSource` 用于下载二进制 .tar.gz。

F-017: 文件 `internal/client/client.go` 第336-384行，`doHTTP` 底层方法：30 秒超时，设置 `x-api-key`、`Authorization: Bearer`、`Content-Type: application/json`、`x-tenant-id` 头，返回 `httpResponse`（statusCode/proto/headers/body）。

F-018: 文件 `internal/client/client.go` 第102-119行，`ResolveSessionID(ctx, projectName)` 先查 `sessionCache`，未命中则调用 `SDK.Sessions.List`（Limit=1）解析 project name 为 UUID，结果缓存。

## Trace 命令（internal/cmd/trace.go）

F-019: 文件 `internal/cmd/trace.go` 第15-40行，`newTraceCmd()` 注册 6 个子命令：`list`、`get`、`export`、`messages`、`stats`、`setup`。Trace 定义为"top-level agent runs and their full hierarchy"。

F-020: 文件 `internal/cmd/trace.go` 第64行，`trace list` 默认 limit 为 20，查询参数 `IsRoot=true`、`Order=Desc`。

F-021: 文件 `internal/cmd/trace.go` 第97-113行，`--show-hierarchy` 模式下，对每个 root run 单独查询子 run（`Trace=traceID`、`Order=Asc`、limit 1000），通过 `output.OutputTree` 渲染树形结构。

F-022: 文件 `internal/cmd/trace.go` 第252-366行，`trace export` 将每个 trace 导出为独立 JSONL 文件，默认 limit 10，支持 `--filename-pattern`（占位符 `{trace_id}`、`{name}`）。

## Run 命令（internal/cmd/run.go）

F-023: 文件 `internal/cmd/run.go` 第13-35行，`newRunCmd()` 注册 3 个子命令：`list`、`get`、`export`。Run 定义为"a single step within a trace"，可查询任意层级。

F-024: 文件 `internal/cmd/run.go` 第58行，`run list` 默认 limit 为 50（非 root-only，即包含所有层级 run）。

F-025: 文件 `internal/cmd/run.go` 第199行，`run export` 默认 limit 为 100，输出单个 JSONL 文件（每行一个 JSON 对象）。

## 过滤器与查询（internal/cmd/filters.go, helpers.go）

F-026: 文件 `internal/cmd/filters.go` 第14-33行，`FilterFlags` 结构体包含 16 个字段：TraceIDs、Limit、Project、ProjectID、LastNMinutes、Since、Before、Cursor、ErrorFlag、NoErrorFlag、Name、RunType、MinLatency、MaxLatency、MinTokens、Tags、Metadata、RawFilter。

F-027: 文件 `internal/cmd/filters.go` 第60-75行，`resolveStartTime(since, lastNMinutes)` 优先级：`lastNMinutes > 0` → N 分钟前；`since` 非空 → 解析 RFC3339/`2006-01-02T15:04:05`/`2006-01-02`；否则默认 7 天前。

F-028: 文件 `internal/cmd/filters.go` 第142-212行，`buildFilterDSL(f)` 生成 LangSmith 过滤器 DSL 字符串：`search(name, ...)`、`gte(latency, ...)`/`lte(latency, ...)`、`has(tags, ...)`（多 tag 用 `or()`）、`eq(metadata_key,...)`/`eq(metadata_value,...)`、`in(trace_id, [...])`，多条件用 `and()` 组合。

F-029: 文件 `internal/cmd/helpers.go` 第44-78行，`queryRuns` 使用 `c.SDK.Runs.Query`，通过 `resp.Cursors.Next` 游标分页；`minTokens` 在客户端过滤（服务端不支持 total_tokens 过滤）。

F-030: 文件 `internal/cmd/helpers.go` 第84-107行，`queryRunsV2` 使用 `c.SDK.Runs.QueryV2AutoPaging` 自动分页，每个 v2 Run 通过 `runV2ToSchema` 归一化为 v1 `RunSchema`，保持下游渲染不变。

F-031: 文件 `internal/cmd/helpers.go` 第124-133行，`queryRunsAuto` 根据 `c.UseV2API(ctx)` 自动选择 v1 或 v2 查询后端，对调用方透明。

F-032: 文件 `internal/cmd/helpers.go` 第137-170行，`toV2Params` 将 v1 `RunQueryParams` 翻译为 v2 `RunQueryV2Params`：Trace→TraceID、IsRoot→IsRoot、RunType（大写）、Error→HasError、StartTime→MinStartTime、EndTime→MaxStartTime、Limit→PageSize；Order 被丢弃（v2 固定 newest-first）。

F-033: 文件 `internal/cmd/helpers.go` 第228-276行，`runV2ToSchema` 字段映射：v2 `ProjectID` → v1 `SessionID`、v2 `ParentRunIDs`（最后一个）→ v1 `ParentRunID`、v2 `RunType` 转小写、metadata 合并到 `Extra["metadata"]`。

## Evaluator 命令（internal/cmd/evaluator.go）

F-034: 文件 `internal/cmd/evaluator.go` 第17-46行，`newEvaluatorCmd()` 注册 5 个子命令：`get`、`list`、`upload`、`create-llm`、`delete`。支持 code evaluator（Python/JS）和 LLM-as-judge 两种类型。

F-035: 文件 `internal/cmd/evaluator.go` 第535-545行，`detectLanguage(filename)` 按扩展名判定：`.py` → language="python"，规范函数名 "perform_eval"；`.js/.ts/.tsx/.mjs` → language="javascript"，规范函数名 "performEval"。

F-036: 文件 `internal/cmd/evaluator.go` 第308-312行，evaluator 的 CRUD 通过原始 HTTP 端点：`POST /api/v1/runs/rules`（创建）、`PATCH /api/v1/runs/rules/{id}`（替换）、`DELETE /api/v1/runs/rules/{id}`（删除）。

## Experiment 命令（internal/cmd/experiment.go）

F-037: 文件 `internal/cmd/experiment.go` 第13-34行，`newExperimentCmd()` 注册 `list` 和 `get` 两个子命令。Experiment 是针对 dataset 的评估运行。

F-038: 文件 `internal/cmd/experiment.go` 第54-58行，`experiment list` 使用 `SessionListParams`，设置 `ReferenceFree=false`（仅实验项目）、`IncludeStats=true`，通过 `ListAutoPaging` 分页。

F-039: 文件 `internal/cmd/experiment.go` 第143-166行，`experiment get` 先尝试 `uuid.Parse`，成功则直接 `Sessions.Get`；否则按 name `Sessions.List`（Limit=1）查找。

## 配置管理（internal/config/config.go）

F-040: 文件 `internal/config/config.go` 第14-17行，默认配置路径 `~/.langsmith/config.json`，可通过 `LANGSMITH_CONFIG_FILE` 环境变量覆盖。`DefaultAPIURL = "https://api.smith.langchain.com"`。

F-041: 文件 `internal/config/config.go` 第20-38行，`Profile` 结构体含 `APIKey`、`APIURL`、`WorkspaceID`、`OAuth`（AccessToken/RefreshToken/ExpiresAt）。`Config` 含 `CurrentProfile` 和 `Profiles map[string]Profile`。

F-042: 文件 `internal/config/config.go` 第116-167行，`SaveTo` 写入配置：创建目录（0700）、写入临时文件、`Chmod(0600)`、`Sync()`、`os.Rename` 原子替换。

F-043: 文件 `internal/config/config.go` 第170-194行，`ResolveProfileName` 优先级：`--profile` flag > `LANGSMITH_PROFILE` 环境变量 > `CurrentProfile` > 名为 "default" 的 profile。

F-044: 文件 `internal/config/config.go` 第88-104行，`warnIfGroupOrWorldReadable` 在非 Windows 上检查配置文件权限，若 group/other 可读则输出警告（每路径仅警告一次，使用 `sync.Map` 去重）。

## OAuth 认证（internal/client/oauth.go, internal/cmd/login.go）

F-045: 文件 `internal/cmd/login.go` 第26行，OAuth client ID 为 `"langsmith-cli"`，设备码轮询间隔默认 5 秒（`defaultDeviceCodePollInterval`）。

F-046: 文件 `internal/client/oauth.go` 第16行，OAuth 发现端点路径为 `/.well-known/oauth-authorization-server`（RFC 8414），metadata 文档大小上限 1 MiB。

F-047: 文件 `internal/client/oauth.go` 第56-71行，`oauthDiscoveryCandidates` 按顺序探测：用户配置的 URL → `<origin>/api` → `<origin>`，去重后依次尝试。

F-048: 文件 `internal/client/oauth.go` 第173-194行，`validateOAuthMetadata` 安全校验：issuer 必须与探测 base 匹配，所有 endpoint 必须与 issuer 同源（scheme+host），防止凭证被重定向到恶意主机。

F-049: 文件 `internal/cmd/login.go` 第35-52行，设备码响应包含 `device_code`、`user_code`、`verification_uri`、`expires_in`、`interval`；token 响应包含 `access_token`、`expires_in`、`refresh_token`。

## 输出层（internal/output/output.go, internal/extract/extract.go）

F-050: 文件 `internal/output/output.go` 第17-32行，`OutputJSON(data, filePath)` 输出缩进 JSON（`MarshalIndent`，2 空格）；filePath 非空时写文件并向 stderr 输出状态，否则输出到 stdout。

F-051: 文件 `internal/output/output.go` 第35-74行，`OutputJSONL` 每行一个 JSON 对象；`OutputTable` 使用 `tablewriter`（无边框、双空格列分隔）；`OutputTree` 使用 `treeprint` 渲染 run 层级树。

F-052: 文件 `internal/extract/extract.go` 第12行，`ExtractRun(run, includeMetadata, includeIO, includeFeedback)` 将 `RunSchema` 归一化为扁平 map，注释标注"This mirrors the Python extract_run() function exactly"。基础字段：run_id、trace_id、name、run_type、parent_run_id、start_time、end_time。

## API 命令（internal/cmd/api/）

F-053: 文件 `internal/cmd/api/api.go` 第12-93行，`api` 命令支持浏览端点和发起认证 HTTP 请求。标志：`--body`、`--input`、`-F/--field`（类型化 JSON 字段）、`-f/--raw-field`（字符串字段）、`-H/--header`、`-i/--include`（含响应头）、`-X/--method`（默认 GET，有 body/field/input 时自动 POST）。子命令：`ls`、`info`。

## Dataset 命令（internal/cmd/dataset.go）

F-054: 文件 `internal/cmd/dataset.go` 第15-44行，`newDatasetCmd()` 注册 6 个子命令：`list`、`get`、`create`、`delete`、`export`、`upload`。默认 pageSize 20，支持 `--name-contains` 过滤。

## Hub 命令（internal/cmd/hub.go）

F-055: 文件 `internal/cmd/hub.go` 第22-49行，Hub 限制常量：`hubMaxFileEntries = 500`（最大文件数）、`hubMaxFileSizeBytes = 1 << 20`（1 MiB）。排除目录：`.git`、`node_modules`、`__pycache__`、`.venv`、`venv`、`dist`、`build`、`target`、`.next`、`.cache`。排除密钥文件后缀：`.pem`、`.key`、`.pfx`、`.p12`、`.crt`。

## 其他命令

F-056: 文件 `internal/cmd/root.go` 第69-87行，其余子命令包括：`project`（list/issues）、`thread`（list/get）、`example`（dataset 示例管理）、`sandbox`（沙箱生命周期/连接）、`insights`、`fleet`、`apps`（自定义应用）、`prompt`（Prompt Hub）、`auth`（login/info/token）、`profile`、`workspace`、`update`（self-update）。

## 结构化命令框架（internal/structured/）

F-057: 文件 `internal/cmd/auth.go` 第34-42行，`structured.Parent` 和 `structured.Command[T]` 泛型框架用于声明式命令定义，将 Action（业务逻辑）与 Render（输出渲染）分离。`auth info` 使用 `structured.PropertyList` 渲染键值对，`auth token` 使用 `structured.Template`。
