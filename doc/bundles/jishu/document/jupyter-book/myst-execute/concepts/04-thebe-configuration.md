---
type: concept
title: "Thebe 配置选项"
description: "详解 thebe-core 的 CoreOptions 配置体系：BinderOptions、KernelOptions、ServerSettings、SavedSessionOptions、MathjaxOptions 各选项的含义和默认值"
tags: [thebe, configuration, options, binder, kernel, server]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/thebe-core-src.md"
    facts: [F-045, F-046, F-047, F-048, F-049, F-050, F-064, F-065, F-066, F-067]
---

# Thebe 配置选项

thebe-core 通过 `CoreOptions` 接口组织所有配置，分为五个子配置组：MathJax、Binder、Saved Sessions、Kernel、Server Settings。`makeConfiguration()` 工厂函数会为所有未提供的选项填充合理默认值。

## CoreOptions 总览

```ts
interface CoreOptions {
  mathjaxUrl?: string;
  mathjaxConfig?: string;
  binderOptions?: BinderOptions;
  savedSessionOptions?: SavedSessionOptions;
  kernelOptions?: KernelOptions;
  serverSettings?: ServerSettings;
}
```

通过 `makeConfiguration(options, events?)` 创建 Config 对象：

```ts
import { makeConfiguration } from 'thebe-core';

const config = makeConfiguration({
  binderOptions: { repo: 'my-user/my-repo', ref: 'main' },
  kernelOptions: { kernelName: 'python3' },
});

// 访问子配置
config.binder;       // BinderOptions（含默认值）
config.kernels;      // KernelOptions
config.serverSettings; // ServerSettings
config.savedSessions; // SavedSessionOptions
config.mathjax;      // MathjaxOptions
config.events;       // ThebeEvents 事件总线
```

## MathJax 配置

控制数学公式渲染的 MathJax 2.x 加载。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `mathjaxUrl` | `string` | `'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js'` | MathJax 库 CDN 地址 |
| `mathjaxConfig` | `string` | `'TeX-AMS_CHTML-full,Safe'` | MathJax 配置文件名 |

```ts
// 默认值
{
  mathjaxUrl: 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js',
  mathjaxConfig: 'TeX-AMS_CHTML-full,Safe',
}
```

如果应用中已加载 MathJax 或使用其他数学渲染方案（如 KaTeX），这些选项可以忽略，但创建 `makeRenderMimeRegistry()` 时仍需要这些配置来初始化默认的数学渲染器。

## BinderOptions

控制通过 BinderHub 连接远程 Jupyter 环境的参数。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `repo` | `string` | `'executablebooks/thebe-binder-base'` | Binder 仓库（格式：`user/repo`） |
| `ref` | `string` | `'HEAD'` | Git 引用（分支名、tag 或 commit hash） |
| `binderUrl` | `string` | `'https://mybinder.org'` | BinderHub 实例 URL |
| `repoProvider` | `string` | `'github'` | 仓库提供商：`'github'`、`'gitlab'`、`'gist'`、`'git'` |

```ts
// 默认值
makeBinderOptions({}) → {
  repo: 'executablebooks/thebe-binder-base',
  ref: 'HEAD',
  binderUrl: 'https://mybinder.org',
  repoProvider: 'github',
}
```

### Binder URL 构建

根据 repoProvider 不同，Binder 构建 URL 格式不同：
- `github`：`{binderUrl}/build/gh/{repo}/{ref}`
- `gitlab`：`{binderUrl}/build/gl/{repo}/{ref}`
- `gist`：`{binderUrl}/build/gist/{repo}/{ref}`
- `git`：`{binderUrl}/build/git/{url-encoded-repo}/{ref}`

### 常用仓库配置示例

```ts
// 使用 GitHub 仓库的 main 分支
binderOptions: {
  repo: 'jupyter-widgets/ipywidgets',
  ref: 'main',
  repoProvider: 'github',
}

// 使用 Gist
binderOptions: {
  repo: 'anonymous/abc123def456',
  repoProvider: 'gist',
}

// 使用自定义 BinderHub 实例
binderOptions: {
  repo: 'my-org/my-env',
  ref: 'main',
  binderUrl: 'https://binder.example.org',
}
```

## KernelOptions

控制创建内核会话时的参数。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `kernelName` | `string` | `'python'` | 内核名称（对应 Jupyter kernelspec name） |
| `path` | `string` | `'/'` | Session 工作路径（影响 Notebook 文件名） |

```ts
// 默认值
makeKernelOptions({}) → {
  path: '/',
  kernelName: 'python',
}
```

