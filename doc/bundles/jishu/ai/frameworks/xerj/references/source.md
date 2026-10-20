---
type: Reference
title: XERJ 信源登记
description: XERJ 源码快照登记——仓库身份、提交哈希、目录规模、关键文件清单与信源路径稳定性判定
tags: [xerj, 信源登记, rust, 源码快照]
generated: { by: source-code-to-okf-wiki/R, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-repo
    resource: https://github.com/xerj-org/xerj
    title: XERJ 官方仓库（xerj-org/xerj）
  - id: xerj-local-snapshot
    resource: /references/source.md
    title: 本知识包采集所依据的本地源码快照
---

# XERJ 信源登记

## 仓库身份

| 项 | 值 |
|---|---|
| 上游仓库 | `https://github.com/xerj-org/xerj` |
| 本地快照路径 | `external/dao/search/xerj`（工作区内相对路径，非 `file:///` 绝对路径） |
| 提交哈希 | `51ff219276d7e55d9d85b4938e8b94f235f9d099` |
| 提交时间 | 2026-10-19 23:05:42 -0500 |
| 提交标题 | `fix(query): parse standalone and infix operators in simple_query_string (#1751) (#1804)` |
| `git describe` | `v1.0.0-rc.97-38-g51ff2192` |
| 许可证 | Apache-2.0（`LICENSE`，`NOTICE`） |
| 工作树状态 | 采集时 `git status --porcelain` 为空（无未提交改动） |

> **版本固定性说明（信源稳定性门 G0）**：本次采集固定在**具体 commit 哈希** `51ff2192…` 上，而非 release tag。`git describe` 输出的 `v1.0.0-rc.97-38-g51ff2192` 表示当前提交位于 `v1.0.0-rc.97` 标签之后 38 个提交，**该提交本身不可变**（哈希即内容地址），但它不是任何已发布 tag 的快照。若后续需要复现"发布版"行为，应另行采集对应 tag 的哈希；本知识包的所有事实均以 `51ff2192…` 为准。

## 目录规模（脚本计数）

计数口径：以 `engine/` 目录为工程根，`*.rs` 为源码文件，逐文件累加行数。

| 项 | 值 | 计数口径 |
|---|---|---|
| `engine/crates/` 下的 crate 数 | **18** | `engine/crates` 下的直接子目录计数 |
| `engine/` 下 Rust 源文件数 | **552** | 递归 `*.rs` 文件计数（含 `tests/`、`fuzz/`） |
| `engine/` 下 Rust 代码行数 | **521,684** | 逐文件 `Get-Content \| Measure-Object -Line` 累加 |
| `xerj-autoindex/src/extract/` 抽取器模块数 | **25** | `extract/` 目录下的 `*.rs` 文件数减去 `mod.rs` 本身 |
| `sniff::Family` 变体数 | **28** | 解析 `sniff.rs` 中 `pub enum Family {…}` 的变体名 |
| MCP 工具数 | **17** | `landing/docs/agents/schemas/mcp-tools.json` 的 `tools[]` 长度 |
| 第二大脑边检测器数 | **9** | `detect::default_detectors()` 返回的注册项数 |
| 顶层子命令数 | **14** | `xerj-server/src/main.rs` 中 `is_top_level_command()` 的字符串匹配项 |
| `docs/recipes/*.md` 数量 | **19** | 目录下 `*.md` 文件计数（含 `README.md`） |
| `docs/*.md` 顶层文档数 | **24** | `docs/` 目录下 `*.md` 文件计数 |
| ES 兼容性 YAML 套件目录数 | **15** | `engine/tests/es-compat-yaml/yaml/` 下的子目录计数 |
| ES 兼容性 YAML 用例文件数 | **221** | 该目录下递归 `*.yml` 文件计数 |

### 各 crate 代码规模（脚本计数，行数）

| crate | 源文件数 | 行数 | crate | 源文件数 | 行数 |
|---|---:|---:|---|---:|---:|
| `xerj-autoindex` | 97 | 116,098 | `xerj-hub` | 15 | 17,182 |
| `xerj-engine` | 30 | 112,622 | `xerj-common` | 27 | 16,760 |
| `xerj-api` | 25 | 73,535 | `xerj-storage` | 14 | 24,454 |
| `xerj-query` | 9 | 12,902 | `xerj-cluster` | 13 | 5,312 |
| `xerj-fts` | 6 | 11,900 | `xerj-console-api` | 29 | 8,537 |
| `xerj-server` | 7 | 10,420 | `xerj-mcp` | 5 | 5,876 |
| `xerj-ai` | 9 | 3,883 | `xerj-vector` | 6 | 3,548 |
| `xerj-rerank` | 2 | 2,730 | `xerj-wasm` | 3 | 2,500 |
| `xerj-compress` | 5 | 2,272 | `xerj-logs` | 5 | 1,550 |

## 关键文件清单（本知识包引用的源码入口）

| 路径（相对仓库根） | 行数 | 作用 |
|---|---:|---|
| `AGENTS.md` | — | 上游自带的智能体指南：定位、地面规则、autoindex 人类运行协议、MCP 工具说明 |
| `README.md` | 503 | 产品故事、参考编码实测数据、ES 兼容与基准摘要 |
| `docs/ARCHITECTURE.md` | 162 | crate 布局、搜索路径、摄取路径、恢复流程、线协议一致性说明 |
| `docs/WHY_XERJ.md` | — | 设计理念与取舍理由 |
| `docs/SECOND_BRAIN.md` | — | 第二大脑（关系层）契约：脑/边/节点、检测器、双跳上限 |
| `docs/RERANK.md` | — | `rerank` 第二阶段重排的外呼边界与失败策略 |
| `docs/SECURITY_MODEL.md` | — | 认证、`127.0.0.1` 绑定默认值、`.xerj-memory-*` 保留命名空间 |
| `landing/llms.txt` | 262+ | 面向智能体的机器可读能力参考，内含"诚实的坑"清单 |
| `tools/xerj-code/SKILL.md` | 557 | 参考编码工作流、语料库纪律、MEATL 输出格式、测量方法学 |
| `engine/crates/xerj-mcp/src/lib.rs` | 3,710 | MCP 服务器：工具定义、认证解析、JSON-RPC 循环 |
| `engine/crates/xerj-mcp/src/token_budget.rs` | 809 | 五个检索工具的 `max_tokens` 硬预算 |
| `engine/crates/xerj-mcp/src/map.rs` | 942 | `xerj_map` 工具：autoindex 目录的按索引字段图 |
| `engine/crates/xerj-mcp/src/hub.rs` | 404 | 三个 `xerj_hub_*` 工具 |
| `engine/crates/xerj-autoindex/src/lib.rs` | 12,362 | autoindex 客户端主流程 |
| `engine/crates/xerj-autoindex/src/cli.rs` | 3,072 | autoindex 命令行帮助文本（阶段序列、决策门、退出码） |
| `engine/crates/xerj-autoindex/src/sniff.rs` | 4,514 | 基于内容的格式识别（`Family` 枚举） |
| `engine/crates/xerj-autoindex/src/extract/mod.rs` | 1,180 | 抽取器总入口、`RawRecord`、`FieldOrigin`、分段常量 |
| `engine/crates/xerj-autoindex/src/gate.rs` | 886 | 10 分钟决策门（`EXIT_NEEDS_DECISION = 4`） |
| `engine/crates/xerj-autoindex/src/estimate.rs` | 783 | 阶段 A 测量与耗时区间估算 |
| `engine/crates/xerj-autoindex/src/detect/mod.rs` | 1,088 | 边检测器注册表与 `edge_id` 派生函数 |
| `engine/crates/xerj-ai/src/embedder.rs` | 874 | 统一嵌入后端（词法/代理/神经/ONNX 四选一） |
| `engine/crates/xerj-ai/src/local.rs` | 208 | 内置词法特征哈希嵌入器（384 维） |
| `engine/crates/xerj-vector/src/hnsw.rs` | 1,817 | HNSW 图索引（M=16、ef_construction=200、flat-slab 布局） |
| `engine/crates/xerj-server/src/main.rs` | 4,109 | 服务器入口、三监听端口、顶层子命令分派、jemalloc 配置 |
| `engine/crates/xerj-common/src/xccode/mod.rs` | 2,146 | 参考编码的代码检索管线 |
| `engine/crates/xerj-query/src/ast.rs` | 1,380 | 查询 AST（`QueryNode` 树） |
| `engine/crates/xerj-query/src/parser.rs` | 6,634 | ES JSON → AST 解析器 |

## 信源路径稳定性判定（G0）

| 检查项 | 结论 |
|---|---|
| 信源类型 | 本地 Git 克隆（工作区内 `external/` 目录），非临时目录、非系统 Temp |
| 引用形式 | 本知识包所有源码引用均写为**仓库相对路径 + 行号**（如 `engine/crates/xerj-mcp/src/lib.rs:12`），不使用 `file:///` 绝对路径，也不引用 `external/` 之外的临时克隆 |
| 版本可复现性 | 以 commit 哈希 `51ff2192…` 固定；上游推进 `main` 不影响本束事实的复现 |
| 清理影响 | 删除本地克隆不会导致本束链接断裂（无绝对路径依赖） |
| 交叉引用 | 事实清单见 [facts.md](facts.md)；架构洞察见 [insights.md](insights.md) |

## 相关参考

- [事实清单](facts.md)：本束全部编号事实（F-001 起）
- [架构洞察与知识地图](insights.md)：洞察四元组与学习路径设计
- [领域背景与研究过程](background-research.md)：检索栈背景、成本模型与信源引用
- [References 索引](index.md)：本目录汇总
