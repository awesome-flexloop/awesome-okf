---
type: spec
scope: codewhale
name: insights
version: "0.1.0"
source: local
description: "CodeWhale 核心架构洞察：从 crate 模块化设计到 Fleet 多 Agent 编排、Workflow JS 引擎、MCP 集成和 Skill 系统的深度分析"
---

# CodeWhale 核心洞察

## 洞察一：Crate 模块化设计——21 个 crate 的严格分层与边界意识

### 陈述

CodeWhale 将一个约 68 万行的 Rust 编码 Agent 拆分为 21 个职责单一的 crate，形成从协议层到 UI 层的严格依赖方向。`core` crate 是运行时边界的汇聚点，但它本身不依赖 `tui`——终端 UI 建立在 core 之上，而非反之。

### 证据

- workspace 成员列表明确定义了 21 个 crate（F-001）。
- `codewhale-core` 依赖 agent、config、execpolicy、hooks、mcp、protocol、state、tools，但不依赖 tui（F-008）。
- `codewhale-tui` 反向依赖 core、tools、workflow、workflow-js、mcp 等（F-020）。
- `codewhale-protocol` 是最底层 crate 之一，仅依赖 chrono、serde、serde_json、uuid，不依赖任何内部 crate（F-013）。
- `codewhale-agent`（模型注册）仅依赖 config 和 serde，极其轻量（F-009）。
- `codewhale-command-contract` 依赖 core，是 TUI 命令提取的原型边界（F-025）。
- Engine 模块注释明确写道："The TUI crate depends on `core`, not the reverse"（`crates/core/src/engine/mod.rs:9`）。

### 反常识

通常大型 Rust 项目会把核心逻辑放在最大的 crate（这里是 tui），但 CodeWhale 正在主动将 turn loop、session、thread manager 从 tui 迁移到 core。engine/mod.rs 的注释直言："Only request-building and fragments have moved so far. The turn loop still lives in `crates/tui/src/core/engine/turn_loop.rs`"。这是一个**进行中的架构迁移**，而非已完成的完美分层——core 目前同时包含已迁移的 `Runtime`（900+ 行）和新建的 `Engine`（channel 边界证明），两者并存。

### 行动

- 阅读源码时，`crates/core/src/lib.rs` 的 `Runtime` 是当前无头运行时的实际入口，而 `crates/core/src/engine/mod.rs` 的 `Engine` 是未来 turn loop 迁移的目标边界。
- 新增核心功能应优先放入 core 或更低层 crate，避免在 tui 中添加不依赖终端的逻辑。
- protocol crate 是跨进程通信的唯一类型来源，不应引入业务逻辑依赖。

---

## 洞察二：Fleet 多 Agent 编排——持久化 worker 与权限传递的 clamp 模型

### 陈述

Fleet 不是简单的 prompt fanout，而是一个本地优先的持久化多 worker 控制平面。每个 fleet worker 是一个无头的 `codewhale exec` 进程，拥有重试、重启存活、账本审计追踪。核心安全原则是"委派转移工作，永不转移权威"——子 agent 的权限被 clamp 到父级实时姿态，只读性在委派链中传递。

### 证据

- Fleet worker 是无头 `codewhale exec` 运行，状态存储在 `.codewhale/fleet.jsonl`（F-074, F-075）。
- 8 种角色：worker、scout、planner、reviewer、builder、verifier、consultant、custom，每种有不同的写/网络/shell 姿态（F-076）。
- 默认 spawn 深度为 3，子 agent 继承父级工具注册表包括 `agent` 本身（F-077）。
- 只读父级委派给写角色时，子级的权限被 clamp：scout 的 builder child 落地为只读，raw shell 和 mutating tools 被拒绝（F-078）。
- `ChildAuthority::clamp` 在 `fleet/exact.rs` 中对每个字段取交集，deny-list 取并集（F-078）。
- `codewhale fleet resume <run-id>` 是幂等的重启恢复动词，重放账本并协调心跳丢失的租约（`docs/FLEET.md:31-36`）。

### 反常识

