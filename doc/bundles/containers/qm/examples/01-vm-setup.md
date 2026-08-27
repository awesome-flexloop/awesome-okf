---
type: Example
title: 创建 QM 虚拟机环境
description: 在 QEMU/KVM 虚拟机中安装 CentOS Automotive Stream Distribution (AutoSD) 并设置 QM 环境的完整步骤
tags: [qemu, kvm, vm, setup, installation, autosd]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: readme
    resource: /bundles/containers/qm/references/readme-source.md
    title: "QM 项目 README 与 man 手册信源"
  - id: qmctl
    resource: /bundles/containers/qm/references/qmctl-source.md
    title: "qmctl 管理工具信源"
---

# 创建 QM 虚拟机环境

本示例展示如何在 QEMU/KVM 虚拟机中安装 CentOS Automotive Stream Distribution (AutoSD) 并完整设置 QM 容器环境。这是学习和测试 QM 的推荐方式，不会影响主机系统。

## 前置条件

### 主机环境要求

- Linux 主机（推荐 Fedora 38+/CentOS Stream 9+）
- 启用 KVM 硬件虚拟化
- 至少 4GB RAM 分配给虚拟机（推荐 8GB）
- 至少 20GB 磁盘空间
- 已安装 `qemu-kvm`、`libvirt`、`virt-install`

### 主机安装虚拟化工具（Fedora/CentOS）

```bash
# Fedora
sudo dnf install @virtualization

# CentOS Stream 9
sudo dnf groupinstall "Virtualization Host"
sudo dnf install qemu-img virt-viewer

# 启动并启用 libvirtd
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt $USER
newgrp libvirt
```

### 下载 AutoSD 镜像

从 CentOS Automotive SIG 下载最新的 AutoSD QEMU 镜像：

```bash
# 创建工作目录
mkdir -p ~/qm-vm && cd ~/qm-vm

# 下载 AutoSD qcow2 镜像（示例 URL，请从官方镜像站获取最新版本）
# 官方镜像站：https://mirror.stream.centos.org/SIGs/9-stream/automotive/
wget https://mirror.stream.centos.org/SIGs/9-stream/automotive/aarch64/images/
# 或 x86_64:
# wget https://mirror.stream.centos.org/SIGs/9-stream/automotive/x86_64/images/

# 注：如果直接下载镜像不可用，也可以使用 AutoSD ISO 安装
```

> **提示**：也可以使用标准 CentOS Stream 9 安装 QM，不一定需要 AutoSD。AutoSD 是预配置了汽车相关包的发行版。

## 方法一：使用 QEMU 直接启动（快速测试）

### 步骤 1：创建支持后端存储的 qcow2 镜像

```bash
cd ~/qm-vm

# 创建后端镜像（如果下载了基础镜像）
qemu-img create -f qcow2 -b autosd-base.qcow2 -F qcow2 qm-vm.qcow2 20G

# 或者创建全新空白镜像（使用 ISO 安装）
qemu-img create -f qcow2 qm-vm.qcow2 20G
```

### 步骤 2：使用 QEMU 启动虚拟机

```bash
qemu-system-x86_64 \
  -enable-kvm \
  -m 4G \
  -smp 2 \
  -cpu host \
  -drive file=qm-vm.qcow2,if=virtio \
  -net nic,model=virtio \
  -net user,hostfwd=tcp::2222-:22 \
  -vga virtio \
  -display gtk \
  -boot d
```

参数说明：
- `-enable-kvm`：启用 KVM 硬件加速
- `-m 4G`：分配 4GB 内存
- `-smp 2`：分配 2 个 vCPU
- `-net user,hostfwd=tcp::2222-:22`：端口转发，主机 2222 → 虚拟机 22（SSH）
- `-display gtk`：使用 GTK 显示窗口

### 步骤 3：SSH 登录虚拟机

