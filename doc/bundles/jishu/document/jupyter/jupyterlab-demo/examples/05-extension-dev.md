---
type: Example
title: "开发 JupyterLab 扩展入门"
description: "基于 cookiecutter 模板创建一个简单的 JupyterLab 扩展，从环境准备到构建安装的完整流程，理解扩展开发的基本模式"
tags: [extension-development, typescript, npm, cookiecutter, plugin, developer]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: narrative, resource: "/references/narrative-source.md", title: "Narrative演示脚本信源" }
---

# 开发 JupyterLab 扩展入门

jupyterlab-demo 展示了 JupyterLab 扩展的强大能力（fasta、geojson、bqplot 等）。本示例提供一个扩展开发的快速入门指南，帮助你创建自己的第一个 JupyterLab 扩展。

> 💡 **前置知识**：建议先阅读 [插件架构与扩展生态](../concepts/08-extension-demo.md) 理解扩展架构的核心概念。

## 前置条件

| 工具 | 版本 | 安装 |
|------|------|------|
| Node.js | 18+ | https://nodejs.org/ |
| npm/yarn | 最新 | 随 Node.js 安装 |
| Python | 3.8+ | 系统已有 |
| JupyterLab | 4.x | `pip install jupyterlab>=4` |
| cookiecutter | 最新 | `pip install cookiecutter` |

> ⚠️ **版本注意**：jupyterlab-demo 基于 JupyterLab 0.27（2017年），扩展API已有较大变化。本示例基于 JupyterLab 4.x 的现代扩展API（预构建扩展），与当前主流开发实践一致。

## 示例目标：创建一个"Hello World"命令面板扩展

我们将创建一个简单的扩展，在命令面板中添加一个"Say Hello"命令，点击后弹出提示框。这虽然简单，但涵盖了扩展开发的核心流程。

## 步骤一：使用 cookiecutter 创建扩展骨架

```bash
# 安装 cookiecutter（如果尚未安装）
pip install cookiecutter

# 使用官方模板创建扩展
cookiecutter https://github.com/jupyterlab/extension-cookiecutter-ts
```

模板会提示你输入以下信息：

| 提示 | 建议输入 | 说明 |
|------|---------|------|
| `author_name` | Your Name | 作者名 |
| `author_email` | you@example.com | 邮箱 |
| `labextension_name` | jupyterlab-hello-world | 扩展包名（npm包名） |
| `python_name` | jupyterlab_hello_world | Python包名 |
| `project_short_description` | A hello world JupyterLab extension | 描述 |
| `has_settings` | n | 是否有设置面板（初学时选no） |
| `has_binder` | n | 是否包含 Binder 配置 |
| `test` | n | 是否包含测试框架 |

执行后会生成 `jupyterlab-hello-world/` 目录，结构如下：

```
jupyterlab-hello-world/
├── package.json           # npm 包配置
├── pyproject.toml         # Python 包配置
├── tsconfig.json          # TypeScript 配置
├── src/
│   └── index.ts           # 扩展入口
└── ...
```

## 步骤二：理解生成的代码

打开 `src/index.ts`，查看生成的骨架代码：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Initialization data for the jupyterlab-hello-world extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-hello-world:plugin',
  description: 'A hello world JupyterLab extension.',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension jupyterlab-hello-world is activated!');
  }
};

export default plugin;
```

核心概念：
- **JupyterFrontEndPlugin**：插件对象，包含唯一 id 和 activate 函数
- **activate**：插件激活时执行的函数，接收 `app`（JupyterFrontEnd 实例）作为参数
- **autoStart: true**：JupyterLab 启动时自动激活此插件

## 步骤三：添加命令

修改 `src/index.ts`，在 activate 函数中添加一个命令：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-hello-world:plugin',
  description: 'A hello world JupyterLab extension.',
  autoStart: true,
  requires: [ICommandPalette],  // 声明依赖：命令面板
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('JupyterLab extension jupyterlab-hello-world is activated!');

    // 添加命令
    const commandId = 'hello-world:say-hello';
    app.commands.addCommand(commandId, {
      label: 'Say Hello',
      caption: 'Say Hello from my extension',
      execute: () => {
        alert('Hello from JupyterLab extension! 👋');
      }
    });

    // 将命令添加到命令面板
    palette.addItem({
      command: commandId,
      category: 'Hello World'
    });
  }
};

export default plugin;
```

关键变化：
1. **import ICommandPalette**：从 `@jupyterlab/apputils` 导入命令面板接口
2. **requires: [ICommandPalette]**：声明需要命令面板作为依赖，JupyterLab 会自动注入
3. **app.commands.addCommand**：注册命令，包含 label（显示名称）和 execute（执行函数）
4. **palette.addItem**：将命令添加到命令面板的指定分类下

## 步骤四：开发模式安装

在开发过程中，使用"开发模式"安装扩展，这样修改代码后可以实时看到效果：

```bash
cd jupyterlab-hello-world

# 安装 npm 依赖
npm install

# 以开发模式安装 Python 包
pip install -e .

# 链接 JupyterLab 前端扩展（开发模式）
jupyter labextension develop . --overwrite

# 启动 JupyterLab
jupyter lab
```

