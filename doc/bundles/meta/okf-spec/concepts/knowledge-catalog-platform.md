---
type: Concept
title: Knowledge Catalog 平台概述与架构
description: Google Cloud Knowledge Catalog（原 Dataplex）AI 驱动数据目录与元数据管理平台——背景动机、三大设计哲学、核心概念体系、四层平台架构与知识生产-消费闭环定位。
tags: [okf, knowledge-catalog, google-cloud, dataplex, data-catalog, platform]
generated: { by: process:learning-bundles-merge, at: 2026-09-02T00:00:00Z }
status: draft
stale_after: 2027-09-02
sources:
  - id: src1
    resource: SpecWeave docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/（00-overview.md、01-core-concepts.md）
    title: Knowledge Catalog Wiki 教程（learning 侧合并来源）
---
> **⚠️ 技术预览版提示**
> - Knowledge Catalog（原Dataplex）目前处于技术预览阶段
> - OKF开放知识格式目前处于**v0.2 Draft极早期阶段**（2026年6月首次发布）
> - 本教程基于官方开源仓库与公开信息整理，是趋势分析而非确定性预测
> - 建议结合OKF开放知识格式完整指南学习，先小范围试点再考虑生产落地
> - 生态仍在快速演进中

# 00 Knowledge Catalog概述与知识地图

## 0.1 Knowledge Catalog是什么

Knowledge Catalog（原Google Cloud Dataplex）是Google Cloud推出的AI驱动数据目录与元数据管理平台。

**核心定位**：为所有结构化与非结构化数据构建动态知识图谱，为AI Agent提供语义层和业务上下文。

**本质**：一套完整的知识生产-消费-可视化解决方案，包含OKF开放知识格式规范、参考Agent实现、可视化工具链与示例数据集。

**一句话价值主张**：你的数据资产可被Git版本控制，你的AI Agent无需适配器即可解析，你的知识编审融入标准软件工程工作流，你的元数据再也不会被锁定在专有服务中。

> **📖 前置阅读**：OKF是Knowledge Catalog的核心知识表示格式，建议先阅读OKF概述与知识地图了解OKF基础。

## 0.2 背景与动机

### 数据目录的演进需求
传统数据目录（如Unity Catalog、Collibra）多为中心化、专有系统，元数据被锁定在服务内部，难以被AI Agent直接消费。

### 知识层缺失的痛点
当前Agent栈三层（模型/MCP/Skills）缺少独立的知识层，知识散落在提示词、Skills描述和向量库中，缺乏统一的表示格式与治理机制。

### 生产与消费的割裂
知识生产（数据治理团队）与知识消费（Agent开发者、业务分析师）使用不同的工具与格式，协作成本高，知识更新难以同步。

### 软件工程化的知识管理
代码已经通过Git实现了版本控制、评审、协作的完整工作流，知识管理也需要同样的软件工程化能力。

## 0.3 学习目标

完成本教程后，你将能够：

1. 理解Knowledge Catalog的核心定位与整体架构，能向团队清晰解释Knowledge Catalog是什么
2. 掌握OKF开放知识格式的核心设计，理解Bundle/Concept/Frontmatter等核心概念
3. 了解参考Agent的双阶段工作流（BQ Pass + Web Pass），能运行参考Agent生成OKF Bundle
4. 使用可视化工具浏览知识图谱，理解交互式知识浏览器的功能
5. 剖析GA4、Stack Overflow、比特币等示例Bundle，设计适合自身团队的知识组织方案
6. 将Knowledge Catalog集成到现有数据治理与Agent工作流中，实现知识的版本控制与团队评审

## 0.4 前置知识要求

- **基础Markdown/YAML知识**：能编写Markdown文档，理解YAML键值对结构
- **AI Agent基本了解**：知道Agent是什么，理解工具调用、RAG等基本概念
- **版本控制（Git）基础**：理解commit/branch/PR等基本概念，OKF基于Git管理
- **数据目录与元数据管理基本概念**：了解数据目录、元数据、数据治理等基本术语
- **Google Cloud基础（可选）**：了解BigQuery、Vertex AI等Google Cloud服务有助于理解参考实现

## 0.5 9章导航表

