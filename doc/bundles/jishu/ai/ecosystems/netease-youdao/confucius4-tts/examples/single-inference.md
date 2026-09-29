---
type: Example
title: 单次推理全流程（HF 后端）
description: 基于 ConfuciusTTS（HF 后端）完成一次零样本合成的最小完整流程，含构造、generate 参数解读、raw 模式与分段控制。
tags: [confucius4-tts, tts, example, inference, huggingface]
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

# 单次推理全流程（HF 后端）

本例基于仓库自带的 example.py 思路（F-c4t-011），演示使用 HF 后端 `ConfuciusTTS` 完成一次零样本声音合成的最小完整流程。接口签名均忠实于 confuciustts/cli/inference.py 的源码（F-c4t-005、F-c4t-006）。

## 前置条件

- 已按 requirements.txt 安装依赖（torch==2.7.0、transformers==4.52.4 等，F-c4t-054），Python >= 3.10（F-c4t-002）；
- config/inference_config.yaml 的 paths 段已就绪：tokenizer_path=./checkpoints、w2v_bert_path=facebook/w2v-bert-2.0、vocoder_path=nvidia/bigvgan_v2_22khz_80band_256x（F-c4t-060）；
- 一段参考音频（prompt_wav），如 reference.wav。

## 完整代码

```python
import torch
import torchaudio
from confuciustts.cli.inference import ConfuciusTTS

# 1. 构造推理器：默认读取 config/inference_config.yaml
model = ConfuciusTTS(
    config_path="config/inference_config.yaml",  # 默认值，可省略
    t2s_checkpoint=None,                          # 默认从配置 paths 读取
    device="cuda" if torch.cuda.is_available() else "cpu",
)

# 2. 单次生成：返回 (sample_rate, audio_tensor)
sample_rate, audio = model.generate(
    "支持多种语言，轻松实现跨语种朗读。",
    "zh",
    "reference.wav",
    temperature=0.8,                 # T2S 自回归采样温度（F-c4t-006）
    n_timesteps=25,                  # S2A flow matching 欧拉步数
    inference_cfg_rate=0.7,          # 推理期 CFG 引导率
    max_text_tokens_per_segment=80,  # 长文本切段阈值
    cross_fade_duration=0.3,         # 段间交叉淡化
    verbose=True,
)

# 3. 保存
torchaudio.save("output.wav", audio.cpu(), sample_rate)
```

## 关键步骤说明

### 构造阶段加载了什么

`__init__(config_path, t2s_checkpoint, device)` 读取 YAML 配置后，依次装配三段构件：T2S 模型（Text2Semantic）、S2A 模型（MaskedDiffWithXvec）、BigVGAN 声码器（`BigVGAN.from_pretrained(paths["vocoder_path"], use_cuda_kernel=False)`，F-c4t-034）。传入 `t2s_checkpoint` 可覆盖配置中的检查点路径。

### generate 参数的四组语义

- **采样组**（temperature/top_p/top_k/num_beams/repetition_penalty/max_length）：控制 T2S 自回归解码。其中 repetition_penalty=10.0 很高，说明语义 token 序列极易出现重复退化；
- **扩散组**（n_timesteps/inference_cfg_rate）：控制 S2A 欧拉求解质量与条件引导强度，详见 [03 声学生成](/concepts/03-flow-matching.md)；
- **分段组**（max_text_tokens_per_segment=80）：文本超过 80 token 即切段，各段独立合成后拼接，详见 [02 长度调节](/concepts/02-length-regulation.md)；
- **拼接组**（cross_fade_duration/edge_fade_duration/edge_pad_duration）：段间过渡的淡化参数。

### raw 模式：拿到未拼接的分段结果

```python
sample_rate, segments = model.generate(
    long_text, "zh", "reference.wav", raw=True,
)
# segments: list[segment_audio]，不做 cross_fade 拼接（F-c4t-007）
```

`raw=True` 时返回各段音频列表，适用于自定义拼接/混音管线，也是注入自定义时长控制的挂接点（替换 `_synth_segment` 中的 `int(T * 1.72)` 启发式，F-c4t-009）。

### 语言选择

lang 取值对应 `LANGUAGE_TOKEN_MAP` 的 93 个键（含 zh/ja/ko/vi/th/id/ms/en/de/fr/es/pt/it/ru 等），推理时提示文本被格式化为 `f"You are a helpful assistant. {lang_token}:{text}"`，lang_token 形如"请用中文朗读接下来的文字"（F-c4t-008、F-c4t-059）。

## 常见调参起点

| 症状 | 建议调整 |
|---|---|
| 语义重复、卡顿 | 调高 repetition_penalty 或降低 temperature |
| 音色不像参考音频 | 确认参考音频质量；S2A 侧可调 inference_cfg_rate（0.7 上下微调） |
| 语速整体偏快/偏慢 | 段数与 cross_fade_duration 联动检查；根本性方案是重标定 1.72 系数 |

## 相关概念

- [00 仓库全景与推理链路总览](/concepts/00-overview.md)
- [02 长度调节与时长启发式](/concepts/02-length-regulation.md)
- [03 声学生成：flow matching 与 DiT 估计器](/concepts/03-flow-matching.md)
