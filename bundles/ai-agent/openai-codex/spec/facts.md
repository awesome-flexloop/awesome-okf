# OpenAI Codex 事实清单

> 信源根目录：`external/libs/ai/agents/codex/`（以下相对路径均以此根为基准）

## Node.js 启动层（codex-cli）

- F-001: 文件 `codex-cli/package.json` 第2行，包名为 `@openai/codex`；第3行，版本为 `0.0.0-dev`。
- F-002: 文件 `codex-cli/package.json` 第4行，`description` 为 "Codex CLI is a coding agent from OpenAI that runs locally on your computer."。
- F-003: 文件 `codex-cli/package.json` 第5行，`license` 为 `Apache-2.0`。
- F-004: 文件 `codex-cli/package.json` 第6-8行，`bin` 字段把命令名 `codex` 映射到 `bin/codex.js`。
- F-005: 文件 `codex-cli/package.json` 第9行，`"type": "module"`（ESM 模块）。
- F-006: 文件 `codex-cli/package.json` 第10-12行，`engines.node` 要求 `>=16`。
- F-007: 文件 `codex-cli/package.json` 第21行，`packageManager` 为 `pnpm@10.34.5`。
- F-008: 文件 `codex-cli/bin/codex.js` 第16-23行，常量 `PLATFORM_PACKAGE_BY_TARGET` 把 6 个 Rust target triple（如 `x86_64-unknown-linux-musl`）映射到 npm 平台包（如 `@openai/codex-linux-x64`）。
- F-009: 文件 `codex-cli/bin/codex.js` 第28-68行，`switch` 依据 `process.platform`/`process.arch` 推导 `targetTriple`，覆盖 linux/android、darwin、win32。
- F-010: 文件 `codex-cli/bin/codex.js` 第70-72行，无法识别平台时 `throw new Error("Unsupported platform")`。
- F-011: 文件 `codex-cli/bin/codex.js` 第79行，函数 `findCodexExecutable()` 定位原生二进制。
- F-012: 文件 `codex-cli/bin/codex.js` 第88-93行，原生二进制路径为 `vendor/<targetTriple>/bin/codex`（win32 下为 `codex.exe`）。
- F-013: 文件 `codex-cli/bin/codex.js` 第98-107行，找不到二进制时报错并提示按包管理器重装（`npm/pnpm/bun install -g @openai/codex@latest`）。
- F-014: 文件 `codex-cli/bin/codex.js` 第137行，函数 `detectPackageManager()` 探测安装 Codex 所用的包管理器。
- F-015: 文件 `codex-cli/bin/codex.js` 第149-151行，通过 `node_modules/.modules.yaml` 判断是否 pnpm 安装（函数 `isPnpmOwnedCodexInstall`）。
- F-016: 文件 `codex-cli/bin/codex.js` 第181-193行，设置环境变量 `CODEX_MANAGED_PACKAGE_ROOT` 与 `CODEX_MANAGED_BY_NPM/PNPM/BUN` 之一，并删除其余两个。
- F-017: 文件 `codex-cli/bin/codex.js` 第195-198行，`spawn(binaryPath, process.argv.slice(2), { stdio: "inherit", env })` 启动原生进程。
- F-018: 文件 `codex-cli/bin/codex.js` 第224-226行，对 `SIGINT`/`SIGTERM`/`SIGHUP` 三个信号调用 `forwardSignal` 转发给子进程。
- F-019: 文件 `codex-cli/bin/codex.js` 第243-248行，子进程退出后父进程镜像其退出码或重新发出信号（`128 + n` 语义）。

## 安装与构建（docs/install.md）

- F-020: 文件 `docs/install.md` 第7行，系统要求 macOS 12+、Ubuntu 20.04+/Debian 10+、或 Windows 11（通过 WSL2）。
- F-021: 文件 `docs/install.md` 第8行，Git 2.23+（可选，供内置 PR 辅助功能使用）。
- F-022: 文件 `docs/install.md` 第9行，内存最低 4 GB（推荐 8 GB）。
- F-023: 文件 `docs/install.md` 第35行，构建命令为 `cargo build`；第38行，启动 TUI 用 `cargo run --bin codex -- "explain this codebase to me"`。
- F-024: 文件 `docs/install.md` 第54行，Codex 是 Rust 程序，通过 `RUST_LOG` 环境变量配置日志。
- F-025: 文件 `docs/install.md` 第56-61行，设为 `log_dir` 后会在该目录写 `codex-tui.log`，可用 `codex -c log_dir=./.codex-log` 开启。
- F-026: 文件 `docs/install.md` 第63行，非交互模式 `codex exec` 默认 `RUST_LOG=error`，消息内联打印。