| 章号 | 标题 | 核心内容 | 适合人群 | 预计阅读时间 |
|------|------|----------|----------|--------------|
| 00 | Knowledge Catalog概述与知识地图 | 背景动机、学习目标、导航表、阅读路径、知识生产-消费闭环架构图、核心组件全景图 | 所有读者 | 4分钟 |
| 01 | 核心概念与平台架构 | 知识图谱、动态元数据、Bundle/Concept/Frontmatter核心概念、平台组件架构、与Dataplex的关系 | 开发者/数据工程师 | 8分钟 |
| 02 | OKF开放知识格式规范深度解析 | OKF v0.2规范详解、frontmatter字段定义、信任层级与来源溯源、渐进式披露机制、链接规则 | 开发者/知识工程师 | 10分钟 |
| 03 | 参考Agent实现原理与运行指南 | BQ Pass与Web Pass双阶段工作流、生产端配置、单概念迭代开发、凭证配置、运行命令详解 | 开发者/数据工程师 | 9分钟 |
| 04 | 工具链与可视化系统 | 交互式知识图谱浏览器、Cytoscape.js图渲染、Markdown实时渲染、搜索与过滤机制、viz.html生成 | 开发者/前端工程师 | 7分钟 |
| 05 | 示例Bundle深度解析 | GA4电商数据集、Stack Overflow公开数据集、比特币区块链、Acme Retail示例剖析 | 所有读者 | 8分钟 |
| 06 | 集成模式与最佳实践 | 企业落地四阶段路径、与现有数据目录集成、Git工作流集成、知识生产消费解耦模式 | 架构师/技术负责人 | 8分钟 |
| 07 | 架构决策与方案对比 | 与Unity Catalog/Collibra等方案对比、OKF局限性分析、选型决策树、风险评估 | 架构师/决策者 | 7分钟 |
| 08 | 资源与术语表 | 30+核心术语定义、官方资源链接、OKF交叉引用、项目内wiki导航 | 所有读者 | 5分钟 |

## 0.6 三条阅读路径

### 路径一：快速上手路径（初学者/开发者）
**目标**：快速了解Knowledge Catalog并运行第一个示例Bundle

**阅读顺序**：00 → 01 → 02 → 05 → 08
**预计总时间**：约35分钟

### 路径二：深度开发路径（开发者/知识工程师/数据工程师）
**目标**：完整掌握OKF规范、参考Agent开发、工具链使用与集成方法

**阅读顺序**：00 → 01 → 02 → 03 → 04 → 05 → 06 → 08
**预计总时间**：约59分钟

### 路径三：架构决策路径（架构师/技术决策者/数据治理专家）
**目标**：判断Knowledge Catalog与OKF是否适合团队，做出技术选型决策

**阅读顺序**：00 → 01 → 02 → 06 → 07 → 08
**预计总时间**：约42分钟

## 0.7 知识生产-消费闭环架构全景图

