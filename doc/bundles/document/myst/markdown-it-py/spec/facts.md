---
type: spec
title: markdown-it-py 事实清单
description: markdown-it-py 源码事实清单
tags:
- markdown-it-py
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py markdown-it-py-source
- id: markdown-it-py-source-1
  resource: /references/token-options-api.md
  title: markdown-it-py token-options-api
---

# markdown-it-py 事实清单

> R阶段产出。所有事实编号 F-xxx，仅记录源码中可验证的客观内容，不含推断。

## 项目元数据

- F-001: 版本号为 `4.2.0`，定义于 `markdown_it/__init__.py` L4
- F-002: `requires-python = ">=3.10"`，定义于 `pyproject.toml` L27
- F-003: 许可证为 MIT，定义于 `pyproject.toml` L15 与 `LICENSE` 文件
- F-004: 构建系统使用 `flit_core >=3.4,<4`，定义于 `pyproject.toml` L2
- F-005: 运行时依赖仅有 `mdurl~=0.1`，定义于 `pyproject.toml` L28-29
- F-006: 可选依赖包括：compare（commonmark/markdown/mistletoe等对比库）、linkify（linkify-it-py>=1,<3）、plugins（mdit-py-plugins>=0.5.0）、rtd（文档构建依赖）、testing（pytest等测试工具）
- F-007: CLI入口点 `markdown-it = "markdown_it.cli.parse:main"`，定义于 `pyproject.toml` L77-78
- F-008: `__init__.py` 通过 `__all__` 仅导出 `MarkdownIt` 类，定义于 `__init__.py` L3
- F-009: 项目描述为 "Python port of markdown-it. Markdown parsing, done right!"，keywords 为 `["markdown", "lexer", "parser", "commonmark", "markdown-it"]`
- F-010: markdown-it-py 是 JavaScript markdown-it 的 Python 端口（pyproject.toml 描述、README 声明）

## 源码结构

- F-011: 核心源码位于 `markdown_it/` 目录，包含以下模块和子包：
  - `__init__.py`, `main.py`, `token.py`, `ruler.py`, `renderer.py`, `tree.py`, `parser_core.py`, `parser_block.py`, `parser_inline.py`, `utils.py`, `_compat.py`, `_punycode.py`
  - `cli/`（CLI 接口）、`common/`（通用工具）、`helpers/`（辅助解析函数）、`presets/`（配置预设）
  - `rules_core/`（核心规则链）、`rules_block/`（块级规则）、`rules_inline/`（行内规则）

## MarkdownIt 主类（main.py）

- F-012: `MarkdownIt` 类定义于 `main.py` L33
- F-013: `MarkdownIt.__init__(self, config="commonmark", options_update=None, *, renderer_cls=RendererHTML)`：初始化方法
  - 创建 `self.inline = ParserInline()`、`self.block = ParserBlock()`、`self.core = ParserCore()`
  - 创建 `self.renderer = renderer_cls(self)`
  - 创建 `self.linkify = linkify_it.LinkifyIt()`（如果 linkify_it 已安装）否则为 None
  - 设置 `self.utils = utils`、`self.helpers = helpers`
  - 调用 `self.configure(config, options_update=options_update)`
- F-014: `_PRESETS` 字典包含6个预设："default"、"js-default"（=default）、"zero"、"commonmark"、"gfm-like"、"gfm-like2"，定义于 `main.py` L23-30
- F-015: `MarkdownIt.configure(presets, options_update=None)`：加载预设配置
  - 字符串预设从 `_PRESETS` 字典查找，不存在则抛 KeyError
  - 设置 options，遍历 config["components"] 对各 ruler 调用 `enableOnly(rules)` 和 `enableOnly(rules2)`
