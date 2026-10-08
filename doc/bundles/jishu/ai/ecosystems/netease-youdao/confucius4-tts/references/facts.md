---
type: reference
title: Confucius4-TTS 源码事实清单
tags:
  - confucius4-tts
  - tts
  - facts
  - source-reading
  - netease-youdao
generated: 2026-09-09
status: verified
sources:
  - resource: vendor/netease-youdao/Confucius4-TTS/README.md
  - resource: vendor/netease-youdao/Confucius4-TTS/setup.py
  - resource: vendor/netease-youdao/Confucius4-TTS/requirements.txt
  - resource: vendor/netease-youdao/Confucius4-TTS/requirements_vllm_add.txt
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/cli/inference.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/cli/inference_vllm.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/cli/train_t2s.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/cli/train_s2a.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/cli/t2s_lightning.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/cli/s2a_lightning.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/llm/llm.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/llm/llm_vllm.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/llm/text_encoder.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/llm/speaker_encoder.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/llm/position_embeddings.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/flow/flow.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/flow/flow_matching.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/flow/length_regulator.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/flow/DiT/dit.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/flow/DiT/modules.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/flow/wavenet.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/frontend/text_normalizer.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/frontend/semantic_extractor.py
  - resource: vendor/netease-youdao/Confucius4-TTS/confuciustts/utils/text_utils.py
  - resource: vendor/netease-youdao/Confucius4-TTS/external/bigvgan/bigvgan.py
  - resource: vendor/netease-youdao/Confucius4-TTS/server.py
  - resource: vendor/netease-youdao/Confucius4-TTS/webui.py
  - resource: vendor/netease-youdao/Confucius4-TTS/example.py
  - resource: vendor/netease-youdao/Confucius4-TTS/config/inference_config.yaml
  - resource: vendor/netease-youdao/Confucius4-TTS/config/train_t2s.yaml
  - resource: vendor/netease-youdao/Confucius4-TTS/config/train_s2a.yaml
---

# Confucius4-TTS 源码事实清单（R 阶段）

> 信源：`vendor/netease-youdao/Confucius4-TTS/`。本清单仅收录可从源码与配置原文核验的事实，编号 F-c4t-001 起连续。
> 包目录名为 `confuciustts`（源码实际拼写，三个 t），任务书与 README 中部分位置写作 `confuciusts`，以磁盘为准。

## 一、仓库与打包（README.md / setup.py）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-001 | README 列出 14 种支持语言：zh、en、ja、ko、de、fr、th、id、vi、es、pt、it、ru、ms | README.md：支持语言段落 |
| F-c4t-002 | setup.py 的 name 为 "confuciustts"，version 为 "0.1.0"，python_requires 为 ">=3.10" | setup.py:setup() |
| F-c4t-003 | setup.py 对 transformers 的版本约束为 ">=4.52,<4.56"；extras_require 包含 train、web、vllm 三组 | setup.py:setup() |
| F-c4t-004 | README 致谢段落列出 Qwen3-TTS、CosyVoice、Amphion/MaskGCT、w2v-BERT 2.0、Seed-VC、BigVGAN，并给出 arXiv 编号 2608.11650；仓库根目录存在 LICENSE 文件 | README.md：致谢段落；LICENSE |

