---
type: Reference
title: cargo 源码信源登记
description: rust-lang/cargo master @ 75d17360 源码坐标、版本基线、文档资产、测试与基准布局及旧名迁移对照清单
tags: [rust, cargo, source, reference]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: external/libs/rust-lang/cargo
    title: rust-lang/cargo 仓库（master @ 75d17360）
---

# cargo 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | cargo |
| 基线 | **master @ 75d17360928f57ff2a7d2f2da1c753f5fe1926d1**（2026-08-26 采集） |
| 包版本（Cargo.toml） | `0.101.0`（F-cargo-003） |
| CLI 显示版本 | `1.100.0`（F-cargo-144，版本双轨制） |
| 描述 | "Cargo, a package manager for Rust."（F-cargo-003） |
| 许可证 | `MIT OR Apache-2.0`（F-cargo-002） |
| MSRV | workspace `1.95` / 主 crate `1.98`（F-cargo-002/003） |
| 源码仓库 | <https://github.com/rust-lang/cargo> |
| 本地路径 | `external/libs/rust-lang/cargo/` |

## ⚠️ 结构基线声明（阅读本 bundle 前必读）

此基线（master @ 75d17360）的 cargo 主 crate 源码已经历一次结构性重组，与网络上绝大多数旧版源码导读的坐标不同：

| 旧文档通行说法 | 本基线实际坐标 | 依据 |
|----------------|----------------|------|
| 主源码位于 `src/cargo/` | 主源码位于 `src/`（`src/lib.rs` + 八大模块目录） | F-cargo-010 |
| 配置类型为 `Config` | 已更名 `GlobalContext`（定义于 `src/context/mod.rs`） | F-cargo-043 |
| `SourceId`/`PackageId` 位于独立的 id 模块 | 位于 `src/workspace/` 模块（`source_id.rs`/`package_id.rs`） | F-cargo-083/085 |
| 根 Cargo.toml 仅为 workspace 或仅为 package | 根 Cargo.toml 同时声明 `[workspace]` 与 `[package]`（双职合一） | F-cargo-001/003 |

**使用旧版 cargo 源码资料时只取架构思想，不取路径坐标。**

## 主 crate 源码坐标

| 路径 | 内容 | 详见 |
|------|------|------|
| `src/lib.rs` | 主 crate 入口：模块声明、re-exports、组件职责文档 | F-cargo-033~040 |
| `src/bin/cargo/main.rs` | CLI 进程入口：`main()`、`setup_logger()`、别名表 | F-cargo-014~020 |
| `src/bin/cargo/cli.rs` | clap 命令构造与 `cli::main()` 分发序 | F-cargo-021~025、031~032 |
| `src/bin/cargo/commands/` | 39 个 builtin 子命令的薄壳模块 | F-cargo-026~027 |
| `src/context/` | `GlobalContext` 配置子系统（两层反序列化） | F-cargo-041~050 |
| `src/ops/` | 命令业务核心（"Every major operation is implemented here"） | F-cargo-051~061 |
| `src/resolver/` | 依赖解析核心算法与 `Resolve` 图 | F-cargo-062~067 |
| `src/sources/` | 五种 `Source` 实现与 registry 协议 | F-cargo-068~076 |
| `src/compiler/` | 编译调度（`BuildRunner` 世界中心） | F-cargo-106~112 |
| `src/workspace/` | Manifest 解析、Package/Workspace 模型、`PackageId`/`SourceId` | F-cargo-077~088 |
| `src/util/` | 42 个基础设施工具模块 | F-cargo-089~105 |
| `src/version.rs` | 版本双轨推导链 | F-cargo-040、144 |
| `crates/` | 19 个子 crate（cargo-platform、cargo-util 等） | F-cargo-011、113~122 |
| `credential/` | 5 个 credential crate（1password/libsecret 等） | F-cargo-123 |

## 文档资产

### doc/man/ — 37 个手册文件（F-cargo-131）

`doc/man/` 含 37 个 `.md` 手册：`cargo.md` 以及 cargo-add / bench / build / check / clean / doc / fetch / fix / generate-lockfile / help / info / init / install / locate-project / login / logout / metadata / new / owner / package / pkgid / publish / remove / report / report-future-incompatibilities / run / rustc / rustdoc / search / test / tree / uninstall / update / vendor / version / yank 各命令一个 `.md`。另有 `includes/` 目录，收录 13 个共享片段（options-display / index / jobs / locked / new / profile / registry / release / targets / test / timings / token.md 与 section-features.md）。

### doc/book/src/ — Cargo Book 四大部分（F-cargo-132/133）

`doc/book/src/SUMMARY.md` 定义四大部分：

1. **Getting Started**：installation、first-steps
2. **Cargo Guide**（11 小节）：含 why-cargo-exists、cargo-toml-vs-cargo-lock、build-performance
3. **Cargo Reference**：manifest / workspaces / dependencies / features / profiles / config / environment-variables / build-scripts / build-cache / pkgid-spec / external-tools / registries（下含 registry-authentication → credential-provider-protocol、running-a-registry → registry-index + registry-web-api）/ semver / future-incompat-report / timings / lints / unstable
4. **Cargo Commands**：general / build / manifest / package / misc 分组

`doc/book/src/` 下的子目录：appendix（glossary.md）、commands（cargo-fmt.md、cargo-miri.md、index.md）、getting-started、guide、images、reference。

### doc/contrib/ — 贡献者指南（F-cargo-134）

`doc/contrib/`（book.toml 独立）的 src 含：process/{index, llm-usage, release, rfc, security, unstable}.md、tests/{crater, index, profiling, running, writing}.md、design.md、issues.md、team.md。

