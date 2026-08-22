# DeepSeek Reasonix 事实清单

> 信源：`external/libs/ai/agents/DeepSeek-Reasonix`（只读）。所有事实均直接引用 Go 源码的类型、函数签名、接口、常量与调用关系，逐字精确，零推测。相对路径为仓库根目录下的路径。

## 模块与构建入口

- F-001: 文件 go.mod 第1行，`module reasonix`
- F-002: 文件 go.mod 第3-5行，`go 1.25.0` / `toolchain go1.26.6`
- F-003: 文件 cmd/reasonix/main.go 第1行，`// Command reasonix is a config- and plugin-driven coding agent CLI.`
- F-004: 文件 cmd/reasonix/main.go 第13-16行，blank import `_ "reasonix/internal/provider/anthropic"`、`_ "reasonix/internal/provider/openai"`、`_ "reasonix/internal/provider/responses"`、`_ "reasonix/internal/tool/builtin"`
- F-005: 文件 cmd/reasonix/main.go 第22-26行，`var (version = "dev"; gitCommit = ""; buildTimeUTC = "")`
- F-006: 文件 cmd/reasonix/main.go 第38-40行，`func main() { os.Exit(runWithCrashCapture(os.Args[1:], version)) }`
- F-007: 文件 cmd/reasonix/main.go 第42-50行，`func runWithCrashCapture(args []string, buildVersion string) (exitCode int)`，panics 时调用 `crashreport.CapturePanic(config.ReasonixHomeDir(), buildVersion, recovered, debug.Stack())`
- F-008: 文件 internal/config/paths.go 第314行，`func ReasonixHomeDir() string { return reasonixHomeDir() }`

## internal/provider（模型提供方抽象）

- F-009: 文件 internal/provider/provider.go 第968-975行，`type Provider interface { Name() string; Stream(ctx context.Context, req Request) (<-chan Chunk, error) }`
- F-010: 文件 internal/provider/provider.go 第1110行，`type Factory func(cfg Config) (Provider, error)`
- F-011: 文件 internal/provider/provider.go 第1116-1121行，`func Register(kind string, f Factory)`，kind 重复时 `panic("provider: duplicate kind " + kind)`
- F-012: 文件 internal/provider/provider.go 第1124-1128行，`func New(kind string, cfg Config) (Provider, error)`，kind 未注册时返回 `fmt.Errorf("provider: unknown kind %q ...")`
- F-013: 文件 internal/provider/provider.go 第45-46行，`type Message struct { Role Role; Content string }`
- F-014: 文件 internal/provider/provider.go 第58行，字段 `ReasoningContent string` json tag `reasoning_content`
- F-015: 文件 internal/provider/provider.go 第73行，字段 `ToolCalls []ToolCall`
- F-016: 文件 internal/provider/provider.go 第203行，`type ToolCall struct`
- F-017: 文件 internal/provider/provider.go 第230-240行，`type Request struct { Messages []Message; Tools []ToolSchema; Temperature *float64; MaxTokens int; ResponseFormat *ResponseFormat; EffortOverride string }`
- F-018: 文件 internal/provider/provider.go 第720行，`type Usage struct`
- F-019: 文件 internal/provider/provider.go 第865-882行，`type Chunk struct { Type ChunkType; Text string; Signature string; ReasoningID string; ReasoningStatus string; ToolCall *ToolCall; ArgChars int; ResponsesItem json.RawMessage; ServerSearch *ServerSearchCall; Usage *Usage; Err error }`
- F-020: 文件 internal/provider/provider.go 第252-261行，常量 `DefaultOrdinaryOutputTokens = 16 * 1024`、`DefaultReasoningOutputTokens = 32 * 1024`、`DefaultHighReasoningOutputTokens = 64 * 1024`、`DefaultHighOutputTokens = 128 * 1024`、`DeepSeekMaxOutputTokens = 384_000`
- F-021: 文件 internal/provider/provider.go 第266行，`func AutoOutputBudget(reasoningEnabled bool, effort string) int`
- F-022: 文件 internal/provider/provider.go 第984-986行，`type ToolCallReasoningPolicy interface { RequiresToolCallReasoning() bool }`

## internal/agent（Agent 运行时）

