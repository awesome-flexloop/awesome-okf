---
type: Example
title: CLI 工具独立使用
description: 使用 myst-docutils-* CLI 工具脱离 Sphinx 转换 Markdown 到 HTML/LaTeX/XML
tags: [myst, cli, docutils, standalone, html, latex, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## CLI 工具独立使用

本示例展示如何使用 myst-docutils-* 命令行工具脱离 Sphinx 独立转换 MyST Markdown。

## 基本转换

### 安装

```bash
pip install myst-parser
```

### Markdown 转 HTML5

```bash
# 转换单个文件到 stdout
myst-docutils-html5 input.md

# 转换并保存到文件
myst-docutils-html5 input.md output.html

# 从 stdin 读取
echo "# Hello" | myst-docutils-html5
```

### Markdown 转 LaTeX

```bash
myst-docutils-latex input.md output.tex
```

### Markdown 转 Pseudo-XML（调试）

```bash
myst-docutils-pseudoxml input.md
```

这会输出 docutils AST 的可视化表示，适合调试解析问题。

## 启用扩展语法

```bash
# 启用数学公式和冒号围栏
myst-docutils-html5 --myst-enable-extensions=dollarmath,amsmath,colon_fence input.md

# 启用所有常用扩展
myst-docutils-html5 \
  --myst-enable-extensions=dollarmath,amsmath,colon_fence,deflist,tasklist,linkify,smartquotes \
  --myst-heading-anchors=3 \
  input.md
```

## 标题锚点提取

```bash
# 提取 H1-H2 标题锚点
myst-anchors -l 2 input.md

# 使用 GitLab 风格 slug
myst-anchors --slug-func=gitlab input.md

# 输出到文件
myst-anchors -o anchors.html input.md
```

## HTML Body 片段（demo 模式）

`myst-docutils-demo` 只输出 HTML body 片段（无 `<html>`/`<head>`/`<body>` 包装），适合嵌入其他页面：

```bash
myst-docutils-demo input.md
```

输出示例：

```html
<section id="hello-world">
<h1>Hello World</h1>
<p>这是一个 <strong>MyST</strong> 文档。</p>
</section>
```

## Python API 调用

### 简单转换

```python
from docutils.core import publish_string
from myst_parser.parsers.docutils_ import Parser

def myst_to_html(markdown_text: str, **config) -> str:
    settings = {
        "output_encoding": "unicode",
        "myst_enable_extensions": ["dollarmath", "colon_fence"],
        "myst_heading_anchors": 3,
    }
    settings.update(config)
    return publish_string(
        markdown_text,
        parser=Parser(),
        writer_name="html5",
        settings_overrides=settings,
    )

html = myst_to_html("# Hello\n\n$E=mc^2$")
print(html)
```

### 仅 Body 片段

```python
from myst_parser.parsers.docutils_ import to_html5_demo

html_body = to_html5_demo(
    "# Hello\n\n:::{note}\n提示内容\n:::",
    myst_enable_extensions=["colon_fence"],
)
```

## docutils.conf 配置文件

创建 `docutils.conf` 文件，CLI 工具会自动读取：

```ini
[general]
myst_enable_extensions: dollarmath,colon_fence,deflist,tasklist
myst_heading_anchors: 3
myst_heading_slug_func: github

[myst parser]
myst_url_schemes: http,https,mailto
```

## 批量转换脚本

```python
#!/usr/bin/env python
"""批量将目录下所有 .md 文件转为 HTML"""
import sys
from pathlib import Path
from docutils.core import publish_file
from myst_parser.parsers.docutils_ import Parser

def convert_dir(input_dir: str, output_dir: str):
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    for md_file in in_path.glob("*.md"):
        html_file = out_path / (md_file.stem + ".html")
        print(f"Converting {md_file} -> {html_file}")
        with open(md_file, encoding="utf-8") as fin, \
             open(html_file, "w", encoding="utf-8") as fout:
            publish_file(
                source=fin,
                destination=fout,
                parser=Parser(),
                writer_name="html5",
                settings_overrides={
                    "myst_enable_extensions": ["dollarmath", "colon_fence"],
                    "myst_heading_anchors": 3,
                    "output_encoding": "unicode",
                },
            )

if __name__ == "__main__":
    convert_dir(sys.argv[1], sys.argv[2])
```

使用：

```bash
python convert.py ./markdown ./html
```

## 适用场景对比

| 场景 | 推荐工具 |
|------|---------|
| 单文件快速预览 | `myst-docutils-html5 file.md \| browser` |
| 批量转换 MD→HTML | Python API 脚本 |
| 嵌入到 Web 应用 | `to_html5_demo()` 函数 |
| 调试解析问题 | `myst-docutils-pseudoxml` |
| 提取文档目录 | `myst-anchors` |
| LaTeX 输出 | `myst-docutils-latex` |
| 完整文档站点 | Sphinx + myst_parser 扩展 |

## 相关概念

- [CLI 工具](../concepts/10-cli-tools.md)
- [Docutils 独立使用](../concepts/15-docutils-standalone.md)
- [快速开始](../concepts/01-getting-started.md)
