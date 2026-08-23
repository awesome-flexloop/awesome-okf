---
type: spec-facts
title: AI-Infra-Guard 源码事实清单
---

# AI-Infra-Guard 源码事实清单

> R阶段产出。所有事实均来自源码，编号 F-001 起。不含推断性表述。

## 1. CLI 命令结构

### F-001 CLI 入口
- 文件：`cmd/cli/main.go`
- `package main`，`main()` 调用 `cmd.Execute()`

### F-002 根命令
- 文件：`cmd/cli/cmd/root.go`
- `var rootCmd = &cobra.Command{Use: "ai-infra-guard", Short: "AI基础设施安全检测工具"}`
- `Execute()` 调用 `options.ShowBanner()` 后执行 `rootCmd.Execute()`
- 导入：`github.com/spf13/cobra`

### F-003 scan 子命令
- 文件：`cmd/cli/cmd/scan.go`
- `var scanCmd = &cobra.Command{Use: "scan", Short: "执行原始扫描功能"}`
- 标志变量：scanTargets, scanTargetFile, scanOutputFile, scanProxyURL, scanTimeOut, scanRateLimit, scanFpTemplates, scanAdvTemplates, scanListVulTemplate, scanCheckVulTargets, scanLocalScan, scanAIAnalysis, scanAIHunyuanToken, scanAIDeepSeekToken, scanHeaders, scanLanguage
- 标志：
  - `--target/-t` []string
  - `--file/-f` string
  - `--output/-o` string
  - `--timeout` int 默认 5
  - `--proxy-url` string
  - `--header` []string
  - `--limit` int 默认 200
  - `--fps` string 默认 "data/fingerprints"
  - `--vul` string 默认 "data/vuln"
  - `--list-vul` bool
  - `--check-vul` bool
  - `--localscan` bool
  - `--ai` bool
  - `--hunyuan-token` string
  - `--deepseek-token` string
  - `--lang` string 默认 "zh"
- Run 中构造 `options.Options`，调用 `runner.New(scanOptions)`，然后 `r.RunEnumeration()`

### F-004 webserver 子命令
- 文件：`cmd/cli/cmd/webserver.go`
- `var webserverCmd = &cobra.Command{Use: "webserver", Short: "启动Web服务器"}`
- 标志：`--server` string 默认 "127.0.0.1:8088"，`--api-checker-url` string
- `defaultAPICheckerURL()` 读取环境变量 `AIG_API_CHECKER_URL`，默认 "http://127.0.0.1:8000"
- Run 中调用 `websocket.RunWebServer(webOptions)`

### F-005 api-checker 子命令
- 文件：`cmd/cli/cmd/api_checker.go` 存在（未逐行读取）

### F-006 Agent 独立入口
- 文件：`cmd/agent/main.go`
- `flag.StringVar(&server, "server", "", "server")`，也读环境变量 `AIG_SERVER`
- URL 格式：`ws://%s/api/v1/agents/ws`
- 创建 `agent.NewAgent(agent.AgentConfig{...})`
- 注册 5 个任务：`AIInfraScanAgent`, `McpTask`, `ModelRedteamReport`, `AgentTask`, `SkillTask`
- 调用 `x.Start()`

## 2. WebSocket / HTTP Server

### F-007 RunWebServer
- 文件：`common/websocket/server.go`
- `func RunWebServer(options *version.Options)`
- 使用 `gin.Default()`
- 初始化：trpc.InitTrpc, database.InitDB, TaskStore, ModelStore, AgentManager, ModelManager, FileUploadConfig, SSEManager, TaskManager
- API 分组 `/api/v1`：
  - `/knowledge/fingerprints` (GET, POST, PUT/:name, DELETE)
  - `/knowledge/vulnerabilities` (GET, POST, PUT/:cve, DELETE)
  - `/knowledge/evaluations` (GET, GET/:name, POST, PUT/:name, DELETE)
  - `/knowledge/mcp` (GET/names, GET, POST, PUT/:id, DELETE/:id)
  - `/knowledge/prompt_collections` (GET, POST, PUT/:id, DELETE/:id)
  - `/knowledge/agent` (GET/names, GET/:name, POST/:name, DELETE/:name, POST/connect, POST/prompt_test, GET/template)
  - `/knowledge/jailbreak` (GET)
  - `/app/tasks` (GET, GET/:sessionId, POST/share, GET/sse/:sessionId, POST, POST/uploadFile, POST/uploadChunk, POST/mergeChunks, POST/:sessionId/downloadFile, PUT/:sessionId, DELETE/:sessionId, POST/:sessionId/terminate)
  - `/app/models` (GET, GET/:modelId, POST, PUT/:modelId, DELETE)
  - `/agents/ws` (GET WebSocket)
  - `/app/taskapi` (POST/tasks, GET/status/:id, GET/result/:id, POST/upload, POST/uploadChunk, POST/mergeChunks)
  - `/version` (GET)
  - `/system/update-data` (POST, GET), `/system/version` (GET)