```mermaid
flowchart TB
    subgraph Producers["🏭 知识生产端 Production"]
        direction TB
        Sources["数据源<br/>（BigQuery/数据库/文档）"]
        BQPass["BQ Pass<br/>（元数据提取）"]
        WebPass["Web Pass<br/>（LLM爬虫增强）"]
        RefAgent["参考Agent<br/>（reference_agent）"]
    end
    
    subgraph KnowledgeLayer["📚 OKF知识层 Knowledge Layer"]
        direction TB
        Bundle["OKF Bundle<br/>（Git管理）"]
        Concepts["概念文档<br/>（concepts/）"]
        References["参考资料<br/>（references/）"]
        Index["索引文件<br/>（index.md）"]
        Log["演进日志<br/>（log.md）"]
    end
    
    subgraph Consumers["🎯 知识消费端 Consumption"]
        direction TB
        Viz["可视化工具<br/>（viz.html/Cytoscape.js）"]
        Agent["AI Agent<br/>（直接加载上下文）"]
        Human["人类用户<br/>（Obsidian/MkDocs/VS Code）"]
        Search["搜索索引<br/>（向量/关键词）"]
    end
    
    Producers --> KnowledgeLayer
    KnowledgeLayer --> Consumers
    
    Sources --> BQPass
    BQPass --> RefAgent
    WebPass --> RefAgent
    RefAgent --> Bundle
    
    Bundle --> Concepts
    Bundle --> References
    Bundle --> Index
    Bundle --> Log
    
    Bundle --> Viz
    Bundle --> Agent
    Bundle --> Human
    Bundle --> Search
    
    style Producers fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style KnowledgeLayer fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Consumers fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

## 0.8 Knowledge Catalog核心组件全景图

```mermaid
graph TD
    KC["Knowledge Catalog<br/>（原Dataplex）"] --> Format["📄 OKF开放知识格式<br/>（核心规范）"]
    KC --> Agent["🤖 参考Agent实现<br/>（reference_agent）"]
    KC --> Viz["📊 可视化工具链<br/>（visualize）"]
    KC --> Samples["📦 示例数据集<br/>（bundles/）"]
    
    Format --> Spec["SPEC.md<br/>（v0.2规范文档）"]
    Format --> Frontmatter["YAML Frontmatter<br/>（元数据字段）"]
    Format --> Markdown["Markdown Body<br/>（正文内容）"]
    Format --> Links["双向链接<br/>（知识图谱关系）"]
    
    Agent --> BQ["BQ Pass<br/>（BigQuery元数据提取）"]
    Agent --> Web["Web Pass<br/>（LLM文档爬取增强）"]
    Agent --> Enrich["enrich命令<br/>（生成OKF Bundle）"]
    Agent --> Single["--concept<br/>（单概念迭代）"]
    
    Viz --> Cyto["Cytoscape.js<br/>（力导向图）"]
    Viz --> Marked["marked.js<br/>（Markdown渲染）"]
    Viz --> SelfContained["自包含HTML<br/>（无后端依赖）"]
    Viz --> Search["搜索/过滤<br/>（类型筛选/关键词）"]
    
    Samples --> GA4["GA4电商数据集<br/>（bundles/ga4/）"]
    Samples --> SO["Stack Overflow<br/>（bundles/stackoverflow/）"]
    Samples --> BTC["比特币区块链<br/>（bundles/crypto_bitcoin/）"]
    Samples --> Acme["Acme Retail<br/>（bundles/acme_retail/）"]
    
    style KC fill:#f5f5f5,stroke:#333,stroke-width:2px
    style Format fill:#e8f5e9,stroke:#2e7d32
    style Agent fill:#e3f2fd,stroke:#1565c0
    style Viz fill:#fce4ec,stroke:#c2185b
    style Samples fill:#fff3e0,stroke:#e65100
