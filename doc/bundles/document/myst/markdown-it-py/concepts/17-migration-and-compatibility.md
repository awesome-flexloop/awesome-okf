---
type: Concept
title: JS 兼容与 Python 扩展
description: markdown-it-py 与 JavaScript markdown-it 的兼容性差异，以及 Python 端特有的扩展特性
tags:
- markdown-it-py
- javascript
- compatibility
- migration
- python
difficulty: 高级
estimated_time: 10分钟
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# JS 兼容与 Python 扩展

markdown-it-py 是 JavaScript markdown-it 的逐行移植，但存在一些差异和 Python 特有的扩展。

## API 兼容性

大部分 API 与 JS 版一致：
- `MarkdownIt(config)` 构造函数
- `parse()`, `render()`, `parseInline()`, `renderInline()`
- `use()`, `enable()`, `disable()`, `set()`, `configure()`
- `add_render_rule()`
- Token 结构和字段

核心架构（三链Ruler、双阶段解析、Token流）完全一致。

## 关键差异

### 1. attrs 格式

| 方面 | JS markdown-it | Python markdown-it-py |
|------|---------------|----------------------|
| 存储格式 | `[["key", "value"], ...]` | `{"key": "value"}` dict |
| 顺序 | 保留插入顺序 | dict 插入顺序保留（Python 3.7+） |
| attrGet | 遍历查找 | dict 直接查找 O(1) |
| as_dict() | - | `as_upstream=True` 时转为JS格式 |

```python
# Python: dict 格式
token.attrs  # {"href": "https://example.com", "class": "link"}

# 需要与JS兼容时
token.as_dict(as_upstream=True)  # attrs变为 [["href", "..."], ["class", "..."]]
```

### 2. 插件签名

JS 插件通常直接修改 md 实例或注册规则。Python 插件使用函数而非类/模块：

```python
# JS: markdown-it.use(require('markdown-it-plugin'), options)
# Python:
def my_plugin(md, options):
    ...
md.use(my_plugin, options)
```

### 3. 类继承

JS 使用原型链，Python 使用类继承。自定义 Renderer 时继承 `RendererHTML`。

## Python 特有扩展

### 1. SyntaxTreeNode

JS 上游没有树结构API，Python 端额外提供 `SyntaxTreeNode` 类，将 Token 流转换为可遍历的树。详见 [SyntaxTreeNode](11-syntax-tree-node.md)。

### 2. store_labels 选项

`store_labels=True` 时，链接/图片的 label 文本存储在 `token.meta["label"]` 中，方便插件访问原始标签。

### 3. tree_depth_first 迭代器

SyntaxTreeNode 提供 `walk_depth_first()` 和 `walk()` 方法用于深度优先遍历。

### 4. 类型注解

Python 版本使用 TypedDict（OptionsType、PresetType）和 dataclass（Token、Rule、Delimiter）提供完整类型信息。

### 5. CLI 工具

Python 版提供 `markdown-it` 命令行工具，支持文件/STDIN/交互模式。

### 6. 更严格的代码检查

pyproject.toml 配置了 Ruff（lint+format）和 Mypy（类型检查），代码质量更严格。

## 从 JS markdown-it 迁移

1. **Token.attrs 适配**：将 `token.attrs` 的数组操作改为 dict 操作
   - JS: `token.attrSet('class', 'x')` → `token.attrs.push(['class', 'x'])`
   - Python: `token.attrSet('class', 'x')` → `token.attrs['class'] = 'x'`
2. **插件导入**：JS 的 `require('plugin')` 改为 Python 的 import + 函数
3. **Renderer 继承**：JS 覆盖 `md.renderer.rules[name]` 改为 `md.add_render_rule(name, fn)`
4. **Preset 名称**：注意 `"default"` 键在 Python 中映射到 gfm-like 预设，使用 `"js-default"` 获取全规则预设

## 与 CommonMark 的关系

markdown-it-py（commonmark 预设）通过 CommonMark 0.30 规范测试套件。与规范的差异主要是插件扩展（table、strikethrough等）和排版选项（typographer、quotes）。
