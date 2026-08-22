---
title: 自定义Shell布局
type: example
bundle: jupyter-notebook
chapter: "03"
difficulty: advanced
tags: ["shell", "layout", "frontend", "customization", "widget"]
prerequisites: ["01-frontend-extension"]
sources: ["F-033", "F-035", "F-036", "F-037"]
related_concepts: ["03-frontend-shell", "06-extension-system"]
---

# 03 | 自定义Shell布局

本教程展示如何通过前端插件自定义NotebookShell的布局，包括添加自定义面板、修改默认区域行为、以及控制widget位置。

## 前置条件

- 已阅读[开发前端扩展](./01-frontend-extension.md)
- 理解NotebookShell六区域模型
- 已有一个可工作的前端扩展项目

## 一、向各区域添加Widget

### 添加到左侧边栏

```typescript
import { INotebookShell } from '@jupyter-notebook/application';
import { Widget } from '@lumino/widgets';

const leftPanelPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:left-panel',
  autoStart: true,
  requires: [INotebookShell],
  activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
    // 创建左侧面板
    const leftWidget = new Widget();
    leftWidget.id = 'my-left-panel';
    leftWidget.title.label = 'My Panel';
    leftWidget.title.caption = 'My Custom Panel';
    leftWidget.title.closable = true;
    leftWidget.addClass('my-left-panel');

    // 添加内容
    const content = document.createElement('div');
    content.innerHTML = '<h3>My Panel</h3><p>Custom content here</p>';
    leftWidget.node.appendChild(content);

    // 添加到left区域，rank=500（在文件浏览器之后）
    shell.add(leftWidget, 'left', { rank: 500 });
  }
};
```

### 添加到右侧边栏

```typescript
const rightPanelPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:right-panel',
  autoStart: true,
  requires: [INotebookShell],
  activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
    const widget = new Widget();
    widget.id = 'my-right-panel';
    widget.title.label = 'Inspector';
    widget.title.iconClass: 'jp-InspectorIcon';

    // rank=600（在属性检查器位置）
    shell.add(widget, 'right', { rank: 600 });
  }
};
```

### 添加到顶部栏

```typescript
const topBarPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:top-bar',
  autoStart: true,
  requires: [INotebookShell],
  activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
    const topWidget = new Widget();
    topWidget.id = 'my-top-widget';
    topWidget.addClass('my-top-bar');

    // 创建一个自定义工具栏按钮
    const btn = document.createElement('button');
    btn.textContent = 'My Action';
    btn.className = 'jp-button jp-mod-styled';
    btn.onclick = () => {
      app.commands.execute('my-extension:my-command');
    };
    topWidget.node.appendChild(btn);

    // rank=100（在默认工具栏之前）
    shell.add(topWidget, 'top', { rank: 100 });
  }
};
```

### 添加到底部面板（Down区域）

```typescript
const downPanelPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:down-panel',
  autoStart: true,
  requires: [INotebookShell],
  activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
    const logWidget = new Widget();
    logWidget.id = 'my-log-panel';
    logWidget.title.label = 'Logs';
    logWidget.title.closable = true;

    // down区域默认占25%高度（F-035: DEFAULT_DOWN_AREA_SIZE = 0.25）
    shell.add(logWidget, 'down', { rank: 300 });
  }
};
```

### 添加自定义主区域Widget

```typescript
const mainWidgetPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:main-widget',
  autoStart: true,
  requires: [INotebookShell],
  activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
    // 创建一个自定义页面widget
    const welcomeWidget = new Widget();
    welcomeWidget.id = 'my-welcome-page';
    welcomeWidget.title.label = 'Welcome';
    welcomeWidget.node.innerHTML = '<h1>Welcome to My Notebook!</h1>';

    // 添加到main区域
    shell.add(welcomeWidget, 'main', {
      rank: 0,  // 优先显示
      activate: true  // 激活此widget
    });
  }
};
```

## 二、控制Widget显示与激活

### 激活特定Widget

```typescript
// 通过命令激活
app.commands.addCommand('my-extension:show-panel', {
  label: 'Show My Panel',
  execute: () => {
    shell.activateById('my-left-panel');
    // 展开对应侧边栏
    shell.expandLeft();
  }
});
```

### 展开/折叠侧边栏

```typescript
// 展开左侧边栏
shell.expandLeft();

// 折叠左侧边栏
shell.collapseLeft();

// 展开/折叠右侧边栏
shell.expandRight();
shell.collapseRight();
```

### 监听当前Widget变化

```typescript
// 监听main区域的当前widget变化
shell.currentChanged.connect((sender, args) => {
  const { newValue, oldValue } = args;
  console.log('Active widget changed from', oldValue?.id, 'to', newValue?.id);
});
```