- F-023: 文件 internal/agent/agent.go 第282行，`type Agent struct`
- F-024: 文件 internal/agent/agent.go 第283-288行，字段 `agentConfig`、`svc agentServices`、`sess sessionRuntime`
- F-025: 文件 internal/agent/agent.go 第291-292行，字段 `responseLanguage atomic.Value`、`reasoningLanguage atomic.Value`
- F-026: 文件 internal/agent/agent.go 第303行，字段 `planMode atomic.Bool`
- F-027: 文件 internal/agent/agent.go 第315行，字段 `mutationDependencyBarrier atomic.Pointer[mutationBarrierCause]`
- F-028: 文件 internal/agent/agent.go 第334-337行，字段 `steerMu sync.Mutex`、`steerQueue []steerEntry`、`steerConsumed bool`
- F-029: 文件 internal/agent/agent.go 第348行，字段 `task taskRuntime`
- F-030: 文件 internal/agent/agent.go 第369行，字段 `turn turnRuntime`
- F-031: 文件 internal/agent/agent.go 第410行，`type KeepPolicy int`
- F-032: 文件 internal/agent/agent.go 第866行，`type Options struct`
- F-033: 文件 internal/agent/agent.go 第1051行，`func New(prov provider.Provider, tools *tool.Registry, session *Session, opts Options, sink event.Sink) *Agent`
- F-034: 文件 internal/agent/agent.go 第246行，`const DefaultMaxSubagentDepth = 2`
- F-035: 文件 internal/agent/agent.go 第250行，`func NormalizeMaxSubagentDepth(depth int) int`
- F-036: 文件 internal/agent/agent.go 第262行，`type ToolHooks interface`
- F-037: 文件 internal/agent/agent.go 第42行，`const maxToolOutputBytes = 32 * 1024`
- F-038: 文件 internal/agent/agent.go 第626行，`const MidTurnSteerPrefix = "[Mid-turn steer queued by the user. ...]"`

## internal/agent/session.go（会话状态）

- F-039: 文件 internal/agent/session.go 第19行，`type Session struct`
- F-040: 文件 internal/agent/session.go 第20-22行，字段 `mu sync.RWMutex`、`Messages []provider.Message`、`version uint64`
- F-041: 文件 internal/agent/session.go 第23行，字段 `rewriteVersion int`
- F-042: 文件 internal/agent/session.go 第81-87行，`func NewSession(system string) *Session`
- F-043: 文件 internal/agent/session.go 第90-95行，`func (s *Session) Add(m provider.Message)`

## internal/agent/scheduler.go（子代理调度）

- F-044: 文件 internal/agent/scheduler.go 第11行，`type SubagentSlotStatus string`
- F-045: 文件 internal/agent/scheduler.go 第13-18行，常量 `SubagentSlotQueued = "queued"`、`SubagentSlotRunning = "running"`、`SubagentSlotDone = "done"`、`SubagentSlotFailed = "failed"`
- F-046: 文件 internal/agent/scheduler.go 第21-34行，`type AcquireRequest struct { Writer bool; WritePaths WritePathSet; Nested bool; Label string }`
- F-047: 文件 internal/agent/scheduler.go 第38-55行，`type SubagentScheduler struct`，含 `maxTotal int`、`maxWriters int`、`parentClaims []WritePathSet`
- F-048: 文件 internal/agent/scheduler.go 第65-68行，`func NewSubagentScheduler(maxTotal, maxWriters int) *SubagentScheduler`

## internal/agent/task.go（子代理任务工具）

- F-049: 文件 internal/agent/task.go 第45行，`const DefaultTaskSystemPrompt = ...`
- F-050: 文件 internal/agent/task.go 第55行，`const DefaultReadOnlyTaskSystemPrompt = ...`
- F-051: 文件 internal/agent/task.go 第248行，`type TaskTool struct`
- F-052: 文件 internal/agent/task.go 第325行，`func NewTaskToolWithOptions(opts TaskToolOptions) *TaskTool`
- F-053: 文件 internal/agent/task.go 第360行，`func NewTaskTool(prov provider.Provider, pricing *provider.Pricing, parentReg *tool.Registry, ...)`
- F-054: 文件 internal/agent/task.go 第538行，`type ReadOnlyTaskTool struct`
- F-055: 文件 internal/agent/task.go 第1722行，`func RunSubAgentWithSession(ctx context.Context, prov provider.Provider, reg *tool.Registry, sess *Session, prompt string, opts Options, sink event.Sink) (string, error)`
- F-056: 文件 internal/agent/task.go 第1832行，`func NewPlannerAgent(prov provider.Provider, reg *tool.Registry, sess *Session, opts Options, sink event.Sink) *Agent`
- F-057: 文件 internal/agent/task.go 第1883行，`func RunReadOnlySubAgentWithSession(...)`

