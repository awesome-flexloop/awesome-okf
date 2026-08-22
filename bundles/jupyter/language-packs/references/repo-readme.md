---
type: Reference
title: "仓库根 README 信源"
description: "language-packs 仓库 README.md 原始内容解析——安装方式、新扩展添加流程、贡献指南"
tags: [jupyterlab, language-pack, i18n, readme]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme-source
    resource: https://github.com/jupyterlab/language-packs/blob/master/README.md
    title: "Jupyterlab Language Packs README"
---

# 仓库根 README 信源

## 源码路径

`external/libs/jupyter/language-packs/README.md`

## 原始内容关键事实

### 项目定位

JupyterLab 语言包 monorepo，提供 JupyterLab 及其扩展的多语言翻译包。

### 安装方式

通过 PyPI 或 conda-forge 安装特定语言包，例如：

```bash
pip install jupyterlab-language-pack-zh-CN
conda install -c conda-forge jupyterlab-language-pack-zh-CN
```

### 特殊包警告

- `jupyterlab-language-pack-ach-UG` 是伪语言包，用于 Crowdin in-context 翻译功能，不应显式安装，其翻译内容无实际意义

### 添加新扩展流程

1. 在 `repository-map.yml` 中添加新条目（按字母顺序）
2. 三个必填字段：
   - `current-version-tag`：最新 Git tag
   - `supported-versions`：semver 范围（npm 语法）
   - `url`：GitHub 仓库 URL（仅支持 HTTP）
3. PR 合并后，Bot 会在后续 PR 中创建/更新 `.pot` 文件
4. 新扩展目录在 Crowdin 上可用后，译者可开始翻译
5. 翻译完成后自动发布为 Python 包（PyPI）和 conda 包（conda-forge）

### 版本收集逻辑

1. 获取 GitHub 仓库最近 100 个 tag
2. 使用 Python `packaging.version.parse` 解析，过滤 dev/prerelease 版本
3. 检查 tag 是否在 `supported-versions` 范围内

### 分支支持

`current-version-tag` 可以是分支名（不推荐），此时 `supported-versions` 无效，仅从当前分支 HEAD 提取字符串。

### 贡献方式

通过 [Crowdin 平台](https://crowdin.com/project/jupyterlab) 贡献翻译。
