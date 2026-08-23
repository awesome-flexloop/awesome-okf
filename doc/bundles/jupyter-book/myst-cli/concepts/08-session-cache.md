---
type: concept
title: "会话与缓存"
description: "myst-cli的Session依赖注入容器、内存缓存与磁盘缓存双层缓存策略"
tags: [myst-cli, session, cache, dependency-injection, performance]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/session.ts"
    facts: [F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/cache.ts"
    facts: [F-026, F-027, F-028]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-cli/src/session/types.ts"
    facts: [F-029]
---

# 会话与缓存

Session 是 myst-cli 的核心运行时容器，实现了依赖注入、资源管理和双层缓存。

## Session 作为依赖注入容器

Session 聚合了构建过程中需要的全部依赖：

| 依赖 | 类型 | 用途 |
|------|------|------|
| `store` | Redux Store | 全局状态管理 |
| `log` | Logger | 彩色终端日志输出 |
| `doiLimiter` | p-limit Limit | DOI 请求并发控制（最多3个） |
| `executionSemaphore` | Semaphore | Notebook 执行并行控制（默认 cpus-1） |
| `proxyAgent` | HttpsProxyAgent | HTTPS 代理支持 |
| `plugins` | ValidatedMystPlugin | 已加载的用户插件 |
| `fetch()` | Function | 带代理和超时提示的 HTTP 客户端 |

所有处理函数（build、process、transforms）通过 `ISession` 参数访问这些能力，不依赖模块级全局变量。

## Session 路径体系

Session 提供统一的路径解析方法，所有构建路径都基于 sourcePath()：

```
sourcePath()  →  /my-project/             （项目根目录）
  └─ buildPath()  →  _build/
      ├─ sitePath()  →  _build/site/
      │   ├─ contentPath()  →  _build/site/content/
      │   └─ publicPath()   →  _build/site/public/
      ├─ exports/   →  _build/exports/
      ├─ temp/      →  _build/temp/
      ├─ cache/     →  _build/cache/
      ├─ logs/      →  _build/logs/
      ├─ templates/ →  _build/templates/
      ├─ html/      →  _build/html/
      └─ execute/   →  _build/execute/
```

## Clone 会话机制

`clone()` 创建共享资源但独立状态的子会话：

- **共享**：logger、doiLimiter、executionSemaphore、Jupyter SessionManager
- **独立**：Redux Store（各自独立状态）、配置文件列表
- **追踪**：父会话通过 `_clones` 数组追踪所有克隆
- **批量警告**：`getAllWarnings()` 聚合父会话和所有克隆会话的警告

Clone 机制用于多项目并行构建场景——每个项目有独立状态但不重复创建昂贵资源。

## 双层缓存策略

### 第一层：内存缓存（ISessionWithCache）

通过 `castSession(session)` 动态挂载到 Session 对象上，用于**同一会话内**的去重：

| 缓存属性 | 类型 | 键 | 缓存内容 |
|----------|------|-----|----------|
| `$citationRenderers` | Record | 文件路径 | Citation.js 渲染器实例 |
| `$doiRenderers` | Record | DOI 字符串 | 单个 DOI 的渲染数据 |
| `$externalReferences` | Record | 引用 ID | 解析后的外部引用 |
| `$mdast` | Record | 绝对路径 | 解析后的 MDAST 树（pre/post 转换） |
| `$outputs` | MinifiedContentCache | - | Notebook 输出缓存 |
| `$siteTemplate` | MystTemplate | - | 站点模板实例 |

$mdast 缓存同时存储 sha256 哈希，用于检测文件是否变化：
- `pre`：转换前的 MDAST（解析后、transforms 之前）
- `post`：转换后的 MDAST（transforms 之后，可选）

使用 `$getMdast(path)` 和 `$setMdast(path, data)` 访问，自动处理路径标准化。

### 第二层：磁盘缓存（_build/cache/）

通过三个函数操作：

```ts
// 写入缓存
writeToCache(session, 'filename.json', JSON.stringify(data));

// 检查缓存是否存在且未过期
checkCache(session, 'filename.json', { maxAge: 7 });  // 7天过期

// 读取缓存
const data = loadFromCache(session, 'filename.json', { maxAge: 7 });
```

磁盘缓存适合存储跨构建会话的数据：
- HTTP 响应缓存（DOI 元数据、Crossref 数据等）
- 模板下载缓存
- 大型计算结果

过期策略基于文件 ctime，`maxAge` 单位为天。

## Jupyter 会话管理

`jupyterSessionManager()` 使用懒加载单例模式：
- 首次调用时创建，后续复用同一实例
- 优先连接已有服务器（`JUPYTER_BASE_URL`/`JUPYTER_TOKEN` 环境变量）
- 否则自动启动本地 Jupyter 服务器
- SessionManager 与 KernelManager 生命周期绑定
- dispose 时自动清理

## 版本升级提示

Session 构造时异步检查 npm 最新版本（不阻塞），首次输出日志时通过 `showUpgradeNotice()` 显示升级提示。使用 boxen 库绘制美观的提示框，显示当前版本、最新版本和升级命令。

## 生命周期

```
new Session()          → 初始化依赖、创建 Store、异步检查版本
  ├─ reload()          → 加载项目和站点配置
  ├─ clone()           → 创建子会话（如需要）
  ├─ build/start/...   → 执行业务逻辑（使用缓存加速）
  └─ dispose()         → 清理克隆、关闭 Jupyter 连接
```

## 相关概念

- [CLI 架构](00-cli-architecture.md) — Session 在 CLI 命令中的创建
- [Build 管线](01-build-pipeline.md) — 构建过程中缓存的使用
- [Store 状态管理](09-store-state.md) — Redux Store 结构
