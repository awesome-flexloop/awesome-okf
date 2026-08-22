---
type: Concept
title: Front Matter 提取与 YAML 输出
description: rst-to-myst 如何将 RST 文档开头的 field list 转换为 YAML front matter。
tags: [front-matter, yaml, field-list, metadata, document-header]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-parser
    resource: /references/source-parser.md
    title: rst-to-myst RST 解析器模块
  - id: src-mdformat-render
    resource: /references/source-mdformat-render.md
    title: rst-to-myst mdformat 渲染集成
---

## 什么是 Front Matter

Front matter 是文档开头的元数据区块，在 MyST/Markdown 中通常使用 YAML 格式，以 `---` 分隔符包裹：

```markdown
---
title: 文档标题
author: 作者名
---

正文内容...
```

在 RST 中，类似的元数据通常通过 field list（字段列表）表示，放在文档最开头：

```rst
:title: 文档标题
:author: 作者名

正文内容...
```

rst-to-myst 实现了从 RST field list 到 YAML front matter 的自动转换。

## FrontMatter Transform

`FrontMatter` 是一个 docutils Transform，负责在 AST 层面将开头的 field_list 识别并替换为自定义的 `FrontMatterNode`。

### 执行条件

Transform 首先检查 `document.settings.front_matter` 是否为 True，为 False 时直接返回（不提取 front matter）。这个设置默认为 True，可通过 `to_docutils_ast(front_matter=False)` 禁用。

### 查找逻辑

1. 跳过 `PreBibliographic` 节点（如注释、bibliographic 元素之前的节点）
2. 找到第一个非前置节点 `candidate`
3. 如果 candidate 是 section（章节），在 section 内部继续查找第一个非前置子节点
4. 如果找到的节点是 `nodes.field_list` 类型，创建 `FrontMatterNode` 替换原 field_list

FrontMatterNode 将 field_list 的所有子节点（field 节点）作为自己的子节点。

### 为什么跳过 PreBibliographic

docutils 中 `PreBibliographic` 类节点包括文档标题（title）、副标题（subtitle）、docinfo 等。FrontMatter Transform 只处理 field_list，不应影响文档标题等结构。section 内的处理允许 field_list 出现在章节标题之后（这是 RST 中常见的写法）。

## Token 生成阶段

在 `MarkdownItRenderer.to_tokens()` 方法中，front matter 的处理是特殊的：它不在 walkabout 过程中直接输出 token，而是在遍历完成后构建专用的 token 序列。

收集到的 front matter 数据存储在 `_front_matter_tokens` 列表中，每项是 `(key_path, tokens)` 元组。token 结构为：

```
front_matter_tokens_open (nesting=1)
  front_matter_key_open (nesting=1, meta={key_path: [...]})
    ...子内容 tokens...
  front_matter_key_close (nesting=-1)
  front_matter_key_open (nesting=1, meta={key_path: [...]})
    ...子内容 tokens...
  front_matter_key_close (nesting=-1)
front_matter_tokens_close (nesting=-1)
```

`key_path` 是一个列表，跟踪嵌套的键路径。例如：
- 顶级键 `title` → `key_path = ["title"]`
- 嵌套键 `substitutions.key` → `key_path = ["substitutions", "key"]`

front matter tokens 被前置到主 token 流的开头，确保在渲染时出现在文档最前面。

## 渲染阶段

`_front_matter_tokens_renderer` 是 mdformat 自定义渲染器，负责将 front_matter_tokens 渲染为 YAML：

1. 遍历子节点，对每个 `front_matter_key_open/close` 对：
   - 从 `meta["key_path"]` 获取键路径
   - 如果有子节点，递归渲染子内容
   - 如果没有子节点，值设为 `True`（YAML 布尔值）
2. 根据 key_path 构建嵌套字典结构
3. 使用 `yaml_dump()` 序列化为 YAML 文本
4. 包裹在 `---\n...\n---` 之间

### 嵌套字典构建

```python
dct = {}
for child in node.children:
    path = child.meta["key_path"]
    value = (
        "\n\n".join(subchild.render(context) for subchild in child.children)
        if child.children
        else True
    )
    subdct = dct
    for key in path[:-1]:
        subdct.setdefault(key, {})
        subdct = subdct[key]
    subdct[path[-1]] = value
```

对于多层嵌套的 key_path（如 `["a", "b", "c"]`），代码逐级深入字典，在最深层设置值。

## YAML 序列化

使用 rst-to-myst 自定义的 `yaml_dump()` 函数（定义在 `utils.py`）：

```python
class YamlDumper(yaml.SafeDumper):
    pass

def represent_str(dumper, data):
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)

YamlDumper.add_representer(str, represent_str)
```

特点：
- 多行字符串自动使用 `|` 块标量样式（保留换行）
- 默认 `sort_keys=True`，按键名字母序排列
- 基于 SafeDumper，安全加载/转储

## 替换（Substitution）识别

front matter 中的 `substitutions` 键有特殊处理：`get_myst_extensions()` 在扫描 tokens 时，如果发现 front_matter_key_open 的 key_path 以 "substitutions" 开头，会标记需要 `substitution` MyST 扩展。这是因为 substitutions 定义通常放在 front matter 中：

```markdown
---
substitutions:
  key: value
---
```

## 禁用 Front Matter

如果不希望 RST field list 被转换为 YAML front matter：

**CLI**：目前 CLI 没有暴露此选项（默认启用）。

**Python API**：
```python
from rst_to_myst import to_docutils_ast

document, ws = to_docutils_ast(text, front_matter=False)
```

## 相关概念

- [mdformat 渲染集成与自定义渲染器](/concepts/07-mdformat-integration.md)
- [LosslessRSTParser 与自定义 Transform](/concepts/04-lossless-parser.md)
