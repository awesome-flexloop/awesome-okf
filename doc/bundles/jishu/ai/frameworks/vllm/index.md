okf_version: "0.2"
type: bundle
title: "vLLM：高吞吐 LLM 推理与服务平台"
description: "vLLM v0.32 源码与官网教程——PagedAttention、continuous batching、V1 引擎架构（API Server/EngineCore/Worker 进程模型）、OpenAI 兼容服务、量化、投机解码、TP/PP/DP/EP 分布式与 PD 分离，覆盖安装部署、核心模块、典型场景与进阶主题"
tags: [vllm, llm-inference, llm-serving, paged-attention, continuous-batching, openai-compatible, quantization, speculative-decoding, distributed-inference, 源码教程]
generated:
  by: seven-concepts-cmd+source-code-to-okf-wiki
  at: "2026-10-22T16:40:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-22T17:10:00+08:00"
status: stable
stale_after: "2027-04-22"
sources:
  - id: local-source
    resource: vllm-project/vllm @ 7d5335936c40306063a29fc4e2ccbe71b280e40c
    title: 本地源码检出（git describe: v0.32.1rc0-283-g7d5335936c，2026-10-22）
  - id: github-repo
    url: https://github.com/vllm-project/vllm
    title: vLLM 官方仓库
  - id: website-home
    url: https://vllm.ai/
    title: vLLM 官网首页
  - id: docs-site
    url: https://docs.vllm.ai/en/latest/
    title: vLLM 官方文档站
  - id: arch-overview
    url: https://docs.vllm.ai/en/latest/design/arch_overview/
    title: Architecture Overview（本地 docs/design/arch_overview.md 同源）
  - id: anatomy-blog
    url: https://vllm.ai/blog/2025-09-05-anatomy-of-vllm
    title: Inside vLLM: Anatomy of a High-Throughput LLM Inference System（2025-09-05）
  - id: paper
    url: https://arxiv.org/abs/2309.06180
    title: Efficient Memory Management for LLM Serving with PagedAttention（SOSP 2023）
  - id: blog-index
    url: https://vllm.ai/blog
    title: vLLM 博客索引（约 159 篇）

---

# vLLM：高吞吐 LLM 推理与服务平台

vLLM 官方自我定位是 **"A high-throughput and memory-efficient inference and serving engine for LLMs"**（高吞吐、省显存的 LLM 推理与服务平台，F-001）。它最初由 UC Berkeley Sky Computing Lab 开发，现为 PyTorch Foundation 旗下项目，社区超过 2000 名贡献者（F-005），GitHub 星标 95K+（2026-10-22 官网时点，F-006）。

本知识包基于**本地源码检出**（v0.32.1rc0-283，commit `7d53359`，2026-10-22；F-002）与 **vLLM 官网/文档站**（stable 0.32.0；F-003）双信源交叉整理：源码侧给出模块级事实，官网侧给出口径与版本状态，二者不一致处以源码检出为准并标注时点。

> **类型**：源码学习教程（可操作）。所有命令与代码示例可在 vLLM v0.32.x 环境复现；版本相关数字均带时点。
> **信源距离**：本地源码（第一手）+ 官网/文档站（第一手）+ SOSP 2023 论文与架构博客（第一手阐释）。
> **核验结论**：本地源码与官网在版本号（0.32.1rc0 vs 0.32.0 stable）、Python 版本要求（3.11–3.14 vs 3.10+/3.12+ 推荐）、模型架构计数（注册表 343 条 vs 官网 "200+"）三处存在**口径差异**，均以时点/统计口径解释，无实质冲突（见 [references/verification.md](references/verification.md)）。

## 本文概要

vLLM 解决的核心问题是 **LLM 服务的显存与吞吐效率**：以 PagedAttention 管理 KV cache（F-030），以 continuous batching 混合调度 prefill/decode 请求（F-034），以 V1 多进程引擎架构分离 API、调度与 GPU 执行（F-010）。它对外提供两个主入口——离线推理 `LLM` 类与在线服务 `vllm serve`（OpenAI 兼容 API，F-060），向下通过 Executor/Worker/ModelRunner 驱动 GPU，向上支撑 200+ 开源模型架构（F-081）。

## 阅读路径

