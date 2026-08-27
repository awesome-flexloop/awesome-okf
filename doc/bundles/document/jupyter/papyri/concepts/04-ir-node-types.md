---
type: Concept
title: IR 节点类型体系
description: Papyri IR 的节点类型分类体系、Node 基类、序列化机制、@register/@debug 装饰器
tags: [papyri, ir, nodes, cbor, ast, serialization]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: nodes-src
    resource: /references/ir-nodes-source.md
    title: Papyri IR 节点类型源码信源
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
---

## Node 基类

所有 IR 节点都继承自 `node_base.py` 中的 `Node` 类。Node 提供了：

- **基于类型注解的自动初始化**：`__init__` 通过 `get_type_hints()` 反射获取字段，按位置参数或关键字参数赋值
- **类型强制转换**：`_coerce_field()` 将 list 自动转为 tuple（cbor2 ≥ 6 解码为 tuple）
- **CBOR 序列化**：`cbor(encoder)` 方法将节点编码为带 tag 的 CBOR 数组
- **JSON 序列化**：`to_json()` / `from_json()` 通过 `node_serializer` 进行递归序列化
- **字典转换**：`to_dict()` / `from_dict()` 用于 JSON 中间格式
- **校验**：`validate()` 递归检查字段类型，类型不匹配抛出 `WrongTypeAtField`
- **等式比较**：基于类型注解中所有字段的值比较

```python
class Node(Base):
    def __init__(self, *args, **kwargs):
        tt = get_type_hints(type(self))
        for attr, val in zip(tt, args, strict=False):
            setattr(self, attr, _coerce_field(tt[attr], val))
        for k, v in kwargs.items():
            assert k in tt
            setattr(self, k, _coerce_field(tt[k], v))
```

## 注册机制：@register 和 @debug

每个可序列化的节点类型必须通过装饰器分配唯一的 CBOR tag：

- `@register(tag)`——标记稳定的生产节点，分配 tag 并加入 `TAG_MAP`/`REV_TAG_MAP`
- `@debug(tag)`——标记 schema 变动中的节点，除了注册外还加入 `DEBUG_TYPES`/`DEBUG_TAG_SET`，查看器应视觉区分这些节点

tag 范围在 4000-4099 之间。`tuple` 类型也被注册为 tag 4444。

### TAG_MAP 和 REV_TAG_MAP

- `TAG_MAP: dict[type, int]`：类型 → CBOR tag 的映射（编码时使用）
- `REV_TAG_MAP: dict[int, type]`：CBOR tag → 类型的映射（解码时使用）

## UnserializableNode：不可序列化节点

某些节点是纯内存中间态，不应该跨越 gen→磁盘边界。继承 `UnserializableNode` 的类：

- `cbor()` 抛出 `NotImplementedError`
- `to_json()` 抛出 `NotImplementedError`
- 子类可通过 `_dont_serialise = True` 标记，递归序列化时被拦截
- `_why_unserializable()` 方法提供具体的错误原因

关键的不可序列化节点：

| 类名 | 作用 |
|------|------|
| `Directive` | 未注册处理器的 RST 指令——**序列化时强制报错**（`_reject_at_validate = True`） |
| `UnprocessedDirective` | 已解析但未分发的指令（验证时允许，后续 visitor 会替换） |
| `GenCode`/`GenToken` | gen 时语法高亮+执行输出的中间态 |
| `IntermediateNode` | 不应进入最终产物的虚拟节点 |

### Directive 的强制拦截机制

`Directive` 节点是特殊的——它表示 gen 遇到了一个没有注册处理器的 RST 指令。它的 `_reject_at_validate = True` 使得 `validate()` 在构建过程中就抛出错误（而非等到写入/打包阶段才发现）。错误信息会提示开发者在 TOML 配置的 `[global.directives]` 中注册处理器。

## Encoder：全局 CBOR 编解码器

`nodes.py` 中提供了模块级的 `encoder` 单例：

```python
encoder = Encoder(REV_TAG_MAP)
```

编码特性：
- **canonical=True**：CBOR map key 按 RFC 8949 §4.2 排序，确保确定性输出
- **节点编码为数组**：字段按类定义顺序排列为 CBOR 数组（非 map），更紧凑
- **cbor2 6.x 兼容**：正确处理 immutable 模式下的 tuple/frozendict
- **Comment 节点在 CBOR 中丢弃**：`Node.cbor()` 过滤 `_drop_in_cbor = True` 的子节点

