# 核心概念索引

本目录包含nbformat的11个核心概念文档，按学习路径排列。

## 入门篇

* [nbformat简介](00-introduction.md) — 什么是nbformat、核心能力、项目信息、在Jupyter生态中的位置。
* [5分钟快速上手](01-getting-started.md) — 安装、基本读写、创建Notebook、验证、版本转换的最小示例。
* [架构总览](02-architecture-overview.md) — 四层架构（公共API层/核心服务层/对象模型层/版本实现层）、核心数据流、版本路由机制。

## 核心篇

* [NotebookNode与Struct](03-notebook-node.md) — NotebookNode对象模型：属性访问、自动嵌套转换、优化的深拷贝、Struct基类的merge和运算符重载。
* [读写API](04-read-write-api.md) — read/write/reads/writes四个核心API、NO_CONVERT哨兵、split_lines/rejoin_lines VCS友好机制、strip_transient临时字段清理。
* [版本系统与转换](05-version-system.md) — v1-v4版本差异、版本检测、递归逐步转换、v3↔v4映射、MIME类型映射、次版本演进。
* [验证体系](06-validation.md) — JSON Schema验证、双后端(fastjsonschema/jsonschema)、验证器缓存、normalize归一化、better_validation_error错误增强、未来版本兼容。

## 进阶篇

* [Notebook构造API](07-notebook-construction.md) — v4工厂函数详解：new_notebook/new_code_cell/new_markdown_cell/new_raw_cell/new_output/output_from_msg。
* [信任与签名](08-trust-and-signing.md) — HMAC签名算法、NotebookNotary门面类、SQLite/内存存储、信任判断规则、jupyter-trust CLI。
* [v4格式详解](09-v4-format.md) — v4.5 JSON格式完整规范：顶层结构、四种cell类型、四种output类型、MIME bundle、metadata、JSON Schema约束。
* [深入实战](10-advanced-patterns.md) — 动态导入import_item、Sentinel哨兵、深拷贝优化原理、自定义验证relax模式、遍历修改Notebook、常见陷阱。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-notebook-node
04-read-write-api
05-version-system
06-validation
07-notebook-construction
08-trust-and-signing
09-v4-format
10-advanced-patterns
```
