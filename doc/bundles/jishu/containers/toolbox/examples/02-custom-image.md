---
type: Example
title: "构建自定义 Toolbx 镜像"
description: "从零编写 Containerfile 构建预装 Go 开发环境的自定义 Toolbx 镜像，使用 Podman 构建，基于自定义镜像创建容器，验证镜像功能，以及镜像优化最佳实践。"
tags: [toolbx, toolbox, custom-image, containerfile, dockerfile, buildah, podman-build, golang, development-environment]
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

# 构建自定义 Toolbx 镜像

本示例带你完整构建一个预装 Go 开发环境的自定义 Toolbx 镜像：编写 Containerfile → 使用 Podman 构建 → 基于自定义镜像创建容器 → 验证所有功能正常 → 镜像优化技巧。

## 前置条件

- 已完成 [第一个开发容器示例](01-first-toolbox.md)，熟悉 Toolbx 基本使用
- 系统已安装 Podman（rootless 模式正常工作）
- 网络连接可拉取 Fedora 基础镜像

## 目标镜像规格

我们将构建一个名为 `go-dev-toolbox` 的自定义镜像，包含：

- 基于官方 `fedora-toolbox:39` 镜像
- Go 1.22 工具链
- 常用 Go 开发工具（gopls、dlv、staticcheck）
- Git、Vim、TMUX、GDB 等通用开发工具
- 预配置的 Shell 环境变量（GOPATH、PATH、EDITOR）
- 正确的 Toolbx 标签和元数据

## 步骤 1：创建工作目录

```bash
[user@hostname ~]$ mkdir -p ~/toolbox-images/go-dev
[user@hostname ~]$ cd ~/toolbox-images/go-dev
```

## 步骤 2：编写 Containerfile

在工作目录下创建 `Containerfile`（等同于 Dockerfile）：

```dockerfile
# Containerfile for Go development Toolbx image
# Based on official fedora-toolbox image
FROM registry.fedoraproject.org/fedora-toolbox:39

# Toolbx 识别标签（必须）
LABEL com.github.containers.toolbox="true" \
      com.github.debarshiray.toolbox="true" \
      name="go-dev-toolbox" \
      version="1.0.0" \
      description="Go development environment for Toolbx" \
      usage="This image should be used with the toolbox command" \
      maintainer="Your Name <your.email@example.com>"

# 避免 dnf 安装时的交互式提示
ENV PAGER=cat
ENV LANG=C.UTF-8

# 安装 Go 和常用开发工具
# 使用 dnf 而不是 yum，Fedora Toolbx 镜像默认配置了 dnf
RUN sudo dnf install -y \
    golang-1.22.* \
    git \
    vim-enhanced \
    tmux \
    gdb \
    strace \
    ltrace \
    valgrind \
    make \
    cmake \
    gcc \
    gcc-c++ \
    patch \
    which \
    tar \
    gzip \
    bzip2 \
    xz \
    unzip \
    zip \
    curl \
    wget \
    jq \
    ripgrep \
    fd-find \
    htop \
    tree \
    nc \
    bind-utils \
    && sudo dnf clean all

# 创建 Go 工作目录
RUN sudo mkdir -p /go/{bin,pkg,src} \
    && sudo chmod -R 777 /go

# 配置 Shell 环境变量（/etc/profile.d/ 是 Toolbx 推荐的位置）
RUN echo '# Go environment' | sudo tee /etc/profile.d/go-dev.sh > /dev/null \
    && echo 'export GOPATH=$HOME/go' | sudo tee -a /etc/profile.d/go-dev.sh > /dev/null \
    && echo 'export GOROOT=/usr/lib/golang' | sudo tee -a /etc/profile.d/go-dev.sh > /dev/null \
    && echo 'export PATH=$PATH:$GOROOT/bin:$GOPATH/bin:/go/bin' | sudo tee -a /etc/profile.d/go-dev.sh > /dev/null \
    && echo 'export EDITOR=vim' | sudo tee -a /etc/profile.d/go-dev.sh > /dev/null \
    && echo 'export GO111MODULE=on' | sudo tee -a /etc/profile.d/go-dev.sh > /dev/null \
    && sudo chmod +x /etc/profile.d/go-dev.sh

# Vim 基础配置（全局）
RUN echo 'set number' | sudo tee -a /etc/vimrc.local > /dev/null \
    && echo 'set tabstop=4' | sudo tee -a /etc/vimrc.local > /dev/null \
    && echo 'set shiftwidth=4' | sudo tee -a /etc/vimrc.local > /dev/null \
    && echo 'set expandtab' | sudo tee -a /etc/vimrc.local > /dev/null \
    && echo 'set autoindent' | sudo tee -a /etc/vimrc.local > /dev/null \
    && echo 'syntax on' | sudo tee -a /etc/vimrc.local > /dev/null \
    && echo 'set mouse=a' | sudo tee -a /etc/vimrc.local > /dev/null

# 验证 Go 安装（构建时验证，失败则构建失败）
RUN go version && go env GOPATH

# 确保 /run/host 目录存在（Toolbx 挂载点）
RUN sudo mkdir -p /run/host

# 默认命令
CMD ["/bin/bash"]
```

