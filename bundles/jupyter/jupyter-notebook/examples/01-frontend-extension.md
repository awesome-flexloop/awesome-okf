---
title: 开发前端扩展
type: example
bundle: jupyter-notebook
okf-version: "0.2"
chapter: "01"
difficulty: advanced
tags: ["extension", "frontend", "plugin", "typescript", "sidebar"]
prerequisites: ["00-quickstart"]
sources: ["F-031", "F-034", "F-038"]
related_concepts: ["06-extension-system", "03-frontend-shell", "10-frontend-packages"]
---

# 01 | 开发前端扩展

本教程将创建一个完整的Jupyter Notebook前端扩展——一个显示服务器信息的侧边栏面板。通过本教程，你将掌握JupyterLab/Notebook插件开发的完整流程。

## 前置条件

- Node.js 18+
- Python 3.10+
- Jupyter Notebook v7 已安装
- 基础的TypeScript知识

## 第一步：使用Cookiecutter创建项目

JupyterLab提供了扩展模板生成器：

```bash
# 安装cookiecutter
pip install cookiecutter

# 生成扩展项目
cookiecutter https://github.com/jupyterlab/extension-cookiecutter-ts
```

按照提示输入：
- `author_name`: 你的名字
- `extension_name`: `server-info`
- `project_short_description`: A Jupyter Notebook extension showing server info

```bash
cd server-info
```

## 第二步：项目结构

生成的项目结构如下：

```
server-info/
├── package.json              # npm包配置
├── tsconfig.json             # TypeScript配置
├── pyproject.toml            # Python包配置
├── setup.py                  # 兼容安装脚本
├── install.json              # JupyterLab扩展安装配置
├── src/
│   └── index.ts              # 插件入口（核心代码）
├── style/
│   ├── base.css              # 基础样式
│   ├── index.css             # 样式入口
│   └── index.js              # 样式导入
└── .github/                  # CI配置
```

## 第三步：编写插件代码

编辑 `src/index.ts`：

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
 * 插件ID
 */
const PLUGIN_ID = 'server-info:plugin';

/**
 * ServerInfoWidget - 显示服务器信息的自定义Widget
 */
class ServerInfoWidget extends Widget {
  constructor() {
    super();
    this.id = 'server-info-widget';
    this.title.iconClass = 'jp-Icon jp-Icon-16 jp-ServerInfoIcon';
    this.title.caption = 'Server Info';
    this.title.closable = true;

    this.addClass('server-info-panel');

    // 创建UI内容
    this._buildUI();
  }

  private _buildUI() {
    const container = document.createElement('div');
    container.className = 'server-info-container';

    // 标题
    const title = document.createElement('h2');
    title.textContent = 'Server Information';
    container.appendChild(title);

    // 服务器版本
    const version = document.createElement('div');
    version.className = 'server-info-item';
    version.innerHTML = `<strong>Notebook Version:</strong> ${PageConfig.getOption('appVersion')}`;
    container.appendChild(version);

    // Base URL
    const baseUrl = document.createElement('div');
    baseUrl.className = 'server-info-item';
    baseUrl.innerHTML = `<strong>Base URL:</strong> ${PageConfig.getBaseUrl()}`;
    container.appendChild(baseUrl);

    // 终端是否可用
    const terminals = document.createElement('div');
    terminals.className = 'server-info-item';
    terminals.innerHTML = `<strong>Terminals:</strong> ${PageConfig.getOption('terminalsAvailable')}`;
    container.appendChild(terminals);

    // JupyterHub信息
    const hubPrefix = PageConfig.getOption('hubPrefix');
    if (hubPrefix) {
      const hubInfo = document.createElement('div');
      hubInfo.className = 'server-info-item';
      hubInfo.innerHTML = `<strong>JupyterHub:</strong> ${hubPrefix} (user: ${PageConfig.getOption('hubUser')})`;
      container.appendChild(hubInfo);
    }

    // 刷新按钮
    const refreshBtn = document.createElement('button');
    refreshBtn.textContent = 'Refresh';
    refreshBtn.className = 'jp-button jp-mod-styled server-info-refresh';
    refreshBtn.onclick = () => this._fetchKernelInfo();
    container.appendChild(refreshBtn);

    // Kernel信息区域
    this._kernelInfo = document.createElement('div');
    this._kernelInfo.className = 'server-info-kernels';
    container.appendChild(this._kernelInfo);

    this.node.appendChild(container);

    // 加载kernel信息
    this._fetchKernelInfo();
  }

