---
okf_version: "0.2"
title: "nbformat"
description: "Jupyter Notebook格式参考实现：.ipynb文件的读写、验证、版本转换与签名信任。本知识包从源码出发，系统讲解nbformat的架构、API和实战用法。"
---

# nbformat

> Jupyter Notebook 文件格式的 Python 参考实现。`nbformat` 提供 `.ipynb` 文件的读写、验证、版本转换和签名信任等核心能力。

## 快速导航

### [核心概念](concepts/index.md)

11篇概念文档，从入门到深入系统讲解nbformat：

- **入门**：[简介](concepts/00-introduction.md) → [5分钟上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md)
- **核心**：[NotebookNode](concepts/03-notebook-node.md) · [读写API](concepts/04-read-write-api.md) · [版本转换](concepts/05-version-system.md) · [验证体系](concepts/06-validation.md)
- **进阶**：[构造API](concepts/07-notebook-construction.md) · [信任签名](concepts/08-trust-and-signing.md) · [v4格式详解](concepts/09-v4-format.md) · [深入实战](concepts/10-advanced-patterns.md)

### [示例代码](examples/index.md)

3个可独立运行的实战示例：

- [创建和写入Notebook](examples/01-create-and-write.md)
- [读取、验证与转换](examples/02-read-validate-convert.md)
- [Notebook批处理与信任管理](examples/03-batch-processing-and-trust.md)

### [源码信源](references/index.md)

5个关键模块的源码解析文档，为概念文档中的溯源引用提供目标。

## 版本信息

| 属性 | 值 |
|------|-----|
| nbformat当前版本 | v4.5 |
| Python要求 | ≥ 3.10 |
| 许可证 | BSD-3-Clause |
| 源码路径 | `external/libs/jupyter/nbformat/nbformat/` |

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
