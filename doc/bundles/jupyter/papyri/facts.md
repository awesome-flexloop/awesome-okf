---
type: Facts
okf_version: "0.2"
title: "papyri 源码事实清单"
generated: "2026-08-22"
tags: [jupyter,documentation,papyri,help-system]
sources:
  - ../../../../../external/libs/jupyter/papyri/pyproject.toml
  - ../../../../../external/libs/jupyter/papyri/papyri/__init__.py
  - ../../../../../external/libs/jupyter/papyri/papyri/nodes.py
  - ../../../../../external/libs/jupyter/papyri/papyri/node_base.py
  - ../../../../../external/libs/jupyter/papyri/papyri/gen.py
  - ../../../../../external/libs/jupyter/papyri/papyri/tree.py
  - ../../../../../external/libs/jupyter/papyri/papyri/graphstore.py
  - ../../../../../external/libs/jupyter/papyri/papyri/bundle.py
  - ../../../../../external/libs/jupyter/papyri/papyri/pack.py
  - ../../../../../external/libs/jupyter/papyri/papyri/doc.py
  - ../../../../../external/libs/jupyter/papyri/ingest/src/ingest.ts
  - ../../../../../external/libs/jupyter/papyri/ingest/src/graph-db.ts
  - ../../../../../external/libs/jupyter/papyri/viewer/src/lib/xref.ts
  - ../../../../../external/libs/jupyter/papyri/viewer/src/lib/render-node.ts
---

# papyri 源码事实清单

## 项目元数据

- F-001: pyproject.toml:6 — 项目名为 `papyri`，作者 Matthias Bussonnier，MIT 许可证
- F-002: pyproject.toml:12 — requires-python 为 `>=3.13`
- F-003: pyproject.toml:14-26 — 核心依赖：cbor2>=6.1.1（CBOR 序列化）、ipython（内省）、jedi（代码补全）、matplotlib（图表内联）、numpydoc（NumPy 风格 docstring 解析）、pygments（语法高亮）、rich（终端输出）、tomli_w（TOML 写入）、tree-sitter>=0.24（RST 解析）、py-tree-sitter-rst>=0.2.2（RST 语法）、typer>=0.9（CLI 框架）
- F-004: pyproject.toml:32 — CLI 入口点：`papyri = "papyri:app"`
- F-005: pyproject.toml:2 — 构建系统使用 flit_core
- F-006: __init__.py:70 — 版本号为 0.0.10
- F-007: __init__.py:80-97 — 使用 typer.Typer 创建 CLI 应用，no_args_is_help=True，pretty_exceptions_enable=False

## CLI 命令体系

- F-008: __init__.py:121-133 — 注册 11 个子命令：about、gen、pack、unpack、bootstrap、find、describe、debug、diff、upload，每个命令对应 cli/ 目录下一个独立模块
- F-009: __init__.py:107-118 — `--version/-V` 选项使用 eager callback，打印 logo 和版本后退出
- F-010: papyri/cli/ 目录按功能拆分：gen.py（IR 生成）、pack.py（打包）、unpack.py（解包）、upload.py（上传到 viewer）、find.py（搜索）、describe.py（描述）、diff.py（差异比较）、debug.py（调试）、about.py（关于）、bootstrap.py（引导）

## IR（中间表示）节点系统

