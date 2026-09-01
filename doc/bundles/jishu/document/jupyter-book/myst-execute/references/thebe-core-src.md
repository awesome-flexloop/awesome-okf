---
type: reference
title: "thebe-core 核心 API 源码"
description: "thebe-core 包的核心 API 源码入口，包含 Config 配置、ThebeServer 连接、ThebeSession 会话、ThebeNotebook 笔记本抽象"
tags: [thebe, thebe-core, jupyter, binder, server-connection]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "thebe/packages/core/src/index.ts"
    facts: [F-005, F-006]
  - path: "thebe/packages/core/src/config.ts"
    facts: [F-045, F-046]
  - path: "thebe/packages/core/src/options.ts"
    facts: [F-047, F-048, F-049, F-050]
  - path: "thebe/packages/core/src/server.ts"
    facts: [F-051, F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059]
  - path: "thebe/packages/core/src/thebe/api.ts"
    facts: [F-060, F-061]
  - path: "thebe/packages/core/src/thebe/entrypoint.ts"
    facts: [F-062, F-063]
  - path: "thebe/packages/core/src/types.ts"
    facts: [F-064, F-065, F-066, F-067, F-068, F-069, F-070]
---

# thebe-core 核心 API 源码

## 源码位置

**仓库根**：`external/libs/ai/jupyter-book/thebe/`
**包目录**：`packages/core/src/`

## 核心文件清单

| 文件 | 职责 | 关键导出 |
|------|------|---------|
| `index.ts` | 包入口 | 汇总导出所有公共类、函数、类型 |
| `config.ts` | 配置对象 | `Config` 类 |
| `options.ts` | 选项工厂函数 | `makeBinderOptions()`, `makeKernelOptions()`, `makeSavedSessionOptions()`, `makeServerSettings()`, `makeConfiguration()` |
| `server.ts` | Jupyter 服务器连接 | `ThebeServer` 类（Binder/直连/JupyterLite 三种连接模式） |
| `session.ts` | 内核会话 | `ThebeSession` 类 |
| `notebook.ts` | 笔记本抽象 | `ThebeNotebook` 类, `CodeBlock` 类型 |
| `cell.ts` | 代码单元格 | `ThebeCodeCell` 类 |
| `markdown.ts` | Markdown 单元格 | `ThebeMarkdownCell` 类 |
| `passive.ts` | 被动渲染器 | `PassiveCellRenderer` 类（无内核的输出渲染） |
| `events.ts` | 事件系统 | `ThebeEvents`, 状态/错误事件常量 |
| `emitter.ts` | 事件发射器 | `EventEmitter` 类 |
| `thebe/api.ts` | 高层 API | `connectToBinder()`, `connectToJupyter()`, `connectToJupyterLite()`, `setupNotebookFromBlocks()`, `setupNotebookFromIpynb()` |
| `thebe/entrypoint.ts` | UMD 入口 | `setupThebeCore()`, `JsApi`, `ThebeCoreGlobal`（window.thebeCore 类型） |
| `types.ts` | 类型定义 | `CoreOptions`, `BinderOptions`, `ServerSettings`, `KernelOptions`, `IThebeCell`, `ServerRuntime`, `ServerRestAPI` |
| `url.ts` | Binder URL 构建 | `makeBinderUrls()`, `WELL_KNOWN_REPO_PROVIDERS` |
| `sessions.ts` | 会话持久化 | `getExistingServer()`, `saveServerInfo()`, `clearAllSavedSessions()` |
| `utils.ts` | 工具函数 | `shortId()` 等 |
| `rendermime.ts` | MIME 渲染 | `makeRenderMimeRegistry()` |
| `manager.ts` | 内核管理器 | 辅助函数 |

## 模块依赖图

```
thebe/entrypoint.ts → thebe/api.ts → server.ts → config.ts
                                         ↓
                                     session.ts → cell.ts
                                         ↓
                                     notebook.ts → cell.ts, markdown.ts, passive.ts
```

## 版本与构建

- 包名：thebe-core
- 构建工具：webpack（CJS bundle）+ esbuild（CSS）
- 测试框架：vitest
- UMD 全局变量：`window.thebeCore`（包含 module、api、version）
- CSS 入口：`index.css`（复制到 dist/lib/thebe-core.css）
