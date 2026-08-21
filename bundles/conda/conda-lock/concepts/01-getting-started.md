---
okf_version: "0.2"
type: "concept"
title: "5分钟快速上手"
sources:
  - "conda_lock/conda_lock.py"
  - "conda_lock/lockfile/__init__.py"
  - "conda_lock/src_parser/__init__.py"
---

# 5分钟快速上手

## 安装 conda-lock

conda-lock 可以通过 pip 或 conda 安装 [F-001]：

```bash
# pip 安装
pip install conda-lock

# 或 conda 安装
conda install -c conda-forge conda-lock

# 或 mamba 安装（更快）
mamba install -c conda-forge conda-lock
```

安装后验证：

```bash
conda-lock --help
```

如果看到 `lock/install/render/render-lock-spec` 四个子命令的帮助信息，说明安装成功。

## 第一步：创建 environment.yml

创建一个标准的 Conda 环境规格文件 [F-002]：

```yaml
# environment.yml
name: my-project
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy>=1.24
  - pandas
  - scikit-learn
  - pip:
      - requests>=2.28
      - pydantic
platforms:
  - linux-64
  - osx-arm64
  - win-64
```

> `platforms` 字段是 conda-lock 扩展字段，指定目标锁定平台。如果不指定，conda-lock 默认锁定当前平台。

## 第二步：生成锁文件

在 environment.yml 所在目录执行 [F-003]：

```bash
# 默认锁定（conda-lock 等同于 conda-lock lock）
conda-lock lock --file environment.yml

# 或显式指定多个源文件
conda-lock lock -f environment.yml -f pyproject.toml

# 指定目标平台（覆盖 environment.yml 中的 platforms）
conda-lock lock -f environment.yml -p linux-64 -p osx-arm64 -p win-64

# 使用 mamba 作为求解后端（更快）
conda-lock lock -f environment.yml --conda mamba

# 包含开发依赖
conda-lock lock -f environment.yml --dev-dependencies
```

执行完成后，当前目录会生成 `conda-lock.yml` 文件。这是锁文件，包含所有平台、所有依赖（含传递依赖）的精确版本和哈希信息。

```bash
# 查看生成的锁文件
ls -la conda-lock.yml

# 查看锁文件内容概要
head -50 conda-lock.yml
```

## 第三步：从锁文件安装环境

使用 `conda-lock install` 从锁文件创建环境 [F-004]：

```bash
# 创建命名环境
conda-lock install --name my-project conda-lock.yml

# 或指定前缀路径
conda-lock install --prefix ./env conda-lock.yml

# 包含开发依赖
conda-lock install --name my-project --dev conda-lock.yml

# 包含额外 category
conda-lock install --name my-project --extras test --extras docs conda-lock.yml
```

安装完成后，激活环境：

```bash
conda activate my-project
```

此时环境中的所有包版本与锁文件完全一致，具有完美的可重现性。

## 第四步：渲染其他格式

锁文件可以渲染为其他格式 [F-005]：

```bash
# 渲染为 explicit 格式（URL 列表，conda create --file 可直接使用）
conda-lock render --kind explicit -p linux-64

# 渲染为 environment.yml 格式（固定版本的环境文件）
conda-lock render --kind env

# 仅渲染特定平台
conda-lock render --kind explicit -p osx-arm64
```

explicit 格式输出示例：

```
# platform: linux-64
@EXPLICIT
https://conda.anaconda.org/conda-forge/linux-64/python-3.10.12-hd12c33a_0_cpython.tar.bz2#d41d8cd98f00b204e9800998ecf8427e
https://conda.anaconda.org/conda-forge/linux-64/numpy-1.24.4-py310h43ef7f0_0.conda#a1b2c3d4e5f6...
...
```

## 第五步：更新锁文件

当需要更新某些包时 [F-006]：

```bash
# 更新所有包到最新兼容版本（增量更新模式）
conda-lock lock --update --file environment.yml

# 更新指定包
conda-lock lock --update numpy --update pandas -f environment.yml

# 仅更新特定平台
conda-lock lock --update -f environment.yml -p linux-64
```

增量更新通过 `lock --update` 模式实现：构造假 conda 环境（包含旧锁文件的包元数据），通过 pinning 机制限制更新范围，比全量重新锁定更快。注意：添加新依赖应修改 environment.yml 后重新运行 `conda-lock lock`（不加 --update），而非使用 --update。

## 完整工作流概览

```
environment.yml ──┐
pyproject.toml ───┤
meta.yaml ────────┤
                  ▼
         conda-lock lock
                  │
                  ▼
          conda-lock.yml  ◄── 可提交到 Git
            │         │
            ▼         ▼
    conda-lock    conda-lock
      install      render
        │            │
        ▼            ▼
   conda 环境    explicit/env
   (精确版本)    (其他工具使用)
```

## 常见问题速查

| 问题 | 解决方案 |
|------|---------|
| 求解太慢 | 使用 `--conda mamba` 切换到 mamba 后端 |
| 需要锁定 CUDA 版本 | 使用 `--virtual-package-spec` 指定虚拟包配置 |
| pip 包未包含 | 确认 environment.yml 中有 `pip:` 段，且未设置 `--no-dev-dependencies` |
| 想排除某些平台 | 使用 `-p` 明确指定需要的平台 |
| 锁文件太大 | 减少目标平台数量，或使用 `--filter-categories` 过滤 |

## 相关概念

- [conda-lock 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [CLI 命令体系](11-cli-commands.md)
- [源文件解析](07-source-parsers.md)
- [基础锁定工作流](../examples/basic-lock-workflow.md)
