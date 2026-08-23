---
type: Reference
title: 事件与IPC系统源码信源
description: src/main/eventtypes.ts 和 src/main/eventmanager.ts 事件类型定义与事件管理器源码登记，包含 EventTypeMain/EventTypeRenderer 枚举、EventManager 类的注册/注销机制
tags: [event, ipc, event-manager, ipcmain, event-types, main-process, renderer-process]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: eventtypes-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/eventtypes.ts
    title: eventtypes.ts source on GitHub
  - id: eventmanager-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/eventmanager.ts
    title: eventmanager.ts source on GitHub
---

# 事件与IPC系统源码信源

## 源码路径

- `src/main/eventtypes.ts` - 事件类型枚举定义
- `src/main/eventmanager.ts` - 事件管理器实现

## EventTypeMain 枚举（主进程接收的事件）

完整列表按功能分类：

### 窗口控制事件

| 事件名 | 字符串值 | 说明 |
|--------|---------|------|
| `MinimizeWindow` | `minimize-window` | 最小化窗口 |
| `MaximizeWindow` | `maximize-window` | 最大化窗口 |
| `RestoreWindow` | `restore-window` | 还原窗口 |
| `CloseWindow` | `close-window` | 关闭窗口 |

### 会话管理事件

| 事件名 | 字符串值 | 说明 |
|--------|---------|------|
| `CreateNewSession` | `create-new-session` | 创建新会话 |
| `CreateNewRemoteSession` | `create-new-remote-session` | 创建远程会话 |
| `OpenFileOrFolder` | `open-file-or-folder` | 打开文件或文件夹 |
| `OpenFile` | `open-file` | 打开文件 |
| `OpenFolder` | `open-folder` | 打开文件夹 |
| `OpenRecentSession` | `open-recent-session` | 打开最近会话 |
| `DeleteRecentSession` | `delete-recent-session` | 删除最近会话 |
| `OpenDroppedFiles` | `open-dropped-files` | 打开拖放文件 |
| `RestartSession` | `restart-session` | 重启会话 |

### Python 环境事件

| 事件名 | 字符串值 | 说明 |
|--------|---------|------|
| `SetSessionPythonPath` | `set-session-python-path` | 设置会话 Python 路径 |
| `ShowEnvSelectPopup` | `show-env-select-popup` | 显示环境选择弹窗 |
| `HideEnvSelectPopup` | `hide-env-select-popup` | 隐藏环境选择弹窗 |
| `SelectPythonPath` | `select-python-path` | 选择 Python 路径（文件对话框） |
| `SetDefaultPythonPath` | `set-default-python-path` | 设置默认 Python 路径 |
| `ValidatePythonPath` | `validate-python-path` | 验证 Python 路径 |
| `InstallBundledPythonEnv` | `install-bundled-python-env` | 安装捆绑环境 |
| `UpdateBundledPythonEnv` | `update-bundled-python-env` | 更新捆绑环境 |
| `CreateNewPythonEnvironment` | `create-new-python-environment` | 创建新 Python 环境 |
| `GetPythonEnvironmentList` | `get-python-environment-list` | 获取环境列表 |
| `DeletePythonEnvironment` | `delete-python-environment` | 删除环境 |

### 设置事件

| 事件名 | 字符串值 | 说明 |
|--------|---------|------|
| `SetTheme` | `set-theme` | 设置主题 |
| `SetSyncJupyterLabTheme` | `set-sync-jupyterlab-theme` | 设置同步主题 |
| `SetStartupMode` | `set-startup-mode` | 设置启动模式 |
| `SetLogLevel` | `set-log-level` | 设置日志级别 |
| `SetServerLaunchArgs` | `set-server-launch-args` | 设置服务器启动参数 |
| `SetServerEnvVars` | `set-server-env-vars` | 设置服务器环境变量 |
| `SetCtrlWBehavior` | `set-ctrl-w-behavior` | 设置 Ctrl+W 行为 |
| `SetCheckForUpdatesAutomatically` | `set-check-for-updates-automatically` | 自动检查更新 |
| `SetSettings` | `set-settings` | 批量设置 |

### 通用事件

| 事件名 | 字符串值 | 说明 |
|--------|---------|------|
| `GetServerInfo` | `get-server-info` | 获取服务器信息（含 origin 校验） |
| `IsDarkTheme` | `is-dark-theme` | 查询是否暗色主题 |
| `LabUIReady` | `lab-ui-ready` | Lab UI 就绪通知 |
| `ShowWelcomeView` | `show-welcome-view` | 显示欢迎页 |
| `CheckForUpdates` | `check-for-updates` | 检查更新 |
| `CopyToClipboard` | `copy-to-clipboard` | 复制到剪贴板 |
| `RestartApp` | `restart-app` | 重启应用 |

## EventTypeRenderer 枚举（渲染进程接收的事件）

| 事件名 | 字符串值 | 说明 |
|--------|---------|------|
| `WorkingDirectorySelected` | `working-directory-selected` | 工作目录已选择 |
| `CustomPythonPathSelected` | `custom-python-path-selected` | 自定义 Python 路径已选择 |
| `SetCurrentPythonPath` | `set-current-python-path` | 设置当前 Python 路径 |
| `SetRecentSessionList` | `set-recent-session-list` | 更新最近会话列表 |
| `SetNewsList` | `set-news-list` | 更新新闻列表 |
| `ShowProgress` | `show-progress` | 显示进度 |
| `SetTitle` | `set-title` | 设置窗口标题 |
| `SetActive` | `set-active` | 设置激活状态 |
| `SetMaximized` | `set-maximized` | 设置最大化状态 |
| `ShowServerStatus` | `show-server-status` | 显示服务器状态 |
| `SetRunningServerList` | `set-running-server-list` | 设置运行中服务器列表 |
| `SetPythonEnvironmentList` | `set-python-environment-list` | 设置环境列表 |
| `SetNotificationMessage` | `set-notification-message` | 设置通知消息 |

## EventManager 类

### 类型定义

```typescript
type AsyncEventHandlerMain = (event: Electron.IpcMainEvent, ...args: any[]) => void;
type SyncEventHandlerMain = (event: Electron.IpcMainEvent, ...args: any[]) => any;
```

### 方法

| 方法 | 说明 |
|------|------|
| `registerEventHandler(eventType, handler)` | 注册异步事件处理器（通过 `ipcMain.on`） |
| `registerSyncEventHandler(eventType, handler)` | 注册同步事件处理器（通过 `ipcMain.handle`，支持 returnValue） |
| `unregisterEventHandler(eventType, handler)` | 注销异步事件处理器 |
| `unregisterSyncEventHandler(eventType, handler)` | 注销同步事件处理器 |
| `unregisterAllEventHandlers()` | 注销所有异步事件处理器 |
| `unregisterAllSyncEventHandlers()` | 注销所有同步事件处理器 |
| `dispose()` | 清理所有事件处理器 |

### 内部数据结构

- `_asyncEventHandlers: Map<EventTypeMain, AsyncEventHandlerMain[]>` - 异步处理器映射
- `_syncEventHandlers: Map<EventTypeMain, SyncEventHandlerMain[]>` - 同步处理器映射

### 注册机制

- 同一事件类型可以注册多个处理器（链式调用）
- 同步处理器使用 `ipcMain.handle` 注册，通过 `ipcMain.removeHandler` 注销
- 异步处理器使用 `ipcMain.on` 注册，通过 `ipcMain.removeListener` 注销

## 相关概念

- [事件与IPC系统](/concepts/08-event-ipc-system.md)
- [会话窗口系统](/concepts/03-session-window-system.md)
