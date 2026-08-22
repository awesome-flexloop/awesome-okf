---
type: Example
title: Second-Me 分层记忆模型解析
description: 从 L0 原始摄取到 L1 身份洞察到 L2 LoRA 对齐——Second-Me 三层记忆架构（HMM）的完整数据管线与代码级走读
tags: [ai-agent, memory, second-me, hmm, lora, dpo, personalization, identity-modeling]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T02:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md#second-me
---

# Second-Me 分层记忆模型解析

Second-Me（mindverse 项目）实现了本知识包中最独特的记忆架构——**分层记忆建模（Hierarchical Memory Modeling, HMM）**。与其他框架将记忆存储在外部数据库中不同，Second-Me 通过 L0→L1→L2 三阶段渐进式抽象，最终将用户身份特征**注入模型权重**（LoRA 微调），实现"AI 原生记忆"。本示例走读三层架构的核心代码和数据流。

## 1. 架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                    Second-Me 记忆架构                          │
│                                                              │
│  L0: 原始摄取层                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 文件/对话/笔记/图片 → Insighter + Summarizer            ││
│  │ 输出: FileInfo, BioInfo (global_bio/status_bio/about_me)││
│  └──────────────────────────┬──────────────────────────────┘│
│                             │ L0→L1 传递                     │
│  L1: 身份洞察层            ▼                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Chunk 分块 + 主题提取 + 阴影生成 + 状态传记              ││
│  │ 输出: Chunks(embedding/tags/topic/type), Topics,        ││
│  │       Shades(矛盾特质), StatusBio, SerializedIdentity   ││
│  └──────────────────────────┬──────────────────────────────┘│
│                             │ L1→L2 训练数据生成              │
│  L2: 模型对齐层            ▼                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ SelfQA + Preference Pairs + Context Data + Diversity   ││
│  │ → LoRA 微调 → DPO 对齐 → GGUF 量化导出                  ││
│  │ 输出: 个性化模型权重 (.gguf / LoRA adapter)             ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  网络层（可选）: AI Space 多人协作 + Roleplay 人格切换         │
└─────────────────────────────────────────────────────────────┘
```

## 2. L0：原始记忆摄取

L0 是记忆管道的入口，负责将原始输入（文件、对话、图片）转化为初步结构化的数据。

### 核心数据契约

```python
# lpm_kernel/L0/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class FileInfo:
    """文件元数据——所有经过 L0 处理的文件都有这个记录"""
    file_path: str
    file_type: str           # pdf/md/txt/docx/epub/image/html/...
    file_size: int
    created_at: datetime
    content_hash: str        # 用于去重和变更检测
    processed: bool = False
    error: Optional[str] = None

@dataclass
class BioInfo:
    """三层传记信息——L0 输出的用户画像初稿"""
    global_bio: str = ""     # 全局传记："这个人是谁"（长期稳定）
    status_bio: str = ""     # 状态传记："最近在做什么/关注什么"（动态更新）
    about_me: str = ""       # 自我描述：用户自己写的简介（最高可信度）
    last_updated: datetime = field(default_factory=datetime.now)
```

### L0 处理流程

```python
# lpm_kernel/L0/l0_generator.py (概念性)
class L0Generator:
    def __init__(self, llm_client, embedding_service):
        self.llm = llm_client
        self.embedding = embedding_service
        self.processors = self._load_processors()  # 多格式处理器
    
    async def process_file(self, file_path: str) -> FileInfo:
        """处理单个文件，提取内容和初步摘要"""
        # 1. 文件类型检测和处理器选择
        file_type = detect_file_type(file_path)
        processor = self.processors[file_type]
        
        # 2. 提取文本内容
        content = await processor.extract_text(file_path)
        
        # 3. Insighter 阶段：提取关键洞察
        insights = await self._insight(content, file_type)
        
        # 4. Summarizer 阶段：生成摘要
        summary = await self._summarize(content, insights)
        
        # 5. 更新 BioInfo
        await self._update_bio(insights, summary)
        
        return FileInfo(
            file_path=file_path,
            file_type=file_type,
            file_size=get_file_size(file_path),
            created_at=datetime.now(),
            content_hash=hash_content(content),
            processed=True
        )
    
    async def _insight(self, content: str, file_type: str) -> dict:
        """使用 LLM 从内容中提取关键洞察"""
        prompt = f"""Analyze the following content and extract:
1. Key facts about the user
2. Recurring themes/interests
3. Behavioral patterns
4. Emotional tone indicators
5. Explicit preferences stated

Content type: {file_type}
Content: {truncate(content, 10000)}
"""
        return await self.llm.structured_complete(prompt)
    
    async def _summarize(self, content: str, insights: dict) -> str:
        """生成摘要，整合 LLM 洞察"""
        # ...
