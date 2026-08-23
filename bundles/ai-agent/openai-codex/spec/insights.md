---
type: spec
scope: openai-codex
name: insights
version: "0.1.0"
source: local
description: >
  架构级洞察，基于对 OpenAI Codex CLI 三语言代码库（Node.js / Rust / Python）
  的源码阅读与事实提取，聚焦多语言架构、Rust 核心迁移、沙箱执行模型、
  Skills/AGENTS.md 约定、TUI 设计五个维度。
---

# Insights — OpenAI Codex CLI

## Insight 1：三语言分层架构——JS 壳、Rust 核、Python 编程接口

### 陈述

Codex CLI 采用严格的三语言分层：Node.js 仅作为 npm 分发的平台启动器（249 行），所有实际逻辑由 Rust 工作区（130+ crate）承载，Python SDK 通过子进程 JSON-RPC 调用同一 Rust 二进制。三者不是平行实现，而是"壳—核—接口"的垂直分层。

### 证据

- Node.js 入口 `codex-cli/bin/codex.js` 只做平台 triple 检测、可选依赖解析、信号转发，不含任何业务逻辑（F-013, F-016）。
- Rust 工作区包含 `cli`、`tui`、`core`、`sandboxing`、`execpolicy`、`skills`、`codex-mcp` 等 130+ crate，是功能的唯一实现（F-006, F-034）。
- Python SDK 依赖 `openai-codex-cli-bin==0.147.0`，通过 `_installed_codex_path()` 定位 Rust 二进制并以子进程方式通信（F-071, F-074）。
- npm 包 `@openai/codex` 同样将平台二进制拆分为六个 optionalDependencies（F-014）。

### 反常识

通常多语言项目意味着多套实现或 FFI 绑定，但 Codex 的 Node.js 和 Python 层都不包含 agent 逻辑——它们纯粹是分发与进程管理壳。Rust 二进制是唯一的"真相来源"，JS/Python 只是不同生态的入口适配器。这意味着理解 Codex 架构必须从 Rust 入手，而非 README 中显眼的 npm 安装命令。

### 行动

- 架构分析应聚焦 `codex-rs/`，将 `codex-cli/` 和 `sdk/python/` 视为薄适配层。
- 新增功能时，核心逻辑必须落在 Rust crate 中；JS/Python 层只暴露调用入口。
- 跨语言调试时，优先检查 Rust 二进制的 `RUST_LOG` 输出（F-077），而非 JS/Python 层日志。

---

## Insight 2：从单体 core 到微核工作区——有意识的"逆膨胀"治理

### 陈述

`codex-core` 曾是唯一的核心 crate，但项目通过 AGENTS.md 中的硬性规则和持续重构，将功能拆分为 130+ 小 crate。项目明确要求"抵制向 codex-core 添加代码"，新功能应优先放入新 crate 或现有小 crate。

### 证据

- AGENTS.md 设有专门章节 "The `codex-core` crate"，声明 "resist adding code to codex-core"，要求新功能考虑新 crate（F-033）。
- `core/src/lib.rs` 仍声明 50+ 模块，但大量功能已外移：sandbox 逻辑在 `codex-sandboxing`（F-040），skills 在 `codex-skills`（F-049），MCP 在 `codex-mcp`（F-065），配置在 `codex-config`（F-061），execpolicy 在独立 crate（F-048）。
- 模块大小有硬约束：目标 <500 LoC，超过 800 LoC 必须拆分；`app.rs`、`chatwidget.rs` 等高触文件被点名监控（F-028）。
- 工作区还包含 `ext/` 目录下的扩展 crate（`ext/agent`、`ext/goal`、`ext/mcp`、`ext/skills` 等），形成扩展点机制（F-006）。

### 反常识

多数 Rust 项目倾向于把核心逻辑堆在一个 `core` crate 中以减少跨 crate 依赖的编译开销。Codex 反其道而行：宁可接受 130+ crate 的编译复杂度，也要保持每个 crate 的单一职责和小体积。这不是渐进式遗留，而是写在贡献指南中的主动架构纪律。

### 行动

