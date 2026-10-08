---
type: Concept
title: 声学生成：flow matching 与 DiT 估计器
description: ConditionalCFM 的 L1 损失/训练 CFG 丢弃/欧拉采样，DiT(depth=13)+WaveNet 末层的估计器结构，以及 MaskedDiffWithXvecConfig 各配置键的语义。
tags: [confucius4-tts, tts, flow-matching, dit, diffusion, cfm]
generated: { by: "reference_agent/trae-solo", at: "2026-09-09T00:00:00Z" }
verified: { by: "process:source-reading-v", at: "2026-09-09T00:00:00Z" }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: Confucius4-TTS 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: Confucius4-TTS 核心洞察与知识地图
---

# 声学生成：flow matching 与 DiT 估计器

S2A（semantic-to-acoustic）段把 T2S 输出的离散语义 token 一次性扩散生成为 80 维 mel。其核心是 `MaskedDiffWithXvec` 模块：masked 指训练期 prompt 掩码机制，xvec 指说话人向量条件。本篇拆解其内部三个构件：配置、条件流匹配器 ConditionalCFM、以及 DiT 估计器。

## 配置键语义

`MaskedDiffWithXvecConfig`（confuciustts/flow/flow.py）默认值（F-c4t-021）按职责可分六组：

| 组 | 键 | 默认值 |
|---|---|---|
| 输入输出 | input_size / output_size | 512 / 80（mel 维度） |
| 条件 | spk_embed_dim / semantic_embed_dim / lm_latent_dim | 192 / 1024 / 1280 |
| 语义嵌入 | semantic_codebook_size / semantic_codebook_dim / semantic_output_dim | 8192 / 8 / 1024 |
| 长度调节 | lr_channels / lr_sampling_ratios / lr_out_channels / lr_in_channels | 512 / (1,1,1,1) / 512 / 1024 |
| CFM | cfm_sigma_min / cfm_training_cfg_rate / cfm_inference_cfg_rate / cfm_t_scheduler | 1e-6 / 0.2 / 0.7 / "linear" |
| 估计器 | estimator_hidden_dim / estimator_num_heads / estimator_depth / estimator_final_layer / estimator_wavenet_num_layers | 512 / 8 / 13 / "wavenet" / 8 |

推理配置 inference_config.yaml 的 s2a_model 段只暴露 6 键（input_size=512、output_size=80、spk_embed_dim=192、semantic_embed_dim=1024、lm_latent_dim=1280、estimator_mlp_ratio=3.0）（F-c4t-061），其余取源码默认——阅读部署配置时须以源码默认补全。

## ConditionalCFM：训练与采样

`ConditionalCFM`（confuciustts/flow/flow_matching.py）是条件流匹配器（F-c4t-025）：

- **训练**：`compute_loss` 使用 L1 loss，并做训练 CFG 条件丢弃（cfm_training_cfg_rate=0.2）；
- **采样**：`forward(mu, x_lens, prompt, spks, n_timesteps=25, inference_cfg_rate=0.7, temperature=1.0)` 经 `solve_euler` 欧拉求解；CFG 时将 batch 翻倍拼接 conditional/unconditional 两支。

默认 25 步欧拉采样是速度与质量的折中：flow matching 的线性 t 调度（cfm_t_scheduler="linear"）使欧拉步进在中等步数下即可逼近目标分布。推理 CFG 率 0.7 与训练丢弃率 0.2 的不对称设计详见 [01 条件化机制](/concepts/01-conditioning.md)。

## DiT 估计器：13 层 Transformer + WaveNet 末层

速度场的估计器是 `DiT`（confuciustts/flow/DiT/dit.py），构造签名（F-c4t-028）：

```python
DiT(hidden_dim=512, num_heads=8, depth=13, mel_dim=80, mu_dim=512,
    spk_dim=192, long_skip_connection=True, max_seq_len=4096,
    ..., final_layer="wavenet", ...)
```

`flow/DiT/modules.py` 提供全套组件类（F-c4t-029）：RMSNorm、AdaptiveLayerNorm、FeedForward、Attention、DiTBlock、FinalLayer、SinusPositionEmbedding、TimestepEmbedding。其中 AdaptiveLayerNorm 是扩散模型的标准做法：把时间步嵌入注入归一化层的仿射参数。

条件入口由 `InputEmbedding` 承担：将 x、cond、mu_proj、spks 拼接后投影（F-c4t-027）——四个输入即 mel 噪声、条件、长度调节后的 mu 投影、说话人嵌入，与 [01 条件化机制](/concepts/01-conditioning.md) 的条件构件一一对应。

末层由 `final_layer="wavenet"` 指定：flow/wavenet.py 定义 WeightNormConv1d 与 WN，estimator_wavenet_num_layers=8（F-c4t-021、F-c4t-030）。选择 WaveNet 卷积栈收尾，在 mel 帧序列上做局部时序精修，弥补 Transformer 对局部波形细节的弱表达。

## 推理调用链

`MaskedDiffWithXvec.inference(semantic_token, lm_latent, prompt_feat, embedding, target_feat_len, n_timesteps=25, inference_cfg_rate=0.7)`（F-c4t-024）是 S2A 对外的推理接口：semantic_token 与 lm_latent 来自 T2S（`return_latent=True`，F-c4t-015、F-c4t-010），prompt_feat 是参考 mel 特征，embedding 是说话人向量，target_feat_len 即 [02 长度调节](/concepts/02-length-regulation.md) 中的 `int(T * 1.72)` 启发式给出。

## 替换与调优边界

级联架构的好处在此充分体现：估计器可独立替换——depth 决定容量、final_layer 可在 "wavenet" 与其他实现间切换、estimator_mlp_ratio 控制前馈层宽度；CFM 侧可调 sigma 下限与步数。但须保持段间契约（语义 token + lm_latent 入，80 维 mel 出）不变，且任何训练侧改动须与 [06 两阶段训练](/concepts/06-training.md) 的冻结策略协同。

## 相关概念

- [01 条件化机制：prompt 掩码、说话人与风格嵌入](/concepts/01-conditioning.md)
- [02 长度调节与时长启发式](/concepts/02-length-regulation.md)
- [06 两阶段训练与微调体系](/concepts/06-training.md)
