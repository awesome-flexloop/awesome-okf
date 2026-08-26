# 概念文档

本目录包含 github-problem-matcher 的 6 个核心概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门与基础

* [00-github-problem-matcher 简介](00-introduction.md) — GitHub Actions Problem Matcher 机制概述、Sphinx Problem Matcher 项目定位与核心价值。
* [01-5分钟快速上手](01-getting-started.md) — 在 GitHub Actions 中集成、最小配置、质量门禁配置、生产级 workflow 示例。
* [02-Action 结构解析](02-action-structure.md) — action.yml 逐行解析、composite action 机制、::add-matcher:: workflow 命令、GitHub 上下文变量。

## 核心机制

* [03-Problem Matcher JSON 格式](03-matcher-json.md) — problemMatcher/pattern/regexp 字段说明、捕获组映射机制、owner 命名、多行匹配。
* [04-三种正则模式详解](04-regex-patterns.md) — 严格模式、宽松模式、兜底模式的正则逐字符解析、覆盖场景、协作关系。
* [05-测试 Problem Matcher](05-testing.md) — test_matcher.js 逐行解析、零框架测试方法、如何为自定义 matcher 编写单元测试。

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-action-structure
03-matcher-json
04-regex-patterns
05-testing
```
