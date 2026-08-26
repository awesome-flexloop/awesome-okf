---
type: Example
title: KVM 子系统使用
description: 在 QM 中启用和使用 KVM 硬件虚拟化子系统，运行嵌套虚拟机的完整步骤
tags: [kvm, virtualization, nested, libvirt, qemu, subsystem]
generated:
  by: "source-code-to-okf-wiki-skill"
  at: "2026-08-26T16:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-26T16:00:00+08:00"
status: stable
stale_after: "2027-08-26"
sources:
  - id: subsystem
    resource: /bundles/containers/qm/references/subsystem-source.md
    title: "QM 子系统扩展信源"
---

# KVM 子系统使用

本示例展示如何安装、配置和使用 QM 的 KVM 子系统，在 QM 隔离环境中运行硬件加速的嵌套虚拟机。KVM 子系统允许在 QM 容器内使用 `/dev/kvm` 设备，运行 QEMU 虚拟机或 libvirt 管理的虚拟机。

## 前置条件

### 主机硬件要求

- CPU 支持硬件虚拟化（Intel VT-x 或 AMD-V）
- **已启用嵌套虚拟化**（如果 QM 本身运行在虚拟机中）
- 额外内存：每个 KVM 虚拟机至少分配 1-2GB

### 检查主机 KVM 支持

```bash
# 检查 CPU 虚拟化支持
egrep -c '(vmx|svm)' /proc/cpuinfo
# 输出 > 0 表示支持

# 检查 KVM 模块是否加载
lsmod | grep kvm
# 预期输出: kvm_intel 或 kvm_amd，以及 kvm 模块

# 检查 /dev/kvm 设备存在
ls -la /dev/kvm
# crw-rw-rw-+ 1 root kvm 10, 232 ... /dev/kvm

# 检查当前用户是否在 kvm 组
groups | grep kvm
```

### 启用嵌套虚拟化（如果在虚拟机中运行 QM）

如果 QM 本身运行在虚拟机内，需要在**宿主机**（运行 QM 虚拟机的主机）启用嵌套虚拟化：

```bash
# Intel CPU
cat /sys/module/kvm_intel/parameters/nested
# 如果输出 N 或 0，需要启用：
sudo modprobe -r kvm_intel
sudo modprobe kvm_intel nested=1
echo "options kvm_intel nested=1" | sudo tee /etc/modprobe.d/kvm-nested.conf

# AMD CPU
cat /sys/module/kvm_amd/parameters/nested
# 如果输出 0，需要启用：
sudo modprobe -r kvm_amd
sudo modprobe kvm_amd nested=1
echo "options kvm_amd nested=1" | sudo tee /etc/modprobe.d/kvm-nested.conf
```

## 安装 KVM 子系统

### 步骤 1：安装 qm-kvm 包

```bash
# CentOS Stream / AutoSD / RHEL
sudo dnf install -y qm-kvm

# 验证包已安装
rpm -q qm-kvm
```

### 步骤 2：检查安装的文件

安装后检查 KVM 子系统文件是否部署到正确位置：

```bash
# 检查主机 drop-in 配置（绑定 /dev/kvm）
ls -la /etc/containers/systemd/qm.container.d/
# 应该有 qm_dropin_mount_bind_kvm.conf

# 查看 drop-in 配置内容
cat /etc/containers/systemd/qm.container.d/qm_dropin_mount_bind_kvm.conf
# 应该包含将 /dev/kvm 绑定挂载到 QM 的配置

# 检查 QM 内的 KVM Quadlet 文件
ls -la /usr/lib/qm/rootfs/etc/containers/systemd/
# 应该有 kvm.container（如果 setup 已运行）

# 如果 kvm.container 不在 QM rootfs，检查子系统安装位置
ls -la /usr/share/qm/kvm/
# ContainerFile, build_kvm_container.sh
```

### 步骤 3：重启 QM 以应用配置

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 重启 QM 服务
sudo systemctl restart qm.service

# 验证 QM 运行
sudo systemctl status qm.service
```

## 验证 KVM 设备在 QM 中可用

### 步骤 1：检查 /dev/kvm 是否在 QM 中

```bash
# 进入 QM
sudo podman exec -ti qm sh

# 在 QM 内检查 /dev/kvm 是否存在
sh-5.2# ls -la /dev/kvm
# crw-rw-rw- 1 root kvm 10, 232 ... /dev/kvm

# 检查 /dev/kvm 设备权限
sh-5.2# test -r /dev/kvm && test -w /dev/kvm && echo "KVM 可读写"
# KVM 可读写

# 检查设备的 SELinux 标签
sh-5.2# ls -Z /dev/kvm
```

### 步骤 2：验证 KVM 加速功能

```bash
# 在 QM 内检查 KVM 能力
sh-5.2# cat /proc/cpuinfo | egrep -c '(vmx|svm)'
# 输出 > 0 表示 vCPU 暴露了虚拟化标志

