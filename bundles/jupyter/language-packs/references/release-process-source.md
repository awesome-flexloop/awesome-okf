---
type: Reference
title: "发布流程信源"
description: "RELEASE.md 描述了从环境准备到 PyPI 发布的完整发布流程"
tags: [jupyterlab, language-pack, release, deployment, cicd]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: release-source
    resource: https://github.com/jupyterlab/language-packs/blob/master/RELEASE.md
    title: "RELEASE.md"
---

# 发布流程信源

## 源码路径

`external/libs/jupyter/language-packs/RELEASE.md`

## 环境准备

```bash
conda create -n language-packs nodejs python -c conda-forge -y -q
conda activate language-packs
pip install -r requirements.txt
npm install gettext-extract -g
```

依赖：
- Node.js + gettext-extract（全局 NPM 包）
- Python 依赖：jupyterlab-translate、copier、hatch、polib、crowdin-api-client 等

## 发布步骤

### 步骤1：更新 Catalogs

前提：JupyterLab 已有 beta 或 RC 版本，代码字符串不再变化。

1. 更新 `repository-map.yml` 指向最新版本
2. 运行 `python scripts/02_update_catalogs.py`
3. 推送到 GitHub，Crowdin 自动加载新 catalogs

### 步骤2：等待翻译

给译者时间更新翻译。

### 步骤3：合并 Crowdin PR

- Crowdin 集成由 JupyterLab-Bot 管理
- 合并前 squash 为单个 commit 保持历史整洁
- 如有冲突，关闭 PR 删除分支，等待重新生成（新分支无冲突）

### 步骤4：准备包

运行 `05_prepare_release.py`（即 `03_prepare_release.py`）：
- 检查哪些包翻译100%完成
- 提升版本号
- 添加 commits 和 tags

### 步骤5：推送提交和标签

```bash
git push upstream --tags
git push upstream master
```

这会触发 GitHub Actions CI 流程，自动在 GitHub 和 PyPI 上创建发布。

## 版本号格式

- 格式：`X.Y.postZ`（如 `4.5.post3`）
- X.Y 跟随 JupyterLab 主版本
- postZ 为翻译修订号
- 默认 `rev` 参数递增 postZ
