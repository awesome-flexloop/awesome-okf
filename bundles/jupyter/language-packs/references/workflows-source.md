---
type: Reference
title: "CI/CD 工作流信源"
description: "GitHub Actions 6个工作流实现全自动翻译流水线：版本检测→POT更新→Crowdin同步→发布构建→PyPI发布"
tags: [jupyterlab, language-pack, github-actions, cicd, automation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: workflows-source
    resource: https://github.com/jupyterlab/language-packs/tree/master/.github/workflows
    title: "GitHub workflows"
---

# CI/CD 工作流信源

## 源码路径

`external/libs/jupyter/language-packs/.github/workflows/`

## 工作流清单

| 工作流文件 | 触发条件 | 核心功能 |
|-----------|---------|---------|
| `check_releases.yml` | 每日定时（2:42 UTC）+ 手动 | 运行 `01_check_releases.py`，检测上游新版本，自动创建PR |
| `update_pot.yml` | repository-map.yml 推送 + 手动 | 运行 `02_update_catalogs.py`，更新POT文件，创建PR |
| `crowdin.yml` | POT文件推送 + 每日定时（1:45 UTC）+ 手动 | Crowdin GitHub Action：上传源文件、下载翻译、创建PR |
| `check_version.yml` | PR中 `__init__.py` 变更 | 运行 `04_check_version.py`，检查版本一致性 |
| `prepare_release.yml` | 手动触发（可指定版本） | 运行 `03_prepare_release.py`，准备发布 |
| `release_publish.yml` | `__init__.py` 推送到main + 手动 | 版本检查→构建wheel→GitHub Release→PyPI发布 |

## check_releases.yml

- 定时：`cron: 42 2 * * *`（每日UTC 2:42）
- 环境：ubuntu-latest, Python 3.9
- 步骤：checkout → 安装依赖 → 运行01脚本 → 如有变更创建PR
- PR标题：`New releases available at {SHA}`
- Bot身份：JupyterLab Language Packs Bot

## update_pot.yml

- 触发：push 到 main 且路径包含 repository-map.yml
- 需安装系统 gettext：`sudo apt-get install gettext`
- 步骤：checkout → 安装gettext → Python 3.9 → 安装依赖 → 运行02脚本 → 如有变更创建PR
- 只检查 `*.pot` 和 `crowdin.yml` 的变更
- PR标题：`Update pot files`

## crowdin.yml

- 触发：push 到 main（`**.pot`路径）+ 定时 `45 1 * * *` + 手动
- 使用 `crowdin/github-action@v2`
- 配置：
  - `upload_sources: true`（上传POT源文件）
  - `upload_translations: false`（不上传翻译）
  - `download_translations: true`（下载翻译）
  - `export_only_approved: false`（非只下载已审核）
  - 分支：main
  - 翻译PR分支：`l10n_crowdin_translations`
- Secrets：`CROWDIN_PROJECT_ID`、`CROWDIN_TOKEN`
- PR标题：`New Crowdin updates`

## prepare_release.yml

- 触发：手动 workflow_dispatch，可输入 version 参数（默认 `rev`）
- 步骤：checkout → Python 3.9 → 安装依赖 → 创建分支 → 设置git身份 → 运行03脚本 → 推送 → 创建PR
- 需要 `CROWDIN_API_KEY` secret（即 CROWDIN_TOKEN）
- PR标题：`Update language packs to '{version}'`

## release_publish.yml

- 触发：push 到 main 且路径匹配 `language-packs/**/__init__.py` + 手动
- 三阶段流水线：

### Stage 1: check-version
运行 `04_check_version.py` 确保所有语言包版本一致

### Stage 2: build-artifacts（矩阵构建）
- `fail-fast: false`：一个语言包失败不影响其他
- 矩阵包含30个语言 locale（ach-UG 到 zh-TW）
- 每个 locale 独立构建：
  1. `python -m build` 构建 wheel
  2. `twine check dist/*` 验证包
  3. 上传 artifact
  4. 创建 GitHub Release（tag 格式：`{locale}@v{version}`）
- 支持 `skipRelease` 参数跳过 release 创建

### Stage 3: publish
- 需要 `id-token: write` 权限（PyPI 可信发布）
- 下载所有 artifacts
- 使用 `pypa/gh-action-pypi-publish@release/v1` 发布到 PyPI
- `skip-existing: true`：已存在的包跳过

## 关键设计模式

1. **Bot 自动化**：所有自动提交使用统一 Bot 身份
2. **PR 驱动**：所有变更通过 PR 进入 main，不直接推送
3. **Crowdin 集成**：官方 Action 处理双向同步
4. **矩阵构建**：30个语言包并行构建，互不阻塞
5. **版本一致性门**：发布前强制检查版本统一
