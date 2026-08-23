---
type: Reference
title: sphinx-design 源码参考与配置速查
description: sphinx-design 源码路径映射、指令/角色/配置项完整速查表
tags:
- sphinx
- extension
- design
- components
- reference
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- sphinx_design/__init__.py
- sphinx_design/extension.py
- sphinx_design/shared.py
- sphinx_design/config.py
- sphinx_design/cards.py
- sphinx_design/grids.py
- sphinx_design/dropdown.py
- sphinx_design/tabs.py
- sphinx_design/badges_buttons.py
- sphinx_design/icons.py
- sphinx_design/article_info.py
---

# sphinx-design 源码参考与配置速查

## 源码路径映射

| 模块文件 | 职责 | 关键导出 |
|---|---|---|
| `__init__.py` | 扩展入口 | `setup(app)` |
| `extension.py` | 主设置函数、静态资源、Div指令、容器visitor覆盖 | `setup_extension()`, `Div`, `AddFirstTitleCss` |
| `config.py` | 配置dataclass与验证 | `SdConfig`, `get_sd_config()`, `setup_sd_config()` |
| `shared.py` | 共享常量、基类、工具函数 | `SdDirective`, `create_component()`, `SEMANTIC_COLORS`, `margin_option()`, `padding_option()` |
| `cards.py` | 卡片组件 | `CardDirective`, `CardCarouselDirective` |
| `grids.py` | 网格布局 | `GridDirective`, `GridItemDirective`, `GridItemCardDirective` |
| `dropdown.py` | 下拉折叠 | `DropdownDirective`, `DropdownHtmlTransform` |
| `tabs.py` | 标签页 | `TabSetDirective`, `TabItemDirective`, `TabSetCodeDirective`, `TabSetHtmlTransform` |
| `badges_buttons.py` | 徽章与按钮 | `BadgeRole`, `LinkBadgeRole`, `XRefBadgeRole`, `ButtonLinkDirective`, `ButtonRefDirective` |
| `icons.py` | 图标系统 | `OcticonRole`, `FontawesomeRole`, `MaterialRole`, `get_octicon()`, `get_material_icon()` |
| `article_info.py` | 文章信息 | `ArticleInfoDirective` |
| `static/sphinx-design.min.css` | 预编译CSS | 所有 `sd-` 前缀样式 |
| `static/design-tabs.js` | Tab同步JS | localStorage持久化、URL hash/query支持 |

## 指令完整列表

### 布局指令

| 指令名 | 参数 | 选项 | 说明 |
|---|---|---|---|
| `grid` | [列数(1-12/auto)] | gutter, margin, padding, outline, reverse, class-container, class-row | 网格容器 |
| `grid-item` | 无 | columns, margin, padding, child-direction(column/row), child-align, outline, class | 网格列 |
| `grid-item-card` | [卡片标题] | columns, margin, padding, class-item + 所有card选项 | 带卡片的网格列 |
| `div` | [CSS类名] | style, name | 无container类的div容器 |

### 卡片指令

| 指令名 | 参数 | 选项 | 说明 |
|---|---|---|---|
| `card` | [标题] | width, margin, text-align, img-top, img-bottom, img-background, img-alt, link, link-type(url/any/ref/doc), link-alt, shadow(none/sm/md/lg), class-card/header/body/title/footer/img-top/img-bottom | 卡片组件 |
| `card-carousel` | 列数(1-12) | class | 横向滚动卡片行 |

卡片内容分隔语法：
- `^^^`（3个以上脱字符）分隔 header 与 body
- `+++`（3个以上加号）分隔 body 与 footer

### 折叠指令

| 指令名 | 参数 | 选项 | 说明 |
|---|---|---|---|
| `dropdown` | [标题] | open(flag), color, icon(octicon名), chevron(right-down/down-up), animate(fade-in/fade-in-slide-down), margin, name, class-container/title/body | 折叠容器 |

### 标签页指令

| 指令名 | 参数 | 选项 | 说明 |
|---|---|---|---|
| `tab-set` | 无 | sync-group, class | Tab容器 |
| `tab-item` | 标签名(必填) | selected(flag), sync, name, class-container/label/content | Tab页 |
| `tab-set-code` | 无 | no-sync(flag), sync-group, class-set/item/label/content | 代码块自动Tab |