- 静态文件：`//go:embed static/*`，`NoRoute` 回退 `serveStaticFallback`
- Swagger UI：`/docs/*any`

### F-008 身份中间件
- `setupIdentityMiddleware()` 从 header `username` 取值，默认 "public_user"，存入 gin context

### F-009 WebSocket 消息类型常量（Agent→Server）
- 文件：`common/websocket/agent.go`
- `WSMsgTypeRegister = "register"`
- `WSMsgTypeDisconnect = "disconnect"`
- `WSMsgTypeLiveStatus = "liveStatus"`
- `WSMsgTypePlanUpdate = "planUpdate"`
- `WSMsgTypeNewPlanStep = "newPlanStep"`
- `WSMsgTypeStatusUpdate = "statusUpdate"`
- `WSMsgTypeToolUsed = "toolUsed"`
- `WSMsgTypeResultUpdate = "resultUpdate"`
- `WSMsgTypeActionLog = "actionLog"`
- `WSMsgTypeError = "error"`

### F-010 Server→Agent 消息类型
- `WSMsgTypeTaskAssign = "task_assign"`（在 task_manager.go 中定义）
- `ServerMsgTypeRegisterResp = "register_ack"`
- `ServerMsgTypeTerminate = "terminate"`

### F-011 WebSocket 常量
- `maxMessageSize = 512 * 1024 * 1024`
- `pongWait = 120 * time.Second`
- `pingPeriod = (pongWait * 8) / 10`
- `writeWait = 60 * time.Second`

### F-012 AgentConnection 结构
- 文件：`common/websocket/agent.go`
- 字段：`conn *websocket.Conn`, `agentID string`, `stateMu sync.RWMutex`, `writeMu sync.Mutex`, `isActive bool`
- 方法：`handleConnection`, `handleRegister`, `handleDisconnect`, `writePump`, `cleanup`, `sendError`, `handleAgentEvent`

### F-013 AgentManager 结构
- 字段：`connections map[string]*AgentConnection`, `mu sync.RWMutex`, `taskManager *TaskManager`
- `NewAgentManager()`, `HandleAgentWebSocket() gin.HandlerFunc`
- `GetAvailableAgents() []*AgentConnection`
- `SetTaskManager(taskManager *TaskManager)`

### F-014 AgentRegisterContent 结构
- 字段：`AgentID string (agent_id, required)`, `Hostname string (hostname, required)`, `IP string (ip, required,ip)`, `Version string (version, required)`, `Capabilities []string`, `Meta string`
- 使用 `github.com/go-playground/validator/v10` 验证

### F-015 TaskManager 结构
- 文件：`common/websocket/task_manager.go`
- 字段：`mu sync.RWMutex`, `tasks map[string]*TaskCreateRequest`, `agentManager *AgentManager`, `taskStore *database.TaskStore`, `modelStore *database.ModelStore`, `fileConfig *FileUploadConfig`, `sseManager *SSEManager`, `dispatchCounter uint64`
- `NewTaskManager(agentManager, taskStore, modelStore, fileConfig, sseManager)`
- 任务状态常量：`TaskStatusTodo="todo"`, `TaskStatusDoing="doing"`, `TaskStatusDone="done"`, `TaskStatusError="error"`, `TaskStatusTerminated="terminated"`