```

### 格式处理器

L0 通过 `file_data/processors/` 支持多种文件格式：

| 处理器 | 格式 | 提取方式 |
|--------|------|---------|
| PDF processor | .pdf | Docling（保留表格/代码）|
| Markdown processor | .md | 直接解析 |
| Text processor | .txt/.rst/.adoc | 纯文本 |
| Image processor | .png/.jpg/.jpeg | Vision 模型描述 |
| DOCX processor | .docx | python-docx |
| EPUB processor | .epub | ebooklib |
| HTML processor | .html | BeautifulSoup |

## 3. L1：身份洞察层

L1 是 HMM 的核心抽象层——从原始记忆中提取结构化的身份特征。

### Chunk 记忆块

```python
# lpm_kernel/L1/bio.py
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

class MemoryType(Enum):
    """记忆类型分类"""
    SUBJECT = "subject"    # 主观内容：观点、感受、偏好
    OBJECT = "object"      # 客观内容：事实、事件、知识
    CHAT = "chat"          # 对话内容：交互记录

class AnalysisType(Enum):
    """分析类型"""
    INSIGHT = "insight"    # 洞察类
    FACT = "fact"          # 事实类
    PREFERENCE = "preference"  # 偏好类
    PATTERN = "pattern"    # 模式类

class TimeType(Enum):
    """时间分层"""
    RECENT = "recent"      # 1天内（高权重）
    EARLIER = "earlier"    # 7天内（中权重）
    ARCHIVE = "archive"    # 更早（低权重，按需检索）

@dataclass
class Chunk:
    """记忆块——L1 的基本存储单元"""
    id: str
    content: str
    embedding: list[float]       # 向量表示
    tags: list[str] = field(default_factory=list)
    topic: str = ""              # 主题标签
    memory_type: MemoryType = MemoryType.OBJECT
    analysis_type: AnalysisType = AnalysisType.FACT
    time_type: TimeType = TimeType.RECENT
    timestamp: datetime = field(default_factory=datetime.now)
    source_file: Optional[str] = None  # 溯源到 L0 文件
    importance: float = 1.0      # 重要性评分（0-1）
    confidence: float = 1.0      # 置信度
```

### L1 生成器管道

```python
# lpm_kernel/L1/l1_generator.py (概念性)
class L1Generator:
    async def generate(self, l0_data: L0Data) -> L1Identity:
        """从 L0 数据生成 L1 身份模型"""
        # 步骤 1：内容分块
        chunks = await self._chunk_content(l0_data)
        
        # 步骤 2：为每个 chunk 生成 embedding 和标签
        for chunk in chunks:
            chunk.embedding = await self.embedding.embed(chunk.content)
            chunk.tags = await self._extract_tags(chunk.content)
            chunk.topic = await self._classify_topic(chunk.content)
            chunk.memory_type = await self._classify_type(chunk.content)
        
        # 步骤 3：主题提取
        topics = await self._extract_topics(chunks)
        
        # 步骤 4：生成人格阴影（矛盾特质）
        shades = await self._generate_shades(chunks)
        
        # 步骤 5：更新状态传记
        status_bio = await self._update_status_bio(
            l0_data.bio_info.status_bio, chunks
        )
        
        return L1Identity(
            chunks=chunks,
            topics=topics,
            shades=shades,
            status_bio=status_bio,
            global_bio=l0_data.bio_info.global_bio
        )
