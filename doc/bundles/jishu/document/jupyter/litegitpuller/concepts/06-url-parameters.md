---
type: Concept
title: URL 参数完整参考
description: litegitpuller 所有 URL 查询参数的完整说明、用法示例和编码要求，包括 repo、branch、provider、urlpath、uploadpath。
tags: [url-parameters, query-string, link-generator, url-encoding, nbgitpuller-link]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:57:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:57:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-index-ts
    resource: /references/index-ts-source.md
    title: src/index.ts 插件入口源码信源
---

## URL 参数机制

litegitpuller 采用零 UI 设计——没有按钮、菜单或对话框，所有配置都通过 URL 查询参数（query string parameters）传递。当 JupyterLab 页面加载时，扩展读取 URL 中的参数，如果存在 `repo` 参数就自动执行仓库拉取。

参数通过标准的 URL 查询字符串格式传递：

```
https://your-jupyterlite.example.com/lab?repo=...&branch=...&urlpath=...
```

## 参数详解

### repo（必填）

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | **是** |
| 默认值 | 无（缺失时扩展不执行任何操作） |

指定要拉取的 Git 仓库的完整 URL。

- **GitHub 格式**：`https://github.com/{owner}/{repo}`
- **GitLab 格式**：`https://gitlab.com/{owner}/{repo}` 或自建 GitLab URL
- **注意**：URL 值必须进行百分号编码（percent-encoding）

GitHub 示例（未编码）：
```
repo=https://github.com/brichet/testing-repo
```

编码后：
```
repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo
```

源码中的处理逻辑：
```typescript
const repo = urlParams.get('repo');
if (!repo) {
  return;  // 没有 repo 参数，直接退出
}
const repoUrl = new URL(repo);
```

`repo` 的值会被传入 `new URL(repo)` 进行解析，因此必须是合法的完整 URL。

### branch（可选）

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 否 |
| 默认值 | `main` |

指定要拉取的分支名称。如果仓库使用 `master` 作为默认分支，或需要拉取特定分支/标签，需要显式设置此参数。

源码处理：
```typescript
const branch = urlParams.get('branch') || 'main';
```

示例：
```
&branch=master
&branch=develop
&branch=v1.0.0
```

### provider（可选）

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 否 |
| 默认值 | `github` |
| 有效值 | `github`, `gitlab` |

指定 Git 平台提供者，决定使用哪个 API 来获取文件。

源码处理：
```typescript
const provider = urlParams.get('provider') || 'github';
```

不同 provider 的 URL 转换逻辑：
- **github**：将 `github.com` 转换为 `api.github.com/repos/...`，并验证 hostname 必须是 `github.com`
- **gitlab**：转换为 `/api/v4/projects/{encoded_path}` 格式，支持任意 GitLab 实例（包括自建）

> **注意**：GitHub Enterprise Server 目前不支持。provider 为 `github` 时会验证 hostname 必须是 `github.com`，否则输出警告并中止。

### urlpath（可选）

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 否 |
| 默认值 | 无（不自动打开文件） |

指定拉取完成后自动打开的文件路径，相对于仓库根目录。通常用于指定一个 Jupyter Notebook（`.ipynb`）文件，使用户打开链接后直接看到教程内容。

源码处理：
```typescript
const filePath = urlParams.get('urlpath');
// ...
puller.clone(repoUrl.href, branch, basePath).then(repoPath => {
  if (filePath) {
    app.commands.execute('filebrowser:open-path', {
      path: PathExt.join(repoPath, filePath)
    });
  }
});
```

最终打开的路径是 `{uploadpath}/{repo-basename}/{urlpath}`。

示例：
```
&urlpath=notebooks/tutorial.ipynb
&urlpath=README.md
&urlpath=lectures/week1/intro.ipynb
```

### uploadpath（可选）

| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必填 | 否 |
| 默认值 | `/` |

指定仓库内容放置在 JupyterLab 文件浏览器中的哪个目录下。默认为根目录 `/`，仓库文件夹会创建在文件浏览器的根目录。

源码处理：
```typescript
const uploadPath = urlParams.get('uploadpath') || '/';
const basePath = PathExt.join(uploadPath, PathExt.basename(repo));
```

