---
okf_version: "0.2"
type: reference
title: "配置迁移工具源码（migrate.py）"
description: "jupyter_core/migrate.py 中 IPython 3.x 到 Jupyter 4.x 配置迁移的完整逻辑与JupyterMigrate应用类"
tags: [migrate, config-migration, ipython, jupyter-migrate, upgrade, JupyterMigrate]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: migrate-py
    resource: "../../../../../external/libs/jupyter/jupyter_core/jupyter_core/migrate.py"
    title: "jupyter_core/migrate.py"
---

# 配置迁移工具源码（migrate.py）

本信源登记 `jupyter_core/migrate.py`（约282行）的所有函数与行为细节。migrate.py 提供 IPython <4.0 到 Jupyter 的配置迁移能力，将配置和资源从旧的 `~/.ipython/` 位置复制到新的 Jupyter 位置。

## 模块级常量

### migrations: dict[str, str]

目录级迁移映射表，键为源路径模板，值为目标路径模板：

| 源路径模板 | 目标路径模板 |
|-----------|------------|
| `{ipython_dir}/nbextensions` | `{jupyter_data}/nbextensions` |
| `{ipython_dir}/kernels` | `{jupyter_data}/kernels` |
| `{profile}/nbconfig` | `{jupyter_config}/nbconfig` |
| `{profile}/security/notebook_secret` | `{jupyter_data}/notebook_secret` |
| `{profile}/security/notebook_cookie_secret` | `{jupyter_data}/notebook_cookie_secret` |
| `{profile}/security/nbsignatures.db` | `{jupyter_data}/nbsignatures.db` |

其中 `{ipython_dir}` = IPython目录，`{jupyter_data}` = jupyter_data_dir()，`{profile}` = `{ipython_dir}/profile_default`，`{jupyter_config}` = jupyter_config_dir()。

### custom_src_t / custom_dst_t

custom.js/css 迁移路径模板：
- 源：`{profile}/static/custom`
- 目标：`{jupyter_config}/custom`

### config_migrations: list[str]

需要迁移的配置文件名列表（不含前缀和扩展名）：`["notebook", "nbconvert", "qtconsole"]`。对应的源文件为 `ipython_{name}_config.py/.json`，目标为 `jupyter_{name}_config.py/.json`。

### config_substitutions: dict[regex, str]

配置文件内容正则替换表，用于将旧的IPython类名替换为Jupyter类名：

| 正则 | 替换为 |
|------|--------|
| `\bIPythonQtConsoleApp\b` | `JupyterQtConsoleApp` |
| `\bIPythonWidget\b` | `JupyterWidget` |
| `\bRichIPythonWidget\b` | `RichJupyterWidget` |
| `\bIPython\.html\b` | `notebook` |
| `\bIPython\.nbconvert\b` | `nbconvert` |

[F-210]

## 公开函数

### get_ipython_dir() -> str

返回 IPython 用户目录路径。直接读取 `IPYTHONDIR` 环境变量，默认 `~/.ipython`。**不从 IPython 包导入**，避免触发 IPython 的目录创建逻辑。

### migrate_dir(src, dst) -> bool

迁移目录：
1. 源目录为空（`iterdir()` 无内容）→ debug 日志，返回 False
2. 目标目录已存在且非空 → debug 日志，返回 False
3. 目标目录存在但为空 → 删除空目录
4. 确保父目录存在，调用 `shutil.copytree(src, dst, symlinks=True)` 复制（保留符号链接）
5. 成功返回 True

### migrate_file(src, dst, substitutions=None) -> bool

迁移单个文件：
1. 目标文件已存在 → debug 日志，返回 False
2. 确保父目录存在，`shutil.copy(src, dst)` 复制
3. 若提供 `substitutions`（正则→替换字典），读取文件内容并执行所有替换后写回
4. 成功返回 True

### migrate_one(src, dst) -> bool

迁移单个项目（自动判断是文件还是目录）：
- `src` 是文件 → 调用 `migrate_file(src, dst)`（无替换）
- `src` 是目录 → 调用 `migrate_dir(src, dst)`
- 都不是 → debug 日志，返回 False

### migrate_static_custom(src, dst) -> bool

迁移 non-empty 的 custom.js 和 custom.css：
1. 检查 custom.js 是否为空（只有注释/空行）
2. 检查 custom_css 是否为空（仅包裹在 `/* ... */` 中）
3. 两者都为空 → 返回 False
4. 非空文件调用 `migrate_file()` 复制到目标目录
5. 任意文件迁移成功返回 True

### migrate_config(name, env) -> list[str]

迁移单个配置文件（.py 和 .json 两种格式）：
1. 源路径：`{profile}/ipython_{name}_config.{ext}`
2. 目标路径：`{jupyter_config}/jupyter_{name}_config.{ext}`
3. 使用 `PyFileConfigLoader`/`JSONFileConfigLoader` 加载源配置
4. 配置为空（无实际设置）→ 不迁移
5. 非空配置调用 `migrate_file(src, dst, substitutions=config_substitutions)` 复制并执行类名替换
6. 返回成功迁移的源文件路径列表

### migrate() -> bool

执行完整迁移流程，返回是否有文件被迁移：

1. 构建 `env` 字典（jupyter_data, jupyter_config, ipython_dir, profile 路径）
2. 遍历 `migrations` 字典：源路径存在则调用 `migrate_one()`
3. 遍历 `config_migrations` 列表：调用 `migrate_config(name, env)`
4. 若 custom 源目录存在，调用 `migrate_static_custom()`
5. 写入标记文件 `{jupyter_config}/migrated`，内容为当前 UTC ISO 时间戳
6. 任意步骤成功迁移则返回 True

> **注意**：`migrate()` 不做交互式确认、不检查 nbconvert、不迁移 kernelspec（kernels 通过目录映射迁移）。它是幂等的——已存在的目标文件不会被覆盖。

[F-211]

## JupyterMigrate 类

继承自 `JupyterApp`，是 `jupyter-migrate` 命令的入口应用：

| 属性 | 值 |
|------|-----|
| `name` | `"jupyter-migrate"` |
| `description` | 迁移说明文本（列出迁移内容） |

### start() -> None

调用 `migrate()` 执行迁移。若返回 False（无内容迁移），log.info 输出 "Found nothing to migrate."。

### main

模块级变量 `main = JupyterMigrate.launch_instance`，作为 CLI 入口点。

[F-212]

## 迁移内容总结

| 迁移类型 | 源位置 | 目标位置 |
|---------|--------|---------|
| 扩展 | `~/.ipython/nbextensions/` | `{data_dir}/nbextensions/` |
| 内核 | `~/.ipython/kernels/` | `{data_dir}/kernels/` |
| 前端配置 | `~/.ipython/profile_default/nbconfig/` | `{config_dir}/nbconfig/` |
| 安全文件 | `~/.ipython/profile_default/security/` | `{data_dir}/` |
| 自定义JS/CSS | `~/.ipython/profile_default/static/custom/` | `{config_dir}/custom/` |
| 配置文件 | `~/.ipython/profile_default/ipython_*_config.py/.json` | `{config_dir}/jupyter_*_config.py/.json` |

所有文件**复制而非移动**，源文件保留。目标已存在时跳过。迁移完成后写入 `migrated` 标记文件防止重复运行 [F-213]。