```

### 人格阴影（Shade）生成

`shade_generator.py` 是 Second-Me 最独特的设计之一——它提取用户**行为中体现但未明确表达**的矛盾特质：

```python
# lpm_kernel/L1/shade_generator.py (概念性)
async def generate_shades(chunks: list[Chunk]) -> list[Shade]:
    """
    生成"人格阴影"——捕捉用户的矛盾特质和隐性特征。
    例如：声称喜欢简单但实际使用复杂工具；
          说自己内向但在某些话题上非常活跃。
    """
    prompt = """Analyze these memory chunks for contradictions and implicit traits:
1. Explicit statements vs. behavioral evidence
2. Stated preferences vs. actual choices
3. Emotional contradictions
4. Unexpressed but evident values
5. Recurring tensions in self-presentation

For each shade found, provide:
- name: Short label for this contradictory trait
- surface: What the user explicitly says/presents
- shadow: What behavior/choices actually reveal
- evidence: Specific chunks supporting this
- strength: How strong this contradiction appears (0-1)
"""
    # 调用 LLM 分析
    shades = await llm.structured_complete(prompt, format=list[Shade])
    return shades
```

阴影的作用是让 AI 分身更真实——真实的人类不是单一特质的集合，而是充满内在矛盾。忽略阴影会导致 AI 分身过于"扁平"。

### 主题提取

`topics_generator.py` 使用聚类和分类提取用户经常讨论/关注的主题：

```python
async def extract_topics(chunks: list[Chunk]) -> list[Topic]:
    """
    主题提取流程：
    1. 使用 embedding 聚类
    2. 对每个聚类生成主题标签
    3. 计算主题频率和情感倾向
    4. 识别核心主题 vs 边缘主题
    """
    # 聚类
    clusters = await cluster_embeddings(
        [c.embedding for c in chunks],
        min_cluster_size=3
    )
    
    topics = []
    for cluster_id, cluster_chunks in clusters.items():
        label = await self._generate_topic_label(cluster_chunks)
        topics.append(Topic(
            name=label,
            chunks=[c.id for c in cluster_chunks],
            frequency=len(cluster_chunks) / len(chunks),
            sentiment=await self._analyze_sentiment(cluster_chunks)
        ))
    
    return sorted(topics, key=lambda t: t.frequency, reverse=True)
```

### 时间分层策略

```python
def classify_time_type(timestamp: datetime) -> TimeType:
    """时间分层"""
    age = datetime.now() - timestamp
    if age.days <= 1:
        return TimeType.RECENT    # 1天内：高权重
    elif age.days <= 7:
        return TimeType.EARLIER   # 7天内：中权重
    else:
        return TimeType.ARCHIVE   # 更早：低权重
```

时间分层影响记忆检索时的权重——近期记忆权重更高。

## 4. L2：模型训练与对齐

L2 是最独特的层——它不将记忆存储在外部数据库，而是通过**LoRA 微调 + DPO 对齐**将身份特征注入模型权重。

### 训练数据生成

```python
# lpm_kernel/L2/l2_generator.py (概念性)
class L2DataGenerator:
    def generate_training_data(self, l1_identity: L1Identity) -> TrainingData:
        """从 L1 身份模型生成训练数据"""
        
        # 1. SelfQA：模型自问自答关于用户的问题
        self_qa = self._generate_self_qa(l1_identity)
        
        # 2. 偏好对比（DPO 训练数据）
        preference_pairs = self._generate_preference_pairs(l1_identity)
        
        # 3. 上下文数据：典型对话场景
        context_data = self._generate_context_data(l1_identity)
        
        # 4. 多样性数据：覆盖不同话题和风格
        diversity_data = self._generate_diversity_data(l1_identity)
        
        return TrainingData(
            self_qa=self_qa,
            preference_pairs=preference_pairs,
            context_data=context_data,
            diversity_data=diversity_data
        )
    
    def _generate_self_qa(self, identity: L1Identity) -> list[QA]:
        """SelfQA：让模型生成关于用户的问答对"""
        prompt = f"""Based on this identity model, generate Q&A pairs that capture who this person is:
- Ask questions someone would ask about this person
- Answer in the first person (as if you ARE this person)
- Cover: background, preferences, expertise, communication style, values

Global Bio: {identity.global_bio}
Topics: {[t.name for t in identity.topics]}
Shades: {[s.name for s in identity.shades]}
"""
        return self.llm.structured_complete(prompt)
    
    def _generate_preference_pairs(self, identity: L1Identity) -> list[PreferencePair]:
        """生成偏好对比对（chosen vs rejected）用于 DPO"""
        pairs = []
        for chunk in identity.chunks:
            if chunk.memory_type == MemoryType.SUBJECT:
                # 主观内容：用户的表达方式是 chosen，替代表达是 rejected
                chosen = chunk.content
                rejected = self._generate_alternative(chunk.content, style="generic")
                pairs.append(PreferencePair(
                    prompt="Respond in the user's style",
                    chosen=chosen,
                    rejected=rejected
                ))
        return pairs
