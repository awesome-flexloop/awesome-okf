---
type: Concept
title: 记忆架构
description: AI Agent 的短期/长期/分层记忆系统——从简单对话历史到三层身份建模（L0→L1→L2）与向量检索
tags: [ai-agent, memory, long-term-memory, short-term-memory, vector-search, hmm, personalization]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T01:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md
  - id: veadk
    resource: /references/ai-agent-sources.md#veadk-python
  - id: zleap
    resource: /references/ai-agent-sources.md#zleap-agent
  - id: secondme
    resource: /references/ai-agent-sources.md#second-me
---

# 记忆架构

记忆（Memory）是 Agent 超越"无状态 API 调用"的关键能力。没有记忆，Agent 每轮对话都是全新的；有了记忆，Agent 可以记住之前的交互、学习用户偏好、积累知识、形成身份。不同框架对"记忆"的理解深度差异巨大——从简单的对话历史缓冲区到三层身份建模架构。

## 记忆的分层模型

通过分析 veadk-python、Zleap-Agent 和 Second-Me 三个项目，可以识别出记忆的四个抽象层次：

```
┌─────────────────────────────────────────────────┐
│ L3: 身份/人格层（Second-Me L2）                  │  ← LoRA 微调注入模型权重
│   用户偏好、行为风格、价值观                       │
├─────────────────────────────────────────────────┤
│ L2: 长期知识层（veadk LongTermMemory, Zleap）    │  ← 向量数据库持久存储
│   历史对话摘要、知识库文档、可复用经验              │
├─────────────────────────────────────────────────┤
│ L1: 工作记忆层（veadk ShortTermMemory）           │  ← 当前对话窗口
│   本轮对话历史、当前任务上下文                      │
├─────────────────────────────────────────────────┤
│ L0: 原始感知层（Second-Me L0）                    │  ← 文件/消息摄取
│   原始文档、原始消息、未经处理的输入                │
└─────────────────────────────────────────────────┘
```

## veadk-python：短期/长期记忆分离

veadk-python 在 `veadk/memory/` 目录下实现了清晰的短期/长期记忆分离架构。

### ShortTermMemory（短期记忆）

短期记忆对应当前对话窗口，维护一个消息列表：

```python
# 概念性伪代码：veadk ShortTermMemory
class ShortTermMemory:
    """短期记忆：当前对话会话的消息历史"""
    
    def __init__(self, max_tokens: int = 8000):
        self.messages: list[Message] = []
        self.max_tokens = max_tokens
    
    def add(self, message: Message):
        """添加消息，超出预算时触发压缩/截断"""
        self.messages.append(message)
        self._maybe_compact()
    
    def get_context(self) -> list[Message]:
        """获取当前上下文窗口内的消息"""
        return self.messages
    
    def _maybe_compact(self):
        """当 token 数超过 max_tokens 时压缩早期消息"""
        # 策略：保留 system prompt + 最近 N 轮，摘要更早的消息
        pass
```

### LongTermMemory（长期记忆）

长期记忆支持多种后端实现，通过统一接口抽象：

```python
# 概念性伪代码：veadk LongTermMemory 后端
class LongTermMemory(ABC):
    """长期记忆抽象基类"""
    
    @abstractmethod
    async def store(self, content: str, metadata: dict = None):
        """存储记忆"""
        pass
    
    @abstractmethod
    async def recall(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        """根据查询向量检索相关记忆"""
        pass
    
    @abstractmethod
    async def forget(self, memory_id: str):
        """删除记忆"""
        pass
```

veadk-python 提供了 **7+ 种长期记忆后端实现**，包括：

| 后端 | 特点 | 适用场景 |
|------|------|---------|
| 内存后端（InMemory） | 进程内存储，重启丢失 | 测试/原型 |
| 文件后端（File） | JSON 文件持久化 | 轻量单机 |
| 向量数据库 | ChromaDB/pgvector 等 | 生产级语义检索 |
| 数据库后端 | SQL 数据库 | 结构化存储 |
| 混合后端 | 向量+关键词组合 | 高性能检索 |

### Agent 中的记忆集成

在 `Agent.model_post_init()` 中，记忆系统与 Agent 其他组件集成：

