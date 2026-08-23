# CodeWhale Facts

> 本文件包含从 CodeWhale 源码和官方文档中提取的 70 条编号事实。每条事实引用具体文件路径和行号。

## 工作区结构

- **F-001**: CodeWhale 是一个 Rust Cargo workspace，包含 21 个 crate 成员，定义在 `Cargo.toml:2-24`。
- **F-002**: workspace 版本为 `0.9.10`，使用 Rust edition 2024，最低 rustc 版本为 1.88（`Cargo.toml:29-35`）。
- **F-003**: 默认构建成员为 `crates/cli`，resolver 设置为 `"2"`（`Cargo.toml:25-26`）。
- **F-004**: workspace 使用三种编译 profile：`dev`（line-tables-only debug）、`release`（thin LTO, strip, 16 codegen units）、`dist`（fat LTO, 1 codegen unit）（`Cargo.toml:85-103`）。
- **F-005**: `dist` profile 不设置 `panic = "abort"`，因为 TUI 的 panic supervision（catch_unwind/spawn_supervised）需要 unwinding（`Cargo.toml:96-98`）。
- **F-006**: workspace 对 `unicode-width` 打了补丁以支持 CJK 宽度表（`Cargo.toml:111-112`）。
- **F-007**: 项目使用 MIT 许可证，仓库地址为 `https://github.com/Hmbown/CodeWhale`（`Cargo.toml:36-37`）。

## Crate 清单

- **F-008**: `codewhale-core`（core crate）描述为 "Core runtime boundaries for Codewhale"，依赖 agent、config、execpolicy、hooks、mcp、protocol、state、tools（`crates/core/Cargo.toml:8,16-23`）。
- **F-009**: `codewhale-agent` 描述为 "Model/provider registry and fallback strategy"，仅依赖 config 和 serde（`crates/agent/Cargo.toml:8,11-12`）。
- **F-010**: `codewhale-cli` 是入口 crate，二进制名称为 `codewhale`，路径为 `src/main.rs`（`crates/cli/Cargo.toml:8,10-12`）。
- **F-011**: `codewhale-mcp` 描述为 "MCP server lifecycle and tool proxy compatibility"，依赖 anyhow、serde、serde_json、tracing（`crates/mcp/Cargo.toml:8,11-14`）。
- **F-012**: `codewhale-tools` 描述为 "Tool invocation lifecycle, schema validation, and scheduler parallelism"，依赖 protocol、async-trait、tokio、uuid（`crates/tools/Cargo.toml:8,11-17`）。
- **F-013**: `codewhale-protocol` 描述为 "App-server protocol frames for Codewhale runtime integrations"，依赖 chrono、serde、serde_json、uuid（`crates/protocol/Cargo.toml:8,11-14`）。
- **F-014**: `codewhale-config` 描述为 "Config schema and precedence model"，依赖 execpolicy、paths、secrets、fd-lock、toml、toml_edit（`crates/config/Cargo.toml:8,11-23`）。
- **F-015**: `codewhale-state` 描述为 "Session/thread persistence and recovery model"，使用 rusqlite（SQLite）和 fd-lock（`crates/state/Cargo.toml:8,11-18`）。
- **F-016**: `codewhale-execpolicy` 描述为 "Execution policy and approval model"，依赖 protocol 和 serde（`crates/execpolicy/Cargo.toml:8,11-13`）。
- **F-017**: `codewhale-hooks` 描述为 "Hook dispatch and notifications support"，依赖 protocol、release、reqwest、async-trait、tokio（`crates/hooks/Cargo.toml:8,11-18`）。
- **F-018**: `codewhale-workflow` 描述为 "Typed Workflow IR and validation"，依赖 serde、serde_json、sha2、thiserror、toml（`crates/workflow/Cargo.toml:8,11-15`）。
- **F-019**: `codewhale-workflow-js` 描述为 "Dynamic Workflow runtime: sandboxed rquickjs scripts that dispatch Codewhale subagents"，使用 rquickjs 0.12（`crates/workflow-js/Cargo.toml:8,13`）。
- **F-020**: `codewhale-tui` 描述为 "Terminal UI for open-source and open-weight coding models"，使用 ratatui 0.30.2、crossterm 0.29、rmcp 2.2.0（`crates/tui/Cargo.toml:8,51,63,68`）。
- **F-021**: `codewhale-lane` 描述为 "Lane registry and Runtime backends for Codewhale workflow instances"（`crates/lane/Cargo.toml:8`）。
- **F-022**: `codewhale-telemetry` 描述为 "Anonymous, user-disableable product usage counting"（`crates/telemetry/Cargo.toml:8`）。
- **F-023**: `codewhale-app-server` 描述为 "App-server transport for Codewhale runtime integrations"，使用 axum 和 tower-http（`crates/app-server/Cargo.toml:9,14,29`）。
- **F-024**: `codewhale-secrets` 描述为 "Secret storage backends for Codewhale, with OS keyring and file fallback"，在 macOS/Windows/Linux 上使用 `keyring` crate（`crates/secrets/Cargo.toml:8,20-27`）。
- **F-025**: `codewhale-command-contract` 描述为 "Prototype command capability and dispatch shapes"，依赖 core（`crates/command-contract/Cargo.toml:8,11`）。