- F-011: node_base.py:45-56 — Node 基类使用 dataclass 风格，通过 `__init__` 按类型注解顺序接收位置参数，自动处理 list→tuple 类型强制转换，支持 `_post_deserialise` 钩子
- F-012: node_base.py:58-70 — Node.cbor() 方法实现 CBOR 序列化：通过 TAG_MAP 查找 CBOR tag，按类型注解顺序编码字段值为数组，过滤标记 `_drop_in_cbor` 的 Comment 节点
- F-013: node_base.py:15-18 — Base 类提供 validate() 方法，通过全局 validate 函数校验节点
- F-014: nodes.py:76-135 — InlineRole 节点表示未解析的 RST 解释文本角色（如 `:func:`numpy.linspace``），包含 value、domain、role、inventory 四个字段，inventory 用于 intersphinx 外部引用
- F-015: nodes.py:138-150 — CrossRef 节点表示跨引用，reference.kind 标记解析状态："to-resolve"（待解析占位符）、"missing"（未找到）、其他值表示已解析（"module"/"local"/"api"等）
- F-016: nodes.py:72 — register(4444)(tuple) 将内置 tuple 类型注册为 CBOR tag 4444
- F-017: nodes.py 中通过 @register(N) 装饰器注册多种 IR 节点类型，每个节点分配唯一 CBOR tag（如 InlineRole=4003, CrossRef=4002, Bundle=4070 等）
- F-018: node_base.py:25-42 — `_coerce_field` 函数在 Node 初始化时自动将 list 转换为 tuple，确保 CBOR 解码（cbor2≥6 将数组解码为 tuple）和手动构造的 list 产生一致的存储类型

## IR 生成管道（papyri gen）

- F-019: gen.py:26-34 — 在模块加载时注册第三方 doctest 选项标志（FLOAT_CMP、REMOTE_DATA、IGNORE_OUTPUT、IGNORE_WARNINGS、IGNORE_EXCEPTION）为 no-op，避免 doctest.DocTestParser 拒绝未知选项
- F-020: gen.py:64-99 — gen 命令导入核心组件：Config 加载、GeneratedDoc 容器、BlockExecutor（doctest 执行）、GenVisitor（RST→IR 转换）、NumpyDocString（numpydoc 解析）、Signature（签名解析）、make_tree（TOC 生成）
- F-021: gen.py:53 — 使用 IPython.core.oinspect.find_file 进行文件内省
- F-022: gen.py:55 — 使用 matplotlib._pylab_helpers 管理图形内联
- F-023: doc.py:1-9 — GeneratedDoc 是 `papyri gen` 输出的核心数据结构，表示单个 API 对象的文档，对应 IngestedDoc（交叉链接后的形式）
- F-024: doc.py:45-60 — _OrderedDictProxy 维护 section 的有序映射，解决 dict 序列化/反序列化可能丢失顺序的问题

## Bundle 打包格式

- F-025: bundle.py:26-27 — 版本常量：PACK_FORMAT_VERSION=1，IR_SCHEMA_VERSION=1
- F-026: bundle.py:30-47 — BundleManifest 是 papyri.json（JSON 清单）的类型化表示，包含 module、version、summary、github_slug、tag、logo、aliases、extra 字段，所有可选字段默认为空字符串/空字典
- F-027: bundle.py:50-66 — Bundle 节点（CBOR tag 4070）是打包后的顶层 IR 对象，字段按顺序排列：pack_format_version、ir_schema_version、module、version、summary、github_slug、tag、logo、aliases、extra、api（dict[str, GeneratedDoc]）、narrative（dict[str, GeneratedDoc]）、examples（dict[str, Section]）、assets（dict[str, bytes]）、toc（tuple[TocTree, ...]）
- F-028: bundle.py:9-11 — Bundle 字段在 CBOR 中按位置编码，pack_format_version 和 ir_schema_version 放在最前面，便于前向兼容性快速检查
- F-029: pack.py:1-8 — `.papyri` 制品是单个 Bundle 节点，使用确定性 CBOR（RFC 8949 §4.2）编码 + gzip 压缩（zero-mtime 头），同一目录两次打包必须产生字节相同的输出
- F-030: pack.py:31 — 允许的顶层目录：papyri.json、toc.json、module、docs、examples、assets
- F-031: pack.py:35-46 — `_safe_child` 函数防止路径遍历攻击：解析 base/name 后检查是否在 base 目录内，拒绝 `../../etc/x` 等逃逸路径
- F-032: pack.py:49-64 — `_is_safe_url` 函数实现 URL 安全检查：仅允许 http/https/mailto 方案和相对 URL，剥离控制字符后检测 scheme，防止 javascript:/data: XSS 向量

