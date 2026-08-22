---
okf_version: "0.2"
---

# Copier Bundle 变更日志

本文件记录 Copier 知识库的内容变更历史。

## v0.1.0 (2026-08-22)

### 新增（Initial Release）

**目录结构**：
- 创建 `concepts/`、`examples/`、`references/` 三级目录结构。

**信源登记簿（references/）**：
- `copier-source.md`：Copier 源码信源登记，版本 9.17.2，Python ≥3.10，核心模块 15 个，公开 API 导出 50+。
- `index.md`：references 目录索引。

**概念文档（concepts/，共 11 篇）**：
- `00-introduction.md`：Copier 简介、安装、对比 Cookiecutter/Cruft。
- `01-getting-started.md`：5 分钟快速上手 walkthrough。
- `02-template-configuration.md`：copier.yml 配置文件全解析。
- `03-questions-and-answers.md`：问题定义、类型、条件、答案合并。
- `04-jinja2-templating.md`：Jinja2 沙箱、渲染、yield 扩展、过滤器。
- `05-worker-and-lifecycle.md`：Worker 类、Phase 阶段、渲染主循环。
- `06-vcs-integration.md`：Git 集成、镜像缓存、版本检测、submodule。
- `07-tasks-and-migrations.md`：任务执行、迁移脚本、命令格式、条件执行。
- `08-cli-reference.md`：CLI 命令、选项、退出码、常用组合。
- `09-security-and-safety.md`：沙箱安全、不安全特性、信任机制、路径保护。
- `10-advanced-patterns.md`：Python API、自定义扩展、错误体系、嵌入使用。
- `index.md`：concepts 目录索引。

**示例文档（examples/，共 5 篇）**：
- `basic-template.md`：基础模板创建与使用（含完整模板代码示例）。
- `conditional-rendering.md`：条件渲染与动态文件（when、yield、动态默认值）。
- `tasks-and-hooks.md`：任务与自动化钩子（shell/argv 命令、迁移脚本）。
- `update-workflow.md`：项目更新工作流（update/recopy、冲突处理、最佳实践）。
- `python-api-usage.md`：Python API 使用（便捷函数、Worker、错误处理、CI 集成、批量生成）。
- `index.md`：examples 目录索引。

**顶层文件**：
- `index.md`：Copier 知识库首页与导航。
- `log.md`：本变更日志文件。

### 信源依据

所有内容基于对以下源码文件的逐模块阅读与事实提取：
- `copier/copier/_main.py`（Worker 类、run_copy/run_update/run_recopy）
- `copier/copier/_template.py`（Template 类、Task 数据类、VCS 处理）
- `copier/copier/_subproject.py`（Subproject 类、AnswersMap）
- `copier/copier/_user_data.py`（Question 类、答案加载）
- `copier/copier/_cli.py`（CLI 命令定义与选项）
- `copier/copier/_jinja_ext.py`（Jinja2 扩展、YieldExtension、Ansible 过滤器）
- `copier/copier/_vcs.py`（VCS 抽象、Git 实现、镜像缓存）
- `copier/copier/_settings.py`（默认配置常量）
- `copier/copier/errors.py`（错误体系）
- `copier/pyproject.toml`（版本与依赖信息）
