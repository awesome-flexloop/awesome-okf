---
type: Reference
title: "CI/CD 工作流配置源码解析"
description: "GitHub Actions 工作流配置（main.yml 和 binder_on_pr.yml）以及 jupyter_notebook_config.py 配置"
tags: [ci, github-actions, micromamba, nbconvert, binder-badge, jupyter-config]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: ci-main, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/.github/workflows/main.yml", title: "main.yml CI workflow" }
  - { id: ci-binder, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/.github/workflows/binder_on_pr.yml", title: "binder_on_pr.yml workflow" }
  - { id: jupyter-config, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/jupyter_notebook_config.py", title: "jupyter_notebook_config.py" }
---

# CI/CD 与配置文件信源

## 源码路径

- `external/libs/jupyter/jupyterlab-demo/.github/workflows/main.yml`
- `external/libs/jupyter/jupyterlab-demo/.github/workflows/binder_on_pr.yml`
- `external/libs/jupyter/jupyterlab-demo/jupyter_notebook_config.py`

## main.yml — CI 构建与测试

### 触发条件

- `push` 到 `master` 分支
- 所有分支的 `pull_request`

### 运行环境

- `runs-on: ubuntu-latest`
- 默认 shell: `bash -el {0}`（登录shell，确保conda环境激活）

### 构建步骤

1. **Checkout**: `actions/checkout@v3`
2. **安装 mamba**: `mamba-org/setup-micromamba@v1`
   - micromamba 版本: `1.5.1-0`
   - 环境文件: `.binder/environment.yml`
   - 环境名称: `jupyterlab-demo`
   - 启用环境缓存: `cache-environment: true`
3. **环境诊断**: 输出 micromamba info/list/config 和环境变量
4. **Notebook 执行验证**:
   ```bash
   jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=60 --stdout notebooks/Data.ipynb > /dev/null
   jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=60 --stdout notebooks/Fasta.ipynb > /dev/null
   jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=60 --stdout notebooks/R.ipynb > /dev/null
   ```
5. **构建验证**: `python build.py`

### 验证范围

CI 验证三个 Notebook 可无错误执行：
- Data.ipynb（数据处理）
- Fasta.ipynb（FASTA序列）
- R.ipynb（R内核）

每个 Notebook 执行超时时间为 60 秒。

## binder_on_pr.yml — PR Binder 徽章

### 触发条件

- `pull_request_target` 事件，类型为 `opened`

### 权限

- `pull-requests: write`（需要写PR评论权限）

### 步骤

使用 `jupyterlab/maintainer-tools/.github/actions/binder-link@v1` 动作：
- 自动在新PR上评论Binder链接
- 允许PR提交者通过Binder预览演示效果
- 需要 `github_token` secrets

## jupyter_notebook_config.py — Jupyter 配置

仅两行配置：

```python
c.LabApp.collaborative = True
c.ContentsManager.allow_hidden = True
```

| 配置项 | 值 | 作用 |
|--------|---|------|
| `c.LabApp.collaborative` | `True` | 启用 JupyterLab 协作模式（多人实时编辑） |
| `c.ContentsManager.allow_hidden` | `True` | 允许文件浏览器显示和访问隐藏文件（以.开头的文件） |
