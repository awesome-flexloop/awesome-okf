# DeepSeek-Reasonix 事实清单

> R 阶段产出。每条事实标注源码路径与行号，不含推断性表述。

## 项目结构与构建

- **F-001**: Go module 名为 `reasonix`，Go 版本要求 1.25.0，toolchain 固定为 go1.26.6。`go.mod:1-5`
- **F-002**: 核心依赖包括 charm.land/bubbletea/v2（TUI 框架）、github.com/larksuite/oapi-sdk-go/v3（飞书 SDK）、golang.org/x/net/websocket（QQ WebSocket）、modernc.org/sqlite（纯 Go SQLite）、mvdan.cc/sh/v3（shell 解析）。`go.mod:8-46`
- **F-003**: Makefile 的 `build` 目标使用 `CGO_ENABLED=0 go build` 输出到 `bin/reasonix`，同时构建 `reasonix-plugin-example`。`Makefile:15-17`
- **F-004**: Makefile 的 `cross` 目标交叉编译 6 个目标：darwin/linux/windows × amd64/arm64。`Makefile:81-87`
- **F-005**: 构建元数据通过 `-ldflags` 注入 `main.version`、`main.gitCommit`、`main.buildTimeUTC`。`Makefile:4-7`
- **F-006**: README 描述项目为 "A coding agent you can leave running"，单 Go 二进制，MIT 协议。`README.md:42-44`
- **F-007**: 四种接入方式：terminal（CLI/TUI）、desktop app（Wails）、browser（HTTP/SSE）、editor over ACP。`README.md:44`
- **F-008**: REASONIX.md 是项目常驻指令文件，加载到每个会话的 system prompt 中作为 cache-stable prefix。`REASONIX.md:1-5`
- **F-009**: REASONIX.md 规定分层规则：utility 包不导入 `reasonix/` 下任何包；只有 cli、serve、acp、bot、botruntime、boot 和 hosts（cmd/、desktop/）可导入 control。`REASONIX.md:14-17`
- **F-010**: CLAUDE.md 通过 `@REASONIX.md` 引用同一文件，Reasonix 和 Claude Code 读取同一份常驻指令。`CLAUDE.md:1-6`

## 主入口

- **F-011**: `cmd/reasonix/main.go` 是 CLI 入口，blank import 注册三个 provider：anthropic、openai、responses，以及 builtin 工具包。`cmd/reasonix/main.go:12-17`
- **F-012**: main 函数调用 `runWithCrashCapture`，recover panic 后通过 `crashreport.CapturePanic` 记录再重新 panic。`cmd/reasonix/main.go:38-49`
- **F-013**: `runCLI` 变量调用 `cli.RunWithBuildInfo`，传入版本、gitCommit、buildTimeUTC。`cmd/reasonix/main.go:30-36`

## Agent 核心

- **F-014**: `Agent` 结构体包含 `agentConfig`（嵌入）、`svc agentServices`、`sess sessionRuntime`、`task taskRuntime`、`turn turnRuntime` 等字段。`internal/agent/agent.go:282-399`
- **F-015**: `New` 函数签名为 `func New(prov provider.Provider, tools *tool.Registry, session *Session, opts Options, sink event.Sink) *Agent`。`internal/agent/agent.go:1051`
- **F-016**: `Run` 方法是 agent 主循环入口，签名为 `func (a *Agent) Run(ctx context.Context, input string) (runErr error)`。`internal/agent/agent.go:1239`
- **F-017**: `maxToolOutputBytes` 常量为 32KB，限制 provider 可见的稳定 Content；RawContent 保留完整本地结果。`internal/agent/agent.go:42`
- **F-018**: `maxStreamRecoveries` 为 5，`maxSamplingAttempts` 为 6（1+5），与 Codex 对齐。`internal/agent/agent.go:49-51`
- **F-019**: `DefaultMaxSubagentDepth` 常量为 2；`NormalizeMaxSubagentDepth` 将小于 1 的值规范化为 1。`internal/agent/agent.go:246-255`
- **F-020**: `Gate` 接口定义 `Check(ctx, toolName, args, readOnly) (allow bool, reason string, err error)`，是 per-call 权限门。`internal/agent/agent.go:215-217`
- **F-021**: `Renderer` 接口定义 `Render(text string) string`，在 turn 文本流完成后重绘最终答案。`internal/agent/agent.go:76-78`
- **F-022**: `Asker` 接口定义 `Ask(ctx, questions) ([]event.AskAnswer, error)`，nil 表示无头模式。`internal/agent/agent.go:85-87`
- **F-023**: `planMode` 是 `atomic.Bool` 字段，切换 plan-first 工作流；system prompt 和 tool list 不随 toggle 改变，保持 cache prefix。`internal/agent/agent.go:300-303`
- **F-024**: `Steer` 方法签名为 `func (a *Agent) Steer(text string) bool`，队列 mid-turn 引导消息；返回 false 时调用方需作为新 turn 投递。`internal/agent/agent.go:699-701`
- **F-025**: `Session` 结构体持有 `Messages []provider.Message`，用 `sync.RWMutex` 保护，run loop 是唯一写入者。`internal/agent/session.go:19-21`
- **F-026**: `Session.Rewrite` 方法原子替换消息日志并增加 `rewriteVersion`，reason 参数记录 provider-visible 变更原因。`internal/agent/session.go:264-273`
- **F-027**: `Session.Snapshot` 返回消息副本，供跨 goroutine 安全读取。`internal/agent/session.go:317-320`

