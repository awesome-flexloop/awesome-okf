# 概念文档

本目录包含 Invocations 的 11 个核心概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门与基础

* [00-Invocations 简介](00-introduction.md) — Invocations 是什么、设计哲学、与 PyInvoke 的关系、核心模块一览。
* [01-快速上手](01-getting-started.md) — 安装、最小示例（组合 checks/docs/pytest 任务）、配置覆盖、查看任务列表。

## 代码质量与测试

* [02-代码检查与格式化](02-checks-formatting.md) — blacken（Black 格式化）和 lint（flake8）任务、配置参数、与 pre-commit 集成。
* [03-测试与覆盖率](03-testing-pytest.md) — pytest 模块（test/integration/coverage）、testing 模块旧版支持、watch_tests 监控。

## 文档与发布

* [04-Sphinx 文档管理](04-docs-sphinx.md) — build/clean/browse/doctest/tree 任务、多站点支持（sites/docs + sites/www）、watch_docs 自动重建。
* [05-包发布生命周期](05-packaging-release.md) — release 模块五阶段流程（status/prepare/build/publish/push）、版本检查、changelog 管理、防御链设计。

## 运维与工具

* [06-CI 自动化](06-ci-automation.md) — make_sudouser/sudo_run/make_sudouser_nopasswd 等 CI 环境任务、SSH 免密配置。
* [07-工具函数与文件监控](07-utilities-watchers.md) — confirm/tmpdir/in_ci 等工具函数、watch 模块（make_handler/observe/watch）的文件监控模式。
* [08-依赖内嵌 vendorize](08-vendorize.md) — vendorize 任务原理与用法、将第三方依赖内嵌到项目 vendor 包中。

## 扩展与组合

* [09-Sphinx Autodoc 扩展](09-autodoc-sphinx.md) — autodoc 模块为 Sphinx 自动文档化 Invoke Task、TaskDocumenter 原理、配置方法。
* [10-组合模式：组装任务集合](10-composition-patterns.md) — 三种导入方式、配置覆盖模式、跨 Collection 调用、创建自定义子集合、命名技巧。

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-checks-formatting
03-testing-pytest
04-docs-sphinx
05-packaging-release
06-ci-automation
07-utilities-watchers
08-vendorize
09-autodoc-sphinx
10-composition-patterns
```
