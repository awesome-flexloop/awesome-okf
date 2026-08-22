---
type: spec
title: mdit-py-plugins 事实清单
description: mdit-py-plugins 源码事实清单
tags:
- mdit-py-plugins
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: mdit-py-plugins-source
  resource: /references/plugin-source-mapping.md
  title: mdit-py-plugins plugin-source-mapping
---

# mdit-py-plugins 事实清单

> R阶段产出。基于源码阅读提取的可验证事实，禁止推断性表述。

## F-001 ~ F-010：项目元数据

- F-001：包名 `mdit-py-plugins`，版本 `0.7.0`（`mdit_py_plugins/__init__.py` L1: `__version__ = "0.7.0"`）
- F-002：构建系统使用 flit_core >=3.4,<4（pyproject.toml L2-3）
- F-003：描述 "Collection of plugins for markdown-it-py"（pyproject.toml L8）
- F-004：作者 Chris Sewell，邮箱 chrisj_sewell@hotmail.com（pyproject.toml L10）
- F-005：许可证 MIT（pyproject.toml L11）
- F-006：Python 要求 >=3.10（pyproject.toml L28）
- F-007：运行时依赖 `markdown-it-py>=2.0.0,<5.0.0`（pyproject.toml L29）
- F-008：项目主页 https://github.com/executablebooks/mdit-py-plugins（pyproject.toml L32）
- F-009：文档地址 https://mdit-py-plugins.readthedocs.io（pyproject.toml L33）
- F-010：测试依赖包含 pytest、pytest-cov、pytest-regressions、pytest-timeout、coverage（pyproject.toml L37-43）

## F-011 ~ F-020：源码结构

- F-011：源码目录为 `mdit_py_plugins/`（pyproject.toml L50: `name = "mdit_py_plugins"`）
- F-012：`mdit_py_plugins/__init__.py` 仅导出版本号 `__version__`
- F-013：`mdit_py_plugins/utils.py` 提供共享工具函数
- F-014：`mdit_py_plugins/py.typed` 是 PEP 561 类型标记文件
- F-015：单文件插件包括 `colon_fence.py` 和 `substitution.py`（直接在包目录下）
- F-016：多文件插件以子目录形式存在，每个子目录包含 `__init__.py`（导出插件函数）和 `index.py`（实现）
- F-017：部分插件子目录包含 `LICENSE` 文件（admon、container、deflist、footnote、front_matter、subscript、tasklists、texmath）
- F-018：部分插件子目录包含 `port.yaml` 文件（admon、container、deflist、footnote、front_matter、subscript、tasklists、texmath），记录从JS版移植信息
- F-019：测试目录 `tests/`，每个插件有对应的 test_*.py 文件
- F-020：测试 fixtures 在 `tests/fixtures/` 目录下，使用 `.md` 格式

## F-021 ~ F-030：共享工具

- F-021：`utils.is_code_block(state, line)` 函数检查指定行是否在代码块内（utils.py L6-14）
- F-022：`is_code_block` 优先调用 markdown-it-py v3+ 的 `state.is_code_block(line)` 方法（v3+ API）
- F-023：`is_code_block` 的 v2 兼容实现检查 `(state.sCount[line] - state.blkIndent) >= 4`（缩进≥4空格）
- F-024：`UNESCAPE_RE` 正则 `r"\\([ \\!\"#$%&'()*+,./:;<=>?@[\]^_`{|}~-])"` 用于反转义（utils.py L18）
- F-025：`WHITESPACE_RE` 正则 `r"(^|[^\\])(\\\\)*\s"` 用于检测未转义空白（utils.py L19）

## F-031 ~ F-050：插件清单（22个插件）

