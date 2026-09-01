---
type: Example
title: 交叉引用实战
description: MyST Markdown 中各种交叉引用方式——文档间引用、锚点引用、标签引用、intersphinx
tags: [myst, sphinx, cross-reference, intersphinx, toctree, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 交叉引用实战

本示例展示 MyST Markdown 中各种交叉引用的写法。

## conf.py 配置

```python
# conf.py
extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
]

myst_enable_extensions = [
    "colon_fence",
    "html_image",
]

myst_heading_anchors = 3
myst_heading_slug_func = "github"

# intersphinx 配置
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# nitpick 模式（未解析引用会报错）
nitpicky = True
nitpick_ignore = [
    ("myst", "ignored-reference"),
]
```

## 项目结构

```
docs/
├── conf.py
├── index.md
├── guide/
│   ├── getting-started.md
│   └── advanced.md
└── api/
    └── reference.md
```

## 文档间引用

### 引用其他 Markdown 文件

```markdown
参见 [快速开始](guide/getting-started.md) 了解安装步骤。

阅读 [高级指南](./guide/advanced.md) 获取更多信息。

查看 [API 参考](../api/reference.md)。
```

### 引用带锚点的文档

```markdown
参见 [安装章节](guide/getting-started.md#安装)。

参考 [配置部分](./guide/advanced.md#配置选项)。
```

## 文档内锚点引用

### 自动标题锚点

启用 `myst_heading_anchors = 3` 后，标题自动生成 GitHub 风格的 slug：

```markdown
## 安装方法

详细内容...

参见 [安装方法](#安装方法) 了解详情。
```

### 显式标签

使用 `(label)=` 语法定义可引用的标签：

```markdown
(my-install-section)=
## 安装

安装说明...

(my-config-section)=
### 配置选项

配置说明...
```

然后在任意位置引用：

```markdown
详细步骤见 [安装章节](#my-install-section)。

也可以在其他文档中引用：[配置](guide/advanced.md#my-config-section)。
```

### 使用 ref 角色

对于显式标签，也可以使用 `{ref}` 角色：

```markdown
请参阅 {ref}`my-install-section`。

自定义链接文本：{ref}`点击这里查看安装<my-install-section>`。
```

## Markdown 链接中的隐式引用

不带 `.md` 扩展名的链接会尝试通过 Sphinx 域系统解析：

```markdown
`dict`                    → 解析为 Python dict 文档（intersphinx）
[Sphinx 应用](sphinx.application.Sphinx) → 解析为 Sphinx API 文档
`my-install-section`      → 解析为本地标签
```

## URL Scheme 自定义

```python
# conf.py
myst_url_schemes = {
    "http": None,
    "https": None,
    "mailto": None,
    "jira": {
        "url": "https://jira.example.com/browse/{path}",
        "title": "JIRA: {path}",
    },
}
```

使用自定义 scheme：

```markdown
相关 JIRA 任务：<jira:PROJ-123>

或使用链接语法：[PROJ-123](jira:PROJ-123)
```

## toctree 指令

使用 colon_fence 语法书写 toctree：

```markdown
# 文档目录

:::{toctree}
:maxdepth: 2
:caption: 用户指南
:hidden:

guide/getting-started
guide/advanced
:::

:::{toctree}
:maxdepth: 1
:caption: API 参考

api/reference
:::
```

## 下载链接

```markdown
下载 {download}`示例文件 <../examples/sample.py>`。
```

## 相关概念

- [交叉引用](../concepts/08-cross-references.md)
- [MyST 语法概览](../concepts/02-myst-syntax-overview.md)
- [指令与角色](../concepts/07-directives-and-roles.md)