## internal/acp（ACP v1 协议层）

- F-058: 文件 internal/acp/protocol.go 第24行，`const ProtocolVersion = 1`
- F-059: 文件 internal/acp/protocol.go 第27-33行，JSON-RPC 错误码 `ErrParse = -32700`、`ErrInvalidRequest = -32600`、`ErrMethodNotFound = -32601`、`ErrInvalidParams = -32602`、`ErrInternal = -32603`
- F-060: 文件 internal/acp/protocol.go 第40-44行，`type InitializeParams struct { ProtocolVersion int; ClientInfo *Implementation; ClientCapabilities ClientCapabilities }`
- F-061: 文件 internal/acp/protocol.go 第73-78行，`type InitializeResult struct { ProtocolVersion int; AgentCapabilities AgentCapabilities; AgentInfo Implementation; AuthMethods []AuthMethod }`
- F-062: 文件 internal/acp/protocol.go 第81-87行，`type AgentCapabilities struct`，含 `LoadSession bool`、`SessionCapabilities`、`PromptCapabilities`、`MCPCapabilities`
- F-063: 文件 internal/acp/protocol.go 第153-157行，`type MCPCapabilities struct { HTTP bool; SSE bool }`
- F-064: 文件 internal/acp/protocol.go 第183-186行，`type SessionNewParams struct { Cwd string; MCPServers []MCPServerSpec }`
- F-065: 文件 internal/acp/protocol.go 第263-268行，`type SessionNewResult struct { SessionID string; Models *SessionModelState; Modes *SessionModeState; ConfigOptions []SessionConfigOption }`
- F-066: 文件 internal/acp/protocol.go 第314-318行，`type SessionLoadParams struct { SessionID string; Cwd string; MCPServers []MCPServerSpec }`
- F-067: 文件 internal/acp/protocol.go 第475-482行，`type SessionPromptParams struct { SessionID string; Prompt []ContentBlock; Action string }`
- F-068: 文件 internal/acp/protocol.go 第486-489行，`type SessionSteerParams struct { SessionID string; Prompt []ContentBlock }`
- F-069: 文件 internal/acp/protocol.go 第498行，`const sessionSteerMethod = "_reasonix.io/session/steer"`
- F-070: 文件 internal/acp/protocol.go 第500-511行，`sessionInboxEnqueueMethod = "_reasonix.io/session/inbox/enqueue"` 等 9 个 inbox 方法常量
- F-071: 文件 internal/acp/protocol.go 第585-588行，`type SessionUpdateParams struct { SessionID string; Update any }`
- F-072: 文件 internal/acp/protocol.go 第591-595行，`type messageChunk struct { SessionUpdate string; Content ContentBlock; Metadata *updateMeta }`
- F-073: 文件 internal/acp/protocol.go 第621-629行，`type toolCall struct`，含 `ToolCallID string`、`Status string`、`RawInput json.RawMessage`
- F-074: 文件 internal/acp/protocol.go 第701-709行，`type FSReadTextFileParams struct { SessionID string; Path string; Line *int; Limit *int }`
- F-075: 文件 internal/acp/protocol.go 第783-788行，`type PermissionOptionKind string` 与常量 `OptAllowOnce = "allow_once"`、`OptAllowAlways = "allow_always"`、`OptRejectOnce = "reject_once"`、`OptRejectAlways = "reject_always"`
- F-076: 文件 internal/acp/protocol.go 第797-802行，`type PermissionRequestParams struct { SessionID string; ToolCall PermissionToolCall; Options []PermissionOption }`
- F-077: 文件 internal/acp/protocol.go 第455-470行，`func FlattenPrompt(blocks []ContentBlock) string`
- F-078: 文件 internal/acp/stop_reason.go 第4-8行，常量 `StopEndTurn StopReason = "end_turn"`、`StopCancelled = "cancelled"`、`StopMaxTurnRequests = "max_turn_requests"`
- F-079: 文件 internal/acp/server.go 第16行，`const maxMessageBytes = 32 << 20`
- F-080: 文件 internal/acp/server.go 第21行，`type RequestHandler func(ctx context.Context, params json.RawMessage) (any, error)`
- F-081: 文件 internal/acp/server.go 第36-39行，`type RPCError struct { Code int; Message string }`
- F-082: 文件 internal/acp/server.go 第51-68行，`type Conn struct`，含 `nextID atomic.Int64`、`pending map[int64]chan rpcResult`
- F-083: 文件 internal/acp/server.go 第107-118行，`func NewConn(r io.Reader, w io.Writer) *Conn`
- F-084: 文件 internal/acp/server.go 第133行，`func (c *Conn) Serve(ctx context.Context) error`
- F-085: 文件 internal/acp/server.go 第283行，`func (c *Conn) Notify(method string, params any) error`
- F-086: 文件 internal/acp/server.go 第293行，`func (c *Conn) Request(ctx context.Context, method string, params any) (json.RawMessage, error)`
- F-087: 文件 internal/acp/service.go 第69行，`type Factory interface`
- F-088: 文件 internal/acp/service.go 第116行，`type AgentInfo struct`
- F-089: 文件 internal/acp/service.go 第128行，`func Serve(ctx context.Context, r io.Reader, w io.Writer, factory Factory, info AgentInfo) error`
- F-090: 文件 internal/acp/service.go 第167行，`type service struct`
- F-091: 文件 internal/acp/service.go 第267行，`type acpSession struct`
- F-092: 文件 internal/acp/dispatch.go 第26行，`type notifier interface`
- F-093: 文件 internal/acp/dispatch.go 第51行，`type updateSink struct`

