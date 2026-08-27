---
type: Concept
title: "日常开发工作流（create/enter/run）"
description: "Toolbx 三大核心命令工作流：create 创建容器、enter 交互式进入、run 非交互式执行命令，以及 list/rm/rmi 生命周期管理。"
tags: [toolbx, toolbox, workflow, create, enter, run, list, rm, rmi, daily-use]
generated: { by: "reference_agent/trae-cn", at: 2026-08-26T15:55:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-26T15:55:00+08:00 }
status: stable
stale_after: 2027-08-26
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README.md 项目概览与定位
  - id: cmd
    resource: /references/cmd-source.md
    title: src/cmd/ 命令行接口与核心命令
---

# 日常开发工作流（create/enter/run）

Toolbx 的日常使用围绕三个核心命令展开：`create`（创建容器）、`enter`（进入交互式 Shell）、`run`（执行单条命令）。配合 `list`、`rm`、`rmi` 完成容器和镜像的完整生命周期管理。

## 核心工作流概览

```
toolbox create  →  toolbox enter  →  开发工作  →  exit（离开容器）
      ↓               ↓
  （一次性）      （每次开发时）
                     ↓
              toolbox run <cmd>  （单次执行场景）
```

典型开发场景：每天打开终端，`toolbox enter` 进入容器，在容器内完成编码、编译、调试、Git 操作，`exit` 或关闭终端离开。容器保持运行状态，下次进入时所有已安装的工具和文件依然存在。

## toolbox create - 创建容器

`create` 命令用于创建新的 Toolbx 容器。这是一次性操作，容器创建后可重复使用。

### 基本用法

```bash
# 创建与主机发行版匹配的默认容器（推荐首次使用）
toolbox create

# 创建指定名称的容器
toolbox create my-dev-env

# 创建指定 Fedora 版本的容器
toolbox create --distro fedora --release 39
toolbox create --distro fedora --release f39  # 两种格式等价

# 创建 Ubuntu 24.04 容器
toolbox create --distro ubuntu --release 24.04

# 创建 RHEL 9.3 容器
toolbox create --distro rhel --release 9.3

# 创建 Arch Linux 容器
toolbox create --distro arch
```

### 首次创建流程

首次运行 `toolbox create` 时，会自动拉取所需的 OCI 镜像：

```bash
[user@hostname ~]$ toolbox create
Image required to create toolbox container.
Download registry.fedoraproject.org/fedora-toolbox:39 (294.1MB)? [y/N]: y
Created container: fedora-toolbox-39
Enter with: toolbox enter
```

使用 `-y/--assumeyes` 选项可跳过确认提示：

```bash
toolbox create -y  # 自动回答 yes，适用于脚本
```

### create 常用选项

| 选项 | 说明 |
|------|------|
| `-c, --container <name>` | 指定容器名称（默认：`<distro>-toolbox-<release>`） |
| `-i, --image <image>` | 使用自定义镜像而非默认发行版镜像 |
| `-d, --distro <distro>` | 指定发行版（arch/fedora/rhel/ubuntu） |
| `-r, --release <release>` | 指定发行版版本 |
| `-y, --assumeyes` | 自动确认所有提示 |

### 默认容器命名规则

不指定名称时，容器自动命名为：`<distro>-toolbox-<release>`

```
fedora-toolbox-39    # Fedora 39 默认容器
ubuntu-toolbox-24.04 # Ubuntu 24.04 默认容器
rhel-toolbox-9.3     # RHEL 9.3 默认容器
```

## toolbox enter - 进入交互式 Shell

`enter` 命令用于进入已存在的 Toolbx 容器，启动交互式 Shell。这是日常开发中最常用的命令。

### 基本用法

```bash
# 进入默认容器（如果不存在会提示创建）
toolbox enter

# 进入指定名称的容器
toolbox enter my-dev-env

# 进入指定发行版版本的容器
toolbox enter --distro fedora --release 39
```

### 进入后的环境

成功进入后，Shell 提示符会变化（默认 Fedora 镜像上增加 `⬢` 前缀）：

```bash
[user@hostname ~]$ toolbox enter
⬢[user@toolbox ~]$
```