## RST 解析与转换

- F-033: tree.py:15-44 — GenVisitor 注册了大量 RST 指令处理器：admonition（注意/警告/提示等）、block_math（块级数学）、code（代码块）、csv_table/list_table（表格）、deprecated/versionadded/versionchanged（版本标记）、figure/image（图片）、include/literalinclude（包含）、plot（绘图）、raw（原始内容）、rubric/seealso/topic（辅助结构）
- F-034: nodes.py:1-56 — RST 解析采用多遍 CST（具体语法树）方法，不追求完全兼容 RST 规范，以保留原始信息和支持 per-section 灵活解析规则为目标
- F-035: nodes.py:37-39 — 高层 section/block 拆分基于 Line/lines 对象，包装 str 并跟踪原始行号和缩进/反缩进操作
- F-036: gen.py 使用 tree-sitter + py-tree-sitter-rst 进行 RST 语法解析（CLAUDE.md 明确说明不使用 tree_sitter_languages 或 tree-sitter-language-pack）

## 存储与图数据库

- F-037: graphstore.py:18-37 — SQLite 图数据库 schema：nodes 表（id, package, version, category, identifier, has_blob, digest，UNIQUE 约束四元组）、links 表（source→dest，外键 CASCADE 删除）、两个索引（idx_links_dest、idx_nodes_pkg_cat_ident）
- F-038: graphstore.py:40-46 — SQLite PRAGMA 配置：foreign_keys=1、journal_mode=WAL、synchronous=NORMAL、cache_size=-65536（64MB）、mmap_size=268435456（256MB）
- F-039: graphstore.py:8-10 — 使用 BLAKE2b-16（16 字节摘要）作为内容指纹，非安全用途，比 SHA-256 更快
- F-040: graphstore.py:16 — 全局数据库路径默认 `~/.papyri/ingest/papyri.db`
- F-041: graphstore.py:49-53 — Key 命名元组：(module, version, kind, path) 四元组唯一标识一个文档节点
- F-042: graphstore.py:56-80 — GraphStore 抽象了文件系统 blob 存储 + SQLite 图索引，文件系统是 blob 内容的可信源，SQLite 是图结构的可信源

## TypeScript Ingest 管道

- F-043: ingest.ts:1-20 — Ingester 类是 Python crosslink.py 的 TypeScript 等效实现，接受解码后的 Bundle 节点，通过 BlobStore + GraphDb 抽象写入交叉引用图
- F-044: ingest.ts:25 — 使用 cbor-x 库进行 CBOR 编解码
- F-045: ingest.ts:26 — 使用 @noble/hashes/blake2b 计算 BLAKE2b 摘要（与 Python 端一致）
- F-046: ingest.ts:27 — 使用 better-sqlite3 进行 SQLite 操作（同步 API）
- F-047: ingest.ts:39 — BLOB_CONCURRENCY=100（bundle flush 时的并发 blob 写入数）
- F-048: ingest.ts:42 — DB_CHUNK_SIZE=500（单批事务的最大语句数，保持事务边界）
- F-049: ingest.ts:49-60 — VOLATILE_FIELDS_BY_TYPE 定义易变字段：IngestedDoc 的 item_line/item_file（源码行号/路径因环境不同而变化）、Figure 的 value（图片资产非确定性）、Image 的 url，计算内容摘要前这些字段置为 null
- F-050: graph-db.ts:19-32 — GraphDb 接口定义异步方法：run、get、all、batch（原子批量事务）、clear（清空所有数据）、close
- F-051: graph-db.ts:38-73 — SqliteGraphDb 将 better-sqlite3 的同步调用包装为 async 接口，batch 方法使用 db.transaction 保证原子性，clear 方法按顺序删除 links→nodes→bundles