1. [00 整体架构与项目身份](concepts/00-overview.md)——身份卡片、两大入口、版本谱系与生态位
2. [01 快速开始](concepts/01-quickstart.md)——安装 → 离线推理 → `vllm serve` 最小闭环
3. [02 安装与硬件平台](concepts/02-installation.md)——平台矩阵、安装方式、硬件插件生态
4. [03 架构总览](concepts/03-architecture.md)——V1 进程架构、类层次、请求生命周期
5. [04 调度与批处理](concepts/04-scheduling.md)——continuous batching、chunked prefill、调度策略
6. [05 KV 缓存与 PagedAttention](concepts/05-kv-cache.md)——block 池、前缀缓存、KV 量化与卸载
7. [06 执行层：Executor 与模型运行](concepts/06-execution.md)——Worker、ModelRunner、CUDA Graph、torch.compile
8. [07 配置体系](concepts/07-configuration.md)——EngineArgs → VllmConfig、常用参数速查
9. [08 在线服务与 API](concepts/08-online-serving.md)——OpenAI 兼容 API 全谱、chat 模板、鉴权与多模态
10. [09 模型支持](concepts/09-model-support.md)——架构注册表、Transformers backend、任务类型
11. [10 量化](concepts/10-quantization.md)——FP8/INT4/GPTQ/AWQ/GGUF 与硬件兼容
12. [11 投机解码](concepts/11-speculative-decoding.md)——EAGLE/MTP/ngram/suffix 与方法选型
13. [12 分布式推理与扩展](concepts/12-distributed.md)——TP/PP/DP/EP/CP 与多节点部署
14. [13 进阶主题](concepts/13-advanced.md)——PD 分离、结构化输出、LoRA、RL、插件系统

实战示例见 [examples/](examples/index.md)（离线推理、OpenAI 服务、结构化输出、基准测试四类典型场景）；编号事实清单见 [references/facts.md](references/facts.md)。

## 核心事实速查

| 项 | 值 | 出处 |
|----|-----|------|
| 官方定位 | 高吞吐、省显存的 LLM 推理与服务平台 | F-001 |
| 版本 | 本地检出 v0.32.1rc0-283（2026-10-22）；官网 stable 0.32.0 | F-002/F-003 |
| 许可证 | Apache-2.0 | F-004 |
| 出身 | UC Berkeley Sky Computing Lab；PyTorch Foundation 项目 | F-005 |
| 社区 | GitHub 95K+ Star、3.8K+ 贡献者（官网 2026-10 时点） | F-006 |
| 核心论文 | PagedAttention，SOSP 2023（arXiv 2309.06180） | F-007 |
| Python 要求 | 官网 3.10+（3.12+ 推荐）；本地 quickstart 3.11–3.14 | F-008 |
| 默认引擎 | V1（V0 已完全废弃，RFC #18571） | F-016 |
| 两大入口 | 离线 `LLM` 类；在线 `vllm serve <model>`（默认 :8000） | F-060/F-064 |
| 进程模型 | API Server + Engine Core（每 DP rank 1 个）+ GPU Worker（每 GPU 1 个）+ DP Coordinator | F-010 |
| 模型支持 | 注册表 121 文本生成 + 124 多模态 + 33 embedding + 65 spec-decode 架构；官网称 200+ | F-080/F-081 |
| 默认开启 | chunked prefill、prefix caching、CUDA graph（`--enforce-eager` 关闭） | F-019/F-033/F-052 |

## 阅读前必知的四条口径

1. **版本双时点**：本地源码检出为 `v0.32.1rc0-283`（release candidate，2026-10-22），官网 stable 为 `0.32.0`。本束功能口径以本地检出为准，版本号以官网 stable 为对外引用口径（F-002、F-003）。
2. **V0 已废弃**：v0.32 起 V1 是唯一引擎；本束所有架构描述均针对 V1，V0 遗留类（如 `LLMEngine` 兼容层）不再展开（F-016）。
3. **注册表计数 ≠ 模型数**：注册表按**架构**登记（343 条），官网 "200+ model architectures" 为可运行架构口径；二者统计对象不同（F-080、F-081）。
4. **动态数字带时点**：Star 数、贡献者数、性能数字均为抓取时点快照，引用须带日期（F-006）。

## 已知边界与时效

- 本束基于 2026-10-22 源码快照，`stale_after: 2027-04-22`；vLLM 版本迭代快（月均一个小版本），到期前或架构明显变化时复核。
- 性能数字（吞吐/延迟）一律引用官方博客的测试条件，**不代表通用结论**；选型以自有负载实测为准。
- 硬件插件生态（Ascend/TPU/Gaudi/Spyre 等）为仓库外独立项目，本束只作索引式介绍，细节以各插件仓库为准（F-122）。

## 信源与可信度

- 编号事实清单（F-001~F-155）：[references/facts.md](references/facts.md)
- 源码树结构与关键文件登记：[references/source-map.md](references/source-map.md)
- 本地源码与官网交叉核验记录：[references/verification.md](references/verification.md)

## 主题关联

- [llama.cpp 本地 LLM 推理](../llama-cpp-local-inference/index.md)：同门的消费级硬件本地推理框架，与本束的 GPU 服务化路线互补
- [tiktoken BPE 分词库](../tiktoken/index.md)：vLLM 输入处理所依赖的分词基础库
- [LangChain-AI LLM 应用框架](../langchain-ai/index.md)：上层应用框架，常以 vLLM 作为 OpenAI 兼容后端消费

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
