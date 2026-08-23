# Facts: Hello-Agents 知识束事实记录

> sources: https://github.com/datawhalechina/hello-agents

## 项目基本信息

- **项目名称**: Hello-Agents（《从零开始构建智能体》）
- **发起方**: Datawhale 社区
- **项目负责人**: 陈思州（jjyaoao）
- **定位**: 系统性智能体学习教程，聚焦 AI Native Agent（而非流程驱动的软件工程类 Agent）
- **在线阅读**: https://datawhalechina.github.io/hello-agents/
- **配套框架**: HelloAgents（https://github.com/jjyaoao/helloagents）
- **许可证**: CC BY-NC-SA 4.0
- **Python 要求**: >= 3.10

## 完整章节结构（16章 + 社区精选）

### 前言
- 项目缘起：2025年"Agent元年"，系统性、重实践教程匮乏
- 目标读者：AI开发者、软件工程师、在校学生、自学者
- 前置要求：基础Python编程能力、LLM基本概念

---

### 第一部分：智能体与语言模型基础（第1-3章）

#### 第一章 初识智能体
- **文件**: `docs/chapter1/第一章 初识智能体.md`
- **核心内容**:
  - 智能体定义：通过传感器感知环境、自主通过执行器采取行动以达成目标的实体
  - 传统智能体演进：反射智能体 → 基于模型的反射智能体 → 基于目标的智能体 → 基于效用的智能体 → 学习型智能体
  - LLM驱动新范式：核心引擎、知识来源、交互方式的本质区别
  - 智能体分类三维度：
    - 内部决策架构（反应式/模型式/基于目标/基于效用/学习型）
    - 时间与反应性（反应式/规划式/混合式）
    - 知识表示（亚符号主义/符号主义/神经符号主义）
  - PEAS任务环境模型（性能度量、环境、执行器、传感器）
  - 智能体构成要素：感知、推理、行动、记忆

#### 第二章 智能体发展史
- **文件**: `docs/chapter2/第二章 智能体发展史.md`
- **核心内容**:
  - 符号主义时代：物理符号系统假说（PSSH）、专家系统（MYCIN）、SHRDLU
  - 反应式范式：包容架构（Subsumption Architecture）
  - 多智能体与分布式AI：合同网协议、分布式问题求解
  - 强化学习智能体：马尔可夫决策过程、Q-Learning、AlphaGo
  - LLM驱动的现代智能体：从工具调用到自主规划
  - "问题驱动"的迭代演进脉络

#### 第三章 大语言模型基础
- **文件**: `docs/chapter3/第三章 大语言模型基础.md`
- **核心内容**:
  - 语言模型演进：N-gram → RNN → Transformer
  - Transformer架构：自注意力机制、位置编码
  - 提示工程：Zero-shot、Few-shot、Chain-of-Thought
  - 主流LLM概览：GPT系列、Claude、Qwen等
  - LLM能力与局限：幻觉问题、上下文窗口限制
  - Token化与采样策略

---

### 第二部分：构建你的大语言模型智能体（第4-7章）

#### 第四章 智能体经典范式构建
- **文件**: `docs/chapter4/第四章 智能体经典范式构建.md`
- **核心内容**:
  - 环境准备：HelloAgentsLLM客户端封装（OpenAI兼容接口）
  - **ReAct范式**（Reasoning + Acting）：
    - Thought → Action → Observation 循环
    - 推理与行动协同，动态调整
    - 提示工程引导固定轨迹
  - **Plan-and-Solve范式**：
    - 三思而后行：先生成完整计划再执行
    - 计划分解与步骤执行
  - **Reflection范式**：
    - 自我批判与修正
    - 反思-评估-改进循环
  - 从零实现的价值：理解框架背后的设计机制

#### 第五章 基于低代码平台的智能体搭建
- **文件**: `docs/chapter5/第五章 基于低代码平台的智能体搭建.md`
- **核心内容**:
  - 平台化构建兴起：降低门槛、提升效率、可视化、标准化
  - **Coze（扣子）**：字节跳动出品，零代码/低代码，丰富插件库，一键多平台发布
  - **Dify**：开源LLM应用开发平台，Agent工作流+RAG Pipeline+微调，企业级
  - **FastGPT**：开源知识库问答平台，RAG极致优化，可视化工作流编排
  - **n8n**：开源工作流自动化工具，数百预置节点，AI能力集成
  - 各平台定位对比与适用人群