## 二、推理链路：ConfuciusTTS（HF 后端）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-005 | `ConfuciusTTS.__init__` 的签名为 `(config_path="config/inference_config.yaml", t2s_checkpoint=None, device="cuda")` | confuciustts/cli/inference.py:ConfuciusTTS.__init__ |
| F-c4t-006 | `ConfuciusTTS.generate` 签名为 `(text, lang, prompt_wav, raw=False, temperature=0.8, top_p=0.8, top_k=30, num_beams=3, repetition_penalty=10.0, max_length=1520, n_timesteps=25, inference_cfg_rate=0.7, max_text_tokens_per_segment=80, cross_fade_duration=0.3, edge_fade_duration=0.1, edge_pad_duration=0.1, verbose=False)` | confuciustts/cli/inference.py:ConfuciusTTS.generate |
| F-c4t-007 | `generate` 返回 (sample_rate, audio_tensor)；`raw=True` 时返回 (sample_rate, list[segment_audio]) 不拼接 | confuciustts/cli/inference.py:ConfuciusTTS.generate |
| F-c4t-008 | 推理时提示文本格式为 f"You are a helpful assistant. {lang_token}:{text}" | confuciustts/cli/inference.py:ConfuciusTTS（prompt 格式化处） |
| F-c4t-009 | 段级 mel 目标长度启发式为 `int(T * 1.72)`（T 为该段文本 token 数），位于 `_synth_segment` 内 | confuciustts/cli/inference.py:ConfuciusTTS._synth_segment |
| F-c4t-010 | 段内调用链为 `t2s_model.generate(..., return_latent=True)` → `s2a_model.inference(...)` → `bigvgan(mel)`，输出经 cross_fade 与 edge_fade 拼接 | confuciustts/cli/inference.py:ConfuciusTTS._synth_segment |
| F-c4t-011 | example.py 为非流式示例，使用 `ConfuciusTTS`（HF 后端） | example.py（全文） |

## 三、LLM 模块（T2S）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-012 | `Text2SemanticConfig(PretrainedConfig)` 默认值：num_layers=24、model_dim=1280、num_heads=20、max_text_seq_lens=520、max_semantic_seq_lens=1520、vocab_size=32000、semantic_vocab_size=8194、text_embedding_dim=4096、speaker_embedding_dim=1024、start_semantic_token=8192、stop_semantic_token=8193 | confuciustts/llm/llm.py:Text2SemanticConfig |
| F-c4t-013 | `class Text2Semantic(PreTrainedModel, GenerationMixin)` | confuciustts/llm/llm.py:Text2Semantic |
| F-c4t-014 | `Text2Semantic` 包含子模块 TextEmbeddingProjector、semantic_embedding、两个 LearnedPositionalEmbedding（text 与 semantic 各一）、GPT2Model（删除 wpe、换 DummyPositionEmbedding、删除 wte）、final_norm、semantic_head、Qwen3TTSSpeakerEncoder | confuciustts/llm/llm.py:Text2Semantic.__init__ |
| F-c4t-015 | `Text2Semantic.generate(text_inputs, condition_vector, ..., return_latent=False)`：`return_latent=True` 时返回 dict（含 "semantic_codes"、"latent"），否则仅返回 semantic codes | confuciustts/llm/llm.py:Text2Semantic.generate |
| F-c4t-016 | `Text2Semantic` 提供 `store_conditioning` 缓存前缀条件嵌入 | confuciustts/llm/llm.py:Text2Semantic.store_conditioning |
| F-c4t-017 | `TextEmbeddingProjector.__init__(vocab_size, embed_dim, output_size, hidden_act="silu", bias=True)`；内部 nn.Embedding 冻结（requires_grad=False），结构为 Embedding→fc1(embed→embed)→SiLU→fc2(embed→output_size)；提供 `load_pretrained_embeddings` | confuciustts/llm/text_encoder.py:TextEmbeddingProjector |
| F-c4t-018 | `Qwen3TTSSpeakerEncoderConfig` 默认值：mel_dim=128、enc_dim=1024、enc_channels=[512,512,512,512,1536]、enc_kernel_sizes=[5,3,3,3,1]、enc_dilations=[1,2,3,4,1]、enc_res2net_scale=8、sample_rate=24000 | confuciustts/llm/speaker_encoder.py:Qwen3TTSSpeakerEncoderConfig |
| F-c4t-019 | `Qwen3TTSSpeakerEncoder` 结构为 TDNN + SE-Res2Net blocks + MFA + AttentiveStatisticsPooling + fc；`extract_embedding` 内含 L2 归一化；文件标注 "Modified from Qwen3-TTS" | confuciustts/llm/speaker_encoder.py:Qwen3TTSSpeakerEncoder |
| F-c4t-020 | `llm/position_embeddings.py` 定义 `DummyPositionEmbedding` 与 `LearnedPositionalEmbedding` | confuciustts/llm/position_embeddings.py |

