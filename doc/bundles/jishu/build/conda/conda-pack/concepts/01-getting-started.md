---
type: "concept"
title: "5分钟快速上手"
description: 安装 conda-pack、打包环境、部署到目标机器的完整流程，包含命令行和 Python API 两种使用方式。
tags: [conda-pack, getting-started, cli, api]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:45:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
  - id: cli
    resource: /references/cli-source.md
    title: cli.py 与辅助模块源码
---

# 5分钟快速上手

## 安装 conda-pack

conda-pack 可以通过 conda 或 pip 安装：

```bash
# 通过 conda 安装（推荐）
conda install -c conda-forge conda-pack

# 或通过 pip 安装
pip install conda-pack
```

conda-pack 的唯一运行时依赖是 setuptools，安装后即可使用 `conda-pack` 命令行工具和 `conda_pack` Python 包 [F-059]。

## 命令行快速体验

### 打包当前激活环境

最简单的用法——打包当前激活的环境：

```bash
# 打包当前环境，输出为 my_env.tar.gz（自动以环境名命名）
conda-pack

# 或显式指定输出路径
conda-pack -o my_env.tar.gz
```

### 打包指定环境

```bash
# 通过环境名
conda-pack -n my_env -o my_env.tar.gz

# 通过环境路径
conda-pack -p /path/to/my_env -o my_env.tar.gz
```

### 选择归档格式

```bash
# zip 格式
conda-pack -n my_env -o my_env.zip

# tar.bz2 格式（更高压缩率）
conda-pack -n my_env -o my_env.tar.bz2 --compress-level 9

# tar.zst 格式（快速压缩，需 zstandard）
conda-pack -n my_env -o my_env.tar.zst

# squashfs 格式（只读压缩文件系统，需 mksquashfs）
conda-pack -n my_env -o my_env.squashfs
```

格式通过文件扩展名自动推断，也可以通过 `--format` 显式指定 [F-017][F-018]。

### 部署到目标机器

```bash
# 1. 将归档复制到目标机器（scp/rsync/U盘等）
scp my_env.tar.gz target-machine:/opt/envs/

# 2. 在目标机器上解压
mkdir -p /opt/envs/my_env
tar -xzf my_env.tar.gz -C /opt/envs/my_env

# 3. 激活环境
source /opt/envs/my_env/bin/activate

# 4. 运行 conda-unpack 修复路径前缀（仅需运行一次）
conda-unpack

# 5. 验证环境可用
python --version
conda --version
```

`conda-unpack` 脚本是 conda-pack 自动生成的，它会将所有文件中的前缀占位符替换为实际的解压路径 [F-038]。

## Python API 快速体验

conda-pack 也可以作为 Python 库使用：

### 基本打包

```python
from conda_pack import pack

# 打包当前激活环境
pack(output="my_env.tar.gz")

# 打包指定名称的环境
pack(name="my_env", output="my_env.tar.gz")

# 打包指定路径的环境
pack(prefix="/path/to/my_env", output="my_env.tar.gz")
```

### 使用 CondaEnv 对象（支持过滤）

```python
from conda_pack import CondaEnv

# 加载环境
env = CondaEnv.from_name("my_env")
print(f"环境路径: {env.prefix}")
print(f"文件数量: {len(env)}")

# 排除 .pyx 文件
env = env.exclude("*.pyx")

# 但重新包含 cytoolz 的 .pyx 文件
env = env.include("lib/python*/site-packages/cytoolz/*.pyx")

# 打包
env.pack(output="my_env_filtered.tar.gz")
```

### 指定目标前缀（跳过 conda-unpack）

如果预先知道目标路径，可以在打包时直接替换前缀，这样部署时不需要运行 conda-unpack：

```python
# 打包时直接重写前缀到 /opt/production/env
pack(
    prefix="/home/user/miniconda3/envs/my_env",
    output="/tmp/my_env.tar.gz",
    dest_prefix="/opt/production/env"
)
# 部署时解压到 /opt/production/env 即可直接使用，无需 conda-unpack
```

### 多线程压缩

```python
# 使用 4 线程压缩 gzip（默认单线程）
pack(name="my_env", output="my_env.tar.gz", n_threads=4)

# 使用所有 CPU 核心
pack(name="my_env", output="my_env.tar.gz", n_threads=-1)
```

### 显示进度

```python
# 命令行
# conda-pack -v  (默认显示进度)
# conda-pack -q  (静默模式)

# Python API
pack(name="my_env", output="my_env.tar.gz", verbose=True)
```

## 常见选项速查

| 选项 | 命令行 | Python API | 说明 |
|------|--------|-----------|------|
| 环境名 | `-n/--name` | `name=` | 按名称选择环境 |
| 环境路径 | `-p/--prefix` | `prefix=` | 按路径选择环境 |
| 输出文件 | `-o/--output` | `output=` | 输出文件路径 |
| 归档格式 | `--format` | `format=` | 归档格式选择 |
| 目标前缀 | `-d/--dest-prefix` | `dest_prefix=` | 预指定目标路径 |
| 压缩级别 | `--compress-level` | `compress_level=` | 0-9（zstd 支持到19） |
| 线程数 | `-j/--n-threads` | `n_threads=` | 压缩线程数，-1 表示全部 |
| 强制覆盖 | `-f/--force` | `force=True` | 覆盖已有输出文件 |
| 静默模式 | `-q/--quiet` | `verbose=False` | 不显示进度 |
| 排除文件 | `--exclude` | `filters=[('exclude', pattern)]` | 排除匹配文件 |
| 包含文件 | `--include` | `filters=[('include', pattern)]` | 包含被排除的文件 |
| 忽略可编辑包 | `--ignore-editable-packages` | `ignore_editable_packages=True` | 跳过 editable 包检查 |
| 忽略缺失文件 | `--ignore-missing-files` | `ignore_missing_files=True` | 跳过缺失文件检查 |

## 相关概念

- [conda-pack 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [CondaEnv 与 File 数据模型](03-conda-env-and-file.md)
