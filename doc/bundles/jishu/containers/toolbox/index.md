---
type: bundle
title: Toolbx 交互式容器开发环境
okf_version: "0.2"
---

# Toolbx 知识库

本知识包是 [Toolbx](https://containertoolbx.org/)（曾用名 Toolbox，Apache-2.0 许可证）的系统化中文源码教程，基于 Toolbx Go 源码（`github.com/containers/toolbox`，本地 vendor/toolbox 子模块，锚定 commit `81401f64`）深度阅读生成。Toolbx 是构建在 Podman 和 OCI 容器技术之上的交互式命令行环境工具，专为 OSTree 不可变系统（Fedora Silverblue/CoreOS）设计，提供完全可变的特权容器用于软件开发和主机故障排查，同时在传统发行版上同样适用。本知识包覆盖从 OSTree 背景、10 类主机资源透传机制，到 create/enter/run 日常工作流、自定义镜像构建的完整知识体系。所有内容均溯源至 Toolbx Go 源码和官方文档，遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 快速入门篇（concepts/）

* [Toolbx 定位与 OSTree 不可变系统背景](concepts/00-introduction.md) — 规范名称 Toolbx（二进制/仓库仍为 toolbox）、Go 1.22.0、github.com/containers/toolbox 模块路径；OSTree 不可变系统核心约束（/usr 只读、无传统 dnf 工作流、原子更新）；Toolbx 解决方案（完全可变特权容器，可自由 dnf install 不影响主机）；非 OSTree 系统同样适用；Podman + OCI 技术栈选型；透传优于隔离的设计哲学；与 Docker 普通容器、Distrobox 的区别对比；7 个核心 Go 依赖（cobra/viper/logrus/dbus/nvlib 等）。
* [主机资源透传机制](concepts/01-pass-through.md) — 10 类透传资源详解：用户主目录（读写 bind mount，dotfiles/Git 直接可用）、当前工作目录（自动 cwd 切换）、Wayland/X11 图形套接字（图形应用直接运行）、共享主机网络（--net=host，Avahi/CA 证书可用）、SSH agent（SSH_AUTH_SOCK 挂载）、D-Bus 会话/系统总线（notify-send/journalctl 可用）、systemd journal、ulimits 资源限制、/dev 设备与 udev 数据库（USB/GPU 透传）、可移动设备；环境变量透传清单；/run/host 万能逃生口挂载实现（--volume /:/run/host:rslave）；容器内标识（⬢ 提示符、/run/.containerenv + /run/.toolboxenv 判断）；rootless 模式 UID 映射安全模型。

## 核心工作流篇（concepts/）

* [日常开发工作流（create/enter/run）](concepts/02-workflow.md) — 三大核心命令详解：`toolbox create`（--distro/--release/--image/-c 容器命名选项、默认命名规则 `<distro>-toolbox-<release>`、首次镜像拉取、-y 无提示模式）、`toolbox enter`（交互式进入、提示符变化、exit 离开不删除容器、自动创建行为）、`toolbox run`（非交互式单命令执行、Shell 脚本集成、管道与重定向无缝配合）；生命周期管理：`list -c/-i` 列出容器镜像、`rm [-f/-a]` 删除容器、`rmi [-f/-a]` 删除镜像；最佳实践：单容器 vs 多容器策略、Shell 别名简化、进入即工作模式、全局选项 -v/-vv 排障；完整命令速查表（10 个常用操作）。
* [自定义镜像与 /run/host 逃生口](concepts/03-custom-images.md) — 自定义镜像适用场景（团队统一环境、预装工具链、企业 CA、特殊发行版）；Toolbx 镜像必备特征（POSIX shell、sudo、shadow-utils、/run/host 挂载点、com.github.containers.toolbox=true 标签、UID/GID 映射约定）；三种构建方式（基于官方 fedora-toolbox 镜像扩展推荐、从 fedora/ubuntu 基础镜像从头构建、社区工具）；官方 images/ 目录 Containerfile 参考（fedora/rhel/ubuntu/arch 子目录）；Containerfile 编写示例；/run/host 5 个高级场景：访问主机系统目录、chroot 故障排查（Silverblue 经典用法）、调用主机二进制、共享包缓存、跨容器共享；镜像优化：版本标签策略、分层缓存、多阶段构建、dnf clean all 同层清理、.containerignore；预装 vs dotfiles vs 容器内手动安装决策矩阵；NVIDIA GPU CDI 支持。

## 实现层篇（concepts/，第二轮源码深读）

* [Podman/Skopeo 调用层](concepts/04-podman-argv-layer.md) — Toolbx 作为外部 CLI 编排器的本质：pkg/shell 执行模型、pkg/podman 子命令映射全表、Podman V1/V2 JSON 双形态适配、双标签识别、CheckVersion 版本门控、flatpak-spawn 转发。
* [镜像与发行版名称解析](concepts/05-name-resolution.md) — 4 发行版 Distro 注册表、三级优先级、全限定镜像构造与 release 校验、容器命名、43 个环境变量白名单、libsubid 子 UID/GID 校验、toolbox.conf。
* [podman create argv 全景解剖](concepts/06-create-argv.md) — 14 个 namespace/安全参数、6 条固定挂载、D-Bus systemd 运行时 socket 发现、符号链接分支、拉取确认竞速交互。
* [init-container 运行时引导](concepts/07-init-container.md) — OCI 不可变性反转、引导八步、15 条 rbind、Kerberos/PKCS#11/RPM 配置、初始化戳记协议（fsnotify/轮询/25 秒超时）。
* [单二进制跨发行版](concepts/08-cross-distro-binary.md) — /run/host 动态链接器与 rpath、-z lazy 与 NVIDIA dlopen、CoreOS 双构建标签、版本 -X 注入。
* [NVIDIA CDI GPU 透传](concepts/09-nvidia-cdi.md) — CDI 生成-传递-应用三段式、NVML/Tegra 探测矩阵、无硬件静默降级、create-symlinks/update-ldcache 钩子。
* [Meson 构建、BATS 测试与发行体系](concepts/10-build-and-tests.md) — 多语言 Meson 编排、三 Shell 补全、22 个 BATS 用例文件、内嵌认证 registry、CI 与 Ansible playbook、四族官方镜像。

## 实战示例（examples/）

* [创建第一个开发容器](examples/01-first-toolbox.md) — Fedora Silverblue/Workstation/Arch/Ubuntu 多平台安装方法；`toolbox create` 默认容器创建全流程（首次镜像下载确认、默认命名）；`toolbox enter` 进入与 ⬢ 提示符识别；容器内 `sudo dnf install` 安装 gcc/gdb/Go/Python/Node.js/git/vim 完整工具链；C 程序编译验证（编译产物主机直接可见）；Firefox 图形应用运行验证；`toolbox run go version` 非交互式执行；主机 build.sh 脚本透明调用容器内 Go 编译；exit 离开容器与持久化验证；`toolbox list/rm/rmi` 生命周期管理；subuid/subgid 范围配置、镜像慢、图形应用无法启动等常见问题排查；10 项验证检查清单。
* [构建自定义 Toolbx 镜像](examples/02-custom-image.md) — 基于官方 fedora-toolbox:39 扩展编写 Containerfile 完整示例（LABEL 标签、sudo dnf 安装、/etc/profile.d/go-dev.sh 环境变量、Vim 全局配置）；`podman build -t localhost/go-dev-toolbox:v1.0.0` 构建流程；`toolbox create -i <image> -c go-dev` 自定义镜像容器创建；6 项功能验证（Go 版本、GOPATH/PATH 环境变量、ripgrep/gdb 工具链、主目录/SSH/网络/run/host/sudo 透传、实际 Go 项目编译运行、gopls/dlv/staticcheck 工具安装）；GOPATH/bin 主目录持久化特性说明（容器删除不丢失）；镜像版本更新与新旧容器并行；4 项镜像优化技巧（多阶段构建、分层缓存顺序、dnf clean all 同层清理、.containerignore）；推送到 Quay.io 远程 registry 团队共享；Ubuntu/Debian 基础镜像注意事项；6 项验证清单。
* [多发行版容器实战](examples/03-multi-distro.md) — Ubuntu 24.04/RHEL 9.3/Arch 三族容器创建进入；distro-release-镜像-容器名对照；release 校验拒绝规则；多容器并行与 toolbox.conf 持久化。
* [NVIDIA GPU 容器实战](examples/04-nvidia-gpu.md) — 驱动前提、零参数 GPU 容器、nvidia-smi/CUDA 验证、cdi-nvidia.json 观察、6 类故障排查。
* [运行与扩展 BATS 系统测试](examples/05-system-tests.md) — 依赖准备、TOOLBX/TMPDIR、localhost:50000 认证 registry、用例模板、CDI 夹具与 Ansible CI。

## 信源登记簿（references/）

* [README.md 项目概览与定位](references/readme-source.md) — `README.md`、`doc/toolbox.1.md`：项目规范名称 Toolbx（Toolb**x**，曾用名 Fedora Toolbox/Toolbox）、二进制名 `toolbox`、Go 1.22.0 要求、Apache-2.0 许可证；OSTree 系统问题背景（Fedora CoreOS/Silverblue）；10 项主机资源透传清单；4 个支持发行版（Arch/Fedora/RHEL ≥8.5/Ubuntu）及版本格式；fedora-toolbox 默认镜像；/run/host 主机文件系统挂载；安全边界说明；名称迁移现状（仓库/二进制/包名仍用 toolbox）。
* [src/cmd/ 命令行接口与核心命令](references/cmd-source.md) — `src/cmd/root.go`、`src/cmd/create.go`、`src/cmd/enter.go`、`src/cmd/run.go`、`src/go.mod`：cobra 命令框架；rootCmd 根命令定义（Use/Short/Version/PersistentPreRunE）；4 个全局选项（-y/--assumeyes、--log-level、--log-podman、-v/-vv verbose）；7 个核心子命令（create/enter/run/list/rm/rmi/completion）及常用选项；src/cmd/ 目录 14 个 Go 源文件清单；8 个内部 pkg 包结构（podman/shell/utils/term/nvidia/skopeo/version）；10 个主要 Go 依赖（cobra/viper/logrus/dbus/v5/nvlib/spinner/osrelease 等）；Meson 构建系统（meson.build、go-build-wrapper）；二进制入口 src/toolbox.go 调用 cmd.Execute()。
* [实现层源码地图](references/source-code-map.md) — 第二轮信源（commit 81401f64）：src/cmd 13 个非测试文件与 src/pkg 7 个子包逐文件 URL、go-build-wrapper、profile.d、data、test/system、playbooks、images 资产登记。
* [官方手册、设计目标与版本演进信源](references/docs-man-source.md) — doc/ 10 个 man 页、GOALS.md、NEWS 0.1.2-0.3 的登记与官方意图/代码互证。

## 信任与生命周期说明

* **status 判定依据**：全部 20 个内容文档（11 个概念 + 5 个示例 + 4 个信源登记）均 `status: stable`。第一轮 8 篇基于命令表层；第二轮 12 篇基于对 Toolbx 实现层（src/cmd/create.go|initContainer.go|run.go、src/pkg 全部 7 个子包、go-build-wrapper、profile.d、data、doc/、meson.build、images/、test/system）的逐文件阅读与约 120 条编号事实提取，经七概念方法论 R→I→E→V 流程生成。
* **信源版本**：第二轮信源锚定 commit `81401f64b3865129ea66f2a5e02a7eb40edd4fb8`（0.3-85-g81401f6，2026-08-05），URL 全部指向该快照而非浮动分支。
* **stale_after 解释**：第二轮文档统一设置为 `2027-09-11`。init-container argv、pkg/podman 映射、CDI 钩子等实现细节随版本演进频率高于命令表层；该日期作为实现层重新核对节点。
* **核验链路**：`generated.at` 记录生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证与计数断言独立复核（如 43 个环境变量、15 条 initContainerMounts、22 个 BATS 文件、10 个 man 页均脚本计数），两者分离、可追溯。

本知识包共收录 20 个内容文档（11 个概念 + 5 个示例 + 4 个信源登记），另含 3 个子目录 index.md、根 index.md 与 log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
