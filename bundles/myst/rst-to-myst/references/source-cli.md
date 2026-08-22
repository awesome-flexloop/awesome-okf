---
type: Reference
title: rst-to-myst CLI 命令行接口
description: cli.py 基于 click 实现 ast/tokens/stream/convert/directives/roles 子命令。
tags: [source-code, cli, click, rst-to-myst, command-line]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:55:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-cli
    resource: /spec/facts.md
    title: rst-to-myst 事实清单
---

## 模块概览

`rst_to_myst/cli.py` 是命令行接口实现（433行），基于 click 框架。

## 主命令

### `main()`

Click 命令组，是 CLI 入口点（通过 `rst2myst` 脚本调用）。支持 `-h/--help` 和 `--version`。

## 子命令

### `ast PATH_OR_STDIN`

解析 RST 文件并输出 docutils AST（抽象语法树）的文本表示。用于调试解析阶段问题。

### `tokens PATH_OR_STDIN`

解析 RST 文件并输出 Markdown-It tokens（YAML 格式）。用于调试 token 生成阶段问题。

### `stream PATH_OR_STDIN`

解析 RST 文件或标准输入（`-`），输出 MyST Markdown 文本。

### `convert PATHS...`

批量转换一个或多个文件/目录：
- 输出文件：同目录下同名 `.md` 文件
- `--dry-run/-d`：不写入文件，仅显示转换结果
- `--replace-files/-R`：转换成功后删除原始 `.rst` 文件
- `--stop-on-fail/-S`：遇到转换失败立即停止
- `--raise-on-warning/-W`：解析警告时抛出异常

### `directives list`

列出所有可用指令名称（空格分隔）。

### `directives show NAME`

显示指定指令的元数据（YAML 格式），包含参数数量、是否有内容、选项列表等。

### `roles list`

列出所有可用角色名称（空格分隔）。

### `roles show NAME`

显示指定角色的元数据。

## 全局选项

| 选项 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--config` | - | None | YAML 配置文件路径（eager加载） |
| `--language` | `-l` | `en` | 指令/角色名语言代码 |
| `--sphinx/--no-sphinx` | - | `True` | 是否加载 Sphinx |
| `--extensions` | `-e` | None | 逗号分隔的 Sphinx 扩展列表 |
| `--default-domain` | `-dd` | `py` | 默认 Sphinx 域 |
| `--default-role` | `-dr` | None | 默认角色（None则转字面量） |
| `--cite-prefix` | `-cp` | `cite` | 引用前缀 |
| `--consecutive-numbering` | - | `True` | 有序列表连续编号 |
| `--colon-fences` | - | `True` | 使用冒号围栏 |
| `--dollar-math` | - | `True` | 使用美元数学 |
| `--conversions` | `-c` | None | 指令转换映射 YAML 文件 |
| `--encoding` | - | `utf8` | 文件编码 |

## 配置文件

配置文件通过 `--config` 指定，YAML 格式，可设置任意 CLI 选项的默认值。配置通过 `ctx.default_map` 机制实现。

## 源码位置

- 文件路径：`rst_to_myst/cli.py`
- 代码行数：433行

## 相关概念

- [命令行工具详细用法](/concepts/01-cli-usage.md)