#### 第六章 框架开发实践
- **文件**: `docs/chapter6/第六章 框架开发实践.md`
- **核心内容**:
  - 框架价值：代码复用、组件解耦、状态管理、可观测性
  - **AutoGen**（微软）：对话驱动协作，AssistantAgent + UserProxyAgent，RoundRobinGroupChat，异步优先分层架构
  - **AgentScope**（阿里巴巴）：多智能体开发平台，易用性+工程化，消息传递机制，分布式部署
  - **CAMEL**：角色扮演协作，初始提示（Inception Prompting），双Agent自主对话
  - **LangGraph**（LangChain生态）：图结构建模，节点+边，原生支持循环，Reflection工作流
  - 四框架设计理念对比

#### 第七章 构建你的Agent框架
- **文件**: `docs/chapter7/第七章 构建你的Agent框架.md`
- **核心内容**:
  - 自建框架动机：过度抽象、快速迭代不稳定、黑盒化、依赖复杂
  - **HelloAgents设计理念**：
    - 轻量级与教学友好平衡
    - 基于标准OpenAI API的务实选择
    - 渐进式学习路径（版本迭代）
    - 统一"工具"抽象：万物皆为Tools
  - 框架架构：
    - core层：Agent基类、LLM接口、消息系统、配置、异常
    - agents层：SimpleAgent、ReActAgent、ReflectionAgent、PlanAndSolveAgent
    - tools层：工具基类、注册机制、工具链、异步执行器、内置工具
  - 分层解耦、职责单一、接口统一原则

---

### 第三部分：高级知识扩展（第8-12章）

#### 第八章 记忆与检索
- **文件**: `docs/chapter8/第八章 记忆与检索.md`
- **核心内容**:
  - 认知科学启发：感觉记忆→工作记忆→长期记忆（程序性/陈述性：语义+情景）
  - LLM两大局限：无状态导致对话遗忘、内置知识静态有限
  - **记忆系统四层架构**：
    - 基础设施层：MemoryManager、MemoryItem、MemoryConfig、BaseMemory
    - 记忆类型层：WorkingMemory（TTL）、EpisodicMemory（事件序列）、SemanticMemory（知识图谱）、PerceptualMemory（多模态）
    - 存储后端层：Qdrant向量存储、Neo4j图存储、SQLite文档存储
    - 嵌入服务层：DashScope/Local/TFIDF嵌入
  - **RAG系统**：文档处理→嵌入表示→向量存储→智能问答（多策略检索：向量+MQE+HyDE）
  - memory_tool与rag_tool工具化设计

#### 第九章 上下文工程
- **文件**: `docs/chapter9/第九章 上下文工程.md`
- **核心内容**:
  - 上下文工程 vs 提示工程：从"写好提示词"到"策划维护最优信息集合"
  - **上下文腐蚀（Context Rot）**：token增加导致回忆能力下降，边际收益递减
  - Transformer注意力预算：n²级关系，长序列注意力被"拉薄"
  - 有效上下文"解剖学"：
    - 系统提示：最小必要信息集，分区组织
    - 工具：职责单一、token友好、最小可行工具集（MVTS）
    - 示例：多样且典型，好示例胜过千言万语
  - **JIT上下文检索**：轻量化引用→运行时动态加载→渐进式披露
  - 长时程任务三手段：
    - 压缩整合（Compaction）：高保真摘要重启上下文
    - 结构化笔记（Structured note-taking）：上下文外持久化
    - 子代理架构（Sub-agent architectures）：主代理规划+子代理深挖
  - **ContextBuilder**：GSSC流水线（Gather-Select-Structure-Compress）
  - NoteTool、TerminalTool配套工具

