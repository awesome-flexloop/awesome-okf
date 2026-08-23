---
type: Concept
title: 警告系统
description: MystWarnings 枚举、create_warning 统一警告创建、警告抑制机制
tags: [myst, sphinx, warning, error, mystwarnings, suppress-warnings, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 警告系统

MyST-Parser 实现了统一的警告系统，通过 `MystWarnings` 枚举分类所有警告类型，`create_warning()` 函数同时支持 Sphinx 和 docutils 两种环境的警告输出。

## MystWarnings 枚举

`MystWarnings` 枚举定义了 23 种警告类型：

### 配置与解析警告

| 枚举值 | 值字符串 | 说明 |
|--------|---------|------|
| `DEPRECATED` | "deprecated" | 使用了已弃用的功能 |
| `NOT_SUPPORTED` | "not_supported" | docutils 暂不支持的功能 |
| `RENDER_METHOD` | "render" | render 方法未实现 |

### Markdown 解析警告

| 枚举值 | 值字符串 | 说明 |
|--------|---------|------|
| `MD_TOPMATTER` | "topmatter" | frontmatter 解析问题 |
| `MD_DEF_DUPE` | "duplicate_def" | 重复的 Markdown 引用定义 |
| `MD_HEADING_NON_CONSECUTIVE` | "header" | 非连续的标题级别 |

### 指令/角色警告

| 枚举值 | 值字符串 | 说明 |
|--------|---------|------|
| `DIRECTIVE_PARSING` | "directive_parse" | 指令解析错误 |
| `DIRECTIVE_OPTION` | "directive_option" | 指令选项解析错误 |
| `DIRECTIVE_OPTION_COMMENTS` | "directive_comments" | 指令选项中的 # 注释 |
| `DIRECTIVE_BODY` | "directive_body" | 指令内容解析错误 |
| `UNKNOWN_DIRECTIVE` | "directive_unknown" | 未知指令 |
| `UNKNOWN_ROLE` | "role_unknown" | 未知角色 |

### 交叉引用警告

| 枚举值 | 值字符串 | 说明 |
|--------|---------|------|
| `XREF_AMBIGUOUS` | "xref_ambiguous" | 找到多个引用目标 |
| `XREF_MISSING` | "xref_missing" | 未找到引用目标 |
| `INV_LOAD` | "inv_retrieval" | inventory 加载失败 |
| `IREF_MISSING` | "iref_missing" | intersphinx 未找到目标 |
| `IREF_AMBIGUOUS` | "iref_ambiguous" | intersphinx 找到多个目标 |
| `LEGACY_DOMAIN` | "domains" | 旧版 domain 未实现 resolve_any_xref |

### 扩展警告

| 枚举值 | 值字符串 | 说明 |
|--------|---------|------|
| `LINKIFY` | "linkify" | linkify 扩展依赖缺失 |
| `HEADING_SLUG` | "heading_slug" | 标题 slug 计算错误 |
| `STRIKETHROUGH` | "strikethrough" | 删除线仅在 HTML 中实现 |
| `HTML_PARSE` | "html" | HTML 解析/转换错误 |
| `INVALID_ATTRIBUTE` | "attribute" | 无效的属性值 |
| `SUBSTITUTION` | "substitution" | 替换无法解析 |

## create_warning() 函数

`create_warning()` 是统一的警告创建函数，自动处理 Sphinx 和 docutils 两种环境：

```python
def create_warning(
    document, message, subtype,
    *, wtype=None, node=None, line=None, append_to=None
):
```

### Sphinx 环境行为

1. 通过 `sphinx.util.logging.getLogger()` 记录 warning 级日志
2. 日志携带 `type="myst"` 和 `subtype=<warning_value>`
3. 检查 `suppress_warnings` 配置决定是否抑制
4. 创建 `nodes.system_message` 节点插入文档 AST

### Docutils 环境行为

1. 通过 `document.reporter.warning()` 报告警告
2. 检查 `document.settings.myst_suppress_warnings` 决定是否抑制
3. 创建 system_message 节点

### 警告消息格式

警告消息格式为：`{message} [myst.{subtype}]`

例如：
```
Unknown source document 'missing.md' [myst.xref_missing]
The `linkify` extension is enabled, but the `linkify-it-py` package is not installed [myst.linkify]
```

## 警告抑制

### Sphinx 环境

通过 `suppress_warnings` 配置抑制警告：

```python
# 抑制所有 myst 警告
suppress_warnings = ["myst"]

# 抑制特定类型
suppress_warnings = ["myst.xref_missing", "myst.directive_unknown"]

# 使用通配符（需 Sphinx 支持）
suppress_warnings = ["myst.xref_*"]
```

### nitpick 模式下的引用警告

在 `nitpicky = True` 模式下，未解析的引用会报错。可以通过 `nitpick_ignore` 抑制：

```python
nitpicky = True
nitpick_ignore = [
    ("myst", "some-target"),  # 忽略特定未解析目标
]
nitpick_ignore_regex = [
    ("myst", r"temp-.*"),      # 正则匹配忽略
]
```

### Docutils CLI 环境

```bash
myst-docutils-html5 --myst-suppress-warnings=myst.xref_missing input.md
```

## 相关概念

- [配置系统](/concepts/04-config-system.md)
- [解析器与渲染器](/concepts/06-parser-and-renderer.md)
- [交叉引用](/concepts/08-cross-references.md)
- [CLI 工具](/concepts/10-cli-tools.md)
