---
type: Concept
title: 样式处理与CSS隔离
description: Plugin Playground 如何通过动态style标签注入、CSS @import重写、快照栈事务机制管理插件样式，实现多插件样式隔离与回滚。
tags: [jupyterlab, plugin-playground, css, style, isolation, snapshot, rollback]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: resolver-api
    resource: /references/resolver-api.md
    title: ImportResolver API 参考
---

## CSS 处理概述

JupyterLab 插件通常需要添加 CSS 样式来美化 UI。在传统扩展开发中，CSS 通过 webpack 打包并注入到页面。但在 Plugin Playground 的即时加载场景下，CSS 需要在运行时动态处理。

ImportResolver 负责 CSS 文件的加载和管理，采用**动态 `<style>` 标签注入 + 快照栈事务**方案，而非 Shadow DOM 隔离。

## 本地 CSS 文件加载

当插件代码中出现 `import './styles.css'` 这样的相对导入时，ImportResolver 通过 `_resolveLocalFile()` 检测到 `.css` 扩展名，调用 `_loadLocalStyle()` 处理：

```typescript
private _loadLocalStyle(path: string, css: string): IModule {
  this._snapshotLocalStyle(path);                    // 1. 保存当前样式快照
  this._loadedLocalStylePaths.add(path);            // 2. 记录已加载路径
  const rewrittenCss = this._rewriteRelativeCssImports(css, path); // 3. 重写@import
  const styleElement = this._ensureLocalStyleElement(path); // 4. 创建/获取style元素
  if (styleElement.textContent !== rewrittenCss) {
    styleElement.textContent = rewrittenCss;        // 5. 设置CSS内容
  }
  return { default: path as unknown as IModuleMember }; // 6. 返回路径作为default导出
}
```

CSS 导入返回 `{ default: path }`，path 是CSS文件在Jupyter内容服务中的路径。

## Style 元素管理

### 创建和获取

`_ensureLocalStyleElement(path)` 为每个CSS路径创建或复用一个 `<style>` 元素：

```typescript
private _ensureLocalStyleElement(path: string): HTMLStyleElement {
  const head = document.head ?? document.documentElement;
  let styleElement = ImportResolver._localCssStyles.get(path);
  if (!styleElement || !styleElement.isConnected) {
    styleElement = document.createElement('style');
    styleElement.setAttribute('data-plugin-playground-style-path', path);
    head.appendChild(styleElement);
    ImportResolver._localCssStyles.set(path, styleElement);
  }
  return styleElement;
}
```

每个CSS路径对应一个 `<style>` 元素，通过 `data-plugin-playground-style-path` 属性标记。元素存储在静态Map `_localCssStyles` 中，跨ImportResolver实例共享。

### 移除样式

静态方法 `removeLocalStyles(paths)` 可以移除指定路径的style元素：

```typescript
static removeLocalStyles(paths: Iterable<string>): void {
  for (const path of paths) {
    const styleElement = ImportResolver._localCssStyles.get(path);
    if (styleElement) {
      styleElement.remove();
    }
    ImportResolver._localCssStyles.delete(path);
  }
}
```

## CSS @import 重写

插件CSS文件中可能包含相对路径的 `@import` 语句（如 `@import './variables.css'`）。这些相对路径在浏览器中无法直接解析，因为CSS是通过 `<style>` 标签注入而非通过 `<link>` 加载。

`_rewriteRelativeCssImports()` 将相对路径的 `@import` 重写为 Jupyter 文件服务 URL：

```typescript
private _rewriteRelativeCssImports(css: string, path: string): string {
  const applicationBaseUrl = new URL(PageConfig.getBaseUrl(), window.location.href);
  const filesBaseUrl = new URL('files/', applicationBaseUrl);
  const baseDirectory = PathExt.dirname(path);

  return css.replace(
    /@import\s+(url\(\s*)?(["']?)([^"')\s;]+)\2\s*\)?/gi,
    (match, urlPrefix, quote, specifier) => {
      if (!this._isRelativeCssSpecifier(specifier)) {
        return match;  // 非相对路径保持不变
      }
      const resolvedPath = ContentUtils.normalizeContentsPath(
        PathExt.join(baseDirectory, specifier)
      );
      const routedSpecifier = new URL(encodeURI(resolvedPath), filesBaseUrl).toString();
      const normalizedQuote = quote || "'";
      if (urlPrefix) {
        return `@import ${urlPrefix}${normalizedQuote}${routedSpecifier}${normalizedQuote})`;
      }
      return `@import ${normalizedQuote}${routedSpecifier}${normalizedQuote}`;
    }
  );
}
```

**重写规则**：
- 基础URL：`{jupyterBaseUrl}files/`
- 相对路径解析为相对于当前CSS文件的路径
- 非相对路径（绝对路径、协议URL、`#`开头）保持不变
- 支持 `@import "file.css"`、`@import 'file.css'`、`@import url("file.css")`、`@import url('file.css')`、`@import url(file.css)` 等格式

**相对路径判定**（`_isRelativeCssSpecifier`）：以下情况视为非相对路径，不重写：
- 以 `/` 开头
- 以 `//` 开头（协议相对URL）
- 以 `#` 开头（ID选择器）
- 匹配协议模式 `[a-z][a-z0-9+.-]*:`（如 `http:`, `https:`, `data:`）

## 快照栈事务机制

多个插件可能加载同一个CSS文件（或不同插件加载的CSS有重叠），ImportResolver 通过快照栈实现CSS样式的事务管理。

### 数据结构

