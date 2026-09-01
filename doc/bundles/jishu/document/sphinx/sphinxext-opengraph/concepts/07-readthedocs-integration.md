---
type: Concept
title: ReadTheDocs 自动检测与集成
description: 详解ReadTheDocs环境下URL自动检测机制、canonical URL配置、版本化文档的最佳实践
tags: [sphinxext-opengraph, readthedocs, RTD, ambient-site-url, canonical-url, environment-variables]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# ReadTheDocs 自动检测与集成

sphinxext-opengraph 对 [Read the Docs（RTD）](https://readthedocs.org/)托管平台有特殊的零配置支持。当检测到文档在RTD环境中构建时，扩展可以自动推断站点URL，无需手动设置 `ogp_site_url`。

## 自动URL检测机制

### ambient_site_url() 函数

```python
def ambient_site_url() -> str:
    if rtd_canonical_url := os.getenv('READTHEDOCS_CANONICAL_URL'):
        parse_result = urlsplit(rtd_canonical_url)
    else:
        msg = 'ReadTheDocs did not provide a valid canonical URL!'
        raise RuntimeError(msg)
    return urlunsplit(
        (parse_result.scheme, parse_result.netloc, parse_result.path, '', '')
    )
```

函数逻辑：
1. 读取 `READTHEDOCS_CANONICAL_URL` 环境变量（由RTD Addons注入）
2. 使用 `urlsplit()` 解析URL
3. 从canonical URL中提取 scheme（https）和 netloc（域名+端口）以及path部分
4. 使用 `urlunsplit()` 重建根URL（去掉query和fragment）

### 触发条件

自动检测在 `get_tags()` 中被触发：

```python
if not config.ogp_site_url and os.getenv('READTHEDOCS'):
    ogp_site_url = ambient_site_url()
else:
    ogp_site_url = config.ogp_site_url
```

触发条件（同时满足）：
1. `ogp_site_url` 配置为空字符串（默认值）
2. `READTHEDOCS` 环境变量存在（RTD构建环境中自动设置）

如果两个条件都满足，调用 `ambient_site_url()` 获取URL。如果 `READTHEDOCS_CANONICAL_URL` 环境变量不存在，会抛出 `RuntimeError`。

## RTD环境变量

ReadTheDocs在构建过程中会设置以下相关环境变量：

| 环境变量 | 说明 | 扩展是否使用 |
|---------|------|------------|
| `READTHEDOCS` | 标记在RTD环境中构建（值通常为"True"） | ✅ 用于检测RTD环境 |
| `READTHEDOCS_CANONICAL_URL` | 当前版本的canonical URL（如 `https://proj.readthedocs.io/en/latest/`） | ✅ 用于解析站点根URL |
| `READTHEDOCS_VERSION` | 当前版本名（如 `latest`、`stable`、`v1.0`） | ❌ 未直接使用 |
| `READTHEDOCS_PROJECT` | 项目slug | ❌ 未直接使用 |
| `READTHEDOCS_LANGUAGE` | 语言代码（如 `en`） | ❌ 未直接使用 |

## Canonical URL 与版本化文档

### ogp_canonical_url 的作用

对于版本化文档，你可能希望社交分享链接指向"稳定版"而非用户当前浏览的版本。这正是 `ogp_canonical_url` 配置的用途：

```python
# RTD上构建，但希望分享时指向stable版本
ogp_site_url = "https://myproj.readthedocs.io/en/latest/"  # 自动检测也可以
ogp_canonical_url = "https://myproj.readthedocs.io/en/stable/"
```

设置后：
- `og:url` 标签指向 canonical URL（stable版）
- 社交卡片中显示的URL文本也使用 canonical URL
- 图片URL仍基于 `ogp_site_url` 解析（确保图片可访问）

源码中的URL拼接逻辑：

```python
ogp_canonical_url = config.ogp_canonical_url or ogp_site_url
page_url = urljoin(ogp_canonical_url, builder.get_target_uri(context['pagename']))
tags['og:url'] = page_url
```

注意 `social_card_for_page()` 中也分别使用了 `ogp_site_url` 和 `ogp_canonical_url`：

```python
url_text = ogp_canonical_url.split('://')[-1]  # 卡片显示的URL文本
# ...
return posixpath.join(ogp_site_url, image_path.as_posix())  # 图片实际链接
```

这确保了：
- 卡片上显示stable URL（用户看到的是"官方"地址）
- 图片链接指向实际构建版本的URL（图片确实存在）

### RTD Addons

RTD的新版Addons系统会自动设置 `READTHEDOCS_CANONICAL_URL`。旧版RTD可能需要在项目设置中启用Addons，或者手动设置环境变量。

如果RTD Addons不可用，你可以手动设置环境变量或直接配置 `ogp_site_url`：

```python
# 不依赖自动检测的显式配置
ogp_site_url = "https://myproj.readthedocs.io/en/latest/"
```

## RTD上的零配置体验

在ReadTheDocs上，最简单的配置就是什么都不配置：

```python
# conf.py
extensions = ['sphinxext.opengraph']
# 不需要设置 ogp_site_url！
```

RTD构建过程中：
1. 检测到 `READTHEDOCS` 环境变量
2. 从 `READTHEDOCS_CANONICAL_URL` 自动获取URL
3. 自动生成所有OGP标签
4. 如果安装了matplotlib（RTD默认不安装），还会生成社交卡片

## 在RTD上启用社交卡片

RTD默认不会安装matplotlib，因此社交卡片功能默认不启用。要在RTD上启用社交卡片，需要在项目的依赖中添加matplotlib：

### 方法1：通过 requirements.txt

创建 `.readthedocs.requirements.txt`（或在现有requirements文件中添加）：

```txt
sphinxext-opengraph[social_cards]
matplotlib
```

然后在 `.readthedocs.yaml` 中指定：

```yaml
version: 2
sphinx:
  configuration: docs/conf.py
python:
  install:
    - requirements: docs/requirements.txt
```

### 方法2：通过 pip 安装选项

在 `.readthedocs.yaml` 中：

```yaml
version: 2
python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs
```

在 `pyproject.toml` 的 `optional-dependencies` 中包含社交卡片依赖。

## 本地开发与RTD的差异

本地开发时没有RTD环境变量，需要显式设置 `ogp_site_url`：

```python
# conf.py
import os

extensions = ['sphinxext.opengraph']

# 本地构建时使用本地URL，RTD上自动检测
if not os.getenv('READTHEDOCS'):
    ogp_site_url = "http://localhost:8000/"
    # 本地构建通常不需要社交卡片（或设置enable=False）
    ogp_social_cards = {"enable": False}
```

更优雅的方式是利用RTD的canonical URL总是公网可访问的特性，在本地也使用RTD URL：

```python
ogp_site_url = "https://myproj.readthedocs.io/en/latest/"
```

这样本地构建生成的页面OG标签指向线上URL，分享时仍然有效。

## 常见问题

### RuntimeError: ReadTheDocs did not provide a valid canonical URL!

这个错误在以下情况出现：
- `READTHEDOCS` 环境变量存在（认为在RTD环境中）
- 但 `READTHEDOCS_CANONICAL_URL` 环境变量不存在

**解决方案**：
1. 启用RTD Addons（在RTD项目设置 → Admin → Addons）
2. 或显式设置 `ogp_site_url` 绕过自动检测
3. 或在构建环境中手动设置 `READTHEDOCS_CANONICAL_URL`

### 社交卡片图片404

在版本化文档中，如果 `ogp_canonical_url` 指向stable而当前构建的是latest版本，图片URL可能指向stable路径上不存在的图片。这是因为社交卡片图片路径中包含页面名和内容哈希，不同版本的哈希值不同。

**解决方案**：确保社交卡片链接使用 `ogp_site_url`（当前版本URL）而非 `ogp_canonical_url`。源码中 `social_card_for_page()` 返回的URL已经使用了 `ogp_site_url`，正常情况下不会出现这个问题。

## 相关概念

- [配置选项全解](02-configuration.md)
- [核心标签生成流程](03-tag-generation.md)
- [社交卡片生成](08-social-cards.md)
- [基础配置示例](../examples/basic-setup.md)
- [sphinxext-opengraph 源码信源登记](../references/sphinxext-opengraph-source.md)