### Containerfile 关键点说明

1. **基础镜像选择**：`FROM registry.fedoraproject.org/fedora-toolbox:39`——直接基于官方 Toolbx 镜像扩展是最可靠的方式，官方镜像已配置好所有 Toolbx 必需的组件（sudo、useradd、/run/host 等），省去从头配置的麻烦。

2. **标签（LABEL）**：`com.github.containers.toolbox="true"` 是关键标签，Toolbx 通过它识别兼容镜像。

3. **sudo 使用**：Toolbx 容器内默认用户不是 root，但有 NOPASSWD sudo 权限，因此 Dockerfile 中需要用 `sudo dnf` 安装软件包（官方 fedora-toolbox 镜像的构建约定）。

4. **profile.d 配置**：环境变量放在 `/etc/profile.d/go-dev.sh` 中，这是 Toolbx 读取 Shell 初始化脚本的标准位置，登录 Shell 时自动加载。

5. **构建时验证**：`RUN go version` 确保 Go 正确安装，如果 dnf 包名错误或安装失败，构建过程会直接失败。

## 步骤 3：构建镜像

使用 Podman 构建镜像：

```bash
[user@hostname go-dev]$ podman build -t localhost/go-dev-toolbox:v1.0.0 -f Containerfile .
```

构建过程输出示例：

```
STEP 1/9: FROM registry.fedoraproject.org/fedora-toolbox:39
STEP 2/9: LABEL com.github.containers.toolbox="true" ...
STEP 3/9: ENV PAGER=cat LANG=C.UTF-8
STEP 4/9: RUN sudo dnf install -y golang-1.22.* ...
Fedora 39 - x86_64                              5.2 MB/s |  65 MB     00:12
Dependencies resolved.
...安装过程...
Complete!
--> 5a3b1c2d4e5f
STEP 5/9: RUN sudo mkdir -p /go/{bin,pkg,src} ...
STEP 6/9: RUN echo '# Go environment' | sudo tee /etc/profile.d/go-dev.sh ...
STEP 7/9: RUN echo 'set number' | sudo tee -a /etc/vimrc.local ...
STEP 8/9: RUN go version && go env GOPATH
go version go1.22.x linux/amd64
/home/user/go
STEP 9/9: CMD ["/bin/bash"]
COMMIT localhost/go-dev-toolbox:v1.0.0
--> 8f7e6d5c4b3a
Successfully tagged localhost/go-dev-toolbox:v1.0.0
```

构建完成后验证镜像存在：

```bash
[user@hostname go-dev]$ podman images | grep go-dev
localhost/go-dev-toolbox          v1.0.0      8f7e6d5c4b3a  1 minute ago  1.2 GB
```

同时添加 `latest` 标签方便使用：

```bash
[user@hostname go-dev]$ podman tag localhost/go-dev-toolbox:v1.0.0 localhost/go-dev-toolbox:latest
```

## 步骤 4：基于自定义镜像创建容器

使用 `--image`/`-i` 选项指定自定义镜像：

```bash
[user@hostname ~]$ toolbox create -i localhost/go-dev-toolbox:latest -c go-dev
Created container: go-dev
Enter with: toolbox enter go-dev
```

进入容器：

```bash
[user@hostname ~]$ toolbox enter go-dev
⬢[user@toolbox ~]$
```

## 步骤 5：验证镜像功能

进入容器后逐项验证功能是否正常。

### 5.1 验证 Go 环境

```bash
# Go 版本
⬢[user@toolbox ~]$ go version
go version go1.22.x linux/amd64

# Go 环境变量
⬢[user@toolbox ~]$ go env GOPATH GOROOT PATH
/home/user/go
/usr/lib/golang
/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/home/user/go/bin:/go/bin

# which 找到 go
⬢[user@toolbox ~]$ which go
/usr/bin/go
```

### 5.2 验证环境变量加载

