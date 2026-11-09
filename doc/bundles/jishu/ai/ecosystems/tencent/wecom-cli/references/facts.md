---
type: reference
title: wecom-cli 源码事实登记（R 阶段）
description: 企业微信官方 CLI @wecom/cli 1.3.4 固定基线的零推测源码事实，F-001 起共 172 条
tags: [wecom, wecom-cli, rust, cli, facts]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: R（事实采集）
baseline: 1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde（npm @wecom/cli 1.3.4）
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
---

# wecom-cli 源码事实登记

本文登记企业微信官方 CLI（npm 包 `@wecom/cli` 1.3.4）在固定基线 commit `1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde` 上的源码事实。所有事实只描述该 commit 的代码与文件现状，不涉及历史沿革、设计动机与效果评价。证据位置一律写作相对仓库根的正斜杠路径加行号（`路径:行号` 或 `路径:起-止`），行号取自对固定基线文件的实测检索。

## 一、仓库与构建

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-001 | 仓库根 `Cargo.toml` 首行声明 `[workspace]`，第 2 行为 `resolver = "3"`。 | `Cargo.toml:1-2` | `Get-Content Cargo.toml -TotalCount 2` |
| F-002 | `Cargo.toml` 的 `members` 数组含 5 个成员路径：`crates/wecom`、`crates/wecom-cli`、`crates/wecom-error`、`crates/wecom-fs`、`crates/wecom-transport`。 | `Cargo.toml:3-9` | `Get-Content Cargo.toml -TotalCount 9` |
| F-003 | `[workspace.package]` 段设 `version = "1.3.4"`、`license = "MIT"`，`repository` 与 `homepage` 均为 `https://github.com/WecomTeam/wecom-cli`。 | `Cargo.toml:11-15` | `Get-Content Cargo.toml -TotalCount 15` |
| F-004 | `[workspace.dependencies]` 中 `wecom` 声明为 `version = "1.1.0"`、`path = "crates/wecom"`、`default-features = false`；`wecom-transport` 同为 `1.1.0` 且 `default-features = false`。 | `Cargo.toml:18-21` | `Get-Content Cargo.toml -TotalCount 21` |
| F-005 | MSRV 在 `clippy.toml` 第 1 行登记为 `msrv = "1.85.0"`。 | `clippy.toml:1` | `Get-Content clippy.toml -TotalCount 1` |
| F-006 | `crates/wecom-cli/Cargo.toml` 的 `[[bin]]` 段设 `name = "wecom-cli"`、`path = "src/main.rs"`；该 crate `edition = "2024"`。 | `crates/wecom-cli/Cargo.toml:4-12` | `Get-Content crates/wecom-cli/Cargo.toml -TotalCount 12` |
| F-007 | `crates/wecom-cli` 的 `[features]` 含 `default = ["call-chain"]`、`call-chain = ["dep:libc", "dep:windows-sys"]`、`custom-endpoint = ["wecom/custom-endpoint"]`、`skip-auth-check = []`。 | `crates/wecom-cli/Cargo.toml:14-18` | `Get-Content crates/wecom-cli/Cargo.toml -TotalCount 18` |
| F-008 | `crates/wecom-cli` 依赖直接声明 `aes-gcm = "0.11"` 与 `clap = "4.6"`。 | `crates/wecom-cli/Cargo.toml:21-24` | `Select-String -Path crates/wecom-cli/Cargo.toml -Pattern 'aes-gcm|clap'` |
| F-009 | `package.json` 的 `name` 为 `@wecom/cli`，`version` 为 `1.3.4`。 | `package.json:2-3` | `Get-Content package.json -TotalCount 3` |
| F-010 | `package.json` 声明 `"type": "module"`，`bin` 映射只有一项：`"wecom-cli": "./bin/wecom.js"`。 | `package.json:17-20` | `Get-Content package.json -TotalCount 20` |
| F-011 | `package.json` 的 `files` 白名单为 `"bin"` 与 `"README.md"` 两项。 | `package.json:21-24` | `Get-Content package.json -TotalCount 24` |
| F-012 | `package.json` 的 `scripts` 含 10 条命令：`check`、`fmt`、`fmt:check`、`lint`、`lint:all`、`prepare`、`test`、`test:default`、`test:skip-auth-check`、`test:doc`。 | `package.json:25-36` | `Get-Content package.json -TotalCount 36` |
| F-013 | `lint` 脚本为 `cargo clippy --workspace --all-targets --features custom-endpoint -- -D warnings`；`lint:all` 追加 `cargo hack` 与 `--feature-powerset`。 | `package.json:29-30` | `Select-String -Path package.json -Pattern 'lint'` |
| F-014 | `package.json` 设 `packageManager` 为 `pnpm@12.3.4`，`engines.node` 为 `>=18`。 | `package.json:53-56` | `Select-String -Path package.json -Pattern 'packageManager|node'` |
| F-015 | `bin/wecom.js` 的 `platformMap` 含 5 个键：`darwin-arm64`、`darwin-x64`、`linux-arm64`、`linux-x64`、`win32-x64`，值分别为对应的 `@wecom/cli-<platform>` 包名。 | `bin/wecom.js:17-23` | `Get-Content bin/wecom.js -TotalCount 23` |
| F-016 | `bin/wecom.js` 在 `os.platform() === 'win32'` 时把二进制文件名取为 `wecom-cli.exe`，其余平台取 `wecom-cli`。 | `bin/wecom.js:44` | `Select-String -Path bin/wecom.js -Pattern 'win32'` |
| F-017 | `bin/wecom.js` 用 `execFileSync(binaryPath, process.argv.slice(2), { stdio: 'inherit', env: process.env })` 调用平台二进制，并在捕获异常时以 `error.status` 作为进程退出码。 | `bin/wecom.js:64-72` | `Get-Content bin/wecom.js | Select-Object -Skip 63 -First 10` |
| F-018 | `pnpm-workspace.yaml` 的 `packages` 为 `'.'` 与 `'packages/*'`；`allowBuilds` 只放行 `lefthook: true`。 | `pnpm-workspace.yaml:1-5` | `Get-Content pnpm-workspace.yaml` |
| F-019 | `packages/` 下存在 5 个平台子包目录：`darwin-arm64`、`darwin-x64`、`linux-arm64`、`linux-x64`、`win32-x64`，每个目录含 `CHANGELOG.md`、`LICENSE`、`README.md`、`package.json` 共 4 个文件。 | `packages/:1-20` | `git -C <repo> ls-tree -r HEAD --name-only | Select-String '^packages/'` |
| F-020 | `.changeset/config.json` 的 `fixed` 组把 6 个包固定同版本发布：`@wecom/cli`、`@wecom/cli-darwin-arm64`、`@wecom/cli-darwin-x64`、`@wecom/cli-linux-x64`、`@wecom/cli-linux-arm64`、`@wecom/cli-win32-x64`。 | `.changeset/config.json:5-14` | `Get-Content .changeset/config.json` |
| F-021 | `.changeset/config.json` 设 `changelog` 为 `@changesets/cli/changelog`、`access` 为 `public`、`baseBranch` 为 `main`、`commit` 为 `false`。 | `.changeset/config.json:3-17` | `Get-Content .changeset/config.json` |
| F-022 | `CHANGELOG.md` 顶层条目为 `## 1.3.4`，其 `### Patch Changes` 下只有一条变更记录 `a0f3749: 增强 trace 调用来源识别能力…`。 | `CHANGELOG.md:3-7` | `Get-Content CHANGELOG.md -TotalCount 7` |
| F-023 | `Cargo.toml` 的 `[profile.release]` 设 `strip = true`、`lto = true`、`codegen-units = 1`。 | `Cargo.toml:35-38` | `Get-Content Cargo.toml | Select-Object -Skip 34 -First 5` |
| F-024 | `rustfmt.toml` 设 `edition = "2024"`、`max_width = 100`、`tab_spaces = 4`、`use_field_init_shorthand = true`、`use_try_shorthand = true`。 | `rustfmt.toml:1-5` | `Get-Content rustfmt.toml` |
| F-025 | `commitlint.config.js` 的 `type-enum` 列出 12 个 type：`feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`、`revert`、`skills`。 | `commitlint.config.js:5-22` | `Get-Content commitlint.config.js` |
| F-026 | `commitlint.config.js` 设 `subject-max-length` 为 100、`header-max-length` 为 120，且 `type-empty`、`subject-empty` 均为 `never`。 | `commitlint.config.js:23-30` | `Get-Content commitlint.config.js | Select-Object -Skip 22` |
| F-027 | `lefthook.yml` 的 `pre-commit` 段设 `parallel: false`，含 3 个命令：`fmt`（`rustfmt +nightly --check`）、`clippy`（`cargo clippy --workspace --all-targets -- -D warnings`）、`eslint`（对暂存 `.js/.ts` 执行 `npx eslint`）。 | `lefthook.yml:1-12` | `Get-Content lefthook.yml -TotalCount 12` |
| F-028 | `lefthook.yml` 的 `commit-msg` 段执行 `npx --no -- commitlint --edit {1}`。 | `lefthook.yml:14-17` | `Get-Content lefthook.yml | Select-Object -Skip 13 -First 4` |
| F-029 | `lefthook.yml` 的 `pre-push` 段设 `parallel: true`，含 `test`（`pnpm test`）与 `check`（`pnpm check`）两个命令，`glob` 均为 `*.rs`。 | `lefthook.yml:19-27` | `Get-Content lefthook.yml | Select-Object -Skip 18` |
| F-030 | `eslint.config.js` 由 `tseslint.config` 组合 `eslint.configs.recommended`、`...tseslint.configs.recommended` 与 `eslint-plugin-prettier/recommended`，`ignores` 为 `node_modules/`、`packages/*/bin/`、`target/`。 | `eslint.config.js:6-12` | `Get-Content eslint.config.js -TotalCount 12` |
| F-031 | `prettier.config.js` 仅设一项配置 `singleQuote: true`。 | `prettier.config.js:4-6` | `Get-Content prettier.config.js` |
| F-032 | `LICENSE` 首行为 `MIT License`，第 3 行为 `Copyright (c) 2026 WeCom`。 | `LICENSE:1-3` | `Get-Content LICENSE -TotalCount 3` |

