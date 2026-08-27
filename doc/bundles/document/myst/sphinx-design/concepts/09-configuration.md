---
type: Concept
title: 配置与自定义指令
description: sphinx-design 的所有配置项详解、自定义指令继承机制、conf.py 配置示例
tags:
- sphinx
- design
- configuration
- custom-directive
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/config.py
- sphinx_design/shared.py
---

# 配置与自定义指令

## 配置项总览

所有配置项在 `conf.py` 中设置，使用 `sd_` 前缀：

| 配置名 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sd_custom_directives` | dict | `{}` | 自定义指令继承映射 |
| `sd_fontawesome_source` | str | `"none"` | FA CSS加载方式 |
| `sd_fontawesome_cdn_url` | str | cdnjs FA 6.1.1 URL | FA CDN地址 |
| `sd_fontawesome_version` | str | `"as-named"` | FA类名方案 |
| `sd_fontawesome_latex` | bool/str | `False` | LaTeX FA渲染模式 |
| `sd_tabs_storage_prefix` | str | `"sphinx-design-tab-id-"` | Tab持久化前缀 |

配置验证策略：
- 无效值不会中断构建，而是发出警告后回退到默认值
- 映射类型（如 `sd_custom_directives`）中单个无效条目被丢弃，不影响其他条目
- 所有值通过 `SdConfig` dataclass 集中验证

## FontAwesome 相关配置

### sd_fontawesome_source

控制 FontAwesome CSS 的加载方式：

```python
# conf.py

# 方式一：不自动加载（默认），自行通过主题或html_css_files引入
sd_fontawesome_source = "none"

# 方式二：自动从CDN加载
sd_fontawesome_source = "cdn"
```

设置为 `"cdn"` 时，扩展会在 `builder-inited` 阶段调用 `app.add_css_file()` 添加 FA CSS。仅对 HTML 构建生效。

### sd_fontawesome_cdn_url

自定义 CDN 地址：

```python
sd_fontawesome_source = "cdn"
sd_fontawesome_cdn_url = "https://cdn.example.com/fontawesome/6.1.1/css/all.min.css"
```

默认值为 `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css`。

### sd_fontawesome_version

控制 FontAwesome 图标角色输出的 CSS 类名方案：

```python
# 默认：按角色名原样输出
sd_fontawesome_version = "as-named"
# :fas: → "fas fa-xxx"
# :fa-solid: → "fa-solid fa-xxx"

# 强制使用 FA6 类名
sd_fontawesome_version = "6"
# :fas: → "fa-solid fa-xxx"
# :fab: → "fa-brands fa-xxx"

# 强制使用 FA5 类名
sd_fontawesome_version = "5"
# :fa-solid: → "fas fa-xxx"

# 强制使用 FA4 类名
sd_fontawesome_version = "4"
# :fas: → "fa fa-xxx"（所有样式都映射到 fa）
```

版本映射表：

| 语义样式 | v4 | v5 | v6 |
|---|---|---|---|
| solid | `fa` | `fas` | `fa-solid` |
| brands | `fa` | `fab` | `fa-brands` |
| regular | `fa` | `far` | `fa-regular` |

### sd_fontawesome_latex

控制 LaTeX/PDF 输出中 FontAwesome 图标的渲染：

```python
# 不渲染（默认），发出一次性警告
sd_fontawesome_latex = False  # 或 "none"

# 使用 fontawesome 包（\faicon 命令）
sd_fontawesome_latex = True  # 或 "fontawesome"

# 使用 fontawesome5 包（\faIcon 命令，推荐，支持brands/regular）
sd_fontawesome_latex = "fontawesome5"
```

`True` 和 `False` 是向后兼容的布尔值，内部归一化为字符串模式。

## Tab 持久化配置

### sd_tabs_storage_prefix

控制 Tab 选中状态在 localStorage 中的 key 前缀：

```python
# 默认：启用持久化
sd_tabs_storage_prefix = "sphinx-design-tab-id-"

# 自定义前缀（多文档站点避免冲突）
sd_tabs_storage_prefix = "my-docs-tab-"

