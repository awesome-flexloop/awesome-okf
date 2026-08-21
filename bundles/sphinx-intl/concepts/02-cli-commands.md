---
type: concept
title: "CLI 命令体系详解"
description: "sphinx-intl 的 Click CLI 架构、6 个子命令、选项体系、配置自动检测和环境变量机制"
tags: [cli, commands, click, options, configuration]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: commands-api
    resource: /references/commands-api.md
    title: "commands.py CLI 入口 API 参考"
---

# CLI 命令体系详解

sphinx-intl 使用 [Click](https://click.palletsprojects.com/) 框架构建命令行界面，采用**命令组（Group）+ 子命令（Command）**的结构。

## CLI 架构总览

```
sphinx-intl                          # 根命令组（main）
├── update                           # 更新/创建 PO 文件
├── build                            # 编译 PO 为 MO
├── stat                             # 翻译统计
├── create-transifexrc               # 创建 .transifexrc（已废弃）
├── create-txconfig                  # 创建 .tx/config
└── update-txconfig-resources        # 更新 .tx/config 资源段
```

入口点定义在 `pyproject.toml` 中：

```toml
[project.scripts]
sphinx-intl = "sphinx_intl.commands:main"
```

也可以通过 Python 模块方式运行：`python -m sphinx_intl`。

## 根命令组：main

`main` 函数使用 `@click.group()` 装饰，是整个 CLI 的入口。它负责**自动检测配置**并设置子命令的默认参数。

### 自动配置检测

main 函数在分发子命令前会执行以下自动检测逻辑：

**1. conf.py 自动查找** [F-018]

依次查找以下路径，找到第一个存在的作为配置文件：
- `./conf.py`
- `./source/conf.py`

也可以通过 `-c/--config` 选项显式指定：
```bash
sphinx-intl -c path/to/conf.py update -p _build/gettext -l ja
```

**2. locale_dir 自动检测** [F-019]

如果找到 conf.py：
- 读取并执行 conf.py，获取 `locale_dirs` 配置
- 默认值为 `['locales']`（Sphinx 的默认 locale 目录名）
- 取列表第一个目录，拼接为相对于 conf.py 的绝对路径

conf.py 的执行通过 `read_config()` 函数完成，该函数支持 `-t/--tag` 选项传递标签（与 `sphinx-build -t` 一致）。

**3. pot_dir 自动检测** [F-020]

依次查找以下目录，找到第一个存在的作为 POT 目录：
- `./_build/gettext`（Sphinx gettext 构建器的默认输出目录）
- `./build/gettext`
- `./_build/locale`
- `./build/locale`

**4. Transifex 项目名自动检测** [F-021]

如果存在 `.tx/config` 文件，从中用正则提取项目名：
```python
matched = re.search(r"\[(.*)\..*\]", open(target).read())
```
匹配 `[<project_name>.<resource_slug>]` 格式。

### 全局选项

| 选项 | 短选项 | 类型 | 说明 |
|------|--------|------|------|
| `--config` | `-c` | FILE | Sphinx conf.py 文件路径 |
| `--tag` | `-t` | TAGS | 传递标签给 conf.py（可多次使用） |

## 子命令详解

### update — 更新 PO 文件

```
sphinx-intl update [OPTIONS]
```

从 POT 文件创建新的 PO 文件或更新已有的 PO 文件 [F-022]。

**选项**:

| 选项 | 短选项 | 默认值 | 说明 |
|------|--------|--------|------|
| `--locale-dir` | `-d` | `locales` | locale 目录 |
| `--pot-dir` | `-p` | `<locale_dir>/pot` | POT 文件目录 |
| `--language` | `-l` | 所有语言目录 | 目标语言（可多次/逗号分隔）|
| `--line-width` | `-w` | `76` | PO 文件最大行宽（≤0 禁用换行）|
| `--no-obsolete` | — | `False` | 移除过时的 `#~` 消息 |
| `--jobs` | `-j` | `0`（全部CPU） | 并行进程数 |

**错误处理**:
- POT 目录不存在：抛出 `click.BadParameter`，提示使用 `-p` 指定
- 未指定语言且无语言目录：抛出 `click.BadParameter`，提示使用 `-l` 指定

**示例**:
```bash
# 更新日语和德语的 PO 文件
sphinx-intl update -p _build/gettext -l de -l ja

# 逗号分隔语言
sphinx-intl update -p _build/gettext -l de,ja

# 使用 4 个并行进程，移除过时消息
sphinx-intl update -p _build/gettext -l ja -j 4 --no-obsolete
```

### build — 编译 MO 文件

```
sphinx-intl build [OPTIONS]
```

将 PO 文件编译为 MO 二进制文件 [F-023]。

**选项**:

| 选项 | 短选项 | 默认值 | 说明 |
|------|--------|--------|------|
| `--locale-dir` | `-d` | `locales` | locale 目录 |
| `--output-dir` | `-o` | 同 locale-dir | MO 输出目录 |
| `--language` | `-l` | 所有语言目录 | 目标语言 |

**行为**:
- 遍历每个语言目录下的 `.po` 文件
- 如果 MO 文件已存在且 mtime 晚于 PO 文件则跳过（增量编译）
- 如果 output_dir 与 locale_dir 相同或未指定，MO 输出到同一目录

**示例**:
```bash
# 编译所有语言
sphinx-intl build

# 只编译日语
sphinx-intl build -l ja
```

### stat — 翻译统计

```
sphinx-intl stat [OPTIONS]
```

打印每个 PO 文件的翻译进度统计 [F-024]。

**选项**:

| 选项 | 短选项 | 默认值 | 说明 |
|------|--------|--------|------|
| `--locale-dir` | `-d` | `locales` | locale 目录 |
| `--language` | `-l` | 所有语言目录 | 目标语言 |

**输出格式**:
```
locale/ja/LC_MESSAGES/index.po: 42 translated, 3 fuzzy, 5 untranslated.
```

返回一个字典，结构为 `{po_file_path: {'translated': int, 'fuzzy': int, 'untranslated': int}}`。

### create-transifexrc — 创建认证配置（已废弃）

```
sphinx-intl create-transifexrc --transifex-token <TOKEN>
```

创建 `~/.transifexrc` 文件。**此命令已废弃**，推荐使用 `TX_TOKEN` 环境变量代替 [F-025]。

### create-txconfig — 创建 Transifex 配置

```
sphinx-intl create-txconfig
```

在当前目录创建 `.tx/config` 文件（仅包含 `[main]` 段）[F-026]。如果文件已存在则跳过。

### update-txconfig-resources — 更新资源配置

```
sphinx-intl update-txconfig-resources [OPTIONS]
```

扫描 POT 文件并自动更新 `.tx/config` 的资源段，为每个 POT 文件调用 `tx add` 命令注册资源 [F-027]。

**选项**:

| 选项 | 说明 |
|------|------|
| `--transifex-organization-name` | Transifex 组织名（必填） |
| `--transifex-project-name` | Transifex 项目名（必填） |
| `--locale-dir` | locale 目录 |
| `--pot-dir` | POT 目录（默认 `<locale_dir>/pot`） |

**前置条件**: 需要安装 Transifex CLI 且版本 ≥ 1.2.1。

## 自定义参数类型

sphinx-intl 定义了两个 Click 参数类型：

### LanguagesType

处理 `-l/--language` 选项的逗号分隔语言列表：

```python
class LanguagesType(click.ParamType):
    name = "languages"
    envvar_list_splitter = ","

    def convert(self, value, param, ctx):
        langs = value.split(",")
        return tuple(langs)
```

支持环境变量中的逗号分隔值自动拆分。

### TagsType

处理 `-t/--tag` 选项的标签列表，逻辑与 LanguagesType 相同。

## 环境变量机制

所有命令行选项都支持环境变量配置，规则为 [F-028]：

- 前缀：`SPHINXINTL_`
- 长选项名转为大写，短横线（`-`）替换为下划线（`_`）

| CLI 选项 | 环境变量 |
|---------|---------|
| `--locale-dir` | `SPHINXINTL_LOCALE_DIR` |
| `--pot-dir` | `SPHINXINTL_POT_DIR` |
| `--language` | `SPHINXINTL_LANGUAGE` |
| `--line-width` | `SPHINXINTL_LINE_WIDTH` |
| `--jobs` | `SPHINXINTL_JOBS` |
| `--transifex-token` | `SPHINXINTL_TRANSIFEX_TOKEN` |

环境变量通过 Click 的 `auto_envvar_prefix` 机制实现：

```python
main(auto_envvar_prefix=ENVVAR_PREFIX)  # ENVVAR_PREFIX = "SPHINXINTL"
```

## default_map 默认值注入

main 函数通过 Click 的 `ctx.default_map` 为子命令注入检测到的默认值 [F-029]：

```python
ctx.default_map = {
    "update": {"locale_dir": ..., "pot_dir": ...},
    "build": {"locale_dir": ...},
    "stat": {"locale_dir": ...},
    "update-txconfig-resources": {
        "locale_dir": ..., "pot_dir": ...,
        "transifex_project_name": ...
    },
}
```

这样用户不必每次都手动指定 `-d` 和 `-p` 选项，sphinx-intl 会自动从 conf.py 和文件系统推断合理的默认值。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [翻译工作流原理](03-translation-workflow.md)
- [更新机制：多进程合并与 Fuzzy](05-update-mechanism.md)
- [Transifex 平台集成](07-transifex-integration.md)
