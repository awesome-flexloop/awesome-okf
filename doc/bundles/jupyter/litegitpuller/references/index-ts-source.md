---
type: Reference
title: src/index.ts 插件入口源码信源
description: litegitpuller JupyterLab扩展入口文件src/index.ts的源码结构、导出函数和插件激活逻辑信源登记
tags: [typescript, jupyterlab-extension, plugin-entry, url-parameters, nbgitpuller-detection]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-index-ts
    resource: /references/index-ts-source.md
    title: src/index.ts 插件入口源码信源
---

## 文件位置

源码路径：`src/index.ts`（TypeScript），编译后输出为 `lib/index.js`。

## 导入依赖

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { PathExt, URLExt } from '@jupyterlab/coreutils';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { ServerConnection } from '@jupyterlab/services';
import { GitPuller, GithubPuller, GitlabPuller } from './gitpuller';
```

## 导出成员

| 成员 | 类型 | 签名 |
|------|------|------|
| `testNbGitPuller` | async function | `() => Promise<boolean>` |
| `gitPullerExtension` (default) | JupyterFrontEndPlugin | `JupyterFrontEndPlugin<void>` |

## testNbGitPuller 函数逻辑

1. 通过 `ServerConnection.makeSettings()` 获取 Jupyter 服务端连接配置
2. 构造请求URL：`URLExt.join(settings.baseUrl, 'git-pull', 'api')`
3. 发起 GET 请求到该URL
4. 请求失败（catch）或 `response.ok` 为 false 时返回 `false`
5. 请求成功且 ok 时返回 `true`

## 插件配置

```typescript
const gitPullerExtension: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlite/litegitpuller:plugin',
  autoStart: true,
  requires: [IDefaultFileBrowser],
  activate: async (app, defaultFileBrowser) => { ... }
};
```

## activate 函数执行流程

1. 调用 `testNbGitPuller()` 检测 nbgitpuller，若已安装则输出日志并 return
2. 输出激活日志
3. 从 `window.location.search` 解析 URLSearchParams
4. 读取 `repo` 参数，不存在则 return
5. 读取其他参数：`branch`（默认 `'main'`）、`provider`（默认 `'github'`）、`urlpath`、`uploadpath`（默认 `'/'`）
6. 计算 `basePath = PathExt.join(uploadPath, PathExt.basename(repo))`
7. 解析 repo URL：
   - **github**：验证 hostname 为 `github.com`，转换为 `api.github.com/repos{pathname}`，创建 `GithubPuller`
   - **gitlab**：构造 `/api/v4/projects/{encoded_path}`，创建 `GitlabPuller`
8. 调用 `puller.clone(repoUrl.href, branch, basePath)`
9. clone 完成后，若 `urlpath` 存在，执行 `app.commands.execute('filebrowser:open-path', {path: PathExt.join(repoPath, filePath)})`

## URL 参数完整列表

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `repo` | 是 | - | GitHub/GitLab 仓库URL |
| `branch` | 否 | `main` | 目标分支 |
| `provider` | 否 | `github` | Git平台提供者（`github` 或 `gitlab`） |
| `urlpath` | 否 | - | 克隆后自动打开的文件路径（相对于仓库根目录） |
| `uploadpath` | 否 | `/` | 仓库克隆到的目标目录 |
