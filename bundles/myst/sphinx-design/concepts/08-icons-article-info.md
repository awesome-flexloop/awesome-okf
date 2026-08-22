---
type: concept
title: 图标系统与文章信息栏
description: octicon/fontawesome/material 三类图标角色用法，article-info 文章元信息指令
tags:
- sphinx
- design
- icon
- octicon
- fontawesome
- material
- article-info
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/icons.py
- sphinx_design/article_info.py
---

# 图标系统与文章信息栏

sphinx-design 内置三套图标系统，并提供 `article-info` 指令用于展示文章元信息。

## 图标系统概览

| 图标库 | 类型 | 角色前缀 | CSS/JS依赖 | LaTeX支持 |
|---|---|---|---|---|
| GitHub Octicons | SVG 内嵌 | `octicon` | 无（预编译JSON） | ❌ 跳过 |
| Font Awesome | CSS class | `fa/fas/fab/far/fa-*` | 需要FA CSS（CDN或主题） | ✅ fontawesome5包 |
| Material Design Icons | SVG 内嵌 | `material-*` | 无（预编译JSON） | ❌ 跳过 |

**SVG 内嵌图标**（Octicon/Material）的特点：
- 零外部依赖，图标数据预编译为 JSON 打包在扩展中
- 直接生成 `<svg>` HTML 标记插入文档
- 无网络请求、无FOIT（无样式文本闪烁）
- 刻意无子文本节点（`astext()` 返回空字符串），避免 SVG 标记污染目录标签、搜索索引、页面标题
- 非HTML输出中使用 SkipNode 跳过（不输出任何内容）

**FontAwesome 图标**的特点：
- 通过 CSS class 渲染（`<span class="fas fa-rocket">`）
- 需要加载 FontAwesome CSS（通过 `sd_fontawesome_source = "cdn"` 或主题提供）
- LaTeX 输出可通过 fontawesome/fontawesome5 包渲染
- 支持v4/v5/v6三种类名方案

## Octicon（GitHub 图标）

### 基本语法

```rst
:octicon:`icon-name`
:octicon:`icon-name;size`
:octicon:`icon-name;size;extra-classes`
```

参数用分号分隔：
1. **图标名**（必填）：Octicon 图标名称
2. **尺寸**（可选）：高度值，支持 `px`/`em`/`rem` 单位，默认 `1em`
3. **额外CSS类**（可选）：空格分隔的类名

### 使用示例

```rst
主页 :octicon:`home;1.2em`
设置 :octicon:`gear;1em;sd-pr-2`
```

MyST:

```markdown
主页 {octicon}`home;1.2em`
```

### 尺寸规则

- 支持的单位：`px`、`em`、`rem`
- 高度格式：`<数值><单位>`，如 `16px`、`1em`、`1.5rem`
- 默认原始尺寸为 16px；当高度 ≥1.5em 或 ≥24px 时自动使用 24px 版本
- 宽度按原始宽高比等比缩放

### 可访问性

- 默认设置 `aria-hidden="true"`（装饰性图标）
- 未来可通过 aria_label 参数添加可访问标签（API已预留，当前role语法未暴露）

### 可用图标

