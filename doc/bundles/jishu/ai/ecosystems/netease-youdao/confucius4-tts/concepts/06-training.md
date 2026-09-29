---
type: Concept
title: 两阶段训练与微调体系
description: t2s/s2a 训练配置差异、S2A 阶段模块冻结策略、EMA、TSV 五列微调数据格式、w2v-bert 2.0 条件提取与依赖锁定。
tags: [confucius4-tts, tts, training, lightning, ema, finetuning]
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

# 两阶段训练与微调体系

Confucius4-TTS 的训练遵循严格的"先收敛 T2S，再训 S2A"两阶段顺序。两阶段共享 PyTorch Lightning + DDP 骨架，但配置呈"前轻后重"的不对称：S2A 阶段引入独立 audio 段与 style_encoder 段，并整体冻结 T2S。

## 训练入口

两个入口均为模块方式执行（F-c4t-045）：

```bash
python -m confuciustts.cli.train_t2s -c config/train_t2s.yaml
python -m confuciustts.cli.train_s2a -c config/train_s2a.yaml
```

数据管线由 dataset 模块的 T2SDataset / T2SDataModule / S2ADataset / S2ADataModule 四类承载（F-c4t-053）。

## 共享骨架

两阶段均以 PyTorch Lightning Trainer + DDPStrategy(nccl) + TensorBoardLogger + ModelCheckpoint(filename="step_{step:09d}") 运行，并含 `get_latest_checkpoint` 恢复逻辑（F-c4t-046）。唯一差异：S2A 的 DDPStrategy 追加 `find_unused_parameters=True`——这是模块冻结的直接后果（冻结子模块不参与梯度计算），删除冻结子模块时该标志可回退以提升 DDP 效率。

## 配置差异对照

| 项 | train_t2s.yaml | train_s2a.yaml |
|---|---|---|
| log_dir | logs/t2s_train | logs/s2a_train |
| seed | 42 | 42 |
| precision | "16-mixed" | "bf16-mixed" |
| optimizer | adamw lr=2.0e-4 betas=[0.9,0.95] | adamw lr=1.0e-4 betas=[0.9,0.98] |
| scheduler | cosine，warmup 2000，total 100000 | 同 t2s |
| epochs / gradient_clip / val_check_interval / save_every_n_steps | 100 / 1.0 / 1000 / 2000 | 同 t2s |
| data 段 | batch_size=2、num_workers=4、sample_rate=16000 | max_text_seq_len、max_semantic_seq_len、semantic_pad_token=0、target_sample_rate=22050、prompt_sample_rate=16000 |
| 独立 audio: 段 | 无 | 有（n_fft/win_length/hop_length/n_mels） |
| style_encoder: 段 | 无 | 有（target=external.campplus.CAMPPlus，checkpoint=./pretrained/campplus/campplus_cn_common.bin） |

依据 F-c4t-047、F-c4t-048、F-c4t-049。S2A 精度用 bf16-mixed、学习率减半、betas 第二分量收紧，反映 flow matching 训练对稳定性的更高要求。

## w2v-bert 2.0 条件提取

跨阶段条件由 w2v-BERT 2.0 提供。路径处理有一处不对称：train_t2s.yaml 的 w2v_bert_path 为本地路径 "pretrained/w2v-bert-2.0"，而 inference_config.yaml 为 Hugging Face id "facebook/w2v-bert-2.0"（F-c4t-050）——部署时勿直接照抄训练配置。

S2ALightningModule 的 `_speaker_condition` 取 w2v-bert 第 17 层 hidden states 并做 mean/std 归一化（F-c4t-051）：第 17 层是经验选择的语义内容层，归一化消除说话人响度与通道差异。

## S2A 冻结策略与 EMA

`S2ALightningModule`（confuciustts/cli/s2a_lightning.py，F-c4t-051）冻结四处模块：`model.input_embedding`、T2S 模型、semantic_extractor、style_encoder（requires_grad=False 且 eval）。这等价于把 T2S 视为"已收敛的语义先验编码器"，把训练不稳定风险全部收敛到 flow matching 估计器一处；代价是语义 token 的偏差无法回传修正，只能由 S2A 的 CFG/条件机制吸收。复刻训练流程时**不要在 S2A 阶段解冻 T2S**——那会破坏 T2S/S2A 之间的段间契约。

稳定器使用 ema_pytorch 的 EMA：beta=0.9999、update_every=10、update_after_step=100、include_online_model=False（F-c4t-051）。T2S 侧的训练模块为 `T2SLightningModule`（confuciustts/cli/t2s_lightning.py，F-c4t-052）。

## 微调：TSV 五列格式

README 微调流程给出 TSV 五列格式（F-c4t-064）：

| 列 | 含义 |
|---|---|
| lang | 语言代码 |
| wav_path | 目标音频路径 |
| norm_text | 归一化后文本 |
| semantic_ids_path | 语义 token 离线提取结果路径 |
| ref_audio_paths | 参考音频路径 |

其中 semantic_ids_path 列意味着语义 token 可离线预提取（由 frontend 的 SemanticExtractor / SemanticCodec 完成 encode/extract/extract_from_file/encode_from_file，F-c4t-058），微调数据管线可绕过 T2S 前向——与 T2S 冻结的设计一致。文本归一化由 TextNormalizer 承担（基于 wetext Normalizer，zh 配置 remove_erhua=False，辅以 inflect；方法 normalize(text, language="auto")、segment_text、contains_chinese、spell_out_numbers；标注 "Modified from CosyVoice"，F-c4t-057）。

## 依赖锁定

训练环境受 requirements.txt 精确版本锁定（torch==2.7.0、pytorch-lightning==2.5.6 等，F-c4t-054），服务化组件另由 requirements_vllm_add.txt 锁定（F-c4t-055）。setup.py 的 train extras_require 对应训练依赖组（F-c4t-003）。

## 相关概念

- [01 条件化机制：prompt 掩码、说话人与风格嵌入](/concepts/01-conditioning.md)
- [03 声学生成：flow matching 与 DiT 估计器](/concepts/03-flow-matching.md)