## 节点类型层次

IR 节点按内容模型分为几个层次：

### 文档结构层

| 节点 | tag | 作用 |
|------|-----|------|
| `Root` | 4001 | 文档根节点 |
| `Section` | 4015 | 文档章节（标题+正文），支持嵌套 |
| `TocTree` | 4021 | 目录树节点 |

### 引用层

| 节点 | tag | 作用 |
|------|-----|------|
| `RefInfo` | 4000 | 跨包引用（module, version, kind, path） |
| `LocalRef` | 4022 | 同包引用（kind, path） |
| `CrossRef` | 4002 | 交叉引用（gen 生成，ingest 解析） |
| `InlineRole` | @debug 4003 | 未解析的 RST 角色（待转换为 CrossRef） |
| `ParamRef` | 4071 | 参数引用（`:param:`name```） |
| `SeeAlsoItem` | 4028 | "See Also"条目 |

### 行内内容层（PhrasingContent）

| 节点 | tag | 作用 |
|------|-----|------|
| `Text` | 4046 | 纯文本 |
| `Emphasis` | 4047 | 斜体 |
| `Strong` | 4048 | 粗体 |
| `InlineCode` | 4051 | 行内代码 |
| `InlineMath` | 4057 | 行内数学公式 |
| `Link` | 4049 | 超链接 |
| `Image` | 4062 | 图片 |
| `SubstitutionRef` | @debug 4041 | 替换引用 |

### 块级内容层（FlowContent）

| 节点 | tag | 作用 |
|------|-----|------|
| `Paragraph` | 4045 | 段落 |
| `Code` | 4050 | 代码块（可含执行结果） |
| `BulletList` | 4053 | 有序/无序列表 |
| `ListItem` | 4054 | 列表项 |
| `Blockquote` | 4059 | 块引用 |
| `Math` | 4058 | 块级数学公式 |
| `Admonition` | 4056 | 提示框（note/warning/tip/danger 等） |
| `Table`/`TableRow`/`TableCell` | 4065/4068/4069 | 结构化表格 |
| `ThematicBreak` | 4019 | 水平分割线 |

### 定义列表与字段列表

| 节点 | tag | 作用 |
|------|-----|------|
| `DefList`/`DefListItem` | 4033/4037 | 定义列表（术语+定义） |
| `FieldList`/`FieldListItem` | 4035/4036 | RST 字段列表 |

### NumPy 文档风格

| 节点 | tag | 作用 |
|------|-----|------|
| `Parameters` | 4026 | 参数列表容器 |
| `DocParam` | 4016 | 单个参数/返回值条目 |
| `NumpydocExample` | 4012 | Examples 节原始行 |
| `NumpydocSeeAlso` | 4013 | See Also 节 |
| `NumpydocSignature` | 4014 | Signature 节原始字符串 |

### Admonition 分类系统

Admonition 使用有限的样式类别集合（`ADMONITION_BASE_TYPES`）：

```python
ADMONITION_BASE_TYPES = frozenset({"note", "tip", "important", "warning", "danger", "neutral"})
```

`kind` 到 `base_type` 的映射通过 `_ADMONITION_KIND_TO_BASE_TYPE` 字典和 `admonition_base_type()` 函数完成。未知 kind 回退到 "note"。version 相关的 kind（versionadded/versionchanged/deprecated）映射到 "neutral"。

## Code 节点的执行状态

`Code` 块包含 `execution_status` 字段：
- `None`：块未执行
- `"ok"`：执行成功
- `"error"`：执行出错
- 其他状态字符串

`out` 字段保存捕获的 stdout/stderr 输出。

## 类型别名

`nodes.py` 定义了联合类型别名用于类型标注：

```python
StaticPhrasingContent = Text | InlineCode | InlineMath | InlineRole | CrossRef | ...
PhrasingContent = StaticPhrasingContent | Emphasis | Strong | Link
FlowContent = Code | Paragraph | ... | Directive | Admonition | ...
SectionContent = FlowContent | Parameters | SubstitutionDef | ...
```

## 相关概念

- [IR 与 DocBundle](03-ir-and-docbundle.md)
- [gen 管线](05-gen-pipeline.md)
- [RST 解析](10-rst-parsing.md)
- [IR 节点类型信源](../references/ir-nodes-source.md)