Octicon 图标列表可使用 `_all-octicon` 指令生成（主要用于自身文档），或参考 [Octicons 官网](https://primer.style/foundations/icons)。

常用图标包括：`home`、`gear`、`rocket`、`alert`、`check`、`x`、`chevron-right`、`chevron-down`、`calendar`、`clock`、`kebab-horizontal`、`link`、`pencil`、`star`、`heart`、`book`、`code`、`terminal`、`file`、`folder`、`search`、`mail`。

## Font Awesome 图标

### 角色名

sphinx-design 注册了多组 FontAwesome 角色，兼容 v4/v5/v6：

| 角色名 | 样式 | 版本兼容性 |
|---|---|---|
| `:fa:`icon`` | Solid（v4兼容） | v4/v5/v6（通过version配置映射） |
| `:fas:`icon`` | Solid | v5+ |
| `:fab:`icon`` | Brands | v5+ |
| `:far:`icon`` | Regular | v5+ |
| `:fa-solid:`icon`` | Solid | v6 规范名 |
| `:fa-brands:`icon`` | Brands | v6 规范名 |
| `:fa-regular:`icon`` | Regular | v6 规范名 |

### 基本语法

```rst
:fas:`icon-name`
:fas:`icon-name;extra-classes`
```

### 使用示例

```rst
:fas:`rocket` :fab:`python` :far:`star`
```

### FontAwesome 版本配置

通过 `sd_fontawesome_version` 配置控制输出的CSS类名：

```python
# conf.py
sd_fontawesome_version = "as-named"  # 默认：按角色名原样输出
```

| 配置值 | `:fas:` 输出 | `:fa-solid:` 输出 |
|---|---|---|
| `"as-named"` | `fas fa-*` | `fa-solid fa-*` |
| `"6"` | `fa-solid fa-*` | `fa-solid fa-*` |
| `"5"` | `fas fa-*` | `fas fa-*` |
| `"4"` | `fa fa-*` | `fa fa-*` |

### 加载 FontAwesome CSS

sphinx-design 默认不加载 FontAwesome CSS。使用 CDN 加载：

```python
# conf.py
sd_fontawesome_source = "cdn"  # 默认使用 cdnjs FA 6.1.1
# 或自定义 CDN：
# sd_fontawesome_cdn_url = "https://你的CDN地址/all.min.css"
```

### LaTeX 输出

要在 LaTeX/PDF 中渲染 FontAwesome 图标：

```python
sd_fontawesome_latex = "fontawesome5"  # 推荐
```

需要 LaTeX 文档中可用 fontawesome5 包。brands 图标和 regular 样式在 fontawesome5 模式下通过 `\faIcon[regular]{name}` 命令支持。

非HTML/LaTeX输出（man/text/texinfo）中 FontAwesome 图标发出一次性警告并跳过。

## Material Design Icons

### 角色名

| 角色名 | 样式 |
|---|---|
| `:material-regular:`icon`` | Regular（填充） |
| `:material-outlined:`icon`` | Outlined（轮廓） |
| `:material-round:`icon`` | Round（圆角） |
| `:material-sharp:`icon`` | Sharp（锐角） |
| `:material-twotone:`icon`` | Two-tone（双色调） |

### 基本语法

```rst
:material-regular:`icon-name`
:material-regular:`icon-name;size`
:material-regular:`icon-name;size;extra-classes`
```

参数格式与 Octicon 相同（分号分隔：name;height;classes）。

### 使用示例

```rst
:material-regular:`home;1.2em`
:material-outlined:`settings;1em;sd-pr-2`
```

尺寸规则与 Octicon 相同：默认原始高度 20px，≥1.5em/≥24px 使用 24px 版本。CSS 类前缀为 `sd-material-icon`。

## article-info（文章信息栏）

`article-info` 指令在文档顶部展示文章元信息（作者、日期、阅读时间、头像），内部使用网格布局和 Octicon 图标。

### 基本用法

```rst
.. article-info::
   :author: 张三
   :date: 2024-01-01
   :read-time: 5 分钟阅读
```

### 完整选项

| 选项 | 值 | 必填 | 说明 |
|---|---|---|---|
| `author` | 文本 | ✅ | 作者名（支持内联标记） |
| `date` | 文本 | ✅ | 日期文本 |
| `read-time` | 文本 | ✅ | 阅读时间文本 |
| `avatar` | URI | ❌ | 头像图片URL |
| `avatar-alt` | 文本 | ❌ | 头像alt文本 |
| `avatar-link` | URI | ❌ | 头像链接URL |
| `avatar-outline` | 语义色 | ❌ | 头像轮廓颜色 |
| `class-container` | CSS类 | ❌ | 容器额外类 |
| `class-avatar` | CSS类 | ❌ | 头像额外类 |

### 带头像的完整示例

```rst
.. article-info::
   :avatar: _static/avatar.jpg
   :avatar-alt: 作者头像
   :avatar-link: https://github.com/author
   :avatar-outline: primary
   :author: 张三
   :date: 2024年1月1日
   :read-time: 约 8 分钟
```

### 布局结构

article-info 使用嵌套网格布局：

```
┌─────────────────────────────────────────┐
│ ┌──────┐ ┌────────────────────────────┐ │
│ │ 头像 │ │ 作者  日历图标 日期 时钟 阅读时间 │ │
│ └──────┘ └────────────────────────────┘ │
└─────────────────────────────────────────┘
```

- 外层：`sd-container-fluid` + `sd-row sd-row-cols-2 sd-gx-2 sd-gy-1`
- 头像列：`sd-col-auto`，头像使用 `sd-avatar-sm` 类
- 信息列：嵌套网格，`sd-row-cols-2 sd-row-cols-sm-3` 响应式列数
- date 字段带 `calendar` octicon（16px，`sd-pr-2`右边距）
- read-time 字段带 `clock` octicon（16px，`sd-pr-2`右边距）
- 文本字段默认解析内联标记（粗体、链接等）

## 相关概念

- [快速上手](/concepts/01-getting-started.md) — FontAwesome CDN 配置
- [卡片组件](/concepts/05-cards.md) — 在卡片中使用图标
- [徽章与按钮](/concepts/07-badges-buttons.md) — 在按钮中使用图标
