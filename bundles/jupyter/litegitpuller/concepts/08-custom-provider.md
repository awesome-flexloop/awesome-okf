---
type: Concept
title: 自定义 Provider
description: 如何通过继承 GitPuller 抽象基类来添加新的 Git 平台支持（如 Gitea、Bitbucket、Gogs 等），包括必须实现的方法和 URL 转换逻辑。
tags: [custom-provider, extensibility, gitea, bitbucket, gogs, template-method, subclassing]
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

## 扩展机制概述

litegitpuller 采用模板方法模式设计，`GitPuller` 抽象基类定义了固定的克隆流程，将平台相关的 API 调用委托给两个抽象方法。要添加新的 Git 平台支持，只需：

1. 创建一个继承 `GitPuller` 的新类
2. 实现 `getFileList()` 方法（获取文件和目录列表）
3. 实现 `getFile()` 方法（获取单个文件内容）
4. 修改 `src/index.ts` 中的 activate 函数，添加 URL 转换和 provider 分支

## 必须实现的方法

### getFileList

```typescript
abstract getFileList(
  url: string,
  branch: string
): Promise<GitPuller.IFileList>;
```

**职责**：调用平台 API 获取指定分支的完整文件树，返回目录列表和文件列表。

**参数**：
- `url`：转换后的 API 基础 URL（由 activate 函数处理）
- `branch`：分支名称

**返回值**（`GitPuller.IFileList`）：
```typescript
interface IFileList {
  directories: string[];  // 目录路径数组，相对于仓库根目录
  files: string[];        // 文件路径数组，相对于仓库根目录
}
```

实现要点：
- 必须使用**递归**（recursive）方式获取文件树，否则只能获取顶层目录
- 返回的路径必须是相对于仓库根目录的路径（不含前导 `/`）
- 需要区分目录（tree）和文件（blob）

### getFile

```typescript
abstract getFile(
  url: string,
  path: string,
  branch: string
): Promise<GitPuller.IFile>;
```

**职责**：获取指定路径的文件内容，返回 Blob 和 MIME 类型。

**参数**：
- `url`：API 基础 URL
- `path`：文件在仓库中的路径（相对于根目录）
- `branch`：分支名称

**返回值**（`GitPuller.IFile`）：
```typescript
interface IFile {
  blob: Blob;    // 文件二进制内容
  type: string;  // MIME 类型（从 Content-Type 响应头获取）
}
```

实现要点：
- 文件路径可能包含特殊字符（空格、中文等），需要 URL 编码
- 返回的 Blob 将被 JupyterLab 上传到文件系统
- Content-Type 帮助 JupyterLab 正确识别文件类型

## 完整实现示例：Gitea Puller

