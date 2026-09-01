---
type: Concept
title: 可插拔 Diff 系统
description: 按文件扩展名注册Diff Provider，内置Nbdime(Notebook)、ImageDiff(图片)、PlainTextDiff(文本回退)三种。
tags: [diff, diff-provider, nbdime, codemirror, notebook-diff, image-diff, pluggable]
generated:
  by: source-code-to-okf-wiki
  at: "2026-08-22T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-22T00:00:00Z"
status: stable
stale_after: "2027-08-22"
sources:
  - /references/model-ts-source.md
  - /references/index-ts-source.md
---

## Diff Provider 系统概述

jupyterlab-git 设计了一套可插拔的 Diff Provider（差异对比提供器）系统，允许不同类型的文件使用专门的可视化 Diff 组件进行差异对比，而非统一使用纯文本对比。该系统基于文件扩展名注册，支持第三方扩展注册自定义的 Diff Provider。

Diff Provider 的注册和查找逻辑在 `src/model.ts` 中实现，使用模块级别的全局注册表存储 Provider 映射。三个内置 Diff Provider 通过独立的 JupyterFrontEndPlugin 在激活时注册。

## DIFF_PROVIDERS 模块级注册表

Diff Provider 系统使用两个模块级变量存储注册表：

```typescript
const DIFF_PROVIDERS: {
  [key: string]: {
    name: string;
    factory: Git.Diff.Factory;
  };
} = {};

const FALLBACK_DIFF_PROVIDER: {
  factory: Git.Diff.Factory | null;
} = { factory: null };
```

- **DIFF_PROVIDERS**：按文件扩展名（如 `'.ipynb'`、`'.png'`）索引的专用 Provider 字典，键是文件扩展名（含点号小写），值包含 Provider 名称和工厂函数
- **FALLBACK_DIFF_PROVIDER**：全局唯一的回退 Provider，当文件没有匹配的专用 Provider 且被识别为文本文件时使用

这种模块级单例模式确保所有 `GitExtension` 实例共享同一份 Diff Provider 注册表。

## 注册 API

### registerDiffProvider()：注册专用 Provider

