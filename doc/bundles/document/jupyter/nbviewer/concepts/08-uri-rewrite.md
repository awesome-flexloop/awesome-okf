---
type: Concept
title: URI重写机制
description: transform_ipynb_uri正则替换管道、默认重写顺序、各Provider重写规则和扩展方式
tags:
  - jupyter
  - nbviewer
  - uri
  - rewrite
  - regex
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/utils.py
---

# URI重写机制

URI重写将用户输入的外部URL转换为nbviewer内部路由路径，在CreateHandler表单提交时执行。

## transform_ipynb_uri() 函数

```python
def transform_ipynb_uri(uri, uri_rewrite_list):
    for reg, rewrite in uri_rewrite_list:
        matches = re.match(reg, uri)
        if matches:
            uri = rewrite.format(*matches.groups())
            break
    if "?" in uri:
        uri, query = uri.split("?", 1)
        uri = "%s/%s" % (uri, quote("?" + query))
    return uri
```

- 按顺序遍历(regex, template)规则，首次匹配生效
- 使用`re.match()`从字符串开头匹配
- 捕获组通过`str.format(*groups)`填入模板
- 查询参数编码为路径段（因为nbviewer路由不使用查询参数传递路径信息）

## 默认重写顺序

```python
default_rewrites = ["gist", "github", "dropbox", "huggingface", "url"]
```

规则顺序至关重要：更具体的规则排在前面。

## 各Provider重写规则

### Gist
- 纯十六进制ID：`^([a-f0-9]+)/?$` → `/{id}`（由GistRedirectHandler重定向到/gist/{id}）
- gist.github.com URL → `/{id}`

### GitHub（规则最多）
- raw.github.com/user/repo/... → /github/user/repo/blob/...
- raw.githubusercontent.com/user/repo/... → /github/user/repo/blob/...
- github.com/.../raw/... → blob路由
- github.com/.../blob|tree/... → 对应路由
- user/repo简写 → /github/user/repo/tree/master/
- user简写 → /github/user/

### Dropbox
- `www.dropbox.com/(sh?)/...` → `/url{s}/dl.dropbox.com/{sh}/...`（替换为直链域名）

### HuggingFace
- `huggingface.co/.../blob/...` → `/urls/huggingface.co/.../resolve/...`（blob→resolve下载路径）

### URL（兜底）
- `http(s?)://(.*)$` → `/url{s}/{path}`
- `^(.*)$` → `/url/{path}`（无协议URL，最后兜底）

## 查询参数编码

URL中的`?param=value`被编码为路径段`/%3Fparam%3Dvalue`，确保缓存键正确区分带参数的URL。

## 扩展方式

创建轻量Provider模块，实现`uri_rewrites()`函数，在`--provider-rewrites`中注册。Dropbox和HuggingFace是典型例子——仅需一个重写函数将外部URL桥接到URLHandler。

## 相关文档

- [Provider插件系统](/concepts/05-provider-plugin-system.md)
- [自定义Provider扩展](/concepts/12-custom-provider.md)