```bash
# 默认用户名密码根据镜像版本不同，AutoSD 通常有 root 或默认用户
ssh -p 2222 root@localhost
# 或使用普通用户
```

## 方法二：使用 virt-install（推荐）

### 步骤 1：创建虚拟机

```bash
cd ~/qm-vm

# 创建磁盘镜像
qemu-img create -f qcow2 qm-vm.qcow2 20G

# 使用 virt-install 安装（使用 ISO）
sudo virt-install \
  --name qm-test \
  --memory 4096 \
  --vcpus 2 \
  --disk qm-vm.qcow2 \
  --cdrom CentOS-Stream-9-latest-x86_64-dvd1.iso \
  --os-variant centos-stream9 \
  --network default \
  --graphics vnc,listen=0.0.0.0 \
  --noautoconsole
```

### 步骤 2：完成 OS 安装

使用 `virt-viewer` 或 VNC 客户端连接虚拟机完成安装：

```bash
virt-viewer qm-test
```

安装时选择 "Minimal Install" 或 "Server" 环境即可。

## 在虚拟机中安装 QM

### 步骤 1：登录虚拟机

```bash
# 获取虚拟机 IP
virsh domifaddr qm-test

# SSH 登录（替换为实际 IP）
ssh root@<vm-ip-address>
```

### 步骤 2：启用 CRB 仓库（CentOS Stream 9）

```bash
# CentOS Stream 9 需要启用 Code Ready Builder 仓库
dnf install -y python3-dnf-plugins-core
dnf config-manager --set-enabled crb

# 对于 AutoSD，仓库可能已预配置
```

### 步骤 3：安装 QM 包

```bash
# 安装 QM 主包
dnf install -y qm

# 验证包已安装
rpm -q qm
```

### 步骤 4：运行 QM 设置脚本

安装完成后，必须运行 setup 脚本来初始化 QM 环境：

```bash
# 运行 setup 脚本（这会安装 rootfs 包）
/usr/share/qm/setup
```

setup 脚本会自动执行以下操作：
1. 在 `/usr/lib/qm/rootfs/` 安装 selinux-policy-targeted、podman、systemd、bluechi 等包
2. 启用并启动 qm.service（Podman Quadlet）
3. 配置 SELinux 策略

> **注意**：setup 脚本可能需要几分钟时间，因为它要下载并安装完整的 rootfs 包。

### 步骤 5：验证 QM 服务运行

```bash
# 查看 qm.service 状态
systemctl status qm.service
```

预期输出（关键部分）：

```
● qm.service - QM Container
     Loaded: loaded (/etc/containers/systemd/qm.container; generated)
     Active: active (running) since ...
   Main PID: ... (conmon)
```

### 步骤 6：验证 QM 环境

```bash
# 1. 进入 QM 容器
podman exec -ti qm sh

# 2. 验证 SELinux 上下文（应该是 qm_t）
sh-5.2# id -Z
system_u:system_r:qm_t:s0:...

# 3. 验证 PID 1 是独立的 systemd
sh-5.2# ps -p 1
PID  TTY          TIME CMD
  1 ?        00:00:01 systemd

# 4. 验证 QM 内有 Podman
sh-5.2# which podman
/usr/bin/podman

# 5. 测试运行嵌套容器
sh-5.2# podman run --rm ubi9-minimal echo "Hello from nested container!"
Resolved "ubi9-minimal" as alias...
Hello from nested container!

# 退出 QM
sh-5.2# exit
```

### 步骤 7：验证 OOM 分数设置

```bash
# 1. 查看 QM 容器 PID
QM_PID=$(systemctl show -P MainPID qm.service)
echo "QM PID: $QM_PID"

# 2. 查看 QM 容器的 oom_score_adj（应该是 500）
cat /proc/$QM_PID/oom_score_adj
# 输出: 500

# 3. 进入 QM 查看嵌套容器默认配置
podman exec qm cat /usr/share/qm/containers.conf | grep oom_score_adj
# 输出: oom_score_adj = 750
```

