---
type: Concept
title: 设置与配置系统
description: UserSettings 与 WorkspaceSettings 双层设置系统、SettingType 枚举、设置项默认值与覆盖机制、设置持久化、服务器启动参数配置
tags: [settings, configuration, user-settings, workspace-settings, defaults, override, persistence]
prerequisites:
  - /concepts/05-python-env-management.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: settings-source
    resource: /references/settings-source.md
    title: 设置系统源码信源
  - id: config-source
    resource: /references/config-source.md
    title: 应用数据与会话配置源码信源
---

# 设置与配置系统

## 概述

JupyterLab Desktop 采用双层设置系统：全局用户设置（UserSettings）和工作区级设置（WorkspaceSettings）。工作区设置可以覆盖部分全局设置，实现每个项目目录独立配置。

## 设置枚举类型

### ThemeType - 主题

```typescript
enum ThemeType {
  System = 'system',   // 跟随系统
  Light = 'light',     // 亮色主题
  Dark = 'dark'        // 暗色主题
}
```

### StartupMode - 启动模式

```typescript
enum StartupMode {
  WelcomePage = 'welcome-page',       // 欢迎页面（默认）
  NewLocalSession = 'new-local-session', // 新建本地会话
  LastSessions = 'restore-sessions'   // 恢复上次会话
}
```

### LogLevel - 日志级别

```typescript
enum LogLevel {
  Error = 'error',
  Warn = 'warn',     // 默认
  Info = 'info',
  Verbose = 'verbose',
  Debug = 'debug'
}
```

### CtrlWBehavior - Ctrl+W 行为

```typescript
enum CtrlWBehavior {
  CloseWindow = 'close',
  Warn = 'warn',
  CloseTab = 'close-tab',  // 默认
  DoNotClose = 'do-not-close'
}
```

### UIMode - UI 模式

```typescript
enum UIMode {
  MultiDocument = 'multi-document',
  SingleDocument = 'single-document',
  Zen = 'zen',
  ManagedByWebApp = 'managed-by-web-app'  // 默认
}
```

## Setting<T> 泛型类

所有设置项都通过 `Setting<T>` 类管理，提供类型安全的设置访问：

```typescript
class Setting<T> {
  constructor(defaultValue: T, options?: { wsOverridable?: boolean });

  get value(): T;              // 获取值（未设置返回默认值）
  set value(val: T);           // 设置值
  get valueSet(): boolean;     // 是否已设置（非默认）
  get differentThanDefault(): boolean;  // 是否与默认值不同
  get wsOverridable(): boolean;         // 是否可被工作区覆盖
  setToDefault();              // 重置为默认值
}
```

## 完整设置项列表（SettingType）

| 设置键 | 类型 | 默认值 | 可工作区覆盖 | 说明 |
|--------|------|--------|-------------|------|
| `checkForUpdatesAutomatically` | boolean | `true` | ❌ | 自动检查更新 |
| `installUpdatesAutomatically` | boolean | `true` | ❌ | 自动安装更新（macOS） |
| `notifyOnBundledEnvUpdates` | boolean | `true` | ❌ | 捆绑环境更新通知 |
| `updateBundledEnvAutomatically` | boolean | `false` | ❌ | 自动更新捆绑环境 |
| `theme` | ThemeType | `System` | ❌ | 主题（全局统一，避免多窗口主题不一致） |
| `syncJupyterLabTheme` | boolean | `true` | ❌ | 同步 JupyterLab Web 主题与桌面主题 |
| `showNewsFeed` | boolean | `true` | ❌ | 显示新闻订阅 |
| `defaultWorkingDirectory` | string | `''`（用户主目录） | ❌ | 默认工作目录 |
| `pythonPath` | string | `''` | ✅ | Python 解释器路径 |
| `serverArgs` | string | `''` | ✅ | Jupyter Server 附加启动参数 |
| `overrideDefaultServerArgs` | boolean | `false` | ✅ | 是否覆盖默认服务器参数 |
| `serverEnvVars` | KeyValueMap | `{}` | ✅ | 服务器环境变量 |
| `startupMode` | StartupMode | `WelcomePage` | ❌ | 启动模式 |
| `ctrlWBehavior` | CtrlWBehavior | `CloseTab` | ❌ | Ctrl+W 快捷键行为 |
| `logLevel` | string | `Warn` | ❌ | 日志级别 |
| `condaPath` | string | `''` | ❌ | Conda 可执行文件路径 |
| `systemPythonPath` | string | `''` | ❌ | 系统 Python 路径 |
| `pythonEnvsPath` | string | `''` | ❌ | Python 环境安装目录 |
| `condaChannels` | string[] | `['conda-forge']` | ❌ | Conda channels |
| `uiMode` | UIMode | `ManagedByWebApp` | ✅ | UI 显示模式 |
| `uiModeForSingleFileOpen` | UIMode | `Zen` | ❌ | 单文件打开时 UI 模式 |
| `showTOCInZenMode` | boolean | `false` | ❌ | Zen 模式显示目录 |

