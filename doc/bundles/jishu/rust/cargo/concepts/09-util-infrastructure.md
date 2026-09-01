---
type: Concept
title: util 基础设施：42 个子模块与构建支撑
description: util 模块的数据结构、并发原语、文件锁、错误体系、Rustc 探测与 build.rs 三函数注入链
tags: [rust, cargo, util, infrastructure, build-rs]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-28T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T10:00:00+08:00" }
status: stable
stale_after: 2027-08-28
sources:
  - id: cargo-source
    resource: /references/cargo-source-map.md
---

# util 基础设施：42 个子模块与构建支撑

`src/util/` 是 cargo 的地基：数据结构、并发原语、进程管理、文件锁、错误体系、VCS 封装全部在此。lib.rs 的 re-exports 通道也经此中转——`GlobalContext`、`CargoResult` 等最常用的类型都是 util 的再出口（F-cargo-034）。

## 模块清单与 re-exports（F-cargo-089/090/091）

42 个子模块（F-cargo-090）：`auth`、`cache_lock`、`canonical_url`、`command_prelude`、`counter`、`cpu`、`credential`、`dependency_queue`、`diagnostic_server`、`edit_distance`、`errors`、`flock`、`frontmatter`、`graph`、`hasher`、`hex`、`important_paths`、`interning`、`into_url`、`into_url_with_base`、`io`、`job`、`local_poll_adapter`、`data_structures`、`lockserver`、`log_message`、`logger`、`machine_message`、`network`、`once`、`open`、`progress`、`queue`、`restricted_names`、`rustc`、`semver_eval_ext`、`semver_ext`、`sqlite`、`time_span`、`unhashed`、`vcs`、`workspace`。

mod.rs 的 re-exports（F-cargo-089）按主题分组：

| 主题 | 项 |
|------|-----|
| 数据结构 | `CanonicalUrl`、`DependencyQueue`、`Graph`、`Queue`、`StableHasher`、`{hash_u64, short_hash, to_hex}` |
| 错误体系 | `CliError`、`{CargoResult, CliResult, internal}` |
| 进程与网络 | `RustfixDiagnosticServer`、`{LockServer, LockServerClient, LockServerStarted}`、`IntoUrl`、`IntoUrlWithBase`、`BuildLogger`、`OnceExt` |
| 文件与锁 | `{FileLock, Filesystem}`、`Unhashed` |
| VCS | `{FossilRepo, GitRepo, HgRepo, PijulRepo, existing_vcs_repo}` |
| 进度 | `{Progress, ProgressStyle}`、`pub use cargo_util_terminal::style;` |
| 配置 | `{ConfigValue, GlobalContext, homedir}` |
| 模糊匹配 | `{closest, closest_msg, edit_distance}` |

mod.rs 公开函数（F-cargo-091）：`pub fn is_rustup() -> bool`（:81）、`pub fn elapsed(duration: Duration) -> String`（:86）、`pub struct HumanBytes(pub u64)`（:97）、`pub fn indented_lines(text: &str) -> String`（:119）、`pub fn truncate_with_ellipsis(s: &str, max_width: usize) -> String`（:131）、`pub fn try_canonicalize<P: AsRef<Path>>(path: P) -> std::io::Result<PathBuf>`（:145）、`pub fn get_umask() -> u32`（:169）。

## Graph：cargo 自己的图原语（F-cargo-092）

```rust
pub struct Graph<N: Clone, E: Clone> {
    nodes: im_rc::OrdMap<N, im_rc::OrdMap<N, E>>,
}
```

方法族：`new`/`add`/`link`/`reversed`/`contains`/`edge`/`edges`/`sort`（sort 为拓扑排序）（F-cargo-092）。`Resolve` 的依赖图（F-cargo-064）与 unit 图都以它为底座。内部用 `im_rc::OrdMap`（持久化数据结构，workspace 依赖 `im-rc = "15.1.0"`，F-cargo-007）——`reversed` 之类的图变换因此可以结构共享。

## flock：文件系统抽象与协作锁（F-cargo-094）

flock.rs 的模块文档（原文）：

> "This module defines the Filesystem type which is an abstraction over a filesystem, ensuring that access to the filesystem is only done through coordinated locks."

