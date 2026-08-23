---
okf_version: "0.2"
type: reference
title: "GitHub API 请求层源码（src/github.ts）"
description: "浏览器端与代理端 GitHub API v3 请求函数，以及 GitHub API 返回数据的 TypeScript 类型定义"
tags: [api, github-api-v3, types, fetch, proxy, base64, contents, blob, repo]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: github-ts
    resource: "../../../../../external/libs/jupyter/jupyterlab-github/src/github.ts"
    title: "src/github.ts"
---

# GitHub API 请求层源码（src/github.ts）

本信源登记 `src/github.ts`（约259行），提供两种 GitHub API 请求方式和完整的类型定义。

## API 请求函数

### browserApiRequest\<T\>(url: string): Promise\<T\>

直接在浏览器端通过 `window.fetch()` 请求 GitHub API：
- 非200状态码时解析 JSON 响应体中的 `message` 字段，抛出 `ServerConnection.ResponseError`
- 成功时返回解析后的 JSON 数据
- **注意**：无认证时受 GitHub 速率限制（每小时60次请求）

### proxiedApiRequest\<T\>(url: string, settings: ServerConnection.ISettings): Promise\<T\>

通过 Jupyter Server 代理请求 GitHub API：
- 使用 `ServerConnection.makeRequest(url, {}, settings)` 发送请求
- 错误处理逻辑与 `browserApiRequest` 相同
- 服务端可附加认证 token，获得更高的速率限制（每小时5000次）

## 类型定义

### GitHubContents（基础接口）

GitHub API v3 Contents API 返回的通用文件/目录条目类型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | `'file' \| 'dir' \| 'submodule' \| 'symlink'` | 条目类型 |
| `size` | `number` | 文件大小（字节） |
| `name` | `string` | 文件名 |
| `path` | `string` | 仓库内路径 |
| `sha` | `string` | Git SHA 标识符 |
| `url` | `string` | API URL |
| `git_url` | `string` | Git 访问 URL |
| `html_url` | `string` | GitHub 网页 URL |
| `download_url` | `string` | 原始下载 URL |
| `_links` | `{ git: string; self: string; html: string }` | 链接集合 |

### GitHubFileContents（extends GitHubContents）

文件内容类型：
- `type` 固定为 `'file'`
- `encoding` 固定为 `'base64'`
- `content` 可选，为 base64 编码的文件内容

### GitHubDirectoryContents（extends GitHubContents）

目录类型：
- `type` 固定为 `'dir'`

### GitHubBlob

Git Data API Blob 类型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `content` | `string` | base64 编码的文件内容 |
| `encoding` | `'base64'` | 编码方式 |
| `url` | `string` | Blob API URL |
| `sha` | `string` | Blob SHA |
| `size` | `number` | Blob 大小（字节） |

### GitHubSymlinkContents / GitHubSubmoduleContents

分别对应 `type: 'symlink'` 和 `type: 'submodule'` 的类型别名。

### GitHubDirectoryListing

类型别名：`GitHubContents[]`——目录列表。

### GitHubRepo（不完整类型）

仓库信息类型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `number` | 仓库 ID |
| `owner` | `any` | 仓库所有者 |
| `name` | `string` | 仓库名 |
| `full_name` | `string` | 完整名称（owner/name） |
| `description` | `string` | 仓库描述 |
| `private` | `boolean` | 是否私有 |
| `fork` | `boolean` | 是否 fork |
| `url` | `string` | API URL |
| `html_url` | `string` | 网页 URL |

> 注释标注为 "This is incomplete"，仅包含扩展使用的字段。