## Agent 运行循环

- **F-028**: `runToolLoop` 是主工具循环，每步调用 `streamWithSamplingRecovery`，根据 calls 长度分流到 `handleFinalResponse` 或 `handleToolRound`。`internal/agent/run_loop.go:245-338`
- **F-029**: `streamWithSamplingRecovery` 实现 Codex 风格的 original-request replay：prepare 一次，freeze 请求，最多 6 次 body 尝试。`internal/agent/run_loop.go:345-468`
- **F-030**: `deferredStreamSink` 在 reasoning 到达前缓冲 tool 事件，防止 malformed turn 闪现重复卡片。`internal/agent/run_loop.go:55-119`
- **F-031**: `beginRunTurn` 处理 evidence scope、delivery 分类、background-job evidence re-lease、初始 user-turn 持久化。`internal/agent/run_loop.go:125-241`
- **F-032**: `handleFinalResponse` 处理无工具调用的 assistant turn：recovery pause、readiness retry、empty final retry、executor handoff nudge、steer drain。`internal/agent/run_loop.go:523-610`
- **F-033**: `handleToolRound` 执行工具批次、持久化工具消息、处理 cancellation、todo stall tracking、recovery finalization pause、max-steps grace round。`internal/agent/run_loop.go:616-723`
- **F-034**: stream retry 退避策略为 ~0.5s, 1s, 2s, 4s, 8s 带 jitter。`internal/agent/run_loop.go:502-517`
- **F-035**: `emitTurnPhase` 发布无内容的 host phase 事件，phase 通过 `event.TurnPhaseName` 标识。`internal/agent/turn_phase.go:14-19`

## Arbiter 与 Governor

- **F-036**: `verdict` 类型定义四级升级阶梯：`verdictContinue`、`verdictAdvise`、`verdictRedirect`、`verdictLand`。`internal/agent/arbiter.go:13-18`
- **F-037**: `applyInterventions` 将一轮信号折叠为最强 verdict，所有 guidance 追加到 round tail 而非合成 user turn。`internal/agent/arbiter.go:38-60`
- **F-038**: governor 通过环境变量 `REASONIX_EXPERIMENT_GOVERNOR=1` 启用，是 A/B 实验门控。`internal/agent/governor.go:17`
- **F-039**: governor 触发条件：`DebtAge == 0 && !LocalExecSeen && lastReasoning >= 1500`。`internal/agent/governor.go:32-34`
- **F-040**: governor 退出条件：`DebtAge > 0 || LocalExecSeen || Discriminating > 0`。`internal/agent/governor.go:39-41`
- **F-041**: governor 启用时将 provider effort 降为 `"low"`，通过 `governorOverride()` 返回。`internal/agent/governor.go:21,67-72`

## Scheduler 与 Fleet