## 四、flow matching 模块（S2A）

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-021 | `MaskedDiffWithXvecConfig` 默认值：input_size=512、output_size=80、spk_embed_dim=192、semantic_embed_dim=1024、lm_latent_dim=1280、semantic_codebook_size=8192、semantic_codebook_dim=8、semantic_output_dim=1024、lr_channels=512、lr_sampling_ratios=(1,1,1,1)、lr_out_channels=512、lr_in_channels=1024、cfm_sigma_min=1e-6、cfm_training_cfg_rate=0.2、cfm_inference_cfg_rate=0.7、cfm_t_scheduler="linear"、estimator_hidden_dim=512、estimator_num_heads=8、estimator_depth=13、estimator_final_layer="wavenet"、estimator_wavenet_num_layers=8 | confuciustts/flow/flow.py:MaskedDiffWithXvecConfig |
| F-c4t-022 | `class MaskedDiffWithXvec(nn.Module)` 组件：InterpolateRegulator、ConditionalCFM、SemanticTokenEmbedding、encoder_proj（Linear(lm_latent_dim+semantic_embed_dim → lr_in_channels)）、prompt_cond（nn.Parameter，形状 1×1×lr_out_channels，初始化 std=0.02） | confuciustts/flow/flow.py:MaskedDiffWithXvec.__init__ |
| F-c4t-023 | 训练时对 prompt 做随机 0–30% 掩码（代码中随机比例上界 0.3） | confuciustts/flow/flow.py:MaskedDiffWithXvec（训练前向） |
| F-c4t-024 | `MaskedDiffWithXvec.inference(semantic_token, lm_latent, prompt_feat, embedding, target_feat_len, n_timesteps=25, inference_cfg_rate=0.7)` | confuciustts/flow/flow.py:MaskedDiffWithXvec.inference |
| F-c4t-025 | `class ConditionalCFM(nn.Module)` 提供 `compute_loss`（L1 loss，训练 CFG 条件丢弃）与 `forward(mu, x_lens, prompt, spks, n_timesteps=25, inference_cfg_rate=0.7, temperature=1.0)`；采样经 `solve_euler`，CFG 时将 batch 翻倍拼接 conditional/unconditional | confuciustts/flow/flow_matching.py:ConditionalCFM |
| F-c4t-026 | `class InterpolateRegulator(nn.Module)`：`content_in_proj` + 每层 Conv1d(kernel=3)+GroupNorm+Mish + 末端 Conv1d(kernel=1)；`F.interpolate(mode="nearest")` 上采样至 `ylens.max()` | confuciustts/flow/length_regulator.py:InterpolateRegulator |
| F-c4t-027 | `class InputEmbedding` 将 x、cond、mu_proj、spks 拼接后投影 | confuciustts/flow/DiT/dit.py:InputEmbedding |
| F-c4t-028 | `class DiT(nn.Module).__init__(hidden_dim=512, num_heads=8, depth=13, mel_dim=80, mu_dim=512, spk_dim=192, long_skip_connection=True, max_seq_len=4096, ..., final_layer="wavenet", ...)` | confuciustts/flow/DiT/dit.py:DiT.__init__ |
| F-c4t-029 | `flow/DiT/modules.py` 定义 RMSNorm、AdaptiveLayerNorm、FeedForward、Attention、DiTBlock、FinalLayer、SinusPositionEmbedding、TimestepEmbedding | confuciustts/flow/DiT/modules.py |
| F-c4t-030 | `flow/wavenet.py` 定义 WeightNormConv1d 与 WN | confuciustts/flow/wavenet.py |

