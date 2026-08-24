---
type: concepts
title: "Papyri 概念文档索引"
description: "Papyri 核心概念文档，按学习路径从入门到深入覆盖 IR、DocBundle、gen 管线、GraphStore、RST 解析、TypeScript viewer 等"
tags: [concepts, index, learning-path, papyri, ir, docbundle]
generated: { by: "reference_agent/trae-soLO", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: overview
    resource: "/concepts/00-introduction.md"
    title: "Papyri 简介"
---

# 概念文档索引

Papyri 概念文档按推荐阅读顺序排列。建议从 00 开始，依次阅读。

## 学习路径

### 入门（00-02）

| 编号 | 文档 | 主题 | 前置知识 |
|------|------|------|---------|
| 00 | [Papyri 简介](00-introduction.md) | 是什么、解决什么问题、核心特性、与 Sphinx 对比 | 无 |
| 01 | [快速开始](01-getting-started.md) | 安装、第一个 TOML、gen/pack/upload、viewer 预览 | Python 基础 |
| 02 | [架构总览](02-architecture-overview.md) | 三端架构（Python gen/TS ingest/Astro viewer）、数据流 | 00-01 |

### IR 与核心数据模型（03-04）

| 编号 | 文档 | 主题 | 前置知识 |
|------|------|------|---------|
| 03 | [IR 中间表示与 DocBundle](03-ir-and-docbundle.md) | IR 概念、DocBundle 目录结构、Bundle Node、.papyri 格式、GeneratedDoc | 02, CBOR 基础 |
| 04 | [IR 节点类型体系](04-ir-node-types.md) | Node 基类、@register/@debug、TAG_MAP、Encoder、节点分类（结构/引用/行内/块级） | 03 |

### 生成管线（05-08）

| 编号 | 文档 | 主题 | 前置知识 |
|------|------|------|---------|
| 05 | [gen 管线与 IR 生成](05-gen-pipeline.md) | 配置加载→API 遍历→docstring 解析→doctest 执行→类型推断→交叉引用→写入磁盘 | 03-04 |
| 06 | [限定名与交叉引用](06-qualified-names.md) | : 分隔符、RefInfo/LocalRef/CrossRef、引用解析流程、Key 四元组 | 04-05 |
| 07 | [配置系统](07-config-system.md) | 文件路径常量、TOML 配置格式、[global]/[meta]/[global.directives]、环境变量 | 05 |
| 08 | [pack 与 upload](08-pack-and-upload.md) | 打包流程、确定性保证、路径遍历防护、HTTP PUT 上传协议 | 03, 05 |

### 存储与链接（09）

| 编号 | 文档 | 主题 | 前置知识 |
|------|------|------|---------|
| 09 | [GraphStore 与交叉链接](09-graphstore-and-crosslinks.md) | SQLite schema、BlobStore、ingest 流程、relink pass、backrefs、FTS5 搜索 | 06, 08 |

### 解析与扩展（10-11）

| 编号 | 文档 | 主题 | 前置知识 |
|------|------|------|---------|
| 10 | [RST 解析与 IR 转换](10-rst-parsing.md) | tree-sitter-rst、GenVisitor、numpydoc 分节、指令/角色处理、代码执行 | 04-05 |
| 11 | [指令处理器扩展](11-directive-handlers.md) | 内置处理器（drop/code_handler）、自定义处理器注册、签名与返回值 | 07, 10 |

### Viewer 与 CLI（12-13）

| 编号 | 文档 | 主题 | 前置知识 |
|------|------|------|---------|
| 12 | [TypeScript 摄取与渲染器](12-ingest-and-viewer.md) | ingest 流程、relink pass、Astro 路由、IR 渲染组件、认证、开发模式 | 09 |
| 13 | [CLI 命令参考](13-cli-reference.md) | gen/pack/unpack/upload/ingest/take/xref/render/bootstrap 完整选项参考 | 01 |

## 概念依赖图

```
00 简介 ──→ 01 快速上手
    │
    └─→ 02 架构总览
         │
         ├─→ 03 IR & DocBundle ──→ 04 IR 节点类型
         │         │                    │
         │         └──────────┬─────────┘
         │                    ↓
         └───────────────→ 05 gen 管线 ──→ 06 限定名 & 交叉引用
                              │                │
                              ├─→ 07 配置系统   │
                              │                ↓
                              ├─→ 08 pack/upload ─→ 09 GraphStore
                              │                     │
                              ├─→ 10 RST 解析 ──────┘
                              │    │
                              │    └─→ 11 指令处理器
                              │
                              └─→ 12 TypeScript Viewer
                                   │
                                   └─→ 13 CLI 参考
```

## 阅读建议

- **初学者**：按顺序阅读 00→01→02→03→05→07→13，配合 [examples/](../examples/01-basic-gen.md) 动手实践
- **文档生成**：重点阅读 05→07→10→11，掌握 gen 管线和自定义扩展
- **部署运维**：重点阅读 08→09→12，理解打包、上传、GraphStore 和 viewer
- **架构理解**：阅读 02→03→04→06→09 后结合 [references/](../references/index.md) 源码信源深入
- **扩展开发**：阅读 10→11，配合 [examples/04](../examples/04-custom-directive-handler.md) 编写处理器

## 导航

- [教程首页](../index.md)
- [源码信源索引](../references/index.md)
- [示例文档索引](../examples/index.md)

```{toctree}
:hidden:

00-introduction
01-getting-started
02-architecture-overview
03-ir-and-docbundle
04-ir-node-types
05-gen-pipeline
06-qualified-names
07-config-system
08-pack-and-upload
09-graphstore-and-crosslinks
10-rst-parsing
11-directive-handlers
12-ingest-and-viewer
13-cli-reference
```