```bash
⬢[user@toolbox ~]$ echo $GOPATH
/home/user/go

⬢[user@toolbox ~]$ echo $EDITOR
vim

⬢[user@toolbox ~]$ echo $GO111MODULE
on
```

### 5.3 验证其他工具安装

```bash
⬢[user@toolbox ~]$ git --version
git version 2.43.x

⬢[user@toolbox ~]$ vim --version | head -2
VIM - Vi IMproved 9.0

⬢[user@toolbox ~]$ rg --version
ripgrep 13.0.0

⬢[user@toolbox ~]$ gdb --version | head -1
GNU gdb (GDB) Fedora 13.2-x.fc39
```

### 5.4 验证 Toolbx 核心透传功能

```bash
# 主目录访问
⬢[user@toolbox ~]$ ls ~/.ssh/
id_ed25519  id_ed25519.pub  known_hosts

# 当前目录
⬢[user@toolbox ~]$ pwd
/home/user

# /run/host 逃生口
⬢[user@toolbox ~]$ ls /run/host/
bin  boot  dev  etc  home  lib  lib64  ...

# sudo 可用
⬢[user@toolbox ~]$ sudo whoami
root

# 网络访问
⬢[user@toolbox ~]$ curl -s https://proxy.golang.org | head -1
```

### 5.5 验证实际 Go 项目编译

创建一个简单的 Go 程序测试完整工作流：

```bash
⬢[user@toolbox ~]$ mkdir -p ~/go/src/hello && cd ~/go/src/hello
⬢[user@toolbox hello]$ go mod init hello
go: creating new go.mod: module hello
```

创建 `main.go`：

```go
package main

import (
    "fmt"
    "runtime"
)

func main() {
    fmt.Println("Hello from Go in Toolbx!")
    fmt.Printf("Go version: %s\n", runtime.Version())
    fmt.Printf("OS/Arch: %s/%s\n", runtime.GOOS, runtime.GOARCH)
}
```

编译并运行：

```bash
⬢[user@toolbox hello]$ go run main.go
Hello from Go in Toolbx!
Go version: go1.22.x
OS/Arch: linux/amd64

⬢[user@toolbox hello]$ go build -o hello .
⬢[user@toolbox hello]$ ./hello
Hello from Go in Toolbx!
Go version: go1.22.x
OS/Arch: linux/amd64
```

编译成功！由于主目录透传，主机上也能看到这个项目：

```bash
⬢[user@toolbox hello]$ exit
logout
[user@hostname ~]$ ls ~/go/src/hello/
go.mod  hello  main.go
[user@hostname ~]$ file ~/go/src/hello/hello
/home/user/go/src/hello/hello: ELF 64-bit LSB executable, x86-64, ...
```

### 5.6 安装额外 Go 工具

容器内可以继续安装 Go 工具（这些不会持久化到镜像，但写入主目录 GOPATH 的工具会保留，因为主目录是挂载的）：

```bash
⬢[user@toolbox ~]$ go install golang.org/x/tools/gopls@latest
⬢[user@toolbox ~]$ go install github.com/go-delve/delve/cmd/dlv@latest
⬢[user@toolbox ~]$ go install honnef.co/go/tools/cmd/staticcheck@latest

# 验证（GOPATH/bin 在 PATH 中）
⬢[user@toolbox ~]$ gopls version
golang.org/x/tools/gopls v0.x.x
```

> 注意：通过 `go install` 安装到 `$GOPATH/bin` 的工具存储在主目录中，**容器删除后仍然保留**——因为 `$HOME` 是从主机挂载的！下次重建容器时这些工具立即可用，无需重新安装。

## 步骤 6：更新镜像版本

如果需要更新镜像（如升级 Go 版本、添加新工具），修改 Containerfile 后重新构建：

```bash
# 修改 Containerfile，比如升级到 Fedora 40
# FROM registry.fedoraproject.org/fedora-toolbox:40

# 构建新版本
[user@hostname go-dev]$ podman build -t localhost/go-dev-toolbox:v1.1.0 -f Containerfile .
[user@hostname go-dev]$ podman tag localhost/go-dev-toolbox:v1.1.0 localhost/go-dev-toolbox:latest
```

基于新镜像创建新容器：

```bash
[user@hostname ~]$ toolbox create -i localhost/go-dev-toolbox:v1.1.0 -c go-dev-v11
```

旧容器和旧镜像可以保留或删除，不影响新容器使用。

## 镜像优化技巧

### 1. 多阶段构建（减小镜像体积）

如果镜像中需要编译某些大型工具（如从源码编译最新版 Neovim），使用多阶段构建将编译产物复制到最终镜像，避免在最终镜像中保留编译依赖：

