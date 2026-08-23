---
type: Example
title: 示例1：Hello World插件
description: 从零创建一个最小的JupyterLab扩展，理解插件的基本结构和生命周期
tags: [example, hello-world, minimal, getting-started]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
status: stable
sources:
  - id: hello-world-src
    resource: /references/plugin-anatomy.md
    title: hello-world/src/index.ts
---

## 目标

创建一个最简单的JupyterLab扩展，加载时在Console输出消息。通过此示例理解插件的基本结构。

## 前置知识

- [Hello World入门](/concepts/01-hello-world.md)
- [项目结构与构建系统](/concepts/02-project-setup.md)
- [插件基础与依赖注入](/concepts/03-plugin-basics.md)

## 步骤

### 1. 创建项目（使用copier模板）

```bash
pip install copier jinja2-time
copier copy https://github.com/jupyterlab/extension-template .
```

按提示输入：
- extension_name: `hello-world`
- author_name: `Your Name`
- author_email: `you@example.com`
- 其他选项保持默认

### 2. 修改src/index.ts

替换为最小插件定义：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/hello-world:plugin',
  description: 'Minimal Hello World extension.',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension hello-world is activated!');
  }
};

export default plugin;
```

### 3. 构建并安装

```bash
pip install -e .
jlpm install
jlpm build
jupyter labextension develop . --overwrite
```

### 4. 运行验证

```bash
jupyter lab
```

打开JupyterLab后，按F12打开浏览器开发者工具，在Console中应看到：

```
JupyterLab extension hello-world is activated!
```

## 代码解释

| 代码 | 说明 |
|------|------|
| `id: '@jupyterlab-examples/hello-world:plugin'` | 插件唯一ID，格式为`npm包名:插件名` |
| `autoStart: true` | JupyterLab启动时自动激活（无需用户手动开启） |
| `activate(app)` | 激活函数，接收JupyterFrontEnd实例作为第一个参数 |
| `console.log(...)` | 在浏览器控制台输出消息（最简单的"效果"） |
| `export default plugin` | 默认导出插件对象，JupyterLab通过此入口加载 |

## 关键点

1. 插件是一个实现 `JupyterFrontEndPlugin<T>` 接口的对象
2. `activate` 函数是插件的入口点
3. 没有依赖注入（requires/optional为空），所以activate只接收app参数
4. 没有 `provides`，所以不提供Token给其他扩展使用
5. `void` 泛型参数表示不返回任何值

## 扩展练习

尝试以下修改：
1. 在activate中添加 `alert('Hello World!')`（注意：仅用于调试，生产代码避免使用alert）
2. 添加 `requires: [ICommandPalette]` 并注册一个命令到面板（参考[示例2：添加命令和面板入口](02-commands-palette.md)）
3. 修改 `description` 字段，在Extension Manager中查看效果

## 相关概念

- [Hello World入门](/concepts/01-hello-world.md)
- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [插件解剖参考](/references/plugin-anatomy.md)
