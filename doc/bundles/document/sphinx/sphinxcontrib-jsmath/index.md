---
okf_version: "0.2"
---

# sphinxcontrib-jsmath 知识库

本知识包是 Sphinx 官方扩展 [sphinxcontrib-jsmath](https://github.com/sphinx-doc/sphinxcontrib-jsmath) 的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到扩展机制理解的完整知识体系。所有内容均溯源至项目源码（核心模块仅 88 行 `__init__.py`），遵循 [OKF v0.2 规范](https://github.com/xinetzone/awesome-okf-xs)。

## 入门与基础（concepts/）

* [sphinxcontrib-jsmath 简介](concepts/00-introduction.md) — 什么是 jsMath 渲染器、项目定位、与 MathJax/imgmath 等方案的对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 安装、conf.py 最小配置、编写数学公式、构建 HTML 文档。

## 核心机制（concepts/）

* [扩展注册与 setup 函数](concepts/02-setup-and-registration.md) — setup 函数 6 个注册动作逐行解析、add_html_math_renderer API 详解。
* [数学节点访问者](concepts/03-math-node-visitors.md) — docutils Visitor 模式、html_visit_math/displaymath 逐行解析、SkipNode 流控制。
* [智能JS加载机制](concepts/04-smart-js-loading.md) — install_jsmath 三重条件检查、env-updated 事件时机、按需资源加载模式。
* [国际化与并行安全](concepts/05-i18n-and-parallel.md) — gettext 消息目录、parallel_read/write_safe、mypy 严格类型。

## 实战示例（examples/）

* [基础使用示例](examples/basic-usage.md) — 从零搭建项目、编写行内/块级/多行公式、验证 HTML 输出。
* [公式编号与引用](examples/equation-numbering.md) — 自动编号、numfig 章节编号、eq/numref 交叉引用。
* [常见问题排查](examples/troubleshooting.md) — ExtensionError、JS不加载、MathJax冲突、增量构建异常。

## 信源登记簿（references/）

* [sphinxcontrib-jsmath 源码信源登记](references/jsmath-source.md) — 项目基本信息、核心文件清单、API 注册表、HTML 输出结构、测试覆盖。

## 信任与生命周期说明

* **status 判定依据**：全部 10 个内容文档（6 个概念 + 3 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 sphinxcontrib-jsmath 源码（`external/libs/docs/sphinxcontrib-jsmath/` 目录）的逐文件阅读与事实提取，经 seven-concepts 方法论 R→I→E→V→C 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。sphinxcontrib-jsmath 核心功能极为稳定（88 行代码、自 2019 年从 Sphinx 核心拆分以来无重大 API 变更），仅需在 Sphinx math renderer API 发生不兼容变更时重新评估。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-21），两者分离、可追溯。

本知识包共收录 10 个内容文档（6 个概念 + 3 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
