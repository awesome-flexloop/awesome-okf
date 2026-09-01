---
okf_version: "0.2"
---

# conda-lock 知识库

本知识包是 Conda 环境锁定文件生成工具 [conda-lock](https://github.com/conda/conda-lock)（MIT 许可证）的系统化中文源码教程，基于 conda-lock 源码深度阅读生成，覆盖从快速上手到跨平台锁定的完整知识体系。所有内容均溯源至 conda-lock 源码（`conda_lock/` 包核心模块，排除 `_vendor/` 目录），遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门篇（concepts/）

* [conda-lock 简介](concepts/00-introduction.md) — 什么是 conda-lock（Conda 环境锁定工具）、MIT 许可证、核心能力（跨平台锁定、conda+pip混合、可重现环境）、与 conda env export/pip-compile/Poetry lock 对比、不自求解释器的设计哲学。
* [5分钟快速上手](concepts/01-getting-started.md) — 安装（pip/conda/mamba）、创建 environment.yml、生成锁文件（conda-lock lock）、安装环境（conda-lock install）、渲染格式（conda-lock render）、增量更新（conda-lock lock --update）、常见问题速查。
* [架构总览](concepts/02-architecture-overview.md) — 五层分层架构（CLI层→源解析层→模型层→求解层→锁文件层），数据流图，vendored 依赖策略（vendored_conda/vendored_poetry/vendored_grayskull），外部可执行文件发现。

## 核心数据模型篇（concepts/）

* [LockSpecification 模型](concepts/03-lock-specification.md) — 核心数据模型：dependencies 按平台分组成字典、channels 列表、sources 追踪、pip_repositories、allow_pypi_requests 开关、platforms 属性、类别过滤机制（make_lock_spec 的 filtered_categories 参数）、构建过程。
* [Channel 与凭证安全](concepts/04-channel-model.md) — Channel 不可变 Pydantic 模型（frozen=True）、from_string() 解析、token/basic-auth 自动检测与环境变量替换、三种 token 脱敏格式（<TOKEN>/*****/**********）识别、normalize_url_with_placeholders() 归一化、凭证安全设计原则。
* [四类依赖模型](concepts/05-dependency-types.md) — _BaseDependency 基类、VersionedDependency（版本约束）、URLDependency（直接URL）、VCSDependency（Git等VCS）、PathDependency（本地路径）、Dependency TypeAlias 联合类型、求解前后信息差异。
* [锁文件 v1/v2 格式](concepts/06-lockfile-formats.md) — v1 单 category vs v2 多 categories 集合、LockedDependency 字段、LockMeta 元数据、hash 字段（md5 for conda/sha256 for pip）、拓扑排序、v1↔v2 双向转换、apply_categories() BFS 传播、_truncate_main_category() 截断。

## 核心业务逻辑篇（concepts/）

* [源文件解析](concepts/07-source-parsers.md) — 三格式支持（environment.yml/meta.yaml/pyproject.toml）、platform selectors 条件注释过滤（# [linux]）、PEP 508 markers 评估、grayskull 包名映射（PyPI↔conda）、aggregate_lock_specs 多源聚合、ordered_union 有序去重。
* [Conda 求解器](concepts/08-conda-solver.md) — dry-run 求解策略（conda create --dry-run --json）、solve_specs_for_arch() 单平台求解、update_specs_for_arch() 增量更新（fake_conda_environment+pinning）、make_fake_python_binary() 防 libmamba v2 失败、FETCH/LINK actions 重建、_to_match_spec() 转换、三种后端差异（conda/mamba/micromamba）。
* [PyPI 求解器](concepts/09-pypi-solver.md) — vendored Poetry 求解器集成、目标平台环境模拟（os_name/sys_platform/machine）、conda↔pip 包名映射（lookup_cache/grayskull）、conda 优先避免重复求解、PEP 508 markers 评估、私有 PyPI 仓库、allow_pypi_requests 开关。
* [虚拟包系统](concepts/10-virtual-packages.md) — 为什么需要虚拟包（跨平台系统依赖）、VirtualPackage/FullVirtualPackage/FakeRepoData 三层模型、默认虚拟包集（__glibc/__cuda/__osx/__archspec/__unix/__win）、CUDA 版本覆盖（override_cuda_version）、CONDA_OVERRIDE_* 环境变量、自定义 virtual-packages.yaml、向后兼容 add_duplicate_osx_package。

## CLI 与工具链篇（concepts/）

* [CLI 命令体系](concepts/11-cli-commands.md) — Click OrderedGroup 默认 lock 子命令、lock/install/render/render-lock-spec 四命令详解、主要选项（lock/render 的 --dev-dependencies、install 的 --dev、--platform/--channel/--extras/--kind/--virtual-package-spec/--conda/--mamba/--check-input-hash）、lock --update 增量更新、位置参数 vs --file 选项、命令调用链。
* [内容哈希机制](concepts/12-content-hash.md) — SHA-256 计算流程（channels JSON + 排序 specs + 虚拟包哈希）、确定性 JSON 序列化（sort_keys=True）、backwards_compatible_content_hashes() 多哈希向后兼容集合、已知设计缺陷（issue #432）：遗漏因素/虚拟包近似/repodata时序/多哈希模糊性。
* [Conda 调用层](concepts/13-invoke-conda.md) — ensureconda 自动发现可执行文件、子进程双线程 I/O 防死锁、stderr 智能日志级别检测（conda/mamba 格式自动识别）、CONDA_SUBDIR 跨平台求解、--override-channels 隔离用户配置、临时包缓存管理（conda_pkgs_dir）、错误处理。

## 高级主题篇（concepts/）

* [依赖类别与传播](concepts/14-categories-and-deps.md) — main/dev/docs/test 自定义 category、environment.yml category 扩展语法、pyproject.toml optional-dependencies 映射、apply_categories() BFS 传播算法、_truncate_main_category() main 截断规则、v2 多 category 设计动机、安装时类别过滤、make_lock_spec() 的 filtered_categories 过滤机制。
* [跨平台锁定策略](concepts/15-cross-platform-locking.md) — DEFAULT_PLATFORMS、CONDA_SUBDIR 覆盖、platform selectors 与 markers 双重过滤、make_fake_python_binary() 防 libmamba 失败、多平台锁文件结构、跨平台安装自动选择、平台映射表、注意事项与限制。

## 实战示例（examples/）

* [基础锁定工作流](examples/basic-lock-workflow.md) — 创建 environment.yml → conda-lock lock → conda-lock install → conda-lock render 的完整入门流程，含 Makefile 一键脚本和常见问题解答。对应概念：[5分钟快速上手](concepts/01-getting-started.md)、[CLI 命令体系](concepts/11-cli-commands.md)。
* [多平台锁定](examples/multi-platform-lock.md) — 指定 --platform 生成 linux-64/osx-arm64/win-64 跨平台锁文件，使用平台选择器处理平台特定依赖，验证跨平台版本一致性，渲染各平台 explicit 文件。对应概念：[跨平台锁定策略](concepts/15-cross-platform-locking.md)、[虚拟包系统](concepts/10-virtual-packages.md)。
* [自定义虚拟包](examples/custom-virtual-packages.md) — 创建 virtual-packages.yaml 锁定 CUDA 版本（__cuda=12.1）、glibc 版本（__glibc=2.28/2.35）、macOS 版本（__osx=13.0），GPU/CentOS/Ubuntu/macOS 多场景配置，虚拟包参考表和验证脚本。对应概念：[虚拟包系统](concepts/10-virtual-packages.md)、[内容哈希机制](concepts/12-content-hash.md)。
* [开发依赖与 category 过滤](examples/dev-dependencies.md) — 使用 category: dev/docs/test 字段标记开发/文档/测试依赖，锁定时通过 --dev-dependencies/--extras、安装时通过 --dev/--extras 控制范围，BFS 类别传播算法详解，environment.yml 和 pyproject.toml 两种格式。对应概念：[依赖类别与传播](concepts/14-categories-and-deps.md)、[锁文件 v1/v2 格式](concepts/06-lockfile-formats.md)。

## 信源登记簿（references/）

* [CLI 入口点 (conda_lock.py)](references/cli-entry.md) — conda-lock CLI 基于 Click 框架构建，使用 OrderedGroup 自定义命令组使 lock 成为默认子命令，包含 lock/install/render/render-lock-spec 四个核心命令及主要选项（lock/render 的 --dev-dependencies、install 的 --dev、--platform/--channel/--extras/--kind）。
* [Conda 求解器 (conda_solver.py)](references/solve-conda.md) — conda-lock 核心求解策略：不自实现 SAT 算法，而是调用 conda/mamba/micromamba 的 `create --dry-run --json` 获取求解结果；包含 solve_conda() 顶层调度、solve_specs_for_arch() 单平台 dry-run 求解、update_specs_for_arch() 增量更新（fake_conda_environment+pinning）、_to_match_spec() 依赖规格转换。
* [锁定规格模型 (models/lock_spec.py)](references/lock-spec-model.md) — 核心数据模型 LockSpecification（按平台分组的依赖字典+通道列表+源追踪+PyPI配置）、四类依赖模型（VersionedDependency/URLDependency/VCSDependency/PathDependency）及 Dependency TypeAlias 联合类型、Channel 不可变模型的凭证安全设计（token/basic-auth 自动脱敏、三种脱敏格式识别、环境变量替换）。
* [内容哈希算法 (content_hash.py)](references/content-hash.md) — SHA-256 内容哈希计算流程（channels JSON + 排序 specs + 虚拟包哈希）、确定性 JSON 序列化（sort_keys=True）、backwards_compatible_content_hashes() 多哈希向后兼容集合、已知设计缺陷说明（issue #432）。

## 信任与生命周期说明

* **status 判定依据**：全部 24 个内容文档（16 个概念 + 4 个示例 + 4 个信源登记）均 `status: stable`。内容基于对 conda-lock 源码（`external/libs/conda-dev/conda-lock/conda_lock/` 目录，排除 `_vendor/`）的逐模块阅读与事实提取，涵盖 CLI 层、源解析层、模型层、求解层、锁文件层五大模块的核心源码分析。
* **stale_after 解释**：统一设置为 `2027-12-31`。conda-lock 的核心架构（委托求解模式、虚拟包系统、LockSpecification 模型、锁文件 v2 格式）相对稳定，CLI 命令和选项可能在小版本中调整，但核心设计模式变化不大；该日期作为针对未来大版本的保守重新评估节点。
* **核验链路**：所有文档基于 2026-08-21 的源码静态分析生成，F-xxx 编号为文档内事实标记。

本知识包共收录 24 个内容文档（16 个概念 + 4 个示例 + 4 个信源登记），另含 3 个子目录 index.md 与根 index.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
