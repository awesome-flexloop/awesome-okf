---
type: Concept
title: 插件配置与 CLI 选项
description: mdformat-footnote 的配置读取机制和 --keep-footnote-orphans 命令行选项。
tags: [configuration, cli, options, orphans, config]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:56:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-plugin
    resource: /references/source-plugin.md
    title: mdformat-footnote 插件核心实现
---

## 插件入口接口

mdformat-footnote 的入口模块 `mdformat_footnote/__init__.py` 导出三个名称：

```python
from .plugin import RENDERERS, add_cli_argument_group, update_mdit
```

这三个名称对应 mdformat 插件的标准接口：
- `update_mdit`：配置 markdown-it 解析器
- `RENDERERS`：token 渲染器映射
- `add_cli_argument_group`：添加自定义 CLI 参数

## CLI 参数添加

插件通过 `add_cli_argument_group(group)` 函数向 mdformat CLI 添加参数组。该函数接收一个 argparse `_ArgumentGroup` 对象，向其中添加自定义参数。

### --keep-footnote-orphans

这是目前唯一添加的 CLI 选项：

```python
group.add_argument(
    "--keep-footnote-orphans",
    action="store_const",
    const=True,
    dest="keep_orphans",
    help="Keep footnote definitions that are never referenced (default: remove them)",
)
```

参数特性：
- **类型**：布尔标志（flag）
- **使用方式**：`mdformat --keep-footnote-orphans document.md`
- **默认行为**：未指定此选项时，从未被引用的脚注定义（孤立脚注）会被自动删除
- **指定后**：保留所有脚注定义，即使它们在正文中从未被引用

### 什么是孤立脚注

孤立脚注（orphan footnote）指的是那些有定义但在正文中从未被 `[^label]` 引用过的脚注。例如：

```markdown
Some text[^1].

[^1]: 这个脚注被引用了，会保留。
[^2]: 这个脚注从未被引用，默认会被删除。
```

## 配置读取机制

配置选项通过 `_helpers.py` 中的 `get_conf` 函数读取。

### get_conf 函数

```python
def get_conf(options: ContextOptions, key: str) -> bool | str | int | None:
    if (api := options["mdformat"].get(key)) is not None:
        return api
    return options["mdformat"].get("plugin", {}).get(__plugin_name__, {}).get(key)
```

配置读取遵循两级优先级：

1. **API 直接配置**：`options["mdformat"][key]` — 通过 Python API 调用时传入的配置优先级最高
2. **插件配置**：`options["mdformat"]["plugin"]["footnote"][key]` — CLI 参数或配置文件中的设置

插件名称通过 `__plugin_name__ = "footnote"` 定义，在 `get_conf` 中用于定位插件配置命名空间。

### _keep_orphans 内部函数

`_keep_orphans(options)` 是 `plugin.py` 中的内部辅助函数，封装了 keep_orphans 配置的读取逻辑：

```python
def _keep_orphans(options: ContextOptions) -> bool:
    return bool(get_conf(options, "keep_orphans")) or False
```

如果配置中未设置 keep_orphans，默认返回 `False`（即删除孤立脚注）。

## 配置传递路径

CLI 参数值在 mdformat 内部存储在 `mdit.options["mdformat"]["plugin"]["footnote"]` 字典中，`update_mdit` 函数在配置 markdown-it 时通过 `_keep_orphans(mdit.options)` 读取此配置，并传递给重排序函数。

## 相关概念

- [脚注渲染格式与缩进规则](/concepts/02-footnote-rendering.md)
- [脚注排序逻辑与分类机制](/concepts/03-footnote-reordering.md)
