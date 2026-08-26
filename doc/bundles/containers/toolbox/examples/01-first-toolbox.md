---
type: Example
title: "创建第一个开发容器"
description: "从零开始安装 Toolbx、创建第一个 Fedora 开发容器、进入容器安装工具、运行图形应用、使用 run 命令和清理容器的完整流程。"
tags: [toolbx, toolbox, quickstart, first-container, tutorial, fedora, create, enter]
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

# 创建第一个开发容器

本示例带你从零开始完成 Toolbx 的完整入门流程：安装 → 创建第一个容器 → 进入容器安装开发工具 → 运行图形应用 → 使用 `toolbox run` 执行单次命令 → 清理容器。

## 前置条件

- Linux 操作系统（推荐 Fedora Silverblue/Workstation，也支持 Arch、Ubuntu、RHEL）
- 已安装 Podman（Toolbx 的底层容器运行时）
- 当前用户已配置 subuid/subgid 范围（rootless Podman 正常工作的前提）

## 步骤 1：安装 Toolbx

### Fedora Silverblue / Kinoite（OSTree 系统）

Toolbx 已预装在 Silverblue/Kinoite 上，无需额外安装。直接在终端输入 `toolbox` 即可使用。

### Fedora Workstation / Server

```bash
sudo dnf install toolbox
```

### Arch Linux

```bash
sudo pacman -S toolbox
```

### Ubuntu 24.04

```bash
sudo apt install podman-toolbox
```

验证安装：

```bash
[user@hostname ~]$ toolbox --version
toolbox version 0.0.99.4
```

> 注：具体版本号可能因发行版和更新时间有所不同。

## 步骤 2：创建第一个容器

使用默认参数创建容器。Toolbx 会自动检测主机发行版版本，拉取对应的 `fedora-toolbox` 镜像（Fedora 系统）或回退到 Fedora 镜像（其他发行版）。

```bash
[user@hostname ~]$ toolbox create
```

首次运行会出现镜像下载提示：

```
Image required to create toolbox container.
Download registry.fedoraproject.org/fedora-toolbox:39 (294.1MB)? [y/N]:
```

输入 `y` 并回车确认下载。镜像拉取和容器创建需要一点时间，完成后会看到：

```
Created container: fedora-toolbox-39
Enter with: toolbox enter
```

容器已创建，默认命名为 `fedora-toolbox-39`（格式为 `<distro>-toolbox-<release>`）。

### 无提示创建（适合脚本）

使用 `-y` 选项自动确认所有提示：

```bash
toolbox create -y
```

### 创建指定名称的容器

如果你希望使用自定义名称：

```bash
[user@hostname ~]$ toolbox create -c my-dev-env
Created container: my-dev-env
Enter with: toolbox enter --container my-dev-env
```

## 步骤 3：进入容器

使用 `enter` 命令进入刚创建的容器：

```bash
[user@hostname ~]$ toolbox enter
```

成功进入后，Shell 提示符会发生变化（Fedora 镜像会出现 `⬢` 前缀）：

```
⬢[user@toolbox ~]$
```

提示符变化表示你已在 Toolbx 容器内部。

验证当前环境：

```bash
# 查看当前用户（应与主机用户名相同）
⬢[user@toolbox ~]$ whoami
user

# 查看 UID（应与主机上的 UID 一致，通常是 1000）
⬢[user@toolbox ~]$ id -u
1000

# 查看当前目录（应与主机当前目录一致）
⬢[user@toolbox ~]$ pwd
/home/user

# 验证主目录可访问
⬢[user@toolbox ~]$ ls ~/.bashrc
/home/user/.bashrc

# 验证 /run/host 主机逃生口存在
⬢[user@toolbox ~]$ ls /run/host/
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```

## 步骤 4：在容器内安装开发工具

现在你在完全可变的容器环境中，可以自由安装任何软件包。以 Fedora 为例，使用 `dnf` 安装开发工具：

