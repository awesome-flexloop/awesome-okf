---
type: Concept
title: GraphStore 与交叉链接
description: Papyri 的 GraphStore SQLite 数据库——存储 IR 节点、建立交叉引用、后向引用和搜索索引
tags: [papyri, graphstore, sqlite, cross-reference, search, backreference]
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

## GraphStore 概述

GraphStore 是 Papyri viewer 端的图数据库，使用 SQLite 实现。它存储所有 bundle 的 IR 节点，建立交叉引用链接，支持全文搜索和导航查询。

Python 端的 `graph_store.py` 和 TypeScript 端的 `store.ts` 实现了相同的数据库 schema，但 TypeScript 端是生产使用的版本（viewer 端），Python 端主要用于测试和开发辅助。

## 数据库 Schema

### nodes 表

```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    cbor BLOB NOT NULL,
    package TEXT NOT NULL,
    version TEXT NOT NULL,
    category TEXT NOT NULL,
    identifier TEXT NOT NULL,
    last_scanned DATETIME,
    UNIQUE(package, version, category, identifier)
)
```

| 字段 | 说明 |
|------|------|
| `id` | 自增主键 |
| `cbor` | IR 节点的 CBOR 序列化字节（BlobStore 中的引用） |
| `package` | 包/模块名（对应 Key.module） |
| `version` | 版本号（对应 Key.version） |
| `category` | 文档类型（对应 Key.kind："api"/"docs"/"examples"） |
| `identifier` | 文档路径（对应 Key.path） |
| `last_scanned` | 上次交叉引用扫描时间 |

### backrefs 表（后向引用）

```sql
CREATE TABLE backrefs (
    source_id INTEGER,
    target_id INTEGER,
    ref_type TEXT,
    FOREIGN KEY(source_id) REFERENCES nodes(id),
    FOREIGN KEY(target_id) REFERENCES nodes(id)
)
CREATE INDEX backrefs_source_idx ON backrefs(source_id)
CREATE INDEX backrefs_target_idx ON backrefs(target_id)
```

`backrefs` 记录了文档间的引用关系：
- `source_id`：引用发起方节点
- `target_id`：被引用的目标节点
- `ref_type`：引用类型（"api"/"docs"/"examples"等）

这使得查看某个 API 时，可以反向查找"哪些文档引用了这个 API"。

### search FTS 表

```sql
CREATE VIRTUAL TABLE search USING fts5(
    package, version, category, identifier, content,
    content='',
    tokenize='unicode61'
)
```

使用 SQLite FTS5 全文搜索引擎，tokenizer 为 `unicode61`（支持 Unicode），内容直接存在虚拟表中（`content=''` 表示无外部内容表）。

## BlobStore：CBOR 存储

GraphStore 依赖 BlobStore（`blob_store.py`）存储和去重 CBOR 二进制 blob：

- **路径**：`~/.papyri/ingest/blobs/`（Python 端）或配置的 blob 目录（TypeScript 端）
- **键**：blob 内容的 SHA256 哈希
- **去重**：相同内容的 IR 节点共享同一个 blob 文件
- **文件命名**：`<sha256>.blob`
- **过期清理**：`gc()` 方法清理不再被任何节点引用的 blob 文件

## 摄取流程（ingest）

当 bundle 通过 upload 上传或 ingest 命令处理时：

1. **解码 Bundle**：CBOR 解码 Bundle 顶层节点
2. **Blob 存储**：将每个 GeneratedDoc/Section 的 CBOR blob 通过 BlobStore 存储
3. **插入 nodes**：为每个文档对象插入 nodes 表记录
4. **relink pass**：遍历所有 IR 节点，解析 CrossRef 中 kind="to-resolve" 的引用：
   - 在已摄取的所有包中查找匹配目标
   - 找到 → 更新 RefInfo 的 module/version/kind/path
   - 找不到 → kind 设为 "missing"
5. **建立 backrefs**：扫描所有解析后的 CrossRef，在 backrefs 表中插入引用关系
6. **全文索引**：提取文档文本内容，插入 search FTS 表
7. **记录版本**：更新 versions 表（TypeScript 端），标记当前默认版本

## 查询 API

### Python 端（graph_store.py）

GraphStore 类提供以下核心方法：

| 方法 | 说明 |
|------|------|
| `put(key, ir_node)` | 存储一个 IR 节点 |
| `get(key)` | 根据 Key 获取 IR 节点 |
| `get_backref(pkg, version, qa, k=None)` | 获取某文档的后向引用 |
| `get_refs(key, k=None)` | 获取某文档的前向引用（它引用了谁） |
| `search(query, limit=10)` | 全文搜索 |
| `list_packages()` | 列出所有已摄取的包 |
| `list_versions(package)` | 列出某包的所有版本 |
| `delete_version(package, version)` | 删除某个版本（级联清理 backrefs 和 blobs） |
| `relink()` | 执行交叉引用解析 pass |
| `gc()` | 垃圾回收未引用的 blob |

### TypeScript 端（store.ts）

`Store` 类提供类似的 API，配合 Astro 路由使用。主要查询方法：

- `getPage(package, version, category, identifier)`：获取页面 IR 数据
- `getBackrefs(package, version, identifier, category)`：获取后向引用
- `search(query, limit)`：全文搜索
- `listPackages()`/`getPackageVersions(package)`：列出包/版本
- `getDefaultVersion(package)`：获取包的默认版本

## Key 寻址

在 GraphStore 中，每个文档通过四元组 Key 唯一标识：

```typescript
// TypeScript
interface Key {
  module: string;
  version: string;
  kind: string;
  path: string;
}
```

这对应 SQLite 的 `(package, version, category, identifier)` UNIQUE 约束。

## 相关概念

- [限定名与交叉引用](06-qualified-names.md)
- [TypeScript 摄取与渲染器](12-ingest-and-viewer.md)
- [pack 与 upload](08-pack-and-upload.md)