## 三、修改默认布局行为

### 隐藏默认组件

NotebookShell没有直接的"隐藏"API，但可以通过CSS和命令来控制：

```typescript
// 隐藏顶部栏
app.commands.execute('application:toggle-top').then(() => {
  // 顶部栏切换隐藏/显示
});

// 切换Zen模式（隐藏所有面板）
app.commands.execute('application:toggle-zen');
```

### 启动时自动展开特定面板

```typescript
const autoOpenPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:auto-open',
  autoStart: true,
  requires: [INotebookShell],
  activate: async (app: JupyterFrontEnd, shell: INotebookShell) => {
    // 等待应用恢复完成
    await app.restored;

    // 展开左侧边栏并激活我的面板
    shell.expandLeft();
    shell.activateById('my-left-panel');
  }
};
```

## 四、创建自定义PanelHandler（高级）

如果需要完全自定义面板的行为，可以继承SidePanelHandler：

```typescript
import { SidePanelHandler, SidePanel, SidePanelPalette } from '@jupyter-notebook/application';

class CustomSidePanelHandler extends SidePanelHandler {
  constructor(side: 'left' | 'right') {
    super(side);
    // 自定义行为
  }

  // 重写方法自定义widget添加逻辑
  addWidget(widget: Widget, options?: any): void {
    // 在添加前做自定义处理
    console.log(`Adding ${widget.id} to ${this.side} panel`);
    super.addWidget(widget, options);
  }
}
```

注意：通常不需要继承Handler，直接使用shell.add()即可满足大部分需求。

## 五、响应式布局

### 根据窗口大小调整布局

```typescript
import { Debouncer } from '@lumino/polling';

const responsivePlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:responsive',
  autoStart: true,
  requires: [INotebookShell],
  activate: (app: JupyterFrontEnd, shell: INotebookShell) => {
    const handleResize = new Debouncer(() => {
      const width = window.innerWidth;

      if (width < 768) {
        // 小屏幕：折叠侧边栏
        shell.collapseLeft();
        shell.collapseRight();
      }
    }, 200);

    window.addEventListener('resize', () => handleResize.invoke());
  }
};
```

## 六、完整示例：自定义仪表盘面板

下面是一个完整的插件示例，添加一个仪表盘面板到右侧边栏：

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookShell } from '@jupyter-notebook/application';

import { ICommandPalette } from '@jupyterlab/apputils';

import { PageConfig } from '@jupyterlab/coreutils';

import { Widget } from '@lumino/widgets';

/**
 * Dashboard Widget - 显示服务器和kernel状态
 */
class DashboardWidget extends Widget {
  constructor() {
    super();
    this.id = 'my-dashboard';
    this.title.label = 'Dashboard';
    this.title.caption = 'Server Dashboard';
    this.title.closable = true;
    this.addClass('my-dashboard');

    this._buildUI();
    this._startRefresh();
  }

  private _buildUI() {
    const container = document.createElement('div');
    container.className = 'my-dashboard-container';

    // 头部
    const header = document.createElement('div');
    header.className = 'my-dashboard-header';
    header.innerHTML = '<h2>📊 Dashboard</h2>';
    container.appendChild(header);

    // 状态卡片
    this._kernelCount = document.createElement('div');
    this._kernelCount.className = 'my-dashboard-card';
    container.appendChild(this._kernelCount);

    this._sessionCount = document.createElement('div');
    this._sessionCount.className = 'my-dashboard-card';
    container.appendChild(this._sessionCount);

    this._terminalCount = document.createElement('div');
    this._terminalCount.className = 'my-dashboard-card';
    container.appendChild(this._terminalCount);

    // 操作按钮
    const btnContainer = document.createElement('div');
    btnContainer.className = 'my-dashboard-buttons';

    const refreshBtn = document.createElement('button');
    refreshBtn.textContent = '🔄 Refresh';
    refreshBtn.className = 'jp-button jp-mod-styled';
    refreshBtn.onclick = () => this._refresh();
    btnContainer.appendChild(refreshBtn);

    const shutdownBtn = document.createElement('button');
    shutdownBtn.textContent = '⏹️ Shutdown All Kernels';
    shutdownBtn.className = 'jp-button jp-mod-warn';
    shutdownBtn.onclick = () => this._shutdownAllKernels();
    btnContainer.appendChild(shutdownBtn);

    container.appendChild(btnContainer);

    this.node.appendChild(container);
  }

  private _startRefresh() {
    // 每10秒刷新一次
    this._timer = setInterval(() => this._refresh(), 10000);
    this._refresh();
  }

