---
type: Concept
title: 架构概览
description: JupyterLab Desktop 的核心模块架构、模块间依赖关系、数据流与关键设计模式
tags: [architecture, modules, data-flow, design-patterns, factory, singleton]
prerequisites:
  - /concepts/00-introduction.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: app-source
    resource: /references/app-source.md
    title: 主应用类源码信源
  - id: tokens-source
    resource: /references/tokens-source.md
    title: 核心类型源码信源
  - id: server-source
    resource: /references/server-source.md
    title: Jupyter服务器源码信源
  - id: registry-source
    resource: /references/registry-source.md
    title: 环境注册表源码信源
---

# 架构概览

## 核心模块

JupyterLab Desktop 主进程包含以下核心模块，每个模块有明确的职责边界：

| 模块 | 文件 | 职责 |
|------|------|------|
| **JupyterApplication** | [app.ts](https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/app.ts) | 主控制器，协调所有子系统 |
| **SessionWindowManager** | app.ts（内部类） | 多窗口管理，窗口创建/销毁/位置偏移 |
| **SessionWindow** | sessionwindow/sessionwindow.ts | 单个 BrowserWindow 生命周期管理 |
| **JupyterServerFactory** | server.ts | 服务器池管理，Factory 模式预创建 |
| **JupyterServer** | server.ts | 单个 Jupyter Server 实例的启停 |
| **Registry** | registry.ts | Python 环境发现、验证、注册表 |
| **EventManager** | eventmanager.ts | IPC 事件注册/分发 |
| **UserSettings** | config/settings.ts | 全局用户设置 |
| **WorkspaceSettings** | config/settings.ts | 工作区级设置（覆盖全局） |
| **ApplicationData** | config/appdata.ts | 应用数据持久化（单例） |
| **SessionConfig** | config/sessionconfig.ts | 单个会话的配置描述 |

## 模块依赖关系

```
JupyterApplication
  ├── SessionWindowManager
  │     └── SessionWindow[]
  │           ├── TitleBarView
  │           ├── WelcomeView / LabView
  │           ├── WorkspaceSettings
  │           └── SessionConfig
  ├── JupyterServerFactory
  │     └── JupyterServer[] (池化管理)
  ├── Registry
  │     └── IPythonEnvironment[]
  ├── EventManager
  ├── UserSettings
  └── ApplicationData (appData)
```

**关键依赖规则**：
- `JupyterApplication` 持有所有顶层管理器的引用
- `SessionWindow` 通过构造函数注入 `IApplication`、`IRegistry`、`IServerFactory` 引用（依赖注入模式）
- `Registry` 不依赖 UI 层，纯数据管理
- `JupyterServerFactory` 不依赖窗口层，通过工厂接口解耦

## 关键设计模式

### 1. Factory 模式（JupyterServerFactory）

JupyterServerFactory 实现了 `IServerFactory` 接口，使用对象池模式管理 JupyterServer 实例：

- **预创建（Free Server）**：应用启动时创建一个空闲服务器，新窗口打开时直接复用，消除服务器启动等待时间
- **复用条件**：相同 workingDirectory + 相同 environment.path 的空闲服务器可复用
- **使用计数**：`used` 布尔标记，分配后设为 true，窗口关闭后停止并移除

```typescript
// 预创建空闲服务器
serverFactory.createFreeServer();

// 窗口请求服务器时复用或新建
const server = await serverFactory.createServer({ workingDirectory, environment });
```

详见 [Jupyter 服务器管理](/concepts/04-server-management.md)。

### 2. 单例模式（ApplicationData / UserSettings）

- `ApplicationData` 通过 `getSingleton()` 获取全局唯一实例，管理 app-data.json 持久化
- `userSettings` 是模块级导出的 `UserSettings` 实例，全局共享

### 3. 双层设置系统（UserSettings + WorkspaceSettings）

- `UserSettings`：全局默认设置，存储在 `{userDataDir}/settings.json`
- `WorkspaceSettings`：继承自 UserSettings，工作区级覆盖，存储在 `{workingDir}/.jupyter/desktop-settings.json`
- 读取设置时工作区优先，未设置则回退到全局值
- 只有标记 `wsOverridable: true` 的设置项可被工作区覆盖

详见 [设置与配置系统](/concepts/06-settings-config.md)。

### 4. 信号模式（@lumino/signaling）

使用 Lumino 的 Signal 实现发布-订阅模式，避免模块间紧耦合：

```typescript
// Registry 发出环境列表更新信号
environmentListUpdated: ISignal<this, void>;

// JupyterApplication 订阅信号
registry.environmentListUpdated.connect(() => {
  // 刷新环境列表 UI
});
```

### 5. IDisposable 模式