- F-016: `MarkdownIt.set(options)`：通过 `OptionsDict(options)` 设置解析选项
- F-017: `MarkdownIt.enable(names, ignoreInvalid=False)`：启用规则（链式调用），遍历 core/block/inline 的 ruler 和 inline.ruler2 调用 enable，未找到且 ignoreInvalid=False 时抛 ValueError
- F-018: `MarkdownIt.disable(names, ignoreInvalid=False)`：禁用规则（链式调用），逻辑同 enable
- F-019: `MarkdownIt.use(plugin, *params, **options)`：加载插件，调用 `plugin(self, *params, **options)` 并返回 self（链式调用）
- F-020: `MarkdownIt.parse(src, env=None) -> list[Token]`：解析源码为 Token 流
  - env 默认空 dict，必须是 MutableMapping，src 必须是 str
  - 创建 `StateCore(src, self, env)`，调用 `self.core.process(state)`，返回 `state.tokens`
- F-021: `MarkdownIt.render(src, env=None) -> str`：解析并渲染，调用 `self.renderer.render(self.parse(src, env), self.options, env)`
- F-022: `MarkdownIt.parseInline(src, env=None) -> list[Token]`：仅解析行内内容，设置 `state.inlineMode = True` 后调用 core.process
- F-023: `MarkdownIt.renderInline(src, env=None) -> str`：解析行内并渲染，结果不包裹 `<p>` 标签
- F-024: `MarkdownIt.add_render_rule(name, function, fmt="html")`：添加渲染规则，当 renderer 输出格式匹配时绑定到 `self.renderer.rules[name]`
- F-025: `MarkdownIt.validateLink(url) -> bool`：调用 `normalize_url.validateLink(url)` 验证链接
- F-026: `MarkdownIt.normalizeLink(url) -> str`：调用 `normalize_url.normalizeLink(url)` 规范化链接
- F-027: `MarkdownIt.normalizeLinkText(link) -> str`：调用 `normalize_url.normalizeLinkText(link)` 规范化自动链接文本
- F-028: `MarkdownIt.get_all_rules() -> dict[str, list[str]]`：返回所有可用规则名称（core/block/inline/inline2）
- F-029: `MarkdownIt.get_active_rules() -> dict[str, list[str]]`：返回当前启用的规则名称
- F-030: `MarkdownIt.reset_rules()`：上下文管理器，退出时重置规则状态
- F-031: `MarkdownIt.__getitem__(name)`：通过下标访问 "inline"/"block"/"core"/"renderer" 组件

## Token 类（token.py）

- F-032: `Token` 是 `@dc.dataclass(slots=True)` 类，定义于 `token.py` L21-22
- F-033: Token 字段：
  - `type: str`（Token类型，如 "paragraph_open"）
  - `tag: str`（HTML标签名，如 "p"）
  - `nesting: Literal[-1, 0, 1]`（1=开标签, 0=自闭合, -1=闭标签）
  - `attrs: dict[str, str | int | float]`（HTML属性，默认空dict）
  - `map: list[int] | None = None`（源码映射 [line_begin, line_end]）
  - `level: int = 0`（嵌套级别）
  - `children: list[Token] | None = None`（子节点，inline和img tokens）
  - `content: str = ""`（自闭合标签的内容）
  - `markup: str = ""`（标记符号，如 '*'、'_'、围栏字符串）
  - `info: str = ""`（附加信息：fence的info字符串、autolink的"auto"、有序列表的标记值）
  - `meta: dict[Any, Any]`（插件存储任意数据的位置，default_factory=dict）
  - `block: bool = False`（是否为块级token）
  - `hidden: bool = False`（渲染时是否忽略，用于紧凑列表隐藏段落）
- F-034: `convert_attrs(value)` 静态函数：将 None 或 `[[key, value], ...]` 格式转为 dict
- F-035: Token 方法：
  - `attrIndex(name) -> int`：已废弃（发出UserWarning），返回属性索引
  - `attrItems() -> list[tuple[str, str|int|float]]`：返回属性键值对列表
  - `attrPush(attrData)`：添加属性
  - `attrSet(name, value)`：设置属性值
  - `attrGet(name) -> str|int|float|None`：获取属性值
  - `attrJoin(name, value)`：通过空格拼接属性值（用于class等）
  - `copy(**changes) -> Token`：浅拷贝（使用 dc.replace）
  - `as_dict(children=True, as_upstream=True, meta_serializer=None, filter=None, dict_factory=dict) -> MutableMapping`：转为字典（可递归children，as_upstream将attrs转为list格式）
  - `from_dict(dct) -> Token`（类方法）：从字典构造Token，递归children

