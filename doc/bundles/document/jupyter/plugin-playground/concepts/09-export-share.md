---
type: Concept
title: 导出、分享与工具栏集成
description: Plugin Playground 的插件导出（zip/wheel）、链接分享、工具栏按钮集成、Run on Save、命令面板集成等高级功能。
tags: [jupyterlab, plugin-playground, export, share, toolbar, wheel, zip]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22T05:08:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-22T05:08:00Z
status: stable
stale_after: 2027-02-22
sources:
  - id: source-index
    resource: /references/source-index.md
    title: Plugin Playground 源码索引
---

## 工具栏集成

Plugin Playground 在文件编辑器（FileEditor）的工具栏中注册了四个按钮项，通过 `IToolbarWidgetRegistry.addFactory()` 实现：

### Load As Extension 按钮

工具栏项名称：`load-as-extension`

点击时执行 `plugin-playground:load-as-extension` 命令，加载当前编辑器文件为插件。图标使用 `runTileIcon`（运行图标）。

### Run on Save 开关

工具栏项名称：`plugin-playground-load-on-save`

这是一个复选框开关，标签为"Run on save"。启用后，每次文件保存成功时自动重新加载插件。

实现原理：
- 监听 `editorTracker.widgetAdded` 信号
- 对每个编辑器 widget 连接 `context.saveState` 信号
- 当 `saveState === 'completed'` 且该路径启用了"Run on save"时，自动调用 `_queuePluginLoad()`
- widget disposed 时断开信号连接，防止内存泄漏

开关状态存储在 JupyterLab 设置中，键为 `loadOnSave`。设置项 `commandInsertDefaultMode` 控制命令插入的默认模式（insert/nothing）。

### Export 按钮

工具栏项名称：`export-extension`（由 ExportToolbarController 管理）

提供导出下拉菜单，支持两种格式：
- **ZIP**：导出为文件夹压缩包，包含完整的插件文件结构
- **Wheel**：导出为 Python wheel 包（.whl），可通过 pip 安装

### Share 按钮

工具栏项名称：`share-via-link`（由 ShareViaLinkController 管理）

通过URL分享当前插件代码。点击后生成包含插件代码的分享链接，复制到剪贴板。

## 命令面板集成

Plugin Playground 在命令面板（Command Palette）中注册了以下命令，统一归类在"Plugin Playground"类别下：

| 命令 | 功能 |
|------|------|
| `plugin-playground:load-as-extension` | 加载当前文件为插件 |
| `plugin-playground:create-new-plugin` | 创建新的插件文件（Start from File） |
| `plugin-playground:create-new-plugin-with-ai` | AI辅助创建插件（Build with AI） |
| `plugin-playground:take-tour` | 启动新手引导 |
| `plugin-playground:export-as-extension` | 导出插件为zip/wheel |
| `plugin-playground:share-via-link` | 通过链接分享插件 |
| `plugin-playground:open-js-explorer` | 打开包参考浏览器 |

### 命令参数 Schema

多个命令通过 `describedBy` 声明了 JSON Schema 参数，支持从命令面板或程序化调用时传入参数：

**CREATE_PLUGIN_ARGS_SCHEMA**（创建插件）：
```json
{
  "type": "object",
  "properties": {
    "cwd": { "type": "string", "description": "工作目录" },
    "path": { "type": "string", "description": "文件路径，自动补.ts扩展名" }
  }
}
```

**EXPORT_AS_EXTENSION_ARGS_SCHEMA**（导出插件）：
```json
{
  "type": "object",
  "properties": {
    "path": { "type": "string", "description": "要导出的文件路径" },
    "format": { "type": "string", "enum": ["zip", "wheel"] }
  }
}
```

**LIST_QUERY_ARGS_SCHEMA**（列表查询命令）：
```json
{
  "type": "object",
  "properties": {
    "query": { "type": "string", "description": "过滤文本" }
  }
}
```

## 导出功能

### ZIP 导出

导出为标准ZIP压缩包，包含：
- 插件源代码文件（.ts/.js）
- package.json（从模板生成或使用现有文件）
- 相关的本地依赖文件（通过归档遍历收集）
- README.md（可选）

导出过程：
1. 确定要导出的根路径和文件列表
2. 排除特定目录：`.git`、`.ipynb_checkpoints`、`__pycache__`、`node_modules`
3. 并发读取文件内容（并发数为8）
4. 生成ZIP归档并触发浏览器下载

### Wheel 导出

导出为 Python wheel 包（.whl 文件），可直接通过 `pip install` 安装到 JupyterLab 环境。wheel 包由 `createPythonWheelArchive()` 函数生成，包含：
- 编译后的 JavaScript 文件
- 插件元数据
- JupyterLab 扩展安装配置

### 导出模板

