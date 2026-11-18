---
type: concept
title: Crate 架构：五个 crate 的职责与依赖方向
description: 拆解 wecom-cli 工作区的 crate 边界、Client/Builder、argv 调度、registry 缓存、输出路由与错误码体系。
tags: [wecom, wecom-cli, architecture]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# Crate 架构：五个 crate 的职责与依赖方向

wecom-cli 的工作区不大，但边界切得很清楚：错误、文件、传输、业务库、二进制各占一个 crate。这样的切法不是为了"看起来模块化"，而是为了让沙箱、协议与命令装配可以分别被单元测试和 e2e 覆盖。理解依赖方向，也就理解了为什么某些能力只能出现在 `wecom` 层，而不能下沉到 `wecom-cli`。

## 一、五个 crate 与依赖方向

工作区共 5 个 crate（见 F-001、F-002）。依赖关系可以概括为一条主链加两个旁支：

```text
wecom-cli ──> wecom ──> wecom-transport ──> wecom-error
    │           └────> wecom-fs ───────────> wecom-error
    └──────────────> wecom-transport / wecom-fs / wecom-error
```

| crate | 类型 | 主要职责 | 依赖 |
|---|---|---|---|
| `wecom-error` | 库 | 工作区错误码分配表、共享错误码与统一错误类型 | 仅 `serde_json` |
| `wecom-fs` | 库 | 沙箱根解析、路径检查、文件读写与临时文件 | `wecom-error`、`tokio` |
| `wecom-transport` | 库 | HTTP 后端、信封、分页、轮询、断点续传、trace 头 | `wecom-error`、`reqwest` |
| `wecom` | 库 | 发现、schema、clap 装配、鉴权、业务编排与输出 | `wecom-error`、`wecom-fs`、`wecom-transport` |
| `wecom-cli` | 二进制 | 参数入口、`auth`/`cache`/`schema` 命令、日志与错误映射 | `wecom`、`wecom-fs`、`wecom-transport`、`wecom-error` |

`wecom-error` 只依赖 `serde_json`，这使它成为整棵依赖树的叶子，也避免了"错误类型反向依赖业务"的环形结构。`wecom-cli` 虽然直接依赖传输与文件 crate，但那是为了装配 `Client` 和注册元命令，业务调用本身仍收敛在 `wecom`。

## 二、`wecom`：Client 与 Builder

`Client` 是对外唯一入口（见 F-061），通过 `Client::builder()` 构造，由 `ClientBuilder::build` 完成装配（见 F-066、F-067）。Builder 负责端点目录与传输后端：`EndpointCatalog` 只保存内建端点的覆盖项，未覆盖的键回落到 `CatalogKey::builtin_default`（见 F-061）；需要覆盖内建端点时由 `custom-endpoint` 特性开放（见 F-007）。`Client::run(argv)` 返回 `CliRun`，再由 `CliRun::execute` 完成"发现 → 方法 → 调用"的编排（见 F-041、F-061）。

Builder 还会接收两类外部依赖：文件系统根（见 F-129）与传输后端。文件系统根一旦注入，所有涉及读写的参数都要经过沙箱校验，这也是为什么"文件类参数"的错误常常来自 `wecom` 而不是具体业务模块。Builder 的默认值由工作区特性控制，例如默认启用调用链遥测（见 F-136 的反向说明）。

`wecom` 内部的处理链是固定的五段：发现并缓存 schema（见 F-073）；按 schema 装配命令（见 F-037、F-044）；解析 argv 得到调用参数（见 F-050）；交由服务执行器查找方法并发起请求（见 F-056）；最后按输出模式渲染（见 F-074、F-075）。这条链的任何一段失败，都会被映射为带码错误并交给二进制决定退出状态。

## 三、argv 调度：二进制的全部职责

`wecom-cli` 的入口只做四件事：注册根命令（见 F-034）、处理首参归一（见 F-041）、拦截 `--version`（见 F-042）、决定是否跳过发现（见 F-043）。真正的 schema 装配发生在 `wecom` 内，二进制只负责把 argv 交给库并接收渲染结果。

