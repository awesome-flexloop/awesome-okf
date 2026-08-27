---
type: Concept
title: 多窗口与会话管理
description: JupyterLab Desktop 的多窗口架构、SessionWindowManager 的窗口池管理、会话恢复、最近会话列表、单实例锁、窗口位置计算、远程会话持久化
tags: [multi-window, session-management, window-manager, session-restore, recent-sessions, single-instance]
prerequisites:
  - /concepts/03-session-window-system.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: app-source
    resource: /references/app-source.md
    title: 主应用类源码信源
  - id: sessionwindow-source
    resource: /references/sessionwindow-source.md
    title: 会话窗口源码信源
  - id: config-source
    resource: /references/config-source.md
    title: 应用数据与会话配置源码信源
  - id: main-source
    resource: /references/main-source.md
    title: 应用入口源码信源
---

# 多窗口与会话管理

## 概述

JupyterLab Desktop 支持多窗口并行工作，每个窗口对应一个独立的 Jupyter 会话（本地或远程）。SessionWindowManager 负责窗口的创建、位置管理和销毁；ApplicationData 负责会话状态的持久化和恢复。

## 多窗口架构

每个窗口是独立的单元：

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   SessionWindow 1    │  │   SessionWindow 2    │  │   SessionWindow 3    │
│  (Project A 本地)    │  │  (Project B 本地)    │  │  (远程服务器)        │
│  ┌─────────────────┐ │  │  ┌─────────────────┐ │  │  ┌─────────────────┐ │
│  │  TitleBarView   │ │  │  │  TitleBarView   │ │  │  │  TitleBarView   │ │
│  ├─────────────────┤ │  │  ├─────────────────┤ │  │  ├─────────────────┤ │
│  │    LabView      │ │  │  │    LabView      │ │  │  │    LabView      │ │
│  └─────────────────┘ │  │  └─────────────────┘ │  │  └─────────────────┘ │
│         ↕            │  │         ↕            │  │         ↕            │
│  JupyterServer 1     │  │  JupyterServer 2     │  │  远程 URL            │
│  (Python Env A)      │  │  (Python Env B)      │  │  (Session Partition) │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ↓
                    ┌─────────────────────────┐
                    │ SessionWindowManager    │
                    │ JupyterServerFactory    │
                    │ Registry (共享)          │
                    └─────────────────────────┘
```

关键特性：
- 每个窗口有独立的 JupyterServer（本地会话）或连接到不同的远程服务器
- 每个窗口有独立的 WorkspaceSettings（基于工作目录）
- 共享 Registry（环境注册表）和 UserSettings（全局设置）
- 窗口之间通过主进程协调，不直接通信

## SessionWindowManager - 窗口管理器

### 窗口创建方法

| 方法 | 内容视图 | 恢复位置 | 用途 |
|------|---------|---------|------|
| `createNewEmptyWindow()` | Welcome | ❌ | 新欢迎页 |
| `restoreLabWindow(config?)` | Lab | ✅ | 恢复上次会话 |
| `createNewLabWindow(config?)` | Lab | ❌ | 新建会话 |
| `getOrCreateEmptyWindow()` | Welcome | ❌ | 获取或创建欢迎页 |

### 窗口位置算法

新建窗口时，位置计算考虑以下因素：

1. **指定位置**：如果传入 rect 参数，使用指定位置
2. **会话配置位置**：sessionConfig 中保存了上次窗口位置（恢复时使用）
3. **默认位置**：居中于光标所在显示器，默认 (100, 100)

#### 重叠检测与偏移

为防止多个窗口完全重叠：

```typescript
const minimumWindowSpacing = 15;  // 最小间距（像素）
const windowSpacing = 30;        // 偏移步长（像素）

// 检查与每个已有窗口的左上角距离
for (const existingWindow of windows) {
  if (Math.abs(newX - existingX) < minimumWindowSpacing &&
      Math.abs(newY - existingY) < minimumWindowSpacing) {
    // 距离太近，偏移
    newX += windowSpacing;
    newY += windowSpacing;
  }
}
```

### 空窗口管理

- `getEmptyWindowCount()`：统计内容视图为 Welcome 类型的窗口数量
- `getOrCreateEmptyWindow()`：优先复用已有的空窗口，避免创建过多欢迎页
- 当用户在欢迎页点击"新建会话"时，该窗口切换为 Lab 视图而非新建窗口

## 单实例锁

使用 `app.requestSingleInstanceLock()` 确保只有一个应用实例运行：

```
实例1启动 → 获取锁成功 → 正常启动
实例2启动 → 获取锁失败
  → 实例1 收到 'second-instance' 事件
  → 实例1 焦点到已有窗口
  → 若实例2 带文件参数，实例1 打开文件
  → 实例2 退出
