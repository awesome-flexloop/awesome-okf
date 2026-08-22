---
type: spec
title: MyST-Parser 源码事实清单
description: MyST-Parser 源码事实清单
tags:
- myst-parser
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: myst-parser-source
  resource: /references/extensions-cheatsheet.md
  title: MyST-Parser extensions-cheatsheet
- id: myst-parser-source-1
  resource: /references/myst-parser-source.md
  title: MyST-Parser myst-parser-source
---

# MyST-Parser 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: `__version__ = "5.1.0"`（`myst_parser/__init__.py` L6）
- F-002: `pyproject.toml` 要求 `requires-python = ">=3.11"`
- F-003: 构建系统使用 `flit_core >=3.4,<4`，build-backend 为 `flit_core.buildapi`
- F-004: 许可证为 MIT
- F-005: 核心依赖：`docutils>=0.20,<0.24`、`jinja2`、`markdown-it-py~=4.2`、`mdit-py-plugins~=0.6,>=0.6.1`、`pyyaml`、`sphinx>=8,<10`
- F-006: 可选依赖组 `linkify = ["linkify-it-py~=2.0"]`
- F-007: CLI 入口点：`myst-anchors`、`myst-inv`、`myst-docutils-html/html5/demo/latex/xml/pseudoxml` 共 7 个
- F-008: 支持 Python 3.11-3.14，CPython 和 PyPy

## 包入口与 Sphinx 注册（myst_parser/__init__.py）

- F-009: `setup(app)` 函数从 `myst_parser.sphinx_ext.main` 导入 `setup_sphinx` 并调用 `setup_sphinx(app, load_parser=True)`
- F-010: `setup(app)` 返回 `{"version": __version__, "parallel_read_safe": True}`

## 配置系统（myst_parser/config/main.py）

- F-011: `MdParserConfig` 是一个 `@dc.dataclass()` 数据类，集中管理所有 MyST 配置选项
- F-012: Sphinx 中配置项名自动加 `myst_` 前缀（通过 `app.add_config_value(f"myst_{name}", default, "env", types=Any)` 注册）
- F-013: 支持的扩展语法集合（`check_extensions` 白名单）：alert、amsmath、attrs_image、attrs_inline、attrs_block、colon_fence、deflist、dollarmath、fieldlist、gfm_autolink、html_admonition、html_image、linkify、replacements、smartquotes、strikethrough、substitution、tasklist（共 18 个）
- F-014: `commonmark_only: bool = False`——严格 CommonMark 模式
- F-015: `gfm_only: bool = False`——严格 GitHub Flavored Markdown 模式
- F-016: `enable_extensions: set[str]`——启用的扩展语法集合，默认空集
- F-017: `disable_syntax: Iterable[str]`——禁用的 CommonMark 语法元素列表
- F-018: `all_links_external: bool = False`——所有链接解析为外部超链接
- F-019: `url_schemes: dict`——默认识别的 URL scheme：http、https、mailto、ftp
- F-020: `ref_domains: Iterable[str] | None = None`——链接引用搜索的 Sphinx 域名
- F-021: `fence_as_directive: set[str]`——将指定语言名的代码围栏解释为指令
- F-022: `heading_anchors: int = 0`——自动生成标题锚点的深度（0-7，0 表示关闭）
- F-023: `heading_slug_func: Callable | None = None`——标题锚点 slug 生成函数，支持预设名 "docutils"/"github"/"gitlab"
- F-024: `heading_anchors_html_ids: bool = True`——标题锚点同时作为 HTML id 输出
- F-025: `html_meta: dict[str, str]`——HTML meta 标签，支持 frontmatter 合并
- F-026: `footnote_sort: bool = True`——将脚注移到文档末尾并按引用顺序排序
- F-027: `substitutions: dict[str, Any]`——替换映射，支持 frontmatter 合并
- F-028: `sub_delimiters: tuple[str, str] = ("{", "}")`——替换定界符
- F-029: `words_per_minute: int = 200`——阅读速度计算
- F-030: `suppress_warnings: Sequence[str]`——抑制的警告类型列表
- F-031: `highlight_code_blocks: bool = True`——Pygments 语法高亮代码块
- F-032: `inventories: dict[str, tuple[str, str | None]]`——项目间引用的 inventory 映射
- F-033: dollarmath 扩展配置：`dmath_allow_labels=True`、`dmath_allow_space=True`、`dmath_allow_digits=True`、`dmath_double_inline=False`
- F-034: `update_mathjax: bool = True`——更新 MathJax 配置以忽略 `$` 定界符
- F-035: `enable_checkboxes: bool = False`——任务列表复选框可编辑
- F-036: `strikethrough_single_tilde: bool = False`——允许单个 `~` 作为删除线
- F-037: `colon_fence_exact_match: bool = False`——冒号围栏开闭冒号数必须完全匹配
- F-038: `linkify_fuzzy_links: bool = True`——识别无 scheme 前缀的 URL
- F-039: `number_code_blocks: Sequence[str]`——为指定语言的代码块添加行号
- F-040: `title_to_header: bool = False`——将 frontmatter 的 title 字段转为 H1
- F-041: 字段 metadata 支持 `validator`、`help`、`extension`、`global_only`、`omit`、`merge_topmatter`、`repr`、`doc_type`、`repr_func` 等键
- F-042: `merge_file_level()` 函数将文件级 frontmatter（YAML）中的 `myst` 键与全局配置合并，支持 `merge_topmatter` 字段的字典合并
- F-043: `read_topmatter()` 函数解析文档开头的 `---` 分隔的 YAML frontmatter

