---
type: Example
title: 启用与配置扩展语法
description: 常用扩展组合的配置示例——学术文档、API文档、项目文档等场景
tags: [myst, sphinx, extensions, configuration, dollarmath, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
  - id: extensions-cheatsheet
    resource: /references/extensions-cheatsheet.md
    title: MyST 扩展语法速查
---

## 启用与配置扩展语法

本示例展示不同文档场景下的扩展配置组合。

## 场景 1：学术/技术文档

包含数学公式、定义、定理等学术写作需求：

```python
# conf.py
extensions = ["myst_parser"]

myst_enable_extensions = [
    "dollarmath",       # 行内/块级数学公式
    "amsmath",          # AMS 数学环境（align/gather）
    "colon_fence",      # ::: 围栏（嵌套指令）
    "deflist",          # 定义列表
    "fieldlist",        # 字段列表
    "html_image",       # HTML img
    "smartquotes",      # 智能引号
    "replacements",     # 文本替换符号
    "substitution",     # 变量替换
    "attrs_inline",     # 行内属性
]

myst_heading_anchors = 4
myst_dmath_allow_labels = True
myst_update_mathjax = True

# 数学宏定义（在 frontmatter 中使用）
myst_substitutions = {
    "R": "\\mathbb{R}",
    "E": "\\mathbb{E}",
}
```

文档示例：

```markdown
---
myst:
  substitutions:
    R: "\\mathbb{R}"
---

# 概率论基础

## 期望定义

期望（Expectation）：对于随机变量 $X$，其期望定义为

$$
\mathbb{{E}}[X] = \int_{{-\infty}}^{{\infty}} x f(x) dx
$$ (expectation)

其中 $f(x)$ 是概率密度函数。

## 常用符号

期望算子
: 将随机变量映射到其加权平均值

概率测度
: 定义在可测空间上的满足 Kolmogorov 公理的集函数

:::{important}
公式 {{eq:expectation}} 是概率论的核心定义，必须熟记。
:::
```

## 场景 2：API/软件文档

包含代码块、任务列表、链接等：

```python
# conf.py
myst_enable_extensions = [
    "colon_fence",
    "tasklist",
    "linkify",
    "smartquotes",
    "replacements",
    "substitution",
    "attrs_inline",
    "strikethrough",
    "html_image",
]

myst_heading_anchors = 3
myst_enable_checkboxes = True  # 交互式复选框
myst_linkify_fuzzy_links = True
myst_number_code_blocks = ["python", "bash"]
```

文档示例：

```markdown
# API v2 迁移指南

## 变更清单

- [x] 废弃旧的 `api/v1/` 端点
- [x] 更新认证方式为 Bearer Token
- [ ] 添加速率限制
- [ ] ~~移除 XML 响应格式~~（延迟到 v3）

## 新认证方式

```python
import requests

response = requests.get(
    "https://api.example.com/v2/users",
    headers={"Authorization": "Bearer <token>"}
)
```

访问 https://api.example.com/docs 查看完整 API 文档。
```

## 场景 3：通用项目 README/博客

简洁配置，常见需求：

```python
# conf.py
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "smartquotes",
    "replacements",
    "linkify",
]

myst_heading_anchors = 2
myst_heading_slug_func = "github"
```

## 场景 4：最小 CommonMark

只需要标准 Markdown，无扩展：

```python
# conf.py
myst_commonmark_only = True
myst_heading_anchors = 0
```

此时不支持指令、角色、数学公式等 MyST 特性，仅解析标准 CommonMark。

## 禁用特定语法

即使启用了扩展，也可以通过 `myst_disable_syntax` 禁用特定 CommonMark 语法：

```python
# 禁用强调（*text* 和 **text**）
myst_disable_syntax = ["emphasis"]
```

## 相关概念

- [扩展语法系统](../concepts/05-extension-system.md)
- [配置系统](../concepts/04-config-system.md)
- [数学公式与 MathJax](../concepts/13-math-and-mathjax.md)
- [MyST 扩展语法速查](../references/extensions-cheatsheet.md)
