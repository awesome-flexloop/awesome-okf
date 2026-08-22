---
type: Reference
title: Echo Kernel 插件注册源码信源
description: src/index.ts 插件入口的源码API登记，包括JupyterFrontEndPlugin定义、IKernelSpecs注册、EchoKernel工厂函数
tags: [plugin, jupyterlab, kernelspecs, registration, typescript]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: index-ts
    resource: /references/plugin-source.md
    title: src/index.ts
---

## 源码位置

- `src/index.ts` — 插件入口文件，约43行

## 导出 API

### 插件定义（kernel 常量，L18-L39）

| 属性 | 值 | 说明 |
|------|-----|------|
| `id` | `'@jupyterlite/echo-kernel:kernel'` | 插件唯一标识符 |
| `autoStart` | `true` | JupyterLab启动时自动激活 |
| `requires` | `[IKernelSpecs]` | 依赖注入：内核规格注册服务 |
| `activate` | `(app, kernelspecs) => void` | 激活函数 |

### activate 函数（L22-L38）

调用 `kernelspecs.register()` 注册内核规格，参数为一个对象：

| 字段 | 类型 | 值 |
|------|------|-----|
| `spec` | `KernelSpec.ISpecModel` | 内核规格描述对象 |
| `spec.name` | `string` | `'echo'` |
| `spec.display_name` | `string` | `'Echo'` |
| `spec.language` | `string` | `'text'` |
| `spec.argv` | `string[]` | `[]`（空数组，浏览器内核无命令行参数） |
| `spec.resources` | `object` | `{ 'logo-32x32': '', 'logo-64x64': '' }`（无自定义logo） |
| `create` | `async (options) => Promise<IKernel>` | 异步工厂函数，返回 `new EchoKernel(options)` |

### 默认导出（L41-L43）

```typescript
const plugins: JupyterFrontEndPlugin<any>[] = [kernel];
export default plugins;
```

导出插件数组，包含一个插件（kernel）。

## 导入依赖

| 导入来源 | 导入项 | 用途 |
|----------|--------|------|
| `@jupyterlab/application` | `JupyterFrontEnd`, `JupyterFrontEndPlugin` | JupyterLab前端插件类型 |
| `@jupyterlite/services` | `IKernel`（type） | 内核接口类型 |
| `@jupyterlite/services` | `IKernelSpecs` | 内核规格注册服务Token |
| `./kernel` | `EchoKernel` | 内核实现类 |

## 关键机制

1. **JupyterLab插件系统**：通过 `JupyterFrontEndPlugin<void>` 定义插件，使用Token（`IKernelSpecs`）声明依赖
2. **内核注册模式**：`kernelspecs.register({spec, create})` 是JupyterLite内核注册的标准模式——spec描述内核元信息，create是工厂函数
3. **浏览器内核特征**：`argv: []` 为空数组，因为浏览器内核不通过命令行启动，而是在Web Worker中实例化
4. **autoStart: true**：插件无需用户手动激活，JupyterLab启动时自动注册内核
