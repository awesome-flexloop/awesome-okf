---
type: Example
title: GitLab 仓库拉取示例
description: 通过 URL 参数从 GitLab（包括 gitlab.com 和自建实例）拉取公开仓库的完整示例。
tags: [gitlab, provider, example, url-construction, self-hosted]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:58:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:58:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-index-ts
    resource: /references/index-ts-source.md
    title: src/index.ts 插件入口源码信源
  - id: source-gitpuller-ts
    resource: /references/gitpuller-ts-source.md
    title: src/gitpuller.ts Git拉取核心源码信源
---

## 示例目标

从 GitLab（gitlab.com 或自建实例）拉取公开仓库到 JupyterLab/JupyterLite。使用 GitLab 时必须显式指定 `provider=gitlab` 参数。

## 前提条件

- JupyterLab >= 4.0.0 已安装并运行
- litegitpuller 扩展已安装
- 目标 GitLab 仓库为公开仓库
- 浏览器可以访问目标 GitLab 实例的 API

## GitLab.com 仓库示例

拉取 gitlab.com 上的 `brichet1/testing-repo` 仓库：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgitlab.com%2Fbrichet1%2Ftesting-repo&provider=gitlab&branch=main
```

解码后的参数：
- `repo` = `https://gitlab.com/brichet1/testing-repo`
- `provider` = `gitlab`
- `branch` = `main`

### URL 转换过程

当 `provider=gitlab` 时，源码中的 URL 转换逻辑为：

```
输入: https://gitlab.com/brichet1/testing-repo
转换: pathname → /api/v4/projects/brichet1%2Ftesting-repo
输出: https://gitlab.com/api/v4/projects/brichet1%2Ftesting-repo
```

注意项目路径 `brichet1/testing-repo` 中的 `/` 被编码为 `%2F`。

## 完整参数 URL

拉取 GitLab 仓库并自动打开 notebook：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgitlab.com%2Fbrichet1%2Ftesting-repo&provider=gitlab&branch=main&urlpath=notebooks%2Fsimple.ipynb
```

## 自建 GitLab 实例示例

litegitpuller 支持自建 GitLab 实例（不做 hostname 检查）。假设你的 GitLab 部署在 `https://gitlab.example.com`：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgitlab.example.com%2Fgroup%2Fproject&provider=gitlab
```

### URL 转换过程

```
输入: https://gitlab.example.com/group/project
转换: pathname → /api/v4/projects/group%2Fproject
输出: https://gitlab.example.com/api/v4/projects/group%2Fproject
```

要求自建实例支持 GitLab API v4（GitLab 9.0+）。

## 使用 JavaScript 生成 GitLab URL

```javascript
function createGitLabUrl(jupyterLabUrl, repoUrl, branch = 'main', filePath = null) {
  const params = new URLSearchParams({
    repo: repoUrl,
    provider: 'gitlab',
    branch: branch
  });
  if (filePath) {
    params.set('urlpath', filePath);
  }
  return `${jupyterLabUrl}?${params.toString()}`;
}

// gitlab.com 示例
const url1 = createGitLabUrl(
  'https://your-jupyterlite.example.com/lab',
  'https://gitlab.com/brichet1/testing-repo',
  'main',
  'notebooks/simple.ipynb'
);

// 自建实例示例
const url2 = createGitLabUrl(
  'http://localhost:8888/lab',
  'https://gitlab.example.com/group/project',
  'main'
);
```

## 使用 Python 生成 GitLab URL

```python
from urllib.parse import urlencode

def create_gitlab_url(jupyter_lab_url, repo_url, branch='main', urlpath=None, uploadpath=None):
    params = {
        'repo': repo_url,
        'provider': 'gitlab',
        'branch': branch
    }
    if urlpath:
        params['urlpath'] = urlpath
    if uploadpath:
        params['uploadpath'] = uploadpath
    return f"{jupyter_lab_url}?{urlencode(params)}"

# 使用示例
url = create_gitlab_url(
    'https://your-jupyterlite.example.com/lab',
    'https://gitlab.com/brichet1/testing-repo',
    'main',
    urlpath='notebooks/simple.ipynb'
)
print(url)
```

## 嵌套群组项目

GitLab 支持嵌套群组（如 `group/subgroup/project`），litegitpuller 会自动对路径进行编码：

```
仓库URL: https://gitlab.com/group/subgroup/project
API URL:  https://gitlab.com/api/v4/projects/group%2Fsubgroup%2Fproject
```

URL 示例：
```
http://localhost:8888/lab?repo=https%3A%2F%2Fgitlab.com%2Fgroup%2Fsubgroup%2Fproject&provider=gitlab
```

## GitLab vs GitHub 对比

在使用时需要注意的差异：

| 对比项 | GitHub | GitLab |
|--------|--------|--------|
| provider 参数 | 默认值，可不传 | **必须显式设置** `provider=gitlab` |
| hostname 检查 | 必须是 `github.com` | 无限制，支持自建实例 |
| 每个文件请求数 | 2次（元数据+下载） | 1次（直接下载） |
| 速率限制 | 60次/小时 | 取决于实例配置 |
| 项目路径 | 直接拼接 | URL编码（`/` → `%2F`） |

## 验证拉取结果

1. 打开浏览器开发者工具（F12），查看 Network 标签页
2. 应能看到对 `/api/v4/projects/...` 端点的请求
3. 文件浏览器中应出现仓库目录
4. 如果拉取失败，检查 Console 标签页的错误信息

## 常见问题

### Q: 提示 "the URL does not match with a GITHUB repository"？

这是因为没有设置 `provider=gitlab` 参数。GitHub provider 会检查 hostname 是否为 `github.com`，GitLab 仓库的 hostname 不是 `github.com`，所以被拒绝。添加 `&provider=gitlab` 即可。

### Q: 自建 GitLab 返回 401/403 错误？

检查项目是否为公开（visibility level 为 Public）。私有项目需要认证，litegitpuller 当前不支持。

### Q: 自建 GitLab API 路径不是 /api/v4？

某些 GitLab 部署可能使用不同的 API 前缀（如反向代理后）。这种情况下需要修改源码中 GitlabPuller 的 URL 构造逻辑，或等待自定义 Provider 功能（参见[自定义Provider](../concepts/08-custom-provider.md)）。

## 相关示例

- [GitHub 仓库拉取基础示例](01-basic-github.md) — GitHub 使用方法
- [自动打开 Notebook](03-open-notebook.md) — 拉取后自动打开文件
- [自定义上传路径](04-custom-uploadpath.md) — 指定目标目录

## 相关概念

- [URL参数完整参考](../concepts/06-url-parameters.md) — provider 参数详解
- [平台 Puller 实现](../concepts/04-platform-pullers.md) — GitlabPuller 的 API 实现
- [自定义Provider](../concepts/08-custom-provider.md) — 如何扩展支持更多平台