  private async _fetchKernelInfo() {
    try {
      const response = await fetch(
        PageConfig.getBaseUrl() + 'api/kernels',
        { credentials: 'include' }
      );
      const kernels = await response.json();
      this._kernelInfo!.innerHTML = `<h3>Running Kernels (${kernels.length})</h3>`;
      kernels.forEach((kernel: any) => {
        const item = document.createElement('div');
        item.className = 'server-info-kernel-item';
        item.textContent = `${kernel.name} - ${kernel.execution_state} (${kernel.id.substring(0, 8)}...)`;
        this._kernelInfo!.appendChild(item);
      });
    } catch (err) {
      this._kernelInfo!.innerHTML = `<div class="server-info-error">Failed to fetch kernel info</div>`;
    }
  }

  private _kernelInfo: HTMLDivElement | null = null;
}

/**
 * 插件定义
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [INotebookShell],
  optional: [ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    shell: INotebookShell,
    palette: ICommandPalette | null
  ) => {
    console.log('JupyterLab extension server-info is activated!');

    // 创建widget实例
    const widget = new ServerInfoWidget();

    // 添加到Shell的left区域
    shell.add(widget, 'left', { rank: 1000 });

    // 注册命令
    const command = 'server-info:open';
    app.commands.addCommand(command, {
      label: 'Open Server Info',
      caption: 'Open Server Information Panel',
      execute: () => {
        shell.activateById(widget.id);
      }
    });

    // 添加到命令面板
    if (palette) {
      palette.addItem({ command, category: 'Server Info' });
    }
  }
};

export default plugin;
```

## 第四步：添加样式

编辑 `style/base.css`：

```css
.server-info-panel {
  overflow-y: auto;
  padding: 12px;
  height: 100%;
}

.server-info-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.server-info-container h2 {
  font-size: 16px;
  margin: 0 0 8px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--jp-border-color1);
}

.server-info-item {
  font-size: 12px;
  padding: 4px 0;
  word-break: break-all;
}

.server-info-item strong {
  color: var(--jp-ui-font-color0);
}

.server-info-refresh {
  margin-top: 12px;
  width: 100%;
}

.server-info-kernels {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--jp-border-color2);
}

.server-info-kernels h3 {
  font-size: 14px;
  margin: 0 0 8px 0;
}

.server-info-kernel-item {
  font-size: 11px;
  padding: 2px 0;
  color: var(--jp-ui-font-color2);
}

.server-info-error {
  color: var(--jp-error-color0);
  font-size: 12px;
}
```

## 第五步：安装和开发

```bash
# 安装依赖
npm install

# 开发模式安装（链接到JupyterLab/Notebook）
pip install -e .

# 链接前端扩展（开发模式）
jupyter labextension develop . --overwrite

# 或者使用notebook扩展命令
jupyter notebook extension develop . --overwrite

# 监听前端变化
npm run watch
```

在另一个终端启动Notebook：

```bash
jupyter notebook
```

访问Notebook后，你应该在左侧边栏看到一个新的"Server Info"标签面板。

## 第六步：生产构建

```bash
# 构建生产版本
npm run build

# 重新安装Python包
pip install .

# 验证扩展已安装
jupyter labextension list
# 应该看到 server-info 已启用
```

## 插件开发核心概念

### 1. Token依赖注入

在 `requires` 和 `optional` 中声明需要的服务Token，运行时自动注入：

```typescript
requires: [INotebookShell],      // 必需依赖
optional: [ICommandPalette],     // 可选依赖（可能不存在）
```

常用Token：

| Token | 提供服务 | 来源 |
|-------|---------|------|
| `INotebookShell` | NotebookShell实例 | `@jupyter-notebook/application` |
| `ICommandPalette` | 命令面板 | `@jupyterlab/apputils` |
| `IMainMenu` | 主菜单 | `@jupyterlab/mainmenu` |
| `IDocumentManager` | 文档管理器 | `@jupyterlab/docmanager` |
| `ISettingRegistry` | 设置注册表 | `@jupyterlab/settingregistry` |
| `ILauncher` | 启动器 | `@jupyterlab/launcher` |
| `IRouter` | 路由服务 | `@jupyterlab/application` |
| `ITranslator` | 翻译服务 | `@jupyterlab/translation` |

### 2. Shell区域选择

`shell.add(widget, area, options)` 的area参数：

| 区域 | 适合内容 | rank范围 |
|------|---------|---------|
| `'left'` | 文件浏览器、工具面板 | 300-900 |
| `'right'` | 属性检查器、调试器 | 500-900 |
| `'top'` | 工具栏、通知栏 | 100-500 |
| `'main'` | 主内容widget | 0-100 |
| `'down'` | 控制台、日志 | 100-500 |
| `'menu'` | 菜单项 | 0-100 |

### 3. 命令系统

```typescript
// 注册命令
app.commands.addCommand('my-command:do-something', {
  label: 'Do Something',          // 显示名称
  caption: 'Does something cool', // 提示文本
  iconClass: 'my-icon-class',     // 图标CSS类
  isEnabled: () => true,          // 是否启用
  isToggled: () => false,         // 是否切换状态
  execute: async (args) => {      // 执行函数
    // 命令逻辑
  }
});

// 执行命令
app.commands.execute('my-command:do-something');
```

### 4. Widget生命周期

```typescript
class MyWidget extends Widget {
  constructor() {
    super();
    this.id = 'my-widget-id';     // DOM ID
    this.title.label = 'My Widget'; // 标签/标题
    this.title.closable = true;    // 是否可关闭
    this.addClass('my-widget');    // CSS类
  }

  onAfterAttach() {
    // Widget被添加到DOM后调用，适合事件监听
  }

  onBeforeDetach() {
    // Widget从DOM移除前调用，适合清理资源
  }

  dispose() {
    // 清理资源
    super.dispose();
  }
}
```

## 调试技巧

1. **浏览器控制台**: `window.jupyterapp` 可访问应用实例（需要 `--expose-app-in-browser`）
2. **日志**: 使用 `console.log()` 输出调试信息
3. **React DevTools**: 适用于React组件
4. **Source Maps**: 开发模式下可以在浏览器中调试TypeScript源码

## 发布到PyPI

```bash
# 安装发布工具
pip install build twine

# 构建包
python -m build

# 上传到PyPI
twine upload dist/*
```

安装方式：`pip install server-info`

## 常见问题

### Q: 扩展不显示在侧边栏？

检查：
1. 扩展是否已启用：`jupyter labextension list`
2. 浏览器控制台是否有错误
3. `shell.add()` 的area参数是否正确
4. widget的id是否唯一

### Q: 找不到 `@jupyter-notebook/application` 模块？

确保package.json中包含正确的依赖：

```json
{
  "dependencies": {
    "@jupyter-notebook/application": "^7.0.0"
  }
}
```

### Q: 如何让扩展同时兼容JupyterLab和Notebook？

将 `INotebookShell` 放在 `optional` 中，同时也支持 `ILabShell`：

```typescript
import { ILabShell } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  optional: [INotebookShell, ILabShell],
  activate: (app, notebookShell, labShell) => {
    const shell = notebookShell || labShell;
    if (shell) {
      shell.add(widget, 'left');
    }
  }
};
```

## 下一步

- [自定义Shell布局](./03-customize-shell.md) 学习更高级的Shell操作
- [开发服务端扩展](./02-server-extension.md) 学习添加后端API
