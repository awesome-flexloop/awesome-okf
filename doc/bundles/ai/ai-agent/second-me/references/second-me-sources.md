---
type: Reference
title: Second-Me 源码信源登记
description: Second-Me 本地 AI 自我项目源码路径、技术栈、三层记忆架构（HMM）、核心目录、关键文件清单与 API 路由索引
tags: [second-me, source, reference, ai-agent, hmm, lora, personal-ai]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T10:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T10:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: secondme-github
    resource: https://github.com/mindverse/Second-Me
    title: Second-Me GitHub 仓库
  - id: secondme-arxiv
    resource: https://arxiv.org/abs/2503.08102
    title: AI-native Memory 2.0 (arXiv)
  - id: secondme-homepage
    resource: https://home.second.me/
    title: Second Me 官方主页
---

# Second-Me 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | Second Me |
| 版本 | **0.1.0**（前端 package.json 标注） |
| 描述 | 开源本地 AI 自我（AI Self）原型——基于分层记忆建模（HMM）与 Me-Alignment 算法，在本地训练和托管个人 AI 分身，并支持跨 Second Me 网络互联协作 |
| 维护者 | Mindverse（mindverse） |
| 许可证 | 详见 LICENSE 文件 |
| 官方主页 | <https://home.second.me/> |
| 源码仓库 | <https://github.com/mindverse/Second-Me> |
| 论文 | AI-native Memory ([arXiv:2406.18312](https://arxiv.org/abs/2406.18312))、AI-native Memory 2.0 ([arXiv:2503.08102](https://arxiv.org/abs/2503.08102)) |

## 源码位置

Second-Me 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/models/ai/mindverse/Second-Me/
```

源码根目录绝对路径：

```
d:\spaces\SpecWeave\external\libs\models\ai\mindverse\Second-Me\
```

## 技术栈概览

Second-Me 采用 **Python 后端 + Next.js 前端** 的双模块架构：

| 层 | 技术 | 说明 |
|----|------|------|
| **后端框架** | Flask | REST API 服务，监听端口 8000（Docker 映射为 8002） |
| **前端框架** | Next.js 14 + React 18 + TypeScript | 基于 App Router，端口 3000 |
| **UI 组件库** | Ant Design 5 + Tailwind CSS | 管理面板与交互界面 |
| **状态管理** | Zustand | 前端全局状态（5 个 store） |
| **数据库** | SQLAlchemy ORM + SQLite | 文档、记忆、L1 数据、Space、Load 持久化 |
| **向量存储** | ChromaDB | 文档 Embedding 与语义检索 |
| **LLM 训练** | HuggingFace Transformers + TRL (SFT/DPO) + PEFT (LoRA) | LoRA 微调与 DPO 偏好对齐 |
| **推理引擎** | llama.cpp (llama-server) | 本地 GGUF 模型推理服务 |
| **模型转换** | GGUF (gguf-py) + MLX (Apple Silicon) | 模型格式转换与 Apple 芯片训练加速 |
| **部署** | Docker Compose | CPU/GPU 双版本编排文件 |

## 核心架构：三层记忆 HMM

Second-Me 的核心创新是**分层记忆建模（Hierarchical Memory Modeling, HMM）**，分为 L0→L1→L2 三层递进流水线：

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户原始资料 (Raw Content)                   │
│              txt / pdf / md / 图片 / 音频 等文件                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  L0 — 原始记忆处理 (Raw Memory Processing)                       │
│  • 文件解析 → 分块(TokenTextSplitter) → LLM洞察(insighter)       │
│  • 生成每个文档的 title / insight / summary / keywords           │
│  • 输出: Document (含insight/summary/keywords, 存入DB+Chroma)    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  L1 — 身份洞察与传记生成 (Identity Insight & Biography)          │
│  • 文档→Note(含embedding) → Chunk分块 → Topic聚类                │
│  • Chunk→Cluster(距离剪枝 DISTANCE_RATE=0.8) → Shade(人格侧面)   │
│  • ShadeGenerator / ShadeMerger / StatusBioGenerator / TopicsGen │
│  • 输出: Bio(双视角传记) + Shades(人格侧面列表) + Clusters       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  L2 — 模型对齐与训练 (Model Alignment & Training)                │
│  • 数据合成: Preference QA + Diversity + Self-QA + GraphRAG      │
│  • SFT 训练: LoRA微调 (q/k/v/o_proj + gate/up/down_proj)         │
│  • DPO训练: Direct Preference Optimization                       │
│  • 权重合并: merge_lora_weights() → PeftModel.merge_and_unload() │
│  • 格式转换: HF → GGUF (f16量化) → llama-server推理              │
│  • 输出: 个人模型 personal_model → merged_model → GGUF model     │
└─────────────────────────────────────────────────────────────────┘
```

## 核心目录结构

| 目录 | 用途 | 关键文件 |
|------|------|---------|
| `lpm_kernel/` | **Python 后端核心** | `app.py`（Flask 入口）、`configs/`、`common/` |
| `lpm_kernel/L0/` | L0 原始记忆处理层 | `l0_generator.py`（L0Generator）、`models.py`（数据模型）、`prompt.py` |
| `lpm_kernel/L1/` | L1 身份洞察层 | `bio.py`（Chunk/Note/Cluster/Shade/Bio/UserInfo）、`l1_generator.py`、`shade_generator.py`、`status_bio_generator.py`、`topics_generator.py` |
| `lpm_kernel/L2/` | L2 训练与模型对齐层 | `l2_generator.py`、`data.py`（L2DataProcessor）、`train.py`（SFT训练）、`merge_lora_weights.py`、`dpo/dpo_train.py`、`gguf-py/`、`mlx_training/` |
| `lpm_kernel/L2/data_pipeline/` | L2 数据合成流水线 | `data_prep/preference/`（偏好QA）、`data_prep/diversity/`（多样性数据）、`data_prep/selfqa/`（自我QA）、`data_prep/context_data/`（上下文数据）、`graphrag_indexing/` |
| `lpm_kernel/api/` | **REST API 服务层** | `__init__.py`（路由注册）、`common/`（通用响应/错误/脚本执行） |
| `lpm_kernel/api/domains/` | API 领域模块 | `health/`、`documents/`、`kernel/`（L1存储）、`kernel2/`（聊天/角色/LLM管理）、`space/`、`trainprocess/`、`memories/`、`loads/`、`upload/`、`user_llm_config/` |
| `lpm_kernel/file_data/` | 文件处理子系统 | `document_service.py`、`chunker.py`、`embedding_service.py`、`models.py`（DocumentModel/ChunkModel）、`processors/`（pdf/markdown/text/image） |
| `lpm_kernel/kernel/` | 内核编排层 | `l0_base.py`、`note_service.py`、`chunk_service.py`、`l1/l1_manager.py` |
| `lpm_kernel/models/` | SQLAlchemy ORM 模型 | `l1.py`（L1版本/Bio/Shade/Cluster）、`space.py`、`memory.py`、`load.py`、`status_biography.py` |
| `lpm_kernel/common/` | 公共基础设施 | `repository/`（数据库会话/向量存储/基类仓库）、`llm.py`、`logging.py`、`strategy/`（分类策略） |
| `lpm_kernel/configs/` | 配置管理 | `config.py`（Config单例，dotenv加载）、`logging.py` |
| `lpm_kernel/database/` | 数据库迁移 | `migration_manager.py`、`migrations/` |
| `lpm_frontend/` | **Next.js 前端** | `src/app/`（页面路由）、`src/components/`、`src/service/`（API调用）、`src/store/`（Zustand状态） |
| `docker/` | Docker 初始化脚本 | `app/init_chroma.py`、`app/check_gpu_support.sh`、`sqlite/init.sql` |
| `dependencies/` | 离线依赖包 | `graphrag-*.tar.gz`、`llama.cpp.zip` |

## 关键文件清单

### 应用入口与配置

| 文件 | 内容 |
|------|------|
| lpm_kernel/app.py | Flask 应用工厂 `create_app()`，初始化数据库、CORS、文件服务，注册所有 Blueprint，监听 0.0.0.0:8000 |
| lpm_kernel/configs/config.py | `Config` 单例类（`__new__` 实现），从 `.env` 加载配置，含 `DatabaseConfig` 子配置，管理 ChromaDB/服务URL等 |
| docker-compose.yml | CPU 版 Docker 编排，后端端口 8002，前端端口 3000 |
| docker-compose-gpu.yml | GPU 版 Docker 编排，支持 CUDA 加速 |

### L0 层 — 原始记忆处理

| 文件 | 内容 |
|------|------|
| lpm_kernel/L0/models.py | 5 个 dataclass：`FileInfo`、`DocumentType`（枚举）、`BioInfo`、`InsighterInput`（含 `from_dict` 工厂）、`SummarizerInput`（含 `from_dict` 工厂） |
| lpm_kernel/L0/l0_generator.py | `L0Generator` 类：`insighter()` 按 DataType 分派到 `_insighter_image/audio/doc` 三方法；`summarizer()` 支持串行细粒度摘要和采样全文摘要两种策略；使用 tiktoken cl100k_base 编码 |
| lpm_kernel/L0/prompt.py | L0 层 prompt 模板集合（image/audio/document 的 parser/overview/breakdown 模板） |

### L1 层 — 身份洞察

| 文件 | 内容 |
|------|------|
| lpm_kernel/L1/bio.py | 核心数据结构：`Chunk`、`Note`（含多种to_str方法）、`Cluster`（均值中心+DISTANCE_RATE=0.8剪枝）、`ShadeInfo`（双视角+ShadeTimeline）、`Bio`（双视角传记+属性/侧面列表）、`UserInfo`（时间窗口划分记忆） |
| lpm_kernel/L1/l1_generator.py | `L1Generator` 类，组合 `ShadeGenerator`/`ShadeMerger`/`StatusBioGenerator`/`TopicsGenerator` 四子生成器 |
| lpm_kernel/L1/shade_generator.py | Shade（人格侧面）生成器 |
| lpm_kernel/L1/status_bio_generator.py | 状态传记生成器（短期身份描述） |
| lpm_kernel/L1/topics_generator.py | 主题提取生成器 |

### L2 层 — 模型训练与对齐

| 文件 | 内容 |
|------|------|
| lpm_kernel/L2/l2_generator.py | `L2Generator` 类，编排 data_preprocess 和 gen_subjective_data（偏好/多样性/自我QA/图索引四类数据） |
| lpm_kernel/L2/data.py | `L2DataProcessor` 类，`__call__` 方法按类型分 subjective/objective notes，导入四类数据生成器 |
| lpm_kernel/L2/train.py | SFT 训练主文件，使用 SFTTrainer+LoraConfig(r=64,alpha=16,dropout=0.1)，自定义 LogTqdm 和 DebugCallback |
| lpm_kernel/L2/merge_lora_weights.py | `merge_lora_weights()` 函数：PeftModel.from_pretrained + merge_and_unload()，自动检测 CUDA |
| lpm_kernel/L2/dpo/dpo_train.py | DPO 训练：DPOTrainer+DPOConfig，数据格式 prompt/chosen/rejected，支持 LoRA |
| lpm_kernel/L2/convert_hf_to_gguf.py | HuggingFace 模型转 GGUF 格式（f16量化） |
| lpm_kernel/L2/memory_manager.py | GPU 内存管理工具，训练后清理显存 |

### API 服务层

| 文件 | 内容 |
|------|------|
| lpm_kernel/api/__init__.py | `init_routes(app)` 注册全部 13 个 Flask Blueprint |
| lpm_kernel/api/domains/trainprocess/trainprocess_service.py | `TrainProcessService` 单例，编排 14 步训练流水线，支持断点续训、进度监控、资源清理 |
| lpm_kernel/api/domains/trainprocess/process_step.py | `ProcessStep` 枚举，定义 14 个训练步骤及有序排列 |
| lpm_kernel/api/domains/kernel2/services/chat_service.py | 聊天服务，调用本地 llama-server，支持流式/非流式响应 |
| lpm_kernel/api/domains/kernel2/services/prompt_builder.py | Prompt 构建责任链：BasePromptStrategy→ContextEnhancedStrategy→RoleBasedStrategy→KnowledgeEnhancedStrategy |
| lpm_kernel/api/domains/space/space_service.py | Space 领域服务层，组合 SpaceRepository+DiscussionService |
| lpm_kernel/api/domains/space/services/discussion_service.py | `DiscussionService`：固定3轮讨论，host opening→participant轮次→host summary |
| lpm_kernel/api/services/local_llm_service.py | 本地 llama-server 进程管理（启动/停止/状态检测/流式响应转发） |
| lpm_kernel/file_data/document_service.py | 文档 CRUD、L0 分析、embedding 处理编排 |

### 前端关键文件

| 文件 | 内容 |
|------|------|
| lpm_frontend/src/service/train.ts | 训练 API 封装，定义 5 个训练阶段类型（StageName） |
| lpm_frontend/src/service/memory.ts | 记忆文件 API，定义 `MemoryFile` 接口（含四状态枚举） |
| lpm_frontend/src/service/space.ts | Space API 封装，定义 SpaceInfo/SpaceMessage 接口 |
| lpm_frontend/src/hooks/useSSE.tsx | Server-Sent Events 自定义 Hook |

## 核心类与数据模型索引

### L0 层数据模型（dataclass）

| 类名 | 定义位置 | 核心字段 | 说明 |
|------|---------|---------|------|
| `FileInfo` | L0/models.py:L6-L13 | data_type, filename, content, file_content | 文件信息封装 |
| `DocumentType` | L0/models.py:L16-L37 | DOCUMENT, TEXT | 文档类型枚举，含 `from_mime_type()` |
| `BioInfo` | L0/models.py:L40-L46 | global_bio, status_bio, about_me | 用户传记信息 |
| `InsighterInput` | L0/models.py:L49-L78 | file_info, bio_info | 洞察输入（含 `from_dict`） |
| `SummarizerInput` | L0/models.py:L81-L106 | file_info, insight | 摘要输入（含 `from_dict`） |
| `L0Generator` | L0/l0_generator.py:L32-L857 | preferred_language, client, tokenizer | L0 主生成器，insighter+summarizer |

### L1 层数据模型

| 类名 | 定义位置 | 核心字段 | 说明 |
|------|---------|---------|------|
| `Chunk` | L1/bio.py:L72-L130 | id, document_id, content, embedding, tags, topic | 文档分块（embedding为numpy数组） |
| `Note` | L1/bio.py:L133-L274 | id, content, embedding, chunks, title, summary, insight, tags, topic, memory_type | 记忆笔记，含多种to_str方法 |
| `Cluster` | L1/bio.py:L289-L349 | cluster_id, memory_list, cluster_center, size, merge_list | 记忆簇，均值中心+离群剪枝 |
| `ShadeInfo` | L1/bio.py:L351-L496 | id, name, aspect, icon, desc/content(third/second_view), timelines, confidence_level | 人格侧面（双视角+时间线） |
| `ShadeTimeline` | L1/bio.py | refMemoryId, createTime, descSecondView/ThirdView | Shade内嵌时间线条目 |
| `Bio` | L1/bio.py:L531-L597 | content/summary(third/second_view), attribute_list, shades_list | L1核心输出：用户传记 |
| `UserInfo` | L1/bio.py:L680-L786 | notes, todos, chats, memories(recent/earlier) | 用户信息聚合，时间窗口划分 |
| `L1Generator` | L1/l1_generator.py | shade_generator, shade_merger, status_bio_generator, topics_generator | L1主生成器 |

### L2 层核心类

| 类名 | 定义位置 | 核心方法 | 说明 |
|------|---------|---------|------|
| `L2Generator` | L2/l2_generator.py:L21-L80 | data_preprocess(), gen_subjective_data(), gen_preference_data(), gen_selfqa_data(), gen_diversity_data() | L2数据生成编排器 |
| `L2DataProcessor` | L2/data.py:L39-L80 | `__call__()`, split_notes_by_type() | 笔记分类与数据预处理 |
| `ModelArguments` | L2/train.py | model_name_or_path, lora_alpha=16, lora_r=64, lora_dropout=0.1, lora_target_modules | LoRA训练参数dataclass |
| `TrainProcessService` | api/domains/trainprocess/trainprocess_service.py:L38-L1109 | 14个step方法, start_process(), _prepare_l2_data() | 训练流水线单例服务 |

### SQLAlchemy ORM 模型（数据库表）

| 模型类 | 表名 | 定义位置 | 核心字段 |
|--------|------|---------|---------|
| `DocumentModel` | `document` | file_data/models.py:L48-L73 | id, name, title, mime_type, raw_content, insight(JSON), summary(JSON), keywords(JSON), extract_status, embedding_status |
| `ChunkModel` | `chunk` | file_data/models.py:L23-L45 | id, document_id(FK), content, has_embedding, tags(JSON), topic |
| `L1Version` | `l1_versions` | models/l1.py:L10-L22 | version(PK), create_time, status, description |
| `L1Bio` | `l1_bios` | models/l1.py:L25-L37 | id, version(FK), content, content_third_view, summary, summary_third_view |
| `L1Shade` | `l1_shades` | models/l1.py:L40-L55 | id, version(FK), name, aspect, icon, desc/content(third/second_view) |
| `L1Cluster` | `l1_clusters` | models/l1.py:L58-L69 | id, version(FK), cluster_id, memory_ids(JSON), cluster_center(JSON) |
| `L1ChunkTopic` | `l1_chunk_topics` | models/l1.py:L72-L83 | id, version(FK), chunk_id, topic, tags(JSON) |
| `Space` | `spaces` | models/space.py:L9-L24 | id(UUID), title, objective, participants(JSON), host, status, conclusion |
| `SpaceMessage` | `space_messages` | models/space.py:L26-L40 | id, space_id(FK), sender_endpoint, content, message_type, round, role |
| `Memory` | `memories` | models/memory.py:L8-L51 | id(UUID), name, size, type, path, meta_data(JSON), document_id |
| `Load` | `loads` | models/load.py:L8-L69 | id(UUID), name, description, email, avatar_data, instance_id, instance_password, status |
| `StatusBiography` | `status_biography` | models/status_biography.py:L5-L18 | id, content, content_third_view, summary, summary_third_view |
| `UserLLMConfig` | `user_llm_configs` | api/models/user_llm_config.py | provider_type, chat/embedding endpoint+key+model, thinking model config |

### Pydantic DTO 模型

| 类名 | 定义位置 | 用途 |
|------|---------|------|
| `CreateSpaceDTO` | space_dto.py | Space 创建请求校验（含URL校验器） |
| `SpaceDTO` | space_dto.py | Space 响应（4状态常量：INITIALIZED/DISCUSSING/INTERRUPTED/FINISHED） |
| `SpaceMessageDTO` | space_dto.py | 消息响应（含from_db/to_dict） |
| `ChatRequest` | kernel2/dto/chat_dto.py | OpenAI兼容聊天请求（messages/stream/temperature/max_tokens等） |
| `CreateRoleRequest`/`UpdateRoleRequest`/`ShareRoleRequest` | kernel2/dto/role_dto.py | 角色CRUD请求 |
| `UpdateUserLLMConfigDTO` | api/dto/user_llm_config_dto.py | LLM配置更新请求 |

### 服务类（核心业务逻辑）

| 类名 | 定义位置 | 职责 |
|------|---------|------|
| `TrainProcessService` | trainprocess_service.py | **单例**，编排14步训练流水线，断点续训+进度监控 |
| `DiscussionService` | discussion_service.py | Space多AI讨论编排（固定3轮） |
| `SpaceService` | space_service.py | Space CRUD + 讨论启动 |
| `ChatService` | chat_service.py | 聊天请求处理，调用llama-server |
| `LocalLLMService` | local_llm_service.py | 本地llama-server进程生命周期管理 |
| `DocumentService` | document_service.py | 文档CRUD+L0分析+embedding |
| `LoadService` | load_service.py | 用户Load（身份）管理 |
| `UserLLMConfigService` | user_llm_config_service.py | LLM配置管理 |

## L0→L1→L2 训练流水线映射

训练流水线由 `ProcessStep` 枚举定义 14 个有序步骤，由 `TrainProcessService.start_process()` 顺序执行，支持断点续训（从上次成功步骤后继续）：

| 序号 | ProcessStep 枚举值 | 前端显示阶段 | 层级 | 核心方法 | 关键操作 |
|------|-------------------|-------------|------|---------|---------|
| 1 | `MODEL_DOWNLOAD` | `downloading_the_base_model` | — | `model_download()` | 从HuggingFace下载基础模型（save_hf_model），独立线程监控下载进度 |
| 2 | `LIST_DOCUMENTS` | — | L0准备 | `list_documents()` | 列出所有已上传文档 |
| 3 | `GENERATE_DOCUMENT_EMBEDDINGS` | `activating_the_memory_matrix` | L0 | `generate_document_embeddings()` | 对每个文档生成文档级embedding，存入ChromaDB |
| 4 | `CHUNK_DOCUMENT` | `activating_the_memory_matrix` | L0 | `process_chunks()` | 使用DocumentChunker（配置chunk_size/overlap）分块，保存到数据库 |
| 5 | `CHUNK_EMBEDDING` | `activating_the_memory_matrix` | L0 | `chunk_embedding()` | 对每个chunk生成embedding |
| 6 | `EXTRACT_DIMENSIONAL_TOPICS` | `synthesize_your_life_narrative` | **L0→L1** | `extract_dimensional_topics()` | 调用document_service.analyze_all_documents()，即L0Generator.insighter()+summarizer() |
| 7 | `GENERATE_BIOGRAPHY` | `synthesize_your_life_narrative` | **L1** | `generate_biography()` | generate_l1_from_l0() → L1Generator生成Bio/Shades/Clusters，存入数据库 |
| 8 | `MAP_ENTITY_NETWORK` | `prepare_training_data_for_deep_comprehension` | L2准备 | `map_your_entity_network()` | L2Generator.data_preprocess()：GraphRAG实体网络构建 |
| 9 | `DECODE_PREFERENCE_PATTERNS` | `prepare_training_data_for_deep_comprehension` | **L2** | `decode_preference_patterns()` | gen_preference_data()：偏好QA数据生成（PreferenceQAGenerator） |
| 10 | `REINFORCE_IDENTITY` | `prepare_training_data_for_deep_comprehension` | **L2** | `reinforce_identity()` | gen_selfqa_data()：自我QA数据生成（SelfQA） |
| 11 | `AUGMENT_CONTENT_RETENTION` | `prepare_training_data_for_deep_comprehension` | **L2** | `augment_content_retention()` | gen_diversity_data()：多样性数据生成（DiversityDataGenerator），合并JSON文件 |
| 12 | `TRAIN` | `training_to_create_second_me` | **L2训练** | `train()` | 执行train_for_user.sh脚本（调用train.py进行SFT+LoRA训练），实时解析tqdm日志更新进度 |
| 13 | `MERGE_WEIGHTS` | — | **L2训练** | `merge_weights()` | 执行merge_weights_for_user.sh（调用merge_lora_weights.py），LoRA适配器合并到基础模型 |
| 14 | `CONVERT_MODEL` | — | **L2部署** | `convert_model()` | 执行convert_hf_to_gguf.py，HF模型→GGUF f16格式，供llama-server推理 |

**关键参数**（通过TrainingParamsManager持久化）：
- `model_name`：基础模型名称
- `learning_rate`：学习率
- `number_of_epochs`：训练轮次
- `concurrency_threads`：数据合成并发线程数
- `data_synthesis_mode`：数据合成模式
- `use_cuda`：是否使用CUDA
- `is_cot`：是否启用Chain-of-Thought

**LoRA 默认配置**（L2/train.py）：
- `lora_r = 64`，`lora_alpha = 16`，`lora_dropout = 0.1`
- target_modules: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

## API 路由列表

所有路由通过 lpm_kernel/api/__init__.py 中的 `init_routes()` 注册，共 13 个 Blueprint。

### Health（健康检查）— `health_bp`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 服务健康检查 |
| GET | `/favicon.ico` | 网站图标 |

### Documents（文档管理）— `document_bp`，URL前缀 `/api`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/documents/list` | 获取文档列表（支持 include_l0 参数） |
| POST | `/api/documents/scan` | 从 USER_RAW_CONTENT_DIR 扫描文档 |
| POST | `/api/documents/analyze` | 分析所有未分析文档（触发L0） |
| GET | `/api/documents/<id>/l0` | 获取文档L0分析结果 |
| GET | `/api/documents/<id>/chunks` | 获取文档分块 |
| POST | `/api/documents/chunks/process` | 批量处理文档分块 |
| POST | `/api/documents/<id>/chunk/embedding` | 生成块级embedding |
| GET | `/api/documents/<id>/chunk/embedding` | 查询块级embedding状态 |
| POST | `/api/documents/<id>/embedding` | 生成文档级embedding |
| GET | `/api/documents/<id>/embedding` | 查询文档级embedding状态 |
| GET | `/api/documents/verify-embeddings` | 验证所有embedding状态 |
| POST | `/api/documents/repair` | 修复异常文档 |

### Kernel（L1数据管理）— `kernel_bp`，URL前缀 `/api/kernel`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/kernel/...` | L1版本/Bio/Shade/Cluster/ChunkTopic的存储与查询 |

### Kernel2（聊天与LLM管理）— `kernel2_bp`，URL前缀 `/api/kernel2`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/kernel2/health` | LLM服务健康状态（含pid/CPU/内存/运行时间） |
| GET | `/api/kernel2/username` | 获取当前用户名 |
| GET | `/api/kernel2/docker/env` | 获取是否在Docker环境中 |
| POST | `/api/kernel2/llama/start` | 启动llama-server（参数：model_name, use_gpu） |
| POST | `/api/kernel2/llama/stop` | 停止llama-server |
| GET | `/api/kernel2/llama/status` | 获取llama-server状态 |
| POST | `/api/kernel2/chat` | **OpenAI兼容聊天接口**（SSE流式/JSON非流式，支持L0/L1检索、角色、温度、token限制） |
| GET | `/api/kernel2/cuda/available` | 检查CUDA可用性 |

### Talk（聊天，旧版接口）— `talk_bp`，URL前缀 `/api/talk`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/talk/chat` | 流式聊天（SSE） |
| POST | `/api/talk/chat_json` | 非流式JSON聊天 |

### Role（角色管理）— `role_bp`，URL前缀 `/api/kernel2/roles`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/kernel2/roles` | 创建角色 |
| GET | `/api/kernel2/roles` | 获取所有角色 |
| GET | `/api/kernel2/roles/<uuid>` | 获取指定角色 |
| PUT | `/api/kernel2/roles/<uuid>` | 更新角色 |
| DELETE | `/api/kernel2/roles/<uuid>` | 删除角色 |
| POST | `/api/kernel2/roles/share` | 分享角色到远程注册中心 |

### Space（多AI协作空间）— `space_bp`，URL前缀 `/api/space`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/space/create` | 创建Space（自动启动讨论） |
| GET | `/api/space/all` | 获取所有Space（支持host参数过滤） |
| GET | `/api/space/<space_id>` | 获取Space详情 |
| DELETE | `/api/space/<space_id>` | 删除Space |
| POST | `/api/space/<space_id>/start` | 启动讨论（异步，固定3轮） |
| GET | `/api/space/<space_id>/status` | 获取讨论状态 |
| POST | `/api/space/<space_id>/share` | 分享Space到远程注册中心 |

### TrainProcess（训练流程）— `trainprocess_bp`，URL前缀 `/api/trainprocess`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/trainprocess/start` | 启动14步训练流水线（后台线程，参数：model_name/lr/epochs/cuda/cot等） |
| GET | `/api/trainprocess/logs` | SSE实时日志流 |
| GET | `/api/trainprocess/progress/<model_name>` | 获取训练进度 |
| POST | `/api/trainprocess/stop` | 停止训练（轮询等待suspended状态） |
| POST | `/api/trainprocess/retrain` | 重置进度并重新训练 |
| GET | `/api/trainprocess/training_params` | 获取训练参数 |

### Memories（记忆文件上传）— `memories_bp`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/memories/file` | 上传记忆文件（multipart/form-data，支持txt/pdf/md） |
| DELETE | `/api/memories/file/<filename>` | 删除记忆文件 |

### Loads（用户身份管理）— `loads_bp`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/loads` | 创建Load（身份） |
| GET | `/api/loads/current` | 获取当前Load（含注册/在线状态） |
| PUT | `/api/loads/current` | 更新当前Load |
| DELETE | `/api/loads/<load_name>` | 删除Load及相关数据（自动停止llama-server） |
| POST | `/api/loads/<load_name>/avatar` | 上传头像（base64） |
| GET | `/api/loads/<load_name>/avatar` | 获取头像 |

### Upload（注册中心交互）— `upload_bp`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload/register` | 注册到远程注册中心 |
| POST | `/api/upload/connect` | 建立WebSocket连接 |
| GET | `/api/upload/status` | 获取Upload实例连接状态 |
| DELETE | `/api/upload` | 注销Upload实例 |
| GET | `/api/upload` | 获取已注册Upload列表（分页+状态过滤） |
| GET | `/api/upload/count` | 获取已注册Upload数量 |
| PUT | `/api/upload` | 更新Upload实例信息 |

### User LLM Config（LLM配置）— `user_llm_config_bp`，URL前缀 `/api/user-llm-configs`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/user-llm-configs` | 获取LLM配置（支持OpenAI/Custom双模式） |
| PUT | `/api/user-llm-configs` | 更新LLM配置（含校验逻辑） |
| PUT | `/api/user-llm-configs/thinking` | 更新思考模型配置 |
| DELETE | `/api/user-llm-configs/key` | 删除API Key |

### 文件服务（静态资源）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/raw_content/<path:path>` | 提供原始内容文件访问（FileServerHandler） |

## 设计模式索引

| 模式 | 应用位置 | 说明 |
|------|---------|------|
| **单例模式** | `Config`、`TrainProcessService`、`LocalLLMService` | 通过 `__new__` 或 `get_instance()` 实现 |
| **策略模式** | Space讨论策略（`SpaceBaseStrategy`→`HostOpeningStrategy`/`HostSummaryStrategy`/`ParticipantStrategy`） | 抽象基类+模板方法+装饰器链 |
| **责任链/装饰器模式** | Prompt构建（`SystemPromptStrategy`→`BasePromptStrategy`→`RoleBasedStrategy`→`KnowledgeEnhancedStrategy`） | 链式包装，逐层增强system prompt |
| **工厂模式** | `SpaceContextManagerFactory`、`process_factory`（文件处理器） | 对象创建封装 |
| **仓库模式** | `SpaceRepository`、`BaseRepository`、`DocumentRepository` | 数据访问抽象 |
| **DTO模式** | Pydantic BaseModel（SpaceDTO/ChatRequest等） + dataclass（InsighterInput等） | 请求/响应数据校验与传输 |
| **模板方法模式** | `SpaceBaseStrategy.build_prompt()` | 定义算法骨架，子类实现具体步骤 |
| **脚本执行器模式** | `ScriptExecutor` | 统一管理外部shell脚本执行（训练/合并/转换） |

## 前端页面结构

```
lpm_frontend/src/app/
├── home/                          # 首页（着陆页）
│   └── page.tsx
├── dashboard/                     # 主控面板（需登录）
│   ├── page.tsx                   # Dashboard首页
│   ├── layout.tsx                 # Dashboard布局（含侧边栏）
│   ├── train/                     # 训练模块
│   │   ├── page.tsx
│   │   ├── identity/page.tsx      # 身份配置
│   │   ├── memories/page.tsx      # 记忆上传
│   │   └── training/page.tsx      # 训练监控
│   ├── playground/                # 交互模块
│   │   ├── page.tsx
│   │   ├── chat/page.tsx          # AI对话
│   │   └── bridge/page.tsx        # API桥接
│   └── applications/              # 应用模块
│       ├── page.tsx
│       ├── api-mcp/page.tsx       # API/MCP接口
│       ├── integrations/page.tsx  # 集成管理
│       ├── network-apps/page.tsx  # 网络应用
│       ├── roleplay-apps/page.tsx # 角色扮演应用
│       └── second-x/page.tsx      # Second X
└── standalone/                    # 独立页面（动态路由）
    ├── layout.tsx
    ├── role/[roleId]/page.tsx     # 角色详情页
    ├── room/[roomId]/page.tsx     # 房间详情页
    └── space/[spaceId]/page.tsx   # Space讨论页
```