## 配置层（codex-rs/config）

- F-027: 文件 `codex-rs/config/src/config_toml.rs` 第152行，文档注释 "Base config deserialized from `~/.codex/config.toml`."。
- F-028: 文件 `codex-rs/config/src/config_toml.rs` 第155行，`pub struct ConfigToml` 定义基础配置结构。
- F-029: 文件 `codex-rs/config/src/config_toml.rs` 第157行，字段 `model: Option<String>` 表示模型选择覆盖。
- F-030: 文件 `codex-rs/config/src/config_toml.rs` 第176行，字段 `approval_policy: Option<AskForApproval>` 为命令执行的默认审批策略。
- F-031: 文件 `codex-rs/config/src/config_toml.rs` 第205行，字段 `sandbox_mode: Option<SandboxMode>` 为沙箱模式。
- F-032: 文件 `codex-rs/config/src/config_toml.rs` 第270行，字段 `mcp_servers: HashMap<String, McpServerConfig>` 定义 MCP 服务器。
- F-033: 文件 `codex-rs/config/src/config_toml.rs` 第293行，字段 `model_providers: HashMap<String, ModelProviderInfo>` 定义用户模型提供方。
- F-034: 文件 `codex-rs/config/src/config_toml.rs` 第323行，字段 `profiles: HashMap<String, ConfigProfile>` 为命名配置档案。
- F-035: 文件 `codex-rs/config/src/config_toml.rs` 第336行，字段 `log_dir: Option<AbsolutePathBuf>` 为日志目录，设置后启用 TUI 文本日志。
- F-036: 文件 `codex-rs/config/defaults.toml` 第2-5行，固定默认值 `include_permissions_instructions`、`include_apps_instructions`、`include_collaboration_mode_instructions`、`include_environment_context` 均为 `true`。
- F-037: 文件 `codex-rs/config/defaults.toml` 第6行，`cli_auth_credentials_store = "file"`。
- F-038: 文件 `codex-rs/config/defaults.toml` 第8行，`project_doc_max_bytes = 32768`。
- F-039: 文件 `codex-rs/config/defaults.toml` 第11行，`file_opener = "vscode"`。
- F-040: 文件 `codex-rs/config/defaults.toml` 第14行，`project_root_markers = [".git"]`。
- F-041: 文件 `codex-rs/config/defaults.toml` 第16-17行，`[history]` 段 `persistence = "save-all"`。
- F-042: 文件 `docs/config.md` 第11-15行，管理员可在 `requirements.toml` 顶层设 `allow_managed_hooks_only = true` 只允许托管 hooks。

## CLI 命令层（codex-rs/cli）

- F-043: 文件 `codex-rs/cli/Cargo.toml` 第2行，crate 名为 `codex-cli`；第9-11行，`[[bin]] name = "codex"` path `src/main.rs`。
- F-044: 文件 `codex-rs/cli/src/main.rs` 第106-113行，clap `#[clap(bin_name = "codex", override_usage = ...)]` 固定命令名与用法。
- F-045: 文件 `codex-rs/cli/src/main.rs` 第115行，结构体 `MultitoolCli` 聚合 `CliConfigOverrides`、`FeatureToggles`、`TuiCli` 与 `Subcommand`。
- F-046: 文件 `codex-rs/cli/src/main.rs` 第133-137行，子命令 `Agents`；第138行 `Exec`（可见别名 `e`）。
- F-047: 文件 `codex-rs/cli/src/main.rs` 第141-178行，子命令 `Review`、`Login`、`Logout`、`Mcp`、`Plugin`、`McpServer`、`AppServer`、`RemoteControl`、`App`、`Completion`、`Update`、`Doctor`、`Sandbox`。
- F-048: 文件 `codex-rs/cli/src/main.rs` 第181-228行，子命令 `Debug`、`Execpolicy`（隐藏）、`Apply`（别名 `a`）、`Resume`、`Queue`、`Archive`、`Delete`、`MigrateRollouts`、`Unarchive`、`Fork`、`Cloud`（别名 `cloud-tasks`）、`ResponsesApiProxy`（隐藏）、`StdioToUds`（隐藏）、`ExecServer`、`Features`。
- F-049: 文件 `codex-rs/cli/src/app_cmd.rs` 第5-13行，`AppCommand { path: PathBuf, download_url_override: Option<String> }` 用于启动桌面应用。

