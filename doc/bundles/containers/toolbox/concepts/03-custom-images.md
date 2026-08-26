---
type: Concept
title: "自定义镜像与 /run/host 逃生口"
description: "Toolbx 自定义镜像构建方法、Containerfile 编写规范、images/ 目录官方镜像参考，以及 /run/host 主机文件系统逃生口的高级用法。"
tags: [toolbx, toolbox, custom-images, containerfile, dockerfile, /run/host, buildah, podman]
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

# 自定义镜像与 /run/host 逃生口

虽然默认的 `fedora-toolbox`、`ubuntu-toolbox` 等官方镜像已能满足大部分开发需求，但对于团队统一开发环境、预装工具链、特殊发行版支持等场景，需要构建自定义 Toolbx 镜像。配合 `/run/host` 逃生口，还可以实现更灵活的主机交互模式。

## 为什么需要自定义镜像

默认镜像虽然方便，但存在以下场景需要自定义：

| 场景 | 自定义镜像的优势 |
|------|----------------|
| 团队统一环境 | 所有成员使用完全相同的工具版本和配置 |
| 预装工具链 | 镜像内预装 Go/Rust/Node.js/Python 等开发环境，无需每次 `dnf install` |
| 自定义配置 | 预配置 vim、bash、git、tmux 等 dotfiles |
| 内部 CA 证书 | 预装企业内部 CA 证书，访问内部 HTTPS 服务 |
| 特殊发行版 | 官方不支持的发行版（如 CentOS Stream、Debian 等） |
| CI/CD 环境 | 用于流水线中的构建容器 |

## Toolbx 镜像的关键特征

Toolbx 容器与普通 OCI 容器不同，需要满足一些特殊约定才能正常工作。

### 必备组件

一个可用的 Toolbx 镜像必须包含：

1. **POSIX Shell**：`/bin/sh`（通常是 bash）
2. **用户管理工具**：`useradd`、`usermod`、`passwd` 等命令（用于创建与主机匹配的用户）
3. **sudo**：允许容器内用户提权（因为 Toolbx 以主机普通用户身份进入容器）
4. **capsh**（可选但推荐）：用于能力边界设置
5. **`/run/host` 挂载点**：目录需存在（即使为空），Toolbx 运行时会挂载主机文件系统

### 用户与 UID/GID 映射

Toolbx 容器的核心约定：容器内创建与主机**完全相同 UID/GID、用户名、组名**的用户。这是透传机制正常工作的基础——主目录文件权限、SSH agent 访问、D-Bus 认证都依赖 UID/GID 一致。

容器初始化流程（`toolbox init-container`，容器内部执行）：
1. 读取主机用户的 UID、GID、用户名、GECOS、Home 目录
2. 在容器内 `/etc/passwd`、`/etc/group` 中创建匹配的用户和组
3. 设置 sudo 权限（NOPASSWD）
4. 配置 Shell 环境

### 官方镜像参考

Toolbx 源码仓库 `images/` 目录下提供了各发行版官方镜像的 Containerfile 作为参考：

```
images/
├── fedora/
│   ├── f36/Containerfile
│   ├── f37/Containerfile
│   ├── f38/Containerfile
│   ├── f39/Containerfile
│   └── ...
├── rhel/
│   ├── 8.5/Containerfile
│   ├── 9.3/Containerfile
│   └── ...
├── ubuntu/
│   ├── 22.04/Containerfile
│   ├── 24.04/Containerfile
│   └── ...
├── arch/
│   └── Containerfile
└── test/
    └── busybox/Containerfile
```

阅读这些 Containerfile 是理解 Toolbx 镜像构建最佳实践的最好方式。

## 构建自定义镜像

### 方式一：基于官方 Toolbx 镜像扩展（推荐）

最简单的方式是从官方 `fedora-toolbox` 或 `ubuntu-toolbox` 镜像开始，在其基础上安装额外软件。这种方式可以确保镜像满足 Toolbx 的所有约定。

**示例：预装 Go 1.22 和常用开发工具的 Fedora Toolbx 镜像**

创建 `Containerfile`：

```dockerfile
# Containerfile
FROM registry.fedoraproject.org/fedora-toolbox:39

# 预装常用开发工具
RUN sudo dnf install -y \
    golang-1.22.* \
    git \
    vim \
    tmux \
    gdb \
    strace \
    ltrace \
    valgrind \
    make \
    cmake \
    gcc \
    gcc-c++ \
    python3-pip \
    nodejs \
    npm \
    && dnf clean all

# 预装 Go 工具
RUN go install golang.org/x/tools/gopls@latest \
    && go install github.com/go-delve/delve/cmd/dlv@latest \
    && go install mvdan.cc/sh/v3/cmd/shfmt@latest

# 配置 Git（可被主目录 dotfiles 覆盖）
RUN git config --system user.name "Your Name" \
    && git config --system user.email "your.email@example.com"

# 添加企业内部 CA 证书（如有）
# COPY corporate-ca.crt /etc/pki/ca-trust/source/anchors/
# RUN update-ca-trust extract

# 设置 Shell 环境变量
RUN echo 'export EDITOR=vim' >> /etc/profile.d/custom.sh \
    && echo 'export GOPATH=$HOME/go' >> /etc/profile.d/custom.sh \
    && echo 'export PATH=$PATH:$GOPATH/bin:/usr/local/go/bin' >> /etc/profile.d/custom.sh
```

