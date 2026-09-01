---
type: Example
title: Markdown 集成示例
description: :markdown:和:markdownhelp:的使用方法、CommonMark支持的语法、代码块高亮、限制与替代方案
tags: [sphinx-argparse, example, markdown, CommonMark, markdownhelp]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:46:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:46:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# Markdown 集成示例

本示例展示如何在 sphinx-argparse 中使用 Markdown 格式编写帮助文本和嵌套内容。

## 安装依赖

Markdown 支持需要 CommonMark 库：

```bash
pip install "sphinx-argparse[markdown]"
# 或单独安装
pip install "CommonMark>=0.5.6"
```

## 在帮助文本中使用 Markdown

使用 `:markdownhelp:` 标志，让 argparse 的 `description`、`epilog` 和 `help` 字符串按 Markdown 解析：

```python
# mdbuild/cli.py
import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        prog='mdbuild',
        description="""
**mdbuild** 是一个现代化的构建工具。

## 功能特性

- 🔄 **增量构建** — 只重新构建变更的文件
- 📦 **多格式输出** — 支持 HTML、PDF、EPUB
- 🎨 **主题系统** — 内置多种主题，支持自定义
- ⚡ **并行构建** — 利用多核 CPU 加速

## 快速开始

```bash
mdbuild init my-project
cd my-project
mdbuild serve
```

访问 [项目文档](https://mdbuild.example.com) 了解更多。
""",
        epilog="""
---

> **提示**：使用 `mdbuild --help` 查看全局选项，
> `mdbuild <command> --help` 查看子命令帮助。
"""
    )
    parser.add_argument(
        '--output', '-o',
        default='./dist',
        help="""输出目录。
默认为 `./dist`。

支持以下路径格式：
- 相对路径：`./output`
- 绝对路径：`/var/www/html`
- 用户目录：`~/public_html`"""
    )
    parser.add_argument(
        '--format', '-f',
        choices=['html', 'pdf', 'epub', 'all'],
        default='html',
        help="""输出格式，可选值：

- `html` — **HTML** 格式（默认），适合网页浏览
- `pdf` — **PDF** 格式，适合打印
- `epub` — **EPUB** 电子书格式
- `all` — 生成所有格式"""
    )

    subparsers = parser.add_subparsers(dest='command')
    serve = subparsers.add_parser(
        'serve',
        help="""启动**开发服务器**，支持**热重载**。

```bash
mdbuild serve --port 8080
```

服务器启动后会自动打开浏览器。文件变更时自动刷新页面。"""
    )
    serve.add_argument('--port', '-p', type=int, default=3000,
                       help='服务器端口，默认 `3000`')
    serve.add_argument('--no-browser', action='store_true',
                       help='启动后**不**自动打开浏览器')

    return parser
```

对应的 RST 指令：

```rst
.. argparse::
   :module: mdbuild.cli
   :func: build_parser
   :prog: mdbuild
   :markdownhelp:
```

### 效果说明

`:markdownhelp:` 会将以下文本按 Markdown 解析：
- `description`（parser 描述）
- `epilog`（结尾文本）
- 每个选项的 `help` 字符串
- 每个子命令的 `help` 和 `description`

支持的 Markdown 语法包括：

| 语法 | 示例 | 效果 |
|------|------|------|
| 粗体 | `**粗体**` | **粗体** |
| 斜体 | `*斜体*` | *斜体* |
| 行内代码 | `` `code` `` | `code` |
| 代码块 | ```` ```bash ```` | 带语法高亮的代码块 |
| 链接 | `[文本](URL)` | 超链接 |
| 列表 | `- item` | 无序列表 |
| 标题 | `## 标题` | 二级标题 |
| 引用 | `> 引用` | 引用块 |
| 水平线 | `---` | 分隔线 |

## 嵌套内容使用 Markdown

使用 `:markdown:` 标志让指令体中的嵌套内容按 Markdown 解析：

