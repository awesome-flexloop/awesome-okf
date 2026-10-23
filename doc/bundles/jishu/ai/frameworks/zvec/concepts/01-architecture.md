---
type: Concept
title: Zvec 源码架构：四层 C++ 分层与 C API 边界
description: ailego 基础库→turbo SIMD 计算层→core 算法层→db 存储引擎层的四层架构，17 个 thirdparty 依赖与 7 语言 SDK 共享的 C API 边界
tags: [zvec, architecture, c-plus-plus, simd, antlr, rocksdb, arrow]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-source
    resource: /references/source-code.md
    title: alibaba/zvec 源码信源
---

# Zvec 源码架构：四层 C++ 分层与 C API 边界

Zvec 的 `src/` 目录由 6 个模块构成清晰的自底向上分层：`ailego`（通用基础库）→ `turbo`（SIMD 计算层）→ `core`（向量算法层）→ `db`（存储引擎层），外加 `include`（公共 C API）与 `binding`（多语言绑定）。所有 SDK 共享同一条 C API 边界，从根上保证 7 语言行为一致。

```text
应用代码（Python / Node.js / Go / Rust / Java / Dart / C++）
        │  7 语言 SDK ── 同一条稳定 C API 边界
        ▼
┌─────────────────────────────────────────────────┐
│ src/include/zvec   c_api.h / export.h           │
├─────────────────────────────────────────────────┤
│ src/db   存储引擎层                               │
│   index/column（fts/inverted/vector 三类列）      │
│   index/segment + index/storage（WAL/Arrow/Parquet）│
│   sqlengine（ANTLR4 SQL 过滤引擎）                │
│   common（rocksdb_context/cgroup_util/roaring）  │
│   reranker（C++ 侧融合重排）                      │
├─────────────────────────────────────────────────┤
│ src/core 向量算法层                               │
│   algorithm（10 个算法目录）                      │
│   quantizer（RaBitQ/Uniform converter+reformer） │
│   metric / framework / interface / mixed_reducer│
├─────────────────────────────────────────────────┤
│ src/turbo SIMD 计算层                             │
│   distance（avx2/avx512/vnni/neon/sse2/scalar） │
│   quantizer（fp16/int4/int8/pq_*）               │
│   preprocessor（fht_rotator/opq_rotator）        │
├─────────────────────────────────────────────────┤
│ src/ailego 通用基础库                              │
│   buffer/container/encoding/hash/io/logger/...  │
└─────────────────────────────────────────────────┘
        │  17 个 thirdparty submodule
        ▼
rocksdb 8.1.1 / arrow 21.0.0 / antlr4 / RaBitQ-Library 0.7.0
cppjieba 5.6.7 / libaio / FastPFOR / utf8proc / snowball ...
```

## 各层职责

### ailego：零外部依赖的基础库

buffer、container、encoding、hash、internal、io、logger、math_batch、parallel、pattern、string、utility 十二个子目录，承担通用数据结构与并行原语，让上层算法代码不直接触碰 STL 之外的系统 API。

### turbo：多架构 SIMD 计算层

- **distance**：九套距离内核目录——avx2、avx512、avx512_fp16、avx512_vnni、neon、neon_fp16、sse2、scalar、common，覆盖 x86 与 ARM 双阵营的多代指令集。
- **quantizer**：存储格式压缩器——fp16/fp32/int4/int8 标量量化与 pq_fast/pq_int4/pq_int8 乘积量化。
- **preprocessor**：量化前旋转——fht_rotator（快速 Hadamard 变换）与 opq_rotator（优化乘积量化旋转），对应 API 层 `enable_rotate=True` 的实现。

### core：向量算法层

`algorithm/` 含 10 个算法目录：cluster（KMeans 聚类，含 turbo_kmeans_context、stratified_cluster）、diskann、flat、flat_sparse、hnsw、hnsw_rabitq、hnsw_sparse、ivf、ivf_rabitq、vamana。注意三个"文档未展开但源码存在"的成员：**flat_sparse/hnsw_sparse** 是稀疏向量索引实现，**vamana** 是 DiskANN 所用图算法的独立实现（配套 VamanaIndexParam/VamanaQueryParam）。`quantizer/` 则是算法内嵌的距离估计量化（binary/cosine/half_float/integer/mips/raw_uint8/uniform_uint4/uniform_uint7 的 converter+reformer 对与 rotator）。

### db：存储引擎层

- **index/column**：三类列引擎——fts_column（BM25/WAND 全文）、inverted_column（倒排过滤）、vector_column（向量索引）。
- **index/segment + storage**：段式多版本管理；存储层含 `wal/`（WAL 预写日志）、arrow_ipc_writer、parquet_writer/parquet_buffer_pool（Apache Arrow 列存）、bufferpool/memory/mmap 三种 forward store 与 chunked_file_writer。
- **sqlengine**：完整的 SQL 过滤表达式引擎——ANTLR4 语法（SQLLexer.g4/SQLParser.g4 + 生成物）→ parser（含 zvec_cached_sql_parser 缓存解析）→ analyzer（query_analyzer/search_cond_binder 等）→ planner（query_planner/optimizer + ops 算子目录），将 `"publish_year > 1936"` 类过滤字符串编译为可执行计划。
- **common**：rocksdb_context（RocksDB KV 上下文）、cgroup_util（容器配额感知）、concurrent_roaring_bitmap（并发位图）、global_resource、error_code。

## C API 边界与绑定

`src/include/zvec` 顶层仅三个头文件：`c_api.h`（公共 C API）、`export.h`（符号导出）、`version.h.in`（版本模板）。`src/binding` 提供 c 与 python 两类绑定；Python 侧经 `_zvec` 原生扩展将枚举与参数类直接映射（`python/zvec/typing/__init__.pyi` 是其类型存根），Python 门面层（model/extension/executor）再包装出 `Collection` 等 API。

## thirdparty 依赖（17 个 submodule）

rocksdb（KV 存储：id_map、FTS 倒排列）、arrow（Arrow IPC/Parquet 列存）、antlr4（SQL 引擎）、RaBitQ-Library（量化算法参考）、cppjieba+limonp（中文分词）、libaio（DiskANN 异步 I/O）、googletest/gflags/glog/magic_enum/yaml-cpp/lz4/FastPFOR/sparsehash/utf8proc/snowball（基础设施）。重型依赖全部 vendored 进仓库，安装产物无需系统级依赖——这是"开箱即用"的工程基础。

## 相关概念

- [总览](00-overview.md)：产品矩阵与特性
- [索引类型](03-index-types.md)：core/algorithm 十目录对应的索引能力
- [存储与配置](08-storage-and-config.md)：WAL/Arrow/RocksDB 细节与 init() 容器自适应
