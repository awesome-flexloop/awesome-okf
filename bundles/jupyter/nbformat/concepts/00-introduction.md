---
okf_version: "0.2"
type: "concept"
title: "nbformat 简介"
description: "Jupyter Notebook格式参考实现：nbformat是什么、核心能力、项目信息与许可证"
tags: [introduction, overview, jupyter, notebook-format]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyproject
    resource: /references/init-api.md
    title: "包入口公共API"
  - id: readme
    resource: "../../../../../external/libs/jupyter/nbformat/README.md"
    title: "README.md"
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/nbformat/pyproject.toml"
    title: "pyproject.toml"
---

# nbformat 简介

## 什么是 nbformat

nbformat 是 [Jupyter](https://jupyter.org/) 项目的 **Notebook 文件格式参考实现**，提供 `.ipynb` 文件的读写、验证、版本转换和签名信任等核心能力 [F-001]。它完全使用 Python 编写，采用 **BSD-3-Clause** 开源许可证，由 Jupyter Development Team 维护 [F-002]。

`.ipynb` 文件本质上是一个符合JSON Schema规范的JSON文档，nbformat 提供了：

1. **读写API**：从文件/字符串读取 Notebook 为 Python 对象，或将 Python 对象序列化为 JSON 文件/字符串
2. **版本管理**：支持 v1/v2/v3/v4 四个主版本间的自动升级与降级转换
3. **Schema验证**：基于JSON Schema验证Notebook结构合法性，支持 fastjsonschema（默认）和 jsonschema 双后端
4. **NotebookNode对象模型**：支持属性风格访问（`nb.cells`）的dict子类，替代原生dict操作
5. **信任签名**：基于HMAC的Notebook签名机制，标记可信/不可信输出，防止恶意HTML/JS执行
6. **构造工厂**：`new_notebook()`/`new_code_cell()`/`new_output()` 等工厂函数，程序化构建Notebook

## 项目信息

| 属性 | 值 |
|------|-----|
| 包名 | `nbformat` |
| 描述 | "The Jupyter Notebook format" |
| 许可证 | BSD-3-Clause |
| 构建系统 | hatchling + hatch-nodejs-version |
| Python要求 | ≥ 3.10（支持3.10-3.14）[F-003] |
| CLI入口 | `jupyter-trust`（签名Notebook） |
| 代码仓库 | https://github.com/jupyter/nbformat |
| 文档 | https://nbformat.readthedocs.io/ |

## 核心依赖

```
fastjsonschema>=2.15    # 默认JSON Schema验证后端
jsonschema>=2.6         # 备用JSON Schema验证后端（用于error_tree）
jupyter_core>=4.12,!=5.0.*  # Jupyter核心（数据目录、配置）
traitlets>=5.1          # 配置系统（NotebookNotary使用）
```

[F-004]

## nbformat 在 Jupyter 生态中的位置

nbformat 是 Jupyter 生态的**基础格式层**：

- **Jupyter Server/Lab/Notebook** 使用 nbformat 读写 `.ipynb` 文件
- **nbconvert** 使用 nbformat 加载Notebook后转换为HTML/PDF/Markdown等格式
- **ipykernel/xeus-python** 等内核通过 nbformat 构造输出对象
- **papermill** 等参数化执行工具基于nbformat操作Notebook

## 安装

```bash
pip install nbformat
```

切换验证后端为jsonschema：设置环境变量 `NBFORMAT_VALIDATOR=jsonschema` [F-005]。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
