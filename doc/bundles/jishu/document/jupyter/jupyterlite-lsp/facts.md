---
type: Facts
okf_version: '0.2'
title: jupyterlite-lsp 源码事实清单
generated: '2026-08-22'
tags:
- jupyter
- jupyterlite
- lsp
- language-server
sources:
- ../../../../../external/libs/jupyter/jupyterlite-lsp/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlite-lsp/package.json
- ../../../../../external/libs/jupyter/jupyterlite-lsp/src/jupyterlite_lsp/constants.py
- ../../../../../external/libs/jupyter/jupyterlite-lsp/src/jupyterlite_lsp/__init__.py
- ../../../../../external/libs/jupyter/jupyterlite-lsp/src/jupyterlite_lsp/js.py
- ../../../../../external/libs/jupyter/jupyterlite-lsp/dodo.py
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/package.json
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/plugin.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/tokens.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/servers.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/session.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/hacks.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/package.json
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/plugin.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/tokens.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/server.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp-yaml/src/worker.ts
- ../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/src/index.ts
---

# jupyterlite-lsp 源码事实清单

## 项目结构与元数据

- F-001: pyproject.toml:6-7 — 项目名为 `jupyterlite-lsp`，版本为 `0.1.0a0`（alpha 阶段）
- F-002: pyproject.toml:8 — 描述为 "Multiplexing Language Server Protocol server for JupyterLite"
- F-003: pyproject.toml:23 — requires-python 为 `>=3.7`
- F-004: pyproject.toml:24-27 — 核心依赖为 `jupyterlab-lsp >=3.10.2` 和 `jupyterlite >=0.1.0b15`
- F-005: pyproject.toml:2 — 构建系统使用 flit_core（`flit_core >=3.7.1,<4`），build-backend 为 `flit_core.buildapi`
- F-006: pyproject.toml:36 — sdist 打包包含 `src/jupyterlite_lsp/_d` 目录（labextension 静态资源）
- F-007: pyproject.toml:41-42 — flit external-data 目录为 `src/jupyterlite_lsp/_d`，用于存放前端构建产物
- F-008: package.json:2 — 根 package.json 标记为 `private: true`，不发布 npm
- F-009: package.json:21-25 — 使用 yarn workspaces，workspace 为 `packages/*`
- F-010: package.json:4 — build 脚本使用 lerna 管理多包构建（`lerna run labextension:build`）
- F-011: package.json:14 — lite:build 命令执行 `jupyter lite build` 并生成 SHA256SUMS 校验
- F-012: package.json:26-36 — devDependencies 包含 lerna ^6.0.3、prettier ^2.8.0、typescript ~4.9.3、yarn-deduplicate ^6.0.0

## Python 包结构

- F-013: src/jupyterlite_lsp/constants.py:9 — Python 模块名为 `jupyterlite_lsp`，NAME 常量为 "jupyterlite-lsp"
- F-014: src/jupyterlite_lsp/constants.py:13 — JS_NAMESPACE 常量为 `@jupyterlite`
- F-015: src/jupyterlite_lsp/constants.py:15-18 — EXTENSION_NAMES 列表包含两个扩展：`"lsp"` 和 `"lsp-yaml"`
- F-016: src/jupyterlite_lsp/__init__.py:8-13 — _jupyter_labextension_paths 返回两个 labextension 路径，映射到 `@jupyterlite/lsp` 和 `@jupyterlite/lsp-yaml`
- F-017: src/jupyterlite_lsp/js.py:11-14 — 静态资源路径查找逻辑：优先使用 in-tree 路径（`_d/share/jupyter/labextensions/@jupyterlite`），不存在则使用 sys.prefix 路径

## doit 构建系统

- F-018: dodo.py:23-28 — 定义了 C（Constants）类，包含 NATIVE_WEBSOCKET = "new WebSocket" 和 HACKED_WEBSOCKET = "new window.MockWebSocket" 两个关键常量
- F-019: dodo.py:57-63 — B（Build）类定义了构建输出路径，JLLSP 指向 `build/lite/extensions/@krassowski/jupyterlab-lsp/static`
- F-020: dodo.py:63 — CONNECTION_JS 指向 jupyterlab-lsp 构建产物中的 `321.0176abf53bb1a24b854d.js` 文件
- F-021: dodo.py:266-279 — task_hack:connection.js 任务的核心操作：将 CONNECTION_JS 中的 `new WebSocket` 替换为 `new window.MockWebSocket`，实现 WebSocket 拦截
- F-022: dodo.py:213-216 — patch_one 函数执行简单的字符串替换（pattern → replacement），用于 WebSocket hack
- F-023: dodo.py:44-45 — doit backend 使用 sqlite3，verbosity 设为 2
- F-024: package.json:37-213 — package.json 内嵌 doit 任务配置，定义了 lite:build、docs:sphinx、dist:npm、dist:py、setup:py:pip、setup:py:ext、build:lib、build:ext 等任务的 file_dep 和 targets