这种"薄入口"设计带来一个可测试性优势：大部分命令行为可以在 `wecom` 的测试里以库调用方式验证，而不必启动进程。代价是二进制层的内建命令（`auth`、`cache`、`schema`）自成一套流程，需要单独覆盖——它们也确实位于 `wecom-cli/src/cmd/` 下，而不是 `wecom` 的服务目录。

## 四、registry 缓存：内存 + 磁盘两层，共用 60 秒 TTL

schema 的获取集中在 `wecom::registry`，TTL 固定为 60 秒，内存缓存与文件缓存共用同一常量（见 F-068）。缓存键是服务标识，缓存的是 discovery 返回的 catalog / detail 结构，而不是整棵 clap 树：

| 组件 | 作用 | 证据 |
|---|---|---|
| 缓存文件命名 | 服务名为空用 `catalog.json`，否则 `service_{服务名}.json`；服务名先经 `sanitize_filename`，路径前缀为 `client.cache_dir()` | F-070 |
| 新鲜度判定 | `modified.elapsed() >= CACHE_TTL` 即视为过期，向 `EndpointKey::ServiceDiscovery` 重新拉取 | F-069、F-072 |
| 原子写入 | 调用 `fs.atomic_write(..., Some(0o644))`，写入失败只记 `tracing::info`，不中断主流程 | F-071 |
| 对外入口 | `ServiceCache::get_or_fetch_catalog` 与 `get_or_fetch_detail`，各自带内存缓存与文件缓存 | F-073 |

60 秒的选择是一种折中：短到足以在服务端迭代后自动跟上，长到能让一次会话内的重复调用共享结果。缓存落在 `client.cache_dir()` 下，意味着同一台机器上的不同进程也能复用上一次的 discovery 结果，而不必每次重新发现；`cache status` / `cache clear` 两个内建命令正是为这层磁盘缓存准备的（见 F-052）。

## 五、输出路由：stdout 只放结果

输出层遵循一条硬规则：**stdout 只写业务结果，stderr 只写日志与诊断**。方法结果以紧凑 JSON 打印；分页模式输出 NDJSON（见 F-074）；`--output` 则把结果写入文件并返回文件元信息（见 F-075）。这使 Agent 可以安全地 `| jq` 或逐行读取，而不必过滤进度条。

`--dry-run` 只做装配与校验、不发起写请求，是排查参数问题的首选（见 F-051）。它与 `--doc`/`--schema` 的区别在于：后者跳过业务调用但仍可能需要网络拉取 schema，前者已经完成了 schema 装配。

## 六、错误码与退出码

错误码空间是 `893000–893999`，按 crate 划分子段，互不重叠（见源码 `crates/wecom-error/src/codes.rs`）：

| 子段 | 归属 | 说明 |
|---|---|---|
| `893000–893099` | `wecom` | 业务、校验、文件、权限等共享码 |
| `893100–893199` | `wecom-transport` | 网络、协议、轮询类错误 |
| `893200–893299` | `wecom-cli` | 入口、命令装配与本地配置错误 |
| `893400–893499` | 预留（Bot） | 尚未使用 |
| `893500–893599` | 预留（Subagent） | 尚未使用 |
| `893999` | 工作区 | 兜底码 |

共享码包括校验失败 `893001`、I/O 失败 `893003`、Builder 配置失败 `893005`、沙箱权限拒绝 `893006`。命令装配失败使用 `10021`（见 F-045），属于装配阶段的专用码。进程退出码只有 0/1/2 三档（见 F-172），业务错误会以结构化信封写到 stdout，因此"退出码 1 + 合法 JSON"是预期组合，而不是崩溃信号。

## 七、延伸阅读

- 命令如何走到这里：[/concepts/01-command-model.md](/concepts/01-command-model.md)
- 鉴权与 Client 的交互：[/concepts/03-auth-session.md](/concepts/03-auth-session.md)
- 传输层的协议细节：[/concepts/04-transport-resilience.md](/concepts/04-transport-resilience.md)
- 沙箱如何介入文件参数：[/concepts/05-sandbox-security.md](/concepts/05-sandbox-security.md)