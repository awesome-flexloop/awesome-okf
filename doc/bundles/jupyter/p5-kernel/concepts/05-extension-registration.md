---
type: Concept
title: 扩展注册与 CDN 配置
description: p5-kernel JupyterLab 扩展的插件注册机制、KernelSpec 定义、p5Url CDN 配置与覆盖方式、logo 资源
tags: [extension, jupyterlab-plugin, kernelspec, cdn, p5url, registration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ext
    resource: /references/extension-source.md
    title: JupyterLab 扩展注册信源
---

## 扩展包概述

`@jupyterlite/p5-kernel-extension` 是 p5-kernel 的 JupyterLab 前端扩展包，负责：

1. 将 P5Kernel 注册到 JupyterLite 的内核规格系统（IKernelSpecs）
2. 提供 p5.js CDN URL 的配置和解析
3. 定义内核在 UI 中显示的名称、语言、logo 等元信息
4. 作为 JupyterLite 扩展被自动发现和加载

扩展入口位于 [src/index.ts](https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel-extension/src/index.ts)。

## 插件定义

```typescript
const kernel: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlite/p5-kernel-extension:kernel',
  autoStart: true,
  requires: [IKernelSpecs],
  activate: (app: JupyterFrontEnd, kernelspecs: IKernelSpecs) => {
    // 注册逻辑
  }
};
```

| 属性 | 值 | 说明 |
|------|-----|------|
| id | `'@jupyterlite/p5-kernel-extension:kernel'` | 插件唯一标识 |
| autoStart | `true` | JupyterLab 启动时自动激活 |
| requires | `[IKernelSpecs]` | 依赖内核规格注册服务 |

插件启动时自动激活，无需用户手动启用。它依赖 `IKernelSpecs`（由 `@jupyterlite/services` 提供），这是 JupyterLite 的内核注册中心。

## p5Url CDN 配置

### 默认 CDN

```typescript
const P5_CDN_URL = 'https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js';
```

默认从 jsDelivr CDN 加载 p5.js v1.9.0。

### URL 解析逻辑

```typescript
const url = PageConfig.getOption('p5Url') || P5_CDN_URL;
const p5Url = URLExt.isLocal(url)
  ? URLExt.join(window.location.origin, url)
  : url;
```

1. 首先尝试从 JupyterLab 的 `PageConfig` 获取 `p5Url` 配置项
2. 如果未配置，使用默认 CDN URL
3. 使用 `URLExt.isLocal()` 判断是否为本地路径（如 `./p5.js` 或 `/static/p5.js`）
4. 本地路径自动拼接 `window.location.origin` 生成完整 URL
5. 远程 URL（以 http/https 开头）直接使用

### 覆盖 CDN 的方法

在 JupyterLite 部署中，可以通过以下方式覆盖默认 p5Url：

1. **JupyterLite 配置文件**：在 `jupyter-lite.json` 中设置 PageConfig 选项
2. **查询参数**：通过 URL 参数传递（取决于 JupyterLite 配置）
3. **自托管 p5.js**：将 p5.js 放在站点目录中，使用本地路径

示例（自托管 p5.js）：
```
# 将 p5.min.js 放在 JupyterLite 站点的 files/ 目录下
# 然后通过 PageConfig 配置 p5Url 为 './files/p5.min.js'
```

## KernelSpec 注册

```typescript
kernelspecs.register({
  spec: {
    name: 'p5js',
    display_name: 'p5.js',
    language: 'javascript',
    argv: [],
    spec: {
      argv: [],
      env: {},
      display_name: 'p5.js',
      language: 'javascript',
      interrupt_mode: 'message',
      metadata: {}
    },
    resources: {
      'logo-32x32': 'TODO',
      'logo-64x64': p5Logo
    }
  },
  create: async (options: IKernel.IOptions): Promise<IKernel> => {
    return new P5Kernel({
      ...options,
      p5Url
    });
  }
});
```

### spec 字段详解

**外层 spec**：

| 字段 | 值 | 说明 |
|------|-----|------|
| name | `'p5js'` | 内核唯一标识符，用于内核选择和 Notebook 元数据 |
| display_name | `'p5.js'` | 内核选择器下拉菜单中显示的名称 |
| language | `'javascript'` | 语言标识，影响代码编辑器的语法高亮模式 |
| argv | `[]` | 启动参数（浏览器内核无后端进程，为空） |

**内层 spec（内核详细规格）**：

| 字段 | 值 | 说明 |
|------|-----|------|
| argv | `[]` | 无命令行参数 |
| env | `{}` | 无额外环境变量 |
| display_name | `'p5.js'` | 显示名称 |
| language | `'javascript'` | 编程语言 |
| interrupt_mode | `'message'` | 通过内核消息中断（非信号中断） |
| metadata | `{}` | 扩展元数据 |

**resources**：

| 字段 | 值 | 说明 |
|------|-----|------|
| logo-32x32 | `'TODO'` | 32x32 图标（未实现） |
| logo-64x64 | p5Logo | 64x64 PNG 图标（从 style/icons/p5js.png 导入） |

> `interrupt_mode: 'message'` 表示中断通过发送 interrupt 消息实现，而非发送 OS 信号。浏览器内核没有进程，所以无法使用信号中断。

### create 工厂函数

`create` 是一个异步工厂函数，接收 `IKernel.IOptions`（包含内核 id、通信通道等标准选项），展开后附加解析好的 `p5Url`，返回 `new P5Kernel({...options, p5Url})` 实例。

## 共享包配置

在 `package.json` 的 `jupyterlab` 配置中：

```json
{
  "sharedPackages": {
    "@jupyterlite/services": {
      "bundled": false,
      "singleton": true
    }
  }
}
```

`@jupyterlite/services` 配置为 singleton（单例）且不打包进扩展 bundle：
- **bundled: false**：不将 `@jupyterlite/services` 的代码打包进扩展的 JS 文件中
- **singleton: true**：运行时与 JupyterLite 主应用共享同一个 `@jupyterlite/services` 实例

这确保扩展中的 `IKernelSpecs` 和 `IKernel` 等服务与主应用使用相同的实例，避免类型不兼容。

## JupyterLite 扩展标记

```json
{
  "jupyterlite": {
    "liteExtension": true
  }
}
```

`liteExtension: true` 标记这是一个 JupyterLite 内核扩展。JupyterLite 构建系统会自动发现此类扩展，将其纳入 JupyterLite 站点的构建产物中，无需额外配置。

## Logo 资源

p5Logo 从 PNG 文件导入：

```typescript
import p5Logo from '../style/icons/p5js.png';
```

通过 `declarations.d.ts` 中的模块声明，TypeScript 可以识别 PNG 导入：

```typescript
declare module '*.png' {
  const value: string;
  export default value;
}
```

构建时，webpack/JupyterLab builder 会将 PNG 文件处理为资源 URL，赋给 `p5Logo` 变量。当前只提供了 64x64 logo（logo-32x32 标记为 'TODO'）。

## 模块导出

```typescript
const plugins: JupyterFrontEndPlugin<void>[] = [kernel];
export default plugins;
```

默认导出插件数组。虽然当前只有一个 kernel 插件，但使用数组格式方便将来添加更多插件（如设置面板、状态条等）。

## 扩展安装与发现流程

```
pip install jupyterlite-p5-kernel
    │
    ▼
jupyter lite build
    │
    ├─ 发现 jupyterlite.liteExtension: true 的已安装包
    ├─ 收集 labextension 静态资源（JS/CSS/logo）
    ├─ 构建到 JupyterLite 站点输出目录
    │
    ▼
浏览器访问 JupyterLite 站点
    │
    ├─ JupyterLab 启动
    ├─ autoStart 插件激活
    ├─ activate(app, kernelspecs) 被调用
    ├─ p5Url 从 PageConfig 或默认 CDN 解析
    ├─ P5Kernel 工厂注册到 IKernelSpecs
    │
    ▼
用户创建新 Notebook，内核选择器中出现 "p5.js"
```

## 相关概念

- [架构概览](/concepts/01-architecture-overview.md)
- [构建与打包](/concepts/06-build-and-packaging.md)
- [第一个 p5 Sketch](/examples/01-first-sketch.md)