## Core 运行时架构

- **F-026**: `Runtime` 结构体组合了 config、model_registry、thread_manager、tool_registry、mcp_manager、exec_policy、hooks、jobs 八个组件（`crates/core/src/lib.rs:902-919`）。
- **F-027**: `Thread` 是持久化的会话单元，拥有 append-only 的 `Journal` 和 `leaf_id` 游标；`Session` 是临时的、per-turn 的，拥有 `messages_revision`（`crates/core/src/session.rs:1-9,29-45,76-85`）。
- **F-028**: `EngineHandle` 通过 `Op`-in / `EventMsg`-out channel 通信，提供 `send`、`cancel`、`steer` 方法（`crates/core/src/engine/mod.rs:63-107`）。
- **F-029**: `EngineConfig` 默认 model 为 `deepseek-v4-flash`，provider 为 `deepseek`，max_steps 为 32（`crates/core/src/engine/mod.rs:127-137`）。
- **F-030**: `spawn_engine` 在后台 tokio task 中运行 Engine，返回 EngineHandle 供 TUI、CLI exec、app-server 和测试共享（`crates/core/src/engine/mod.rs:233-240`）。
- **F-031**: `ThreadManager` 管理线程的 spawn、resume、fork、archive、goal 生命周期，底层使用 `StateStore` 持久化（`crates/core/src/lib.rs:521-899`）。
- **F-032**: `JobManager` 支持后台任务的重试逻辑，默认最大重试 3 次，指数退避基数 500ms，历史记录上限 64 条（`crates/core/src/lib.rs:115-117,120-144`）。
- **F-033**: `InitialHistory` 枚举有三种变体：`New`、`Forked(Vec<Value>)`、`Resumed`（`crates/core/src/lib.rs:54-66`）。
- **F-034**: `Runtime::reload_config_and_policy` 可以热重载 config 和 exec_policy，但不重载 mcp_manager、tool_registry、model_registry（`crates/core/src/lib.rs:983-986`）。
- **F-035**: tool dispatch 超时在测试中为 50ms，生产环境为 300 秒（`crates/core/src/lib.rs:45-51`）。

## MCP 协议集成

- **F-036**: `McpServerConfig` 包含 name、command、args、env、enabled 五个字段（`crates/mcp/src/lib.rs:20-35`）。
- **F-037**: `ToolFilter` 使用 allow/deny 列表，deny 优先于 allow，空 allow 表示暴露所有工具（`crates/mcp/src/lib.rs:41-49,511-519`）。
- **F-038**: `McpManager` 管理多个 MCP 服务器连接，提供 register_server、start_all、list_tools、call_tool、call_qualified_tool 等方法（`crates/mcp/src/lib.rs:210-505`）。
- **F-039**: MCP 工具的限定名格式为 `mcp__<server>__<tool>`，超过 64 字符时使用哈希截断（`crates/mcp/src/lib.rs:534-560`）。
- **F-040**: 服务器名称经过 `sanitize_component` 折叠（`-`、`.`、大小写折叠为 `_`），碰撞名称会被拒绝注册（`crates/mcp/src/lib.rs:225-242,521-532`）。
- **F-041**: `McpManagedClient` trait 定义了 list_tools、call_tool、list_resources、read_resource 四个方法（`crates/mcp/src/lib.rs:131-140`）。
- **F-042**: stdio JSON-RPC 服务器支持 13 个方法：initialize、healthz、capabilities、tools/list、tools/call、resources/list、resources/read、server/list、server/register、server/start、server/stop、server/unregister、shutdown（`crates/mcp/src/lib.rs:796-812`）。
- **F-043**: 工具过滤器在调用时强制执行，而不仅仅在列出时；被 deny 的工具无法通过直接寻址执行（`crates/mcp/src/lib.rs:380-391`）。
- **F-044**: 失败的 qualified tool call 不会被重试，以防止文件写入、提交或付费 API 的重复副作用（`crates/mcp/src/lib.rs:393-418`，测试在 `:1247-1280`）。
- **F-045**: TUI 中 `codewhale-tui serve --mcp` 运行 MCP stdio 服务器，`codewhale mcp-server` 是等价的 dispatcher 入口（`docs/MCP.md:12-15`）。