# 完全禁用持久化（每次刷新恢复默认选中）
sd_tabs_storage_prefix = ""
```

JS 在脚本加载时通过 `document.currentScript.getAttribute("data-sd-tabs-storage-prefix")` 读取此值（作为 script 标签的 data 属性注入）。空字符串时 localStorage 读写被跳过，但 Tab 同步和 URL hash 功能仍正常工作。

## 自定义指令（sd_custom_directives）

这是 sphinx-design 最强大的扩展能力之一，允许在 `conf.py` 中声明新的指令名，继承内置指令并预设参数和选项，**无需编写 Python 代码**。

### 基本语法

```python
# conf.py
sd_custom_directives = {
    "新指令名": {
        "inherit": "继承的内置指令名",
        "argument": "默认位置参数",       # 可选
        "options": {                      # 可选
            "选项名": "默认值",
        },
    },
}
```

### 示例1：预设样式的卡片

```python
sd_custom_directives = {
    "warning-card": {
        "inherit": "card",
        "argument": "⚠️ 警告",
        "options": {
            "shadow": "lg",
        },
    },
    "info-card": {
        "inherit": "card",
        "options": {
            "shadow": "sm",
        },
    },
}
```

使用时：

```rst
.. warning-card::

   这是一个预设为"警告"样式的卡片。

.. info-card:: 自定义标题
   :shadow: md

   这是一个信息卡片，覆盖了默认阴影。
```

自定义指令的默认选项会在指令自身未提供该选项时生效；指令中显式指定的选项优先级更高（覆盖默认值）。

### 示例2：预设颜色的按钮

```python
sd_custom_directives = {
    "btn-get-started": {
        "inherit": "button-ref",
        "argument": "getting-started",
        "options": {
            "color": "primary",
            "ref-type": "ref",
            "shadow": "",  # flag类型选项，空字符串即启用
            "expand": "",
        },
    },
}
```

注意：flag 类型选项（无值的开关选项），在 options 中设置为空字符串 `""` 即可启用。

### 验证规则

注册自定义指令时，系统会验证：
1. `inherit` 值必须是已注册的 sphinx-design 指令名，否则发出警告
2. `options` 中的 key 必须在继承指令的 `option_spec` 中存在，否则发出警告
3. 无效的自定义指令配置不会影响其他指令或阻止构建

验证发生在 `config-inited` 事件中，使用 `capture_directives` 捕获的指令映射表。

## docinfo 字段：sd_hide_title

在文档开头的 docinfo 中添加 `:sd_hide_title:` 字段，可以隐藏第一个 section 的标题（用于 landing page 等场景）：

```rst
:sd_hide_title:

Welcome
=======

这是首页，标题被隐藏了。
```

这由 `AddFirstTitleCss` Transform（priority=699）实现，给第一个 title 添加 `sd-d-none` 类（display: none）。

## 完整配置示例

```python
# conf.py
extensions = [
    "sphinx_design",
    # ... 其他扩展
]

# FontAwesome 配置
sd_fontawesome_source = "cdn"
sd_fontawesome_version = "6"
sd_fontawesome_latex = "fontawesome5"

# Tab 配置
sd_tabs_storage_prefix = "myproject-tab-"

# 自定义指令
sd_custom_directives = {
    "feature-card": {
        "inherit": "grid-item-card",
        "options": {
            "columns": "6 6 4 3",
            "shadow": "md",
            "text-align": "center",
        },
    },
    "note-dropdown": {
        "inherit": "dropdown",
        "options": {
            "color": "info",
            "icon": "info",
        },
    },
    "code-tab": {
        "inherit": "tab-set-code",
        "options": {
            "sync-group": "code",
        },
    },
}
```

## 相关概念

- [扩展架构与两阶段渲染](02-extension-architecture.md) — SdDirective 基类如何应用自定义默认值
- [源码参考与配置速查](../references/source-reference.md) — 完整指令/角色/配置列表
- [快速上手](01-getting-started.md) — 安装和基础配置