  private async _refresh() {
    try {
      const baseUrl = PageConfig.getBaseUrl();

      // 获取kernels
      const kRes = await fetch(baseUrl + 'api/kernels', { credentials: 'include' });
      const kernels = await kRes.json();
      this._kernelCount!.innerHTML = `<strong>🖥️ Kernels</strong><br>${kernels.length} running`;

      // 获取sessions
      const sRes = await fetch(baseUrl + 'api/sessions', { credentials: 'include' });
      const sessions = await sRes.json();
      this._sessionCount!.innerHTML = `<strong>📓 Sessions</strong><br>${sessions.length} active`;

      // 获取terminals
      const tRes = await fetch(baseUrl + 'api/terminals', { credentials: 'include' });
      const terminals = await tRes.json();
      this._terminalCount!.innerHTML = `<strong>💻 Terminals</strong><br>${terminals.length} open`;
    } catch (err) {
      console.error('Dashboard refresh failed:', err);
    }
  }

  private async _shutdownAllKernels() {
    if (!confirm('Shutdown all kernels?')) return;

    try {
      const baseUrl = PageConfig.getBaseUrl();
      const res = await fetch(baseUrl + 'api/kernels', { credentials: 'include' });
      const kernels = await res.json();

      for (const kernel of kernels) {
        await fetch(baseUrl + 'api/kernels/' + kernel.id, {
          method: 'DELETE',
          credentials: 'include'
        });
      }

      this._refresh();
    } catch (err) {
      console.error('Shutdown failed:', err);
    }
  }

  dispose() {
    if (this._timer) {
      clearInterval(this._timer);
    }
    super.dispose();
  }

  private _kernelCount: HTMLDivElement | null = null;
  private _sessionCount: HTMLDivElement | null = null;
  private _terminalCount: HTMLDivElement | null = null;
  private _timer: ReturnType<typeof setInterval> | null = null;
}

/**
 * 插件定义
 */
const dashboardPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:dashboard',
  autoStart: true,
  requires: [INotebookShell],
  optional: [ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    shell: INotebookShell,
    palette: ICommandPalette | null
  ) => {
    // 创建并添加dashboard到右侧边栏
    const dashboard = new DashboardWidget();
    shell.add(dashboard, 'right', { rank: 500 });

    // 注册命令
    const command = 'my-extension:show-dashboard';
    app.commands.addCommand(command, {
      label: 'Show Dashboard',
      caption: 'Open Server Dashboard',
      execute: () => {
        shell.activateById(dashboard.id);
        shell.expandRight();
      }
    });

    // 添加到命令面板
    if (palette) {
      palette.addItem({ command, category: 'My Extension' });
    }

    // 添加快捷键: Ctrl+Shift+D
    app.commands.addKeyBinding({
      command,
      keys: ['Ctrl Shift D'],
      selector: 'body'
    });
  }
};

export default dashboardPlugin;
```

### 配套CSS

```css
.my-dashboard {
  overflow-y: auto;
  padding: 12px;
  height: 100%;
  background: var(--jp-layout-color1);
}

.my-dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.my-dashboard-header h2 {
  font-size: 16px;
  margin: 0;
  color: var(--jp-ui-font-color0);
}

.my-dashboard-card {
  padding: 12px;
  background: var(--jp-layout-color2);
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
}

.my-dashboard-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}
```

## 七、rank值参考

Notebook内置组件的rank值，供自定义widget时选择合适位置：

| 区域 | 组件 | 大致rank |
|------|------|---------|
| left | 文件浏览器 | 100 |
| left | 运行面板 | 200 |
| left | 目录(TOC) | 400 |
| left | 扩展管理器 | 500 |
| right | 属性检查器 | 300 |
| right | 调试器 | 500 |
| top | 菜单栏 | 0 |
| top | 工具栏 | 100 |
| top | 面包屑 | 300 |
| down | 控制台 | 100 |
| down | 终端 | 200 |

默认rank=900（F-036），不指定rank的widget排在后面。

## 常见问题

### Q: 我的widget不显示？

检查：
1. widget是否有唯一的 `id`
2. `shell.add()` 是否被调用（在activate函数中）
3. rank是否合理（过高可能被其他widget遮挡）
4. 侧边栏是否展开
5. 浏览器控制台是否有错误

### Q: 如何在JupyterLab和Notebook中都工作？

```typescript
import { ILabShell } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:widget',
  optional: [INotebookShell, ILabShell],
  activate: (app, notebookShell, labShell) => {
    const shell = notebookShell || labShell;
    if (shell) {
      shell.add(widget, 'left', { rank: 500 });
    }
  }
};
```

### Q: 如何修改默认打开的页面？

```python
# 在配置中设置默认URL
c.JupyterNotebookApp.default_url = "/notebooks/my-notebook.ipynb"
```

## 下一步

- [集成自定义认证](./04-custom-auth.md) 学习后端+前端联合扩展