`path` 参数的作用：
- 如果 path 匹配 `/*.ipynb$/`，文件名部分会被提取作为 session name
- 对于 JupyterLite 模式，path 中的 `/` 会被替换为 `-`（因为 lite 不支持子目录路径）
- 这个路径是 Jupyter Server 中的虚拟工作目录

### 常用内核名称

| 内核 | kernelName |
|------|-----------|
| Python 3 (IPython) | `'python3'` |
| Python (默认名) | `'python'` |
| R (IRkernel) | `'ir'` |
| Julia | `'julia-1.x'` |

> **注意**：具体可用的内核名称取决于 Binder 镜像中安装的 kernelspec。可以通过 `server.getKernelSpecs()` 查询可用内核。

## ServerSettings

直连 Jupyter Server 时的连接参数。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `baseUrl` | `string` | `'http://localhost:8888'` | Jupyter Server 基础 URL |
| `token` | `string` | `shortId()`（随机） | 认证 token |
| `appendToken` | `boolean` | `true` | 是否在 URL 中自动附加 token |
| `wsUrl` | `string` | 从 baseUrl 推导（http→ws） | WebSocket URL |

```ts
// 默认值
makeServerSettings({}) → {
  baseUrl: 'http://localhost:8888',
  token: <随机短ID>,
  appendToken: true,
  wsUrl: 'ws://localhost:8888',
}
```

> **安全注意**：默认 token 是随机生成的（`shortId()`），这是为了防止意外连接到本地运行的未认证 Jupyter Server。连接本地服务器时必须提供正确的 token（从 Jupyter 启动日志中获取，通常在 `?token=xxx` 中）。

### wsUrl 推导逻辑

```ts
const wsUrl = settings.wsUrl ?? baseUrl.replace(/^http/, 'ws');
// http://localhost:8888 → ws://localhost:8888
// https://mybinder.org/... → wss://mybinder.org/...
```

### 直连本地服务器示例

```ts
serverSettings: {
  baseUrl: 'http://localhost:8888',
  token: 'abc123...',  // 从 jupyter lab 启动日志获取
  appendToken: true,
}
```

## SavedSessionOptions

Binder 会话持久化配置——通过 localStorage 保存已构建的 Binder 服务器地址，避免每次页面加载都重新触发 Binder 构建。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | `boolean` | `true` | 是否启用 session 持久化 |
| `maxAge` | `number` | `86400`（24小时） | 保存的 session 最大有效期（秒） |
| `storagePrefix` | `string` | `'thebe-binder'` | localStorage key 前缀 |

```ts
// 默认值
makeSavedSessionOptions({}) → {
  enabled: true,
  maxAge: 86400,
  storagePrefix: 'thebe-binder',
}
```

### 工作机制

1. 首次连接 Binder 成功后，服务器 URL 和 token 保存到 `localStorage[storageKey]`
2. storageKey 由 binderUrl + repo + ref + repoProvider 组合生成
3. 下次连接时，先检查 localStorage 中是否有未过期的保存信息
4. 如果有，尝试直接连接保存的服务器（发送 ping 请求检测存活）
5. 如果连接失败或已过期，回退到正常 Binder 构建流程

### 禁用 Session 持久化

```ts
savedSessionOptions: {
  enabled: false;  // 每次都重新构建 Binder 环境
}
```

## 配置示例：三种连接模式

### Binder 连接

```ts
const config = makeConfiguration({
  binderOptions: {
    repo: 'executablebooks/thebe-binder-base',
    ref: 'HEAD',
    binderUrl: 'https://mybinder.org',
  },
  kernelOptions: { kernelName: 'python' },
  savedSessionOptions: { enabled: true, maxAge: 86400 },
});
const server = connectToBinder(config);
```

### 直连本地 Jupyter

```ts
const config = makeConfiguration({
  serverSettings: {
    baseUrl: 'http://localhost:8888',
    token: 'your-token-from-jupyter-log',
  },
  kernelOptions: { kernelName: 'python3' },
});
const server = connectToJupyter(config);
```

### JupyterLite/Pyodide

```ts
const config = makeConfiguration({
  kernelOptions: { kernelName: 'python' },
});
// 需要先加载 thebe-lite
const server = connectToJupyterLite(config);
```

## 相关概念

- [03-thebe-core-api.md](03-thebe-core-api.md)：核心 API 对象层次
- [05-thebe-binder.md](05-thebe-binder.md)：Binder 连接机制
- [06-thebe-lite-pyodide.md](06-thebe-lite-pyodide.md)：JupyterLite 无服务器模式
- [02-thebe-interactive.md](../examples/02-thebe-interactive.md)：配置示例