此时你已在容器内，可以：
- 安装软件包（`sudo dnf install`、`apt install` 等）
- 访问主目录下的所有文件和项目
- 运行编译器、编辑器、调试器、Git 等开发工具
- 启动图形应用（Firefox、VS Code 等）
- 使用 SSH agent、D-Bus 等主机服务

### 离开容器

使用 `exit` 命令或按 `Ctrl+D` 离开容器：

```bash
⬢[user@toolbox ~]$ exit
logout
[user@hostname ~]$
```

容器在退出 Shell 后**不会自动删除**，保持停止状态。下次 `toolbox enter` 时容器会重新启动，所有已安装的软件和文件更改都会保留。

### 自动创建行为

如果默认容器不存在，`toolbox enter` 会提示是否创建：

```bash
[user@hostname ~]$ toolbox enter
No toolbox containers found. Create now? [y/N] y
...创建并进入...
```

## toolbox run - 非交互式执行命令

`run` 命令用于在 Toolbx 容器中执行单条命令，不进入交互式 Shell。适用于脚本化调用和一次性命令场景。

### 基本用法

```bash
# 在默认容器中执行命令
toolbox run <command> [args...]

# 示例：在容器内查看 gcc 版本
toolbox run gcc --version

# 在指定容器中执行
toolbox run --container my-dev-env make build

# 在指定发行版容器中执行
toolbox run --distro fedora --release 39 dnf info ansible
```

### run vs enter 的选择

| 场景 | 使用 `enter` | 使用 `run` |
|------|-------------|-----------|
| 多步开发工作（编码/编译/调试） | ✅ 推荐 | ❌ 不便 |
| 单次执行命令（查看版本、跑个脚本） | ❌ 繁琐 | ✅ 推荐 |
| Shell 脚本中调用 Toolbx 工具 | ❌ 无法交互 | ✅ 适合 |
| 交互式程序（vim、gdb TUI） | ✅ 推荐 | ⚠️ 需 `-t` 分配 tty |

### 与 Shell 管道结合

`toolbox run` 可以与主机 Shell 管道、重定向无缝配合：

```bash
# 容器内编译，结果输出到主机文件
toolbox run gcc -o hello hello.c
./hello  # 编译出的二进制在主机当前目录直接运行（如架构兼容）

# 管道处理
toolbox run cat /etc/os-release | grep PRETTY_NAME

# 复杂脚本
toolbox run bash -c "
    sudo dnf install -y golang
    go build -o myapp .
    ./myapp --version
"
```

## toolbox list - 列出容器和镜像

`list` 命令用于查看已有的 Toolbx 容器和镜像。

### 基本用法

```bash
# 列出所有容器和镜像
toolbox list

# 只列出容器（-c/--containers）
toolbox list -c

# 只列出镜像（-i/--images）
toolbox list -i
```

### 输出示例

```bash
[user@hostname ~]$ toolbox list -c

CONTAINER ID  CONTAINER NAME     CREATED        STATUS   IMAGE NAME
a1b2c3d4e5f6  fedora-toolbox-39  2 weeks ago    running  registry.fedoraproject.org/fedora-toolbox:39
f6e5d4c3b2a1  ubuntu-toolbox-24  3 days ago     exited   registry.fedoraproject.org/ubuntu-toolbox:24.04
```

容器状态：
- `running`：容器正在运行（可能是 enter 会话或后台进程）
- `exited`：容器已停止，可随时 enter 启动
- `created`：容器已创建但从未启动

## toolbox rm - 删除容器

`rm` 命令用于删除不再需要的 Toolbx 容器。**删除容器会清除容器内所有已安装的软件和文件系统更改**（主目录挂载不受影响）。

### 基本用法

```bash
# 删除指定容器
toolbox rm fedora-toolbox-39

# 强制删除运行中的容器（-f/--force）
toolbox rm -f my-dev-env

# 删除所有容器（-a/--all）
toolbox rm -a

# 删除所有容器并跳过确认
toolbox rm -af
```

### 注意事项

