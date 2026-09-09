---
type: reference
title: Confucius4-TTS 信源登记
tags:
  - confucius4-tts
  - tts
  - sources
  - netease-youdao
generated: 2026-09-09
status: verified
sources:
  - resource: vendor/netease-youdao/Confucius4-TTS/
---

# Confucius4-TTS 信源登记

## 上游仓库

| 项 | 值 |
|---|---|
| 仓库名 | netease-youdao/Confucius4-TTS |
| 上游 URL | `git@github.com:netease-youdao/Confucius4-TTS.git` |
| 本地路径 | `vendor/netease-youdao/Confucius4-TTS/`（third_party 子模块，只读） |
| 固定基线 commit | `4fb32c481302d8858c3aec6a1c2a8b4cea8894c0`（`git rev-parse HEAD`，2026-09-09 核验） |
| 许可证 | Apache License 2.0（January 2004，仓库根 LICENSE） |
| 包名 | `confuciustts`（setup.py name="confuciustts"，version 0.1.0，python_requires>=3.10；源码目录三个 t） |

## 关键信源文件清单

### 仓库级

| 文件 | 核验内容 |
|---|---|
| `README.md` | 14 种支持语言、致谢（Qwen3-TTS/CosyVoice/MaskGCT/w2v-BERT 2.0/Seed-VC/BigVGAN，arXiv 2608.11650）、用法与微调 TSV 格式 |
| `setup.py` | 包名/版本/Python 约束、transformers>=4.52,<4.56、extras_require（train/web/vllm） |
| `requirements.txt` | torch==2.7.0、transformers==4.52.4、pytorch-lightning==2.5.6 等精确版本 |
| `requirements_vllm_add.txt` | vllm==0.16.0、gradio==5.50.0、fastapi==0.136.3、uvicorn==0.49.0 等 |
| `LICENSE` | Apache-2.0 |
| `example.py` | HF 后端非流式用法示例 |

### 配置

| 文件 | 核验内容 |
|---|---|
| `config/inference_config.yaml` | paths（tokenizer/w2v-bert/vocoder/style_encoder）、t2s_model、s2a_model、audio 段 |
| `config/train_t2s.yaml` | t2s 训练超参（16-mixed、lr=2e-4、cosine 100k）、data 段 |
| `config/train_s2a.yaml` | s2a 训练超参（bf16-mixed、lr=1e-4）、独立 audio: 与 style_encoder: 段 |

### 推理与服务化

| 文件 | 核验内容 |
|---|---|
| `confuciustts/cli/inference.py` | `ConfuciusTTS`（HF 后端）：generate 签名、`int(T*1.72)` 启发式、段内调用链、cross/edge fade |
| `confuciustts/cli/inference_vllm.py` | `ConfuciusTTSVLLM`：async generate/generate_stream、patch_vllm 注册、model_dir 覆盖 |
| `server.py` | FastAPI + vLLM 服务：`/health`、`/api/tts`、`/api/tts/stream`，常量与上传限制 |
| `webui.py` | Gradio Blocks WebUI（Soft 主题，7860 端口，event loop 驱动 async generate） |

### 模型实现

| 文件 | 核验内容 |
|---|---|
| `confuciustts/llm/llm.py` | `Text2SemanticConfig`/`Text2Semantic`（GPT2Model 改造、generate、store_conditioning） |
| `confuciustts/llm/llm_vllm.py` | `Text2SemanticVLLM` 及 vLLM 多模态适配层（PLACEHOLDER_TOKEN、ProcessingInfo 等） |
| `confuciustts/llm/text_encoder.py` | `TextEmbeddingProjector`（冻结 Embedding + SiLU 投影） |
| `confuciustts/llm/speaker_encoder.py` | `Qwen3TTSSpeakerEncoder`（TDNN+SE-Res2Net+MFA+ASP，L2 归一化） |
| `confuciustts/llm/position_embeddings.py` | `DummyPositionEmbedding`/`LearnedPositionalEmbedding` |
| `confuciustts/flow/flow.py` | `MaskedDiffWithXvecConfig`/`MaskedDiffWithXvec`（prompt 0–30% 掩码、prompt_cond、inference 签名） |
| `confuciustts/flow/flow_matching.py` | `ConditionalCFM`（L1 loss、训练 CFG 丢弃、solve_euler 采样、推理 CFG） |
| `confuciustts/flow/length_regulator.py` | `InterpolateRegulator`（Conv1d+GroupNorm+Mish，nearest 上采样） |
| `confuciustts/flow/DiT/dit.py`、`modules.py` | `DiT`（depth=13、final_layer="wavenet"）与 RMSNorm/AdaLN/DiTBlock 等组件 |
| `confuciustts/flow/wavenet.py` | WeightNormConv1d 与 WN（估计器末层） |
| `external/bigvgan/bigvgan.py` | `BigVGAN`（Snake 激活、AMP resblock、from_pretrained 加载） |

### 训练与前端

| 文件 | 核验内容 |
|---|---|
| `confuciustts/cli/train_t2s.py`、`t2s_lightning.py` | t2s 训练入口与 `T2SLightningModule` |
| `confuciustts/cli/train_s2a.py`、`s2a_lightning.py` | s2a 训练入口与 `S2ALightningModule`（冻结四处模块、EMA、w2v-bert 第 17 层条件） |
| `confuciustts/dataset/` | T2S/S2A Dataset 与 DataModule |
| `confuciustts/frontend/text_normalizer.py` | `TextNormalizer`（wetext + inflect，Modified from CosyVoice） |
| `confuciustts/frontend/semantic_extractor.py` | `SemanticExtractor`/`SemanticCodec` 及加载函数 |
| `confuciustts/utils/text_utils.py` | `LANGUAGE_TOKEN_MAP`（93 键，"请用中文朗读接下来的文字"式 token） |

> 完整证据位置映射见 [facts.md](facts.md) 各条「证据位置」列。本 bundle 尚无 index.md 与上级 toctree 登记，留待索引阶段处理。