- F-031：`admon_plugin` — 导出自 `mdit_py_plugins.admon`，告警块插件
- F-032：`amsmath_plugin` — 定义在 `mdit_py_plugins.amsmath.__init__`，AMS数学环境插件
- F-033：`anchors_plugin` — 导出自 `mdit_py_plugins.anchors`，标题锚点插件
- F-034：`attrs_plugin` 和 `attrs_block_plugin` — 导出自 `mdit_py_plugins.attrs`，属性插件（行内和块级）
- F-035：`colon_fence_plugin` — 定义在 `mdit_py_plugins.colon_fence.py` L18，冒号围栏插件（`:::`替代```）
- F-036：`container_plugin` — 导出自 `mdit_py_plugins.container`，自定义容器插件
- F-037：`deflist_plugin` — 导出自 `mdit_py_plugins.deflist`，定义列表插件
- F-038：`dollarmath_plugin` — 导出自 `mdit_py_plugins.dollarmath`，美元数学公式插件
- F-039：`fieldlist_plugin` — 定义在 `mdit_py_plugins.field_list.__init__` L12，字段列表插件（reST风格）
- F-040：`footnote_plugin` — 导出自 `mdit_py_plugins.footnote`，脚注插件
- F-041：`front_matter_plugin` — 导出自 `mdit_py_plugins.front_matter`，YAML前置元数据插件
- F-042：`gfm_plugin` — 定义在 `mdit_py_plugins.gfm.__init__` L53，GFM组合插件
- F-043：`gfm_autolink_plugin` — 导出自 `mdit_py_plugins.gfm_autolink`，GFM自动链接插件
- F-044：`myst_blocks_plugin` — 导出自 `mdit_py_plugins.myst_blocks`，MyST块语法插件
- F-045：`myst_role_plugin` — 导出自 `mdit_py_plugins.myst_role`，MyST角色语法插件
- F-046：`section_ref_plugin` — 导出自 `mdit_py_plugins.section_ref`，章节引用插件
- F-047：`sub_plugin` — 定义在 `mdit_py_plugins.subscript.__init__.py` L104，下标插件（`~sub~`）
- F-048：`superscript_plugin` — 导出自 `mdit_py_plugins.superscript`，上标插件（`^sup^`）
- F-049：`tasklists_plugin` — 定义在 `mdit_py_plugins.tasklists.__init__.py` L33，任务列表插件
- F-050：`texmath_plugin` — 导出自 `mdit_py_plugins.texmath`，TeX数学公式插件（`\\(\\)`/`\\[\\]`分隔符）
- F-051：`wordcount_plugin` — 定义在 `mdit_py_plugins.wordcount.__init__.py` L13，字数统计插件
- F-052：`substitution` 相关功能在 `mdit_py_plugins/substitution.py` 中

## F-053 ~ F-065：dollarmath_plugin 详情

- F-053：dollarmath_plugin 函数签名：`(md, *, allow_labels=True, allow_space=True, allow_digits=True, allow_blank_lines=True, double_inline=False, label_normalizer=None, renderer=None, label_renderer=None) -> None`（dollarmath/index.py L20-31）
- F-054：行内数学规则注册位置：`md.inline.ruler.before("escape", "math_inline", math_inline_dollar(...))`（dollarmath/index.py L59-63）
- F-055：块级数学规则注册位置：`md.block.ruler.before("fence", "math_block", math_block_dollar(...))`（dollarmath/index.py L64-68）
- F-056：注册4个渲染规则：math_inline、math_inline_double、math_block、math_block_label（dollarmath/index.py L130-134）
- F-057：行内数学渲染为 `<span class="math inline">...</span>`（dollarmath/index.py L96）
- F-058：块级数学渲染为 `<div class="math block">...</div>`（dollarmath/index.py L116）
- F-059：带标签块级数学渲染为 `<div id="{label}" class="math block">` 包含锚点链接（dollarmath/index.py L125-128）
- F-060：默认渲染器对内容执行 `escapeHtml()` 转义（dollarmath/index.py L75）
- F-061：`is_escaped(state, back_pos, mod=0)` 函数检测反斜杠转义（dollarmath/index.py L137-155）
- F-062：`allow_space=False` 时，`$` 后/前紧邻空白则不匹配（dollarmath/index.py L194-200, L246-252）
- F-063：`allow_digits=False` 时，`$` 前/后紧邻数字则不匹配（dollarmath/index.py L202-208, L254-260）
- F-064：`double_inline=True` 时行内上下文中也匹配 `$$...$$`（dollarmath/index.py L214）
- F-065：带标签数学块支持 `$$eq$$ (label)` 语法，标签使用 `DOLLAR_EQNO_REV` 正则反向匹配（dollarmath/index.py L287）

## F-066 ~ F-080：footnote_plugin 详情

- F-066：footnote_plugin 函数签名：`(md, *, inline=True, move_to_end=True, always_match_refs=False) -> None`（footnote/index.py L23-29）
- F-067：脚注定义规则注册位置：`md.block.ruler.before("reference", "footnote_def", footnote_def, {"alt": ["paragraph", "reference"]})`（footnote/index.py L54-56）
- F-068：inline=True 时注册行内脚注（`^[...]`）在 image 规则之后（footnote/index.py L59）
- F-069：脚注引用规则注册位置：`md.inline.ruler.after("footnote_inline"/"image", "footnote_ref", ...)`（footnote/index.py L60-62）
- F-070：move_to_end=True 时注册 footnote_tail 核心规则在 inline 之后，将脚注定义移到文档末尾（footnote/index.py L63-64）
- F-071：注册8个渲染规则：footnote_ref、footnote_block_open/close、footnote_open/close、footnote_anchor、footnote_caption、footnote_anchor_name（footnote/index.py L66-75）
- F-072：脚注数据存储在 `env["footnotes"]`，包含 `refs`（标签映射）和 `list`（脚注数据）两个字典（footnote/index.py L87-98）
- F-073：脚注引用语法为 `[^label]`，定义语法为 `[^label]: content`（footnote/index.py L40-47）
- F-074：行内脚注语法为 `^[inline content]`（footnote/index.py L49）
- F-075：footnote_ref 渲染为 `<sup class="footnote-ref"><a href="#fn{id}" id="fnref{refid}">[n]</a></sup>`（footnote/index.py L449-457）
- F-076：footnote_block_open 渲染为 `<hr class="footnotes-sep">\n<section class="footnotes">\n<ol class="footnotes-list">`（footnote/index.py L467-475）
- F-077：footnote_tail 后处理移除 `footnote_reference_open/close` 对，将脚注内容移到 tokens 末尾（footnote/index.py L302-396）
- F-078：footnote_def 解析时修改 state.blkIndent += 4 并递归调用 `state.md.block.tokenize()` 解析脚注内容（footnote/index.py L178-184）
- F-079：同一脚注多次引用时，count 递增，生成多个 footnote_anchor（footnote/index.py L291-292, L383-387）
- F-080：支持 `docId` 环境变量用于多文档场景，生成 `fn-{docId}-n` 格式ID（footnote/index.py L413-417）

## F-081 ~ F-095：其他核心插件

- F-081：container_plugin 函数签名：`(md, name, marker=":", validate=None, render=None) -> None`（container/index.py L20-26）
- F-082：container 默认标记字符为 `:`，最少3个（`:::`开头）（container/index.py L63-66）
- F-083：container 默认验证函数检查 params 第一个词是否等于 name（container/index.py L47-48）
- F-084：container 默认渲染为 `<div class="{name}">...</div>`（container/index.py L50-61）
- F-085：front_matter_plugin 块规则注册在 table 之前：`md.block.ruler.before("table", "front_matter", ...)`（front_matter/index.py L22-27）
- F-086：front_matter 语法为 `---\nYAML\n---`，仅匹配文档起始（startLine==0且首字符为`-`）（front_matter/index.py L43）
- F-087：front_matter 最少3个连续 `-` 标记（front_matter/index.py L56）
- F-088：deflist_plugin 支持 `: definition` 和 `~ definition` 标记（deflist/index.py L40）
- F-089：deflist 标记后必须有空格（deflist/index.py L46-47）
- F-090：tasklists_plugin 注册为 Core 规则在 inline 之后：`md.core.ruler.after("inline", "github-tasklists", fcn)`（tasklists/__init__.py L70）
- F-091：tasklists_plugin 参数：enabled=False（checkbox是否禁用）、label=False（是否label包裹）、label_after=False（label是否在checkbox后）（tasklists/__init__.py L33-38）
- F-092：tasklists 检测 `list_item_open > paragraph_open > inline` 中以 `[ ] ` 或 `[x] `/`[X] ` 开头的项（tasklists/__init__.py L79-85）
- F-093：tasklists 匹配时插入 `html_inline` token 包含 `<input type="checkbox">`，并移除前3字符（tasklists/__init__.py L87-91, L107-120）
- F-094：tasklists 为 list_item_open 添加 `class="task-list-item"`，为父列表添加 `class="contains-task-list"`（tasklists/__init__.py L62-68）
- F-095：colon_fence_plugin 块规则注册在 fence 之前：`md.block.ruler.before("fence", "colon_fence", ...)`（colon_fence.py L29-34）

## F-096 ~ F-110：更多插件

- F-096：colon_fence 使用 `:` 替代反引号，最少3个，渲染为 `<pre><code class="block-{name}">...</code></pre>`（colon_fence.py L18-35, L154-159）
- F-097：sub_plugin 行内规则注册在 emphasis 之后：`md.inline.ruler.after("emphasis", "sub", tokenize)`（subscript/__init__.py L113）
- F-098：sub_plugin 匹配 `~content~`，内容中不能有未转义空白，渲染为 `<sub>...</sub>`（subscript/__init__.py L27-79, L82-101）
- F-099：amsmath_plugin 块规则注册在 blockquote 之前：`md.block.ruler.before("blockquote", "amsmath", ...)`（amsmath/__init__.py L77-82）
- F-100：amsmath 支持的环境列表：equation, multline, gather, align, alignat, flalign, matrix, pmatrix, bmatrix, Bmatrix, vmatrix, Vmatrix, eqnarray（amsmath/__init__.py L22-46）
- F-101：amsmath 匹配 `\begin{env}...\end{env}`，不自动闭合（必须找到结束标签）（amsmath/__init__.py L99-143）
- F-102：amsmath 渲染为 `<div class="math amsmath">...</div>`（amsmath/__init__.py L93-94）
- F-103：wordcount_plugin 注册为 Core 规则 push 到链末尾：`md.core.ruler.push("wordcount", ...)`（wordcount/__init__.py L58）
- F-104：wordcount 默认统计函数 basic_count 按空格分割，忽略纯标点元素，仅计含字母的词（wordcount/__init__.py L8-10）
- F-105：wordcount 将结果存入 `env["wordcount"] = {"words": N, "minutes": M}`，参数 per_minute 默认200（wordcount/__init__.py L16, L50-56）
- F-106：fieldlist_plugin 块规则注册在 paragraph 之前，alt 包含 paragraph/reference/blockquote（field_list/__init__.py L40-45）
- F-107：fieldlist 语法为 `:name: body`，渲染为 `<dl class="field-list"><dt>name</dt><dd>body</dd>...</dl>`（field_list/__init__.py L17-28, L116-118）
- F-108：fieldlist 使用 `@contextmanager set_parent_type(state, name)` 临时修改 state.parentType（field_list/__init__.py L90-96）
- F-109：gfm_plugin 是组合插件，启用内置 table/strikethrough、设置 tasklists/alerts/strikethrough_single_tilde 选项，并加载 gfm_autolink_plugin 和 footnote_plugin（gfm/__init__.py L76-89）
- F-110：gfm_plugin 可选参数 dollarmath/front_matter/tasklists_editable，要求 markdown-it-py >= 4.1.0（gfm/__init__.py L54-69）

## F-111 ~ F-120：插件模式与架构

- F-111：所有插件遵循统一模式：`def plugin_func(md: MarkdownIt, ...options) -> None`，接收 MarkdownIt 实例
- F-112：多文件插件采用 `__init__.py` 导出插件函数、`index.py` 包含实现的布局
- F-113：部分插件从 JS markdown-it 插件移植：footnote来自markdown-it-footnote、container来自markdown-it-container、deflist来自markdown-it-deflist、front_matter来自markdown-it-front-matter、sub来自markdown-it-sub、tasklists来自markdown-it-task-lists
- F-114：attrs_plugin 包含解析模块 `attrs/parse.py`，支持行内属性 `{.class #id key=value}` 语法
- F-115：texmath_plugin 使用 `\\(...\\)`（行内）和 `\\[...\\]`（块级）分隔符，是dollarmath的替代方案
- F-116：gfm_autolink_plugin 包含 `_match.py` 匹配模块，自动识别文本中的URL/邮箱
- F-117：admon_plugin 支持 `!!! type "Title"` 语法（与Python-Markdown admonitions兼容）
- F-118：myst_role_plugin 支持 MyST 角色语法 `{role}`text``
- F-119：myst_blocks_plugin 支持 MyST 块语法（如 ```` ```{directive} ````）
- F-120：所有插件的块级规则都先调用 `is_code_block(state, startLine)` 检查，避免在代码块内触发

## F-121 ~ F-130：测试与质量配置

- F-121：代码检查使用 Ruff，扩展规则集包含 B, C4, I, ICN, ISC, N, PERF, PGH, PIE, PTH, RUF, SIM, UP, T20（pyproject.toml L58-74）
- F-122：忽略规则 ISC001, N802, N803, N806（pyproject.toml L75）
- F-123：Mypy 配置 strict=True（pyproject.toml L83-87）
- F-124：pytest 超时设置为10秒（pyproject.toml L89-90）
- F-125：测试 fixtures 使用 `.md` 文件，格式为"标题\n.\nmarkdown输入\n.\n期望HTML输出\n."（来自AGENTS.md描述）
- F-126：测试使用 pytest-regressions 进行回归测试
- F-127：`--force-regen` 选项可更新回归测试 fixtures
- F-128：tox 配置测试环境，使用 tox-uv 加速环境创建
- F-129：sdist 打包排除 docs/ 和 tests/ 目录（pyproject.toml L52-56）
- F-130：支持 Python 3.8 到 3.12 及 PyPy（pyproject.toml L17-23）