## 前端包：@jupyterlite/lsp（核心 LSP 多路复用）

- F-025: packages/lsp/package.json:2 — npm 包名为 `@jupyterlite/lsp`，版本 `0.1.0-alpha0`
- F-026: packages/lsp/package.json:26-28 — 运行时依赖为 `@jupyterlite/server ^0.1.0-beta.15` 和 `@krassowski/jupyterlab-lsp ^3.10.2`
- F-027: packages/lsp/package.json:42 — JupyterLab extension 入口为 `lib/plugin.js`
- F-028: packages/lsp/package.json:43 — 构建输出目录为 `../../src/jupyterlite_lsp/_d/share/jupyter/labextensions/@jupyterlite/lsp`
- F-029: packages/lsp/package.json:45-50 — sharedPackages 配置：`@krassowski/jupyterlab-lsp` 设为 bundled: false, singleton: true（不打包，使用宿主单例）
- F-030: packages/lsp/package.json:52-54 — jupyterlite 配置标记 `liteExtension: true`，表示这是 JupyterLite 服务端插件
- F-031: packages/lsp/src/plugin.ts:18-25 — hacksPlugin：id 为 `@jupyterlite/lsp:hacks`，provides ILSPHacks，autoStart，activate 时调用 applyHacks(app)
- F-032: packages/lsp/src/plugin.ts:27-35 — serverPlugin：id 为 `@jupyterlite/lsp:plugin`，provides ILanguageServers，autoStart，activate 时创建 LanguageServers 实例
- F-033: packages/lsp/src/plugin.ts:37-48 — routesPlugin：id 为 `@jupyterlite/lsp:routes`，autoStart，requires ILanguageServers，注册 GET `/lsp/status` 路由返回 LSP 服务器状态 JSON
- F-034: packages/lsp/src/tokens.ts:16 — ILanguageServers Token 标识符为 `@jupyterlite/lsp:ILSPServer`
- F-035: packages/lsp/src/tokens.ts:23 — ILSPHacks Token 标识符为 `@jupyterlite/lsp:ILSPHacks`
- F-036: packages/lsp/src/tokens.ts:29-36 — IAddServerOptions 接口包含 spec（LanguageServerSpec）和 createNewServer（IServerFactory 工厂函数）
- F-037: packages/lsp/src/tokens.ts:38-42 — IJSONRPCLanguageServer 接口定义三个方法：initialize()、write(msg)、read()（AsyncGenerator）
- F-038: packages/lsp/src/tokens.ts:44 — DEBUG 常量通过 URL 包含 `LSP_LITE_DEBUG` 参数启用调试模式
- F-039: packages/lsp/src/tokens.ts:46 — WS_BASE_URL 通过 PageConfig.getBaseUrl() 转换为 WebSocket URL（http → ws 替换）

## LanguageServers 管理器

- F-040: packages/lsp/src/servers.ts:6-28 — LanguageServers 类维护两个 Map：_specs（id → LanguageServerSpec）和 _sessions（id → Session）
- F-041: packages/lsp/src/servers.ts:10-13 — addLanguageServer 方法注册 spec 并创建对应的 Session 实例
- F-042: packages/lsp/src/servers.ts:15-28 — status() 方法返回 ServersResponse（version: 2），包含所有 sessions 的 JSON 状态和 specs 映射

## Session：WebSocket → Web Worker 桥接

- F-043: packages/lsp/src/session.ts:2 — 使用 mock-socket 库的 WebSocketClient 和 WebSocketServer 在浏览器内创建虚拟 WebSocket 服务
- F-044: packages/lsp/src/session.ts:11-70 — Session 类管理单个 LSP 服务器的生命周期，桥接 WebSocket 客户端和实际语言服务器
- F-045: packages/lsp/src/session.ts:24-26 — WebSocket URL 为 `${WS_BASE_URL}lsp/ws/${id}` 格式
- F-046: packages/lsp/src/session.ts:28-43 — initServer 方法创建 WebSocketServer（mock-socket），在 connection 事件中创建语言服务器实例、初始化、绑定消息处理、启动 read 循环
- F-047: packages/lsp/src/session.ts:45-49 — read 方法使用 for-await-of 循环从语言服务器的 AsyncGenerator 读取消息，通过 socket.send 转发给 WebSocket 客户端
- F-048: packages/lsp/src/session.ts:51-55 — onMessage 方法将 WebSocket 客户端消息通过 langServer.write 转发给语言服务器
- F-049: packages/lsp/src/session.ts:61-69 — toJSON 返回 LanguageServerSession，初始 status 为 'not_started'，handler_count 初始为 0

