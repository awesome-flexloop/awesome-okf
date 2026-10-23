---
type: reference
scope: zvec
name: zvec 事实清单
version: "1.0.0"
source: external/dao/alibaba/zvec @ 8d49969, https://zvec.org/zh/ @ 2026-10-22
description: R 阶段编号事实清单（零推测）——源码与官方文档双信源交叉采集，数量类事实均经脚本计数
generated: { by: "teleagent/seven-concepts-r", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
---

# zvec 事实清单（73 条，编号 F-001 ~ F-110，按主题跳号分组）

> 采集信源：源码 S = `external/dao/alibaba/zvec` @ commit 8d49969（v0.8.0-4）；文档 D = zvec.org 中文站 2026-10-22 快照。数量类事实均以脚本计数复核（R 正则/AST → V 独立手段）。

## 一、产品与定位

- **F-001**（D 首页）：Zvec 定位为"本地优先检索内置即用"——面向应用的嵌入式检索与面向开发者和 AI Agent 的本地工作区搜索。
- **F-002**（D 总览）：产品线分两个——Zvec（嵌入式检索引擎，应用内 Schema/索引/过滤/混合查询）与 Zvec-Grep（本地工作区搜索，CLI/MCP/Agent）。
- **F-003**（D 关于页）：Zvec 是开源、高性能、轻量级向量数据库，完全以进程内（嵌入式）方式运行——无需服务器、守护进程或外部软件设施。
- **F-004**（D 关于页）：Zvec 既可作为独立向量数据库，也可集成到既有搜索系统（如传统 SQL 数据库）充当专用向量搜索引擎。
- **F-005**（D 关于页）：Zvec 经历阿里巴巴集团生产级工作负载验证；适用场景从快速原型/本地开发到嵌入式应用/边缘部署再到超十亿级规模生产系统。
- **F-006**（S README_CN）：README 列出 v0.8.0 变更——Intel Mac 与 Windows ARM64 构建、DiskANN 扩展至 Windows/Android/iOS、RaBitQ 新增 Windows x86_64、内置 Jieba 中文词典和 HMM 模型、UTF-8 文档 ID 长度上限提升至 1024 字节、新增 Uniform 系列量化器、优化 Vamana 图布局与预取。
- **F-007**（D 首页）：SDK 覆盖 Python / Node.js / Go / Rust / Dart / C++ 共 6 类入口链接（C/C++ 指向 alibaba/zvec 本体）。
- **F-008**（D 平台页）：语言 SDK 共 7 种（Python/Node.js/Go/Rust/Java/Dart-Flutter/C-C++），全部共享同一条稳定 C API 边界。
- **F-009**（D 平台页）：平台矩阵——Linux（x86_64/ARM64，glibc 与 musl）、macOS（x86_64/ARM64）、Windows（x86_64/ARM64）、Android（arm64-v8a，C/C++ SDK）、iOS（arm64，C/C++ SDK）、RISC-V（riscv64 需源码构建）；Windows ARM64 不提供 Python 3.10 wheel。
- **F-010**（D 平台页）：索引可用性矩阵为 9 类索引 × 9 平台。
- **F-011**（D 首页性能卡）：Cohere 1000 万 · VectorDBBench，16 vCPU · 64 GiB · INT8 · 最高 20 并发——1000 万向量、8500+ QPS、约 1 小时构建。
- **F-012**（D 首页生态）：开源生态集成五例——Logseq（混合检索）、MyContext（向量存储）、ReMe（记忆后端）、txtai（稠密 ANN）、CocoIndex（索引 Connector）。

## 二、源码架构

- **F-020**（S 目录）：`src/` 含 6 个模块目录：ailego、binding、core、db、include、turbo（脚本计数 = 6）。
- **F-021**（S 目录）：`src/ailego` 为通用基础库——buffer、container、encoding、hash、internal、io、logger、math_batch、parallel、pattern、string、utility 子目录。
- **F-022**（S 目录）：`src/turbo` 为 SIMD 计算层——distance（avx2/avx512/avx512_fp16/avx512_vnni/neon/neon_fp16/scalar/sse2/common）、quantizer（fp16/fp32/int4/int8/pq_fast/pq_int4/pq_int8）、preprocessor（fht_rotator/opq_rotator）、conversion（avx512）。
- **F-023**（S 目录）：`src/core/algorithm` 含 10 个算法目录：cluster、diskann、flat、flat_sparse、hnsw、hnsw_rabitq、hnsw_sparse、ivf、ivf_rabitq、vamana。
- **F-024**（S 目录）：`src/core/quantizer` 含 converter/reformer 对（binary、cosine、half_float、integer、mips、raw_uint8、uniform_uint4、uniform_uint7）+ rotator 子目录。
- **F-025**（S 目录）：`src/db` 含 common、index、reranker、sqlengine 四个子目录。
- **F-026**（S 目录）：`src/db/sqlengine` 为完整 SQL 过滤引擎——antlr（SQLLexer.g4、SQLParser.g4 + gen 生成物）、analyzer、parser（含 zvec_cached_sql_parser）、planner（query_planner/optimizer/ops/）、common。
- **F-027**（S 目录）：`src/db/index` 含 column（fts_column/inverted_column/vector_column）、common（manifest/id_map/schema/version_manager）、segment（segment_manager 等）、storage 子目录。
- **F-028**（S 目录）：`src/db/index/storage` 含 wal/（local_wal_file、wal_file）、arrow_ipc_writer、parquet_writer、parquet_buffer_pool、forward_writer、chunked_file_writer、bufferpool/memory/mmap_forward_store。
- **F-029**（S 目录）：`src/db/common` 含 rocksdb_context、cgroup_util、concurrent_roaring_bitmap、global_resource、error_code 等文件。
- **F-030**（S grep）：rocksdb 引用出现在 rocksdb_context、id_map、bm25_scorer、segment_helper、file_helper。
- **F-031**（S 目录）：`src/include/zvec` 顶层头文件仅 3 个：c_api.h、export.h、version.h.in——公共 C API 边界。
- **F-032**（S 目录）：`src/binding` 含 c 与 python 两类绑定（python 下含 include/model/typing）。
- **F-033**（S .gitmodules 计数）：thirdparty 含 17 个 submodule（脚本计数 = 17）：googletest、sparsehash、gflags、rocksdb-8.1.1、yaml-cpp、arrow-21.0.0、glog、lz4、antlr4、magic_enum、RaBitQ-Library-0.7.0、libaio-0.3、cppjieba-5.6.7、FastPFOR、limonp、utf8proc、snowball。
- **F-034**（S 目录）：`examples/` 含 C 示例 7 个（basic/collection_schema/diskann/doc/field_schema/index/optimized）与 C++ 示例 5 个 .cc（ailego/main、core/main、core/diskann_main、core/external_vector_example、db/main）。
- **F-035**（S 目录）：`tools/core` 含 bench、recall、local_builder 基准工具及 convert_cohere_parquet.py；`tools/db` 含 fts_bench_main.cc。

## 三、数据模型与 API

- **F-040**（S .pyi 计数）：DataType 枚举 23 个成员——基础标量 8（STRING/BOOL/INT32/INT64/UINT32/UINT64/FLOAT/DOUBLE）+ 稠密向量 5（VECTOR_FP16/FP32/FP64/INT8/UINT8）+ 稀疏向量 2（SPARSE_VECTOR_FP32/FP16）+ 数组 8（ARRAY_*）。
- **F-041**（D 数据结构页）：文档侧 DataType 列出基础 8 + 稠密 3（FP16/FP32/INT8）+ 稀疏 2 + 数组 8 = 21 个；源码多出 VECTOR_FP64 与 VECTOR_UINT8（文档-源码差异，以源码为准）。
- **F-042**（S .pyi 计数）：IndexType 枚举 10 个成员：UNDEFINED、HNSW、IVF、IVF_RABITQ、FLAT、HNSW_RABITQ、DISKANN、VAMANA、INVERT、FTS。
- **F-043**（S .pyi 计数）：QuantizeType 枚举 8 个成员：UNDEFINED、FP16、INT8、INT4、RABITQ、UNIFORM_UINT7、UNIFORM_UINT8、UNIFORM_UINT4。
- **F-044**（S .pyi 计数）：MetricType 枚举 3 个成员：L2（1）、IP（2）、COSINE（3）。
- **F-045**（S .pyi 计数）：IOBackendType 枚举 4 个成员：PREAD（同步 pread）、LIBAIO（运行时 dlopen 加载）、IO_URING（raw 系统调用零依赖）、WINDOWS_OVERLAPPED（IO 完成端口）——用于 DiskANN 磁盘读。
- **F-046**（S .pyi 计数）：StatusCode 枚举 11 个成员（OK/NOT_FOUND/ALREADY_EXISTS/INVALID_ARGUMENT/PERMISSION_DENIED/FAILED_PRECONDITION/RESOURCE_EXHAUSTED/UNAVAILABLE/INTERNAL_ERROR/NOT_SUPPORTED/UNKNOWN）。
- **F-047**（S collection.py 计数）：Collection 类公共成员 24 个——方法 20（add_column、alter_column、close、create_index、delete、delete_by_filter、destroy、drop_column、drop_index、fetch、flush、group_by_query、insert、iter_docs、optimize、query、query_internal_ids、resolve_internal_ids、update、upsert）+ 属性 4（path、option、schema、stats）。
- **F-048**（S zvec.py）：生命周期三函数 init / create_and_open / open；init() 仅可调用一次，共 12 个可选参数（log_type、log_level、log_dir、log_basename、log_file_size、log_overdue_days、query_threads、optimize_threads、invert_to_forward_scan_ratio、brute_force_by_keys_ratio、fts_brute_force_by_keys_ratio、memory_limit_mb），None 参数回落 cgroup 环境感知默认值。
- **F-049**（S __init__.py）：Python SDK 32 位解释器在 import 时即抛 ImportError（要求 64 位 CPython）。
- **F-050**（S 目录）：python/zvec 含 model（collection/doc/schema/param/convert）、extension、executor、tool、typing、common 子包；`python/zvec/__init__.pyi` 与 `typing/__init__.pyi` 为 C++ 绑定的类型存根。
- **F-051**（S 目录计数）：python/tests 含 42 个 test_*.py（顶层 31 + detail/ 11）。
- **F-052**（S 目录计数）：python/zvec/extension 含 16 个 .py 模块文件（含 __init__.py）。

## 四、检索与索引

- **F-060**（D 向量索引页）：官方文档索引类型 6 种——Flat、HNSW、HNSW-RaBitQ、DiskANN、IVF、IVF-RaBitQ；Vamana 为 DiskANN 内图算法（源码另有独立 vamana 算法目录与 VamanaIndexParam/VamanaQueryParam）。
- **F-061**（D HNSW 页）：HNSW 构建参数 metric_type/m/ef_construction/quantize_type；查询参数 ef/radius/is_linear/is_using_refiner。
- **F-062**（D HNSW-RaBitQ 页）：平台要求 Linux x86_64 + AVX2/AVX512；参数 m/ef_construction/total_bits（默认 7，1-9 位）/num_clusters（默认 16）/sample_count；维度限制 64–4095；论文口径 7 位约 99% Recall、5 位约 95%、4 位约 90%。
- **F-063**（D DiskANN 页）：平台仅 Linux；libaio 可选依赖；构建参数 max_degree/list_size/pq_chunk_num；查询参数 list_size；Vamana 图 + PQ 内存压缩 + 束搜索 + BFS 层级缓存；NeurIPS 2019 论文出处。
- **F-064**（D IVF 页）：构建参数 n_list（建议 ≈ √N）/n_iters/quantize_type；查询参数 n_probe/radius/is_linear。
- **F-065**（D IVF-RaBitQ 页）：默认值 nlist=1024、total_bits=7、sample_count=0、nprobe=10、radius=0.0、is_using_refiner=False、scale_factor=10.0；仅支持 FP32 稠密向量、64–4095 维。
- **F-066**（D 量化页）：Zvec 同时存储原始向量与量化版本；量化仅在 FP32 向量上收益；INT8/INT4 可设 quantizer_param 的 enable_rotate=True 施加随机正交旋转。
- **F-067**（D FTS 页）：FTS 索引参数 tokenizer_name/filters/extra_params；查询参数 match_string、query_string、default_operator；WAND（Weak AND）+ Block-Max 以 128 个 Document 为一块快速跳跃。
- **F-068**（D FTS 页）：分词器 standard（Unicode UAX #29，类 Elasticsearch standard）、whitespace、jieba；过滤器 lowercase、stemmer、ascii_folding。
- **F-069**（D FTS 页）：单个 Query 内 fts 与 vector/id 互斥；混合需多路查询配合重排序或应用层合并。
- **F-070**（D 倒排索引页）：倒排索引支持精确值过滤（=、IN）、范围查询、LIKE 前后缀匹配、CONTAIN_ANY / CONTAIN_ALL 数组成员查询。
- **F-071**（D 查询页）：query() 支持 6 种查询类型——单向量、多向量、条件过滤、向量+过滤（hybrid）、全文检索（fts）、分组搜索（group_by_query，参数 group_by_field_name/group_count/topk_per_group）。
- **F-072**（D 查询页）：Query 指定 field_name + 查询来源（vector 或 Document id 或 fts 子句）+ 可选 param；多路查询传 Query 列表。
- **F-073**（D 优化页）：新插入向量先暂存 Flat 缓冲区，optimize() 后台合并进配置索引、不锁 collection；建议未索引文档达 10 万条以上时优化。

## 五、Embedding 与 Reranker

- **F-080**（D Embedding 页）：Embedding 函数 7 种——DefaultLocalDenseEmbedding（all-MiniLM-L6-v2，384 维，~80MB，ModelScope 可选中文模型）、DefaultLocalSparseEmbedding（SPLADE）、BM25EmbeddingFunction（DashText，本地免 API）、QwenDenseEmbedding、QwenSparseEmbedding、OpenAIDenseEmbedding、JinaDenseEmbedding（v5 系列，Matryoshka 32-1024 维）。
- **F-081**（D Embedding 页）：协议基类 DenseEmbeddingFunction[T] / SparseEmbeddingFunction[T]；框架基类 SentenceTransformerFunctionBase / QwenFunctionBase / OpenAIFunctionBase；当前仅支持文本模态。
- **F-082**（D Reranker 页）：Reranker 4 种——DefaultLocalReRanker（cross-encoder/ms-marco-MiniLM-L6-v2）、QwenReRanker（gte-rerank-v2）、RrfReRanker（倒数排名融合，rank_constant）、WeightedReRanker（权重融合）；RrfReRanker 仅用排名位置不需评分。
- **F-083**（S __init__.py）：extension 导出 17 个公开名（含 BM25EmbeddingFunction、JinaFunctionBase 等）。
- **F-084**（S extension/__init__.py）：JinaDenseEmbedding 与 JinaFunctionBase 由 `zvec.extension` 子包导出（`from .jina_embedding_function import JinaDenseEmbedding`），但顶层 `zvec` 命名空间 `__all__` 未包含二者——V 阶段 Grep 验证发现并留痕。

## 六、Agent 集成与 zvec-grep

- **F-090**（D MCP 页）：zvec-mcp-server 通过 uvx 分发，暴露 17 个工具，覆盖 Collection 管理（4）、Document 操作（5）、向量查询（2）、索引管理（3）、AI Embedding（3）；环境变量 OPENAI_API_KEY/OPENAI_BASE_URL/OPENAI_EMBEDDING_MODEL。
- **F-091**（D Skills 页）：Agent Skills 安装命令 `npx skills add github:zvec-ai/zvec-agent-skills --skill "zvec"`；注入 Schema 设计、索引策略、分块经验知识。
- **F-092**（D zvec-grep 页）：zvec-grep 为面向开发者与 AI Agent 的本地工作区检索工具，zg CLI 或本地 MCP；仓库 zvec-ai/zvec-grep（独立于 alibaba/zvec）。
- **F-093**（D 快速上手页）：安装需 Node.js 22+，`npm install -g @zvec/zvec-grep`；索引保存于 `<workspace>/.zvec-grep/`。
- **F-094**（D CLI 页）：zg 命令面——query、index、status、install、uninstall、server、config、auth、help、version；环境变量 ZVEC_GREP_MODE、ZVEC_GREP_EMBEDDING、ZVEC_GREP_MODEL_CACHE、ZVEC_GREP_DEVICE。
- **F-095**（D 检索指南页）：zg query 四路径——默认混合（位置参数）、--fts（BM25）、--vector（纯语义）、--rg（内置 ripgrep 穷举）；--hybrid 融合词法与向量；-g glob、-t 类型、--modified-after/before、--refresh background|wait|off。
- **F-096**（D Embedding 模型页）：本地模型 11 个（文档表格口径）——potion-code-16m-v2（默认）、potion-retrieval-32m、potion-multilingual-128m（Model2Vec FP16/FP32）、all-minilm-l6-v2、bge-small-en-v1.5、multilingual-e5-small、jina-embeddings-v2-base-code、gte-modernbert-base、nomic-embed-text-v1.5（ONNX Q4/Q8）、embeddinggemma-300m、qwen3-embedding-0.6b（GGUF Q8_0）；远程模型 3 个（qwen/text-embedding-v4、qwen/qwen3.7-text-embedding、qwen/qwen3-vl-embedding）。
  > 勘误留痕：初稿误记"本地模型 10 个"，V 阶段逐条清点表格为 11 条目（Potion 3 + ONNX 6 + GGUF 2），已同步束内概念文档。
- **F-097**（D Embedding 模型页）：设备支持 auto/cpu/metal/vulkan/cuda（Transformer 与 GGUF）；Potion 静态查表模型 GPU 无加速；模型缓存默认 ~/.zvec-grep/models。
- **F-098**（D agents 页）：zg install 目标 codex/claude/qwen/cursor/opencode/all/auto；默认仅暴露 1 个 MCP 工具 zvec_grep_search；检索路由——精确词语/路径/正则用原生 grep/rg，措辞或位置未知用 zvec_grep_search；索引创建/重建/删除仍由用户 CLI 显式执行。
- **F-099**（D supported-content 页）：结构化提取保留符号/签名/面包屑的语言 7 类——C/C++、Go、Java、JavaScript/JSX、TypeScript/TSX、Python、Rust；Vue/Svelte 脚本部分尽力结构化；PDF、Office、压缩包、音视频、二进制不索引；图片（GIF/JPEG/PNG/WebP）默认不索引、需显式包含。
- **F-100**（D Benchmark 页）：SWE-QA-Bench（11 仓库 20 任务×3 次）+1.50pp 回答质量 / −47.3% 输入 Token / −58.6% 工具调用 / −37.5% Agent 耗时；BrowseComp-Plus（100,195 篇文档 80 样例×2 次）+0.33pp / −37.56% / −43.52% / −38.58%。
- **F-101**（D quickstart 页）：MCP 工具调用形态 `zvec_grep_zvec_grep_search {"root":...,"query":...,"fts":[...],"fuse":true}`。

## 七、基准复现

- **F-110**（D benchmarks 页）：VectorDBBench（zilliztech）+ Cohere 1M/10M（768 维）；复现环境 Ubuntu 24.04、g9i.4xlarge（16 vCPU 64 GiB）；Cohere 10M 参数 quantize-type int8、m 50、ef-search 118、--is-using-refiner；Cohere 1M 参数 m 15、ef-search 180；并发 12/14/16/18/20。
