---
type: Reference
title: Papyri IR 节点类型源码信源
description: Papyri 中间表示（IR）全部节点类型的分类、CBOR 标签、字段定义源码索引
tags: [papyri, ir, nodes, cbor, ast]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-repo
    resource: https://github.com/carreau/papyri
    title: Papyri GitHub Repository
---

## IR 节点类型分类索引

源码路径：`external/libs/jupyter/papyri/papyri/nodes.py`

所有可序列化节点通过 `@register(tag)` 装饰器分配唯一 CBOR tag（4000-4099 范围），debug 阶段节点使用 `@debug(tag)` 标记。

### 文档结构节点

| 类名 | CBOR Tag | 字段 | 说明 |
|------|----------|------|------|
| `Root` | 4001 | children: tuple[...] | 文档根节点 |
| `Section` | 4015 | children, title, level, target | 文档章节（标题+正文） |
| `TocTree` | 4021 | children, title, ref: LocalRef | 目录树节点 |

### 引用与链接节点

| 类名 | CBOR Tag | 字段 | 说明 |
|------|----------|------|------|
| `RefInfo` | 4000 | module, version, kind, path | 跨包引用信息（frozen dataclass） |
| `LocalRef` | 4022 | kind, path | 同包内本地引用（frozen dataclass） |
| `CrossRef` | 4002 | value, reference: RefInfo\|LocalRef, kind | 交叉引用（gen 生成，ingest 解析） |
| `InlineRole` | @debug 4003 | value, domain, role, inventory | 未解析的 RST 解释文本角色 |
| `Link` | 4049 | children, url, title | 内联超链接 |
| `Target` | 4061 | label, url | RST 超链接目标/内部锚点 |
| `ParamRef` | 4071 | name | 参数引用（`:param:`name```） |
| `SeeAlsoItem` | 4028 | name: CrossRef, descriptions, type | "See Also"条目 |

### 行内内容节点（Phrasing Content）

| 类名 | CBOR Tag | 字段 | 说明 |
|------|----------|------|------|
| `Text` | 4046 | value: str | 纯文本 |
| `Emphasis` | 4047 | children | 斜体（RST `*text*`） |
| `Strong` | 4048 | children | 粗体（RST `**text**`） |
| `InlineCode` | 4051 | value: str | 行内代码（RST ` ``code`` `） |
| `InlineMath` | 4057 | value: str | 行内 LaTeX 数学公式 |
| `SubstitutionRef` | @debug 4041 | value: str | 替换引用（`|XXX|`） |
| `CitationReference` | 4063 | label: str | 引用引用（`[CIT2002]_`） |
| `FootnoteReference` | 4066 | label: str | 脚注引用（`[1]_`） |
| `Image` | 4062 | url, alt | 行内图片 |

### 块级内容节点（Flow Content）

| 类名 | CBOR Tag | 字段 | 说明 |
|------|----------|------|------|
| `Paragraph` | 4045 | children | 段落 |
| `Code` | 4050 | value, execution_status, out | 代码块（可含执行结果） |
| `BulletList` | 4053 | ordered, start, children | 有序/无序列表 |
| `ListItem` | 4054 | children | 列表项 |
| `Blockquote` | 4059 | children | 块引用 |
| `Math` | 4058 | value: str | 块级 LaTeX 数学公式 |
| `ThematicBreak` | 4019 | - | 水平分割线 |
| `Admonition` | 4056 | kind, base_type, children | 提示框（note/warning/tip 等） |
| `AdmonitionTitle` | 4055 | children | 提示框标题 |
| `Figure` | 4024 | value: RefInfo | 图片 figure（跨引用图片） |
| `Table` | 4065 | children: tuple[TableRow] | 结构化表格 |
| `TableRow` | 4068 | header, children: tuple[TableCell] | 表格行 |
| `TableCell` | 4069 | children | 表格单元格 |

### 定义列表与字段列表

| 类名 | CBOR Tag | 字段 | 说明 |
|------|----------|------|------|
| `DefList` | 4033 | children: tuple[DefListItem] | 定义列表 |
| `DefListItem` | 4037 | dt, dd | 定义列表项（术语+定义） |
| `FieldList` | 4035 | children: tuple[FieldListItem] | RST 字段列表（`:param x:`） |
| `FieldListItem` | 4036 | name, body | 字段列表项 |

### NumPy 文档风格节点

| 类名 | CBOR Tag | 字段 | 说明 |
|------|----------|------|------|
| `Parameters` | 4026 | children: tuple[DocParam] | 参数列表容器 |
| `DocParam` | 4016 | name, annotation, desc | 单个参数/返回值条目 |
| `NumpydocExample` | 4012 | value: tuple[str] | NumPy Examples 节 |
| `NumpydocSeeAlso` | 4013 | value: tuple[SeeAlsoItem] | NumPy See Also 节 |
| `NumpydocSignature` | 4014 | value: str | NumPy Signature 节 |

### 引用节点（Bibliography）

| 类名 | CBOR Tag | 字段 | 说明 |
|------|----------|------|------|
| `Citation` | 4064 | label, children | 块级引用定义 |
| `Footnote` | 4067 | label, children | 块级脚注定义 |

### 特殊节点

| 类名 | CBOR Tag | 说明 |
|------|----------|------|
| `Directive` | Unserializable | 未处理指令（遇到即报错，阻止序列化） |
| `UnprocessedDirective` | Unserializable | 已解析但未分发的指令（中间态） |
| `Unimplemented` | @debug 4018 | gen 尚未处理的块级 RST 构造 |
| `UnimplementedInline` | @debug 4017 | gen 尚未处理的行内 RST 构造 |
| `SubstitutionDef` | @debug 4027 | 替换定义 |
| `Comment` | 无@register（CBOR中丢弃） | RST 注释 |
| `Options` | @debug 4034 | 指令选项块 |
| `GenCode`/`GenToken` | Unserializable | gen 时内存中间态（语法高亮+执行输出） |
| `Leaf` | - | 单值节点基类（value: str） |
| `IntermediateNode` | - | 不应进入最终产物的虚拟中间节点 |

### 类型别名

| 别名 | 包含类型 |
|------|---------|
| `StaticPhrasingContent` | Text \| InlineCode \| InlineMath \| InlineRole \| CrossRef \| ParamRef \| CitationReference \| FootnoteReference \| SubstitutionRef \| Unimplemented |
| `PhrasingContent` | StaticPhrasingContent \| Emphasis \| Strong \| Link |
| `FlowContent` | Code \| Paragraph \| UnprocessedDirective \| ThematicBreak \| Blockquote \| BulletList \| Target \| Directive \| Admonition \| Math \| DefList \| ... |
| `SectionContent` | FlowContent + Parameters + SubstitutionDef + ... |

### Encoder 全局实例

- `encoder = Encoder(REV_TAG_MAP)`：模块级 CBOR 编码器/解码器单例
- `canonical=True`：CBOR map key 排序，确保确定性编码
