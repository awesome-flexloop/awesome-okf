---
type: Concept
title: "dh CLI 架构与分层"
description: "dh 的入口、Cobra 命令树、Factory 依赖注入、IOStreams 抽象、错误与退出码体系，对应 F-007~F-016"
tags: [dh, dolthub, cli, go, architecture, cobra]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-09" }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: dh-cli-source
    resource: /references/source.md
    title: "dh CLI 源码事实登记"
---

# dh CLI 架构与分层

> 本文档拆解 `dh` 的工程结构：入口、命令树、依赖注入、I/O 抽象、错误与退出码。对应 [F-007~F-016](/references/source.md)。

`dh` 的架构高度同构于 GitHub CLI（`gh`）——它是把成熟 Go CLI 工程范式迁移到数据领域的一个精简范本。理解其分层，即可掌握"如何用 Go 写一个可测试、可维护的现代 CLI"。

## 分层总览

```
cmd/dh/main.go         进程入口（os.Exit + 版本注入）
        │
internal/app/app.go    装配器：factory.New → root.NewCmdRoot → execute
        │
pkg/cmd/root/root.go   Cobra 命令树（14 个命令组）
        │
pkg/cmd/*              各命令实现（Options 结构 + 窄依赖注入）
        │
pkg/cmdutil/*          跨命令工具（错误/JSON 输出/数据库 flag/版本源）
pkg/iostreams/*        I/O 抽象（In/Out/ErrOut + TTY 检测）
        │
internal/*             领域层（dolthub 客户端、credentials、oauth、upload…）
```

## 入口与装配

入口极薄——`main.go` 只定义 `version`（默认 `"dev"`，编译期可注入）并委托给 `app.Main`（F-007）：

```go
func main() {
    os.Exit(app.Main(os.Args[1:], os.Stdin, os.Stdout, os.Stderr, version))
}
```

`app.Main` 包装为 `app.Run`，后者做三件事（F-009）：

1. `factory.New(version, streams)` 构造依赖工厂
2. `root.NewCmdRoot(f)` 构建命令树
3. `cmd.SetArgs(args)` 后 `execute` 执行

## 命令树

根命令在 `root.go` 中一次性 `AddCommand` 挂载 14 个命令组（F-011），每个命令组又是一个 Cobra 子命令（如 `auth` 下挂 `login`/`logout`/`status`）。

## 依赖注入：Factory

`Factory` 聚合了命令所需的全部能力（F-015），是"单一事实来源"的依赖容器：

```go
type Factory struct {
    AppVersion        string
    IO                *iostreams.IOStreams
    Config            func() (config.Config, error)
    Credentials       credentials.Store
    RefreshToken      credentials.RefreshFunc
    Authenticator     authflow.Authenticator
    Prompter          prompt.Prompter
    ResolveRepository func(context.Context, string) (repository.Repository, error)
    LookupEnv         func(string) (string, bool)
    APIClientForHost  func(string) (*dolthub.Client, error)
    Browser           browser.Browser
}
```

`factory.New` 用 `sync.Once` 惰性加载配置，并组装生产实现（FallbackStore 凭据、System prompter、BrowserAuthenticator、APIClientForHost、ResolveRepository）（F-016）。

**每个命令使用"窄依赖"而非直接持有 Factory**——命令定义自己的 `Options` 结构，只声明它需要的能力（如 `sql.Options` 持有 `ResolveRepository`、`APIClientForHost`）。这是可测试性的关键：测试可注入假依赖。

## I/O 抽象：IOStreams

`IOStreams` 封装 `In`/`Out`/`ErrOut` 三个流 + TTY 状态（F-012 附近的 F-012 实为错误类型，I/O 见源码 `iostreams.go`）。通过 `os.ModeCharDevice` 判断是否终端，`NewTest()` 提供 buffer 测试流。TTY 检测驱动两种输出形态：终端用 tabwriter 对齐表格，非终端用 tab 分隔（F-050）。

## 错误与退出码

错误类型分六类（F-012），`renderError` 按类型映射退出码（F-013）：

| 错误类型 | 语义 | 退出码 |
|----------|------|--------|
| `NoResultsError` | 成功但无结果 | 0 |
| `SilentError` | 已向用户呈现错误 | 1 |
| `FlagError` | 命令行用法错误 | 2（附 usage） |
| `CancelError` | 用户取消 | 2 |
| `AuthError` | 认证缺失/被拒 | 4（提示 `dh auth login`） |
| `ExternalCommandError` | 子进程失败 | 透传子进程退出码 |

`unknown command` 前缀的错误被 `execute` 统一转为 `FlagError`（F-014），保证"命令不存在"也走用法错误分支。

## 洞察：可测试性贯穿始终

`dh` 的工程价值在于"副作用可注入"——IO、网络客户端、时间、浏览器、环境变量都被抽象为可替换的窄接口。这是它能把 CLI 写出高单测覆盖（`_test.go` 文件遍布各包）的根因。对自建 CLI 而言，这条经验比任何具体代码都更可迁移。

## 相关概念

* [dh CLI 概述与安装](/concepts/00-overview.md)
* [认证与凭据管理](/concepts/02-authentication.md)
* [结构化输出与异步操作](/concepts/05-output-and-operations.md)
