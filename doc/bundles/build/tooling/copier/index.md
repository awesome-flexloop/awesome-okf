---
okf_version: "0.2"
---

# Copier 知识库

本知识包是 Python 项目模板渲染库 [Copier](https://copier.readthedocs.io/) 的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到高级 API 集成的完整知识体系。Copier 是一个用于从模板创建项目并支持后续更新的库和 CLI 工具，核心特性包括 Jinja2 模板渲染、Git 版本管理、交互式问卷、条件任务、跨版本迁移和智能三向合并更新。所有内容均溯源至 Copier 源码（`external/libs/copier/` 包核心模块），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [Copier 简介](concepts/00-introduction.md) — 项目模板渲染库的设计哲学、安装方法、与 Cookiecutter/Cruft 的对比、核心优势。
* [5分钟快速上手](concepts/01-getting-started.md) — 创建第一个模板、编写 copier.yml、使用 `copier copy` 生成项目、理解 answers 文件。
* [模板配置文件](concepts/02-template-configuration.md) — copier.yml/copier.yaml 配置详解：配置项（`_` 前缀）、问题定义、排除规则、子目录、外部数据。
* [问题与答案系统](concepts/03-questions-and-answers.md) — Question 类详解、问题类型（str/int/bool/json/yaml/secret）、条件问题、AnswersMap 多源合并、交互式问卷流程。
* [Jinja2 模板渲染](concepts/04-jinja2-templating.md) — SandboxedEnvironment 沙箱安全模型、模板后缀、文件/路径/字符串渲染机制、yield 扩展多文件生成、自定义过滤器、渲染上下文变量。

## 配置与执行（concepts/）

* [Worker 与生命周期](concepts/05-worker-and-lifecycle.md) — Worker 类详解（23 个配置字段、上下文管理器）、run_copy/run_recopy/run_update 三种操作、Phase 执行阶段、模板渲染主循环。
* [VCS 集成与版本管理](concepts/06-vcs-integration.md) — Git 克隆/镜像缓存、URL 快捷方式（gh:/gl:）、PEP440 标签版本检测、dirty changes 处理、submodule 支持、Git index 模式。
* [任务与迁移](concepts/07-tasks-and-migrations.md) — Task 数据类、shell/argv 命令执行、条件任务、工作目录、迁移任务（before/after 两阶段）、版本比较逻辑、消息钩子。

## 高级主题（concepts/）

* [CLI 命令参考](concepts/08-cli-reference.md) — copier 主命令与 4 个子命令（copy/recopy/update/check-update）、所有选项详解、退出码、非交互模式、常用命令组合。
* [安全与信任机制](concepts/09-security-and-safety.md) — SandboxedEnvironment 沙箱、不安全特性检测（jinja_extensions/tasks/migrations）、信任机制（--trust）、ForbiddenPathError 路径越界保护、符号链接安全、secret 问题处理。
* [高级模式与 API 集成](concepts/10-advanced-patterns.md) — Python API（run_copy/run_update/Worker）、Phase 枚举、LazyDict 延迟字典、自定义 Jinja2 扩展、错误处理层次、文件权限跨平台同步、嵌入其他工具。

## 实战示例（examples/）

* [基础模板创建与使用](examples/basic-template.md) — 从零创建 Python 项目模板，配置 copier.yml、编写 Jinja2 模板文件、交互式/非交互式生成项目、使用远程 Git 模板的完整 walkthrough。
* [条件渲染与动态文件](examples/conditional-rendering.md) — `when` 条件问题、Jinja2 控制流条件内容、动态默认值联动、yield 标签从一个模板生成多个文件（含 yield 工作原理和限制说明）。
* [任务与自动化钩子](examples/tasks-and-hooks.md) — `_tasks` 任务执行（shell 字符串/argv 列表两种格式、条件任务、工作目录）、`_migrations` 版本迁移脚本（before/after 两阶段、版本比较逻辑）、前后消息配置、--skip-tasks 和 pretend 模式。
* [项目更新工作流](examples/update-workflow.md) — `copier update` 智能更新流程、冲突解决（inline/rej 两种模式、上下文行数控制）、迁移脚本编写、recopy vs update 对比、CI/CD 更新最佳实践。
* [Python API 使用](examples/python-api-usage.md) — run_copy/run_update/run_recopy 便捷函数、Worker 类精细控制（属性访问、模板信息检查）、错误处理（7 种异常类型）、构建自定义 CLI 工具、CI/CD 集成脚本、批量生成多个项目。

## 信源登记簿（references/）

* [Copier 源码信源登记](references/copier-source.md) — Copier 源码路径、版本（9.17.2）、核心模块清单与公开 API 导出列表、依赖说明。

## 信任与生命周期说明

* **status 判定依据**：全部 18 个内容文档（11 个概念 + 5 个示例 + 1 个信源登记 + 1 个信源索引）均 `status: stable`。内容基于对 Copier 源码（`external/libs/copier/copier/copier/` 目录，15 个核心模块）的逐模块阅读与事实提取，经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。Copier 9.x API 相对稳定，核心类（Worker/Template/Subproject/Question/Task）自 8.x 以来的架构变化主要集中在安全沙箱和 VCS 集成；该日期作为针对未来大版本升级（如 10.x）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-22）；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 17 个内容文档（11 个概念 + 5 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