## UserSettings 类（全局设置）

### 持久化位置

`{userDataDir}/settings.json`

### 保存策略

`save()` 方法只保存 `differentThanDefault` 的设置项，避免存储冗余默认值。空文件或缺失字段使用默认值。

### 关键方法

| 方法 | 说明 |
|------|------|
| `getValue(setting)` | 获取设置值 |
| `setValue(setting, value)` | 设置值（不立即保存） |
| `unsetValue(setting)` | 重置为默认值 |
| `read()` | 从 JSON 文件读取 |
| `save()` | 保存非默认值到文件 |
| `resolvedWorkingDirectory` | 解析后的工作目录（空/无效路径回退到用户主目录） |
| `settings` | 获取全部设置对象（Setting 实例集合） |

### 工作目录解析

`resolvedWorkingDirectory` getter：
1. 如果 `defaultWorkingDirectory` 为空，返回用户主目录
2. 如果路径不存在或不是目录，回退到用户主目录
3. 否则返回设置的工作目录

## WorkspaceSettings 类（工作区设置）

继承自 `UserSettings`，实现工作区级别的设置覆盖。

### 持久化位置

`{workingDirectory}/.jupyter/desktop-settings.json`

### 覆盖规则

```
读取设置值的优先级：
1. 工作区设置文件中的值（如果存在且该设置可覆盖）
2. 全局设置值
3. 默认值
```

### 关键方法

| 方法 | 说明 |
|------|------|
| `getValue(setting)` | 优先返回工作区值，否则全局值 |
| `setValue(setting, value)` | 设置工作区级值（不可覆盖项静默忽略） |
| `unsetValue(setting)` | 删除工作区级覆盖 |
| `hasValue(setting)` | 工作区是否有该设置 |
| `save()` | 保存工作区设置 |

### 特殊处理

`uiMode` 即使与全局默认值相同也会保存到工作区设置文件（因为这是显式的工作区选择）。

## 服务器启动参数

### 固定参数（不可修改）

```typescript
const serverLaunchArgsFixed = [
  '--no-browser',
  '--expose-app-in-browser',
  '--ServerApp.port={port}',
  '--ServerApp.password=""',
  '--ServerApp.token="{token}"',
  '--LabApp.quit_button=False'
];
```

这些参数确保服务器在桌面应用中正确运行，用户无法覆盖。

### 默认参数（可覆盖）

```typescript
const serverLaunchArgsDefault = [
  '--JupyterApp.config_file_name=""',
  '--ContentsManager.allow_hidden=True'
];
```

- `--JupyterApp.config_file_name=""`：不加载用户全局 Jupyter 配置，确保桌面环境独立
- `--ContentsManager.allow_hidden=True`：允许访问隐藏文件（如 `.jupyter/` 目录）

用户可通过 `overrideDefaultServerArgs=true` + `serverArgs` 覆盖这些默认参数。

### 用户自定义参数

通过 `serverArgs` 设置项添加附加参数，追加在固定参数和默认参数之后。

## 窗口尺寸默认值

```typescript
const DEFAULT_WIN_WIDTH = 1024;
const DEFAULT_WIN_HEIGHT = 768;
```

## 设置文件格式

### 全局设置（settings.json）

```json
{
  "theme": "dark",
  "pythonPath": "/usr/local/bin/python3",
  "startupMode": "restore-sessions",
  "checkForUpdatesAutomatically": true
}
```

### 工作区设置（.jupyter/desktop-settings.json）

```json
{
  "pythonPath": "/home/user/myproject/venv/bin/python",
  "serverArgs": "--ServerApp.root_dir=/data",
  "serverEnvVars": {
    "MY_VAR": "value"
  }
}
```

## 相关信源

- [Settings 信源](/references/settings-source.md)
- [Config 信源](/references/config-source.md)

## 下一篇

- [CLI 命令系统](/concepts/07-cli-system.md)
- [事件与IPC系统](/concepts/08-event-ipc-system.md)

## 相关概念

- [Python 环境管理](/concepts/05-python-env-management.md) — pythonPath、condaPath 等设置项用于环境管理
- [CLI 命令系统](/concepts/07-cli-system.md) — jlab config 子命令通过 CLI 读写设置
- [事件与IPC系统](/concepts/08-event-ipc-system.md) — 设置变更通过 IPC 事件通知渲染进程
