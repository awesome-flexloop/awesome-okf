---
type: Concept
title: 配置选项全解
description: 详解sphinxext-opengraph的11个conf.py配置项，包含类型、默认值、用法示例与注意事项
tags: [sphinxext-opengraph, configuration, conf.py, options, ogp_site_url, ogp_image]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 配置选项全解

sphinxext-opengraph 通过 `setup()` 函数在 Sphinx 应用上注册了11个配置值。所有配置项都以 `ogp_` 前缀命名，放在 `conf.py` 中设置。本章逐个详解每个配置项的作用、类型、默认值和使用场景。

## 配置注册机制

所有配置项通过 `app.add_config_value()` 注册，第三个参数 `'html'` 表示这些配置仅在HTML构建器中生效。这意味着非HTML构建（如epub、latex）不会处理OGP标签——实际上 `html_page_context` 函数开头就检查了 `app.builder.name == 'epub'` 并直接返回。

## 基础URL配置

### ogp_site_url

**类型**：`str`  
**默认值**：`''`（空字符串）  
**必填性**：强烈建议设置（ReadTheDocs环境可自动检测）

这是最重要的配置项，指定你的文档站点的公开根URL。所有页面的 `og:url` 和图片URL都基于此URL拼接。

```python
ogp_site_url = "https://docs.example.org/en/latest/"
```

URL应该以 `/` 结尾，以确保 `urljoin` 正确拼接页面路径。如果不以 `/` 结尾，最后一个路径段会被当作文件名处理，导致URL拼接错误。

在ReadTheDocs环境中，如果 `ogp_site_url` 未设置且检测到 `READTHEDOCS` 环境变量，扩展会自动调用 `ambient_site_url()` 从 `READTHEDOCS_CANONICAL_URL` 环境变量解析URL。

### ogp_canonical_url

**类型**：`str`  
**默认值**：`''`（空字符串，回退到 `ogp_site_url`）

用于设置规范URL（canonical URL），主要用于版本化文档场景。当你的文档有多个版本（如 `en/latest/`、`en/stable/`、`en/v2.0/`）时，你可能希望 `og:url` 指向 `stable` 版本而非当前浏览版本，这类似HTML的 `<link rel="canonical">` 功能。

```python
ogp_site_url = "https://docs.example.org/en/latest/"
ogp_canonical_url = "https://docs.example.org/en/stable/"
```

设置后，`og:url` 和社交卡片中显示的URL文本将使用 `ogp_canonical_url`，而非 `ogp_site_url`。如果未设置，默认使用 `ogp_site_url` 的值。

## 描述配置

### ogp_description_length

**类型**：`int`  
**默认值**：`200`

控制自动从页面内容提取的描述文本的最大字符数。描述提取器（DescriptionParser）遍历doctree时，会在累积文本超过此长度时截断并追加 `...`。

```python
ogp_description_length = 300  # 使用更长的描述
```

注意：实际截断长度会预留3个字符给 `...`，所以设置为200时，描述实际最长为200字符（含省略号）。截断逻辑位于 `DescriptionParser.dispatch_departure()` 中。

此值可以被页面级 field lists 的 `:ogp_description_length:` 覆盖。

### ogp_enable_meta_description

**类型**：`bool`  
**默认值**：`True`

控制是否同时生成 `<meta name="description" content="...">` 标签。Open Graph的 `og:description` 和HTML标准的 `meta name="description"` 是两个不同的标签，前者供社交媒体爬虫使用，后者供搜索引擎使用。

```python
ogp_enable_meta_description = True   # 默认，同时生成两个标签
ogp_enable_meta_description = False  # 仅生成 og:description
```

当此选项为True时，扩展会先通过 `get_meta_description()` 检查 `context['metatags']` 中是否已存在手动设置的 `<meta name="description">` 标签。如果已存在，则不覆盖，避免重复或冲突。

## 站点信息配置

### ogp_site_name

**类型**：`str | bool | None`  
**默认值**：`None`（回退到 `project` 配置值）

设置站点名称，对应 `og:site_name` 标签。站点名称通常显示在社交媒体卡片中标题的上方。

```python
ogp_site_name = "My Project Documentation"  # 自定义名称
ogp_site_name = False                        # 禁用 site_name 标签
```

行为逻辑：
- 设置为字符串：使用该值作为 `og:site_name`
- 设置为 `False`：不生成 `og:site_name` 标签
- 设置为 `None`（默认）：使用Sphinx内置的 `project` 配置值
- 设置为 `True`（非法值）：会被当作字符串 "True" 处理（不推荐）

### ogp_type

**类型**：`str`  
**默认值**：`'website'`

设置 `og:type` 标签，指定页面内容类型。Open Graph协议定义了多种类型：

| 类型 | 适用场景 |
|------|---------|
| `website`（默认） | 普通网站/文档页面 |
| `article` | 博客文章、新闻条目 |
| `book` | 书籍 |
| `profile` | 个人资料页 |
| `music.song` / `video.movie` 等 | 特定媒体类型 |

```python
ogp_type = "article"  # 博客/文章类文档
```

