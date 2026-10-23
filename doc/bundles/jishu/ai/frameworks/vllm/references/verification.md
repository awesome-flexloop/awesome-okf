---
type: Reference
title: "核验记录：本地源码 × 官网交叉验证"
description: "vLLM 知识包的本地源码检出与 vllm.ai 官网/文档站交叉核验记录——三处口径差异（版本号、Python 要求、模型计数）的解释，以及关键事实的双源确认清单
tags: [vllm, verification, cross-check, source-reconciliation]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/V, at: "2026-10-22T17:10:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /source-map.md
    title: 本地源码检出（v0.32.1rc0-283，2026-10-22）
  - id: website
    url: https://docs.vllm.ai/en/latest/
    title: 官网文档站（stable 0.32.0，2026-10-22 抓取）
---

# 核验记录：本地源码 × 官网交叉验证

本知识包采用**双信源**：本地源码检出（一手代码）与 vllm.ai 官网/文档站（一手口径）。二者在三处存在**口径差异**，均以时点/统计口径解释，无实质冲突。

## 口径差异及解释

| # | 差异项 | 本地源码 | 官网 | 解释 |
|---|--------|---------|------|------|
| 1 | 版本号 | `v0.32.1rc0-283`（release candidate，2026-10-22 提交） | stable `0.32.0` | 本地检出超前于 stable 一个 RC 周期；功能口径以本地检出为准，对外版本号引用官网 stable（F-002/F-003） |
| 2 | Python 要求 | quickstart 3.11–3.14 | 安装页 3.10+（3.12+ 推荐） | 本地 quickstart 为最新开发版口径，官网为稳定版兼容口径（F-008） |
| 3 | 模型架构计数 | 注册表 346 条架构 | "200+ model architectures" | 注册表按架构登记（含 spec-decode/reward 等），官网 200+ 为可运行架构的对外表述；统计对象不同（F-081/F-082） |

## 关键事实双源确认

| 事实 | 源码侧 | 官网侧 | 结论 |
|------|--------|--------|------|
| V1 为唯一引擎（F-016） | `vllm/v1/` 为唯一引擎目录，无 V0 运行时 | docs/usage/v1_guide.md 明确 V0 废弃 | ✅ 一致 |
| 进程模型（F-010/F-011） | `vllm/v1/engine/core.py` 类结构 | docs/design/arch_overview.md 计数公式 | ✅ 一致 |
| chunked prefill 默认开（F-019/F-046） | `SchedulerConfig.enable_chunked_prefill: bool = True` | docs/usage/v1_guide.md 默认开启清单 | ✅ 一致 |
| 注册表计数（F-081） | registry.py 统计 346 | supported_models.md "200+" | ⚠️ 口径差异 #3，已解释 |
| 结构化输出 API（F-143） | `StructuredOutputsParams` in sampling_params.py | docs/features/structured_outputs.md 迁移表 | ✅ 一致（guided_* v0.12 移除） |
| 投机解码方法（F-111/F-114） | `vllm/v1/spec_decode/` 文件清单 | docs/features/speculative_decoding/ 选型表 | ✅ 一致 |
| 量化兼容表（F-097） | quantization/ 目录实现 | docs/features/quantization/README.md 表格 | ✅ 一致（时点 2026-10） |
| benchmark 工具族（F-147） | `vllm/entrypoints/cli/benchmark/` | docs/benchmarking/cli.md | ✅ 一致 |

## 未采纳/待核项

- **官网 blog 约 159 篇**：仅采架构总览篇（2025-09-05 Anatomy of vLLM）与首页/Community 口径，其余博文未逐篇核验；性能数字一律引用官方博客测试条件，不代表通用结论。
- **硬件插件生态**（Ascend/TPU/Gaudi/Spyre/Metal）为仓库外独立项目，本包只做索引式介绍（F-121/F-122），细节以各插件仓库为准。
- **docs/design/paged_attention.md**：官方自述为历史文档（描述论文时代实现），本包引用时已标注，现实现口径以 `csrc/` 与 `vllm/v1/attention/backends/` 为准（F-058）。
- **动态数字**（Star/贡献者/兼容表）带 2026-10-22 时点，`stale_after: 2027-04-22` 前复核。

## 核验方法

1. 源码侧：文件路径 + 行号级 grep/读取（见 [facts.md](facts.md) 来源列）。
2. 官网侧：WebFetch 抓取 docs.vllm.ai/en/latest/ 对应页面，与本地 `docs/`（mkdocs 构建源）同源互校。
3. 差异处理：以本地检出为准并标注时点；官网动态数字仅作对外引用口径。