```bash
# 安装常用开发工具链
⬢[user@toolbox ~]$ sudo dnf install -y \
    gcc \
    gcc-c++ \
    make \
    cmake \
    gdb \
    strace \
    valgrind \
    git \
    vim \
    tmux \
    curl \
    wget \
    python3 \
    python3-pip \
    golang \
    nodejs \
    npm
```

安装完成后验证工具可用：

```bash
⬢[user@toolbox ~]$ gcc --version
gcc (GCC) 13.x.x

⬢[user@toolbox ~]$ go version
go version go1.22.x linux/amd64

⬢[user@toolbox ~]$ python3 --version
Python 3.12.x

⬢[user@toolbox ~]$ git --version
git version 2.43.x
```

所有工具都安装在容器内，不会影响主机系统。

## 步骤 5：运行项目代码

进入你的项目目录（主目录已透传，直接访问即可）：

```bash
⬢[user@toolbox ~]$ cd ~/projects/hello-world
⬢[user@toolbox hello-world]$ ls
main.c
```

`main.c` 内容：

```c
#include <stdio.h>

int main() {
    printf("Hello from Toolbx container!\n");
    return 0;
}
```

编译并运行：

```bash
⬢[user@toolbox hello-world]$ gcc -o hello main.c
⬢[user@toolbox hello-world]$ ./hello
Hello from Toolbx container!
```

编译出的 `hello` 二进制文件直接出现在主机的 `~/projects/hello-world/` 目录中，因为主目录是从主机 bind mount 的。退出容器后，主机上可以直接看到这个文件。

## 步骤 6：运行图形应用（可选）

Toolbx 透传了 Wayland/X11 套接字，可以直接在容器内运行图形应用：

```bash
# 安装 Firefox
⬢[user@toolbox ~]$ sudo dnf install -y firefox

# 启动 Firefox（会在主机桌面上弹出窗口）
⬢[user@toolbox ~]$ firefox
```

图形应用与主机上原生应用外观完全一致，可以正常访问网络、播放音频、使用输入法。

## 步骤 7：使用 toolbox run 执行单次命令

对于不需要进入交互式 Shell 的场景，使用 `toolbox run` 在容器内执行单条命令：

**场景：在主机脚本中使用容器内的 Go 编译**

在主机上创建 `build.sh`：

```bash
#!/bin/bash
# build.sh - 在 Toolbx 容器内编译 Go 项目

echo "Building in Toolbx container..."
toolbox run bash -c '
    cd ~/projects/myapp
    go mod download
    go build -v -o myapp .
    go test ./...
'

if [ $? -eq 0 ]; then
    echo "Build successful!"
    ls -lh myapp
else
    echo "Build failed!"
    exit 1
fi
```

运行：

```bash
[user@hostname ~]$ chmod +x build.sh
[user@hostname ~]$ ./build.sh
```

**其他 run 命令示例**：

```bash
# 在容器内查看 Go 版本（不进入 Shell）
[user@hostname ~]$ toolbox run go version

# 在指定容器内执行命令
[user@hostname ~]$ toolbox run --container my-dev-env gcc --version

# 管道：容器内输出 → 主机工具处理
[user@hostname ~]$ toolbox run cat /etc/os-release | grep PRETTY_NAME
PRETTY_NAME="Fedora Linux 39 (Container Image)"
```

## 步骤 8：离开容器

使用 `exit` 命令或 `Ctrl+D` 退出容器 Shell：

```bash
⬢[user@toolbox ~]$ exit
logout
[user@hostname ~]$
```

你已回到主机。容器**没有被删除**，只是停止运行。所有已安装的软件包和容器内文件系统更改都被保留。

下次直接 `toolbox enter` 即可回到上次的环境，所有工具都还在。

## 步骤 9：列出和管理容器

查看已有的容器和镜像：

```bash
# 列出所有容器
[user@hostname ~]$ toolbox list -c

# 列出所有镜像
[user@hostname ~]$ toolbox list -i

# 同时列出容器和镜像
[user@hostname ~]$ toolbox list
```

