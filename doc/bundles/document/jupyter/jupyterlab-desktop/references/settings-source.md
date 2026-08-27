---
type: Reference
title: 设置与配置系统源码信源
description: src/main/config/settings.ts 设置系统源码登记，包含 SettingType 枚举、Setting 泛型类、UserSettings 全局设置、WorkspaceSettings 工作区设置
tags: [settings, configuration, user-settings, workspace-settings, defaults, override]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: settings-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/config/settings.ts
    title: settings.ts source on GitHub
---

# 设置与配置系统源码信源

## 源码路径

`src/main/config/settings.ts`

## 文件职责

实现双层设置系统：全局用户设置（`UserSettings`）和工作区级设置（`WorkspaceSettings`），支持设置项的默认值、覆盖检测、JSON 持久化。

## 枚举类型

### ThemeType

```typescript
enum ThemeType {
  System = 'system',
  Light = 'light',
  Dark = 'dark'
}
```

### StartupMode

```typescript
enum StartupMode {
  WelcomePage = 'welcome-page',
  NewLocalSession = 'new-local-session',
  LastSessions = 'restore-sessions'
}
```

### LogLevel

```typescript
enum LogLevel {
  Error = 'error',
  Warn = 'warn',
  Info = 'info',
  Verbose = 'verbose',
  Debug = 'debug'
}
```

### CtrlWBehavior

```typescript
enum CtrlWBehavior {
  CloseWindow = 'close',
  Warn = 'warn',
  CloseTab = 'close-tab',
  DoNotClose = 'do-not-close'
}
```

### UIMode

```typescript
enum UIMode {
  MultiDocument = 'multi-document',
  SingleDocument = 'single-document',
  Zen = 'zen',
  ManagedByWebApp = 'managed-by-web-app'
}
```

## SettingType 枚举（完整设置键列表）

| 键 | 类型 | 默认值 | 可工作区覆盖 | 说明 |
|----|------|--------|-------------|------|
| `checkForUpdatesAutomatically` | boolean | true | 否 | 自动检查更新 |
| `installUpdatesAutomatically` | boolean | true | 否 | 自动安装更新 |
| `notifyOnBundledEnvUpdates` | boolean | true | 否 | 捆绑环境更新通知 |
| `updateBundledEnvAutomatically` | boolean | false | 否 | 自动更新捆绑环境 |
| `theme` | ThemeType | System | 否 | 主题（不可工作区覆盖，多窗口主题一致性） |
| `syncJupyterLabTheme` | boolean | true | 否 | 同步 JupyterLab 主题 |
| `showNewsFeed` | boolean | true | 否 | 显示新闻订阅 |
| `defaultWorkingDirectory` | string | ''（用户主目录） | 否 | 默认工作目录 |
| `pythonPath` | string | '' | 是 | 默认 Python 路径 |
| `serverArgs` | string | '' | 是 | 服务器启动附加参数 |
| `overrideDefaultServerArgs` | boolean | false | 是 | 覆盖默认服务器参数 |
| `serverEnvVars` | KeyValueMap | {} | 是 | 服务器环境变量 |
| `startupMode` | StartupMode | WelcomePage | 否 | 启动模式 |
| `ctrlWBehavior` | CtrlWBehavior | CloseTab | 否 | Ctrl+W 行为 |
| `logLevel` | string | Warn | 否 | 日志级别 |
| `condaPath` | string | '' | 否 | Conda 路径 |
| `systemPythonPath` | string | '' | 否 | 系统 Python 路径 |
| `pythonEnvsPath` | string | '' | 否 | Python 环境安装目录 |
| `condaChannels` | string[] | ['conda-forge'] | 否 | Conda channels |
| `uiMode` | UIMode | ManagedByWebApp | 是 | UI 模式 |
| `uiModeForSingleFileOpen` | UIMode | Zen | 否 | 单文件打开时 UI 模式 |
| `showTOCInZenMode` | boolean | false | 否 | Zen 模式显示目录 |

## 服务器启动参数常量

### serverLaunchArgsFixed（固定参数，不可覆盖）

```typescript
[
  '--no-browser',
  '--expose-app-in-browser',
  '--ServerApp.port={port}',
  '--ServerApp.password=""',
  '--ServerApp.token="{token}"',
  '--LabApp.quit_button=False'
]
```

### serverLaunchArgsDefault（默认参数，可覆盖）

```typescript
[
  '--JupyterApp.config_file_name=""',
  '--ContentsManager.allow_hidden=True'
]
```

## Setting<T> 泛型类

```typescript
class Setting<T> {
  constructor(defaultValue: T, options?: Setting.IOptions);
  get value(): T;           // 返回设置值（未设置则返回默认值）
  set value(val: T);        // 设置值
  get valueSet(): boolean;  // 是否已设置
  get differentThanDefault(): boolean;  // 是否与默认值不同
  get wsOverridable(): boolean;         // 是否可被工作区覆盖
  setToDefault();           // 重置为默认值
}
```

## UserSettings 类

全局设置单例，持久化到 `{userDataDir}/settings.json`。

| 方法/属性 | 说明 |
|-----------|------|
| `constructor(readSettings=true)` | 构造时自动从文件读取 |
| `getValue(setting)` | 获取设置值 |
| `setValue(setting, value)` | 设置值（不立即保存） |
| `unsetValue(setting)` | 重置为默认值 |
| `read()` | 从 JSON 文件读取设置 |
| `save()` | 保存非默认设置到 JSON 文件（只保存 differentThanDefault 的项） |
| `resolvedWorkingDirectory` | 解析后的工作目录（空则回退到用户主目录，无效路径也回退） |
| `settings` | 获取全部设置对象 |

### 保存策略

`save()` 方法只将 `differentThanDefault` 的设置项写入文件，避免存储冗余默认值。

## WorkspaceSettings 类

继承自 `UserSettings`，工作区级设置，持久化到 `{workingDirectory}/.jupyter/desktop-settings.json`。

| 方法 | 说明 |
|------|------|
| `constructor(workingDirectory)` | 先读取全局设置，再读取工作区设置覆盖 |
| `getValue(setting)` | 优先返回工作区设置值，否则返回全局设置值 |
| `setValue(setting, value)` | 设置工作区级值 |
| `unsetValue(setting)` | 删除工作区级覆盖 |
| `hasValue(setting)` | 检查工作区是否有该设置 |
| `save()` | 保存工作区设置（uiMode 特殊处理：即使与全局默认相同也保存） |

### 工作区设置覆盖规则

只有标记为 `wsOverridable: true` 的设置项才能被工作区覆盖。当尝试覆盖不可覆盖项时静默忽略。

## resolveWorkingDirectory() 函数

```typescript
function resolveWorkingDirectory(workingDirectory: string, resetIfInvalid: boolean = true): string
```

- 空路径解析为用户主目录
- `resetIfInvalid=true` 时，路径不存在或不是目录则回退到主目录

## 相关概念

- [设置与配置系统](../concepts/06-settings-config.md)
- [Python 环境管理](../concepts/05-python-env-management.md)
