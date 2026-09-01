---
type: Concept
title: CLI 工具
description: myst-docutils-* 系列命令行工具和 myst-anchors 的用法
tags: [myst, cli, docutils, command-line, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## CLI 工具

MyST-Parser 提供了 7 个命令行工具，基于 docutils 的 `publish_cmdline` 框架，可以脱离 Sphinx 独立将 MyST Markdown 转换为多种输出格式。

## CLI 命令列表

| 命令 | 输出格式 | 说明 |
|------|---------|------|
| `myst-docutils-html` | HTML (XHTML) | 完整 HTML 文档 |
| `myst-docutils-html5` | HTML5 | HTML5 文档 |
| `myst-docutils-demo` | HTML5 body | 仅 HTML body 片段（演示用） |
| `myst-docutils-latex` | LaTeX | LaTeX 文档 |
| `myst-docutils-xml` | docutils XML | docutils 原生 XML |
| `myst-docutils-pseudoxml` | pseudo-XML | 可视化 AST（调试用） |
| `myst-anchors` | HTML | 提取标题锚点 |
| `myst-inv` | - | Sphinx inventory 文件操作 |

## 基本用法

所有 `myst-docutils-*` 命令遵循 docutils CLI 通用格式：

```bash
myst-docutils-html [options] [<source> [<destination>]]
```

### 转换单个文件

```bash
# 输出到 stdout
myst-docutils-html5 input.md

# 输出到文件
myst-docutils-html5 input.md output.html

# 从 stdin 读取
echo "# Hello" | myst-docutils-html5
```

## 常用选项

### MyST 特定选项

```bash
# 启用扩展语法
myst-docutils-html5 --myst-enable-extensions=dollarmath,colon_fence input.md

# 设置标题锚点深度
myst-docutils-html5 --myst-heading-anchors=3 input.md

# 指定 slug 函数
myst-docutils-html5 --myst-heading-slug-func=github input.md

# 设置 URL schemes
myst-docutils-html5 --myst-url-schemes=http,https,mailto input.md

# 严格 CommonMark 模式
myst-docutils-html5 --myst-commonmark-only input.md

# 抑制特定警告
myst-docutils-html5 --myst-suppress-warnings=myst.xref_missing input.md
```

### Docutils 通用选项

```bash
# 指定配置文件
myst-docutils-html5 --config=docutils.conf input.md

# 设置标题级别
myst-docutils-html5 --initial-header-level=2 input.md

# 不生成 XML 声明
myst-docutils-html5 --no-xml-declaration input.md

# 查看帮助
myst-docutils-html5 --help
```

## myst-docutils-demo

`myst-docutils-demo` 是一个特殊命令，使用 `SimpleWriter` 和 `SimpleTranslator` 仅输出 HTML body 内容（不包含 `<html>`、`<head>`、`<body>` 框架），适合在网页中嵌入预览：

```bash
myst-docutils-demo input.md
```

输出仅包含正文 HTML 片段，如：

```html
<section id="hello">
<h1>Hello</h1>
<p>World</p>
</section>
```

### Python API 调用

```python
from myst_parser.parsers.docutils_ import to_html5_demo

html = to_html5_demo("# Hello\n\nWorld")
print(html)
```

## myst-anchors

`myst-anchors` 专门用于提取 Markdown 文件中的标题及其锚点：

```bash
# 提取 H1-H2 的锚点
myst-anchors -l 2 input.md

# 使用 gitlab slug
myst-anchors --slug-func=gitlab input.md

# 输出到文件
myst-anchors -o anchors.html input.md
```

## Python API 转换

```python
from docutils.core import publish_string
from myst_parser.parsers.docutils_ import Parser

# 转 HTML5
output = publish_string(
    "# Hello\n\nWorld",
    parser=Parser(),
    writer_name="html5",
    settings_overrides={
        "myst_enable_extensions": ["dollarmath"],
        "myst_heading_anchors": 3,
        "output_encoding": "unicode",
    },
)
```

## docutils.conf 配置

CLI 工具也支持通过 `docutils.conf` 文件配置：

```ini
[myst parser]
myst_enable_extensions: dollarmath,colon_fence,deflist
myst_heading_anchors: 3
myst_heading_slug_func: github
```

## 相关概念

- [快速开始](01-getting-started.md)
- [Docutils 独立使用](15-docutils-standalone.md)
- [配置系统](04-config-system.md)
- [CLI 工具使用示例](../examples/05-standalone-cli.md)
