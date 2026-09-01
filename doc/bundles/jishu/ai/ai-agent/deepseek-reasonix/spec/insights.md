---
type: spec
scope: deepseek-reasonix
name: insights
version: "0.1.0"
source: local
description: DeepSeek-Reasonix 架构洞察——ACP 协议设计、Agent 运行循环与仲裁调控、Bot 多平台网关、Checkpoint 恢复机制、Fleet/Subagent 架构
---

# DeepSeek-Reasonix 架构洞察

## 洞察一：ACP 协议是传输无关的适配层而非核心引擎

**陈述**：ACP（Agent Client Protocol）包是一个独立的适配器层，仅依赖 `control.Controller` 稳定契约，通过 `Factory` 接口将 per-session agent 的组装权委托给 composition root（CLI 的 `reasonix acp` 命令）。协议本身不包含任何 provider、tool 或 MCP 的组装逻辑。

**证据**：
- `internal/acp/protocol.go:1-14` 包注释明确声明 "The package is an adapter layer over the v2 kernel and depends only on stable contracts"
- `internal/acp/service.go:69-71` `Factory` 接口仅定义 `NewSession(ctx, SessionParams) (*control.Controller, error)`
- `internal/acp/service.go:46-61` `SessionParams` 携带 Cwd、MCPServers、Sink、Model 等，由 Factory 消费
- `internal/acp/server.go:51-68` `Conn` 封装 NDJSON JSON-RPC，写操作 mutex 序列化，每个请求独立 goroutine
- F-056 至 F-067 覆盖协议版本、错误码、能力协商、handler 注册、事件映射、inbox 意图

**反常识**：多数 agent 项目将协议层与核心引擎耦合（协议 handler 直接构建 agent），导致新增传输方式需复制组装逻辑。Reasonix 的 Factory 模式让 ACP、CLI、bot、desktop 共享同一个 `boot.BuildRuntime` 组装路径，ACP 包甚至不导入 `internal/boot`。

**行动**：理解 Reasonix 架构时，不应从 ACP handler 追踪 agent 构建——应从 `boot.BuildRuntime` 入手，ACP 只是该 Controller 的一种传输前端。新增传输方式时实现 Factory 接口即可，无需修改 agent 核心。

---

## 洞察二：运行循环以"采样恢复 + 仲裁升级"为双层容错骨架

**陈述**：Agent 主循环不是简单的"调用 model → 执行 tool → 重复"，而是包含 Codex 风格的请求冻结重放（`streamWithSamplingRecovery`，最多 6 次尝试）和四级 verdict 仲裁阶梯（continue/advise/redirect/land），governor 在探索阶段动态降低 reasoning depth。

**证据**：
- `internal/agent/run_loop.go:345-468` `streamWithSamplingRecovery` prepare 一次、freeze 请求、最多 `maxSamplingAttempts=6` 次 body 尝试，失败尝试不写 Session 状态
- `internal/agent/run_loop.go:55-119` `deferredStreamSink` 在 reasoning 到达前缓冲 tool 事件，malformed turn 重试不闪卡
- `internal/agent/run_loop.go:502-517` 退避 0.5s→1s→2s→4s→8s 带 jitter
- `internal/agent/arbiter.go:13-18` verdict 四级：continue/advise/redirect/land
- `internal/agent/arbiter.go:38-60` `applyInterventions` 将多信号折叠为最强 verdict，guidance 追加到 round tail 而非合成 user turn
- `internal/agent/governor.go:32-41` 触发条件 `DebtAge==0 && !LocalExecSeen && lastReasoning>=1500`，退出条件 `DebtAge>0 || LocalExecSeen || Discriminating>0`
- F-028 至 F-041 覆盖循环结构、采样恢复、仲裁、governor

**反常识**：常见 agent 循环把重试和调控混在业务逻辑里，Reasonix 将"传输层重试"（stream recovery，不写状态）和"语义层仲裁"（arbiter verdict，写 guidance 到 tail）严格分离。governor 是环境变量门控的 A/B 实验而非默认行为，说明该机制仍在验证中。

**行动**：排查 agent 行为异常时，先区分是 stream recovery 重试（同一 frozen 请求）还是 arbiter 干预（不同 guidance tail）。governor 仅在 `REASONIX_EXPERIMENT_GOVERNOR=1` 时生效，默认运行不应期待 reasoning depth 自动降低。

---

## 洞察三：Bot 网关以 Adapter/Session/Render 三层解耦多平台差异

**陈述**：Bot 网关采用 Hermes 模式的三层架构：`Adapter` 抽象平台连接（QQ WebSocket、飞书 HTTP、微信、钉钉），`Session` 通过 `BuildSessionKey` 按会话类型隔离上下文，`renderSink` 将统一事件流渲染为各平台消息格式。队列模式（steer/followup/collect/interrupt）处理并发入站消息。

**证据**：
- `internal/bot/types.go:14-19` 四个 Platform 常量；`internal/bot/types.go:24-30` 五种 ChatType
- `internal/bot/types.go:55-78` `InboundMessage` 统一入站结构，携带 Platform、ConnectionID、ChatType、ChatID、UserID、Media
- `internal/bot/session.go:92-115` `BuildSessionKey` 按 DM（chat 隔离）、group（user 隔离）、thread（共享）生成 SHA-256 key
- `internal/bot/session.go:13-22` 四种队列模式，默认 cap 20
- `internal/bot/connloop.go:89-117` `RunWithRetry` 指数退避重连 1s→30s，60s 健康后重置
- `internal/bot/qq/adapter.go:1-8` QQ 适配器使用 `golang.org/x/net/websocket`，支持 C2C/group/guild/direct
- `internal/bot/feishu/retry.go:32-59` 飞书传输级重试 3 次，500ms→5s
- `internal/bot/render.go:17-50` `messageEditor` 接口让飞书获得原地编辑流式输出
- F-068 至 F-080 覆盖平台类型、会话隔离、队列、重连、适配器、渲染

