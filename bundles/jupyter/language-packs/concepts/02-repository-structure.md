---
type: Concept
title: "仓库目录结构"
description: "language-packs 仓库顶层目录布局——配置文件、源码模板、扩展POT、语言包、脚本和CI工作流的组织方式"
tags: [jupyterlab, language-pack, repository, structure, directories]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:23:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-readme, resource: /references/repo-readme.md, title: "仓库根 README 信源" }
  - { id: package-structure, resource: /references/package-structure-source.md, title: "语言包结构信源" }
---

# 仓库目录结构

```
language-packs/
├── .github/                          # GitHub 配置
│   ├── ISSUE_TEMPLATE/               # Issue 模板（bug/feature/新语言）
│   │   ├── bug_report.md
│   │   ├── config.yml
│   │   ├── feature_request.md
│   │   └── new_language.md
│   ├── workflows/                    # CI/CD 工作流（6个）
│   │   ├── check_releases.yml        # 每日检测上游新版本
│   │   ├── check_version.yml         # PR版本一致性检查
│   │   ├── crowdin.yml               # Crowdin 双向同步
│   │   ├── prepare_release.yml       # 手动触发发布准备
│   │   ├── release_publish.yml       # 自动构建发布PyPI
│   │   └── update_pot.yml            # POT模板更新
│   └── dependabot.yml                # 依赖自动更新配置
├── extensions/                       # 扩展POT模板目录
│   ├── dask_labextension/locale/
│   ├── jupyter_archive/locale/
│   ├── jupyter_collaboration/locale/
│   ├── jupyter_resource_usage/locale/
│   ├── jupyterlab_git/locale/
│   ├── jupyterlab_lsp/locale/
│   ├── jupyterlab_recents/locale/
│   ├── jupyterlab_search_replace/locale/
│   ├── jupyterlab_spreadsheet_editor/locale/
│   ├── jupyterlab_tour/locale/
│   ├── jupyterlab_widgets/locale/
│   ├── jupytext/locale/
│   ├── nbdime/locale/
│   ├── notebook/locale/
│   ├── retrolab/locale/              # 已废弃扩展（仍保留POT）
│   └── spellchecker/locale/
├── jupyterlab/                       # JupyterLab核心POT模板
│   └── locale/
│       └── jupyterlab.pot
├── language-packs/                   # 各语言包（31个）
│   ├── README.md                     # 语言包目录说明
│   ├── jupyterlab-language-pack-ach-UG/
│   ├── jupyterlab-language-pack-ar-SA/
│   ├── ...（共31个语言包目录）
│   └── jupyterlab-language-pack-zh-TW/
├── scripts/                          # Python自动化脚本
│   ├── github_ql.py                  # GitHub GraphQL API封装
│   ├── 01_check_releases.py          # 检测上游新版本
│   ├── 02_update_catalogs.py         # 更新POT模板
│   ├── 03_prepare_release.py         # 准备发布
│   └── 04_check_version.py           # 版本一致性检查
├── .gitignore
├── crowdin.yml                       # Crowdin文件映射配置
├── LICENSE.txt                       # BSD-3-Clause许可证
├── README.md                         # 项目说明
├── RELEASE.md                        # 发布流程文档
├── repository-map.yml                # 核心配置：包→版本→URL映射
└── requirements.txt                  # Python依赖
```

## 目录职责

| 目录/文件 | 职责 | 谁来更新 |
|-----------|------|---------|
| `repository-map.yml` | 核心配置，定义要翻译的包和版本 | Bot（01_check_releases.py）或人工PR |
| `crowdin.yml` | Crowdin平台文件映射 | Bot（02_update_catalogs.py自动生成） |
| `jupyterlab/locale/*.pot` | 核心POT模板 | Bot（02_update_catalogs.py） |
| `extensions/*/locale/*.pot` | 扩展POT模板 | Bot（02_update_catalogs.py） |
| `language-packs/*/` | 各语言包（含PO翻译） | Crowdin Bot PR |
| `scripts/` | 自动化Python脚本 | 人工维护 |
| `.github/workflows/` | CI/CD流水线 | 人工维护 |
| `repos/`（.gitignore） | 临时克隆的上游仓库 | 脚本运行时创建 |

## 关键设计

### extensions/ 与 language-packs/ 的分离

- `extensions/` 和 `jupyterlab/` 存放**源语言**的 POT 模板（英文），一个扩展对应一个 POT
- `language-packs/` 存放**目标语言**的翻译，每个语言一个目录，包含所有扩展的 PO 文件

这种分离使得：
1. POT 更新不影响已有的翻译
2. 每个语言包独立打包为 wheel
3. 翻译文件按语言组织，便于 Crowdin 同步

### repos/ 目录

`repos/` 在 .gitignore 中被排除，是脚本运行时临时克隆上游仓库的目录。`02_update_catalogs.py` 执行时会自动创建，使用浅克隆（`--depth=1`）减少下载量。

### .gitignore 关键规则

- `**/LC_MESSAGES/*.json` 和 `**/LC_MESSAGES/*.mo`：构建产物不纳入版本控制
- `repos/`：临时克隆目录
- `node_modules/`：NPM依赖
- 标准Python忽略项（`__pycache__/`、`dist/`、`*.egg-info/`等）

## 相关概念

- [整体架构概览](01-architecture-overview.md)
- [语言包结构剖析](05-package-anatomy.md)
- [自动化脚本体系](07-automation-scripts.md)