#### 第十章 智能体通信协议
- **文件**: `docs/chapter10/第十章 智能体通信协议.md`
- **核心内容**:
  - 通信协议价值：标准化接口、互操作性、动态发现、可扩展性
  - **MCP（Model Context Protocol）**：
    - Anthropic提出，智能体与工具/资源的标准化通信
    - "上下文共享"哲学，不仅是RPC
    - 统一访问文件系统、数据库、API等外部服务
  - **A2A（Agent-to-Agent Protocol）**：
    - Google提出，智能体间点对点通信
    - "对等通信"哲学，每个Agent既是提供者也是消费者
    - 支持对话、协商、协作
  - **ANP（Agent Network Protocol）**：
    - 开源社区维护，大规模智能体网络基础设施
    - "去中心化服务发现"哲学
    - 服务注册、发现、路由机制
  - 三协议对比与选型指南
  - HelloAgents三层架构：协议实现层→工具封装层→智能体集成层

#### 第十一章 Agentic-RL
- **文件**: `docs/chapter11/第十一章 Agentic-RL.md`
- **核心内容**:
  - LLM训练全景：预训练（因果语言建模）→后训练（SFT→RM→RLHF/RLAIF）
  - **Agentic RL核心理念**：
    - LLM作为可学习策略嵌入序贯决策循环
    - 多步交互、状态演化、中间反馈、累积奖励
    - PBRFT（单轮对话质量优化）vs Agentic RL（多步任务完成优化）
  - MDP形式化对比：状态空间、行动空间、转移函数、奖励函数、目标函数
  - 六大核心能力：推理、工具使用、记忆、规划、自我改进、感知
  - **SFT（监督微调）**：指令遵循、对话格式
  - **GRPO（群组相对策略优化）**：
    - 无需critic网络，群组内相对优势估计
    - 降低训练成本和显存占用
  - 完整训练pipeline：数据加载→奖励函数→LoRA配置→SFT训练→GRPO训练→评估
  - 分布式训练：DeepSpeed ZeRO2/ZeRO3、多GPU DDP

#### 第十二章 智能体性能评估
- **文件**: `docs/chapter12/第十二章 智能体性能评估.md`
- **核心内容**:
  - 评估挑战：输出不确定性、标准多样性、API成本高昂
  - **工具调用评估基准**：
    - BFCL（Berkeley Function Calling Leaderboard）：1120+样本，AST匹配
    - ToolBench：16000+真实API场景
    - API-Bank：53个常用API
  - **通用能力评估基准**：
    - GAIA（Meta+HuggingFace）：466个真实世界问题，3级难度，准精确匹配
    - AgentBench（清华）：8个领域任务
    - WebArena（CMU）：真实网页环境
  - **多智能体协作评估**：ChatEval、SOTOPIA
  - 评估指标：准确性（Accuracy/EM/F1）、效率（响应时间/Token用量）、鲁棒性（错误率/故障恢复）、协作（通信效率/任务完成度）
  - LLM Judge、Win Rate、人工验证
  - 数据生成质量评估完整流程

---

### 第四部分：综合案例进阶（第13-15章）

#### 第十三章 智能旅行助手
- **文件**: `docs/chapter13/第十三章 智能旅行助手.md`
- **核心内容**:
  - 智能行程规划、地图可视化、预算计算、行程编辑、PDF导出
  - 前后端分离架构：Vue3+TypeScript前端 / FastAPI后端 / HelloAgents智能体层 / 外部服务层
  - 4个专门Agent：景点搜索、天气查询、酒店推荐、行程规划
  - MCP协议调用外部API（高德地图、Unsplash、LLM API）

#### 第十四章 自动化深度研究智能体
- **文件**: `docs/chapter14/第十四章 自动化深度研究智能体.md`
- **核心内容**:
  - 问题剖析→多轮信息采集→反思与总结
  - 三Agent架构：TODO Planner、Task Summarizer、Report Writer
  - 两核心工具：SearchTool、NoteTool
  - SSE流式推送进度与结果
  - 信息去重整合、知识空白识别、结构化报告生成

#### 第十五章 构建赛博小镇
- **文件**: `docs/chapter15/第十五章 构建赛博小镇.md`
- **核心内容**:
  - AI NPC：自然语言对话、记忆系统、好感度系统
  - Godot 4.5游戏引擎 + FastAPI后端 + HelloAgents智能体层
  - 2D像素风格办公室场景，玩家自由移动与NPC互动
  - 短期记忆+长期记忆，Qdrant向量存储+SQLite持久化
  - Agent与游戏结合，模拟社会动态

