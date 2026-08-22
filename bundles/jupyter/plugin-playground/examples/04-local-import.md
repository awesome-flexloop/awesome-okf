---
type: Example
title: 本地模块导入与CSS样式
description: 演示如何在Plugin Playground中创建多文件插件，包含相对路径导入的TypeScript模块和CSS样式文件，以及CSS @import链的处理。
tags: [jupyterlab, plugin-playground, import, css, local-module, multi-file]
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
  - id: style-handling
    resource: /concepts/08-style-handling.md
    title: 样式处理与CSS隔离
related:
  - id: module-resolution
    resource: /concepts/04-module-resolution.md
    title: 模块解析系统
  - id: style-handling
    resource: /concepts/08-style-handling.md
    title: 样式处理与CSS隔离
---

## 示例说明

本示例演示多文件插件开发：
1. 主插件文件 `my-extension/index.ts`
2. 工具模块 `my-extension/utils.ts`
3. 组件模块 `my-extension/widget.tsx`
4. CSS样式 `my-extension/style.css`
5. 嵌套CSS `my-extension/theme.css`（被style.css @import）

展示了相对路径导入、CSS样式注入、@import重写等机制。

## 文件结构

在JupyterLab文件浏览器中创建以下目录和文件：

```
my-extension/
├── index.ts       # 主插件入口
├── utils.ts       # 工具函数模块
├── widget.tsx     # Widget组件模块
├── style.css      # 主样式文件
└── theme.css      # 主题变量（被style.css导入）
```

## 文件1: my-extension/utils.ts（工具模块）

```typescript
/**
 * 工具函数模块 - 提供格式化和日志工具
 */

export function formatMessage(name: string, message: string): string {
  const timestamp = new Date().toLocaleTimeString();
  return `[${timestamp}] ${name}: ${message}`;
}

export function logWithPrefix(prefix: string, ...args: any[]): void {
  console.log(`[${prefix}]`, ...args);
}

export function createId(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).substring(2, 9)}`;
}

// 默认导出
export default {
  formatMessage,
  logWithPrefix,
  createId
};
```

## 文件2: my-extension/theme.css（主题变量）

```css
/* 主题CSS变量 */
:root {
  --myext-primary: #673ab7;
  --myext-primary-light: #9575cd;
  --myext-bg: #f5f0ff;
  --myext-text: #333;
  --myext-border-radius: 8px;
  --myext-shadow: 0 2px 8px rgba(103, 58, 183, 0.2);
}
```

## 文件3: my-extension/style.css（主样式）

```css
/* 主样式文件 - 通过@import引入主题变量 */
@import './theme.css';

