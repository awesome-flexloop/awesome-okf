---
type: bundle
title: markdown-it-py 中文 Wiki
description: markdown-it-py（Python Markdown 解析器）完整中文教程，涵盖从入门到插件开发的全栈知识。markdown-it-py 是 Executable Books 生态解析核心层的核心组件，MyST-Parser 的依赖。
tags:
- python
- markdown
- parser
- commonmark
- executable-books
- myst
- markdown-it
bundle_id: myst/markdown-it-py
version: 4.2.0
source: "https://github.com/executablebooks/markdown-it-py"
prerequisites:
- mdurl
okf_version: '0.2'
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
---

# markdown-it-py 中文 Wiki

**markdown-it-py** 是 JavaScript 库 markdown-it 的 Python 移植版，版本 4.2.0，MIT 许可证。它提供 CommonMark 兼容的 Markdown 解析能力，通过插件系统支持 GFM 表格、删除线等扩展语法，是 [MyST-Parser](https://github.com/executablebooks/MyST-Parser) 的核心依赖。

- **版本**：4.2.0
- **Python 要求**：≥ 3.10
- **运行时依赖**：mdurl ~= 0.1
- **许可证**：MIT
- **源仓库**：<https://github.com/executablebooks/markdown-it-py>

## 快速导航

| 目录 | 内容 | 链接 |
|------|------|------|
| 📖 **概念文档** | 18篇，从入门到高级 | [concepts/index.md](concepts/index.md) |
| 💡 **示例文档** | 3篇，可运行代码 | [examples/index.md](examples/index.md) |
| 📚 **信源索引** | 源码映射、API速查 | [references/index.md](references/index.md) |
| 📋 **事实清单** | 120条可验证事实 | [spec/facts.md](spec/facts.md) |
| 🔍 **架构洞察** | 5个核心洞察+知识地图 | [spec/insights.md](spec/insights.md) |

## 前置依赖

阅读本 Wiki 前建议先了解：
- [mdurl Wiki](https://github.com/executablebooks/mdurl) — markdown-it-py 的唯一运行时依赖，负责 URL 解析/编码/解码

## 学习路径

### 🚀 入门（建议按顺序阅读）

1. [markdown-it-py 简介](concepts/00-introduction.md) — 是什么、特性、安装
2. [快速开始](concepts/01-getting-started.md) — parse/render、预设、自定义渲染
3. [预设与选项](concepts/02-presets-and-options.md) — 五种预设对比、选项配置

### 🔧 核心（理解解析器内部）

4. [Token 流模型](concepts/03-token-stream.md) — 解析结果的数据结构
5. [解析管线架构](concepts/04-parsing-pipeline.md) — Core→Block→Inline 三链协作
6. [Ruler 规则管理](concepts/05-ruler.md) — 规则添加/启用/排序/缓存
7. [StateBlock 块级解析状态](concepts/06-state-block.md) — 行偏移数组、Token输出
8. [StateInline 行内解析状态](concepts/07-state-inline.md) — pending缓冲、delimiters链表
9. [块级规则详解](concepts/08-block-rules.md) — 11条块级规则
10. [行内规则详解](concepts/09-inline-rules.md) — 12+4条行内规则
11. [渲染器详解](concepts/10-renderer.md) — Token→HTML渲染机制

### 🧠 高级（按需阅读）

12. [SyntaxTreeNode 语法树](concepts/11-syntax-tree-node.md) — Python树状视图扩展
13. [插件系统](concepts/12-plugin-system.md) — 编写自定义语法插件
14. [URL 与链接处理](concepts/13-url-and-link-processing.md) — 链接规范化与XSS防护
15. [通用工具函数](concepts/14-common-utilities.md) — HTML转义、实体、字符分类
16. [核心规则深入](concepts/15-core-rules-deep-dive.md) — 7条Core规则详解
17. [安全与 XSS 防护](concepts/16-security-and-xss.md) — 安全配置建议
18. [JS 兼容与 Python 扩展](concepts/17-migration-and-compatibility.md) — 与JS版差异

## 五分钟快速上手

```bash
pip install markdown-it-py
```

```python
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark")
html = md.render("# Hello, markdown-it-py!\n\nThis is **bold** and *italic*.")
print(html)
# <h1>Hello, markdown-it-py!</h1>
# <p>This is <strong>bold</strong> and <em>italic</em>.</p>
```

GFM 风格：
```python
md = MarkdownIt("gfm-like")  # 表格+删除线+自动链接
html = md.render("| a | b |\n|---|---|\n| 1 | 2 |\n\n~~done~~")
```

自定义渲染：
```python
md = MarkdownIt()
md.add_render_rule("link_open", lambda t,i,o,e,r: (
    t[i].attrSet("target", "_blank") or r.renderToken(t,i,o)))
```

## 核心架构概览

markdown-it-py 采用三链嵌套规则引擎架构：

1. **Core 链**（7条规则）：全局编排，负责换行规范化、块级调度、行内调度、后处理
2. **Block 链**（11条规则）：行驱动的块级解析，识别段落、标题、列表、代码块、表格等
3. **Inline 链**（12+4条规则）：字符驱动的行内解析，识别强调、链接、代码、图片等

解析结果是线性 Token 流（非 AST），通过 nesting（1/0/-1）表示开标签/自闭合/闭标签，level 表示嵌套深度，children 字段存储行内子元素。

```
src → normalize → block解析 → inline解析 → linkify/replacements/text_join
     → Token流 → Renderer → HTML
```

## 生态位置

```
MyST-Parser（MyST Markdown 解析器）
    ↓
mdit-py-plugins（扩展插件集） → markdown-it-py → mdurl（URL处理）
```

## 变更日志

见 [log.md](log.md)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
