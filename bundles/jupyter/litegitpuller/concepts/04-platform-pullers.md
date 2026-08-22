---
type: Concept
title: 平台 Puller 实现
description: GithubPuller 和 GitlabPuller 两个具体类的 API 调用差异、URL 转换逻辑和文件获取方式详解。
tags: [github-puller, gitlab-puller, platform-implementation, rest-api, github-api, gitlab-api]
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

## 平台实现概述

`GitPuller` 抽象基类定义了两个抽象方法——`getFileList()` 和 `getFile()`，它们分别负责获取文件树和获取单个文件内容。`GithubPuller` 和 `GitlabPuller` 通过调用不同平台的 REST API 实现这两个方法。

两个具体类没有覆盖 `clone()` 方法，完全继承基类的模板方法实现。这意味着克隆流程、目录创建、文件上传、错误处理等逻辑在所有平台上完全一致。

## GithubPuller

`GithubPuller` 类继承自 `GitPuller`，使用 GitHub REST API v3 获取仓库内容。

### URL 转换

在插件激活函数中，用户提供的 GitHub 仓库 URL 会被转换为 API 基础 URL：

```
用户输入:  https://github.com/{owner}/{repo}
转换为:    https://api.github.com/repos/{owner}/{repo}
```

转换逻辑（在 `src/index.ts` 的 activate 函数中）：
1. 验证 hostname 为 `github.com`，否则输出警告并中止
2. 将 hostname 改为 `api.github.com`
3. 在 pathname 前添加 `/repos` 前缀

```typescript
if (repoUrl.hostname !== 'github.com') {
  console.warn('litegitpuller: the URL does not match with a GITHUB repository');
  return;
}
repoUrl.hostname = 'api.github.com';
repoUrl.pathname = `/repos${repoUrl.pathname}`;
```

### getFileList 实现

```typescript
async getFileList(url: string, branch: string): Promise<GitPuller.IFileList> {
  const fetchUrl = `${url}/git/trees/${branch}?recursive=true`;
  const fileList = await fetch(fetchUrl, {
    method: 'GET',
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'request'
    }
  })
    .then(resp => resp.json())
    .then(data => data.tree as any[]);

  const directories = Object.values(fileList)
    .filter(fileDesc => fileDesc.type === 'tree')
    .map(directory => directory.path as string);
  const files = Object.values(fileList)
    .filter(fileDesc => fileDesc.type === 'blob')
    .map(file => file.path);

  return { directories, files };
}
```

API 端点：`GET https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=true`

请求头：
- `Accept: application/vnd.github+json` — GitHub 推荐的媒体类型
- `X-GitHub-Api-Version: 2022-11-28` — API 版本标识
- `User-Agent: request` — GitHub API 要求必须有 User-Agent

响应处理：响应 JSON 的 `tree` 数组中，`type: 'tree'` 表示目录，`type: 'blob'` 表示文件。

### getFile 实现

```typescript
async getFile(url: string, path: string, branch: string): Promise<GitPuller.IFile> {
  // 第一步：获取文件元数据
  const fetchUrl = `${url}/contents/${path}?ref=${branch}`;
  const downloadUrl = await fetch(fetchUrl, {
    method: 'GET',
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'request'
    }
  })
    .then(resp => resp.json())
    .then(data => data.download_url);

  // 第二步：下载文件内容
  const resp = await fetch(downloadUrl);
  const blob = await resp.blob();
  const type = resp.headers.get('Content-Type') ?? '';

  return { blob, type };
}
```

GitHub 的文件获取需要**两次请求**：
1. 先请求 Contents API 获取文件的元数据（包括 `download_url`）
2. 再请求 `download_url` 获取实际文件内容（blob）

API 端点：
- 元数据：`GET https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}`
- 下载：`{data.download_url}`（GitHub 返回的预签名下载 URL）

## GitlabPuller

`GitlabPuller` 类继承自 `GitPuller`，使用 GitLab REST API v4 获取仓库内容。

### URL 转换

GitLab 的 URL 转换与 GitHub 不同。GitLab API 使用项目 ID（URL 编码的路径）而非简单的路径拼接：

```
用户输入:  https://gitlab.com/{owner}/{repo}
转换为:    https://gitlab.com/api/v4/projects/{encodeURIComponent(owner/repo)}
```