```

## 0.9 为什么知识平台重要

- **模型是租的，可以换**：GPT换Claude换Gemini，随时切换
- **框架是工具，可以换**：LangChain换LlamaIndex换自研，工具而已
- **Skills是招式，可以学**：新技能可以快速开发、训练、迭代
- **数据与知识是企业自己的，是长期不被商品化的护城河**：业务概念、数据定义、指标口径、操作流程、决策逻辑、历史经验——这些才是真正沉淀下来、不可替代的核心资产

Knowledge Catalog与OKF要做的，就是让这些核心资产有一个开放、可移植、可演进、能被AI Agent直接消费的载体，让知识管理像代码管理一样工程化。

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [README（目录）](README.md) | [README](README.md) | [01 核心概念与平台架构](01-core-concepts.md) |


---

# 01 核心概念与平台架构

## 1.1 核心设计哲学

Knowledge Catalog 平台建立在三大设计哲学之上，这些哲学贯穿于格式定义、参考实现与生态工具的各个层面。

### 1.1.1 人与Agent共读（Human- and Agent-Readable）

知识表示格式必须同时对人类和智能体友好，无需专用SDK或查询语言即可直接访问：

- **人类可读**：工程师可以使用 `cat` 命令直接查看概念文档，无需安装专有工具；内容以标准Markdown编写，支持现有编辑器直接编辑。
- **Agent可解析**：智能体无需定制SDK即可解析YAML frontmatter提取结构化元数据，Markdown正文可直接注入LLM上下文窗口。
- **结构化优先**：鼓励使用标题、列表、表格、围栏代码块等结构化Markdown元素，而非自由文本——这既提升人类阅读体验，也显著提高RAG检索准确率，减少幻觉。

> **与OKF格式关系**：本平台采用 Open Knowledge Format (OKF) 作为底层知识表示格式。OKF的极简设计（Markdown + YAML frontmatter）正是实现人与Agent共读的基础。

### 1.1.2 Git原生（Git-Native Version Control）

知识管理应成为正常的软件工程活动，而非孤立的元数据存储：

- **天然版本控制**：Bundle以Git仓库形式分发，Pull Request、逐行diff、blame、代码评审等工作流开箱即用。
- **可审计变更**：每一次知识更新都有完整的提交历史，支持追溯"谁在何时修改了什么"。
- **协作标准化**：人类工程师、参考Agent、自动化流程可以像协作源代码一样在同一知识包上协作。
- **无中央服务器**：无需依赖专有元数据存储服务，知识包就是普通目录，可以通过tarball、静态文件服务器、任意Git托管平台分发。

### 1.1.3 生产消费解耦（Producer/Consumer Independence）

知识生产者与消费者彻底分离，格式是唯一契约：

- **多生产者支持**：人类手工编写、基于任意框架（Google ADK、LangChain、自定义）的Agent生成、现有数据目录（Dataplex、Unity Catalog、Collibra）导出管道、数据库扫描脚本——任何角色都可以产出OKF Bundle。
- **多消费者支持**：静态文件服务器、知识管理UI（Obsidian、Notion、MkDocs）、LLM上下文加载、搜索索引、图谱查看器——任何角色都可以消费同一Bundle。
- **避免平台锁定**：就像HTML不关心是VS Code还是Word编写，也不关心Chrome还是Safari打开，OKF不绑定特定Agent框架、模型供应商或服务系统。

## 1.2 核心概念体系

本节定义Knowledge Catalog平台的核心术语。其中格式层概念遵循 OKF核心规范。

### 1.2.1 Bundle（知识包）

**知识包（Knowledge Bundle）** 是自包含的知识文档层次集合，是分发和版本控制的基本单元。

- **物理形态**：一个Markdown文件目录树，可作为Git仓库、zip/tarball归档或monorepo子目录存在。
- **目录组织**：目录结构由生产者自行定义，平台不强制特定分类方式。
- **分发单元**：Bundle是跨系统、跨组织交换知识的最小单位。

**保留文件名**（任何层级均不得用作Concept文件名）：

| 文件名 | 用途 |
|--------|------|
| `index.md` | 目录内容列表，支持渐进式披露 |
| `log.md` | 该范围内的高层变更历史 |

### 1.2.2 Concept（概念文档）

**概念（Concept）** 是Bundle内的一个知识单元，对应一个UTF-8编码的Markdown文件。

- **描述对象**：可以描述有形资产（表、API端点）、抽象概念（指标、业务流程）或任何其他知识实体。
- **概念ID（Concept ID）**：文件在Bundle内的相对路径（去掉`.md`后缀），是概念的稳定标识符。
- **文件结构**：每个Concept由两部分组成：YAML frontmatter元数据块 + Markdown正文。

### 1.2.3 Frontmatter（元数据头）

**Frontmatter** 是文件开头以`---`分隔的YAML元数据块，承载结构化、可查询的字段。

**必填字段**：

| 字段 | 说明 |
|------|------|
| `type` | 概念类型（如`BigQuery Table`、`Metric`、`Playbook`、`Attested Computation`）。类型值不集中注册，由生产者自描述；消费者必须优雅容忍未知类型。 |

**推荐字段**：

| 字段 | 说明 |
|------|------|
| `title` | 人类可读名称，省略时消费者可从文件名推导 |
| `description` | 一句话摘要，用于索引生成、搜索片段、预览卡片 |
| `resource` | 所描述资产的规范URI（如BigQuery控制台链接），抽象概念可省略 |
| `tags` | YAML列表形式的横切分类标签 |

**可扩展字段**：生产者可添加任意自定义键值对，消费者往返处理时应保留未知字段，不得因无法识别的字段拒绝文档。

### 1.2.4 Source（来源与可信度信号）

**来源（Source）** 记录概念衍生自的材料（Bundle内部或外部），承载在`sources` frontmatter字段中，是对抗幻觉的关键机制。

每个来源条目包含：

| 字段 | 必填 | 说明 |
|------|------|------|
| `resource` | ✅ | 具体工件的可访问路径（绝对URL、Bundle相对路径、`references/`子目录路径）或范围描述符 |
| `id` | 推荐 | 稳定键，用于正文中的逐句归因（通过Markdown脚注关联） |
| `title` | 可选 | 来源的人类可读标签 |

**可信度信号**（客观、逐来源记录，供消费者推断信任度，而非存储主观评分）：

- `author`：来源的生产者（遵循Actor约定），权威性信号。
- `usage_count`：在`usage_window`内`resource`被使用的次数（仪表盘浏览量、查询执行次数、页面阅读量），采用度与活跃度信号。
- `last_modified`：来源本身最后变更日期（`YYYY-MM-DD`），时效性信号（与`generated.at`记录概念编写时间不同）。
- `usage_window`：`{ from, to }`日期范围，统一框定所有`usage_count`的统计窗口。

**逐句归因**：正文中的特定主张使用Markdown脚注标注，脚注标签为`sources[].id`，消费者通过匹配的条目解析归因，而非解析脚注文本。

### 1.2.5 Trust Tier（信任层级）

**信任层级（Trust Tier）** 是消费者从`verified`字段推导的可信度等级（建议性信号，非访问控制）：

| 层级 | 条件 |
|------|------|
| **unverified（未验证）** | 无`verified`键 |
| **machine-confirmed（机器确认）** | `verified`仅包含非`human:`执行者 |
| **human-reviewed（人类审核）** | `verified`包含`human:<id>`执行者 |

**相关字段**：

- `generated: { by, at }`：记录当前内容的生产者（`by`遵循Actor约定，`at`为ISO 8601时间）和最后有意义变更时间。
- `verified: [{ by, at }]`：验证事件列表，记录谁/什么对照来源或`resource`确认了内容；内容编写者与验证者分离。
- `status`：生命周期状态（`draft`/`stable`/`deprecated`），缺失时默认为`stable`。
- `stale_after`：绝对过期日期（`YYYY-MM-DD`），当`today >= stale_after`时概念视为过时。

**Actor约定**：

- Agent/工具：`<producer>/<version>`，如`reference_agent/gemini-2.5-pro`
- 人类：`human:<id>`，如`human:ahormati`
- 自动化流程：`process:<id>`，如`process:finance-nightly`

### 1.2.6 Attested Computation（认证计算）

**认证计算（Attested Computation）** 是一种特殊Concept类型（`type: Attested Computation`），不仅承载值的含义，还承载值的**受认可计算方式**，使消费者能够确认Agent运行了指定计算而非自行编造。

**核心设计动机**：

- 来源（Provenance）回答"这个主张从哪里来"；认证（Attestation）回答"这个数字是否按规定方式产生"。
- 一个计算可服务于多个消费者（指标、仪表盘概念、报表），作为独立Concept可一次定义多次引用。
- 信任状态按计算独立维护：收入、利润、毛利各自独立验证和认证。

**契约字段**（frontmatter）：

| 字段 | 必填 | 说明 |
|------|------|------|
| `runtime` | ✅ | 运行时类型（如`bigquery`、`postgres`、`dbt`、`python`、`Looker`），决定`parameters`语义、执行器和认证器解释方式 |
| `parameters` | 可选 | 类型化命名参数列表：`{ name, type, required }`；Agent只能为声明的参数提供值，不得编写或修改计算本身 |
| `computation` | 可选 | 指向计算文件的路径（替代正文内联围栏代码块）；缺失时正文`# Computation`围栏块为计算内容 |
| `executor` | 可选 | 执行方式：`resource`指向运行指令或代码，`receipt`声明运行必须返回的证据字段列表 |
| `attester` | 可选 | 确定性（无LLM）检查代码：`resource`指向接收receipt并返回结论的代码，在消费者侧运行 |

