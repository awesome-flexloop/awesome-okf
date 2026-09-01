---
type: "example"
title: "文件过滤与环境定制"
description: 使用 --include/--exclude 过滤文件，使用 Python API 的 filters 参数精确控制打包内容，处理可编辑包和缺失文件。
tags: [conda-pack, filtering, exclude, include, editable-packages, filters]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: core
    resource: /references/core-source.md
    title: core.py 核心模块源码
---

# 文件过滤与环境定制

conda-pack 提供灵活的文件过滤机制，可以精确控制哪些文件被包含在归档中。这对于减小包体积、排除测试文件、清理缓存非常有用。

## 过滤规则语法

过滤规则遵循 gitignore 风格，支持 glob 模式匹配：

| 模式 | 匹配 |
|------|------|
| `*.pyc` | 所有 .pyc 文件（任何目录） |
| `__pycache__/` | 所有 __pycache__ 目录 |
| `tests/` | 所有 tests 目录 |
| `lib/python*/site-packages/*/tests/` | site-packages 下的 tests 目录 |
| `bin/conda*` | bin 目录下以 conda 开头的文件 |

> 注意：过滤是按顺序应用的，`--exclude` 和 `--include` 交错出现时，后面的规则可以覆盖前面的。

## CLI 示例

### 排除字节码和缓存

```bash
conda-pack -n my_env \
  --exclude '*.pyc' \
  --exclude '__pycache__' \
  --exclude '*.pyo' \
  -o my_env.tar.gz
```

### 排除测试和文档

```bash
conda-pack -n my_env \
  --exclude '*/tests/*' \
  --exclude '*/test/*' \
  --exclude '*/doc/*' \
  --exclude '*/docs/*' \
  -o my_env.tar.gz
```

### 排除但保留特定包的测试

```bash
# 先排除所有 tests，再 include 特定包的 tests
conda-pack -n my_env \
  --exclude '*/tests/*' \
  --include 'lib/python*/site-packages/numpy/tests/*' \
  -o my_env.tar.gz
```

### 排除 conda 缓存和元数据冗余

```bash
conda-pack -n my_env \
  --exclude 'conda-meta/history' \
  --exclude 'bin/conda' \
  --exclude 'bin/activate' \
  -o minimal_env.tar.gz
```

## Python API 示例

### 基础过滤

```python
from conda_pack import pack

# filters 参数是 (action, pattern) 元组列表，按顺序应用
pack(
    name="my_env",
    output="/tmp/my_env.tar.gz",
    filters=[
        ("exclude", "*.pyc"),
        ("exclude", "__pycache__"),
        ("exclude", "*.pyo"),
    ],
)
```

### 复杂过滤链

```python
pack(
    name="my_env",
    output="/tmp/production_env.tar.gz",
    filters=[
        # 排除所有缓存和字节码
        ("exclude", "*.pyc"),
        ("exclude", "*.pyo"),
        ("exclude", "__pycache__"),
        ("exclude", "*.egg-info"),
        # 排除测试
        ("exclude", "*/tests/*"),
        ("exclude", "*/test/*"),
        # 排除文档
        ("exclude", "*/doc/*"),
        ("exclude", "*/docs/*"),
        # 排除 git 相关
        ("exclude", ".git*"),
        # 保留 numpy 的测试（可能被依赖）
        ("include", "lib/python*/site-packages/numpy/tests/*"),
        # 排除 man pages 和 locale
        ("exclude", "share/man/*"),
        ("exclude", "share/doc/*"),
    ],
)
```

### 使用 CondaEnv 对象进行更精细的控制

```python
from conda_pack import CondaEnv

# 先加载环境
env = CondaEnv.from_name("my_env")

# 查看文件数量
print(f"总文件数: {len(env.files)}")

# 按包名过滤：只包含特定包
env = env.include(packages=["numpy", "pandas", "scikit-learn"])

# 按包名排除：排除特定包
env = env.exclude(packages=["pytest", "ipython"])

# 按模式过滤
env = env.exclude(
    patterns=[
        "*.pyc",
        "__pycache__",
        "*/tests/*",
    ]
)

# 链式调用
env = (CondaEnv.from_name("my_env")
       .exclude(packages=["pytest"])
       .exclude(patterns=["*.pyc", "__pycache__"])
       .exclude(patterns=["*/tests/*"]))

# 最后打包
env.pack(output="/tmp/filtered_env.tar.gz")
```

### 按文件类型分析

```python
from conda_pack import CondaEnv
from collections import Counter

env = CondaEnv.from_name("my_env")

# 统计文件类型分布
ext_counter = Counter()
for f in env.files:
    if f.target.endswith('.py'):
        ext_counter['.py'] += 1
    elif f.target.endswith('.so'):
        ext_counter['.so'] += 1
    elif f.target.endswith('.pyc'):
        ext_counter['.pyc'] += 1
    else:
        ext_counter['other'] += 1

print(ext_counter)
```

## 处理可编辑包

### 检测可编辑包

```bash
# 可编辑包会导致打包失败，错误信息会列出违规包
conda-pack -n my_env
# CondaPackError: Cannot pack an environment with editable packages
# installed (e.g. from `pip install -e`). Editable packages found:
# - my_custom_package
```

### 方案1：忽略可编辑包（不推荐）

```bash
conda-pack -n my_env --ignore-editable-packages
```

仅当你确认可编辑包不影响运行时使用，否则部署后可能缺失模块。

### 方案2：重新安装为非可编辑模式（推荐）

```bash
conda activate my_env
pip uninstall my_custom_package -y
pip install /path/to/my_custom_package  # 不加 -e 参数
conda-pack -n my_env
```

## 处理缺失文件

### 什么是缺失文件？

conda-meta 中记录的文件在实际文件系统中不存在（通常是 pip 覆盖或卸载了 conda 安装的包）。

### 默认行为：报错

```bash
conda-pack -n my_env
# CondaPackError:
# - numpy-1.24.0-py310h...
#   lib/python3.10/site-packages/numpy/__init__.py
```

### 忽略缺失文件

```bash
conda-pack -n my_env --ignore-missing-files
```

这会跳过缺失的文件，继续打包。适用于已知缺失文件不影响核心功能的场景。

```python
pack(name="my_env", ignore_missing_files=True, output="/tmp/my_env.tar.gz")
```

## 体积优化示例：最小化生产环境包

```bash
conda-pack -n my_env \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '__pycache__' \
  --exclude '*.egg-info' \
  --exclude '*/tests/*' \
  --exclude '*/test/*' \
  --exclude '*/doc/*' \
  --exclude '*/docs/*' \
  --exclude 'share/man/*' \
  --exclude 'share/doc/*' \
  --exclude '.git*' \
  --exclude 'bin/conda' \
  --exclude 'bin/conda-env' \
  --compress-level 9 \
  -j -1 \
  -o production_minimal.tar.gz
```

典型效果：可以将 1GB+ 的环境压缩到 300-500MB，具体取决于环境内容。

## 相关概念

- [CondaEnv 与 File 数据模型](../concepts/03-conda-env-and-file.md)
- [环境加载与文件收集](../concepts/04-environment-loading.md)
