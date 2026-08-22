---
type: Example
title: 自定义上传路径
description: 使用 uploadpath 参数将仓库内容拉取到 JupyterLab 文件浏览器的指定目录中，实现内容分类管理。
tags: [uploadpath, custom-directory, file-organization, example, content-management]
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

使用 `uploadpath` 参数将仓库内容拉取到指定目录而非根目录，实现文件的分类组织，避免多个仓库在根目录下混杂。

## 前提条件

- 理解 URL 参数编码规则
- 如果目标目录不存在，litegitpuller 会自动创建

## 默认行为 vs 自定义路径

### 默认行为（uploadpath=/）

不指定 `uploadpath` 时，仓库默认拉取到根目录：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fuser%2Fmy-repo
```

文件结构：
```
/
├── my-repo/          ← 仓库在根目录
│   ├── notebooks/
│   ├── data/
│   └── README.md
└── ...
```

### 自定义路径

指定 `uploadpath=/tutorials`：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fuser%2Fmy-repo&uploadpath=%2Ftutorials
```

文件结构：
```
/
├── tutorials/
│   └── my-repo/      ← 仓库在 tutorials/ 下
│       ├── notebooks/
│       ├── data/
│       └── README.md
└── ...
```

## 路径计算规则

源码中 `basePath` 的计算方式：

```typescript
const uploadPath = urlParams.get('uploadpath') || '/';
const basePath = PathExt.join(uploadPath, PathExt.basename(repo));
```

即：`basePath = {uploadpath} + "/" + {仓库名（从repo URL提取）}`。

`PathExt.basename(repo)` 提取 URL 路径的最后一段作为目录名：

| repo URL | PathExt.basename(repo) |
|----------|----------------------|
| `https://github.com/user/my-repo` | `my-repo` |
| `https://github.com/user/project.git` | `project.git`（注意：不会去除.git后缀） |
| `https://gitlab.com/group/sub/project` | `project` |

## 多层嵌套目录示例

将仓库放到 `/courses/2024/python/` 目录下：

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fcourse%2Fpython-101&uploadpath=%2Fcourses%2F2024%2Fpython
```

最终路径：`/courses/2024/python/python-101/`

litegitpuller 会自动创建路径上不存在的目录（`courses/`、`courses/2024/`、`courses/2024/python/`）。

## 多仓库分类组织

通过不同的 uploadpath，可以将多个仓库组织到不同目录中：

```html
<!-- 教程仓库 -->
<a href="...?repo=...&uploadpath=%2Ftutorials">教程仓库</a>

<!-- 数据集仓库 -->
<a href="...?repo=...&uploadpath=%2Fdatasets">数据集仓库</a>

<!-- 项目模板仓库 -->
<a href="...?repo=...&uploadpath=%2Ftemplates">模板仓库</a>
```

文件结构：
```
/
├── tutorials/
│   ├── repo-a/
│   └── repo-b/
├── datasets/
│   └── sample-data/
└── templates/
    └── ml-template/
```

## 结合 urlpath 使用

uploadpath 可以与 urlpath 结合，将仓库拉取到指定目录并自动打开文件。

```
http://localhost:8888/lab?repo=https%3A%2F%2Fgithub.com%2Fcourse%2Fpython-101&uploadpath=%2Fcourses%2F2024&branch=main&urlpath=lectures%2Fweek1.ipynb
```

最终打开的文件路径：`/courses/2024/python-101/lectures/week1.ipynb`

计算过程：
1. `uploadpath` = `/courses/2024`
2. 仓库名 = `python-101`
3. `basePath` = `/courses/2024/python-101`
4. `urlpath` = `lectures/week1.ipynb`
5. 最终路径 = `/courses/2024/python-101/lectures/week1.ipynb`

## JavaScript 示例：课程链接生成器

```javascript
function createCourseLink(jupyterLabUrl, repoUrl, notebookPath, 
                          category = 'tutorials', branch = 'main') {
  const params = new URLSearchParams({
    repo: repoUrl,
    branch: branch,
    urlpath: notebookPath,
    uploadpath: `/${category}`
  });
  return `${jupyterLabUrl}?${params.toString()}`;
}

// 教程类
const tutorialLink = createCourseLink(
  'https://jupyterlite.example.com/lab',
  'https://github.com/brichet/testing-repo',
  'notebooks/simple.ipynb',
  'tutorials'
);

// 工作坊类
const workshopLink = createCourseLink(
  'https://jupyterlite.example.com/lab',
  'https://github.com/org/workshop-materials',
  'index.ipynb',
  'workshops/2024'
);
```

## Python 示例：批量生成课程链接

```python
from urllib.parse import urlencode

def create_course_link(jupyter_lab_url, repo_url, notebook_path, 
                       upload_path='/tutorials', branch='main'):
    params = {
        'repo': repo_url,
        'branch': branch,
        'urlpath': notebook_path,
        'uploadpath': upload_path
    }
    return f"{jupyter_lab_url}?{urlencode(params)}"

courses = [
    {
        'name': 'Python 入门',
        'repo': 'https://github.com/course/python-intro',
        'notebook': 'lectures/01-intro.ipynb',
        'category': '/courses/python'
    },
    {
        'name': '机器学习',
        'repo': 'https://github.com/course/ml-basics',
        'notebook': 'notebooks/01-overview.ipynb',
        'category': '/courses/ml'
    }
]

for course in courses:
    url = create_course_link(
        'https://jupyterlite.example.com/lab',
        course['repo'],
        course['notebook'],
        upload_path=course['category']
    )
    print(f"{course['name']}: {url}")
```

## uploadpath 注意事项

1. **路径编码**：uploadpath 值中的 `/` 需要编码为 `%2F`（如 `/tutorials` 编码为 `%2Ftutorials`）
2. **开头斜杠**：路径建议以 `/` 开头，表示从根目录开始；不以 `/` 开头的行为可能不一致
3. **仓库名自动添加**：不需要在 uploadpath 中包含仓库名，系统会自动追加 `PathExt.basename(repo)`
4. **目录自动创建**：路径上的所有不存在的目录都会自动创建，无需预建
5. **与 nbgitpuller 的差异**：nbgitpuller 使用 `urlpath` 参数来同时指定目标路径和打开文件，litegitpuller 将这两个功能分离到 `uploadpath` 和 `urlpath` 两个参数

## 相关示例

- [GitHub 仓库拉取基础示例](01-basic-github.md) — 基础用法
- [自动打开 Notebook](03-open-notebook.md) — urlpath 用法
- [GitLab 仓库拉取示例](02-gitlab-repo.md) — GitLab 用法

## 相关概念

- [URL参数完整参考](/concepts/06-url-parameters.md) — uploadpath 参数详解
- [GitPuller 抽象基类](/concepts/03-gitpuller-base.md) — createTree 目录创建逻辑
