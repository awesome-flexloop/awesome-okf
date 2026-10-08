# 实战示例

本目录登记 base-llm 仓库 `code/` 目录下的全部示例代码。每个章节目录对应教程的相关章节，包含从基础算法到手写架构再到完整项目的渐进式代码实现。

源码位置：https://github.com/datawhalechina/base-llm/tree/main/code

---

## C2 词向量

**目录**：`code/C2/`

| 文件 | 说明 |
|------|------|
| `01_jieba.py` | jieba 分词基础用法——精确模式/全模式/搜索引擎模式、词性标注、关键词提取 |
| `04_gensim.ipynb` | Gensim Word2Vec 实战——语料预处理、模型训练、词向量查询、相似度计算、可视化 |
| `user_dict.txt` | 自定义用户词典 |
| `user_pos_dict.txt` | 带词性标注的自定义词典 |

对应概念：[词向量与循环神经网络](../concepts/word-vectors-rnn.md)

---

## C3 循环神经网络

**目录**：`code/C3/`

| 文件 | 说明 |
|------|------|
| `01_RNN.py` | RNN 从零实现——隐藏状态传递、参数共享、BPTT 反向传播 |
| `02_LSTM.py` | LSTM 从零实现——遗忘门/输入门/输出门、细胞状态更新、GRU 对比 |

对应概念：[词向量与循环神经网络](../concepts/word-vectors-rnn.md)

---

## C4 Transformer

**目录**：`code/C4/`

| 文件/目录 | 说明 |
|-----------|------|
| `01_Seq2Seq.py` | Seq2Seq 编码器-解码器基础实现 |
| `02_attention.py` | Bahdanau/Luong 注意力机制实现 |
| `03_Self-Attention.py` | 自注意力机制（Q/K/V）实现 |
| `transformer/src/attention.py` | 多头注意力模块 |
| `transformer/src/pos.py` | 正弦位置编码 |
| `transformer/src/ffn.py` | 位置前馈网络 |
| `transformer/src/norm.py` | 层归一化 |
| `transformer/src/transformer.py` | Encoder/Decoder 完整组装 |
| `transformer/main.py` | Transformer 运行入口 |

对应概念：[Transformer 架构](../concepts/transformer.md)

---

## C5 预训练模型

**目录**：`code/C5/`

| 文件 | 说明 |
|------|------|
| `01_bert_usage.py` | BERT 模型加载与特征提取/文本编码 |
| `02_gpt_usage.py` | GPT 模型加载与自回归文本生成 |
| `03_t5_usage.py` | T5 文本到文本任务（翻译/摘要） |
| `03_bucket_id.py` | Hugging Face Bucket ID 机制 |
| `04_hf_usage.ipynb` | Hugging Face Transformers/Datasets/Pipeline 综合实战 |
| `cat.jpg` | 测试图片 |

对应概念：[预训练语言模型](../concepts/pretrained-models.md)

---

## C6 大模型架构

**目录**：`code/C6/`

### llama2/ — 手写 Llama2

| 文件 | 说明 |
|------|------|
| `src/attention.py` | GQA 分组查询注意力 + KV Cache |
| `src/rope.py` | RoPE 旋转位置编码 |
| `src/norm.py` | RMSNorm 归一化 |
| `src/ffn.py` | SwiGLU 前馈网络 |
| `src/transformer.py` | Llama2 Block 和模型组装 |
| `main.py` | 运行入口 |

### MoE/ — 手写混合专家

| 文件 | 说明 |
|------|------|
| `src/attention.py` | 注意力模块 |
| `src/rope.py` | RoPE 位置编码 |
| `src/norm.py` | RMSNorm |
| `src/ffn.py` | MoE 层（多专家+路由） |
| `src/transformer.py` | MoE Transformer 组装 |
| `main.py` | 运行入口 |

对应概念：[大模型架构深入](../concepts/llm-architecture.md)

---

## C7 文本分类

**目录**：`code/C7/`

| 文件 | 说明 |
|------|------|
| `01_text_classification.ipynb` | 文本分类简单实现（TF-IDF + 传统分类器） |
| `02_lstm_text_classification.ipynb` | 基于 LSTM 的文本分类 |
| `03_bert_text_classification.ipynb` | 微调 BERT 进行文本分类（Hugging Face Trainer） |

对应概念：[预训练语言模型](../concepts/pretrained-models.md)

---

## C8 命名实体识别

**目录**：`code/C8/` — 完整 NER 工程项目

### 数据

| 文件 | 说明 |
|------|------|
| `data/CMeEE-V2_train.json` | CMeEE-V2 中文医学 NER 训练集 |
| `data/CMeEE-V2_dev.json` | CMeEE-V2 验证集 |
| `data/categories.json` | 实体类别定义 |
| `data/vocabulary.json` | 词表文件 |

### 源码（src/）

| 模块 | 说明 |
|------|------|
| `configs/configs.py` | 训练配置（超参数/路径） |
| `data/dataset.py` | PyTorch Dataset 定义 |
| `data/data_loader.py` | DataLoader 构建 |
| `tokenizer/` | 字符级分词器（CharTokenizer/Vocabulary） |
| `loss/ner_loss.py` | NER 损失函数 |
| `metrics/entity_metrics.py` | 实体级评估指标（P/R/F1） |
| `trainer/trainer.py` | 训练循环封装 |
| `utils/early_stop.py` | 早停机制 |
| `utils/logger.py` | 日志工具 |
| `utils/file_io.py` | 文件 I/O 工具 |

### 脚本

