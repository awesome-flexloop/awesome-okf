---
type: Concept
title: 架构概览
description: sphinx-autobuild 的整体架构——ASGI 应用结构、四大核心组件协作流程、从文件变化到浏览器刷新的完整链路
tags: [sphinx-autobuild, architecture, ASGI, asyncio, Starlette]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 架构概览

## 整体架构

sphinx-autobuild 是一个基于 **ASGI（Asynchronous Server Gateway Interface）** 的异步 Web 应用，使用 Starlette 作为 Web 框架、Uvicorn 作为 ASGI 服务器。整体架构可以分为四个核心组件：

```
┌─────────────────────────────────────────────────────────────┐
│                      Uvicorn ASGI Server                     │
│                    (监听 HTTP/WebSocket)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Starlette Application                      │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ WebSocketRoute   │  │ StaticFiles  │  │ Middleware     │  │
│  │ /websocket-reload│  │ / (静态文件)  │  │ JS注入中间件   │  │
│  └────────┬─────────┘  └──────────────┘  └───────┬────────┘  │
│           │                                      │           │
│  ┌────────▼─────────────────────────────────────▼────────┐  │
│  │              RebuildServer (核心控制器)                 │  │
│  │  ┌──────────────┐  ┌───────────────┐  ┌────────────┐  │  │
│  │  │ watch()      │  │ watch_reloads()│  │ flag Event │  │  │
│  │  │ 文件监听循环  │  │ WS推送循环     │  │ 信号标志    │  │  │
│  │  └──────┬───────┘  └───────────────┘  └────────────┘  │  │
│  └─────────┼─────────────────────────────────────────────┘  │
└────────────┼────────────────────────────────────────────────┘
             │ 变化回调 (ProcessPoolExecutor)
┌────────────▼────────────────────────────────────────────────┐
│                       Builder                                │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │ pre_build 命令    │  │ subprocess: python -m sphinx ... │ │
│  │ sphinx-build 调用 │  │ post_build 命令                  │ │
│  └──────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                    IgnoreFilter                              │
│         glob 模式匹配 + 正则表达式匹配                        │
└─────────────────────────────────────────────────────────────┘
```

## 四大核心组件

### 1. Builder（构建器）

[Builder](/concepts/04-builder-system.md) 负责封装 sphinx-build 的调用逻辑。它接收变更路径列表，依次执行 pre-build 命令、sphinx-build 子进程、post-build 命令。Builder 是一个可调用对象（实现了 `__call__`），在文件变化时被 RebuildServer 调用。

关键设计：**构建在独立子进程中执行**，通过 `ProcessPoolExecutor` 提交，避免阻塞 asyncio 事件循环。

### 2. IgnoreFilter（忽略过滤器）

[IgnoreFilter](/concepts/05-file-watching.md) 决定哪些文件变化应该被忽略。它支持两种匹配模式：

- **路径前缀/glob 匹配**：对路径前缀和 fnmatch glob 模式进行匹配
- **正则表达式匹配**：对完整路径进行正则搜索

当 `SPHINX_AUTOBUILD_DEBUG` 环境变量被设置为非空非零值时，会输出调试信息帮助配置忽略规则。

### 3. RebuildServer（重建服务器）

[RebuildServer](/concepts/06-server-and-hotreload.md) 是整个系统的核心控制器，承担两个职责：

- **文件监听**：通过 `watchfiles.awatch()` 异步监听文件系统变化，过滤后触发 Builder 执行构建
- **WebSocket 服务**：处理浏览器 WebSocket 连接，构建完成后发送 `"refresh"` 消息触发页面刷新

它使用 `asyncio.Event`（`self.flag`）作为构建完成的信号标志：watch() 检测到变化并完成构建后 `flag.set()`，watch_reloads() 等待 flag 后发送消息并 `flag.clear()`。

### 4. JavascriptInjectorMiddleware（JS注入中间件）

