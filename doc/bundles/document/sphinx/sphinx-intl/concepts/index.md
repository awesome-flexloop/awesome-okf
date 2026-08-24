# 概念文档（concepts/）

本目录包含 9 篇从入门到进阶的 sphinx-intl 概念文档，按学习路径分为三篇。

## 入门篇（00-02）

* [00. sphinx-intl 简介](00-introduction.md) — sphinx-intl 是什么、核心能力、项目信息、代码结构、在 Sphinx i18n 工作流中的位置。
* [01. 5分钟快速上手](01-getting-started.md) — 安装、conf.py 配置、make gettext、sphinx-intl update/build/stat、环境变量配置。
* [02. CLI 命令体系详解](02-cli-commands.md) — Click 命令组架构、6 个子命令、选项体系、配置自动检测、default_map 注入机制。

## 核心篇（03-06）

* [03. 翻译工作流原理](03-translation-workflow.md) — POT/PO/MO 三文件类型、LC_MESSAGES 目录约定、文件路径映射规则、完整生命周期。
* [04. 目录文件操作：Catalog 模块](04-catalog-operations.md) — catalog.py 对 Babel 的封装、两阶段 charset 探测、条目过滤函数、update_with_fuzzy 合并。
* [05. 更新机制：多进程合并与 Fuzzy](05-update-mechanism.md) — UpdateItem/UpdateResult 数据类、multiprocessing.Pool 并行架构、_update_single_file 逻辑、fuzzy 标记处理。
* [06. 编译与统计机制](06-build-stat-mechanism.md) — MO 增量编译（mtime 判断）、translated/fuzzy/untranslated 三类统计、语言目录自动发现。

## 高级篇（07-08）

* [07. Transifex 平台集成](07-transifex-integration.md) — Transifex CLI 检测、资源名规范化、tx config 自动配置、云端协作工作流。
* [08. 配置读取与 Python 兼容层](08-config-and-compat.md) — read_config 执行 conf.py、Tags 类、execfile_ Python 2/3 兼容、自动配置检测流程。

```{toctree}
:hidden:

00-introduction
01-getting-started
02-cli-commands
03-translation-workflow
04-catalog-operations
05-update-mechanism
06-build-stat-mechanism
07-transifex-integration
08-config-and-compat
```