```rst
.. argparse::
   :module: mdbuild.cli
   :func: build_parser
   :prog: mdbuild
   :markdown:

   # 开始使用

   mdbuild 是一个功能强大的文档构建工具。

   ## 安装

   ```bash
   pip install mdbuild
   ```

   ## 基本用法

   1. 初始化项目：`mdbuild init`
   2. 编写内容：编辑 `src/` 目录下的文件
   3. 构建：`mdbuild build`
   4. 预览：`mdbuild serve`

   > **注意**：嵌套内容的第一个标题必须是一级标题（`#`）。
```

**注意事项**：
- 第一个标题必须是一级标题（`#` 或 `====` 下划线式）
- 硬换行（行尾两个空格）因 Sphinx 预处理限制无法正确工作
- 嵌套内容使用 Markdown 时，无法使用 definition_list 内容增强（@before/@after等）

## 同时使用两种 Markdown 标志

`:markdown:` 和 `:markdownhelp:` 是独立的，可以同时使用：

```rst
.. argparse::
   :module: mdbuild.cli
   :func: build_parser
   :prog: mdbuild
   :markdown:         # 嵌套内容按 Markdown 解析
   :markdownhelp:     # 帮助文本按 Markdown 解析

   # 补充说明

   这是 **Markdown 格式** 的补充说明。
```

也可以只使用其中一个：

```rst
.. 只有帮助文本是Markdown，嵌套内容是RST
.. argparse::
   :module: mdbuild.cli
   :func: build_parser
   :prog: mdbuild
   :markdownhelp:

   这是 RST 格式的补充内容。
   这里可以使用 :ref:`交叉引用` 和其他 RST 特性。
```

```rst
.. 只有嵌套内容是Markdown，帮助文本是RST
.. argparse::
   :module: mdbuild.cli
   :func: build_parser
   :prog: mdbuild
   :markdown:

   # 补充说明
   这是 Markdown 格式。
```

## 代码块语法高亮

Markdown 代码块支持语言标注，会自动应用语法高亮：

```python
# 在help文本中使用带语言标注的代码块
parser.add_argument(
    '--filter',
    help="""结果过滤器，使用JMESPath表达式：

```python
# 过滤状态为active的用户
--filter "[?status=='active']"
```

```bash
# 命令行示例
mdbuild query --filter "name.contains('admin')"
```
"""
)
```

## 与 MyST-Parser 协同

如果你的项目已经在使用 MyST-Parser（.md 文件），推荐的做法是：

1. **CLI 文档保持 .rst 格式**：因为 `.. argparse::` 是 RST 指令
2. **使用 `:markdownhelp:`**：让 argparse 中的 help 文本支持 Markdown
3. **嵌套内容使用 RST**：这样可以使用完整的内容增强功能

```rst
.. cli.rst（RST文件）
.. argparse::
   :module: myapp.cli
   :func: build_parser
   :prog: myapp
   :markdownhelp:

   这是 RST 格式的补充内容，可以使用 :doc:`其他文档` 交叉引用、
   .. note:: 等RST指令、以及definition_list内容增强。

   serve
       serve 子命令用于启动开发服务器。
```

## 限制与替代方案

sphinx-argparse 的 Markdown 支持是精简实现，有以下限制：

| 限制 | 说明 | 替代方案 |
|------|------|----------|
| 不支持表格 | CommonMark 基础方言无表格 | 使用 RST 格式的嵌套内容添加表格 |
| 不支持 definition_list | 无法使用内容增强 | 需要增强时用 RST 格式 |
| 硬换行不可用 | 行尾空格被 Sphinx 去除 | 用空行分段 |
| 不支持 GFM 扩展 | 无任务列表、删除线等 | 使用 RST 格式 |
| 无脚注 | CommonMark 基础不支持 | 使用 RST |

对于需要完整 Markdown 功能的复杂文档，建议：
- argparse help 文本保持简洁，使用简单 Markdown
- 复杂的补充说明通过 RST 嵌套内容添加
- 或考虑使用 MyST-Parser 配合 eval-rst 嵌入 argparse 指令

## 相关概念

- [Markdown 支持](../concepts/07-markdown-support.md)
- [嵌套内容增强系统](../concepts/06-nested-content-enhancement.md)
- [基础用法完整示例](basic-usage.md)
