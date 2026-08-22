---
type: Concept
title: Docutils 独立使用
description: 不依赖 Sphinx 直接使用 MyST-Parser——Python API、CLI 工具、自定义 Writer
tags: [myst, docutils, standalone, cli, api, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## Docutils 独立使用

MyST-Parser 不仅是 Sphinx 扩展，也可以作为独立的 docutils 解析器使用，脱离 Sphinx 构建环境将 MyST Markdown 转换为 HTML、LaTeX、XML 等格式。

## 独立解析器类

`myst_parser.parsers.docutils_.Parser` 是独立 docutils 解析器，继承自 `docutils.parsers.rst.Parser`，不依赖 Sphinx。

与 Sphinx 版本的主要区别：

| 特性 | Sphinx 解析器 (MystParser) | Docutils 解析器 (Parser) |
|------|--------------------------|-------------------------|
| 基类 | `sphinx.parsers.Parser` | `docutils.parsers.rst.Parser` |
| 渲染器 | `SphinxRenderer` | `DocutilsRenderer` |
| 配置来源 | `app.env.myst_config` | `document.settings` (CLI/conf) |
| 引用解析 | `MystReferenceResolver`（Sphinx Post-Transform） | 基础引用（无 intersphinx） |
| Transforms | + Sphinx 内置 transforms | docutils 标准 transforms |
| 入口 | Sphinx 扩展 setup() | docutils publish_* / CLI |

## Python API 使用

### 基本转换

```python
from docutils.core import publish_string
from myst_parser.parsers.docutils_ import Parser

# 转 HTML5
output = publish_string(
    "# Hello MyST\n\n这是 **MyST Markdown** 文档。",
    parser=Parser(),
    writer_name="html5",
    settings_overrides={
        "output_encoding": "unicode",
    },
)
print(output)
```

### 启用扩展

```python
output = publish_string(
    "$E=mc^2$",
    parser=Parser(),
    writer_name="html5",
    settings_overrides={
        "myst_enable_extensions": ["dollarmath", "smartquotes"],
        "myst_heading_anchors": 3,
        "output_encoding": "unicode",
    },
)
```

### 使用 to_html5_demo（仅 body）

```python
from myst_parser.parsers.docutils_ import to_html5_demo

html_body = to_html5_demo("# Hello\n\nWorld")
# 返回 <section>...</section> 片段，无 HTML 框架
```

### 自定义配置

```python
from docutils.core import publish_cmdline
from myst_parser.parsers.docutils_ import Parser

publish_cmdline(
    parser=Parser(),
    writer_name="html5",
    description="MyST to HTML5 converter",
)
```

## CLI 工具使用

### 基本转换

```bash
# Markdown → HTML5
myst-docutils-html5 input.md output.html

# Markdown → LaTeX
myst-docutils-latex input.md output.tex

# Markdown → pseudo-XML（调试 AST）
myst-docutils-pseudoxml input.md
```

### 启用扩展

```bash
myst-docutils-html5 --myst-enable-extensions=dollarmath,colon_fence,deflist input.md
```

### 常用 CLI 选项

```bash
# 标题锚点
myst-docutils-html5 --myst-heading-anchors=3 --myst-heading-slug-func=github input.md

# 严格 CommonMark
myst-docutils-html5 --myst-commonmark-only input.md

# 代码块行号
myst-docutils-html5 --myst-number-code-blocks=python,javascript input.md

# 查看所有选项
myst-docutils-html5 --help
```

## docutils.conf 配置文件

可以通过 `docutils.conf` 文件设置默认配置：

```ini
[general]
myst_enable_extensions: dollarmath,colon_fence,tasklist
myst_heading_anchors: 3
myst_heading_slug_func: github

[myst parser]
myst_url_schemes: http,https,mailto
```

## 与 Sphinx 模式的功能差异

Docutils 独立模式下以下功能不可用（因为需要 Sphinx 环境）：

| 功能 | 原因 |
|------|------|
| intersphinx 跨项目引用 | 需要 Sphinx 的 InventoryAdapter |
| `sphinx.ext.*` 指令/角色 | 由 Sphinx 扩展注册 |
| Domain 系统（py:, js: 等） | Sphinx 特有 |
| 并行构建 | Sphinx 功能 |
| Builder 输出体系 | docutils 仅有内置 Writer |
| toctree 指令 | Sphinx 特有 |

## 创建自定义 Writer

可以基于 docutils 的 Writer 基类创建自定义输出格式：

```python
from docutils.writers import Writer
from myst_parser.parsers.docutils_ import Parser
from docutils.core import publish_string

class CustomWriter(Writer):
    def translate(self):
        # 遍历 doctree 生成自定义输出
        visitor = CustomTranslator(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body

output = publish_string(
    "# Test",
    parser=Parser(),
    writer=CustomWriter(),
    settings_overrides={"output_encoding": "unicode"},
)
```

## 适用场景

Docutils 独立模式适合：
- **快速预览**：无需完整 Sphinx 项目即可转换单个 Markdown 文件
- **CI/CD 流水线**：在 CI 中简单转换 Markdown 为 HTML
- **自定义输出格式**：基于 docutils Writer 体系创建自定义输出
- **嵌入式文档渲染**：在 Python 应用中嵌入 MyST 渲染功能
- **调试 AST**：通过 pseudo-XML 输出查看解析结果

对于完整的文档站点（多页面、交叉引用、主题、搜索），仍应使用 Sphinx 模式。

## 相关概念

- [CLI 工具](/concepts/10-cli-tools.md)
- [解析器与渲染器](/concepts/06-parser-and-renderer.md)
- [Sphinx 集成机制](/concepts/11-sphinx-integration.md)
- [CLI 工具实战示例](/examples/05-standalone-cli.md)
