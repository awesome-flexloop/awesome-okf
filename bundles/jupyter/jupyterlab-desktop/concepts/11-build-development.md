---
type: Concept
title: 构建与开发指南
description: JupyterLab Desktop 的项目结构、构建系统、开发环境搭建、electron-builder 打包配置、关键依赖版本、开发工作流
tags: [build, development, electron-builder, project-structure, dependencies, dev-workflow]
prerequisites:
  - /concepts/00-introduction.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: main-source
    resource: /references/main-source.md
    title: 应用入口源码信源
  - id: app-source
    resource: /references/app-source.md
    title: 主应用类源码信源
  - id: server-source
    resource: /references/server-source.md
    title: Jupyter服务器源码信源
---

# 构建与开发指南

## 项目结构

```
jupyterlab-desktop/
├── package.json              # 项目配置、依赖、构建脚本
├── tsconfig.json             # TypeScript 配置
├── webpack.config.js         # Webpack 打包配置（如适用）
├── electron-builder.yml      # electron-builder 打包配置
├── src/
│   ├── main/                 # 主进程代码（TypeScript）
│   │   ├── main.ts           # 应用入口
│   │   ├── app.ts            # JupyterApplication
│   │   ├── server.ts         # JupyterServer + Factory
│   │   ├── env.ts            # Python 环境管理
│   │   ├── cli.ts            # CLI 命令
│   │   ├── registry.ts       # Python 环境注册表
│   │   ├── tokens.ts         # 类型定义
│   │   ├── eventtypes.ts     # IPC 事件类型
│   │   ├── eventmanager.ts   # IPC 事件管理器
│   │   ├── navigationguard.ts # 导航安全守卫
│   │   ├── utils.ts          # 工具函数
│   │   ├── connect.ts        # 远程服务器连接
│   │   ├── config/           # 配置模块
│   │   │   ├── settings.ts   # UserSettings/WorkspaceSettings
│   │   │   ├── appdata.ts    # ApplicationData
│   │   │   └── sessionconfig.ts # SessionConfig
│   │   ├── sessionwindow/    # 会话窗口
│   │   ├── labview/          # Lab 视图
│   │   ├── titlebarview/     # 自定义标题栏
│   │   ├── welcomeview/      # 欢迎页
│   │   ├── settingsdialog/   # 设置对话框
│   │   ├── pythonenvdialog/  # Python 环境管理对话框
│   │   ├── updatedialog/     # 更新对话框
│   │   ├── authwindow/       # 认证窗口
│   │   ├── authdialog/       # 认证对话框
│   │   ├── progressview/     # 进度视图
│   │   ├── pythonenvselectpopup/ # 环境选择弹窗
│   │   ├── remoteserverselectdialog/ # 远程服务器选择
│   │   ├── aboutdialog/      # 关于对话框
│   │   └── dialog/           # 对话框基类
│   └── renderer/             # 渲染进程代码（如适用）
├── resources/                # 静态资源（图标、HTML模板等）
├── env_installer/            # Python 环境安装脚本
│   └── env_info.py           # 环境信息获取脚本
├── test/                     # 测试
└── dist/                     # 构建输出
```

## 关键依赖版本（基于 package.json 分析）

| 依赖 | 版本 | 用途 |
|------|------|------|
| `electron` | 42.x | 桌面应用框架 |
| `electron-builder` | 26.x | 应用打包与安装程序生成 |
| `typescript` | - | 主进程语言 |
| `@lumino/signaling` | - | 信号/事件机制 |
| `semver` | - | 版本号比较 |
| `yargs` | - | CLI 参数解析 |
| `electron-log` | - | 日志管理 |
| `ejs` | - | 模板引擎（生成启动脚本等） |
| `which` | v7+ | PATH 中查找可执行文件 |
| `winreg` | - | Windows 注册表访问 |
| `fix-path` | - | macOS PATH 修复 |
| `update-electron-app` | - | macOS 自动更新 |
| `node-fetch` / `net` | - | HTTP 请求（更新检查） |

## Python 依赖

捆绑环境中安装的核心 Python 包：
- `jupyterlab >= 3.0.0`（最低要求）
- `jupyter_server`（Jupyter 服务器）
- `ipykernel`（Python kernel）
- 常用数据科学包（numpy、pandas 等，视捆绑配置而定）

## 开发环境搭建

### 前置要求

- Node.js（推荐 LTS 版本）
- npm 或 yarn
- Python 3.x（用于运行 JupyterLab，开发时可用系统 Python 代替捆绑环境）
- Conda（可选，用于 conda 环境管理）

### 安装依赖

```bash
git clone https://github.com/jupyterlab/jupyterlab-desktop.git
cd jupyterlab-desktop
npm install
```