多 agent 系统通常假设"专门的 builder 角色就应该能写文件"。但 CodeWhale 的 scout 即使委派给 builder，builder 也不能写——因为 scout 本身是只读的。角色定义的是**意图姿态**，父级的有效姿态始终是上限。这意味着一个配置为只读的 agent 无法通过委派来"升级"权限，即使它调用了一个名义上有写权限的角色。这与许多 agent 框架中"子 agent 拥有角色声明的全部权限"形成鲜明对比。

### 行动

- 设计 Fleet profile 时，角色的默认权限是意图而非保证；实际权限由父级姿态 clamp。
- 需要持久化、重启存活的工作应使用 Fleet CLI（`codewhale fleet run`），而非短暂的 `agent` 工具 fanout。
- `/fleet workers` 查看当前会话子 agent，`codewhale fleet status` 查看持久化账本——两者是不同的数据集。

---

## 洞察三：Workflow 引擎——声明式 IR + 命令式 JS 双轨设计与确定性回放

### 陈述

CodeWhale 的 Workflow 系统采用双轨架构：`codewhale-workflow` 提供类型化的声明式 IR（8 种节点类型、预算/权限/模型策略），`codewhale-workflow-js` 提供基于 QuickJS 的命令式 JS 运行时。两者共享 1000 agent 生命周期上限和 16 并发上限，但职责严格分离——IR 负责校验/记录/回放，JS 负责动态编排。

### 证据

- WorkflowSpec 包含 goal、budget、permissions、model_policy、gates、nodes（F-066）。
- 8 种节点：BranchSet（并行/串行分支）、Leaf（实际 agent 任务）、Sequence、Reduce、TeacherReview、LoopUntil、Cond、Expand（F-067）。
- JS 运行时基于 rquickjs，VM 单线程，通过 channel 与多线程引擎桥接（F-071）。
- JS 全局函数：`task()` 派发 subagent、`parallel()`/`pipeline()` 扇出、`log()`/`phase()` 进度、`budget` 预算快照（F-072）。
- `Date.now()`、`new Date()`、`Math.random()` 在 JS 中抛出异常，确保运行可确定性回放（F-072）。
- 硬上限：1000 agent/run、5 层深度、16 并发、1000 项/parallel 调用（F-070, F-073）。
- IsolationMode.Auto 在并行写时自动解析为 Worktree，避免并发写冲突（F-069）。

### 反常识

大多数工作流引擎选择要么全声明式（如 DAG）要么全命令式（如脚本）。CodeWhale 同时提供两者，但不是简单叠加——声明式 IR 有 `TeacherReview` 和 `PromotionGate` 这样的"教师评审循环"（自动对比 baseline/candidate 回放分数、检查测试通过、策略违规），这在纯命令式 JS 中很难声明性地保证。而 JS 侧则承担 IR 难以表达的动态 fanout（`Expand` 节点在运行时生成子节点）。关键设计是：JS 不能直接执行副作用，所有 `task()` 调用都通过 `WorkflowDriver` trait 桥接到宿主，使得 JS 逻辑可以在 `FakeDriver` 上完全测试。

### 行动

- 需要可审计、可回放的多步编排使用声明式 WorkflowSpec TOML。
- 需要动态条件分支和运行时生成任务的使用 JS workflow，但注意确定性约束（不能用 Date/random）。
- Workflow 节点的 `role` 和 `profile` 字段在 dispatch 时通过 Fleet roster 解析，不在定义时绑定。

---

## 洞察四：MCP 集成——防重放、名称折叠安全与调用时过滤

### 陈述

CodeWhale 的 MCP 实现在工具代理兼容性之外，解决了三个实际安全问题：限定名碰撞、过滤器绕过和失败重试导致的重复副作用。工具名经过 sanitize 折叠后碰撞会被拒绝；过滤器在调用时（而非仅列出时）强制执行；失败的 qualified tool call 不会回退到重新解析循环。

### 证据