## internal/bot（机器人网关）

- F-094: 文件 internal/bot/types.go 第12行，`type Platform string`
- F-095: 文件 internal/bot/types.go 第55行，`type InboundMessage struct`
- F-096: 文件 internal/bot/types.go 第94行，`type OutboundMessage struct`
- F-097: 文件 internal/bot/types.go 第182-203行，`type Adapter interface { Platform() Platform; Start(ctx context.Context) error; Stop() error; Send(ctx context.Context, msg OutboundMessage) (SendResult, error); SendTyping(ctx context.Context, chatID string) error; Messages() <-chan InboundMessage; Name() string }`
- F-098: 文件 internal/bot/types.go 第212行，`type MessageHandler func(ctx context.Context, msg InboundMessage)`
- F-099: 文件 internal/bot/gateway.go 第26行，`type GatewayConfig struct`
- F-100: 文件 internal/bot/gateway.go 第172-200行，`type BotGateway struct`，含 `controllers map[string]*sessionState`、`buildController func(context.Context, boot.Options) (*control.Controller, error)`
- F-101: 文件 internal/bot/gateway.go 第287行，`func NewGateway(cfg GatewayConfig, adapters map[Platform]Adapter, logger *slog.Logger) *BotGateway`
- F-102: 文件 internal/bot/gateway.go 第297行，`func NewGatewayWithAdapterBindings(cfg GatewayConfig, adapters []AdapterBinding, logger *slog.Logger) *BotGateway`
- F-103: 文件 internal/bot/gateway.go 第2602行，`const defaultBotApprovalTimeout = 30 * time.Minute`
- F-104: 文件 internal/bot/session.go 第174行，`type SessionManager struct`
- F-105: 文件 internal/bot/session.go 第184行，`func NewSessionManager(debounce time.Duration) *SessionManager`
- F-106: 文件 internal/bot/session.go 第92行，`func BuildSessionKey(src SessionSource) string`
- F-107: 文件 internal/bot/connloop.go 第25行，`type RetryConfig struct`
- F-108: 文件 internal/bot/connloop.go 第89行，`func RunWithRetry(ctx context.Context, log *slog.Logger, name string, cfg RetryConfig, attempt func(context.Context) error)`
- F-109: 文件 internal/bot/feishu/feishu.go 第132行，`func New(cfg config.FeishuBotConfig, logger *slog.Logger) bot.Adapter`
- F-110: 文件 internal/bot/feishu/feishu.go 第620行，`func SendText(ctx context.Context, cfg config.FeishuBotConfig, chatID, text string) (bot.SendResult, error)`

## internal/cli（命令行与 TUI）

