---
type: Concept
title: 会话窗口系统
description: SessionWindow 与 SessionWindowManager 的设计，包括多窗口管理、窗口生命周期、内容视图切换、标题栏、环境选择弹窗、LabView 加载流程
tags: [session-window, browserwindow, multi-window, titlebar, labview, welcomeview, content-view]
prerequisites:
  - /concepts/01-architecture-overview.md
  - /concepts/02-app-entry-lifecycle.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: sessionwindow-source
    resource: /references/sessionwindow-source.md
    title: 会话窗口源码信源
  - id: app-source
    resource: /references/app-source.md
    title: 主应用类源码信源
  - id: config-source
    resource: /references/config-source.md
    title: 应用数据与会话配置源码信源
---

# 会话窗口系统

## 概述

会话窗口系统是 JupyterLab Desktop 的 UI 核心。每个 Jupyter 会话（本地或远程）对应一个独立的 Electron BrowserWindow，由 `SessionWindowManager` 统一管理。

## ContentViewType - 内容视图类型

每个窗口有两种内容视图状态：

| 类型 | 说明 | 对应视图 |
|------|------|---------|
| `Welcome` | 欢迎页面 | WelcomeView |
| `Lab` | JupyterLab 工作界面 | LabView |

窗口创建时指定初始内容视图类型，后续可在两种视图间切换。

## SessionWindow 类

### 构造过程

```typescript
new SessionWindow({
  app,                    // IApplication 引用
  registry,               // IRegistry 引用
  serverFactory,          // IServerFactory 引用
  contentView,            // ContentViewType
  sessionConfig?,         // SessionConfig（可选）
  rect?                   // IRect 窗口位置/尺寸（可选）
})
```

构造函数执行序列：

1. 保存依赖引用（app、registry、serverFactory）
2. 创建 `WorkspaceSettings` 实例（基于 sessionConfig.workingDirectory）
3. CLI 同时指定 workingDir + pythonPath 时，将 pythonPath 保存为工作区设置
4. 检测暗色主题（`isDarkTheme(wsSettings.getValue(SettingType.theme))`）
5. 创建 BrowserWindow：
   - 默认位置 (100, 100)，默认尺寸 1024×768
   - 最小尺寸 400×300
   - macOS：`titleBarStyle: 'hidden'` + `frame: true`（原生框架+隐藏标题栏）
   - 其他平台：`frame: false`（完全自定义标题栏）
   - `webPreferences.devTools: false`（默认关闭开发者工具）
   - 背景色根据主题设置（LightThemeBGColor / DarkThemeBGColor）
6. 调用 `guardAppOwnedView(window.webContents)` 安装导航安全守卫
7. 设置菜单栏不可见（`setMenuBarVisibility(false)`）
8. 显示窗口（`show()`）
9. 注册事件监听器
10. 创建 ProgressView（加载进度指示器）
11. 创建环境选择弹窗（EnvSelectPopup）

### load() - 加载内容

在构造后调用，完成 UI 初始化：

1. **创建 TitleBarView**：高度 29px，添加为窗口的 child view
2. **监听窗口焦点变化**：
   - focus → 激活标题栏 + 将焦点转给内容视图 webContents
   - blur → 停用标题栏 + 隐藏环境选择弹窗
3. **加载标题栏内容**（`titleBarView.load()`）
4. **根据 contentViewType 加载内容**：
   - Welcome → `_showWelcomeView()`
   - Lab → `_loadLabView()`

### _createServerForSession() - 创建本地服务器

本地会话加载 Lab 前需要创建 Jupyter Server：

1. 从 WorkspaceSettings 获取 pythonPath
2. 从 Registry 获取对应环境信息
3. 调用 `serverFactory.createServer({ workingDirectory, environment })`
   - 可能复用预创建的 free server
   - 可能新建服务器进程
4. 等待 `server.server.started` Promise
5. 填充 sessionConfig 的 token、url、defaultKernel

### _loadLabView() - 加载 Lab 界面

```typescript
async _loadLabView() {
  // 1. 显示进度视图
  this._showProgressView();

  if (this._sessionConfig.isRemote) {
    // 2a. 远程会话：直接加载 remoteURL
    //     使用 sessionConfig.partition（持久化或临时 session）
    await this._labView.loadURL(this._sessionConfig.remoteURL);
  } else {
    // 2b. 本地会话：创建/复用服务器
    await this._createServerForSession();
    await this._labView.loadURL(this._sessionConfig.url.href);
  }

  // 3. 隐藏进度视图
  this._hideProgressView();
}
```

### 窗口布局

窗口使用 Electron 的 `contentView.addChildView()` 管理子视图布局：

```
┌─────────────────────────────────────┐
│          TitleBarView (29px)         │  ← 自定义标题栏
├─────────────────────────────────────┤
│                                     │
│      LabView / WelcomeView          │  ← 主内容区域
│      (y: 29, 占剩余空间)             │
│                                     │
└─────────────────────────────────────┘
```

- TitleBarView 始终占顶部 29px
- 内容视图从 y=29 开始，高度为窗口高度 - 29px
- 窗口 resize 时通过 `setBounds()` 动态调整子视图位置