### 按钮指令

| 指令名 | 参数 | 选项 | 说明 |
|---|---|---|---|
| `button-link` | URL(必填) | color, outline(flag), align(left/right/center), expand(flag), click-parent(flag), tooltip, shadow(flag), ref-type, class | 外部链接按钮 |
| `button-ref` | 引用目标(必填) | 同button-link | 内部引用按钮 |

### 其他指令

| 指令名 | 参数 | 选项 | 说明 |
|---|---|---|---|
| `article-info` | 无 | avatar, avatar-alt, avatar-link, avatar-outline, author(必填), date(必填), read-time(必填), class-container/avatar | 文章元信息栏 |

## 角色完整列表

### 徽章角色

| 角色名格式 | 说明 |
|---|---|
| `:bdg:`text`` | 无色徽章 |
| `:bdg-{color}:`text`` | 语义色徽章 |
| `:bdg-{color}-line:`text`` | 语义色轮廓徽章 |
| `:bdg-link:`text <url>`` | 外部链接徽章 |
| `:bdg-link-{color}:`text <url>`` | 彩色外部链接徽章 |
| `:bdg-link-{color}-line:`text <url>`` | 彩色轮廓外部链接徽章 |
| `:bdg-ref:`text <target>`` | 内部引用徽章 |
| `:bdg-ref-{color}:`text <target>`` | 彩色内部引用徽章 |
| `:bdg-ref-{color}-line:`text <target>`` | 彩色轮廓内部引用徽章 |

徽章 tooltip 语法：`:bdg-primary:`主要;这是提示``

语义色值：primary, secondary, success, info, warning, danger, light, muted, dark, white, black

### 图标角色

| 角色名格式 | 语法 | 说明 |
|---|---|---|
| `:octicon:`name;height;classes`` | `:octicon:`rocket;1em;sd-pr-2`` | GitHub Octicon SVG图标 |
| `:fas/fa/fab/far:`name;classes`` | `:fas:`rocket;sd-pr-2`` | FontAwesome v4/v5图标 |
| `:fa-solid/fa-brands/fa-regular:`name;classes`` | `:fa-solid:`rocket`` | FontAwesome v6图标 |
| `:material-regular/outlined/round/sharp/twotone:`name;height;classes`` | `:material-regular:`home`` | Material Design SVG图标 |

## 配置项完整列表

| 配置名 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sd_custom_directives` | dict | `{}` | 自定义指令继承映射 |
| `sd_fontawesome_source` | str | `"none"` | FA CSS加载方式：none/cdn |
| `sd_fontawesome_cdn_url` | str | cdnjs FA 6.1.1 URL | FA CDN地址 |
| `sd_fontawesome_version` | str | `"as-named"` | FA类名方案：as-named/4/5/6 |
| `sd_fontawesome_latex` | bool/str | `False` | LaTeX FA渲染：False/True/none/fontawesome/fontawesome5 |
| `sd_tabs_storage_prefix` | str | `"sphinx-design-tab-id-"` | Tab持久化localStorage前缀 |

## 自定义指令配置格式

```python
# conf.py
sd_custom_directives = {
    "warning-card": {
        "inherit": "card",
        "argument": "⚠️ 警告",
        "options": {
            "shadow": "lg",
        }
    }
}
```

## setup() 函数参考

```python
def setup(app: Sphinx) -> dict:
    from .extension import setup_extension
    setup_extension(app)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```

setup_extension 执行顺序：
1. `setup_sd_config(app)` — 注册配置
2. `app.connect("builder-inited", add_static_assets)` — 注册静态资源
3. 覆盖 `nodes.container` HTML visitor
4. 注册 `PassthroughTextElement` null visitors
5. 上下文管理器内注册所有指令（用于 capture_directives）：
   - `div` 指令 + `AddFirstTitleCss` transform
   - `setup_badges_and_buttons(app)`
   - `setup_cards(app)`
   - `setup_grids(app)`
   - `setup_dropdown(app)`
   - `setup_icons(app)`
   - `setup_tabs(app)`
   - `setup_article_info(app)`
6. `app.connect("config-inited", setup_custom_directives)`
