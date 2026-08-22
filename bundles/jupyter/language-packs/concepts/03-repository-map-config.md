---
type: Concept
title: "repository-map.yml 配置详解"
description: "repository-map.yml 是流水线的核心配置文件——定义包版本映射、semver范围、上游仓库URL，驱动所有自动化流程"
tags: [jupyterlab, language-pack, configuration, yaml, semver, versioning]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:23:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-map, resource: /references/repo-map-source.md, title: "repository-map.yml 配置信源" }
  - { id: scripts, resource: /references/scripts-source.md, title: "自动化脚本信源" }
---

# repository-map.yml 配置详解

`repository-map.yml` 是 language-packs 仓库最核心的配置文件，定义了"哪些包的哪些版本需要翻译"。所有自动化脚本（版本检测、POT更新、Crowdin同步）都以此文件为输入。

## 文件位置

仓库根目录：`repository-map.yml`

## 配置格式

```yaml
{package-name}:
  current-version-tag: {git-tag}
  supported-versions: {semver-range}
  url: https://github.com/{owner}/{repo}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `current-version-tag` | string | ✅ | 当前跟踪的 Git tag（或分支名），Bot 检测到新版本时自动更新 |
| `supported-versions` | string | ✅ | npm 风格的 semver 版本范围，用于多版本字符串合并 |
| `url` | string | ✅ | GitHub 仓库 URL（仅支持 github.com HTTP URL） |

## 包名命名规则

- 包名使用 **kebab-case**（连字符分隔），与 npm 包名一致
- 对应 extensions/ 目录名使用 **snake_case**（下划线分隔）
- 脚本自动做 kebab-case → snake_case 转换

示例映射：

| repository-map.yml 键名 | extensions/ 目录名 |
|------------------------|-------------------|
| `dask-labextension` | `dask_labextension` |
| `jupyterlab-git` | `jupyterlab_git` |
| `jupyterlab_widgets` | `jupyterlab_widgets`（已是snake_case，不变） |

## semver 范围语法

`supported-versions` 使用 npm semver 范围语法（通过 Python `semantic_version.NpmSpec` 解析）：

| 范围表达式 | 含义 | 示例 |
|-----------|------|------|
| `>=4.3` | 大于等于4.3.0 | jupyterlab |
| `4.x` | 4.x.x 所有版本 | jupyterlab-tour |
| `8.x` | 8.x.x 所有版本 | jupyterlab_widgets |
| `7.x` | 7.x.x 所有版本 | notebook |
| `>=0.40.0` | 大于等于0.40.0 | jupyterlab-git |
| `>=0.6.4` | 大于等于0.6.4 | jupyter-resource-usage |
| `>=1.13.2 <2.0.0` | 1.x范围（≥1.13.2） | jupytext |
| `>=3.8.0 <3.9.2 \|\| >=3.9.3` | 排除有bug的版本 | jupyterlab-lsp |
| `>=6.0.0` | 大于等于6.0.0 | dask-labextension |

## 版本收集算法

`02_update_catalogs.py` 按以下逻辑确定需要合并的版本：

1. 调用 GitHub GraphQL API 获取最近 100 个 tag（按提交日期降序）
2. 使用 `packaging.version.parse()` 解析版本号
3. 过滤条件：
   - 非 dev 版本（`version.is_devrelease == False`）
   - 非 prerelease 版本（`version.is_prerelease == False`）
   - 版本号可被 semver 解析
4. 检查版本是否在 `supported-versions` 范围内
5. 对所有匹配版本 clone 并提取字符串，merge 到同一个 POT 文件
6. 最后提取 `current-version-tag` 版本，确保包含最新字符串

### 为什么合并多版本？

一个扩展在不同小版本间可能新增或修改字符串。合并多个版本的 POT 可以：
- 包含所有支持版本中出现过的字符串
- 避免因版本差异导致某些字符串缺失翻译
- 旧版本用户也能获得完整翻译

## current-version-tag 特殊处理

### JupyterLab 主版本过滤

对于 `jupyterlab` 包，版本检测时会按主版本号前缀过滤（如 `v4.`），避免检测到跨大版本的 tag（如 v3.x 的最后一个patch版本可能比v4.0.0更新）。

### 分支名支持

`current-version-tag` 可以是分支名（不推荐），此时：
- `supported-versions` 无效
- 仅从当前分支 HEAD 提取字符串
- 不与之前 POT merge

## 自动更新机制

`01_check_releases.py`（每日定时运行）：

1. 读取 repository-map.yml
2. 对每个包查询 GitHub 最新 tag
3. 发现新版本（非dev/prerelease且大于current-version-tag）时更新配置
4. 如果新版本不在 supported-versions 范围内，报错提醒维护者
5. 写回 repository-map.yml 并创建 PR

## 添加新扩展

在 repository-map.yml 中按字母顺序插入新条目：

```yaml
{new-extension}:
  current-version-tag: v{version}
  supported-versions: '{version-range}'
  url: https://github.com/{owner}/{repo}
```

PR 合并后：
1. update_pot.yml 触发 → 运行 02_update_catalogs.py
2. 02 脚本自动更新 crowdin.yml（添加文件映射）
3. 自动 clone 新仓库并提取 POT
4. 创建 POT 更新 PR
5. 合并后 Crowdin 同步，译者可开始翻译

## 配置与代码的一致性

`02_update_catalogs.py` 中的 `update_crowdin_config()` 函数会根据 repository-map.yml 自动重新生成 crowdin.yml 的 files 列表，确保两者始终同步。无需手动编辑 crowdin.yml。

## 相关概念

- [整体架构概览](01-architecture-overview.md)
- [Crowdin 翻译平台集成](04-crowdin-integration.md)
- [自动化脚本体系](07-automation-scripts.md)
- [添加新扩展指南](12-adding-extension.md)
