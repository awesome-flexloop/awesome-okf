---
okf_version: "0.2"
---

# GitHub Problem Matcher 知识库

本知识包是 GitHub Action [sphinx-doc/github-problem-matcher](https://github.com/sphinx-doc/github-problem-matcher) 的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到自定义 Matcher 的完整知识体系。所有内容均溯源至项目源码（`action.yml`、`sphinx_matcher.json`、`test_matcher.js`），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [github-problem-matcher 简介](concepts/00-introduction.md) — GitHub Actions Problem Matcher 机制、项目定位、核心价值与适用场景。
* [5分钟快速上手](concepts/01-getting-started.md) — 最小 workflow 配置、关键注意事项、质量门禁配置。
* [Action 结构解析](concepts/02-action-structure.md) — action.yml 逐行解析、composite action、`::add-matcher::` 命令与上下文变量。

## 核心机制（concepts/）

* [Problem Matcher JSON 格式](concepts/03-matcher-json.md) — problemMatcher/pattern 对象结构、regexp 正则、捕获组映射字段（file/line/severity/message）。
* [三种正则模式详解](concepts/04-regex-patterns.md) — 严格模式、宽松模式、兜底模式的正则逐字符解析与覆盖场景分析。
* [测试 Problem Matcher](concepts/05-testing.md) — test_matcher.js 逐行解析、零框架单元测试方法与自定义 matcher 测试模板。

## 实战示例（examples/）

* [基础使用示例](examples/basic-usage.md) — 最简/生产级/多版本矩阵 workflow、MyST 兼容、条件启用、常见问题排查。
* [自定义 Problem Matcher](examples/custom-matcher.md) — 为 pylint/ruff/eslint/pytest 创建自定义 matcher 的完整教程与模板。

## 信源登记簿（references/）

* [github-problem-matcher 源码信源登记](references/github-problem-matcher-source.md) — 项目基本信息、核心文件清单、action.yml/sphinx_matcher.json/test_matcher.js 结构解析。

## 信任与生命周期说明

* **status 判定依据**：全部 9 个内容文档（6 个概念 + 2 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 github-problem-matcher 源码（`external/libs/docs/github-problem-matcher/` 目录）的逐文件阅读与事实提取（39 条源码事实），经 seven-concepts 方法论 R→I→E→V→C 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。github-problem-matcher 核心功能极为稳定（一行 echo 命令 + 3 条正则），自 2020 年创建以来无重大 API 变更；该日期作为针对 GitHub Actions workflow 命令语法或 Sphinx 输出格式重大变化的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-21），两者分离、可追溯。

本知识包共收录 9 个内容文档（6 个概念 + 2 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