```

### LoRA 训练

```python
# lpm_kernel/L2/train.py (概念性)
async def train_lora(
    training_data: TrainingData,
    base_model: str,
    output_dir: str,
    config: TrainConfig = TrainConfig()
) -> LoRAModel:
    """基于 L1/L2 数据训练 LoRA 适配器"""
    
    # 1. 加载基础模型
    model = load_model(base_model, load_in_4bit=config.load_in_4bit)
    tokenizer = load_tokenizer(base_model)
    
    # 2. 配置 LoRA
    lora_config = LoraConfig(
        r=config.lora_rank,           # LoRA rank（通常 8-64）
        lora_alpha=config.lora_alpha,
        target_modules=find_linear_layers(model),
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # 3. 准备训练数据
    dataset = create_dataset(training_data, tokenizer)
    
    # 4. SFT 训练（Supervised Fine-Tuning）
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            output_dir=output_dir,
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            fp16=config.fp16,
        ),
        peft_config=lora_config,
    )
    trainer.train()
    
    # 5. DPO 对齐
    if training_data.preference_pairs:
        dpo_trainer = DPOTrainer(
            model=model,
            ref_model=None,  # LoRA 模式下不需要单独的 ref model
            args=DPOConfig(...),
            train_dataset=create_dpo_dataset(training_data.preference_pairs),
            tokenizer=tokenizer,
        )
        dpo_trainer.train()
    
    # 6. 保存 LoRA adapter
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    return LoRAModel(path=output_dir, base_model=base_model)
```

### MLX 加速（Apple Silicon）

L2 支持 Apple M 系列芯片的 MLX 加速：

```python
# lpm_kernel/L2/mlx_training/ (概念性)
def train_lora_mlx(training_data, base_model, output_dir):
    """使用 Apple MLX 框架在 M 系列芯片上加速训练"""
    # MLX 专为 Apple Silicon 的 Unified Memory 设计
    # 比 PyTorch CPU 训练快 5-10x
    ...
```

### GGUF 量化导出

训练完成后，模型可以导出为 GGUF 格式供 llama.cpp 推理：

```python
# lpm_kernel/L2/gguf-py/ (概念性)
def export_gguf(lora_model: LoRAModel, output_path: str, quantize: str = "Q4_K_M"):
    """合并 LoRA 权重并导出为量化 GGUF"""
    # 1. 将 LoRA 权重合并到基础模型
    merged = merge_lora(lora_model)
    # 2. 转换为 GGUF 格式
    gguf_model = convert_to_gguf(merged)
    # 3. 量化（Q4_K_M 在质量和大小间取得平衡）
    quantized = quantize(gguf_model, quantize)
    quantized.save(output_path)
```

## 5. 记忆检索：GraphRAG + ChromaDB

Second-Me 使用 GraphRAG 增强记忆检索：

```python
# lpm_kernel/L2/data_pipeline/graphrag_indexing/ (概念性)
class GraphRAGMemory:
    """基于知识图谱的记忆检索"""
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        """混合检索：向量 + 图谱 + 关键词"""
        # 1. 向量检索（找到语义相似的 chunks）
        vector_results = await self.vector_search(query, top_k=top_k * 2)
        
        # 2. 图谱扩展（找到相关实体的关联 chunks）
        entities = self.extract_entities(query)
        graph_results = self.graph.neighbors(entities, depth=2)
        
        # 3. RRF 融合
        results = self.rrf_merge(vector_results, graph_results)
        
        # 4. 时间衰减加权
        results = self.apply_time_decay(results)
        
        return results[:top_k]