## 二、命令模型

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-033 | CLI 入口 `main.rs` 用 `#[tokio::main]` 标注 `async fn main()`，函数体第一句为 `dotenvy::dotenv().ok()`。 | `crates/wecom-cli/src/main.rs:17-19` | `Get-Content crates/wecom-cli/src/main.rs -TotalCount 19` |
| F-034 | 根命令由 `Command::new(self.client.bin_name())` 构造，设 `.version(constants::CLI_INFO.display_with_name(...))` 与 `.arg_required_else_help(true)`。 | `crates/wecom/src/client/run/execute.rs:157-159` | `Get-Content crates/wecom/src/client/run/execute.rs -TotalCount 159` |
| F-035 | 扩展（自定义）命令注册在服务发现子命令之前：`cmd.subcommands(custom_cmds.iter().map(|c| c.command().clone()))`。 | `crates/wecom/src/client/run/execute.rs:163-164` | `Select-String -Path crates/wecom/src/client/run/execute.rs -Pattern 'custom_cmds.iter'` |
| F-036 | 构建根命令前先构造 `taken` 名称集合，成员为自定义命令名、服务规范名、内置子命令名；alias 注册时以该集合判定冲突并跳过。 | `crates/wecom/src/client/run/execute.rs:169-175` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 168 -First 8` |
| F-037 | 遍历 `service_list` 时，仅当 `target_service` 的 `name` 与当前服务名相等才传入 `target_schema`，其余服务以 `None` 构建骨架树；与自定义命令同名的服务被跳过。 | `crates/wecom/src/client/run/execute.rs:177-191` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 176 -First 16` |
| F-038 | 服务 alias 以 `service_cmd.alias(alias)` 注册，冲突时记 `warn` 并跳过；随后以 `cmd.subcommand(service_cmd)` 挂入根命令。 | `crates/wecom/src/client/run/execute.rs:193-204` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 192 -First 12` |
| F-039 | 内置子命令 `cache`、`schema` 在服务子命令之后追加（`cmd.subcommands(post_cmds)`），其唯一来源为 `fn post_subcmds() -> [Command; 2]`。 | `crates/wecom/src/client/run/execute.rs:206-207`、`crates/wecom/src/client/run/execute.rs:249-260` | `Select-String -Path crates/wecom/src/client/run/execute.rs -Pattern 'post_subcmds'` |
| F-040 | 解析成功后按 `matches.subcommand()` 分派三段：`("cache", m)`、`("schema", m)`、其余名字先查自定义命令、再落 `service::handle_service_cmd`；无子命令返回 `Error::other("Missing subcommand")`。 | `crates/wecom/src/client/run/execute.rs:103-113` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 102 -First 12` |
| F-041 | `execute` 从 argv 中取第一个满足 `== "-V"`、`== "--version"` 或不以 `-` 开头的 token 作为 `first_arg`。 | `crates/wecom/src/client/run/execute.rs:41-47` | `Get-Content crates/wecom/src/client/run/execute.rs -TotalCount 47` |
| F-042 | `first_arg` 为 `-V` 或 `--version` 时，打印 `constants::CLI_INFO.display_with_name(bin_name)` 后直接返回。 | `crates/wecom/src/client/run/execute.rs:51-55` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 50 -First 6` |
| F-043 | 当 `first_arg` 命中内置子命令或自定义命令时跳过 `list_services_with_options`，`service_list` 置为空数组。 | `crates/wecom/src/client/run/execute.rs:57-69` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 56 -First 14` |
| F-044 | 命令树构建分两阶段：异步阶段只收集 `service_list` 与目标 `schema`；同步阶段由闭包 `build_root_cmd` 纯函数建树，并以 `try_get_matches_from_mut` 解析。 | `crates/wecom/src/client/run/execute.rs:61-97` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 60 -First 38` |
| F-045 | 后台返回错误码 10021 时，按参数/用法错误处理：渲染 `error:` 行加当前命令 help，以 `CliOutput` 返回，退出码 2。 | `crates/wecom/src/client/run/execute.rs:116-120` | `Get-Content crates/wecom/src/client/run/execute.rs | Select-Object -Skip 115 -First 6` |
| F-046 | 文档把命令分为四类形态：`<service> [resource...] <method>`、`<service> +<helper>`、`auth <init\|show>`、`schema … / cache …`。 | `docs/cli-reference.md:7-14` | `Get-Content docs/cli-reference.md -TotalCount 14` |
| F-047 | 文档列出的常见服务品类共 13 个：`message`、`mail`、`doc`、`sheet`、`smartsheet`、`smartpage`、`calendar`、`meeting`、`todo`、`disk`、`contact`、`media`、`identity`。 | `docs/cli-reference.md:19` | `Get-Content docs/cli-reference.md | Select-Object -Skip 18 -First 1` |
| F-048 | 文档列出 `auth init` 的 4 个参数：`--noninteractive`、`--no-browser`、`--output-qrcode <PATH>`、`--manual`。 | `docs/cli-reference.md:40-45` | `Get-Content docs/cli-reference.md | Select-Object -Skip 39 -First 7` |
| F-049 | 文档列出 `auth show` 的参数 `--status`，输出 `authorized` / `unauthorized` 单行。 | `docs/cli-reference.md:51-53` | `Get-Content docs/cli-reference.md | Select-Object -Skip 50 -First 4` |
| F-050 | 文档列出请求体给定的两种方式：`--json '<JSON>'` 直接给完整请求体、`--set path=value` 深层覆盖且可重复。 | `docs/cli-reference.md:87-91` | `Get-Content docs/cli-reference.md | Select-Object -Skip 86 -First 6` |
| F-051 | 文档列出 `--dry-run`、`--page-count <n>`（输出 NDJSON）、`--page-delay <ms>`（默认 100）、`--output`/`-o`、`--output-dir <dir>`（默认当前目录）5 个 flag。 | `docs/cli-reference.md:105-111` | `Get-Content docs/cli-reference.md | Select-Object -Skip 104 -First 8` |
| F-052 | 文档列出 4 条内建命令用法：`schema list`、`schema get <service.resource.method>`、`cache status`、`cache clear`。 | `docs/cli-reference.md:124-129` | `Get-Content docs/cli-reference.md | Select-Object -Skip 123 -First 7` |
| F-053 | `handle_service_cmd` 先处理 service 级 `--doc`（打印本地或远程 doc）与 `--schema`（`serde_json::to_string_pretty`），再进入子命令路径解析。 | `crates/wecom/src/service/handler.rs:37-55` | `Get-Content crates/wecom/src/service/handler.rs -TotalCount 55` |
| F-054 | 子命令路径命中 helper 时（`svc.helper(&cmd_path_strs)`），按 `--help`、`--schema`、`--doc`、`helper.execute` 顺序分派，并在 helper 分支内 `return`，不再走 method 分支。 | `crates/wecom/src/service/handler.rs:62-99` | `Get-Content crates/wecom/src/service/handler.rs | Select-Object -Skip 61 -First 38` |
| F-055 | helper 查找规则：`HelperRegistry::get_helper` 以路径最后一段为 helper 名、其余段与 `Helper::path()` 全等匹配。 | `crates/wecom/src/helpers/registry.rs:38-44` | `Get-Content crates/wecom/src/helpers/registry.rs | Select-Object -Skip 37 -First 8` |
| F-056 | method 查找 `svc.method(&cmd_path_strs)?` 发生在解析 `MethodCmdArgs` 与装配 payload 之前。 | `crates/wecom/src/service/handler.rs:101-114` | `Get-Content crates/wecom/src/service/handler.rs | Select-Object -Skip 100 -First 15` |
| F-057 | 启用 `skip-auth-check` 特性构建时不注册 auth 命令（`#[cfg(not(feature = "skip-auth-check"))]`），未知子命令走 `InvalidSubcommand`、退出码 2。 | `crates/wecom-cli/src/main.rs:89-92` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 88 -First 5` |
| F-058 | 命令未找到时向 stderr 打印常量 `SKILL_HINT`，文案为“该接口不存在，可能为接口命令错误，请更新到最新 skill 后重试”。 | `crates/wecom-cli/src/main.rs:101-111` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 100 -First 12` |
| F-059 | 顶层错误处理以 `println!("{}", err.render())` 输出，并 `std::process::exit(err.exit_code())`。 | `crates/wecom-cli/src/main.rs:99-107` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 98 -First 10` |