## Ruler 类（ruler.py）

- F-036: `Ruler` 泛型类 `Ruler[RuleFuncTv]`，定义于 `ruler.py` L75
- F-037: Ruler 内部维护 `__rules__: list[Rule]` 和 `__cache__: dict[str, list[RuleFuncTv]] | None`
- F-038: `Rule` 是 `@dataclass(slots=True)` 类，字段：`name: str`, `enabled: bool`, `fn: RuleFuncTv`, `alt: list[str]`
- F-039: Ruler 方法：
  - `at(ruleName, fn, options=None)`：替换指定名称的规则
  - `before(beforeName, ruleName, fn, options=None)`：在指定规则前插入新规则
  - `after(afterName, ruleName, fn, options=None)`：在指定规则后插入新规则
  - `push(ruleName, fn, options=None)`：在规则链末尾添加新规则
  - `enable(names, ignoreInvalid=False) -> list[str]`：启用规则
  - `enableOnly(names, ignoreInvalid=False) -> list[str]`：仅启用指定规则（禁用其他所有）
  - `disable(names, ignoreInvalid=False) -> list[str]`：禁用规则
  - `getRules(chainName="") -> list[RuleFuncTv]`：获取活动规则函数列表（缓存编译）
  - `get_all_rules() -> list[str]`：获取所有规则名称
  - `get_active_rules() -> list[str]`：获取当前启用的规则名称
- F-040: `__compile__()` 方法：编译规则缓存，收集所有 enabled 规则的 alt 链名，为每个链名构建活动规则函数列表
- F-041: `RuleOptionsType` 是 TypedDict，包含 `alt: list[str]` 字段（可选）
- F-042: `StateBase` 类定义于 `ruler.py` L32-56，是所有 State 类的基类
  - 属性：`src`（源码字符串）、`env`（环境沙箱）、`md`（MarkdownIt实例）
  - `srcCharCode` 属性已废弃（DeprecationWarning），建议直接使用 src

## RendererHTML（renderer.py）

- F-043: `RendererProtocol` 是 Protocol 类，要求 `__output__: ClassVar[str]` 和 `render(tokens, options, env) -> Any` 方法
- F-044: `RendererHTML` 类实现 `RendererProtocol`，`__output__ = "html"`，定义于 `renderer.py` L28
- F-045: `RendererHTML.__init__(self, parser=None)`：通过 `inspect.getmembers` 收集所有非 render/_ 开头的方法作为渲染规则存入 `self.rules` 字典
- F-046: `RendererHTML.render(tokens, options, env) -> str`：遍历token流渲染
  - type 为 "inline" 的 token 调用 `self.renderInline(token.children, options, env)`
  - type 在 self.rules 中的调用对应渲染规则
  - 其他调用 `self.renderToken(tokens, i, options, env)`
- F-047: `RendererHTML.renderInline(tokens, options, env) -> str`：遍历inline tokens渲染，逻辑同 render 但不处理 inline 嵌套
- F-048: `RendererHTML.renderToken(tokens, idx, options, env) -> str`：默认token渲染器
  - hidden token 返回空串
  - 按 nesting 生成 `<tag` 或 `</tag`
  - 调用 `renderAttrs(token)` 渲染属性
  - nesting==0 且 xhtmlOut=True 时添加 ` /`
  - 块级token根据next token决定是否添加换行
- F-049: `RendererHTML.renderAttrs(token) -> str`（静态方法）：遍历 attrItems()，用 escapeHtml 转义键值
- F-050: `RendererHTML.renderInlineAsText(tokens, options, env) -> str`：递归渲染为纯文本（用于alt属性），处理text/image/softbreak
- F-051: RendererHTML 内置渲染规则方法：
  - `code_inline`：`<code>content</code>`
  - `code_block`：`<pre><code>content</code></pre>\n`
  - `fence`：围栏代码块，支持 options.highlight 高亮函数，支持 langPrefix CSS类
  - `image`：设置alt属性后调用renderToken
  - `list_item_open`：支持tasklists的checkbox渲染
  - `hardbreak`：`<br />\n` 或 `<br>\n`
  - `softbreak`：根据 options.breaks 决定输出 `<br>` 或 `\n`
  - `text`：`escapeHtml(content)`
  - `html_block`、`html_inline`：直接输出 content（原始HTML）

