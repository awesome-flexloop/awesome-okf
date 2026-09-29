---
type: spec
title: "Facts — OpenAI Codex CLI"
---

# Facts — OpenAI Codex CLI

> R-Phase facts extracted from the local source tree at
> `d:\spaces\SpecWeave\external\libs\ai\agents\codex\`.
> Each fact cites the file path and line range where the evidence was found.

## 1. Workspace & Repository Structure

- **F-001**: The repository is a monorepo whose root `package.json` declares the package name `codex-monorepo` with `private: true`, used only for repo-wide maintenance tooling such as Prettier and a `write-hooks-schema` script. — `package.json:1-9`
- **F-002**: The pnpm workspace defines three packages: `codex-cli`, `codex-rs/responses-api-proxy/npm`, and `sdk/typescript`. — `pnpm-workspace.yaml:1-4`
- **F-003**: The pnpm workspace enforces supply-chain policies including `minimumReleaseAge: 10080` (7 days), `blockExoticSubdeps: true`, `strictDepBuilds: true`, and `trustPolicy: no-downgrade`. — `pnpm-workspace.yaml:9-15`
- **F-004**: The root `engines` field requires Node.js `>=22` and pnpm `>=10.34.5`, with the packageManager pinned to `pnpm@10.34.5`. — `package.json:34-38`
- **F-005**: The repository contains three major implementation parts: a Node.js CLI wrapper under `codex-cli/`, a Rust workspace under `codex-rs/`, and a Python SDK under `sdk/python/`. — `LS codex/` directory listing
- **F-006**: The Rust workspace (`codex-rs/Cargo.toml`) declares over 130 workspace members, each crate prefixed with `codex-` per the AGENTS.md convention. — `codex-rs/Cargo.toml:1-138`; `AGENTS.md:5`
- **F-007**: The Rust workspace uses edition `2024`, license `Apache-2.0`, and version `0.0.0` for all internal crates. — `codex-rs/Cargo.toml:141-148`
- **F-008**: The project uses Bazel as a secondary build system alongside Cargo, with `MODULE.bazel` declaring `bazel_skylib`, `platforms`, `protobuf`, `llvm`, and `windows_support` as external dependencies. — `MODULE.bazel:1-9`
- **F-009**: The root `BUILD.bazel` defines custom platforms for Linux (`local_linux` with glibc 2.28 constraint) and multiple Windows ABIs (`gnullvm`, `msvc`), plus an RBE alias. — `BUILD.bazel:5-73`
- **F-010**: The `justfile` sets its working directory to `codex-rs` and provides aliases such as `c` for `codex`, `exec` for non-interactive mode, and `bazel-codex` for Bazel-built runs. — `justfile:1-22,124-131`

## 2. Node.js CLI (codex-cli)

- **F-011**: The npm package name is `@openai/codex`, published with a single `bin` entry mapping the `codex` command to `bin/codex.js`. — `codex-cli/package.json:2-8`
- **F-012**: The Node.js CLI requires Node.js `>=16` and is an ES module (`"type": "module"`), shipping only `bin/codex.js` in its published files. — `codex-cli/package.json:9-15`
- **F-013**: `bin/codex.js` is a thin launcher that detects the platform/architecture triple and resolves a platform-specific native binary from optional dependency packages. — `codex-cli/bin/codex.js:16-77`
- **F-014**: Six platform packages are mapped: `@openai/codex-linux-x64`, `@openai/codex-linux-arm64`, `@openai/codex-darwin-x64`, `@openai/codex-darwin-arm64`, `@openai/codex-win32-x64`, and `@openai/codex-win32-arm64`. — `codex-cli/bin/codex.js:16-23`
- **F-015**: The launcher detects whether it was installed via npm, pnpm, or Bun by searching ancestor `node_modules/.modules.yaml` files and inspecting `npm_config_user_agent`, then sets `CODEX_MANAGED_BY_NPM`, `CODEX_MANAGED_BY_PNPM`, or `CODEX_MANAGED_BY_BUN` accordingly. — `codex-cli/bin/codex.js:118-193`
- **F-016**: The Node.js launcher uses asynchronous `spawn` (not `spawnSync`) so that Node can respond to signals (SIGINT, SIGTERM, SIGHUP) and forward them to the native child process. — `codex-cli/bin/codex.js:112-117,195-226`
- **F-017**: The child exit code or signal is mirrored in the parent process so shell scripts observe the correct exit status. — `codex-cli/bin/codex.js:228-249`

## 3. Rust CLI Entry Point (codex-rs/cli)

- **F-018**: The primary Rust binary is `codex-rs/cli/src/main.rs`, which uses `clap` derive macros to define a `MultitoolCli` with a default interactive TUI mode and numerous subcommands. — `codex-rs/cli/src/main.rs:100-130`
- **F-019**: Subcommands include `agents`, `exec` (alias `e`), `review`, `login`, `logout`, `mcp`, `plugin`, `mcp-server` (deprecated), `app-server`, `resume`, `queue`, `archive`, `delete`, `fork`, `cloud`, `exec-server`, `features`, `sandbox`, `doctor`, and `update`. — `codex-rs/cli/src/main.rs:132-230`
- **F-020**: The `exec` subcommand delegates to `codex_exec::run_main`, while the default (no subcommand) and `agents` subcommand launch the interactive TUI via `run_interactive_tui`. — `codex-rs/cli/src/main.rs:1093-1161`
- **F-021**: The CLI supports `--enable` and `--disable` feature flags that are folded into config overrides as `features.<name>=true/false`, validated against known feature keys via `is_known_feature_key`. — `codex-rs/cli/src/main.rs:960-1006`
- **F-022**: The `--remote` flag accepts `ws://host:port`, `wss://host:port`, `unix://`, or `unix://PATH` to connect the TUI to a remote app-server endpoint. — `codex-rs/cli/src/main.rs:971-983`
- **F-023**: The `sandbox` subcommand is platform-typed: `SeatbeltCommand` on macOS, `LandlockCommand` on Linux, and `WindowsCommand` on Windows. — `codex-rs/cli/src/main.rs:453-458`
- **F-024**: The `app-server` subcommand supports `--listen` with values `stdio://` (default), `unix://`, `ws://IP:PORT`, or `off`, and can generate TypeScript or JSON Schema bindings. — `codex-rs/cli/src/main.rs:546-596,674-692`