## 三、5 个 crate 的职责与关键模块

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-060 | `crates/wecom/src/lib.rs` 中 `pub mod telemetry` 与 `pub mod transport` 为公开模块，`pub(crate) mod builtins` 与 `pub(crate) mod client` 为 crate 内私有模块。 | `crates/wecom/src/lib.rs:55-60` | `Get-Content crates/wecom/src/lib.rs | Select-Object -Skip 54 -First 7` |
| F-061 | `wecom` 顶层再导出 `Client`、`ClientBuilder`、`CliRun`、`CustomCommand`、`EndpointCatalog`、`EndpointKey`、`default_private_fs`、`default_workspace_fs` 等 `client` 类型。 | `crates/wecom/src/lib.rs:37-41` | `Get-Content crates/wecom/src/lib.rs | Select-Object -Skip 36 -First 6` |
| F-062 | 同文件再导出 `CLI_INFO`、`CliInfo`、`DEFAULT_BIN_NAME`（来自 `constants`），以及 `Helper`、`HelperMeta`、`HelperRegistry`（来自 `helpers`）与 `ServiceInfo`（来自 `registry`）。 | `crates/wecom/src/lib.rs:42-48` | `Get-Content crates/wecom/src/lib.rs | Select-Object -Skip 41 -First 8` |
| F-063 | `Client::config_dir()` 的文档写明默认值为 `~/.config/wecom`，返回 `&Path`。 | `crates/wecom/src/client/mod.rs:101-104` | `Get-Content crates/wecom/src/client/mod.rs | Select-Object -Skip 100 -First 5` |
| F-064 | `Client::cache_dir()` 返回 `self.config_dir.join("cache")`，文档写明缓存目录为 `<config_dir>/cache` 且不可独立设置。 | `crates/wecom/src/client/mod.rs:106-111` | `Get-Content crates/wecom/src/client/mod.rs | Select-Object -Skip 105 -First 7` |
| F-065 | `Client::bin_name()` 返回 `&self.bin_name`，该值出现在 `--version` / `--help` / `--doc` 输出中的命令名位置。 | `crates/wecom/src/client/mod.rs:128-132` | `Get-Content crates/wecom/src/client/mod.rs | Select-Object -Skip 127 -First 6` |
| F-066 | `ClientBuilder` 提供 `private_fs`、`workspace_fs`、`config_dir` 三个链式设置方法，分别在第 92、113、138 行声明。 | `crates/wecom/src/client/builder.rs:92-138` | `Select-String -Path crates/wecom/src/client/builder.rs -Pattern 'pub fn (private_fs|workspace_fs|config_dir)'` |
| F-067 | `ClientBuilder::build(self) -> Result<Client>` 在第 258 行声明。 | `crates/wecom/src/client/builder.rs:258` | `Select-String -Path crates/wecom/src/client/builder.rs -Pattern 'pub fn build'` |
| F-068 | registry 缓存 TTL 常量定义为 `pub(super) const CACHE_TTL: Duration = Duration::from_secs(60)`。 | `crates/wecom/src/registry/mod.rs:14` | `Select-String -Path crates/wecom/src/registry/mod.rs -Pattern 'CACHE_TTL'` |
| F-069 | 磁盘缓存新鲜度判定为 `modified.elapsed().unwrap_or_default() >= CACHE_TTL` 即视为过期并向远端重取。 | `crates/wecom/src/registry/cache.rs:115-126` | `Get-Content crates/wecom/src/registry/cache.rs | Select-Object -Skip 114 -First 13` |
| F-070 | 缓存文件命名规则：服务名为空时用 `catalog.json`，否则用 `service_{}.json`，其中服务名先经 `fs::sanitize_filename` 处理，路径前缀为 `client.cache_dir()`。 | `crates/wecom/src/registry/cache.rs:28-33` | `Get-Content crates/wecom/src/registry/cache.rs -TotalCount 33` |
| F-071 | 缓存写入调用 `fs.atomic_write(&cache_file, data.as_bytes(), Some(0o644))`，写入失败只记 `tracing::info` 而不返回错误。 | `crates/wecom/src/registry/cache.rs:57-64` | `Get-Content crates/wecom/src/registry/cache.rs | Select-Object -Skip 56 -First 9` |
| F-072 | discovery 请求载荷：给定服务名时为 `{"service": <name>}`，否则为 `{}`；目标端点为 `EndpointKey::ServiceDiscovery`。 | `crates/wecom/src/registry/cache.rs:87-107` | `Get-Content crates/wecom/src/registry/cache.rs | Select-Object -Skip 86 -First 22` |
| F-073 | `registry` 对外提供两个带缓存的入口：`get_or_fetch_catalog`（第 38 行）与 `get_or_fetch_detail`（第 56 行）。 | `crates/wecom/src/registry/mod.rs:38-56` | `Select-String -Path crates/wecom/src/registry/mod.rs -Pattern 'get_or_fetch'` |
| F-074 | 分页输出逻辑：`options.page_count.is_none()` 或 multipart 时不进入分页；进入后按 `(1..options.page_count.unwrap_or(1))` 循环，每页之间 `tokio::time::sleep(Duration::from_millis(options.page_delay_ms))`。 | `crates/wecom/src/service/execute.rs:197-238` | `Get-Content crates/wecom/src/service/execute.rs | Select-Object -Skip 196 -First 43` |
| F-075 | `write_page` 的职责为“有文件则追加写入，否则通过 `output.print()` 输出”，即分页模式与单页模式的输出分流点。 | `crates/wecom/src/service/execute.rs:319` | `Select-String -Path crates/wecom/src/service/execute.rs -Pattern 'fn write_page'` |

