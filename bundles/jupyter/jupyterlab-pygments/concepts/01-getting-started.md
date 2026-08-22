---
okf_version: "0.2"
type: concept
title: "快速上手"
description: "安装 jupyterlab_pygments，验证扩展加载，并在 Python 中使用 JupyterStyle 生成主题感知的语法高亮 HTML。"
tags: [getting-started, installation, pip, conda, usage, quickstart, pygments-html]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/README.md"
    title: "README.md"
  - id: init-py
    resource: "/references/init-py-source.md"
    title: "__init__.py 源码信源"
  - id: style-py
    resource: "/references/style-py-source.md"
    title: "style.py 源码信源"
  - id: generate-css-py
    resource: "/references/generate-css-source.md"
    title: "generate_css.py 源码信源"
---

# 快速上手

本文档演示如何安装和使用 jupyterlab_pygments，从基础安装到在 JupyterLab 中体验主题感知的语法高亮。

## 安装

### 使用 conda 安装（推荐）

```bash
conda install -c conda-forge jupyterlab_pygments
```

### 使用 pip 安装

```bash
pip install jupyterlab_pygments
```

安装后，JupyterLab 前端扩展会自动注册——无需手动运行 `jupyter labextension install`，因为这是一个**预构建扩展（prebuilt extension）**，Python 包中已包含编译好的前端资源。

### 验证安装

安装后启动 JupyterLab：

```bash
jupyter lab
```

在 JupyterLab 中，可以通过以下方式验证扩展是否已加载：

1. 打开菜单栏 **Settings → Extension Manager**，确认 `jupyterlab_pygments` 在已安装列表中
2. 打开一个 Notebook，执行一段包含语法高亮输出的代码，观察高亮颜色是否跟随主题变化

## 在 Python 中使用 JupyterStyle

`JupyterStyle` 类是包的核心，可以在任何使用 Pygments 的场景中替代默认样式：

### 基础用法：生成主题感知的高亮 HTML

```python
"""使用 JupyterStyle 生成适配 JupyterLab 主题的高亮 HTML"""

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from jupyterlab_pygments import JupyterStyle

code = """
def fibonacci(n: int) -> int:
    \"\"\"计算斐波那契数列的第 n 项\"\"\"
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b  # 迭代计算
    return b
"""

# 使用 JupyterStyle 创建格式化器
formatter = HtmlFormatter(style=JupyterStyle)

# 生成高亮 HTML
html = highlight(code, PythonLexer(), formatter)

# 获取 CSS 样式定义
css = formatter.get_style_defs('.highlight')

print("=== 生成的 CSS（使用 CSS 变量）===")
for line in css.splitlines()[:10]:
    print(line)
```

输出的 CSS 将包含类似这样的规则：

```css
.highlight .k { color: var(--jp-mirror-editor-keyword-color); font-weight: bold }
.highlight .c { color: var(--jp-mirror-editor-comment-color); font-style: italic }
.highlight .s { color: var(--jp-mirror-editor-string-color) }
.highlight .m { color: var(--jp-mirror-editor-number-color) }
```

注意所有颜色值都是 `var(--jp-mirror-editor-*)` 格式——这些 CSS 变量由 JupyterLab 主题提供，切换主题时自动更新。

### 在 IPython/Jupyter 中自定义高亮

```python
"""在 Notebook 中临时切换代码高亮样式"""

from IPython.display import HTML, display
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from jupyterlab_pygments import JupyterStyle

code = "print('Hello, JupyterLab with Pygments!')"
formatter = HtmlFormatter(style=JupyterStyle)
html = highlight(code, PythonLexer(), formatter)
display(HTML(html))
```

## 开发者安装（从源码）

如需修改源码或贡献代码，以可编辑模式安装：

```bash
git clone https://github.com/jupyterlab/jupyterlab_pygments.git
cd jupyterlab_pygments

# 安装 Python 包（可编辑模式）
pip install -e .

# 安装 Node.js 依赖（需要 Node.js）
jlpm install

# 开发构建
jlpm build
```

### 重新生成 CSS

修改了 `JupyterStyle` 的 token 映射后，需要重新生成 CSS：

```bash
python generate_css.py
```

这会更新 `style/base.css` 文件，然后重新构建 labextension 即可生效：

```bash
jlpm build:lib && jlpm build:labextension:dev
```

## 版本检查

```python
import jupyterlab_pygments
print(f"版本: {jupyterlab_pygments.__version__}")
print(f"JupyterStyle 类: {jupyterlab_pygments.JupyterStyle}")
```

在开发模式下（未安装包时），`__version__` 将显示为 `"dev"`。

## 卸载

```bash
pip uninstall jupyterlab_pygments
# 或
conda remove jupyterlab_pygments
```

---

**下一步阅读：**
- [双桥架构解析](02-dual-bridge-architecture.md) — 理解 Python→CSS→JS 三层桥接设计
- [JupyterStyle 类详解](03-jupyter-style-class.md) — 深入 token 映射与 CSS 变量体系
- [CSS 生成流水线](04-css-generation-pipeline.md) — 理解 generate_css.py 的转换机制
