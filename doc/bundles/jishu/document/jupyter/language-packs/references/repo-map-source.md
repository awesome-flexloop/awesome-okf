---
type: Reference
title: "repository-map.yml 配置信源"
description: "repository-map.yml 定义了17个包的版本映射，是自动化流水线的核心配置文件"
tags: [jupyterlab, language-pack, configuration, repository-map, version-management]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: repo-map-source
    resource: https://github.com/jupyterlab/language-packs/blob/master/repository-map.yml
    title: "repository-map.yml"
---

# repository-map.yml 配置信源

## 源码路径

`external/libs/jupyter/language-packs/repository-map.yml`

## 配置结构

每个包条目包含三个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `current-version-tag` | string | 当前参考版本的 Git tag（如 `v4.6.1`） |
| `supported-versions` | string | semver 版本范围，npm 语法（如 `>=4.3`、`4.x`、`>=0.40.0`） |
| `url` | string | GitHub 仓库 URL |

## 当前注册包列表（17个）

| 包名 | 当前版本 | 版本范围 | 仓库 |
|------|---------|---------|------|
| dask-labextension | 7.0.0 | >=6.0.0 | dask/dask-labextension |
| jupyter-archive | v3.4.0 | 3.x | jupyterlab-contrib/jupyter-archive |
| jupyter-chat | v0.22.1 | >=0.20.0 | jupyterlab/jupyter-chat |
| jupyter-collaboration | v4.4.1 | >=2.0.0 | jupyterlab/jupyter-collaboration |
| jupyter-resource-usage | v1.2.1 | >=0.6.4 | jupyter-server/jupyter-resource-usage |
| jupyterlab | v4.6.1 | >=4.3 | jupyterlab/jupyterlab |
| jupyterlab-git | v0.54.0 | >=0.40.0 | jupyterlab/jupyterlab-git |
| jupyterlab-lsp | v5.3.0 | >=3.8.0 <3.9.2 \|\| >=3.9.3 | jupyter-lsp/jupyterlab-lsp |
| jupyterlab-recents | v3.3.0 | >=3.3.0 | jupyterlab-contrib/jupyterlab-recents |
| jupyterlab-search-replace | v1.1.3 | >=1.0.0 | jupyterlab-contrib/search-replace |
| jupyterlab-spreadsheet-editor | v0.7.2 | >=0.6.0 | jupyterlab-contrib/jupyterlab-spreadsheet-editor |
| jupyterlab-tour | v4.0.1 | 4.x | jupyterlab-contrib/jupyterlab-tour |
| jupyterlab_widgets | 8.1.8 | 8.x | jupyter-widgets/ipywidgets |
| jupytext | v1.19.4 | >=1.13.2 <2.0.0 | mwouts/jupytext |
| nbdime | v4.0.4 | >=4.0.0 | jupyter/nbdime |
| notebook | v7.6.0 | 7.x | jupyter/notebook |
| spellchecker | v0.8.4 | >=0.7.0 | jupyterlab-contrib/spellchecker |

## 注意事项

- 包名使用 kebab-case（连字符），对应目录名使用 snake_case（下划线）
- `jupyterlab` 作为核心包，版本检测时使用主版本号前缀过滤（如 `v4.`）
- 版本范围使用 npm semver 语法，通过 `semantic_version.NpmSpec` 解析
