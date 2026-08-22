# 概念文档

本目录包含 Copier 的 11 个核心概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门与基础

* [00-Copier 简介](00-introduction.md) — 项目模板渲染库的设计哲学、安装方法、与 Cookiecutter/Cruft 的对比。
* [01-5分钟快速上手](01-getting-started.md) — 创建第一个模板、编写 copier.yml、使用 copier copy 生成项目、理解 answers 文件。
* [02-模板配置文件](02-template-configuration.md) — copier.yml 配置详解：配置项（`_` 前缀）、问题定义、排除规则、子目录、外部数据。
* [03-问题与答案系统](03-questions-and-answers.md) — Question 类、问题类型（str/int/bool/json/yaml/secret）、条件问题、AnswersMap 多源合并、交互式问卷流程。
* [04-Jinja2 模板渲染](04-jinja2-templating.md) — SandboxedEnvironment 沙箱、模板后缀、文件/路径/字符串渲染、yield 扩展、自定义过滤器、渲染上下文变量。

## 核心机制

* [05-Worker 与生命周期](05-worker-and-lifecycle.md) — Worker 类详解、run_copy/run_recopy/run_update 三种操作、Phase 执行阶段、模板渲染主循环、任务执行、安全检查。
* [06-VCS 集成与版本管理](06-vcs-integration.md) — Git 集成、URL 快捷方式（gh:/gl:）、镜像缓存机制、标签版本检测（PEP440）、dirty changes 处理、submodule 支持、Git index 模式。
* [07-任务与迁移](07-tasks-and-migrations.md) — Task 数据类、shell/argv 命令执行、条件任务、工作目录、迁移任务（before/after）、版本比较逻辑、消息钩子。

## CLI 与安全

* [08-CLI 命令参考](08-cli-reference.md) — copier 主命令与 4 个子命令（copy/recopy/update/check-update）、所有选项详解、退出码、非交互模式、常用命令组合。
* [09-安全与信任机制](09-security-and-safety.md) — 沙箱环境、不安全特性检测（jinja_extensions/tasks/migrations）、信任机制（--trust）、ForbiddenPathError 路径越界保护、符号链接安全、secret 问题。

## 高级主题

* [10-高级模式与 API 集成](10-advanced-patterns.md) — Python API（run_copy/run_update/Worker）、Phase 枚举、LazyDict 延迟字典、自定义 Jinja2 扩展、错误处理层次、文件权限跨平台同步、嵌入其他工具。
