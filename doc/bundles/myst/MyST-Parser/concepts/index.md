# 概念文档（Concepts）

按学习路径排列的概念文档，从入门到深入。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | MyST-Parser 简介——定位、核心能力、三阶段架构 |
| [01-getting-started.md](01-getting-started.md) | 快速开始——安装、最小 conf.py、第一个 MyST 文档 |
| [02-myst-syntax-overview.md](02-myst-syntax-overview.md) | MyST 语法概览——CommonMark 基础、指令、角色、交叉引用 |

## 核心架构

| 文档 | 说明 |
|------|------|
| [03-architecture-pipeline.md](03-architecture-pipeline.md) | 三阶段解析管线——Markdown→Token→AST→输出 |
| [04-config-system.md](04-config-system.md) | 配置系统——MdParserConfig、自动注册、双层配置 |
| [05-extension-system.md](05-extension-system.md) | 扩展语法系统——18 个可选扩展详解 |
| [06-parser-and-renderer.md](06-parser-and-renderer.md) | 解析器与渲染器——create_md_parser、DocutilsRenderer/SphinxRenderer |

## 机制详解

| 文档 | 说明 |
|------|------|
| [07-directives-and-roles.md](07-directives-and-roles.md) | 指令与角色——语法、Mock 桥接、自定义指令注册 |
| [08-cross-references.md](08-cross-references.md) | 交叉引用——MystReferenceResolver、intersphinx、URL scheme |
| [09-slug-and-anchors.md](09-slug-and-anchors.md) | Slug 与锚点——三种 slug 预设、unique_slug、myst-anchors CLI |
| [10-cli-tools.md](10-cli-tools.md) | CLI 工具——myst-docutils-* 系列、Python API |

## Sphinx 集成

| 文档 | 说明 |
|------|------|
| [11-sphinx-integration.md](11-sphinx-integration.md) | Sphinx 集成机制——setup_sphinx 注册流程、事件连接 |
| [12-frontmatter.md](12-frontmatter.md) | YAML Frontmatter——文件级配置覆盖、html_meta、substitutions 合并 |
| [13-math-and-mathjax.md](13-math-and-mathjax.md) | 数学公式——dollarmath/amsmath、MathJax 自动配置 |
| [14-warning-system.md](14-warning-system.md) | 警告系统——MystWarnings 枚举、create_warning、抑制机制 |
| [15-docutils-standalone.md](15-docutils-standalone.md) | Docutils 独立使用——脱离 Sphinx 的 Python API 和 CLI |
