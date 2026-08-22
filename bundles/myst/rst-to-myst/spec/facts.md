---
type: spec
title: rst-to-myst 事实清单
description: rst-to-myst 源码事实清单
tags:
- rst-to-myst
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: rst-to-myst-source
  resource: /references/source-cli.md
  title: rst-to-myst source-cli
- id: rst-to-myst-source-1
  resource: /references/source-markdownit.md
  title: rst-to-myst source-markdownit
- id: rst-to-myst-source-2
  resource: /references/source-mdformat-render.md
  title: rst-to-myst source-mdformat-render
- id: rst-to-myst-source-3
  resource: /references/source-namespace.md
  title: rst-to-myst source-namespace
- id: rst-to-myst-source-4
  resource: /references/source-parser.md
  title: rst-to-myst source-parser
---

# rst-to-myst 事实清单

> 零推断事实采集，所有事实可在源码中直接验证。

## 包元数据

- **F-001**: 包版本为 `0.4.0`，定义于 `rst_to_myst/__init__.py:9`
- **F-002**: CLI 入口点注册为 `rst2myst = "rst_to_myst.cli:main"`，定义于 `pyproject.toml:38`
- **F-003**: 要求 Python 版本 `>=3.9`，定义于 `pyproject.toml:22`
- **F-004**: 运行时依赖包含 `docutils>=0.17,<0.22`、`pyyaml`、`markdown-it-py~=2.0`、`mdformat~=0.7.16`、`mdformat-myst~=0.1.5`、`mdformat-deflist~=0.1.2`、`click>=7.1,<9`，定义于 `pyproject.toml:23-31`
- **F-005**: 可选依赖 `sphinx = ["sphinx>=5,<7"]`，定义于 `pyproject.toml:41`
- **F-006**: `__init__.py` 导出三个名称：`compile_namespace`、`rst_to_myst`、`to_docutils_ast`，位于 `__init__.py:7`

## 公开 API 函数

- **F-007**: `to_docutils_ast(text, uri, report_level, halt_level, warning_stream, language_code, use_sphinx, extensions, default_domain, conversions, front_matter, namespace)` 函数位于 `parser.py:139-218`，返回 `tuple[nodes.document, StringIO]`
- **F-008**: `rst_to_myst(text, *, warning_stream, language_code, use_sphinx, extensions, conversions, default_domain, default_role, raise_on_warning, cite_prefix, consecutive_numbering, colon_fences, dollar_math)` 函数位于 `mdformat_render.py:182-246`，返回 `ConvertedOutput`
- **F-009**: `compile_namespace(extensions, use_sphinx, default_domain, language_code)` 函数位于 `namespace.py:178-252`，返回 `ApplicationNamespace`
- **F-010**: `ConvertedOutput` 是 NamedTuple，包含字段 `text: str`、`tokens: list[Token]`、`env: dict[str, Any]`、`warning_stream: IO`、`extensions: set[str]`，位于 `mdformat_render.py:172-179`

## CLI 命令

- **F-011**: CLI 基于 click，主组为 `main()`，位于 `cli.py:13-16`
- **F-012**: `ast` 子命令读取 RST 文件并打印 docutils AST，位于 `cli.py:185-204`
- **F-013**: `tokens` 子命令读取 RST 文件并打印 Markdown-It tokens（YAML格式），位于 `cli.py:207-246`
- **F-014**: `stream` 子命令读取 RST 文件/stdin 并输出 MyST Markdown 文本，位于 `cli.py:249-291`
- **F-015**: `convert` 子命令批量转换文件（支持目录、dry-run、replace-files、stop-on-fail），输出扩展名为 `.md`，位于 `cli.py:294-367`
- **F-016**: `directives list` 子命令列出所有可用指令，位于 `cli.py:375-381`
- **F-017**: `directives show <name>` 子命令显示单个指令的元数据，位于 `cli.py:384-398`
- **F-018**: `roles list` 子命令列出所有可用角色，位于 `cli.py:406-412`
- **F-019**: `roles show <name>` 子命令显示单个角色的元数据，位于 `cli.py:415-429`

## CLI 选项