## 工具系统

- **F-046**: `ToolCapability` 枚举定义六种能力：ReadOnly、WritesFiles、ExecutesCode、Network、Sandboxable、RequiresApproval（`crates/tools/src/lib.rs:27-40`）。
- **F-047**: `ApprovalRequirement` 有三个级别：Auto（默认）、Suggest、Required（`crates/tools/src/lib.rs:44-52`）。
- **F-048**: `ToolRegistry` 使用 `HashMap<String, Arc<dyn ToolHandler>>` 存储处理器，`ToolCallRuntime` 使用 `RwLock` 管理并行/串行执行（`crates/tools/src/lib.rs:500-544`）。
- **F-049**: 支持并行的工具获取读锁（允许重叠），串行工具获取写锁（独占访问）；可重入调用跳过锁以避免死锁（`crates/tools/src/lib.rs:520-532`）。
- **F-050**: `ToolHandler` trait 要求实现 `kind()`、`is_mutating()`（默认 false）、`handle()` 三个方法（`crates/tools/src/lib.rs:470-493`）。
- **F-051**: `ToolDescriptor` 包含 name、input_schema、output_schema、supports_parallel_tool_calls、timeout_ms（`crates/tools/src/lib.rs:352-364`）。
- **F-052**: `FunctionCallError` 有六种错误：ToolNotFound、KindMismatch、MutatingToolRejected、TimedOut、Cancelled、ExecutionFailed（`crates/tools/src/lib.rs:450-463`）。
- **F-053**: 工具参数提取器对类型不匹配采取严格策略：`null` 表示缺省取默认值，但字符串 `"true"` 不会被强制转为布尔值（`crates/tools/src/lib.rs:227-346`）。

## Hooks 系统

- **F-054**: `HookEvent` 枚举包含七个变体：ResponseStart、ResponseDelta、ResponseEnd、ToolLifecycle、JobLifecycle、ApprovalLifecycle、GenericEventFrame，使用 `snake_case` 序列化（`crates/hooks/src/lib.rs:21-78`）。
- **F-055**: 提供四种内置 HookSink：StdoutHookSink、JsonlHookSink、WebhookHookSink、UnixSocketHookSink（`crates/hooks/src/lib.rs:117-309`）。
- **F-056**: `HookDispatcher` 将事件广播到所有注册的 sink，单个 sink 的错误被静默丢弃，不影响其他 sink（`crates/hooks/src/lib.rs:318-344`）。
- **F-057**: WebhookHookSink 最多重试 2 次，指数退避为 200ms、400ms（`crates/hooks/src/lib.rs:224-251`）。
- **F-058**: Hooks 是 TUI 运行时特性，`codewhale exec`（headless）、CLI dispatcher、app-server/ACP 不触发 hooks（`docs/HOOKS.md:18-25`）。

## 执行策略与安全

- **F-059**: `RulesetLayer` 有三层优先级：BuiltinDefault(0)、Agent(1)、User(2)（`crates/execpolicy/src/lib.rs:19-23`）。
- **F-060**: `PermissionAction` 有三种：Allow、Ask、Deny；同一 ruleset 内 deny 胜过 ask 胜过 allow（`crates/execpolicy/src/lib.rs:80-87,100-101`）。
- **F-061**: `AskForApproval` 有五种模式：UnlessTrusted、OnFailure、OnRequest、Reject、Never（`crates/execpolicy/src/lib.rs:201-219`）。
- **F-062**: Deny 规则在词边界匹配位置 token，`rm` 阻止 `rm -rf /` 但不阻止 `rmdir`；支持 flag 感知匹配，`git -c foo=bar push` 仍被 `git push` 规则匹配（`crates/execpolicy/src/lib.rs:448-471,732-796`）。
- **F-063**: 链式命令（`&&`、`||`、`;`、`|`、`&`）不会被 trusted prefix 自动批准，`git log ; rm -rf /` 不会因为 `git log` 受信任而通过（`crates/execpolicy/src/lib.rs:480-487,712-714`）。
- **F-064**: Deny 扫描通过 `shell_expand` 进行 shell 词法展开，能检测命令替换、子 shell、wrapper 等绕过方式（`crates/execpolicy/src/lib.rs:664-690`）。
- **F-065**: macOS 使用 Seatbelt（sandbox-exec），Linux 使用 Bubblewrap（bwrap，需 opt-in `prefer_bwrap = true`），Windows 当前无 OS 沙箱（`docs/SANDBOX.md:14-19,46-50`）。

