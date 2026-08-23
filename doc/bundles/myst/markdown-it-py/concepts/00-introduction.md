---
type: Concept
title: markdown-it-py 简介
description: markdown-it-py 是 JavaScript markdown-it 的 Python 移植版，CommonMark 兼容的 Markdown 解析器，通过插件系统提供可扩展语法支持
tags:
- markdown-it-py
- markdown
- parser
- commonmark
- introduction
difficulty: 入门
estimated_time: 10分钟
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# markdown-it-py 简介

## 它是什么

markdown-it-py 是 JavaScript 库 [markdown-it](https://github.com/markdown-it/markdown-it) 的 Python 移植版本，版本号 4.2.0，许可证 MIT，要求 Python ≥ 3.10。它将 Markdown 文本解析为结构化的 Token 流，再渲染为 HTML，默认严格遵循 CommonMark 规范，并通过插件系统支持 GFM 表格、删除线、任务列表、告警块等扩展语法。

```python
from markdown_it import MarkdownIt

md = MarkdownIt()
html = md.render("# Hello, World!\n\nThis is **Markdown**.")
print(html)
# <h1>Hello, World!</h1>
# <p>This is <strong>Markdown</strong>.</p>
```

markdown-it-py 是 Executable Books 生态中 [MyST-Parser](https://github.com/executablebooks/MyST-Parser)（MyST Markdown 语法的解析器）的核心依赖。

## 核心特性

- **CommonMark 兼容**：通过 CommonMark 测试套件（550+ 测试用例），默认 `commonmark` 预设严格遵循规范
- **可配置预设**：内置五种预设（zero/commonmark/default/gfm-like/gfm-like2），支持细粒度规则启用/禁用
- **插件系统**：通过 `use()` 方法加载插件，插件可添加新语法规则和自定义渲染
- **Token 流模型**：解析结果是线性 Token 序列而非 AST，性能优秀且易于流式处理
- **语法树视图**：Python 端额外提供 `SyntaxTreeNode` 类，将 Token 流转换为树状结构方便遍历
- **HTML 安全**：默认 `commonmark` 预设允许 HTML（XHTML输出），可通过 `html=False` 禁用；内置 XSS 链接验证
- **CLI 工具**：提供 `markdown-it` 命令行工具，支持文件/STDIN/交互模式

## 生态位置

markdown-it-py 在 Executable Books 生态中处于解析核心层：

| 依赖/被依赖 | 关系 | 说明 |
|-------------|------|------|
| mdurl | 依赖 | URL 解析/格式化/编解码（运行时唯一依赖） |
| MyST-Parser | 被依赖 | MyST Markdown 解析器，基于 markdown-it-py 构建 |
| mdit-py-plugins | 配套插件集 | 提供脚注、定义列表、缩写、dollarmath等扩展 |

```
MyST-Parser
    ↓ uses
mdit-py-plugins → markdown-it-py → mdurl
```

## 与 JavaScript markdown-it 的关系

markdown-it-py 是 markdown-it JS 版的逐行移植，核心架构、规则系统、Token 模型与 JS 版一致：
- 相同的三链解析架构（Core→Block→Inline）
- 相同的 Ruler 规则管理和 Plugin 机制
- 相同的 Token 字段设计（attrs 除外——Python 端使用 `dict` 而非 `list of [key, value]` 对，`Token.as_dict(as_upstream=True)` 可转换为上游格式）
- Python 端额外特性：`SyntaxTreeNode` 语法树视图、`store_labels` 选项、`tree_depth_first` 迭代器

## 安装

```bash
pip install markdown-it-py
```

仅有的运行时依赖是 `mdurl~=0.1`，无需编译扩展。

```bash
# 带链接自动识别
pip install markdown-it-py[linkify]

# 安装所有额外功能
pip install markdown-it-py[plugins]
```

## 下一步

- [快速开始](01-getting-started.md)：实例化、解析、渲染的完整流程
- [预设与选项](02-presets-and-options.md)：五种预设的选择与选项配置
- [Token 流模型](03-token-stream.md)：理解解析结果的核心数据结构