## 四、认证与会话

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-076 | `auth` 模块对外再导出 8 项：`auth_endpoint`、`BindSource`/`fetch_auth`/`resolve_auth_endpoint`、`try_migrate_legacy_credentials`、`QrSession`、`resolve_authorization`、`AuthSession`/`RefreshOutcome`、`load_credentials`/`save_credentials`、`Bot`/`ResolvedAuthorization`。 | `crates/wecom-cli/src/auth/mod.rs:34-41` | `Get-Content crates/wecom-cli/src/auth/mod.rs | Select-Object -Skip 33` |
| F-077 | 凭据路径函数把文件定位到 `default_home_dir().join("credentials.enc")`。 | `crates/wecom-cli/src/auth/store.rs:14-17` | `Get-Content crates/wecom-cli/src/auth/store.rs -TotalCount 17` |
| F-078 | 旧版凭据路径为 `[dir.join("bot.enc"), dir.join("token.enc")]`。 | `crates/wecom-cli/src/auth/store.rs:25-27` | `Get-Content crates/wecom-cli/src/auth/store.rs | Select-Object -Skip 24 -First 4` |
| F-079 | `save_credentials` 调用 `crypto::atomic_write(&credentials_path(), &encrypted, 0o600)`，权限位为 `0600`。 | `crates/wecom-cli/src/auth/store.rs:45-57` | `Get-Content crates/wecom-cli/src/auth/store.rs | Select-Object -Skip 44 -First 14` |
| F-080 | 加密算法为 `Aes256Gcm`，`NONCE_SIZE = 12`、`TAG_SIZE = 16`。 | `crates/wecom-cli/src/auth/crypto/cipher.rs:2-10` | `Get-Content crates/wecom-cli/src/auth/crypto/cipher.rs -TotalCount 10` |
| F-081 | 密文布局为 `nonce || ciphertext || tag`（12 + 明文长度 + 16 字节）；解密前若长度小于 `NONCE_SIZE + TAG_SIZE` 直接报错。 | `crates/wecom-cli/src/auth/crypto/cipher.rs:31-45`、`crates/wecom-cli/src/auth/crypto/cipher.rs:54-56` | `Get-Content crates/wecom-cli/src/auth/crypto/cipher.rs | Select-Object -Skip 30 -First 16` |
| F-082 | 加密密钥文件路径为 `default_home_dir().join(".encryption_key")`。 | `crates/wecom-cli/src/auth/crypto/keystore.rs:21-23` | `Get-Content crates/wecom-cli/src/auth/crypto/keystore.rs -TotalCount 23` |
| F-083 | keystore 保留 keyring 常量 `KEYRING_SERVICE = "wecom-cli"` 与 `KEYRING_USER_PREFIX = "encryption-key"`。 | `crates/wecom-cli/src/auth/crypto/keystore.rs:12-14` | `Get-Content crates/wecom-cli/src/auth/crypto/keystore.rs -TotalCount 14` |
| F-084 | `load_existing_key()` 的读取顺序为“先文件、后 keyring”：`load_key_from_file().or_else(load_key_from_keyring)`。 | `crates/wecom-cli/src/auth/crypto/keystore.rs:105-108` | `Get-Content crates/wecom-cli/src/auth/crypto/keystore.rs | Select-Object -Skip 104 -First 5` |
| F-085 | `save_key` 始终以 `0o600` 写文件兜底；`keyring_available()` 为真时再写 keyring，keyring 写入失败只记 `tracing::warn` 并返回 `Ok`。 | `crates/wecom-cli/src/auth/crypto/keystore.rs:110-130` | `Get-Content crates/wecom-cli/src/auth/crypto/keystore.rs | Select-Object -Skip 109 -First 22` |
| F-086 | 扫码轮询参数：`POLL_INTERVAL = 3s`、`POLL_TIMEOUT = 300s`。 | `crates/wecom-cli/src/auth/qrcode.rs:19-21` | `Get-Content crates/wecom-cli/src/auth/qrcode.rs | Select-Object -Skip 18 -First 4` |
| F-087 | 扫码相关三个 URL 常量：`QR_GENERATE_URL = https://work.weixin.qq.com/ai/qc/generate`、`QR_QUERY_URL = .../qc/query_result`、`QR_CODE_PAGE = .../qc/gen`。 | `crates/wecom-cli/src/auth/qrcode.rs:14-16` | `Get-Content crates/wecom-cli/src/auth/qrcode.rs -TotalCount 16` |
| F-088 | 鉴权引导签名为 `sha256_hex(secret + bot_id + time + nonce)`。 | `crates/wecom-cli/src/auth/bootstrap.rs:1-5` | `Get-Content crates/wecom-cli/src/auth/bootstrap.rs -TotalCount 5` |
| F-089 | 引导端点兜底值为 `https://qyapi.weixin.qq.com/cgi-bin/aibot/cli/get_cli_config`，解析优先级为运行时 env → `config.json` 的 `auth_endpoint` → 编译期 env → 常量。 | `crates/wecom-cli/src/auth/bootstrap.rs:22-29` | `Get-Content crates/wecom-cli/src/auth/bootstrap.rs | Select-Object -Skip 21 -First 9` |
| F-090 | 引导端点装配使用产品层 `FlatRes` 扁平信封并挂 `SuppressAuth`，即换取 token 的请求不携带 `Authorization` 头。 | `crates/wecom-cli/src/auth/bootstrap.rs:64-71` | `Get-Content crates/wecom-cli/src/auth/bootstrap.rs | Select-Object -Skip 63 -First 9` |
| F-091 | 授权材料解析优先级：`WECOM_CLI_ACCESS_TOKEN` 非空即返回 `ResolvedAuthorization::Env`，否则回退 `credentials.enc` 的 `Credentials`；文件仅有 bot 无 token 时 `token()` 为 `None`。 | `crates/wecom-cli/src/auth/resolve.rs:6-26` | `Get-Content crates/wecom-cli/src/auth/resolve.rs -TotalCount 26` |
| F-092 | 出网后端常量 `TOKEN_EXPIRED_ERRCODE: i64 = 853004`；`backend.rs` 以该常量与后台 `errcode` 比较。 | `crates/wecom-cli/src/transport/backend.rs:19` | `Select-String -Path crates/wecom-cli/src/transport/backend.rs -Pattern '853004'` |
| F-093 | 命中 853004 时，后端先记 `tracing::info!("token expired (853004), attempting silent refresh")`，再调用 `session.refresh(sent_token.as_deref(), &bootstrap_transport)` 并重放原请求；刷新失败则返回原始错误。 | `crates/wecom-cli/src/transport/backend.rs:125-158` | `Get-Content crates/wecom-cli/src/transport/backend.rs | Select-Object -Skip 124 -First 35` |
| F-094 | `env.rs` 定义 5 个环境变量常量：`CONFIG_DIR = "WECOM_CLI_CONFIG_DIR"`、`ADDITIONAL_HEADERS = "WECOM_CLI_ADDITIONAL_HEADERS"`、`ACCESS_TOKEN = "WECOM_CLI_ACCESS_TOKEN"`、`BASE_URL = "WECOM_CLI_BASE_URL"`、`AUTH_ENDPOINT = "WECOM_CLI_AUTH_ENDPOINT"`（后两者仅在 `custom-endpoint` 特性下编译）。 | `crates/wecom-cli/src/env.rs:10-25` | `Get-Content crates/wecom-cli/src/env.rs | Select-Object -Skip 9 -First 17` |
| F-095 | `default_home_dir()` 先取 `WECOM_CLI_CONFIG_DIR`（空值视为未设置），否则取 `dirs::home_dir()/.config/wecom`；配置文件路径为 `default_home_dir().join("config.json")`。 | `crates/wecom-cli/src/config.rs:47-66` | `Get-Content crates/wecom-cli/src/config.rs | Select-Object -Skip 46 -First 21` |
| F-096 | `auth init` 的 `--manual` 声明 `conflicts_with = "noninteractive"`；`--output-qrcode` 声明 `conflicts_with_all = ["manual", "bot_id"]`。 | `crates/wecom-cli/src/cmd/auth.rs:35-50` | `Get-Content crates/wecom-cli/src/cmd/auth.rs -TotalCount 50` |
| F-097 | `resolve_bind_mode(noninteractive, manual, is_tty)`：`noninteractive` 为真直接返回扫码模式（不受 TTY 影响）；`manual` 为真但非 TTY 时返回错误，文案要求改用 `--noninteractive`。 | `crates/wecom-cli/src/cmd/auth.rs:243-258` | `Get-Content crates/wecom-cli/src/cmd/auth.rs | Select-Object -Skip 242 -First 17` |
| F-098 | 手动输入模式下 `--output-qrcode` 被忽略，并记 `tracing::warn!("手动输入模式不输出二维码，--output-qrcode 已忽略")`。 | `crates/wecom-cli/src/cmd/auth.rs:159-164` | `Get-Content crates/wecom-cli/src/cmd/auth.rs | Select-Object -Skip 158 -First 7` |
| F-099 | `try_migrate_legacy_credentials` 位于 `legacy_migration.rs` 第 38 行；仅在无 `credentials.enc` 且存在 `bot.enc` 时读取旧 botid/secret 并走鉴权引导换取 token。 | `crates/wecom-cli/src/auth/legacy_migration.rs:1-48` | `Get-Content crates/wecom-cli/src/auth/legacy_migration.rs -TotalCount 48` |
| F-100 | `auth show --status` 按 `ResolvedAuthorization` 分支输出：`Env` 来源与有效凭据两条分支均为 `Status: authorized`，`None` 分支为 `Status: unauthorized`。 | `crates/wecom-cli/src/cmd/auth.rs:100-110` | `Get-Content crates/wecom-cli/src/cmd/auth.rs | Select-Object -Skip 99 -First 12` |

