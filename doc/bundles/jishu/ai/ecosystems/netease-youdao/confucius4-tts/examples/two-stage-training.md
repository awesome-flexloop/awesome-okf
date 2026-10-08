---
type: Example
title: 两阶段训练配置解读
description: 逐步解读 train_t2s.yaml 与 train_s2a.yaml 的关键配置段，执行两阶段训练命令，并说明 S2A 冻结策略与微调 TSV 五列数据格式。
tags: [confucius4-tts, tts, example, training, lightning, finetuning]
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

# 两阶段训练配置解读

本例逐步执行并解读 Confucius4-TTS 的两阶段训练：先收敛 T2S（文本→语义 token），再冻结 T2S 训 S2A（语义 token→mel）。配置键值忠实于 config/train_t2s.yaml 与 config/train_s2a.yaml 原文（F-c4t-045~051）。

## 前置条件

- 本地准备 w2v-bert 2.0：train_t2s.yaml 的 w2v_bert_path 为本地路径 "pretrained/w2v-bert-2.0"（F-c4t-050），注意推理配置用的是 HF id "facebook/w2v-bert-2.0"，两者不可混用；
- S2A 阶段另需 CAMPPlus 权重 ./pretrained/campplus/campplus_cn_common.bin（F-c4t-049）；
- 安装 train 依赖组（setup.py extras_require 的 train 组，F-c4t-003；精确版本见 requirements.txt，F-c4t-054）。

## 阶段一：训练 T2S

```bash
python -m confuciustts.cli.train_t2s -c config/train_t2s.yaml
```

关键配置解读（F-c4t-047）：

```yaml
log_dir: logs/t2s_train
seed: 42
precision: "16-mixed"            # fp16 混合精度
optimizer:                       # adamw, lr=2.0e-4, betas=[0.9, 0.95]
scheduler: cosine                # warmup 2000, total 100000
epochs: 100
gradient_clip: 1.0
val_check_interval: 1000
save_every_n_steps: 2000         # checkpoint: step_{step:09d}
data:
  batch_size: 2
  num_workers: 4
  sample_rate: 16000
paths:
  w2v_bert_path: pretrained/w2v-bert-2.0   # 本地路径（F-c4t-050）
```

T2S 阶段独立训练自回归 LLM：24 层、1280 维，直接从文本 token 预测离散语义 token（vocab 8194，F-c4t-012）。此阶段**无独立 audio: 段、无 style_encoder: 段**（F-c4t-049），音频仅以 16000 Hz 条件形式进入。

## 阶段二：训练 S2A（冻结 T2S）

```bash
python -m confuciustts.cli.train_s2a -c config/train_s2a.yaml
```

关键配置解读（F-c4t-048、F-c4t-049）：

```yaml
log_dir: logs/s2a_train
precision: "bf16-mixed"          # 比 t2s 更保守的数值精度
optimizer:                       # adamw, lr=1.0e-4, betas=[0.9, 0.98]
data:
  semantic_pad_token: 0
  target_sample_rate: 22050      # mel 目标采样率
  prompt_sample_rate: 16000      # 参考音频采样率
audio:                           # 仅 s2a 有此段
  n_fft: 1024
  win_length: 1024
  hop_length: 256
  n_mels: 80
style_encoder:                   # 仅 s2a 有此段
  target: external.campplus.CAMPPlus
  checkpoint: ./pretrained/campplus/campplus_cn_common.bin
```

S2ALightningModule 在训练前做四处置零冻结（requires_grad=False 且 eval）：`model.input_embedding`、T2S 模型、semantic_extractor、style_encoder（F-c4t-051）。跨阶段条件来自 w2v-bert 第 17 层 hidden states 的 mean/std 归一化（F-c4t-051）。稳定器为 EMA（beta=0.9999、update_every=10、update_after_step=100、include_online_model=False，F-c4t-051）。

### 冻结架构的直接后果：find_unused_parameters

两阶段共享 Lightning + DDPStrategy(nccl) 骨架，但 S2A 的 DDPStrategy 须追加 `find_unused_parameters=True`——因为冻结子模块不参与梯度计算，DDP 默认的梯度同步会报缺失（F-c4t-046）。若移除任何冻结模块，该标志可回退以提升多卡效率。

## 微调：TSV 五列数据

README 微调流程使用 TSV 五列格式（F-c4t-064）：

```text
lang	wav_path	norm_text	semantic_ids_path	ref_audio_paths
zh	data/spk1/utt1.wav	请用中文朗读接下来的文字。	data/spk1/utt1.sem	data/spk1/ref.wav
```

- `norm_text`：经 TextNormalizer 归一化后的文本（normalize(text, language="auto")，F-c4t-057）；
- `semantic_ids_path`：语义 token 离线提取结果——说明微调管线可绕过 T2S 前向，与 T2S 冻结设计一致（F-c4t-058）；
- `ref_audio_paths`：参考音频路径，供 prompt 条件使用。

## 常见误区

1. **在 S2A 阶段解冻 T2S**：会破坏 T2S/S2A 的段间契约，训练不稳定风险将从 flow matching 处扩散到全链路（F-c4t-051）；
2. **照抄训练 w2v_bert_path 到推理配置**：训练用本地路径、推理用 HF id，两者各就其位（F-c4t-050）；
3. **忽略精度差异**：t2s 用 16-mixed、s2a 用 bf16-mixed，换用需谨慎回归（F-c4t-047、F-c4t-048）。

## 相关概念

- [01 条件化机制：prompt 掩码、说话人与风格嵌入](/concepts/01-conditioning.md)
- [03 声学生成：flow matching 与 DiT 估计器](/concepts/03-flow-matching.md)
- [06 两阶段训练与微调体系](/concepts/06-training.md)
