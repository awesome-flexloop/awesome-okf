---
type: Concept
title: 架构总览
description: Papyri 三端架构（Python gen → TypeScript ingest → Astro viewer）的全局视图与数据流
tags: [papyri, architecture, pipeline, data-flow]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: viewer-src
    resource: /references/viewer-source.md
    title: Papyri TypeScript 摄取器与查看器源码信源
---

## 三端架构

Papyri 采用三端分离架构，以 IR（中间表示）作为各端之间的稳定契约边界：

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Python (gen)   │     │  TypeScript      │     │  Astro Viewer   │
│                 │     │  (ingest)        │     │                 │
│  papyri gen     │ ──→ │  papyri-ingest   │ ──→ │  Web Renderer   │
│  papyri pack    │     │  Graph Store     │     │  HTML Output    │
│  papyri upload  │     │  Blob Store      │     │  Search/XRef    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                      │                       │
        ▼                      ▼                       ▼
   DocBundle (JSON)     .papyri (CBOR+gz)       SQLite + CBOR Blobs
   ~/.papyri/data/      → HTTP PUT →           ~/.papyri/ingest/
                        /api/bundle
```

### 端一：Python IR 生成器（papyri/）

**职责**：遍历 Python 库的公开 API，解析 docstring，执行示例代码，生成结构化的 IR。

**核心模块**：

- `gen.py`——核心 IR 生成管线（gen_main 函数）
- `tree.py` + `ts.py`——RST 解析（基于 tree-sitter）与 IR 转换
- `nodes.py` + `node_base.py`——IR 节点类型系统与序列化
- `doc.py`——GeneratedDoc 每个 API 对象的文档容器
- `signature.py`——Python 函数签名解析
- `bundle.py` + `pack.py`——Bundle 组装与 CBOR 打包

**输入**：TOML 配置文件 + 已安装的 Python 库
**输出**：`~/.papyri/data/<lib>_<ver>/` 目录（JSON 格式的 DocBundle）

### 端二：TypeScript 摄取引擎（ingest/）

**职责**：接收上传的 DocBundle，解码 CBOR，写入 Blob Store 和 Graph DB，解析交叉引用，建立前向/后向链接。

**核心模块**：

- `ingest.ts`——Ingester 类，协调整个摄取过程
- `encoder.ts`——CBOR 编解码与 IR 节点类型
- `graph-db.ts`——GraphDb 接口 + SqliteGraphDb 实现
- `blob-store.ts`——BlobStore 接口 + FsBlobStore 实现
- `raw-store.ts`——RawStore（原始 .papyri.gz 归档）
- `visitor.ts`——IR 树遍历，收集前向引用
- `inventory.ts`——Intersphinx objects.inv 解析（链接到非 papyri 项目）

**输入**：HTTP PUT `/api/bundle`（.papyri 制品）
**输出**：SQLite 图数据库（`papyri.db`）+ CBOR blob 文件

### 端三：Astro Web 查看器（viewer/）

**职责**：从 SQLite 图和 CBOR blob 读取 IR，渲染为 HTML 页面，提供搜索、导航、跨包引用浏览。

**技术栈**：Astro + React islands + TypeScript，`@astrojs/node` 适配器（server output 模式）。

**核心模块**：

- `ir-reader.ts`——Blob → 类型化 IR 解码（IR 变更的减震器）
- `render-node.ts`——IR 节点 → HTML 字符串
- `graph.ts`——图查询（后向引用、前向引用）
- `xref.ts`——交叉引用解析
- `qualname-page.ts` / `doc-page.ts`——页面视图模型
- `search.ts`——全文搜索索引

## 数据流详解

### 1. IR 生成阶段（papyri gen）

```
TOML Config → 导入目标模块 → inspect 遍历 API
    → 提取 docstring → numpydoc 解析
    → tree-sitter RST 解析 → IR 节点树
    → 类型推断（可选）→ 示例执行（可选）
    → 交叉引用解析（尽力而为）
    → 写入 JSON DocBundle 目录
```

生成过程中的规范化步骤：

- Examples 节的类型推断 → 存储为 `(token, reference)` 对，使渲染器可以超链接 `np.array`
- "See Also" 解析为结构化列表
- 本地引用解析为完全限定名（如 `zeros_like` → `numpy.zeros_like`）
- 示例执行以捕获输出图片（部分实现）

### 2. 打包阶段（papyri pack）

```
JSON DocBundle 目录 → 读取 papyri.json + 所有 JSON 文件
    → 组装为 Bundle Node → canonical CBOR 编码
    → gzip 压缩（zero-mtime header）
    → 输出 .papyri 制品（确定性输出）
```

### 3. 摄取阶段（viewer POST /api/bundle）

```
.papyri 制品 → gzip 解压 → CBOR 解码为 Bundle
    → 存储原始归档到 RawStore
    → 遍历 IR 节点收集所有引用 → visitor
    → 写入 BlobStore（每个文档的 CBOR blob）
    → 写入 GraphStore（节点表 + 链接表）
    → 执行 relink 解析跨包引用
```

### 4. 渲染阶段（viewer HTTP 请求）

```
HTTP 请求 → Astro 路由匹配 → 限定名解析
    → 从 GraphStore 查询节点元数据
    → 从 BlobStore 读取 CBOR blob → ir-reader 解码
    → render-node 将 IR 树渲染为 HTML
    → 组装布局（导航、TOC、签名、反向引用）
    → 返回 HTML 响应
```

## 存储架构

Papyri 的存储分为三层：

| 层级 | 格式 | 位置 | 说明 |
|------|------|------|------|
| 开发期 Bundle 目录 | JSON | `~/.papyri/data/` | 人类可读，gen 直接输出，可检查调试 |
| 发布制品 | CBOR + gzip | `.papyri` 文件 | 单文件、确定性编码、适合传输 |
| 运行时存储 | SQLite + CBOR blobs | `~/.papyri/ingest/` | viewer 运行时使用，支持图查询 |

**权威来源**：Raw Store 中的 `_raw/<pkg>/<ver>.papyri.gz` 是唯一权威 IR。Graph Store 和 Blob Store 是派生缓存，可通过 `POST /api/reingest` 重建。

## IR 边界契约

Python 端（gen）和 TypeScript 端（ingest/viewer）之间的边界是**磁盘上的 IR**，保持稳定以使得任何渲染器（本地或托管）都可以消费它而不需要修改 Python 包。

IR 的核心设计原则：

- **节点类型带 CBOR tag**：每个节点类型通过 `@register(tag)` 分配唯一数字标签
- **字段位置编码**：CBOR 中字段按类定义顺序排列为数组（非 map），保证紧凑
- **canonical 编码**：map key 排序，确保确定性输出
- **debug 节点标记**：schema 变动中的节点使用 `@debug` 标记，不应被视为稳定输出

## 相关概念

- [Papyri 简介](00-introduction.md)
- [IR 与 DocBundle](03-ir-and-docbundle.md)
- [IR 节点类型体系](04-ir-node-types.md)
- [gen 管线](05-gen-pipeline.md)
- [TypeScript 摄取与渲染器](12-ingest-and-viewer.md)