## 五、传输与韧性

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-101 | 传输层 3 个默认常量：`DEFAULT_MIN_POLL_INTERVAL_MS = 500`、`DEFAULT_POLL_TIMEOUT_SECS = 120`、`MAX_CONSECUTIVE_NETWORK_ERRORS = 3`。 | `crates/wecom-transport/src/common/constants.rs:1-8` | `Get-Content crates/wecom-transport/src/common/constants.rs` |
| F-102 | 长任务轮询元信息结构 `LongTaskPollInfo` 的字段为 `done`、`task_timeout`、`polling_interval_ms`。 | `crates/wecom-transport/src/polling.rs:12-16` | `Get-Content crates/wecom-transport/src/polling.rs -TotalCount 16` |
| F-103 | 轮询模式枚举 `PollMode` 的线格式为 `TaskQuery = 0`、`ReuseEndpoint = 1`；`TaskQuery` 对应 `POST /task/query` 且载荷为 `{method, payload}`。 | `crates/wecom-transport/src/polling.rs:27-37` | `Get-Content crates/wecom-transport/src/polling.rs | Select-Object -Skip 26 -First 12` |
| F-104 | 每轮轮询的休眠时长为 `task_info.polling_interval_ms`（缺省时取默认值），实现为 `tokio::time::sleep(Duration::from_millis(interval))`。 | `crates/wecom-transport/src/polling.rs:134-142` | `Get-Content crates/wecom-transport/src/polling.rs | Select-Object -Skip 133 -First 10` |
| F-105 | 超时判定：首次拿到 `task_timeout` 时记录起点，后续每轮比较 `elapsed >= t` 即返回 `Error::other` 超时错误。 | `crates/wecom-transport/src/polling.rs:113-131` | `Get-Content crates/wecom-transport/src/polling.rs | Select-Object -Skip 112 -First 20` |
| F-106 | `ApiResponse` 含 6 个字段：`result: Option<String>`、`error: Option<ApiErrorInfo>`、`taskid: Option<String>`、`poll_mode: Option<PollMode>`、`long_task_poll: Option<LongTaskPollInfo>`、以及 `#[serde(flatten)] extra: IndexMap<String, serde_json::Value>`。 | `crates/wecom-transport/src/http/protocol.rs:7-17` | `Get-Content crates/wecom-transport/src/http/protocol.rs -TotalCount 17` |
| F-107 | `ApiErrorInfo` 的字段为 `code: Option<i64>`、`message: Option<String>` 与 `#[serde(flatten)]` 的额外字段。 | `crates/wecom-transport/src/http/protocol.rs:19-24` | `Get-Content crates/wecom-transport/src/http/protocol.rs | Select-Object -Skip 18 -First 7` |
| F-108 | `ResponseEnvelope` trait 声明两个方法：`decode(&self, url: &str, body: Value) -> Result<ApiResponse>` 与 `name(&self) -> &'static str`。 | `crates/wecom-transport/src/http/envelope.rs:44-48` | `Get-Content crates/wecom-transport/src/http/envelope.rs | Select-Object -Skip 43 -First 6` |
| F-109 | 传输层自带两个信封实现：请求侧 `PassthroughReq`（`encode` 原样返回 payload）与响应侧 `GatewayRes`。 | `crates/wecom-transport/src/http/envelope.rs:29-36`、`crates/wecom-transport/src/http/envelope.rs:54-67` | `Get-Content crates/wecom-transport/src/http/envelope.rs -TotalCount 67` |
| F-110 | 断点续传常量：`MAX_RANGE_SEGMENTS = 4096`，单段上限 `MAX_RANGE_SIZE = 64 * 1024 * 1024`（64 MiB），`clamp_size` 把 schema 声明的段长夹到 `[1, MAX_RANGE_SIZE]`。 | `crates/wecom-transport/src/http/resumable.rs:33-45` | `Get-Content crates/wecom-transport/src/http/resumable.rs | Select-Object -Skip 32 -First 14` |
| F-111 | 续传流的三个终止信号：已知 `total` 且 `next >= total`、某段返回 0 字节、下一段返回 `416 Range Not Satisfiable`；短读（`seg_len < size`）不终止。 | `crates/wecom-transport/src/http/resumable.rs:15-23` | `Get-Content crates/wecom-transport/src/http/resumable.rs -TotalCount 23` |
| F-112 | `HttpRequest::timeout` 默认为 `None`（不设全局超时），只有业务显式 `.timeout(Duration)` 才写入请求；测试用例断言 `.timeout(30s)` 后 `get_timeout()` 为 `Some(30s)`。 | `crates/wecom-transport/src/http_client/request.rs:436-462` | `Get-Content crates/wecom-transport/src/http_client/request.rs | Select-Object -Skip 435 -First 28` |
| F-113 | 请求收尾函数 `finalize_request(builder, timeout)` 仅在 `Some(t)` 时调用 `builder.timeout(t)`，`None` 则不设置。 | `crates/wecom-transport/src/http_client/shared.rs:12-22` | `Get-Content crates/wecom-transport/src/http_client/shared.rs | Select-Object -Skip 11 -First 12` |
| F-114 | reqwest 发送实现把 `req.options.timeout` 透传给 `finalize_request`；未设 timeout 的慢请求正常完成。 | `crates/wecom-transport/src/http_client/reqwest_send.rs:62` | `Select-String -Path crates/wecom-transport/src/http_client/reqwest_send.rs -Pattern 'finalize_request'` |
| F-115 | `protocol::ApiResponse` 实现 `LongTaskPollData`，其 `poll_info()` 直接克隆 `self.long_task_poll`。 | `crates/wecom-transport/src/http/polling.rs:15-19` | `Get-Content crates/wecom-transport/src/http/polling.rs -TotalCount 19` |

