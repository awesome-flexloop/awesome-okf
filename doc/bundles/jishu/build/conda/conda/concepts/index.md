# 概念文档

本目录包含 Conda 的 18 个核心概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门篇

* [00-Conda 简介](00-introduction.md) — Conda 是什么（包管理器+环境管理器+跨平台），BSD 许可证，版本 26.7.1，核心能力概览，conda vs pip vs mamba 对比。
* [01-5分钟快速上手](01-getting-started.md) — 安装 Conda、创建环境、安装包、导出环境、删除环境，含命令行和 Python API 快速体验。
* [02-架构总览](02-architecture-overview.md) — 七层分层架构（auxlib→base→common→models→core→gateways→cli/plugins），单向依赖规则，启动流程调用链。

## 核心数据模型篇

* [03-Channel 与 Subdir](03-channel-subdir.md) — Channel 类的 URL 分解、from_value() 缓存、Subdir 平台子目录、defaults/conda-forge 通道概念。
* [04-MatchSpec 包查询语言](04-matchspec.md) — MatchSpec 语法解析、V3 方括号语法、版本约束、MatchSpec.merge() 合并、CEP-26 包名校验，含语法速查表。
* [05-版本系统 VersionOrder](05-version-system.md) — 版本字符串解析规则、组件分割算法、版本比较、VersionSpec 约束匹配、BuildNumberMatch。
* [06-三级包记录模型](06-package-records.md) — PackageRecord→PackageCacheRecord→PrefixRecord 继承链，Entity 字段系统，Link 实体，NoarchType/PackageType 枚举。

## 核心业务逻辑篇

* [07-Context 全局配置](07-context-configuration.md) — context 单例、condarc 配置文件搜索路径、Configuration/ParameterLoader 框架、参数类型体系、frozendict 不可变配置。
* [08-Index 与 Repodata](08-index-and-repodata.md) — Index 聚合四类信息源、SubdirDataType 元类缓存、repodata.json 加载、pickle 缓存机制、PackageRecordList 懒转换。
* [09-Solver 求解器与 SAT 算法](09-solver-and-resolve.md) — BaseSolver 三方法、SAT 后端选择（PycoSat/PyCryptoSat/PySat）、Clauses 子句管理（Tseitin 转换）、DepsModifier/UpdateModifier 枚举、插件后端委托模式。
* [10-事务与包链接](10-transaction-link.md) — UnlinkLinkTransaction 事务、determine_link_type() 决策（hardlink→softlink→copy）、path_actions 操作集合、LinkType 枚举。
* [11-环境管理与 History](11-environments-history.md) — PrefixData 管理 conda-meta/、envs_manager 环境注册、History 类记录变更历史、PrefixGraph 拓扑排序。

## CLI 与 Shell 篇

* [12-CLI 命令体系](12-cli-commands.md) — 24 个内置命令、双入口模型（main_subshell vs main_sourced）、两阶段参数解析、do_call() 分发、-V 快速路径。
* [13-Shell 激活机制](13-shell-activation.md) — _Activator 抽象基类、shell 脚本输出→eval 模型、conda init 钩子安装、Windows 行尾修复、栈式环境激活。
* [14-异常体系与错误处理](14-exceptions-and-errors.md) — CondaError 基类、CondaMultiError 批量异常、CondaExitZero 正常退出、CondaSignalInterrupt 信号处理、printf 风格消息格式化。

## 高级扩展篇

* [15-插件系统](15-plugin-system.md) — CondaPluginManager（pluggy）、19 种钩子类型、FORBIDDEN_HEADERS 安全边界、内置插件目录结构、求解器可插拔。
* [16-网关层 I/O](16-gateways-io.md) — CondaSession 五协议适配器、disk/ 磁盘操作、并行下载、repodata 缓存管理、subprocess 子进程封装。
* [17-公开 Python API](17-public-api.md) — Solver/SubdirData/PackageCacheData/PrefixData 四个 API 类、_internal 委托模式、reload() 强制刷新、Beta API 声明。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-channel-subdir
04-matchspec
05-version-system
06-package-records
07-context-configuration
08-index-and-repodata
09-solver-and-resolve
10-transaction-link
11-environments-history
12-cli-commands
13-shell-activation
14-exceptions-and-errors
15-plugin-system
16-gateways-io
17-public-api
```
