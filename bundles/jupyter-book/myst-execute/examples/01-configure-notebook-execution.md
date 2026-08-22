---
type: example
title: "构建时 Notebook 执行配置"
description: "展示 myst-execute 在 MyST 项目中配置构建时 Notebook 执行的各种方式，包括 frontmatter 配置、缓存控制、环境变量依赖和命令行参数"
tags: [myst-execute, configuration, build-time, cache, frontmatter, cli]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-execute-src.md"
    facts: [F-001, F-002, F-004, F-025, F-026, F-027, F-028, F-029, F-032, F-034, F-036, F-041]
related_concepts:
  - /concepts/00-execution-architecture.md
  - /concepts/01-myst-execute-kernel.md
  - /concepts/02-execution-cache.md
---

# 构建时 Notebook 执行配置

本示例展示如何在 MyST 项目中配置 myst-execute 插件，在构建时自动执行 Jupyter Notebook 中的代码块和内联表达式，并缓存结果以加速增量构建。

## 前置条件

- Node.js 18+ 环境
- MyST CLI（mystmd）已安装：`npm install -g mystmd`
- 本地或远程可访问的 Jupyter Kernel（如 `python3`）
- myst-execute 包作为 mystmd 依赖已安装（通常无需单独安装）

## 基本配置

### 1. 项目级配置（myst.yml）

在项目根目录的 `myst.yml` 中配置执行选项：

```yaml
# myst.yml
version: 1
project:
  title: "My Interactive Book"
  execute:
    timeout: 120           # 单个代码块执行超时（秒），默认 30 秒
    cache: ./_build/.cache  # 缓存目录路径
    # depends_on_env: []    # 默认不依赖环境变量
  kernels:
    python3:               # 内核名称（对应 jupyter kernelspec）
      name: python3
      display_name: Python 3
      language: python

site:
  # ... 站点配置
```

### 2. 文档级 frontmatter 配置

在单个 Markdown 文档的 YAML frontmatter 中覆盖项目级配置：

```markdown
---
title: "数据处理示例"
kernelspec:
  name: python3
  display_name: Python 3
execute:
  timeout: 60
  cache: true
  depends_on_env:
    - DATA_DATE        # 该代码执行依赖 DATA_DATE 环境变量
---
```

### 3. 代码块级标签

在代码块上使用 MyST 标签控制单个单元格的行为：

````markdown
```{code-cell} python3
:label: cell-imports
import pandas as pd
import numpy as np
```

```{code-cell} python3
:raises-exception:
# 这个单元格预期会抛出异常，不会导致构建失败
raise ValueError("This is expected")
```

```{code-cell} python3
:label: cell-data
df = pd.read_csv('data.csv')
df.head()
```
````

关键标签：
- `:raises-exception:` — 标记该单元格预期抛出异常，构建不会因错误中断
- `:label: cell-id` — 为单元格设置唯一标识符，用于交叉引用和缓存匹配

### 4. 内联表达式

使用 `{eval}` role 在正文中嵌入执行结果：

```markdown
数据集中共有 {eval}`len(df)` 行记录，
其中 {eval}`df['category'].nunique()` 个不同类别。
均值为 {eval}`df['value'].mean():.2f`。
```

内联表达式在构建时执行，其结果直接渲染到输出中。表达式语法与对应内核语言一致（Python 表达式）。

## 缓存配置详解

### 启用/禁用缓存

```markdown
---
execute:
  cache: true    # 启用缓存（默认）
---
```

设置 `cache: false` 将强制每次构建都重新执行所有代码块，不读取也不写入缓存。

```markdown
---
execute:
  cache: false   # 禁用缓存，每次重新执行
---
```

### 命令行控制缓存

```bash
# 正常构建（使用缓存）
myst build

# 忽略缓存，强制重新执行所有 Notebook
myst build --ignore-cache

# 清除缓存目录
rm -rf _build/.cache
```