## 六、沙箱、安全与遥测

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-116 | `main.rs` 注释写明双域沙箱构造规则：`PrivateFs` 的 roots 为 `[config_dir]`；`WorkspaceFs` 的 roots 为 `[cwd, 固定临时目录]`，并叠加配置目录 deny；roots 与 deny 只能在构造期注入，无 env/flag/config 扩展口。 | `crates/wecom-cli/src/main.rs:31-40` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 30 -First 11` |
| F-117 | 私有域由 `wecom::default_private_fs(&config_dir)` 构造，随后以该 fs 读取 `config.json`（`config::load_config_file`）。 | `crates/wecom-cli/src/main.rs:42-48` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 41 -First 8` |
| F-118 | 工作域 `allowed_roots` 初值为 `vec![fs_cwd.as_path()]`，当 `pinned_temp_dir()` 返回 `Some` 时追加该临时目录。 | `crates/wecom-cli/src/main.rs:54-58` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 53 -First 6` |
| F-119 | 工作域策略链为 `Policy::new().with_allowed_dirs(&allowed_roots).with_deny(wecom_fs::recommended_deny_rule()).with_deny(wecom_fs::DenyRule::prefix(&config_dir))`。 | `crates/wecom-cli/src/main.rs:59-64` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 58 -First 7` |
| F-120 | 内建 deny glob 表 `COMMON_DENY_GLOBS` 共 34 条，按注释分为凭据目录段、凭据/历史文件名、密钥证书扩展名、多段凭据库四组。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:32-71` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 31 -First 40` |
| F-121 | 目录段 7 条：`**/.ssh`、`**/.aws`、`**/.azure`、`**/.gnupg`、`**/.kube`、`**/.docker`、`**/.git`。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:34-40` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 33 -First 8` |
| F-122 | 凭据/历史文件名 16 条，含 `**/.env`、`**/.env.local`、`**/.env.production`、`**/.git-credentials`、`**/.netrc`、`**/.npmrc`、`**/id_rsa`、`**/id_ed25519`、`**/.bash_history` 等。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:42-57` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 41 -First 17` |
| F-123 | 密钥/证书扩展名 5 条：`**/*.pem`、`**/*.key`、`**/*.p12`、`**/*.pfx`、`**/*.jks`。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:58-63` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 57 -First 7` |
| F-124 | 多段凭据库 6 条：`**/.config/gh`、`**/.config/gcloud`、`**/.config/wecom`、`**/.gem/credentials`、`**/.cargo/credentials`、`**/.cargo/credentials.toml`。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:64-70` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 63 -First 8` |
| F-125 | Unix 系统目录 deny 表为 6 条前缀：`/etc`、`/proc`、`/sys`、`/dev`、`/root`、`/var/run`。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:75-76` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 74 -First 3` |
| F-126 | Windows deny 表含 4 个目录前缀（`C:\Windows`、`C:\ProgramData`、`C:\Program Files`、`C:\Program Files (x86)`）与 2 条 DPAPI 形状（`**/AppData/Roaming/Microsoft/Credentials`、`**/AppData/Local/Microsoft/Credentials`）。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:81-95` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 80 -First 16` |
| F-127 | 当 `SystemRoot` 环境变量值与字面量 `C:\Windows` 不相等时，`recommended_deny_rule` 追加一条 `DenyRule::prefix(sr)`。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:113-123` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 112 -First 12` |
| F-128 | `SandboxedFs::new` 的 denylist 默认为空，须调用方显式 `with_deny(recommended_deny_rule())`；deny 恒优先于 allow，即使 roots 为 `None`（不受限模式）仍生效。 | `crates/wecom-fs/src/sandbox/policy/denylist.rs:97-108` | `Get-Content crates/wecom-fs/src/sandbox/policy/denylist.rs | Select-Object -Skip 96 -First 13` |
| F-129 | `default_private_fs(config_dir: &Path) -> Arc<dyn crate::fs::Fs>` 定义在 `crates/wecom/src/client/builder.rs` 第 352 行。 | `crates/wecom/src/client/builder.rs:352` | `Select-String -Path crates/wecom/src/client/builder.rs -Pattern 'fn default_private_fs'` |
| F-130 | `default_workspace_fs(cwd: &Path) -> Arc<dyn crate::fs::Fs>` 定义在同文件第 372 行。 | `crates/wecom/src/client/builder.rs:372` | `Select-String -Path crates/wecom/src/client/builder.rs -Pattern 'fn default_workspace_fs'` |
| F-131 | `pinned_temp_dir()` 在 Unix 返回字面量 `"/tmp"`，在 Windows 返回 `dirs::data_local_dir().map(|d| d.join("Temp"))`，其他平台返回 `None`；刻意不用 `std::env::temp_dir()`。 | `crates/wecom-cli/src/config.rs:221-238` | `Get-Content crates/wecom-cli/src/config.rs | Select-Object -Skip 220 -First 19` |
| F-132 | trace 头常量 `TRACE_HEADER = "x-wecom-trace"`，其值为 `base64("#chain={chain}#id={id}#")`，`MAX_CHAIN_LEN = 512`。 | `crates/wecom-cli/src/trace/mod.rs:7-17` | `Get-Content crates/wecom-cli/src/trace/mod.rs -TotalCount 17` |
| F-133 | `call-chain` 特性开启时，`main` 把 `build_trace_header_value()` 结果写入 transport 的 `x-wecom-trace` 头；头值不是合法 `HeaderValue` 时跳过注入。 | `crates/wecom-cli/src/main.rs:68-80` | `Get-Content crates/wecom-cli/src/main.rs | Select-Object -Skip 67 -First 14` |
| F-134 | 日志子系统读取 3 个环境变量/编译期量：`WECOM_CLI_LOG_LEVEL`（stderr 过滤）、`WECOM_CLI_LOG_DIR`（日志目录）、`WECOM_CLI_DEFAULT_LOG_DIR`（编译期默认目录）。 | `crates/wecom-cli/src/logging.rs:12-19` | `Get-Content crates/wecom-cli/src/logging.rs -TotalCount 19` |
| F-135 | `telemetry` 模块只订阅 `json_repair` 事件中的 `outcome == "ok_repaired"` 一种情形，命中后向 stderr 打印 `JSON_REPAIR_HINT`。 | `crates/wecom-cli/src/telemetry.rs:10-38` | `Get-Content crates/wecom-cli/src/telemetry.rs -TotalCount 38` |
| F-136 | 文档写明 trace 调用链头默认开启且不提供开关，`--doc` 与 `--schema` 不发送网络请求。 | `docs/data-collection.md:12-18` | `Get-Content docs/data-collection.md | Select-Object -Skip 11 -First 8` |

