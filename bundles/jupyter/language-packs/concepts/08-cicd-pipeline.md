---
type: Concept
title: "CI/CD 流水线"
description: "6 个 GitHub Actions 工作流构成的自动化流水线——版本检测、POT更新、Crowdin同步、版本检查、发布准备、构建发布的完整链路"
tags: [jupyterlab, language-pack, github-actions, cicd, workflow, automation]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: workflows, resource: /references/workflows-source.md, title: "CI/CD 工作流信源" }
  - { id: scripts, resource: /references/scripts-source.md, title: "自动化脚本信源" }
---

# CI/CD 流水线

language-packs 使用 6 个 GitHub Actions 工作流实现端到端自动化。整个流水线设计目标是**人类译者不需要任何 Git 操作**——从版本检测到翻译同步到 PyPI 发布，全部由 Bot 自动完成。

## 工作流总览

```mermaid
flowchart TB
    subgraph "定时触发（每日）"
        A[check_releases.yml<br/>0:00 UTC]
    end
    
    subgraph "配置/POT变更触发"
        B[update_pot.yml<br/>repository-map或POT变更]
    end
    
    subgraph "Crowdin同步"
        C[crowdin.yml<br/>POT变更/每日1:45 UTC/手动]
    end
    
    subgraph "PR检查"
        D[check_version.yml<br/>每次PR]
    end
    
    subgraph "手动触发"
        E[prepare_release.yml<br/>workflow_dispatch]
    end
    
    subgraph "自动发布"
        F[release_publish.yml<br/>GitHub Release发布]
    end
    
    A -->|更新repository-map.yml PR| B
    B -->|更新POT/crowdin.yml PR| C
    C -->|上传POT到Crowdin| G[Crowdin平台]
    G -->|翻译完成下载| H[翻译PR]
    H -->|触发PR检查| D
    E -->|版本提升/贡献者更新| I[版本更新PR]
    I -->|创建GitHub Release| F
    F -->|构建30个wheel| J[PyPI发布]
    
    classDef trigger fill:#e3f2fd,stroke:#1565c0
    classDef auto fill:#e8f5e9,stroke:#2e7d32
    classDef manual fill:#fff3e0,stroke:#ef6c00
    classDef external fill:#fce4ec,stroke:#c62828
    class A,B,C,D auto; E manual; F auto; G,H,J external
```

## 1. check_releases.yml — 版本检测

| 属性 | 值 |
|------|-----|
| **触发** | 每日 cron `0 0 * * *`（UTC 0:00）+ 手动 |
| **权限** | contents: write, pull-requests: write |
| **环境** | ubuntu-latest, Python 3.x |
| **核心步骤** | 安装依赖 → 配置Bot身份 → 运行 `01_check_releases.py` |

### 工作原理
1. Checkout 仓库（persist-credentials: true 允许 push）
2. 安装 requirements.txt 中的依赖
3. 设置 git user 为 `github-actions[bot]`
4. 运行 `01_check_releases.py`，脚本检测到新版本会：
   - 更新 repository-map.yml
   - 创建新分支 `bot-releases`
   - commit 并 push
   - 通过 GitHub API 创建 PR，打 `github-actions` 标签

## 2. update_pot.yml — POT 更新

| 属性 | 值 |
|------|-----|
| **触发** | push/PR 到 main（路径过滤：repository-map.yml、.pot文件、scripts/、本工作流文件）|
| **权限** | contents: write, pull-requests: write |
| **环境** | ubuntu-latest, Python 3.12（miniconda）|
| **核心步骤** | 安装jupyterlab-translate+copier → 配置Bot → 运行 `02_update_catalogs.py` |

### 关键配置
- 使用 `conda-incubator/setup-miniconda` 配置 Python 环境
- 依赖安装顺序：requirements.txt → jupyterlab-translate[cli]（可编辑安装）→ copier
- 多文件修改但脚本只创建一个 PR（所有变更在一个 commit 中）
- `persist-credentials: true` 使 checkout 的 token 可用于 push

## 3. crowdin.yml — Crowdin 双向同步

| 属性 | 值 |
|------|-----|
| **触发** | push 到 main（.pot或crowdin.yml变更）+ 每日 cron `45 1 * * *` + 手动 |
| **权限** | contents: write, pull-requests: write |
| **环境** | ubuntu-latest |
| **核心动作** | `crowdin/github-action@v2` |

### 双向操作参数

**上传源文件（Push POT）**：
- `upload_sources: true`
- `download_translations: false`（push触发时只上传）
- 参数：`--branch=main --preserve-hierarchy`
- 条件：`github.event_name != 'schedule' && github.event.action != 'download_translations'`

**下载翻译（Pull PO）**：
- `upload_sources: false`
- `download_translations: true`
- 参数：`--branch=main`
- `export_only_approved: false`（下载所有翻译，不只审核通过的）
- `push_translations: true`（自动创建PR）
- 自动创建分支 `l10n_crowdin_translations`