```

文件处理子系统使用 ChromaDB 作为向量存储：

```python
# lpm_kernel/file_data/chroma_utils.py
class ChromaStore:
    """ChromaDB 向量存储"""
    async def add(self, chunks: list[Chunk]): ...
    async def query(self, embedding: list[float], top_k: int = 5) -> list[Chunk]: ...
    async def delete(self, chunk_id: str): ...
```

## 6. AI Space：去中心化协作

Second-Me 的网络层允许多个 Second Me 协作：

```python
# lpm_kernel/api/domains/space/ (概念性)
class AISpaceService:
    async def create_discussion(self, topic: str, participants: list[SecondMe]):
        """创建多人 AI 讨论空间"""
        # Host 策略：引导讨论、综合观点
        host = self.select_host(participants)
        host_strategy = HostStrategy(topic=topic)
        
        # Participant 策略：基于各自记忆发表观点
        participant_strategies = [
            ParticipantStrategy(
                memory=p.get_l1_identity(),
                model=p.get_l2_model(),
                role=p.role
            )
            for p in participants
        ]
        
        # 运行讨论轮次
        for round in range(config.max_rounds):
            # 收集 participant 观点
            opinions = await asyncio.gather(*[
                ps.contribute(host.last_message)
                for ps in participant_strategies
            ])
            # Host 综合
            synthesis = await host_strategy.synthesize(opinions)
        
        return synthesis
```

## 7. API 层：FastAPI 服务

```python
# lpm_kernel/api/domains/kernel2/services/ (概念性)
# 聊天服务
class ChatService:
    async def chat(self, message: str, session_id: str) -> AsyncIterator[str]:
        """流式聊天，使用 L2 模型 + L1 记忆检索"""
        # 1. 检索相关记忆
        memories = await self.memory.retrieve(message)
        # 2. 构建上下文（包含 L1 身份信息）
        context = self.build_context(memories, session_id)
        # 3. 使用 L2 模型推理
        async for chunk in self.l2_model.stream_chat(context, message):
            yield chunk
```

## 8. 三层层级对比总结

| 维度 | L0 原始层 | L1 身份层 | L2 对齐层 |
|------|----------|----------|----------|
| 存储形式 | 文件系统+数据库 | 结构化数据（Chunks/Topics/Shades） | 模型权重（LoRA/GGUF） |
| 处理方式 | 文本提取+摘要 | LLM深度分析+聚类 | SFT+DPO训练 |
| 核心产出 | FileInfo, BioInfo | 身份特征（传记/主题/阴影） | 个性化模型 |
| 检索方式 | 直接读取 | 向量检索+图谱+RRF | 模型前向传播（无需检索） |
| 类比 | 感知和经历 | 记忆和自我认知 | 技能和本能 |
| 更新频率 | 每次新文件/对话 | 每次新数据增量更新 | 定期重训练 |
| Token成本 | 低（提取+摘要） | 中（深度分析） | 高（模型训练） |

## 关键收获

Second-Me 的 HMM 架构提供了 Agent 记忆的全新范式：

1. **渐进式抽象**：L0→L1→L2 是一个从原始数据到身份模型的渐进式蒸馏管道，每层都在上层基础上增加抽象深度
2. **模型内化 vs 外部检索**：L2 将记忆内化为模型权重，推理时不需要检索（节省 token），但需要训练成本
3. **人格阴影**：捕捉矛盾特质而非只看表面声明，让 AI 分身更真实
4. **时间分层**：Recent/Earlier/Archive 三档时间权重，模拟人类记忆的遗忘曲线
5. **去中心化协作**：AI Space 的 host/participant 双策略模式，探索了 Agent-to-Agent 社交协议
6. **本地优先隐私**：所有训练和推理在本地运行（Docker 部署），数据不出设备
