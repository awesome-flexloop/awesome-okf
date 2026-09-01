---
type: Concept
title: 社交卡片生成
description: 详解基于Matplotlib的社交预览卡片自动生成机制，包括图片渲染、缓存复用、样式自定义与字体配置
tags: [sphinxext-opengraph, social-cards, matplotlib, preview-image, og:image, PNG]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 社交卡片生成

社交卡片（Social Cards）是 sphinxext-opengraph 最具特色的功能——当页面没有配置OG图片时，扩展使用 **Matplotlib** 自动生成一张PNG格式的社交媒体预览图，包含站点名称、页面标题、描述文本和站点URL。这确保了即使你没有为每页设计预览图，分享链接时也能展示专业的卡片效果。

## 功能启用条件

社交卡片自动生成需要满足**所有**以下条件：

1. **matplotlib已安装**：`pip install sphinxext-opengraph[social_cards]`，未安装时扩展会打印警告并禁用此功能
2. **没有其他图片来源**：
   - 页面没有通过 `:og:image:` field list指定图片
   - `ogp_image` 配置为None（默认）
   - `ogp_use_first_image` 为False（默认），或页面无有效图片
3. **社交卡片未被禁用**：`ogp_social_cards` 未设置 `enable: False`

```python
# __init__.py 中的条件判断
if (not (image_url or ogp_use_first_image)
    and config_social.get('enable') is not False
    and create_social_card is not None):
    image_url = social_card_for_page(...)
```

如果matplotlib未安装，`create_social_card` 为None：

```python
try:
    from sphinxext.opengraph._social_cards import (
        DEFAULT_SOCIAL_CONFIG, create_social_card,
    )
except ImportError:
    print('matplotlib is not installed, social cards will not be generated')
    create_social_card = None
    DEFAULT_SOCIAL_CONFIG = {}
```

## 卡片布局与设计

社交卡片尺寸约为 **1146 × 600 像素**（1.91:1比例），这是Open Graph协议推荐的图片比例。

### 卡片元素布局

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  [Site Name]                              [Logo Image]  │
│                                                         │
│  [Page Title - Large Bold Text]                         │
│                                                         │
│                                                         │
│  [Description text - smaller, wraps to multiple lines] │
│                                                         │
│  [site-url.org]                   [Sphinx Mini Logo]    │
│                                                         │
│  ███████████████████████████████████████████████████████│
│                                                    (粗线)│
└─────────────────────────────────────────────────────────┘
```

卡片包含五个文本/图片元素：

| 元素 | 位置 | 字号 | 颜色 | 说明 |
|------|------|------|------|------|
| 站点名称 | 左上 | 24pt | #585e63（灰色） | 来自ogp_site_name或project配置 |
| 页面标题 | 站点名称下方 | 46pt | #2f363d（深灰/黑），粗体 | 自动截断至80字符 |
| 描述文本 | 中下部 | 17pt | #585e63（灰色） | 自动截断至157字符+省略号 |
| 站点URL | 左下 | 22pt | #2f363d（深灰/黑），粗体 | 从canonical URL提取 |
| 底部线条 | 最底部 | 25px线宽 | #5A626B（可配置） | 装饰线 |

图片元素：
- **右上角大图**：默认使用 `html_logo`，可通过 `image` 配置自定义
- **右下角小图**：默认为内置Sphinx logo阴影图（sphinx-logo-shadow.png），可通过 `image_mini` 配置

## 核心函数详解

### social_card_for_page()

```python
def social_card_for_page(
    config_social, site_name, title, description, pagename,
    ogp_site_url, ogp_canonical_url, *,
    srcdir, outdir, config, env,
) -> str:
```

此函数为单页生成社交卡片，返回图片相对于站点根目录的URL路径。

处理流程：
1. **文本截断**：描述截断至 `description_max_length`（默认157字符+`...`），标题截断至80字符+`...`
2. **URL处理**：从canonical URL提取显示文本（去掉scheme部分）
3. **调用create_social_card()**：生成PNG文件
4. **返回图片URL**：使用 `posixpath.join(ogp_site_url, image_path)` 拼接

### create_social_card()

```python
def create_social_card(
    config_social, site_name, page_title, description, url_text, page_path,
    *, srcdir, outdir, env, html_logo=None,
) -> Path:
```

这是社交卡片生成的核心函数，负责：

#### 1. 内容哈希与缓存

```python
hash = hashlib.sha1(
    (site_name + page_title + description + str(config_social)).encode(),
    usedforsecurity=False,
).hexdigest()[:8]
```

基于站点名+页面标题+描述+配置的SHA1哈希（前8位），用于：
- 生成唯一文件名：`summary_{pagename}_{hash}.png`
- 缓存判断：如果文件已存在则跳过生成（内容不变则图片不变）

文件名中的 `/` 被替换为 `_`：`summary_{page_path.replace("/", "_")}_{hash}.png`

#### 2. 输出路径

图片输出到：`{outdir}/_images/social_previews/summary_*.png`

`{outdir}` 是Sphinx的HTML输出目录（通常为 `_build/html/`）。

#### 3. 图片资源处理

```python
if cs_image := config_social.get('image'):
    kwargs_fig['image'] = Path(srcdir) / cs_image
