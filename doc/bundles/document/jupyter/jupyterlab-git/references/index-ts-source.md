---
type: Reference
title: 插件入口 src/index.ts
description: jupyterlab-git 前端插件入口，注册5个JupyterFrontEndPlugin并完成activate生命周期
tags: [frontend, plugin, entrypoint, activation]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: src-index
    resource: /references/index-ts-source.md
    title: "src/index.ts 源码分析"
---

# 插件入口 src/index.ts

## 文件位置

`src/index.ts` 是 jupyterlab-git 前端扩展的入口文件，位于 npm 包 `@jupyterlab/git` 的源码根目录。

## 导出的插件列表

文件默认导出一个包含5个 `JupyterFrontEndPlugin` 的数组：

| 插件 | ID | 类型 | 说明 |
|------|-----|------|------|
| `plugin` | `@jupyterlab/git:plugin` | `IGitExtension` | 主插件，提供 GitExtension 实例 |
| `gitCloneCommandPlugin` | （在cloneCommand.tsx中定义） | `void` | Git 克隆对话框命令插件 |
| `notebookDiffPlugin` | `@jupyterlab/git:notebook-diff` | `void` | 注册 nbdime Notebook diff provider |
| `imageDiffPlugin` | `@jupyterlab/git:image-diff` | `void` | 注册图片 diff provider（.jpeg/.jpg/.png） |
| `plainTextDiffPlugin` | `@jupyterlab/git:plain-text-diff` | `void` | 注册纯文本回退 diff provider |

## 主插件 activate 函数

`activate` 函数是主插件的生命周期入口，签名：

```typescript
async function activate(
  app: JupyterFrontEnd,
  restorer: ILayoutRestorer,
  editorServices: IEditorServices,
  fileBrowser: IDefaultFileBrowser,
  settingRegistry: ISettingRegistry,
  docmanager: IDocumentManager,
  mainMenu: IMainMenu | null,
  statusBar: IStatusBar | null,
  palette: ICommandPalette | null,
  translator: ITranslator | null
): Promise<IGitExtension>
```

### 必需依赖（requires）

- `ILayoutRestorer` - 布局恢复
- `IEditorServices` - 编辑器服务（用于diff视图）
- `IDefaultFileBrowser` - 默认文件浏览器（注意：显式使用default而非current，避免第三方Drive冲突）
- `ISettingRegistry` - 设置注册表
- `IDocumentManager` - 文档管理器

### 可选依赖（optional）

- `IMainMenu` - 主菜单
- `IStatusBar` - 状态栏
- `ICommandPalette` - 命令面板
- `ITranslator` - 国际化翻译

## activate 执行流程

1. **加载设置**：通过 `settingRegistry.load(plugin.id)` 加载插件设置
2. **设置迁移**：将旧版 `doubleClickDiff` 布尔设置迁移为 `fileClickAction` 枚举
3. **获取服务端设置**：调用 `getServerSettings()` 获取版本信息并验证
   - 验证 git 版本 ≥ 2
   - 验证前后端版本一致
4. **创建 GitExtension 模型**：`new GitExtension(docmanager, app.docRegistry, settings, serverSettings)`
5. **路径同步**：监听文件浏览器路径变化，同步 `pathRepository`
6. **事件连接**：
   - `fileBrowser.model.pathChanged` → 更新仓库路径
   - `gitExtension.headChanged` → 刷新文件浏览器
   - `app.serviceManager.contents.fileChanged` → 刷新Git状态
7. **UI创建**（当settings加载成功时）：
   - 调用 `addCommands()` 注册所有命令
   - 创建 `GitWidget` 并添加到左侧面板（rank: 200）
   - 添加命令面板项
   - 通过 `restorer.add()` 注册布局恢复
   - 添加Git菜单（JLab < 3.1时）
   - 添加状态栏widget
   - 添加文件浏览器右键菜单

## Diff Provider 注册机制

三个diff插件通过 `registerDiffProvider` 和 `registerFallbackDiffProvider` 注册：

```typescript
// Notebook diff（.ipynb）— 基于nbdime
gitExtension.registerDiffProvider('Nbdime', ['.ipynb'], createNotebookDiff);

// 图片 diff（.jpeg/.jpg/.png）
gitExtension.registerDiffProvider('ImageDiff', ['.jpeg', '.jpg', '.png'], createImageDiff);

// 纯文本回退 diff（CodeMirror）— 所有文本文件
gitExtension.registerFallbackDiffProvider(createPlainTextDiff);
```

## 版本校验

activate 中执行严格的版本校验：

```typescript
if (frontendVersion && frontendVersion !== serverVersion) {
  throw new Error('前端版本与Python包版本不匹配');
}
```

这确保了前后端API兼容性。

## 重新导出

文件重新导出了以下公共API：

```typescript
export { DiffModel } from './components/diff/model';
export { NotebookDiff } from './components/diff/NotebookDiff';
export { PlainTextDiff } from './components/diff/PlainTextDiff';
export { Git, IGitExtension } from './tokens';
```

## 相关概念

- [GitExtension核心模型](../concepts/04-git-extension-model.md)
- [可插拔Diff系统](../concepts/06-diff-provider-system.md)
- [命令系统与菜单](../concepts/10-commands-and-menu.md)
- [插件系统与五个Plugin](../concepts/03-extension-plugin-system.md)
