---
type: Reference
title: markdown-it-py 源码路径映射
description: markdown-it-py 核心源文件路径、职责与关键代码位置索引，覆盖全部核心模块
tags: [markdown-it-py, markdown, parser, source, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: markdown-it-py-repo
    resource: https://github.com/executablebooks/markdown-it-py
    title: markdown-it-py GitHub Repository
---

# markdown-it-py 源码路径映射

本文档为 markdown-it-py 源码的文件级索引，标注每个核心文件的路径、职责和关键代码。源路径相对于 `external/libs/ai/executablebooks/markdown-it-py/markdown_it/`。

## 项目元数据

| 属性 | 值 |
|------|-----|
| 名称 | markdown-it-py |
| 版本 | 4.2.0 |
| 描述 | Python port of markdown-it. Markdown parsing, done right! |
| 许可证 | MIT |
| Python 要求 | >=3.10 |
| 构建系统 | flit_core >=3.4,<4 |
| 运行时依赖 | mdurl~=0.1 |
| CLI 入口 | `markdown-it = markdown_it.cli.parse:main` |
| 项目主页 | https://github.com/executablebooks/markdown-it-py |

## 核心文件清单

| 文件 | 职责 | 关键代码 |
|------|------|---------|
| `__init__.py` | 包入口，导出 MarkdownIt 类和版本号 | `__all__` L3、`__version__ = "4.2.0"` L4 |
| `main.py` | MarkdownIt 主类（解析器入口） | `class MarkdownIt` L33、`parse()` L252、`render()` L275、`use()` L235、`enable/disable` L160/L192、`configure()` L104 |
| `token.py` | Token 数据类 | `@dataclass class Token` L22、nesting/attrs/children/level等字段 L23-75、attrSet/attrGet/attrJoin/copy/as_dict 方法 |
| `ruler.py` | Ruler 规则管理器 + StateBase 基类 | `class Ruler` L75、push/before/after/at/enable/disable/getRules L110-267、`class Rule` L68、`class StateBase` L32 |
| `renderer.py` | HTML 渲染器 | `class RendererHTML` L28、`render()` L67、`renderToken()` L109、`renderInline()` L90、内置渲染规则 L212-356 |
| `tree.py` | SyntaxTreeNode 语法树（Python扩展） | `class SyntaxTreeNode` L23、`_set_children_from_tokens()` L198、`to_tokens()` L90、`walk()` L244、`pretty()` L222 |
| `parser_core.py` | ParserCore 核心规则链 | `class ParserCore` L37、7条核心规则 L26-34、`process()` L43 |
| `parser_block.py` | ParserBlock 块级解析器 | `class ParserBlock` L48、11条块级规则 L27-45、`tokenize()` L60、`parse()` L105 |
| `parser_inline.py` | ParserInline 行内解析器 | `class ParserInline` L98、12+4条行内规则 L67-95、`tokenize()` L174、`skipToken()` L132、`add_terminator_char()` L114 |
| `utils.py` | 类型定义与工具函数 | `OptionsType` L18、`PresetType` L54、`OptionsDict` L63、`EnvType` L12、`read_fixture_file()` L175 |

## 状态对象

| 文件 | 职责 | 关键代码 |
|------|------|---------|
| `rules_core/state_core.py` | StateCore 全局解析状态 | `class StateCore` L13、src/md/env/tokens/inlineMode |
| `rules_block/state_block.py` | StateBlock 块级解析状态 | `class StateBlock` L14、bMarks/eMarks/tShift/sCount 行缓存 L31-48、push() L119、行工具方法 L131-261 |
| `rules_inline/state_inline.py` | StateInline 行内解析状态 | `class StateInline` L44、pos/pending/delimiters/backticks/cache L54-76、`class Delimiter` L16、`class Scanned` L38、push()/pushPending()/scanDelims() |

## 规则模块

### 核心规则（rules_core/）

| 文件 | 规则名 | 职责 |
|------|--------|------|
| `normalize.py` | normalize | 换行符规范化（\\r\\n?\\|\\n→\\n）、NULL替换 |
| `block.py` | block | 调度 ParserBlock.parse（或inlineMode时创建inline token） |
| `inline.py` | inline | 遍历inline tokens，调度 ParserInline.parse 填充children |
| `linkify.py` | linkify | 自动链接转换（需linkify-it-py） |
| `replacements.py` | replacements | 排版替换（--→—等） |
| `smartquotes.py` | smartquotes | 智能引号替换 |
| `text_join.py` | text_join | 合并相邻text tokens |

### 块级规则（rules_block/）

| 规则名 | 文件 | 职责 |
|--------|------|------|
| table | `table.py` | GFM 表格解析 |
| code | `code.py` | 缩进代码块（4空格缩进） |
| fence | `fence.py` | 围栏代码块（```或~~~） |
| blockquote | `blockquote.py` | 引用块（>） |
| hr | `hr.py` | 水平分隔线（---/___/***） |
| list | `list.py` | 有序/无序列表 |
| reference | `reference.py` | 链接引用定义（[label]: url） |
| html_block | `html_block.py` | HTML 块级元素 |
| heading | `heading.py` | ATX 标题（#） |
| lheading | `lheading.py` | Setext 标题（===/---下划线） |
| paragraph | `paragraph.py` | 段落（兜底规则） |

### 行内规则（rules_inline/）

| 规则名 | 文件 | 职责 |
|--------|------|------|
| text | `text.py` | 纯文本（累积pending字符） |
| linkify | `linkify.py` | 行内自动链接 |
| newline | `newline.py` | 换行符（hardbreak/softbreak） |
| escape | `escape.py` | 反斜杠转义 |
| backticks | `backticks.py` | 行内代码（\`code\`） |
| strikethrough | `strikethrough.py` | 删除线（~~text~~），含tokenize/postProcess |
| emphasis | `emphasis.py` | 强调（*em*/**strong**），含tokenize/postProcess |
| link | `link.py` | 链接（``[text](url)``） |
| image | `image.py` | 图片（!``[alt](url)``） |
| autolink | `autolink.py` | 自动链接（<url>） |
| html_inline | `html_inline.py` | 行内HTML标签 |
| entity | `entity.py` | HTML实体（&amp;等） |
| balance_pairs | `balance_pairs.py` | 成对标记平衡处理（ruler2） |
| fragments_join | `fragments_join.py` | 合并未使用的分隔符片段（ruler2） |

## 预设（presets/）

| 文件 | 预设名 | 特点 |
|------|--------|------|
| `commonmark.py` | commonmark（默认） | 严格CommonMark，html=True, xhtmlOut=True, maxNesting=20 |
| `default.py` | default/js_default | 全规则启用，html=False, xhtmlOut=False, maxNesting=100 |
| `zero.py` | zero | 最小配置（仅paragraph+text） |
| `__init__.py` | gfm_like | commonmark+table+strikethrough+linkify |
| `__init__.py` | gfm_like2 | gfm_like+tasklists+alerts+single_tilde_strikethrough |

## 辅助模块

| 目录/文件 | 职责 |
|-----------|------|
| `common/utils.py` | 通用工具：escapeHtml、unescapeAll、isWhiteSpace、isMdAsciiPunct、normalizeReference、isValidEntityCode等 |
| `common/entities.py` | HTML实体名称→字符映射字典 |
| `common/html_blocks.py` | HTML块级元素规则 |
| `common/html_re.py` | HTML标签正则表达式 |
| `common/normalize_url.py` | URL验证与规范化（validateLink/normalizeLink/normalizeLinkText） |
| `helpers/parse_link_destination.py` | 链接目标解析 |
| `helpers/parse_link_label.py` | 链接标签解析 |
| `helpers/parse_link_title.py` | 链接标题解析 |
| `cli/parse.py` | CLI 接口（main函数、文件/STDIN/交互模式） |

## 构建与配置文件

| 文件 | 说明 |
|------|------|
| `pyproject.toml` | 项目元数据、依赖、CLI入口、Ruff/Mypy/pytest配置 |
| `LICENSE` | MIT 许可证 |
| `README.md` | 项目简介 |
| `CHANGELOG.md` | 版本变更记录 |

## 相关概念

- [markdown-it-py 简介](/concepts/00-introduction.md)
- [Token 流模型](/concepts/03-token-stream.md)
- [解析管线架构](/concepts/04-parsing-pipeline.md)
- [Ruler 规则管理](/concepts/05-ruler.md)