- F-111: 文件 internal/cli/cli.go 第59行，`func Run(args []string, version string) int`
- F-112: 文件 internal/cli/cli.go 第65行，`func RunWithBuildInfo(args []string, info BuildInfo) int`
- F-113: 文件 internal/cli/cli.go 第485行，`func runAgent(args []string, version string) int`
- F-114: 文件 internal/cli/cli.go 第977行，`func chatREPL(args []string, version string) int`
- F-115: 文件 internal/cli/cli.go 第1445行，`func setupConfig(args []string) int`
- F-116: 文件 internal/cli/chat_tui.go 第52行，`type chatTUI struct`
- F-117: 文件 internal/cli/chat_tui.go 第636行，`func newChatTUI(ctrl control.SessionAPI, missing string, eventCh chan event.Event, termW int) chatTUI`
- F-118: 文件 internal/cli/chat_tui.go 第467行，`const maxEventDrain = 512`
- F-119: 文件 internal/cli/chat_tui.go 第2996行，`var toolWorkingFrames = []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"}`

## internal/checkpoint（检查点与恢复）

- F-120: 文件 internal/checkpoint/checkpoint.go 第38行，`type FileSnap struct`
- F-121: 文件 internal/checkpoint/checkpoint.go 第70行，`type Checkpoint struct`
- F-122: 文件 internal/checkpoint/checkpoint.go 第144行，`type Store struct`
- F-123: 文件 internal/checkpoint/checkpoint.go 第169行，`func New(dir, root string) *Store`
- F-124: 文件 internal/checkpoint/checkpoint.go 第897行，`var errSymlinkPath = errors.New("workspace path contains symbolic link")`
- F-125: 文件 internal/checkpoint/blob.go 第16行，`type BlobStore struct`
- F-126: 文件 internal/checkpoint/blob.go 第181行，`func Digest(data []byte) string`
- F-127: 文件 internal/checkpoint/capture.go 第17行，`type Fingerprint struct`
- F-128: 文件 internal/checkpoint/capture.go 第43行，`func CapturePath(path string, opts CaptureOptions) (Fingerprint, *CoverageGap, error)`

## internal/billing（计费）

- F-129: 文件 internal/billing/money.go 第14行，`type Money struct`
- F-130: 文件 internal/billing/money.go 第21行，`const amountScale int64 = 1_000_000_000`
- F-131: 文件 internal/billing/money.go 第24行，`type Amount int64`
- F-132: 文件 internal/billing/balance.go 第21行，`type Balance struct`
- F-133: 文件 internal/billing/balance.go 第86行，`var httpClient = &http.Client{Timeout: 12 * time.Second}`
- F-134: 文件 internal/billing/balance.go 第92行，`func Fetch(ctx context.Context, url, apiKey string) (*Balance, error)`
- F-135: 文件 internal/billing/catalog.go 第15行，`var deepSeekV4August2026EffectiveAt = time.Date(2026, time.August, 16, 16, 0, 0, 0, time.UTC)`
- F-136: 文件 internal/billing/catalog.go 第18行，`type CatalogEntry struct`
- F-137: 文件 internal/billing/catalog.go 第53行，`func OfficialCatalog() []CatalogEntry`
- F-138: 文件 internal/billing/catalog.go 第117行，`func DeepSeekRateBand(at time.Time) string`
- F-139: 文件 internal/billing/ledger.go 第13行，`type LedgerEntry struct`
- F-140: 文件 internal/billing/ledger.go 第48行，`const LedgerVersion = 1`

## internal/boot（装配层）

- F-141: 文件 internal/boot/boot.go 第99行，`type Options struct`
- F-142: 文件 internal/boot/boot.go 第217行，`func build(ctx context.Context, opts Options) (*BuildResult, error)`
- F-143: 文件 internal/boot/boot.go 第2510行，`func NewProvider(e *config.ProviderEntry) (provider.Provider, error)`
- F-144: 文件 internal/boot/boot.go 第75行，`var ErrUnknownModel = errors.New("unknown model")`

## desktop（Wails 桌面应用）

- F-145: 文件 desktop/app.go 第127行，`type App struct`
- F-146: 文件 desktop/app.go 第413行，`func NewApp() *App`
- F-147: 文件 desktop/app.go 第79行，`const eventChannel = "agent:event"`
- F-148: 文件 desktop/app.go 第81行，`const singleInstanceIDPrefix = "com.reasonix.desktop"`