## ParserCore（parser_core.py）

- F-052: `ParserCore` 类定义于 `parser_core.py` L37
- F-053: `RuleFuncCoreType = Callable[[StateCore], None]`
- F-054: Core规则链 `_rules` 按顺序包含7条规则：
  1. "normalize" → `rules_core.normalize`
  2. "block" → `rules_core.block`
  3. "inline" → `rules_core.inline`
  4. "linkify" → `rules_core.linkify`
  5. "replacements" → `rules_core.replace`
  6. "smartquotes" → `rules_core.smartquotes`
  7. "text_join" → `rules_core.text_join`
- F-055: `ParserCore.__init__`：创建 Ruler 并 push 所有 _rules
- F-056: `ParserCore.process(state)`：遍历 `self.ruler.getRules("")` 中的每条规则函数，依次调用 `rule(state)`

## ParserBlock（parser_block.py）

- F-057: `ParserBlock` 类定义于 `parser_block.py` L48
- F-058: `RuleFuncBlockType = Callable[[StateBlock, int, int, bool], bool]`，签名：(state, startLine, endLine, silent) -> matched
- F-059: Block规则链 `_rules` 按顺序包含11条规则（每条带名称、函数、alt列表）：
  1. "table" → `rules_block.table`，alt=["paragraph","reference"]
  2. "code" → `rules_block.code`，alt=[]
  3. "fence" → `rules_block.fence`，alt=["paragraph","reference","blockquote","list"]
  4. "blockquote" → `rules_block.blockquote`，alt=["paragraph","reference","blockquote","list"]
  5. "hr" → `rules_block.hr`，alt=["paragraph","reference","blockquote","list"]
  6. "list" → `rules_block.list_block`，alt=["paragraph","reference","blockquote"]
  7. "reference" → `rules_block.reference`，alt=[]
  8. "html_block" → `rules_block.html_block`，alt=["paragraph","reference","blockquote"]
  9. "heading" → `rules_block.heading`，alt=["paragraph","reference","blockquote"]
  10. "lheading" → `rules_block.lheading`，alt=[]
  11. "paragraph" → `rules_block.paragraph`，alt=[]
- F-060: `ParserBlock.tokenize(state, startLine, endLine)`：逐行解析块级内容
  - 跳过空行，检查缩进（sCount[line] < blkIndent 时终止嵌套）
  - 检查嵌套级别（level >= maxNesting 时跳至末尾）
  - 遍历所有block规则，找到第一个返回True的规则
  - 维护 tight/loose 列表状态
- F-061: `ParserBlock.parse(src, md, env, outTokens) -> list[Token] | None`：创建 StateBlock 并调用 tokenize

## ParserInline（parser_inline.py）

- F-062: `ParserInline` 类定义于 `parser_inline.py` L98
- F-063: `RuleFuncInlineType = Callable[[StateInline, bool], bool]`，签名：(state, silent) -> matched
- F-064: `RuleFuncInline2Type = Callable[[StateInline], None]`（后置处理规则）
- F-065: Inline规则链 `_rules` 按顺序包含12条规则：
  1. "text" → `rules_inline.text`
  2. "linkify" → `rules_inline.linkify`
  3. "newline" → `rules_inline.newline`
  4. "escape" → `rules_inline.escape`
  5. "backticks" → `rules_inline.backtick`
  6. "strikethrough" → `rules_inline.strikethrough.tokenize`
  7. "emphasis" → `rules_inline.emphasis.tokenize`
  8. "link" → `rules_inline.link`
  9. "image" → `rules_inline.image`
  10. "autolink" → `rules_inline.autolink`
  11. "html_inline" → `rules_inline.html_inline`
  12. "entity" → `rules_inline.entity`
