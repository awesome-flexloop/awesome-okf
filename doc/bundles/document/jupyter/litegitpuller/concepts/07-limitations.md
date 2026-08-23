---
type: Concept
title: 限制与注意事项
description: litegitpuller 的使用限制，包括 GitHub API 速率限制、大仓库限制、文件冲突行为、不支持的 Git 特性等。
tags: [limitations, rate-limit, github-api, file-conflicts, private-repos, lfs]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:57:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:57:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-gitpuller-ts
    resource: /references/gitpuller-ts-source.md
    title: src/gitpuller.ts Git拉取核心源码信源
  - id: source-index-ts
    resource: /references/index-ts-source.md
    title: src/index.ts 插件入口源码信源
---

## GitHub API 速率限制

litegitpuller 使用 GitHub 未认证 REST API 来获取文件内容，这是最显著的限制。

### 限制详情

- **未认证请求**：每小时每个 IP 地址最多 60 个请求
- **文件列表**：获取文件树仅需 1 次 API 请求（`/git/trees/{branch}?recursive=true`）
- **文件下载**：每个文件需要 2 次 API 请求（1 次获取 metadata + 1 次下载内容）

### 实际影响

假设仓库有 N 个文件：
- 总请求数 ≈ 1 + 2N
- 60 次/小时的限制意味着每小时最多可拉取约 **29-30 个文件**（1次列表 + 29×2次文件 = 59次请求）

这意味着 litegitpuller 不适合拉取大型仓库——只适合小型教程仓库、示例 notebook 集合等文件数量较少的场景。

### GitLab 速率限制

GitLab 的速率限制取决于具体实例配置。GitLab.com 对未认证请求也有限制，但具体阈值与 GitHub 不同。自建 GitLab 实例的限制由管理员配置。

### 文件下载优化差异

值得注意的是，GitLab 的文件获取只需 1 次请求（直接下载原始内容），而 GitHub 需要 2 次（先获取 download_url 再下载）。因此在相同速率限制下，GitLab 每小时可以拉取约 **59 个文件**（1次列表 + 59次文件 = 60次请求），是 GitHub 的约 2 倍。

## 文件大小与数量建议

基于 API 速率限制，建议：

| 仓库类型 | 文件数建议 | 说明 |
|---------|-----------|------|
| 小型教程 | ≤20 个文件 | 安全范围内，一次拉取不会触发限制 |
| 中等示例 | 20-30 个文件 | 接近 GitHub 限制，可能部分文件失败 |
| 大型项目 | >30 个文件 | **不推荐**，会触发速率限制 |

### 大文件限制

- litegitpuller 通过浏览器 `fetch().blob()` 获取文件内容，大文件可能导致浏览器内存占用过高
- GitHub API 对通过 Contents API 获取的文件有大小限制（1MB 以下推荐使用此 API；大于 1MB 的文件需要使用 Blob API，litegitpuller 当前未实现）

## 文件冲突行为

litegitpuller 的文件冲突处理策略是**跳过而非覆盖**：

```typescript
if (await this.fileExists(filePath)) {
  this.addUploadError('File already exist', filePath);
  continue;
}
```

这意味着：
- 如果目标路径上已存在同名文件，该文件**不会被更新或覆盖**
- 新文件仍然正常拉取
- 被跳过的文件会在浏览器控制台输出警告
- **没有"强制覆盖"或"智能合并"选项**

### 实际影响

- 如果用户多次访问同一 URL 拉取同一仓库，第二次访问时所有文件都已存在，只会输出警告，不会更新文件
- 如果远端仓库更新了内容，本地已有的旧文件不会被更新
- 要重新拉取更新的内容，用户需要手动删除已有目录后重新访问 URL

## 不支持的 Git 特性

litegitpuller 通过 REST API 获取文件快照，不执行真正的 `git clone`，因此以下 Git 特性不被支持：

| 特性 | 支持情况 | 说明 |
|------|---------|------|
| Git 历史记录 | ❌ | 不包含 .git 目录，无 commit 历史 |
| 分支切换 | ❌ | 只能在 URL 中指定分支，加载后无法切换 |
| git pull 更新 | ❌ | 不会自动更新已拉取的文件 |
| git push | ❌ | 完全不支持写回远程仓库 |
| Git LFS | ❌ | 不处理 Git LFS 指针文件 |
| Submodules | ❌ | 不会递归拉取子模块 |
| 私有仓库 | ❌ | 未实现认证，仅支持公开仓库 |
| .gitignore | ❌ | 所有文件都拉取，不尊重 .gitignore 规则 |
| 符号链接 | ⚠️ | 取决于 API 返回行为，可能不正确处理 |
| 文件权限 | ❌ | JupyterLite 文件系统不支持 Unix 权限 |

## 平台限制

### GitHub Enterprise Server 不支持

当 `provider === 'github'` 时，代码会验证 hostname 必须是 `github.com`：

```typescript
if (repoUrl.hostname !== 'github.com') {
  console.warn('litegitpuller: the URL does not match with a GITHUB repository');
  return;
}
```

GitHub Enterprise Server（自建 GitHub 实例）虽然 API 兼容，但由于 hostname 检查会被拒绝。

### GitLab 自建实例支持

GitLab provider 不做 hostname 检查，因此支持自建 GitLab 实例。但需要注意：
- URL 必须是可从用户浏览器访问的地址
- API 路径为 `/api/v4/projects/...`，要求 GitLab 实例支持 v4 API
- 项目路径会自动 URL 编码

## 浏览器兼容性

litegitpuller 使用以下浏览器 API，需要现代浏览器支持：

- `fetch()` API
- `URLSearchParams`
- `URL()` 构造函数
- `Blob` API
- `File` API

这些 API 在所有现代浏览器（Chrome、Firefox、Safari、Edge）中均已支持，但不兼容 IE 等老旧浏览器。

## 网络依赖

litegitpuller 的工作依赖于浏览器能够访问：
1. **JupyterLab/JupyterLite 服务**（加载应用本身）
2. **GitHub/GitLab API**（获取文件列表和内容）

如果用户处于网络受限环境（如企业防火墙阻断对 `api.github.com` 的访问），拉取会失败。所有 API 请求都从浏览器端发出（非服务端代理），因此受用户本地网络环境影响。

## 无 UI 反馈

litegitpuller 不提供任何 UI 进度指示——没有进度条、没有加载动画、没有完成提示。用户只能通过：
1. 浏览器开发者工具控制台查看日志和错误
2. 文件浏览器中出现新文件
3. 如果设置了 `urlpath`，目标文件自动打开

对于不熟悉开发者工具的用户，这可能造成困惑——页面看起来没有变化，但后台正在拉取文件。

## 错误处理限制

错误信息仅通过 `console.warn()` 输出到浏览器控制台，不会：
- 弹出对话框通知用户
- 在界面上显示错误信息
- 重试失败的请求
- 区分网络错误和 API 错误

常见的静默失败场景：
- 速率限制导致 API 返回 403/429 → 文件获取失败
- 网络中断 → fetch 抛出异常
- 仓库不存在 → API 返回 404
- 分支不存在 → API 返回 404

这些情况下，控制台会有错误信息，但用户界面不会有任何提示。

## 相关概念

- [litegitpuller 简介](00-introduction.md) — 了解基本工作方式
- [平台 Puller 实现](04-platform-pullers.md) — GitHub 和 GitLab API 调用细节
- [URL参数完整参考](06-url-parameters.md) — 如何正确构造 URL
- [自定义Provider](08-custom-provider.md) — 扩展支持更多平台
