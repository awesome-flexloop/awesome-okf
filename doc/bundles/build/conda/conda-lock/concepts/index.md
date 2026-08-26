---
okf_version: "0.2"
type: "index"
title: "conda-lock 概念文档"
sources:
  - "conda_lock/"
---

# 概念文档

本目录包含 conda-lock 的 16 个核心概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门篇

* [00-conda-lock 简介](00-introduction.md) — 什么是 conda-lock（Conda 环境锁定工具）、MIT 许可证、核心能力（跨平台锁定、conda+pip混合、可重现环境）、与 conda env export/pip-compile/Poetry lock 对比、不自求解释器的设计哲学。
* [01-5分钟快速上手](01-getting-started.md) — 安装（pip/conda/mamba）、创建 environment.yml、生成锁文件（conda-lock lock）、安装环境（conda-lock install）、渲染格式（conda-lock render）、增量更新（conda-lock lock --update）。
* [02-架构总览](02-architecture-overview.md) — 五层分层架构（CLI层→源解析层→模型层→求解层→锁文件层）、数据流图、vendored 依赖策略、外部可执行文件发现。

## 核心数据模型篇

* [03-LockSpecification 模型](03-lock-specification.md) — 核心数据模型：dependencies 按平台分组成字典、channels 列表、sources 追踪、pip_repositories、allow_pypi_requests 开关、platforms 属性、类别过滤机制（make_lock_spec 的 filtered_categories 参数）。
* [04-Channel 与凭证安全](04-channel-model.md) — Channel 不可变 Pydantic 模型（frozen=True）、from_string() 解析、token/basic-auth 自动检测与环境变量替换、三种 token 脱敏格式（<TOKEN>/*****/**********）、normalize_url_with_placeholders() 归一化。
* [05-四类依赖模型](05-dependency-types.md) — _BaseDependency 基类、VersionedDependency（版本约束）、URLDependency（直接URL）、VCSDependency（Git等VCS）、PathDependency（本地路径）、Dependency TypeAlias 联合类型、求解前后信息差异。
* [06-锁文件 v1/v2 格式](06-lockfile-formats.md) — v1 单 category vs v2 多 categories 集合、LockedDependency 字段、LockMeta 元数据、hash 字段（md5 for conda/sha256 for pip）、拓扑排序、v1↔v2 双向转换、apply_categories() BFS 传播。

## 核心业务逻辑篇

* [07-源文件解析](07-source-parsers.md) — 三格式支持（environment.yml/meta.yaml/pyproject.toml）、platform selectors 条件注释过滤、PEP 508 markers 评估、grayskull 包名映射、aggregate_lock_specs 多源聚合、ordered_union 有序去重。
* [08-Conda 求解器](08-conda-solver.md) — dry-run 求解策略（conda create --dry-run --json）、solve_specs_for_arch() 单平台求解、update_specs_for_arch() 增量更新、fake_conda_environment() 假环境构造、make_fake_python_binary() 防 libmamba 失败、FETCH/LINK actions 重建、三种后端差异。
* [09-PyPI 求解器](09-pypi-solver.md) — vendored Poetry 求解器集成、目标平台环境模拟（os_name/sys_platform/machine）、conda↔pip 包名映射（lookup_cache/grayskull）、conda 优先避免重复求解、PEP 508 markers 评估、私有 PyPI 仓库支持。
* [10-虚拟包系统](10-virtual-packages.md) — 为什么需要虚拟包（跨平台系统依赖）、VirtualPackage/FullVirtualPackage/FakeRepoData 三层模型、默认虚拟包集（__glibc/__cuda/__osx/__archspec/__unix/__win）、CUDA 版本覆盖、CONDA_OVERRIDE_* 环境变量、自定义 virtual-packages.yaml。

## CLI 与工具链篇

* [11-CLI 命令体系](11-cli-commands.md) — Click OrderedGroup 默认 lock 子命令、lock/install/render/render-lock-spec 四命令详解、主要选项（lock/render 的 --dev-dependencies、install 的 --dev、--platform/--channel/--extras/--kind/--virtual-package-spec/--conda）、lock --update 增量更新、命令调用链。
* [12-内容哈希机制](12-content-hash.md) — SHA-256 计算流程（channels JSON + 排序 specs + 虚拟包哈希）、确定性 JSON 序列化（sort_keys=True）、backwards_compatible_content_hashes() 多哈希向后兼容集合、已知设计缺陷（issue #432）。
* [13-Conda 调用层](13-invoke-conda.md) — ensureconda 自动发现可执行文件、子进程双线程 I/O 防死锁、stderr 智能日志级别检测（conda/mamba 格式）、CONDA_SUBDIR 跨平台求解、--override-channels 隔离用户配置、临时包缓存管理。

## 高级主题篇

* [14-依赖类别与传播](14-categories-and-deps.md) — main/dev 自定义 category、apply_categories() BFS 传播算法、_truncate_main_category() main 截断规则、v2 多 category 设计动机、安装时类别过滤。
* [15-跨平台锁定策略](15-cross-platform-locking.md) — DEFAULT_PLATFORMS、CONDA_SUBDIR 覆盖、platform selectors 与 markers 双重过滤、fake python binary 防 libmamba 失败、多平台锁文件结构、平台映射表、跨平台安装自动选择。

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-lock-specification
04-channel-model
05-dependency-types
06-lockfile-formats
07-source-parsers
08-conda-solver
09-pypi-solver
10-virtual-packages
11-cli-commands
12-content-hash
13-invoke-conda
14-categories-and-deps
15-cross-platform-locking
```
