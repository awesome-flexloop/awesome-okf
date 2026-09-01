---
type: Concept
title: IR 中间表示与 DocBundle
description: Papyri 中间表示（IR）的核心概念、DocBundle 目录结构与 Bundle 顶层节点
tags: [papyri, ir, docbundle, bundle, serialization]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: nodes-src
    resource: /references/ir-nodes-source.md
    title: Papyri IR 节点类型源码信源
---

## 什么是 IR

IR（Intermediate Representation，中间表示）是 Papyri 的核心数据结构。它是一个树形的文档 AST（抽象语法树），将 RST 格式的 docstring 解析为类型化的节点对象。IR 是 Python 生成端和 TypeScript 渲染端之间的稳定契约。

IR 的设计目标：

- **与渲染器无关**：同一份 IR 可以被渲染为 HTML、终端输出或任何其他格式
- **可序列化**：支持 JSON（人类可读）和 CBOR（紧凑二进制）两种格式
- **类型安全**：每个节点类型有明确的字段定义和 CBOR tag，序列化/反序列化有类型校验
- **可增量更新**：跨包引用通过 RefInfo 延迟解析，支持后续 relink

## DocBundle 目录结构

`papyri gen` 输出的 DocBundle 是一个目录，位于 `~/.papyri/data/<lib>_<ver>/`，采用 JSON 格式以便人类检查和调试：

```
<lib>_<ver>/
├── papyri.json        # Bundle 清单（BundleManifest JSON）
├── toc.json           # 目录树（TocTree 节点列表，可为空时不存在）
├── module/            # API 对象文档
│   └── <qa>.json      # 每个完全限定名一个 GeneratedDoc JSON 文件
├── docs/              # 叙述性文档页面（RST 文件转换而来）
│   └── <name>         # 无后缀，GeneratedDoc JSON
├── examples/          # 示例文档
│   └── <name>         # 无后缀，Section JSON
└── assets/            # 二进制资源（图片等），原样存储
    └── <name>
```

### papyri.json（BundleManifest）

Bundle 清单是 JSON 文件，包含元数据：

```json
{
  "module": "numpy",
  "version": "2.0.0",
  "summary": "NumPy is the fundamental package for array computing with Python.",
  "github_slug": "numpy/numpy",
  "tag": "v2.0.0",
  "logo": "assets/logo.png",
  "aliases": { "np": "numpy" },
  "extra": {}
}
```

对应 `BundleManifest` dataclass（bundle.py），字段：
- `module`（str）：模块名
- `version`（str）：版本号
- `summary`（str）：一句话摘要
- `github_slug`（str）：GitHub 仓库 slug
- `tag`（str）：Git 标签
- `logo`（str）：Logo 资源路径
- `aliases`（dict[str, str]）：别名映射
- `extra`（dict[str, str]）：额外元数据（未识别的标量键值）

## Bundle 顶层节点

Bundle 是 `.papyri` 制品中的顶层 Node，通过 `@register(4070)` 标记。它包含一个库的全部文档数据：

```python
@register(4070)
class Bundle(Node):
    pack_format_version: int      # 打包格式版本（当前为 1）
    ir_schema_version: int        # IR schema 版本（当前为 1）
    module: str                   # 模块名
    version: str                  # 版本号
    summary: str                  # 摘要
    github_slug: str              # GitHub slug
    tag: str                      # Git 标签
    logo: str                     # Logo 路径
    aliases: dict[str, str]       # 别名映射
    extra: dict[str, str]         # 额外元数据
    api: dict[str, GeneratedDoc]  # API 文档（QA → GeneratedDoc）
    narrative: dict[str, GeneratedDoc]  # 叙述文档（name → GeneratedDoc）
    examples: dict[str, Section]  # 示例文档（name → Section）
    assets: dict[str, bytes]      # 二进制资源
    toc: tuple[TocTree, ...]      # 目录树
```

字段在 CBOR 中按位置编码（`pack_format_version` 和 `ir_schema_version` 排在最前），便于前向兼容快速检查。

## .papyri 制品格式

`papyri pack` 将 DocBundle 目录打包为单个 `.papyri` 文件：

- **编码**：canonical CBOR（RFC 8949 §4.2 确定性编码，map key 排序）
- **压缩**：gzip，zero-mtime header（确保可重现构建）
- **确定性**：同一输入目录两次运行产生字节完全相同的输出
- **安全性**：`papyri unpack` 使用 `_safe_child()` 拒绝路径遍历

## 双格式序列化策略

Papyri 采用双格式序列化设计：

| 阶段 | 格式 | 特点 | 位置 |
|------|------|------|------|
| 开发/调试 | JSON | 人类可读、可文本编辑器检查 | `~/.papyri/data/` 目录 |
| 传输/存储 | CBOR + gzip | 紧凑、确定性编码、快速传输 | `.papyri` 文件、ingest blob store |

CBOR 编码从 pack 阶段开始：
- Bundle 目录（gen 输出）是 JSON——故意保持人类可读
- `.papyri` 制品（pack 输出）是 CBOR——gzip 压缩
- ingest/viewer 层只消费 CBOR，不写 JSON

## GeneratedDoc：每个对象的文档容器

GeneratedDoc 是每个 API 对象（模块/类/函数/方法）的文档容器，通过 `@register(4011)` 标记。

核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `_content` | dict[str, Section] | 各文档节内容（Parameters/Returns/Examples 等） |
| `_ordered_sections` | list[str] | 节的顺序（保证序列化后顺序不丢失） |
| `example_section_data` | Section | Examples 节数据 |
| `item_file` | str \| None | 源文件路径 |
| `item_line` | int \| None | 源文件行号 |
| `item_type` | str \| None | 对象类型（function/class/module 等） |
| `aliases` | tuple[str, ...] | 别名列表 |
| `see_also` | tuple[SeeAlsoItem, ...] | "See Also" 条目 |
| `signature` | SignatureNode \| None | 函数签名 |
| `references` | tuple[str, ...] \| None | 引用列表 |
| `arbitrary` | tuple[Section, ...] | 任意额外节 |
| `local_refs` | tuple[str, ...] | 本地引用列表 |

标准节顺序（`GeneratedDoc.sections`）：

```
Signature → Summary → Extended Summary → Parameters → Returns →
Yields → Receives → Raises → Warns → Other Parameters → Attributes →
Methods → See Also → Notes → Warnings → References → Examples
```

`_OrderedDictProxy` 类维护 `_content` 字典的插入顺序，解决普通 dict 序列化/反序列化时可能丢失顺序的问题。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [IR 节点类型体系](04-ir-node-types.md)
- [gen 管线](05-gen-pipeline.md)
- [pack 与 upload](08-pack-and-upload.md)
- [CLI 参考](13-cli-reference.md)