```

参数传递机制：
- 全局变量 `fileToOpenInMainInstance` 缓存第二个实例的文件路径
- 第一个实例在 `second-instance` 事件中读取并处理

## 会话持久化

### 活动会话跟踪

`appData.sessions: SessionConfig[]` 保存当前活动会话的配置。窗口关闭时更新该列表。

### 最近会话列表

`appData.recentSessions: IRecentSession[]` 保存最近关闭的会话，最多 20 个（`MAX_RECENT_SESSIONS = 20`）。

#### 添加到最近会话（addSessionToRecents）

- **本地会话**：按 `workingDirectory` + `filesToOpen` 去重
- **远程会话**：按 `remoteURL` 去重
- 已存在的条目更新 `date` 为当前时间
- 超过 MAX_RECENT_SESSIONS 时删除最旧的，并清理持久化 session 数据

#### 排序

按 `date` 降序排列（最新在前）。

### 远程会话持久化

远程会话支持两种 session 模式：

| Partition 前缀 | 持久化 | 说明 |
|---------------|--------|------|
| `persist:{timestamp}` | ✅ | Cookie/缓存持久化到磁盘，下次连接同一 URL 可恢复登录状态 |
| `partition:{timestamp}` | ❌ | 临时 session，关闭窗口后清除数据 |

- `persistSessionData=true`（默认）→ 使用 `persist:` 前缀
- `persistSessionData=false` → 使用 `partition:` 前缀
- 删除远程会话记录时，`persist:` 前缀的 session 调用 `clearSession()` 清除数据

### SessionConfig 序列化

`SessionConfig.serialize()` 只保存非默认值，减小文件体积：

```typescript
serialize(): any {
  const jsonData: any = {
    x: this.x, y: this.y,
    width: this.width, height: this.height,
    lastOpened: this.lastOpened.toISOString()
  };
  // 有值才写入
  if (this.remoteURL) jsonData.remoteURL = this.remoteURL;
  if (this.workingDirectory) jsonData.workingDirectory = this.workingDirectory;
  if (this.filesToOpen.length > 0) jsonData.filesToOpen = [...this.filesToOpen];
  // persistSessionData 为 false 时才写入（默认 true 不写）
  if (this.persistSessionData === false) jsonData.persistSessionData = false;
  if (this.persistSessionData) jsonData.partition = this.partition;
  return jsonData;
}
```

## 会话恢复（StartupMode.LastSessions）

当启动模式设置为"恢复上次会话"时：

1. 从 `appData.sessions` 读取上次关闭时的活动会话列表
2. 对每个 SessionConfig 调用 `sessionWindowManager.restoreLabWindow(config)`
3. 使用 `restorePosition=true` 恢复窗口位置和尺寸

### 启动模式优先级

1. **CLI 参数最高**：命令行指定了文件/目录/URL → 直接打开，忽略启动模式
2. **StartupMode 设置**：
   - `WelcomePage`：显示欢迎页
   - `NewLocalSession`：创建新的本地会话
   - `LastSessions`：恢复上次会话
3. **默认**：WelcomePage

## 窗口关闭流程

```
用户关闭窗口
  │
  ├─→ 保存窗口位置和尺寸到 sessionConfig
  ├─→ 将会话添加到最近会话列表
  ├─→ 停止关联的 JupyterServer（本地会话）
  │     └─→ serverFactory.stopServer(factoryId)
  │           ├─→ Windows: taskkill /T /F
  │           └─→ 其他: API shutdown + kill 兜底
  ├─→ 清理子视图（TitleBarView、LabView/WelcomeView）
  ├─→ 从 SessionWindowManager 列表中移除
  └─→ BrowserWindow.destroy()
```

窗口关闭后，`createFreeServersIfNeeded()` 补充空闲服务器池。

## 应用退出流程

```
app.on('will-quit')
  │
  ├─→ appData.save()           ← 保存所有持久化数据
  ├─→ userSettings.save()      ← 保存设置
  └─→ jupyterApp.dispose()
       ├─→ sessionWindowManager.dispose()  ← 关闭所有窗口
       ├─→ serverFactory.killAllServers()  ← 停止所有服务器
       ├─→ eventManager.dispose()          ← 注销所有 IPC 事件
       └─→ registry.dispose()              ← 等待环境发现完成
```

## 远程服务器管理

### 远程 URL 历史

`appData.recentRemoteURLs: IRecentRemoteURL[]` 保存用户连接过的远程服务器 URL，支持去重和按日期排序。

### 运行中服务器发现

`Registry.getRunningServerList()` 通过执行 `jupyter server list --json` 发现外部运行的 Jupyter 服务器：

- 过滤掉桌面应用自己启动的服务器（token 以 `jlab:srvr:` 开头）
- 检查端口是否仍在使用
- 返回完整 URL 列表供用户连接

## 文件打开方式

| 打开方式 | 处理流程 |
|---------|---------|
| 菜单/欢迎页"打开文件" | 文件对话框 → 创建 SessionConfig（文件所在目录为工作目录） |
| 菜单/欢迎页"打开文件夹" | 目录对话框 → SessionConfig.createLocal(dir) |
| CLI 位置参数 | SessionConfig.createFromArgs(argv) |
| macOS Dock/双击文件 | app.on('open-file') → 缓存路径 → 应用就绪后打开 |
| 拖拽文件到窗口 | OpenDroppedFiles IPC 事件 |
| 第二实例 CLI 参数 | second-instance 事件 → 传递文件路径到第一实例 |

## 相关信源

- [App 信源](../references/app-source.md)
- [SessionWindow 信源](../references/sessionwindow-source.md)
- [Config 信源](../references/config-source.md)
- [Main 信源](../references/main-source.md)

## 下一篇

- [构建与开发指南](11-build-development.md)

## 相关概念

- [会话窗口系统](03-session-window-system.md) — 单个 SessionWindow 的生命周期与 UI 管理
- [Jupyter 服务器管理](04-server-management.md) — 多窗口下 Factory 模式管理多个服务器实例
- [安全与导航策略](09-security-navigation.md) — 多窗口环境下的导航安全守卫
- [应用入口与生命周期](02-app-entry-lifecycle.md) — 单实例锁与 second-instance 事件处理
- [构建与开发指南](11-build-development.md) — 开发环境搭建与应用构建流程
