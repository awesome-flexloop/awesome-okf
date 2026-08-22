---
type: Concept
title: 快速开始
description: Papyri 的安装方法、基本使用流程（gen → upload → viewer），以及验证安装的步骤
tags: [papyri, installation, quickstart, usage]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: cli-src
    resource: /references/cli-source.md
    title: Papyri CLI 命令源码信源
  - id: config-src
    resource: /references/config-source.md
    title: Papyri 配置系统源码信源
---

## 安装

Papyri 要求 Python **3.13+**，使用 `flit_core` 构建系统驱动。

### 开发安装（推荐）

项目近期没有在 PyPI 上重新发布版本，演进速度快于发布速度。从源码克隆安装：

```bash
git clone https://github.com/carreau/papyri
cd papyri
pip install -e .
```

RST 解析使用 `py-tree-sitter-rst`，基于 `tree-sitter >= 0.24`，两者均作为常规依赖自动安装。

### 从 PyPI 安装

```bash
pip install papyri
```

> [!WARNING]
> PyPI 上的版本为 0.0.8（2024年3月），早于当前架构。建议使用开发安装。

### 验证安装

```bash
papyri --help
```

### 运行测试

```bash
pip install -r requirements-dev.txt
python -m pytest
```

使用 `python -m pytest`（而非裸 `pytest`）以确保使用与可编辑安装相同的解释器。

## 基本使用流程

Papyri 有两个在不同上下文中运行的阶段：

1. **IR 生成**（`papyri gen`）——由库维护者在项目自己的环境（通常是 CI）中运行，在磁盘上生成自包含的 DocBundle。
2. **上传**（`papyri upload`）——将 DocBundle 推送到 viewer 实例，其 `/api/bundle` 端点在服务端运行 TypeScript 摄取管道，将 bundle 连接到交叉链接图中。

渲染由 `viewer/` Web 应用处理，它读取摄取后的图。

### 第一步：生成 IR

使用 examples/ 目录中的 TOML 配置文件：

```bash
papyri gen examples/numpy.toml
```

输出位于 `~/.papyri/data/<library>_<version>/`。

为单个对象生成文档：

```bash
papyri gen examples/numpy.toml --only numpy:einsum
```

> [!IMPORTANT]
> Papyri 使用**完全限定名**（`numpy:einsum`，而非 `numpy.einsum`）以避免模块/属性歧义。

完整 numpy/scipy 生成较慢，可使用 `--no-infer` 跳过示例的类型推断以加快速度。

### 第二步：上传到 Viewer

```bash
papyri upload ~/.papyri/data/<bundle-folder>
```

默认端点为 `http://localhost:4321/api/bundle`；通过 `--url` 覆盖。认证通过 `$PAPYRI_UPLOAD_TOKEN` 环境变量或 `--token` 选项。

### 第三步：本地查看

启动 viewer 开发服务器：

```bash
cd viewer
pnpm install --frozen-lockfile
pnpm dev
```

然后在浏览器中访问 `http://localhost:4321`。

## 常用选项速查

### gen 命令常用选项

| 选项 | 作用 |
|------|------|
| `--no-infer` | 跳过类型推断（加快生成速度） |
| `--exec/--no-exec` | 控制是否执行 docstring 代码示例 |
| `--only <qualname>` | 限制生成到指定限定名（可重复） |
| `--fail-early` | 遇到错误立即失败 |
| `--pack` | 生成后自动打包为 `.papyri` 制品 |
| `--upload` | 生成后自动上传 |

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PAPYRI_UPLOAD_URL` | `http://localhost:4321/api/bundle` | Viewer 上传端点 |
| `PAPYRI_UPLOAD_TOKEN` | （无） | 上传认证令牌 |

## 目录布局

安装和运行后，Papyri 在用户主目录下创建以下结构：

```
~/.papyri/
├── data/           # gen 输出的 DocBundle 目录（JSON 格式）
│   └── <lib>_<ver>/
│       ├── papyri.json    # Bundle 清单
│       ├── toc.json       # 目录树
│       ├── module/        # API 对象文档（每个 QA 一个 JSON）
│       ├── docs/          # 叙述文档
│       ├── examples/      # 示例文档
│       └── assets/        # 二进制资源
├── ingest/         # Viewer 摄取数据（SQLite + CBOR blobs）
│   ├── papyri.db   # 交叉引用图数据库
│   └── _raw/       # 原始 .papyri.gz 归档
└── config.toml     # 用户配置文件
```

## 常见问题

**SqlOperationalError**：DB schema 变更。执行 `rm -rf ~/.papyri/ingest/` 后重新上传 bundle 到新的 viewer 实例。

**ModuleNotFoundError: No module named 'tomli_w'**：pytest 使用了与 papyri 不同的 Python 解释器，使用 `python -m pytest`。

**tree-sitter 相关导入错误**：重新安装 `pip install -e .` 以拉取正确版本的 tree-sitter 依赖。

## 相关概念

- [Papyri 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [配置系统](07-config-system.md)
- [基本 gen 工作流示例](/examples/01-basic-gen-workflow.md)