### 环境变量依赖

当代码执行结果依赖环境变量时（如数据日期、API endpoint 等），配置 `depends_on_env` 使这些变量值参与缓存键计算：

```markdown
---
execute:
  depends_on_env:
    - DATA_DATE
    - API_ENV
---

```{code-cell} python3
import os
data_date = os.environ.get('DATA_DATE', '2024-01-01')
print(f"Loading data for {data_date}")
```
```

当 `DATA_DATE` 或 `API_ENV` 的值改变时，缓存自动失效并重新执行。未列入 `depends_on_env` 的环境变量不影响缓存键。

### 缓存目录结构

```
_build/.cache/
├── 4f8a2b...c3.json     # NotebookExecutionCache（ipynb 格式）
├── a1b2c3...d4.json     # ... 每个文档的缓存文件
└── ...
```

缓存文件名是基于 kernelSpec.name + 所有可执行节点内容 + 依赖环境变量计算的 MD5 哈希值。缓存文件是标准 Jupyter Notebook 格式（nbformat 4.5），可以直接用 Jupyter 打开查看。

## 内核配置

### 自动检测

myst-execute 会自动在系统中查找可用的 Jupyter 内核。如果文档 frontmatter 中指定了 `kernelspec.name`，则使用指定的内核；否则使用默认内核。

### 多内核支持

项目中可以同时使用多种内核，每个文档指定自己的内核：

```markdown
---
title: "R 统计分析"
kernelspec:
  name: ir
  display_name: R
---

```{code-cell} r
data <- c(1, 2, 3, 4, 5)
mean(data)
```
```

## 执行超时配置

### 项目级超时

```yaml
# myst.yml
project:
  execute:
    timeout: 300   # 全局默认 5 分钟超时
```

### 文档级超时

```markdown
---
execute:
  timeout: 600    # 本文档 10 分钟超时（适合耗时计算）
---
```

超时后内核连接会被中断，该单元格标记为执行失败。超时错误不会阻止后续单元格执行。

## 执行错误处理

### raises-exception 标签

预期会出错的代码块应标记 `:raises-exception:`：

````markdown
```{code-cell} python3
:raises-exception:
import nonexistent_module  # 这会失败，但构建继续
```
````

未标记 `:raises-exception:` 的单元格如果执行失败，会记录错误日志，输出区域显示错误信息，但构建不会中断（错误信息写入输出，不中断流程）。

### 执行中错误不写入缓存

无论是否有 `raises-exception:` 标签，只要执行过程中发生错误（errorOccurred=true），结果不会写入缓存，下次构建会重新尝试执行。只有全部成功执行的结果才会被缓存。

## 工作流示例

### 快速迭代开发

```bash
# 首次构建：执行所有代码，填充缓存
myst build

# 修改某个代码块后再次构建：只重新执行受影响的单元格
myst build

# 切换到完全重新执行（不使用缓存）
myst build --ignore-cache
```

### CI/CD 环境

```bash
# CI 中使用缓存目录持久化
# 1. 恢复缓存（如果有）
# 2. 构建
myst build
# 3. 保存缓存目录用于下次构建
```

在 CI 中，建议设置较长的超时时间：

```yaml
execute:
  timeout: 300
```

## 验证配置

构建成功后，在输出 HTML 中检查：
1. 代码块下方显示执行输出（文本、表格、图表等）
2. 内联表达式被替换为计算结果
3. 标记 `:raises-exception:` 的单元格显示错误堆栈而非构建失败
4. 二次构建使用缓存（日志中显示 "💾 Adding cached notebook outputs"）

## 相关文档

- [00-execution-architecture.md](/concepts/00-execution-architecture.md)：执行架构总览
- [01-myst-execute-kernel.md](/concepts/01-myst-execute-kernel.md)：内核管理机制
- [02-execution-cache.md](/concepts/02-execution-cache.md)：缓存系统详解
