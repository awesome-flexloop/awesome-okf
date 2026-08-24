# 实践示例索引

本目录包含 litegitpuller 的使用示例，从基础到进阶，帮助你快速上手各种使用场景。

## 示例列表

| 示例 | 说明 | 涉及参数 |
|------|------|---------|
| [01-GitHub仓库拉取](01-basic-github.md) | 从GitHub拉取公开仓库的最简示例 | repo, branch |
| [02-GitLab仓库拉取](02-gitlab-repo.md) | 从GitLab（含自建实例）拉取仓库 | repo, provider, branch |
| [03-自动打开Notebook](03-open-notebook.md) | 拉取完成后自动打开指定Notebook | repo, urlpath, branch |
| [04-自定义上传路径](04-custom-uploadpath.md) | 将仓库拉取到指定目录 | repo, uploadpath, urlpath |

## 按场景查找示例

### 初次使用
👉 从 [01-GitHub仓库拉取](01-basic-github.md) 开始，了解最基本的URL构造方式。

### 教学/教程分发
👉 使用 [03-自动打开Notebook](03-open-notebook.md) 创建"一键打开教程"链接。

### 使用GitLab
👉 参考 [02-GitLab仓库拉取](02-gitlab-repo.md) 了解provider参数和路径编码。

### 多仓库管理
👉 参考 [04-自定义上传路径](04-custom-uploadpath.md) 将不同仓库组织到不同目录。

## 示例URL模板

快速复制使用，替换占位符即可：

**最简GitHub拉取**：
```
{JUPYTER_URL}?repo=https%3A%2F%2Fgithub.com%2F{OWNER}%2F{REPO}
```

**拉取并打开Notebook**：
```
{JUPYTER_URL}?repo=https%3A%2F%2Fgithub.com%2F{OWNER}%2F{REPO}&urlpath={NOTEBOOK_PATH}
```

**GitLab拉取**：
```
{JUPYTER_URL}?repo=https%3A%2F%2Fgitlab.com%2F{OWNER}%2F{REPO}&provider=gitlab
```

**自定义目录**：
```
{JUPYTER_URL}?repo=https%3A%2F%2Fgithub.com%2F{OWNER}%2F{REPO}&uploadpath=%2F{TARGET_DIR}
```

```{toctree}
:hidden:

01-basic-github
02-gitlab-repo
03-open-notebook
04-custom-uploadpath
```