```python
class Agent(LlmAgent):
    short_term_memory: ShortTermMemory = Field(default_factory=ShortTermMemory)
    long_term_memory: LongTermMemory | None = None
    
    def model_post_init(self, __context):
        # 初始化短期记忆
        if not self.short_term_memory:
            self.short_term_memory = ShortTermMemory()
        # 初始化长期记忆（如果配置了）
        if self.long_term_memory_config:
            self.long_term_memory = self._create_long_term_memory()
```

## Zleap-Agent：分区记忆 + RRF 向量召回

Zleap-Agent 的记忆系统基于 PostgreSQL + pgvector 实现，核心特点是**记忆分区**和 **RRF（Reciprocal Rank Fusion）** 检索。

### 记忆三分区

Zleap-Agent 将长期记忆分为三个语义分区：

| 分区 | 存储内容 | 更新频率 |
|------|---------|---------|
| **人（Person）** | 用户偏好、习惯、风格 | 低频，稳定 |
| **事（Event）** | 事件状态、任务进展 | 中频，随任务变化 |
| **经验（Experience）** | 可复用方法、问题解决方案 | 高频，持续积累 |

### RRF 融合检索

Zleap 使用 RRF（Reciprocal Rank Fusion）算法融合多路召回结果：

```
RRF_score(d) = Σ 1/(k + rank_i(d))
```

其中 `k` 是常数（通常 60），`rank_i(d)` 是文档 d 在第 i 路召回中的排名。多路召回通常包括：
- 向量相似度（embedding cosine）
- 关键词匹配（BM25）
- 时间衰减（近期记忆权重更高）

### Context 组装

Zleap 在 `session_assembling` 阶段构建 Agent 可见的上下文：

```
Context = System Prompt
        + Workspace Prompt（当前 Workspace 专属指令）
        + Tools Description（当前 Workspace 可用工具）
        + Retrieved Memory（从三分区检索的相关记忆）
        + Conversation History（近期对话历史）
```

## Second-Me：三层记忆建模（HMM）

Second-Me（mindverse 项目）实现了最复杂的记忆架构——**分层记忆建模（Hierarchical Memory Modeling, HMM）**，通过 L0→L1→L2 三阶段从原始数据到模型权重的渐进式抽象。

### L0：原始记忆摄取

```
输入：文件、对话记录、笔记、图片
处理：Insighter（洞察提取）+ Summarizer（摘要）
输出：FileInfo（文件元数据）、BioInfo（初步传记信息）
```

核心数据结构：

```python
# lpm_kernel/L0/models.py
@dataclass
class FileInfo:
    """文件元数据"""
    file_path: str
    file_type: str  # pdf/md/txt/image/...
    file_size: int
    created_at: datetime
    content_hash: str

@dataclass
class BioInfo:
    """三层传记信息"""
    global_bio: str      # 全局传记："这个人是谁"
    status_bio: str      # 状态传记："最近在做什么"
    about_me: str        # 自我描述：用户自己写的简介
```

### L1：身份洞察与传记生成

L1 从 L0 的原始记忆中提取结构化的身份特征：

```python
# lpm_kernel/L1/bio.py
class Chunk:
    """记忆块"""
    content: str
    embedding: list[float]
    tags: list[str]
    topic: str
    memory_type: MemoryType    # SUBJECT(主观)/OBJECT(客观)/CHAT(对话)
    analysis_type: AnalysisType
    time_type: TimeType        # Recent(1天内)/Earlier(7天内)
    timestamp: datetime
```

L1 的子生成器包括：

| 生成器 | 功能 |
|--------|------|
| `l1_generator.py` | 主生成器：提取核心身份特征 |
| `shade_generator.py` | "人格阴影"：捕捉矛盾、隐性特质（不直接表达但行为中体现的特征） |
| `status_bio_generator.py` | 动态状态传记：最近的关注点和情绪状态 |
| `topics_generator.py` | 主题提取：用户经常讨论/关注的主题 |

时间分层策略：
- **Recent（1天内）**：高权重，直接影响当前行为
- **Earlier（7天内）**：中权重，提供近期背景
- **Archive（更早）**：低权重，通过向量检索按需召回

### L2：模型训练与对齐

L2 是最独特的层——它不将记忆存储在外部数据库中，而是通过 **LoRA 微调 + DPO（Direct Preference Optimization）** 将身份特征**注入模型权重**：

