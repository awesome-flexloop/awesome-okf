---
type: Concept
title: YAML Frontmatter
description: Markdown 文件开头的 YAML 元数据、文件级配置覆盖、html_meta 和 substitutions 合并
tags: [myst, sphinx, yaml, frontmatter, metadata, topmatter, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## YAML Frontmatter

每个 MyST Markdown 文件可以在开头包含 YAML frontmatter（前 matter），用于定义文件级元数据和覆盖全局配置。frontmatter 由 `---` 分隔符包围。

## 基本语法

```markdown
---
key1: value1
key2: value2
---

# 文档标题

正文内容...
```

Frontmatter 以 `---` 开头和结尾（或 `...` 结尾）：

```markdown
---
title: 我的文档
...
```

## MyST 文件级配置

在 frontmatter 的 `myst` 键下可以覆盖全局 `myst_*` 配置：

```markdown
---
myst:
  enable_extensions: ["dollarmath", "tasklist"]
  substitutions:
    version: "1.0"
    project: "My Project"
  html_meta:
    "description lang=en": "My document description"
---
```

### 可在文件级覆盖的配置

所有 MdParserConfig 字段除了标记 `global_only=True` 的都可以覆盖：

- `enable_extensions`：启用的扩展
- `substitutions`：替换变量
- `html_meta`：HTML meta 标签
- `heading_anchors`：标题锚点深度
- `footnote_sort`：脚注排序
- `dmath_*`：数学公式配置
- `linkify_fuzzy_links`：linkify 模糊匹配
- 等等

### 不可在文件级覆盖的配置（global_only=True）

- `heading_slug_func`：标题 slug 函数
- `update_mathjax`：MathJax 配置更新
- `mathjax_classes`：MathJax CSS 类
- `suppress_warnings`：警告抑制列表
- `inventories`：intersphinx inventory 映射

## 合并策略

`merge_file_level()` 函数处理全局配置和文件级配置的合并：

### 普通字段

文件级值直接覆盖全局值：

```python
# 全局
myst_heading_anchors = 2

# 文件级
myst:
  heading_anchors: 4
# 结果：heading_anchors = 4
```

### merge_topmatter 字段

标记了 `merge_topmatter=True` 的字段执行字典合并（`{**global, **file}`）：

- `html_meta`：HTML meta 标签合并
- `substitutions`：替换变量合并

```python
# 全局
myst_substitutions = {"name": "Project", "version": "1.0"}

# 文件级
myst:
  substitutions:
    version: "2.0"
    author: "张三"
# 结果：substitutions = {"name": "Project", "version": "2.0", "author": "张三"}
```

### 废弃的顶层键

`html_meta` 和 `substitutions` 曾支持在 frontmatter 顶层使用（不在 `myst` 键下），现在会发出 `MD_TOPMATTER` 弃用警告：

```markdown
---
# 已弃用，会发出警告
html_meta:
  description: "..."
substitutions:
  key: value
---
```

应改为：

```markdown
---
myst:
  html_meta:
    description: "..."
  substitutions:
    key: value
---
```

## title_to_header

启用 `myst_title_to_header = True` 时，frontmatter 的 `title` 字段会自动转换为 H1 标题：

```markdown
---
title: 自动生成的标题
myst:
  title_to_header: true
---

（这里不需要写 # 标题，title 字段会自动成为 H1）

正文从这里开始。
```

## HTML Meta 标签

`html_meta` 配置生成 HTML `<meta>` 标签：

```markdown
---
myst:
  html_meta:
    "description lang=en": "Page description"
    "keywords": "myst, sphinx, markdown"
    "og:title": "Open Graph Title"
---
```

渲染为：

```html
<meta content="Page description" lang="en" name="description" />
<meta content="myst, sphinx, markdown" name="keywords" />
<meta content="Open Graph Title" property="og:title" />
```

键名中的 `lang=xx` 会设置 `lang` 属性；键名含 `:` 时使用 `property` 而非 `name` 属性（Open Graph 协议）。

## 字段验证

文件级配置值通过与全局配置相同的验证器验证（`validate_field()`）。验证失败时发出 `MD_TOPMATTER` 警告，但不中断解析：

```markdown
---
myst:
  heading_anchors: 99  # 无效值（有效范围 0-7），发出警告但继续
---
```

## 读取实现

`read_topmatter(text)` 函数负责解析：

1. 检查第一行是否以 `---` 开头
2. 逐行读取直到遇到 `---` 或 `...`
3. 使用 `yaml.safe_load()` 解析 YAML
4. 验证结果为字典类型

解析失败时抛出 `TopmatterReadError`，在 `parse()` 方法中被捕获，错误会在渲染阶段报告。

## 与 Sphinx 元数据的关系

Frontmatter 中的非 `myst` 键会被 Sphinx 作为文档元数据处理，可在模板中通过 `meta` 变量访问：

```markdown
---
title: 文档标题
author: 作者名
myst:
  enable_extensions: ["dollarmath"]
---
```

## 相关概念

- [配置系统](04-config-system.md)
- [解析器与渲染器](06-parser-and-renderer.md)
- [Sphinx 集成机制](11-sphinx-integration.md)
- [基础配置示例](../examples/01-basic-setup.md)