## 非交互执行层（codex-rs/exec）

- F-050: 文件 `codex-rs/exec/src/cli.rs` 第11-13行，`override_usage = "codex exec [OPTIONS] [PROMPT]\n       codex exec [OPTIONS] <COMMAND> [ARGS]"`。
- F-051: 文件 `codex-rs/exec/src/cli.rs` 第20-21行，标志 `--strict-config`（对未知字段报错）。
- F-052: 文件 `codex-rs/exec/src/cli.rs` 第27-44行，标志 `--skip-git-repo-check`、`--ephemeral`、`--ignore-user-config`、`--ignore-rules`、`--output-schema`。
- F-053: 文件 `codex-rs/exec/src/cli.rs` 第55-60行，标志 `--json`（别名 `experimental-json`）以 JSONL 输出事件到 stdout。
- F-054: 文件 `codex-rs/exec/src/cli.rs` 第63-69行，标志 `-o`/`--output-last-message` 把模型最后一条消息写入指定文件。
- F-055: 文件 `codex-rs/exec/src/cli.rs` 第143-153行，枚举 `Command { Resume, Fork, Review }` 作为 `codex exec` 的子命令。
- F-056: 文件 `codex-rs/exec/src/cli.rs` 第267-299行，`ReviewArgs` 含 `--uncommitted`、`--base`、`--commit`、`--title` 等代码审查参数。

## TUI 层（codex-rs/tui）

- F-057: 文件 `codex-rs/tui/src/cli.rs` 第10行起，结构体 `Cli` 承载交互式 TUI 的参数，第13行 `prompt: Option<String>` 为起始提示。
- F-058: 文件 `codex-rs/tui/src/cli.rs` 第64-66行，标志 `-a`/`--ask-for-approval` 映射 `approval_policy: Option<ApprovalModeCliArg>`。
- F-059: 文件 `codex-rs/tui/src/cli.rs` 第68-70行，标志 `--search`（`web_search: bool`）启用联网搜索。
- F-060: 文件 `codex-rs/tui/src/cli.rs` 第75-76行，标志 `--no-alt-screen` 以内联模式运行，保留终端滚动缓冲。

## Skills 层（codex-rs/skills & codex-rs/core）

- F-061: 文件 `codex-rs/skills/src/parser.rs` 第4行，`MAX_NAME_LEN: usize = 64`。
- F-062: 文件 `codex-rs/skills/src/parser.rs` 第6-14行，`SkillFrontmatter` 含字段 `name`、`description`、`metadata`。
- F-063: 文件 `codex-rs/skills/src/parser.rs` 第16-20行，`SkillFrontmatterMetadata` 含 `short_description`（YAML 键 `short-description`）。
- F-064: 文件 `codex-rs/skills/src/parser.rs` 第44-47行，函数 `parse_skill_frontmatter_metadata` 解析并校验 SKILL.md 的 frontmatter。
- F-065: 文件 `codex-rs/skills/src/parser.rs` 第83-85行，`description` 为空时返回 `MissingField("description")`。
- F-066: 文件 `codex-rs/skills/src/model.rs` 第8-20行，`SkillMetadata` 含 `name`、`description`、`short_description`、`interface`、`dependencies`、`policy`、`path_to_skills_md`、`scope`、`plugin_id`、`remote_plugin_id`。
- F-067: 文件 `codex-rs/skills/src/model.rs` 第23-28行，`allows_implicit_invocation()` 默认返回 `true`（除非 policy 显式关闭）。
- F-068: 文件 `codex-rs/skills/src/model.rs` 第63-68行，`SkillPolicy { allow_implicit_invocation: Option<bool>, products: Vec<Product> }`。
- F-069: 文件 `codex-rs/core/src/skills.rs` 第103-108行，`SkillScope` 枚举映射为字符串 `"user"`/`"repo"`/`"system"`/`"admin"`。

## AGENTS.md 层（codex-rs/core）