- **F-020**: `--config` 选项读取 YAML 配置文件（is_eager=True），位于 `cli.py:36-43`
- **F-021**: `--language/-l` 选项设置语言代码，默认 `"en"`，位于 `cli.py:46-53`
- **F-022**: `--sphinx/--no-sphinx` 选项控制是否加载 Sphinx，默认 `True`，位于 `cli.py:117-124`
- **F-023**: `--extensions/-e` 选项指定逗号分隔的 Sphinx 扩展列表，位于 `cli.py:134-140`
- **F-024**: `--default-domain/-dd` 选项设置默认 Sphinx 域，默认 `"py"`，位于 `cli.py:142-148`
- **F-025**: `--default-role/-dr` 选项设置默认角色，默认 `None`（转换为字面量），位于 `cli.py:149-154`
- **F-026**: `--cite-prefix/-cp` 选项设置引用前缀，默认 `"cite"`，位于 `cli.py:155-161`
- **F-027**: `--consecutive-numbering/--no-consecutive-numbering` 选项控制有序列表连续编号，默认 `True`，位于 `cli.py:165-170`
- **F-028**: `--colon-fences/--no-colon-fences` 选项控制冒号围栏语法，默认 `True`，位于 `cli.py:171-176`
- **F-029**: `--dollar-math/--no-dollar-math` 选项控制美元数学公式语法，默认 `True`，位于 `cli.py:177-182`
- **F-030**: `--conversions/-c` 选项指定 YAML 文件映射指令转换规则，位于 `cli.py:94-102`
- **F-031**: `--encoding` 选项设置读写编码，默认 `"utf8"`，位于 `cli.py:65-67`
- **F-032**: `convert` 子命令额外选项：`--dry-run/-d`、`--replace-files/-R`、`--stop-on-fail/-S`、`--raise-on-warning/-W`，位于 `cli.py:296-299,162-163`

## 解析器架构

- **F-033**: `LosslessRSTParser` 继承自 `docutils.parsers.rst.Parser`，位于 `parser.py:30-42`
- **F-034**: `LosslessRSTParser.inliner` 设置为 `InlinerMyst()` 实例，位于 `parser.py:42`
- **F-035**: `LosslessRSTParser.state_classes` 通过 `get_state_classes()` 获取，位于 `parser.py:38`
- **F-036**: `to_docutils_ast` 函数应用以下 docutils Transform：`PropagateTargets`、`FrontMatter`、`AnonymousHyperlinks`、`Footnotes`、`StripFootnoteLabel`、`ResolveListItems`，位于 `parser.py:205-216`

## 自定义 Docutils Transforms

- **F-037**: `IndirectHyperlinks(Transform)` 解析间接超链接但不解析实际引用，位于 `parser.py:45-53`
- **F-038**: `StripFootnoteLabel(Transform)` 移除脚注和引用的 label 子节点，位于 `parser.py:56-64`
- **F-039**: `ResolveListItems(Transform)` 为列表项传播 bullet/prefix 属性，支持 arabic/lowerroman/upperroman/loweralpha/upperalpha 编号类型，位于 `parser.py:67-106`
- **F-040**: `FrontMatter(Transform)` 将文档开头的 field_list 提取为 `FrontMatterNode`，位于 `parser.py:109-129`

## 自定义节点类型

- **F-041**: `UnprocessedText(nodes.Text)` - 不做转义处理的文本，位于 `nodes.py:6-7`
- **F-042**: `EvalRstNode(nodes.Element)` - 包含 eval-rst 替换内容，位于 `nodes.py:10-11`
- **F-043**: `RoleNode(nodes.Element)` - 角色节点，位于 `nodes.py:14-15`
- **F-044**: `DirectiveNode(nodes.Element)` - 指令节点，包含 name/module/conversion/options_list 属性，可选 ArgumentNode 和 ContentNode 子节点，位于 `nodes.py:18-38`
- **F-045**: `ArgumentNode(nodes.Element)` - 指令参数节点，位于 `nodes.py:41-42`
- **F-046**: `ContentNode(nodes.Element)` - 指令内容节点，位于 `nodes.py:45-46`
- **F-047**: `FrontMatterNode(nodes.Element)` - 文档开头的 front matter 节点，位于 `nodes.py:49-50`

