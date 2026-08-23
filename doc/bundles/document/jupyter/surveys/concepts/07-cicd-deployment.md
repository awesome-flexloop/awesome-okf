---
type: concept
title: "CI/CD与GitHub Pages部署"
description: "Jupyter Surveys的持续集成与部署机制：GitHub Actions工作流、BASE_URL子路径配置、Node.js/Python双环境、GitHub Pages部署流程。"
tags: ["cicd", "github-actions", "github-pages", "deploy", "base_url"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/.github/workflows/deploy.yml"
    lines: "1-34"
    description: "GitHub Actions部署工作流"
  - resource: "../../../../../../external/libs/jupyter/surveys/noxfile.py"
    lines: "1-27"
    description: "Nox构建脚本"
---

# CI/CD与GitHub Pages部署

Jupyter Surveys使用GitHub Actions实现文档的**持续集成和自动部署**——每次push到master分支时，自动构建MyST文档站点并部署到GitHub Pages。

## 部署架构

```
代码push到master
    ↓
GitHub Actions触发
    ↓
┌─────────────────────┐
│  Build Job          │
│  ├─ Checkout代码    │
│  ├─ 安装Node.js 20  │
│  ├─ 安装uv (Python) │
│  ├─ 配置Pages环境   │
│  ├─ nox -s docs     │ ← 构建HTML
│  └─ 上传artifact    │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Deploy Job         │
│  └─ deploy-pages    │ ← 部署到GitHub Pages
└─────────────────────┘
    ↓
https://jupyter.github.io/surveys
```

完整工作流源码见：[GitHub Actions部署工作流解析](../references/deploy-workflow-source.md)

## 工作流配置详解

### 触发条件

```yaml
on:
  push:
    branches:
      - master
```

仅在**向master分支push**时触发。Pull request不会触发部署（避免重复构建），但如果需要PR预览，可以添加`pull_request`触发。

### 权限配置

```yaml
permissions:
  contents: write    # 允许写入gh-pages分支
  pages: write       # 允许配置GitHub Pages
  id-token: write    # OIDC认证（安全部署）
```

这三个权限是GitHub Pages部署的最小权限集。

### 双环境构建

mystmd需要**Node.js**（运行时），nox/uv需要**Python**（构建自动化）：

| 步骤 | 工具 | 用途 |
|------|------|------|
| setup-node@v4 | Node.js 20.x | mystmd CLI运行环境 |
| pip install uv | Python uv | Nox虚拟环境后端 |

### 关键环境变量：BASE_URL

```yaml
- run: nox -s docs
  env:
    BASE_URL: /surveys/
```

**BASE_URL**是部署中最容易出错的配置：

- 本地构建时：站点在根路径（`/`），链接如`/index.html`
- GitHub Pages部署时：站点在子路径（`/surveys/`），链接需变为`/surveys/index.html`

`BASE_URL=/surveys/`告诉mystmd所有内部链接添加`/surveys/`前缀，避免子路径部署时的404错误。

> ⚠️ **常见坑**：忘记设置BASE_URL是部署后样式/图片404的头号原因。本地预览正常但部署后样式丢失，99%是这个问题。

### Build与Deploy分离

工作流分为两个job：

1. **build job**：构建HTML并上传为artifact
2. **deploy job**：依赖build完成后，将artifact部署到Pages

这种分离的好处：
- 构建失败不会影响部署环境
- artifact可以下载调试
- deploy job非常简单（只有一个deploy-pages步骤）

## GitHub Pages配置前提

要让部署成功，仓库需要正确配置GitHub Pages：

1. 进入仓库 Settings → Pages
2. Source选择**"GitHub Actions"**（不是"Deploy from branch"）
3. 确保master分支是默认分支

## 部署故障排查

### 问题1：部署后页面空白/样式404

**症状**：页面加载但没有CSS样式，控制台显示404错误。

**原因**：BASE_URL未设置或设置错误。

**修复**：确认deploy.yml中`BASE_URL: /surveys/`存在且值正确。格式是`/<repo-name>/`（注意前后斜杠）。

### 问题2：myst命令找不到

**症状**：CI日志显示`myst: command not found`。

**原因**：`session.install("-r", "docs/requirements.txt")`未正确执行，或requirements.txt中未列出mystmd。

**修复**：检查`docs/requirements.txt`包含`mystmd`，且`pip install`步骤成功。

### 问题3：权限错误

**症状**：部署失败，日志显示"Permission denied"或"403"。

**原因**：工作流权限不足或Pages未配置为Actions源。

**修复**：
1. Settings → Pages → Source设为"GitHub Actions"
2. 确认workflow文件中有正确的`permissions`配置
3. Settings → Actions → General → Workflow permissions选"Read and write"

### 问题4：本地构建正常但CI失败

**原因**：本地和CI环境差异。常见原因：
- Node.js版本不同（CI用20.x，本地可能是旧版）
- Python依赖版本差异
- 路径大小写敏感（Windows本地不敏感，Linux CI敏感）

**修复**：使用`--ci`标志运行myst命令模拟CI环境。

## 本地验证部署构建

在推送前，可以在本地模拟CI构建：

```bash
# Linux/macOS
BASE_URL=/surveys/ nox -s docs

# Windows PowerShell
$env:BASE_URL="/surveys/"; nox -s docs
```

构建产物在`_build/html/`，用浏览器打开`_build/html/index.html`检查链接是否正确（需要HTTP服务器，不能直接file://打开）。

## 相关内容

- [MyST文档系统](04-myst-docs-system.md)：mystmd构建工具
- [noxfile.py解析](../references/noxfile-source.md)：构建脚本详解
- [部署工作流解析](../references/deploy-workflow-source.md)：完整工作流源码
- [本地构建文档](../examples/01-build-docs-locally.md)：本地构建实战
