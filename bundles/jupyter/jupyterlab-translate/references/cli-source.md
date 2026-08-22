---
type: Reference
title: CLI命令行接口源码映射
description: jupyterlab-translate CLI模块（cli.py）的命令、参数和源码位置映射
tags: [cli, click, command-line, entry-point]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cli-source
    resource: /references/cli-source.md
    title: cli.py 源码
---

# CLI命令行接口源码映射

本文档记录 `jupyterlab_translate/cli.py` 模块中定义的所有CLI命令、参数及其对应的API函数。

## 模块信息

- **源文件**：`jupyterlab_translate/cli.py`
- **框架**：Click
- **入口点**：`jupyterlab-translate = "jupyterlab_translate.cli:main"`（pyproject.toml）

## 全局参数

| 参数名 | 类型 | 定义位置 | 说明 |
|--------|------|---------|------|
| `package_repo_dir` | click.Path(exists=True, path_type=Path) | 第26-28行 | 包仓库目录路径 |
| `language_packs_repo_dir` | click.Path(exists=True) | 第23-25行 | 语言包仓库目录路径 |
| `project` | str | 第29行 | 项目名称 |
| `--locales` / `-l` | multiple=True, default=None | 第34-36行 | 目标语言列表 |

## 命令清单

### 独立扩展包命令

| 命令 | 参数 | 调用API | 源码行 |
|------|------|---------|--------|
| `extract` | package_repo_dir, project | `extract_package()` | 第53-61行 |
| `update` | package_repo_dir, project, --locales | `update_package()` | 第63-71行 |
| `compile` | package_repo_dir, project, --locales | `compile_package()` | 第105-111行 |
| `update-contributors` | package_repo_dir | `get_contributors_report()` | 第74-102行 |

### 集中语言包命令

| 命令 | 参数 | 调用API | 源码行 |
|------|------|---------|--------|
| `extract-pack` | package_repo_dir, language_packs_repo_dir, project | `extract_language_pack()` | 第116-126行 |
| `update-pack` | package_repo_dir, language_packs_repo_dir, project, --locales | `update_language_pack()` | 第129-140行 |
| `compile-pack` | language_packs_repo_dir, project, --locales | `compile_language_pack()` | 第143-150行 |

## 环境变量

| 变量名 | 使用位置 | 说明 |
|--------|---------|------|
| `CROWDIN_API_KEY` | 第80行, plugin.py第86行 | Crowdin API密钥，用于更新贡献者列表 |

## 相关概念

- [CLI命令参考](/concepts/03-cli-commands.md)
- [架构总览](/concepts/02-architecture-overview.md)
- [API层源码映射](/references/api-source.md)
