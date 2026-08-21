---
okf_version: "0.2"
type: "concept"
title: "conda-lock 简介"
sources:
  - "conda_lock/conda_lock.py"
  - "conda_lock/src_parser/__init__.py"
  - "conda_lock/models/lock_spec.py"
---

# conda-lock 简介

## 什么是 conda-lock

conda-lock 是一个 **Conda 环境锁定文件生成工具** [F-001]，采用 MIT 开源许可证发布。它的核心功能是从 Conda 环境规格文件（environment.yml、meta.yaml、pyproject.toml）生成完全可重现的跨平台锁定文件（conda-lock.yml），精确记录每个包的名称、版本、构建号、哈希值和下载 URL，确保在不同机器、不同时间创建的环境完全一致。

conda-lock 解决的核心痛点是：`conda env create` 或 `conda install` 在不同时间执行可能得到不同版本的包（因为通道中的包不断更新），导致"我这边能跑"的环境不可重现问题。

```python
# conda_lock/conda_lock.py — CLI 入口模块
# 基于 Click 框架构建，提供 lock/install/render/render-lock-spec 四个核心命令（lock 为默认子命令），增量更新通过 lock --update 实现
# conda-lock 不自实现依赖求解算法，而是委托给 conda/mamba/micromamba
```

## 核心能力

### 1. 跨平台锁定

conda-lock 可以在一个平台上为多个目标平台生成锁文件 [F-002]。例如在 macOS 开发机上同时锁定 linux-64、osx-arm64、win-64 三个平台的依赖，生成一个包含所有平台包信息的统一锁文件。这通过虚拟包（virtual packages）机制模拟目标平台的系统依赖（如 __glibc、__cuda、__osx 版本）实现。

### 2. conda + pip 混合锁定

conda-lock 同时支持 conda 包和 PyPI(pip) 包的锁定 [F-003]。conda 依赖通过调用 conda/mamba/micromamba 的 dry-run 接口求解，pip 依赖使用 vendored 的 Poetry 求解器独立求解，两者结果合并到同一个锁文件中。conda↔pip 包名映射通过 grayskull 的映射数据自动处理。

### 3. 可重现环境

锁文件中记录每个包的精确版本、构建字符串、MD5/SHA256 哈希和下载 URL [F-004]。安装时从锁文件读取精确信息下载和安装，确保环境完全一致。锁文件支持 v1 和 v2 两种格式，v2 使用 categories 集合支持一包多类别。

### 4. 多源文件聚合

支持同时解析多个 environment.yml/pyproject.toml/meta.yaml 文件并聚合锁定 [F-005]。`aggregate_lock_specs()` 函数将多源文件的依赖规格合并，处理通道合并、依赖去重和类别传播。

### 5. 增量更新

通过 `conda-lock lock --update` 进行增量更新 [F-006]，通过构造假 conda 环境（fake_conda_environment）和 pinning 机制限制求解器更新范围，而非每次全量重新求解。指定包名可仅更新特定包：`conda-lock lock --update <package>`。

## 与同类工具对比

| 特性 | conda-lock | conda env export | pip-compile | Poetry lock |
|------|-----------|------------------|-------------|-------------|
| **锁定 conda 包** | ✅ | ✅ | ❌ | ❌ |
| **锁定 pip 包** | ✅ | ⚠️ 仅pip列表 | ✅ | ✅ |
| **跨平台锁定** | ✅ 多平台单文件 | ❌ 当前平台 | ❌ | ❌ |
| **输入格式** | environment.yml/meta.yaml/pyproject.toml | 当前环境导出 | requirements.in | pyproject.toml |
| **求解方式** | 委托conda/mamba + Poetry | N/A（导出当前状态） | pip + resolvelib | Poetry solver |
| **虚拟包支持** | ✅ 完整模拟系统依赖 | ❌ | ❌ | ❌ |
| **锁文件格式** | conda-lock.yml (v1/v2) | environment.yml | requirements.txt | poetry.lock |
| **增量更新** | ✅ fake-env + pinning | ❌ | ✅ | ✅ |
| **许可证** | MIT | BSD-3-Clause | BSD-3-Clause | MIT |

**关键区别说明**：

- **conda env export** 导出的是当前环境中实际安装的包列表，只能锁定当前平台；conda-lock 从规格文件出发主动求解，可以在一个平台上为其他平台锁定。
- **pip-compile** 和 **Poetry lock** 仅处理 Python 包，不处理 conda 的非 Python 依赖（如 CUDA、MKL、C 编译器等）。
- conda-lock 的独特优势在于**全栈跨平台锁定**：同时管理 conda 二进制包和 pip Python 包，支持多平台，利用虚拟包系统正确处理系统级依赖约束。

## 设计哲学

conda-lock 的核心设计决策是 **"不自求解释器"** [F-007]：不重新实现 conda 的 SAT 求解算法，而是通过子进程调用 conda/mamba/micromamba 的 `--dry-run --json` 接口获取求解结果。这一决策使得 conda-lock 天然与 conda 生态的求解逻辑保持一致，避免了求解器算法的维护负担，但也带来了对 conda CLI 输出格式的依赖。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
- [源文件解析](07-source-parsers.md)
- [Conda 求解器](08-conda-solver.md)