.my-extension-panel {
  background: var(--myext-bg);
  color: var(--myext-text);
  border-radius: var(--myext-border-radius);
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.my-extension-panel h2 {
  color: var(--myext-primary);
  margin-top: 0;
  border-bottom: 2px solid var(--myext-primary-light);
  padding-bottom: 8px;
}

.my-extension-panel .info-box {
  background: white;
  border-left: 4px solid var(--myext-primary);
  padding: 12px 16px;
  margin: 12px 0;
  border-radius: 4px;
  box-shadow: var(--myext-shadow);
}

.my-extension-panel .log-area {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  max-height: 200px;
  overflow-y: auto;
  margin: 12px 0;
}

.my-extension-panel .log-area .log-entry {
  padding: 2px 0;
  border-bottom: 1px solid #333;
}

.my-extension-panel .log-area .log-entry:last-child {
  border-bottom: none;
}

.my-extension-panel button {
  background: var(--myext-primary);
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 8px;
  transition: background 0.2s;
}

.my-extension-panel button:hover {
  background: var(--myext-primary-light);
}
```

## 文件4: my-extension/widget.tsx（Widget模块）

```typescript
/**
 * Widget模块 - 自定义面板组件
 */
import { ReactWidget } from '@jupyterlab/apputils';
import React from 'react';
import { formatMessage, createId } from './utils';
import './style.css';

interface ILogEntry {
  id: string;
  text: string;
}

export class MyExtensionWidget extends ReactWidget {
  private _logs: ILogEntry[] = [];

  constructor() {
    super();
    this.addClass('my-extension-widget');
    // 初始日志
    this._logs.push({
      id: createId('log'),
      text: formatMessage('System', 'Widget initialized')
    });
  }

  addLog(message: string): void {
    this._logs.push({
      id: createId('log'),
      text: message
    });
    if (this._logs.length > 50) {
      this._logs.shift();
    }
    this.update();
  }

  render(): JSX.Element {
    return React.createElement(
      'div',
      { className: 'my-extension-panel' },
      React.createElement('h2', { key: 'title' }, '🔌 我的扩展面板'),
      React.createElement(
        'div',
        { className: 'info-box', key: 'info' },
        '这是一个多文件插件示例，演示了本地模块导入和CSS样式注入。'
      ),
      React.createElement(
        'div',
        { key: 'actions' },
        React.createElement(
          'button',
          {
            key: 'btn-log',
            onClick: () => {
              this.addLog(formatMessage('User', `Clicked at ${Date.now()}`));
            }
          },
          '添加日志'
        ),
        React.createElement(
          'button',
          {
            key: 'btn-clear',
            onClick: () => {
              this._logs = [];
              this.addLog(formatMessage('System', 'Logs cleared'));
            },
            style: { background: '#e53935' }
          },
          '清空日志'
        )
      ),
      React.createElement(
        'div',
        { className: 'log-area', key: 'logs' },
        this._logs.map(log =>
          React.createElement(
            'div',
            { className: 'log-entry', key: log.id },
            log.text
          )
        )
      )
    );
  }
}
```

## 文件5: my-extension/index.ts（主插件入口）

```typescript
/**
 * 主插件入口 - 多文件插件示例
 */
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { logWithPrefix } from './utils';
import { MyExtensionWidget } from './widget';
import './style.css';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    const LOG = 'MyExtension';
    let mainWidget: MainAreaWidget<MyExtensionWidget> | null = null;

    // 注册打开面板命令
    const command = 'my-extension:open';
    app.commands.addCommand(command, {
      label: '打开我的扩展面板',
      caption: '打开多文件扩展示例面板',
      execute: () => {
        if (mainWidget && !mainWidget.isDisposed) {
          app.shell.activateById(mainWidget.id);
          mainWidget.content.addLog('面板已激活');
          return;
        }

        const content = new MyExtensionWidget();
        mainWidget = new MainAreaWidget({ content });
        mainWidget.id = 'my-extension-main';
        mainWidget.title.label = '我的扩展';
        mainWidget.title.closable = true;
        mainWidget.disposed.connect(() => {
          mainWidget = null;
        });
        app.shell.add(mainWidget, 'main');
        app.shell.activateById(mainWidget.id);

        content.addLog('面板已创建并激活');
        logWithPrefix(LOG, 'Panel opened');
      }
    });

    palette.addItem({ command, category: 'My Extension' });
    logWithPrefix(LOG, 'Plugin activated successfully');
  }
};

