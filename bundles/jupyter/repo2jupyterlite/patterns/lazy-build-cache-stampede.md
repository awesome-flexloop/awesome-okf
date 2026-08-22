---
type: Pattern
title: 懒构建触发与缓存雪崩防护模式
description: 仅在HTML页面请求时触发昂贵的构建操作，静态资源请求返回404，防止单个HTML页面引用的数十个JS/CSS资源导致请求风暴
tags: [lazy-build, cache-stampede, thundering-herd, html-only-trigger, async-subprocess]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T16:30:00+08:00" }
status: stable
source: repo2jupyterlite
applicability: 按需构建服务、静态站点生成器、SSG预览服务、CI触发的Web服务
---

# 懒构建触发与缓存雪崩防护模式

## 问题

按需构建服务（如BinderLite）在首次访问时需要执行昂贵的构建操作（JupyterLite构建可能耗时数十秒到数分钟）。当构建完成后，HTML页面中引用了大量静态资源（JS、CSS、WASM、图片、字体等）。如果构建缓存被驱逐（磁盘清理、部署重启等）：

1. 浏览器请求HTML页面 → 触发构建 → 构建中...
2. HTML返回后，浏览器立即并发请求数十个JS/CSS/WASM文件
3. 如果所有这些请求都触发新的构建，会导致"请求风暴"（缓存雪崩/thundering herd）
4. 多个并发构建争抢资源，可能导致服务崩溃

## 解决方案

**仅HTML文件请求触发构建**，非HTML文件请求在构建未完成时直接返回404：

```python
if not (await publisher.exists(slug)):
    if path.endswith(".html"):
        # 只有HTML请求触发构建
        cmd = ["repo2jupyterlite", provider.get_resolved_repo(), "--ref", ref, str(d)]
        proc = await asyncio.create_subprocess_exec(*cmd)
        retcode = await proc.wait()
        if retcode != 0:
            raise HTTPException(status_code=500, detail="Build failed")
        await publisher.upload(d, slug)
    else:
        # 非HTML请求（JS/CSS/图片等）直接404
        return Response(status_code=404)

return await publisher.serve_object(slug, path, request.headers)
```

## 工作流程

```
首次访问 /v1/gh/user/repo/SHA/lab/index.html:
  → HTML请求 → 触发构建（阻塞等待）→ 返回HTML
  → 浏览器解析HTML，请求 /lab.js /lab.css /kernel.js /pyodide/...
  → 这些非HTML请求 → 构建已完成（因为HTML请求已完成构建）→ 正常服务

缓存被驱逐后的恢复：
  → HTML请求 → 检测到不存在 → 触发重新构建 → 返回HTML
  → JS/CSS等请求 → 构建未完成或正在进行 → 返回404
  → 浏览器收到HTML后JS/CSS 404 → 用户刷新或浏览器自动重试
  → 重试时构建已完成 → 所有资源正常加载
```

## 关键原则

1. **HTML是入口**：用户始终从HTML页面开始访问，HTML请求是唯一可靠的"首次访问"信号
2. **浏览器重试机制**：现代浏览器对404资源不会无限重试，但刷新页面可以恢复——这是可接受的降级行为
3. **异步子进程**：使用`asyncio.create_subprocess_exec`执行构建，不阻塞事件循环，允许处理其他请求
4. **幂等构建**：`get_target_dir`在构建前清理输出目录（`shutil.rmtree`），确保重新构建是干净的
5. **构建失败返回500**：不是404或其他错误码，明确告知是服务端问题

## 为何有效

一个典型的JupyterLite页面引用50+静态资源。如果每个都触发构建，系统需要同时处理50+个构建进程。通过只让HTML触发构建：
- 并发构建数从N个降为1个
- 资源请求快速返回404（不占用构建资源）
- HTML构建完成后，资源请求自然命中缓存

## 反模式

- ❌ 所有请求都触发构建（缓存雪崩）
- ❌ 构建期间排队所有请求（可能导致连接耗尽）
- ❌ 同步执行构建（阻塞事件循环，无法处理健康检查等请求）
- ❌ 构建失败返回200或重定向（用户无法区分构建中和构建失败）

## 适用场景

- 按需静态站点构建服务（BinderLite、Vercel预览、Netlify Deploy Preview）
- JupyterLite/Thebe等浏览器端计算环境
- 任何首次访问触发构建的Web服务
- 高并发场景下的缓存恢复策略