- **F-042**: `SubagentScheduler` 是 session 级并发控制器，字段包含 `maxTotal`、`maxWriters`、`activeTotal`、`activeWriters`、`parentClaims`。`internal/agent/scheduler.go:38-55`
- **F-043**: `AcquireRequest` 包含 `Writer bool`、`WritePaths WritePathSet`、`Nested bool`；Nested 请求在容量不足时立即失败而非排队。`internal/agent/scheduler.go:21-34`
- **F-044**: `FleetTool` 实现 2-64 个并行 sub-agent 任务调度，支持 `depends_on` 依赖图和 `fail_fast`。`internal/agent/fleet.go:19-74`
- **F-045**: Fleet 任务状态有 `pending`、`completed`、`failed`、`cancelled`、`skipped` 五种。`internal/agent/fleet.go:94-100`

## Task 与 Subagent

- **F-046**: `DefaultTaskSystemPrompt` 引导 sub-agent 返回简洁自包含的最终答案，parent 只看到该答案。`internal/agent/task.go:45-50`
- **F-047**: `DefaultReadOnlyTaskSystemPrompt` 禁止只读 sub-agent 写文件、安装 capability、变更 memory、控制长生命周期进程。`internal/agent/task.go:55-62`
- **F-048**: `subagentRecursiveTools` 列表包含 task、read_only_task、run_skill、read_only_skill、explore、research、review、security_review。`internal/agent/task.go:71-80`
- **F-049**: `subagentAlwaysHiddenTools` 列表包含 parallel_tasks、fleet、read_subagent_result、set_session_title、install_skill、install_source。`internal/agent/task.go:82-89`

## Compaction

- **F-050**: `defaultCompactRatio` 为 0.80，是唯一自动维护触发点；`recentTailBudgetRatio` 为 0.16。`internal/agent/compact.go:21-22`
- **F-051**: `summaryOutputMaxTokens` 为 8192；`minRecentKeep` 为 2；`minCompactMessages` 为 2。`internal/agent/compact.go:23-25`
- **F-052**: 压缩摘要使用 `<compaction-summary>` 标签包裹，包含 7 个固定章节：Standing facts、Goal、Decisions、Files、Commands、Errors、Pending。`internal/agent/compact.go:38-69`

## Fork 与 Branch

- **F-053**: `ForkBundle` 结构体冻结完整 turn 状态用于 policy 实验（EBM、governor、delegation admission），字段包含 Version、Policy、Input、EligibleRound、Messages。`internal/agent/fork.go:19-33`
- **F-054**: `forkBundleVersion` 常量为 1。`internal/agent/fork.go:35`
- **F-055**: `BranchMeta` 是会话分支元数据 sidecar，包含 ID、ParentID、ForkTurn、ForkMessageIndex、CreatedAt、WorkspaceRoot、Model、QualityFloor 等字段。`internal/agent/branch.go:26-60`

## ACP 协议

- **F-056**: ACP 包实现 Agent Client Protocol v1，通过 stdio NDJSON JSON-RPC 2.0 通信。`internal/acp/protocol.go:1-5`
- **F-057**: `ProtocolVersion` 常量为 1。`internal/acp/protocol.go:24`
- **F-058**: JSON-RPC 错误码：`ErrParse=-32700`、`ErrInvalidRequest=-32600`、`ErrMethodNotFound=-32601`、`ErrInvalidParams=-32602`、`ErrInternal=-32603`。`internal/acp/protocol.go:28-33`
- **F-059**: `InitializeParams` 包含 ProtocolVersion、ClientInfo、ClientCapabilities（FS、Terminal、Meta）。`internal/acp/protocol.go:40-55`
- **F-060**: `AgentCapabilities` 包含 LoadSession、SessionCapabilities（list/resume/close/delete）、PromptCapabilities（image/audio/embeddedContext）、MCPCapabilities（http/sse）。`internal/acp/protocol.go:81-87`
- **F-061**: `Conn` 结构体封装 NDJSON JSON-RPC 连接，写操作由 `sync.Mutex` 序列化，每个 inbound request/notification 在独立 goroutine 运行。`internal/acp/server.go:51-68`
- **F-062**: `maxMessageBytes` 为 32 MiB，限制单条 NDJSON 行大小。`internal/acp/server.go:16`
- **F-063**: `Factory` 接口定义 `NewSession(ctx, SessionParams) (*control.Controller, error)`，由 composition root 实现。`internal/acp/service.go:69-71`
- **F-064**: `Serve` 函数注册的 handler 包括 initialize、authenticate、session/new、session/load、session/resume、session/prompt、session/steer、session/inbox 系列方法。`internal/acp/service.go:136-150`
- **F-065**: `updateSink` 将 agent 的 typed event stream 映射到 ACP `session/update` 通知，tool call 经历 ToolDispatch → ToolResult 两态。`internal/acp/dispatch.go:51-71`
- **F-066**: `maxResultChars` 为 8000，裁剪跨线传输的 tool result（完整结果仍发送给 model）。`internal/acp/dispatch.go:33`
- **F-067**: ACP inbox 支持 `IntentSteer` 和 `IntentFollowup` 两种意图；steer 调用 `TryEnqueueAndSteer`，followup 调用 `EnqueueInbox`。`internal/acp/inbox.go:41-61`