## 五、BigVGAN 声码器

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-031 | `class BigVGAN(torch.nn.Module, PyTorchModelHubMixin, library_name="bigvgan")`；`__init__(h: AttrDict, use_cuda_kernel=False)` | external/bigvgan/bigvgan.py:BigVGAN |
| F-c4t-032 | `BigVGAN.forward(x)` 流程：conv_pre → ups（ConvTranspose1d）→ AMP resblocks（均值聚合）→ activation_post（Snake/SnakeBeta）→ conv_post → tanh/clamp | external/bigvgan/bigvgan.py:BigVGAN.forward |
| F-c4t-033 | `BigVGAN` 提供 `remove_weight_norm()` 与 `load_hparams_from_json` | external/bigvgan/bigvgan.py:BigVGAN |
| F-c4t-034 | 推理以 `BigVGAN.from_pretrained(paths["vocoder_path"], use_cuda_kernel=False)` 加载；inference_config.yaml 中 vocoder_path 为 "nvidia/bigvgan_v2_22khz_80band_256x" | confuciustts/cli/inference.py:ConfuciusTTS.__init__；config/inference_config.yaml:paths.vocoder_path |

## 六、vLLM 加速路径

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-035 | `class ConfuciusTTSVLLM`：`__init__(config_path, gpu_memory_utilization=0.4, device="cuda", model_dir=None)`；model_dir 或 MODEL_DIR 环境变量可重写 "./checkpoints" 前缀 | confuciustts/cli/inference_vllm.py:ConfuciusTTSVLLM.__init__ |
| F-c4t-036 | `async def generate(text, lang, prompt_wav, request_id=None, raw=False, n_timesteps=25, inference_cfg_rate=0.7, max_text_tokens_per_segment=80, cross_fade_duration=0.3, verbose=False)` | confuciustts/cli/inference_vllm.py:ConfuciusTTSVLLM.generate |
| F-c4t-037 | `async def generate_stream(..., first_chunk_size_tokens=25, chunk_size_tokens=50, overlap_tokens=10, ...)` 返回 AsyncIterator[torch.Tensor]；内部 `_synth_segment` 与 `_synth_segment_stream` 分别对应非流式与流式段合成 | confuciustts/cli/inference_vllm.py:ConfuciusTTSVLLM.generate_stream |
| F-c4t-038 | `llm_vllm.py` 定义 `PLACEHOLDER_TOKEN = "!"`、`PLACEHOLDER_TOKEN_ID = 0`，以及 `class Text2SemanticVLLM(nn.Module, SupportsPP, SupportsMultiModal)`（另有 ConfuciusTTSProcessingInfo、ConfuciusTTSDummyInputsBuilder、ConfuciusTTSDataParser、ConfuciusTTSMultiModalProcessor、_TransformerBackbone） | confuciustts/llm/llm_vllm.py |
| F-c4t-039 | inference_vllm.py 顶层 `import confuciustts.llm.patch_vllm` 注册自定义架构 | confuciustts/cli/inference_vllm.py:模块导入处 |

## 七、服务化：server.py / webui.py

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-040 | server.py 基于 FastAPI，以 vLLM 后端启动；命令行默认 `--host 0.0.0.0 --port 8000 --gpu_memory_utilization 0.4`，uvicorn workers=1 | server.py:argparse/main |
| F-c4t-041 | server.py 常量：`LANGUAGES = ("zh","en","ja","ko","de","fr","th","id","vi","es","pt","it","ru","ms")`（14 个）、`ALLOWED_AUDIO_EXTENSIONS={.wav,.flac,.mp3,.m4a,.ogg}`、`MAX_REFERENCE_AUDIO_BYTES=50MB`、`MAX_TEXT_LENGTH=1024` | server.py:模块常量 |
| F-c4t-042 | server.py 路由：`GET /health`；`POST /api/tts` 返回 WAV PCM_16，响应头含 X-Sample-Rate/X-Duration-Sec/X-Elapsed-Sec；`POST /api/tts/stream` 返回原始 int16-LE PCM 流，响应头含 X-Sample-Rate/X-Channels/X-Encoding | server.py:路由定义 |
| F-c4t-043 | server.py 上传参考音频暂存于 `/tmp/confucius4_upload_<uuid>` | server.py:上传处理 |
| F-c4t-044 | webui.py 基于 Gradio Blocks（theme Soft），默认 `--port 7860 --host 0.0.0.0`；`build_demo` 内新建 event loop 驱动 async `model.generate` | webui.py:build_demo/main |