export default plugin;
```

## 关键机制解析

### 1. 相对路径导入解析

当代码中出现 `import { something } from './utils'` 时，ImportResolver 的处理流程：

1. 检测到以 `.` 开头的路径（相对路径）
2. 基于 basePath（当前文件所在目录）解析完整路径
3. 如果路径指向目录，尝试加载 `index.ts`/`index.js`/`index.json`
4. 自动补全扩展名（.ts → .js → 无扩展名）
5. 通过Jupyter内容服务（`IContentsManager`）读取文件
6. 如果是 `.ts`/`.js` 文件，调用 PluginLoader.loadFile() 转译并执行
7. 返回模块的 exports 对象

### 2. CSS 文件导入

当代码中出现 `import './style.css'` 时：

1. ImportResolver 检测到 `.css` 扩展名
2. 通过Jupyter内容服务读取CSS文件内容
3. 调用 `_snapshotLocalStyle(path)` 保存样式快照
4. 调用 `_rewriteRelativeCssImports()` 重写 `@import './theme.css'` 为绝对URL
5. 创建或复用 `<style>` 元素，设置CSS内容
6. CSS样式立即生效（注入到 document.head）
7. 返回 `{ default: path }` 作为模块导出

### 3. CSS @import 链处理

`style.css` 中的 `@import './theme.css'` 被重写为：

```css
@import 'http://localhost:8888/files/path/to/my-extension/theme.css';
```

重写基于：
- JupyterLab base URL
- `files/` 路径前缀（Jupyter文件服务路由）
- 相对于当前CSS文件的目录解析
- 只重写相对路径的 @import，绝对URL保持不变

### 4. 跨文件CSS import

注意：CSS `@import` 在浏览器中是原生支持的，但 `<style>` 标签中的相对路径@import无法正确解析。Plugin Playground 通过重写为绝对URL解决了这个问题。

但对于嵌套的 @import（theme.css 中再 @import 其他CSS），由于重写后的URL是Jupyter文件服务的绝对路径，浏览器会正确处理后续的相对路径解析（相对于被import的CSS的URL路径）。

### 5. basePath 的作用

basePath 是主入口文件所在的目录路径。所有相对导入都基于此路径解析。ImportResolver 在创建时接收 basePath，用于：
- 解析相对模块路径（./utils → /path/to/utils.ts）
- 查找最近的 package.json（用于版本范围协商）
- 解析CSS文件的相对路径
- 查找 schema 目录和声明的样式

## 运行步骤

1. 在JupyterLab中创建目录 `my-extension/`
2. 依次创建上述5个文件，确保编码为UTF-8
3. 打开 `my-extension/index.ts` 文件
4. 点击工具栏 **Load As Extension**
5. 打开命令面板，搜索 "我的扩展" → 执行"打开我的扩展面板"
6. 观察：
   - 面板打开，紫色主题样式生效
   - CSS变量正确应用（紫色主色调）
   - 点击"添加日志"按钮在黑色日志区域添加日志
   - 控制台输出 `[MyExtension] Plugin activated successfully`

## 常见问题

### 文件找不到 (404)

**原因**：相对路径解析错误或文件不存在。

**排查**：
1. 确认所有文件在JupyterLab文件浏览器中可见
2. 确认相对路径正确（注意 `./` 和 `../`）
3. 打开浏览器控制台，查看Network标签中失败的请求
4. 文件编码必须是UTF-8

### CSS样式不生效

**原因**：
1. CSS选择器优先级不够（被JupyterLab默认样式覆盖）
2. CSS文件路径错误
3. 插件加载失败导致CSS未注入

**解决**：
1. 使用浏览器DevTools检查元素，确认style标签是否存在（查找 `data-plugin-playground-style-path` 属性）
2. 使用更具体的CSS选择器
3. 使用CSS变量确保主题一致性

### TypeScript 转译错误

**原因**：导入的模块有语法错误。

**解决**：
1. 检查所有 `.ts` 文件语法
2. 注意：React JSX 语法（`<div>...</div>`）在 Plugin Playground 的转译器中可能不支持。使用 `React.createElement()` 替代
3. 类型注解是可选的，转译时会擦除

### 重新加载后样式重复

**原因**：之前加载的样式没有正确回滚。

**解决**：PluginLoader 在重新加载时会自动调用 `rollbackLocalStyleMutations()` 回滚上一次的样式变更。如果样式仍然重复，可以刷新页面。

## 扩展练习

1. 在 `utils.ts` 中添加一个 `debounce` 工具函数，在 widget 中使用
2. 创建 `my-extension/components/` 子目录，拆分子组件
3. 添加多个CSS文件，分别在widget和index中导入
4. 尝试添加CSS动画（`@keyframes`）

## 预期结果

- ✅ 插件加载成功，无控制台错误
- ✅ 面板显示紫色主题样式
- ✅ CSS变量正确解析
- ✅ 日志区域黑色背景、等宽字体
- ✅ 点击按钮可添加/清空日志
- ✅ 重复加载不导致样式重复
