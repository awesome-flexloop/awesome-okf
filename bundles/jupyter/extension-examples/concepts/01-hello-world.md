---
type: Concept
title: Hello World：最小插件
description: 从最简单的hello-world示例入手，理解JupyterFrontEndPlugin对象结构和插件激活流程
tags: [jupyterlab, hello-world, minimal-plugin, JupyterFrontEndPlugin]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: hello-src
    resource: /references/plugin-anatomy.md
    title: hello-world/src/index.ts 最小插件源码
---

## 最小插件源码

hello-world 是所有示例的起点，整个插件只需要一个 `JupyterFrontEndPlugin` 对象：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab-examples/hello-world:plugin',
  description: 'Minimal JupyterLab extension.',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('The JupyterLab main application:', app);
  }
};

export default plugin;
```

这18行代码就是一个完整的JupyterLab扩展。

## 逐行解析

### 导入

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
```

- `JupyterFrontEnd`：JupyterLab前端应用类的类型注解
- `JupyterFrontEndPlugin<T>`：插件定义的泛型接口，类型参数 `T` 表示插件提供的服务类型（void表示不提供服务）

### 插件对象

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
```

定义一个遵循 `JupyterFrontEndPlugin` 接口的对象。`<void>` 表示此插件不通过 `provides` 导出任何Token供其他插件使用。

### id：插件唯一标识

```typescript
id: '@jupyterlab-examples/hello-world:plugin',
```

- 格式约定：`@scope/package-name:plugin-name`
- 必须全局唯一，用于设置系统、插件间依赖引用
- 多插件导出时每个插件需要不同id（如clap-button示例的`:pluginLab`和`:pluginNotebook`）

### description：描述

```typescript
description: 'Minimal JupyterLab extension.',
```

人类可读的插件描述，显示在扩展管理器中。

### autoStart：自动启动

```typescript
autoStart: true,
```

- `true`：JupyterLab启动时自动激活此插件
- `false`：仅当其他插件依赖它或用户手动激活时才加载

大多数扩展示例设置为 `autoStart: true`。

### activate：激活函数

```typescript
activate: (app: JupyterFrontEnd) => {
  console.log('The JupyterLab main application:', app);
}
```

这是插件的核心逻辑所在。当JupyterLab激活插件时调用此函数：

- 第一个参数始终是 `JupyterFrontEnd` 实例（即 `app`）
- 后续参数是 `requires`/`optional` 中声明的依赖，按顺序注入
- 在activate函数中执行命令注册、Widget创建、事件监听等初始化工作

hello-world的activate只是打印app对象到控制台——这是验证插件成功加载的最简单方式。

### 默认导出

```typescript
export default plugin;
```

**必须使用 `export default`**，JupyterLab通过默认导出发现插件对象。支持两种形式：

1. 单个插件：`export default plugin;`
2. 多个插件：`export default [plugin1, plugin2];`（如clap-button、metadata-form示例）

## 激活流程

JupyterLab启动时的插件激活顺序：

1. 加载所有已安装扩展的JavaScript模块
2. 构建依赖图（根据 `requires`/`optional`/`provides`）
3. 按拓扑排序激活插件（被依赖的先激活）
4. 对每个 `autoStart: true` 的插件，调用其 `activate` 函数
5. 等待所有activate完成后，JupyterLab界面就绪

## 验证插件加载

启动JupyterLab后：

1. 打开浏览器开发者工具（F12）
2. 切换到Console标签
3. 应能看到 `The JupyterLab main application:` 日志输出
4. 也可在命令面板搜索 "hello-world" 或查看扩展管理器

## 从Hello World进阶

hello-world演示了插件的骨架，但没有添加任何用户可见功能。后续示例在此基础上逐步增加：

| 增加内容 | 对应示例 |
|---------|---------|
| 注册命令 | commands |
| 添加到命令面板 | command-palette |
| 创建Widget | widgets |
| 添加到Launcher | launcher |
| 注册设置 | settings |

## 相关概念

- [JupyterLab扩展开发入门](/concepts/00-introduction.md)
- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [命令系统](/concepts/04-commands.md)
- [插件解剖结构参考](/references/plugin-anatomy.md)
