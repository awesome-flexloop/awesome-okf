---
type: Concept
title: GitHub 模板三步部署
description: 通过 GitHub Template 创建仓库、启用 GitHub Pages、自定义环境，三步完成 xeus-lite 部署
tags: [deployment, github-template, github-pages, getting-started, ci-cd]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
  - id: deploy-wf
    resource: /references/deploy-workflow-source.md
    title: CI/CD 流水线信源
---

## 三步部署流程

xeus-lite-demo 设计为极简部署体验，只需三步即可上线一个完整的 JupyterLite 站点。

### 步骤 1：使用 GitHub 模板创建仓库

1. 打开 [xeus-lite-demo 仓库](https://github.com/jupyterlite/xeus-lite-demo)
2. 点击右上角的 **"Use this template"** 按钮
3. 选择 **"Create a new repository"**
4. 填写：
   - **Repository name**：你的项目名（如 `my-jupyterlite`）
   - **Description**：可选描述
   - **Public/Private**：Public（GitHub Pages 免费版需要 Public 仓库，或使用 Pro 版的 Private Pages）
5. 点击 **"Create repository from template"**

完成后你就拥有了一个包含完整 CI/CD 配置的 xeus-lite 仓库。

### 步骤 2：启用 GitHub Pages

创建仓库后，需要启用 GitHub Pages 以启用自动部署：

1. 进入你刚创建的仓库页面
2. 点击 **Settings**（设置）标签
3. 在左侧菜单找到 **Pages**
4. 在 **Source** 部分，将下拉菜单从 "Deploy from a branch" 改为 **"GitHub Actions"**
5. 不需要配置其他选项

> 💡 这一步是必须的——如果不启用 GitHub Pages，deploy job 会因为权限不足而失败。

### 步骤 3：自定义 conda 环境

现在你可以编辑 `environment.yml` 来定制你需要的包：

1. 在仓库页面点击 `environment.yml` 文件
2. 点击编辑图标（铅笔图标✏️）
3. 修改 `dependencies` 列表，添加你需要的包
4. 在页面底部填写 commit message，点击 **"Commit changes"**

push 到 main 分支后，GitHub Actions 会自动触发构建和部署。

## 访问你的站点

部署成功后，你的 JupyterLite 站点将可通过以下 URL 访问：

```
https://{你的用户名}.github.io/{仓库名}/
```

例如：用户 `johndoe` 创建了 `my-jupyterlite` 仓库，站点地址为：
`https://johndoe.github.io/my-jupyterlite/`

首次部署通常需要 3-5 分钟。你可以在 **Actions** 标签页查看构建进度。

## 自动部署机制

理解自动部署的工作原理有助于排查问题：

1. **push 到 main 分支** → 触发 `build` job → 构建静态站点 → 触发 `deploy` job → 部署到 GitHub Pages
2. **Pull Request** → 只触发 `build` job（验证构建是否成功，不部署）
3. **构建缓存** → micromamba 环境被缓存，后续构建更快

你可以在仓库的 **Actions** 标签页查看每次构建的状态和日志。

## 无需本地工具的工作流

xeus-lite-demo 支持完全在 GitHub 网页上操作，不需要本地安装 git、conda 或任何工具：

| 操作 | 网页操作方式 |
|------|------------|
| 添加 Notebook | 上传 .ipynb 文件到 `content/` 目录（Add file → Upload files） |
| 编辑 Notebook | 目前不支持网页编辑 .ipynb，建议本地编辑后上传 |
| 添加包 | 直接在网页上编辑 `environment.yml` |
| 查看部署状态 | 点击 Actions 标签页 |
| 访问站点 | 打开 `https://{user}.github.io/{repo}/` |

## 本地构建（可选）

如果你想在本地预览修改效果，可以在本地构建：

```bash
# 创建构建环境
conda env create -f .github/build-environment.yml
conda activate build-env

# 构建站点
cp README.md content
jupyter lite build --contents content --output-dir dist

# 本地预览
jupyter lite serve --contents content
# 访问 http://localhost:8000
```

> 本地构建需要安装 conda（或 mamba/micromamba），适合需要频繁调整配置的场景。大部分用户不需要本地构建，直接利用 GitHub Actions 即可。

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Actions 中 deploy job 失败 | GitHub Pages 未启用 | 回到步骤2，确认 Source 设置为 "GitHub Actions" |
| 站点打开 404 | 首次部署尚未完成 | 等待 Actions 完成，或检查仓库名是否正确 |
| import 包报错 | 包未加入 environment.yml 或包无 WASM 版本 | 检查 environment.yml，确认包在 emscripten-forge 中可用 |
| 构建时间过长 | 首次构建需要下载包 | 后续构建会使用缓存，等待即可 |

## 相关概念

- [xeus-lite-demo 简介](00-introduction.md) — 了解项目全貌
- [CI/CD 流水线](06-cicd-pipeline.md) — 深入理解 GitHub Actions 工作流
- [运行时环境配置](04-runtime-env-config.md) — 如何配置 environment.yml
- [创建第一个部署](../examples/01-first-deployment.md) — 图文实操指南
