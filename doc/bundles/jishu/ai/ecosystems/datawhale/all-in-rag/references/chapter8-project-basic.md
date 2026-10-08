---
type: reference
title: "第八章 项目实战一（基础篇）"
bundle: /datawhale/all-in-rag
description: "基于HowToCook菜谱数据集的'尝尝咸淡'食谱问答系统，涵盖环境配置、数据准备、索引构建、检索优化、生成集成与系统整合"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter8/
path: docs/chapter8/
code:
  - code/C8/
tags: [project, recipe, faiss, langchain, kimi, hybrid-search, query-routing]
status: stable
---

# 第八章 项目实战一（基础篇）

## 信源信息

- **章节路径**：`docs/chapter8/`
- **代码路径**：`code/C8/`
- **小节列表**：
  - 环境配置与项目架构（`01_env_architecture.md`）
  - 数据准备模块实现（`02_data_preparation.md`）
  - 索引构建与检索优化（`03_index_retrieval.md`）
  - 生成集成与系统整合（`04_generation_sys.md`）

## 内容概要

### 第一节 环境配置与项目架构

- 项目背景：基于 HowToCook 菜谱数据集构建"尝尝咸淡"智能问答系统
- 环境配置：Python 3.12.7、依赖安装、Kimi API Key 配置
- 项目目标：菜品做法查询、菜品推荐、食材信息咨询
- 数据分析：约 300+ Markdown 菜谱，结构规整、篇幅约 700 字
- 系统架构设计：数据准备→索引构建→检索优化→生成集成四模块

### 第二节 数据准备模块实现

- Markdown 文档加载
- 元数据提取（菜品名、分类、难度）
- 父子文档分块策略

### 第三节 索引构建与检索优化

- FAISS 向量索引构建与持久化
- 混合检索实现
- 元数据过滤搜索

### 第四节 生成集成与系统整合

- Kimi（Moonshot）API 集成
- 查询路由（list/detail/general 三种类型）
- 查询重写
- 多模式生成（列表回答、分步指导、基础回答）
- 流式输出
- 交互式问答主程序

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C8/main.py` | RecipeRAGSystem 主类，串联全流程 |
| `code/C8/config.py` | RAGConfig 配置管理 |
| `code/C8/rag_modules/data_preparation.py` | 数据准备模块 |
| `code/C8/rag_modules/index_construction.py` | 索引构建模块 |
| `code/C8/rag_modules/retrieval_optimization.py` | 检索优化模块 |
| `code/C8/rag_modules/generation_integration.py` | 生成集成模块 |
| `code/C8/requirements.txt` | 项目依赖 |

## 对应概念与示例

- [项目实战](../concepts/project-practice.md)
- [基础RAG食谱问答系统](../examples/c8-basic-rag.md)