`basePath` 的计算规则：`uploadpath + '/' + repo 仓库名`。

示例：

| uploadpath | repo URL | basePath |
|-----------|----------|----------|
| `/`（默认） | `https://github.com/user/my-repo` | `/my-repo` |
| `/tutorials` | `https://github.com/user/my-repo` | `/tutorials/my-repo` |
| `/workshops/2024` | `https://github.com/user/materials` | `/workshops/2024/materials` |

## URL 编码

URL 参数值中的特殊字符必须进行百分号编码。常见编码：

| 字符 | 编码 | 出现场景 |
|------|------|---------|
| `:` | `%3A` | URL 中的协议分隔符（`https:`） |
| `/` | `%2F` | URL 中的路径分隔符 |
| ` `（空格） | `%20` 或 `+` | 路径中有空格 |
| `?` | `%3F` | 不会出现在 repo 值中 |
| `#` | `%23` | 不会出现在 repo 值中 |
| `&` | `%26` | 不会出现在 repo 值中 |

### JavaScript 编码

```javascript
const params = new URLSearchParams({
  repo: 'https://github.com/user/repo',
  branch: 'main',
  urlpath: 'notebooks/tutorial.ipynb'
});
const url = `https://example.com/lab?${params.toString()}`;
// 结果: https://example.com/lab?repo=https%3A%2F%2Fgithub.com%2Fuser%2Frepo&branch=main&urlpath=notebooks%2Ftutorial.ipynb
```

### Python 编码

```python
from urllib.parse import urlencode

params = {
    'repo': 'https://github.com/user/repo',
    'branch': 'main',
    'urlpath': 'notebooks/tutorial.ipynb'
}
query = urlencode(params)
url = f"https://example.com/lab?{query}"
```

## 与 nbgitpuller 链接生成器兼容

litegitpuller 的 URL 参数格式设计为与 [nbgitpuller link generator](https://nbgitpuller.readthedocs.io/en/latest/link.html) 兼容。可以使用 nbgitpuller 的在线链接生成器来构造 URL，只需注意：

1. 将环境 URL 改为你的 JupyterLite/JupyterLab 地址
2. litegitpuller 支持 nbgitpuller 的 `repo`、`branch`、`urlpath` 参数
3. litegitpuller 额外支持 `provider` 参数（指定 gitlab）
4. litegitpuller 额外支持 `uploadpath` 参数

nbgitpuller 的其他参数（如 `application`、`custom_image` 等 JupyterHub 特有参数）会被 litegitpuller 忽略，不会产生错误。

## 常见 URL 模式

### 最简模式

仅指定 repo，拉取 main 分支到根目录：
```
?repo=https%3A%2F%2Fgithub.com%2Fuser%2Frepo
```

### 教学模式

拉取仓库并自动打开 notebook：
```
?repo=https%3A%2F%2Fgithub.com%2Fuser%2Ftutorials&urlpath=notebooks%2Flecture1.ipynb
```

### 指定分支

拉取特定分支：
```
?repo=https%3A%2F%2Fgithub.com%2Fuser%2Frepo&branch=develop
```

### GitLab 仓库

使用 GitLab provider：
```
?repo=https%3A%2F%2Fgitlab.com%2Fuser%2Frepo&provider=gitlab
```

### 自定义目录

拉取到指定目录：
```
?repo=https%3A%2F%2Fgithub.com%2Fuser%2Frepo&uploadpath=%2Fworkshops%2F2024
```

### 完整示例

所有参数都用上：
```
?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo&branch=main&urlpath=notebooks%2Fsimple.ipynb&provider=github&uploadpath=%2F
```

## 相关概念

- [安装与快速开始](01-getting-started.md) — 第一个 URL 示例
- [扩展插件机制](05-extension-plugin.md) — activate 函数中参数解析的完整流程
- [GitHub仓库拉取示例](../examples/01-basic-github.md) — 构造 GitHub 拉取 URL 的完整示例
- [GitLab仓库拉取示例](../examples/02-gitlab-repo.md) — 构造 GitLab 拉取 URL 的完整示例
- [限制与注意事项](07-limitations.md) — API 速率限制等使用限制
