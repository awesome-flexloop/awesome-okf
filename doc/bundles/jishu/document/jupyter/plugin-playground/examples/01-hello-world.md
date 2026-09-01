---
type: Example
title: 最小插件示例 - Hello World
description: 从零开始创建一个最简单的 JupyterLab 插件，在激活时弹出 Hello World 通知。展示插件的基本结构和最小代码量。
tags: [jupyterlab, plugin-playground, hello-world, minimal, getting-started]
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
related:
  - id: plugin-basics
    resource: /concepts/02-plugin-basics.md
    title: JupyterLab 插件基础结构
  - id: plugin-loader
    resource: /concepts/05-plugin-loader.md
    title: 插件加载流程
---

## 示例说明

这是最小化的 JupyterLab 插件示例，代码量不到20行。插件加载后在通知中心弹出 "Hello, Plugin Playground!" 消息。

## 完整代码

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'hello-world:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    app.commands.addCommand('hello-world:greet', {
      label: 'Say Hello',
      execute: () => {
        alert('Hello, Plugin Playground!');
      }
    });

    console.log('Hello World plugin activated!');
  }
};

export default plugin;
```

## 逐步解析

### 1. 导入核心类型

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
```

- `JupyterFrontEnd`：JupyterLab 前端应用的基类类型，提供对 commands、shell、serviceManager 等核心服务的访问
- `JupyterFrontEndPlugin<T>`：插件对象的类型，泛型 T 是 provides 服务的类型（无提供时用 `void`）

这两个类型会在转译时被擦除（类型导入），不会产生运行时代码。

### 2. 定义插件对象

```typescript
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'hello-world:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => { ... }
};
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `id` | `'hello-world:plugin'` | 插件唯一标识，建议格式 `'命名空间:插件名'` |
| `autoStart` | `true` | 应用加载后自动激活，无需其他插件依赖 |
| `activate` | 函数 | 插件激活时执行的回调 |

### 3. activate 函数

```typescript
activate: (app: JupyterFrontEnd) => {
  app.commands.addCommand('hello-world:greet', {
    label: 'Say Hello',
    execute: () => {
      alert('Hello, Plugin Playground!');
    }
  });
  console.log('Hello World plugin activated!');
}
```

activate 接收 JupyterFrontEnd 实例作为第一个参数。在函数内：
- `app.commands.addCommand()` 注册一个命令，id 为 `'hello-world:greet'`
- 命令有 label（命令面板中显示的名称）和 execute（执行时调用的函数）
- `console.log` 输出确认插件已激活

### 4. 导出插件

```typescript
export default plugin;
```

`export default` 是**必须的**。PluginLoader 会从 `module.default` 提取插件对象。没有 default export 会触发转译失败回退，旧格式下需要直接返回插件对象而非使用export。

## 在 Plugin Playground 中运行

1. 打开 JupyterLab，创建一个新文件（File → New → Text File），重命名为 `hello-world.ts`
2. 确保文件类型被识别为 TypeScript（右下角语言模式选择 TypeScript）
3. 将上面的代码粘贴到编辑器中
4. 点击工具栏中的 **▶ Load As Extension** 按钮
5. 打开浏览器控制台（F12），应看到 "Hello World plugin activated!"
6. 打开命令面板（Ctrl+Shift+C），搜索 "Say Hello" 并执行，应弹出 alert 对话框

## 常见错误排查

### "No default export found"

**原因**：代码中没有 `export default plugin;` 语句。

**解决**：确保最后有 `export default plugin;`。如果你不想用 export 语法，也可以直接写插件对象（不赋值给变量、不用export），PluginLoader 会通过旧格式回退处理：

```typescript
// 旧格式（不推荐但有效）：
({
  id: 'hello-world:plugin',
  autoStart: true,
  activate: (app) => {
    console.log('Hello!');
  }
})
```

注意旧格式需要用括号包裹对象字面量，否则 JavaScript 引擎会将花括号解析为代码块而非对象。

### "Required token ... not found"

**原因**：requires 中使用了不存在的 Token 名。

**解决**：在 Hello World 示例中不要添加 requires，确保可以独立运行。

### 插件加载成功但没有反应

**原因**：`autoStart` 设置为 `false` 或插件被其他插件依赖才会激活。

**解决**：确保 `autoStart: true`，这样插件会在应用加载完成后自动激活。

## 扩展练习

1. 将 `alert()` 改为使用 JupyterLab 的通知系统：
```typescript
import { Notification } from '@jupyterlab/apputils';
// 然后在 activate 中：
Notification.success('Hello, Plugin Playground!', { autoClose: 3000 });
```

2. 添加命令到命令面板分类：
```typescript
// 需要 ICommandPalette
requires: ['@jupyterlab/apputils:ICommandPalette'],
activate: (app, palette) => {
  // ...注册命令后：
  palette.addItem({ command: 'hello-world:greet', category: 'Hello World' });
}
```

## 预期结果

- ✅ 工具栏点击 Load 后无错误
- ✅ 控制台输出 "Hello World plugin activated!"
- ✅ 命令面板中可找到 "Say Hello" 命令
- ✅ 执行命令弹出 alert 对话框
