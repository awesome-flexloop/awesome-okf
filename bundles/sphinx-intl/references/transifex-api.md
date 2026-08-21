---
type: reference
title: "transifex.py Transifex 集成 API 参考"
description: "sphinx-intl Transifex 平台集成函数、资源命名规范和 CLI 检测机制的源码信源"
tags: [transifex, localization, tx-cli, api-reference]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: transifex-py
    resource: "sphinx_intl/transifex.py"
    title: "sphinx-intl Transifex integration module"
---

# transifex.py Transifex 集成 API 参考

本文件记录 `sphinx_intl/transifex.py` 中定义的 Transifex 平台集成功能。

## 模块级常量

```python
TRANSIFEX_CLI_MINIMUM_VERSION = (1, 2, 1)
```

要求的 Transifex CLI 最低版本（1.2.1）。

### IGNORED_RESOURCE_NAMES

```python
IGNORED_RESOURCE_NAMES = ("glossary", "settings")
```

Transifex 的保留资源名 slug，直接使用会导致 API 错误。sphinx-intl 通过追加下划线（`_`）来避免冲突。

### 配置模板

```python
TRANSIFEXRC_TEMPLATE = """\
[https://www.transifex.com]
rest_hostname = https://rest.api.transifex.com
token = %(transifex_token)s
"""

TXCONFIG_TEMPLATE = """\
[main]
host = https://www.transifex.com
"""
```

## 工具函数

### normalize_resource_name(name) -> str

将文件路径转换为 Transifex 合法的资源名称。

- **转换规则**:
  1. 路径分隔符（`\` 和 `/`）替换为 `--`
  2. 非 `-`、`_`、字母、数字的字符替换为 `_`
  3. 如果结果在 `IGNORED_RESOURCE_NAMES` 中，追加 `_` 直到不冲突
- **示例**:
  - `docs/index` → `docs--index`
  - `glossary` → `glossary_`
  - `chapter1.section2` → `chapter1_section2`

### check_transifex_cli_installed()

检测 Transifex CLI (`tx`) 是否已安装且版本满足要求。

- **检测流程**:
  1. 使用 `shutil.which("tx")` 检查命令是否存在
  2. 执行 `tx --version` 检查输出版本
  3. 验证输出以 `"TX Client"` 开头（排除旧版 transifex_client）
  4. 解析版本号，要求 ≥ 1.2.1
- **异常**: `click.BadParameter` — CLI 未安装、版本过旧或为旧版客户端时抛出
- **安装提示**: 给出 `curl -o- https://raw.githubusercontent.com/transifex/cli/master/install.sh | bash` 命令

## 命令函数

### create_transifexrc(transifex_token)

创建 `$HOME/.transifexrc` 配置文件。

- **参数**: `transifex_token` (str) — Transifex API token
- **行为**:
  1. 目标路径: `~/.transifexrc`
  2. 如果文件已存在，跳过并提示
  3. 写入 `TRANSIFEXRC_TEMPLATE` 内容
- **状态**: **已废弃**，推荐使用 `TX_TOKEN` 环境变量
- **异常**: `click.BadParameter` — token 为空时抛出

### create_txconfig()

创建 `./.tx/config` 配置文件。

- **行为**:
  1. 目标路径: `.tx/config`
  2. 如果 `.tx` 目录不存在则创建
  3. 如果文件已存在，跳过并提示
  4. 写入 `TXCONFIG_TEMPLATE`（仅包含 `[main]` 段）

### update_txconfig_resources(transifex_organization_name, transifex_project_name, locale_dir, pot_dir)

自动更新 `.tx/config` 的资源段，为每个 POT 文件调用 `tx add` 注册资源。

- **参数**:
  - `transifex_organization_name` (str): Transifex 组织名
  - `transifex_project_name` (str): Transifex 项目名
  - `locale_dir` (str): locale 目录路径
  - `pot_dir` (str): POT 文件目录路径
- **行为**:
  1. 调用 `check_transifex_cli_installed()` 验证环境
  2. 清理项目名: 空格→连字符，移除非 `-_` 和字母数字字符
  3. 遍历 `pot_dir/**/*.pot` 所有 POT 文件
  4. 使用 `click.progressbar` 显示进度
  5. 对每个 POT 文件:
     - 计算 resource_path（相对 pot_dir 的路径，去扩展名）
     - 调用 `normalize_resource_name()` 生成合法 slug
     - 加载 POT 文件，跳过空文件（`len(pot) == 0`）
     - 构建并执行 `tx add` 命令

**tx add 命令模板**:
```
tx add
  --organization <org_name>
  --project <project_name>
  --resource <resource_slug>
  --resource-name <resource_name>
  --file-filter "<locale_dir>/<lang>/LC_MESSAGES/<resource_path>.po"
  --type PO
  <pot_dir>/<resource_path>.pot
```