**计算提供方式**：

- **内联**：正文`# Computation`标题下的单个围栏代码块，适合短小、与契约一同评审的计算。
- **文件引用**：设置`computation`为路径并省略正文围栏，适合较长或生成的计算、或已作为真实文件与非OKF工具共享的计算。

**验证与认证的区别**：

- `verified`：确认定义仍符合策略，文档级别、慢速、记录在Bundle内。
- Attestation：确认单次运行按受认可方式产生值，每次调用、运行时、不存储在Bundle内。

### 1.2.7 Index/Log文件（索引与日志文件）

**索引文件（index.md）** 支持渐进式披露：

- 可出现在任何目录（包括Bundle根目录）。
- 无frontmatter（例外：Bundle根index.md可携带`okf_version`键）。
- 作用：让人类或Agent在打开单个文档前即可了解目录内容。
- 结构：按逻辑分组，列出Concept链接及description。
- 可自动生成，也可手写；无index.md时消费者可动态扫描合成。

**日志文件（log.md）** 记录高层变更历史：

- 可出现在任何层级，记录该范围的高层更新历史（类似CHANGELOG，非逐条commit记录）。
- 格式：按ISO日期（`YYYY-MM-DD`）倒序排列，每个日期下是条目。
- 条目通常以粗体动词开头（**Create**/**Update**/**Deprecation**），这是约定而非强制要求。

