---
type: Concept
title: 安装与快速开始
description: 安装 litegitpuller 扩展，了解 URL 参数格式，通过第一个示例快速上手使用。
tags: [getting-started, installation, url-parameters, quickstart, pip]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:56:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:56:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-build-config
    resource: /references/build-config-source.md
    title: 构建配置源码信源
  - id: source-index-ts
    resource: /references/index-ts-source.md
    title: src/index.ts 插件入口源码信源
---

## 安装

litegitpuller 作为 Python 包发布，可以通过 pip 安装：

```bash
pip install litegitpuller
```

安装后，JupyterLab 4.x 会自动识别该扩展（通过 `_jupyter_labextension_paths()` 函数注册），无需手动启用。

### 前置条件

- JupyterLab >= 4.0.0
- Python >= 3.8

### 开发模式安装

如果需要从源码开发：

```bash
# 克隆仓库
git clone https://github.com/jupyterlite/litegitpuller.git
cd litegitpuller

# 安装 Python 包（开发模式）
pip install -e "."

# 链接开发版本到 JupyterLab
jupyter labextension develop . --overwrite

# 构建 TypeScript
jlpm install
jlpm build

# 监听源码变更自动重建
jlpm watch
```

### 卸载

```bash
pip uninstall litegitpuller
```

## URL 参数基础

litegitpuller 完全通过 URL 查询参数驱动。在 JupyterLab/JupyterLite 的 URL 后附加参数即可触发仓库拉取。

### 参数一览

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `repo` | **是** | - | 仓库完整 URL（如 `https://github.com/user/repo`） |
| `branch` | 否 | `main` | 要拉取的分支名 |
| `provider` | 否 | `github` | Git 平台：`github` 或 `gitlab` |
| `urlpath` | 否 | - | 拉取后自动打开的文件路径（相对仓库根目录） |
| `uploadpath` | 否 | `/` | 仓库内容放置的目标目录 |

## 第一个示例：拉取 GitHub 仓库

假设你有一个 JupyterLite 部署在 `https://example.com/lab`，要从 GitHub 拉取一个教程仓库并自动打开 notebook：

```
https://example.com/lab?repo=https%3A%2F%2Fgithub.com%2Fbrichet%2Ftesting-repo&urlpath=notebooks%2Fsimple.ipynb&branch=main
```

解码后的参数：
- `repo`: `https://github.com/brichet/testing-repo`
- `urlpath`: `notebooks/simple.ipynb`
- `branch`: `main`

打开此 URL 后，litegitpuller 会：
1. 在文件浏览器根目录下创建 `testing-repo/` 目录
2. 拉取仓库 main 分支的所有文件到该目录
3. 自动打开 `testing-repo/notebooks/simple.ipynb`

## 参数使用详解

### repo 参数

`repo` 参数必须是完整的仓库 URL，并且需要 URL 编码。

- GitHub 格式：`https://github.com/{owner}/{repo}`
- GitLab 格式：`https://gitlab.com/{owner}/{repo}` 或自建 GitLab 实例 URL

### branch 参数

指定要拉取的分支，默认为 `main`。如果仓库使用 `master` 或其他分支名，需要显式指定：

```
?repo=https%3A%2F%2Fgithub.com%2Fuser%2Frepo&branch=master
```

### provider 参数

支持两个值：
- `github`（默认）：使用 GitHub REST API v3（`api.github.com`）
- `gitlab`：使用 GitLab API v4（`/api/v4/projects/`）

使用 GitLab 时必须显式指定 `provider=gitlab`：

```
?repo=https%3A%2F%2Fgitlab.com%2Fbrichet1%2Ftesting-repo&provider=gitlab&branch=main
```

### urlpath 参数

指定拉取完成后自动打开的文件路径。路径相对于仓库根目录：

```
&urlpath=notebooks/tutorial.ipynb
```

打开后实际路径为 `{uploadpath}/{repo-basename}/{urlpath}`。

### uploadpath 参数

控制仓库克隆到哪个目录下，默认为根目录 `/`。例如设置 `uploadpath=/tutorials`：

```
&uploadpath=/tutorials
```

则仓库内容会被放在 `/tutorials/{repo-basename}/` 下。

## URL 编码注意事项

URL 参数中的特殊字符必须进行百分号编码（percent-encoding）：

| 字符 | 编码 |
|------|------|
| `:` | `%3A` |
| `/` | `%2F` |
| `?` | `%3F` |
| `=` | `%3D` |
| `&` | `%26` |

在 JavaScript 中可以使用 `encodeURIComponent()`，在 Python 中使用 `urllib.parse.quote()`。

## 验证安装

安装后打开 JupyterLab，按 F12 打开浏览器开发者工具，在控制台中应能看到：

```
JupyterLab extension @jupyterlite/litegitpuller is activated!
```

如果看到以下消息，说明 nbgitpuller 已安装且 litegitpuller 自动避让：

```
@jupyterlite/litegitpuller is not activated, to avoid conflict with nbgitpuller
```

## 相关概念

- [litegitpuller 简介](00-introduction.md) — 了解是什么和为什么
- [整体架构](02-architecture.md) — 理解内部工作流程
- [URL参数完整参考](06-url-parameters.md) — 所有参数的详细说明和示例
- [GitHub仓库拉取示例](../examples/01-basic-github.md) — 完整可运行的示例
