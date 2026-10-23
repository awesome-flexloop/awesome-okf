---
type: reference
scope: zvec
name: zvec 源码信源
version: "0.8.0-4-g8d49969"
source: external/dao/alibaba/zvec
description: alibaba/zvec 源码镜像登记——commit 8d49969（v0.8.0-4），本束全部源码级事实的可追溯锚点
generated: { by: "teleagent/seven-concepts-r", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
---

# zvec 源码信源登记

## 一、信源定位

| 属性 | 值 |
|---|---|
| 仓库 | [alibaba/zvec](https://github.com/alibaba/zvec) |
| 本地镜像 | `external/dao/alibaba/zvec`（SpecWeave 工作区内稳定归档位置，含完整 `.git`） |
| 固定版本 | commit `8d4996924bce78f8b072a353803c305101bcc807`（`v0.8.0-4-g8d49969`，main 分支） |
| 基准 tag | v0.8.0（HEAD 位于其后 4 个提交） |
| 许可证 | Apache License 2.0 |
| 采集日期 | 2026-10-22 |

> 镜像工作区干净（`git status` 无未提交变更）。引用版本以 commit hash 为准；tag 名仅作辅助定位。

## 二、仓库顶层结构

```
zvec/
├── src/           # C++ 源码（ailego/binding/core/db/include/turbo 六模块）
├── python/        # Python SDK（zvec 包 + 42 个测试文件）
├── examples/      # C 示例 7 个 + C++ 示例 5 个
├── tools/         # core（bench/recall/local_builder）与 db（fts_bench）基准工具
├── tests/         # C++ 测试
├── thirdparty/    # 17 个 git submodule 依赖
├── cmake/         # CMake 模块
├── scripts/       # 构建脚本
├── CMakeLists.txt # 顶层构建
├── README.md / README_CN.md
└── pyproject.toml # Python 包定义
```

## 三、thirdparty 依赖（17 个 submodule）

| 依赖 | 版本 | 在 zvec 中的用途 |
|---|---|---|
| rocksdb | 8.1.1 | KV 存储（id_map、FTS 倒排列、manifest 相关） |
| arrow | 21.0.0 | 列存（Arrow IPC / Parquet 存储层） |
| antlr4 | — | SQL 过滤表达式引擎（SQLLexer.g4/SQLParser.g4） |
| RaBitQ-Library | 0.7.0 | RaBitQ 量化算法参考实现 |
| cppjieba / limonp | 5.6.7 / v1.0.2 | 中文分词（FTS Jieba） |
| libaio | 0.3 | Linux 异步 I/O（DiskANN 可选加速） |
| googletest / gflags / glog / magic_enum / yaml-cpp / lz4 / FastPFOR / sparsehash / utf8proc / snowball | — | 测试、标志、日志、枚举反射、配置、压缩、编码等基础设施 |

## 四、源码级事实锚点（V 阶段 Grep 验证目标）

| 锚点 | 路径 |
|---|---|
| 公共 C API | `src/include/zvec/c_api.h`、`export.h`、`version.h.in` |
| Python 公共 API | `python/zvec/__init__.py`（`__all__` 导出） |
| 枚举定义 | `python/zvec/typing/__init__.pyi`（DataType 23 / IndexType 10 / QuantizeType 8 / MetricType 3 / IOBackendType 4 / StatusCode 11） |
| Collection 类 | `python/zvec/model/collection.py`（24 个公共成员：20 方法 + 4 属性） |
| 生命周期入口 | `python/zvec/zvec.py`（`init` / `create_and_open` / `open`） |
| 索引算法 | `src/core/algorithm/`（cluster/diskann/flat/flat_sparse/hnsw/hnsw_rabitq/hnsw_sparse/ivf/ivf_rabitq/vamana 共 10 个算法目录） |
| 量化器 | `src/turbo/quantizer/` 与 `src/core/quantizer/` |
| SIMD 距离内核 | `src/turbo/distance/`（avx2/avx512/avx512_fp16/avx512_vnni/neon/neon_fp16/sse2/scalar） |
| SQL 引擎 | `src/db/sqlengine/`（antlr/analyzer/parser/planner/ops） |
| 存储层 | `src/db/index/storage/`（wal/、arrow_ipc_writer、parquet_writer、bufferpool/memory/mmap_forward_store） |
| Embedding/Reranker 扩展 | `python/zvec/extension/`（16 个模块文件） |