## 4. Rust TUI Architecture (codex-rs/tui)

- **F-025**: The TUI library crate is `codex-tui` (`codex-rs/tui/`), and its `lib.rs` forbids accidental stdout/stderr writes with `#![deny(clippy::print_stdout, clippy::print_stderr)]`. — `codex-rs/tui/src/lib.rs:1-5`
- **F-026**: The TUI is built on `ratatui` 0.30 with `crossterm` 0.29 backend, using features `crossterm`, `layout-cache`, and `underline-color`. — `codex-rs/Cargo.toml:388-392`
- **F-027**: The TUI `lib.rs` declares over 100 submodules including `app`, `chatwidget`, `bottom_pane`, `render`, `markdown`, `multi_agents`, `model_catalog`, `session_start`, `startup_orchestration`, and `token_usage`. — `codex-rs/tui/src/lib.rs:95-199`
- **F-028**: The top-level `App` struct in `app.rs` owns the application state and coordinates submodules; the file is explicitly called out in AGENTS.md as a high-touch module that should not grow beyond 800 LoC. — `codex-rs/tui/src/app.rs:1-5`; `AGENTS.md:49-61`
- **F-029**: `AppEvent` is the internal message bus between UI components and the `App` loop; widgets emit events to request actions (opening pickers, persisting config, shutting down) without direct access to `App` internals. — `codex-rs/tui/src/app_event.rs:1-10`
- **F-030**: The TUI terminal layer (`tui.rs`) uses crossterm's alternate screen, raw mode, bracketed paste, and synchronized updates; it supports job control (SIGTSTP) on Unix. — `codex-rs/tui/src/tui.rs:17-29,57-76`
- **F-031**: The standalone `codex-tui` binary (`tui/src/main.rs`) is a thinner entry point that parses a `TopCli`, splices config overrides, and calls `codex_tui::run_main`. — `codex-rs/tui/src/main.rs:41-83`
- **F-032**: TUI styling conventions require ratatui `Stylize` trait helpers (e.g., `"text".red()`, `"text".dim()`) over manual `Span::styled`, and forbid hardcoded `.white()`. — `AGENTS.md:137-156`

