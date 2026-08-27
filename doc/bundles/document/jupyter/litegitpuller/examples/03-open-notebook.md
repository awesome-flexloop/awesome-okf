---
type: Example
title: 拉取后自动打开 Notebook
description: 使用 urlpath 参数在仓库拉取完成后自动打开指定的 Jupyter Notebook 或其他文件，实现一键打开教程内容。
tags: [urlpath, auto-open, notebook, tutorial, one-click, example]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:58:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:58:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-index-ts
    resource: /references/index-ts-source.md
    title: src/index.ts 插件入口源码信源
---

## 示例目标

通过 `urlpath` 参数，在仓库拉取完成后自动打开指定的 Notebook 文件，实现"一键打开教程"的用户体验——用户点击链接后，JupyterLab 加载、仓库拉取、Notebook 打开全自动完成。

## 前提条件

- 目标仓库中存在要打开的文件
- 文件路径相对于仓库根目录正确
- 目标文件类型被 JupyterLab 支持（.ipynb、.py、.md 等）

## 基础示例：打开 Notebook

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo&branch=main&urlpath=notebooks%2Fsimple.ipynb
```

解码后：
- `repo` = `https://github.com/brichet/testing-repo`
- `branch` = `main`
- `urlpath` = `notebooks/simple.ipynb`

### 执行流程

1. JupyterLab 页面加载
2. litegitpuller 激活，解析 URL 参数
3. 创建 `testing-repo/` 目录，拉取 main 分支所有文件
4. 拉取完成后，执行 `filebrowser:open-path` 命令
5. JupyterLab 在新标签页打开 `testing-repo/notebooks/simple.ipynb`

## 路径拼接规则

最终打开的文件路径计算公式：

```
最终路径 = {uploadpath}/{仓库名}/{urlpath}
```

默认 `uploadpath` 为 `/`（根目录），所以实际路径为：

```
/{仓库名}/{urlpath}
```

示例：
| repo | urlpath | uploadpath | 最终打开路径 |
|------|---------|------------|-------------|
| `https://github.com/user/repo` | `notebooks/tutorial.ipynb` | `/`（默认） | `/repo/notebooks/tutorial.ipynb` |
| `https://github.com/user/repo` | `README.md` | `/` | `/repo/README.md` |
| `https://github.com/user/repo` | `lectures/w1.ipynb` | `/courses` | `/courses/repo/lectures/w1.ipynb` |

## 打开不同类型文件

`urlpath` 不仅限于 Notebook，可以打开任何 JupyterLab 支持的文件类型：

### 打开 Python 脚本

```
...&urlpath=scripts%2Fanalysis.py
```

### 打开 Markdown 文件

```
...&urlpath=README.md
```

### 打开 CSV 数据文件

```
...&urlpath=data%2Fsample.csv
```

## JavaScript 生成带 urlpath 的链接

```javascript
function createTutorialLink(jupyterLabUrl, repoUrl, notebookPath, branch = 'main') {
  const params = new URLSearchParams({
    repo: repoUrl,
    branch: branch,
    urlpath: notebookPath
  });
  return `${jupyterLabUrl}?${params.toString()}`;
}

// 创建教程链接
const tutorialUrl = createTutorialLink(
  'https://your-jupyterlite.example.com/lab',
  'https://github.com/brichet/testing-repo',
  'notebooks/simple.ipynb',
  'main'
);

// 在网页中创建链接
const link = document.createElement('a');
link.href = tutorialUrl;
link.textContent = '打开教程 Notebook';
link.target = '_blank';
document.body.appendChild(link);
```

## Python 生成带 urlpath 的链接

```python
from urllib.parse import urlencode

def create_tutorial_link(jupyter_lab_url, repo_url, notebook_path, branch='main', provider='github'):
    params = {
        'repo': repo_url,
        'branch': branch,
        'urlpath': notebook_path
    }
    if provider != 'github':
        params['provider'] = provider
    return f"{jupyter_lab_url}?{urlencode(params)}"

# GitHub 教程
url1 = create_tutorial_link(
    'https://your-jupyterlite.example.com/lab',
    'https://github.com/brichet/testing-repo',
    'notebooks/simple.ipynb'
)

# GitLab 教程
url2 = create_tutorial_link(
    'https://your-jupyterlite.example.com/lab',
    'https://gitlab.com/brichet1/testing-repo',
    'notebooks/simple.ipynb',
    provider='gitlab'
)
```

## 教学场景：多教程链接

在教学网站或课程页面中，可以为每个章节创建一个链接：

```html
<h2>Python 数据科学教程</h2>
<ul>
  <li><a href="https://jupyterlite.example.com/lab?repo=https%3A%2F%2Fgithub.com%2Fmyorg%2Fds-course&urlpath=lectures%2F01-intro.ipynb" target="_blank">
    第1讲：Python 入门
  </a></li>
  <li><a href="https://jupyterlite.example.com/lab?repo=https%3A%2F%2Fgithub.com%2Fmyorg%2Fds-course&urlpath=lectures%2F02-pandas.ipynb" target="_blank">
    第2讲：Pandas 数据分析
  </a></li>
  <li><a href="https://jupyterlite.example.com/lab?repo=https%3A%2F%2Fgithub.com%2Fmyorg%2Fds-course&urlpath=lectures%2F03-viz.ipynb" target="_blank">
    第3讲：数据可视化
  </a></li>
</ul>
```

所有链接共享同一个仓库（`myorg/ds-course`），但打开不同的 notebook 文件。由于 litegitpuller 会跳过已存在的文件，第一次访问时拉取全部内容，后续访问直接打开对应文件。

## 注意事项

1. **路径区分大小写**：urlpath 的路径大小写必须与仓库中实际文件路径一致
2. **路径不要以 `/` 开头**：urlpath 是相对于仓库根目录的路径，不要加前导 `/`
3. **目录中的文件不会自动打开**：urlpath 必须指向具体文件，不能指向目录
4. **文件不存在时静默失败**：如果 urlpath 指定的文件在仓库中不存在，命令执行后不会打开任何文件，也不会报错

## 相关示例

- [GitHub 仓库拉取基础示例](01-basic-github.md) — 基础 GitHub 用法
- [GitLab 仓库拉取示例](02-gitlab-repo.md) — GitLab 用法
- [自定义上传路径](04-custom-uploadpath.md) — 结合 uploadpath 使用

## 相关概念

- [URL参数完整参考](../concepts/06-url-parameters.md) — urlpath 参数详解
- [扩展插件机制](../concepts/05-extension-plugin.md) — filebrowser:open-path 命令调用
