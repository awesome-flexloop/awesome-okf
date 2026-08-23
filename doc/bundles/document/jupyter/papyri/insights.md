---
type: Insights
okf_version: "0.2"
title: "papyri 架构洞察"
generated: "2026-08-22"
tags: [jupyter,documentation,papyri,help-system]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/papyri/CLAUDE.md
  - ../../../../../external/libs/jupyter/papyri/papyri/bundle.py
  - ../../../../../external/libs/jupyter/papyri/papyri/pack.py
  - ../../../../../external/libs/jupyter/papyri/papyri/node_base.py
  - ../../../../../external/libs/jupyter/papyri/ingest/src/ingest.ts
  - ../../../../../external/libs/jupyter/papyri/viewer/src/lib/xref.ts
---

# papyri 架构洞察

## I-001：IR 作为契约的生成-打包-摄取-渲染四阶段分离管道

**类型**：架构模式  
**关联事实**：F-003, F-008, F-019, F-025, F-027, F-029, F-043, F-054, F-058, F-060, F-070

**洞察**：papyri 的核心架构决策是将文档系统拆分为四个独立阶段，各阶段通过一个精确定义的中间表示（IR）契约连接，彻底解决了 Sphinx "构建与渲染耦合"的根本问题。

Sphinx 的痛点是：解析 docstring 和渲染 HTML 在同一步骤完成，更新模板（如 accessibility 改进）必须从源码重新构建所有项目。papyri 通过四阶段管道解耦：

| 阶段 | 执行者 | 语言 | 输入 | 输出 | 职责 |
|------|--------|------|------|------|------|
| **gen** | 库维护者（CI） | Python | 源码 + TOML 配置 | ~/.papyri/data/ JSON bundle 目录 | 内省对象、解析 docstring（tree-sitter RST + numpydoc）、执行 doctest、提取签名 → 生成 IR |
| **pack** | 库维护者 | Python | JSON bundle 目录 | `.papyri` 文件（确定性 gzip+CBOR） | 序列化为紧凑二进制格式，保证字节确定性 |
| **ingest** |  viewer 服务端 | TypeScript | `.papyri` 文件 | BlobStore（CBOR blobs）+ GraphDb（SQLite 交叉引用图） | 解码 Bundle、写入 blob 存储、构建交叉引用链接图、计算内容摘要 |
| **render** | viewer（用户访问时） | TypeScript (Astro) | BlobStore + GraphDb 查询 | HTML 页面 | 读取 IR 节点、解析 CrossRef、渲染为 HTML、Shiki 高亮 + KaTeX 数学 |

**关键设计**：
- **JSON ↔ CBOR 双格式**（F-058）：bundle 目录使用 JSON（人类可读、可调试、`papyri debug` 检查），.papyri 制品使用 CBOR（紧凑、确定性编码、传输格式）。CBOR 从 pack 阶段开始，viewer/ingest 层不接受 JSON，明确分隔了"开发调试"和"生产传输"的边界。
- **确定性打包**（F-029）：同一 bundle 目录两次 pack 产生字节相同的输出（RFC 8949 §4.2 确定性 CBOR + gzip zero-mtime），这使得内容寻址、签名、镜像成为可能。
- **语言职责分离**（F-060, F-070）：Python 只做 IR 生成和 CLI（利用 inspect/IPython/jedi 等 Python 生态优势），TypeScript 做服务端摄取和前端渲染（利用 Astro/Node.js 生态），两端通过 CBOR（cbor2 Python ↔ cbor-x TypeScript）交换数据。禁止在 Python 端添加渲染逻辑，也禁止在 TypeScript 端添加 IR 生成逻辑。
- **IR 减震器模式**（F-063）：`ir-reader.ts` 是唯一的 IR 解码入口，IR 格式变更时修复集中在此一处，不扩散到组件层。这是防腐层（Anti-Corruption Layer）模式在数据格式层面的应用。

```
库维护者环境                          Viewer 服务端
┌─────────────┐    ┌─────────┐     ┌──────────┐    ┌──────────┐
│ papyri gen  │───→│ papyri  │────→│ ingest   │───→│ render   │
│ (Python)    │    │ pack    │ PUT │ (TS)     │    │ (Astro)  │
│ 源码→JSON IR│    │ JSON→   │/api/│ CBOR→    │    │ IR→HTML  │
│             │    │ .papyri │bundle│ Blob+Graph│    │          │
└─────────────┘    └─────────┘     └──────────┘    └──────────┘
   生成阶段          打包阶段        摄取阶段         渲染阶段
   ← 可以独立更新各阶段，不影响其他阶段 →
```