核心类实现 `IDisposable` 接口，提供异步资源清理：

| 类 | dispose() 行为 |
|----|---------------|
| JupyterApplication | 停止所有服务器、关闭所有窗口、注销所有事件 |
| SessionWindowManager | 关闭所有 SessionWindow |
| JupyterServerFactory | 停止所有服务器进程 |
| EventManager | 注销所有 IPC 事件处理器 |
| Registry | 标记 disposing，等待初始化完成 |

## 核心数据流

### 启动数据流

```
app.ready
  → processArgs()                    // 解析CLI参数
  → handleMultipleAppInstances()     // 单实例锁
  → updateBundledPythonEnvInstallation()  // 更新捆绑环境
  → installGlobalNavigationGuard()  // 安装安全守卫
  → new JupyterApplication(argv)     // 创建主应用
       ├── new Registry()            // 环境注册表（异步发现环境）
       ├── new JupyterServerFactory() // 服务器工厂
       ├── new SessionWindowManager() // 窗口管理器
       ├── createFreeServer()        // 预创建空闲服务器
       ├── _registerListeners()      // 注册IPC事件
       └── startup()                 // 根据启动模式打开窗口
```

### 新建本地会话数据流

```
用户点击 "New Session"
  → JupyterApplication.createNewEmptySession()
  → SessionWindowManager.createNewLabWindow(sessionConfig)
       ├── new SessionWindow({ contentView: Lab, sessionConfig })
       │     ├── new BrowserWindow()
       │     ├── guardAppOwnedView()
       │     ├── load()
       │     │     ├── new TitleBarView()
       │     │     └── _loadLabView()
       │     │           ├── _createServerForSession()
       │     │           │     └── serverFactory.createServer()
       │     │           │           ├── 复用 free server?
       │     │           │           └── 或新建 JupyterServer.start()
       │     │           └── labView.loadURL(server.url)
       │     └── 窗口显示
       └── 窗口位置偏移计算
```

## 核心接口契约

### IApplication 接口

主应用对外暴露的操作接口：

```typescript
interface IApplication {
  createNewEmptySession(): void;
  createFreeServersIfNeeded(): void;
  checkForUpdates(showDialog: 'on-new-version' | 'always'): void;
  showSettingsDialog(activateTab?: SettingsDialog.Tab): void;
  cliArgs: ICLIArguments;
  registry: IRegistry;
}
```

### IRegistry 接口

环境注册表接口，详见 [Registry 信源](/references/registry-source.md)。

### IServerFactory 接口

服务器工厂接口，抽象了服务器创建逻辑，使 SessionWindow 不直接依赖 JupyterServer 具体实现。

## 目录结构

```
src/main/
├── main.ts                    # 应用入口
├── app.ts                     # JupyterApplication + SessionWindowManager
├── server.ts                  # JupyterServer + JupyterServerFactory
├── env.ts                     # Python 环境工具函数
├── cli.ts                     # CLI 命令解析
├── registry.ts                # Python 环境注册表
├── tokens.ts                  # 核心类型定义
├── eventtypes.ts              # IPC 事件类型枚举
├── eventmanager.ts            # IPC 事件管理器
├── navigationguard.ts         # 导航安全守卫
├── connect.ts                 # 远程服务器连接
├── utils.ts                   # 工具函数
├── config/
│   ├── settings.ts            # 设置系统（UserSettings/WorkspaceSettings）
│   ├── appdata.ts             # 应用数据持久化
│   └── sessionconfig.ts       # 会话配置
├── sessionwindow/
│   └── sessionwindow.ts       # 会话窗口
├── labview/
│   ├── labview.ts             # Lab 视图（WebContentsView）
│   └── preload.ts             # Lab 预加载脚本
├── titlebarview/              # 自定义标题栏视图
├── welcomeview/               # 欢迎页面视图
├── settingsdialog/            # 设置对话框
├── pythonenvdialog/           # Python 环境管理对话框
├── updatedialog/              # 更新对话框
├── authwindow/                # 认证窗口
├── authdialog/                # 认证对话框
├── dialog/                    # 对话框基类
└── ...
```

## 下一篇

- [应用入口与生命周期](/concepts/02-app-entry-lifecycle.md)
- [会话窗口系统](/concepts/03-session-window-system.md)

## 相关概念

- [JupyterLab Desktop 简介](/concepts/00-introduction.md) — 应用概述与核心特性
- [应用入口与生命周期](/concepts/02-app-entry-lifecycle.md) — 从进程启动到就绪的启动序列
- [会话窗口系统](/concepts/03-session-window-system.md) — 多窗口管理与窗口生命周期
- [Jupyter 服务器管理](/concepts/04-server-management.md) — Factory 模式与服务器进程管理
