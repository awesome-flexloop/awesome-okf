---
type: Example
title: 版本切换器与即时搜索
description: 多版本文档的 switcher.json、警告横幅、公告条与 search-as-you-type 配置
tags: [sphinx, theme, pydata, example, version-switcher, search]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:32:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 版本切换器与即时搜索

## 场景

文档有 `2.3`、`2.4`（稳定）、`latest`（开发）三个版本，部署在：

```text
https://docs.acme.example/2.3/
https://docs.acme.example/2.4/
https://docs.acme.example/latest/
```

希望顶部有版本下拉，旧版本显示警告横幅，并开启搜索即输。

## 1. switcher.json

放在一个稳定 URL，例如 `https://docs.acme.example/switcher.json`：

```json
[
  {
    "name": "stable (2.4)",
    "version": "2.4",
    "url": "https://docs.acme.example/2.4/",
    "preferred": true
  },
  {
    "name": "latest",
    "version": "2.5.dev0",
    "url": "https://docs.acme.example/latest/"
  },
  {
    "version": "2.3",
    "url": "https://docs.acme.example/2.3/"
  }
]
```

规则：

- `preferred` 最多一个，用于警告横幅判断“最新稳定版”。
- `version` 必须能被 `compare-versions` 解析（或至少与 `version_match` 精确匹配）。
- 所有版本共用同一个 JSON URL，新增版本时只改这个文件。

## 2. conf.py

```python
import os

release = "2.4.1"
version = "2.4"

# 本地开发时用相对路径；CI/线上用绝对 URL
json_url = os.environ.get(
    "SWITCHER_JSON_URL",
    "https://docs.acme.example/switcher.json",
)
version_match = os.environ.get("DOCS_VERSION", version)

html_theme_options = {
    "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
    "navbar_center": ["version-switcher", "navbar-nav"],
    "show_version_warning_banner": True,
    "sticky_banners": True,
    "check_switcher": True,
    "search_as_you_type": True,
    "search_bar_text": "搜索文档…",
}
```

## 3. 构建与部署

```console
# 稳定版
$ DOCS_VERSION=2.4 sphinx-build -b html . _build/2.4

# 开发版
$ DOCS_VERSION=2.5.dev0 sphinx-build -b html . _build/latest
```

部署后确认：

1. 顶部下拉按钮显示当前版本名（`stable (2.4)` 或 `latest`）。
2. 在 `2.3` 页面看到“an old version (2.3)”横幅与“Switch to stable version”。
3. 在 `latest` 页面看到“an unstable development version”。
4. 点击切换器条目时，若目标页不存在会落到目标版首页。

## 4. 本地预览的坑

直接双击 `_build/2.4/index.html`（`file://`）时：

- 浏览器禁止 fetch 本地 JSON，切换器为空。
- 警告横幅也不会出现。

用 HTTP 服务器：

```console
$ python -m http.server -d _build/2.4 8000
```

并把 `json_url` 临时指向本地可访问的 JSON（或设 `check_switcher=False` 跳过构建期校验）。

## 5. 公告条

远程公告文件 `https://docs.acme.example/announcement.html`：

```html
<strong>2.4 已发布！</strong>
<a href="https://docs.acme.example/2.4/changelog.html">查看变更</a>
```

```python
html_theme_options = {
    "announcement": "https://docs.acme.example/announcement.html",
}
```

- 修改该文件即可让所有版本文档同步更新，无需重建。
- 把文件清空即可移除公告。
- 用户关闭后 14 天内不再显示。

## 6. 搜索即输的行为

开启后：

1. 点击搜索按钮或按 `Ctrl/Cmd+K` 打开弹窗。
2. 输入关键词，停止输入 300 ms 后触发搜索。
3. 结果出现在输入框下方；`Escape` 关闭并清空。
4. 在 `/search` 页面，该功能自动关闭，使用 Sphinx 原生搜索页。

若站点使用第三方搜索（如 Read the Docs 服务端搜索），应禁用内置搜索：

```python
html_theme_options = {"disable_search": True}
```

## 7. 验收清单

- [ ] 三个版本的切换器都能互相跳转。
- [ ] 旧版本显示警告横幅，稳定版不显示。
- [ ] 开发版显示“unstable development version”。
- [ ] 公告条可通过改远程文件更新/移除。
- [ ] 搜索即输有 300 ms 防抖，结果链接不 404。
- [ ] `Escape` 能关闭搜索弹窗。
- [ ] `file://` 预览的限制已记录在团队文档中。

## 相关概念

- [搜索、版本切换与公告](../concepts/08-search-versioning-and-announcements.md)
- [主题配置项](../concepts/06-theme-options.md)
- [可访问性、性能与 FAQ](../concepts/10-accessibility-performance-faq.md)
