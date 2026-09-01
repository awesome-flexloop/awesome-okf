---
type: Pattern
title: 双重重定向规范化模式
description: 通过两次HTTP重定向将可变引用（分支名/标签）转化为不可变内容地址（commit SHA），并补全默认路径，生成CDN友好的可缓存规范URL
tags: [redirect, canonical-url, cache-friendly, content-addressing, http, cdn]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T16:30:00+08:00" }
status: stable
source: repo2jupyterlite
applicability: 按需构建服务、静态站点生成器、内容寻址Web服务、Git仓库浏览器
---

# 双重重定向规范化模式

## 问题

Web 服务接收的请求包含可变引用（如 `HEAD`、`main` 分支名），这些引用指向的内容会随时间变化。直接使用可变引用构建缓存会导致：
- 缓存无法永久命中（分支更新后旧缓存失效）
- 用户访问同一URL可能在不同时间得到不同内容
- CDN 无法有效缓存（URL与内容不是一一映射）

同时，用户可能输入不完整路径（如缺少文件路径），需要服务端补全。

## 解决方案

在服务文件前执行两次连续的HTTP重定向，将请求URL规范化为**内容寻址的永久URL**：

1. **第一次重定向（路径补全）**：当路径为空时，自动追加默认入口路径（如 `/lab/index.html`）
2. **第二次重定向（引用解析）**：将可变引用（分支/tag）解析为不可变commit SHA，重定向到SHA路径

两次重定向后的URL格式：`/v1/{provider}/{user}/{repo}/{commit-sha}/{path}`

## 核心代码

```python
@app.get("/v1/{provider_name}/{spec_and_path:path}")
async def render(provider_name, spec_and_path, request):
    provider, path = provider_class.from_spec_and_path(spec_and_path)
    
    # 第一次重定向：补全路径
    if path.strip() == "":
        url = URL(str(request.url))
        existing_query = url.query
        url = url.with_path(url.path.rstrip("/") + "/lab/index.html").with_query(existing_query)
        return RedirectResponse(url)
    
    # 第二次重定向：解析引用为SHA
    ref = await provider.get_resolved_ref()
    if ref != provider.unresolved_ref:
        url = URL(str(request.url))
        existing_query = url.query
        url = url.with_path(
            f"/v1/{provider_name}/{await provider.get_resolved_spec()}/{path}"
        ).with_query(existing_query)
        return RedirectResponse(url)
    
    # 规范化完成，继续构建/服务
    ...
```

## 关键原则

1. **query参数保留**：重定向时必须保留query参数（yarl的`with_query(existing_query)`处理），否则如`?path=notebook.ipynb`这类参数会丢失
2. **302而非301**：使用临时重定向（302），因为分支引用会变化，不应被浏览器永久缓存
3. **commit SHA作为缓存键**：SHA是内容哈希，同一SHA的内容永远不变，可被CDN永久缓存
4. **路径补全前置**：先补全路径再解析引用，避免两次重定向顺序导致的多余跳转

## 反模式

- ❌ 在可变引用URL上设置长缓存（分支更新后用户看到旧内容）
- ❌ 重定向时丢弃query参数（破坏深度链接）
- ❌ 使用301永久重定向解析分支引用（分支指向新commit后无法更新）
- ❌ 不做引用解析直接构建（每次构建可能产生不同内容，无法利用缓存）

## 适用场景

- BinderHub/mybinder.org 类按需构建服务
- Git仓库静态站点预览服务
- 基于内容哈希的CDN缓存优化
- 需要将人类可读URL映射到永久内容地址的服务
