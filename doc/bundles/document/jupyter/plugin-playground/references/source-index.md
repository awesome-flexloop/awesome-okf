---
type: Reference
title: Plugin Playground 源码索引
description: Plugin Playground 核心源码模块索引，包含文件路径、模块职责、公开API映射表。
tags: [jupyterlab, plugin-playground, source, reference]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: plugin-playground-source
    resource: /references/source-index.md
    title: Plugin Playground Source Code Index
---

## 项目基本信息

| 属性 | 值 |
|------|-----|
| 包名 | `@jupyterlab/plugin-playground` |
| 版本 | 1.0.0 |
| 许可证 | BSD-3-Clause |
| 仓库 | https://github.com/jupyterlab/plugin-playground |
| JupyterLab 兼容版本 | ^4.5.5 |
| TypeScript 版本 | ~5.5.4 |
| 构建工具 | tsc + jupyter labextension build |
| 包管理器 | yarn@3.5.0 |

## 源码文件索引

### 核心运行时模块

| 文件 | 职责 | 主要导出 |
|------|------|---------|
| `src/index.ts` | JupyterLab 扩展入口，命令/工具栏/侧边栏注册 | `PluginPlayground`, `IPluginPlayground`, `CommandIDs` |
| `src/loader.ts` | 插件代码加载与执行 | `PluginLoader`, `PluginLoadingError` |
| `src/transpiler.ts` | TypeScript→CommonJS 浏览器端转译 | `PluginTranspiler`, `NoDefaultExportError` |
| `src/resolver.ts` | ES import 语句解析与模块加载 | `ImportResolver` |
| `src/modules.ts` | 已知模块名列表与动态导入 | `KNOWN_MODULE_NAMES`, `loadKnownModule` |
| `src/known-modules.ts` | 模块注册、发现与元数据管理 | `registerKnownModule`, `listKnownModules`, `registerCoreKnownModules`, `discoverFederatedKnownModules` |
| `src/requirejs.ts` | 隔离 iframe 中的 RequireJS 加载 | `RequireJSLoader`, `loadInIsolated`, `IRequireJS` |
| `src/runtime-shared-modules.ts` | Webpack/Rspack 共享作用域模块加载 | `loadSharedScopeModule` |
| `src/types.ts` | 模块类型定义 | `IModule`, `IModuleMember` |

### 工具与辅助模块

| 文件 | 职责 | 主要导出 |
|------|------|---------|
| `src/contents.ts` | Jupyter Contents API 封装与编辑器工具 | `ContentUtils` |
| `src/errors.tsx` | 错误信息 React 渲染组件 | `formatErrorWithResult`, `formatImportError` |
| `src/command-completion.ts` | 编辑器中命令 ID 自动补全 | `CommandCompletionProvider`, `getCommandRecords`, `getCommandArgumentDocumentation` |
| `src/token-insertion.ts` | Token/import 语句插入到编辑器 | `insertImportStatement`, `insertTokenDependency`, `parseTokenReference` |
| `src/archive.ts` | 文件归档下载 | `downloadArchive`, `IArchiveEntry` |
| `src/export-template.ts` | 导出模板归档创建 | `createTemplateArchive` |
| `src/wheel.ts` | Python wheel 包创建 | `createPythonWheelArchive` |
| `src/share-link.ts` | 分享链接编解码 | （内部工具） |
| `src/share-via-link-controller.ts` | 通过链接分享插件控制器 | `ShareViaLinkController` |
| `src/encoding.ts` | 编码工具 | （内部工具） |

### UI 组件模块

| 文件 | 职责 | 主要导出 |
|------|------|---------|
| `src/token-sidebar.tsx` | Token/命令/模块浏览器侧边栏 | `TokenSidebar`, `filterTokenRecords`, `filterCommandRecords` |
| `src/example-sidebar.tsx` | 扩展示例浏览器侧边栏 | `ExampleSidebar`, `filterExampleRecords` |
| `src/loaded-plugins-sidebar.tsx` | 已加载插件管理侧边栏 | `LoadedPluginsSidebar` |
| `src/dialogs.tsx` | CDN 同意对话框等 | `formatCDNConsentDialog` |
| `src/export-toolbar.tsx` | 导出工具栏控件 | `ExportToolbarController` |
| `src/share-toolbar.tsx` | 分享工具栏控件 | （内部组件） |
| `src/split-action.tsx` | 分割操作按钮组件 | （内部组件） |
| `src/icons.ts` | 自定义 SVG 图标 | `runTileIcon`, `tokenSidebarIcon`, `loadOnSaveToggleIcon` |
| `src/tour.ts` | 新手引导集成 | `launchPluginPlaygroundTour`, `hasPluginPlaygroundTourSupport` |
| `src/components/url-load-hint.ts` | URL 加载提示浮动组件 | `createFloatingUrlLoadHint` |

## 核心公开 API 速查

### PluginLoader

```typescript
class PluginLoader {
  constructor(options: PluginLoader.IOptions);
  load(code: string, basePath: string | null): Promise<PluginLoader.IResult>;
  loadFile(code: string): Promise<IModule>;
}

// IOptions: { transpiler, importFunction, tokenMap, requirejs, serviceManager }
// IResult: { plugins: IPlugin[], code, transpiled, schemas, declaredStylePaths }
```

### PluginTranspiler

```typescript
class PluginTranspiler {
  constructor(options: PluginTranspiler.IOptions);
  readonly importFunctionName = 'require';
  transpile(code: string, requireDefaultExport: boolean, fileName?: string): string;
}
```

### ImportResolver

```typescript
class ImportResolver {
  constructor(options: ImportResolver.IOptions);
  resolve(module: string): Promise<Token<any> | IModule | IModuleMember>;
  rollbackLocalStyleMutations(): void;
  commitLocalStyleMutations(): void;
  loadedLocalStylePaths: ReadonlySet<string>;
}
```

### ContentUtils

```typescript
namespace ContentUtils {
  function normalizeContentsPath(path: string | null | undefined): string;
  function isSafeRelativePath(path: string): boolean;
  async function getFileModel(serviceManager, path): Promise<IFileModel | null>;
  async function getDirectoryModel(serviceManager, path): Promise<IDirectoryModel | null>;
  function fileModelToText(fileModel): string | null;
  async function readContentsFileAsText(serviceManager, path): Promise<string | null>;
  async function ensureContentsDirectory(serviceManager, path): Promise<void>;
  function highlightEditorLines(editor, lines, timeoutMs?): void;
  async function copyValueToClipboard(value: string): Promise<void>;
}
```

## 相关概念

- [插件加载流程](../concepts/05-plugin-loader.md)
- [TypeScript 转译机制](../concepts/03-typescript-transpilation.md)
- [模块解析系统](../concepts/04-module-resolution.md)
- [Token 依赖注入](../concepts/06-token-system.md)
