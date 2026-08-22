---
type: Reference
title: "GitHub Actions 部署工作流解析"
description: ".github/workflows/deploy.yml的源码级解析：触发条件、权限配置、Node.js/uv环境、mystmd构建、GitHub Pages部署。"
tags: ["github-actions", "cicd", "github-pages", "deploy", "myst"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
sources:
  - resource: "../../../../../../external/libs/jupyter/surveys/.github/workflows/deploy.yml"
    lines: "1-34"
    description: "GitHub Actions部署工作流"
---

# GitHub Actions 部署工作流解析

## 概述

[deploy.yml](../../../../../../external/libs/jupyter/surveys/.github/workflows/deploy.yml) 是Jupyter Surveys的CI/CD流水线，定义在`.github/workflows/deploy.yml`中。工作流在push到master分支时自动构建MyST文档并部署到GitHub Pages。

## 完整工作流结构

### 触发条件

```yaml
on:
  push:
    branches:
      - master
```

仅在向`master`分支push时触发。pull request不触发部署。

### 权限配置

```yaml
permissions:
  contents: write
  pages: write
  id-token: write
```

| 权限 | 用途 |
|------|------|
| `contents: write` | 允许actions部署到gh-pages分支 |
| `pages: write` | 允许写入GitHub Pages |
| `id-token: write` | 支持OIDC认证 |

### build job：构建文档

1. **checkout**：检出仓库代码（actions/checkout@v4）
2. **setup-node**：安装Node.js 20.x（mystmd需要Node.js运行时）
3. **安装uv**：通过pip安装uv包管理器
4. **setup-pages**：配置GitHub Pages环境
5. **构建文档**：`nox -s docs`（设置`BASE_URL: /surveys/`）
6. **上传产物**：将`_build/html/`上传为Pages artifact

### deploy job：部署到GitHub Pages

依赖`build` job完成后，使用`actions/deploy-pages@v4`将artifact部署到GitHub Pages。

## 关键设计决策

| 决策 | 原因 |
|------|------|
| Node.js + Python双环境 | mystmd需要Node.js，nox/uv需要Python |
| uv而非pip直接安装 | 与本地开发环境一致 |
| BASE_URL环境变量 | 解决子路径部署问题（/surveys/而非/） |
| build+deploy分离 | 构建失败不影响部署环境 |

## 常见部署问题排查

1. **样式/图片404**：BASE_URL未设置或错误。检查`BASE_URL: /surveys/`
2. **myst命令找不到**：Node.js版本过旧或依赖未安装
3. **权限错误**：仓库Settings → Pages → Source需设为"GitHub Actions"

## 相关概念

- [CI/CD与GitHub Pages部署](../concepts/07-cicd-deployment.md)：部署流程的概念详解
- [MyST文档系统](../concepts/04-myst-docs-system.md)：mystmd构建工具
- [noxfile.py解析](noxfile-source.md)：本地构建脚本详解