### F-016 TaskManager 方法
- `AddTask(req *TaskCreateRequest, traceID string) error`
- `AddTaskApi(req *TaskCreateRequest) error`
- `dispatchTask(sessionId string, traceID string) error` — round-robin 选择 Agent
- `HandleAgentEvent(sessionId string, eventType string, event interface{})`
- `TerminateTask(sessionId, username, traceID string) error`
- `UpdateTask`, `DeleteTask`, `GetTaskDetail`, `GetUserTasks`, `SearchUserTasksSimple`
- `UploadFile`, `UploadFileChunk`, `MergeFileChunks`, `DownloadFile`
- `EstablishSSEConnection`, `CloseSSESession`
- `generateTaskTitle(req *TaskCreateRequest) string` — 根据任务类型生成中文/英文标题
- `CalcSecScore` 在 runner 中

### F-017 任务类型常量（标题生成中引用）
- `agent.TaskTypeAIInfraScan`
- `agent.TaskTypeMcpScan`
- `agent.TaskTypeModelJailbreak`
- `agent.TaskTypeModelRedteamReport`
- `agent.TaskTypeAgentScan`
- `agent.TaskTypeSkillScan`

### F-018 TaskCreateRequest 结构
- 文件：`common/websocket/task.go`
- 字段：`ID string`, `SessionID string`, `Username string`, `Task string (taskType)`, `Timestamp int64`, `Content string`, `Params map[string]interface{}`, `Attachments []string`, `CountryIsoCode string`

### F-019 TaskEventMessage 结构
- 字段：`ID string`, `Type string`, `SessionID string`, `Timestamp int64`, `Event interface{}`

### F-020 事件体结构（task.go）
- `LiveStatusEvent`: ID, Type, Timestamp, Text
- `PlanUpdateEvent`: ID, Type, Timestamp, Tasks []PlanTaskItem
- `PlanTaskItem`: StepID, Status, Title, StartedAt
- `NewPlanStepEvent`: ID, Type, Timestamp, StepID, Title
- `StatusUpdateEvent`: ID, Type, Timestamp, AgentStatus, Brief, Description, NoRender, PlanStepID
- `ToolUsedEvent`: ID, Type, Timestamp, Description, PlanStepID, StatusID, Tools []ToolInfo, Detail
- `ToolInfo`: ToolID, Tool, Status, Brief, Message, Result
- `ActionLogEvent`: ID, Type, Timestamp, ActionID, Tool, PlanStepID, ActionLog
- `ResultUpdateEvent`: ID, Type, Timestamp, Result interface{}
- `TaskAssignMessage`: Type, Content TaskContent
- `TaskContent`: SessionID, TaskType, Content, Params, Attachments, Timeout, CountryIsoCode

### F-021 WebSocket 基础类型（types.go）
- `WSMessage`: Type string, Content interface{}
- `Response`: Status int, Message string, Data interface{}
- `ScanRequest`: ScanType, Target []string, Headers map[string]string, Lang
- `ReportInfo`: SecScore, HighRisk, MiddleRisk, LowRisk
- `ScanRet`: Status int, Msg string
- `Log`: Message string, Level string
- 消息类型常量：`WSMsgTypeLog="log"`, `WSMsgTypeScanResult="result"`, `WSMsgTypeProcessInfo="processing"`, `WSMsgTypeReportInfo="report"`, `WSMsgTypeScanRet="scan_ret"`

### F-022 SSE 管理器
- 文件：`common/websocket/sse_manager.go` 存在
- `NewSSEManager()`, `AddConnection`, `RemoveConnection`, `SendEvent`, `HasConnection`

