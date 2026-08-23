---
okf_version: "0.2"
type: group
title: "⚡ FastAPI Web 框架生态"
description: "FastAPI 高性能 ASGI Web 框架及其同生态项目的源码级中文教程"
---

# ⚡ FastAPI Web 框架生态

本组存放 [FastAPI](https://fastapi.tiangolo.com/) 及其同生态项目（由 Sebastián Ramírez 创建）的源码级中文教程。

> **生态关系**：FastAPI 构建在 Starlette（ASGI 工具包）和 Pydantic（数据验证）之上；Typer（CLI 框架）和 SQLModel（数据库 ORM）复用了 FastAPI 的类型注解驱动设计理念。

## 学习路径

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 1 | [fastapi](fastapi/index.md) | FastAPI 核心框架——类型注解驱动、依赖注入树、APIRouter 组合、OpenAPI 自动生成、SSE/JSONL 流式、双层 AsyncExitStack 生命周期（14概念+5示例+8信源，共27文档） |