### 窗口关闭处理

监听 `window.on('close')` 事件：

1. 保存窗口位置和尺寸到 sessionConfig（x, y, width, height）
2. 将当前会话添加到最近会话列表（`appData.addSessionToRecents()`）
3. 若有本地服务器，调用 `serverFactory.stopServer(factoryId)` 停止
4. 清理 TitleBarView、LabView/WelcomeView、ProgressView 等子视图
5. 销毁 BrowserWindow

### 环境切换（switchPythonEnvironment）

用户在 UI 中切换 Python 环境时：

1. 停止当前关联的服务器
2. 更新 WorkspaceSettings 中的 pythonPath
3. 重新调用 `_loadLabView()` 创建新服务器并加载

## SessionWindowManager 类

SessionWindowManager 是 JupyterApplication 的内部类，管理所有 SessionWindow 实例。

### 窗口创建方法

| 方法 | 初始视图 | restorePosition | 说明 |
|------|---------|----------------|------|
| `createNewEmptyWindow()` | Welcome | false | 创建新的欢迎页窗口 |
| `restoreLabWindow(sessionConfig?)` | Lab | true | 恢复上次的 Lab 窗口（记住位置） |
| `createNewLabWindow(sessionConfig?)` | Lab | false | 创建新的 Lab 窗口 |
| `getOrCreateEmptyWindow()` | Welcome | false | 获取已有的空窗口或新建 |

### 核心创建逻辑（createNew）

所有窗口创建最终调用 `createNew()` 方法：

1. 计算窗口位置：
   - 若指定了 rect，使用指定位置
   - 否则居中于当前光标所在显示器
2. **窗口重叠检测**：
   - 检查与已有窗口的左上角距离
   - 若距离 < `minimumWindowSpacing`（15px），则以 `windowSpacing`（30px）步长偏移
   - 防止多个窗口完全重叠
3. 创建 SessionWindow 实例
4. 调用 `sessionWindow.load()` 加载内容
5. 保存到内部窗口列表

### 窗口位置偏移算法

```
新窗口默认位置：显示器中央
检查与每个已有窗口的左上角距离：
  如果 |x1 - x2| < 15 且 |y1 - y2| < 15:
    新位置 = (默认位置 + 30px 偏移)
```

### 空窗口管理

- `getEmptyWindowCount()`：统计内容视图为 Welcome 的窗口数量
- `getOrCreateEmptyWindow()`：优先返回已有的空窗口（避免创建过多欢迎页窗口）

## SessionConfig - 会话配置

每个会话由 SessionConfig 描述，支持两种创建方式：

### 本地会话

```typescript
SessionConfig.createLocal(workingDirectory?, filesToOpen?, pythonPath?)
SessionConfig.createLocalForFilesOrFolders(fileOrFolders[])
SessionConfig.createFromArgs(cliArgs)  // 从 CLI 参数自动检测
```

关键属性：
- `workingDirectory`：工作目录（影响服务器启动目录和工作区设置）
- `filesToOpen`：要打开的文件列表（相对于工作目录）
- `pythonPath`：Python 解释器路径（可选，为空则使用默认环境）
- `x/y/width/height`：窗口位置和尺寸（恢复时使用）

### 远程会话

```typescript
SessionConfig.createRemote(remoteURL, persistSessionData, partition?)
```

关键属性：
- `remoteURL`：远程服务器完整 URL（含 token）
- `persistSessionData`：是否持久化 cookie/会话数据
- `partition`：Electron session partition 字符串（`persist:` 前缀持久化，`partition:` 前缀临时）
- 从 URL 自动解析 token

详见 [应用数据与会话配置信源](/references/config-source.md)。

## 环境选择弹窗

TitleBarView 中有环境选择器，点击显示 EnvSelectPopup：

- 列出当前可用的所有 Python 环境
- 显示当前使用的环境（高亮）
- 支持切换环境（触发 switchPythonEnvironment）
- 支持打开环境管理对话框
- 窗口失焦时自动隐藏

## 进度视图

ProgressView 是覆盖在内容区域上的加载指示器：

- 服务器启动期间显示
- LabView 加载完成后隐藏
- 提供加载状态反馈

## 相关信源

- [SessionWindow 信源](/references/sessionwindow-source.md)
- [App 信源](/references/app-source.md)
- [Config 信源](/references/config-source.md)
- [导航安全信源](/references/navigation-source.md)

## 下一篇

- [Jupyter 服务器管理](/concepts/04-server-management.md)
- [Python 环境管理](/concepts/05-python-env-management.md)

## 相关概念

- [架构概览](/concepts/01-architecture-overview.md) — 理解 SessionWindow 在整体架构中的位置
- [应用入口与生命周期](/concepts/02-app-entry-lifecycle.md) — 了解窗口创建的启动时序
- [Jupyter 服务器管理](/concepts/04-server-management.md) — 本地会话中 LabView 加载依赖的服务器创建流程
- [安全与导航策略](/concepts/09-security-navigation.md) — 窗口中 guardAppOwnedView 导航守卫的安全机制