```typescript
registerDiffProvider(
  name: string,
  fileExtensions: string[],
  factory: Git.Diff.Factory
): void
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | `string` | Provider 的唯一名称，如 `'Nbdime'`、`'ImageDiff'` |
| `fileExtensions` | `string[]` | 绑定的文件扩展名列表，如 `['.ipynb']`、`['.jpeg', '.jpg', '.png']` |
| `factory` | `Git.Diff.Factory` | Diff Widget 工厂函数，接收 `IFactoryOptions` 返回 `IDiffWidget` |

该方法遍历 `fileExtensions`，将每个扩展名映射到 `DIFF_PROVIDERS` 字典中。如果同一扩展名被多次注册，后注册的会覆盖先前的。

### registerFallbackDiffProvider()：注册回退 Provider

```typescript
registerFallbackDiffProvider(factory: Git.Diff.Factory): void
```

注册全局唯一的文本回退 Provider。回退 Provider 不需要绑定文件扩展名，当文件没有专用 Provider 且被识别为文本文件（通过 `docRegistry` 判断）时自动使用。重复注册回退 Provider 会覆盖之前的。

## getDiffProvider()：Provider 查找逻辑

模块级函数 `getDiffProvider(filename, isText?)` 实现了 Provider 的查找逻辑：

```typescript
export function getDiffProvider(
  filename: string,
  isText?: boolean
): Git.Diff.Factory | null
```

### 查找流程

1. **提取文件扩展名**：从 `filename` 中提取扩展名（转为小写，含点号）
2. **查找专用 Provider**：在 `DIFF_PROVIDERS` 字典中按扩展名精确查找，若找到则返回对应的 `factory`
3. **回退到文本 Provider**：如果没有专用 Provider 匹配，且 `isText` 参数为 `true`（或内部通过 docRegistry 判断文件是文本类型），则返回 `FALLBACK_DIFF_PROVIDER.factory`
4. **无 Provider**：如果二进制文件没有专用 Provider，返回 `null`，此时前端显示 "Binary file not shown" 或不支持 Diff 的提示

### 调用示例

```typescript
// 在 GitExtension 中查找某个文件的 Diff Provider
const factory = getDiffProvider(filename, isTextFile);
if (factory) {
  const diffWidget = factory({
    currentRef,
    previousRef,
    baseRef,
    filename,
    repositoryPath,
    challenger,
    reference,
    base,
    trans,
    editorFactory?
  });
  // 显示 diffWidget
}
```

## 三种内置 Diff Provider

### Nbdime Provider（Notebook Diff）

- **注册名称**：`'Nbdime'`
- **文件扩展名**：`['.ipynb']`
- **注册插件**：`notebookDiffPlugin`（`@jupyterlab/git:notebook-diff`）
- **工厂函数**：`createNotebookDiff`
- **基础组件**：导出的 `NotebookDiff` 组件（`src/components/diff/NotebookDiff.tsx`）

Nbdime Provider 基于 nbdime 库实现 Jupyter Notebook（`.ipynb` 文件）的语义化 Diff。与纯文本 diff 不同，nbdime 理解 Notebook 的 JSON 结构（cell、metadata、output），能够：
- 识别 cell 的新增、删除、移动和修改
- 分别对比 cell 的输入（source）、输出（outputs）和元数据（metadata）
- 提供 Notebook 特有的 diff 视图（cell 级别、行级别的差异标记）
- 支持合并（merge）视图（nbdime 的 merge_notebooks 功能）

后端 `Git.changed_files()` 方法对 `.ipynb` 文件也使用 nbdime 进行语义化 diff 计算，而非标准的 `git diff` 文本比较。

**注册代码**：
```typescript
gitExtension.registerDiffProvider('Nbdime', ['.ipynb'], createNotebookDiff);
```

### ImageDiff Provider（图片 Diff）

- **注册名称**：`'ImageDiff'`
- **文件扩展名**：`['.jpeg', '.jpg', '.png']`
- **注册插件**：`imageDiffPlugin`（`@jupyterlab/git:image-diff`）
- **工厂函数**：`createImageDiff`

ImageDiff Provider 提供图片文件的可视化对比视图，允许用户直观地看到图片的变化。图片 Diff 通过 Git 内容端点（`/git/{path}/content`）获取两个版本的图片二进制数据（base64 编码），在浏览器中并排显示或叠加对比。

**注册代码**：
```typescript
gitExtension.registerDiffProvider('ImageDiff', ['.jpeg', '.jpg', '.png'], createImageDiff);
```

### PlainTextDiff Provider（纯文本回退）

- **注册类型**：Fallback Provider（回退）
- **注册插件**：`plainTextDiffPlugin`（`@jupyterlab/git:plain-text-diff`）
- **工厂函数**：`createPlainTextDiff`
- **基础组件**：导出的 `PlainTextDiff` 组件（`src/components/diff/PlainTextDiff.tsx`）

PlainTextDiff 是所有文本文件的默认回退 Diff Provider，基于 CodeMirror 编辑器实现内联（inline）或并排（side-by-side）的文本差异对比：

- 使用 CodeMirror 编辑器显示文件内容
- 通过 diff-match-patch 或类似算法计算行级别和字符级别的差异
- 支持语法高亮（通过 CodeMirror modes，根据文件类型自动选择）
- 支持合并冲突时的三方对比（base、reference、challenger）
- 提供增/删/改的行高亮标记

与 Nbdime 和 ImageDiff 不同，PlainTextDiff 通过 `registerFallbackDiffProvider()` 而非 `registerDiffProvider()` 注册，不绑定特定文件扩展名。

**注册代码**：
```typescript
gitExtension.registerFallbackDiffProvider(createPlainTextDiff);
```

## Git.Diff 命名空间接口

Diff 系统的核心类型定义在 `src/tokens.ts` 的 `Git.Diff` 命名空间中。

### Git.Diff.IModel：Diff 模型

```typescript
interface IModel {
  readonly challenger: IContent;    // 当前版本（挑战方）
  readonly reference: IContent;     // 参考版本（被比较方）
  readonly base?: IContent;         // 共同祖先版本（三方合并时）
  readonly filename: string;        // 文件名
  readonly changed: ISignal<IModel, IModelChange>;  // 内容变化信号
  readonly hasConflict: boolean;    // 是否存在合并冲突
}
```

### Git.Diff.IContent：Diff 内容

```typescript
interface IContent {
  readonly content: Promise<string>;  // 异步获取文件内容
  readonly label: string;             // 版本标签（如 "Working Directory"、"HEAD"）
  readonly source: SpecialRef;        // 引用来源
  readonly updateAt: number;          // 更新时间戳
}
```

### Git.Diff.IFactoryOptions：工厂选项

```typescript
interface IFactoryOptions {
  currentRef: SpecialRef;     // 当前版本引用
  previousRef: SpecialRef;    // 上一个版本引用
  baseRef?: SpecialRef;       // 基础版本引用（三方合并）
  filename: string;           // 文件名
  repositoryPath: string;     // 仓库根路径
  challenger: Git.Diff.IContent;
  reference: Git.Diff.IContent;
  base?: Git.Diff.IContent;
  trans?: TranslationBundle;  // 国际化翻译器
  editorFactory?: CodeEditor.Factory;  // 编辑器工厂
}
```

### Git.Diff.Factory：工厂函数类型

```typescript
type Factory = (options: IFactoryOptions) => IDiffWidget;
```

工厂函数接收 `IFactoryOptions`，返回一个实现 `IDiffWidget` 接口的 Widget 实例。

### Git.Diff.IDiffWidget：Diff Widget 接口

```typescript
interface IDiffWidget extends IDisposable {
  readonly model: IModel;                          // Diff 模型
  getResolvedFile(): Promise<string>;              // 获取合并解决后的文件内容
  readonly isFileResolved: boolean;                // 文件冲突是否已解决
  refresh(): Promise<void>;                        // 刷新 Diff 视图
}
```

所有 Diff Widget（NotebookDiff、PlainTextDiff、ImageDiff 以及第三方自定义 Widget）必须实现此接口，确保统一的行为契约。

## SpecialRef 枚举：特殊引用

```typescript
enum SpecialRef {
  WORKING,   // 工作区（当前未提交的更改）
  INDEX,     // 暂存区（已 git add 但未提交）
  BASE       // 共同祖先（三方合并时的 base 版本）
}
```

`SpecialRef` 枚举标识 Diff 内容的来源，在 `IFactoryOptions` 和 `IContent.source` 中使用，前端根据 ref 类型向后端 `/git/{path}/content` 端点请求对应版本的文件内容：
- `WORKING`：读取工作区文件
- `INDEX`：通过 `git show :filename` 获取暂存区版本
- `BASE`：通过 `git show HEAD:filename` 获取 HEAD 版本

## 第三方扩展自定义 Diff Provider

第三方 JupyterLab 扩展可以通过以下步骤注册自定义文件类型的 Diff Provider：

1. **依赖 IGitExtension Token**：在插件的 `requires` 中添加 `IGitExtension`
2. **在 activate 中注册**：调用 `gitExtension.registerDiffProvider()` 或 `registerFallbackDiffProvider()`

示例：

```typescript
const myCustomDiffPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:custom-diff',
  requires: [IGitExtension],
  autoStart: true,
  activate: (app: JupyterFrontEnd, gitExtension: IGitExtension) => {
    // 注册自定义文件类型的 Diff Provider
    gitExtension.registerDiffProvider(
      'MyCustomDiff',
      ['.myext', '.myformat'],
      (options) => new MyCustomDiffWidget(options)
    );
  }
};
```

自定义 Diff Widget 需要实现 `Git.Diff.IDiffWidget` 接口。这种机制使得 jupyterlab-git 的 Diff 能力可以无限扩展到任意文件类型。

## 相关概念

- [插件系统与五个Plugin](03-extension-plugin-system.md)
- [GitExtension核心模型](04-git-extension-model.md)
- [架构总览](02-architecture-overview.md)
- [REST API通信机制](05-rest-api-and-communication.md)