## Workflow 引擎

- **F-066**: `WorkflowSpec` 包含 goal、budget、permissions、model_policy、promotion_policy、gates、nodes（`crates/workflow/src/lib.rs:122-143`）。
- **F-067**: `WorkflowNode` 有八种节点类型：BranchSet、Leaf、Sequence、Reduce、TeacherReview、LoopUntil、Cond、Expand（`crates/workflow/src/lib.rs:175-184`）。
- **F-068**: `AgentType` 有六种角色：General、Explore、Plan、Review、Implementer、Verifier（`crates/workflow/src/lib.rs:543-551`）。
- **F-069**: `IsolationMode` 有三种：Auto（并行写时自动变 Worktree）、Shared、Worktree（`crates/workflow/src/lib.rs:563-596`）。
- **F-070**: Workflow 运行的硬上限为 1000 个 agent，最大深度为 5（`crates/workflow/src/lib.rs:98-99`；`crates/workflow-js/src/lib.rs:63`）。
- **F-071**: JS Workflow 运行时基于 rquickjs（QuickJS），VM 保持单线程，通过 channel 与多线程引擎桥接（`crates/workflow-js/Cargo.toml:55`；`crates/workflow-js/src/lib.rs:1-11`）。
- **F-072**: JS 脚本全局函数包括 `task()`、`parallel()`、`pipeline()`、`log()`、`phase()`，以及 `budget` 对象；`Date.now()` 和 `Math.random()` 被禁用以保证确定性回放（`crates/workflow-js/src/lib.rs:15-34`）。
- **F-073**: Workflow JS 最大并发为 16，单次 `parallel()`/`pipeline()` 最多 1000 项（`crates/workflow-js/src/lib.rs:70-75`）。

## Fleet 多 Agent

- **F-074**: Fleet 是本地优先的持久化多 worker 运行控制平面，fleet worker 是一个无头的 `codewhale exec` 运行（`docs/FLEET.md:1-9`）。
- **F-075**: Fleet 状态存储在工作区的 `.codewhale/fleet.jsonl`，日志在 `.codewhale/fleet/`（`docs/FLEET.md:38-40`）。
- **F-076**: Fleet worker 角色包括 worker、scout、planner、reviewer、builder、verifier、consultant、custom（`docs/SUBAGENTS.md:65-74`）。
- **F-077**: 子 agent 默认继承父级工具注册表，包括 `agent` 本身；默认深度为 3，支持递归 spawn（`docs/SUBAGENTS.md:28-36`）。
- **F-078**: "委派转移工作，永不转移权威"——只读角色的子 agent 权限被 clamp 到父级实时姿态，只读性在委派链中是传递的（`docs/SUBAGENTS.md:85-100`）。
- **F-079**: 模型面向的 subagent 工具名为 `agent`，已移除的 `agent_open`/`agent_eval`/`agent_close` 不再存在（`AGENTS.md:34-36`）。

## 模型与 Provider

- **F-080**: `ModelFamily` 枚举包含 11 个模型家族：DeepSeek、Anthropic、OpenAI、Google、Meta、Mistral、Qwen、Grok、Cohere、GptOss、Inferencer（`crates/agent/src/lib.rs:8-20`）。
- **F-081**: `ModelInfo` 包含 id、provider、aliases、supports_tools、supports_reasoning（`crates/agent/src/lib.rs:28-39`）。
- **F-082**: ProviderKind 有 42 个条目，包括 deepseek、openai、anthropic、google、ollama、openrouter、moonshot、zai、xai 等（`docs/PROVIDERS.md:43-52`）。
- **F-083**: DeepSeek 是默认 provider，默认模型为 `deepseek-v4-flash`（`crates/core/src/engine/mod.rs:130-131`；`docs/PROVIDERS.md:4`）。

## 状态持久化

- **F-084**: `StateStore` 由 SQLite 数据库和 append-only JSONL 会话索引文件支持（`crates/state/src/lib.rs:1-4`）。
- **F-085**: StateStore 管理 threads、messages（树形分支）、checkpoints、jobs、dynamic tools 五类数据（`crates/state/src/lib.rs:5-10`）。
- **F-086**: `ThreadMetadata` 存储 id、preview、model_provider、cwd、status、git 信息、sandbox_policy、approval_mode、memory_mode 等（`crates/state/src/lib.rs:57-102`）。
- **F-087**: `SESSION_INDEX_LOCK` 使用全局 `LazyLock<Mutex<()>>` 序列化所有 session_index.jsonl 的读写/压缩/重命名操作（`crates/state/src/lib.rs:21`）。

