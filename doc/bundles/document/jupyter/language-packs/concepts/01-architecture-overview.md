---
type: Concept
title: "整体架构概览"
description: "language-packs 的五层架构——配置层、源字符串层、翻译层、自动化层、分发层，以及数据流转全链路"
tags: [jupyterlab, language-pack, architecture, pipeline, crowdin]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:23:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-readme, resource: /references/repo-readme.md, title: "仓库根 README 信源" }
  - { id: scripts, resource: /references/scripts-source.md, title: "自动化脚本信源" }
  - { id: workflows, resource: /references/workflows-source.md, title: "CI/CD 工作流信源" }
---

# 整体架构概览

language-packs 项目的架构可以分为五层，形成从源码到用户安装包的完整翻译流水线。

## 五层架构

```
┌─────────────────────────────────────────────────────────────┐
│  ⑤ 分发层 (Distribution)                                     │
│  PyPI + conda-forge 发布 · GitHub Release · pip/conda 安装   │
├─────────────────────────────────────────────────────────────┤
│  ④ 自动化层 (Automation)                                     │
│  GitHub Actions 6个工作流 · Python脚本5个 · Bot身份自动操作   │
├─────────────────────────────────────────────────────────────┤
│  ③ 翻译层 (Translation)                                      │
│  Crowdin 众包平台 · 30+语言 · 译者社区贡献                   │
├─────────────────────────────────────────────────────────────┤
│  ② 源字符串层 (Source Strings)                                │
│  POT模板文件 · jupyterlab-translate提取 · 多版本merge        │
├─────────────────────────────────────────────────────────────┤
│  ① 配置层 (Configuration)                                    │
│  repository-map.yml · crowdin.yml · 版本映射与文件路径配置   │
└─────────────────────────────────────────────────────────────┘
```

### ① 配置层

配置层是整个流水线的"控制中心"，由两个核心 YAML 文件驱动：

- **repository-map.yml**：定义哪些包需要翻译、当前跟踪版本、支持的版本范围、Git 仓库 URL
- **crowdin.yml**：定义源 POT 文件到目标 PO 文件的路径映射规则，支持 `%locale%`、`%file_name%` 等占位符

配置变更触发后续所有流程：添加新扩展 → 更新 repository-map.yml → 自动提取 POT → 同步 Crowdin → 翻译 → 发布。

### ② 源字符串层

源字符串层负责从各上游扩展仓库中提取可翻译字符串：

1. `02_update_catalogs.py` 脚本读取 repository-map.yml
2. 浅克隆（`--depth=1`）每个扩展仓库的指定版本
3. 调用 `jupyterlab_translate.api.extract_language_pack()` 扫描源码
4. 对 supported-versions 范围内的多个版本进行 merge（合并多版本字符串）
5. 生成/更新 POT 文件（extensions/ 和 jupyterlab/ 目录下）

### ③ 翻译层

翻译层由 Crowdin 平台承载：

1. update_pot.yml 工作流检测到 POT 变更后，crowdin.yml 工作流自动上传新 POT 到 Crowdin
2. 全球译者在 Crowdin 平台上翻译字符串（支持 in-context 实时翻译预览）
3. Crowdin 每日定时 + POT 变更触发下载翻译
4. 翻译结果以 PO 文件形式通过 Bot PR 提交到 language-packs 仓库

### ④ 自动化层

自动化层由 GitHub Actions + Python 脚本构成，实现"零人工 Git 操作"：

- **版本检测**：每日定时检查上游新版本，自动更新 repository-map.yml
- **POT 更新**：配置变更后自动提取新字符串
- **翻译同步**：双向同步 Crowdin
- **版本一致性检查**：所有语言包必须版本一致
- **发布准备**：版本提升、贡献者更新、copier 模板同步
- **构建发布**：矩阵构建 30 个语言包 wheel，发布到 PyPI

### ⑤ 分发层

最终产物通过两个渠道分发：

- **PyPI**：`pip install jupyterlab-language-pack-zh-CN`
- **conda-forge**：`conda install -c conda-forge jupyterlab-language-pack-zh-CN`

用户安装后，JupyterLab 通过 entry-point 自动发现语言包。

## 数据流转全链路

```mermaid
flowchart LR
    A[上游扩展仓库<br/>jupyterlab/jupyterlab-git/...] -->|02_update_catalogs.py<br/>jupyterlab-translate| B[POT模板<br/>extensions/*.pot<br/>jupyterlab/locale/*.pot]
    B -->|crowdin.yml Action<br/>upload_sources| C[Crowdin平台]
    D[译者社区] -->|翻译| C
    C -->|crowdin.yml Action<br/>download_translations| E[PO文件<br/>language-packs/*/locale/*/LC_MESSAGES/*.po]
    E -->|prepare_release.yml<br/>03_prepare_release.py| F[版本提升+贡献者更新]
    F -->|release_publish.yml<br/>hatch build| G[Wheel包<br/>*.whl]
    G -->|gh-action-pypi-publish| H[PyPI]
    G -->|手动PR| I[conda-forge]
    H --> J[pip install]
    I --> K[conda install]
    J --> L[用户JupyterLab]
    K --> L
    L -->|entry-point发现<br/>加载.mo/.json| M[本地化界面]

    classDef config fill:#e3f2fd,stroke:#1565c0
    classDef source fill:#f3e5f5,stroke:#7b1fa2
    classDef translate fill:#fff3e0,stroke:#ef6c00
    classDef auto fill:#e8f5e9,stroke:#2e7d32
    classDef dist fill:#fce4ec,stroke:#c62828
    class A,B source; C,D translate; E,F,G auto; H,I,J,K,L,M dist;
```

## 核心设计洞察

### "配置即流水线"

整个系统的"智能"几乎全部编码在 repository-map.yml 和 5 个 Python 脚本中。添加一个新的可翻译扩展，只需要在 YAML 中加三行配置，Bot 自动完成后续所有步骤。

### 人类只做翻译

整个流水线中，人类的唯一手工劳动是在 Crowdin 上翻译字符串。所有 Git 操作、版本管理、包构建、发布均由 Bot 自动完成。这种设计极大降低了贡献门槛——译者不需要懂 Git 或 Python。

### 版本跟随策略

语言包的版本号 `X.Y.postZ` 中，X.Y 跟随 JupyterLab 主版本，postZ 是翻译修订号。这意味着：
- JupyterLab 升级 → 语言包主版本跟着升
- 翻译更新/修正 → postZ 递增
- 所有语言包必须版本完全一致（由 04_check_version.py 强制检查）

## 相关概念

- [仓库目录结构](02-repository-structure.md)
- [repository-map.yml 配置详解](03-repository-map-config.md)
- [Crowdin 翻译平台集成](04-crowdin-integration.md)
- [CI/CD 流水线](08-cicd-pipeline.md)
- [发布流程](09-release-workflow.md)
