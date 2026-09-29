---
type: concept
title: JETS 联合训练与 HiFiGAN 声码器
description: 解读 JETSGenerator 把声学模型与声码器内嵌为单一模块的结构、mel 重建损失主导（dec_mel_loss×45）的损失组合、DDP 训练循环与 g_/do_ checkpoint 组织。
tags: [emotivoice, tts, jets, hifigan, joint-training, vocoder]
generated: { by: "reference_agent/trae-solo", at: 2026-09-09T00:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T00:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: EmotiVoice 源码事实清单（v0.3 @ 59f0f36）
  - id: insights
    resource: /references/insights.md
    title: EmotiVoice 架构洞察与知识地图（v0.3 @ 59f0f36）
---

# JETS 联合训练与 HiFiGAN 声码器

传统流水线式 TTS 把声学模型与声码器当作两个可独立替换的组件；EmotiVoice 采用的 JETS 架构则把二者**内嵌进同一个生成器模块、放进同一个训练循环**。本文解读这一联合结构及其训练机制。

## JETSGenerator：声码器内嵌进生成器

`models/prompt_tts_modified/jets.py` 的 `JETSGenerator(nn.Module)` 在 `__init__(config)` 中完成两件内联（F-ev-018）：

```python
self.am = PromptTTS(config)              # 声学模型（音素 → mel）
self.generator = HiFiGANGenerator(config.model)  # 声码器（mel → 波形）
self.upsample_factor = int(np.prod(config.model.upsample_rates))
self.segment_size = config.segment_size
```

`PromptTTS` 负责把音素序列（配合风格嵌入、说话人嵌入）转成 mel 谱；`HiFiGANGenerator` 把 mel 直接上采样成波形。上采样率连乘 `int(np.prod(config.model.upsample_rates))` 对应 `config/joint/config.yaml` 中的 `upsample_rates [8,8,2,2]`（乘积 256，等于 `hop_size 256`，F-ev-030），保证「一次 mel 帧对应一个 hop 的波形样本」。

## forward：从音素到波形的单次前向

`forward` 签名暴露了全部条件输入（F-ev-019）：

```python
forward(self, inputs_ling, input_lengths, inputs_speaker,
        inputs_style_embedding, inputs_content_embedding,
        mel_targets=None, output_lengths=None,
        pitch_targets=None, energy_targets=None,
        alpha=1.0, cut_flag=True)
```

训练分支先用 `get_random_segments` 从目标 mel 上随机切出长度为 `segment_size`（config.yaml 中为 32，F-ev-030）的片段，再调 `self.generator(z_segments)` 生成对应波形段，结果写入 `outputs["wav_predictions"]`（F-ev-019）。推理分支则整句生成，`alpha=1.0` 写死（见 [00 整体架构与推理入口](/concepts/00-architecture.md)）。

## 训练循环：DDP + 联合优化

`train_am_vocoder_joint.py` 的 `train(args, config)` 组织完整训练循环（F-ev-031）：

```
torch.distributed.init_process_group(backend="nccl", init_method="env://")
        │
        ▼
StyleEncoder 冻结加载（strict=False，key[7:] 去前缀）
        │
        ▼
数据侧：Dataset_PromptTTS_JETS + DistributedSampler
        + DataLoader(num_workers=8)
        │
        ▼
模型侧：generator = JETSGenerator(conf)
        discriminator = Discriminator(conf)
        （来自 models.hifigan.pretrained_discriminator）
        两者均经 DDP 包装
        │
        ▼
优化器 Adam(lr=conf.optimizer.lr, betas=conf.optimizer.betas)
调度器 ExponentialLR(gamma=conf.scheduler.gamma)
损失   loss_fn = TTSLoss()
```

三个细节值得注意：

1. **风格编码器冻结**：StyleEncoder 不参与联合训练梯度（F-ev-031），风格嵌入在预处理阶段离线缓存（npy 缓存逻辑见 [05](/concepts/05-labels-dataset-mfa.md)），训练成本集中在生成器与判别器；
2. **判别器复用预训练件**：`Discriminator` 直接来自 `models.hifigan.pretrained_discriminator`（F-ev-031），`models/hifigan/models.py` 注明改自 jik876/hifi-gan，定义 `ResBlock1`（dilation (1,3,5)，每组 3 个卷积）、`ResBlock2`（dilation (1,3)）、`Generator`、`discriminator_loss`、`generator_loss`、`feature_loss`（F-ev-023）；
3. **超参**：优化器 lr 1.25e-5、betas [0.5, 0.9]，调度器 gamma 0.999875（F-ev-030）。

## 损失组合：mel 重建主导

生成器损失为（F-ev-032）：

```
loss_gen + loss_fm + dec_mel_loss*45 + dur_loss*1
         + pitch_loss*1 + energy_loss*1 + forwardsum_loss*2 + bin_loss*2
```

其中 `dec_mel_loss` 实际以 `F.l1_loss(y_mel, y_hat_mel)` 计算，权重 45 倍于时长/音高/能量项——**mel 谱重建是训练的锚点**，对抗损失（loss_gen/loss_fm）与韵律损失为辅。判别器损失为 `discriminator_loss`（f/s 两组）（F-ev-032）。

这一权重设计带来两个实践推论：

- **评估合成质量应优先看 mel 谱重建**，而非仅听感——训练目标本身以 mel 损失为锚；
- 采样率仅 16 kHz（F-ev-029、F-ev-030），对抗 HiFi 直觉的 22.05/24 kHz 惯例，波形细节上限由数据与采样率共同决定。

## checkpoint 组织

- 命名：`g_{:08d}`（生成器）/ `do_{:08d}`（判别器，含 discriminator、optim_g、optim_d、steps、epoch）（F-ev-032）；
- 扫描：`scan_checkpoint` 模式为 `prefix + '????????'`（F-ev-032）；推理主入口引用的 `g_00140000` 即此命名（F-ev-002）；
- **勿单独替换 vocoder checkpoint**：`g_xxxxxxxx` 同时内含声学模型与声码器生成器（F-ev-018、F-ev-032），替换它会同时换掉声学模型；
- 每 `iters_per_validation`（1000）跑 validate，每 `iters_per_checkpoint`（10000）存 checkpoint，`train_steps = 10_000_000`、epoch 上限 5_000_000（F-ev-029、F-ev-032）。

## vocoder 工具函数

`models/hifigan/get_vocoder.py` 定义 `MAX_WAV_VALUE = 32768.0`（推理输出的幅值缩放常数，F-ev-022）；`vocoder(hifi_gan_path, hifi_gan_name)` 在 CPU 上加载独立声码器（读 config.json 为 AttrDict、取 `state_dict_g['generator']`、`remove_weight_norm()`），另有 `vocoder2(config, hifi_gan_ckpt_path)` 与 `vocoder_inference(vocoder, melspec, max_db, min_db)`（F-ev-022）。这些是独立于 JETS 主链路的辅助路径，适合「只换独立声码器做对比实验」的场景。

## 相关概念

- [00 整体架构与推理入口](/concepts/00-architecture.md)
- [03 PromptTTS 风格条件注入](/concepts/03-style-conditioning.md)
- [05 标签体系、数据集与 MFA 对齐流水线](/concepts/05-labels-dataset-mfa.md)
- [06 服务化部署](/concepts/06-serving-api.md)