## Viewer 前端渲染

- F-052: xref.ts:1-16 — CrossRef 解析采用两阶段模式：（1）页面预先收集所有 CrossRef，`await resolveRefs(graphDb, refs)` 一次性批量查询图数据库，构建同步的 XRefResolver 闭包；（2）Astro/React 组件在渲染时调用同步闭包解析链接。解决了模板深层循环中无法 await 的问题
- F-053: xref.ts:56-57 — "to-resolve" 和 "current-module" 是 gen 时的占位符，不参与图查询
- F-054: render-node.ts:1-7 — renderNode 是服务端 IR 节点渲染器，单异步函数按 __type 分发返回 HTML 字符串，与 IrNode.astro 组件逻辑镜像
- F-055: render-node.ts:23-29 — escapeHtml 函数实现 HTML 转义（&<>"）
- F-056: render-node.ts:45-56 — unresolvedRefDebug 为未解析的 CrossRef 生成 data-debug 属性（CSS hover 提示）和 data-ref-* 属性（devtools 检查），包含 module/version/kind/path 四个字段的调试信息
- F-057: render-node.ts:13 — 使用 papyri-ingest/url-safety 的 isSafeUrl 进行 URL 安全检查（与 Python 端 pack.py 对应）

## 数据格式双轨制

- F-058: CLAUDE.md 明确说明：bundle 目录（~/.papyri/data/<pkg>_<ver>/）使用 JSON 格式（人类可读，便于检查和调试）；.papyri 制品使用 gzip 压缩的 CBOR 格式（传输和存储格式）；ingest/viewer 层只接受 CBOR，不接受 JSON
- F-059: CLAUDE.md 说明：graphstore 是派生缓存，`_raw/<pkg>/<ver>.papyri.gz` 原始归档是唯一权威 IR，所有图存储内容可通过 POST /api/reingest 从原始归档重建

## Python-Typescript 跨语言架构

- F-060: papyri/ 目录（Python）负责 IR 生成（gen）和 CLI 操作；ingest/ 目录（TypeScript papyri-ingest 包）负责服务端摄取管道；viewer/ 目录（TypeScript Astro + React islands）负责 Web 渲染
- F-061: ingest/ 有独立的 package.json、tsconfig.json、eslint 配置和 tests/ 目录，作为独立的 npm 包发布
- F-062: viewer/ 使用 Astro 框架（@astrojs/node，output: "server"），运行在 Node.js 上，支持本地开发和 VPS 部署
- F-063: viewer/src/lib/ir-reader.ts 被指定为 IR 变更的"减震器"（shock absorber）：IR 格式变化时修复首先落在 ir-reader.ts，而非分散在各组件中
- F-064: 包通过 pnpm workspace 管理（pnpm-workspace.yaml），ingest 和 viewer 作为工作区包

## 安全设计

- F-065: pack.py:35-46 — unpack 时路径遍历防护
- F-066: pack.py:49-64 + render-node.ts:13 — Python 和 TypeScript 两端都实现 URL 安全检查（禁止 javascript:/data: 等危险 scheme）
- F-067: ingest/src/url-safety.ts 提供 TypeScript 端的 URL 安全验证（与 Python 端 _is_safe_url 对应）

## 编码约定

- F-068: CLAUDE.md 要求使用 assert 表达内部不变量（不替换为 raise），显式 raise 仅用于系统边界的输入验证
- F-069: CLAUDE.md 要求 CLI 命令函数内部保持惰性导入（`papyri --help` 快速启动）
- F-070: CLAUDE.md 明确禁止：Python 端渲染、papyri ingest CLI 命令、JupyterLab 扩展
- F-071: CLAUDE.md 说明早期 Cloudflare Workers（R2+D1）目标已放弃（ingest 延迟过高），存储抽象保留以便未来切换后端
