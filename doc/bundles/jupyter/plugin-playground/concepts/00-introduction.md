---
type: Concept
title: Plugin Playground 简介
description: Plugin Playground 是一个 JupyterLab 扩展，让你在浏览器中即时编写、运行和测试 JupyterLab 插件，无需构建步骤。
tags: [jupyterlab, plugin-playground, introduction, getting-started]
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

## 什么是 Plugin Playground

Plugin Playground（`@jupyterlab/plugin-playground`）是一个 JupyterLab 扩展，它在浏览器中提供了一个完整的插件开发环境。你可以直接在 JupyterLab 的代码编辑器中编写 TypeScript 插件代码，点击"Load Current File As Extension"按钮后，代码会在当前 JupyterLab 实例中即时转译并运行——无需本地构建环境、无需 `pip install`、无需重启 JupyterLab。

Plugin Playground 的核心价值在于消除了 JupyterLab 插件开发的"构建-安装-重启"循环。传统的 JupyterLab 插件开发需要配置 Node.js、TypeScript、webpack，每次修改后都要重新构建和安装。Plugin Playground 将这一过程缩短到几秒：在编辑器中写代码 → 点击运行 → 立即看到效果。

## 主要功能

Plugin Playground 提供以下功能：

- **即时加载**：将当前编辑器中的 TypeScript/JavaScript 文件作为 JupyterLab 插件加载运行
- **TypeScript 转译**：浏览器内实时 TypeScript→JavaScript 转译，支持 ES module 语法
- **自动补全**：编辑器中提供 JupyterLab 命令 ID 的自动补全
- **Extension Points 浏览器**：侧边栏面板展示所有可用的 Token（依赖注入标识）和命令 ID
- **示例浏览器**：内置扩展示例浏览和加载
- **已加载插件管理**：查看和停用当前通过 Playground 加载的插件
- **导出功能**：将插件导出为 `.zip` 文件夹或 Python `.whl` 包
- **分享链接**：通过 URL 分享插件代码
- **保存自动运行**：可选的"Run on save"模式，文件保存后自动重新加载
- **CDN 模块加载**：经用户同意后可从 CDN 加载第三方 AMD 模块

## 安装要求

Plugin Playground 作为 JupyterLab 扩展安装，要求：

- JupyterLab ^4.5.5
- 安装命令：`pip install jupyterlab-plugin-playground` 或通过 JupyterLab Extension Manager 安装

安装后，在命令面板（Ctrl+Shift+C / Cmd+Shift+C）中搜索"Plugin Playground"即可使用。

## 快速体验

安装后通过以下步骤创建你的第一个插件：

1. 打开命令面板，执行 "Plugin Playground: Start from File"
2. 系统会创建一个新的 `.ts` 文件，包含 Hello World 模板
3. 点击编辑器工具栏上的"运行"按钮（Run Tile 图标），或执行 "Load Current File As Extension" 命令
4. 插件立即生效——你会看到弹出 "Hello World!" 提示框

模板代码：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'hello-world:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    alert('Hello World!');
  },
};

export default plugin;
```

## 适用场景

Plugin Playground 适合以下场景：

- **学习 JupyterLab 扩展开发**：无需搭建构建环境即可快速实验
- **原型验证**：快速验证插件想法和 API 调用
- **API 探索**：通过 Extension Points 面板发现可用的 Token 和命令
- **教学演示**：在培训和演示中实时展示插件开发
- **Bug 复现**：创建最小复现案例分享给开发者

对于生产环境的插件发布，仍建议使用官方的扩展模板（`copier` template）进行完整的构建和打包。

## 相关概念

- [整体架构与数据流](/concepts/01-architecture-overview.md)
- [JupyterLab 插件基础结构](/concepts/02-plugin-basics.md)
- [Hello World 示例](/examples/01-hello-world.md)
- [源码索引](/references/source-index.md)