## 八、训练配置与训练脚本

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-045 | 训练入口：`python -m confuciustts.cli.train_t2s -c config/train_t2s.yaml` 与 `python -m confuciustts.cli.train_s2a -c config/train_s2a.yaml` | confuciustts/cli/train_t2s.py:main；confuciustts/cli/train_s2a.py:main |
| F-c4t-046 | 两阶段训练均以 PyTorch Lightning Trainer + DDPStrategy(nccl) + TensorBoardLogger + ModelCheckpoint(filename="step_{step:09d}") 运行，含 `get_latest_checkpoint` 恢复逻辑；S2A 的 DDPStrategy 追加 find_unused_parameters=True | confuciustts/cli/train_t2s.py；confuciustts/cli/train_s2a.py |
| F-c4t-047 | train_t2s.yaml：log_dir=logs/t2s_train、seed=42、precision="16-mixed"、optimizer adamw lr=2.0e-4 betas=[0.9,0.95]、scheduler cosine（warmup 2000，total 100000）、epochs=100、gradient_clip=1.0、val_check_interval=1000、save_every_n_steps=2000；data 段 batch_size=2、num_workers=4、sample_rate=16000 | config/train_t2s.yaml |
| F-c4t-048 | train_s2a.yaml：log_dir=logs/s2a_train、precision="bf16-mixed"、optimizer adamw lr=1.0e-4 betas=[0.9,0.98]、scheduler 与 epochs/gradient_clip/val_check_interval/save_every_n_steps 同 t2s；data 段含 max_text_seq_len、max_semantic_seq_len、semantic_pad_token=0、target_sample_rate=22050、prompt_sample_rate=16000 | config/train_s2a.yaml |
| F-c4t-049 | 结构差异：train_s2a.yaml 含独立 `audio:` 段（n_fft/win_length/hop_length/n_mels）与 `style_encoder` 段（target=external.campplus.CAMPPlus，checkpoint=./pretrained/campplus/campplus_cn_common.bin）；train_t2s.yaml 无这两段 | config/train_s2a.yaml；config/train_t2s.yaml |
| F-c4t-050 | train_t2s.yaml 的 w2v_bert_path 为本地路径 "pretrained/w2v-bert-2.0"；inference_config.yaml 的 w2v_bert_path 为 Hugging Face id "facebook/w2v-bert-2.0" | config/train_t2s.yaml:paths；config/inference_config.yaml:paths |
| F-c4t-051 | `class S2ALightningModule(L.LightningModule)` 冻结 model.input_embedding、T2S 模型、semantic_extractor、style_encoder（requires_grad=False 且 eval）；EMA 来自 ema_pytorch（beta=0.9999、update_every=10、update_after_step=100、include_online_model=False）；`_speaker_condition` 取 w2v-bert 第 17 层 hidden states 并做 mean/std 归一化 | confuciustts/cli/s2a_lightning.py |
| F-c4t-052 | `class T2SLightningModule(L.LightningModule)` 位于 t2s_lightning.py | confuciustts/cli/t2s_lightning.py:T2SLightningModule |
| F-c4t-053 | dataset 模块定义 T2SDataset、T2SDataModule、S2ADataset、S2ADataModule | confuciustts/dataset（类定义处） |