```typescript
// 静态：所有实例共享的样式元素映射
private static _localCssStyles = new Map<string, HTMLStyleElement>();

// 静态：每个路径的快照栈
private static _localCssSnapshotStacks = new Map<string, ILocalCssSnapshotEntry[]>();

// 静态：快照ID自增计数器
private static _nextLocalCssSnapshotId = 0;

// 实例：当前实例的快照ID
private readonly _localCssSnapshotId = ImportResolver._nextLocalCssSnapshotId++;

// 实例：当前实例的快照（路径→之前CSS内容）
private _localCssSnapshots = new Map<string, string | null>();

// 实例：当前实例已加载的样式路径
private _loadedLocalStylePaths = new Set<string>();

interface ILocalCssSnapshotEntry {
  id: number;        // 快照所属实例ID
  previousCss: string | null;  // 该层之前的CSS内容
}
```

### 保存快照（Snapshot）

加载CSS前，`_snapshotLocalStyle(path)` 保存当前状态：

```typescript
private _snapshotLocalStyle(path: string): void {
  if (this._localCssSnapshots.has(path)) return;  // 已快照，不重复

  const previousCss = ImportResolver._getCurrentLocalCss(path);
  this._localCssSnapshots.set(path, previousCss);

  const stack = ImportResolver._localCssSnapshotStacks.get(path) ?? [];
  stack.push({ id: this._localCssSnapshotId, previousCss });
  ImportResolver._localCssSnapshotStacks.set(path, stack);
}
```

栈结构示意（三个插件依次加载同一CSS）：

```
Stack for '/path/styles.css':
[2] → { id: plugin3, previousCss: ".plugin2 { color: red; }" }
[1] → { id: plugin2, previousCss: ".plugin1 { color: blue; }" }
[0] → { id: plugin1, previousCss: null }  ← 栈底，加载前为空
```

### 回滚（Rollback）

插件加载失败或停用时，`rollbackLocalStyleMutations()` 撤销该实例的样式变更：

```typescript
rollbackLocalStyleMutations(): void {
  for (const [path, previousCss] of this._localCssSnapshots) {
    const stack = ImportResolver._localCssSnapshotStacks.get(path);
    if (!stack) continue;

    const index = stack.findIndex(entry => entry.id === this._localCssSnapshotId);
    if (index === -1) continue;

    const isTopOfStack = index === stack.length - 1;
    if (isTopOfStack) {
      // 在栈顶：直接恢复
      this._restoreLocalStyle(path, previousCss);
    } else {
      // 不在栈顶（后续插件覆盖了）：将旧CSS传递给上一层
      stack[index + 1].previousCss = previousCss;
    }

    stack.splice(index, 1);
    if (stack.length === 0) {
      ImportResolver._localCssSnapshotStacks.delete(path);
    }
  }
  this._localCssSnapshots.clear();
  this._loadedLocalStylePaths.clear();
}
```

**回滚逻辑**：
- 如果快照在栈顶（最后加载该CSS的实例），直接恢复CSS内容
- 如果快照不在栈顶（后续有其他插件加载了同一路径），将保存的旧CSS传递给栈中下一个条目，确保最终回滚时能恢复到正确状态
- `_restoreLocalStyle`：previousCss为null时移除style元素，否则恢复textContent

### 提交（Commit）

插件成功加载后，`commitLocalStyleMutations()` 确认样式保留：

```typescript
commitLocalStyleMutations(): void {
  for (const path of this._localCssSnapshots.keys()) {
    const stack = ImportResolver._localCssSnapshotStacks.get(path);
    if (!stack) continue;

    const index = stack.findIndex(entry => entry.id === this._localCssSnapshotId);
    if (index === -1) continue;

    const isTopOfStack = index === stack.length - 1;
    if (isTopOfStack && index > 0) {
      // 在栈顶且不是栈底：更新前一条目的previousCss为当前CSS
      stack[index - 1].previousCss = ImportResolver._getCurrentLocalCss(path);
    }

    stack.splice(index, 1);
    if (stack.length === 0) {
      ImportResolver._localCssSnapshotStacks.delete(path);
    }
  }
  this._localCssSnapshots.clear();
}
```

提交操作将当前快照从栈中移除。如果在栈顶，需要将当前CSS状态传播给前一个条目（因为该条目回滚时需要恢复到提交后的状态，而非它加载时的状态）。

### 为什么需要栈结构

多个插件可能加载同一个CSS路径（例如从同一目录加载），后加载的插件会覆盖先加载的CSS内容。栈结构确保：

1. 后加载的插件回滚时，先加载插件的CSS能正确恢复
2. 先加载的插件回滚时（后加载的已提交），不会错误地清空样式
3. 支持任意顺序的加载和卸载

## package.json 声明的样式

除了相对导入CSS文件外，PluginLoader还通过 `_discoverDeclaredStyles()` 从 package.json 的 `style` 字段发现声明的CSS文件：

```typescript
// 查找package.json的style字段
const packageData = JSON.parse(packageJson);
const style = packageData.style;
if (typeof style === 'string' && style.endsWith('.css')) {
  const stylePath = PathExt.join(PathExt.dirname(packageJsonPath), style);
  return [stylePath];
}
```

这些声明的样式路径在 `PluginLoader.IResult.declaredStylePaths` 中返回，由PluginPlayground主类负责加载。

## 相关概念

- [模块解析系统](04-module-resolution.md)
- [插件加载流程](05-plugin-loader.md)
- [ImportResolver API 参考](../references/resolver-api.md)
