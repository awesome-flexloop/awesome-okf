---
type: Example
title: 执行模式与缓存配置
description: 5 种执行模式的配置对比、jupyter-cache 使用、CI 场景配置、错误处理策略
tags: [myst-nb, execution, cache, ci, jupyter-cache]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 执行模式与缓存配置

本示例展示不同场景下的执行模式配置策略。

## 场景 1：本地开发（推荐 cache 模式）

```python
# conf.py
nb_execution_mode = "cache"
nb_execution_cache_path = ".jupyter_cache"
nb_execution_timeout = 120  # 本地开发可设长一些
nb_execution_in_temp = True  # 避免污染源码目录
```

cache 模式的优势：
- 代码不变不重复执行，构建速度快
- 缓存持久化到 `.jupyter_cache/` 目录
- 修改某个 notebook 后只重新执行该 notebook
- 适合频繁构建的开发场景

## 场景 2：首次构建 / 干净构建

```python
# conf.py
nb_execution_mode = "force"
nb_execution_timeout = 60
nb_execution_allow_errors = False
nb_execution_raise_on_error = True  # CI 中出错立即失败
```

force 模式强制重新执行所有 notebook，确保所有输出都是最新的。

## 场景 3：CI/CD 流水线

```python
# conf.py - CI 配置
import os

# CI 环境变量判断
if os.environ.get("CI"):
    nb_execution_mode = "cache"
    nb_execution_cache_path = ".jupyter_cache"
    nb_execution_timeout = 120
    nb_execution_raise_on_error = True
    nb_execution_show_tb = True  # CI 中显示 traceback 便于调试
else:
    nb_execution_mode = "auto"
    nb_execution_timeout = 60
```

### GitHub Actions 示例

```yaml
# .github/workflows/docs.yml
name: Build Docs
on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install myst-nb sphinx-book-theme ipykernel

      - name: Cache jupyter-cache
        uses: actions/cache@v4
        with:
          path: .jupyter_cache
          key: jupyter-cache-${{ hashFiles('**/*.ipynb', '**/*.md') }}

      - name: Build docs
        env:
          CI: "true"
        run: sphinx-build -b html docs docs/_build/html
```

## 场景 4：仅渲染不执行（输出已保存）

```python
# conf.py - 展示已有输出
nb_execution_mode = "off"
```

适用于：
- notebook 已经在 Jupyter 中执行完毕，outputs 已保存到 .ipynb
- 文档代码仅作示意，不需要执行
- 不需要 Jupyter kernel 环境（如纯文档服务器）

## 场景 5：允许错误的教程文档

```python
# conf.py - 教学文档（故意展示错误）
nb_execution_mode = "auto"
nb_execution_allow_errors = True  # 错误不中断构建
nb_output_stderr = "show"
```

在预期会出错的 cell 上使用 `raises-exception` 标签：

````markdown
```{code-cell}
:tags: [raises-exception]

1 / 0  # 故意演示 ZeroDivisionError
```
````

## 场景 6：内联求值（eval 模式）

```python
# conf.py - 需要 eval 内联求值
nb_execution_mode = "inline"
nb_eval_name_regex = r"^[a-zA-Z_][a-zA-Z0-9_]*$"  # 默认，仅允许变量名

# 放宽限制允许方法调用（谨慎使用）
# nb_eval_name_regex = r"^[a-zA-Z_][a-zA-Z0-9_.\[\]()]*$"
```

````markdown
数据集中有 {eval}`n_samples` 个样本，
准确率为 {eval}`accuracy:.2%`。
````

## 排除模式配置

```python
# 排除特定 notebook 不执行
nb_execution_excludepatterns = [
    "notebooks/slow_*.ipynb",     # 排除运行慢的 notebook
    "notebooks/drafts/*",         # 排除草稿
    "notebooks/*_solution.ipynb", # 排除答案
    "**/untitled*.ipynb",         # 排除临时文件
]
```

## Kernel 名称映射

```python
# 将不存在的 kernel 名映射到 python3
nb_kernel_rgx_aliases = {
    r"conda-env-.*-py": "python3",
    r"my-custom-kernel": "python3",
    r".*python.*": "python3",
}
```

## Cell 级执行配置

在单个 cell 上覆盖执行配置：

````markdown
```{code-cell}
---
mystnb:
  execution_timeout: 300  # 这个 cell 允许运行 5 分钟
---
# 长时间运行的训练代码
model.train(epochs=100)
```
````

跳过特定 cell 执行：

````markdown
```{code-cell}
:tags: [skip-execution]

# 这段代码不执行（如需要特定环境）
import gpu_only_library
```
````

## 执行统计表

MyST-NB 可以生成执行统计表，显示每个 notebook 的执行状态：

```markdown
```{nb-exec-table}
```
```

## 相关概念

- [执行模式与缓存](../concepts/05-execution-modes.md)
- [配置系统](../concepts/04-config-system.md)
- [代码隐藏与输出控制](../concepts/09-hiding-code.md)
- [基础配置示例](01-basic-setup.md)
