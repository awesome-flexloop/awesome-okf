---
type: Concept
title: conf.py 配置选项详解
description: sphinxarg_full_subcommand_name、索引构建与toctree配置、命令分组配置等conf.py选项完整说明
tags: [sphinx-argparse, conf.py, configuration, sphinxarg_full_subcommand_name, setup-config]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T22:43:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T22:43:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-argparse-source
    resource: /references/sphinx-argparse-source.md
---

# conf.py 配置选项详解

sphinx-argparse 提供多个 `conf.py` 配置项，用于控制扩展的全局行为。所有配置项都以 `sphinxarg_` 为前缀。

## 配置项总览

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `sphinxarg_full_subcommand_name` | bool | `False` | 子命令标题是否显示完整命令名 |
| `sphinxarg_build_commands_index` | bool | `False` | 是否生成简单命令索引 |
| `sphinxarg_commands_index_in_toctree` | bool | `False` | 命令索引是否加入 toctree |
| `sphinxarg_build_commands_by_group_index` | bool | `False` | 是否生成分组命令索引 |
| `sphinxarg_commands_by_group_index_in_toctree` | bool | `False` | 分组索引是否加入 toctree |
| `sphinxarg_commands_by_group_index_file_suffix` | str | `"by-group"` | 分组索引文件名后缀 |
| `sphinxarg_commands_by_group_index_title` | str | `"Commands by Group"` | 分组索引标题 |

## sphinxarg_full_subcommand_name

控制子命令标题是否显示完整命令路径。

**默认值**：`False`

**值为 False 时**：
- 子命令标题只显示子命令名（如 "install"、"build"）
- 页面中每个子命令的 section 标题简洁
- 适合单页文档化整个 CLI

**值为 True 时**：
- 子命令标题显示完整命令路径（如 "mytool install"、"mytool remote add"）
- 每个子命令独立成页时更清晰
- 配合 `:path:` 选项和多页面文档化使用最佳

**配置示例**：

```python
# conf.py
sphinxarg_full_subcommand_name = True
```

**内部实现**：在 `add_argparse_command()` 中，通过 `command_pos_args(parser_info, pos_args)` 递归遍历 parent 链构建完整命令名：

```python
if app.config.sphinxarg_full_subcommand_name:
    full_name = " ".join(command_pos_args(parser_info))
else:
    full_name = pos_args[0]
```

## 命令索引配置

### sphinxarg_build_commands_index

是否在 HTML 构建时生成简单命令索引页面。

**默认值**：`False`

```python
sphinxarg_build_commands_index = True
```

启用后生成 `commands-index.html` 页面，可通过 `:ref:`commands-index`` 引用。索引中所有命令按首字母分组排列。

### sphinxarg_commands_index_in_toctree

是否创建临时 RST 文件使命令索引可以加入 toctree。

**默认值**：`False`
**依赖**：`sphinxarg_build_commands_index = True`

```python
sphinxarg_build_commands_index = True
sphinxarg_commands_index_in_toctree = True
```

启用后会在源码目录创建 `commands-index.rst` 临时文件，使索引可以作为普通文档页面加入 toctree。构建完成后临时文件自动删除。

## 分组命令索引配置

### sphinxarg_build_commands_by_group_index

是否生成分组命令索引。

**默认值**：`False`

```python
sphinxarg_build_commands_by_group_index = True
```

启用后，使用 `:index-groups:` 选项标注的命令会按分组显示在索引中。

### sphinxarg_commands_by_group_index_in_toctree

是否将分组索引加入 toctree。

**默认值**：`False`

```python
sphinxarg_build_commands_by_group_index = True
sphinxarg_commands_by_group_index_in_toctree = True
```

### sphinxarg_commands_by_group_index_file_suffix

分组索引 HTML 文件名的后缀部分。

**默认值**：`"by-group"`

```python
# 生成 commands-by-service.html 而非 commands-by-group.html
sphinxarg_commands_by_group_index_file_suffix = "by-service"
```

修改后，引用标签也相应变为 `:ref:`commands-by-service``。

### sphinxarg_commands_by_group_index_title

分组索引页面的标题。

**默认值**：`"Commands by Group"`

```python
sphinxarg_commands_by_group_index_title = "按服务分类的命令参考"
```

## 扩展注册

在 `conf.py` 中添加扩展：

```python
extensions = [
    'sphinxarg.ext',
    # 其他扩展...
]
```

这会触发 `setup(app)` 函数，该函数：
1. 注册 `ArgParseDirective`（`.. argparse::` 指令）
2. 注册 `ArgParseDomain`（`commands` 域，含 `:command:` 角色）
3. 注册两个索引（CommandsIndex、CommandsByGroupIndex）
4. 添加所有配置项（`add_config_value`）
5. 连接 `builder-inited` 和 `build-finished` 事件处理器
6. 返回版本信息和并行构建安全标志

## 典型配置方案

### 方案一：单页文档化（简单项目）

```python
extensions = ['sphinxarg.ext']
# 不需要额外配置，所有默认值即可
```

适合单页文档化整个 CLI，所有子命令在一个页面中。

### 方案二：多页文档化（中等复杂度项目）

```python
extensions = ['sphinxarg.ext']
sphinxarg_full_subcommand_name = True
```

配合 `:path:` 选项将每个子命令拆分为独立页面，子命令标题显示完整路径。

### 方案三：带索引的多页文档化（复杂项目）

```python
extensions = ['sphinxarg.ext']
sphinxarg_full_subcommand_name = True
sphinxarg_build_commands_index = True
sphinxarg_commands_index_in_toctree = True
```

生成命令索引页面并加入导航。

### 方案四：分组索引（大型项目）

```python
extensions = ['sphinxarg.ext']
sphinxarg_full_subcommand_name = True
sphinxarg_build_commands_by_group_index = True
sphinxarg_commands_by_group_index_in_toctree = True
sphinxarg_commands_by_group_index_title = "命令分类索引"
```

在每个指令中使用 `:index-groups:` 标注分组，生成按功能分类的命令索引。

## 注意事项

1. **临时文件冲突**：启用 `in_toctree` 选项时，扩展会在源码目录创建临时 RST 文件。如果该目录下已存在同名文件（如 `commands-index.rst`），会抛出 `ExtensionError`，防止覆盖你的文档。
2. **配置生效时机**：所有配置项在 `setup()` 中注册默认值，在 `builder-inited` 事件中读取生效。修改配置后需要完全重新构建（`make clean && make html`）。
3. **索引只在 HTML 构建生成**：命令索引是 HTML 特定功能，man page/PDF 等其他构建器不会生成。

## 相关概念

- [Commands 域与交叉引用](09-domain-crossref.md)
- [命令索引生成](10-command-indices.md)
- [子命令与路径导航](05-nested-subcommands.md)
