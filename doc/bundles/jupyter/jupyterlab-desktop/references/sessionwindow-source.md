---
type: Reference
title: SessionWindow 会话窗口源码信源
description: src/main/sessionwindow/sessionwindow.ts 会话窗口源码登记，包含 SessionWindow 类、ContentViewType 枚举、LabView/WelcomeView 切换、服务器创建与加载、环境切换、标题栏管理
tags: [session-window, browserwindow, titlebar, labview, welcomeview, server-session]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: sessionwindow-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/sessionwindow/sessionwindow.ts
    title: sessionwindow.ts source on GitHub
---

# SessionWindow 会话窗口源码信源

## 源码路径

`src/main/sessionwindow/sessionwindow.ts`

## 文件职责

`SessionWindow` 类管理单个 Electron BrowserWindow 的完整生命周期，包括标题栏、内容视图（Welcome/Lab）、服务器关联、环境切换、进度显示等。

## ContentViewType 枚举

```typescript
enum ContentViewType {
  Welcome = 'welcome',
  Lab = 'lab'
}
```

## IServerInfo 接口

```typescript
interface IServerInfo {
  type: 'local' | 'remote';
  url?: string;
  persistSessionData?: boolean;
  environment?: {
    name?: string;
    path?: string;
    versions?: IVersionContainer;
  };
  workingDirectory?: string;
  defaultKernel?: string;
  pageConfig?: any;
  error?: string;
}
```

## SessionWindow 类

### 构造函数

1. 初始化 `_app`、`_registry`、`_serverFactory` 引用
2. 创建 `WorkspaceSettings` 实例（基于 sessionConfig.workingDirectory）
3. CLI 指定了 workingDir + pythonPath 时，将 pythonPath 保存为工作区设置
4. 检测暗色主题（`isDarkTheme()`）
5. 创建 BrowserWindow：
   - 默认位置 (100, 100)，默认尺寸 1024x768（DEFAULT_WIN_WIDTH/DEFAULT_WIN_HEIGHT）
   - 最小尺寸 400x300
   - macOS 使用 `titleBarStyle: 'hidden'` + `frame: true`（原生框架）
   - 其他平台 `frame: false`（自定义标题栏）
   - devTools 默认关闭
   - 背景色根据主题设置
6. 调用 `guardAppOwnedView()` 保护 webContents 导航
7. 注册事件监听器，创建 ProgressView 和 EnvSelectPopup

### 关键常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `titleBarHeight` | 29 | 自定义标题栏高度（像素） |
| `defaultEnvSelectPopupHeight` | 330 | 环境选择弹窗默认高度 |

### 核心方法

#### 服务器创建 (_createServerForSession)

1. 从 `WorkspaceSettings` 获取 pythonPath
2. 从 `Registry` 获取环境信息
3. 调用 `serverFactory.createServer()` 创建服务器（可能复用 free server）
4. 等待 `server.started` Promise
5. 填充 sessionConfig 的 token、url、defaultKernel

#### 内容加载 (load)

1. 创建 TitleBarView（高度 29px），添加为 BrowserWindow 的 child view
2. 监听窗口 focus/blur 事件，控制标题栏激活/失活状态
3. 根据 contentViewType 调用 `_showWelcomeView()` 或 `_loadLabView()`

#### _loadLabView() - 加载 Lab 界面

1. 远程会话：直接加载 remoteURL，使用 session.partition
2. 本地会话：调用 `_createServerForSession()` 创建/复用服务器，然后加载服务器 URL
3. 显示 ProgressView 作为加载指示器
4. 创建 LabView（WebContentsView），添加到窗口
5. 隐藏 ProgressView

#### 环境切换 (switchPythonEnvironment)

1. 停止当前服务器（`_serverFactory.stopServer()`）
2. 更新工作区设置中的 pythonPath
3. 重新加载 LabView

#### 窗口关闭处理

- 监听 `window.on('close')` 事件
- 保存窗口位置和尺寸到 sessionConfig
- 将会话添加到最近会话列表
- 停止关联的服务器
- 清理 TitleBarView、LabView、WelcomeView 等子视图

### SessionWindow.IOptions 接口

```typescript
namespace SessionWindow {
  interface IOptions {
    app: IApplication;
    registry: IRegistry;
    serverFactory: IServerFactory;
    contentView: ContentViewType;
    sessionConfig?: SessionConfig;
    rect?: IRect;
  }
}
```

### 标题栏边界计算 (_titleBarBounds)

标题栏占窗口顶部 29px，宽度为窗口宽度。LabView/WelcomeView 从 y=29 开始布局。

## 相关概念

- [会话窗口系统](/concepts/03-session-window-system.md)
- [Jupyter 服务器管理](/concepts/04-server-management.md)
- [导航安全策略](/concepts/09-security-navigation.md)
