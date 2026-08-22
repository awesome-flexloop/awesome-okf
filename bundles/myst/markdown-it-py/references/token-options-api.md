---
type: Reference
title: Token 与 Options API 参考
description: Token 类完整字段/方法签名速查，OptionsType 全部选项说明
tags: [markdown-it-py, token, options, api, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:05:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: markdown-it-py-repo
    resource: https://github.com/executablebooks/markdown-it-py
    title: markdown-it-py GitHub Repository
---

# Token 与 Options API 参考

本文档提供 Token 类和 OptionsType 的完整字段/方法速查。

## Token 字段一览

`Token` 是 `@dataclass(slots=True)` 类，构造签名：

```python
Token(
    type: str,           # Token类型，如 "paragraph_open", "text", "inline"
    tag: str,            # HTML标签名，如 "p", "", "em"
    nesting: Literal[-1, 0, 1],  # 1=开标签, 0=自闭合, -1=闭标签
    attrs: dict = {},    # HTML属性字典
    map: list[int] | None = None,  # 源码映射 [line_begin, line_end]
    level: int = 0,      # 嵌套级别
    children: list[Token] | None = None,  # 子tokens（inline容器）
    content: str = "",   # 自闭合标签内容
    markup: str = "",    # 标记符号（*, _, ```等）
    info: str = "",      # 附加信息
    meta: dict = {},     # 插件元数据
    block: bool = False, # 是否为块级token
    hidden: bool = False,# 渲染时是否忽略
)
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | `str` | 必填 | Token类型标识符 |
| `tag` | `str` | 必填 | HTML标签名 |
| `nesting` | `Literal[-1,0,1]` | 必填 | 开标签=1, 自闭合=0, 闭标签=-1 |
| `attrs` | `dict[str, str\|int\|float]` | `{}` | HTML属性键值对 |
| `map` | `list[int] \| None` | `None` | 源码行映射 |
| `level` | `int` | `0` | 嵌套层级 |
| `children` | `list[Token] \| None` | `None` | 子token列表 |
| `content` | `str` | `""` | 文本/代码内容 |
| `markup` | `str` | `""` | 标记符号串 |
| `info` | `str` | `""` | 附加信息字符串 |
| `meta` | `dict` | `{}` | 插件自定义数据 |
| `block` | `bool` | `False` | 块级/行内标记 |
| `hidden` | `bool` | `False` | 渲染隐藏标记 |

## Token 方法一览

| 方法 | 签名 | 说明 |
|------|------|------|
| `attrIndex` | `(name: str) -> int` | 已废弃（UserWarning），返回属性索引 |
| `attrItems` | `() -> list[tuple[str, str\|int\|float]]` | 返回属性键值对列表 |
| `attrPush` | `(attrData: tuple[str, str\|int\|float]) -> None` | 添加属性 |
| `attrSet` | `(name: str, value: str\|int\|float) -> None` | 设置属性值 |
| `attrGet` | `(name: str) -> str\|int\|float\|None` | 获取属性值 |
| `attrJoin` | `(name: str, value: str) -> None` | 空格拼接属性值（用于class） |
| `copy` | `(**changes) -> Token` | 浅拷贝（dataclasses.replace） |
| `as_dict` | `(children=True, as_upstream=True, ...) -> MutableMapping` | 转为字典（as_upstream时attrs为list格式） |
| `from_dict` | `(dct: MutableMapping) -> Token` | 类方法，从字典构造Token |

## OptionsType 选项一览

| 选项 | 类型 | commonmark默认 | 说明 |
|------|------|---------------|------|
| `maxNesting` | `int` | 20 | 递归保护限制（default预设为100） |
| `html` | `bool` | True | 允许源码中的HTML标签 |
| `linkify` | `bool` | False | 自动将URL文本转为链接（需linkify-it-py） |
| `typographer` | `bool` | False | 启用替换+智能引号 |
| `quotes` | `str` | `"\u201c\u201d\u2018\u2019"` | 引号替换字符（""''） |
| `xhtmlOut` | `bool` | True | 自闭合标签使用`/`（`<br />` vs `<br>`） |
| `breaks` | `bool` | False | 段落内换行转为`<br>` |
| `langPrefix` | `str` | `"language-"` | 围栏代码块CSS语言前缀 |
| `highlight` | `Callable\|\|None` | None | 代码高亮函数 `(content, lang, attrs) -> str` |
| `store_labels` | `bool` | （可选） | 在token.meta中存储链接标签（Python特有） |
| `tasklists` | `bool` | （可选） | GFM任务列表复选框检测 |
| `alerts` | `bool` | （可选） | GitHub风格告警块（> [!NOTE]） |
| `tasklists_editable` | `bool` | （可选） | 任务列表复选框可交互 |
| `strikethrough_single_tilde` | `bool` | （可选） | 允许单波浪线`~text~`删除线 |

## 预设快速对比

| 选项 | zero | commonmark | default | gfm-like | gfm-like2 |
|------|------|-----------|---------|----------|-----------|
| maxNesting | 20 | 20 | 100 | 20 | 20 |
| html | False | True | False | True | True |
| xhtmlOut | False | True | False | True | True |
| linkify | False | False | False | True | True |
| table | - | ❌ | ✅ | ✅ | ✅ |
| strikethrough | - | ❌ | ✅ | ✅ | ✅(单~) |
| tasklists | - | ❌ | ❌ | ❌ | ✅ |
| alerts | - | ❌ | ❌ | ❌ | ✅ |

## MarkdownIt 公共 API 签名

```python
class MarkdownIt:
    def __init__(self, config: str|PresetType = "commonmark",
                 options_update: Mapping|None = None, *,
                 renderer_cls: Callable = RendererHTML)
    def parse(src: str, env: EnvType|None = None) -> list[Token]
    def render(src: str, env: EnvType|None = None) -> str
    def parseInline(src: str, env: EnvType|None = None) -> list[Token]
    def renderInline(src: str, env: EnvType|None = None) -> str
    def enable(names: str|Iterable[str], ignoreInvalid: bool = False) -> MarkdownIt
    def disable(names: str|Iterable[str], ignoreInvalid: bool = False) -> MarkdownIt
    def use(plugin: Callable, *params, **options) -> MarkdownIt
    def set(options: OptionsType) -> None
    def configure(presets: str|PresetType, options_update=None) -> MarkdownIt
    def add_render_rule(name: str, function: Callable, fmt: str = "html") -> None
    def get_all_rules() -> dict[str, list[str]]
    def get_active_rules() -> dict[str, list[str]]
    def validateLink(url: str) -> bool
    def normalizeLink(url: str) -> str
    def normalizeLinkText(link: str) -> str
    def reset_rules() -> contextmanager  # 上下文管理器
```

## 相关概念

- [Token 流模型](/concepts/03-token-stream.md)
- [预设与选项](/concepts/02-presets-and-options.md)
- [渲染器详解](/concepts/10-renderer.md)
- [插件系统](/concepts/12-plugin-system.md)