## Markdown-it 解析器构建（myst_parser/parsers/mdit.py）

- F-044: `create_md_parser(config, renderer)` 是工厂函数，返回配置好的 `MarkdownIt` 实例
- F-045: commonmark_only 模式：仅启用 `wordcount_plugin`
- F-046: gfm_only 模式：启用 `gfm_plugin`（含 tasklist）+ `wordcount_plugin`
- F-047: 默认模式（非 commonmark/gfm）启用的基础插件：front_matter_plugin、myst_block_plugin、myst_role_plugin、footnote_plugin（inline=False, move_to_end=False, always_match_refs=True）、wordcount_plugin
- F-048: 默认模式额外启用 table 规则（`md.enable("table")`）
- F-049: 扩展插件按需加载：smartquotes/replacements 启用 typographer；linkify 启用 linkify 规则；dollarmath 启用 dollarmath_plugin；colon_fence 使用 `make_fence_rule` 构建自定义围栏规则插入到 fence 规则之前；amsmath/deflist/fieldlist 分别启用对应插件；attrs_inline/attrs_block 启用属性插件；substitution 启用 substitution_plugin
- F-050: `linkify_available()` 函数检查 `markdown_it.main.linkify_it` 是否不为 None（即 linkify-it-py 是否已安装）
- F-051: `disable_syntax` 配置的语法元素通过 `md.disable(name, True)` 禁用

## Sphinx 集成（myst_parser/sphinx_ext/main.py）

- F-052: `setup_sphinx(app, load_parser=False)` 是独立的 Sphinx 初始化函数，可供外部包（如 myst_nb）调用
- F-053: 当 `load_parser=True` 时，调用 `app.add_source_suffix(".md", "markdown")` 和 `app.add_source_parser(MystParser)` 注册 .md 源文件解析器
- F-054: 注册角色 `sub-ref`（SubstitutionReferenceRole）
- F-055: 注册指令 `figure-md`（FigureMarkdown）
- F-056: 替换 Sphinx 内置的 `UnreferencedFootnotesDetector` transform 为 MyST 版本
- F-057: 注册 post-transform `MystReferenceResolver`（优先级 9，高于 Sphinx 默认 ReferencesResolver 的 10）
- F-058: 覆盖 `nodes.container` 的 HTML visit/depart 方法，移除 "container" CSS 类（避免 Bootstrap 冲突）
- F-059: 遍历 `MdParserConfig()` 的所有字段，对非 omit=["sphinx"] 的字段调用 `app.add_config_value(f"myst_{name}", default, "env", types=Any)` 注册配置值，重建级别为 "env"
- F-060: 连接 `builder-inited` 事件到 `create_myst_config` 和 `override_mathjax`
- F-061: `create_myst_config(app)` 在 builder-inited 时从 `app.config` 读取所有 `myst_*` 配置值，创建 `MdParserConfig` 实例并存入 `app.env.myst_config`
- F-062: 配置无效时记录 error 日志并回退到默认 `MdParserConfig()`

## Sphinx 解析器（myst_parser/parsers/sphinx_.py）

- F-063: `class MystParser(SphinxParser)` 继承自 `sphinx.parsers.Parser`
- F-064: `supported = ("md", "markdown", "myst")`——支持的文件后缀别名
- F-065: `settings_spec = RstParser.settings_spec`——复用 RST 解析器的运行时设置
- F-066: `get_transforms()` 返回父类 transforms + [SortFootnotes, CollectFootnotes, AddSlugIds, PrioritiseExplicitIds, ResolveAnchorIds]
- F-067: `parse(inputstring, document)` 方法流程：从 `document.settings.env.myst_config` 获取全局配置 → 读取 frontmatter → merge_file_level 合并文件级配置 → `create_md_parser(config, SphinxRenderer)` 创建解析器 → 设置 `parser.options["document"] = document` → `parser.render(inputstring)` 执行渲染

