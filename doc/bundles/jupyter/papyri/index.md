---
type: bundle
title: "Papyri"
description: "Papyri 是一个 Python 库文档生成工具，将 docstring 解析为可移植的中间表示（IR），通过三端架构（Python 生成 + TypeScript 摄取 + Astro 渲染）实现更好的文档浏览体验。本教程覆盖从入门到扩展开发的完整知识体系。"
tags: [papyri, documentation, docstring, ir, cbor, astro, typescript, python, jupyter]
bundle_name: "papyri"
version: "0.1"
language: zh-CN
license: CC-BY-4.0
generated: { by: "reference_agent/trae-soLO", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: official-repo
    title: "Papyri GitHub"
    uri: "https://github.com/carreau/papyri"
  - id: source-root
    resource: "../../../../external/libs/jupyter/papyri/papyri"
    title: "papyri/ 源码目录"
---

# Papyri

> 将 Python docstring 解析为可移植 IR，构建更好的文档浏览体验。

## 概述

Papyri 是一个文档生成工具，解决了 Python 生态中 docstring 文档的以下问题：

- ✅ **IR 中间表示**：将 RST docstring 解析为类型化的 AST 节点树，与渲染器无关
- ✅ **三端架构分离**：Python 生成（gen）、TypeScript 摄取（ingest）、Astro 渲染（viewer）各司其职
- ✅ **跨包交叉引用**：通过 RefInfo/LocalRef/CrossRef 和 relink pass 建立包间链接
- ✅ **确定性打包**：canonical CBOR + gzip zero-mtime，字节级可重现
- ✅ **交互式文档查看**：Astro SSR 渲染，支持搜索、后向引用、内联代码执行
- ✅ **可扩展指令系统**：通过 TOML 注册自定义 RST 指令处理器
- ✅ **NumPy/SciPy 支持**：内置 numpydoc 风格解析和 doctest 执行

## 快速开始

```bash
# 安装
pip install papyri

# 创建最小配置 my-lib.toml
cat > my-lib.toml << 'EOF'
[meta]
github_slug = 'your-org/your-lib'

[global]
module = 'your_lib'
EOF

# 生成 IR 文档
papyri gen my-lib.toml

# 打包
papyri gen my-lib.toml --pack

# 上传到本地 viewer（需先启动 viewer）
papyri gen my-lib.toml --upload
```

→ 更多详情见 [快速开始](concepts/01-getting-started.md)

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    Python 生成端 (gen)                   │
│  TOML 配置 → 模块遍历 → docstring 解析 → doctest 执行    │
│  → RST→IR (tree-sitter) → 类型推断 → DocBundle (JSON)    │
└──────────────────────┬──────────────────────────────────┘
                       │ papyri pack
                       ↓
              ┌─────────────────┐
              │  .papyri 制品    │
              │  CBOR + gzip    │
              │  确定性编码       │
              └────────┬────────┘
                       │ papyri upload (HTTP PUT)
                       ↓
┌─────────────────────────────────────────────────────────┐
│               TypeScript 摄取端 (ingest)                 │
│  CBOR 解码 → BlobStore (SHA256) → SQLite nodes 表        │
│  → relink pass（解析 to-resolve 引用）→ backrefs → FTS5  │
└──────────────────────┬──────────────────────────────────┘
                       │ Astro SSR
                       ↓
┌─────────────────────────────────────────────────────────┐
│                 Astro 渲染端 (viewer)                    │
│  页面路由 → IR→HTML 组件递归渲染 → 搜索 → 后向引用        │
│  → Debug 节点标记 → 管理员面板 → 认证                    │
└─────────────────────────────────────────────────────────┘
```

## 文档导航

### 📚 概念文档（按学习路径）

| 章节 | 内容 |
|------|------|
| [00 简介](concepts/00-introduction.md) | 是什么、为什么、核心特性、与 Sphinx 对比 |
| [01 快速开始](concepts/01-getting-started.md) | 安装、第一个 TOML、gen/pack/upload、viewer 预览 |
| [02 架构总览](concepts/02-architecture-overview.md) | 三端架构、数据流、目录布局 |
| [03 IR 与 DocBundle](concepts/03-ir-and-docbundle.md) | 中间表示概念、DocBundle 结构、Bundle Node、.papyri 格式 |
| [04 IR 节点类型体系](concepts/04-ir-node-types.md) | Node 基类、@register/@debug、50+ 节点类型分类 |
| [05 gen 管线](concepts/05-gen-pipeline.md) | 配置加载→API 遍历→解析→执行→组装→写入的8个阶段 |
| [06 限定名与交叉引用](concepts/06-qualified-names.md) | : 分隔符、RefInfo/LocalRef/CrossRef、Key 四元组 |
| [07 配置系统](concepts/07-config-system.md) | TOML 格式、[global]/[meta]/directives、环境变量 |
| [08 pack 与 upload](concepts/08-pack-and-upload.md) | 确定性打包、路径防护、HTTP 上传协议 |
| [09 GraphStore 与交叉链接](concepts/09-graphstore-and-crosslinks.md) | SQLite schema、BlobStore、relink、FTS5 搜索 |
| [10 RST 解析](concepts/10-rst-parsing.md) | tree-sitter-rst、GenVisitor、numpydoc 分节 |
| [11 指令处理器扩展](concepts/11-directive-handlers.md) | 内置处理器、自定义处理器编写、Admonition 映射 |
| [12 TypeScript 摄取与渲染器](concepts/12-ingest-and-viewer.md) | ingest 流程、Astro 路由、IR 组件、认证 |
| [13 CLI 命令参考](concepts/13-cli-reference.md) | 所有子命令的完整选项和示例 |

→ [完整概念索引](concepts/index.md)

### 🧪 可运行示例

| 示例 | 内容 |
|------|------|
| [01 基础 gen 工作流](examples/01-basic-gen.md) | 最小配置、gen 执行、输出检查、--only 调试 |
| [02 自定义 TOML 配置](examples/02-custom-config.md) | 子模块、排除项、指令注册、叙述文档、严格模式 |
| [03 Pack 与 Upload 工作流](examples/03-pack-and-upload.md) | 打包/解包、确定性验证、本地上传、CI 部署 |
| [04 自定义指令处理器](examples/04-custom-directive-handler.md) | drop/code_handler、Admonition、多节点返回 |

→ [完整示例索引](examples/index.md)

### 📖 源码信源

所有 API 描述均可溯源至源码信源文档：

→ [信源索引](references/index.md)

## 项目信息

| 属性 | 值 |
|------|---|
| 项目名 | `papyri` |
| Python 要求 | ≥ 3.13 |
| 构建系统 | flit_core |
| 核心依赖 | cbor2, ipython, jedi, matplotlib, numpydoc, pygments, rich, tomli_w, tree-sitter, py-tree-sitter-rst, typer |
| TypeScript 依赖 | astro, better-sqlite3, cbor-x |
| 源码 | `external/libs/jupyter/papyri/papyri/` |
| 教程版本 | 0.1 |

## 适用场景

- 需要比 Sphinx 更好的交互式文档浏览体验
- 科学计算库（NumPy/SciPy/Matplotlib 等）的 API 文档生成
- 跨包交叉引用的文档系统
- 需要将 docstring 转换为可移植 IR 的工具链
- 本地/离线文档查看器