转换逻辑：
```typescript
repoUrl.pathname = `/api/v4/projects/${encodeURIComponent(repoUrl.pathname.slice(1))}`;
```

注意 `repoUrl.pathname.slice(1)` 去掉开头的 `/`，然后对 `owner/repo` 进行 URL 编码（因为 `/` 在项目路径中需要编码为 `%2F`）。

### getFileList 实现

```typescript
async getFileList(url: string, branch: string): Promise<GitPuller.IFileList> {
  const fetchUrl = `${url}/repository/tree?ref=${branch}&recursive=true`;
  const fileList = await fetch(fetchUrl, {
    method: 'GET'
  })
    .then(resp => resp.json())
    .then(data => data as any[]);

  const directories = Object.values(fileList)
    .filter(fileDesc => fileDesc.type === 'tree')
    .map(directory => directory.path as string);
  const files = Object.values(fileList)
    .filter(fileDesc => fileDesc.type === 'blob')
    .map(file => file.path);

  return { directories, files };
}
```

API 端点：`GET {api_base}/repository/tree?ref={branch}&recursive=true`

与 GitHub 版本的主要区别：
- 不需要特殊请求头（无 Accept、X-GitHub-Api-Version 等）
- 响应直接是数组（GitHub 是 `{tree: [...]}` 对象）
- 使用 `ref` 参数指定分支（GitHub 使用 URL 路径中的 `{branch}`）
- 同样通过 `type === 'tree'` / `type === 'blob'` 区分目录和文件

### getFile 实现

```typescript
async getFile(url: string, path: string, branch: string): Promise<GitPuller.IFile> {
  const fetchUrl = `${url}/repository/files/${encodeURIComponent(path)}/raw?ref=${branch}`;
  const resp = await fetch(fetchUrl);
  const blob = await resp.blob();
  const type = resp.headers.get('Content-Type') ?? '';
  return { blob, type };
}
```

API 端点：`GET {api_base}/repository/files/{encoded_path}/raw?ref={branch}`

与 GitHub 版本的关键区别：
- **一次请求直接获取文件内容**（GitHub 需要两次）
- 文件路径在 URL 中需要 `encodeURIComponent` 编码（子目录路径中的 `/` 编码为 `%2F`）
- 端点末尾的 `/raw` 表示直接返回原始文件内容
- 不需要额外的 headers
- 同样从 `Content-Type` 响应头获取 MIME 类型

## GitHub vs GitLab API 对比

| 对比项 | GithubPuller | GitlabPuller |
|--------|-------------|-------------|
| API 版本 | REST API v3 | REST API v4 |
| 文件树端点 | `/git/trees/{branch}?recursive=true` | `/repository/tree?ref={branch}&recursive=true` |
| 文件树响应格式 | `{tree: [{type, path, ...}]}` | `[{type, path, ...}]`（直接数组） |
| 文件内容端点 | `/contents/{path}?ref={branch}` → 再请求 download_url | `/repository/files/{path}/raw?ref={branch}` |
| 请求次数/文件 | 2次（元数据+下载） | 1次（直接下载） |
| 特殊请求头 | 需要（Accept + API版本 + UA） | 不需要 |
| 路径编码 | 不需要（路径在URL中直接拼接） | 需要（encodeURIComponent） |
| 分支指定方式 | URL路径中 `/{branch}` | 查询参数 `?ref={branch}` |
| 速率限制 | 未认证 60次/小时 | 取决于实例配置 |

## 共享逻辑

两个 Puller 类共享基类 `GitPuller` 的以下逻辑：
- `clone()` 模板方法流程
- `createTree()` 目录创建
- `createFile()` 文件上传（两阶段策略）
- `fileExists()` 文件存在检查
- `addUploadError()` 错误收集
- `_errors` Map 错误存储

这意味着无论使用哪个平台，文件冲突处理、目录创建顺序、上传方式、错误报告等行为完全一致。

## 相关概念

- [GitPuller 抽象基类](03-gitpuller-base.md) — 基类的 clone 流程和通用方法
- [整体架构](02-architecture.md) — 模板方法模式在架构中的角色
- [扩展插件机制](05-extension-plugin.md) — activate 函数中如何选择和实例化 Puller
- [自定义Provider](08-custom-provider.md) — 如何添加新的 Git 平台支持