## 5. Rust Core Agent Logic (codex-rs/core)

- **F-033**: The `codex-core` crate (`codex-rs/core/`) is the largest crate; AGENTS.md explicitly instructs contributors to "resist adding code to codex-core" and prefer new or existing smaller crates. — `AGENTS.md:72-83`
- **F-034**: `core/src/lib.rs` declares modules for `agent`, `client`, `config`, `context`, `exec`, `mcp`, `sandboxing`, `skills`, `agents_md`, `shell`, `spawn`, `safety`, `thread_manager`, and `codex_thread` (the main conversation type). — `codex-rs/core/src/lib.rs:8-150`
- **F-035**: `CodexThread` is the core conversation/thread type, and `ThreadManager` manages thread lifecycle; older names `ConversationManager`, `NewConversation`, and `CodexConversation` are preserved as deprecated type aliases. — `codex-rs/core/src/lib.rs:44,119-135`
- **F-036**: The `agent` submodule contains `agent_resolver`, `control`, `registry`, `role`, and `status`, supporting multi-agent thread spawning with depth limits (`exceeds_thread_spawn_depth_limit`). — `codex-rs/core/src/agent/mod.rs:1-11`
- **F-037**: The core library also forbids direct stdout/stderr writes with `#![deny(clippy::print_stdout, clippy::print_stderr)]`. — `codex-rs/core/src/lib.rs:3-6`
- **F-038**: Model-visible context rules mandate incremental building (no history rewrite), bounded item sizes (no item > 10K tokens), and all injected fragments must be structs implementing `ContextualUserFragment`. — `AGENTS.md:91-100`
- **F-039**: The config module (`core/src/config/mod.rs`) integrates permission profiles, network proxy, OSS providers, features flags, MCP servers, model providers, and sandbox settings into a unified `Config`. — `codex-rs/core/src/config/mod.rs:1-192`

## 6. Sandbox & Execution Model

