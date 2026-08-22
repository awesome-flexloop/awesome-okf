---
type: Concept
title: Papyri 简介
description: Papyri 是什么——将 Python 库 docstring 解析为可移植中间表示（IR）的文档工具，实现构建与渲染分离
tags: [papyri, introduction, documentation, ir]
generated: { by: reference_agent/trae-soLO, at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-api-check", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: papyri-src
    resource: /references/papyri-source.md
    title: Papyri Python 核心包源码信源
  - id: viewer-src
    resource: /references/viewer-source.md
    title: Papyri TypeScript 摄取器与查看器源码信源
---

## Papyri 是什么

Papyri 是一个 Python 工具，它将库的 docstring（文档字符串）解析为一种可移植的**中间表示（Intermediate Representation, IR）**，使得文档可以"一次构建、多次渲染"——独立于项目、跨项目地进行渲染。

项目名称来源于 [Villa of the Papyri](https://en.wikipedia.org/wiki/Villa_of_the_Papyri)（纸草别墅），以其收藏的大量纸草卷轴命名。当前版本为 0.0.10，处于活跃开发阶段，要求 Python 3.13+。

## Papyri 解决的两个核心问题

### 问题一：Sphinx 中构建与渲染耦合

在标准的 Sphinx 工作流中，**解析文档**和**渲染为 HTML** 发生在同一步骤中。这意味着：

- 修复 HTML 模板（例如为了可访问性）需要完全重建每个使用该模板的项目——包括重新安装项目、其依赖项，以及重新执行所有示例代码。
- 渲染环境必须与构建环境完全匹配。
- "项目文档的内容"和"文档的外观"之间没有可复用的产物。

Papyri 通过分离这两个关注点来解决：

1. **IR 生成**（`papyri gen`）——由库维护者在项目自己的 CI 或构建环境中运行，产生一个自包含的 *DocBundle*，以结构化的、与渲染器无关的格式捕获文档化的 API。
2. **渲染**——一个独立的、无状态的过程，读取 DocBundle 并生成 HTML。更新渲染器永远不需要触碰原始源码或重新运行项目的构建环境。

### 问题二：文档跨域碎片化

每个 Python 库都在自己的子域名上托管文档（`numpy.org/doc`、`docs.scipy.org`、`pandas.pydata.org/docs`……）。这导致：

- 无法在一个地方跨项目搜索。
- 无法在不离开当前域名的情况下跟踪跨包链接。
- 当上游 API 变化时，无法保持这些跨链接的有效性。

Papyri 的模型（灵感来自 conda-forge）：

- 每个库维护者在项目 CI 中运行 `papyri gen`，然后 `papyri upload` 生成的 DocBundle 到中央服务。
- 中央服务将 bundle 摄取到一个交叉链接的图中，并从一个地方提供所有服务，包间具有真正的双向交叉链接。TypeScript 的 `papyri-ingest` 包（位于 `ingest/` 目录）在服务端执行摄取，由 viewer 的上传端点调用。

## 核心设计理念

- **构建-渲染分离**：IR 是 Python 端（gen）和渲染端（viewer）之间的稳定契约
- **跨包交叉引用**：基于限定名系统实现包间链接
- **确定性输出**：同一输入产生字节相同的 `.papyri` 制品（canonical CBOR + zero-mtime gzip）
- **安全优先**：未处理的 RST 指令阻止序列化、URL 安全校验、路径遍历防护
- **双格式序列化**：JSON（人类可读的开发期 bundle 目录）→ CBOR（压缩传输的发布制品）

## 相关概念

- [架构总览](02-architecture-overview.md)：深入了解三端架构
- [IR 与 DocBundle](03-ir-and-docbundle.md)：理解中间表示的结构
- [快速开始](01-getting-started.md)：安装和基本使用