## 七、Skills 层

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-137 | `skills/` 下共 15 个目录：`wecomcli-calendar`、`wecomcli-contact`、`wecomcli-disk`、`wecomcli-doc`、`wecomcli-doc-manage`、`wecomcli-email`、`wecomcli-media`、`wecomcli-meeting`、`wecomcli-message`、`wecomcli-pptx`、`wecomcli-shared`、`wecomcli-sheet`、`wecomcli-smartpage`、`wecomcli-smartsheet`、`wecomcli-todo`。 | `skills/:1-1` | `Get-ChildItem skills -Directory | Measure-Object` |
| F-138 | `wecomcli-shared/SKILL.md` 的 frontmatter 只有 `name` 与 `description` 两个键，不含 `metadata`。 | `skills/wecomcli-shared/SKILL.md:1-4` | `Get-Content skills/wecomcli-shared/SKILL.md -TotalCount 4` |
| F-139 | 其余 14 个 `SKILL.md` 的 frontmatter 均含 `metadata.requires.bins: ["wecom-cli"]`，例如 `wecomcli-contact` 在第 4-6 行、`wecomcli-disk` 在第 5-7 行。 | `skills/wecomcli-contact/SKILL.md:4-6`、`skills/wecomcli-disk/SKILL.md:5-7` | `Select-String -Path skills/*/SKILL.md -Pattern 'bins'` |
| F-140 | `wecomcli-shared` 的 `description` 写明版本检查下限为“不低于 1.2.1”，并要求任何 `wecomcli-*` 技能首次执行前同时读取该技能。 | `skills/wecomcli-shared/SKILL.md:3` | `Get-Content skills/wecomcli-shared/SKILL.md | Select-Object -Skip 2 -First 1` |
| F-141 | `wecomcli-calendar` 目录共 8 个文件，其中 `references/` 7 个、`scripts/` 0 个。 | `skills/wecomcli-calendar/SKILL.md:1-8` | `Get-ChildItem skills/wecomcli-calendar -File -Recurse | Measure-Object` |
| F-142 | `wecomcli-email` 目录共 8 个文件，其中 `references/` 7 个、`scripts/` 0 个。 | `skills/wecomcli-email/SKILL.md:1-8` | `Get-ChildItem skills/wecomcli-email -File -Recurse | Measure-Object` |
| F-143 | `wecomcli-meeting` 目录共 7 个文件，其中 `references/` 6 个；`wecomcli-todo` 同为 7 个文件、6 个 references。 | `skills/wecomcli-meeting/SKILL.md:1-7`、`skills/wecomcli-todo/SKILL.md:1-7` | `Get-ChildItem skills/wecomcli-meeting,skills/wecomcli-todo -File -Recurse | Measure-Object` |
| F-144 | `wecomcli-sheet` 目录共 20 个文件：`references/` 17 个、`scripts/` 2 个、`SKILL.md` 1 个。 | `skills/wecomcli-sheet/SKILL.md:1-20` | `Get-ChildItem skills/wecomcli-sheet -File -Recurse | Measure-Object` |
| F-145 | `wecomcli-pptx` 目录共 84 个文件，其中 `references/` 27 个、`scripts/` 3 个，references 下另有 `templates/` 模板目录。 | `skills/wecomcli-pptx/SKILL.md:1-84` | `Get-ChildItem skills/wecomcli-pptx -Recurse -File | Measure-Object` |
| F-146 | `wecomcli-smartpage` 目录共 14 个文件，`references/` 13 个（顶层 4 个 md，`references/formula/` 9 个 md）。 | `skills/wecomcli-smartpage/SKILL.md:1-14` | `Get-ChildItem skills/wecomcli-smartpage/references -File -Recurse | Measure-Object` |
| F-147 | `wecomcli-smartsheet` 目录共 32 个文件，其中 `references/` 10 个，另含 `assets/templates/` 下的模板文件。 | `skills/wecomcli-smartsheet/SKILL.md:1-32` | `Get-ChildItem skills/wecomcli-smartsheet -File -Recurse | Measure-Object` |
| F-148 | `wecomcli-doc` 目录共 5 个文件（`references/` 3 个、`scripts/` 1 个）；`wecomcli-doc-manage` 共 4 个文件（`references/` 3 个）。 | `skills/wecomcli-doc/SKILL.md:1-5`、`skills/wecomcli-doc-manage/SKILL.md:1-4` | `Get-ChildItem skills/wecomcli-doc,skills/wecomcli-doc-manage -File -Recurse | Measure-Object` |
| F-149 | 5 个技能没有 `references/` 目录，整目录只有 `SKILL.md` 一个文件：`wecomcli-contact`、`wecomcli-disk`、`wecomcli-media`、`wecomcli-message`、`wecomcli-shared`。 | `skills/wecomcli-contact/SKILL.md:1-1` | `Get-ChildItem skills/*/references -Directory -ErrorAction SilentlyContinue | Measure-Object` |
| F-150 | `docs/skills.md` 的导航表列出 15 行 Skill，行序从 `wecomcli-shared`（公共前置检查）到 `wecomcli-pptx`（在线 PPT 演示文稿）。 | `docs/skills.md:9-25` | `Get-Content docs/skills.md | Select-Object -Skip 8 -First 18` |
| F-151 | 口径差异（同一基线的并置登记）：`AGENTS.md` 第 33 行把 `skills/*` 记作“内置 Agent Skills（14 个，导航见 `docs/skills.md`）”。 | `AGENTS.md:33` | `Get-Content AGENTS.md | Select-Object -Skip 32 -First 1` |
| F-152 | 口径差异（同一基线的并置登记）：`docs/skills.md` 第 7 行写“当前共内置 15 个 Agent Skills”，同文件表格亦为 15 行；`skills/` 实际目录数为 15。 | `docs/skills.md:7`、`docs/skills.md:9-25` | `Get-Content docs/skills.md -TotalCount 7` |
| F-153 | `wecomcli-shared` 正文第 8 行写明“首次准备执行任意 `wecom-cli` 命令前，先完成本技能”，第 10 行写明不能代替业务技能。 | `skills/wecomcli-shared/SKILL.md:8-10` | `Get-Content skills/wecomcli-shared/SKILL.md | Select-Object -Skip 7 -First 4` |
| F-154 | `AGENTS.md` 的仓库结构表把 `skills/*` 归入内置 Agent Skills，并指向 `docs/skills.md` 作为导航入口。 | `AGENTS.md:33`、`docs/skills.md:1-3` | `Get-Content docs/skills.md -TotalCount 3` |

## 八、文档与测试

