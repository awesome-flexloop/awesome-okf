---
type: Reference
title: cli.py 与辅助模块源码
description: conda-pack CLI 入口和辅助模块源码索引，包含 argparse 参数定义、MultiAppendAction、compat.py 兼容层、_progress.py 进度条。
tags: [conda-pack, source, cli, compat, progress]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T05:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T06:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: conda-pack-cli
    resource: conda_pack/cli.py
    title: conda-pack cli.py
  - id: conda-pack-compat
    resource: conda_pack/compat.py
    title: conda-pack compat.py
  - id: conda-pack-progress
    resource: conda_pack/_progress.py
    title: conda-pack _progress.py
---

# cli.py 与辅助模块源码

## cli.py（约183行）

CLI 入口模块，使用 argparse 定义命令行接口。

| 定义 | 行号 | 说明 |
|------|------|------|
| `MultiAppendAction` | L9-L18 | 自定义 argparse Action，支持多次 `--exclude`/`--include` 追加为 `(kind, pattern)` 元组列表 |
| `build_parser()` | L21-L132 | 构建 argparse 解析器，定义所有命令行参数 |
| `PARSER` | L136 | 模块级解析器实例（供 sphinxcontrib.autoprogram 使用） |
| `fail(msg)` | L139-L141 | 打印错误到 stderr 并 exit(1) |
| `main(args=None, pack=pack)` | L144-L179 | CLI 主函数，解析参数→调用 pack()→异常处理 |

### CLI 参数一览

| 参数 | 短选项 | 说明 |
|------|--------|------|
| `--name` | `-n` | 环境名称 |
| `--prefix` | `-p` | 环境路径 |
| `--output` | `-o` | 输出文件路径 |
| `--arcroot` | | 归档内根路径 |
| `--dest-prefix` | `-d` | 目标前缀（指定后不生成 conda-unpack） |
| `--parcel-root/name/version/distro` | | Cloudera Parcel 参数 |
| `--format` | | 归档格式（infer/zip/tar.gz/tar.bz2/tar.xz/tar.zst/tar/parcel/squashfs/no-archive） |
| `--compress-level` | | 压缩级别 0-9（zstd 支持到19） |
| `--n-threads` | `-j` | 压缩线程数（-1 表示所有核心） |
| `--zip-symlinks` | | zip 中存储符号链接 |
| `--no-zip-64` | | 禁用 ZIP64 扩展 |
| `--ignore-editable-packages` | | 跳过可编辑包检查 |
| `--ignore-missing-files` | | 跳过缺失文件检查 |
| `--exclude` | | 排除文件模式（可多次使用） |
| `--include` | | 包含文件模式（可多次使用） |
| `--force` | `-f` | 覆盖已有输出文件 |
| `--quiet` | `-q` | 静默模式 |
| `--help` | `-h` | 显示帮助 |
| `--version` | | 显示版本 |

### 入口点

```
[project.scripts]
conda-pack = "conda_pack.cli:main"
```

## compat.py（约45行）

跨平台兼容层。

| 定义 | 行号 | 说明 |
|------|------|------|
| `default_encoding` | L4 | 系统默认编码 |
| `on_win` | L5 | Windows 平台标志 |
| `on_mac` | L6 | macOS 平台标志 |
| `on_linux` | L7 | Linux 平台标志 |
| `is_32bit` | L8 | 32位系统检测 |
| `PY2` | L10 | Python 2 兼容标志 |
| `Queue` | L16/L25 | 跨版本 Queue 导入（PY2: Queue, PY3: queue.Queue） |
| `load_source(name, path)` | L14-L32 | 动态加载 Python 源文件 |
| `find_py_source(path, ignore)` | L35-L45 | 从 .pyc/.pyo 路径查找对应的 .py 源文件 |

## _progress.py（约99行）

简单的文本进度条组件。

| 定义 | 行号 | 说明 |
|------|------|------|
| `format_time(t)` | L7-L22 | 将秒数格式化为人类可读时间（s/min/hr） |
| `progressbar` | L25-L99 | 进度条类，支持上下文管理器协议 |

### progressbar 特性

- 使用后台线程（daemon=True）每 0.1 秒刷新一次
- 显示格式：`[########--------] | 50% Completed | 10.2s`
- 支持 `enabled` 参数开关进度报告
- 可自定义输出文件（默认 stdout）
- 上下文管理器退出时打印换行