完整类型列表参见 [Open Graph官方文档](https://ogp.me/#types)。此值可被页面级 `:og:type:` 覆盖。

## 图片配置

### ogp_image

**类型**：`str | None`  
**默认值**：`None`

设置全局默认的OG图片URL。当页面没有通过 `:og:image:` field list指定图片，且 `ogp_use_first_image` 为False时，使用此图片作为 `og:image`。

```python
ogp_image = "https://docs.example.org/_static/logo.png"
# 或相对路径（相对于ogp_site_url根目录）
ogp_image = "_static/logo.png"
```

相对路径会通过 `urljoin(ogp_site_url, image_path)` 转换为绝对URL。

### ogp_image_alt

**类型**：`str | bool | None`  
**默认值**：`None`

设置 `og:image:alt` 标签，为图片提供替代文本（无障碍访问要求）。

```python
ogp_image_alt = "My Project Logo"  # 自定义alt文本
ogp_image_alt = False              # 禁用alt标签
```

回退逻辑：
1. 如果 `ogp_image_alt` 是字符串，使用该值
2. 如果为 `None` 且 `ogp_site_name` 有值，使用站点名称
3. 如果为 `None` 且页面标题存在，使用页面标题
4. 设置为 `False` 时不生成 `og:image:alt`

### ogp_use_first_image

**类型**：`bool`  
**默认值**：`False`

设置为 `True` 时，扩展会自动查找页面中的第一张图片（通过 `doctree.next_node(nodes.image)` ），将其作为OG图片。这对包含截图或插图的教程页面特别有用。

```python
ogp_use_first_image = True
```

图片选择逻辑：
1. 查找doctree中第一个 `nodes.image` 节点
2. 检查图片文件扩展名是否在 `IMAGE_MIME_TYPES` 支持列表中
3. 如果找到有效图片，使用其URI和alt文本
4. 如果未找到有效图片，回退到 `ogp_image` 配置
5. 如果两者都没有，且社交卡片功能启用，自动生成社交卡片

注意：当页面通过 `:og:image:` field list指定了图片时，此选项被忽略。

## 社交卡片配置

### ogp_social_cards

**类型**：`dict | None`  
**默认值**：`None`（等价于 `DEFAULT_SOCIAL_CONFIG`）

配置自动生成的社交媒体预览卡片。设置为字典可自定义卡片外观和行为，设置为 `None` 使用默认配置。

```python
# 完全禁用社交卡片
ogp_social_cards = {
    "enable": False,
}

# 自定义卡片
ogp_social_cards = {
    "image": "_static/custom-logo.png",
    "line_color": "#4078c0",
    "font": "Noto Sans CJK JP",
}
```

社交卡片仅在以下条件全部满足时才会生成：
- `ogp_image` 未设置或为None
- `ogp_use_first_image` 为False（或页面无有效图片）
- `ogp_social_cards` 未设置 `enable: False`
- matplotlib已安装（`create_social_card` 不为None）

详细配置参见[社交卡片生成](/concepts/08-social-cards.md)章节。

## 自定义标签

### ogp_custom_meta_tags

**类型**：`list | tuple`  
**默认值**：`()`（空元组）

添加自定义HTML meta标签片段。列表中的每个字符串会被原样插入到页面的meta标签区域。

```python
ogp_custom_meta_tags = [
    '<meta property="og:ignore_canonical" content="true" />',
    '<meta name="twitter:site" content="@myproject" />',
]
```

这是添加扩展未原生支持的OGP标签（如 `og:video`、`og:audio`、Twitter特有标签等）的通用方式。注意：字符串必须是完整的、自闭合的HTML标签。

## 配置优先级总结

多个配置来源的优先级从高到低：

1. **页面级field lists**（`:og:*` 字段）— 最高优先级
2. **conf.py配置值**（`ogp_*` 变量）
3. **环境自动检测**（ReadTheDocs环境变量）
4. **内置默认值**— 最低优先级

但有一个重要例外：`ogp_custom_meta_tags` 是追加而非覆盖——自定义标签总是被添加到标签列表末尾。

## 典型配置组合

### 最小配置

```python
ogp_site_url = "https://docs.example.org/"
```

### 标准文档站配置

```python
ogp_site_url = "https://docs.example.org/en/latest/"
ogp_image = "_static/og-logo.png"
ogp_use_first_image = True
```

### 带社交卡片的完整配置

```python
ogp_site_url = "https://docs.example.org/"
ogp_social_cards = {
    "enable": True,
    "line_color": "#009688",
}
ogp_custom_meta_tags = [
    '<meta name="twitter:creator" content="@author_handle" />',
]
```

### 版本化文档配置

```python
ogp_site_url = f"https://docs.example.org/en/{version}/"
ogp_canonical_url = "https://docs.example.org/en/stable/"
```

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [核心标签生成流程](/concepts/03-tag-generation.md)
- [页面图片处理逻辑](/concepts/05-image-handling.md)
- [社交卡片生成](/concepts/08-social-cards.md)
- [页面级覆盖机制](/concepts/06-per-page-overrides.md)
- [高级配置示例](/examples/advanced-config.md)
- [sphinxext-opengraph 源码信源登记](/references/sphinxext-opengraph-source.md)
