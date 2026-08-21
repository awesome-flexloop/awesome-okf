---
type: reference
title: "commands.py CLI 入口 API 参考"
description: "sphinx-intl CLI 命令定义、选项、配置读取函数的源码信源"
tags: [cli, commands, click, api-reference]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: commands-py
    resource: "sphinx_intl/commands.py"
    title: "sphinx-intl CLI commands module"
---

# commands.py CLI 入口 API 参考

本文件记录 `sphinx_intl/commands.py` 中定义的 CLI 命令、选项和工具函数。

## 模块级常量

```python
ENVVAR_PREFIX = "SPHINXINTL"
```

环境变量前缀，所有命令行选项均可通过 `SPHINXINTL_<UPPER_LONG_NAME>` 格式的环境变量设置。

## 工具函数

### read_config(path, passed_tags)

读取并执行 Sphinx 的 `conf.py` 文件，返回配置命名空间字典。

- **参数**:
  - `path` (str): conf.py 文件路径
  - `passed_tags` (tuple): 通过 `-t` 选项传递的 tags
- **返回**: `dict` — 包含 conf.py 中所有配置项的命名空间
- **行为**:
  - 创建 `Tags()` 实例，添加 passed_tags
  - 将 `__file__` 和 `tags` 注入执行命名空间
  - 切换到 conf.py 所在目录执行文件
  - 执行完毕恢复原工作目录
- **异常**: `click.BadParameter` — 文件不存在时抛出

### get_lang_dirs(path)

获取指定路径下的语言目录列表。

- **参数**: `path` (str) — locale 目录路径
- **返回**: `tuple` — 语言目录名元组（包装在单元素元组中，如 `(('de', 'ja'),)`）
- **匹配规则**: `glob(path + "/[a-z]*")` 且排除以 `pot` 结尾的目录

## Click 参数类型

### LanguagesType(click.ParamType)

- `name = "languages"`
- `envvar_list_splitter = ","`
- `convert()`: 将逗号分隔的字符串拆分为 tuple

### TagsType(click.ParamType)

- `name = "tags"`
- `envvar_list_splitter = ","`
- `convert()`: 将逗号分隔的字符串拆分为 tuple

## CLI 选项定义

| 选项变量 | 短选项 | 长选项 | 环境变量 | 类型 | 默认值 | 说明 |
|---------|--------|--------|---------|------|--------|------|
| `option_locale_dir` | `-d` | `--locale-dir` | `SPHINXINTL_LOCALE_DIR` | Path | `locales` | locale 目录 |
| `option_pot_dir` | `-p` | `--pot-dir` | `SPHINXINTL_POT_DIR` | Path | locale_dir/pot | POT 文件目录 |
| `option_output_dir` | `-o` | `--output-dir` | `SPHINXINTL_OUTPUT_DIR` | Path | 同locale_dir | MO 输出目录 |
| `option_tag` | `-t` | `--tag` | `SPHINXINTL_TAG` | TAGS | 无 | 传递给 conf.py 的 tags |
| `option_language` | `-l` | `--language` | `SPHINXINTL_LANGUAGE` | LANGUAGES | 所有语言 | 目标语言 |
| `option_line_width` | `-w` | `--line-width` | `SPHINXINTL_LINE_WIDTH` | int | 76 | PO 文件最大行宽 |
| `option_jobs` | `-j` | `--jobs` | `SPHINXINTL_JOBS` | int | 0（全部CPU） | 并行进程数 |
| `option_no_obsolete` | — | `--no-obsolete` | `SPHINXINTL_NO_OBSOLETE` | flag | False | 移除过时消息 |
| `option_transifex_token` | — | `--transifex-token` | `SPHINXINTL_TRANSIFEX_TOKEN` | str | 必填（已废弃） | Transifex token |
| `option_transifex_organization_name` | — | `--transifex-organization-name` | `SPHINXINTL_TRANSIFEX_ORGANIZATION_NAME` | str | 必填 | Transifex 组织名 |
| `option_transifex_project_name` | — | `--transifex-project-name` | `SPHINXINTL_TRANSIFEX_PROJECT_NAME` | str | 必填 | Transifex 项目名 |

## CLI 命令组

### main(ctx, config, tag) — Click Group

根命令组，自动检测配置：

1. **config 自动检测**: 依次查找 `conf.py`、`source/conf.py`
2. **locale_dir 自动检测**: 从 conf.py 读取 `locale_dirs`，默认 `['locales']`
3. **pot_dir 自动检测**: 依次查找 `_build/gettext`、`build/gettext`、`_build/locale`、`build/locale`
4. **transifex_project_name 自动检测**: 从 `.tx/config` 正则解析 `[<project>.<resource>]`
5. **default_map**: 为子命令注入默认参数

### update 子命令

```python
@main.command()
@option_locale_dir
@option_pot_dir
@option_language
@option_line_width
@option_no_obsolete
@option_jobs
def update(locale_dir, pot_dir, language, line_width, no_obsolete, jobs):
```

从 POT 文件更新指定语言的 PO 文件。调用 `basic.update()`。

### build 子命令

```python
@main.command()
@option_locale_dir
@option_output_dir
@option_language
def build(locale_dir, output_dir, language):
```

将 PO 文件编译为 MO 文件。调用 `basic.build()`。

### stat 子命令

```python
@main.command()
@option_locale_dir
@option_language
def stat(locale_dir, language):
```

打印所有 PO 文件的翻译统计。调用 `basic.stat()`。

### create-transifexrc 子命令

```python
@main.command("create-transifexrc")
@option_transifex_token
def create_transifexrc(transifex_token):
```

创建 `$HOME/.transifexrc` 文件。**已废弃**，推荐使用 `TX_TOKEN` 环境变量。

### create-txconfig 子命令

```python
@main.command("create-txconfig")
def create_txconfig():
```

创建 `./.tx/config` 文件。

### update-txconfig-resources 子命令

```python
@main.command("update-txconfig-resources")
@option_transifex_organization_name
@option_transifex_project_name
@option_locale_dir
@option_pot_dir
def update_txconfig_resources(transifex_organization_name, transifex_project_name, locale_dir, pot_dir):
```

更新 `.tx/config` 的资源段，为每个 POT 文件调用 `tx add` 注册。