以 [Gitea](https://gitea.io/)（一个自建 Git 服务）为例，展示如何添加新的 Provider。

### 第一步：创建 GiteaPuller 类

```typescript
import { GitPuller } from './gitpuller';

export class GiteaPuller extends GitPuller {
  /**
   * 获取文件和目录列表
   * Gitea API 兼容 GitHub API 格式
   */
  async getFileList(url: string, branch: string): Promise<GitPuller.IFileList> {
    // Gitea 的 API 路径与 GitHub 类似
    const fetchUrl = `${url}/git/trees/${branch}?recursive=true`;
    const response = await fetch(fetchUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    const data = await response.json();
    const fileList = data.tree as any[];

    const directories = fileList
      .filter((item: any) => item.type === 'tree')
      .map((item: any) => item.path as string);

    const files = fileList
      .filter((item: any) => item.type === 'blob')
      .map((item: any) => item.path as string);

    return { directories, files };
  }

  /**
   * 获取单个文件内容
   * Gitea 的 /contents 端点也兼容 GitHub 格式
   */
  async getFile(
    url: string,
    path: string,
    branch: string
  ): Promise<GitPuller.IFile> {
    // Gitea Contents API 返回 download_url
    const metaUrl = `${url}/contents/${encodeURIComponent(path)}?ref=${branch}`;
    const metaResp = await fetch(metaUrl);
    const meta = await metaResp.json();

    // 获取文件内容
    const fileResp = await fetch(meta.download_url);
    const blob = await fileResp.blob();
    const type = fileResp.headers.get('Content-Type') ?? '';

    return { blob, type };
  }
}
```

### 第二步：在 activate 函数中添加 Provider 分支

修改 `src/index.ts`，添加 URL 转换和 Provider 实例化逻辑：

```typescript
import { GiteaPuller } from './gitpuller'; // 添加导入

// 在 activate 函数中，现有的 provider 分支后添加：
else if (provider === 'gitea') {
  // Gitea 实例 URL 转换
  // 用户输入: https://gitea.example.com/user/repo
  // API URL:  https://gitea.example.com/api/v1/repos/user/repo
  repoUrl.pathname = `/api/v1/repos${repoUrl.pathname}`;
  puller = new GiteaPuller({
    defaultFileBrowser: defaultFileBrowser,
    contents: app.serviceManager.contents
  });
}
```

### 第三步：导出新类

在 `src/gitpuller.ts` 的导出中添加新类：

```typescript
export class GiteaPuller extends GitPuller {
  // ...实现
}
```

在 `src/index.ts` 的导入中添加：
```typescript
import { GitPuller, GithubPuller, GitlabPuller, GiteaPuller } from './gitpuller';
```

## URL 转换模式

不同平台的 URL 转换是 activate 函数中需要处理的关键逻辑。以下是常见平台的转换模式：

### GitHub 模式（api.github.com）

```
用户URL:  https://github.com/{owner}/{repo}
API URL:  https://api.github.com/repos/{owner}/{repo}
```
- hostname 从 `github.com` 改为 `api.github.com`
- pathname 前添加 `/repos`

### GitLab 模式（项目ID编码）

```
用户URL:  https://gitlab.com/{owner}/{repo}
API URL:  https://gitlab.com/api/v4/projects/{encoded(owner/repo)}
```
- pathname 替换为 `/api/v4/projects/{url_encode(owner/repo)}`
- 项目路径中的 `/` 编码为 `%2F`

### Gitea/Gogs 模式（API v1）

```
用户URL:  https://gitea.example.com/{owner}/{repo}
API URL:  https://gitea.example.com/api/v1/repos/{owner}/{repo}
```
- hostname 保持不变
- pathname 前添加 `/api/v1/repos`

### Bitbucket 模式（API 2.0）

```
用户URL:  https://bitbucket.org/{owner}/{repo}
API URL:  https://api.bitbucket.org/2.0/repositories/{owner}/{repo}
```
- hostname 改为 API 域名
- pathname 完全替换

## 实现注意事项

### 认证支持（扩展）

当前所有 Puller 都不支持认证。如需支持私有仓库，可以在构造函数中接收 token 参数：

```typescript
interface IOptions {
  defaultFileBrowser: IDefaultFileBrowser;
  contents: Contents.IManager;
  token?: string;  // 新增：访问令牌
}
```

然后在 fetch 请求中添加 Authorization header：
```typescript
const headers: Record<string, string> = {
  'Accept': 'application/json'
};
if (this._token) {
  headers['Authorization'] = `token ${this._token}`;
}
```

### 文件路径编码

不同平台对文件路径的编码要求不同：
- GitHub：路径直接拼接在 URL 中（`/contents/path/to/file`）
- GitLab：路径需要 `encodeURIComponent`（`/files/{encoded}/raw`）
- 通用建议：始终对路径部分进行编码，以防特殊字符导致问题

### 大文件支持

GitHub Contents API 对大于 1MB 的文件返回 blob SHA，需要额外调用 Blob API 获取内容。如果需要支持大文件，可以在 getFile 中添加判断：

```typescript
if (meta.size > 1000000) {
  // 使用 Git Blob API 获取大文件
  const blobUrl = `${url}/git/blobs/${meta.sha}`;
  // ... 处理 base64 编码的内容
}
```

### 错误处理增强

当前实现中，API 请求失败（网络错误、速率限制、权限不足等）会导致 fetch 抛出异常，clone 方法中的循环会中断。可以考虑：
- 添加重试逻辑
- 对 403/429（速率限制）输出更友好的错误信息
- 继续处理其他文件而非中断整个克隆流程

## 测试自定义 Provider

实现新的 Puller 后，可以通过以下步骤测试：

1. 构建扩展：`jlpm build`
2. 启动 JupyterLab/JupyterLite
3. 使用对应 provider 参数构造 URL：
   ```
   ?repo=https%3A%2F%2Fgitea.example.com%2Fuser%2Frepo&provider=gitea
   ```
4. 打开浏览器开发者工具，观察控制台日志和网络请求
5. 验证文件是否正确下载到文件浏览器
6. 检查错误情况（不存在的仓库、错误的分支、速率限制）

## 相关概念

- [GitPuller 抽象基类](03-gitpuller-base.md) — 基类的完整 API 和 clone 流程
- [平台 Puller 实现](04-platform-pullers.md) — 现有 GithubPuller/GitlabPuller 的参考实现
- [整体架构](02-architecture.md) — 模板方法模式的架构角色
- [扩展插件机制](05-extension-plugin.md) — activate 函数中 Provider 选择逻辑
