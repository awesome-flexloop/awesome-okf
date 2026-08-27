---
type: Example
title: CLI 工具独立使用
description: mystnb-docutils-*、mystnb-quickstart、mystnb-to-jupyter 命令的使用示例
tags: [myst-nb, cli, docutils, standalone, quickstart]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## CLI 工具独立使用

本示例展示如何使用 MyST-NB 的 CLI 工具脱离 Sphinx 独立使用。

## mystnb-quickstart：创建项目模板

```bash
# 创建一个新的 MyST-NB 项目
mystnb-quickstart my-docs
```

生成文件：
- `my-docs/conf.py`：包含所有 nb_* 配置项（注释形式）
- `my-docs/index.md`：包含 toctree 的首页
- `my-docs/notebook1.ipynb`：Jupyter Notebook 示例
- `my-docs/notebook2.md`：文本格式 Notebook 示例
- `my-docs/.gitignore`：排除 _build 和 .ipynb_checkpoints

### 选项

```bash
# 覆盖已存在的目录
mystnb-quickstart -o my-docs

# 详细输出
mystnb-quickstart -v my-docs
```

生成后用 Sphinx 构建：

```bash
cd my-docs
pip install sphinx sphinx-book-theme ipykernel
sphinx-build -b html . _build/html
```

## mystnb-to-jupyter：文本格式转 .ipynb

```bash
# 将 mystnb 文本格式 notebook 转为 Jupyter .ipynb
mystnb-to-jupyter notebook.md notebook.ipynb

# 自动推断输出路径（notebook.md → notebook.ipynb）
mystnb-to-jupyter notebook.md

# 覆盖已存在文件
mystnb-to-jupyter -o notebook.md notebook.ipynb
```

示例：转换分析文档

```bash
# 假设有 analysis.md
cat analysis.md
# ---
# file_format: mystnb
# kernelspec:
#   name: python3
# ---
#
# # 分析
#
# ```{code-cell}
# print("hello")
# ```

mystnb-to-jupyter analysis.md
# 生成 analysis.ipynb，可直接在 Jupyter 中打开
```

## mystnb-docutils-*：单文件转换

### 转换为 HTML5

```bash
# 基本转换（不执行代码）
mystnb-docutils-html5 --nb-execution-mode=off notebook.ipynb output.html

# 文本格式 .md 转 HTML5
mystnb-docutils-html5 --nb-execution-mode=off notebook.md output.html

# 启用 MyST 扩展
mystnb-docutils-html5 \
  --myst-enable-extensions=dollarmath,colon_fence,tasklist \
  --nb-execution-mode=off \
  notebook.md output.html
```

### 转换为 LaTeX

```bash
mystnb-docutils-latex --nb-execution-mode=off notebook.ipynb output.tex
```

### 转换为 Pseudo-XML（调试用）

```bash
# 输出 docutils AST 的 XML 表示，用于调试渲染问题
mystnb-docutils-pseudoxml --nb-execution-mode=off notebook.md
```

### 强制执行代码

```bash
# 注意：需要安装 ipykernel 且有可用的 Jupyter kernel
mystnb-docutils-html5 --nb-execution-mode=force notebook.ipynb output.html
```

### 从 stdin 读取

```bash
echo '---
file_format: mystnb
kernelspec:
  name: python3
---

# Test

\`\`\`{code-cell}
print("Hello from CLI")
\`\`\`' | mystnb-docutils-html5 --nb-execution-mode=off
```

## Python API 独立使用

### 简单转换

```python
from docutils.core import publish_string
from myst_nb.docutils_ import Parser

def nb_to_html(nb_content: str, source_path: str = "<string>", **config) -> str:
    """将 notebook 内容转为 HTML5 字符串。"""
    settings = {
        "output_encoding": "unicode",
        "nb_execution_mode": "off",
        "myst_enable_extensions": ["dollarmath", "colon_fence"],
    }
    settings.update(config)
    return publish_string(
        nb_content,
        source_path=source_path,
        parser=Parser(),
        writer_name="html5",
        settings_overrides=settings,
    )

# 转换文本格式 notebook
md_content = """\
---
file_format: mystnb
kernelspec:
  name: python3
---
# Hello

```{code-cell}
print("Hello World")
```
"""

html = nb_to_html(md_content)
print(html)
```

### 转换 .ipynb 文件

```python
from pathlib import Path
from docutils.core import publish_file
from myst_nb.docutils_ import Parser

def convert_ipynb_to_html(input_path: str, output_path: str):
    with open(input_path, encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        publish_file(
            source=fin,
            destination=fout,
            parser=Parser(),
            writer_name="html5",
            settings_overrides={
                "nb_execution_mode": "off",
                "output_encoding": "unicode",
            },
        )

convert_ipynb_to_html("notebook.ipynb", "output.html")
```

### 批量转换脚本

```python
#!/usr/bin/env python
"""批量将目录下所有 .ipynb/.md 转为 HTML。"""
import sys
from pathlib import Path
from docutils.core import publish_file
from myst_nb.docutils_ import Parser

def batch_convert(input_dir: str, output_dir: str):
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    for ext in ["*.ipynb", "*.md"]:
        for nb_file in in_path.glob(ext):
            # 检查 .md 是否为 mystnb 格式
            if ext == "*.md":
                content = nb_file.read_text(encoding="utf-8")
                if "file_format: mystnb" not in content.split("---")[1] if "---" in content[:50] else "":
                    continue

            html_file = out_path / (nb_file.stem + ".html")
            print(f"Converting {nb_file.name} -> {html_file.name}")

            with open(nb_file, encoding="utf-8") as fin, \
                 open(html_file, "w", encoding="utf-8") as fout:
                publish_file(
                    source=fin,
                    destination=fout,
                    source_path=str(nb_file),
                    parser=Parser(),
                    writer_name="html5",
                    settings_overrides={
                        "nb_execution_mode": "off",
                        "output_encoding": "unicode",
                        "myst_enable_extensions": ["dollarmath", "colon_fence"],
                    },
                )

if __name__ == "__main__":
    batch_convert(sys.argv[1], sys.argv[2])
```

## CLI 使用场景

| 场景 | 命令 |
|------|------|
| 快速创建项目 | `mystnb-quickstart my-docs` |
| 文本→ipynb 转换 | `mystnb-to-jupyter notebook.md` |
| CI 中快速预览 | `mystnb-docutils-html5 --nb-execution-mode=off nb.ipynb out.html` |
| 调试 AST 结构 | `mystnb-docutils-pseudoxml --nb-execution-mode=off nb.md` |
| LaTeX 输出 | `mystnb-docutils-latex --nb-execution-mode=off nb.ipynb out.tex` |
| 嵌入 Python 应用 | Python API（publish_string/publish_file） |

## 与 Sphinx 模式的功能对比

| 功能 | CLI/Docutils | Sphinx |
|------|-------------|--------|
| 单文件转换 | ✅ | ✅ |
| 多页面/TOC | ❌ | ✅ |
| 跨页面 glue | ❌ | ✅ |
| 主题/模板 | ❌（默认样式） | ✅ |
| intersphinx | ❌ | ✅ |
| 执行代码 | ⚠️ 需要 kernel | ✅ |
| 缓存执行 | ❌ | ✅ jupyter-cache |
| ipywidgets | ⚠️ 需手动加 JS | ✅ 自动加载 |

## 相关概念

- [Docutils 独立使用](../concepts/11-docutils-standalone.md)
- [快速开始](../concepts/01-getting-started.md)
- [MyST Notebook 文件格式](../concepts/02-notebook-format.md)