# 安装 qemu-kvm（如果 QM 内未安装）
sh-5.2# dnf install -y qemu-kvm
# 或从主机安装到 rootfs：
# sudo dnf install --installroot=/usr/lib/qm/rootfs qemu-kvm
```

## 使用 KVM 子系统容器

KVM 子系统提供了一个预构建的容器镜像，包含 QEMU/KVM 运行环境。

### 步骤 1：构建 KVM 容器镜像（如需要）

```bash
# 在主机上，进入 KVM 子系统构建目录
cd /usr/share/qm/kvm/

# 查看 ContainerFile
cat ContainerFile

# 构建 KVM 容器（使用 buildah 或 podman）
# 注意：这是在 QM rootfs 内运行的，需要进入 QM 或使用 --rootfs 选项
sudo podman exec -ti qm sh -c "cd /usr/share/qm/kvm && ./build_kvm_container.sh"
```

### 步骤 2：启动 KVM Quadlet 服务

```bash
# 进入 QM
sudo podman exec -ti qm sh

# 重新加载 systemd（在 QM 内）
sh-5.2# systemctl daemon-reload

# 启用并启动 kvm 服务
sh-5.2# systemctl enable kvm.service
sh-5.2# systemctl start kvm.service

# 检查 KVM 容器状态
sh-5.2# systemctl status kvm.service
sh-5.2# podman ps | grep kvm
```

## 手动在 QM 内运行 QEMU/KVM 虚拟机

不使用预构建容器，也可以直接在 QM 内安装 QEMU 运行虚拟机。

### 步骤 1：在 QM 内安装虚拟化包

```bash
# 从主机安装到 QM rootfs
sudo dnf install --installroot=/usr/lib/qm/rootfs -y \
  qemu-kvm \
  qemu-img \
  libvirt \
  virt-install \
  bridge-utils \
  libguestfs-tools

# 或进入 QM 后安装
sudo podman exec -ti qm sh
sh-5.2# dnf install -y qemu-kvm qemu-img
```

### 步骤 2：准备测试镜像

```bash
# 在主机上准备一个小型测试镜像（如 Alpine Linux）
cd /tmp
wget https://dl-cdn.alpinelinux.org/alpine/latest-stable/releases/x86_64/alpine-virt-3.20-x86_64.iso

# 复制镜像到 QM 内
sudo mkdir -p /var/lib/qm/vm-images/
sudo cp alpine-virt-3.20-x86_64.iso /var/lib/qm/vm-images/

# 或者使用 qmctl 复制
# ./qmctl cp alpine-virt-3.20-x86_64.iso qm:/var/lib/qm/vm-images/
```

### 步骤 3：创建虚拟磁盘

```bash
# 进入 QM
sudo podman exec -ti qm sh

# 创建磁盘镜像目录
sh-5.2# mkdir -p /var/lib/libvirt/images /vm-images
sh-5.2# cd /vm-images

# 创建 qcow2 磁盘
sh-5.2# qemu-img create -f qcow2 test-vm.qcow2 5G
# Formatting 'test-vm.qcow2', fmt=qcow2 cluster_size=65536 ...
```

### 步骤 4：启动 QEMU 虚拟机（无图形模式）

```bash
# 在 QM 内，使用 KVM 加速启动虚拟机
sh-5.2# cd /vm-images
sh-5.2# qemu-system-x86_64 \
  -enable-kvm \
  -m 1G \
  -smp 1 \
  -cpu host \
  -drive file=test-vm.qcow2,if=virtio \
  -cdrom /var/lib/qm/vm-images/alpine-virt-3.20-x86_64.iso \
  -net nic,model=virtio \
  -net user,hostfwd=tcp::2222-:22 \
  -nographic \
  -serial mon:stdio
```

参数说明：
- `-enable-kvm`：启用 KVM 硬件加速
- `-m 1G`：分配 1GB 内存
- `-cpu host`：使用主机 CPU 型号（暴露所有虚拟化特性）
- `-nographic`：无图形模式，输出到串口
- `-serial mon:stdio`：串口重定向到标准 IO
- `hostfwd=tcp::2222-:22`：QM 内 2222 端口转发到虚拟机 22 端口

### 步骤 5：验证 KVM 加速生效

在 QEMU monitor 中（按 Ctrl+A C 切换到 monitor），检查 KVM 状态：

```
(qemu) info kvm
kvm support: enabled
```

或者从另一个终端检查：

```bash
# 在 QM 内检查 QEMU 进程
sudo podman exec qm ps aux | grep qemu
# 确认命令行有 -enable-kvm

# 检查 KVM 模块使用计数（在主机上）
lsmod | grep kvm
# kvm_intel 或 kvm_amd 的 Used by 计数应该增加
```

## 使用 libvirt 管理虚拟机（可选）

如果需要更完整的虚拟化管理，可以在 QM 内运行 libvirt。

### 步骤 1：启动 libvirtd

```bash
# 在 QM 内
sh-5.2# systemctl start libvirtd
sh-5.2# systemctl status libvirtd

