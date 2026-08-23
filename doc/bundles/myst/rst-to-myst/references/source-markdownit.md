---
type: Reference
title: rst-to-myst MarkdownIt 渲染器
description: markdownit.py 实现 MarkdownItRenderer 将 docutils AST 转换为 markdown-it tokens。
tags: [source-code, markdown-it, token, renderer, ast]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-markdownit
    resource: /spec/facts.md
    title: rst-to-myst 事实清单
---

## 模块概览

`rst_to_myst/markdownit.py` 实现 docutils AST 到 markdown-it token 流的转换（约600行，此处记录核心机制）。

## 核心类

### `MarkdownItRenderer(nodes.GenericNodeVisitor)`

docutils 节点访问者，遍历 AST 生成 markdown-it token 流。继承自 `docutils.nodes.GenericNodeVisitor`。

#### 构造参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `document` | 必填 | docutils document 节点 |
| `warning_stream` | StringIO | 警告输出流 |
| `raise_on_warning` | `False` | 警告时是否抛异常 |
| `cite_prefix` | `"cite_"` | 引用标签前缀 |
| `default_role` | `None` | 默认角色（None则转字面量） |
| `colon_fences` | `True` | 是否使用冒号围栏 |
| `dollar_math` | `True` | 是否使用美元数学 |

#### 核心方法

##### `to_tokens() -> RenderOutput`

重置状态，调用 `document.walkabout(self)` 遍历 AST，前置 front-matter tokens，返回 `RenderOutput(tokens, env)`。

##### `add_token(ttype, tag, nesting, *, content="", **kwargs) -> Token`

向 token 流添加 token，自动处理：
- 跟踪 `parent_tokens` 栈（记录 `_open/_close` 配对）
- 遇到 paragraph_open/heading_open/th_open/td_open/dt_open 时自动创建 inline 子 token
- 遇到对应 close 时关闭 inline 容器
- 已有 inline 容器时，新 token 添加为 inline 的 children

##### `nested_parse(nodes) -> list[Token]`

创建新的 MarkdownItRenderer 实例递归解析子节点列表，返回子 token 列表。用于指令内容等嵌套解析场景。

##### `unknown_visit/unknown_departure(node)`

未知节点类型的处理：输出警告，若 `raise_on_warning=True` 则抛 NotImplementedError。

#### 已实现的访问方法

- `visit_document/depart_document` - 空操作
- `visit_Element/depart_Element` - 空操作
- `visit_system_message/visit_problematic` - 跳过（SkipNode）
- `visit_section/depart_section` - 空操作（由 title 处理）
- `visit_title/depart_title` - 生成 heading_open/close，markup 为对应数量的 `#`
- `visit_paragraph/depart_paragraph` - 生成 paragraph_open/close，tight list 中标记 hidden=True

### `RenderOutput(NamedTuple)`

- `tokens: list[Token]` - 生成的 markdown-it token 列表
- `env: dict[str, Any]` - 渲染环境（引用定义等）

## 状态管理

`reset_state()` 方法初始化：
- `_tokens: list[Token]` - 输出 token 流
- `_env: dict` - 环境字典（references、duplicate_refs）
- `_inline: Optional[Token]` - 当前 inline 容器
- `parent_tokens: dict[str, int]` - 父 token 嵌套计数
- `_front_matter_tokens: list` - front matter 键值对 token 列表
- `_tight_list: bool` - 当前是否在 tight 列表内

## 源码位置

- 文件路径：`rst_to_myst/markdownit.py`

## 相关概念

- [MarkdownItRenderer 与 AST→Token 遍历](/concepts/06-token-rendering.md)
