---
type: Concept
title: 快速开始
description: Alabaster 的安装、最小配置和 html_sidebars 设置——3 分钟启用默认主题
tags: [sphinx, theme, alabaster, installation, getting-started]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:53:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# 快速开始

Alabaster 作为 Sphinx 的默认主题，在安装 Sphinx 时已自动安装。但要正确启用 Alabaster 的全部侧边栏组件，需要在 `conf.py` 中进行最小配置。

## 安装

Alabaster 随 Sphinx 自动安装，无需单独安装。如果需要手动安装最新版本：

```bash
pip install alabaster
```

验证安装：

```bash
python -c "import alabaster; print(alabaster.__version__)"
```

## 最小配置

在 Sphinx 项目的 `conf.py` 中添加以下配置：

```python
# conf.py

# 1. 指定主题
html_theme = 'alabaster'

# 2. 配置侧边栏组件（必须，否则 Alabaster 的自定义侧边栏不会加载）
html_sidebars = {
    '**': [
        'about.html',       # Logo、项目名、描述、GitHub 按钮
        'searchfield.html', # 搜索框（Sphinx 内置）
        'navigation.html',  # 目录树导航
        'relations.html',   # 上下页导航
        'donate.html',      # 捐赠链接（可选）
    ]
}

# 3. 如果使用 logo 或自定义 CSS，指定静态文件路径
html_static_path = ['_static']
```

> ⚠️ **重要**：`html_sidebars` 配置是必须的。如果不设置，Sphinx 会使用 basic 主题的默认侧边栏（`localtoc.html`等），Alabaster 的 `about.html`、`navigation.html` 等自定义组件不会加载。

## 主题选项基础配置

在 `conf.py` 中添加 `html_theme_options` 字典配置主题选项：

```python
html_theme_options = {
    # 基础信息
    'description': '一个简洁的 Sphinx 文档主题',
    'github_user': 'your-username',
    'github_repo': 'your-repo',
    'github_button': True,
    'github_type': 'star',
    'show_powered_by': False,

    # 布局
    'page_width': '1000px',
    'sidebar_width': '240px',
    'fixed_sidebar': True,

    # 配色
    'link': '#0066cc',
    'link_hover': '#cc6600',
}
```

## Read the Docs 注意事项

如果文档托管在 [Read the Docs](https://readthedocs.org/) 上，需要在 `conf.py` 中显式设置 `html_theme = 'alabaster'`——RTD 默认会覆盖主题设置，不做显式配置可能不会使用 Alabaster。

## 验证

运行 Sphinx 构建查看效果：

```bash
sphinx-build -b html docs docs/_build/html
```

或使用 Sphinx 自带的预览服务器：

```bash
sphinx-autobuild docs docs/_build/html
```

打开浏览器访问 `http://localhost:8000`，应该能看到 Alabaster 主题的页面——左侧是 Logo 和导航侧边栏，右侧是文档正文，底部有版权信息。

## 侧边栏组件说明

| 组件 | 功能 | 是否必须 |
|------|------|---------|
| `about.html` | 项目 Logo、名称、描述、GitHub 按钮 | 建议保留 |
| `searchfield.html` | 搜索框 | 建议保留 |
| `navigation.html` | 完整目录树（toctree）+ 自定义外部链接 | 建议保留 |
| `relations.html` | 上下页链接和面包屑导航 | 可选 |
| `donate.html` | 捐赠/支持链接（GitHub Sponsors/Open Collective/Tidelift） | 可选 |

可以根据项目需要增删侧边栏组件，例如不需要捐赠链接就移除 `donate.html`，不需要上下页导航就移除 `relations.html`。

## 下一步

- [主题架构四要素](02-theme-architecture.md)：理解 Alabaster 的底层架构
- [主题配置选项体系](04-theme-options.md)：完整的 50+ 配置选项参考
- [基础配置示例](../examples/basic-setup.md)：完整 conf.py 示例
