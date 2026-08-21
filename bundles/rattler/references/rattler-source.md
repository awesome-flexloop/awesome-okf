---
type: "reference"
title: "Rattler 源码结构参考"
sources:
  - id: rattler-repo
    resource: https://github.com/conda/rattler
    title: "conda/rattler GitHub Repository"
---

# Rattler 源码结构参考

本文档记录 Rattler 仓库的目录结构与核心 crate 布局，作为其他概念文档的信源索引。

## 仓库根目录

```
rattler/
├── crates/              # 所有 Rust crates（核心库）
├── py-rattler/          # Python 绑定（PyO3）
├── js-rattler/          # JavaScript/WASM 绑定
├── tools/               # 辅助工具（libsolv 绑定生成等）
├── test-data/           # 测试数据（外部 git submodule）
├── assets/              # README 图片等静态资源
├── .github/             # CI/CD 工作流
├── Cargo.toml           # workspace 根配置
├── Cargo.lock           # 依赖锁定
├── pixi.toml            # pixi 开发环境配置
├── pixi.lock            # pixi 环境锁定
├── README.md            # 项目说明
├── LICENSE              # BSD-3-Clause
├── CHANGELOG.md         # 变更日志
└── AGENTS.md            # AI 协作入口
```

## Crates 目录（crates/）

Rattler 是一个 Rust workspace，包含约 30 个 crate。以下按分层架构排列：

### 基础类型层

| Crate | 路径 | 职责 |
|-------|------|------|
| `rattler_conda_types` | `crates/rattler_conda_types/` | Conda 生态核心数据模型：Version、Platform、MatchSpec、Channel、PackageRecord、RepoData 等 |
| `rattler_digest` | `crates/rattler_digest/` | 哈希算法封装（MD5、SHA256），支持 serde 和 tokio |
| `rattler_redaction` | `crates/rattler_redaction/` | 敏感信息脱敏（URL 中的 token 等） |
| `rattler_macros` | `crates/rattler_macros/` | 过程宏（sorted enum/struct 派生） |
| `rattler_config` | `crates/rattler_config/` | 配置文件解析（.condarc 兼容，含 S3/TLS/代理/并发配置） |
| `coalesced_map` | `crates/coalesced_map/` | 合并映射数据结构 |
| `file_url` | `crates/file_url/` | file:// URL 处理 |
| `path_resolver` | `crates/path_resolver/` | 路径解析工具 |
| `simple_spawn_blocking` | `crates/simple_spawn_blocking/` | tokio spawn_blocking 封装与取消支持 |

### 网络与 I/O 层

| Crate | 路径 | 职责 |
|-------|------|------|
| `rattler_networking` | `crates/rattler_networking/` | 网络中间件：认证（OAuth）、镜像、重试策略、S3/GCS/OCI 中间件、代理 |
| `rattler_repodata_gateway` | `crates/rattler_repodata_gateway/` | Repodata 下载、缓存、分片（sharded repodata）、Gateway 高级 API |
| `rattler_package_streaming` | `crates/rattler_package_streaming/` | Conda 包归档（.conda/.tar.bz2）的下载、解压、读取、写入 |
| `rattler_cache` | `crates/rattler_cache/` | 包缓存管理（package-cache），含校验验证 |
| `rattler_git` | `crates/rattler_git/` | Git 源处理（凭证、resolver、SHA、LFS） |
| `rattler_s3` | `crates/rattler_s3/` | S3 存储支持（clap 集成） |

### 核心逻辑层

| Crate | 路径 | 职责 |
|-------|------|------|
| `rattler_solve` | `crates/rattler_solve/` | 依赖求解Trait（SolverImpl），后端：libsolv_c（C FFI）、resolvo（Rust 原生） |
| `rattler_virtual_packages` | `crates/rattler_virtual_packages/` | 虚拟包检测：__linux/__osx/__win/__glibc/__cuda/__archspec 等 |
| `rattler_shell` | `crates/rattler_shell/` | 环境激活脚本生成、在环境中执行命令 |
| `rattler_lock` | `crates/rattler_lock/` | Conda lockfile 解析与生成（v3/v5/v6/v7 多版本格式） |
| `rattler_index` | `crates/rattler_index/` | 本地 conda channel 索引创建 |
| `rattler_menuinst` | `crates/rattler_menuinst/` | 跨平台菜单/快捷方式安装（Windows/macOS/Linux） |
| `rattler_pty` | `crates/rattler_pty/` | 伪终端（PTY）支持（Unix） |
| `rattler_prefix_guard` | `crates/rattler_prefix_guard/` | 环境前缀并发访问守卫 |
| `rattler_upload` | `crates/rattler_upload/` | 包上传（Anaconda/Cloudsmith/conda-forge/S3/OCI attestation） |
| `rattler_sandbox` | `crates/rattler_sandbox/` | 沙箱执行环境 |
| `rattler_libsolv_c` | `crates/rattler_libsolv_c/` | libsolv C 库的 Rust FFI 绑定 |

### 高层集成层

| Crate | 路径 | 职责 |
|-------|------|------|
| `rattler` | `crates/rattler/` | 高层 API：整合所有 crate 提供"从零创建环境"功能，含 install 模块（link/unlink/transaction/entry_point/python/apple_codesign）和 cli 模块 |
| `rattler-bin` | `crates/rattler-bin/` | CLI 二进制示例（`rattler` 命令），展示所有 crate 的使用 |

## Python 绑定（py-rattler/）

```
py-rattler/
├── src/              # PyO3 Rust 绑定源码
├── docs/             # Python 文档（Markdown，含 Sphinx 构建）
├── build.rs          # 构建脚本
├── Cargo.toml        # 绑定 crate 配置
└── README.md
```

Python 绑定提供异步API（基于 asyncio），主要模块包括：`solve()`、`install()`、`Gateway`、`VirtualPackage`、`Channel`、`MatchSpec`、`Version`、`Platform`、`PackageRecord` 等。

## JavaScript/WASM 绑定（js-rattler/）

```
js-rattler/
├── src/              # TypeScript 源码
├── crate/            # Rust WASM crate（wasm-bindgen）
├── e2e/              # 端到端测试
├── package.json      # npm 包配置
├── rollup.config.*   # Rollup 打包配置
└── tsconfig.json     # TypeScript 配置
```

JS 包名为 `@conda-org/rattler`，编译为 WebAssembly，支持浏览器和 Node.js。

## 开发命令

参考 `AGENTS.md`：

```bash
pixi run build       # 构建所有 crates
pixi run test        # 运行所有测试
pixi run lint        # 运行所有 lint 检查
pixi run cargo-fmt   # 格式化代码
pixi run cargo-clippy # Clippy 检查
pixi run -- cargo nextest run -p <crate_name> <test_name>  # 单个测试
```

`rattler-bin` 提供的 CLI 示例命令：

```bash
cargo run --bin rattler --release create <package>   # 创建环境并安装包
cargo run --bin rattler --release run -p <prefix> <command>  # 在环境中运行命令
cargo run --bin rattler --release solve <specs>      # 求解依赖
cargo run --bin rattler --release shell-hook         # 输出 shell 激活脚本
```
