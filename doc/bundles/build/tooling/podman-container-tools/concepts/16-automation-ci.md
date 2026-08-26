---
type: Concept
title: 自动化与Machine OS
description: automation/目录CI工作流、mac测试池与renovate配置；podman-machine-os构建COREOS/WSL虚拟机镜像
tags: [podman, concept, automation, ci, machine-os, coreos, wsl, rpm-ostree, osbuild, ginkgo, renovate]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources: [{id:"podman-source", resource:"/references/podman-source.md", title:"Podman Container Tools 源码信源登记"}]
---

## automation/ 目录结构

`automation/` 目录（F-100~F-110）包含 Podman 项目完整的 CI/CD 自动化基础设施，确保代码质量、多平台兼容性和发布流程的自动化。该目录是项目工程健康的核心保障。

```text
automation/
├── container-images/    # CI 流水线使用的容器镜像
├── mac_pw_pool/         # macOS 测试密码池管理
├── renovate/            # Renovate 依赖更新配置
└── ...                  # CI 脚本、工作流定义
```

automation 目录下的内容主要分为四大类：
1. **CI 工作流脚本**：定义 PR 验证、镜像构建、发布等自动化流程
2. **container-images/**：CI 环境自身使用的容器镜像
3. **mac_pw_pool/**：macOS CI 测试环境的密码池管理
4. **renovate/**：自动化依赖更新配置

## CI 工作流

Podman CI 流水线定义了多类自动化工作流，覆盖代码从提交到发布的完整生命周期：

| 工作流 | 触发时机 | 主要任务 |
|--------|---------|---------|
| **build_images** | CI 镜像变更、定期 | 构建和更新 CI 使用的容器镜像 |
| **pr** | Pull Request 提交/更新 | 代码编译、单元测试、集成测试、静态检查 |
| **release** | 版本 tag 推送 | 构建发布二进制、跨平台编译、发布镜像 |
| **validate** | PR 提交、定期 | 代码格式、lint、DCO 签名检查、文档验证 |

### PR 验证流程

每个 Pull Request 会触发自动化验证：
1. **编译检查**：在多个 Linux 发行版、macOS 上编译，确保无编译错误
2. **单元测试**：运行 Go 单元测试，验证核心逻辑
3. **集成测试**：运行容器相关的端到端测试
4. **静态分析**：go vet、golangci-lint 等静态检查
5. **跨架构测试**：通过 QEMU 模拟在非 x86 架构上测试
6. **rootless 测试**：专门验证 rootless 模式功能
7. **DCO 检查**：验证所有 commit 都有 Signed-off-by 签名

### 发布流程

版本发布时自动化执行：
1. 为所有支持平台（Linux/Windows/macOS）交叉编译二进制
2. 构建官方容器镜像（调用 image_build 系统）
3. 生成 SBOM（软件物料清单）
4. 签名发布产物
5. 发布到 GitHub Releases、quay.io 等渠道
6. 更新文档和发布说明

## container-images/：CI 镜像

`automation/container-images/` 目录构建 CI 流水线自身使用的容器镜像，这些镜像预安装了 Podman 构建和测试所需的所有依赖：

**CI 镜像的作用**：
- **环境一致性**：所有 CI runner 使用相同的构建环境，消除"在我机器上能跑"问题
- **速度优化**：预安装依赖，避免每次 CI 运行都从零安装
- **隔离性**：容器化 CI 环境，不污染宿主机

CI 镜像通常包含：
- Go 工具链（特定版本）
- 容器运行时（crun/runc/conmon）
- 构建依赖（libdevmapper、btrfs-progs 等开发头文件）
- 测试工具（ginkgo、bats 等测试框架）
- 网络工具（netavark、aardvark-dns）
- QEMU 用户态模拟器（跨架构测试）

## mac_pw_pool/：Mac 测试密码池

`automation/mac_pw_pool/`（F-106）管理 macOS CI 测试环境的密码池。macOS 上测试 Podman（特别是 Podman Machine 功能）需要特殊的权限配置：

**为什么需要密码池**：
- macOS CI 测试需要管理员权限来配置虚拟化框架
- Podman Machine 在 macOS 上创建和管理虚拟机需要特权操作
- 多个 CI 任务并行运行时需要安全地分发和管理测试机凭据

密码池机制：
- 维护一组 macOS 测试机的凭据池
- CI 任务调度时从池中获取可用的测试机凭据
- 测试完成后归还凭据
- 确保测试环境的安全隔离和凭据轮换

## renovate/：依赖更新配置

`automation/renovate/`（F-109）包含 Renovate Bot 的配置，Renovate 是一个自动化依赖更新工具：

**自动化依赖更新的作用**：
- 自动检测 Go 模块依赖的新版本
- 自动检测容器镜像引用的新版本
- 自动创建 PR 更新依赖
- 自动运行 CI 测试验证更新兼容性

Renovate 配置管理的依赖类型：
- **Go 模块依赖**：go.mod 中的第三方库更新
- **容器镜像引用**：Containerfile 和 CI 配置中的镜像标签更新
- **GitHub Actions**：CI 工作流使用的 Action 版本更新
- **基础镜像**：CI 镜像的基础镜像（如 Fedora 版本）更新

自动依赖更新的好处：
- 及时获得安全补丁
- 减少手动更新依赖的维护负担
- 通过 CI 自动验证更新是否引入破坏性变更
- 保持依赖版本处于维护期内

## podman-machine-os/：Machine OS 构建系统

`podman-machine-os/` 目录（F-400~F-415）是一个相对独立的子项目，负责构建 Podman Machine 使用的虚拟机磁盘镜像。Podman 在 macOS 和 Windows 上通过轻量级虚拟机运行 Linux 容器，这些虚拟机使用的操作系统镜像由此目录构建。

### 为什么需要 Machine OS

- macOS 和 Windows 内核原生不支持 Linux 容器特性（cgroup、namespace 等）
- Podman 通过启动一个轻量级 Linux 虚拟机来提供容器运行环境
- 虚拟机需要一个经过优化、预配置的 Linux 客户机镜像
- podman-machine-os 专门构建这种"Podman 专用"虚拟机镜像

### build.sh：构建入口

`build.sh` 是 Podman Machine OS 构建的入口脚本（F-404）：

```bash
# 构建脚本基本用法（概念示意）
cd podman-machine-os/
sudo ./build.sh <type>
# type: coreos | wsl
```bash

**构建前提条件**：
- 必须在 Linux 环境下运行构建
- 必须以 root 权限运行（F-405：需要 root 权限来操作镜像构建工具、挂载文件系统、创建磁盘镜像）
- 需要安装 rpm-ostree 和 osbuild 等构建依赖
- 需要足够的磁盘空间和 QEMU 虚拟化支持

### 构建依赖

podman-machine-os 构建依赖以下核心工具：

| 依赖 | 作用 |
|------|------|
| **rpm-ostree** | 基于 rpm 的原子化操作系统构建工具，用于构建不可变的操作系统镜像 |
| **osbuild** | OS 镜像构建框架，定义镜像构建流水线，支持多种输出格式 |
| **qemu** | 模拟器，用于镜像验证和启动测试 |
| **podman/buildah** | 构建过程中使用的容器工具 |
| **coreos-installer** | Fedora CoreOS 镜像安装工具 |

rpm-ostree 构建的操作系统特点：
- **不可变**：系统文件只读，更新通过原子化部署进行
- **事务性更新**：更新要么全部成功要么回滚，不会出现部分更新状态
- **容器友好**：预配置容器运行时所需的内核模块和配置

### 两种镜像类型

podman-machine-os 构建两种虚拟机镜像，分别对应不同平台：

| 镜像类型 | 目标平台 | 基础 | 磁盘格式 |
|---------|---------|------|---------|
| **COREOS 镜像** | macOS（Podman Machine 默认）、Linux | Fedora CoreOS | qcow2（QEMU 磁盘格式） |
| **WSL 镜像** | Windows（WSL2 后端） | Fedora 基础 | tar.gz（WSL 分发格式） |

#### COREOS 镜像（macOS/Linux）

基于 Fedora CoreOS 构建：
- 使用 rpm-ostree 定制，加入 Podman 运行所需包
- qcow2 格式，适配 QEMU 和 Apple Hypervisor
- 预配置 podman.sock，支持宿主机 podman-remote 连接
- 自动配置端口转发和文件共享
- 支持 vz 虚拟化框架（macOS 13+）和 QEMU 两种后端

镜像预装内容：
- Podman、Buildah、Skopeo 全套工具
- crun/runc 容器运行时
- netavark 网络栈 + aardvark-dns
- conmon 容器监控
- fuse-overlayfs（存储驱动）
- gvisor-tap-vsock（虚拟机网络）
- SSH 服务（用于宿主机通信）

#### WSL 镜像（Windows）

为 Windows Subsystem for Linux 2 构建：
- tar.gz 格式，可通过 `wsl --import` 导入
- 针对 WSL2 环境优化配置
- 预配置 systemd 支持（WSL2 特有配置）
- 自动处理 Windows 路径转换（/mnt/c 等）
- 与 Docker Desktop WSL 后端类似但更轻量

### verify/：镜像验证测试

`verify/` 目录（F-415）包含 Go 语言编写的镜像验证测试，使用 Ginkgo BDD 测试框架：

**验证测试内容**：
- 镜像是否可以成功启动
- Podman 服务是否在虚拟机内正常运行
- 基本容器操作是否可用（run、ps、build 等）
- 网络连通性是否正常
- 卷挂载是否工作
- 端口转发是否正确
- rootless 模式功能
- API socket 是否可访问

**测试流程**：
1. 使用 QEMU 启动刚构建好的镜像
2. 等待虚拟机 SSH 服务就绪
3. 通过 SSH 连接到虚拟机
4. 执行一系列 ginkgo 测试用例
5. 收集测试结果
6. 关闭虚拟机
7. 报告测试通过/失败

Ginkgo 测试框架的优势：
- BDD（行为驱动开发）风格，测试可读性好
- 丰富的匹配器和断言库
- 支持并行测试
- 测试报告结构化输出

```go
// verify 测试示例（概念示意）
var _ = Describe("Machine OS", func() {
    It("should be able to run a container", func() {
        session := ssh.Run("podman run --rm alpine echo hello")
        Expect(session.ExitCode()).To(Equal(0))
        Expect(string(session.Out.Contents())).To(ContainSubstring("hello"))
    })

    It("should have podman socket accessible", func() {
        session := ssh.Run("systemctl is-active podman.socket")
        Expect(session.ExitCode()).To(Equal(0))
    })
})
```bash

## 自动化基础设施的工程价值

Podman 的自动化基础设施体现了成熟开源项目的工程实践：

### 质量保障
- 每次 PR 都经过多平台、多架构、多配置的全面测试
- rootless 模式有专门测试，确保核心安全特性不退化
- 镜像发布前经过自动化验证，防止"无法启动"的坏镜像流出

### 跨平台支持
- macOS 测试池确保 Apple 生态兼容性
- QEMU 跨架构测试覆盖 ARM、Power、Z 系列
- WSL 镜像测试覆盖 Windows 用户场景

### 供应链安全
- Renovate 自动更新依赖，及时应用安全补丁
- 镜像构建可复现，从源码到镜像全链路可追溯
- 官方镜像带审计标签（built.by、vcs-ref 等）

### 开发者体验
- CI 镜像预配置所有依赖，新贡献者可快速上手
- 自动化测试减少手动验证负担
- 自动化发布流程保证版本发布的一致性

## 与 image_build 的关系

`automation/` 和 `image_build/` 是两个不同的镜像构建系统，职责明确区分：

| 维度 | automation/container-images | image_build/ |
|------|----------------------------|-------------|
| **目标** | CI 流水线内部使用的镜像（用于构建和测试 Podman） | 发布给最终用户的官方镜像（Podman/Buildah/Skopeo 可执行镜像） |
| **用户** | Podman CI 系统 | Podman 最终用户 |
| **内容** | Go 工具链、编译依赖、测试工具 | Podman/Buildah/Skopeo 运行时 |
| **发布位置** | CI registry（内部） | quay.io/containers/（公开） |
| **构建触发** | CI 配置变更 | 版本发布 |

两者共享底层构建技术（buildah/podman/QEMU 多架构构建），但服务于不同的工程目标。

## 相关概念

- [容器工具生态全景](/concepts/14-ecosystem.md) — automation/community/image_build/podman-machine-os五大子目录概览
- [官方镜像构建](/concepts/15-image-build.md) — image_build/用户镜像构建与automation/CI镜像的对比
- [架构概览](/concepts/02-architecture-overview.md) — Podman Machine虚拟机在跨平台架构中的角色
- [无Root容器](/concepts/10-rootless.md) — Machine OS镜像中的rootless模式预配置