## Docutils 解析器与 CLI（myst_parser/parsers/docutils_.py）

- F-068: `class Parser(RstParser)` 是独立 docutils 解析器（不依赖 Sphinx）
- F-069: 同样支持 `("md", "markdown", "myst")` 文件别名
- F-070: `settings_spec` 包含自定义 "MyST options" 选项组，通过 `create_myst_settings_spec()` 从 MdParserConfig 字段自动生成 optparse 选项
- F-071: `get_transforms()` 返回父类 transforms + [UnreferencedFootnotesDetector, SortFootnotes, CollectFootnotes, AddSlugIds, PrioritiseExplicitIds, ResolveAnchorIds]（比 Sphinx 版本多 UnreferencedFootnotesDetector）
- F-072: `parse()` 方法还检查行长限制（line_length_limit）、处理 raw_enabled 设置
- F-073: 提供 CLI 入口：`cli_html`、`cli_html5`、`cli_html5_demo`、`cli_latex`、`cli_xml`、`cli_pseudoxml`，均通过 `_run_cli()` 调用 `publish_cmdline()`
- F-074: `cli_html5_demo` 使用自定义 `SimpleWriter`/`SimpleTranslator`，只输出 body 内容（无完整 HTML 框架）
- F-075: `to_html5_demo()` 函数通过 `publish_string()` 将 MyST 字符串直接转为 HTML body 片段
- F-076: 覆盖 `visit_rubric_html`/`depart_rubric_html` 方法使 rubric 节点输出正确的 `<hN>` 标签（解决嵌套组件中标题的结构问题）
- F-077: 覆盖 `visit_container_html`/`depart_container_html` 方法，对 `is_div=True` 的 container 移除 "container" CSS 类

## 渲染器体系（myst_parser/mdit_to_docutils/）

### DocutilsRenderer（base.py）

- F-078: `class DocutilsRenderer(RendererProtocol)` 是 markdown-it-py 的渲染器，实现 `__output__ = "docutils"`
- F-079: `__init__` 中通过 `inspect.getmembers(self, predicate=inspect.ismethod)` 自动发现所有 `render_*` 方法构建规则映射表
- F-080: `setup_render(options, env)` 初始化每次渲染的状态：md_env、md_config、document、current_node、reporter、language_module_rst、_heading_offset、_level_to_section、_heading_slugs
- F-081: `sphinx_env` 属性尝试返回 `document.settings.env`，无 Sphinx 环境时返回 None
- F-082: 渲染管线：`_render_tokens(tokens)` 将 token 的行号从 0-based 转为 1-based，然后按 token type 分发给对应 render_* 方法
- F-083: 提供 `create_warning()` 方法生成 docutils system_message 节点，自动处理 Sphinx/docutils 两种环境的警告抑制逻辑

### SphinxRenderer（sphinx_.py）

- F-084: `class SphinxRenderer(DocutilsRenderer)` 继承 DocutilsRenderer，添加 Sphinx 特有功能
- F-085: `sphinx_env` 属性重写为直接返回 `document.settings.env`（不再返回 None）
- F-086: `render_link_project()` 处理 `project:` 前缀的项目内文档链接，解析相对路径、生成 pending_xref 节点
- F-087: `_handle_relative_docs()` 处理 `relative-docs` include 选项的路径转换

## 引用解析（myst_parser/sphinx_ext/myst_refs.py）

- F-088: `class MystReferenceResolver(ReferencesResolver)` 继承 Sphinx 的 ReferencesResolver，`default_priority = 9`
- F-089: `run()` 方法遍历所有 `pending_xref` 节点，仅处理 `reftype == "myst"` 的引用
- F-090: 解析优先级：doc 域引用（`refdomain == "doc"`）→ 本地域解析（resolve_myst_ref_any）→ intersphinx 解析 → 本地锚点回退 → 警告并降级为外部链接
- F-091: `resolve_myst_ref_doc()` 解析文档间引用（支持带锚点的 `doc.md#target` 格式）
- F-092: `resolve_myst_ref_any()` 尝试 std:ref、std:doc、std domain objects、其他 domains 的 resolve_any_xref，多结果时发出 XREF_AMBIGUOUS 警告
- F-093: 支持 `nitpick_ignore` 和 `nitpick_ignore_regex` 配置抑制引用警告
- F-094: 未解析的引用默认降级为外部链接（`normalizeLink(target)`）

## 自定义指令与角色（myst_parser/sphinx_ext/directives.py）