- **F-040**: The `codex-sandboxing` crate provides platform-specific sandboxes: Linux `landlock` and `bwrap` (bubblewrap), macOS `seatbelt`, and Windows sandboxing. — `codex-rs/sandboxing/src/lib.rs:1-12`
- **F-041**: `SandboxType`, `SandboxManager`, `SandboxCommand`, `SandboxTransformRequest`, and `get_platform_sandbox` are the public sandboxing API surface. — `codex-rs/sandboxing/src/lib.rs:20-30`
- **F-042**: The `spawn` module sets two sandbox environment variables: `CODEX_SANDBOX_NETWORK_DISABLED` (non-empty when network is restricted) and `CODEX_SANDBOX` (e.g., `"seatbelt"` on macOS). — `codex-rs/core/src/spawn.rs:13-26`
- **F-043**: AGENTS.md forbids adding or modifying code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR` because tests rely on these being set in the sandbox. — `AGENTS.md:8-10`
- **F-044**: The `exec` module defines `DEFAULT_EXEC_COMMAND_TIMEOUT_MS = 10_000` (10 seconds), `EXEC_OUTPUT_MAX_BYTES` tied to `DEFAULT_OUTPUT_BYTES_CAP`, and a hard cap of `MAX_EXEC_OUTPUT_DELTAS_PER_CALL = 10_000`. — `codex-rs/core/src/exec.rs:61-83`
- **F-045**: The shell module supports four shell types: `Zsh`, `Bash`, `Sh` (using `-lc`/`-c`), `PowerShell` (`-NoProfile -Command`), and `Cmd` (`/c`). — `codex-rs/core/src/shell.rs:22-49`
- **F-046**: The `safety` module defines `SafetyCheck` with three variants: `AutoApprove`, `AskUser`, and `Reject { reason }`, and assesses patch safety based on approval policy and sandbox enforcement. — `codex-rs/core/src/safety.rs:19-80`
- **F-047**: The Python SDK exposes three sandbox presets as an enum: `read_only`, `workspace_write`, and `full_access`, mapping to wire types `readOnly`, `workspaceWrite`, and `dangerFullAccess`. — `sdk/python/src/openai_codex/_sandbox.py:15-26,42-73`
- **F-048**: The `execpolicy` crate provides a policy parser and rule engine with `PrefixRule`, `NetworkRuleProtocol`, `PatternToken`, and `ExecPolicyCheckCommand` for checking commands against execution policy files. — `codex-rs/execpolicy/src/lib.rs:1-33`

## 7. Skills System

- **F-049**: The `codex-skills` crate loads and parses skills from SKILL.md files, with modules for `loading`, `parser`, `model`, `mentions`, `selection`, `invocation`, and `interface`. — `codex-rs/skills/src/lib.rs:1-44`
- **F-050**: System skills are embedded at compile time via `include_dir::include_dir!("$CARGO_MANIFEST_DIR/src/assets/samples")` and installed to `$CODEX_HOME/skills/.system` with a fingerprint marker to avoid redundant writes. — `codex-rs/skills/src/lib.rs:55-99`
- **F-051**: The skills directory name is `"skills"`, the system subdirectory is `".system"`, and the marker file is `".codex-system-skills.marker"` salted with `"v1"`. — `codex-rs/skills/src/lib.rs:57-60`
- **F-052**: In `codex-core`, the `skills` module handles both explicit skill invocations (user `@mentions`) and implicit invocations detected from shell commands, emitting analytics via `codex.skill.injected` counter. — `codex-rs/core/src/skills.rs:36-100`
- **F-053**: The `.codex/skills/` directory in the repository root contains an example skill `test-tui/SKILL.md`, demonstrating the project-local skills convention. — `LS .codex/skills/`

## 8. AGENTS.md Support

- **F-054**: `DEFAULT_AGENTS_MD_FILENAME` is `"AGENTS.md"` and `LOCAL_AGENTS_MD_FILENAME` is `"AGENTS.override.md"`. — `codex-rs/core/src/agents_md.rs:41-44`
- **F-055**: AGENTS.md discovery walks upward from the CWD to the project root (identified by `project_root_markers`, default `.git`), collects every `AGENTS.md` from root to CWD, and concatenates them in order. — `codex-rs/core/src/agents_md.rs:1-17`
- **F-056**: The discovery does not walk past the project root; if no marker is found, only the CWD is considered; an empty marker list disables parent traversal entirely. — `codex-rs/core/src/agents_md.rs:8-17`
- **F-057**: User-provided instructions and project AGENTS.md content are concatenated with the separator `"\n\n--- project-doc ---\n\n"`. — `codex-rs/core/src/agents_md.rs:46-48`
- **F-058**: The project doc total size is bounded by `config.project_doc_max_bytes`, and concurrent ancestor probes are capped at `MAX_CONCURRENT_ANCESTOR_PROBES = 256`. — `codex-rs/core/src/agents_md.rs:50-53,68`
- **F-059**: Untrusted projects (where `config.active_project.is_untrusted()`) skip AGENTS.md loading entirely and return only host-provided user instructions. — `codex-rs/core/src/agents_md.rs:64-66`

## 9. Config System

- **F-060**: The primary config file is `config.toml` (`CONFIG_TOML_FILE = "config.toml"`), loaded by the `codex-config` crate which supports layered config, requirements, profiles, and schema validation. — `codex-rs/config/src/lib.rs:40`
- **F-061**: The `codex-config` crate exposes modules for `config_toml`, `permissions_toml`, `profile_toml`, `loader`, `merge`, `schema`, `types`, `mcp_edit`, and `state`. — `codex-rs/config/src/lib.rs:1-38`
- **F-062**: Config supports V2 profiles via `ProfileV2Name`, layering `$CODEX_HOME/<name>.config.toml` on top of the base user config, selected with `--profile`/`-p`. — `codex-rs/cli/src/lib.rs:64-66`
- **F-063**: The `--strict-config` flag causes Codex to error when `config.toml` contains unrecognized fields. — `codex-rs/cli/src/main.rs:303-305`
- **F-064**: The config system supports managed requirements via `requirements.toml`; admins can set `allow_managed_hooks_only = true` there to restrict hooks to managed layers only. — `docs/config.md:9-15`

## 10. MCP (Model Context Protocol) Support

- **F-065**: The `codex-mcp` crate provides MCP client/runtime functionality including `McpRuntime`, `McpManager`, `McpConfig`, `ToolInfo`, `McpServerRegistration`, and resource clients. — `codex-rs/codex-mcp/src/lib.rs:1-48`
- **F-066**: The `codex-core` `mcp` module defines `McpManager` which coordinates plugin managers, extension registries, Codex Apps tools cache, and tool catalog cache across thread environments. — `codex-rs/core/src/mcp.rs:72-78`
- **F-067**: MCP servers can be configured in `config.toml` under `mcp_servers`, and the CLI provides `codex mcp` subcommands for management. — `codex-rs/cli/src/main.rs:150-151,1199-1210`
- **F-068**: The `codex mcp-server` subcommand runs Codex as a stdio MCP server (though it is deprecated and warns on use). — `codex-rs/cli/src/main.rs:156-157,1183-1198`
- **F-069**: The project depends on `rmcp` version `=3.1.3` for Rust MCP protocol implementation. — `codex-rs/Cargo.toml:401`

## 11. Python SDK

- **F-070**: The Python package is named `openai-codex`, requires Python `>=3.10`, and is built with `uv_build` (PEP 517 backend). — `sdk/python/pyproject.toml:1-11`
- **F-071**: Runtime dependencies are `pydantic>=2.12` and `openai-codex-cli-bin==0.147.0` (the pinned native Codex binary). — `sdk/python/pyproject.toml:19`
- **F-072**: The SDK exposes synchronous `Codex` and asynchronous `AsyncCodex` clients, plus `Thread`, `AsyncThread`, `TurnHandle`, `TurnResult`, input types, `Sandbox`, and `ApprovalMode`. — `sdk/python/src/openai_codex/__init__.py:16-38`
- **F-073**: The `Codex` client starts its runtime connection in `__init__`, supports context manager protocol (`with Codex() as codex:`), and validates initialize metadata on startup. — `sdk/python/src/openai_codex/api.py:75-95`
- **F-074**: The SDK communicates with the native Codex binary via a subprocess JSON-RPC transport; `_installed_codex_path()` resolves the binary from the `codex_cli_bin` package or `CodexConfig.codex_bin`. — `sdk/python/src/openai_codex/client.py:111-119`
- **F-075**: The SDK includes generated protocol models under `src/openai_codex/generated/` (`v2_all.py`, `notification_registry.py`) produced from the app-server protocol schema. — `sdk/python/src/openai_codex/client.py:21-55`; glob `sdk/python/src/**/*.py`
- **F-076**: Authentication methods include ChatGPT browser login (`login_chatgpt`), device-code login (`login_chatgpt_device_code`), and API key login (`login_api_key`). — `sdk/python/README.md:31-59`

## 12. Observability, Testing & Build Conventions

- **F-077**: The TUI honors the `RUST_LOG` environment variable for tracing; non-interactive `codex exec` defaults to `RUST_LOG=error`. — `docs/install.md:52-63`
- **F-078**: Tests use `cargo-nextest` via `just test`, with `RUST_MIN_STACK=8388608` (8 MiB) and `NEXTEST_PROFILE=local`; direct `cargo test` is discouraged. — `justfile:81-92`; `AGENTS.md:64-68`
- **F-079**: The project uses `insta` for snapshot testing, especially in the TUI; any user-visible UI change requires updated snapshots. — `AGENTS.md:180-202`; `codex-rs/Cargo.toml:352`
- **F-080**: The workspace enforces strict Clippy lints including `deny` for `unwrap_used`, `expect_used`, `redundant_clone`, `manual_map`, `await_holding_lock`, and many others. — `codex-rs/Cargo.toml:506-542`
- **F-081**: The project does not accept external code contributions or pull requests; community participation is limited to issues, bug reports, and feedback. — `docs/contributing.md:5-13`
- **F-082**: The repository is licensed under Apache-2.0 and requires an Individual Contributor License Agreement (CLA) for any contributions. — `README.md:81`; `docs/CLA.md:1-6`
