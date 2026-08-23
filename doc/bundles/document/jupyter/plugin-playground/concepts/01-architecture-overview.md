---
type: Concept
title: 整体架构与数据流
description: Plugin Playground 的整体架构设计，从代码编辑到插件运行的完整数据流：编辑器→转译器→加载器→解析器→JupyterLab。
tags: [jupyterlab, plugin-playground, architecture, data-flow]
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
  - id: loader-api
    resource: /references/loader-transpiler-api.md
    title: PluginLoader 与 PluginTranspiler API 参考
  - id: resolver-api
    resource: /references/resolver-api.md
    title: ImportResolver API 参考
---

## 架构总览

Plugin Playground 的运行时架构由五个核心组件构成，它们协同工作实现"即写即运行"的插件开发体验。

```
┌─────────────────────────────────────────────────────────────┐
│                    JupyterLab FrontEnd                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Editor  │→ │PluginLoader  │→ │  Activated Plugin(s)  │  │
│  │ (CodeMirror)│ │              │  │  (IPlugin objects)    │  │
│  └──────────┘  │  ┌─────────┐ │  └───────────┬───────────┘  │
│     ↑  ↓       │  │Transpiler│ │              │              │
│  ┌──────────┐  │  └────┬────┘ │  ┌───────────▼───────────┐  │
│  │ Sidebars │  │       │      │  │  JupyterLab App       │  │
│  │ (Token/  │  │  ┌────▼────┐ │  │  (commands, shell,    │  │
│  │ Example/ │──┼→ │Resolver │ │  │   services, registry) │  │
│  │ Loaded)  │  │  └────┬────┘ │  └───────────────────────┘  │
│  └──────────┘  └───────┼──────┘                             │
│                        │                                     │
│     ┌──────────────────┼──────────────────────┐             │
│     ↓                  ↓                      ↓             │
│  Known Modules   Federated Exts      RequireJS (iframe)     │
│  (webpack        (window._JUPYTERLAB)  (CDN AMD modules)    │
│   dynamic                                         │         │
│   imports)                                        ↓         │
│                                          ContentUtils       │
│                                          (local files,      │
│                                           CSS injection)    │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件职责

### PluginTranspiler（转译器）

PluginTranspiler 是浏览器端的 TypeScript 转译器，负责将用户编写的 TypeScript/ES6+ 代码转换为可在沙箱中执行的 CommonJS 格式代码。

转译器执行三个关键转换：

1. **Default Export 检测**：验证代码中存在 `export default`（新风格插件必需）
2. **Require Await 化**：将所有 `require()` 调用包装为 `await require()`，使模块导入异步化
3. **Exports 包装**：创建 `exports = {}` 对象，在代码末尾添加 `return exports`，使转译后的代码可作为AsyncFunction执行

### ImportResolver（解析器）

ImportResolver 是模块解析的核心，负责处理转译后代码中的 `require()` 调用。它实现了一个四级回退解析策略链：

1. **已知模块（Runtime Known Module）**：优先从硬编码的已知模块列表和 webpack 共享作用域加载 JupyterLab/Lumino 核心包
2. **联邦扩展（Federated Extension）**：通过 `window._JUPYTERLAB` 访问已安装的其他 JupyterLab 扩展
3. **本地文件（Local File）**：解析相对路径导入，支持 `.ts`/`.tsx`/`.js`/`.css`/`.svg` 文件
4. **CDN AMD 模块**：经用户同意后通过隔离 iframe 中的 RequireJS 从 CDN 加载

此外，ImportResolver 还负责：
- CSS 样式的注入、快照、提交和回滚
- 相对路径 CSS `@import` 的 URL 重写
- 从 package.json 读取依赖版本范围用于 semver 匹配
- Token 感知的 Proxy 模块包装

### PluginLoader（加载器）

PluginLoader 是插件加载的协调者，它：

1. 调用 PluginTranspiler 转译代码
2. 处理转译失败的回退（旧风格对象插件）
3. 通过 AsyncFunction 或 Function 构造函数创建沙箱执行环境
4. 将 importFunction（即 ImportResolver.resolve）注入沙箱
5. 从执行结果中提取插件对象（`module.default`）
6. 解析插件 requires/optional 中的字符串 Token 名为 Token 实例
7. 自动发现 JSON schema 文件和声明的 CSS 样式

### ContentUtils（内容工具）

ContentUtils 封装了 Jupyter Contents API，提供：

- 文件/目录的读写操作（兼容 Jupyter Server 和 JupyterLite 的路径差异）
- Base64 解码和 JSON 解析
- 目录递归创建
- 剪贴板操作
- CodeMirror 编辑器行高亮
- 外部链接安全打开

### RequireJSLoader（RequireJS 隔离加载器）

RequireJS 在隐藏 iframe 中加载，避免污染全局 window 对象。iframe 不能从 DOM 中移除（否则 RequireJS 的定时器无法工作）。

## 数据流：一次插件加载的完整过程

当用户点击"Load Current File As Extension"时，数据流如下：

**步骤1：获取代码**
- 从当前编辑器 widget 获取源代码文本
- 获取当前文件路径作为 basePath

**步骤2：转译代码**
- `PluginTranspiler.transpile(code, true)` 将 TS 转为 CommonJS
- 三个 Transformer 依次处理：default export 检测 → require await 化 → exports 包装
- 若无 default export，捕获 NoDefaultExportError，回退到 `'use strict'; return (${code})` 模式

**步骤3：创建沙箱环境**
- transpiled 模式：`new AsyncFunction('require', code)(importFunction)`
- 回退模式：`new Function('require','requirejs','define', code)(requirejs.require, ...)`

**步骤4：执行与模块解析**
- 沙箱代码执行时遇到 `require('@jupyterlab/apputils')` 等调用
- ImportResolver.resolve() 按四级链查找模块
- 找到模块后通过 Proxy 包装，支持 Token 属性访问和默认导入合成

**步骤5：提取插件对象**
- transpiled 模式：从 `module.default` 获取插件源
- 回退模式：直接获取函数返回值
- 函数类型的插件源会被调用（支持插件工厂函数）
- Promise 会被 await
- 单个插件或插件数组都被规范化为数组

**步骤6：解析 Token 依赖**
- 遍历每个插件的 `requires` 和 `optional` 数组
- 字符串类型的依赖名通过 tokenMap 查找对应 Token 实例
- requires 中找不到的 Token 抛出错误
- optional 中找不到的 Token 仅打印警告并过滤

**步骤7：发现 schema 和样式**
- 从 basePath 向上查找 package.json
- 读取 jupyterlab.schemaDir 目录下的 JSON schema 文件
- 读取 package.json 的 style 字段声明的 CSS 文件
- 多插件场景下按插件 ID 后缀匹配 schema 文件

**步骤8：激活插件**
- 通过 app 注册并激活插件
- 样式通过 ImportResolver 的 CSS 管理机制注入
- 插件被添加到已加载插件列表（LoadedPluginsSidebar）

## 侧边栏与辅助UI

Plugin Playground 注册了三个右侧面板：

1. **Extension Points（TokenSidebar）**：展示所有可用 Token、命令、已知模块，支持搜索和一键插入 import 语句
2. **Extension Examples（ExampleSidebar）**：从 `extension-examples/` 目录发现示例文件，支持打开和查看 README
3. **Currently Loaded Plugins（LoadedPluginsSidebar）**：显示当前通过 Playground 加载的插件，支持停用

工具栏集成：
- Load As Extension 按钮（运行当前文件）
- Run on Save 开关（保存自动运行）
- Export 按钮（导出为 zip/wheel）
- Share 按钮（通过链接分享）

## 命令系统

Plugin Playground 注册了以下核心命令（CommandIDs 命名空间）：

| 命令 ID | 功能 |
|---------|------|
| `plugin-playground:load-as-extension` | 加载当前文件为插件 |
| `plugin-playground:create-new-plugin` | 创建新插件文件 |
| `plugin-playground:create-new-plugin-with-ai` | AI 辅助创建插件 |
| `plugin-playground:export-as-extension` | 导出插件为 zip/wheel |
| `plugin-playground:share-via-link` | 通过链接分享插件 |
| `plugin-playground:open-js-explorer` | 打开包参考浏览器 |
| `plugin-playground:list-tokens` | 列出可用 Token |
| `plugin-playground:list-commands` | 列出可用命令 |
| `plugin-playground:list-extension-examples` | 列出示例 |
| `plugin-playground:take-tour` | 启动新手引导 |

## 安全机制

Plugin Playground 包含多层安全机制：

- **CDN 同意弹窗**：首次从 CDN 加载外部模块时需用户明确同意
- **路径安全检查**：`ContentUtils.isSafeRelativePath()` 防止路径遍历攻击
- **iframe 隔离**：RequireJS 在隐藏 iframe 中运行，避免全局污染
- **本地路径规范化**：去除开头斜杠、尝试有/无斜杠两种路径格式

## 相关概念

- [Plugin Playground 简介](/concepts/00-introduction.md)
- [JupyterLab 插件基础结构](/concepts/02-plugin-basics.md)
- [TypeScript 转译机制](/concepts/03-typescript-transpilation.md)
- [模块解析系统](/concepts/04-module-resolution.md)
- [插件加载流程](/concepts/05-plugin-loader.md)
