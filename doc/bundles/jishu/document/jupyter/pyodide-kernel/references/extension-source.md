---
type: Reference
title: JupyterLab Extension 源码参考
description: "@jupyterlite/pyodide-kernel-extension JupyterLab 扩展源码，负责在 JupyterLab 中注册 Pyodide 内核规范"
tags: [extension, jupyterlab, plugin, kernel-spec]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ext-index
    resource: /references/extension-source.md
    title: "packages/pyodide-kernel-extension/src/index.ts"
  - id: ext-schema
    resource: /references/extension-source.md
    title: "packages/pyodide-kernel-extension/schema/kernel.v0.schema.json"
---

## 源码文件位置

Extension 包位于 `packages/pyodide-kernel-extension/`，源码路径：
`external/libs/jupyter/pyodide-kernel/packages/pyodide-kernel-extension/`

## 核心文件

| 文件 | 说明 |
|------|------|
| `src/index.ts` | JupyterLab 插件定义，注册 kernel 和服务 |
| `schema/kernel.v0.schema.json` | 插件设置 JSON Schema |

## JupyterLab 插件

插件 ID：`@jupyterlite/pyodide-kernel-extension:kernel`

```typescript
const plugin: JupyterFrontEndPlugin<IPyodideWorkerKernel> = {
  id: '@jupyterlite/pyodide-kernel-extension:kernel',
  autoStart: true,
  requires: [IKernelSpecsManager, ISettingRegistry, IServiceWorkerManager],
  optional: [IBrowserRegistry],
  provides: IPyodideWorkerKernel,
  activate: async (app, kernelspecsManager, settingRegistry, serviceWorkerManager, browserRegistry) => {
    // 1. 加载插件设置
    // 2. 注册 Pyodide kernel spec
    // 3. 返回 kernel factory
  }
};
```

## Kernel Spec

注册的 kernel spec 结构：

```typescript
const pyodideSpec: ISpecModel = {
  name: 'pyodide',
  display_name: 'Pyodide',
  language: 'python',
  argv: [],  // 浏览器中无命令行参数
  resources: {},
  spec: {
    argv: [],
    display_name: 'Pyodide',
    language: 'python',
    interrupt_mode: 'message',  // 通过消息中断而非 SIGINT
    metadata: {},
  },
};
```

## 插件设置 Schema

设置项（通过 `schema/kernel.v0.schema.json` 定义）：

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `pyodideUrl` | string | 从 CDN | Pyodide 发行版 URL |
| `loadPyodideOptions` | object | `{}` | 传递给 loadPyodide 的选项 |
| `pipliteUrls` | string[] | `[]` | piplite wheel 索引 URL 列表 |
| `pipliteWheelUrl` | string | 内置 | piplite wheel 包 URL |
| `disablePyPIFallback` | boolean | `false` | 禁用 PyPI 回退 |
| `browsingContextId` | string | - | Service Worker 浏览上下文 ID |
| `mountDrive` | boolean | `false` | 是否挂载 Emscripten DriveFS |

## 注册时机

插件激活时：
1. 等待 `serviceWorkerManager.ready`（如需要 Service Worker）
2. 通过 `IKernelSpecsManager.registerSpecs({ pyodide: pyodideSpec })` 注册内核
3. 通过 `IKernelSpecsManager.setDefaultKernel('pyodide')` 设为默认内核
4. 读取用户配置（ISettingRegistry），覆盖默认设置

## 相关概念

- [Pyodide Kernel 介绍](../concepts/00-introduction.md)
- [快速开始](../concepts/01-getting-started.md)