---

### 第五部分：毕业设计及未来展望（第16章）

#### 第十六章 毕业设计
- **文件**: `docs/chapter16/第十六章 毕业设计.md`
- **核心内容**:
  - 开源项目形式提交至Co-creation-projects目录
  - 命名规范：`{GitHub用户名}-{项目名称}`
  - 提交内容：可运行代码、requirements.txt、README.md
  - 选题方向：生产力工具、学习辅助、创意娱乐、数据分析、生活服务
  - Git/GitHub协作流程、PR评审机制

---

### 社区贡献精选（Extra-Chapter，13篇）

| 编号 | 标题 | 文件 | 内容 |
|------|------|------|------|
| 00 | 共创毕业设计 | `Co-creation-projects/` | 社区共创毕业设计项目集合（40+项目） |
| 01a | Agent面试题总结 | `Extra-Chapter/Extra01-面试问题总结.md` | Agent岗位相关面试问题 |
| 01b | Agent面试题答案 | `Extra-Chapter/Extra01-参考答案.md` | 相关面试问题参考答案 |
| 02 | 上下文工程补充知识 | `Extra-Chapter/Extra02-上下文工程补充知识.md` | 上下文工程内容扩展 |
| 03 | Dify智能体创建保姆级教程 | `Extra-Chapter/Extra03-Dify智能体创建保姆级操作流程.md` | Dify操作全流程 |
| 04 | Hello-agents课程常见问题 | `Extra-Chapter/Extra04-DatawhaleFAQ.md` | Datawhale课程FAQ |
| 05 | Agent Skills解读 | `Extra-Chapter/Extra05-AgentSkills解读.md` | Agent Skills与MCP技术对比 |
| 06 | GUI Agent科普与实战 | `Extra-Chapter/Extra06-GUIAgent科普与实战.md` | GUI Agent科普与多场景实战 |
| 07 | 环境配置 | `Extra-Chapter/Extra07-环境配置.md` | 开发环境配置指南 |
| 08 | 如何写出好的Skill | `Extra-Chapter/Extra08-如何写出好的Skill.md` | Skill写作最佳实践 |
| 09 | Agent应用开发踩坑经验 | `Extra-Chapter/Extra09-Agent应用开发实践踩坑与经验分享.md` | Code Agent开发踩坑总结 |
| 10 | Agent自进化 | `Extra-Chapter/Extra10-Agent自进化.md` | Agent Self-Evolution四类闭环与代表项目 |
| 11 | WebAgent科普与实战 | `Extra-Chapter/Extra11-WebAgent科普与实战.md` | Web Agent原理、反爬实战、HelloAgents集成 |
| 12 | 旅行助手后训练实战 | `Extra-Chapter/Extra12-旅行助手后训练实战.md` | 旅行助手Demo打磨为可用Planner |
| 13 | 视频课录制共创 | `Extra-Chapter/Extra13-Hello-Agents视频课录制共创.md` | 视频课程共创录制资源 |

## 代码资源结构

```
hello-agents/
├── code/
│   ├── chapter10/          # MCP/A2A/ANP协议代码（14个示例）
│   ├── chapter11/          # Agentic-RL训练代码（8个脚本+加速配置）
│   └── chapter12/          # 评估代码（BFCL/GAIA/数据生成，8个脚本）
├── Co-creation-projects/   # 40+社区共创毕业设计项目
├── Extra-Chapter/          # 13篇社区精选文章
└── docs/                   # 16章教程文档
```

## 关键技术标签

- Agent范式: ReAct, Plan-and-Solve, Reflection
- 低代码平台: Coze, Dify, FastGPT, n8n
- 开发框架: AutoGen, AgentScope, CAMEL, LangGraph, HelloAgents
- 记忆系统: Working/Episodic/Semantic/Perceptual Memory, RAG
- 上下文工程: ContextBuilder, GSSC, Compaction, JIT检索
- 通信协议: MCP, A2A, ANP
- 训练技术: SFT, GRPO, RLHF, RLAIF, LoRA, DeepSpeed
- 评估基准: BFCL, GAIA, AgentBench, WebArena, ToolBench
- 综合案例: 智能旅行助手, 深度研究Agent, 赛博小镇