## 测试与基准

### tests/ — testsuite 120+ 测试模块（F-cargo-140）

- `tests/testsuite/`：集成测试套件；`testsuite/main.rs` 以 `mod` 声明 120+ 测试模块
- `tests/build-std/main.rs`：build-std 独立测试入口
- 前 120 行已声明的模块包括：advanced_env、alt_registry、artifact_dep、artifact_dir、bad_config、bad_manifest_path、bench、binary_name、build、build_analysis、build_dir、build_dir_fine_grain_locking、build_dir_legacy、build_script、build_script_env、build_script_extra_link_arg、build_scripts_multiple、cache_lock、cache_messages、cargo、cargo_add、cargo_alias_config、cargo_bench、cargo_build、cargo_check、cargo_clean、cargo_command、cargo_config、cargo_doc、cargo_env_config、cargo_features、cargo_fetch、cargo_fix、cargo_generate_lockfile、cargo_git_checkout、cargo_help、cargo_info、cargo_init、cargo_install、cargo_locate_project、cargo_login、cargo_logout、cargo_metadata、cargo_new、cargo_owner、cargo_package、cargo_pkgid、cargo_publish、cargo_read_manifest、cargo_remove、cargo_report、cargo_report_future_incompat、cargo_report_rebuilds、cargo_report_sessions、cargo_report_timings、cargo_run、cargo_rustc、cargo_rustdoc、cargo_search、cargo_targets、cargo_test、cargo_tree、cargo_uninstall、cargo_update、cargo_vendor、cargo_verify_project、cargo_version、cargo_yank、cfg、check、check_cfg、clean、clean_legacy_layout、collisions、compile_time_deps、concurrent、config、config_cli、config_include、corrupt_git、credential_process、cross_compile、cross_publish、custom_target、death、dep_info、diagnostics、direct_minimal_versions、directory、doc、docscrape、edition、error、feature_unification、features、features2、features_namespaced、fetch、fix、fix_n_times、freshness、freshness_checksum、freshness_mtime、future_incompat_report、generate_lockfile、git、git_auth、git_gc、git_shallow、glob_targets、global_cache_tracker、help、hint_msrv、hints、https、inheritable_workspace_fields、install、install_upgrade、jobserver、lints 等

### benches/ — 三类基准（F-cargo-141/142）

- 布局：`benchsuite/`（Cargo.toml + src/lib.rs）、`capture/`（src/main.rs）、`workspaces/`（9 个 .tgz 样本：cargo、diem、empty、gecko-dev、rust、servo、substrate、tikv、toml-rs）
- `benches/README.md` 原文："This uses [Criterion] for running benchmarks"，三类基准：
  - **global_cache_tracker** — 向全局缓存跟踪数据库写入数据的基准
  - **resolve** — 以真实 workspace 模拟为输入的 resolver 基准
  - **workspace_initialization** — workspace 初始化基准

## 构建与 CI 坐标（F-cargo-135~138、143）

- `build.rs`：`fn main()` 调用 `commit_info()`、`compress_man()`、`windows_manifest()` 三个函数，并输出 `cargo:rustc-env=RUST_HOST_TARGET={target}`（F-cargo-135）
- `.cargo/config.toml`：`[alias]` 段定义 5 个 xtask 别名（build-man、stale-label、bump-check、lint-docs、spellcheck，均形如 `run --package xtask-* --`）；`[env]` 段设置 `CARGO_RUSTC_CURRENT_DIR = { value = "", relative = true }`（F-cargo-139）
- `.github/workflows/`：audit.yml、contrib.yml、main.yml、release.yml
- `ci/`：generate.py、validate-man.sh、validate-version-bump.sh、fetch-smoke-test.sh 等
- `etc/`：cargo.bashcomp.sh 与 _cargo（补全脚本）
- 仓库根另有：`publish.py`、`clippy.toml`、`deny.toml`、`rustfmt.toml`、`LICENSE-APACHE`、`LICENSE-MIT`、`LICENSE-THIRD-PARTY`、`.git-blame-ignore-revs`、`CODE_OF_CONDUCT.md`、`CONTRIBUTING.md`（F-cargo-013）
- `CHANGELOG.md` 全文仅一行："The changelog has moved to the [Cargo Book](https://doc.rust-lang.org/nightly/cargo/CHANGELOG.html)."（F-cargo-012）

## 事实编号索引

本篇为主覆盖（信源坐标类事实的登记工位）：

| 区间 | 内容 |
|------|------|
| F-cargo-131 | doc/man 37 个手册与 includes/ 片段 |
| F-cargo-132 | doc/book/src/SUMMARY.md 四大部分 |
| F-cargo-133 | doc/book/src/ 子目录 |
| F-cargo-134 | doc/contrib 贡献者指南 |
| F-cargo-139 | .cargo/config.toml xtask 别名与环境 |
| F-cargo-140 | tests/testsuite 120+ 测试模块 |
| F-cargo-141 | benches/ 布局 |
| F-cargo-142 | benches/README.md 三类基准 |
| F-cargo-143 | CI/workflow/补全脚本 |

## 相关概念

- [简介与架构总览](/concepts/00-intro-architecture-overview.md) — 主 crate 组件地图与版本双轨制
- [Crate 组织与 CLI 分发](/concepts/01-crate-organization-cli-dispatch.md) — src/bin/cargo/ 入口链与 19+5 个子 crate
- [util 基础设施](/concepts/09-util-infrastructure.md) — build.rs 注入链（F-cargo-135~138）的展开