**log.md vs git log**：git log是细粒度提交历史（如"修复typo"）供开发者查看；log.md是高层摘要（如"5月新增客户指标表"）供人类/Agent快速浏览演变脉络。

## 1.3 平台架构分层

Knowledge Catalog平台采用四层架构，从底层格式到上层应用清晰分离：

```mermaid
flowchart TD
    subgraph Layer4["第四层：应用与工具层 Applications & Tools"]
        A1["参考Agent<br/>(reference_agent)"]
        A2["可视化工具<br/>(viz.html)"]
        A3["第三方UI<br/>(Obsidian/Notion/MkDocs)"]
        A4["搜索索引/图谱查看器"]
    end

    subgraph Layer3["第三层：生态集成层 Ecosystem Integration"]
        E1["BigQuery元数据导出"]
        E2["Web文档爬取与 enrichment"]
        E3["现有目录导入<br/>(Dataplex/Unity Catalog)"]
        E4["references/ 约定<br/>(外部材料镜像)"]
    end

    subgraph Layer2["第二层：OKF格式层 Open Knowledge Format"]
        F1["Bundle目录结构"]
        F2["Concept文件<br/>(YAML Frontmatter + Markdown Body)"]
        F3["跨链接规则<br/>(Absolute/Relative Links)"]
        F4["信任与生命周期<br/>(sources/generated/verified/status/stale_after)"]
        F5["认证计算<br/>(Attested Computation)"]
        F6["Index/Log保留文件"]
    end

    subgraph Layer1["第一层：基础设施工具层 Infrastructure"]
        I1["Git版本控制"]
        I2["文件系统"]
        I3["标准Markdown/YAML解析器"]
        I4["静态文件服务"]
    end

    Layer1 --> Layer2
    Layer2 --> Layer3
    Layer3 --> Layer4

    A1 --> E1
    A1 --> E2
    A2 --> F2
    A2 --> F3
    E1 --> F1
    E2 --> F2
    E3 --> F1
```

### 1.3.1 第一层：基础设施工具层

平台不引入专有基础设施，完全构建在通用、成熟的工具之上：

- **Git**：提供版本控制、分发、协作评审能力。
- **文件系统**：Bundle就是普通目录，无需数据库或专有存储。
- **标准Markdown/YAML解析器**：任何语言的标准库解析器都可读取OKF，无专用SDK依赖。
- **静态文件服务**：可通过任意静态HTTP服务器托管Bundle。

### 1.3.2 第二层：OKF格式层

这是平台的核心契约层，定义知识表示的结构规则：

- Bundle目录结构规范与保留文件名约定。
- Concept文件的两部分结构（YAML Frontmatter + Markdown Body）。
- 跨链接规则（Bundle绝对链接/相对链接）与断链容忍策略。
- 信任来源与生命周期字段家族（sources/generated/verified/status/stale_after）。
- 认证计算类型的专用契约字段。

> **规范说明**：格式层的完整规范见 OKF格式核心概念 与OKF SPEC文档。

### 1.3.3 第三层：生态集成层

该层提供将外部世界知识转化为OKF Bundle的生产能力，以及约定性的组织模式：

- **BigQuery元数据导出**：从BigQuery数据集提取表、列、分区等元数据作为初始Concept。
- **Web文档爬取与enrichment**：参考Agent作为自主爬虫，抓取权威文档URL并丰富现有Concept。
- **现有目录导入**：从Dataplex、Unity Catalog、Collibra等现有数据目录批量导出为OKF。
- **`references/`目录约定**：将外部材料、运行指令、代码镜像为Bundle内的一类Concept，sources/executor/attester通常指向该目录。

### 1.3.4 第四层：应用与工具层

该层包含具体的生产者、消费者实现：

- **参考Agent（reference_agent）**：平台提供的概念验证生产者，分两阶段运行——BQ Pass（从BigQuery元数据生成初始Concept）和Web Pass（LLM自主爬取文档并丰富Concept）。
- **可视化工具（viz.html）**：自包含交互式HTML可视化，使用Cytoscape.js绘制力导向图谱、marked.js渲染Markdown，是概念验证消费者。
- **第三方UI集成**：Obsidian、Notion、MkDocs、Hugo、Jekyll等现有Markdown工具可直接浏览/编辑Bundle。
- **搜索索引/图谱查看器**：消费者可从frontmatter提取`type`、`tags`等字段构建搜索索引，或从跨链接构建关系图谱。