### Crowdin Action 配置
- `crowdin_branch_name: main`
- `config: crowdin.yml`
- `project_id: ${{ secrets.CROWDIN_PROJECT_ID }}`
- `token: ${{ secrets.CROWDIN_TOKEN }}`
- `create_pull_request: true`（下载后自动创建PR）

## 4. check_version.yml — 版本一致性检查

| 属性 | 值 |
|------|-----|
| **触发** | pull_request（所有PR）|
| **权限** | 最小权限（无特殊write）|
| **环境** | ubuntu-latest, Python 3.x |
| **核心步骤** | 运行 `04_check_version.py` |

### 工作原理
1. Checkout PR 的代码
2. 安装 Python
3. 运行 `python scripts/04_check_version.py`
4. 如果有语言包版本不一致，脚本返回非零退出码，PR 检查失败

这是质量门禁，确保不会出现"中文包版本4.5.post1，法文包版本4.5.post0"的情况。

## 5. prepare_release.yml — 发布准备

| 属性 | 值 |
|------|-----|
| **触发** | workflow_dispatch（手动，可指定 version-tag 参数）|
| **权限** | contents: write, pull-requests: write |
| **环境** | ubuntu-latest, Python 3.12（miniconda）+ Node.js 20 |
| **核心步骤** | 版本更新 → 贡献者更新 → Copier同步 → 版本检查 |

### 输入参数
- `version-tag`：可选，指定要发布的版本tag，默认为最新tag

### 详细步骤
1. Checkout 完整历史（fetch-depth: 0）
2. 安装 Python 依赖 + copier + jupyterlab-translate
3. 运行 `03_prepare_release.py --version-tag <tag>`：
   - 版本提升：更新所有 `__init__.py`
   - 贡献者：调用 Crowdin API 获取翻译贡献者，更新 CONTRIBUTORS.md
   - Copier：对每个语言包执行 `copier update` 同步模板
4. 创建发布准备 PR
5. 人工审查合并后，手动创建 GitHub Release 触发发布

## 6. release_publish.yml — 构建发布

| 属性 | 值 |
|------|-----|
| **触发** | release published（GitHub Release 创建/发布时）|
| **权限** | contents: read, id-token: write（PyPI trusted publisher）|
| **环境** | ubuntu-latest, Python 3.12（miniconda）|
| **核心步骤** | 矩阵构建30个语言包 → 发布到PyPI |

### 矩阵构建策略
- 不使用 GitHub Actions 的 matrix 策略
- 而是由 `build.yaml` 共享配置 + 手动遍历 `language-packs/` 目录
- 使用 `jupyter-releaser` 钩子：`before-build-npm`、`before-build-python`（跳过JavaScript构建）、`before-publish-dist`
- 通过 `gh-action-pypi-publish` 发布到 PyPI
- 支持 PyPI trusted publisher（OIDC认证，无需长期token）

### 构建流程
1. 对每个语言包目录：
   - 读取 pyproject.toml
   - 安装依赖（hatchling + jupyterlab-translate）
   - 运行 hatch build 编译 PO → MO/JSON
   - 生成 wheel 和 sdist
2. 使用 twine 或 gh-action-pypi-publish 上传所有 wheel

## Secrets 配置汇总

| Secret | 使用工作流 | 获取方式 |
|--------|-----------|---------|
| `BOT_TOKEN` / `GITHUB_TOKEN` | check_releases, update_pot, prepare_release | GitHub App 自动/内置 |
| `CROWDIN_PROJECT_ID` | crowdin | Crowdin 项目设置 → API |
| `CROWDIN_TOKEN` | crowdin | Crowdin 个人访问令牌 |
| `CROWDIN_API_KEY` | prepare_release | 同 CROWDIN_TOKEN |
| PyPI trusted publisher | release_publish | PyPI 项目设置 → 配置 |

## 路径触发过滤

workflow 使用 `paths` 过滤避免不必要的触发：

```yaml
paths:
  - 'repository-map.yml'
  - 'jupyterlab/**/*.pot'
  - 'extensions/**/*.pot'
  - 'scripts/**'
  - '.github/workflows/update_pot.yml'
```

翻译文件（.po）变更通过 Crowdin Action 处理，不触发 update_pot 工作流。

## 常见操作模式

### "正常翻译更新"模式
```
每日定时: check_releases → 发现新版本 → PR更新map → update_pot → 更新POT → crowdin上传
                                                                    ↓
每日定时: crowdin下载翻译 → PR → 审查squash合并 → 积累足够翻译 → 手动prepare_release
                                                                              ↓
                            PyPI发布 ← release_publish ← 创建GitHub Release ←
```

### "翻译PR处理"模式
- Crowdin 创建的 PR 必须 squash 合并
- 如有冲突：关闭 PR、删除分支、等 Crowdin 重新生成
- 不要直接在 PR 中修改 .po 文件

## 相关概念

- [自动化脚本体系](07-automation-scripts.md)
- [发布流程](09-release-workflow.md)
- [Crowdin 翻译平台集成](04-crowdin-integration.md)