| 文件 | 说明 |
|------|------|
| `01_build_category.py` | 构建实体类别映射 |
| `02_build_vocabulary.py` | 构建词表 |
| `03_data_loader.py` | 数据加载测试 |
| `04_model.py` | NER 模型定义（BERT+BiLSTM+CRF 等） |
| `05_train.py` | 模型训练 |
| `06_predict.py` | 模型推理与预测 |

对应概念：[预训练语言模型](../concepts/pretrained-models.md)

---

## C11 参数高效微调

**目录**：`code/C11/`

| 文件 | 说明 |
|------|------|
| `03_peft_pythia-2.8b.ipynb` | 使用 peft 库对 Pythia-2.8b 进行 LoRA 微调 |
| `04_dataset_gen.ipynb` | 私有数据集生成（blackwukong 对话数据） |
| `04_qwen2.5_qlora.ipynb` | Qwen2.5 QLoRA 4-bit 量化微调完整流程 |
| `04_qwen2.5_test.ipynb` | 微调后 Qwen2.5 模型推理测试 |
| `data/blackwukong.md` | 黑神话悟空原始文本数据 |
| `data/wukong_base_*.jsonl` | 基座模型生成数据 |
| `data/wukong_dataset_*.jsonl` | 格式化训练数据集 |

对应概念：[参数高效微调与人类对齐](../concepts/finetuning-alignment.md)

---

## C13 量化

**目录**：`code/C13/`

| 文件 | 说明 |
|------|------|
| `01_qwen2.5_llmcompressor.ipynb` | 使用 LLM Compressor 对 Qwen2.5 进行 PTQ 量化（INT8/INT4） |

对应概念：[量化推理与服务部署](../concepts/inference-deployment.md)

---

## C14 服务部署

**目录**：`code/C14/`

### ner_deployment/ — 生产级 NER 服务

| 文件/目录 | 说明 |
|-----------|------|
| `main.py` | FastAPI 应用入口（路由/请求响应模型/服务启动） |
| `predict.py` | 模型加载和推理逻辑 |
| `src/tokenizer/` | 分词器（CharTokenizer/Vocabulary/Base） |
| `src/utils/file_io.py` | 文件 I/O 工具 |
| `data/categories.json` | 实体类别 |
| `data/vocabulary.json` | 词表 |
| `checkpoints/config.json` | 模型检查点配置 |
| `Dockerfile` | Docker 镜像构建文件 |
| `docker-compose.yml` | Docker Compose 服务编排 |
| `pyproject.toml` | Python 项目依赖管理（uv） |

### 其他文件

| 文件 | 说明 |
|------|------|
| `01_main.py` | FastAPI 基础示例 |
| `01_test.py` | 服务测试脚本 |

对应概念：[量化推理与服务部署](../concepts/inference-deployment.md)

---

## C19 图文多模态

**目录**：`code/C19/`

| 文件 | 说明 |
|------|------|
| `02_clip.py` | CLIP 模型实现——图像编码器/文本编码器/对比学习损失/零样本分类 |

对应概念：[大模型安全与多模态前沿](../concepts/safety-multimodal.md)

---

## C20 视觉问答

**目录**：`code/C20/seeker-omni/` — 从零训练简化版 Omni 多模态模型

### 配置（configs/）

| 文件 | 说明 |
|------|------|
| `model/base_26m.yaml` | 26M 参数模型架构配置 |
| `stages/s0.yaml` | 预训练阶段配置 |
| `stages/sft_text.yaml` | 文本 SFT 阶段配置 |
| `e2e.yaml` | 端到端训练配置 |
| `train.yaml` | 训练配置 |

### 数据准备（dataprep/）

| 模块 | 说明 |
|------|------|
| `download/flickr8k.py` | Flickr8k 数据集下载与解析 |
| `download/minimind.py` | minimind 数据集下载 |
| `download/cleaning.py` | 数据清洗 |
| `prepare/text_bpe.py` | BPE 分词器训练 |
| `prepare/memmap.py` | 内存映射数据格式 |
| `prepare/packed_builder.py` | 打包序列构建 |
| `prepare/sft_builder.py` | SFT 数据构建 |
| `prepare/tokenizer.py` | 分词器封装 |

### 模型（seeker_omni/model/）

| 文件 | 说明 |
|------|------|
| `attention.py` | 多头注意力 |
| `block.py` | Transformer Block |
| `lm.py` | 语言模型主体 |
| `mlp.py` | 前馈网络 |
| `norm.py` | 层归一化/RMSNorm |
| `rope.py` | RoPE 旋转位置编码 |
| `projector.py` | 视觉-语言模态投影器 |
| `resampler.py` | 视觉特征重采样器 |

### 训练（seeker_omni/）

| 模块 | 说明 |
|------|------|
| `steps/e2e/runner.py` | 端到端训练运行器 |
| `steps/e2e/vision.py` | 视觉训练步骤 |
| `steps/e2e/distill.py` | 知识蒸馏 |
| `train/loop.py` | 训练循环 |
| `train/checkpoint.py` | 检查点管理 |
| `train/lr.py` | 学习率调度 |
| `train/seed.py` | 随机种子 |
| `pipeline.py` | 训练流水线 |
| `config.py` | 配置加载 |

对应概念：[大模型安全与多模态前沿](../concepts/safety-multimodal.md)

---

## Extra-chapter

**目录**：`Extra-chapter/minimax-api-tutorial/`

| 文件 | 说明 |
|------|------|
| `code/01_basic_chat.py` | MiniMax API 基础对话 |
| `code/02_streaming.py` | 流式输出 |
| `code/03_multi_turn.py` | 多轮对话 |
| `code/04_long_context.py` | 长上下文处理 |
| `code/requirements.txt` | 依赖列表 |
| `readme.md` | 教程说明 |