### F-023 文件上传安全
- `validateFileUpload(header)` 检查 `..`, `/`, `\`
- `validatePathSafety(targetPath)` 确保路径在 UploadDir 内
- 分片上传临时目录 `temp/{fileID}/chunk_{index}`
- 文件名安全化：`generateSecureFileName` 生成 `{baseName}_{uuid}{ext}`

## 3. Runner 扫描引擎

### F-024 Runner 结构
- 文件：`common/runner/runner.go`
- 字段：`Options *options.Options`, `hp *httpx.HTTPX`, `hm *hybrid.HybridMap`, `rateLimiter ratelimit.Limiter`, `result chan HttpResult`, `fpEngine *preload.Runner`, `advEngine *vulstruct.AdvisoryEngine`, `total int`, `done chan struct{}`, `callback func(interface{})`

### F-025 Runner 初始化
- `New(options2 *options.Options) (*Runner, error)` 依次调用：
  - `initStorage()` — hybrid.DefaultDiskOptions
  - `processTargets()` — 处理 --target/--file/--localscan，支持 CIDR 展开
  - `initComponents()` — ratelimit, fastdialer, httpx
  - `initFingerprints()` — 加载 data/fingerprints/*.yaml
  - `initVulnerabilityDB()` — 加载 data/vuln/ 或 data/vuln_en/

### F-026 目标处理
- `processTargetList(targets)` 对每个目标判断 `utils.IsCIDR(t)`，CIDR 调用 `IPAddresses(t)` 展开
- LocalScan 调用 `utils.GetLocalOpenPorts()` 获取本机开放端口
- 使用 `sizedwaitgroup.New(r.Options.RateLimit)` 控制并发

### F-027 扫描流程
- `RunEnumeration()` 启动 `handleOutput` goroutine，遍历 hm 中所有目标
- 不带 http 前缀的目标调用 `runHostRequest(domain)` — 先 http 再 https 重试
- 带 http 前缀的调用 `runDomainRequest(fullUrl)`
- `extractContent(fullUrl, resp, respTime)` 提取：
  - 状态码彩色输出
  - 3xx 跳转跟随 Location
  - favicon hash：`utils.FaviconHash(iconData)`
  - 指纹匹配：`r.fpEngine.RunFpReqs(fullUrl, 10, faviconHash)`
  - 漏洞匹配：`r.advEngine.GetAdvisories(item.Name, item.Version, isInternal)`

### F-028 安全评分
- `CalcSecScore(advisories []vulstruct.Info) CallbackReportInfo`
- high/critical 每个 -70，medium 每个 -30，low 每个 -10
- 基础分 100，最低 0
- 支持中英文严重级别："high"/"critical"/"高危"/"严重"，"medium"/"中危"

### F-029 回调类型（types.go）
- `CallbackScanResult`: TargetURL, StatusCode, Title, Fingerprint, Vulnerabilities, Resp, ScreenShot, Reason, Summary
- `CallbackProcessInfo`: Current, Total
- `CallbackReportInfo`: SecScore, HighRisk, MediumRisk, LowRisk
- `CallbackErrorInfo`: Target, Error
- `FpInfos`: FpName, Vuls, Desc
- `Step01`: Text

### F-030 AI 截图分析（ai.go）
- `LoadSensitivePrompt(language)` 返回内网未鉴权风险分析 prompt 模板
- `LoadWebPageScreenShotSummary(language)` 返回网页截图描述 prompt
- `ScreenShot(url)` 调用 `chromium.NewWebScreenShotWithOptions()`
- `Analysis(url, resp, language, model)` 返回 screenshotData, *vulstruct.Info, summary, error
- `extractTag(text, tag)` 提取 `<tag>...</tag>` 内容

## 4. 指纹 DSL 解析器

### F-031 指纹数据结构
- 文件：`common/fingerprints/parser/parser.go`
- `FingerPrintInfo`: Name, Author, Example []string, Desc, Severity, Metadata map[string]string, Recommendation int
- `Extractor`: Part, Group, Regex
- `HttpRule`: Method, Path, Matchers []string, Data, dsl []*Rule, VersionRange, Extractor
- `FingerPrint`: Info FingerPrintInfo, Http []HttpRule, Version []HttpRule
- `Config`: Body string, Header string, Icon int32, Hash string
- `AdvisoryConfig`: Version string, IsInternal bool
- `FpResult`: Name, Version

### F-032 Token 类型
- 文件：`common/fingerprints/parser/token.go`
- 内容 token：`tokenBody="body"`, `tokenHeader="header"`, `tokenIcon="icon"`, `tokenHash="hash"`, `tokenText="text"`
- 比较操作符：`tokenContains="="`, `tokenFullEqual="=="`, `tokenNotEqual="!="`, `tokenRegexEqual="~="`
- 逻辑操作符：`tokenAnd="&&"`, `tokenOr="||"`
- 括号：`tokenLeftBracket="("`, `tokenRightBracket=")"`
- 版本 token：`tokenVersion="version"`, `tokenIsInternal="is_internal"`
- 版本比较：`tokenGt=">"`, `tokenGte=">="`, `tokenLt="<"`, `tokenLte="<="`

### F-033 词法分析
- `ParseTokens(s string) ([]Token, error)` — 支持 body/header/icon/hash
- `ParseAdvisorTokens(s string) ([]Token, error)` — 支持 version/is_internal
- `parseTokensWithOptions(s, validKeywords)` 公共实现
- 支持双引号字符串，转义 `\"`
- `CheckBalance(tokens)` 检查括号匹配