- F-095: `class SubstitutionReferenceRole(SphinxRole)` 实现 substitution 引用角色（docutils 原生未实现），生成 `nodes.substitution_reference`
- F-096: `class FigureMarkdown(SphinxDirective)` 实现 `figure-md` 指令，支持 Markdown 语法的图片+标题
- F-097: FigureMarkdown 选项：width（长度/百分比/"image"）、class（类选项）、align（left/center/right）、name
- F-098: FigureMarkdown 运行时临时启用 html_image 扩展以解析 HTML img 标签，解析后恢复

## 警告系统（myst_parser/warnings_.py）

- F-099: `class MystWarnings(Enum)` 定义 23 种警告类型：DEPRECATED、NOT_SUPPORTED、RENDER_METHOD、MD_TOPMATTER、MD_DEF_DUPE、MD_HEADING_NON_CONSECUTIVE、DIRECTIVE_PARSING、DIRECTIVE_OPTION、DIRECTIVE_OPTION_COMMENTS、DIRECTIVE_BODY、UNKNOWN_DIRECTIVE、UNKNOWN_ROLE、XREF_AMBIGUOUS、XREF_MISSING、INV_LOAD、IREF_MISSING、IREF_AMBIGUOUS、LEGACY_DOMAIN、LINKIFY、HEADING_SLUG、STRIKETHROUGH、HTML_PARSE、INVALID_ATTRIBUTE、SUBSTITUTION
- F-100: `create_warning()` 统一警告创建函数，同时处理 Sphinx 环境（logger.warning + system_message 节点）和 docutils 环境（document.reporter.warning），支持 suppress_warnings 抑制

## Slug 生成（myst_parser/slugs.py）

- F-101: 提供三种预设 slug 函数：`github_slugify`、`gitlab_slugify`、`docutils_slugify`，注册在 `SLUG_PRESETS` 字典中
- F-102: github_slugify 算法：lowercase → 空格替换为 `-` → 移除非 word/CJK/连字符/空格字符，保留首尾空格生成的连字符
- F-103: gitlab_slugify 算法：strip + lowercase → 移除非 word/连字符/空格 → 空格转 `-` → 压缩连续 `-` → 纯数字结果加 `anchor-` 前缀
- F-104: docutils_slugify 算法：lowercase → 二合字母映射（ß→sz, æ→ae 等）→ 特殊拉丁字母映射 → NFKD 规范化去非 ASCII → 非字母数字转 `-` → 去除首尾数字/连字符和尾部连字符；与 docutils.nodes.make_id 字节一致
- F-105: `unique_slug(slug, existing)` 函数为重复 slug 追加 `-1`、`-2` 后缀，基础 slug 不变

## CLI 工具（myst_parser/cli.py）

- F-106: `print_anchors()` 是 `myst-anchors` CLI 入口，从 stdin/文件读取 Markdown，输出带标题锚点的 HTML
- F-107: 支持参数：input（默认 stdin）、-o/--output（默认 stdout）、-l/--level（最大标题级别，默认 2）、--slug-func（slug 预设，默认 github）
- F-108: 内部使用 anchors_plugin 并添加自定义 filter 插件仅保留 heading token

## 文档辅助模块（myst_parser/_docs.py）

- F-109: 提供 Sphinx 文档构建用的自定义指令：MystConfigDirective（自动生成配置选项表格）、DocutilsCliHelpDirective（输出 CLI help）、DirectiveDoc（指令文档化）、MystWarningsDirective（列出所有警告类型）、MystToHTMLDirective（MyST 转 HTML 示例）、MystAdmonitionDirective（admonition 标签页展示）
- F-110: 提供 post-transform：StripUnsupportedLatex（LaTeX 构建时移除 SVG 图片和 Mermaid 图表）、NumberSections（HTML 中给标题编号）
- F-111: 定义 MystLexer（Pygments 词法分析器），为 MyST 特有语法（(target)=、:::、{role}、<scheme:...>）提供语法高亮

## 其他模块

- F-112: `myst_parser/mocking.py` 提供 MockState、MockInliner、MockStateMachine、MockRSTParser、MockIncludeDirective 等 mock 对象，用于在 Markdown 解析过程中复用 docutils 的指令/角色解析基础设施
- F-113: `myst_parser/inventory.py` 处理 Sphinx inventory 文件（objects.inv）的读取和 intersphinx 引用过滤
- F-114: `myst_parser/_compat.py` 提供 Python 版本兼容工具（如 findall 函数）

## 三阶段解析管线

- F-115: 阶段一——Markdown 解析：MyST Markdown 文本 → markdown-it-py 解析 → Token 流（由 `create_md_parser()` 配置的插件链处理）
- F-116: 阶段二——Token 渲染：Token 流 → DocutilsRenderer/SphinxRenderer.render_* 方法 → docutils document AST（doctree）
- F-117: 阶段三——Sphinx 后处理：MystReferenceResolver post-transform → 解析交叉引用 → 最终 doctree 供 Builder 输出