- 阅读核心逻辑时，不要只看 `core/`；功能可能已迁移到 `sandboxing/`、`skills/`、`codex-mcp/`、`config/` 等独立 crate。
- 贡献代码前先搜索是否有现成的小 crate 适合放置，避免直接修改 `codex-core`。
- 理解扩展机制：`ext/` 目录下的 crate 通过 `ExtensionRegistry` 注册，是插件化的入口。

---

## Insight 3：多层防御的沙箱执行模型——平台原语 + 策略引擎 + 审批门控

### 陈述

Codex 的命令执行安全不是单一沙箱，而是三层防御：（1）平台级沙箱（macOS Seatbelt、Linux Landlock/bwrap、Windows Sandbox），（2）execpolicy 声明式规则引擎，（3）用户审批策略（AskForApproval）和 SafetyCheck 补丁安全评估。三层独立运作但协同决策。

### 证据

- `codex-sandboxing` crate 按目标 OS 条件编译不同后端：`bwrap`/`landlock` on Linux，`seatbelt` on macOS，`windows` on Windows（F-040）。
- `spawn` 模块设置 `CODEX_SANDBOX_NETWORK_DISABLED` 和 `CODEX_SANDBOX` 环境变量，让子进程自感知沙箱状态（F-042）；AGENTS.md 严禁修改这些变量相关代码（F-043）。
- `execpolicy` crate 提供独立的策略解析器和规则引擎，支持 `PrefixRule`、`NetworkRuleProtocol` 等，可通过 `codex execpolicy check` 独立调用（F-048, F-024）。
- `safety.rs` 的 `SafetyCheck` 枚举（AutoApprove / AskUser / Reject）根据 `AskForApproval` 策略和文件系统沙箱策略综合判断补丁是否可自动批准（F-046）。
- 执行超时硬编码为 10 秒（`DEFAULT_EXEC_COMMAND_TIMEOUT_MS`），输出有 `EXEC_OUTPUT_MAX_BYTES` 和 10,000 个 delta 事件上限（F-044）。

### 反常识

沙箱常被理解为"把命令关进容器"，但 Codex 的模型更精细：平台沙箱负责文件系统/网络隔离，execpolicy 负责命令白名单/黑名单，审批层负责用户信任决策。即使沙箱不可用（如非 Linux/macOS/Windows 平台），SafetyCheck 仍会回退到 AskUser 而非直接放行。此外，Shell 类型被显式建模（Zsh/Bash/Sh/PowerShell/Cmd），因为不同 shell 的参数转义和登录模式直接影响安全边界。

### 行动

- 排查命令执行问题时，需同时检查三层：沙箱后端是否可用、execpolicy 规则是否匹配、审批策略设置。
- 新增 shell 命令支持时，必须在 `shell.rs` 的 `derive_exec_args` 中处理 `-lc`/`-c`/`-Command`/`/c` 等差异。
- Python SDK 用户通过 `Sandbox.read_only`/`workspace_write`/`full_access` 三档预设控制，对应底层的 `SandboxPolicy` 联合类型（F-047）。

---

## Insight 4：AGENTS.md + Skills——文件即上下文的约定优于配置

### 陈述

Codex 不使用集中式的 agent 配置数据库，而是通过文件系统约定注入上下文：`AGENTS.md` 文件沿目录树向上发现并拼接，`SKILL.md` 文件从 skills 目录加载并通过 `@mention` 或命令模式隐式触发。两者都是"文件即指令"，且有严格的大小上限和信任边界。

### 证据

- AGENTS.md 发现算法：从 CWD 向上走到项目根（默认标记为 `.git`），收集路径上所有 `AGENTS.md` 并按从根到叶顺序拼接，不越过项目根（F-055, F-056）。
- 支持 `AGENTS.override.md` 作为本地覆盖文件，以及 `project_doc_fallback_filenames` 配置备选文件名（F-054）。
- 用户指令与项目文档用 `"--- project-doc ---"` 分隔符拼接（F-057）。
- 总大小受 `project_doc_max_bytes` 限制，并发探测上限 256（F-058）；不可信项目完全跳过 AGENTS.md 加载（F-059）。
- Skills 系统有独立 crate，系统 skills 编译时嵌入二进制并安装到 `$CODEX_HOME/skills/.system`，通过指纹标记避免重复写入（F-050, F-051）。
- Skills 支持显式调用（`@skill-name`）和隐式调用（根据 shell 命令和工作目录检测），两种路径都有分析埋点（F-052）。

