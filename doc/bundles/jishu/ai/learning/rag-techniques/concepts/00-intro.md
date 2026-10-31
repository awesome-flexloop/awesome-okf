---
okf_version: "0.2"
type: concept
title: RAG_Techniques 项目概述
description: NirDiamant/RAG_Techniques 仓库的身份、定位、核心数据与组织结构（F-001 至 F-020）
tags: [rag, rag-techniques, nirdiamant, overview, notebook]
generated:
  by: seven-concepts-cmd
  at: "2026-10-31T11:00:00+08:00"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA
  - id: github-rag-techniques
    url: https://github.com/NirDiamant/RAG_Techniques
---

# RAG_Techniques 项目概述

## 项目基本信息

| 属性 | 值 | F 编号 |
|------|-----|--------|
| 仓库 | `NirDiamant/RAG_Techniques` | F-002 / F-046 |
| GitHub | https://github.com/NirDiamant/RAG_Techniques | — |
| 作者 | Nir Diamant（个人账号） | F-046 |
| 定位 | 可执行的 RAG 故障对照表（**非框架**） | F-003 |
| 组织方式 | 按 RAG pipeline 阶段分段 | F-006 |
| License | Custom License Agreement（非商用，非标准开源协议） | F-037 |

## 核心数据

> ⚠️ Star 数为 2026-10-31 核实时点值；博文发布时（2026-10-27）口径为 **30,003**（F-004）。

| 指标 | 核实时值 | F 编号 |
|------|---------|--------|
| GitHub Star 数 | 30,149 | F-047 |
| 技术 notebook 数 | 42（`all_rag_techniques/*.ipynb`） | F-005 / F-048 |
| 可运行脚本数 | 21（`all_rag_techniques_runnable_scripts/*.py`） | F-009 / F-049 |
| 统一依赖清单 | 无（全树无 `requirements.txt`） | F-026 / F-050 |

## 它是什么

一句话：**它不是框架，是一张可执行的 RAG 故障对照表**（F-003）。

每个 notebook 对应一个具体失效模式，内含直觉解释、可运行代码与参考文献。与多数 RAG 教程「按算法热度排」不同，本仓库按 **RAG pipeline 的阶段** 排序（F-006）——对工程团队友好之处在于：**系统卡在哪一段，直接翻那一段**。

## 组织结构：七段 pipeline 归并视图

博文将 42 篇分为七段（F-007 / F-010）：

| 段 | 篇数（博文口径） | 代表篇目 |
|----|----------------|---------|
| 基础 | 6 | 最朴素 RAG、CSV 问答、可靠 RAG、chunk 大小选择、命题切分、Mistral OCR 文档解析 |
| 查询改写 | 3 | 查询变换、HyDE、HyPE |
| 上下文增强 | 6 | 块头上下文、相关片段抽取、窗口扩展、语义切分、上下文压缩、文档增强 |
| 高级检索 | 6 | 融合检索、重排序、多面过滤、层级索引、飞镖盘检索、多模态描述 |
| 迭代与自适应 | 2 | 反馈回路、自适应检索 |
| 评估 | 4 | DeepEval、GroUSE、端到端评估、Open-RAG-Eval |
| 进阶架构 | 8 | Graph RAG、微软 GraphRAG、RAPTOR、Agentic RAG、Self-RAG、CRAG、可验证归因的本地 Graph RAG、LightRAG |

> ⚠️ **口径说明**（F-007 / F-051）：七段篇数之和为 6+3+6+6+2+4+8 = **35**，与「42 个 notebook」不等。核验确认逐段篇数与 README 完全吻合，说明七段是**按 pipeline 阶段的归并视图**；而 `all_rag_techniques/` 下 `.ipynb` 实测为 **42 个**。README 自身也同时存在「42 notebooks」与表格 38 行 / 10 分类标签的口径张力。**本 bundle 以目录树实测值 42 为准**，七段作为归类视角呈现。

## 三个值得单独说的设计

### 1. notebook 与脚本双轨（F-011）

`all_rag_techniques/` 下 42 个 `.ipynb`，`all_rag_techniques_runnable_scripts/` 下 21 个 `.py`（F-008 / F-009）。notebook 展示每一步的中间结果（切完的块长什么样、召回的 top_k 分布、重排前后的分数变化），脚本供直接拿去做集成。

多数教程只做前者；只做前者的问题是「学完还得自己翻译成工程代码，中间那一步最容易走样」。

### 2. 按软件工程方式维护教学内容（F-012~F-015）

| 组件 | 作用 |
|------|------|
| `tests/test_imports.py` | 用 nbformat 解析每个 notebook，把 import 语句抽出来执行 |
| `.github/workflows/` | `github-test.yml`、`local-test.yml`（测试流水线） |
| `.github/dependabot.yml` | 自动更新依赖版本 |
| `.pr_agent.toml` | Qodo PR 自动审查 |
| `AGENTS.md` / `llms.txt` / `REVIEW.md` | 面向智能体与贡献者的元文件 |

这套测试的意义在于**保证 notebook 的依赖不会烂掉**（F-016）——RAG 教程常见的死法是「半年后 pip install 一片红」。

> ⚠️ **时效提示**（F-013 / F-053）：`github-test.yml` 在博文时点（2026-10-27）存在，核验当日（2026-10-31）的提交 #211「Fix the 31 Oct audit…CI…」已将其移出。工作流迭代活跃，具体清单以仓库当前状态为准。

### 3. 三种学习入口（F-017 / F-018）

- **notebook**：42 篇分类盘点与可运行代码；
- **配套书《RAG Made Simple》**：博文称「400 页可视化版，据官方标注是 Amazon 生成式 AI 畅销书」——⚠️ **属作者自述式标注**（F-054），第三方书目站各版本页数为 250 / 427（F-055），与「400 页」口径不一致；
- **作者 YouTube 系列**：一集讲一个概念；官方档案另四个视频对应四个问题——RAG 为什么会答错你自己的文档、怎么按语义搜一张表格、怎么判断答案不是编的、为什么问一个事实却返回一整段。

## 作者生态

Nir Diamant 在该方向上有持续产出，除本仓库外还有 GenAI Agents、Prompt Engineering、Agent Memory Techniques 等仓库（F-020 / F-057）。

> 作者观点（F-043）：项目维护动力来自作者个人品牌与商业闭环，更新节奏取决于个人精力，**不应视作带 SLA 的基础设施**。

## 主题关联

- [01-techniques](./01-techniques.md)：七段技术机制详解与代表性架构
- [02-practice](./02-practice.md)：安装现状、企业落地与边界约束