**反常识**：多平台 bot 通常在每个适配器里硬编码会话管理和消息渲染。Reasonix 将 session key 生成算法集中在 `BuildSessionKey`，渲染器通过 `messageEditor` 接口能力探测决定流式策略，适配器只需实现 `Start/Stop/Send/Messages` 四个方法。

**行动**：新增 IM 平台时实现 `bot.Adapter` 接口即可，会话隔离和消息渲染由网关层统一处理。注意 `SleepCtx` 必须替代 `time.Sleep`，否则 Stop 会阻塞到退避结束。

---

## 洞察四：Checkpoint 是带事务语义的文件+对话双回滚系统

**陈述**：Checkpoint 系统不止是"保存快照"，它实现了带冲突检测的事务化 rewind：`RewindPlan` 预检查返回冲突列表，`TransactionManifest` 经历 prepared→committing→committed/aborted 状态机，`BlobStore` 以 SHA-256 内容寻址存储文件载荷，支持 `RewindCode`/`RewindConversation`/`RewindBoth` 三种范围。

**证据**：
- `internal/checkpoint/types.go:117-121` `RewindScope` 三种：code/conversation/both
- `internal/checkpoint/types.go:163-187` `RewindPlan` 包含 Coverage、Conflicts、Files、ActiveWriters、BoundaryIndex
- `internal/checkpoint/types.go:222-228` `TransactionState` 五态：prepared/committing/committed/aborted/undone
- `internal/checkpoint/types.go:259-290` `TransactionManifest` 携带 Targets（含 restore/forward 双份载荷）、ConversationForward、CheckpointBackup
- `internal/checkpoint/types.go:137-150` 冲突原因 11 种：manual_edit、external_change、deleted_and_recreated、type_change、active_writer 等
- `internal/checkpoint/blob.go:16-58` `BlobStore` Put 时校验 SHA-256，原子写入
- `internal/checkpoint/types.go:19-24` Coverage 四态：complete/partial/none/legacy
- F-081 至 F-088 覆盖 schema 版本、覆盖度、文件修订、回滚范围、事务状态、blob 存储、保留策略、加载逻辑

**反常识**：多数 agent checkpoint 是"覆盖式保存+整体恢复"，Reasonix 的 rewind 是两阶段提交：prepare 阶段将当前文件复制到 backup、checkpoint 文件写到 staging tmp，commit 阶段 rename 发布，crash 后通过 `Published` 标记恢复。对话回滚还支持 fork 分支（`ConversationForked`）。

**行动**：调用 rewind 前必须检查 `RewindPlan.Conflicts`，`active_writer` 冲突意味着后台 subagent 仍在写文件。`CoverageLegacy` 的 v1 checkpoint 无法验证后续手动编辑，回滚时会有 `legacy_unverified` gap。

---

## 洞察五：Fleet/Subagent 以写路径声明和调度槽位实现安全并行

**陈述**：多 agent 并行不是简单地 goroutine 启动，而是通过 `SubagentScheduler` 的 `maxTotal`/`maxWriters` 双限制 + `WritePathSet` 写路径声明实现 TOCTOU 安全：并发 writer 必须声明不重叠的 write_paths，父 agent 写操作通过 `parentClaims` 阻塞重叠 subagent，fleet 支持 `depends_on` 依赖图形成 DAG 调度。

**证据**：
- `internal/agent/scheduler.go:38-55` `SubagentScheduler` 字段：maxTotal、maxWriters、activeTotal、activeWriters、parentClaims、waiters FIFO
- `internal/agent/scheduler.go:21-34` `AcquireRequest` 的 `Nested bool` 在容量不足时立即失败（防止嵌套死锁）
- `internal/agent/fleet.go:19-74` `FleetTool` 2-64 任务，`write_paths` 声明，`depends_on` DAG，`fail_fast` 控制失败策略
- `internal/agent/fleet.go:39` Description 明确："Tasks with no dependency between them run in parallel and must declare non-overlapping write_paths"
- `internal/agent/task.go:45-62` 读写 subagent 使用不同 system prompt，只读 sub-agent 不接收 writer tools
- `internal/agent/agent.go:246` `DefaultMaxSubagentDepth=2`，递归深度有上限
- `internal/agent/agent.go:1218-1232` `reserveParentWrite` 在父 agent 写工具执行期间保留写声明
- F-042 至 F-049 覆盖调度器、fleet、task prompt、递归工具

**反常识**：常见多 agent 系统要么完全串行（安全但慢），要么完全并行（快但有写冲突）。Reasonix 的写路径声明是 preflight 检查——两个无依赖关系的 writer 如果 write_paths 重叠，在任何任务启动前就失败，不会出现运行到一半才发现冲突。有序任务（depends_on）可以共享路径，因为它们不会并发执行。

**行动**：使用 fleet 时，无依赖的并行任务必须声明不重叠的 `write_paths`；省略 write_paths 等于声明整个工作区，两个这样的任务必然 preflight 失败。嵌套 sub-agent（depth>0）不会阻塞等待槽位，容量不足时立即失败。