### 反常识

传统 agent 框架通常将指令存在数据库或配置中心，Codex 却选择纯文件约定——这意味着 agent 行为随代码一起版本控制、code review、分支切换。反常识之处在于：这种"去中心化"设计反而使上下文更可审计，因为每条指令都能追溯到文件系统中的具体路径和提交。Skills 的隐式触发（根据命令自动注入 skill 指令）更进一步：用户不需要知道 skill 存在，系统根据命令模式匹配自动加载。

### 行动

- 项目维护者应在仓库根放置 `AGENTS.md`，子目录可放置补充指令；注意总字节上限。
- 创建 skill 时，在 `.codex/skills/<name>/SKILL.md` 放置 frontmatter + 指令；系统会自动发现。
- 调试上下文注入问题时，检查 `active_project.is_untrusted()` 状态和 `project_doc_max_bytes` 配置。
- 多环境场景下，AGENTS.md 通过 exec-server 的文件系统接口读取，沙箱策略会影响可见性。

---

## Insight 5：TUI 作为一等公民——事件驱动 + 快照测试 + 终端原语深度集成

### 陈述

Codex 的 TUI 不是简单的命令行包装，而是一个完整的事件驱动终端应用，拥有 100+ 子模块、内部消息总线（AppEvent）、ratatui 渲染层、crossterm 终端控制、快照测试体系，以及对 alternate screen、raw mode、bracketed paste、synchronized updates、job control 等终端原语的精细管理。

### 证据

- `tui/src/lib.rs` 声明 100+ 模块（F-027），涵盖 `chatwidget`、`bottom_pane`、`render`、`markdown_render`、`multi_agents`、`model_catalog`、`session_start`、`startup_orchestration` 等。
- `AppEvent` 是内部消息总线，widget 通过发送事件请求 app 层操作，避免直接耦合到 `App` 内部（F-029）。
- 终端层使用 crossterm 的 alternate screen、raw mode、bracketed paste、synchronized updates，Unix 下支持 SIGTSTP job control（F-030）。
- AGENTS.md 对 TUI 代码有专门的样式约定：强制使用 ratatui Stylize 助手、禁止 `.white()`、文本换行必须用 `textwrap::wrap` 或 `wrapping.rs` 助手（F-032, AGENTS.md:158-163）。
- 任何用户可见 UI 变更必须添加或更新 insta 快照测试（F-079）。
- 库代码 `#![deny(clippy::print_stdout, clippy::print_stderr)]` 防止意外绕过渲染抽象（F-025）。
- TUI 还支持 pets（终端宠物动画，含 sixel 图像）、tooltips、keymap 自定义、主题选择器等富交互特性。

### 反常识

TUI 常被视为"开发者工具的附属品"，但 Codex 将其作为主要交互界面（默认无参启动即进入 TUI），并投入了比 CLI 子命令多得多的代码量。非交互模式 `codex exec` 反而是次要路径。更深层的反常识是：TUI 通过 app-server 协议与核心 agent 通信，这意味着 TUI 可以连接本地或远程 app-server（`--remote ws://...`），TUI 本身是一个纯客户端——它不直接执行 agent 逻辑，而是通过 JSON-RPC 驱动 app-server。

### 行动

- 理解 Codex 交互流程应从 TUI 的 `App` 事件循环入手，而非直接读 core agent。
- 修改 UI 时必须同步更新 insta 快照：`just test -p codex-tui` + `cargo insta accept`。
- 远程调试场景可用 `codex --remote ws://host:port` 将 TUI 连接到远程 app-server。
- 新增 TUI 模块应保持 <500 LoC，高触文件（app.rs、chatwidget.rs）不应添加独立方法。
