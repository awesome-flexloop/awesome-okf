---
type: Example
title: 训练个人AI
description: 通过 Second-Me 的三层记忆架构（L0→L1→L2），从文档上传到 LoRA 微调，完成个人 AI 数字分身的完整训练流程。
tags: [second-me, example, training, lora, l0, l1, l2, personal-ai]
generated: { by: "agent:okf-wiki-generator", at: "2026-08-22T22:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /.spec/facts.md
    title: Second-Me 源码事实清单
---

## 场景说明

你需要训练一个属于自己的 AI 数字分身。流程分为三个核心阶段：

1. **L0 层（原始记忆处理）**：上传个人文档（聊天记录、笔记、文章等），系统提取洞察和摘要
2. **L1 层（身份洞察）**：基于记忆生成人格侧面（Shade）、传记（Bio）和主题聚类
3. **L2 层（模型对齐）**：通过 LoRA 微调基础模型，使模型学会你的表达风格和思维模式

## 前置条件

### 硬件要求

| 配置 | CPU模式 | GPU模式 |
|------|---------|---------|
| 内存 | ≥16GB | ≥16GB |
| GPU | 不需要 | ≥8GB VRAM（推荐 NVIDIA GPU） |
| 磁盘 | ≥20GB（含基础模型） | ≥20GB |

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/mindverse/Second-Me.git
cd Second-Me

# 使用 Docker Compose 启动（推荐）
# CPU 版本
docker-compose up -d

# GPU 版本（需要 NVIDIA Docker runtime）
docker-compose -f docker-compose-gpu.yml up -d
```

服务启动后：
- 后端 API：`http://localhost:8002`
- 前端界面：`http://localhost:3000`

## 完整训练流程

### 阶段 1：上传文档（L0 原始记忆）

L0 层负责处理原始输入数据，支持三种数据类型：

| 类型 | 支持格式 | 处理方式 |
|------|---------|---------|
| 文档（DOCUMENT） | .txt, .pdf, .md | TokenTextSplitter 分块 + chunk_filter 采样 → 生成 insight 和 title |
| 图片（IMAGE） | 常见图片格式 | 3段 prompt 调用链 → 生成 summary 和 title |
| 音频（AUDIO） | 常见音频格式 | 超过1200秒自动分段 → 生成 insight 和 title |

#### 1.1 通过 API 上传文件

```bash
# 上传记忆文件
curl -X POST http://localhost:8002/api/memories/file \
  -F "file=@/path/to/your/notes.pdf"

# 支持的格式：txt, pdf, md
# 上传后文件保存到 USER_RAW_CONTENT_DIR
```

#### 1.2 扫描并分析文档

```bash
# 扫描目录中的文档
curl -X POST http://localhost:8002/api/documents/scan

# 分析所有未处理文档（生成 L0 洞察）
curl -X POST http://localhost:8002/api/documents/analyze
```

L0Generator 在分析时执行以下步骤：

```python
# L0 处理流程（概念示意，实际由 API 自动完成）
from lpm_kernel.L0.l0_generator import L0Generator
from lpm_kernel.L0.models import InsighterInput, FileInfo, DocumentType

generator = L0Generator(preferred_language="Chinese")

# 1. 文档洞察生成
insighter_input = InsighterInput.from_dict({
    "data_type": "DOCUMENT",
    "filename": "my-notes.pdf",
    "content": file_content,
    "file_content": raw_file_bytes,
    # BioInfo 可选，用于个性化生成
    "bio_info": {
        "global_bio": "",
        "status_bio": "",
        "about_me": "软件工程师，喜欢开源项目"
    }
})

# 返回 {"title": str, "insight": str}
result = generator.insighter(insighter_input)

# 2. 摘要生成
from lpm_kernel.L0.models import SummarizerInput
summarizer_input = SummarizerInput.from_dict({
    "data_type": "DOCUMENT",
    "filename": "my-notes.pdf",
    "content": file_content,
    "insight": result["insight"]
})

# 返回 title/summary/keywords 三元组
summary = generator.summarizer(summarizer_input)
```

#### 1.3 文档分块与 Embedding

```bash
# 批量分块处理
curl -X POST http://localhost:8002/api/documents/chunks/process

# 块级 embedding
curl -X POST http://localhost:8002/api/documents/{id}/chunk/embedding

# 文档级 embedding
curl -X POST http://localhost:8002/api/documents/{id}/embedding
```

L0 层数据模型关系：

```
FileInfo (原始文件)
  ↓ insighter()
{title, insight} (洞察结果)
  ↓ summarizer()
{title, summary, keywords} (摘要三元组)
  ↓ chunking
Chunk[] (文档分块，含 embedding 向量)
  ↓ clustering
Cluster[] (记忆簇，按 DISTANCE_RATE=0.8 剪枝离群点)
```

### 阶段 2：生成身份洞察（L1 层）

L1 层基于 L0 处理后的记忆，生成结构化的人格画像。

#### 2.1 L1 核心数据结构

```python
from lpm_kernel.L1.bio import (
    Chunk, Note, Cluster, ShadeInfo, ShadeTimeline,
    Bio, UserInfo, TimeType, MemoryType, ConfidenceLevel
)

# Note 是 L1 的核心记忆单元
note = Note(
    id="note-uuid",
    content="记忆内容文本",
    create_time=datetime.now(),
    memory_type=MemoryType.TEXT,  # TEXT/MARKDOWN/PDF/LINK
    embedding=np.array([...]),    # 1536维向量 (DEFAULT_EMBEDDING_DIM=1536)
    chunks=[chunk1, chunk2],
    title="记忆标题",
    summary="摘要",
    insight="洞察",
    tags=["技术", "开源"],
    topic="编程"
)

# ShadeInfo 表示一个人格侧面
shade = ShadeInfo(
    id="shade-uuid",
    name="开源贡献者",
    aspect="专业",         # 侧面维度
    icon="💻",
    desc={
        "third_view": "他是一个活跃的开源贡献者...",  # 第三人称
        "second_view": "你是一个活跃的开源贡献者..."  # 第二人称（用于对话）
    },
    content={
        "third_view": "详细描述...",
        "second_view": "详细描述..."
    },
    timelines=[ShadeTimeline(
        refMemoryId="note-uuid",
        createTime=datetime.now(),
        descSecondView="在某时做了某事...",
        descThirdView="在某时做了某事..."
    )],
    confidence_level=ConfidenceLevel.HIGH
)
```

#### 2.2 L1 生成器

```python
from lpm_kernel.L1.l1_generator import L1Generator

l1_generator = L1Generator()

# L1Generator 组合使用四个子生成器：
# 1. ShadeGenerator - 生成人格侧面
# 2. ShadeMerger - 合并相似侧面
# 3. StatusBioGenerator - 生成状态传记
# 4. TopicsGenerator - 生成主题标签

# UserInfo 聚合用户所有记忆
from lpm_kernel.L1.bio import UserInfo, Todo, Chat

user_info = UserInfo(
    notes=note_list,      # 笔记列表（按 create_time 降序）
    todos=todo_list,      # 待办事项
    chats=chat_list       # 聊天记录
)

# 时间窗口划分
recent = user_info.get_range_memories(TimeType.RECENT)   # 1天内，最少3条
earlier = user_info.get_range_memories(TimeType.EARLIER) # 7天内，最少10条
```

#### 2.3 通过 API 触发生成

L0→L1 的转换在训练流水线中自动执行，你可以通过前端界面或 API 查看结果：

```bash
# 查看文档列表（含 L0 状态）
curl http://localhost:8002/api/documents/list?include_l0=true
```

### 阶段 3：模型微调（L2 层）

L2 层通过 LoRA 微调将你的人格特征注入基础模型。

#### 3.1 LoRA 配置参数

L2/train.py 中定义的默认 LoRA 参数（`ModelArguments`）：

```python
from lpm_kernel.L2.train import ModelArguments

# 默认 LoRA 配置
model_args = ModelArguments(
    model_name_or_path="meta-llama/Llama-3.1-8B-Instruct",  # 基础模型
    lora_alpha=16,          # LoRA alpha 参数
    lora_dropout=0.1,       # LoRA dropout
    lora_r=64,              # LoRA 秩（rank），越大表达能力越强但显存需求越大
    lora_target_modules=[   # 目标模块（默认覆盖注意力+MLP全层）
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ]
)
```

| 参数 | 默认值 | 说明 | 建议调整 |
|------|--------|------|---------|
| lora_r | 64 | LoRA 秩 | 显存不足可降至 16/32 |
| lora_alpha | 16 | 缩放系数 | 通常设为 lora_r 的 1/4 |
| lora_dropout | 0.1 | 正则化 | 数据量少时可适当增大 |

#### 3.2 启动训练

通过前端界面：
1. 打开 `http://localhost:3000`
2. 进入 Train → Training 页面
3. 配置训练参数（学习率、epoch 数等）
4. 点击 "Start Training"

或通过 API：

```bash
# 启动训练（后台线程执行12步流水线）
curl -X POST http://localhost:8002/api/trainprocess/start \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "second-me-model",
    "learning_rate": 2e-4,
    "number_of_epochs": 3,
    "concurrency_threads": 2,
    "data_synthesis_mode": "full",
    "use_cuda": true,
    "is_cot": true
  }'
```

训练的12步流水线：

| 步骤 | 阶段 | 说明 |
|------|------|------|
| 1 | 健康检查 | 检查 LLM 配置和 GPU 可用性 |
| 2 | 生成 L0 | 处理所有上传文档 |
| 3 | 文档 embedding | 生成文档级向量 |
| 4 | 分块 | 将文档拆分为 Chunk |
| 5 | Chunk embedding | 生成块级向量 |
| 6 | 分析文档 | 聚类、生成 Note |
| 7 | 生成 L1 | 生成 Bio/Shade/Topics |
| 8 | 下载模型 | 下载基础模型（如 Llama） |
| 9 | 准备数据 | 生成 SFT/DPO 训练数据 |
| 10 | 训练模型 | LoRA 微调 |
| 11 | 合并权重 | 将 LoRA 合并到基础模型 |
| 12 | 转换模型 | 转换为部署格式（可选 GGUF/MLX） |

#### 3.3 监控训练进度

```bash
# SSE 实时日志流
curl http://localhost:8002/api/trainprocess/logs

# 获取训练进度
curl http://localhost:8002/api/trainprocess/progress/second-me-model
```

训练阶段（前端显示的5个阶段）：

1. **downloading_the_base_model** — 下载基础模型
2. **activating_the_memory_matrix** — 激活记忆矩阵（L0+embedding+分块）
3. **synthesize_your_life_narrative** — 合成生活叙事（L1人格生成）
4. **prepare_training_data_for_deep_comprehension** — 准备训练数据
5. **training_to_create_second_me** — 训练模型

#### 3.4 训练数据生成

L2DataProcessor 生成四类训练数据：

```python
from lpm_kernel.L2.data import L2DataProcessor
from lpm_kernel.L2.l2_generator import L2Generator

l2_generator = L2Generator(
    data_path="../raw_data",
    preferred_lang="Chinese",
    is_cot=True  # 启用 Chain-of-Thought 训练
)

# 数据预处理
# split_notes_by_type 将笔记分为：
# - subjective_memory_notes: TEXT/MARKDOWN/PDF 类型（主观记忆）
# - objective_memory_notes: LINK 类型（客观记忆）
processed_data = l2_generator.data_preprocess(note_list, basic_info)

# 生成四类主观数据：
# 1. Preference QA - 偏好问答对
# 2. Diversity Data - 多样性数据
# 3. Self-QA - 自我问答
# 4. Graph Indexing - 图谱索引
subjective_data = l2_generator.gen_subjective_data(
    note_list, basic_info,
    # ...其他参数
)
```

#### 3.5 合并 LoRA 权重

训练完成后，需要将 LoRA 适配器合并到基础模型：

```python
from lpm_kernel.L2.merge_lora_weights import merge_lora_weights

merge_lora_weights(
    base_model_path="meta-llama/Llama-3.1-8B-Instruct",
    lora_adapter_path="./output/lora-adapter",
    output_model_path="./output/second-me-merged"
)
# 自动检测 CUDA：cuda→float16, cpu→float32
```

#### 3.6 可选：DPO 训练

除了 SFT（监督微调），还支持 DPO（直接偏好优化）：

```python
# DPO 训练使用 TRL 库的 DPOTrainer
# 训练数据格式：{"prompt": [system, user], "chosen": str, "rejected": str}
# lora_r=0 时禁用 LoRA（全参数 DPO）
```

#### 3.7 可选：GGUF/MLX 格式转换

```bash
# 转换为 GGUF（用于 llama.cpp 等推理引擎）
python lpm_kernel/L2/convert_hf_to_gguf.py \
  --input ./output/second-me-merged \
  --output ./output/second-me.gguf \
  --outtype q8_0

# MLX 格式（Apple Silicon 优化）
# 使用 lpm_kernel/L2/mlx_training/ 目录下的脚本
```

### 阶段 4：验证与对话

训练完成后，通过 API 测试对话：

```bash
# 流式聊天（SSE）
curl -X POST http://localhost:8002/api/talk/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，你是谁？",
    "enable_l0_retrieval": true,
    "enable_l1_retrieval": true,
    "temperature": 0.7,
    "max_tokens": 2048
  }'

# 非流式 JSON 响应
curl -X POST http://localhost:8002/api/talk/chat_json \
  -H "Content-Type: application/json" \
  -d '{
    "message": "介绍一下你自己",
    "enable_l0_retrieval": true,
    "enable_l1_retrieval": true
  }'
```

对话时的 Prompt 构建使用责任链/装饰器模式：

```
用户消息
  ↓ BasePromptStrategy（提取 system message）
  ↓ KnowledgeEnhancedStrategy（注入 L0/L1 检索知识）
  ↓ RoleBasedStrategy（应用角色 system_prompt）
  ↓ ContextEnhancedStrategy/ContextCriticStrategy（可选增强）
  ↓ 最终 Prompt → LLM
```

## 训练参数调优建议

| 场景 | learning_rate | epochs | lora_r | 说明 |
|------|--------------|--------|--------|------|
| 快速验证 | 5e-4 | 1-2 | 16 | 快速看到效果，可能过拟合 |
| 标准训练 | 2e-4 | 3 | 64 | 默认配置，平衡质量与速度 |
| 高质量 | 1e-4 | 5-10 | 128 | 更多数据+更长训练，质量更好 |
| 数据稀少 | 1e-4 | 2-3 | 32 | 避免过拟合，增大 lora_dropout |

## 训练排障

1. **CUDA out of memory**：降低 lora_r（如 64→16），减小 batch_size，使用 CPU 模式
2. **下载模型慢**：设置 HuggingFace 镜像 `HF_ENDPOINT=https://hf-mirror.com`
3. **L1 生成质量差**：增加上传文档数量（建议 ≥50 条有效记忆）
4. **对话不连贯**：增加 epochs 或调整 temperature（0.5-0.8 范围较好）
5. **查看实时日志**：通过 SSE 端点 `/api/trainprocess/logs` 查看详细进度

## 停止/重新训练

```bash
# 停止训练
curl -X POST http://localhost:8002/api/trainprocess/stop

# 重新训练（重置进度）
curl -X POST http://localhost:8002/api/trainprocess/retrain
```

## 相关概念

- [三层记忆架构 HMM](../concepts/three-layer-memory-hmm.md)
- [L0 原始记忆层](../concepts/l0-raw-memory.md)
- [L1 语义网络层](../concepts/l1-semantic-network.md)
- [L2 推理模型层](../concepts/l2-inference-model.md)
- [训练流水线](../concepts/training-pipeline.md)
- [Flask API 服务](../concepts/flask-api-server.md)