使用 Podman/Buildah 构建镜像：

```bash
# 使用 podman build
podman build -t my-dev-toolbox -f Containerfile .

# 或使用 buildah
buildah build -t my-dev-toolbox -f Containerfile .
```

基于自定义镜像创建容器：

```bash
toolbox create -i my-dev-toolbox -c my-dev
toolbox enter my-dev
```

### 方式二：从通用发行版镜像从头构建

如果需要从基础镜像（如 `fedora:39`、`ubuntu:24.04`）开始构建，可以参考官方镜像的 Containerfile。

**Fedora 基础镜像最小 Containerfile 示例**：

```dockerfile
FROM fedora:39

ENV NAME=fedora-toolbox VERSION=39
LABEL com.github.containers.toolbox="true" \
      com.github.debarshiray.toolbox="true" \
      name="$NAME" \
      version="$VERSION" \
      usage="This image is meant to be used with the toolbox command"

# 安装 Toolbx 容器必备组件
RUN dnf -y install \
    bash \
    sudo \
    shadow-utils \
    util-linux \
    coreutils \
    grep \
    sed \
    gawk \
    findutils \
    && dnf -y reinstall glibc-common \
    && dnf clean all

# 创建 /run/host 挂载点
RUN mkdir -p /run/host

# 配置 sudo：允许 wheel 组成员无密码 sudo
RUN echo "%wheel ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/toolbox \
    && sed -i '/^#includedir.*/i /etc/sudoers.d/toolbox' /etc/sudoers

# 确保 /etc/hosts 等文件存在
RUN touch /etc/hosts /etc/resolv.conf /etc/machine-id

CMD ["/bin/bash"]
```

关键标签 `com.github.containers.toolbox="true"` 是 Toolbx 识别兼容镜像的标志之一。

### 方式三：使用 Boxkit/toolbox-image-builder 等工具