### F-034 AST 节点
- 文件：`common/fingerprints/parser/synax.go`
- `Exp` 接口：`Name() string`
- `Rule` struct：`root Exp`
- `dslExp`：op, left, right, cacheRegx *regexp.Regexp
- `logicExp`：op, left Exp, right Exp
- `bracketExp`：inner Exp

### F-035 语法解析与求值
- `TransFormExp(tokens) (*Rule, error)`
- `parseExpr`, `parsePrimaryExpr` 递归下降
- `Rule.Eval(config *Config) bool` — 指纹匹配，支持 =(contains), ==(exact), !=, ~=(regex)
- `Rule.AdvisoryEval(config *AdvisoryConfig) bool` — 版本比较，使用 `github.com/hashicorp/go-version`
- `versionCheck(version)` 去除 v 前缀，字母替换为 .0，"latest" → "999"
- `Rule.hashUsage()` 返回 (usesHash, hashOnly)，hash 不能与其他 matcher 共存
- `InitFingerPrintFromData(data []byte) (*FingerPrint, error)` 编译所有 matchers
- `compileMatchers(rules)` 编译时校验 hash 互斥规则

## 5. 漏洞结构

### F-036 Info 结构
- 文件：`pkg/vulstruct/advisory.go`
- yaml 标签：`name`, `cve`, `summary`, `details`, `cvss`, `severity`, `security_advise`, `references`, `author`
- 字段：FingerPrintName, CVEName, Summary, Details, CVSS, Severity, SecurityAdvise, References []string, Author

### F-037 VersionVul 结构
- 文件：`pkg/vulstruct/scanner.go`
- 字段：`Info Info`, `Rule string`, `RuleCompile *parser.Rule`, `References []string`
- 自定义 `UnmarshalYAML`，rule 字段必填
- `ReadVersionVul(body []byte) (*VersionVul, error)` 解析 YAML 并编译规则

### F-038 AdvisoryEngine
- 文件：`pkg/vulstruct/advisory.go`
- 字段：`ads []VersionVul`
- `NewAdvisoryEngine() *AdvisoryEngine`
- `LoadFromDirectory(dir string) error` — 递归扫描 .yaml
- `LoadFromHost(host string) error` — HTTP 获取
- `GetAdvisories(packageName, version string, isInternal bool) ([]VersionVul, error)`
- `GetCount() int`, `GetAll() []VersionVul`
- 匹配逻辑：FingerPrintName 相等，version 非空且 Rule 非空时调用 `RuleCompile.AdvisoryEval`

## 6. Agent 客户端与任务

### F-039 Agent 结构
- 文件：`common/agent/agent.go`
- 字段：`info AgentInfo`, `serverURL string`, `conn *websocket.Conn`, `Tasks []*TaskContext`, `taskFunc []TaskInterface`, `sendChan chan interface{}`, `ctx context.Context`, `cancel context.CancelFunc`, `mutex sync.RWMutex`
- `NewAgent(config AgentConfig) *Agent`
- `RegisterTaskFunc(taskFunc TaskInterface)`
- `Start() error` — connect + handleSend goroutine + handleReceive
- `Stop()` — cancel 所有任务，关闭连接

### F-040 AgentInfo 结构
- 文件：`common/agent/types.go`
- 字段：ID, HostName, IP, Version, Capabilities []string, Metadata