`pub struct FileLock { f: Option<File>, path: PathBuf }` 实现 Read/Write/Seek，drop 时释放锁；导出 `lock_exclusive`/`lock_shared`/`try_lock_exclusive`/`try_lock_shared`/`unlock`（F-cargo-094）。`Filesystem` 是 `target_dir`/`build_dir`/`home_path` 等字段的类型（F-cargo-043/079）——目录创建与锁竞争在这些字段的消费处自动发生。全局包缓存锁由 context 的 `CacheLocker`（`package_cache_lock` 字段）编排（F-cargo-043）。

## 并发原语：Queue、job、cpu（F-cargo-095/096/097）

- **Queue**（F-cargo-096）：`pub struct Queue<T> { state: Mutex<State<T>>, popper_cv: Condvar, bounded_cv: Condvar, bound: usize }`；文档原文："`push` will never block, and allows the queue to grow without bounds. `push_bounded` will block if the queue is over bounds"——两条入队路径（无界/有界）供 job_queue 的消费端（F-cargo-106）选用。
- **job**（F-cargo-097）：Job Objects（Windows 作业对象）管理。模块文档原文："Job management (mostly for windows)"、"On Windows, however, this does not happen and Ctrl-C just kills cargo."、"we use Job Objects to ensure that all processes die at the same time"——`pub fn setup() -> Option<Setup>` 在 `main()` 前置流程中被调用（F-cargo-014），解决 Windows 上 Ctrl-C 只杀 cargo 不杀子进程的问题。
- **cpu**（F-cargo-095）：`pub struct State(imp::State)`、`State::current() -> io::Result<State>`、`idle_since(&self, previous: &State) -> f64`（"as a percentage from 0.0 to 100.0"）——CPU 空闲率采样，供 `build.job` 自动并发数决策；Linux 实现读取 user/nice/system/idle/iowait/irq/softirq/steal/guest 各计数。

## 字符串驻留与稳定哈希（F-cargo-098/099）

- **interning**（F-cargo-099）：`pub struct InternedString` 实现 `Deref<str>`/`AsRef<str>`/`AsRef<OsStr>`/`AsRef<Path>`/`Hash`/`Borrow<str>`/`Serialize`——包名/特征名等高频短字符串的全局驻留，`PackageIdInner`（F-cargo-083）与 `UnitInner`（F-cargo-109）的 `features: Vec<InternedString>` 都以它为元素。
- **hasher**（F-cargo-098）：模块文档原文："A hasher that produces the same values across releases and platforms."、"not sufficient for cryptographic purposes"；`pub use rustc_stable_hash::StableSipHasher128 as StableHasher;`——**跨版本跨平台稳定**的哈希（`dep_hash`、fingerprint 缓存键的基础），但明确声明不可用于密码学场景。

## 进度显示与 sqlite（F-cargo-093/100）

- **progress**（F-cargo-093）：`pub struct Progress<'gctx>`（:29）、`pub enum ProgressStyle`（:213）——下载/编译进度条的渲染层。
- **sqlite**（F-cargo-100）：模块文档 "Utilities to help with sqlite."；`pub type Migration = Box<dyn Fn(&Connection) -> CargoResult<()>>`、`pub fn basic_migration(stmt: &'static str) -> Migration`、`pub fn migrate(conn: &mut Connection, migrations: &[Migration]) -> CargoResult<()>`——数据库迁移框架，供 global_cache_tracker（F-cargo-078）使用；rusqlite 以 `features = ["bundled"]` 引入（F-cargo-007）。

## 命令工具与 URL（F-cargo-101/102）

- **util::workspace**（F-cargo-101）：`print_available_packages/ws` 与 `print_available_examples/binaries/benches/tests(ws, options)`、`path_args(ws, unit) -> (PathBuf, PathBuf)`、`add_path_args(ws, unit, cmd: &mut ProcessBuilder)`——运行类命令（run/test）构造子进程参数的辅助。
- **into_url**（F-cargo-102）：`pub trait IntoUrl`（:8）——字符串到 `Url` 的安全转换，registry URL 处理的入口转换。

## 错误体系（F-cargo-103）

