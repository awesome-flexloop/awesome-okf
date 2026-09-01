---
type: Reference
title: sphinxext-opengraph 源码信源登记
description: sphinxext-opengraph v0.13.0 源码路径、版本信息、核心模块清单、配置项与公开API
tags: [sphinxext-opengraph, source, reference, v0.13.0, opengraph, sphinx-extension]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-github
    resource: https://github.com/sphinx-doc/sphinxext-opengraph
    title: sphinxext-opengraph GitHub 仓库
    author: team:sphinx-doc
  - id: sphinxext-opengraph-docs
    resource: https://sphinxext-opengraph.readthedocs.io/
    title: sphinxext-opengraph 官方文档
  - id: sphinxext-opengraph-pypi
    resource: https://pypi.org/project/sphinxext-opengraph/
    title: sphinxext-opengraph on PyPI
---

# sphinxext-opengraph 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | sphinxext-opengraph |
| 版本 | **0.13.0** |
| 描述 | Sphinx Extension to enable OGP support |
| 作者 | Itay Ziv (itay220204@gmail.com) |
| 维护组织 | sphinx-doc |
| 许可证 | BSD-3-Clause |
| Python 要求 | ≥ 3.9 |
| 核心依赖 | Sphinx ≥ 6.0 |
| 可选依赖 | matplotlib ≥ 3（社交卡片生成） |
| 构建系统 | flit_core ≥ 3.12 |
| 官方文档 | <https://sphinxext-opengraph.readthedocs.io/> |
| 源码仓库 | <https://github.com/sphinx-doc/sphinxext-opengraph> |
| PyPI | <https://pypi.org/project/sphinxext-opengraph/> |

## 源码位置

