---
type: Concept
title: 执行模式与缓存
description: 5 种执行模式（off/auto/force/cache/inline）的行为差异、jupyter-cache 缓存机制、排除模式、超时与错误处理
tags: [myst-nb, execution, cache, jupyter-cache, nbclient]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 执行模式与缓存

执行层是 MyST-NB 区别于 MyST-Parser 的核心，负责运行 notebook 中的代码 cell 并填充 outputs。MyST-NB 提供 5 种执行模式，适配不同的构建场景。

## 五种执行模式

### off 模式

```python
nb_execution_mode = "off"
```

**行为**：完全不执行代码，使用文件中已有的 outputs。

**适用场景**：
- notebook 已经在 Jupyter 中执行完毕，outputs 已保存
- CI 中不需要重新执行（节省时间）
- 展示性文档（代码仅作示意）

### auto 模式（默认）

```python
nb_execution_mode = "auto"
```

**行为**：
1. 检查所有代码 cell 是否有 outputs
2. 如果所有 cell 都有 outputs，跳过执行
3. 如果存在至少一个无 outputs 的 cell，执行整个 notebook

**适用场景**：
- 首次构建（执行所有代码）
- 修改了某个 cell 后重新构建（只重新执行有变更的 notebook——注意：是整个 notebook 执行，不是单个 cell）
- 本地开发默认模式

### force 模式

```python
nb_execution_mode = "force"
```

**行为**：强制重新执行所有 notebook，忽略已有 outputs。

**适用场景**：
- 数据/依赖更新后需要重新生成所有输出
- 发布前的干净构建
- 验证代码可复现性

### cache 模式

```python
nb_execution_mode = "cache"
nb_execution_cache_path = ".jupyter_cache"
```

**行为**：使用 jupyter-cache 缓存执行结果：
1. 计算 notebook 内容的哈希
2. 如果缓存中有匹配的结果，直接复用 outputs
3. 如果缓存未命中，执行 notebook 并存入缓存

**适用场景**：
- 本地开发频繁构建（代码不变不重复执行）
- CI 流水线（缓存可持久化）
- 大型项目缩短构建时间

**缓存路径**：
- 默认为 Sphinx 构建目录的父目录下 `.jupyter_cache/`
- 可通过 `nb_execution_cache_path` 自定义
- 缓存在不同构建之间持久存在

### inline 模式

```python
nb_execution_mode = "inline"
```

**行为**：启动持久 Jupyter kernel，支持在文档正文中通过 `{eval}` 角色内联求值变量。

**适用场景**：
- 需要在 Markdown 句子中嵌入动态计算值
- 交互式文档

**注意**：inline 模式会保持 kernel 运行，构建结束后关闭。

## 执行客户端架构

```
NotebookClientBase (基类，不执行)
    ├── NotebookClientDirect (直接执行 - nbclient)
    │     └── 调用 nbclient.NotebookClient.execute()
    ├── NotebookClientCache (缓存执行 - jupyter-cache)
    │     └── jupyter_cache 缓存命中/执行/存储
    └── NotebookClientInline (内联执行 - eval)
          └── 持久 kernel 连接，eval_variable()
```

`create_client()` 工厂函数（`core/execute/__init__.py` L19-81）根据 `execution_mode` 分发到对应客户端。

## 排除执行

使用 `nb_execution_excludepatterns` 排除特定文件：

```python
nb_execution_excludepatterns = [
    "notebooks/slow_*.ipynb",     # 排除慢 notebook
    "notebooks/drafts/*",         # 排除草稿
    "**/skip_*.md",              # 跳过特定文件
]
```

使用 POSIX glob 模式匹配文件路径。

## 超时控制

```python
nb_execution_timeout = 60  # 默认 30 秒
```

单个 cell 的最大执行时间（秒）。超时后 cell 会被标记为超时错误。

也可在 cell 级别覆盖：
````markdown
```{code-cell}
---
mystnb:
  execution_timeout: 120
---
# 这个 cell 允许运行 2 分钟
import time
time.sleep(60)
```
````

## 错误处理

### 允许错误

```python
nb_execution_allow_errors = True  # 默认 False
```

允许执行过程中的错误，错误信息会作为输出渲染（红色 traceback），而不是中断构建。

Cell 级别：
````markdown
```{code-cell}
:tags: [raises-exception]

1 / 0  # 预期会报错
```
````

### 错误时抛异常

```python
nb_execution_raise_on_error = True  # 默认 False
```

执行失败时抛出异常，中断构建（CI 中推荐开启）。

### 显示 traceback

```python
nb_execution_show_tb = True  # 默认 False
```

执行出错时将完整 traceback 打印到 stderr（调试时有用）。

## 临时目录执行

```python
nb_execution_in_temp = True  # 默认 False
```

在临时目录中执行 notebook（cwd 为临时目录），避免执行过程中产生的文件污染源码目录。

## Kernel 名称映射

```python
nb_kernel_rgx_aliases = {
    "conda-env-.*-py": "python3",
    "my-custom-kernel": "python3",
}
```

使用正则映射 kernel 名称。当 notebook 指定了特定 kernel 但构建环境中不存在时，可以映射到可用的 kernel。

## 执行统计表

MyST-NB 自动生成执行统计表，显示每个 notebook 的执行状态和耗时。启用 `nb_execution_mode` 后，可通过 `{nb-exec-table}` 指令插入统计表。

## 相关概念

- [四阶段处理管线](03-processing-pipeline.md)
- [配置系统](04-config-system.md)
- [Eval 内联求值](08-eval.md)
- [代码隐藏与输出控制](09-hiding-code.md)
- [执行模式配置示例](/examples/02-execution-config.md)
