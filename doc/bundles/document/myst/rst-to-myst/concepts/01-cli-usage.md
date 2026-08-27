---
type: Concept
title: 命令行工具详细用法
description: rst2myst CLI 的所有子命令、选项和配置文件用法详解。
tags: [cli, command-line, usage, options, convert, stream]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:57:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: src-cli
    resource: /references/source-cli.md
    title: rst-to-myst CLI 命令行接口
---

## CLI 总览

`rst2myst` 是基于 click 构建的命令行工具，采用多子命令结构：

```
rst2myst [OPTIONS] COMMAND [ARGS]...
```

使用 `rst2myst -h` 或 `rst2myst --help` 查看帮助。

## 子命令

### stream - 流式转换

从文件或标准输入读取 RST，输出 MyST Markdown 文本到标准输出。

```bash
rst2myst stream [OPTIONS] PATH_OR_STDIN
```

`PATH_OR_STDIN` 为文件路径或 `-`（表示标准输入）。

**常用场景**：
```bash
# 转换单个文件到 stdout
rst2myst stream index.rst

# 从管道读取
cat chapter.rst | rst2myst stream -

# 转换并保存到文件
rst2myst stream input.rst > output.md
```

### convert - 批量文件转换

转换一个或多个文件/目录，生成对应的 `.md` 文件。

```bash
rst2myst convert [OPTIONS] PATHS...
```

输出文件与源文件同目录，扩展名为 `.md`（如 `doc.rst` → `doc.md`）。

**特有选项**：

| 选项 | 缩写 | 说明 |
|------|------|------|
| `--dry-run` | `-d` | 试运行，不写入文件 |
| `--replace-files` | `-R` | 转换成功后删除原始 `.rst` 文件 |
| `--stop-on-fail` | `-S` | 遇到第一个转换失败时停止 |

**示例**：
```bash
# 预览转换结果（不写入文件）
rst2myst convert --dry-run docs/

# 转换并替换原文件
rst2myst convert --replace-files docs/*.rst

# 批量转换目录，遇错停止
rst2myst convert --stop-on-fail docs/
```

转换完成后，CLI 会输出所需的 MyST 扩展列表：
```
CONVERTED (extensions: ['colon_fence', 'deflist'])
FINISHED ALL! (extensions: ['colon_fence', 'deflist'])
```

### ast - 输出 docutils AST

解析 RST 并输出 docutils 抽象语法树的文本表示，用于调试解析阶段问题。

```bash
rst2myst ast [OPTIONS] PATH_OR_STDIN
```

**示例**：
```bash
rst2myst ast document.rst
```

输出格式为 docutils AST 的 `pformat()` 结果，以缩进形式展示节点树结构。

### tokens - 输出 Markdown-It Tokens

解析 RST 并输出 markdown-it tokens（YAML 格式），用于调试 token 生成阶段问题。

```bash
rst2myst tokens [OPTIONS] PATH_OR_STDIN
```

**示例**：
```bash
rst2myst tokens document.rst
```

每个 token 以 YAML 对象形式输出，包含 type、tag、nesting、content、children 等字段。

### directives 指令管理

```bash
# 列出所有可用指令名称
rst2myst directives list

# 显示特定指令的详细信息
rst2myst directives show image
```

`directives show` 输出的信息包括：指令名称、描述、Python类路径、必需/可选参数数量、是否有内容、选项列表。

### roles 角色管理

```bash
# 列出所有可用角色名称
rst2myst roles list

# 显示特定角色的详细信息
rst2myst roles show math
```

## 全局选项

| 选项 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--config FILE` | - | None | YAML 配置文件路径（提前加载） |
| `--language CODE` | `-l` | `en` | 指令/角色名语言代码 |
| `--sphinx/--no-sphinx` | - | `--sphinx` | 是否加载 Sphinx |
| `--extensions LIST` | `-e` | None | 逗号分隔的 Sphinx 扩展列表 |
| `--default-domain NAME` | `-dd` | `py` | 默认 Sphinx 域 |
| `--default-role NAME` | `-dr` | None | 默认角色（None则转为字面量） |
| `--cite-prefix PREFIX` | `-cp` | `cite` | 引用标签前缀 |
| `--consecutive-numbering/--no-consecutive-numbering` | - | 开启 | 有序列表连续编号 |
| `--colon-fences/--no-colon-fences` | - | 开启 | 对有内容的指令使用冒号围栏 |
| `--dollar-math/--no-dollar-math` | - | 开启 | 将数学转为美元定界格式 |
| `--conversions FILE` | `-c` | None | 指令转换映射 YAML 文件 |
| `--encoding ENC` | - | `utf8` | 文件读写编码 |
| `--raise-on-warning` | `-W` | 关闭 | 解析警告时抛出异常 |

### --sphinx/--no-sphinx

默认尝试加载 Sphinx。如果环境中未安装 Sphinx，使用 `--sphinx` 会报错。此时可：
1. 安装 Sphinx：`pip install "rst-to-myst[sphinx]"`
2. 或使用 `--no-sphinx` 禁用 Sphinx 加载

### --conversions 自定义指令映射

通过 YAML 文件指定自定义指令转换规则，格式为：

```yaml
# conversions.yml
mydirective: eval_rst
```

然后使用：
```bash
rst2myst convert --conversions conversions.yml docs/
```

## 配置文件

通过 `--config` 指定 YAML 配置文件，可以设置任何 CLI 选项的默认值：

```yaml
# config.yml
default_domain: py
sphinx: true
consecutive_numbering: true
colon_fences: true
dollar_math: true
```

使用方式：
```bash
rst2myst --config config.yml stream document.rst
```

配置文件是 eager 加载的（在其他选项解析前加载），可以被命令行参数覆盖。

## 相关概念

- [Python API 使用](02-python-api.md)
- [三阶段转换流水线架构](03-conversion-pipeline.md)
- [转换选项详解](10-configuration-options.md)