### 开发模式运行

```bash
npm run start        # 启动开发模式
# 或
npm run dev
```

开发模式特性：
- 日志输出到 console（非文件）
- devTools 启用
- 支持热重载（视配置而定）

### 构建应用

```bash
npm run build        # 编译 TypeScript
npm run dist         # 打包安装程序（使用 electron-builder）
```

## electron-builder 打包配置

打包生成以下平台安装包：

| 平台 | 格式 |
|------|------|
| Windows | NSIS 安装程序 (.exe)、便携版 |
| macOS | DMG、zip |
| Linux | AppImage、deb、rpm、Snap |

### 打包内容

- 编译后的 JavaScript 代码
- HTML/CSS 等静态资源
- 捆绑 Python 环境（conda-pack 归档）
- 应用图标
- electron-builder 自动生成的安装程序

## 应用数据位置

| 数据 | 路径 |
|------|------|
| 设置 | `{userDataDir}/settings.json` |
| 应用数据 | `{userDataDir}/app-data.json` |
| 日志 | `{app.getPath('logs')}/main.log` 等 |
| 捆绑环境 | `{app.getPath('userData')}/env/` |
| 用户创建的环境 | `{userDataDir}/envs/`（默认） |

`userDataDir` 因平台而异：
- Windows: `%APPDATA%/jupyterlab-desktop/`
- macOS: `~/Library/Application Support/jupyterlab-desktop/`
- Linux: `~/.config/jupyterlab-desktop/`（Snap 路径不同）

## Snap 包特殊处理

Linux Snap 包有严格的文件系统隔离，需要特殊路径处理：

- `XDG_CONFIG_HOME`、`XDG_DATA_HOME`、`XDG_CACHE_HOME` 需重定向到 Snap 的 common 目录
- `updatePathsForSnap()` 是启动序列的第一步
- 捆绑环境在 Snap 中路径不同

## 自动更新机制

### macOS

使用 `update-electron-app` 模块：
- 基于 Squirrel.Mac 自动更新框架
- 后台下载更新
- 下载完成后弹出"Restart / Later"对话框
- 支持 `installUpdatesAutomatically` 设置

### Windows/Linux

手动检查更新：
- `checkForUpdates()` 从 GitHub Releases 获取 `latest.yml`
- 使用 semver 比较版本号
- 有新版本时显示 UpdateDialog，链接到下载页面
- `checkForUpdatesAutomatically` 控制启动时是否自动检查

## 添加新 IPC 事件

1. 在 `eventtypes.ts` 的 `EventTypeMain` 或 `EventTypeRenderer` 枚举中添加事件名
2. 在对应组件中调用 `eventManager.registerEventHandler()` 或 `registerSyncEventHandler()`
3. 在渲染进程的 preload 脚本中添加对应的 IPC 调用
4. 在渲染进程 UI 中使用暴露的 API

**注意**：`eventtypes.ts` 会被打包到 preload.js 中，保持文件精简。

## 添加新设置项

1. 在 `settings.ts` 的 `SettingType` 枚举中添加键
2. 创建 `Setting<T>` 实例，指定默认值和 `wsOverridable` 选项
3. 在设置 UI 中添加对应的控件
4. 如需持久化，确保 `save()` 方法能正确处理（只保存 non-default 值）

## 日志系统

使用 `electron-log`：

```typescript
import log from 'electron-log';

log.error('Error message');
log.warn('Warning message');
log.info('Info message');
log.verbose('Verbose message');
log.debug('Debug message');
```

日志级别通过 `--log-level` CLI 参数或 `logLevel` 设置控制。

生产模式日志写入文件，开发模式输出到 console。

## 测试

项目包含单元测试（`test/unit/`），使用 Jest 或类似框架：

```bash
npm test
```

测试文件示例：
- `sessionwindow-titlebar-bounds.test.ts` - 标题栏边界计算测试
- `sessionwindow-dispose.test.ts` - 窗口清理测试

## 相关信源

- [Main 信源](/references/main-source.md)
- [App 信源](/references/app-source.md)
- [Server 信源](/references/server-source.md)

## 相关概念

- [JupyterLab Desktop 简介](/concepts/00-introduction.md) — 技术栈与核心特性概览
- [架构概览](/concepts/01-architecture-overview.md) — 核心模块与目录结构
- [应用入口与生命周期](/concepts/02-app-entry-lifecycle.md) — 开发模式下的启动流程
- [设置与配置系统](/concepts/06-settings-config.md) — 添加新设置项的完整流程
- [事件与IPC系统](/concepts/08-event-ipc-system.md) — 添加新 IPC 事件的标准步骤