### F-041 任务类型常量
- `TaskTypeTestDemo = "Test-Demo"`
- `TaskTypeAIInfraScan = "AI-Infra-Scan"`
- `TaskTypeMcpScan = "Mcp-Scan"`
- `TaskTypeModelRedteamReport = "Model-Redteam-Report"`
- `TaskTypeModelJailbreak = "Model-Jailbreak"`
- `TaskTypeAgentScan = "Agent-Scan"`
- `TaskTypeSkillScan = "Skill-Scan"`

### F-042 TaskInterface
- `GetName() string`
- `Execute(ctx context.Context, request TaskRequest, callbacks TaskCallbacks) error`

### F-043 TaskCallbacks
- 字段：ResultCallback, ToolUseLogCallback, ToolUsedCallback, NewPlanStepCallback, StepStatusUpdateCallback, PlanUpdateCallback, ErrorCallback

### F-044 TaskRequest
- 字段：SessionId, TaskType, Params json.RawMessage, Timeout int, Content, Language, Attachments []string

### F-045 状态枚举
- 任务状态：pending, running, complete, failed
- 插件状态：doing, done
- Agent 状态：running, completed, failed, idle
- 子任务状态：todo, doing, done

### F-046 AIInfraScanAgent
- 文件：`common/agent/tasks.go`
- 结构体：`AIInfraScanAgent{Server string}`
- `GetName()` 返回 `TaskTypeAIInfraScan`
- `ScanRequest`: Target []string, Headers, Timeout, Model{Model, Token, BaseUrl}
- 3 步计划：准备扫描环境 / 执行深度扫描 / 智能分析与报告生成
- 对 IP 目标调用 `utils.NmapScan(host, "11434,1337,7000-9000,18789")`
- 使用 `runner.Runner` 纯 Go 扫描
- AI 模式下并发截图+LLM分析，信号量 `maxConcurrentAnalysis=5`
- 最终结果：total, score, results

### F-047 McpTask
- 文件：`common/agent/mcp_task.go`
- 结构体：`McpTask{Server string}`
- `GetName()` 返回 `TaskTypeMcpScan`
- 两种传输模式：
  - code：附件 zip/tar.gz/tgz/whl 解压，或 github.com git clone
  - url：从 content 中正则提取 `https?://[^\s]+`
- 调用命令：`uv run --no-project main.py`
- 参数：--model, --base_url, --api_key, --prompt, --debug, --aig-mode, --language, --header, --repo/--server_url
- code 模式 3 步：信息收集/代码审计/漏洞整理
- url 模式 4 步：信息收集/恶意行为检测/漏洞检测/漏洞整理
- 工作目录：`utils.ResolveMcpScanDir()`

### F-048 AgentTask
- 文件：`common/agent/agent_task.go`
- 结构体：`AgentTask{Server string}`
- `GetName()` 返回 `TaskTypeAgentScan`
- 参数：agent_data (yaml), eval_model{Model, Token, BaseUrl, Limit}
- 写入临时 yaml 文件，传 `--agent_provider`
- 调用：`uv run --no-project main.py`，参数 -m, -k, -u, --agent_provider, --language, --aig-mode
- 3 步：Info Collection / Vulnerability Detection / Vulnerability Review
- 工作目录：`utils.ResolveAgentScanDir()`

### F-049 ModelRedteamReport
- 文件：`common/agent/prompt_tasks.go`
- 结构体：`ModelRedteamReport{Server string}`
- `GetName()` 返回 `TaskTypeModelRedteamReport`
- ModelParams: BaseUrl, Token, Model, Limit
- 参数：model []ModelParams, eval_model, datasets{DataFile, NumPrompts, RandomSeed, PromptColumn}, prompt, techniques
- 调用：`uv run --no-project cli_run.py --async_mode`
- 参数：--model, --base_url, --api_key, --max_concurrent, --evaluate_model, --eval_base_url, --eval_api_key, --techniques Raw, --choice serial/parallel, --lang, --scenarios
- scenarios 支持：`Custom:prompt=...`, `MultiDataset:dataset_file=...,num_prompts=...,random_seed=...`
- 评测集通过 `utils.GetEvaluationsDetail(server, dataName)` 下载
- 3 步：初始化越狱环境 / 执行模型安全评估 / 生成模型安全报告
- 工作目录：`utils.ResolvePromptSecurityDir()`