## Bot 网关

- **F-068**: `Platform` 类型定义四个平台常量：`PlatformQQ="qq"`、`PlatformFeishu="feishu"`、`PlatformWeixin="weixin"`、`PlatformDingtalk="dingtalk"`。`internal/bot/types.go:14-19`
- **F-069**: `ChatType` 定义五种会话类型：`dm`、`group`、`guild`、`direct`、`thread`。`internal/bot/types.go:24-30`
- **F-070**: `InboundMessage` 包含 Platform、ConnectionID、ChatType、ChatID、UserID、Text、MessageID、Media 等字段。`internal/bot/types.go:55-78`
- **F-071**: `GatewayConfig` 包含 Model、ToolApprovalMode、MaxSteps、QueueMode、PairingEnabled、ApprovalTimeout、Channels、Routes、Allowlist 等字段。`internal/bot/gateway.go:26-85`
- **F-072**: 队列模式有四种：`steer`、`followup`、`collect`、`interrupt`；默认 `DefaultQueueCap` 为 20。`internal/bot/session.go:13-22`
- **F-073**: `BuildSessionKey` 按会话类型生成 key：DM 按 chat 隔离，群聊按 user 隔离，thread 共享；使用 SHA-256 取前 16 字符。`internal/bot/session.go:92-115`
- **F-074**: `RunWithRetry` 实现持久连接适配器的指数退避重连：1s → 30s，60s 健康连接后重置。`internal/bot/connloop.go:89-117`
- **F-075**: `SleepCtx` 是 context-aware 的 sleep，替代 `time.Sleep` 使 Stop 及时生效。`internal/bot/connloop.go:56-71`
- **F-076**: QQ 适配器实现 `bot.Adapter` 接口，使用 `golang.org/x/net/websocket` 连接 QQ Bot API v2 gateway，支持 C2C/group/guild/direct。`internal/bot/qq/adapter.go:1-8,30-49`
- **F-077**: 飞书 `withTransientRetry` 对传输级错误（connection reset、timeout、broken pipe）重试 3 次，指数退避 500ms→5s 带 jitter。`internal/bot/feishu/retry.go:32-59`
- **F-078**: 飞书 `newIdempotencyKey` 生成 16 字节随机 hex 作为 uuid 去重字段，重试时复用防止重复消息。`internal/bot/feishu/retry.go:24-30`
- **F-079**: `renderSink` 将事件流渲染为平台消息；实现 `messageEditor` 接口的适配器（飞书）获得原地编辑流式输出。`internal/bot/render.go:17-50`
- **F-080**: 渲染常量：`renderSoftFlushAfter=1200ms`、`renderMaxChunkRunes=1800`、`renderHardChunkRunes=3500`。`internal/bot/render.go:52-58`

## Checkpoint 系统

- **F-081**: checkpoint schema 版本有 V1=1、V2=2、V3=3 三个常量。`internal/checkpoint/types.go:11-14`
- **F-082**: `Coverage` 类型有 `complete`、`partial`、`none`、`legacy` 四种覆盖度。`internal/checkpoint/types.go:19-24`
- **F-083**: `FileRevision` 包含 Path、Existed、Mode、SHA256、BlobRef、CaptureSource、AfterSHA256、Content 等字段。`internal/checkpoint/types.go:74-90`
- **F-084**: `RewindScope` 有三种：`RewindCode`（仅文件）、`RewindConversation`（仅消息）、`RewindBoth`。`internal/checkpoint/types.go:117-121`
- **F-085**: `TransactionState` 有 prepared、committing、committed、aborted、undone 五态。`internal/checkpoint/types.go:222-228`
- **F-086**: `BlobStore` 是内容寻址存储，blob 以 SHA-256 hex 命名，原子写入。`internal/checkpoint/blob.go:16-58`
- **F-087**: 默认保留策略：`DefaultRetainCheckpoints=100`、`DefaultBlobQuotaBytes=1GiB`、`DefaultMaxFileBytes=32MiB`。`internal/checkpoint/types.go:295-298`
- **F-088**: checkpoint 加载按 turn 编号选择最新时间戳的检查点，v1 schema 标记为 `legacy_unverified`。`internal/checkpoint/load.go:15-80`