## WebSocket Hack 机制

- F-050: packages/lsp/src/hacks.ts:9-22 — hackServerConnection 函数：替换 ServerConnection.makeSettings，将 fetch 绑定到 JupyterLiteServer 的 app.fetch，使 HTTP 请求走服务端路由
- F-051: packages/lsp/src/hacks.ts:24-26 — hoistMockSocket 函数：将 mock-socket 的 WebSocket 挂载到 window.MockWebSocket
- F-052: packages/lsp/src/hacks.ts:28-32 — applyHacks 函数依次执行 hackServerConnection 和 hoistMockSocket，返回 `{ hacked: true }`
- F-053: dodo.py:275-277 — 构建时 patch jupyterlab-lsp 的 connection.js：将 `new WebSocket(...)` 替换为 `new window.MockWebSocket(...)`，使 jupyterlab-lsp 前端连接到浏览器内的 mock WebSocket 服务器而非真实网络

## 前端包：@jupyterlite/lsp-yaml（YAML/JSON 语言服务器）

- F-054: packages/lsp-yaml/package.json:2 — npm 包名为 `@jupyterlite/lsp-yaml`，版本 `0.1.0-alpha0`
- F-055: packages/lsp-yaml/package.json:3 — 描述为 "json-language-server for JupyterLite"（实际同时支持 YAML 和 JSON）
- F-056: packages/lsp-yaml/package.json:25-31 — 运行时依赖：`@jupyterlite/lsp ^0.1.0a0`、`@jupyterlite/server ^0.1.0-beta.15`、`jsonc-parser ^3.2.0`、`wait-queue ^1.1.4`、`yaml-language-server ^1.10.0`
- F-057: packages/lsp-yaml/package.json:47 — 构建输出目录为 `../../src/jupyterlite_lsp/_d/share/jupyter/labextensions/@jupyterlite/lsp-yaml`
- F-058: packages/lsp-yaml/src/plugin.ts:6-20 — 插件 id 为 `@jupyterlite/lsp-yaml:plugin`，autoStart，requires ILanguageServers，activate 时注册 id 为 'json' 的语言服务器
- F-059: packages/lsp-yaml/src/plugin.ts:14-17 — 语言服务器工厂使用动态 import（`await import('./server')`）加载 JSONLanguageServer，实现代码分割
- F-060: packages/lsp-yaml/src/tokens.ts:10-15 — SPEC 定义语言服务器规格：display_name: 'YAML'，languages: ['yaml', 'json']，mime_types: ['text/x-yaml', 'text/yaml', 'application/json']，version: 2

## JSONLanguageServer：Worker 桥接实现

- F-061: packages/lsp-yaml/src/server.ts:5-36 — JSONLanguageServer 实现 IJSONRPCLanguageServer 接口，通过 Web Worker 运行 yaml-language-server
- F-062: packages/lsp-yaml/src/server.ts:10-16 — initialize 方法动态导入 wait-queue，创建 WaitQueue 实例，通过 `new Worker(new URL('yaml-language-server/lib/esm/webworker/yamlServerMain', import.meta.url))` 创建 Web Worker
- F-063: packages/lsp-yaml/src/server.ts:19-22 — onWorkerMessage 将 Worker 消息放入 WaitQueue（unshift）
- F-064: packages/lsp-yaml/src/server.ts:24-31 — read 方法使用 while 循环 + WaitQueue.pop() 实现 AsyncGenerator，持续从队列取出消息 yield
- F-065: packages/lsp-yaml/src/server.ts:33-36 — write 方法通过 worker.postMessage 向 Worker 发送消息
- F-066: packages/lsp-yaml/src/worker.ts:1 — Worker 入口仅一行：`import 'yaml-language-server/lib/esm/webworker/yamlServerMain'`，在 Worker 上下文中启动 YAML 语言服务器

## 整体通信架构

- F-067: packages/lsp/src/session.ts + packages/lsp/src/hacks.ts + dodo.py — 形成三层桥接：①构建时 patch jupyterlab-lsp 的 WebSocket 构造函数为 window.MockWebSocket；②运行时 hacks 挂载 mock-socket 的 WebSocket 到 window.MockWebSocket；③Session 创建 mock WebSocketServer 监听 lsp/ws/{id} 路径
- F-068: packages/lsp/src/hacks.ts:15 — ServerConnection.makeSettings 被 hack 后 fetch 使用 app.fetch，使 jupyterlab-lsp 的 HTTP 状态请求（/lsp/status）走 JupyterLite 服务端路由
