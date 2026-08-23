---
type: Reference
title: "Python 依赖信源"
description: "requirements.txt 列出了语言包仓库的 Python 依赖及其用途"
tags: [jupyterlab, language-pack, dependencies, python, requirements]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:22:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: requirements-source
    resource: https://github.com/jupyterlab/language-packs/blob/master/requirements.txt
    title: "requirements.txt"
---

# Python 依赖信源

## 源码路径

`external/libs/jupyter/language-packs/requirements.txt`

## 依赖清单

| 包名 | 最低版本 | 用途 |
|------|---------|------|
| `build` | - | Python 包构建工具（`python -m build`） |
| `copier` | >=9.2.0 | 项目模板生成/更新工具，用于创建和更新语言包 |
| `pydantic` | - | 数据验证库 |
| `crowdin-api-client` | - | Crowdin API 客户端，获取翻译贡献者信息 |
| `hatch` | >=1.5.0 | Python 包版本管理和构建工具 |
| `jupyterlab-translate` | >=1.3.1 | **核心工具**：提供翻译字符串提取、语言包创建 API |
| `packaging` | - | 版本号解析（`packaging.version.parse`） |
| `pip` | - | Python 包管理器 |
| `polib` | - | gettext PO/POT/MO 文件处理库 |
| `pyyaml` | - | YAML 文件读写（repository-map.yml、crowdin.yml） |
| `requests` | - | HTTP 客户端（GitHub GraphQL API 调用） |
| `semantic_version` | - | npm 风格 semver 范围解析（NpmSpec） |
| `twine` | - | PyPI 包上传和验证工具 |

## 系统依赖

除 Python 依赖外，还需要：

- **gettext**：系统级 gettext 工具（`sudo apt-get install gettext`）
- **Node.js**：运行 `gettext-extract` NPM 包
- **gettext-extract**：全局 NPM 包（`npm install gettext-extract -g`）

## 关键依赖详解

### jupyterlab-translate

核心依赖，提供两个主要 API：

1. `api.extract_language_pack(repo_dir, output_dir, package_name, merge)`：
   - 从 JupyterLab 扩展源码中提取可翻译字符串
   - 生成或更新 POT 文件
   - 支持多版本 merge（合并多个版本的字符串）

2. `api.create_new_language_pack(output_dir, locale, version=None)`：
   - 使用 Copier 模板创建新的语言包目录结构

3. `contributors.get_contributors_report(locale, crowdin_key)`：
   - 从 Crowdin API 获取指定语言的贡献者列表
   - 生成 CONTRIBUTORS.md 文件

### polib

Python 库，用于读写 PO/POT/MO 文件：
- `polib.pofile()`：读取/写入 PO 文件
- `polib.MOFile`：编译/读取 MO 文件
- 提供条目遍历、修改、保存 API

### semantic_version

用于解析 npm 风格的版本范围：
- `semantic_version.NpmSpec(range)`：解析如 `>=4.3`、`4.x`、`>=0.40.0` 的范围表达式
- `semantic_version.Version(version)`：解析语义化版本号
- 版本 `in` 范围判断：`semversion in range`