```dockerfile
# 构建阶段
FROM registry.fedoraproject.org/fedora-toolbox:39 AS builder
RUN sudo dnf install -y gcc make git cmake ...
RUN git clone https://github.com/neovim/neovim /tmp/neovim \
    && cd /tmp/neovim \
    && make CMAKE_BUILD_TYPE=Release \
    && make install DESTDIR=/tmp/neovim-install

# 最终镜像
FROM registry.fedoraproject.org/fedora-toolbox:39
# 只复制编译好的二进制，不复制编译器和源码
COPY --from=builder /tmp/neovim-install/ /
```

### 2. 分层缓存优化

Podman/Docker 会缓存镜像层，将变化频率低的操作放在前面，变化频率高的操作放在后面：

```dockerfile
# 好：先装大型包（不常变化），后复制配置文件（常变化）
RUN sudo dnf install -y golang git vim ... && sudo dnf clean all
COPY vimrc.local /etc/vimrc.local
COPY profile.d/ /etc/profile.d/

# 不好：每次配置变化都导致 dnf install 重新执行
COPY vimrc.local /etc/vimrc.local
RUN sudo dnf install -y golang git vim ...
```

### 3. 清理 dnf 缓存

务必在同一个 `RUN` 指令中执行 `dnf install` 和 `dnf clean all`，否则缓存会留在镜像层中增大体积：

```dockerfile
# 好：同一层清理缓存
RUN sudo dnf install -y pkg1 pkg2 && sudo dnf clean all

# 不好：缓存在单独的层，clean 不减小体积
RUN sudo dnf install -y pkg1 pkg2
RUN sudo dnf clean all
```

### 4. 使用 .containerignore

创建 `.containerignore` 文件排除不需要的文件：

```
# .containerignore
.git
.gitignore
*.md
.DS_Store
```

## 推送到远程 Registry（可选）

如果需要在多台机器上使用自定义镜像，可以推送到容器镜像仓库：

```bash
# 标记为远程仓库格式
[user@hostname ~]$ podman tag localhost/go-dev-toolbox:v1.0.0 quay.io/yourusername/go-dev-toolbox:v1.0.0

# 登录 registry
[user@hostname ~]$ podman login quay.io

# 推送
[user@hostname ~]$ podman push quay.io/yourusername/go-dev-toolbox:v1.0.0
```

在其他机器上直接使用：

```bash
# 另一台机器上直接创建（自动拉取镜像）
toolbox create -i quay.io/yourusername/go-dev-toolbox:v1.0.0 -c go-dev
```

## 验证清单

完成本示例后，你应该能够：

- [x] 理解 Toolbx 自定义镜像的基本结构和必需标签
- [x] 编写基于官方 fedora-toolbox 扩展的 Containerfile
- [x] 使用 `podman build` 构建自定义镜像
- [x] 使用 `toolbox create -i <image>` 基于自定义镜像创建容器
- [x] 验证容器内 Go 工具链、环境变量、核心透传功能正常
- [x] 理解镜像预装工具与主目录持久化工具的区别
- [x] 了解镜像分层缓存优化、多阶段构建等优化技巧
- [x] 知道如何将镜像推送到远程 registry 共享给团队

## 常见问题

### Q: 为什么 Containerfile 中用 `sudo dnf` 而不是直接 `dnf`？

官方 `fedora-toolbox` 镜像的 Containerfile 设计上以非 root 用户构建（与 Toolbx 运行时一致），因此需要 sudo。如果你的基础镜像在构建时默认是 root（如从 `fedora:39` 开始），则不需要 sudo。

### Q: 自定义镜像需要包含 toolbox 二进制本身吗？

不需要。Toolbx 二进制安装在主机上，通过 Podman 调用，不需要在镜像内安装 `toolbox` 命令。

### Q: 为什么我构建的镜像比官方镜像大很多？

官方镜像经过精简。使用 `podman history <image>` 查看各层大小，确保 `dnf clean all` 在同一 RUN 层，避免不必要的文档和缓存文件。

### Q: 可以在自定义镜像中使用 Ubuntu/Debian 基础镜像吗？

可以，参考 `images/ubuntu/` 目录下官方 Ubuntu Toolbx 镜像的 Containerfile 了解 Ubuntu/Debian 上的必要配置（如 sudo 配置、用户管理工具包名差异）。

## 相关概念

- [/concepts/03-custom-images.md](../concepts/03-custom-images.md)
- [/concepts/02-workflow.md](../concepts/02-workflow.md)
- [/examples/01-first-toolbox.md](01-first-toolbox.md)
