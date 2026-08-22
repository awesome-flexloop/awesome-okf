---
type: Reference
title: GitHub Pages 部署流水线信源
description: deploy.yml CI/CD 工作流的完整配置、构建步骤、部署机制登记
tags: [github-pages, ci-cd, deploy, github-actions, workflow, build]
source_type: github-actions-workflow
source_path: .github/workflows/deploy.yml
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: workflow
    resource: https://github.com/jupyterlite/demo/blob/main/.github/workflows/deploy.yml
    title: deploy.yml
---

## 工作流基本信息

| 属性 | 值 |
|------|-----|
| 工作流名称 | Build and Deploy |
| 触发条件 | push 到 main 分支、所有 PR |
| 运行环境 | ubuntu-latest |
| Python 版本 | 3.11 |

## Job 概览

```
build (必跑)
├── 步骤1: Checkout (actions/checkout@v4)
├── 步骤2: Setup Python 3.11 (actions/setup-python@v5)
├── 步骤3: 安装依赖 (pip install -r requirements.txt)
├── 步骤4: 构建站点 (jupyter lite build --contents content --output-dir dist)
└── 步骤5: 上传产物 (actions/upload-pages-artifact@v3 → ./dist)

deploy (仅 main 分支, 依赖 build)
├── 权限: pages:write, id-token:write
├── 环境: github-pages
└── 步骤: Deploy (actions/deploy-pages@v4)
```

## 构建命令详解

```bash
# 将 README.md 复制到内容目录，作为站点内的一个笔记本可访问
cp README.md content

# 构建 JupyterLite 站点
# --contents content: 指定内容目录（笔记本和数据文件所在位置）
# --output-dir dist: 指定输出目录（构建产物存放位置）
jupyter lite build --contents content --output-dir dist
```

关键参数：
- `--contents`：指定内容源目录，构建时会将该目录下的所有文件复制到站点的文件系统中
- `--output-dir`：指定构建输出目录，默认为 `_output/`
- `--lite-dir`（未使用）：指定包含配置文件的目录
- `--apps`（未使用）：指定构建哪些应用（lab、repl、tree、retro 等），默认全部构建

## 部署配置

### deploy job 条件

```yaml
needs: build                    # 必须等待 build 完成
if: github.ref == 'refs/heads/main'  # 仅在 main 分支执行
permissions:
  pages: write                  # Pages 写入权限
  id-token: write               # OIDC token 权限（用于 Pages 认证）
environment:
  name: github-pages            # 使用 github-pages 环境
  url: ${{ steps.deployment.outputs.page_url }}  # 部署后的 URL
```

### Actions 版本

| Action | 版本 | 用途 |
|--------|------|------|
| actions/checkout | v4 | 检出仓库代码 |
| actions/setup-python | v5 | 设置 Python 环境 |
| actions/upload-pages-artifact | v3 | 上传构建产物到 Pages |
| actions/deploy-pages | v4 | 部署到 GitHub Pages |

## 前置条件

要使用此工作流，仓库需要：
1. 在 Settings → Pages 中将 Source 设置为 "GitHub Actions"
2. 确保 requirements.txt 中的依赖可从 PyPI 安装
3. 仓库启用 Actions（默认启用）
