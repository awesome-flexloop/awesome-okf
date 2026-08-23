---
type: Concept
title: jupyter-cache 简介
description: jupyter-cache 是什么——Jupyter Notebook执行结果的通用缓存层，避免重复执行，支持CI和文档构建
tags: [jupyter, cache, notebook, execution, introduction, mybinder]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T04:34:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: jc-source
    resource: /references/cache-source.md
    title: jupyter-cache 源码路径映射
---

# jupyter-cache 简介

jupyter-cache 是 Executable Books 生态中的 Jupyter Notebook 执行缓存工具。它为 Notebook 执行结果提供通用缓存层，避免在文档构建和CI流程中重复执行未修改的 Notebook，显著减少构建时间。

## 解决的问题

在使用 MyST-NB、jupyter-book 等工具构建包含 Notebook 的文档时，每次构建都重新执行所有 Notebook 非常耗时：
- 数据分析 Notebook 可能执行数分钟甚至数小时
- 代码未修改但重新执行产生相同结果，浪费资源
- CI 流水线每次都要等待 Notebook 执行完成

jupyter-cache 通过内容哈希缓存机制解决这个问题：**只有代码内容发生变化的 Notebook 才会被重新执行**。

## 核心功能

- **内容哈希缓存**：基于 Notebook 代码单元格内容计算 hashkey，相同代码复用缓存
- **SQLite 持久化**：缓存元数据存储在 SQLite 数据库中
- **双表分离设计**：项目 Notebook 列表与缓存结果独立管理
- **执行器插件体系**：支持多种执行后端（本地 Kernel、Docker等）
- **命令行工具**：`jcache` CLI 管理缓存和执行
- **Python API**：编程方式操作缓存
- **LRU 自动淘汰**：缓存超限时自动清理最旧记录
- **Artifact 管理**：Notebook 执行产生的关联文件（图片等）一并缓存
- **并行构建安全**：SQLAlchemy session 事务管理

## 架构概览

```
项目 Notebook (nbproject表)
       │
       │ 内容哈希匹配
       ▼
执行缓存 (nbcache表) ←→ 文件系统 (executed/{hashkey}/)
       │
       │ 插件体系
       ▼
执行器 (executors/)  ←→ Kernel/Docker/云
```

## 适用场景

- **文档构建**：jupyter-book/MyST-NB 构建时缓存 Notebook 输出
- **CI/CD 流水线**：仅重新执行修改过的 Notebook
- **Notebook 批处理**：管理大量 Notebook 的执行和结果缓存
- **教学环境**：缓存教学 Notebook 的标准输出

## 缓存目录结构

```
.jupyter_cache/
├── global.db              # SQLite数据库
├── __version__.txt        # 缓存版本
└── executed/
    └── {hashkey}/
        ├── base.ipynb     # 执行后的Notebook
        └── artifacts/     # 关联资源文件
```

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [缓存架构设计](/concepts/02-architecture.md)
- [CLI 命令参考](/concepts/05-cli-reference.md)