## 九、依赖项

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-054 | requirements.txt 精确版本：torch==2.7.0、torchaudio==2.7.0、transformers==4.52.4、pytorch-lightning==2.5.6、numpy==1.26.4、librosa==0.10.2.post1、soundfile==0.13.1、wetext==0.1.4、ema-pytorch==0.7.9 等 | requirements.txt |
| F-c4t-055 | requirements_vllm_add.txt 精确版本：vllm==0.16.0、gradio==5.50.0、fastapi==0.136.3、uvicorn==0.49.0、ffmpy、nvidia-nvshmem-cu12==3.3.20 | requirements_vllm_add.txt |
| F-c4t-056 | requirements.txt 中 inflect 与 regex 各出现两次（重复条目） | requirements.txt |

## 十、前端与文本工具

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-057 | `class TextNormalizer` 基于 wetext Normalizer（zh 配置 remove_erhua=False，ImportError 时置 None）与 inflect；方法 `normalize(text, language="auto")`、`segment_text`、contains_chinese、spell_out_numbers；文件标注 "Modified from CosyVoice" | confuciustts/frontend/text_normalizer.py:TextNormalizer |
| F-c4t-058 | frontend 定义 `SemanticExtractor`、`SemanticCodec`、`load_semantic_extractor`、`load_semantic_codec`，提供 encode/extract/extract_from_file/encode_from_file | confuciustts/frontend/semantic_extractor.py |
| F-c4t-059 | `LANGUAGE_TOKEN_MAP` 共 93 个键（含 zh/ja/ko/vi/th/id/ms/en/de/fr/es/pt/it/ru 等，V 阶段复核计数），值形如 "请用中文朗读接下来的文字" | confuciustts/utils/text_utils.py:LANGUAGE_TOKEN_MAP |

## 十一、推理配置 inference_config.yaml

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-060 | paths 段：tokenizer_path=./checkpoints、w2v_bert_path=facebook/w2v-bert-2.0、w2v_stat（路径）、style_encoder.target=external.campplus.CAMPPlus（feat_dim=80、embedding_size=192、checkpoint=campplus_cn_common.bin）、vocoder_path=nvidia/bigvgan_v2_22khz_80band_256x | config/inference_config.yaml:paths |
| F-c4t-061 | `t2s_model` 段键值与 Text2SemanticConfig 源码默认一致；`s2a_model` 段仅 6 键：input_size=512、output_size=80、spk_embed_dim=192、semantic_embed_dim=1024、lm_latent_dim=1280、estimator_mlp_ratio=3.0 | config/inference_config.yaml:t2s_model、s2a_model |
| F-c4t-062 | `audio` 段：target_sample_rate=22050、prompt_sample_rate=16000、n_fft=1024、hop_length=256、win_length=1024、n_mels=80、fmin=0、fmax=null | config/inference_config.yaml:audio |

## 十二、README 用法说明

| 编号 | 事实陈述 | 证据位置 |
|---|---|---|
| F-c4t-063 | README 用法包含：example.py（HF 后端）、vLLM 示例、webui.py --port 7860、server.py --port 8000（含 /api/tts 与 /api/tts/stream） | README.md：Usage 段落 |
| F-c4t-064 | README 微调流程给出 TSV 五列格式：lang、wav_path、norm_text、semantic_ids_path、ref_audio_paths | README.md：微调段落 |

## 存疑与读不到之处

- `confuciustts` 包内共 47 个 `^class` 定义（Grep 计数，V 阶段复核）；本清单仅收录与推理链路、训练配置、服务化直接相关的类，未逐一展开 dataset 与 DiT 组件内部实现。
- README 宣称 CUDA 12.6 / Python 3.10 环境，setup.py 约束为 python_requires>=3.10，两处表述颗粒度不同，本清单以 setup.py 原文为准。
- train_t2s.yaml 未含 style_encoder 段与独立 audio 段，S2A 训练时的风格编码器来源以此差异为准记录；若 t2s 训练另有条件提取入口，本次阅读未在 train_t2s.yaml 中发现对应配置键。
- 本 bundle 目录（confucius4-tts/）为本次 R 阶段新建，尚无 index.md 与上级 toctree 登记，留待后续索引阶段处理。
