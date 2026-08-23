---
type: Concept
title: Invocations 简介
description: 什么是 Invocations、设计哲学、与 PyInvoke 的关系、适用场景
tags: [invocations, introduction, best-practices, task-collections]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T16:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: invocations-source
    resource: /references/invocations-source.md
---

# Invocations 简介

## 什么是 Invocations

**Invocations** 是 [PyInvoke](/concepts/00-introduction.md) 官方维护的**可复用任务集合库**（reusable task collections）。它将 Python 项目中常见的自动化工作流——代码格式化、测试运行、文档构建、包发布、CI 环境设置等——封装为即插即用的 Invoke 任务模块。

Invocations 最初源自 Invoke 项目自身的 `tasks.py`，后来被抽离为独立库，目标是成为 Python 项目自动化"最佳实践"的交换中心（clearinghouse）。

## 与 PyInvoke 的关系

| | PyInvoke (invoke) | Invocations (invocations) |
|---|---|---|
| 定位 | 任务执行**框架/引擎** | 任务**集合/菜谱库** |
| 核心提供 | @task 装饰器、Context、Collection、Executor、Runner 等执行基础设施 | 开箱即用的 @task 定义、Collection 配置、工具函数 |
| 类比 | Make（引擎） | Makefile 片段集（菜谱） |
| 用户角色 | 框架用户，自己写所有任务 | 库用户，组装已有任务 + 编写自定义任务 |

简单说：**PyInvoke 给你锤子和钉子，Invocations 给你预制的家具模块**。你可以只用 PyInvoke 从零写所有任务，也可以导入 Invocations 的任务模块快速搭出常用工作流。

## 设计哲学

Invocations 遵循以下设计原则：

- **模块化组合（Modular Composition）**：每个功能领域（测试/文档/发布/检查/CI）是独立模块，用户按需导入、自由组合，不强制"全家桶"
- **配置驱动（Configuration-Driven）**：每个任务集合通过 `ns.configure()` 提供合理默认值，用户通过自己的 Collection 配置覆盖
- **双层 API（Two-Layer API）**：模块同时暴露可在命令行调用的 @task 任务和可在 Python 代码中复用的工具函数
- **半自动而非全自动（Semi-Automatic）**：关键操作（如发布）采用"检查→确认→执行→验证"流程，保留人工审核环节而非一键黑箱
- **防御性编程（Defensive）**：如发布流程中的 `twine check`、临时 venv 安装测试、dry-run 模式等安全网

## 功能概览

| 模块 | 功能 | 典型命令 |
|------|------|---------|
| `checks` | 代码格式化与 lint | `inv blacken`, `inv lint`, `inv checks.all` |
| `pytest` | Pytest 测试执行 | `inv test`, `inv integration`, `inv coverage` |
| `testing` | 旧版 Spec/Nose 测试（含 flakiness 检测） | `inv test`, `inv watch-tests`, `inv count-errors` |
| `docs` | Sphinx 文档构建与监控 | `inv docs.build`, `inv docs.watch-docs`, `inv docs.sites` |
| `packaging.release` | Python 包发布全流程 | `inv release.status`, `inv release`, `inv release.publish` |
| `packaging.vendorize` | 第三方依赖 vendor 化 | `inv vendorize` |
| `ci` | CI 环境 sudo 用户/SSH 设置 | `inv make-sudouser`, `inv sudo-run` |
| `autodoc` | Sphinx 扩展（文档化 Task 对象） | 在 conf.py 中添加扩展 |
| `console` | 终端交互工具 | `from invocations.console import confirm` |
| `util` | 通用工具 | `from invocations.util import tmpdir` |
| `watch` | 文件监控 | `from invocations.watch import watch, observe` |
| `environment` | 环境检测 | `from invocations.environment import in_ci` |

## 安装

```bash
pip install invocations
```

安装后在你的 `tasks.py` 中按需导入即可。部分功能（如文件监控）需要额外安装可选依赖：

```bash
pip install watchdog  # 文件监控
```

## 适用场景

Invocations 特别适合以下场景：

1. **Python 开源项目维护者**：需要标准的测试→构建→文档→发布流水线
2. **多项目开发者**：不想在每个项目中重复编写类似的 tasks.py
3. **学习 PyInvoke 最佳实践**：Invocations 的源码本身就是 PyInvoke 高级用法的优秀范例
4. **需要 Sphinx + CI + PyPI 发布标准流程**的项目

[^invocations-source]: Invocations 源码信源，见 [invocations-source.md](/references/invocations-source.md)。
