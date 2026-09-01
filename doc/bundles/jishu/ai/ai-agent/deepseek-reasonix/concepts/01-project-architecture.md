---
type: Concept
title: 项目架构
description: Reasonix 整体架构——cmd 入口、internal 包分层、boot 启动组装流程、前端共享 Controller
tags: [deepseek-reasonix, architecture, boot, packages, layering]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /references/source.md
    title: DeepSeek-Reasonix 源码信源索引
---

## 整体架构

Reasonix 采用严格的 Go 包分层架构。核心原则是：一个 transport-agnostic 的 `control.Controller` 位于所有前端之后，所有行为添加到 Controller 而非前端，使 CLI、桌面、浏览器、ACP 四种前端继承相同功能。（F-009）

## 目录结构

```
reasonix/
├── cmd/
│   └── reasonix/main.go       # CLI 入口
├── internal/
│   ├── agent/                 # Agent 核心：运行循环、会话、调度、仲裁
│   ├── acp/                   # ACP 协议适配层
│   ├── bot/                   # Bot 网关：QQ/飞书/微信/钉钉
│   ├── cli/                   # CLI 命令和 TUI
│   ├── boot/                  # 配置→Controller 组装
│   ├── checkpoint/            # 检查点、blob 存储、回滚
│   ├── control/               # 前端共享 Controller
│   ├── provider/              # LLM provider 抽象
│   ├── tool/                  # 工具注册和内置工具
│   ├── config/                # 配置加载
│   ├── event/                 # 类型化事件流
│   └── ...                    # 其他 utility 包
├── desktop/                   # Wails v2 桌面应用
├── docs/                      # 文档
├── go.mod
├── Makefile
└── README.md
```

## 分层规则

REASONIX.md 明确强制执行以下分层（F-009）：

- **Utility 包**：不导入 `reasonix/` 下任何包
- **前端层**：`cli`、`serve`、`acp`、`bot`、`botruntime`、`boot` 和 hosts（`cmd/`、`desktop/`）可导入 `control`
- **下层包**：不能导入前端层包
- 声明的集合存在于 `tools/repolint/layers.go`

## cmd 入口

`cmd/reasonix/main.go` 是唯一的 CLI 入口点：

```go
var runCLI = func(args []string, buildVersion string) int {
    return cli.RunWithBuildInfo(args, cli.BuildInfo{
        Version:      buildVersion,
        GitCommit:    gitCommit,
        BuildTimeUTC: buildTimeUTC,
    })
}

func main() {
    os.Exit(runWithCrashCapture(os.Args[1:], version))
}
```

（F-011, F-013）

入口通过 blank import 注册三个 provider 和内置工具：

```go
import (
    _ "reasonix/internal/provider/anthropic"
    _ "reasonix/internal/provider/openai"
    _ "reasonix/internal/provider/responses"
    _ "reasonix/internal/provider/responses"
    _ "reasonix/internal/tool/builtin"
)
```

（F-011）

panic 捕获通过 `crashreport.CapturePanic` 记录后重新 panic，版本信息通过 `-ldflags` 注入。（F-005, F-012）

## boot 启动组装

`boot` 包是将"用户配置"转换为"可驱动 Controller"的唯一位置。`BuildRuntime` 函数运行完整组装：

```go
func BuildRuntime(ctx context.Context, opts Options) (*BuildResult, error) {
    return build(ctx, opts)
}
```

（F-092）

`BuildResult` 包含：

| 字段 | 说明 |
|------|------|
| `Controller` | ready-to-drive 的 `control.Controller` |
| `Snapshot` | extension kernel 冻结快照 |
| `Runtime` | extension sidecar 生命周期集合 |
| `Dispatcher` | 不可变的 extension 拦截调度器 |
| `ProviderResolver` | 有效 provider 解析器 |
| `Extensions` | sidecar Manager |

（F-091）

`Options` 携带前端选择的 per-run 旋钮（Model、MaxSteps、Sink、EffortOverride、PermissionAllow 等），其余全部从配置读取。（F-090）

## Provider 解析

`LocalProviderResolver` 从配置构建 provider 目录：

```go
func (r *LocalProviderResolver) Catalog() []provider.Descriptor {
    // 遍历 cfg.Providers，返回 Ref、DisplayName、Model、
    // ContextWindow、Vision、Pricing、Efforts 等
}
```

当配置的 model 无法解析到 provider 时返回 `ErrUnknownModel`，调用方可检测此错误重新运行 setup。（F-093, F-094）

## 构建系统

Makefile 提供以下关键目标：

| 目标 | 作用 |
|------|------|
| `make build` | `CGO_ENABLED=0 go build` → `bin/reasonix` |
| `make cross` | 交叉编译 6 目标到 `dist/` |
| `make test` | `go test ./...` |
| `make lint` | golangci-lint + repolint |
| `make wails-install` | 安装固定版本 Wails CLI |

（F-003, F-004）

交叉编译目标矩阵：darwin/amd64、darwin/arm64、linux/amd64、linux/arm64、windows/amd64、windows/arm64。（F-004）

## 相关概念

- [Reasonix 简介](00-introduction.md)
- [Agent 运行循环](02-agent-run-loop.md)——boot 组装后的核心执行引擎
- [ACP 协议](03-acp-protocol.md)——ACP 如何通过 Factory 使用 boot 组装
- [CLI 与 TUI](05-cli-tui.md)——CLI 前端如何调用 boot