errors.rs 的类型族：

```rust
pub type CargoResult<T> = anyhow::Result<T>;       // :11
pub type CliResult = Result<(), CliError>;          // :308
pub struct CliError;                                 // :316
pub struct VerboseError;                             // :144
pub struct InternalError;                            // :179
pub struct AlreadyPrintedError;                      // :212
pub struct ManifestError;                            // :246
pub struct HttpNotSuccessful;                        // :34
pub struct GitCliError;                              // :375
pub fn internal<S: fmt::Display>(error: S) -> anyhow::Error;  // :426
```

（F-cargo-103。）`CargoResult` 直接别名到 `anyhow::Result`——错误处理策略是"应用层 anyhow"；`InternalError` 链在 `display_error` 中触发 "this is an unexpected cargo internal error" 输出（F-cargo-036），`AlreadyPrintedError` 表示错误已上屏、避免重复输出。这些类型经 lib.rs 顶层 re-export（F-cargo-034）成为全仓库公共词汇。

## 日志与工具链探测（F-cargo-104/105）

- **logger**（F-cargo-104）：`pub struct BuildLogger`（:102）内部含 FileLogger/InMemoryLogger 与 `pub struct RunId`（:161）——构建日志的双通道（文件 + 内存）。
- **rustc**（F-cargo-105）：`pub struct Rustc` 的字段：`path: PathBuf`、`wrapper: Option<PathBuf>`、`workspace_wrapper: Option<PathBuf>`、`verbose_version: String`、`version: semver::Version`、`host: InternedString`、`commit_hash: Option<String>`、`cache: Mutex<Cache>`；`Rustc::new(path, wrapper, workspace_wrapper, rustup_rustc, cache_location, gctx)` 通过执行 `rustc -vV` 获取信息。编译调度的工具链认知（版本、host、wrapper 链）全部由此探测——三层 wrapper（RUSTC wrapper / workspace wrapper）的字段即 `--wrapper` 链的实现基础。

## build.rs：仓库自身的构建注入（F-cargo-135~138）

仓库根 build.rs 的 `fn main()` 调用三个函数并输出环境注入（F-cargo-135）：

1. **`commit_info()`**（F-cargo-137）：环境变量 `CFG_OMIT_GIT_HASH` 存在时直接返回（发行版 tarball 无 git）；否则从 `git log -1 --date=short --format="%H %h %cd"` 或 rustc source tarball 的 `git-commit-info` 文件读取，输出 `CARGO_COMMIT_HASH`/`CARGO_COMMIT_SHORT_HASH`/`CARGO_COMMIT_DATE`——`cargo -vV` 的 commit 行（F-cargo-032）与 `version()` 推导链（F-cargo-144）的数据源。
2. **`compress_man()`**（F-cargo-136）：将 `etc/man/*.{1}` 与 `doc/man/generated_txt/*.txt` 打包为 `OUT_DIR/man.tgz`（tar `HeaderMode::Deterministic` + gzip `Compression::best()`），每个文件输出 `cargo:rerun-if-changed`——手册页嵌入二进制的机制。
3. **`windows_manifest()`**（F-cargo-138）：仅 `target_os = "windows"` 且 `target_env = "msvc"` 时嵌入 `windows.manifest.xml`（`cargo:rustc-link-arg-bin=cargo=/MANIFEST:EMBED` 与 `/MANIFESTINPUT`，并加 `/WX`）。

外加输出 `cargo:rustc-env=RUST_HOST_TARGET={target}`（F-cargo-135）——`cargo -vV` 的 host 字段（F-cargo-032 中 `env!("RUST_HOST_TARGET")`）由此编译期固化。

## 相关概念

- [简介与架构总览](/concepts/00-intro-architecture-overview.md) — lib.rs re-exports 通道与版本链
- [编译调度与 unit 图](/concepts/07-build-scheduling-unit-graph.md) — Graph/Queue/job/Rustc 的主要消费者
- [依赖解析 resolver](/concepts/04-dependency-resolver.md) — Graph 与 InternedString 在解析侧的使用
- [认证与 credential](/concepts/08-auth-credential.md) — auth 子模块与 credential 子模块的分工
