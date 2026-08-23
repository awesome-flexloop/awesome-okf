---
okf_version: "0.2"
type: index
title: Conda 源码信源参考
sources:
  - conda/
---

# 信源登记簿

本目录登记本知识包所有内容据以派生的 Conda 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。

* [CLI 入口点 (main.py)](cli-main.md) — Conda CLI 双入口模型：`main()` 分发函数、`main_subshell()` 子命令入口、`main_sourced()` shell 激活入口，展示 conda 如何区分普通子命令与 `shell.` 前缀的激活命令。
* [Solver 求解器 API](solver-init.md) — Conda 高层求解 API：`Solver` 类的 `__init__` 构造函数及三个公开方法 `solve_final_state()`、`solve_for_diff()`、`solve_for_transaction()`，通过插件后端委托模式实现求解器可插拔。
* [SubdirData 仓库数据 API](subdir-data-api.md) — Conda 仓库元数据管理 API：`SubdirData` 类封装 repodata.json 的加载、查询与缓存，提供单频道查询 `query()`、跨频道查询 `query_all()`、记录遍历 `iter_records()` 和数据重载 `reload()` 方法。
* [插件钩子规范 (hookspec)](plugin-hookspec.md) — Conda 插件系统的 Pluggy hookspec 定义：`CondaSpecs` 类声明所有插件扩展点，包括 `conda_solvers`（求解器注册）和 `conda_subcommands`（子命令注册）等钩子，以及 `_hookspec`/`hookimpl` 装饰器标记。
