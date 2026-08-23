---
type: Concept
title: CLI命令参考
description: jupyterlab-translate命令行工具的完整参考，包含7个子命令的参数、选项和使用场景
tags: [cli, commands, reference, click, extract, update, compile, contributors]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cli-source
    resource: /references/cli-source.md
    title: CLI源码映射
---

# CLI命令参考

jupyterlab-translate 提供两个入口命令：`jupyterlab-translate`（主命令）和 `gettext-extract`（TypeScript字符串提取子命令）。本节详细介绍主命令的所有子命令。

## 命令概览

```
jupyterlab-translate <command> [OPTIONS] ARGUMENTS
```

| 命令 | 用途 | 模式 |
|------|------|------|
| `extract` | 从扩展包提取字符串，生成POT模板 | 独立扩展包 |
| `update` | 创建或更新指定语言的PO翻译文件 | 独立扩展包 |
| `compile` | 编译PO文件为MO和JSON格式 | 独立扩展包 |
| `extract-pack` | 从扩展提取字符串到语言包仓库 | 集中语言包 |
| `update-pack` | 更新语言包仓库中的PO文件 | 集中语言包 |
| `compile-pack` | 编译语言包并移动到正确目录 | 集中语言包 |
| `update-contributors` | 从Crowdin更新贡献者列表 | 通用 |

## 全局参数

### 位置参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `PACKAGE_REPO_DIR` | 路径（必须存在） | 扩展包的源代码目录 |
| `LANGUAGE_PACKS_REPO_DIR` | 路径（必须存在） | 语言包仓库目录（仅_pack命令使用） |
| `PROJECT` | 字符串 | 项目名称（会被规范化：小写，`-`转`_`） |

### 选项

| 选项 | 缩写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--locales` | `-l` | 字符串列表（可多次指定） | None（自动发现） | 目标语言代码，如 `zh_CN`、`es_ES` |

## 独立扩展包命令

### extract

从JupyterLab扩展包提取可翻译字符串并创建POT模板。

```bash
jupyterlab-translate extract PACKAGE_REPO_DIR PROJECT
```

**示例：**
```bash
jupyterlab-translate extract ./my-jupyterlab-ext my_extension
```

**行为：**
1. 在 `PACKAGE_REPO_DIR/PROJECT/` 目录下创建 `locale/` 目录
2. 扫描Python、TypeScript、TSX源文件和JSON Schema文件
3. 生成 `locale/PROJECT.pot` 模板文件
4. 自动合并和去重字符串

**输出目录结构：**
```
<package_dir>/<project>/locale/<project>.pot
```

### update

创建或更新指定语言的PO翻译文件。

```bash
jupyterlab-translate update PACKAGE_REPO_DIR PROJECT [-l LOCALE]...
```

**示例：**
```bash
# 更新所有已存在的语言
jupyterlab-translate update ./my-ext my_extension

# 更新指定语言
jupyterlab-translate update ./my-ext my_extension -l zh_CN -l es_ES
```

**行为：**
1. 如果PO文件不存在，使用 `pybabel init` 创建新文件
2. 如果PO文件已存在，使用 `pybabel update` 合并新字符串
3. 更新PO文件头中的Project-Id-Version信息

**PO文件路径：**
```
<package_dir>/<project>/locale/<locale>/LC_MESSAGES/<project>.po
```

### compile

将PO文件编译为MO（二进制）和JSON（Jed格式）文件。

```bash
jupyterlab-translate compile PACKAGE_REPO_DIR PROJECT [-l LOCALE]...
```

**示例：**
```bash
jupyterlab-translate compile ./my-ext my_extension -l zh_CN
```

**行为：**
1. 对每个指定的locale，调用pybabel compile编译PO文件
2. 将PO转换为Jed JSON格式供前端使用
3. 使用polib将PO保存为MO二进制文件

**输出文件：**
- `<package_dir>/<project>/locale/<locale>/LC_MESSAGES/<project>.mo`
- `<package_dir>/<project>/locale/<locale>/LC_MESSAGES/<project>.json`

## 集中语言包命令

### extract-pack

从扩展包提取字符串到语言包仓库。

```bash
jupyterlab-translate extract-pack PACKAGE_REPO_DIR LANGUAGE_PACKS_REPO_DIR PROJECT
```

**示例：**
```bash
# JupyterLab核心
jupyterlab-translate extract-pack ./jupyterlab ./language-packs jupyterlab

# 第三方扩展
jupyterlab-translate extract-pack ./my-ext ./language-packs my_extension
```

**输出目录差异：**
- JupyterLab核心：`<language_packs_dir>/jupyterlab/locale/`
- 第三方扩展：`<language_packs_dir>/extensions/<project>/locale/`

### update-pack

更新语言包仓库中的PO翻译文件。

```bash
jupyterlab-translate update-pack PACKAGE_REPO_DIR LANGUAGE_PACKS_REPO_DIR PROJECT [-l LOCALE]...
```

输出目录为 `<language_packs_dir>/jupyterlab_extensions/<project>/locale/`（第三方扩展）或 `<language_packs_dir>/jupyterlab/locale/`（核心）。

### compile-pack

编译语言包仓库中的翻译文件并移动到最终位置。

```bash
jupyterlab-translate compile-pack LANGUAGE_PACKS_REPO_DIR PROJECT [-l LOCALE]...
```

**行为：**
1. 编译PO文件为MO和JSON
2. 将编译产物移动到语言包目录结构：
   `language-packs/jupyterlab-language-pack-<locale-dash>/jupyterlab_language_pack_<locale>/locale/<locale>/LC_MESSAGES/`
3. 如果目标语言包目录不存在，使用copier从cookiecutter模板创建

## 贡献者管理命令

### update-contributors

从Crowdin项目更新贡献者列表。

```bash
jupyterlab-translate update-contributors PACKAGE_REPO_DIR
```

**前置条件：** 需要设置 `CROWDIN_API_KEY` 环境变量。

**行为：**
1. 在包目录中查找 `jupyterlab_language_pack_??_??` 格式的Python包
2. 从包名提取locale代码
3. 调用Crowdin API下载贡献者报告
4. 格式化为Markdown并写入CONTRIBUTORS.md

## gettext-extract 命令

`gettext-extract` 是TypeScript字符串提取工具的直接入口，内部将参数转发给Node.js执行打包的gettext-extract脚本：

```bash
gettext-extract --config <config.json>
```

通常不需要直接调用此命令，它由 `extract_tsx_strings()` 函数内部使用。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [字符串提取流水线](/concepts/04-extraction-pipeline.md)
- [翻译目录管理](/concepts/05-catalog-management.md)
- [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
- [Crowdin贡献者集成](/concepts/10-contributors-crowdin.md)
- [双模式分发机制](/concepts/11-dual-mode-distribution.md)
- [CLI源码映射](/references/cli-source.md)