**复用价值**：此模式适用于任何需要将"数据生产"和"数据呈现"解耦的文档/内容系统。核心原则是：定义一个版本化、确定性、可序列化的 IR 契约，将生产和消费分离到不同进程/语言/时间点，通过确定性编码实现内容寻址和可验证构建。

---

## I-002：Blob + Graph 双层存储与两阶段交叉引用解析

**类型**：存储/查询模式  
**关联事实**：F-015, F-037, F-039, F-042, F-049, F-052, F-059, F-065, F-066

**洞察**：papyri 采用"文件系统 Blob 存储内容 + SQLite 图数据库存储关系"的双层存储架构，并通过两阶段 CrossRef 解析模式解决了跨包文档链接和服务端渲染的性能问题。

**双层存储的职责划分**：

- **BlobStore（文件系统）**：以 4 元组 (package, version, category, identifier) 为键存储 CBOR 编码的 IR 节点内容（GeneratedDoc/Section 等）。文件系统是内容的可信源（source of truth）（F-042）。
- **GraphDb（SQLite）**：存储 nodes 表（哪些文档存在 + 内容摘要 BLAKE2b-16）和 links 表（文档间的 forward/backward 引用关系）。SQLite 是图结构的可信源。通过 WAL 模式、64MB cache、256mmap 优化读性能（F-038）。
- **RawStore**：存储原始 `.papyri.gz` 归档，是唯一权威 IR——graphstore 完全可从 raw archive 通过 reingest 重建（F-059），这形成了简单的灾备策略：保留原始制品即可重建所有索引。

**内容摘要的易变字段剥离**（F-049）：计算 BLAKE2b 内容摘要时，自动剥离跨构建不稳定的字段：`item_line`/`item_file`（源码绝对路径和行号因环境不同而变化）、Figure 的 value（matplotlib 输出非确定性）、Image 的 url。这确保了"同一内容重建"产生相同摘要，不会因无关变动导致版本差异误判。

**两阶段 CrossRef 解析**解决了异步图查询与同步模板渲染的矛盾（F-052）：

1. **收集阶段**（async）：页面渲染前，递归遍历 IR 树，收集所有 CrossRef 节点的 ref-tuple，一次性批量查询 GraphDb，构建 `ref-tuple → {url, label}` 的 Map；
2. **渲染阶段**（sync）：将 Map 封装为同步闭包 `XRefResolver`，传入 Astro/React 组件，模板深层循环中调用闭包即可获得解析结果，无需 await。

CrossRef 的 kind 字段形成了三态模型（F-015, F-053）：
- `"to-resolve"`：gen 时无法解析的占位符，由 ingest 或 viewer 解析；
- `"missing"`：ingest 尝试解析但未找到目标，渲染时显示为纯文本（附带 debug 信息）；
- 已解析值（"module"/"api"/"local"等）：直接生成链接。

未解析引用的调试体验设计（F-056）：渲染为带 `data-debug` 属性的 `<span>`，CSS `:hover::after` 显示 `unresolved RefInfo(module=?, version=?, kind=?, path=?)`，无需打开 devtools 即可诊断链接断裂原因。

**安全双重防护**（F-065, F-066）：Python 端 pack 时和 TypeScript 端 ingest 时都进行 URL 安全检查（仅允许 http/https/mailto + 相对路径，禁止 javascript:/data: XSS 向量），unpack 时进行路径遍历检查，形成深度防御。

```
┌─────────────────────────────────────────────────────┐
│  RawStore: _raw/<pkg>/<ver>.papyri.gz (权威源)       │
│  → POST /api/reingest 可重建一切                      │
├─────────────────────────────────────────────────────┤
│  BlobStore (FS)     │  GraphDb (SQLite)              │
│  CBOR blobs         │  nodes(id,pkg,ver,cat,ident)   │
│  按4元组索引         │  links(source→dest)            │
│  内容可信源          │  关系可信源                     │
├─────────────────────────────────────────────────────┤
│  渲染层: collectXrefs → resolveRefs(batch)          │
│         → XRefResolver(sync closure) → renderNode   │
└─────────────────────────────────────────────────────┘
```

**复用价值**：Blob+Graph 双层存储适用于内容寻址+关系查询的混合场景；两阶段解析模式（async 批量收集 → sync 闭包渲染）是服务端模板渲染中处理异步依赖的通用模式；易变字段剥离确保了基于哈希的变更检测的可靠性。
