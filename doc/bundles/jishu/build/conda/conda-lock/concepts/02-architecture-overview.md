---
okf_version: "0.2"
type: "concept"
title: "架构总览"
sources:
  - "conda_lock/conda_lock.py"
  - "conda_lock/src_parser/__init__.py"
  - "conda_lock/conda_solver.py"
  - "conda_lock/pypi_solver.py"
  - "conda_lock/lockfile/__init__.py"
  - "conda_lock/interfaces/"
---

# 架构总览

conda-lock 采用五层分层架构，数据从 CLI 输入流经源解析、模型构建、依赖求解，最终写入锁文件。整体遵循"不自求解释器"的设计原则——conda 依赖求解委托给外部 conda/mamba/micromamba 进程，pip 依赖求解使用 vendored 的 Poetry 求解器。

## 五层架构

```
┌─────────────────────────────────────────────────────────┐
│  1. CLI 层 (conda_lock.py + click_helpers.py)           │
│     Click OrderedGroup → lock/install/render/render-lock-spec     │
├─────────────────────────────────────────────────────────┤
│  2. 源解析层 (src_parser/)                              │
│     environment_yaml.py / meta_yaml.py / pyproject_toml │
│     → selectors.py (平台条件过滤)                        │
│     → markers.py (PEP 508 标记评估)                     │
│     → aggregation.py (多源聚合)                         │
├─────────────────────────────────────────────────────────┤
│  3. 模型层 (models/)                                    │
│     lock_spec.py (LockSpecification + Dependency)       │
│     channel.py (凭证安全通道模型)                        │
│     pip_repository.py (PyPI 私有仓库)                   │
│     dry_run_install.py (安装计划模型)                    │
├─────────────────────────────────────────────────────────┤
│  4. 求解层                                              │
│     conda_solver.py (调用 conda/mamba/micromamba)       │
│     pypi_solver.py (vendored Poetry 求解器)             │
│     virtual_package.py (虚拟包系统)                      │
│     invoke_conda.py (子进程调用)                        │
│     content_hash.py (内容哈希计算)                      │
├─────────────────────────────────────────────────────────┤
│  5. 锁文件层 (lockfile/)                                │
│     v1/models.py (v1 单 category 格式)                  │
│     v2prelim/models.py (v2 多 category 格式)            │
│     __init__.py (解析/写入/category传播)                │
└─────────────────────────────────────────────────────────┘
```

### 第1层：CLI 层

CLI 层基于 Click 框架构建 [F-001]，使用自定义 `OrderedGroup` 命令组使 `lock` 成为默认子命令。四个核心命令：

- **lock**：从源文件生成锁文件（默认命令），支持 `--update` 选项进行增量更新
- **install**：从锁文件安装环境，使用 `--dev/--no-dev` 标志控制开发依赖
- **render**：将锁文件渲染为其他格式（explicit/env），使用 `--dev-dependencies/--no-dev-dependencies` 标志
- **render-lock-spec**：输出锁定规格（LockSpecification）的结构化表示

> **注意**：增量更新不是独立子命令，而是通过 `lock --update` 实现的。`lock` 和 `render` 命令使用 `--dev-dependencies/--no-dev-dependencies` 标志，`install` 命令使用 `--dev/--no-dev` 标志。

CLI 层负责参数解析和选项传递，不包含业务逻辑。主要选项如 `--platform`、`--channel`、`--dev-dependencies`（lock/render）、`--dev`（install）、`--extras`、`--kind`、`--virtual-package-spec` 等，通过函数参数传递给下层。

### 第2层：源解析层

源解析层负责将不同格式的输入文件解析为统一的 `LockSpecification` 模型 [F-002]：

- **environment_yaml.py**：解析 Conda 标准的 `environment.yml`，支持平台选择器（`# [linux]` 条件注释）、pip 子段、category 扩展字段
- **meta_yaml.py**：解析 conda-build 的 `meta.yaml` 配方文件
- **pyproject_toml.py**：解析 PEP 621/Poetry 格式的 `pyproject.toml`，通过 grayskull 策略将 Poetry 依赖映射为 conda 依赖
- **selectors.py**：处理 `# [selector]` 格式的条件行过滤，支持 `linux`/`osx`/`win`/`unix`/`x86_64`/`arm64` 等选择器
- **markers.py**：评估 PEP 508 环境标记（如 `python_version >= "3.10"`），判断 pip 依赖是否适用于目标平台
- **aggregation.py**：聚合多源文件的锁定规格，处理通道合并和依赖去重

入口函数 `make_lock_spec()` 接受文件路径列表，根据文件扩展名分派到对应的解析器，最后调用 `aggregate_lock_specs()` 合并。

### 第3层：模型层

模型层使用 Pydantic 定义核心数据结构 [F-003]：

