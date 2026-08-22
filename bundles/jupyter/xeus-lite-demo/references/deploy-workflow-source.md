---
type: Reference
title: GitHub Actions CI/CD 流水线信源
description: .github/workflows/deploy.yml 完整内容登记，定义自动构建和部署到 GitHub Pages 的流程
tags: [github-actions, cicd, deploy, github-pages, reference]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: deploy-yml
    resource: https://github.com/jupyterlite/xeus-lite-demo/blob/main/.github/workflows/deploy.yml
    title: xeus-lite-demo .github/workflows/deploy.yml
---

## 源文件路径

`.github/workflows/deploy.yml`

## 完整工作流结构

### 触发条件

```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - '*'
```

- push 到 main 分支 → 触发 build + deploy
- PR 到任意分支 → 只触发 build（验证不部署）

### Build Job

| 步骤 | Action | 配置 |
|------|--------|------|
| Checkout | `actions/checkout@v3` | 检出仓库代码 |
| Setup Python | `actions/setup-python@v5` | Python 3.12 |
| Install mamba | `mamba-org/setup-micromamba@v1` | micromamba 1.5.8-0，使用 .github/build-environment.yml，启用缓存 |
| Build JupyterLite | shell: `bash -l {0}` | `cp README.md content && jupyter lite build --contents content --output-dir dist` |
| Upload artifact | `actions/upload-pages-artifact@v3` | path: `./dist` |

### Deploy Job

| 属性 | 值 |
|------|-----|
| 依赖 | `needs: build` |
| 条件 | `github.ref == 'refs/heads/main'`（仅 main 分支部署） |
| 权限 | `pages: write`, `id-token: write` |
| 环境 | name: `github-pages`，url: `${{ steps.deployment.outputs.page_url }}` |
| 运行平台 | `ubuntu-latest` |
| 部署步骤 | `actions/deploy-pages@v4`，id: `deployment` |

## 构建命令解析

```bash
cp README.md content          # 将 README 复制到 content 目录，在 JupyterLite 中可访问
jupyter lite build \
  --contents content \        # 指定内容目录（包含 Notebook 和 README）
  --output-dir dist           # 输出目录（静态站点产物）
```

## 关键说明

- 使用 micromamba（轻量 mamba 实现）而非 conda，加快环境创建速度
- `cache-environment: true` 缓存 conda 环境，加速后续构建
- `bash -l {0}` 使用 login shell，确保 conda/mamba 初始化脚本正确加载
- build job 始终运行（含 PR），deploy job 仅在 main 分支 push 时运行
- 产物通过 upload-pages-artifact 传递给 deploy job
- 使用 OIDC（id-token: write）进行 GitHub Pages 认证，无需手动配置 token