sphinxext-opengraph 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/docs/sphinxext-opengraph/
```

该目录通过 git submodule 引入，本地不做修改。

## 核心模块清单

| 模块 | 文件路径 | 说明 |
|------|---------|------|
| 包入口 | `sphinxext/opengraph/__init__.py` | 主模块，定义版本常量、配置注册、事件处理、标签生成核心逻辑 |
| 描述解析器 | `sphinxext/opengraph/_description_parser.py` | 从 doctree 自动提取页面描述文本 |
| Meta解析器 | `sphinxext/opengraph/_meta_parser.py` | 检测已有的 `<meta name="description">` 标签 |
| 标题解析器 | `sphinxext/opengraph/_title_parser.py` | 解析标题中的HTML标签，提取纯文本和标签外文本 |
| 社交卡片 | `sphinxext/opengraph/_social_cards.py` | 使用Matplotlib生成社交媒体预览PNG图片 |
| 静态资源 | `sphinxext/opengraph/_static/` | 内置Roboto-Flex字体和Sphinx logo阴影图片 |

## 版本常量

定义于 `__init__.py` 第39-40行：

```python
__version__ = '0.13.0'
version_info = (0, 13, 0)
```

## 默认常量

| 常量名 | 值 | 说明 |
|--------|-----|------|
| `DEFAULT_DESCRIPTION_LENGTH` | 200 | 默认描述文本最大字符数 |
| `DEFAULT_DESCRIPTION_LENGTH_SOCIAL_CARDS` | 160 | 社交卡片描述默认最大字符数 |
| `DEFAULT_PAGE_LENGTH_SOCIAL_CARDS` | 80 | 社交卡片页面标题默认最大字符数 |

## 支持的图片MIME类型

`IMAGE_MIME_TYPES` 字典（`__init__.py` 第47-58行）映射文件扩展名到MIME类型：

- gif → image/gif
- apng → image/apng
- webp → image/webp
- jpeg/jpg → image/jpeg
- png → image/png
- bmp → image/bmp
- heic → image/heic
- heif → image/heif
- tiff → image/tiff

## Sphinx扩展注册

`setup(app)` 函数（`__init__.py` 第331-369行）执行以下注册：

1. 注册11个配置值（见下方配置项表）
2. 连接事件：`html-page-context` → `html_page_context`
3. 返回扩展元数据：
   - `version`: `__version__`
   - `env_version`: 1
   - `parallel_read_safe`: True
   - `parallel_write_safe`: True

## 配置项完整清单

| 配置名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `ogp_site_url` | str | `''` | 站点公开URL，必填（RTD环境可自动检测） |
| `ogp_canonical_url` | str | `''` | 规范URL，默认继承ogp_site_url |
| `ogp_description_length` | int | 200 | 页面描述最大字符数 |
| `ogp_image` | str \| None | None | 全局默认OG图片URL |
| `ogp_image_alt` | str \| bool \| None | None | 图片alt文本 |
| `ogp_use_first_image` | bool | False | 是否使用页面第一张图片作为OG图片 |
| `ogp_type` | str | `'website'` | OG类型（website/article等） |
| `ogp_site_name` | str \| bool \| None | None | 站点名称，False禁用，None默认用project |
| `ogp_social_cards` | dict \| None | None | 社交卡片配置字典 |
| `ogp_custom_meta_tags` | list \| tuple | () | 自定义HTML meta标签片段列表 |
| `ogp_enable_meta_description` | bool | True | 是否生成`<meta name="description">` |

## 公开函数清单

### `__init__.py`

| 函数 | 签名 | 说明 |
|------|------|------|
| `setup` | `(app: Sphinx) -> ExtensionMetadata` | Sphinx扩展入口 |
| `html_page_context` | `(app, pagename, templatename, context, doctree) -> None` | html-page-context事件处理器 |
| `get_tags` | `(context, doctree, *, srcdir, outdir, config, builder, env) -> str` | 核心标签生成函数，返回meta标签HTML字符串 |
| `ambient_site_url` | `() -> str` | 从ReadTheDocs环境变量检测站点URL |
| `social_card_for_page` | `(config_social, site_name, title, description, pagename, ogp_site_url, ogp_canonical_url, *, srcdir, outdir, config, env) -> str` | 为单页生成社交卡片图片，返回图片URL路径 |
| `make_tag` | `(property: str, content: str, type_: str = 'property') -> str` | 生成单个meta标签HTML字符串 |

### `_description_parser.py`

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `get_description` | `(doctree: nodes.document, description_length: int, known_titles: Set[str] = frozenset()) -> str` | 从doctree提取描述文本入口函数 |
| `DescriptionParser` | 继承 `nodes.NodeVisitor` | doctree遍历器，智能提取页面描述 |

`DescriptionParser` 关键方法：
- `__init__(self, document, *, desc_len, known_titles=frozenset())`
- `dispatch_visit(self, node)` - 访问节点，跳过Admonition/Invisible/raw/literal_block
- `dispatch_departure(self, node)` - 离开节点，处理标点和长度截断

### `_meta_parser.py`

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `get_meta_description` | `(meta_tags: str) -> bool` | 检测已有meta description标签 |
| `HTMLTextParser` | 继承 `HTMLParser` | 解析HTML meta标签 |

### `_title_parser.py`

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `get_title` | `(title: str) -> tuple[str, str]` | 返回(含HTML标签文本, 纯文本)二元组 |
| `HTMLTextParser` | 继承 `HTMLParser` | 解析标题中的HTML标签 |

### `_social_cards.py`

| 函数/常量 | 签名 | 说明 |
|-----------|------|------|
| `DEFAULT_SOCIAL_CONFIG` | dict | 社交卡片默认配置 |
| `create_social_card` | `(config_social, site_name, page_title, description, url_text, page_path, *, srcdir, outdir, env, html_logo=None) -> Path` | 创建社交卡片PNG，返回相对路径 |
| `render_social_card` | `(path, site_title, page_title, description, siteurl, plt_objects) -> PltObjects` | 渲染卡片到文件，更新Matplotlib文本对象 |
| `create_social_card_objects` | `(image=None, image_mini=None, ...) -> PltObjects` | 创建Matplotlib Figure和Text对象 |

## 社交卡片默认配置

```python
DEFAULT_SOCIAL_CONFIG = {
    'enable': True,
    'site_url': True,
    'site_title': True,
    'page_title': True,
    'description': True,
}
```

社交卡片支持的配置键：
- `enable` (bool): 是否启用社交卡片
- `site_url` (bool|str): 显示的URL，True自动从canonical URL提取
- `image` (str): 右上角大图路径（相对于srcdir）
- `image_mini` (str): 右下角小图路径
- `text_color` / `line_color` / `background_color` (str): 颜色自定义（十六进制）
- `font` (str): 字体名称（需Matplotlib可发现）
- `description_max_length` (int): 描述最大长度

## 社交卡片技术规格

- 输出尺寸：约 1146 × 600 像素（1200/628 比例 × 6倍数）
- 输出格式：PNG
- 输出路径：`_images/social_previews/summary_{pagename}_{hash}.png`
- 缓存机制：基于内容SHA1哈希（前8位），相同内容不重复生成
- Matplotlib对象复用：通过 `env.ogp_social_card_plt_objects` 缓存Figure对象
- 默认字体：Roboto Flex（内置TTF字体文件）
- 默认小图：sphinx-logo-shadow.png（内置）
- SVG图片不支持：Matplotlib不支持SVG渲染，会被跳过并警告

## Per-Page Field Lists 支持的覆盖字段

通过RST field lists在页面顶部设置：

| 字段 | 说明 |
|------|------|
| `:ogp_disable:` | 禁用当前页面的OG标签生成 |
| `:ogp_description_length:` | 覆盖描述长度 |
| `:og:description:` | 覆盖OG描述文本 |
| `:og:title:` | 覆盖OG标题 |
| `:og:type:` | 覆盖OG类型 |
| `:og:image:` | 设置页面图片（仅绝对URL） |
| `:og:image:alt:` | 设置图片alt文本 |
| `:description:` | 设置meta description |
| 任意 `:og:*:` | 添加任意OGP标签 |

## ReadTheDocs 环境自动检测

- 检测环境变量：`READTHEDOCS`（判断是否在RTD环境）
- 获取规范URL：`READTHEDOCS_CANONICAL_URL`
- 通过 `ambient_site_url()` 函数解析URL的scheme和netloc部分
- 自动设置 `ogp_site_url`，无需手动配置