- 主目录 `$HOME` 是从主机挂载的，删除容器**不会**删除主目录下的文件
- 容器内通过 `dnf install`/`apt install` 安装的软件包会随容器删除而丢失
- 建议将需要持久化的自定义配置写入 dotfiles（`.bashrc`、`.gitconfig` 等），这些存储在主目录中不会丢失

## toolbox rmi - 删除镜像

`rmi` 命令用于删除 Toolbx 镜像。删除镜像前需先删除使用该镜像的所有容器。

```bash
# 删除指定镜像
toolbox rmi registry.fedoraproject.org/fedora-toolbox:39

# 删除所有镜像（-a/--all）
toolbox rmi -a

# 强制删除（-f/--force）
toolbox rmi -f <image>
```

## 日常使用最佳实践

### 1. 一个容器 vs 多个容器

| 策略 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| 单容器 | 简单，所有工具在一个环境 | 不同项目依赖可能冲突 | 通用开发、依赖一致的项目 |
| 多容器（按项目/语言） | 环境隔离，依赖干净 | 需要管理多个容器 | 多语言开发、依赖版本差异大 |

推荐新手从单容器开始，遇到依赖冲突时再拆分多个容器：

```bash
# 多容器示例：按项目/语言分
toolbox create -c go-dev      # Go 开发环境
toolbox create -c python-dev  # Python 数据科学环境
toolbox create -c rust-dev    # Rust 开发环境
```

### 2. 别名简化输入

在主机 `~/.bashrc` 或 `~/.zshrc` 中添加别名可减少输入：

```bash
alias tb="toolbox"
alias tbe="toolbox enter"
alias tbr="toolbox run"
alias tbc="toolbox create"
alias tbl="toolbox list"
```

### 3. 进入容器即工作

Toolbx 透传当前目录和主目录，因此以下工作流非常顺畅：

```bash
[user@hostname ~]$ cd ~/projects/myapp
[user@hostname myapp]$ toolbox enter  # 直接进入，自动 cd 到 ~/projects/myapp
⬢[user@toolbox myapp]$ vim main.go
⬢[user@toolbox myapp]$ go build
⬢[user@toolbox myapp]$ go test
⬢[user@toolbox myapp]$ exit
[user@hostname myapp]$ ls  # 编译产物直接在主机目录可见
```

### 4. 在 Shell 脚本中使用

利用 `toolbox run` 可在主机脚本中透明使用容器内的工具：

```bash
#!/bin/bash
# build.sh - 在 Toolbx 容器内构建项目
toolbox run make clean
toolbox run make all
toolbox run make test
echo "Build completed successfully"
```

### 5. 全局选项

所有命令都支持以下全局选项：

| 选项 | 用途 |
|------|------|
| `-y, --assumeyes` | 自动回答 yes，适用于 CI/脚本 |
| `-v, --verbose` | 启用 debug 日志 |
| `-vv` | 启用 debug 日志 + Podman 调用日志 |
| `--log-level <level>` | 设置日志级别 |
| `--log-podman` | 显示底层 Podman 命令输出（排障用） |

排障时使用 `-vv` 查看详细的 Podman 调用：

```bash
toolbox -vv create  # 查看创建容器时底层执行的所有 Podman 命令
```

## 命令速查表

| 操作 | 命令 |
|------|------|
| 创建默认容器 | `toolbox create` |
| 创建指定发行版容器 | `toolbox create -d fedora -r 39` |
| 创建命名容器 | `toolbox create -c my-env` |
| 进入默认容器 | `toolbox enter` |
| 进入命名容器 | `toolbox enter my-env` |
| 在容器内执行命令 | `toolbox run <cmd>` |
| 列出容器/镜像 | `toolbox list [-c/-i]` |
| 删除容器 | `toolbox rm [-f] <name>` |
| 删除所有容器 | `toolbox rm -af` |
| 删除镜像 | `toolbox rmi <image>` |
| 查看帮助 | `toolbox help [command]` |
| 查看版本 | `toolbox --version` |

## 相关概念

- [/concepts/00-introduction.md](00-introduction.md)
- [/concepts/01-pass-through.md](01-pass-through.md)
- [/concepts/03-custom-images.md](03-custom-images.md)
- [/examples/01-first-toolbox.md](../examples/01-first-toolbox.md)
