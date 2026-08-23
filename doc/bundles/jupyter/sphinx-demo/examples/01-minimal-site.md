---
type: Example
title: 最小可运行站点：从安装到构建
description: 从零创建一个包含 jupyterlite-sphinx 的最小 Sphinx 站点，包含完整的目录结构、配置文件和构建命令
tags: [minimal, quickstart, setup, tutorial]
difficulty: beginner
estimated_time: 10min
prerequisites:
  - Python 3.10+
  - pip 或 uv
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: minimal
    resource: /references/conf-py-source.md
    title: sphinx-demo 最小配置
---

## 目标

创建一个最小的 Sphinx 文档站点，嵌入一个可交互的 JupyterLite 环境。完成后你将能在浏览器中直接运行 Python 代码。

## 步骤 1：创建项目结构

```bash
mkdir my-jupyterlite-docs
cd my-jupyterlite-docs
mkdir -p docs/source/_static
```

最终目录结构：

```
my-jupyterlite-docs/
├── docs/
│   ├── Makefile
│   └── source/
│       ├── _static/
│       ├── conf.py
│       └── index.md
└── requirements.txt
```

## 步骤 2：创建 requirements.txt

```txt
sphinx>=7.0
jupyterlite-sphinx
jupyterlite-pyodide-kernel
pydata-sphinx-theme
myst-nb
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 步骤 3：创建 conf.py

在 `docs/source/conf.py` 中写入：

```python
project = "My JupyterLite Docs"
copyright = "2025, Your Name"
author = "Your Name"
release = "0.1.0"

extensions = [
    "jupyterlite_sphinx",
    "myst_nb",
]

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

# 启用 JupyterLite
jupyterlite_contents = []
```

这是最小配置——只包含 JupyterLite 核心扩展和 MyST Notebook 支持。

## 步骤 4：创建 index.md

在 `docs/source/index.md` 中写入：

````markdown
# 我的交互文档

欢迎！这是一个嵌入 JupyterLite 的 Sphinx 文档站点。

## 在浏览器中运行 Python

点击下方 Jupyter 环境，直接在浏览器中编写和运行 Python 代码：

```{jupyterlite}
:width: 100%
:height: 500px
```

## Try Examples 演示

当启用 `global_enable_try_examples` 后，docstring 中的示例会自动添加交互按钮。

以下代码可以直接在 Try Examples 中运行：

```python
def fibonacci(n):
    """Generate Fibonacci sequence up to n."""
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

print(fibonacci(10))
```
````

## 步骤 5：创建 Makefile

在 `docs/` 目录下创建 Makefile：

```makefile
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

%:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

或者直接使用 sphinx-quickstart 生成：

```bash
cd docs
sphinx-quickstart --sep -p "My JupyterLite Docs" -a "Your Name" -v 0.1.0 --ext-autodoc --no-makefile --no-batchfile source
```

但推荐手动创建以保持最小化。

## 步骤 6：构建站点

```bash
cd docs
make html
```

首次构建需要下载 Pyodide 运行时（约 20MB），耐心等待。构建成功后会看到：

```
build succeeded.

The HTML pages are in build/html.
```

## 步骤 7：预览

```bash
cd build/html
python -m http.server 8000
```

打开浏览器访问 `http://localhost:8000`，你将看到：
- 文档首页
- 嵌入的 JupyterLab 环境，可以直接创建 Notebook 运行 Python
- 如果配置了 TryExamples，代码示例旁会有"Try it online"按钮

> ⚠️ **必须通过 HTTP 服务器访问**，不能直接双击 HTML 文件。`file://` 协议会阻止 WebAssembly 加载。

## 验证清单

- [ ] 页面正常加载，无 404 错误
- [ ] JupyterLite iframe 显示 JupyterLab 界面
- [ ] 在 JupyterLab 中可以创建 Notebook 并执行 `print("Hello, JupyterLite!")`
- [ ] 浏览器控制台无 CORS 或 WASM 错误

## 扩展：启用 TryExamples

要让文档中的代码示例自动添加"Try it online"按钮，在 conf.py 中添加：

```python
extensions = [
    "jupyterlite_sphinx",
    "myst_nb",
    "sphinx.ext.autodoc",   # 添加 autodoc
    "numpydoc",             # 添加 numpydoc
]

global_enable_try_examples = True
try_examples_global_button_text = "在线运行"
```

然后创建一个 Python 模块（如 `docs/source/example.py`），编写带 NumPy 风格 Examples 节的 docstring：

```python
def greet(name):
    """Generate a greeting message.

    Parameters
    ----------
    name : str
        The name to greet.

    Returns
    -------
    str
        Greeting message.

    Examples
    --------
    >>> greet("World")
    'Hello, World!'
    """
    return f"Hello, {name}!"
```

在 index.md 中使用 automodule：

```rst
.. automodule:: example
   :members:
```

记得在 conf.py 中添加路径：

```python
import sys, os
sys.path.insert(0, os.path.abspath("."))
```

重新构建后，Examples 节旁边会出现"在线运行"按钮。

## 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| JupyterLite 区域空白 | file:// 协议打开 | 使用 http.server |
| 构建超时 | 首次下载 Pyodide | 等待或检查网络 |
| 按钮不出现 | numpydoc 未安装 | `pip install numpydoc` |
| 内核启动失败 | defaultKernelName 错误 | Pyodide 用 "python" |

## 下一步

- 阅读 [/concepts/03-sphinx-conf.md](/concepts/03-sphinx-conf.md) 了解更多配置选项
- 查看 [/examples/02-pyodide-setup.md](/examples/02-pyodide-setup.md) 学习完整 Pyodide 配置
- 阅读 [/concepts/06-try-examples.md](/concepts/06-try-examples.md) 深入了解交互示例