## 步骤五：测试扩展

1. 启动 JupyterLab 后，打开浏览器的开发者工具（F12）
2. 你应该在 Console 中看到：`JupyterLab extension jupyterlab-hello-world is activated!`
3. 按 **Ctrl/Cmd+Shift+C** 打开命令面板
4. 搜索 "Say Hello" 或 "Hello World"
5. 点击命令，应该弹出 "Hello from JupyterLab extension! 👋" 提示框

## 步骤六：添加更多功能（进阶）

### 添加键盘快捷键

```typescript
app.commands.addKeyBinding({
  command: commandId,
  keys: ['Accel Shift H'],
  selector: 'body'
});
```

现在按 Ctrl/Cmd+Shift+H 也能触发命令。

### 添加菜单项

```typescript
import { IMainMenu } from '@jupyterlab/mainmenu';

// 在 plugin 中添加 requires: [IMainMenu]
// activate 参数中添加 mainMenu: IMainMenu
const { commands } = app;
const helloMenu = [
  { command: commandId }
];
mainMenu.fileMenu.addGroup(helloMenu, 40);
```

### 添加一个侧边栏面板

```typescript
import { Widget } from '@lumino/widgets';

const helloWidget = new Widget();
helloWidget.node.textContent = 'Hello from sidebar!';
helloWidget.id = 'hello-world-widget';
helloWidget.title.label = 'Hello World';
helloWidget.title.closable = true;

app.shell.add(helloWidget, 'left', { rank: 700 });
```

### 添加新的文件查看器（参考 fasta 扩展）

```typescript
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';

// 为自定义 MIME 类型创建渲染器
const FACTORY = 'My Viewer';
const myFileType = {
  name: 'my-format',
  extensions: ['.myf'],
  mimeTypes: ['application/x-my-format'],
  icon: '📄'
};

app.docRegistry.addFileType(myFileType);
app.docRegistry.addWidgetFactory({
  name: FACTORY,
  fileTypes: ['my-format'],
  defaultFor: ['my-format'],
  createNew: (context) => new MyViewerWidget(context)
});
```

## 步骤七：构建和发布

### 构建生产版本

```bash
# Python 包构建
pip install build
python -m build

# 这会生成 dist/ 目录下的 .whl 和 .tar.gz
```

### 本地安装测试

```bash
pip install dist/jupyterlab_hello_world-0.1.0-py3-none-any.whl
```

### 发布到 PyPI

```bash
pip install twine
twine upload dist/*
```

用户安装你的扩展只需：
```bash
pip install jupyterlab-hello-world
```

JupyterLab 4.x 的预构建扩展（prebuilt extension）安装后无需重建，直接生效。

## 从简单到复杂：学习路径

| 阶段 | 项目类型 | 参考项目 |
|------|---------|---------|
| 入门 | 命令面板/快捷键/菜单项 | 本示例 |
| 初级 | 侧边栏面板/状态栏组件 | jupyterlab-toc |
| 中级 | 文件查看器/渲染器 | jupyterlab-fasta、jupyterlab-geojson |
| 高级 | Notebook增强/自定义Widget | bqplot、ipyleaflet |
| 专家 | 新的文档类型/完整应用 | jupyterlab-drawio、jupyterlab-git |

## 学习资源

| 资源 | 链接 |
|------|------|
| JupyterLab 扩展开发官方文档 | https://jupyterlab.readthedocs.io/en/latest/extension/ |
| 扩展示例仓库 | https://github.com/jupyterlab/extension-examples |
| Lumino 文档 | https://lumino.readthedocs.io/ |
| JupyterLab Discourse | https://discourse.jupyter.org/ |
| Extension Cookiecutter | https://github.com/jupyterlab/extension-cookiecutter-ts |

## 核心 API 速查

| 你想做什么 | API | 包 |
|-----------|-----|-----|
| 添加命令 | `app.commands.addCommand()` | `@jupyterlab/application` |
| 添加命令面板项 | `palette.addItem()` | `@jupyterlab/apputils` |
| 添加键盘快捷键 | `app.commands.addKeyBinding()` | `@jupyterlab/application` |
| 添加菜单 | `mainMenu.*Menu.addGroup()` | `@jupyterlab/mainmenu` |
| 添加侧边栏 | `app.shell.add(widget, 'left')` | `@jupyterlab/application` |
| 添加文件类型 | `app.docRegistry.addFileType()` | `@jupyterlab/docregistry` |
| 添加文件查看器 | `app.docRegistry.addWidgetFactory()` | `@jupyterlab/docregistry` |
| 添加MIME渲染器 | `rendermime.addFactory()` | `@jupyterlab/rendermime` |
| 创建Widget | `new Widget()` (Lumino) | `@lumino/widgets` |

## 相关概念

- [插件架构与扩展生态](../concepts/08-extension-demo.md)
- [工作区布局与交互体验设计](../concepts/07-workspace-layout.md)
- [为演示添加自定义内容](04-add-demo-content.md)