## 配置与路径

- **F-088**: 配置文件存储在 `~/.codewhale/config.toml`，旧版 `~/.deepseek/config.toml` 仍受支持（`docs/GUIDE.md:109-111`）。
- **F-089**: `codewhale doctor` 提供离线健康检查，`--json` 输出机器可读报告（`docs/GUIDE.md:117-131`）。
- **F-090**: `codewhale-paths` crate 是用户范围的运行时路径权威，仅依赖 `dirs` crate（`crates/paths/Cargo.toml:8-11`）。

## TUI 与前端

- **F-091**: TUI 有三种模式：Plan（只读，拒绝文件修改和 shell 执行）、Work（普通多步执行）、Operate（多任务调度姿态）（`docs/MODES.md:31-33`）。
- **F-092**: Tab 循环模式（Plan→Work→Operate），Shift+Tab 循环权限姿态（Ask→Auto-Review→Full Access），Ctrl+T 循环推理力度（`docs/MODES.md:23-27`）。
- **F-093**: TUI 支持 16 种语言区域，包括 zh-Hans、zh-Hant、ja、ko 等（`crates/tui/locales/` 目录）。
- **F-094**: `codewhale web` 在 `127.0.0.1:7878` 启动本地浏览器客户端，使用一次性 bootstrap URL 和 HttpOnly SameSite=Strict cookie 认证（`docs/WEB.md:3,16,42-48`）。
- **F-095**: TUI 的 `BASE_PROMPT` 位于 `crates/tui/src/prompts/text.rs`，是唯一的基础 prompt（`AGENTS.md:37`）。

## 技能与插件

- **F-096**: Skills 是可复用的 `SKILL.md` 指令包，架构分四层：根目录、审计、变更控制器、管理器视图（`docs/SKILLS.md:3,13-18`）。
- **F-097**: Skills 可写目录为项目级 `<workspace>/.codewhale/skills/` 和全局级 `~/.codewhale/skills/`（`docs/SKILLS.md:28-31`）。
- **F-098**: 插件支持三种安装源：本地目录、GitHub archive、直接 tarball URL；安装后需要 trust（hash-bound）再 enable（`docs/PLUGINS.md:19-25,43-55`）。
- **F-099**: 插件安装到 `~/.codewhale/plugins/<name>/`，更新时字节相同则 no-op，变化则原子交换并自动失效 trust receipt（`docs/PLUGINS.md:38-39,70-74`）。

## 缓存与记忆

- **F-100**: 系统 prompt + 工具目录在会话启动后是冻结字节，历史只增长；volatile 事实作为 user-role 消息追加，不拼接到冻结前缀（`docs/CACHE.md:10-11,20-28`）。
- **F-101**: `PrefixStabilityManager` 记录每次前缀变更的原因，`/cache stats` 报告前缀稳定性和 drift 计数（`docs/CACHE.md:32-33`）。
- **F-102**: 原生记忆系统使用 Markdown 文件 + SQLite FTS5 索引，按 git origin hash 限定工作区范围，完全离线（`docs/MEMORY.md:9-10`）。
- **F-103**: 记忆是 opt-in 的，通过 `DEEPSEEK_MEMORY=on` 环境变量或 `[memory] enabled = true` 配置启用（`docs/MEMORY.md:24-36`）。

## 安装与分发

- **F-104**: npm 包名为 `codewhale`，crates.io 包名为 `codewhale-cli`（`README.md:11-12,18`）。
- **F-105**: 项目起源于 `deepseek-tui`，仍保留配置和会话兼容性（`README.md:91-92`）。
- **F-106**: Docker 镜像发布在 `ghcr.io/hmbown/codewhale`，容器以非 root 用户 `codewhale`（UID/GID 1000:1000）运行（`docs/DOCKER.md:7,44`）。
- **F-107**: CLI 使用 mimalloc 作为全局分配器（`crates/cli/Cargo.toml:40`）。
- **F-108**: CLI 在 Unix 上使用 PR_SET_PDEATHSIG、在 Windows 上使用 Job Objects 实现父进程死亡时清理子进程（`crates/cli/Cargo.toml:50-59`）。

## 协议层

- **F-109**: `Status` trait 定义三个通用方法：`is_terminal()`、`is_active()`、`is_paused()`，被 thread、goal、fleet、job 等状态枚举实现（`crates/protocol/src/lib.rs:21-33`）。
- **F-110**: protocol crate 包含 agent_mail、agent_run、event_msg、fleet、ids、journal、op、runtime、workroom 九个模块（`crates/protocol/src/lib.rs:6-14`）。
