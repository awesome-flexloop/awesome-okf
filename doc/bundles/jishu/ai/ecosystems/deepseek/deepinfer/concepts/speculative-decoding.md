---
type: concept
scope: deepinfer
name: DSpark 推测解码
version: "0.1.0"
source: deepinfer/model_executor/models/mtp/, deepinfer/model_executor/layers/tilelang_ops/dflash.py, csrc/engine/mtp_varlen.hpp
description: DSpark 推测解码——DFlash 草稿模型、ConfidenceHead 接受率预测与变长验证调度
sources:
  - id: dspark-paper
    resource: https://arxiv.org/abs/2607.05147
    title: "DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation"
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# DSpark 推测解码

DSpark 是 DeepSeek 提出的投机解码算法框架。相比 DFlash 在输出的 base logits 上叠加**只依赖前一 token id 的低秩 logit bias**，用极轻量的串行修正补回相邻 token 的局部条件化信息，提升 draft 准确率。

---

## 一、组成部件

| 部件 | 位置 | 职责 |
|---|---|---|
| DFlash 草稿模型 | `deepinfer/model_executor/models/mtp/dflash.py`（392 行，`mtp/` 下唯一实现） | nextn 预测草稿 token |
| Next 预测头 | `DFlashNextPredictHeadHC`（`v4_modules/heads.py`） | nextn 预测头 |
| **ConfidenceHead** | `mtp/dflash.py` | 预测每个 draft token 的接受概率（输入 `n_embed + markov_rank`，输出 1 维接受概率） |
| 融合算子 | `confidence_head_fused`（`layers/tilelang_ops/dflash.py`） | TileLang 融合实现的 confidence head |
| 变长验证 | `csrc/engine/mtp_varlen.hpp` | 变长验证调度（含 `SamplerRuntimeEstimator` 滑窗中位数估计 sampler 耗时） |
| draft 信息池 | `layers/mtp_info_pool.py` | draft token 元信息池 |
| 专用 CUDA Graph | `worker/dflash_cuda_graph_runner.py` | DSpark 专用图捕获 |

## 二、变长验证（核心创新）

**问题**：不同请求、不同位置的 draft token 接受概率不同，固定长度验证会把验证算力浪费在低概率 token 上。

**方案**：DSpark 通过 Confidence Head 预测每个 draft token 的接受率，调度时把验证算力分配给**边际收益最高**的 token：

1. 线上部署时 draft 一次生成 5 个 token；
2. 根据 profile 出的硬件吞吐曲线与每个请求每个 draft token 的接受率，把各 draft token 按预期接受率排序；
3. 选取**有效吞吐最大的前缀子集**进行验证。

**收益**：相比固定验证 5 个 token，变长验证在线上部署场景吞吐提升 **6%**。

## 三、与异步调度的配合

ZOS（零开销调度）下，schedule(N+1) 执行时第 N 步的 confidence 尚未回传，CPU 无法预知逐请求验证长度。解法：

- CPU 调度时**只确定总预算**；
- 逐请求长度在 GPU 上由一个 TileLang kernel 重算（累乘、全局排序取 top-k、融合 remap scatter）；
- 结果回写 pinned buffer 供调度器消费。

## 四、用户开关与观测

| 环境变量 | 默认 | 含义 |
|---|---|---|
| `DEEPINFER_ENABLE_MTP_VARLEN` | 0 | DSpark 变长验证总开关 |
| `DEEPINFER_USE_NEXTN_DECODE` | 5 | 最大 draft 长度；设 0 关闭投机解码 |
| `DEEPINFER_MAX_BACKTRACKING_TOKENS` | nextn+1 | 验证回退上限 |
| `DEEPINFER_DFLASH_CONFIDENCE_HEAD_TEMPERATURE` | 1.0 | confidence head 温度（可逗号分隔 per-nextn 元组） |

验证结果经 `RequestOutput` 暴露（`_C/engine.pyi` 契约）：`confidence_score` / `draft_tok` / `accept_tok` 字段供上层统计接受率。`examples/offline_inference.py` 的输出即包含 `accept_rate` 字段（见[离线推理示例](../examples/offline-inference.md)）。