### F-050 SkillTask
- 文件：`common/agent/skill_task.go`
- 结构体：`SkillTask{Server string}`
- `GetName()` 返回 `TaskTypeSkillScan`
- 仅 code 模式（附件或 github URL）
- 调用：`uv run --no-project main.py`，参数同 McpTask 加 `--repo`
- 3 步：信息收集/代码审计/漏洞整理
- 工作目录：`utils.ResolveSkillScanDir()`

### F-051 Python stdout 桥接
- 文件：`common/agent/parse_cmdline.go`
- `ParseStdoutLine(server, rootDir, tasks, line, callbacks, config, upload)`
- 只解析首字符为 `{` 的 JSON 行
- `CmdContent{Type string, Content json.RawMessage}`
- 支持类型：newPlanStep, statusUpdate, toolUsed, actionLog, resultUpdate, error
- `CmdNewPlanStep{Title, StepId}`
- `CmdStatusUpdate{Brief, Description, StepId, Status}`
- `CmdToolUsed{ToolId, ToolName, Brief, Status, StepId, Params}`
- `CmdActionLog{ToolId, ToolName, Log, StepId}`
- `PromptContent{Results []PromptResults, Total int, Score float32, Attachment string, Jailbreak int}`
- `PromptResults{Status, ModelName, Vulnerability, AttackMethod, Input, Output, Reason}`
- upload=true 时上传 result 中的 attachment 文件

### F-052 Agent 消息发送方法
- `SendTaskResult(sessionId, result)`
- `SendsToolUsedLog(sessionId, actionId, tool, planStepId, actionLog)`
- `SendToolUsed(sessionId, planStepId, statusId, description, tools)`
- `SendNewPlanStep(sessionId, stepId, title)`
- `SendStepStatusUpdate(sessionId, planStepId, statusId, agentStatus, brief, description)`
- `SendPlanUpdate(sessionId, tasks)`
- `SendError(sessionId, msg)`
- `CreateTool(toolId, tool, status, brief, action, param, result) Tool`
- `CreateSubTask(status, title, startedAt, stepId) SubTask`

## 7. internal/mcp

### F-053 Scanner 结构
- 文件：`internal/mcp/scanner.go`
- 字段：`mutex sync.Mutex`, `results []*Issue`, `PluginConfigs []*PluginConfig`, `aiModel *models.OpenAI`, `client *client.Client`, `csvResult [][]string`, `codePath string`, `url string`, `callback func(interface{})`, `language string`, `logger *gologger.Logger`
- `NewScanner(aiConfig, logger)`
- `RegisterPlugin(plugins []string)` 从 `data/mcp/` 加载 yaml
- `InputCommand(ctx, command, argv)` — stdio MCP 客户端
- `InputUrl(ctx, url)` — 尝试 "", "/mcp", "/sse" 三个路径
- `InputSSELink(ctx, link)` — SSE 客户端
- `InputStreamLink(ctx, link)` — Streamable HTTP 客户端
- `InputCodePath(codePath)`
- 使用 `github.com/mark3labs/mcp-go` 库

### F-054 PluginConfig
- 文件：`internal/mcp/plugins.go`
- 字段：
  - Info: ID, Name, Description, Author, Category []string
  - Rules []Rule
  - PromptTemplate string
- `Rule`: Name, Pattern, Description
- `NewYAMLPlugin(configPath)`

### F-055 MCP 类型常量
- `LevelLow="low"`, `LevelMedium="medium"`, `LevelHigh="high"`, `LevelCritical="critical"`
- `MCPTypeCommand="command"`, `MCPTypeSSE="sse"`, `MCPTypeSTREAM="stream"`, `MCPTypeCode="code"`

### F-056 Issue 结构
- 字段：Title, Description, Level, Suggestion, RiskType