elif html_logo:
    kwargs_fig['image'] = Path(srcdir) / html_logo

if cs_image_mini := config_social.get('image_mini'):
    kwargs_fig['image_mini'] = Path(srcdir) / cs_image_mini
else:
    kwargs_fig['image_mini'] = Path(__file__).parent / '_static/sphinx-logo-shadow.png'
```

图片验证：
- SVG图片不支持（Matplotlib限制），会打印警告并跳过
- 不存在的图片文件会打印警告并跳过

#### 4. Matplotlib对象复用

```python
try:
    plt_objects = env.ogp_social_card_plt_objects
except AttributeError:
    plt_objects = create_social_card_objects(**kwargs_fig)
plt_objects = render_social_card(path, site_name, page_title, description, url_text, plt_objects)
env.ogp_social_card_plt_objects = plt_objects
```

**性能优化**：Matplotlib Figure和Text对象在第一次创建后缓存在 `BuildEnvironment` 上（`env.ogp_social_card_plt_objects`），后续页面只更新Text对象的内容并重新savefig，避免重复创建Figure。这对大型文档站点（数百页面）的构建性能有显著提升。

### create_social_card_objects()

此函数创建Matplotlib Figure和Text对象：

1. **字体加载**：默认使用内置Roboto Flex字体（`_static/Roboto-Flex.ttf`），通过 `matplotlib.font_manager.FontEntry` 注册
2. **Figure创建**：使用 `figsize=(ratio * multiple, multiple)` 其中 ratio=1200/628, multiple=6，最终约1146×600像素
3. **坐标轴设置**：
   - `axtext`：全文本区域（0,0,1,1）
   - `axim_logo`：右上角logo（0.65,0.65,0.3,0.3），锚点NE
   - `axim_mini`：右下角小图（0.82,0.1,0.1,0.1），锚点NE
   - `axline`：底部线条（-0.1,-0.04,1.2,0.1）
4. **文本对象创建**：创建5个Text对象（站点名、页面标题、描述、URL），使用 `wrap=True` 自动换行
5. **图片加载**：使用 `mpimg.imread()` 加载logo图片
6. **坐标轴美化**：所有axes调用 `set_axis_off()` 隐藏刻度和边框

返回值是一个五元组：`(Figure, Text_site, Text_page, Text_desc, Text_url)`

### render_social_card()

```python
def render_social_card(path, site_title, page_title, description, siteurl, plt_objects):
    fig, txt_site_title, txt_page_title, txt_description, txt_url = plt_objects
    txt_site_title.set_text(site_title)
    txt_page_title.set_text(page_title)
    txt_description.set_text(description)
    txt_url.set_text(siteurl)
    fig.savefig(path, facecolor=None)
    return fig, txt_site_title, txt_page_title, txt_description, txt_url
