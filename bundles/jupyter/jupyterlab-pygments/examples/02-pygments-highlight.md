---
okf_version: "0.2"
type: example
title: "在 Jupyter 环境中使用 Pygments 高亮"
description: "在 Notebook 中使用 JupyterStyle 生成主题感知的高亮 HTML，结合 IPython.display 实现与编辑器一致的代码高亮。"
tags: [example, jupyter-notebook, pygments-html, ipython-display, nbconvert, theme-aware]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: style-py
    resource: "/references/style-py-source.md"
    title: "style.py 源码信源"
  - id: generate-css-py
    resource: "/references/generate-css-source.md"
    title: "generate_css.py 源码信源"
---

# 在 Jupyter 环境中使用 Pygments 高亮

本示例展示在 Jupyter Notebook/Lab 环境中如何使用 JupyterStyle 生成与 JupyterLab 主题一致的语法高亮 HTML。

## 示例 1：在 Notebook 中渲染主题感知的代码块

```python
"""在 Notebook 中展示使用 JupyterStyle 的语法高亮代码"""

from IPython.display import HTML, display
from pygments import highlight
from pygments.lexers import (
    PythonLexer, JavascriptLexer, HtmlLexer,
    get_lexer_by_name
)
from pygments.formatters import HtmlFormatter
from jupyterlab_pygments import JupyterStyle


def show_code(code: str, language: str = 'python'):
    """使用 JupyterStyle 高亮代码并在 Notebook 中显示"""
    lexer = get_lexer_by_name(language)
    formatter = HtmlFormatter(style=JupyterStyle)
    html = highlight(code, lexer, formatter)
    display(HTML(html))


# === Python 代码 ===
python_code = '''
import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataPoint:
    """表示一个数据点"""
    timestamp: float
    value: float
    label: Optional[str] = None

async def process_data(points: list[DataPoint]) -> dict:
    """异步处理数据点"""
    results = {}
    for point in points:
        if point.value > 0:
            await asyncio.sleep(0.01)  # 模拟异步操作
            results[point.label] = point.value * 2
    return results

# 错误示例
# results = process_data(None)  # AttributeError!
'''

show_code(python_code, 'python')
```

当你在 JupyterLab 中运行这段代码时，输出的代码块颜色会与 Notebook 编辑器中的颜色一致——切换浅色/深色主题后，刷新页面即可看到高亮颜色跟随变化。

## 示例 2：生成完整的 HTML 文档（含 CSS）

```python
"""生成包含 CSS 的完整 HTML 文档，可用于 nbconvert 导出或独立展示"""

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from jupyterlab_pygments import JupyterStyle

def generate_highlighted_html(code: str, title: str = "Code Example") -> str:
    """生成包含完整 CSS 的 HTML 文档"""
    formatter = HtmlFormatter(style=JupyterStyle)
    
    # 生成高亮 HTML
    highlighted_code = highlight(code, PythonLexer(), formatter)
    
    # 获取 CSS 样式
    css = formatter.get_style_defs('.highlight')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: var(--jp-cell-editor-background, white);
            color: var(--jp-mirror-editor-variable-color, #222);
        }}
        .highlight {{
            background: var(--jp-cell-editor-background, white);
            padding: 16px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        {css}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {highlighted_code}
</body>
</html>"""
    return html


code = '''
def fibonacci(n):
    """生成斐波那契数列"""
    a, b = 0, 1
    for _ in range(n):
        yield a  # 使用生成器
        a, b = b, a + b

# 使用示例
for num in fibonacci(10):
    print(num)
'''

html_doc = generate_highlighted_html(code, "Fibonacci Generator")
print(html_doc[:800])  # 打印前 800 字符

# 也可以保存到文件
# with open('highlighted_code.html', 'w') as f:
#     f.write(html_doc)
```

注意：在 JupyterLab 外部查看这个 HTML 时，`var(--jp-mirror-editor-*)` CSS 变量没有定义，会使用后备颜色（如 `color: #222`）。在 JupyterLab 内部查看时，变量由 JupyterLab 主题提供值。

## 示例 3：多语言代码高亮对比

```python
"""演示多种编程语言使用 JupyterStyle 的高亮效果"""

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from jupyterlab_pygments import JupyterStyle
from IPython.display import HTML, display

formatter = HtmlFormatter(style=JupyterStyle)

examples = {
    'python': '''
class Animal:
    def __init__(self, name: str, age: int = 0):
        self.name = name
        self.age = age

    def speak(self) -> str:
        raise NotImplementedError("Subclass must implement speak()")

class Dog(Animal):
    def speak(self):
        return f"{self.name} says: Woof!"
''',
    'javascript': '''
class Animal {
    constructor(name, age = 0) {
        this.name = name;
        this.age = age;
    }

    speak() {
        throw new Error("Subclass must implement speak()");
    }
}

class Dog extends Animal {
    speak() {
        return `${this.name} says: Woof!`;
    }
}
''',
    'html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Example Page</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1 class="title">Hello, World!</h1>
    <p>This is a <strong>demo</strong> page.</p>
    <script src="app.js"></script>
</body>
</html>
'''
}

for lang, code in examples.items():
    lexer = get_lexer_by_name(lang)
    html = highlight(code, lexer, formatter)
    display(HTML(f"<h3>{lang.capitalize()} Code</h3>{html}"))
```

## 示例 4：nbconvert 自定义模板中使用 JupyterStyle

在使用 `nbconvert` 将 Notebook 导出为 HTML 时，可以通过配置使用 JupyterStyle：

```python
"""nbconvert 配置：使用 JupyterStyle 作为代码高亮样式"""

# 在 jupyter_nbconvert_config.py 中配置
c = get_config()  # noqa

# 方法 1：指定 Pygments 样式名称（需要 JupyterStyle 已安装并注册）
c.HTMLExporter.highlight_class = 'highlight'
# 注意：JupyterStyle 使用 CSS 变量，nbconvert 默认导出的 HTML
# 在 JupyterLab 中查看时颜色匹配，在外部浏览器中需要额外引入 CSS 变量

# 方法 2：在自定义模板中注入 CSS
c.HTMLExporter.template_name = 'classic'
```

在自定义 HTML 模板中添加：

```html
<!-- 在模板的 <head> 中添加 JupyterStyle CSS -->
<style>
/* JupyterLab Pygments 主题 - CSS 变量由 JupyterLab 提供 */
{% for css_class, style in resources.css_highlighter.items() %}
.{{ css_class }} { {{ style }} }
{% endfor %}
</style>
```

## 关键注意事项

1. **CSS 变量的作用域**：JupyterStyle 生成的 CSS 依赖 `--jp-mirror-editor-*` 变量。在 JupyterLab/Notebook 中这些变量由主题系统自动提供；在外部 HTML 文件中需要自行定义。

2. **不依赖 Pygments 主题名称注册**：JupyterStyle 通过 Python 类直接使用（`HtmlFormatter(style=JupyterStyle)`），不需要通过 `pygments.styles.get_style_by_name()` 注册查找——这是通过 Pygments 的类直接传递方式实现的。

3. **背景色继承**：`.highlight` 的 `background-color` 使用 `var(--jp-cell-editor-background)`，确保代码块背景与 JupyterLab 编辑器一致。如果在 Notebook 输出中发现背景色不对，检查是否有其他 CSS 覆盖了 `.highlight` 样式。