容器状态说明：
- `running`：容器正在运行
- `exited`：容器已停止（可随时 enter 启动）

## 步骤 10：清理（可选）

如果不再需要某个容器，可以删除它：

```bash
# 先停止容器（如果正在运行，-f 强制删除）
[user@hostname ~]$ toolbox rm -f fedora-toolbox-39

# 删除所有容器
[user@hostname ~]$ toolbox rm -af
```

删除镜像（需要先删除使用该镜像的容器）：

```bash
# 列出镜像获取名称
[user@hostname ~]$ toolbox list -i

# 删除指定镜像
[user@hostname ~]$ toolbox rmi registry.fedoraproject.org/fedora-toolbox:39

# 删除所有镜像
[user@hostname ~]$ toolbox rmi -a
```

> **重要**：删除容器只会清除容器内通过 `dnf install` 安装的软件包，**不会删除主机主目录 `$HOME` 下的任何文件**（因为主目录是挂载的）。但如果你在容器内 `/usr/local`、`/opt` 等非主目录位置安装了软件，这些会随容器删除而丢失。

## 常见问题排查

### 问题：提示 "Missing subgid and/or subuid ranges"

rootless Podman 要求用户有 subuid/subgid 配置：

```bash
# 查看当前用户 subuid 配置
[user@hostname ~]$ grep $USER /etc/subuid
[user@hostname ~]$ grep $USER /etc/subgid

# 如果没有输出，为用户分配范围（Fedora）
[user@hostname ~]$ sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER

# 注销并重新登录
```

### 问题：镜像下载缓慢

Fedora 镜像可能较慢，可以配置镜像加速器或使用其他发行版镜像：

```bash
# 使用 Ubuntu 镜像创建容器
toolbox create -d ubuntu -r 24.04
```

### 问题：进入容器后 sudo 不工作

确保基础镜像中安装了 `sudo` 并正确配置了 wheel 组。使用官方镜像（如 `fedora-toolbox`）通常不会有此问题。

### 问题：图形应用无法启动

检查 Wayland/X11 相关环境变量是否正确：

```bash
⬢[user@toolbox ~]$ echo $WAYLAND_DISPLAY
⬢[user@toolbox ~]$ echo $DISPLAY
⬢[user@toolbox ~]$ ls $XDG_RUNTIME_DIR/wayland-0
```

如果为空，可能是在纯 TTY 环境（无图形会话）中运行，无法启动图形应用是正常的。

## 验证清单

完成本示例后，你应该能够：

- [x] 安装 Toolbx 并验证版本
- [x] 使用 `toolbox create` 创建第一个容器
- [x] 使用 `toolbox enter` 进入容器并识别提示符变化
- [x] 在容器内使用包管理器安装开发工具
- [x] 在容器内编译和运行代码
- [x] 理解主目录透传的效果（编译产物在主机可见）
- [x] 使用 `toolbox run` 执行非交互式命令
- [x] 使用 `exit` 离开容器且容器保持持久化
- [x] 使用 `toolbox list` 查看容器和镜像
- [x] 使用 `toolbox rm`/`toolbox rmi` 清理容器和镜像

## 下一步

- 阅读 [/concepts/01-pass-through.md](/concepts/01-pass-through.md) 了解 10 类主机资源透传的详细机制
- 阅读 [/examples/02-custom-image.md](/examples/02-custom-image.md) 学习构建自定义预装工具镜像
- 尝试创建多个容器：`toolbox create -c go-dev -d fedora -r 39`、`toolbox create -c python-dev -d ubuntu -r 24.04`
- 配置 Shell 别名（如 `alias tbe="toolbox enter"`）简化日常使用

## 相关概念

- [/concepts/00-introduction.md](/concepts/00-introduction.md)
- [/concepts/02-workflow.md](/concepts/02-workflow.md)
- [/examples/02-custom-image.md](/examples/02-custom-image.md)
