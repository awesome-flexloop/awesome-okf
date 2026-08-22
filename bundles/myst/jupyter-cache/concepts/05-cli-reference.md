---
type: Concept
title: CLI 命令详解
description: jcache命令行工具的完整用法，包括缓存管理、Notebook管理和项目管理子命令
tags: [jupyter, cache, cli, command-line, jcache]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:44:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
  - id: jc-cli
    resource: /references/cli-commands.md
    title: CLI 命令参考
---

# CLI 命令详解

`jcache` 是 jupyter-cache 的命令行工具，基于 Click 框架构建。

## 全局用法

```bash
jcache [GLOBAL_OPTIONS] COMMAND [ARGS]...
```

### 全局选项

| 选项 | 说明 |
|------|------|
| `-p, --cache-path PATH` | 指定缓存目录路径，默认为 `./.jupyter_cache` |
| `-v, --verbose` | 启用详细输出 |
| `-V, --version` | 显示版本号 |
| `--help` | 显示帮助 |

### 指定缓存路径

```bash
# 使用默认路径 ./.jupyter_cache
jcache cache list

# 使用自定义路径
jcache -p /path/to/cache cache list
```

## 项目管理命令

### jcache project info

显示项目/缓存的基本信息：

```bash
jcache project info
```

输出包括：缓存路径、版本号、Notebook数量、缓存数量。

### jcache project clear

清空项目记录（保留已执行的缓存）：

```bash
jcache project clear
```

用于重新添加Notebook列表，但保留已有的执行缓存。

## Notebook 管理命令

### jcache notebook list

列出项目中的所有Notebook：

```bash
jcache notebook list
```

输出表格列：
- **ID**：Notebook主键
- **URI**：Notebook路径（自动缩短显示）
- **Reader**：读取器名称
- **Added**：添加时间
- **Status**：缓存状态（✅/❌/❗️/-）
- **Assets**：关联资源数量

### jcache notebook add

添加Notebook到项目：

```bash
# 添加单个文件
jcache notebook add notebook.ipynb

# 添加多个文件
jcache notebook add nb1.ipynb nb2.ipynb

# 使用glob（shell展开）
jcache notebook add notebooks/*.ipynb
```

### jcache notebook remove

从项目移除Notebook：

```bash
# 按ID移除
jcache notebook remove 1

# 按URI移除
jcache notebook remove notebooks/intro.ipynb

# 移除多个
jcache notebook remove 1 2 3
```

### jcache notebook execute

执行指定Notebook：

```bash
# 按ID执行
jcache notebook execute 1

# 执行多个
jcache notebook execute 1 2 3
```

如果Notebook已缓存（代码未变），直接从缓存返回结果。

### jcache notebook execute-all

执行项目中所有未缓存的Notebook：

```bash
jcache notebook execute-all
```

这是最常用的命令——它自动计算每个Notebook的内容hashkey，命中缓存则跳过，未命中则执行。

### jcache notebook match

显示项目Notebook与缓存的匹配状态：

```bash
jcache notebook match
```

## 缓存管理命令

### jcache cache list

列出所有缓存的执行结果：

```bash
jcache cache list
```

输出列：ID、Origin URI、Created、Accessed。

### jcache cache show

显示指定缓存记录的详细信息：

```bash
jcache cache show 1
```

输出包括：hashkey、数据字段、描述等。

### jcache cache add

手动添加已执行的Notebook到缓存：

```bash
jcache cache add executed_notebook.ipynb
```

### jcache cache remove

删除缓存记录及其文件：

```bash
jcache cache remove 1
```

删除NbCacheRecord和 `executed/{hashkey}/` 目录。

### jcache cache clear

清空所有缓存：

```bash
jcache cache clear
```

删除整个缓存目录并重建空数据库。

### jcache cache limit

查看或设置缓存上限：

```bash
# 查看当前限制
jcache cache limit

# 设置限制
jcache cache limit 500
```

超过限制时自动触发LRU淘汰。

## 状态符号说明

| 符号 | 含义 | 处理方式 |
|------|------|---------|
| `✅ [ID]` | 已缓存，括号内为缓存ID | 无需执行 |
| `❌` | 执行失败，有traceback | 修复后清除traceback重试 |
| `❗️ (unreadable)` | Notebook读取失败 | 检查文件格式和路径 |
| `-` | 未缓存/待执行 | 执行execute或execute-all |

## 典型CLI工作流

```bash
# 1. 初始化（可选，首次运行自动初始化）
jcache project info

# 2. 添加Notebook
jcache notebook add notebooks/*.ipynb

# 3. 查看状态
jcache notebook list

# 4. 执行所有（命中缓存的跳过）
jcache notebook execute-all

# 5. 修改Notebook后重新执行（仅执行修改的）
jcache notebook execute-all

# 6. 查看缓存
jcache cache list

# 7. 清理不需要的缓存
jcache cache remove 3
```

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [缓存架构设计](/concepts/02-architecture.md)
- [配置项参考](/concepts/07-configuration.md)
- [CLI命令参考](/references/cli-commands.md)
- [基本使用示例](/examples/basic-usage.md)
