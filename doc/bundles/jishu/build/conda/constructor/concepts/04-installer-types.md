---
type: concept
title: "安装程序类型"
description: "constructor 支持的五种安装程序类型（sh/pkg/exe/msi/docker）的详细说明、平台限制、特性对比和选型指南。"
tags: [安装程序类型, sh, pkg, exe, msi, docker, 跨平台, 选型]
status: stable
stale_after: 2027-12-31
level: beginner
prerequisites: ["00-introduction", "01-getting-started"]
reading_time: 10
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-main
    resource: "constructor/main.py"
---

# 安装程序类型

constructor 支持五种安装程序类型，每种类型对应不同的操作系统和安装体验。你可以通过 `installer_type` 配置字段或 `--installer-type` 命令行参数来选择。

## 类型概览

| 类型 | 格式 | 平台 | 安装体验 | GUI | 模块 |
|------|------|------|---------|-----|------|
| `sh` | Shell 自解压脚本（.sh） | Linux, macOS | 命令行/终端交互 | ❌ | [shar.py](../references/shar-installer.md) |
| `pkg` | macOS Installer 包（.pkg） | macOS | 原生 GUI 安装向导 | ✅ | osxpkg.py |
| `exe` | NSIS 安装程序（.exe） | Windows | 原生 GUI 安装向导 | ✅ | [winexe.py](../references/winexe-installer.md) |
| `msi` | Windows Installer（.msi） | Windows | 原生 MSI 向导 | ✅ | briefcase.py（实验性） |
| `docker` | Dockerfile + Docker 镜像 | Linux | Docker 部署 | — | docker_build.py |

## 平台-类型映射

constructor 根据当前构建平台自动确定可用的安装程序类型：

```python
os_allowed = {
    "linux": ("sh",),                                    # Linux 仅 sh
    "osx":   ("sh", "pkg"),                              # macOS: sh + pkg
    "win":   ("exe", "msi"),                             # Windows: exe + msi
}
```

| 构建平台 | 默认类型 | `installer_type: all` 构建 |
|---------|---------|---------------------------|
| Linux | `sh` | `.sh` + Dockerfile（如配置 docker_base_image） |
| macOS | `sh` + `pkg` | `.sh` + `.pkg` |
| Windows | `exe` | `.exe` |

## 各类型详解

### sh — Shell 自解压安装程序

sh 类型生成一个 `.sh` 文件，它是一个纯 shell 脚本，头部包含安装逻辑，尾部以二进制追加 tarball 数据。

**适用平台**：Linux、macOS

**特性**：
- ✅ 无需 root 权限（可安装到用户目录）
- ✅ 支持交互模式和批处理模式（`-b`）
- ✅ 跨平台（同一脚本可在 Linux/macOS 运行，匹配各自架构）
- ✅ 文件体积小（shell 脚本头部仅数千行）
- ❌ 无 GUI（终端界面）
- ❌ 不支持自定义页面/向导步骤

**命令行选项**：
```bash
bash installer.sh -b -p ~/mypython   # 批处理安装到指定路径
bash installer.sh -u                  # 更新现有安装
bash installer.sh -k                  # 保留包缓存
```

**模板**：[`constructor/header.sh`](../references/shar-installer.md) 是 Jinja2 模板，在构建时渲染为最终的 shell 脚本。

### pkg — macOS PKG 安装程序

pkg 类型使用 Apple 的 `pkgbuild` 和 `productbuild` 工具创建原生 `.pkg` 安装包，提供标准的 macOS 安装向导体验。

**适用平台**：macOS（必须在 macOS 上构建）

**特性**：
- ✅ 原生 macOS 安装向导（引导式界面）
- ✅ 支持代码签名（`signing_identity_name`）和公证（`notarization_identity_name`）
- ✅ 支持"仅我"和"所有用户"安装域
- ✅ 支持欢迎页、README、许可协议、完成页自定义
- ✅ 支持安装后自定义页面插件（Xcode项目）
- ❌ 只能在 macOS 上构建
- ❌ 不支持跨平台构建

**自定义页面**：通过 `welcome_file`、`readme_file`、`conclusion_file` 添加 .txt/.rtf/.html 内容；通过 `post_install_pages` 添加编译后的 installer 插件。

### exe — Windows NSIS 安装程序

exe 类型使用 NSIS（Nullsoft Scriptable Install System）创建 `.exe` GUI 安装程序，是 Windows 平台的默认和推荐类型。