- 限定名格式 `mcp__<server>__<tool>`，超过 64 字符时哈希截断（F-039）。
- `sanitize_component` 将 `-`、`.`、非字母数字折叠为 `_` 并小写化；`my-server`、`my_server`、`My.Server` 全部限定为 `mcp__my_server__*`，注册第二个会报错（F-040）。
- ToolFilter 在 `call_tool` 时检查，不仅在 `list_tools` 时；deny 优先于 allow（F-037, F-043）。
- `call_qualified_tool` 的快速路径在调用失败时直接返回错误，不 fall through 到扫描循环——防止文件写入/提交/付费 API 被执行两次（F-044）。
- stdio JSON-RPC 服务器支持 13 个方法，包括完整的 server 生命周期管理（F-042）。
- 插件贡献的 MCP 服务器使用更严格的审查边界：未知字段失败关闭、远程 literal headers 被拒绝、声明的网络主机必须精确匹配（`docs/MCP.md:48-57`）。

### 反常识

MCP 工具名通常被视为不透明字符串，但 CodeWhale 发现名称折叠会引入安全问题：如果 `my-server` 和 `my_server` 都注册为 MCP 服务器，它们的工具都映射到 `mcp__my_server__*`，HashMap 迭代顺序决定哪个服务器响应调用——这是一个非确定性的安全漏洞。代码通过在注册时检测折叠后碰撞来关闭这个问题。类似地，大多数实现在 list 时过滤工具就满足了，但 CodeWhale 在 call 时也过滤，因为客户端可以直接构造限定名调用而不经过 list。

### 行动

- 配置 MCP 服务器时避免使用仅在 `-`/`_`/`.` 上不同的名称。
- 插件捆绑的 MCP 服务器比用户 `mcp.json` 配置的服务器受到更严格的验证，这是设计有意为之。
- MCP 工具调用失败不会自动重试，需要调用方自行处理——这对于有副作用的工具是正确的行为。

---

## 洞察五：Skill 系统——四层架构与所有权边界

### 陈述

CodeWhale 的 Skill 系统采用四层架构：根目录（优先级和所有权的唯一来源）、审计（只读未合并磁盘清单）、变更控制器（唯一写入者）、管理器视图（TUI 仅发事件不写文件）。关键设计是只有 CodeWhale 拥有的目录可写，兼容的外部目录（`.claude/skills`、`.cursor/skills` 等）只读发现。

### 证据

- Skills 是可复用的 `SKILL.md` 指令包（F-096）。
- 四层架构：Root catalog → Audit → Mutation controller → Skills manager view（F-096）。
- 可写目录：项目级 `<workspace>/.codewhale/skills/` 和全局级 `~/.codewhale/skills/`（F-097）。
- 只读兼容目录包括 `.agents/skills`、`.claude/skills`、`.cursor/skills`、`.opencode/skills` 等（`docs/SKILLS.md:35-37`）。
- 审计层故意**不合并**同名 skill，显示每个磁盘副本以使冲突和遮蔽可见（`docs/SKILLS.md:21-22`）。
- 运行时发现（SkillRegistry）合并 skill 供模型使用，但审计显示所有副本（`docs/SKILLS.md:20-22`）。
- TUI 视图从不直接调用安装助手或触碰文件系统，它发出变更请求，宿主运行控制器（`docs/SKILLS.md:96-98`）。
- 插件可以贡献 MCP 服务器和 skills，但需要 hash-bound trust receipt 才能启用（F-098, F-099）。

### 反常识

大多数 agent 工具的 skill 系统会合并所有发现路径中的同名 skill，让"最后加载的获胜"。CodeWhale 的审计层反其道而行：它**故意不合并**，让用户看到同一 skill 名在 `.claude/skills/` 和 `.codewhale/skills/` 中各有一个副本。运行时确实合并（模型看到一个），但审计视图保持透明。此外，TUI 本身被禁止写文件——它只能发出意图事件，由宿主的变更控制器执行。这种"视图与控制器严格分离"在终端应用中不常见，但防止了 TUI 渲染逻辑意外损坏用户文件。

### 行动

- 安装 skill 时使用 `/skill install`，不要手动复制到外部兼容目录（外部目录只读）。
- 如果 skill 行为异常，用 `/skills inspect` 查看所有磁盘副本和来源路径。
- 插件更新后 trust receipt 自动失效（hash 不匹配），需要重新审查才能激活。