- F-070: 文件 `codex-rs/core/src/agents_md.rs` 第6-16行，AGENTS.md 发现算法：自 cwd 向上找 `project_root_markers`（默认 `.git`）确定项目根，收集根到 cwd 间所有 AGENTS.md 并拼接，不越过项目根。
- F-071: 文件 `codex-rs/core/src/agents_md.rs` 第42行，`DEFAULT_AGENTS_MD_FILENAME: &str = "AGENTS.md"`。
- F-072: 文件 `codex-rs/core/src/agents_md.rs` 第44行，`LOCAL_AGENTS_MD_FILENAME: &str = "AGENTS.override.md"`。
- F-073: 文件 `codex-rs/core/src/agents_md.rs` 第48行，多个项目文档拼接分隔符为 `"\n\n--- project-doc ---\n\n"`。
- F-074: 文件 `codex-rs/core/src/agents_md.rs` 第53行，`MAX_CONCURRENT_ANCESTOR_PROBES: usize = 256`。

## 命令执行与 Shell 层（codex-rs/core）

- F-075: 文件 `codex-rs/core/src/exec.rs` 第61行，`DEFAULT_EXEC_COMMAND_TIMEOUT_MS: u64 = 10_000`。
- F-076: 文件 `codex-rs/core/src/exec.rs` 第79行，`EXEC_OUTPUT_MAX_BYTES: usize = DEFAULT_OUTPUT_BYTES_CAP`（限制命令输出字节数）。
- F-077: 文件 `codex-rs/core/src/shell.rs` 第10-13行，`Shell { shell_type: ShellType, shell_path: PathBuf }`。
- F-078: 文件 `codex-rs/core/src/shell.rs` 第22-49行，`derive_exec_args`：Zsh/Bash/Sh 用 `-c`/`-lc`，PowerShell 用 `-NoProfile`/`-Command`，Cmd 用 `/c`。

## Python SDK（sdk/python）

- F-079: 文件 `sdk/python/pyproject.toml` 第6行，项目名 `openai-codex`；第7行版本 `0.0.0-dev`；第10行 `requires-python = ">=3.10"`。
- F-080: 文件 `sdk/python/pyproject.toml` 第19行，依赖 `pydantic>=2.12` 与 `openai-codex-cli-bin==0.147.0`。
- F-081: 文件 `sdk/python/src/openai_codex/__init__.py` 第15行，`from ._version import __version__`；第56行起 `__all__` 列表导出公开 API。
- F-082: 文件 `sdk/python/src/openai_codex/client.py` 第67行，`RUNTIME_PKG_NAME = "openai-codex-cli-bin"`。
- F-083: 文件 `sdk/python/src/openai_codex/client.py` 第194-210行，`CodexConfig` 数据类字段：`codex_bin`、`launch_args_override`、`config_overrides`、`cwd`、`env`、`client_name`、`client_title`、`client_version`、`experimental_api`。
- F-084: 文件 `sdk/python/src/openai_codex/client.py` 第213行，`CodexClient` 是 "Synchronous typed JSON-RPC client for `codex app-server` over stdio"。
- F-085: 文件 `sdk/python/src/openai_codex/client.py` 第252-253行，启动子进程参数含 `["app-server", "--listen", "stdio://"]`。
- F-086: 文件 `sdk/python/src/openai_codex/client.py` 第293-310行，`initialize()` 发送 `"initialize"` 方法请求并 `notify("initialized", None)`。
- F-087: 文件 `sdk/python/src/openai_codex/client.py` 第863-864行，`default_codex_home()` 返回 `~/.codex`。
- F-088: 文件 `sdk/python/src/openai_codex/api.py` 第75行，`class Codex`；第104-113行 `login_api_key(api_key)`。
- F-089: 文件 `sdk/python/src/openai_codex/api.py` 第132-170行，`thread_start(...)` 接受 `approval_mode`、`sandbox`、`model`、`cwd` 等关键字参数并返回 `Thread`。
- F-090: 文件 `sdk/python/src/openai_codex/api.py` 第537-557行，`Thread.run(input)` 返回 `TurnResult`（含最终回复）。
- F-091: 文件 `sdk/python/src/openai_codex/_sandbox.py` 第24-26行，`Sandbox` 枚举三个预设：`read_only = "read-only"`、`workspace_write = "workspace-write"`、`full_access = "full-access"`。
- F-092: 文件 `sdk/python/src/openai_codex/_approval_mode.py` 第16-17行，`ApprovalMode` 枚举：`deny_all = "deny_all"`、`auto_review = "auto_review"`。