---
type: Reference
title: 应用数据与会话配置源码信源
description: src/main/config/appdata.ts 和 src/main/config/sessionconfig.ts 应用数据持久化与会话配置源码登记，包含 ApplicationData 单例、SessionConfig 类、序列化/反序列化、最近会话管理
tags: [appdata, sessionconfig, persistence, serialization, recent-sessions, singleton]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: appdata-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/config/appdata.ts
    title: appdata.ts source on GitHub
  - id: sessionconfig-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/config/sessionconfig.ts
    title: sessionconfig.ts source on GitHub
---

# 应用数据与会话配置源码信源

## 源码路径

- `src/main/config/appdata.ts` - 应用级数据持久化
- `src/main/config/sessionconfig.ts` - 单个会话配置

---

## ApplicationData 类（appdata.ts）

单例模式，通过 `appData = ApplicationData.getSingleton()` 导出全局实例。

### 数据文件位置

`{userDataDir}/app-data.json`（通过 `getUserDataDir()` 获取 userData 目录）。

### 持久化字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `pythonPath` | `string` | `''` | 发现的默认 Python 路径 |
| `condaPath` | `string` | `''` | 发现的 Conda 可执行文件路径 |
| `systemPythonPath` | `string` | `''` | 发现的系统 Python 路径 |
| `sessions` | `SessionConfig[]` | `[]` | 当前活动会话配置 |
| `recentSessions` | `IRecentSession[]` | `[]` | 最近会话列表（最多20个） |
| `recentRemoteURLs` | `IRecentRemoteURL[]` | `[]` | 最近远程 URL 列表 |
| `discoveredPythonEnvs` | `IPythonEnvironment[]` | `[]` | 自动发现的 Python 环境（缓存） |
| `userSetPythonEnvs` | `IPythonEnvironment[]` | `[]` | 用户手动添加的环境 |
| `newsList` | `INewsItem[]` | `[]` | 新闻列表 |
| `updateBundledEnvOnRestart` | `boolean` | `false` | 重启时更新捆绑环境标志 |

### 关键方法

| 方法 | 说明 |
|------|------|
| `read()` | 从 JSON 文件读取数据，兼容旧版 `condaRootPath` 字段（迁移为 condaPath） |
| `save()` | 序列化为 JSON 写入文件，空字段不写入 |
| `addRemoteURLToRecents(url)` | 添加远程 URL 到最近列表（去重，更新日期） |
| `removeRemoteURLFromRecents(url)` | 从最近列表移除 URL |
| `addSessionToRecents(session)` | 添加会话到最近列表（本地：工作目录+文件匹配；远程：URL 匹配），超过 MAX_RECENT_SESSIONS(20) 时删除最旧的 |
| `removeSessionFromRecents(index)` | 删除指定索引的最近会话，清除 persist partition 的 session 数据 |
| `setActiveSessions(sessionConfigs)` | 设置当前活动会话列表 |

### 最近会话排序

按 `date` 降序排列（最新在前）。

### 持久化 session 清理

删除远程会话时，若 `partition` 以 `persist:` 开头，调用 `clearSession(electronSession.fromPartition(partition))` 清除持久化的 cookie/缓存数据。

---

## SessionConfig 类（sessionconfig.ts）

描述单个 Jupyter 会话的完整配置。

### 属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `x`, `y` | `number` | 0 | 窗口位置 |
| `width` | `number` | 1024(DEFAULT_WIN_WIDTH) | 窗口宽度 |
| `height` | `number` | 768(DEFAULT_WIN_HEIGHT) | 窗口高度 |
| `remoteURL` | `string` | `''` | 远程服务器 URL（空表示本地会话） |
| `persistSessionData` | `boolean` | `true` | 是否持久化远程会话数据 |
| `partition` | `string` | `''` | Electron session partition |
| `workingDirectory` | `string` | `''` | 工作目录 |
| `filesToOpen` | `string[]` | `[]` | 要打开的文件列表 |
| `pythonPath` | `string` | `''` | 会话使用的 Python 路径 |
| `defaultKernel` | `string` | `''` | 默认 kernel 名称 |
| `lastOpened` | `Date` | `new Date()` | 最后打开时间 |
| `url` | `URL` | - | 服务器 URL（运行时填充） |
| `token` | `string` | - | 服务器 token（运行时填充） |
| `pageConfig` | `any` | - | 页面配置（运行时填充） |
| `cookies` | `Electron.Cookie[]` | - | Cookie 数据 |

### 静态工厂方法

| 方法 | 说明 |
|------|------|
| `SessionConfig.createLocal(workingDirectory?, filesToOpen?, pythonPath?)` | 创建本地会话配置，默认值从 userSettings 获取 |
| `SessionConfig.createLocalForFilesOrFolders(fileOrFolders?)` | 从文件/文件夹路径列表创建，文件取第一个文件所在目录为工作目录 |
| `SessionConfig.createRemote(remoteURL, persistSessionData, partition?)` | 创建远程会话配置，解析 URL 获取 token，自动生成 partition（persist: 或 partition: 前缀+时间戳） |
| `SessionConfig.createFromArgs(cliArgs)` | 从 CLI 参数创建，自动检测 URL（远程）或本地路径 |

### 计算属性

| 属性 | 说明 |
|------|------|
| `isRemote` | `remoteURL !== ''` |
| `resolvedWorkingDirectory` | 调用 `resolveWorkingDirectory(workingDirectory)` 解析为有效路径 |

### 序列化/反序列化

- `serialize()` → JSON 对象：仅保存非默认值（如 remoteURL 非空、filesToOpen 非空时才写入）
- `deserialize(jsonData)` → 从 JSON 恢复：兼容缺失字段，日期字符串转为 Date 对象

### setFilesToOpen(filePaths)

验证文件是否存在（在 resolvedWorkingDirectory 下），仅添加实际存在的文件。

## 相关概念

- [会话窗口系统](/concepts/03-session-window-system.md)
- [设置与配置系统](/concepts/06-settings-config.md)
