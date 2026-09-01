---
okf_version: "0.2"
type: reference
title: "插件入口源码（src/index.ts）"
description: "JupyterLab GitHub 扩展的插件注册入口，包含插件定义、激活函数、设置系统集成与安全警告对话框"
tags: [plugin, entry-point, activation, settings, security-dialog, labicon]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: index-ts
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/src/index.ts"
    title: "src/index.ts"
---

# 插件入口源码（src/index.ts）

本信源登记 `src/index.ts`（约171行），这是 JupyterLab GitHub 扩展的前端入口文件，负责插件注册、依赖注入、Drive 挂载和 UI 初始化。

## 导出项

### 默认导出：fileBrowserPlugin

类型 `JupyterFrontEndPlugin<void>`，插件元数据：

| 属性 | 值 |
|------|-----|
| `id` | `'@jupyterlab/github:drive'` |
| `requires` | `[IDocumentManager, IFileBrowserFactory, ISettingRegistry]` |
| `optional` | `[ILayoutRestorer]` |
| `activate` | `activateFileBrowser` |
| `autoStart` | `true` |

### 命名导出：gitHubIcon

`LabIcon` 实例，使用 octocat-light.svg 作为图标源，name 为 `'github-filebrowser:icon'`。

## 常量

| 常量 | 值 | 用途 |
|------|-----|------|
| `NAMESPACE` | `'github-filebrowser'` | 插件状态命名空间，用于布局恢复 |
| `PLUGIN_ID` | `'@jupyterlab/github:drive'` | 插件唯一标识符 |

## activateFileBrowser 函数

签名：`function activateFileBrowser(app: JupyterFrontEnd, manager: IDocumentManager, factory: IFileBrowserFactory, settingRegistry: ISettingRegistry, restorer: ILayoutRestorer | null): void`

执行流程：

1. **创建并注册 Drive**：`new GitHubDrive(app.docRegistry)` → `manager.services.contents.addDrive(drive)`
2. **创建文件浏览器**：`factory.createFileBrowser(NAMESPACE, { driveName: drive.name, refreshInterval: 300000 })`——5分钟刷新间隔
3. **包装为 GitHubFileBrowser**：设置图标（`gitHubIcon`）、标题（`'Browse GitHub'`）、ID（`'github-file-browser'`）
4. **注册布局恢复**：如果 `restorer` 存在，调用 `restorer.add(gitHubBrowser, NAMESPACE)`
5. **添加到左侧面板**：`app.shell.add(gitHubBrowser, 'left', { rank: 102 })`
6. **设置监听**：注册 `onSettingsUpdated` 回调处理 `baseUrl` 和 `accessToken` 变更
7. **初始加载**：`Promise.all([settingRegistry.load(PLUGIN_ID), app.restored])` 后连接 settings.changed 信号，处理 defaultRepo 自动导航

### 设置更新逻辑（onSettingsUpdated）

- 读取 `baseUrl` 设置（默认 `DEFAULT_GITHUB_BASE_URL`）
- 读取 `accessToken` 设置：有 token 时弹出安全警告对话框（首次加载不弹），用户确认后设置 `drive.accessToken`；取消则移除设置项
- 无 token 时设为 `null`

### 默认仓库导航

- 读取 `defaultRepo` 设置（格式 `'owner/repository'`）
- 浏览器模型恢复后执行 `browser.model.cd('/${defaultRepo}')`

## Private 命名空间

### showWarning(): Promise\<boolean\>

显示安全警告对话框（`showDialog`）：
- 标题：`'Security Alert!'`
- 内容：警告客户端 access token 的安全风险，建议使用服务端扩展
- 按钮：CANCEL（cancelButton）和 PROCEED（warnButton）
- 返回：用户接受返回 `true`，取消返回 `false`
