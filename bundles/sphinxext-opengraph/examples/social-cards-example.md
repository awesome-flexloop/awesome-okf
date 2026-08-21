---
type: Example
title: 社交卡片完整配置示例
description: 配置自动生成社交媒体预览PNG卡片的完整示例，包括自定义图片、颜色、字体和卡片禁用
tags: [sphinxext-opengraph, example, social-cards, matplotlib, customization, preview-image]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 社交卡片完整配置示例

本示例演示如何配置和自定义sphinxext-opengraph的社交卡片（Social Cards）功能，让文档链接在社交媒体分享时自动展示精美的预览图片。

## 前置条件

社交卡片功能需要matplotlib：

```bash
pip install sphinxext-opengraph[social_cards]
```

或单独安装：

```bash
pip install sphinxext-opengraph matplotlib
```

## 基础社交卡片配置

最简单的社交卡片配置——什么都不配置，使用默认设置：

```python
# conf.py
extensions = ['sphinxext.opengraph']

ogp_site_url = 'https://my-project.readthedocs.io/en/latest/'
html_logo = '_static/logo.png'  # 可选，用作卡片右上角图片
```

默认情况下，社交卡片会自动启用，使用：
- 白色背景
- 内置Roboto Flex字体
- 默认蓝灰色装饰线（#5A626B）
- html_logo作为右上角图片（如果有）
- 内置Sphinx logo作为右下角小图

## 完整自定义配置

```python
# conf.py
extensions = ['sphinxext.opengraph']

ogp_site_url = 'https://my-project.readthedocs.io/en/latest/'
html_logo = '_static/my-logo.png'

ogp_social_cards = {
    # 启用/禁用
    "enable": True,

    # 右上角大图：优先使用image，否则使用html_logo
    "image": "_static/og-preview.png",  # 自定义大图（相对于srcdir）

    # 右下角小图
    "image_mini": "_static/favicon.png",

    # URL显示
    "site_url": "my-project.readthedocs.io",  # 自定义显示URL（True=自动提取）

    # 颜色自定义（十六进制）
    "line_color": "#4078c0",        # 底部装饰线颜色（GitHub蓝）
    "background_color": "#1a1a2e",  # 深色背景
    "text_color": "#eaeaea",        # 标题和URL文本颜色（浅色适应深色背景）

    # 字体
    "font": "Noto Sans CJK SC",     # 思源黑体（需系统已安装）

    # 文本长度
    "description_max_length": 150,  # 描述文本最大长度
}
```

## 禁用社交卡片

如果已有统一的OG图片且不需要自动生成卡片：

```python
# 方法1：配置中禁用
ogp_social_cards = {
    "enable": False,
}
ogp_image = '_static/default-og-image.png'  # 使用固定图片代替

# 方法2：不安装matplotlib（功能自动禁用）
# pip install sphinxext-opengraph  # 不安装[social_cards] extra
```

## 不同页面不同图片策略

结合 `ogp_use_first_image` 和社交卡片，实现智能图片选择：

```python
# 全局配置：优先使用页面第一张图片，无图片时自动生成卡片
ogp_site_url = 'https://my-project.readthedocs.io/en/latest/'
ogp_use_first_image = True
ogp_image = '_static/default-logo.png'  # 兜底：页面无图时的默认图
# 注意：如果ogp_image也未设置，则社交卡片作为最终兜底
```

图片选择优先级：
1. 页面 `:og:image:` field list
2. 页面第一张图片（ogp_use_first_image=True时）
3. 全局ogp_image
4. 自动生成社交卡片

## 中文文档字体配置

对于中文文档，默认的Roboto Flex字体不支持中文字符，需要配置支持中文的字体：

```python
ogp_social_cards = {
    "font": "Noto Sans CJK SC",  # 思源黑体
    # 或
    "font": "Microsoft YaHei",   # 微软雅黑（Windows系统）
    # 或
    "font": "WenQuanYi Micro Hei",  # 文泉驿（Linux系统）
}
```

确保所选字体在构建环境中已安装：

```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk

# macOS（通常已自带中文字体）

# Windows（通常已自带微软雅黑）
```

## ReadTheDocs上的社交卡片配置

RTD默认不安装matplotlib，需要在 `.readthedocs.yaml` 中指定安装社交卡片依赖：

```yaml
# .readthedocs.yaml
version: 2

sphinx:
  configuration: docs/conf.py

python:
  install:
    - requirements: docs/requirements.txt
```

在 `docs/requirements.txt` 中添加：

```txt
sphinxext-opengraph[social_cards]
matplotlib
```

## 预览生成的卡片

构建后，卡片PNG文件位于：

```
_build/html/_images/social_previews/
```

文件名格式为 `summary_{pagename}_{hash}.png`，例如：
- `summary_index_a1b2c3d4.png`（首页）
- `summary_api_reference_e5f6g7h8.png`（API参考页）

可以直接打开这些文件预览效果。

### 使用预览脚本

项目自带的预览生成脚本（需要克隆源码）：

```bash
cd docs
python script/generate_social_card_previews.py
```

这会在 `docs/tmp/` 目录下生成示例卡片预览。

## 验证卡片效果

### 本地验证

1. 使用Python内置HTTP服务器预览构建结果：

```bash
cd _build/html
python -m http.server 8000
```

2. 打开 `http://localhost:8000`，查看页面源码确认meta标签存在

3. 使用浏览器开发者工具检查 `<meta property="og:image">` 的URL是否可访问

### 在线验证

- [opengraph.xyz](https://www.opengraph.xyz/) — 输入已部署的URL，预览Twitter/Facebook/LinkedIn等平台效果
- [Twitter Card Validator](https://cards-dev.twitter.com/validator/) — Twitter卡片预览
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/) — Facebook分享调试

## 禁用特定页面的卡片

如果某个页面不需要社交卡片（如搜索页、索引页），使用field list禁用：

```rst
:ogp_disable:

======
Search
======
```

注意：`:ogp_disable:` 会禁用**所有**OGP标签，不仅仅是社交卡片。

## 常见问题

### 卡片图片不显示

检查：
1. matplotlib是否安装（`python -c "import matplotlib; print(matplotlib.__version__)"`）
2. 构建日志中是否有"matplotlib is not installed"警告
3. `ogp_image` 或 `ogp_use_first_image` 是否抢占了图片来源
4. `ogp_social_cards` 中 `enable` 是否设为False

### 卡片上中文显示为方块

这是字体问题。确保：
1. 配置了支持中文的字体
2. 构建环境中安装了该字体
3. 字体名称与Matplotlib FontManager中的名称一致

检查Matplotlib可用字体：

```python
import matplotlib.font_manager as fm
for f in fm.fontManager.ttflist:
    if 'CJK' in f.name or 'Hei' in f.name or 'YaHei' in f.name:
        print(f.name, f.fname)
```

### SVG图片警告

社交卡片不支持SVG图片（Matplotlib限制）。如果 `image` 配置为SVG文件，会看到警告：

```
WARNING: [Social card] image cannot be an SVG image, skipping...
```

改用PNG或JPEG格式的图片。

## 相关概念

- [社交卡片生成](/concepts/08-social-cards.md)
- [页面图片处理逻辑](/concepts/05-image-handling.md)
- [配置选项全解](/concepts/02-configuration.md)
- [基础配置示例](/examples/basic-setup.md)
- [高级配置示例](/examples/advanced-config.md)
- [sphinxext-opengraph 源码信源登记](/references/sphinxext-opengraph-source.md)