- F-066: Inline后置规则链 `_rules2` 按顺序包含4条规则：
  1. "balance_pairs" → `rules_inline.link_pairs`
  2. "strikethrough" → `rules_inline.strikethrough.postProcess`
  3. "emphasis" → `rules_inline.emphasis.postProcess`
  4. "fragments_join" → `rules_inline.fragments_join`
- F-067: `ParserInline` 有两个 Ruler：`self.ruler`（主规则链）和 `self.ruler2`（后置处理链）
- F-068: `_DEFAULT_TERMINATORS` 是24个终止字符的 frozenset：`\n!#$%&*+-:<=>@[\]^_`{}~`
- F-069: `_default_terminator_re()` 使用 `@functools.cache` 懒编译默认终止符正则
- F-070: `ParserInline.add_terminator_char(ch)`：注册额外终止字符（供插件使用），动态重建 terminator_re
- F-071: `ParserInline.skipToken(state)`：以silent模式运行所有规则跳过一个token，使用cache缓存跳过位置
- F-072: `ParserInline.tokenize(state)`：逐字符解析行内内容，匹配规则时更新pos和tokens，不匹配时累积pending字符，最后pushPending
- F-073: `ParserInline.parse(src, md, env, tokens) -> list[Token]`：创建 StateInline，调用 tokenize，然后运行 ruler2 后置规则

## StateCore（rules_core/state_core.py）

- F-074: `StateCore` 继承 `StateBase`，定义于 `state_core.py` L13
- F-075: StateCore 属性：`src`（源码）、`md`（MarkdownIt实例）、`env`（环境）、`tokens: list[Token]`、`inlineMode: bool = False`

## StateBlock（rules_block/state_block.py）

- F-076: `StateBlock` 继承 `StateBase`，定义于 `state_block.py` L14
- F-077: StateBlock 在 `__init__` 中构建行缓存数组：
  - `bMarks: list[int]`：每行起始偏移
  - `eMarks: list[int]`：每行结束偏移
  - `tShift: list[int]`：每行首非空字符偏移（tabs未展开）
  - `sCount: list[int]`：每行缩进（tabs展开）
  - `bsCount: list[int]`：blockquote虚拟空格计数
  - 末尾追加一个fake entry简化边界检查
- F-078: StateBlock 解析状态变量：
  - `blkIndent: int = 0`：块内容缩进
  - `line: int = 0`、`lineMax: int`：当前行/最大行
  - `tight: bool = False`：紧凑/松散列表模式
  - `ddIndent: int = -1`：定义列表缩进
  - `listIndent: int = -1`：列表缩进
  - `parentType: str = "root"`：父节点类型（"blockquote"/"list"/"root"/"paragraph"/"reference"）
  - `level: int = 0`：嵌套级别
  - `tokens: list[Token]`、`env`、`md`、`src`
- F-079: StateBlock 方法：
  - `push(ttype, tag, nesting) -> Token`：创建Token并添加到流，自动管理level
  - `isEmpty(line) -> bool`：判断行是否为空
  - `skipEmptyLines(from_pos) -> int`：跳过空行
  - `skipSpaces(pos) -> int`/`skipSpacesBack(pos, minimum) -> int`：跳过空格
  - `skipChars(pos, code) -> int`/`skipCharsStr(pos, ch) -> int`：跳过指定字符
  - `skipCharsBack(pos, code, minimum) -> int`/`skipCharsStrBack(pos, ch, minimum) -> int`：反向跳过
  - `getLines(begin, end, indent, keepLastLF) -> str`：从源码截取行范围
  - `is_code_block(line) -> bool`：判断是否为代码块（缩进>=4且code规则启用）

## StateInline（rules_inline/state_inline.py）

- F-080: `StateInline` 继承 `StateBase`，定义于 `state_inline.py` L44
- F-081: StateInline 属性：
  - `pos: int = 0`、`posMax: int = len(src)`：当前/最大位置
  - `level: int = 0`：嵌套级别
  - `pending: str = ""`：待推送文本累积
  - `pendingLevel: int = 0`：pending文本的级别
  - `cache: dict[int, int] = {}`：{start:end} 缓存（用于成对解析回溯优化）
  - `delimiters: list[Delimiter] = []`：强调分隔符列表
  - `_prev_delimiters: list[list[Delimiter]] = []`：上层标签的分隔符栈
  - `backticks: dict[int, int] = {}`：反引号长度→最后位置映射
  - `backticksScanned: bool = False`
  - `linkLevel: int = 0`：链接嵌套级别（禁用linkify）
  - `tokens: list[Token]`、`tokens_meta: list[dict|None]`
- F-082: `Delimiter` 是 `@dataclass(slots=True)` 类，字段：`marker: int`、`length: int`、`token: int`、`end: int`、`open: bool`、`close: bool`、`level: bool|None = None`
- F-083: `Scanned` 是 NamedTuple，字段：`can_open: bool`、`can_close: bool`、`length: int`
- F-084: StateInline 方法：
  - `pushPending() -> Token`：将pending文本作为text token推送
  - `push(ttype, tag, nesting) -> Token`：推送新token，自动管理level和delimiters栈
  - `scanDelims(start, canSplitWord) -> Scanned`：扫描强调分隔符，判断can_open/can_close

## 核心规则（rules_core/）

- F-085: `normalize(state)`（rules_core/normalize.py）：将 `\r\n?|\n` 替换为 `\n`，将 `\0` 替换为 `\ufffd`
- F-086: `block(state)`（rules_core/block.py）：inlineMode 时创建单个inline token；否则调用 `state.md.block.parse(state.src, state.md, state.env, state.tokens)`
- F-087: `inline(state)`（rules_core/inline.py）：遍历所有type=="inline"的token，对其content调用 `state.md.inline.parse()` 填充children
- F-088: rules_core 目录包含：`__init__.py`, `block.py`, `inline.py`, `linkify.py`, `normalize.py`, `replacements.py`, `smartquotes.py`, `state_core.py`, `text_join.py`

## 块级规则（rules_block/）

- F-089: rules_block 目录包含13个文件：`__init__.py`, `blockquote.py`, `code.py`, `fence.py`, `heading.py`, `hr.py`, `html_block.py`, `lheading.py`, `list.py`, `paragraph.py`, `reference.py`, `state_block.py`, `table.py`
- F-090: 所有block规则函数签名为 `func(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool`

## 行内规则（rules_inline/）

- F-091: rules_inline 目录包含17个文件：`__init__.py`, `autolink.py`, `backticks.py`, `balance_pairs.py`, `emphasis.py`, `entity.py`, `escape.py`, `fragments_join.py`, `html_inline.py`, `image.py`, `link.py`, `linkify.py`, `newline.py`, `state_inline.py`, `strikethrough.py`, `text.py`
- F-092: 主inline规则函数签名为 `func(state: StateInline, silent: bool) -> bool`
- F-093: 后置规则（ruler2）函数签名为 `func(state: StateInline) -> None`

## 配置预设（presets/）

- F-094: `commonmark` 预设：maxNesting=20, html=True, linkify=False, typographer=False, xhtmlOut=True, breaks=False, langPrefix="language-", highlight=None
  - core规则：["normalize", "block", "inline", "text_join"]
  - block规则：["blockquote","code","fence","heading","hr","html_block","lheading","list","reference","paragraph"]（不含table）
  - inline规则：["autolink","backticks","emphasis","entity","escape","html_inline","image","link","newline","text"]（不含strikethrough、linkify）
  - inline2规则：["balance_pairs","emphasis","fragments_join"]
- F-095: `default`（js_default）预设：maxNesting=100, html=False, xhtmlOut=False, 其余options同commonmark；components为空字典（启用所有默认规则）
- F-096: `zero` 预设：最小配置，block仅"paragraph"，inline仅"text"，inline2为["balance_pairs","fragments_join"]
- F-097: `gfm_like` 预设：基于commonmark，添加linkify/core、table/block、strikethrough+linkify/inline、strikethrough/inline2，options.linkify=True, html=True
- F-098: `gfm_like2` 预设：基于gfm_like，添加tasklists=True, alerts=True, strikethrough_single_tilde=True, tasklists_editable=False

## OptionsDict（utils.py）

- F-099: `OptionsType` TypedDict 字段：maxNesting(int), html(bool), linkify(bool), typographer(bool), quotes(str), xhtmlOut(bool), breaks(bool), langPrefix(str), highlight(Callable|None)；可选字段：store_labels(bool), tasklists(bool), alerts(bool), tasklists_editable(bool), strikethrough_single_tilde(bool)
- F-100: `OptionsDict` 类实现 MutableMapping 接口，同时提供属性访问器（.maxNesting, .html, .linkify 等），内部存储在 `self._options` dict 中
- F-101: `EnvType = MutableMapping[str, Any]`：环境沙箱类型别名

## SyntaxTreeNode（tree.py）

- F-102: `SyntaxTreeNode` 类定义于 `tree.py` L23（Python扩展，非JS上游所有）
- F-103: `_NesterTokens` 是 NamedTuple，字段：`opening: Token`, `closing: Token`
- F-104: SyntaxTreeNode 节点三种形态：
  - 根节点（is_root=True）：token=None, nester_tokens=None
  - 单个token节点（self.token 非 None）：非嵌套token
  - 容器节点（self.nester_tokens 非 None）：_open/_close token对及其间子节点
- F-105: SyntaxTreeNode 属性：`token`, `nester_tokens`, `parent`, `children`, `type`（root / token.type / opening.type去掉"_open"后缀）
- F-106: SyntaxTreeNode 方法：
  - `__init__(tokens=(), *, create_root=True)`：从token流构建树
  - `to_tokens() -> list[Token]`：递归还原线性token流
  - `__getitem__(item)`：下标/切片访问children
  - `walk(*, include_self=True) -> Generator`：深度优先遍历
  - `pretty(indent=2, show_text=False) -> str`：XML风格树字符串
  - 属性代理：tag, attrs, map, level, content, markup, info, meta, block, hidden 均代理到 nester_tokens.opening 或 self.token
- F-107: `_set_children_from_tokens(tokens)` 内部方法：使用栈算法从token序列构建子树，遇到nesting=1入栈，nesting=-1出栈配对

## 工具函数（common/utils.py）

- F-108: `isValidEntityCode(c) -> bool`：验证Unicode码点是否合法（排除代理对0xD800-0xDFFF、非字符0xFDD0-0xFDEF、控制字符等）
- F-109: `escapeHtml(raw) -> str`：转义 &<>" 为HTML实体（不转义单引号）
- F-110: `unescapeAll(string) -> str`：反转义 \\反斜杠转义 和 HTML实体
- F-111: `isWhiteSpace(code) -> bool`：判断是否Unicode空白字符（Zs类+\t\f\v\r\n）
- F-112: `isMdAsciiPunct(ch) -> bool`：判断是否Markdown ASCII标点字符（32个标点符号）
- F-113: `isPunctChar(ch) -> bool`：判断是否Unicode标点字符（P/S类）
- F-114: `normalizeReference(string) -> str`：规范化引用标签（collapse空白，lower().upper()大小写折叠）
- F-115: `isLinkOpen(string) -> bool`/`isLinkClose(string) -> bool`：检测HTML `<a>` 开/闭标签

## CLI（cli/parse.py）

- F-116: CLI `main(args=None) -> int`：支持三种模式——文件转换（filenames参数）、标准输入（--stdin）、交互模式（无参数时REPL）
- F-117: CLI 使用 argparse，参数：-v/--version, --stdin, filenames（nargs="*"）
- F-118: 交互模式支持多行输入，Ctrl-D完成解析，Ctrl-C退出

## helpers/ 辅助模块

- F-119: helpers/ 目录包含3个解析辅助模块：`parse_link_destination.py`, `parse_link_label.py`, `parse_link_title.py`，提供链接目标、标签、标题的解析函数
- F-120: common/ 目录包含：`entities.py`（HTML实体映射）、`html_blocks.py`（HTML块级元素规则）、`html_re.py`（HTML正则）、`normalize_url.py`（URL验证/规范化）、`utils.py`（通用工具函数）
