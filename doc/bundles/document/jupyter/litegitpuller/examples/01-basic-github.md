---
type: Example
title: GitHub 仓库拉取基础示例
description: 通过 URL 参数从 GitHub 拉取公开仓库到 JupyterLab/JupyterLite 文件系统的完整示例，包含 URL 构造方法和 JavaScript/Python 链接生成代码。
tags: [github, basic-usage, url-construction, example, link-generator]
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

通过 URL 参数从 GitHub 拉取一个公开仓库到 JupyterLab/JupyterLite 文件系统中。这是 litegitpuller 最基础的使用方式。

## 前提条件

- JupyterLab >= 4.0.0 已安装并运行
- litegitpuller 扩展已安装（`pip install litegitpuller`）
- 目标 GitHub 仓库为公开仓库
- 浏览器可以访问 `api.github.com`

## 最简 URL 示例

假设 JupyterLab 运行在 `http://localhost:8888/lab`，要拉取 GitHub 上的 `brichet/testing-repo` 仓库：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo
```

解码后的参数：
- `repo` = `https://github.com/brichet/testing-repo`

### 执行结果

访问上述 URL 后：
1. JupyterLab 正常启动
2. litegitpuller 扩展自动激活
3. 在文件浏览器根目录创建 `testing-repo/` 文件夹
4. 拉取 `main` 分支的所有文件到该文件夹
5. 控制台输出拉取进度和任何错误

## 完整 URL（含分支指定）

如果仓库使用 `main` 以外的分支（如 `master` 或 `develop`）：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo&branch=master
```

## 使用 JavaScript 生成 URL

在网页中创建 litegitpuller 链接：

```javascript
function createLiteGitPullerUrl(jupyterLabUrl, repoUrl, branch = 'main') {
  const params = new URLSearchParams({
    repo: repoUrl,
    branch: branch
  });
  return `${jupyterLabUrl}?${params.toString()}`;
}

// 使用示例
const url = createLiteGitPullerUrl(
  'https://your-jupyterlite.example.com/lab',
  'https://github.com/brichet/testing-repo',
  'main'
);
console.log(url);
// 输出: https://your-jupyterlite.example.com/lab?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo&branch=main
```

## 使用 Python 生成 URL

在 Python 脚本或 Notebook 中生成链接：

```python
from urllib.parse import urlencode

def create_litegitpuller_url(jupyter_lab_url, repo_url, branch='main'):
    params = {
        'repo': repo_url,
        'branch': branch
    }
    return f"{jupyter_lab_url}?{urlencode(params)}"

# 使用示例
url = create_litegitpuller_url(
    'https://your-jupyterlite.example.com/lab',
    'https://github.com/brichet/testing-repo',
    'main'
)
print(url)
```

## 在 JupyterLite 部署中使用

如果使用 JupyterLite 静态部署，URL 格式类似：

```
https://your-jupyterlite.github.io/lab/index.html?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo
```

## 在 Binder 中使用

litegitpuller 也可以在 Binder 环境中使用（虽然 Binder 本身支持 nbgitpuller）：

```
https://mybinder.org/v2/gh/jupyterlite/litegitpuller/main?urlpath=lab
```

然后在打开的 JupyterLab 中附加 repo 参数。

## 验证拉取结果

拉取完成后，可以通过以下方式验证：

1. **文件浏览器**：检查根目录下是否出现了以仓库名命名的文件夹
2. **开发者工具控制台**：查看是否有错误警告（已存在的文件会显示 "File already exist" 警告）
3. **终端**：在 JupyterLab 终端中运行 `ls` 查看文件列表

## 常见问题

### Q: 为什么没有看到文件？

检查以下几点：
- URL 中的 `repo` 参数是否正确编码（`://` 应编码为 `%3A%2F%2F`）
- 仓库是否为公开仓库（私有仓库不支持）
- 浏览器控制台是否有错误信息
- 是否已触发 GitHub API 速率限制（每小时60次未认证请求）

### Q: 第二次访问同一 URL 没有更新文件？

litegitpuller 不会覆盖已存在的文件。如需重新拉取，请先删除目标文件夹后刷新页面。

## 相关示例

- [GitLab 仓库拉取示例](02-gitlab-repo.md) — 使用 GitLab provider
- [自动打开 Notebook](03-open-notebook.md) — 拉取后自动打开指定文件
- [自定义上传路径](04-custom-uploadpath.md) — 将仓库拉取到指定目录

## 相关概念

- [URL参数完整参考](../concepts/06-url-parameters.md) — 所有参数的详细说明
- [平台 Puller 实现](../concepts/04-platform-pullers.md) — GitHub API 调用细节
- [限制与注意事项](../concepts/07-limitations.md) — API 速率限制等使用限制