- **lock_spec.py**：`LockSpecification` 主模型 + 四类 `Dependency` 模型（VersionedDependency/URLDependency/VCSDependency/PathDependency）。Dependency 使用 TypeAlias 联合类型，通过 Pydantic 判别字段自动解析。
- **channel.py**：`Channel` 不可变模型（`frozen=True`），核心能力是凭证安全——`from_string()` 自动检测 token 和 basic auth，将凭证存入环境变量，URL 中只保留环境变量引用。支持 conda/mamba v1/mamba v2 三种 token 脱敏格式的识别和归一化。
- **virtual_package.py**：虚拟包系统（见求解层说明）

### 第4层：求解层

求解层是 conda-lock 的核心业务逻辑 [F-004]：

- **conda_solver.py**：Conda 依赖求解。**不自实现 SAT 算法**，而是对每个平台调用 `conda create --prefix <tmp> --dry-run --json` 获取安装计划。关键策略：
  - `solve_specs_for_arch()`：单平台 dry-run 求解
  - `update_specs_for_arch()`：增量更新，通过 `fake_conda_environment()` 构造假环境 + pinning 机制约束更新范围
  - `make_fake_python_binary()`：伪造 python 二进制防止 libmamba v2 的 pip inspect 检查失败
- **pypi_solver.py**：PyPI 依赖求解，使用 vendored 的 Poetry 求解器，模拟目标平台环境（platform/python_version/implementation）
- **virtual_package.py**：虚拟包系统，通过构造假 repodata.json 注入 `__glibc`/`__cuda`/`__osx`/`__archspec`/`__unix` 等系统依赖，实现跨平台锁定
- **invoke_conda.py**：Conda 子进程调用封装，双线程读取 stdout/stderr 防死锁，stderr 智能日志级别检测
- **content_hash.py**：SHA-256 内容哈希计算，用于快速检测输入变化

### 第5层：锁文件层

锁文件层负责锁文件的读写和版本管理 [F-005]：

- **v1/models.py**：v1 格式，`LockedDependency` 使用单字符串 category 字段
- **v2prelim/models.py**：v2 格式，`LockedDependency` 使用 `categories: Set[str]` 集合支持一包多类别，提供 `lockfile_v1_to_v2()` 和 `to_v1()` 双向转换
- **__init__.py**：统一读写入口 `parse_conda_lock_file()`/`write_conda_lock_file()`，`apply_categories()` BFS 传播类别标签

## 数据流

```
environment.yml ─┐
meta.yaml ───────┤─→ src_parser.make_lock_spec() ─→ LockSpecification
pyproject.toml ──┘         │                           │
                           │                    ┌──────┴──────┐
                           │                    │ 按平台分发   │
                           │                    └──┬───────┬──┘
                           │            conda 求解│       │pip 求解
                           │                       ▼       ▼
                           │             conda_solver  pypi_solver
                           │             (dry-run)   (Poetry)
                           │                       │       │
                           │                       └───┬───┘
                           │            VersionedDependency 列表
                           │                           │
                           │                  virtual_package
                           │                  (系统依赖注入)
                           │                           │
                           │                  content_hash 计算
                           │                           │
                           ▼                           ▼
                  lockfile.write_conda_lock_file() → conda-lock.yml
                                                      │
                                            ┌─────────┼─────────┐
                                            ▼         ▼         ▼
                                         install   render    render-lock-spec
                                       (创建环境) (格式转换) (输出锁定规格)
```

## Vendored 依赖策略

conda-lock 在 `interfaces/` 目录下 vendored 了三个外部依赖的适配接口 [F-006]：

| Vendored 模块 | 来源 | 用途 |
|--------------|------|------|
| `vendored_conda` | conda | MatchSpec 解析、toposort 拓扑排序等核心组件 |
| `vendored_poetry` | Poetry | PyPI 依赖求解器 |
| `vendored_grayskull` | grayskull | conda 包名 ↔ PyPI 包名映射数据 |
| `vendored_poetry_markers` | Poetry | PEP 508 环境标记解析和评估 |

这种 vendor 策略避免了运行时对 conda/poetry 的 Python 包依赖（仅需命令行的 conda/mamba 可执行文件），同时确保求解器行为与 Poetry 生态一致。

## 外部可执行文件发现

conda-lock 通过 `ensureconda` 库自动发现系统中的 conda/mamba/micromamba 可执行文件 [F-007]，优先级为 micromamba > mamba > conda（可通过 `--conda` 选项显式指定）。求解器后端差异被抽象到 `invoke_conda.py` 中统一处理。

## 相关概念

- [conda-lock 简介](00-introduction.md)
- [5分钟快速上手](01-getting-started.md)
- [LockSpecification 模型](03-lock-specification.md)
- [Conda 求解器](08-conda-solver.md)
- [源文件解析](07-source-parsers.md)