## 命名空间系统

- **F-048**: `ApplicationNamespace` 类是 `sphinx.application.Sphinx` 的 Mock 对象，位于 `namespace.py:31-175`
- **F-049**: `ApplicationNamespace` 维护 `extensions`、`directives`、`roles`、`domains`、`default_domain`、`language_module` 属性，位于 `namespace.py:38-48`
- **F-050**: `DomainMock` 类模拟 Sphinx 域，包含 name/directives/roles 属性，位于 `namespace.py:21-28`
- **F-051**: `compile_namespace` 函数使用线程锁（`LOCK = threading.Lock()`）保护全局状态修改，位于 `namespace.py:18,218-250`
- **F-052**: `compile_namespace` 先注册 docutils 标准指令和角色，然后加载 Sphinx 内置扩展和用户指定扩展，位于 `namespace.py:195-245`
- **F-053**: 元素查找优先级：语言翻译→指定域→默认域→std域→全局位置，位于 `namespace.py:85-117`

## MarkdownIt 渲染器

- **F-054**: `MarkdownItRenderer` 继承自 `nodes.GenericNodeVisitor`，位于 `markdownit.py:17`
- **F-055**: `MarkdownItRenderer` 构造参数：document、warning_stream、raise_on_warning、cite_prefix、default_role、colon_fences、dollar_math，位于 `markdownit.py:20-39`
- **F-056**: `RenderOutput` 是 NamedTuple，包含 `tokens: list[Token]` 和 `env: dict[str, Any]`，位于 `markdownit.py:12-14`
- **F-057**: `to_tokens()` 方法调用 `document.walkabout(self)` 遍历 AST，然后前置 front-matter tokens，位于 `markdownit.py:63-81`
- **F-058**: `add_token()` 方法自动处理 paragraph/heading/th/td/dt 的 open/close 时插入 inline token，位于 `markdownit.py:96-128`
- **F-059**: 标题通过 `heading_open`/`heading_close` token 渲染，markup 为对应数量的 `#`，位于 `markdownit.py:178-184`
- **F-060**: tight list 中的 paragraph token 标记为 `hidden=True`，位于 `markdownit.py:191-193`

## mdformat 渲染集成

- **F-061**: `from_tokens()` 函数创建 `MDRenderer` 实例，加载 myst/tables/frontmatter/deflist 扩展和 AdditionalRenderers，位于 `mdformat_render.py:112-150`
- **F-062**: `AdditionalRenderers.RENDERERS` 注册四个自定义渲染器：unprocessed、front_matter_tokens、substitution_block/substitution_inline、directive，位于 `mdformat_render.py:102-109`
- **F-063**: `_directive_render` 函数输出 MyST 指令围栏格式：反引号/冒号/波浪号围栏包裹 `{name}`，可选参数行、YAML 选项块、内容，位于 `mdformat_render.py:45-99`
- **F-064**: `_front_matter_tokens_renderer` 函数输出 YAML front matter，格式为 `---\nYAML\n---`，位于 `mdformat_render.py:21-37`
- **F-065**: `_sub_renderer` 输出替换语法 `{{ content }}`，位于 `mdformat_render.py:40-42`
- **F-066**: `get_myst_extensions(tokens)` 函数根据 token 类型推断所需 MyST 扩展：substitution、colon_fence、dollarmath、deflist，位于 `mdformat_render.py:153-169`
- **F-067**: 渲染时设置 `finalize=False`，然后手动输出所有引用定义（不仅是使用过的），位于 `mdformat_render.py:139-144`

## 指令数据

- **F-068**: 默认指令转换映射从 `rst_to_myst/data/directives.yml` 加载，使用 `@lru_cache` 缓存，位于 `parser.py:132-136`
- **F-069**: YAML 序列化使用自定义 `YamlDumper`，多行字符串使用 `|` 块标量样式，位于 `utils.py:11-18`

## 枚举类型转换

- **F-070**: 支持的枚举编号类型：arabic、lowerroman、upperroman、loweralpha、upperalpha，位于 `parser.py:67-73`
- **F-071**: markdown-it 仅支持数字编号，TODO 注释表明非数字编号类型未完全支持，位于 `parser.py:98-101`