## 使用 qmctl 工具管理 QM

qmctl 是 QM 提供的便利管理工具：

```bash
# 如果 qmctl 未在 PATH 中，从源码目录运行
cd /path/to/qm/tools/qmctl
chmod +x qmctl

# 查看 QM 基本信息
./qmctl show

# 查看所有信息
./qmctl show all

# 查看命名空间
./qmctl show namespaces

# 在 QM 内执行命令
./qmctl exec uname -a
./qmctl exec cat /etc/os-release

# 在 QM 和主机之间复制文件
echo "test file" > /tmp/test.txt
./qmctl cp /tmp/test.txt qm:/tmp/
./qmctl exec cat /tmp/test.txt

# 复制回来
./qmctl cp qm:/tmp/test.txt /tmp/test2.txt
cat /tmp/test2.txt
```

## 安装可选子系统（可选）

根据需要安装子系统包：

```bash
# KVM 虚拟化子系统（注意：虚拟机嵌套虚拟化需要主机启用）
# dnf install -y qm-kvm

# Wayland 图形子系统
# dnf install -y qm-wayland

# 音频子系统
# dnf install -y qm-sound

# 视频子系统
# dnf install -y qm-video

# 安装后重启 QM
systemctl daemon-reload
systemctl restart qm.service
```

## 常见问题排查

### 问题 1：setup 脚本下载包失败

检查网络连接，可能需要配置代理：

```bash
# 为 dnf 配置代理
echo "proxy=http://your-proxy:port" >> /etc/dnf/dnf.conf
# 重新运行 setup
/usr/share/qm/setup
```

### 问题 2：qm.service 启动失败

查看日志排查原因：

```bash
# 查看 qm 服务日志
journalctl -u qm.service -b -e

# 检查 SELinux 是否有拒绝
ausearch -m avc -ts recent | audit2why

# 手动运行容器查看错误
podman run --rm --name qm-debug -it --entrypoint /bin/bash /usr/lib/qm/rootfs
```

### 问题 3：无法进入 QM（podman exec 失败）

```bash
# 检查容器是否运行
podman ps -a | grep qm

# 如果容器退出，查看容器日志
podman logs qm

# 重启服务
systemctl restart qm.service
```

### 问题 4：嵌套容器无法拉取镜像

QM 内可能需要配置镜像仓库或代理：

```bash
# 进入 QM
podman exec -ti qm sh

# 配置 registries.conf 或代理
# vi /etc/containers/registries.conf
```

## 验证 BlueChi（可选）

如果安装了 bluechi 相关包，可以验证 BlueChi agent：

```bash
# 在主机上（如果安装了 bluechi-controller）
# bluechictl list-nodes

# 在 QM 内检查 bluechi-agent
podman exec qm systemctl status bluechi-agent
```

## 环境快照与清理

### 关闭虚拟机

```bash
# 优雅关闭
virsh shutdown qm-test

# 强制关闭
virsh destroy qm-test
```

### 创建快照（推荐）

在测试复杂配置前创建快照：

```bash
virsh snapshot-create-as qm-test qm-baseline "QM 安装完成的基础快照"
virsh snapshot-list qm-test
```

### 恢复快照

```bash
virsh snapshot-revert qm-test qm-baseline
```

### 删除虚拟机

```bash
virsh undefine qm-test --nvram --remove-all-storage
rm -f ~/qm-vm/qm-vm.qcow2
```

## 下一步

完成 QM 虚拟机环境搭建后，建议继续阅读：

- [嵌套隔离架构](../concepts/01-nested-architecture.md)：深入了解 QM 架构
- [三级 OOM 策略与 SELinux 隔离](../concepts/02-oom-selinux.md)：测试内存和安全隔离
- [KVM 子系统使用](02-kvm-subsystem.md)：在 QM 中使用 KVM（需要嵌套虚拟化）