| 编号 | 事实陈述 | 证据位置 | 取证命令 |
|---|---|---|---|
| F-155 | `docs/` 下共 9 个 Markdown 文件：顶层 5 个（`README.md`、`cli-reference.md`、`skills.md`、`data-collection.md`、`development.md`），`docs/e2e/` 下 4 个（`FRAMEWORK.md`、`DESC_SPEC.md`、`DESC_SPEC_HUMAN.md`、`CODEGEN.md`）。 | `docs/README.md:7-11` | `Get-ChildItem docs -Recurse -File \| Select-Object -ExpandProperty Name` |
| F-156 | `docs/README.md` 的「从这里开始」节列出 4 条主题入口（cli-reference、skills、data-collection、development）与 1 条 e2e 入口（同列 FRAMEWORK、DESC_SPEC、CODEGEN、DESC_SPEC_HUMAN 四篇）。 | `docs/README.md:1-11` | `Get-Content docs/README.md -TotalCount 11` |
| F-157 | `docs/README.md` 第 15 行的清单项以「优先把持续维护的…写进 `docs/`」开头，第 16 行的清单项为「同一主题只保留一个主入口，其他页面通过链接复用」。 | `docs/README.md:13-16` | `Get-Content docs/README.md \| Select-Object -Skip 12 -First 4` |
| F-158 | `docs/e2e/FRAMEWORK.md` 首行为「# e2e 测试框架方案」，第 295-304 行给出 4 条 `cargo test` 示例（library-level 全套件、带 `custom-endpoint` 特性、process-level 全套件、单用例 `run::method_call`）。 | `docs/e2e/FRAMEWORK.md:1`、`docs/e2e/FRAMEWORK.md:295-304` | `Get-Content docs/e2e/FRAMEWORK.md \| Select-Object -Skip 294 -First 11` |
| F-159 | `docs/e2e/CODEGEN.md` 首行为「# 根据 desc.md 生成 e2e 测试代码 — 操作手册」。 | `docs/e2e/CODEGEN.md:1` | `Get-Content docs/e2e/CODEGEN.md -TotalCount 1` |
| F-160 | `docs/e2e/DESC_SPEC.md` 首行为「# desc.md 规范标准」，第 16 行给出 `desc.md` 模板首行 `# <标题>`。 | `docs/e2e/DESC_SPEC.md:1`、`docs/e2e/DESC_SPEC.md:16` | `Get-Content docs/e2e/DESC_SPEC.md -TotalCount 16` |
| F-161 | `docs/e2e/DESC_SPEC_HUMAN.md` 首行为「# desc.md 速写指南」。 | `docs/e2e/DESC_SPEC_HUMAN.md:1` | `Get-Content docs/e2e/DESC_SPEC_HUMAN.md -TotalCount 1` |
| F-162 | 根 `README.md` 的「前置条件」节第 36 行写 `Node.js >= 18`；「安装 & 使用」节第 44 行为 `npm install -g @wecom/cli`，第 47 行为 `npx skills add WeComTeam/wecom-cli -y -g`。 | `README.md:33-47` | `Get-Content README.md \| Select-Object -Skip 32 -First 16` |
| F-163 | 根 `README.md` 的「许可证」节第 68 行写「本项目基于 `[MIT 许可证](./LICENSE)` 开源」。 | `README.md:66-68` | `Get-Content README.md \| Select-Object -Skip 65 -First 3` |
| F-164 | `docs/development.md` 第 7 行写「本仓库为 Cargo workspace，Rust 核心拆为三个 crate」，其后的结构表只列 `crates/wecom/`、`crates/wecom-cli/`、`crates/wecom-transport/` 三行 crate。 | `docs/development.md:7-13` | `Get-Content docs/development.md \| Select-Object -Skip 6 -First 7` |
| F-165 | 口径差异（同一基线的并置登记）：根 `Cargo.toml` 的 `members` 列 5 个 crate——`crates/wecom`、`crates/wecom-cli`、`crates/wecom-transport`、`crates/wecom-fs`、`crates/wecom-error`。 | `Cargo.toml:3-9` | `Get-Content Cargo.toml -TotalCount 9` |
| F-166 | `docs/development.md` 第 46 行记 e2e 套件位于各 crate 的 `<crate>/test-e2e/`，结构为 `run.rs` 编译入口 + `helpers/` + `cases/<group>/<NNN>-<slug>/{desc.md,test.rs}`。 | `docs/development.md:44-52` | `Get-Content docs/development.md \| Select-Object -Skip 43 -First 9` |
| F-167 | 每个 e2e 用例目录含 `desc.md` 与 `test.rs` 两个文件，例如 `crates/wecom/test-e2e/cases/cache/001-status/` 下即这两文件。 | `crates/wecom/test-e2e/cases/cache/001-status/desc.md:1`、`crates/wecom/test-e2e/cases/cache/001-status/test.rs:1` | `Get-ChildItem crates/wecom/test-e2e/cases/cache/001-status -File` |
| F-168 | `crates/wecom/test-e2e/cases/` 下分 9 个分组（`cache`、`client`、`directive`、`error`、`headers`、`output`、`pagination`、`run`、`schema`），共 56 个编号用例目录；`crates/wecom-cli/test-e2e/cases/` 下分 6 个分组（`auth`、`config`、`logging`、`repair`、`sandbox_paths`、`startup`），共 19 个编号用例目录。 | `crates/wecom/test-e2e/run.rs:1`、`crates/wecom-cli/test-e2e/run.rs:1` | `Get-ChildItem crates/wecom/test-e2e/cases -Directory -Recurse \| Where-Object Name -match '^\d{3}-' \| Measure-Object` |
| F-169 | `crates/wecom-cli/test-e2e/cases/sandbox_paths/` 下共 12 个用例目录（`001` 至 `012`），目录名含 `symlink-escape`、`hardlink-alias-threat-model`、`dotdot-escape`、`config-dir-under-cwd-denied` 等。 | `crates/wecom-cli/test-e2e/cases/sandbox_paths/003-symlink-escape/desc.md:1` | `Get-ChildItem crates/wecom-cli/test-e2e/cases/sandbox_paths -Directory` |
| F-170 | 仓库根下无 `tests/` 目录（`Test-Path tests` 返回 `False`）；单元测试以 `#[cfg(test)]` 模块内嵌在源码中，crates 下含该属性的 `.rs` 文件共 105 个，例如 `crates/wecom/src/client/builder.rs` 第 264 行与第 382 行各有一个。 | `crates/wecom/src/client/builder.rs:264`、`crates/wecom/src/client/builder.rs:382` | `Select-String -Path crates/wecom/src/client/builder.rs -Pattern '#\[cfg\(test\)\]'` |
| F-171 | `docs/cli-reference.md` 的节顺序为：命令模型（第 5 行）、配置凭证 `auth`（21）、查看帮助 `--help`（55）、调用工具（77）、内建命令（120）、运行时路径（131）、环境变量（141）、配置文件 `config.json`（151）、退出码与错误格式（170）。 | `docs/cli-reference.md:5-170` | `Select-String -Path docs/cli-reference.md -Pattern '^##'` |
| F-172 | `docs/cli-reference.md` 的运行时路径表 5 行（配置目录、凭据文件、加密密钥、discovery 缓存、下载目录）；环境变量表 5 行（`WECOM_CLI_CONFIG_DIR`、`WECOM_CLI_ACCESS_TOKEN`、`WECOM_CLI_ADDITIONAL_HEADERS`、`WECOM_CLI_LOG_LEVEL`、`WECOM_CLI_LOG_DIR`）；退出码表 3 行（`0` 成功、`1` 运行时错误、`2` 用法错误）。 | `docs/cli-reference.md:133-149`、`docs/cli-reference.md:172-176` | `Get-Content docs/cli-reference.md \| Select-Object -Skip 132 -First 17` |

## 统计

| 项目 | 数值 | 备注 |
|---|---|---|
| 事实条数 | 172 | 编号 F-001 至 F-172，连续无跳号、无重复 |
| 主题节数 | 8 | 仓库与构建、命令模型、5 个 crate、认证与会话、传输与韧性、沙箱安全与遥测、Skills 层、文档与测试 |
| 覆盖 crate 数 | 5 | `wecom`、`wecom-cli`、`wecom-transport`、`wecom-fs`、`wecom-error` |
| 基线 | `1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde` | npm `@wecom/cli` 1.3.4 |
| 口径差异条目 | 2 组 | F-151/F-152（Skill 计数 14 vs 15）、F-164/F-165（crate 计数 3 vs 5） |