```
L1 身份特征 → 训练数据生成（偏好QA、SelfQA、多样性数据、上下文数据）
           → LoRA 微调（学习个人风格和知识）
           → DPO 对齐（学习偏好和价值观）
           → 个性化 AI 模型（.gguf 量化导出）
```

```python
# lpm_kernel/L2/train.py 概念
def train_lora(identity_data: L1Identity, base_model: str) -> LoRAModel:
    """基于 L1 身份数据训练 LoRA 适配器"""
    training_data = generate_training_data(identity_data)
    # 包含：
    # - SelfQA：模型自问自答，生成关于用户的知识
    # - Preference pairs：偏好对比（DPO 训练数据）
    # - Context data：典型对话场景
    # - Diversity data：覆盖不同话题和风格
    model = lora_finetune(base_model, training_data)
    return model

def dpo_align(model: LoRAModel, preferences: list[PreferencePair]):
    """DPO 对齐：让模型行为与用户偏好一致"""
    # DPO 直接从偏好对中学习奖励模型，无需显式 reward model
    pass
```

L2 还支持：
- **GraphRAG 索引**：在 L1 记忆上构建知识图谱，增强检索
- **MLX 加速**：Apple M 系列芯片上的 MLX 框架加速训练
- **GGUF 量化**：导出为 llama.cpp 可推理的量化格式

### 三层层级对比

| 层级 | 功能 | 存储形式 | 检索方式 | 类比 |
|------|------|---------|---------|------|
| L0 | 原始数据摄取 | 文件系统 | 直接读取 | 感知器官 |
| L1 | 身份洞察 | 结构化数据（Chunks/Topics/Shades） | 向量检索+图谱 | 工作记忆+长期记忆 |
| L2 | 模型对齐 | LoRA 权重 | 模型前向传播 | 技能/本能 |

## 记忆检索策略对比

| 策略 | veadk-python | Zleap-Agent | Second-Me |
|------|-------------|-------------|-----------|
| **向量检索** | ✅（ChromaDB等后端） | ✅（pgvector） | ✅（ChromaDB） |
| **关键词检索** | 取决于后端 | ✅（BM25） | ✅（文件处理器） |
| **混合检索** | 混合后端支持 | ✅（RRF融合） | ✅（GraphRAG） |
| **时间衰减** | 取决于后端 | ✅（Recent/Earlier分层） | ✅（TimeType分层） |
| **记忆分区** | ST/LT分离 | ✅（人/事/经验三分区） | ✅（L0/L1/L2三阶段） |
| **模型内化** | ❌ | ❌ | ✅（LoRA微调） |
| **记忆压缩** | ✅（ST compaction） | ✅（记忆压缩） | ✅（摘要+主题提取） |

## 记忆系统设计权衡

### 1. 外部检索 vs 模型内化

传统 RAG 方法（veadk/Zleap）将记忆存储在外部向量数据库，推理时检索相关片段注入上下文。优点是可更新、可解释、不需要训练；缺点是受上下文窗口限制、检索质量影响大。

Second-Me 的 L2 层将记忆内化为模型权重（LoRA 微调），优点是不需要在推理时检索（节省 token）、响应更自然；缺点是训练成本高、更新不实时、可能产生幻觉。

### 2. 统一存储 vs 分区存储

简单方案用一个向量集合存储所有记忆；Zleap 的人/事/经验分区和 Second-Me 的 L0/L1/L2 分层提供了更精细的控制，但增加了实现复杂度和检索融合的难度。

### 3. 记忆遗忘机制

三个框架对"遗忘"的处理不同：veadk 有 `forget()` 方法；Zleap 通过时间衰减降低旧记忆权重；Second-Me 的 L2 层通过增量更新覆盖旧模式。有效的遗忘机制和记忆机制同样重要。

## 相关概念

- [Agent 核心循环](01-agent-loop.md) — 记忆如何在循环中被检索和更新
- [上下文管理](06-context-management.md) — 记忆与上下文窗口的交互
- [技能与 Persona 系统](07-skill-persona.md) — 记忆如何塑造 Agent 的 Persona
- [Second-Me 分层记忆模型解析](/examples/second-me-memory-model.md) — L0→L1→L2 的代码级分析
