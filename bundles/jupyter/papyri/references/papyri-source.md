---
type: Reference
title: Papyri Python 核心包源码信源
description: Papyri Python 包（papyri/）核心模块源码索引，覆盖 IR 生成、节点类型、配置系统等
tags: [papyri, python, source, core]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-repo
    resource: https://github.com/carreau/papyri
    title: Papyri GitHub Repository
---

## Papyri Python 包核心模块索引

源码路径：`external/libs/jupyter/papyri/papyri/`

### 入口与 CLI

| 文件 | 职责 |
|------|------|
| `__init__.py` | Typer CLI 应用入口，注册所有子命令（gen/upload/pack/unpack/find/describe/debug/diff/about/bootstrap） |
| `__main__.py` | 允许 `python -m papyri` 执行 |
| `cli/gen.py` | `papyri gen` 子命令，从 TOML 配置生成 DocBundle |
| `cli/upload.py` | `papyri upload` 子命令，PUT 上传到 viewer `/api/bundle` |
| `cli/pack.py` | `papyri pack` 子命令，将 DocBundle 打包为 `.papyri` 制品 |
| `cli/unpack.py` | `papyri unpack` 子命令，解包 `.papyri` 制品为 JSON 目录 |
| `cli/find.py` | `papyri find` 子命令 |
| `cli/describe.py` | `papyri describe` 子命令 |
| `cli/debug.py` | `papyri debug` 子命令 |
| `cli/diff.py` | `papyri diff` 子命令 |
| `cli/about.py` | `papyri about` 子命令 |
| `cli/bootstrap.py` | `papyri bootstrap` 子命令 |

### IR 节点类型系统

| 文件 | 职责 |
|------|------|
| `nodes.py` | 全部 IR 节点类型定义（Text/Paragraph/Section/Code/Admonition/RefInfo/CrossRef 等 50+ 节点类） |
| `node_base.py` | Node 基类、CBOR 序列化、@register/@debug 装饰器、validate 校验 |
| `node_serializer.py` | 节点递归序列化辅助 |
| `serde.py` | 通用 dataclass JSON/CBOR 双向序列化（get_type_hints/deserialize） |

### IR 生成管线

| 文件 | 职责 |
|------|------|
| `gen.py` | 核心 IR 生成器（gen_main 函数），遍历 API、执行 doctest、输出 DocBundle 目录 |
| `doc.py` | GeneratedDoc 数据类——每个 API 对象的文档容器；_OrderedDictProxy 保持 section 顺序 |
| `tree.py` | RST→IR 访问者（GenVisitor），处理 directive 分发 |
| `ts.py` | tree-sitter RST 解析器包装 |
| `tokens.py` | RST 词法分析 token 类型与脚本解析 |
| `directives.py` | RST 指令注册表（drop/code_handler 等内置处理器） |
| `signature.py` | Python 函数签名解析（Signature 类、SignatureNode） |
| `numpydoc_compat.py` | NumPy 风格 docstring 解析兼容层 |
| `toc.py` | 目录树（TocTree）构建 |
| `examples.py` | 示例代码执行辅助 |
| `executors.py` | Doctest/示例执行器（BlockExecutor） |

### 打包与存储

| 文件 | 职责 |
|------|------|
| `bundle.py` | Bundle 顶层 Node（pack_format_version/ir_schema_version/api/narrative/examples/assets/toc），BundleManifest JSON 桥接 |
| `pack.py` | `.papyri` 制品构建：CBOR 编码 + gzip 压缩，确定性输出（canonical CBOR + zero-mtime） |
| `graphstore.py` | Python 端只读 GraphStore（SQLite blob+graph 索引），Key 命名元组 (module,version,kind,path) |
| `crosslink.py` | 摄取后的只读交叉引用访问（IngestedDoc） |

### 配置与工具

| 文件 | 职责 |
|------|------|
| `config.py` | 文件系统路径常量（base_dir=~/.papyri/、data_dir、ingest_dir、user_config_path），ensure_dirs() |
| `config_loader.py` | TOML 配置加载（Config dataclass、load_configuration） |
| `user_config.py` | 用户配置管理 |
| `utils.py` | 工具函数（Canonical/FullQual/dedent_but_first/full_qual/obj_from_qualname/strip_clinic_signature） |
| `errors.py` | 自定义异常（IncorrectInternalDocsLen/NumpydocParseError/TextSignatureParsingFailed） |
| `error_collector.py` | 错误收集器（ErrorCollector） |
| `_progress.py` | Rich 进度条自定义列 |

### 关键事实

- 版本：`__version__ = "0.0.10"`
- Python 要求：`>=3.13`（CI 运行在 3.14）
- 构建系统：flit_core
- CLI 入口：`papyri = "papyri:app"`（typer.Typer 应用）
- RST 解析：py-tree-sitter-rst（tree-sitter >= 0.24）
- 序列化：JSON（bundle目录，人类可读）→ CBOR（.papyri制品，压缩传输）
- 编码规范：ruff format/lint + mypy 严格模式
