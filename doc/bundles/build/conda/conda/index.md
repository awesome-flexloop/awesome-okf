---
okf_version: "0.2"
---

# Conda 知识库

本知识包是 Python 跨平台包与环境管理器 [Conda](https://conda.io/)（BSD-3-Clause 许可证）的系统化中文源码教程，基于 conda v26.7.1 源码深度阅读生成，覆盖从快速上手到插件开发的完整知识体系。所有内容均溯源至 Conda 源码（`conda/` 包核心模块），遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门篇（concepts/）

* [Conda 简介](concepts/00-introduction.md) — 包管理器+环境管理器+跨平台特性，核心能力概览，conda vs pip vs mamba 对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 安装 Conda、创建环境、安装包、导出环境、删除环境，含 Python API 快速体验。
* [架构总览](concepts/02-architecture-overview.md) — 七层分层架构（auxlib→base→common→models→core→gateways→cli/plugins），单向依赖规则。

## 核心数据模型篇（concepts/）

* [Channel 与 Subdir](concepts/03-channel-subdir.md) — URL 分解、from_value() 缓存、平台子目录、通道概念。
* [MatchSpec 包查询语言](concepts/04-matchspec.md) — 方括号语法、版本约束、merge 合并、CEP-26 包名校验，含语法速查表。
* [版本系统 VersionOrder](concepts/05-version-system.md) — 版本字符串解析、组件分割、版本比较算法、VersionSpec 约束匹配。
* [三级包记录模型](concepts/06-package-records.md) — PackageRecord→PackageCacheRecord→PrefixRecord 继承链、Entity 字段系统。

## 核心业务逻辑篇（concepts/）

* [Context 全局配置](concepts/07-context-configuration.md) — context 单例、condarc 配置、Configuration/ParameterLoader 框架。
* [Index 与 Repodata](concepts/08-index-and-repodata.md) — Index 聚合四类信息源、SubdirData 缓存、repodata.json 加载、pickle 缓存。
* [Solver 求解器与 SAT 算法](concepts/09-solver-and-resolve.md) — 依赖求解三方法、SAT 后端、Clauses 子句管理、插件委托模式。
* [事务与包链接](concepts/10-transaction-link.md) — UnlinkLinkTransaction、链接类型决策（hardlink→softlink→copy）、path_actions。
* [环境管理与 History](concepts/11-environments-history.md) — PrefixData、envs_manager、History 变更记录、PrefixGraph 拓扑排序。

## CLI 与 Shell 篇（concepts/）

* [CLI 命令体系](concepts/12-cli-commands.md) — 24 个内置命令、双入口模型、两阶段参数解析。
* [Shell 激活机制](concepts/13-shell-activation.md) — _Activator 抽象类、shell 脚本输出→eval 模型、conda init。
* [异常体系与错误处理](concepts/14-exceptions-and-errors.md) — CondaError 基类、CondaMultiError、信号处理、异常处理器。

## 高级扩展篇（concepts/）

* [插件系统](concepts/15-plugin-system.md) — pluggy 插件框架、19 种钩子类型、FORBIDDEN_HEADERS 安全边界。
* [网关层 I/O](concepts/16-gateways-io.md) — CondaSession 五协议适配器、磁盘操作、并行下载、subprocess 封装。
* [公开 Python API](concepts/17-public-api.md) — Solver/SubdirData/PackageCacheData/PrefixData 四个 API 类、_internal 委托模式。

## 实战示例（examples/）

* [程序化创建 Conda 环境](examples/basic-env-create.md) — 使用 Solver API 从 Python 代码创建环境并安装包。
* [MatchSpec 查询示例](examples/matchspec-queries.md) — 7 种 MatchSpec 构造方式与常见查询场景。
* [查询已安装包和包缓存](examples/query-installed-packages.md) — PrefixData/PackageCacheData/SubdirData 三级查询。
* [自定义求解器插件](examples/custom-solver-plugin.md) — 通过 pluggy 钩子注册自定义求解器后端。
* [虚拟包检测与使用](examples/virtual-packages.md) — 9 种内置虚拟包详解与自定义虚拟包插件。

## 信源登记簿（references/）

* [CLI 入口点](references/cli-main.md) — main.py 双入口模型源码。
* [Solver API](references/solver-init.md) — 高层求解器 API 源码片段。
* [SubdirData API](references/subdir-data-api.md) — 仓库元数据 API 源码片段。
* [插件 hookspec](references/plugin-hookspec.md) — Pluggy 钩子规范定义源码。

## 信任与生命周期说明

* **status 判定依据**：全部 27 个内容文档（18 个概念 + 5 个示例 + 4 个信源登记）均 `status: stable`。内容基于对 Conda v26.7.1 源码（`external/libs/conda-dev/conda/conda/` 目录）的逐模块阅读与事实提取（80 条源码事实 F-001~F-080），经 seven-concepts 方法论 R→I→E→V→C 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。Conda 核心架构（分层模型/Context单例/MatchSpec/Solver/Plugin）自 4.x 以来相对稳定，API 层（conda.api）虽标注 Beta 但接口契约变化不大；该日期作为针对未来大版本（如 27.x/28.x）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 27 个内容文档（18 个概念 + 5 个示例 + 4 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