社区有一些工具可简化自定义 Toolbx 镜像的构建，例如：
- **[boxkit](https://github.com/termie/boxkit)**：声明式构建 Toolbx 镜像的工具
- 发行版包管理器提供的 toolbox 镜像构建脚本

## 使用自定义镜像

构建完成后，使用 `--image`/`-i` 选项指定镜像创建容器：

```bash
# 基于本地镜像创建
toolbox create -i localhost/my-dev-toolbox:latest -c my-dev

# 基于远程仓库镜像创建
toolbox create -i quay.io/myorg/my-toolbox:v1.0 -c team-env

# 进入容器
toolbox enter my-dev
```

如果镜像不存在于本地，`toolbox create` 会自动从 registry 拉取。

### 验证镜像兼容性

进入自定义镜像创建的容器后，验证以下功能是否正常：

```bash
# 1. 用户身份正确
whoami
id  # UID/GID 应与主机一致

# 2. sudo 可用
sudo whoami  # 应输出 root

# 3. 主目录正常
ls ~
pwd  # 应在主目录

# 4. /run/host 可访问
ls /run/host/

# 5. D-Bus 可用（如适用）
busctl list | head

# 6. 网络可用
curl --head https://fedoraproject.org
```

## /run/host 逃生口高级用法

`/run/host` 挂载了主机的完整根文件系统，为高级场景提供了"逃生"通道。理解它的挂载方式和正确使用场景，可以大幅扩展 Toolbx 的能力边界。

### 挂载实现

Toolbx 创建容器时，执行等价于以下 Podman 参数的挂载：

```bash
--volume /:/run/host:rslave  # 将主机根目录以 rslave 绑定挂载到 /run/host
```

`rslave` 传播标志意味着主机后续挂载的磁盘/USB 设备也会自动传播到 `/run/host` 下。

### 场景一：访问主机系统目录

容器内需要读取或修改主机配置文件：

```bash
# 查看主机内核版本（容器可能有自己的内核头文件但运行在主机内核上）
⬢[user@toolbox ~]$ cat /run/host/proc/version

# 查看主机已安装的 RPM 包（对比容器内）
⬢[user@toolbox ~]$ dnf --installroot /run/host list installed | grep kernel

# 访问主机的 systemd 套接字
⬢[user@toolbox ~]$ systemctl --root /run/host status podman
```

### 场景二：chroot 到主机环境进行故障排查

这是 Toolbx 在 Silverblue/CoreOS 上的经典故障排查用法——主机不可变，但 Toolbx 容器是可变的，通过 chroot `/run/host` 可以在"干净"环境中执行主机维护操作：

```bash
⬢[user@toolbox ~]$ sudo chroot /run/host
[root@toolbox /]#  # 现在已 chroot 到主机根文件系统
[root@toolbox /]# ostree admin status   # 查看 OSTree 部署
[root@toolbox /]# rpm-ostree status    # 查看包分层
[root@toolbox /]# exit                 # 退出 chroot
⬢[user@toolbox ~]$
```

> ⚠️ **注意**：在 rootless Toolbx 中，容器内 root 映射到主机普通用户，因此 chroot 后并非真正的主机 root，无法修改主机系统文件。在 rootful Toolbx（`sudo toolbox`）中需要格外小心。

### 场景三：调用主机上的二进制程序

如果某个工具只安装在主机上（或主机版本更新），可以直接通过 `/run/host` 调用：

```bash
# 调用主机上的 podman（容器内嵌套容器的一种方式）
⬢[user@toolbox ~]$ /run/host/usr/bin/podman version

# 调用主机上的编辑器打开文件
⬢[user@toolbox ~]$ /run/host/usr/bin/vim /run/host/etc/hosts
```

### 场景四：使用主机的包管理器缓存

在 Fedora Silverblue 上，主机的 DNF 缓存可以被容器共享，加速包安装：

```bash
# 挂载主机 DNF 缓存到容器内（高级用法，需谨慎）
⬢[user@toolbox ~]$ sudo mkdir -p /var/cache/dnf
⬢[user@toolbox ~]$ sudo mount --bind /run/host/var/cache/dnf /var/cache/dnf
```

### 场景五：跨容器文件共享

由于所有 Toolbx 容器都挂载 `/run/host`，而主机主目录是共享挂载，因此多个 Toolbx 容器通过主目录自然共享文件。`/run/host/tmp` 也可作为临时共享空间。

### /run/host 与安全边界

理解 `/run/host` 的安全含义很重要：

- **它不是安全漏洞**：Toolbx 容器内用户与主机用户 UID/GID 相同，`/run/host` 并没有让容器获得超出用户已有权限的能力——用户在主机上能读写什么文件，在容器内通过 `/run/host` 同样能读写什么文件
- **rootless 模式保护**：在 rootless Podman 下，容器内的 root（UID 0）映射为主机上的普通用户（通常 UID >= 100000 的子 UID），无法通过 `/run/host` 修改主机系统文件
- **网络安全**：Toolbx 使用 `--net=host`，容器和主机共享网络栈，这也是开发环境的设计选择，不是安全缺陷

## 自定义镜像最佳实践

### 1. 版本标签策略

为自定义镜像使用语义化版本或日期标签，避免使用 `latest` 导致环境不可复现：

```bash
# 好
podman build -t my-dev-toolbox:2026.08 -f Containerfile .
podman build -t my-dev-toolbox:v1.2.0 -f Containerfile .

# 避免（无法回溯具体版本）
podman build -t my-dev-toolbox -f Containerfile .
```

### 2. 保持镜像精简

- 只预装真正所有团队成员都需要的通用工具
- 个人化配置（vim 配色、Shell 别名）放在主目录 dotfiles 中，不放入镜像
- 使用多阶段构建（如需要编译某些工具）减小镜像体积

### 3. 利用 profile.d 进行环境配置

Toolbx 会读取 `/etc/profile.d/*.sh`，将环境变量和 Shell 初始化逻辑放在这里是最佳实践：

```dockerfile
COPY custom-env.sh /etc/profile.d/custom-env.sh
RUN chmod +x /etc/profile.d/custom-env.sh
```

`custom-env.sh`:
```bash
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
export EDITOR=vim
```

### 4. 自定义镜像 vs 容器启动后手动安装

| 方式 | 优点 | 缺点 | 适用 |
|------|------|------|------|
| 镜像内预装 | 可复现、快速启动、团队一致 | 镜像更新需重建 | 团队通用工具、稳定依赖 |
| 容器内手动安装 | 灵活、个性化 | 新容器需重复安装 | 个人实验性工具、临时使用 |
| dotfiles 配置 | 跨容器持久化、个人化 | 不适合二进制工具 | Shell 配置、编辑器配置 |

三者结合使用效果最佳：镜像装通用工具，dotfiles 放个人配置，容器内按需安装临时工具。

### 5. NVIDIA GPU 支持

Toolbx 原生支持 NVIDIA GPU 透传（通过 NVIDIA Container Toolkit/CDI）。自定义镜像中安装 CUDA 工具包即可：

```dockerfile
# Fedora 上安装 CUDA（示例，需根据实际版本调整）
RUN dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/fedora39/x86_64/cuda-fedora39.repo \
    && dnf install -y cuda-toolkit \
    && dnf clean all
```

运行 `nvidia-smi` 验证 GPU 可用性。

## 相关概念

- [/concepts/00-introduction.md](/concepts/00-introduction.md)
- [/concepts/01-pass-through.md](/concepts/01-pass-through.md)
- [/concepts/02-workflow.md](/concepts/02-workflow.md)
- [/examples/02-custom-image.md](/examples/02-custom-image.md)