`createTemplateArchive()` 创建标准的插件模板归档，包含必要的配置文件和目录结构。模板包含：
- package.json 模板
- tsconfig.json
- 插件入口文件模板

## 分享链接功能

ShareViaLinkController 提供通过URL分享插件的能力：

1. 将当前插件代码编码到URL参数中
2. 生成完整分享链接
3. 复制到剪贴板
4. 接收方打开URL时，Plugin Playground检测URL参数，自动加载代码到编辑器并显示加载提示

分享链接打开时，会显示一个浮动提示（`createFloatingUrlLoadHint`），提示用户点击"Load as Extension"运行。

## 侧边栏面板

Plugin Playground 在右侧添加了一个 SidePanel，包含三个折叠面板：

### Extension Points（Token 浏览器）

TokenSidebar 面板展示：
- 所有可用的 Token（可搜索过滤）
- 所有可用的命令 ID（可搜索过滤，显示label和caption）
- 所有已知模块（含文档和仓库链接）
- 每个命令的参数文档（usage和args schema）

支持的操作：
- 点击Token插入import语句到编辑器
- 点击命令插入命令执行代码
- 打开Token/模块的文档链接
- 切换命令插入模式（insert/nothing）

插入import语句由 `token-insertion.ts` 中的工具函数处理：
- `insertImportStatement()`：在编辑器中插入import语句
- `insertTokenDependency()`：在requires/optional数组中插入Token
- `findPluginActivateAppParameterName()`：找到activate函数的app参数名
- `ensurePluginActivateAppContext()`：确保activate函数有正确的参数

### Extension Examples（示例浏览器）

ExampleSidebar 面板从 `extension-examples/` 目录发现扩展示例文件：
- 读取示例目录列表
- 显示示例名称和描述
- 点击打开示例文件
- 支持打开示例的README

### Currently Loaded Plugins（已加载插件）

LoadedPluginsSidebar 面板显示当前通过Playground加载的插件：
- 列出已激活的插件ID
- 显示插件是否通过自动启动加载
- 支持停用（deactivate）已加载的插件

## 自动加载与队列

`_queuePluginLoad()` 方法管理插件加载队列：
- 加载前回滚之前的样式变更
- 执行加载流程
- 成功后提交样式变更
- 失败时回滚样式变更并显示错误
- 通过Notification系统显示加载结果通知

加载结果（IPluginLoadResult）包含：
- `status`：'loaded' | 'editor-not-active' | 'loading-failed' | 'autostart-failed'
- `ok`：是否成功
- `path`：加载的文件路径
- `pluginIds`：激活的插件ID列表
- `transpiled`：是否经过转译
- `skippedAutoStartPluginIds`：跳过自动启动的插件ID

## 列表查询命令

三个列表命令提供编程式查询接口：

- `listTokens`：返回可用Token列表，支持query过滤
- `listCommands`：返回可用命令列表，支持query过滤
- `listExtensionExamples`：返回扩展示例列表，支持query过滤

返回格式：
```typescript
{
  query: string;      // 查询文本
  total: number;      // 总数
  count: number;      // 过滤后数量
  items: T[];         // 结果项
}
```

这些命令可被其他扩展调用，用于发现可用的扩展点。

## 其他辅助功能

### 编辑器行高亮

ContentUtils.highlightEditorLines() 使用 CodeMirror 的 StateField 和 Decoration 实现代码行高亮：
- 通过 StateEffect 分发高亮位置
- Decoration.line 创建行背景装饰
- 超时（默认1200ms）后自动清除高亮
- 使用 WeakSet 和 WeakMap 管理编辑器状态和定时器

### URL布局控制

通过URL query参数 `hide` 控制界面元素隐藏：
- `?hide=all`：隐藏菜单和状态栏
- `?hide=menu`：仅隐藏菜单
- `?hide=statusbar`：仅隐藏状态栏

### 动态设置存储

动态设置（非schema定义的设置）存储在 sessionStorage 中，键前缀为 `plugin-playground:dynamic-settings:`。

### JupyterLite AI 集成

如果安装了 `@jupyterlite/ai` 扩展，Plugin Playground 提供"Build with AI"功能：
- 检查AI扩展可用性
- 打开AI聊天面板
- 如果AI provider未配置，显示设置提示
- AI不可用时显示安装提示

### 新手引导（Tour）

集成了 jupyterlab-tour 扩展提供新手引导：
- `hasPluginPlaygroundTourSupport()` 检测tour扩展是否可用
- `launchPluginPlaygroundTour()` 启动引导
- tour不可用时显示通知提示安装
- 默认禁用了 `jupyterlab-tour:default-tours`（在package.json的disabledExtensions中配置）

## 相关概念

- [整体架构与数据流](01-architecture-overview.md)
- [插件加载流程](05-plugin-loader.md)
- [样式处理与CSS隔离](08-style-handling.md)
- [自定义命令示例](../examples/03-custom-command.md)