## 1.4 组件关系图

以下Mermaid图展示Knowledge Catalog平台核心组件之间的关系与数据流：

```mermaid
flowchart LR
    subgraph Producers["生产者侧"]
        Human["人类作者<br/>(human:id)"]
        RefAgent["参考Agent<br/>(reference_agent/gemini-2.5-pro)"]
        Pipeline["导出管道<br/>(process:id)"]
    end

    subgraph BundleNode["OKF Bundle (Git仓库)"]
        direction TB
        IndexMD["index.md<br/>(渐进式披露)"]
        LogMD["log.md<br/>(变更历史)"]
        Concepts["Concept文档<br/>(*.md)"]
        Computations["Attested Computation<br/>(type: Attested Computation)"]
        Refs["references/<br/>(外部材料镜像)"]

        Concepts -->|"链接"| Computations
        Computations -->|"executor/attester指向"| Refs
        IndexMD -->|"列出"| Concepts
        IndexMD -->|"列出"| Computations
    end

    subgraph Consumers["消费者侧"]
        VIZ["可视化工具<br/>(viz.html)"]
        LLM["LLM/Agent<br/>(上下文加载)"]
        Search["搜索/索引"]
        ThirdPartyUI["第三方UI<br/>(Obsidian/MkDocs)"]
        AttestRunner["认证运行器<br/>(执行+验证)"]
    end

    subgraph RuntimeArtifacts["运行时工件 不存储在Bundle"]
        Receipt["Receipt<br/>(执行证据：job_id/executed_sql/result)"]
        Verdict["Verdict<br/>(认证结论)"]
    end

    Human -->|"编写/评审"| BundleNode
    RefAgent -->|"生成/丰富"| BundleNode
    Pipeline -->|"批量导出"| BundleNode

    BundleNode -->|"读取"| VIZ
    BundleNode -->|"读取"| LLM
    BundleNode -->|"扫描"| Search
    BundleNode -->|"直接浏览"| ThirdPartyUI

    Computations -->|"加载契约"| AttestRunner
    AttestRunner -->|"执行"| Receipt
    AttestRunner -->|"运行attester"| Verdict
    Receipt -->|"检查"| Verdict

    style BundleNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style RuntimeArtifacts fill:#fff3e0,stroke:#e65100,stroke-width:1px,stroke-dasharray:5 5
```

### 1.4.1 数据流说明

1. **生产阶段**：人类作者、参考Agent、自动化管道通过Git协作向Bundle贡献Concept文档；参考Agent支持单Concept迭代（`--concept`参数）。
2. **存储阶段**：所有知识以纯文本Markdown文件存储在Git仓库中，Index和Log文件提供导航和历史摘要。
3. **消费阶段**：
   - 可视化工具、LLM、搜索索引、第三方UI直接读取Bundle内容。
   - 认证运行器在运行时加载Attested Computation契约，绑定参数后通过executor执行，获得Receipt，再通过attester（确定性无LLM代码）检查Receipt产出Verdict。
4. **信任传播**：Receipt和Verdict是运行时工件，不存储在Bundle中；认证失败时消费者应拒绝显示或给出警告，而非静默丢弃。

### 1.4.2 参考Agent两阶段工作流

参考Agent作为平台提供的概念验证生产者，采用两阶段流水线：

1. **BQ Pass**：仅使用BigQuery元数据，为数据源 advertised 的每个Concept写入一个OKF文档。
2. **Web Pass**：LLM作为自主爬虫运行——接收种子URL列表，通过`fetch_url`工具抓取种子页面，根据出站链接是否看起来像现有Concept的权威文档决定是否跟进；对每个抓取页面选择（a）丰富现有Concept、（b）创建独立`references/<slug>`文档、（c）跳过。

Web Pass内置安全限制：硬上限`--web-max-pages`、同域允许主机过滤器（`--web-allowed-host`可配置），使用`--no-web`可跳过Web Pass。

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [00 概述与知识地图](00-overview.md) | [README](README.md) | [02 OKF格式规范](02-okf-specification.md) |