```

简单高效——更新Text对象的文本内容，然后savefig保存。

## 配置选项

`ogp_social_cards` 字典支持以下配置键：

| 键 | 类型 | 默认值 | 说明 |
|----|------|--------|------|
| `enable` | bool | True | 是否启用社交卡片自动生成 |
| `site_url` | bool \| str | True | 卡片上显示的URL；True自动从canonical URL提取；str为自定义URL文本 |
| `image` | str | None | 右上角大图路径（相对于srcdir），默认使用html_logo |
| `image_mini` | str | 内置Sphinx logo | 右下角小图路径（相对于srcdir） |
| `font` | str | 'Roboto Flex'（内置） | 自定义字体名称（需Matplotlib可发现） |
| `line_color` | str | '#5A626B' | 底部装饰线颜色（十六进制） |
| `text_color` | str | '#2f363d' | 页面标题和URL文本颜色 |
| `background_color` | str | 'white' | 卡片背景颜色 |
| `description_max_length` | int | 157 | 描述文本最大字符数 |
| `site_title` | bool | True | 是否显示站点名称 |
| `page_title` | bool | True | 是否显示页面标题 |
| `description` | bool | True | 是否显示描述文本 |

### 内置默认配置

```python
DEFAULT_SOCIAL_CONFIG = {
    'enable': True,
    'site_url': True,
    'site_title': True,
    'page_title': True,
    'description': True,
}
```

用户配置通过字典update覆盖默认值：

```python
config_social = DEFAULT_SOCIAL_CONFIG.copy()
social_card_user_options = config.ogp_social_cards or {}
config_social.update(social_card_user_options)
```

## 社交卡片专用Meta标签

当社交卡片被生成时，扩展会额外设置以下标签：

```python
tags['og:image:width'] = '1146'
tags['og:image:height'] = '600'
meta_tags['twitter:card'] = 'summary_large_image'
```

- `og:image:width/height`：帮助社交平台快速获取图片尺寸，提升渲染性能
- `twitter:card = summary_large_image`：告诉Twitter/X使用大图片卡片模式（而非小缩略图模式）

## 字体配置

默认使用内置的Roboto Flex字体，支持拉丁字符。如果文档使用中文、日文或其他非拉丁文字，需要指定支持这些字符的字体：

```python
ogp_social_cards = {
    "font": "Noto Sans CJK SC",  # 思源黑体简体中文
}
```

注意事项：
- 字体名称必须是Matplotlib FontManager可发现的名称
- 可能需要额外安装字体包（如 `fonts-noto-cjk` on Linux）
- 参见 [Matplotlib字体文档](https://matplotlib.org/stable/tutorials/text/text_props.html#default-font)

## 禁用社交卡片

如果你不需要社交卡片功能（例如已有统一的OG图片，或不想安装matplotlib依赖）：

```python
ogp_social_cards = {
    "enable": False,
}
```

或者不安装matplotlib，功能会自动禁用。

## 预览卡片效果

构建文档后，社交卡片PNG文件位于：

```
_build/html/_images/social_previews/
```

你可以直接打开这些PNG文件预览效果。此外，扩展自身文档目录中有一个预览生成脚本：

```
docs/script/generate_social_card_previews.py
```

在线预览工具：
- [opengraph.xyz](https://www.opengraph.xyz/) — 输入URL预览多平台效果
- [Twitter Card Validator](https://cards-dev.twitter.com/validator) — Twitter卡片预览

## 相关概念

- [页面图片处理逻辑](05-image-handling.md)
- [配置选项全解](02-configuration.md)
- [核心标签生成流程](03-tag-generation.md)
- [社交卡片配置示例](../examples/social-cards-example.md)
- [sphinxext-opengraph 源码信源登记](../references/sphinxext-opengraph-source.md)