## Boot 系统

- **F-089**: boot 包从配置组装 ready-to-drive 的 `control.Controller`，是 "用户配置" 到 "可驱动 Controller" 的唯一转换点。`internal/boot/boot.go:1-8`
- **F-090**: `Options` 结构体包含 Model、MaxSteps、RequireKey、Sink、EffortOverride、PermissionAllow、AdditionalDirs、WorkspaceRoot 等字段。`internal/boot/boot.go:99-120`
- **F-091**: `BuildResult` 包含 Controller、Snapshot、Runtime、Owner、Extensions、Dispatcher、ExtensionUI、ProviderResolver 等字段。`internal/boot/runtime.go:30-76`
- **F-092**: `BuildRuntime` 函数运行完整 boot 组装并返回 controller 加 extension kernel 冻结快照。`internal/boot/runtime.go:96-98`
- **F-093**: `LocalProviderResolver` 从 config 解析 provider，`Catalog()` 返回所有已配置 provider 的 `provider.Descriptor`。`internal/boot/resolver.go:16-55`
- **F-094**: `ErrUnknownModel` 在配置的 model 无法解析到 provider 时返回。`internal/boot/boot.go:75`

## CLI/TUI

- **F-095**: `cli.RunWithBuildInfo` 是完整 CLI 入口，返回进程退出码；无参数且交互终端时启动 `chatREPL`。`internal/cli/cli.go:65-116`
- **F-096**: CLI 使用 `github.com/spf13/pflag` 做 flag 解析，TUI 使用 `charm.land/bubbletea/v2`。`internal/cli/cli.go:45-47`
- **F-097**: `parseMCPAdd` 解析 `reasonix mcp add` 参数，支持 `--http`、`--sse`、`--env`、`--header` 和 stdio 命令。`internal/cli/mcp.go:31-80`
- **F-098**: `/provider` 命令无参数时打开 provider picker，带参数时切换到指定 provider。`internal/cli/provider.go:17-25`
- **F-099**: `/model <ref>` 原地切换模型并携带对话历史，controller 构建异步执行不阻塞 TUI 事件循环。`internal/cli/model.go:19-60`
- **F-100**: `subagentCommand` 支持 list、create、edit、delete、try、run 子命令。`internal/cli/subagent.go:37-62`
- **F-101**: `pluginCommand` 支持 install、list、show、remove、enable、disable、doctor、migrate 子命令。`internal/cli/plugin.go:18-48`

## Desktop

- **F-102**: desktop 包使用 Wails v2 框架，`eventChannel` 常量为 `"agent:event"`，前端通过该 Wails 事件通道订阅 agent 事件流。`desktop/app.go:31,79`
- **F-103**: `singleInstanceID` 基于 `config.ReasonixHomeDir()` 的 SHA-256 前 8 字符生成，确保同数据目录的二次启动路由到已有进程。`desktop/app.go:81-100`
- **F-104**: desktop 导入 internal/agent、internal/boot、internal/botruntime、internal/checkpoint、internal/control 等核心包。`desktop/app.go:33-62`

## 服务与扩展

- **F-105**: `agentServices` 结构体分离 agent 的协作者（prov、tools、sink、gate、extensions、recoveryGate、hooks、asker 等）与记忆状态。`internal/agent/services.go:24-78`
- **F-106**: `ToolHooks` 接口定义 PreToolUse（可阻断）、PostToolUse、PostToolUseFailure、PostLLMCall、SubagentStop、PreCompact 六个钩子。`internal/agent/agent.go:262-278`
- **F-107**: `DeliveryRuntimeMarker` 是追加到 delivery-first 模式 user turn 的缓存冻结合约块，文本为 `<delivery-runtime>` 标签。`internal/agent/agent.go:63-69`
