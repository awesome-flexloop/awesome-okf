---
okf_version: "0.2"
---

# Invocations 知识库

本知识包是 [Invocations](https://invocations.readthedocs.io/)（PyInvoke 的官方最佳实践任务集合库）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到高级组合的完整知识体系。所有内容均溯源至 Invocations v4.1.0 源码（`external/libs/pyinvoke/invocations/` 目录），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [Invocations 简介](concepts/00-introduction.md) — 库定位、设计哲学（模块化乐高积木）、与 PyInvoke 的关系、14 个核心模块概览。
* [快速上手](concepts/01-getting-started.md) — 安装方法、最小 tasks.py 示例、配置覆盖、`inv --list` 查看任务。

## 代码质量与测试（concepts/）

* [代码检查与格式化](concepts/02-checks-formatting.md) — `blacken`（Black 格式化）和 `lint`（flake8）任务详解、参数配置、CI 集成。
* [测试与覆盖率](concepts/03-testing-pytest.md) — `pytest` 模块（test/integration/coverage）、`testing` 模块旧版支持、`watch_tests` 监控。

## 文档与发布（concepts/）

* [Sphinx 文档管理](concepts/04-docs-sphinx.md) — build/clean/browse/doctest/tree 任务、多站点支持（sites/docs + sites/www）、`watch_docs` 自动重建、`_site()` 工厂函数。
* [包发布生命周期](concepts/05-packaging-release.md) — `packaging.release` 五阶段流程（status/prepare/build/publish/push）、版本号管理、changelog 维护、防御链设计（twine check → test_install → upload）。

## 运维与工具（concepts/）

* [CI 自动化](concepts/06-ci-automation.md) — `make_sudouser`/`sudo_run`/`make_sudouser_nopasswd` 等 CI 环境任务、SSH 免密配置。
* [工具函数与文件监控](concepts/07-utilities-watchers.md) — `console.confirm`/`util.tmpdir`/`environment.in_ci` 工具函数、`watch` 模块（`make_handler`/`observe`/`watch`）的文件监控模式。
* [依赖内嵌 vendorize](concepts/08-vendorize.md) — `vendorize` 任务原理与用法、将第三方依赖内嵌到项目 vendor 包。

## 扩展与组合（concepts/）

* [Sphinx Autodoc 扩展](concepts/09-autodoc-sphinx.md) — `autodoc` 模块为 Sphinx 自动文档化 Invoke Task、`TaskDocumenter` 工作原理、conf.py 配置方法。
* [组合模式：组装任务集合](concepts/10-composition-patterns.md) — 三种导入方式、配置覆盖优先级、跨 Collection 任务调用、创建自定义子集合、命名空间冲突处理、典型组合范例。

## 实战示例（examples/）

* [基础使用：在自己项目中引入 Invocations](examples/basic-usage.md) — 从零配置 tasks.py，含测试、格式化、文档、发布的完整项目模板。
* [自定义发布流程](examples/custom-release-flow.md) — 在标准 release 基础上添加前置检查、Docker 构建、发布后通知。
* [多站点文档构建配置](examples/multi-site-docs.md) — 配置 docs 模块管理 API 文档 + 主网站双站点，含 watch_docs 监控。
* [文件监控自动测试](examples/file-watch-auto-test.md) — 实现代码变化自动运行测试，多任务监控（源码→测试、文档→构建）。
* [打包安装验证模式](examples/test-install-verification.md) — 使用 `test_install` 在临时 venv 中验证安装、导入、类型检查，自定义增强验证。

## 信源登记簿（references/）

* [Invocations v4.1.0 源码信源登记](references/invocations-source.md) — 源码路径、版本信息、14 个核心模块清单、公开 API 导出列表。

## 信任与生命周期说明

* **status 判定依据**：全部 17 个内容文档（11 个概念 + 5 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 Invocations v4.1.0 源码（`external/libs/pyinvoke/invocations/invocations/` 目录）的逐模块阅读与事实提取（64 源码事实），经 seven-concepts 方法论 R→I→E→A→V 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。Invocations v4.x API 相对稳定，核心模块（checks/pytest/docs/packaging/ci/watch）自 2.x/3.x 以来接口变化较小；该日期作为针对未来大版本升级（如 PyInvoke 3.x 适配导致的 breaking changes）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-21），两者分离、可追溯。

本知识包共收录 17 个内容文档（11 个概念 + 5 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