[JavascriptInjectorMiddleware](/concepts/07-middleware-injection.md) 是一个 ASGI 中间件，拦截 HTML 响应并注入 WebSocket 热重载脚本。它不需要修改 Sphinx 的任何模板或主题文件，对 Sphinx 构建过程完全透明。

## 请求处理流程

### 静态文件请求（HTML页面访问）

```
浏览器请求 GET /index.html
    → Uvicorn 接收
    → JavascriptInjectorMiddleware 拦截
    → StaticFiles 返回 HTML 内容
    → 中间件在 </body> 前注入 <script> 标签
    → 中间件添加 Cache-Control: no-cache 头
    → 响应返回浏览器
    → 浏览器执行脚本，建立 WebSocket 连接
```

### 文件变化到页面刷新

```
1. 编辑器保存 docs/index.rst
2. watchfiles.awatch() 检测到变化事件
3. IgnoreFilter 判断是否忽略 → 不忽略
4. ProcessPoolExecutor 提交 Builder(changed_paths)
5. Builder 在子进程中：
   a. 执行 pre-build 命令（如有）
   b. 调用 subprocess.run([python, -m, sphinx, build, ...])
   c. 构建成功则执行 post-build 命令（如有）
6. 子进程完成，flag.set()
7. watch_reloads() 检测到 flag
8. 通过 WebSocket 发送 "refresh" 消息
9. 浏览器收到消息 → window.location.reload()
10. flag.clear()，等待下一次变化
```

## ASGI 路由配置

在 `_create_app()` 函数中，Starlette 应用配置了两条路由和一个中间件：

| 路由/中间件 | 类型 | 目标 |
|------------|------|------|
| `/websocket-reload` | WebSocketRoute | `RebuildServer.__call__` 处理 WebSocket 连接 |
| `/` | Mount (StaticFiles) | 托管构建输出目录的静态文件，`html=True` 启用目录索引 |
| JavascriptInjectorMiddleware | Middleware | 注入热重载脚本，传入 `ws_url` 参数 |

Lifespan 上下文管理器绑定到 `watcher.lifespan`，在应用启动时创建 `main()` 任务（运行文件监听循环），在应用关闭时设置 `should_exit` 事件并等待任务结束。

## 异步任务模型

RebuildServer 中使用了 asyncio 的任务并发模式：

**主循环（main）**：同时运行两个任务，任一完成则取消另一个：
- `self.watch()`：文件监听循环（长运行）
- `self.should_exit.wait()`：等待退出信号

**WebSocket 连接处理**：同时运行两个任务，任一完成则取消另一个：
- `self.watch_reloads(ws)`：等待构建信号并推送
- `self.wait_client_disconnect(ws)`：等待客户端断开

这种模式称为"竞赛模式"（`asyncio.wait(FIRST_COMPLETED)`），确保资源在任一终止条件满足时被正确清理。

## 版本兼容性处理

Builder 在调用 sphinx-build 时有版本分支：

```python
if sphinx.version_info[:3] >= (7, 2, 3):
    sphinx_build_args = ["-m", "sphinx", "build"] + self.sphinx_args
else:
    sphinx_build_args = ["-m", "sphinx"] + self.sphinx_args
```

Sphinx 7.2.3 将 CLI 入口从 `sphinx.cmd.build` 模块迁移到 `python -m sphinx build` 子命令格式，sphinx-autobuild 通过版本检查确保兼容性。

## 相关概念

- [CLI 入口与参数解析](/concepts/03-cli-and-entrypoint.md)
- [构建系统](/concepts/04-builder-system.md)
- [文件监听与过滤](/concepts/05-file-watching.md)
- [服务器与热重载](/concepts/06-server-and-hotreload.md)
- [中间件注入机制](/concepts/07-middleware-injection.md)
- [sphinx-autobuild 源码信源登记](/references/sphinx-autobuild-source.md)
