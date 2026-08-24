---
okf_version: "0.2"
---

# sphinxext-rediraffe 知识库

本知识包是 Sphinx 官方生态中的页面重定向扩展 [sphinxext-rediraffe](https://github.com/sphinx-doc/sphinxext-rediraffe) 的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到核心架构的完整知识体系。所有内容均溯源至 sphinxext-rediraffe 源码（单文件 `sphinxext/rediraffe.py`，485行核心代码），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [sphinxext-rediraffe 简介](concepts/00-introduction.md) — 什么是rediraffe、核心特性、安装方法、与其他重定向方案对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 3步完成配置：安装扩展、dict/文件配置重定向、构建验证。

## 核心架构（concepts/）

* [架构概览](concepts/02-architecture-overview.md) — 三大核心组件（图处理/构建钩子/Diff检查）、事件钩子机制、数据流总览、支持的构建器。
* [重定向图模型](concepts/03-redirect-graph.md) — 有向图建模、create_graph解析算法、create_simple_redirects链式压缩、循环检测、复杂度分析。
* [配置项详解](concepts/04-configuration.md) — 4个配置项（rediraffe_redirects/branch/template/auto_redirect_perc）完整参考。
* [Builder体系详解](concepts/05-builders.md) — html/dirhtml自动生成、rediraffecheckdiff变更检查、rediraffewritediff自动写入。
* [Jinja2模板系统](concepts/06-jinja-templates.md) — 默认模板三层降级策略、5个模板变量、自定义模板加载机制、URL参数保留原理。
* [路径处理与跨平台兼容](concepts/07-path-and-cross-platform.md) — Windows/POSIX路径标准化、dirhtml目录URL、增量构建JSON记录、冲突检测。

## 实战示例（examples/）

* [基础重定向配置](examples/basic-redirects.md) — dict方式和文件方式、链式重定向验证、嵌套目录、常见错误排查。
* [CI Diff检查集成](examples/diff-checker-ci.md) — GitHub Actions工作流、ReadTheDocs集成、本地验证方法、修复流程。
* [自动重定向写入](examples/auto-redirect-writer.md) — rediraffewritediff使用、相似度阈值选择、Git重命名检测、批量修复工作流。
* [自定义Jinja模板](examples/custom-jinja-template.md) — 品牌化页面、SEO优化、倒计时提示、三层降级最佳实践。

## 信源登记簿（references/）

* [sphinxext-rediraffe 源码信源登记](references/rediraffe-source.md) — 源码路径、版本0.3.0、核心模块清单、完整API导出列表、测试覆盖范围。

## 信任与生命周期说明

* **status 判定依据**：全部 13 个内容文档（8 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 sphinxext-rediraffe 源码（`external/libs/docs/sphinxext-rediraffe/sphinxext/rediraffe.py`，485行核心代码）的逐行阅读与事实提取，经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。sphinxext-rediraffe 核心架构稳定（单文件扩展、图论模型+build-finished钩子+Git diff Builder），主要API自0.x版本以来变化不大；该日期作为针对未来大版本升级的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-21），两者分离、可追溯。

本知识包共收录 13 个内容文档（8 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
log
```
