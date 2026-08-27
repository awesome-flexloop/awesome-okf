---
type: Reference
title: MyST-Parser 源码路径映射
description: MyST-Parser 核心源文件路径、职责与关键代码位置索引
tags: [myst, sphinx, parser, source, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-repo
    resource: https://github.com/executablebooks/MyST-Parser
    title: MyST-Parser GitHub Repository
---

# MyST-Parser 源码路径映射

本文档为 MyST-Parser 源码的文件级索引，标注每个核心文件的路径、职责和关键代码。源路径相对于 `external/libs/ai/executablebooks/MyST-Parser/`。

## 核心文件清单

| 文件 | 职责 | 关键代码 |
|------|------|---------|
| `myst_parser/__init__.py` | 包入口，Sphinx setup() 函数 | `setup()` L9-14：调用 setup_sphinx |
| `myst_parser/config/main.py` | MdParserConfig 数据类、验证器、frontmatter | `MdParserConfig` L184-539、`check_extensions()` L25-53、`merge_file_level()` L542-599、`read_topmatter()` L606-639 |
| `myst_parser/parsers/mdit.py` | markdown-it-py 解析器工厂 | `create_md_parser()` L37-146：插件装配、扩展按需加载 |
| `myst_parser/parsers/sphinx_.py` | Sphinx 解析器类 | `MystParser` L30-87：parse() 方法流程 |
| `myst_parser/parsers/docutils_.py` | Docutils 独立解析器与 CLI | `Parser` L237-342、`cli_html/html5/latex/xml/pseudoxml` L377-437 |
| `myst_parser/mdit_to_docutils/base.py` | Token→docutils AST 渲染器基类 | `DocutilsRenderer` L98+：render_* 方法族、setup_render() |
| `myst_parser/mdit_to_docutils/sphinx_.py` | Sphinx 专用渲染器 | `SphinxRenderer` L25+：render_link_project()、pending_xref 生成 |
| `myst_parser/mdit_to_docutils/transforms.py` | Docutils Transforms | AddSlugIds、CollectFootnotes、SortFootnotes、ResolveAnchorIds |
| `myst_parser/sphinx_ext/main.py` | Sphinx 扩展注册入口 | `setup_sphinx()` L20-68：config/parser/directive/role/transform 注册 |
| `myst_parser/sphinx_ext/myst_refs.py` | MyST 引用解析 Post-Transform | `MystReferenceResolver` L31+：跨文档、intersphinx 引用解析 |
| `myst_parser/sphinx_ext/directives.py` | 自定义指令和角色 | `FigureMarkdown` L40-137、`SubstitutionReferenceRole` L27-37 |
| `myst_parser/sphinx_ext/mathjax.py` | MathJax 配置覆盖 | override_mathjax() 函数 |
| `myst_parser/warnings_.py` | 警告类型枚举与创建函数 | `MystWarnings` L11-68、`create_warning()` L96-159 |
| `myst_parser/slugs.py` | 标题锚点 slug 生成 | `SLUG_PRESETS` L139-143、三种 slugify 函数 |
| `myst_parser/cli.py` | myst-anchors CLI | `print_anchors()` L13-53 |
| `myst_parser/mocking.py` | Docutils Mock 对象 | MockState、MockInliner、MockStateMachine 等 |
| `myst_parser/inventory.py` | Sphinx inventory 处理 | intersphinx 引用过滤 |
| `myst_parser/_docs.py` | 文档构建辅助指令 | MystConfigDirective、MystLexer 等 |
| `myst_parser/_compat.py` | Python 版本兼容 | findall 等兼容函数 |

## 配置项完整列表（myst_ 前缀）

| Sphinx 配置名 | 类型 | 默认值 | 说明 |
|--------------|------|--------|------|
| `myst_commonmark_only` | bool | False | 严格 CommonMark 模式 |
| `myst_gfm_only` | bool | False | 严格 GFM 模式 |
| `myst_enable_extensions` | set[str] | set() | 启用的扩展语法集合 |
| `myst_disable_syntax` | list[str] | [] | 禁用的 CommonMark 语法 |
| `myst_all_links_external` | bool | False | 所有链接作为外部链接 |
| `myst_url_schemes` | dict | {http,https,mailto,ftp:None} | 识别为外部链接的 URL scheme |
| `myst_ref_domains` | list[str] | None | 引用搜索的 Sphinx 域 |
| `myst_heading_anchors` | int(0-7) | 0 | 标题锚点深度 |
| `myst_heading_slug_func` | str/Callable | None | 标题 slug 函数 |
| `myst_html_meta` | dict | {} | HTML meta 标签 |
| `myst_footnote_sort` | bool | True | 脚注排序 |
| `myst_substitutions` | dict | {} | 替换映射 |
| `myst_number_code_blocks` | list[str] | [] | 添加行号的代码块语言 |
| `myst_title_to_header` | bool | False | frontmatter title 转 H1 |

## 扩展语法列表（enable_extensions）

| 扩展名 | 依赖 | 功能 |
|--------|------|------|
| dollarmath | mdit-py-plugins | `$...$` 和 `$$...$$` 数学公式 |
| amsmath | mdit-py-plugins | AMS 数学环境（`\begin{align}` 等） |
| colon_fence | 内置（make_fence_rule） | `:::` 围栏指令语法 |
| deflist | mdit-py-plugins | 定义列表语法 |
| fieldlist | mdit-py-plugins | 字段列表语法（RST 兼容） |
| tasklist | markdown-it | 任务列表 `- [ ]` |
| linkify | linkify-it-py | 自动链接识别 |
| substitution | mdit-py-plugins | `{{key}}` 变量替换 |
| smartquotes | markdown-it | 智能引号 |
| replacements | markdown-it | 文本替换（(c)→© 等） |
| strikethrough | markdown-it | `~~删除线~~` |
| html_admonition | - | HTML 式提示块 |
| html_image | - | HTML img 标签支持 |
| attrs_inline | mdit-py-plugins | 行内属性 `{.class #id}` |
| attrs_block | mdit-py-plugins | 块级属性 |
| gfm_autolink | mdit-py-plugins | GFM 自动链接 |
| alert | markdown-it | GitHub 风格 alert 块 |

## CLI 入口点

| 命令 | 入口函数 | 功能 |
|------|---------|------|
| `myst-anchors` | `myst_parser.cli:print_anchors` | 输出标题锚点 |
| `myst-inv` | `myst_parser.inventory:inventory_cli` | Inventory 文件操作 |
| `myst-docutils-html` | `parsers.docutils_:cli_html` | 转 HTML |
| `myst-docutils-html5` | `parsers.docutils_:cli_html5` | 转 HTML5 |
| `myst-docutils-demo` | `parsers.docutils_:cli_html5_demo` | 转 HTML body 片段 |
| `myst-docutils-latex` | `parsers.docutils_:cli_latex` | 转 LaTeX |
| `myst-docutils-xml` | `parsers.docutils_:cli_xml` | 转 docutils XML |
| `myst-docutils-pseudoxml` | `parsers.docutils_:cli_pseudoxml` | 转 pseudo-XML |

## setup_sphinx() 注册清单

```python
# 解析器注册
app.add_source_suffix(".md", "markdown")      # .md 文件关联
app.add_source_parser(MystParser)              # 解析器类

# 指令和角色
app.add_role("sub-ref", SubstitutionReferenceRole())
app.add_directive("figure-md", FigureMarkdown)

# Transforms
app.registry.transforms.remove(SphinxUnreferencedFootnotesDetector)
app.add_transform(UnreferencedFootnotesDetector)
app.add_post_transform(MystReferenceResolver)  # priority=9

# 配置值（自动遍历 MdParserConfig 字段）
for name, default, field in MdParserConfig().as_triple():
    app.add_config_value(f"myst_{name}", default, "env")

# 事件连接
app.connect("builder-inited", create_myst_config)
app.connect("builder-inited", override_mathjax)
```

## 相关概念

- [MyST-Parser 简介](../concepts/00-introduction.md)
- [三阶段解析管线](../concepts/03-architecture-pipeline.md)
- [配置系统](../concepts/04-config-system.md)
- [Sphinx 集成机制](../concepts/11-sphinx-integration.md)
