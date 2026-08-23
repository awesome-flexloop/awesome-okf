---
type: Reference
title: "自动化脚本信源"
description: "scripts/ 目录包含5个Python脚本，驱动从版本检测到发布准备的全自动化流程"
tags: [jupyterlab, language-pack, scripts, automation, python]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: scripts-source
    resource: https://github.com/jupyterlab/language-packs/tree/master/scripts
    title: "scripts directory"
---

# 自动化脚本信源

## 源码路径

`external/libs/jupyter/language-packs/scripts/`

## 脚本清单

| 脚本 | 功能 | 依赖 |
|------|------|------|
| `01_check_releases.py` | 检测上游新版本，更新 repository-map.yml | github_ql, pyyaml, semantic_version, packaging |
| `02_update_catalogs.py` | 更新 POT 翻译模板，同步 crowdin.yml | jupyterlab_translate, github_ql, git subprocess |
| `03_prepare_release.py` | 准备发布：版本提升、贡献者更新、copier模板更新 | jupyterlab_translate, copier, hatch, git subprocess |
| `04_check_version.py` | 检查所有语言包版本一致性 | hatch subprocess |
| `github_ql.py` | GitHub GraphQL API 封装，获取仓库标签 | requests |

## 01_check_releases.py 关键逻辑

1. 读取 repository-map.yml
2. 通过 GitHub GraphQL API 获取仓库最近100个 tag（按提交日期降序）
3. 解析版本号，跳过 dev/prerelease 版本
4. 发现新版本时更新 current-version-tag
5. 检查新版本是否在 supported-versions 范围内，不在范围则报错
6. JupyterLab 特殊处理：按主版本号前缀过滤 tag

核心函数：
- `get_tags(owner, repo, n=100, filter=None)`：GraphQL 查询标签列表

## 02_update_catalogs.py 关键逻辑

1. `load_repo_map()` / `save_crowdin()` / `load_crowdin()`：配置读写
2. `update_crowdin_config()`：根据 repository-map.yml 自动生成 crowdin.yml files 列表
3. `update_repo(package_name, url, version)`：clone 或 fetch 指定版本的仓库（浅克隆 --depth=1）
4. `update_catalog(package_name, version, merge)`：调用 `jupyterlab_translate.api.extract_language_pack()` 提取/更新 POT 文件
5. 对 supported-versions 范围内的多个版本进行 merge（合并多版本翻译字符串）
6. 最后合并当前版本，确保包含最新字符串

## 03_prepare_release.py 关键逻辑

1. `bumpversion(path, new_version)`：使用 `hatch version` 提升版本
2. `prepare_jupyterlab_lp_release(crowdin_key, new_version)`：
   - 遍历所有语言包目录
   - 第一个包确定最终版本号，其余包使用 copier 更新模板
   - 调用 `jupyterlab_translate.api.create_new_language_pack()` 创建新语言包
   - 调用 `contributors.get_contributors_report()` 更新贡献者列表
   - 每个包单独 git commit

## 04_check_version.py 关键逻辑

1. 遍历 language-packs/ 下所有目录
2. 使用 `hatch version` 获取每个包的版本
3. 检查所有包版本一致，不一致则报错

## github_ql.py 关键逻辑

- 需要 `GITHUB_TOKEN` 环境变量
- 使用 GitHub GraphQL API v4
- 查询 `refs(refPrefix: "refs/tags/", orderBy: {field: TAG_COMMIT_DATE, direction: DESC})`
- 支持按前缀过滤 tag（如 `v4.`）