# 验证 virsh 工作
sh-5.2# virsh list --all
```

### 步骤 2：使用 virt-install 创建虚拟机

```bash
# 在 QM 内创建虚拟机
sh-5.2# virt-install \
  --name test-vm \
  --memory 1024 \
  --vcpus 1 \
  --disk /vm-images/test-vm.qcow2 \
  --import \
  --os-variant alpinelinux3.20 \
  --network user \
  --graphics none \
  --console pty,target_type=serial
```

### 步骤 3：virsh 基本操作

```bash
# 列出虚拟机
sh-5.2# virsh list --all

# 启动虚拟机
sh-5.2# virsh start test-vm

# 连接到控制台
sh-5.2# virsh console test-vm

# 关闭虚拟机
sh-5.2# virsh shutdown test-vm
```

## 性能对比：KVM 加速 vs 纯软件模拟

在 QM 内使用 KVM 加速和纯 QEMU TCG 模拟的性能差异：

| 指标 | KVM 加速 | QEMU TCG（无 KVM） |
|------|---------|-------------------|
| CPU 性能 | 接近原生（~95%） | 10-20% 原生速度 |
| 启动时间（Alpine） | ~5-10 秒 | ~30-60 秒 |
| 内存开销 | 低（直接映射） | 高（动态翻译） |
| 使用场景 | 实际工作负载 | 仅用于测试/兼容性 |

验证 KVM 是否真正在加速：

```bash
# 在虚拟机内（如果是 Linux），检查是否有虚拟化时钟
dmesg | grep -i kvm
# 或检查系统启动时间
systemd-analyze
```

## 网络配置

QM 内的 KVM 虚拟机网络选项：

### 选项 1：用户模式网络（默认，最简单）

```bash
-net nic,model=virtio -net user
```
- 虚拟机可以访问外网
- 主机/QM 内可以通过端口转发访问虚拟机
- 虚拟机之间不能直接通信
- 无需额外配置

### 选项 2：桥接网络（高级）

需要在主机和 QM 内配置网桥，适用于需要虚拟机直接访问外部网络的场景：

1. 主机配置网桥（通过 QM drop-in 挂载到 QM）
2. QM 内配置 bridge-utils
3. QEMU 使用 `-net bridge` 参数

## 常见问题排查

### 问题 1：QM 内 /dev/kvm 不存在

```bash
# 检查 qm-kvm 包是否安装
rpm -q qm-kvm

# 检查 drop-in 配置是否存在
ls -la /etc/containers/systemd/qm.container.d/qm_dropin_mount_bind_kvm.conf

# 检查主机 /dev/kvm 存在
ls -la /dev/kvm

# 重启 QM
sudo systemctl daemon-reload
sudo systemctl restart qm.service
```

### 问题 2：KVM 设备无权限访问

```bash
# 检查 QM 内 /dev/kvm 权限
sudo podman exec qm ls -la /dev/kvm

# 检查设备 cgroup 允许访问
# 查看 QM 容器的 devices.allow
cat /sys/fs/cgroup/system.slice/qm.service/devices.list

# 如果需要，通过 drop-in 添加设备访问
```

### 问题 3：嵌套虚拟化不工作

```bash
# 在最底层宿主机检查嵌套是否启用
cat /sys/module/kvm_intel/parameters/nested  # Intel
cat /sys/module/kvm_amd/parameters/nested    # AMD
# 必须是 Y 或 1

# 在 QEMU 命令行使用 -cpu host（不要用默认的 qemu64）
```

### 问题 4：虚拟机性能很差

可能没有真正启用 KVM：

```bash
# 检查 QEMU 命令行是否有 -enable-kvm
ps aux | grep qemu | grep enable-kvm

# 在 QEMU monitor 检查
# Ctrl+A C 进入 monitor
(qemu) info kvm
# 应该显示 "kvm support: enabled"
```

### 问题 5：SELinux 阻止 KVM 访问

```bash
# 检查 SELinux AVC 拒绝
sudo ausearch -m avc -ts recent | grep kvm
sudo sealert -a /var/log/audit/audit.log

# 临时设置为 permissive 模式测试（仅限调试）
# sudo setenforce 0
```

## 安全注意事项

1. **设备访问风险**：KVM 子系统将 `/dev/kvm` 暴露给 QM 容器，这允许 QM 内的进程使用硬件虚拟化。在安全关键场景中评估此风险。
2. **嵌套虚拟化风险**：嵌套虚拟化增加攻击面，生产环境谨慎启用。
3. **资源隔离**：通过 cgroups 限制 KVM 虚拟机的 CPU 和内存使用，防止资源耗尽影响 QM 和主机。
4. **镜像来源**：仅使用可信来源的虚拟机镜像。

## 相关示例

- [创建 QM 虚拟机环境](/bundles/containers/qm/examples/01-vm-setup.md)：本示例的前置条件，先搭建 QM 基础环境

## 相关概念

- [子系统扩展](/bundles/containers/qm/concepts/03-subsystems.md)：了解其他子系统（Wayland、ROS2 等）
- [嵌套隔离架构](/bundles/containers/qm/concepts/01-nested-architecture.md)：了解 QM 的设备绑定挂载机制
