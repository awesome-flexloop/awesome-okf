---
type: Reference
title: "src/cmd/ 命令行接口与核心命令"
description: "Toolbx CLI 框架（cobra）、7个核心子命令（create/enter/list/rm/rmi/run/completion）、全局选项与构建系统。"
tags: [toolbx, toolbox, cobra, cli, create, enter, run, list, rm, rmi, go]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:55:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:55:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: cmd-root
    resource: https://github.com/containers/toolbox/blob/main/src/cmd/root.go
    title: src/cmd/root.go 根命令定义
  - id: cmd-create
    resource: https://github.com/containers/toolbox/blob/main/src/cmd/create.go
    title: src/cmd/create.go 创建命令
  - id: cmd-enter
    resource: https://github.com/containers/toolbox/blob/main/src/cmd/enter.go
    title: src/cmd/enter.go 进入命令
  - id: cmd-run
    resource: https://github.com/containers/toolbox/blob/main/src/cmd/run.go
    title: src/cmd/run.go 运行命令
---

# src/cmd/ 命令行接口

Toolbx 使用 `github.com/spf13/cobra` 作为 CLI 框架，根命令在 `root.go` 中定义，各子命令独立文件实现。

## 目录结构（src/cmd/）

`src/cmd/` 目录包含 14 个 Go 源文件：

| 文件 | 功能说明 |
|------|---------|
| `root.go` | 根命令定义、全局选项、初始化、日志配置、迁移逻辑 |
| `create.go` | `toolbox create` 子命令：创建新容器 |
| `enter.go` | `toolbox enter` 子命令：进入交互式容器 Shell |
| `run.go` | `toolbox run` 子命令：在容器中执行单条命令 |
| `list.go` | `toolbox list` 子命令：列出容器和镜像 |
| `rm.go` | `toolbox rm` 子命令：删除容器 |
| `rmi.go` | `toolbox rmi` 子命令：删除镜像 |
| `completion.go` | `toolbox completion` 子命令：Shell 补全脚本生成 |
| `help.go` | 帮助命令与 man page 显示逻辑 |
| `initContainer.go` | 容器初始化命令（容器内部使用） |
| `rootDefault.go` | 默认命令行为实现 |
| `rootMigrationPath.go` | Podman 版本迁移路径处理 |
| `utils.go` | CLI 工具函数 |
| `root_test.go` | 根命令单元测试 |

## 根命令定义（rootCmd）

```go
var rootCmd = &cobra.Command{
    Use:               "toolbox",
    Short:             "Tool for interactive command line environments on Linux",
    PersistentPreRunE: preRun,
    RunE:              rootRun,
    Version:           version.GetVersion(),
}
```

## 全局选项（Persistent Flags）

| 选项 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--assumeyes` | `-y` | bool | `false` | 自动对所有问题回答 yes |
| `--log-level` | - | string | `"error"` | 日志级别：trace/debug/info/warn/error/fatal/panic |
| `--log-podman` | - | bool | `false` | 显示 Podman 调用日志（受 log-level 控制） |
| `--verbose` | `-v` | count | 0 | `-v` 等同于 `--log-level=debug`；`-vv` 同时启用 `--log-podman` |

## 核心子命令概览

### 1. toolbox create - 创建容器

创建新的 Toolbx 容器。首次运行时会自动拉取所需的 OCI 镜像（如 `fedora-toolbox`）。

常用选项：
- `--distro <distro>`：指定发行版（arch/fedora/rhel/ubuntu）
- `--release <release>`：指定发行版版本
- `--image <image>`：使用自定义镜像
- `--container <name>`：指定容器名称

### 2. toolbox enter - 进入容器

进入已存在的 Toolbx 容器，启动交互式 Shell。容器不存在时会提示是否先创建。

```bash
toolbox enter                  # 进入默认容器
toolbox enter my-container     # 进入指定名称容器
```

进入容器后，提示符会变化（如 `⬢[user@toolbox ~]$`），表示已在容器环境内。

### 3. toolbox run - 容器内执行命令

在 Toolbx 容器中执行单条命令，不进入交互式 Shell。

```bash
toolbox run <command>          # 在默认容器中执行命令
toolbox run --container <name> <cmd>  # 在指定容器执行
```

### 4. toolbox list - 列出资源

列出已存在的 Toolbx 容器和镜像。

```bash
toolbox list                   # 列出容器和镜像
toolbox list -c                # 只列出容器
toolbox list -i                # 只列出镜像
```

### 5. toolbox rm - 删除容器

删除一个或多个 Toolbx 容器。

```bash
toolbox rm <container-name>    # 删除指定容器
toolbox rm -a                  # 删除所有容器
toolbox rm -f <container>      # 强制删除运行中的容器
```

### 6. toolbox rmi - 删除镜像

删除一个或多个 Toolbx 镜像。

```bash
toolbox rmi <image-name>       # 删除指定镜像
toolbox rmi -a                 # 删除所有镜像
```

### 7. toolbox completion - Shell 补全

生成 Shell 补全脚本，支持 bash/zsh/fish/powershell。

## Go 包依赖

| 依赖包 | 用途 |
|--------|------|
| `github.com/spf13/cobra` | CLI 命令框架 |
| `github.com/spf13/viper` | 配置文件解析 |
| `github.com/sirupsen/logrus` | 结构化日志 |
| `github.com/godbus/dbus/v5` | D-Bus 通信 |
| `github.com/NVIDIA/go-nvlib` | NVIDIA GPU 支持 |
| `github.com/briandowns/spinner` | 终端加载动画 |
| `github.com/acobaugh/osrelease` | 操作系统发行版检测 |

## 内部包结构（src/pkg/）

| 包 | 功能 |
|----|------|
| `pkg/podman` | Podman CLI 封装与交互 |
| `pkg/shell` | Shell 环境检测与启动 |
| `pkg/utils` | 工具函数（架构检测、RHEL/Fedora/Ubuntu 检测、文件锁等） |
| `pkg/term` | 终端处理 |
| `pkg/nvidia` | NVIDIA GPU 支持 |
| `pkg/skopeo` | Skopeo 镜像操作封装 |
| `pkg/version` | 版本信息 |

## 构建系统

Toolbx 使用 **Meson** 构建系统：
- 根目录 `meson.build`：顶层构建定义
- `src/meson.build`：Go 二进制构建规则
- `src/go-build-wrapper`：Go 编译包装脚本
- `src/meson_go_fmt.py`：Go 代码格式化辅助脚本

二进制入口点为 `src/toolbox.go`，调用 `cmd.Execute()` 启动 CLI。