### F-057 结果解析
- `ParseIssues(input string) []Issue`
- 正则提取 `<result>...</result>` 块
- 块内提取 `<title>`, `<desc>`, `<level>`, `<risk_type>`, `<suggestion>`
- `SummaryResult(ctx, agent, config)` 调用 LLM 生成总结
- `SummaryChat`, `SummaryReport`

## 8. Python 子系统目录结构

### F-058 mcp-scan/
- 入口：`main.py`, `pyproject.toml`
- 包：`mcp_scan/`
  - `__main__.py`, `main.py`
  - `agent/`: base_agent.py, agent.py
  - `prompt/`: agents/dynamic/*.md, *.md
  - `redteam/`: attacker.py, evaluator.py, orchestrator.py, report.py, strategy.py, target.py
  - `tools/`: execute/, file/, finish/, mcp_tool/, thinking/, dispatcher.py, registry.py
  - `utils/`: aig_logger.py, config.py, extract_vuln.py, llm.py, llm_manager.py, mcp_tools.py, parse.py, pre_scan.py, project_analyzer.py, prompt_manager.py, sarif_formatter.py, tool_context.py

### F-059 agent-scan/
- 入口：`main.py`, `pyproject.toml`, `requirements.txt`, `providers.yaml`
- 包：`agent_scan/`
  - `__init__.py`, `__main__.py`, `main.py`
  - `utils/llm.py`
- 测试：`testcase/case1/main1.py`, `testcase/case3/main.py`

### F-060 AIG-PromptSecurity/
- 入口：`cli_run.py`, `pyproject.toml`
- 包：`cli/`
  - `__init__.py`, `mappings.py`, `models.py`, `parsers.py`
- Dockerfile, LICENSE.md, README.md, README_ZH.md

## 9. 数据规模

### F-061 指纹数据
- 目录：`data/fingerprints/`
- 数量：142 个 .yaml 文件
- 示例：dify.yaml, vllm.yaml, ollama.yaml, ray.yaml, langflow.yaml, flowise.yaml 等

### F-062 漏洞数据
- 中文目录：`data/vuln/`
- 数量：2014 个 .yaml 文件（递归统计）
- 子目录按组件名：dask/, dify/, jan/, mcp/, n8n/, ollama/, ray/, vllm/
- 英文目录：`data/vuln_en/`（ray/, vllm/ 有部署安全提示）

### F-063 MCP 插件规则
- 目录：`data/mcp/`
- 数量：15 个 .yaml 文件
- 文件：cors.yaml, mcp_path_traversal.yaml, mcp_sql_injection.yaml, mcp_ssrf.yaml, mcp_tool_rug_pull.yaml, tool_poisoning.yaml 等

### F-064 评测数据集
- 目录：`data/eval/`
- 数量：17 个 .json 文件
- 示例：advbench.json, cnsafe.json, JailBench-Tiny.json, CBRN-weapon.json, violent.json, misinformation.json 等

## 10. 其他关键事实

### F-065 Options 结构
- 文件：`internal/options/options.go`（未逐行读取，从使用处推断字段）
- 已知字段：Target []string, TargetFile, Output, ProxyURL, TimeOut, RateLimit, FPTemplates, AdvTemplates, ListVulTemplate, CheckVulTargets, LocalScan, Headers []string, Language, WebServer bool, WebServerAddr, APICheckerURL, LoadRemote, Callback func(interface{})

### F-066 preload 指纹引擎
- 文件：`common/fingerprints/preload/preload.go`, `version_range.go`, `version_detection.go`, `mlfow.go`
- `preload.New(hp, fps) *Runner`
- `RunFpReqs(fullUrl string, timeout int, faviconHash int32) []FpResult`
- `CollectedFpReqs() int`

### F-067 许可证与归属
- Copyright 2024-2026 Tencent Zhuque Lab
- Apache License 2.0
- 集成/衍生作品须在文档或 UI 中署名 Tencent Zhuque Lab
- 仓库：https://github.com/Tencent/AI-Infra-Guard

### F-068 前端
- 目录：`frontend/`
- React + TypeScript + Vite
- i18n：zh.json, en.json
- API 客户端：agentApi.ts, evaluationApi.ts, modelApi.ts, pluginApi.ts, relayApi.ts, systemApi.ts, userApi.ts
