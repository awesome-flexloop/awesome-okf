---
type: Reference
title: JupyterLab 扩展注册信源
description: p5-kernel-extension 插件的注册机制、CDN 配置、KernelSpec 定义
tags: [extension, jupyterlab-plugin, kernelspec, cdn, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ext-src
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel-extension/src/index.ts
    title: packages/p5-kernel-extension/src/index.ts
  - id: ext-pkg
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel-extension/package.json
    title: packages/p5-kernel-extension/package.json
---

## 插件定义

插件是一个 `JupyterFrontEndPlugin<void>`，配置如下：

| 属性 | 值 |
|------|-----|
| id | `'@jupyterlite/p5-kernel-extension:kernel'` |
| autoStart | `true` |
| requires | `[IKernelSpecs]` |

## activate 函数

```typescript
activate: (app: JupyterFrontEnd, kernelspecs: IKernelSpecs) => void
```

### p5Url 解析逻辑

```typescript
const P5_CDN_URL = 'https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js';
const url = PageConfig.getOption('p5Url') || P5_CDN_URL;
const p5Url = URLExt.isLocal(url)
  ? URLExt.join(window.location.origin, url)
  : url;
```

1. 默认 CDN URL：`https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js`（p5.js v1.9.0）
2. 可通过 JupyterLab PageConfig 的 `p5Url` 选项覆盖
3. 使用 `URLExt.isLocal()` 判断是否为本地路径
4. 本地路径通过 `URLExt.join(window.location.origin, url)` 拼接完整 URL

### kernelspecs.register() 调用

注册的 kernel spec：

```typescript
{
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
      'logo-64x64': p5Logo   // 从 ../style/icons/p5js.png 导入
    }
  },
  create: async (options: IKernel.IOptions): Promise<IKernel> => {
    return new P5Kernel({
      ...options,
      p5Url
    });
  }
}
```

### KernelSpec 关键字段

| 字段 | 值 | 说明 |
|------|-----|------|
| name | `'p5js'` | 内核唯一标识名 |
| display_name | `'p5.js'` | 内核选择器中显示的名称 |
| language | `'javascript'` | 语言标识（代码编辑器使用 JavaScript 模式） |
| interrupt_mode | `'message'` | 中断模式：通过消息传递中断 |
| argv | `[]` | 无命令行参数（浏览器内核无后端进程） |
| resources['logo-64x64'] | p5Logo (PNG) | 64x64 logo 图标 |

### create 工厂函数

接收 `IKernel.IOptions`，展开后附加 `p5Url`，返回 `new P5Kernel({...options, p5Url})`。

## 模块导出

```typescript
const plugins: JupyterFrontEndPlugin<void>[] = [kernel];
export default plugins;
```

默认导出插件数组（当前仅包含 kernel 一个插件）。

## JupyterLab 扩展配置（package.json）

```json
{
  "jupyterlab": {
    "extension": true,
    "outputDir": "../../jupyterlite_p5_kernel/labextension",
    "sharedPackages": {
      "@jupyterlite/services": {
        "bundled": false,
        "singleton": true
      }
    }
  },
  "jupyterlite": {
    "liteExtension": true
  }
}
```

- `extension: true`：标记为 JupyterLab 扩展
- `outputDir`：构建产物输出到 Python 包的 labextension 目录
- `sharedPackages`：`@jupyterlite/services` 不打包进扩展，使用单例模式与宿主共享
- `jupyterlite.liteExtension: true`：标记为 JupyterLite 内核扩展（由 JupyterLite 内核系统发现和加载）

## PNG 资源类型声明

```typescript
// declarations.d.ts
declare module '*.png' {
  const value: string;
  export default value;
}
```

允许 TypeScript 直接 `import p5Logo from '../style/icons/p5js.png'` 导入图片资源，返回图片的 URL 路径。