**适用平台**：Windows

**特性**：
- ✅ 原生 Windows GUI 安装向导
- ✅ 支持"Just Me"和"All Users"双模式
- ✅ UAC 权限提升
- ✅ PATH 环境变量管理
- ✅ Python 注册（写入注册表）
- ✅ 自定义 NSIS 页面和脚本
- ✅ 代码签名（signtool/azuresigntool）
- ✅ 开始菜单快捷方式管理
- ✅ 支持静默安装（`/S`）
- ❌ 需要 makensis.exe（NSIS 编译器）

**静默安装选项**：
```cmd
installer.exe /S /D=C:\mypython /AddToPath=1 /RegisterPython=0
```

**自定义 NSIS 页面**：通过 `welcome_file`（.nsi）、`post_install_pages`（.nsi列表）、`conclusion_file`（.nsi）插入自定义页面。

### msi — Windows MSI 安装程序（实验性）

msi 类型使用 Briefcase 和 WiX Toolset 创建 `.msi` 安装包，提供标准的 Windows Installer 体验。

**适用平台**：Windows

**特性**：
- ✅ Windows Installer 标准格式（企业部署友好）
- ✅ 支持组策略部署
- ⚠️ 实验性功能（constructor 文档明确标注 experimental）
- ❌ 不支持自定义 NSIS 模板
- ❌ 需要 briefcase WiX backend

选择 msi 还是 exe？
- **企业环境**（组策略部署、SCCM）：选 msi
- **普通用户分发**：选 exe（更成熟、更灵活）

### docker — Docker 镜像

docker 类型生成 Dockerfile 和可选的 Docker 镜像 tar 包，用于容器化部署。

**适用平台**：Linux（构建和运行）

**特性**：
- ✅ 生成 Dockerfile（可自定义 base image）
- ✅ 支持构建并导出 Docker 镜像为 tar 包
- ✅ 自动设置 OCI 标签（`org.opencontainers.image.title/version`）
- ❌ 必须提供 `docker_base_image`
- ❌ 必须在有 Docker 或 buildx 的环境构建
- ❌ 仅支持 Linux 容器

**最小配置**：
```yaml
installer_type: docker
docker_base_image: debian:bookworm-slim
specs:
  - python
```

构建后可使用：
```bash
# 加载导出的镜像
docker load -i myenv-1.0-Linux-x86_64-docker.tar

# 或使用生成的 Dockerfile 自行构建
docker build -t myenv:1.0 .
```

## 选择指南

| 场景 | 推荐类型 | 理由 |
|------|---------|------|
| Linux 服务器/CI 部署 | `sh` | 轻量、批处理、无 X11 依赖 |
| macOS 开发者分发 | `pkg` + `sh` | 为普通用户提供 GUI（pkg），为高级用户提供脚本（sh） |
| Windows 桌面用户 | `exe` | 成熟的 NSIS 方案，功能丰富 |
| Windows 企业批量部署 | `msi` | Windows Installer 标准，GPO 友好 |
| 容器化/微服务 | `docker` | 镜像直接部署 |
| 跨平台单安装包 | 各平台各自构建 | constructor 不生成跨平台的单一安装程序 |

## 多类型同时构建

可以通过列表或 `all` 关键字同时构建多种类型：

```yaml
installer_type: all     # macOS 上生成 .sh + .pkg
# 或
installer_type: [sh, pkg]
```

也可在命令行指定：

```bash
constructor . --installer-type all
```

当构建多种类型时，`process_build_outputs()` 会自动处理 `info` 字典中不同类型特有的键值（如 pkg 有而 sh 没有的字段，会以列表形式存储）。

## 交叉构建

constructor 支持在一种平台上构建另一种平台的安装程序：

```bash
# 在 Linux 上构建 Windows 安装程序
constructor . --platform win-64 --conda-exe /path/to/conda.exe
```

**限制**：
- macOS pkg 安装程序**不能**在非 macOS 平台构建（需要 pkgbuild 工具）
- 交叉构建必须显式提供 `--conda-exe`（指向目标平台的 conda-standalone）
- 目标平台的 conda-standalone 必须能在构建机器上运行（通常需要 QEMU/Wine 等模拟）
- Docker 构建始终在 Linux 上进行

## 下一步

- [05-CLI 命令行入口](05-cli-and-entrypoint.md)：了解如何通过命令行控制安装程序构建
- [09-平台安装器实现](09-platform-installers.md)：深入各平台模块的实现细节
