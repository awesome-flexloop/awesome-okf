---
type: bundle
title: Toolbx 交互式容器开发环境
okf_version: "0.2"
---

# Toolbx 知识库

本知识包是 [Toolbx](https://containertoolbx.org/)（曾用名 Toolbox，Apache-2.0 许可证）的系统化中文源码教程，基于 Toolbx Go 源码（`external/dao/action/Containers/toolbox/` 目录）深度阅读生成。Toolbx 是构建在 Podman 和 OCI 容器技术之上的交互式命令行环境工具，专为 OSTree 不可变系统（Fedora Silverblue/CoreOS）设计，提供完全可变的特权容器用于软件开发和主机故障排查，同时在传统发行版上同样适用。本知识包覆盖从 OSTree 背景、10 类主机资源透传机制，到 create/enter/run 日常工作流、自定义镜像构建的完整知识体系。所有内容均溯源至 Toolbx Go 源码和官方文档，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 快速入门篇（concepts/）

* [Toolbx 定位与 OSTree 不可变系统背景](concepts/00-introduction.md) — 规范名称 Toolbx（二进制/仓库仍为 toolbox）、Go 1.22.0、github.com/containers/toolbox 模块路径；OSTree 不可变系统核心约束（/usr 只读、无传统 dnf 工作流、原子更新）；Toolbx 解决方案（完全可变特权容器，可自由 dnf install 不影响主机）；非 OSTree 系统同样适用；Podman + OCI 技术栈选型；透传优于隔离的设计哲学；与 Docker 普通容器、Distrobox 的区别对比；7 个核心 Go 依赖（cobra/viper/logrus/dbus/nvlib 等）。
* [主机资源透传机制](concepts/01-pass-through.md) — 10 类透传资源详解：用户主目录（读写 bind mount，dotfiles/Git 直接可用）、当前工作目录（自动 cwd 切换）、Wayland/X11 图形套接字（图形应用直接运行）、共享主机网络（--net=host，Avahi/CA 证书可用）、SSH agent（SSH_AUTH_SOCK 挂载）、D-Bus 会话/系统总线（notify-send/journalctl 可用）、systemd journal、ulimits 资源限制、/dev 设备与 udev 数据库（USB/GPU 透传）、可移动设备；环境变量透传清单；/run/host 万能逃生口挂载实现（--volume /:/run/host:rslave）；容器内标识（⬢ 提示符、/run/.containerenv + /run/.toolboxenv 判断）；rootless 模式 UID 映射安全模型。

## 核心工作流篇（concepts/）

* [日常开发工作流（create/enter/run）](concepts/02-workflow.md) — 三大核心命令详解：`toolbox create`（--distro/--release/--image/-c 容器命名选项、默认命名规则 `<distro>-toolbox-<release>`、首次镜像拉取、-y 无提示模式）、`toolbox enter`（交互式进入、提示符变化、exit 离开不删除容器、自动创建行为）、`toolbox run`（非交互式单命令执行、Shell 脚本集成、管道与重定向无缝配合）；生命周期管理：`list -c/-i` 列出容器镜像、`rm [-f/-a]` 删除容器、`rmi [-f/-a]` 删除镜像；最佳实践：单容器 vs 多容器策略、Shell 别名简化、进入即工作模式、全局选项 -v/-vv 排障；完整命令速查表（10 个常用操作）。
* [自定义镜像与 /run/host 逃生口](concepts/03-custom-images.md) — 自定义镜像适用场景（团队统一环境、预装工具链、企业 CA、特殊发行版）；Toolbx 镜像必备特征（POSIX shell、sudo、shadow-utils、/run/host 挂载点、com.github.containers.toolbox=true 标签、UID/GID 映射约定）；三种构建方式（基于官方 fedora-toolbox 镜像扩展推荐、从 fedora/ubuntu 基础镜像从头构建、社区工具）；官方 images/ 目录 Containerfile 参考（fedora/rhel/ubuntu/arch 子目录）；Containerfile 编写示例；/run/host 5 个高级场景：访问主机系统目录、chroot 故障排查（Silverblue 经典用法）、调用主机二进制、共享包缓存、跨容器共享；镜像优化：版本标签策略、分层缓存、多阶段构建、dnf clean all 同层清理、.containerignore；预装 vs dotfiles vs 容器内手动安装决策矩阵；NVIDIA GPU CDI 支持。

## 实战示例（examples/）

* [创建第一个开发容器](examples/01-first-toolbox.md) — Fedora Silverblue/Workstation/Arch/Ubuntu 多平台安装方法；`toolbox create` 默认容器创建全流程（首次镜像下载确认、默认命名）；`toolbox enter` 进入与 ⬢ 提示符识别；容器内 `sudo dnf install` 安装 gcc/gdb/Go/Python/Node.js/git/vim 完整工具链；C 程序编译验证（编译产物主机直接可见）；Firefox 图形应用运行验证；`toolbox run go version` 非交互式执行；主机 build.sh 脚本透明调用容器内 Go 编译；exit 离开容器与持久化验证；`toolbox list/rm/rmi` 生命周期管理；subuid/subgid 范围配置、镜像慢、图形应用无法启动等常见问题排查；10 项验证检查清单。
* [构建自定义 Toolbx 镜像](examples/02-custom-image.md) — 基于官方 fedora-toolbox:39 扩展编写 Containerfile 完整示例（LABEL 标签、sudo dnf 安装、/etc/profile.d/go-dev.sh 环境变量、Vim 全局配置）；`podman build -t localhost/go-dev-toolbox:v1.0.0` 构建流程；`toolbox create -i <image> -c go-dev` 自定义镜像容器创建；6 项功能验证（Go 版本、GOPATH/PATH 环境变量、ripgrep/gdb 工具链、主目录/SSH/网络/run/host/sudo 透传、实际 Go 项目编译运行、gopls/dlv/staticcheck 工具安装）；GOPATH/bin 主目录持久化特性说明（容器删除不丢失）；镜像版本更新与新旧容器并行；4 项镜像优化技巧（多阶段构建、分层缓存顺序、dnf clean 同层清理、.containerignore）；推送到 Quay.io 远程 registry 团队共享；Ubuntu/Debian 基础镜像注意事项；6 项验证清单。

## 信源登记簿（references/）

* [README.md 项目概览与定位](references/readme-source.md) — `README.md`、`doc/toolbox.1.md`：项目规范名称 Toolbx（Toolb**x**，曾用名 Fedora Toolbox/Toolbox）、二进制名 `toolbox`、Go 1.22.0 要求、Apache-2.0 许可证；OSTree 系统问题背景（Fedora CoreOS/Silverblue）；10 项主机资源透传清单；4 个支持发行版（Arch/Fedora/RHEL ≥8.5/Ubuntu）及版本格式；fedora-toolbox 默认镜像；/run/host 主机文件系统挂载；安全边界说明；名称迁移现状（仓库/二进制/包名仍用 toolbox）。
* [src/cmd/ 命令行接口与核心命令](references/cmd-source.md) — `src/cmd/root.go`、`src/cmd/create.go`、`src/cmd/enter.go`、`src/cmd/run.go`、`src/go.mod`：cobra CLI 框架；rootCmd 根命令定义（Use/Short/Version/PersistentPreRunE）；4 个全局选项（-y/--assumeyes、--log-level、--log-podman、-v/-vv verbose）；7 个核心子命令（create/enter/run/list/rm/rmi/completion）及常用选项；src/cmd/ 目录 14 个 Go 源文件清单；8 个内部 pkg 包结构（podman/shell/utils/term/nvidia/skopeo/version）；10 个主要 Go 依赖（cobra/viper/logrus/dbus/v5/nvlib/spinner/osrelease 等）；Meson 构建系统（meson.build、go-build-wrapper）；二进制入口 src/toolbox.go 调用 cmd.Execute()。

## 信任与生命周期说明

* **status 判定依据**：全部 8 个内容文档（4 个概念 + 2 个示例 + 2 个信源登记）均 `status: stable`。内容基于对 Toolbx 源码（`src/cmd/` 目录、`src/go.mod`、`README.md`、`doc/toolbox.1.md`、`images/` 目录 Containerfile）的逐文件阅读与事实提取（15 条源码事实），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-26`。Toolbx 核心命令接口（create/enter/run/list/rm/rmi）、透传机制设计和镜像规范自项目确立以来保持高度稳定；该日期作为针对未来大版本（如命令行接口破坏性变更、镜像规范升级）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（rootCmd/cobra.Command、create/enter/run/list/rm/rmi 命令、go.mod 依赖版本、透传资源清单等关键信息逐一比对源码），两者分离、可追溯。

本知识包共收录 8 个内容文档（4 个概念 + 2 个示例 + 2 个信源登记），另含 3 个子目录 index.md、根 index.md 与 log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
