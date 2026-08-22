---
type: reference
title: "thebe-react React 集成源码"
description: "thebe-react 包提供 React Context Provider 和 Hooks，用于在 React 应用中声明式集成 thebe 交互式代码执行功能"
tags: [thebe, react, hooks, provider, context]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "thebe/packages/react/src/index.ts"
    facts: [F-008]
  - path: "thebe/packages/react/src/ThebeLoaderProvider.tsx"
    facts: [F-009, F-076]
  - path: "thebe/packages/react/src/ThebeServerProvider.tsx"
    facts: [F-077]
  - path: "thebe/packages/react/src/ThebeSessionProvider.tsx"
    facts: [F-078]
  - path: "thebe/packages/react/src/hooks/notebook.ts"
    facts: [F-079, F-080]
  - path: "thebe/packages/react/src/hooks/index.ts"
    facts: []
---

# thebe-react React 集成源码

## 源码位置

**仓库根**：`external/libs/ai/jupyter-book/thebe/`
**包目录**：`packages/react/src/`

## 核心文件清单

| 文件 | 职责 | 关键导出 |
|------|------|---------|
| `index.ts` | 包入口 | 汇总导出所有 Providers、Hooks、组件 |
| `ThebeLoaderProvider.tsx` | 核心库加载 | `ThebeLoaderProvider`（ESM import）、`ThebeBundleLoaderProvider`（script 标签）、`useThebeLoader()` |
| `ThebeServerProvider.tsx` | 服务器连接 | `ThebeServerProvider`, `ThebeServerContext`, `useThebeServer()`, `useThebeConfig()`, `useDisposeThebeServer()` |
| `ThebeSessionProvider.tsx` | 会话管理 | `ThebeSessionProvider`, `ThebeSessionContext`, `useThebeSession()` |
| `ThebeRenderMimeRegistryProvider.tsx` | MIME 渲染注册表 | `ThebeRenderMimeRegistryProvider`, `useRenderMimeRegistry()` |
| `OutputAreaByRef.tsx` | 输出区域组件 | 通过 ref 挂载 Jupyter 输出 |
| `hooks/notebook.ts` | Notebook Hooks | `useNotebook()`, `useNotebookFromSource()`, `useNotebookBase()`, `findErrors()` |
| `hooks/interpolate.ts` | 字符串插值 | 辅助 Hook |

## Provider 嵌套顺序

正确的嵌套顺序（从外到内）：

```
ThebeLoaderProvider 或 ThebeBundleLoaderProvider  // 加载 thebe-core
  └─ ThebeServerProvider                          // 建立服务器连接
       └─ ThebeRenderMimeRegistryProvider         // 创建渲染注册表
            └─ ThebeSessionProvider               // 启动内核会话
                 └─ (使用 useNotebook/useNotebookFromSource 的组件)
```

## 核心 Hooks

### useThebeLoader()

返回 `{ core, error, loading, load }`，其中 `core` 是动态 import 的 thebe-core 模块。

### useThebeServer()

返回 `{ config, events, server, connecting, ready, error, connect, disconnect, subscribe, unsubAll }`。

- `connect()`：手动触发服务器连接（Binder/直连/JupyterLite）
- `disconnect()`：销毁当前服务器并创建新实例
- `subscribe(fn)`：订阅服务器/会话/内核状态事件

### useThebeSession()

返回 `{ path, starting, ready, session, error, start, shutdown }`。

### useNotebook(name, fetchNotebook, opts?)

- 异步加载 ipynb 文件，创建 ThebeNotebook 实例
- 返回 `{ ready, loading, attached, executing, executed, errors, notebook, cellRefs, cellIds, executeAll, executeSome, clear }`
- opts.refsForWidgetsOnly（默认 true）：只为标记 widget 的单元格生成 DOM ref

### useNotebookFromSource(sourceCode, opts?)

- 从代码字符串数组创建 Notebook
- 返回接口同 useNotebook

## ThebeBundleLoaderProvider 选项

- `start?: boolean`：是否自动开始加载
- `loadThebeLite?: boolean`：是否同时加载 thebe-lite
- `publicPath?: string`：script 标签的公共路径前缀
- `options?: { attempts?: number, delay?: number }`：轮询配置（默认 50 次，间隔 300ms）
