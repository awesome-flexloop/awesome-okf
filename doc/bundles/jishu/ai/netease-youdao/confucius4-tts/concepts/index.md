# 概念文档

Confucius4-TTS 核心概念，共 7 篇，按"推理链路 → 条件化 → 生成机制 → 加速服务 → 训练"顺序组织。

## 推理链路

* [00 仓库全景与推理链路总览](00-overview.md) — 14 语言、安装依赖、三段级联链路（T2S/S2A/BigVGAN）、generate 参数全貌、inference_config.yaml 四段结构。
* [01 条件化机制：prompt 掩码、说话人与风格嵌入](01-conditioning.md) — prompt 0–30% 随机掩码、prompt_cond 可学习参数、Qwen3-TTS 说话人编码器、CAMPPlus 风格编码器、训练-推理 CFG 不对称。
* [02 长度调节与时长启发式](02-length-regulation.md) — int(T*1.72) 目标帧数启发式、InterpolateRegulator nearest 上采样、cross_fade/edge_fade 拼接、80 token 分段。
* [03 声学生成：flow matching 与 DiT 估计器](03-flow-matching.md) — ConditionalCFM L1 损失/训练 CFG 丢弃/欧拉采样、DiT(depth=13) + WaveNet 末层、配置键六组语义。

## 声码器与服务化

* [04 声码器与 BigVGAN 集成](04-bigvgan-vocoder.md) — Snake 激活、AMP 抗混叠 resblock、from_pretrained 加载、vocoder_path 替换边界。
* [05 vLLM 加速路径与服务化](05-vllm-serving.md) — 双后端分治对照表、patch_vllm 架构注册、generate_stream 流式切块、FastAPI/Gradio 两种服务化形态。

## 训练

* [06 两阶段训练与微调体系](06-training.md) — T2S/S2A 配置差异对照、四处置零冻结、EMA、w2v-bert 第 17 层条件、TSV 五列微调格式。

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-conditioning
02-length-regulation
03-flow-matching
04-bigvgan-vocoder
05-vllm-serving
06-training
```
